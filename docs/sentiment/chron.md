## SR01 baseline run, real data only

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_pn | f1_pn_std | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SR01-jais2 | dev | `sr01_jais2` | 3 | 80.47 | 80.66 | 80.46 | 0.72 | 81.27 | 79.87 | 0.84 | 82.73 | 81.67 | 77.01 |
| SR01-jais2 | test | `sr01_jais2` | 3 | 67.02 | 67.22 | 67.94 | 0.95 | 71.74 | 74.74 | 1.59 | 80.81 | 51.59 | 68.66 |
| SR01-fanar | dev | `sr01_fanar` | 1 | 79.42 | 79.46 | 79.41 | – | 80.10 | 78.70 | – | 80.80 | 80.87 | 76.61 |
| SR01-fanar | test | `sr01_fanar` | 1 | 66.63 | 66.25 | 67.71 | – | 70.83 | 74.13 | – | 79.56 | 51.63 | 68.71 |
| SR01-aya | dev | `sr01_aya` | 3 | 79.36 | 80.20 | 78.84 | 1.06 | 80.20 | 78.57 | 1.09 | 81.22 | 80.94 | 75.92 |
| SR01-aya | test | `sr01_aya` | 3 | 65.72 | 65.67 | 67.05 | 0.60 | 69.86 | 73.03 | 1.06 | 78.58 | 51.09 | 67.49 |
| SR01-marbert | dev | `sr01_marbert` | 3 | 78.68 | 78.79 | 78.79 | 1.14 | 79.64 | 77.97 | 0.66 | 81.42 | 80.10 | 74.53 |
| SR01-marbert | test | `sr01_marbert` | 3 | 65.14 | 65.05 | 66.50 | 0.15 | 69.96 | 73.54 | 0.48 | 79.46 | 48.35 | 67.61 |
| SR01-marbertv2 | dev | `sr01_marbertv2` | 3 | 78.42 | 78.35 | 78.67 | 0.52 | 79.61 | 77.37 | 0.58 | 81.46 | 80.53 | 73.28 |
| SR01-marbertv2 | test | `sr01_marbertv2` | 3 | 63.95 | 63.81 | 66.06 | 0.41 | 68.78 | 72.18 | 1.58 | 78.50 | 47.50 | 65.86 |
| SR01-falcon_h1 | dev | `sr01_falcon_h1` | 1 | 77.93 | 77.72 | 78.16 | – | 79.21 | 76.59 | – | 80.79 | 80.60 | 72.40 |
| SR01-falcon_h1 | test | `sr01_falcon_h1` | 1 | 63.31 | 63.20 | 65.77 | – | 67.80 | 70.90 | – | 76.97 | 48.13 | 64.84 |
| SR01-qwen3 | dev | `sr01_qwen3` | 1 | 77.82 | 78.32 | 77.46 | – | 79.29 | 76.27 | – | 80.59 | 80.92 | 71.94 |
| SR01-qwen3 | test | `sr01_qwen3` | 1 | 63.92 | 63.80 | 65.02 | – | 68.60 | 70.99 | – | 77.89 | 49.78 | 64.10 |
| SR01-arabertv02_twitter | dev | `sr01_arabertv02_twitter` | 3 | 77.31 | 77.24 | 77.42 | 0.17 | 78.49 | 76.05 | 0.34 | 79.79 | 79.81 | 72.32 |
| SR01-arabertv02_twitter | test | `sr01_arabertv02_twitter` | 3 | 63.78 | 63.69 | 65.76 | 0.48 | 68.51 | 71.58 | 0.20 | 77.91 | 48.18 | 65.25 |

## SG01 0 shot Prompt Generation

Each cell: requested → kept after filter → selected (target 500 per cell).

**Jais-2-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 1,300 → 38 → 38 | 1,300 → 8 → 8 | 1,300 → 186 → 186 | 232 |
| egypt | 1,300 → 247 → 247 | 1,300 → 122 → 122 | 1,300 → 514 → 500 | 869 |
| gulf | 1,300 → 482 → 482 | 1,300 → 252 → 252 | 1,300 → 361 → 361 | 1,095 |
| levant | 1,300 → 469 → 469 | 1,300 → 237 → 237 | 1,300 → 516 → 500 | 1,206 |
| **Total** | 5,200 → 1,236 → 1,236 | 5,200 → 619 → 619 | 5,200 → 1,577 → 1,547 | 3,402 |

