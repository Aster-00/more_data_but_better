 ## Dataset for Sentiment Analysis (ArSarcasm-V2)
### Here are it's annotation guidelines
Positive (POS): Text whose overall feeling is positive. This includes congratulations, celebrations or occasions, wins or gains, and any event that brings good news or optimism.

e.g. a tweet saying Mohamed Salah deserves the best-player award.

Negative (NEG): Text that expresses something negative or sad, or reports bad news. Anger or strong emotional agitation also counts as negative.

e.g. an Egyptian-dialect tweet saying there’s zero excitement about the World Cup qualifiers.

Neutral (NEU): Text with neither positive nor negative expressions.

e.g. a question about how many qualifier matches someone played, or a news-style quote reported without the writer’s own sentiment.

## SR01 baseline run, real data only

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR01-jais2 | dev | `sr01_jais2` | 3 | 80.47 | 80.66 | 80.46 | 0.72 | 81.27 | 82.73 | 81.67 | 77.01 |
| SR01-jais2 | test | `sr01_jais2` | 3 | 67.02 | 67.22 | 67.94 | 0.95 | 71.74 | 80.81 | 51.59 | 68.66 |
| SR01-fanar | dev | `sr01_fanar` | 1 | 79.42 | 79.46 | 79.41 | – | 80.10 | 80.80 | 80.87 | 76.61 |
| SR01-fanar | test | `sr01_fanar` | 1 | 66.63 | 66.25 | 67.71 | – | 70.83 | 79.56 | 51.63 | 68.71 |
| SR01-aya | dev | `sr01_aya` | 3 | 79.36 | 80.20 | 78.84 | 1.06 | 80.20 | 81.22 | 80.94 | 75.92 |
| SR01-aya | test | `sr01_aya` | 3 | 65.72 | 65.67 | 67.05 | 0.60 | 69.86 | 78.58 | 51.09 | 67.49 |
| SR01-marbert | dev | `sr01_marbert` | 3 | 78.68 | 78.79 | 78.79 | 1.14 | 79.64 | 81.42 | 80.10 | 74.53 |
| SR01-marbert | test | `sr01_marbert` | 3 | 65.14 | 65.05 | 66.50 | 0.15 | 69.96 | 79.46 | 48.35 | 67.61 |
| SR01-marbertv2 | dev | `sr01_marbertv2` | 3 | 78.42 | 78.35 | 78.67 | 0.52 | 79.61 | 81.46 | 80.53 | 73.28 |
| SR01-marbertv2 | test | `sr01_marbertv2` | 3 | 63.95 | 63.81 | 66.06 | 0.41 | 68.78 | 78.50 | 47.50 | 65.86 |
| SR01-falcon_h1 | dev | `sr01_falcon_h1` | 1 | 77.93 | 77.72 | 78.16 | – | 79.21 | 80.79 | 80.60 | 72.40 |
| SR01-falcon_h1 | test | `sr01_falcon_h1` | 1 | 63.31 | 63.20 | 65.77 | – | 67.80 | 76.97 | 48.13 | 64.84 |
| SR01-qwen3 | dev | `sr01_qwen3` | 1 | 77.82 | 78.32 | 77.46 | – | 79.29 | 80.59 | 80.92 | 71.94 |
| SR01-qwen3 | test | `sr01_qwen3` | 1 | 63.92 | 63.80 | 65.02 | – | 68.60 | 77.89 | 49.78 | 64.10 |
| SR01-arabertv02_twitter | dev | `sr01_arabertv02_twitter` | 3 | 77.31 | 77.24 | 77.42 | 0.17 | 78.49 | 79.79 | 79.81 | 72.32 |
| SR01-arabertv02_twitter | test | `sr01_arabertv02_twitter` | 3 | 63.78 | 63.69 | 65.76 | 0.48 | 68.51 | 77.91 | 48.18 | 65.25 |
| SR01-camelbert_mix | dev | `sr01_camelbert_mix` | 3 | 76.67 | 76.79 | 76.63 | 0.14 | 77.85 | 79.28 | 78.98 | 71.76 |
| SR01-camelbert_mix | test | `sr01_camelbert_mix` | 3 | 61.70 | 61.88 | 63.20 | 0.59 | 66.92 | 76.84 | 46.02 | 62.24 |
| SR01-camelbert_da | dev | `sr01_camelbert_da` | 3 | 74.90 | 74.78 | 75.04 | 0.20 | 75.95 | 75.80 | 78.03 | 70.88 |
| SR01-camelbert_da | test | `sr01_camelbert_da` | 3 | 62.00 | 62.17 | 63.43 | 0.61 | 67.24 | 77.20 | 46.02 | 62.78 |
| SR01-arbert | dev | `sr01_arbert` | 3 | 76.16 | 75.76 | 76.81 | 0.61 | 77.69 | 79.94 | 79.19 | 69.36 |
| SR01-arbert | test | `sr01_arbert` | 3 | 62.78 | 62.75 | 64.47 | 0.36 | 67.53 | 77.18 | 48.79 | 62.36 |
| SR01-arbertv2 | dev | `sr01_arbertv2` | 3 | 75.56 | 74.81 | 76.85 | 0.16 | 77.07 | 79.05 | 79.23 | 68.39 |
| SR01-arbertv2 | test | `sr01_arbertv2` | 3 | 61.10 | 61.92 | 64.05 | 0.84 | 66.23 | 76.13 | 44.74 | 62.43 |

## Sr02 
which is a run that uses SG01, which is a run that uses 0 shot prompting and generates 500 for every sentiment in every dialect.

| id | split | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|
| SR02-marbertv2_fanar | dev | 3 | 79.27 | 78.96 | 79.81 | 1.30 | 80.36 | 82.63 | 80.85 | 74.34 |
| SR02-marbertv2_fanar | test | 3 | 64.45 | 63.89 | 66.52 | 0.15 | 68.84 | 78.45 | 48.62 | 66.28 |
| SR02-marbertv2_qwen3 | dev | 3 | 78.28 | 77.71 | 79.06 | 0.65 | 79.35 | 81.35 | 80.08 | 73.42 |
| SR02-marbertv2_qwen3 | test | 3 | 64.08 | 63.44 | 66.31 | 0.57 | 68.38 | 77.87 | 48.63 | 65.73 |
| SR02-marbertv2_aya | dev | 3 | 78.99 | 78.64 | 79.42 | 0.48 | 80.18 | 82.05 | 81.17 | 73.76 |
| SR02-marbertv2_aya | test | 3 | 64.09 | 63.29 | 66.10 | 0.15 | 68.28 | 77.81 | 48.36 | 66.11 |
| SR02-marbert_fanar | dev | 3 | 78.35 | 78.64 | 78.24 | 1.19 | 79.43 | 80.80 | 80.37 | 73.90 |
| SR02-marbert_fanar | test | 3 | 65.62 | 65.69 | 66.81 | 0.72 | 70.36 | 79.48 | 48.98 | 68.40 |
| SR02-marbert_qwen3 | dev | 3 | 78.20 | 77.86 | 78.76 | 0.73 | 79.00 | 80.25 | 79.66 | 74.70 |
| SR02-marbert_qwen3 | test | 3 | 64.65 | 64.44 | 66.30 | 0.41 | 69.18 | 78.36 | 48.47 | 67.13 |
| SR02-marbert_aya | dev | 3 | 78.18 | 77.83 | 78.74 | 0.87 | 79.16 | 80.52 | 80.16 | 73.85 |
| SR02-marbert_aya | test | 3 | 64.48 | 63.72 | 66.20 | 0.08 | 68.53 | 77.78 | 48.73 | 66.94 |
| SR02-arabertv02_twitter_fanar | dev | 3 | 77.81 | 78.03 | 77.71 | 0.84 | 79.13 | 81.07 | 80.14 | 72.23 |
| SR02-arabertv02_twitter_fanar | test | 3 | 63.82 | 63.47 | 65.07 | 0.59 | 68.34 | 77.75 | 48.96 | 64.74 |
| SR02-arabertv02_twitter_qwen3 | dev | 3 | 77.85 | 78.17 | 77.62 | 0.95 | 79.21 | 80.78 | 80.52 | 72.26 |
| SR02-arabertv02_twitter_qwen3 | test | 3 | 63.88 | 63.38 | 65.25 | 0.79 | 68.27 | 77.63 | 49.35 | 64.65 |
| SR02-arabertv02_twitter_aya | dev | 3 | 77.49 | 77.86 | 77.22 | 1.42 | 78.73 | 79.95 | 80.08 | 72.43 |
| SR02-arabertv02_twitter_aya | test | 3 | 63.63 | 62.85 | 65.22 | 0.36 | 67.52 | 76.66 | 49.40 | 64.84 |
| SR02-camelbert_mix_fanar | dev | 3 | 75.71 | 76.01 | 75.61 | 1.10 | 77.10 | 77.84 | 79.01 | 70.29 |
| SR02-camelbert_mix_fanar | test | 3 | 61.71 | 62.11 | 62.70 | 1.38 | 66.88 | 76.63 | 46.18 | 62.33 |
| SR02-camelbert_mix_qwen3 | dev | 3 | 76.50 | 76.34 | 76.90 | 2.09 | 77.53 | 78.65 | 78.75 | 72.09 |
| SR02-camelbert_mix_qwen3 | test | 3 | 61.56 | 61.58 | 63.02 | 0.06 | 66.51 | 76.39 | 46.42 | 61.86 |
| SR02-camelbert_mix_aya | dev | 3 | 75.62 | 75.91 | 75.44 | 0.79 | 76.73 | 76.99 | 78.48 | 71.40 |
| SR02-camelbert_mix_aya | test | 3 | 61.45 | 61.10 | 62.88 | 0.26 | 66.16 | 75.99 | 46.70 | 61.65 |
| SR02-camelbert_da_fanar | dev | 3 | 74.28 | 74.28 | 74.43 | 0.99 | 75.66 | 75.33 | 78.41 | 69.11 |
| SR02-camelbert_da_fanar | test | 3 | 62.07 | 61.48 | 63.46 | 0.41 | 66.38 | 76.00 | 48.10 | 62.09 |
| SR02-camelbert_da_qwen3 | dev | 3 | 74.45 | 74.54 | 74.43 | 0.60 | 75.60 | 76.03 | 77.41 | 69.90 |
| SR02-camelbert_da_qwen3 | test | 3 | 62.11 | 61.89 | 62.98 | 0.43 | 67.04 | 77.00 | 46.80 | 62.52 |
| SR02-camelbert_da_aya | dev | 3 | 74.23 | 74.00 | 74.58 | 1.03 | 75.31 | 74.86 | 77.68 | 70.16 |
| SR02-camelbert_da_aya | test | 3 | 61.87 | 61.53 | 63.30 | 0.16 | 66.69 | 76.66 | 46.11 | 62.84 |
| SR02-arbert_fanar | dev | 3 | 76.92 | 76.93 | 76.93 | 0.24 | 78.71 | 80.32 | 80.92 | 69.53 |
| SR02-arbert_fanar | test | 3 | 62.88 | 62.06 | 64.68 | 0.23 | 66.77 | 76.12 | 49.79 | 62.74 |
| SR02-arbert_qwen3 | dev | 3 | 76.29 | 76.93 | 75.90 | 0.50 | 78.20 | 80.36 | 79.87 | 68.65 |
| SR02-arbert_qwen3 | test | 3 | 63.04 | 62.86 | 63.57 | 0.85 | 67.70 | 77.37 | 49.38 | 62.37 |
| SR02-arbert_aya | dev | 3 | 75.88 | 75.87 | 75.93 | 0.50 | 77.72 | 79.73 | 79.74 | 68.18 |
| SR02-arbert_aya | test | 3 | 62.53 | 61.70 | 64.06 | 0.25 | 66.51 | 75.93 | 48.71 | 62.94 |
| SR02-arbertv2_fanar | dev | 3 | 76.06 | 76.32 | 75.88 | 0.46 | 77.80 | 79.47 | 79.72 | 68.98 |
| SR02-arbertv2_fanar | test | 3 | 63.26 | 62.82 | 64.71 | 0.48 | 67.70 | 77.18 | 48.29 | 64.31 |
| SR02-arbertv2_qwen3 | dev | 3 | 75.72 | 76.05 | 75.59 | 0.09 | 77.31 | 78.92 | 78.99 | 69.25 |
| SR02-arbertv2_qwen3 | test | 3 | 63.25 | 63.26 | 64.00 | 0.48 | 68.09 | 77.50 | 47.49 | 64.76 |
| SR02-arbertv2_aya | dev | 3 | 75.64 | 76.00 | 75.48 | 0.15 | 77.15 | 78.40 | 78.99 | 69.52 |
| SR02-arbertv2_aya | test | 3 | 62.44 | 62.32 | 63.66 | 0.64 | 66.88 | 76.25 | 47.60 | 63.47 |

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

