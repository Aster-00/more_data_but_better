# Progress log

**Evaluated on:** MLADI dev set (120 sentences, 8 dialects), leaderboard settings (max length 128, threshold 0.3). **Metric:** macro F1. The private test set has not been used.
Numbers are copied from `results/tables/dev_summary.md`, which `python -m src.evaluation.summarize_runs` generates from each run's result folder under `results/runs/`.

**Run IDs.** A run `R<NN>` is one fixed setup: prompt, data and training settings. Each model tried under that setup is a row `R<NN>-<model>` (e.g. `R03-marbertv2`), so models are compared only within a run. Seeds are folded into the row as mean ± std. `configs/runs.json` maps result folders to these IDs; register every new run there. Generator checks use the same scheme with `G` (`G01-fanar`).

## All runs

### R00: metric check (2026-10-06)

| ID | Trained on | Seeds | Macro F1 | Precision | Recall | Result folder |
|---|---|---|---|---|---|---|
| R00-sample_submission | organizers' sample submission, no model | — | 42.47 | 38.14 | 50.33 | — |

### R01: published LahjatBERT models, not trained by us (2026-10-06)

| ID | Hub model | Seeds | Macro F1 | Precision | Recall | Result folder |
|---|---|---|---|---|---|---|
| R01-lahjatbert_cl_cardinality | `Mohamedelzeftawy/LahjatBERT_cl_cardinality` (MARBERT) | — | 72.68 | 68.98 | 80.64 | `Mohamedelzeftawy__LahjatBERT_cl_cardinality` |
| R01-lahjatbert_cl_aldi | `Mohamedelzeftawy/LahjatBERT_cl_aldi` (MARBERT) | — | 70.27 | 71.35 | 71.32 | `Mohamedelzeftawy__LahjatBERT_cl_aldi` |
| R01-lahjatbert_baseline | `Mohamedelzeftawy/LahjatBERT_baseline` (MARBERT) | — | 67.41 | 73.66 | 63.66 | `Mohamedelzeftawy__LahjatBERT_baseline` |

### R02: smoke test, D1, 500 examples (2026-10-06)

| ID | Hub model | Seeds | Macro F1 | Precision | Recall | Result folder |
|---|---|---|---|---|---|---|
| R02-marbert | `UBC-NLP/MARBERT` | 42 | 53.2 | — | 100 | deleted |

### R03: real only (condition 1), D1, our settings (2026-10-06)

| ID | Hub model | Seeds | Macro F1 | Precision | Recall | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R03-marbert | `UBC-NLP/MARBERT` | 42, 43, 44 | **71.34 ± 1.03** | 71.67 ± 2.54 | 72.98 ± 0.40 | 70.65 / 72.52 / 70.84 | `baseline_real_only_seed*` |
| R03-arabertv02_twitter | `aubmindlab/bert-base-arabertv02-twitter` | 42, 43, 44 | **70.52 ± 0.52** | 69.15 ± 1.34 | 75.12 ± 0.30 | 70.80 / 70.83 / 69.92 | `baseline_real_only_arabertv02_twitter_seed*` |
| R03-marbertv2 | `UBC-NLP/MARBERTv2` | 42, 43, 44 | **70.11 ± 0.55** | 70.94 ± 1.15 | 71.62 ± 0.90 | 70.00 / 69.62 / 70.70 | `baseline_real_only_marbertv2_seed*` |
| R03-tfidf_lr | TF-IDF + logistic regression | 42, 43, 44 | **62.58 ± 0.05** | 65.83 ± 1.27 | 62.28 ± 0.54 | 62.52 / 62.59 / 62.62 | `baseline_real_only_tfidf_lr_seed*` |

### R04: real only, D1, LahjatBERT's settings (2026-10-06)

| ID | Hub model | Seeds | Macro F1 | Precision | Recall | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R04-marbert | `UBC-NLP/MARBERT` | 42, 43, 44 | **68.71 ± 0.35** | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.00 / 68.81 / 68.32 | `repro_lahjatbert_baseline_seed*` |

Per-dialect F1 for every run: `results/tables/dev_summary.md`.

### T: MLADI test set (leaderboard, 1,000 sentences, 11 dialects)