**Fanar-1-9B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 646 → 500 | 650 → 644 → 500 | 650 → 649 → 500 | 1,500 |
| egypt | 650 → 646 → 500 | 650 → 647 → 500 | 650 → 648 → 500 | 1,500 |
| gulf | 650 → 646 → 500 | 650 → 647 → 500 | 650 → 649 → 500 | 1,500 |
| levant | 650 → 645 → 500 | 650 → 647 → 500 | 650 → 646 → 500 | 1,500 |
| **Total** | 2,600 → 2,583 → 2,000 | 2,600 → 2,585 → 2,000 | 2,600 → 2,592 → 2,000 | 6,000 |

**Qwen3-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 648 → 500 | 650 → 645 → 500 | 650 → 648 → 500 | 1,500 |
| egypt | 650 → 643 → 500 | 650 → 650 → 500 | 650 → 635 → 500 | 1,500 |
| gulf | 650 → 648 → 500 | 650 → 650 → 500 | 650 → 646 → 500 | 1,500 |
| levant | 650 → 648 → 500 | 650 → 649 → 500 | 650 → 642 → 500 | 1,500 |
| **Total** | 2,600 → 2,587 → 2,000 | 2,600 → 2,594 → 2,000 | 2,600 → 2,571 → 2,000 | 6,000 |

**Aya-Expanse-8B**

| Variety | NEG | NEU | POS | Total selected |
|---|---|---|---|---|
| msa | 650 → 559 → 500 | 650 → 613 → 500 | 650 → 572 → 500 | 1,500 |
| egypt | 650 → 640 → 500 | 650 → 644 → 500 | 650 → 641 → 500 | 1,500 |
| gulf | 650 → 647 → 500 | 650 → 628 → 500 | 650 → 624 → 500 | 1,500 |
| levant | 650 → 641 → 500 | 650 → 648 → 500 | 650 → 642 → 500 | 1,500 |
| **Total** | 2,600 → 2,487 → 2,000 | 2,600 → 2,533 → 2,000 | 2,600 → 2,479 → 2,000 | 6,000 |

SG01 Jais-2, Fanar, Qwen3, Aya.

| Generator | Requested | Distinct texts | Kept after filter | Exact dup. | Near dup. | Script | Length | Unparsed | Selected | Short cells | Test matches | Translations cut | Texts/s | Mean words (selected) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jais-2-8B | 15,600 | 4,398 (28.2%) | 3,432 (22.0%) | 11,168 | 950 | 14 | 1 | 35 | 3,402 | 10 of 12 | 0 | 264 | 4.07 | 12.4 |
| Fanar-1-9B | 7,800 | 7,794 (99.9%) | 7,760 (99.5%) | 6 | 1 | 26 | 7 | 0 | 6,000 | 0 of 12 | 0 | 116 | 1.28 | 13.8 |
| Qwen3-8B | 7,800 | 7,772 (99.6%) | 7,752 (99.4%) | 28 | 5 | 6 | 9 | 0 | 6,000 | 0 of 12 | 0 | 2 | 1.93 | 13.9 |
| Aya-Expanse-8B | 7,800 | 7,714 (98.9%) | 7,499 (96.1%) | 86 | 213 | 1 | 1 | 0 | 6,000 | 0 of 12 | 0 | 4 | 2.20 | 17.4 |

Column explanation
- Script: Rejected because under 70% of the letters are Arabic script, e.g. mostly English, or Chinese characters mixed in
- Length: Rejected because the tweet has fewer than 2 or more than 60 words
- Unparsed: The output held no usable tweet: the parser found no Arabic line, only an explanation or English

**Takeaway:**
- Jais-2 repeats itself almost word for word.
- TODO: check what each model generations looked like, what they got wrong, any drifts and any mislabeling

**Future runs:**
- 

