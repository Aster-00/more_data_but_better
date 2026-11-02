#!/usr/bin/env bash
# Sentiment SG04 queue (D-023, test-contaminated): minimal pairs for the SR02 TEST hard-case types
# (prompts/sentiment/pairs_targeted_v2.json, Ammar 2026-11-02), Fanar / Qwen3 / Aya, then BERT training.
#   1. per generator: generate 3,200 pair requests (1.6 x 2,000 target pairs), resumable; filter
#      (configs/filtering/sentiment_pairs_sg04.json: SG03 filter + near-copies of the test set rejected);
#      keep 2,000 complete pairs, judge-confirmed pairs first, set fidelity >= 0.8 (select_pairs
#      --min-fidelity); if a type or the fidelity is short, top up to 2.0x, 2.5x, then 3.0x and refilter
#   2. SQ05: quality of the selected sets (measure_quality --set sg04, universal topic spread), before training
#   3. SR07 (+ SG04): 7 BERTs x 3 generators x seeds 42/43/44. No random control (Ammar 2026-11-02).
# Restartable: every finished step is skipped; an interrupted generation resumes where it stopped.
# Log: results/sentiment/queue_sg04.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg04.log
PLAN=prompts/sentiment/pairs_targeted_v2.json
GENS="aya qwen3 fanar"
BERTS="marbertv2 arabertv02_twitter marbert camelbert_mix camelbert_da arbert arbertv2"
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

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l) (SG04 code not committed, Ammar: no commit without asking)"

# 1. Generate, filter, select.
declare -A READY
for g in $GENS; do
  sg=sg04_$g
  cfg=configs/sentiment/generation/$sg.json
  ok=0
  for scale in 1.6 2.0 2.5 3.0; do
    want=$($PY -c "import math,json;t=json.load(open('$PLAN',encoding='utf-8'))['types'];print(2*sum(math.ceil(v['target_pairs']*$scale) for v in t.values()))")
    for attempt in 1 2; do
      n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
      [ "$n" -ge "$want" ] && break
      gpu_free; say "$sg: generating ($n/$want records done, scale $scale, attempt $attempt)"
      $PY -m src.sentiment.generate_pairs --config "$cfg" --scale $scale >> "$LOGS/$sg.console.log" 2>&1 \
        || say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"
    done
    n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
    if [ "$n" -lt "$want" ]; then say "$sg: only $n/$want records generated"; break; fi
    # Filter and select again whenever the set grew (or nothing was selected yet).
    if [ ! -f "$SYN/$sg.selected.jsonl" ] || [ "$SYN/$sg.jsonl" -nt "$SYN/$sg.selected.jsonl" ]; then
      $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment_pairs_sg04.json \
        > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
      gpu_free
      $PY -m src.sentiment.select_pairs --data "$SYN/$sg.filtered.jsonl" --plan $PLAN --min-fidelity 0.8 \
        > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
      say "$sg (scale $scale): $(tail -1 "$LOGS/${sg}_select.console.log") | fidelity $($PY -c "import json;s=json.load(open('results/filtering/$sg.selection.json',encoding='utf-8'));print(s['fidelity'], s['fidelity_per_type'])")"
    fi
    if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
  done
  if [ "$ok" -eq 1 ]; then READY[$sg]=1; else say "SKIP $sg: could not reach the target pairs / fidelity 0.8, no training"; fi
done

# 2. SQ05 quality rows, needs all three generators.
for g in $GENS; do
  [ -n "${READY[sg04_$g]:-}" ] || { say "STOP: not all generators of sg04 reached the target; SQ05 needs all three"; exit 1; }
done
if [ ! -f results/quality/sentiment/sg04_quality.json ]; then
  gpu_free; say "SQ05 sg04: measuring"
  $PY -m src.sentiment.measure_quality --set sg04 > "$LOGS/sq05_sg04.console.log" 2>&1 || { say "STOP: SQ05 failed"; exit 1; }
  say "SQ05 sg04 done"
fi
if [ ! -f results/quality/sentiment/universal_topics_sg04.json ]; then
  gpu_free; say "topic spread: measuring"
  sets="real=data/processed/sentiment/arsarcasm_v2_train.jsonl"
  for g in $GENS; do sets="$sets sg04_$g=$SYN/sg04_$g.selected.jsonl"; done
  $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
    --out results/quality/sentiment/universal_topics_sg04 > "$LOGS/sq_topics_sg04.console.log" 2>&1 \
    || { say "STOP: topic spread failed"; exit 1; }
  say "topic spread done"
fi

# 3. SR07: BERT training, 3 seeds each.
for g in $GENS; do
  for tag in $BERTS; do
    for seed in 42 43 44; do
      run=sr07_${tag}_${g}_seed${seed}
      if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
      # A folder without train_log.json is an aborted run: never overwritten.
      if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; continue; fi
      gpu_free; say "$run: start"
      if $PY -m src.sentiment.train_classifier --config configs/sentiment/sr07_${tag}_$g.json --seed $seed \
          > "$LOGS/$run.console.log" 2>&1; then
        say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
      else say "FAILED $run (see $LOGS/$run.console.log)"; fi
    done
  done
done

$PY -m src.sentiment.summarize_quality > /dev/null 2>&1; $PY -m src.sentiment.summarize_runs > /dev/null 2>&1
say "DONE"