Test scores copied from the public leaderboard into `results/leaderboard.jsonl` (raw export: `results/leaderboard/2026-10-08T15-39_export.csv`); validation and dev scores from each run's `train_log.json` (validation = 10% held-out split of D1 at the chosen epoch). All scores are macro-averaged over the split's dialects. Models are submitted only after being chosen on dev (best dev seed per model); every submission is listed here, good or bad.

| Model | Split | Labels | Dialects | Sentences | F1 | Precision | Recall | Accuracy |
|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | validation | automatic (LahjatBERT) | 18 | 5,838 | 80.67 | 73.10 | **90.10** | — |
| | dev | human | 8 | 120 | 70.70 | 72.06 | 71.57 | — |
| | **test (T01)** | human | 11 | 1,000 | **67.71** | **63.58** | 75.36 | 77.14 |
| AraBERTv02-Twitter | validation | automatic | 18 | 5,838 | 79.13 | 69.99 | **91.29** | — |
| | dev | human | 8 | 120 | 70.83 | 69.69 | 75.32 | — |
| | **test (T02)** | human | 11 | 1,000 | **67.31** | **61.86** | 77.65 | 76.04 |

Submissions:
- **T01:** `Ammar-06/mladi-marbertv2-r03`, commit `48fc50e`, from R03-marbertv2 seed 44, `predict_binary_outcomes`. Rank 3 when read (2026-10-08).
- **T02:** `Ammar-06/mladi-arabertv02-twitter-r03`, commit `bce9290`, from R03-arabertv02_twitter seed 43, `predict_binary_outcomes`. Rank 4 when read (2026-10-08).

**T01/T02 notes.**
- MARBERTv2 (67.71) and AraBERTv02-Twitter (67.31) are 0.4 apart on test with one submission each: within noise, so the test set does not rank the two.
- F1 falls about 10 points from validation to dev and 3 more to test. The validation split shares its labelling scheme and source with the training data, so it overstates performance on human labels; use it for epoch selection only.
- **Recall** falls most from validation to dev (90–91 → 72–75): the models reproduce the automatic labels' multi-dialect pattern well but miss human-valid dialects. It is similar on dev and test.
- **Precision** holds from validation to dev (≈70–73) and drops only on test (62–64). Possible reasons, untested: the three test-only dialects (Iraq, Morocco, Saudi_Arabia), and a different mix of single- vs multi-dialect sentences in the test set. The leaderboard gives only macro scores, so per-dialect test numbers are not available to check.
- On test both models mark too many dialects per sentence (recall 75–78 vs precision 62–64). The leaderboard fixes the threshold at 0.3, so a stricter cutoff would have to be built into the model: through training, or by lowering the output-layer bias, which acts like a higher threshold (any such shift must be chosen on dev, not test).
- The rows are not strictly comparable: different dialect sets, label sources and sizes. Macro F1 is averaged per dialect, so it is not the harmonic mean of the macro P and R shown.


### G01: generator feasibility, 4-bit NF4, 20 sentences, minimal prompt (2026-10-06 / 07)

Script `scripts/check_generators.py`: 4 sentences each for Egypt, Morocco, Syria, Saudi_Arabia, Iraq; one English instruction naming the dialect; temperature 0.9, top-p 0.95, top-k 50, max 48 new tokens, seed 42. Not scored by a model yet; the counts below are from `samples.jsonl` (regex counts, not judgments).

| ID | Hub model | Status | Peak VRAM (reserved) | Load | Tokens/s | Batch | Added translation | Refusals | Foreign script | Hit 48-token cap | Result folder |
|---|---|---|---|---|---|---|---|---|---|---|---|
| G01-fanar | `QCRI/Fanar-1-9B-Instruct` | ok | 5284 MiB | 119 s | 52.68 | 5 | 16/20 | 0 | 0 | 14 | `G01_QCRI__Fanar-1-9B-Instruct` |
| G01-allam | `humain-ai/ALLaM-7B-Instruct-preview` | ok | 4562 MiB | 20 s | 46.90 | 5 | 0 | 5/20 | 0 | 0 | `G03_humain-ai__ALLaM-7B-Instruct-preview` |
| G01-qwen3 | `Qwen/Qwen3-8B` | ok | 6066 MiB | 116 s | 41.05 | 5 | 0 | 0 | 0 | 2 | `G01_Qwen__Qwen3-8B` |
| G01-gemma | `google/gemma-2-9b-it` | ok | 6174 MiB | 102 s | 27.76 | 5 | 0 | 0 | 0 | 0 | `G02_google__gemma-2-9b-it` |
| G01-jais2 | `inception42/Jais-2-8B-Chat` | ok | 5750 MiB | 92 s | 26.65 | 5 | 0 | 0 | 0 (4/20 presentation forms) | 4 | `G01_inception42__Jais-2-8B-Chat` |
| G01-falcon_h1 | `tiiuae/Falcon-H1-7B-Instruct` | ok (batch 1) | 5184 MiB | 126 s | 8.97 | 1 | 0 | 0 | 7/20 | 0 | `G01_tiiuae__Falcon-H1-7B-Instruct` |

