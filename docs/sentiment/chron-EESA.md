The main metric for this dataset i Micro-f1
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

## SR02-EASA results (EASA test micro F1; BERTs: mean ± std over 3 seeds; LLMs: seed 42 only)

| Classifier | SR01-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.88 ± 0.32 | 88.43 (−0.45) | 88.22 (−0.66) | 88.22 (−0.66) |
| MARBERTv2 | 86.06 ± 0.32 | 86.23 (+0.17) | 86.35 (+0.29) | 85.82 (−0.24) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.60 (+0.33) | 84.15 (−0.12) | 84.03 (−0.24) |
| ARBERT | 84.39 ± 0.46 | 84.80 (+0.41) | 83.58 (−0.81) | 84.47 (+0.08) |
| ARBERTv2 | 82.36 ± 0.79 | 82.89 (+0.53) | 82.36 (+0.00) | 83.41 (+1.05) |
| CAMeLBERT-mix | 81.58 ± 0.07 | 82.60 (+1.02) | 82.68 (+1.10) | 82.76 (+1.18) |
| CAMeLBERT-DA | 80.20 ± 0.61 | 80.60 (+0.40) | 81.50 (+1.30) | 81.91 (+1.71) |
| **Mean of 7 BERTs** | **83.96** | **84.31 (+0.34)** | **84.12 (+0.16)** | **84.37 (+0.41)** |
| Fanar (LLM) | 91.56 | 91.44 (−0.12) | – | 91.81 (+0.25) |
| Jais-2 (LLM) | 91.08 | 91.69 (+0.61) | 91.32 (+0.24) | 89.73 (−1.35) |
| Aya (LLM) | 89.24 | – | 89.73 (+0.49) | 88.88 (−0.36) |
| Qwen3 (LLM) | 86.43 | 89.36 (+2.93) | 88.39 (+1.96) | – |
| Falcon-H1 (LLM) | 81.05 | 85.33 (+4.28) | 85.70 (+4.65) | 85.33 (+4.28) |
| **Mean change, 5 LLMs** | | **+1.92** | **+1.84** | **+0.71** |

