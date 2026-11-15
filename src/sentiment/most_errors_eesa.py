"""SG01-most-errors: the EESA dev texts most EESA runs get wrong; quality row and E5 error clusters.

Set: EESA dev texts wrong in >= 43 of the 84 EESA BERT runs (SR01-EASA 21 + SR02-EASA 63; 7 BERTs x
seeds 42/43/44; a majority, the hard_cases rule). Dev only (D-032). Ammar, 2026-11-10.

Quality (same measures as src.sentiment.measure_quality / explore_eesa). The set is small (about 100
texts), so every size-dependent measure is also computed on random same-size samples of EESA dev
(seeds 0-19, mean and std): the reference row "EESA dev (same-size samples)". The two rows compare
with each other only, not with the full-size rows of the quality table.
  size-dependent  MTLD (whitespace tokens), Self-BLEU-4 (shared tokenisation), topics of 30 (E5 k-means
                  on EESA train, k 30, seed 42; topics with >= 1% of the texts), universal topics of 19
                  (frozen universal list; 18 named + Unclustered; exp(entropy); texts cleaned as the pool,
                  under 5 words not scored), Vendi (E5)
  size-free       MSA share (ALDi < 0.11), dialectness (mean ALDi), repeats (exact or near duplicates,
                  char 5-gram Jaccard >= 0.8); dev reference: all of dev
  fidelity        N/A (real texts with gold labels)
Error clusters: E5 k-means (k 8, seed 0) on the set; per cluster gold -> majority wrong prediction,
universal topics, and all texts sorted by closeness to the centre.

Outputs:
  data/inspect/hard_cases/sg01_most_errors_eesa.jsonl          the set (text; gitignored)
  data/inspect/hard_cases/sg01_most_errors_eesa_clusters.md    clusters with texts (gitignored)
  results/quality/sentiment/sg01_most_errors_eesa.json / .md   numbers only

Rebuild from the training-loss reruns (D-035): --runs tl reads sr01_eesa_tl_* / sr02_eesa_tl_* and writes
every output with the suffix _tl (the first set is kept). Cluster names apply to the first set only.

Usage:
  python -m src.sentiment.most_errors_eesa
  python -m src.sentiment.most_errors_eesa --runs tl
  python -m src.sentiment.most_errors_eesa --limit 2     # tiny mode: 2 reference samples
"""
from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.quality.measure_dataset_quality import tokens  # noqa: E402
from scripts.topics.fit_topics import clean_for_topics, embed  # noqa: E402
from src.data.build_dataset import git_commit, sha256  # noqa: E402
from src.filtering.dedup import dedup_key, exact_duplicates, near_duplicates_within  # noqa: E402
from src.quality.lexical import mtld, self_bleu, tokenize  # noqa: E402
from src.sentiment.measure_quality import vendi  # noqa: E402

RUNS = ROOT / "results/sentiment/runs"
BERTS = ["marbert", "marbertv2", "arabertv02_twitter", "camelbert_mix", "camelbert_da", "arbert", "arbertv2"]
GENS, SEEDS = ["fanar", "qwen3", "aya"], [42, 43, 44]
TRAIN, DEV = ROOT / "data/processed/sentiment/eesa_train.jsonl", ROOT / "data/processed/sentiment/eesa_dev.jsonl"
TOPICS = ROOT / "data/topics/universal_clean_k50_seed0"
NAMES = ROOT / "configs/quality/topic_names_universal_clean_k50.json"
INSPECT = ROOT / "data/inspect/hard_cases"
OUT = ROOT / "results/quality/sentiment/sg01_most_errors_eesa"
MIN_WRONG, K_ERR, ALDI_CUT = 43, 8, 0.11
CLASSES = ["NEG", "NEU", "POS"]
# Error-cluster names (Ammar, 2026-11-10), valid for k 8, seed 0 on this set.
CLUSTER_NAMES = {1: "Hype and fandom comments", 2: '"Why the dislikes?" questions',
                 3: "Long opinion with a question or advice", 6: "Indirect praise and wishes",
                 7: "Short stretched or emoji comments", 0: "English names of films, shows and products",
                 5: "Neutral remarks on a negative subject", 4: "One or two words"}


