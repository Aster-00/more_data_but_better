"""EESA dev errors of the 8-epoch BERT runs (SR05-EESA, SR06-EESA, SR06-random-EESA; D-036).

Dev only (Ammar, 2026-11-15); test is not read. For every dev text: how many of the runs get it wrong.
Shared errors = texts wrong in a majority of the runs. Reported:
  per class        error rate of each gold class (mean over runs), errors by gold -> predicted class
  per script bin   Arabic share of the text's Arabic + Latin letters (links and mentions removed), in the
                   10-point bins of src.sentiment.explore_eesa; error rate and shared errors per bin
  per error type   the SG01-most-errors type of each shared error (D-034; "not in SG01-most-errors" if new),
                   with its script bins and classes
  per condition    the error rate of each run set; SR06-EESA is dev-contaminated (its few-shot examples
                   were SG01-most-errors dev texts), so it is shown apart and also left out of a clean count
Output: printed tables and results/quality/sentiment/eesa_dev_errors_8ep.json (no text).

--compare-3ep: the same dev analysis for the paired 3-epoch runs (same BERT, generator and seed; the only
change is the epoch count): SR05-EESA <-> SR03-EESA (sr01_eesa_tl / sr02_eesa_tl), SR06-EESA <-> SR04-EESA,
SR06-random-EESA <-> SR04-random-EESA. Output results/quality/sentiment/eesa_dev_errors_3v8ep.json.

Usage:
  python -m src.sentiment.dev_errors_eesa
  python -m src.sentiment.dev_errors_eesa --compare-3ep
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from src.quality.measure import ARABIC_LETTER_RE, LATIN_LETTER_RE, PLACEHOLDER_RE

RUNS = Path("results/sentiment/runs")
DEV = Path("data/processed/sentiment/eesa_dev.jsonl")
TYPES = Path("data/inspect/hard_cases/sg01_most_errors_eesa.jsonl")
OUT = Path("results/quality/sentiment/eesa_dev_errors_8ep.json")
CONDS = {"sr05": "SR05-EESA (real only, + SG01-EESA)", "sr06r": "SR06-random-EESA", "sr06": "SR06-EESA (dev-contaminated)"}
CLASSES = ["NEG", "NEU", "POS"]


def arabic_bin(text: str) -> int | None:
    """Bin b = Arabic share of Arabic + Latin letters in [10b-5, 10b+5) percent, as explore_eesa."""
    t = PLACEHOLDER_RE.sub(" ", text)
    ar, lat = len(ARABIC_LETTER_RE.findall(t)), len(LATIN_LETTER_RE.findall(t))
    return None if ar + lat == 0 else min(10, int(10 * ar / (ar + lat) + 0.5))


def bin_label(b: int) -> str:
    """Bin label as in the chron script-mix table (Arabic share)."""
    return f"{max(0, 10 * b - 5)}-{min(100, 10 * b + 5)}%"


def main() -> None:
    """Count wrong runs per dev text and print the tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    dev = [json.loads(l) for l in open(DEV, encoding="utf-8")]
    types = {r["text_id"]: r["error_type"] for r in map(json.loads, open(TYPES, encoding="utf-8"))}
    runs = sorted(d for d in RUNS.iterdir() if re.fullmatch(r"sr0(5|6|6r)_eesa_.+_seed4[234]", d.name))
    n_runs = Counter(d.name.split("_")[0] for d in runs)
    # wrong[i][(condition, predicted class)] = number of runs.
    wrong: dict[int, Counter] = defaultdict(Counter)
    for d in runs:
        cond = d.name.split("_")[0]
        for i, line in enumerate(open(d / "dev_predictions.jsonl", encoding="utf-8")):
            p = json.loads(line)
            assert p["text_id"] == dev[i]["text_id"], d
            if p["pred"] != p["gold"]:
                wrong[i][(cond, p["pred"])] += 1
    total = len(runs)
    n_wrong = [sum(wrong[i].values()) for i in range(len(dev))]
    rate = [n / total for n in n_wrong]
    shared = [i for i in range(len(dev)) if n_wrong[i] > total / 2]
    clean = sum(n_runs[c] for c in ("sr05", "sr06r"))
    n_clean = [sum(v for (c, _), v in wrong[i].items() if c in ("sr05", "sr06r")) for i in range(len(dev))]
    def top_pred(i: int) -> str:
        c = Counter()
        for (_, p), v in wrong[i].items():
            c[p] += v
        return c.most_common(1)[0][0]
    out = {"runs": dict(n_runs), "n_dev": len(dev), "never_wrong": sum(n == 0 for n in n_wrong),
           "shared_errors": len(shared), "wrong_in_90pct": sum(r >= 0.9 for r in rate),
           "wrong_in_all": sum(n == total for n in n_wrong),
           "shared_errors_without_sr06": sum(n > clean / 2 for n in n_clean)}
    print(f"{total} runs {dict(n_runs)}; dev {len(dev)}; never wrong {out['never_wrong']}; shared errors (majority) "
          f"{len(shared)}; wrong in >= 90% {out['wrong_in_90pct']}; in all {out['wrong_in_all']}; "
          f"shared without SR06-EESA {out['shared_errors_without_sr06']}")

    # Per class: error rate (mean over runs) and where the errors go.
    print("\n| Gold class | Dev texts | Error rate (mean of runs) | Of all errors | Predicted as NEG / NEU / POS | Shared errors |")
    print("|---|---|---|---|---|---|")
    all_err = sum(n_wrong)
    out["per_class"] = {}
    for c in CLASSES:
        idx = [i for i in range(len(dev)) if dev[i]["sentiment"] == c]
        to = Counter()
        for i in idx:
            for (_, p), v in wrong[i].items():
                to[p] += v
        err = sum(n_wrong[i] for i in idx)
        sh = sum(1 for i in shared if dev[i]["sentiment"] == c)
        out["per_class"][c] = {"n": len(idx), "error_rate": err / (len(idx) * total), "share_of_errors": err / all_err,
                               "to": {k: to[k] / err for k in CLASSES}, "shared": sh}
        print(f"| {c} | {len(idx)} | {err / (len(idx) * total):.1%} | {err / all_err:.1%} | "
              + " / ".join("–" if k == c else f"{to[k] / err:.0%}" for k in CLASSES) + f" | {sh} |")

    # Per condition and class.
    print("\n| Condition | Runs | Error rate | NEG | NEU | POS |")
    print("|---|---|---|---|---|---|")
    out["per_condition"] = {}
    for cond, name in CONDS.items():
        def r(sel: list[int]) -> float:
            return sum(sum(v for (cc, _), v in wrong[i].items() if cc == cond) for i in sel) / (len(sel) * n_runs[cond])
        cls = {c: r([i for i in range(len(dev)) if dev[i]["sentiment"] == c]) for c in CLASSES}
        out["per_condition"][cond] = {"error_rate": r(list(range(len(dev)))), **cls}
        print(f"| {name} | {n_runs[cond]} | {r(list(range(len(dev)))):.1%} | " + " | ".join(f"{cls[c]:.1%}" for c in CLASSES) + " |")

    # Per script bin.
    bins = [arabic_bin(d.get("text_raw", d["text"])) for d in dev]
    print("\n| Arabic share | Latin share | Dev texts | Error rate | Shared errors | Share of bin | NEG / NEU / POS (gold) |")
    print("|---|---|---|---|---|---|---|")
    out["per_script_bin"] = []
    for b in range(10, -1, -1):
        idx = [i for i in range(len(dev)) if bins[i] == b]
        if not idx:
            continue
        sh = [i for i in shared if bins[i] == b]
        g = Counter(dev[i]["sentiment"] for i in idx)
        er = sum(n_wrong[i] for i in idx) / (len(idx) * total)
        out["per_script_bin"].append({"arabic": bin_label(b), "n": len(idx), "error_rate": er, "shared": len(sh)})
        lo, hi = max(0, 10 * b - 5), min(100, 10 * b + 5)
        print(f"| {lo}-{hi}% | {100 - hi}-{100 - lo}% | {len(idx)} | {er:.1%} | {len(sh)} | {len(sh) / len(idx):.1%} | "
              + " / ".join(str(g[c]) for c in CLASSES) + " |")
    print(f"no Arabic or Latin letter: {sum(b is None for b in bins)}")

    # Per error type of the shared errors: classes, errors and script bins.
    print("\n| Error type | Shared errors | Gold NEG / NEU / POS | Main error (gold → predicted) | Arabic share: 95-100 / 65-95 / 35-65 / under 35% | Mean Arabic share |")
    print("|---|---|---|---|---|---|")
    groups = defaultdict(list)
    for i in shared:
        groups[types.get(dev[i]["text_id"], "not in SG01-most-errors")].append(i)
    out["per_error_type"] = {}
    def share(i: int) -> float:
        t = PLACEHOLDER_RE.sub(" ", dev[i].get("text_raw", dev[i]["text"]))
        ar, lat = len(ARABIC_LETTER_RE.findall(t)), len(LATIN_LETTER_RE.findall(t))
        return ar / (ar + lat) if ar + lat else float("nan")
    for t, idx in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        g = Counter(dev[i]["sentiment"] for i in idx)
        moves = Counter(f"{dev[i]['sentiment']}→{top_pred(i)}" for i in idx).most_common(2)
        s = [share(i) for i in idx]
        bands = [sum(x >= 0.95 for x in s), sum(0.65 <= x < 0.95 for x in s), sum(0.35 <= x < 0.65 for x in s), sum(x < 0.35 for x in s)]
        out["per_error_type"][t] = {"n": len(idx), "gold": dict(g), "bands": bands, "mean_arabic": sum(s) / len(s)}
        print(f"| {t} | {len(idx)} | {g['NEG']} / {g['NEU']} / {g['POS']} | {', '.join(f'{m} {k}' for m, k in moves)} | "
              + " / ".join(map(str, bands)) + f" | {sum(s) / len(s):.0%} |")
    s_all = [share(i) for i in range(len(dev)) if bins[i] is not None]
    print(f"dev mean Arabic share {sum(s_all) / len(s_all):.0%}; shared errors {sum(share(i) for i in shared) / len(shared):.0%}")
    out["mean_arabic_dev"], out["mean_arabic_shared"] = sum(s_all) / len(s_all), sum(share(i) for i in shared) / len(shared)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