LLM rows (QLoRA, seed 42 only; – = the LLM's own set): these are the SR03-EASA runs. The dev rule picks the same epoch in all 17, so the scores are the same; they are discussed under SR03-EASA.

- **Breadth:** Aya improves 6 of 7 BERTs, Qwen3 4 and Fanar 3.
- **Where it helps:** the gain grows as the BERT gets weaker (CAMeLBERT-mix +1.0 to +1.2, CAMeLBERT-DA +0.4 to +1.7). The best BERT, MARBERT, gets worse with every set (−0.45 to −0.66).
- **By class:** test NEU F1 rises by 0.73–1.05.

**Takeaway: EESA-generated data adds +0.2 to +0.4 micro F1 on average, which is no more than the seed spread. It helps the two weakest BERTs by about 1 point and lowers MARBERT.**

## SR03-EASA results: epoch chosen by training loss (EASA test micro F1; BERTs: mean ± std over 3 seeds; LLMs: seed 42 only)
SR01-EASA and SR02-EASA rerun with one change: the epoch with the lowest training loss is kept, not the best dev macro F1 (D-035). Every run kept the last epoch (3). Registry run SR03-EESA (folders `sr01_eesa_tl_*`, `sr02_eesa_tl_*`); the old runs are kept.

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.67 (+0.00) | 88.43 (−0.24) | 88.22 (−0.45) |
| MARBERTv2 | 86.06 ± 0.32 | 86.59 (+0.53) | 86.47 (+0.41) | 86.10 (+0.04) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.60 (+0.33) | 84.52 (+0.25) | 84.03 (−0.24) |
| ARBERT | 84.39 ± 0.46 | 84.80 (+0.41) | 84.47 (+0.08) | 84.80 (+0.41) |
| ARBERTv2 | 82.36 ± 0.79 | 82.93 (+0.57) | 83.09 (+0.73) | 83.41 (+1.05) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 83.01 (+1.18) | 82.89 (+1.06) | 82.76 (+0.93) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 81.70 (+0.20) | 82.31 (+0.81) | 82.44 (+0.94) |
| **Mean of 7 BERTs** | **84.15** | **84.61 (+0.46)** | **84.60 (+0.44)** | **84.54 (+0.38)** |
| Fanar (LLM) | 91.56 | 91.44 (−0.12) | – | 91.81 (+0.25) |
| Jais-2 (LLM) | 91.08 | 91.69 (+0.61) | 91.32 (+0.24) | 89.73 (−1.35) |
| Aya (LLM) | 89.24 | – | 89.73 (+0.49) | 88.88 (−0.36) |
| Qwen3 (LLM) | 86.43 | 89.36 (+2.93) | 88.39 (+1.96) | – |
| Falcon-H1 (LLM) | 81.05 | 85.33 (+4.28) | 85.70 (+4.65) | 85.33 (+4.28) |
| **Mean change, 5 LLMs** | | **+1.92** | **+1.84** | **+0.71** |

**LLM rows:** QLoRA classifiers, seed 42 only, same setup. No LLM trains on a set it generated itself (–). In all 17 runs the epoch with the lowest training loss is also the one with the best dev macro F1, so the dev rule gives the same models: these are also the LLM results for SR01-EESA (real only) and SR02-EASA (+ SG01-EASA).

**BERTs**
- **Real only barely moves:** 84.15 against 83.96 with the dev rule. Four BERTs are identical, because they had already kept epoch 3; CAMeLBERT-DA gains most (+1.30), MARBERT loses 0.21.
- **Breadth:** Aya and Fanar now improve 6 of 7 BERTs, Qwen3 5 (with the dev rule: 6, 3 and 4). MARBERT is unchanged with Aya and lower with the other two.
- **Where it helps:** still most for the weak BERTs (ARBERTv2 and CAMeLBERT-mix +0.6 to +1.2).
- **By class:** test NEU F1 rises by 0.82–1.00.
- **Over all 21 BERT × generator pairs:** +0.43 on average, 17 improve, 3 get worse, 1 tie (sign test p = 0.003).

**LLMs**
- **Breadth:** 9 of the 12 LLM × generator pairs improve. Two of the three losses are with the Qwen3 set (Jais-2 −1.35, Aya −0.36).
- **Where it helps:** Falcon-H1 gains 4.3–4.7 points and Qwen3 2–3; Fanar, Jais-2 and Aya move by less than 1 point either way, except Jais-2 + Qwen3.
- **Falcon-H1** is far below the others on real data only (81.05) and had an unstable first epoch (training loss 5.1, then 0.26).

**Takeaway (BERTs): with the training-loss rule the SG01-EESA gain is slightly larger and broader (+0.4 to +0.5 micro F1, 17 of 21 pairs). Dev no longer picks the epoch, so these runs are the baseline for SR04-EASA.**

**Takeaway (LLMs): without synthetic data, four of the five LLM classifiers are 2–7 points above the BERT mean (84.15); Falcon-H1 is 3 points below it. SG01-EESA helps only the two weakest LLMs. One seed, so single cells are not results.**
  
**Future Runs** 
- More Epochs for BERTS  
- Try minimal pairs on the same classes

## SR04-EASA results: few-shot sets, targeted vs random examples (EASA test micro F1; BERTs: mean ± std over 3 seeds; LLMs: seed 42 only)
EESA train + 1,320 few-shot texts (D-034), epoch by training loss, baseline SR03-EASA (real only). **SR04-EASA** = SG02-EASA, whose examples are the most-errored dev texts of 4 types (dev-contaminated). **SR04-random-EASA** = SG02-random-EASA, the same size and class mix with random EESA train examples. LLM rows: QLoRA, seed 42 only; – = the LLM's own set.

**SR04-EASA (+ SG02-EASA, targeted)**

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.43 (−0.24) | 88.55 (−0.12) | 88.59 (−0.08) |
| MARBERTv2 | 86.06 ± 0.32 | 87.25 (+1.19) | 86.84 (+0.78) | 85.86 (−0.20) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.56 (+0.29) | 84.92 (+0.65) | 83.54 (−0.73) |
| ARBERT | 84.39 ± 0.46 | 84.52 (+0.13) | 84.15 (−0.24) | 82.93 (−1.46) |
| ARBERTv2 | 82.36 ± 0.79 | 83.33 (+0.97) | 83.41 (+1.05) | 82.68 (+0.32) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 82.97 (+1.14) | 83.46 (+1.63) | 82.03 (+0.20) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 81.78 (+0.28) | 81.42 (−0.08) | 81.66 (+0.16) |
| **Mean of 7 BERTs** | **84.15** | **84.69 (+0.54)** | **84.68 (+0.52)** | **83.90 (−0.26)** |
| Fanar (LLM) | 91.56 | 93.15 (+1.59) | – | 90.46 (−1.10) |
| Jais-2 (LLM) | 91.08 | 91.32 (+0.24) | 91.08 (+0.00) | 90.34 (−0.74) |
| Aya (LLM) | 89.24 | – | 89.24 (+0.00) | 88.88 (−0.36) |
| Qwen3 (LLM) | 86.43 | 89.61 (+3.18) | 88.02 (+1.59) | – |
| Falcon-H1 (LLM) | 81.05 | 85.57 (+4.52) | 85.21 (+4.16) | 84.23 (+3.18) |
| **Mean change, 5 LLMs** | | **+2.38** | **+1.44** | **+0.25** |

**SR04-random-EASA (+ SG02-random-EASA, random examples)**

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.35 (−0.32) | 88.71 (+0.04) | 88.59 (−0.08) |
| MARBERTv2 | 86.06 ± 0.32 | 86.35 (+0.29) | 86.63 (+0.57) | 86.39 (+0.33) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.47 (+0.20) | 84.60 (+0.33) | 84.76 (+0.49) |
| ARBERT | 84.39 ± 0.46 | 85.13 (+0.74) | 84.68 (+0.29) | 84.64 (+0.25) |
| ARBERTv2 | 82.36 ± 0.79 | 83.37 (+1.01) | 84.11 (+1.75) | 83.58 (+1.22) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 82.76 (+0.93) | 83.94 (+2.11) | 83.17 (+1.34) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 81.62 (+0.12) | 82.68 (+1.18) | 82.40 (+0.90) |
| **Mean of 7 BERTs** | **84.15** | **84.58 (+0.42)** | **85.05 (+0.90)** | **84.79 (+0.64)** |
| Fanar (LLM) | 91.56 | 91.69 (+0.13) | – | 92.42 (+0.86) |
| Jais-2 (LLM) | 91.08 | 91.20 (+0.12) | 91.08 (+0.00) | 91.56 (+0.48) |
| Aya (LLM) | 89.24 | – | 90.83 (+1.59) | 89.73 (+0.49) |
| Qwen3 (LLM) | 86.43 | 89.12 (+2.69) | 88.26 (+1.83) | – |
| Falcon-H1 (LLM) | 81.05 | 84.96 (+3.91) | 84.11 (+3.06) | 85.21 (+4.16) |
| **Mean change, 5 LLMs** | | **+1.71** | **+1.62** | **+1.50** |

**Paired comparisons** (test micro F1, per classifier × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | BERTs (21 pairs) | LLMs (12 pairs) |
|---|---|---|
| Targeted vs random examples | −0.38, 7 / 13 / 1 (p = 0.26) | −0.26, 5 / 6 / 1 (p = 1.00) |
| Random few-shot vs real only | +0.65, 19 / 2 / 0 (p < 0.001) | +1.61, 11 / 0 / 1 (p = 0.001) |
| Targeted vs real only | +0.27, 13 / 8 / 0 (p = 0.38) | +1.35, 7 / 3 / 2 (p = 0.34) |
| Random few-shot vs zero-shot (SR03 + SG01) | +0.22, 14 / 7 / 0 (p = 0.19) | +0.12, 5 / 7 / 0 (p = 0.77) |

- **Targeting does not help:** the targeted sets score below the random-example sets in 13 of 21 BERT pairs and 6 of 12 LLM pairs. The gap is not significant in micro F1. In macro F1 it is larger for the BERTs (−0.49, 16 of 21 pairs, p = 0.027).
- **Random examples help broadly:** the Fanar random set improves all 7 BERTs, the Aya and Qwen3 sets 6. Of the 12 LLM pairs, 11 improve and 1 is unchanged.
- **Qwen3's targeted set hurts:** it lowers 4 of 7 BERTs (ARBERT −1.46) and 3 of 4 LLMs. Its fidelity is the lowest of the six sets (70.1%).
- **Where it helps:** as before, the weak classifiers gain most (ARBERTv2 and CAMeLBERT-mix about +1 to +2 with the Aya and Fanar sets; Falcon-H1 +3 to +4.5, Qwen3 +1.6 to +3.2). MARBERT stays within ±0.3.
- **By class (BERTs):** test NEU F1 rises by 0.74–1.47 with the targeted sets and 1.13–1.61 with the random sets.
- **Dev is not a result for SR04-EASA:** its examples are dev texts, and its dev scores are higher than its test scores.

**Takeaway: on EESA, few-shot generation with random real examples is the best setting so far (+0.65 micro F1 for BERTs, 19 of 21 pairs; +1.61 for LLMs). Aiming the examples at the most-errored comment types adds nothing on test and is slightly worse.**

## SR05-EASA results: SR03-EASA with 8 epochs (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
SR03-EASA repeated with 8 epochs instead of 3; nothing else changes (epoch by training loss, D-035; learning rate 5e-5). Every 3-epoch run had kept its last epoch, so the BERTs were probably undertrained. No LLM classifiers.

**How 8 was chosen (pilot).** 21 real-only runs (7 BERTs × 3 seeds) with 10 epochs. Rule fixed before the pilot: the earliest epoch whose mean dev micro F1 is within 0.25 of the best epoch. Epoch 8 is the first one inside that margin. Only real-only runs and dev were used; no synthetic set and no test score.

| Epoch | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mean dev micro F1 (21 runs) | 75.10 | 83.82 | 85.15 | 85.68 | 86.67 | 86.85 | 87.29 | 87.64 | 87.61 | 87.68 |

**Real only: 3 epochs against 8 epochs**

| Classifier | SR03-EASA (3 epochs) | SR05-EASA (8 epochs) | Δ |
|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 89.98 ± 0.53 | +1.31 |
| MARBERTv2 | 86.06 ± 0.32 | 89.28 ± 0.39 | +3.22 |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 86.88 ± 0.07 | +2.61 |
| ARBERT | 84.39 ± 0.46 | 86.10 ± 0.25 | +1.71 |
| ARBERTv2 | 82.36 ± 0.79 | 84.84 ± 0.42 | +2.48 |
| CAMeLBERT-mix | 81.83 ± 0.31 | 84.43 ± 0.58 | +2.60 |
| CAMeLBERT-DA | 81.50 ± 0.60 | 82.76 ± 0.86 | +1.26 |
| **Mean of 7 BERTs** | **84.15** | **86.32** | **+2.17** |

**SR05-EASA (+ SG01-EASA, zero-shot), 8 epochs**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.28 (−0.70) | 88.92 (−1.06) | 89.08 (−0.90) |
| MARBERTv2 | 89.28 ± 0.39 | 88.88 (−0.40) | 89.08 (−0.20) | 88.79 (−0.49) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.15 (−0.73) | 86.39 (−0.49) | 86.59 (−0.29) |
| ARBERT | 86.10 ± 0.25 | 86.43 (+0.33) | 86.84 (+0.74) | 87.16 (+1.06) |
| ARBERTv2 | 84.84 ± 0.42 | 84.60 (−0.24) | 84.84 (+0.00) | 85.29 (+0.45) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.31 (−0.12) | 84.52 (+0.09) | 84.52 (+0.09) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 82.89 (+0.13) | 83.01 (+0.25) | 83.54 (+0.78) |
| **Mean of 7 BERTs** | **86.32** | **86.08 (−0.25)** | **86.23 (−0.10)** | **86.42 (+0.10)** |

- **More epochs help every BERT:** real only rises by 1.3 to 3.2 points, 2.17 on average (7 of 7). MARBERTv2 gains most and is now 0.7 below MARBERT (it was 2.6 below).
- **The SG01-EESA gain is gone:** over the 21 BERT × generator pairs the change against real only is −0.08 (9 improve, 11 get worse, 1 tie; p = 0.82). With 3 epochs it was +0.43 (17 of 21, p = 0.003).
- **Breadth:** Aya improves 2 of 7 BERTs, Fanar 3 and Qwen3 4. The three strongest BERTs (MARBERT, MARBERTv2, AraBERTv02-Twitter) get worse with every set.
- **Where it still helps:** ARBERT (+0.3 to +1.1) and CAMeLBERT-DA (+0.1 to +0.8).
- **By class:** test NEU F1 rises by 0.10–0.55 (0.82–1.00 with 3 epochs).
- **Epoch kept:** 8 in 78 of the 84 runs and 7 in the other 6, where the training loss rose slightly in the last epoch.

**Takeaway: training for 8 epochs instead of 3 adds +2.2 micro F1 to the real-only BERTs, about five times the gain from SG01-EESA at 3 epochs. With 8 epochs the zero-shot sets no longer help on average. Most of the earlier synthetic-data gain looks like a stand-in for more training.**

## SR06-EASA results: SR04-EASA with 8 epochs, targeted vs random examples (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
SR04-EASA and SR04-random-EASA repeated with 8 epochs, baseline SR05-EASA (real only, 8 epochs). **SR06-EASA** = + SG02-EASA (targeted, dev-contaminated). **SR06-random-EASA** = + SG02-random-EASA. No LLM classifiers.

**SR06-EASA (+ SG02-EASA, targeted)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.28 (−0.70) | 88.88 (−1.10) | 89.00 (−0.98) |
| MARBERTv2 | 89.28 ± 0.39 | 88.71 (−0.57) | 89.16 (−0.12) | 88.30 (−0.98) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.55 (−0.33) | 86.59 (−0.29) | 86.35 (−0.53) |
| ARBERT | 86.10 ± 0.25 | 86.67 (+0.57) | 86.02 (−0.08) | 85.98 (−0.12) |
| ARBERTv2 | 84.84 ± 0.42 | 84.35 (−0.49) | 84.96 (+0.12) | 85.00 (+0.16) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 85.04 (+0.61) | 84.56 (+0.13) | 84.80 (+0.37) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 82.89 (+0.13) | 82.84 (+0.08) | 83.05 (+0.29) |
| **Mean of 7 BERTs** | **86.32** | **86.21 (−0.11)** | **86.14 (−0.18)** | **86.07 (−0.26)** |

**SR06-random-EASA (+ SG02-random-EASA, random examples)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 88.92 (−1.06) | 89.12 (−0.86) | 89.24 (−0.74) |
| MARBERTv2 | 89.28 ± 0.39 | 88.55 (−0.73) | 88.67 (−0.61) | 88.75 (−0.53) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.47 (−0.41) | 86.59 (−0.29) | 85.86 (−1.02) |
| ARBERT | 86.10 ± 0.25 | 87.12 (+1.02) | 86.63 (+0.53) | 86.72 (+0.62) |
| ARBERTv2 | 84.84 ± 0.42 | 85.21 (+0.37) | 85.13 (+0.29) | 85.04 (+0.20) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.52 (+0.09) | 85.00 (+0.57) | 85.37 (+0.94) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 83.09 (+0.33) | 83.37 (+0.61) | 84.35 (+1.59) |
| **Mean of 7 BERTs** | **86.32** | **86.27 (−0.06)** | **86.36 (+0.03)** | **86.48 (+0.15)** |

**Paired comparisons, 8 epochs** (test micro F1, per BERT × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | BERTs (21 pairs), 8 epochs | Same comparison, 3 epochs (SR04) |
|---|---|---|
| Targeted vs random examples | −0.23, 6 / 14 / 1 (p = 0.12) | −0.38, 7 / 13 / 1 (p = 0.26) |
| Random few-shot vs real only | +0.04, 12 / 9 / 0 (p = 0.66) | +0.65, 19 / 2 / 0 (p < 0.001) |
| Targeted vs real only | −0.18, 9 / 12 / 0 (p = 0.66) | +0.27, 13 / 8 / 0 (p = 0.38) |
| Random few-shot vs zero-shot (+ SG01) | +0.12, 13 / 8 / 0 (p = 0.38) | +0.22, 14 / 7 / 0 (p = 0.19) |

- **The few-shot gain is gone too:** the random-example sets add +0.04 over real only (12 of 21 pairs, p = 0.66). With 3 epochs they added +0.65 (19 of 21).
- **Split by BERT strength:** every set lowers MARBERT, MARBERTv2 and AraBERTv02-Twitter (−0.1 to −1.1). The random sets still improve all four weaker BERTs (+0.1 to +1.6); the targeted sets improve them in 9 of 12 cells.
- **Targeting still does not help:** targeted is below random in 14 of 21 pairs (−0.23, p = 0.12). In macro F1 the gap is −0.30 (16 of 21 pairs, p = 0.027), the same picture as with 3 epochs.
- **More epochs help every condition:** each of the 63 synthetic-data runs is higher with 8 epochs than with 3 (+1.6 to +1.7 on average), but less than real only (+2.17), which is why the gap closes.
- **By class:** test NEU F1 rises by 0.41–0.64 with the targeted sets and 0.60–0.88 with the random sets, about half of the 3-epoch rise.
- **Dev is not a result for SR06-EASA:** its examples are dev texts (mean dev 87.72 against 87.20 for the random sets, while test is lower).

**Takeaway: once the BERTs are trained for 8 epochs, no EESA synthetic set improves them on average (−0.26 to +0.15 micro F1); only the weaker BERTs still gain, and the three strongest lose. The SR02–SR04 gains came mostly from undertrained baselines. Targeted examples remain no better than random ones.**

Full per-classifier rows (dev and test, all metrics): `docs/sentiment/tables/sentiment_summary_EESA.csv`.

## SR07-EASA results: matrix-language pilot (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
Does stating the matrix language (the language that supplies the grammar of a code-switched comment) in the prompt change the generated code-switching and the BERT scores? (D-037; idea from Yoo et al. 2025.) Zero-shot sets of 1,320 texts from Qwen3, Aya and Fanar, identical except one instruction in the prompt: **NM** = mix Egyptian Arabic and English, no matrix stated; **DM3** = Egyptian Arabic sentence with English words inserted (prompt v3); **EM** = English sentence with Egyptian Arabic words inserted. Every arm asks for about 1 switched word in 5 (EESA train: 23% Latin-script words). Prompts: `prompts/sentiment/matrix_eesa_{nm,dm,em}_v2.json`, `matrix_eesa_dm_v3.json`. Training as SR03-EASA: 3 epochs, epoch by training loss, baseline SR03-EASA (real only). 10 sets, 210 runs, no failure. Registry runs SR07-EESA-NM / -DM / -DM3 / -EM (folders `sr07{nm,dm,dm3,em}_eesa_*`).

**Why DM3:** the first dialect-matrix prompt (**DM**, prompt v2) inserted almost no English with Qwen3, so it was reworded before Aya and Fanar were generated: "Every comment must contain English words written in Latin letters, placed inside the Egyptian sentence where an Egyptian would say them in English (for example like, video, song, nice, fake, subscribe)". Three rewordings were tried on 48 Qwen3 requests each (4%, 7% and 4% Latin-script words); v3 is the 7% one. DM prompt v2 exists for Qwen3 only. **Limit:** v3 names example words and says "must"; the NM and EM prompts do not, so DM3 differs from them in more than the matrix statement.

**The sets** (code-switching read from the script per word, `src/sentiment/cmi.py`; CMI = code-mixing index, 0 = one language only)

| Set | Requests | Not parsed | Rejected by script filter | Latin-script words | CMI | Texts with no switch | Switch-point fraction | Words per text | MTLD | Fidelity (NEG / NEU / POS) |
|---|---|---|---|---|---|---|---|---|---|---|
| EESA train (real) | – | – | – | 22.8% | 22.6 | 1% | 0.23 | 12.6 | 1,226 | 89.4% (93 / 80 / 94) |
| SG03-EASA-NM Aya | 1,716 | 0 | 0 | 7.7% | 7.2 | 80% | 0.01 | 23.7 | 402 | 75.0% (100 / 25 / 100) |
| SG03-EASA-NM Fanar | 2,400 | 299 | 48 | 21.0% | 18.2 | 28% | 0.09 | 16.0 | 1,045 | 78.9% (96 / 41 / 99) |
| SG03-EASA-NM Qwen3 | 1,716 | 7 | 6 | 4.8% | 5.2 | 64% | 0.04 | 21.0 | 73 | 79.2% (65 / 76 / 96) |
| SG03-EASA-DM3 Aya | 1,716 | 0 | 0 | 6.8% | 6.6 | 81% | 0.01 | 23.5 | 320 | 71.1% (99 / 15 / 100) |
| SG03-EASA-DM3 Fanar | 1,716 | 75 | 20 | 25.1% | 23.7 | 9% | 0.10 | 20.1 | 850 | 74.5% (97 / 26 / 100) |
| SG03-EASA-DM3 Qwen3 | 1,716 | 32 | 3 | 4.8% | 5.6 | 56% | 0.07 | 20.2 | 90 | 70.2% (78 / 44 / 88) |
| SG03-EASA-DM Qwen3 (prompt v2) | 1,716 | 98 | 3 | 2.5% | 2.9 | 75% | 0.02 | 27.1 | 42 | 74.2% (63 / 71 / 89) |
| SG03-EASA-EM Aya | 1,716 | 0 | 0 | 12.0% | 11.2 | 72% | 0.03 | 28.4 | 513 | 75.8% (100 / 28 / 100) |
| SG03-EASA-EM Fanar | 3,300 | 825 | 615 | 63.6% | 23.4 | 2% | 0.19 | 16.7 | 514 | 65.2% (75 / 22 / 99) |
| SG03-EASA-EM Qwen3 | 3,300 | 845 | 475 | 66.2% | 25.3 | 0% | 0.10 | 22.4 | 73 | 71.5% (100 / 15 / 100) |

**SR07-EASA-NM (+ SG03-EASA-NM, no matrix stated)**

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.55 (−0.12) | 87.86 (−0.81) | 87.98 (−0.69) |
| MARBERTv2 | 86.06 ± 0.32 | 86.47 (+0.41) | 85.37 (−0.69) | 85.86 (−0.20) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.80 (+0.53) | 84.68 (+0.41) | 84.52 (+0.25) |
| ARBERT | 84.39 ± 0.46 | 84.96 (+0.57) | 84.19 (−0.20) | 84.84 (+0.45) |
| ARBERTv2 | 82.36 ± 0.79 | 82.68 (+0.32) | 82.64 (+0.28) | 82.80 (+0.44) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 82.68 (+0.85) | 82.27 (+0.44) | 82.64 (+0.81) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 81.38 (−0.12) | 81.74 (+0.24) | 82.27 (+0.77) |
| **Mean of 7 BERTs** | **84.15** | **84.50 (+0.35)** | **84.11 (−0.05)** | **84.42 (+0.26)** |

**SR07-EASA-DM3 (+ SG03-EASA-DM3, Egyptian Arabic as matrix, prompt v3); last column: Qwen3 with DM prompt v2 (SR07-EASA-DM)**

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 | + Qwen3, DM prompt v2 |
|---|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.75 (+0.08) | 87.57 (−1.10) | 87.53 (−1.14) | 88.43 (−0.24) |
| MARBERTv2 | 86.06 ± 0.32 | 86.88 (+0.82) | 84.31 (−1.75) | 85.21 (−0.85) | 84.47 (−1.59) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 85.29 (+1.02) | 84.27 (+0.00) | 84.31 (+0.04) | 84.27 (+0.00) |
| ARBERT | 84.39 ± 0.46 | 84.68 (+0.29) | 83.37 (−1.02) | 84.84 (+0.45) | 85.33 (+0.94) |
| ARBERTv2 | 82.36 ± 0.79 | 83.50 (+1.14) | 82.72 (+0.36) | 82.56 (+0.20) | 83.54 (+1.18) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 82.52 (+0.69) | 82.11 (+0.28) | 82.72 (+0.89) | 82.31 (+0.48) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 82.11 (+0.61) | 81.13 (−0.37) | 80.77 (−0.73) | 81.78 (+0.28) |
| **Mean of 7 BERTs** | **84.15** | **84.82 (+0.66)** | **83.64 (−0.51)** | **83.99 (−0.16)** | **84.30 (+0.15)** |

**SR07-EASA-EM (+ SG03-EASA-EM, English as matrix)**

| Classifier | SR03-EASA (real only) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 88.67 ± 0.39 | 88.67 (+0.00) | 87.20 (−1.47) | 88.75 (+0.08) |
| MARBERTv2 | 86.06 ± 0.32 | 86.31 (+0.25) | 85.57 (−0.49) | 86.27 (+0.21) |
| AraBERTv02-Twitter | 84.27 ± 1.03 | 84.76 (+0.49) | 84.07 (−0.20) | 84.92 (+0.65) |
| ARBERT | 84.39 ± 0.46 | 84.72 (+0.33) | 84.19 (−0.20) | 83.78 (−0.61) |
| ARBERTv2 | 82.36 ± 0.79 | 83.41 (+1.05) | 82.44 (+0.08) | 83.37 (+1.01) |
| CAMeLBERT-mix | 81.83 ± 0.31 | 82.97 (+1.14) | 82.56 (+0.73) | 81.70 (−0.13) |
| CAMeLBERT-DA | 81.50 ± 0.60 | 81.30 (−0.20) | 82.31 (+0.81) | 80.97 (−0.53) |
| **Mean of 7 BERTs** | **84.15** | **84.59 (+0.44)** | **84.05 (−0.11)** | **84.25 (+0.10)** |

**Paired comparisons** (test micro F1, per BERT × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | BERTs |
|---|---|
| NM vs real only | +0.19, 14 / 7 / 0 (p = 0.19) |
| DM3 vs real only | −0.00, 13 / 7 / 1 (p = 0.26) |
| EM vs real only | +0.14, 12 / 8 / 1 (p = 0.50) |
| DM3 vs NM | −0.19, 7 / 13 / 1 (p = 0.26) |
| EM vs NM | −0.04, 10 / 10 / 1 (p = 1.00) |
| DM3 vs EM | −0.15, 10 / 11 / 0 (p = 1.00) |
| NM vs zero-shot (SR03 + SG01) | −0.24, 5 / 16 / 0 (p = 0.03) |
| DM3 vs zero-shot (SR03 + SG01) | −0.43, 7 / 14 / 0 (p = 0.19) |
| EM vs zero-shot (SR03 + SG01) | −0.29, 5 / 14 / 2 (p = 0.06) |
| DM prompt v2 vs real only (Qwen3 only, 7 pairs) | +0.15, 4 / 2 / 1 (p = 0.69) |
| DM3 vs DM prompt v2 (Qwen3 only, 7 pairs) | −0.31, 3 / 4 / 0 (p = 1.00) |

All rows are over 21 pairs unless marked.

- **The matrix instruction does not separate the arms:** over the 21 pairs the three arms lie within 0.2 of each other (−0.00 to +0.19 against real only) and no comparison between arms is significant.
- **The generator matters more than the arm:** the Aya sets help in every arm (+0.35 to +0.66), the Fanar sets hurt in every arm (−0.05 to −0.51), Qwen3 is in between (−0.16 to +0.26).
- **Only Fanar code-switches like EESA:** 21–25% Latin-script words and CMI 18–24 in its NM and DM3 sets (EESA 22.8%, 22.6), and its MTLD is the highest (850–1,045). Its sets are still the least useful.
- **Aya ignores the instruction and helps most:** 7–12% Latin-script words and 72–81% of texts without a switch in every arm; even its English-matrix set is mostly Arabic (13% of texts mostly English, against 83% for Fanar and 87% for Qwen3). So more EESA-like code-switching did not mean more useful data here.
- **The dialect-matrix prompt removed English with Qwen3:** prompt v2 gave less English than no instruction (2.5% against 4.8% Latin-script words; 75% of texts with no switch). The rewording (v3) brought Qwen3 only back to the NM level (4.8%), with fewer unparsed outputs (32 against 98) but weaker NEU labels (the judge confirms 44% against 71%), and its set is less useful than v2 (−0.31 over 7 pairs).
- **English-matrix is costly for Fanar and Qwen3:** both needed 3,300 requests (825–845 not parsed, 475–615 under the 10% Arabic-letter rule); Aya filled every set on the first pass with nothing rejected. The Fanar and Qwen3 English-matrix sets are the mirror of EESA (mostly English with Arabic inserted), not EESA.
- **Weak NEU labels almost everywhere:** the judge confirms 15–44% of the NEU comments in 8 of the 9 three-generator sets (76% for Qwen3 NM), against 80% on real EESA dev.
- **Qwen3 has the least variety:** MTLD 42–90 against 216 for SG01-EASA Qwen3 and 1,226 for EESA; its comments are 1.6–2.2 times longer than real ones and often repeat a phrase.
- **All below the plain zero-shot set:** SG01-EASA scored 84.54–84.61 per generator; NM is below it in 16 of 21 pairs (−0.24, p = 0.03), EM in 14 (−0.29, p = 0.06), DM3 in 14 (−0.43, p = 0.19).
- **Split by BERT strength:** the three strongest BERTs lose on average in every arm (−0.05 to −0.32); the four weaker ones gain (+0.23 to +0.40). The Fanar sets lower MARBERT by 0.8–1.5 and MARBERTv2 by 0.5–1.8.
- **By class:** test NEG F1 rises with every set (+0.3 to +1.4). NEU rises with Aya (+0.8 to +1.0) and falls or stays with Fanar (−0.55 to +0.29); POS falls with Fanar (−0.4 to −1.3).
- **Epoch kept:** 3 in all runs.

**Takeaway: stating the matrix language in the prompt does not change how useful the generated data is (three arms within 0.2 micro F1, none significant, all below the plain zero-shot SG01-EASA sets). What changes the result is the generator: the Aya sets help in every arm and the Fanar sets hurt in every arm, although Fanar is the only one whose code-switching looks like EESA. Qwen3 does not write Egyptian sentences with inserted English when asked zero-shot, even after rewording. 3 epochs; the 8-epoch repeat is SR08-EASA below.**

Full per-classifier rows: `docs/sentiment/tables/sentiment_summary_EESA.csv` (runs SR07-EESA-NM / -DM / -DM3 / -EM). Code-switching per text: `results/quality/sentiment/cmi_sg03_eesa_*.json`.

## SR08-EASA results: matrix-language pilot with 8 epochs (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
The SR07-EASA runs repeated with 8 epochs instead of 3 (D-036 recipe); nothing else changes (epoch by training loss, learning rate 5e-5). Baseline SR05-EASA (real only, 8 epochs). Arms **NM** (no matrix stated), **DM3** (Egyptian Arabic as matrix, prompt v3) and **EM** (English as matrix), 3 generators, 189 runs, plus the Qwen3 dialect-matrix set with prompt v2 (21 runs). 210 runs, no failure. Registry runs SR08-EESA-NM / -DM / -DM3 / -EM (folders `sr08{nm,dm,dm3,em}_eesa_*`). The sets and their code-switching are in the SR07-EASA section above.

**SR08-EASA-NM (+ SG03-EASA-NM, no matrix stated)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.00 (−0.98) | 88.55 (−1.43) | 88.83 (−1.15) |
| MARBERTv2 | 89.28 ± 0.39 | 89.41 (+0.13) | 88.88 (−0.40) | 88.75 (−0.53) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.35 (−0.53) | 86.84 (−0.04) | 86.59 (−0.29) |
| ARBERT | 86.10 ± 0.25 | 86.76 (+0.66) | 85.86 (−0.24) | 87.12 (+1.02) |
| ARBERTv2 | 84.84 ± 0.42 | 85.41 (+0.57) | 84.76 (−0.08) | 85.78 (+0.94) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.56 (+0.13) | 84.96 (+0.53) | 84.47 (+0.04) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 83.13 (+0.37) | 82.48 (−0.28) | 83.86 (+1.10) |
| **Mean of 7 BERTs** | **86.32** | **86.37 (+0.05)** | **86.05 (−0.28)** | **86.49 (+0.16)** |

**SR08-EASA-DM3 (+ SG03-EASA-DM3, Egyptian Arabic as matrix, prompt v3)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.24 (−0.74) | 88.43 (−1.55) | 88.06 (−1.92) |
| MARBERTv2 | 89.28 ± 0.39 | 89.41 (+0.13) | 87.98 (−1.30) | 87.20 (−2.08) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.59 (−0.29) | 85.86 (−1.02) | 86.19 (−0.69) |
| ARBERT | 86.10 ± 0.25 | 86.96 (+0.86) | 85.57 (−0.53) | 86.67 (+0.57) |
| ARBERTv2 | 84.84 ± 0.42 | 85.29 (+0.45) | 84.60 (−0.24) | 84.52 (−0.32) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.15 (−0.28) | 84.88 (+0.45) | 83.78 (−0.65) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 83.13 (+0.37) | 82.56 (−0.20) | 83.29 (+0.53) |
| **Mean of 7 BERTs** | **86.32** | **86.40 (+0.07)** | **85.70 (−0.63)** | **85.67 (−0.65)** |

**SR08-EASA-EM (+ SG03-EASA-EM, English as matrix)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.41 (−0.57) | 88.79 (−1.19) | 88.63 (−1.35) |
| MARBERTv2 | 89.28 ± 0.39 | 89.08 (−0.20) | 88.43 (−0.85) | 88.88 (−0.40) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.15 (−0.73) | 85.98 (−0.90) | 86.67 (−0.21) |
| ARBERT | 86.10 ± 0.25 | 87.08 (+0.98) | 86.63 (+0.53) | 86.27 (+0.17) |
| ARBERTv2 | 84.84 ± 0.42 | 85.25 (+0.41) | 85.04 (+0.20) | 84.76 (−0.08) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.88 (+0.45) | 84.19 (−0.24) | 84.35 (−0.08) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 82.97 (+0.21) | 83.82 (+1.06) | 81.99 (−0.77) |
| **Mean of 7 BERTs** | **86.32** | **86.40 (+0.08)** | **86.13 (−0.20)** | **85.94 (−0.39)** |

**Paired comparisons** (test micro F1, per BERT × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | BERTs (21 pairs), 8 epochs | Same comparison, 3 epochs (SR07) |
|---|---|---|
| NM vs real only | −0.02, 10 / 11 / 0 (p = 1.00) | +0.19, 14 / 7 / 0 (p = 0.19) |
| DM3 vs real only | −0.40, 7 / 14 / 0 (p = 0.19) | −0.00, 13 / 7 / 1 (p = 0.26) |
| EM vs real only | −0.17, 8 / 13 / 0 (p = 0.38) | +0.14, 12 / 8 / 1 (p = 0.50) |
| DM3 vs NM | −0.38, 4 / 15 / 2 (p = 0.02) | −0.19, 7 / 13 / 1 (p = 0.26) |
| EM vs NM | −0.15, 9 / 12 / 0 (p = 0.66) | −0.04, 10 / 10 / 1 (p = 1.00) |
| DM3 vs EM | −0.23, 7 / 14 / 0 (p = 0.19) | −0.15, 10 / 11 / 0 (p = 1.00) |
| NM vs zero-shot (+ SG01) | +0.06, 10 / 10 / 1 (p = 1.00) | −0.24, 5 / 16 / 0 (p = 0.03) |
| DM3 vs zero-shot (+ SG01) | −0.32, 6 / 15 / 0 (p = 0.08) | −0.43, 7 / 14 / 0 (p = 0.19) |
| EM vs zero-shot (+ SG01) | −0.09, 10 / 10 / 1 (p = 1.00) | −0.29, 5 / 14 / 2 (p = 0.06) |

- **No arm helps at 8 epochs:** against real only the three arms are at −0.02 (NM), −0.17 (EM) and −0.40 (DM3) over the 21 pairs; each loses in more pairs than it wins. None is significant.
- **The small 3-epoch gains are gone:** NM went from +0.19 to −0.02 and EM from +0.14 to −0.17, the same pattern as SR05-EASA and SR06-EASA.
- **The reworded dialect-matrix arm is the worst:** DM3 is below NM in 15 of 21 pairs (−0.38, p = 0.02, the only comparison under 0.05, among nine tested). DM3 names example words in its prompt, so this is not a clean test of the matrix statement.
- **Generator order holds, but smaller:** the Aya sets are level with real only in every arm (+0.05 to +0.08), the Fanar sets below it (−0.20 to −0.63), the Qwen3 sets from +0.16 (NM) to −0.65 (DM3).
- **Split by BERT strength:** the three strongest BERTs lose with almost every set (2 wins in 27 cells; −0.58 to −1.05 on average); the four weaker ones gain a little (+0.08 to +0.40; 23 wins in 36 cells).
- **Dialect-matrix prompt v2 (Qwen3 only):** 86.42 (+0.10 against real only; 4 wins, 3 losses), against 85.67 for DM3 from the same generator. The reworded prompt gave more English and a less useful set.
- **Against plain zero-shot at 8 epochs:** NM and EM are level with SG01-EASA (+0.06, −0.09); DM3 is below it (−0.32, 15 of 21 pairs, p = 0.08).
- **More epochs help every condition:** 62 of the 63 arm runs are higher with 8 epochs (+1.77 to +1.96 on average), but less than real only (+2.17).
- **By class:** test NEU F1 still rises with Aya (+0.7 to +0.8) and with NM from Qwen3 (+0.57); POS falls with Fanar (−0.4 to −1.0).
- **Epoch kept:** 8 in 199 of the 210 runs, 7 in the other 11.

**Takeaway: with BERTs trained for 8 epochs, none of the matrix-language sets improves on real data alone (−0.02 to −0.40 micro F1 over 21 pairs, none significant), and stating the matrix language gives no advantage over the plain zero-shot prompt. The one clear difference is negative: the reworded dialect-matrix prompt (DM3) is worse than no instruction. As in SR05-EASA and SR06-EASA, the 3-epoch gains came from undertrained baselines.**

Full per-classifier rows: `docs/sentiment/tables/sentiment_summary_EESA.csv` (runs SR08-EESA-NM / -DM / -DM3 / -EM).

## SR09-EASA results: dislike comments, targeted examples (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
Can generated dislike comments fix the dislike errors that remain after 8 epochs (D-038)? EESA train + SG04-EASA: 2,640 generated comments about dislikes per generator (1,320 NEG / 1,320 NEU, twice the size of SG01–SG03), few-shot with 5 examples per request from the 15 EESA dev dislike comments that most of the 210 eight-epoch runs get wrong (8 NEG, 7 NEU; **dev-contaminated**). Prompt `prompts/sentiment/fewshot_eesa_v1.json`, type "Dislike comments". Training as SR05-EASA: 8 epochs, epoch by training loss, baseline SR05-EASA (real only, 8 epochs). 63 runs, no failure. Registry run SR09-EESA (folders `sr09_eesa_*`). The size-matched control with random train dislike comments as examples is SR09-random-EASA (next section).

**The sets** (code-switching from `src/sentiment/cmi.py`; "mention dislikes" = the dislike regex of `src/sentiment/dislike_pools_eesa.py`)

| Set | Requests | Rejected by filter (of them copies of dev texts) | Mention dislikes | Latin-script words | CMI | Texts with no switch | Words per text | MTLD | Fidelity (NEG / NEU) |
|---|---|---|---|---|---|---|---|---|---|
| EESA train (real) | – | – | 23% of NEG + NEU | 22.8% | 22.6 | 1% | 12.6 | 1,226 | 93 / 80 |
| SG04-EASA Aya | 4,224 | 4 (0) | 50% | 0.4% | 0.6 | 94% | 19.7 | 192 | 99 / 44 |
| SG04-EASA Fanar | 4,224 | 3 (0) | 37% | 3.3% | 4.2 | 58% | 14.2 | 459 | 94 / 43 |
| SG04-EASA Qwen3 | 4,224 | 189 (87) | 65% | 5.2% | 6.7 | 41% | 12.7 | 92 | 71 / 34 |

**SR09-EASA (+ SG04-EASA, targeted dislike comments)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.85 (−0.13) | 89.32 (−0.66) | 89.12 (−0.86) |
| MARBERTv2 | 89.28 ± 0.39 | 89.00 (−0.28) | 88.79 (−0.49) | 87.65 (−1.63) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.27 (−0.61) | 87.08 (+0.20) | 87.08 (+0.20) |
| ARBERT | 86.10 ± 0.25 | 86.31 (+0.21) | 85.86 (−0.24) | 85.57 (−0.53) |
| ARBERTv2 | 84.84 ± 0.42 | 84.56 (−0.28) | 84.64 (−0.20) | 84.64 (−0.20) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 84.76 (+0.33) | 85.53 (+1.10) | 84.72 (+0.29) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 83.09 (+0.33) | 83.05 (+0.29) | 83.54 (+0.78) |
| **Mean of 7 BERTs** | **86.32** | **86.26 (−0.06)** | **86.32 (+0.00)** | **86.05 (−0.28)** |

**Paired comparisons, 8 epochs** (per BERT × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | Test micro F1 (21 pairs) | Test macro F1 (21 pairs) |
|---|---|---|
| SR09-EASA vs real only | −0.11, 9 / 12 / 0 (p = 0.66) | −0.08, 10 / 11 / 0 (p = 1.00) |
| SR09-EASA vs zero-shot (+ SG01) | −0.03, 12 / 8 / 1 (p = 0.50) | −0.13, 9 / 11 / 1 (p = 0.82) |
| SR09-EASA vs random few-shot (+ SG02-random, SR06-random-EASA) | −0.16, 8 / 12 / 1 (p = 0.50) | −0.26, 8 / 13 / 0 (p = 0.38) |
| SR09-EASA vs targeted few-shot (+ SG02, SR06-EASA) | +0.07, 11 / 10 / 0 (p = 1.00) | +0.04, 11 / 10 / 0 (p = 1.00) |

**Error rate on dislike comments** (share of the comments a run gets wrong, mean over the runs; dislike regex as above)

| Condition | Runs | Dev: the 15 example texts | Dev: all 117 dislike comments | Dev: NEG (93) / NEU (22) | Test: all 106 dislike comments | Test: NEG (85) / NEU (19) |
|---|---|---|---|---|---|---|
| SR05-EASA real only | 21 | 65.4% | 18.1% | 7.2% / 61.9% | 17.8% | 6.9% / 64.9% |
| SR05-EASA + SG01-EASA | 63 | 66.9% | 17.4% | 9.8% / 47.8% | 17.1% | 8.7% / 52.6% |
| SR06-random-EASA | 63 | 67.8% | 17.6% | 9.3% / 50.2% | 17.7% | 8.7% / 55.8% |
| SR06-EASA (dev-contaminated) | 63 | 57.9% | 16.8% | 14.7% / 23.4% | 18.3% | 11.9% / 42.7% |
| **SR09-EASA (dev-contaminated)** | 63 | **26.2%** | **14.1%** | 13.2% / 15.3% | **17.4%** | 11.3% / 41.5% |

- **No gain on average:** against real only the dislike sets give −0.11 micro F1 over the 21 pairs (9 better, 12 worse, p = 0.66); per generator −0.06 (Aya), +0.00 (Fanar), −0.28 (Qwen3).
- **Same split by BERT strength:** the three strongest BERTs lose (−0.47; 2 of 9 cells up), the four weaker gain a little (+0.16; 7 of 12 up). The Qwen3 set lowers MARBERTv2 by 1.63.
- **Not better than the earlier sets:** level with zero-shot SG01-EASA (−0.03) and targeted SG02-EASA (+0.07), slightly below random-example SG02-random-EASA (−0.16); none significant. SG04-EASA is twice their size.
- **The dev drop is contamination:** errors on the 15 example texts fall from 65% to 26%, but these texts were the examples.
- **On test the dislike errors do not fall:** 17.4% against 17.8% for real only. The errors move from NEU to NEG: NEU dislike comments 64.9% → 41.5% wrong, NEG dislike comments 6.9% → 11.3% wrong, and 83% of the wrong NEG ones are read as NEU. SR06-EASA showed the same trade (11.9% / 42.7%).
- **By class:** test NEU F1 +0.60, NEG −0.57, POS −0.27 against real only; the Qwen3 set lowers NEG by 1.06.
- **The sets are narrow and their NEU is weak:** the judge confirms 34–44% of the NEU comments; only 37–65% mention dislikes at all; 89–96% fall in the unclustered universal topic; almost no code-switching (CMI 0.6–6.7 against 22.6). Qwen3 copied 87 dev example texts closely enough to be filtered out, and its MTLD is 92.
- **Epoch kept:** 8 in 61 of the 63 runs, 7 in 2.

**Takeaway: 2,640 generated dislike comments per generator, made from the dev dislike errors, do not improve the 8-epoch BERTs (−0.11 micro F1, 9 of 21 pairs, not significant) and do not lower the error on test dislike comments (17.4% against 17.8%). They shift the errors from NEU to NEG, as the SG02-EASA dislike type did. EESA labels a dislike comment NEG when it insults the dislikers and NEU when it only asks about them; the generated sets carry that line weakly (the judge confirms 34–44% of their NEU comments). The dev improvement on the example texts is contamination. The random-example control is in the next section.**

Full per-classifier rows: `docs/sentiment/tables/sentiment_summary_EESA.csv` (run SR09-EESA). Numbers: `python -m src.sentiment.compare_eesa_sr09`.

## SR09-random-EASA results: dislike comments, random examples; targeted vs random (EASA test micro F1; BERTs only, mean ± std over 3 seeds)
The size-matched control for SR09-EASA (D-038): EESA train + SG04-random-EASA, 2,640 generated dislike comments per generator (1,320 NEG / 1,320 NEU), same prompt, but the 5 examples per request are random EESA train dislike comments (pool of 311: 258 NEG, 53 NEU), so no dev text is used. Training as SR09-EASA (8 epochs, epoch by training loss), baseline SR05-EASA real only. 62 of 63 runs: `sr09r_eesa_marbert_fanar_seed43` was cut off by a PC shutdown and is not rerun, so MARBERT + Fanar is the mean of 2 seeds. Registry run SR09-random-EESA (folders `sr09r_eesa_*`).

**The sets** (as for SR09-EASA)

| Set | Requests | Rejected by filter (of them copies of dev texts) | Mention dislikes | Latin-script words | CMI | Texts with no switch | Words per text | MTLD | Fidelity (NEG / NEU) |
|---|---|---|---|---|---|---|---|---|---|
| EESA train (real) | – | – | 23% of NEG + NEU | 22.8% | 22.6 | 1% | 12.6 | 1,226 | 93 / 80 |
| SG04-random-EASA Aya | 4,224 | 18 (0) | 32% | 0.7% | 0.9 | 90% | 20.6 | 207 | 98 / 57 |
| SG04-random-EASA Fanar | 4,224 | 3 (0) | 38% | 3.7% | 4.6 | 54% | 14.7 | 516 | 97 / 46 |
| SG04-random-EASA Qwen3 | 4,224 | 84 (0) | 67% | 6.1% | 7.3 | 29% | 13.8 | 121 | 87 / 46 |

**SR09-random-EASA (+ SG04-random-EASA, random dislike examples)**

| Classifier | SR05-EASA (real only, 8 epochs) | + Aya | + Fanar | + Qwen3 |
|---|---|---|---|---|
| MARBERT | 89.98 ± 0.53 | 89.16 (−0.82) | 88.69 (−1.29), 2 seeds | 88.43 (−1.55) |
| MARBERTv2 | 89.28 ± 0.39 | 89.41 (+0.13) | 88.35 (−0.93) | 88.43 (−0.85) |
| AraBERTv02-Twitter | 86.88 ± 0.07 | 86.92 (+0.04) | 86.84 (−0.04) | 86.88 (+0.00) |
| ARBERT | 86.10 ± 0.25 | 86.02 (−0.08) | 86.02 (−0.08) | 86.15 (+0.05) |
| ARBERTv2 | 84.84 ± 0.42 | 85.66 (+0.82) | 84.76 (−0.08) | 84.15 (−0.69) |
| CAMeLBERT-mix | 84.43 ± 0.58 | 85.25 (+0.82) | 84.56 (+0.13) | 84.92 (+0.49) |
| CAMeLBERT-DA | 82.76 ± 0.86 | 82.93 (+0.17) | 83.25 (+0.49) | 83.54 (+0.78) |
| **Mean of 7 BERTs** | **86.32** | **86.48 (+0.15)** | **86.07 (−0.26)** | **86.07 (−0.25)** |

**Paired comparisons, 8 epochs** (per BERT × generator pair: mean Δ, wins / losses / ties, two-sided sign test)

| Comparison | Test micro F1 (21 pairs) | Test macro F1 (21 pairs) |
|---|---|---|
| Targeted vs random dislike examples (SR09-EASA − SR09-random-EASA) | +0.01, 10 / 10 / 1 (p = 1.00) | −0.01, 11 / 10 / 0 (p = 1.00) |
| SR09-random-EASA vs real only | −0.12, 10 / 10 / 1 (p = 1.00) | −0.07, 14 / 7 / 0 (p = 0.19) |
| SR09-EASA vs real only (above) | −0.11, 9 / 12 / 0 (p = 0.66) | −0.08, 10 / 11 / 0 (p = 1.00) |

**Error rate on dislike comments** (mean over the runs; rows for the other conditions in the SR09-EASA section)

| Condition | Runs | Dev: the 15 SR09-EASA example texts | Dev: all 117 dislike comments | Dev: NEG (93) / NEU (22) | Test: all 106 dislike comments | Test: NEG (85) / NEU (19) |
|---|---|---|---|---|---|---|
| SR05-EASA real only | 21 | 65.4% | 18.1% | 7.2% / 61.9% | 17.8% | 6.9% / 64.9% |
| SR09-EASA (targeted, dev-contaminated) | 63 | 26.2% | 14.1% | 13.2% / 15.3% | 17.4% | 11.3% / 41.5% |
| SR09-random-EASA (random) | 62 | 65.6% | 17.6% | 15.4% / 25.1% | 18.2% | 12.5% / 40.9% |

- **Targeting makes no difference:** targeted and random dislike examples tie over the 21 pairs (+0.01 micro F1, 10 wins and 10 losses; −0.01 macro F1).
- **Neither helps:** both are 0.1 below real only on average (−0.11 and −0.12). Per generator the random sets give +0.15 (Aya), −0.26 (Fanar) and −0.25 (Qwen3).
- **Same split by BERT strength:** with random examples the three strongest BERTs lose (−0.59; 2 of 9 cells up) and the four weaker gain (+0.23; 8 of 12 up). MARBERT loses with every set (−0.82 to −1.55).
- **The dev gain of SR09-EASA was contamination:** on the 15 example texts the random-example runs are as wrong as real only (65.6% against 65.4%), the targeted runs much less (26.2%). On test the two are the same (17.4% and 18.2%).
- **The NEU-to-NEG trade comes from the dislike comments, not from the examples:** with random examples too, NEU dislike comments on test go from 64.9% to 40.9% wrong and NEG ones from 6.9% to 12.5% wrong; 84% of the wrong NEG ones are read as NEU.
- **By class:** test NEU F1 +0.55, NEG −0.43, POS −0.34 against real only, close to SR09-EASA (+0.60, −0.57, −0.27).
- **Random sets are slightly cleaner:** the judge confirms more of their NEU comments (46–57% against 34–44%), Qwen3 has fewer repeats (1.5% against 4.2%) and copied no dev text; they mention dislikes about as often (32–67%) and code-switch as little (CMI 0.9–7.3).
- **Epoch kept:** 8 in 61 of the 62 runs, 7 in 1.

**Takeaway: aiming the examples at the dev dislike errors gives exactly the same result as random train dislike comments (+0.01 micro F1 over 21 pairs). Neither set improves the 8-epoch BERTs (−0.11 and −0.12) or lowers the error on test dislike comments; both only move errors from NEU to NEG dislike comments. As with SG02-EASA, targeting the remaining error type does not work, and the only effect of the targeted examples is on the dev texts they were made from.**

Full per-classifier rows: `docs/sentiment/tables/sentiment_summary_EESA.csv` (runs SR09-EESA, SR09-random-EESA). Numbers: `python -m src.sentiment.compare_eesa_sr09`.

## SR00 results: zero-shot, no training, English vs Arabic prompt (EASA test micro F1; 5 LLMs, one deterministic run each)

- **Question:** how well do the roster LLMs classify EASA sentiment with no training at all, and does the prompt language matter?
- **Setup:** 4-bit LLMs, no examples, no class definitions. The prompt asks for the sentiment of the YouTube comment in one word; the prediction is the answer word with the highest log-probability (`src/sentiment/zero_shot.py`). SR00-EnPrompt: negative / neutral / positive (one token each). SR00-ArPrompt: سلبي / محايد / إيجابي (2–4 tokens, summed log-probability). Comments cut to 128 tokens (7–16 per split cut). Reference: the same LLMs trained on EASA train (SR03-EASA, QLoRA, seed 42).

| Model | SR00-EnPrompt | SR00-ArPrompt | Ar − En | Trained, real only (SR03-EASA) | En − trained |
|---|---|---|---|---|---|
| Jais-2 | **85.57** | **82.40** | −3.17 | 91.08 | −5.51 |
| Aya | 82.03 | 74.21 | −7.82 | 89.24 | −7.21 |
| Fanar | 78.36 | 72.86 | −5.50 | 91.56 | −13.20 |
| Falcon-H1 | 74.45 | 72.00 | −2.45 | 81.05 | −6.60 |
| Qwen3 | 62.59 | 76.28 | +13.69 | 86.43 | −23.84 |
| **Mean of 5 LLMs** | **76.60** | **75.55** | **−1.05** | **87.87** | **−11.27** |

Floor: always POS = 44.38. Mean of the 7 trained BERTs (SR05-EASA, 8 epochs): 86.32.

**Per-class test F1 and predicted counts** (gold NEG 197 / NEU 258 / POS 363)

| Model | Prompt | NEG F1 | NEU F1 | POS F1 | Predicted NEG / NEU / POS |
|---|---|---|---|---|---|
| Jais-2 | En | 86.4 | 76.5 | 90.6 | 231 / 202 / 385 |
| Jais-2 | Ar | 87.6 | 76.4 | 84.7 | 205 / 331 / 282 |
| Aya | En | 84.0 | 71.1 | 87.5 | 234 / 195 / 389 |
| Aya | Ar | 84.8 | 49.5 | 80.4 | 197 / 126 / 495 |
| Fanar | En | 86.8 | 60.2 | 83.0 | 206 / 141 / 471 |
| Fanar | Ar | 81.1 | 37.7 | 81.8 | 269 / 66 / 483 |
| Falcon-H1 | En | 85.6 | 68.6 | 72.6 | 228 / 369 / 221 |
| Falcon-H1 | Ar | 80.2 | 65.7 | 72.8 | 217 / 360 / 241 |
| Qwen3 | En | 63.4 | 61.7 | 63.4 | 112 / 533 / 173 |
| Qwen3 | Ar | 75.7 | 67.1 | 83.4 | 273 / 234 / 311 |

- **Zero-shot Jais-2 is already a usable classifier:** 85.57 with the English prompt, about the mean of the 7 trained BERTs (86.32), 5.5 below trained Jais-2.
- **Training still matters:** every LLM is 5.5 to 23.8 below its trained version (mean −11.3).
- **The ranking changes with training:** zero-shot Jais-2 > Aya > Fanar > Falcon-H1 > Qwen3; trained Fanar is the best (91.56) but zero-shot it is third.
- **English prompt is better for 4 of 5 LLMs** (−2.5 to −7.8 with Arabic). Qwen3 is the exception (+13.7 with Arabic).
- **Qwen3 with the English prompt calls most comments neutral** (533 NEU predicted, 258 gold); with Arabic its counts are close to gold.
- **NEU is the hard class everywhere** (37.7–76.5 F1). Fanar and Aya with the Arabic prompt rarely answer محايد (66 and 126 NEU) and over-predict POS.
- **The expected Arabic length bias against POS did not show:** إيجابي has the most tokens, yet POS is over-predicted by Aya and Fanar.
- **Dev agrees with test** (within 1–4 points; dev chose nothing here).

**Takeaway: without training the LLMs reach 62.6–85.6 test micro F1 (mean 76.6 English, 75.6 Arabic). Only Jais-2 comes close to the trained BERTs; training adds 5.5–23.8 points for every LLM. English is the better prompt for 4 of 5 LLMs; Qwen3 is the exception.**

Full rows: `docs/sentiment/tables/sentiment_summary_EESA.csv` (runs SR00-EnPrompt, SR00-ArPrompt).
