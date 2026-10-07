"""Turn G01 feasibility samples into synthetic records that src/quality/measure.py can score (Q02).

For each results/runs/<G01 member>/samples.jsonl: clean every raw output with the generation
pipeline's own parser (src/generation/prompts.parse_output, one sentence, Arabic script) and
write data/synthetic/g01_<model>.jsonl. Outputs the parser rejects are dropped and counted.
Also writes a size-matched real reference: per G01 dialect, as many single-label D1 tweets as
each generator was asked for (seeded random), to data/processed/d1_g01match_seed<seed>.jsonl.
Lexical and embedding diversity depend on set size, so generators are compared with this
matched set, not with the 2000-text Q01 sample.

Usage:
  python scripts/g01_to_records.py
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.generation.prompts import parse_output  # noqa: E402

RUNS = Path("results/runs")


def g01_members() -> dict[str, str]:
    """Result folder -> model tag for every G01 member in configs/runs.json."""
    with open("configs/runs.json", encoding="utf-8") as f:
        members = json.load(f)["members"]
    return {folder: m["model"] for folder, m in members.items() if m["run"] == "G01"}


def convert(folder: str, tag: str, out_dir: Path) -> dict:
    """Clean one generator's samples into records; return counts."""
    with open(RUNS / folder / "samples.jsonl", encoding="utf-8") as f:
        samples = [json.loads(l) for l in f if l.strip()]
    with open(RUNS / folder / "feasibility.json", encoding="utf-8") as f:
        feas = json.load(f)
    records, dropped = [], 0
    for s in samples:
        kept = parse_output(s["raw_output"], 1, "arabic")
        if not kept:
            dropped += 1
            continue
        records.append({
            "text_id": f"g01_{tag}_{s['index']:03d}", "text": kept[0], "source": "synthetic",
            "condition": "open", "target_dialect": s["dialect"], "generator": feas["model"],
            "run": "G01", "result_folder": folder, "raw_output": s["raw_output"], "prompt": s.get("prompt"),
            "sampling": feas.get("sampling"), "seed": feas.get("seed"),
        })
    out = out_dir / f"g01_{tag}.jsonl"
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in records)
    return {"tag": tag, "n_samples": len(samples), "kept": len(records), "dropped_by_parser": dropped,
            "per_dialect": dict(Counter(s["dialect"] for s in samples)), "file": str(out)}


def matched_real(per_dialect: dict[str, int], d1: Path, out: Path, seed: int) -> int:
    """Seeded sample of single-label D1 tweets with the same per-dialect counts as G01."""
    with open(d1, encoding="utf-8") as f:
        records = [json.loads(l) for l in f if l.strip()]
    rng = random.Random(seed)
    chosen = []
    for dialect, n in sorted(per_dialect.items()):
        pool = [r for r in records if [d for d, v in r["labels"].items() if v == 1] == [dialect]]
        chosen += rng.sample(pool, n)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps({**r, "source": "real"}, ensure_ascii=False) + "\n" for r in chosen)
    return len(chosen)


def main() -> None:
    """Convert every G01 member and write the matched real reference."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--d1", type=Path, default=Path("data/processed/nadi_lahjatbert.jsonl"))
    p.add_argument("--seed", type=int, default=42)
    args = p.parse_args()

    out_dir = Path("data/synthetic")
    out_dir.mkdir(parents=True, exist_ok=True)
    summaries = [convert(folder, tag, out_dir) for folder, tag in g01_members().items()]
    for s in summaries:
        print(f"{s['tag']:10s} kept {s['kept']}/{s['n_samples']}  dropped by parser {s['dropped_by_parser']}")

    # All G01 members used the same request plan, so any member's per-dialect counts will do.
    real_out = Path("data/processed") / f"d1_g01match_seed{args.seed}.jsonl"
    n = matched_real(summaries[0]["per_dialect"], args.d1, real_out, args.seed)
    print(f"matched real reference: {n} texts -> {real_out}")
    with open(out_dir / "g01_conversion.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump({"summaries": summaries, "matched_real": str(real_out), "seed": args.seed}, f, indent=2)


if __name__ == "__main__":
    main()
