#!/usr/bin/env bash
# After SG02-EESA generation (queue_sg02_eesa.sh), D-034; chained by Ammar's choice (2026-11-10: option b,
# training starts after the quality rows; he reads the rows while it trains).
#   1. wait until queue_sg02_eesa.log ends with DONE and all 6 sets are complete
#   2. quality rows: measure_quality --set sg02_eesa / sg02r_eesa, universal topic spread, Self-BLEU (explore_eesa),
#      combined table rebuilt
#   3. BERTs: SR04-EESA (+ SG02-EESA) and SR04-random-EESA (+ SG02-random-EESA), 7 BERTs x 3 generators x seeds 42/43/44
#   4. LLM classifiers, seed 42 only: Qwen3, Aya, Fanar, Jais-2, Falcon-H1 on SR01-EESA (real only), SR02-EESA
#      (+ SG01-EASA), SR04-EESA and SR04-random-EESA; no LLM on its own generator's set (D-020). 41 runs.
# GPU rest: after every 20 h of GPU work since the last rest (counted from the generation queue's start), 1 h pause.
# Restartable: finished runs are skipped; LLM runs resume from their checkpoint.
# Log: results/sentiment/queue_sr04_eesa.log; console output per run in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sr04_eesa.log
GENLOG=results/sentiment/queue_sg02_eesa.log
REST=results/sentiment/queue_sr04_eesa.last_rest     # epoch seconds of the last rest (or of the chain's start)
BERTS="marbertv2 marbert arabertv02_twitter arbert arbertv2 camelbert_mix camelbert_da"
GENS="qwen3 aya fanar"
LLMS="qwen3 aya fanar jais2 falcon_h1"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# The 20-h clock starts with the generation queue (first line of its log), unless a rest was taken since.
if [ ! -f "$REST" ]; then
  start=$(head -1 "$GENLOG" | sed -n 's/^\[\([^]]*\)\].*/\1/p')
  date -d "$start" +%s > "$REST"
fi

# Rest 1 h once 20 h of GPU work have passed since the last rest.
rest_if_due() {
  local last now
  last=$(cat "$REST"); now=$(date +%s)
  if [ $((now - last)) -ge 72000 ]; then
    say "GPU rest: 1 h (20 h since $(date -d @"$last" '+%F %T'))"; sleep 3600
    date +%s > "$REST"; say "GPU rest over"
  fi
}

# Wait (up to 60 min) while another process holds the GPU (it is shared with other chats).
gpu_free() {
  rest_if_due
  sleep 30
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge "$1" ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"

# 1. Wait for the generation queue.
while ! tail -1 "$GENLOG" 2>/dev/null | grep -q "DONE"; do
  [ -z "${WAITED:-}" ] && say "waiting for queue_sg02_eesa.sh to finish"; WAITED=1; sleep 300
done
for s in sg02_eesa sg02r_eesa; do
  for g in $GENS; do
    grep -q "shortfall none" "$LOGS/${s}_${g}_select.console.log" 2>/dev/null \
      || { say "STOP: ${s}_$g incomplete (see $GENLOG); no training on an incomplete set"; exit 1; }
  done
done

# 2. Quality rows.
for s in sg02_eesa sg02r_eesa; do
  if [ ! -f results/quality/sentiment/${s}_quality.json ]; then
    gpu_free 6000; say "quality $s: measuring"
    $PY -m src.sentiment.measure_quality --set $s > "$LOGS/sq_$s.console.log" 2>&1 || { say "STOP: quality $s failed"; exit 1; }
  fi
done
if [ ! -f results/quality/sentiment/universal_topics_sg02_eesa.json ]; then
  gpu_free 6000; say "topic spread sg02_eesa / sg02r_eesa: measuring"
  sets="real_eesa=data/processed/sentiment/eesa_train.jsonl"
  for s in sg02_eesa sg02r_eesa; do for g in $GENS; do sets="$sets ${s}_$g=$SYN/${s}_$g.selected.jsonl"; done; done
  $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
    --out results/quality/sentiment/universal_topics_sg02_eesa > "$LOGS/sq_topics_sg02_eesa.console.log" 2>&1 \
    || { say "STOP: topic spread failed"; exit 1; }
fi
$PY -m src.sentiment.explore_eesa > "$LOGS/explore_eesa.console.log" 2>&1 || say "NOTE: explore_eesa (Self-BLEU) failed"
$PY -m src.sentiment.summarize_quality > /dev/null 2>&1
say "quality rows done: docs/sentiment/datasets/EESA/dataset_quality.md, results/quality/sentiment/eesa_explore.md (Self-BLEU)"

# 3. BERTs, interleaved (seed -> BERT -> generator -> condition) so a partial queue still has matched runs.
bert_one() {
  local cfg=$1 seed=$2 run=$3
  [ -f "$RUNS/$run/train_log.json" ] && return
  [ -d "$RUNS/$run" ] && { say "NOTE $run: aborted folder found, left untouched"; return; }
  gpu_free 4000; say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}
for seed in 42 43 44; do
  for b in $BERTS; do
    for g in $GENS; do
      for sr in sr04_eesa sr04r_eesa; do bert_one "${sr}_${b}_$g" $seed "${sr}_${b}_${g}_seed${seed}"; done
    done
  done
done
say "BERTs done"

# 4. LLM classifiers, seed 42, resumable from checkpoints; one retry on failure.
llm_one() {
  local cfg=$1 run=$2
  [ -f "$RUNS/$run/train_log.json" ] && return
  for attempt in 1 2; do
    gpu_free 6000
    [ -f "$RUNS/$run/checkpoint.pt" ] && say "$run: resuming from checkpoint" || say "$run: start"
    if $PY -m src.sentiment.train_lora_classifier --config "configs/sentiment/$cfg.json" >> "$LOGS/$run.console.log" 2>&1; then
      say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"; return
    fi
    say "$run: failed (attempt $attempt; $(grep -hE 'Error' "$LOGS/$run.console.log" | tail -1))"; sleep 120
  done
  say "FAILED $run (rerun the queue to resume)"
}
for m in $LLMS; do llm_one "sr01_eesa_$m" "sr01_eesa_${m}_seed42"; done
for m in $LLMS; do
  for g in $GENS; do
    [ "$g" = "$m" ] && continue
    for sr in sr02_eesa sr04_eesa sr04r_eesa; do llm_one "${sr}_${m}_$g" "${sr}_${m}_${g}_seed42"; done
  done
done
$PY -m src.sentiment.summarize_quality > /dev/null 2>&1
say "DONE"
