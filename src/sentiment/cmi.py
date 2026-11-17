"""Code-mixing statistics per text for code-switched sets (matrix-language pilot, SG03-EESA, D-037).

Per text, after links and mentions are removed (the placeholder rule of src/quality/measure.py):
  - every whitespace token gets a language by script: "ar" if it has Arabic letters and no Latin
    letters, "en" if it has a Latin word (2+ letters) and no Arabic letters, "mixed" if it has both,
    otherwise "other" (digits, emoji, punctuation; language-independent);
  - CMI (Das and Gambaeck 2014): 100 x (1 - max(n_ar, n_en) / (n - u)), with n the tokens and u the
    "other" tokens; 0 when no token has a language. "mixed" tokens count as words of neither language;
  - switch-point fraction: language changes between neighbouring language tokens / (language tokens - 1);
  - Latin-word share: Latin-script words / all words (quality row 8).
Sentence-ALDi is not used: it strips Latin letters.

Limit: the language is read from the script, so Arabic written in Latin letters (Franco-Arabic) counts
as English and an English word written in Arabic letters counts as Arabic.

Inputs: name=path.jsonl pairs (real or synthetic records with `text`). Outputs: <out>.json with the
per-set summary (mean, median, share of texts with CMI 0) and, for synthetic sets, <path>.cmi.jsonl
with one row per text (text_id, template_id, matrix_language, the statistics), so every sample keeps
its matrix-language setting.

Usage:
  python -m src.sentiment.cmi --sets real_eesa=data/processed/sentiment/eesa_train.jsonl \
      sg03dm_eesa_qwen3=data/synthetic/sentiment/sg03dm_eesa_qwen3.selected.jsonl --out results/quality/sentiment/cmi_sg03_eesa
  python -m src.sentiment.cmi --sets ... --out ... --limit 50     # tiny mode
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from src.data.build_dataset import git_commit, sha256
from src.quality.measure import ARABIC_LETTER_RE, LATIN_WORD_RE, PLACEHOLDER_RE


def token_language(token: str) -> str:
    """'ar', 'en', 'mixed' or 'other' from the token's script."""
    ar, en = bool(ARABIC_LETTER_RE.search(token)), bool(LATIN_WORD_RE.search(token))
    return "mixed" if ar and en else "ar" if ar else "en" if en else "other"


def text_stats(text: str) -> dict:
    """CMI, switch-point fraction and Latin-word share of one text."""
    langs = [token_language(t) for t in PLACEHOLDER_RE.sub(" ", text).split()]
    n_ar, n_en = langs.count("ar"), langs.count("en")
    with_lang = len(langs) - langs.count("other")
    # Switch points between neighbouring Arabic / English tokens ("other" and "mixed" tokens are skipped).
    seq = [l for l in langs if l in ("ar", "en")]
    switches = sum(a != b for a, b in zip(seq, seq[1:]))
    return {"words": len(langs), "arabic_words": n_ar, "latin_words": n_en,
            "cmi": 100 * (1 - max(n_ar, n_en) / with_lang) if with_lang else 0.0,
            "switch_points": switches,
            "switch_point_fraction": switches / (len(seq) - 1) if len(seq) > 1 else 0.0,
            "latin_word_share": n_en / len(langs) if langs else 0.0,
            "dominant": "ar" if n_ar > n_en else "en" if n_en > n_ar else "tie"}


def main() -> None:
    """Measure every set, write the summary and the per-text rows of the synthetic sets."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--sets", nargs="+", required=True, help="name=path.jsonl pairs")
    p.add_argument("--out", type=Path, required=True, help="output path without extension")
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N texts per set, no per-text files")
    args = p.parse_args()

    summary = {}
    for pair in args.sets:
        name, path = pair.split("=", 1)
        with open(path, encoding="utf-8") as f:
            records = [r for r in map(json.loads, f) if r.get("text")][:args.limit]
        # The matrix-language setting is the template's (prompts/sentiment/matrix_eesa_*): one per set.
        matrix = None
        if records and records[0].get("source") == "synthetic":
            cfg = json.loads(Path(records[0]["config_file"]).read_text(encoding="utf-8"))
            matrix = json.loads(Path(cfg["template"]).read_text(encoding="utf-8")).get("matrix_language")
        rows = [{"text_id": r.get("text_id"), "sentiment": r.get("sentiment"), "template_id": r.get("template_id"),
                 "matrix_language": matrix, **text_stats(r["text"])} for r in records]
        mean = lambda k: statistics.fmean(x[k] for x in rows)
        summary[name] = {"path": path, "sha256": sha256(Path(path)), "n": len(rows), "matrix_language": matrix,
                         "cmi_mean": mean("cmi"), "cmi_median": statistics.median(x["cmi"] for x in rows),
                         "cmi_zero_share": statistics.fmean(x["cmi"] == 0 for x in rows),
                         "switch_point_fraction_mean": mean("switch_point_fraction"),
                         "switch_points_mean": mean("switch_points"),
                         "latin_word_share_mean": mean("latin_word_share"),
                         "latin_word_share_median": statistics.median(x["latin_word_share"] for x in rows),
                         "words_mean": mean("words"),
                         "dominant_share": {d: statistics.fmean(x["dominant"] == d for x in rows) for d in ("ar", "en", "tie")}}
        s = summary[name]
        print(f"{name}: n {s['n']}, CMI {s['cmi_mean']:.1f} (median {s['cmi_median']:.1f}, zero {s['cmi_zero_share']:.0%}), "
              f"switch-point fraction {s['switch_point_fraction_mean']:.2f}, Latin words {s['latin_word_share_mean']:.0%}, "
              f"{s['words_mean']:.1f} words", flush=True)
        # Per-text rows next to the synthetic set, so each sample carries its CMI and matrix setting.
        if matrix is not None and args.limit is None:
            with open(Path(path).with_suffix(".cmi.jsonl"), "w", encoding="utf-8", newline="\n") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out.with_suffix(".json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump({"sets": summary, "git_commit": git_commit(), "finished": time.strftime("%Y-%m-%d %H:%M")},
                  f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    sys.exit(main())
