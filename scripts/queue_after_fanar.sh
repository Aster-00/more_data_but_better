#!/usr/bin/env bash
# Queue to run after the Fanar seed-42 QLoRA run: for Aya-Expanse-8B, Jais-2-8B and Falcon-H1-7B
# (custom last-token head, src/training/decoder_head.py), a 2,000-sentence smoke test, then the
# full real-only run (seed 42). A model whose smoke test fails, does not fit 8 GB, or is too slow
# (> MAX_S_PER_STEP) is skipped and the queue moves on. Logged to results/queue_after_fanar.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOG=results/queue_after_fanar.log
MAX_S_PER_STEP=3.0   # above this, one epoch takes > 5.5 h per epoch (6,569 micro-batches)
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
TRAIN="$PY -m src.training.train_lora_classifier"

# 0. Wait for the first queue to end (DONE or STOP line in its log).
say "waiting for the Fanar queue to finish"
until grep -qE "\] (DONE|STOP)" results/queue_after_qwen.log 2>/dev/null; do sleep 60; done
say "Fanar queue ended: $(grep -hE '\] (DONE|STOP)' results/queue_after_qwen.log | tail -1)"

for tag in aya jais2 falcon_h1; do
  cfg=configs/lora_real_only_$tag.json
  # 1. Smoke test: must finish, fit in 8192 MiB, and be fast enough.
  say "$tag: smoke test (2,000 sentences)"
  if ! $TRAIN --config "$cfg" --limit 2000 > results/lora_${tag}_limit2000.console.log 2>&1; then
    say "SKIP $tag: smoke test failed ($(grep -hE 'Error|error' results/lora_${tag}_limit2000.console.log | tail -1))"; continue; fi
  dev=$(grep -h "^DEV" results/lora_${tag}_limit2000.console.log)
  rate=$(grep -h "step 200/" results/lora_${tag}_limit2000.console.log | sed -n 's/.* \([0-9.]*\) s\/step.*/\1/p')
  vram=$(echo "$dev" | sed -n 's/.*peak VRAM \([0-9]*\) MiB.*/\1/p')
  say "$tag smoke: $dev; ${rate:-?} s/step"
  if [ "${vram:-99999}" -ge 8192 ]; then say "SKIP $tag: peak VRAM ${vram} MiB does not fit 8192 MiB"; continue; fi
  if ! $PY -c "import sys; sys.exit(0 if float('${rate:-99}') <= $MAX_S_PER_STEP else 1)"; then
    say "SKIP $tag: ${rate} s/step is above $MAX_S_PER_STEP (full run would take too long)"; continue; fi

  # 2. Full run (resumable: rerun the same command to continue from the last checkpoint).
  say "$tag: full run, seed 42"
  if $TRAIN --config "$cfg" > results/lora_real_only_${tag}_seed42.console.log 2>&1; then
    say "$tag done: $(grep -h '^DEV' results/lora_real_only_${tag}_seed42.console.log)"
  else
    say "FAILED $tag full run (rerun: $TRAIN --config $cfg)"
  fi
done
say "DONE"
