#!/usr/bin/env bash
# Sentiment open-synthetic queue (SG01 zero-shot generation with 4 generators, SR02 training on it; Ammar 2026-10-16).
# File names renamed on 2026-10-16 (results/sentiment/renames_2026-10-16.json); the first run used sg0N_* / sr0N_* names.
# Per generator, in order Jais-2, Fanar, Qwen3, Aya:
#   1. generate 7,800 tweets (650 per variety x sentiment cell, zero-shot), resumable
#   2. filter (configs/filtering/sentiment.json), 3. select 500 per cell (6,000);
#      if a cell is short after filtering, top up to 900 then 1,300 per cell and refilter
#   4. train MARBERTv2, AraBERTv02-Twitter, MARBERT on S1 train + the selected set, seeds 42/43/44
# Restartable: every finished step is skipped; an interrupted generation resumes where it stopped.
# A failing generator is logged and skipped, the queue goes on with the next one.
# Log: results/sentiment/queue_sg_open.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg_open.log
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
for g in jais2 fanar qwen3 aya; do
  sg=sg01_$g
  cfg=configs/sentiment/generation/$sg.json

  # 1-3. Generate, filter, select 500 per cell. If a cell comes out short (duplicates), top up
  # the same set to 900, then 1,300 requests per cell (existing records are kept) and refilter.
  ok=0
  for target in 650 900 1300; do
    want=$((target * 12))
    for attempt in 1 2; do
      n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
      [ "$n" -ge "$want" ] && break
      gpu_free; say "$sg: generating ($n/$want done, attempt $attempt)"
      $PY -m src.sentiment.generate --config "$cfg" --per-cell $target >> "$LOGS/$sg.console.log" 2>&1         || say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"
    done
    n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
    if [ "$n" -lt "$want" ]; then say "$sg: only $n/$want generated"; break; fi
    # Filter and select again whenever the set grew (or nothing was selected yet).
    if [ ! -f "$SYN/$sg.selected.jsonl" ] || [ "$SYN/$sg.jsonl" -nt "$SYN/$sg.selected.jsonl" ]; then
      $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment.json           > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
      $PY -m src.sentiment.select_synthetic --data "$SYN/$sg.filtered.jsonl"           > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
      say "$sg ($target per cell): $(tail -1 "$LOGS/${sg}_select.console.log")"
    fi
    if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
  done
  if [ "$ok" -ne 1 ]; then say "SKIP $sg: could not reach 500 per cell, no training"; continue; fi

  # 4. BERT training, 3 seeds each.
  for tag in marbertv2 arabertv02_twitter marbert; do
    for seed in 42 43 44; do
      run=sr02_${tag}_${g}_seed${seed}
      if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
      # A folder without train_log.json is an aborted run: never overwritten; the watch check reruns it under a new name.
      if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; continue; fi
      gpu_free; say "$run: start"
      if $PY -m src.sentiment.train_classifier --config configs/sentiment/sr02_${tag}_$g.json --seed $seed \
          > "$LOGS/$run.console.log" 2>&1; then
        say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
      else say "FAILED $run (see $LOGS/$run.console.log)"; fi
    done
  done
done

$PY -m src.sentiment.summarize_runs > "$LOGS/summarize_sg_open.console.log" 2>&1 && say "tables regenerated"
say "DONE"
