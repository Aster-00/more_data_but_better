"""Stage 0 of the compositional pipeline: measurement of the real EESA data. No model is run.

  script bins     Latin share per text by three methods (src.sentiment.compositional.script_ratio) and the
                  check that the existing rule reproduces the script-mix table of chron-EESA
  per bin         English vs Franco share of the Latin tokens (heuristic), class mix, and the baseline
                  macro F1 and micro F1 from saved predictions (bins from 75% Latin merged)
  compound slice  texts with a connective of the lexicon, and the baseline on that slice vs the rest
  review files    a sample of tagged Latin tokens and of matched compound texts for manual checking
                  (train split only; written under data/, which is not in git)

Outputs: <out_dir>/stage0.json, stage0_report.md (numbers only, no text), stage0_rows.jsonl (one row
per text, no text); <inspect_dir>/stage0_token_sample.csv, stage0_compound_sample.csv.

Usage:
  python -m src.sentiment.compositional.stage0_measure --config configs/sentiment/compositional/stage0.json
  python -m src.sentiment.compositional.stage0_measure --config ... --limit 200     # tiny mode, no baseline
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import re
import statistics
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

from sklearn.metrics import f1_score

from src.data.build_dataset import git_commit, sha256
from src.sentiment.compositional.lexicon import LatinTagger, find_connectives, load_connectives, words
from src.sentiment.compositional.script_ratio import BIN_LABELS, METHODS, latin_bin, merged_bin_label, script_counts

TAGS = ["english", "franco", "unknown", "other"]


def read_jsonl(path: Path) -> list[dict]:
    """All records of a JSONL file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def pct(x: float) -> str:
    """Percentage with one decimal."""
    return f"{100 * x:.1f}%"


def mean_sd(xs: list[float]) -> str:
    """Mean ± standard deviation over seeds, as percentages."""
    if not xs:
        return "–"
    return f"{100 * statistics.fmean(xs):.1f} ± {100 * (statistics.stdev(xs) if len(xs) > 1 else 0):.1f}"


def scores(gold: list[str], pred: list[str]) -> tuple[float, float]:
    """(macro F1 over the classes present in gold, micro F1 = accuracy)."""
    present = sorted(set(gold))
    macro = f1_score(gold, pred, labels=present, average="macro", zero_division=0)
    return macro, sum(g == p for g, p in zip(gold, pred)) / len(gold)


# ---------------------------------------------------------------- per-text measurement

def measure(records: list[dict], cfg: dict, entries: list[dict], tagger: LatinTagger) -> list[dict]:
    """One row per text: counts and bin per method, Latin-token tags, connectives found."""
    rows = []
    for r in records:
        text = r.get(cfg["text_field"], r["text"])
        row = {"text_id": r["text_id"], "split": r["split"], "sentiment": r["sentiment"]}
        for m in METHODS:
            ar, lat = script_counts(text, m, cfg["ratio"]["strict_arabic_letters"])
            row[m] = {"arabic": ar, "latin": lat, "ratio": lat / (ar + lat) if ar + lat else None, "bin": latin_bin(ar, lat)}
        # Bin with Arabic letters only (no Arabic punctuation or digits), to see what that choice changes.
        row["bin_strict_arabic"] = latin_bin(*script_counts(text, cfg["ratio"]["analysis_method"], True))
        tags = tagger.tag_text(text)
        row["latin_tags"] = dict(Counter(g for _, g in tags))
        toks = words(text, cfg["connective_strip_diacritics"])
        row["n_words"] = len(toks)
        row["connectives"] = find_connectives(toks, entries, cfg["connective_min_side_words"])
        row["_tags"], row["_text"] = tags, text       # dropped before writing
        rows.append(row)
    return rows


# ---------------------------------------------------------------- tables

def bin_counts(rows: list[dict], method: str) -> list[int]:
    """Texts per bin 0..10 for one method."""
    c = Counter(r[method]["bin"] for r in rows)
    return [c[b] for b in range(11)]


GROUPS = ["five_patterns", "other_subordinator", "neither"]


