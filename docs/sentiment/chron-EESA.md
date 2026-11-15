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
