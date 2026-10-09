"""18-output classification head for decoder LLMs that transformers has no
`AutoModelForSequenceClassification` class for (Jais-2, Falcon-H1, Cohere / Aya in 5.18).

LastTokenClassifier reproduces what the library's *ForSequenceClassification classes do for
Qwen3 and Gemma-2 / Fanar: run the decoder body, take the hidden state of the last
non-padding token, and map it with a bias-free linear layer (`score`) to one logit per dialect.
So all five LLMs share the same head design; only how it is built differs.

The body is loaded in 4-bit and gets LoRA adapters (via peft); the head is a plain fp32
nn.Linear trained in full. Saving writes the LoRA adapter with peft and the head to
`score_head.pt` next to it.
"""
from __future__ import annotations

from pathlib import Path

import torch
from peft import (LoraConfig, PeftModel, get_peft_model, get_peft_model_state_dict,
                  prepare_model_for_kbit_training, set_peft_model_state_dict)
from transformers import AutoConfig, AutoModel
from transformers.modeling_outputs import SequenceClassifierOutput
from transformers.models.auto.modeling_auto import MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES

HEAD_FILE = "score_head.pt"


def needs_custom_head(name: str) -> bool:
    """True if transformers has no sequence-classification class for this architecture."""
    return AutoConfig.from_pretrained(name).model_type not in MODEL_FOR_SEQUENCE_CLASSIFICATION_MAPPING_NAMES


class LastTokenClassifier(torch.nn.Module):
    """Decoder body + linear head on the last non-padding token, returning `.logits` like HF models."""

    def __init__(self, body: torch.nn.Module, num_labels: int):
        super().__init__()
        self.body = body
        self.config = body.config
        # Bias-free, as in the library's sequence-classification heads; fp32 for a stable update.
        self.score = torch.nn.Linear(body.config.hidden_size, num_labels, bias=False,
                                     dtype=torch.float32, device="cuda")

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor, **_) -> SequenceClassifierOutput:
        hidden = self.body(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        # Position of the last real token in each row; works for left or right padding.
        last = attention_mask.shape[1] - 1 - attention_mask.flip(1).float().argmax(1)
        pooled = hidden[torch.arange(hidden.shape[0], device=hidden.device), last]
        return SequenceClassifierOutput(logits=self.score(pooled.float()))


def load_body(name: str, quant) -> torch.nn.Module:
    """Frozen 4-bit decoder body (no language-model head)."""
    return AutoModel.from_pretrained(name, quantization_config=quant, dtype=torch.bfloat16,
                                     device_map={"": 0})


def build_for_training(name: str, quant, lora: LoraConfig, num_labels: int) -> LastTokenClassifier:
    """4-bit body with LoRA adapters and gradient checkpointing, plus a fresh head."""
    body = prepare_model_for_kbit_training(load_body(name, quant), use_gradient_checkpointing=True)
    return LastTokenClassifier(get_peft_model(body, lora), num_labels)


def load_trained(name: str, quant, model_dir: Path, num_labels: int) -> LastTokenClassifier:
    """Fresh 4-bit body + saved LoRA adapter + saved head, for scoring."""
    model = LastTokenClassifier(PeftModel.from_pretrained(load_body(name, quant), model_dir), num_labels)
    model.score.load_state_dict(torch.load(model_dir / HEAD_FILE, map_location="cuda"))
    return model.eval()


def save(model: LastTokenClassifier, model_dir: Path) -> None:
    """Save the LoRA adapter (peft format) and the head."""
    model.body.save_pretrained(model_dir)
    torch.save(model.score.state_dict(), model_dir / HEAD_FILE)


def trainable_state(model: LastTokenClassifier) -> dict:
    """Adapter + head weights, for periodic checkpoints."""
    return {"lora": get_peft_model_state_dict(model.body), "score": model.score.state_dict()}


def load_trainable_state(model: LastTokenClassifier, state: dict) -> None:
    """Restore weights written by trainable_state."""
    set_peft_model_state_dict(model.body, state["lora"])
    model.score.load_state_dict(state["score"])
