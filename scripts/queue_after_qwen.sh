#!/usr/bin/env bash
# Queue to run after the Qwen3 seed-42 QLoRA run: (1) checkpoint kill-and-resume test,
# (2) Fanar smoke test (VRAM check), (3) Fanar full run. Stops at the first failure.
# Everything is logged to results/queue_after_qwen.log. Run from the repo root.
set -u
cd /f/Thesis/code
export PYTHONIOENCODING=utf-8 HF_HUB_CACHE=F:/Thesis/models HF_HUB_OFFLINE=1
PY=.venv/Scripts/python.exe
LOG=results/queue_after_qwen.log
say() { echo "[$(date '+%F %T')] $*" | tee -a "$LOG"; }
TRAIN="$PY -m src.training.train_lora_classifier"

# 0. Wait for the Qwen run to finish (its train_log.json appears) or its process to vanish.
say "waiting for Qwen3 seed 42 to finish"
until [ -f results/runs/lora_real_only_qwen3_seed42/train_log.json ] || ! tasklist //FI "PID eq ${QWEN_PID:-37020}" | grep -q python; do sleep 60; done
if [ ! -f results/runs/lora_real_only_qwen3_seed42/train_log.json ]; then
  say "STOP: Qwen process ended without train_log.json (crashed or killed)"; exit 1; fi
say "Qwen3 finished: $(grep -h DEV results/lora_real_only_qwen3_seed42.console.log)"

# 1. Checkpoint test: uninterrupted reference vs a run killed after a checkpoint and resumed.
if grep -q "^DEV" results/resumetest_ref.console.log 2>/dev/null; then
  say "1/3 checkpoint test: reusing finished reference run (training is deterministic)"
else
  say "1/3 checkpoint test: reference run"
  $TRAIN --config configs/lora_resumetest_ref_qwen3.json --limit 2000 > results/resumetest_ref.console.log 2>&1 \
    || { say "STOP: reference run failed"; exit 1; }
fi
rm -rf results/runs/lora_resumetest_kill_qwen3_seed42_limit2000 results/resumetest_kill_part*.log   # start clean
say "1/3 checkpoint test: run to be killed"
# Launch as a Windows process so we know its PID, and later kill only that process tree.
# The PID goes to a file: capturing PowerShell's output with $(...) made bash wait until
# the training run finished (the child inherits the pipe), so the kill came too late.
powershell.exe -NoProfile -Command "\$env:PYTHONIOENCODING='utf-8'; \$env:HF_HUB_CACHE='F:/Thesis/models'; \$env:HF_HUB_OFFLINE='1'; (Start-Process -FilePath 'F:\Thesis\code\.venv\Scripts\python.exe' -ArgumentList '-m','src.training.train_lora_classifier','--config','configs/lora_resumetest_kill_qwen3.json','--limit','2000' -WorkingDirectory 'F:\Thesis\code' -RedirectStandardOutput 'F:\Thesis\code\results\resumetest_kill_part1.console.log' -RedirectStandardError 'F:\Thesis\code\results\resumetest_kill_part1.stderr.log' -WindowStyle Hidden -PassThru).Id" > results/resumetest_kill.pid
kpid=$(tr -d $'\r\n' < results/resumetest_kill.pid)
say "run to be killed has PID $kpid"
until grep -q "checkpoint saved" results/resumetest_kill_part1.console.log 2>/dev/null; do sleep 5; done
sleep 45   # train a little past the checkpoint, so the resume must discard unsaved work
taskkill //F //T //PID "$kpid" > /dev/null 2>&1   # /T: also the real python child of the venv launcher
sleep 10
say "killed after: $(grep -h 'checkpoint saved' results/resumetest_kill_part1.console.log | tail -1)"
grep -q "^epoch 1:" results/resumetest_kill_part1.console.log && { say "STOP: test invalid, the run finished its epoch before the kill"; exit 1; }
$TRAIN --config configs/lora_resumetest_kill_qwen3.json --limit 2000 > results/resumetest_kill_part2.console.log 2>&1 \
  || { say "STOP: resumed run failed"; exit 1; }
grep -q "resumed from checkpoint" results/resumetest_kill_part2.console.log || { say "STOP: run did not resume"; exit 1; }
ref=$(grep -h "^epoch 1:" results/resumetest_ref.console.log); res=$(grep -h "^epoch 1:" results/resumetest_kill_part2.console.log)
say "reference: $ref"; say "resumed:   $res"
# Compare train loss (2 decimals) and validation macro F1 (within 1 point; GPU kernels are not bit-exact).
$PY - "$ref" "$res" <<'PYEOF' || { say "STOP: resumed run differs from reference"; exit 1; }
import re, sys
a, b = (re.search(r"train loss ([\d.]+)\s+val macro F1 ([\d.]+)", s).groups() for s in sys.argv[1:3])
ok = abs(float(a[0]) - float(b[0])) < 0.01 and abs(float(a[1]) - float(b[1])) < 1.0
print("loss", a[0], b[0], "val F1", a[1], b[1], "OK" if ok else "DIFFERENT"); sys.exit(0 if ok else 1)
PYEOF
say "1/3 checkpoint test passed"

# 2. Fanar smoke test: must stay under the card's 8192 MiB.
say "2/3 Fanar smoke test (500 sentences)"
$TRAIN --config configs/lora_real_only_fanar.json --limit 500 > results/lora_fanar_limit500.console.log 2>&1 \
  || { say "STOP: Fanar smoke test failed"; exit 1; }
dev=$(grep -h "^DEV" results/lora_fanar_limit500.console.log); say "Fanar smoke: $dev"
vram=$(echo "$dev" | sed -n 's/.*peak VRAM \([0-9]*\) MiB.*/\1/p')
[ "${vram:-99999}" -lt 8192 ] || { say "STOP: Fanar peak VRAM ${vram} MiB does not fit 8192 MiB"; exit 1; }

# 3. Fanar full run (resumable: rerun this same command to continue after a crash).
say "3/3 Fanar full run, seed 42"
$TRAIN --config configs/lora_real_only_fanar.json > results/lora_real_only_fanar_seed42.console.log 2>&1 \
  || { say "STOP: Fanar run failed (rerun the command to resume from the checkpoint)"; exit 1; }
say "DONE: $(grep -h DEV results/lora_real_only_fanar_seed42.console.log)"
