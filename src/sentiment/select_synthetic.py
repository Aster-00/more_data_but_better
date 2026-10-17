"""Pick the final synthetic training set: `per_cell` filtered texts per (variety, sentiment) cell.

Input is the filter's <set>.filtered.jsonl (src.filtering.filter_synthetic with
configs/filtering/sentiment.json). From each cell a seeded random sample of `per_cell`
texts is kept; a cell with fewer survivors keeps all of them and the shortfall is reported,
so set sizes are never padded silently. Sampling is random (not "first N"), so later
requests are not favoured over earlier ones.

Also reported, never used to drop anything: exact matches (dedup key) between the selected
texts and the official test set. The test set is not used for filtering (CLAUDE.md); a
non-zero count is a warning to look at, not a filter.

Outputs: <set>.selected.jsonl next to the input, statistics in results/filtering/<set>.selection.json.

Usage:
  python -m src.sentiment.select_synthetic --data data/synthetic/sentiment/sg01_jais2.filtered.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import defaultdict
from pathlib import Path

from src.data.build_dataset import git_commit, sha256
from src.filtering.dedup import dedup_key

TEST = Path("data/processed/sentiment/arsarcasm_v2_test.jsonl")


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, required=True, help="<set>.filtered.jsonl")
    p.add_argument("--per-cell", type=int, default=500)
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    # Group the filtered records by cell, in file order.
    cells: dict[tuple[str, str], list[dict]] = defaultdict(list)
    with open(args.data, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            cells[(r["controls"]["variety"], r["controls"]["sentiment"])].append(r)

    # Seeded sample per cell; own RNG per cell so cells do not influence each other.
    selected, per_cell = [], {}
    for (v, s), recs in sorted(cells.items()):
        rng = random.Random(f"{args.seed}:{v}:{s}")
        chosen = recs if len(recs) <= args.per_cell else rng.sample(recs, args.per_cell)
        chosen.sort(key=lambda r: r["request_id"])
        selected += chosen
        per_cell[f"{v}/{s}"] = {"filtered": len(recs), "selected": len(chosen),
                                "shortfall": max(0, args.per_cell - len(recs))}

    # Report-only overlap with the official test set.
    with open(TEST, encoding="utf-8") as f:
        test_keys = {dedup_key(json.loads(l)["text"]) for l in f if l.strip()}
    test_hits = [r["text_id"] for r in selected if dedup_key(r["text"]) in test_keys]

    stem = args.data.name.removesuffix(".filtered.jsonl")
    out = args.data.with_name(f"{stem}.selected.jsonl")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"data": str(args.data), "data_sha256": sha256(args.data), "output": str(out),
             "output_sha256": sha256(out), "per_cell_target": args.per_cell, "seed": args.seed,
             "n_selected": len(selected), "cells": per_cell,
             "exact_matches_with_test": len(test_hits), "test_match_ids": test_hits,
             "git_commit": git_commit(), "finished": time.strftime("%Y-%m-%d %H:%M")}
    Path("results/filtering").mkdir(parents=True, exist_ok=True)
    with open(Path("results/filtering") / f"{stem}.selection.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    short = {k: v["shortfall"] for k, v in per_cell.items() if v["shortfall"]}
    print(f"selected {len(selected)} texts; shortfall {short or 'none'}; exact test matches {len(test_hits)}")


if __name__ == "__main__":
    sys.exit(main())
