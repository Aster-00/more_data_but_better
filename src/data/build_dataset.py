"""Build the clean multi-label training set in one run: NADI tweet text + LahjatBERT labels.

Steps:
  1. read the NADI 2020/2021/2023 training TSVs and the LahjatBERT label CSV
  2. join labels to tweets through the tweet text, one record per unique text
  3. undo the double escaping of quoted NADI 2021 tweets
  4. replace links with URL and @mentions with USER (each step can be switched off)
  5. write the records and a statistics file (no tweet text in the stats)

No other normalization is applied: diacritics, letter variants, emoji, Latin script,
punctuation and stopwords are kept, because script and code-switching are
experimental factors. (LahjatBERT's preprocess.py removes all of these.)

Outputs:
  data/processed/nadi_lahjatbert.jsonl                text = cleaned, text_raw = original
  results/data_stats/nadi_lahjatbert_stats.json

Usage:
  python -m src.data.build_dataset
  python -m src.data.build_dataset --no-mentions
  python -m src.data.build_dataset --limit 300      # tiny-subset smoke test
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import re
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

# The 18 country-level dialects, in the order the MLADI leaderboard expects model outputs.
DIALECTS = [
    "Algeria", "Bahrain", "Egypt", "Iraq", "Jordan", "Kuwait", "Lebanon", "Libya",
    "Morocco", "Oman", "Palestine", "Qatar", "Saudi_Arabia", "Sudan", "Syria",
    "Tunisia", "UAE", "Yemen",
]
# Source name (as used in the LahjatBERT CSV) -> NADI training file name.
NADI_FILES = {
    "NADI2020": "NADI2020-TWT.tsv",
    "NADI2021": "NADI2021-TWT.tsv",
    "NADI2023": "NADI2023-TWT.tsv",
}
# ALDi bins used by LahjatBERT's curriculum (data_utils.ALDI_THRESHOLDS), highest first.
ALDI_BINS = [(0.77, "[0.77,1.00]"), (0.44, "[0.44,0.77)"), (0.11, "[0.11,0.44)"), (0.0, "[0.00,0.11)")]
# Groups for "number of valid dialects" in the statistics: (lowest, highest, name).
CARDINALITY_BUCKETS = [(0, 0, "0"), (1, 1, "1"), (2, 2, "2"), (3, 5, "3-5"),
                       (6, 11, "6-11"), (12, 17, "12-17"), (18, 18, "18")]

# Cleaning patterns. Links may be glued to the preceding word ("كذاpic.twitter.com/x"), so no \b.
URL_RE = re.compile(r"https?://\S+|(?:pic)?\.?twitter\.com/\S+|www\.\S+|\bhttps?\b(?:\s+t\b)?")
MENTION_RE = re.compile(r"@\w+")
MULTISPACE_RE = re.compile(r" {2,}")
# Cleaning step name -> (pattern to find, placeholder to put in its place).
CLEANING_STEPS = {"urls": (URL_RE, "URL"), "mentions": (MENTION_RE, "USER")}

# Statistics patterns (count both raw links/handles and the URL/USER placeholders).
ANY_URL_RE = re.compile(r"https?://\S+|pic\.twitter\.com/\S+|www\.\S+|\bURL\b")
ANY_MENTION_RE = re.compile(r"@\w+|\bUSER\b")
PLACEHOLDER_RE = re.compile(r"\b(?:USER|URL|NUM)\b")
LATIN_WORD_RE = re.compile(r"[A-Za-z]{3,}")
ARABIC_CHAR_RE = re.compile(r"[؀-ۿݐ-ݿࢠ-ࣿ]")
NON_ARABIC_LETTER_RE = re.compile(r"[پچژگکیەێۆڕڵےہٹڈ]")  # Persian / Kurdish / Urdu letters
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF☀-➿]")

# Allow very long fields so the csv module never rejects a row.
csv.field_size_limit(10_000_000)


@dataclass
class Tweet:
    """One row of a NADI training file, text exactly as stored in the file."""
    source: str
    tweet_id: str
    text: str
    country: str
    province: str | None


# ---------------------------------------------------------------- reading

def read_nadi(nadi_dir: Path, limit: int | None) -> list[Tweet]:
    """Read the three NADI training TSVs, keeping every field exactly as stored."""
    tweets: list[Tweet] = []
    for source, fname in NADI_FILES.items():
        # QUOTE_NONE: take each field literally; quote handling is done later in unescape_text.
        with open(nadi_dir / fname, encoding="utf-8", newline="") as f:
            reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
            next(reader)  # skip the header row
            for i, row in enumerate(reader):
                # Tiny-subset mode: stop after the first `limit` rows of each file.
                if limit is not None and i >= limit:
                    break
                # Every row needs at least id, text and country.
                if len(row) < 3:
                    raise ValueError(f"{fname}: malformed row {i + 2}: {len(row)} fields")
                # NADI 2020/2021 have a 4th column (province); NADI 2023 does not.
                province = row[3] if len(row) > 3 else None
                tweets.append(Tweet(source, row[0], row[1], row[2], province))
    return tweets


def read_labels(path: Path) -> list[dict]:
    """Read the LahjatBERT label CSV: key (nadi_source, train_id), ALDi score, 18 labels."""
    rows = []
    with open(path, encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            # Keep only what the join needs, converted to proper types.
            rows.append({
                "row_id": r["id"],
                "key": (r["nadi_source"], r["train_id"]),
                "aldi": float(r["aldi_score"]),
                "labels": [int(r[d]) for d in DIALECTS],
            })
    return rows


def read_dev(path: Path) -> tuple[list[str], dict[str, list[int]]]:
    """Read the MLADI dev set: sentences and 0/1 labels for the 8 dialects it covers."""
    # Read the header (sentence + dialect names) and all rows.
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)
        header = next(reader)
        rows = list(reader)
    # Column 0 is the sentence; every other column is one dialect with "y"/"n" values.
    texts = [r[0] for r in rows]
    labels = {d: [1 if r[i] == "y" else 0 for r in rows] for i, d in enumerate(header) if i > 0}
    return texts, labels


# ---------------------------------------------------------------- joining

def build_records(tweets: list[Tweet], label_rows: list[dict]) -> tuple[list[dict], dict]:
    """Join label rows to tweets through their text; return one record per unique text + join stats.

    LahjatBERT: their CSV has no text. When they created it, they gave each label row a
    train_id by searching the NADI files for the row's text and taking the first match
    (inferred from the data: that code is not in their repo, but all 320 repeated IDs are
    the first occurrence of their text, in file order 2020 -> 2021 -> 2023). So every copy of a
    repeated text points at the same ID (320 IDs repeated) and the other tweets look
    unlabelled (383). Wrong because joining on the ID alone loses or mismatches these.
    Fix: map each ID to its text, then group tweets and label rows by that text.
    Copies with different labels (21 texts) get a per-dialect majority vote, ties = valid.
    """
    # Look-up table: (source, tweet id) -> tweet text. Each ID belongs to exactly one tweet.
    key_to_text = {(t.source, t.tweet_id): t.text for t in tweets}

    # Group the tweets by text: tweets with identical text end up in the same list.
    tweets_by_text: dict[str, list[Tweet]] = defaultdict(list)
    for t in tweets:
        tweets_by_text[t.text].append(t)

    # Group the label rows by the text their ID points at; count IDs not found in NADI.
    labels_by_text: dict[str, list[dict]] = defaultdict(list)
    unmatched_label_rows = 0
    for r in label_rows:
        text = key_to_text.get(r["key"])
        if text is None:
            unmatched_label_rows += 1
        else:
            labels_by_text[text].append(r)

    # How often each ID occurs in the label file, and which tweets' IDs never occur (for stats).
    key_counts = Counter(r["key"] for r in label_rows)
    missing = [t for t in tweets if (t.source, t.tweet_id) not in key_counts]

    # Build one record per unique text.
    records, unlabelled, size_mismatch, conflicts = [], [], 0, 0
    for text, group in tweets_by_text.items():
        # Texts with no label row at all are skipped and their tweet IDs reported.
        lrows = labels_by_text.get(text, [])
        if not lrows:
            unlabelled.extend(f"{t.source}:{t.tweet_id}" for t in group)
            continue
        # Normally there is one label row per tweet; count the groups where that is not so.
        size_mismatch += len(lrows) != len(group)

        # Combine the label copies: per dialect, count the copies that say "valid";
        # valid if at least half say so (ties count as valid).
        n = len(lrows)
        votes = [sum(r["labels"][i] for r in lrows) for i in range(len(DIALECTS))]
        labels = {d: int(2 * v >= n) for d, v in zip(DIALECTS, votes)}
        # A conflict means the copies did not all agree on at least one dialect.
        conflict = any(0 < v < n for v in votes)
        conflicts += conflict
        aldis = [r["aldi"] for r in lrows]

        # The record: a stable ID from the text, the text, every original tweet with its
        # country/province, the combined labels and the mean ALDi of the copies.
        records.append({
            "text_id": "t" + hashlib.sha1(text.encode("utf-8")).hexdigest()[:16],
            "file_text": text,
            "source": "real",
            "origin": "NADI-train+LahjatBERT-labels",
            "nadi_refs": [{"source": t.source, "id": t.tweet_id, "country": t.country,
                           "province": t.province} for t in group],
            "countries": sorted({t.country for t in group}),
            "labels": labels,
            "cardinality": sum(labels.values()),
            "n_label_rows": n,
            "label_conflict": conflict,
            "aldi_score": round(statistics.fmean(aldis), 6),
        })

    # Join statistics: how the IDs, label rows and tweets matched up.
    join = {
        "label_rows": len(label_rows),
        "unique_keys": len(key_counts),
        "duplicate_keys": sum(c > 1 for c in key_counts.values()),
        "duplicate_key_copies": dict(sorted(Counter(c for c in key_counts.values() if c > 1).items())),
        "label_rows_by_source": dict(Counter(r["key"][0] for r in label_rows)),
        "label_rows_key_not_in_nadi": unmatched_label_rows,
        "nadi_tweets": len(tweets),
        "nadi_tweets_key_missing_from_labels": len(missing),
        "of_which_text_shared_with_other_tweet": sum(len(tweets_by_text[t.text]) > 1 for t in missing),
        "unique_texts": len(tweets_by_text),
        "unique_texts_labelled": len(records),
        "unlabelled_tweets": len(unlabelled),
        "unlabelled_tweet_ids": unlabelled,
        "groups_label_rows_ne_tweets": size_mismatch,
        "groups_with_label_conflict": conflicts,
    }
    return records, join


# ---------------------------------------------------------------- cleaning

def unescape_text(text: str) -> tuple[str, bool]:
    """Undo the double escaping of quoted tweets; return the text and whether it changed.

    NADI 2021 (365 tweets): tweets containing quotes were stored escaped twice, e.g.
    '\"\"\"مقتنعه ب جمله \\\"\" لكل فعل…\"\"\"'. LahjatBERT reads the file with pandas'
    default CSV parsing, which removes only the outer layer and leaves wrapping quotes and
    backslashes (\\") in the text. Wrong because those characters were never in the tweet.
    Fix: remove both layers (CSV quoting, then the wrapping quotes and \\" escapes).
    """
    # Only fields wrapped in quotes are escaped; everything else is returned unchanged.
    if len(text) < 2 or not (text.startswith('"') and text.endswith('"')):
        return text, False
    # Layer 1 (CSV): drop the outer quotes and turn "" back into ".
    inner = text[1:-1].replace('""', '"')
    # Layer 2: drop the second pair of wrapping quotes, then turn \" back into ".
    if len(inner) >= 2 and inner.startswith('"') and inner.endswith('"'):
        inner = inner[1:-1]
    return inner.replace('\\"', '"'), True


def clean_text(text: str, steps: list[str]) -> tuple[str, Counter]:
    """Replace links with URL and @mentions with USER; return the text and replacement counts.

    LahjatBERT (preprocess.py): removes punctuation (: / .) before its URL regex, so the
    regex never matches and links are deleted instead of becoming URL; it also has no
    pattern for pic.twitter.com/... or www.... links. NADI organizers: their own masking
    left ".twitter.com/x" fragments (after masking "@pic") and cut-off links ending in a
    bare "https" / "http t" (NADI 2023). Wrong because links stay in the text or vanish
    without a trace. Fix: one pattern for all these link forms, applied to the
    unmodified text, padded with spaces so links glued to a word become separate tokens.
    """
    # Run each enabled step; " URL " / " USER " are padded so glued links get split off.
    counts: Counter = Counter()
    for step in steps:
        pattern, token = CLEANING_STEPS[step]
        text, n = pattern.subn(f" {token} ", text)
        counts[step] += n
    # Remove the extra spaces the padding created (only if something was replaced).
    if counts:
        text = MULTISPACE_RE.sub(" ", text).strip()
    return text, counts


def apply_cleaning(records: list[dict], steps: list[str]) -> dict:
    """Set text_raw (unescaped) and text (cleaned) on every record; return cleaning stats."""
    totals: Counter = Counter()
    changed: Counter = Counter()
    unescaped = 0
    for r in records:
        # text_raw = the tweet as it was written (file escaping undone, nothing else changed).
        r["text_raw"], was_escaped = unescape_text(r.pop("file_text"))
        unescaped += was_escaped
        # text = text_raw with links and mentions replaced; record which steps were applied.
        r["text"], counts = clean_text(r["text_raw"], steps)
        r["cleaning"] = steps
        # Count replacements in total and the number of records each step changed.
        totals.update(counts)
        changed.update(s for s, n in counts.items() if n)
    # Different texts can become identical after cleaning (e.g. differing only in a link).
    text_counts = Counter(r["text"] for r in records)
    return {
        "steps": steps,
        "unescaped_quoted_texts": unescaped,
        "records_changed": dict(changed),
        "replacements": dict(totals),
        "texts_identical_after_cleaning": sum(c for c in text_counts.values() if c > 1),
        "distinct_texts_after_cleaning": len(text_counts),
    }


# ---------------------------------------------------------------- statistics

def sha256(path: Path) -> str:
    """SHA-256 of a file, to record which data version a run used."""
    # Read in 1 MB chunks so large files do not need to fit in memory.
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str | None:
    """Current git commit, or None outside a repository."""
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def summarize(values: list[float]) -> dict:
    """Mean, median, 95th percentile, min and max of a list of numbers."""
    if not values:
        return {}
    s = sorted(values)
    return {"mean": round(statistics.fmean(s), 2), "median": statistics.median(s),
            "p95": s[int(0.95 * (len(s) - 1))], "min": s[0], "max": s[-1]}


def text_stats(texts: list[str]) -> dict:
    """Length, link/mention, script and code-switching counts for a list of texts."""
    # Word counts, and a copy of each text without links and placeholders (for script checks).
    words = [len(t.split()) for t in texts]
    stripped = [PLACEHOLDER_RE.sub(" ", ANY_URL_RE.sub(" ", t)) for t in texts]
    # Share of letters that are Arabic script, per text (texts with no letters are skipped).
    arabic_share = []
    for t in stripped:
        letters = sum(c.isalpha() for c in t)
        if letters:
            arabic_share.append(len(ARABIC_CHAR_RE.findall(t)) / letters)
    # Each count is the number of texts with that property.
    return {
        "n": len(texts),
        "chars": summarize([len(t) for t in texts]),
        "words": summarize(words),
        "le_3_words": sum(w <= 3 for w in words),
        "with_url": sum(bool(ANY_URL_RE.search(t)) for t in texts),
        "with_raw_url": sum("http" in t or "pic.twitter.com" in t for t in texts),
        "with_mention": sum(bool(ANY_MENTION_RE.search(t)) for t in texts),
        "with_NUM": sum(bool(re.search(r"\bNUM\b", t)) for t in texts),
        "with_hashtag": sum("#" in t for t in texts),
        "with_emoji": sum(bool(EMOJI_RE.search(t)) for t in texts),
        "with_latin_word": sum(bool(LATIN_WORD_RE.search(t)) for t in stripped),
        "with_persian_kurdish_urdu_letters": sum(bool(NON_ARABIC_LETTER_RE.search(t)) for t in texts),
        "mostly_non_arabic_letters": sum(s < 0.5 for s in arabic_share),
        "no_letters_after_stripping": len(texts) - len(arabic_share),
    }


def aldi_bin(score: float) -> str:
    """Name of the LahjatBERT ALDi bin a score falls into."""
    # Bins are ordered highest first, so the first threshold reached is the right bin.
    for threshold, name in ALDI_BINS:
        if score >= threshold:
            return name
    return ALDI_BINS[-1][1]


def cardinality_bucket(k: int) -> str:
    """Name of the bucket for a number of valid dialects (0, 1, 2, 3-5, ...)."""
    for lo, hi, name in CARDINALITY_BUCKETS:
        if lo <= k <= hi:
            return name
    raise ValueError(k)


def nadi_stats(tweets: list[Tweet]) -> dict:
    """Per-file and cross-file statistics of the original single-label NADI data."""
    # Per file: size, countries, provinces, duplicates and text properties.
    per_file = {}
    texts_by_source: dict[str, set[str]] = {}
    for source in NADI_FILES:
        ts = [t for t in tweets if t.source == source]
        texts = [t.text for t in ts]
        texts_by_source[source] = set(texts)
        per_file[source] = {
            "rows": len(ts),
            "countries": dict(sorted(Counter(t.country for t in ts).items())),
            "n_provinces": len({t.province for t in ts if t.province}),
            "provinces_per_country": dict(sorted(Counter(
                c for c, _ in {(t.country, t.province) for t in ts if t.province}).items())),
            "duplicate_texts_within_file": len(texts) - len(set(texts)),
            "text": text_stats([unescape_text(t)[0] for t in texts]),
        }
    # Texts that appear in two files.
    sources = list(NADI_FILES)
    overlap = {f"{a}&{b}": len(texts_by_source[a] & texts_by_source[b])
               for i, a in enumerate(sources) for b in sources[i + 1:]}
    # Texts tweeted from more than one country.
    countries_by_text: dict[str, set[str]] = defaultdict(set)
    for t in tweets:
        countries_by_text[t.text].add(t.country)
    # Country counts over all three files together, and largest / smallest country ratio.
    pooled = Counter(t.country for t in tweets)
    return {
        "per_file": per_file,
        "cross_file_text_overlap": overlap,
        "pooled_countries": dict(sorted(pooled.items())),
        "pooled_imbalance_max_over_min": round(max(pooled.values()) / min(pooled.values()), 2),
        "texts_with_conflicting_country_labels": sum(len(c) > 1 for c in countries_by_text.values()),
    }


def label_stats(records: list[dict]) -> dict:
    """Statistics of the joined multi-label data; one unit = one unique text."""
    # Number of valid dialects per text, positives per dialect, records per bucket, ALDi bins.
    n = len(records)
    card = Counter(r["cardinality"] for r in records)
    per_dialect = {d: sum(r["labels"][d] for r in records) for d in DIALECTS}
    by_bucket: dict[str, list[dict]] = defaultdict(list)
    for r in records:
        by_bucket[cardinality_bucket(r["cardinality"])].append(r)
    bins = Counter(aldi_bin(r["aldi_score"]) for r in records)

    # Agreement with the original geolocation label: is the posting country marked valid?
    # Counted per tweet, and separately for texts with exactly one valid dialect.
    geo_total, geo_hit = Counter(), Counter()
    single_hit = single_total = 0
    for r in records:
        for ref in r["nadi_refs"]:
            geo_total[ref["country"]] += 1
            geo_hit[ref["country"]] += r["labels"].get(ref["country"], 0)
        if r["cardinality"] == 1:
            single_total += 1
            single_hit += any(r["labels"][c] for c in r["countries"])
    # Most common dialect pairs among texts valid in exactly two dialects.
    pairs = Counter("+".join(d for d in DIALECTS if r["labels"][d])
                    for r in records if r["cardinality"] == 2)

    def group_profile(group: list[dict]) -> dict:
        """ALDi and text profile of one cardinality group."""
        return {
            "n": len(group),
            "aldi_ge_0_5": sum(r["aldi_score"] >= 0.5 for r in group),
            "aldi_lt_0_11": sum(r["aldi_score"] < 0.11 for r in group),
            "le_3_words": sum(len(r["text"].split()) <= 3 for r in group),
            "with_persian_kurdish_urdu_letters": sum(bool(NON_ARABIC_LETTER_RE.search(r["text"]))
                                                     for r in group),
        }

    return {
        "unique_texts": n,
        "cardinality_histogram": dict(sorted(card.items())),
        "cardinality_buckets": {name: len(by_bucket[name]) for _, _, name in CARDINALITY_BUCKETS},
        "all_18": group_profile(by_bucket["18"]),
        "zero_labels": group_profile(by_bucket["0"]),
        "per_dialect_positive": per_dialect,
        "per_dialect_positive_rate": {d: round(v / n, 4) for d, v in per_dialect.items()},
        "aldi": summarize([r["aldi_score"] for r in records]),
        "aldi_bins": {name: bins.get(name, 0) for _, name in ALDI_BINS},
        "mean_aldi_by_cardinality_bucket": {
            name: round(statistics.fmean(r["aldi_score"] for r in g), 4) if g else None
            for _, _, name in CARDINALITY_BUCKETS for g in [by_bucket[name]]},
        "geo_label_marked_valid_rate": {
            c: round(geo_hit[c] / geo_total[c], 4) for c in sorted(geo_total)},
        "geo_label_marked_valid_rate_overall": round(sum(geo_hit.values()) / sum(geo_total.values()), 4),
        "single_label_agrees_with_geo_label": round(single_hit / single_total, 4) if single_total else None,
        "top_pairs_cardinality_2": dict(pairs.most_common(15)),
    }


def dev_stats(dev_path: Path, train_texts: set[str]) -> dict:
    """Statistics of the MLADI dev set, plus exact-overlap check against the training texts."""
    texts, labels = read_dev(dev_path)
    # Number of valid dialects per dev sentence (out of the 8 dialects the dev set covers).
    card = Counter(sum(labels[d][i] for d in labels) for i in range(len(texts)))
    return {
        "rows": len(texts),
        "dialects": list(labels),
        "per_dialect_positive": {d: sum(v) for d, v in labels.items()},
        "cardinality_histogram": dict(sorted(card.items())),
        # Any dev sentence also in training would leak evaluation data into training.
        "exact_overlap_with_training_texts": sum(t in train_texts for t in texts),
        "text": text_stats(texts),
    }


def print_summary(stats: dict) -> None:
    """Print the headline numbers (ASCII only, safe on the Windows console)."""
    j, lab, nadi, cl = stats["join"], stats["labels"], stats["nadi"], stats["cleaning"]
    print(f"NADI tweets: {j['nadi_tweets']}  unique texts: {j['unique_texts']}")
    print(f"Label rows: {j['label_rows']}  unique keys: {j['unique_keys']}  "
          f"duplicate keys: {j['duplicate_keys']}  keys not in NADI: {j['label_rows_key_not_in_nadi']}")
    print(f"Tweets whose key is missing from labels: {j['nadi_tweets_key_missing_from_labels']} "
          f"({j['of_which_text_shared_with_other_tweet']} share their text with another tweet)")
    print(f"Labelled unique texts: {j['unique_texts_labelled']}  unlabelled tweets: {j['unlabelled_tweets']}  "
          f"label conflicts: {j['groups_with_label_conflict']}  "
          f"group size mismatches: {j['groups_label_rows_ne_tweets']}")
    print(f"Cleaning {cl['steps']}: unescaped {cl['unescaped_quoted_texts']}  "
          f"changed {cl['records_changed']}  identical after cleaning {cl['texts_identical_after_cleaning']}")
    print(f"Cardinality buckets: {lab['cardinality_buckets']}")
    print(f"Geo label marked valid: {lab['geo_label_marked_valid_rate_overall']}  "
          f"single-label agrees with geo: {lab['single_label_agrees_with_geo_label']}")
    print(f"Pooled imbalance (max/min country): {nadi['pooled_imbalance_max_over_min']}  "
          f"texts with conflicting country labels: {nadi['texts_with_conflicting_country_labels']}")
    if "dev" in stats:
        print(f"Dev rows: {stats['dev']['rows']}  exact overlap with training: "
              f"{stats['dev']['exact_overlap_with_training_texts']}")


# ---------------------------------------------------------------- entry point

def parse_args() -> argparse.Namespace:
    """Command-line options: input/output paths, cleaning switches, tiny-subset limit."""
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--nadi-dir", type=Path, default=Path("MLADI/train"))
    p.add_argument("--labels", type=Path,
                   default=Path("LahjatBERT_-main/data/stage_1_and_gpt_with_ids.csv"))
    p.add_argument("--dev", type=Path, default=Path("MLADI/dev/NADI2024_subtask1_dev2.tsv"))
    p.add_argument("--out", type=Path, default=Path("data/processed/nadi_lahjatbert.jsonl"))
    p.add_argument("--stats-out", type=Path,
                   default=Path("results/data_stats/nadi_lahjatbert_stats.json"))
    p.add_argument("--no-urls", action="store_true", help="keep links as they are")
    p.add_argument("--no-mentions", action="store_true", help="keep @mentions as they are")
    p.add_argument("--limit", type=int, default=None,
                   help="tiny-subset mode: read only the first N tweets of each NADI file")
    return p.parse_args()


def main() -> None:
    """Read, join, clean, and write the dataset and its statistics."""
    # Options; the cleaning steps are all steps not switched off with --no-<step>.
    args = parse_args()
    steps = [s for s in CLEANING_STEPS if not getattr(args, f"no_{s}")]
    # Tiny-subset mode writes to separate ".limitN" files so real outputs are not overwritten.
    if args.limit is not None:
        args.out = args.out.with_name(args.out.stem + f".limit{args.limit}" + args.out.suffix)
        args.stats_out = args.stats_out.with_name(
            args.stats_out.stem + f".limit{args.limit}" + args.stats_out.suffix)

    # Read the inputs; in tiny-subset mode keep only label rows for the tweets that were read.
    tweets = read_nadi(args.nadi_dir, args.limit)
    label_rows = read_labels(args.labels)
    if args.limit is not None:
        loaded = {(t.source, t.tweet_id) for t in tweets}
        label_rows = [r for r in label_rows if r["key"] in loaded]

    # Join, then clean.
    records, join = build_records(tweets, label_rows)
    cleaning = apply_cleaning(records, steps)

    # Collect statistics plus provenance (code version, settings, exact input files).
    stats = {
        "provenance": {
            "git_commit": git_commit(),
            "python": platform.python_version(),
            "args": {k: str(v) for k, v in vars(args).items()},
            "input_sha256": {
                **{s: sha256(args.nadi_dir / f) for s, f in NADI_FILES.items()},
                "labels": sha256(args.labels),
            },
        },
        "nadi": nadi_stats(tweets),
        "join": join,
        "cleaning": cleaning,
        "labels": label_stats(records),
    }
    # Dev statistics, checking overlap against both the cleaned and the original text.
    if args.dev.exists():
        stats["dev"] = dev_stats(args.dev, {r["text"] for r in records} | {r["text_raw"] for r in records})

    # Write one JSON record per line (UTF-8, Arabic kept readable), then the statistics.
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    args.stats_out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.stats_out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

    print_summary(stats)
    print(f"Wrote {len(records)} records to {args.out} and stats to {args.stats_out}")


if __name__ == "__main__":
    sys.exit(main())