"Foreign script" = Cyrillic, CJK or Devanagari characters. "Presentation forms" = Arabic Presentation Forms (U+FB50–FDFF, U+FE70–FEFF) instead of standard letters.

**Old IDs** (before 2026-10-06 renumbering; used in commits and console logs): R00 → R00-sample_submission; R01/R02/R03 → R01-lahjatbert_cl_cardinality / R01-lahjatbert_cl_aldi / R01-lahjatbert_baseline; R04 → R02-marbert; R05–R07 → R03-marbert; R09 → R03-marbertv2; R10 → R03-arabertv02_twitter and R03-tfidf_lr; R08 → R04-marbert; G01/G02/G03 → G01-fanar / G01-gemma / G01-allam.

## Run notes

**R00: metric check.** Our metric code (`src/evaluation/metrics.py`) and the official scorer give the same numbers on the sample submission, and both match the MLADI README. Our dev scores can be compared with official ones.

**R01: published LahjatBERT models.** Downloaded and scored, no training. These are the reference to beat.
- Both curriculum models beat their baseline, as in their paper.
- The ranking differs from their test-set results (there cl_aldi was best). The dev set has only 120 sentences, so 1–2 point differences are noise.

**R02: smoke test.** Checked that training, saving and scoring all run end to end. The model predicts "valid" for every dialect (recall 100), which is expected after 500 examples. Not a real result.

**R03-marbert: real-only baseline (condition 1).**
- Config: `configs/baseline_real_only.json` (seed changed with `--seed`). First 8 of 12 layers frozen, dropout 0.3, lr 5e-5, batch 24, 2 epochs, fp16. 90/10 random train/validation split of D1. Best epoch chosen by validation macro F1. About 7.4 min per run.
- Differences from LahjatBERT's baseline (R01-lahjatbert_baseline): dropout 0.3 actually applied (theirs stays at 0.1 because of a bug), macro-F1 epoch selection instead of micro F1, 2 epochs instead of 3, and our own deduplicated, unnormalized D1 text.
- **Result:** about 4 points above their baseline (71.3 vs 67.4). Even the worst seed (70.65) beats it. We are level with their best model (72.7). Why we beat the baseline is not known yet; R04 will test it. (Answered by R04: the training settings, not the data.)
- Seed spread is about ±1 point, so differences under ~2 points between conditions are not results.
- Weakest dialect for every model: Algeria (~62 F1).
- ⚠️ The logs record commit `75330bf`, but the training code was not committed yet at that point.

**R04-marbert: faithful reproduction of LahjatBERT's baseline.**
- Config: `configs/repro_lahjatbert_baseline.json`, seeds 42/43/44. Same code and data (D1) as R03-marbert; changed: dropout 0.3 → 0.1, epoch selection macro → micro F1, 2 → 3 epochs. 11–14 min per run.
- **Result:** 68.71 ± 0.35, within noise of their published baseline R01-lahjatbert_baseline (67.41) and 2.6 points below our R03-marbert (71.34 ± 1.03). With their settings we land where they did, so our D1 preparation is not why R03-marbert beats R01-lahjatbert_baseline; the settings are.
- Lower recall drives the drop (65.5 vs 73.0); precision is higher (74.9 vs 71.7). Every dialect except Egypt falls; Algeria drops most (54.8 vs 62.0 mean F1).
- Micro-F1 selection changed nothing: every seed picked epoch 3, and validation macro and micro F1 were within 0.15 of each other at every epoch. The gap therefore comes from dropout (0.1 vs 0.3) and/or the third epoch. R04 cannot separate the two.
- Validation F1 still rose from epoch 2 to 3 in every seed (≈82.2 → ≈82.9), yet R04-marbert scores lower on dev than the 2-epoch R03-marbert. Whether the third epoch itself hurts dev is untested (dev was only scored on the selected checkpoint); if it does, geolocation-labelled validation is a poor guide for model selection.
- The logs record commit `ad08dd5`, not `3c35ac9` (the commit made before the run): the commit is read after training, and docs-only commits landed meanwhile. `git diff 3c35ac9 ad08dd5 -- src configs` is empty, so the code is the same.

