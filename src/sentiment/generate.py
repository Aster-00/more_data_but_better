"""Generate a synthetic sentiment set (ArSarcasm-v2 track) from a config, resumably.

Pipeline stage 2 (open) for the sentiment track. The plan has one cell per (variety,
sentiment), with variety one of the ArSarcasm-v2 region labels (msa/egypt/gulf/levant;
magreb is left out, 37 train tweets) and `per_cell` requests in every cell. The plan is
fixed before anything is generated, so sets from different generators match cell for cell.
Requests are interleaved over cells, so a tiny run (--limit) or a partial run stays balanced.

Reuses the dialect track's generator loader (src/generation/llm.py) and output parser
(src/generation/prompts.py). One addition, sentiment track only: `strip_translation`
removes an English translation appended on the same line as the tweet (Fanar did this in
16/20 G01 outputs; the shared parser only drops translations on their own line), and
Markdown bold markers (**) are removed before parsing (the shared parser drops lines
starting with ** as preambles; Jais-2 bolds whole tweets). Then the same link/mention
cleaning as the real S1 data (URL, USER) is applied; the uncleaned text is kept as text_raw.

Few-shot (optional, SG02): with a `few_shot` block {k, source} in the config, every request
gets k real tweets of its own (variety, sentiment) cell from S1 train, drawn afresh per request
and reproducibly from (seed, request_id). Only S1 train is allowed as the source (never dev or
test); the example ids are stored in the record (few_shot_ids).

Output: one JSONL record per request, appended as batches finish; on restart, requests that
already have a record are skipped. Sidecar <output>.meta.json: config, template hash,
generator revision, git commit, timing.

Record schema: text_id, request_id, text, source="synthetic", origin, condition, generator,
  generator_revision, quantization, template_id, template_version, template_sha256,
  controls{variety, sentiment}, dialect, target_dialect (= variety, for the shared filter),
  sentiment, sarcasm (None: not controlled), few_shot_ids, sampling, seed, prompt, raw_output, parse_ok,
  translation_stripped, text_raw, cleaning, created, git_commit, config_file

Usage:
  python -m src.sentiment.generate --config configs/sentiment/generation/sg01_jais2.json --dry-run
  python -m src.sentiment.generate --config configs/sentiment/generation/sg01_jais2.json --limit 24
  python -m src.sentiment.generate --config configs/sentiment/generation/sg01_jais2.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

from src.data.build_dataset import CLEANING_STEPS, clean_text, git_commit
from src.generation.generate import existing_request_ids
from src.generation.prompts import ARABIC_LETTER_RE, Template, parse_output

# Same-line translation: a run of >= 3 Latin words (optionally in brackets or after a dash,
# "Translation:" etc.) at the end of a line that also contains Arabic.
TRANSLATION_TAIL_RE = re.compile(
    r"[\s\-–—|:]*[\(\[]?\s*(?:translation|english|meaning)?\s*[:：]?\s*"
    r"[A-Za-z][A-Za-z'’\-]*(?:[\s,.;:!?\"]+[A-Za-z'’\-]+){2,}[\s.!?\"]*[\)\]]?\s*$", re.I)


# Cleaning steps applied to every synthetic text (S1 used the same two).
CLEAN_STEPS = list(CLEANING_STEPS)


@dataclass
class Request:
    """One generation request: a (variety, sentiment) cell and its index within the cell."""
    request_id: str
    variety: str
    sentiment: str
    index: int
    few_shot_ids: list[str] = field(default_factory=list)
    few_shot_texts: list[str] = field(default_factory=list)


def build_plan(cfg: dict) -> list[Request]:
    """Every request of a run, interleaved over cells: index 0 of every cell, then index 1, ..."""
    cells = [(v, s) for v in cfg["varieties"] for s in cfg["sentiments"]]
    return [Request(f"{cfg['set_name']}:{v}:{s}:{j}", v, s, j)
            for j in range(cfg["per_cell"]) for v, s in cells]


def assign_few_shot(plan: list[Request], cfg: dict) -> None:
    """Give every request k real S1-train tweets of its own cell, reproducibly from (seed, request_id)."""
    fs = cfg.get("few_shot") or {}
    if not fs.get("k"):
        return
    # Per (variety, sentiment) cell, every S1 train tweet is a candidate.
    pool: dict[tuple[str, str], list[dict]] = {}
    with open(Path(fs["source"]), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("source") != "real" or r.get("split") != "train":
                raise ValueError("few-shot source must be real S1 train data")
            pool.setdefault((r["dialect"], r["sentiment"]), []).append(r)
    for req in plan:
        candidates = pool.get((req.variety, req.sentiment), [])
        if len(candidates) < fs["k"]:
            raise ValueError(f"only {len(candidates)} few-shot candidates for {req.variety}/{req.sentiment}")
        chosen = random.Random(f"{cfg['seed']}:{req.request_id}").sample(candidates, fs["k"])
        req.few_shot_ids = [c["text_id"] for c in chosen]
        req.few_shot_texts = [c["text"] for c in chosen]


def render_messages(template: Template, req: Request) -> list[dict]:
    """Fill the template with the request's variety, sentiment and examples; return chat messages."""
    var, sen = template.options["variety"][req.variety], template.options["sentiment"][req.sentiment]
    values = {"variety_name": var["name"], "variety_instruction": var["instruction"],
              "sentiment_name": sen["name"], "sentiment_definition": sen["definition"], "few_shot_block": ""}
    if req.few_shot_texts:
        items = "\n".join(template.few_shot_item.format(text=t) for t in req.few_shot_texts)
        values["few_shot_block"] = template.few_shot_header.format(**values) + "\n" + items + "\n\n"
    messages = [{"role": "system", "content": template.system.format(**values)}] if template.system else []
    return messages + [{"role": "user", "content": template.user.format(**values)}]


