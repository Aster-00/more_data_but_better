#!/usr/bin/env bash
# Sentiment SG02 queue: open generation with 5 real S1-train examples per request (few-shot),
# Fanar / Qwen3 / Aya (Jais-2 and Falcon-H1 not generators), then SR04 = BERT training on it (Ammar 2026-10-28).
#   1. per generator: generate 7,800 tweets (650 per variety x sentiment cell), resumable;
#      filter (configs/filtering/sentiment.json), select 500 per cell (6,000);
#      if a cell is short after filtering, top up to 900 then 1,300 per cell and refilter (as SG01)
#   2. SQ02: quality of the three selected sets (src.sentiment.measure_quality --set sg02), before any training
#   3. SR04: 7 BERTs x 3 sets x seeds 42/43/44 on S1 train + the selected set (no LLM classifiers yet)
# Restartable: every finished step is skipped; an interrupted generation resumes where it stopped.
# A failing generator is logged and skipped. Log: results/sentiment/queue_sg02.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg02.log
GENS="fanar qwen3 aya"
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

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"

# 1. Generate, filter, select.
ready=""
for g in $GENS; do
  sg=sg02_$g
  cfg=configs/sentiment/generation/$sg.json
  ok=0
  for target in 650 900 1300; do
    want=$((target * 12))
    for attempt in 1 2; do
      n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
      [ "$n" -ge "$want" ] && break
      gpu_free; say "$sg: generating ($n/$want done, attempt $attempt)"
      $PY -m src.sentiment.generate --config "$cfg" --per-cell $target >> "$LOGS/$sg.console.log" 2>&1 \
        || say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"
    done
    n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
    if [ "$n" -lt "$want" ]; then say "$sg: only $n/$want generated"; break; fi
    # Filter and select again whenever the set grew (or nothing was selected yet).
    if [ ! -f "$SYN/$sg.selected.jsonl" ] || [ "$SYN/$sg.jsonl" -nt "$SYN/$sg.selected.jsonl" ]; then
      $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment.json \
        > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
      $PY -m src.sentiment.select_synthetic --data "$SYN/$sg.filtered.jsonl" \
        > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
      say "$sg ($target per cell): $(tail -1 "$LOGS/${sg}_select.console.log")"
    fi
    if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
  done
  if [ "$ok" -eq 1 ]; then ready="$ready $g"; else say "SKIP $sg: could not reach 500 per cell, no training"; fi
done

# 2. SQ02 quality rows, needs all three selected sets.
if [ "$(echo $ready | wc -w)" -ne 3 ]; then say "STOP: only [$ready ] reached 500 per cell; SQ02 needs all three"; exit 1; fi
if [ ! -f results/quality/sentiment/sg02_quality.json ]; then
  gpu_free; say "SQ02: measuring"
  $PY -m src.sentiment.measure_quality --set sg02 > "$LOGS/sq02.console.log" 2>&1 || { say "STOP: SQ02 failed"; exit 1; }
  say "SQ02 done"
fi

# 3. SR04: BERT training, 3 seeds each.
for g in $ready; do
  for tag in $BERTS; do
    for seed in 42 43 44; do
      run=sr04_${tag}_${g}_seed${seed}
      if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
      # A folder without train_log.json is an aborted run: never overwritten.
      if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; continue; fi
      gpu_free; say "$run: start"
      if $PY -m src.sentiment.train_classifier --config configs/sentiment/sr04_${tag}_$g.json --seed $seed \
          > "$LOGS/$run.console.log" 2>&1; then
        say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
      else say "FAILED $run (see $LOGS/$run.console.log)"; fi
    done
  done
done

say "DONE"
