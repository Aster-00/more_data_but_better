"""Scorer models shared by filtering and quality measurement: CAMeLBERT DID, ALDi, E5.

  DIDScorer("nadi")   CAMeL-Lab/bert-base-arabic-camelbert-mix-did-nadi (21 countries)
  DIDScorer("madar")  CAMeL-Lab/bert-base-arabic-camelbert-mix-did-madar-corpus26 (25 cities + MSA)
  ALDiScorer()        VARabi/Sentence-ALDi (regression, 0 = MSA ... 1 = fully dialectal)
  E5Embedder()        intfloat/multilingual-e5-large (normalized sentence embeddings)

Each DID prediction is mapped onto the 18 MLADI country labels. Labels outside the 18
(Djibouti, Mauritania, Somalia, MSA) map to None. MADAR has no city for Bahrain, Kuwait
or the UAE, so for those targets the MADAR scorer cannot confirm fidelity: callers get
`covered=False` and must not count it as a rejection.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import torch
from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer

from src.data.build_dataset import DIALECTS

DID_MODELS = {
    "nadi": "CAMeL-Lab/bert-base-arabic-camelbert-mix-did-nadi",
    "madar": "CAMeL-Lab/bert-base-arabic-camelbert-mix-did-madar-corpus26",
}
ALDI_MODEL = "VARabi/Sentence-ALDi"
E5_MODEL = "intfloat/multilingual-e5-large"

# NADI DID label -> MLADI label (identical names omitted; None = outside the 18).
NADI_LABEL_MAP = {"United_Arab_Emirates": "UAE", "Djibouti": None, "Mauritania": None, "Somalia": None}
# MADAR city code -> country (MSA -> None).
MADAR_CITY_MAP = {
    "ALE": "Syria", "ALG": "Algeria", "ALX": "Egypt", "AMM": "Jordan", "ASW": "Egypt", "BAG": "Iraq",
    "BAS": "Iraq", "BEI": "Lebanon", "BEN": "Libya", "CAI": "Egypt", "DAM": "Syria", "DOH": "Qatar",
    "FES": "Morocco", "JED": "Saudi_Arabia", "JER": "Palestine", "KHA": "Sudan", "MOS": "Iraq",
    "MSA": None, "MUS": "Oman", "RAB": "Morocco", "RIY": "Saudi_Arabia", "SAL": "Jordan",
    "SAN": "Yemen", "SFX": "Tunisia", "TRI": "Libya", "TUN": "Tunisia",
}


def _cache_kwargs(cache_dir: Path | None) -> dict:
    """from_pretrained kwargs for the local model cache."""
    return {"cache_dir": str(cache_dir)} if cache_dir else {}


class DIDScorer:
    """Dialect-identification classifier whose outputs are mapped onto the 18 MLADI countries."""

    def __init__(self, variant: str, cache_dir: Path | None = None, device: str = "cuda",
                 batch_size: int = 64, max_length: int = 128) -> None:
        """Load one CAMeLBERT DID variant ("nadi" or "madar") and build its label map."""
        self.variant, self.device, self.batch_size, self.max_length = variant, device, batch_size, max_length
        self.model_id = DID_MODELS[variant]
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, **_cache_kwargs(cache_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, **_cache_kwargs(cache_dir)).to(device).eval()
        # Raw model labels in output order, and each one's MLADI country (or None).
        self.raw_labels = [self.model.config.id2label[i] for i in range(self.model.config.num_labels)]
        mapping = NADI_LABEL_MAP if variant == "nadi" else MADAR_CITY_MAP
        self.label_to_country = [mapping.get(l, l if l in DIALECTS else None) for l in self.raw_labels]
        for raw, c in zip(self.raw_labels, self.label_to_country):
            if c is not None and c not in DIALECTS:
                raise ValueError(f"{variant}: label {raw} mapped to unknown country {c}")
        self.covered = {c for c in self.label_to_country if c is not None}

    @torch.no_grad()
    def probabilities(self, texts: list[str]) -> np.ndarray:
        """Softmax probabilities over the raw labels, (n x n_labels)."""
        out = []
        for start in range(0, len(texts), self.batch_size):
            enc = self.tokenizer(texts[start:start + self.batch_size], truncation=True, padding=True,
                                 max_length=self.max_length, return_tensors="pt").to(self.device)
            out.append(torch.softmax(self.model(**enc).logits.float(), dim=-1).cpu().numpy())
        return np.concatenate(out) if out else np.zeros((0, len(self.raw_labels)))

    def predict(self, texts: list[str]) -> list[dict]:
        """Per text: top raw label, its probability, the top country, and probability mass per country.

        MADAR has several cities per country, so a country's probability is the sum over its
        cities; the top country is the one with the largest summed mass.
        """
        probs = self.probabilities(texts)
        results = []
        for p in probs:
            by_country: dict[str, float] = {}
            for prob, c in zip(p, self.label_to_country):
                if c is not None:
                    by_country[c] = by_country.get(c, 0.0) + float(prob)
            top_i = int(p.argmax())
            top_country = max(by_country, key=by_country.get) if by_country else None
            results.append({
                "top_raw": self.raw_labels[top_i],
                "top_raw_prob": round(float(p[top_i]), 4),
                "top_country": top_country,
                "top_country_prob": round(by_country.get(top_country, 0.0), 4) if top_country else None,
                "by_country": {c: round(v, 4) for c, v in by_country.items()},
            })
        return results

    def is_covered(self, country: str) -> bool:
        """Whether this scorer has at least one label for the country."""
        return country in self.covered


class ALDiScorer:
    """Sentence-level Arabic Level of Dialectness (Keleg et al. 2023): regression in [0, 1]."""

    def __init__(self, cache_dir: Path | None = None, device: str = "cuda", batch_size: int = 64,
                 max_length: int = 128) -> None:
        """Load the Sentence-ALDi regression model."""
        self.device, self.batch_size, self.max_length = device, batch_size, max_length
        self.model_id = ALDI_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, **_cache_kwargs(cache_dir))
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_id, **_cache_kwargs(cache_dir)).to(device).eval()

    @torch.no_grad()
    def score(self, texts: list[str]) -> list[float]:
        """ALDi score per text, clipped to [0, 1] as in the authors' inference code."""
        scores = []
        for start in range(0, len(texts), self.batch_size):
            enc = self.tokenizer(texts[start:start + self.batch_size], truncation=True, padding=True,
                                 max_length=self.max_length, return_tensors="pt").to(self.device)
            logits = self.model(**enc).logits.float().squeeze(-1)
            scores.extend(torch.clamp(logits, 0.0, 1.0).cpu().tolist())
        return [round(s, 4) for s in scores]


