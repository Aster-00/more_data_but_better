"""Class directions, layer choice and class-specific neurons from SV02 activations (CPU step).

Reads what `activations_generated` saved (no model is loaded; deterministic, CPU only) and builds:

  class vectors  DiffMean, one class against the other two (pos, neg, neu), per layer; per_dialect
                 (difference inside each variety, equal-weight average, as SV01) and pooled
  pair vectors   mean of (B - A) over the minimal pairs of each pair type, per layer; the topic is
                 shared inside a pair, so it cancels
  layer choice   5-fold cross-validation grouped by pair_id (the two sides of a pair are never split):
                 DiffMean probe (argmax of the projections on the three train-fold class vectors),
                 logistic regression on PCA features, held-out Cohen's d along each class vector, and
                 pair-flip accuracy ((B - A) . v_pair > 0 on held-out pairs)
  neurons        LAPE (Tang et al., ACL 2024) over the three classes and over the four varieties:
                 firing probability per group, kept if its maximum is above the configured quantile,
                 then the lowest-entropy share of all neurons; plus the top neurons per class by a
                 token-level effect size of the down_proj input
Every vector is L2-normalised per layer. Layer 0 = embeddings, l = output of decoder layer l-1.

Outputs: vectors.pt in output_dir (same layout as SV01's, for the steering hooks); metrics.json,
report.md and figures (*.png) in report_dir.

Usage:
  python -m src.sentiment.steering.analyze_generated --config configs/sentiment/steering/sv02_sg04_fanar.json
  python -m src.sentiment.steering.analyze_generated --config configs/sentiment/steering/sv02_sg04_fanar.json --limit 48
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score

from src.data.build_dataset import git_commit

CLASSES = ("NEG", "NEU", "POS")


def unit(v: torch.Tensor) -> torch.Tensor:
    """L2-normalise the last dimension."""
    return v / v.norm(dim=-1, keepdim=True).clamp(min=1e-12)


def ovr_vector(X: torch.Tensor, y: np.ndarray, dia: np.ndarray, idx: np.ndarray, cls: str,
               varieties: list[str], min_n: int, mode: str) -> torch.Tensor | None:
    """Raw DiffMean of `cls` against the rest over rows `idx`, [L+1, H]; None if a side is empty."""
    if mode == "pooled":
        t, c = idx[y[idx] == cls], idx[y[idx] != cls]
        return X[t].mean(0) - X[c].mean(0) if len(t) and len(c) else None
    # per_dialect: the difference inside each variety large enough on both sides, equal weights.
    diffs = []
    for d in varieties:
        t = idx[(y[idx] == cls) & (dia[idx] == d)]
        c = idx[(y[idx] != cls) & (dia[idx] == d)]
        if len(t) >= min_n and len(c) >= min_n:
            diffs.append(X[t].mean(0) - X[c].mean(0))
    return sum(diffs) / len(diffs) if diffs else None


def pair_vector(X: torch.Tensor, pairs: dict, dia: dict, pids: list[str], varieties: list[str],
                min_n: int, mode: str) -> torch.Tensor | None:
    """Raw mean of (B - A) over the pairs `pids`, [L+1, H]; per_dialect averages varieties equally."""
    if not pids:
        return None
    diff = lambda ps: (X[[pairs[p]["B"] for p in ps]] - X[[pairs[p]["A"] for p in ps]]).mean(0)
    if mode == "pooled":
        return diff(pids)
    groups = [[p for p in pids if dia[p] == d] for d in varieties]
    groups = [g for g in groups if len(g) >= min_n]
    return sum(diff(g) for g in groups) / len(groups) if groups else diff(pids)


def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    """Standardised mean difference with the pooled standard deviation."""
    if len(a) < 2 or len(b) < 2:
        return float("nan")
    s = math.sqrt(((len(a) - 1) * a.var(ddof=1) + (len(b) - 1) * b.var(ddof=1)) / (len(a) + len(b) - 2))
    return float((a.mean() - b.mean()) / max(s, 1e-12))


def cross_validate(X, y, dia, pairs, pair_dia, pair_type, cfg) -> dict:
    """Per-layer held-out probe F1, Cohen's d per class vector and pair-flip accuracy (grouped folds)."""
    n_layers = X.shape[1]
    # Every pair_id gets a fold, incomplete ones too (tiny mode), so both sides stay together.
    pids = sorted(set(cfg["_row_pair"]))
    random.Random(cfg["seed"]).shuffle(pids)
    fold_of = {p: i % cfg["folds"] for i, p in enumerate(pids)}
    row_fold = np.array([fold_of[pid] for pid in cfg["_row_pair"]])
    types = sorted(set(pair_type.values()))
    out = {"diffmean_f1": np.zeros((cfg["folds"], n_layers)), "lr_f1": np.zeros((cfg["folds"], n_layers)),
           "d": {c: np.zeros((cfg["folds"], n_layers)) for c in CLASSES},
           "flip": {t: np.zeros((cfg["folds"], n_layers)) for t in types}}
    min_n = cfg["min_group_size"]
    for f in range(cfg["folds"]):
        tr, te = np.where(row_fold != f)[0], np.where(row_fold == f)[0]
        vecs = {c: ovr_vector(X, y, dia, tr, c, cfg["varieties"], min_n, "per_dialect") for c in CLASSES}
        # Fold vectors fall back to pooled when a variety is too small (tiny mode).
        vecs = {c: unit(v if v is not None else ovr_vector(X, y, dia, tr, c, cfg["varieties"], 1, "pooled"))
                for c, v in vecs.items()}
        mu = X[tr].mean(0)                                             # [L+1, H]
        proj = {c: ((X[te] - mu) * vecs[c]).sum(-1).numpy() for c in CLASSES}   # [n_te, L+1]
        scores = np.stack([proj[c] for c in CLASSES], -1)             # [n_te, L+1, 3]
        for layer in range(n_layers):
            pred = np.array(CLASSES)[scores[:, layer].argmax(-1)]
            out["diffmean_f1"][f, layer] = f1_score(y[te], pred, average="macro", labels=list(CLASSES))
            for c in CLASSES:
                out["d"][c][f, layer] = cohens_d(proj[c][y[te] == c, layer], proj[c][y[te] != c, layer])
            # Logistic regression on PCA features fitted on the train fold only.
            k = min(cfg["pca_dims"], len(tr) - 1, X.shape[2])
            pca = PCA(n_components=k, random_state=cfg["seed"]).fit(X[tr, layer].numpy())
            ztr, zte = pca.transform(X[tr, layer].numpy()), pca.transform(X[te, layer].numpy())
            sd = ztr.std(0) + 1e-6
            lr = LogisticRegression(max_iter=2000, random_state=cfg["seed"]).fit(ztr / sd, y[tr])
            out["lr_f1"][f, layer] = f1_score(y[te], lr.predict(zte / sd), average="macro", labels=list(CLASSES))
        # Pair flip: vector from train-fold pairs of the type, tested on held-out pairs of the type.
        for t in types:
            ptr = [p for p in pairs if pair_type[p] == t and fold_of[p] != f]
            pte = [p for p in pairs if pair_type[p] == t and fold_of[p] == f]
            v = pair_vector(X, pairs, pair_dia, ptr, cfg["varieties"], min_n, "per_dialect")
            if v is None or not pte:
                out["flip"][t][f] = np.nan
                continue
            dif = X[[pairs[p]["B"] for p in pte]] - X[[pairs[p]["A"] for p in pte]]
            out["flip"][t][f] = ((dif * unit(v)).sum(-1) > 0).float().mean(0).numpy()
        print(f"  fold {f + 1}/{cfg['folds']} done", flush=True)
    return out


