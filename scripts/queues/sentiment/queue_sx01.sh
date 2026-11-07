#!/usr/bin/env bash
# SX01 queue (D-028): trained SR01-SR07 classifiers scored on the Mawqif and EESA test sets, no training.
# GPU order (Ammar, 2026-11-07): SR12/SR13 queue, then SV01 steering extraction, then this queue.
# Starts only after SV01 logged its extraction as done AND the GPU has stayed free for 10 minutes.
# BERTs first (one process), then one process per LLM run, because reloading 4-bit bases in one
# process has exhausted the Windows page file before.
# Restartable: a run with scores.json is skipped.
# Log: results/sentiment/queue_sx01.log; console output in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
CFG=configs/sentiment/cross_eval_sx01.json
OUT=results/sentiment/cross_eval
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sx01.log
SV01_LOG=results/sentiment/steering/queue_sv01.log
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait until the GPU has at least 6000 MiB free for $1 minutes in a row.
gpu_free_for() {
  ok=0
  while [ "$ok" -lt "$1" ]; do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    if [ "$free" -ge 6000 ]; then ok=$((ok + 1)); else ok=0; fi
    sleep 60
  done
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
say "waiting for SV01 extraction to finish"
until grep -q -E 'SV01 extraction (done|already done)' "$SV01_LOG"; do sleep 60; done
say "SV01 extraction finished; waiting for the GPU to stay free for 10 min"
gpu_free_for 10

# BERTs: 357 runs in one process.
say "BERTs: start"
if $PY -m src.sentiment.cross_eval --config "$CFG" --family bert > "$LOGS/sx01_bert.console.log" 2>&1; then
  say "BERTs: done"
else say "FAILED BERTs (see $LOGS/sx01_bert.console.log)"; exit 1; fi
$PY -m src.sentiment.summarize_runs >> "$LOG" 2>&1

# LLMs: SR01 and SR02 first, then SR03. The run list is sorted by name.
fails=0
for run in $($PY -m src.sentiment.cross_eval --config "$CFG" --list llm | tr -d '\r'); do
  if [ -f "$OUT/$run/scores.json" ]; then continue; fi
  gpu_free_for 1
  say "$run: start"
  if $PY -m src.sentiment.cross_eval --config "$CFG" --run "$run" > "$LOGS/sx01_$run.console.log" 2>&1; then
    say "$(grep -h "^$run: " "$LOGS/sx01_$run.console.log" | tail -1)"
  else say "FAILED $run (see $LOGS/sx01_$run.console.log)"; fails=$((fails + 1)); fi
done
$PY -m src.sentiment.summarize_runs >> "$LOG" 2>&1
say "DONE ($fails failed)"
