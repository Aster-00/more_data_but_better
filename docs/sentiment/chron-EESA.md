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


**Takeaways**
- 

**Future Runs**
- SG01-EESA: zero-shot generation for EESA (prompt `prompts/sentiment/open_eesa_v1.json`, accepted 2026-11-08), 1,320 per generator, code-switched like EESA; then SR02-EESA
- SG03-EESA and SG03-random-EESA: minimal pairs for the types of the SR02-EESA dev errors; then SR05-EESA and SR06-EESA

## SR02-EASA results (EASA test macro F1, mean ± std over 3 seeds)

| BERT | SR01-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 87.89 ± 0.29 | 87.65 (−0.24) | 87.59 (−0.30) | 87.35 (−0.54) |
| MARBERTv2 | 85.09 ± 0.32 | 85.55 (+0.45) | 85.56 (+0.46) | 84.86 (−0.23) |
| AraBERTv02-Twitter | 83.36 ± 1.07 | 83.86 (+0.50) | 83.43 (+0.07) | 83.24 (−0.12) |
| ARBERT | 83.20 ± 0.46 | 83.85 (+0.65) | 82.65 (−0.55) | 83.39 (+0.19) |
| ARBERTv2 | 80.85 ± 0.85 | 81.91 (+1.07) | 81.44 (+0.60) | 82.12 (+1.28) |
| CAMeLBERT-mix | 80.28 ± 0.12 | 81.37 (+1.10) | 81.53 (+1.25) | 81.63 (+1.35) |
| CAMeLBERT-DA | 79.20 ± 0.49 | 79.80 (+0.60) | 80.81 (+1.60) | 81.17 (+1.97) |
| **Mean of 7** | **82.84** | **83.43 (+0.59)** | **83.29 (+0.45)** | **83.39 (+0.56)** |

- **Breadth:** Aya improves 6 of 7 BERTs, Fanar 5 and Qwen3 4.
- **Where it helps:** the gain grows as the BERT gets weaker. The best BERT, MARBERT, gets slightly worse with every set.
- **By class:** test NEU F1 rises by 0.73–1.05.

**Takeaway: EESA-generated data adds about +0.5 on average, which is roughly the size of the seed spread. It helps the weak BERTs by 1–2 points and does nothing for MARBERT.**
