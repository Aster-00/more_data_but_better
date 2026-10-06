"""Fine-tune a multi-label dialect classifier (18 sigmoid outputs) from a JSON config.

Recipe follows LahjatBERT's baseline (bert_trainer.py): MARBERT, lower 8 encoder layers
frozen, fp16, AdamW lr 5e-5 with 500 warmup steps and linear decay, weight decay 0.01,
batch 24, random 90/10 train/validation split of the training data, early stopping on the
validation score, threshold 0.3. Differences are documented in the function docstrings.

The MLADI dev set is NOT used for training or checkpoint selection; it is only scored
once at the end (results/runs/<run>/dev_metrics.json).

Outputs in results/runs/<run_name>/:
  model/            best checkpoint (gitignored)
  train_log.json    config, seed, git commit, data hash, per-epoch validation scores
  dev_*             dev-set metrics and predictions (see src/evaluation/evaluate_dev.py)

Usage:
  python -m src.training.train_classifier --config configs/baseline_real_only.json
  python -m src.training.train_classifier --config configs/baseline_real_only.json --limit 500
"""
from __future__ import annotations

import argparse
import json
import platform
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from torch.utils.data import DataLoader, TensorDataset
from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                          get_linear_schedule_with_warmup)

from src.data.build_dataset import DIALECTS, git_commit, sha256
from src.evaluation.evaluate_dev import evaluate as evaluate_dev
from src.evaluation.metrics import multilabel_scores