**F1-PN, SR01 and SR02** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev SR01 | Dev Fanar | Dev Qwen3 | Dev Aya | Test SR01 | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | 77.37 ± 0.58 | 78.48 ± 0.66 | 77.39 ± 0.68 | 77.90 ± 0.23 | 72.18 ± 1.58 | 72.37 ± 0.37 | 71.80 ± 0.45 | 71.96 ± 0.33 |
| MARBERT | 77.97 ± 0.66 | 77.35 ± 0.80 | 77.47 ± 0.83 | 77.19 ± 0.93 | 73.54 ± 0.48 | 73.94 ± 0.20 | 72.74 ± 1.43 | 72.36 ± 0.91 |
| AraBERTv02-Tw | 76.05 ± 0.34 | 76.65 ± 0.43 | 76.52 ± 0.79 | 76.19 ± 1.14 | 71.58 ± 0.20 | 71.25 ± 0.37 | 71.14 ± 0.44 | 70.75 ± 0.74 |
| CAMeLBERT-mix | 75.52 ± 0.54 | 74.06 ± 1.02 | 75.37 ± 1.46 | 74.20 ± 0.65 | 69.54 ± 0.30 | 69.48 ± 0.59 | 69.12 ± 0.31 | 68.82 ± 0.84 |
| CAMeLBERT-DA | 73.34 ± 0.21 | 72.22 ± 0.40 | 72.96 ± 0.47 | 72.51 ± 1.14 | 69.99 ± 0.52 | 69.05 ± 0.57 | 69.76 ± 0.53 | 69.75 ± 1.00 |
| ARBERT | 74.65 ± 0.16 | 74.92 ± 0.83 | 74.51 ± 0.58 | 73.96 ± 0.67 | 69.77 ± 0.33 | 69.43 ± 1.00 | 69.87 ± 0.33 | 69.43 ± 0.10 |
| ARBERTv2 | 73.72 ± 0.56 | 74.23 ± 0.07 | 74.08 ± 0.50 | 73.96 ± 0.40 | 69.28 ± 1.16 | 70.75 ± 1.53 | 71.13 ± 0.60 | 69.86 ± 1.18 |
| Jais-2-8B | 79.87 ± 0.84 | 78.65 ± 0.26 | 78.94 ± 0.16 | 79.00 ± 0.76 | 74.74 ± 1.59 | 73.54 ± 1.48 | 73.27 ± 1.86 | 74.40 ± 0.22 |
| **Mean** | **76.06** | **75.82** | **75.91** | **75.61** | **71.33** | **71.23** | **71.10** | **70.92** |



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


**All classifiers and classes, SR02 (S1 train + SG01)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 79.27 ± 0.62 | 82.63 | 80.85 | 74.34 | 64.45 ± 0.53 | 78.45 | 48.62 | 66.28 |
| MARBERTv2 | Qwen3 | 78.28 ± 0.60 | 81.35 | 80.08 | 73.42 | 64.08 ± 0.46 | 77.87 | 48.63 | 65.73 |
| MARBERTv2 | Aya | 78.99 ± 0.28 | 82.05 | 81.17 | 73.76 | 64.09 ± 0.23 | 77.81 | 48.36 | 66.11 |
| MARBERT | Fanar | 78.35 ± 0.66 | 80.80 | 80.37 | 73.90 | 65.62 ± 0.92 | 79.48 | 48.98 | 68.40 |
| MARBERT | Qwen3 | 78.20 ± 0.63 | 80.25 | 79.66 | 74.70 | 64.65 ± 0.55 | 78.36 | 48.47 | 67.13 |
| MARBERT | Aya | 78.18 ± 0.99 | 80.52 | 80.16 | 73.85 | 64.48 ± 0.54 | 77.78 | 48.73 | 66.94 |
| AraBERTv02-Tw | Fanar | 77.81 ± 0.41 | 81.07 | 80.14 | 72.23 | 63.82 ± 0.36 | 77.75 | 48.96 | 64.74 |
| AraBERTv02-Tw | Qwen3 | 77.85 ± 0.67 | 80.78 | 80.52 | 72.26 | 63.88 ± 0.39 | 77.63 | 49.35 | 64.65 |
| AraBERTv02-Tw | Aya | 77.49 ± 0.95 | 79.95 | 80.08 | 72.43 | 63.63 ± 0.54 | 76.66 | 49.40 | 64.84 |
| CAMeLBERT-mix | Fanar | 75.71 ± 0.77 | 77.84 | 79.01 | 70.29 | 61.71 ± 0.35 | 76.63 | 46.18 | 62.33 |
| CAMeLBERT-mix | Qwen3 | 76.50 ± 1.16 | 78.65 | 78.75 | 72.09 | 61.56 ± 0.63 | 76.39 | 46.42 | 61.86 |
| CAMeLBERT-mix | Aya | 75.62 ± 0.50 | 76.99 | 78.48 | 71.40 | 61.45 ± 0.51 | 75.99 | 46.70 | 61.65 |
| CAMeLBERT-DA | Fanar | 74.28 ± 0.29 | 75.33 | 78.41 | 69.11 | 62.07 ± 0.69 | 76.00 | 48.10 | 62.09 |
| CAMeLBERT-DA | Qwen3 | 74.45 ± 0.21 | 76.03 | 77.41 | 69.90 | 62.11 ± 0.56 | 77.00 | 46.80 | 62.52 |
| CAMeLBERT-DA | Aya | 74.23 ± 0.82 | 74.86 | 77.68 | 70.16 | 61.87 ± 0.49 | 76.66 | 46.11 | 62.84 |
| ARBERT | Fanar | 76.92 ± 0.43 | 80.32 | 80.92 | 69.53 | 62.88 ± 0.49 | 76.12 | 49.79 | 62.74 |
| ARBERT | Qwen3 | 76.29 ± 0.35 | 80.36 | 79.87 | 68.65 | 63.04 ± 0.48 | 77.37 | 49.38 | 62.37 |
| ARBERT | Aya | 75.88 ± 0.29 | 79.73 | 79.74 | 68.18 | 62.53 ± 0.15 | 75.93 | 48.71 | 62.94 |
| ARBERTv2 | Fanar | 76.06 ± 0.04 | 79.47 | 79.72 | 68.98 | 63.26 ± 1.26 | 77.18 | 48.29 | 64.31 |
| ARBERTv2 | Qwen3 | 75.72 ± 0.20 | 78.92 | 78.99 | 69.25 | 63.25 ± 0.47 | 77.50 | 47.49 | 64.76 |
| ARBERTv2 | Aya | 75.64 ± 0.45 | 78.40 | 78.99 | 69.52 | 62.44 ± 0.71 | 76.25 | 47.60 | 63.47 |
| Jais-2-8B | Fanar | 79.46 ± 0.28 | 82.77 | 81.07 | 74.53 | 66.34 ± 0.60 | 79.40 | 51.94 | 67.68 |
| Jais-2-8B | Qwen3 | 79.87 ± 0.32 | 82.13 | 81.74 | 75.75 | 66.11 ± 0.70 | 79.25 | 51.80 | 67.29 |
| Jais-2-8B | Aya | 79.65 ± 0.78 | 82.25 | 80.95 | 75.76 | 66.90 ± 0.31 | 80.55 | 51.90 | 68.26 |
| **Mean** | **Fanar** | **77.23** | **80.03** | **80.06** | **71.61** | **63.77** | **77.63** | **48.86** | **64.82** |
| **Mean** | **Qwen3** | **77.14** | **79.81** | **79.63** | **72.00** | **63.59** | **77.67** | **48.54** | **64.54** |
| **Mean** | **Aya** | **76.96** | **79.34** | **79.66** | **71.88** | **63.42** | **77.20** | **48.44** | **64.63** |
| **MARBERTv2** | **Mean** | **78.85** | **82.01** | **80.70** | **73.84** | **64.21** | **78.04** | **48.54** | **66.04** |
| **MARBERT** | **Mean** | **78.24** | **80.52** | **80.06** | **74.15** | **64.92** | **78.54** | **48.73** | **67.49** |
| **AraBERTv02-Tw** | **Mean** | **77.72** | **80.60** | **80.25** | **72.31** | **63.78** | **77.35** | **49.24** | **64.74** |
| **CAMeLBERT-mix** | **Mean** | **75.94** | **77.83** | **78.75** | **71.26** | **61.57** | **76.34** | **46.43** | **61.95** |
| **CAMeLBERT-DA** | **Mean** | **74.32** | **75.41** | **77.83** | **69.72** | **62.02** | **76.55** | **47.00** | **62.48** |
| **ARBERT** | **Mean** | **76.36** | **80.14** | **80.18** | **68.79** | **62.82** | **76.47** | **49.29** | **62.68** |
| **ARBERTv2** | **Mean** | **75.81** | **78.93** | **79.23** | **69.25** | **62.98** | **76.98** | **47.79** | **64.18** |
| **Jais-2-8B** | **Mean** | **79.66** | **82.38** | **81.25** | **75.35** | **66.45** | **79.73** | **51.88** | **67.74** |
| **Mean** | **All** | **77.11** | **79.73** | **79.78** | **71.83** | **63.59** | **77.50** | **48.61** | **64.66** |

## SR03 real data only, NEU dropped

S1 train / dev / test without NEU tweets (6,069 / 675 / 2,252), 2-class NEG/POS head, 3 seeds (SD-007). Macro F1 is over NEG and POS only (so f1_pn = macro_f1); not comparable with SR01/SR02.

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR03-jais2 | dev | `sr03_jais2` | 3 | 92.56 | 93.07 | 92.12 | 0.83 | 93.58 | 95.31 | – | 89.80 |
| SR03-jais2 | test | `sr03_jais2` | 3 | 84.85 | 83.34 | 87.17 | 0.44 | 87.76 | 91.48 | – | 78.21 |
| SR03-fanar | dev | `sr03_fanar` | 3 | 92.01 | 91.77 | 92.29 | 0.88 | 92.99 | 94.80 | – | 89.22 |
| SR03-fanar | test | `sr03_fanar` | 3 | 84.23 | 82.52 | 87.06 | 0.59 | 87.11 | 90.96 | – | 77.50 |
| SR03-aya | dev | `sr03_aya` | 3 | 91.91 | 91.90 | 91.93 | 0.33 | 92.94 | 94.79 | – | 89.03 |
| SR03-aya | test | `sr03_aya` | 3 | 83.29 | 81.58 | 86.33 | 0.50 | 86.25 | 90.32 | – | 76.27 |
| SR03-marbertv2 | dev | `sr03_marbertv2` | 3 | 91.62 | 91.43 | 91.87 | 0.15 | 92.64 | 94.54 | – | 88.69 |
| SR03-marbertv2 | test | `sr03_marbertv2` | 3 | 81.88 | 80.21 | 86.16 | 1.02 | 84.61 | 88.89 | – | 74.87 |
| SR03-marbert | dev | `sr03_marbert` | 3 | 91.45 | 91.52 | 91.39 | 0.27 | 92.54 | 94.51 | – | 88.38 |
| SR03-marbert | test | `sr03_marbert` | 3 | 82.64 | 80.83 | 86.32 | 0.55 | 85.49 | 89.68 | – | 75.60 |
| SR03-camelbert_mix | dev | `sr03_camelbert_mix` | 3 | 90.16 | 90.41 | 89.99 | 0.99 | 91.46 | 93.73 | – | 86.59 |
| SR03-camelbert_mix | test | `sr03_camelbert_mix` | 3 | 79.93 | 78.46 | 82.53 | 0.42 | 83.54 | 88.44 | – | 71.41 |
| SR03-arabertv02_twitter | dev | `sr03_arabertv02_twitter` | 3 | 90.13 | 90.03 | 90.28 | 0.37 | 91.36 | 93.61 | – | 86.66 |
| SR03-arabertv02_twitter | test | `sr03_arabertv02_twitter` | 3 | 81.43 | 79.76 | 84.64 | 0.35 | 84.61 | 89.11 | – | 73.76 |
| SR03-qwen3 | dev | `sr03_qwen3` | 3 | 89.89 | 90.05 | 89.76 | 0.90 | 91.21 | 93.54 | – | 86.23 |
| SR03-qwen3 | test | `sr03_qwen3` | 3 | 80.42 | 78.89 | 83.39 | 0.34 | 83.82 | 88.57 | – | 72.27 |
| SR03-arbert | dev | `sr03_arbert` | 3 | 89.42 | 89.08 | 89.85 | 0.43 | 90.67 | 93.05 | – | 85.78 |
| SR03-arbert | test | `sr03_arbert` | 3 | 79.40 | 77.82 | 83.02 | 0.19 | 82.68 | 87.62 | – | 71.18 |
| SR03-falcon_h1 | dev | `sr03_falcon_h1` | 3 | 89.08 | 89.55 | 88.73 | 0.62 | 90.57 | 93.11 | – | 85.06 |
| SR03-falcon_h1 | test | `sr03_falcon_h1` | 3 | 81.17 | 79.84 | 83.69 | 0.46 | 84.62 | 89.21 | – | 73.13 |
| SR03-arbertv2 | dev | `sr03_arbertv2` | 3 | 88.85 | 88.25 | 89.65 | 0.29 | 90.07 | 92.54 | – | 85.16 |
| SR03-arbertv2 | test | `sr03_arbertv2` | 3 | 80.21 | 78.57 | 84.50 | 0.47 | 83.16 | 87.84 | – | 72.59 |
| SR03-camelbert_da | dev | `sr03_camelbert_da` | 3 | 86.78 | 86.07 | 87.83 | 0.13 | 88.15 | 91.03 | – | 82.52 |
| SR03-camelbert_da | test | `sr03_camelbert_da` | 3 | 77.17 | 76.00 | 82.21 | 1.22 | 80.09 | 85.30 | – | 69.04 |

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
## SR04 Real + SG02


Mean over seeds 42/43/44. Generated from `docs/sentiment/tables/sentiment_summary.csv`.

