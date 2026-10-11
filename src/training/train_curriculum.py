"""Curriculum-learning (CL) version of train_classifier: train on a sequence of stages, easy first.

Stage construction follows LahjatBERT (data_utils.py, run_workflow.sh):
  cardinality  one stage per cardinality level (number of valid dialects), in a fixed order.
               Stage L = all texts with cardinality L, plus up to n = |stage L| texts from each
               earlier level (cardinality 1: n // 18 single-label texts per country).
               Cardinality-0 texts are in no stage.
  aldi         four cumulative stages over ALDi bins (4 = [0.77, 1], 3 = [0.44, 0.77),
               2 = [0.11, 0.44), 1 = [0, 0.11)); stage k = all texts in the first k bins of the order.
Each stage starts from the previous stage's model with a fresh optimizer and warmup + linear-decay
schedule, gets its own seeded 90/10 train/validation split, and trains `epochs_per_stage`
epochs (best epoch by validation score, as in train_classifier). The model after the last stage
is scored once on the MLADI dev set.

Everything else (model, dropout, frozen layers, lr, batch, threshold, selection metric) comes
from the config exactly as in train_classifier.

Usage:
  python -m src.training.train_curriculum --config configs/cl_cardinality_real_only.json
  python -m src.training.train_curriculum --config configs/cl_aldi_real_only.json --limit 2000
  python -m src.training.train_curriculum --config configs/cl_aldi_real_only.json --dry-run
"""
from __future__ import annotations

import argparse
import copy
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, get_linear_schedule_with_warmup

from src.data.build_dataset import DIALECTS, git_commit, sha256
from src.evaluation.evaluate_dev import evaluate as evaluate_dev
from src.training.train_classifier import (build_model, make_loader, set_seed, split_train_val,
                                           strip_diacritics, train_one_epoch, validation_scores)

# Lower bound of each ALDi bin (LahjatBERT data_utils.ALDI_THRESHOLDS).
ALDI_BIN_FLOORS = {4: 0.77, 3: 0.44, 2: 0.11, 1: 0.0}


def load_records(path: Path, text_field: str, limit: int | None, remove_diacritics: bool) -> list[dict]:
    """Read the JSONL dataset; keep text, 18-dim label vector, cardinality and ALDi bin."""
    records = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            # Tiny-subset mode: only the first `limit` records.
            if limit is not None and i >= limit:
                break
            r = json.loads(line)
            labels = [r["labels"][d] for d in DIALECTS]
            aldi_bin = next(b for b, floor in ALDI_BIN_FLOORS.items() if r["aldi_score"] >= floor)
            records.append({"text": strip_diacritics(r[text_field]) if remove_diacritics else r[text_field],
                            "labels": labels, "cardinality": sum(labels), "aldi_bin": aldi_bin,
                            "country": [d for d, v in zip(DIALECTS, labels) if v]})
    return records


def balance_countries(records: list[dict], n_per_country: int, seed: int) -> list[int]:
    """n_per_country single-label texts per country (with replacement only when a country has too few).

    Same as LahjatBERT's balance_countries; countries with no single-label text are skipped.
    """
    if n_per_country < 1:
        return []
    picked = []
    for d in DIALECTS:
        pool = [i for i, r in enumerate(records) if r["cardinality"] == 1 and r["country"] == [d]]
        if pool:
            rng = np.random.default_rng(seed)
            picked += rng.choice(pool, n_per_country, replace=len(pool) < n_per_country).tolist()
    return picked


