# CLAUDE.md

Context for Claude Code working in this repository. Keep this file current: when a decision in "Open questions" is settled, move it into the relevant section.

## What this project is

Bachelor thesis at the German International University (GIU), Winter 2026.

- **Title:** More Data But Better: Controllable Synthetic Data for Low-Resource Arabic Sentiment and Dialect Classification
- **Topic ID:** 23101
- **Student:** Ammar (Informatics and Computer Science)
- **Supervisor:** Dr. Caroline Sabty

**Central question:** which synthetic-data strategy actually helps low-resource Arabic classification? A bigger LLM-generated dataset is not automatically a better one: synthetic examples tend to repeat vocabulary, topics, sentence patterns and code-switching styles. The thesis tests whether *controlled* generation beats *open* generation when the extra data is used to train a real classifier.

## Scope decisions so far

- **Task:** Arabic dialect identification, framed as **multi-label** (a sentence can be valid in several dialects), not single-label.
- **Dialect coverage:** Arabic dialects in general. This is not an Egyptian-only project.
- **Test set:** MLADI (human-labelled, multi-label), an extended NADI 2024 test set: 1,000 sentences, labelled for 11 dialects (Algeria, Egypt, Iraq, Jordan, Morocco, Palestine, Saudi_Arabia, Sudan, Syria, Tunisia, Yemen). The labels are **private**. The only way to evaluate is to submit a model to the public leaderboard Space https://huggingface.co/spaces/AMR-KELEG/MLADI. The Space loads a Hub model repo by name and commit and runs one of its fixed inference methods, e.g. `predict_binary_outcomes`: 18 sigmoid logits in the order Algeria, Bahrain, Egypt, Iraq, Jordan, Kuwait, Lebanon, Libya, Morocco, Oman, Palestine, Qatar, Saudi_Arabia, Sudan, Syria, Tunisia, UAE, Yemen, with a fixed 0.3 threshold and max_length 128. Every submission shows up publicly. Cite Keleg, Goldwater & Magdy (ACL 2025) and NADI 2024.
- **Multi-label dev set:** `MLADI/dev/NADI2024_subtask1_dev2.tsv` has 120 sentences labelled for 8 dialects (no Iraq, Morocco or Saudi_Arabia). This is the only local human multi-label gold, so use it for model selection and threshold checks.
- **Training / seed data:** the LahjatBERT label set over NADI 2020 / 2021 / 2023 tweets. The tweet text has arrived, in `MLADI/train/`: about 58.8k single-label, geolocation-labelled tweets over 18 countries. Alternative datasets with the same qualities are being scouted in parallel.
- **Label trust rule:** human labels are the evaluation reference. Automatically labelled data (geolocation, keyword lists, LLM labels) is acceptable for training only, and only when validated against human gold.
- **Models:** see "Model roster" below.
- **Cost constraint:** open-source, zero-cost models only. Do not add paid API dependencies.

## Model roster

Final model set (decided 2026-10-08; four BERTs added for sentiment 2026-10-21, SD-007): classifiers MARBERTv2, AraBERTv02-Twitter, MARBERT v1, CAMeLBERT-mix, CAMeLBERT-DA, ARBERT, ARBERTv2, Qwen3-8B, Jais-2-8B, Falcon-H1-7B, Aya-Expanse-8B; Fanar-1-9B kept. **No longer used** (files kept on disk, their scores in `docs/tables/` kept as they are): TF-IDF + LR, Gemma-2, ALLaM, NLLB (never run), the scorers (CAMeLBERT DID, Sentence-ALDi, multilingual-e5-large; changed 2026-10-10). Open: the leaderboard Space runs on `cpu-basic` (no GPU, ~16 GB RAM) and loads `AutoModelForSequenceClassification` without `trust_remote_code`; transformers has no sequence-classification class for Jais-2, Falcon-H1 or Aya (Cohere), and 7–9B models do not fit its memory, so the trained large models cannot be scored there as it stands (ask the organizer).

Checked on the Hub on 2026-10-06. About 6.7 GB of the 8 GB of VRAM is free. Peak VRAM figures are from G01 (generation, 4-bit, batch 5, 48 new tokens).

