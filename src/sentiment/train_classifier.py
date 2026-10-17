"""Fine-tune a BERT-style encoder as a 3-class sentiment classifier (NEG/NEU/POS) from a config.

Recipe kept as close as possible to the dialect track (src/training/train_classifier.py,
D-008): lower 8 encoder layers frozen, dropout 0.3, fp16, AdamW lr 5e-5 with linear decay,
weight decay 0.01, batch 24, max length 128. Differences, because the task is single-label:
  - softmax head with cross-entropy loss (not 18 sigmoids with BCE), prediction = argmax
  - the epoch is chosen by macro F1 on the S1 dev split (carved from the official train set);
    there is no extra validation split
  - warmup is a share of all steps (warmup_ratio), because S1 train gives ~470 steps per
    epoch and the dialect setting of 500 warmup steps would last more than one epoch
The official test set is scored once at the end and never used for any choice.
Conditions 2/3: an optional `synthetic_data` file (kept separate from the real data, source
"synthetic") is appended to the real training texts; dev and test stay real only.

Outputs in results/sentiment/runs/<run_name>/:
  model/                    best checkpoint (gitignored)
  train_log.json            config, seed, git commit, data hashes, per-epoch dev scores, dev/test scores
  {dev,test}_predictions.jsonl  per-text gold, prediction and class probabilities

Usage:
  python -m src.sentiment.train_classifier --config configs/sentiment/sr01_marbertv2.json
  python -m src.sentiment.train_classifier --config ... --seed 43
  python -m src.sentiment.train_classifier --config ... --limit 300      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)

from src.data.build_dataset import git_commit, sha256
from src.sentiment.build_dataset import SENTIMENTS
from src.sentiment.common import (ID2LABEL, LABEL2ID, evaluate_splits, load_split, predict_logits,
                                  print_scores, sentiment_scores)
from src.training.train_classifier import set_seed

RUNS_DIR = Path("results/sentiment/runs")


def make_loader(tokenizer, texts: list[str], labels, max_length: int, batch_size: int,
                seed: int) -> DataLoader:
    """Tokenize once and wrap in a shuffling DataLoader (single process, Windows-safe)."""
    enc = tokenizer(texts, truncation=True, padding="max_length", max_length=max_length,
                    return_tensors="pt")
    dataset = TensorDataset(enc["input_ids"], enc["attention_mask"], torch.from_numpy(labels))
    # A seeded generator makes the shuffling order reproducible.
    return DataLoader(dataset, batch_size=batch_size, shuffle=True,
                      generator=torch.Generator().manual_seed(seed))


def build_model(name: str, dropout: float, freeze_layers: int):
    """Pretrained encoder with a 3-class head, dropout set at load time, lower layers frozen."""
    # Dropout passed to from_pretrained so the layers are built with it (see the dialect script).
    model = AutoModelForSequenceClassification.from_pretrained(
        name, num_labels=len(SENTIMENTS), id2label=ID2LABEL, label2id=LABEL2ID,
        problem_type="single_label_classification",
        hidden_dropout_prob=dropout, attention_probs_dropout_prob=dropout)
    # Freeze the first `freeze_layers` encoder layers; embeddings stay trainable.
    for layer in model.base_model.encoder.layer[:freeze_layers]:
        for p in layer.parameters():
            p.requires_grad = False
    return model


def train(cfg: dict, device: str) -> dict:
    """Train with epoch selection on dev macro F1; save the best checkpoint; return the log."""
    set_seed(cfg["seed"])
    model_dir = RUNS_DIR / cfg["run_name"] / "model"

    # Data: S1 train for learning, S1 dev for picking the epoch.
    train_texts, train_labels, _ = load_split(Path(cfg["train_data"]), cfg["text_field"], cfg["limit"])
    n_real = len(train_texts)
    # Conditions 2/3: synthetic texts (a separate file, source="synthetic") appended to the real ones.
    if cfg.get("synthetic_data"):
        syn_texts, syn_labels, _ = load_split(Path(cfg["synthetic_data"]), "text", cfg["limit"])
        train_texts, train_labels = train_texts + syn_texts, np.concatenate([train_labels, syn_labels])
    dev_texts, dev_labels, _ = load_split(Path(cfg["dev_data"]), cfg["text_field"], cfg["limit"])
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"])
    loader = make_loader(tokenizer, train_texts, train_labels, cfg["max_length"], cfg["batch_size"], cfg["seed"])

    # Model, optimizer (trainable parameters only), warmup + linear decay, fp16 loss scaling.
    model = build_model(cfg["model"], cfg["dropout"], cfg["freeze_layers"]).to(device)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                  lr=cfg["learning_rate"], weight_decay=cfg["weight_decay"])
    total_steps = len(loader) * cfg["epochs"]
    scheduler = get_linear_schedule_with_warmup(optimizer, int(cfg["warmup_ratio"] * total_steps), total_steps)
    use_amp = cfg["fp16"] and device == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    log = {"config": cfg, "device": device, "n_train": len(train_texts), "n_train_real": n_real,
           "n_train_synthetic": len(train_texts) - n_real, "n_dev": len(dev_texts), "epochs": []}
    best_f1, epochs_without_gain = -1.0, 0
    for epoch in range(1, cfg["epochs"] + 1):
        # One pass over the training data (the model computes cross-entropy from the labels).
        model.train()
        start, running_loss = time.time(), 0.0
        for input_ids, mask, y in loader:
            with torch.autocast("cuda", dtype=torch.float16, enabled=use_amp):
                loss = model(input_ids=input_ids.to(device), attention_mask=mask.to(device),
                             labels=y.to(device)).loss
            optimizer.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            running_loss += loss.item()

        # Dev macro F1 picks the epoch.
        with torch.autocast("cuda", dtype=torch.float16, enabled=use_amp):
            logits = predict_logits(model, tokenizer, dev_texts, cfg["max_length"], device)
        scores = sentiment_scores(dev_labels, logits.argmax(-1))
        f1 = scores["macro"]["f1"]
        log["epochs"].append({"epoch": epoch, "train_loss": running_loss / len(loader), "dev_macro_f1": f1,
                              "dev_accuracy": scores["accuracy"], "dev_f1_pn": scores["f1_pn"],
                              "seconds": round(time.time() - start)})
        print(f"epoch {epoch}: train loss {running_loss / len(loader):.4f}  dev macro F1 {f1:.2f}  "
              f"acc {scores['accuracy']:.2f}  ({time.time() - start:.0f} s)", flush=True)

        # Keep the best checkpoint on disk; stop after `patience` epochs without improvement.
        if f1 > best_f1:
            best_f1, epochs_without_gain = f1, 0
            model.save_pretrained(model_dir)
            tokenizer.save_pretrained(model_dir)
            log["best_epoch"] = epoch
        else:
            epochs_without_gain += 1
            if epochs_without_gain >= cfg["patience"]:
                print("early stopping")
                break
    log["best_dev_macro_f1"] = best_f1
    return log


def main() -> None:
    """Train from a config, then score the best checkpoint on dev and (once) on test."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts per split, 1 epoch")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()

    # Config; seed override and tiny-subset mode change the run name so real runs are never overwritten.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.seed is not None:
        cfg.update(seed=args.seed, run_name=f"{cfg['run_name'].rsplit('_seed', 1)[0]}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, epochs=1, run_name=cfg["run_name"] + f"_limit{args.limit}")
    run_dir = RUNS_DIR / cfg["run_name"]
    if (run_dir / "train_log.json").exists():
        sys.exit(f"{run_dir} already has a finished run; rerun under a new name.")
    if args.device == "cpu":
        print("WARNING: CUDA not available, training on CPU (very slow)")

    # Train, then reload the best checkpoint and score dev and test.
    started = time.time()
    log = train(cfg, args.device)
    model = AutoModelForSequenceClassification.from_pretrained(run_dir / "model").to(args.device)
    tokenizer = AutoTokenizer.from_pretrained(run_dir / "model")
    log.update(evaluate_splits(lambda t: predict_logits(model, tokenizer, t, cfg["max_length"], args.device),
                               cfg, run_dir))

    # Provenance alongside the results.
    log.update(git_commit=git_commit(), python=platform.python_version(), torch=torch.__version__,
               data_sha256={s: sha256(Path(cfg[f"{s}_data"])) for s in ("train", "synthetic", "dev", "test")
                            if cfg.get(f"{s}_data")},
               config_file=str(args.config), total_seconds=round(time.time() - started))
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print_scores(log)


if __name__ == "__main__":
    sys.exit(main())