| id | split | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|
| SR04-marbertv2_fanar | dev | 3 | 79.10 | 78.73 | 79.57 | 0.42 | 80.23 | 82.44 | 80.88 | 73.98 |
| SR04-marbertv2_fanar | test | 3 | 63.63 | 62.86 | 65.78 | 0.10 | 67.90 | 77.69 | 48.16 | 65.06 |
| SR04-marbert_qwen3 | dev | 3 | 78.79 | 78.28 | 79.51 | 0.28 | 79.64 | 80.65 | 80.64 | 75.08 |
| SR04-marbert_qwen3 | test | 3 | 64.28 | 64.37 | 66.11 | 1.06 | 69.12 | 78.46 | 47.57 | 66.80 |
| SR04-marbertv2_qwen3 | dev | 3 | 78.51 | 78.18 | 79.01 | 0.41 | 79.64 | 81.28 | 80.67 | 73.57 |
| SR04-marbertv2_qwen3 | test | 3 | 64.92 | 64.62 | 66.61 | 0.25 | 69.64 | 79.13 | 48.33 | 67.31 |
| SR04-marbertv2_aya | dev | 3 | 78.50 | 78.33 | 78.73 | 0.92 | 79.83 | 81.85 | 80.92 | 72.72 |
| SR04-marbertv2_aya | test | 3 | 64.08 | 63.31 | 66.12 | 0.49 | 68.28 | 77.79 | 48.24 | 66.20 |
| SR04-marbert_aya | dev | 3 | 78.46 | 78.12 | 78.88 | 0.30 | 79.35 | 80.50 | 80.27 | 74.61 |
| SR04-marbert_aya | test | 3 | 64.90 | 64.48 | 66.69 | 0.11 | 69.32 | 78.44 | 48.47 | 67.79 |
| SR04-marbert_fanar | dev | 3 | 78.46 | 78.48 | 78.53 | 0.64 | 79.40 | 80.64 | 80.27 | 74.47 |
| SR04-marbert_fanar | test | 3 | 64.78 | 64.80 | 66.26 | 0.40 | 69.77 | 79.19 | 47.13 | 68.02 |
| SR04-arabertv02_twitter_qwen3 | dev | 3 | 77.90 | 77.85 | 78.06 | 1.38 | 79.13 | 80.61 | 80.39 | 72.71 |
| SR04-arabertv02_twitter_qwen3 | test | 3 | 63.72 | 63.35 | 65.59 | 0.55 | 68.17 | 77.48 | 48.69 | 65.00 |
| SR04-arabertv02_twitter_fanar | dev | 3 | 77.52 | 77.86 | 77.22 | 0.46 | 78.89 | 80.63 | 80.14 | 71.78 |
| SR04-arabertv02_twitter_fanar | test | 3 | 63.96 | 63.30 | 65.48 | 0.29 | 68.13 | 77.45 | 49.96 | 64.47 |
| SR04-arabertv02_twitter_aya | dev | 3 | 76.92 | 77.31 | 76.65 | 1.29 | 78.41 | 79.87 | 79.99 | 70.90 |
| SR04-arabertv02_twitter_aya | test | 3 | 63.74 | 62.96 | 65.41 | 0.71 | 67.68 | 76.78 | 49.34 | 65.09 |
| SR04-camelbert_mix_qwen3 | dev | 3 | 76.82 | 76.53 | 77.18 | 1.16 | 77.96 | 79.07 | 79.40 | 71.98 |
| SR04-camelbert_mix_qwen3 | test | 3 | 61.80 | 61.76 | 63.51 | 0.80 | 66.86 | 76.70 | 45.60 | 63.11 |
| SR04-arbert_qwen3 | dev | 3 | 76.64 | 76.64 | 76.76 | 0.36 | 78.44 | 80.81 | 80.07 | 69.03 |
| SR04-arbert_qwen3 | test | 3 | 63.56 | 63.16 | 64.80 | 0.22 | 67.96 | 77.17 | 49.18 | 64.33 |
| SR04-arbertv2_fanar | dev | 3 | 76.06 | 76.08 | 76.08 | 0.05 | 77.55 | 79.06 | 79.29 | 69.83 |
| SR04-arbertv2_fanar | test | 3 | 62.55 | 61.96 | 64.43 | 0.07 | 66.86 | 76.45 | 48.28 | 62.93 |
| SR04-arbert_fanar | dev | 3 | 75.99 | 75.81 | 76.30 | 0.22 | 77.74 | 79.36 | 80.10 | 68.49 |
| SR04-arbert_fanar | test | 3 | 62.30 | 61.78 | 64.34 | 0.43 | 66.49 | 76.13 | 48.98 | 61.78 |
| SR04-arbertv2_qwen3 | dev | 3 | 75.82 | 75.60 | 76.21 | 0.89 | 77.37 | 78.93 | 79.28 | 69.26 |
| SR04-arbertv2_qwen3 | test | 3 | 63.43 | 63.07 | 65.35 | 0.52 | 67.77 | 76.92 | 48.75 | 64.62 |
| SR04-arbert_aya | dev | 3 | 75.79 | 75.97 | 75.63 | 0.99 | 77.80 | 79.98 | 79.89 | 67.49 |
| SR04-arbert_aya | test | 3 | 62.76 | 62.06 | 64.00 | 0.73 | 66.83 | 76.29 | 49.24 | 62.76 |
| SR04-camelbert_mix_aya | dev | 3 | 75.72 | 76.17 | 75.43 | 1.24 | 76.97 | 77.35 | 78.86 | 70.95 |
| SR04-camelbert_mix_aya | test | 3 | 61.21 | 61.00 | 62.45 | 0.58 | 65.82 | 75.39 | 46.70 | 61.53 |
| SR04-camelbert_mix_fanar | dev | 3 | 75.65 | 75.81 | 75.67 | 0.56 | 76.86 | 77.71 | 78.52 | 70.71 |
| SR04-camelbert_mix_fanar | test | 3 | 61.24 | 60.99 | 63.03 | 0.29 | 65.98 | 75.87 | 46.68 | 61.17 |
| SR04-arbertv2_aya | dev | 3 | 75.63 | 75.96 | 75.55 | 0.80 | 77.21 | 78.57 | 79.08 | 69.25 |
| SR04-arbertv2_aya | test | 3 | 62.80 | 63.10 | 64.04 | 0.67 | 67.86 | 77.40 | 46.91 | 64.09 |
| SR04-camelbert_da_qwen3 | dev | 3 | 74.91 | 74.91 | 75.06 | 0.81 | 76.14 | 76.43 | 78.22 | 70.09 |
| SR04-camelbert_da_qwen3 | test | 3 | 62.03 | 61.99 | 63.39 | 0.40 | 67.02 | 76.89 | 47.01 | 62.21 |
| SR04-camelbert_da_fanar | dev | 3 | 74.16 | 74.13 | 74.32 | 0.50 | 75.44 | 75.27 | 77.92 | 69.28 |
| SR04-camelbert_da_fanar | test | 3 | 62.05 | 61.53 | 63.64 | 0.54 | 66.44 | 76.06 | 48.07 | 62.03 |
| SR04-camelbert_da_aya | dev | 3 | 73.75 | 73.49 | 74.10 | 0.33 | 75.04 | 74.95 | 77.59 | 68.70 |
| SR04-camelbert_da_aya | test | 3 | 61.57 | 60.87 | 63.52 | 0.24 | 65.72 | 75.21 | 47.14 | 62.37 |

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


**All classifiers and classes, SR04 (S1 train + SG02)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 79.10 ± 0.03 | 82.44 | 80.88 | 73.98 | 63.63 ± 0.57 | 77.69 | 48.16 | 65.06 |
| MARBERTv2 | Qwen3 | 78.51 ± 0.25 | 81.28 | 80.67 | 73.57 | 64.92 ± 0.29 | 79.13 | 48.33 | 67.31 |
| MARBERTv2 | Aya | 78.50 ± 0.58 | 81.85 | 80.92 | 72.72 | 64.08 ± 0.57 | 77.79 | 48.24 | 66.20 |
| MARBERT | Fanar | 78.46 ± 0.30 | 80.64 | 80.27 | 74.47 | 64.78 ± 0.57 | 79.19 | 47.13 | 68.02 |
| MARBERT | Qwen3 | 78.79 ± 0.46 | 80.65 | 80.64 | 75.08 | 64.28 ± 0.71 | 78.46 | 47.57 | 66.80 |
| MARBERT | Aya | 78.46 ± 0.28 | 80.50 | 80.27 | 74.61 | 64.90 ± 0.37 | 78.44 | 48.47 | 67.79 |
| AraBERTv02-Tw | Fanar | 77.52 ± 0.27 | 80.63 | 80.14 | 71.78 | 63.96 ± 0.38 | 77.45 | 49.96 | 64.47 |
| AraBERTv02-Tw | Qwen3 | 77.90 ± 0.92 | 80.61 | 80.39 | 72.71 | 63.72 ± 0.27 | 77.48 | 48.69 | 65.00 |
| AraBERTv02-Tw | Aya | 76.92 ± 0.84 | 79.87 | 79.99 | 70.90 | 63.74 ± 0.50 | 76.78 | 49.34 | 65.09 |
| CAMeLBERT-mix | Fanar | 75.65 ± 0.08 | 77.71 | 78.52 | 70.71 | 61.24 ± 0.56 | 75.87 | 46.68 | 61.17 |
| CAMeLBERT-mix | Qwen3 | 76.82 ± 0.93 | 79.07 | 79.40 | 71.98 | 61.80 ± 0.47 | 76.70 | 45.60 | 63.11 |
| CAMeLBERT-mix | Aya | 75.72 ± 0.76 | 77.35 | 78.86 | 70.95 | 61.21 ± 0.49 | 75.39 | 46.70 | 61.53 |
| CAMeLBERT-DA | Fanar | 74.16 ± 0.12 | 75.27 | 77.92 | 69.28 | 62.05 ± 0.43 | 76.06 | 48.07 | 62.03 |
| CAMeLBERT-DA | Qwen3 | 74.91 ± 0.61 | 76.43 | 78.22 | 70.09 | 62.03 ± 0.41 | 76.89 | 47.01 | 62.21 |
| CAMeLBERT-DA | Aya | 73.75 ± 0.29 | 74.95 | 77.59 | 68.70 | 61.57 ± 0.23 | 75.21 | 47.14 | 62.37 |
| ARBERT | Fanar | 75.99 ± 0.46 | 79.36 | 80.10 | 68.49 | 62.30 ± 0.56 | 76.13 | 48.98 | 61.78 |
| ARBERT | Qwen3 | 76.64 ± 0.29 | 80.81 | 80.07 | 69.03 | 63.56 ± 0.38 | 77.17 | 49.18 | 64.33 |
| ARBERT | Aya | 75.79 ± 0.87 | 79.98 | 79.89 | 67.49 | 62.76 ± 0.95 | 76.29 | 49.24 | 62.76 |
| ARBERTv2 | Fanar | 76.06 ± 0.30 | 79.06 | 79.29 | 69.83 | 62.55 ± 0.66 | 76.45 | 48.28 | 62.93 |
| ARBERTv2 | Qwen3 | 75.82 ± 0.30 | 78.93 | 79.28 | 69.26 | 63.43 ± 1.04 | 76.92 | 48.75 | 64.62 |
| ARBERTv2 | Aya | 75.63 ± 0.47 | 78.57 | 79.08 | 69.25 | 62.80 ± 0.09 | 77.40 | 46.91 | 64.09 |
| **Mean** | **Fanar** | **76.71** | **79.30** | **79.59** | **71.22** | **62.93** | **76.98** | **48.18** | **63.64** |
| **Mean** | **Qwen3** | **77.06** | **79.68** | **79.81** | **71.67** | **63.39** | **77.54** | **47.88** | **64.77** |
| **Mean** | **Aya** | **76.40** | **79.01** | **79.51** | **70.66** | **63.01** | **76.76** | **48.01** | **64.26** |
| **MARBERTv2** | **Mean** | **78.70** | **81.86** | **80.82** | **73.42** | **64.21** | **78.20** | **48.24** | **66.19** |
| **MARBERT** | **Mean** | **78.57** | **80.60** | **80.39** | **74.72** | **64.65** | **78.70** | **47.72** | **67.54** |
| **AraBERTv02-Tw** | **Mean** | **77.45** | **80.37** | **80.17** | **71.80** | **63.81** | **77.24** | **49.33** | **64.85** |
| **CAMeLBERT-mix** | **Mean** | **76.06** | **78.04** | **78.93** | **71.21** | **61.42** | **75.99** | **46.33** | **61.94** |
| **CAMeLBERT-DA** | **Mean** | **74.27** | **75.55** | **77.91** | **69.36** | **61.88** | **76.05** | **47.41** | **62.20** |
| **ARBERT** | **Mean** | **76.14** | **80.05** | **80.02** | **68.34** | **62.87** | **76.53** | **49.13** | **62.96** |
| **ARBERTv2** | **Mean** | **75.84** | **78.85** | **79.22** | **69.45** | **62.93** | **76.92** | **47.98** | **63.88** |
| **Mean** | **All** | **76.72** | **79.33** | **79.64** | **71.18** | **63.11** | **77.09** | **48.02** | **64.22** |

**F1-PN, SR04** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 78.21 ± 0.02 | 77.43 ± 0.29 | 77.29 ± 0.80 | 71.37 ± 0.70 | 73.22 ± 0.50 | 71.99 ± 0.49 |
| MARBERT | 77.55 ± 0.39 | 77.87 ± 0.49 | 77.55 ± 0.32 | 73.61 ± 0.21 | 72.63 ± 0.90 | 73.11 ± 0.97 |
| AraBERTv02-Tw | 76.20 ± 0.31 | 76.66 ± 1.15 | 75.38 ± 1.20 | 70.96 ± 0.17 | 71.24 ± 0.74 | 70.94 ± 0.33 |
| CAMeLBERT-mix | 74.21 ± 0.34 | 75.53 ± 1.34 | 74.15 ± 0.83 | 68.52 ± 0.36 | 69.90 ± 0.24 | 68.46 ± 0.68 |
| CAMeLBERT-DA | 72.27 ± 0.30 | 73.26 ± 0.92 | 71.82 ± 0.53 | 69.05 ± 1.13 | 69.55 ± 0.65 | 68.79 ± 0.41 |
| ARBERT | 73.93 ± 0.62 | 74.92 ± 0.50 | 73.74 ± 1.13 | 68.95 ± 0.47 | 70.75 ± 0.66 | 69.53 ± 0.76 |
| ARBERTv2 | 74.44 ± 0.27 | 74.10 ± 0.62 | 73.91 ± 0.63 | 69.69 ± 0.89 | 70.77 ± 0.50 | 70.75 ± 0.60 |
| **Mean** | **75.26** | **75.68** | **74.83** | **70.31** | **71.15** | **70.51** |
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

