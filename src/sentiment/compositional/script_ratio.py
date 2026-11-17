"""Latin-script share of a text and its 10-point bin (Stage 0 of the compositional pipeline).

Three methods, all after links, mentions and the USER / URL placeholders are removed:
  char_letters        Latin letters / (Arabic + Latin letters). The rule of src.sentiment.explore_eesa,
                      which produced the script-mix table in chron-EESA; digits never count.
  char_franco_digits  the same, but a digit inside a Latin word counts as a Latin letter (3ala, 7elw, co2).
                      Standalone numbers are ignored.
  token               Latin tokens / (Arabic + Latin tokens). A whitespace token belongs to the script with
                      more of its letters (tie: Arabic); tokens without letters are ignored.
Emojis, punctuation and the hashtag sign are never letters, so they are ignored by all three.

Bins are the ones of explore_eesa, centred on 0, 10, ..., 100: b0 = Latin 0-5%, b1 = 5-15%, ...,
b10 = 95-100%. A value exactly on an edge goes to the lower-Latin bin, as in explore_eesa.
"""
from __future__ import annotations

import re

from src.quality.measure import ARABIC_LETTER_RE, PLACEHOLDER_RE

METHODS = ("char_letters", "char_franco_digits", "token")
LATIN_LETTER_RE = re.compile(r"[A-Za-z]")
# A Latin word: a run of Latin letters and digits with at least one letter.
LATIN_WORD_RE = re.compile(r"[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*")
# Arabic letters only (no Arabic punctuation or digits); ARABIC_LETTER_RE covers whole Unicode blocks.
STRICT_ARABIC_RE = re.compile(r"[ء-غف-يٮ-ۓۺ-ۿݐ-ݿﭐ-ﮱﯓ-ﴽﹰ-ﻼ]")
BIN_LABELS = ["0-5", "5-15", "15-25", "25-35", "35-45", "45-55", "55-65", "65-75", "75-85", "85-95", "95-100"]


def strip_placeholders(text: str) -> str:
    """Text without links, mentions and USER / URL placeholders."""
    return PLACEHOLDER_RE.sub(" ", text)


def script_counts(text: str, method: str = "char_franco_digits", strict_arabic: bool = False) -> tuple[int, int]:
    """(Arabic units, Latin units) of a text; units are letters or tokens, by method."""
    t = strip_placeholders(text)
    arabic_re = STRICT_ARABIC_RE if strict_arabic else ARABIC_LETTER_RE
    if method == "char_letters":
        return len(arabic_re.findall(t)), len(LATIN_LETTER_RE.findall(t))
    if method == "char_franco_digits":
        return len(arabic_re.findall(t)), sum(len(w) for w in LATIN_WORD_RE.findall(t))
    if method == "token":
        ar_tokens = lat_tokens = 0
        for tok in t.split():
            ar = len(arabic_re.findall(tok))
            lat = sum(len(w) for w in LATIN_WORD_RE.findall(tok))
            if ar + lat == 0:
                continue
            if lat > ar:
                lat_tokens += 1
            else:
                ar_tokens += 1
        return ar_tokens, lat_tokens
    raise ValueError(f"unknown method {method!r}; use one of {METHODS}")


def latin_ratio(text: str, method: str = "char_franco_digits", strict_arabic: bool = False) -> float | None:
    """Latin share in [0, 1]; None if the text has no Arabic or Latin letter."""
    ar, lat = script_counts(text, method, strict_arabic)
    return lat / (ar + lat) if ar + lat else None


def latin_bin(ar: int, lat: int) -> int | None:
    """Bin 0..10 of the Latin share, from the two counts (integer arithmetic, no rounding error)."""
    total = ar + lat
    if total == 0:
        return None
    # explore_eesa: Arabic bin = int(10 * ar / total + 0.5); the Latin bin is its mirror.
    return 10 - min(10, (20 * ar + total) // (2 * total))


def ratio_bin(ratio: float) -> int:
    """Bin 0..10 of a Latin share given as a number (for generated text, where only the ratio is kept)."""
    return 10 - min(10, int(10 * (1 - ratio) + 0.5))


def merged_bin_label(b: int, merge_from: int) -> str:
    """Bin label for evaluation: bins from `merge_from` up are one group."""
    if b >= merge_from:
        return f"{BIN_LABELS[merge_from].split('-')[0]}-100"
    return BIN_LABELS[b]
