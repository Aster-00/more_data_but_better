# MLADI dev set (120 sentences, 8 dialects), threshold 0.3

| Model | Seeds | Macro F1 | Precision | Recall | Micro F1 |
|---|---|---|---|---|---|
| Mohamedelzeftawy__LahjatBERT_cl_cardinality | 1 | 72.68 | 68.98 | 80.64 | 73.07 |
| baseline_real_only | 3 | 71.34 ± 1.03 | 71.67 ± 2.54 | 72.98 ± 0.40 | 71.54 ± 0.76 |
| baseline_real_only_arabertv02_twitter | 3 | 70.52 ± 0.52 | 69.15 ± 1.34 | 75.12 ± 0.30 | 71.99 ± 0.66 |
| Mohamedelzeftawy__LahjatBERT_cl_aldi | 1 | 70.27 | 71.35 | 71.32 | 70.93 |
| baseline_real_only_marbertv2 | 3 | 70.11 ± 0.55 | 70.94 ± 1.15 | 71.62 ± 0.90 | 69.81 ± 0.32 |
| repro_lahjatbert_baseline | 3 | 68.71 ± 0.35 | 74.89 ± 1.48 | 65.49 ± 0.59 | 69.12 ± 0.35 |
| Mohamedelzeftawy__LahjatBERT_baseline | 1 | 67.41 | 73.66 | 63.66 | 67.86 |
| baseline_real_only_tfidf_lr | 3 | 62.58 ± 0.05 | 65.83 ± 1.27 | 62.28 ± 0.54 | 63.91 ± 0.07 |

Per-dialect F1 (mean over seeds):

| Model | Algeria | Egypt | Jordan | Palestine | Sudan | Syria | Tunisia | Yemen |
|---|---|---|---|---|---|---|---|---|
| Mohamedelzeftawy__LahjatBERT_cl_cardinality | 59.3 | 83.7 | 71.2 | 71.1 | 69.8 | 66.1 | 77.3 | 83.1 |
| baseline_real_only | 62.0 | 86.4 | 67.1 | 72.3 | 72.2 | 68.4 | 71.0 | 71.3 |
| baseline_real_only_arabertv02_twitter | 57.6 | 78.7 | 70.9 | 76.0 | 70.5 | 68.0 | 66.2 | 76.3 |
| Mohamedelzeftawy__LahjatBERT_cl_aldi | 58.2 | 83.7 | 67.9 | 69.6 | 75.9 | 69.9 | 65.2 | 71.7 |
| baseline_real_only_marbertv2 | 69.4 | 80.2 | 67.5 | 70.3 | 63.3 | 69.2 | 74.0 | 67.1 |
| repro_lahjatbert_baseline | 54.8 | 87.2 | 64.5 | 69.8 | 67.9 | 65.5 | 70.0 | 70.0 |
| Mohamedelzeftawy__LahjatBERT_baseline | 55.6 | 86.1 | 65.3 | 65.6 | 69.6 | 63.9 | 63.4 | 69.8 |
| baseline_real_only_tfidf_lr | 46.9 | 78.7 | 60.4 | 66.2 | 53.8 | 63.6 | 61.7 | 69.3 |
