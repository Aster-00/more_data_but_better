"""Residual-stream and MLP-neuron activations of a generator on its own synthetic texts (SV02, GPU step).

Each generated text is placed in the assistant turn of its generator's chat template (user turn =
the same fixed neutral request as SV01), so the activations come from response positions, as during
generation. One forward pass per batch, no sampling: the result is deterministic.

Per text and layer, two things are averaged over the text's tokens:
  residual   hidden state (hidden_states order: 0 = embeddings, l = output of decoder layer l-1)
  neurons    per MLP neuron of every decoder layer: firing share (act_fn(gate) > 0, the LAPE rule),
             mean and mean square of the down_proj input act_fn(gate) * up
Residual means are stored per text (fp16, every layer). Neuron statistics are too large per text
(42 x 14,336 for Fanar), so they are summed per (pair_type, pair_role, dialect) group; the role fixes
the sentiment. The CPU step (`analyze_generated`) builds vectors, probes and neuron rankings from these.

Outputs in output_dir: text_vectors.pt, neuron_sums.pt, meta.json.

Usage:
  python -m src.sentiment.steering.activations_generated --config configs/sentiment/steering/sv02_sg04_fanar.json --limit 48 --check-hooks
  python -m src.sentiment.steering.activations_generated --config configs/sentiment/steering/sv02_sg04_fanar.json
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
from src.sentiment.steering.extract import check_hooks, decoder_layers, encode


def neuron_key(r: dict) -> str:
    """Group of one text for the neuron sums: pair type, pair role and dialect."""
    return f"{r['pair_type']}|{r['pair_role']}|{r['dialect']}"


def load_rows(cfg: dict, limit: int | None) -> list[dict]:
    """Synthetic texts of the configured varieties; tiny mode = a seeded random `limit` of them."""
    with open(cfg["data"], encoding="utf-8") as f:
        rows = [json.loads(line) for line in f]
    rows = [r for r in rows if r["dialect"] in cfg["varieties"]]
    # Tiny mode: a seeded shuffle first, so the subset covers the groups instead of the file head.
    if limit is not None:
        random.Random(cfg["seed"]).shuffle(rows)
        rows = rows[:limit]
    return rows


@torch.no_grad()
def collect(gen, rows: list[dict], ids: list[list[int]], n_prefix: int, cfg: dict,
            keys_of=lambda r: [neuron_key(r)], keep_text: bool = True, per_text_path: Path | None = None) -> dict:
    """Per-text residual means (if `keep_text`) and per-group sums of per-text neuron statistics.

    `keys_of(row)` gives the groups a text is summed into (one or several). With `per_text_path`,
    every text's mean down_proj input of every neuron is also written there, fp16 [N, L * I] in the
    order of `rows` (a .npy memmap, so it never has to fit in memory).
    """
    layers = decoder_layers(gen.model)
    # Every layer must own its activation module, or one hook would see several layers.
    acts = [layer.mlp.act_fn for layer in layers]
    if len({id(a) for a in acts}) != len(acts):
        raise RuntimeError("act_fn is shared between layers; per-layer firing hooks would mix layers")

    # Hooks reduce [B, T, I] to per-text means at once, so no full activation tensor is kept.
    state: dict = {"m": None, "n": None, "fire": {}, "mean": {}, "sq": {}}

    def fire_hook(k):
        def hook(module, inputs, output):
            state["fire"][k] = ((output > 0).float() * state["m"]).sum(1) / state["n"]
        return hook

    def down_hook(k):
        def hook(module, inputs):
            x = inputs[0].float()
            state["mean"][k] = (x * state["m"]).sum(1) / state["n"]
            state["sq"][k] = (x.square() * state["m"]).sum(1) / state["n"]
        return hook

    handles = []
    for k, layer in enumerate(layers):
        handles.append(layer.mlp.act_fn.register_forward_hook(fire_hook(k)))
        handles.append(layer.mlp.down_proj.register_forward_pre_hook(down_hook(k)))

    pad = gen.tokenizer.pad_token_id
    n_layers = len(layers)
    sums, counts = {}, Counter()
    text_vecs, norm_sum, norm_tokens, per_text = None, None, 0, None
    # Length-sorted batches: little padding, so the GPU time goes to real tokens.
    order = sorted(range(len(rows)), key=lambda i: len(ids[i]))
    bs, t0 = cfg["batch_size"], time.time()
    try:
        for b, start in enumerate(range(0, len(order), bs), 1):
            idx = order[start:start + bs]
            width = max(len(ids[i]) for i in idx)
            # Right padding; the text mask marks positions n_prefix .. len(ids) - 1 of each row.
            x = torch.full((len(idx), width), pad, dtype=torch.long)
            attn = torch.zeros((len(idx), width), dtype=torch.long)
            text = torch.zeros((len(idx), width), dtype=torch.bool)
            for j, i in enumerate(idx):
                x[j, :len(ids[i])] = torch.tensor(ids[i])
                attn[j, :len(ids[i])] = 1
                text[j, n_prefix:len(ids[i])] = True
            dev = gen.model.device
            state["m"] = text.to(dev)[:, :, None].float()              # [B, T, 1]
            state["n"] = state["m"].sum(1).clamp(min=1)                 # [B, 1]
            # The base model (no LM head): vocabulary logits are not needed.
            hs = gen.model.model(input_ids=x.to(dev), attention_mask=attn.to(dev),
                                 output_hidden_states=True).hidden_states
            # One layer at a time in fp32 (stacking all layers in fp32 overflowed the card in SV01).
            means = torch.stack([(h.float() * state["m"]).sum(1) / state["n"] for h in hs]).cpu()   # [L+1, B, H]
            tok_norm = torch.stack([(h.float().norm(dim=-1) * state["m"][..., 0]).sum() for h in hs]).double().cpu()
            del hs
            norm_sum = tok_norm if norm_sum is None else norm_sum + tok_norm
            norm_tokens += int(text.sum())
            stats = {s: torch.stack([state[s][k] for k in range(n_layers)]).cpu() for s in ("fire", "mean", "sq")}  # [L, B, I]

            if per_text_path is not None:
                if per_text is None:
                    import numpy as np
                    per_text = np.lib.format.open_memmap(per_text_path, mode="w+", dtype=np.float16,
                                                         shape=(len(rows), stats["mean"].shape[0] * stats["mean"].shape[2]))
                for j, i in enumerate(idx):
                    per_text[i] = stats["mean"][:, j].reshape(-1).half().numpy()
            if keep_text and text_vecs is None:
                text_vecs = torch.empty((len(rows), means.shape[0], means.shape[-1]), dtype=torch.float16)
            for j, i in enumerate(idx):
                if keep_text:
                    text_vecs[i] = means[:, j].half()
                for key in keys_of(rows[i]):
                    if key not in sums:
                        sums[key] = {s: torch.zeros_like(stats[s][:, j], dtype=torch.float64) for s in stats}
                    for s in stats:
                        sums[key][s] += stats[s][:, j].double()
                    counts[key] += 1
            if b % 50 == 0 or start + bs >= len(order):
                print(f"  batch {b}: {start + len(idx)}/{len(order)} texts, {(time.time() - t0) / 60:.1f} min", flush=True)
    finally:
        for h in handles:
            h.remove()
        if per_text is not None:
            per_text.flush()
            del per_text
    # fp32 on disk: the sums are of per-text shares and means, so fp32 keeps ample precision.
    sums = {k: {s: v.float() for s, v in d.items()} for k, d in sums.items()}
    return {"text_vectors": text_vecs, "neuron_sums": sums, "counts": dict(counts),
            "token_norm_mean": (norm_sum / norm_tokens).float()}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: a seeded random N texts")
    p.add_argument("--check-hooks", action="store_true", help="verify hook output == hidden_states[k+1]")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    out_dir = Path(cfg["output_dir"])
    # Tiny runs write to their own folder so they never mix with the real activations.
    if args.limit is not None:
        out_dir = out_dir.with_name(out_dir.name + f"_limit{args.limit}")
    if (out_dir / "meta.json").exists():
        raise SystemExit(f"{out_dir} already has a finished extraction; use a new output_dir")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = load_rows(cfg, args.limit)
    print(f"{len(rows)} texts from {cfg['data']}", flush=True)
    generators = {r["generator"] for r in rows}
    # The activations must come from the model that wrote the texts (the one to be steered).
    if generators != {cfg["generator"]}:
        raise SystemExit(f"texts are from {generators}, config generator is {cfg['generator']}")

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
    fields = ("text_id", "pair_id", "pair_type", "pair_role", "sentiment", "dialect", "text")
    torch.save({"vectors": res["text_vectors"], **{f: [r[f] for r in rows] for f in fields}},
               out_dir / "text_vectors.pt")
    torch.save({"sums": res["neuron_sums"], "counts": res["counts"]}, out_dir / "neuron_sums.pt")
    meta = {"config": cfg, "config_file": str(args.config), "limit": args.limit, "n_texts": len(rows),
            "group_counts": res["counts"], "prefix_tokens": n_prefix, "boundary_mismatches": mismatches,
            "truncated_texts": sum(len(i) == n_prefix + cfg["max_text_tokens"] for i in ids),
            "n_layers_plus_embeddings": int(res["token_norm_mean"].shape[0]),
            "token_norm_mean": [round(x, 2) for x in res["token_norm_mean"].tolist()],
            "hook_check": hook_check, "generator_revision": gen.revision, "seconds": round(time.time() - t0),
            "vram": vram_mib(), "git_commit": git_commit(), "python": platform.python_version(),
            "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(out_dir / "meta.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"saved to {out_dir} ({meta['seconds']}s)", flush=True)


if __name__ == "__main__":
    sys.exit(main())
