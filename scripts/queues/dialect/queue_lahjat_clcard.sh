#!/usr/bin/env bash
# Every BERT run (R02-R07, R10-R24) repeated with Mohamedelzeftawy/LahjatBERT_cl_cardinality as the
# starting model instead of UBC-NLP/MARBERT (configs/*_lahjat_clcard.json), seeds 42/43/44, one after another.
# Multi-model runs (R03, R07, R02, R05, R06) first, then R04, the curricula and the dropout x epochs grid.
# A run whose train_log.json exists is skipped, so the queue can be restarted at any time.
# Logged to results/queue_lahjat_clcard.log; each run to results/<run>.console.log.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HOME=F:/Thesis/hf_home HF_HUB_CACHE=F:/Thesis/models HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOG=results/queue_lahjat_clcard.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

MULTI="baseline_real_only card1to18_real_only card1to18_nodiac_real_only card1to17_real_only card0to17_real_only"
SINGLE="repro_lahjatbert_baseline cl_cardinality_real_only cl_aldi_real_only"
GRID="dropout03_ep2 dropout01_ep2 dropout03_ep3 dropout01_ep3 dropout02_ep2 dropout05_ep2 dropout02_ep3 dropout05_ep3
      dropout01_ep4 dropout02_ep4 dropout03_ep4 dropout05_ep4"

for name in ${@:-$MULTI $SINGLE $(for g in $GRID; do echo ${g}_real_only; done)}; do   # configs can be given as arguments
  case $name in cl_*) mod=src.training.train_curriculum ;; *) mod=src.training.train_classifier ;; esac
  for seed in 42 43 44; do
    run=${name}_lahjat_clcard_seed${seed}
    if [ -f results/runs/$run/train_log.json ]; then say "$run: already finished, skipping"; continue; fi
    say "$run: start"
    if $PY -m $mod --config configs/${name}_lahjat_clcard.json --seed $seed > results/$run.console.log 2>&1; then
      say "$run done: $(grep -h '^DEV' results/$run.console.log | tail -1)"
    else
      say "FAILED $run ($(grep -hE 'Error' results/$run.console.log | tail -1))"
    fi
  done
done
say "DONE"
