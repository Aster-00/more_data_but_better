"""SG04 / SR07 analysis: comparisons with earlier runs and where the test errors change (D-023).

Post-hoc, on finished runs only; SR07 is test-contaminated (the SG04 types came from the SR02
test errors), so every number here is leakage analysis, not an unbiased result.

Tables (macro F1 and F1-PN from docs/sentiment/tables/sentiment_summary_ar_sarcv2.csv; the rest from the runs'
test_predictions.jsonl; BERTs only, seeds 42/43/44):
  1. performance     SR07 per BERT x generator, mean +- std over seeds
  2. deltas          SR07 - SR01 / SR05 / SR06 per BERT x generator, and a summary over the 21
                     cells with a two-sided sign test (SR01 has one value per BERT, so its cells
                     are not independent)
  3. subsets         error rate on the 917 hard cases, the other test tweets and each type's
                     candidate list (data/inspect/hard_cases/; candidates are rough keyword rules):
                     mean over seeds per BERT x generator cell, then over cells
  4. label shares    share of each predicted label, all runs pooled, with the gold shares
  5. error types     gold -> predicted shares on the non-hard test tweets, mean over runs
  6. groups          error rate by gold label, by sarcasm, and by gold label inside the hard cases
  7. flips           per tweet, majority label over a condition's runs: SR01 -> SR07 fixed / broken
  8. flips by run    the same for SR05 / SR06 / SR07 by error type, with a noise reference: two halves
                     of the SR01 runs (fewer runs per side, so it overstates the noise somewhat)
  9. religious       error rate of test tweets with the rough `religious` cue of src.sentiment.hard_cases,
                     by gold label, and the cue's label counts in S1 train, test and the SG04 sets
Conditions: SR01 (real only), SR05 (+ SG03), SR06 (+ SG03-random), SR07 (+ SG04).

Outputs: docs/sentiment/tables/sg04_analysis.md, results/sentiment/analysis/sg04_analysis.json,
data/inspect/hard_cases/sr07_broken_tweets.csv (the tweets broken from SR01 to SR07, for reading).

Usage:
  python -m src.sentiment.sg04_analysis
"""
from __future__ import annotations

import csv
import json
import re
import statistics
import sys
from collections import Counter
from math import comb
from pathlib import Path

from src.sentiment.hard_cases import CUES

TEST = Path("data/processed/sentiment/arsarcasm_v2_test.jsonl")
RUNS_DIR = Path("results/sentiment/runs")
SUMMARY = Path("docs/sentiment/tables/sentiment_summary_ar_sarcv2.csv")
HARD = Path("data/inspect/hard_cases/sr02_test_hard_cases.csv")
CANDIDATES = Path("data/inspect/hard_cases/sg04_type_candidates.csv")
BERTS = [("marbertv2", "MARBERTv2"), ("marbert", "MARBERT"), ("arabertv02_twitter", "AraBERTv02-Tw"),
         ("camelbert_mix", "CAMeLBERT-mix"), ("camelbert_da", "CAMeLBERT-DA"), ("arbert", "ARBERT"),
         ("arbertv2", "ARBERTv2")]
GENS = [("fanar", "Fanar"), ("qwen3", "Qwen3"), ("aya", "Aya")]
CONDITIONS = {"SR01": lambda b: [f"sr01_{b}"], "SR05": lambda b: [f"sr05_{b}_{g}" for g, _ in GENS],
              "SR06": lambda b: [f"sr06_{b}_{g}" for g, _ in GENS], "SR07": lambda b: [f"sr07_{b}_{g}" for g, _ in GENS]}
LABELS = ["NEG", "NEU", "POS"]
TYPE_NAMES = {"1": "sarcastic praise", "2": "dry jab", "3": "maxim / remark", "4": "prayer",
              "5": "spam hashtag (not generated)", "6": "emoji"}


def sign_p(xs: list[float]) -> float:
    """Two-sided sign test p-value (ties dropped)."""
    n, k = sum(x != 0 for x in xs), sum(x > 0 for x in xs)
    k = min(k, n - k)
    return min(1.0, 2 * sum(comb(n, i) for i in range(k + 1)) / 2 ** n)


