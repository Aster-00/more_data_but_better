## Dataset for Sentiment Analysis (EESA)
EESA-Corpus: Egyptian Arabic-English code-switched comments, labelled positive / negative / neutral. Most comments are YouTube comments on Egyptian songs, music videos, TV ads, films, series and TV shows. Source `data/datasets/sa/EESA-Corpus-main/` (official train / dev / test, no header row). Built by `python -m src.sentiment.build_eesa` (data versions E1 test, E2 train and dev; `docs/sentiment/data.md`).

| Split | Texts | NEG / NEU / POS |
|---|---|---|
| Train | 2,463 | 594 / 778 / 1,091 |
| Dev | 818 | 197 / 258 / 363 |
| Test | 818 | 197 / 258 / 363 |

### Here are it's annotation guidelines
TODO: the README does not give the annotation guidelines; take them from the EESA paper (not checked yet, nothing here is invented).

What the labels look like in EESA train and dev (my keyword rules, 3,282 texts; observed, not the official guidelines):
- Insulting the people who pressed dislike is NEG (42 of 42 such comments).
- Channel promotion ("subscribe to my channel", links) is mostly NEU (82%).
- "Who loves X, press like" is mostly NEU (72%).
- Saying a song is copied ("مسروقة من ...") is mostly NEG (72%).
- Greetings from another country are almost always POS (97%).

### Script and code-switching (quality row 8 rules, all 4,100 texts)
- 98.7% of texts contain at least one Latin-script word.
- Script: 63.7% Arabic script, 33.5% mixed, 2.8% Arabizi.
- In the Arabic-script texts: 74.3% light code-switching, 23.7% heavy, 2.0% none; 1.6 Latin words per text on average (13.8% of the words).
- The English is mostly platform words (dislike, like, subscribe, views), short praise (love, nice, wow) and names (BTS, we, Tamer).

### Topics (universal E5 list, D-019)
- Only 61% of texts get a topic: 1,488 texts are not Arabic script and were never in the pool, 107 have under 5 words.
- Of those, 53.1% fall in unnamed clusters; Films, TV, music and celebrities is 23.2%, Greetings 4.9%, Love and feelings 4.7%.
- The unnamed clusters are largely "dislike" comments (C17 53%, C16 50%, C44 44%).

## SX01: models trained on ArSarcasm-v2, scored on EESA test
No retraining (D-028). Test macro F1, mean ± std over seeds.

| Classifier | Trained on | Seeds | EESA test macro F1 | F1 NEG | F1 NEU | F1 POS |
|---|---|---|---|---|---|---|
| jais2 | ArSarcasm-v2 | 3 | 84.20 ± 1.32 | 85.60 | 77.12 | 89.87 |
| fanar | ArSarcasm-v2 | 1 | 83.93 ± 0.00 | 83.98 | 77.50 | 90.32 |
| aya | ArSarcasm-v2 | 3 | 81.67 ± 1.83 | 82.42 | 74.02 | 88.56 |
| marbert | ArSarcasm-v2 | 3 | 81.33 ± 0.54 | 80.56 | 73.81 | 89.62 |
| marbertv2 | ArSarcasm-v2 | 3 | 79.83 ± 1.74 | 79.06 | 72.97 | 87.46 |
| falcon_h1 | ArSarcasm-v2 | 1 | 79.91 ± 0.00 | 80.60 | 72.05 | 87.08 |
| qwen3 | ArSarcasm-v2 | 1 | 78.28 ± 0.00 | 78.00 | 70.73 | 86.11 |
| arabertv02_twitter | ArSarcasm-v2 | 3 | 76.12 ± 0.92 | 74.43 | 69.99 | 83.93 |
| camelbert_mix | ArSarcasm-v2 | 3 | 73.20 ± 0.32 | 69.56 | 67.82 | 82.21 |
| arbert | ArSarcasm-v2 | 3 | 75.84 ± 0.54 | 73.11 | 69.29 | 85.12 |
| arbertv2 | ArSarcasm-v2 | 3 | 75.61 ± 0.73 | 72.83 | 69.67 | 84.33 |
| camelbert_da | ArSarcasm-v2 | 3 | 69.82 ± 0.91 | 66.22 | 64.24 | 79.01 |

