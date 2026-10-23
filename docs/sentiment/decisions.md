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

## SD-005 — 2026-10-17 — Quality measures for the SG01 sets; ALDi and E5 back for measurement only
- **Decision:** Measure each SG01 selected set, next to a real S1 reference, with: imbalance (max : min cell count), MSA share and dialectness (Sentence-ALDi; MSA cutoff = best msa/dialect split on S1 train), lexical diversity (MTLD), topic spread (how many of 30 k-means topics of S1 train E5 embeddings get ≥ 1% of the texts), semantic diversity (Vendi on E5), repeats (exact + near duplicates in the raw output) and sentiment fidelity (share predicted as the requested class by the SR01 MARBERT classifiers, 3 seeds, mean probabilities). Size-dependent measures on seeded samples of 3,000. Script `src/sentiment/measure_quality.py`, run SQ01.
- **Why:** Ammar's column list (2026-10-17); definitions proposed and accepted. The filter only removes surface duplicates; these measures describe diversity, dialect and label quality, which the SR02 results alone cannot explain.
- **Scorers:** Sentence-ALDi and multilingual-e5-large were dropped from the roster on 2026-10-10 (as scorers/filters); Ammar approved them again for measurement only, not filtering. CAMeLBERT DID stays dropped.
- **Limits:** the fidelity classifiers are ~80% accurate on dev, so fidelity is an estimate (the real reference row gives their dev accuracy); the classifiers were trained on real tweets, so a generator that writes "typical" sentiment can score above real data. No test data is used.

## SD-006 — 2026-10-18 — Jais-2-8B is a classifier only in the sentiment track, not a generator
- **Decision:** Jais-2-8B is dropped as a sentiment generator and kept as the main sentiment classifier. Later sentiment generation (open and controlled) uses Fanar-1-9B, Qwen3-8B and Aya-Expanse-8B.
- **Why:** Ammar's decision. Jais-2 is by far the worst generator: in SQ01 its SG01 output had 77.7% repeats (others 0.1–3.8%), it could not fill its cells (imbalance 62.5 : 1 vs 1.0 : 1), and its lexical and semantic diversity were among the lowest (MTLD 339.3, Vendi 2.8), so its set was never trained on in SR02. As a classifier it is the best in the roster: SR01 dev macro F1 80.47 ± 0.66 (3 seeds) and test 67.02 ± 1.03, ahead of Fanar (79.42 dev, 1 seed), Aya (79.36 ± 0.79) and every BERT (best MARBERT 78.68 ± 0.42). Numbers from `docs/sentiment/tables/sg01_quality.md` and `sentiment_summary.md`.
- **Side effect:** Jais-2 never classifies data it generated itself, so the self-generation question left open in SD-004 does not arise for it (it still applies to any other model used in both roles).
- **Alternatives considered:** Fixing Jais-2 generation (e.g. other sampling settings or prompts) to keep four generators; not tried.

## SD-007 — 2026-10-21 — Four more BERT classifiers; SR03 = real only without NEU
- **Decision:**
  - New sentiment classifiers: CAMeLBERT-mix (`CAMeL-Lab/bert-base-arabic-camelbert-mix`), CAMeLBERT-DA (`CAMeL-Lab/bert-base-arabic-camelbert-da`), ARBERT (`UBC-NLP/ARBERT`) and ARBERTv2 (`UBC-NLP/ARBERTv2`). They join SR01 and SR02 (all three SG01 sets) with the MARBERT recipe unchanged (lr 5e-5, batch 24, 3 epochs, dropout 0.3, 8 frozen layers, max length 128), seeds 42/43/44.
  - SR03: real only (S1) with every NEU tweet dropped from train, dev and test (6,069 / 675 / 2,252 tweets), 2-class NEG/POS head, all 12 classifiers (7 BERTs, 5 LLMs with their SR01 QLoRA recipes), seeds 42/43/44. Implemented as an optional config field `classes` (default NEG/NEU/POS) in `src/sentiment/common.py` and both trainers.
- **Why:** Ammar's choices (2026-10-21). Both CAMeLBERT variants and both ARBERT versions, as MARBERT v1/v2 are both in. SR03 isolates NEG vs POS, the part of the task the WANLP F1-PN metric scores, from the NEU class that drives the dev→test drop.
- **Not comparable:** SR03 macro F1 is over two classes on a NEG/POS-only dev and test, so it cannot be compared with SR01/SR02 macro F1 or F1-PN (those are 3-class models scored on all tweets). Ammar is aware and wants the runs anyway; rescoring SR01 on the NEG/POS subset was offered and not wanted.
- **Cost:** ~2.5 h for the new BERTs in SR01/SR02, ~30 min for the SR03 BERTs, ~16 h for the SR03 LLMs (estimated from SR01 times scaled to the smaller data). Queue `scripts/sentiment/queue_sr03.sh`.
- **Not in the dialect roster:** these four models are used in the sentiment track only.

## SD-008 — 2026-10-23 — Measure label agreement on S1 dev by relabelling a sample
- **Decision:** Ammar relabels a sample of S1 dev tweets (NEG / NEU / POS) under the ArSarcasm-v2 sentiment guidelines, without seeing the gold labels or any model predictions. Cohen's kappa against the gold labels is computed overall and per class. The sample has two parts:
  - **A, random:** 150 dev tweets, stratified by gold sentiment. This part gives the agreement estimate for the whole dataset.
  - **B, model errors:** every dev NEG tweet that at least one SR03 run (12 models × 3 seeds) called POS (138 tweets). This part shows how many of these errors are label errors.
  - Tweets in both parts are labelled once. The order is shuffled, so Ammar cannot tell which part a tweet is from.
- **Why (Ammar's justification, 2026-10-23):**
  1. **A real number for label quality.** Today we only guess the labels are noisy. Agreement turns the guess into a measured, citable number.
  2. **A ceiling for our scores.** Models cannot be more reliable than their labels. Agreement shows roughly where that ceiling is, and how much room any method still has.
  3. **A way to judge small differences.** If labels often disagree, small score gaps are noise. We then know which differences between models or conditions to ignore.
  4. **An explanation for weak classes.** Agreement per class shows whether low NEU and POS F1 is partly a label problem rather than only a model problem.
  5. **A reason synthetic data did not help.** If the hard cases are the ones where the labels themselves disagree, clean synthetic data cannot fix them. This supports "better data, not more data".
  6. **A target for controlled generation.** Agreement shows which kinds of tweets are confusing. Controlled generation can then produce those cases, following the guidelines.
  7. **Evidence of analytical work.** The supervisor rewards analysis, not only headline numbers. A label-quality study with Cohen's kappa is that kind of analysis.
- **Trigger:** the SR03 dev error review (2026-10-22). Of 22 dev NEG tweets that at least half of the SR03 runs called POS, about 4–5 look POS under the guidelines (e.g. "ابق قويا ♥✨", 36/36 runs). Too few to estimate a rate.
- **Rules:** dev only; the test set is not relabelled or inspected. The gold labels stay the evaluation reference (CLAUDE.md label trust rule). Ammar's labels are an analysis, not a new training or test version. Using them to relabel train would be a new data version and needs its own decision.
- **Cost:** no GPU. About 280 tweets of Ammar's time.
- **Known bias:** Ammar already saw the 22 most confident part-B tweets with gold labels (2026-10-22); part-B results are reported with and without them.
- **Open:** the source of the guideline text and of the "~80% annotator agreement" figure (to be checked before citing).
