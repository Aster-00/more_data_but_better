"""Pick the final minimal-pair training set: `target_pairs` complete pairs per type (SG03, SG03-random).

Input is the filter's <set>.filtered.jsonl (src.filtering.filter_synthetic with
configs/filtering/sentiment_pairs.json). A pair is complete when both its A and B record passed
the filter; incomplete pairs are dropped, so the set stays balanced pair by pair. From each type
a seeded random sample of `target_pairs` complete pairs is kept (targets from the plan template,
prompts/sentiment/pairs_targeted_v1.json); a type with fewer keeps all of them and the shortfall
is reported, so set sizes are never padded silently.

Also reported, never used to drop anything: exact matches (dedup key) between the selected texts
and the official test set (as src.sentiment.select_synthetic).

Outputs: <set>.selected.jsonl next to the input, statistics in results/filtering/<set>.selection.json.

Usage:
  python -m src.sentiment.select_pairs --data data/synthetic/sentiment/sg03_qwen3.filtered.jsonl
"""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from src.data.build_dataset import git_commit, sha256
from src.filtering.dedup import dedup_key

TEST = Path("data/processed/sentiment/arsarcasm_v2_test.jsonl")
PLAN = Path("prompts/sentiment/pairs_targeted_v1.json")


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, required=True, help="<set>.filtered.jsonl")
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()
    targets = {k: t["target_pairs"] for k, t in json.loads(PLAN.read_text(encoding="utf-8"))["types"].items()}

    # Complete pairs per type, in file order.
    by_pair: dict[str, dict[str, dict]] = defaultdict(dict)
    with open(args.data, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            by_pair[r["pair_id"]][r["pair_role"]] = r
    complete: dict[str, list[str]] = defaultdict(list)
    for pid, roles in by_pair.items():
        if set(roles) == {"A", "B"}:
            complete[roles["A"]["pair_type"]].append(pid)

    # Seeded sample per type; own RNG per type so types do not influence each other.
    selected, shortfall = [], {}
    for t, want in targets.items():
        pids = complete.get(t, [])
        if len(pids) < want:
            shortfall[t] = want - len(pids)
        keep = set(random.Random(f"{args.seed}:{t}").sample(pids, min(want, len(pids))))
        selected += [by_pair[pid][role] for pid in pids if pid in keep for role in ("A", "B")]

    # Overlap with the official test set: reported only.
    with open(TEST, encoding="utf-8") as f:
        test_keys = {dedup_key(json.loads(l)["text"]) for l in f}
    test_hits = sum(dedup_key(r["text"]) in test_keys for r in selected)

    out = args.data.with_name(args.data.name.replace(".filtered.jsonl", ".selected.jsonl"))
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        for r in selected:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    stats = {"data": str(args.data), "data_sha256": sha256(args.data), "seed": args.seed, "targets": targets,
             "complete_pairs": {t: len(complete.get(t, [])) for t in targets},
             "incomplete_pairs": sum(1 for roles in by_pair.values() if set(roles) != {"A", "B"}),
             "selected_pairs": {t: min(targets[t], len(complete.get(t, []))) for t in targets},
             "selected_texts": len(selected), "per_sentiment": dict(Counter(r["sentiment"] for r in selected)),
             "per_variety": dict(Counter(r["dialect"] for r in selected)), "shortfall": shortfall,
             "exact_matches_with_test": test_hits, "output": str(out), "git_commit": git_commit(),
             "finished": time.strftime("%Y-%m-%d %H:%M")}
    stem = args.data.name.replace(".filtered.jsonl", "")
    Path("results/filtering").mkdir(parents=True, exist_ok=True)
    with open(Path("results/filtering") / f"{stem}.selection.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: stats[k] for k in ("complete_pairs", "selected_texts", "per_sentiment", "exact_matches_with_test")},
                     ensure_ascii=False))
    print(f"{stem}: {len(selected)} texts selected, shortfall {shortfall or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
