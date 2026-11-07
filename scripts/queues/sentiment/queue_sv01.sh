#!/usr/bin/env bash
# Sentiment SV01 queue: class vectors of Fanar from real S1 train (D-027), then the CPU layer analysis.
# Waits until the GPU has stayed free for 10 minutes: the card is shared with other chats, whose
# queues leave only short gaps between runs. Restartable: a finished extraction is not repeated.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
CFG=configs/sentiment/steering/sv01_fanar.json
OUT=data/steering/sv01_fanar
LOG=results/sentiment/steering/queue_sv01.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

gpu_free_10min() {
  ok=0
  while [ "$ok" -lt 10 ]; do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    if [ "$free" -ge 6000 ]; then ok=$((ok + 1)); else ok=0; fi
    sleep 60
  done
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
if [ -f "$OUT/meta.json" ]; then
  say "SV01 extraction already done, skipped"
else
  say "waiting for the GPU to stay free for 10 min"
  gpu_free_10min
  # A crashed earlier attempt leaves a folder without meta.json; extract.py reuses it.
  say "SV01 extraction start"
  if $PY -m src.sentiment.steering.extract --config "$CFG" --check-hooks >> "$LOG" 2>&1; then
    say "SV01 extraction done"
  else say "SV01 extraction FAILED"; exit 1; fi
fi
if $PY -m src.sentiment.steering.analyze_real --config "$CFG" >> "$LOG" 2>&1; then
  say "SV01 analysis done"
else say "SV01 analysis FAILED"; exit 1; fi
say "DONE"
