"""What the SV01 class directions look like: overlap, noise level, surface features, stability (CPU).

Reads what `extract.py` saved; no model is loaded. S1 train only. For each generator, at the layer
given on the command line (one layer for all classes), on the non-sarcastic tweets:

  overlap    cosine between the class vectors, and between the pairwise directions; held-out AUC of
             each class against the rest and of each pair; confusion of the direction-only classifier
  noise      the same held-out d and AUC with labels shuffled inside each variety: what no signal looks like
  layers     best layer per class by held-out d (from analyze_real's metrics.json)
  features   correlation of the projection on each vector with surface features, over all tweets and
             inside each class (a within-class correlation means the direction tracks the feature
             beyond the label); share of each feature per class. The word list is hand-written.
  stability  cosine between vectors built on two random halves, repeated `--splits` times
  sarcasm    mean projection of sarcastic NEG against non-sarcastic NEG (sarcastic tweets are not in
             the vectors, so this is an unseen phenomenon)

Outputs: results/sentiment/steering/sv01_explore.json and, per generator, the tweets at both ends of
each direction in data/inspect/steering/sv01_<generator>_direction_ends.csv.

Usage:
  python -m src.sentiment.steering.explore_real --layers fanar=32 qwen3=32 aya=22
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

from src.data.build_dataset import git_commit
from src.sentiment.steering.analyze_generated import CLASSES, cohens_d, ovr_vector, unit

EMOJI_RE = re.compile("[\U0001F300-\U0001FAFF☀-➿]")
RELIGIOUS_RE = re.compile(r"الله|اللهم|ربي|ربنا|يارب|يا رب|آمين|امين")
FEATURES = {
    "link": lambda t: "URL" in t,
    "mention": lambda t: "USER" in t,
    "hashtag": lambda t: "#" in t,
    "emoji": lambda t: bool(EMOJI_RE.search(t)),
    "question": lambda t: "?" in t or "؟" in t,
    "exclamation": lambda t: "!" in t,
    "digit": lambda t: bool(re.search(r"[0-9٠-٩]", t)),
    "religious": lambda t: bool(RELIGIOUS_RE.search(t)),
}


def r(a: np.ndarray, b: np.ndarray) -> float:
    """Pearson correlation; 0 for a constant input."""
    return float(np.corrcoef(a, b)[0, 1]) if a.std() > 0 and b.std() > 0 else 0.0


def folds_of(n: int, k: int, seed: int) -> np.ndarray:
    """Seeded fold number per row."""
    order = list(range(n))
    random.Random(seed).shuffle(order)
    fold = np.empty(n, dtype=int)
    fold[order] = np.arange(n) % k
    return fold


def held_out(X: torch.Tensor, y: np.ndarray, dia: np.ndarray, varieties: list[str], min_n: int,
             k: int, seed: int) -> dict:
    """Held-out d and AUC per class, AUC per pair, and the confusion of the direction-only classifier."""
    fold = folds_of(len(y), k, seed)
    proj = {c: np.zeros(len(y)) for c in CLASSES}
    pair = {}
    for f in range(k):
        tr, te = np.where(fold != f)[0], np.where(fold == f)[0]
        mu = X[tr].mean(0)
        for c in CLASSES:
            proj[c][te] = ((X[te] - mu) @ unit(ovr_vector(X, y, dia, tr, c, varieties, min_n, "per_dialect"))).numpy()
        # Pair direction: difference of class means inside each variety, equal weights.
        for a, b in (("POS", "NEG"), ("POS", "NEU"), ("NEG", "NEU")):
            diffs = [X[tr[(y[tr] == a) & (dia[tr] == d)]].mean(0) - X[tr[(y[tr] == b) & (dia[tr] == d)]].mean(0)
                     for d in varieties]
            pair.setdefault((a, b), np.zeros(len(y)))[te] = ((X[te] - mu) @ unit(sum(diffs))).numpy()
    pred = np.array(CLASSES)[np.stack([proj[c] for c in CLASSES], 1).argmax(1)]
    return {"d": {c: round(cohens_d(proj[c][y == c], proj[c][y != c]), 3) for c in CLASSES},
            "auc": {c: round(float(roc_auc_score(y == c, proj[c])), 3) for c in CLASSES},
            "pair_auc": {f"{a}-{b}": round(float(roc_auc_score(y[(y == a) | (y == b)] == a, v[(y == a) | (y == b)])), 3)
                         for (a, b), v in pair.items()},
            "confusion": {c: {p: round(float((pred[y == c] == p).mean()), 3) for p in CLASSES} for c in CLASSES}}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--layers", nargs="+", required=True, help="generator=layer, one layer for all classes")
    p.add_argument("--folds", type=int, default=5)
    p.add_argument("--shuffles", type=int, default=3)
    p.add_argument("--splits", type=int, default=20)
    p.add_argument("--ends", type=int, default=30, help="tweets per end of each direction in the CSV")
    args = p.parse_args()
    t0 = time.time()
    out: dict = {"git_commit": git_commit(), "generators": {}}
    Path("data/inspect/steering").mkdir(parents=True, exist_ok=True)

    for item in args.layers:
        g, layer = item.split("=")
        layer = int(layer)
        with open(f"configs/sentiment/steering/sv01_{g}.json", encoding="utf-8") as f:
            cfg = json.load(f)
        data = Path(cfg["output_dir"])
        tv = torch.load(data / "text_vectors.pt", weights_only=False)
        vec = torch.load(data / "vectors.pt", weights_only=False)["vectors"]
        with open(cfg["train_data"], encoding="utf-8") as f:
            text_of = {x["text_id"]: x["text"] for x in map(json.loads, f)}
        i = list(tv["layers"]).index(layer)
        X_all = tv["vectors"][:, i].float()
        y_all, dia_all = np.array(tv["sentiment"]), np.array(tv["dialect"])
        sarc = np.array(tv["sarcasm"])
        texts_all = [text_of[t] for t in tv["text_id"]]
        keep = np.where(~sarc)[0]
        X, y, dia = X_all[keep], y_all[keep], dia_all[keep]
        texts = [texts_all[j] for j in keep]
        V = {c: vec[c.lower()]["per_dialect"] for c in CLASSES}         # [L+1, H] each
        res: dict = {"layer": layer, "n": int(len(y))}
        varieties, min_n = cfg["varieties"], cfg["min_group_size"]

        # Overlap of the full-data vectors at this layer, and its range over the middle layers.
        pairs = (("POS", "NEG"), ("POS", "NEU"), ("NEG", "NEU"))
        res["cosine"] = {f"{a}-{b}": round(float(V[a][layer] @ V[b][layer]), 3) for a, b in pairs}
        n_lay = V["POS"].shape[0]
        res["cosine_range_layers_8_to_last"] = {
            f"{a}-{b}": [round(float(x), 3) for x in (lambda s: (s.min(), s.max()))((V[a][8:-1] * V[b][8:-1]).sum(-1))]
            for a, b in pairs}
        M = torch.stack([V[c][layer] for c in CLASSES])
        sv = torch.linalg.svdvals(M)
        res["singular_share"] = [round(float(x), 3) for x in (sv ** 2 / (sv ** 2).sum())]

        res["held_out"] = held_out(X, y, dia, varieties, min_n, args.folds, cfg["seed"])

        # Noise level: labels shuffled inside each variety, so dialect stays as it is.
        noise = []
        for s in range(args.shuffles):
            rng = np.random.default_rng(s)
            ys = y.copy()
            for d in varieties:
                idx = np.where(dia == d)[0]
                ys[idx] = rng.permutation(ys[idx])
            noise.append(held_out(X, ys, dia, varieties, min_n, args.folds, cfg["seed"]))
        res["shuffled_labels"] = {"d": {c: round(float(np.mean([n["d"][c] for n in noise])), 3) for c in CLASSES},
                                  "auc": {c: round(float(np.mean([n["auc"][c] for n in noise])), 3) for c in CLASSES}}

        # Best layer per class by held-out d.
        m = json.load(open(f"results/sentiment/steering/sv01_{g}/metrics.json", encoding="utf-8"))
        inner = [j for j, l in enumerate(m["layers"]) if 0 < l < m["layers"][-1]]
        res["best_layer_by_d"] = {c: {"layer": m["layers"][max(inner, key=lambda j: m["d"][c][j])],
                                      "d": max(m["d"][c][j] for j in inner),
                                      "d_at_chosen": m["d"][c][m["layers"].index(layer)]} for c in CLASSES}

        # Surface features: share per class, and correlation with each projection.
        F = {n: np.array([fn(t) for t in texts], dtype=float) for n, fn in FEATURES.items()}
        F["n_words"] = np.array([len(t.split()) for t in texts], dtype=float)
        F["is_msa"] = (dia == "msa").astype(float)
        mu = X.mean(0)
        P = {c: ((X - mu) @ V[c][layer]).numpy() for c in CLASSES}
        res["feature_by_class"] = {n: {c: round(float(v[y == c].mean()), 3) for c in CLASSES} for n, v in F.items()}
        res["corr_all"] = {c: {n: round(r(P[c], v), 3) for n, v in F.items()} for c in CLASSES}
        res["corr_within_class"] = {c: {n: round(r(P[c][y == c], v[y == c]), 3) for n, v in F.items()} for c in CLASSES}

        # Stability: two random halves of the tweets, built the same way.
        cos = {c: [] for c in CLASSES}
        for s in range(args.splits):
            perm = np.random.default_rng(100 + s).permutation(len(y))
            h1, h2 = perm[:len(y) // 2], perm[len(y) // 2:]
            for c in CLASSES:
                a = ovr_vector(X, y, dia, h1, c, varieties, min_n, "per_dialect")
                b = ovr_vector(X, y, dia, h2, c, varieties, min_n, "per_dialect")
                cos[c].append(float(unit(a) @ unit(b)))
        res["split_half_cosine"] = {c: [round(float(np.mean(v)), 3), round(float(np.min(v)), 3)] for c, v in cos.items()}

        # Sarcasm: unseen by the vectors, compared inside NEG.
        Ps = {c: ((X_all - mu) @ V[c][layer]).numpy() for c in CLASSES}
        neg_s, neg_n = (y_all == "NEG") & sarc, (y_all == "NEG") & ~sarc
        res["sarcasm_inside_neg_d"] = {c: round(cohens_d(Ps[c][neg_s], Ps[c][neg_n]), 3) for c in CLASSES}
        res["sarcastic_neg_n"] = int(neg_s.sum())

        # Tweets at both ends of each direction, for reading.
        with open(f"data/inspect/steering/sv01_{g}_direction_ends.csv", "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f)
            w.writerow(["direction", "end", "rank", "projection", "gold", "dialect", "text"])
            for c in CLASSES:
                order = np.argsort(-P[c])
                for end, ids in (("high", order[:args.ends]), ("low", order[::-1][:args.ends])):
                    for k, j in enumerate(ids, 1):
                        w.writerow([c, end, k, round(float(P[c][j]), 2), y[j], dia[j], texts[j]])
        out["generators"][g] = res
        print(f"{g}: done, {time.time() - t0:.0f}s", flush=True)

    out["seconds"] = round(time.time() - t0)
    out["finished"] = time.strftime("%Y-%m-%d %H:%M")
    with open("results/sentiment/steering/sv01_explore.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main())