class E5Embedder:
    """multilingual-e5-large sentence embeddings (mean pooling, L2-normalized), as the model card specifies."""

    def __init__(self, cache_dir: Path | None = None, device: str = "cuda", batch_size: int = 64,
                 max_length: int = 128, prefix: str = "query: ") -> None:
        """Load the encoder; `prefix` is the E5 instruction prefix ("query: " for symmetric tasks)."""
        self.device, self.batch_size, self.max_length, self.prefix = device, batch_size, max_length, prefix
        self.model_id = E5_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id, **_cache_kwargs(cache_dir))
        self.model = AutoModel.from_pretrained(self.model_id, **_cache_kwargs(cache_dir)).to(device).eval()
        if device == "cuda":
            self.model.half()

    @torch.no_grad()
    def embed(self, texts: list[str]) -> np.ndarray:
        """(n x 1024) float32 unit-length embeddings."""
        out = []
        for start in range(0, len(texts), self.batch_size):
            batch = [self.prefix + t for t in texts[start:start + self.batch_size]]
            enc = self.tokenizer(batch, truncation=True, padding=True, max_length=self.max_length,
                                 return_tensors="pt").to(self.device)
            hidden = self.model(**enc).last_hidden_state.float()
            # Mean over real tokens only (padding masked out), then unit length.
            mask = enc["attention_mask"].unsqueeze(-1).float()
            emb = (hidden * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            out.append(torch.nn.functional.normalize(emb, dim=-1).cpu().numpy())
        return np.concatenate(out) if out else np.zeros((0, 1024), dtype=np.float32)
