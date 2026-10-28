"""Download every model listed in configs/models.json into the model cache (F:/Thesis/models).

Only the files needed to load each model with PyTorch are downloaded: weights in
safetensors format when the repo has them (else .bin), configs and tokenizer files.
TensorFlow, Flax, ONNX and GGUF copies are skipped. Downloads resume if interrupted,
and models already in the cache are not downloaded again.

Gated models (Gemma) use the Hugging Face login saved on this machine (`hf auth login`).

Usage:
  python scripts/download_models.py                 # all models
  python scripts/download_models.py --only scorers  # one group
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from huggingface_hub import list_repo_files, snapshot_download

# Files never needed for PyTorch loading.
SKIP_PATTERNS = ["*.h5", "*.msgpack", "*.onnx", "*.onnx_data", "*.ot", "*.gguf", "*.tflite",
                 "flax_model*", "tf_model*", "onnx/*", "openvino/*", "original/*", "*.pth",
                 "optimizer.pt", "scheduler.pt", "rng_state.pth", "training_args.bin", "trainer_state.json"]


def skip_patterns_for(repo_id: str) -> list[str]:
    """Patterns to skip for one repo: the standard list, plus .bin weights if safetensors exist."""
    files = list_repo_files(repo_id)
    # Many repos ship the same weights twice (.bin and .safetensors); keep only safetensors.
    if any(f.endswith(".safetensors") for f in files):
        return SKIP_PATTERNS + ["*.bin"]
    return SKIP_PATTERNS


def main() -> None:
    """Download the selected model groups and print where each one is stored."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, default=Path("configs/models.json"))
    p.add_argument("--only", choices=["generators", "scorers", "classifiers"], default=None)
    args = p.parse_args()

    # Read the model list; the cache folder comes from the config so it is on record.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    groups = [args.only] if args.only else ["classifiers", "scorers", "generators"]

    # Download group by group (small models first), continuing past failures.
    failed = []
    for group in groups:
        for repo_id in cfg[group]:
            print(f"[{group}] {repo_id} ...", flush=True)
            try:
                path = snapshot_download(repo_id, cache_dir=cfg["cache_dir"],
                                         ignore_patterns=skip_patterns_for(repo_id))
                print(f"  ok -> {path}", flush=True)
            except Exception as e:  # report and move on, so one failure does not stop the rest
                print(f"  FAILED: {type(e).__name__}: {e}", flush=True)
                failed.append(repo_id)

    print("done" if not failed else f"done, {len(failed)} failed: {failed}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