def cell_predictions(cond: str) -> list[list[list[str]]]:
    """Per BERT x generator cell (SR01: per BERT), the test predictions of each finished seed."""
    cells = []
    for b, _ in BERTS:
        for pattern in CONDITIONS[cond](b):
            seeds = [[json.loads(l)["pred"] for l in open(d / "test_predictions.jsonl", encoding="utf-8")]
                     for d in sorted(RUNS_DIR.glob(pattern + "_seed*"))
                     # Smoke tests ("_limit<N>") are not results.
                     if re.fullmatch(r".*_seed\d+", d.name) and (d / "test_predictions.jsonl").exists()]
            if seeds:
                cells.append(seeds)
    return cells


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    """Markdown table lines."""
    return ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)] + ["| " + " | ".join(r) + " |" for r in rows]


def main() -> None:
    """Compute every table, write the markdown and JSON."""
    sys.stdout.reconfigure(encoding="utf-8")
    test = [json.loads(l) for l in open(TEST, encoding="utf-8")]
    gold = [r["sentiment"] for r in test]
    with open(HARD, encoding="utf-8-sig") as f:
        hard_ids = {r["text_id"] for r in csv.DictReader(f)}
    hard = [r["text_id"] in hard_ids for r in test]
    cand: dict[str, set[str]] = {}
    with open(CANDIDATES, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            cand.setdefault(r["n"].split(".")[0], set()).add(r["text_id"])
    with open(SUMMARY, encoding="utf-8") as f:
        summary = [r for r in csv.DictReader(f) if r["eval_corpus"] == r["train_corpus"]]
    # Macro F1 and the official F1-PN: (mean, std) per run folder and split.
    metrics = {name: {(r["folder"], r["split"]): (float(r[k]), float(r[f"{k}_std"])) for r in summary}
               for name, k in (("Macro F1", "macro_f1"), ("F1-PN", "f1_pn"))}
    preds = {c: cell_predictions(c) for c in CONDITIONS}
    out: dict = {}
    md = ["# SG04 / SR07 analysis (test-contaminated, D-023)", "",
          "Generated by `python -m src.sentiment.sg04_analysis`. Do not edit by hand. SR07 test scores are leakage "
          "analysis, not a result: the SG04 types came from the SR02 test errors. BERTs only, seeds 42/43/44.", ""]

    # 1. Performance per BERT x generator.
    cols = [(s, g, gn) for s in ("dev", "test") for g, gn in GENS]
    header = ["BERT"] + [f"{s.capitalize()} {gn}" for s, _, gn in cols]
    md += ["## 1. SR07 performance", "", "Mean ± std over seeds; columns = generator of the SG04 set. F1-PN = mean F1 of "
           "POS and NEG, the official ArSarcasm-v2 metric.", ""]
    for metric, f1 in metrics.items():
        rows, means = [], {c: [] for c in cols}
        for b, bn in BERTS:
            row = [bn]
            for c in cols:
                m, sd = f1[(f"sr07_{b}_{c[1]}", c[0])]
                means[c].append(m)
                row.append(f"{m:.2f} ± {sd:.2f}")
            rows.append(row)
        rows.append(["**Mean**"] + [f"**{statistics.fmean(means[c]):.2f}**" for c in cols])
        md += [f"**{metric}**", ""] + table(header, rows) + [""]

    # 2. Deltas against earlier runs, per cell and summarised.
    bases = {"SR01": lambda b, g: f"sr01_{b}", "SR05": lambda b, g: f"sr05_{b}_{g}", "SR06": lambda b, g: f"sr06_{b}_{g}"}
    labels = {"SR01": "real only", "SR05": "SG03", "SR06": "SG03-random"}
    md += ["## 2. Comparison with earlier runs", ""]
    summary_rows, out["deltas"] = [], {}
    for base, name in bases.items():
        cells = []
        for metric, f1 in metrics.items():
            ds = {c: [f1[(f"sr07_{b}_{c[1]}", c[0])][0] - f1[(name(b, c[1]), c[0])][0] for b, _ in BERTS] for c in cols}
            rows = [[bn] + [f"{ds[c][i]:+.2f}" for c in cols] for i, (_, bn) in enumerate(BERTS)]
            rows.append(["**Mean**"] + [f"**{statistics.fmean(ds[c]):+.2f}**" for c in cols])
            rows.append(["Better in"] + [f"{sum(x > 0 for x in ds[c])}/7" for c in cols])
            md += [f"**Δ SR07 − {base}, {metric}** (SG04 vs {labels[base]}; + = SG04 better)", ""] + table(header, rows) + [""]
            for s in ("dev", "test"):
                xs = [x for c in cols if c[0] == s for x in ds[c]]
                cells.append(f"{statistics.fmean(xs):+.2f} (better in {sum(x > 0 for x in xs)}/21, p = {sign_p(xs):.3f})")
                key = f"{base}_{s}" if metric == "Macro F1" else f"{base}_{s}_f1_pn"
                out["deltas"][key] = {"mean": statistics.fmean(xs), "better": sum(x > 0 for x in xs), "p": sign_p(xs)}
        summary_rows.append([f"SR07 − {base} ({labels[base]})"] + cells)
    md += ["**Summary over the 21 BERT × generator cells** (two-sided sign test; SR01 has one value per BERT, so "
           "its 21 cells are not independent)", ""] + table(["Comparison", "Dev macro F1", "Test macro F1", "Dev F1-PN", "Test F1-PN"], summary_rows) + [""]

    # 3. Error rate on test subsets: mean over seeds per cell, then over cells.
    def subset_error(cond: str, idx: list[int]) -> float:
        return statistics.fmean(statistics.fmean(sum(p[i] != gold[i] for i in idx) / len(idx) for p in seeds)
                                for seeds in preds[cond])
    subsets = {"Hard cases (SG04 built from these)": [i for i in range(len(test)) if hard[i]],
               "Other test tweets": [i for i in range(len(test)) if not hard[i]]}
    for k, ids in sorted(cand.items()):
        subsets[f"Type {k} candidates: {TYPE_NAMES.get(k, k)}"] = [i for i, r in enumerate(test) if r["text_id"] in ids]
    conds = ["SR01", "SR05", "SR07"]
    rows, out["subsets"] = [], {}
    for name, idx in subsets.items():
        e = {c: subset_error(c, idx) for c in conds}
        out["subsets"][name] = {"n": len(idx)} | e
        rows.append([name, f"{len(idx):,}"] + [f"{100 * e[c]:.1f}%" for c in conds] + [f"{100 * (e['SR07'] - e['SR01']):+.1f}"])
    md += ["## 3. Error rate: hard cases or not", "",
           "Share of the subset's test tweets a run gets wrong; mean over seeds per BERT × generator cell, then over "
           "cells (SR01: 7 cells, others: 21). Lower is better; the last column is in percentage points.", ""]
    md += table(["Test subset", "Tweets", "SR01 real", "SR05 + SG03", "SR07 + SG04", "SR07 − SR01"], rows) + [""]

    # 4. Predicted label shares, all runs pooled.
    rows, out["label_shares"] = [["Gold"] + [f"{100 * gold.count(l) / len(gold):.1f}%" for l in LABELS]], {}
    for c in conds:
        cnt = Counter(x for seeds in preds[c] for p in seeds for x in p)
        n = sum(cnt.values())
        out["label_shares"][c] = {l: cnt[l] / n for l in LABELS}
        rows.append([c] + [f"{100 * cnt[l] / n:.1f}%" for l in LABELS])
    md += ["## 4. Predicted label shares on test", "", "All runs pooled.", ""] + table(["", *LABELS], rows) + [""]

    # 5. Error types on the non-hard tweets.
    other = subsets["Other test tweets"]
    kinds = [(g, p) for g in LABELS for p in LABELS if g != p]
    share = {c: {k: statistics.fmean(sum(gold[i] == k[0] and p[i] == k[1] for i in other) / len(other)
                                     for seeds in preds[c] for p in seeds) for k in kinds} for c in conds}
    rows = [[f"{g} → {p}"] + [f"{100 * share[c][(g, p)]:.2f}%" for c in conds]
            + [f"{100 * (share['SR07'][(g, p)] - share['SR01'][(g, p)]):+.2f}"] for g, p in kinds]
    out["error_types_other"] = {f"{g}->{p}": {c: share[c][(g, p)] for c in conds} for g, p in kinds}
    md += ["## 5. Error types on the other (non-hard) test tweets", "",
           f"Share of the {len(other):,} tweets with this gold → predicted error; mean over runs.", ""]
    md += table(["Error", *conds, "SR07 − SR01"], rows) + [""]

    # 6. Error rate by gold label and sarcasm.
    groups = {f"Gold {l}": [i for i in range(len(test)) if gold[i] == l] for l in LABELS}
    groups |= {"Sarcastic": [i for i, r in enumerate(test) if r["sarcasm"]],
               "Not sarcastic": [i for i, r in enumerate(test) if not r["sarcasm"]]}
    groups |= {f"Hard cases, gold {l}": [i for i in range(len(test)) if hard[i] and gold[i] == l] for l in LABELS}
    rows, out["groups"] = [], {}
    for name, idx in groups.items():
        e = {c: subset_error(c, idx) for c in conds}
        out["groups"][name] = {"n": len(idx)} | e
        rows.append([name, f"{len(idx):,}"] + [f"{100 * e[c]:.1f}%" for c in conds] + [f"{100 * (e['SR07'] - e['SR01']):+.1f}"])
    md += ["## 6. Error rate by gold label and sarcasm", "", "As table 3.", ""]
    md += table(["Group", "Tweets", *conds, "SR07 − SR01"], rows) + [""]

    # 7. Flips: majority label per tweet over all runs of a condition.
    def majority(cond: str) -> list[str]:
        runs = [p for seeds in preds[cond] for p in seeds]
        return [Counter(p[i] for p in runs).most_common(1)[0][0] for i in range(len(test))]
    m1, m7 = majority("SR01"), majority("SR07")
    fixed = [i for i in range(len(test)) if m1[i] != gold[i] and m7[i] == gold[i]]
    broken = [i for i in range(len(test)) if m1[i] == gold[i] and m7[i] != gold[i]]
    out["flips"] = {"fixed": len(fixed), "fixed_hard": sum(hard[i] for i in fixed), "broken": len(broken),
                    "broken_as": dict(Counter(f"{gold[i]}->{m7[i]}" for i in broken)),
                    "fixed_from": dict(Counter(f"{gold[i]} (was {m1[i]})" for i in fixed))}
    rows = [["Fixed (wrong in SR01, right in SR07)", str(len(fixed)), f"{sum(hard[i] for i in fixed)} hard cases"],
            ["Broken (right in SR01, wrong in SR07)", str(len(broken)), f"{sum(hard[i] for i in broken)} hard cases"],
            ["Net", f"{len(fixed) - len(broken):+d}", ""]]
    md += ["## 7. Tweets that flip from SR01 to SR07", "",
           "Per tweet, the majority label over all runs of a condition.", ""]
    md += table(["", "Tweets", "Of which"], rows) + [""]
    md += table(["Broken as (gold → SR07)", "Tweets"], [[k.replace("->", " → "), str(v)] for k, v in
                                                          Counter(f"{gold[i]}->{m7[i]}" for i in broken).most_common()]) + [""]

    # 8. Flips per condition, against the noise between two halves of the SR01 runs.
    def flips(a: list[str], b: list[str]) -> tuple[list[int], list[int]]:
        return ([i for i in range(len(test)) if a[i] != gold[i] and b[i] == gold[i]],
                [i for i in range(len(test)) if a[i] == gold[i] and b[i] != gold[i]])

    def vote(runs: list[list[str]]) -> list[str]:
        return [Counter(p[i] for p in runs).most_common(1)[0][0] for i in range(len(test))]
    sr01_runs = [p for seeds in preds["SR01"] for p in seeds]
    half = flips(vote(sr01_runs[0::2]), vote(sr01_runs[1::2]))
    rows = [["SR01 half vs half (noise)", str(len(half[0])), str(len(half[1])), str(len(half[0]) + len(half[1]))]
            + [str(sum(gold[i] == g and vote(sr01_runs[1::2])[i] == q for i in half[1])) for g, q in kinds]]
    out["flips_by_run"] = {"noise": {"fixed": len(half[0]), "broken": len(half[1])}}
    for c in ("SR05", "SR06", "SR07"):
        mc = vote([p for seeds in preds[c] for p in seeds])
        fx, br = flips(m1, mc)
        out["flips_by_run"][c] = {"fixed": len(fx), "broken": len(br)}
        rows.append([f"SR01 → {c}", str(len(fx)), str(len(br)), str(len(fx) + len(br))]
                    + [str(sum(gold[i] == g and mc[i] == q for i in br)) for g, q in kinds])
    md += ["## 8. Flips by run, with a noise reference", "",
           "Majority label per tweet. The noise row compares two halves of the SR01 runs; each half has few runs, so it "
           "overstates the noise somewhat. Error columns count broken tweets (gold → predicted).", ""]
    md += table(["Comparison", "Fixed", "Broken", "All flips"] + [f"{g} → {q}" for g, q in kinds], rows) + [""]

    # 9. Religious tweets: the prayer type teaches NEU, while POS is the common label of real ones.
    def religious(text: str) -> bool:
        return bool(re.search(CUES["religious"], text))
    rel = [i for i, r in enumerate(test) if religious(r["text"])]
    groups = {"All": rel} | {f"Gold {l}": [i for i in rel if gold[i] == l] for l in LABELS}
    all_conds = ["SR01", "SR05", "SR06", "SR07"]
    rows, out["religious"] = [], {}
    for name, idx in groups.items():
        e = {c: subset_error(c, idx) for c in all_conds}
        out["religious"][name] = {"n": len(idx)} | e
        rows.append([name, str(len(idx))] + [f"{100 * e[c]:.1f}%" for c in all_conds] + [f"{100 * (e['SR07'] - e['SR01']):+.1f}"])
    md += ["## 9. Test tweets with the religious cue", "", "Error rate as table 3; the cue is a rough keyword rule.", ""]
    md += table(["Group", "Tweets", *all_conds, "SR07 − SR01"], rows) + [""]
    rows = []
    sources = {"S1 train": Path("data/processed/sentiment/arsarcasm_v2_train.jsonl"), "S1 test": TEST}
    sources |= {f"SG04 {gn}": Path(f"data/synthetic/sentiment/sg04_{g}.selected.jsonl") for g, gn in GENS}
    for name, path in sources.items():
        with open(path, encoding="utf-8") as f:
            cnt = Counter(r["sentiment"] for r in map(json.loads, f) if religious(r["text"]))
        rows.append([name] + [str(cnt[l]) for l in LABELS])
    md += ["Texts with the cue, by label:", ""] + table(["Source", *LABELS], rows) + [""]

    # Broken tweets for reading; "all generators" = also broken by each generator's own majority.
    gen_votes = [vote([p for k, seeds in enumerate(preds["SR07"]) if k % len(GENS) == j for p in seeds]) for j in range(len(GENS))]
    with open("data/inspect/hard_cases/sr07_broken_tweets.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["error", "broken_by_all_generators", "hard_case", "sarcasm", "dialect", "religious_cue", "text_id", "text"])
        for i in sorted(broken, key=lambda i: (gold[i], m7[i])):
            w.writerow([f"{gold[i]} -> {m7[i]}", all(v[i] != gold[i] for v in gen_votes), hard[i], test[i]["sarcasm"],
                        test[i]["dialect"], religious(test[i]["text"]), test[i]["text_id"], test[i]["text"]])
    out["flips"]["broken_by_all_generators"] = sum(all(v[i] != gold[i] for v in gen_votes) for i in broken)

    Path("docs/sentiment/tables/sg04_analysis.md").write_text("\n".join(md), encoding="utf-8", newline="\n")
    Path("results/sentiment/analysis").mkdir(parents=True, exist_ok=True)
    Path("results/sentiment/analysis/sg04_analysis.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                                                     encoding="utf-8", newline="\n")
    print("wrote docs/sentiment/tables/sg04_analysis.md and results/sentiment/analysis/sg04_analysis.json")


if __name__ == "__main__":
    sys.exit(main())
