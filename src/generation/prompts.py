"""Prompt templates, generation plans, few-shot selection and output parsing.

A template is a versioned JSON file in prompts/ (see prompts/open_v1.json and
prompts/controlled_v1.json). A plan is the full list of requests one generation run will
make: one entry per (dialect, index) with every control-factor value fixed in advance, so
open and controlled sets have matched sizes and every record is traceable to its factors.
"""
from __future__ import annotations

import hashlib
import json
import random
import re
from dataclasses import dataclass, field
from itertools import product
from pathlib import Path

from src.data.build_dataset import DIALECTS

DIALECTS_FILE = Path("prompts/dialects.json")

# Output clean-up: list markers, numbering, quotes and label prefixes the models like to add.
LIST_PREFIX_RE = re.compile(r"^\s*(?:[-*•]|\(?\d{1,2}[.)-]|\d{1,2}\s*[-–])\s*")
LABEL_PREFIX_RE = re.compile(r"^\s*(?:sentence|tweet|output|answer|الجملة|التغريدة|الجواب)\s*[:：]\s*", re.I)
QUOTE_CHARS = "\"'«»“”„‘’`"
# Lines starting like this are preambles or explanations, never the sentence itself.
PREAMBLE_STARTS = ("here is", "here are", "here's", "sure", "certainly", "translation", "note",
                   "explanation", "meaning", "(", "**", "الترجمة", "ملاحظة", "بالطبع", "تفضل", "إليك", "اليك")
# Placeholders left by D1 cleaning; texts containing them make poor few-shot examples.
PLACEHOLDER_RE = re.compile(r"\b(?:USER|URL)\b")
# Arabic-script letters (Arabic, Supplement, Extended-A, Presentation Forms).
ARABIC_LETTER_RE = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿﭐ-﷿ﹰ-﻿]")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")


@dataclass
class Template:
    """A versioned prompt template loaded from prompts/<id>.json."""
    id: str
    version: int
    condition: str
    system: str
    user: str
    sha256: str
    path: str
    few_shot_header: str = ""
    few_shot_item: str = "- {text}"
    options: dict = field(default_factory=dict)

    @classmethod
    def load(cls, path: Path) -> "Template":
        """Read a template file and record its hash so records can be tied to the exact wording."""
        raw = path.read_bytes()
        t = json.loads(raw.decode("utf-8"))
        return cls(id=t["id"], version=t["version"], condition=t["condition"], system=t.get("system", ""),
                   user=t["user"], sha256=hashlib.sha256(raw).hexdigest(), path=str(path),
                   few_shot_header=t.get("few_shot_header", ""), few_shot_item=t.get("few_shot_item", "- {text}"),
                   options=t.get("options", {}))


def load_dialect_names() -> dict[str, dict]:
    """Country label -> {"en", "ar", "demonym"} from prompts/dialects.json."""
    with open(DIALECTS_FILE, encoding="utf-8") as f:
        return json.load(f)["dialects"]


# ---------------------------------------------------------------- plan

@dataclass
class Request:
    """One generation request: the target dialect, its index and the control-factor values."""
    request_id: str
    dialect: str
    index: int
    controls: dict
    few_shot_ids: list[str] = field(default_factory=list)
    few_shot_texts: list[str] = field(default_factory=list)


def control_grid(controls: dict) -> list[dict]:
    """Every combination of the control-factor values given in the config (the balanced grid)."""
    # Each factor is a list of values; "lengths" is a dict name -> [min_words, max_words].
    factors = {
        "topic": controls["topics"],
        "script": controls["scripts"],
        "length": list(controls["lengths"]),
        "code_switching": controls["code_switching"],
    }
    names = list(factors)
    return [dict(zip(names, combo)) for combo in product(*factors.values())]


def build_plan(cfg: dict) -> list[Request]:
    """List every request of a run: per dialect, `per_dialect` entries, with factor values assigned.

    Open condition: the only control is the dialect. Controlled condition: the values are
    taken from a per-dialect shuffled copy of the full factor grid, cycled, so every factor
    level occurs equally often within each dialect (up to rounding), and the two conditions
    have exactly the same number of requests per dialect.
    """
    dialects = DIALECTS if cfg["dialects"] == "all" else cfg["dialects"]
    per_dialect, seed = cfg["per_dialect"], cfg["seed"]
    grid = control_grid(cfg["controls"]) if cfg.get("controls") else None
    plan = []
    for d_i, dialect in enumerate(dialects):
        # Own RNG per dialect so adding a dialect never changes another dialect's plan.
        rng = random.Random(f"{seed}:{dialect}")
        order = rng.sample(grid, len(grid)) if grid else None
        for j in range(per_dialect):
            controls = {"dialect": dialect}
            if order:
                # Cycle through the shuffled grid; reshuffle each time it is exhausted.
                if j % len(order) == 0 and j > 0:
                    order = rng.sample(grid, len(grid))
                controls.update(order[j % len(order)])
            plan.append(Request(request_id=f"{cfg['set_name']}:{dialect}:{j}", dialect=dialect,
                                index=j, controls=controls))
    return plan


# ---------------------------------------------------------------- few-shot

