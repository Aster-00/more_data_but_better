"""SR14 step 1: nearest EESA train comments for every dev and test comment (retrieval for RAG few-shot).

For each retriever, every dev and test comment (the query) gets its `k_max` most similar train
comments. Only train is ever in the pool: dev and test texts are queries, never neighbours.

Retrievers (config `retrievers`):
  e5       intfloat/multilingual-e5-large, local ("query: " prefix, mean pooling, unit length;
           same encoder settings as src/quality/scorers.py E5Embedder)
  openai   OpenAI text-embedding-3-large through OpenRouter (paid API, Ammar 2026-11-21;
           key from OPENAI_API_KEY in the environment or the gitignored .env)
  bm25     rank_bm25 Okapi BM25 over word tokens (no model)

Embedding retrievers are searched twice, with the same cosine similarity:
  faiss    faiss IndexFlatIP (exact inner-product search)
  numpy    plain dot product + sort
Both are exact, so they should return the same neighbours; the script reports how often they do.

Outputs in `out_dir` (data, gitignored):
  emb_<retriever>_<split>.npy               embeddings, row order = split file order (cached;
                                            an existing file is reused, so paid calls are made once)
  neighbours_<retriever>_<search>.json      {split: {text_id: [[train_text_id, score], ...]}}, most similar first
  retrieval_log.json                        config, model ids, git commit, data hashes, FAISS-vs-numpy agreement,
                                            and how many queries have an exact train copy as top neighbour

Usage:
  python -m src.sentiment.retrieval --config configs/sentiment/sr14_eesa_retrieval.json
  python -m src.sentiment.retrieval --config ... --retrievers e5 bm25     # subset of retrievers
  python -m src.sentiment.retrieval --config ... --limit 30              # tiny-subset mode
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

import numpy as np

from src.data.build_dataset import git_commit, sha256

SPLITS = ("train", "dev", "test")
# BM25 tokens: runs of letters/digits (Arabic and Latin alike). Latin is lower-cased for matching
# only; no Arabic normalisation (alef/yaa, diacritics) is applied, as CLAUDE.md requires it be explicit.
TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def load_texts(path: Path, text_field: str, limit: int | None) -> tuple[list[str], list[str]]:
    """Text ids and texts of one split, in file order (first `limit` rows in tiny-subset mode)."""
    ids, texts = [], []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if limit is not None and len(ids) >= limit:
                break
            r = json.loads(line)
            ids.append(r["text_id"])
            texts.append(r[text_field])
    return ids, texts


def embed_e5(texts: list[str], cache_dir: Path) -> np.ndarray:
    """Unit-length E5 embeddings with the shared encoder settings."""
    from src.quality.scorers import E5Embedder
    return E5Embedder(cache_dir=cache_dir, device="cuda").embed(texts)


def embed_openai(texts: list[str], cfg: dict, batch: int = 256) -> np.ndarray:
    """Unit-length text-embedding-3-large embeddings (the API returns unit vectors; re-normalised to be safe).

    Served through OpenRouter (config `openai_base_url`, `openai_model`; Ammar 2026-11-21), which
    forwards to OpenAI: the texts go to both services.
    """
    from openai import OpenAI
    # Key from the environment, else from the gitignored .env in the repo root (never from a config).
    env_file = Path(".env")
    if not os.environ.get("OPENAI_API_KEY") and env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("OPENAI_API_KEY="):
                os.environ["OPENAI_API_KEY"] = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("OPENAI_API_KEY is not set (environment or .env).")
    client, out = OpenAI(base_url=cfg["openai_base_url"]), []
    for start in range(0, len(texts), batch):
        # Empty strings are rejected by the API; a single space keeps the row order.
        chunk = [t if t.strip() else " " for t in texts[start:start + batch]]
        resp = client.embeddings.create(model=cfg["openai_model"], input=chunk)
        out.extend(d.embedding for d in sorted(resp.data, key=lambda d: d.index))
        print(f"  openai {min(start + batch, len(texts))}/{len(texts)}", flush=True)
    emb = np.asarray(out, dtype=np.float32)
    return emb / np.linalg.norm(emb, axis=1, keepdims=True)


def embeddings(name: str, split: str, texts: list[str], out_dir: Path, cfg: dict, tag: str) -> np.ndarray:
    """Cached embeddings of one split; computed only if the cache file is missing."""
    path = out_dir / f"emb_{name}_{split}{tag}.npy"
    if path.exists():
        emb = np.load(path)
        if len(emb) == len(texts):
            return emb
        sys.exit(f"{path} has {len(emb)} rows but the split has {len(texts)}; delete it only if you are sure.")
    emb = embed_e5(texts, Path(cfg["cache_dir"])) if name == "e5" else embed_openai(texts, cfg)
    np.save(path, emb)
    return emb


def search_faiss(pool: np.ndarray, queries: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Exact inner-product search with faiss (IndexFlatIP): (scores, indices), best first."""
    import faiss
    index = faiss.IndexFlatIP(pool.shape[1])
    index.add(np.ascontiguousarray(pool, dtype=np.float32))
    return index.search(np.ascontiguousarray(queries, dtype=np.float32), k)


