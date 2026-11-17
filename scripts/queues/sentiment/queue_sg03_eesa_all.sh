#!/usr/bin/env bash
# Rest of the matrix-language pilot in one chain (Ammar, 2026-11-15: "queue everything"), D-037:
#   1. Qwen3, dialect-matrix arm with prompt v3 (set sg03dm3_eesa_qwen3, runs sr07dm3_eesa_*_qwen3)
#   2. Aya and Fanar, arms nm (v2), dm3 (v3) and em (v2), then their SR07-EESA runs (3 epochs)
#   3. SR08-EESA: every complete SG03-EESA set again with 8 epochs (D-036 recipe; baseline SR05-EESA real only)
# Each stage is queue_sg03_eesa.sh (restartable; a finished stage is passed through in a few minutes).
# Log: results/sentiment/queue_sg03_eesa.log (each stage ends with "DONE stage ..."; the chain with "ALL DONE").
set -u
cd /f/Thesis/code
Q=scripts/queues/sentiment/queue_sg03_eesa.sh
LOG=results/sentiment/queue_sg03_eesa.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
say "chain start (pid $$)"
ARMS="dm3" bash $Q qwen3
ARMS="nm dm3 em" bash $Q aya fanar
TRAIN_ONLY=1 SR=sr08 ARMS="nm dm dm3 em" bash $Q qwen3 aya fanar
say "ALL DONE"
