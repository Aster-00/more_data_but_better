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
| SR01-camelbert_mix | dev | `sr01_camelbert_mix` | 3 | 76.67 | 76.79 | 76.63 | 0.14 | 77.85 | 75.52 | 0.54 | 79.28 | 78.98 | 71.76 |
| SR01-camelbert_mix | test | `sr01_camelbert_mix` | 3 | 61.70 | 61.88 | 63.20 | 0.59 | 66.92 | 69.54 | 0.30 | 76.84 | 46.02 | 62.24 |
| SR01-camelbert_da | dev | `sr01_camelbert_da` | 3 | 74.90 | 74.78 | 75.04 | 0.20 | 75.95 | 73.34 | 0.21 | 75.80 | 78.03 | 70.88 |
| SR01-camelbert_da | test | `sr01_camelbert_da` | 3 | 62.00 | 62.17 | 63.43 | 0.61 | 67.24 | 69.99 | 0.52 | 77.20 | 46.02 | 62.78 |
| SR01-arbert | dev | `sr01_arbert` | 3 | 76.16 | 75.76 | 76.81 | 0.61 | 77.69 | 74.65 | 0.16 | 79.94 | 79.19 | 69.36 |
| SR01-arbert | test | `sr01_arbert` | 3 | 62.78 | 62.75 | 64.47 | 0.36 | 67.53 | 69.77 | 0.33 | 77.18 | 48.79 | 62.36 |
| SR01-arbertv2 | dev | `sr01_arbertv2` | 3 | 75.56 | 74.81 | 76.85 | 0.16 | 77.07 | 73.72 | 0.56 | 79.05 | 79.23 | 68.39 |
| SR01-arbertv2 | test | `sr01_arbertv2` | 3 | 61.10 | 61.92 | 64.05 | 0.84 | 66.23 | 69.28 | 1.16 | 76.13 | 44.74 | 62.43 |

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

| Generator | Requested | Distinct texts | Kept after filter | Exact dup. | Near dup. | Script | Length | Unparsed | Selected | Short cells | Test matches | Translations cut | Texts/s | Mean words (selected) | Imbalance (max : min) | MSA share | Dialectness | Lexical diversity | Topic spread (of 30) | Semantic diversity (Vendi) | Repeats | Fidelity |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Jais-2-8B | 15,600 | 4,398 (28.2%) | 3,432 (22.0%) | 11,168 | 950 | 14 | 1 | 35 | 3,402 | 10 of 12 | 0 | 264 | 4.07 | 12.4 | 62.5 : 1 | 9.6% | 0.69 | 339 | 9 | 2.8 | 77.7% | 98.0% |
| Fanar-1-9B | 7,800 | 7,794 (99.9%) | 7,760 (99.5%) | 6 | 1 | 26 | 7 | 0 | 6,000 | 0 of 12 | 0 | 116 | 1.28 | 13.8 | 1.0 : 1 | 25.0% | 0.48 | 1123 | 11 | 3.1 | 0.1% | 94.9% |
| Qwen3-8B | 7,800 | 7,772 (99.6%) | 7,752 (99.4%) | 28 | 5 | 6 | 9 | 0 | 6,000 | 0 of 12 | 0 | 2 | 1.93 | 13.9 | 1.0 : 1 | 22.1% | 0.56 | 323 | 8 | 3.2 | 0.4% | 88.7% |
| Aya-Expanse-8B | 7,800 | 7,714 (98.9%) | 7,499 (96.1%) | 86 | 213 | 1 | 1 | 0 | 6,000 | 0 of 12 | 0 | 4 | 2.20 | 17.4 | 1.0 : 1 | 20.4% | 0.57 | 499 | 7 | 2.8 | 3.8% | 91.2% |
| S1 real (reference) | — | — | — | — | — | — | — | — | — | — | — | — | — | — | 37.7 : 1 | 22.4% | 0.54 | 2518 | 29 | 4.0 | 1.0% | 80.3% |



