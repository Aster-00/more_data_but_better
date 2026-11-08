#!/usr/bin/env bash
# SG01-EESA and SR02-EESA (D-032; prompt open_eesa_v1 approved by Ammar 2026-11-08).
# Per generator (Qwen3, Aya, Fanar; fastest first):
#   0. smoke test: 24 requests (--limit 24, separate _limit24 file); stop the generator if none parse
#   1. generate 572 requests per sentiment cell (egypt only, 1,716), resumable
#   2. filter (configs/filtering/sentiment_eesa.json), 3. select 440 per cell (1,320), overlap reported against EESA test;
#      if a cell is short after filtering, top up to 800, then 1,100 requests per cell and refilter
# Then, once all three sets are complete:
#   4. quality rows: src.sentiment.measure_quality --set sg01_eesa, universal topic spread (quality row 5)
#   5. SR02-EESA: the 7 BERTs on EESA train + each set, seeds 42/43/44 (queue_eesa.sh sr02_eesa)
# Restartable: finished steps are skipped; an interrupted generation resumes where it stopped.
# Log: results/sentiment/queue_sg01_eesa.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg01_eesa.log
GENS="qwen3 aya fanar"
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

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
# Ammar (2026-11-08): run when the GPU is free. Wait for any cross-evaluation job (e.g. SX02) to finish first.
while ps -ef | grep -q "[s]rc.sentiment.cross_eval"; do
  [ -z "${WAITED:-}" ] && say "waiting for a running cross_eval job to finish"; WAITED=1; sleep 60
done
declare -A READY
for g in $GENS; do
  sg=sg01_eesa_$g
  cfg=configs/sentiment/generation/$sg.json

  # 0. Smoke test (kept apart from the full set).
  if [ ! -f "$SYN/${sg}_limit24.jsonl" ]; then
    gpu_free; say "$sg: smoke test (24 requests)"
    $PY -m src.sentiment.generate --config "$cfg" --limit 24 > "$LOGS/${sg}_limit24.console.log" 2>&1 \
      || { say "SKIP $sg: smoke test failed (see $LOGS/${sg}_limit24.console.log)"; continue; }
  fi
  parsed=$(grep -c '"parse_ok": true' "$SYN/${sg}_limit24.jsonl" 2>/dev/null); parsed=${parsed:-0}
  say "$sg: smoke test $parsed/24 parsed"
  if [ "$parsed" -eq 0 ]; then say "SKIP $sg: no smoke-test output parsed"; continue; fi

  # 1-3. Generate, filter, select 440 per cell; top up if a cell is short.
  ok=0
  for target in 572 800 1100; do
    want=$((target * 3))
    for attempt in 1 2; do
      n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
      [ "$n" -ge "$want" ] && break
      gpu_free; say "$sg: generating ($n/$want done, attempt $attempt)"
      $PY -m src.sentiment.generate --config "$cfg" --per-cell $target >> "$LOGS/$sg.console.log" 2>&1 \
        || say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"
    done
    n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
    if [ "$n" -lt "$want" ]; then say "$sg: only $n/$want generated"; break; fi
    if [ ! -f "$SYN/$sg.selected.jsonl" ] || [ "$SYN/$sg.jsonl" -nt "$SYN/$sg.selected.jsonl" ]; then
      $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment_eesa.json \
        > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
      $PY -m src.sentiment.select_synthetic --data "$SYN/$sg.filtered.jsonl" --per-cell 440 \
        --test data/processed/sentiment/eesa_test.jsonl > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
      say "$sg ($target per cell): $(tail -1 "$LOGS/${sg}_select.console.log")"
    fi
    if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
  done
  if [ "$ok" -eq 1 ]; then READY[$g]=1; else say "SKIP $sg: could not reach 440 per cell"; fi
done

# 4. Quality rows; they need all three sets.
for g in $GENS; do
  [ -n "${READY[$g]:-}" ] || { say "STOP: sg01_eesa_$g incomplete; quality rows and SR02-EESA need all three sets"; exit 1; }
done
if [ ! -f results/quality/sentiment/sg01_eesa_quality.json ]; then
  gpu_free; say "quality sg01_eesa: measuring"
  $PY -m src.sentiment.measure_quality --set sg01_eesa > "$LOGS/sq_sg01_eesa.console.log" 2>&1 \
    || { say "STOP: quality sg01_eesa failed"; exit 1; }
  say "quality sg01_eesa done"
fi
if [ ! -f results/quality/sentiment/universal_topics_sg01_eesa.json ]; then
  gpu_free; say "topic spread sg01_eesa: measuring"
  sets="real_eesa=data/processed/sentiment/eesa_train.jsonl"
  for g in $GENS; do sets="$sets sg01_eesa_$g=$SYN/sg01_eesa_$g.selected.jsonl"; done
  $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
    --out results/quality/sentiment/universal_topics_sg01_eesa > "$LOGS/sq_topics_sg01_eesa.console.log" 2>&1 \
    || { say "STOP: topic spread failed"; exit 1; }
  $PY -m src.sentiment.summarize_quality > /dev/null 2>&1
  say "topic spread sg01_eesa done; docs/sentiment/datasets/dataset_quality.md rebuilt"
fi

# 5. SR02-EESA training (its own log: results/sentiment/queue_eesa.log).
say "SR02-EESA: starting queue_eesa.sh sr02_eesa"
bash scripts/queues/sentiment/queue_eesa.sh sr02_eesa
$PY -m src.sentiment.summarize_quality > /dev/null 2>&1
say "DONE"