**F1-PN, SR05** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 77.80 ± 0.51 | 77.49 ± 0.43 | 78.10 ± 0.39 | 71.44 ± 0.51 | 71.91 ± 0.77 | 71.44 ± 0.72 |
| MARBERT | 77.39 ± 1.18 | 77.17 ± 0.87 | 77.45 ± 1.11 | 72.21 ± 0.14 | 71.51 ± 0.77 | 72.17 ± 1.19 |
| AraBERTv02-Tw | 76.59 ± 0.70 | 76.19 ± 0.68 | 75.68 ± 0.49 | 70.00 ± 0.05 | 71.38 ± 0.42 | 70.09 ± 0.18 |
| CAMeLBERT-mix | 75.09 ± 0.79 | 73.96 ± 0.84 | 73.92 ± 0.91 | 68.78 ± 0.23 | 69.66 ± 0.08 | 68.46 ± 0.59 |
| CAMeLBERT-DA | 72.14 ± 0.64 | 71.84 ± 0.46 | 72.61 ± 0.36 | 68.02 ± 0.85 | 68.33 ± 1.24 | 67.62 ± 0.64 |
| ARBERT | 74.63 ± 0.75 | 73.59 ± 0.79 | 74.50 ± 0.81 | 68.38 ± 1.32 | 69.83 ± 1.57 | 68.29 ± 1.34 |
| ARBERTv2 | 73.29 ± 0.30 | 73.61 ± 0.81 | 73.26 ± 0.87 | 69.00 ± 0.64 | 70.12 ± 0.53 | 68.75 ± 0.75 |
| **Mean** | **75.28** | **74.84** | **75.07** | **69.69** | **70.39** | **69.55** |

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

