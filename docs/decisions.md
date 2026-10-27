# Thesis Decisions Log

One running record of the decisions made during chats with Claude, for both tracks: dialect identification (**DI**) and sentiment analysis (**SA**). Each heading carries a track tag: `[DI]`, `[SA]` or `[both]`. Entries are in date order, newest at the bottom.

IDs are permanent and never reused or renumbered. `D-001` to `D-010` were the dialect log; `SD-001` to `SD-009` were the sentiment log (`docs/sentiment/decisions.md`), merged into this file on 2026-10-28 (D-012) with their IDs unchanged. From D-011 on, both tracks share the `D-NNN` sequence. Timestamps are local time (UTC+3). The exact time of D-001 to D-004 and D-006 was not recorded: D-001 and D-006 have only a date, and D-002 to D-004 show when they were committed (`75330bf`), so they were decided at or before that time.

<!-- Entry format:
## D-NNN [DI|SA|both] — YYYY-MM-DD HH:MM — Short title
- **Decision:** what was decided
- **Why:** reasoning
- **Alternatives considered:** (if any)
-->

## D-001 [both] — 2026-10-05 — Decisions log location
- **Decision:** Keep the decisions log at `code/decisions.md`.
- **Why:** User preference; keeps it alongside the thesis code.
- **Alternatives considered:** `F:\Thesis\decisions.md` (top of the Thesis folder).

## D-002 [DI] — 2026-10-06 ≤05:53 — Joining NADI text with LahjatBERT labels
- **Decision:** Join the LahjatBERT label CSV to the NADI tweets through the tweet text, not the `(nadi_source, train_id)` key alone, and keep one record per unique text (now in `src/data/build_dataset.py`). When copies of a text carry different labels (21 texts), take the majority per dialect, with ties counted as valid, and set `label_conflict`. No text normalization at this stage.
- **Why:** LahjatBERT assigned IDs by text lookup, so every duplicated text points at one ID (381 of the 383 "missing" tweets have an exact-text twin). Joining on text recovers 58,384 labelled unique texts, leaving only 2 tweets unlabelled.
- **Alternatives considered:** Joining on the ID only, which would drop 383 tweets and duplicate 320 keys. For the 21 conflicting texts, dropping them or counting ties as not valid was considered and rejected as not worth it: 19 of them are 1-vs-1 ties, and together they are 0.04% of the data, too few to affect results.

## D-003 [DI] — 2026-10-06 ≤05:53 — Replace links and mentions
- **Decision:** Replace links with `URL` and @mentions with `USER` (now in `src/data/build_dataset.py`). Both steps can be switched off, and the original text is kept in `text_raw`. No other normalization is applied.
- **Why:** This makes NADI 2020 (raw links and handles) consistent with 2021 and 2023, which the organizers had already masked. It follows what LahjatBERT's `preprocess.py` intends; their version strips punctuation first, so their URL pattern never matches.
- **Alternatives considered:** Copying the full LahjatBERT `cleaning()` function. Rejected because it also deletes Latin script, emoji and stopwords, and merges letter variants, which conflicts with script and code-switching being experimental factors.

## D-004 [DI] — 2026-10-06 ≤05:53 — One build script; undo double-escaped quotes
- **Decision:** Joining and cleaning run in one script, `src/data/build_dataset.py`, which writes `data/processed/nadi_lahjatbert.jsonl` with `text` (cleaned) and `text_raw` (original tweet). It also undoes the double escaping of 365 quoted NADI 2021 tweets.
- **Why:** The user wants the clean data generated in one run. The escaping is a file-format artifact: `"""…\""…"""` in the file is `…"…` in the actual tweet. LahjatBERT's pandas reader removes only one layer, leaving the wrapping quotes and `\"` in the text.

