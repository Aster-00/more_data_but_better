#!/usr/bin/env bash
# Sentiment repair tests on SG04 (D-026, test-contaminated like SR07): no new generation.
#   SR12  SR11 without the NEU pairs (whole POS/NEG pairs, 1,600 texts)
#   SR13  SR12 + the NEG sides of public jab and personal remark (2,600 texts)
# 3 BERTs x seeds 42/43/44, interleaved so a partial queue still has matched runs.
# Restartable: finished runs are skipped; an aborted folder is left untouched and reported.
# Log: results/sentiment/queue_sr12_no_neu.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr12_no_neu.log
BERTS="marbertv2 arabertv02_twitter camelbert_mix"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 60 min) while another process holds the GPU (it is shared with other chats).
gpu_free() {
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 4000 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for seed in 42 43 44; do
  for tag in $BERTS; do
    for g in qwen3 aya fanar; do
      for sr in sr12 sr13; do
        run=${sr}_${tag}_${g}_seed${seed}
        if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
        if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; continue; fi
        gpu_free; say "$run: start"
        if $PY -m src.sentiment.train_classifier --config configs/sentiment/${sr}_${tag}_$g.json --seed $seed \
            > "$LOGS/$run.console.log" 2>&1; then
          say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
        else say "FAILED $run (see $LOGS/$run.console.log)"; fi
      done
    done
  done
done
$PY -m src.sentiment.summarize_runs > /dev/null 2>&1
say "DONE"
