#!/usr/bin/env bash
# SG03-EESA and SR07-EESA: matrix-language pilot (D-037, Ammar 2026-11-15; idea from Yoo et al. 2025).
# Three arms, identical except the writing instruction of the prompt (prompts/sentiment/matrix_eesa_<arm>_v2.json):
#   nm  no matrix instruction        sets sg03nm_eesa_<generator>   runs sr07nm_eesa_<bert>_<generator>
#   dm  Egyptian Arabic is the matrix sets sg03dm_eesa_<generator>   runs sr07dm_eesa_<bert>_<generator>
#   em  English is the matrix         sets sg03em_eesa_<generator>   runs sr07em_eesa_<bert>_<generator>
# Usage: bash queue_sg03_eesa.sh [generators...]   default "qwen3" (stage 1); stage 2: "aya fanar".
# Per generator and arm:
#   0. smoke test, 24 requests (Qwen3: done by hand on 2026-11-15, *_limit24 with prompt v1, *_limit48 with v2)
#   1. generate 572 requests per sentiment cell (1,716), resumable
#   2. filter (configs/filtering/sentiment_eesa.json, the same for every arm), 3. select 440 per cell (1,320);
#      if a cell is short, top up to 800, then 1,100 requests per cell and refilter
# Then, for the arms that are complete:
#   4. quality rows (measure_quality --generators, universal topic spread), CMI per text (src.sentiment.cmi)
#   5. SR07-EESA: the 7 BERTs on EESA train + each set, seeds 42/43/44, 3 epochs, epoch by training loss (D-035),
#      two runs at a time on the GPU (Ammar: Qwen3 results sooner); run folders are junctions to drive G: (F: is full)
# Restartable: finished steps and runs are skipped; an interrupted generation resumes; an aborted run folder is
# reported and left untouched. Log: results/sentiment/queue_sg03_eesa.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
QDIR=results/quality/sentiment
LOG=results/sentiment/queue_sg03_eesa.log
GENS="${*:-qwen3}"
# Options (environment), added 2026-11-15 for the later stages:
#   ARMS        arms of this call (default "nm dm em"); dm3 = the dialect-matrix arm with prompt v3
#   SR          run prefix (default sr07 = 3 epochs; sr08 = the same runs with 8 epochs, D-036 recipe)
#   TRAIN_ONLY  1 = no generation and no measuring: train on the sets that are already complete
STAGE=$(echo "$GENS" | tr ' ' '_')
[ -n "${ARMS:-}" ] && STAGE="${STAGE}_$(echo "$ARMS" | tr ' ' '_')"
ARMS="${ARMS:-nm dm em}"
SR="${SR:-sr07}"
[ "$SR" != sr07 ] && STAGE="${STAGE}_$SR"
TRAIN_ONLY="${TRAIN_ONLY:-}"
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

say "queue start (pid $$), generators: $GENS, arms: $ARMS, runs: $SR${TRAIN_ONLY:+, training only}, git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
READY=""
for g in $GENS; do
  for arm in $ARMS; do
    sg=sg03${arm}_eesa_$g
    cfg=configs/sentiment/generation/$sg.json
    # Training only: a set counts if its selection is complete; a set that was never generated is passed over.
    if [ -n "$TRAIN_ONLY" ]; then
      grep -q "shortfall none" "$LOGS/${sg}_select.console.log" 2>/dev/null && [ -f "$SYN/$sg.selected.jsonl" ] && READY="$READY $sg"
      continue
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
    if [ "$parsed" -eq 0 ]; then say "SKIP $sg: no smoke-test output parsed"; continue; fi

    # 1-3. Generate, filter, select 440 per cell; top up if a cell is short.
    ok=0
    for target in 572 800 1100; do
      want=$((target * 3))
      for attempt in 1 2; do
        n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
        [ "$n" -ge "$want" ] && break
        gpu_free 6000 60; say "$sg: generating ($n/$want done, attempt $attempt)"
        $PY -m src.sentiment.generate --config "$cfg" --per-cell $target >> "$LOGS/$sg.console.log" 2>&1 \
          || { say "$sg: generation exited with an error ($(grep -hE 'Error' "$LOGS/$sg.console.log" | tail -1))"; sleep 120; }
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
    if [ "$ok" -eq 1 ]; then READY="$READY $sg"; else say "SKIP $sg: could not reach 440 per cell; this arm is not trained"; fi
  done
done
[ -n "$READY" ] || { say "STOP: no set is complete"; exit 1; }
say "complete sets:$READY"

# 4. Quality rows per arm, over every generator of the arm that has a selected set (stage 2 re-measures stage 1's).
[ -n "$TRAIN_ONLY" ] && ARMS_Q="" || ARMS_Q="$ARMS"
for arm in $ARMS_Q; do
  tag=sg03${arm}_eesa; have=""
  for g in fanar qwen3 aya; do [ -f "$SYN/${tag}_$g.selected.jsonl" ] && have="$have $g"; done
  [ -n "$have" ] || continue
  missing=0
  for g in $have; do grep -q "\"$g\": {" "$QDIR/${tag}_quality.json" 2>/dev/null || missing=1; done
  if [ "$missing" -eq 1 ]; then
    gpu_free 6000 60; say "quality $tag ($have): measuring"
    $PY -m src.sentiment.measure_quality --set $tag --generators $have > "$LOGS/sq_${tag}_$STAGE.console.log" 2>&1 \
      || say "NOTE: quality $tag failed (see $LOGS/sq_${tag}_$STAGE.console.log)"
  fi
