"""Upload a QLoRA classifier run (LoRA adapter + classification head) to the Hugging Face Hub.

For R08 runs (src/training/train_lora_classifier.py). Only the adapter is published (~0.2 GB),
not a merged 7-9B model: users load it on top of the base model. The MLADI leaderboard Space
cannot score these models (cpu-basic, no peft support), so this is for sharing, not submission.

Steps:
  1. write a model card from train_log.json into results/runs/<run>/model/README.md
  2. create a public model repo and upload the model folder
  3. download the uploaded files again and check they are byte-identical to the local ones
     (no GPU needed); the dev score in the card is the local run's
  4. append the repo id and commit to results/submissions.jsonl (marked not submittable)

Usage:
  python -m scripts.upload_adapter_to_hub --run lora_real_only_fanar_seed42 --repo mladi-fanar-r08 --run-id R08-fanar
  python -m scripts.upload_adapter_to_hub --run ... --repo ... --dry-run     # write the card only
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

from huggingface_hub import HfApi, snapshot_download

from src.data.build_dataset import DIALECTS, git_commit


def model_card(run: str, log: dict, run_id: str, repo_id: str) -> str:
    """Model card: what the adapter is, how it was trained, how to load it, its dev score."""
    cfg, m = log["config"], log["dev"]["macro"]
    custom = log.get("head", "").startswith("custom")
    load = ("# custom last-token head: see src/training/decoder_head.py in the thesis code"
            if custom else
            f'''from peft import PeftModel
from transformers import AutoModelForSequenceClassification, AutoTokenizer
base = AutoModelForSequenceClassification.from_pretrained(
    "{cfg["model"]}", num_labels=18, problem_type="multi_label_classification")
model = PeftModel.from_pretrained(base, "{repo_id}")
tokenizer = AutoTokenizer.from_pretrained("{repo_id}")
base.config.pad_token_id = tokenizer.pad_token_id''')
    return f"""---
language: ar
library_name: peft
pipeline_tag: text-classification
base_model: {cfg["model"]}
tags: [arabic, dialect-identification, multi-label, mladi, nadi, lora, qlora]
---

# {run_id}: multi-label Arabic dialect identification (LoRA adapter)

LoRA adapter and 18-output classification head on top of `{cfg["model"]}` for multi-label
country-level dialect identification (one sigmoid per country). Bachelor thesis project,
German International University. **Adapter only:** load it on top of the base model.

- **Training data:** NADI 2020/2021/2023 training tweets with the LahjatBERT multi-label labels
  ({log["n_train"] + log["n_val"]:,} unique texts, file `{Path(cfg["data"]).name}`; links and mentions
  replaced, no other normalization).
- **Recipe:** 4-bit NF4 base (frozen), LoRA r {cfg["lora_r"]} / alpha {cfg["lora_alpha"]} / dropout {cfg["lora_dropout"]} on
  {", ".join(cfg["lora_target_modules"])}; classification head trained in full; lr {cfg["learning_rate"]},
  {cfg["warmup_ratio"]:.0%} warmup, micro-batch {cfg["micro_batch_size"]} x {cfg["grad_accum"]} accumulation, {cfg["epochs"]} epochs, bf16,
  max length {cfg["max_length"]}, seed {cfg["seed"]}; epoch chosen by macro F1 on a 10% validation split.
- **Use:** sigmoid over the 18 logits; a dialect is valid if its probability is >= {cfg["threshold"]}.
- **Label order:** {", ".join(DIALECTS)}.
- **MLADI dev set (120 sentences, 8 dialects):** macro F1 {m["f1"]:.2f}, precision {m["precision"]:.2f}, recall {m["recall"]:.2f}
  (scored with the 4-bit base, as trained).
- Training run `{run}`, code commit `{log["git_commit"]}`.

```python
{load}
```
"""


def sha256(path: Path) -> str:
    """SHA-256 of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run", required=True, help="folder under results/runs/")
    p.add_argument("--repo", required=True, help="repo name under the logged-in account")
    p.add_argument("--run-id", required=True, help="run ID (docs/progress.md), e.g. R08-fanar")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    run_dir = Path("results/runs") / args.run
    with open(run_dir / "train_log.json", encoding="utf-8") as f:
        log = json.load(f)
    api = HfApi()
    repo_id = f"{api.whoami()['name']}/{args.repo}"
    card = model_card(args.run, log, args.run_id, repo_id)
    (run_dir / "model" / "README.md").write_text(card, encoding="utf-8")
    if args.dry_run:
        print(card)
        return

    # Upload the adapter folder (adapter, head, tokenizer, card) to a public repo.
    api.create_repo(repo_id, private=False, exist_ok=True)
    info = api.upload_folder(repo_id=repo_id, folder_path=run_dir / "model",
                             commit_message=f"Upload {args.run} (code {log['git_commit'][:7]})")

    # Check the upload: every local file must come back byte-identical from the Hub.
    local = {p.name: sha256(p) for p in (run_dir / "model").iterdir() if p.is_file()}
    with tempfile.TemporaryDirectory() as tmp:
        snapshot_download(repo_id, revision=info.oid, local_dir=tmp)
        remote = {name: sha256(Path(tmp) / name) for name in local if (Path(tmp) / name).exists()}
    ok = remote == local
    record = {"repo_id": repo_id, "commit": info.oid, "run": args.run, "run_id": args.run_id,
              "local_dev_macro_f1": log["dev"]["macro"]["f1"], "files_identical": ok,
              "kind": "lora_adapter", "leaderboard": "not submittable (cpu-basic Space, no peft)",
              "upload_code_commit": git_commit()}
    with open("results/submissions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(json.dumps(record, indent=2, ensure_ascii=False))
    if not ok:
        sys.exit(f"Hub files differ from local files: {sorted(set(local) ^ set(remote))}")


if __name__ == "__main__":
    main()