**R03-marbertv2: MARBERTv2 real-only baseline.**
- Config: `configs/baseline_real_only_marbertv2.json`, seeds 42/43/44. Identical to R03-marbert (`configs/baseline_real_only.json`) except the model: `UBC-NLP/MARBERT` → `UBC-NLP/MARBERTv2`. Commit `60b1cdd` (committed before the run; matches the logs). About 7.1 min per run. Every seed picked epoch 2.
- **Result:** 70.11 ± 0.55, 1.2 points below MARBERT v1 (R03-marbert, 71.34 ± 1.03). That is inside the seed spread and the ~2-point noise level of the 120-sentence dev set, so v2 is **not shown to be better or worse** than v1 here.
- Per dialect, v2 is clearly better on Algeria (69.4 vs 62.0, the weakest dialect so far) and worse on Sudan (63.3 vs 72.2) and Egypt (80.2 vs 86.4). With 120 sentences each per-dialect number rests on few positives, so these are leads, not findings.
- Validation macro F1 (geolocation-labelled split) ≈80.6–81.1 at the chosen epoch.

**R03-arabertv02_twitter and R03-tfidf_lr: AraBERTv02-Twitter and TF-IDF + LR real-only baselines.**
- AraBERT config: `configs/baseline_real_only_arabertv02_twitter.json`, identical to R03-marbertv2 except the model. Commit `60b1cdd`. About 6.6 min per run. Raw text is fed to the model: aubmindlab's recommended `ArabertPreprocessor` is **not** applied, because the leaderboard feeds raw text and normalization must be an explicit step (CLAUDE.md). Whether the preprocessor would help is untested.
- **AraBERT result:** 70.52 ± 0.52, level with MARBERTv2 (70.11) and within noise of MARBERT v1 (71.34). It has the highest recall of our trained models (75.1) and lower precision (69.2). Seed 42 picked epoch 1, seeds 43/44 epoch 2.
- TF-IDF + LR config: `configs/baseline_real_only_tfidf_lr.json`, script `src/training/train_tfidf.py`. Character 2–5-grams (within word boundaries, max 300k) + word 1–2-grams (whitespace tokens), sublinear TF, min_df 2, no lowercasing or normalization (~324k features); one liblinear logistic regression per dialect, C = 1.0, threshold 0.3. Same D1 data and seeded 90/10 split as the transformers; settings fixed in advance, not tuned on validation or dev. Commit `21461f8`. About 30 s per run on CPU.
- **TF-IDF + LR result:** 62.58 ± 0.05, about 8 points below the three transformers. Its spread is tiny because the seed only changes the train/validation split (the solver is deterministic). It is weakest on Algeria (46.9) and Sudan (53.8). It cannot be submitted to the leaderboard (the Space only loads Hub transformers), so it is a dev-only reference.
- The first TF-IDF attempt (commit `60b1cdd`) crashed at full data size: joblib hands large arrays to worker processes as read-only memory maps and liblinear needs writable input (`WRITEBACKIFCOPY base is read-only`). The 500-record smoke test was too small to trigger it. Fixed in `21461f8` (`parallel_config(max_nbytes=None)`); no results came from the failed attempt.
- **Overall (R03):** the three transformer classifiers are within ~1.2 points of each other on dev, below the noise level, so the choice of main classifier cannot be settled by dev score alone. TF-IDF + LR is clearly weaker.