def cardinality_stage(records: list[dict], level: int, order: list[int], seed: int) -> list[int]:
    """Indices of the cardinality stage `level` (LahjatBERT create_cl_cardinality_stage).

    LahjatBERT draws the n texts of an earlier level WITH replacement when that level has more
    than n texts (sklearn resample(replace=True)); kept as is so the stages match theirs.
    """
    by_level = {L: [i for i, r in enumerate(records) if r["cardinality"] == L] for L in order}
    stage = list(by_level[level])
    n = len(stage)
    for earlier in order[:order.index(level)]:
        if earlier == 1:
            stage += balance_countries(records, n // 18, seed)
        elif len(by_level[earlier]) > n:
            stage += np.random.default_rng(seed).choice(by_level[earlier], n, replace=True).tolist()
        else:
            stage += by_level[earlier]
    return stage


def build_stages(records: list[dict], cl: dict, seed: int) -> list[tuple[int, list[int]]]:
    """(stage id, record indices) for every stage, in training order."""
    order = cl["order"]
    if cl["method"] == "cardinality":
        return [(L, cardinality_stage(records, L, order, seed)) for L in order]
    if cl["method"] == "aldi":
        # Cumulative: stage k contains the bins order[0..k].
        return [(b, [i for i, r in enumerate(records) if r["aldi_bin"] in order[:k + 1]])
                for k, b in enumerate(order)]
    raise ValueError(f"unknown curriculum method {cl['method']!r}")


def train(cfg: dict, device: str, dry_run: bool = False) -> dict:
    """Train stage by stage; save the final model; return the log."""
    set_seed(cfg["seed"])
    cl = cfg["curriculum"]
    run_dir = Path("results/runs") / cfg["run_name"]
    model_dir = run_dir / "model"

    # Data and stages.
    records = load_records(Path(cfg["data"]), cfg["text_field"], cfg["limit"],
                           cfg.get("strip_diacritics", False))
    stages = [(sid, idx) for sid, idx in build_stages(records, cl, cfg["seed"]) if idx]
    for sid, idx in stages:
        print(f"stage {sid}: {len(idx)} texts")
    log = {"config": cfg, "device": device, "n_records": len(records),
           "stage_sizes": {str(sid): len(idx) for sid, idx in stages}, "stages": []}
    if dry_run:
        return log

    tokenizer = AutoTokenizer.from_pretrained(cfg["model"])
    model = build_model(cfg["model"], cfg["dropout"], cfg["freeze_layers"]).to(device)
    use_amp = cfg["fp16"] and device == "cuda"
    labels = np.asarray([r["labels"] for r in records], dtype=np.float32)
    texts = [r["text"] for r in records]

    for sid, idx in stages:
        # Per-stage split, loaders, and a fresh optimizer + schedule (as LahjatBERT's per-stage Trainer).
        idx = np.asarray(idx)
        tr, va = split_train_val(len(idx), cfg["val_fraction"], cfg["seed"])
        train_loader = make_loader(tokenizer, [texts[i] for i in idx[tr]], labels[idx[tr]],
                                   cfg["max_length"], cfg["batch_size"], True, cfg["seed"])
        val_loader = make_loader(tokenizer, [texts[i] for i in idx[va]], labels[idx[va]],
                                 cfg["max_length"], 64, False, cfg["seed"])
        optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                      lr=cfg["learning_rate"], weight_decay=cfg["weight_decay"])
        scheduler = get_linear_schedule_with_warmup(optimizer, cfg["warmup_steps"],
                                                    len(train_loader) * cl["epochs_per_stage"])
        scaler = torch.amp.GradScaler("cuda", enabled=use_amp)

        # Train the stage; keep the best epoch's weights (in memory) as the stage's model.
        stage_log = {"stage": sid, "n_train": len(tr), "n_val": len(va), "epochs": []}
        best_f1, best_state = -1.0, None
        for epoch in range(1, cl["epochs_per_stage"] + 1):
            start = time.time()
            train_loss = train_one_epoch(model, train_loader, optimizer, scheduler, scaler, use_amp,
                                         device, epoch)
            scores = validation_scores(model, val_loader, cfg["threshold"], device)
            f1 = scores["micro_f1"] if cfg.get("selection_metric", "macro") == "micro" else scores["macro"]["f1"]
            stage_log["epochs"].append({"epoch": epoch, "train_loss": train_loss,
                                        "val_macro_f1": scores["macro"]["f1"],
                                        "val_micro_f1": scores["micro_f1"],
                                        "seconds": round(time.time() - start)})
            print(f"stage {sid} epoch {epoch}: train loss {train_loss:.4f}  "
                  f"val macro F1 {scores['macro']['f1']:.2f}  micro F1 {scores['micro_f1']:.2f}")
            if f1 > best_f1:
                best_f1, stage_log["best_epoch"] = f1, epoch
                # Only needed when the stage has more than one epoch to choose from.
                if cl["epochs_per_stage"] > 1:
                    best_state = copy.deepcopy({k: v.cpu() for k, v in model.state_dict().items()})
        if best_state is not None:
            model.load_state_dict(best_state)
        log["stages"].append(stage_log)

    # The model after the last stage is the run's model.
    model.save_pretrained(model_dir)
    tokenizer.save_pretrained(model_dir)
    log["selection_metric"] = cfg.get("selection_metric", "macro")
    return log


def main() -> None:
    """Train a curriculum from a config, then score the final model once on the MLADI dev set."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N records")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    p.add_argument("--dry-run", action="store_true", help="only build the stages and print their sizes")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    # Seed override and tiny-subset mode, as in train_classifier.
    if args.seed is not None:
        base = cfg["run_name"].rsplit("_seed", 1)[0]
        cfg.update(seed=args.seed, run_name=f"{base}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, warmup_steps=0, run_name=cfg["run_name"] + f"_limit{args.limit}")
    if args.device == "cpu" and not args.dry_run:
        print("WARNING: CUDA not available, training on CPU (very slow)")

    started = time.time()
    log = train(cfg, args.device, args.dry_run)
    if args.dry_run:
        print(f"total stage texts: {sum(log['stage_sizes'].values())}")
        return
    log.update(git_commit=git_commit(), data_sha256=sha256(Path(cfg["data"])),
               python=platform.python_version(), torch=torch.__version__,
               config_file=str(args.config), total_seconds=round(time.time() - started))

    # Score the final model on the dev set (same settings as the leaderboard).
    run_dir = Path("results/runs") / cfg["run_name"]
    dev_scores, _ = evaluate_dev(str(run_dir / "model"), Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"),
                                 cfg["threshold"], args.device)
    log["dev"] = dev_scores
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    m = dev_scores["macro"]
    print(f"DEV  macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}  "
          f"| micro F1 {dev_scores['micro_f1']:.2f}")


if __name__ == "__main__":
    sys.exit(main())
