#!/usr/bin/env bash
# SG02-EESA and SG02-random-EESA generation (D-034; prompt fewshot_eesa_v1).
# Per set (sg02_eesa = targeted, sg02r_eesa = random control) and generator (Qwen3, Aya, Fanar; fastest first):
#   0. smoke test: 24 requests (--limit 24, separate _limit24 file); skip the generator if none parse
#   1. generate ceil(target x 1.6) requests per group (2,114), resumable
#   2. filter (configs/filtering/sentiment_eesa.json: no duplicates within the set or against EESA train/dev),
#   3. select each group's target (select_synthetic --config; 1,320 in total); overlap with EESA test reported only.
#      If a group is short after filtering, top up with --margin 2.2, then 3.0, and refilter.
# Stops after selection: the quality rows are shown to Ammar before any training (SR04-EESA, SR04-random-EESA).
# Restartable: finished steps are skipped; an interrupted generation resumes where it stopped.
# Log: results/sentiment/queue_sg02_eesa.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg02_eesa.log
GENS="qwen3 aya fanar"
SETS="sg02_eesa sg02r_eesa"
mkdir -p "$LOGS"
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }

# Wait (up to 60 min) while another process holds the GPU (it is shared with other chats).
gpu_free() {
  # Windows frees a finished model's memory late (os error 1455, 2026-11-08): pause before every load.
  sleep 60
  for i in $(seq 1 12); do
    free=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits | head -1)
    [ "$free" -ge 6000 ] && return 0
    say "waiting: only ${free} MiB GPU memory free"; sleep 300
  done
  say "STOP: GPU busy for 60 min"; exit 1
}

say "queue start (pid $$), git $(git rev-parse --short HEAD), uncommitted files: $(git status --porcelain | wc -l)"
for set in $SETS; do
  for g in $GENS; do
    sg=${set}_$g
    cfg=configs/sentiment/generation/$sg.json
    [ -f "$SYN/$sg.selected.jsonl" ] && grep -q "shortfall none" "$LOGS/${sg}_select.console.log" 2>/dev/null \
      && [ "$SYN/$sg.selected.jsonl" -nt "$SYN/$sg.jsonl" ] && { say "$sg: already complete"; continue; }

    # 0. Smoke test (kept apart from the full set).
    if [ ! -f "$SYN/${sg}_limit24.jsonl" ]; then
      gpu_free; say "$sg: smoke test (24 requests)"
      $PY -m src.sentiment.generate --config "$cfg" --limit 24 > "$LOGS/${sg}_limit24.console.log" 2>&1 \
        || { say "$sg: smoke test failed, retrying in 2 min"; sleep 120;
             $PY -m src.sentiment.generate --config "$cfg" --limit 24 > "$LOGS/${sg}_limit24.console.log" 2>&1 \
               || { say "SKIP $sg: smoke test failed twice (see $LOGS/${sg}_limit24.console.log)"; continue; }; }
    fi
    parsed=$(grep -c '"parse_ok": true' "$SYN/${sg}_limit24.jsonl" 2>/dev/null); parsed=${parsed:-0}
    say "$sg: smoke test $parsed/24 parsed"
    [ "$parsed" -eq 0 ] && { say "SKIP $sg: no smoke-test output parsed"; continue; }

    # 1-3. Generate, filter, select; top up with a larger margin if a group is short.
    ok=0
    for margin in 1.6 2.2 3.0; do
      want=$($PY -c "import json,math;c=json.load(open('$cfg',encoding='utf-8'));print(sum(math.ceil(x['target']*$margin) for x in c['cells']))")
      for attempt in 1 2; do
        n=$( [ -f "$SYN/$sg.jsonl" ] && wc -l < "$SYN/$sg.jsonl" || echo 0 )
        [ "$n" -ge "$want" ] && break
        gpu_free; say "$sg: generating ($n/$want done, margin $margin, attempt $attempt)"
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
    [ "$ok" -eq 1 ] || say "SKIP $sg: could not reach every group's target"
  done
done
say "DONE (generation only; quality rows next, then SR04-EESA after Ammar has seen them)"
