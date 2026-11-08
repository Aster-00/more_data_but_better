"""Choose the neurons for neuron steering from real S1 train tweets (SNG runs, CPU step).

Reads the per-tweet pass of `activations_real --per-text`; no model is loaded. Non-sarcastic tweets
only (as the vectors); dev and test are never read. Layers are decoder layer indices (0-based).

  lape         Tang 2024, recipe of Elozeiri 2026: firing probability per class (equal weight per
               variety); keep neurons whose probability is in the top `lape_prob_quantile` for at least
               one class, then the lowest `lape_share` of all neurons by entropy across the classes.
               A neuron belongs to every class where its probability passes the threshold. Ranked by
               entropy (lowest first).
  ap           Kojima 2024: each neuron's per-tweet mean value scored by average precision for "class
               vs rest", pooled over varieties; the `ap_k` highest (part +1) and `ap_k` lowest (part -1).
               Ranked by distance from the class share (the AP of a useless neuron).
  random_lape  per class, random neurons with the same count per layer as the lape list (SNG08)
  random_ap    the same for the ap list

Also saved, for every neuron and class: mean and median of the per-tweet value over the class's
tweets (the fixed values of fix_mean / fix_median in `neuron_hook`).

Output: data/steering/sv01_<generator>_neurons_pertext/neurons.pt and neurons.json (counts, settings).

Usage:
  python -m src.sentiment.steering.select_neurons --generator fanar
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

from src.data.build_dataset import git_commit
from src.sentiment.steering.analyze_generated import lape
from src.sentiment.steering.analyze_neurons_real import FOLDS, rates, tables

CLASSES = ("NEG", "NEU", "POS")


def average_precision(values: torch.Tensor, positive: torch.Tensor) -> torch.Tensor:
    """AP of every column as a score for `positive` rows; values [N, C], positive [N] bool -> [C]."""
    order = torch.argsort(values, dim=0, descending=True)
    rel = positive[order].float()                                      # [N, C], ranked
    precision = rel.cumsum(0) / torch.arange(1, len(values) + 1, dtype=torch.float32)[:, None]
    return (precision * rel).sum(0) / positive.sum()


def per_text_stats(mm: np.ndarray, keep: np.ndarray, y: np.ndarray, chunk: int) -> dict:
    """AP per class, and class mean and median, for every neuron; read in column chunks."""
    n_cols = mm.shape[1]
    out = {k: torch.zeros((3, n_cols)) for k in ("ap", "mean", "median")}
    pos = {c: torch.from_numpy(y == c) for c in CLASSES}
    t0 = time.time()
    for start in range(0, n_cols, chunk):
        block = torch.from_numpy(np.asarray(mm[keep, start:start + chunk], dtype=np.float32))
        for i, c in enumerate(CLASSES):
            out["ap"][i, start:start + chunk] = average_precision(block, pos[c])
            out["mean"][i, start:start + chunk] = block[pos[c]].mean(0)
            out["median"][i, start:start + chunk] = block[pos[c]].median(0).values
        if (start // chunk) % 10 == 0:
            print(f"  columns {start + block.shape[1]}/{n_cols}, {(time.time() - t0) / 60:.1f} min", flush=True)
    return out


def random_like(entry: dict, n_int: int, seed: int) -> dict:
    """Random neurons with the same count per layer as `entry`, none of them in it."""
    g = torch.Generator().manual_seed(seed)
    layers, neurons = [torch.empty(0, dtype=torch.long)], [torch.empty(0, dtype=torch.long)]
    for lay in entry["layer"].unique().tolist():
        taken = set(entry["neuron"][entry["layer"] == lay].tolist())
        n = int((entry["layer"] == lay).sum())
        pool = torch.tensor([j for j in range(n_int) if j not in taken])
        pick = pool[torch.randperm(len(pool), generator=g)[:n]]
        layers.append(torch.full((n,), lay, dtype=torch.long))
        neurons.append(pick)
    return {"layer": torch.cat(layers), "neuron": torch.cat(neurons)}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--generator", required=True)
    p.add_argument("--lape-prob-quantile", type=float, default=0.95)
    p.add_argument("--lape-share", type=float, default=0.01)
    p.add_argument("--ap-k", type=int, default=1000)
    p.add_argument("--chunk", type=int, default=8192)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--limit", type=int, default=None, help="use the tiny-mode pass (_limitN)")
    args = p.parse_args()
    t0 = time.time()
    d = Path(f"data/steering/sv01_{args.generator}_neurons_pertext")
    if args.limit is not None:
        d = d.with_name(d.name + f"_limit{args.limit}")

    # LAPE from the firing sums, all folds, equal weight per variety.
    ns = torch.load(d / "neuron_sums.pt", weights_only=False)
    p_all = rates(tables(ns)["all"], list(range(FOLDS)))               # [3, L, I]
    n_layers, n_int = p_all.shape[1:]
    sel, member, thr = lape(p_all, args.lape_prob_quantile, args.lape_share)
    q = p_all / p_all.sum(0, keepdim=True).clamp(min=1e-12)
    entropy = -(q * q.clamp(min=1e-12).log()).sum(0)                    # [L, I]
    methods: dict = {"lape": {}, "ap": {}, "random_lape": {}, "random_ap": {}}
    for i, c in enumerate(CLASSES):
        idx = member[i].flatten().nonzero().squeeze(1)
        idx = idx[torch.argsort(entropy.flatten()[idx])]
        methods["lape"][c] = {"layer": idx // n_int, "neuron": idx % n_int, "score": entropy.flatten()[idx]}

    # AP and class values from the per-tweet means, non-sarcastic tweets.
    with open(d / "rows.json", encoding="utf-8") as f:
        rows = json.load(f)
    keep = np.array([not r["sarcasm"] for r in rows])
    y = np.array([r["sentiment"] for r in rows])[keep]
    mm = np.load(d / "per_text_mean.npy", mmap_mode="r")
    st = per_text_stats(mm, np.where(keep)[0], y, args.chunk)
    for i, c in enumerate(CLASSES):
        ap = st["ap"][i]
        base = float((y == c).mean())                                    # AP of a neuron with no signal
        k = min(args.ap_k, len(ap) // 2)
        top, bottom = torch.topk(ap, k).indices, torch.topk(-ap, k).indices
        idx = torch.cat([top, bottom])
        part = torch.cat([torch.ones(k, dtype=torch.long), -torch.ones(k, dtype=torch.long)])
        order = torch.argsort(-(ap[idx] - base).abs())
        idx, part = idx[order], part[order]
        methods["ap"][c] = {"layer": idx // n_int, "neuron": idx % n_int, "score": ap[idx], "part": part}
    for i, c in enumerate(CLASSES):
        for m in ("lape", "ap"):
            methods[f"random_{m}"][c] = random_like(methods[m][c], n_int, args.seed + 7 * i + (m == "ap"))

    stats = {k: st[k].reshape(3, n_layers, n_int).half() for k in ("mean", "median")}
    torch.save({"methods": methods, "stats": stats, "lape_threshold": thr, "ap_base": {c: float((y == c).mean()) for c in CLASSES}},
               d / "neurons.pt")
    info = {"generator": args.generator, "n_tweets": int(keep.sum()), "n_layers": int(n_layers), "neurons_per_layer": int(n_int),
            "settings": {k: v for k, v in vars(args).items()}, "lape_threshold": round(thr, 4),
            "counts": {m: {c: int(len(e["layer"])) for c, e in v.items()} for m, v in methods.items()},
            "lape_layers": {c: torch.bincount(methods["lape"][c]["layer"], minlength=n_layers).tolist() for c in CLASSES},
            "ap_layers": {c: torch.bincount(methods["ap"][c]["layer"], minlength=n_layers).tolist() for c in CLASSES},
            "overlap_lape_ap": {c: len(set((methods["lape"][c]["layer"] * n_int + methods["lape"][c]["neuron"]).tolist())
                                       & set((methods["ap"][c]["layer"] * n_int + methods["ap"][c]["neuron"]).tolist())) for c in CLASSES},
            "git_commit": git_commit(), "seconds": round(time.time() - t0), "finished": time.strftime("%Y-%m-%d %H:%M")}
    with open(d / "neurons.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(info, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: info[k] for k in ("counts", "overlap_lape_ap", "seconds")}), flush=True)


if __name__ == "__main__":
    sys.exit(main())
