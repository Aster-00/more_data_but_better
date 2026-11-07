 ## Dataset for Sentiment Analysis (ArSarcasm-V2)
### Here are it's annotation guidelines
Positive (POS): Text whose overall feeling is positive. This includes congratulations, celebrations or occasions, wins or gains, and any event that brings good news or optimism.

e.g. a tweet saying Mohamed Salah deserves the best-player award.

Negative (NEG): Text that expresses something negative or sad, or reports bad news. Anger or strong emotional agitation also counts as negative.

e.g. an Egyptian-dialect tweet saying there’s zero excitement about the World Cup qualifiers.

Neutral (NEU): Text with neither positive nor negative expressions.

e.g. a question about how many qualifier matches someone played, or a news-style quote reported without the writer’s own sentiment.

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
- SG04 generate synthetic data for ArSarcasmV2 but with few shot and not controlled: DONE
- SG05 generate synthetic data for diverse topics for ArSarcasmV2 for dialects using stats of the ArSarcasmV2
  - Compare it with the 0 shot performance 
- SG06 but neuron activated
  - after understanding the neurons activation from the ArSar2 we need to monitor if any trend happens for a specific class or dialect that fires unfamiliar neurons and look at that text and figure out how different that text is from the text from the other neurons. For generation and learning text
- SG07 but vector Steered
- SG08 neuron activated and vector steered (if possible)

## Universal Topic Clustering

One frozen topic list for every dataset, real or generated, so the topic mix of any two sets can be compared (quality row 5). Both tracks use it (D-018, D-019).

- **Pool:** 555,820 unique texts from 19 datasets, both tracks (`data/topics/pool/universal_v1.jsonl`, `scripts/topics/build_topic_pool.py`). Only Arabic-script texts (at least 70% Arabic letters), only human-written (no machine translation, no LLM output), no song lyrics. MLADI dev, ArSarcasm-v2 test and all synthetic sets are left out.
- **Cleaning (D-015):** placeholders, links and mentions removed, hashtags turned into words, laughter shortened, texts under 5 words dropped: 489,815 texts.
- **Cap:** at most 20,000 texts per dataset, so no single dataset sets the topics: 181,905 texts.
- **Clustering:** E5 embeddings, k-means with 50 clusters, seed 0 (`configs/quality/topics_universal_clean_k50.json`, 18 min). Ammar reviewed every cluster and named 18 topics. Report with tweets per cluster: `data/topics/universal_clean_k50_seed0/report.md`. Backup: private Hub dataset `Ammar-06/thesis-topic-embeddings`.

| Topic | Clusters | Texts | Share |
|---|---|---|---|
| Books and novels | 20, 19, 29, 40, 11 | 22,957 | 12.6% |
| COVID-19 | 18, 12, 22, 7, 21 | 18,835 | 10.4% |
| Hotels and stays | 33, 42, 31, 24, 49, 8 | 18,138 | 10.0% |
| Religion and prayer | 15, 34 | 9,325 | 5.1% |
| Politics and government | 30, 10 | 9,286 | 5.1% |
| War and conflict | 39, 5 | 9,144 | 5.0% |
| Restaurants and food | 46, 6, 25 | 9,126 | 5.0% |
| Love and feelings | 26, 47 | 8,634 | 4.7% |
| News and official announcements | 28, 2 | 6,455 | 3.5% |
| Products and shopping | 37, 13 | 6,298 | 3.5% |
| Greetings | 23, 32 | 5,357 | 2.9% |
| Films, TV, music and celebrities | 9, 36 | 5,331 | 2.9% |
| Football | 0 | 4,494 | 2.5% |
| Friendship and affection | 4 | 4,284 | 2.4% |
| Places, malls and attractions | 1 | 2,718 | 1.5% |
| Apps, phones and technology | 48 | 2,591 | 1.4% |
| Women's empowerment | 27 | 1,587 | 0.9% |
| Digital transformation | 38 | 1,407 | 0.8% |
| Not named | 14, 45, 3, 43, 44, 35, 17, 41, 16 | 35,938 | 19.8% |

**Takeaways:**
- Unlike D1, one subject is split by sentiment and length (hotels 6 clusters, books 5, COVID-19 5); these splits were merged, since only the subject counts.
- Books, COVID-19 and hotels are a third of the pool, and each comes mainly from one or two datasets (LABR and 100k Reviews; ArSen-20; TripAdvisor and 100k Reviews).
- Unnamed clusters are grouped by form, not subject: mixed chatter, very short emoji replies, stretched letters, questions (C16) and short negative statements (C17, a tone).
- The list is for measurement only. Generation topics stay the 24 of D-016.

## SG02

**Topic spread across the universal topic list**
Few shot Generation

Frozen list `universal_clean_k50_seed0` (50 E5 clusters, 18 named topics, D-019). Texts cleaned as the pool (D-015), under 5 words not scored. Effective topics = exp(entropy), mean ± std over 10 samples of 800 texts. Distance to real = Jensen-Shannon divergence (base 2, 0 = same mix, 1 = no overlap) between the set's topic shares (18 named topics + unnamed) and S1 real train. Generated by `python -m src.quality.topic_spread` (`results/quality/sentiment/universal_topics.json`).

| Set | Effective clusters (of 50) | Effective named topics (of 18) | Unnamed | Distance to real | War | Politics | News | Religion | Greetings | Love |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 real train | 15.6 ± 0.7 | 6.5 ± 0.5 | 19% | 0.000 | 38% | 6% | 7% | 3% | 3% | 4% |
| SG01 Jais-2 | 17.6 ± 0.5 | 7.0 ± 0.3 | 36% | 0.336 | 0% | 3% | 8% | 23% | 12% | 7% |
| SG01 Fanar | 16.8 ± 0.7 | 8.7 ± 0.4 | 25% | 0.257 | 4% | 10% | 9% | 15% | 19% | 6% |
| SG02 Fanar | 17.9 ± 0.5 | 10.2 ± 0.2 | 10% | 0.179 | 9% | 15% | 15% | 14% | 9% | 5% |
| SG01 Qwen3 | 15.7 ± 0.4 | 7.7 ± 0.3 | 39% | 0.272 | 1% | 9% | 9% | 14% | 2% | 16% |
| SG02 Qwen3 | 20.4 ± 0.5 | 10.3 ± 0.3 | 35% | 0.143 | 6% | 10% | 10% | 9% | 2% | 8% |
| SG01 Aya | 16.7 ± 0.4 | 8.8 ± 0.3 | 31% | 0.318 | 1% | 8% | 5% | 14% | 17% | 7% |
| SG02 Aya | 18.8 ± 0.3 | 10.9 ± 0.2 | 16% | 0.190 | 9% | 14% | 7% | 10% | 15% | 3% |



**Fidelity against diversity**


| Set | Fidelity | Fidelity NEU | MTLD | Vendi | Topic spread (of 30) | Effective universal topics (of 18) | Distance to real |
|---|---|---|---|---|---|---|---|
| S1 real (reference) | 80.3% | 78.9% | 2518 | 4.01 | 29 | 6.5 | 0.000 |
| SG01 Jais-2 | 98.0% | 90.1% | 339 | 2.76 | 9 | 7.0 | 0.336 |
| SG01 Fanar | 94.9% | 85.2% | 1123 | 3.09 | 11 | 8.7 | 0.257 |
| SG02 Fanar | 95.4% | 87.0% | 1756 | 3.41 | 13 | 10.2 | 0.179 |
| SG01 Qwen3 | 88.7% | 74.5% | 323 | 3.22 | 8 | 7.7 | 0.272 |
| SG02 Qwen3 | 88.2% | 74.8% | 507 | 3.62 | 17 | 10.3 | 0.143 |
| SG01 Aya | 91.2% | 73.7% | 499 | 2.77 | 7 | 8.8 | 0.318 |
| SG02 Aya | 89.0% | 67.7% | 1053 | 3.15 | 10 | 10.9 | 0.190 |

