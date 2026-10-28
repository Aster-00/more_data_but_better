#!/usr/bin/env bash
# SR01 extra seeds for the best LLMs (SD-003): Jais-2 (best on dev) and Aya (0.8 behind),
# seeds 43 and 44. Same configs as seed 42. Restartable like queue_sr01.sh.
# Logged to results/sentiment/queue_sr01.log (same log as the main SR01 queue).
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr01.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

say "SR01 extra-seeds queue start"
for tag in jais2 aya; do
  for seed in 43 44; do
    run=sr01_${tag}_seed${seed}
    if [ -f "$RUNS/$run/train_log.json" ]; then say "$run: done, skipping"; continue; fi
    # Refuse to start when another process holds the GPU (shared with other chats).
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6000 ] || { say "STOP: only ${free} MiB GPU memory free"; exit 1; }
    [ -f "$RUNS/$run/checkpoint.pt" ] && say "$run: resuming from checkpoint" || say "$run: start"
    if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr01_$tag.json --seed $seed \
        >> "$LOGS/$run.console.log" 2>&1; then
      say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
    else say "FAILED $run (rerun the queue to resume)"; fi
  done
done
say "DONE extra seeds"
