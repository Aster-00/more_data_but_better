"""SR00: zero-shot sentiment classification with the roster LLMs, no training.

The trained runs (SR01 on) predict through a classification head on the last token; that head
is random until trained, so it cannot be used without training. Here the model's own language
head answers instead:
  1. The comment (cut to `max_length` tokens, as in the trained runs) goes into a chat prompt
     (template file in prompts/sentiment/) that asks for its sentiment.
  2. Each class has one answer word (e.g. negative / neutral / positive). Its score is the
     summed log-probability of the word's tokens right after the assistant turn starts.
  3. Prediction = the class with the highest score. Deterministic (no sampling), never unparsed.
The three scores are written as `logits`, so the per-text probabilities in the prediction files
are a softmax over the three answers. Metrics, prediction files and log keys are the same as
in the trained runs (src/sentiment/common.py).

Outputs in results/sentiment/runs/<run_name>/:
  train_log.json                 config, prompt, git commit, data hashes, dev/test scores (no training)
  {dev,test}_predictions.jsonl   per-text gold, prediction and class probabilities

Usage:
  python -m src.sentiment.zero_shot --config configs/sentiment/sr00_eesa_qwen3.json
  python -m src.sentiment.zero_shot --config ... --limit 30      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import gc
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import torch

from src.data.build_dataset import git_commit, sha256
from src.generation.llm import Generator, vram_mib
from src.sentiment.common import evaluate_splits, print_scores, run_classes

RUNS_DIR = Path("results/sentiment/runs")


class ZeroShotScorer:
    """Scores the class answer words after a chat prompt with a 4-bit LLM."""

    def __init__(self, cfg: dict, template: dict) -> None:
        """Load the model (shared 4-bit loader) and tokenise the answer words once."""
        self.cfg, self.template = cfg, template
        self.classes = run_classes(cfg)
        self.gen = Generator(cfg["model"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
        self.tok, self.model = self.gen.tokenizer, self.gen.model
        # Answer tokens per class, without special tokens (they follow the rendered prompt directly).
        self.answers = [self.tok(template["answers"][c], add_special_tokens=False)["input_ids"]
                        for c in self.classes]
        self.n_truncated = 0

    def cut(self, text: str) -> str:
        """The comment cut to `max_length` tokens, as the trained runs see it."""
        ids = self.tok(text, add_special_tokens=False)["input_ids"]
        if len(ids) <= self.cfg["max_length"]:
            return text
        self.n_truncated += 1
        return self.tok.decode(ids[:self.cfg["max_length"]], skip_special_tokens=True)

    def prompt_ids(self, text: str) -> list[int]:
        """Token ids of the rendered chat prompt, ending where the assistant's answer starts."""
        messages = [{"role": "user", "content": self.template["user"].format(text=self.cut(text))}]
        if self.template.get("system"):
            messages.insert(0, {"role": "system", "content": self.template["system"]})
        # The chat template already adds BOS, so the tokenizer must not add a second one.
        return self.tok(self.gen.render(messages), add_special_tokens=False)["input_ids"]

    @torch.no_grad()
    def score(self, text: str) -> np.ndarray:
        """Summed log-probability of each class's answer word (one row of `logits`)."""
        prompt = self.prompt_ids(text)
        # One batch = the same prompt + each answer, right-padded: padding comes after every
        # real token, so it changes nothing that the causal model computes for the real tokens.
        seqs = [prompt + a for a in self.answers]
        width = max(map(len, seqs))
        pad = self.tok.pad_token_id
        ids = torch.tensor([s + [pad] * (width - len(s)) for s in seqs], device=self.model.device)
        mask = torch.tensor([[1] * len(s) + [0] * (width - len(s)) for s in seqs], device=self.model.device)
        logits = self.model(input_ids=ids, attention_mask=mask).logits
        out = []
        for i, a in enumerate(self.answers):
            # Positions len(prompt)-1 ... predict the answer tokens.
            step = logits[i, len(prompt) - 1:len(prompt) - 1 + len(a)].float().log_softmax(-1)
            out.append(step[torch.arange(len(a)), torch.tensor(a, device=step.device)].sum().item())
        return np.asarray(out)

    def predict(self, texts: list[str]) -> np.ndarray:
        """Class scores for a list of texts, with a progress line every 200 texts."""
        rows, t0 = [], time.time()
        for i, text in enumerate(texts, 1):
            rows.append(self.score(text))
            if i % 200 == 0 or i == len(texts):
                print(f"  {i}/{len(texts)} texts, {i / (time.time() - t0):.1f} texts/s", flush=True)
        return np.stack(rows)


def main() -> None:
    """Score dev and test zero-shot from a config; write the log and prediction files."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts per split")
    args = p.parse_args()
    if not torch.cuda.is_available():
        sys.exit("Zero-shot scoring needs CUDA (4-bit bitsandbytes); refusing to fall back to CPU.")

    # Config and tiny-subset mode, as in the trainers.
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.limit is not None:
        cfg.update(limit=args.limit, run_name=cfg["run_name"] + f"_limit{args.limit}")
    run_dir = RUNS_DIR / cfg["run_name"]
    if (run_dir / "train_log.json").exists():
        sys.exit(f"{run_dir} already has a finished run; rerun under a new name.")
    run_dir.mkdir(parents=True, exist_ok=True)
    with open(cfg["template"], encoding="utf-8") as f:
        template = json.load(f)

    # Load once, score dev and test (no choice is made on either; nothing is tuned).
    started = time.time()
    torch.manual_seed(cfg["seed"])
    scorer = ZeroShotScorer(cfg, template)
    print(f"loaded {cfg['model']} in {scorer.gen.load_seconds} s; answer tokens "
          f"{dict(zip(scorer.classes, map(len, scorer.answers)))}", flush=True)
    log = {"config": cfg, "device": "cuda", "method": "zero-shot, answer-word log-probability (no training)",
           "template": template, "answer_token_ids": dict(zip(scorer.classes, scorer.answers)),
           "model_revision": scorer.gen.revision, "best_epoch": None}
    log.update(evaluate_splits(scorer.predict, cfg, run_dir))

    # Provenance alongside the results.
    log.update(n_truncated=scorer.n_truncated, peak_vram_mib=vram_mib().get("peak_reserved"),
               git_commit=git_commit(), python=platform.python_version(), torch=torch.__version__,
               data_sha256={s: sha256(Path(cfg[f"{s}_data"])) for s in ("dev", "test")},
               config_file=str(args.config), total_seconds=round(time.time() - started))
    with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print_scores(log)
    print(f"peak VRAM {log['peak_vram_mib']} MiB, {log['total_seconds']} s", flush=True)
    del scorer
    gc.collect()
    torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
