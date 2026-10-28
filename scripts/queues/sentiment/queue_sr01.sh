#!/usr/bin/env bash
# SR01 queue (sentiment, real only, S1; decision SD-003). Order:
#   1. BERT models, seeds 42/43/44 (~3 min each)
#   2. 300-text smoke test for each LLM (must finish and fit 8192 MiB, or the model is skipped)
#   3. full runs, seed 42: jais2, qwen3 (afternoon), then fanar, aya, falcon_h1 (overnight)
# Restartable: finished runs are skipped, interrupted LLM runs resume from checkpoint.pt.
# Logged to results/sentiment/queue_sr01.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr01.log
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Refuse to start a GPU job when another process holds the GPU (shared with other chats).
gpu_free() {
  free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
  [ "$free" -ge 6000 ] || { say "STOP: only ${free} MiB GPU memory free"; exit 1; }
}

say "SR01 queue start"
# 1. BERT models, 3 seeds.
for tag in marbertv2 arabertv02_twitter marbert; do
  for seed in 42 43 44; do
    run=sr01_${tag}_seed${seed}
    if [ -f "$RUNS/$run/train_log.json" ]; then say "$run: done, skipping"; continue; fi
    gpu_free; say "$run: start"
    if $PY -m src.sentiment.train_classifier --config configs/sentiment/sr01_$tag.json --seed $seed \
        > "$LOGS/$run.console.log" 2>&1; then
      say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
    else say "FAILED $run (see $LOGS/$run.console.log)"; fi
  done
done

# 2. LLM smoke tests; a model that fails or does not fit is left out of step 3.
ok=""
for tag in jais2 qwen3 fanar aya falcon_h1; do
  run=sr01_${tag}_seed42_limit300
  if [ -f "$RUNS/$run/train_log.json" ] || [ -f "$RUNS/sr01_${tag}_seed42/train_log.json" ]; then ok="$ok $tag"; continue; fi
  gpu_free; say "$tag: smoke test (300 texts)"
  if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr01_$tag.json --limit 300 \
      > "$LOGS/$run.console.log" 2>&1; then
    vram=$(sed -n 's/^peak VRAM \([0-9]*\) MiB.*/\1/p' "$LOGS/$run.console.log")
    say "$tag smoke: $(grep -h '^DEV' "$LOGS/$run.console.log"); peak VRAM ${vram:-?} MiB"
    if [ "${vram:-99999}" -lt 8192 ]; then ok="$ok $tag"; else say "SKIP $tag: does not fit 8192 MiB"; fi
  else say "SKIP $tag: smoke test failed ($(grep -hE 'Error' "$LOGS/$run.console.log" | tail -1))"; fi
done

# 3. Full LLM runs, seed 42, in schedule order (appending, so a resumed run keeps its earlier log).
for tag in $ok; do
  run=sr01_${tag}_seed42
  if [ -f "$RUNS/$run/train_log.json" ]; then say "$run: done, skipping"; continue; fi
  gpu_free
  [ -f "$RUNS/$run/checkpoint.pt" ] && say "$run: resuming from checkpoint" || say "$run: start"
  if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr01_$tag.json \
      >> "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
  else say "FAILED $run (rerun the queue to resume)"; fi
done
say "DONE"
