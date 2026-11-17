"""EESA: SR09-EESA (+ SG04-EESA, targeted dislike comments) and SR09-random-EESA against the 8-epoch baselines (D-038).

Prints the numbers for the SR09-EASA section of docs/sentiment/chron-EESA.md; writes no files.
  1. Test micro F1 per BERT (mean of 3 seeds) and per generator, against SR05-EESA real only (8 epochs).
  2. Paired comparisons over the 21 BERT x generator pairs (seed means): mean delta, wins / losses / ties,
     two-sided exact sign test (ties dropped); micro and macro F1; mean change of the per-class test F1.
  3. Error rate on dislike comments (regex of src.sentiment.dislike_pools_eesa), mean over the runs of a
     condition: dev (the 15 pool texts, all dev dislike comments) and test (all test dislike comments).
     Dev is dev-contaminated for SR09-EESA (its examples are the 15 dev texts); test is the fair measure.
  4. Epoch kept per run (train_log.json).
Scores from docs/sentiment/tables/sentiment_summary_EESA.csv (run python -m src.sentiment.summarize_runs first).

Usage:
  python -m src.sentiment.compare_eesa_sr09
"""
from __future__ import annotations

import csv
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

from src.sentiment.dislike_pools_eesa import DISLIKE

ROOT = Path(__file__).resolve().parents[2]
TABLE = ROOT / "docs/sentiment/tables/sentiment_summary_EESA.csv"
RUNS = ROOT / "results/sentiment/runs"
PROC = ROOT / "data/processed/sentiment"
POOL = ROOT / "data/inspect/hard_cases/sg04_dislike_errors_eesa.jsonl"
BERTS = ["marbert", "marbertv2", "arabertv02_twitter", "arbert", "arbertv2", "camelbert_mix", "camelbert_da"]
GENS = ["aya", "fanar", "qwen3"]
SEEDS = (42, 43, 44)
# condition -> (registry run, folder prefix); "SR05-EESA:real" = the real-only members of SR05-EESA.
COND = {"SR05-EESA:real": ("SR05-EESA", "sr05_eesa"), "SR05-EESA:sg01": ("SR05-EESA", "sr05_eesa"),
        "SR06-EESA": ("SR06-EESA", "sr06_eesa"), "SR06-random-EESA": ("SR06-random-EESA", "sr06r_eesa"),
        "SR09-EESA": ("SR09-EESA", "sr09_eesa"), "SR09-random-EESA": ("SR09-random-EESA", "sr09r_eesa")}
PAIRS = [("SR09-EESA", "SR05-EESA:real", "SR09-EASA vs real only"),
         ("SR09-EESA", "SR05-EESA:sg01", "SR09-EASA vs zero-shot (+ SG01)"),
         ("SR09-EESA", "SR06-random-EESA", "SR09-EASA vs random few-shot (+ SG02-random)"),
         ("SR09-EESA", "SR06-EESA", "SR09-EASA vs targeted few-shot (+ SG02)"),
         ("SR09-random-EESA", "SR05-EESA:real", "SR09-random-EASA vs real only"),
         ("SR09-EESA", "SR09-random-EESA", "Targeted vs random dislike examples")]


def sign_test(wins: int, losses: int) -> float:
    """Two-sided exact sign test p-value (ties dropped)."""
    n = wins + losses
    if n == 0:
        return 1.0
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(min(wins, losses) + 1)) / 2 ** n)


