"""Multi-label dialect-identification metrics, computed the way the NADI 2024 / MLADI scorers do."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


def multilabel_scores(gold: dict[str, list[int]], pred: dict[str, list[int]]) -> dict:
    """Per-dialect binary precision/recall/F1/accuracy, their macro averages, and micro F1.

    Only dialects present in `gold` are scored (the dev set has 8, the test set 11).
    The official metric is macro F1: F1 per dialect, then the plain average.

    LahjatBERT (bert_trainer._print_evaluation_metrics): reports micro-averaged F1 on the
    dev set. Wrong for comparison because the NADI 2024 scorer and the MLADI leaderboard
    rank by macro F1, so their printed number is not the official one.
    Fix: report macro (official) first, and micro alongside for comparison with their logs.
    """
    # Score each dialect as its own yes/no task (positive class = "valid"), in percent.
    per_dialect = {}
    for d, y_true in gold.items():
        y_pred = pred[d]
        per_dialect[d] = {
            "precision": 100 * precision_score(y_true, y_pred, zero_division=0),
            "recall": 100 * recall_score(y_true, y_pred, zero_division=0),
            "f1": 100 * f1_score(y_true, y_pred, zero_division=0),
            "accuracy": 100 * accuracy_score(y_true, y_pred),
            "gold_positives": int(sum(y_true)),
            "predicted_positives": int(sum(y_pred)),
        }

    # Macro = plain average over the scored dialects.
    macro = {m: float(np.mean([s[m] for s in per_dialect.values()]))
             for m in ("precision", "recall", "f1", "accuracy")}

    # Micro F1 = pool every (sentence, dialect) decision, then compute one F1.
    all_true = np.concatenate([np.asarray(gold[d]) for d in gold])
    all_pred = np.concatenate([np.asarray(pred[d]) for d in gold])
    micro_f1 = 100 * f1_score(all_true, all_pred, zero_division=0)

    return {"macro": macro, "micro_f1": micro_f1, "per_dialect": per_dialect,
            "dialects_scored": list(gold)}
