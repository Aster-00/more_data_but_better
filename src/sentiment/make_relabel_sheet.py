"""Build the blind relabelling sheet for the S1 dev agreement study (SD-008).

Two parts, labelled once and shuffled together:
  A  random: `n_random` dev tweets, stratified by gold sentiment (dataset-wide agreement estimate)
  B  errors: every dev NEG tweet that at least one SR03 run predicted POS (are model errors label errors?)

The sheet shows only an item number and the text, so the annotator sees no gold label,
no part and no model prediction. Everything else goes to a separate key file.

Outputs (data/annotation/sentiment/, gitignored):
  relabel_dev_v1.csv        item, text, label (to fill: NEG / NEU / POS), note; UTF-8 with BOM so Excel shows Arabic
  relabel_dev_v1.key.jsonl  item -> text_id, gold labels, part(s), how many SR03 runs called it POS
  relabel_dev_v1.meta.json  settings, counts, data hash, git commit

Usage:
  python -m src.sentiment.make_relabel_sheet
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.data.build_dataset import git_commit, sha256

DEV = Path("data/processed/sentiment/arsarcasm_v2_dev.jsonl")
RUNS = Path("results/sentiment/runs")
OUT = Path("data/annotation/sentiment")


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n-random", type=int, default=150)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--name", default="relabel_dev_v1")
    args = p.parse_args()
    rng = random.Random(args.seed)

    # Dev tweets, in file order.
    with open(DEV, encoding="utf-8") as f:
        dev = [json.loads(line) for line in f]
    by_id = {r["text_id"]: r for r in dev}

    # Part B: count, per dev NEG tweet, the finished SR03 runs (no smoke tests) that predicted POS.
    run_dirs = sorted(d for d in RUNS.glob("sr03_*_seed*") if "limit" not in d.name and (d / "train_log.json").exists())
    pos_votes: Counter = Counter()
    for d in run_dirs:
        with open(d / "dev_predictions.jsonl", encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                if r["gold"] == "NEG" and r["pred"] == "POS":
                    pos_votes[r["text_id"]] += 1
    part_b = set(pos_votes)

    # Part A: stratified random sample, class shares as in dev (rounded; the last class takes the remainder).
    by_class = defaultdict(list)
    for r in dev:
        by_class[r["sentiment"]].append(r["text_id"])
    classes = sorted(by_class)
    part_a: set[str] = set()
    remaining = args.n_random
    for i, c in enumerate(classes):
        k = remaining if i == len(classes) - 1 else round(args.n_random * len(by_class[c]) / len(dev))
        part_a.update(rng.sample(sorted(by_class[c]), k))
        remaining -= k

    # One item per tweet, shuffled so neither the part nor the class can be guessed from the order.
    items = sorted(part_a | part_b)
    rng.shuffle(items)

    OUT.mkdir(parents=True, exist_ok=True)
    # Sheet: text only. utf-8-sig so Excel opens the Arabic correctly.
    with open(OUT / f"{args.name}.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["item", "text", "label", "note"])
        for n, tid in enumerate(items, 1):
            w.writerow([n, by_id[tid]["text"], "", ""])
    # Key: everything the annotator must not see.
    with open(OUT / f"{args.name}.key.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for n, tid in enumerate(items, 1):
            r = by_id[tid]
            f.write(json.dumps({"item": n, "text_id": tid, "gold": r["sentiment"], "sarcasm": r["sarcasm"],
                                "dialect": r["dialect"], "part_a": tid in part_a, "part_b": tid in part_b,
                                "sr03_runs_pos": pos_votes.get(tid, 0), "sr03_runs": len(run_dirs)},
                               ensure_ascii=False) + "\n")
    meta = {"name": args.name, "seed": args.seed, "n_random": args.n_random, "n_items": len(items),
            "part_a": len(part_a), "part_b": len(part_b), "overlap": len(part_a & part_b),
            "part_a_gold": dict(Counter(by_id[t]["sentiment"] for t in part_a)),
            "sr03_runs": [d.name for d in run_dirs], "dev_sha256": sha256(DEV), "git_commit": git_commit()}
    (OUT / f"{args.name}.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in meta.items() if k != "sr03_runs"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
