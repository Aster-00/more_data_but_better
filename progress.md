# Progress log

**Evaluated on:** MLADI dev set (120 sentences, 8 dialects), leaderboard settings (max length 128, threshold 0.3). **Metric:** macro F1. The private test set has not been used.
Numbers are copied from each run's result folder under `results/runs/`. The generated summary is in `results/tables/dev_summary.md`.

## All runs

| ID | Date | Model | Trained on | Seed | Macro F1 | Precision | Recall | Result folder |
|---|---|---|---|---|---|---|---|---|
| R00 | 2026-10-06 | none (organizers' sample submission) | — | — | 42.47 | 38.14 | 50.33 | — |
| R01 | 2026-10-06 | `Mohamedelzeftawy/LahjatBERT_cl_cardinality` (MARBERT) | published, not trained by us | — | 72.68 | 68.98 | 80.64 | `Mohamedelzeftawy__LahjatBERT_cl_cardinality` |
| R02 | 2026-10-06 | `Mohamedelzeftawy/LahjatBERT_cl_aldi` (MARBERT) | published, not trained by us | — | 70.27 | 71.35 | 71.32 | `Mohamedelzeftawy__LahjatBERT_cl_aldi` |
| R03 | 2026-10-06 | `Mohamedelzeftawy/LahjatBERT_baseline` (MARBERT) | published, not trained by us | — | 67.41 | 73.66 | 63.66 | `Mohamedelzeftawy__LahjatBERT_baseline` |
| R04 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, 500 examples (smoke test) | 42 | 53.2 | — | 100 | deleted |
| R05 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only | 42 | 70.65 | 69.75 | 73.12 | `baseline_real_only_seed42` |
| R06 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only | 43 | 72.52 | 74.55 | 72.53 | `baseline_real_only_seed43` |
| R07 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only | 44 | 70.84 | 70.72 | 73.30 | `baseline_real_only_seed44` |
| R08 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only, LahjatBERT settings | 42 | 69.00 | 75.43 | 65.67 | `repro_lahjatbert_baseline_seed42` |
| R08 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only, LahjatBERT settings | 43 | 68.81 | 76.03 | 64.83 | `repro_lahjatbert_baseline_seed43` |
| R08 | 2026-10-06 | `UBC-NLP/MARBERT` | D1, real only, LahjatBERT settings | 44 | 68.32 | 73.22 | 65.97 | `repro_lahjatbert_baseline_seed44` |

**R05–R07 mean ± std:** macro F1 **71.34 ± 1.03**, precision 71.67 ± 2.54, recall 72.98 ± 0.40.
**R08 mean ± std:** macro F1 **68.71 ± 0.35**, precision 74.89 ± 1.48, recall 65.49 ± 0.59.

## Run notes

**R00: metric check.** Our metric code (`src/evaluation/metrics.py`) and the official scorer give the same numbers on the sample submission, and both match the MLADI README. Our dev scores can be compared with official ones.

**R01–R03: published LahjatBERT models.** Downloaded and scored, no training. These are the reference to beat.
- Both curriculum models beat their baseline, as in their paper.
- The ranking differs from their test-set results (there cl_aldi was best). The dev set has only 120 sentences, so 1–2 point differences are noise.

**R04: smoke test.** Checked that training, saving and scoring all run end to end. The model predicts "valid" for every dialect (recall 100), which is expected after 500 examples. Not a real result.

**R05–R07: real-only baseline (condition 1).**
- Config: `configs/baseline_real_only.json` (seed changed with `--seed`). First 8 of 12 layers frozen, dropout 0.3, lr 5e-5, batch 24, 2 epochs, fp16. 90/10 random train/validation split of D1. Best epoch chosen by validation macro F1. About 7.4 min per run.
- Differences from LahjatBERT's baseline (R03): dropout 0.3 actually applied (theirs stays at 0.1 because of a bug), macro-F1 epoch selection instead of micro F1, 2 epochs instead of 3, and our own deduplicated, unnormalized D1 text.
- **Result:** about 4 points above their baseline (71.3 vs 67.4). Even the worst seed (70.65) beats it. We are level with their best model (72.7). Why we beat the baseline is not known yet; R08 will test it. (Answered by R08: the training settings, not the data.)
- Seed spread is about ±1 point, so differences under ~2 points between conditions are not results.
- Weakest dialect for every model: Algeria (~62 F1).
- ⚠️ The logs record commit `75330bf`, but the training code was not committed yet at that point.

**R08: faithful reproduction of LahjatBERT's baseline.**
- Config: `configs/repro_lahjatbert_baseline.json`, seeds 42/43/44. Same code and data (D1) as R05–R07; changed: dropout 0.3 → 0.1, epoch selection macro → micro F1, 2 → 3 epochs. 11–14 min per run.
- **Result:** 68.71 ± 0.35, within noise of their published baseline R03 (67.41) and 2.6 points below our R05–R07 (71.34 ± 1.03). With their settings we land where they did, so our D1 preparation is not why R05–R07 beat R03; the settings are.
- Lower recall drives the drop (65.5 vs 73.0); precision is higher (74.9 vs 71.7). Every dialect except Egypt falls; Algeria drops most (54.8 vs 62.0 mean F1).
- Micro-F1 selection changed nothing: every seed picked epoch 3, and validation macro and micro F1 were within 0.15 of each other at every epoch. The gap therefore comes from dropout (0.1 vs 0.3) and/or the third epoch. R08 cannot separate the two.
- Validation F1 still rose from epoch 2 to 3 in every seed (≈82.2 → ≈82.9), yet R08 scores lower on dev than the 2-epoch R05–R07. Whether the third epoch itself hurts dev is untested (dev was only scored on the selected checkpoint); if it does, geolocation-labelled validation is a poor guide for model selection.
- The logs record commit `ad08dd5`, not `3c35ac9` (the commit made before the run): the commit is read after training, and docs-only commits landed meanwhile. `git diff 3c35ac9 ad08dd5 -- src configs` is empty, so the code is the same.

## Next runs

| ID | Model | What | Why |
|---|---|---|---|
| R09 | `UBC-NLP/MARBERTv2` | Real-only baseline, 3 seeds | The thesis classifier is v2, not v1 |
| R10 | `aubmindlab/bert-base-arabertv02-twitter`, TF-IDF + LR | Real-only baseline, 3 seeds | The other two classifiers |

---

## Reference

### Data versions

| ID | File | SHA-256 (first 12) | Contents |
|---|---|---|---|
| D1 | `data/processed/nadi_lahjatbert.jsonl` | `d299edd78f3d` | 58,384 unique NADI 2020/2021/2023 texts, 18 LahjatBERT labels. Links → `URL`, mentions → `USER`, 365 quotes restored. No normalization. All-18 and zero-label texts kept. Built by `src/data/build_dataset.py`; details in `decisions.md`. |

### Model roster

Checked on the Hub on 2026-10-06. About 6.7 GB of the 8 GB of VRAM is free.

| Role | Hub ID | Size | Fits 8 GB? | Notes |
|---|---|---|---|---|
| Generator | `QCRI/Fanar-1-9B-Instruct` | 8.8B | 4-bit only | Tight fit |
| Generator | `google/gemma-2-9b-it` | 9.2B | 4-bit only | Gated: accept the license and use an access token |
| Generator | `humain-ai/ALLaM-7B-Instruct-preview` | 7.0B | 4-bit | |
| Generator | `facebook/nllb-200-1.3B` | 1.3B | yes | Translation / back-translation |
| Generator | GPT-4o-mini (optional) | — | remote | Paid: conflicts with the zero-cost rule |
| Scorer (fidelity) | `CAMeL-Lab/bert-base-arabic-camelbert-mix-did-nadi` or `-did-madar-corpus26` | ~110M | yes | Variant not decided |
| Scorer (dialectness) | `VARabi/Sentence-ALDi` | ~110M | yes | |
| Scorer (diversity) | `intfloat/multilingual-e5-large` | 560M | yes | |
| Classifier | `UBC-NLP/MARBERTv2` | ~163M | yes | Main classifier (R05–R07 used v1) |
| Classifier | `aubmindlab/bert-base-arabertv02-twitter` | 135M | yes | |
| Classifier | TF-IDF + logistic regression | — | CPU | |
