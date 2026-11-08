#!/usr/bin/env bash
# Sentiment SV01 neuron queue: MLP-neuron statistics of the three generators on real S1 train.
# Restartable: a generator with meta.json is skipped; a crashed attempt is rerun in its own folder.
cd "$(dirname "$0")/../../.." || exit 1
export PYTHONIOENCODING=utf-8
PY=.venv/Scripts/python.exe
LOG=results/sentiment/steering/queue_sv01_neurons.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait while another process holds the GPU (it is shared with other chats).
gpu_free() {
  while :; do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6400 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 120
  done
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for g in fanar qwen3 aya; do
  if [ -f data/steering/sv01_${g}_neurons/meta.json ]; then say "$g: already done, skipped"; continue; fi
  gpu_free
  say "$g: neurons start"
  if $PY -m src.sentiment.steering.activations_real --config configs/sentiment/steering/sv01_$g.json --check-hooks >> "$LOG" 2>&1; then
    say "$g: neurons done"
  else say "$g: neurons FAILED"; exit 1; fi
done
say "DONE"
