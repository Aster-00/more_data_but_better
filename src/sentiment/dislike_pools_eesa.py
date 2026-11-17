"""Few-shot example pools for SG04-EESA (dislike comments) and its random control SG04-random-EESA.

Dislike comment = mentions dislikes (dislike / unlike / دس لايك, any spelling below). error_type is set to
"Dislike comments" so the generator's type_sentiment matching (D-034) works unchanged. NEG and NEU only
(Ammar, 2026-11-17: half NEG, half NEU; POS dropped, the error pool has one POS text).
  targeted: EESA dev dislike comments that a majority of the 210 8-epoch BERT runs get wrong
            (SR05-EESA, SR06-EESA, SR06-random-EESA; src.sentiment.dev_errors_eesa) -> dev-contaminated
  control:  all EESA train dislike comments of those classes (random 5 drawn per request by the generator)
Outputs: data/inspect/hard_cases/sg04_dislike_errors_eesa.jsonl, sg04r_dislike_train_eesa.jsonl.

Usage:
  python -m src.sentiment.dislike_pools_eesa
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

RUNS = Path("results/sentiment/runs")
OUT = Path("data/inspect/hard_cases")
DISLIKE = re.compile(r"dis+\s*-?likes?|deslik|un\s*likes?|دس\s*لايك|ديس\s*لايك|دسلايك", re.I)
TYPE, CLASSES = "Dislike comments", ("NEG", "NEU")


def read(path: Path) -> list[dict]:
    """JSONL records."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f]


def main() -> None:
    """Write the targeted (dev errors) and control (train) pools."""
    sys.stdout.reconfigure(encoding="utf-8")
    dev = read(Path("data/processed/sentiment/eesa_dev.jsonl"))
    train = read(Path("data/processed/sentiment/eesa_train.jsonl"))
    runs = sorted(d for d in RUNS.iterdir() if re.fullmatch(r"sr0(5|6|6r)_eesa_.+_seed4[234]", d.name))
    wrong = Counter()
    for d in runs:
        for i, line in enumerate(open(d / "dev_predictions.jsonl", encoding="utf-8")):
            p = json.loads(line)
            assert p["text_id"] == dev[i]["text_id"], d
            wrong[i] += p["pred"] != p["gold"]
    OUT.mkdir(parents=True, exist_ok=True)
    targeted = [dev[i] | {"error_type": TYPE, "wrong_runs": wrong[i], "of_runs": len(runs)}
                for i in range(len(dev)) if DISLIKE.search(dev[i]["text"]) and dev[i]["sentiment"] in CLASSES
                and wrong[i] > len(runs) / 2]
    control = [r | {"error_type": TYPE} for r in train if DISLIKE.search(r["text"]) and r["sentiment"] in CLASSES]
    for name, recs in (("sg04_dislike_errors_eesa", targeted), ("sg04r_dislike_train_eesa", control)):
        with open(OUT / f"{name}.jsonl", "w", encoding="utf-8", newline="\n") as f:
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"{name}: {len(recs)} {dict(Counter(r['sentiment'] for r in recs))}")
    for r in sorted(targeted, key=lambda r: (r["sentiment"], -r["wrong_runs"])):
        print(f"  {r['sentiment']} {r['wrong_runs']}/{len(runs)} | " + " ".join(r["text"].split())[:120])


if __name__ == "__main__":
    sys.exit(main())
