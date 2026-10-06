"""Score a multi-label dialect model on the MLADI dev set (120 sentences, 8 dialects).

Prediction follows the MLADI leaderboard's `predict_binary_outcomes` exactly: raw sentence
-> tokenizer (truncation, max_length 128) -> 18 logits -> sigmoid -> valid if >= threshold
(0.3). So a dev score here uses the same settings the leaderboard will use on the test set.

Outputs in results/runs/<run-name>/:
  dev_metrics.json      macro/micro scores, per-dialect breakdown, settings, provenance
  dev_predictions.txt   18 comma-separated 0/1 per line (NADI 2024 scorer format)
  dev_probabilities.tsv 18 sigmoid probabilities per line (for later threshold analysis)

Usage:
  python -m src.evaluation.evaluate_dev --model Mohamedelzeftawy/LahjatBERT_cl_aldi
  python -m src.evaluation.evaluate_dev --model results/runs/<run>/model --run-name <run>
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data.build_dataset import DIALECTS, git_commit, read_dev, sha256
from src.evaluation.metrics import multilabel_scores


def predict_probabilities(model, tokenizer, texts: list[str], device: str,
                          batch_size: int = 32) -> np.ndarray:
    """Sigmoid probabilities (n_texts x 18) for raw texts, leaderboard-style tokenization."""
    model.eval()
    chunks = []
    # Batches of sentences; padding inside a batch is masked, so results match one-by-one inference.
    for start in range(0, len(texts), batch_size):
        batch = texts[start:start + batch_size]
        enc = tokenizer(batch, truncation=True, padding=True, max_length=128,
                        return_tensors="pt").to(device)
        with torch.no_grad():
            logits = model(**enc).logits
        chunks.append(torch.sigmoid(logits.float()).cpu().numpy())
    return np.concatenate(chunks)


def check_label_order(model) -> None:
    """Stop if the model's outputs are not the 18 dialects in leaderboard order."""
    # Models with generic names (LABEL_0...) cannot be checked, so they are trusted as-is.
    names = [model.config.id2label[i] for i in range(model.config.num_labels)]
    if len(names) != len(DIALECTS):
        raise ValueError(f"model has {len(names)} outputs, expected {len(DIALECTS)}")
    if not names[0].startswith("LABEL_") and names != DIALECTS:
        raise ValueError(f"label order differs from leaderboard order: {names}")


def evaluate(model_path: str, dev_path: Path, threshold: float, device: str) -> tuple[dict, np.ndarray]:
    """Load a model, predict the dev set, and score it; return metrics and probabilities."""
    # Load model and tokenizer (from the Hub or a local folder) and check the output order.
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(model_path).to(device)
    check_label_order(model)

    # Predict every dev sentence, then threshold the probabilities into 0/1 decisions.
    texts, gold = read_dev(dev_path)
    probs = predict_probabilities(model, tokenizer, texts, device)
    decisions = (probs >= threshold).astype(int)

    # Score only the dialects the dev set has labels for.
    pred = {d: decisions[:, DIALECTS.index(d)].tolist() for d in gold}
    return multilabel_scores(gold, pred), probs


def parse_args() -> argparse.Namespace:
    """Command-line options: model, run name, dev file, threshold, device."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", required=True, help="Hub model id or local model folder")
    p.add_argument("--run-name", default=None, help="results folder name (default: model name)")
    p.add_argument("--dev", type=Path, default=Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"))
    p.add_argument("--threshold", type=float, default=0.3, help="0.3 = leaderboard setting")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--results-dir", type=Path, default=Path("results/runs"))
    return p.parse_args()


def main() -> None:
    """Evaluate one model on the dev set and write metrics and predictions."""
    args = parse_args()
    run_name = args.run_name or args.model.replace("/", "__")
    out_dir = args.results_dir / run_name
    out_dir.mkdir(parents=True, exist_ok=True)

    # Predict and score.
    scores, probs = evaluate(args.model, args.dev, args.threshold, args.device)

    # Save metrics together with the settings and versions that produced them.
    report = {
        "model": args.model,
        "dev_file": str(args.dev),
        "dev_sha256": sha256(args.dev),
        "threshold": args.threshold,
        "max_length": 128,
        "device": args.device,
        "git_commit": git_commit(),
        "python": platform.python_version(),
        "torch": torch.__version__,
        **scores,
    }
    with open(out_dir / "dev_metrics.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Save 0/1 decisions (NADI scorer format) and raw probabilities, one line per sentence.
    decisions = (probs >= args.threshold).astype(int)
    with open(out_dir / "dev_predictions.txt", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(",".join(map(str, row)) + "\n" for row in decisions)
    with open(out_dir / "dev_probabilities.tsv", "w", encoding="utf-8", newline="\n") as f:
        f.write("\t".join(DIALECTS) + "\n")
        f.writelines("\t".join(f"{p:.6f}" for p in row) + "\n" for row in probs)

    # Console summary: macro scores first, then per-dialect F1.
    m = scores["macro"]
    print(f"{args.model}  macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}  "
          f"Acc {m['accuracy']:.2f}  | micro F1 {scores['micro_f1']:.2f}")
    print("  per-dialect F1: " + "  ".join(f"{d} {s['f1']:.1f}" for d, s in scores["per_dialect"].items()))
    print(f"  wrote {out_dir}")


if __name__ == "__main__":
    sys.exit(main())
