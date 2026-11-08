"""MLP-neuron statistics of a generator on real S1 train tweets (SV01 neurons, GPU step).

Same reading as SV01 (`extract.py`): each tweet sits in the assistant turn after a fixed neutral
user turn; one forward pass, no sampling. Same neuron statistics as SV02 (`activations_generated`):
firing share (act_fn(gate) > 0, the LAPE rule), mean and mean square of the down_proj input, each
averaged over the tweet's tokens. Only S1 train is read; dev and test never.

Neuron values are too large to keep per tweet, so they are summed per group. The groups are chosen
so that the CPU step can test neurons fairly:
  real      sentiment | sarcasm | dialect | has link | fold    (fold = held-out test of neuron lists)
  shuffled  shuf | sentiment shuffled inside the dialect | dialect | fold, non-sarcastic tweets only
            (what selecting neurons looks like when the label carries no information)

Outputs in output_dir: neuron_sums.pt (sums, counts, fold per text_id), meta.json.
With --per-text (needed for AP neurons, Kojima 2024) the folder ends in _pertext and also holds
per_text_mean.npy (fp16 [N, L * I], each tweet's mean down_proj input per neuron; about 10-13 GB
per generator) and rows.json (text_id, sentiment, sarcasm, dialect of each row, same order).

Usage:
  python -m src.sentiment.steering.activations_real --config configs/sentiment/steering/sv01_fanar.json --limit 48 --check-hooks
  python -m src.sentiment.steering.activations_real --config configs/sentiment/steering/sv01_fanar.json
  python -m src.sentiment.steering.activations_real --config configs/sentiment/steering/sv01_fanar.json --per-text
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from pathlib import Path

import torch

from src.data.build_dataset import git_commit
from src.sentiment.steering.activations_generated import collect
from src.sentiment.steering.extract import check_hooks, encode, load_train

FOLDS = 5
BATCH_SIZE = 4                  # the same for every generator; neuron hooks need more memory than SV01


def assign_groups(rows: list[dict], seed: int) -> None:
    """Give every row a fold and, if non-sarcastic, a sentiment shuffled inside its dialect."""
    order = sorted(range(len(rows)), key=lambda i: rows[i]["text_id"])
    random.Random(seed).shuffle(order)
    for n, i in enumerate(order):
        rows[i]["_fold"] = n % FOLDS
    for d in sorted({r["dialect"] for r in rows}):
        idx = sorted((i for i, r in enumerate(rows) if r["dialect"] == d and not r["sarcasm"]),
                     key=lambda i: rows[i]["text_id"])
        labels = [rows[i]["sentiment"] for i in idx]
        random.Random(f"{seed}:{d}").shuffle(labels)
        for i, s in zip(idx, labels):
            rows[i]["_shuffled"] = s


def keys_of(r: dict) -> list[str]:
    """The groups one tweet is summed into."""
    link = int("URL" in r["text"])
    keys = [f"{r['sentiment']}|{int(bool(r['sarcasm']))}|{r['dialect']}|{link}|{r['_fold']}"]
    if "_shuffled" in r:
        keys.append(f"shuf|{r['_shuffled']}|{r['dialect']}|{r['_fold']}")
    return keys


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: a seeded random N train tweets")
    p.add_argument("--check-hooks", action="store_true", help="verify hook output == hidden_states[k+1]")
    p.add_argument("--per-text", action="store_true", help="also save every tweet's neuron means (for AP)")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    cfg["batch_size"] = BATCH_SIZE
    out_dir = Path(cfg["output_dir"]).with_name(Path(cfg["output_dir"]).name + "_neurons" + ("_pertext" if args.per_text else ""))
    # Tiny runs write to their own folder so they never mix with the real statistics.
    if args.limit is not None:
        out_dir = out_dir.with_name(out_dir.name + f"_limit{args.limit}")
    if (out_dir / "meta.json").exists():
        raise SystemExit(f"{out_dir} already has a finished run; use a new output_dir")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_train(cfg, args.limit)
    assign_groups(rows, cfg["seed"])
    print(f"{len(rows)} train tweets", flush=True)

    # Load the generator only now (slow, needs the GPU).
    from src.generation.llm import Generator, vram_mib
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    print(f"loaded {cfg['generator']} in {gen.load_seconds}s, VRAM {vram_mib()}", flush=True)
    ids, n_prefix, mismatches = encode(gen, rows, cfg)
    print(f"prefix {n_prefix} tokens, {mismatches} boundary mismatches", flush=True)
    hook_check = check_hooks(gen, ids[0]) if args.check_hooks else None
    if hook_check:
        print(f"hook check: {hook_check}", flush=True)

    t0 = time.time()
    res = collect(gen, rows, ids, n_prefix, cfg, keys_of=keys_of, keep_text=False,
                  per_text_path=out_dir / "per_text_mean.npy" if args.per_text else None)
    if args.per_text:
        with open(out_dir / "rows.json", "w", encoding="utf-8") as f:
            json.dump([{k: r[k] for k in ("text_id", "sentiment", "sarcasm", "dialect")} for r in rows], f, ensure_ascii=False)
    torch.save({"sums": res["neuron_sums"], "counts": res["counts"],
                "fold": {r["text_id"]: r["_fold"] for r in rows}}, out_dir / "neuron_sums.pt")
    meta = {"config": cfg, "config_file": str(args.config), "limit": args.limit, "per_text": args.per_text, "n_tweets": len(rows),
            "folds": FOLDS, "group_counts": res["counts"], "prefix_tokens": n_prefix,
            "boundary_mismatches": mismatches, "hook_check": hook_check, "generator_revision": gen.revision,
            "seconds": round(time.time() - t0), "vram": vram_mib(), "git_commit": git_commit(),
            "python": platform.python_version(), "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(out_dir / "meta.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"saved to {out_dir} ({meta['seconds']}s)", flush=True)


if __name__ == "__main__":
    sys.exit(main())