## Sr02 
which is a run that uses SG01, which is a run that uses 0 shot prompting and generates 500 for every sentiment in every dialect.

| id | split | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_pn | f1_pn_std | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SR02-marbertv2_fanar | dev | 3 | 79.27 | 78.96 | 79.81 | 1.30 | 80.36 | 78.48 | 0.66 | 82.63 | 80.85 | 74.34 |
| SR02-marbertv2_fanar | test | 3 | 64.45 | 63.89 | 66.52 | 0.15 | 68.84 | 72.37 | 0.37 | 78.45 | 48.62 | 66.28 |
| SR02-marbertv2_qwen3 | dev | 3 | 78.28 | 77.71 | 79.06 | 0.65 | 79.35 | 77.39 | 0.68 | 81.35 | 80.08 | 73.42 |
| SR02-marbertv2_qwen3 | test | 3 | 64.08 | 63.44 | 66.31 | 0.57 | 68.38 | 71.80 | 0.45 | 77.87 | 48.63 | 65.73 |
| SR02-marbertv2_aya | dev | 3 | 78.99 | 78.64 | 79.42 | 0.48 | 80.18 | 77.90 | 0.23 | 82.05 | 81.17 | 73.76 |
| SR02-marbertv2_aya | test | 3 | 64.09 | 63.29 | 66.10 | 0.15 | 68.28 | 71.96 | 0.33 | 77.81 | 48.36 | 66.11 |
| SR02-marbert_fanar | dev | 3 | 78.35 | 78.64 | 78.24 | 1.19 | 79.43 | 77.35 | 0.80 | 80.80 | 80.37 | 73.90 |
| SR02-marbert_fanar | test | 3 | 65.62 | 65.69 | 66.81 | 0.72 | 70.36 | 73.94 | 0.20 | 79.48 | 48.98 | 68.40 |
| SR02-marbert_qwen3 | dev | 3 | 78.20 | 77.86 | 78.76 | 0.73 | 79.00 | 77.47 | 0.83 | 80.25 | 79.66 | 74.70 |
| SR02-marbert_qwen3 | test | 3 | 64.65 | 64.44 | 66.30 | 0.41 | 69.18 | 72.74 | 1.43 | 78.36 | 48.47 | 67.13 |
| SR02-marbert_aya | dev | 3 | 78.18 | 77.83 | 78.74 | 0.87 | 79.16 | 77.19 | 0.93 | 80.52 | 80.16 | 73.85 |
| SR02-marbert_aya | test | 3 | 64.48 | 63.72 | 66.20 | 0.08 | 68.53 | 72.36 | 0.91 | 77.78 | 48.73 | 66.94 |
| SR02-arabertv02_twitter_fanar | dev | 3 | 77.81 | 78.03 | 77.71 | 0.84 | 79.13 | 76.65 | 0.43 | 81.07 | 80.14 | 72.23 |
| SR02-arabertv02_twitter_fanar | test | 3 | 63.82 | 63.47 | 65.07 | 0.59 | 68.34 | 71.25 | 0.37 | 77.75 | 48.96 | 64.74 |
| SR02-arabertv02_twitter_qwen3 | dev | 3 | 77.85 | 78.17 | 77.62 | 0.95 | 79.21 | 76.52 | 0.79 | 80.78 | 80.52 | 72.26 |
| SR02-arabertv02_twitter_qwen3 | test | 3 | 63.88 | 63.38 | 65.25 | 0.79 | 68.27 | 71.14 | 0.44 | 77.63 | 49.35 | 64.65 |
| SR02-arabertv02_twitter_aya | dev | 3 | 77.49 | 77.86 | 77.22 | 1.42 | 78.73 | 76.19 | 1.14 | 79.95 | 80.08 | 72.43 |
| SR02-arabertv02_twitter_aya | test | 3 | 63.63 | 62.85 | 65.22 | 0.36 | 67.52 | 70.75 | 0.74 | 76.66 | 49.40 | 64.84 |