**Takeaway:**
- ArSarcasm-v2 is very focused on war
- need to identify the unnamed topics to train the E5 on them to generate better
- why is topic spread of 30 lower than topic spread of 18?
- need to increase MTLD, Vendi and possibly Topic spread of 30 if found to be useful

## SR04 Real + SG02


Mean over seeds 42/43/44. Generated from `docs/sentiment/tables/sentiment_summary.csv`.

| id | split | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_pn | f1_pn_std | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| SR04-marbertv2_fanar | dev | 3 | 79.10 | 78.73 | 79.57 | 0.42 | 80.23 | 78.21 | 0.02 | 82.44 | 80.88 | 73.98 |
| SR04-marbertv2_fanar | test | 3 | 63.63 | 62.86 | 65.78 | 0.10 | 67.90 | 71.37 | 0.70 | 77.69 | 48.16 | 65.06 |
| SR04-marbert_qwen3 | dev | 3 | 78.79 | 78.28 | 79.51 | 0.28 | 79.64 | 77.87 | 0.49 | 80.65 | 80.64 | 75.08 |
| SR04-marbert_qwen3 | test | 3 | 64.28 | 64.37 | 66.11 | 1.06 | 69.12 | 72.63 | 0.90 | 78.46 | 47.57 | 66.80 |
| SR04-marbertv2_qwen3 | dev | 3 | 78.51 | 78.18 | 79.01 | 0.41 | 79.64 | 77.43 | 0.29 | 81.28 | 80.67 | 73.57 |
| SR04-marbertv2_qwen3 | test | 3 | 64.92 | 64.62 | 66.61 | 0.25 | 69.64 | 73.22 | 0.50 | 79.13 | 48.33 | 67.31 |
| SR04-marbertv2_aya | dev | 3 | 78.50 | 78.33 | 78.73 | 0.92 | 79.83 | 77.29 | 0.80 | 81.85 | 80.92 | 72.72 |
| SR04-marbertv2_aya | test | 3 | 64.08 | 63.31 | 66.12 | 0.49 | 68.28 | 71.99 | 0.49 | 77.79 | 48.24 | 66.20 |
| SR04-marbert_aya | dev | 3 | 78.46 | 78.12 | 78.88 | 0.30 | 79.35 | 77.55 | 0.32 | 80.50 | 80.27 | 74.61 |
| SR04-marbert_aya | test | 3 | 64.90 | 64.48 | 66.69 | 0.11 | 69.32 | 73.11 | 0.97 | 78.44 | 48.47 | 67.79 |
| SR04-marbert_fanar | dev | 3 | 78.46 | 78.48 | 78.53 | 0.64 | 79.40 | 77.55 | 0.39 | 80.64 | 80.27 | 74.47 |
| SR04-marbert_fanar | test | 3 | 64.78 | 64.80 | 66.26 | 0.40 | 69.77 | 73.61 | 0.21 | 79.19 | 47.13 | 68.02 |
| SR04-arabertv02_twitter_qwen3 | dev | 3 | 77.90 | 77.85 | 78.06 | 1.38 | 79.13 | 76.66 | 1.15 | 80.61 | 80.39 | 72.71 |
| SR04-arabertv02_twitter_qwen3 | test | 3 | 63.72 | 63.35 | 65.59 | 0.55 | 68.17 | 71.24 | 0.74 | 77.48 | 48.69 | 65.00 |
| SR04-arabertv02_twitter_fanar | dev | 3 | 77.52 | 77.86 | 77.22 | 0.46 | 78.89 | 76.20 | 0.31 | 80.63 | 80.14 | 71.78 |
| SR04-arabertv02_twitter_fanar | test | 3 | 63.96 | 63.30 | 65.48 | 0.29 | 68.13 | 70.96 | 0.17 | 77.45 | 49.96 | 64.47 |
| SR04-arabertv02_twitter_aya | dev | 3 | 76.92 | 77.31 | 76.65 | 1.29 | 78.41 | 75.38 | 1.20 | 79.87 | 79.99 | 70.90 |
| SR04-arabertv02_twitter_aya | test | 3 | 63.74 | 62.96 | 65.41 | 0.71 | 67.68 | 70.94 | 0.33 | 76.78 | 49.34 | 65.09 |
| SR04-camelbert_mix_qwen3 | dev | 3 | 76.82 | 76.53 | 77.18 | 1.16 | 77.96 | 75.53 | 1.34 | 79.07 | 79.40 | 71.98 |
| SR04-camelbert_mix_qwen3 | test | 3 | 61.80 | 61.76 | 63.51 | 0.80 | 66.86 | 69.90 | 0.24 | 76.70 | 45.60 | 63.11 |
| SR04-arbert_qwen3 | dev | 3 | 76.64 | 76.64 | 76.76 | 0.36 | 78.44 | 74.92 | 0.50 | 80.81 | 80.07 | 69.03 |
| SR04-arbert_qwen3 | test | 3 | 63.56 | 63.16 | 64.80 | 0.22 | 67.96 | 70.75 | 0.66 | 77.17 | 49.18 | 64.33 |
| SR04-arbertv2_fanar | dev | 3 | 76.06 | 76.08 | 76.08 | 0.05 | 77.55 | 74.44 | 0.27 | 79.06 | 79.29 | 69.83 |
| SR04-arbertv2_fanar | test | 3 | 62.55 | 61.96 | 64.43 | 0.07 | 66.86 | 69.69 | 0.89 | 76.45 | 48.28 | 62.93 |
| SR04-arbert_fanar | dev | 3 | 75.99 | 75.81 | 76.30 | 0.22 | 77.74 | 73.93 | 0.62 | 79.36 | 80.10 | 68.49 |
| SR04-arbert_fanar | test | 3 | 62.30 | 61.78 | 64.34 | 0.43 | 66.49 | 68.95 | 0.47 | 76.13 | 48.98 | 61.78 |
| SR04-arbertv2_qwen3 | dev | 3 | 75.82 | 75.60 | 76.21 | 0.89 | 77.37 | 74.10 | 0.62 | 78.93 | 79.28 | 69.26 |
| SR04-arbertv2_qwen3 | test | 3 | 63.43 | 63.07 | 65.35 | 0.52 | 67.77 | 70.77 | 0.50 | 76.92 | 48.75 | 64.62 |
| SR04-arbert_aya | dev | 3 | 75.79 | 75.97 | 75.63 | 0.99 | 77.80 | 73.74 | 1.13 | 79.98 | 79.89 | 67.49 |
| SR04-arbert_aya | test | 3 | 62.76 | 62.06 | 64.00 | 0.73 | 66.83 | 69.53 | 0.76 | 76.29 | 49.24 | 62.76 |
| SR04-camelbert_mix_aya | dev | 3 | 75.72 | 76.17 | 75.43 | 1.24 | 76.97 | 74.15 | 0.83 | 77.35 | 78.86 | 70.95 |
| SR04-camelbert_mix_aya | test | 3 | 61.21 | 61.00 | 62.45 | 0.58 | 65.82 | 68.46 | 0.68 | 75.39 | 46.70 | 61.53 |
| SR04-camelbert_mix_fanar | dev | 3 | 75.65 | 75.81 | 75.67 | 0.56 | 76.86 | 74.21 | 0.34 | 77.71 | 78.52 | 70.71 |
| SR04-camelbert_mix_fanar | test | 3 | 61.24 | 60.99 | 63.03 | 0.29 | 65.98 | 68.52 | 0.36 | 75.87 | 46.68 | 61.17 |
| SR04-arbertv2_aya | dev | 3 | 75.63 | 75.96 | 75.55 | 0.80 | 77.21 | 73.91 | 0.63 | 78.57 | 79.08 | 69.25 |
| SR04-arbertv2_aya | test | 3 | 62.80 | 63.10 | 64.04 | 0.67 | 67.86 | 70.75 | 0.60 | 77.40 | 46.91 | 64.09 |
| SR04-camelbert_da_qwen3 | dev | 3 | 74.91 | 74.91 | 75.06 | 0.81 | 76.14 | 73.26 | 0.92 | 76.43 | 78.22 | 70.09 |
| SR04-camelbert_da_qwen3 | test | 3 | 62.03 | 61.99 | 63.39 | 0.40 | 67.02 | 69.55 | 0.65 | 76.89 | 47.01 | 62.21 |
| SR04-camelbert_da_fanar | dev | 3 | 74.16 | 74.13 | 74.32 | 0.50 | 75.44 | 72.27 | 0.30 | 75.27 | 77.92 | 69.28 |
| SR04-camelbert_da_fanar | test | 3 | 62.05 | 61.53 | 63.64 | 0.54 | 66.44 | 69.05 | 1.13 | 76.06 | 48.07 | 62.03 |
| SR04-camelbert_da_aya | dev | 3 | 73.75 | 73.49 | 74.10 | 0.33 | 75.04 | 71.82 | 0.53 | 74.95 | 77.59 | 68.70 |
| SR04-camelbert_da_aya | test | 3 | 61.57 | 60.87 | 63.52 | 0.24 | 65.72 | 68.79 | 0.41 | 75.21 | 47.14 | 62.37 |

