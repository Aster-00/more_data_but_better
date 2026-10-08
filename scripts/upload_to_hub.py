"""Upload a trained run's model to the Hugging Face Hub for the MLADI leaderboard, then check it.

Steps:
  1. create a public model repo (the leaderboard Space can only load public models)
  2. upload results/runs/<run>/model/ plus a model card built from train_log.json
  3. re-score the uploaded copy on the MLADI dev set, loaded from the Hub by name the way
     the Space loads it, and require the same macro F1 as the local run
  4. append the repo id, commit and both dev scores to results/submissions.jsonl

The leaderboard submission itself is made by hand in the Space's web form
(model name, the commit printed here, inference method predict_binary_outcomes).

Usage:
  python -m scripts.upload_to_hub --run baseline_real_only_marbertv2_seed44 --repo mladi-marbertv2-r03
  python -m scripts.upload_to_hub --run ... --repo ... --dry-run     # write the card only, no upload
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from huggingface_hub import HfApi

from src.data.build_dataset import DIALECTS, git_commit
from src.evaluation.evaluate_dev import evaluate

DEV = Path("MLADI/dev/NADI2024_subtask1_dev2.tsv")


def model_card(run: str, log: dict, run_id: str) -> str:
    """Model card: what the model is, how it was trained, how to use it, its dev score."""
    cfg, m = log["config"], log["dev"]["macro"]
    return f"""---
language: ar
pipeline_tag: text-classification
base_model: {cfg["model"]}
tags: [arabic, dialect-identification, multi-label, mladi, nadi]
---

# {run_id}: multi-label Arabic dialect identification

Fine-tuned from `{cfg["model"]}` for multi-label country-level dialect identification
(18 sigmoid outputs, one per country). Bachelor thesis project, German International University.

- **Training data:** NADI 2020/2021/2023 training tweets with the LahjatBERT multi-label labels
  ({log["n_train"] + log["n_val"]:,} unique texts, file `{Path(cfg["data"]).name}`; links and mentions
  replaced, no other normalization).
- **Recipe:** lower {cfg["freeze_layers"]} encoder layers frozen, dropout {cfg["dropout"]}, AdamW lr {cfg["learning_rate"]},
  {cfg["warmup_steps"]} warmup steps, batch {cfg["batch_size"]}, {cfg["epochs"]} epochs, fp16, max length {cfg["max_length"]},
  seed {cfg["seed"]}; epoch chosen by macro F1 on a 10% validation split of the training data.
- **Use:** sigmoid over the 18 logits, a dialect is valid if its probability is >= {cfg["threshold"]}
  (MLADI leaderboard method `predict_binary_outcomes`).
- **Label order:** {", ".join(DIALECTS)}.
- **MLADI dev set (120 sentences, 8 dialects):** macro F1 {m["f1"]:.2f}, precision {m["precision"]:.2f}, recall {m["recall"]:.2f}.
- Training run `{run}`, code commit `{log["git_commit"]}`.
"""


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True, help="folder under results/runs/")
    p.add_argument("--repo", required=True, help="repo name under the logged-in account")
    p.add_argument("--run-id", default=None, help="progress.md ID for the card, e.g. R03-marbertv2")
    p.add_argument("--device", default="cuda")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    run_dir = Path("results/runs") / args.run
    with open(run_dir / "train_log.json", encoding="utf-8") as f:
        log = json.load(f)
    card = model_card(args.run, log, args.run_id or args.repo)
    (run_dir / "model" / "README.md").write_text(card, encoding="utf-8")
    if args.dry_run:
        print(card)
        return

    # Upload the model folder (weights, config, tokenizer, card) to a public repo.
    api = HfApi()
    repo_id = f"{api.whoami()['name']}/{args.repo}"
    api.create_repo(repo_id, private=False, exist_ok=True)
    info = api.upload_folder(repo_id=repo_id, folder_path=run_dir / "model",
                             commit_message=f"Upload {args.run} (code {log['git_commit'][:7]})")
    commit = info.oid

    # Load from the Hub by name, as the Space does, and compare with the local dev score.
    hub_scores, _ = evaluate(repo_id, DEV, log["config"]["threshold"], args.device)
    local_f1, hub_f1 = log["dev"]["macro"]["f1"], hub_scores["macro"]["f1"]
    ok = abs(local_f1 - hub_f1) < 0.01
    record = {"repo_id": repo_id, "commit": commit, "run": args.run, "run_id": args.run_id,
              "local_dev_macro_f1": local_f1, "hub_dev_macro_f1": hub_f1, "match": ok,
              "upload_code_commit": git_commit(), "inference_method": "predict_binary_outcomes"}
    with open("results/submissions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, indent=2, ensure_ascii=False))
    if not ok:
        sys.exit("Hub copy scores differently from the local run: do not submit.")


if __name__ == "__main__":
    main()
