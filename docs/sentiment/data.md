# Sentiment data

Data for the sentiment track (interim, started 2026-10-13 while the full MLADI data is pending). The dialect track's data is in `../data.md`. Raw and processed data live in `data/` (gitignored). Counts below are from `results/data_stats/sentiment/arsarcasm_v2_stats.json`; reasons for each step are in `decisions.md`.

## Sources

| Source | What | Where | Used for |
|---|---|---|---|
| ArSarcasm-v2 (Abu Farha, Zaghouani & Magdy, WANLP 2021) | 15,548 tweets, human-labelled for sentiment (POS/NEG/NEU), sarcasm and region dialect (msa/egypt/levant/gulf/magreb). Official split 12,548 train / 3,000 test. MIT license. Cloned 2026-10-13 from `github.com/iabufarha/ArSarcasm-v2`, commit `eb85513` | `data/raw/ArSarcasm-v2/ArSarcasm-v2/{training,testing}_data.csv` | Training, dev (carved from train), final test |

Raw files as released:
- **Train (12,548):** NEU 5,747 / NEG 4,621 / POS 2,180; sarcastic 2,168; msa 8,562 / egypt 2,675 / gulf 644 / levant 624 / magreb 43.
- **Test (3,000):** NEG 1,677 / NEU 748 / POS 575; sarcastic 821; msa 2,323 / gulf 322 / egypt 306 / levant 47 / magreb 2.
- Train is NEU-heavy, test NEG-heavy: expect a gap between dev and test scores; use macro F1.
- Links and @mentions are raw in the text (`http` in 4,831 train tweets).

## Versions

| ID | Files | SHA-256 (first 12) | Texts | Contents | Built by |
|---|---|---|---|---|---|
| S1 | `data/processed/sentiment/arsarcasm_v2_train.jsonl` | `8244d8a1ed18` | 11,208 | Official train, deduplicated on cleaned text, 25 sentiment-conflict texts (50 rows) and 4 test-overlapping texts dropped, minus dev. Links → `URL`, mentions → `USER`; no other normalization | `python -m src.sentiment.build_dataset` (seed 42, dev fraction 0.1) |
| S1 | `data/processed/sentiment/arsarcasm_v2_dev.jsonl` | `38713d095d1d` | 1,246 | 10% of the cleaned train, stratified by sentiment × sarcasm | same |
| S1 | `data/processed/sentiment/arsarcasm_v2_test.jsonl` | `53ed8f4dc09a` | 3,000 | Official test, all rows kept as released, same cleaning | same |

The build is deterministic: a rerun gives byte-identical files.

## S1 at a glance

| Split | n | NEG | NEU | POS | Sarcastic | msa / egypt / gulf / levant / magreb |
|---|---|---|---|---|---|---|
| train | 11,208 | 4,116 (36.7%) | 5,139 (45.9%) | 1,953 (17.4%) | 1,930 | 7,678 / 2,385 / 568 / 540 / 37 |
| dev | 1,246 | 458 (36.8%) | 571 (45.8%) | 217 (17.4%) | 215 | 809 / 276 / 74 / 81 / 6 |
| test | 3,000 | 1,677 (55.9%) | 748 (24.9%) | 575 (19.2%) | 821 | 2,323 / 306 / 322 / 47 / 2 |

- **Duplicates in train:** 62 groups after cleaning (59 on raw text). 25 disagree on sentiment and are dropped entirely; the rest keep one copy. 20 kept texts had copies disagreeing on sarcasm or dialect; the first copy's labels are kept and the field is listed in `label_conflict`.
- **Test overlap:** 4 train texts match a test text after cleaning (2 on raw text) and are dropped from train (raw rows 4312, 6168, 7450, 11322).
- **Test duplicates:** 5 texts after cleaning (4 on raw text), kept because the official test set is not modified.
- **Cross-split overlap** (cleaned text): train&dev 0, train&test 0, dev&test 0.
- **Dialect coverage is thin:** 68% of train is MSA; magreb has 37 train / 6 dev / 2 test tweets, so dialect is not a usable control factor on this dataset beyond msa vs egypt (and maybe gulf/levant).

## Record format

One JSON object per line: `text_id` (hash of cleaned text), `text` (cleaned), `text_raw`, `source` (`real`), `origin` (`ArSarcasm-v2`), `split`, `sentiment` (NEG/NEU/POS), `sarcasm` (bool), `dialect`, `raw_rows` (0-based row numbers in the raw CSV), `label_conflict`, `cleaning`.
