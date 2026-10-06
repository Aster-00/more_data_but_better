"""Exact and near-duplicate detection (MinHash + LSH over character shingles), no extra dependencies.

Near-duplicate = estimated Jaccard similarity of character n-gram shingle sets >= threshold.
MinHash signatures (num_perm universal hash functions) are indexed with LSH banding so
that only likely pairs are compared; every candidate pair is then verified with the exact
Jaccard of the shingle sets, so the reported similarity is exact, not an estimate.

Keys are built with `dedup_key`, which only lowercases Latin letters and collapses
whitespace. No Arabic normalization is applied (CLAUDE.md), so texts that differ only in
alef/yaa variants count as different for the exact check and as near-duplicates if their
shingles overlap enough.
"""
from __future__ import annotations

import re
from collections import defaultdict

import numpy as np

WS_RE = re.compile(r"\s+")
# Large Mersenne prime for the universal hash family h(x) = (a*x + b) mod p.
MERSENNE = (1 << 61) - 1
MAX_HASH = (1 << 32) - 1


def dedup_key(text: str) -> str:
    """Canonical form for duplicate checks: collapse whitespace, lowercase Latin letters only."""
    return WS_RE.sub(" ", text).strip().lower()


def shingles(key: str, n: int = 5) -> set[str]:
    """Character n-gram set of a key (whole key if shorter than n)."""
    if len(key) <= n:
        return {key}
    return {key[i:i + n] for i in range(len(key) - n + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    """Exact Jaccard similarity of two sets."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


class MinHasher:
    """MinHash signatures of shingle sets with `num_perm` seeded hash functions."""

    def __init__(self, num_perm: int = 128, seed: int = 1) -> None:
        """Draw the (a, b) parameters of the hash functions from a fixed seed."""
        rng = np.random.default_rng(seed)
        self.num_perm = num_perm
        self.a = rng.integers(1, MERSENNE, size=num_perm, dtype=np.uint64)
        self.b = rng.integers(0, MERSENNE, size=num_perm, dtype=np.uint64)

    def signature(self, shingle_set: set[str]) -> np.ndarray:
        """num_perm minimum hash values of the shingles (uint32)."""
        if not shingle_set:
            return np.full(self.num_perm, MAX_HASH, dtype=np.uint64)
        # Base hash of each shingle (Python's hash is salted per process, so use a stable one).
        base = np.array([stable_hash(s) for s in shingle_set], dtype=np.uint64)
        # All hash functions at once: (num_shingles x num_perm), then min over shingles.
        # Values are reduced mod the Mersenne prime via object arithmetic avoided: use uint64
        # wraparound on (a*x + b) which is still a valid universal-style family for our purpose.
        h = (base[:, None] * self.a[None, :] + self.b[None, :]) & np.uint64(MAX_HASH)
        return h.min(axis=0)


def stable_hash(s: str) -> int:
    """Deterministic 32-bit FNV-1a hash of a string (independent of PYTHONHASHSEED)."""
    h = 0x811C9DC5
    for byte in s.encode("utf-8"):
        h = ((h ^ byte) * 0x01000193) & 0xFFFFFFFF
    return h


class LSHIndex:
    """Banded LSH over MinHash signatures: items whose signatures agree on any band are candidates."""

    def __init__(self, num_perm: int = 128, bands: int = 16) -> None:
        """Split the signature into `bands` bands of num_perm // bands rows each."""
        if num_perm % bands:
            raise ValueError("num_perm must be divisible by bands")
        self.bands, self.rows = bands, num_perm // bands
        self.tables: list[dict[bytes, list[int]]] = [defaultdict(list) for _ in range(bands)]

    def _keys(self, sig: np.ndarray) -> list[bytes]:
        """One hashable key per band."""
        return [sig[b * self.rows:(b + 1) * self.rows].tobytes() for b in range(self.bands)]

    def add(self, item_id: int, sig: np.ndarray) -> None:
        """Index one signature."""
        for table, key in zip(self.tables, self._keys(sig)):
            table[key].append(item_id)

    def candidates(self, sig: np.ndarray) -> set[int]:
        """IDs of indexed items that share at least one band with the signature."""
        out: set[int] = set()
        for table, key in zip(self.tables, self._keys(sig)):
            out.update(table.get(key, ()))
        return out


def exact_duplicates(keys: list[str]) -> dict[int, int]:
    """Map each index to the first index with the same key (only for repeated keys)."""
    first: dict[str, int] = {}
    dup = {}
    for i, k in enumerate(keys):
        if k in first:
            dup[i] = first[k]
        else:
            first[k] = i
    return dup


def near_duplicates_within(keys: list[str], threshold: float = 0.8, n: int = 5, num_perm: int = 128,
                           bands: int = 16) -> dict[int, tuple[int, float]]:
    """For each index, the earliest earlier index it is a near-duplicate of (and the exact Jaccard).

    Items are processed in order, so the first occurrence of a cluster is kept and later
    members are marked. Exact duplicates are near-duplicates too (Jaccard 1.0).
    """
    hasher, index = MinHasher(num_perm), LSHIndex(num_perm, bands)
    sets = [shingles(k, n) for k in keys]
    marked: dict[int, tuple[int, float]] = {}
    for i, s in enumerate(sets):
        sig = hasher.signature(s)
        best = None
        for j in index.candidates(sig):
            sim = jaccard(s, sets[j])
            if sim >= threshold and (best is None or sim > best[1] or (sim == best[1] and j < best[0])):
                best = (j, sim)
        if best is not None:
            marked[i] = (best[0], round(best[1], 4))
        index.add(i, sig)
    return marked


def near_duplicates_against(keys: list[str], reference_keys: list[str], threshold: float = 0.8,
                            n: int = 5, num_perm: int = 128, bands: int = 16) -> dict[int, tuple[int, float]]:
    """For each key, the most similar reference key with exact Jaccard >= threshold (index, similarity)."""
    hasher, index = MinHasher(num_perm), LSHIndex(num_perm, bands)
    ref_sets = [shingles(k, n) for k in reference_keys]
    for j, s in enumerate(ref_sets):
        index.add(j, hasher.signature(s))
    matched: dict[int, tuple[int, float]] = {}
    for i, k in enumerate(keys):
        s = shingles(k, n)
        best = None
        for j in index.candidates(hasher.signature(s)):
            sim = jaccard(s, ref_sets[j])
            if sim >= threshold and (best is None or sim > best[1]):
                best = (j, sim)
        if best is not None:
            matched[i] = (best[0], round(best[1], 4))
    return matched
