"""Train a TF-IDF + logistic regression multi-label dialect classifier from a JSON config.

Non-neural baseline: one binary logistic regression per dialect (one-vs-rest) over
TF-IDF features, character n-grams (within word boundaries) plus word n-grams. Uses the
same data, seeded 90/10 train/validation split, threshold (0.3) and metrics as
src/training/train_classifier.py, so its scores can be compared with the transformers.

The MLADI dev set is NOT used for training or settings; it is only scored once at the end.
This model cannot be submitted to the MLADI leaderboard (the Space only loads Hub
transformer models), so it is a dev-set-only reference.

Outputs in results/runs/<run_name>/:
  train_log.json    config, seed, git commit, data hash, validation and dev scores

Usage:
  python -m src.training.train_tfidf --config configs/baseline_real_only_tfidf_lr.json
  python -m src.training.train_tfidf --config configs/baseline_real_only_tfidf_lr.json --limit 500
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import sklearn
from joblib import parallel_config
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

from src.data.build_dataset import DIALECTS, git_commit, read_dev, sha256
from src.evaluation.metrics import multilabel_scores
from src.training.train_classifier import load_records, split_train_val


def build_vectorizers(cfg: dict) -> list[TfidfVectorizer]:
    """Character and word TF-IDF vectorizers; no lowercasing or other text normalization."""
    # lowercase=False keeps Latin-script casing as is (script and code-switching are factors).
    common = dict(lowercase=False, sublinear_tf=True, min_df=cfg["min_df"], dtype=np.float32)
    return [
        TfidfVectorizer(analyzer="char_wb", ngram_range=tuple(cfg["char_ngrams"]),
                        max_features=cfg["max_features"], **common),
        TfidfVectorizer(analyzer="word", ngram_range=tuple(cfg["word_ngrams"]),
                        token_pattern=r"\S+", max_features=cfg["max_features"], **common),
    ]


def scores_at_threshold(probs: np.ndarray, gold: np.ndarray, threshold: float,
                        dialects: list[str]) -> dict:
    """Macro/micro scores for the given dialect columns after thresholding probabilities."""
    decisions = (probs >= threshold).astype(int)
    idx = [DIALECTS.index(d) for d in dialects]
    # gold columns are in the order of `dialects`; prediction columns are in DIALECTS order.
    return multilabel_scores({d: gold[:, j].astype(int).tolist() for j, d in enumerate(dialects)},
                             {d: decisions[:, i].tolist() for d, i in zip(dialects, idx)})


def train(cfg: dict) -> dict:
    """Fit TF-IDF + one-vs-rest logistic regression; score validation and dev; return the log."""
    # Data: load and split exactly as the transformer trainer does.
    texts, labels = load_records(Path(cfg["data"]), cfg["text_field"], cfg["limit"])
    train_idx, val_idx = split_train_val(len(texts), cfg["val_fraction"], cfg["seed"])
    train_texts, val_texts = [texts[i] for i in train_idx], [texts[i] for i in val_idx]

    # Features: fit the vocabularies and IDF on the training split only.
    start = time.time()
    vectorizers = build_vectorizers(cfg)
    x_train = hstack([v.fit_transform(train_texts) for v in vectorizers]).tocsr()
    x_val = hstack([v.transform(val_texts) for v in vectorizers]).tocsr()

    # One logistic regression per dialect. Dialects with no positive example in a tiny
    # subset would crash the solver, so their column is predicted as always 0 instead.
    y_train = labels[train_idx].astype(int)
    present = [j for j in range(len(DIALECTS)) if 0 < y_train[:, j].sum() < len(y_train)]
    clf = OneVsRestClassifier(
        LogisticRegression(C=cfg["C"], max_iter=cfg["max_iter"], solver="liblinear",
                           random_state=cfg["seed"]),
        n_jobs=cfg["n_jobs"])
    # joblib passes large arrays to worker processes as read-only memory maps, which
    # liblinear cannot use ("WRITEBACKIFCOPY base is read-only"); max_nbytes=None sends
    # each worker its own writable copy instead.
    with parallel_config(max_nbytes=None):
        clf.fit(x_train, y_train[:, present])

    def predict(x) -> np.ndarray:
        """18-column probability matrix (columns of absent dialects stay 0)."""
        probs = np.zeros((x.shape[0], len(DIALECTS)), dtype=np.float32)
        probs[:, present] = clf.predict_proba(x)
        return probs

    # Validation split: all 18 dialects, same threshold as the transformers.
    val_scores = scores_at_threshold(predict(x_val), labels[val_idx], cfg["threshold"], DIALECTS)

    # Dev set: scored once, on the dialects it has labels for.
    dev_texts, dev_gold = read_dev(Path(cfg["dev"]))
    x_dev = hstack([v.transform(dev_texts) for v in vectorizers]).tocsr()
    dev_probs = predict(x_dev)
    dev_dialects = list(dev_gold)
    dev_gold_matrix = np.array([dev_gold[d] for d in dev_dialects]).T
    dev_scores = scores_at_threshold(dev_probs, dev_gold_matrix, cfg["threshold"], dev_dialects)

    return {"config": cfg, "n_train": len(train_idx), "n_val": len(val_idx),
            "n_features": x_train.shape[1], "dialects_fitted": [DIALECTS[j] for j in present],
            "val_macro_f1": val_scores["macro"]["f1"], "val_micro_f1": val_scores["micro_f1"],
            "val_macro": val_scores["macro"], "fit_seconds": round(time.time() - start),
            "dev": dev_scores}


def main() -> None:
    """Train from a config, score validation and dev, write train_log.json."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N records")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    args = p.parse_args()

    # Load the config; seed and tiny-subset overrides work as in train_classifier.py.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.seed is not None:
        base = cfg["run_name"].rsplit("_seed", 1)[0]
        cfg.update(seed=args.seed, run_name=f"{base}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, run_name=cfg["run_name"] + f"_limit{args.limit}")

    # Train and score, recording provenance alongside the results.
    started = time.time()
    log = train(cfg)
    log.update(git_commit=git_commit(), data_sha256=sha256(Path(cfg["data"])),
               dev_sha256=sha256(Path(cfg["dev"])), python=platform.python_version(),
               sklearn=sklearn.__version__, config_file=str(args.config),
               total_seconds=round(time.time() - started))
    run_dir = Path("results/runs") / cfg["run_name"]
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    m = log["dev"]["macro"]
    print(f"VAL  macro F1 {log['val_macro_f1']:.2f}  micro F1 {log['val_micro_f1']:.2f}")
    print(f"DEV  macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}  "
          f"| micro F1 {log['dev']['micro_f1']:.2f}")


if __name__ == "__main__":
    sys.exit(main())
