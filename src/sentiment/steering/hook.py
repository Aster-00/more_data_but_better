"""Activation steering during generation: add a class vector to the residual stream of one layer.

The vector of each batch row is added to the output of one decoder layer, at response positions
only, because that is where the vectors were extracted (`extract.py`). That means the last prompt
position (it predicts the first response token) and every generated token. The other prompt
positions stay untouched, so the instruction is read normally.

Strength: unit vector * alpha * mean token norm of that layer, so alpha means the same on every
layer. `token_budget` stops steering after that many response tokens (None = the whole response).

`layer` follows the hidden_states order of the vectors: l = output of decoder layer l-1.

Usage:
  steerer = Steerer(gen.model, cfg["steering"])
  with steerer:
      steerer.set_rows(["neg", "pos", ...])     # one vector name per batch row
      gen.generate(...)
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import torch

from src.sentiment.steering.extract import decoder_layers


class Steerer:
    """Forward hook on one decoder layer that adds a per-row vector at response positions."""

    def __init__(self, model, cfg: dict) -> None:
        """Load the vectors of `cfg["vectors"]` at `cfg["layer"]` and scale them by `cfg["alpha"]`."""
        path = Path(cfg["vectors"])
        data = torch.load(path, weights_only=False)
        self.layers = decoder_layers(model)
        self.layer, self.alpha, self.budget = cfg["layer"], cfg["alpha"], cfg.get("token_budget")
        # Layer 0 is the embeddings and has no decoder layer to hook.
        if not 1 <= self.layer <= len(self.layers):
            raise ValueError(f"layer {self.layer} outside 1..{len(self.layers)}")
        scale = self.alpha * float(data["token_norm_mean"][self.layer])
        self.vectors = {n: modes[cfg["mode"]][self.layer].float() * scale
                        for n, modes in data["vectors"].items() if cfg["mode"] in modes}
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        self.scale = scale
        self.rows: torch.Tensor | None = None
        self.steps = 0
        self.handle = None

    def set_rows(self, names: list[str]) -> None:
        """Choose the vector of every batch row and restart the token budget."""
        self.rows = torch.stack([self.vectors[n] for n in names])      # [B, H]
        self.steps = 0

    def _hook(self, module, inputs, output):
        """Add the row vectors to the last position of this forward pass, within the token budget."""
        h = output[0] if isinstance(output, tuple) else output
        # Prefill (T > 1) and decoding (T = 1) both end at the position that predicts the next token.
        if self.rows is not None and (self.budget is None or self.steps < self.budget):
            h[:, -1, :] += self.rows.to(device=h.device, dtype=h.dtype)
        self.steps += 1
        return output

    def __enter__(self) -> "Steerer":
        """Register the hook; the output of decoder layer `layer - 1` is hidden_states[layer]."""
        self.handle = self.layers[self.layer - 1].register_forward_hook(self._hook)
        return self

    def __exit__(self, *exc) -> None:
        """Remove the hook, so the model is unsteered again."""
        self.handle.remove()
        self.handle, self.rows = None, None