## SR01-EESA baseline run, real data only
EESA train only, 7 BERTs, 3 seeds, SR01 recipe; EESA dev chooses the epoch, EESA test scored once.

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR01-EESA-marbert | dev | `sr01_eesa_marbert` | 3 | 88.33 | 88.30 | 88.85 | 0.14 | 89.20 | 86.89 | 84.30 | 93.82 |
| SR01-EESA-marbert | test | `sr01_eesa_marbert` | 3 | 87.89 | 87.92 | 87.99 | 0.28 | 88.88 | 85.76 | 84.03 | 93.87 |
| SR01-EESA-marbertv2 | dev | `sr01_eesa_marbertv2` | 3 | 85.90 | 85.84 | 86.46 | 0.41 | 86.84 | 84.88 | 80.83 | 91.98 |
| SR01-EESA-marbertv2 | test | `sr01_eesa_marbertv2` | 3 | 85.09 | 84.93 | 85.51 | 0.46 | 86.06 | 83.62 | 80.16 | 91.49 |
| SR01-EESA-arbert | dev | `sr01_eesa_arbert` | 3 | 83.96 | 83.92 | 84.26 | 0.66 | 84.88 | 82.15 | 80.00 | 89.72 |
| SR01-EESA-arbert | test | `sr01_eesa_arbert` | 3 | 83.20 | 83.14 | 83.31 | 0.29 | 84.39 | 79.57 | 79.55 | 90.47 |
| SR01-EESA-arabertv02_twitter | dev | `sr01_eesa_arabertv02_twitter` | 3 | 83.33 | 83.16 | 83.63 | 1.36 | 84.39 | 80.87 | 78.80 | 90.32 |
| SR01-EESA-arabertv02_twitter | test | `sr01_eesa_arabertv02_twitter` | 3 | 83.36 | 83.32 | 83.50 | 0.98 | 84.27 | 80.90 | 79.64 | 89.54 |
| SR01-EESA-camelbert_mix | dev | `sr01_eesa_camelbert_mix` | 3 | 81.99 | 82.13 | 82.38 | 0.45 | 83.13 | 79.00 | 78.23 | 88.73 |
| SR01-EESA-camelbert_mix | test | `sr01_eesa_camelbert_mix` | 3 | 80.28 | 80.34 | 80.45 | 0.32 | 81.58 | 75.44 | 77.74 | 87.65 |
| SR01-EESA-arbertv2 | dev | `sr01_eesa_arbertv2` | 3 | 80.13 | 81.41 | 80.52 | 0.97 | 81.54 | 79.54 | 73.39 | 87.45 |
| SR01-EESA-arbertv2 | test | `sr01_eesa_arbertv2` | 3 | 80.85 | 81.58 | 80.84 | 0.87 | 82.36 | 78.15 | 75.50 | 88.88 |
| SR01-EESA-camelbert_da | dev | `sr01_eesa_camelbert_da` | 3 | 79.53 | 79.59 | 79.65 | 0.04 | 80.68 | 76.18 | 75.53 | 86.88 |
| SR01-EESA-camelbert_da | test | `sr01_eesa_camelbert_da` | 3 | 79.20 | 79.47 | 79.61 | 0.74 | 80.20 | 74.71 | 77.03 | 85.86 |

**SX01 vs SR01-EESA** (EESA test macro F1, same BERTs)

| BERT | Trained on ArSarcasm-v2 (SX01) | Trained on EESA (SR01-EESA) | Δ |
|---|---|---|---|
| marbert | 81.33 | 87.89 | +6.56 |
| marbertv2 | 79.83 | 85.09 | +5.26 |
| arabertv02_twitter | 76.12 | 83.36 | +7.24 |
| arbert | 75.84 | 83.20 | +7.36 |
| arbertv2 | 75.61 | 80.85 | +5.24 |
| camelbert_mix | 73.20 | 80.28 | +7.08 |
| camelbert_da | 69.82 | 79.20 | +9.38 |
| **mean of 7** | 75.96 | 82.84 | +6.87 |

**Takeaways**
- 