## D-005 [DI] — 2026-10-06 06:34 — Environment, evaluation and baseline recipe
- **Decision:** Use a project venv (`.venv`, Python 3.12, torch 2.14.1+cu126, transformers 5.18, versions pinned in `requirements.txt`). Score the dev set with `src/evaluation/evaluate_dev.py`, using exactly the leaderboard's `predict_binary_outcomes` settings (raw text, max_length 128, sigmoid, threshold 0.3); macro F1 is the main metric. Train the real-only baseline with `src/training/train_classifier.py` + `configs/baseline_real_only.json`, following LahjatBERT's recipe (MARBERT, first 8 layers frozen, fp16, lr 5e-5, warmup 500, batch 24, 90/10 train/val split, early stopping), with two fixes: dropout 0.3 is passed when the model is built (LahjatBERT sets it afterwards, so their dropout stays 0.1, verified), and the best checkpoint is chosen by validation macro F1 instead of micro F1.
- **Why:** Dev scores should predict leaderboard scores, and the official metric is macro F1. Our metric code reproduces the NADI scorer's reference numbers exactly (38.14 / 50.33 / 42.47 / 50.83).
- **Reference numbers (dev, macro F1):** LahjatBERT_cl_cardinality 72.68, LahjatBERT_cl_aldi 70.27, LahjatBERT_baseline 67.41.

## D-006 [DI] — 2026-10-06 — Keep all-18 and zero-label texts (for now)
- **Decision:** Keep D1 as it is: the 7,642 all-18 texts, the 2,271 zero-label texts and the 268 texts that became identical after cleaning all stay in. Diacritics are not stripped.
- **Why:** The real-only baseline trained on D1 (R03-marbert, 71.34 ± 1.03 dev macro F1) already beats LahjatBERT's baseline and matches their best model. Revisit later as an ablation.
- **Update (R04-marbert):** With LahjatBERT's own settings, D1 gives 68.71 ± 0.35, in line with their baseline (67.41). So the gain in R03-marbert comes from the training settings, not from D1; what R04-marbert does show is that D1 is not worse than their data, which still supports keeping it.
- **Update (R05):** Removing the zero-label and all-18 texts (D2) lowers dev macro F1 for all four classifiers (MARBERT 71.34 → 69.25, AraBERTv02-Twitter 70.52 → 69.82, MARBERTv2 70.11 → 64.89, TF-IDF + LR 62.58 → 56.54), mostly through lower recall. Keep D1. D2 is also 17% smaller, so quantity and composition are not separated yet.
- **Update (R06/R07):** Removing only the zero-label texts changes nothing (all models within 0.9 of R03); removing only the all-18 texts costs as much as removing both. The all-18 texts are the useful ones. Keep D1.

