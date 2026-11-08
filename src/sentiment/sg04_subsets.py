"""Filtered copies of the SG04 selected sets for the repair tests SR08-SR13 (D-025, D-026; D-029 merged the scripts).

No new generation; the texts are unchanged, rows are only dropped, so the sets get smaller:
  sg04_<gen>.noprayer.jsonl   without the prayer pairs (SR08, SR11)
  sg04_qwen3.nosame.jsonl     without pairs whose two sides have the same words, only punctuation or
                              emoji differ (SR09; Fanar and Aya have no such pairs)
  sg04_<gen>.posneg.jsonl     whole POS/NEG pairs only: sarcastic praise, emoji in context; 1,600 texts (SR12)
  sg04_<gen>.negsides.jsonl   the posneg texts + the NEG sides of public jab and personal remark; 2,600 texts (SR13)
SR13 - SR12 is therefore the effect of those 1,000 NEG sides. SR10 trains on the selected set itself.

Counts go to results/filtering/sg04_subsets.json. The files in data/ were built by the two scripts this one
replaced; their counts stay in results/filtering/sg04_variants.json and sg04_no_neu.json. Rerunning rewrites
the data files, so use --out-dir to check the output somewhere else first.

Usage:
  python -m src.sentiment.sg04_subsets
  python -m src.sentiment.sg04_subsets --out-dir <folder>
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.data.build_dataset import git_commit, sha256
from src.sentiment.sg04_adherence import words

SYN = Path("data/synthetic/sentiment")
GENERATORS = ("fanar", "qwen3", "aya")
POS_NEG_TYPES = {"sarcastic_praise", "emoji_context"}
NEU_PAIR_TYPES = {"public_jab", "personal_remark"}


def write(records: list[dict], path: Path) -> int:
    """Write records as JSONL; return their number."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(records)


def same_word_pairs(records: list[dict]) -> set[str]:
    """Pair IDs whose two sides have the same words."""
    pairs: dict[str, dict[str, str]] = defaultdict(dict)
    for r in records:
        pairs[r["pair_id"]][r["pair_role"]] = r["text"]
    return {pid for pid, sides in pairs.items() if words(sides["A"]) == words(sides["B"])}


def subsets(records: list[dict], gen: str) -> dict[str, list[dict]]:
    """The subsets of one generator, by file suffix."""
    posneg = [r for r in records if r["pair_type"] in POS_NEG_TYPES]
    negsides = posneg + [r for r in records if r["pair_type"] in NEU_PAIR_TYPES and r["sentiment"] == "NEG"]
    if any(r["sentiment"] == "NEU" for r in negsides):
        raise ValueError(f"NEU text in the POS/NEG subsets of {gen}")

    sets = {"noprayer": [r for r in records if r["pair_type"] != "prayer"], "posneg": posneg, "negsides": negsides}
    if gen == "qwen3":
        same = same_word_pairs(records)
        sets["nosame"] = [r for r in records if r["pair_id"] not in same]
    return sets


def main() -> None:
    """Write the subsets of every generator and their counts."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out-dir", type=Path, help="write here instead of the data and results folders")
    args = p.parse_args()
    out_dir = args.out_dir or SYN
    stats_path = (args.out_dir or Path("results/filtering")) / "sg04_subsets.json"

    stats = {"git_commit": git_commit(), "sets": {}}
    for g in GENERATORS:
        src = SYN / f"sg04_{g}.selected.jsonl"
        with open(src, encoding="utf-8") as f:
            recs = [json.loads(l) for l in f]
        for name, subset in subsets(recs, g).items():
            out = out_dir / f"sg04_{g}.{name}.jsonl"
            stats["sets"][out.name] = {"source_sha256": sha256(src), "texts": write(subset, out),
                                       "pairs_dropped": len({r["pair_id"] for r in recs} - {r["pair_id"] for r in subset}),
                                       "per_sentiment": dict(Counter(r["sentiment"] for r in subset)),
                                       "per_type": dict(Counter(r["pair_type"] for r in subset))}
    stats_path.write_text(json.dumps(stats, indent=2), encoding="utf-8", newline="\n")
    print(json.dumps(stats["sets"], indent=2))


if __name__ == "__main__":
    sys.exit(main())
