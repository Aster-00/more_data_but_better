"""Collect dev-set scores of all logged runs into per-run tables (mean ± std over seeds).

A run (R<NN>) is one fixed setup; each model tried under it is a member R<NN>-<model>.
configs/runs.json maps result folders to members. This script reads
results/runs/*/train_log.json (our trained models) and results/runs/*/dev_metrics.json
(evaluated external models), groups folders that differ only in their seed (name ends in
_seed<N>), and writes:
  results/tables/dev_summary.md    one table per run, one row per model
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
REGISTRY = Path("configs/runs.json")
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
    """Group folders by run and model, average their dev scores over seeds, write the tables."""
    with open(REGISTRY, encoding="utf-8") as f:
        registry = json.load(f)

    # Every folder's dev scores under its name with "_seed<N>" removed, seeds kept in folder order.
    groups: dict[str, list[dict]] = defaultdict(list)
    for run_dir in sorted(p for p in RUNS_DIR.iterdir() if p.is_dir()):
        scores = load_dev_scores(run_dir)
        if scores is not None:
            groups[re.sub(r"_seed\d+$", "", run_dir.name)].append(scores)

    # One row per group: macro P/R/F1, per-seed F1 and per-dialect F1, each as mean and std over seeds.
    # Folders missing from the registry are kept under run "unassigned" so nothing is silently dropped.
    rows = []
    for folder, runs in groups.items():
        member = registry["members"].get(folder, {"run": "unassigned", "model": folder})
        row = {"run": member["run"], "id": f"{member['run']}-{member['model']}", "folder": folder,
               "seeds": len(runs), "seed_f1": " / ".join(f"{r['macro']['f1']:.2f}" for r in runs)}
        for m in ("f1", "precision", "recall"):
            row[f"macro_{m}"], row[f"macro_{m}_std"] = mean_std([r["macro"][m] for r in runs])
        row["micro_f1"], row["micro_f1_std"] = mean_std([r["micro_f1"] for r in runs])
        for d in runs[0]["dialects_scored"]:
            row[f"f1_{d}"], _ = mean_std([r["per_dialect"][d]["f1"] for r in runs])
        rows.append(row)
    # Runs in ID order (unassigned last), models within a run best first.
    rows.sort(key=lambda r: (r["run"] == "unassigned", r["run"], -r["macro_f1"]))

    # CSV with every column.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "dev_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows({k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()} for r in rows)

    # Markdown: per run, a macro-score table and a per-dialect F1 table, one row per model.
    dialects = next(iter(groups.values()))[0]["dialects_scored"]
    lines = ["# MLADI dev set (120 sentences, 8 dialects), threshold 0.3", ""]
    for run_id in dict.fromkeys(r["run"] for r in rows):
        members = [r for r in rows if r["run"] == run_id]
        lines += [f"## {run_id}: {registry['runs'].get(run_id, 'not in configs/runs.json')}", "",
                  "| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |",
                  "|---|---|---|---|---|---|---|---|"]
        for r in members:
            def cell(key: str) -> str:
                return f"{r[key]:.2f}" + (f" ± {r[key + '_std']:.2f}" if r["seeds"] > 1 else "")
            lines.append(f"| {r['id']} | {r['seeds']} | {cell('macro_f1')} | {cell('macro_precision')} "
                         f"| {cell('macro_recall')} | {cell('micro_f1')} | {r['seed_f1']} | `{r['folder']}` |")
        lines += ["", "Per-dialect F1 (mean over seeds):", "",
                  "| ID | " + " | ".join(dialects) + " |", "|---|" + "---|" * len(dialects)]
        for r in members:
            lines.append(f"| {r['id']} | " + " | ".join(f"{r['f1_' + d]:.1f}" for d in dialects) + " |")
        lines.append("")
    (OUT_DIR / "dev_summary.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sys.exit(main())
