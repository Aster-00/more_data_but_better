# Thesis Decisions Log

A running record of decisions made during chats with Claude. Newest entries at the bottom.

<!-- Entry format:
## YYYY-MM-DD — Short title
- **Decision:** what was decided
- **Why:** reasoning
- **Alternatives considered:** (if any)
-->

## 2026-10-05 — Decisions log location
- **Decision:** Keep the decisions log at `code/decisions.md`.
- **Why:** User preference; keeps it alongside the thesis code.
- **Alternatives considered:** `F:\Thesis\decisions.md` (top of the Thesis folder).

## 2026-10-06 — Joining NADI text with LahjatBERT labels
- **Decision:** Join the LahjatBERT label CSV to the NADI tweets through the tweet text, not the `(nadi_source, train_id)` key alone, and keep one record per unique text (now in `src/data/build_dataset.py`). When copies of a text carry different labels (21 texts), take the majority per dialect, with ties counted as valid, and set `label_conflict`. No text normalization at this stage.
- **Why:** LahjatBERT assigned IDs by text lookup, so every duplicated text points at one ID (381 of the 383 "missing" tweets have an exact-text twin). Joining on text recovers 58,384 labelled unique texts, leaving only 2 tweets unlabelled.
- **Alternatives considered:** Joining on the ID only, which would drop 383 tweets and duplicate 320 keys. For the 21 conflicting texts, dropping them or counting ties as not valid was considered and rejected as not worth it: 19 of them are 1-vs-1 ties, and together they are 0.04% of the data, too few to affect results.

## 2026-10-06 — Replace links and mentions
- **Decision:** Replace links with `URL` and @mentions with `USER` (now in `src/data/build_dataset.py`). Both steps can be switched off, and the original text is kept in `text_raw`. No other normalization is applied.
- **Why:** This makes NADI 2020 (raw links and handles) consistent with 2021 and 2023, which the organizers had already masked. It follows what LahjatBERT's `preprocess.py` intends; their version strips punctuation first, so their URL pattern never matches.
- **Alternatives considered:** Copying the full LahjatBERT `cleaning()` function. Rejected because it also deletes Latin script, emoji and stopwords, and merges letter variants, which conflicts with script and code-switching being experimental factors.

## 2026-10-06 — One build script; undo double-escaped quotes
- **Decision:** Joining and cleaning run in one script, `src/data/build_dataset.py`, which writes `data/processed/nadi_lahjatbert.jsonl` with `text` (cleaned) and `text_raw` (original tweet). It also undoes the double escaping of 365 quoted NADI 2021 tweets.
- **Why:** The user wants the clean data generated in one run. The escaping is a file-format artifact: `"""…\""…"""` in the file is `…"…` in the actual tweet. LahjatBERT's pandas reader removes only one layer, leaving the wrapping quotes and `\"` in the text.

## 2026-10-06 — Environment, evaluation and baseline recipe
- **Decision:** Use a project venv (`.venv`, Python 3.12, torch 2.14.1+cu126, transformers 5.18, versions pinned in `requirements.txt`). Score the dev set with `src/evaluation/evaluate_dev.py`, using exactly the leaderboard's `predict_binary_outcomes` settings (raw text, max_length 128, sigmoid, threshold 0.3); macro F1 is the main metric. Train the real-only baseline with `src/training/train_classifier.py` + `configs/baseline_real_only.json`, following LahjatBERT's recipe (MARBERT, first 8 layers frozen, fp16, lr 5e-5, warmup 500, batch 24, 90/10 train/val split, early stopping), with two fixes: dropout 0.3 is passed when the model is built (LahjatBERT sets it afterwards, so their dropout stays 0.1, verified), and the best checkpoint is chosen by validation macro F1 instead of micro F1.
- **Why:** Dev scores should predict leaderboard scores, and the official metric is macro F1. Our metric code reproduces the NADI scorer's reference numbers exactly (38.14 / 50.33 / 42.47 / 50.83).
- **Reference numbers (dev, macro F1):** LahjatBERT_cl_cardinality 72.68, LahjatBERT_cl_aldi 70.27, LahjatBERT_baseline 67.41.
