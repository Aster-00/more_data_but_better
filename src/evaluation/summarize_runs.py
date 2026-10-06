"""Collect dev-set scores of all logged runs into one table (mean ± std over seeds).

Reads results/runs/*/train_log.json (our trained models) and results/runs/*/dev_metrics.json
(evaluated external models), groups runs that differ only in their seed (name ends in
_seed<N>), and writes:
  results/tables/dev_summary.md    readable table
  results/tables/dev_summary.csv   same numbers for plotting

Usage:
  python -m src.evaluation.summarize_runs
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

RUNS_DIR = Path("results/runs")
OUT_DIR = Path("results/tables")


def load_dev_scores(run_dir: Path) -> dict | None:
    """Dev scores of one run: from train_log.json (trained) or dev_metrics.json (evaluated only)."""
    train_log = run_dir / "train_log.json"
    if train_log.exists():
        with open(train_log, encoding="utf-8") as f:
            return json.load(f)["dev"]
    dev_metrics = run_dir / "dev_metrics.json"
    if dev_metrics.exists():
        with open(dev_metrics, encoding="utf-8") as f:
            return json.load(f)
    return None


def mean_std(values: list[float]) -> tuple[float, float]:
    """Mean and sample standard deviation (0 when there is a single value)."""
    return statistics.fmean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def main() -> None:
    """Group runs by name without the seed suffix, average their dev scores, write the tables."""
    # Group every run's dev scores under its name with "_seed<N>" removed.
    groups: dict[str, list[dict]] = defaultdict(list)
    for run_dir in sorted(p for p in RUNS_DIR.iterdir() if p.is_dir()):
        scores = load_dev_scores(run_dir)
        if scores is not None:
            groups[re.sub(r"_seed\d+$", "", run_dir.name)].append(scores)

    # One row per group: macro P/R/F1 and per-dialect F1, each as mean and std over seeds.
    rows = []
    for name, runs in groups.items():
        dialects = runs[0]["dialects_scored"]
        row = {"model": name, "seeds": len(runs)}
        for m in ("f1", "precision", "recall"):
            row[f"macro_{m}"], row[f"macro_{m}_std"] = mean_std([r["macro"][m] for r in runs])
        row["micro_f1"], row["micro_f1_std"] = mean_std([r["micro_f1"] for r in runs])
        for d in dialects:
            row[f"f1_{d}"], _ = mean_std([r["per_dialect"][d]["f1"] for r in runs])
        rows.append(row)
    rows.sort(key=lambda r: r["macro_f1"], reverse=True)

    # CSV with every column.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dev_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()} for r in rows)

    # Markdown: macro scores, then per-dialect F1 means (all runs are scored on the same dev dialects).
    dialects = next(iter(groups.values()))[0]["dialects_scored"]
    lines = ["# MLADI dev set (120 sentences, 8 dialects), threshold 0.3", "",
             "| Model | Seeds | Macro F1 | Precision | Recall | Micro F1 |",
             "|---|---|---|---|---|---|"]
    for r in rows:
        def cell(key: str) -> str:
            return f"{r[key]:.2f}" + (f" ± {r[key + '_std']:.2f}" if r["seeds"] > 1 else "")
        lines.append(f"| {r['model']} | {r['seeds']} | {cell('macro_f1')} | {cell('macro_precision')} "
                     f"| {cell('macro_recall')} | {cell('micro_f1')} |")
    lines += ["", "Per-dialect F1 (mean over seeds):", "",
              "| Model | " + " | ".join(dialects) + " |", "|---|" + "---|" * len(dialects)]
    for r in rows:
        lines.append(f"| {r['model']} | " + " | ".join(f"{r['f1_' + d]:.1f}" for d in dialects) + " |")
    (OUT_DIR / "dev_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
