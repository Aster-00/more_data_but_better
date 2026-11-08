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


## SR01-EESA baseline run, real data only
EESA train only, 7 BERTs, 3 seeds, SR01 recipe; EESA dev chooses the epoch, EESA test scored once.

| id | split | folder | seeds | micro_f1 | macro_f1 | macro_precision | macro_recall | macro_recall_std | f1_NEG | f1_NEU | f1_POS |
|---|---|---|---|---|---|---|---|---|---|---|---|
| SR01-EESA-marbert | dev | `sr01_eesa_marbert` | 3 | 89.20 | 88.33 | 88.30 | 88.85 | 0.14 | 86.89 | 84.30 | 93.82 |
| SR01-EESA-marbert | test | `sr01_eesa_marbert` | 3 | 88.88 | 87.89 | 87.92 | 87.99 | 0.28 | 85.76 | 84.03 | 93.87 |
| SR01-EESA-marbertv2 | dev | `sr01_eesa_marbertv2` | 3 | 86.84 | 85.90 | 85.84 | 86.46 | 0.41 | 84.88 | 80.83 | 91.98 |
| SR01-EESA-marbertv2 | test | `sr01_eesa_marbertv2` | 3 | 86.06 | 85.09 | 84.93 | 85.51 | 0.46 | 83.62 | 80.16 | 91.49 |
| SR01-EESA-arbert | dev | `sr01_eesa_arbert` | 3 | 84.88 | 83.96 | 83.92 | 84.26 | 0.66 | 82.15 | 80.00 | 89.72 |
| SR01-EESA-arbert | test | `sr01_eesa_arbert` | 3 | 84.39 | 83.20 | 83.14 | 83.31 | 0.29 | 79.57 | 79.55 | 90.47 |
| SR01-EESA-arabertv02_twitter | dev | `sr01_eesa_arabertv02_twitter` | 3 | 84.39 | 83.33 | 83.16 | 83.63 | 1.36 | 80.87 | 78.80 | 90.32 |
| SR01-EESA-arabertv02_twitter | test | `sr01_eesa_arabertv02_twitter` | 3 | 84.27 | 83.36 | 83.32 | 83.50 | 0.98 | 80.90 | 79.64 | 89.54 |
| SR01-EESA-camelbert_mix | dev | `sr01_eesa_camelbert_mix` | 3 | 83.13 | 81.99 | 82.13 | 82.38 | 0.45 | 79.00 | 78.23 | 88.73 |
| SR01-EESA-camelbert_mix | test | `sr01_eesa_camelbert_mix` | 3 | 81.58 | 80.28 | 80.34 | 80.45 | 0.32 | 75.44 | 77.74 | 87.65 |
| SR01-EESA-arbertv2 | dev | `sr01_eesa_arbertv2` | 3 | 81.54 | 80.13 | 81.41 | 80.52 | 0.97 | 79.54 | 73.39 | 87.45 |
| SR01-EESA-arbertv2 | test | `sr01_eesa_arbertv2` | 3 | 82.36 | 80.85 | 81.58 | 80.84 | 0.87 | 78.15 | 75.50 | 88.88 |
| SR01-EESA-camelbert_da | dev | `sr01_eesa_camelbert_da` | 3 | 80.68 | 79.53 | 79.59 | 79.65 | 0.04 | 76.18 | 75.53 | 86.88 |
| SR01-EESA-camelbert_da | test | `sr01_eesa_camelbert_da` | 3 | 80.20 | 79.20 | 79.47 | 79.61 | 0.74 | 74.71 | 77.03 | 85.86 |

**SX01 vs SR01-EESA** (EESA test, same BERTs; micro F1 from `sentiment_summary_EESA.csv` `accuracy`, mean of 7 computed from those rows)

| BERT | Micro F1, trained on ArSarcasm-v2 (SX01) | Micro F1, trained on EESA (SR01-EESA) | Δ micro | Macro F1, SX01 | Macro F1, SR01-EESA | Δ macro |
|---|---|---|---|---|---|---|
| marbert | 82.64 | 88.88 | +6.24 | 81.33 | 87.89 | +6.56 |
| marbertv2 | 81.01 | 86.06 | +5.05 | 79.83 | 85.09 | +5.26 |
| arabertv02_twitter | 77.14 | 84.27 | +7.13 | 76.12 | 83.36 | +7.24 |
| arbert | 77.26 | 84.39 | +7.13 | 75.84 | 83.20 | +7.36 |
| arbertv2 | 77.14 | 82.36 | +5.22 | 75.61 | 80.85 | +5.24 |
| camelbert_mix | 74.53 | 81.58 | +7.05 | 73.20 | 80.28 | +7.08 |
| camelbert_da | 71.15 | 80.20 | +9.05 | 69.82 | 79.20 | +9.38 |
| **mean of 7** | 77.27 | 83.96 | +6.70 | 75.96 | 82.84 | +6.87 |

**Takeaways**
- 

**Future Runs**
- SG01-EESA: zero-shot generation for EESA (prompt `prompts/sentiment/open_eesa_v1.json`, accepted 2026-11-08), 1,320 per generator, code-switched like EESA; then SR02-EESA
- SG03-EESA and SG03-random-EESA: minimal pairs for the types of the SR02-EESA dev errors; then SR05-EESA and SR06-EESA
