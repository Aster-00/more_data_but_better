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
               mean over the BERTs; dev and test macro F1 and F1-PN, test F1 per class, and the change against
               SR01 over the same BERTs. Only BERTs: the synthetic runs train BERTs only, and the
               LLM classifiers of SR01 would make the real row incomparable.
EESA rows (D-032): the EESA real train set and the sets generated for EESA (SG01-EESA: SR02-EESA,
SG03-EESA: SR05-EESA, SG03-random-EESA: SR06-EESA); their Δ is against SR01-EESA, not SR01.
Read-only: nothing is measured or trained here.

Outputs: docs/sentiment/datasets/dataset_quality.{csv,md} (generated, never edited by hand).

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
OUT_DIR = Path("docs/sentiment/datasets")   # moved from tables/ in commit ddc7684
SETS = ["sg01", "sg02", "sg03", "sg03r", "sg04", "sg04pn", "sg01_eesa", "sg03_eesa", "sg03r_eesa"]
SET_NAMES = {"sg01": "SG01", "sg02": "SG02", "sg03": "SG03", "sg03r": "SG03-random", "sg04": "SG04 (test-contaminated)",
             "sg04pn": "SG04-PN (test-contaminated)", "sg01_eesa": "SG01-EESA", "sg03_eesa": "SG03-EESA",
             "sg03r_eesa": "SG03-random-EESA"}
TRAIN_RUN = {"real": "sr01", "sg01": "sr02", "sg02": "sr04", "sg03": "sr05", "sg03r": "sr06", "sg04": "sr07", "sg04pn": "sr12_3600",
             "real_eesa": "sr01_eesa", "sg01_eesa": "sr02_eesa", "sg03_eesa": "sr05_eesa", "sg03r_eesa": "sr06_eesa"}
# Run labels as in the registry (EESA runs: SR02-EESA etc.); the others keep their old label.
RUN_LABEL = {k: v.upper().replace("_EESA", "-EESA") for k, v in TRAIN_RUN.items()}
# Real set and real-only run per corpus; EESA sets end in _eesa.
REAL = {"ArSarcasm-v2": ("real", "S1 real (train)", "arsarcasm_v2_train.jsonl"),
        "EESA": ("real_eesa", "EESA real (train)", "eesa_train.jsonl")}
GEN_NAMES = {"jais2": "Jais-2", "fanar": "Fanar", "qwen3": "Qwen3", "aya": "Aya"}
BERTS = ["marbertv2", "arabertv02_twitter", "marbert", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"]
QUALITY = ["imbalance", "msa_share", "dialectness", "mtld", "topic_spread", "vendi", "repeats", "fidelity"]
SCORES = ["dev_macro_f1", "test_macro_f1", "dev_f1_pn", "test_f1_pn", "test_f1_NEG", "test_f1_NEU", "test_f1_POS"]
DELTAS = ["dev_macro_f1", "test_macro_f1", "dev_f1_pn", "test_f1_pn", "test_f1_NEU"]


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
                  "dev_f1_pn": statistics.fmean(l["dev"]["f1_pn"] for l in logs),
                  "test_f1_pn": statistics.fmean(l["test"]["f1_pn"] for l in logs),
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
    real_scores = {c: bert_scores(f"{TRAIN_RUN[REAL[c][0]]}_{{bert}}") for c in REAL}
    rows, seen = [], set()
    # Real reference per corpus: identical in every quality file of that corpus, taken from the first.
    for tag in SETS:
        path = QUALITY_DIR / f"{tag}_quality.json"
        if not path.exists():
            continue
        q = json.loads(path.read_text(encoding="utf-8"))
        corpus = "EESA" if tag.endswith("_eesa") else "ArSarcasm-v2"
        if corpus not in seen:
            seen.add(corpus)
            key, name, file = REAL[corpus]
            rows.append({"dataset": name, "set": key, "corpus": corpus, "generator": "", "file": file, **q["sets"]["real"]})
        for g, s in q["sets"].items():
            if g != "real":
                rows.append({"dataset": f"{SET_NAMES[tag]} {GEN_NAMES[g]}", "set": tag, "corpus": corpus, "generator": g,
                             "file": f"{tag}_{g}.selected.jsonl", **s})

    for r in rows:
        # Fidelity per class and universal topics.
        for c, v in (r.pop("fidelity_per_class", None) or {}).items():
            r[f"fidelity_{c}"] = v
        t = topics.get(r["file"], {})
        r["universal_clusters"], r["universal_named"] = t.get("effective_clusters"), t.get("effective_named")
        # Mean BERT scores when trained on this set, and the change against real only over the same BERTs.
        base = real_scores[r["corpus"]]
        is_real = r["set"] in ("real", "real_eesa")
        sc = base if is_real else bert_scores(f"{TRAIN_RUN[r['set']]}_{{bert}}_{r['generator']}")
        r["train_run"] = RUN_LABEL[r["set"]]
        r["n_berts"], r["n_runs"] = len(sc), sum(v["seeds"] for v in sc.values())
        for k in SCORES:
            r[k] = statistics.fmean(v[k] for v in sc.values()) if sc else None
        same = [b for b in sc if b in base]
        for k in DELTAS:
            r[f"delta_{k}"] = (statistics.fmean(sc[b][k] - base[b][k] for b in same)
                               if same and not is_real else None)
        r.pop("name", None)

    cols = (["dataset", "set", "generator", "n"] + QUALITY + ["fidelity_NEG", "fidelity_NEU", "fidelity_POS",
            "universal_clusters", "universal_named", "train_run", "n_berts", "n_runs"] + SCORES
            + [f"delta_{k}" for k in DELTAS])
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
          "S1 train + the set (per BERT the mean of its finished seeds); Δ = change against SR01 over the same BERTs. "
          "F1-PN = mean F1 of POS and NEG, the official ArSarcasm-v2 metric.", "",
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
           "| Dataset | Run | BERTs (runs) | Dev macro F1 | Dev F1-PN | Test macro F1 | Test F1-PN | Test F1 NEG / NEU / POS | "
           "Δ dev | Δ dev F1-PN | Δ test | Δ test F1-PN | Δ test NEU |",
           "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['dataset']} | {r['train_run']} | {r['n_berts']} ({r['n_runs']}) | {fmt(r['dev_macro_f1'], '{:.2f}')} | "
                  f"{fmt(r['dev_f1_pn'], '{:.2f}')} | {fmt(r['test_macro_f1'], '{:.2f}')} | {fmt(r['test_f1_pn'], '{:.2f}')} | "
                  f"{fmt(r['test_f1_NEG'], '{:.1f}')} / {fmt(r['test_f1_NEU'], '{:.1f}')} / "
                  f"{fmt(r['test_f1_POS'], '{:.1f}')} | {fmt(r['delta_dev_macro_f1'], '{:+.2f}')} | "
                  f"{fmt(r['delta_dev_f1_pn'], '{:+.2f}')} | {fmt(r['delta_test_macro_f1'], '{:+.2f}')} | "
                  f"{fmt(r['delta_test_f1_pn'], '{:+.2f}')} | {fmt(r['delta_test_f1_NEU'], '{:+.2f}')} |")
    with open(OUT_DIR / "dataset_quality.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[6:]))


if __name__ == "__main__":
    sys.exit(main())
