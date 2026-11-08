"""Method 1 layer choice for vector steering (refusal-paper selection rule), resumable.

For one generator, every candidate layer is tested by steering with the no-label prompt, so any
sentiment in the text comes from the vector ("keep a candidate only if adding it produces the property
on its own"). Every layer gets the same requests and the same sampling seeds, so only the layer
changes; an unsteered baseline (same prompt, no hook) shows what the model writes by chance.

Steps (one command each):
  generate   texts for the baseline and every layer, appended to <output_dir>/texts.jsonl
  kl         side-effect check on neutral prompts: KL(unsteered || steered) of the next-token
             distribution at the response start, mean over prompts and the three class vectors.
             kl.mode "add" adds the vector as in generation; "ablate" removes the direction at every
             position (the refusal paper's form). Written to <output_dir>/kl.json
  score      SR01 MARBERT judge (the fidelity judge of the quality table) on every text; per layer
             the share judged as the requested class, against the baseline, with KL. Written to
             <output_dir>/summary.json and summary.md. The final choice is Ammar's.

The confirmation stage ("stage": "confirm") uses other request ids and seeds than the screen, so the
layers are chosen on a separate validation set. Vectors come from SV01 (real S1 train only).

Config keys: run_name, stage, generator, cache_dir, quantization, vectors, mode, strength, alpha,
token_budget, template (no-label), condition, varieties, sentiments, per_cell, seed, layers (list, or
{"below_depth": 0.8}), skip_layers, sampling, batch_size, output_dir, kl {prompts, mode, max_kl}.

Usage:
  python -m src.sentiment.steering.layer_sweep --config <config> --step generate [--limit 2 --layers 10 20]
  python -m src.sentiment.steering.layer_sweep --config <config> --step kl
  python -m src.sentiment.steering.layer_sweep --config <config> --step score
  python -m src.sentiment.steering.layer_sweep --config <config> --step generate --layers 21 --alpha 0.2   # alpha calibration
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import torch

from src.data.build_dataset import clean_text, git_commit
from src.generation.generate import existing_request_ids
from src.generation.prompts import Template, parse_output
from src.sentiment.generate import CLEAN_STEPS, build_plan, render_messages, strip_translation
from src.sentiment.steering.extract import decoder_layers
from src.sentiment.steering.hook import Steerer

CLASSES = ("NEG", "NEU", "POS")


def candidate_layers(cfg: dict, n_layers: int) -> list[int]:
    """Layers to test (hidden_states order, 1..n_layers), minus `skip_layers`."""
    spec = cfg["layers"]
    if isinstance(spec, dict):
        layers = [l for l in range(1, n_layers + 1) if l < spec["below_depth"] * n_layers]
    else:
        layers = list(spec)
    return [l for l in layers if l not in set(cfg.get("skip_layers", []))]


def steer_cfg(cfg: dict, layer: int) -> dict:
    """The Steerer settings for one layer."""
    return {"vectors": cfg["vectors"], "mode": cfg["mode"], "strength": cfg["strength"], "layer": layer,
            "alpha": cfg["alpha"], "token_budget": cfg.get("token_budget")}


def generate(cfg: dict, layers: list[int], limit: int | None) -> None:
    """Texts for the baseline (layer 0 = unsteered) and every layer; skips texts already written."""
    from src.generation.llm import Generator, Sampling, vram_mib
    template = Template.load(Path(cfg["template"]))
    if "{sentiment_name}" in template.user:
        raise ValueError("Method 1 needs the no-label prompt: the sentiment must come from the vector")
    plan = build_plan({**cfg, "set_name": f"{cfg['run_name']}:{cfg['stage']}"})
    if limit is not None:
        plan = plan[:limit]
    out = Path(cfg["output_dir"]) / "texts.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)
    done = existing_request_ids(out)
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    sampling = Sampling(**cfg["sampling"])
    print(f"loaded {cfg['generator']} in {gen.load_seconds}s, VRAM {vram_mib()}", flush=True)
    bs, commit = cfg["batch_size"], git_commit()
    with open(out, "a", encoding="utf-8", newline="\n") as f:
        for layer in [0] + layers:
            todo = [r for r in plan if f"L{layer}:{r.request_id}" not in done]
            if not todo:
                continue
            steerer = Steerer(gen.model, steer_cfg(cfg, layer)) if layer else None
            t0 = time.time()
            for start in range(0, len(todo), bs):
                batch = todo[start:start + bs]
                # Seed from the request, not the layer: every layer sees the same sampling noise.
                seed = cfg["seed"] + int(hashlib.sha1(batch[0].request_id.encode()).hexdigest()[:6], 16)
                msgs = [render_messages(template, r) for r in batch]
                if steerer:
                    with steerer:
                        steerer.set_rows([r.sentiment.lower() for r in batch])
                        outs = gen.generate(msgs, sampling, seed=seed)
                else:
                    outs = gen.generate(msgs, sampling, seed=seed)
                for req, o in zip(batch, outs):
                    parsed = parse_output(o["raw_output"].replace("**", ""), 1, "arabic")
                    raw, _ = strip_translation(parsed[0]) if parsed else (None, False)
                    text = clean_text(raw, CLEAN_STEPS)[0] if raw else None
                    f.write(json.dumps({"request_id": f"L{layer}:{req.request_id}", "layer": layer,
                                        "alpha": cfg["alpha"] if layer else 0.0, "strength": cfg["strength"],
                                        "variety": req.variety, "sentiment": req.sentiment, "text": text,
                                        "raw_output": o["raw_output"], "seed": seed, "stage": cfg["stage"],
                                        "scales": steerer.scales if steerer else None,
                                        "vectors_sha256": steerer.sha256 if steerer else None,
                                        "template_sha256": template.sha256, "git_commit": commit},
                                       ensure_ascii=False) + "\n")
                f.flush()
            print(f"layer {layer}: {len(todo)} texts, {(time.time() - t0) / 60:.1f} min", flush=True)


@torch.no_grad()
def kl_check(cfg: dict, layers: list[int]) -> None:
    """Mean KL(unsteered || steered) of the next-token distribution on neutral prompts, per layer."""
    from src.generation.llm import Generator
    with open(cfg["kl"]["prompts"], encoding="utf-8") as f:
        prompts = json.load(f)
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    texts = [gen.render([{"role": "user", "content": p}]) for p in prompts]
    enc = gen.tokenizer(texts, return_tensors="pt", padding=True, add_special_tokens=False).to(gen.model.device)
    base = torch.log_softmax(gen.model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)
    mode, res = cfg["kl"]["mode"], {}
    for layer in layers:
        st = Steerer(gen.model, steer_cfg(cfg, layer))
        kls = []
        for name in ("neg", "neu", "pos"):
            if mode == "add":
                with st:
                    st.set_rows([name] * len(texts))
                    lp = torch.log_softmax(gen.model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)
            else:
                # Ablate: remove the unit direction from the layer output at every position.
                v = torch.nn.functional.normalize(st.vectors[name], dim=0)

                def hook(module, inputs, output, v=v):
                    h = output[0] if isinstance(output, tuple) else output
                    vv = v.to(device=h.device, dtype=h.dtype)
                    h -= (h @ vv)[..., None] * vv
                    return output
                handle = decoder_layers(gen.model)[layer - 1].register_forward_hook(hook)
                try:
                    lp = torch.log_softmax(gen.model(**enc, logits_to_keep=1).logits[:, -1].float(), -1)
                finally:
                    handle.remove()
            kls.append(float((base.exp() * (base - lp)).sum(-1).mean()))
        res[layer] = {"kl_mean": round(float(np.mean(kls)), 5), "kl_by_class": dict(zip(CLASSES, [round(k, 5) for k in kls]))}
        print(f"layer {layer}: KL {res[layer]['kl_mean']}", flush=True)
    with open(Path(cfg["output_dir"]) / "kl.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump({"mode": mode, "n_prompts": len(prompts), "layers": res, "git_commit": git_commit()}, f, indent=1)


def score(cfg: dict) -> None:
    """Judge every text; per layer the share judged as the requested class, against the baseline."""
    from src.sentiment.measure_quality import SENTIMENTS, sentiment_probs
    d = Path(cfg["output_dir"])
    with open(d / "texts.jsonl", encoding="utf-8") as f:
        recs = [json.loads(line) for line in f]
    recs = [r for r in recs if r["text"]]
    probs = sentiment_probs([r["text"] for r in recs], "cuda" if torch.cuda.is_available() else "cpu")
    pred = [SENTIMENTS[k] for k in probs.argmax(1)]
    kl = {}
    if (d / "kl.json").exists():
        with open(d / "kl.json", encoding="utf-8") as f:
            kl = {int(k): v for k, v in json.load(f)["layers"].items()}
    max_kl = cfg.get("kl", {}).get("max_kl", 0.1)
    by_layer: dict = {}
    for r, p in zip(recs, pred):
        by_layer.setdefault(r["layer"], []).append((r["sentiment"], p))
    base = by_layer.get(0, [])
    base_share = float(np.mean([s == p for s, p in base])) if base else float("nan")
    rows = {}
    for layer, pairs in sorted(by_layer.items()):
        share = float(np.mean([s == p for s, p in pairs]))
        n = len(pairs)
        # Normal-approximation 95% interval of the gain over the baseline (independent samples).
        se = math.sqrt(share * (1 - share) / n + (base_share * (1 - base_share) / len(base) if base else 0))
        rows[layer] = {"n": n, "share": round(share, 4), "gain": round(share - base_share, 4),
                       "gain_low": round(share - base_share - 1.96 * se, 4),
                       "per_class": {c: round(float(np.mean([s == p for s, p in pairs if s == c])), 4) for c in CLASSES
                                     if any(s == c for s, _ in pairs)},
                       "kl": kl.get(layer, {}).get("kl_mean")}
        rows[layer]["passes"] = bool(layer and rows[layer]["gain_low"] > 0
                                     and rows[layer]["kl"] is not None and rows[layer]["kl"] < max_kl)
    summary = {"run_name": cfg["run_name"], "stage": cfg["stage"], "baseline_share": round(base_share, 4),
               "max_kl": max_kl, "layers": rows, "git_commit": git_commit(), "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(d / "summary.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    L = [f"# {cfg['run_name']} ({cfg['stage']}): Method 1 layer test", "",
         "Generated by `src.sentiment.steering.layer_sweep --step score`; do not edit. Share = texts the SR01 judge reads as the "
         "requested class, with no sentiment in the prompt. Layer 0 = unsteered baseline.", "",
         "| Layer | n | Share | Gain over baseline | Gain, lower 95% | NEG | NEU | POS | KL | Passes |", "|---|---|---|---|---|---|---|---|---|---|"]
    for layer, r in rows.items():
        pc = r["per_class"]
        L.append(f"| {layer} | {r['n']} | {r['share']:.3f} | {r['gain']:+.3f} | {r['gain_low']:+.3f} | "
                 f"{pc.get('NEG', float('nan')):.2f} | {pc.get('NEU', float('nan')):.2f} | {pc.get('POS', float('nan')):.2f} | "
                 f"{r['kl'] if r['kl'] is not None else '–'} | {'yes' if r['passes'] else ''} |")
    with open(d / "summary.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L), flush=True)


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--step", choices=("generate", "kl", "score"), required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N requests per layer, own output folder")
    p.add_argument("--layers", type=int, nargs="+", default=None, help="override the candidate layers")
    p.add_argument("--alpha", type=float, default=None, help="alpha calibration: override alpha, own output folder")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.limit is not None:
        cfg["output_dir"] = str(Path(cfg["output_dir"]).with_name(Path(cfg["output_dir"]).name + f"_limit{args.limit}"))
    # Alpha calibration (one middle layer, several alphas): each alpha in its own folder.
    if args.alpha is not None:
        cfg["alpha"] = args.alpha
        cfg["output_dir"] = str(Path(cfg["output_dir"]).with_name(Path(cfg["output_dir"]).name + f"_alpha{args.alpha:g}"))
    n_layers = len(torch.load(cfg["vectors"], weights_only=False)["token_norm_mean"]) - 1
    layers = args.layers or candidate_layers(cfg, n_layers)
    print(f"{cfg['run_name']} {cfg['stage']}: layers {layers}", flush=True)
    if args.step == "generate":
        generate(cfg, layers, args.limit)
    elif args.step == "kl":
        kl_check(cfg, layers)
    else:
        score(cfg)


if __name__ == "__main__":
    sys.exit(main())