def search_numpy(pool: np.ndarray, queries: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray]:
    """Exact inner-product search with numpy: (scores, indices), best first (stable sort, ties by train order)."""
    sims = queries.astype(np.float32) @ pool.astype(np.float32).T
    idx = np.argsort(-sims, axis=1, kind="stable")[:, :k]
    return np.take_along_axis(sims, idx, axis=1), idx


def tokens(text: str) -> list[str]:
    """BM25 tokens (see TOKEN_RE)."""
    return [t.lower() for t in TOKEN_RE.findall(text)]


def search_bm25(pool_texts: list[str], query_texts: list[str], k: int) -> tuple[np.ndarray, np.ndarray]:
    """Okapi BM25 (rank_bm25 defaults k1=1.5, b=0.75): (scores, indices), best first."""
    from rank_bm25 import BM25Okapi
    bm25 = BM25Okapi([tokens(t) for t in pool_texts])
    scores = np.stack([bm25.get_scores(tokens(q)) for q in query_texts])
    idx = np.argsort(-scores, axis=1, kind="stable")[:, :k]
    return np.take_along_axis(scores, idx, axis=1), idx


def to_json(scores: np.ndarray, idx: np.ndarray, query_ids: list[str], pool_ids: list[str]) -> dict:
    """{query text_id: [[train text_id, score], ...]} with scores rounded for the file."""
    return {q: [[pool_ids[j], round(float(s), 6)] for s, j in zip(srow, irow)]
            for q, srow, irow in zip(query_ids, scores, idx)}


def main() -> None:
    """Embed, search and write neighbour files for every configured retriever."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--retrievers", nargs="+", default=None, help="subset of the config's retrievers")
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts per split")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    retrievers = args.retrievers or cfg["retrievers"]
    # Tiny-subset mode writes to its own files so it never mixes with the full run.
    tag = f"_limit{args.limit}" if args.limit else ""
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    data = {s: load_texts(Path(cfg[f"{s}_data"]), cfg["text_field"], args.limit) for s in SPLITS}
    train_ids, train_texts = data["train"]
    train_text_set = {t: i for i, t in zip(train_ids, train_texts)}
    log_path = out_dir / f"retrieval_log{tag}.json"
    log = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else {"retrievers": {}}
    log.update(config=cfg, config_file=str(args.config), git_commit=git_commit(), limit=args.limit,
               data_sha256={s: sha256(Path(cfg[f"{s}_data"])) for s in SPLITS})

    for name in retrievers:
        t0, entry = time.time(), {}
        print(f"== {name}", flush=True)
        if name == "bm25":
            results = {"bm25": {s: search_bm25(train_texts, data[s][1], cfg["k_max"]) for s in ("dev", "test")}}
            entry["model"] = "rank_bm25 BM25Okapi (k1=1.5, b=0.75), tokens = \\w+ runs, Latin lower-cased"
        else:
            pool = embeddings(name, "train", train_texts, out_dir, cfg, tag)
            queries = {s: embeddings(name, s, data[s][1], out_dir, cfg, tag) for s in ("dev", "test")}
            results = {search: {s: fn(pool, queries[s], cfg["k_max"]) for s in ("dev", "test")}
                       for search, fn in (("faiss", search_faiss), ("numpy", search_numpy))}
            entry["model"] = ("intfloat/multilingual-e5-large" if name == "e5"
                              else f"{cfg['openai_model']} via {cfg['openai_base_url']}")
            entry["dim"] = int(pool.shape[1])
            # FAISS vs numpy: same neighbour list (ids, in order) per query, and same set.
            agree = {}
            for s in ("dev", "test"):
                fi, ni = results["faiss"][s][1], results["numpy"][s][1]
                agree[s] = {"same_order": float((fi == ni).all(1).mean()),
                            "same_set": float(np.mean([set(a) == set(b) for a, b in zip(fi, ni)])),
                            "max_score_diff": float(np.abs(results["faiss"][s][0] - results["numpy"][s][0]).max())}
            entry["faiss_vs_numpy"] = agree
            print(f"  faiss vs numpy: {agree}", flush=True)

        # Write one neighbour file per search; count queries whose text is also in train verbatim.
        for search, by_split in results.items():
            out = {s: to_json(sc, ix, data[s][0], train_ids) for s, (sc, ix) in by_split.items()}
            with open(out_dir / f"neighbours_{name}_{search}{tag}.json", "w", encoding="utf-8", newline="\n") as f:
                json.dump(out, f, ensure_ascii=False)
        entry["queries_with_exact_train_copy"] = {s: sum(t in train_text_set for t in data[s][1]) for s in ("dev", "test")}
        entry["seconds"] = round(time.time() - t0)
        log["retrievers"][name] = entry
        print(f"  {entry}", flush=True)

    with open(log_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
