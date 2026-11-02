"""Survey of the downloaded Arabic sentiment datasets against the dataset standards (chron.md, 2026-10-31).

Why: ArSarcasm-v2's official test split differs from its train split (links 38.5% vs 14.7%, labels
NEU 46% vs 25%; SA-E01), so the SG03 experiment is repeated on a dataset whose splits match.
Every candidate is checked against the same standards:
  S1 human labels      sentence-level sentiment labelled by people (not star ratings, emojis or lexicons)
  S2 three classes     POS / NEG / NEU, as ArSarcasm-v2, so macro F1 and the NEU findings compare
  S3 Arabic script     each text is Arabic script if >= 70% of its letters are Arabic (quality row 8);
                       a dataset passes if >= 70% of its texts are, or if after keeping only the Arabic-
                       script texts it still passes S4 and S5
  S4 uniform splits    official train and test from the same distribution: every class share within
                       5 points between train and test, and link, mention and hashtag shares within 5
                       points, mean length within a factor 1.25 (after the S3 filter). Without an official
                       split a stratified split can be made, but there is then no independent benchmark
  S5 size              after the S3 filter: train >= 1,000 texts, test >= 500, smallest class >= 5% of train
  S6 text available    the texts themselves are in the download (not tweet IDs only)
Only datasets that pass S1 and S2 are measured; the others are listed with the reason.

Outputs: docs/sentiment/tables/dataset_survey.{csv,md}. No text is written.

Usage:
  python -m src.sentiment.dataset_survey
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

from src.data.xlsx import read_xlsx

SA, BOTH = Path("data/datasets/sa"), Path("data/datasets/both")
LABELS = {"positive": "POS", "negative": "NEG", "neutral": "NEU", "pos": "POS", "neg": "NEG", "neu": "NEU",
          "1": "POS", "-1": "NEG", "0": "NEU"}
ARABIC_RE, LATIN_RE = re.compile(r"[؀-ۿݐ-ݿ]"), re.compile(r"[A-Za-z]")
LINK_RE, MENTION_RE = re.compile(r"https?://|\bURL\b"), re.compile(r"@\w|\bUSER\b|@user")


def rows_csv(path: Path, text: str, label: str, delimiter: str = ",", header: bool = True) -> list[tuple[str, str]]:
    """(text, raw label) pairs of a CSV/TSV, by column name or (without a header) index."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        if header:
            return [(r[text] or "", r[label] or "") for r in csv.DictReader(f, delimiter=delimiter)]
        return [(r[int(text)], r[int(label)]) for r in csv.reader(f, delimiter=delimiter) if len(r) > 1]


def candidates() -> dict[str, dict]:
    """The S1 + S2 candidates: name -> {splits: {split: [(text, label)]}, notes}."""
    ars = BOTH / "ArSarcasm-v2" / "ArSarcasm-v2"
    out = {"ArSarcasm-v2 (current)": {"splits": {s: rows_csv(ars / f"{f}_data.csv", "tweet", "sentiment")
                                                 for s, f in (("train", "training"), ("test", "testing"))},
                                      "source": "tweets, crowd labels"}}
    out["EESA"] = {"splits": {s.lower(): rows_csv(SA / "EESA-Corpus-main" / f"EESA-{s}.csv", "0", "1", header=False)
                              for s in ("Train", "Dev", "Test")},
                   "source": "Egyptian YouTube comments, Arabic-English code-switched"}
    for lang, name in (("arq", "AfriSenti Algerian (arq)"), ("ary", "AfriSenti Moroccan (ary)")):
        out[name] = {"splits": {s: rows_csv(SA / "afrisent-semeval-2023-main" / "data" / lang / f"{s}.tsv", "tweet", "label", "\t")
                                for s in ("train", "dev", "test")}, "source": "tweets, 3 native annotators (SemEval-2023)"}
    out["Mawqif"] = {"splits": {s.lower(): rows_csv(SA / "Mawqif-Arabic-Stance-main" / "Data" / f"Mawqif_AllTargets_{s}.csv",
                                                    "text", "sentiment") for s in ("Train", "Test")},
                     "source": "tweets on 3 targets (COVID vaccine, digital transformation, women's empowerment)"}
    out["ArSen-20"] = {"splits": {"all": rows_csv(SA / "ArSen-20-main" / "data" / "ArSen-20_publish.csv", "tweet", "label")},
                       "source": "COVID-19 tweets 2020-2023; the file has no split column"}
    at = read_xlsx(SA / "AT-ODTSA-main" / "AT-ODTSA_Dataset_RawDataV1-1.xlsx")["Sayfa1"]
    out["AT-ODTSA"] = {"splits": {"all": [(r[0], r[2]) for r in at[1:] if len(r) > 2]},
                       "source": "tweets, sentiment towards a named target (targeted SA); no split"}
    return out


EXCLUDED = [  # (dataset, reason): fail S1 or S2, not measured
    ("MASC", "S2: Positive / Negative only (no neutral)"),
    ("AJGT", "S2: Positive / Negative only"),
    ("ASTD, ArTwitter, QRCI (ar-embeddings copy)", "S2: binary labels in this copy"),
    ("Arabic 100k Reviews", "S1: labels from star ratings; classes Positive / Negative / Mixed"),
    ("LABR; ATT, HTL, MOV, PROD, RES", "S1: labels from star ratings (reviews)"),
    ("E_MSA_BDs (Bahraini)", "S1: labels from the original ratings, texts translated"),
    ("arabic-sentiment-analysis", "S1: labels from emojis (automatic)"),
    ("ALR", "S1/S2: aspect-level laptop review labels"),
    ("ASAD (`official_ASAD.csv`)", "S6: tweet IDs and labels only, no text (100,000 tweets: Neutral 69,369 / "
                                   "Positive 15,282 / Negative 15,349); the texts would need hydrating through the paid X API"),
]


