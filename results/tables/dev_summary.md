# MLADI dev set (120 sentences, 8 dialects), threshold 0.3

## R01: Published LahjatBERT models, downloaded and scored (not trained by us)

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R01-lahjatbert_cl_cardinality | 1 | 72.68 | 68.98 | 80.64 | 73.07 | 72.68 | `Mohamedelzeftawy__LahjatBERT_cl_cardinality` |
| R01-lahjatbert_cl_aldi | 1 | 70.27 | 71.35 | 71.32 | 70.93 | 70.27 | `Mohamedelzeftawy__LahjatBERT_cl_aldi` |
| R01-lahjatbert_baseline | 1 | 67.41 | 73.66 | 63.66 | 67.86 | 67.41 | `Mohamedelzeftawy__LahjatBERT_baseline` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R01-lahjatbert_cl_cardinality | 59.3 | 83.7 | 71.2 | 71.1 | 69.8 | 66.1 | 77.3 | 83.1 |
| R01-lahjatbert_cl_aldi | 58.2 | 83.7 | 67.9 | 69.6 | 75.9 | 69.9 | 65.2 | 71.7 |
| R01-lahjatbert_baseline | 55.6 | 86.1 | 65.3 | 65.6 | 69.6 | 63.9 | 63.4 | 69.8 |

## R03: Real only (condition 1), D1, our settings: dropout 0.3, 2 epochs, macro-F1 epoch selection, threshold 0.3

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R03-marbert | 3 | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 | 70.65 / 72.52 / 70.84 | `baseline_real_only` |
| R03-arabertv02_twitter | 3 | 70.52 ± 0.52 | 69.15 ± 1.34 | 75.12 ± 0.30 | 71.99 ± 0.66 | 70.80 / 70.83 / 69.92 | `baseline_real_only_arabertv02_twitter` |
| R03-marbertv2 | 3 | 70.11 ± 0.55 | 70.94 ± 1.15 | 71.62 ± 0.90 | 69.81 ± 0.32 | 70.00 / 69.62 / 70.70 | `baseline_real_only_marbertv2` |
| R03-tfidf_lr | 3 | 62.58 ± 0.05 | 65.83 ± 1.27 | 62.28 ± 0.54 | 63.91 ± 0.07 | 62.52 / 62.59 / 62.62 | `baseline_real_only_tfidf_lr` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R03-marbert | 62.0 | 86.4 | 67.1 | 72.3 | 72.2 | 68.4 | 71.0 | 71.3 |
| R03-arabertv02_twitter | 57.6 | 78.7 | 70.9 | 76.0 | 70.5 | 68.0 | 66.2 | 76.3 |
| R03-marbertv2 | 69.4 | 80.2 | 67.5 | 70.3 | 63.3 | 69.2 | 74.0 | 67.1 |
| R03-tfidf_lr | 46.9 | 78.7 | 60.4 | 66.2 | 53.8 | 63.6 | 61.7 | 69.3 |

## R04: Real only, D1, LahjatBERT's settings: dropout 0.1, 3 epochs, micro-F1 epoch selection

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R04-marbert | 3 | 68.71 ± 0.35 | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.12 ± 0.35 | 69.00 / 68.81 / 68.32 | `repro_lahjatbert_baseline` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R04-marbert | 54.8 | 87.2 | 64.5 | 69.8 | 67.9 | 65.5 | 70.0 | 70.0 |

## R05: Real only, D2 (D1 without zero-label and all-18 texts), otherwise identical to R03

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R05-arabertv02_twitter | 3 | 69.82 ± 0.65 | 69.60 ± 0.61 | 73.80 ± 1.54 | 71.89 ± 0.69 | 69.47 / 70.58 / 69.43 | `card1to17_real_only_arabertv02_twitter` |
| R05-marbert | 3 | 69.25 ± 0.54 | 72.53 ± 0.56 | 68.40 ± 1.39 | 70.53 ± 0.62 | 69.81 / 68.72 / 69.20 | `card1to17_real_only` |
| R05-marbertv2 | 3 | 64.89 ± 1.44 | 69.07 ± 0.51 | 64.27 ± 2.45 | 66.33 ± 1.34 | 64.47 / 66.49 / 63.71 | `card1to17_real_only_marbertv2` |
| R05-tfidf_lr | 3 | 56.54 ± 0.82 | 65.95 ± 0.44 | 53.43 ± 0.63 | 59.64 ± 0.74 | 56.14 / 56.00 / 57.49 | `card1to17_real_only_tfidf_lr` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R05-arabertv02_twitter | 56.0 | 78.8 | 72.5 | 76.2 | 69.7 | 67.1 | 61.1 | 77.2 |
| R05-marbert | 54.1 | 85.4 | 68.5 | 71.7 | 73.3 | 71.6 | 60.2 | 69.1 |
| R05-marbertv2 | 52.3 | 79.0 | 64.4 | 70.0 | 56.5 | 67.3 | 62.0 | 67.7 |
| R05-tfidf_lr | 28.0 | 76.8 | 58.4 | 64.0 | 46.2 | 60.2 | 52.6 | 66.2 |

