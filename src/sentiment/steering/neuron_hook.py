"""Neuron steering during generation: change chosen MLP neurons of each row's class (SNG runs).

A neuron's value is the down_proj input act_fn(gate) * up, the value whose statistics the neuron
lists were built from (`activations_real`, `select_neurons`). The neurons of the row's class are
changed at response positions only (last position of every forward pass), as in vector steering:

  scale       value * alpha                      (LAPE, Tang 2024 / Elozeiri 2026: amplify)
  fix_median  value = the neuron's class median  (AP, Kojima 2024)
  fix_mean    value = the neuron's class mean    (SNG09)
With `suppress_others`, the neurons of the other two classes are set to 0 first (SNG10).

Config block (`neuron_steering` in a generation config):
  neurons          path to neurons.pt of select_neurons
  method           lape | ap | random_lape | random_ap
  intervention     scale | fix_median | fix_mean
  alpha            for scale; `alpha_by_class` {NEG: .., NEU: .., POS: ..} overrides it per class
  max_neurons      optional: keep only the first N of each class list (matched count, SNG07);
                   an AP list keeps N/2 top and N/2 bottom neurons
  suppress_others  bool
  token_budget     None = the whole response
  by_sentiment     {NEG: NEG, ...}: which class list a requested sentiment uses

Usage:
  steerer = NeuronSteerer(gen.model, cfg["neuron_steering"])
  with steerer:
      steerer.set_rows(["NEG", "POS", ...])
      gen.generate(...)
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import torch

from src.sentiment.steering.extract import decoder_layers

CLASSES = ("NEG", "NEU", "POS")


def truncate(entry: dict, n: int | None) -> dict:
    """The first `n` neurons of a ranked list; AP lists keep n/2 of their top and n/2 of their bottom part."""
    if n is None or len(entry["layer"]) <= n:
        return entry
    if "part" in entry:
        keep = []
        for part, k in ((1, n - n // 2), (-1, n // 2)):
            keep += [i for i, p in enumerate(entry["part"].tolist()) if p == part][:k]
        keep = torch.tensor(sorted(keep))
    else:
        keep = torch.arange(n)
    return {k: v[keep] for k, v in entry.items()}


class NeuronSteerer:
    """Pre-hooks on down_proj of every layer that holds chosen neurons of any class."""

    def __init__(self, model, cfg: dict) -> None:
        """Load the class lists of `cfg["method"]` and the values the intervention needs."""
        path = Path(cfg["neurons"])
        data = torch.load(path, weights_only=False)
        self.layers = decoder_layers(model)
        self.cfg, self.budget = cfg, cfg.get("token_budget")
        self.intervention = cfg["intervention"]
        if self.intervention not in ("scale", "fix_median", "fix_mean"):
            raise ValueError(f"unknown intervention {self.intervention!r}")
        alpha = {c: cfg.get("alpha_by_class", {}).get(c, cfg.get("alpha", 1.0)) for c in CLASSES}
        stats = data["stats"]

        # Per class and layer: neuron indices and, for fix_*, the class's value of each neuron.
        self.plan: dict[str, dict[int, tuple[torch.Tensor, torch.Tensor | None]]] = {}
        self.counts = {}
        for ci, c in enumerate(CLASSES):
            entry = truncate(data["methods"][cfg["method"]][c], cfg.get("max_neurons"))
            self.counts[c] = int(len(entry["layer"]))
            per_layer = {}
            for lay in entry["layer"].unique().tolist():
                m = entry["layer"] == lay
                idx = entry["neuron"][m]
                val = None
                if self.intervention != "scale":
                    key = "median" if self.intervention == "fix_median" else "mean"
                    val = stats[key][ci, lay, idx].float()
                per_layer[lay] = (idx, val)
            self.plan[c] = per_layer
        self.alpha = alpha
        self.sha256 = hashlib.sha256(path.read_bytes()).hexdigest()
        self.rows: list[str] | None = None
        self.active, self.steps, self.handles = False, 0, []

    def set_rows(self, classes: list[str]) -> None:
        """Choose the class of every batch row and restart the token budget."""
        self.rows, self.steps = list(classes), 0

    def _count(self, module, inputs):
        """Once per forward pass (first decoder layer): is this pass still within the token budget?"""
        self.active = self.rows is not None and (self.budget is None or self.steps < self.budget)
        self.steps += 1

    def _hook(self, layer: int):
        def hook(module, inputs):
            if not self.active:
                return None
            x = inputs[0]
            for b, c in enumerate(self.rows):
                # The other classes' neurons are zeroed, except those that also belong to the row's own class.
                if self.cfg.get("suppress_others"):
                    own = self.plan[c][layer][0] if layer in self.plan[c] else torch.empty(0, dtype=torch.long)
                    for o in CLASSES:
                        if o != c and layer in self.plan[o]:
                            other = self.plan[o][layer][0]
                            other = other[~torch.isin(other, own)]
                            x[b, -1, other.to(x.device)] = 0
                if layer in self.plan[c]:
                    idx, val = self.plan[c][layer]
                    idx = idx.to(x.device)
                    if val is None:
                        x[b, -1, idx] = x[b, -1, idx] * self.alpha[c]
                    else:
                        x[b, -1, idx] = val.to(device=x.device, dtype=x.dtype)
            return None
        return hook

    def __enter__(self) -> "NeuronSteerer":
        """Register the budget counter and one pre-hook per layer that holds chosen neurons."""
        self.handles = [self.layers[0].register_forward_pre_hook(self._count)]
        used = sorted({lay for plan in self.plan.values() for lay in plan})
        for lay in used:
            self.handles.append(self.layers[lay].mlp.down_proj.register_forward_pre_hook(self._hook(lay)))
        return self

    def __exit__(self, *exc) -> None:
        """Remove all hooks, so the model is unsteered again."""
        for h in self.handles:
            h.remove()
        self.handles, self.rows, self.active = [], None, False
