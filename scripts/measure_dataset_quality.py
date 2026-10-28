"""Descriptive dataset-quality statistics for every real (and G01 synthetic) data set in the repo.

Aggregate numbers only: no text, tweet ID or user ID is printed, logged or written. Outputs go to
results/dataset_quality/ (or --out). No training, tuning or selection happens here.

Measures (see summary.md for the exact definitions):
  A size, B lexical diversity on length-matched 5,000-token samples, C class balance,
  D duplication and cross-dataset overlap, E dialectness (Sentence-ALDi),
  F semantic diversity (multilingual-e5-large), G label consistency.

Two text views per row:
  lexical view  `tokens()` below, the shared preprocessing given for comparability with existing
                numbers. It strips diacritics/tatweel, unifies alef forms and lowercases. This is
                an explicit normalization used only for these measures; the data files are untouched.
  model view    the repo's D1 cleaning (build_dataset.unescape_text + clean_text: links -> URL,
                mentions -> USER), so raw NADI files, D1 and MLADI dev are scored on the same kind
                of text. D1-D4 `text` already is this view.

Usage:
  python -m scripts.measure_dataset_quality                        # everything, GPU
  python -m scripts.measure_dataset_quality --limit 300 --out <dir> # tiny-subset smoke test
  python -m scripts.measure_dataset_quality --datasets NADI2023 --out <dir>  # re-run one data set
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import platform
import re
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

from src.data.build_dataset import (DIALECTS, NADI_FILES, clean_text, git_commit, read_dev, sha256,
                                    unescape_text)

# ---------------------------------------------------------------- settings

NADI_DIR = Path("MLADI/train")
MLADI_DEV = Path("MLADI/dev/NADI2024_subtask1_dev2.tsv")
D_FILES = {
    "LahjatBERT-D1": Path("data/processed/nadi_lahjatbert.jsonl"),
    "LahjatBERT-D2-card1to17": Path("data/processed/nadi_lahjatbert_card1to17.jsonl"),
    "LahjatBERT-D3-card0to17": Path("data/processed/nadi_lahjatbert_card0to17.jsonl"),
    "LahjatBERT-D4-card1to18": Path("data/processed/nadi_lahjatbert_card1to18.jsonl"),
}
G01_MATCH = Path("data/processed/d1_g01match_seed42.jsonl")
G01_DIR = Path("data/synthetic")
EXTRA_DIR = Path("data/datasets/di")   # external corpora added 2026-10-11; moved from results/datasets/ 2026-10-28
HABIBI_CSV = EXTRA_DIR / "habibi_full_corpus_csv (1)" / "arabicLyrics.csv"
TRAVEL_CSV = EXTRA_DIR / "multidialectal_travel_corpus" / "multidialectal_travel_corpus.csv"
PADIC_XML = EXTRA_DIR / "PADIC" / "PADIC.xml"
INSPECT_FILES = {"cardinality=18": Path("data/inspect/d1_all18.tsv"),
                 "cardinality=0": Path("data/inspect/d1_zero.tsv")}
# Documented row counts (docs/data.md, results/data_stats/nadi_lahjatbert_stats.json).
EXPECTED_ROWS = {
    "NADI2020-TWT": 20370, "NADI2021-TWT": 20398, "NADI2023-TWT": 18000,
    "LahjatBERT-D1": 58384, "LahjatBERT-D2-card1to17": 48471, "LahjatBERT-D3-card0to17": 50742,
    "LahjatBERT-D4-card1to18": 56113, "MLADI-dev": 120, "D1-G01-match": 20,
}

ALDI_MODEL = "AMR-KELEG/Sentence-ALDi"   # redirects on the Hub to VARabi/Sentence-ALDi (same commit)
E5_MODEL = "intfloat/multilingual-e5-large"
LEX_TOKENS, LEX_REPEATS = 5000, 30        # B: sample size in tokens, seeds 0..29
ALDI_MAX, ALDI_SEED = 20000, 0            # E: random sample per split above this size
SEM_N, SEM_SEEDS = 2000, range(5)         # F: texts per repeat, seeds 0..4
MIN_SUBSET_TEXTS = 50                     # per-label subsets with fewer texts are skipped
ROUND = 4

csv.field_size_limit(10_000_000)

# ---------------------------------------------------------------- shared preprocessing (given)

DIAC = re.compile(r'[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]')


def tokens(s) -> list[str]:
    """Shared lexical preprocessing: drop links/mentions/placeholders, diacritics; unify alef; lowercase."""
    s = str(s)
    s = re.sub(r'https?://\S+|www\.\S+', ' ', s)
    s = re.sub(r'@\w+', ' ', s)
    s = re.sub(r'\b(USER|URL|EMOJI|NUM)\b', ' ', s)
    s = DIAC.sub('', s)
    s = re.sub('[إأآٱ]', 'ا', s).lower()
    return re.findall(r'[\u0621-\u064A\u0671-\u06D3a-z]+', s)


def norm(s) -> str:
    """Normalized string used for duplication and overlap."""
    return ' '.join(tokens(s))


def model_text(raw: str) -> str:
    """Model-input view: the repo's D1 cleaning (unescape quotes, links -> URL, mentions -> USER)."""
    return clean_text(unescape_text(raw)[0], ["urls", "mentions"])[0]

