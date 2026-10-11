#!/usr/bin/env bash
# R04 follow-ups (MARBERT, D1, real only, seeds 42/43/44), run one after another on the GPU:
#   core:   R12-R15 dropout {0.3, 0.1} x epochs {2, 3}; R10 / R11 R03 settings + cardinality / ALDi curriculum
#   extras: dropout {0.2, 0.5} x epochs {2, 3}; dropout {0.1, 0.2, 0.3, 0.5} x 4 epochs
# A run whose train_log.json exists is skipped, so the queue can be restarted at any time.
# Logged to results/queue_r04_followups.log; each run to results/<run>.console.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOG=results/queue_r04_followups.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# config name -> training module
CORE="dropout03_ep2 dropout01_ep2 dropout03_ep3 dropout01_ep3 cl_cardinality cl_aldi"
EXTRAS="dropout02_ep2 dropout05_ep2 dropout02_ep3 dropout05_ep3 dropout01_ep4 dropout02_ep4 dropout03_ep4 dropout05_ep4"

for name in ${@:-$CORE $EXTRAS}; do   # configs can be given as arguments
  case $name in cl_*) mod=src.training.train_curriculum ;; *) mod=src.training.train_classifier ;; esac
  for seed in 42 43 44; do
    run=${name}_real_only_seed${seed}
    if [ -f results/runs/$run/train_log.json ]; then say "$run: already finished, skipping"; continue; fi
    say "$run: start"
    if $PY -m $mod --config configs/${name}_real_only.json --seed $seed > results/$run.console.log 2>&1; then
      say "$run done: $(grep -h '^DEV' results/$run.console.log | tail -1)"
    else
      say "FAILED $run ($(grep -hE 'Error' results/$run.console.log | tail -1))"
    fi
  done
done
say "DONE"
