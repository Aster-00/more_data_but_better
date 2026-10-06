"""Validate the scorer models against human gold: the MLADI dev set (120 sentences, 8 dialects).

The label trust rule says automatic labellers may be used only once validated against
human labels. The DID scorers will act as dialect-fidelity filters for synthetic data, so
this measures how often their decisions agree with the MLADI annotators.

CAMeLBERT DID (nadi, madar), predictions mapped onto the 18 MLADI countries:
  top1        only the top country is valid (a single-label classifier used as multi-label)
  mass>=0.3   every country whose summed probability is >= 0.3 is valid (leaderboard
              threshold, not tuned)
  top1_in_gold  share of sentences whose top country is one of the gold-valid dialects;
              this is exactly the fidelity filter's accept decision. Sentences whose top
              country has no dev label (e.g. Iraq) are counted separately as "unscorable".
Sentence-ALDi: Spearman correlation between the ALDi score and the number of dialects a
sentence is valid in (more dialectal sentences are expected to be valid in fewer dialects).
E5 has no labelled target here, so it is not validated by this script.

Output: results/scorers/<run_id>.json

Usage:
  python -m src.quality.validate_scorers --run-id S01
  python -m src.quality.validate_scorers --run-id S01_limit --limit 20
"""
from __future__ import annotations

import argparse
import json
import platform
import sys
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

from src.data.build_dataset import git_commit, read_dev, sha256
from src.evaluation.metrics import multilabel_scores
from src.quality.scorers import ALDiScorer, DIDScorer


def did_scores(scorer: DIDScorer, texts: list[str], gold: dict[str, list[int]], threshold: float) -> dict:
    """Multi-label scores of one DID scorer under the top-1 and mass-threshold decision rules."""
    preds = scorer.predict(texts)
    dialects = list(gold)
    # Decision rules turned into 0/1 columns for the dev dialects.
    top1 = {d: [int(p["top_country"] == d) for p in preds] for d in dialects}
    mass = {d: [int(p["by_country"].get(d, 0.0) >= threshold) for p in preds] for d in dialects}

    # Fidelity-filter view: is the top country one of the sentence's gold-valid dialects?
    in_gold = unscorable = 0
    for i, p in enumerate(preds):
        if p["top_country"] not in gold:
            unscorable += 1
        elif gold[p["top_country"]][i] == 1:
            in_gold += 1
    scorable = len(texts) - unscorable
    return {
        "model": scorer.model_id,
        "top1": multilabel_scores(gold, top1),
        f"mass>={threshold}": multilabel_scores(gold, mass),
        "top1_in_gold": {"n_scorable": scorable, "n_unscorable": unscorable,
                         "accepted": in_gold,
                         "share_of_scorable": round(100 * in_gold / scorable, 2) if scorable else None},
        "top_country_counts": {c: sum(p["top_country"] == c for p in preds)
                               for c in sorted({str(p["top_country"]) for p in preds})},
    }


def aldi_scores(scorer: ALDiScorer, texts: list[str], gold: dict[str, list[int]]) -> dict:
    """Spearman correlation between ALDi and how many dev dialects a sentence is valid in."""
    aldi = np.array(scorer.score(texts))
    cardinality = np.array([sum(gold[d][i] for d in gold) for i in range(len(texts))])
    rho, p = spearmanr(aldi, cardinality)
    # Mean ALDi per cardinality, to show the shape of the relation.
    by_card = {int(k): {"n": int((cardinality == k).sum()), "mean_aldi": round(float(aldi[cardinality == k].mean()), 4)}
               for k in sorted(set(cardinality.tolist()))}
    return {"model": scorer.model_id, "spearman_rho": round(float(rho), 4), "p_value": float(p),
            "mean_aldi": round(float(aldi.mean()), 4), "by_cardinality": by_card}


def main() -> None:
    """Score the DID and ALDi scorers on the dev set and write one JSON report."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--run-id", required=True)
    p.add_argument("--dev", type=Path, default=Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"))
    p.add_argument("--threshold", type=float, default=0.3)
    p.add_argument("--cache-dir", type=Path, default=Path("F:/Thesis/models"))
    p.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    p.add_argument("--limit", type=int, default=None, help="tiny-subset mode: first N dev sentences")
    args = p.parse_args()

    # Dev sentences and their human multi-label gold (8 dialects).
    texts, gold = read_dev(args.dev)
    if args.limit is not None:
        texts, gold = texts[:args.limit], {d: v[:args.limit] for d, v in gold.items()}

    report = {"run_id": args.run_id, "dev_file": str(args.dev), "dev_sha256": sha256(args.dev),
              "n_sentences": len(texts), "dialects_scored": list(gold), "threshold": args.threshold,
              "device": args.device, "git_commit": git_commit(), "python": platform.python_version(),
              "torch": torch.__version__}
    # One scorer at a time on the GPU.
    for variant in ("nadi", "madar"):
        scorer = DIDScorer(variant, args.cache_dir, args.device)
        report[f"did_{variant}"] = did_scores(scorer, texts, gold, args.threshold)
        del scorer
    report["aldi"] = aldi_scores(ALDiScorer(args.cache_dir, args.device), texts, gold)

    out = Path("results/scorers") / f"{args.run_id}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # Console summary.
    for variant in ("nadi", "madar"):
        r = report[f"did_{variant}"]
        for rule in ("top1", f"mass>={args.threshold}"):
            m = r[rule]["macro"]
            print(f"DID-{variant:5s} {rule:9s} macro F1 {m['f1']:.2f}  P {m['precision']:.2f}  R {m['recall']:.2f}")
        g = r["top1_in_gold"]
        print(f"DID-{variant:5s} top-1 in gold: {g['accepted']}/{g['n_scorable']} = {g['share_of_scorable']}%  "
              f"(unscorable {g['n_unscorable']})")
    a = report["aldi"]
    print(f"ALDi vs cardinality: Spearman {a['spearman_rho']} (p={a['p_value']:.3g})  {a['by_cardinality']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    sys.exit(main())
