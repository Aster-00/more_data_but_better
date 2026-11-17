"""Exploration of the EESA corpus (all splits): universal topics, class balance, script mix, Self-BLEU.

No model and no GPU: topics come from the frozen universal assignments (D-019), so nothing is embedded.

  topics        EESA texts in the universal pool (data/topics/universal_clean_k50_seed0/assignments.jsonl),
                joined with the processed labels by split and raw row; one row per named topic and per
                unnamed cluster; texts not in the pool are counted by reason
  balance       NEG / NEU / POS per split, imbalance = largest / smallest class
  script        per text, Arabic share of its Arabic + Latin letters (row-8 letter rules, links and
                mentions removed), in 10-point bins centred on 0, 10, ..., 100
  self_bleu     Self-BLEU-4 (src.quality.lexical.self_bleu) on 1,000 random texts, seeds 0-4, shared
                tokenisation of scripts/quality/measure_dataset_quality.py; EESA plus comparison sets

Outputs: results/quality/sentiment/eesa_explore.json and .md (numbers only, no text).

Usage:
  python -m src.sentiment.explore_eesa
  python -m src.sentiment.explore_eesa --limit 200     # tiny mode: Self-BLEU on 200 texts, 2 seeds
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.quality.measure_dataset_quality import tokens  # noqa: E402
from scripts.topics.fit_topics import clean_for_topics  # noqa: E402
from src.data.build_dataset import git_commit  # noqa: E402
from src.quality.lexical import self_bleu  # noqa: E402
from src.quality.measure import ARABIC_LETTER_RE, LATIN_LETTER_RE, PLACEHOLDER_RE, observed_script, script_features  # noqa: E402

PROC = ROOT / "data" / "processed" / "sentiment"
TOPICS = ROOT / "data" / "topics" / "universal_clean_k50_seed0"
NAMES = ROOT / "configs" / "quality" / "topic_names_universal_clean_k50.json"
OUT = ROOT / "results" / "quality" / "sentiment" / "eesa_explore"
SPLITS = {"train": "Train", "dev": "Dev", "test": "Test"}
CLASSES = ["NEG", "NEU", "POS"]
# Comparison sets for Self-BLEU (same size and seeds as EESA).
COMPARE = {
    "SG01-EASA Fanar": ROOT / "data/synthetic/sentiment/sg01_eesa_fanar.selected.jsonl",
    "SG01-EASA Qwen3": ROOT / "data/synthetic/sentiment/sg01_eesa_qwen3.selected.jsonl",
    "SG01-EASA Aya": ROOT / "data/synthetic/sentiment/sg01_eesa_aya.selected.jsonl",
    "ArSarcasm-v2 train (S1)": PROC / "arsarcasm_v2_train.jsonl",
}
# SG02-EESA and SG02-random-EESA (D-034), SG04-EESA and SG04-random-EESA (D-038), SG03-EESA matrix arms (D-037).
for _g, _n in [("fanar", "Fanar"), ("qwen3", "Qwen3"), ("aya", "Aya")]:
    for _tag, _name in [("sg02_eesa", "SG02-EESA"), ("sg02r_eesa", "SG02-random-EESA"),
                        ("sg04_eesa", "SG04-EESA"), ("sg04r_eesa", "SG04-random-EESA"),
                        ("sg03nm_eesa", "SG03-EESA-NM"), ("sg03dm_eesa", "SG03-EESA-DM"),
                        ("sg03dm3_eesa", "SG03-EESA-DM3"), ("sg03em_eesa", "SG03-EESA-EM")]:
        if (ROOT / f"data/synthetic/sentiment/{_tag}_{_g}.selected.jsonl").exists():
            COMPARE[f"{_name} {_n}"] = ROOT / f"data/synthetic/sentiment/{_tag}_{_g}.selected.jsonl"


def read_jsonl(path: Path) -> list[dict]:
    """All records of a JSONL file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def pct(x: float) -> str:
    """Percentage with one decimal."""
    return f"{100 * x:.1f}%"


# ---------------------------------------------------------------- topics

