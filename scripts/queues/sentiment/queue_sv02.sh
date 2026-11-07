#!/usr/bin/env bash
# Sentiment SV02 queue: activations of each SG04 generator on its own selected texts (GPU step).
# Restartable: a generator whose output folder already has meta.json is skipped.
# Then the CPU step (vectors, probes, neurons, figures) for every finished generator.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
LOG=results/sentiment/steering/queue_sv02.log
say() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"; }

for g in fanar qwen3 aya; do
  cfg=configs/sentiment/steering/sv02_sg04_$g.json
  if [ -f data/steering/sv02_sg04_$g/meta.json ]; then say "SV02 $g: already done, skipped"; continue; fi
  # A crashed earlier attempt leaves a folder without meta.json; it is removed before the rerun.
  rm -rf data/steering/sv02_sg04_$g
  say "SV02 $g: activations start"
  if $PY -m src.sentiment.steering.activations_generated --config "$cfg" --check-hooks >> "$LOG" 2>&1; then
    say "SV02 $g: activations done"
  else
    say "SV02 $g: activations FAILED"; exit 1
  fi
done
say "SV02 GPU step done"