**Column explanation:**
-  Script: Rejected because under 70% of the letters are Arabic script, e.g. mostly English, or Chinese characters mixed in
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
| SR02-camelbert_mix_fanar | dev | 3 | 75.71 | 76.01 | 75.61 | 1.10 | 77.10 | 74.06 | 1.02 | 77.84 | 79.01 | 70.29 |
| SR02-camelbert_mix_fanar | test | 3 | 61.71 | 62.11 | 62.70 | 1.38 | 66.88 | 69.48 | 0.59 | 76.63 | 46.18 | 62.33 |
| SR02-camelbert_mix_qwen3 | dev | 3 | 76.50 | 76.34 | 76.90 | 2.09 | 77.53 | 75.37 | 1.46 | 78.65 | 78.75 | 72.09 |
| SR02-camelbert_mix_qwen3 | test | 3 | 61.56 | 61.58 | 63.02 | 0.06 | 66.51 | 69.12 | 0.31 | 76.39 | 46.42 | 61.86 |
| SR02-camelbert_mix_aya | dev | 3 | 75.62 | 75.91 | 75.44 | 0.79 | 76.73 | 74.20 | 0.65 | 76.99 | 78.48 | 71.40 |
| SR02-camelbert_mix_aya | test | 3 | 61.45 | 61.10 | 62.88 | 0.26 | 66.16 | 68.82 | 0.84 | 75.99 | 46.70 | 61.65 |
| SR02-camelbert_da_fanar | dev | 3 | 74.28 | 74.28 | 74.43 | 0.99 | 75.66 | 72.22 | 0.40 | 75.33 | 78.41 | 69.11 |
| SR02-camelbert_da_fanar | test | 3 | 62.07 | 61.48 | 63.46 | 0.41 | 66.38 | 69.05 | 0.57 | 76.00 | 48.10 | 62.09 |
| SR02-camelbert_da_qwen3 | dev | 3 | 74.45 | 74.54 | 74.43 | 0.60 | 75.60 | 72.96 | 0.47 | 76.03 | 77.41 | 69.90 |
| SR02-camelbert_da_qwen3 | test | 3 | 62.11 | 61.89 | 62.98 | 0.43 | 67.04 | 69.76 | 0.53 | 77.00 | 46.80 | 62.52 |
| SR02-camelbert_da_aya | dev | 3 | 74.23 | 74.00 | 74.58 | 1.03 | 75.31 | 72.51 | 1.14 | 74.86 | 77.68 | 70.16 |
| SR02-camelbert_da_aya | test | 3 | 61.87 | 61.53 | 63.30 | 0.16 | 66.69 | 69.75 | 1.00 | 76.66 | 46.11 | 62.84 |
| SR02-arbert_fanar | dev | 3 | 76.92 | 76.93 | 76.93 | 0.24 | 78.71 | 74.92 | 0.83 | 80.32 | 80.92 | 69.53 |
| SR02-arbert_fanar | test | 3 | 62.88 | 62.06 | 64.68 | 0.23 | 66.77 | 69.43 | 1.00 | 76.12 | 49.79 | 62.74 |
| SR02-arbert_qwen3 | dev | 3 | 76.29 | 76.93 | 75.90 | 0.50 | 78.20 | 74.51 | 0.58 | 80.36 | 79.87 | 68.65 |
| SR02-arbert_qwen3 | test | 3 | 63.04 | 62.86 | 63.57 | 0.85 | 67.70 | 69.87 | 0.33 | 77.37 | 49.38 | 62.37 |
| SR02-arbert_aya | dev | 3 | 75.88 | 75.87 | 75.93 | 0.50 | 77.72 | 73.96 | 0.67 | 79.73 | 79.74 | 68.18 |
| SR02-arbert_aya | test | 3 | 62.53 | 61.70 | 64.06 | 0.25 | 66.51 | 69.43 | 0.10 | 75.93 | 48.71 | 62.94 |
| SR02-arbertv2_fanar | dev | 3 | 76.06 | 76.32 | 75.88 | 0.46 | 77.80 | 74.23 | 0.07 | 79.47 | 79.72 | 68.98 |
| SR02-arbertv2_fanar | test | 3 | 63.26 | 62.82 | 64.71 | 0.48 | 67.70 | 70.75 | 1.53 | 77.18 | 48.29 | 64.31 |
| SR02-arbertv2_qwen3 | dev | 3 | 75.72 | 76.05 | 75.59 | 0.09 | 77.31 | 74.08 | 0.50 | 78.92 | 78.99 | 69.25 |
| SR02-arbertv2_qwen3 | test | 3 | 63.25 | 63.26 | 64.00 | 0.48 | 68.09 | 71.13 | 0.60 | 77.50 | 47.49 | 64.76 |
| SR02-arbertv2_aya | dev | 3 | 75.64 | 76.00 | 75.48 | 0.15 | 77.15 | 73.96 | 0.40 | 78.40 | 78.99 | 69.52 |
| SR02-arbertv2_aya | test | 3 | 62.44 | 62.32 | 63.66 | 0.64 | 66.88 | 69.86 | 1.18 | 76.25 | 47.60 | 63.47 |

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
| camelbert_mix | dev | SR01 real only | 76.67 ± 0.32 | 76.79 ± 0.54 | 76.63 ± 0.14 |  |
| camelbert_mix | dev | SR02 + SG01 Fanar | 75.71 ± 0.77 | 76.01 ± 0.76 | 75.61 ± 1.10 | -0.96 |
| camelbert_mix | dev | SR02 + SG01 Qwen3 | 76.50 ± 1.16 | 76.34 ± 0.40 | 76.90 ± 2.09 | -0.17 |
| camelbert_mix | dev | SR02 + SG01 Aya | 75.62 ± 0.50 | 75.91 ± 0.16 | 75.44 ± 0.79 | -1.05 |
| camelbert_mix | test | SR01 real only | 61.70 ± 0.14 | 61.88 ± 0.05 | 63.20 ± 0.59 |  |
| camelbert_mix | test | SR02 + SG01 Fanar | 61.71 ± 0.35 | 62.11 ± 1.62 | 62.70 ± 1.38 | +0.01 |
| camelbert_mix | test | SR02 + SG01 Qwen3 | 61.56 ± 0.63 | 61.58 ± 0.27 | 63.02 ± 0.06 | -0.14 |
| camelbert_mix | test | SR02 + SG01 Aya | 61.45 ± 0.51 | 61.10 ± 0.89 | 62.88 ± 0.26 | -0.25 |
| camelbert_da | dev | SR01 real only | 74.90 ± 0.19 | 74.78 ± 0.41 | 75.04 ± 0.20 |  |
| camelbert_da | dev | SR02 + SG01 Fanar | 74.28 ± 0.29 | 74.28 ± 0.47 | 74.43 ± 0.99 | -0.62 |
| camelbert_da | dev | SR02 + SG01 Qwen3 | 74.45 ± 0.21 | 74.54 ± 0.22 | 74.43 ± 0.60 | -0.45 |
| camelbert_da | dev | SR02 + SG01 Aya | 74.23 ± 0.82 | 74.00 ± 0.74 | 74.58 ± 1.03 | -0.67 |
| camelbert_da | test | SR01 real only | 62.00 ± 0.84 | 62.17 ± 0.89 | 63.43 ± 0.61 |  |
| camelbert_da | test | SR02 + SG01 Fanar | 62.07 ± 0.69 | 61.48 ± 0.79 | 63.46 ± 0.41 | +0.07 |
| camelbert_da | test | SR02 + SG01 Qwen3 | 62.11 ± 0.56 | 61.89 ± 0.79 | 62.98 ± 0.43 | +0.11 |
| camelbert_da | test | SR02 + SG01 Aya | 61.87 ± 0.49 | 61.53 ± 0.88 | 63.30 ± 0.16 | -0.13 |
| arbert | dev | SR01 real only | 76.16 ± 0.27 | 75.76 ± 0.76 | 76.81 ± 0.61 |  |
| arbert | dev | SR02 + SG01 Fanar | 76.92 ± 0.43 | 76.93 ± 0.60 | 76.93 ± 0.24 | +0.76 |
| arbert | dev | SR02 + SG01 Qwen3 | 76.29 ± 0.35 | 76.93 ± 0.62 | 75.90 ± 0.50 | +0.13 |
| arbert | dev | SR02 + SG01 Aya | 75.88 ± 0.29 | 75.87 ± 0.23 | 75.93 ± 0.50 | -0.28 |
| arbert | test | SR01 real only | 62.78 ± 0.02 | 62.75 ± 0.43 | 64.47 ± 0.36 |  |
| arbert | test | SR02 + SG01 Fanar | 62.88 ± 0.49 | 62.06 ± 0.52 | 64.68 ± 0.23 | +0.10 |
| arbert | test | SR02 + SG01 Qwen3 | 63.04 ± 0.48 | 62.86 ± 0.46 | 63.57 ± 0.85 | +0.26 |
| arbert | test | SR02 + SG01 Aya | 62.53 ± 0.15 | 61.70 ± 0.14 | 64.06 ± 0.25 | -0.25 |
| arbertv2 | dev | SR01 real only | 75.56 ± 0.46 | 74.81 ± 0.67 | 76.85 ± 0.16 |  |
| arbertv2 | dev | SR02 + SG01 Fanar | 76.06 ± 0.04 | 76.32 ± 0.57 | 75.88 ± 0.46 | +0.50 |
| arbertv2 | dev | SR02 + SG01 Qwen3 | 75.72 ± 0.20 | 76.05 ± 0.38 | 75.59 ± 0.09 | +0.16 |
| arbertv2 | dev | SR02 + SG01 Aya | 75.64 ± 0.45 | 76.00 ± 1.23 | 75.48 ± 0.15 | +0.08 |
| arbertv2 | test | SR01 real only | 61.10 ± 1.22 | 61.92 ± 1.11 | 64.05 ± 0.84 |  |
| arbertv2 | test | SR02 + SG01 Fanar | 63.26 ± 1.26 | 62.82 ± 1.48 | 64.71 ± 0.48 | +2.16 |
| arbertv2 | test | SR02 + SG01 Qwen3 | 63.25 ± 0.47 | 63.26 ± 0.94 | 64.00 ± 0.48 | +2.15 |
| arbertv2 | test | SR02 + SG01 Aya | 62.44 ± 0.71 | 62.32 ± 2.07 | 63.66 ± 0.64 | +1.34 |