**Future Runs**
- SG01-EESA: zero-shot generation for EESA (prompt `prompts/sentiment/open_eesa_v1.json`, accepted 2026-11-08), 1,320 per generator, code-switched like EESA; then SR02-EESA
- SG03-EESA and SG03-random-EESA: minimal pairs for the types of the SR02-EESA dev errors; then SR05-EESA and SR06-EESA

## SR02-EESA-XFER, SR05-EESA-XFER, SR06-EESA-XFER (stopped, not EESA results)
EESA train + subsets of the ArSarcasm-v2 generations (SG01 1,320 texts; SG03 and SG03-random 880 texts). Stopped 2026-11-08 07:08, because the synthetic data must be generated for EESA (D-032). Seed 42 only, MARBERTv2 and MARBERT only. Renamed from `sr0N_eesa_*` (`results/sentiment/renames_2026-11-08.json`).

**SR02-EESA-XFER** (+ SG01 subset)

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR02-EESA-XFER-marbert_aya | dev | `sr02_eesaxfer_marbert_aya` | 1 | 89.59 | 89.41 | 89.83 | – | 90.10 | 88.89 | 86.79 | 93.09 |
| SR02-EESA-XFER-marbert_aya | test | `sr02_eesaxfer_marbert_aya` | 1 | 88.50 | 88.38 | 88.65 | – | 89.24 | 87.28 | 84.71 | 93.52 |
| SR02-EESA-XFER-marbert_qwen3 | dev | `sr02_eesaxfer_marbert_qwen3` | 1 | 89.19 | 88.95 | 89.59 | – | 89.98 | 87.38 | 85.88 | 94.31 |
| SR02-EESA-XFER-marbert_qwen3 | test | `sr02_eesaxfer_marbert_qwen3` | 1 | 87.52 | 87.67 | 87.39 | – | 88.39 | 85.93 | 83.59 | 93.04 |
| SR02-EESA-XFER-marbertv2_qwen3 | dev | `sr02_eesaxfer_marbertv2_qwen3` | 1 | 86.69 | 86.72 | 87.13 | – | 87.65 | 85.71 | 81.57 | 92.77 |
| SR02-EESA-XFER-marbertv2_qwen3 | test | `sr02_eesaxfer_marbertv2_qwen3` | 1 | 84.55 | 84.48 | 84.72 | – | 85.70 | 81.08 | 81.20 | 91.36 |
| SR02-EESA-XFER-marbertv2_fanar | dev | `sr02_eesaxfer_marbertv2_fanar` | 1 | 86.35 | 86.31 | 87.05 | – | 87.29 | 85.31 | 81.33 | 92.41 |
| SR02-EESA-XFER-marbertv2_fanar | test | `sr02_eesaxfer_marbertv2_fanar` | 1 | 85.63 | 85.35 | 86.09 | – | 86.43 | 85.02 | 80.48 | 91.39 |
| SR02-EESA-XFER-marbertv2_aya | dev | `sr02_eesaxfer_marbertv2_aya` | 1 | 86.26 | 86.11 | 87.07 | – | 87.16 | 85.19 | 81.24 | 92.35 |
| SR02-EESA-XFER-marbertv2_aya | test | `sr02_eesaxfer_marbertv2_aya` | 1 | 85.66 | 85.33 | 86.37 | – | 86.55 | 83.76 | 81.36 | 91.85 |