## R06: Real only, D3 (D1 without all-18 texts; zero-label kept), otherwise identical to R03

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R06-arabertv02_twitter | 3 | 69.27 ± 0.60 | 68.82 ± 0.58 | 73.13 ± 0.72 | 71.02 ± 0.53 | 69.46 / 69.75 / 68.60 | `card0to17_real_only_arabertv02_twitter` |
| R06-marbert | 3 | 67.11 ± 1.13 | 69.68 ± 1.46 | 67.36 ± 0.87 | 68.71 ± 0.74 | 66.28 / 68.40 / 66.64 | `card0to17_real_only` |
| R06-marbertv2 | 3 | 66.29 ± 1.21 | 69.29 ± 1.01 | 66.60 ± 1.49 | 67.50 ± 1.13 | 66.80 / 67.16 / 64.91 | `card0to17_real_only_marbertv2` |
| R06-tfidf_lr | 3 | 56.27 ± 0.64 | 68.02 ± 0.94 | 51.77 ± 1.00 | 59.11 ± 0.65 | 55.80 / 57.00 / 56.00 | `card0to17_real_only_tfidf_lr` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R06-arabertv02_twitter | 55.7 | 78.0 | 71.4 | 74.2 | 70.0 | 66.1 | 62.2 | 76.5 |
| R06-marbert | 51.9 | 82.5 | 66.7 | 70.9 | 71.1 | 66.2 | 56.9 | 70.6 |
| R06-marbertv2 | 52.2 | 78.7 | 67.1 | 69.2 | 62.7 | 68.3 | 64.0 | 68.1 |
| R06-tfidf_lr | 27.5 | 74.4 | 56.3 | 62.0 | 45.7 | 60.1 | 55.3 | 68.8 |

## R07: Real only, D4 (D1 without zero-label texts; all-18 kept), otherwise identical to R03

| ID | Seeds | Macro F1 | Precision | Recall | Micro F1 | F1 per seed | Result folder |
|---|---|---|---|---|---|---|---|
| R07-marbert | 3 | 72.17 ± 0.75 | 72.02 ± 2.11 | 74.05 ± 0.74 | 71.94 ± 0.73 | 72.96 / 72.09 / 71.46 | `card1to18_real_only` |
| R07-arabertv02_twitter | 3 | 70.74 ± 0.52 | 69.35 ± 0.45 | 75.34 ± 0.98 | 71.83 ± 0.45 | 70.61 / 70.31 / 71.32 | `card1to18_real_only_arabertv02_twitter` |
| R07-marbertv2 | 3 | 69.79 ± 0.56 | 70.38 ± 1.08 | 71.52 ± 0.83 | 69.94 ± 0.53 | 69.51 / 69.41 / 70.43 | `card1to18_real_only_marbertv2` |
| R07-tfidf_lr | 3 | 62.70 ± 1.00 | 64.13 ± 1.09 | 63.49 ± 0.95 | 63.95 ± 0.83 | 63.81 / 61.86 / 62.41 | `card1to18_real_only_tfidf_lr` |

Per-dialect F1 (mean over seeds):

| ID | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| R07-marbert | 65.1 | 85.1 | 67.3 | 70.2 | 74.6 | 69.6 | 73.9 | 71.6 |
| R07-arabertv02_twitter | 60.1 | 78.4 | 71.8 | 74.3 | 69.7 | 66.5 | 68.2 | 76.9 |
| R07-marbertv2 | 67.4 | 81.0 | 68.3 | 70.6 | 62.0 | 70.9 | 70.9 | 67.2 |
| R07-tfidf_lr | 48.0 | 75.6 | 61.0 | 66.0 | 56.6 | 64.8 | 60.8 | 68.7 |