| Split | NEG | NEU |POS	| Best class | Worst class |
|---|---|---|---|---|---| 
| Dev	| 79.7	 | 79.8 |	71.8	| NEG and NEU tie (12 members each) | POS (all 24 members) |
| Test | 77.5 | 48.6 | 64.7 | NEG (all 24) | NEU (all 24) |

| | POS precision | POS recall |
|---|---|--
| Jais-2 | 71.7 | 86.0 |
| MARBERT | 66.3 | 88.0 |

Takeaway:
- BERTS dont show improvement
- SR02, per-class F1 averaged over all 24 members:
  - In dev 
    - POS is the worst falling behind by 8 points and it is the worst for all the 24 members
    - NEG and NEU are the best models tied by 12 models each
  - In Test 
    - NEU is the worst for all 2 models
  - a fifth of the NEG statements that were labelled POS were labelling errors by the annotators which fits the 80% agreement between annotators
- When i looked at the errors of NEG tweets that the models labelled as positive they were mostly angry prayers, sad news with positive words, and hopeful tweets that mention hardship, which is what the model needs to train on better. This is the "Better Data" 

**Future runs
- SG02 same prompt but with one shot
- SG03 few shot
- SG04 few shot with controlled generation
  - lexical diverisity
  - semantic diversity
  - topic diversity
