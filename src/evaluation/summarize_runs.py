"""Collect dev-set scores of all logged runs into per-run tables (mean ± std over seeds).

A run (R<NN>) is one fixed setup; each model tried under it is a member R<NN>-<model>.
configs/runs.json maps result folders to members. This script reads
results/runs/*/train_log.json (our trained models) and results/runs/*/dev_metrics.json
(evaluated external models), groups folders that differ only in their seed (name ends in
_seed<N>), and writes:
  results/tables/dev_summary.md    one table per run, one row per model
  results/tables/dev_summary.csv   same numbers for plotting
  results/tables/split_summary.csv three rows per model (train, dev, test), same columns:
    train = held-out validation split of the training data (best epoch), dev = MLADI dev,
    test  = MLADI leaderboard submissions from results/leaderboard.jsonl.
    A row with no scores yet is kept with empty cells, so every model always has all three.

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
from typing import Callable

RUNS_DIR = Path("results/runs")
REGISTRY = Path("configs/runs.json")
OUT_DIR = Path("results/tables")
LEADERBOARD = Path("results/leaderboard.jsonl")
SPLITS = ("train", "dev", "test")


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


def load_train_scores(run_dir: Path) -> dict | None:
    """Validation-split scores of a trained run (best epoch), in the same shape as the dev scores.

    The validation split is the held-out part of the training data, so this is the "train" row.
    Per-dialect scores are not logged for it.
    """
    train_log = run_dir / "train_log.json"
    if not train_log.exists():
        return None
    with open(train_log, encoding="utf-8") as f:
        log = json.load(f)
    # Neural runs log one entry per epoch; TF-IDF + LR logs a single fit at top level.
    best = next((e for e in log.get("epochs", []) if e["epoch"] == log.get("best_epoch")), log)
    if "val_macro" not in best:
        return None
    return {"macro": best["val_macro"], "micro_f1": best["val_micro_f1"], "per_dialect": {}}


def load_test_scores() -> dict[str, list[dict]]:
    """Leaderboard submissions grouped by member ID (R<NN>-<model>), fractions converted to percent."""
    by_id: dict[str, list[dict]] = defaultdict(list)
    if not LEADERBOARD.exists():
        return by_id
    with open(LEADERBOARD, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                by_id[t["run_id"]].append({
                    "macro": {m: 100 * t[m] for m in ("f1", "precision", "recall")},
                    "micro_f1": None, "per_dialect": {}, "test_id": t["test_id"], "run": t["run"]})
    return by_id


def group_by_folder(loader: Callable[[Path], dict | None]) -> dict[str, list[dict]]:
    """Scores of every run folder under its name with "_seed<N>" removed, seeds kept in folder order."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for run_dir in sorted(p for p in RUNS_DIR.iterdir() if p.is_dir()):
        # Tiny-subset smoke tests (--limit N -> "_limit<N>") check that code runs; they are not results.
        if re.search(r"_limit\d+$", run_dir.name):
            continue
        scores = loader(run_dir)
        if scores is not None:
            groups[re.sub(r"_seed\d+$", "", run_dir.name)].append(scores)
    return groups


def mean_std(values: list[float]) -> tuple[float, float]:
    """Mean and sample standard deviation (0 when there is a single value)."""
    return statistics.fmean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def main() -> None:
    """Group folders by run and model, average their dev scores over seeds, write the tables."""
    with open(REGISTRY, encoding="utf-8") as f:
        registry = json.load(f)

    groups = group_by_folder(load_dev_scores)

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
    # Runs in ID order (unassigned last), models within a run best on dev first.
    rows.sort(key=lambda r: (r["run"] == "unassigned", r["run"], -r["macro_f1"]))

    dialects = next(iter(groups.values()))[0]["dialects_scored"]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_split_summary(registry, rows, groups, dialects)
    print(f"wrote {OUT_DIR / 'split_summary.csv'}")


def split_row(base: dict, split: str, runs: list[dict], dialects: list[str]) -> dict:
    """One CSV row for one split of one model: mean and std over seeds, empty cells when not scored."""
    row = {**base, "split": split, "seeds": len(runs)}
    row = {k: row[k] for k in ("run", "id", "split", "folder", "seeds")}
    row["seed_f1"] = " / ".join(f"{r['macro']['f1']:.2f}" for r in runs)
    for m in ("f1", "precision", "recall"):
        row[f"macro_{m}"], row[f"macro_{m}_std"] = mean_std([r["macro"][m] for r in runs]) if runs else ("", "")
    micro = [r["micro_f1"] for r in runs if r["micro_f1"] is not None]
    row["micro_f1"], row["micro_f1_std"] = mean_std(micro) if micro else ("", "")
    for d in dialects:
        per_d = [r["per_dialect"][d]["f1"] for r in runs if d in r["per_dialect"]]
        row[f"f1_{d}"] = mean_std(per_d)[0] if per_d else ""
    # Where the numbers come from; test rows name the submitted seed folder(s).
    if not runs:
        row["source"] = ""
    elif split == "test":
        row["source"] = "MLADI leaderboard (11 dialects): " + ", ".join(f"{r['test_id']} {r['run']}" for r in runs)
    else:
        row["source"] = {"train": "validation split of the training data, best epoch",
                         "dev": "MLADI dev (120 sentences, 8 dialects)"}[split]
    return row


def write_split_summary(registry: dict, dev_rows: list[dict], dev_groups: dict[str, list[dict]],
                        dialects: list[str]) -> None:
    """Write split_summary.csv: train, dev and test rows for every model, in dev_summary order."""
    train_groups = group_by_folder(load_train_scores)
    test_by_id = load_test_scores()

    # Models in dev_summary order, then any model that has validation scores but no dev scores.
    bases = [{"run": r["run"], "id": r["id"], "folder": r["folder"]} for r in dev_rows]
    for folder in train_groups.keys() - {r["folder"] for r in dev_rows}:
        member = registry["members"].get(folder, {"run": "unassigned", "model": folder})
        bases.append({"run": member["run"], "id": f"{member['run']}-{member['model']}", "folder": folder})

    out = []
    for base in bases:
        per_split = {"train": train_groups.get(base["folder"], []),
                     "dev": dev_groups.get(base["folder"], []),
                     "test": test_by_id.get(base["id"], [])}
        out += [split_row(base, s, per_split[s], dialects) for s in SPLITS]

    with open(OUT_DIR / "split_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(out[0]))
        writer.writeheader()
        writer.writerows({k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()} for r in out)


if __name__ == "__main__":
    sys.exit(main())