def folders(cond: str) -> list[Path]:
    """Finished run folders of a condition (all BERTs, generators, seeds)."""
    pre = COND[cond][1]
    gens = [""] if cond == "SR05-EESA:real" else [f"_{g}" for g in GENS]
    out = [RUNS / f"{pre}_{b}{g}_seed{s}" for b in BERTS for g in gens for s in SEEDS]
    return [d for d in out if (d / "train_log.json").exists()]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    score = {}
    for r in csv.DictReader(open(TABLE, encoding="utf-8")):
        if r["train_corpus"] != "EESA" or r["eval_corpus"] != "EESA" or r["split"] != "test":
            continue
        for cond, (run, _) in COND.items():
            if r["run"] == run and (cond != "SR05-EESA:real" or not r["generator"]) \
                    and (cond != "SR05-EESA:sg01" or r["generator"]):
                score[(cond, r["classifier"], r["generator"])] = r

    def get(cond: str, b: str, g: str, m: str) -> float | None:
        r = score.get((cond, b, "" if cond == "SR05-EESA:real" else g))
        return float(r[m]) if r and r[m] else None

    # 1. Per-BERT test micro F1.
    for cond in ("SR09-EESA", "SR09-random-EESA"):
        if not any(k[0] == cond for k in score):
            print(f"\n{cond}: no rows yet"); continue
        print(f"\n## {cond} test micro F1 (Δ vs SR05-EESA real only)")
        means = {g: [] for g in GENS}
        for b in BERTS:
            base = score[("SR05-EESA:real", b, "")]
            cells = []
            for g in GENS:
                v = get(cond, b, g, "micro_f1")
                means[g].append(v)
                cells.append("–" if v is None else f"{v:.2f} ({v - float(base['micro_f1']):+.2f})".replace("-", "−"))
            print(f"| {b} | {float(base['micro_f1']):.2f} ± {float(base['micro_f1_std']):.2f} | " + " | ".join(cells) + " |")
        bm = statistics.fmean(get("SR05-EESA:real", b, "", "micro_f1") for b in BERTS)
        print(f"| mean | {bm:.2f} | " + " | ".join(
            f"{statistics.fmean(v):.2f} ({statistics.fmean(v) - bm:+.2f})" if None not in v else "–" for v in means.values()) + " |")

    # 2. Paired comparisons and per-class change.
    print("\n## Paired comparisons (21 pairs, test)")
    for a, b_, name in PAIRS:
        for m in ("micro_f1", "macro_f1"):
            d = [get(a, b, g, m) - get(b_, b, g, m) for b in BERTS for g in GENS
                 if get(a, b, g, m) is not None and get(b_, b, g, m) is not None]
            if not d:
                continue
            w, l = sum(x > 0 for x in d), sum(x < 0 for x in d)
            print(f"{name} [{m}]: {statistics.fmean(d):+.2f}, {w} / {l} / {len(d) - w - l} (p = {sign_test(w, l):.3f}), n={len(d)}")
        cls = {c: [get(a, b, g, f"f1_{c}") - get(b_, b, g, f"f1_{c}") for b in BERTS for g in GENS
                   if get(a, b, g, f"f1_{c}") is not None and get(b_, b, g, f"f1_{c}") is not None]
               for c in ("NEG", "NEU", "POS")}
        if cls["NEG"]:
            print("   per-class F1 change: " + ", ".join(f"{c} {statistics.fmean(v):+.2f}" for c, v in cls.items()))
        if a.startswith("SR09") and b_ == "SR05-EESA:real" and cls["NEG"]:
            for g in GENS:
                gc = {c: statistics.fmean(get(a, b, g, f"f1_{c}") - get(b_, b, g, f"f1_{c}") for b in BERTS)
                      for c in ("NEG", "NEU", "POS") if all(get(a, b, g, f"f1_{c}") is not None for b in BERTS)}
                if gc:
                    print(f"   {g}: " + ", ".join(f"{c} {v:+.2f}" for c, v in gc.items()))
            strong = [get(a, b, g, "micro_f1") - get(b_, b, g, "micro_f1") for b in BERTS[:3] for g in GENS
                      if get(a, b, g, "micro_f1") is not None]
            weak = [get(a, b, g, "micro_f1") - get(b_, b, g, "micro_f1") for b in BERTS[3:] for g in GENS
                    if get(a, b, g, "micro_f1") is not None]
            print(f"   3 strongest: {statistics.fmean(strong):+.2f} ({sum(x > 0 for x in strong)} of {len(strong)} up); "
                  f"4 weaker: {statistics.fmean(weak):+.2f} ({sum(x > 0 for x in weak)} of {len(weak)} up)")

    # 3. Dislike-comment error rates (dev and test), mean over runs; predicted classes of the errors.
    pool = {json.loads(l)["text_id"] for l in open(POOL, encoding="utf-8")}
    print("\n## Dislike comments: error rate, mean over runs (errors predicted as NEG / NEU / POS)")
    for split in ("dev", "test"):
        data = [json.loads(l) for l in open(PROC / f"eesa_{split}.jsonl", encoding="utf-8")]
        sets = {"all dislike": {i for i, r in enumerate(data) if DISLIKE.search(r["text"])}}
        for c in ("NEG", "NEU", "POS"):
            sets[f"dislike {c}"] = {i for i in sets["all dislike"] if data[i]["sentiment"] == c}
        if split == "dev":
            sets["pool (15)"] = {i for i, r in enumerate(data) if r["text_id"] in pool}
        print(f"\n{split}: " + ", ".join(f"{k} n={len(v)}" for k, v in sets.items()))
        for cond in COND:
            runs = folders(cond)
            if not runs:
                continue
            rate = {k: [] for k in sets}
            pred = {k: Counter() for k in sets}
            for d in runs:
                preds = [json.loads(l) for l in open(d / f"{split}_predictions.jsonl", encoding="utf-8")]
                for k, idx in sets.items():
                    if idx:
                        wrong = [i for i in idx if preds[i]["pred"] != preds[i]["gold"]]
                        rate[k].append(100 * len(wrong) / len(idx))
                        pred[k].update(preds[i]["pred"] for i in wrong)
            print(f"  {cond:18s} runs={len(runs):3d} | " + " | ".join(
                f"{k} {statistics.fmean(v):.1f}%" for k, v in rate.items() if v))
            print(f"  {'':18s} errors predicted as: " + " | ".join(
                f"{k} " + "/".join(str(pred[k][c]) for c in ("NEG", "NEU", "POS")) for k in ("dislike NEG", "dislike NEU")))

    # 4. Epoch kept.
    for cond in ("SR09-EESA", "SR09-random-EESA"):
        ep = Counter(json.load(open(d / "train_log.json", encoding="utf-8")).get("best_epoch") for d in folders(cond))
        if ep:
            print(f"\n{cond} epoch kept: {dict(ep)}")

    # 5. Share of generated texts that mention dislikes (same regex), per set and class.
    print()
    for tag in ("sg04_eesa", "sg04r_eesa"):
        for g in GENS:
            f = ROOT / f"data/synthetic/sentiment/{tag}_{g}.selected.jsonl"
            if f.exists():
                recs = [json.loads(l) for l in open(f, encoding="utf-8")]
                by = {c: [bool(DISLIKE.search(r["text"])) for r in recs if r["sentiment"] == c] for c in ("NEG", "NEU")}
                print(f"{tag}_{g}: mentions dislikes {100 * statistics.fmean(by['NEG'] + by['NEU']):.0f}% "
                      f"(NEG {100 * statistics.fmean(by['NEG']):.0f}%, NEU {100 * statistics.fmean(by['NEU']):.0f}%)")


if __name__ == "__main__":
    main()
