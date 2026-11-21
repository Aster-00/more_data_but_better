"""SR14: retrieval-augmented (RAG) few-shot sentiment classification with the roster LLMs, no training.

Same scoring as SR00 (src/sentiment/zero_shot.py): prediction = the answer word with the highest
summed log-probability right after the assistant turn starts. The only change is the prompt: the
k EESA train comments nearest to the comment (from src/sentiment/retrieval.py) are shown first,
each with its gold label, most similar last (next to the comment).
  - Pool = train only; the comment itself is never an example (dev and test are not in the pool).
  - Examples are cut to `max_length` tokens, like the comment.
  - k = 0 renders exactly the SR00-En prompt (sanity check against SR00).

k is chosen on dev only: `--split dev` runs every k in the config's `ks` with one model load;
`--split test --ks K` then runs test once with the chosen K. Each (k, split) gets its own folder
in results/sentiment/runs/<run_prefix>_k<K>_<split>/ with the usual files:
  train_log.json                 config, prompt template, first rendered prompt, git commit, data hashes, scores
  <split>_predictions.jsonl      per-text gold, prediction and class probabilities
  <split>_examples.jsonl         per-text train ids shown as examples (traceability)

Usage:
  python -m src.sentiment.rag_few_shot --config configs/sentiment/sr14_eesa_e5_qwen3.json --split dev
  python -m src.sentiment.rag_few_shot --config ... --split test --ks 8
  python -m src.sentiment.rag_few_shot --config ... --split dev --limit 30     # tiny-subset smoke test
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
from src.generation.llm import vram_mib
from src.sentiment.common import load_split, sentiment_scores, write_predictions
from src.sentiment.zero_shot import ZeroShotScorer

RUNS_DIR = Path("results/sentiment/runs")


class RagScorer(ZeroShotScorer):
    """ZeroShotScorer whose prompt carries the k retrieved train comments with their labels."""

    def __init__(self, cfg: dict, template: dict) -> None:
        """Load the LLM (parent), the train pool (id -> text, label) and the neighbour lists."""
        super().__init__(cfg, template)
        self.train = {}
        with open(cfg["train_data"], encoding="utf-8") as f:
            for line in f:
                r = json.loads(line)
                self.train[r["text_id"]] = (r[cfg["text_field"]], r["sentiment"])
        with open(cfg["neighbours"], encoding="utf-8") as f:
            self.neighbours = json.load(f)
        self.k, self.split, self.query_id = 0, "dev", None

    def cut_example(self, text: str) -> str:
        """An example cut to `max_length` tokens (not counted in `n_truncated`, which is for comments)."""
        ids = self.tok(text, add_special_tokens=False)["input_ids"]
        return text if len(ids) <= self.cfg["max_length"] else \
            self.tok.decode(ids[:self.cfg["max_length"]], skip_special_tokens=True)

    def example_ids(self, query_id: str) -> list[str]:
        """The k nearest train ids for a query, ordered least to most similar (most similar last)."""
        return [tid for tid, _ in self.neighbours[self.split][query_id][:self.k]][::-1]

    def examples_block(self, query_id: str) -> str:
        """Header + formatted examples + footer; empty string when k = 0."""
        if self.k == 0:
            return ""
        t = self.template
        rows = [t["example_format"].format(example=self.cut_example(self.train[tid][0]),
                                           label=t["answers"][self.train[tid][1]])
                for tid in self.example_ids(query_id)]
        return t["examples_header"] + t["example_separator"].join(rows) + t["examples_footer"]

    def prompt_messages(self, text: str, query_id: str) -> list[dict]:
        """Chat messages for one comment."""
        user = self.template["user"].format(examples=self.examples_block(query_id), text=self.cut(text))
        messages = [{"role": "user", "content": user}]
        if self.template.get("system"):
            messages.insert(0, {"role": "system", "content": self.template["system"]})
        return messages

    def prompt_ids(self, text: str) -> list[int]:
        """Token ids of the rendered prompt for the current query (set in `predict`)."""
        return self.tok(self.gen.render(self.prompt_messages(text, self.query_id)),
                        add_special_tokens=False)["input_ids"]

    @torch.no_grad()
    def score(self, text: str) -> np.ndarray:
        """As ZeroShotScorer.score, but the LM head runs only on the answer positions.

        Few-shot prompts reach 1,000+ tokens; full-vocabulary logits for every position took
        about 2 GB and pushed peak VRAM past the 8 GB card (smoke test, k = 16). `logits_to_keep`
        keeps only the last positions, which hold every answer step; the hidden states are the
        same, so the scores are unchanged (checked: k = 0 equals SR00-En).
        """
        prompt = self.prompt_ids(text)
        seqs = [prompt + a for a in self.answers]
        width = max(map(len, seqs))
        pad = self.tok.pad_token_id
        ids = torch.tensor([s + [pad] * (width - len(s)) for s in seqs], device=self.model.device)
        mask = torch.tensor([[1] * len(s) + [0] * (width - len(s)) for s in seqs], device=self.model.device)
        keep = width - len(prompt) + 1  # positions len(prompt)-1 .. width-1
        logits = self.model(input_ids=ids, attention_mask=mask, logits_to_keep=keep).logits
        out = []
        for i, a in enumerate(self.answers):
            # Kept position 0 = prompt position len(prompt)-1, which predicts the first answer token.
            step = logits[i, :len(a)].float().log_softmax(-1)
            out.append(step[torch.arange(len(a)), torch.tensor(a, device=step.device)].sum().item())
        return np.asarray(out)

    def predict_ids(self, texts: list[str], ids: list[str]) -> tuple[np.ndarray, int]:
        """Class scores per text and the longest prompt (tokens), with a progress line every 200 texts."""
        rows, longest, t0 = [], 0, time.time()
        for i, (text, qid) in enumerate(zip(texts, ids), 1):
            self.query_id = qid
            longest = max(longest, len(self.prompt_ids(text)))
            rows.append(self.score(text))
            if i % 200 == 0 or i == len(texts):
                print(f"  k={self.k} {i}/{len(texts)} texts, {i / (time.time() - t0):.1f} texts/s", flush=True)
        return np.stack(rows), longest


def main() -> None:
    """Score one split for every requested k with one model load."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--split", choices=("dev", "test"), required=True)
    p.add_argument("--ks", type=int, nargs="+", default=None, help="k values (default: config `ks`; test needs one)")
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N texts")
    args = p.parse_args()
    if not torch.cuda.is_available():
        sys.exit("RAG scoring needs CUDA (4-bit bitsandbytes); refusing to fall back to CPU.")

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    ks = args.ks or cfg["ks"]
    # Test is run once, with the k chosen on dev: refuse a test sweep.
    if args.split == "test" and len(ks) != 1:
        sys.exit("Test takes exactly one k (chosen on dev): pass --ks K.")
    suffix = f"_limit{args.limit}" if args.limit is not None else ""
    run_dirs = {k: RUNS_DIR / f"{cfg['run_prefix']}_k{k}_{args.split}{suffix}" for k in ks}
    for k, d in run_dirs.items():
        if (d / "train_log.json").exists():
            sys.exit(f"{d} already has a finished run; rerun under a new name.")
    with open(cfg["template"], encoding="utf-8") as f:
        template = json.load(f)

    started = time.time()
    torch.manual_seed(cfg["seed"])
    scorer = RagScorer(cfg, template)
    scorer.split = args.split
    print(f"loaded {cfg['model']} in {scorer.gen.load_seconds} s", flush=True)
    texts, gold, ids = load_split(Path(cfg[f"{args.split}_data"]), cfg["text_field"], args.limit, scorer.classes)

    for k in ks:
        t0, run_dir = time.time(), run_dirs[k]
        run_dir.mkdir(parents=True, exist_ok=True)
        scorer.k, scorer.n_truncated = k, 0
        torch.cuda.reset_peak_memory_stats()
        logits, longest = scorer.predict_ids(texts, ids)
        write_predictions(run_dir / f"{args.split}_predictions.jsonl", ids, gold, logits, scorer.classes)
        with open(run_dir / f"{args.split}_examples.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for qid in ids:
                f.write(json.dumps({"text_id": qid, "examples_least_to_most_similar": scorer.example_ids(qid)}) + "\n")
        scores = sentiment_scores(gold, logits.argmax(-1), scorer.classes)

        # Log: config with this k, template, the first rendered prompt, provenance.
        scorer.query_id = ids[0]
        log = {"config": {**cfg, "k": k, "split": args.split, "limit": args.limit}, "device": "cuda",
               "method": "RAG few-shot, answer-word log-probability (no training)",
               "template": template, "first_prompt": scorer.gen.render(scorer.prompt_messages(texts[0], ids[0])),
               "answer_token_ids": dict(zip(scorer.classes, scorer.answers)),
               "model_revision": scorer.gen.revision, "best_epoch": None, args.split: scores,
               "n_truncated": scorer.n_truncated, "longest_prompt_tokens": longest,
               "peak_vram_mib": vram_mib().get("peak_reserved"), "git_commit": git_commit(),
               "python": platform.python_version(), "torch": torch.__version__,
               "data_sha256": {s: sha256(Path(cfg[f"{s}_data"])) for s in ("train", args.split)},
               "neighbours_sha256": sha256(Path(cfg["neighbours"])),
               "config_file": str(args.config), "seconds": round(time.time() - t0),
               "total_seconds_since_load_start": round(time.time() - started)}
        with open(run_dir / "train_log.json", "w", encoding="utf-8", newline="\n") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        print(f"{args.split.upper()} k={k}: micro F1 (acc) {scores['accuracy']:.2f}  macro F1 {scores['macro']['f1']:.2f}  "
              f"longest prompt {longest} tok, peak VRAM {log['peak_vram_mib']} MiB, {log['seconds']} s", flush=True)

    del scorer
    gc.collect()
    torch.cuda.empty_cache()


if __name__ == "__main__":
    main()