done
sets="real_eesa=data/processed/sentiment/eesa_train.jsonl"
for sg in $READY; do sets="$sets $sg=$SYN/$sg.selected.jsonl"; done
if [ -z "$TRAIN_ONLY" ] && [ ! -f "$QDIR/universal_topics_sg03_eesa_$STAGE.json" ]; then
  gpu_free 6000 60; say "topic spread: measuring"
  $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
    --out "$QDIR/universal_topics_sg03_eesa_$STAGE" > "$LOGS/sq_topics_sg03_eesa_$STAGE.console.log" 2>&1 \
    || say "NOTE: topic spread failed"
fi
if [ -z "$TRAIN_ONLY" ]; then
  $PY -m src.sentiment.cmi --sets $sets --out "$QDIR/cmi_sg03_eesa_$STAGE" > "$LOGS/cmi_sg03_eesa_$STAGE.console.log" 2>&1 \
    && while read -r line; do say "CMI $line"; done < "$LOGS/cmi_sg03_eesa_$STAGE.console.log" || say "NOTE: CMI failed"
  $PY -m src.sentiment.summarize_quality > /dev/null 2>&1
fi
for sg in $READY; do
  tag=${sg%_*}; g=${sg##*_}
  grep -q "\"$g\": {" "$QDIR/${tag}_quality.json" 2>/dev/null \
    || { say "STOP: no quality row for $sg; no set is trained on without its quality rows"; exit 1; }
done
say "quality rows done: docs/sentiment/datasets/EESA/dataset_quality.md, $QDIR/cmi_sg03_eesa_$STAGE.json"

# 5. SR07-EESA: one run. The folder is a directory junction to drive G: (F: is full), so every path stays the same.
run_one() {
  local cfg=$1 seed=$2 run=${1}_seed$2
  [ -f "$RUNS/$run/train_log.json" ] && return
  [ -d "$RUNS/$run" ] && { say "NOTE $run: aborted folder found, left untouched"; return; }
  free_g=$(df -BG --output=avail /g | tail -1 | tr -dc '0-9')
  [ "$free_g" -ge 5 ] || { say "STOP: less than 5 GB free on G:"; return 1; }
  mkdir -p "/g/Thesis/results/sentiment/runs/$run"
  cmd //c mklink //J "$(cygpath -w "/f/Thesis/code/$RUNS/$run")" "$(cygpath -w "/g/Thesis/results/sentiment/runs/$run")" > /dev/null \
    || { say "STOP: could not link $run to G:"; return 1; }
  gpu_free 2500 0 || return 1
  say "$run: start"
  if $PY -m src.sentiment.train_classifier --config "configs/sentiment/$cfg.json" --seed "$seed" > "$LOGS/$run.console.log" 2>&1; then
    say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1) (best epoch $(sed -n 's/.*"best_epoch": \([0-9]*\).*/\1/p' "$RUNS/$run/train_log.json" | head -1))"
  else say "FAILED $run (see $LOGS/$run.console.log)"; fi
}
# Run list, interleaved (seed -> BERT -> set) so a partial queue still has matched runs.
LIST=results/sentiment/queue_sg03_eesa_$STAGE.runs.txt
: > "$LIST"
for seed in 42 43 44; do for b in $BERTS; do for sg in $READY; do
  tag=${sg%_*}; g=${sg##*_}; arm=${tag#sg03}; arm=${arm%_eesa}
  echo "${SR}${arm}_eesa_${b}_$g $seed" >> "$LIST"
done; done; done
say "${SR^^}-EESA: $(wc -l < "$LIST") runs, two at a time"
gpu_free 6000 60
# Two workers: worker k takes every second line of the list. The list is loaded into an array first and the
# counters are local: in the first passes (2026-11-15 12:19 and 13:07) gpu_free's loop variable overwrote the
# worker's line counter and the list was read while runs were going, so runs were skipped (42, then 43 of 63
# finished) and false "aborted folder" notes were logged. No run was damaged.
worker() {
  local k=$1 n=0 line lines
  mapfile -t lines < "$LIST"
  for line in "${lines[@]}"; do
    if [ $((n % 2)) -eq "$k" ]; then run_one ${line% *} ${line#* } < /dev/null || return 1; fi
    n=$((n + 1))
  done
}
worker 0 & W0=$!
sleep 20
worker 1 & W1=$!
wait $W0 $W1
done_n=0
while read -r cfg seed; do [ -f "$RUNS/${cfg}_seed$seed/train_log.json" ] && done_n=$((done_n + 1)); done < "$LIST"
$PY -m src.sentiment.summarize_quality > /dev/null 2>&1
say "DONE stage $STAGE ($done_n/$(wc -l < "$LIST") runs finished)"
