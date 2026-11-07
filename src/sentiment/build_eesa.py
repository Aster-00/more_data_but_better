"""Build the EESA test file for cross-dataset evaluation (SX01, D-028).

Only the official test split is built: EESA is used here as an unseen evaluation set, not for
training. Same cleaning as S1 and Mawqif (links -> URL, mentions -> USER). All rows are kept as
released, including mostly English comments, because the code-switching is what EESA measures.
The CSV has no header row: column 1 is the comment, column 2 its sentiment.

Outputs:
  data/processed/sentiment/eesa_test.jsonl
  results/data_stats/sentiment/eesa_stats.json

Usage:
  python -m src.sentiment.build_eesa
  python -m src.sentiment.build_eesa --limit 300      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import sys
from collections import Counter
from pathlib import Path

from src.data.build_dataset import CLEANING_STEPS, clean_text, git_commit, sha256, text_stats
from src.sentiment.build_dataset import SENTIMENTS

LABELS = {"positive": "POS", "negative": "NEG", "neutral": "NEU"}


def read_test(path: Path, limit: int | None, steps: list[str]) -> list[dict]:
    """Read the headerless EESA CSV into cleaned records."""
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if limit is not None and i >= limit:
                break
            # Fail loudly on anything outside the documented two columns and three labels.
            if len(row) != 2 or row[1] not in LABELS:
                raise ValueError(f"{path.name}: unexpected row {i + 1}: {len(row)} columns")
            text, _ = clean_text(row[0], steps)
            # The row number is part of the id, so repeated comments keep separate ids.
            records.append({"text_id": "e" + hashlib.sha1(f"{i}|{text}".encode("utf-8")).hexdigest()[:16],
                            "text": text, "text_raw": row[0], "source": "real", "origin": "EESA",
                            "split": "test", "sentiment": LABELS[row[1]], "dialect": "egypt",
                            "raw_rows": [i + 1], "cleaning": steps})
    return records


def main() -> None:
    """Read, clean and write the test file and its statistics."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw", type=Path, default=Path("data/datasets/sa/EESA-Corpus-main/EESA-Test.csv"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/sentiment"))
    p.add_argument("--stats-out", type=Path, default=Path("results/data_stats/sentiment/eesa_stats.json"))
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N rows")
    args = p.parse_args()
    suffix = f".limit{args.limit}" if args.limit is not None else ""
    records = read_test(args.raw, args.limit, list(CLEANING_STEPS))

    # Test file, one JSON line per comment.
    args.out_dir.mkdir(parents=True, exist_ok=True)
    out = args.out_dir / f"eesa_test{suffix}.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Statistics without comment text.
    sent = Counter(r["sentiment"] for r in records)
    stats = {"provenance": {"git_commit": git_commit(), "python": platform.python_version(),
                            "args": {k: str(v) for k, v in vars(args).items()},
                            "input_sha256": sha256(args.raw), "output_sha256": sha256(out)},
             "n": len(records), "sentiment": {s: sent.get(s, 0) for s in SENTIMENTS},
             "duplicate_texts": len(records) - len({r["text"] for r in records}),
             "text": text_stats([r["text"] for r in records])}
    stats_out = args.stats_out.with_name(args.stats_out.stem + suffix + args.stats_out.suffix)
    stats_out.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"test n={stats['n']}  {stats['sentiment']}  duplicates {stats['duplicate_texts']}")


if __name__ == "__main__":
    sys.exit(main())