def load_few_shot_pool(cfg: dict) -> dict[str, list[dict]]:
    """Per dialect, the D1 records allowed as few-shot examples (never MLADI dev/test).

    Only D1 (the training data) is read. Candidates must have the dialect marked valid,
    at most `max_cardinality` valid dialects (so the example is characteristic of that
    dialect rather than valid everywhere) and ALDi >= `min_aldi` (so it is dialectal, not MSA).
    """
    fs = cfg.get("few_shot") or {}
    if not fs.get("k"):
        return {}
    pool: dict[str, list[dict]] = {d: [] for d in DIALECTS}
    with open(Path(fs["source"]), encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            if r.get("source") != "real":
                raise ValueError("few-shot source must be real data (D1)")
            if r["cardinality"] > fs.get("max_cardinality", 1) or r["aldi_score"] < fs.get("min_aldi", 0.5):
                continue
            # Skip very short texts and texts with USER/URL placeholders; they make poor examples.
            if len(r["text"].split()) < fs.get("min_words", 4):
                continue
            if fs.get("exclude_placeholders", True) and PLACEHOLDER_RE.search(r["text"]):
                continue
            for d, v in r["labels"].items():
                if v:
                    pool[d].append({"text_id": r["text_id"], "text": r["text"]})
    return pool


def assign_few_shot(plan: list[Request], pool: dict[str, list[dict]], cfg: dict) -> None:
    """Pick k examples per request from the pool, reproducibly from (seed, request_id)."""
    k = (cfg.get("few_shot") or {}).get("k", 0)
    if not k:
        return
    for req in plan:
        candidates = pool.get(req.dialect, [])
        if len(candidates) < k:
            raise ValueError(f"only {len(candidates)} few-shot candidates for {req.dialect}, need {k}")
        rng = random.Random(f"{cfg['seed']}:{req.request_id}")
        chosen = rng.sample(candidates, k)
        req.few_shot_ids = [c["text_id"] for c in chosen]
        req.few_shot_texts = [c["text"] for c in chosen]


# ---------------------------------------------------------------- rendering

def render_messages(template: Template, req: Request, cfg: dict, names: dict[str, dict]) -> list[dict]:
    """Fill the template with the request's values; return chat messages (system + user)."""
    d = req.dialect
    values = {
        "dialect": d,
        "dialect_name": names[d]["en"],
        "dialect_name_ar": names[d]["ar"],
        "demonym": names[d]["demonym"],
        # English article for the demonym ("an Egyptian", "a Syrian").
        "article": "an" if names[d]["demonym"][0].lower() in "aeiou" else "a",
        "n_sentences": cfg.get("sentences_per_request", 1),
    }
    # Controlled condition: turn each factor value into its instruction text from the template.
    if cfg.get("controls"):
        c, opts = req.controls, template.options
        lo, hi = cfg["controls"]["lengths"][c["length"]]
        values.update(
            topic=c["topic"],
            script_instruction=opts["script"][c["script"]],
            length_instruction=opts["length"].format(min_words=lo, max_words=hi),
            code_switching_instruction=opts["code_switching"][c["code_switching"]].format(
                foreign_language=cfg["controls"]["foreign_language"].get(d, cfg["controls"]["foreign_language"]["default"])),
        )
    # Few-shot block (empty string when k = 0).
    if req.few_shot_texts:
        items = "\n".join(template.few_shot_item.format(text=t) for t in req.few_shot_texts)
        values["few_shot_block"] = template.few_shot_header.format(**values) + "\n" + items + "\n\n"
    else:
        values["few_shot_block"] = ""
    user = template.user.format(**values)
    messages = []
    if template.system:
        messages.append({"role": "system", "content": template.system.format(**values)})
    messages.append({"role": "user", "content": user})
    return messages


# ---------------------------------------------------------------- parsing

def clean_line(line: str) -> str:
    """Remove list markers, label prefixes and wrapping quotes from one output line."""
    s = LIST_PREFIX_RE.sub("", line.strip())
    s = LABEL_PREFIX_RE.sub("", s)
    s = s.strip().strip(QUOTE_CHARS).strip()
    return s


def parse_output(raw: str, n_sentences: int, script: str = "arabic") -> list[str]:
    """Extract the generated sentence(s) from the raw model output.

    Models often add a preamble ("Here is a sentence:"), numbering, quotes, or an English
    translation/explanation after the sentence. Rules: drop lines that end with ":" or start
    like a preamble/explanation ("Here is", "Translation", "Note", parentheses); clean the
    rest; for Arabic-script requests keep only lines with Arabic letters, for Arabizi
    requests only lines with Latin letters and no Arabic letters; return the first
    `n_sentences`. The raw output is always stored, so nothing is lost.
    """
    lines = [l for l in raw.replace("\r", "").split("\n") if l.strip()]
    kept = []
    for l in lines:
        low = l.strip().lower()
        if low.endswith(":") or low.startswith(PREAMBLE_STARTS):
            continue
        s = clean_line(l)
        if not s:
            continue
        has_ar, has_lat = bool(ARABIC_LETTER_RE.search(s)), bool(LATIN_LETTER_RE.search(s))
        if script == "arabizi" and (has_ar or not has_lat):
            continue
        if script != "arabizi" and not has_ar:
            continue
        kept.append(s)
        if len(kept) == n_sentences:
            break
    return kept
