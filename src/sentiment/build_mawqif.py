"""Build the sentiment train/dev/test files from Mawqif (second sentiment dataset, D-022).

Same recipe as src/sentiment/build_dataset.py (ArSarcasm-v2):
  1. read the official Mawqif train and test CSVs (Mawqif_AllTargets_{Train,Test}.csv)
  2. replace links with URL and @mentions with USER
  3. train: one record per unique text; drop texts whose copies disagree on sentiment;
     drop texts that also occur in the test set
  4. split train into train/dev, stratified by sentiment x target (3 x 3), fixed seed
  5. write the three files and a statistics file (no tweet text in the stats)
Labels: sentiment Positive / Negative / Neutral -> POS / NEG / NEU. Stance, target, sarcasm and the
annotation confidences are kept as fields. Mawqif has no dialect label: `dialect` is None.
The official test set is kept as released (619 rows). It is for final evaluation only.

Outputs:
  data/processed/sentiment/mawqif_{train,dev,test}.jsonl
  results/data_stats/sentiment/mawqif_stats.json

Usage:
  python -m src.sentiment.build_mawqif
  python -m src.sentiment.build_mawqif --limit 300      # tiny-subset smoke test
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
from src.sentiment.build_dataset import SENTIMENTS, drop_test_overlap

RAW_FILES = {"train": "Mawqif_AllTargets_Train.csv", "test": "Mawqif_AllTargets_Test.csv"}
LABELS = {"Positive": "POS", "Negative": "NEG", "Neutral": "NEU"}


def read_split(path: Path, limit: int | None) -> list[dict]:
    """Read one Mawqif CSV; keep the fields with proper types and the row number."""
    rows = []
    with open(path, encoding="utf-8-sig", newline="") as f:
        for i, r in enumerate(csv.DictReader(f)):
            if limit is not None and i >= limit:
                break
            # Fail loudly on labels outside the documented set.
            if r["sentiment"] not in LABELS or r["sarcasm"] not in ("Yes", "No"):
                raise ValueError(f"{path.name}: unexpected labels in row {i + 2}")
            rows.append({"row": i, "text_raw": r["text"], "sentiment": LABELS[r["sentiment"]],
                         "sarcasm": r["sarcasm"] == "Yes", "target": r["target"], "stance": r["stance"],
                         "sentiment_confidence": float(r["sentiment:confidence"] or "nan"),
                         "stance_confidence": float(r["stance:confidence"] or "nan"), "date": r.get("Date")})
    return rows


def make_record(copies: list[dict], split: str, steps: list[str]) -> dict:
    """One output record: stable ID, cleaned and raw text, labels, and the source rows."""
    first = copies[0]
    return {
        "text_id": "m" + hashlib.sha1(first["text"].encode("utf-8")).hexdigest()[:16],
        "text": first["text"], "text_raw": first["text_raw"], "source": "real", "origin": "Mawqif", "split": split,
        "sentiment": first["sentiment"], "sarcasm": first["sarcasm"], "dialect": None,
        "target": first["target"], "stance": first["stance"],
        "sentiment_confidence": first["sentiment_confidence"], "stance_confidence": first["stance_confidence"],
        "date": first["date"], "raw_rows": [c["row"] for c in copies],
        "label_conflict": [k for k in ("sarcasm", "target", "stance") if len({c[k] for c in copies}) > 1],
        "cleaning": steps,
    }


def dedup_train(rows: list[dict], steps: list[str]) -> tuple[list[dict], dict]:
    """One record per unique (cleaned) training text; drop texts whose copies disagree on sentiment.

    Mawqif train has 7 repeated texts. As in ArSarcasm-v2 (build_dataset.dedup_train): a text
    trained towards two classes, or copies on both sides of train/dev, would be wrong.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        groups[r["text"]].append(r)
    records, dropped = [], []
    for copies in groups.values():
        if len({c["sentiment"] for c in copies}) > 1:
            dropped += [c["row"] for c in copies]
            continue
        records.append(make_record(copies, "train", steps))
    return records, {"rows": len(rows), "unique_texts": len(groups),
                     "duplicate_groups": sum(len(c) > 1 for c in groups.values()),
                     "rows_dropped_sentiment_conflict": len(dropped), "dropped_raw_rows": dropped}