- before any runs define constrains to ensure that generated datasets will look like real
    - if there is time, find which constraint is the most effective
 no improvement shown beyond noise, no need to run Jais


## SR03 real data only, NEU dropped

S1 train / dev / test without NEU tweets (6,069 / 675 / 2,252), 2-class NEG/POS head, 3 seeds (SD-007). Macro F1 is over NEG and POS only (so f1_pn = macro_f1); not comparable with SR01/SR02.

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_pn | f1_pn_std | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SR03-jais2 | dev | `sr03_jais2` | 3 | 92.56 | 93.07 | 92.12 | 0.83 | 93.58 | 92.56 | 0.50 | 95.31 | – | 89.80 |
| SR03-jais2 | test | `sr03_jais2` | 3 | 84.85 | 83.34 | 87.17 | 0.44 | 87.76 | 84.85 | 0.74 | 91.48 | – | 78.21 |
| SR03-fanar | dev | `sr03_fanar` | 3 | 92.01 | 91.77 | 92.29 | 0.88 | 92.99 | 92.01 | 0.71 | 94.80 | – | 89.22 |
| SR03-fanar | test | `sr03_fanar` | 3 | 84.23 | 82.52 | 87.06 | 0.59 | 87.11 | 84.23 | 0.08 | 90.96 | – | 77.50 |
| SR03-aya | dev | `sr03_aya` | 3 | 91.91 | 91.90 | 91.93 | 0.33 | 92.94 | 91.91 | 0.33 | 94.79 | – | 89.03 |
| SR03-aya | test | `sr03_aya` | 3 | 83.29 | 81.58 | 86.33 | 0.50 | 86.25 | 83.29 | 0.65 | 90.32 | – | 76.27 |
| SR03-marbertv2 | dev | `sr03_marbertv2` | 3 | 91.62 | 91.43 | 91.87 | 0.15 | 92.64 | 91.62 | 0.43 | 94.54 | – | 88.69 |
| SR03-marbertv2 | test | `sr03_marbertv2` | 3 | 81.88 | 80.21 | 86.16 | 1.02 | 84.61 | 81.88 | 2.33 | 88.89 | – | 74.87 |
| SR03-marbert | dev | `sr03_marbert` | 3 | 91.45 | 91.52 | 91.39 | 0.27 | 92.54 | 91.45 | 0.62 | 94.51 | – | 88.38 |
| SR03-marbert | test | `sr03_marbert` | 3 | 82.64 | 80.83 | 86.32 | 0.55 | 85.49 | 82.64 | 0.73 | 89.68 | – | 75.60 |
| SR03-camelbert_mix | dev | `sr03_camelbert_mix` | 3 | 90.16 | 90.41 | 89.99 | 0.99 | 91.46 | 90.16 | 0.58 | 93.73 | – | 86.59 |
| SR03-camelbert_mix | test | `sr03_camelbert_mix` | 3 | 79.93 | 78.46 | 82.53 | 0.42 | 83.54 | 79.93 | 0.77 | 88.44 | – | 71.41 |
| SR03-arabertv02_twitter | dev | `sr03_arabertv02_twitter` | 3 | 90.13 | 90.03 | 90.28 | 0.37 | 91.36 | 90.13 | 0.75 | 93.61 | – | 86.66 |
| SR03-arabertv02_twitter | test | `sr03_arabertv02_twitter` | 3 | 81.43 | 79.76 | 84.64 | 0.35 | 84.61 | 81.43 | 0.76 | 89.11 | – | 73.76 |
| SR03-qwen3 | dev | `sr03_qwen3` | 3 | 89.89 | 90.05 | 89.76 | 0.90 | 91.21 | 89.89 | 0.46 | 93.54 | – | 86.23 |
| SR03-qwen3 | test | `sr03_qwen3` | 3 | 80.42 | 78.89 | 83.39 | 0.34 | 83.82 | 80.42 | 0.93 | 88.57 | – | 72.27 |
| SR03-arbert | dev | `sr03_arbert` | 3 | 89.42 | 89.08 | 89.85 | 0.43 | 90.67 | 89.42 | 0.33 | 93.05 | – | 85.78 |
| SR03-arbert | test | `sr03_arbert` | 3 | 79.40 | 77.82 | 83.02 | 0.19 | 82.68 | 79.40 | 0.79 | 87.62 | – | 71.18 |
| SR03-falcon_h1 | dev | `sr03_falcon_h1` | 3 | 89.08 | 89.55 | 88.73 | 0.62 | 90.57 | 89.08 | 0.16 | 93.11 | – | 85.06 |
| SR03-falcon_h1 | test | `sr03_falcon_h1` | 3 | 81.17 | 79.84 | 83.69 | 0.46 | 84.62 | 81.17 | 1.18 | 89.21 | – | 73.13 |
| SR03-arbertv2 | dev | `sr03_arbertv2` | 3 | 88.85 | 88.25 | 89.65 | 0.29 | 90.07 | 88.85 | 0.85 | 92.54 | – | 85.16 |
| SR03-arbertv2 | test | `sr03_arbertv2` | 3 | 80.21 | 78.57 | 84.50 | 0.47 | 83.16 | 80.21 | 1.13 | 87.84 | – | 72.59 |
| SR03-camelbert_da | dev | `sr03_camelbert_da` | 3 | 86.78 | 86.07 | 87.83 | 0.13 | 88.15 | 86.78 | 0.79 | 91.03 | – | 82.52 |
| SR03-camelbert_da | test | `sr03_camelbert_da` | 3 | 77.17 | 76.00 | 82.21 | 1.22 | 80.09 | 77.17 | 2.43 | 85.30 | – | 69.04 |

**Takeaways**:
- NEU labels have alot of inaccuracies
- need to explore annotation standards, what is considered NEU, POS or NEG

**Future Runs**
- 