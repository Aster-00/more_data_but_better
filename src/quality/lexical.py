"""Lexical diversity measures on whitespace tokens: TTR, distinct-n, MTLD, Self-BLEU.

Tokens are whitespace-separated strings exactly as written (no Arabic normalization, no
punctuation stripping), so a word with and without a trailing comma counts as two types.
This is the explicit choice for this project: normalization would hide script and
code-switching differences, which are experimental factors.
"""
from __future__ import annotations

import math
from collections import Counter


def tokenize(text: str) -> list[str]:
    """Whitespace tokens, unchanged."""
    return text.split()


def ttr(tokens: list[str]) -> float:
    """Type-token ratio (depends on sample size; compare sets at equal size)."""
    return len(set(tokens)) / len(tokens) if tokens else 0.0


def ngrams(tokens: list[str], n: int) -> list[tuple[str, ...]]:
    """All n-grams of a token list."""
    return [tuple(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


def distinct_n(sentences: list[list[str]], n: int) -> float:
    """Distinct-n (Li et al. 2016): unique n-grams / total n-grams over the whole set."""
    total, seen = 0, set()
    for toks in sentences:
        grams = ngrams(toks, n)
        total += len(grams)
        seen.update(grams)
    return len(seen) / total if total else 0.0


def _mtld_one_direction(tokens: list[str], threshold: float) -> float:
    """MTLD factor count in one direction (McCarthy & Jarvis 2010)."""
    factors, types, count = 0.0, set(), 0
    for tok in tokens:
        count += 1
        types.add(tok)
        if len(types) / count <= threshold:
            factors += 1
            types, count = set(), 0
    # Partial last factor, weighted by how far its TTR dropped towards the threshold.
    if count:
        partial_ttr = len(types) / count
        factors += (1 - partial_ttr) / (1 - threshold) if partial_ttr < 1 else 0.0
    return len(tokens) / factors if factors else float(len(tokens))


def mtld(tokens: list[str], threshold: float = 0.72) -> float:
    """Measure of Textual Lexical Diversity: mean of forward and backward factor lengths."""
    if len(tokens) < 2:
        return 0.0
    return (_mtld_one_direction(tokens, threshold) + _mtld_one_direction(tokens[::-1], threshold)) / 2


def self_bleu(sentences: list[list[str]], max_n: int = 4) -> float:
    """Self-BLEU (Zhu et al. 2018): mean BLEU-4 of each sentence against all the others as references.

    Clipped counts use the maximum n-gram count over the other sentences. For each n-gram
    the two largest per-sentence counts are precomputed, so the maximum over "all others"
    is available in O(1) per n-gram instead of rebuilding references per hypothesis.
    Smoothing: add-epsilon (Chen & Cherry 2014, method 1) for zero precisions.
    Brevity penalty uses the closest reference length among the others. Higher = less diverse.
    """
    if len(sentences) < 2:
        return 0.0
    # For every n and n-gram: the top two (count, sentence index) pairs.
    top2: list[dict[tuple, list[tuple[int, int]]]] = [{} for _ in range(max_n + 1)]
    per_sentence_counts: list[list[Counter]] = []
    for i, toks in enumerate(sentences):
        counts_n = []
        for n in range(1, max_n + 1):
            c = Counter(ngrams(toks, n))
            counts_n.append(c)
            for g, cnt in c.items():
                lst = top2[n].get(g, [])
                lst.append((cnt, i))
                lst.sort(reverse=True)
                top2[n][g] = lst[:2]
        per_sentence_counts.append(counts_n)
    length_counts = Counter(len(t) for t in sentences)
    distinct_lengths = sorted(length_counts)

    scores = []
    for i, toks in enumerate(sentences):
        if not toks:
            continue
        log_prec = 0.0
        for n in range(1, max_n + 1):
            hyp = per_sentence_counts[i][n - 1]
            total = max(sum(hyp.values()), 1)
            clipped = 0
            for g, cnt in hyp.items():
                lst = top2[n][g]
                # Max count among the other sentences: skip the entry belonging to i.
                other = next((c for c, j in lst if j != i), 0)
                clipped += min(cnt, other)
            prec = clipped / total if clipped else 0.1 / total  # epsilon smoothing
            log_prec += math.log(prec) / max_n
        # Brevity penalty against the closest other sentence's length (ties -> shorter length,
        # as in sacrebleu); the hypothesis's own length counts only if another sentence shares it.
        h = len(toks)
        r = min((abs(l - h), l) for l in distinct_lengths if l != h or length_counts[h] > 1)[1]
        bp = 1.0 if h > r else math.exp(1 - r / h)
        scores.append(bp * math.exp(log_prec))
    return sum(scores) / len(scores) if scores else 0.0


def lexical_summary(texts: list[str]) -> dict:
    """All lexical measures for a list of texts."""
    sents = [tokenize(t) for t in texts]
    tokens = [tok for s in sents for tok in s]
    return {
        "n_texts": len(texts),
        "n_tokens": len(tokens),
        "vocab": len(set(tokens)),
        "mean_words": round(len(tokens) / len(texts), 2) if texts else 0.0,
        "ttr": round(ttr(tokens), 4),
        "distinct_1": round(distinct_n(sents, 1), 4),
        "distinct_2": round(distinct_n(sents, 2), 4),
        "mtld": round(mtld(tokens), 2),
        "self_bleu": round(self_bleu(sents), 4),
    }
