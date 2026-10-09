# Data

Every data set used in training or measurement, with its version ID. Raw and processed data live in `data/` (gitignored, never uploaded). Counts below are from the stats files in `results/data_stats/`. The reasons behind each step are in `decisions.md` (D-002 to D-004, D-006).

## Sources

| Source | What | Where | Used for |
|---|---|---|---|
| NADI 2020 / 2021 / 2023 tweets | Single-label, geolocation-labelled tweets over 18 countries | `MLADI/train/` | Training text |
| LahjatBERT labels | Automatic multi-label annotation (18 dialects) of the same tweets | `LahjatBERT_-main/data/stage_1_and_gpt_with_ids.csv` | Training labels |
| MLADI dev | 120 sentences, human multi-label gold for 8 dialects | `MLADI/dev/NADI2024_subtask1_dev2.tsv` | Model selection, scorer validation |
| MLADI test | 1,000 sentences, 11 dialects, labels private | Leaderboard Space only | Final evaluation only |

## Versions

| ID | File | SHA-256 (first 12) | Texts | Contents | Built by |
|---|---|---|---|---|---|
| D1 | `data/processed/nadi_lahjatbert.jsonl` | `d299edd78f3d` | 58,384 | Unique NADI 2020/2021/2023 texts with the 18 LahjatBERT labels. Links → `URL`, mentions → `USER`, double-escaped quotes restored. No other normalization. All-18 and zero-label texts kept. **Default training set.** | `src/data/build_dataset.py` |
| D2 | `data/processed/nadi_lahjatbert_card1to17.jsonl` | `47bedd182435` | 48,471 | D1 without the 2,271 zero-label and 7,642 all-18 texts | `src/data/filter_cardinality.py --min-card 1 --max-card 17` |
| D3 | `data/processed/nadi_lahjatbert_card0to17.jsonl` | `128bd0bf6e0d` | 50,742 | D1 without the 7,642 all-18 texts (zero-label kept) | `filter_cardinality --min-card 0 --max-card 17` |
| D4 | `data/processed/nadi_lahjatbert_card1to18.jsonl` | `5e3e642f6fb9` | 56,113 | D1 without the 2,271 zero-label texts (all-18 kept) | `filter_cardinality --min-card 1 --max-card 18` |

Other files:
- `data/processed/d1_g01match_seed42.jsonl`: 20 single-label D1 tweets, 4 for each of the 5 G01 dialects. The size-matched real reference for Q02.
- `data/synthetic/g01_<model>.jsonl`: the 20 G01 sentences per generator after the pipeline's parser (`scripts/g01_to_records.py`). Scored in Q02.

## D1 at a glance

From `results/data_stats/nadi_lahjatbert_stats.json`:
- **Join:** 58,768 NADI tweets → 58,386 unique texts, 58,384 of them labelled (2 tweets have no label). 21 texts had conflicting labels across copies; majority per dialect, ties counted as valid (D-002).
- **Cleaning:** links replaced in 4,819 texts, mentions in 1,202. 268 texts became identical to another text after cleaning; they are kept.
- **Valid dialects per text:** 0 → 2,271; 1 → 13,065; 2 → 11,421; 3–5 → 10,160; 6–11 → 4,251; 12–17 → 9,574; all 18 → 7,642.
- **Country imbalance** in the original single labels: largest / smallest country = 6.85 (Egypt 9,756 vs Bahrain and Sudan 1,425 each).
- **Overlap with MLADI dev:** 0 exact text matches.

TODO: `decisions.md` D-004 says 365 quoted tweets were restored; the stats file says 364 (`cleaning.unescaped_quoted_texts`). The stats file was written at commit `4150272`. Check which number is right for the current D1.