def read_jsonl(path: Path) -> list[dict]:
    """All records of a JSONL file."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def effective(labels: list[str]) -> float:
    """exp(Shannon entropy) of the label counts."""
    c, n = Counter(labels), len(labels)
    return math.exp(-sum(v / n * math.log(v / n) for v in c.values())) if n else 0.0


def select(dev: list[dict], tag: str = "") -> list[dict]:
    """Dev texts wrong in >= MIN_WRONG of the 84 runs, with wrong-run count and majority wrong prediction."""
    runs = [RUNS / f"sr01_eesa_{tag}{b}_seed{s}" for b in BERTS for s in SEEDS]
    runs += [RUNS / f"sr02_eesa_{tag}{b}_{g}_seed{s}" for b in BERTS for g in GENS for s in SEEDS]
    wrong = [Counter() for _ in dev]
    for run in runs:
        for i, r in enumerate(read_jsonl(run / "dev_predictions.jsonl")):     # keyed by row position
            assert r["gold"] == dev[i]["sentiment"], f"row order differs in {run}"
            if r["pred"] != r["gold"]:
                wrong[i][r["pred"]] += 1
    out = [r | {"row": i, "wrong_runs": sum(w.values()), "of_runs": len(runs), "majority_wrong_pred": w.most_common(1)[0][0]}
           for i, (r, w) in enumerate(zip(dev, wrong)) if sum(w.values()) >= MIN_WRONG]
    return sorted(out, key=lambda r: (-r["wrong_runs"], r["row"]))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--limit", type=int, default=None, help="tiny mode: number of reference samples")
    p.add_argument("--device", default="cuda")
    p.add_argument("--runs", choices=["first", "tl"], default="first", help="tl: the training-loss reruns (D-035)")
    args = p.parse_args()
    tag, sfx = ("tl_", "_tl") if args.runs == "tl" else ("", "")
    cluster_names = CLUSTER_NAMES if args.runs == "first" else {}
    out = OUT.with_name(OUT.name + sfx)
    t0 = time.time()
    n_ref = args.limit or 20

    train, dev = read_jsonl(TRAIN), read_jsonl(DEV)
    hard = select(dev, tag)
    n = len(hard)
    INSPECT.mkdir(parents=True, exist_ok=True)
    with open(INSPECT / f"sg01_most_errors_eesa{sfx}.jsonl", "w", encoding="utf-8", newline="\n") as f:
        f.writelines(json.dumps(r, ensure_ascii=False) + "\n" for r in hard)
    print(f"{n} dev texts wrong in >= {MIN_WRONG}/84 runs", flush=True)

    # Models: ALDi for dialectness, E5 (fp32) for topics, Vendi and the error clusters.
    from src.quality.scorers import ALDiScorer
    aldi = ALDiScorer(Path("F:/Thesis/models"), args.device)
    dev_aldi = np.asarray(aldi.score([r["text"] for r in dev]))
    del aldi
    hard_rows = [r["row"] for r in hard]
    meta = json.loads((TOPICS / "meta.json").read_text(encoding="utf-8"))
    clean = meta["config"]["clean"]
    X_train, _ = embed([r["text"] for r in train], args.device)
    X_dev, _ = embed([r["text"] for r in dev], args.device)
    cleaned = [clean_for_topics(r["text"], clean) for r in dev]
    X_clean, e5_rev = embed(cleaned, args.device)

    # Topic lists: 30 EESA-train topics (as measure_quality) and the frozen universal list (18 named + Unclustered).
    from sklearn.cluster import KMeans
    km30 = KMeans(n_clusters=30, n_init=10, random_state=42).fit(X_train)
    t30 = km30.predict(X_dev)
    names = json.loads(NAMES.read_text(encoding="utf-8"))
    name_of = {c: nm for nm, cs in names["topics"].items() for c in cs}
    uni = [name_of.get(int(c), "Unclustered") for c in (X_clean @ np.load(TOPICS / "centroids.npy").T).argmax(1)]
    scored = [len(t.split()) >= clean["min_words"] for t in cleaned]

    def measures(idx: list[int]) -> dict:
        """Size-dependent measures on the dev rows idx."""
        texts = [dev[i]["text"] for i in idx]
        return {"mtld": mtld([t for x in texts for t in tokenize(x)]),
                "self_bleu": self_bleu([tokens(x) for x in texts]),
                "topics30": sum(1 for c in Counter(t30[i] for i in idx).values() if c >= 0.01 * len(idx)),
                "universal19": effective([uni[i] for i in idx if scored[i]]),
                "vendi": vendi(X_dev[idx].astype(np.float64))}

    def size_free(idx: list[int]) -> dict:
        """MSA share, dialectness and repeats on the dev rows idx."""
        keys = [dedup_key(dev[i]["text"]) for i in idx]
        rep = set(exact_duplicates(keys)) | set(near_duplicates_within(keys, 0.8, 5))
        return {"msa_share": float((dev_aldi[idx] < ALDI_CUT).mean()), "dialectness": float(dev_aldi[idx].mean()),
                "repeats": len(rep) / len(idx)}

    ref_runs = [measures(random.Random(s).sample(range(len(dev)), n)) for s in range(n_ref)]
    ref = {m: {"mean": statistics.mean(r[m] for r in ref_runs),
               "std": statistics.stdev(r[m] for r in ref_runs) if n_ref > 1 else 0.0} for m in ref_runs[0]}
    rows = {"dev_ref": {"name": f"EESA dev ({n}-text samples)", "n": len(dev), "samples": n_ref,
                        "class_shares": {c: sum(r["sentiment"] == c for r in dev) / len(dev) for c in CLASSES},
                        **size_free(list(range(len(dev)))), **{m: v["mean"] for m, v in ref.items()},
                        "std": {m: v["std"] for m, v in ref.items()}},
            "most_errors": {"name": "SG01-most-errors", "n": n,
                            "class_shares": {c: sum(r["sentiment"] == c for r in hard) / n for c in CLASSES},
                            **size_free(hard_rows), **measures(hard_rows)}}

    # Error clusters: E5 k-means on the set (cleaned text, as the topic lists).
    Xh = X_clean[hard_rows]
    kmE = KMeans(n_clusters=K_ERR, n_init=10, random_state=0).fit(Xh)
    cent = kmE.cluster_centers_ / np.linalg.norm(kmE.cluster_centers_, axis=1, keepdims=True)
    sims = (Xh * cent[kmE.labels_]).sum(1)
    clusters, md_txt = [], [f"# SG01-most-errors: E5 error clusters (k = {K_ERR})", "",
                            f"{n} EESA dev texts wrong in >= {MIN_WRONG}/84 EESA runs. Generated by "
                            "`python -m src.sentiment.most_errors_eesa`. Texts sorted by closeness to the cluster centre (sim).", ""]
    for c, size in Counter(kmE.labels_.tolist()).most_common():
        idx = [j for j in np.argsort(-sims) if kmE.labels_[j] == c]
        conf = Counter(f"{hard[j]['sentiment']}→{hard[j]['majority_wrong_pred']}" for j in idx)
        tops = Counter(uni[hard_rows[j]] if scored[hard_rows[j]] else "(under 5 words)" for j in idx)
        clusters.append({"cluster": c, "n": size, "gold_to_pred": dict(conf.most_common()), "universal_topics": dict(tops.most_common())})
        name = f": {cluster_names[c]}" if c in cluster_names else ""
        md_txt += [f"## Cluster E{c} ({size} texts){name}", "",
                   "Gold → prediction: " + ", ".join(f"{k} {v}" for k, v in conf.most_common()),
                   "Universal topics: " + ", ".join(f"{k} {v}" for k, v in tops.most_common()), "",
                   "| sim | Wrong | Gold → pred | Text |", "|---|---|---|---|"]
        md_txt += [f"| {sims[j]:.3f} | {hard[j]['wrong_runs']}/84 | {hard[j]['sentiment']} → {hard[j]['majority_wrong_pred']} | "
                   f"{hard[j]['text'].replace('|', '/').replace(chr(10), ' ')} |" for j in idx]
        md_txt.append("")
    (INSPECT / f"sg01_most_errors_eesa{sfx}_clusters.md").write_text("\n".join(md_txt), encoding="utf-8", newline="\n")
    # The set again, now with each text's cluster and type name (few-shot pool of SG05-EESA, D-034).
    with open(INSPECT / f"sg01_most_errors_eesa{sfx}.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for j, r in enumerate(hard):
            c = int(kmE.labels_[j])
            f.write(json.dumps(r | {"error_cluster": f"E{c}", "error_type": cluster_names.get(c)}, ensure_ascii=False) + "\n")

    res = {"min_wrong": MIN_WRONG, "of_runs": 84, "aldi_cutoff": ALDI_CUT, "k_errors": K_ERR, "rows": rows,
           "gold_to_pred": dict(Counter(f"{r['sentiment']}→{r['majority_wrong_pred']}" for r in hard).most_common()),
           "clusters": clusters, "e5_revision": e5_rev, "inputs": {"dev": sha256(DEV), "train": sha256(TRAIN)},
           "git_commit": git_commit(), "seconds": round(time.time() - t0)}
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".json").write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding="utf-8")

    def fmt(r: dict, m: str, f: str) -> str:
        """Value, with ± std for the reference row."""
        return format(r[m], f) + (f" ± {format(r['std'][m], f)}" if "std" in r else "")
    md = ["# SG01-most-errors quality", "", "Generated by `python -m src.sentiment.most_errors_eesa`. Do not edit by hand. "
          "Size-dependent columns: the reference row is the mean ± std over random same-size dev samples.", "",
          "| Dataset | Texts | NEG / NEU / POS | MSA share | Dialectness | MTLD | Self-BLEU | Topics (of 30) | Universal (topics of 19) | Vendi | Repeats |",
          "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows.values():
        cs = " / ".join(f"{r['class_shares'][c]:.0%}" for c in CLASSES)
        md.append(f"| {r['name']} | {r['n']:,} | {cs} | {r['msa_share']:.1%} | {r['dialectness']:.2f} | {fmt(r, 'mtld', '.0f')} | "
                  f"{fmt(r, 'self_bleu', '.3f')} | {fmt(r, 'topics30', '.1f')} | {fmt(r, 'universal19', '.1f')} | "
                  f"{fmt(r, 'vendi', '.1f')} | {r['repeats']:.1%} |")
    md += ["", "| Cluster | Texts | Gold → prediction | Universal topics |", "|---|---|---|---|"]
    md += [f"| E{c['cluster']} | {c['n']} | " + ", ".join(f"{k} {v}" for k, v in c["gold_to_pred"].items()) + " | "
           + ", ".join(f"{k} {v}" for k, v in c["universal_topics"].items()) + " |" for c in clusters]
    out.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(md))
    print(f"done in {res['seconds']}s")


if __name__ == "__main__":
    main()
