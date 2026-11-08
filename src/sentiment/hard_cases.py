"""Hard cases: tweets that the SR02 BERT runs get wrong, for grouping into error types (SG03 / SG04).

SG03 grouped the dev tweets wrong in all 63 SR02 runs (7 BERTs x 3 generators x seeds 42/43/44).
SG04 does the same on the official test set (Ammar, 2026-11-02; test-contaminated, see decisions.md):
the test set then shaped the prompts, so SG04 test scores are not an unbiased result.

Per tweet: wrong_runs = runs whose prediction differs from gold, majority_wrong_pred = most common
wrong prediction, sg03_types = the SG03 types the tweet matches (keyword rules of
src.sentiment.error_by_type; "other" = none), cue_tags = rough keyword cues for grouping the
test errors (CUES below; a tweet can have several, "-" = none). Kept: tweets with wrong_runs >= --min-wrong (default: a majority, 32 of 63, as
the dev list), sorted by wrong_runs, then file order.

EESA (D-032, --corpus eesa): the same rule over the 63 SR02-EESA runs on EESA dev, for the SG03-EESA types.
Dev only: EESA test must not shape any generation.

Outputs: data/inspect/hard_cases/sr02_<split>_hard_cases.{csv,md}; EESA: sr02_eesa_dev_hard_cases.{csv,md}.

Usage:
  python -m src.sentiment.hard_cases --split test
  python -m src.sentiment.hard_cases --split dev --min-wrong 60
  python -m src.sentiment.hard_cases --split dev --corpus eesa
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

from src.sentiment.error_by_type import types_of

RUNS_DIR = Path("results/sentiment/runs")
OUT_DIR = Path("data/inspect/hard_cases")
BERTS = ["marbertv2", "arabertv02_twitter", "marbert", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"]
GENS = ["fanar", "qwen3", "aya"]
SEEDS = [42, 43, 44]
# Keyword cues for grouping the test hard cases (proposal, 2026-11-02; rough, not validated).
CUES = {
    "spam_hashtag": r"#\S*(\S)\1\1\S*.*[A-Za-z0-9]{4,6}\s*$|#كلنا_ا+لدلماني|#\S*(\S)\2\2\S*_",
    "religious": r"اللهم|سبحان|استغفر|أستغفر|ﷺ|\(\(|﴿|\[[^\]]*:\s*\d+\]|لا اله الا|لا إله إلا|يارب|يا رب|الحمدلله|الحمد لله",
    "cry_laugh_emoji": r"😭|😂💔|💔😂|ه{6,}",
    "football": r"النصر|الهلال|الاهلي|الأهلي|الاتحاد|الدوري|مباراة|المباراه|المنتخب|هدف|ريال مدريد|برشلونة|الليغا",
    "politics": r"انتخاب|مجلس|نائب|النواب|الحكوم|السيسي|الرئيس|حزب|الوزير|وزير|البرلمان|الشعب|الثور|الحوثي|داعش|ايران|إيران",
    "kpop_fan": r"جين|يونجون|بانقتان|كيبوب|تيهيونق|سونقدوك|جيمين|بيكهيون|تيزر|ألبوم|البوم",
}


def cues_of(text: str) -> str:
    """Keyword cues of one tweet, plus very_short (at most 4 words)."""
    out = [k for k, pat in CUES.items() if re.search(pat, text)]
    if len(text.split()) <= 4:
        out.append("very_short")
    return " ".join(out) or "-"


COLS = ["text_id", "text", "wrong_runs", "of_runs", "majority_wrong_pred", "sg03_types", "cue_tags", "source", "origin", "split",
        "sentiment", "sarcasm", "dialect", "raw_rows", "label_conflict", "cleaning"]


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--split", choices=["dev", "test"], required=True)
    p.add_argument("--min-wrong", type=int, default=None, help="default: a majority of the runs")
    p.add_argument("--corpus", choices=["arsarcasm_v2", "eesa"], default="arsarcasm_v2")
    args = p.parse_args()
    if args.corpus == "eesa" and args.split != "dev":
        sys.exit("EESA hard cases come from dev only (D-032): EESA test must not shape generation")
    run = "sr02" if args.corpus == "arsarcasm_v2" else "sr02_eesa"

    # Wrong predictions per tweet over the 63 SR02 BERT runs.
    runs = [RUNS_DIR / f"{run}_{b}_{g}_seed{s}" / f"{args.split}_predictions.jsonl" for b in BERTS for g in GENS for s in SEEDS]
    missing = [r for r in runs if not r.exists()]
    if missing:
        sys.exit(f"missing predictions: {missing[:3]} ... ({len(missing)})")
    # Keyed by row position, not text_id: the test set has 5 ids on two rows with different gold labels.
    wrong: dict[int, Counter] = {}
    for path in runs:
        with open(path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                r = json.loads(line)
                c = wrong.setdefault(i, Counter())
                if r["pred"] != r["gold"]:
                    c[r["pred"]] += 1
    min_wrong = args.min_wrong or len(runs) // 2 + 1

    # Keep the hard tweets with their data fields.
    rows = []
    with open(f"data/processed/sentiment/{args.corpus}_{args.split}.jsonl", encoding="utf-8") as f:
        for i, line in enumerate(f):
            r = json.loads(line)
            c = wrong[i]
            if sum(c.values()) >= min_wrong:
                rows.append((-sum(c.values()), i, r | {"wrong_runs": sum(c.values()), "of_runs": len(runs),
                                                       "majority_wrong_pred": c.most_common(1)[0][0],
                                                       "sg03_types": " ".join(types_of(r)), "cue_tags": cues_of(r["text"])}))
    rows = [r for *_, r in sorted(rows, key=lambda x: x[:2])]

    # CSV (with BOM, as the dev file, so Excel shows Arabic) and a markdown view.
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stem = OUT_DIR / f"{run}_{args.split}_hard_cases"
    with open(stem.with_suffix(".csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    md = ["| # | Wrong | Gold → pred | SG03 type | Cues | Sarc. | Dialect | Text |", "|---|---|---|---|---|---|---|---|"]
    md += [f"| {k} | {r['wrong_runs']}/{r['of_runs']} | {r['sentiment']} → {r['majority_wrong_pred']} | "
           f"{r['sg03_types']} | {r['cue_tags']} | {'yes' if r.get('sarcasm') else ''} | {r['dialect']} | {r['text'].replace('|', '/').replace(chr(10), ' ')} |"
           for k, r in enumerate(rows, 1)]
    stem.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print(f"{args.split}: {len(rows)} tweets wrong in >= {min_wrong}/{len(runs)} runs -> {stem}.md")
    print(dict(Counter(f"{r['sentiment']}->{r['majority_wrong_pred']}" for r in rows).most_common()))
    print(dict(Counter(t for r in rows for t in r["sg03_types"].split()).most_common()))
    print(dict(Counter(t for r in rows for t in r["cue_tags"].split()).most_common()))


if __name__ == "__main__":
    sys.exit(main())