def group_of(r: dict, cfg: dict) -> str:
    """Sentence group of a text: a connective of the five patterns, else another subordinator, else neither."""
    pats = {c["pattern"] for c in r["connectives"]}
    if pats & set(cfg["compositional_patterns"]):
        return "five_patterns"
    return "other_subordinator" if pats else "neither"


def length_band(n_words: int, edges: list[int]) -> str:
    """Length band of a text from its word count, e.g. '1-9', '10-19', '20+'."""
    lo = 1
    for e in edges:
        if n_words < e:
            return f"{lo}-{e - 1}"
        lo = e
    return f"{lo}+"


def baseline_runs(base: dict, cfg: dict) -> list[Path]:
    """Run folders of one baseline entry (a regular expression, or a prefix with seeds)."""
    root = Path(cfg["runs_dir"])
    if "run_regex" in base:
        return sorted(d for d in root.iterdir() if re.fullmatch(base["run_regex"], d.name))
    return [root / f"{base['run_prefix']}_seed{seed}" for seed in base["seeds"]]


def baseline_tables(rows_by_split: dict, cfg: dict, method: str) -> dict:
    """Per baseline and split: scores and errors per slice (bin, sentence group, pattern, length band)."""
    out = {}
    merge = cfg["merge_bins_from"]
    contrastive = set(cfg["contrastive_patterns"])
    for base in cfg["baselines"]:
        runs = baseline_runs(base, cfg)
        res = {"n_runs": len(runs)}
        for split in cfg["eval_splits"]:
            rows = rows_by_split[split]
            # Slices: index lists into the split (predictions are in file order).
            slices: dict[str, list[int]] = defaultdict(list)
            for i, r in enumerate(rows):
                slices["all"].append(i)
                if r[method]["bin"] is not None:
                    slices["bin:" + merged_bin_label(r[method]["bin"], merge)].append(i)
                g = group_of(r, cfg)
                pats = {c["pattern"] for c in r["connectives"]}
                slices["group:" + g].append(i)
                slices[f"len:{length_band(r['n_words'], cfg['length_bands'])}|{g}"].append(i)
                if pats & contrastive:
                    slices["compound_contrastive"].append(i)
                for pat in pats:
                    slices["pattern:" + pat].append(i)
            # Scores per run, and how many runs get each text wrong.
            per_run: dict[str, list[tuple[float, float]]] = defaultdict(list)
            wrong = [0] * len(rows)
            for d in runs:
                preds = read_jsonl(d / f"{split}_predictions.jsonl")
                assert [x["text_id"] for x in preds] == [r["text_id"] for r in rows], d
                for i, x in enumerate(preds):
                    wrong[i] += x["pred"] != x["gold"]
                for name, idx in slices.items():
                    per_run[name].append(scores([preds[i]["gold"] for i in idx], [preds[i]["pred"] for i in idx]))
            res[split] = {name: {"n": len(slices[name]), "macro_f1": [v[0] for v in vals], "micro_f1": [v[1] for v in vals],
                                 "errors": sum(wrong[i] for i in slices[name]),
                                 "wrong_in_majority": sum(wrong[i] > len(runs) / 2 for i in slices[name])}
                          for name, vals in per_run.items()}
        out[base["name"]] = res
    return out