def is_arabic(t: str) -> bool:
    """Quality row 8: Arabic script if >= 70% of the letters are Arabic."""
    a, l = len(ARABIC_RE.findall(t)), len(LATIN_RE.findall(t))
    return a > 0 and a >= 0.7 * (a + l)


def describe(rows: list[tuple[str, str]]) -> dict:
    """Form and label statistics of one split (texts already filtered)."""
    labs = Counter(LABELS.get(l.strip().lower(), "other") for _, l in rows)
    n = max(1, len(rows))
    return {"n": len(rows), **{f"share_{c}": labs[c] / n for c in ("NEG", "NEU", "POS")},
            "share_other_label": labs["other"] / n,
            "links": sum(bool(LINK_RE.search(t)) for t, _ in rows) / n,
            "mentions": sum(bool(MENTION_RE.search(t)) for t, _ in rows) / n,
            "hashtags": sum("#" in t for t, _ in rows) / n,
            "words": statistics.fmean(len(t.split()) for t, _ in rows) if rows else 0.0}


def main() -> None:
    """Measure every candidate, apply the standards, write the tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    table = []
    for name, d in candidates().items():
        allrows = [r for rs in d["splits"].values() for r in rs]
        arabic_share = sum(is_arabic(t) for t, _ in allrows) / len(allrows)
        splits = {s: describe([r for r in rs if is_arabic(r[0])]) for s, rs in d["splits"].items()}
        train = splits.get("train") or splits["all"]
        test = splits.get("test")
        row = {"dataset": name, "source": d["source"], "texts": len(allrows), "arabic_share": arabic_share,
               "official_split": "/".join(s for s in d["splits"] if s != "all") or "none",
               "train_n": train["n"], "test_n": test["n"] if test else None,
               "train_labels": f"{train['share_NEG']:.0%} / {train['share_NEU']:.0%} / {train['share_POS']:.0%}",
               "test_labels": f"{test['share_NEG']:.0%} / {test['share_NEU']:.0%} / {test['share_POS']:.0%}" if test else "–"}
        if test:
            row["max_label_gap"] = max(abs(train[f"share_{c}"] - test[f"share_{c}"]) for c in ("NEG", "NEU", "POS"))
            row["link_gap"] = abs(train["links"] - test["links"])
            row["mention_gap"] = abs(train["mentions"] - test["mentions"])
            row["hashtag_gap"] = abs(train["hashtags"] - test["hashtags"])
            row["length_ratio"] = max(train["words"], test["words"]) / max(1e-9, min(train["words"], test["words"]))
        row["train_links"], row["test_links"] = train["links"], test["links"] if test else None
        # The standards (S1 and S2 hold for every measured candidate; S6: texts are in every download).
        s4 = bool(test) and row["max_label_gap"] <= 0.05 and max(row["link_gap"], row["mention_gap"], row["hashtag_gap"]) <= 0.05 \
            and row["length_ratio"] <= 1.25
        s5 = train["n"] >= 1000 and bool(test) and test["n"] >= 500 and min(train[f"share_{c}"] for c in ("NEG", "NEU", "POS")) >= 0.05
        s3 = arabic_share >= 0.7 or (s4 and s5)
        row.update(S3=s3, S4=s4 if test else "no official split", S5=s5, passes=s3 and s4 is True and s5)
        table.append(row)

    cols = ["dataset", "source", "texts", "arabic_share", "official_split", "train_n", "test_n", "train_labels", "test_labels",
            "max_label_gap", "link_gap", "mention_gap", "hashtag_gap", "length_ratio", "train_links", "test_links",
            "S3", "S4", "S5", "passes"]
    out = Path("docs/sentiment/tables")
    with open(out / "dataset_survey.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(table)
    pct = lambda v: "–" if v is None else f"{v:.0%}"
    yes = lambda v: "yes" if v is True else ("no" if v is False else v)
    ratio = lambda v: "–" if v is None else f"{v:.2f}"
    md = ["# Arabic sentiment datasets against the dataset standards", "",
          "Generated by `python -m src.sentiment.dataset_survey`. Do not edit by hand. Standards S1–S6 in "
          "`docs/sentiment/chron.md` (2026-10-31). All split statistics after keeping only Arabic-script texts "
          "(S3 rule). Labels NEG / NEU / POS. Gaps = absolute difference between train and test.", "",
          "| Dataset | Texts | Arabic script | Official split | Train / test (Arabic) | Train labels | Test labels | Max label gap | Links train / test | Mention gap | Hashtag gap | Length ratio | S3 | S4 | S5 | Passes |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in table:
        md.append(f"| {r['dataset']} | {r['texts']:,} | {pct(r['arabic_share'])} | {r['official_split']} | {r['train_n']:,} / "
                  f"{r['test_n'] if r['test_n'] is not None else '–'} | {r['train_labels']} | {r['test_labels']} | "
                  f"{pct(r.get('max_label_gap'))} | {pct(r['train_links'])} / {pct(r['test_links'])} | {pct(r.get('mention_gap'))} | "
                  f"{pct(r.get('hashtag_gap'))} | {ratio(r.get('length_ratio'))} | "
                  f"{yes(r['S3'])} | {yes(r['S4'])} | {yes(r['S5'])} | **{yes(r['passes'])}** |")
    md += ["", "Not measured (fail S1 or S2):", ""] + [f"- **{n}:** {why}" for n, why in EXCLUDED]
    (out / "dataset_survey.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[4:]))


if __name__ == "__main__":
    sys.exit(main())
