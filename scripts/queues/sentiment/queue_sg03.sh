#!/usr/bin/env bash
# Sentiment SG03 queue: minimal pairs for the hard-case types (SG03) and the size-matched random
# control (SG03-random), Fanar / Qwen3 / Aya as in SG02, then BERT training (Ammar 2026-10-30).
#   1. per generator and set: generate 2,200 pair requests (1.1 x 2,000 target pairs), resumable;
#      filter (configs/filtering/sentiment_pairs.json), keep 2,000 complete pairs per set (select_pairs);
#      if a type is short, top up to 1.4x, 1.8x, then 2.4x requests and refilter (as SG02)
#   2. SQ04: quality of the selected sets (src.sentiment.measure_quality --set sg03 / sg03r, and the universal
#      topic spread), before any training
#   3. SR05 (+ SG03) and SR06 (+ SG03-random): 7 BERTs x 3 generators x seeds 42/43/44, alternating
#      SR05 / SR06 so a partial queue still has matched runs
# Restartable: every finished step is skipped; an interrupted generation resumes where it stopped.
# A failing generator is logged and skipped. Log: results/sentiment/queue_sg03.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
RUNS=results/sentiment/runs
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg03.log
GENS="fanar qwen3 aya"
SETS="sg03 sg03r"
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

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l) (SG03 code is not committed, Ammar 2026-10-30)"

# 1. Generate, filter, select.
declare -A READY
for g in $GENS; do
  for s in $SETS; do
    sg=${s}_$g
    cfg=configs/sentiment/generation/$sg.json
    ok=0
    for scale in 1.1 1.4 1.8 2.4; do
      want=$($PY -c "import math,json;t=json.load(open('prompts/sentiment/pairs_targeted_v1.json',encoding='utf-8'))['types'];print(2*sum(math.ceil(v['target_pairs']*$scale) for v in t.values()))")
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
        $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment_pairs.json \
          > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "$sg: filter failed"; break; }
        $PY -m src.sentiment.select_pairs --data "$SYN/$sg.filtered.jsonl" \
          > "$LOGS/${sg}_select.console.log" 2>&1 || { say "$sg: selection failed"; break; }
        say "$sg (scale $scale): $(tail -1 "$LOGS/${sg}_select.console.log")"
      fi
      if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
    done
    if [ "$ok" -eq 1 ]; then READY[$sg]=1; else say "SKIP $sg: could not reach the target pairs, no training"; fi
  done
done

# 2. SQ04 quality rows per set, needs all three generators of that set.
for s in $SETS; do
  if [ -z "${READY[${s}_fanar]:-}" ] || [ -z "${READY[${s}_qwen3]:-}" ] || [ -z "${READY[${s}_aya]:-}" ]; then
    say "STOP: not all generators of $s reached the target; SQ04 needs all three"; exit 1
  fi
  if [ ! -f results/quality/sentiment/${s}_quality.json ]; then
    gpu_free; say "SQ04 $s: measuring"
    $PY -m src.sentiment.measure_quality --set $s > "$LOGS/sq04_$s.console.log" 2>&1 || { say "STOP: SQ04 $s failed"; exit 1; }
    say "SQ04 $s done"
  fi
done
# Universal topic spread (quality row 5, as SQ03 of 2026-10-28) of the six selected sets and S1 train.
if [ ! -f results/quality/sentiment/universal_topics_sg03.json ]; then
  gpu_free; say "topic spread: measuring"
  sets="real=data/processed/sentiment/arsarcasm_v2_train.jsonl"
  for s in $SETS; do for g in $GENS; do sets="$sets ${s}_$g=$SYN/${s}_$g.selected.jsonl"; done; done
  $PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
    --out results/quality/sentiment/universal_topics_sg03 > "$LOGS/sq_topics_sg03.console.log" 2>&1 \
    || { say "STOP: topic spread failed"; exit 1; }
  say "topic spread done"
fi

# 3. SR05 / SR06: BERT training, 3 seeds each, alternating the two conditions.
for g in $GENS; do
  for tag in $BERTS; do
    for seed in 42 43 44; do
      for sr in sr05 sr06; do
        run=${sr}_${tag}_${g}_seed${seed}
        if [ -f "$RUNS/$run/train_log.json" ]; then continue; fi
        # A folder without train_log.json is an aborted run: never overwritten.
        if [ -d "$RUNS/$run" ]; then say "NOTE $run: aborted folder found, left untouched"; continue; fi
        gpu_free; say "$run: start"
        if $PY -m src.sentiment.train_classifier --config configs/sentiment/${sr}_${tag}_$g.json --seed $seed \
            > "$LOGS/$run.console.log" 2>&1; then
          say "$run: $(grep -h '^DEV' "$LOGS/$run.console.log" | tail -1)"
        else say "FAILED $run (see $LOGS/$run.console.log)"; fi
      done
    done
  done
done

say "DONE"
