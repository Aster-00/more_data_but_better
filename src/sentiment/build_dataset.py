"""Build the sentiment train/dev/test files from ArSarcasm-v2 in one run.

Steps:
  1. read the official ArSarcasm-v2 training and testing CSVs
  2. replace links with URL and @mentions with USER (same cleaning as the dialect data;
     each step can be switched off)
  3. train: one record per unique text; drop texts whose copies disagree on sentiment;
     drop texts that also occur in the test set
  4. split train into train/dev, stratified by sentiment x sarcasm, fixed seed
  5. write the three files and a statistics file (no tweet text in the stats)

The official test set is kept as released (all 3,000 rows, duplicates included) so scores
stay comparable with the WANLP 2021 shared task. It is for final evaluation only.
No other normalization is applied (diacritics, letter variants, emoji, Latin kept).

Outputs:
  data/processed/sentiment/arsarcasm_v2_{train,dev,test}.jsonl
  results/data_stats/sentiment/arsarcasm_v2_stats.json

Usage:
  python -m src.sentiment.build_dataset
  python -m src.sentiment.build_dataset --dev-fraction 0.1 --seed 42
  python -m src.sentiment.build_dataset --limit 300      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.data.build_dataset import CLEANING_STEPS, clean_text, git_commit, sha256, text_stats

SENTIMENTS = ["NEG", "NEU", "POS"]
RAW_FILES = {"train": "training_data.csv", "test": "testing_data.csv"}


# ---------------------------------------------------------------- reading

def read_split(path: Path, limit: int | None) -> list[dict]:
    """Read one ArSarcasm-v2 CSV; keep the fields with proper types and the row number."""
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            # Tiny-subset mode: stop after the first `limit` rows.
            if limit is not None and i >= limit:
                break
            # Fail loudly on labels outside the documented set.
            if r["sentiment"] not in SENTIMENTS or r["sarcasm"] not in ("TRUE", "FALSE"):
                raise ValueError(f"{path.name}: unexpected labels in row {i + 2}: {r}")
            rows.append({"row": i, "text_raw": r["tweet"], "sentiment": r["sentiment"],
                         "sarcasm": r["sarcasm"] == "TRUE", "dialect": r["dialect"]})
    return rows


# ---------------------------------------------------------------- records

def make_record(copies: list[dict], split: str, steps: list[str]) -> dict:
    """One output record: stable ID, cleaned and raw text, labels, and the source rows."""
    first = copies[0]
    return {
        "text_id": "s" + hashlib.sha1(first["text"].encode("utf-8")).hexdigest()[:16],
        "text": first["text"],
        "text_raw": first["text_raw"],
        "source": "real",
        "origin": "ArSarcasm-v2",
        "split": split,
        "sentiment": first["sentiment"],
        "sarcasm": first["sarcasm"],
        "dialect": first["dialect"],
        "raw_rows": [c["row"] for c in copies],
        # Fields on which the copies of a duplicated text disagree (the first copy is kept).
        "label_conflict": [k for k in ("sarcasm", "dialect") if len({c[k] for c in copies}) > 1],
        "cleaning": steps,
    }


def dedup_train(rows: list[dict], steps: list[str]) -> tuple[list[dict], dict]:
    """One record per unique training text; drop texts whose copies disagree on sentiment.

    ArSarcasm-v2: 59 training texts occur 2-3 times, 25 of them with different sentiment
    labels on the copies. Kept as they are, the same text would be trained towards two
    classes, and a copy could land in train and another in dev. Fix: group by text; drop
    groups with conflicting sentiment (with 2 copies there is no majority); otherwise keep
    one record, taking sarcasm/dialect from the first copy and listing conflicts.
    Grouping is on the cleaned text, so tweets that differ only in a link or @mention
    count as copies and cannot end up on both sides of the train/dev split.
    """
    # Group rows by their cleaned text, in file order.
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["text"]].append(r)
    # Keep groups whose copies agree on sentiment; count what was dropped.
    records, dropped_rows = [], []
    for copies in groups.values():
        if len({c["sentiment"] for c in copies}) > 1:
            dropped_rows.extend(c["row"] for c in copies)
            continue
        records.append(make_record(copies, "train", steps))
    stats = {
        "rows": len(rows),
        "unique_texts": len(groups),
        "duplicate_groups": sum(len(c) > 1 for c in groups.values()),
        "groups_sentiment_conflict_dropped": sum(len({c["sentiment"] for c in g}) > 1
                                                 for g in groups.values()),
        "rows_dropped_sentiment_conflict": len(dropped_rows),
        "dropped_raw_rows": dropped_rows,
        "kept_with_other_label_conflict": sum(bool(r["label_conflict"]) for r in records),
    }
    return records, stats


def drop_test_overlap(train: list[dict], test: list[dict]) -> tuple[list[dict], list[int]]:
    """Remove training records whose raw or cleaned text also occurs in the test set.

    ArSarcasm-v2: 2 test tweets also appear in the official training file. Wrong because
    a model would be evaluated on text it was trained on. Fix: drop them from train
    (the test set stays as released).
    """
    test_texts = {r["text_raw"] for r in test} | {r["text"] for r in test}
    kept, dropped = [], []
    for r in train:
        if r["text_raw"] in test_texts or r["text"] in test_texts:
            dropped.extend(r["raw_rows"])
        else:
            kept.append(r)
    return kept, dropped


# ---------------------------------------------------------------- splitting

def stratum(r: dict) -> str:
    """Stratification key: sentiment x sarcasm (6 groups)."""
    return f"{r['sentiment']}|{'sarc' if r['sarcasm'] else 'nosarc'}"


def stratified_split(records: list[dict], dev_fraction: float, seed: int) -> tuple[list[dict], list[dict]]:
    """Split records into train/dev, taking dev_fraction of every stratum, fixed by the seed."""
    # Group by stratum in a fixed order (sorted keys, records in file order).
    by_stratum: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_stratum[stratum(r)].append(r)
    # Shuffle each stratum with its own seeded generator and move the first share to dev.
    train, dev = [], []
    for key in sorted(by_stratum):
        group = by_stratum[key][:]
        random.Random(f"{seed}|{key}").shuffle(group)
        n_dev = round(len(group) * dev_fraction)
        dev.extend(group[:n_dev])
        train.extend(group[n_dev:])
    # Mark the split and restore file order inside each split.
    for r in dev:
        r["split"] = "dev"
    order = lambda r: r["raw_rows"][0]
    return sorted(train, key=order), sorted(dev, key=order)


# ---------------------------------------------------------------- statistics

def split_stats(records: list[dict]) -> dict:
    """Label counts and text profile of one split."""
    n = len(records)
    sent = Counter(r["sentiment"] for r in records)
    return {
        "n": n,
        "sentiment": {s: sent.get(s, 0) for s in SENTIMENTS},
        "sentiment_share": {s: round(sent.get(s, 0) / n, 4) if n else None for s in SENTIMENTS},
        "sarcasm_true": sum(r["sarcasm"] for r in records),
        "strata": dict(sorted(Counter(stratum(r) for r in records).items())),
        "dialect": dict(Counter(r["dialect"] for r in records).most_common()),
        "duplicate_texts": n - len({r["text"] for r in records}),
        "text": text_stats([r["text"] for r in records]),
    }


def print_summary(stats: dict) -> None:
    """Print the headline numbers (ASCII only, safe on the Windows console)."""
    d = stats["dedup_train"]
    print(f"Train rows {d['rows']}  unique {d['unique_texts']}  duplicate groups {d['duplicate_groups']}  "
          f"sentiment conflicts dropped {d['groups_sentiment_conflict_dropped']} groups "
          f"({d['rows_dropped_sentiment_conflict']} rows)")
    print(f"Train rows dropped for test overlap: {len(stats['test_overlap_dropped_raw_rows'])}")
    for name in ("train", "dev", "test"):
        s = stats["splits"][name]
        print(f"{name:5s} n={s['n']:5d}  {s['sentiment']}  sarcasm={s['sarcasm_true']}")


# ---------------------------------------------------------------- entry point

def parse_args() -> argparse.Namespace:
    """Command-line options: paths, cleaning switches, dev fraction, seed, tiny-subset limit."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/raw/ArSarcasm-v2/ArSarcasm-v2"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/sentiment"))
    p.add_argument("--stats-out", type=Path,
                   default=Path("results/data_stats/sentiment/arsarcasm_v2_stats.json"))
    p.add_argument("--dev-fraction", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-urls", action="store_true", help="keep links as they are")
    p.add_argument("--no-mentions", action="store_true", help="keep @mentions as they are")
    p.add_argument("--limit", type=int, default=None,
                   help="tiny-subset mode: read only the first N rows of each CSV")
    return p.parse_args()


def main() -> None:
    """Read, clean, deduplicate, split, and write the files and their statistics."""
    sys.stdout.reconfigure(encoding="utf-8")
    args = parse_args()
    steps = [s for s in CLEANING_STEPS if not getattr(args, f"no_{s}")]
    # Tiny-subset mode writes with a ".limitN" suffix so real outputs are not overwritten.
    suffix = f".limit{args.limit}" if args.limit is not None else ""
    if suffix:
        args.stats_out = args.stats_out.with_name(args.stats_out.stem + suffix + args.stats_out.suffix)

    # Read both official files and clean every row's text.
    raw = {name: read_split(args.raw_dir / fname, args.limit) for name, fname in RAW_FILES.items()}
    for rows in raw.values():
        for r in rows:
            r["text"], _ = clean_text(r["text_raw"], steps)

    # Test: every row kept as released, only cleaned.
    test = [make_record([r], "test", steps) for r in raw["test"]]
    # Train: deduplicate, remove test overlap, then carve out the stratified dev split.
    train_all, dedup = dedup_train(raw["train"], steps)
    train_all, overlap_rows = drop_test_overlap(train_all, test)
    train, dev = stratified_split(train_all, args.dev_fraction, args.seed)

    # Write the three files (UTF-8, Arabic kept readable).
    args.out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, records in (("train", train), ("dev", dev), ("test", test)):
        paths[name] = args.out_dir / f"arsarcasm_v2_{name}{suffix}.jsonl"
        with open(paths[name], "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Statistics plus provenance (code version, settings, exact input and output files).
    stats = {
        "provenance": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "args": {k: str(v) for k, v in vars(args).items()},
            "input_sha256": {name: sha256(args.raw_dir / f) for name, f in RAW_FILES.items()},
            "output_sha256": {name: sha256(p) for name, p in paths.items()},
        },
        "dedup_train": dedup,
        "test_overlap_dropped_raw_rows": overlap_rows,
        "splits": {"train": split_stats(train), "dev": split_stats(dev), "test": split_stats(test)},
        # Sanity checks: no text may appear in two splits (test duplicates are within test only).
        "cross_split_overlap": {
            f"{a}&{b}": len({r["text"] for r in x} & {r["text"] for r in y})
            for a, x, b, y in (("train", train, "dev", dev), ("train", train, "test", test),
                               ("dev", dev, "test", test))},
    }
    args.stats_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.stats_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print_summary(stats)
    print(f"Cross-split overlap (cleaned text): {stats['cross_split_overlap']}")
    print(f"Wrote {', '.join(str(p) for p in paths.values())} and {args.stats_out}")


if __name__ == "__main__":
    sys.exit(main())