**R05: real only on D2 (zero-label and all-18 texts removed), all four classifiers.**
- Config: `configs/card1to17_real_only*.json`, seeds 42/43/44. Identical to the matching R03 configs except `data`: D1 → D2 (`src/data/filter_cardinality.py` drops 2,271 zero-label and 7,642 all-18 texts; 48,471 of 58,384 kept, 43,624 train / 4,847 validation). Commit `3dcac61` (committed before the run; matches the logs). 5.7–6.2 min per transformer run, under 1 min per TF-IDF run. Every transformer seed picked epoch 2.
- **Result: removing these texts lowers dev macro F1 for every classifier.**

  | Model | R03 (D1) | R05 (D2) | Change |
  |---|---|---|---|
  | MARBERT | 71.34 ± 1.03 | 69.25 ± 0.54 | −2.1 |
  | AraBERTv02-Twitter | 70.52 ± 0.52 | 69.82 ± 0.65 | −0.7 |
  | MARBERTv2 | 70.11 ± 0.55 | 64.89 ± 1.44 | −5.2 |
  | TF-IDF + LR | 62.58 ± 0.05 | 56.54 ± 0.82 | −6.0 |

- MARBERTv2 and TF-IDF + LR drop clearly (well beyond the ~2-point noise level); MARBERT is at the noise boundary; AraBERT is within noise. No model improves.
- **The loss is in recall, not precision:** recall falls for all four (MARBERT 73.0 → 68.4, MARBERTv2 71.6 → 64.3, TF-IDF 62.3 → 53.4, AraBERT 75.1 → 73.8) while precision is flat or slightly higher. A likely explanation (untested): the all-18 texts teach the model that some sentences are valid everywhere, and many MLADI dev sentences are valid in several dialects (S01: sentences valid in all 8 exist), so without them the model predicts fewer dialects per sentence.
- Algeria and Tunisia fall the most (e.g. MARBERT Algeria 62.0 → 54.1, Tunisia 71.0 → 60.2; TF-IDF Algeria 46.9 → 28.0). Per-dialect values rest on few positives.
- **Confound:** D2 is 17% smaller than D1, so R05 changes data quantity as well as composition. A random 48,471-text sample of D1 would separate the two; not run.
- Validation F1 on D2 (≈70.7–74.2) is not comparable with R03's (≈80–83): the validation split no longer contains all-18 texts.
- Supports keeping D1 as it is (decisions.md D-006).

**R06 / R07: remove only one of the two groups (all four classifiers).**
- R06 drops only the 7,642 all-18 texts (D3, 50,742 texts, 45,668 train); R07 drops only the 2,271 zero-label texts (D4, 56,113 texts, 50,502 train). Configs `configs/card0to17_real_only*.json` and `configs/card1to18_real_only*.json`, seeds 42/43/44, otherwise identical to R03. Commit `c11a0b8` (committed before the run; matches the logs). 6.0–7.2 min per transformer run. Every transformer seed picked epoch 2.
- **Result: the all-18 texts are what matter; the zero-label texts do not.**

  | Model | R03 (all kept) | R07 (no zero-label) | R06 (no all-18) | R05 (neither) |
  |---|---|---|---|---|
  | MARBERT | 71.34 ± 1.03 | 72.17 ± 0.75 | 67.11 ± 1.13 | 69.25 ± 0.54 |
  | AraBERTv02-Twitter | 70.52 ± 0.52 | 70.74 ± 0.52 | 69.27 ± 0.60 | 69.82 ± 0.65 |
  | MARBERTv2 | 70.11 ± 0.55 | 69.79 ± 0.56 | 66.29 ± 1.21 | 64.89 ± 1.44 |
  | TF-IDF + LR | 62.58 ± 0.05 | 62.70 ± 1.00 | 56.27 ± 0.64 | 56.54 ± 0.82 |

- Removing the zero-label texts (R07) changes nothing: every model is within 0.9 points of R03, inside the noise level.
- Removing the all-18 texts (R06) costs about as much as removing both (R05): MARBERT −4.2, MARBERTv2 −3.8, TF-IDF −6.3, AraBERT −1.3 vs R03. As in R05, the loss is in recall (e.g. MARBERT 73.0 → 67.4, TF-IDF 62.3 → 51.8). This fits the R05 explanation (all-18 texts teach the model that a sentence can be valid everywhere), still untested.
- Size is a weaker explanation than composition here: R06 loses 13% of the data and drops as much as R05 (17%), while R07 loses 4% and does not drop. A size-matched random sample of D1 would settle it; not run.
- Decision unchanged: keep D1 with both groups (decisions.md D-006).