| Role | Hub ID | Size | Fits 8 GB? | Status | Notes |
|---|---|---|---|---|---|
| Generator, classifier (R08) | `QCRI/Fanar-1-9B-Instruct` | 8.8B | 4-bit only (G01: 5284 MiB) | in use | Tight fit |
| Generator, classifier (R08) | `Qwen/Qwen3-8B` | 8.2B | 4-bit (G01: 6066 MiB) | in use | Added 2026-10-06; thinking mode disabled in `src/generation/llm.py` |
| Generator, classifier (R08) | `tiiuae/Falcon-H1-7B-Instruct` | 7.6B | 4-bit (G01: 5184 MiB) | in use | Added 2026-10-06; Arabic among its languages (Falcon3 has none); hybrid Mamba, batch 1 only for generation |
| Generator, classifier (R08) | `inception42/Jais-2-8B-Chat` | 8.1B | 4-bit (G01: 5750 MiB) | in use | Added 2026-10-06; gated (license accepted on the Hub) |
| Classifier (R08) | `CohereLabs/aya-expanse-8b` | 8B | 4-bit (TODO: peak VRAM) | in use | QLoRA config `configs/lora_real_only_aya.json` |
| Classifier | `UBC-NLP/MARBERTv2` | ~163M | yes | in use | Main classifier |
| Classifier | `aubmindlab/bert-base-arabertv02-twitter` | 135M | yes | in use | |
| Classifier | `UBC-NLP/MARBERT` | ~163M | yes | in use | v1; compared with v2 in R03 |
| Classifier (sentiment) | `CAMeL-Lab/bert-base-arabic-camelbert-mix` | ~110M | yes | in use | Added 2026-10-21 (SD-007); SR01–SR03 |
| Classifier (sentiment) | `CAMeL-Lab/bert-base-arabic-camelbert-da` | ~110M | yes | in use | Added 2026-10-21 (SD-007); SR01–SR03 |
| Classifier (sentiment) | `UBC-NLP/ARBERT` | ~163M | yes | in use | Added 2026-10-21 (SD-007); SR01–SR03 |
| Classifier (sentiment) | `UBC-NLP/ARBERTv2` | ~163M | yes | in use | Added 2026-10-21 (SD-007); SR01–SR03 |
| Generator | `google/gemma-2-9b-it` | 9.2B | 4-bit only (G01: 6174 MiB) | dropped | Gated: accept the license and use an access token |
| Generator | `humain-ai/ALLaM-7B-Instruct-preview` | 7.0B | 4-bit (G01: 4562 MiB) | dropped | |
| Generator | `facebook/nllb-200-1.3B` | 1.3B | yes | dropped | Translation / back-translation. Downloaded, never run |
| Generator | `facebook/nllb-200-distilled-1.3B` | 1.3B | yes | dropped | Same. Downloaded, never run |
| Generator | GPT-4o-mini (optional) | — | remote | not used | Paid: conflicts with the zero-cost rule |
| Scorer (fidelity) | `CAMeL-Lab/bert-base-arabic-camelbert-mix-did-nadi` or `-did-madar-corpus26` | ~110M | yes | dropped | S01 favoured `-did-nadi` |
| Scorer (dialectness) | `VARabi/Sentence-ALDi` | ~110M | yes | dropped | |
| Scorer (diversity) | `intfloat/multilingual-e5-large` | 560M | yes | dropped | |
| Classifier | TF-IDF + logistic regression | — | CPU | dropped | Dev-only reference (cannot be submitted to the leaderboard) |

## Experimental design

The same classifier is trained under three conditions and evaluated on the same real, unseen test set:

1. **Real only** (baseline)
2. **Real + open synthetic** (ordinary, unconstrained LLM generation)
3. **Real + controlled synthetic** (prompts specify the control factors)

Control factors for condition 3: dialect, class, topic, sentence length. Script and code-switching are not control factors (D-010, 2026-10-27): every generated text is Arabic script with Arabic words only; script and code-switching are only measured, as dataset properties (quality row 8). The augmentation should aim for class balance and for diversity across topics and dialects.

Before training, the generated sets are compared with:

