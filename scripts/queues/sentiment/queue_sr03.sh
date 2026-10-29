#!/usr/bin/env bash
# Sentiment queue (Ammar 2026-10-21, SD-007):
#   1. 300-text SR03 smoke tests for the QLoRA trainer on the 2-class path: Jais-2 (custom head) and
#      Qwen3 (library head); the queue stops if either fails or does not fit 8192 MiB
#   2. SR01: new BERTs (CAMeLBERT-mix, CAMeLBERT-DA, ARBERT, ARBERTv2), seeds 42/43/44   (~2 min each)
#   3. SR02: the same BERTs on S1 + each SG01 set (Fanar, Qwen3, Aya), seeds 42/43/44     (~3.5 min each)
#   4. SR03 (real only, NEU dropped): all 7 BERTs, seeds 42/43/44                          (~1.5 min each)
#   5. SR03: the 5 LLMs (QLoRA); seed 42 on all, then 43, then 44                          (~45-105 min each)
# Restartable: finished runs are skipped, an interrupted LLM run resumes from its checkpoint.pt.
# Log: results/sentiment/queue_sr03.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
LOG=results/sentiment/queue_sr03.log
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

# One run: <trainer module> <config name> <seed>; skipped when its train_log.json exists.
run() {
  local trainer=$1 cfg=$2 seed=$3
  local name=${cfg}_seed${seed}
  if [ -f "$RUNS/$name/train_log.json" ]; then say "$name: done, skipping"; return; fi
  gpu_free
  [ -f "$RUNS/$name/checkpoint.pt" ] && say "$name: resuming from checkpoint" || say "$name: start"
  if $PY -m src.sentiment.$trainer --config configs/sentiment/$cfg.json --seed $seed \
      >> "$LOGS/$name.console.log" 2>&1; then
    say "$name: $(grep -h '^DEV' "$LOGS/$name.console.log" | tail -1)"
  else say "FAILED $name (rerun the queue to resume)"; fi
}

say "queue start (pid $$)"
# 1. QLoRA smoke tests on the 2-class path.
for tag in jais2 qwen3; do
  smoke=sr03_${tag}_seed42_limit300
  [ -f "$RUNS/$smoke/train_log.json" ] && continue
  gpu_free; say "smoke test $smoke"
  if $PY -m src.sentiment.train_lora_classifier --config configs/sentiment/sr03_$tag.json --limit 300 \
      > "$LOGS/$smoke.console.log" 2>&1; then
    vram=$(sed -n 's/^peak VRAM \([0-9]*\) MiB.*/\1/p' "$LOGS/$smoke.console.log")
    say "smoke: $(grep -h '^DEV' "$LOGS/$smoke.console.log"); peak VRAM ${vram:-?} MiB"
    [ "${vram:-99999}" -lt 8192 ] || { say "STOP: does not fit 8192 MiB"; exit 1; }
  else say "STOP: smoke test failed ($(grep -hE 'Error' "$LOGS/$smoke.console.log" | tail -1))"; exit 1; fi
done

NEW_BERTS="camelbert_mix camelbert_da arbert arbertv2"
# 2. SR01 for the new BERTs.
for tag in $NEW_BERTS; do for seed in 42 43 44; do run train_classifier sr01_$tag $seed; done; done
# 3. SR02 for the new BERTs.
for tag in $NEW_BERTS; do for gen in fanar qwen3 aya; do for seed in 42 43 44; do
  run train_classifier sr02_${tag}_$gen $seed; done; done; done
# 4. SR03 BERTs.
for tag in marbertv2 arabertv02_twitter marbert $NEW_BERTS; do for seed in 42 43 44; do
  run train_classifier sr03_$tag $seed; done; done
# 5. SR03 LLMs, one seed across all models at a time.
for seed in 42 43 44; do for tag in jais2 aya qwen3 fanar falcon_h1; do
  run train_lora_classifier sr03_$tag $seed; done; done
say "DONE"
