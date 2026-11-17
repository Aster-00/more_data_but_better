#!/usr/bin/env bash
# SR05-EESA, SR06-EESA, SR06-random-EESA (Ammar, 2026-11-14): the SR03-EESA and SR04-EESA BERT runs with more epochs;
# nothing else changes (epoch by training loss, D-035). 7 BERTs, seeds 42/43/44, no LLM classifiers.
#   1. Pilot: real only (sr05_eesa_<bert>), 10 epochs, 21 runs.
#   2. Epoch count chosen automatically (Ammar away): pick_epochs_eesa.py, rule fixed beforehand.
#   3. If the count is not 10: the pilot folders are renamed *_10ep (kept, not registered) and the 70 configs are set
#      to the chosen count.
#   4. All 210 runs with the chosen count, interleaved (seed -> BERT -> condition).
# Earlier attempts today (5, 10, 4 epochs, each stopped by Ammar): the *_5ep / *_4ep / *_10ep folders listed in
# results/sentiment/renames_2026-11-14.json.
# From 11:10 new run folders are junctions to G:/Thesis/results/sentiment/runs (F: full; Ammar: use the other drive).
# Restartable: finished runs are skipped; an aborted folder is reported, not touched; the choice is kept in
# results/sentiment/eesa_epoch_choice.txt. Log: results/sentiment/queue_eesa_epochs.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_eesa_epochs.log
CHOICE=results/sentiment/eesa_epoch_choice.txt
BERTS="marbertv2 marbert arabertv02_twitter arbert arbertv2 camelbert_mix camelbert_da"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Epoch count in the 70 configs and in the registry text.
set_epochs() {
  sed -i -E "s/\"epochs\": [0-9]+,/\"epochs\": $1,/" configs/sentiment/sr05_eesa_*.json configs/sentiment/sr06_eesa_*.json configs/sentiment/sr06r_eesa_*.json
  sed -i -E "s/with [0-9]+ epochs instead of 3/with $1 epochs instead of 3/" configs/sentiment/runs.json
}

# Wait (up to 60 min) while another process holds the GPU.
gpu_free() {
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 4000 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

run_one() {
  local cfg=$1 seed=$2 run=${1}_seed$2
  [ -f "$RUNS/$run/train_log.json" ] && return
  [ -d "$RUNS/$run" ] && { say "NOTE $run: aborted folder found, left untouched"; return; }
  # Drive F: is full (2026-11-14): the run folder is a directory junction to drive G:, so every path stays the same.
  free_g=$(df -BG --output=avail /g | tail -1 | tr -dc '0-9')
  [ "$free_g" -ge 5 ] || { say "STOP: less than 5 GB free on G:"; exit 1; }
  mkdir -p "/g/Thesis/results/sentiment/runs/$run"
  cmd //c mklink //J "$(cygpath -w "/f/Thesis/code/$RUNS/$run")" "$(cygpath -w "/g/Thesis/results/sentiment/runs/$run")" > /dev/null \
    || { say "STOP: could not link $run to G:"; exit 1; }
  [ -d "$RUNS/$run" ] || { say "STOP: link for $run missing"; exit 1; }
  gpu_free; say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1) (best epoch $(sed -n 's/.*"best_epoch": \([0-9]*\).*/\1/p' "$RUNS/$run/train_log.json" | head -1))"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
if [ ! -f "$CHOICE" ]; then
  # 1. Pilot.
  set_epochs 10
  for seed in 42 43 44; do for b in $BERTS; do run_one "sr05_eesa_$b" $seed; done; done
  # 2. Choice.
  N=$($PY scripts/queues/sentiment/pick_epochs_eesa.py 2>> "$LOG") || { say "STOP: pilot incomplete, no epoch count chosen"; exit 1; }
  case "$N" in ''|*[!0-9]*) say "STOP: bad epoch count: $N"; exit 1;; esac
  say "pilot done: chosen epoch count $N (results/sentiment/eesa_epoch_pilot.json)"
  # 3. Pilot folders aside if the count differs.
  if [ "$N" -ne 10 ]; then
    for seed in 42 43 44; do for b in $BERTS; do
      mv "$RUNS/sr05_eesa_${b}_seed$seed" "$RUNS/sr05_eesa_${b}_seed${seed}_10ep"
      mv "$LOGS/sr05_eesa_${b}_seed$seed.console.log" "$LOGS/sr05_eesa_${b}_seed${seed}_10ep.console.log" 2>/dev/null
    done; done
    say "pilot folders renamed sr05_eesa_<bert>_seed<N>_10ep (kept, not registered)"
    set_epochs "$N"
  fi
  echo "$N" > "$CHOICE"
fi
N=$(cat "$CHOICE"); say "all runs with $N epochs"
grep -q "\"epochs\": $N," configs/sentiment/sr06r_eesa_marbert_aya.json || { say "STOP: configs are not at $N epochs"; exit 1; }

# 4. All runs.
for seed in 42 43 44; do
  for b in $BERTS; do
    run_one "sr05_eesa_$b" $seed
    for g in qwen3 aya fanar; do
      run_one "sr05_eesa_${b}_$g" $seed
      run_one "sr06_eesa_${b}_$g" $seed
      run_one "sr06r_eesa_${b}_$g" $seed
    done
  done
done
n=$(ls -d $RUNS/sr0[56]*_eesa_*_seed4[234] 2>/dev/null | grep -v xfer | while read d; do [ -f "$d/train_log.json" ] && echo; done | wc -l)
say "DONE ($n/210 runs finished, $N epochs)"
