"""Fine-tune a 7-9B decoder LLM as a multi-label dialect classifier with 4-bit QLoRA.

Same task, data, split, threshold and dev scoring as train_classifier.py (18 sigmoid outputs,
seeded 90/10 train/validation split, epoch chosen by validation macro F1, MLADI dev scored
once at the end). What differs, because a 7-9B model does not fit 8 GB of VRAM otherwise:
  - the base model is loaded in 4-bit NF4 and frozen (bitsandbytes)
  - LoRA adapters on every attention and MLP projection are trained, plus the new
    classification head (`score`), which is kept in full precision
  - gradient checkpointing, small micro-batches with gradient accumulation
  - bf16 compute instead of fp16 + loss scaling
  - batches are padded to their longest text, not to max_length (tweets are short)

Architectures with an AutoModelForSequenceClassification class (Qwen3, Gemma-2 / Fanar) use
it. Jais-2, Falcon-H1 and Cohere / Aya have none in transformers 5.18; for them the same
last-token head is built in src/training/decoder_head.py (and padding is forced to the right,
so Falcon-H1's Mamba layers never read padding before the real tokens).

Runs are resumable: every `checkpoint_minutes` (default 30) and after each epoch the adapter,
optimizer, scheduler, progress and RNG states are written to results/runs/<run_name>/checkpoint.pt.
Starting the same command again continues from there; the file is deleted when the run finishes.

Outputs in results/runs/<run_name>/:
  model/            LoRA adapter + classification head + tokenizer (gitignored)
  train_log.json    config, seed, git commit, data hash, per-epoch validation scores, dev scores

Usage:
  python -m src.training.train_lora_classifier --config configs/lora_real_only_qwen3.json
  python -m src.training.train_lora_classifier --config ... --limit 500     # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import gc
import json
import os
import platform
import random
import sys
import time
from pathlib import Path

import numpy as np
import torch
from peft import (LoraConfig, PeftModel, TaskType, get_peft_model, get_peft_model_state_dict,
                  prepare_model_for_kbit_training, set_peft_model_state_dict)
from transformers import (AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig,
                          get_linear_schedule_with_warmup)

from src.data.build_dataset import DIALECTS, git_commit, read_dev, sha256
from src.training import decoder_head
from src.training.decoder_head import LastTokenClassifier
from src.evaluation.evaluate_dev import predict_probabilities
from src.evaluation.metrics import multilabel_scores
from src.training.train_classifier import load_records, set_seed, split_train_val


def quant_config() -> BitsAndBytesConfig:
    """4-bit NF4 with double quantization and bf16 compute (QLoRA settings)."""
    return BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                              bnb_4bit_compute_dtype=torch.bfloat16, bnb_4bit_use_double_quant=True)


def load_base(name: str, pad_token_id: int):
    """Frozen 4-bit base model with an 18-output multi-label head (head in fp32)."""
    model = AutoModelForSequenceClassification.from_pretrained(
        name,
        num_labels=len(DIALECTS),
        id2label=dict(enumerate(DIALECTS)),
        label2id={d: i for i, d in enumerate(DIALECTS)},
        problem_type="multi_label_classification",
        quantization_config=quant_config(),
        dtype=torch.bfloat16,
        device_map={"": 0},
    )
    # Decoder models pool the last non-padding token, so the model must know the pad id.
    model.config.pad_token_id = pad_token_id
    model.score.to(torch.float32)
    return model


def load_tokenizer(name: str, right_padding: bool = False):
    """Tokenizer with a padding token (decoder tokenizers often lack one: reuse EOS)."""
    tokenizer = AutoTokenizer.from_pretrained(name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    if right_padding:
        tokenizer.padding_side = "right"
    return tokenizer


def adapter_state(model) -> dict:
    """Trainable weights (LoRA adapters + head) for a checkpoint."""
    if isinstance(model, LastTokenClassifier):
        return decoder_head.trainable_state(model)
    return get_peft_model_state_dict(model)


def load_adapter_state(model, state: dict) -> None:
    """Restore weights written by adapter_state."""
    if isinstance(model, LastTokenClassifier):
        decoder_head.load_trainable_state(model, state)
    else:
        set_peft_model_state_dict(model, state)


def batches(texts: list[str], labels: np.ndarray, batch_size: int, shuffle: bool, seed: int):
    """Yield (texts, labels) batches; a seeded generator fixes the shuffling order."""
    order = np.random.default_rng(seed).permutation(len(texts)) if shuffle else np.arange(len(texts))
    for start in range(0, len(order), batch_size):
        idx = order[start:start + batch_size]
        yield [texts[i] for i in idx], labels[idx]


def scores_on(model, tokenizer, texts: list[str], gold: np.ndarray, threshold: float,
              eval_batch_size: int) -> dict:
    """Macro/micro scores over all 18 dialects (validation split)."""
    with torch.autocast("cuda", dtype=torch.bfloat16):
        probs = predict_probabilities(model, tokenizer, texts, "cuda", batch_size=eval_batch_size)
    decisions = (probs >= threshold).astype(int)
    gold = gold.astype(int)
    return multilabel_scores({d: gold[:, i].tolist() for i, d in enumerate(DIALECTS)},
                             {d: decisions[:, i].tolist() for i, d in enumerate(DIALECTS)})


def save_checkpoint(path: Path, cfg: dict, model, optimizer, scheduler, state: dict) -> None:
    """Write adapter, optimizer, scheduler, progress and RNG states; atomic (temp file + rename)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"cfg": cfg, "state": state,
               "adapter": adapter_state(model),
               "optimizer": optimizer.state_dict(), "scheduler": scheduler.state_dict(),
               "rng": {"python": random.getstate(), "numpy": np.random.get_state(),
                       "torch": torch.get_rng_state(), "cuda": torch.cuda.get_rng_state_all()}}
    tmp = path.with_suffix(".tmp")
    torch.save(payload, tmp)
    os.replace(tmp, path)