**comparing SR02 and SR04**

Macro F1, mean ± std over 3 seeds. SR02 = + SG01 (zero-shot), SR04 = + SG02 (few-shot, k = 5), same generator.

| Model | Split | Generator | SR01 real only | SR02 + SG01 | SR04 + SG02 | Δ SR04 vs SR02 | Δ SR04 vs SR01 |
|---|---|---|---|---|---|---|---|
| marbertv2 | dev | Fanar | 78.42 ± 0.44 | 79.27 ± 0.62 | 79.10 ± 0.03 | -0.17 | +0.68 |
| marbertv2 | dev | Qwen3 | 78.42 ± 0.44 | 78.28 ± 0.60 | 78.51 ± 0.25 | +0.23 | +0.09 |
| marbertv2 | dev | Aya | 78.42 ± 0.44 | 78.99 ± 0.28 | 78.50 ± 0.58 | -0.49 | +0.08 |
| marbertv2 | test | Fanar | 63.95 ± 0.20 | 64.45 ± 0.53 | 63.63 ± 0.57 | -0.82 | -0.32 |
| marbertv2 | test | Qwen3 | 63.95 ± 0.20 | 64.08 ± 0.46 | 64.92 ± 0.29 | +0.84 | +0.97 |
| marbertv2 | test | Aya | 63.95 ± 0.20 | 64.09 ± 0.23 | 64.08 ± 0.57 | -0.01 | +0.13 |
| marbert | dev | Fanar | 78.68 ± 0.42 | 78.35 ± 0.66 | 78.46 ± 0.30 | +0.11 | -0.22 |
| marbert | dev | Qwen3 | 78.68 ± 0.42 | 78.20 ± 0.63 | 78.79 ± 0.46 | +0.59 | +0.11 |
| marbert | dev | Aya | 78.68 ± 0.42 | 78.18 ± 0.99 | 78.46 ± 0.28 | +0.28 | -0.22 |
| marbert | test | Fanar | 65.14 ± 0.46 | 65.62 ± 0.92 | 64.78 ± 0.57 | -0.84 | -0.36 |
| marbert | test | Qwen3 | 65.14 ± 0.46 | 64.65 ± 0.55 | 64.28 ± 0.71 | -0.37 | -0.86 |
| marbert | test | Aya | 65.14 ± 0.46 | 64.48 ± 0.54 | 64.90 ± 0.37 | +0.42 | -0.24 |
| arabertv02_twitter | dev | Fanar | 77.31 ± 0.26 | 77.81 ± 0.41 | 77.52 ± 0.27 | -0.29 | +0.21 |
| arabertv02_twitter | dev | Qwen3 | 77.31 ± 0.26 | 77.85 ± 0.67 | 77.90 ± 0.92 | +0.05 | +0.59 |
| arabertv02_twitter | dev | Aya | 77.31 ± 0.26 | 77.49 ± 0.95 | 76.92 ± 0.84 | -0.57 | -0.39 |
| arabertv02_twitter | test | Fanar | 63.78 ± 0.28 | 63.82 ± 0.36 | 63.96 ± 0.38 | +0.14 | +0.18 |
| arabertv02_twitter | test | Qwen3 | 63.78 ± 0.28 | 63.88 ± 0.39 | 63.72 ± 0.27 | -0.16 | -0.06 |
| arabertv02_twitter | test | Aya | 63.78 ± 0.28 | 63.63 ± 0.54 | 63.74 ± 0.50 | +0.11 | -0.04 |
| camelbert_mix | dev | Fanar | 76.67 ± 0.32 | 75.71 ± 0.77 | 75.65 ± 0.08 | -0.06 | -1.02 |
| camelbert_mix | dev | Qwen3 | 76.67 ± 0.32 | 76.50 ± 1.16 | 76.82 ± 0.93 | +0.32 | +0.15 |
| camelbert_mix | dev | Aya | 76.67 ± 0.32 | 75.62 ± 0.50 | 75.72 ± 0.76 | +0.10 | -0.95 |
| camelbert_mix | test | Fanar | 61.70 ± 0.14 | 61.71 ± 0.35 | 61.24 ± 0.56 | -0.47 | -0.46 |
| camelbert_mix | test | Qwen3 | 61.70 ± 0.14 | 61.56 ± 0.63 | 61.80 ± 0.47 | +0.24 | +0.10 |
| camelbert_mix | test | Aya | 61.70 ± 0.14 | 61.45 ± 0.51 | 61.21 ± 0.49 | -0.24 | -0.49 |
| camelbert_da | dev | Fanar | 74.90 ± 0.19 | 74.28 ± 0.29 | 74.16 ± 0.12 | -0.12 | -0.74 |
| camelbert_da | dev | Qwen3 | 74.90 ± 0.19 | 74.45 ± 0.21 | 74.91 ± 0.61 | +0.46 | +0.01 |
| camelbert_da | dev | Aya | 74.90 ± 0.19 | 74.23 ± 0.82 | 73.75 ± 0.29 | -0.48 | -1.15 |
| camelbert_da | test | Fanar | 62.00 ± 0.84 | 62.07 ± 0.69 | 62.05 ± 0.43 | -0.02 | +0.05 |
| camelbert_da | test | Qwen3 | 62.00 ± 0.84 | 62.11 ± 0.56 | 62.03 ± 0.41 | -0.08 | +0.03 |
| camelbert_da | test | Aya | 62.00 ± 0.84 | 61.87 ± 0.49 | 61.57 ± 0.23 | -0.30 | -0.43 |
| arbert | dev | Fanar | 76.16 ± 0.27 | 76.92 ± 0.43 | 75.99 ± 0.46 | -0.93 | -0.17 |
| arbert | dev | Qwen3 | 76.16 ± 0.27 | 76.29 ± 0.35 | 76.64 ± 0.29 | +0.35 | +0.48 |
| arbert | dev | Aya | 76.16 ± 0.27 | 75.88 ± 0.29 | 75.79 ± 0.87 | -0.09 | -0.37 |
| arbert | test | Fanar | 62.78 ± 0.02 | 62.88 ± 0.49 | 62.30 ± 0.56 | -0.58 | -0.48 |
| arbert | test | Qwen3 | 62.78 ± 0.02 | 63.04 ± 0.48 | 63.56 ± 0.38 | +0.52 | +0.78 |
| arbert | test | Aya | 62.78 ± 0.02 | 62.53 ± 0.15 | 62.76 ± 0.95 | +0.23 | -0.02 |
| arbertv2 | dev | Fanar | 75.56 ± 0.46 | 76.06 ± 0.04 | 76.06 ± 0.30 | +0.00 | +0.50 |
| arbertv2 | dev | Qwen3 | 75.56 ± 0.46 | 75.72 ± 0.20 | 75.82 ± 0.30 | +0.10 | +0.26 |
| arbertv2 | dev | Aya | 75.56 ± 0.46 | 75.64 ± 0.45 | 75.63 ± 0.47 | -0.01 | +0.07 |
| arbertv2 | test | Fanar | 61.10 ± 1.22 | 63.26 ± 1.26 | 62.55 ± 0.66 | -0.71 | +1.45 |
| arbertv2 | test | Qwen3 | 61.10 ± 1.22 | 63.25 ± 0.47 | 63.43 ± 1.04 | +0.18 | +2.33 |
| arbertv2 | test | Aya | 61.10 ± 1.22 | 62.44 ± 0.71 | 62.80 ± 0.09 | +0.36 | +1.70 |