- duplicate and near-duplicate filtering
- embedding-based diversity measures
- lexical diversity
- label-consistency checks / dialect fidelity (does the text really belong to the dialect it was generated for)
- agreement statistics such as Cohen's kappa where a second labeller (human or model) is involved

**Learning curves:** repeat the three conditions at several real-data sizes to test whether synthetic data helps most when real data is scarce.

The supervisor's standing question is "more data vs better data", so every experiment should make it possible to separate the effect of *quantity* from the effect of *quality*. When comparing open vs controlled synthetic data, match the number of synthetic examples.

## Dataset quality metrics

One universal matrix rates every dataset, real and generated, the same way, so any two rows are comparable. Results go to the thesis Google Sheet (https://docs.google.com/spreadsheets/d/1ar52kcOnueAYdcmszD1yPToYJjZyYLZ6E2UQ1ok5q3o): summary in tab `08_DATASET_RATING` (explanations in `08b_RATING_DETAILS`), details in `10_LEXICAL_DIVERSITY`, `11_DIALECTNESS`, `12_TOPIC_DIVERSITY`. Every generated dataset gets its rows in all four tabs before training. Show Ammar the rows before writing them to the sheet. (Ammar, 2026-10-26 / 2026-10-27.)

| # | Parameter | How we rate it |
|---|---|---|
| 1 | Class balance | Imbalance = largest class count / smallest class count (multi-label: valid texts per dialect). Generated sets: over the requested labels. |
| 2 | Dialect coverage | Which dialects occur and how many texts each has. MSA share = share of texts with Sentence-ALDi below 0.11 (one cut-off for every dataset; SG01's 0.175 is replaced). |
| 3 | Dialectness | Mean Sentence-ALDi score (0 = MSA, 1 = fully dialectal), plus shares below 0.11 and above 0.5. All texts, or a random 20,000 for larger splits. Rows from the old stand-in scorer are marked "stand-in". |
| 4 | Lexical diversity | **MTLD** (main score) on 30 random samples of exactly 5,000 tokens, plus distinct-2 and hapax share on the same samples. **Self-BLEU** on 1,000 texts, seeds 0–4: do texts copy each other's phrasing? Shared tokenisation of `scripts/quality/measure_dataset_quality.py` for all. TTR is not used. |
| 5 | Semantic / topic diversity | **Vendi** on E5 embeddings (2,000 texts, mean of seeds 0–4). **Topic spread** = effective topics of 30 (exp of entropy, 800-text samples × 10) against frozen E5 k-means topic lists: a universal list (equal sample of every real training split) and a per-track list (dialect: D1; sentiment: ArSarcasm-v2 train). Generated data, MLADI dev and ArSarcasm-v2 test are never in a topic pool. Robustness: 10 / 20 / 50 topics and seeds 0–4. |
| 6 | Duplication and leakage | Repeats = share of rows that are an exact copy of an earlier row after normalisation, on the set as trained (near-copies before filtering go in 08b). Leakage = share of unique texts also in the evaluation data (MLADI dev for dialect, ArSarcasm-v2 test for sentiment). |
| 7 | Fidelity | Synthetic sets only; N/A for real data. Share of texts whose requested label is confirmed by a fixed judge. Dialect: LahjatBERT `cl_cardinality` (published; requested dialect at probability ≥ 0.3). Sentiment: the real-only SR01 classifiers. A proxy, since the judges make errors. |
| 8 | Script, code-switching and length | Rule-based, `src/quality/measure.py`, after links and mentions are removed. Script per text: Arabic if at least 70% of its letters are Arabic, Arabizi if at least 70% are Latin, otherwise mixed; reported as shares. Code-switching (Arabic-script texts only): share of a text's words that are Latin-script words (2+ letters), none (0%) / light (above 0%, below 20%) / heavy (20% or more); reported as level shares plus the mean Latin-word share. Cut-offs hand-set (Ammar, 2026-10-27): at about 14 words per tweet, 1–2 Latin words fall in light and 3+ in heavy. Length: mean and spread of words per text. A description of the dataset only; generated sets are expected to be Arabic script with no Latin words. |

- Labelling columns (trust, agreement, annotation error) are N/A for generated sets.
- Sentence-ALDi, multilingual-e5-large and LahjatBERT `cl_cardinality` are used here only as measurement tools; this is separate from the model roster above.
- Datasets measured are listed in one config; raw files are in `data/datasets/`. QADI: test split only (its training labels come from user location). ArSenTD-LEV: remove repeated tweets first (about 31%).

### Universal topic pool

One E5 topic list for all texts from all datasets (Ammar, 2026-10-28), cleaned as in D-015, then named by Ammar like D1 (D-016). Pool rules: Arabic script only (per text, at least 70% Arabic letters, as in row 8), written by humans (no machine translation, no LLM output), no song lyrics. Row counts are approximate.

**Included**

| Dataset | Task | Brief | Rows |
|---|---|---|---|
| D1 (NADI 2020/21/23 + LahjatBERT labels) | DI | Tweets, 18 countries | 58k |
| AOC-ALDi (train, dev, test) | DI, dialectness | Reader comments on Arabic news sites (Youm7, Alghad, Alriyadh) with dialectness scores | 128k |
| AOC dialect-classification batch 2 (2010) | DI | Raw crowd-annotation file behind AOC: news comments and article sentences; mostly overlaps AOC-ALDi | 3.3k HITs |
| QADI test | DI | Tweets, 18 countries, human-checked | 3.5k |
| E_MSA_BDs, Bahraini part | SA | Product reviews translated to Bahraini by native speakers | 5k |
| ArSarcasm-v2 train and dev | SA, sarcasm | Tweets | 12.5k |
| Arabic 100k Reviews | SA | Hotel, book, airline and product reviews | 100k |
| ArSen-20 | SA | Tweets, mostly neutral | 20k |
| AJGT | SA | Jordanian tweets | 1.8k |
| AT-ODTSA | targeted SA | Tweets | ~3k |
| Mawqif | stance, SA, sarcasm | Tweets on COVID vaccine, digital transformation, women's empowerment | 4.1k |
| EESA | SA | Egyptian Arabic-English code-switched comments (Arabic-script texts only) | 4.1k |
| ALR | aspect SA | Laptop reviews | ~1.7k |
| MASC | SA | Multi-domain reviews and comments | ~8.9k |
| LABR | SA | Goodreads book reviews | 16k |
| ASTD, ArTwitter, QRCI | SA | Tweets (QRCI noisy) | 4.3k |
| arabic-sentiment-analysis | SA | Tweets labelled through emojis | 58k |
| ATT, HTL, MOV, PROD, RES | SA | TripAdvisor / elcinema / souq / qaym reviews | 34k |
| AfriSenti, Algerian and Moroccan | SA | Tweets in Arabic and Latin script (Arabic-script texts only) | ~9k |

**Excluded**

| Dataset | Task | Brief | Why |
|---|---|---|---|
| Habibi | DI | Song lyrics, 528k lines | Song lyrics |
| E_MSA_BDs, MSA part | SA | Same reviews in MSA | Google Translate (machine) |
| E_MSA_BDs, English part | SA | Original Amazon reviews | Not Arabic |
| MPQA-ar | subjectivity | English news sentences in Arabic | Machine-translated |
| PADIC (`data/datasets/di/PADIC/PADIC.xml`) | DI | Human-translated sentences in 6 varieties | Stored in Buckwalter Latin transliteration, not Arabic script |
| AfriSenti, other 12 languages | SA | Amharic, Hausa and others | Not Arabic |
| QADI train | DI | Tweet IDs only | No text |
| MASC lexicons, EESA lexicon | SA | Sentiment word lists | Not texts |
| MLADI dev, ArSarcasm-v2 test | DI, SA | Evaluation data | Never in a topic pool (D-011) |
| MLADI test | DI | Leaderboard test | No text (private) |
| D2–D4 | DI | Subsets of D1 | Copies of D1 |
| Synthetic sets (G01, SG01) | DI, SA | LLM output | Machine-made (D-011) |

## Pipeline

0. Task and seed data
1. Data loading, cleaning, splits
2. Open generation
3. Controlled generation
4. Filtering (duplicates, label consistency)
5. Quality measurement of each synthetic set
6. Classifier training under the three conditions
7. Evaluation on the real test set, learning curves
8. Analysis and ablations (which control factors and which filters matter)

## Rules for working in this repo

**Evaluation integrity**
- The test set is used for final evaluation only. Never use it for training, model selection, prompt design, few-shot examples or filtering thresholds. Use a dev split carved out of the training data for all of those.
- All three conditions must share the same classifier, hyperparameter budget, splits and metrics. If something differs between conditions, call it out.
- Report multi-label metrics, macro-averaged at minimum, with per-dialect breakdowns.
- Run multiple seeds and report mean and spread. A single-seed difference is not a result.
- befre running any model or long task tell me an estimate of how long it will take

**Reproducibility**
- Record every run in `docs/progress.md`: what was used, what changed from the previous run, the results, and an explanation. Score tables are not written by hand: register the result folder in `configs/runs.json`, regenerate `docs/tables/` (`python -m src.evaluation.summarize_runs`, `python -m src.quality.summarize_quality`) and quote numbers from there. Record decisions of both tracks in the one log `docs/decisions.md` (tag each `[DI]`, `[SA]` or `[both]`) and new data versions in `docs/data.md`.
- Commit the code before a run, so the git commit in its log identifies the exact code.
- Every run is driven by a config file and a fixed seed; log the config, seed, git commit and data version alongside the results.
- Save every prompt template and every generation setting (model, temperature, sampling parameters) with the data it produced. Synthetic examples must be traceable to the prompt and control-factor values that generated them.
- Never hand-edit result files. Tables and figures in the thesis are regenerated by scripts from logged runs.
- Every generated synthetic dataset (open, controlled, steered, any track) is rated with the dataset quality metrics below before it is used for training. No set is trained on without its quality rows. See "Dataset quality metrics".
- Never delete trained models: no weights, adapters, heads (`score_head.pt`) or whole run folders under `results/runs/`, including smoke tests, aborted runs and dropped models. Do not overwrite a run folder either; rerun under a new folder name. Freeing disk space means moving models to backup storage, and only with Ammar's explicit approval.

**Data handling**
- MLADI and the NADI tweet text were obtained under access agreements. Keep raw data out of git (`data/` is gitignored).
- All text is UTF-8. Do not apply Arabic normalization (alef/yaa unification, diacritic stripping, tatweel removal, emoji or Latin removal) implicitly; make it an explicit, configurable step, because script and code-switching are measured properties of the data.
- Keep real and synthetic data in separate files with a `source` field so they can never be confused after merging.

**Honesty**
- Never invent numbers, citations, dataset statistics or paper results. If something is unknown, say so and leave a TODO.
- Negative results are valid findings here. Do not tune until the controlled condition wins.

**Compute**
- The thesis machine is a Windows desktop PC: 12th Gen Intel Core i7-12700 (2.10 GHz, 12 cores / 20 threads), 32 GB RAM, 64-bit x64, NVIDIA GeForce RTX 3070 (8 GB VRAM). CUDA is available locally and this is the default place to run everything.
- 8 GB VRAM is the binding limit. Fine-tuning a BERT-sized classifier such as MARBERT fits comfortably (use mixed precision). Generator LLMs must be small or loaded quantized (4-bit) to fit; check a model's VRAM needs before choosing its size, and say so if it will not fit rather than silently falling back to CPU.
- Keep device selection configurable (`cuda` / `cpu`) so a run can move to a remote GPU if a larger generator is ever needed.
- Generation is the slow stage. Make it resumable: write outputs incrementally and skip examples that already exist.
- Use Windows-safe code: `pathlib` for paths, explicit `encoding="utf-8"` on every file open (the Windows default codepage corrupts Arabic text), and `if __name__ == "__main__":` guards around anything using DataLoader workers or multiprocessing.
- Provide a tiny-subset mode for every script so the pipeline can be checked end to end in minutes.

**Style**
- Python, with type hints and short docstrings. Prefer small scripts with clear inputs and outputs over large notebooks; notebooks are for exploration and figures only.
- Ask before adding heavy dependencies or changing the directory layout.

## Suggested layout

```
configs/        experiment configs (one per run or sweep)
data/           raw/, processed/, synthetic/   (gitignored)
prompts/        open and controlled prompt templates
src/
  data/         loading, cleaning, splits
  generation/   open and controlled generation
  filtering/    dedup, label consistency
  quality/      diversity, fidelity, agreement metrics
  training/     classifier fine-tuning
  evaluation/   metrics, learning curves
scripts/        entry points (index: scripts/README.md)
  topics/       topic pool, topic lists, cluster analysis
  quality/      dataset quality statistics
  generation/   generator checks
  hub/          model download and Hub upload
  queues/       restartable run queues, dialect/ and sentiment/
  system/       machine utilities
notebooks/      figures and exploration only; numbers come from scripts and logged results
results/        logged runs: raw results, console logs (source of every number)
docs/           progress.md (run notes), decisions.md, data.md
  tables/       generated summary tables, each as .csv and .md (never hand-edited)
thesis/         report source
```

## Deadlines

| Date | Milestone |
|---|---|
| 13 Oct 2026 | First interim report (progress so far) |
| 15 Nov 2026 | Second interim report (preliminary results, substantially close to the final thesis) |
| 5 Jan 2027 | Thesis submission (late within one week: minus 10%; later: fail) |
| 19 to 27 Jan 2027 | Defence: 20-minute presentation plus 10-minute Q&A |
| 31 Jan 2027 | Final amended thesis |

Preliminary results are needed by mid-November, so favour a working end-to-end pipeline early over polishing any single stage.

## What is graded

The supervisor scores quality of work, interim reports, presentations and independence; supervisor and reviewer score the written report and the oral defence. Top grades require the implementation to be backed by substantial theoretical or analytical work, so analysis and ablations matter as much as the headline numbers. The thesis text must be Ammar's own writing: when asked for writing help, give drafts and feedback for him to revise, and never fabricate references.

## Current tasks (from the latest supervisor meeting)

1. Justify why MLADI is the test set rather than a held-out part of the LahjatBERT data.
2. Catalogue all data-augmentation techniques gathered from the literature.
3. List all quality measures for augmented data.
4. Start using models for data augmentation (details to follow).

## Open questions

- Final training dataset: the NADI tweet text is now available, but alternatives are still being considered.
- Test-set evaluation budget: the leaderboard is public and evaluates one model at a time, so 3 conditions × seeds × learning-curve sizes would mean many public submissions. Decide which runs to submit, or ask the organizer (Amr Keleg) about batch or private evaluation.
- Final label inventory: country-level labels, or countries regrouped into regions.
- Generators are chosen (see Model roster above), and G01 showed that all of them fit the 8 GB card in 4-bit. Still open: whether GPT-4o-mini is allowed.
- Exact metric set and the real-data sizes for the learning curves.
- Fluency measure for generated text (perplexity, local LLM judge or manual check): parked 2026-10-26, not measured for now.
- Whether sentiment classification stays in scope as a secondary task or is dropped. Update 2026-10-13: sentiment work starts now on ArSarcasm-v2 while waiting for the full MLADI data; its long-term role is still open. The sentiment track has its own code (`src/sentiment/`) and docs (`docs/sentiment/`: data.md, progress.md with SR/SG/SQ run IDs); its decisions are in the shared `docs/decisions.md` (old SD-NNN IDs kept, tag `[SA]`).
- **Pending (raised 2026-10-09): make D4 the default training set for all runs?** D4 is D1 without the 2,271 zero-label texts, with the all-18 texts kept (`nadi_lahjatbert_card1to18.jsonl`). On dev, R07 (D4) is the best setup for MARBERT (72.17 ± 0.75 vs 71.34 on D1) and AraBERTv02-Twitter (70.74 vs 70.52), but not for MARBERTv2 (69.79 vs 70.11 on D1). Decide only after (1) the R07 models uploaded on 2026-10-09 have leaderboard test scores and (2) the processes running now have finished (LLM-classifier queue: Fanar, Jais-2, Falcon-H1, Aya). Until then, keep D1 as the default and do not switch configs. Test so far: MARBERT D4 68.61 (T03) vs D1 68.65 (T04), no difference; AraBERT D4 67.48 (T05) vs D1 67.31 (T02), no difference. Condition (1) is met.