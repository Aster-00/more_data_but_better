"""Residual-stream DiffMean steering vectors from real S1 train tweets (steering plan, step 2).

Each train tweet is placed in the assistant turn of the generator's chat template (user turn =
a fixed neutral request), so activations come from response positions, as during generation.
For every layer the hidden state is averaged over the tweet's tokens, and the per-tweet means
are summed per group (sentiment, sarcasm, dialect). A vector is a difference of group means:

  pooled       mean(target tweets) - mean(contrast tweets), dialects mixed as they come
  per_dialect  the same difference inside each variety, then averaged with equal weight over
               the varieties with >= min_group_size tweets on both sides. S1 train is skewed
               (MSA is 78.5% of NEU but 57.7% of NEG; half of sarcastic NEG is Egyptian), so a
               pooled vector partly encodes dialect; this mode removes that.

A union side ("NEG + NEU") is tweet-weighted within a dialect. Every vector is L2-normalised
per layer. Layer index 0 = embeddings, l = output of decoder layer l-1 (hidden_states order).

Also saved: the mean per-token residual norm per layer (to scale alpha), group counts, the
cosine of every vector with an egypt-vs-msa direction (how much dialect it carries), and
per-tweet mean vectors (fp16) on every `text_vector_layer_step`-th layer for the probe check.

Only S1 train is read. Dev and test are never used here.

Outputs in output_dir: group_sums.pt, vectors.pt, text_vectors.pt, meta.json.

Usage:
  python -m src.sentiment.steering.extract --config configs/sentiment/steering/sv01_fanar.json --limit 48 --check-hooks
  python -m src.sentiment.steering.extract --config configs/sentiment/steering/sv01_fanar.json
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from collections import Counter
from pathlib import Path

import torch

from src.data.build_dataset import git_commit


def group_key(sentiment: str, sarcasm: bool, dialect: str) -> str:
    """Key of one (sentiment, sarcasm, dialect) group."""
    return f"{sentiment}|{int(bool(sarcasm))}|{dialect}"


def load_train(cfg: dict, limit: int | None) -> list[dict]:
    """S1 train tweets of the configured varieties; tiny mode = a seeded random `limit` of them."""
    with open(cfg["train_data"], encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    rows = [r for r in rows if r["dialect"] in cfg["varieties"] and r["split"] == "train"]
    # Tiny mode: a seeded shuffle first, so the subset covers the groups instead of the file head.
    if limit is not None:
        random.Random(cfg["seed"]).shuffle(rows)
        rows = rows[:limit]
    return rows


def decoder_layers(model) -> torch.nn.ModuleList:
    """The decoder blocks whose outputs are the residual stream (where steering hooks go)."""
    for path in ("model.layers", "model.model.layers", "transformer.h"):
        obj = model
        try:
            for part in path.split("."):
                obj = getattr(obj, part)
            return obj
        except AttributeError:
            continue
    raise AttributeError(f"no decoder layer list found on {type(model).__name__}")


def encode(gen, rows: list[dict], cfg: dict) -> tuple[list[list[int]], int, int]:
    """Token ids of prefix + tweet per row; return ids, prefix length, boundary mismatches.

    The prefix is the chat-templated user turn plus the assistant header; the tweet follows it
    directly (no end-of-turn token), exactly where generated text would start.
    """
    prefix = gen.render([{"role": "user", "content": cfg["user_prompt"]}])
    prefix_ids = gen.tokenizer(prefix, add_special_tokens=False)["input_ids"]
    n_prefix, mismatches, out = len(prefix_ids), 0, []
    for r in rows:
        ids = gen.tokenizer(prefix + r[cfg["text_field"]], add_special_tokens=False)["input_ids"]
        # A merge across the prefix/tweet boundary would shift the tweet span; count it.
        mismatches += ids[:n_prefix] != prefix_ids
        out.append(ids[:n_prefix + cfg["max_text_tokens"]])
    return out, n_prefix, mismatches


@torch.no_grad()
def check_hooks(gen, ids: list[int]) -> dict:
    """Confirm that a forward hook on decoder layer k sees hidden_states[k + 1] (middle layer).

    The steering hook adds to that same output, so this checks that vectors and hooks index
    the residual stream the same way.
    """
    layers = decoder_layers(gen.model)
    k, seen = len(layers) // 2, {}

    def hook(module, inputs, output):
        seen["h"] = (output[0] if isinstance(output, tuple) else output).detach()

    handle = layers[k].register_forward_hook(hook)
    try:
        x = torch.tensor([ids], device=gen.model.device)
        hs = gen.model(input_ids=x, output_hidden_states=True).hidden_states
    finally:
        handle.remove()
    diff = (hs[k + 1].float() - seen["h"].float()).abs().max().item()
    return {"layer": k, "n_layers": len(layers), "max_abs_diff": diff, "match": diff < 1e-3}


@torch.no_grad()
def collect(gen, rows: list[dict], ids: list[list[int]], n_prefix: int, cfg: dict) -> dict:
    """Per-group sums of per-tweet mean hidden states, token-norm stats and per-tweet vectors."""
    pad = gen.tokenizer.pad_token_id
    sums, counts = {}, Counter()
    norm_sum, norm_tokens = None, 0
    text_vecs, layer_sel = None, None
    # Length-sorted batches: little padding, so the GPU time goes to real tokens.
    order = sorted(range(len(rows)), key=lambda i: len(ids[i]))
    bs, t0 = cfg["batch_size"], time.time()
    for b, start in enumerate(range(0, len(order), bs), 1):
        idx = order[start:start + bs]
        width = max(len(ids[i]) for i in idx)
        # Right padding; the tweet mask marks positions n_prefix .. len(ids) - 1 of each row.
        x = torch.full((len(idx), width), pad, dtype=torch.long)
        attn = torch.zeros((len(idx), width), dtype=torch.long)
        tweet = torch.zeros((len(idx), width), dtype=torch.bool)
        for j, i in enumerate(idx):
            x[j, :len(ids[i])] = torch.tensor(ids[i])
            attn[j, :len(ids[i])] = 1
            tweet[j, n_prefix:len(ids[i])] = True
        # The base model (no LM head): vocabulary logits are not needed and cost ~1 GB per batch.
        hs = gen.model.model(input_ids=x.to(gen.model.device), attention_mask=attn.to(gen.model.device),
                             output_hidden_states=True).hidden_states
        # One layer at a time in fp32: stacking all layers in fp32 overflowed the 8 GB card.
        m = tweet.to(hs[0].device)[:, :, None].float()       # [B, T, 1]
        n_tok = m.sum(1).clamp(min=1)                         # [B, 1]
        means = torch.stack([(h.float() * m).sum(1) / n_tok for h in hs]).cpu()                   # [L+1, B, H]
        tok_norm = torch.stack([(h.float().norm(dim=-1) * m[..., 0]).sum() for h in hs]).double().cpu()  # [L+1]
        del hs
        norm_sum = tok_norm if norm_sum is None else norm_sum + tok_norm
        norm_tokens += int(tweet.sum())

        # First batch: allocate the per-tweet store (every step-th layer, fp16, original order).
        if text_vecs is None:
            layer_sel = list(range(0, means.shape[0], cfg["text_vector_layer_step"]))
            text_vecs = torch.empty((len(rows), len(layer_sel), means.shape[-1]), dtype=torch.float16)
        for j, i in enumerate(idx):
            r = rows[i]
            key = group_key(r["sentiment"], r["sarcasm"], r["dialect"])
            v = means[:, j].double()
            sums[key] = v if key not in sums else sums[key] + v
            counts[key] += 1
            text_vecs[i] = means[layer_sel, j].half()
        if b % 50 == 0 or start + bs >= len(order):
            el = time.time() - t0
            print(f"  batch {b}: {start + len(idx)}/{len(order)} tweets, {el / 60:.1f} min", flush=True)
    return {"sums": sums, "counts": dict(counts), "token_norm_mean": (norm_sum / norm_tokens).float(),
            "text_vectors": text_vecs, "text_vector_layers": layer_sel}


def side_mean(sums: dict, counts: dict, side: list, dialects: list[str]) -> tuple[torch.Tensor | None, int]:
    """Tweet-weighted mean over the (sentiment, sarcasm) groups of one side, within `dialects`."""
    keys = [group_key(s, sc, d) for s, sc in side for d in dialects]
    n = sum(counts.get(k, 0) for k in keys)
    if n == 0:
        return None, 0
    return sum(sums[k] for k in keys if k in sums) / n, n


def unit(v: torch.Tensor) -> torch.Tensor:
    """L2-normalise every layer row."""
    return (v / v.norm(dim=-1, keepdim=True).clamp(min=1e-12)).float()


def build_vectors(sums: dict, counts: dict, cfg: dict) -> tuple[dict, dict]:
    """Pooled and per-dialect unit vectors per spec; return vectors and their build info."""
    vectors, info = {}, {}
    for name, spec in cfg["vectors"].items():
        vectors[name], info[name] = {}, {}
        # Pooled: all varieties together.
        t, nt = side_mean(sums, counts, spec["target"], cfg["varieties"])
        c, nc = side_mean(sums, counts, spec["contrast"], cfg["varieties"])
        if t is not None and c is not None:
            vectors[name]["pooled"] = unit(t - c)
            info[name]["pooled"] = {"n_target": nt, "n_contrast": nc,
                                    "raw_norm": [round(x, 4) for x in (t - c).norm(dim=-1).tolist()]}
        # Per dialect: the difference inside each variety large enough on both sides, equal weights.
        diffs, used = [], {}
        for d in cfg["varieties"]:
            t, nt = side_mean(sums, counts, spec["target"], [d])
            c, nc = side_mean(sums, counts, spec["contrast"], [d])
            if nt >= cfg["min_group_size"] and nc >= cfg["min_group_size"]:
                diffs.append(t - c)
                used[d] = {"n_target": nt, "n_contrast": nc}
        if diffs:
            raw = sum(diffs) / len(diffs)
            vectors[name]["per_dialect"] = unit(raw)
            info[name]["per_dialect"] = {"dialects": used,
                                         "raw_norm": [round(x, 4) for x in raw.norm(dim=-1).tolist()]}
        if not vectors[name]:
            print(f"WARNING: vector {name!r} has an empty side; not built", flush=True)
    return vectors, info


def dialect_cosines(vectors: dict, sums: dict, counts: dict, cfg: dict) -> dict:
    """Cosine per layer between each vector and the egypt-vs-msa direction (all sentiments)."""
    every = [(s, sc) for s in ("NEG", "NEU", "POS") for sc in (False, True)]
    e, _ = side_mean(sums, counts, every, ["egypt"])
    m, _ = side_mean(sums, counts, every, ["msa"])
    if e is None or m is None:
        return {}
    d = unit(e - m)
    return {name: {mode: [round(x, 3) for x in (v * d).sum(-1).tolist()] for mode, v in modes.items()}
            for name, modes in vectors.items()}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: a seeded random N train tweets")
    p.add_argument("--check-hooks", action="store_true", help="verify hook output == hidden_states[k+1]")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    out_dir = Path(cfg["output_dir"])
    # Tiny runs write to their own folder so they never mix with the real vectors.
    if args.limit is not None:
        out_dir = out_dir.with_name(out_dir.name + f"_limit{args.limit}")
        cfg["min_group_size"] = 1
    if (out_dir / "meta.json").exists():
        raise SystemExit(f"{out_dir} already has a finished extraction; use a new output_dir")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_train(cfg, args.limit)
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
    res = collect(gen, rows, ids, n_prefix, cfg)
    vectors, info = build_vectors(res["sums"], res["counts"], cfg)

    torch.save({"sums": res["sums"], "counts": res["counts"]}, out_dir / "group_sums.pt")
    torch.save({"vectors": vectors, "token_norm_mean": res["token_norm_mean"]}, out_dir / "vectors.pt")
    torch.save({"vectors": res["text_vectors"], "layers": res["text_vector_layers"],
                "text_id": [r["text_id"] for r in rows], "sentiment": [r["sentiment"] for r in rows],
                "sarcasm": [bool(r["sarcasm"]) for r in rows], "dialect": [r["dialect"] for r in rows]},
               out_dir / "text_vectors.pt")
    meta = {"config": cfg, "config_file": str(args.config), "limit": args.limit, "n_tweets": len(rows),
            "group_counts": res["counts"], "prefix_tokens": n_prefix, "boundary_mismatches": mismatches,
            "n_layers_plus_embeddings": int(res["token_norm_mean"].shape[0]),
            "token_norm_mean": [round(x, 2) for x in res["token_norm_mean"].tolist()],
            "vector_info": info, "cos_with_egypt_vs_msa": dialect_cosines(vectors, res["sums"], res["counts"], cfg),
            "hook_check": hook_check, "generator_revision": gen.revision, "seconds": round(time.time() - t0),
            "vram": vram_mib(), "git_commit": git_commit(), "python": platform.python_version(),
            "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(out_dir / "meta.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"saved to {out_dir} ({meta['seconds']}s)", flush=True)


if __name__ == "__main__":
    sys.exit(main())