def topics(records: list[dict]) -> dict:
    """Universal-topic shares of EESA texts in the pool, with class mix per topic and exclusion reasons."""
    names = json.loads(NAMES.read_text(encoding="utf-8"))
    cluster_name = {c: n for n, cs in names["topics"].items() for c in cs}
    # Pool ids are "EESA:EESA-<Split>.csv:<0-based csv row>"; processed raw_rows are 1-based.
    by_key = {(r["split"], rr - 1): r for r in records for rr in r["raw_rows"]}
    split_of = {v: k for k, v in SPLITS.items()}
    in_pool: dict[str, int] = {}
    with open(TOPICS / "assignments.jsonl", encoding="utf-8") as f:
        for line in f:
            a = json.loads(line)
            if not a["text_id"].startswith("EESA:"):
                continue
            _, file, row = a["text_id"].split(":")
            r = by_key.get((split_of[file[len("EESA-"):-len(".csv")]], int(row)))
            if r is not None:
                in_pool[r["text_id"]] = a["cluster"]

    rows: dict[str, Counter] = defaultdict(Counter)
    for r in records:
        c = in_pool.get(r["text_id"])
        if c is None:
            continue
        key = cluster_name.get(c, "Unclustered")      # all unnamed clusters in one row (Ammar, 2026-11-10)
        rows[key][r["sentiment"]] += 1
    n_pool = sum(sum(c.values()) for c in rows.values())

    # Why the other texts are missing: pool rules (row-8 script, under 5 words, repeat).
    reasons = Counter()
    clean = json.loads((TOPICS / "meta.json").read_text(encoding="utf-8"))["config"]["clean"]
    for r in records:
        if r["text_id"] in in_pool:
            continue
        raw = r.get("text_raw", r["text"])
        if observed_script(script_features(raw)) != "arabic":
            reasons["not Arabic script"] += 1
        elif len(clean_for_topics(raw, clean).split()) < clean["min_words"]:
            reasons["under 5 words"] += 1
        else:
            reasons["repeat of an earlier pool text"] += 1

    table = []
    for k, c in sorted(rows.items(), key=lambda kv: -sum(kv[1].values())):
        n = sum(c.values())
        table.append({"topic": k, "named": k != "Unclustered", "n": n, "share": n / n_pool,
                      **{cl: c[cl] / n for cl in CLASSES}})
    return {"n_total": len(records), "n_in_pool": n_pool, "not_in_pool": dict(reasons), "rows": table}


# ---------------------------------------------------------------- class balance

def balance(records: list[dict]) -> list[dict]:
    """Class counts, shares and imbalance per split and for all splits."""
    out = []
    for name in [*SPLITS, "all"]:
        rs = records if name == "all" else [r for r in records if r["split"] == name]
        c = Counter(r["sentiment"] for r in rs)
        out.append({"split": name, "n": len(rs), **{cl: c[cl] for cl in CLASSES},
                    "imbalance": max(c.values()) / min(c.values())})
    return out


# ---------------------------------------------------------------- script mix

def script_bins(records: list[dict]) -> dict:
    """Share of texts per 10-point bin of Arabic letters among Arabic + Latin letters."""
    bins, no_letters, other_letters = Counter(), 0, 0
    for r in records:
        t = PLACEHOLDER_RE.sub(" ", r.get("text_raw", r["text"]))
        ar, lat = len(ARABIC_LETTER_RE.findall(t)), len(LATIN_LETTER_RE.findall(t))
        if sum(ch.isalpha() for ch in t) > ar + lat:
            other_letters += 1        # e.g. Korean; those letters are ignored
        if ar + lat == 0:
            no_letters += 1
            continue
        bins[min(10, int(10 * ar / (ar + lat) + 0.5))] += 1     # bin b = Arabic share in [10b-5, 10b+5)
    n = len(records)
    rows = []
    for b in range(10, -1, -1):
        lo, hi = max(0, 10 * b - 5), min(100, 10 * b + 5)
        rows.append({"arabic": f"{lo}-{hi}%", "latin": f"{100 - hi}-{100 - lo}%", "n": bins[b], "share": bins[b] / n})
    return {"n": n, "rows": rows, "no_arabic_or_latin_letters": no_letters, "texts_with_other_letters": other_letters}


# ---------------------------------------------------------------- Self-BLEU

def self_bleu_runs(texts: list[str], n: int, seeds: range) -> dict:
    """Self-BLEU on n random texts per seed; mean and std over the seeds."""
    vals = [self_bleu([tokens(t) for t in random.Random(s).sample(texts, n)]) for s in seeds]
    return {"n_texts": n, "seeds": list(seeds), "mean": statistics.mean(vals),
            "std": statistics.stdev(vals) if len(vals) > 1 else 0.0, "values": vals}


