"""How close are the clusters of a frozen E5 topic list, and why? Writes tables and a 2D layout for the HTML view.

Inputs: a fitted topic list (data/topics/<name>/: centroids, embeddings, assignments) and a names config
(configs/quality/topic_names_<name>.json). Reads only; the frozen files are never changed.
Outputs, in results/quality/topics/<name>/:
  analysis.json   centroid similarities, tree (average linkage), nearest clusters, drivers, unnamed-cluster checks
  layout.json     t-SNE of a sample of texts (2D), for the plot
  console log     summary numbers

Usage:
  python scripts/topics/analyze_topic_clusters.py --names configs/quality/topic_names_universal_clean_k50.json
  python scripts/topics/analyze_topic_clusters.py --names ... --per-cluster 20   (tiny mode)
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
from scipy.spatial.distance import jensenshannon, squareform


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--names", required=True)
    p.add_argument("--per-cluster", type=int, default=200, help="texts per cluster in the t-SNE sample")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    names = json.loads(Path(args.names).read_text(encoding="utf-8"))
    tl = names["topic_list"]
    src = Path("data/topics") / tl
    out = Path("results/quality/topics") / (tl + (f"_sample{args.per_cluster}" if args.per_cluster != 200 else ""))
    out.mkdir(parents=True, exist_ok=True)

    C = np.load(src / "centroids.npy")
    X = np.load(src / "embeddings.npy", mmap_mode="r")
    rows = [json.loads(l) for l in open(src / "assignments.jsonl", encoding="utf-8")]
    lab = np.array([r["cluster"] for r in rows])
    k = len(C)
    topic = {c: t for t, cs in names["topics"].items() for c in cs}
    topic.update({int(c): "Not named" for c in names["not_named"]})
    assert sorted(topic) == list(range(k)), "every cluster needs a topic or a not-named entry"

    # Cluster profiles: size, mean words is not stored, so dataset mix (from text_id prefix) and mean sim.
    ds = [r["text_id"].split(":", 1)[0] for r in rows]
    datasets = sorted(set(ds))
    mix = np.zeros((k, len(datasets)))
    for c, d in zip(lab, ds):
        mix[c, datasets.index(d)] += 1
    sizes = mix.sum(1)
    mix /= sizes[:, None]

    # 1. Centroid cosine similarity and an average-linkage tree on 1 - cosine.
    S = C @ C.T
    D = np.clip(1 - S, 0, None)
    np.fill_diagonal(D, 0)
    Z = linkage(squareform(D, checks=False), method="average")
    dn = dendrogram(Z, no_plot=True)
    order = [int(i) for i in dn["leaves"]]

    # 2. Are clusters of the same topic closer than clusters of different topics?
    iu = np.triu_indices(k, 1)
    same = [S[i, j] for i, j in zip(*iu) if topic[i] == topic[j] and topic[i] != "Not named"]
    diff = [S[i, j] for i, j in zip(*iu) if topic[i] != topic[j]]
    # Rank of the nearest same-topic cluster among all others (1 = it is the nearest).
    ranks = {}
    for c in range(k):
        if topic[c] == "Not named" or len(names["topics"][topic[c]]) < 2:
            continue
        nn = [j for j in np.argsort(-S[c]) if j != c]
        ranks[c] = next(r for r, j in enumerate(nn, 1) if topic[j] == topic[c])

    # 3. Why are clusters close? Correlate centroid similarity with dataset-mix similarity (1 - JS distance).
    mixsim = np.array([1 - jensenshannon(mix[i], mix[j], base=2) for i, j in zip(*iu)])
    r_mix = float(np.corrcoef(S[iu], mixsim)[0, 1])

    # 4. Unnamed clusters: nearest named clusters (centroids) and where their texts would go.
    named = [c for c in range(k) if topic[c] != "Not named"]
    unnamed = {}
    rng = np.random.default_rng(args.seed)
    for c_str, why in names["not_named"].items():
        c = int(c_str)
        nn = sorted(named, key=lambda j: -S[c, j])[:3]
        idx = np.flatnonzero(lab == c)
        Xi = np.asarray(X[idx])
        own = Xi @ C[c]
        Sn = Xi @ C[named].T
        best = Sn.argmax(1)
        to = Counter(topic[named[b]] for b in best)
        unnamed[c] = {"why": why, "size": int(sizes[c]),
                      "nearest_named": [{"cluster": int(j), "topic": topic[j], "sim": round(float(S[c, j]), 3)} for j in nn],
                      "texts_to_topic": {t: round(n / len(idx), 3) for t, n in to.most_common(5)},
                      "mean_sim_own": round(float(own.mean()), 3), "mean_sim_best_named": round(float(Sn.max(1).mean()), 3),
                      "share_closer_to_named_than_own": round(float((Sn.max(1) > own).mean()), 3)}

    # 5. 2D map: t-SNE of a sample of texts (same number per cluster), plus centroid positions as sample means.
    from sklearn.manifold import TSNE
    samp = np.concatenate([rng.choice(np.flatnonzero(lab == c), min(args.per_cluster, int(sizes[c])), replace=False)
                           for c in range(k)])
    samp.sort()
    Y = TSNE(n_components=2, metric="cosine", init="pca", perplexity=40, random_state=args.seed).fit_transform(np.asarray(X[samp]))
    pts = [{"x": round(float(y[0]), 2), "y": round(float(y[1]), 2), "c": int(lab[i])} for y, i in zip(Y, samp)]

    clusters = [{"cluster": c, "topic": topic[c], "size": int(sizes[c]),
                 "top_datasets": [[datasets[j], round(float(mix[c, j]), 3)] for j in np.argsort(-mix[c])[:3]],
                 "nearest": [[int(j), round(float(S[c, j]), 3)] for j in np.argsort(-S[c]) if j != c][:3]}
                for c in range(k)]
    analysis = {"topic_list": tl, "names_config": args.names, "k": k, "order": order,
                "similarity": np.round(S, 3).tolist(),
                "dendrogram": {"icoord": dn["icoord"], "dcoord": dn["dcoord"]},
                "same_topic_sim": {"n": len(same), "mean": round(float(np.mean(same)), 3)},
                "different_topic_sim": {"n": len(diff), "mean": round(float(np.mean(diff)), 3)},
                "nearest_same_topic_rank": {str(c): r for c, r in ranks.items()},
                "corr_centroid_sim_vs_dataset_mix_sim": round(r_mix, 3),
                "clusters": clusters, "unnamed": {str(c): v for c, v in unnamed.items()}}
    (out / "analysis.json").write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    (out / "layout.json").write_text(json.dumps({"seed": args.seed, "per_cluster": args.per_cluster, "points": pts}),
                                     encoding="utf-8")

    print(f"same-topic centroid sim {np.mean(same):.3f} (n={len(same)}) vs different-topic {np.mean(diff):.3f} (n={len(diff)})")
    print(f"nearest same-topic cluster is the nearest overall for {sum(r == 1 for r in ranks.values())} of {len(ranks)} clusters; "
          f"ranks {sorted(ranks.values())}")
    print(f"correlation of centroid similarity with dataset-mix similarity: r = {r_mix:.3f}")
    for c, v in unnamed.items():
        print(f"C{c} ({v['why']}): nearest named {[(n['cluster'], n['topic'], n['sim']) for n in v['nearest_named']]}; "
              f"own {v['mean_sim_own']} vs best named {v['mean_sim_best_named']}; closer to named: "
              f"{v['share_closer_to_named_than_own']:.0%}; texts -> {v['texts_to_topic']}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
