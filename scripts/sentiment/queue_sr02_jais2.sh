#!/usr/bin/env bash
# SR02 Jais-2 queue (Ammar 2026-10-16): Jais-2 QLoRA classifier (SR01 recipe) on S1 train + each SG01 set
# that has 500 per cell (Fanar, Qwen3, Aya), seeds 42/43/44. Order: seed 42 on all three sets, then 43, then 44.
#   1. 300-text smoke test (must finish and fit 8192 MiB, otherwise the queue stops)
#   2. 9 full runs (~2.4 h each)
# Restartable: finished runs are skipped, an interrupted run resumes from its checkpoint.pt.
# Log: results/sentiment/queue_sr02_jais2.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr02_jais2.log
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 60 min) while another process holds the GPU (it is shared with other chats).
gpu_free() {
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6000 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

say "queue start (pid $$)"
# 1. Smoke test on the first set.
smoke=sr02_jais2_fanar_seed42_limit300
if [ ! -f "$RUNS/$smoke/train_log.json" ]; then
  gpu_free; say "smoke test (300 texts)"
  if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr02_jais2_fanar.json --limit 300 \
      > "$LOGS/$smoke.console.log" 2>&1; then
    vram=$(sed -n 's/^peak VRAM \([0-9]*\) MiB.*/\1/p' "$LOGS/$smoke.console.log")
    say "smoke: $(grep -h '^DEV' "$LOGS/$smoke.console.log"); peak VRAM ${vram:-?} MiB"
    [ "${vram:-99999}" -lt 8192 ] || { say "STOP: does not fit 8192 MiB"; exit 1; }
  else say "STOP: smoke test failed ($(grep -hE 'Error' "$LOGS/$smoke.console.log" | tail -1))"; exit 1; fi
fi

# 2. Full runs (appending to the console log, so a resumed run keeps its earlier output).
for seed in 42 43 44; do
  for g in fanar qwen3 aya; do
    run=sr02_jais2_${g}_seed${seed}
    if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
    gpu_free
    [ -f "$RUNS/$run/checkpoint.pt" ] && say "$run: resuming from checkpoint" || say "$run: start"
    if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr02_jais2_$g.json --seed $seed \
        >> "$LOGS/$run.console.log" 2>&1; then
      say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
    else say "FAILED $run (rerun the queue to resume)"; fi
  done
done
$PY -m src.sentiment.summarize_runs > "$LOGS/summarize_sr02_jais2.console.log" 2>&1 && say "tables regenerated"
say "DONE"
