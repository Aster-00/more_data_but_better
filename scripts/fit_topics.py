"""Fit a frozen E5 k-means topic list on real data and write a report for naming the topics.

Inputs: a config (configs/quality/topics_*.json) naming a real JSONL set, k and a seed.
Outputs, in <output_dir>/<name>/ (gitignored, because the report quotes tweets):
  centroids.npy     (k x 1024) unit-length cluster centres: the frozen topic list
  embeddings.npy    (n x 1024) E5 vectors, if save_embeddings is set
  assignments.jsonl text_id, cluster and cosine similarity to the centre, one line per record
  report.md         per cluster: size, share, mean ALDi, top countries, closest and random tweets
  meta.json         config, seed, git commit, E5 revision, data hash, counts, timings

Usage:
  python scripts/fit_topics.py --config configs/quality/topics_d1.json
  python scripts/fit_topics.py --config configs/quality/topics_d1.json --limit 2000   (tiny mode)
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.build_dataset import git_commit, sha256  # noqa: E402


# Optional cleaning for the E5 input only (explicit and configurable, CLAUDE.md data rules).
# The run d1_k30_seed0 showed E5 grouping tweets by form (placeholders, laughter, length), not topic.
# EMOJI is QADI's emoji placeholder (added for the universal pool; D1 has none, so d1_* lists are unchanged).
PLACEHOLDER_RE = re.compile(r"\b(?:USER|URL|NUM|EMOJI)\b|https?://\S+|@\w+|…")
LAUGH_RE = re.compile(r"(?:ه){3,}")


def clean_for_topics(text: str, opts: dict) -> str:
    """Remove placeholders, turn hashtags into words, shorten laughter; collapse spaces."""
    if opts.get("remove_placeholders"):
        text = PLACEHOLDER_RE.sub(" ", text)
    if opts.get("hashtags_to_words"):
        text = re.sub(r"#(\S+)", lambda m: m.group(1).replace("_", " "), text)
    if opts.get("shorten_laughter"):
        text = LAUGH_RE.sub("هه", text)
    return " ".join(text.split())


def load_records(path: Path, text_field: str, limit: int | None, clean: dict | None = None,
                 group_field: str = "countries") -> list[dict]:
    """Real records only; one record per unique (cleaned) text, the first one.

    With `clean`, E5 sees the cleaned text and texts shorter than clean["min_words"] are skipped.
    `group_field` (a string or a list per record) is what the report counts per cluster.
    """
    clean = clean or {}
    out, seen = [], set()
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            if limit is not None and i >= limit:
                break
            r = json.loads(line)
            # Topic lists are fitted on real data only (D-011).
            if r.get("source") != "real":
                raise ValueError(f"{path} has a non-real record: topic pools must be real data")
            t = clean_for_topics(r[text_field], clean) if clean else r[text_field]
            if t in seen or len(t.split()) < clean.get("min_words", 0):
                continue
            seen.add(t)
            g = r.get(group_field, [])
            out.append({"text_id": r["text_id"], "text": t, "aldi": r.get("aldi_score"),
                        "groups": [g] if isinstance(g, str) else g})
    return out


def cap_groups(recs: list[dict], cap: int, seed: int) -> list[dict]:
    """At most `cap` records per group (seeded random sample), so no single dataset sets the topics."""
    rng = random.Random(seed)
    by_group: dict[str, list[dict]] = {}
    for r in recs:
        by_group.setdefault(r["groups"][0], []).append(r)
    keep = {id(r) for rs in by_group.values() for r in (rng.sample(rs, cap) if len(rs) > cap else rs)}
    return [r for r in recs if id(r) in keep]   # input order kept


def embed(texts: list[str], device: str) -> tuple[np.ndarray, str | None]:
    """E5 embeddings in fp32 (as in measure_dataset_quality.py), plus the model revision."""
    from src.quality.scorers import E5Embedder
    emb = E5Embedder(None, device, batch_size=64)
    emb.model.float()  # fp32 keeps re-runs reproducible
    # Length-sorted batches waste less padding; results are put back in the input order.
    order = sorted(range(len(texts)), key=lambda i: len(texts[i]))
    X = emb.embed([texts[i] for i in order])
    out = np.empty_like(X)
    out[order] = X
    return out, getattr(emb.model.config, "_commit_hash", None)


def write_report(path: Path, recs: list[dict], labels: np.ndarray, sims: np.ndarray, cfg: dict) -> None:
    """Markdown report: clusters by size, each with stats, closest-to-centre and random tweets."""
    n, k = len(recs), cfg["k"]
    sizes = Counter(labels.tolist())
    rng = random.Random(cfg["seed"])
    lines = [f"# Topic clusters: {cfg['name']}", "",
             f"{n} unique texts from `{cfg['data']}`, E5 k-means, k = {k}, seed {cfg['seed']}. "
             f"Clusters sorted by size. 'sim' = cosine similarity to the cluster centre.", ""]
    for c, size in sizes.most_common():
        idx = np.flatnonzero(labels == c)
        aldi = [recs[i]["aldi"] for i in idx if recs[i]["aldi"] is not None]
        groups = Counter(g for i in idx for g in recs[i]["groups"])
        top = ", ".join(f"{g} {cnt / size:.0%}" for g, cnt in groups.most_common(4))
        lines += [f"## Cluster {c}: {size} texts ({size / n:.1%})", "",
                  f"- Mean ALDi {f'{np.mean(aldi):.2f}' if aldi else 'n/a'}; mean sim {sims[idx].mean():.3f}; "
                  f"mean words {np.mean([len(recs[i]['text'].split()) for i in idx]):.1f}",
                  f"- Top {cfg.get('group_field', 'countries')}: {top}", "", "Closest to the centre:", ""]
        for i in idx[np.argsort(-sims[idx])][:cfg["n_closest"]]:
            lines.append(f"- ({sims[i]:.3f}) {recs[i]['text']}")
        lines += ["", "Random:", ""]
        for i in rng.sample(list(idx), min(cfg["n_random"], size)):
            lines.append(f"- ({sims[i]:.3f}) {recs[i]['text']}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--config", required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N records, name gets _limitN")
    p.add_argument("--device", default="cuda", choices=["cuda", "cpu"])
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    name = cfg["name"] + (f"_limit{args.limit}" if args.limit else "")
    out_dir = Path(cfg["output_dir"]) / name
    if out_dir.exists():
        raise SystemExit(f"{out_dir} exists; a frozen topic list is never overwritten")
    t0 = time.time()

    # Data: unique real texts.
    recs = load_records(Path(cfg["data"]), cfg["text_field"], args.limit, cfg.get("clean"),
                        cfg.get("group_field", "countries"))
    print(f"{len(recs)} unique texts", flush=True)
    if cfg.get("cap_per_group"):
        recs = cap_groups(recs, cfg["cap_per_group"], cfg["seed"])
        print(f"{len(recs)} texts after the cap of {cfg['cap_per_group']} per {cfg['group_field']}", flush=True)

    # Embeddings.
    X, e5_rev = embed([r["text"] for r in recs], args.device)
    t_embed = time.time() - t0
    print(f"E5 done ({t_embed:.0f}s)", flush=True)

    # k-means on unit vectors; centres re-normalised so cosine = dot product.
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=cfg["k"], n_init=cfg["n_init"], random_state=cfg["seed"]).fit(X)
    C = km.cluster_centers_ / np.linalg.norm(km.cluster_centers_, axis=1, keepdims=True)
    labels = km.labels_
    sims = (X * C[labels]).sum(1)
    t_km = time.time() - t0 - t_embed
    print(f"k-means done ({t_km:.0f}s)", flush=True)

    # Outputs.
    out_dir.mkdir(parents=True)
    np.save(out_dir / "centroids.npy", C.astype(np.float32))
    if cfg.get("save_embeddings"):
        # Same row order as assignments.jsonl, so other k values can be fitted without re-embedding.
        np.save(out_dir / "embeddings.npy", X.astype(np.float32))
    with open(out_dir / "assignments.jsonl", "w", encoding="utf-8") as f:
        for r, c, s in zip(recs, labels, sims):
            f.write(json.dumps({"text_id": r["text_id"], "cluster": int(c), "sim": round(float(s), 4)}) + "\n")
    write_report(out_dir / "report.md", recs, labels, sims, cfg | {"name": name})
    sizes = Counter(labels.tolist())
    group_sizes = Counter(r["groups"][0] for r in recs if r["groups"])
    meta = {"config": cfg, "config_file": args.config, "limit": args.limit, "git_commit": git_commit(),
            "group_sizes": dict(group_sizes.most_common()),
            "data_sha256": sha256(Path(cfg["data"])), "e5_model": "intfloat/multilingual-e5-large",
            "e5_revision": e5_rev, "n_texts": len(recs), "inertia": float(km.inertia_),
            "cluster_sizes": {int(c): s for c, s in sorted(sizes.items())},
            "seconds": {"embed": round(t_embed), "kmeans": round(t_km), "total": round(time.time() - t0)}}
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    # Console shows sizes only (console logs may be tracked; tweets stay in data/).
    print("cluster sizes (largest first):", [s for _, s in sizes.most_common()])
    print(f"written to {out_dir} ({time.time() - t0:.0f}s total)")


if __name__ == "__main__":
    main()