def load_checkpoint(path: Path, cfg: dict, model, optimizer, scheduler) -> dict:
    """Restore a checkpoint written by save_checkpoint; refuse one made with a different config."""
    payload = torch.load(path, map_location="cpu", weights_only=False)
    if payload["cfg"] != cfg:
        sys.exit(f"{path} was written with a different config; delete it to start over.")
    load_adapter_state(model, payload["adapter"])
    optimizer.load_state_dict(payload["optimizer"])
    scheduler.load_state_dict(payload["scheduler"])
    rng = payload["rng"]
    random.setstate(rng["python"])
    np.random.set_state(rng["numpy"])
    torch.set_rng_state(rng["torch"])
    torch.cuda.set_rng_state_all(rng["cuda"])
    return payload["state"]


def train(cfg: dict) -> dict:
    """QLoRA training with epoch selection on validation macro F1; saves the best adapter."""
    set_seed(cfg["seed"])
    model_dir = Path("results/runs") / cfg["run_name"] / "model"

    # Data: load and split exactly as train_classifier.py does.
    texts, labels = load_records(Path(cfg["data"]), cfg["text_field"], cfg["limit"])
    train_idx, val_idx = split_train_val(len(texts), cfg["val_fraction"], cfg["seed"])
    train_texts, train_labels = [texts[i] for i in train_idx], labels[train_idx]
    val_texts, val_labels = [texts[i] for i in val_idx], labels[val_idx]

    # Model: 4-bit base + LoRA adapters; the classification head is trained in full.
    # Architectures without a library classification class get the equivalent custom head.
    custom = decoder_head.needs_custom_head(cfg["model"])
    tokenizer = load_tokenizer(cfg["model"], right_padding=custom)
    lora = LoraConfig(task_type=None if custom else TaskType.SEQ_CLS, r=cfg["lora_r"],
                      lora_alpha=cfg["lora_alpha"], lora_dropout=cfg["lora_dropout"],
                      target_modules=cfg["lora_target_modules"])
    if custom:
        model = decoder_head.build_for_training(cfg["model"], quant_config(), lora, len(DIALECTS))
    else:
        model = load_base(cfg["model"], tokenizer.pad_token_id)
        model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
        model = get_peft_model(model, lora)
    log_head = "custom last-token head (decoder_head.py)" if custom else "AutoModelForSequenceClassification"
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"trainable parameters: {n_trainable:,}")

    # Optimizer and warmup + linear decay over optimizer steps (after gradient accumulation).
    accum = cfg["grad_accum"]
    optimizer = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad],
                                  lr=cfg["learning_rate"], weight_decay=cfg["weight_decay"])
    micro_per_epoch = -(-len(train_texts) // cfg["micro_batch_size"])
    total_steps = -(-micro_per_epoch // accum) * cfg["epochs"]
    scheduler = get_linear_schedule_with_warmup(optimizer, int(cfg["warmup_ratio"] * total_steps), total_steps)

    log = {"config": cfg, "device": "cuda", "n_train": len(train_texts), "n_val": len(val_texts),
           "trainable_parameters": n_trainable, "head": log_head, "epochs": []}
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
            # BCE-with-logits in fp32; divided by accum so the update averages the micro-batches.
            loss = torch.nn.functional.binary_cross_entropy_with_logits(
                logits.float(), torch.from_numpy(by).to("cuda"))
            (loss / accum).backward()
            running_loss += loss.item()
            if step % accum == 0 or step == micro_per_epoch:
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                # Periodic checkpoint, only right after an optimizer step (no half-accumulated gradients).
                if time.time() - last_ckpt >= every:
                    save_checkpoint(ckpt_path, cfg, model, optimizer, scheduler, {
                        "epoch": epoch, "step": step, "running_loss": running_loss,
                        "seconds": seconds_before + time.time() - start, "log": log,
                        "best_f1": best_f1, "epochs_without_gain": epochs_without_gain})
                    last_ckpt = time.time()
                    print(f"  checkpoint saved at epoch {epoch} step {step}", flush=True)
            if step % 200 == 0:
                done = step - start_step
                rate = (time.time() - start) / done
                print(f"  epoch {epoch} step {step}/{micro_per_epoch} loss {running_loss / step:.4f} "
                      f"{rate:.2f} s/step, epoch eta {rate * (micro_per_epoch - step) / 60:.0f} min",
                      flush=True)

        # Validation macro F1 picks the epoch, as in train_classifier.py.
        scores = scores_on(model, tokenizer, val_texts, val_labels, cfg["threshold"], cfg["eval_batch_size"])
        f1 = scores["macro"]["f1"]
        epoch_seconds = seconds_before + time.time() - start
        log["epochs"].append({"epoch": epoch, "train_loss": running_loss / micro_per_epoch,
                              "val_macro_f1": f1, "val_micro_f1": scores["micro_f1"],
                              "val_macro": scores["macro"], "seconds": round(epoch_seconds),
                              "resumed_at_step": start_step or None})
        print(f"epoch {epoch}: train loss {running_loss / micro_per_epoch:.4f}  val macro F1 {f1:.2f}  "
              f"micro F1 {scores['micro_f1']:.2f}  ({epoch_seconds / 60:.1f} min)", flush=True)

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
        # End-of-epoch checkpoint: a resume starts the next epoch without redoing validation.
        save_checkpoint(ckpt_path, cfg, model, optimizer, scheduler, {
            "epoch": epoch + 1, "step": 0, "running_loss": 0.0, "seconds": 0.0, "log": log,
            "best_f1": best_f1, "epochs_without_gain": epochs_without_gain})
        if stop:
            print("early stopping")
            break
    # The run finished: the checkpoint (~0.5 GB) is no longer needed.
    ckpt_path.unlink(missing_ok=True)
    log["selection_metric"] = "macro"
    log["best_val_selection_score"] = best_f1
    log["peak_vram_mib"] = round(torch.cuda.max_memory_reserved() / 2**20)
    del model, optimizer
    gc.collect()
    torch.cuda.empty_cache()
    return log


def evaluate_saved(cfg: dict, threshold: float) -> dict:
    """Reload the saved best adapter on a fresh 4-bit base and score the MLADI dev set."""
    model_dir = Path("results/runs") / cfg["run_name"] / "model"
    custom = decoder_head.needs_custom_head(cfg["model"])
    tokenizer = load_tokenizer(str(model_dir), right_padding=custom)
    if custom:
        model = decoder_head.load_trained(cfg["model"], quant_config(), model_dir, len(DIALECTS))
    else:
        model = PeftModel.from_pretrained(load_base(cfg["model"], tokenizer.pad_token_id), model_dir)
    texts, gold = read_dev(Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"))
    with torch.autocast("cuda", dtype=torch.bfloat16):
        probs = predict_probabilities(model, tokenizer, texts, "cuda", batch_size=cfg["eval_batch_size"])
    decisions = (probs >= threshold).astype(int)
    pred = {d: decisions[:, DIALECTS.index(d)].tolist() for d in gold}
    return multilabel_scores(gold, pred)


def main() -> None:
    """Train from a config, then score the best adapter once on the MLADI dev set."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N records, 1 epoch")
    p.add_argument("--seed", type=int, default=None, help="override the config seed (run name gets _seedN)")
    args = p.parse_args()
    if not torch.cuda.is_available():
        sys.exit("QLoRA training needs CUDA (4-bit bitsandbytes); refusing to fall back to CPU.")

    # Config, seed override and tiny-subset mode, as in train_classifier.py.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.seed is not None:
        base = cfg["run_name"].rsplit("_seed", 1)[0]
        cfg.update(seed=args.seed, run_name=f"{base}_seed{args.seed}")
    if args.limit is not None:
        cfg.update(limit=args.limit, epochs=1, run_name=cfg["run_name"] + f"_limit{args.limit}")

    # Train, record provenance, then score the dev set once.
    started = time.time()
    log = train(cfg)
    log.update(git_commit=git_commit(), data_sha256=sha256(Path(cfg["data"])),
               python=platform.python_version(), torch=torch.__version__,
               config_file=str(args.config), train_seconds=round(time.time() - started))
    log["dev"] = evaluate_saved(cfg, cfg["threshold"])
    log["total_seconds"] = round(time.time() - started)
    run_dir = Path("results/runs") / cfg["run_name"]
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

    m = log["dev"]["macro"]
    print(f"DEV  macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}  "
          f"| micro F1 {log['dev']['micro_f1']:.2f}  (best val epoch {log.get('best_epoch')}, "
          f"peak VRAM {log['peak_vram_mib']} MiB)")


if __name__ == "__main__":
    main()
