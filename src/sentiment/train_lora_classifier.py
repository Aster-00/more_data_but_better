"""Fine-tune a 7-9B decoder LLM as a 3-class sentiment classifier with 4-bit QLoRA.

Same setup as the dialect track's src/training/train_lora_classifier.py (4-bit NF4 frozen
base, LoRA on every attention and MLP projection, fp32 last-token head, gradient
checkpointing, bf16, resumable checkpoints, custom head from decoder_head.py for Jais-2,
Falcon-H1 and Aya). Differences, because the task is single-label sentiment:
  - 3 outputs (NEG/NEU/POS) with cross-entropy loss, prediction = argmax
  - the epoch is chosen by macro F1 on the S1 dev split; no extra validation split
  - after training, dev and the official test set are scored once (test never used for choices)
Conditions 2/3: an optional `synthetic_data` file (kept separate, source "synthetic") is appended
to the real training texts; dev and test stay real only.

Outputs in results/sentiment/runs/<run_name>/:
  model/                    LoRA adapter + classification head + tokenizer (gitignored)
  train_log.json            config, seed, git commit, data hashes, per-epoch dev scores, dev/test scores
  {dev,test}_predictions.jsonl  per-text gold, prediction and class probabilities

Usage:
  python -m src.sentiment.train_lora_classifier --config configs/sentiment/sr01_qwen3.json
  python -m src.sentiment.train_lora_classifier --config ... --limit 300      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import gc
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch
from peft import LoraConfig, PeftModel, TaskType, get_peft_model
from transformers import AutoModelForSequenceClassification, get_linear_schedule_with_warmup

from src.data.build_dataset import git_commit, sha256
from src.sentiment.build_dataset import SENTIMENTS
from src.sentiment.common import (ID2LABEL, LABEL2ID, evaluate_splits, load_split, predict_logits,
                                  print_scores, sentiment_scores)
from src.training import decoder_head
from src.training.train_classifier import set_seed
from src.training.train_lora_classifier import (batches, load_checkpoint, load_tokenizer, quant_config,
                                                save_checkpoint)

RUNS_DIR = Path("results/sentiment/runs")


def load_base(name: str, pad_token_id: int):
    """Frozen 4-bit base model with a 3-class single-label head (head in fp32)."""
    model = AutoModelForSequenceClassification.from_pretrained(
        name, num_labels=len(SENTIMENTS), id2label=ID2LABEL, label2id=LABEL2ID,
        problem_type="single_label_classification", quantization_config=quant_config(),
        dtype=torch.bfloat16, device_map={"": 0})
    # Decoder models pool the last non-padding token, so the model must know the pad id.
    model.config.pad_token_id = pad_token_id
    model.score.to(torch.float32)
    return model


def dev_scores(model, tokenizer, texts: list[str], gold: np.ndarray, cfg: dict) -> dict:
    """Dev-split scores of the current model (bf16 inference)."""
    with torch.autocast("cuda", dtype=torch.bfloat16):
        logits = predict_logits(model, tokenizer, texts, cfg["max_length"], "cuda", cfg["eval_batch_size"])
    return sentiment_scores(gold, logits.argmax(-1))


def train(cfg: dict) -> dict:
    """QLoRA training with epoch selection on dev macro F1; saves the best adapter."""
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

    # Model: 4-bit base + LoRA adapters; the classification head is trained in full.
    # Architectures without a library classification class get the equivalent custom head.
    custom = decoder_head.needs_custom_head(cfg["model"])
    tokenizer = load_tokenizer(cfg["model"], right_padding=custom)
    lora = LoraConfig(task_type=None if custom else TaskType.SEQ_CLS, r=cfg["lora_r"],
                      lora_alpha=cfg["lora_alpha"], lora_dropout=cfg["lora_dropout"],
                      target_modules=cfg["lora_target_modules"])
    if custom:
        model = decoder_head.build_for_training(cfg["model"], quant_config(), lora, len(SENTIMENTS),
                                                cfg.get("embeddings_16bit", False))
    else:
        model = load_base(cfg["model"], tokenizer.pad_token_id)
        model = decoder_head.prepare_kbit(model, cfg.get("embeddings_16bit", False))
        model = get_peft_model(model, lora)
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"trainable parameters: {n_trainable:,}", flush=True)

    # Optimizer and warmup + linear decay over optimizer steps (after gradient accumulation).
    accum = cfg["grad_accum"]
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                  lr=cfg["learning_rate"], weight_decay=cfg["weight_decay"])
    micro_per_epoch = -(-len(train_texts) // cfg["micro_batch_size"])
    total_steps = -(-micro_per_epoch // accum) * cfg["epochs"]
    scheduler = get_linear_schedule_with_warmup(optimizer, int(cfg["warmup_ratio"] * total_steps), total_steps)

    log = {"config": cfg, "device": "cuda", "n_train": len(train_texts), "n_train_real": n_real,
           "n_train_synthetic": len(train_texts) - n_real, "n_dev": len(dev_texts),
           "trainable_parameters": n_trainable,
           "head": "custom last-token head (decoder_head.py)" if custom else "AutoModelForSequenceClassification",
           "epochs": []}
    state = {"epoch": 1, "step": 0, "running_loss": 0.0, "seconds": 0.0, "log": log,
             "best_f1": -1.0, "epochs_without_gain": 0}

    # Resume from the last periodic checkpoint if one exists (e.g. the process was killed).
    ckpt_path = model_dir.parent / "checkpoint.pt"
    if ckpt_path.exists():
        state = load_checkpoint(ckpt_path, cfg, model, optimizer, scheduler)
        log = state["log"]
        print(f"resumed from checkpoint: epoch {state['epoch']} step {state['step']}", flush=True)
    best_f1, epochs_without_gain = state["best_f1"], state["epochs_without_gain"]
    every = cfg.get("checkpoint_minutes", 30) * 60

    for epoch in range(state["epoch"], cfg["epochs"] + 1):
        # One pass over the training data; the seed + epoch fixes the shuffling order.
        model.train()
        resumed = epoch == state["epoch"]
        start_step = state["step"] if resumed else 0
        running_loss = state["running_loss"] if resumed else 0.0
        seconds_before = state["seconds"] if resumed else 0.0
        start = last_ckpt = time.time()
        optimizer.zero_grad(set_to_none=True)
        for step, (bt, by) in enumerate(batches(train_texts, train_labels, cfg["micro_batch_size"],
                                                True, cfg["seed"] + epoch), 1):
            # Batches already trained before the checkpoint are skipped (same order, same seed).
            if step <= start_step:
                continue
            enc = tokenizer(bt, truncation=True, padding=True, max_length=cfg["max_length"],
                            return_tensors="pt").to("cuda")
            with torch.autocast("cuda", dtype=torch.bfloat16):
                logits = model(**enc).logits
            # Cross-entropy in fp32; divided by accum so the update averages the micro-batches.
            loss = torch.nn.functional.cross_entropy(logits.float(), torch.from_numpy(by).to("cuda"))
            (loss / accum).backward()
            running_loss += loss.item()
            if step % accum == 0 or step == micro_per_epoch:
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                # Periodic checkpoint, only right after an optimizer step.
                if time.time() - last_ckpt >= every:
                    save_checkpoint(ckpt_path, cfg, model, optimizer, scheduler, {
                        "epoch": epoch, "step": step, "running_loss": running_loss,
                        "seconds": seconds_before + time.time() - start, "log": log,
                        "best_f1": best_f1, "epochs_without_gain": epochs_without_gain})
                    last_ckpt = time.time()
                    print(f"  checkpoint saved at epoch {epoch} step {step}", flush=True)
            if step % 200 == 0:
                rate = (time.time() - start) / (step - start_step)
                print(f"  epoch {epoch} step {step}/{micro_per_epoch} loss {running_loss / step:.4f} "
                      f"{rate:.2f} s/step, epoch eta {rate * (micro_per_epoch - step) / 60:.0f} min", flush=True)

        # Dev macro F1 picks the epoch.
        scores = dev_scores(model, tokenizer, dev_texts, dev_labels, cfg)
        f1 = scores["macro"]["f1"]
        epoch_seconds = seconds_before + time.time() - start
        log["epochs"].append({"epoch": epoch, "train_loss": running_loss / micro_per_epoch, "dev_macro_f1": f1,
                              "dev_accuracy": scores["accuracy"], "dev_f1_pn": scores["f1_pn"],
                              "seconds": round(epoch_seconds), "resumed_at_step": start_step or None})
        print(f"epoch {epoch}: train loss {running_loss / micro_per_epoch:.4f}  dev macro F1 {f1:.2f}  "
              f"acc {scores['accuracy']:.2f}  ({epoch_seconds / 60:.1f} min)", flush=True)

        # Keep the best adapter on disk; stop after `patience` epochs without improvement.
        stop = False
        if f1 > best_f1:
            best_f1, epochs_without_gain = f1, 0
            if custom:
                decoder_head.save(model, model_dir)
            else:
                model.save_pretrained(model_dir)
            tokenizer.save_pretrained(model_dir)
            log["best_epoch"] = epoch
        else:
            epochs_without_gain += 1
            stop = epochs_without_gain >= cfg["patience"]
        # End-of-epoch checkpoint: a resume starts the next epoch without redoing the dev pass.
        save_checkpoint(ckpt_path, cfg, model, optimizer, scheduler, {
            "epoch": epoch + 1, "step": 0, "running_loss": 0.0, "seconds": 0.0, "log": log,
            "best_f1": best_f1, "epochs_without_gain": epochs_without_gain})
        if stop:
            print("early stopping")
            break
    # The run finished: the resume checkpoint is no longer needed (the best adapter is in model/).
    ckpt_path.unlink(missing_ok=True)
    log["best_dev_macro_f1"] = best_f1
    log["peak_vram_mib"] = round(torch.cuda.max_memory_reserved() / 2**20)
    del model, optimizer
    gc.collect()
    torch.cuda.empty_cache()
    return log


def load_saved(cfg: dict):
    """Fresh 4-bit base + the saved best adapter and head, plus its tokenizer."""
    model_dir = RUNS_DIR / cfg["run_name"] / "model"
    custom = decoder_head.needs_custom_head(cfg["model"])
    tokenizer = load_tokenizer(str(model_dir), right_padding=custom)
    if custom:
        model = decoder_head.load_trained(cfg["model"], quant_config(), model_dir, len(SENTIMENTS))
    else:
        model = PeftModel.from_pretrained(load_base(cfg["model"], tokenizer.pad_token_id), model_dir)
    return model, tokenizer


def main() -> None:
    """Train from a config, then score the best adapter on dev and (once) on test."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts per split, 1 epoch")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    args = p.parse_args()
    if not torch.cuda.is_available():
        sys.exit("QLoRA training needs CUDA (4-bit bitsandbytes); refusing to fall back to CPU.")

    # Config, seed override and tiny-subset mode, as in train_classifier.py.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.seed is not None:
        cfg.update(seed=args.seed, run_name=f"{cfg['run_name'].rsplit('_seed', 1)[0]}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, epochs=1, run_name=cfg["run_name"] + f"_limit{args.limit}")
    run_dir = RUNS_DIR / cfg["run_name"]
    if (run_dir / "train_log.json").exists():
        sys.exit(f"{run_dir} already has a finished run; rerun under a new name.")

    # Train, then reload the best adapter on a fresh base and score dev and test.
    started = time.time()
    log = train(cfg)
    log["train_seconds"] = round(time.time() - started)
    model, tokenizer = load_saved(cfg)

    def predict(texts: list[str]) -> np.ndarray:
        """Logits of the saved model, bf16 inference."""
        with torch.autocast("cuda", dtype=torch.bfloat16):
            return predict_logits(model, tokenizer, texts, cfg["max_length"], "cuda", cfg["eval_batch_size"])

    log.update(evaluate_splits(predict, cfg, run_dir))

    # Provenance alongside the results.
    log.update(git_commit=git_commit(), python=platform.python_version(), torch=torch.__version__,
               data_sha256={s: sha256(Path(cfg[f"{s}_data"])) for s in ("train", "synthetic", "dev", "test")
                            if cfg.get(f"{s}_data")},
               config_file=str(args.config), total_seconds=round(time.time() - started))
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print_scores(log)
    print(f"peak VRAM {log['peak_vram_mib']} MiB", flush=True)


if __name__ == "__main__":
    main()
