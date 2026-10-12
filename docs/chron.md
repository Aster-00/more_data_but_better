# Runs in order

One block per run: the question it answers, its scores, the takeaway. Numbers are copied from `docs/tables/split_summary.md` (generated; state of 2026-10-11). Dev = MLADI dev, 120 sentences, 8 dialects, threshold 0.3; mean ± std over 3 seeds unless noted. Test = MLADI leaderboard, one seed per submission.

## R00 – Does our scoring code match the official scorer?

On the organizers' sample submission our code gives macro F1 42.47, P 38.14, R 50.33, identical to the official README.

**Takeaway:** our dev scores are comparable with official ones.

## R01 – How well do the published LahjatBERT models score on dev?

Downloaded and scored, not trained by us. One published checkpoint each, so no std.

| Model | Dev F1 | P | R | micro F1 |
|---|---|---|---|---|
| cl_cardinality | 72.68 | 68.98 | 80.64 | 73.07 |
| cl_aldi | 70.27 | 71.35 | 71.32 | 70.93 |
| baseline | 67.41 | 73.66 | 63.66 | 67.86 |

**Takeaway:** the reference to beat.  

`cl` is curicculum learning where the model sees easy training examples first then hard trainning examples later. the difference between `cl_cardinality` and `cl_aldi` is how do we define whats hard and whats easy.

`cl_cardinality` orders the training data by cardinality: how many dialects a sentence is labelled

`cl_aldi` orders the data by ALDi (Arabic Level of Dialectness, Keleg et al. 2023)

## R02 – Does removing diacritics from the training text change anything?

R07 setup (D4, our R03 settings) with `strip_diacritics: true` (`configs/card1to18_nodiac_real_only*.json`). MARBERTv2 seed 44 was stopped before it finished (no score), so MARBERTv2 has 2 seeds. Diacritics are stripped from training text only; dev text is scored as it is.

| Model | Seeds | R07 dev F1 (D4) | R02 dev F1 (D4, no diacritics) | P | R | micro F1 | Validation F1 | Dev F1 per seed (42 / 43 / 44) |
|---|---|---|---|---|---|---|---|---|
| MARBERT | 3 | 72.17 ± 0.75 | 71.39 ± 1.52 | 71.14 ± 2.87 | 73.30 ± 0.77 | 71.12 ± 1.38 | 82.48 ± 0.08 | 73.15 / 70.55 / 70.48 |
| AraBERTv02-Twitter | 3 | 70.74 ± 0.52 | 70.84 ± 0.10 | 69.84 ± 0.73 | 74.87 ± 0.45 | 71.92 ± 0.13 | 80.14 ± 0.07 | 70.73 / 70.93 / 70.86 |
| MARBERTv2 | 2 | 69.79 ± 0.56 | 69.70 ± 0.35 | 70.45 ± 1.32 | 71.29 ± 1.81 | 69.78 ± 0.33 | 81.72 ± 0.24 | 69.46 / 69.95 / — |

**Takeaway:** removing diacritics makes no measurable difference for any of the three models (all changes within seed spread).

## R03 – Real only (condition 1) on D1, our training settings

Dropout 0.3, 2 epochs, epoch chosen by macro F1.

| Model | Dev F1 | P | R | micro F1 | Test |
|---|---|---|---|---|---|
| MARBERT | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 | 68.65 (T04) |
| AraBERTv02-Twitter | 70.52 ± 0.52 | 69.15 ± 1.34 | 75.12 ± 0.30 | 71.99 ± 0.66 | 67.31 (T02) |
| MARBERTv2 | 70.11 ± 0.55 | 70.94 ± 1.15 | 71.62 ± 0.90 | 69.81 ± 0.32 | 67.71 (T01) |

**Takeaway:** the three transformers are within about 1 point (noise) and level with LahjatBERT's best model. 
## R04 – Why does R03 beat LahjatBERT's baseline?

MARBERT with LahjatBERT's own settings: dropout 0.1, 3 epochs, micro-F1 selection.

| Run | Model | Dev F1 | P | R | micro F1 | Validation F1 (automatic labels) |
|---|---|---|---|---|---|---|
| R04 | MARBERT, LahjatBERT's settings, trained by us | 68.71 ± 0.35 | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.12 ± 0.35 | 82.85 ± 0.06 |
| R01 | LahjatBERT baseline, published checkpoint| 67.41 | 73.66 | 63.66 | 67.86 | — |
| R03 | MARBERT, our settings (for comparison) | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 | 81.44 ± 0.14 |

Settings that differ. R03: `configs/baseline_real_only.json`; R04: `configs/repro_lahjatbert_baseline.json`; R01 baseline: `LahjatBERT_-main/baseline.py`. Everything else is the same in all three (MARBERT, lr 5e-5, batch 24, warmup 500, weight decay 0.01, first 8 of 12 layers frozen, max length 128, fp16, threshold 0.3, 90/10 split).

