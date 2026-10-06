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
| R09 | 2026-10-06 | `UBC-NLP/MARBERTv2` | D1, real only | 42 | 70.00 | 69.76 | 72.54 | `baseline_real_only_marbertv2_seed42` |
| R09 | 2026-10-06 | `UBC-NLP/MARBERTv2` | D1, real only | 43 | 69.62 | 70.99 | 70.74 | `baseline_real_only_marbertv2_seed43` |
| R09 | 2026-10-06 | `UBC-NLP/MARBERTv2` | D1, real only | 44 | 70.70 | 72.06 | 71.57 | `baseline_real_only_marbertv2_seed44` |
| R10 | 2026-10-06 | `aubmindlab/bert-base-arabertv02-twitter` | D1, real only | 42 | 70.80 | 70.14 | 74.77 | `baseline_real_only_arabertv02_twitter_seed42` |
| R10 | 2026-10-06 | `aubmindlab/bert-base-arabertv02-twitter` | D1, real only | 43 | 70.83 | 69.69 | 75.32 | `baseline_real_only_arabertv02_twitter_seed43` |
| R10 | 2026-10-06 | `aubmindlab/bert-base-arabertv02-twitter` | D1, real only | 44 | 69.92 | 67.62 | 75.26 | `baseline_real_only_arabertv02_twitter_seed44` |
| R10 | 2026-10-06 | TF-IDF + logistic regression | D1, real only | 42 | 62.52 | 64.71 | 62.64 | `baseline_real_only_tfidf_lr_seed42` |
| R10 | 2026-10-06 | TF-IDF + logistic regression | D1, real only | 43 | 62.59 | 67.21 | 61.66 | `baseline_real_only_tfidf_lr_seed43` |
| R10 | 2026-10-06 | TF-IDF + logistic regression | D1, real only | 44 | 62.62 | 65.56 | 62.54 | `baseline_real_only_tfidf_lr_seed44` |

**R05–R07 mean ± std:** macro F1 **71.34 ± 1.03**, precision 71.67 ± 2.54, recall 72.98 ± 0.40.
**R08 mean ± std:** macro F1 **68.71 ± 0.35**, precision 74.89 ± 1.48, recall 65.49 ± 0.59.
**R09 (MARBERTv2) mean ± std:** macro F1 **70.11 ± 0.55**, precision 70.94 ± 1.15, recall 71.62 ± 0.90.
**R10 (AraBERTv02-Twitter) mean ± std:** macro F1 **70.52 ± 0.52**, precision 69.15 ± 1.34, recall 75.12 ± 0.30.
**R10 (TF-IDF + LR) mean ± std:** macro F1 **62.58 ± 0.05**, precision 65.83 ± 1.27, recall 62.28 ± 0.54.

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

**R09: MARBERTv2 real-only baseline.**
- Config: `configs/baseline_real_only_marbertv2.json`, seeds 42/43/44. Identical to R05–R07 (`configs/baseline_real_only.json`) except the model: `UBC-NLP/MARBERT` → `UBC-NLP/MARBERTv2`. Commit `60b1cdd` (committed before the run; matches the logs). About 7.1 min per run. Every seed picked epoch 2.
- **Result:** 70.11 ± 0.55, 1.2 points below MARBERT v1 (R05–R07, 71.34 ± 1.03). That is inside the seed spread and the ~2-point noise level of the 120-sentence dev set, so v2 is **not shown to be better or worse** than v1 here.
- Per dialect, v2 is clearly better on Algeria (69.4 vs 62.0, the weakest dialect so far) and worse on Sudan (63.3 vs 72.2) and Egypt (80.2 vs 86.4). With 120 sentences each per-dialect number rests on few positives, so these are leads, not findings.
- Validation macro F1 (geolocation-labelled split) ≈80.6–81.1 at the chosen epoch.

**R10: AraBERTv02-Twitter and TF-IDF + LR real-only baselines.**
- AraBERT config: `configs/baseline_real_only_arabertv02_twitter.json`, identical to R09 except the model. Commit `60b1cdd`. About 6.6 min per run. Raw text is fed to the model: aubmindlab's recommended `ArabertPreprocessor` is **not** applied, because the leaderboard feeds raw text and normalization must be an explicit step (CLAUDE.md). Whether the preprocessor would help is untested.
- **AraBERT result:** 70.52 ± 0.52, level with MARBERTv2 (70.11) and within noise of MARBERT v1 (71.34). It has the highest recall of our trained models (75.1) and lower precision (69.2). Seed 42 picked epoch 1, seeds 43/44 epoch 2.
- TF-IDF + LR config: `configs/baseline_real_only_tfidf_lr.json`, script `src/training/train_tfidf.py`. Character 2–5-grams (within word boundaries, max 300k) + word 1–2-grams (whitespace tokens), sublinear TF, min_df 2, no lowercasing or normalization (~324k features); one liblinear logistic regression per dialect, C = 1.0, threshold 0.3. Same D1 data and seeded 90/10 split as the transformers; settings fixed in advance, not tuned on validation or dev. Commit `21461f8`. About 30 s per run on CPU.
- **TF-IDF + LR result:** 62.58 ± 0.05, about 8 points below the three transformers. Its spread is tiny because the seed only changes the train/validation split (the solver is deterministic). It is weakest on Algeria (46.9) and Sudan (53.8). It cannot be submitted to the leaderboard (the Space only loads Hub transformers), so it is a dev-only reference.
- The first TF-IDF attempt (commit `60b1cdd`) crashed at full data size: joblib hands large arrays to worker processes as read-only memory maps and liblinear needs writable input (`WRITEBACKIFCOPY base is read-only`). The 500-record smoke test was too small to trigger it. Fixed in `21461f8` (`parallel_config(max_nbytes=None)`); no results came from the failed attempt.
- **Overall (R05–R10):** the three transformer classifiers are within ~1.2 points of each other on dev, below the noise level, so the choice of main classifier cannot be settled by dev score alone. TF-IDF + LR is clearly weaker.

