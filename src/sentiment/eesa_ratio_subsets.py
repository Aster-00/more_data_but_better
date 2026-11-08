"""Seeded subsets of the SG01, SG03 and SG03-random selected sets for the EESA runs SR02-EESA, SR05-EESA and SR06-EESA (D-032).

No new generation; rows are only sampled. Each subset keeps the share of synthetic data that the set had
next to S1 train (11,208 tweets) when it is added to EESA train instead:
  n_subset = n_set x n_EESA_train / n_S1_train
  SG01 (12 cells x 500)           -> an equal number per variety x sentiment cell
  SG03 / SG03-random (2,000 pairs) -> whole pairs only, each pair type keeps its share
The sets were generated for ArSarcasm-v2 (generation_corpus stays ArSarcasm-v2).

Outputs: data/synthetic/sentiment/<set>.eesa_ratio.jsonl; counts in results/filtering/eesa_ratio_subsets.json.

Usage:
  python -m src.sentiment.eesa_ratio_subsets
  python -m src.sentiment.eesa_ratio_subsets --out-dir <folder>     # write somewhere else to check
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.data.build_dataset import git_commit, sha256

SYN = Path("data/synthetic/sentiment")
S1_TRAIN = Path("data/processed/sentiment/arsarcasm_v2_train.jsonl")
EESA_TRAIN = Path("data/processed/sentiment/eesa_train.jsonl")
GENERATORS = ("aya", "fanar", "qwen3")
SETS = [f"sg01_{g}" for g in GENERATORS] + [f"sg03_{g}" for g in GENERATORS] + [f"sg03r_{g}" for g in GENERATORS]


def count_lines(path: Path) -> int:
    """Number of records in a JSONL file."""
    with open(path, encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())


def sample_cells(records: list[dict], per_cell: int, rng: random.Random) -> list[dict]:
    """SG01: the same number of texts from every variety x sentiment cell."""
    cells = defaultdict(list)
    for r in records:
        cells[(r["controls"]["variety"], r["sentiment"])].append(r)
    keep = {id(r) for key in sorted(cells) for r in rng.sample(cells[key], per_cell)}
    return [r for r in records if id(r) in keep]   # file order kept


def sample_pairs(records: list[dict], ratio: float, rng: random.Random) -> list[dict]:
    """SG03 / SG03-random: whole pairs, round(ratio x pairs) per pair type."""
    pairs = defaultdict(set)
    for r in records:
        pairs[r["pair_type"]].add(r["pair_id"])
    keep = set()
    for t in sorted(pairs):
        keep |= set(rng.sample(sorted(pairs[t]), round(len(pairs[t]) * ratio)))
    return [r for r in records if r["pair_id"] in keep]


def main() -> None:
    """Sample every set and write the subsets and their counts."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, default=SYN)
    p.add_argument("--counts-out", type=Path, default=Path("results/filtering/eesa_ratio_subsets.json"))
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()
    ratio = count_lines(EESA_TRAIN) / count_lines(S1_TRAIN)
    report = {"provenance": {"git_commit": git_commit(), "seed": args.seed, "s1_train_sha256": sha256(S1_TRAIN),
                             "eesa_train_sha256": sha256(EESA_TRAIN)}, "ratio": ratio, "sets": {}}

    args.out_dir.mkdir(parents=True, exist_ok=True)
    for name in SETS:
        src = SYN / f"{name}.selected.jsonl"
        with open(src, encoding="utf-8") as f:
            records = [json.loads(line) for line in f if line.strip()]
        # One seeded generator per set, so a set's sample does not depend on the order of the others.
        rng = random.Random(f"{args.seed}|{name}")
        if name.startswith("sg01_"):
            n_cells = len({(r["controls"]["variety"], r["sentiment"]) for r in records})
            subset = sample_cells(records, round(len(records) * ratio / n_cells), rng)
        else:
            subset = sample_pairs(records, ratio, rng)
        out = args.out_dir / f"{name}.eesa_ratio.jsonl"
        with open(out, "w", encoding="utf-8", newline="\n") as f:
            for r in subset:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        sent = Counter(r["sentiment"] for r in subset)
        report["sets"][name] = {"source": str(src), "source_sha256": sha256(src), "n_source": len(records),
                                "n": len(subset), "sentiment": dict(sorted(sent.items())),
                                "output": str(out), "output_sha256": sha256(out)}
        print(f"{name}: {len(records)} -> {len(subset)}  {dict(sorted(sent.items()))}")
    args.counts_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.counts_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"ratio {ratio:.4f}")


if __name__ == "__main__":
    sys.exit(main())
