"""Generate a synthetic set (open or controlled condition) from a config, resumably.

Pipeline stages 2 and 3. The config names the generator, the prompt template, the dialects,
how many requests per dialect, the sampling settings and (controlled only) the control-factor
values. The plan of requests is fixed by the seed before anything is generated, so the open
and controlled sets have matched sizes and every output is traceable to its factors.

Output: one JSONL record per generated sentence, appended as batches finish. On restart,
requests whose records already exist are skipped. A sidecar <output>.meta.json records the
config, template hash, generator revision, git commit and timing.

Record schema (every field is always present):
  text_id, request_id, text, source="synthetic", condition, generator, generator_revision,
  quantization, template_id, template_version, template_sha256, controls{dialect,...},
  target_dialect, labels{18 x 0/1 or null}, label_mode, sampling{...}, seed, few_shot_ids,
  prompt (rendered), raw_output, parse_ok, created, git_commit, config_file

Usage:
  python -m src.generation.generate --config configs/generation/open_v1_fanar.json --dry-run
  python -m src.generation.generate --config configs/generation/open_v1_fanar.json --limit 10
  python -m src.generation.generate --config configs/generation/controlled_v1_fanar.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

from src.data.build_dataset import DIALECTS, git_commit
from src.generation.prompts import (Request, Template, assign_few_shot, build_plan,
                                    load_dialect_names, load_few_shot_pool, parse_output,
                                    render_messages)

LABEL_MODES = ("target_only", "target_unknown")


def make_labels(target: str, mode: str) -> dict[str, int | None]:
    """18-way label dict for a synthetic sentence generated for `target`.

    target_only:    target = 1, the other 17 = 0 (the usual single-label assumption).
    target_unknown: target = 1, the other 17 = None (unknown; a loss mask must handle them).
    Labels from a scorer are added later by the filtering stage, not here.
    """
    if mode not in LABEL_MODES:
        raise ValueError(f"label_mode must be one of {LABEL_MODES}")
    other = 0 if mode == "target_only" else None
    return {d: (1 if d == target else other) for d in DIALECTS}


def existing_request_ids(path: Path) -> set[str]:
    """Request IDs already in the output file (for resuming)."""
    done = set()
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    done.add(json.loads(line)["request_id"])
    return done


def make_record(req: Request, text: str | None, sub: int, out: dict, cfg: dict, template: Template,
                gen_revision: str | None, provenance: dict) -> dict:
    """Assemble one output record for sentence `sub` of a request (text None = parse failed)."""
    rid = f"{req.request_id}#{sub}"
    return {
        "text_id": "s" + hashlib.sha1(rid.encode("utf-8")).hexdigest()[:16],
        "request_id": req.request_id,
        "text": text,
        "source": "synthetic",
        "condition": cfg["condition"],
        "generator": cfg["generator"],
        "generator_revision": gen_revision,
        "quantization": cfg["quantization"],
        "template_id": template.id,
        "template_version": template.version,
        "template_sha256": template.sha256,
        "controls": req.controls,
        "target_dialect": req.dialect,
        "labels": make_labels(req.dialect, cfg["label_mode"]),
        "label_mode": cfg["label_mode"],
        "sampling": cfg["sampling"],
        "seed": out.get("seed"),
        "few_shot_ids": req.few_shot_ids,
        "prompt": out.get("prompt"),
        "raw_output": out.get("raw_output"),
        "parse_ok": text is not None,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        **provenance,
    }


def run(cfg: dict, config_file: str, limit: int | None, dry_run: bool) -> dict:
    """Build the plan, generate what is missing, append records; return a summary."""
    template = Template.load(Path(cfg["template"]))
    if template.condition != cfg["condition"]:
        raise ValueError(f"template {template.id} is for condition {template.condition}, config says {cfg['condition']}")
    names = load_dialect_names()
    plan = build_plan(cfg)
    assign_few_shot(plan, load_few_shot_pool(cfg), cfg)
    # Tiny mode: the first `limit` requests only (spread over dialects by interleaving).
    if limit is not None:
        per = max(1, limit // max(1, len({r.dialect for r in plan})))
        plan = [r for r in plan if r.index < per][:limit]
    n_sent = cfg.get("sentences_per_request", 1)

    # Dry run: show the rendered prompts and plan statistics, load no model.
    if dry_run:
        for req in plan[:3]:
            print(f"--- {req.request_id} controls={req.controls} few_shot={req.few_shot_ids}")
            for m in render_messages(template, req, cfg, names):
                print(f"[{m['role']}] {m['content']}")
        print(f"plan: {len(plan)} requests, {len(plan) * n_sent} sentences, "
              f"{len({r.dialect for r in plan})} dialects")
        return {"dry_run": True, "requests": len(plan)}

    # Resume: skip requests that already have records.
    out_path = Path(cfg["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = existing_request_ids(out_path)
    todo = [r for r in plan if r.request_id not in done]
    print(f"plan {len(plan)} requests, {len(done)} already done, {len(todo)} to generate")
    if not todo:
        return {"requests": len(plan), "generated_now": 0}

    # Load the generator only now (slow, needs the GPU).
    from src.generation.llm import Generator, Sampling, vram_mib
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    sampling = Sampling(**cfg["sampling"])
    provenance = {"git_commit": git_commit(), "config_file": config_file}
    print(f"loaded {cfg['generator']} in {gen.load_seconds}s, VRAM {vram_mib()}")

    # Generate batch by batch and append immediately, so a crash loses at most one batch.
    started, n_records, n_failed, n_tokens = time.time(), 0, 0, 0
    bs = cfg["batch_size"]
    with open(out_path, "a", encoding="utf-8", newline="\n") as f:
        for b, start in enumerate(range(0, len(todo), bs), 1):
            batch = todo[start:start + bs]
            # Batch seed derived from the first request id, so re-running gives the same text.
            seed = cfg["seed"] + int(hashlib.sha1(batch[0].request_id.encode()).hexdigest()[:6], 16)
            outs = gen.generate([render_messages(template, r, cfg, names) for r in batch], sampling, seed=seed)
            for req, out in zip(batch, outs):
                out["seed"] = seed
                sentences = parse_output(out["raw_output"], n_sent, req.controls.get("script", "arabic"))
                # Pad with None so every request always yields exactly n_sent records.
                sentences += [None] * (n_sent - len(sentences))
                for sub, text in enumerate(sentences):
                    f.write(json.dumps(make_record(req, text, sub, out, cfg, template, gen.revision, provenance),
                                       ensure_ascii=False) + "\n")
                    n_records += 1
                    n_failed += text is None
                n_tokens += out["new_tokens"]
            f.flush()
            if b % 10 == 0 or start + bs >= len(todo):
                el = time.time() - started
                print(f"  batch {b}: {n_records} records, {n_failed} unparsed, "
                      f"{n_tokens / el:.1f} tok/s, {el / 60:.1f} min")

    summary = {"requests": len(plan), "generated_now": n_records, "unparsed_now": n_failed,
               "seconds": round(time.time() - started), "tokens_per_second": round(n_tokens / max(1e-9, time.time() - started), 2),
               "vram": vram_mib(), "generator_revision": gen.revision,
               "system_role_supported": gen.system_role_supported}
    return summary


def main() -> None:
    """CLI entry point."""
    # Windows consoles default to cp1252, which cannot print Arabic; force UTF-8 output.
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: only the first N requests, output gets _limitN")
    p.add_argument("--dry-run", action="store_true", help="print rendered prompts and plan size; no model")
    p.add_argument("--generator", default=None, help="override the generator Hub ID (set name gets a suffix)")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    # Overrides keep real outputs separate from tiny/alternative runs.
    if args.generator:
        cfg["generator"] = args.generator
        tag = args.generator.split("/")[-1].lower().replace("-", "_")
        cfg["set_name"] += f"_{tag}"
        cfg["output"] = str(Path(cfg["output"]).with_name(f"{cfg['set_name']}.jsonl"))
    if args.limit is not None:
        cfg["set_name"] += f"_limit{args.limit}"
        cfg["output"] = str(Path(cfg["output"]).with_name(f"{cfg['set_name']}.jsonl"))

    summary = run(cfg, str(args.config), args.limit, args.dry_run)
    summary.update(config=cfg, template_sha256=Template.load(Path(cfg["template"])).sha256,
                   git_commit=git_commit(), python=platform.python_version(),
                   finished=time.strftime("%Y-%m-%d %H:%M"))
    # Sidecar metadata next to the data file (one per set; overwritten on each resume).
    if not args.dry_run:
        meta_path = Path(cfg["output"]).with_suffix(".meta.json")
        with open(meta_path, "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