Mean of the 7 BERTs (each a 3-seed mean):

| Metric | SR01 | SR02 Fanar | SR04 Fanar | SR02 Qwen3 | SR04 Qwen3 | SR02 Aya | SR04 Aya |
|---|---|---|---|---|---|---|---|
| Dev macro F1 | 76.81 | 76.91 | 76.71 | 76.76 | 77.06 | 76.58 | 76.40 |
| Dev F1-PN | 75.52 | 75.42 | 75.26 | 75.47 | 75.68 | 75.13 | 74.83 |
| Dev F1 NEG | 79.53 | 79.64 | 79.30 | 79.48 | 79.68 | 78.93 | 79.01 |
| Dev F1 NEU | 79.41 | 79.92 | 79.59 | 79.33 | 79.81 | 79.47 | 79.51 |
| Dev F1 POS | 71.50 | 71.20 | 71.22 | 71.47 | 71.67 | 71.33 | 70.66 |
| Test macro F1 | 62.92 | 63.40 | 62.93 | 63.22 | 63.39 | 62.93 | 63.01 |
| Test F1-PN | 70.84 | 70.90 | 70.31 | 70.79 | 71.15 | 70.42 | 70.51 |
| Test F1 NEG | 77.60 | 77.37 | 76.98 | 77.45 | 77.54 | 76.73 | 76.76 |
| Test F1 NEU | 47.09 | 48.42 | 48.18 | 48.08 | 47.88 | 47.94 | 48.01 |
| Test F1 POS | 64.08 | 64.41 | 63.64 | 64.15 | 64.77 | 64.11 | 64.26 |


**Takeaway (SR):**
- No results better then previous runs more than noise

**Takeaway (SG):**
- Fidelity and Topic Spread (18) was good and better than the Human Data. MTLD, Vendi and Topic Spread (30) were less
- they are not the issue, the Generated dataset needs to train the model on examples similar to the ones it failed on. similar grammatical structure, topic or scentence structure. 
- hard cases that the model failed can possibly be grouped by E5 as it groups on many things not just topic, so if we can generate from that cluster but correctly labelled which is another task
- another method is to directly invoke these groups but the LLM will know what this group represents because i will be telling it
- i could do the E5 method but the distillNusaBERT method for labelling

**Future runs (SR):**
- relabel to strengthen labels? mayeb thats the issue?
- too easy tweets. i may need niche topics or more linguistic tweets

**Future runs (SG):**
- to add the topics (books and reading, films and TV series, travel and hotels, women and society, weather) and find tweets/texts for them to create a cluster for them
- Methods to generate for hard cases
  - find clustering for the hard cases in E5. If distinction clear then generate from these clusters  
    - Label using distillNusaBERT method for labelling
    - Annotate a few samples by hand and let claude continue the rest
  - Go through the hard cases myself and invoke the LLM to generate for these hard classes if that makes the LLM label them easier if i give it the topic of what these cases look like


## SG03
**Why**: Open Synthetic data doesnt help we need few shot.

**Thought Process**: 
- i wanted to give the shots to focus on the examples, phenomenons or scentence types that create more errors. 
- **issues**: 
  - as per the annotation guidelines, News should be NEU, but many annotators have chosen POS or NEG based on the news itself not on the writers emotion, which is wrong.
  
| Type | Tweets | NEG | NEU | POS |
  |---|---|---|---|---|
  | Bad-news headline | 468 | 36% | 60% | 4% |
  | Good-news headline | 158 | 4% | 67% | 29% |
- i then went through all the cases that all the models got wrong (63) `@data/inspect/hard_cases/sr02_dev_hard_cases.md` and classified them into groups (Complaint, Lyric/praise, Lyric/sadness, Fan/ad post)
- wrote the opposing pair by changing only the part that decides the sentiment. 

- so this is how i constructed the prompt
  | Pair type | Tweet A → Tweet B | Pairs | What the model had to learn |
  |---|---|---|---|
  | Bad-news headline | NEU → NEG | 250 | A report is neutral; the writer's own anger makes it NEG |
  | Good-news headline | NEU → POS | 250 | A report is neutral; the writer's own joy makes it POS |
  | **Short dialect complaint** | NEG → NEU | **500** | A short dialect tweet with a complaint word isn't always NEG; some are neutral remarks |
  | Quoted lyric, praise | NEU → POS | 250 | Quoting a song is neutral; the writer's own praise makes it POS |
  | Quoted lyric, sadness | NEU → NEG | 250 | Quoting a song is neutral; the writer's own sadness makes it NEG |
  | **Fan / ad post** | POS → NEU | **500** | Hearts and hashtags on a promo or fan post don't always mean POS |
  - we also followed the annotation guidelines of the majority not of on the guidelines. 

**Dataset quality metrics (SQ04)**

Topic spread on the frozen universal list `universal_clean_k50_seed0` (50 E5 clusters, 18 named topics, D-019), as for SG02. Effective topics = exp(entropy), mean ± std over 10 samples of 800 texts. Distance to real = Jensen-Shannon divergence (base 2) between the set's topic shares (18 named topics + unnamed) and S1 real train. Source `results/quality/sentiment/universal_topics_sg03.json`.

