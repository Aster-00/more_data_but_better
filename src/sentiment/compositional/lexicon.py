"""Connective lexicon matching and the English-vs-Franco tag of Latin tokens (compositional pipeline).

Connectives (configs/sentiment/compositional/connectives.yaml): a text is "compound" if a lexicon entry
occurs in it as whole words, in the position the entry allows. This is a surface match: an ambiguous word
such as بس ("but" or "only") is counted either way, so the compound count is an upper bound.

Latin-token tag (a heuristic, to be checked by reading a sample):
  english   in the English word list (also after removing a plural, -ed, -ing or 's / n't ending)
  franco    has a Franco digit (2 3 5 6 7 8 9) among its letters, or is in the Franco list
  unknown   neither: names, brands, misspellings, joined words
  other     single letters and number-like tokens (4k, 10m, 2nd)
"""
from __future__ import annotations

import re
from pathlib import Path

import yaml

from src.sentiment.compositional.script_ratio import strip_placeholders

# Words for matching: Arabic letter runs (with diacritics) or Latin letter / digit runs with apostrophes.
WORD_RE = re.compile(r"[ء-غـ-ْٮ-ۓۺ-ۿ]+|[A-Za-z0-9]+(?:'[A-Za-z]+)*")
DIACRITICS_RE = re.compile(r"[ـً-ْ]")      # tatweel and tashkeel
LATIN_TOKEN_RE = re.compile(r"[A-Za-z0-9]*[A-Za-z][A-Za-z0-9]*(?:'[A-Za-z]+)*")
FRANCO_DIGIT_RE = re.compile(r"[2356789]")
NUMBER_LIKE_RE = re.compile(r"\d+(?:[.,]\d+)?(?:k|m|b|bn|gb|mb|kb|th|st|nd|rd|s|x|p|d|h|am|pm|fps|hd|min|sec|cm|km|kg)")


def words(text: str, strip_diacritics: bool = True) -> list[str]:
    """Lower-cased word tokens of a text (placeholders removed) for connective matching."""
    out = WORD_RE.findall(strip_placeholders(text))
    if strip_diacritics:
        out = [DIACRITICS_RE.sub("", w) for w in out]
    return [w.lower() for w in out if w]


def load_connectives(path: Path) -> list[dict]:
    """Lexicon entries, each with its words split (`tokens`)."""
    entries = yaml.safe_load(path.read_text(encoding="utf-8"))["connectives"]
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate connective id"
    for e in entries:
        e["tokens"] = e["text"].lower().split()
    return entries


def find_connectives(tokens: list[str], entries: list[dict], min_side: int = 2) -> list[dict]:
    """Lexicon entries found in a tokenised text, with their token span."""
    found = []
    for e in entries:
        n = len(e["tokens"])
        for i in range(len(tokens) - n + 1):
            if tokens[i:i + n] != e["tokens"]:
                continue
            before, after = i, len(tokens) - i - n
            # A joining connective needs a clause on each side; a subordinator or frame needs one after it.
            if e["position"] == "medial" and (before < min_side or after < min_side):
                continue
            if e["position"] == "any" and before + after < 2 * min_side:
                continue
            if e.get("later") and not any(w in tokens[i + n:] for w in e["later"]):
                continue
            found.append({"id": e["id"], "pattern": e["pattern"], "script": e["script"], "start": i, "end": i + n})
            break       # one hit per entry is enough
    return found


class LatinTagger:
    """English / Franco / unknown / other tag for every Latin-script token of a text."""

    def __init__(self, english_wordlist: Path, franco_lexicon: Path) -> None:
        self.english = {w.strip().lower() for w in english_wordlist.read_text(encoding="utf-8").split() if w.strip()}
        lex = yaml.safe_load(franco_lexicon.read_text(encoding="utf-8"))
        self.franco = set(lex["franco"])
        self.ambiguous = set(lex["ambiguous"])

    def is_english(self, w: str) -> bool:
        """In the English list, directly or after removing a common ending."""
        if w in self.english:
            return True
        base = re.sub(r"(?:n't|'s|'m|'re|'ve|'ll|'d)$", "", w)
        if base != w and base in self.english:
            return True
        w = w.replace("'", "")
        for end in ("s", "es", "ed", "d", "ing", "ly", "er", "est"):
            if w.endswith(end) and len(w) - len(end) >= 3 and w[:-len(end)] in self.english:
                return True
        return False

    def sure_tag(self, w: str) -> str:
        """Tag from the token alone; 'ambiguous' is settled by tag_text()."""
        letters = re.sub(r"[^a-z]", "", w)
        if w in self.franco:
            return "franco"
        if w in self.ambiguous:
            return "ambiguous"
        if re.search(r"\d", w):
            if NUMBER_LIKE_RE.fullmatch(w):
                return "other"
            # English word plus a number (covid19, furious9) before the Franco digit rule.
            if len(letters) >= 3 and letters in self.english and re.fullmatch(r"[a-z]+\d+", w):
                return "english"
            if len(letters) >= 2 and FRANCO_DIGIT_RE.search(w) and not re.search(r"[014]", w):
                return "franco"
            return "other"
        if len(letters) == 1:
            return "english" if w in ("i", "a", "u") else "other"
        return "english" if self.is_english(w) else "unknown"

    def tag_text(self, text: str) -> list[tuple[str, str]]:
        """(token, tag) for every Latin token of a text."""
        toks = [t.lower() for t in LATIN_TOKEN_RE.findall(strip_placeholders(text))]
        tags = [self.sure_tag(t) for t in toks]
        # Ambiguous words follow the rest of the text: Franco only next to sure Franco words.
        n_fr, n_en = tags.count("franco"), tags.count("english")
        as_franco = n_fr > 0 and n_fr >= n_en
        out = []
        for t, g in zip(toks, tags):
            if g == "ambiguous":
                g = "franco" if as_franco else ("english" if self.is_english(t) else "unknown")
            out.append((t, g))
        return out