def set_seed(seed: int) -> None:
    """Seed Python, NumPy and PyTorch (CPU and GPU) for a reproducible run."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def load_records(path: Path, text_field: str, limit: int | None) -> tuple[list[str], np.ndarray]:
    """Read the JSONL dataset; return texts and an (n x 18) 0/1 label matrix."""
    texts, labels = [], []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            # Tiny-subset mode: only the first `limit` records.
            if limit is not None and i >= limit:
                break
            r = json.loads(line)
            texts.append(r[text_field])
            labels.append([r["labels"][d] for d in DIALECTS])
    return texts, np.asarray(labels, dtype=np.float32)


def split_train_val(n: int, val_fraction: float, seed: int) -> tuple[np.ndarray, np.ndarray]:
    """Random train/validation index split of n examples, fixed by the seed."""
    order = np.random.default_rng(seed).permutation(n)
    n_val = int(round(n * val_fraction))
    return order[n_val:], order[:n_val]


def make_loader(tokenizer, texts: list[str], labels: np.ndarray, max_length: int,
                batch_size: int, shuffle: bool, seed: int) -> DataLoader:
    """Tokenize once and wrap in a DataLoader (single process, Windows-safe)."""
    # Pad every example to max_length so batches can be stacked without a custom collate.
    enc = tokenizer(texts, truncation=True, padding="max_length", max_length=max_length,
                    return_tensors="pt")
    dataset = TensorDataset(enc["input_ids"], enc["attention_mask"], torch.from_numpy(labels))
    # A seeded generator makes the shuffling order reproducible.
    generator = torch.Generator().manual_seed(seed)
    return DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, generator=generator)


def build_model(name: str, dropout: float, freeze_layers: int):
    """Load the pretrained encoder with an 18-output multi-label head, set dropout, freeze lower layers.

    LahjatBERT (bert_trainer._load_model): sets config.hidden_dropout_prob and
    attention_probs_dropout_prob to 0.3 AFTER the model is built. Wrong because the dropout
    layers read those values only when they are created, so the change has no effect and
    the model trains with the default 0.1. Fix: pass the dropout values to from_pretrained,
    so the layers are built with them.
    """
    model = AutoModelForSequenceClassification.from_pretrained(
        name,
        num_labels=len(DIALECTS),
        id2label=dict(enumerate(DIALECTS)),
        label2id={d: i for i, d in enumerate(DIALECTS)},
        problem_type="multi_label_classification",
        hidden_dropout_prob=dropout,
        attention_probs_dropout_prob=dropout,
    )
    # Freeze the first `freeze_layers` encoder layers (as LahjatBERT does); embeddings stay trainable.
    for layer in model.base_model.encoder.layer[:freeze_layers]:
        for p in layer.parameters():
            p.requires_grad = False
    return model


def validation_scores(model, loader: DataLoader, threshold: float, device: str) -> dict:
    """Macro/micro scores over all 18 dialects on the validation split.

    LahjatBERT (bert_trainer._multi_label_metrics): selects the best checkpoint by micro F1.
    Wrong for this project because the leaderboard and our reporting use macro F1, so
    micro selection can favour frequent dialects. Fix: select by macro F1.
    """
    model.eval()
    probs, golds = [], []
    with torch.no_grad():
        for input_ids, mask, labels in loader:
            logits = model(input_ids=input_ids.to(device), attention_mask=mask.to(device)).logits
            probs.append(torch.sigmoid(logits.float()).cpu().numpy())
            golds.append(labels.numpy())
    # Threshold the probabilities and score each dialect as a yes/no task.
    decisions = (np.concatenate(probs) >= threshold).astype(int)
    gold = np.concatenate(golds).astype(int)
    return multilabel_scores({d: gold[:, i].tolist() for i, d in enumerate(DIALECTS)},
                             {d: decisions[:, i].tolist() for i, d in enumerate(DIALECTS)})


def train(cfg: dict, device: str) -> dict:
    """Train with early stopping on validation macro F1; save the best checkpoint; return the log."""
    set_seed(cfg["seed"])
    run_dir = Path("results/runs") / cfg["run_name"]
    model_dir = run_dir / "model"

    # Data: load, split into train/validation, tokenize.
    texts, labels = load_records(Path(cfg["data"]), cfg["text_field"], cfg["limit"])
    train_idx, val_idx = split_train_val(len(texts), cfg["val_fraction"], cfg["seed"])
    tokenizer = AutoTokenizer.from_pretrained(cfg["model"])
    train_loader = make_loader(tokenizer, [texts[i] for i in train_idx], labels[train_idx],
                               cfg["max_length"], cfg["batch_size"], True, cfg["seed"])
    val_loader = make_loader(tokenizer, [texts[i] for i in val_idx], labels[val_idx],
                             cfg["max_length"], 64, False, cfg["seed"])

    # Model, optimizer (trainable parameters only) and warmup + linear-decay schedule.
    model = build_model(cfg["model"], cfg["dropout"], cfg["freeze_layers"]).to(device)
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                  lr=cfg["learning_rate"], weight_decay=cfg["weight_decay"])
    total_steps = len(train_loader) * cfg["epochs"]
    scheduler = get_linear_schedule_with_warmup(optimizer, cfg["warmup_steps"], total_steps)
    # Mixed precision: fp16 forward pass, with loss scaling to avoid underflow.
    use_amp = cfg["fp16"] and device == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

    log = {"config": cfg, "device": device, "n_train": len(train_idx), "n_val": len(val_idx),
           "epochs": []}
    best_f1, epochs_without_gain = -1.0, 0
    for epoch in range(1, cfg["epochs"] + 1):
        # One pass over the training data.
        model.train()
        start, running_loss = time.time(), 0.0
        for step, (input_ids, mask, y) in enumerate(train_loader, 1):
            with torch.autocast("cuda", dtype=torch.float16, enabled=use_amp):
                # problem_type=multi_label -> the model computes BCE-with-logits loss.
                loss = model(input_ids=input_ids.to(device), attention_mask=mask.to(device),
                             labels=y.to(device)).loss
            optimizer.zero_grad(set_to_none=True)
            scaler.scale(loss).backward()
            scaler.step(optimizer)
            scaler.update()
            scheduler.step()
            running_loss += loss.item()
            if step % 200 == 0:
                print(f"  epoch {epoch} step {step}/{len(train_loader)} loss {running_loss / step:.4f}")

        # Score on the validation split and log the epoch. The score used to pick the best
        # epoch is macro F1 by default; "micro" reproduces LahjatBERT's selection.
        scores = validation_scores(model, val_loader, cfg["threshold"], device)
        f1 = scores["micro_f1"] if cfg.get("selection_metric", "macro") == "micro" else scores["macro"]["f1"]
        log["epochs"].append({"epoch": epoch, "train_loss": running_loss / len(train_loader),
                              "val_macro_f1": scores["macro"]["f1"], "val_micro_f1": scores["micro_f1"],
                              "val_macro": scores["macro"], "seconds": round(time.time() - start)})
        print(f"epoch {epoch}: train loss {running_loss / len(train_loader):.4f}  "
              f"val macro F1 {scores['macro']['f1']:.2f}  micro F1 {scores['micro_f1']:.2f}")

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
    log["selection_metric"] = cfg.get("selection_metric", "macro")
    log["best_val_selection_score"] = best_f1
    return log


def main() -> None:
    """Train from a config, then score the best checkpoint once on the MLADI dev set."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N records, 1 epoch")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()

    # Load the config; tiny-subset mode overrides size and name so real runs are never overwritten.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    # Seed override: same config, new seed, run name ends in _seed<N> instead of the config's seed.
    if args.seed is not None:
        base = cfg["run_name"].rsplit("_seed", 1)[0]
        cfg.update(seed=args.seed, run_name=f"{base}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, epochs=1, warmup_steps=0,
                   run_name=cfg["run_name"] + f"_limit{args.limit}")
    if args.device == "cpu":
        print("WARNING: CUDA not available, training on CPU (very slow)")

    # Train, recording provenance alongside the results.
    started = time.time()
    log = train(cfg, args.device)
    log.update(git_commit=git_commit(), data_sha256=sha256(Path(cfg["data"])),
               python=platform.python_version(), torch=torch.__version__,
               config_file=str(args.config), total_seconds=round(time.time() - started))

    # Score the best checkpoint on the dev set (same settings as the leaderboard).
    run_dir = Path("results/runs") / cfg["run_name"]
    dev_scores, _ = evaluate_dev(str(run_dir / "model"), Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"),
                                 cfg["threshold"], args.device)
    log["dev"] = dev_scores
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    m = dev_scores["macro"]
    print(f"DEV  macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}  "
          f"| micro F1 {dev_scores['micro_f1']:.2f}  (best val epoch {log.get('best_epoch')})")


if __name__ == "__main__":
    sys.exit(main())
