#!/usr/bin/env bash
# SG04-PN (D-027, test-contaminated): POS/NEG pairs of SG04 grown to 3,600 texts per generator, then quality rows.
# Stops before training: the rows go to Ammar and the sheet first; SR12-3600 is queue_sr12_3600.sh.
#   per generator: top up with new pairs (same prompts), pool with the old pairs, SG04 filter, select with
#   the SR12 fidelity per type; raise the scale until no group is short. Scales are per generator (yields differ).
# Restartable: generation resumes, the short pool / filter / select steps are repeated.
# Log: results/sentiment/queue_sg04pn.log; console output per step in results/sentiment/logs/.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HOME=F:/Thesis/hf_home HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOGS=results/sentiment/logs
SYN=data/synthetic/sentiment
LOG=results/sentiment/queue_sg04pn.log
GENS="aya qwen3 fanar"
declare -A SCALES=([aya]="0.75 1.0 1.3" [qwen3]="1.8 2.2 2.6" [fanar]="1.15 1.4 1.7")
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

# 1. Generate, pool, filter, select.
for g in $GENS; do
  sg=sg04pn_$g
  ok=0
  for scale in ${SCALES[$g]}; do
    gpu_free; say "$sg: generating at scale $scale"
    $PY -m src.sentiment.generate_pairs --config configs/sentiment/generation/$sg.json --scale $scale >> "$LOGS/$sg.console.log" 2>&1 \
      || { say "STOP $sg: generation failed, see $LOGS/$sg.console.log"; exit 1; }
    $PY -m src.sentiment.sg04pn pool --gen $g > "$LOGS/${sg}_pool.console.log" 2>&1 || { say "STOP $sg: pool failed"; exit 1; }
    $PY -m src.filtering.filter_synthetic --data "$SYN/$sg.jsonl" --config configs/filtering/sentiment_pairs_sg04.json \
      > "$LOGS/${sg}_filter.console.log" 2>&1 || { say "STOP $sg: filter failed"; exit 1; }
    gpu_free
    $PY -m src.sentiment.sg04pn select --gen $g > "$LOGS/${sg}_select.console.log" 2>&1 || { say "STOP $sg: selection failed"; exit 1; }
    say "$sg (scale $scale): $(tail -1 "$LOGS/${sg}_select.console.log")"
    if grep -q "shortfall none" "$LOGS/${sg}_select.console.log"; then ok=1; break; fi
  done
  [ "$ok" -eq 1 ] || { say "STOP $sg: still short after the last scale; decision for Ammar"; exit 1; }
done

# 2. Quality, needs all three generators.
gpu_free; say "SG04-PN quality: measuring"
$PY -m src.sentiment.measure_quality --set sg04pn > "$LOGS/sq_sg04pn.console.log" 2>&1 || { say "STOP: quality failed"; exit 1; }
sets="real=data/processed/sentiment/arsarcasm_v2_train.jsonl"
for g in $GENS; do sets="$sets sg04pn_$g=$SYN/sg04pn_$g.selected.jsonl"; done
$PY -m src.quality.topic_spread --names configs/quality/topic_names_universal_clean_k50.json --sets $sets \
  --out results/quality/sentiment/universal_topics_sg04pn > "$LOGS/sq_topics_sg04pn.console.log" 2>&1 || { say "STOP: topic spread failed"; exit 1; }
$PY -m src.sentiment.summarize_quality > /dev/null 2>&1
say "DONE (quality rows ready; training waits for the rows)"
