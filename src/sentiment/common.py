"""Shared pieces of the sentiment track: loading S1 splits, prediction, metrics, prediction files.

Metrics: macro F1 over NEG/NEU/POS is the main score (CLAUDE.md: macro-averaged at minimum).
F1-PN, the mean F1 of POS and NEG only, is reported alongside because it is the official
metric of the WANLP 2021 shared task (sentiment subtask) that released ArSarcasm-v2, so our
test scores can be compared with the published ones.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import torch
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support

from src.sentiment.build_dataset import SENTIMENTS

LABEL2ID = {s: i for i, s in enumerate(SENTIMENTS)}
ID2LABEL = dict(enumerate(SENTIMENTS))


def load_split(path: Path, text_field: str, limit: int | None) -> tuple[list[str], np.ndarray, list[str]]:
    """Read one S1 split; return texts, label ids (NEG=0, NEU=1, POS=2) and text ids."""
    texts, labels, ids = [], [], []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            # Tiny-subset mode: only the first `limit` records.
            if limit is not None and i >= limit:
                break
            r = json.loads(line)
            texts.append(r[text_field])
            labels.append(LABEL2ID[r["sentiment"]])
            ids.append(r["text_id"])
    return texts, np.asarray(labels, dtype=np.int64), ids


def predict_logits(model, tokenizer, texts: list[str], max_length: int, device: str,
                   batch_size: int = 64) -> np.ndarray:
    """Class logits (n_texts x 3) for raw texts; batches padded to their longest text."""
    model.eval()
    chunks = []
    for start in range(0, len(texts), batch_size):
        enc = tokenizer(texts[start:start + batch_size], truncation=True, padding=True,
                        max_length=max_length, return_tensors="pt").to(device)
        with torch.no_grad():
            chunks.append(model(**enc).logits.float().cpu().numpy())
    return np.concatenate(chunks)


def sentiment_scores(gold: np.ndarray, pred: np.ndarray) -> dict:
    """Macro P/R/F1, accuracy, F1-PN, per-class scores and the confusion matrix (in percent)."""
    labels = list(range(len(SENTIMENTS)))
    p, r, f, support = precision_recall_fscore_support(gold, pred, labels=labels, zero_division=0)
    per_class = {s: {"precision": 100 * p[i], "recall": 100 * r[i], "f1": 100 * f[i],
                     "gold": int(support[i]), "predicted": int((pred == i).sum())}
                 for i, s in enumerate(SENTIMENTS)}
    return {
        "macro": {"precision": 100 * float(p.mean()), "recall": 100 * float(r.mean()),
                  "f1": 100 * float(f.mean())},
        "accuracy": 100 * accuracy_score(gold, pred),
        "f1_pn": (per_class["POS"]["f1"] + per_class["NEG"]["f1"]) / 2,
        "per_class": per_class,
        # Rows = gold class, columns = predicted class, both in SENTIMENTS order.
        "confusion": confusion_matrix(gold, pred, labels=labels).tolist(),
        "classes": SENTIMENTS,
    }


def write_predictions(path: Path, ids: list[str], gold: np.ndarray, logits: np.ndarray) -> None:
    """One JSON line per text: id, gold and predicted label, class probabilities."""
    probs = torch.softmax(torch.from_numpy(logits), dim=-1).numpy()
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for i, text_id in enumerate(ids):
            f.write(json.dumps({"text_id": text_id, "gold": ID2LABEL[int(gold[i])],
                                "pred": ID2LABEL[int(probs[i].argmax())],
                                "probs": {s: round(float(probs[i][k]), 5) for k, s in ID2LABEL.items()}}) + "\n")


def evaluate_splits(predict, cfg: dict, run_dir: Path) -> dict:
    """Score the selected model on dev and test; write per-text predictions; return both score sets.

    `predict(texts) -> logits`. Dev chose the epoch; test is scored here once and never used
    for any choice.
    """
    out = {}
    for split in ("dev", "test"):
        texts, gold, ids = load_split(Path(cfg[f"{split}_data"]), cfg["text_field"], cfg["limit"])
        logits = predict(texts)
        write_predictions(run_dir / f"{split}_predictions.jsonl", ids, gold, logits)
        out[split] = sentiment_scores(gold, logits.argmax(-1))
    return out


def print_scores(log: dict) -> None:
    """Print the dev and test headline numbers (ASCII only)."""
    for split in ("dev", "test"):
        s = log[split]
        print(f"{split.upper():4s} macro F1 {s['macro']['f1']:.2f}  P {s['macro']['precision']:.2f}  "
              f"R {s['macro']['recall']:.2f}  acc {s['accuracy']:.2f}  F1-PN {s['f1_pn']:.2f}  "
              f"(best epoch {log.get('best_epoch')})", flush=True)
