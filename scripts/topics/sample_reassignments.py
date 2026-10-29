"""Review file: what moves where if each text of an unnamed cluster goes to its nearest named cluster centre.

For each unnamed cluster, texts are reassigned to the nearest named centroid; for each destination topic
(largest first) a seeded random sample of moved texts is listed, with its target cluster and similarities.
Output (gitignored, quotes texts): data/topics/<name>/reassignment_review.md

Usage:
  python scripts/topics/sample_reassignments.py --names configs/quality/topic_names_universal_clean_k50.json
  python scripts/topics/sample_reassignments.py --names ... --per-topic 3 --topics 2   (tiny mode)
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--names", required=True)
    p.add_argument("--per-topic", type=int, default=6, help="sample texts per destination topic")
    p.add_argument("--topics", type=int, default=4, help="destination topics listed per unnamed cluster")
    p.add_argument("--seed", type=int, default=0)
    args = p.parse_args()

    names = json.loads(Path(args.names).read_text(encoding="utf-8"))
    src = Path("data/topics") / names["topic_list"]
    C = np.load(src / "centroids.npy")
    X = np.load(src / "embeddings.npy", mmap_mode="r")
    rows = [json.loads(l) for l in open(src / "assignments.jsonl", encoding="utf-8")]
    lab = np.array([r["cluster"] for r in rows])
    topic = {c: t for t, cs in names["topics"].items() for c in cs}
    named = sorted(topic)

    # Pick the sample first, so only the needed texts are read from the pool.
    rng = np.random.default_rng(args.seed)
    picks: dict[int, list[tuple[str, list[tuple[int, int, float, float]]]]] = {}
    need: set[str] = set()
    for c_str in names["not_named"]:
        c = int(c_str)
        idx = np.flatnonzero(lab == c)
        Xi = np.asarray(X[idx])
        Sn = Xi @ C[named].T
        best = Sn.argmax(1)
        own = Xi @ C[c]
        dest = np.array([topic[named[b]] for b in best])
        picks[c] = []
        for t, n in Counter(dest.tolist()).most_common(args.topics):
            sel = np.flatnonzero(dest == t)
            sel = rng.choice(sel, min(args.per_topic, len(sel)), replace=False)
            items = [(int(idx[i]), named[best[i]], float(Sn[i, best[i]]), float(own[i])) for i in sel]
            need.update(rows[i]["text_id"] for i, *_ in items)
            picks[c].append((f"{t}: {n:,} of {len(idx):,} texts ({n / len(idx):.0%})", items))

    # Texts come from the pool named in the topic list's meta.
    data = json.loads((src / "meta.json").read_text(encoding="utf-8"))["config"]["data"]
    text = {}
    with open(data, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r["text_id"] in need:
                text[r["text_id"]] = (r["text"], r.get("dataset", ""))

    out = [f"# Reassignment review: {names['topic_list']}", "",
           "Each text of an unnamed cluster moved to its nearest named cluster centre. Random sample per destination "
           f"topic (seed {args.seed}). `to` = destination similarity, `own` = similarity to its current centre "
           "(own is higher for almost every text). Mark each text: fits / does not fit.", ""]
    for c_str, why in names["not_named"].items():
        out += [f"## C{c_str}: {why}", ""]
        for head, items in picks[int(c_str)]:
            out += [f"### → {head}", ""]
            for i, tgt, s_to, s_own in items:
                t, ds = text[rows[i]["text_id"]]
                out.append(f"- [C{tgt}, to {s_to:.3f}, own {s_own:.3f}, {ds}] {' '.join(t.split())[:220]}")
            out.append("")
    path = src / "reassignment_review.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"written to {path}")


if __name__ == "__main__":
    main()
