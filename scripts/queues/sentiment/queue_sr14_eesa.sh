#!/usr/bin/env bash
# SR14: RAG few-shot EESA sentiment with the 5 roster LLMs, no training (Ammar 2026-11-21).
# Dev sweep only: k = 4, 8, 16 per (retriever, LLM); test runs later, once, with the k chosen on dev.
# Usage: bash scripts/queues/sentiment/queue_sr14_eesa.sh
#   Retrievers in order: openai (numpy; FAISS identical), bm25, e5 numpy, e5 faiss.
#   Per retriever, LLMs Qwen3, Aya, Jais-2, Fanar, Falcon-H1 (slowest last).
# Restartable: a k whose folder has train_log.json is skipped; a folder without it (aborted) is moved
# to runs/_aborted/ and that k reruns. Log: results/sentiment/queue_sr14_eesa.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr14_eesa.log
MODELS="qwen3 aya jais2 fanar falcon_h1"
RETRIEVERS="openai_numpy bm25 e5_numpy e5_faiss"
KS="4 8 16"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 3 h) for 6,500 MiB of free GPU memory.
wait_gpu() {
  local i free
  for i in $(seq 1 36); do
    sleep 30   # Windows frees a model's memory late
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6500 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 270
  done
  say "STOP: GPU busy for 3 h"; exit 1
}

# One (retriever, LLM) config: run the k values that have no finished folder yet.
run_one() {
  local prefix=$1 k todo="" d
  for k in $KS; do
    d="$RUNS/${prefix}_k${k}_dev"
    [ -f "$d/train_log.json" ] && continue
    if [ -d "$d" ]; then
      mkdir -p "$RUNS/_aborted"; mv "$d" "$RUNS/_aborted/${prefix}_k${k}_dev_$(date +%Y%m%d%H%M%S)"
      say "NOTE ${prefix}_k${k}_dev: aborted folder moved to $RUNS/_aborted/"
    fi
    todo="$todo $k"
  done
  [ -z "$todo" ] && return 0
  wait_gpu
  say "$prefix: start, k =$todo"
  if $PY -m src.sentiment.rag_few_shot --config "configs/sentiment/$prefix.json" --split dev --ks $todo \
      >> "$LOGS/$prefix.dev.console.log" 2>&1; then
    grep -h '^DEV k=' "$LOGS/$prefix.dev.console.log" | tail -n "$(echo $todo | wc -w)" | while read -r l; do say "$prefix: $l"; done
    return 0
  fi
  say "FAILED $prefix (see $LOGS/$prefix.dev.console.log)"; return 1
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for r in $RETRIEVERS; do
  for m in $MODELS; do run_one "sr14_eesa_${r}_${m}"; done
done
say "ALL DONE"
