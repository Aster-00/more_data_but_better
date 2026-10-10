"""Collect dev-set scores of all logged runs into per-run tables (mean ± std over seeds).

A run (R<NN>) is one fixed setup; each model tried under it is a member R<NN>-<model>.
configs/runs.json maps result folders to members. This script reads
results/runs/*/train_log.json (our trained models) and results/runs/*/dev_metrics.json
(evaluated external models), groups folders that differ only in their seed (name ends in
_seed<N>), and writes:
  docs/tables/split_summary.csv three rows per model (train, dev, test), same columns:
    train = held-out validation split of the training data (best epoch), dev = MLADI dev,
    test  = MLADI leaderboard submissions from results/leaderboard.jsonl.
    A row with no scores yet is kept with empty cells, so every model always has all three.
    The "origin" column marks published models we only scored ("external" in configs/runs.json):
    we have neither their training code nor data, so they cannot be retrained or built on.
  docs/tables/split_summary.md  the same numbers for reading: one table per run, one row per model,
    per-dialect dev F1, and every leaderboard submission with the scores of the submitted seed.

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
OUT_DIR = Path("docs/tables")
LEADERBOARD = Path("results/leaderboard.jsonl")
SPLITS = ("train", "dev", "test")
ORIGIN_OURS = "ours"
ORIGIN_EXTERNAL = "external"


def origin(member: dict) -> str:
    """Whether a model was trained by us or is a published checkpoint we can only evaluate."""
    return ORIGIN_EXTERNAL if member.get("external") else ORIGIN_OURS


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
        row = {"run": member["run"], "id": f"{member['run']}-{member['model']}", "origin": origin(member),
               "folder": folder,
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
    out = write_split_summary(registry, rows, groups, dialects)
    write_split_markdown(registry, out, dialects)
    print(f"wrote {OUT_DIR / 'split_summary.csv'} and {OUT_DIR / 'split_summary.md'}")


def split_row(base: dict, split: str, runs: list[dict], dialects: list[str]) -> dict:
    """One CSV row for one split of one model: mean and std over seeds, empty cells when not scored."""
    row = {**base, "split": split, "seeds": len(runs)}
    row = {k: row[k] for k in ("run", "id", "origin", "split", "folder", "seeds")}
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
                        dialects: list[str]) -> list[dict]:
    """Write split_summary.csv: train, dev and test rows for every model, in dev-table order."""
    train_groups = group_by_folder(load_train_scores)
    test_by_id = load_test_scores()

    # Models in dev-table order, then any model that has validation scores but no dev scores.
    bases = [{"run": r["run"], "id": r["id"], "origin": r["origin"], "folder": r["folder"]} for r in dev_rows]
    for folder in train_groups.keys() - {r["folder"] for r in dev_rows}:
        member = registry["members"].get(folder, {"run": "unassigned", "model": folder})
        bases.append({"run": member["run"], "id": f"{member['run']}-{member['model']}",
                      "origin": origin(member), "folder": folder})

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
    return out


def pm(row: dict, key: str) -> str:
    """A score as "mean ± std" (std left out for one seed), or "—" when the split was not scored."""
    if row[key] == "":
        return "—"
    return f"{row[key]:.2f}" if row["seeds"] < 2 else f"{row[key]:.2f} ± {row[key + '_std']:.2f}"


def fmt(v: float | None) -> str:
    """One score with two decimals, or "—" when missing."""
    return "—" if v is None else f"{v:.2f}"


def write_split_markdown(registry: dict, out: list[dict], dialects: list[str]) -> None:
    """Write split_summary.md: per run a score table and a per-dialect dev table, then the submissions."""
    by_id: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in out:
        by_id[r["id"]][r["split"]] = r
    lines = ["# Scores by split", "",
             "Generated by `python -m src.evaluation.summarize_runs` from `results/runs/*` and "
             "`results/leaderboard.jsonl`. Do not edit by hand. Full precision: `split_summary.csv`.", "",
             "- **Train F1:** macro F1 on the 10% validation split of the training data (automatic labels, "
             "18 dialects), best epoch.",
             "- **Dev:** MLADI dev, 120 human-labelled sentences, 8 dialects, threshold 0.3.",
             "- **Test F1:** MLADI leaderboard, 1,000 sentences, 11 dialects; one submitted seed per model.",
             "- Scores are mean ± std over seeds. *External* models are published checkpoints we only scored.", ""]

    # One section per run, in the order the rows were written (run ID order, best dev F1 first).
    for run in dict.fromkeys(r["run"] for r in out):
        ids = [i for i, s in by_id.items() if s["dev"]["run"] == run]
        lines += [f"## {run}: {registry['runs'].get(run, 'not in configs/runs.json')}", "",
                  "| ID | Seeds | Train F1 | Dev F1 | Dev P | Dev R | Dev micro F1 | Dev F1 per seed | Test F1 | Result folder |",
                  "|---|---|---|---|---|---|---|---|---|---|"]
        for i in ids:
            s = by_id[i]
            dev, label = s["dev"], i + (" *(external)*" if s["dev"]["origin"] != ORIGIN_OURS else "")
            lines.append(f"| {label} | {dev['seeds']} | {pm(s['train'], 'macro_f1')} | **{pm(dev, 'macro_f1')}** | "
                         f"{pm(dev, 'macro_precision')} | {pm(dev, 'macro_recall')} | {pm(dev, 'micro_f1')} | "
                         f"{dev['seed_f1'] or '—'} | {pm(s['test'], 'macro_f1')} | `{dev['folder']}` |")
        # Per-dialect dev F1 only for models scored on dev.
        scored = [i for i in ids if by_id[i]["dev"]["seeds"]]
        if scored:
            lines += ["", "Per-dialect dev F1 (mean over seeds):", "",
                      "| ID | " + " | ".join(dialects) + " |", "|---" * (len(dialects) + 1) + "|"]
            lines += [f"| {i} | " + " | ".join(f"{by_id[i]['dev'][f'f1_{d}']:.1f}" for d in dialects) + " |"
                      for i in scored]
        lines.append("")

    # Every leaderboard submission, with the validation and dev scores of the exact seed submitted.
    lines += ["## Leaderboard submissions (test)", "",
              "| Test ID | Model | Submitted folder | Hub repo @ commit | Train F1 | Dev F1 | Test F1 | Test P | Test R | Test accuracy | Rank when read |",
              "|---|---|---|---|---|---|---|---|---|---|---|"]
    if LEADERBOARD.exists():
        with open(LEADERBOARD, encoding="utf-8") as f:
            subs = [json.loads(line) for line in f if line.strip()]
        for t in subs:
            log_path = RUNS_DIR / t["run"] / "train_log.json"
            log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {}
            val = next((e["val_macro"]["f1"] for e in log.get("epochs", []) if e["epoch"] == log.get("best_epoch")), None)
            dev = log.get("dev", {}).get("macro", {}).get("f1")
            lines.append(f"| {t['test_id']} | {t['run_id']} | `{t['run']}` | `{t['repo_id']}` @ `{t['commit'][:7]}` | "
                         f"{fmt(val)} | {fmt(dev)} | **{100 * t['f1']:.2f}** | {100 * t['precision']:.2f} | "
                         f"{100 * t['recall']:.2f} | {100 * t['accuracy']:.2f} | {t.get('rank_at_reading') or '—'} |")
    (OUT_DIR / "split_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
