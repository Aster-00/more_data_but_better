"""Back-translation with NLLB-200: dialect -> English -> dialect, as a third synthetic generator.

Source sentences come from D1 only (real, single-label texts of the target dialect). Each is
translated to the pivot language and back with NLLB's dialect codes. NLLB-200 covers only
some dialects (Egyptian arz, Moroccan ary, Tunisian aeb, Mesopotamian acm, North Levantine
apc, South Levantine ajp, Najdi ars, Ta'izzi-Adeni acq, MSA arb); for the other countries the
config maps to the nearest code and the record carries `nllb_exact=false`.

Output: JSONL (resumable by parent text_id) with the same provenance fields as the LLM
generators, plus parent_text_id, parent_text, pivot_text, src_lang, tgt_lang, nllb_exact.
Labels are copied from the parent (label_mode "parent_labels").

Usage:
  python -m src.generation.backtranslate --config configs/generation/backtranslate_v1.json --limit 10
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import time
from pathlib import Path

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

from src.data.build_dataset import DIALECTS, git_commit, sha256
from src.generation.prompts import PLACEHOLDER_RE


def select_parents(cfg: dict) -> dict[str, list[dict]]:
    """Per dialect, the D1 records chosen as back-translation sources (reproducible from the seed)."""
    sel = cfg["selection"]
    pool: dict[str, list[dict]] = {d: [] for d in DIALECTS}
    with open(Path(cfg["source"]), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("source") != "real":
                raise ValueError("back-translation sources must be real data (D1)")
            # Single-label, dialectal, long enough and without placeholders.
            if r["cardinality"] != 1 or r["aldi_score"] < sel["min_aldi"]:
                continue
            if not sel["min_words"] <= len(r["text"].split()) <= sel["max_words"]:
                continue
            if sel.get("exclude_placeholders", True) and PLACEHOLDER_RE.search(r["text"]):
                continue
            d = next(k for k, v in r["labels"].items() if v)
            pool[d].append({"text_id": r["text_id"], "text": r["text"], "labels": r["labels"]})
    # Sample per dialect; fewer if the pool is smaller (recorded in the meta file).
    dialects = DIALECTS if cfg["dialects"] == "all" else cfg["dialects"]
    chosen = {}
    for d in dialects:
        rng = random.Random(f"{cfg['seed']}:{d}")
        chosen[d] = rng.sample(pool[d], min(cfg["per_dialect"], len(pool[d])))
    return chosen


class Translator:
    """NLLB-200 seq2seq model with batched translation between language codes."""

    def __init__(self, model_id: str, cache_dir: Path, device: str, batch_size: int) -> None:
        """Load the model in bf16 on the device."""
        kw = {"cache_dir": str(cache_dir)}
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, **kw)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id, dtype=torch.bfloat16, **kw).to(device).eval()
        self.device, self.batch_size = device, batch_size

    @torch.no_grad()
    def translate(self, texts: list[str], src: str, tgt: str, decoding: dict) -> list[str]:
        """Translate texts from `src` to `tgt` (NLLB codes) with the given decoding settings."""
        self.tokenizer.src_lang = src
        out = []
        for start in range(0, len(texts), self.batch_size):
            enc = self.tokenizer(texts[start:start + self.batch_size], return_tensors="pt", padding=True,
                                 truncation=True, max_length=decoding["max_length"]).to(self.device)
            gen = self.model.generate(**enc, forced_bos_token_id=self.tokenizer.convert_tokens_to_ids(tgt),
                                      num_beams=decoding["num_beams"], do_sample=decoding["do_sample"],
                                      temperature=decoding.get("temperature", 1.0), top_p=decoding.get("top_p", 1.0),
                                      max_new_tokens=decoding["max_length"])
            out.extend(self.tokenizer.batch_decode(gen, skip_special_tokens=True))
        return out


def run(cfg: dict, config_file: str, limit: int | None, device: str) -> dict:
    """Select parents, back-translate those not done yet, append records; return a summary."""
    parents = select_parents(cfg)
    jobs = [(d, p) for d, ps in parents.items() for p in ps]
    if limit is not None:
        per = max(1, limit // max(1, len(parents)))
        jobs = [(d, p) for d, ps in parents.items() for p in ps[:per]][:limit]

    # Resume: skip parents already in the output.
    out_path = Path(cfg["output"])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    done = set()
    if out_path.exists():
        with open(out_path, encoding="utf-8") as f:
            done = {json.loads(l)["parent_text_id"] for l in f if l.strip()}
    todo = [(d, p) for d, p in jobs if p["text_id"] not in done]
    print(f"{len(jobs)} parents, {len(done)} done, {len(todo)} to translate")
    summary = {"parents": len(jobs), "parents_per_dialect": {d: len(ps) for d, ps in parents.items()},
               "generated_now": 0}
    if not todo:
        return summary

    tr = Translator(cfg["generator"], Path(cfg["cache_dir"]), device, cfg["batch_size"])
    provenance = {"git_commit": git_commit(), "config_file": config_file,
                  "generator_revision": getattr(tr.model.config, "_commit_hash", None)}
    started, n = time.time(), 0
    with open(out_path, "a", encoding="utf-8", newline="\n") as f:
        # Group by dialect so one src/tgt code is used per batch.
        for d in DIALECTS:
            group = [p for dd, p in todo if dd == d]
            if not group:
                continue
            lang = cfg["nllb_lang"].get(d)
            if lang is None:
                print(f"  {d}: no NLLB code configured, skipped")
                continue
            code, exact = lang["code"], lang["exact"]
            texts = [p["text"] for p in group]
            # Forward to the pivot and back.
            pivot = tr.translate(texts, code, cfg["pivot"], cfg["decoding"])
            back = tr.translate(pivot, cfg["pivot"], code, cfg["decoding"])
            for p, piv, bt in zip(group, pivot, back):
                rid = f"{cfg['set_name']}:{p['text_id']}"
                f.write(json.dumps({
                    "text_id": "s" + hashlib.sha1(rid.encode("utf-8")).hexdigest()[:16],
                    "request_id": rid,
                    "text": bt.strip() or None,
                    "source": "synthetic",
                    "condition": "backtranslation",
                    "generator": cfg["generator"],
                    "quantization": "none",
                    "template_id": None, "template_version": None, "template_sha256": None,
                    "controls": {"dialect": d},
                    "target_dialect": d,
                    "labels": p["labels"],
                    "label_mode": "parent_labels",
                    "sampling": cfg["decoding"],
                    "seed": cfg["seed"],
                    "few_shot_ids": [],
                    "prompt": None,
                    "raw_output": bt,
                    "parse_ok": bool(bt.strip()),
                    "parent_text_id": p["text_id"],
                    "parent_text": p["text"],
                    "pivot_text": piv,
                    "src_lang": code, "pivot_lang": cfg["pivot"], "nllb_exact": exact,
                    "created": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    **provenance,
                }, ensure_ascii=False) + "\n")
                n += 1
            f.flush()
            print(f"  {d}: {len(group)} done ({(time.time() - started) / 60:.1f} min)")
    summary.update(generated_now=n, seconds=round(time.time() - started), **provenance)
    return summary


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N parents, output gets _limitN")
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    args = p.parse_args()
    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    if args.limit is not None:
        cfg["set_name"] += f"_limit{args.limit}"
        cfg["output"] = str(Path(cfg["output"]).with_name(f"{cfg['set_name']}.jsonl"))
    summary = run(cfg, str(args.config), args.limit, args.device)
    summary.update(config=cfg, source_sha256=sha256(Path(cfg["source"])), python=platform.python_version(),
                   finished=time.strftime("%Y-%m-%d %H:%M"))
    with open(Path(cfg["output"]).with_suffix(".meta.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: v for k, v in summary.items() if k != "config"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
