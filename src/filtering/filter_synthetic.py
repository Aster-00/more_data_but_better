"""Filter a synthetic set (pipeline stage 4): duplicates, script, length, dialect fidelity.

Every record is scored by every enabled check first (so the statistics say how many texts
fail each check), then the checks are applied in config order and a record is rejected by
the first failing one. Nothing is deleted: kept records go to <set>.filtered.jsonl, rejected
ones to <set>.rejected.jsonl with `rejected_by` and `failed_checks`, and the counts go to
results/filtering/<set>.json. Each check can be switched off in the config.

Checks (names as in the config):
  parse_ok            the generator output could be parsed into a sentence
  exact_dup_within    identical text earlier in the set (first occurrence kept)
  near_dup_within     MinHash near-duplicate of an earlier text (Jaccard of char 5-grams >= threshold)
  dup_against_real    near-duplicate of a D1 text (copied or memorised training data)
  dup_against_dev     near-duplicate of an MLADI dev sentence (leak check)
  script              letter shares match the requested script (open sets: Arabic script expected)
  length              word count inside [min_words, max_words]
  did_nadi/did_madar  CAMeLBERT DID top-1 country == target (or P(target) >= min_prob);
                      targets the scorer has no label for are not rejected (madar: Bahrain, Kuwait, UAE)
  aldi                Sentence-ALDi score >= min_score (the text is dialectal, not MSA)

Thresholds are set on D1 and the dev set (see src/quality/measure.py on a D1 sample), never
on the test set.

Usage:
  python -m src.filtering.filter_synthetic --data data/synthetic/open_v1_fanar.jsonl
  python -m src.filtering.filter_synthetic --data data/synthetic/open_v1_fanar.jsonl --config configs/filtering/default.json --limit 50
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from collections import Counter
from pathlib import Path

from src.data.build_dataset import git_commit, sha256
from src.filtering.dedup import dedup_key, exact_duplicates, near_duplicates_against, near_duplicates_within
from src.quality.measure import observed_script, script_features

CHECK_ORDER = ["parse_ok", "exact_dup_within", "near_dup_within", "dup_against_real", "dup_against_dev",
               "script", "length", "did_nadi", "did_madar", "aldi"]


def read_reference_keys(path: Path) -> list[str]:
    """Dedup keys of a reference file: D1 JSONL (field `text`) or the MLADI dev TSV (column 0)."""
    keys = []
    if path.suffix == ".tsv":
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            next(reader)
            keys = [dedup_key(row[0]) for row in reader]
    else:
        with open(path, encoding="utf-8") as f:
            keys = [dedup_key(json.loads(l)["text"]) for l in f if l.strip()]
    return keys


def run_checks(records: list[dict], cfg: dict, device: str) -> dict[str, list[dict]]:
    """Evaluate every enabled check on every record; return check name -> per-record results.

    Each per-record result is {"ok": bool, ...details}. Records without text fail only
    `parse_ok`; the other checks mark them ok so they are not double counted.
    """
    f = cfg["checks"]
    texts = [r.get("text") or "" for r in records]
    has_text = [bool(t) for t in texts]
    keys = [dedup_key(t) for t in texts]
    results: dict[str, list[dict]] = {}

    results["parse_ok"] = [{"ok": h} for h in has_text]

    if f["exact_dup_within"]["enabled"]:
        dup = exact_duplicates([k if h else f"__empty_{i}" for i, (k, h) in enumerate(zip(keys, has_text))])
        results["exact_dup_within"] = [{"ok": i not in dup, "duplicate_of": records[dup[i]]["text_id"] if i in dup else None}
                                       for i in range(len(records))]
    if f["near_dup_within"]["enabled"]:
        c = f["near_dup_within"]
        near = near_duplicates_within([k if h else f"__empty_{i}" for i, (k, h) in enumerate(zip(keys, has_text))],
                                      c["threshold"], c["ngram"])
        results["near_dup_within"] = [{"ok": i not in near, "duplicate_of": records[near[i][0]]["text_id"] if i in near else None,
                                       "jaccard": near[i][1] if i in near else None} for i in range(len(records))]
    for name in ("dup_against_real", "dup_against_dev"):
        if f[name]["enabled"]:
            c = f[name]
            ref = read_reference_keys(Path(c["reference"]))
            hit = near_duplicates_against(keys, ref, c["threshold"], c["ngram"])
            results[name] = [{"ok": not (has_text[i] and i in hit), "reference_index": hit[i][0] if i in hit else None,
                              "jaccard": hit[i][1] if i in hit else None} for i in range(len(records))]

    if f["script"]["enabled"]:
        c, out = f["script"], []
        for r, t, h in zip(records, texts, has_text):
            expected = r.get("controls", {}).get("script", c["default_script"])
            feats = script_features(t)
            obs = observed_script(feats, c["min_share"])
            out.append({"ok": (not h) or obs == expected, "expected": expected, "observed": obs,
                        "arabic_share": round(feats["arabic_share"], 3), "latin_share": round(feats["latin_share"], 3)})
        results["script"] = out

    if f["length"]["enabled"]:
        c = f["length"]
        results["length"] = [{"ok": (not h) or c["min_words"] <= len(t.split()) <= c["max_words"], "words": len(t.split())}
                             for t, h in zip(texts, has_text)]

    # Model-based checks: load each scorer once, score only records with text.
    idx = [i for i, h in enumerate(has_text) if h]
    for variant in ("nadi", "madar"):
        name = f"did_{variant}"
        if f[name]["enabled"]:
            from src.quality.scorers import DIDScorer
            c = f[name]
            scorer = DIDScorer(variant, Path(cfg["cache_dir"]), device)
            preds = scorer.predict([texts[i] for i in idx])
            out = [{"ok": True, "covered": False} for _ in records]
            for i, p in zip(idx, preds):
                target = records[i]["target_dialect"]
                covered = scorer.is_covered(target)
                p_target = p["by_country"].get(target, 0.0)
                ok = (not covered) or (p["top_country"] == target if c["mode"] == "top1" else p_target >= c["min_prob"])
                out[i] = {"ok": ok, "covered": covered, "top_country": p["top_country"], "top_raw": p["top_raw"],
                          "p_target": round(p_target, 4)}
            results[name] = out
            del scorer
    if f["aldi"]["enabled"]:
        from src.quality.scorers import ALDiScorer
        c = f["aldi"]
        scores = ALDiScorer(Path(cfg["cache_dir"]), device).score([texts[i] for i in idx])
        out = [{"ok": True, "aldi": None} for _ in records]
        for i, s in zip(idx, scores):
            out[i] = {"ok": s >= c["min_score"], "aldi": s}
        results["aldi"] = out
    return results


def apply(records: list[dict], results: dict[str, list[dict]]) -> tuple[list[dict], list[dict], dict]:
    """Reject each record by the first failing check (config order); return kept, rejected, stats."""
    order = [c for c in CHECK_ORDER if c in results]
    kept, rejected = [], []
    failed_any = Counter()
    rejected_by = Counter()
    rejected_by_dialect: dict[str, Counter] = {}
    for i, r in enumerate(records):
        failed = [c for c in order if not results[c][i]["ok"]]
        failed_any.update(failed)
        r = dict(r)
        r["checks"] = {c: results[c][i] for c in order}
        if failed:
            r["rejected_by"], r["failed_checks"] = failed[0], failed
            rejected_by[failed[0]] += 1
            rejected_by_dialect.setdefault(r["target_dialect"], Counter())[failed[0]] += 1
            rejected.append(r)
        else:
            kept.append(r)
    stats = {
        "n_in": len(records), "n_kept": len(kept), "n_rejected": len(rejected),
        "kept_rate": round(len(kept) / max(1, len(records)), 4),
        "check_order": order,
        "failed_any_check": {c: failed_any.get(c, 0) for c in order},
        "rejected_by_first_failing_check": {c: rejected_by.get(c, 0) for c in order},
        "kept_per_dialect": dict(Counter(r["target_dialect"] for r in kept)),
        "rejected_per_dialect": {d: dict(c) for d, c in sorted(rejected_by_dialect.items())},
    }
    return kept, rejected, stats


def write_jsonl(path: Path, records: list[dict]) -> None:
    """Write records as UTF-8 JSONL."""
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def main() -> None:
    """CLI entry point."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, required=True, help="synthetic JSONL set")
    p.add_argument("--config", type=Path, default=Path("configs/filtering/default.json"))
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N records, outputs get _limitN")
    p.add_argument("--device", default="cuda")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:
        cfg = json.load(f)
    with open(args.data, encoding="utf-8") as f:
        records = [json.loads(l) for l in f if l.strip()]
    if any(r.get("source") != "synthetic" for r in records):
        raise ValueError("this filter is for synthetic sets only (source must be 'synthetic')")
    if args.limit is not None:
        records = records[:args.limit]
    stem = args.data.stem + (f"_limit{args.limit}" if args.limit is not None else "")

    started = time.time()
    results = run_checks(records, cfg, args.device)
    kept, rejected, stats = apply(records, results)
    write_jsonl(args.data.with_name(f"{stem}.filtered.jsonl"), kept)
    write_jsonl(args.data.with_name(f"{stem}.rejected.jsonl"), rejected)
    stats.update(data=str(args.data), data_sha256=sha256(args.data), config=cfg, config_file=str(args.config),
                 git_commit=git_commit(), python=platform.python_version(), seconds=round(time.time() - started),
                 finished=time.strftime("%Y-%m-%d %H:%M"))
    out_dir = Path("results/filtering")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / f"{stem}.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(json.dumps({k: stats[k] for k in ("n_in", "n_kept", "n_rejected", "failed_any_check", "rejected_by_first_failing_check")},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    sys.exit(main())
