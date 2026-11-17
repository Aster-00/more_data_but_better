#!/usr/bin/env bash
# SG04-EESA / SR09-EESA and SG04-random-EESA / SR09-random-EESA: dislike comments (D-038, Ammar 2026-11-17).
# Usage: bash queue_sg04_eesa.sh [sets...]   default "sg04_eesa sg04r_eesa" (targeted first, then the control;
# Ammar: finish the targeted set and its runs first, then the random one).
# Per set, generators Qwen3, Aya, Fanar (fastest first):
#   0. smoke test, 24 requests (--limit 24, separate _limit24 file); skip the generator if none parse
#   1. generate ceil(1,320 x 1.6) = 2,112 requests per class (NEG, NEU), resumable
#   2. filter (configs/filtering/sentiment_eesa.json), 3. select 1,320 per class (select_synthetic --config);
#      overlap with EESA test reported only. If a class is short, top up with --margin 2.2, then 3.0, and refilter.
# Then, when all three generators of the set are complete:
#   4. quality rows (measure_quality), universal topic spread, CMI per text (src.sentiment.cmi)
#   5. training: 7 BERTs x 3 generators x seeds 42/43/44, 8 epochs, epoch by training loss (SR05-EASA recipe),
#      one run at a time; run folders are directory junctions to drive G: (F: is full)
# Restartable: finished steps and runs are skipped; an interrupted generation resumes; an aborted run folder is
# reported and left untouched. Log: results/sentiment/queue_sg04_eesa.log; console output in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
QDIR=results/quality/sentiment
LOG=results/sentiment/queue_sg04_eesa.log
SETS="${*:-sg04_eesa sg04r_eesa}"
GENS="qwen3 aya fanar"
BERTS="marbertv2 marbert arabertv02_twitter arbert arbertv2 camelbert_mix camelbert_da"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 60 min) until $1 MiB of GPU memory are free; pause $2 s first (Windows frees a model's memory late).
gpu_free() {
  local i free
  sleep "${2:-0}"
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge "$1" ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

# One training run. The folder is a directory junction to drive G: (F: is full), so every path stays the same.
run_one() {
  local cfg=$1 seed=$2 run=${1}_seed$2 free_g
  [ -f "$RUNS/$run/train_log.json" ] && return 0
  [ -d "$RUNS/$run" ] && { say "NOTE $run: aborted folder found, left untouched"; return 0; }
  free_g=$(df -BG --output=avail /g | tail -1 | tr -dc '0-9')
  [ "$free_g" -ge 5 ] || { say "STOP: less than 5 GB free on G:"; exit 1; }
  mkdir -p "/g/Thesis/results/sentiment/runs/$run"
  cmd //c mklink //J "$(cygpath -w "/f/Thesis/code/$RUNS/$run")" "$(cygpath -w "/g/Thesis/results/sentiment/runs/$run")" > /dev/null \
    || { say "STOP: could not link $run to G:"; exit 1; }
  gpu_free 2500 0
  say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1) (best epoch $(sed -n 's/.*"best_epoch": \([0-9]*\).*/\1/p' "$RUNS/$run/train_log.json" | head -1))"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}

say "queue start (pid $$), sets: $SETS, git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for set in $SETS; do
  sr=$([ "$set" = sg04_eesa ] && echo sr09_eesa || echo sr09r_eesa)
  READY=""
  for g in $GENS; do
    sg=${set}_$g
    cfg=configs/sentiment/generation/$sg.json
    if [ -f "$SYN/$sg.selected.jsonl" ] && grep -q "shortfall none" "$LOGS/${sg}_select.console.log" 2>/dev/null \
        && [ "$SYN/$sg.selected.jsonl" -nt "$SYN/$sg.jsonl" ]; then
      say "$sg: already complete"; READY="$READY $g"; continue
    fi
    # 0. Smoke test (kept apart from the full set).
    if [ ! -f "$SYN/${sg}_limit24.jsonl" ]; then
      gpu_free 6000 60; say "$sg: smoke test (24 requests)"
      if ! $PY -m src.sentiment.generate --config "$cfg" --limit 24 > "$LOGS/${sg}_limit24.console.log" 2>&1; then
        say "$sg: smoke test failed, retrying in 2 min ($(grep -hE 'Error' "$LOGS/${sg}_limit24.console.log" | tail -1))"; sleep 120
        $PY -m src.sentiment.generate --config "$cfg" --limit 24 > "$LOGS/${sg}_limit24.console.log" 2>&1 \
          || { say "SKIP $sg: smoke test failed twice (see $LOGS/${sg}_limit24.console.log)"; continue; }
      fi
    fi
    parsed=$(grep -c '"parse_ok": true' "$SYN/${sg}_limit24.jsonl" 2>/dev/null); parsed=${parsed:-0}
    say "$sg: smoke test $parsed/24 parsed"
    [ "$parsed" -eq 0 ] && { say "SKIP $sg: no smoke-test output parsed"; continue; }
    # 1-3. Generate, filter, select; top up with a larger margin if a class is short.
    ok=0
    for margin in 1.6 2.2 3.0; do
      want=$($PY -c "import json,math;c=json.load(open('$cfg',encoding='utf-8'));print(sum(math.ceil(x['target']*$margin) for x in c['cells']))")
      for attempt in 1 2; do
        n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
        [ "$n" -ge "$want" ] && break
        gpu_free 6000 60; say "$sg: generating ($n/$want done, margin $margin, attempt $attempt)"
        $PY -m src.sentiment.generate --config "$cfg" --margin $margin >> "$LOGS/$sg.console.log" 2>&1 \
          || { say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"; sleep 120; }
      done
      n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
      [ "$n" -lt "$want" ] && { say "$sg: only $n/$want generated"; break; }
      if [ ! -f "$SYN/$sg.selected.jsonl" ] || [ "$SYN/$sg.jsonl" -nt "$SYN/$sg.selected.jsonl" ]; then
        $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment_eesa.json \
          > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
        $PY -m src.sentiment.select_synthetic --data "$SYN/$sg.filtered.jsonl" --config "$cfg" \
          --test data/processed/sentiment/eesa_test.jsonl > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
        say "$sg (margin $margin): $(tail -1 "$LOGS/${sg}_select.console.log")"
      fi
      grep -q "shortfall none" "$LOGS/${sg}_select.console.log" && { ok=1; break; }
    done
    [ "$ok" -eq 1 ] && READY="$READY $g" || say "SKIP $sg: could not reach 1,320 per class"
  done
  [ "$(echo $READY | wc -w)" -eq 3 ] || { say "STOP: $set has only [$READY ] complete; quality rows and training need all three"; exit 1; }

  # 4. Quality rows, universal topic spread and CMI, before any training.
  if [ ! -f "$QDIR/${set}_quality.json" ]; then
    gpu_free 6000 60; say "quality $set: measuring"
    $PY -m src.sentiment.measure_quality --set $set > "$LOGS/sq_$set.console.log" 2>&1 \
      || { say "STOP: quality $set failed (see $LOGS/sq_$set.console.log)"; exit 1; }
  fi
  sets="real_eesa=data/processed/sentiment/eesa_train.jsonl"
  for g in $GENS; do sets="$sets ${set}_$g=$SYN/${set}_$g.selected.jsonl"; done
  if [ ! -f "$QDIR/universal_topics_$set.json" ]; then
    gpu_free 6000 60; say "topic spread $set: measuring"
    $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
      --out "$QDIR/universal_topics_$set" > "$LOGS/sq_topics_$set.console.log" 2>&1 || say "NOTE: topic spread failed"
  fi
  if [ ! -f "$QDIR/cmi_$set.json" ]; then
    $PY -m src.sentiment.cmi --sets $sets --out "$QDIR/cmi_$set" > "$LOGS/cmi_$set.console.log" 2>&1 \
      && while read -r line; do say "CMI $line"; done < "$LOGS/cmi_$set.console.log" || say "NOTE: CMI failed"
  fi
  $PY -m src.sentiment.summarize_quality > /dev/null 2>&1
  say "quality rows $set done"

  # 5. Training, interleaved (seed -> BERT -> generator) so a partial queue still has matched runs.
  say "${sr}: 63 runs, 8 epochs, one at a time"
  gpu_free 6000 60
  for seed in 42 43 44; do for b in $BERTS; do for g in $GENS; do
    run_one "${sr}_${b}_$g" $seed < /dev/null
  done; done; done
  done_n=$(for seed in 42 43 44; do for b in $BERTS; do for g in $GENS; do
    [ -f "$RUNS/${sr}_${b}_${g}_seed$seed/train_log.json" ] && echo x; done; done; done | wc -l)
  $PY -m src.sentiment.summarize_quality > /dev/null 2>&1
  say "SET DONE $set ($done_n/63 runs of $sr finished)"
done
say "ALL DONE"
