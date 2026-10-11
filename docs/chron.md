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

## R02 – Does training work end to end?

Smoke test, 500 examples. The model predicted every dialect as valid (R 100, F1 53.2). Not a result; folder deleted.

## R03 – Real only (condition 1) on D1, our training settings

Dropout 0.3, 2 epochs, epoch chosen by macro F1.

| Model | Dev F1 | P | R | micro F1 | Test |
|---|---|---|---|---|---|
| MARBERT | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 | 68.65 (T04) |
| AraBERTv02-Twitter | 70.52 ± 0.52 | 69.15 ± 1.34 | 75.12 ± 0.30 | 71.99 ± 0.66 | 67.31 (T02) |
| MARBERTv2 | 70.11 ± 0.55 | 70.94 ± 1.15 | 71.62 ± 0.90 | 69.81 ± 0.32 | 67.71 (T01) |
| TF-IDF + LR | 62.58 ± 0.05 | 65.83 ± 1.27 | 62.28 ± 0.54 | 63.91 ± 0.07 | — |

**Takeaway:** the three transformers are within about 1 point (noise) and level with LahjatBERT's best model. TF-IDF is about 8 points behind. Algeria is the weakest dialect for every model.

## R04 – Why does R03 beat LahjatBERT's baseline?

MARBERT with LahjatBERT's own settings: dropout 0.1, 3 epochs, micro-F1 selection.

| Model | Dev F1 | P | R | micro F1 |
|---|---|---|---|---|
| MARBERT | 68.71 ± 0.35 | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.12 ± 0.35 |

**Takeaway:** with their settings we land where they did (67.41), so the R03 gain comes from the training settings, not the data, and shows up as higher recall.

## R05 / R06 / R07 – Does removing zero-label or all-18 texts from D1 help?

Dev F1. R03 is repeated as the reference.

| Run | Data | MARBERT | MARBERTv2 | AraBERT | TF-IDF |
|---|---|---|---|---|---|
| R03 | D1 (everything) | 71.34 ± 1.03 | 70.11 ± 0.55 | 70.52 ± 0.52 | 62.58 ± 0.05 |
| R05 | D2: both groups removed | 69.25 ± 0.54 | 64.89 ± 1.44 | 69.82 ± 0.65 | 56.54 ± 0.82 |
| R06 | D3: all-18 removed | 67.11 ± 1.13 | 66.29 ± 1.21 | 69.27 ± 0.60 | 56.27 ± 0.64 |
| R07 | D4: zero-label removed | 72.17 ± 0.75 | 69.79 ± 0.56 | 70.74 ± 0.52 | 62.70 ± 1.00 |

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
