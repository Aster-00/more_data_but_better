#!/usr/bin/env bash
# SR00-EnPrompt / SR00-ArPrompt: zero-shot EESA sentiment with the 5 roster LLMs, no training (Ammar 2026-11-18).
# Usage: bash queue_sr00_eesa.sh
#   0. wait until the SG04 queue (SR09-random-EESA) has ended and 6,500 MiB of GPU memory are free
#   1. smoke test: Qwen3, English prompt, 30 texts per split (_limit30 folder); stop if it fails
#   2. per model (Qwen3, Aya, Jais-2, Fanar, Falcon-H1 last: slowest), English then Arabic prompt, dev + test
# Restartable: finished runs are skipped; a folder without train_log.json (aborted) is moved to runs/_aborted/
# (no model is stored in it, only partial predictions). Log: results/sentiment/queue_sr00_eesa.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr00_eesa.log
MODELS="qwen3 aya jais2 fanar falcon_h1"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 3 h) for the SG04 queue to end, then for 6,500 MiB of free GPU memory.
wait_gpu() {
  local i free
  for i in $(seq 1 36); do
    if ! grep -q "ALL DONE" results/sentiment/queue_sg04_eesa.log && \
       ps -ef | grep -q "[q]ueue_sg04_eesa"; then
      [ "$i" = 1 ] && say "waiting for the SG04 queue to finish"; sleep 300; continue
    fi
    sleep 60   # Windows frees a model's memory late
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6500 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 240
  done
  say "STOP: GPU busy for 3 h"; exit 1
}

# One zero-shot run (config name, optional extra args).
run_one() {
  local cfg=$1; shift
  local run
  run=$(sed -n 's/.*"run_name": "\([^"]*\)".*/\1/p' "configs/sentiment/$cfg.json")
  [ "${1:-}" = "--limit" ] && run="${run}_limit$2"
  [ -f "$RUNS/$run/train_log.json" ] && return 0
  if [ -d "$RUNS/$run" ]; then
    mkdir -p "$RUNS/_aborted"; mv "$RUNS/$run" "$RUNS/_aborted/${run}_$(date +%Y%m%d%H%M%S)"
    say "NOTE $run: aborted folder moved to $RUNS/_aborted/"
  fi
  wait_gpu
  say "$run: start"
  if $PY -m src.sentiment.zero_shot --config "configs/sentiment/$cfg.json" "$@" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1 | sed 's/  (best epoch.*//')"
    say "$run: $(grep -h '^TEST' "$LOGS/$run.console.log" | tail -1 | sed 's/  (best epoch.*//') | $(grep -h '^peak VRAM' "$LOGS/$run.console.log")"
    return 0
  fi
  say "FAILED $run (see $LOGS/$run.console.log)"; return 1
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
run_one sr00en_eesa_qwen3 --limit 30 || { say "STOP: smoke test failed"; exit 1; }
for m in $MODELS; do
  for p in en ar; do run_one "sr00${p}_eesa_$m"; done
done
say "ALL DONE"
