"""Collect the scores of all sentiment runs into tables (mean ± std over seeds).

A run (SR<NN>) is one fixed setup; each model tried under it is a member SR<NN>-<model>.
configs/sentiment/runs.json maps result folders to members. This script reads
results/sentiment/runs/*/train_log.json and results/sentiment/cross_eval/*/scores.json, groups folders
that differ only in their seed (name ends in _seed<N>; tiny-subset "_limit<N>" folders are skipped), and writes:
  docs/sentiment/tables/sentiment_summary.csv  one row per model x evaluation set
  docs/sentiment/tables/sentiment_summary.md   per run: score table, per-class F1 on dev and test
  docs/sentiment/tables/cross_eval.md          scores on other corpora: mean over the BERTs, then every member

Which corpus a row belongs to (D-029):
  train_corpus       real corpus the model trained on, from the training file in its log
  generation         SG label of the synthetic set, empty for real-only runs; the same prompt style keeps
                     the same label on every corpus, so SG01 + generation_corpus names one set
  generation_corpus  corpus the set was generated for; both from run_data in the registry, because
                     the paths in old logs predate the 2026-10-16 rename
  eval_corpus        corpus of the scored split

Rows with eval_corpus = train_corpus are the model's own dev and test sets: dev chose the epoch, test was
scored once. Other rows are the same trained model scored unchanged on another corpus (SX01, D-028); they have
no best epoch or training time. Readers that want one row per model and split must keep the own-corpus rows.

Usage:
  python -m src.sentiment.summarize_runs
  python -m src.sentiment.summarize_runs --out-dir <folder>
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
import sys
from collections import defaultdict
from pathlib import Path

from src.sentiment.build_dataset import SENTIMENTS

RUNS_DIR = Path("results/sentiment/runs")
CROSS_DIR = Path("results/sentiment/cross_eval")
REGISTRY = Path("configs/sentiment/runs.json")
OUT_DIR = Path("docs/sentiment/tables")
SPLITS = ("dev", "test")
# Corpus names by the stem of the processed files and the cross-evaluation dataset keys.
CORPORA = {"arsarcasm_v2": "ArSarcasm-v2", "mawqif": "Mawqif", "eesa": "EESA"}
BERTS = {"marbertv2", "arabertv02_twitter", "marbert", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"}
REAL_ONLY_LABELS = {"SR01": "real only", "SR03": "NEG vs POS only"}


def load_logs() -> dict[str, list[dict]]:
    """Train logs of every finished run folder, grouped by folder name without "_seed<N>"."""
    groups: dict[str, list[dict]] = defaultdict(list)
    for run_dir in sorted(p for p in RUNS_DIR.iterdir() if p.is_dir()):
        # Smoke tests check that code runs; they are not results.
        if re.search(r"_limit\d+$", run_dir.name) or not (run_dir / "train_log.json").exists():
            continue
        log = json.loads((run_dir / "train_log.json").read_text(encoding="utf-8"))
        log["folder_seed"] = run_dir.name
        groups[re.sub(r"_seed\d+$", "", run_dir.name)].append(log)
    return groups


def load_cross_scores() -> dict[str, dict[str, list[dict]]]:
    """Folder without "_seed<N>" -> dataset key -> scores of every finished seed."""
    scores: dict[str, dict[str, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for path in sorted(CROSS_DIR.glob("*/scores.json")):
        record = json.loads(path.read_text(encoding="utf-8"))
        for name, s in record["datasets"].items():
            scores[re.sub(r"_seed\d+$", "", record["run"])][name].append(s)
    return scores


def corpus_of(data_path: str) -> str:
    """Corpus name of a processed file such as data/processed/sentiment/mawqif_train.jsonl."""
    return CORPORA[Path(data_path).stem.rsplit("_", 1)[0]]


def mean_std(values: list[float]) -> tuple[float, float]:
    """Mean and sample standard deviation (0 when there is a single value)."""
    return statistics.fmean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def row_labels(member: dict, folder: str, logs: list[dict], run_data: dict) -> dict:
    """The columns that say what a model is: run, corpus, generation, classifier and generator."""
    data = run_data.get(member["run"], {})
    generation = data.get("generation", "")
    classifier, generator = member["model"].rsplit("_", 1) if generation else (member["model"], "")
    return {"run": member["run"], "id": f"{member['run']}-{member['model']}",
            "train_corpus": corpus_of(logs[0]["config"]["train_data"]), "generation": generation,
            "generation_corpus": data.get("generation_corpus", ""), "classifier": classifier,
            "generator": generator, "folder": folder}


def score_row(labels: dict, eval_corpus: str, split: str, scores: list[dict]) -> dict:
    """One CSV row: one model on one evaluation set, mean and std over seeds."""
    row = {**labels, "eval_corpus": eval_corpus, "split": split, "seeds": len(scores),
           "seed_f1": " / ".join(f"{s['macro']['f1']:.2f}" for s in scores)}
    # Macro scores, accuracy and F1-PN, each as mean and std.
    metrics = {"macro_f1": lambda s: s["macro"]["f1"], "macro_precision": lambda s: s["macro"]["precision"],
               "macro_recall": lambda s: s["macro"]["recall"], "accuracy": lambda s: s["accuracy"],
               "f1_pn": lambda s: s["f1_pn"]}
    for name, get in metrics.items():
        row[name], row[f"{name}_std"] = mean_std([get(s) for s in scores])
    # Per-class F1, each as mean and std; empty for a class the run does not use.
    for c in SENTIMENTS:
        used = c in scores[0]["per_class"]
        row[f"f1_{c}"], row[f"f1_{c}_std"] = (mean_std([s["per_class"][c]["f1"] for s in scores]) if used else (None, None))
    row["best_epochs"], row["minutes_per_seed"] = "", ""
    return row


def own_rows(labels: dict, logs: list[dict]) -> list[dict]:
    """The dev and test rows of a model on the corpus it trained on."""
    rows = [score_row(labels, corpus_of(logs[0]["config"]["test_data"]), s, [log[s] for log in logs]) for s in SPLITS]
    for row in rows:
        row["best_epochs"] = " / ".join(str(log.get("best_epoch")) for log in logs)
        row["minutes_per_seed"] = statistics.fmean(log["total_seconds"] for log in logs) / 60
    return rows


def f1_cell(value: float | None) -> str:
    """A per-class F1 cell; "-" for a class the run does not use (SR03 has no NEU)."""
    return "–" if value is None else f"{value:.1f}"


def pm(row: dict, key: str) -> str:
    """A score as "mean ± std" (std left out for one seed)."""
    return f"{row[key]:.2f}" if row["seeds"] < 2 else f"{row[key]:.2f} ± {row[key + '_std']:.2f}"


def bert_means(rows: list[dict]) -> list[str]:
    """Markdown table: mean over BERTs per run x generator, with the change against SR01."""
    groups = defaultdict(list)
    for r in rows:
        if r["classifier"] in BERTS:
            groups[(r["run"], r["generator"])].append(r)
    base = {r["classifier"]: r for r in groups.get(("SR01", ""), [])}
    out = ["| Run | Set | BERTs | Macro F1 | Δ macro F1 | F1-PN | Δ F1-PN | F1 NEG | F1 NEU | F1 POS |",
           "|---|---|---|---|---|---|---|---|---|---|"]
    for (run, generator), members in sorted(groups.items()):
        def mean(metric: str, part: list[dict] = members) -> float | None:
            vals = [r[metric] for r in part if r[metric] is not None]
            return statistics.fmean(vals) if vals else None

        def delta(metric: str) -> str:
            """Change against SR01 over the same BERTs; SR03 has other classes and texts, so none."""
            same = [r for r in members if r["classifier"] in base]
            if run in REAL_ONLY_LABELS or not same:
                return ""
            return f"{mean(metric, same) - mean(metric, [base[r['classifier']] for r in same]):+.2f}"
        cells = [f"{v:.2f}" if v is not None else "" for v in map(mean, ("macro_f1", "f1_pn", "f1_NEG", "f1_NEU", "f1_POS"))]
        label = REAL_ONLY_LABELS.get(run) or f"+ {members[0]['generation']} {generator}"
        out.append(f"| {run} | {label} | {len(members)} | {cells[0]} | {delta('macro_f1')} | {cells[1]} "
                   f"| {delta('f1_pn')} | {cells[2]} | {cells[3]} | {cells[4]} |")
    return out


def write_cross_markdown(rows: list[dict], out_dir: Path) -> None:
    """Scores on other corpora, per corpus: mean over the BERTs, then every member."""
    lines = ["# Cross-dataset scores (SX01)", "",
             "Generated by `python -m src.sentiment.summarize_runs` from `results/sentiment/cross_eval/*`. Do not edit "
             "by hand. Full precision: the rows of `sentiment_summary.csv` with `eval_corpus` other than `train_corpus`. "
             "Models scored unchanged on unseen test sets. Mean over seeds. SR03 has 2 classes and is scored on the NEG "
             "and POS texts only, so it is not comparable with the other rows.", ""]
    for train, name in sorted({(r["train_corpus"], r["eval_corpus"]) for r in rows}):
        part = sorted((r for r in rows if (r["train_corpus"], r["eval_corpus"]) == (train, name)),
                      key=lambda r: (r["run"], r["classifier"], r["generator"]))
        lines += [f"## {name} (trained on {train}): mean over BERTs", ""] + bert_means(part) + ["",
                  f"## {name} (trained on {train}): every member", "",
                  "| Run | Classifier | Set | Seeds | Macro F1 | F1-PN | F1 NEG | F1 NEU | F1 POS |",
                  "|---|---|---|---|---|---|---|---|---|"]
        for r in part:
            neu = "" if r["f1_NEU"] is None else r["f1_NEU"]
            lines.append(f"| {r['run']} | {r['classifier']} | {r['generator']} | {r['seeds']} | {pm(r, 'macro_f1')} "
                         f"| {pm(r, 'f1_pn')} | {r['f1_NEG']} | {neu} | {r['f1_POS']} |")
        lines.append("")
    (out_dir / "cross_eval.md").write_text("\n".join(lines), encoding="utf-8", newline="\n")


def write_markdown(registry: dict, rows: list[dict], out_dir: Path) -> None:
    """Per run: one score table (dev and test side by side) and per-class F1 tables."""
    by_id: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        by_id[r["id"]][r["split"]] = r
    lines = ["# Sentiment scores", "",
             "Generated by `python -m src.sentiment.summarize_runs` from `results/sentiment/runs/*`. "
             "Do not edit by hand. Full precision: `sentiment_summary.csv`.", "",
             "- **Dev:** S1 dev split, 1,246 tweets carved from the official train set; it chose the epoch.",
             "- **Test:** official ArSarcasm-v2 test set, 3,000 tweets, scored once per model, never used for choices.",
             "- **Macro F1** over NEG/NEU/POS is the main score. **F1-PN** = mean F1 of POS and NEG, "
             "the WANLP 2021 shared-task metric.",
             "- Scores are mean ± std over seeds. A model with 1 seed has no spread yet: not a result on its own.", ""]
    for run in dict.fromkeys(r["run"] for r in rows):
        ids = [i for i, s in by_id.items() if s["dev"]["run"] == run]
        lines += [f"## {run}: {registry['runs'].get(run, 'not in configs/sentiment/runs.json')}", "",
                  "| ID | Seeds | Dev F1 | Dev P | Dev R | Dev acc | Dev F1-PN | Dev F1 per seed | "
                  "Test F1 | Test acc | Test F1-PN | Best epoch | Min/seed | Result folder |",
                  "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for i in ids:
            d, t = by_id[i]["dev"], by_id[i]["test"]
            lines.append(f"| {i} | {d['seeds']} | **{pm(d, 'macro_f1')}** | {pm(d, 'macro_precision')} | "
                         f"{pm(d, 'macro_recall')} | {pm(d, 'accuracy')} | {pm(d, 'f1_pn')} | {d['seed_f1']} | "
                         f"**{pm(t, 'macro_f1')}** | {pm(t, 'accuracy')} | {pm(t, 'f1_pn')} | {d['best_epochs']} | "
                         f"{d['minutes_per_seed']:.0f} | `{d['folder']}` |")
        # Per-class F1 on both splits, so class-specific failures (e.g. POS) are visible.
        lines += ["", "Per-class F1 (mean over seeds):", "",
                  "| ID | " + " | ".join(f"Dev {c}" for c in SENTIMENTS) + " | "
                  + " | ".join(f"Test {c}" for c in SENTIMENTS) + " |",
                  "|---" * (2 * len(SENTIMENTS) + 1) + "|"]
        for i in ids:
            d, t = by_id[i]["dev"], by_id[i]["test"]
            lines.append(f"| {i} | " + " | ".join(f1_cell(d[f'f1_{c}']) for c in SENTIMENTS) + " | "
                         + " | ".join(f1_cell(t[f'f1_{c}']) for c in SENTIMENTS) + " |")
        lines.append("")
    (out_dir / "sentiment_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    """Group run folders by model, average over seeds, write the CSV and markdown tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=OUT_DIR)
    args = p.parse_args()

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    groups = load_logs()
    cross = load_cross_scores()
    if not groups:
        sys.exit(f"no finished runs in {RUNS_DIR}")
    if cross.keys() - groups.keys():
        sys.exit(f"cross-evaluation scores without a training log: {sorted(cross.keys() - groups.keys())}")

    # Folders missing from the registry are kept under run "unassigned" so nothing is silently dropped.
    rows = []
    for folder, logs in groups.items():
        member = registry["members"].get(folder, {"run": "unassigned", "model": folder})
        labels = row_labels(member, folder, logs, registry["run_data"])
        rows += own_rows(labels, logs)
        rows += [score_row(labels, CORPORA[name], "test", scores) for name, scores in sorted(cross.get(folder, {}).items())]
    # Runs in ID order (unassigned last); models within a run best on dev first; own corpus before the others.
    dev_f1 = {r["id"]: r["macro_f1"] for r in rows if r["split"] == "dev"}
    rows.sort(key=lambda r: (r["run"] == "unassigned", r["run"], -dev_f1[r["id"]], r["id"],
                             r["eval_corpus"] != r["train_corpus"], r["eval_corpus"], r["split"]))
    # The CSV and cross_eval.md use 2 decimals; sentiment_summary.md rounds the full values itself.
    rounded = [{k: round(v, 2) if isinstance(v, float) else v for k, v in r.items()} for r in rows]

    args.out_dir.mkdir(parents=True, exist_ok=True)
    with open(args.out_dir / "sentiment_summary.csv", "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rounded)
    write_markdown(registry, [r for r in rows if r["eval_corpus"] == r["train_corpus"]], args.out_dir)
    write_cross_markdown([r for r in rounded if r["eval_corpus"] != r["train_corpus"]], args.out_dir)
    print(f"wrote sentiment_summary.csv ({len(rows)} rows), sentiment_summary.md and cross_eval.md to {args.out_dir}")


if __name__ == "__main__":
    sys.exit(main())
