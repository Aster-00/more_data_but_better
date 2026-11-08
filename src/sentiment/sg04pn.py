"""SG04-PN: the POS/NEG pairs of SG04 grown to 3,600 texts per generator, for SR12-3600 (D-027, test-contaminated).

SG04-PN is the old SG04 sarcastic praise and emoji pairs plus new pairs from the same prompts
(plan prompts/sentiment/pairs_targeted_v2_posneg.json, output sg04pn_<gen>_new.jsonl).
  pool    write sg04pn_<gen>.jsonl = old pairs of the two types + the new pairs (then run the SG04 filter on it)
  select  keep 1,125 sarcastic + 675 emoji pairs with the fidelity of SR12: per type, the same shares of
          pairs with 2 / 1 / 0 judge-confirmed sides as sg04_<gen>.posneg.jsonl, seeded random inside each group.
A flat 80% rule would change fidelity between SR12 and SR12-3600; matching it leaves size as the difference.
A group that is too small is a shortfall, never filled from another group, so the queue tops up.

Outputs: sg04pn_<gen>.selected.jsonl, statistics in results/filtering/sg04pn_<gen>.selection.json.

Usage:
  python -m src.sentiment.sg04pn pool --gen aya
  python -m src.sentiment.sg04pn select --gen aya
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
from src.sentiment.measure_quality import SENTIMENTS, cell, sentiment_probs
from src.sentiment.sg04_subsets import POS_NEG_TYPES, SYN, write

PLAN = Path("prompts/sentiment/pairs_targeted_v2_posneg.json")


def read(path: Path) -> list[dict]:
    """All records of a JSONL file; none if it does not exist yet."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def confirmed_sides(records: list[dict], device: str) -> dict[str, int]:
    """Judge-confirmed sides (0, 1 or 2) per pair, with the judge of src.sentiment.select_pairs."""
    pred = sentiment_probs([r["text"] for r in records], device).argmax(-1)
    sides = {r["pair_id"]: 0 for r in records}
    for r, k in zip(records, pred):
        sides[r["pair_id"]] += int(SENTIMENTS[k] == cell(r)[1])
    return sides


def pool(gen: str) -> None:
    """Old pairs first, so the near-duplicate filter keeps them over new copies."""
    old = [r for r in read(SYN / f"sg04_{gen}.jsonl") if r["pair_type"] in POS_NEG_TYPES]
    new = read(SYN / f"sg04pn_{gen}_new.jsonl")
    n = write(old + new, SYN / f"sg04pn_{gen}.jsonl")
    print(f"sg04pn_{gen}: {n} records ({len(old)} old, {len(new)} new)")


def select(gen: str, seed: int, device: str) -> None:
    """Pick the target pairs per type with the SR12 shares of 2 / 1 / 0 confirmed sides."""
    targets = {k: t["target_pairs"] for k, t in json.loads(PLAN.read_text(encoding="utf-8"))["types"].items()}

    # Complete pairs of the filtered pool and their confirmed sides.
    src = SYN / f"sg04pn_{gen}.filtered.jsonl"
    by_pair: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in read(src):
        by_pair[r["pair_id"]][r["pair_role"]] = r
    complete = {p: v for p, v in by_pair.items() if set(v) == {"A", "B"}}
    conf = confirmed_sides([r for v in complete.values() for r in v.values()], device)

    # The SR12 composition per type, from the same judge.
    sr12 = read(SYN / f"sg04_{gen}.posneg.jsonl")
    sr12_conf = confirmed_sides(sr12, device)
    sr12_type = {r["pair_id"]: r["pair_type"] for r in sr12}

    selected, shortfall, report = [], {}, {}
    for t, want in targets.items():
        ref = Counter(c for p, c in sr12_conf.items() if sr12_type[p] == t)
        n_ref = sum(ref.values())
        need = {c: round(want * ref[c] / n_ref) for c in (2, 1)}
        need[0] = want - need[2] - need[1]
        order = sorted(p for p, v in complete.items() if v["A"]["pair_type"] == t)
        random.Random(f"{seed}:{t}").shuffle(order)
        have = {c: [p for p in order if conf[p] == c] for c in (2, 1, 0)}
        for c in (2, 1, 0):
            selected += [complete[p][role] for p in have[c][:need[c]] for role in ("A", "B")]
            if len(have[c]) < need[c]:
                shortfall[f"{t}:{c}"] = need[c] - len(have[c])
        report[t] = {"sr12_pairs_by_sides": {str(c): ref[c] for c in (2, 1, 0)}, "need": {str(c): need[c] for c in (2, 1, 0)},
                     "available": {str(c): len(have[c]) for c in (2, 1, 0)},
                     "sr12_fidelity": (2 * ref[2] + ref[1]) / (2 * n_ref),
                     "fidelity": (2 * need[2] + need[1]) / (2 * want)}

    # Write the set; the statistics say how far each group is from its target.
    out = SYN / f"sg04pn_{gen}.selected.jsonl"
    write(selected, out)
    stats = {"data": str(src), "data_sha256": sha256(src), "seed": seed, "targets": targets, "per_type": report,
             "selected_texts": len(selected), "per_sentiment": dict(Counter(r["sentiment"] for r in selected)),
             "per_variety": dict(Counter(r["dialect"] for r in selected)),
             "new_pairs_selected": sum(r["pair_id"].startswith("sg04pn_") for r in selected) // 2,
             "shortfall": shortfall, "output": str(out), "git_commit": git_commit(),
             "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(Path("results/filtering") / f"sg04pn_{gen}.selection.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps(report, ensure_ascii=False))
    print(f"sg04pn_{gen}: {len(selected)} texts selected, shortfall {shortfall or 'none'}")


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("step", choices=["pool", "select"])
    p.add_argument("--gen", required=True, choices=["fanar", "qwen3", "aya"])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--device", default="cuda")
    args = p.parse_args()
    if args.step == "pool":
        pool(args.gen)
    else:
        select(args.gen, args.seed, args.device)


if __name__ == "__main__":
    sys.exit(main())