| Setting | R03 (ours) | R04 (LahjatBERT's settings, our code) | R01 baseline (published, their code) |
|---|---|---|---|
| Dropout | 0.3 | 0.1 | 0.1 (code sets 0.3 after the model is built, so it never applies) |
| Epochs | 2 | 3 | 3 |
| Epoch chosen by | macro F1 on validation | micro F1 on validation | micro F1 (`eval_f1`) |
| Training data | D1 (deduplicated, unnormalized) | D1 | their `stage_1_and_gpt.csv`, no normalization |
| Split seed | run seed | run seed | fixed `random_state=42` |
| Seeds | 3 (42/43/44) | 3 | 1 checkpoint |

Micro-F1 selection changed nothing (every R04 seed picked epoch 3), so the gap comes from dropout and/or the third epoch; R04 cannot separate the two.

**Takeaways:** 

- R03 finds about 7.5 points more of the dialects that humans marked valid, and gives up about 3 points of precision. Algeria improves the most (62.0 vs 54.8). 

- R04 fits the training labels more closely. Less dropout (0.1 vs 0.3) and an extra epoch (2 vs 3)let it learn them more tightly. STATEMENT TO BE VERIFIED
  - Confirmed by R12–R15 below. Evidence from the train logs: R04's training loss ends at 0.123 (epoch 3) vs 0.283 for R03 (epoch 2); after its own epoch 2 R04 is already at 0.196, so lower dropout alone lowers the training loss. Validation F1 (automatic labels) is higher for R04 (82.85 vs 81.44) while dev is lower.
  
*Further investigation:** 
- Run R3 (our settings) again with `cl_cardinality` as R10 and `cl_adli` as R11.
- Run Different settings for the R3 vs R4 to find what exactly caused this difference
  - R12 Dropout = 0.3, Epochs = 2
  - R13 Dropout = 0.1, Epochs = 2
  - R14 Dropout = 0.3, Epochs = 3
  - R15 Dropout = 0.1, Epochs =3
  - Maybe try 4 Epochs and 0.5, 0.2 dropouts  
- Run the best combination of these 2 Expirements R16

## R05 / R06 / R07 – Does removing zero-label or all-18 texts from D1 help?

Dev F1. R03 is repeated as the reference.

| Run | Data | MARBERT | MARBERTv2 | AraBERT | TF-IDF |
|---|---|---|---|---|---|
| R03 | D1 (everything) | 71.34 ± 1.03 | 70.11 ± 0.55 | 70.52 ± 0.52 | 62.58 ± 0.05 |
| R05 | D2: both groups removed | 69.25 ± 0.54 | 64.89 ± 1.44 | 69.82 ± 0.65 | 56.54 ± 0.82 |
| R06 | D3: all-18 removed | 67.11 ± 1.13 | 66.29 ± 1.21 | 69.27 ± 0.60 | 56.27 ± 0.64 |
| R07 | D4: zero-label removed | 72.17 ± 0.75 | 69.79 ± 0.56 | 70.74 ± 0.52 | 62.70 ± 1.00 |

Dev precision (macro).

| Run | Data | MARBERT | MARBERTv2 | AraBERT | TF-IDF |
|---|---|---|---|---|---|
| R03 | D1 (everything) | 71.67 ± 2.54 | 70.94 ± 1.15 | 69.15 ± 1.34 | 65.83 ± 1.27 |
| R05 | D2: both groups removed | 72.53 ± 0.56 | 69.07 ± 0.51 | 69.60 ± 0.61 | 65.95 ± 0.44 |
| R06 | D3: all-18 removed | 69.68 ± 1.46 | 69.29 ± 1.01 | 68.82 ± 0.58 | 68.02 ± 0.94 |
| R07 | D4: zero-label removed | 72.02 ± 2.11 | 70.38 ± 1.08 | 69.35 ± 0.45 | 64.13 ± 1.09 |

Dev recall (macro).

| Run | Data | MARBERT | MARBERTv2 | AraBERT | TF-IDF |
|---|---|---|---|---|---|
| R03 | D1 (everything) | 72.98 ± 0.40 | 71.62 ± 0.90 | 75.12 ± 0.30 | 62.28 ± 0.54 |
| R05 | D2: both groups removed | 68.40 ± 1.39 | 64.27 ± 2.45 | 73.80 ± 1.54 | 53.43 ± 0.63 |
| R06 | D3: all-18 removed | 67.36 ± 0.87 | 66.60 ± 1.49 | 73.13 ± 0.72 | 51.77 ± 1.00 |
| R07 | D4: zero-label removed | 74.05 ± 0.74 | 71.52 ± 0.83 | 75.34 ± 0.98 | 63.49 ± 0.95 |

**Takeaway:** the all-18 texts matter (removing them costs recall); the zero-label texts do not. D1 vs D4 as the default is still open. Caveat: data size also changes, and no size-matched control has been run.

## R08 – Can 7–9B decoder LLMs beat BERT-sized classifiers?

4-bit QLoRA on D1. **One seed only.** Falcon-H1 skipped (~30 h per run).

| Model | Dev F1 | P | R | micro F1 |
|---|---|---|---|---|
| Jais-2-8B | 69.31 | 76.08 | 65.53 | 69.14 |
| Aya-Expanse-8B | 69.11 | 75.50 | 66.07 | 69.11 |
| Fanar-1-9B | 67.30 | 74.06 | 63.56 | 67.96 |
| Qwen3-8B | 65.15 | 73.48 | 61.20 | 65.28 |

**Takeaway:** none beats the BERT models. Highest precision, low recall, 5–11 h per run (vs ~7 min for BERT), and not scorable on the leaderboard as it stands.


## R10 / R11 – Does LahjatBERT's curriculum learning help on our settings?

R03 settings (dropout 0.3, macro selection), LahjatBERT's stages (orders from their `run_workflow.sh`), 1 epoch per stage. Validation F1 has no single value (each stage has its own split).

| Run | Model | Dev F1 | P | R | micro F1 |
|---|---|---|---|---|---|
| R10 | cl_cardinality, our settings | 71.79 ± 1.63 | 67.73 ± 2.15 | 80.03 ± 1.73 | 72.02 ± 1.70 |
| R11 | cl_aldi, our settings | 70.87 ± 0.70 | 69.98 ± 0.57 | 73.35 ± 0.97 | 71.02 ± 1.01 |
| R12 | no curriculum, our settings | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 |
| R01 | LahjatBERT cl_cardinality, published | 72.68 | 68.98 | 80.64 | 73.07 |
| R01 | LahjatBERT baseline, published | 67.41 | 73.66 | 63.66 | 67.86 |

**Takeaways:**

- **No gain beyond noise.** Both curricula are within 0.5 points of R12.
- LahjatBERT's cl_cardinality beat their own baseline by 5.3 points, but that baseline had the dropout bug. Against a baseline trained with dropout 0.3, almost all of the gain is gone. Our R10 lands where their cl_cardinality does (71.79 vs 72.68), with the same profile.
- R10 changes the error profile: about 7 points more recall, 4 points less precision (it names more dialects per sentence). The leaderboard models already name too many dialects on test (T01–T05), so whether this helps on test is untested.

**R16 not run:** R10 already is "best grid setting + better curriculum". A curriculum trains one epoch per stage, so the epochs dimension does not carry over. Options in `progress.md` → Next runs.
  
***future runs:*** 

- verify the satement made by the baseline by repeating the runs with LahjaBERT as R9
## R12–R24 – Which R04 change costs the dev points: dropout or epochs?

MARBERT, D1, 3 seeds, R03 settings except dropout and epochs. Val = macro F1 on the 10% validation split of D1 (automatic labels, never trained on); Dev = macro F1 on the 120 human-labelled MLADI dev sentences. Mean ± std over the 3 seeds. **R12** = R03's setup, **R15** = R04's.

| Dropout \ Epochs | 2 | 3 | 4 |
|---|---|---|---|
| 0.1 | R13: Val (82.75 ± 0.11), Dev (70.42 ± 0.55) | **R15**: Val (82.85 ± 0.06), Dev (68.71 ± 0.35) | R21: Val (82.83 ± 0.13), Dev (68.19 ± 0.42) |
| 0.2 | R17: Val (82.18 ± 0.17), Dev (71.21 ± 0.52) | R19: Val (82.46 ± 0.16), Dev (71.01 ± 1.80) | R22: Val (82.48 ± 0.06), Dev (69.76 ± 1.40) |
| 0.3 | **R12**: Val (81.44 ± 0.14), Dev (71.34 ± 1.03) | R14: Val (81.83 ± 0.06), Dev (70.98 ± 1.60) | R23: Val (81.99 ± 0.18), Dev (69.56 ± 2.10) |
| 0.5 | R18: Val (73.51 ± 1.06), Dev (58.34 ± 1.00) | R20: Val (74.74 ± 0.64), Dev (58.79 ± 0.81) | R24: Val (74.56 ± 0.23), Dev (57.03 ± 1.01) |

All runs, with dev precision, recall and micro F1:

| Run | Dropout | Epochs | Val F1 | Dev F1 | P | R | micro F1 |
|---|---|---|---|---|---|---|---|
| R12 | 0.3 | 2 | 81.44 ± 0.14 | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 |
| R13 | 0.1 | 2 | 82.75 ± 0.11 | 70.42 ± 0.55 | 74.22 ± 1.44 | 68.85 ± 0.90 | 70.62 ± 0.51 |
| R14 | 0.3 | 3 | 81.83 ± 0.06 | 70.98 ± 1.60 | 72.06 ± 1.02 | 71.67 ± 2.34 | 70.89 ± 1.07 |
| R15 | 0.1 | 3 | 82.85 ± 0.06 | 68.71 ± 0.35 | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.12 ± 0.35 |
| R17 | 0.2 | 2 | 82.18 ± 0.17 | 71.21 ± 0.52 | 73.06 ± 2.14 | 71.60 ± 0.67 | 71.13 ± 0.58 |
| R18 | 0.5 | 2 | 73.51 ± 1.06 | 58.34 ± 1.00 | 64.83 ± 2.74 | 55.95 ± 2.91 | 58.66 ± 1.08 |
| R19 | 0.2 | 3 | 82.46 ± 0.16 | 71.01 ± 1.80 | 74.17 ± 1.31 | 69.87 ± 2.27 | 70.93 ± 1.17 |
| R20 | 0.5 | 3 | 74.74 ± 0.64 | 58.79 ± 0.81 | 67.07 ± 1.00 | 55.13 ± 0.60 | 58.98 ± 1.12 |
| R21 | 0.1 | 4 | 82.83 ± 0.13 | 68.19 ± 0.42 | 76.08 ± 1.20 | 63.94 ± 0.25 | 68.70 ± 0.35 |
| R22 | 0.2 | 4 | 82.48 ± 0.06 | 69.76 ± 1.40 | 73.91 ± 1.21 | 68.09 ± 1.48 | 69.82 ± 0.83 |
| R23 | 0.3 | 4 | 81.99 ± 0.18 | 69.56 ± 2.10 | 72.12 ± 1.84 | 69.11 ± 2.71 | 69.51 ± 1.64 |
| R24 | 0.5 | 4 | 74.56 ± 0.23 | 57.03 ± 1.01 | 68.42 ± 2.11 | 52.30 ± 0.48 | 57.34 ± 0.97 |

**Takeaways:**

- R12 and R15 reproduce R03 and R04 seed for seed, so training is deterministic and every difference here comes from the settings.
- **Neither change alone matters; together they cost 2.6 points.** Dropout 0.3 → 0.1 alone: −0.9 (R12 → R13). 2 → 3 epochs alone: −0.4 (R12 → R14). Both: −2.6 (R15). Lower dropout hurts more the longer the model trains.
- Dropout 0.5 is too much: the model underfits (dev ~58, validation ~74).
- The best cell is the setting we already had (R12). Dropout 0.2 / 2 epochs (R17) is level with it. More epochs never helped dev.
- **The statement under R04 is confirmed:** lower dropout and more epochs both lower the training loss (0.28 for R12 → 0.12 for R15) and raise validation F1 on the automatic labels (81.44 → 82.85), while dev F1 drops through recall. The two runs with the highest validation F1 (R15, R21) have the lowest dev F1. So validation F1 on geolocation labels cannot pick these settings; the human dev set has to. Why tighter fitting costs recall is a hypothesis (the model names fewer dialects per sentence), not tested yet.

Caveat: "epochs" is the planned length of the learning-rate schedule, so epoch 2 of a 3-epoch run is not the same as a 2-epoch run.


***future runs:***

- If it proves that R9 produces the same results as the published baselines then we will run these tests again with all the other models not just MARBERT, because this proves that different models respond differently to different hyperparameters. **LOW PRIORITY**

- 
## T01–T05 – Leaderboard test submissions

| Test | Model | Test F1 | P | R |
|---|---|---|---|---|
| T04 | R03-MARBERT (D1) | 68.65 | 64.60 | 76.39 |
| T03 | R07-MARBERT (D4) | 68.61 | 63.75 | 77.36 |
| T01 | R03-MARBERTv2 (D1) | 67.71 | 63.58 | 75.36 |
| T05 | R07-AraBERT (D4) | 67.48 | 61.57 | 78.58 |
| T02 | R03-AraBERT (D1) | 67.31 | 61.86 | 77.65 |

**Takeaway:** no test difference between D1 and D4. All models mark too many dialects per sentence (precision drops from dev to test).

## Non-R runs

- **G01** – Do the generators fit in 8 GB? All six fit in 4-bit; output quality varies (see `progress.md`).
- **Q01 / Q02** – Reference quality values on real data, and the quality of the G01 outputs.
- **S01** – Dialect scorers checked against human labels. The scorers have since been dropped.
