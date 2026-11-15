"""Pick the epoch count for SR05-EESA / SR06-EESA from the 10-epoch real-only pilot (Ammar, 2026-11-14).

Pilot: sr05_eesa_<bert>_seed<42-44>, EESA train only, 10 epochs, 7 BERTs x 3 seeds = 21 runs.
Rule (fixed before the pilot ran): mean dev micro F1 per epoch over the 21 runs; take the earliest epoch whose
mean is within MARGIN points of the best epoch's mean. Real-only runs only, so no synthetic set and no test
score influences the choice. Prints the chosen epoch count; writes results/sentiment/eesa_epoch_pilot.json.
Caveat: epoch e of a 10-epoch run is not exactly a run trained for e epochs (the learning rate decays over 10).
"""
import json
import statistics as st
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
RUNS = ROOT / "results/sentiment/runs"
BERTS = ["marbertv2", "marbert", "arabertv02_twitter", "arbert", "arbertv2", "camelbert_mix", "camelbert_da"]
MARGIN = 0.25

if __name__ == "__main__":
    # Dev micro F1 (= accuracy) of every pilot run at every epoch.
    per_epoch: dict[int, list[float]] = {}
    per_bert: dict[str, dict[int, list[float]]] = {}
    for b in BERTS:
        for seed in (42, 43, 44):
            log = json.loads((RUNS / f"sr05_eesa_{b}_seed{seed}" / "train_log.json").read_text(encoding="utf-8"))
            assert log["config"]["epochs"] == 10 and len(log["epochs"]) == 10, (b, seed)
            for e in log["epochs"]:
                per_epoch.setdefault(e["epoch"], []).append(e["dev_accuracy"])
                per_bert.setdefault(b, {}).setdefault(e["epoch"], []).append(e["dev_accuracy"])

    # The rule: earliest epoch within MARGIN of the best mean.
    means = {e: st.fmean(v) for e, v in sorted(per_epoch.items())}
    best = max(means, key=means.get)
    chosen = min(e for e, m in means.items() if m >= means[best] - MARGIN)

    out = {"rule": f"earliest epoch with mean dev micro F1 within {MARGIN} of the best epoch's mean (21 real-only runs)",
           "mean_dev_micro_f1": {e: round(m, 2) for e, m in means.items()}, "best_epoch": best, "chosen_epochs": chosen,
           "per_bert": {b: {e: round(st.fmean(v), 2) for e, v in d.items()} for b, d in per_bert.items()}}
    (ROOT / "results/sentiment/eesa_epoch_pilot.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out["mean_dev_micro_f1"]), file=sys.stderr)
    print(chosen)