## D-007 [both] — 2026-10-09 10:36 — Documentation in `docs/`, score tables generated only
- **Decision:** All documentation and summary tables live in `docs/`: `progress.md` (run notes only, no score tables), `decisions.md` (this file, moved from the repo root, which supersedes D-001's location), `data.md` (data versions), and `docs/tables/` with generated tables, each as `.csv` and `.md`: `split_summary` (R and T: validation, dev and test scores), `quality_summary` (Q), `scorer_summary` (S), `generator_summary` (G). `dev_summary.md/.csv` are removed: their numbers are the dev rows of `split_summary`. The model roster moved from `progress.md` to `CLAUDE.md`. Console logs are tracked in git. `CLAUDE.md` and `README.md` stay at the root.
- **Why:** `progress.md` was hard to scan (about 270 lines, two-thirds tables), and the same numbers were written in several places. Generating every table from the logged results follows the rule "never hand-edit result files" and leaves one source per number.
- **Alternatives considered:** one notes file per run (rejected for now: one file is easier to search before the interim report); keeping `dev_summary` next to `split_summary` (rejected: duplicate numbers).

## D-008 [DI] — 2026-10-11 16:55 — Keep dropout 0.3, 2 epochs; no curriculum by default
- **Decision:** BERT-sized classifiers keep R03's training settings (dropout 0.3, 2 epochs, macro-F1 epoch selection). Curriculum learning is not added to the default recipe.
- **Why:** In the dropout × epochs grid (R12–R15, R17–R24, MARBERT, D1, 3 seeds) no cell beats R12 (71.34 ± 1.03); dropout 0.2 / 2 epochs (R17, 71.21) is level, longer training never helps dev, dropout 0.5 underfits (~58). R04's 2.6-point drop needs both low dropout and the third epoch. LahjatBERT's cardinality and ALDi curricula on our settings (R10 71.79 ± 1.63, R11 70.87 ± 0.70) are within noise of R12.
- **Alternatives considered:** dropout 0.2 (level with 0.3, not better on 120 sentences); cardinality curriculum (same dev F1, but much higher recall and lower precision; could still be checked on the leaderboard, open).

## D-009 [both] — 2026-10-13 09:57 — PC crashes: keep the SSD out of the pipeline, check PCIe power saving
- **Context:** The thesis PC shut down unexpectedly at 04:53:56 on 2026-10-13, killing the LahjatBERT queue after 51 of 60 runs (the run in progress, `dropout02_ep4_real_only_lahjat_clcard_seed42`, was deleted with Ammar's approval). Windows logs 6 unexpected shutdowns in the 30 days to 2026-10-13. Bugcheck `0x154 UNEXPECTED_STORE_EXCEPTION` on 2026-10-05 and 2026-10-13 (`0xEF` on 2026-09-27). Each time, writing the crash dump failed (volmgr event 161), so the faulting driver is unknown. The 5 corrected WHEA hardware errors come from the PCIe root port of the Realtek 2.5GbE network card, not from a disk or the GPU. RAM (2 × 16 GB Crucial) runs at 2666 MHz (no XMP), and a BERT run uses about 1.8 GB of the 32 GB, so neither memory pressure nor a RAM overclock explains the crashes. The only SSD is `C:` (XPG Spectrix S20G NVMe, about 25 GB free); `F:`/`G:` are on a 2 TB WD HDD. Leading suspect: the NVMe SSD or its driver (unconfirmed).
- **Decision:** (1) No thesis data, models, checkpoints or caches on the `C:` SSD. (2) Turn off PCIe link-state power management (ASPM). (3) Long GPU queues must stay restartable (skip finished runs) so a crash only costs the run in progress.
- **PC settings changed during the thesis:**
  - 2026-10-13: user environment variable `HF_HOME=F:\Thesis\hf_home` (Hugging Face token copied there; login verified as `Ammar-06`). `HF_HUB_CACHE=F:\Thesis\models` was already set. Model downloads, checkpoints and results were already on `F:`; this moves the remaining Hugging Face state (token, xet cache, default hub) off `C:`. Git Bash does not see user variables, so scripts export both (`scripts/queue_lahjat_clcard.sh`). Undo: delete the `HF_HOME` user variable.
  - 2026-10-13 09:5x: `powercfg /setacvalueindex SCHEME_CURRENT SUB_PCIEXPRESS ASPM 0` on the active plan ("Driver Booster Power Plan", `25e098a7-…`). **No effective change:** ASPM was already off (AC index 0) before the command. So PCIe link power saving is ruled out as the cause.
  - 2026-10-12: created `refs/main` (→ `f18b12e`) in the model cache for `Mohamedelzeftawy/LahjatBERT_baseline`, so it loads offline by name (cache bookkeeping only).
  - 2026-10-13 ~10:05: crash dumps moved to `F:\CrashDumps` (registry `HKLM\SYSTEM\CurrentControlSet\Control\CrashControl`), run by Ammar in an administrator PowerShell with `scripts/pc_crashdump_to_F.ps1`, so the next crash names the faulting driver. Before: `DumpFile C:\WINDOWS\MEMORY.DMP`, `MinidumpDir C:\WINDOWS\Minidumps`, no `DedicatedDumpFile` / `DumpFileSize`. After: `DumpFile F:\CrashDumps\MEMORY.DMP`, `MinidumpDir F:\CrashDumps\Minidump`, `DedicatedDumpFile F:\CrashDumps\DedicatedDump.sys`, `DumpFileSize 2048` (MB). `CrashDumpEnabled` unchanged at 3 (small memory dump). Active since the reboot at 2026-10-13 10:09 (verified after the reboot). Undo: the same script with `-Undo`, then reboot.
- **Not done (options still open):** check the SSD's health (CrystalDiskInfo) and update its firmware (XPG SSD Toolbox); move the pip cache (2.55 GB) to `F:` and delete the stray 1.3 GB Hugging Face cache on `C:` (`C:\Users\ammar_duayw04\.cache\huggingface\hub`). Moving TEMP to `F:` was rejected: it affects every program for about 0.5 GB.
- **Alternatives considered:** smaller batch size or fewer dataloader workers (rejected: RAM use is about 1.8 GB and the trainer uses no worker processes); turning off XMP (not applicable: XMP is not enabled).

## SD-001 [SA] — 2026-10-13 — Start a sentiment track on ArSarcasm-v2, documented separately
- **Decision:** Run the synthetic-data experiments on Arabic sentiment (3 classes) using ArSarcasm-v2 while the full MLADI data is pending. Code goes in `src/sentiment/`, docs in `docs/sentiment/`.
- **Why:** Lets the generation → filtering → training pipeline be tested now. ArSarcasm-v2 has human sentiment labels on both train and test, an official split, an MIT license, and public test labels, so every condition and seed can be scored locally.
- **Alternatives considered:** Waiting for MLADI; other Arabic sentiment sets (not yet compared).

## SD-002 [SA] — 2026-10-13 — Build of S1: cleaning, deduplication, test overlap, dev split
- **Decision:**
  - Same link/mention cleaning as the dialect data (`URL`, `USER`, switchable); no other normalization.
  - Train is deduplicated on the cleaned text. Texts whose copies disagree on sentiment (25) are dropped; other duplicates keep one copy (first copy's sarcasm/dialect, conflicts listed in `label_conflict`).
  - Train texts that match a test text (4 after cleaning) are dropped from train.
  - Dev = 10% of the remaining train, stratified by sentiment × sarcasm, seed 42.
  - The official test set is kept as released (3,000 rows, duplicates included) and used for final evaluation only.
- **Why:** Conflicting copies would train the same text towards two classes and could straddle train/dev; with 2 copies there is no majority. Matching on cleaned text also catches tweets that differ only in a link. Stratifying on sarcasm too keeps sarcastic tweets (positive words, negative meaning) evenly spread. Keeping the test set intact keeps scores comparable with the WANLP 2021 shared task.
- **Alternatives considered:** Majority vote on duplicates (impossible with ties); stratifying on dialect too (magreb has 43 train tweets, strata would be too small); using the shared-task test set for model selection (forbidden by the evaluation rules).

## SD-003 [SA] — 2026-10-13 14:55 — SR01 models, seeds and schedule
- **Decision:** SR01 (real only, S1) trains every classifier in the roster. The three BERT models (MARBERTv2, AraBERTv02-Twitter, MARBERT) get 3 seeds (42, 43, 44). The five LLMs (Qwen3-8B, Jais-2-8B, Fanar-1-9B, Aya-Expanse-8B, Falcon-H1-7B) first get a 300-text smoke test, then one full run with seed 42. Jais-2 and Qwen3 run in the afternoon after the BERTs; Fanar, Aya and Falcon-H1 overnight. The best LLM on dev macro F1 then gets more seeds (43, 44); other LLMs get more seeds only if they come out close to it.
- **Why:** BERT runs take ~3 min each, so 3 seeds cost nothing. One seed per LLM takes 1.4–6.5 h (~15 h for all five), and 3 seeds each would be ~45 h. Spending the extra seeds on the best LLM gives a mean ± std where it matters for the comparison with the BERTs. Single-seed LLM scores are marked as such and are not treated as results until they have seeds.
- **Alternatives considered:** 3 seeds for every LLM (~45 h); LLMs skipped for sentiment.

## SD-004 [SA] — 2026-10-16 06:50 — First synthetic sets: open, zero-shot, 4 generators, 500 per cell, BERTs only
- **Decision:**
  - Condition 2 (open) first. The prompt fixes only the variety (ArSarcasm-v2 region label msa/egypt/gulf/levant; magreb left out, 37 train tweets) and the sentiment class, with a one-line definition of each class. Zero-shot: no real tweets in the prompt. Template `prompts/sentiment/open_v1.json`.
  - Four generators, same plan: Jais-2-8B, Fanar-1-9B, Qwen3-8B, Aya-Expanse-8B (4-bit NF4). Sampling as in the dialect configs (T 1.0, top-p 0.95, top-k 50), max 96 new tokens, seed 42.
  - 500 synthetic tweets per variety × sentiment cell (12 cells, 6,000 per set). 650 requested per cell; the shared filter (exact / near duplicates within the set and against S1 train and dev, Arabic script, 2–60 words; `configs/filtering/sentiment.json`) runs first, then a seeded sample of 500 per cell is kept (`src/sentiment/select_synthetic.py`). Overlap with the official test set is reported, not filtered.
  - Classifiers: MARBERTv2, AraBERTv02-Twitter, MARBERT, seeds 42/43/44, same recipe as SR01; run SR02, one member per classifier × generator set. (Renumbered 2026-10-16 by Ammar: SG01 = the zero-shot generation with all four generators, SR02 = training on SG01; file and folder names keep the earlier sg01–sg04 / sr02–sr05 numbering.) LLM classifiers only after the BERT results are seen.
  - Later controls for condition 3: variety, sarcasm (NEG/NEU only: 51 of 1,930 sarcastic train tweets are POS) and length.
- **Why:** Ammar's choices (2026-10-16). A uniform 500 per cell balances variety and class without making any cell mostly synthetic by a large margin (largest: gulf POS 107 real → 607). BERT runs are ~3 min, LLM runs ~2–5 h on 17k texts, so BERTs give the generator comparison overnight. Zero-shot keeps real tweets out of the prompts, so the synthetic set measures the generator alone.
- **Alternatives considered:** 1,000 per cell (synthetic would outnumber real in 8 of 12 cells); filling cells to a floor of 500; bringing NEG/POS up to NEU; few-shot k=3; small (1–4B) generators (kept as a possible size ablation); LLM classifiers now (~15 h per set per seed).
- **Open:** whether a classifier gains unfairly from data its own model generated (needs a crossover design, e.g. Jais-2 and Fanar each trained on both sets).

## SD-005 [SA] — 2026-10-17 — Quality measures for the SG01 sets; ALDi and E5 back for measurement only
- **Decision:** Measure each SG01 selected set, next to a real S1 reference, with: imbalance (max : min cell count), MSA share and dialectness (Sentence-ALDi; MSA cutoff = best msa/dialect split on S1 train), lexical diversity (MTLD), topic spread (how many of 30 k-means topics of S1 train E5 embeddings get ≥ 1% of the texts), semantic diversity (Vendi on E5), repeats (exact + near duplicates in the raw output) and sentiment fidelity (share predicted as the requested class by the SR01 MARBERT classifiers, 3 seeds, mean probabilities). Size-dependent measures on seeded samples of 3,000. Script `src/sentiment/measure_quality.py`, run SQ01.
- **Why:** Ammar's column list (2026-10-17); definitions proposed and accepted. The filter only removes surface duplicates; these measures describe diversity, dialect and label quality, which the SR02 results alone cannot explain.
- **Scorers:** Sentence-ALDi and multilingual-e5-large were dropped from the roster on 2026-10-10 (as scorers/filters); Ammar approved them again for measurement only, not filtering. CAMeLBERT DID stays dropped.
- **Limits:** the fidelity classifiers are ~80% accurate on dev, so fidelity is an estimate (the real reference row gives their dev accuracy); the classifiers were trained on real tweets, so a generator that writes "typical" sentiment can score above real data. No test data is used.

## SD-006 [SA] — 2026-10-18 — Jais-2-8B is a classifier only in the sentiment track, not a generator
- **Decision:** Jais-2-8B is dropped as a sentiment generator and kept as the main sentiment classifier. Later sentiment generation (open and controlled) uses Fanar-1-9B, Qwen3-8B and Aya-Expanse-8B.
- **Why:** Ammar's decision. Jais-2 is by far the worst generator: in SQ01 its SG01 output had 77.7% repeats (others 0.1–3.8%), it could not fill its cells (imbalance 62.5 : 1 vs 1.0 : 1), and its lexical and semantic diversity were among the lowest (MTLD 339.3, Vendi 2.8), so its set was never trained on in SR02. As a classifier it is the best in the roster: SR01 dev macro F1 80.47 ± 0.66 (3 seeds) and test 67.02 ± 1.03, ahead of Fanar (79.42 dev, 1 seed), Aya (79.36 ± 0.79) and every BERT (best MARBERT 78.68 ± 0.42). Numbers from `docs/sentiment/tables/sg01_quality.md` and `sentiment_summary.md`.
- **Side effect:** Jais-2 never classifies data it generated itself, so the self-generation question left open in SD-004 does not arise for it (it still applies to any other model used in both roles).
- **Alternatives considered:** Fixing Jais-2 generation (e.g. other sampling settings or prompts) to keep four generators; not tried.

## SD-007 [SA] — 2026-10-21 — Four more BERT classifiers; SR03 = real only without NEU
- **Decision:**
  - New sentiment classifiers: CAMeLBERT-mix (`CAMeL-Lab/bert-base-arabic-camelbert-mix`), CAMeLBERT-DA (`CAMeL-Lab/bert-base-arabic-camelbert-da`), ARBERT (`UBC-NLP/ARBERT`) and ARBERTv2 (`UBC-NLP/ARBERTv2`). They join SR01 and SR02 (all three SG01 sets) with the MARBERT recipe unchanged (lr 5e-5, batch 24, 3 epochs, dropout 0.3, 8 frozen layers, max length 128), seeds 42/43/44.
  - SR03: real only (S1) with every NEU tweet dropped from train, dev and test (6,069 / 675 / 2,252 tweets), 2-class NEG/POS head, all 12 classifiers (7 BERTs, 5 LLMs with their SR01 QLoRA recipes), seeds 42/43/44. Implemented as an optional config field `classes` (default NEG/NEU/POS) in `src/sentiment/common.py` and both trainers.
- **Why:** Ammar's choices (2026-10-21). Both CAMeLBERT variants and both ARBERT versions, as MARBERT v1/v2 are both in. SR03 isolates NEG vs POS, the part of the task the WANLP F1-PN metric scores, from the NEU class that drives the dev→test drop.
- **Not comparable:** SR03 macro F1 is over two classes on a NEG/POS-only dev and test, so it cannot be compared with SR01/SR02 macro F1 or F1-PN (those are 3-class models scored on all tweets). Ammar is aware and wants the runs anyway; rescoring SR01 on the NEG/POS subset was offered and not wanted.
- **Cost:** ~2.5 h for the new BERTs in SR01/SR02, ~30 min for the SR03 BERTs, ~16 h for the SR03 LLMs (estimated from SR01 times scaled to the smaller data). Queue `scripts/sentiment/queue_sr03.sh`.
- **Not in the dialect roster:** these four models are used in the sentiment track only.

## SD-008 [SA] — 2026-10-23 — Measure label agreement on S1 dev by relabelling a sample
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

## SD-009 [SA] — 2026-10-26 — Activation steering of Fanar for controlled sentiment generation
- **Decision:** Implement the steering plan (claude.ai doc "Steering Plan — ArSarcasm Sentiment") in `src/sentiment/steering/`:
  - **Generator:** Fanar-1-9B-Instruct, 4-bit NF4. ALLaM (named in the plan) was dropped from the roster; Jais-2 is classifier-only (SD-006).
  - **Vectors (run ID prefix SV):** residual-stream DiffMean from S1 train only: v_pos, v_neg, v_neu (one-vs-rest, non-sarcastic tweets), v_sarc (sarcastic vs non-sarcastic NEG), plus neg_withsarc (ablation: v_neg built with sarcastic tweets). Every vector is built pooled and per-dialect-averaged. Config `configs/sentiment/steering/sv01_fanar.json`.
  - **Neutral is steered too** (Ammar), so steered sets stay 3-class like S1.
  - **Methods, each a synthetic set (Mirror mix only):** prompt only, DiffMean, prompt + DiffMean, LAPE neurons, AP neurons. Count-matched, 500 per variety × sentiment cell as in SG01.
  - Layer, alpha and token budget are chosen on generated text scored by the SR01 classifiers (dev-trained); test is never used.
  - Every set gets a row in the dataset quality table (Google Sheet tab 08_DATASET_RATING, via `scripts/measure_dataset_quality.py`) before training (CLAUDE.md rule, 2026-10-26).
- **Why:** SQ01 showed open zero-shot sets are narrow and "too clean" (fidelity 89–98% vs 80% real), and SR02 gave no gain. Steering controls the label through the model's internals, and alpha sets how strong the signal is.
- **Step 0 finding (S1 train crosstab, magreb excluded):** MSA is 78.6% of NEU, 65.3% of POS and 58.0% of NEG; Egyptian is 43.8% of sarcastic NEG (751/1,713) against 20.6% of non-sarcastic NEG (491/2,381). The plan's rule ("skewed → average inside each dialect") therefore applies; per-dialect vectors are the default, pooled ones the ablation. Each vector's cosine with an egypt-vs-msa direction is logged to show how much dialect a pooled vector carries.
- **Parked (Ammar, 2026-10-26):** the Boost mix (until Ammar is back), fluency measurement, and a dialect classifier for generated text (ALDi in the quality table covers dialectness).
- **Alternatives considered:** SAE features (public SAEs only for Qwen3-8B-Base); attention-head steering (possible extension).

## D-010 [both] — 2026-10-27 — Script and code-switching are not control factors
- **Decision:** Controlled generation varies dialect, class, topic and sentence length only. Every generated text is Arabic script with Arabic words only (no Arabizi, no English / French words); the template states this as a fixed requirement. Script and code-switching are only measured, as a description of each dataset (quality row 8 in CLAUDE.md).
- **Why:** Ammar's choice. No Latin words are to be generated at all.
- **Changed:** `prompts/controlled_v1.json` (script and code-switching options removed, fixed Arabic-only lines added), `configs/generation/controlled_v1_fanar.json` (grid 15 topics x 3 lengths = 45 per dialect, was 270), `src/generation/prompts.py` (grid and instructions), `src/quality/measure.py` (adherence checks the fixed Arabic script / no foreign words). No data had been generated with `controlled_v1`, so nothing is invalidated.
- **Also (same day):** code-switching level is measured as the share of Latin-script words in a text, not a count: none 0%, light above 0% and below 20%, heavy 20% or more (hand-set; at about 14 words per tweet, 1–2 Latin words are light, 3+ heavy). Links and @mentions are removed before counting.

## D-011 [both] — 2026-10-27 — One universal quality matrix for every dataset
- **Decision:** Every dataset, real and generated, in both tracks, is rated with the same 8-row matrix (table "Dataset quality metrics" in CLAUDE.md). Results go to the Google Sheet tabs `08_DATASET_RATING`, `08b_RATING_DETAILS`, `10_LEXICAL_DIVERSITY`, `11_DIALECTNESS`, `12_TOPIC_DIVERSITY`. No generated set is trained on before its rows exist. Rows are shown to Ammar before they are written. Choices within the matrix:
  - **Dialectness:** Sentence-ALDi (`VARabi/Sentence-ALDi`) replaces the stand-in ridge n-gram scorer used in the sheet. Old stand-in rows are marked "stand-in".
  - **MSA cut-off:** Sentence-ALDi below 0.11, for every dataset. Replaces SG01's 0.175 (SD-005).
  - **Lexical diversity:** MTLD is the main score (30 samples of exactly 5,000 tokens), plus distinct-2, hapax share and Self-BLEU (1,000 texts, seeds 0–4). TTR is dropped.
  - **Topic diversity:** effective topics against frozen E5 k-means topic lists (30 topics). There are two lists: a universal one (an equal sample of every real training split) and a per-track one (DI: D1; SA: ArSarcasm-v2 train). These replace the sheet's NMF word-topic model. Generated data, MLADI dev and ArSarcasm-v2 test are never in a topic pool. Robustness is checked with 10, 20 and 50 topics and seeds 0–4. Vendi on E5 is an independent check.
  - **Fidelity judge:** DI uses LahjatBERT `cl_cardinality` (the requested dialect counts as confirmed at probability 0.3 or higher). SA uses the real-only SR01 classifiers.
  - **Generated sets:** the labelling columns (trust: train, trust: test, agreement, error: train) are N/A.
  - **Datasets:** raw files are in `data/datasets/`. QADI uses its test split only. ArSenTD-LEV is deduplicated first.
  - Sentence-ALDi, multilingual-e5-large and LahjatBERT are measurement tools only. They are not part of the model roster.
- **Why:**
  - A single matrix makes any two rows comparable (Ammar).
  - The stand-in scorer puts MSA at about 0.1–0.2 and under-scores Maghrebi.
  - An NMF topic model fitted on one dataset cannot be compared across datasets.
  - TTR depends on text length. MTLD and TTR ranked the 49 tab-10 rows almost the same way (Spearman 0.909), so dropping TTR loses little.
  - QADI's training labels come from user location. About 31% of ArSenTD-LEV is repeats.
- **Alternatives considered:** keep the stand-in scorer and NMF (rejected: not comparable across datasets); keep TTR next to MTLD (rejected by Ammar); a per-dataset topic model (rejected: it would force topics onto single-topic sets).

## D-012 [both] — 2026-10-28 — One decision log for both tracks
- **Decision:** The sentiment log (`docs/sentiment/decisions.md`, SD-001 to SD-009) is merged into `docs/decisions.md` in date order. All IDs are kept, so existing references to them still work. Each heading carries a track tag: `[DI]`, `[SA]` or `[both]`. New decisions in either track use the shared `D-NNN` sequence. `docs/sentiment/decisions.md` now only points here. Sentiment `data.md` and `progress.md` stay separate.
- **Why:** Ammar's choice. Many decisions now apply to both tracks (quality matrix, generation rules), and one log avoids splitting them.
- **Supersedes:** the separate sentiment log from SD-001.

## D-013 [DI] — 2026-10-28 — controlled_v1 settings: length kept; size and few-shot vary
- **Decision:**
  - **Length buckets:** kept as they are: short 3–7, medium 8–15, long 16–30 words, in equal thirds. For comparison, D1's thirds are 7 or fewer, 8–14, and 15 or more words (median 10).
  - **Requests per dialect (`per_dialect`) and few-shot examples (`few_shot.k`):** experiment variables that change between runs. Within any open vs controlled comparison, both conditions use the same values.
- **Still open:** the topic list (keep the 15 hand-written topics, or name them from the D1 topic groups) and `label_mode` (settled in D-014). `target_only` labels the 17 non-requested dialects as invalid. That is often wrong in a multi-label task: in MLADI, 90% of Palestine-valid sentences are also valid for Jordan. `target_unknown` needs a loss mask in `train_classifier.py`.
- **Why:** Ammar, 2026-10-28.

## D-014 [DI] — 2026-10-28 — Generated texts: only the requested dialect is labelled
- **Decision:** Open and controlled generation use `label_mode: target_unknown`. The requested dialect is labelled 1, and the other 17 dialects are unknown (`null`). Training skips the unknown labels with a loss mask, so they add no loss. Validation and model selection use real data only.
- **Why:** The task is multi-label, and many sentences are valid in several dialects (in MLADI, 90% of Palestine-valid sentences are also valid for Jordan). Setting the other 17 to 0 (`target_only`) would teach false "not this dialect" labels. Synthetic data could then hurt because of label noise rather than text quality, which would confound open vs controlled. The real data (D1) already has multi-dialect labels.
- **To do before the first augmented run:** `src/training/train_classifier.py` cannot use these labels yet. It needs (1) a masked BCE loss that ignores `null` labels and (2) loading of real + synthetic files, with the validation split taken from the real data only.
- **Alternatives considered:**
  - `target_only`: can be kept as an ablation.
  - Labelling the other 17 dialects with LahjatBERT `cl_cardinality`: rejected, because it is the fidelity judge (D-011) and would end up grading its own labels.