def stratified_split(records: list[dict], dev_fraction: float, seed: int) -> tuple[list[dict], list[dict]]:
    """Train/dev split taking dev_fraction of every sentiment x target stratum, fixed by the seed."""
    by_stratum: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_stratum[f"{r['sentiment']}|{r['target']}"].append(r)
    train, dev = [], []
    for key in sorted(by_stratum):
        group = by_stratum[key][:]
        random.Random(f"{seed}|{key}").shuffle(group)
        n_dev = round(len(group) * dev_fraction)
        dev += group[:n_dev]
        train += group[n_dev:]
    for r in dev:
        r["split"] = "dev"
    order = lambda r: r["raw_rows"][0]
    return sorted(train, key=order), sorted(dev, key=order)


def split_stats(records: list[dict]) -> dict:
    """Label counts and text profile of one split."""
    n, sent = len(records), Counter(r["sentiment"] for r in records)
    return {"n": n, "sentiment": {s: sent.get(s, 0) for s in SENTIMENTS},
            "sentiment_share": {s: round(sent.get(s, 0) / n, 4) if n else None for s in SENTIMENTS},
            "target": dict(Counter(r["target"] for r in records).most_common()),
            "sarcasm_true": sum(r["sarcasm"] for r in records),
            "sentiment_confidence_below_0.6": sum(r["sentiment_confidence"] < 0.6 for r in records),
            "duplicate_texts": n - len({r["text"] for r in records}), "text": text_stats([r["text"] for r in records])}


def main() -> None:
    """Read, clean, deduplicate, split, and write the files and their statistics."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--raw-dir", type=Path, default=Path("data/datasets/sa/Mawqif-Arabic-Stance-main/Data"))
    p.add_argument("--out-dir", type=Path, default=Path("data/processed/sentiment"))
    p.add_argument("--stats-out", type=Path, default=Path("results/data_stats/sentiment/mawqif_stats.json"))
    p.add_argument("--dev-fraction", type=float, default=0.15)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N rows of each CSV")
    args = p.parse_args()
    steps = list(CLEANING_STEPS)
    suffix = f".limit{args.limit}" if args.limit is not None else ""

    # Read both official files and clean every row's text.
    raw = {name: read_split(args.raw_dir / f, args.limit) for name, f in RAW_FILES.items()}
    for rows in raw.values():
        for r in rows:
            r["text"], _ = clean_text(r["text_raw"], steps)
    test = [make_record([r], "test", steps) for r in raw["test"]]
    train_all, dedup = dedup_train(raw["train"], steps)
    train_all, overlap_rows = drop_test_overlap(train_all, test)
    train, dev = stratified_split(train_all, args.dev_fraction, args.seed)

    args.out_dir.mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, records in (("train", train), ("dev", dev), ("test", test)):
        paths[name] = args.out_dir / f"mawqif_{name}{suffix}.jsonl"
        with open(paths[name], "w", encoding="utf-8", newline="\n") as f:
            for r in records:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"provenance": {"git_commit": git_commit(), "python": platform.python_version(),
                            "args": {k: str(v) for k, v in vars(args).items()},
                            "input_sha256": {n: sha256(args.raw_dir / f) for n, f in RAW_FILES.items()},
                            "output_sha256": {n: sha256(p) for n, p in paths.items()}},
             "dedup_train": dedup, "test_overlap_dropped_raw_rows": overlap_rows,
             "splits": {n: split_stats(r) for n, r in (("train", train), ("dev", dev), ("test", test))},
             "cross_split_overlap": {f"{a}&{b}": len({r["text"] for r in x} & {r["text"] for r in y})
                                     for a, x, b, y in (("train", train, "dev", dev), ("train", train, "test", test),
                                                        ("dev", dev, "test", test))}}
    args.stats_out.with_name(args.stats_out.stem + suffix + args.stats_out.suffix).parent.mkdir(parents=True, exist_ok=True)
    with open(args.stats_out.with_name(args.stats_out.stem + suffix + args.stats_out.suffix), "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"train rows {dedup['rows']}, unique {dedup['unique_texts']}, dropped (sentiment conflict) "
          f"{dedup['rows_dropped_sentiment_conflict']}, dropped (test overlap) {len(overlap_rows)}")
    for n in ("train", "dev", "test"):
        s = stats["splits"][n]
        print(f"{n:5s} n={s['n']:5d}  {s['sentiment']}  targets {s['target']}")
    print(f"cross-split overlap: {stats['cross_split_overlap']}")


if __name__ == "__main__":
    sys.exit(main())
