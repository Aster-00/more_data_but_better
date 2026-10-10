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


def prepare_kbit(model: torch.nn.Module, embeddings_16bit: bool = False) -> torch.nn.Module:
    """Freeze the 4-bit model and enable gradient checkpointing (peft's k-bit preparation).

    peft.prepare_model_for_kbit_training (0.21.2) casts every non-4-bit 16-bit weight to fp32,
    including the input embedding table. Wrong for models with a very large vocabulary: Aya's
    256k x 4096 table grows from 2.1 to 4.2 GB, and the model no longer fits 8 GB. The table is
    frozen and was stored in 16-bit, so fp32 adds memory but no information. Fix (opt-in via
    `embeddings_16bit`): the same steps, except the input embedding table stays 16-bit.
    """
    if not embeddings_16bit:
        return prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)
    table = model.get_input_embeddings().weight
    for param in model.parameters():
        param.requires_grad = False
    for param in model.parameters():
        if (param is not table and param.dtype in (torch.float16, torch.bfloat16)
                and param.__class__.__name__ != "Params4bit"):
            param.data = param.data.to(torch.float32)
    torch.cuda.empty_cache()
    model.enable_input_require_grads()
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={})
    return model


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


def build_for_training(name: str, quant, lora: LoraConfig, num_labels: int,
                       embeddings_16bit: bool = False) -> LastTokenClassifier:
    """4-bit body with LoRA adapters and gradient checkpointing, plus a fresh head."""
    body = prepare_kbit(load_body(name, quant), embeddings_16bit)
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
