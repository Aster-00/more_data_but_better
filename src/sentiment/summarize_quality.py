"""One table of every sentiment dataset: quality measures plus the mean BERT score when trained on it.

Rows: the real S1 train set and every synthetic set measured by src.sentiment.measure_quality
(results/quality/sentiment/<set>_quality.json; SG01, SG02, SG03, SG03-random, per generator).
Columns:
  quality      imbalance, MSA share, dialectness, MTLD, topic spread (of 30, S1-train k-means),
               Vendi, repeats, fidelity (+ per class) from the <set>_quality.json files
  topics       effective clusters / named topics on the universal topic list (src.quality.topic_spread,
               results/quality/sentiment/universal_topics*.json), matched by file path
  performance  the BERTs trained on S1 train + that set (real: SR01, SG01: SR02, SG02: SR04,
               SG03: SR05, SG03-random: SR06): per BERT the mean over its finished seeds, then the
               mean over the BERTs; dev and test macro F1, test F1 per class, and the change against
               SR01 over the same BERTs. Only BERTs: the synthetic runs train BERTs only, and the
               LLM classifiers of SR01 would make the real row incomparable.
Read-only: nothing is measured or trained here.

Outputs: docs/sentiment/tables/dataset_quality.{csv,md} (generated, never edited by hand).

Usage:
  python -m src.sentiment.summarize_quality
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from pathlib import Path

QUALITY_DIR = Path("results/quality/sentiment")
RUNS_DIR = Path("results/sentiment/runs")
OUT_DIR = Path("docs/sentiment/tables")
SETS = ["sg01", "sg02", "sg03", "sg03r"]
SET_NAMES = {"sg01": "SG01", "sg02": "SG02", "sg03": "SG03", "sg03r": "SG03-random"}
TRAIN_RUN = {"real": "sr01", "sg01": "sr02", "sg02": "sr04", "sg03": "sr05", "sg03r": "sr06"}
GEN_NAMES = {"jais2": "Jais-2", "fanar": "Fanar", "qwen3": "Qwen3", "aya": "Aya"}
BERTS = ["marbertv2", "arabertv02_twitter", "marbert", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"]
QUALITY = ["imbalance", "msa_share", "dialectness", "mtld", "topic_spread", "vendi", "repeats", "fidelity"]
SCORES = ["dev_macro_f1", "test_macro_f1", "test_f1_NEG", "test_f1_NEU", "test_f1_POS"]


def bert_scores(pattern: str) -> dict[str, dict[str, float]]:
    """Per BERT: the scores averaged over its finished seeds (folders pattern.format(bert=...) + "_seed<N>")."""
    out = {}
    for b in BERTS:
        logs = [json.loads((d / "train_log.json").read_text(encoding="utf-8"))
                for d in sorted(RUNS_DIR.glob(pattern.format(bert=b) + "_seed*"))
                # Smoke tests ("_limit<N>") are not results.
                if re.fullmatch(r".*_seed\d+", d.name) and (d / "train_log.json").exists()]
        if not logs:
            continue
        out[b] = {"seeds": len(logs),
                  "dev_macro_f1": statistics.fmean(l["dev"]["macro"]["f1"] for l in logs),
                  "test_macro_f1": statistics.fmean(l["test"]["macro"]["f1"] for l in logs),
                  **{f"test_f1_{c}": statistics.fmean(l["test"]["per_class"][c]["f1"] for l in logs)
                     for c in ("NEG", "NEU", "POS")}}
    return out


def topic_rows() -> dict[str, dict]:
    """Universal topic spread per data file path (later files win for a path measured twice)."""
    out = {}
    for f in sorted(QUALITY_DIR.glob("universal_topics*.json")):
        for s in json.loads(f.read_text(encoding="utf-8"))["sets"].values():
            out[Path(s["path"]).name] = s
    return out


def main() -> None:
    """Build the rows and write the CSV and Markdown tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    topics = topic_rows()
    real_scores = bert_scores("sr01_{bert}")
    rows = []
    # Real reference: identical in every quality file (same samples and seeds), taken from the first.
    for tag in SETS:
        path = QUALITY_DIR / f"{tag}_quality.json"
        if not path.exists():
            continue
        q = json.loads(path.read_text(encoding="utf-8"))
        if not rows:
            rows.append({"dataset": "S1 real (train)", "set": "real", "generator": "", "file": "arsarcasm_v2_train.jsonl",
                         **q["sets"]["real"]})
        for g, s in q["sets"].items():
            if g != "real":
                rows.append({"dataset": f"{SET_NAMES[tag]} {GEN_NAMES[g]}", "set": tag, "generator": g,
                             "file": f"{tag}_{g}.selected.jsonl", **s})

    for r in rows:
        # Fidelity per class and universal topics.
        for c, v in (r.pop("fidelity_per_class", None) or {}).items():
            r[f"fidelity_{c}"] = v
        t = topics.get(r["file"], {})
        r["universal_clusters"], r["universal_named"] = t.get("effective_clusters"), t.get("effective_named")
        # Mean BERT scores when trained on this set, and the change against real only over the same BERTs.
        sc = real_scores if r["set"] == "real" else bert_scores(f"{TRAIN_RUN[r['set']]}_{{bert}}_{r['generator']}")
        r["train_run"] = TRAIN_RUN[r["set"]].upper()
        r["n_berts"], r["n_runs"] = len(sc), sum(v["seeds"] for v in sc.values())
        for k in SCORES:
            r[k] = statistics.fmean(v[k] for v in sc.values()) if sc else None
        same = [b for b in sc if b in real_scores]
        for k in ("dev_macro_f1", "test_macro_f1", "test_f1_NEU"):
            r[f"delta_{k}"] = (statistics.fmean(sc[b][k] - real_scores[b][k] for b in same)
                               if same and r["set"] != "real" else None)
        r.pop("name", None)

    cols = (["dataset", "set", "generator", "n"] + QUALITY + ["fidelity_NEG", "fidelity_NEU", "fidelity_POS",
            "universal_clusters", "universal_named", "train_run", "n_berts", "n_runs"] + SCORES
            + ["delta_dev_macro_f1", "delta_test_macro_f1", "delta_test_f1_NEU"])
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dataset_quality.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    # Markdown: rounded, one table for quality, one for performance.
    def fmt(v, spec: str) -> str:
        return "–" if v is None else spec.format(v)
    md = ["# Sentiment datasets: quality and BERT performance", "",
          "Generated by `python -m src.sentiment.summarize_quality` from `results/quality/sentiment/*_quality.json`, "
          "`universal_topics*.json` and the run folders. Do not edit by hand. Quality: SQ01 measures (SD-005); "
          "fidelity = SR01 MARBERT judge (real: accuracy on S1 dev). Performance: mean over the BERTs trained on "
          "S1 train + the set (per BERT the mean of its finished seeds); Δ = change against SR01 over the same BERTs.", "",
          "## Quality", "",
          "| Dataset | Texts | Imbalance | MSA share | Dialectness | MTLD | Topics (of 30) | Universal clusters (of 50) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['dataset']} | {r['n']:,} | {fmt(r['imbalance'], '{:.1f} : 1')} | {fmt(r['msa_share'], '{:.1%}')} | "
                  f"{fmt(r['dialectness'], '{:.2f}')} | {fmt(r['mtld'], '{:.0f}')} | {r['topic_spread']} | "
                  f"{fmt(r['universal_clusters'], '{:.1f}')} | {fmt(r['vendi'], '{:.1f}')} | {fmt(r['repeats'], '{:.1%}')} | "
                  f"{fmt(r['fidelity'], '{:.1%}')} ({fmt(r.get('fidelity_NEG'), '{:.0%}')} / {fmt(r.get('fidelity_NEU'), '{:.0%}')} / "
                  f"{fmt(r.get('fidelity_POS'), '{:.0%}')}) |")
    md += ["", "## Mean BERT performance when trained on S1 train + the set", "",
           "| Dataset | Run | BERTs (runs) | Dev macro F1 | Test macro F1 | Test F1 NEG / NEU / POS | Δ dev | Δ test | Δ test NEU |",
           "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['dataset']} | {r['train_run']} | {r['n_berts']} ({r['n_runs']}) | {fmt(r['dev_macro_f1'], '{:.2f}')} | "
                  f"{fmt(r['test_macro_f1'], '{:.2f}')} | {fmt(r['test_f1_NEG'], '{:.1f}')} / {fmt(r['test_f1_NEU'], '{:.1f}')} / "
                  f"{fmt(r['test_f1_POS'], '{:.1f}')} | {fmt(r['delta_dev_macro_f1'], '{:+.2f}')} | "
                  f"{fmt(r['delta_test_macro_f1'], '{:+.2f}')} | {fmt(r['delta_test_f1_NEU'], '{:+.2f}')} |")
    with open(OUT_DIR / "dataset_quality.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[6:]))


if __name__ == "__main__":
    sys.exit(main())
