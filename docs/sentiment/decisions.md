# Sentiment decisions log

Decisions for the sentiment track. Dialect-track decisions are in `../decisions.md`. IDs are `SD-NNN`, permanent, never reused. Newest at the bottom. Timestamps are local time (UTC+3).

<!-- Entry format:
## SD-NNN — YYYY-MM-DD HH:MM — Short title
- **Decision:** what was decided
- **Why:** reasoning
- **Alternatives considered:** (if any)
-->

## SD-001 — 2026-10-13 — Start a sentiment track on ArSarcasm-v2, documented separately
- **Decision:** Run the synthetic-data experiments on Arabic sentiment (3 classes) using ArSarcasm-v2 while the full MLADI data is pending. Code goes in `src/sentiment/`, docs in `docs/sentiment/`.
- **Why:** Lets the generation → filtering → training pipeline be tested now. ArSarcasm-v2 has human sentiment labels on both train and test, an official split, an MIT license, and public test labels, so every condition and seed can be scored locally.
- **Alternatives considered:** Waiting for MLADI; other Arabic sentiment sets (not yet compared).

## SD-002 — 2026-10-13 — Build of S1: cleaning, deduplication, test overlap, dev split
- **Decision:**
  - Same link/mention cleaning as the dialect data (`URL`, `USER`, switchable); no other normalization.
  - Train is deduplicated on the cleaned text. Texts whose copies disagree on sentiment (25) are dropped; other duplicates keep one copy (first copy's sarcasm/dialect, conflicts listed in `label_conflict`).
  - Train texts that match a test text (4 after cleaning) are dropped from train.
  - Dev = 10% of the remaining train, stratified by sentiment × sarcasm, seed 42.
  - The official test set is kept as released (3,000 rows, duplicates included) and used for final evaluation only.
- **Why:** Conflicting copies would train the same text towards two classes and could straddle train/dev; with 2 copies there is no majority. Matching on cleaned text also catches tweets that differ only in a link. Stratifying on sarcasm too keeps sarcastic tweets (positive words, negative meaning) evenly spread. Keeping the test set intact keeps scores comparable with the WANLP 2021 shared task.
- **Alternatives considered:** Majority vote on duplicates (impossible with ties); stratifying on dialect too (magreb has 43 train tweets, strata would be too small); using the shared-task test set for model selection (forbidden by the evaluation rules).

## SD-003 — 2026-10-13 14:55 — SR01 models, seeds and schedule
- **Decision:** SR01 (real only, S1) trains every classifier in the roster. The three BERT models (MARBERTv2, AraBERTv02-Twitter, MARBERT) get 3 seeds (42, 43, 44). The five LLMs (Qwen3-8B, Jais-2-8B, Fanar-1-9B, Aya-Expanse-8B, Falcon-H1-7B) first get a 300-text smoke test, then one full run with seed 42. Jais-2 and Qwen3 run in the afternoon after the BERTs; Fanar, Aya and Falcon-H1 overnight. The best LLM on dev macro F1 then gets more seeds (43, 44); other LLMs get more seeds only if they come out close to it.
- **Why:** BERT runs take ~3 min each, so 3 seeds cost nothing. One seed per LLM takes 1.4–6.5 h (~15 h for all five), and 3 seeds each would be ~45 h. Spending the extra seeds on the best LLM gives a mean ± std where it matters for the comparison with the BERTs. Single-seed LLM scores are marked as such and are not treated as results until they have seeds.
- **Alternatives considered:** 3 seeds for every LLM (~45 h); LLMs skipped for sentiment.

## SD-004 — 2026-10-16 06:50 — First synthetic sets: open, zero-shot, 4 generators, 500 per cell, BERTs only
- **Decision:**
  - Condition 2 (open) first. The prompt fixes only the variety (ArSarcasm-v2 region label msa/egypt/gulf/levant; magreb left out, 37 train tweets) and the sentiment class, with a one-line definition of each class. Zero-shot: no real tweets in the prompt. Template `prompts/sentiment/open_v1.json`.
  - Four generators, same plan: Jais-2-8B, Fanar-1-9B, Qwen3-8B, Aya-Expanse-8B (4-bit NF4). Sampling as in the dialect configs (T 1.0, top-p 0.95, top-k 50), max 96 new tokens, seed 42.
  - 500 synthetic tweets per variety × sentiment cell (12 cells, 6,000 per set). 650 requested per cell; the shared filter (exact / near duplicates within the set and against S1 train and dev, Arabic script, 2–60 words; `configs/filtering/sentiment.json`) runs first, then a seeded sample of 500 per cell is kept (`src/sentiment/select_synthetic.py`). Overlap with the official test set is reported, not filtered.
  - Classifiers: MARBERTv2, AraBERTv02-Twitter, MARBERT, seeds 42/43/44, same recipe as SR01; run SR02, one member per classifier × generator set. (Renumbered 2026-10-16 by Ammar: SG01 = the zero-shot generation with all four generators, SR02 = training on SG01; file and folder names keep the earlier sg01–sg04 / sr02–sr05 numbering.) LLM classifiers only after the BERT results are seen.
  - Later controls for condition 3: variety, sarcasm (NEG/NEU only: 51 of 1,930 sarcastic train tweets are POS) and length.
- **Why:** Ammar's choices (2026-10-16). A uniform 500 per cell balances variety and class without making any cell mostly synthetic by a large margin (largest: gulf POS 107 real → 607). BERT runs are ~3 min, LLM runs ~2–5 h on 17k texts, so BERTs give the generator comparison overnight. Zero-shot keeps real tweets out of the prompts, so the synthetic set measures the generator alone.
- **Alternatives considered:** 1,000 per cell (synthetic would outnumber real in 8 of 12 cells); filling cells to a floor of 500; bringing NEG/POS up to NEU; few-shot k=3; small (1–4B) generators (kept as a possible size ablation); LLM classifiers now (~15 h per set per seed).
- **Open:** whether a classifier gains unfairly from data its own model generated (needs a crossover design, e.g. Jais-2 and Fanar each trained on both sets).
