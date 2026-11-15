#!/usr/bin/env bash
# D-035: SR01-EASA-TL and SR02-EASA-TL = SR01-EASA / SR02-EASA rerun with the epoch chosen by training loss
# (config epoch_selection "train_loss"); old folders kept. 7 BERTs, seeds 42/43/44, 84 runs, interleaved
# (seed -> BERT -> condition). Then SG01-most-errors is rebuilt from these runs (most_errors_eesa --runs tl).
# Stops there: Ammar checks how the error types changed before SG02-EESA generation resumes.
# Restartable: finished runs are skipped; an aborted folder is reported, not touched.
# Log: results/sentiment/queue_eesa_tl.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_eesa_tl.log
BERTS="marbertv2 marbert arabertv02_twitter arbert arbertv2 camelbert_mix camelbert_da"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

gpu_free() {
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 4000 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

run_one() {
  local cfg=$1 seed=$2 run=$3
  [ -f "$RUNS/$run/train_log.json" ] && return
  [ -d "$RUNS/$run" ] && { say "NOTE $run: aborted folder found, left untouched"; return; }
  gpu_free; say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1) (best epoch $(sed -n 's/.*"best_epoch": \([0-9]*\).*/\1/p' "$RUNS/$run/train_log.json" | head -1))"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
# Tiny check of the new epoch rule (300 texts, 1 epoch; separate _limit300 folder).
smoke=sr01_eesa_tl_marbert_seed42_limit300
if [ ! -f "$RUNS/$smoke/train_log.json" ]; then
  gpu_free; say "smoke test ($smoke)"
  $PY -m src.sentiment.train_classifier --config configs/sentiment/sr01_eesa_tl_marbert.json --limit 300 > "$LOGS/$smoke.console.log" 2>&1 \
    || { say "STOP: smoke test failed ($(grep -hE 'Error' "$LOGS/$smoke.console.log" | tail -1))"; exit 1; }
  grep -q '"epoch_selection": "train_loss"' "$RUNS/$smoke/train_log.json" || { say "STOP: epoch rule not in the log"; exit 1; }
  say "smoke test ok"
fi

for seed in 42 43 44; do
  for b in $BERTS; do
    run_one "sr01_eesa_tl_$b" $seed "sr01_eesa_tl_${b}_seed${seed}"
    for g in qwen3 aya fanar; do run_one "sr02_eesa_tl_${b}_$g" $seed "sr02_eesa_tl_${b}_${g}_seed${seed}"; done
  done
done
n=$(ls -d $RUNS/sr0[12]_eesa_tl_*_seed4[234] 2>/dev/null | while read d; do [ -f "$d/train_log.json" ] && echo; done | wc -l)
[ "$n" -eq 84 ] || { say "STOP: only $n/84 runs finished; error set not rebuilt"; exit 1; }

gpu_free; say "SG01-most-errors (tl): rebuilding"
$PY -m src.sentiment.most_errors_eesa --runs tl > "$LOGS/most_errors_eesa_tl.console.log" 2>&1 \
  || { say "STOP: most_errors_eesa --runs tl failed"; exit 1; }
say "$(grep 'dev texts wrong' "$LOGS/most_errors_eesa_tl.console.log")"
say "DONE (review the new error types before SG02-EESA generation)"