def universal19() -> dict:
    """Effective number of universal topics, 18 named + all unnamed clusters as one 'Unclustered' topic.

    exp(entropy) of the whole-set shares stored by src.quality.topic_spread; no texts are re-embedded.
    """
    out = {}
    # One topic_spread file per generation round; the real set is the same in each (first one kept).
    for f in sorted((ROOT / "results/quality/sentiment").glob("universal_topics_sg0*_eesa*.json")):
        d = json.loads(f.read_text(encoding="utf-8"))
        for k, s in d["sets"].items():
            if k in out:
                continue
            sh = [p for p in s["topic_shares"].values() if p > 0]     # "unnamed" is one share = Unclustered
            out[k] = {"n_scored": s["n_scored"], "effective": math.exp(-sum(p * math.log(p) for p in sh))}
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--limit", type=int, default=None, help="tiny mode: Self-BLEU on N texts, seeds 0-1")
    args = p.parse_args()
    t0 = time.time()
    n_bleu, seeds = (args.limit, range(2)) if args.limit else (1000, range(5))

    records = [r for s in SPLITS for r in read_jsonl(PROC / f"eesa_{s}.jsonl")]
    sets = {"EESA train": [r["text"] for r in records if r["split"] == "train"],
            "EESA all splits": [r["text"] for r in records]}
    sets |= {k: [r["text"] for r in read_jsonl(v) if r.get("text")] for k, v in COMPARE.items()}
    bleu = {k: self_bleu_runs(v, n_bleu, seeds) for k, v in sets.items() if len(v) >= n_bleu}

    res = {"topics": topics(records), "balance": balance(records), "script": script_bins(records),
           "self_bleu": bleu, "universal19": universal19(), "git_commit": git_commit(), "seconds": None}
    res["seconds"] = round(time.time() - t0, 1)
    suffix = f"_limit{args.limit}" if args.limit else ""
    OUT.parent.mkdir(parents=True, exist_ok=True)
    Path(f"{OUT}{suffix}.json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")

    # Markdown tables
    tp = res["topics"]
    md = ["# EESA exploration", "",
          f"Generated by `python -m src.sentiment.explore_eesa` (git {res['git_commit'][:7]}). Do not edit by hand.", "",
          f"## Universal topics ({tp['n_in_pool']:,} of {tp['n_total']:,} texts in the pool)", "",
          "| Topic | Texts | Share | NEG / NEU / POS |", "|---|---|---|---|"]
    md += [f"| {r['topic']} | {r['n']:,} | {pct(r['share'])} | {r['NEG']:.0%} / {r['NEU']:.0%} / {r['POS']:.0%} |"
           for r in tp["rows"]]
    md += ["", "Not in the pool: " + ", ".join(f"{k} {v:,}" for k, v in tp["not_in_pool"].items()), "",
           "## Class balance", "", "| Split | Texts | NEG | NEU | POS |", "|---|---|---|---|---|"]
    md += [f"| {b['split']} | {b['n']:,} | " + " | ".join(f"{b[c] / b['n']:.1%} ({b[c]:,})" for c in CLASSES)
           + " |" for b in res["balance"]]
    sc = res["script"]
    md += ["", f"## Script mix ({sc['n']:,} texts)", "", "| share | Arabic Script perc | Latin Script Perc | Texts |",
           "|---|---|---|---|"]
    md += [f"| {pct(r['share'])} | {r['arabic']} | {r['latin']} | {r['n']:,} |" for r in sc["rows"]]
    md += ["", f"No Arabic or Latin letter: {sc['no_arabic_or_latin_letters']}; "
           f"texts with other letters (ignored): {sc['texts_with_other_letters']}.", "",
           f"## Self-BLEU ({n_bleu:,} texts, seeds {seeds.start}-{seeds.stop - 1})", "",
           "| Set | Self-BLEU |", "|---|---|"]
    md += [f"| {k} | {v['mean']:.4f} ± {v['std']:.4f} |" for k, v in bleu.items()]
    md += ["", "## Effective universal topics (of 19: 18 named + Unclustered)", "",
           "exp(entropy) of the whole-set topic shares in `universal_topics_sg01_eesa.json` (no sampling).", "",
           "| Set | Scored texts | Effective topics (of 19) |", "|---|---|---|"]
    md += [f"| {k} | {v['n_scored']:,} | {v['effective']:.2f} |" for k, v in res["universal19"].items()]
    Path(f"{OUT}{suffix}.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))
    print(f"done in {res['seconds']}s")


if __name__ == "__main__":
    main()
