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
- **Models** (Hub IDs, sizes and VRAM fit are in `progress.md` → Model roster):
  - Generators: Fanar-1-9B, Gemma-2-9B, ALLaM-7B, NLLB-1.3B, and GPT-4o-mini (optional; it is a paid API, so it conflicts with the cost constraint below).
  - Scorers: CAMeLBERT-mix DID (dialect fidelity), ALDi (dialectness), E5-multilingual-large (embeddings for diversity).
  - Classifiers: MARBERTv2 (main), AraBERTv02-Twitter, TF-IDF + logistic regression.
- **Cost constraint:** open-source, zero-cost models only. Do not add paid API dependencies.

## Experimental design

The same classifier is trained under three conditions and evaluated on the same real, unseen test set:

1. **Real only** (baseline)
2. **Real + open synthetic** (ordinary, unconstrained LLM generation)
3. **Real + controlled synthetic** (prompts specify the control factors)

Control factors for condition 3: dialect, class, topic, script (Arabic script vs Arabizi), sentence length, amount of code-switching. The augmentation should aim for class balance and for diversity across topics and dialects.

Before training, the generated sets are compared with:

- duplicate and near-duplicate filtering
- embedding-based diversity measures
- lexical diversity
- label-consistency checks / dialect fidelity (does the text really belong to the dialect it was generated for)
- agreement statistics such as Cohen's kappa where a second labeller (human or model) is involved

**Learning curves:** repeat the three conditions at several real-data sizes to test whether synthetic data helps most when real data is scarce.

The supervisor's standing question is "more data vs better data", so every experiment should make it possible to separate the effect of *quantity* from the effect of *quality*. When comparing open vs controlled synthetic data, match the number of synthetic examples.

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
- Record every run in `progress.md`: what was used, what changed from the previous run, the results, and an explanation. Copy numbers from the logged files only.
- Commit the code before a run, so the git commit in its log identifies the exact code.
- Every run is driven by a config file and a fixed seed; log the config, seed, git commit and data version alongside the results.
- Save every prompt template and every generation setting (model, temperature, sampling parameters) with the data it produced. Synthetic examples must be traceable to the prompt and control-factor values that generated them.
- Never hand-edit result files. Tables and figures in the thesis are regenerated by scripts from logged runs.

**Data handling**
- MLADI and the NADI tweet text were obtained under access agreements. Keep raw data out of git (`data/` is gitignored) and never upload it to third-party services.
- All text is UTF-8. Do not apply Arabic normalization (alef/yaa unification, diacritic stripping, tatweel removal, emoji or Latin removal) implicitly; make it an explicit, configurable step, because script and code-switching are experimental factors.
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
scripts/        entry points
results/        logged runs, tables, figures
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
- Generators are chosen (see Models above). Still open: whether 9B models in 4-bit leave enough VRAM for generation on the 8 GB card (about 6.7 GB is free), whether GPT-4o-mini is allowed, and which CAMeLBERT DID variant to use (`-did-nadi` or `-did-madar-corpus26`).
- Exact metric set and the real-data sizes for the learning curves.
- Whether sentiment classification stays in scope as a secondary task or is dropped.