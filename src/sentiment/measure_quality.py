"""Quality measures of the SG01 / SG02 synthetic sentiment sets, with a real S1 reference (decision SD-005).

Measures (definitions agreed with Ammar, 2026-10-17); all on the selected sets (the texts used
for training) unless stated:
  imbalance        largest / smallest count over the 12 variety x sentiment cells (full set)
  msa_share        share of dialect-cell texts (egypt/gulf/levant) with ALDi below a cutoff; the
                   cutoff is the ALDi value that best separates msa from dialect tweets in S1 train
                   (max balanced accuracy)
  dialectness      mean ALDi (Sentence-ALDi, 0 = MSA, 1 = strongly dialectal) of the dialect-cell texts
  mtld             lexical diversity (MTLD, whitespace tokens), on a seeded sample of `n` texts
  topic_spread     number of the 30 topics (k-means on E5 embeddings of S1 train) that receive at
                   least 1% of a sample of `n` texts
  vendi            Vendi score of the E5 embeddings of the same sample
  repeats          share of the raw generated texts that are exact or near duplicates (from the
                   filter statistics; before filtering)
  fidelity         share of texts whose sentiment, as predicted by the SR01 MARBERT classifiers
                   (seeds 42/43/44, mean of the class probabilities; trained on real data only),
                   equals the requested sentiment
Real reference row: a seeded sample of `n` S1 train tweets (msa/egypt/gulf/levant) for the
label-free measures; imbalance over all of S1 train; repeats = near/exact duplicates in that
sample; fidelity = the same classifiers' accuracy on S1 dev (on train it would be in-sample).
The official test set is not used. Size-dependent measures use equal-size samples.

Outputs: results/quality/sentiment/<set>_quality.json, docs/sentiment/tables/<set>_quality.{csv,md}
(<set> = sg01, the default, or sg02: same measures, k-means seed and sample seed, so rows compare).

Usage:
  python -m src.sentiment.measure_quality
  python -m src.sentiment.measure_quality --set sg02
  python -m src.sentiment.measure_quality --n 300        # tiny mode
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch

from src.data.build_dataset import git_commit, sha256
from src.filtering.dedup import dedup_key, exact_duplicates, near_duplicates_within
from src.quality.lexical import mtld, tokenize

GENERATOR_NAMES = {"jais2": "Jais-2-8B", "fanar": "Fanar-1-9B", "qwen3": "Qwen3-8B", "aya": "Aya-Expanse-8B"}
# Generators per synthetic set (SG02 without Jais-2, SD-006).
SET_GENERATORS = {"sg01": ["jais2", "fanar", "qwen3", "aya"], "sg02": ["fanar", "qwen3", "aya"]}
VARIETIES, SENTIMENTS = ["msa", "egypt", "gulf", "levant"], ["NEG", "NEU", "POS"]
DIALECTS = {"egypt", "gulf", "levant"}
TRAIN = Path("data/processed/sentiment/arsarcasm_v2_train.jsonl")
DEV = Path("data/processed/sentiment/arsarcasm_v2_dev.jsonl")
SYN = Path("data/synthetic/sentiment")
CLASSIFIERS = [Path(f"results/sentiment/runs/sr01_marbert_seed{s}/model") for s in (42, 43, 44)]
CACHE = Path("F:/Thesis/models")


def read(path: Path) -> list[dict]:
    """JSONL records with text."""
    with open(path, encoding="utf-8") as f:
        return [r for r in map(json.loads, f) if r.get("text")]


def cell(r: dict) -> tuple[str, str]:
    """(variety, sentiment) of a real or synthetic record."""
    c = r.get("controls")
    return (c["variety"], c["sentiment"]) if c else (r["dialect"], r["sentiment"])


def aldi_cutoff(scores: np.ndarray, is_msa: np.ndarray) -> float:
    """ALDi value that best separates real msa from dialect tweets (max balanced accuracy)."""
    best, best_t = -1.0, 0.5
    for t in np.unique(np.round(scores, 3)):
        bal = ((scores[is_msa] < t).mean() + (scores[~is_msa] >= t).mean()) / 2
        if bal > best:
            best, best_t = bal, float(t)
    return best_t


def vendi(emb: np.ndarray) -> float:
    """Vendi score of L2-normalized embeddings (as in src/quality/measure.py)."""
    eig = np.linalg.eigvalsh(emb.T @ emb / len(emb))
    eig = eig[eig > 1e-12]
    return float(np.exp(-(eig * np.log(eig)).sum()))


def sentiment_probs(texts: list[str], device: str) -> np.ndarray:
    """Mean class probabilities (NEG/NEU/POS) of the three SR01 MARBERT seeds."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    from src.sentiment.common import predict_logits
    total = np.zeros((len(texts), len(SENTIMENTS)))
    for path in CLASSIFIERS:
        tok = AutoTokenizer.from_pretrained(path)
        model = AutoModelForSequenceClassification.from_pretrained(path).to(device)
        total += torch.softmax(torch.from_numpy(predict_logits(model, tok, texts, 128, device)), -1).numpy()
        del model
    return total / len(CLASSIFIERS)


