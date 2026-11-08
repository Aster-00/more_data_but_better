"""Does the SV01 NEU direction depend on links? Vectors with and without link tweets (CPU, S1 train only).

Usage: python -m src.sentiment.steering.link_check
Output: results/sentiment/steering/sv01_links.json
"""
import json, sys
import numpy as np, torch
from sklearn.metrics import roc_auc_score
from src.sentiment.steering.analyze_generated import CLASSES, ovr_vector, unit
from src.sentiment.steering.explore_real import folds_of
out = {}
for g, L in (("fanar", 32), ("qwen3", 32), ("aya", 22)):
    cfg = json.load(open(f"configs/sentiment/steering/sv01_{g}.json", encoding="utf-8"))
    tv = torch.load(f"data/steering/sv01_{g}/text_vectors.pt", weights_only=False)
    txt = {x["text_id"]: x["text"] for x in map(json.loads, open(cfg["train_data"], encoding="utf-8"))}
    i = list(tv["layers"]).index(L)
    keep = np.where(~np.array(tv["sarcasm"]))[0]
    X = tv["vectors"][keep, i].float()
    y = np.array(tv["sentiment"])[keep]; d = np.array(tv["dialect"])[keep]
    link = np.array(["URL" in txt[tv["text_id"][j]] for j in keep])
    V = cfg["varieties"]; m = 30
    idx = np.arange(len(y)); nl = idx[~link]
    res = {"n_nolink": {c: int(((y == c) & ~link).sum()) for c in CLASSES}}
    vall = {c: unit(ovr_vector(X, y, d, idx, c, V, m, "per_dialect")) for c in CLASSES}
    vno = {c: unit(ovr_vector(X, y, d, nl, c, V, m, "per_dialect")) for c in CLASSES}
    res["cos_all_vs_nolink"] = {c: round(float(vall[c] @ vno[c]), 3) for c in CLASSES}
    # Link direction: link minus no link inside each class and variety, equal weights.
    diffs = [X[(y == c) & (d == v) & link].mean(0) - X[(y == c) & (d == v) & ~link].mean(0) for c in CLASSES for v in V
             if ((y == c) & (d == v) & link).sum() >= m and ((y == c) & (d == v) & ~link).sum() >= m]
    lk = unit(sum(diffs))
    res["cos_with_link_direction"] = {c: round(float(vall[c] @ lk), 3) for c in CLASSES}
    res["cos_nolink_vec_with_link_direction"] = {c: round(float(vno[c] @ lk), 3) for c in CLASSES}
    # Held-out AUC: all-tweet vectors, scored on no-link tweets only, and no-link vectors on no-link tweets.
    fold = folds_of(len(y), 5, cfg["seed"]); a = {c: np.zeros(len(y)) for c in CLASSES}; b = {c: np.zeros(len(y)) for c in CLASSES}
    for f in range(5):
        tr, te = idx[fold != f], idx[fold == f]; trn = tr[~link[tr]]; mu = X[tr].mean(0)
        for c in CLASSES:
            a[c][te] = ((X[te] - mu) @ unit(ovr_vector(X, y, d, tr, c, V, m, "per_dialect"))).numpy()
            b[c][te] = ((X[te] - mu) @ unit(ovr_vector(X, y, d, trn, c, V, m, "per_dialect"))).numpy()
    res["auc_on_nolink_all_vec"] = {c: round(float(roc_auc_score(y[nl] == c, a[c][nl])), 3) for c in CLASSES}
    res["auc_on_nolink_nolink_vec"] = {c: round(float(roc_auc_score(y[nl] == c, b[c][nl])), 3) for c in CLASSES}
    res["auc_on_link_all_vec"] = {c: round(float(roc_auc_score(y[link] == c, a[c][link])), 3) for c in CLASSES}
    out[g] = res; print(g, json.dumps(res), flush=True)
json.dump(out, open("results/sentiment/steering/sv01_links.json", "w", encoding="utf-8"), indent=1)