## Next runs

| ID | Model | What | Why |
|---|---|---|---|
| G01 | `QCRI/Fanar-1-9B-Instruct` | Generator feasibility: 4-bit load, 20 sentences (`scripts/check_generators.py`) | VRAM peak, tokens/s, is the output dialectal? Runs automatically once the download finishes and the GPU is free |
| G02 | `google/gemma-2-9b-it` | Same | Same |
| G03 | `humain-ai/ALLaM-7B-Instruct-preview` | Same | Same |

---

## Reference

### Data versions

| ID | File | SHA-256 (first 12) | Contents |
|---|---|---|---|
| D1 | `data/processed/nadi_lahjatbert.jsonl` | `d299edd78f3d` | 58,384 unique NADI 2020/2021/2023 texts, 18 LahjatBERT labels. Links → `URL`, mentions → `USER`, 365 quotes restored. No normalization. All-18 and zero-label texts kept. Built by `src/data/build_dataset.py`; details in `decisions.md`. |

### Quality measurements (`src/quality/measure.py`, results in `results/quality/`)

| ID | Date | Data | n | Exact / near dup | TTR | Distinct-2 | Self-BLEU | E5 cos. dist. | Vendi | DID-nadi top-1 agree | DID-madar top-1 agree | ALDi mean | File |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q01 | 2026-10-06 | D1 random sample (seed 42) | 2000 | 0.05% / 0.10% | 0.514 | 0.948 | 0.063 | 0.163 | 3.77 | 61.5% (429 single-label texts) | 49.0% (406) | 0.603 | `real_d1_sample2000_seed42.json` |

**Q01 notes.** Reference values for comparing synthetic sets (measure them at the same `--sample 2000`). The DID scorers agree with the LahjatBERT single label on only 62% / 49% of real tweets (kappa 0.55 / 0.38; the two scorers agree with each other with kappa 0.26), so a top-1 DID fidelity filter would also reject about 40% of real data: fidelity thresholds must be set relative to these numbers, not to 100%. Per-dialect DID-nadi agreement is 0% for Bahrain, Jordan and Palestine (small n) and 82% for Egypt.

### Scorer validation against human gold (`src/quality/validate_scorers.py`, results in `results/scorers/`)

| ID | Date | Data | Scorer | Top-1 macro F1 / P / R | Mass ≥ 0.3 macro F1 / P / R | Top-1 in gold | File |
|---|---|---|---|---|---|---|---|
| S01 | 2026-10-06 | MLADI dev (120, 8 dialects) | CAMeLBERT DID-nadi | 22.77 / 79.62 / 15.10 | 23.78 / 86.58 / 15.63 | 48/59 = 81.4% (61 unscorable) | `S01.json` |
| S01 | 2026-10-06 | MLADI dev (120, 8 dialects) | CAMeLBERT DID-madar | 19.07 / 59.03 / 12.79 | 19.07 / 52.81 / 13.03 | 41/65 = 63.1% (55 unscorable) | `S01.json` |
| S01 | 2026-10-06 | MLADI dev (120, 8 dialects) | Sentence-ALDi | Spearman ρ with number of valid dialects = −0.44 (p = 4.2e-07) | | | `S01.json` |

**S01 notes.** Commit `3f39088`. Checks the scorers against the human MLADI labels (label trust rule) before they are used as fidelity filters.
- Low macro F1 is expected and not the point: both DID models are single-label, while dev sentences are valid in several dialects, so recall is capped. What matters for a fidelity filter is **precision / top-1 in gold**: when the scorer names a dev dialect, is that dialect valid?
- **DID-nadi is clearly the better filter:** top-1 in gold 81% vs 63%, macro precision 80–87 vs 53–59. This agrees with Q01 (agreement with D1 labels: kappa 0.55 vs 0.38). Evidence for the open DID-variant question; not decided yet.
- **Half the dev sentences cannot be checked:** the top country is outside the 8 dev dialects for 61 (nadi) / 55 (madar) of 120 sentences, e.g. Saudi_Arabia 20×, Libya 10× for nadi. Those sentences may still be valid in that country; the dev set has no label to tell.
- **Per dialect (nadi, top-1):** Egypt is reliable (P 96, R 56); Jordan (P 50) and Syria (P 56) are weak. Levantine fidelity checks will be the least trustworthy.
- **ALDi:** more dialectal sentences are valid in fewer dialects (mean ALDi 0.17 for sentences valid in all 8 vs 0.65–0.78 for 1–5). That fits ALDi as a proxy for how dialect-specific a sentence is.
- E5 is an embedding model with no labelled target, so it is not validated here.

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
| Classifier | `UBC-NLP/MARBERTv2` | ~163M | yes | Main classifier (R05–R07 used v1; R09 used v2) |
| Classifier | `aubmindlab/bert-base-arabertv02-twitter` | 135M | yes | |
| Classifier | TF-IDF + logistic regression | — | CPU | |
