"""Build the universal topic pool: Arabic-script, human-written texts from every included dataset.

Inclusion rules and the dataset list: CLAUDE.md "Universal topic pool" (Ammar, 2026-10-28).
Each text is kept only if its script is Arabic (at least 70% Arabic letters, the row-8 rule of
src/quality/measure.py). Texts are stored unchanged; cleaning and the per-dataset cap are applied
later, by scripts/fit_topics.py (configs/quality/topics_universal_clean_k50.json).

Output (gitignored, since it holds the raw texts): data/topics/pool/universal_v1.jsonl with
text_id, source ("real"), dataset, file and text, plus a .meta.json with counts per dataset.

Usage:
  python scripts/build_topic_pool.py
  python scripts/build_topic_pool.py --limit 200      (tiny mode: first 200 rows per file, name gets _limit200)
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Callable, Iterator

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.data.build_dataset import git_commit  # noqa: E402
from src.data.xlsx import read_xlsx  # noqa: E402
from src.quality.measure import observed_script, script_features  # noqa: E402

csv.field_size_limit(2**31 - 1)
DS = Path("data/datasets")
OUT_DIR = Path("data/topics/pool")


# ---------------------------------------------------------------- readers (each yields raw texts)

def jsonl_texts(path: Path, field: str = "text") -> Iterator[str]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)[field]


def csv_texts(path: Path, column: str | int, delimiter: str = ",", encoding: str = "utf-8-sig",
              header: bool = True) -> Iterator[str]:
    """One column of a CSV/TSV, by name (with a header) or by index (without one)."""
    with open(path, encoding=encoding, newline="") as f:
        if header:
            for row in csv.DictReader(f, delimiter=delimiter):
                yield row.get(column) or ""
        else:
            for row in csv.reader(f, delimiter=delimiter):
                yield row[column] if len(row) > column else ""


def label_tab_texts(path: Path) -> Iterator[str]:
    """Lines of the form 'label<TAB>text' (arabic-sentiment-analysis tweets)."""
    with open(path, encoding="utf-8") as f:
        for line in f:
            parts = line.rstrip("\n").split("\t", 1)
            if len(parts) == 2:
                yield parts[1]


def aoc_batch_texts(path: Path) -> Iterator[str]:
    """AOC crowd batch: every HIT row holds Sentence1..Sentence12."""
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            for k, v in row.items():
                if k and re.fullmatch(r"Sentence\d+", k) and v:
                    yield v


def xlsx_texts(path: Path, column: str) -> Iterator[str]:
    """One named column of every sheet (sheets without that header are skipped)."""
    for rows in read_xlsx(path).values():
        if rows and column in rows[0]:
            i = rows[0].index(column)
            for r in rows[1:]:
                if len(r) > i:
                    yield r[i]


def alr_texts(path: Path) -> Iterator[str]:
    """ALR laptop reviews: <sentence><text> elements."""
    for t in ET.parse(path).getroot().iter("text"):
        yield t.text or ""


# ---------------------------------------------------------------- the included datasets (CLAUDE.md table)

def sources() -> list[tuple[str, Path, Callable[[Path], Iterator[str]]]]:
    """(dataset name = cap group, file, reader); order = first-come order for cross-dataset repeats."""
    sa, di, both = DS / "sa", DS / "di", DS / "both"
    out = [("D1", Path("data/processed/nadi_lahjatbert.jsonl"), jsonl_texts)]
    out += [("AOC-ALDi", di / "AOC-ALDi" / f"{s}.tsv", lambda p: csv_texts(p, "sentence", "\t"))
            for s in ("train", "dev", "test")]
    out.append(("AOC-batch2", di / "dialect-classification_batch2_2010-12-20"
                / "dialect-classification_batch2_2010-12-20.tsv", aoc_batch_texts))
    out.append(("QADI-test", di / "QADI-master" / "testset" / "QADI_test.txt",
                lambda p: csv_texts(p, 0, "\t", "utf-8", header=False)))
    # Bahraini part only: native-speaker translations. The file is Windows-1256, not UTF-8.
    out.append(("E_MSA_BDs-Bahraini", both / "E_MSA_BDs-PR-SA" / "Bahraini Dialects Dataset.csv",
                lambda p: csv_texts(p, "Review Text", ",", "cp1256")))
    out += [("ArSarcasm-v2", Path(f"data/processed/sentiment/arsarcasm_v2_{s}.jsonl"), jsonl_texts)
            for s in ("train", "dev")]   # test is evaluation data: never in a topic pool (D-011)
    out.append(("Arabic-100k-Reviews", sa / "Arabic 100k Reviews" / "ar_reviews_100k.tsv",
                lambda p: csv_texts(p, "text", "\t")))
    out.append(("ArSen-20", sa / "ArSen-20-main" / "data" / "ArSen-20_publish.csv", lambda p: csv_texts(p, "tweet")))
    out.append(("AJGT", sa / "Arabic-twitter-corpus-AJGT" / "AJGT.xlsx", lambda p: xlsx_texts(p, "Feed")))
    out.append(("AT-ODTSA", sa / "AT-ODTSA-main" / "AT-ODTSA_Dataset_RawDataV1-1.xlsx",
                lambda p: xlsx_texts(p, "نص التغريدة")))
    out += [("Mawqif", sa / "Mawqif-Arabic-Stance-main" / "Data" / f"Mawqif_AllTargets_{s}.csv",
             lambda p: csv_texts(p, "text")) for s in ("Train", "Test")]
    out += [("EESA", sa / "EESA-Corpus-main" / f"EESA-{s}.csv", lambda p: csv_texts(p, 0, header=False))
            for s in ("Train", "Dev", "Test")]
    out.append(("ALR", sa / "Arabic-Laptop-Reviews-ALR-Dataset-master" / "Arabic_Laptop_Reviews.xml", alr_texts))
    masc = both / "masc-master" / "MASC Corpus" / "MASC Corpus" / "Excel Format"
    out += [("MASC", masc / f, lambda p: xlsx_texts(p, "Text"))
            for f in ("MASC corpus - Main.xlsx", "MSAC corpus- Political.xlsx", "MSAC corpus- software.xlsx")]
    emb = sa / "ar-embeddings" / "datasets"
    out.append(("LABR", emb / "LABR-book-reviews.csv", lambda p: csv_texts(p, "txt")))
    out += [("ASTD+ArTwitter+QRCI", emb / "tweets" / f, lambda p: csv_texts(p, "txt"))
            for f in ("ASTD.csv", "ArTwitter.csv", "qrci.csv")]
    out += [("arabic-sentiment-analysis", p, label_tab_texts)
            for p in sorted((sa / "arabic-sentiment-analysis" / "arabic_tweets_tsv").rglob("*.tsv"))]
    large = sa / "large-arabic-sentiment-analysis-resouces" / "datasets"   # RES.csv = RES1 + RES2, so skipped
    out += [("ATT+HTL+MOV+PROD+RES", large / f, lambda p: csv_texts(p, "text"))
            for f in ("ATT.csv", "HTL.csv", "MOV.csv", "PROD.csv", "RES1.csv", "RES2.csv")]
    out += [("AfriSenti-arq+ary", sa / "afrisent-semeval-2023-main" / "data" / lang / f"{s}.tsv",
             lambda p: csv_texts(p, "tweet", "\t")) for lang in ("arq", "ary") for s in ("train", "dev", "test")]
    return out


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--limit", type=int, default=None, help="tiny mode: first N rows per file")
    args = p.parse_args()

    name = "universal_v1" + (f"_limit{args.limit}" if args.limit else "")
    out_path = OUT_DIR / f"{name}.jsonl"
    if out_path.exists():
        raise SystemExit(f"{out_path} exists; build a new version instead of overwriting")
    t0 = time.time()

    seen: set[str] = set()
    stats: dict[str, Counter] = {}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as out:
        for dataset, path, reader in sources():
            c = stats.setdefault(dataset, Counter())
            if not path.exists():
                raise FileNotFoundError(path)
            for i, text in enumerate(reader(path)):
                if args.limit is not None and i >= args.limit:
                    break
                c["rows"] += 1
                text = (text or "").strip()
                # Filters: empty, not Arabic script (row-8 rule), exact repeat of an earlier pool text.
                if not text:
                    c["empty"] += 1
                    continue
                if observed_script(script_features(text)) != "arabic":
                    c["not_arabic_script"] += 1
                    continue
                if text in seen:
                    c["repeat"] += 1
                    continue
                seen.add(text)
                c["kept"] += 1
                rec = {"text_id": f"{dataset}:{path.name}:{i}", "source": "real", "dataset": dataset,
                       "file": str(path).replace("\\", "/"), "text": text}
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")

    meta = {"git_commit": git_commit(), "limit": args.limit, "rules": "CLAUDE.md 'Universal topic pool'",
            "counts": {d: dict(c) for d, c in stats.items()}, "kept_total": len(seen),
            "seconds": round(time.time() - t0)}
    (OUT_DIR / f"{name}.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    for d, c in stats.items():
        print(f"{d:28s} rows {c['rows']:>7}  kept {c['kept']:>7}  not-arabic {c['not_arabic_script']:>6}  "
              f"repeat {c['repeat']:>6}  empty {c['empty']:>5}")
    print(f"{len(seen)} texts written to {out_path} ({time.time() - t0:.0f}s)")


if __name__ == "__main__":
    main()
