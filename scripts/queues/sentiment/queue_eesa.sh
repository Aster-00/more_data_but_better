#!/usr/bin/env bash
# EESA runs (D-032): the 7 BERTs trained on EESA train (data version E2), chosen on EESA dev, scored on EESA test.
#   SR01-EESA  real only                       (baseline)
#   SR02-EESA  + SG01 subset, 1,320 texts      (0.54 x real, as SR02)
#   SR05-EESA  + SG03 subset, 880 texts        (0.36 x real, as SR05)
#   SR06-EESA  + SG03-random subset, 880 texts (control for SR05-EESA, as SR06)
# 210 runs, interleaved (seed -> BERT -> condition) so a partial queue still has matched runs.
# Usage: bash queue_eesa.sh [conditions...]   e.g. "sr01_eesa" only; default all four.
# Restartable: finished runs are skipped; an aborted folder is left untouched and reported.
# Log: results/sentiment/queue_eesa.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_eesa.log
CONDS="${*:-sr01_eesa sr02_eesa sr05_eesa sr06_eesa}"
BERTS="marbertv2 marbert arabertv02_twitter arbert arbertv2 camelbert_mix camelbert_da"
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

# One run: skip if finished, report an aborted folder, otherwise train.
run_one() {
  local cfg=$1 seed=$2 run=$3
  if [ -f "$RUNS/$run/train_log.json" ]; then return; fi
  if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; return; fi
  gpu_free; say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" \
      > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}

say "queue start (pid $$), conditions: $CONDS, git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for seed in 42 43 44; do
  for tag in $BERTS; do
    case " $CONDS " in *" sr01_eesa "*) run_one "sr01_eesa_$tag" $seed "sr01_eesa_${tag}_seed${seed}";; esac
    for g in qwen3 aya fanar; do
      for sr in sr02_eesa sr05_eesa sr06_eesa; do
        case " $CONDS " in *" $sr "*) run_one "${sr}_${tag}_$g" $seed "${sr}_${tag}_${g}_seed${seed}";; esac
      done
    done
  done
done
$PY -m src.sentiment.summarize_runs > /dev/null 2>&1
say "DONE"
