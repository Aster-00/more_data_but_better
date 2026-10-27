# Sentiment data

Data for the sentiment track (interim, started 2026-10-13 while the full MLADI data is pending). The dialect track's data is in `../data.md`. Raw and processed data live in `data/` (gitignored). Counts below are from `results/data_stats/sentiment/arsarcasm_v2_stats.json`; reasons for each step are in `../decisions.md` (shared log, tag `[SA]`).

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

## Synthetic sets (S2, open condition, 2026-10-16)

Built by `scripts/sentiment/queue_sg_open.sh` (decision SD-004, run SG01 in `progress.md`). Zero-shot, template `prompts/sentiment/open_v1.json` (SHA-256 `b2a5012c6764`), seed 42. Every record carries `source: "synthetic"`, the generator, its prompt, raw output, sampling settings and the cell (`controls.variety`, `controls.sentiment`); kept separate from the real S1 files. Selection = seeded sample of 500 per variety × sentiment cell from the filtered texts.

| ID | Generator | File | SHA-256 (first 12) | Texts |
|---|---|---|---|---|
| S2-SG01-jais2 | Jais-2-8B | `data/synthetic/sentiment/sg01_jais2.jsonl` (all outputs) | `6d9499722a86` | 15,600 |
| S2-SG01-jais2 | | `sg01_jais2.selected.jsonl` | `c9f7f95a4aa8` | 3,402 (cells short; not used for training) |
| S2-SG01-fanar | Fanar-1-9B | `sg01_fanar.jsonl` | `35261df56889` | 7,800 |
| S2-SG01-fanar | | `sg01_fanar.selected.jsonl` (SR02) | `cbb9ffe3a0a8` | 6,000 |
| S2-SG01-qwen3 | Qwen3-8B | `sg01_qwen3.jsonl` | `be1438c04e1e` | 7,800 |
| S2-SG01-qwen3 | | `sg01_qwen3.selected.jsonl` (SR02) | `2cf037f87f4c` | 6,000 |
| S2-SG01-aya | Aya-Expanse-8B | `sg01_aya.jsonl` | `568c0a02a012` | 7,800 |
| S2-SG01-aya | | `sg01_aya.selected.jsonl` (SR02) | `118e5dcda679` | 6,000 |

- Each selected set: 500 per cell over msa/egypt/gulf/levant × NEG/NEU/POS (2,000 per class), no sarcasm label (`sarcasm: null`, not controlled).
- `.filtered.jsonl` / `.rejected.jsonl` next to each file hold the filter outcome per record; counts in `results/filtering/`.
- Same cleaning as S1 (links → `URL`, mentions → `USER`, original in `text_raw`); `**` markers and same-line English translations removed before that (`translation_stripped`).
- Files were renamed on 2026-10-16 to the SG01/SR02 numbering (map: `results/sentiment/renames_2026-10-16.json`); contents were not edited, so `set_name`, `request_id`, `config_file` inside the records and `run_name` / `synthetic_data` inside the train logs still show the first names (sg02_fanar, sr03_marbertv2_seed42, …).
- No selected text matches an official test text exactly (reported, not filtered).

## Relabelling sheet for the dev agreement study (SD-008)

Built 2026-10-23 by `python -m src.sentiment.make_relabel_sheet` (seed 42). Files in `data/annotation/sentiment/` (gitignored): `relabel_dev_v1.csv` (sheet: item, text, label, note; UTF-8 with BOM), `relabel_dev_v1.key.jsonl` (gold labels, part, SR03 votes per item), `relabel_dev_v1.meta.json`. Source: S1 dev (`38713d095d1d`).

| Part | Tweets | Content |
|---|---|---|
| A, random | 150 | Stratified by gold: NEG 55 / NEU 69 / POS 26 |
| B, model errors | 138 | Every dev NEG tweet that ≥ 1 of 36 SR03 runs predicted POS |
| Overlap | 16 | In both parts, labelled once |
| **Sheet** | **272** | Shuffled; text only, no gold, part or prediction shown |

- **Bias to handle in the analysis:** Ammar already saw 22 part-B tweets with their gold labels and Claude's reading (2026-10-22, the ≥ 18/36 tweets). Report part-B results with and without those 22.
