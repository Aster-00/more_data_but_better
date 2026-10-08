"""Drop texts with zero valid dialects or all 18 valid dialects from a training JSONL.

A zero-label text says no dialect is valid and an all-18 text says every dialect is valid;
neither tells the classifier anything about which dialect a sentence belongs to. D1 keeps
both (decisions.md D-006); this script writes the filtered version used as an ablation.

Outputs:
  data/processed/nadi_lahjatbert_card1to17.jsonl          records with 1 to 17 valid dialects
  results/data_stats/nadi_lahjatbert_card1to17_stats.json counts, input/output hashes

Usage:
  python -m src.data.filter_cardinality
  python -m src.data.filter_cardinality --limit 500      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from src.data.build_dataset import DIALECTS, git_commit, sha256


def filter_records(in_path: Path, out_path: Path, min_card: int, max_card: int,
                   limit: int | None) -> dict:
    """Copy records whose number of valid dialects is in [min_card, max_card]; return counts."""
    kept, dropped = 0, Counter()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(in_path, encoding="utf-8") as fin, open(out_path, "w", encoding="utf-8") as fout:
        for i, line in enumerate(fin):
            if limit is not None and i >= limit:
                break
            r = json.loads(line)
            # Recount from the labels rather than trusting the stored cardinality field.
            card = sum(r["labels"][d] for d in DIALECTS)
            if min_card <= card <= max_card:
                fout.write(line)
                kept += 1
            else:
                dropped[card] += 1
    return {"n_in": kept + sum(dropped.values()), "n_kept": kept,
            "n_dropped_by_cardinality": {str(k): v for k, v in sorted(dropped.items())}}


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("data/processed/nadi_lahjatbert.jsonl"))
    p.add_argument("--out", type=Path, default=Path("data/processed/nadi_lahjatbert_card1to17.jsonl"))
    p.add_argument("--stats-out", type=Path,
                   default=Path("results/data_stats/nadi_lahjatbert_card1to17_stats.json"))
    p.add_argument("--min-card", type=int, default=1)
    p.add_argument("--max-card", type=int, default=len(DIALECTS) - 1)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N records")
    args = p.parse_args()

    # Tiny-subset mode writes to separate ".limitN" files so real outputs are not overwritten.
    if args.limit is not None:
        args.out = args.out.with_name(args.out.stem + f".limit{args.limit}" + args.out.suffix)
        args.stats_out = args.stats_out.with_name(
            args.stats_out.stem + f".limit{args.limit}" + args.stats_out.suffix)

    stats = filter_records(args.data, args.out, args.min_card, args.max_card, args.limit)
    stats.update(input=str(args.data), input_sha256=sha256(args.data), output=str(args.out),
                 output_sha256=sha256(args.out), min_card=args.min_card, max_card=args.max_card,
                 limit=args.limit, git_commit=git_commit())
    args.stats_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.stats_out, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
