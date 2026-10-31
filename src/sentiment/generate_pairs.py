"""Generate a minimal-pair synthetic sentiment set (SG03 and its control SG03-random), resumably.

One request asks the generator for two tweets on the same subject that differ only in what
decides the sentiment: tweet A with label `a`, tweet B with label `b`. The plan comes from the
`types` block of the targeted template (prompts/sentiment/pairs_targeted_v1.json): per type the
labels (a, b), the varieties and `target_pairs`; `ceil(target_pairs * scale)` requests are made
per type (default scale 1.1, raised for a top-up), spread evenly over the type's varieties and
interleaved over types, so a tiny or partial run stays balanced. Both sets use the same plan, so
SG03 and SG03-random match request for request.

  mode "targeted" (SG03): the type's task text, its fixed example pairs and a subject hint drawn
                          per request from the type's hint list.
  mode "random" (SG03-random, the control): generic example pairs and one real S1-train tweet of
                          the same variety and sentiment `a` as inspiration (drawn per request).
Hints and seed tweets are drawn reproducibly from (seed, request_id). Only S1 train is a source.

Output: two JSONL records per request (pair_role "A" and "B", same pair_id), appended as batches
finish; on restart, requests that already have both records are skipped. Parsing, translation
stripping and link/mention cleaning are those of src/sentiment/generate.py. Sidecar
<output>.meta.json: config, template hashes, generator revision, git commit, timing.

Record schema: as src/sentiment/generate.py, plus pair_id, pair_role, pair_type, pair_labels,
  hint, seed_tweet_id; controls{variety, sentiment, type}.

Usage:
  python -m src.sentiment.generate_pairs --config configs/sentiment/generation/sg03_qwen3.json --dry-run
  python -m src.sentiment.generate_pairs --config configs/sentiment/generation/sg03_qwen3.json --limit 24
  python -m src.sentiment.generate_pairs --config configs/sentiment/generation/sg03_qwen3.json --scale 1.4
  python -m src.sentiment.generate_pairs --config configs/sentiment/generation/sg03_fanar.json --reparse
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from src.data.build_dataset import clean_text, git_commit
from src.generation.prompts import ARABIC_LETTER_RE, clean_line
from src.sentiment.generate import CLEAN_STEPS, strip_translation

# "A: ..." / "B: ..." lines; also "A)", "A -", "**A:**", "Tweet A:", "A (neutral):", and the Arabic
# letters "أ:" / "ب:" (Fanar labelled the tweets so in 322 of 4,672 SG03 sides, 2026-10-30).
PAIR_LINE_RE = re.compile(r"^\W*(?:tweet\s*)?([ABأب])\s*(?:\([^)]*\))?\s*\**\s*[:：\-–)]\s*\**\s*(.+)$", re.I)
ROLE = {"A": "A", "B": "B", "أ": "A", "ب": "B"}


@dataclass
class Request:
    """One pair request: type, variety, index within the type and the drawn hint or seed tweet."""
    request_id: str
    type: str
    variety: str
    a: str
    b: str
    index: int
    hint: str | None = None
    seed_tweet_id: str | None = None
    seed_tweet: str | None = None


def load_json(path: Path) -> tuple[dict, str]:
    """A template file and the SHA-256 of its bytes."""
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), hashlib.sha256(raw).hexdigest()


def build_plan(cfg: dict, types: dict, scale: float) -> list[Request]:
    """Every request of a run: per type ceil(target * scale), varieties in turn, interleaved over types."""
    per_type = {}
    for name, t in types.items():
        n = math.ceil(t["target_pairs"] * scale)
        per_type[name] = [Request(f"{cfg['set_name']}:{name}:{t['varieties'][j % len(t['varieties'])]}:{j}",
                                  name, t["varieties"][j % len(t["varieties"])], t["a"], t["b"], j) for j in range(n)]
    # Round robin over types, weighted by size: type with the lowest done share goes next.
    plan, pos = [], {k: 0 for k in per_type}
    total = sum(len(v) for v in per_type.values())
    while len(plan) < total:
        k = min((k for k in per_type if pos[k] < len(per_type[k])), key=lambda k: (pos[k] / len(per_type[k]), k))
        plan.append(per_type[k][pos[k]])
        pos[k] += 1
    return plan


def assign_inputs(plan: list[Request], cfg: dict, types: dict) -> None:
    """Draw the subject hint (targeted) or the real seed tweet (random) of every request."""
    if cfg["mode"] == "targeted":
        for req in plan:
            req.hint = random.Random(f"{cfg['seed']}:{req.request_id}").choice(types[req.type]["hints"])
        return
    pool: dict[tuple[str, str], list[dict]] = {}
    with open(Path(cfg["seed_source"]), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("source") != "real" or r.get("split") != "train":
                raise ValueError("seed tweets must be real S1 train data")
            pool.setdefault((r["dialect"], r["sentiment"]), []).append(r)
    for req in plan:
        c = random.Random(f"{cfg['seed']}:{req.request_id}").choice(pool[(req.variety, req.a)])
        req.seed_tweet_id, req.seed_tweet = c["text_id"], c["text"]


def render_messages(template: dict, types: dict, req: Request, mode: str) -> list[dict]:
    """Fill the template for one request; return chat messages."""
    var = template["variety"][req.variety]
    values = {"variety_name": var["name"], "variety_instruction": var["instruction"]}
    if mode == "targeted":
        t = types[req.type]
        values.update(task=t["task"], hint=req.hint,
                      examples="\n\n".join(template["example_item"].format(a=a, b=b) for a, b in t["pairs"]))
    else:
        sen = template["sentiment"]
        values.update(a_name=sen[req.a]["name"], a_definition=sen[req.a]["definition"],
                      b_name=sen[req.b]["name"], b_definition=sen[req.b]["definition"], seed_tweet=req.seed_tweet,
                      examples="\n\n".join(template["example_item"].format(a=a, text_a=ta, b=b, text_b=tb)
                                           for a, ta, b, tb in template["examples"]))
    messages = [{"role": "system", "content": template["system"]}] if template.get("system") else []
    return messages + [{"role": "user", "content": template["user"].format(**values)}]


def parse_pair(raw: str) -> dict[str, str]:
    """The tweet after "A:" and after "B:" (first of each, Arabic lines only); missing sides are absent."""
    out: dict[str, str] = {}
    for line in raw.replace("\r", "").replace("**", "").split("\n"):
        m = PAIR_LINE_RE.match(line.strip())
        if not m or ROLE[m.group(1).upper()] in out:
            continue
        s = clean_line(m.group(2))
        if s and ARABIC_LETTER_RE.search(s):
            out[ROLE[m.group(1).upper()]] = s
    return out


def make_records(req: Request, parsed: dict[str, str], out: dict, cfg: dict, tmpl_meta: dict,
                 gen_revision: str | None, provenance: dict) -> list[dict]:
    """The A and B records of one request (text None = side not parseable)."""
    recs = []
    for role, label in (("A", req.a), ("B", req.b)):
        text_raw, stripped = strip_translation(parsed[role]) if role in parsed else (None, False)
        text_raw = text_raw or None
        # Same link/mention cleaning as the real S1 tweets.
        text = clean_text(text_raw, CLEAN_STEPS)[0] if text_raw else None
        rid = f"{req.request_id}:{role}"
        recs.append({
            "text_id": "s" + hashlib.sha1(rid.encode("utf-8")).hexdigest()[:16],
            "request_id": rid,
            "pair_id": req.request_id,
            "pair_role": role,
            "pair_type": req.type,
            "pair_labels": [req.a, req.b],
            "text": text,
            "source": "synthetic",
            "origin": cfg["generator"],
            "condition": cfg["condition"],
            "generator": cfg["generator"],
            "generator_revision": gen_revision,
            "quantization": cfg["quantization"],
            **tmpl_meta,
            "controls": {"variety": req.variety, "sentiment": label, "type": req.type},
            "dialect": req.variety,
            "target_dialect": req.variety,
            "sentiment": label,
            "sarcasm": None,
            "hint": req.hint,
            "seed_tweet_id": req.seed_tweet_id,
            "few_shot_ids": [],
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
        })
    return recs


def done_pairs(path: Path) -> set[str]:
    """Pair ids that already have both records (for resuming)."""
    roles: dict[str, set[str]] = {}
    if path.exists():
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    roles.setdefault(r["pair_id"], set()).add(r["pair_role"])
    return {p for p, r in roles.items() if r == {"A", "B"}}


def reparse(path: Path) -> dict:
    """Parse every record's stored raw output again (after a parser fix); the old file is kept as a backup.

    Only text, text_raw, translation_stripped and parse_ok change; every record gets `reparsed`.
    """
    backup = path.with_name(path.stem + ".before_reparse.jsonl")
    if backup.exists():
        raise FileExistsError(f"{backup} exists; a set is reparsed once")
    recs = [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    path.rename(backup)
    changed = 0
    for r in recs:
        parsed = parse_pair(r["raw_output"])
        text_raw, stripped = strip_translation(parsed[r["pair_role"]]) if r["pair_role"] in parsed else (None, False)
        text_raw = text_raw or None
        text = clean_text(text_raw, CLEAN_STEPS)[0] if text_raw else None
        changed += text != r["text"]
        r.update(text=text, text_raw=text_raw, translation_stripped=stripped, parse_ok=text is not None,
                 reparsed=time.strftime("%Y-%m-%d %H:%M"))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in recs:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return {"records": len(recs), "text_changed": changed, "unparsed_after": sum(r["text"] is None for r in recs),
            "backup": str(backup)}


def run(cfg: dict, config_file: str, limit: int | None, dry_run: bool, scale: float) -> dict:
    """Build the plan, generate what is missing, append records; return a summary."""
    template, t_sha = load_json(Path(cfg["template"]))
    targeted, p_sha = load_json(Path(cfg["plan_template"]))
    types = targeted["types"]
    if template["condition"] != cfg["condition"]:
        raise ValueError(f"template {template['id']} is for {template['condition']}, config says {cfg['condition']}")
    tmpl_meta = {"template_id": template["id"], "template_version": template["version"], "template_sha256": t_sha,
                 "plan_template_sha256": p_sha}
    plan = build_plan(cfg, types, scale)
    assign_inputs(plan, cfg, types)
    # Tiny mode: the first `limit` requests (interleaving keeps every type represented).
    if limit is not None:
        plan = plan[:limit]

    # Dry run: show rendered prompts and plan size, load no model.
    if dry_run:
        for req in plan[:3]:
            print(f"--- {req.request_id}")
            for m in render_messages(template, types, req, cfg["mode"]):
                print(f"[{m['role']}] {m['content']}")
        print(f"plan: {len(plan)} pair requests over {len(types)} types")
        return {"dry_run": True, "requests": len(plan)}

    # Resume: skip requests that already have both records.
    out_path = Path(cfg["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = done_pairs(out_path)
    todo = [r for r in plan if r.request_id not in done]
    print(f"plan {len(plan)} pair requests, {len(done)} already done, {len(todo)} to generate", flush=True)
    if not todo:
        return {"requests": len(plan), "generated_now": 0}

    # Load the generator only now (slow, needs the GPU).
    from src.generation.llm import Generator, Sampling, vram_mib
    gen = Generator(cfg["generator"], cache_dir=Path(cfg["cache_dir"]), quantization=cfg["quantization"])
    sampling = Sampling(**cfg["sampling"])
    provenance = {"git_commit": git_commit(), "config_file": config_file}
    print(f"loaded {cfg['generator']} in {gen.load_seconds}s, VRAM {vram_mib()}", flush=True)

    # Generate batch by batch and append immediately, so a crash loses at most one batch.
    started, n_done, n_bad_sides, n_tokens = time.time(), 0, 0, 0
    bs = cfg["batch_size"]
    with open(out_path, "a", encoding="utf-8", newline="\n") as f:
        for b, start in enumerate(range(0, len(todo), bs), 1):
            batch = todo[start:start + bs]
            # Batch seed derived from the first request id, so a rerun gives the same text.
            seed = cfg["seed"] + int(hashlib.sha1(batch[0].request_id.encode()).hexdigest()[:6], 16)
            outs = gen.generate([render_messages(template, types, r, cfg["mode"]) for r in batch], sampling, seed=seed)
            for req, out in zip(batch, outs):
                out["seed"] = seed
                recs = make_records(req, parse_pair(out["raw_output"]), out, cfg, tmpl_meta, gen.revision, provenance)
                for r in recs:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
                n_done += 1
                n_bad_sides += sum(r["text"] is None for r in recs)
                n_tokens += out["new_tokens"]
            f.flush()
            if b % 20 == 0 or start + bs >= len(todo):
                el = time.time() - started
                print(f"  batch {b}: {n_done}/{len(todo)} pairs, {n_bad_sides} unparsed sides, "
                      f"{n_done / el:.2f} pairs/s, {n_tokens / el:.1f} tok/s, {el / 60:.1f} min", flush=True)

    el = time.time() - started
    return {"requests": len(plan), "generated_now": n_done, "unparsed_sides_now": n_bad_sides,
            "seconds": round(el), "pairs_per_second": round(n_done / max(1e-9, el), 3),
            "tokens_per_second": round(n_tokens / max(1e-9, el), 2), "vram": vram_mib(),
            "generator_revision": gen.revision, "system_role_supported": gen.system_role_supported}


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N requests, output gets _limitN")
    p.add_argument("--scale", type=float, default=None,
                   help="requests per type = ceil(target_pairs * scale); top-up raises it (same set, records kept)")
    p.add_argument("--dry-run", action="store_true", help="print rendered prompts and plan size; no model")
    p.add_argument("--reparse", action="store_true", help="parse the stored raw outputs again (after a parser fix); no model")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.reparse:
        print(json.dumps(reparse(Path(cfg["output"])), ensure_ascii=False))
        return
    scale = args.scale if args.scale is not None else cfg.get("scale", 1.1)
    # Tiny runs write to their own file so they never mix with the real set.
    if args.limit is not None:
        cfg["set_name"] += f"_limit{args.limit}"
        cfg["output"] = str(Path(cfg["output"]).with_name(f"{cfg['set_name']}.jsonl"))

    summary = run(cfg, str(args.config), args.limit, args.dry_run, scale)
    summary.update(config=cfg, scale=scale, template_sha256=load_json(Path(cfg["template"]))[1],
                   git_commit=git_commit(), python=platform.python_version(), finished=time.strftime("%Y-%m-%d %H:%M"))
    if not args.dry_run:
        with open(Path(cfg["output"]).with_suffix(".meta.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