def lape(p: torch.Tensor, quantile: float, top_share: float) -> tuple[torch.Tensor, torch.Tensor, float]:
    """LAPE selection over groups. p: [G, L, I] firing probabilities.

    Return a [L, I] bool mask of selected neurons, a [G, L, I] bool mask of the groups each selected
    neuron belongs to (p above the threshold), and the threshold.
    """
    thr = float(torch.quantile(p.flatten().float()[torch.randperm(p.numel(), generator=torch.Generator().manual_seed(0))[:2_000_000]], quantile))
    q = p / p.sum(0, keepdim=True).clamp(min=1e-12)
    ent = -(q * q.clamp(min=1e-12).log()).sum(0)                     # [L, I]
    ent = torch.where(p.max(0).values >= thr, ent, torch.full_like(ent, float("inf")))
    k = int(top_share * ent.numel())
    sel = torch.zeros_like(ent, dtype=torch.bool)
    if k:
        flat = ent.flatten()
        cand = torch.topk(flat, k, largest=False).indices
        cand = cand[torch.isfinite(flat[cand])]
        sel.view(-1)[cand] = True
    return sel, (p >= thr) & sel[None], thr


def neuron_tables(ns: dict, type_role_class: dict, cfg: dict) -> dict:
    """Firing, mean and token variance per class and per variety (equal-weight); LAPE and top neurons."""
    sums, counts = ns["sums"], ns["counts"]
    min_n = cfg["min_group_size"]

    def agg(match) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, int]:
        keys = [k for k in sums if match(k)]
        n = sum(counts[k] for k in keys)
        f = sum(sums[k]["fire"] for k in keys) / n
        m = sum(sums[k]["mean"] for k in keys) / n
        v = (sum(sums[k]["sq"] for k in keys) / n - m.square()).clamp(min=0)
        return f, m, v, n

    def cls_of(k):
        t, r, _ = k.split("|")
        return type_role_class[(t, r)]

    def by_class(c, rest=False):
        # Equal weight per variety (as the per_dialect vectors), over varieties large enough.
        parts = []
        for d in cfg["varieties"]:
            match = lambda k, d=d: k.split("|")[2] == d and ((cls_of(k) != c) if rest else (cls_of(k) == c))
            if sum(counts[k] for k in sums if match(k)) >= min_n:
                parts.append(agg(match))
        if not parts:
            parts = [agg(lambda k: (cls_of(k) != c) if rest else (cls_of(k) == c))]
        return tuple(sum(p[i] for p in parts) / len(parts) for i in range(3))

    cls = {c: by_class(c) for c in CLASSES}
    rest = {c: by_class(c, rest=True) for c in CLASSES}
    out = {"class_fire": torch.stack([cls[c][0] for c in CLASSES])}
    sel, member, thr = lape(out["class_fire"], cfg["lape_prob_quantile"], cfg["lape_top_entropy"])
    out["class_lape"] = {"selected": sel, "member": member, "threshold": thr}

    # Varieties: all classes together, equal weight per class.
    dia_fire = []
    for d in cfg["varieties"]:
        parts = [agg(lambda k, d=d, c=c: k.split("|")[2] == d and cls_of(k) == c) for c in CLASSES
                 if any(k.split("|")[2] == d and cls_of(k) == c for k in sums)]
        dia_fire.append(sum(p[0] for p in parts) / len(parts))
    out["dialect_fire"] = torch.stack(dia_fire)
    sel, member, thr = lape(out["dialect_fire"], cfg["lape_prob_quantile"], cfg["lape_top_entropy"])
    out["dialect_lape"] = {"selected": sel, "member": member, "threshold": thr}

    # Top neurons per class by a token-level effect size of the down_proj input (class vs rest).
    top = {}
    for c in CLASSES:
        f1, m1, v1 = cls[c]
        f0, m0, v0 = rest[c]
        d = (m1 - m0) / (0.5 * (v1 + v0)).sqrt().clamp(min=1e-6)
        idx = torch.topk(d.flatten(), cfg["top_neurons"]).indices
        n_int = d.shape[1]
        top[c] = [{"layer": int(i // n_int), "neuron": int(i % n_int), "effect": round(float(d.flatten()[i]), 3),
                   "fire_class": round(float(f1.flatten()[i]), 3), "fire_rest": round(float(f0.flatten()[i]), 3),
                   "mean_class": round(float(m1.flatten()[i]), 4), "mean_rest": round(float(m0.flatten()[i]), 4)}
                  for i in idx]
    out["top"] = top

    # Pair types: firing of side B minus side A (pooled over varieties).
    pair_top = {}
    for t in sorted({k.split("|")[0] for k in sums}):
        fa = agg(lambda k, t=t: k.split("|")[:2] == [t, "A"])[0]
        fb = agg(lambda k, t=t: k.split("|")[:2] == [t, "B"])[0]
        diff = (fb - fa).flatten()
        n_int = fa.shape[1]
        idx = torch.topk(diff.abs(), 10).indices
        pair_top[t] = [{"layer": int(i // n_int), "neuron": int(i % n_int), "fire_B_minus_A": round(float(diff[i]), 3)}
                       for i in idx]
    out["pair_top"] = pair_top
    return out


def figures(rep: Path, cv: dict, cos: dict, names: list[str], best: int, X, y, nt: dict, cfg: dict) -> None:
    """Write the six analysis figures into the report folder."""
    layers = np.arange(cv["diffmean_f1"].shape[1])
    run = cfg["run_name"]

    # 1. Probe macro F1 per layer.
    fig, ax = plt.subplots(figsize=(8, 4))
    for key, lab in (("diffmean_f1", "DiffMean probe"), ("lr_f1", f"LogReg on PCA-{cfg['pca_dims']}")):
        m, s = cv[key].mean(0), cv[key].std(0)
        ax.plot(layers, m, label=lab)
        ax.fill_between(layers, m - s, m + s, alpha=0.2)
    ax.axvline(best, ls="--", c="grey", lw=1, label=f"chosen layer {best}")
    ax.set(xlabel="layer (0 = embeddings)", ylabel="held-out macro F1", title=f"{run}: class probe by layer")
    ax.legend()
    fig.tight_layout(); fig.savefig(rep / "probe_by_layer.png", dpi=130); plt.close(fig)

    # 2. Separation along the class vectors and pair-flip accuracy.
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    for c in CLASSES:
        axs[0].plot(layers, np.nanmean(cv["d"][c], 0), label=f"v_{c.lower()}")
    axs[0].set(xlabel="layer", ylabel="held-out Cohen's d (class vs rest)", title="separation along class vectors")
    for t, v in cv["flip"].items():
        axs[1].plot(layers, np.nanmean(v, 0), label=t)
    axs[1].axhline(0.5, c="grey", lw=1)
    axs[1].set(xlabel="layer", ylabel="share of held-out pairs with (B-A).v > 0", title="pair-flip accuracy")
    for a in axs:
        a.axvline(best, ls="--", c="grey", lw=1); a.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(rep / "separation_by_layer.png", dpi=130); plt.close(fig)

    # 3. Cosine between all vectors at the chosen layer.
    M = np.array([[cos[a][b] for b in names] for a in names])
    fig, ax = plt.subplots(figsize=(1.0 + 0.6 * len(names), 0.6 + 0.55 * len(names)))
    im = ax.imshow(M, vmin=-1, vmax=1, cmap="RdBu_r")
    ax.set_xticks(range(len(names)), names, rotation=60, ha="right", fontsize=8)
    ax.set_yticks(range(len(names)), names, fontsize=8)
    for i in range(len(names)):
        for j in range(len(names)):
            ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=6)
    fig.colorbar(im, ax=ax, shrink=0.8)
    ax.set_title(f"cosine of directions, layer {best}")
    fig.tight_layout(); fig.savefig(rep / "cosine_best_layer.png", dpi=130); plt.close(fig)

    # 4. Texts at the chosen layer, PCA of all texts.
    Z = PCA(n_components=2, random_state=cfg["seed"]).fit_transform(X[:, best].numpy())
    fig, ax = plt.subplots(figsize=(6, 5))
    for c, col in zip(CLASSES, ("tab:red", "tab:grey", "tab:green")):
        ax.scatter(Z[y == c, 0], Z[y == c, 1], s=4, alpha=0.5, c=col, label=c)
    ax.set(title=f"texts at layer {best} (PCA)", xlabel="PC1", ylabel="PC2")
    ax.legend(markerscale=4)
    fig.tight_layout(); fig.savefig(rep / "pca_best_layer.png", dpi=130); plt.close(fig)

    # 5. Class- and variety-specific (LAPE) neurons per layer.
    fig, axs = plt.subplots(1, 2, figsize=(12, 4))
    for ax, key, groups in ((axs[0], "class_lape", CLASSES), (axs[1], "dialect_lape", cfg["varieties"])):
        cnt = nt[key]["member"].sum(-1).numpy()                      # [G, L]
        bottom = np.zeros(cnt.shape[1])
        for g, row in zip(groups, cnt):
            ax.bar(np.arange(1, cnt.shape[1] + 1), row, bottom=bottom, label=g)
            bottom += row
        ax.set(xlabel="decoder layer", ylabel="neurons", title=f"LAPE-specific neurons ({key.split('_')[0]})")
        ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(rep / "lape_neurons_by_layer.png", dpi=130); plt.close(fig)

    # 6. Firing probability of the top neurons per class.
    rows = [(c, n) for c in CLASSES for n in nt["top"][c][:10]]
    F = np.array([[float(nt["class_fire"][k, n["layer"], n["neuron"]]) for k in range(3)] for _, n in rows])
    fig, ax = plt.subplots(figsize=(4.5, 0.25 * len(rows) + 1.2))
    im = ax.imshow(F, aspect="auto", cmap="viridis", vmin=0, vmax=1)
    ax.set_xticks(range(3), CLASSES)
    ax.set_yticks(range(len(rows)), [f"{c}: L{n['layer']}#{n['neuron']}" for c, n in rows], fontsize=7)
    fig.colorbar(im, ax=ax, label="firing probability")
    ax.set_title("top-10 neurons per class")
    fig.tight_layout(); fig.savefig(rep / "top_neurons_heatmap.png", dpi=130); plt.close(fig)


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="analyse the tiny-mode extraction (_limitN)")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    data_dir, rep = Path(cfg["output_dir"]), Path(cfg["report_dir"])
    if args.limit is not None:
        data_dir = data_dir.with_name(data_dir.name + f"_limit{args.limit}")
        rep = rep.with_name(rep.name + f"_limit{args.limit}")
        cfg.update(min_group_size=1, folds=2, pca_dims=8)
    rep.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    tv = torch.load(data_dir / "text_vectors.pt", weights_only=False)
    ns = torch.load(data_dir / "neuron_sums.pt", weights_only=False)
    with open(data_dir / "meta.json", encoding="utf-8") as f:
        ext_meta = json.load(f)
    X = tv["vectors"].float()                                           # [N, L+1, H]
    y, dia = np.array(tv["sentiment"]), np.array(tv["dialect"])
    print(f"{X.shape[0]} texts, {X.shape[1]} layers, hidden {X.shape[2]}", flush=True)

    # Pairs: row index of side A and side B; incomplete pairs (tiny mode) are left out of pair stats.
    pairs, pair_dia, pair_type, type_role_class = {}, {}, {}, {}
    for i, (pid, role, t, d, s) in enumerate(zip(tv["pair_id"], tv["pair_role"], tv["pair_type"], tv["dialect"], tv["sentiment"])):
        pairs.setdefault(pid, {})[role] = i
        pair_dia[pid], pair_type[pid] = d, t
        type_role_class[(t, role)] = s
    pairs = {p: v for p, v in pairs.items() if "A" in v and "B" in v}
    # Folds group rows by pair; a row of an incomplete pair is its own group.
    cfg["_row_pair"] = list(tv["pair_id"])
    labels = {t: f"{type_role_class[(t, 'A')]}->{type_role_class[(t, 'B')]}" for t in sorted(set(pair_type.values()))}

    # Full-data vectors (the ones to steer with).
    all_idx = np.arange(len(y))
    vectors, raw_norm = {}, {}
    for c in CLASSES:
        name = c.lower()
        vectors[name] = {}
        for mode in ("per_dialect", "pooled"):
            v = ovr_vector(X, y, dia, all_idx, c, cfg["varieties"], cfg["min_group_size"], mode)
            if v is not None:
                vectors[name][mode], raw_norm[f"{name}/{mode}"] = unit(v), v.norm(dim=-1)
    for t in labels:
        name = f"pair_{t}"
        vectors[name] = {}
        for mode in ("per_dialect", "pooled"):
            v = pair_vector(X, pairs, pair_dia, [p for p in pairs if pair_type[p] == t], cfg["varieties"],
                            cfg["min_group_size"], mode)
            if v is not None:
                vectors[name][mode], raw_norm[f"{name}/{mode}"] = unit(v), v.norm(dim=-1)
    e, m = X[dia == "egypt"], X[dia == "msa"]
    egy = unit(e.mean(0) - m.mean(0)) if len(e) and len(m) else None

    print("cross-validation ...", flush=True)
    cv = cross_validate(X, y, dia, pairs, pair_dia, pair_type, cfg)
    # Chosen layer: best held-out DiffMean probe, embeddings and the final (normed) layer excluded.
    dm = cv["diffmean_f1"].mean(0)
    best = int(np.argmax(dm[1:-1]) + 1)
    print(f"chosen layer {best} (DiffMean F1 {dm[best]:.3f})", flush=True)

    # Cosines at the chosen layer; per_dialect where built.
    vec_at = {n: (v.get("per_dialect", v.get("pooled")))[best] for n, v in vectors.items() if v}
    if egy is not None:
        vec_at["egypt_vs_msa"] = egy[best]
    names = list(vec_at)
    cos = {a: {b: round(float(vec_at[a] @ vec_at[b]), 3) for b in names} for a in names}
    cos_egy_by_layer = ({n: [round(float(x), 3) for x in (v.get("per_dialect", v.get("pooled")) * egy).sum(-1)]
                         for n, v in vectors.items() if v} if egy is not None else {})

    print("neurons ...", flush=True)
    nt = neuron_tables(ns, type_role_class, cfg)
    figures(rep, cv, cos, names, best, X, y, nt, cfg)

    # Example texts: highest and lowest projection on each class vector at the chosen layer.
    mu = X[:, best].mean(0)
    examples = {}
    for c in CLASSES:
        pr = ((X[:, best] - mu) @ vec_at[c.lower()]).numpy()
        order = np.argsort(-pr)
        examples[c] = {"top": [(round(float(pr[i]), 2), y[i], tv["text"][i]) for i in order[:5]],
                       "bottom": [(round(float(pr[i]), 2), y[i], tv["text"][i]) for i in order[-5:][::-1]]}

    torch.save({"vectors": vectors, "token_norm_mean": torch.tensor(ext_meta["token_norm_mean"]),
                "chosen_layer": best, "egypt_vs_msa": egy, "raw_norm": raw_norm}, data_dir / "vectors.pt")
    n_lay = nt["class_lape"]["member"].shape[1]
    metrics = {
        "run_name": cfg["run_name"], "generator": cfg["generator"], "data": cfg["data"], "n_texts": int(len(y)),
        "class_counts": {c: int((y == c).sum()) for c in CLASSES}, "n_pairs": len(pairs), "pair_labels": labels,
        "chosen_layer": best,
        "per_layer": {"diffmean_f1_mean": dm.round(4).tolist(), "diffmean_f1_sd": cv["diffmean_f1"].std(0).round(4).tolist(),
                      "lr_f1_mean": cv["lr_f1"].mean(0).round(4).tolist(), "lr_f1_sd": cv["lr_f1"].std(0).round(4).tolist(),
                      "d": {c: np.nanmean(v, 0).round(3).tolist() for c, v in cv["d"].items()},
                      "pair_flip": {t: np.nanmean(v, 0).round(4).tolist() for t, v in cv["flip"].items()}},
        "best_lr_layer": int(np.argmax(cv["lr_f1"].mean(0))),
        "raw_norm_over_token_norm_at_chosen": {k: round(float(v[best]) / ext_meta["token_norm_mean"][best], 4)
                                               for k, v in raw_norm.items()},
        "cosine_at_chosen": cos, "cos_with_egypt_vs_msa_by_layer": cos_egy_by_layer,
        "lape": {k: {"threshold": round(nt[k]["threshold"], 4), "n_selected": int(nt[k]["selected"].sum()),
                     "per_group": {g: int(nt[k]["member"][i].sum()) for i, g in
                                   enumerate(CLASSES if k == "class_lape" else cfg["varieties"])},
                     "per_group_layer": {g: nt[k]["member"][i].sum(-1).tolist() for i, g in
                                         enumerate(CLASSES if k == "class_lape" else cfg["varieties"])}}
                 for k in ("class_lape", "dialect_lape")},
        "top_neurons": nt["top"], "pair_top_neurons": nt["pair_top"], "examples": examples,
        "n_decoder_layers": n_lay, "extraction": {k: ext_meta[k] for k in ("git_commit", "finished", "seconds", "hook_check")},
        "git_commit": git_commit(), "seconds": round(time.time() - t0), "finished": time.strftime("%Y-%m-%d %H:%M"),
        "config": {k: v for k, v in cfg.items() if not k.startswith("_r")},
    }
    with open(rep / "metrics.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=1)
    write_report(rep, metrics)
    print(f"saved {data_dir / 'vectors.pt'} and {rep} ({metrics['seconds']}s)", flush=True)


def write_report(rep: Path, m: dict) -> None:
    """Markdown summary of metrics.json (generated, never hand-edited)."""
    b, pl = m["chosen_layer"], m["per_layer"]
    L = [f"# {m['run_name']}: activations of {m['generator']} on its own SG04 texts", "",
         "Generated by `src.sentiment.steering.analyze_generated`; do not edit. **Test-contaminated** (SG04 types "
         "come from test errors, D-023). Labels are the requested ones.", "",
         f"- Texts: {m['n_texts']} ({', '.join(f'{c} {n}' for c, n in m['class_counts'].items())}), {m['n_pairs']} pairs",
         f"- Chosen layer (best held-out DiffMean probe, layers 1..L-1): **{b}** of {len(pl['diffmean_f1_mean']) - 1}; "
         f"best logistic-regression layer: {m['best_lr_layer']}", "",
         "## Held-out scores by layer (every 2nd layer)", "",
         "| Layer | DiffMean F1 | LogReg F1 | d pos | d neg | d neu | " + " | ".join(f"flip {t}" for t in pl["pair_flip"]) + " |",
         "|---" * (6 + len(pl["pair_flip"])) + "|"]
    for l in range(0, len(pl["diffmean_f1_mean"]), 2):
        L.append(f"| {l}{' *' if l == b else ''} | {pl['diffmean_f1_mean'][l]:.3f} ± {pl['diffmean_f1_sd'][l]:.3f} | "
                 f"{pl['lr_f1_mean'][l]:.3f} | {pl['d']['POS'][l]:.2f} | {pl['d']['NEG'][l]:.2f} | {pl['d']['NEU'][l]:.2f} | "
                 + " | ".join(f"{v[l]:.2f}" for v in pl["pair_flip"].values()) + " |")
    L += ["", f"Pair labels (A->B): " + ", ".join(f"{t} {lab}" for t, lab in m["pair_labels"].items()), "",
          f"## Cosine of directions at layer {b}", "", "![cosine](cosine_best_layer.png)", "",
          "| | " + " | ".join(m["cosine_at_chosen"]) + " |", "|---" * (len(m["cosine_at_chosen"]) + 1) + "|"]
    for a, row in m["cosine_at_chosen"].items():
        L.append(f"| {a} | " + " | ".join(f"{v:.2f}" for v in row.values()) + " |")
    L += ["", f"Raw DiffMean norm / mean token norm at layer {b} (scale for alpha): "
          + ", ".join(f"{k} {v}" for k, v in m["raw_norm_over_token_norm_at_chosen"].items()), "",
          "## LAPE-specific neurons", ""]
    for k, v in m["lape"].items():
        L.append(f"- **{k.split('_')[0]}**: {v['n_selected']} selected (firing threshold {v['threshold']}); "
                 + ", ".join(f"{g} {n}" for g, n in v["per_group"].items()))
    L += ["", "![lape](lape_neurons_by_layer.png)", "", "## Top neurons per class (token-level effect size)", "",
          "| Class | Layer | Neuron | Effect | Fire class | Fire rest |", "|---|---|---|---|---|---|"]
    for c, rows in m["top_neurons"].items():
        for r in rows[:10]:
            L.append(f"| {c} | {r['layer']} | {r['neuron']} | {r['effect']} | {r['fire_class']} | {r['fire_rest']} |")
    L += ["", "![top neurons](top_neurons_heatmap.png)", "", f"## Texts along each class vector (layer {b})", ""]
    for c, ex in m["examples"].items():
        L.append(f"**v_{c.lower()}, highest projection**")
        L += [f"- {s} [{lab}] {t}" for s, lab, t in ex["top"]]
        L.append(f"**v_{c.lower()}, lowest projection**")
        L += [f"- {s} [{lab}] {t}" for s, lab, t in ex["bottom"]]
        L.append("")
    L += ["## Figures", "", "![probe](probe_by_layer.png)", "", "![separation](separation_by_layer.png)", "",
          "![pca](pca_best_layer.png)", ""]
    with open(rep / "report.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


if __name__ == "__main__":
    sys.exit(main())
