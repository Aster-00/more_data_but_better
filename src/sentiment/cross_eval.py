"""Score trained sentiment classifiers on unseen datasets, with no retraining (SX01, D-028).

Each trained run is loaded from results/sentiment/runs/<run>/model and predicts every dataset in
the config. The train_log.json of the run gives its model, classes, max length and batch size, so
scoring matches the original run. 2-class runs (SR03) are scored on the NEG and POS texts only.

Before scoring, a run re-predicts the first `check_texts` ArSarcasm-v2 test texts and must match
its stored test_predictions.jsonl. This catches a wrongly loaded model or head. The stored
predictions are only compared, nothing is chosen from them.

Run folders are never written to. Outputs in results/sentiment/cross_eval/<run>/:
  <dataset>_predictions.jsonl   per-text gold, prediction and class probabilities
  scores.json                   scores, check result, provenance (also marks the run as finished)

Usage:
  python -m src.sentiment.cross_eval --config configs/sentiment/cross_eval_sx01.json --list llm
  python -m src.sentiment.cross_eval --config ... --family bert        # all BERTs, one process
  python -m src.sentiment.cross_eval --config ... --run sr01_jais2_seed42
  python -m src.sentiment.cross_eval --config ... --family bert --limit 40 --max-runs 2 --device cpu
"""
from __future__ import annotations

import argparse
import gc
import json
import platform
import re
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from src.data.build_dataset import git_commit, sha256
from src.sentiment.common import load_split, predict_logits, run_classes, sentiment_scores, write_predictions

RUNS_DIR = Path("results/sentiment/runs")


def read_log(run: str) -> dict:
    """The train_log.json of a run. Older logs keep their first run_name, so it is reset to the folder."""
    with open(RUNS_DIR / run / "train_log.json", encoding="utf-8") as f:
        log = json.load(f)
    log["config"]["run_name"] = run
    return log


def is_llm(cfg: dict) -> bool:
    """QLoRA configs have LoRA fields; BERT configs do not."""
    return "lora_r" in cfg


def list_runs(pattern: str, family: str) -> list[str]:
    """Finished runs matching the pattern, sorted; smoke tests and aborted folders do not match."""
    runs = []
    for d in sorted(RUNS_DIR.iterdir()):
        if re.match(pattern, d.name) and (d / "train_log.json").exists() and (d / "model").is_dir():
            if is_llm(read_log(d.name)["config"]) == (family == "llm"):
                runs.append(d.name)
    return runs


def make_predictor(cfg: dict, device: str):
    """Load a saved run; return `predict(texts) -> logits`, built as in the two trainers."""
    if is_llm(cfg):
        # Imported here so BERT-only runs do not load the QLoRA stack.
        from src.sentiment.train_lora_classifier import load_saved
        model, tokenizer = load_saved(cfg)

        def predict(texts: list[str]) -> np.ndarray:
            """Logits of the saved adapter, bf16 inference."""
            with torch.autocast("cuda", dtype=torch.bfloat16):
                return predict_logits(model, tokenizer, texts, cfg["max_length"], "cuda", cfg["eval_batch_size"])
        return predict
    model_dir = RUNS_DIR / cfg["run_name"] / "model"
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    tokenizer = AutoTokenizer.from_pretrained(model_dir)
    return lambda texts: predict_logits(model, tokenizer, texts, cfg["max_length"], device)


def check_stored(predict, cfg: dict, n: int) -> float:
    """Share of the first n ArSarcasm-v2 test texts predicted as in the stored predictions of the run."""
    classes = run_classes(cfg)
    texts, _, ids = load_split(Path(cfg["test_data"]), cfg["text_field"], n, classes)
    with open(RUNS_DIR / cfg["run_name"] / "test_predictions.jsonl", encoding="utf-8") as f:
        stored = [json.loads(line) for _, line in zip(range(n), f)]
    if [r["text_id"] for r in stored] != ids:
        raise RuntimeError(f"{cfg['run_name']}: stored predictions are in a different order")
    now = [classes[i] for i in predict(texts).argmax(-1)]
    return float(np.mean([a == r["pred"] for a, r in zip(now, stored)]))


def score_run(run: str, xc: dict, out_root: Path, device: str, limit: int | None) -> None:
    """Check one run, predict every dataset, and write its outputs; scores.json comes last."""
    out = out_root / run
    if (out / "scores.json").exists():
        return
    started = time.time()
    cfg = read_log(run)["config"]
    classes = run_classes(cfg)
    predict = make_predictor(cfg, device)

    agreement = check_stored(predict, cfg, xc["check_texts"])
    if agreement < xc["check_min_agreement"]:
        raise RuntimeError(f"{run}: only {agreement:.0%} of the stored test predictions reproduced")

    # scores.json is written last, so a crash leaves a run that is simply scored again.
    out.mkdir(parents=True, exist_ok=True)
    scores = {}
    for name, path in xc["datasets"].items():
        texts, gold, ids = load_split(Path(path), xc["text_field"], limit, classes)
        logits = predict(texts)
        write_predictions(out / f"{name}_predictions.jsonl", ids, gold, logits, classes)
        scores[name] = {"n": len(texts), **sentiment_scores(gold, logits.argmax(-1), classes)}
    record = {"run": run, "classes": classes, "datasets": scores, "check_agreement": agreement,
              "check_texts": xc["check_texts"], "model": cfg["model"], "cross_eval": xc, "limit": limit,
              "data_sha256": {n: sha256(Path(p)) for n, p in xc["datasets"].items()},
              "git_commit": git_commit(), "python": platform.python_version(), "torch": torch.__version__,
              "device": device, "seconds": round(time.time() - started, 1)}
    with open(out / "scores.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"{run}: " + "  ".join(f"{n} F1 {s['macro']['f1']:.2f}" for n, s in scores.items())
          + f"  check {agreement:.0%}  {record['seconds']}s", flush=True)


def main() -> None:
    """Pick the runs from the arguments and score them; finished runs are skipped."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--family", choices=("bert", "llm"), help="score every run of this family")
    p.add_argument("--run", help="score one run folder")
    p.add_argument("--list", choices=("bert", "llm"), help="print the run names of a family and stop")
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts per dataset")
    p.add_argument("--max-runs", type=int, default=None, help="tiny-subset mode: first N runs")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        xc = json.load(f)
    if args.list:
        print("\n".join(list_runs(xc["run_pattern"], args.list)))
        return
    runs = [args.run] if args.run else list_runs(xc["run_pattern"], args.family)
    # Tiny-subset results go to their own folder, so they never count as finished real runs.
    out_root = Path(xc["out_dir"] + (f"_limit{args.limit}" if args.limit is not None else ""))
    for run in runs[:args.max_runs]:
        score_run(run, xc, out_root, args.device, args.limit)
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


if __name__ == "__main__":
    sys.exit(main())
