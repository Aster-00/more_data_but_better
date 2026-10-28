"""Topic spread of data sets against a frozen E5 topic list (quality row 5).

Every text is cleaned exactly as the topic pool was (D-015: placeholders, links and mentions
removed, hashtags to words, laughter shortened; fewer than 5 words -> not scored), embedded with
multilingual-e5-large in fp32 (as in scripts/fit_topics.py) and assigned to the nearest of the
frozen centroids (cosine; both are unit length). Nothing is refitted.

Measures per set:
  effective_clusters  exp(entropy) of the cluster shares, on 800-text samples x 10 (seeds 0-9),
                      mean and std; at most k (50 for the universal list)
  effective_named     the same over the named topics (clusters merged by name, D-019), named texts only
  unnamed_share       share of scored texts in unnamed clusters
  topic_shares        share of every named topic (and "unnamed") on the whole set
Size-dependent, so every set is scored on samples of the same size.

Outputs: <out>.json (all numbers) and <out>.md (table). No text is written.

Usage:
  python -m src.quality.topic_spread --names configs/quality/topics_universal_names.json \
      --sets real=data/processed/sentiment/arsarcasm_v2_train.jsonl sg02_fanar=data/synthetic/sentiment/sg02_fanar.selected.jsonl \
      --out results/quality/sentiment/universal_topics
  ... --limit 300     # tiny mode: first 300 texts per set, 2 samples of 100
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.fit_topics import clean_for_topics, embed  # noqa: E402
from src.data.build_dataset import git_commit, sha256  # noqa: E402


def effective(counts: Counter) -> float:
    """exp(Shannon entropy) of a count distribution: the number of equally used topics it equals."""
    n = sum(counts.values())
    return math.exp(-sum(c / n * math.log(c / n) for c in counts.values() if c)) if n else 0.0


def load_texts(path: Path, clean: dict, limit: int | None) -> tuple[list[str], int]:
    """Cleaned texts with at least clean['min_words'] words; also the number of records read."""
    texts, n = [], 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if limit is not None and n >= limit:
                break
            r = json.loads(line)
            if not r.get("text"):
                continue
            n += 1
            t = clean_for_topics(r["text"], clean)
            if len(t.split()) >= clean.get("min_words", 0):
                texts.append(t)
    return texts, n


def main() -> None:
    """Score every set against the frozen topic list; write JSON and a Markdown table."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--names", type=Path, required=True, help="topic names config (points to the topic list)")
    p.add_argument("--sets", nargs="+", required=True, help="name=path.jsonl pairs")
    p.add_argument("--out", type=Path, required=True, help="output path without extension")
    p.add_argument("--sample", type=int, default=800)
    p.add_argument("--repeats", type=int, default=10)
    p.add_argument("--device", default="cuda")
    p.add_argument("--limit", type=int, default=None, help="tiny mode")
    args = p.parse_args()
    started = time.time()
    if args.limit:
        args.sample, args.repeats = 100, 2

    # The frozen topic list and the cleaning it was fitted with.
    names_cfg = json.loads(args.names.read_text(encoding="utf-8"))
    topic_dir = Path(names_cfg["topic_list"])
    meta = json.loads((topic_dir / "meta.json").read_text(encoding="utf-8"))
    clean = meta["config"]["clean"]
    C = np.load(topic_dir / "centroids.npy")
    name_of = {c: n for n, cs in names_cfg["names"].items() for c in cs}

    results = {}
    for spec in args.sets:
        key, path = spec.split("=", 1)
        texts, n_read = load_texts(Path(path), clean, args.limit)
        X, e5_rev = embed(texts, args.device)
        labels = (X @ C.T).argmax(1)
        topics = [name_of.get(int(c), "unnamed") for c in labels]

        # Effective topics on equal-size samples (seeds 0..repeats-1).
        eff_c, eff_n = [], []
        for seed in range(args.repeats):
            idx = np.random.default_rng(seed).choice(len(texts), min(args.sample, len(texts)), replace=False)
            eff_c.append(effective(Counter(int(labels[i]) for i in idx)))
            eff_n.append(effective(Counter(topics[i] for i in idx if topics[i] != "unnamed")))
        shares = Counter(topics)
        results[key] = {
            "path": path, "sha256": sha256(Path(path)), "n_read": n_read, "n_scored": len(texts),
            "effective_clusters": float(np.mean(eff_c)), "effective_clusters_std": float(np.std(eff_c)),
            "effective_named": float(np.mean(eff_n)), "effective_named_std": float(np.std(eff_n)),
            "unnamed_share": shares["unnamed"] / len(texts),
            "topic_shares": {t: c / len(texts) for t, c in shares.most_common()},
        }
        print(f"{key}: {len(texts)}/{n_read} scored, effective clusters {np.mean(eff_c):.1f}, "
              f"named {np.mean(eff_n):.1f}, unnamed {results[key]['unnamed_share']:.1%}", flush=True)

    # Write JSON and the table.
    k, n_names = len(C), len(names_cfg["names"])
    out = {"topic_list": str(topic_dir), "k": k, "n_named_topics": n_names, "clean": clean,
           "sample": args.sample, "repeats": args.repeats, "e5_revision": e5_rev, "sets": results,
           "git_commit": git_commit(), "seconds": round(time.time() - started),
           "finished": time.strftime("%Y-%m-%d %H:%M")}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out.with_suffix(".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    md = [f"# Topic spread against `{topic_dir.name}`", "",
          f"Generated by `python -m src.quality.topic_spread` ({args.out.with_suffix('.json').as_posix()}). Do not edit by hand. "
          f"Effective topics = exp(entropy), mean ± std over {args.repeats} samples of {args.sample} texts; texts cleaned as the pool, "
          f"under {clean.get('min_words', 0)} words not scored.", "",
          f"| Set | Scored texts | Effective clusters (of {k}) | Effective named topics (of {n_names}) | Unnamed share | Top 3 topics |",
          "|---|---|---|---|---|---|"]
    for key, r in results.items():
        top = ", ".join(f"{t} {s:.0%}" for t, s in list(r["topic_shares"].items())[:3])
        md.append(f"| {key} | {r['n_scored']:,} of {r['n_read']:,} | {r['effective_clusters']:.1f} ± {r['effective_clusters_std']:.1f} | "
                  f"{r['effective_named']:.1f} ± {r['effective_named_std']:.1f} | {r['unnamed_share']:.1%} | {top} |")
    with open(args.out.with_suffix(".md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[4:]))


if __name__ == "__main__":
    sys.exit(main())