**G01: generator feasibility (all six chat generators).**
- **All six fit the 8 GB card in 4-bit** with ≥ 1.8 GB to spare; Gemma (6174 MiB) and Qwen3 (6066 MiB) are the tightest. The 9B-in-4-bit open question is answered: yes, for 20-sentence batches of 5 at 48 new tokens. Longer outputs or bigger batches are untested.
- Speeds are not all comparable: Falcon-H1 ran at batch 1 (see below), the rest at batch 5.
- Qualitative reading (Claude, 20 sentences each; to be replaced by DID-nadi fidelity and diversity scores):
  - **Jais-2:** clearest dialect markers (Iraqi ماكو/شلونك, Egyptian النهاردة, Syrian كتير). All 4 Moroccan outputs came out in Arabic Presentation Forms and were cut off mid-character; NFKC normalization would map them back, but that must be an explicit, logged cleaning step. Low variety within a dialect (يا سلام على هالخير والبركة 3×).
  - **Fanar:** clearly dialectal and the fastest, but appends an English translation in 16/20 outputs, often on the same line as the sentence. The cleaner in `src/generation/prompts.py` only drops translation lines that start a new line, so same-line `(Translation: …)` needs a fix before real generation. Topics repeat (Ramadan, Eid, good morning).
  - **Falcon-H1:** good markers incl. the only convincing Iraqi besides Jais, but 7/20 outputs contain Russian, Chinese or Hindi tokens (plus stray English/Spanish); a script filter would drop them.
  - **Gemma-2:** clean single sentences, no extra text; dialects drift (Moroccan and Iraqi requests come back Egyptian/Levantine).
  - **ALLaM:** 5/20 refusals (Morocco, Iraq, Syria), saying it only writes MSA or "widely understood" dialects; other outputs often MSA with formulaic religious/patriotic wording.
  - **Qwen3:** many semantically broken sentences, drift to Egyptian-like fillers (أنا بس, عايز), one degenerate repetition loop. `enable_thinking=False` worked (no `<think>` blocks).
