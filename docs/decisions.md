# Thesis Decisions Log

A running record of decisions made during chats with Claude. Newest entries at the bottom.

Each decision has a permanent ID (D-001, D-002, …) and a timestamp (local time, UTC+3). IDs are never reused or renumbered. The exact time of D-001 to D-004 and D-006 was not recorded: D-001 and D-006 have only a date, and D-002 to D-004 show when they were committed (`75330bf`), so they were decided at or before that time.

<!-- Entry format:
## D-NNN — YYYY-MM-DD HH:MM — Short title
- **Decision:** what was decided
- **Why:** reasoning
- **Alternatives considered:** (if any)
-->

## D-001 — 2026-10-05 — Decisions log location
- **Decision:** Keep the decisions log at `code/decisions.md`.
- **Why:** User preference; keeps it alongside the thesis code.
- **Alternatives considered:** `F:\Thesis\decisions.md` (top of the Thesis folder).

## D-002 — 2026-10-06 ≤05:53 — Joining NADI text with LahjatBERT labels
- **Decision:** Join the LahjatBERT label CSV to the NADI tweets through the tweet text, not the `(nadi_source, train_id)` key alone, and keep one record per unique text (now in `src/data/build_dataset.py`). When copies of a text carry different labels (21 texts), take the majority per dialect, with ties counted as valid, and set `label_conflict`. No text normalization at this stage.
- **Why:** LahjatBERT assigned IDs by text lookup, so every duplicated text points at one ID (381 of the 383 "missing" tweets have an exact-text twin). Joining on text recovers 58,384 labelled unique texts, leaving only 2 tweets unlabelled.
- **Alternatives considered:** Joining on the ID only, which would drop 383 tweets and duplicate 320 keys. For the 21 conflicting texts, dropping them or counting ties as not valid was considered and rejected as not worth it: 19 of them are 1-vs-1 ties, and together they are 0.04% of the data, too few to affect results.

## D-003 — 2026-10-06 ≤05:53 — Replace links and mentions
- **Decision:** Replace links with `URL` and @mentions with `USER` (now in `src/data/build_dataset.py`). Both steps can be switched off, and the original text is kept in `text_raw`. No other normalization is applied.
- **Why:** This makes NADI 2020 (raw links and handles) consistent with 2021 and 2023, which the organizers had already masked. It follows what LahjatBERT's `preprocess.py` intends; their version strips punctuation first, so their URL pattern never matches.
- **Alternatives considered:** Copying the full LahjatBERT `cleaning()` function. Rejected because it also deletes Latin script, emoji and stopwords, and merges letter variants, which conflicts with script and code-switching being experimental factors.

## D-004 — 2026-10-06 ≤05:53 — One build script; undo double-escaped quotes
- **Decision:** Joining and cleaning run in one script, `src/data/build_dataset.py`, which writes `data/processed/nadi_lahjatbert.jsonl` with `text` (cleaned) and `text_raw` (original tweet). It also undoes the double escaping of 365 quoted NADI 2021 tweets.
- **Why:** The user wants the clean data generated in one run. The escaping is a file-format artifact: `"""…\""…"""` in the file is `…"…` in the actual tweet. LahjatBERT's pandas reader removes only one layer, leaving the wrapping quotes and `\"` in the text.

## D-005 — 2026-10-06 06:34 — Environment, evaluation and baseline recipe
- **Decision:** Use a project venv (`.venv`, Python 3.12, torch 2.14.1+cu126, transformers 5.18, versions pinned in `requirements.txt`). Score the dev set with `src/evaluation/evaluate_dev.py`, using exactly the leaderboard's `predict_binary_outcomes` settings (raw text, max_length 128, sigmoid, threshold 0.3); macro F1 is the main metric. Train the real-only baseline with `src/training/train_classifier.py` + `configs/baseline_real_only.json`, following LahjatBERT's recipe (MARBERT, first 8 layers frozen, fp16, lr 5e-5, warmup 500, batch 24, 90/10 train/val split, early stopping), with two fixes: dropout 0.3 is passed when the model is built (LahjatBERT sets it afterwards, so their dropout stays 0.1, verified), and the best checkpoint is chosen by validation macro F1 instead of micro F1.
- **Why:** Dev scores should predict leaderboard scores, and the official metric is macro F1. Our metric code reproduces the NADI scorer's reference numbers exactly (38.14 / 50.33 / 42.47 / 50.83).
- **Reference numbers (dev, macro F1):** LahjatBERT_cl_cardinality 72.68, LahjatBERT_cl_aldi 70.27, LahjatBERT_baseline 67.41.

## D-006 — 2026-10-06 — Keep all-18 and zero-label texts (for now)
- **Decision:** Keep D1 as it is: the 7,642 all-18 texts, the 2,271 zero-label texts and the 268 texts that became identical after cleaning all stay in. Diacritics are not stripped.
- **Why:** The real-only baseline trained on D1 (R03-marbert, 71.34 ± 1.03 dev macro F1) already beats LahjatBERT's baseline and matches their best model. Revisit later as an ablation.
- **Update (R04-marbert):** With LahjatBERT's own settings, D1 gives 68.71 ± 0.35, in line with their baseline (67.41). So the gain in R03-marbert comes from the training settings, not from D1; what R04-marbert does show is that D1 is not worse than their data, which still supports keeping it.
- **Update (R05):** Removing the zero-label and all-18 texts (D2) lowers dev macro F1 for all four classifiers (MARBERT 71.34 → 69.25, AraBERTv02-Twitter 70.52 → 69.82, MARBERTv2 70.11 → 64.89, TF-IDF + LR 62.58 → 56.54), mostly through lower recall. Keep D1. D2 is also 17% smaller, so quantity and composition are not separated yet.
- **Update (R06/R07):** Removing only the zero-label texts changes nothing (all models within 0.9 of R03); removing only the all-18 texts costs as much as removing both. The all-18 texts are the useful ones. Keep D1.

## D-007 — 2026-10-09 10:36 — Documentation in `docs/`, score tables generated only
- **Decision:** All documentation and summary tables live in `docs/`: `progress.md` (run notes only, no score tables), `decisions.md` (this file, moved from the repo root, which supersedes D-001's location), `data.md` (data versions), and `docs/tables/` with generated tables, each as `.csv` and `.md`: `split_summary` (R and T: validation, dev and test scores), `quality_summary` (Q), `scorer_summary` (S), `generator_summary` (G). `dev_summary.md/.csv` are removed: their numbers are the dev rows of `split_summary`. The model roster moved from `progress.md` to `CLAUDE.md`. Console logs are tracked in git. `CLAUDE.md` and `README.md` stay at the root.
- **Why:** `progress.md` was hard to scan (about 270 lines, two-thirds tables), and the same numbers were written in several places. Generating every table from the logged results follows the rule "never hand-edit result files" and leaves one source per number.
- **Alternatives considered:** one notes file per run (rejected for now: one file is easier to search before the interim report); keeping `dev_summary` next to `split_summary` (rejected: duplicate numbers).