BERTS = ["marbert", "marbertv2", "arabertv02_twitter", "arbert", "arbertv2", "camelbert_mix", "camelbert_da"]
GENS = ["aya", "fanar", "qwen3"]


def pairs() -> list[tuple[str, str, str]]:
    """(condition, 3-epoch folder, 8-epoch folder) for every BERT x generator x seed."""
    out = []
    for s in (42, 43, 44):
        for b in BERTS:
            out.append(("SR05-EESA", f"sr01_eesa_tl_{b}_seed{s}", f"sr05_eesa_{b}_seed{s}"))
            for g in GENS:
                out.append(("SR05-EESA", f"sr02_eesa_tl_{b}_{g}_seed{s}", f"sr05_eesa_{b}_{g}_seed{s}"))
                out.append(("SR06-EESA", f"sr04_eesa_{b}_{g}_seed{s}", f"sr06_eesa_{b}_{g}_seed{s}"))
                out.append(("SR06-random-EESA", f"sr04r_eesa_{b}_{g}_seed{s}", f"sr06r_eesa_{b}_{g}_seed{s}"))
    return out


def compare() -> None:
    """Dev errors of the 210 paired runs at 3 and at 8 epochs."""
    sys.stdout.reconfigure(encoding="utf-8")
    dev = [json.loads(l) for l in open(DEV, encoding="utf-8")]
    types = {r["text_id"]: r["error_type"] for r in map(json.loads, open(TYPES, encoding="utf-8"))}
    P = pairs()
    missing = [f for _, a, b in P for f in (a, b) if not (RUNS / f / "dev_predictions.jsonl").exists()]
    if missing:
        sys.exit(f"missing dev predictions: {missing[:3]} ({len(missing)})")
    # wrong[ep][i] = runs wrong on text i; per-run error rates for the paired test.
    wrong = {3: Counter(), 8: Counter()}
    run_err = {3: [], 8: []}
    cls_err = {3: Counter(), 8: Counter()}
    for _, f3, f8 in P:
        for ep, f in ((3, f3), (8, f8)):
            n = 0
            for i, line in enumerate(open(RUNS / f / "dev_predictions.jsonl", encoding="utf-8")):
                p = json.loads(line)
                assert p["text_id"] == dev[i]["text_id"], f
                if p["pred"] != p["gold"]:
                    wrong[ep][i] += 1
                    cls_err[ep][p["gold"]] += 1
                    n += 1
            run_err[ep].append(n / len(dev))
    N = len(P)
    diffs = [b - a for a, b in zip(run_err[3], run_err[8])]
    better = sum(d < 0 for d in diffs)
    out = {"pairs": N, "error_rate": {ep: sum(run_err[ep]) / N for ep in (3, 8)},
           "runs_better_at_8": better, "runs_worse_at_8": sum(d > 0 for d in diffs)}
    print(f"{N} paired runs; dev error rate 3 ep {out['error_rate'][3]:.1%} -> 8 ep {out['error_rate'][8]:.1%} "
          f"({out['error_rate'][8] - out['error_rate'][3]:+.1%}); fewer errors at 8 ep in {better} runs, more in {out['runs_worse_at_8']}")

    # Per class.
    print("\n| Gold class | Dev texts | Error rate 3 epochs | 8 epochs | Change |")
    print("|---|---|---|---|---|")
    out["per_class"] = {}
    for c in CLASSES:
        n = sum(d["sentiment"] == c for d in dev)
        a, b = cls_err[3][c] / (n * N), cls_err[8][c] / (n * N)
        out["per_class"][c] = {"3": a, "8": b}
        print(f"| {c} | {n} | {a:.1%} | {b:.1%} | {b - a:+.1%} |")

    # Per condition.
    print("\n| Condition | Pairs | Error rate 3 epochs | 8 epochs | Change |")
    print("|---|---|---|---|---|")
    for cond in ("SR05-EESA", "SR06-random-EESA", "SR06-EESA"):
        idx = [k for k, (c, _, _) in enumerate(P) if c == cond]
        a, b = (sum(run_err[ep][k] for k in idx) / len(idx) for ep in (3, 8))
        print(f"| {cond} | {len(idx)} | {a:.1%} | {b:.1%} | {b - a:+.1%} |")

    # Shared errors (majority of the paired runs) at each epoch count and how they move.
    shared = {ep: {i for i in range(len(dev)) if wrong[ep][i] > N / 2} for ep in (3, 8)}
    both, fixed, new = shared[3] & shared[8], shared[3] - shared[8], shared[8] - shared[3]
    never = {ep: sum(wrong[ep][i] == 0 for i in range(len(dev))) for ep in (3, 8)}
    out["shared"] = {"3": len(shared[3]), "8": len(shared[8]), "both": len(both), "fixed": len(fixed), "new": len(new),
                     "never_wrong_3": never[3], "never_wrong_8": never[8]}
    print(f"\nshared errors: 3 ep {len(shared[3])}, 8 ep {len(shared[8])}; in both {len(both)}; "
          f"fixed by 8 ep {len(fixed)}; new at 8 ep {len(new)}; never wrong 3 ep {never[3]}, 8 ep {never[8]}")
    # Per text: change in the number of wrong runs.
    moved = Counter()
    for i in range(len(dev)):
        d = wrong[8][i] - wrong[3][i]
        moved["fewer wrong runs (by 21+)" if d <= -21 else "more wrong runs (by 21+)" if d >= 21 else "about the same (within 20)"] += 1
    out["per_text"] = dict(moved)
    print("per text (change in wrong runs out of 210):", dict(moved))

    # Shared errors per error type, 3 vs 8.
    print("\n| Error type | Shared at 3 epochs | Shared at 8 epochs | In both | Mean wrong runs 3 → 8 (texts shared at either) |")
    print("|---|---|---|---|---|")
    groups = defaultdict(set)
    for i in shared[3] | shared[8]:
        groups[types.get(dev[i]["text_id"], "not in SG01-most-errors")].add(i)
    out["per_error_type"] = {}
    for t, idx in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        a, b = len(idx & shared[3]), len(idx & shared[8])
        m3, m8 = (sum(wrong[ep][i] for i in idx) / len(idx) for ep in (3, 8))
        out["per_error_type"][t] = {"3": a, "8": b, "both": len(idx & both), "mean_wrong_3": m3, "mean_wrong_8": m8}
        print(f"| {t} | {a} | {b} | {len(idx & both)} | {m3:.0f} → {m8:.0f} of {N} |")
    print("\nfixed by 8 epochs (shared at 3, not at 8):")
    for i in sorted(fixed, key=lambda i: wrong[8][i] - wrong[3][i]):
        print(f"  {wrong[3][i]} -> {wrong[8][i]} | {dev[i]['sentiment']} | {types.get(dev[i]['text_id'], 'new')[:30]} | "
              + " ".join(dev[i]["text"].split())[:110])
    print("new at 8 epochs (shared at 8, not at 3):")
    for i in sorted(new, key=lambda i: wrong[3][i] - wrong[8][i]):
        print(f"  {wrong[3][i]} -> {wrong[8][i]} | {dev[i]['sentiment']} | {types.get(dev[i]['text_id'], 'new')[:30]} | "
              + " ".join(dev[i]["text"].split())[:110])
    (OUT.parent / "eesa_dev_errors_3v8ep.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    sys.exit(compare() if "--compare-3ep" in sys.argv[1:] else main())