# ---------------------------------------------------------------- data


@dataclass
class Row:
    """One text with its labels. `text` never leaves this process."""
    text: str                                    # lexical-view input
    mtext: str                                   # model-view input
    label: str | None = None                     # single country label (None if none / several)
    labels: dict[str, int] | None = None         # multi-label validity, if the set has it
    meta: dict = field(default_factory=dict)     # aggregate-only extras (nadi_refs, cardinality, id)
    label2: str | None = None                    # second single-label family (Habibi song dialect)


@dataclass
class Split:
    """One split of one data set."""
    dataset: str
    split: str
    path: str
    rows: list[Row]
    kind: str            # "single", "multi" or "single+multi"
    label_name: str      # what `label` means
    label2_name: str = ""  # what `label2` means, if used
    notes: list[str] = field(default_factory=list)  # aggregate-only notes for summary.md


def read_habibi(path: Path, limit: int | None) -> Split:
    """Habibi lyrics (arabicLyrics.csv): one row per lyric line; labels = singer nationality, song dialect."""
    rows, empty, songs = [], 0, set()
    with open(path, encoding="utf-8-sig", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            if limit is not None and i >= limit:
                break
            # Empty lines are counted, not measured.
            if not r["Lyrics"].strip():
                empty += 1
                continue
            songs.add(r["songID"])
            rows.append(Row(r["Lyrics"], model_text(r["Lyrics"]), label=r["SingerNationality"], label2=r["SongDialect"]))
    return Split("Habibi-lyrics", "all", str(path), rows, "single", "singer nationality",
                 "song dialect", [f"Habibi: unit = one lyric line; {len(rows)} non-empty lines from {len(songs)} songs; "
                                  f"{empty} empty lines skipped."])


def read_parallel(name: str, path: Path, columns: list[tuple[str, list[str]]], limit: int | None) -> Split:
    """Parallel corpus -> one row per non-empty cell, label = variety; meta holds the source row and MSA cell."""
    rows, empty = [], Counter()
    # Walk source rows, then varieties, so cells of one source sentence stay together.
    n_src = len(columns[0][1]) if limit is None else min(limit, len(columns[0][1]))
    msa = dict(columns).get("MSA")
    for j in range(n_src):
        for variety, cells in columns:
            t = cells[j]
            if not t.strip():
                empty[variety] += 1
                continue
            rows.append(Row(t, model_text(t), label=variety,
                            meta={"src": j, "msa": msa[j] if msa is not None and variety != "MSA" else None}))
    note = f"{name}: unit = one cell of the parallel corpus; {n_src} source rows x {len(columns)} varieties"
    note += f"; empty cells skipped: {dict(empty)}." if empty else "; no empty cells."
    return Split(name, "all", str(path), rows, "single", "variety", "", [note])


def read_travel(path: Path, limit: int | None) -> Split:
    """multidialectal_travel_corpus.csv: 6 parallel columns (MSA + 5 dialects)."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        data = list(csv.reader(f))
    names = {"Modern Standard Arabic": "MSA", "Saudi Dialect": "Saudi", "Egyptian Dialect": "Egyptian",
             "Iraqi Dialect": "Iraqi", "Levantine Dialect": "Levantine", "Moroccan Dialect": "Moroccan"}
    cols = [(names[h], [r[i] for r in data[1:]]) for i, h in enumerate(data[0])]
    return read_parallel("Travel-parallel", path, cols, limit)


def read_padic(path: Path, limit: int | None) -> Split:
    """PADIC.xml: <Sentence> elements with 6 parallel varieties (Algiers, Annaba, MSA, Syrian, Palestinian, Moroccan)."""
    from xml.etree import ElementTree as ET
    sents = ET.parse(path).getroot().findall("Sentence")
    tags = [c.tag for c in sents[0]]
    names = {t: ("MSA" if t == "MODERN-STANDARD-ARABIC" else t.title()) for t in tags}
    cols = [(names[t], [(s.findtext(t) or "") for s in sents]) for t in tags]
    return read_parallel("PADIC", path, cols, limit)


def read_nadi_file(path: Path, limit: int | None) -> list[Row]:
    """Rows of one NADI TSV (QUOTE_NONE, as build_dataset.read_nadi)."""
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        next(reader)
        for i, r in enumerate(reader):
            if limit is not None and i >= limit:
                break
            rows.append(Row(r[1], model_text(r[1]), label=r[2]))
    return rows


def read_jsonl(path: Path, limit: int | None) -> list[dict]:
    """Records of a JSONL file."""
    out = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            out.append(json.loads(line))
    return out


def d_rows(records: list[dict]) -> list[Row]:
    """D1-D4 records -> rows; single label = the original NADI country if all copies agree."""
    return [Row(r["text"], r["text"], label=r["countries"][0] if len(r["countries"]) == 1 else None,
                labels=r["labels"], meta={"nadi_refs": r["nadi_refs"], "cardinality": r["cardinality"],
                                          "text_id": r["text_id"]})
            for r in records]


def load_all(limit: int | None, only: set[str] | None) -> tuple[list[Split], list[str]]:
    """Load every data set found in the repo; return the splits and notes on what is missing."""
    splits, notes = [], []

    def want(name: str) -> bool:
        return only is None or name in only

    # 1. NADI training files (the MLADI release contains train only; no dev/test files).
    for source, fname in NADI_FILES.items():
        name = f"{source}-TWT"
        if want(name):
            p = NADI_DIR / fname
            if p.exists():
                splits.append(Split(name, "train", str(p), read_nadi_file(p, limit), "single", "country"))
            else:
                notes.append(f"{name}: {p} not found")
    notes.append("NADI 2020/2021/2023 dev and test splits: not in the repo (the MLADI release ships the "
                 "three train files only), so no dev/test rows and no dev/test-in-train leakage for them.")

    # 2. LahjatBERT pseudo-labels joined to NADI text (D1) and its cardinality-filtered versions.
    for name, p in D_FILES.items():
        if want(name):
            if p.exists():
                splits.append(Split(name, "train", str(p), d_rows(read_jsonl(p, limit)), "single+multi",
                                    "original NADI country"))
            else:
                notes.append(f"{name}: {p} not found")

    # 3. MLADI dev (multi-label, 8 dialects). The test text is not in the repo.
    if want("MLADI-dev"):
        texts, labels = read_dev(MLADI_DEV)
        n = len(texts) if limit is None else min(limit, len(texts))
        rows = [Row(texts[i], model_text(texts[i]), labels={d: v[i] for d, v in labels.items()})
                for i in range(n)]
        splits.append(Split("MLADI-dev", "dev", str(MLADI_DEV), rows, "multi", ""))
    notes.append("MLADI test: text not in the repo (labels private, leaderboard only), so not measured.")

    # 4. Other data: the G01 pilot (6 x 20 synthetic sentences + 20 size-matched D1 tweets).
    if want("D1-G01-match") and G01_MATCH.exists():
        splits.append(Split("D1-G01-match", "all", str(G01_MATCH), d_rows(read_jsonl(G01_MATCH, limit)),
                            "single", "original NADI country"))
    for p in sorted(G01_DIR.glob("g01_*.jsonl")):
        name = "G01-synthetic-" + p.stem[len("g01_"):]
        if want(name):
            rows = [Row(r["text"], model_text(r["text"]), label=r["target_dialect"])
                    for r in read_jsonl(p, limit)]
            splits.append(Split(name, "all", str(p), rows, "single", "target dialect"))

    # 5. External corpora in data/datasets/di/ (no splits shipped: each measured as one split "all").
    for name, path, reader in (("Habibi-lyrics", HABIBI_CSV, read_habibi), ("Travel-parallel", TRAVEL_CSV, read_travel),
                               ("PADIC", PADIC_XML, read_padic)):
        if want(name):
            if path.exists():
                splits.append(reader(path, limit))
            else:
                notes.append(f"{name}: {path} not found")
    return splits, notes

# ---------------------------------------------------------------- A + B lexical


def lexical_sample_scores(toks: list[list[str]], seed: int) -> tuple[float, float, float]:
    """One length-matched sample: TTR, distinct-2 (within-text bigrams), hapax share at 5,000 tokens."""
    order = np.random.default_rng(seed).permutation(len(toks))
    words, bigrams, need = [], [], LEX_TOKENS
    # Concatenate whole texts in shuffled order; the last one is cut so the total is exactly 5,000.
    for i in order:
        t = toks[i][:need]
        if not t:
            continue
        words.extend(t)
        bigrams.extend(zip(t, t[1:]))
        need -= len(t)
        if need == 0:
            break
    counts = Counter(words)
    return (len(counts) / LEX_TOKENS, len(set(bigrams)) / len(bigrams) if bigrams else 0.0,
            sum(c == 1 for c in counts.values()) / LEX_TOKENS)


def lexical_row(ds: str, split: str, subset: str, rows: list[Row]) -> dict:
    """Size measures plus the mean of 30 length-matched lexical samples (or 'under 5,000 tokens')."""
    toks = [tokens(r.text) for r in rows]
    n_tok = sum(map(len, toks))
    out = {"dataset": ds, "split": split, "subset": subset, "texts": len(rows), "tokens": n_tok,
           "unique_words": len({w for t in toks for w in t}),
           "mean_tokens": round(n_tok / len(rows), ROUND) if rows else ""}
    # Length-matched diversity only when the subset holds at least 5,000 tokens.
    if n_tok < LEX_TOKENS:
        out.update(ttr_5000="under 5,000 tokens", distinct2="under 5,000 tokens", hapax_share="under 5,000 tokens")
    else:
        s = np.array([lexical_sample_scores(toks, seed) for seed in range(LEX_REPEATS)])
        out.update(ttr_5000=round(s[:, 0].mean(), ROUND), distinct2=round(s[:, 1].mean(), ROUND),
                   hapax_share=round(s[:, 2].mean(), ROUND))
    return out

# ---------------------------------------------------------------- C balance


def balance_rows(sp: Split) -> tuple[list[dict], dict]:
    """Per-label counts and shares, cardinality shares for multi-label sets; plus the max/min ratio."""
    out, ratios, n = [], {}, len(sp.rows)
    # Single-label: one row per label, shares sum to 1 (rows with no single label are their own row).
    if sp.kind in ("single", "single+multi"):
        c = Counter(r.label if r.label is not None else "(several countries)" for r in sp.rows)
        for lab, k in sorted(c.items()):
            out.append({"dataset": sp.dataset, "split": sp.split, "label": f"{sp.label_name}:{lab}",
                        "count": k, "share": round(k / n, 6)})
        real = {k: v for k, v in c.items() if k != "(several countries)"}
        ratios["single"] = round(max(real.values()) / min(real.values()), ROUND) if real else None
    # Second single-label family (Habibi song dialect): its own rows, its shares also sum to 1.
    if sp.label2_name:
        c2 = Counter(r.label2 for r in sp.rows)
        for lab, k in sorted(c2.items()):
            out.append({"dataset": sp.dataset, "split": sp.split, "label": f"{sp.label2_name}:{lab}",
                        "count": k, "share": round(k / n, 6)})
        ratios["single2"] = round(max(c2.values()) / min(c2.values()), ROUND)
    # Multi-label: positives per country (share of texts), then cardinality 0 / 1 / 2 / 3+ (sums to 1).
    if sp.kind in ("multi", "single+multi"):
        countries = list(sp.rows[0].labels)
        pos = {d: sum(r.labels[d] for r in sp.rows) for d in countries}
        for d in countries:
            out.append({"dataset": sp.dataset, "split": sp.split, "label": f"valid:{d}",
                        "count": pos[d], "share": round(pos[d] / n, 6)})
        card = Counter(min(sum(r.labels.values()), 3) for r in sp.rows)
        for k in range(4):
            out.append({"dataset": sp.dataset, "split": sp.split, "label": f"cardinality:{k if k < 3 else '3+'}",
                        "count": card.get(k, 0), "share": round(card.get(k, 0) / n, 6)})
        ratios["multi"] = round(max(pos.values()) / min(pos.values()), ROUND) if min(pos.values()) else None
    return out, ratios

# ---------------------------------------------------------------- D duplication / overlap


def norm_set(rows: list[Row]) -> tuple[set[str], int, int]:
    """Unique non-empty normalized texts, number of non-empty rows, number of empty rows."""
    normed = [norm(r.text) for r in rows]
    nonempty = [t for t in normed if t]
    return set(nonempty), len(nonempty), len(normed) - len(nonempty)

# ---------------------------------------------------------------- E + F model measures


def aldi_scores(texts: list[str], device: str, cache_dir: Path | None) -> dict[str, float]:
    """Sentence-ALDi score per unique text (fp32, length-sorted batches)."""
    from src.quality.scorers import ALDiScorer
    scorer = ALDiScorer(cache_dir, device, batch_size=64)
    uniq = sorted(set(texts), key=lambda t: (len(t), t))
    return dict(zip(uniq, scorer.score(uniq)))


def e5_embeddings(texts: list[str], device: str, cache_dir: Path | None) -> dict[str, np.ndarray]:
    """E5 embedding per unique text ("query: " prefix, mean pooling, L2-normalized; fp32 for stability)."""
    from src.quality.scorers import E5Embedder
    emb = E5Embedder(cache_dir, device, batch_size=64)
    emb.model.float()  # the shared embedder halves on CUDA; fp32 keeps re-runs reproducible
    uniq = sorted(set(texts), key=lambda t: (len(t), t))
    return dict(zip(uniq, emb.embed(uniq).astype(np.float64)))


def semantic_one(X: np.ndarray) -> tuple[float, float, float]:
    """Mean pairwise cosine distance, mean cosine distance to the centroid, Vendi score (unit rows)."""
    n = X.shape[0]
    s = X.sum(0)
    # Sum of all pairwise similarities (i != j) from the norm of the sum; diagonal = n.
    pair = 1.0 - (s @ s - n) / (n * (n - 1)) if n > 1 else float("nan")
    c = s / np.linalg.norm(s)
    cent = float(np.mean(1.0 - X @ c))
    # Non-zero eigenvalues of K/n = X X^T / n equal those of X^T X / n (d x d, cheaper than n x n).
    lam = np.clip(np.linalg.eigvalsh(X.T @ X / n), 0.0, None)
    lam = lam[lam > 1e-12]
    vendi = float(np.exp(-(lam * np.log(lam)).sum()))
    return pair, cent, vendi

# ---------------------------------------------------------------- G consistency


def consistency_rows(splits: list[Split]) -> list[dict]:
    """LahjatBERT vs NADI geolocation per country; MLADI dev validity counts and cardinality."""
    out = []
    for sp in splits:
        # LahjatBERT vs NADI: per tweet (each NADI copy), is its own country among the pseudo-labels?
        if sp.dataset == "LahjatBERT-D1":
            per = defaultdict(list)
            for r in sp.rows:
                for ref in r.meta["nadi_refs"]:
                    for scope in ("all", ref["source"]):
                        per[(scope, ref["country"])].append((r.labels.get(ref["country"], 0), sum(r.labels.values())))
            for (scope, country), v in sorted(per.items()):
                ds = "LahjatBERT-vs-NADI" + ("" if scope == "all" else f"-{scope}")
                own, card = np.array(v).T
                out += [{"dataset": ds, "country": country, "n": len(v), "measure": "own_country_in_pseudo_labels_share",
                         "value": round(float(own.mean()), ROUND)},
                        {"dataset": ds, "country": country, "n": len(v), "measure": "mean_pseudo_labels",
                         "value": round(float(card.mean()), ROUND)},
                        {"dataset": ds, "country": country, "n": len(v), "measure": "zero_pseudo_labels_share",
                         "value": round(float((card == 0).mean()), ROUND)}]
        # MLADI dev: valid count per country, and share of tweets valid in exactly 0 / 1 / 2 / 3+ countries.
        if sp.dataset == "MLADI-dev":
            n = len(sp.rows)
            for d in sp.rows[0].labels:
                k = sum(r.labels[d] for r in sp.rows)
                out.append({"dataset": "MLADI-dev", "country": d, "n": n, "measure": "valid_count", "value": k})
                out.append({"dataset": "MLADI-dev", "country": d, "n": n, "measure": "valid_share",
                            "value": round(k / n, ROUND)})
            card = Counter(min(sum(r.labels.values()), 3) for r in sp.rows)
            for k in range(4):
                out.append({"dataset": "MLADI-dev", "country": "(all)", "n": n,
                            "measure": f"valid_in_exactly_{k if k < 3 else '3+'}_share",
                            "value": round(card.get(k, 0) / n, ROUND)})
        # Habibi: does each singer nationality map to one song dialect? (share of lines with the majority dialect)
        if sp.label2_name:
            by = defaultdict(Counter)
            for r in sp.rows:
                by[r.label][r.label2] += 1
            for country, c in sorted(by.items()):
                n = sum(c.values())
                out.append({"dataset": sp.dataset, "country": country, "n": n,
                            "measure": "majority_song_dialect_share", "value": round(max(c.values()) / n, ROUND)})
                out.append({"dataset": sp.dataset, "country": country, "n": n,
                            "measure": "n_song_dialects", "value": len(c)})
        # Parallel corpora: share of dialect cells identical to their MSA source after norm() (untranslated).
        if any(r.meta.get("msa") is not None for r in sp.rows[:50]):
            per = defaultdict(list)
            for r in sp.rows:
                if r.label != "MSA" and r.meta.get("msa") is not None:
                    per[r.label].append(norm(r.text) == norm(r.meta["msa"]))
            for variety, v in sorted(per.items()):
                out.append({"dataset": sp.dataset, "country": variety, "n": len(v),
                            "measure": "identical_to_msa_share", "value": round(float(np.mean(v)), ROUND)})
    return out

# ---------------------------------------------------------------- output


def write_csv(path: Path, rows: list[dict], cols: list[str]) -> None:
    """Write rows with exactly these columns (UTF-8)."""
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def md_table(rows: list[dict], cols: list[str]) -> str:
    """Markdown table of rows."""
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(r.get(c, "")) for c in cols) + " |" for r in rows]
    return "\n".join(lines)


def section(title: str, rows: list[dict], cols: list[str], main=lambda r: True) -> str:
    """Summary section: split-level table, then every row in a collapsed block if there are more."""
    top = [r for r in rows if main(r)]
    s = f"## {title}\n\n{md_table(top, cols)}\n"
    if len(top) < len(rows):
        s += f"\n<details><summary>All {len(rows)} rows (per label)</summary>\n\n{md_table(rows, cols)}\n\n</details>\n"
    return s + "\n"

# ---------------------------------------------------------------- main


def subsets_of(sp: Split) -> list[tuple[str, list[Row]]]:
    """The split itself plus each single-label subset with at least MIN_SUBSET_TEXTS texts."""
    out = [("all", sp.rows)]
    if sp.kind in ("single", "single+multi"):
        by = defaultdict(list)
        for r in sp.rows:
            if r.label is not None:
                by[r.label].append(r)
        out += [(f"{sp.label_name.split()[-1]}={k}", v) for k, v in sorted(by.items()) if len(v) >= MIN_SUBSET_TEXTS]
    # Second label family (Habibi song dialect).
    if sp.label2_name:
        by2 = defaultdict(list)
        for r in sp.rows:
            by2[r.label2].append(r)
        out += [(f"{sp.label2_name.split()[-1]}={k}", v) for k, v in sorted(by2.items()) if len(v) >= MIN_SUBSET_TEXTS]
    # D1 only: the zero-label and all-18 subsets (exported as data/inspect/*.tsv).
    if sp.dataset == "LahjatBERT-D1":
        for k in (0, 18):
            out.append((f"cardinality={k}", [r for r in sp.rows if r.meta["cardinality"] == k]))
    return out


def skipped_subsets(sp: Split) -> list[str]:
    """Names and sizes of per-label subsets below MIN_SUBSET_TEXTS."""
    if sp.kind not in ("single", "single+multi"):
        return []
    c = Counter(r.label for r in sp.rows if r.label is not None)
    return [f"{k} ({v})" for k, v in sorted(c.items()) if v < MIN_SUBSET_TEXTS]


def main() -> None:
    """Load the data sets, compute measures A-G, write the CSVs and summary.md."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", type=Path, default=Path("results/dataset_quality"))
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N rows per file")
    p.add_argument("--datasets", nargs="*", default=None, help="only these data sets (names as in the CSVs)")
    p.add_argument("--device", default="cuda")
    p.add_argument("--cache-dir", type=Path, default=Path("F:/Thesis/models"))
    p.add_argument("--no-models", action="store_true", help="skip E and F (CPU-only smoke test)")
    args = p.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    # Load. Print only names and counts.
    splits, notes = load_all(args.limit, set(args.datasets) if args.datasets else None)
    for sp in splits:
        print(f"loaded {sp.dataset}/{sp.split}: {len(sp.rows)} rows ({sp.path})", flush=True)

    # A + B per split and per subset.
    lexical, skipped = [], {}
    for sp in splits:
        for name, rows in subsets_of(sp):
            lexical.append(lexical_row(sp.dataset, sp.split, name, rows))
        if skipped_subsets(sp):
            skipped[f"{sp.dataset}/{sp.split}"] = skipped_subsets(sp)
    print(f"lexical done ({time.time() - t0:.0f}s)", flush=True)

    # C.
    balance, ratios = [], {}
    for sp in splits:
        rows, r = balance_rows(sp)
        balance += rows
        ratios[f"{sp.dataset}/{sp.split}"] = r

    # D: within-split repeats; train-split overlap of dev/test (none of the sets has both); cross-set overlap.
    sets, duplication = {}, []
    for sp in splits:
        uniq, n_nonempty, n_empty = norm_set(sp.rows)
        sets[sp.dataset] = uniq
        duplication.append({"dataset": sp.dataset, "split": sp.split,
                            "repeat_share": round((n_nonempty - len(uniq)) / n_nonempty, 6) if n_nonempty else "",
                            "in_train_share": "", "_empty": n_empty})
    pairs = [("MLADI-dev", b) for b in ("NADI2020-TWT", "NADI2021-TWT", "NADI2023-TWT", "LahjatBERT-D1")]
    nadi = ["NADI2020-TWT", "NADI2021-TWT", "NADI2023-TWT"]
    pairs += [(a, b) for a in nadi for b in nadi if a != b]
    pairs += [(d, "LahjatBERT-D1") for d in sets if d.startswith("G01-synthetic-")]
    # External corpora: leakage into MLADI dev, overlap with the training set, and with each other.
    extra = ["Habibi-lyrics", "Travel-parallel", "PADIC"]
    pairs += [("MLADI-dev", e) for e in extra] + [(e, "LahjatBERT-D1") for e in extra]
    pairs += [(a, b) for a in extra for b in extra if a != b]
    overlap = []
    for a, b in pairs:
        if a in sets and b in sets and sets[a]:
            k = len(sets[a] & sets[b])
            overlap.append({"set_a": a, "set_b": b, "shared_unique_texts": k, "share_of_a": round(k / len(sets[a]), 6)})

    # E + F.
    dialectness, semantic = [], []
    if not args.no_models:
        import os
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        # Fix every sample first, then score only the texts the samples need.
        # ALDi: every row, or a fixed random 20,000 rows (seed 0); subsets use the sampled rows.
        aldi_keep = {}
        for sp in splits:
            idx = (np.random.default_rng(ALDI_SEED).choice(len(sp.rows), ALDI_MAX, replace=False)
                   if len(sp.rows) > ALDI_MAX else np.arange(len(sp.rows)))
            aldi_keep[sp.dataset] = {id(sp.rows[i]) for i in idx}
        # E5: 2,000 random texts per repeat (seeds 0..4), or all texts once if the subset is smaller.
        sem_draws = {}
        for sp in splits:
            for name, rows in subsets_of(sp):
                n = len(rows)
                sem_draws[(sp.dataset, name)] = ([np.random.default_rng(s).choice(n, SEM_N, replace=False)
                                                  for s in SEM_SEEDS] if n > SEM_N else [np.arange(n)])
        t1 = time.time()
        aldi = aldi_scores([r.mtext for sp in splits for r in sp.rows if id(r) in aldi_keep[sp.dataset]],
                           args.device, args.cache_dir)
        print(f"ALDi scored {len(aldi)} unique texts ({time.time() - t1:.0f}s)", flush=True)
        for sp in splits:
            keep = aldi_keep[sp.dataset]
            for name, rows in subsets_of(sp):
                v = np.array([aldi[r.mtext] for r in rows if id(r) in keep])
                if len(v):
                    dialectness.append({"dataset": sp.dataset, "split": sp.split, "subset": name, "n": len(v),
                                        "mean_aldi": round(v.mean(), ROUND),
                                        "share_below_0.11": round((v < 0.11).mean(), ROUND),
                                        "share_above_0.5": round((v > 0.5).mean(), ROUND),
                                        "share_above_0.77": round((v > 0.77).mean(), ROUND)})
        del aldi
        import torch
        torch.cuda.empty_cache()
        t1 = time.time()
        need = [rows[i].mtext for sp in splits for name, rows in subsets_of(sp)
                for d in sem_draws[(sp.dataset, name)] for i in d]
        emb = e5_embeddings(need, args.device, args.cache_dir)
        print(f"E5 embedded {len(emb)} unique texts ({time.time() - t1:.0f}s)", flush=True)
        for sp in splits:
            for name, rows in subsets_of(sp):
                n, draws = len(rows), sem_draws[(sp.dataset, name)]
                vals = np.array([semantic_one(np.stack([emb[rows[i].mtext] for i in d])) for d in draws])
                semantic.append({"dataset": sp.dataset, "split": sp.split, "subset": name, "n": min(n, SEM_N),
                                 "mean_pairwise_cos_dist": round(vals[:, 0].mean(), ROUND),
                                 "mean_centroid_dist": round(vals[:, 1].mean(), ROUND),
                                 "vendi": round(vals[:, 2].mean(), 2), "_repeats": len(draws),
                                 "_vendi_sd": round(vals[:, 2].std(), 2)})
        del emb

    # G.
    consistency = consistency_rows(splits)

    # Checks: documented row counts, single-label shares sum to 1, inspect exports = D1 subsets.
    checks = []
    for sp in splits:
        exp = EXPECTED_ROWS.get(sp.dataset)
        if exp is not None:
            ok = len(sp.rows) == exp
            checks.append(f"{'OK ' if ok else 'MISMATCH'} rows {sp.dataset}/{sp.split}: {len(sp.rows)} (documented {exp})")
    # Each single-label family (text before ":" in the label) must cover every row once.
    for sp in splits:
        if sp.kind not in ("single", "single+multi"):
            continue
        for fam in [sp.label_name] + ([sp.label2_name] if sp.label2_name else []):
            fam_rows = [b for b in balance if (b["dataset"], b["split"]) == (sp.dataset, sp.split)
                        and b["label"].split(":")[0] == fam]
            tot, sh = sum(b["count"] for b in fam_rows), sum(b["share"] for b in fam_rows)
            checks.append(f"{'OK ' if tot == len(sp.rows) and abs(sh - 1) < 1e-4 else 'MISMATCH'} single-label balance "
                          f"{sp.dataset}/{sp.split} [{fam}]: counts sum {tot} of {len(sp.rows)}, shares sum {sh:.6f}")
    d1 = next((s for s in splits if s.dataset == "LahjatBERT-D1"), None)
    if d1 is not None and args.limit is None:
        for name, path in INSPECT_FILES.items():
            with open(path, encoding="utf-8-sig", newline="") as f:
                ids = {r["text_id"] for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE)}
            k = int(name.split("=")[1])
            d1ids = {r.meta["text_id"] for r in d1.rows if r.meta["cardinality"] == k}
            checks.append(f"{'OK ' if ids == d1ids else 'MISMATCH'} {path} has {len(ids)} text_ids, "
                          f"D1 {name} has {len(d1ids)}, identical sets: {ids == d1ids}")
    for c in checks:
        print(c)

    # Write CSVs (aggregate columns only).
    write_csv(args.out / "lexical.csv", lexical, ["dataset", "split", "subset", "texts", "tokens", "unique_words",
                                                  "mean_tokens", "ttr_5000", "distinct2", "hapax_share"])
    write_csv(args.out / "balance.csv", balance, ["dataset", "split", "label", "count", "share"])
    write_csv(args.out / "duplication.csv", duplication, ["dataset", "split", "repeat_share", "in_train_share"])
    write_csv(args.out / "overlap.csv", overlap, ["set_a", "set_b", "shared_unique_texts", "share_of_a"])
    sem_cols = ["dataset", "split", "subset", "n", "mean_pairwise_cos_dist", "mean_centroid_dist", "vendi"]
    ald_cols = ["dataset", "split", "subset", "n", "mean_aldi", "share_below_0.11", "share_above_0.5", "share_above_0.77"]
    if not args.no_models:
        write_csv(args.out / "dialectness.csv", dialectness, ald_cols)
        write_csv(args.out / "semantic.csv", semantic, sem_cols)
    write_csv(args.out / "consistency.csv", consistency, ["dataset", "country", "n", "measure", "value"])

    # summary.md.
    from huggingface_hub import scan_cache_dir
    revs = {}
    try:
        for repo in scan_cache_dir(args.cache_dir).repos:
            if repo.repo_id in ("VARabi/Sentence-ALDi", E5_MODEL):
                revs[repo.repo_id] = sorted(r.commit_hash for r in repo.revisions)
    except Exception as e:  # cache scan is provenance only
        revs["error"] = type(e).__name__
    split_level = lambda r: r.get("subset", "all") == "all"
    md = [f"# Dataset quality statistics\n",
          f"Generated by `scripts/measure_dataset_quality.py` (git commit `{git_commit()}`, Python "
          f"{platform.python_version()}), {time.strftime('%Y-%m-%d %H:%M')}, runtime {time.time() - t0:.0f} s. "
          f"Aggregate numbers only. Tiny-subset limit: {args.limit}. Data sets filter: {args.datasets}.\n",
          "## Data sets measured\n",
          md_table([{"dataset": s.dataset, "split": s.split, "path": f"`{s.path}`", "rows": len(s.rows),
                     "sha256[:12]": sha256(Path(s.path.split("::")[0]))[:12]} for s in splits],
                   ["dataset", "split", "path", "rows", "sha256[:12]"]) + "\n",
          "Copies not measured twice (identical SHA-256): `LahjatBERT_-main/evaluation/NADI2024_subtask1_dev2.tsv` = "
          "MLADI dev; `MLADI/MLADI_subtask1.tar.gz` contains the same three NADI files and dev file. "
          "`data/inspect/d1_all18.tsv` and `d1_zero.tsv` are exports of D1's all-18 and zero-label texts and are "
          "measured as D1 subsets `cardinality=18` / `cardinality=0`.\n",
          "Unit notes:\n" + "\n".join(f"- {n}" for s in splits for n in s.notes) + "\n",
          "Not available / skipped:\n" + "\n".join(f"- {n}" for n in notes)
          + "\n- MLADI dev has no geolocated-country column, so the geolocation-vs-validity measure of G is skipped."
          + f"\n- Per-label subsets with fewer than {MIN_SUBSET_TEXTS} texts are skipped: "
          + (json.dumps(skipped) if skipped else "none") + "\n",
          "## Settings\n",
          f"- Lexical view: the shared `tokens()` / `norm()` preprocessing (in the script). Model view: D1 cleaning "
          f"(links -> URL, mentions -> USER, NADI 2021 double-escaped quotes undone).\n"
          f"- B: {LEX_REPEATS} repeats, seeds 0..{LEX_REPEATS - 1}; shuffle texts, concatenate whole texts, cut at "
          f"exactly {LEX_TOKENS} tokens. distinct-2 counts bigrams inside a text only (the cut text keeps its "
          f"included part). Mean over repeats.\n"
          f"- C: single-label shares are over all rows (rows whose copies have different countries are "
          f"`(several countries)`); multi-label `valid:` shares are positives / texts; cardinality 0/1/2/3+ sums to 1.\n"
          f"- D: on norm(text), empty norms excluded. repeat_share = (non-empty rows - unique) / non-empty rows, i.e. "
          f"the share of rows that are an extra copy of an earlier row. in_train_share is empty: no data set here "
          f"has both a train and a dev/test split (cross-set leakage is in overlap.csv).\n"
          f"- E: `{ALDI_MODEL}` (Hub redirect to `VARabi/Sentence-ALDi`, cached revisions "
          f"{revs.get('VARabi/Sentence-ALDi')}), fp32, max_length 128, scores clipped to [0, 1]. All texts, or a "
          f"random {ALDI_MAX} rows (seed {ALDI_SEED}) for larger splits; per-label subsets use the sampled rows.\n"
          f"- F: `{E5_MODEL}` (revisions {revs.get(E5_MODEL)}), prefix \"query: \", mean pooling, L2-normalised, fp32, "
          f"max_length 128. {SEM_N} random texts per repeat, seeds {list(SEM_SEEDS)} (subsets with <= {SEM_N} texts: "
          f"all texts once, n recorded). Pairwise distance = 1 - mean cosine over i != j; centroid distance = mean "
          f"cosine distance to the mean vector; Vendi = exp(entropy of eigenvalues of K/n), K = cosine-similarity "
          f"matrix (computed from X^T X / n, same non-zero eigenvalues).\n"
          f"- Per-label subsets: NADI country; D1-D4 original NADI country (texts whose copies all share one "
          f"country); G01 target dialect; Habibi singer nationality and song dialect; Travel / PADIC variety "
          f"(parallel-corpus column); minimum {MIN_SUBSET_TEXTS} texts.\n"
          f"- External corpora (Habibi, Travel-parallel, PADIC) ship no splits: each is one split `all`. Only the "
          f"texts the ALDi / E5 samples need are scored.\n"
          f"- G extras: Habibi `majority_song_dialect_share` = share of a nationality's lines carrying its most common "
          f"song dialect; parallel corpora `identical_to_msa_share` = share of a variety's cells whose norm() equals "
          f"the MSA cell of the same source row.\n",
          "## Checks\n", "\n".join(f"- {c}" for c in checks) + "\n",
          section("A + B. Size and lexical diversity", lexical,
                  ["dataset", "split", "subset", "texts", "tokens", "unique_words", "mean_tokens", "ttr_5000",
                   "distinct2", "hapax_share"], split_level),
          section("C. Class balance", balance, ["dataset", "split", "label", "count", "share"],
                  lambda r: r["label"].startswith("cardinality:")),
          "Largest / smallest label ratio (single = original/target label, multi = valid positives per country):\n\n"
          + md_table([{"split": k, "single": v.get("single", ""), "single2": v.get("single2", ""),
                       "multi": v.get("multi", "")} for k, v in ratios.items()],
                     ["split", "single", "single2", "multi"]) + "\n\n(single2 = Habibi song dialect.)\n\n",
          section("D. Duplication", duplication, ["dataset", "split", "repeat_share", "in_train_share", "_empty"]),
          "`_empty` = rows whose normalized text is empty (excluded from D).\n\n",
          section("D. Cross-dataset overlap (unique normalized texts)", overlap,
                  ["set_a", "set_b", "shared_unique_texts", "share_of_a"])]
    if not args.no_models:
        md += [section("E. Dialectness (Sentence-ALDi)", dialectness, ald_cols, split_level),
               section("F. Semantic diversity (multilingual-e5-large)", semantic,
                       sem_cols + ["_repeats", "_vendi_sd"], split_level)]
    md += [section("G. Label consistency", consistency, ["dataset", "country", "n", "measure", "value"],
                   lambda r: r["measure"] in ("majority_song_dialect_share", "identical_to_msa_share")
                   or r["dataset"] in ("LahjatBERT-vs-NADI", "MLADI-dev")
                   and r["measure"] in ("own_country_in_pseudo_labels_share", "mean_pseudo_labels", "valid_count")
                   or r["measure"].startswith("valid_in_exactly"))]
    (args.out / "summary.md").write_text("\n".join(md), encoding="utf-8")
    print(f"wrote {args.out} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