**SR05-EESA-XFER** (+ SG03 subset)

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR05-EESA-XFER-marbert_aya | dev | `sr05_eesaxfer_marbert_aya` | 1 | 88.74 | 88.92 | 89.21 | – | 89.61 | 87.26 | 84.94 | 94.01 |
| SR05-EESA-XFER-marbert_aya | test | `sr05_eesaxfer_marbert_aya` | 1 | 86.49 | 86.68 | 86.57 | – | 87.53 | 84.52 | 82.38 | 92.58 |
| SR05-EESA-XFER-marbert_qwen3 | dev | `sr05_eesaxfer_marbert_qwen3` | 1 | 88.50 | 88.68 | 88.91 | – | 89.36 | 87.41 | 84.34 | 93.75 |
| SR05-EESA-XFER-marbert_qwen3 | test | `sr05_eesaxfer_marbert_qwen3` | 1 | 86.29 | 86.45 | 86.24 | – | 87.41 | 84.21 | 81.69 | 92.97 |
| SR05-EESA-XFER-marbertv2_qwen3 | dev | `sr05_eesaxfer_marbertv2_qwen3` | 1 | 86.90 | 86.88 | 87.33 | – | 87.78 | 85.92 | 82.30 | 92.48 |
| SR05-EESA-XFER-marbertv2_qwen3 | test | `sr05_eesaxfer_marbertv2_qwen3` | 1 | 83.88 | 83.80 | 83.98 | – | 84.96 | 81.00 | 80.00 | 90.63 |
| SR05-EESA-XFER-marbertv2_fanar | dev | `sr05_eesaxfer_marbertv2_fanar` | 1 | 85.86 | 85.90 | 86.55 | – | 86.92 | 84.65 | 80.33 | 92.58 |
| SR05-EESA-XFER-marbertv2_fanar | test | `sr05_eesaxfer_marbertv2_fanar` | 1 | 85.00 | 84.83 | 85.35 | – | 86.06 | 81.84 | 81.60 | 91.56 |
| SR05-EESA-XFER-marbertv2_aya | dev | `sr05_eesaxfer_marbertv2_aya` | 1 | 85.80 | 85.84 | 86.53 | – | 86.80 | 84.92 | 80.33 | 92.16 |
| SR05-EESA-XFER-marbertv2_aya | test | `sr05_eesaxfer_marbertv2_aya` | 1 | 85.16 | 84.91 | 85.77 | – | 86.06 | 82.74 | 81.69 | 91.06 |

**SR06-EESA-XFER** (+ SG03-random subset)

| id | split | folder | seeds | macro_f1 | macro_precision | macro_recall | macro_recall_std | accuracy | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR06-EESA-XFER-marbert_aya | dev | `sr06_eesaxfer_marbert_aya` | 1 | 89.05 | 88.84 | 89.60 | – | 89.73 | 88.10 | 85.43 | 93.63 |
| SR06-EESA-XFER-marbert_aya | test | `sr06_eesaxfer_marbert_aya` | 1 | 87.26 | 87.16 | 87.48 | – | 88.14 | 85.50 | 83.43 | 92.86 |
| SR06-EESA-XFER-marbert_qwen3 | dev | `sr06_eesaxfer_marbert_qwen3` | 1 | 88.19 | 88.16 | 88.55 | – | 89.00 | 87.02 | 84.25 | 93.30 |
| SR06-EESA-XFER-marbert_qwen3 | test | `sr06_eesaxfer_marbert_qwen3` | 1 | 86.94 | 87.42 | 86.70 | – | 88.02 | 84.85 | 83.03 | 92.94 |
| SR06-EESA-XFER-marbertv2_fanar | dev | `sr06_eesaxfer_marbertv2_fanar` | 1 | 86.86 | 86.71 | 87.59 | – | 87.65 | 86.45 | 81.89 | 92.24 |
| SR06-EESA-XFER-marbertv2_fanar | test | `sr06_eesaxfer_marbertv2_fanar` | 1 | 85.90 | 85.65 | 86.52 | – | 86.80 | 84.16 | 81.62 | 91.92 |
| SR06-EESA-XFER-marbertv2_qwen3 | dev | `sr06_eesaxfer_marbertv2_qwen3` | 1 | 86.15 | 86.13 | 86.71 | – | 87.04 | 85.38 | 81.16 | 91.91 |
| SR06-EESA-XFER-marbertv2_qwen3 | test | `sr06_eesaxfer_marbertv2_qwen3` | 1 | 84.87 | 84.72 | 85.40 | – | 85.82 | 82.94 | 80.65 | 91.01 |
| SR06-EESA-XFER-marbertv2_aya | dev | `sr06_eesaxfer_marbertv2_aya` | 1 | 85.91 | 85.76 | 86.76 | – | 86.80 | 84.99 | 80.82 | 91.92 |
| SR06-EESA-XFER-marbertv2_aya | test | `sr06_eesaxfer_marbertv2_aya` | 1 | 86.00 | 85.74 | 86.75 | – | 86.80 | 84.58 | 81.95 | 91.47 |
