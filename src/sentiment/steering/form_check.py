"""Do the SV01 class directions still separate classes when tweet form is held fixed? (CPU)

Held-out projections as in `explore_real` (5 folds, S1 train, non-sarcastic tweets, one layer per
generator). AUC of each class against the rest is then computed inside strata, comparing only tweets
of the same form, and averaged weighted by stratum size:

  length       3 bands (up to 8 words, 9-16, 17 or more; bands hand-set)
  link         with or without a link
  topic        universal topic cluster (k = 50, D-018); tweets under 5 words after cleaning have none
  all three    length x link x topic

A stratum counts only with at least `--min-side` tweets on both sides. If the AUC stays well above 0.5
under a control, the direction is not explained by that form. Output: results/sentiment/steering/sv01_form_check.json

Usage:
  python -m src.sentiment.steering.form_check --layers fanar=32 qwen3=32 aya=22
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import numpy as np
import torch
from sklearn.metrics import roc_auc_score

from src.data.build_dataset import git_commit
from src.sentiment.steering.analyze_generated import CLASSES, ovr_vector, unit
from src.sentiment.steering.explore_real import folds_of


def topic_of_tweets(train_file: str) -> dict:
    """text_id -> topic cluster, through the row index in the universal topic assignments."""
    with open(train_file, encoding="utf-8") as f:
        ids = [json.loads(line)["text_id"] for line in f]
    out = {}
    prefix = "ArSarcasm-v2:arsarcasm_v2_train.jsonl:"
    with open("data/topics/universal_clean_k50_seed0/assignments.jsonl", encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["text_id"].startswith(prefix):
                out[ids[int(r["text_id"][len(prefix):])]] = r["cluster"]
    return out


def strat_auc(target: np.ndarray, score: np.ndarray, strata: np.ndarray, min_side: int) -> dict:
    """AUC inside each stratum, weighted by stratum size; with the share of tweets covered."""
    total, weight = 0.0, 0
    for s in np.unique(strata):
        m = strata == s
        if target[m].sum() >= min_side and (~target[m]).sum() >= min_side:
            total += roc_auc_score(target[m], score[m]) * m.sum()
            weight += int(m.sum())
    return {"auc": round(total / weight, 3) if weight else None, "covered": round(weight / len(target), 3)}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--layers", nargs="+", required=True, help="generator=layer")
    p.add_argument("--min-side", type=int, default=5)
    p.add_argument("--folds", type=int, default=5)
    args = p.parse_args()
    t0, out = time.time(), {"git_commit": git_commit(), "min_side": args.min_side, "generators": {}}

    for item in args.layers:
        g, layer = item.split("=")
        layer = int(layer)
        with open(f"configs/sentiment/steering/sv01_{g}.json", encoding="utf-8") as f:
            cfg = json.load(f)
        tv = torch.load(f"data/steering/sv01_{g}/text_vectors.pt", weights_only=False)
        with open(cfg["train_data"], encoding="utf-8") as f:
            text_of = {x["text_id"]: x["text"] for x in map(json.loads, f)}
        topic_of = topic_of_tweets(cfg["train_data"])
        keep = np.where(~np.array(tv["sarcasm"]))[0]
        i = list(tv["layers"]).index(layer)
        X = tv["vectors"][keep, i].float()
        y, dia = np.array(tv["sentiment"])[keep], np.array(tv["dialect"])[keep]
        ids = [tv["text_id"][j] for j in keep]
        texts = [text_of[t] for t in ids]

        # Held-out projection of every tweet on each class vector.
        fold = folds_of(len(y), args.folds, cfg["seed"])
        P = {c: np.zeros(len(y)) for c in CLASSES}
        for f in range(args.folds):
            tr, te = np.where(fold != f)[0], np.where(fold == f)[0]
            mu = X[tr].mean(0)
            for c in CLASSES:
                v = unit(ovr_vector(X, y, dia, tr, c, cfg["varieties"], cfg["min_group_size"], "per_dialect"))
                P[c][te] = ((X[te] - mu) @ v).numpy()

        # Form strata; tweets without a topic get -1 and stay out of the topic strata.
        words = np.array([len(t.split()) for t in texts])
        band = np.digitize(words, [9, 17])
        link = np.array(["URL" in t for t in texts]).astype(int)
        topic = np.array([topic_of.get(t, -1) for t in ids])
        has_topic = topic >= 0
        res: dict = {"layer": layer, "tweets_with_topic": round(float(has_topic.mean()), 3), "classes": {}}
        for c in CLASSES:
            t, s = y == c, P[c]
            res["classes"][c] = {
                "none": round(float(roc_auc_score(t, s)), 3),
                "length": strat_auc(t, s, band, args.min_side),
                "link": strat_auc(t, s, link, args.min_side),
                "length_link": strat_auc(t, s, band * 2 + link, args.min_side),
                "topic": strat_auc(t[has_topic], s[has_topic], topic[has_topic], args.min_side),
                "all_three": strat_auc(t[has_topic], s[has_topic],
                                       topic[has_topic] * 10 + band[has_topic] * 2 + link[has_topic], args.min_side)}
        out["generators"][g] = res
        print(g, json.dumps(res, ensure_ascii=False), flush=True)

    out["seconds"], out["finished"] = round(time.time() - t0), time.strftime("%Y-%m-%d %H:%M")
    with open("results/sentiment/steering/sv01_form_check.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    sys.exit(main())