def strip_translation(text: str) -> tuple[str, bool]:
    """Remove a same-line English translation after the Arabic tweet; return (text, stripped?)."""
    m = TRANSLATION_TAIL_RE.search(text)
    # Only strip when Arabic remains before the Latin tail (an all-Latin text is left alone).
    if m and ARABIC_LETTER_RE.search(text[:m.start()]):
        return text[:m.start()].rstrip(" -–—|:([").strip(), True
    return text, False


def make_record(req: Request, text: str | None, text_raw: str | None, stripped: bool, out: dict, cfg: dict,
                template: Template, gen_revision: str | None, provenance: dict) -> dict:
    """Assemble the output record of one request (text None = nothing parseable)."""
    return {
        "text_id": "s" + hashlib.sha1(req.request_id.encode("utf-8")).hexdigest()[:16],
        "request_id": req.request_id,
        "text": text,
        "source": "synthetic",
        "origin": cfg["generator"],
        "condition": cfg["condition"],
        "generator": cfg["generator"],
        "generator_revision": gen_revision,
        "quantization": cfg["quantization"],
        "template_id": template.id,
        "template_version": template.version,
        "template_sha256": template.sha256,
        "controls": {"variety": req.variety, "sentiment": req.sentiment},
        "dialect": req.variety,
        "target_dialect": req.variety,
        "sentiment": req.sentiment,
        "sarcasm": None,
        "few_shot_ids": req.few_shot_ids,
        "sampling": cfg["sampling"],
        "seed": out.get("seed"),
        "prompt": out.get("prompt"),
        "raw_output": out.get("raw_output"),
        "parse_ok": text is not None,
        "translation_stripped": stripped,
        "text_raw": text_raw,
        "cleaning": CLEAN_STEPS,
        "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
        **provenance,
    }


