"""Generator feasibility check: does each LLM fit the 8 GB card in 4-bit, and is its output dialectal?

For one generator: load in NF4, generate `--n` short sentences spread over a few dialects
with a minimal prompt, and record VRAM peak, load time, tokens/second and the outputs.
Each model runs in its own process (one call per model) so VRAM is released cleanly.
If loading or generation fails (e.g. out of memory), the error is recorded as the result;
there is no CPU fallback.

Outputs in results/runs/<run_id>_<model>/:
  feasibility.json   settings, VRAM, speed, errors, provenance
  samples.jsonl      one record per generated sentence (dialect, prompt, raw output)

Usage:
  python scripts/check_generators.py --run-id G01 --model QCRI/Fanar-1-9B-Instruct
  python scripts/check_generators.py --run-id G01 --model google/gemma-2-9b-it --n 20
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
import time
import traceback
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.build_dataset import git_commit  # noqa: E402
from src.generation.llm import Generator, Sampling, vram_mib  # noqa: E402

# Dialects used for the check: a Maghrebi, an Egyptian, a Levantine, a Gulf and a Mesopotamian one.
CHECK_DIALECTS = ["Egypt", "Morocco", "Syria", "Saudi_Arabia", "Iraq"]
# Minimal instruction, English with the dialect name, like the open condition will use.
PROMPT = ("Write one short, natural tweet-like sentence in {dialect_name}, as a native "
          "speaker would write it on social media. Output only the sentence, nothing else.")


def dialect_names() -> dict[str, str]:
    """Country label -> dialect name used in prompts (from prompts/dialects.json)."""
    with open(Path("prompts/dialects.json"), encoding="utf-8") as f:
        return {k: v["en"] for k, v in json.load(f)["dialects"].items()}


def write(run_dir: Path, result: dict, samples: list[dict]) -> None:
    """Write feasibility.json and samples.jsonl (UTF-8, Arabic kept readable)."""
    result["finished"] = time.strftime("%Y-%m-%d %H:%M")
    with open(run_dir / "feasibility.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    with open(run_dir / "samples.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for s in samples:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")


def main() -> None:
    """Run the check for one model and write the results."""
    # Windows consoles default to cp1252, which cannot print Arabic; force UTF-8 output.
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-id", required=True, help="e.g. G01; results go to results/runs/<run-id>_<model>")
    p.add_argument("--model", required=True, help="Hub ID")
    p.add_argument("--n", type=int, default=20, help="sentences to generate")
    p.add_argument("--batch-size", type=int, default=5)
    p.add_argument("--max-new-tokens", type=int, default=48)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--min-free-mib", type=int, default=6000, help="refuse to start below this much free VRAM")
    p.add_argument("--cache-dir", type=Path, default=Path("F:/Thesis/models"))
    args = p.parse_args()

    run_dir = Path("results/runs") / f"{args.run_id}_{args.model.replace('/', '__')}"
    run_dir.mkdir(parents=True, exist_ok=True)
    result = {"run_id": args.run_id, "model": args.model, "n_requested": args.n,
              "batch_size": args.batch_size, "max_new_tokens": args.max_new_tokens,
              "seed": args.seed, "quantization": "nf4", "git_commit": git_commit(),
              "python": platform.python_version(), "torch": torch.__version__,
              "gpu": torch.cuda.get_device_name(0), "vram_before_load": vram_mib(), "status": "ok"}

    # Refuse to start if another process already holds most of the card.
    if result["vram_before_load"].get("card_free", 0) < args.min_free_mib:
        result.update(status="skipped", error=f"less than {args.min_free_mib} MiB free on the GPU; "
                                              "another job is probably running")
        write(run_dir, result, [])
        print(result["error"])
        return

    # Load; an out-of-memory error here means "does not fit" and is the finding.
    try:
        gen = Generator(args.model, cache_dir=args.cache_dir)
    except Exception as e:  # noqa: BLE001 - any failure is the finding
        result.update(status="load_failed", error=f"{type(e).__name__}: {e}",
                      traceback=traceback.format_exc(), vram_after_fail=vram_mib())
        write(run_dir, result, [])
        print("LOAD FAILED:", result["error"])
        return
    result.update(load_seconds=gen.load_seconds, model_revision=gen.revision,
                  system_role_supported=gen.system_role_supported, vram_after_load=vram_mib())
    print(f"loaded in {gen.load_seconds}s, VRAM after load: {result['vram_after_load']}")

    # Build n requests cycling through the check dialects.
    names = dialect_names()
    requests = [(CHECK_DIALECTS[i % len(CHECK_DIALECTS)], i) for i in range(args.n)]
    sampling = Sampling(temperature=0.9, top_p=0.95, top_k=50, max_new_tokens=args.max_new_tokens)
    result["sampling"] = sampling.as_dict()

    # Generate in batches, measuring tokens per second over all batches.
    samples, total_tokens, total_seconds = [], 0, 0.0
    try:
        for start in range(0, len(requests), args.batch_size):
            batch = requests[start:start + args.batch_size]
            messages = [[{"role": "user", "content": PROMPT.format(dialect_name=names[d])}] for d, _ in batch]
            outs = gen.generate(messages, sampling, seed=args.seed + start)
            for (d, i), o in zip(batch, outs):
                samples.append({"index": i, "dialect": d, **o})
                total_tokens += o["new_tokens"]
            total_seconds += outs[0]["batch_seconds"]
            print(f"  batch {start // args.batch_size + 1}: {outs[0]['batch_seconds']:.1f}s")
    except Exception as e:  # noqa: BLE001
        result.update(status="generation_failed", error=f"{type(e).__name__}: {e}",
                      traceback=traceback.format_exc())
    result.update(n_generated=len(samples), generated_tokens=total_tokens,
                  generation_seconds=round(total_seconds, 1),
                  tokens_per_second=round(total_tokens / total_seconds, 2) if total_seconds else None,
                  vram_peak=vram_mib())
    write(run_dir, result, samples)
    print(json.dumps({k: result.get(k) for k in ("status", "load_seconds", "tokens_per_second", "vram_peak")},
                     indent=2))
    for s in samples:
        print(f"[{s['dialect']}] {s['raw_output']!r}")


if __name__ == "__main__":
    main()