| Model | Split | Run | Macro F1 | Macro P | Macro R | Δ F1 vs SR01 |
|---|---|---|---|---|---|---|
| marbertv2 | dev | SR01 real only | 78.42 ± 0.44 | 78.35 ± 0.36 | 78.67 ± 0.52 |  |
| marbertv2 | dev | SR02 + SG01 Fanar | 79.27 ± 0.62 | 78.96 ± 0.26 | 79.81 ± 1.30 | +0.85 |
| marbertv2 | dev | SR02 + SG01 Qwen3 | 78.28 ± 0.60 | 77.71 ± 0.59 | 79.06 ± 0.65 | -0.14 |
| marbertv2 | dev | SR02 + SG01 Aya | 78.99 ± 0.28 | 78.64 ± 0.28 | 79.42 ± 0.48 | +0.57 |
| marbertv2 | test | SR01 real only | 63.95 ± 0.20 | 63.81 ± 1.08 | 66.06 ± 0.41 |  |
| marbertv2 | test | SR02 + SG01 Fanar | 64.45 ± 0.53 | 63.89 ± 0.19 | 66.52 ± 0.15 | +0.50 |
| marbertv2 | test | SR02 + SG01 Qwen3 | 64.08 ± 0.46 | 63.44 ± 0.34 | 66.31 ± 0.57 | +0.13 |
| marbertv2 | test | SR02 + SG01 Aya | 64.09 ± 0.23 | 63.29 ± 0.25 | 66.10 ± 0.15 | +0.14 |
| marbert | dev | SR01 real only | 78.68 ± 0.42 | 78.79 ± 0.53 | 78.79 ± 1.14 |  |
| marbert | dev | SR02 + SG01 Fanar | 78.35 ± 0.66 | 78.64 ± 0.20 | 78.24 ± 1.19 | -0.33 |
| marbert | dev | SR02 + SG01 Qwen3 | 78.20 ± 0.63 | 77.86 ± 0.78 | 78.76 ± 0.73 | -0.48 |
| marbert | dev | SR02 + SG01 Aya | 78.18 ± 0.99 | 77.83 ± 1.32 | 78.74 ± 0.87 | -0.50 |
| marbert | test | SR01 real only | 65.14 ± 0.46 | 65.05 ± 0.42 | 66.50 ± 0.15 |  |
| marbert | test | SR02 + SG01 Fanar | 65.62 ± 0.92 | 65.69 ± 0.37 | 66.81 ± 0.72 | +0.48 |
| marbert | test | SR02 + SG01 Qwen3 | 64.65 ± 0.55 | 64.44 ± 1.30 | 66.30 ± 0.41 | -0.49 |
| marbert | test | SR02 + SG01 Aya | 64.48 ± 0.54 | 63.72 ± 0.81 | 66.20 ± 0.08 | -0.66 |
| arabertv02_twitter | dev | SR01 real only | 77.31 ± 0.26 | 77.24 ± 0.56 | 77.42 ± 0.17 |  |
| arabertv02_twitter | dev | SR02 + SG01 Fanar | 77.81 ± 0.41 | 78.03 ± 0.28 | 77.71 ± 0.84 | +0.50 |
| arabertv02_twitter | dev | SR02 + SG01 Qwen3 | 77.85 ± 0.67 | 78.17 ± 0.35 | 77.62 ± 0.95 | +0.54 |
| arabertv02_twitter | dev | SR02 + SG01 Aya | 77.49 ± 0.95 | 77.86 ± 0.44 | 77.22 ± 1.42 | +0.18 |
| arabertv02_twitter | test | SR01 real only | 63.78 ± 0.28 | 63.69 ± 0.02 | 65.76 ± 0.48 |  |
| arabertv02_twitter | test | SR02 + SG01 Fanar | 63.82 ± 0.36 | 63.47 ± 0.36 | 65.07 ± 0.59 | +0.04 |
| arabertv02_twitter | test | SR02 + SG01 Qwen3 | 63.88 ± 0.39 | 63.38 ± 0.32 | 65.25 ± 0.79 | +0.10 |
| arabertv02_twitter | test | SR02 + SG01 Aya | 63.63 ± 0.54 | 62.85 ± 0.69 | 65.22 ± 0.36 | -0.15 |

Takeaway:
- if BERTS show improvement then train the LLMs