def run(cfg: dict, config_file: str, limit: int | None, dry_run: bool) -> dict:
    """Build the plan, generate what is missing, append records; return a summary."""
    template = Template.load(Path(cfg["template"]))
    if template.condition != cfg["condition"]:
        raise ValueError(f"template {template.id} is for {template.condition}, config says {cfg['condition']}")
    plan = build_plan(cfg)
    assign_few_shot(plan, cfg)
    # Tiny mode: the first `limit` requests (interleaving keeps every cell represented).
    if limit is not None:
        plan = plan[:limit]

    # Dry run: show rendered prompts and plan size, load no model.
    if dry_run:
        for req in plan[:3]:
            print(f"--- {req.request_id}")
            for m in render_messages(template, req):
                print(f"[{m['role']}] {m['content']}")
        print(f"plan: {len(plan)} requests over {len(cfg['varieties']) * len(cfg['sentiments'])} cells")
        return {"dry_run": True, "requests": len(plan)}

    # Resume: skip requests that already have a record.
    out_path = Path(cfg["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = existing_request_ids(out_path)
    todo = [r for r in plan if r.request_id not in done]
    print(f"plan {len(plan)} requests, {len(done)} already done, {len(todo)} to generate", flush=True)
    if not todo:
        return {"requests": len(plan), "generated_now": 0}

    # Load the generator only now (slow, needs the GPU).
    from src.generation.llm import Generator, Sampling, vram_mib
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    sampling = Sampling(**cfg["sampling"])
    provenance = {"git_commit": git_commit(), "config_file": config_file}
    print(f"loaded {cfg['generator']} in {gen.load_seconds}s, VRAM {vram_mib()}", flush=True)

    # Generate batch by batch and append immediately, so a crash loses at most one batch.
    started, n_done, n_failed, n_stripped, n_tokens = time.time(), 0, 0, 0, 0
    bs = cfg["batch_size"]
    with open(out_path, "a", encoding="utf-8", newline="\n") as f:
        for b, start in enumerate(range(0, len(todo), bs), 1):
            batch = todo[start:start + bs]
            # Batch seed derived from the first request id, so a rerun gives the same text.
            seed = cfg["seed"] + int(hashlib.sha1(batch[0].request_id.encode()).hexdigest()[:6], 16)
            outs = gen.generate([render_messages(template, r) for r in batch], sampling, seed=seed)
            for req, out in zip(batch, outs):
                out["seed"] = seed
                parsed = parse_output(out["raw_output"].replace("**", ""), 1, "arabic")
                text_raw, stripped = strip_translation(parsed[0]) if parsed else (None, False)
                text_raw = text_raw or None
                # Same link/mention cleaning as the real S1 tweets.
                text = clean_text(text_raw, CLEAN_STEPS)[0] if text_raw else None
                f.write(json.dumps(make_record(req, text, text_raw, stripped, out, cfg, template, gen.revision, provenance),
                                   ensure_ascii=False) + "\n")
                n_done, n_failed, n_stripped = n_done + 1, n_failed + (text is None), n_stripped + stripped
                n_tokens += out["new_tokens"]
            f.flush()
            if b % 20 == 0 or start + bs >= len(todo):
                el = time.time() - started
                print(f"  batch {b}: {n_done}/{len(todo)} records, {n_failed} unparsed, {n_stripped} translations "
                      f"stripped, {n_done / el:.2f} texts/s, {n_tokens / el:.1f} tok/s, {el / 60:.1f} min", flush=True)

    el = time.time() - started
    return {"requests": len(plan), "generated_now": n_done, "unparsed_now": n_failed,
            "translations_stripped_now": n_stripped, "seconds": round(el),
            "texts_per_second": round(n_done / max(1e-9, el), 3),
            "tokens_per_second": round(n_tokens / max(1e-9, el), 2), "vram": vram_mib(),
            "generator_revision": gen.revision, "system_role_supported": gen.system_role_supported}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N requests, output gets _limitN")
    p.add_argument("--per-cell", type=int, default=None,
                   help="top-up: raise requests per cell (same set; existing records are kept)")
    p.add_argument("--dry-run", action="store_true", help="print rendered prompts and plan size; no model")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.per_cell is not None:
        cfg["per_cell"] = args.per_cell
    # Tiny runs write to their own file so they never mix with the real set.
    if args.limit is not None:
        cfg["set_name"] += f"_limit{args.limit}"
        cfg["output"] = str(Path(cfg["output"]).with_name(f"{cfg['set_name']}.jsonl"))

    summary = run(cfg, str(args.config), args.limit, args.dry_run)
    summary.update(config=cfg, template_sha256=Template.load(Path(cfg["template"])).sha256,
                   git_commit=git_commit(), python=platform.python_version(),
                   finished=time.strftime("%Y-%m-%d %H:%M"))
    if not args.dry_run:
        with open(Path(cfg["output"]).with_suffix(".meta.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