| Set | Effective clusters (of 50) | Effective named topics (of 18) | Unnamed | Distance to real | War | Politics | News | Religion | Greetings | Love | Films, TV, music |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 real train | 15.6 ± 0.7 | 6.5 ± 0.5 | 19% | 0.000 | 38% | 6% | 7% | 3% | 3% | 4% | 7% |
| SG03 Fanar | 14.8 ± 0.5 | 8.0 ± 0.2 | 27% | 0.255 | 1% | 2% | 17% | 1% | 2% | 15% | 19% |
| SG03-random Fanar | 19.7 ± 0.6 | 11.4 ± 0.4 | 19% | 0.147 | 7% | 18% | 8% | 4% | 2% | 6% | 12% |
| SG03 Qwen3 | 11.2 ± 0.3 | 6.5 ± 0.2 | 35% | 0.300 | 1% | 1% | 18% | 0% | 0% | 20% | 12% |
| SG03-random Qwen3 | 19.5 ± 0.7 | 9.2 ± 0.3 | 31% | 0.130 | 10% | 8% | 7% | 2% | 1% | 18% | 6% |
| SG03 Aya | 16.2 ± 0.7 | 8.6 ± 0.3 | 19% | 0.233 | 3% | 5% | 15% | 0% | 2% | 14% | 21% |
| SG03-random Aya | 21.6 ± 0.5 | 12.4 ± 0.4 | 25% | 0.110 | 10% | 10% | 8% | 4% | 3% | 7% | 9% |

Fidelity = share of texts whose requested label the SR01 MARBERT ensemble agrees with (real: accuracy on S1 dev). Imbalance over the requested variety × sentiment cells only. Source `results/quality/sentiment/{sg03,sg03r}_quality.json`; all sets in `tables/dataset_quality.md`.

| Set | Fidelity | Fidelity NEG / NEU / POS | MTLD | Vendi | Topic spread (of 30) | Effective universal topics (of 18) | Distance to real | MSA share | Dialectness | Repeats | Imbalance |
|---|---|---|---|---|---|---|---|---|---|---|---|
| S1 real (reference) | 80.3% | 85% / 79% / 75% | 2518 | 4.01 | 29 | 6.5 | 0.000 | 22.4% | 0.54 | 1.0% | 37.7 : 1 |
| SG03 Fanar | 73.9% | 91% / 59% / 87% | 1865 | 3.83 | 18 | 8.0 | 0.255 | 31.0% | 0.46 | 0.0% | 4.3 : 1 |
| SG03-random Fanar | 68.8% | 87% / 48% / 91% | 2817 | 3.76 | 19 | 11.4 | 0.147 | 28.9% | 0.46 | 0.0% | 4.1 : 1 |
| SG03 Qwen3 | 68.5% | 78% / 56% / 84% | 989 | 3.94 | 18 | 6.5 | 0.300 | 24.7% | 0.51 | 5.0% | 4.1 : 1 |
| SG03-random Qwen3 | 55.9% | 65% / 46% / 67% | 1496 | 3.98 | 22 | 9.2 | 0.130 | 9.8% | 0.66 | 8.1% | 3.9 : 1 |
| SG03 Aya | 77.7% | 98% / 58% / 97% | 1435 | 3.63 | 16 | 8.6 | 0.233 | 23.8% | 0.53 | 1.1% | 4.0 : 1 |
| SG03-random Aya | 65.1% | 92% / 39% / 91% | 2162 | 3.50 | 17 | 12.4 | 0.110 | 11.0% | 0.61 | 0.0% | 4.0 : 1 |

SG03 changes four things besides the targeting: quantity (from 11,208 to 15,208 texts), source (LLM-written instead of human), format (minimal pairs instead of single tweets) and label mix (50% NEU). I built SG03-random to keep all four the same and remove only the targeting, so the comparison is fair and tests only the targeting.

## SR05 + SG03
Macro F1, mean ± std over seeds 42/43/44. Source `tables/sentiment_summary.csv`. Columns = the generator of the SG03 set.

**Performance**

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 78.68 ± 0.44 | 78.40 ± 0.54 | 78.95 ± 0.12 | 63.82 ± 0.57 | 63.85 ± 0.73 | 64.05 ± 0.68 |
| MARBERT | 78.58 ± 0.93 | 78.17 ± 0.78 | 78.53 ± 0.74 | 64.43 ± 0.72 | 63.50 ± 0.70 | 64.79 ± 1.09 |
| AraBERTv02-Tw | 77.99 ± 0.55 | 77.59 ± 0.58 | 77.37 ± 0.47 | 62.89 ± 0.50 | 62.65 ± 0.46 | 62.91 ± 0.55 |
| CAMeLBERT-mix | 76.55 ± 0.56 | 75.42 ± 0.83 | 75.63 ± 0.76 | 61.37 ± 0.86 | 61.14 ± 0.83 | 61.08 ± 0.27 |
| CAMeLBERT-DA | 74.08 ± 0.52 | 73.88 ± 0.39 | 74.47 ± 0.32 | 60.88 ± 0.32 | 60.57 ± 0.74 | 60.48 ± 0.48 |
| ARBERT | 76.27 ± 0.55 | 75.13 ± 0.56 | 76.41 ± 0.46 | 61.48 ± 0.53 | 62.30 ± 0.88 | 61.73 ± 0.93 |
| ARBERTv2 | 75.03 ± 0.10 | 74.98 ± 0.33 | 75.22 ± 0.53 | 60.99 ± 0.14 | 61.42 ± 0.40 | 61.22 ± 0.40 |
| **Mean** | **76.74** | **76.22** | **76.65** | **62.27** | **62.20** | **62.32** |

