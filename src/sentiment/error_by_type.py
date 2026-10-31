"""Test error rates by SG03 text type: did the targeted pairs fix the types they were made for?

Post-hoc analysis after SR05/SR06 were scored (the test set is not used to design anything here).
Every official test tweet is tagged by keyword rules into the SG03 types (rough: the same rules
as the S1-train counts behind D-021; a tweet can match several types, or none = "other"):
  news_bad    a link and a bad-event word (killed, strike, arrest, ...), no first-person word
  news_good   a link and a good-event word (win, opening, award, ...), no bad-event word, no first person
  short_dialect  egypt/gulf/levant tweet of at most 10 words without a link (complaint candidates)
  lyric       a singer or poet hashtag, or a music emoji (🎶 🎵)
  fan_post    at most 14 words, a hashtag and a heart / star emoji, no link
For each type and each condition (SR01 real, SR04 + SG02, SR05 + SG03, SR06 + SG03-random; BERTs
only), the error rate = share of the type's test tweets a run gets wrong, averaged over the runs
(mean of the seed means per BERT x generator cell, then over cells), also split by gold label.

Outputs: results/sentiment/analysis/error_by_type.json, docs/sentiment/tables/error_by_type.{csv,md}.

Usage:
  python -m src.sentiment.error_by_type
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

TEST = Path("data/processed/sentiment/arsarcasm_v2_test.jsonl")
RUNS_DIR = Path("results/sentiment/runs")
BERTS = ["marbertv2", "arabertv02_twitter", "marbert", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"]
GENS = ["fanar", "qwen3", "aya"]
CONDITIONS = {"SR01 real": ["sr01_{b}"], "SR04 + SG02": ["sr04_{b}_" + g for g in GENS],
              "SR05 + SG03": ["sr05_{b}_" + g for g in GENS], "SR06 + SG03-random": ["sr06_{b}_" + g for g in GENS]}

BAD = r"قتل|مقتل|قتلى|غار[ةات]|قصف|انفجار|تفجير|اعتقا?ل|يعتقل|شهيد|شهداء|جرحى|[إا]صاب|ضحايا|هجوم|[إا]رهاب|تدين|يدين|[إا]دانة|حادث|اشتباك|معارك|اغتيال|احتجاز|ضبط|حريق|غرق|وفاة|مصرع|[إا]عدام|حصار|تهجير|دمار|مي?لي?شيا|احتلال|استيطان|عدوان|تعذيب|طوارئ"
GOOD = r"فوز|يفوز|فاز|تكريم|يكرم|افتتاح|يفتتح|نجاح|[إا]نجاز|جائز[ةه]|يحتفل|احتفال|تأهل|يتأهل|يتوج|تتويج|ميدالية|ذهبية"
FIRST = r"(?:^|\s)(?:انا|أنا|احس|أحس|عندي|ابغى|ابغا|ودي|بدي)(?:\s|$)"
SINGER = r"#(?:[إا]ليسا|نوال_الزغبي|نانسي|عمرو_دياب|شيرين|راغب|تامر_حسني|ماجدة|وائل|هيفاء|فيروز|كاظم|محمد_عبده|عبدالحليم|[اأ]م_كلثوم|حسين_الجسمي|[اأ]صالة|ملحم|جورج_وسوف|محمد_منير|[اأ]حلام)|🎶|🎵"
HEART = r"[❤♥💕💞💘😍🥰😘😙💙💛💚🌹🔥👏⭐🌟]"


def types_of(r: dict) -> list[str]:
    """SG03 types a test tweet matches (keyword rules)."""
    t, n = r["text"], len(r["text"].split())
    out = []
    news = "URL" in t and not re.search(FIRST, t)
    if news and re.search(BAD, t):
        out.append("news_bad")
    elif news and re.search(GOOD, t):
        out.append("news_good")
    if r["dialect"] in ("egypt", "gulf", "levant") and n <= 10 and "URL" not in t:
        out.append("short_dialect")
    if re.search(SINGER, t):
        out.append("lyric")
    if n <= 14 and "#" in t and re.search(HEART, t) and "URL" not in t:
        out.append("fan_post")
    return out or ["other"]


def errors(pattern: str, ids: set[str]) -> list[float] | None:
    """Per finished seed of one cell: share of the given test tweets predicted wrongly."""
    out = []
    for d in sorted(RUNS_DIR.glob(pattern + "_seed*")):
        if not re.fullmatch(r".*_seed\d+", d.name) or not (d / "test_predictions.jsonl").exists():
            continue
        preds = [json.loads(l) for l in open(d / "test_predictions.jsonl", encoding="utf-8")]
        sel = [p for p in preds if p["text_id"] in ids]
        out.append(sum(p["pred"] != p["gold"] for p in sel) / len(sel))
    return out or None


def main() -> None:
    """Tag the test set, compute error rates per type x gold x condition, write tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    test = [json.loads(l) for l in open(TEST, encoding="utf-8")]
    groups: dict[str, set[str]] = {}
    gold = {r["text_id"]: r["sentiment"] for r in test}
    for r in test:
        for t in types_of(r):
            groups.setdefault(t, set()).add(r["text_id"])
            groups.setdefault(f"{t} | gold {r['sentiment']}", set()).add(r["text_id"])
    groups["all"] = set(gold)

    rows = []
    for name in ["all", "news_bad", "news_good", "short_dialect", "lyric", "fan_post", "other"] + sorted(
            k for k in groups if "|" in k):
        ids = groups.get(name)
        if not ids:
            continue
        row = {"group": name, "n": len(ids), "gold": dict(Counter(gold[i] for i in ids))}
        for cond, patterns in CONDITIONS.items():
            # Mean over seeds per cell, then mean over BERT x generator cells.
            cells = [statistics.fmean(e) for b in BERTS for p in patterns if (e := errors(p.format(b=b), ids))]
            row[cond] = statistics.fmean(cells) if cells else None
        rows.append(row)

    out = Path("results/sentiment/analysis")
    out.mkdir(parents=True, exist_ok=True)
    (out / "error_by_type.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    conds = list(CONDITIONS)
    with open("docs/sentiment/tables/error_by_type.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["group", "n", "gold"] + conds)
        for r in rows:
            w.writerow([r["group"], r["n"], json.dumps(r["gold"])] + [r[c] for c in conds])
    md = ["# Test error rate by SG03 text type", "",
          "Generated by `python -m src.sentiment.error_by_type`. Do not edit by hand. Error rate = share of the group's "
          "official test tweets a run gets wrong; mean over seeds per BERT (× generator) cell, then over cells "
          "(SR01: 7 cells, others: 21). Types are keyword rules (rough); a tweet can be in several types. "
          "Δ = SR05 − SR06 (negative = the targeted pairs make fewer errors than the control).", "",
          "| Group | Tweets | Gold NEG / NEU / POS | " + " | ".join(conds) + " | Δ SR05 − SR01 | Δ SR05 − SR06 |",
          "|---|---|---|" + "---|" * (len(conds) + 2)]
    for r in rows:
        g = r["gold"]
        md.append(f"| {r['group']} | {r['n']} | {g.get('NEG', 0)} / {g.get('NEU', 0)} / {g.get('POS', 0)} | "
                  + " | ".join(f"{100 * r[c]:.1f}%" for c in conds)
                  + f" | {100 * (r['SR05 + SG03'] - r['SR01 real']):+.1f} | {100 * (r['SR05 + SG03'] - r['SR06 + SG03-random']):+.1f} |")
    Path("docs/sentiment/tables/error_by_type.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[4:]))


if __name__ == "__main__":
    sys.exit(main())