def main() -> None:
    """Measure every generator's set of one synthetic run and the real reference; write JSON and tables."""
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--n", type=int, default=3000, help="sample size for the size-dependent measures")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--set", default="sg01", choices=sorted(SET_GENERATORS))
    p.add_argument("--device", default="cuda")
    args = p.parse_args()
    started = time.time()
    tag = args.set
    GENERATORS = {g: GENERATOR_NAMES[g] for g in SET_GENERATORS[tag]}

    # Real data: S1 train restricted to the four varieties used for generation.
    train = [r for r in read(TRAIN) if r["dialect"] in VARIETIES]
    dev = [r for r in read(DEV) if r["dialect"] in VARIETIES]
    # Tiny mode (--n < 1000): fewer real texts for the cutoff, the topics and the dev fidelity.
    if args.n < 1000:
        train, dev = random.Random(args.seed).sample(train, 2000), dev[:300]
    sets = {"real": {"name": "S1 real (reference)", "all": train,
                     "sample": random.Random(args.seed).sample(train, min(args.n, len(train)))}}
    for g, name in GENERATORS.items():
        sel = read(SYN / f"{tag}_{g}.selected.jsonl")
        sets[g] = {"name": name, "all": sel, "sample": random.Random(args.seed).sample(sel, min(args.n, len(sel)))}

    # ALDi: cutoff from S1 train (msa vs dialect labels), then scores for every set's dialect cells.
    from src.quality.scorers import ALDiScorer, E5Embedder
    aldi = ALDiScorer(CACHE, args.device)
    train_aldi = np.asarray(aldi.score([r["text"] for r in train]))
    cutoff = aldi_cutoff(train_aldi, np.asarray([r["dialect"] == "msa" for r in train]))
    print(f"ALDi cutoff {cutoff} (from S1 train)", flush=True)
    for s in sets.values():
        dia = [r["text"] for r in s["all"] if cell(r)[0] in DIALECTS]
        sc = np.asarray(aldi.score(dia))
        s["msa_share"], s["dialectness"] = float((sc < cutoff).mean()), float(sc.mean())
    del aldi

    # E5: 30 topics from S1 train, then topic spread and Vendi on each sample.
    from sklearn.cluster import KMeans
    e5 = E5Embedder(CACHE, args.device)
    km = KMeans(n_clusters=30, n_init=10, random_state=args.seed).fit(e5.embed([r["text"] for r in train]))
    for s in sets.values():
        emb = e5.embed([r["text"] for r in s["sample"]]).astype(np.float64)
        counts = Counter(km.predict(emb.astype(np.float32)))
        s["topic_spread"] = sum(1 for c in counts.values() if c >= 0.01 * len(emb))
        s["vendi"] = vendi(emb)
    del e5

    # Lexical diversity on the samples; imbalance over the full sets.
    for s in sets.values():
        s["mtld"] = mtld([t for r in s["sample"] for t in tokenize(r["text"])])
        cells = Counter(cell(r) for r in s["all"])
        counts = [cells.get((v, c), 0) for v in VARIETIES for c in SENTIMENTS]
        s["imbalance"] = max(counts) / max(1, min(counts))

    # Repeats: synthetic from the filter statistics (raw output); real from duplicates in its sample.
    for g in GENERATORS:
        f = json.load(open(f"results/filtering/{tag}_{g}.json", encoding="utf-8"))
        rb = f["rejected_by_first_failing_check"]
        sets[g]["repeats"] = (rb["exact_dup_within"] + rb["near_dup_within"]) / f["n_in"]
    keys = [dedup_key(r["text"]) for r in sets["real"]["sample"]]
    sets["real"]["repeats"] = len(set(exact_duplicates(keys)) | set(near_duplicates_within(keys, 0.8, 5))) / len(keys)

    # Fidelity: SR01 MARBERT ensemble agrees with the requested label (real: accuracy on S1 dev).
    for key, s in sets.items():
        recs = dev if key == "real" else s["all"]
        pred = sentiment_probs([r["text"] for r in recs], args.device).argmax(-1)
        s["fidelity"] = float(np.mean([SENTIMENTS[k] == cell(r)[1] for k, r in zip(pred, recs)]))
        s["fidelity_per_class"] = {c: float(np.mean([SENTIMENTS[k] == c for k, r in zip(pred, recs) if cell(r)[1] == c]))
                                   for c in SENTIMENTS}

    # Write JSON and tables.
    cols = ["imbalance", "msa_share", "dialectness", "mtld", "topic_spread", "vendi", "repeats", "fidelity"]
    out = {"set": tag, "n_sample": args.n, "seed": args.seed, "aldi_cutoff": cutoff,
           "sets": {k: {c: s[c] for c in cols + ["fidelity_per_class"]} | {"name": s["name"], "n": len(s["all"])}
                    for k, s in sets.items()},
           "inputs": {k: sha256(SYN / f"{tag}_{k}.selected.jsonl") for k in GENERATORS} | {"train": sha256(TRAIN), "dev": sha256(DEV)},
           "git_commit": git_commit(), "seconds": round(time.time() - started), "finished": time.strftime("%Y-%m-%d %H:%M")}
    Path("results/quality/sentiment").mkdir(parents=True, exist_ok=True)
    with open(f"results/quality/sentiment/{tag}_quality.json", "w", encoding="utf-8", newline="\n") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    fmt = {"imbalance": "{:.1f} : 1", "msa_share": "{:.1%}", "dialectness": "{:.2f}", "mtld": "{:.1f}",
           "topic_spread": "{}", "vendi": "{:.1f}", "repeats": "{:.1%}", "fidelity": "{:.1%}"}
    heads = ["Imbalance (max : min)", "MSA share", "Dialectness", "Lexical diversity (MTLD)", "Topic spread (of 30)",
             "Semantic diversity (Vendi)", "Repeats", "Fidelity"]
    Path("docs/sentiment/tables").mkdir(parents=True, exist_ok=True)
    with open(f"docs/sentiment/tables/{tag}_quality.csv", "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["set"] + cols)
        for s in sets.values():
            w.writerow([s["name"]] + [s[c] for c in cols])
    md = [f"# {tag.upper()} quality", "", f"Generated by `python -m src.sentiment.measure_quality --set {tag}` (results/quality/sentiment/{tag}_quality.json). "
          f"Do not edit by hand. Samples of {args.n} texts for MTLD, topic spread and Vendi; ALDi cutoff {cutoff} from S1 train.", "",
          "| Set | " + " | ".join(heads) + " |", "|" + "---|" * (len(heads) + 1)]
    md += ["| " + s["name"] + " | " + " | ".join(fmt[c].format(s[c]) for c in cols) + " |" for s in sets.values()]
    with open(f"docs/sentiment/tables/{tag}_quality.md", "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(md) + "\n")
    print("\n".join(md[4:]))


if __name__ == "__main__":
    sys.exit(main())
