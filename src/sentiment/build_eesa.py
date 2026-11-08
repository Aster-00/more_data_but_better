"""Build the EESA train, dev and test files (E1: test for SX01, D-028; E2: train and dev for the SRxx-EESA runs, D-032).

Same cleaning as S1 and Mawqif (links -> URL, mentions -> USER). All rows are kept as released,
including mostly English comments, because the code-switching is what EESA measures.
The CSVs have no header row: column 1 is the comment, column 2 its sentiment.

Splits are the official ones. A train text that also occurs in dev or test (after cleaning) is dropped
from train, so no text is in two splits; repeats within one split are kept. The test file is unchanged
from E1 (same rows, ids and bytes).

Outputs:
  data/processed/sentiment/eesa_{train,dev,test}.jsonl
  results/data_stats/sentiment/eesa_stats_e2.json   (E1 statistics stay in eesa_stats.json)

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
RAW = Path("data/datasets/sa/EESA-Corpus-main")
SPLITS = {"train": "EESA-Train.csv", "dev": "EESA-Dev.csv", "test": "EESA-Test.csv"}


def read_split(path: Path, split: str, limit: int | None, steps: list[str]) -> list[dict]:
    """Read one headerless EESA CSV into cleaned records."""
    records = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for i, row in enumerate(csv.reader(f)):
            if limit is not None and i >= limit:
                break
            # Fail loudly on anything outside the documented two columns and three labels.
            if len(row) != 2 or row[1] not in LABELS:
                raise ValueError(f"{path.name}: unexpected row {i + 1}: {len(row)} columns")
            text, _ = clean_text(row[0], steps)
            # The row number is part of the id, so repeated comments keep separate ids. Test ids keep the
            # E1 form; train and dev ids also hash the split, so equal row numbers in two splits cannot clash.
            key = f"{i}|{text}" if split == "test" else f"{split}|{i}|{text}"
            records.append({"text_id": "e" + hashlib.sha1(key.encode("utf-8")).hexdigest()[:16],
                            "text": text, "text_raw": row[0], "source": "real", "origin": "EESA",
                            "split": split, "sentiment": LABELS[row[1]], "dialect": "egypt",
                            "raw_rows": [i + 1], "cleaning": steps})
    return records


def main() -> None:
    """Read, clean and write the three splits and their statistics."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=RAW)
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/sentiment"))
    p.add_argument("--stats-out", type=Path, default=Path("results/data_stats/sentiment/eesa_stats_e2.json"))
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N rows per split")
    args = p.parse_args()
    suffix = f".limit{args.limit}" if args.limit is not None else ""
    steps = list(CLEANING_STEPS)
    data = {s: read_split(args.raw_dir / f, s, args.limit, steps) for s, f in SPLITS.items()}

    # No text in two splits: drop train texts that are also in dev or test.
    held_out = {r["text"] for s in ("dev", "test") for r in data[s]}
    n_raw_train = len(data["train"])
    data["train"] = [r for r in data["train"] if r["text"] not in held_out]

    # One JSON line per comment, per split.
    args.out_dir.mkdir(parents=True, exist_ok=True)
    stats = {"provenance": {"git_commit": git_commit(), "python": platform.python_version(),
                            "args": {k: str(v) for k, v in vars(args).items()}},
             "train_dropped_in_dev_or_test": n_raw_train - len(data["train"]), "splits": {}}
    for split, records in data.items():
        out = args.out_dir / f"eesa_{split}{suffix}.jsonl"
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        # Statistics without comment text.
        sent = Counter(r["sentiment"] for r in records)
        stats["splits"][split] = {"input_sha256": sha256(args.raw_dir / SPLITS[split]), "output_sha256": sha256(out),
                                  "n": len(records), "sentiment": {s: sent.get(s, 0) for s in SENTIMENTS},
                                  "duplicate_texts": len(records) - len({r["text"] for r in records}),
                                  "text": text_stats([r["text"] for r in records])}
        print(f"{split} n={len(records)}  {stats['splits'][split]['sentiment']}  "
              f"duplicates {stats['splits'][split]['duplicate_texts']}")
    print(f"train rows dropped (also in dev or test): {stats['train_dropped_in_dev_or_test']}")
    stats_out = args.stats_out.with_name(args.stats_out.stem + suffix + args.stats_out.suffix)
    stats_out.parent.mkdir(parents=True, exist_ok=True)
    with open(stats_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