**Δ SR05 − SR04** (SG03 vs SG02, same BERT and generator; + = SG03 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.42 | -0.11 | +0.45 | +0.19 | -1.07 | -0.03 |
| MARBERT | +0.12 | -0.62 | +0.07 | -0.35 | -0.78 | -0.11 |
| AraBERTv02-Tw | +0.47 | -0.31 | +0.45 | -1.07 | -1.07 | -0.83 |
| CAMeLBERT-mix | +0.90 | -1.40 | -0.09 | +0.13 | -0.66 | -0.13 |
| CAMeLBERT-DA | -0.08 | -1.03 | +0.72 | -1.17 | -1.46 | -1.09 |
| ARBERT | +0.28 | -1.51 | +0.62 | -0.82 | -1.26 | -1.03 |
| ARBERTv2 | -1.03 | -0.84 | -0.41 | -1.56 | -2.01 | -1.58 |
| **Mean** | **+0.03** | **-0.83** | **+0.26** | **-0.66** | **-1.19** | **-0.69** |
| Better in | 4/7 | 0/7 | 5/7 | 2/7 | 0/7 | 0/7 |

## SR06 + SG03-random
Same layout as SR05.

**Performance**

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 78.12 ± 0.32 | 77.78 ± 0.34 | 78.04 ± 0.68 | 64.25 ± 0.19 | 63.95 ± 0.57 | 63.39 ± 0.53 |
| MARBERT | 78.69 ± 0.16 | 77.95 ± 1.03 | 78.50 ± 0.27 | 64.00 ± 0.63 | 64.70 ± 0.75 | 64.50 ± 0.20 |
| AraBERTv02-Tw | 77.03 ± 0.49 | 77.03 ± 0.52 | 76.96 ± 0.34 | 63.78 ± 0.59 | 63.44 ± 0.27 | 62.85 ± 0.34 |
| CAMeLBERT-mix | 74.75 ± 0.43 | 75.19 ± 0.19 | 74.27 ± 0.55 | 61.25 ± 0.06 | 61.03 ± 0.61 | 60.85 ± 0.80 |
| CAMeLBERT-DA | 73.64 ± 0.34 | 73.92 ± 0.19 | 73.52 ± 0.26 | 61.62 ± 0.40 | 61.21 ± 1.72 | 60.24 ± 0.72 |
| ARBERT | 75.80 ± 0.52 | 74.62 ± 0.38 | 75.53 ± 0.32 | 61.68 ± 1.18 | 61.49 ± 0.81 | 61.31 ± 1.03 |
| ARBERTv2 | 75.48 ± 0.47 | 74.64 ± 0.54 | 75.13 ± 0.93 | 62.43 ± 0.59 | 61.70 ± 0.31 | 61.25 ± 0.28 |
| **Mean** | **76.22** | **75.88** | **75.99** | **62.72** | **62.50** | **62.06** |

**Δ SR05 − SR06** (SG03 vs its size-matched control; + = SG03 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | +0.56 | +0.62 | +0.91 | -0.43 | -0.10 | +0.66 |
| MARBERT | -0.11 | +0.22 | +0.03 | +0.43 | -1.20 | +0.29 |
| AraBERTv02-Tw | +0.96 | +0.56 | +0.41 | -0.89 | -0.79 | +0.06 |
| CAMeLBERT-mix | +1.80 | +0.23 | +1.36 | +0.12 | +0.11 | +0.23 |
| CAMeLBERT-DA | +0.44 | -0.04 | +0.95 | -0.74 | -0.64 | +0.24 |
| ARBERT | +0.47 | +0.51 | +0.88 | -0.20 | +0.81 | +0.42 |
| ARBERTv2 | -0.45 | +0.34 | +0.09 | -1.44 | -0.28 | -0.03 |
| **Mean** | **+0.52** | **+0.35** | **+0.66** | **-0.45** | **-0.30** | **+0.27** |
| Better in | 5/7 | 6/7 | 7/7 | 2/7 | 2/7 | 6/7 |

**Takeaways**
- Qwen3's SG03 set is the weakest
- Aya's SG03 is the only set that beats its control on test

| Comparison | Test | Dev |
|---|---|---|
| SR06 (control) vs real-only | −0.50 | −0.79 |
| SR05 (targeted) vs control | −0.16 (not significant, better in 10/21) | **+0.51 (better in 18/21)** |

1. **The loss isn't caused by the targeting.** The untargeted control loses almost as much (−0.50). The loss comes from what both sets share: the LLM source, the pair format and the label mix.
2. **Targeting does have an effect, but only on dev.** On dev, the targeted pairs beat the control in 18 of 21 cells. On test there's no difference. Dev and train come from the same distribution, while test is different (SA-E01), so what targeting teaches doesn't carry over to test.
3. **Test had no change beyond noise** because the classes that we targeted dont exist heavily in the test, they exist mostly in the dev. Dev and Test are not balanced

**Future Runs**
- Repeat the run but get the errors from the test. 

## SG04
Test Set
| Type | Tweets |
|---|---|
| 1. Sarcastic praise (NEG → POS) | 141 |
| 2. Dry sarcastic jab (NEG → NEU) | 162 |
| 3. Maxim / reflection (NEU → NEG) | 194 |
| 4. Prayer / verse / greeting (NEU → POS) | 13 |
| 5. Election / promo hashtag (NEU → POS) | 26 |
| 6. Crying / laughing emoji | 47 |

These are the errors from test where at least 32/63 runs classified them wrong classified into groups.
This generation will focus on the errors from test instead of dev because in ArSarcasm-V2 the errors in dev almost dont exist in test, because test and dev are not equally balanced. This could be considered cheating the model, but how else will we generate data for the models weakness.

Your labels are saved in [sg04_review_ammar.csv](data/inspect/hard_cases/sg04_review_ammar.csv). The test gold labels are not changed.




| Type | Change | Pairs |
|---|---|---|
| 1. Sarcastic praise, POS → NEG | Keep. The task text says sincere praise or encouragement stays POS. | 500 |
| 2. Dry sarcastic jab, NEU → NEG | Keep. Merge in the reproach / disapproval tweets from type 3 (3.5, 3.10, 3.24): disapproval without negative words is NEG. | 600 |
| 3. Maxim / reflection | Narrow to real general sayings (لهفة البدايات ليست حبّ…), which stay NEU. Pair: saying NEU ↔ the writer's own sad or happy use of it, NEG / POS. | 400 |
| 4. Prayer / verse, NEU → POS | Keep. Only 13 test tweets, so it stays small. | 200 |
| 5. Spam hashtag | Drop. | 0 |
| 6. 😭 / 😂💔 | Redefine as a context pair. The same emoji appears in both tweets, and only the context decides: POS (excitement) ↔ NEG (sadness). That turns your "depends on context" into what the pair teaches. | 300 |

| Type | Read | Gold label wrong | Share |
|---|---|---|---|
| 1. Sarcastic praise | 32 | 6 | 19% |
| 2. Dry sarcastic jab | 32 | 0 | 0% |
| 3. Maxim / reflection | 32 | 4 | 13% |
- So the example tweets in the prompts must use my label, not the gold one.

**Type 1: sarcastic praise (keep)**
- Tweet A: real praise, POS.
- Tweet B: the same praise, but sarcastic, NEG.
- What the model learns: nice words can be mockery.
- Change: the prompt says real praise or encouragement stays POS.
**Types 2 + 3: neutral remark vs a dig (merge into one type)**
- Tweet A: a plain remark or joke, NEU.
- Tweet B: the same remark, but with a real dig at someone, NEG.
- Why merge: both types make this same pair. Type 2 errors miss the dig, and type 3 errors see a dig that isn't there. One pair fixes both.

**Type 4: prayer or verse (keep, small)**
- Tweet A: a prayer or verse alone, NEU.
- Tweet B: the same prayer plus the writer's own joy or thanks, POS.
- What the model learns: religious words alone are not POS.

**Type 5: spam hashtags (drop)**
- These tweets can't be read, as you said.

**Type 6: 😭 and 😂💔 (redefine)**
- Both tweets use the same emoji.
- Tweet A: excitement (e.g. a fan seeing their idol), POS.
- Tweet B: real sadness, NEG.
- What the model learns: the emoji alone doesn't decide; the context does. That is your "depends on context".


## Size

| Type | Pairs |
|---|---|
| 1. Sarcastic praise | 500 |
| 2+3. Remark vs dig | 1,000 |
| 4. Prayer / verse | 200 |
| 6. Emoji in context | 300 |
| **Total** | **2,000** (4,000 tweets, same as SG03) |

- Sentiment split: NEG 1,800, NEU 1,200, POS 1,000.
- This leans NEG, like the test set.
- Keep a Fidelity at a minimum of 80% (generation repeats until each set reaches 80%.) using That is judge-based filtering with a set-level target. It ranks pairs by how many sides an external judge (the SR01 MARBERT ensemble) confirms. It then keeps generating until set reaches 80% agreement.


**Dataset quality** (source `tables/dataset_quality.md`; fidelity = SR01 MARBERT judge, which SG04 was also selected by, so its ≥ 80% holds by construction)

| Dataset | Texts | Imbalance | MSA share | Dialectness | MTLD | Topics (of 30) | Universal clusters (of 50) | Vendi | Repeats | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 real (train) | 11,171 | 37.7 : 1 | 22.4% | 0.54 | 2518 | 29 | 15.6 | 4.0 | 1.0% | 80.3% (85% / 79% / 75%) |
| SG03 Fanar | 4,000 | 4.3 : 1 | 31.0% | 0.46 | 1865 | 18 | 14.8 | 3.8 | 0.0% | 73.9% (91% / 59% / 87%) |
| SG03 Qwen3 | 4,000 | 4.1 : 1 | 24.7% | 0.51 | 989 | 18 | 11.2 | 3.9 | 5.0% | 68.5% (78% / 56% / 84%) |
| SG03 Aya | 4,000 | 4.0 : 1 | 23.8% | 0.53 | 1435 | 16 | 16.2 | 3.6 | 1.1% | 77.7% (98% / 58% / 97%) |
| SG04 (test-contaminated) Fanar | 4,000 | 2.4 : 1 | 22.6% | 0.51 | 1749 | 12 | 20.9 | 3.5 | 0.0% | 81.3% (90% / 53% / 99%) |
| SG04 (test-contaminated) Qwen3 | 4,000 | 3.2 : 1 | 25.8% | 0.49 | 901 | 9 | 18.6 | 3.5 | 3.0% | 80.7% (80% / 72% / 91%) |
| SG04 (test-contaminated) Aya | 4,000 | 2.6 : 1 | 18.8% | 0.58 | 1159 | 10 | 17.8 | 3.1 | 0.4% | 82.4% (98% / 44% / 100%) |

- Fidelity per type after selection (`results/filtering/sg04_<gen>.selection.json`):

| Type | Fanar | Qwen3 | Aya |
|---|---|---|---|
| Sarcastic praise | 86.0% | 64.2% | 100% |
| Public jab | 91.2% | 93.9% | 83.3% |
| Personal remark | 68.0% | 81.8% | 66.4% |
| Prayer | 50.5% | 57.3% | 50.0% |
| Emoji in context | 100% | 100% | 100% |
| **Set** | **81.3%** (2.0× requests) | **80.7%** (3.0×) | **82.4%** (2.0×) |

- Prayer stays near 50% for every generator: the judge reads neutral prayers as POS (the error the type targets).
- Note: types 2 and 3 were finally kept as two types (public jab 500, personal remark 500), not merged.

## SG04 / SR07
**Performance** (macro F1, mean ± std over seeds 42/43/44; source `tables/sentiment_summary.csv`; columns = generator of the SG04 set)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 78.13 ± 0.50 | 77.87 ± 0.49 | 77.76 ± 0.20 | 62.49 ± 0.12 | 63.22 ± 1.13 | 63.57 ± 0.84 |
| MARBERT | 77.70 ± 0.36 | 78.37 ± 0.56 | 77.88 ± 0.35 | 63.36 ± 1.09 | 63.92 ± 0.76 | 63.98 ± 1.02 |
| AraBERTv02-Tw | 76.15 ± 0.54 | 76.03 ± 0.69 | 76.91 ± 0.37 | 61.62 ± 0.25 | 62.67 ± 0.96 | 62.24 ± 0.72 |
| CAMeLBERT-mix | 75.16 ± 0.27 | 74.83 ± 0.96 | 74.57 ± 0.38 | 60.33 ± 0.84 | 60.73 ± 0.66 | 60.24 ± 0.89 |
| CAMeLBERT-DA | 74.32 ± 0.30 | 73.50 ± 0.42 | 74.21 ± 0.73 | 60.32 ± 1.17 | 60.66 ± 0.44 | 60.09 ± 0.97 |
| ARBERT | 75.45 ± 0.80 | 75.16 ± 0.56 | 75.50 ± 0.65 | 60.32 ± 0.05 | 61.81 ± 0.26 | 60.82 ± 0.61 |
| ARBERTv2 | 74.72 ± 0.68 | 74.75 ± 0.66 | 74.45 ± 0.33 | 60.70 ± 1.08 | 61.26 ± 0.90 | 59.98 ± 0.41 |
| **Mean** | **75.95** | **75.79** | **75.90** | **61.31** | **62.04** | **61.56** |

**Comparison with previous runs**

**Δ SR07 − SR01 (SG04 vs real only, same BERT; + = SG04 better)**

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.29 | -0.55 | -0.66 | -1.46 | -0.73 | -0.38 |
| MARBERT | -0.98 | -0.31 | -0.80 | -1.78 | -1.22 | -1.16 |
| AraBERTv02-Tw | -1.16 | -1.28 | -0.40 | -2.16 | -1.11 | -1.54 |
| CAMeLBERT-mix | -1.51 | -1.84 | -2.10 | -1.37 | -0.97 | -1.46 |
| CAMeLBERT-DA | -0.58 | -1.40 | -0.69 | -1.68 | -1.34 | -1.91 |
| ARBERT | -0.71 | -1.00 | -0.66 | -2.46 | -0.97 | -1.96 |
| ARBERTv2 | -0.84 | -0.81 | -1.11 | -0.40 | +0.16 | -1.12 |
| **Mean** | **-0.87** | **-1.03** | **-0.92** | **-1.62** | **-0.88** | **-1.36** |
| Better in | 0/7 | 0/7 | 0/7 | 0/7 | 1/7 | 0/7 |

**Δ SR07 − SR05 (SG04 vs SG03, same BERT and generator; + = SG04 better)**

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.55 | -0.53 | -1.19 | -1.33 | -0.63 | -0.48 |
| MARBERT | -0.88 | +0.20 | -0.65 | -1.07 | +0.42 | -0.81 |
| AraBERTv02-Tw | -1.84 | -1.56 | -0.46 | -1.27 | +0.02 | -0.67 |
| CAMeLBERT-mix | -1.39 | -0.59 | -1.06 | -1.04 | -0.41 | -0.84 |
| CAMeLBERT-DA | +0.24 | -0.38 | -0.26 | -0.56 | +0.09 | -0.39 |
| ARBERT | -0.82 | +0.03 | -0.91 | -1.16 | -0.49 | -0.91 |
| ARBERTv2 | -0.31 | -0.23 | -0.77 | -0.29 | -0.16 | -1.24 |
| **Mean** | **-0.79** | **-0.44** | **-0.76** | **-0.96** | **-0.17** | **-0.76** |
| Better in | 1/7 | 2/7 | 0/7 | 0/7 | 3/7 | 0/7 |

**Δ SR07 − SR06 (SG04 vs SG03-random, same BERT and generator; + = SG04 better)**

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | +0.01 | +0.09 | -0.28 | -1.76 | -0.73 | +0.18 |
| MARBERT | -0.99 | +0.42 | -0.62 | -0.64 | -0.78 | -0.52 |
| AraBERTv02-Tw | -0.88 | -1.00 | -0.05 | -2.16 | -0.77 | -0.61 |
| CAMeLBERT-mix | +0.41 | -0.36 | +0.30 | -0.92 | -0.30 | -0.61 |
| CAMeLBERT-DA | +0.68 | -0.42 | +0.69 | -1.30 | -0.55 | -0.15 |
| ARBERT | -0.35 | +0.54 | -0.03 | -1.36 | +0.32 | -0.49 |
| ARBERTv2 | -0.76 | +0.11 | -0.68 | -1.73 | -0.44 | -1.27 |
| **Mean** | **-0.27** | **-0.09** | **-0.10** | **-1.41** | **-0.46** | **-0.50** |
| Better in | 3/7 | 4/7 | 2/7 | 0/7 | 1/7 | 1/7 |

**Summary over the 21 BERT × generator cells** (sign test, two-sided)

| Comparison | Dev | Test |
|---|---|---|
| SR07 − SR01 (real only) | -0.94 (better in 0/21, p = 0.000) | -1.29 (better in 1/21, p = 0.000) |
| SR07 − SR05 (SG03) | -0.66 (better in 3/21, p = 0.001) | -0.63 (better in 3/21, p = 0.001) |
| SR07 − SR06 (SG03-random) | -0.15 (better in 9/21, p = 0.664) | -0.79 (better in 2/21, p = 0.000) |

- SR01 has one value per BERT, so in SR07 − SR01 the three generator cells of a BERT share the same baseline; the 21 cells are not independent.


**Where the errors come from: hard cases or not**

Error rate = share of the subset's test tweets a run gets wrong; mean over seeds per BERT × generator cell, then over cells (SR01: 7 cells, others: 21). Subsets from `data/inspect/hard_cases/` (candidate lists are rough keyword rules).

| Test subset | Tweets | SR01 real | SR05 + SG03 | SR07 + SG04 | SR07 − SR01 |
|---|---|---|---|---|---|
| Hard cases (SG04 built from these) | 917 | 82.6% | 82.4% | 79.9% | −2.7 |
| Other test tweets | 2,083 | 9.9% | 10.8% | 12.2% | +2.4 |
| Type 1 candidates: sarcastic praise | 141 | 82.4% | 79.8% | 76.4% | −6.1 |
| Type 2 candidates: dry jab | 162 | 67.8% | 71.6% | 63.5% | −4.3 |
| Type 3 candidates: maxim / remark | 194 | 93.6% | 91.9% | 91.5% | −2.1 |
| Type 4 candidates: prayer | 13 | 92.7% | 95.1% | 73.9% | −18.8 |
| Type 5 candidates: spam hashtag (not generated) | 26 | 91.2% | 92.0% | 90.9% | −0.3 |
| Type 6 candidates: emoji | 47 | 87.7% | 84.1% | 87.2% | −0.6 |


### Which labels the classifiers predict

| | NEG | NEU | POS |
|---|---|---|---|
| Gold labels (test) | 55.9% | 24.9% | 19.2% |
| SR01 (real only) | 54.9% | 18.6% | 26.5% |
| SR05 (+ SG03) | 54.6% | 20.0% | 25.4% |
| SR07 (+ SG04) | 56.2% | 19.7% | 24.1% |


### Error rate by gold label and sarcasm

| Group | Tweets | SR01 | SR07 | Change |
|---|---|---|---|---|
| Gold POS | 575 | 23.8% | 30.2% | **+6.4** |
| Gold NEU | 748 | 58.8% | 59.3% | +0.5 |
| Gold NEG | 1,677 | 23.1% | 22.1% | −1.0 |
| Hard cases, gold NEG | 371 | 76.1% | 71.2% | −4.9 |
| Sarcastic | 821 | 24.0% | 23.5% | −0.5 |
| Not sarcastic | 2,179 | 35.2% | 36.5% | +1.3 |


### What kind of mistakes grow on the ordinary tweets

| Error (gold → predicted) | Change vs SR01 |
|---|---|
| POS → NEU | **+1.37** |
| NEG → NEU | +0.58 |
| NEU → NEG | +0.52 |
| NEG → POS | −0.48 |



### Tweets that flip from SR01 to SR07

Per tweet, the majority label over all runs of a condition.

| | Tweets | Of which |
|---|---|---|
| Fixed (wrong in SR01, right in SR07) | 109 | 76 hard cases |
| Broken (right in SR01, wrong in SR07) | 119 | 36 hard cases |
| Net | −10 | |

| Broken as (gold → SR07) | Tweets |
|---|---|
| NEG → NEU | 33 |
| POS → NEU | 32 |
| NEU → NEG | 28 |
| NEU → POS | 9 |
| POS → NEG | 9 |
| NEG → POS | 8 |

- About 230 tweets (8% of test) change their answer, for a net of −10: SG04 trades one set of errors for another rather than adding knowledge.
- Most broken tweets become NEU (65 of 119).

### Fidelity vs usefulness

| Generator | Fidelity | Test macro F1 |
|---|---|---|
| Fanar | 81.3% | 61.30 |
| Qwen3 | 80.7% | 62.04 |
| Aya | 82.4% | 61.56 |

- The lowest-fidelity set (Qwen3) trained the best classifiers, and the highest (Aya) did not; with three sets this is a hint, not a result.
- Prayer fidelity is about 50% by design: the judge reads neutral prayers as POS, which is the error the type targets. So for that type a high fidelity would mean the pairs failed.

**Take awawys**
- improvement but need to generate more data, and more targeted on the normal cases so that the model doesnt overtrain on hard
- a 2.4% rise in error on other test tweets was enough to reverse and make our progress look bad
**Where the errors come from**
- SG04 fixes some of the hard cases: about 25 tweets (2.7% of 917), most clearly prayer (−18.8) and sarcastic praise (−6.1). SG03 barely moved them (−0.2).
- It breaks more of the ordinary tweets: about 50 tweets (2.4% of 2,083). SG03 did the same, but less (+0.9).
- So the net test score falls: the loss on the easy tweets outweighs the gain on the hard ones.
**Which labels the classifiers predict**
- SG04 makes the classifiers predict POS less often (26.5% → 24.1%) real is (19.2%). score still falls because some of the dropped POS predictions were correct ones.
**What kind of mistakes grow from the ordinary tweets**
- The biggest new error is sincere positive tweets read as neutral. It is not specific to SG04: POS → NEU also grows with SG03 and SG03-random (32 broken tweets here, 18 and 28 there). NEG → NEU is the same (33 here, 28 and 41 there).
- The one error that shrinks is negative tweets read as positive (−0.48 points). That fits the sarcastic-praise lesson, but the change is small and SG03 shrinks it too (−0.20).
- **SG04's own new error is NEU → NEG:** 28 broken tweets, against 10 with SG03 and 11 with SG03-random. They are mostly dry remarks and ironic questions, so the public-jab lesson seems over-applied. Some read like real digs, so part of this may be wrong gold labels (not read yet).
- **Real POS tweets are where SG04 does the damage**, with 6.4 points more errors.
- The clearest measured cause is the prayer rule. Gold POS tweets with a religious cue go from 8.6% to 28.5% error (SG03 8.5%, SG03-random 10.0%), about 13 of the roughly 37 extra POS errors. SG04 taught "a prayer alone is NEU", but real prayers are mostly POS (train 161 POS / 70 NEU, test 65 / 19). It fixed about 3 NEU prayers and broke about 13 POS ones.
- Praise words and positive emoji on the NEG side of pairs may explain part of the rest. This is not tested.
- NEG improves, most clearly on the hard NEG tweets (−4.9). Sarcastic tweets improve slightly, while non-sarcastic ones get worse.
- The flip counts above are partly noise: two halves of the SR01 runs already disagree on 142 tweets (SR07 flips: 228). Only 41 of the 119 broken tweets are broken by all three generators.


**Future runs** 
- MUST find classification of `other test tweets`
- may try other methods, but so far this is workng great (are we cheating?)
- Need to keep the POS generations focused on the ones that were removed and the ones that made the loss when removed
- keep the same generations for weak classes but generate more for POS