#!/usr/bin/env bash
# Sentiment SV01 queue: class vectors of the SG generators from real S1 train, then the CPU layer analysis.
# Waits until the GPU has stayed free for 10 minutes: the card is shared with other chats, whose
# queues leave only short gaps between runs. Restartable: finished steps are not repeated.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
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
for g in fanar qwen3 aya; do
  cfg=configs/sentiment/steering/sv01_$g.json
  if [ -f data/steering/sv01_$g/meta.json ]; then
    say "SV01 $g: extraction already done, skipped"
  else
    say "SV01 $g: waiting for the GPU to stay free for 10 min"
    gpu_free_10min
    # A crashed earlier attempt leaves a folder without meta.json; extract.py reuses it.
    say "SV01 $g: extraction start"
    if $PY -m src.sentiment.steering.extract --config "$cfg" --check-hooks >> "$LOG" 2>&1; then
      say "SV01 $g: extraction done"
    else say "SV01 $g: extraction FAILED"; exit 1; fi
  fi
  if [ -f results/sentiment/steering/sv01_$g/metrics.json ]; then continue; fi
  if $PY -m src.sentiment.steering.analyze_real --config "$cfg" --compare data/steering/sv02_sg04_$g/vectors.pt >> "$LOG" 2>&1; then
    say "SV01 $g: analysis done"
  else say "SV01 $g: analysis FAILED"; exit 1; fi
done
say "DONE"
