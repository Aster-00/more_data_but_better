"""Quality measures for one data set (real or synthetic), written to results/quality/<name>.json.

Measures (pipeline stage 5):
  duplicates   exact and near-duplicate rates within the set, and near-duplicate rate against D1
  lexical      TTR, distinct-1/2, MTLD, Self-BLEU (whitespace tokens, no normalization)
  embedding    E5 mean pairwise cosine distance and Vendi score (Friedman & Dieng 2022)
  fidelity     CAMeLBERT DID top-1 agreement with the target dialect (both variants), ALDi distribution
  adherence    controlled sets: share of texts that follow each control factor (script, length,
               code-switching); topic needs a judge and is left as TODO
  kappa        Cohen's kappa between the two DID scorers, and between each scorer and the target

The same script runs on a real D1 sample (`--sample`), where the target dialect of a text is
its single valid label (texts with 0 or several valid dialects have no target and are only
used for the label-free measures). Sizes should be matched when comparing sets.

Usage:
  python -m src.quality.measure --data data/synthetic/open_v1_fanar.jsonl --name open_v1_fanar
  python -m src.quality.measure --data data/processed/nadi_lahjatbert.jsonl --name real_d1_sample2000 --sample 2000
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import re
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
from sklearn.metrics import cohen_kappa_score

from src.data.build_dataset import DIALECTS, git_commit, sha256
from src.filtering.dedup import dedup_key, exact_duplicates, near_duplicates_against, near_duplicates_within
from src.quality.lexical import lexical_summary

ARABIC_LETTER_RE = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{2,}")
PLACEHOLDER_RE = re.compile(r"\b(?:USER|URL)\b")


# ---------------------------------------------------------------- loading

def load_records(path: Path, sample: int | None, seed: int) -> list[dict]:
    """Read a JSONL set; keep records with text; optionally take a seeded random sample."""
    with open(path, encoding="utf-8") as f:
        records = [json.loads(l) for l in f if l.strip()]
    records = [r for r in records if r.get("text")]
    if sample is not None and sample < len(records):
        records = random.Random(seed).sample(records, sample)
    return records


def target_of(r: dict) -> str | None:
    """Target dialect: synthetic records carry it; real records only if exactly one dialect is valid."""
    if r.get("source") == "synthetic":
        return r["target_dialect"]
    valid = [d for d, v in r["labels"].items() if v == 1]
    return valid[0] if len(valid) == 1 else None


# ---------------------------------------------------------------- script / code-switching features

def script_features(text: str) -> dict:
    """Arabic and Latin letter shares and the number of Latin-script words (placeholders removed)."""
    t = PLACEHOLDER_RE.sub(" ", text)
    letters = sum(c.isalpha() for c in t)
    ar = len(ARABIC_LETTER_RE.findall(t))
    lat = len(LATIN_LETTER_RE.findall(t))
    return {"letters": letters, "arabic_share": ar / letters if letters else 0.0,
            "latin_share": lat / letters if letters else 0.0, "latin_words": len(LATIN_WORD_RE.findall(t))}


def observed_script(f: dict, min_share: float = 0.7) -> str:
    """'arabic', 'arabizi' or 'mixed' from the letter shares."""
    if f["arabic_share"] >= min_share:
        return "arabic"
    if f["latin_share"] >= min_share:
        return "arabizi"
    return "mixed"


def observed_code_switching(f: dict) -> str:
    """'none' (0 Latin words), 'light' (1-2) or 'heavy' (3+); only meaningful for Arabic-script text."""
    return "none" if f["latin_words"] == 0 else ("light" if f["latin_words"] <= 2 else "heavy")


# ---------------------------------------------------------------- measures

def duplicate_measures(texts: list[str], cfg: dict, reference: Path | None) -> dict:
    """Exact / near-duplicate rates within the set and against the reference (D1)."""
    keys = [dedup_key(t) for t in texts]
    exact = exact_duplicates(keys)
    near = near_duplicates_within(keys, cfg["near_threshold"], cfg["ngram"])
    out = {"n": len(texts), "exact_duplicates": len(exact), "exact_rate": round(len(exact) / max(1, len(texts)), 4),
           "near_duplicates": len(near), "near_rate": round(len(near) / max(1, len(texts)), 4),
           "near_threshold": cfg["near_threshold"], "ngram": cfg["ngram"]}
    if reference is not None:
        with open(reference, encoding="utf-8") as f:
            ref_keys = [dedup_key(json.loads(l)["text"]) for l in f if l.strip()]
        against = near_duplicates_against(keys, ref_keys, cfg["near_threshold"], cfg["ngram"])
        out.update(near_vs_reference=len(against), near_vs_reference_rate=round(len(against) / max(1, len(texts)), 4),
                   reference=str(reference))
    return out


def embedding_measures(texts: list[str], cfg: dict, device: str, cache_dir: Path) -> dict:
    """Mean pairwise cosine distance and Vendi score of E5 embeddings (on at most `max_n` texts)."""
    from src.quality.scorers import E5Embedder
    if len(texts) > cfg["max_n"]:
        texts = random.Random(cfg["seed"]).sample(texts, cfg["max_n"])
    emb = E5Embedder(cache_dir, device).embed(texts).astype(np.float64)
    n = len(emb)
    if n < 2:
        return {"n": n}
    # Mean off-diagonal cosine similarity via ||sum x||^2 = sum_ij <x_i, x_j>.
    total = float(np.dot(emb.sum(0), emb.sum(0)))
    mean_sim = (total - n) / (n * (n - 1))
    # Vendi score: exp(entropy of the eigenvalues of K/n); K/n and X^T X / n share nonzero eigenvalues.
    eig = np.linalg.eigvalsh(emb.T @ emb / n)
    eig = eig[eig > 1e-12]
    vendi = float(np.exp(-(eig * np.log(eig)).sum()))
    return {"n": n, "model": "intfloat/multilingual-e5-large", "mean_pairwise_cosine_distance": round(1 - mean_sim, 4),
            "vendi_score": round(vendi, 2), "vendi_score_normalized": round(vendi / n, 4)}


def fidelity_measures(records: list[dict], texts: list[str], device: str, cache_dir: Path) -> tuple[dict, dict]:
    """DID agreement per variant, ALDi distribution, and kappa between labellers; also per-record scores."""
    from src.quality.scorers import ALDiScorer, DIDScorer
    targets = [target_of(r) for r in records]
    per_record: dict[str, list] = {}
    out: dict = {}
    for variant in ("nadi", "madar"):
        scorer = DIDScorer(variant, cache_dir, device)
        preds = scorer.predict(texts)
        per_record[f"did_{variant}"] = [p["top_country"] for p in preds]
        # Agreement only where the target is known and the scorer has a label for it.
        pairs = [(t, p["top_country"]) for t, p in zip(targets, preds) if t and scorer.is_covered(t)]
        per_dialect = {}
        for d in DIALECTS:
            dp = [(t, p) for t, p in pairs if t == d]
            if dp:
                per_dialect[d] = {"n": len(dp), "top1_agreement": round(sum(t == p for t, p in dp) / len(dp), 4)}
        out[f"did_{variant}"] = {
            "model": scorer.model_id, "n_scored": len(pairs),
            "n_target_not_covered": sum(1 for t in targets if t and not scorer.is_covered(t)),
            "top1_agreement": round(sum(t == p for t, p in pairs) / len(pairs), 4) if pairs else None,
            "per_dialect": per_dialect,
            "predicted_distribution": dict(Counter(p["top_country"] or "none" for p in preds)),
        }
        del scorer
    aldi = ALDiScorer(cache_dir, device).score(texts)
    per_record["aldi"] = aldi
    hist = Counter(min(int(a * 10), 9) for a in aldi)
    out["aldi"] = {"model": "VARabi/Sentence-ALDi", "n": len(aldi), "mean": round(statistics.fmean(aldi), 4) if aldi else None,
                   "median": round(statistics.median(aldi), 4) if aldi else None,
                   "share_ge_0_5": round(sum(a >= 0.5 for a in aldi) / len(aldi), 4) if aldi else None,
                   "histogram_0.1_bins": {f"{b / 10:.1f}": hist.get(b, 0) for b in range(10)}}

    # Cohen's kappa between labellers, over records where both labels lie in the shared label space.
    kappa = {}
    nadi, madar = per_record["did_nadi"], per_record["did_madar"]
    both = [(a, b) for a, b in zip(nadi, madar) if a and b]
    kappa["did_nadi_vs_did_madar"] = {"n": len(both), "kappa": round(cohen_kappa_score([a for a, _ in both], [b for _, b in both]), 4) if len(both) > 1 else None}
    for name, preds in (("did_nadi", nadi), ("did_madar", madar)):
        pairs = [(t, p) for t, p in zip(targets, preds) if t and p]
        kappa[f"{name}_vs_target"] = {"n": len(pairs), "kappa": round(cohen_kappa_score([t for t, _ in pairs], [p for _, p in pairs]), 4) if len(pairs) > 1 else None}
    out["kappa"] = kappa
    return out, per_record


def adherence_measures(records: list[dict], length_buckets: dict | None) -> dict | None:
    """Share of controlled-generation texts that follow each requested factor value."""
    ctrl = [r for r in records if r.get("condition") == "controlled"]
    if not ctrl:
        return None
    ok: dict[str, list[bool]] = {"script": [], "length": [], "code_switching": []}
    per_level: dict[str, Counter] = {"script": Counter(), "length": Counter(), "code_switching": Counter()}
    totals: dict[str, Counter] = {"script": Counter(), "length": Counter(), "code_switching": Counter()}
    for r in ctrl:
        c, f = r["controls"], script_features(r["text"])
        # Script: observed script equals the requested one.
        s_ok = observed_script(f) == c["script"]
        # Length: word count inside the requested bucket's bounds.
        lo, hi = (length_buckets or {}).get(c["length"], (0, 10**9))
        l_ok = lo <= len(r["text"].split()) <= hi
        for name, flag, level in (("script", s_ok, c["script"]), ("length", l_ok, c["length"])):
            ok[name].append(flag)
            totals[name][level] += 1
            per_level[name][level] += flag
        # Code-switching is measurable only for Arabic-script requests (Latin words = foreign words).
        if c["script"] == "arabic":
            cs_ok = observed_code_switching(f) == c["code_switching"]
            ok["code_switching"].append(cs_ok)
            totals["code_switching"][c["code_switching"]] += 1
            per_level["code_switching"][c["code_switching"]] += cs_ok
    return {
        "n": len(ctrl),
        **{name: {"rate": round(sum(v) / len(v), 4) if v else None,
                  "per_level": {lvl: round(per_level[name][lvl] / totals[name][lvl], 4) for lvl in totals[name]}}
           for name, v in ok.items()},
        "topic": None,  # TODO: needs a topic judge (LLM or human); not measured automatically
        "dialect": "see fidelity.did_*.top1_agreement",
    }


def measure(records: list[dict], cfg: dict, device: str, name: str) -> tuple[dict, dict]:
    """Run every enabled measure; return the report and per-record scores."""
    texts = [r["text"] for r in records]
    cache_dir = Path(cfg["cache_dir"])
    report: dict = {"name": name, "n": len(records),
                    "per_dialect_counts": dict(Counter(target_of(r) or "none" for r in records)),
                    "conditions": dict(Counter(r.get("condition", "real") for r in records))}
    per_record: dict = {}
    # The reference comparison is skipped when the set IS the reference (a D1 sample would match itself).
    reference = Path(cfg["duplicates"]["reference"]) if cfg["duplicates"].get("reference") else None
    if reference is not None and cfg.get("_data_path") and Path(cfg["_data_path"]).resolve() == reference.resolve():
        reference = None
    report["duplicates"] = duplicate_measures(texts, cfg["duplicates"], reference)
    report["lexical"] = lexical_summary(texts)
    if cfg["embedding"]["enabled"]:
        report["embedding"] = embedding_measures(texts, cfg["embedding"], device, cache_dir)
    if cfg["fidelity"]["enabled"]:
        report["fidelity"], per_record = fidelity_measures(records, texts, device, cache_dir)
    report["control_adherence"] = adherence_measures(records, cfg.get("length_buckets"))
    return report, per_record


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, required=True)
    p.add_argument("--name", required=True, help="output name: results/quality/<name>.json")
    p.add_argument("--config", type=Path, default=Path("configs/quality/default.json"))
    p.add_argument("--sample", type=int, default=None, help="seeded random sample of N records")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cuda")
    p.add_argument("--no-models", action="store_true", help="skip E5 and scorer measures (CPU-only smoke test)")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.no_models:
        cfg["embedding"]["enabled"] = cfg["fidelity"]["enabled"] = False
    started = time.time()
    records = load_records(args.data, args.sample, args.seed)
    cfg["_data_path"] = str(args.data)
    report, per_record = measure(records, cfg, args.device, args.name)
    report.update(data=str(args.data), data_sha256=sha256(args.data), sample=args.sample, seed=args.seed,
                  config=cfg, git_commit=git_commit(), python=platform.python_version(),
                  seconds=round(time.time() - started), finished=time.strftime("%Y-%m-%d %H:%M"))

    out_dir = Path("results/quality")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{args.name}.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    # Per-record scorer outputs, for later analysis (text_id -> scores).
    if per_record:
        with open(out_dir / f"{args.name}.scores.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for i, r in enumerate(records):
                f.write(json.dumps({"text_id": r["text_id"], "target": target_of(r),
                                    **{k: v[i] for k, v in per_record.items()}}, ensure_ascii=False) + "\n")
    print(json.dumps({k: report[k] for k in ("n", "duplicates", "lexical", "embedding", "fidelity", "control_adherence") if k in report},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
