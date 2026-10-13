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
