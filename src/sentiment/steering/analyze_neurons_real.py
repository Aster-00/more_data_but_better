"""Do class-specific neurons hold up on unseen real tweets? (SV01 neurons, CPU step)

Reads `neuron_sums.pt` of `activations_real`; no model is loaded. Non-sarcastic S1 train tweets.
Firing rate of a class = mean firing share, averaged with equal weight over the varieties (as the
per-dialect vectors). Firing gap of a class = its rate minus the mean rate of the other two classes.

Held-out test, 5 folds: the K neurons with the largest gap are picked on four folds, then their gap
is measured on the fifth, which played no part in picking them. The same is done
  shuffled  with labels shuffled inside each variety (selection with no real signal)
  random    with K random neurons (no selection)
  no link   measuring the held-out gap on tweets without a link only
Retention = held-out gap / picked gap: about 1 if the list is real, about 0 if it is chance.
Overlap = mean Jaccard between the lists of two folds: do different tweets pick the same neurons?

LAPE (Tang et al., ACL 2024) on all folds, same cut-offs as SV02: how many selected neurons belong to
one class only. K and the LAPE cut-offs are hand-set, for exploration.

Outputs per generator in results/sentiment/steering/sv01_<generator>_neurons/: metrics.json, report.md,
top_neurons.csv, layers.png.

Usage:
  python -m src.sentiment.steering.analyze_neurons_real --generators fanar qwen3 aya
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch

from src.data.build_dataset import git_commit
from src.sentiment.steering.analyze_generated import CLASSES, lape

VARIETIES = ("msa", "egypt", "gulf", "levant")
FOLDS = 5


def tables(ns: dict) -> dict:
    """Firing sums and counts as [class, variety, fold, ...], for all, no-link and shuffled tweets."""
    first = next(iter(ns["sums"].values()))["fire"]
    shape = (3, len(VARIETIES), FOLDS, *first.shape)
    out = {k: (torch.zeros(shape), torch.zeros(shape[:3])) for k in ("all", "nolink", "shuf")}
    for key, stats in ns["sums"].items():
        parts, n = key.split("|"), ns["counts"][key]
        if parts[0] == "shuf":
            c, v, f = CLASSES.index(parts[1]), VARIETIES.index(parts[2]), int(parts[3])
            targets = ["shuf"]
        else:
            if parts[1] == "1":
                continue
            c, v, f = CLASSES.index(parts[0]), VARIETIES.index(parts[2]), int(parts[4])
            targets = ["all"] + (["nolink"] if parts[3] == "0" else [])
        for t in targets:
            out[t][0][c, v, f] += stats["fire"]
            out[t][1][c, v, f] += n
    return out


def rates(tab: tuple, folds: list[int]) -> torch.Tensor:
    """Firing rate per class over `folds`, equal weight per variety; [3, L, I]."""
    s, n = tab
    per = s[:, :, folds].sum(2) / n[:, :, folds].sum(2).clamp(min=1)[..., None, None]
    return per.mean(1)


def gaps(p: torch.Tensor) -> torch.Tensor:
    """Firing gap of every class against the mean of the other two; [3, L, I]."""
    return p - (p.sum(0, keepdim=True) - p) / 2


def jaccard(lists: list[set]) -> float:
    """Mean Jaccard over all pairs of lists."""
    return float(np.mean([len(a & b) / len(a | b) for a, b in itertools.combinations(lists, 2)]))


def held_out(tabs: dict, k: int, seed: int) -> dict:
    """Picked and held-out gap of the top-k lists per class, for real, shuffled and random selection."""
    res = {c: {"picked": [], "held_out": [], "share_positive": [], "shuffled_picked": [], "shuffled_held_out": [],
               "random_held_out": [], "nolink_held_out": [], "lists": []} for c in CLASSES}
    gen = torch.Generator().manual_seed(seed)
    for f in range(FOLDS):
        tr = [x for x in range(FOLDS) if x != f]
        g_tr, g_te = gaps(rates(tabs["all"], tr)), gaps(rates(tabs["all"], [f]))
        g_no = gaps(rates(tabs["nolink"], [f]))
        s_tr, s_te = gaps(rates(tabs["shuf"], tr)), gaps(rates(tabs["shuf"], [f]))
        for i, c in enumerate(CLASSES):
            top = torch.topk(g_tr[i].flatten(), k).indices
            sel = torch.topk(s_tr[i].flatten(), k).indices
            rnd = torch.randint(0, g_te[i].numel(), (k,), generator=gen)
            r = res[c]
            r["picked"].append(float(g_tr[i].flatten()[top].mean()))
            r["held_out"].append(float(g_te[i].flatten()[top].mean()))
            r["share_positive"].append(float((g_te[i].flatten()[top] > 0).float().mean()))
            r["nolink_held_out"].append(float(g_no[i].flatten()[top].mean()))
            r["shuffled_picked"].append(float(s_tr[i].flatten()[sel].mean()))
            r["shuffled_held_out"].append(float(s_te[i].flatten()[sel].mean()))
            r["random_held_out"].append(float(g_te[i].flatten()[rnd].mean()))
            r["lists"].append(set(top.tolist()))
    out = {}
    for c, r in res.items():
        m = {x: round(float(np.mean(v)), 4) for x, v in r.items() if x != "lists"}
        m["retention"] = round(m["held_out"] / max(m["picked"], 1e-9), 3)
        m["shuffled_retention"] = round(m["shuffled_held_out"] / max(m["shuffled_picked"], 1e-9), 3)
        m["nolink_retention"] = round(m["nolink_held_out"] / max(m["picked"], 1e-9), 3)
        m["overlap"] = round(jaccard(r["lists"]), 3)
        out[c] = m
    return out


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--generators", nargs="+", required=True)
    p.add_argument("--k", nargs="+", type=int, default=[20, 100, 1000])
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--lape-quantile", type=float, default=0.95)
    p.add_argument("--lape-share", type=float, default=0.01)
    args = p.parse_args()

    for g in args.generators:
        t0 = time.time()
        rep = Path(f"results/sentiment/steering/sv01_{g}_neurons")
        rep.mkdir(parents=True, exist_ok=True)
        ns = torch.load(f"data/steering/sv01_{g}_neurons/neuron_sums.pt", weights_only=False)
        tabs = tables(ns)
        n_layers, n_int = tabs["all"][0].shape[3:]
        m: dict = {"generator": g, "n_layers": n_layers, "neurons_per_layer": n_int,
                   "n_neurons": n_layers * n_int, "tweets_per_class": {c: int(tabs["all"][1][i].sum()) for i, c in enumerate(CLASSES)},
                   "held_out": {str(k): held_out(tabs, k, args.seed) for k in args.k}}

        # All folds: LAPE membership, and the final top lists for reading.
        p_all = rates(tabs["all"], list(range(FOLDS)))
        sel, member, thr = lape(p_all, args.lape_quantile, args.lape_share)
        n_groups = member.sum(0)
        m["lape"] = {"threshold": round(thr, 4), "selected": int(sel.sum()),
                     "one_class": int((n_groups == 1).sum()), "two_classes": int((n_groups == 2).sum()),
                     "three_classes": int((n_groups == 3).sum()),
                     "one_class_only": {c: int(((n_groups == 1) & member[i]).sum()) for i, c in enumerate(CLASSES)}}
        g_all = gaps(p_all)
        k = args.k[1]
        counts = {}
        with open(rep / "top_neurons.csv", "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["class", "rank", "layer", "neuron", "gap", "fire_NEG", "fire_NEU", "fire_POS"])
            for i, c in enumerate(CLASSES):
                idx = torch.topk(g_all[i].flatten(), k).indices
                counts[c] = torch.bincount(idx // n_int, minlength=n_layers).tolist()
                for rank, j in enumerate(idx.tolist(), 1):
                    lay, neu = j // n_int, j % n_int
                    w.writerow([c, rank, lay, neu, round(float(g_all[i, lay, neu]), 4),
                                *[round(float(p_all[q, lay, neu]), 4) for q in range(3)]])
        m["top_k_by_layer"] = counts
        m["git_commit"], m["seconds"] = git_commit(), round(time.time() - t0)
        m["finished"] = time.strftime("%Y-%m-%d %H:%M")
        with open(rep / "metrics.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(m, f, ensure_ascii=False, indent=1)

        fig, ax = plt.subplots(figsize=(8, 4))
        for c in CLASSES:
            ax.plot(range(1, n_layers + 1), counts[c], label=c)
        ax.set(xlabel="decoder layer", ylabel=f"neurons in the top {k}", title=f"{g}: where the top neurons sit")
        ax.legend()
        fig.tight_layout(); fig.savefig(rep / "layers.png", dpi=130); plt.close(fig)

        L = [f"# {g}: class-specific neurons on real S1 train", "",
             "Generated by `src.sentiment.steering.analyze_neurons_real`; do not edit. Firing gap = class rate minus the "
             "mean of the other two. Held-out = fold not used to pick the neurons.", "",
             "| K | Class | Picked gap | Held-out gap | Retention | No-link retention | Shuffled retention | Random gap | Overlap |",
             "|---|---|---|---|---|---|---|---|---|"]
        for kk, row in m["held_out"].items():
            for c, r in row.items():
                L.append(f"| {kk} | {c} | {r['picked']:.3f} | {r['held_out']:.3f} | {r['retention']:.2f} | {r['nolink_retention']:.2f} | "
                         f"{r['shuffled_retention']:.2f} | {r['random_held_out']:.4f} | {r['overlap']:.2f} |")
        L += ["", f"LAPE: {m['lape']}", "", "![layers](layers.png)", ""]
        with open(rep / "report.md", "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(L))
        print(f"{g}: done, {m['seconds']}s", flush=True)


if __name__ == "__main__":
    sys.exit(main())