- **Falcon-H1 batch 5 failed** (`RuntimeError: The expanded size of the tensor (49) must match the existing size (45)`, during generation after a successful load at 6158 MiB), probably batched left-padding in the hybrid Mamba model. Rerun at `--batch-size 1` succeeded; the failed result is kept as `feasibility_batch5_failed.json`.
- Provenance: Fanar at commit `6df4ec0`; the others at `5451ac6`, which adds `enable_thinking=False` to the chat template call (Fanar's rendered prompt was checked to be identical with and without it). The working tree also had an uncommitted docstring-only change in `scripts/check_generators.py` (another session); code unchanged.
- G01-gemma and G01-allam were run by another Claude session (folders `G02_…`, `G03_…`). Its first Fanar attempt collided with ours (both loaded at once; "paging file is too small") and failed; ours succeeded and is the recorded result.
- Download note: ALLaM's repo has 466 files (took about 1 h 4 min).

## Next runs

| ID | Model | What | Why |
|---|---|---|---|
| G02 | NLLB-200-1.3B and -distilled-1.3B | Back-translation check (`src/generation/backtranslate.py`) on a small D1 sample | The only downloaded models never run; does dialect survive the round trip? |

---

## Reference

### Data versions

| ID | File | SHA-256 (first 12) | Contents |
|---|---|---|---|
| D1 | `data/processed/nadi_lahjatbert.jsonl` | `d299edd78f3d` | 58,384 unique NADI 2020/2021/2023 texts, 18 LahjatBERT labels. Links → `URL`, mentions → `USER`, 365 quotes restored. No normalization. All-18 and zero-label texts kept. Built by `src/data/build_dataset.py`; details in `decisions.md`. |
| D2 | `data/processed/nadi_lahjatbert_card1to17.jsonl` | `47bedd182435` | D1 without the 2,271 zero-label and 7,642 all-18 texts: 48,471 texts with 1–17 valid dialects. Built by `src/data/filter_cardinality.py` (stats in `results/data_stats/nadi_lahjatbert_card1to17_stats.json`). |
| D3 | `data/processed/nadi_lahjatbert_card0to17.jsonl` | `128bd0bf6e0d` | D1 without the 7,642 all-18 texts (zero-label kept): 50,742 texts. `filter_cardinality --min-card 0 --max-card 17`. |
| D4 | `data/processed/nadi_lahjatbert_card1to18.jsonl` | `5e3e642f6fb9` | D1 without the 2,271 zero-label texts (all-18 kept): 56,113 texts. `filter_cardinality --min-card 1 --max-card 18`. |

### Quality measurements (`src/quality/measure.py`, results in `results/quality/`)

| ID | Date | Data | n | Exact / near dup | TTR | Distinct-2 | Self-BLEU | E5 cos. dist. | Vendi | DID-nadi top-1 agree | DID-madar top-1 agree | ALDi mean | File |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Q01 | 2026-10-06 | D1 random sample (seed 42) | 2000 | 0.05% / 0.10% | 0.514 | 0.948 | 0.063 | 0.163 | 3.77 | 61.5% (429 single-label texts) | 49.0% (406) | 0.603 | `real_d1_sample2000_seed42.json` |
| Q02 | 2026-10-07 | D1 matched to G01: 4 single-label tweets × 5 dialects (seed 42) | 20 | 0% / 0% | 0.885 | 1.000 | 0.028 | 0.172 | 2.48 | 60% | 35% | 0.714 | `Q02_real_d1_g01match.json` |
| Q02 | 2026-10-07 | G01-fanar | 20 | 0% / 0% | 0.838 | 0.984 | 0.028 | 0.126 | 2.02 | 55% | 45% | 0.534 | `Q02_g01_fanar.json` |
| Q02 | 2026-10-07 | G01-falcon_h1 | 20 | 0% / 0% | 0.853 | 1.000 | 0.023 | 0.131 | 2.07 | 55% | 40% | 0.649 | `Q02_g01_falcon_h1.json` |
| Q02 | 2026-10-07 | G01-jais2 | 20 | 0% / 0% | 0.662 | 0.784 | 0.253 | 0.129 | 1.99 | 50% | 50% | 0.669 | `Q02_g01_jais2.json` |
| Q02 | 2026-10-07 | G01-allam | 20 | 0% / 0% | 0.710 | 0.902 | 0.075 | 0.140 | 2.11 | 50% | 25% | 0.234 | `Q02_g01_allam.json` |
| Q02 | 2026-10-07 | G01-gemma | 20 | 0% / 0% | 0.862 | 0.978 | 0.059 | 0.129 | 2.03 | 40% | 15% | 0.682 | `Q02_g01_gemma.json` |
| Q02 | 2026-10-07 | G01-qwen3 | 20 | 0% / 0% | 0.646 | 0.806 | 0.038 | 0.130 | 2.06 | 15% | 15% | 0.621 | `Q02_g01_qwen3.json` |

**Q01 notes.** Reference values for comparing synthetic sets (measure them at the same `--sample 2000`). The DID scorers agree with the LahjatBERT single label on only 62% / 49% of real tweets (kappa 0.55 / 0.38; the two scorers agree with each other with kappa 0.26), so a top-1 DID fidelity filter would also reject about 40% of real data: fidelity thresholds must be set relative to these numbers, not to 100%. Per-dialect DID-nadi agreement is 0% for Bahrain, Jordan and Palestine (small n) and 82% for Egypt.

**Q02 notes.** Commit `68d1e50`. The 20 G01 sentences per generator, cleaned by the pipeline's own parser (`scripts/g01_to_records.py` → `data/synthetic/g01_<model>.jsonl`; the parser kept all 120), scored with `src/quality/measure.py` (default config). The reference is a size-matched real set with the same dialect counts (`data/processed/d1_g01match_seed42.jsonl`), because TTR, Self-BLEU and Vendi depend on set size; do not compare Q02 rows with Q01.
- **Very small samples.** With n = 20, one sentence moves top-1 agreement by 5 points; a 95% interval is roughly ±20 points. Only differences of about 25+ points mean anything here; per-dialect values (n = 4) are anecdotes.
- **Dialect fidelity (DID-nadi top-1 vs the requested dialect):** real 60%; Fanar 55%, Falcon-H1 55%, Jais-2 50%, ALLaM 50%, Gemma 40%, **Qwen3 15%**. Only Qwen3 is clearly below real data. The top four are indistinguishable at this n.
- **Dialectness (ALDi mean):** real 0.71; Gemma 0.68, Jais-2 0.67, Falcon-H1 0.65, Qwen3 0.62, Fanar 0.53, **ALLaM 0.23**. ALLaM writes mostly MSA, confirming the G01 reading. Fanar's 0.53 is partly the appended English translations, which the parser keeps when they are on the same line.
- **Diversity: every generator is less diverse than real tweets.** E5 mean pairwise distance 0.126–0.140 vs 0.172 for real, Vendi 1.99–2.11 vs 2.48. This holds for all six, so it is the most consistent finding, but it is still 20 texts each.
- **Jais-2 repeats itself:** Self-BLEU 0.253 vs 0.028 real, distinct-2 0.78 vs 1.00 (e.g. the same Saudi sentence three times). **Gemma writes very short texts:** 5.5 words on average vs 11.3 real.
- Leftovers the parser does not remove are scored as text: Fanar's same-line translations (16/20), ALLaM's 5 Arabic refusals, Jais-2's 4 presentation-form Moroccan fragments. Scores after fixing the parser could differ.
- Duplicates: no exact or near duplicates within any set or against D1. The real reference shows 20/20 "near duplicates of D1" only because it is drawn from D1 (the self-comparison is skipped only when the file path is D1 itself).
- **Next:** a bigger G-run (e.g. 200 sentences per generator over all 18 dialects, after fixing the translation cleanup) is needed before choosing generators; at n = 20 the ranking is only suggestive.

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

Final model set (decided 2026-10-08): classifiers MARBERTv2, AraBERTv02-Twitter, Qwen3-8B, Jais-2-8B, Falcon-H1-7B, Aya-Expanse-8B; Fanar-1-9B kept. **No longer used** (files kept on disk, scores above kept as they are): MARBERT v1, TF-IDF + LR, Gemma-2, ALLaM, NLLB (never run), CAMeLBERT DID scorers as classifiers. Open: the leaderboard Space runs on `cpu-basic` (no GPU, ~16 GB RAM) and loads `AutoModelForSequenceClassification` without `trust_remote_code`; transformers has no sequence-classification class for Jais-2, Falcon-H1 or Aya (Cohere), and 7–9B models do not fit its memory, so the trained large models cannot be scored there as it stands (ask the organizer).

Checked on the Hub on 2026-10-06. About 6.7 GB of the 8 GB of VRAM is free.

| Role | Hub ID | Size | Fits 8 GB? | Notes |
|---|---|---|---|---|
| Generator | `QCRI/Fanar-1-9B-Instruct` | 8.8B | 4-bit only | Tight fit |
| Generator | `google/gemma-2-9b-it` | 9.2B | 4-bit only | Gated: accept the license and use an access token |
| Generator | `humain-ai/ALLaM-7B-Instruct-preview` | 7.0B | 4-bit | |
| Generator | `facebook/nllb-200-1.3B` | 1.3B | yes | Translation / back-translation. Downloaded, not run yet |
| Generator | `facebook/nllb-200-distilled-1.3B` | 1.3B | yes | Same. Downloaded, not run yet |
| Generator | `Qwen/Qwen3-8B` | 8.2B | 4-bit (G01: 6066 MiB) | Added 2026-10-06; thinking mode disabled in `src/generation/llm.py` |
| Generator | `tiiuae/Falcon-H1-7B-Instruct` | 7.6B | 4-bit (G01: 5184 MiB) | Added 2026-10-06; Arabic among its languages (Falcon3 has none); hybrid Mamba, batch 1 only |
| Generator | `inception42/Jais-2-8B-Chat` | 8.1B | 4-bit (G01: 5750 MiB) | Added 2026-10-06; gated (license accepted on the Hub) |
| Generator | GPT-4o-mini (optional) | — | remote | Paid: conflicts with the zero-cost rule |
| Scorer (fidelity) | `CAMeL-Lab/bert-base-arabic-camelbert-mix-did-nadi` or `-did-madar-corpus26` | ~110M | yes | Variant not decided |
| Scorer (dialectness) | `VARabi/Sentence-ALDi` | ~110M | yes | |
| Scorer (diversity) | `intfloat/multilingual-e5-large` | 560M | yes | |
| Classifier | `UBC-NLP/MARBERTv2` | ~163M | yes | Main classifier (compared in R03: R03-marbert is v1, R03-marbertv2 is v2) |
| Classifier | `aubmindlab/bert-base-arabertv02-twitter` | 135M | yes | |
| Classifier | TF-IDF + logistic regression | — | CPU | |