def write_samples(rows: list[dict], cfg: dict, rng: random.Random) -> dict:
    """CSV samples for manual checking: tagged Latin tokens and matched compound texts (one split only)."""
    split = cfg["review_samples"]["split"]
    rows = [r for r in rows if r["split"] == split]
    out_dir = Path(cfg["inspect_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)

    # Latin tokens: the same number per tag where possible.
    by_tag = defaultdict(list)
    for r in rows:
        for tok, tag in r["_tags"]:
            by_tag[tag].append((r, tok))
    per_tag = cfg["review_samples"]["tokens"] // 3
    picked = []
    for tag in ("english", "franco", "unknown"):
        picked += [(tag, r, tok) for r, tok in rng.sample(by_tag[tag], min(per_tag, len(by_tag[tag])))]
    tok_path = out_dir / "stage0_token_sample.csv"
    with open(tok_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["text_id", "token", "tag", "text", "tag_correct (y/n)", "right_tag"])
        for tag, r, tok in picked:
            w.writerow([r["text_id"], tok, tag, " ".join(r["_text"].split()), "", ""])

    # Compound texts: the same number per pattern where possible.
    by_pat = defaultdict(list)
    for r in rows:
        for c in r["connectives"]:
            by_pat[c["pattern"]].append((r, c))
    per_pat = cfg["review_samples"]["compound_texts"] // max(1, len(by_pat))
    comp_path = out_dir / "stage0_compound_sample.csv"
    n_comp = 0
    with open(comp_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["text_id", "sentiment", "pattern", "connective_id", "text", "is_compound (y/n)", "pattern_correct (y/n)"])
        for pat in sorted(by_pat):
            for r, c in rng.sample(by_pat[pat], min(per_pat, len(by_pat[pat]))):
                w.writerow([r["text_id"], r["sentiment"], pat, c["id"], " ".join(r["_text"].split()), "", ""])
                n_comp += 1
    return {"token_sample": str(tok_path), "n_tokens": len(picked), "compound_sample": str(comp_path), "n_compound": n_comp}


# ---------------------------------------------------------------- report

def report_md(res: dict, cfg: dict) -> str:
    """The Stage 0 report (numbers only)."""
    L: list[str] = []
    method = cfg["ratio"]["analysis_method"]
    n = res["n_texts"]
    L += ["# Stage 0: script mix, compound sentences and the MARBERTv2 baseline on real EESA", "",
          f"Generated by `src.sentiment.compositional.stage0_measure` ({res['finished']}, commit `{res['git_commit']}`). "
          f"Texts: {n} (train {res['n_split']['train']}, dev {res['n_split']['dev']}, test {res['n_split']['test']}). No model was run; "
          "baseline scores come from saved predictions.", ""]

    # 1. Reproduction.
    rep = res["reproduction"]
    L += ["## 1. Does `latin_ratio` reproduce the script-mix table?", "",
          "`char_letters` is the existing rule (letters only). `char_franco_digits` also counts digits inside Latin words. "
          "`token` counts tokens instead of letters.", "",
          "| bin | Latin % | target | char_letters | diff | char_franco_digits | diff | token | diff |", "|---|---|---|---|---|---|---|---|---|"]
    for b in range(11):
        t = rep["target"][b]
        cells = " | ".join(f"{rep[m][b]} | {rep[m][b] - t:+d}" for m in METHODS)
        L.append(f"| b{b} | {BIN_LABELS[b]} | {t} | {cells} |")
    L += ["", f"- Tolerance: {rep['tolerance']} texts per bin."]
    for m in METHODS:
        L.append(f"- `{m}`: largest difference {rep['max_diff'][m]} texts; {'reproduces' if rep['ok'][m] else 'does NOT reproduce'} the table; "
                 f"{rep['moved'][m]} texts ({pct(rep['moved'][m] / n)}) are in a different bin than under `char_letters`.")
    L += [f"- Texts without any Arabic or Latin letter: {rep['no_letters']}.",
          f"- Counting only true Arabic letters (no Arabic punctuation or digits) would move {rep['moved_strict_arabic']} texts "
          f"({pct(rep['moved_strict_arabic'] / n)}) to another bin. Not applied.",
          f"- Bins used in the rest of this report: `{method}`.", ""]

    # 2. Per bin: class mix and Latin-token language.
    L += ["## 2. Per bin: classes and the language of the Latin tokens", "",
          "All splits. English / Franco / unknown / other are shares of the Latin tokens in the bin (heuristic; "
          "precision still to be checked on the review sample).", "",
          "| bin | Latin % | texts | NEG | NEU | POS | Latin tokens | English | Franco | unknown | other |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for row in res["per_bin"]:
        nt = row["n"]
        cls = " | ".join(pct(row["classes"][c] / nt) if nt else "–" for c in cfg["classes"])
        lt = sum(row["latin_tags"].values())
        tg = " | ".join(pct(row["latin_tags"].get(t, 0) / lt) if lt else "–" for t in TAGS)
        L.append(f"| b{row['bin']} | {BIN_LABELS[row['bin']]} | {nt} | {cls} | {lt} | {tg} |")
    tot = res["latin_tags_total"]
    lt = sum(tot.values())
    L += ["", f"- All Latin tokens ({lt}): " + ", ".join(f"{t} {pct(tot.get(t, 0) / lt)}" for t in TAGS) + ".",
          f"- Texts with at least one Franco-tagged token: {res['texts_with_franco']} ({pct(res['texts_with_franco'] / n)}).", ""]

    # 3. Baseline per bin.
    L += ["## 3. MARBERTv2 baseline per bin", "",
          f"Mean ± standard deviation over the runs, in %. Bins from {BIN_LABELS[cfg['merge_bins_from']].split('-')[0]}% Latin are merged. "
          "Macro F1 is over the classes present in the slice. Micro F1 equals accuracy.", ""]
    for base, full in res["baseline"].items():
        by_split = {k: v for k, v in full.items() if k != "n_runs"}
        L += [f"**{base}** ({full['n_runs']} runs)", "", "| Latin % | " + " | ".join(f"{s} n | {s} macro F1 | {s} micro F1" for s in by_split) + " |",
              "|---|" + "---|---|---|" * len(by_split)]
        names = ["all"] + [k for k in dict.fromkeys(merged_bin_label(b, cfg["merge_bins_from"]) for b in range(11))]
        for name in names:
            key = name if name == "all" else "bin:" + name
            cells = []
            for s in by_split:
                d = by_split[s].get(key)
                cells.append(f"{d['n']} | {mean_sd(d['macro_f1'])} | {mean_sd(d['micro_f1'])}" if d else "0 | – | –")
            L.append(f"| {name} | " + " | ".join(cells) + " |")
        L.append("")

    # 4. Sentence groups.
    comp = res["compound"]
    L += ["## 4. Compound and complex sentences (texts with a lexicon connective)", "",
          "Three groups, by word match on the unreviewed lexicon:", "",
          "- `five_patterns`: a connective of contrast, concession, expectation violation, counterfactual or reinforcement "
          "(the sentences the pipeline builds).",
          "- `other_subordinator`: none of those, but a reason, time, condition or relative-clause word (عشان, لما, لو, اللي, because, if).",
          "- `neither`: the rest.", "",
          "Counts are an upper bound (for example بس also means \"only\"), and sentences joined only with و are missed.", "",
          "| slice | all | train | dev | test |", "|---|---|---|---|---|"]
    for name, d in comp["counts"].items():
        L.append(f"| {name} | {d['all']} ({pct(d['all'] / n)}) | {d['train']} | {d['dev']} | {d['test']} |")
    L += ["", "By script of the connective (texts, all splits): " + ", ".join(f"{k} {v}" for k, v in comp["by_script"].items()) + ".", "",
          "Most frequent connectives (texts, all splits): " + ", ".join(f"`{k}` {v}" for k, v in comp["top"]) + ".", "",
          f"Lexicon entries never found: {comp['never_found']} of {comp['n_entries']}.", "",
          "Class mix and length (all splits):", "", "| slice | texts | NEG | NEU | POS | mean words |", "|---|---|---|---|---|---|"]
    for name, d in comp["classes"].items():
        nt = sum(d.values())
        L.append(f"| {name} | {nt} | " + " | ".join(pct(d.get(c, 0) / nt) if nt else "–" for c in cfg["classes"]) + f" | {comp['mean_words'][name]:.1f} |")
    L.append("")

    # 4b. Share of all errors per group, and the same per length band.
    L += ["### Share of the errors", "",
          "Errors are summed over the runs. `share of errors` is the group's part of all errors in the split; compare it with `share of texts`. "
          "`wrong in majority` = texts that more than half of the runs get wrong.", ""]
    for base, full in res["baseline"].items():
        L += [f"**{base}** ({full['n_runs']} runs)", "",
              "| split | group | texts | share of texts | error rate | share of errors | wrong in majority | share of those |", "|---|---|---|---|---|---|---|---|"]
        for split in cfg["eval_splits"]:
            d_all = full[split]["all"]
            for g in GROUPS:
                d = full[split].get("group:" + g)
                if not d:
                    continue
                L.append(f"| {split} | {g} | {d['n']} | {pct(d['n'] / d_all['n'])} | {pct(d['errors'] / (d['n'] * full['n_runs']))} | "
                         f"{pct(d['errors'] / d_all['errors'])} | {d['wrong_in_majority']} | {pct(d['wrong_in_majority'] / d_all['wrong_in_majority'])} |")
        L.append("")
    L += ["### Error rate by length", "",
          "Texts in the two connective groups are longer. Error rate per group inside each length band (words), with the number of texts in brackets.", ""]
    bands = [length_band(x, cfg["length_bands"]) for x in [1] + cfg["length_bands"]]
    for base, full in res["baseline"].items():
        L += [f"**{base}**", "", "| split | group | " + " | ".join(f"{b} words" for b in bands) + " |", "|---|---|" + "---|" * len(bands)]
        for split in cfg["eval_splits"]:
            for g in GROUPS:
                cells = []
                for b in bands:
                    d = full[split].get(f"len:{b}|{g}")
                    cells.append(f"{pct(d['errors'] / (d['n'] * full['n_runs']))} ({d['n']})" if d else "– (0)")
                L.append(f"| {split} | {g} | " + " | ".join(cells) + " |")
        L.append("")

    # 4c. Scores per group and pattern.
    L += ["### Scores per group and pattern", ""]
    for base, full in res["baseline"].items():
        by_split = {k: v for k, v in full.items() if k != "n_runs"}
        L += [f"**{base}**", "", "| slice | " + " | ".join(f"{s} n | {s} macro F1 | {s} micro F1" for s in by_split) + " |",
              "|---|" + "---|---|---|" * len(by_split)]
        keys = ["group:" + g for g in GROUPS] + ["compound_contrastive"] + sorted({k for v in by_split.values() for k in v if k.startswith("pattern:")})
        for key in keys:
            cells = []
            for s in by_split:
                d = by_split[s].get(key)
                cells.append(f"{d['n']} | {mean_sd(d['macro_f1'])} | {mean_sd(d['micro_f1'])}" if d else "0 | – | –")
            L.append(f"| {key.replace('group:', '')} | " + " | ".join(cells) + " |")
        L.append("")

    # 5. Review files.
    s = res["samples"]
    L += ["## 5. Files for manual review", "",
          f"- `{cfg['connectives']}`: {comp['n_entries']} connectives, all `reviewed: false`.",
          f"- `{cfg['franco_lexicon']}`: Franco word list, `reviewed: false`.",
          f"- `{s['token_sample']}`: {s['n_tokens']} Latin tokens with their tag ({cfg['review_samples']['split']} split). Fill `tag_correct`.",
          f"- `{s['compound_sample']}`: {s['n_compound']} matched texts ({cfg['review_samples']['split']} split). Fill `is_compound` and `pattern_correct`.",
          "", "## Limits", "",
          "- The English-vs-Franco tag and the compound match are heuristics; their precision is unknown until the samples are checked.",
          "- Per-bin scores above 55% Latin rest on few test texts.",
          "- The test split is only scored here. Design choices (flattening strength, thresholds) should use the dev columns.", ""]
    return "\n".join(L)


# ---------------------------------------------------------------- main

def main() -> None:
    """Measure every split, write the JSON, the report, the per-text rows and the review samples."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N texts per split, no baseline, outputs get a .limitN suffix")
    args = p.parse_args()
    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    rng = random.Random(cfg["seed"])
    method = cfg["ratio"]["analysis_method"]

    # Load the lexicons and the data.
    entries = load_connectives(Path(cfg["connectives"]))
    tagger = LatinTagger(Path(cfg["english_wordlist"]), Path(cfg["franco_lexicon"]))
    rows_by_split = {}
    for split, path in cfg["splits"].items():
        rows_by_split[split] = measure(read_jsonl(Path(path))[:args.limit], cfg, entries, tagger)
    rows = [r for s in rows_by_split.values() for r in s]
    n = len(rows)

    # 1. Reproduction of the chron-EESA table (over all splits).
    target, tol = cfg["target_bins"]["counts"], cfg["target_bins"]["tolerance"]
    rep = {"target": target, "tolerance": tol, "max_diff": {}, "ok": {}, "moved": {}}
    for m in METHODS:
        rep[m] = bin_counts(rows, m)
        rep["max_diff"][m] = max(abs(a - b) for a, b in zip(rep[m], target))
        rep["ok"][m] = rep["max_diff"][m] <= tol
        rep["moved"][m] = sum(r[m]["bin"] != r["char_letters"]["bin"] for r in rows)
    rep["no_letters"] = sum(r["char_letters"]["bin"] is None for r in rows)
    rep["moved_strict_arabic"] = sum(r["bin_strict_arabic"] != r[method]["bin"] for r in rows)

    # 2. Per bin: classes and Latin-token tags.
    per_bin, total_tags = [], Counter()
    for b in range(11):
        sel = [r for r in rows if r[method]["bin"] == b]
        tags = Counter()
        for r in sel:
            tags.update(r["latin_tags"])
        total_tags.update(tags)
        per_bin.append({"bin": b, "n": len(sel), "classes": dict(Counter(r["sentiment"] for r in sel)) | {c: sum(r["sentiment"] == c for r in sel) for c in cfg["classes"]},
                        "latin_tags": dict(tags)})

    # 4. Sentence group and pattern counts.
    contrastive = set(cfg["contrastive_patterns"])
    def in_slice(r: dict, name: str) -> bool:
        pats = {c["pattern"] for c in r["connectives"]}
        if name in GROUPS:
            return group_of(r, cfg) == name
        if name == "compound_contrastive":
            return bool(pats & contrastive)
        return name in pats
    patterns = list(dict.fromkeys(e["pattern"] for e in entries))
    counts, classes, mean_words = {}, {}, {}
    for name in GROUPS + ["compound_contrastive"] + patterns:
        sel = [r for r in rows if in_slice(r, name)]
        counts[name] = {"all": len(sel), **{s: sum(r["split"] == s for r in sel) for s in cfg["splits"]}}
        classes[name] = dict(Counter(r["sentiment"] for r in sel))
        mean_words[name] = statistics.fmean(r["n_words"] for r in sel) if sel else 0.0
    hits = Counter(c["id"] for r in rows for c in r["connectives"])
    text_of = {e["id"]: e["text"] for e in entries}
    by_script = Counter(s for r in rows for s in {c["script"] for c in r["connectives"]})
    compound = {"counts": counts, "classes": classes, "mean_words": mean_words, "by_script": dict(by_script), "n_entries": len(entries),
                "top": [(f"{text_of[k]} ({k})", v) for k, v in hits.most_common(15)],
                "never_found": sum(e["id"] not in hits for e in entries), "per_connective": dict(hits)}

    res = {"config": str(args.config), "git_commit": git_commit(), "finished": time.strftime("%Y-%m-%d %H:%M"),
           "seed": cfg["seed"], "limit": args.limit, "n_texts": n, "n_split": {s: len(v) for s, v in rows_by_split.items()},
           "data_sha256": {s: sha256(Path(pth)) for s, pth in cfg["splits"].items()},
           "lexicon_sha256": {k: sha256(Path(cfg[k])) for k in ("connectives", "franco_lexicon", "english_wordlist")},
           "reproduction": rep, "per_bin": per_bin, "latin_tags_total": dict(total_tags),
           "texts_with_franco": sum(r["latin_tags"].get("franco", 0) > 0 for r in rows), "compound": compound,
           # 3. Baseline from saved predictions (skipped in tiny mode: predictions cover the whole split).
           "baseline": {} if args.limit else baseline_tables(rows_by_split, cfg, method),
           "samples": write_samples(rows, cfg, rng) if not args.limit else {"token_sample": "-", "n_tokens": 0, "compound_sample": "-", "n_compound": 0}}

    # Write the outputs.
    out_dir = Path(cfg["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    suffix = f".limit{args.limit}" if args.limit else ""
    with open(out_dir / f"stage0_rows{suffix}.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps({k: v for k, v in r.items() if not k.startswith("_")}, ensure_ascii=False) + "\n")
    (out_dir / f"stage0{suffix}.json").write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / f"stage0_report{suffix}.md").write_text(report_md(res, cfg), encoding="utf-8")
    print(f"{n} texts; reproduction ok: {rep['ok']}; report {out_dir / f'stage0_report{suffix}.md'}")


if __name__ == "__main__":
    sys.exit(main())
