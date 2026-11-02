"""Pick the final minimal-pair training set: `target_pairs` complete pairs per type (SG03, SG03-random).

Input is the filter's <set>.filtered.jsonl (src.filtering.filter_synthetic with
configs/filtering/sentiment_pairs.json). A pair is complete when both its A and B record passed
the filter; incomplete pairs are dropped, so the set stays balanced pair by pair. From each type
a seeded random sample of `target_pairs` complete pairs is kept (targets from the plan template,
prompts/sentiment/pairs_targeted_v1.json); a type with fewer keeps all of them and the shortfall
is reported, so set sizes are never padded silently.

With --min-fidelity (SG04, Ammar 2026-11-02): every text of the complete pairs is scored by the
fidelity judge of the quality measures (SR01 MARBERT ensemble, src.sentiment.measure_quality), and
within each type pairs with both sides confirmed come first, then one side, then none (seeded
random order inside each group). If the selected set's fidelity is below the minimum, a
"fidelity" entry is added to the shortfall, so the queue tops up the generation. The judge is the
same one that reports fidelity in the quality table, so that value is reached by construction.

Also reported, never used to drop anything: exact matches (dedup key) between the selected texts
and the official test set (as src.sentiment.select_synthetic).

Outputs: <set>.selected.jsonl next to the input, statistics in results/filtering/<set>.selection.json.

Usage:
  python -m src.sentiment.select_pairs --data data/synthetic/sentiment/sg03_qwen3.filtered.jsonl
  python -m src.sentiment.select_pairs --data data/synthetic/sentiment/sg04_aya.filtered.jsonl       --plan prompts/sentiment/pairs_targeted_v2.json --min-fidelity 0.8
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
    p.add_argument("--plan", type=Path, default=PLAN, help="template with the types and target_pairs")
    p.add_argument("--min-fidelity", type=float, default=None, help="prefer judge-confirmed pairs; minimum set fidelity")
    p.add_argument("--device", default="cuda")
    args = p.parse_args()
    targets = {k: t["target_pairs"] for k, t in json.loads(args.plan.read_text(encoding="utf-8"))["types"].items()}

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

    # Optional: judge-confirmed sides per pair (0, 1 or 2), for fidelity-first selection.
    confirmed: dict[str, int] = {}
    if args.min_fidelity is not None:
        from src.sentiment.measure_quality import SENTIMENTS, cell, sentiment_probs
        recs = [by_pair[pid][role] for pids in complete.values() for pid in pids for role in ("A", "B")]
        pred = sentiment_probs([r["text"] for r in recs], args.device).argmax(-1)
        for r, k in zip(recs, pred):
            confirmed[r["pair_id"]] = confirmed.get(r["pair_id"], 0) + (SENTIMENTS[k] == cell(r)[1])

    # Seeded sample per type; own RNG per type so types do not influence each other. With the judge,
    # the seeded order is kept inside each confirmed-sides group (2, then 1, then 0).
    selected, shortfall, type_fidelity = [], {}, {}
    for t, want in targets.items():
        pids = complete.get(t, [])
        if len(pids) < want:
            shortfall[t] = want - len(pids)
        if confirmed:
            order = random.Random(f"{args.seed}:{t}").sample(pids, len(pids))
            order.sort(key=lambda pid: -confirmed[pid])
            keep = set(order[:want])
        else:  # as SG03 (same draw, so earlier selections reproduce)
            keep = set(random.Random(f"{args.seed}:{t}").sample(pids, min(want, len(pids))))
        selected += [by_pair[pid][role] for pid in pids if pid in keep for role in ("A", "B")]
        if confirmed and keep:
            type_fidelity[t] = sum(confirmed[pid] for pid in keep) / (2 * len(keep))
    fidelity = (sum(confirmed[r["pair_id"]] for r in selected if r["pair_role"] == "A") / len(selected)
                if confirmed and selected else None)
    if fidelity is not None and fidelity < args.min_fidelity:
        shortfall["fidelity"] = round(fidelity, 4)

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
             "plan": str(args.plan), "min_fidelity": args.min_fidelity, "fidelity": fidelity,
             "fidelity_per_type": type_fidelity,
             "exact_matches_with_test": test_hits, "output": str(out), "git_commit": git_commit(),
             "finished": time.strftime("%Y-%m-%d %H:%M")}
    stem = args.data.name.replace(".filtered.jsonl", "")
    Path("results/filtering").mkdir(parents=True, exist_ok=True)
    with open(Path("results/filtering") / f"{stem}.selection.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: stats[k] for k in ("complete_pairs", "selected_texts", "per_sentiment", "exact_matches_with_test",
                                            "fidelity", "fidelity_per_type")},
                     ensure_ascii=False))
    print(f"{stem}: {len(selected)} texts selected, shortfall {shortfall or 'none'}")


if __name__ == "__main__":
    sys.exit(main())