**F1-PN, Δ SR05 − SR04** (+ = SG03 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.41 | +0.06 | +0.81 | +0.07 | -1.31 | -0.55 |
| MARBERT | -0.16 | -0.70 | -0.10 | -1.40 | -1.12 | -0.94 |
| AraBERTv02-Tw | +0.39 | -0.47 | +0.30 | -0.96 | +0.14 | -0.85 |
| CAMeLBERT-mix | +0.88 | -1.57 | -0.23 | +0.26 | -0.24 | +0.00 |
| CAMeLBERT-DA | -0.13 | -1.42 | +0.79 | -1.03 | -1.22 | -1.17 |
| ARBERT | +0.70 | -1.33 | +0.76 | -0.57 | -0.92 | -1.24 |
| ARBERTv2 | -1.15 | -0.49 | -0.65 | -0.69 | -0.65 | -2.00 |
| **Mean** | **+0.02** | **-0.85** | **+0.24** | **-0.62** | **-0.76** | **-0.96** |
| Better in | 3/7 | 1/7 | 4/7 | 2/7 | 1/7 | 0/7 |

**All classifiers and classes, SR05 (S1 train + SG03)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.68 ± 0.44 | 82.29 | 80.44 | 73.31 | 63.82 ± 0.57 | 78.29 | 48.59 | 64.59 |
| MARBERTv2 | Qwen3 | 78.40 ± 0.54 | 81.97 | 80.20 | 73.02 | 63.85 ± 0.73 | 78.45 | 47.73 | 65.36 |
| MARBERTv2 | Aya | 78.95 ± 0.12 | 82.35 | 80.65 | 73.85 | 64.05 ± 0.68 | 78.14 | 49.28 | 64.74 |
| MARBERT | Fanar | 78.58 ± 0.93 | 80.54 | 80.97 | 74.24 | 64.43 ± 0.72 | 78.92 | 48.87 | 65.49 |
| MARBERT | Qwen3 | 78.17 ± 0.78 | 80.69 | 80.17 | 73.64 | 63.50 ± 0.70 | 77.96 | 47.47 | 65.06 |
| MARBERT | Aya | 78.53 ± 0.74 | 80.80 | 80.67 | 74.11 | 64.79 ± 1.09 | 78.24 | 50.05 | 66.09 |
| AraBERTv02-Tw | Fanar | 77.99 ± 0.55 | 79.80 | 80.78 | 73.37 | 62.89 ± 0.50 | 77.37 | 48.66 | 62.64 |
| AraBERTv02-Tw | Qwen3 | 77.59 ± 0.58 | 80.12 | 80.38 | 72.25 | 62.65 ± 0.46 | 78.22 | 45.18 | 64.55 |
| AraBERTv02-Tw | Aya | 77.37 ± 0.47 | 79.63 | 80.74 | 71.74 | 62.91 ± 0.55 | 76.90 | 48.54 | 63.29 |
| CAMeLBERT-mix | Fanar | 76.55 ± 0.56 | 78.96 | 79.47 | 71.22 | 61.37 ± 0.86 | 77.05 | 46.55 | 60.52 |
| CAMeLBERT-mix | Qwen3 | 75.42 ± 0.83 | 77.54 | 78.34 | 70.38 | 61.14 ± 0.83 | 77.71 | 44.12 | 61.61 |
| CAMeLBERT-mix | Aya | 75.63 ± 0.76 | 77.43 | 79.06 | 70.42 | 61.08 ± 0.27 | 76.64 | 46.32 | 60.28 |
| CAMeLBERT-DA | Fanar | 74.08 ± 0.52 | 75.86 | 77.95 | 68.41 | 60.88 ± 0.32 | 76.62 | 46.59 | 59.43 |
| CAMeLBERT-DA | Qwen3 | 73.88 ± 0.39 | 75.39 | 77.97 | 68.29 | 60.57 ± 0.74 | 76.84 | 45.06 | 59.82 |
| CAMeLBERT-DA | Aya | 74.47 ± 0.32 | 75.59 | 78.19 | 69.64 | 60.48 ± 0.48 | 75.71 | 46.20 | 59.53 |
| ARBERT | Fanar | 76.27 ± 0.55 | 80.71 | 79.54 | 68.56 | 61.48 ± 0.53 | 77.23 | 47.67 | 59.53 |
| ARBERT | Qwen3 | 75.13 ± 0.56 | 79.76 | 78.20 | 67.42 | 62.30 ± 0.88 | 77.58 | 47.24 | 62.08 |
| ARBERT | Aya | 76.41 ± 0.46 | 80.63 | 80.24 | 68.37 | 61.73 ± 0.93 | 76.60 | 48.60 | 59.98 |
| ARBERTv2 | Fanar | 75.03 ± 0.10 | 78.88 | 78.51 | 67.70 | 60.99 ± 0.14 | 77.08 | 44.97 | 60.92 |
| ARBERTv2 | Qwen3 | 74.98 ± 0.33 | 79.08 | 77.72 | 68.14 | 61.42 ± 0.40 | 77.69 | 44.00 | 62.56 |
| ARBERTv2 | Aya | 75.22 ± 0.53 | 79.00 | 79.14 | 67.51 | 61.22 ± 0.40 | 76.82 | 46.17 | 60.68 |
| **Mean** | **Fanar** | **76.74** | **79.58** | **79.67** | **70.97** | **62.27** | **77.51** | **47.41** | **61.87** |
| **Mean** | **Qwen3** | **76.22** | **79.22** | **79.00** | **70.45** | **62.20** | **77.78** | **45.83** | **63.01** |
| **Mean** | **Aya** | **76.65** | **79.35** | **79.81** | **70.81** | **62.32** | **77.01** | **47.88** | **62.08** |
| **MARBERTv2** | **Mean** | **78.68** | **82.20** | **80.43** | **73.39** | **63.91** | **78.29** | **48.53** | **64.90** |
| **MARBERT** | **Mean** | **78.43** | **80.68** | **80.60** | **74.00** | **64.24** | **78.37** | **48.80** | **65.55** |
| **AraBERTv02-Tw** | **Mean** | **77.65** | **79.85** | **80.63** | **72.45** | **62.82** | **77.50** | **47.46** | **63.49** |
| **CAMeLBERT-mix** | **Mean** | **75.87** | **77.98** | **78.96** | **70.67** | **61.20** | **77.13** | **45.66** | **60.80** |
| **CAMeLBERT-DA** | **Mean** | **74.14** | **75.61** | **78.04** | **68.78** | **60.64** | **76.39** | **45.95** | **59.59** |
| **ARBERT** | **Mean** | **75.94** | **80.37** | **79.33** | **68.12** | **61.84** | **77.14** | **47.84** | **60.53** |
| **ARBERTv2** | **Mean** | **75.08** | **78.99** | **78.46** | **67.78** | **61.21** | **77.20** | **45.05** | **61.39** |
| **Mean** | **All** | **76.54** | **79.38** | **79.49** | **70.74** | **62.26** | **77.43** | **47.04** | **62.32** |

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

**F1-PN, SR06** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 76.83 ± 0.59 | 76.75 ± 0.29 | 76.73 ± 0.93 | 72.30 ± 0.36 | 72.38 ± 0.96 | 70.81 ± 0.74 |
| MARBERT | 77.73 ± 0.12 | 77.04 ± 0.96 | 77.43 ± 0.35 | 71.97 ± 1.23 | 72.77 ± 0.64 | 71.96 ± 0.39 |
| AraBERTv02-Tw | 75.39 ± 0.72 | 75.42 ± 0.67 | 75.24 ± 0.65 | 71.09 ± 0.97 | 70.66 ± 0.37 | 69.43 ± 0.54 |
| CAMeLBERT-mix | 73.07 ± 0.68 | 73.72 ± 0.23 | 72.42 ± 0.80 | 68.22 ± 0.97 | 68.30 ± 0.20 | 67.32 ± 1.20 |
| CAMeLBERT-DA | 71.80 ± 0.26 | 72.61 ± 0.41 | 71.85 ± 0.61 | 68.60 ± 0.66 | 69.10 ± 1.45 | 67.61 ± 0.43 |
| ARBERT | 74.26 ± 0.53 | 72.65 ± 0.92 | 73.37 ± 0.61 | 69.13 ± 1.56 | 68.44 ± 1.29 | 68.08 ± 1.70 |
| ARBERTv2 | 73.77 ± 0.47 | 72.84 ± 0.81 | 73.03 ± 0.84 | 70.63 ± 0.55 | 69.70 ± 1.20 | 68.57 ± 0.53 |
| **Mean** | **74.69** | **74.43** | **74.30** | **70.28** | **70.19** | **69.11** |

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

**F1-PN, Δ SR05 − SR06** (+ = SG03 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | +0.97 | +0.74 | +1.37 | -0.86 | -0.47 | +0.63 |
| MARBERT | -0.34 | +0.13 | +0.02 | +0.24 | -1.26 | +0.21 |
| AraBERTv02-Tw | +1.20 | +0.77 | +0.44 | -1.09 | +0.72 | +0.66 |
| CAMeLBERT-mix | +2.02 | +0.24 | +1.50 | +0.56 | +1.36 | +1.14 |
| CAMeLBERT-DA | +0.34 | -0.77 | +0.76 | -0.58 | -0.77 | +0.01 |
| ARBERT | +0.37 | +0.94 | +1.13 | -0.75 | +1.39 | +0.21 |
| ARBERTv2 | -0.48 | +0.77 | +0.23 | -1.63 | +0.42 | +0.18 |
| **Mean** | **+0.58** | **+0.40** | **+0.78** | **-0.59** | **+0.20** | **+0.43** |
| Better in | 5/7 | 6/7 | 7/7 | 2/7 | 4/7 | 7/7 |

**Takeaways**
- Qwen3's SG03 set is the weakest
- Aya's SG03 is the only set that beats its control on test

| Comparison | Test | Dev |
|---|---|---|
| SR06 (control) vs real-only | −0.50 | −0.79 |
| SR05 (targeted) vs control | −0.16 (not significant, better in 10/21) | **+0.51 (better in 18/21)** |

**F1-PN** (Wilcoxon signed-rank over the 21 cells; the cells share baselines, so p is indicative only)

| Comparison | Test | Dev |
|---|---|---|
| SR06 (control) vs real-only | −0.98 (better in 4/21, p < 0.001) | −1.04 (better in 1/21, p < 0.001) |
| SR05 (targeted) vs control | +0.02 (better in 13/21, p = 0.95) | +0.59 (better in 18/21, p = 0.001) |

1. **The loss isn't caused by the targeting.** The untargeted control loses almost as much (−0.50). The loss comes from what both sets share: the LLM source, the pair format and the label mix.
2. **Targeting does have an effect, but only on dev.** On dev, the targeted pairs beat the control in 18 of 21 cells. On test there's no difference. Dev and train come from the same distribution, while test is different (SA-E01), so what targeting teaches doesn't carry over to test.
3. **Test had no change beyond noise** because the classes that we targeted dont exist heavily in the test, they exist mostly in the dev. Dev and Test are not balanced

**Future Runs**
- Repeat the run but get the errors from the test. 

**All classifiers and classes, SR06 (S1 train + SG03-random)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.12 ± 0.32 | 82.35 | 80.70 | 71.31 | 64.25 ± 0.19 | 79.07 | 48.14 | 65.54 |
| MARBERTv2 | Qwen3 | 77.78 ± 0.34 | 81.79 | 79.82 | 71.72 | 63.95 ± 0.57 | 79.16 | 47.07 | 65.60 |
| MARBERTv2 | Aya | 78.04 ± 0.68 | 81.88 | 80.64 | 71.59 | 63.39 ± 0.53 | 77.67 | 48.56 | 63.95 |
| MARBERT | Fanar | 78.69 ± 0.16 | 81.24 | 80.62 | 74.22 | 64.00 ± 0.63 | 78.41 | 48.05 | 65.54 |
| MARBERT | Qwen3 | 77.95 ± 1.03 | 80.43 | 79.76 | 73.65 | 64.70 ± 0.75 | 78.84 | 48.56 | 66.70 |
| MARBERT | Aya | 78.50 ± 0.27 | 80.27 | 80.64 | 74.59 | 64.50 ± 0.20 | 78.06 | 49.57 | 65.86 |
| AraBERTv02-Tw | Fanar | 77.03 ± 0.49 | 79.89 | 80.30 | 70.90 | 63.78 ± 0.59 | 77.75 | 49.17 | 64.44 |
| AraBERTv02-Tw | Qwen3 | 77.03 ± 0.52 | 79.68 | 80.27 | 71.16 | 63.44 ± 0.27 | 77.04 | 49.00 | 64.29 |
| AraBERTv02-Tw | Aya | 76.96 ± 0.34 | 79.44 | 80.41 | 71.04 | 62.85 ± 0.34 | 75.97 | 49.70 | 62.89 |
| CAMeLBERT-mix | Fanar | 74.75 ± 0.43 | 76.93 | 78.11 | 69.22 | 61.25 ± 0.06 | 76.50 | 47.32 | 59.94 |
| CAMeLBERT-mix | Qwen3 | 75.19 ± 0.19 | 76.83 | 78.13 | 70.62 | 61.03 ± 0.61 | 75.69 | 46.49 | 60.90 |
| CAMeLBERT-mix | Aya | 74.27 ± 0.55 | 76.53 | 77.99 | 68.31 | 60.85 ± 0.80 | 75.54 | 47.92 | 59.09 |
| CAMeLBERT-DA | Fanar | 73.64 ± 0.34 | 75.24 | 77.33 | 68.35 | 61.62 ± 0.40 | 76.35 | 47.65 | 60.85 |
| CAMeLBERT-DA | Qwen3 | 73.92 ± 0.19 | 75.32 | 76.55 | 69.89 | 61.21 ± 1.72 | 76.63 | 45.44 | 61.56 |
| CAMeLBERT-DA | Aya | 73.52 ± 0.26 | 75.06 | 76.86 | 68.65 | 60.24 ± 0.72 | 75.01 | 45.51 | 60.21 |
| ARBERT | Fanar | 75.80 ± 0.52 | 80.31 | 78.89 | 68.20 | 61.68 ± 1.18 | 77.25 | 46.79 | 61.00 |
| ARBERT | Qwen3 | 74.62 ± 0.38 | 78.93 | 78.58 | 66.36 | 61.49 ± 0.81 | 76.04 | 47.58 | 60.84 |
| ARBERT | Aya | 75.53 ± 0.32 | 79.97 | 79.86 | 66.77 | 61.31 ± 1.03 | 76.64 | 47.76 | 59.53 |
| ARBERTv2 | Fanar | 75.48 ± 0.47 | 79.47 | 78.89 | 68.06 | 62.43 ± 0.59 | 78.04 | 46.02 | 63.22 |
| ARBERTv2 | Qwen3 | 74.64 ± 0.54 | 78.33 | 78.24 | 67.35 | 61.70 ± 0.31 | 76.42 | 45.69 | 62.99 |
| ARBERTv2 | Aya | 75.13 ± 0.93 | 78.64 | 79.34 | 67.42 | 61.25 ± 0.28 | 76.06 | 46.62 | 61.09 |
| **Mean** | **Fanar** | **76.22** | **79.35** | **79.26** | **70.04** | **62.72** | **77.62** | **47.59** | **62.93** |
| **Mean** | **Qwen3** | **75.88** | **78.76** | **78.76** | **70.11** | **62.50** | **77.12** | **47.12** | **63.27** |
| **Mean** | **Aya** | **75.99** | **78.83** | **79.39** | **69.77** | **62.06** | **76.42** | **47.95** | **61.80** |
| **MARBERTv2** | **Mean** | **77.98** | **82.01** | **80.39** | **71.54** | **63.86** | **78.63** | **47.92** | **65.03** |
| **MARBERT** | **Mean** | **78.38** | **80.65** | **80.34** | **74.15** | **64.40** | **78.44** | **48.73** | **66.03** |
| **AraBERTv02-Tw** | **Mean** | **77.01** | **79.67** | **80.33** | **71.03** | **63.36** | **76.92** | **49.29** | **63.87** |
| **CAMeLBERT-mix** | **Mean** | **74.74** | **76.76** | **78.08** | **69.38** | **61.04** | **75.91** | **47.24** | **59.98** |
| **CAMeLBERT-DA** | **Mean** | **73.69** | **75.21** | **76.91** | **68.96** | **61.02** | **76.00** | **46.20** | **60.87** |
| **ARBERT** | **Mean** | **75.32** | **79.74** | **79.11** | **67.11** | **61.49** | **76.64** | **47.38** | **60.46** |
| **ARBERTv2** | **Mean** | **75.08** | **78.81** | **78.82** | **67.61** | **61.79** | **76.84** | **46.11** | **62.43** |
| **Mean** | **All** | **76.03** | **78.98** | **79.14** | **69.97** | **62.42** | **77.05** | **47.55** | **62.67** |

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

**F1-PN, SR07** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 77.14 ± 0.89 | 76.85 ± 0.39 | 76.60 ± 0.20 | 71.15 ± 0.09 | 72.40 ± 1.23 | 71.58 ± 1.11 |
| MARBERT | 76.52 ± 0.37 | 77.34 ± 0.71 | 76.89 ± 0.31 | 71.93 ± 1.07 | 72.96 ± 1.07 | 71.65 ± 1.16 |
| AraBERTv02-Tw | 74.19 ± 0.82 | 74.12 ± 0.67 | 75.45 ± 0.43 | 69.00 ± 0.79 | 70.66 ± 1.39 | 69.52 ± 1.01 |
| CAMeLBERT-mix | 73.39 ± 0.44 | 73.10 ± 1.12 | 72.62 ± 0.50 | 68.57 ± 1.50 | 69.21 ± 1.02 | 67.96 ± 1.33 |
| CAMeLBERT-DA | 72.41 ± 0.35 | 71.50 ± 0.77 | 72.35 ± 0.84 | 67.77 ± 0.85 | 69.15 ± 1.09 | 67.81 ± 0.78 |
| ARBERT | 73.58 ± 1.21 | 73.29 ± 0.48 | 73.55 ± 0.90 | 67.97 ± 0.77 | 69.84 ± 0.62 | 67.97 ± 1.46 |
| ARBERTv2 | 72.82 ± 0.79 | 72.91 ± 0.71 | 72.31 ± 0.29 | 69.51 ± 1.86 | 70.03 ± 1.60 | 67.55 ± 0.68 |
| **Mean** | **74.29** | **74.16** | **74.25** | **69.41** | **70.61** | **69.15** |

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

**F1-PN, Δ SR07 − SR01** (+ = SG04 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.23 | -0.52 | -0.77 | -1.03 | +0.22 | -0.60 |
| MARBERT | -1.45 | -0.63 | -1.08 | -1.61 | -0.58 | -1.89 |
| AraBERTv02-Tw | -1.86 | -1.93 | -0.60 | -2.58 | -0.92 | -2.06 |
| CAMeLBERT-mix | -2.13 | -2.42 | -2.90 | -0.97 | -0.33 | -1.58 |
| CAMeLBERT-DA | -0.93 | -1.84 | -0.99 | -2.22 | -0.84 | -2.18 |
| ARBERT | -1.07 | -1.36 | -1.10 | -1.80 | +0.07 | -1.80 |
| ARBERTv2 | -0.90 | -0.81 | -1.41 | +0.23 | +0.75 | -1.73 |
| **Mean** | **-1.22** | **-1.36** | **-1.26** | **-1.43** | **-0.23** | **-1.69** |
| Better in | 0/7 | 0/7 | 0/7 | 1/7 | 3/7 | 0/7 |

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

**F1-PN, Δ SR07 − SR05** (+ = SG04 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | -0.66 | -0.64 | -1.50 | -0.29 | +0.49 | +0.14 |
| MARBERT | -0.87 | +0.17 | -0.56 | -0.28 | +1.45 | -0.52 |
| AraBERTv02-Tw | -2.40 | -2.07 | -0.23 | -1.00 | -0.72 | -0.57 |
| CAMeLBERT-mix | -1.70 | -0.86 | -1.30 | -0.21 | -0.45 | -0.50 |
| CAMeLBERT-DA | +0.27 | -0.34 | -0.26 | -0.25 | +0.82 | +0.19 |
| ARBERT | -1.05 | -0.30 | -0.95 | -0.41 | +0.01 | -0.32 |
| ARBERTv2 | -0.47 | -0.70 | -0.95 | +0.51 | -0.09 | -1.20 |
| **Mean** | **-0.98** | **-0.68** | **-0.82** | **-0.28** | **+0.22** | **-0.40** |
| Better in | 1/7 | 1/7 | 0/7 | 1/7 | 4/7 | 2/7 |

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

**F1-PN, Δ SR07 − SR06** (+ = SG04 better)

| BERT | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | +0.31 | +0.10 | -0.13 | -1.15 | +0.02 | +0.77 |
| MARBERT | -1.21 | +0.30 | -0.54 | -0.04 | +0.19 | -0.31 |
| AraBERTv02-Tw | -1.20 | -1.30 | +0.21 | -2.09 | +0.00 | +0.09 |
| CAMeLBERT-mix | +0.32 | -0.62 | +0.20 | +0.35 | +0.91 | +0.64 |
| CAMeLBERT-DA | +0.61 | -1.11 | +0.50 | -0.83 | +0.05 | +0.20 |
| ARBERT | -0.68 | +0.64 | +0.18 | -1.16 | +1.40 | -0.11 |
| ARBERTv2 | -0.95 | +0.07 | -0.72 | -1.12 | +0.33 | -1.02 |
| **Mean** | **-0.40** | **-0.27** | **-0.04** | **-0.86** | **+0.41** | **+0.04** |
| Better in | 3/7 | 4/7 | 4/7 | 1/7 | 6/7 | 4/7 |

**Summary over the 21 BERT × generator cells** (sign test, two-sided)

| Comparison | Dev | Test |
|---|---|---|
| SR07 − SR01 (real only) | -0.94 (better in 0/21, p = 0.000) | -1.29 (better in 1/21, p = 0.000) |
| SR07 − SR05 (SG03) | -0.66 (better in 3/21, p = 0.001) | -0.63 (better in 3/21, p = 0.001) |
| SR07 − SR06 (SG03-random) | -0.15 (better in 9/21, p = 0.664) | -0.79 (better in 2/21, p = 0.000) |

**F1-PN, summary over the 21 BERT × generator cells** (sign test, two-sided)

| Comparison | Dev | Test |
|---|---|---|
| SR07 − SR01 (real only) | -1.28 (better in 0/21, p = 0.000) | -1.12 (better in 4/21, p = 0.007) |
| SR07 − SR05 (SG03) | -0.83 (better in 2/21, p = 0.000) | -0.15 (better in 7/21, p = 0.189) |
| SR07 − SR06 (SG03-random) | -0.24 (better in 11/21, p = 1.000) | -0.14 (better in 11/21, p = 0.824) |

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

**F1-PN**

| Generator | Fidelity | Test F1-PN |
|---|---|---|
| Fanar | 81.3% | 69.41 |
| Qwen3 | 80.7% | 70.61 |
| Aya | 82.4% | 69.15 |

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

**All classifiers and classes, SR07 (S1 train + SG04)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.13 ± 0.50 | 81.68 | 80.11 | 72.60 | 62.49 ± 0.12 | 78.51 | 45.17 | 63.78 |
| MARBERTv2 | Qwen3 | 77.87 ± 0.49 | 81.21 | 79.91 | 72.50 | 63.22 ± 1.13 | 78.90 | 44.85 | 65.91 |
| MARBERTv2 | Aya | 77.76 ± 0.20 | 81.20 | 80.07 | 72.00 | 63.57 ± 0.84 | 77.95 | 47.56 | 65.21 |
| MARBERT | Fanar | 77.70 ± 0.36 | 80.21 | 80.04 | 72.83 | 63.36 ± 1.09 | 79.23 | 46.22 | 64.62 |
| MARBERT | Qwen3 | 78.37 ± 0.56 | 79.94 | 80.43 | 74.74 | 63.92 ± 0.76 | 79.39 | 45.84 | 66.52 |
| MARBERT | Aya | 77.88 ± 0.35 | 80.14 | 79.85 | 73.65 | 63.98 ± 1.02 | 78.10 | 48.62 | 65.21 |
| AraBERTv02-Tw | Fanar | 76.15 ± 0.54 | 79.58 | 80.08 | 68.80 | 61.62 ± 0.25 | 77.85 | 46.85 | 60.15 |
| AraBERTv02-Tw | Qwen3 | 76.03 ± 0.69 | 78.86 | 79.85 | 69.38 | 62.67 ± 0.96 | 78.06 | 46.68 | 63.26 |
| AraBERTv02-Tw | Aya | 76.91 ± 0.37 | 80.22 | 79.83 | 70.67 | 62.24 ± 0.72 | 77.16 | 47.69 | 61.87 |
| CAMeLBERT-mix | Fanar | 75.16 ± 0.27 | 77.63 | 78.70 | 69.16 | 60.33 ± 0.84 | 77.32 | 43.83 | 59.83 |
| CAMeLBERT-mix | Qwen3 | 74.83 ± 0.96 | 76.29 | 78.29 | 69.91 | 60.73 ± 0.66 | 76.97 | 43.75 | 61.46 |
| CAMeLBERT-mix | Aya | 74.57 ± 0.38 | 76.65 | 78.45 | 68.60 | 60.24 ± 0.89 | 77.05 | 44.79 | 58.86 |
| CAMeLBERT-DA | Fanar | 74.32 ± 0.30 | 75.35 | 78.14 | 69.48 | 60.32 ± 1.17 | 76.51 | 45.42 | 59.04 |
| CAMeLBERT-DA | Qwen3 | 73.50 ± 0.42 | 73.92 | 77.49 | 69.09 | 60.66 ± 0.44 | 77.08 | 43.66 | 61.23 |
| CAMeLBERT-DA | Aya | 74.21 ± 0.73 | 75.77 | 77.92 | 68.93 | 60.09 ± 0.97 | 75.96 | 44.64 | 59.67 |
| ARBERT | Fanar | 75.45 ± 0.80 | 80.46 | 79.17 | 66.71 | 60.32 ± 0.05 | 77.54 | 45.03 | 58.39 |
| ARBERT | Qwen3 | 75.16 ± 0.56 | 79.27 | 78.90 | 67.31 | 61.81 ± 0.26 | 77.17 | 45.75 | 62.51 |
| ARBERT | Aya | 75.50 ± 0.65 | 80.04 | 79.39 | 67.06 | 60.82 ± 0.61 | 77.50 | 46.52 | 58.43 |
| ARBERTv2 | Fanar | 74.72 ± 0.68 | 79.36 | 78.53 | 66.28 | 60.70 ± 1.08 | 78.43 | 43.07 | 60.59 |
| ARBERTv2 | Qwen3 | 74.75 ± 0.66 | 78.74 | 78.43 | 67.09 | 61.26 ± 0.90 | 77.44 | 43.71 | 62.62 |
| ARBERTv2 | Aya | 74.45 ± 0.33 | 79.18 | 78.72 | 65.44 | 59.98 ± 0.41 | 76.36 | 44.83 | 58.74 |
| **Mean** | **Fanar** | **75.95** | **79.18** | **79.25** | **69.41** | **61.31** | **77.91** | **45.08** | **60.91** |
| **Mean** | **Qwen3** | **75.79** | **78.32** | **79.04** | **70.00** | **62.04** | **77.86** | **44.89** | **63.36** |
| **Mean** | **Aya** | **75.90** | **79.03** | **79.18** | **69.48** | **61.56** | **77.15** | **46.38** | **61.14** |
| **MARBERTv2** | **Mean** | **77.92** | **81.36** | **80.03** | **72.37** | **63.09** | **78.45** | **45.86** | **64.97** |
| **MARBERT** | **Mean** | **77.98** | **80.10** | **80.11** | **73.74** | **63.75** | **78.91** | **46.89** | **65.45** |
| **AraBERTv02-Tw** | **Mean** | **76.36** | **79.55** | **79.92** | **69.62** | **62.18** | **77.69** | **47.07** | **61.76** |
| **CAMeLBERT-mix** | **Mean** | **74.85** | **76.86** | **78.48** | **69.22** | **60.43** | **77.11** | **44.12** | **60.05** |
| **CAMeLBERT-DA** | **Mean** | **74.01** | **75.01** | **77.85** | **69.17** | **60.36** | **76.52** | **44.57** | **59.98** |
| **ARBERT** | **Mean** | **75.37** | **79.92** | **79.15** | **67.03** | **60.98** | **77.40** | **45.77** | **59.78** |
| **ARBERTv2** | **Mean** | **74.64** | **79.09** | **78.56** | **66.27** | **60.65** | **77.41** | **43.87** | **60.65** |
| **Mean** | **All** | **75.88** | **78.84** | **79.16** | **69.63** | **61.63** | **77.64** | **45.45** | **61.80** |

# which part of SG04 caused the damage, and can we undo it without generating new data?

## SR08 on SG04
removed the 200 prayer pairs per generator. Errors on real POS prayers jumped in SR07, from 8.6% to 28.5%. SG04 taught "a prayer alone is NEU", but real prayers are mostly POS. We removed them to test whether this rule caused the damage.

**Takeaways**
- the prayer damage is almost gone, and the hard-case gain mostly stays. This confirms Finding 1. It also has 10% fewer synthetic texts, so size changed as well.

**All classifiers and classes, SR08 (S1 train + SG04 without prayer pairs)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.49 ± 0.39 | 81.07 | 80.70 | 73.69 | 63.54 ± 0.22 | 78.28 | 47.02 | 65.33 |
| MARBERTv2 | Qwen3 | 77.65 ± 0.36 | 80.45 | 80.04 | 72.47 | 63.65 ± 1.14 | 78.56 | 45.77 | 66.62 |
| MARBERTv2 | Aya | 78.16 ± 0.52 | 80.82 | 80.78 | 72.89 | 63.67 ± 0.73 | 77.31 | 47.88 | 65.80 |
| AraBERTv02-Tw | Fanar | 77.30 ± 0.28 | 79.69 | 80.51 | 71.70 | 63.20 ± 0.48 | 77.68 | 48.03 | 63.90 |
| AraBERTv02-Tw | Qwen3 | 76.52 ± 0.20 | 78.07 | 79.57 | 71.93 | 62.81 ± 0.27 | 76.73 | 47.01 | 64.69 |
| AraBERTv02-Tw | Aya | 77.90 ± 0.32 | 80.39 | 80.90 | 72.39 | 62.75 ± 0.94 | 76.61 | 48.17 | 63.46 |
| CAMeLBERT-mix | Fanar | 76.19 ± 0.66 | 77.99 | 79.66 | 70.93 | 60.96 ± 0.43 | 77.37 | 44.40 | 61.11 |
| CAMeLBERT-mix | Qwen3 | 75.75 ± 0.34 | 77.81 | 78.80 | 70.63 | 61.27 ± 0.63 | 77.50 | 43.72 | 62.58 |
| CAMeLBERT-mix | Aya | 75.67 ± 0.33 | 77.05 | 78.96 | 71.01 | 60.75 ± 0.92 | 76.82 | 44.89 | 60.54 |
| **Mean** | **Fanar** | **77.33** | **79.58** | **80.29** | **72.11** | **62.57** | **77.78** | **46.48** | **63.45** |
| **Mean** | **Qwen3** | **76.64** | **78.78** | **79.47** | **71.68** | **62.58** | **77.60** | **45.50** | **64.63** |
| **Mean** | **Aya** | **77.24** | **79.42** | **80.21** | **72.10** | **62.39** | **76.91** | **46.98** | **63.27** |
| **MARBERTv2** | **Mean** | **78.10** | **80.78** | **80.51** | **73.02** | **63.62** | **78.05** | **46.89** | **65.92** |
| **AraBERTv02-Tw** | **Mean** | **77.24** | **79.38** | **80.33** | **72.01** | **62.92** | **77.01** | **47.74** | **64.02** |
| **CAMeLBERT-mix** | **Mean** | **75.87** | **77.62** | **79.14** | **70.86** | **60.99** | **77.23** | **44.34** | **61.41** |
| **Mean** | **All** | **77.07** | **79.26** | **79.99** | **71.96** | **62.51** | **77.43** | **46.32** | **63.78** |

**F1-PN, SR08** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 77.38 ± 0.34 | 76.46 ± 0.39 | 76.86 ± 0.69 | 71.80 ± 0.71 | 72.59 ± 1.22 | 71.56 ± 1.02 |
| AraBERTv02-Tw | 75.70 ± 0.32 | 75.00 ± 0.21 | 76.39 ± 0.32 | 70.79 ± 0.91 | 70.71 ± 0.37 | 70.03 ± 1.16 |
| CAMeLBERT-mix | 74.46 ± 0.74 | 74.22 ± 0.42 | 74.03 ± 0.32 | 69.24 ± 0.61 | 70.04 ± 0.54 | 68.68 ± 0.55 |
| **Mean** | **75.85** | **75.23** | **75.76** | **70.61** | **71.11** | **70.09** |

**Was it useful? SR08 against SR07** (same 9 cells; Δ = mean change, cells better, sign test; judge on dev, test is leakage analysis; source `datasets/SG04/sg04_repair.md`)

| Measure | SR01 real only | SR07 | SR08 | Δ SR08 − SR07 |
|---|---|---|---|---|
| Dev macro F1 | 77.47 | 76.38 | 77.07 | +0.69 (8/9, p = 0.039) |
| Dev F1-PN | 76.31 | 74.83 | 75.61 | +0.78 (8/9, p = 0.039) |
| Test macro F1 | 63.14 | 61.90 | 62.51 | +0.61 (9/9, p = 0.004) |
| Test F1-PN | 71.10 | 70.01 | 70.60 | +0.60 (8/9, p = 0.039) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 24.5% | 9.7% | −14.8 pts |
| Test error, hard cases | 83.4% | 80.2% | 81.3% | +1.1 pts |
| Test error, other tweets | 9.2% | 11.7% | 11.0% | −0.7 pts |

**Useful: better than SR07 on dev and test, and the prayer error is back near SR01. Still below real only.**

## SR09 on SG04
removes the 116/2000 Qwen3 pairs where A and B have the same words. Qwen3 only. with only "!" or an emoji different, yet they carried opposite labels. That is label noise, so we tested whether it was hurting the classifiers.

**Takeaways**
- no clear effect. With only 3 cells, it can't show much either way.

**All classifiers and classes, SR09 (S1 train + SG04 Qwen3 without same-word pairs)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Qwen3 | 77.64 ± 0.48 | 80.58 | 80.06 | 72.29 | 63.14 ± 0.24 | 78.05 | 45.97 | 65.40 |
| AraBERTv02-Tw | Qwen3 | 76.77 ± 0.12 | 79.34 | 79.72 | 71.25 | 62.14 ± 0.24 | 77.40 | 46.09 | 62.93 |
| CAMeLBERT-mix | Qwen3 | 75.70 ± 1.20 | 77.40 | 78.47 | 71.22 | 60.76 ± 0.16 | 77.48 | 43.20 | 61.61 |
| **Mean** | **Qwen3** | **76.70** | **79.11** | **79.42** | **71.59** | **62.01** | **77.64** | **45.09** | **63.31** |

**F1-PN, SR09** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Qwen3 | Test Qwen3 |
|---|---|---|
| MARBERTv2 | 76.43 ± 0.68 | 71.72 ± 0.17 |
| AraBERTv02-Tw | 75.29 ± 0.22 | 70.17 ± 0.48 |
| CAMeLBERT-mix | 74.31 ± 1.71 | 69.54 ± 0.60 |
| **Mean** | **75.34** | **70.48** |

**Was it useful? SR09 against SR07** (same 3 cells: Qwen3 only; Δ = mean change, cells better, sign test; judge on dev, test is leakage analysis; source `datasets/SG04/sg04_repair.md`)

| Measure | SR01 real only | SR07 (Qwen3) | SR09 | Δ SR09 − SR07 |
|---|---|---|---|---|
| Dev macro F1 | 77.47 | 76.24 | 76.70 | +0.46 (2/3, p = 1.00) |
| Dev F1-PN | 76.31 | 74.69 | 75.34 | +0.65 (2/3, p = 1.00) |
| Test macro F1 | 63.14 | 62.20 | 62.01 | −0.19 (1/3, p = 1.00) |
| Test F1-PN | 71.10 | 70.76 | 70.48 | −0.28 (1/3, p = 1.00) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 18.1% | 16.2% | −1.9 pts |
| Test error, hard cases | 83.4% | 77.9% | 79.4% | +1.5 pts |
| Test error, other tweets | 9.2% | 12.2% | 12.1% | −0.1 pts |

**Not shown useful: small dev gain, small test loss, and 3 cells cannot show either.**

## SR10 on SG04
same data, but the last epoch uses real tweets only. SG04 fixed some hard cases but broke more ordinary tweets. A last epoch on real data might remind the model of normal tweets, while keeping what it learned from SG04.

**Takeaways**
-  it protects ordinary tweets best, but gives up most of the hard-case gain. The worry from earlier didn't hold: dev picked the real-only epoch in 23 of 27 runs.

**All classifiers and classes, SR10 (S1 train + SG04, two-stage training)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.17 ± 0.57 | 81.47 | 80.19 | 72.85 | 62.86 ± 0.33 | 78.58 | 45.58 | 64.43 |
| MARBERTv2 | Qwen3 | 78.64 ± 0.87 | 81.22 | 80.81 | 73.89 | 63.14 ± 0.23 | 78.79 | 45.17 | 65.46 |
| MARBERTv2 | Aya | 78.27 ± 0.58 | 81.37 | 80.21 | 73.23 | 63.61 ± 0.25 | 78.25 | 46.86 | 65.72 |
| AraBERTv02-Tw | Fanar | 76.71 ± 0.42 | 79.79 | 80.07 | 70.28 | 62.99 ± 0.26 | 77.51 | 48.35 | 63.12 |
| AraBERTv02-Tw | Qwen3 | 76.13 ± 0.43 | 78.55 | 79.60 | 70.24 | 63.20 ± 0.53 | 77.34 | 48.08 | 64.19 |
| AraBERTv02-Tw | Aya | 77.48 ± 0.46 | 80.88 | 80.12 | 71.46 | 62.94 ± 0.21 | 77.34 | 48.61 | 62.86 |
| CAMeLBERT-mix | Fanar | 75.57 ± 0.22 | 77.17 | 78.86 | 70.68 | 61.56 ± 0.49 | 76.78 | 46.62 | 61.28 |
| CAMeLBERT-mix | Qwen3 | 75.64 ± 0.64 | 76.42 | 78.44 | 72.04 | 61.67 ± 0.33 | 76.74 | 46.18 | 62.10 |
| CAMeLBERT-mix | Aya | 75.17 ± 0.25 | 76.34 | 78.82 | 70.35 | 61.00 ± 0.11 | 76.47 | 46.05 | 60.48 |
| **Mean** | **Fanar** | **76.82** | **79.48** | **79.71** | **71.27** | **62.47** | **77.62** | **46.85** | **62.94** |
| **Mean** | **Qwen3** | **76.80** | **78.73** | **79.62** | **72.06** | **62.67** | **77.62** | **46.48** | **63.92** |
| **Mean** | **Aya** | **76.97** | **79.53** | **79.72** | **71.68** | **62.52** | **77.35** | **47.17** | **63.02** |
| **MARBERTv2** | **Mean** | **78.36** | **81.35** | **80.40** | **73.32** | **63.20** | **78.54** | **45.87** | **65.20** |
| **AraBERTv02-Tw** | **Mean** | **76.77** | **79.74** | **79.93** | **70.66** | **63.04** | **77.40** | **48.35** | **63.39** |
| **CAMeLBERT-mix** | **Mean** | **75.46** | **76.64** | **78.71** | **71.02** | **61.41** | **76.66** | **46.28** | **61.29** |
| **Mean** | **All** | **76.86** | **79.25** | **79.68** | **71.67** | **62.55** | **77.53** | **46.83** | **63.29** |

**F1-PN, SR10** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 77.16 ± 0.83 | 77.55 ± 0.86 | 77.30 ± 0.57 | 71.50 ± 0.56 | 72.12 ± 0.90 | 71.99 ± 0.35 |
| AraBERTv02-Tw | 75.04 ± 0.56 | 74.39 ± 0.62 | 76.17 ± 0.50 | 70.32 ± 0.28 | 70.77 ± 0.50 | 70.10 ± 0.33 |
| CAMeLBERT-mix | 73.92 ± 0.19 | 74.23 ± 0.93 | 73.34 ± 0.45 | 69.03 ± 0.45 | 69.42 ± 0.63 | 68.47 ± 0.28 |
| **Mean** | **75.37** | **75.39** | **75.60** | **70.28** | **70.77** | **70.19** |

**Was it useful? SR10 against SR07** (same 9 cells; Δ = mean change, cells better, sign test; judge on dev, test is leakage analysis; source `datasets/SG04/sg04_repair.md`)

| Measure | SR01 real only | SR07 | SR10 | Δ SR10 − SR07 |
|---|---|---|---|---|
| Dev macro F1 | 77.47 | 76.38 | 76.86 | +0.49 (9/9, p = 0.004) |
| Dev F1-PN | 76.31 | 74.83 | 75.46 | +0.63 (9/9, p = 0.004) |
| Test macro F1 | 63.14 | 61.90 | 62.55 | +0.65 (8/9, p = 0.039) |
| Test F1-PN | 71.10 | 70.01 | 70.41 | +0.41 (8/9, p = 0.039) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 24.5% | 17.3% | −7.2 pts |
| Test error, hard cases | 83.4% | 80.2% | 82.1% | +1.9 pts |
| Test error, other tweets | 9.2% | 11.7% | 10.6% | −1.1 pts |

**Useful: better than SR07 in every cell on dev, but the dev gain is smaller than SR08's and most of the hard-case gain is lost. Still below real only.**

## SR11
both the SR08 and SR10 changes: the prayer rule and the loss on ordinary tweets. We combined them to see whether their gains add up. They didn't.

| Run (same 3 BERTs) | Dev macro F1 | Test macro F1 | Dev vs SR07 | Test vs SR07 |
|---|---|---|---|---|
| SR01 real only | 77.47 | 63.14 | | |
| SR07 SG04 | 76.38 | 61.90 | | |
| **SR08 no prayer pairs** | **77.07** | 62.51 | +0.69 (better in 8/9) | +0.61 (9/9) |
| **SR10 two-stage** | 76.86 | **62.55** | +0.49 (9/9) | +0.65 (8/9) |
| SR09 no same-word pairs* | 76.70 | 62.01 | +0.46 (2/3) | −0.19 (1/3) |

**F1-PN, same 3 BERTs** (Δ against SR07: mean, better in, sign test)

| Run | Dev F1-PN | Test F1-PN | Dev vs SR07 | Test vs SR07 |
|---|---|---|---|---|
| SR01 real only | 76.31 | 71.10 |  |  |
| SR07 | 74.83 | 70.01 |  |  |
| SR08 no prayer pairs | 75.61 | 70.60 | +0.78 (8/9, p = 0.039) | +0.60 (8/9, p = 0.039) |
| SR10 two-stage | 75.46 | 70.41 | +0.63 (9/9, p = 0.004) | +0.41 (8/9, p = 0.039) |
| SR09 no same-word pairs (SR07 on the same cells: 74.69 / 70.76) | 75.34 | 70.48 | +0.65 (2/3, p = 1.00) | −0.28 (1/3, p = 1.00) |
| SR11 no prayer pairs + two-stage | 75.67 | 70.61 | +0.84 (8/9, p = 0.039) | +0.60 (8/9, p = 0.039) |

| Test error rate | SR01 | SR07 | SR08 | SR10 |
|---|---|---|---|---|
| Gold POS with a religious cue | 8.0% | 24.5% | **9.7%** | 17.3% |
| Hard cases | 83.4% | 80.2% | 81.3% | 82.1% |
| Other tweets | 9.2% | 11.7% | 11.0% | **10.6%** |

**All classifiers and classes, SR11 (S1 train + SG04 without prayer pairs, two-stage training)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.06 ± 0.44 | 80.61 | 79.91 | 73.66 | 63.39 ± 0.34 | 78.34 | 46.81 | 65.03 |
| MARBERTv2 | Qwen3 | 77.54 ± 0.15 | 80.30 | 80.22 | 72.10 | 63.19 ± 0.27 | 77.88 | 46.06 | 65.64 |
| MARBERTv2 | Aya | 78.27 ± 0.59 | 81.56 | 80.77 | 72.48 | 64.05 ± 0.68 | 77.90 | 48.14 | 66.11 |
| AraBERTv02-Tw | Fanar | 77.47 ± 0.38 | 80.51 | 80.65 | 71.24 | 63.01 ± 0.71 | 77.75 | 47.20 | 64.07 |
| AraBERTv02-Tw | Qwen3 | 76.46 ± 0.55 | 78.29 | 79.66 | 71.44 | 63.13 ± 0.40 | 76.96 | 47.85 | 64.58 |
| AraBERTv02-Tw | Aya | 77.77 ± 0.19 | 80.25 | 80.36 | 72.70 | 63.14 ± 0.17 | 76.96 | 48.44 | 64.03 |
| CAMeLBERT-mix | Fanar | 76.37 ± 0.26 | 78.13 | 79.53 | 71.45 | 61.29 ± 0.76 | 77.48 | 44.90 | 61.51 |
| CAMeLBERT-mix | Qwen3 | 75.97 ± 0.11 | 77.79 | 78.86 | 71.26 | 60.93 ± 0.64 | 77.18 | 43.62 | 61.99 |
| CAMeLBERT-mix | Aya | 75.77 ± 0.26 | 77.31 | 79.02 | 70.99 | 60.92 ± 0.79 | 77.10 | 45.20 | 60.46 |
| **Mean** | **Fanar** | **77.30** | **79.75** | **80.03** | **72.12** | **62.56** | **77.86** | **46.30** | **63.54** |
| **Mean** | **Qwen3** | **76.66** | **78.79** | **79.58** | **71.60** | **62.42** | **77.34** | **45.84** | **64.07** |
| **Mean** | **Aya** | **77.27** | **79.71** | **80.05** | **72.06** | **62.70** | **77.32** | **47.26** | **63.53** |
| **MARBERTv2** | **Mean** | **77.96** | **80.82** | **80.30** | **72.75** | **63.54** | **78.04** | **47.00** | **65.59** |
| **AraBERTv02-Tw** | **Mean** | **77.23** | **79.68** | **80.22** | **71.79** | **63.09** | **77.22** | **47.83** | **64.23** |
| **CAMeLBERT-mix** | **Mean** | **76.04** | **77.74** | **79.14** | **71.23** | **61.05** | **77.25** | **44.57** | **61.32** |
| **Mean** | **All** | **77.08** | **79.42** | **79.89** | **71.92** | **62.56** | **77.51** | **46.47** | **63.71** |

**F1-PN, SR11** (official metric: mean F1 of POS and NEG; mean ± std over seeds)

| Classifier | Dev Fanar | Dev Qwen3 | Dev Aya | Test Fanar | Test Qwen3 | Test Aya |
|---|---|---|---|---|---|---|
| MARBERTv2 | 77.14 ± 0.38 | 76.20 ± 0.15 | 77.02 ± 0.81 | 71.68 ± 0.19 | 71.76 ± 0.31 | 72.01 ± 0.79 |
| AraBERTv02-Tw | 75.88 ± 0.57 | 74.87 ± 0.74 | 76.47 ± 0.19 | 70.91 ± 0.52 | 70.77 ± 0.50 | 70.49 ± 0.13 |
| CAMeLBERT-mix | 74.79 ± 0.26 | 74.52 ± 0.21 | 74.15 ± 0.29 | 69.49 ± 0.19 | 69.58 ± 0.52 | 68.78 ± 0.32 |
| **Mean** | **75.94** | **75.20** | **75.88** | **70.69** | **70.70** | **70.43** |

**Was it useful? SR11 against its two parts, SR08 and SR10** (same 9 cells; Δ = mean change, cells better, sign test, computed from the per-cell tables above; judge on dev, test is leakage analysis)

| Measure | SR01 real only | SR08 | SR10 | SR11 | Δ SR11 − SR08 | Δ SR11 − SR10 |
|---|---|---|---|---|---|---|
| Dev macro F1 | 77.47 | 77.07 | 76.86 | 77.08 | +0.01 (5/9, p = 1.00) | +0.21 (6/9, p = 0.51) |
| Dev F1-PN | 76.31 | 75.61 | 75.46 | 75.67 | +0.06 (6/9, p = 0.51) | +0.22 (6/9, p = 0.51) |
| Test macro F1 | 63.14 | 62.51 | 62.55 | 62.56 | +0.05 (5/9, p = 1.00) | +0.01 (5/9, p = 1.00) |
| Test F1-PN | 71.10 | 70.60 | 70.41 | 70.61 | +0.00 (6/9, p = 0.51) | +0.19 (7/9, p = 0.18) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 9.7% | 17.3% | 9.3% | −0.4 pts | −8.0 pts |
| Test error, hard cases | 83.4% | 81.3% | 82.1% | 82.1% | +0.8 pts | 0.0 pts |
| Test error, other tweets | 9.2% | 11.0% | 10.6% | 10.5% | −0.5 pts | −0.1 pts |

**Not useful: SR11 scores the same as SR08 alone, so adding the two-stage step on top brings nothing clear.**

## SR12

**All classifiers and classes, SR12 (S1 train + SG04 POS/NEG pairs only, two-stage training)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.22 ± 0.41 | 81.31 | 79.84 | 73.51 | 62.77 ± 0.52 | 77.73 | 45.62 | 64.96 |
| MARBERTv2 | Qwen3 | 78.06 ± 0.81 | 80.57 | 80.04 | 73.58 | 63.09 ± 0.72 | 76.89 | 47.25 | 65.13 |
| MARBERTv2 | Aya | 78.82 ± 0.39 | 81.21 | 80.37 | 74.89 | 63.56 ± 0.47 | 78.42 | 46.32 | 65.93 |
| AraBERTv02-Tw | Fanar | 77.72 ± 0.57 | 80.03 | 79.95 | 73.17 | 62.96 ± 0.61 | 77.69 | 47.27 | 63.92 |
| AraBERTv02-Tw | Qwen3 | 77.37 ± 0.14 | 80.01 | 80.10 | 72.01 | 62.96 ± 1.22 | 78.35 | 45.57 | 64.95 |
| AraBERTv02-Tw | Aya | 78.02 ± 0.61 | 80.20 | 80.25 | 73.60 | 63.30 ± 0.07 | 77.47 | 48.09 | 64.34 |
| CAMeLBERT-mix | Fanar | 76.08 ± 0.24 | 78.23 | 78.79 | 71.23 | 61.63 ± 0.83 | 77.80 | 44.60 | 62.50 |
| CAMeLBERT-mix | Qwen3 | 76.07 ± 0.27 | 77.86 | 78.73 | 71.61 | 61.87 ± 1.10 | 77.41 | 45.61 | 62.60 |
| CAMeLBERT-mix | Aya | 76.57 ± 0.11 | 78.95 | 79.28 | 71.49 | 61.37 ± 0.95 | 77.29 | 45.39 | 61.42 |
| **Mean** | **Fanar** | **77.34** | **79.86** | **79.53** | **72.64** | **62.45** | **77.74** | **45.83** | **63.79** |
| **Mean** | **Qwen3** | **77.17** | **79.48** | **79.62** | **72.40** | **62.64** | **77.55** | **46.14** | **64.23** |
| **Mean** | **Aya** | **77.80** | **80.12** | **79.97** | **73.33** | **62.74** | **77.73** | **46.60** | **63.90** |
| **MARBERTv2** | **Mean** | **78.37** | **81.03** | **80.08** | **73.99** | **63.14** | **77.68** | **46.40** | **65.34** |
| **AraBERTv02-Tw** | **Mean** | **77.70** | **80.08** | **80.10** | **72.93** | **63.07** | **77.84** | **46.98** | **64.40** |
| **CAMeLBERT-mix** | **Mean** | **76.24** | **78.35** | **78.93** | **71.44** | **61.62** | **77.50** | **45.20** | **62.17** |
| **Mean** | **All** | **77.44** | **79.82** | **79.71** | **72.79** | **62.61** | **77.67** | **46.19** | **63.97** |

**Was it useful? SR12 against SR11** (same 9 cells; Δ = mean change, cells better, sign test; judge on dev, test is leakage analysis; source `datasets/SG04/sg04_repair.md` and the per-cell tables above)

| Measure | SR01 real only | SR11 | SR12 | Δ SR12 − SR11 |
|---|---|---|---|---|
| Synthetic texts | 0 | 3,600 | 1,600 | −2,000 |
| Dev macro F1 | 77.47 | 77.08 | 77.44 | +0.36 (8/9, p = 0.039) |
| Dev F1-PN | 76.31 | 75.67 | 76.30 | +0.63 (8/9, p = 0.039) |
| Test macro F1 | 63.14 | 62.56 | 62.61 | +0.05 (4/9, p = 1.00) |
| Test F1-PN | 71.10 | 70.61 | 70.82 | +0.21 (6/9, p = 0.51) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 9.3% | 8.6% | −0.7 pts |
| Test error, all gold POS | 23.5% | 24.5% | 21.9% | −2.6 pts |
| Test error, hard cases | 83.4% | 82.1% | 81.9% | −0.2 pts |
| Test error, other tweets | 9.2% | 10.5% | 10.2% | −0.3 pts |

**Useful on dev: better than SR11 in 8 of 9 cells, and level with real only (−0.03). Test does not move. Size also falls, so content and size are not separated.**

## SR13

**All classifiers and classes, SR13 (S1 train + SG04 POS/NEG pairs + NEG sides of jab and remark, two-stage training)**

| Classifier | Generator | Dev macro F1 | Dev NEG | Dev NEU | Dev POS | Test macro F1 | Test NEG | Test NEU | Test POS |
|---|---|---|---|---|---|---|---|---|---|
| MARBERTv2 | Fanar | 78.23 ± 0.24 | 81.01 | 80.16 | 73.53 | 63.03 ± 0.57 | 77.70 | 45.85 | 65.55 |
| MARBERTv2 | Qwen3 | 77.54 ± 0.69 | 80.25 | 79.87 | 72.50 | 63.31 ± 0.24 | 77.14 | 47.20 | 65.58 |
| MARBERTv2 | Aya | 78.23 ± 0.39 | 81.55 | 80.25 | 72.90 | 63.73 ± 0.26 | 79.14 | 45.49 | 66.57 |
| AraBERTv02-Tw | Fanar | 78.15 ± 0.58 | 79.64 | 80.57 | 74.24 | 63.47 ± 0.38 | 77.69 | 47.98 | 64.72 |
| AraBERTv02-Tw | Qwen3 | 77.17 ± 0.24 | 79.20 | 79.69 | 72.62 | 63.23 ± 0.12 | 78.25 | 46.26 | 65.19 |
| AraBERTv02-Tw | Aya | 78.03 ± 0.60 | 80.07 | 80.52 | 73.50 | 63.41 ± 0.16 | 77.68 | 47.82 | 64.73 |
| CAMeLBERT-mix | Fanar | 75.99 ± 0.05 | 77.45 | 78.84 | 71.68 | 62.11 ± 0.17 | 77.59 | 46.28 | 62.46 |
| CAMeLBERT-mix | Qwen3 | 76.13 ± 0.79 | 77.45 | 78.97 | 71.96 | 62.39 ± 0.43 | 77.65 | 46.89 | 62.63 |
| CAMeLBERT-mix | Aya | 76.01 ± 0.50 | 77.60 | 78.88 | 71.54 | 61.81 ± 0.43 | 77.13 | 45.94 | 62.35 |
| **Mean** | **Fanar** | **77.46** | **79.37** | **79.86** | **73.15** | **62.87** | **77.66** | **46.70** | **64.24** |
| **Mean** | **Qwen3** | **76.95** | **78.97** | **79.51** | **72.36** | **62.98** | **77.68** | **46.78** | **64.47** |
| **Mean** | **Aya** | **77.42** | **79.74** | **79.88** | **72.65** | **62.98** | **77.98** | **46.42** | **64.55** |
| **MARBERTv2** | **Mean** | **78.00** | **80.94** | **80.09** | **72.98** | **63.36** | **77.99** | **46.18** | **65.90** |
| **AraBERTv02-Tw** | **Mean** | **77.78** | **79.64** | **80.26** | **73.45** | **63.37** | **77.87** | **47.35** | **64.88** |
| **CAMeLBERT-mix** | **Mean** | **76.04** | **77.50** | **78.90** | **71.73** | **62.10** | **77.46** | **46.37** | **62.48** |
| **Mean** | **All** | **77.28** | **79.36** | **79.75** | **72.72** | **62.94** | **77.77** | **46.63** | **64.42** |

**Was it useful? SR13 against SR12** (same 9 cells; the only change is the 1,000 NEG sides of public jab and personal remark; Δ = mean change, cells better, sign test; judge on dev, test is leakage analysis; source `datasets/SG04/sg04_repair.md` and the per-cell tables above)

| Measure | SR01 real only | SR12 | SR13 | Δ SR13 − SR12 |
|---|---|---|---|---|
| Synthetic texts | 0 | 1,600 | 2,600 | +1,000 |
| Dev macro F1 | 77.47 | 77.44 | 77.28 | −0.16 (4/9, p = 1.00) |
| Dev F1-PN | 76.31 | 76.30 | 76.04 | −0.26 (1/9, p = 0.039) |
| Test macro F1 | 63.14 | 62.61 | 62.94 | +0.33 (9/9, p = 0.004) |
| Test F1-PN | 71.10 | 70.82 | 71.10 | +0.28 (8/9, p = 0.039) |
| Test error, gold POS with religious cue (lower is better) | 8.0% | 8.6% | 9.2% | +0.6 pts |
| Test error, all gold POS | 23.5% | 21.9% | 23.3% | +1.4 pts |
| Test error, hard cases | 83.4% | 81.9% | 81.7% | −0.2 pts |
| Test error, other tweets | 9.2% | 10.2% | 10.0% | −0.2 pts |
| Test gold NEU predicted NEG | 38.2% | 38.4% | 39.2% | +0.8 pts |

**Not useful on dev: F1-PN falls in 8 of 9 cells. Test rises in every cell, but test is leakage analysis, so it does not count.**

# Interpretation of the F1-PN changes, SR01–SR13

**Question:** how does F1-PN (mean of POS F1 and NEG F1, NEU ignored) change from SR01 to SR13, and why?

Numbers come from the tables in this file. The SR01 7-BERT means, the per-class changes and the "gap closed" shares are computed from them. They match the summaries above (for example SR07 − SR01 = −1.28 dev, −1.12 test). From SR07 on, test columns are leakage analysis.

## Part 1: synthetic sets against real only (7 BERTs, 21 cells)

| Run | Dev F1-PN | Δ dev | Test F1-PN | Δ test | Test Δ NEG F1 | Test Δ POS F1 |
|---|---|---|---|---|---|---|
| SR01 real only | 75.52 | | 70.84 | | | |
| SR02 + SG01 (zero-shot) | 75.78 | +0.26 | 71.08 | +0.24 | −0.10 | +0.58 |
| SR04 + SG02 (one-shot) | 75.26 | −0.26 | 70.66 | −0.18 | −0.51 | +0.14 |
| SR05 + SG03 (targeted pairs) | 75.06 | −0.46 | 69.88 | −0.96 | −0.17 | −1.76 |
| SR06 + SG03-random | 74.47 | −1.05 | 69.86 | −0.98 | −0.55 | −1.41 |
| SR07 + SG04 | 74.23 | −1.29 | 69.72 | −1.12 | +0.04 | −2.28 |

**1. The F1-PN loss is a POS loss.**
- Test NEG F1 stays within about ±0.5 in every run.
- POS F1 carries the change: in SR07 the whole −1.12 comes from POS (−2.28 / 2).
- The error tables agree: gold POS error rises from 23.8% to 30.2%, and POS → NEU is the error that grows most.
- On dev, POS also falls most (SR07: POS −1.87, NEG −0.69).

**2. The pair format is what costs F1-PN, not the targeting.**
- The open and one-shot sets (SG01, SG02) stay within noise.
- All three pair sets (SG03, SG03-random, SG04) lose about 1 point.
- The random pairs lose as much as the targeted ones on test (−0.98 against −0.96).

**3. Targeting helps on dev only.**
- SR05 − SR06 is +0.59 on dev (better in 18/21) and +0.02 on test.
- What targeting teaches does not carry over to the test distribution.

**4. SG04's extra damage is in NEU, not in POS/NEG.**
- SR07 − SR06: macro F1 on test is −0.79 (better in 2/21), but F1-PN is only −0.14 (11/21).
- SR07 − SR05 shows the same pattern: macro −0.63, F1-PN −0.15.
- So SG04 hurts POS/NEG no more than random pairs do. Its additional loss sits in the NEU class, which F1-PN does not count.

**5. No set beats real only beyond noise.**
- SR02 is the only run above SR01 (+0.26 / +0.24).
- That is smaller than the seed spread, for example SR01 MARBERTv2 test ± 1.58.

## Part 2: the SG04 repairs (3 BERTs, 9 cells)

"Gap closed" = share of the SR07 → SR01 gap that the run recovers.

| Run | Dev F1-PN | Gap closed (dev) | Test F1-PN | Gap closed (test) | Test POS F1 |
|---|---|---|---|---|---|
| SR01 real only | 76.31 | 100% | 71.10 | 100% | 64.45 |
| SR07 SG04 | 74.83 | 0% | 70.01 | 0% | 62.26 |
| SR08 no prayer pairs | 75.61 | 53% | 70.60 | 54% | 63.78 |
| SR09 no same-word pairs (3 cells) | 75.34 | n/a | 70.48 | n/a | 63.31 |
| SR10 two-stage | 75.46 | 43% | 70.41 | 37% | 63.29 |
| SR11 SR08 + SR10 | 75.67 | 57% | 70.61 | 55% | 63.71 |
| SR12 no NEU generations | 76.30 | 99% | 70.82 | 74% | 63.97 |
| SR13 SR12 + NEG sides | 76.04 | 82% | 71.10 | 100% | 64.42 |

**6. Recovering F1-PN means recovering POS.**
- Test NEG F1 stays at 77.4–77.8 in every repair run.
- Test POS F1 climbs from 62.26 back to 64.42.

**7. The prayer pairs explain about half of the gap.**
- SR08 closes 53–54%.
- Two-stage training (SR10) closes less (37–43%).
- Combining them (SR11) adds almost nothing: 55–57%.

**8. Removing the NEU generations closes the dev gap fully.**
- SR12 reaches 76.30 against 76.31.
- The set also shrinks from 3,600 to 1,600 texts, so content and size are not separated.
- Dev F1-PN rises as the set shrinks, so "less SG04" may simply be "closer to real only".

**9. SR13 is where dev and test disagree.**
- Adding the 1,000 NEG sides lowers dev F1-PN (−0.26, better in 1/9) through dev NEG F1 (−0.46).
- Test F1-PN reaches SR01 exactly (71.10) through POS.
- Judged on dev, SR13 brings no benefit.

**10. F1-PN makes the repairs look more complete than they are.**
- SR13 ties SR01 on test F1-PN, but its test macro F1 is still −0.20.
- The difference is NEU (46.63 against 47.23), which F1-PN hides.
- SR12 shows the same: test NEU −1.04 and worse in all 9 cells.

## Other patterns

- **Generator:** in SR07, Qwen3 is the only set near SR01 on test (70.61, against 69.41 for Fanar and 69.15 for Aya). Qwen3 is also the only generator that made true minimal pairs (word overlap 0.62).
- **Fidelity:** it does not predict F1-PN. Aya has the highest fidelity (82.4%) and the lowest test F1-PN.
- **LLM classifiers:** Jais-2 is the strongest on real only (79.87 / 74.74). Adding SG01 lowers it slightly (test 73.27–74.40), within its spread.
- **Dev–test gap:** about 5 F1-PN points in every run, against about 13 for macro F1. Most of the test difficulty is in NEU (test NEU F1 about 47).
- **SR03:** NEU is dropped, so its F1-PN is a 2-class score and cannot be compared with the others.

## Caveats
- **Seeds:** only 3 per cell.
- **Shared baseline:** the SR01 baseline is shared across generator cells, so the cells are not independent.
- **Test leakage:** from SR07 on, SG04 was built from test hard cases, so those test columns are leakage analysis.

**Takeaway: in F1-PN terms, synthetic data at best does no harm and never helps. Every loss is a loss on POS, mostly from the pair format, and in SG04 above all from the prayer pairs. The best repair (SR12) gets dev back to real only, but in the same step the synthetic set shrinks to under half its size. SR12 and SR13 hide a remaining NEU loss that only macro F1 shows.**
