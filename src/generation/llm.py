"""Shared loader and batched chat generation for the open-source generator LLMs.

Every generator (Fanar-1-9B, Gemma-2-9B, ALLaM-7B) is loaded the same way: 4-bit NF4
weights (bitsandbytes), bf16 compute, whole model on the GPU. Nothing is offloaded to the
CPU; if the model does not fit, loading fails loudly (CLAUDE.md: never fall back silently).

Usage (from other modules):
    gen = Generator("QCRI/Fanar-1-9B-Instruct", cache_dir=Path("F:/Thesis/models"))
    outputs = gen.generate([messages_1, messages_2], sampling, seed=42)
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from pathlib import Path

import torch
from jinja2.exceptions import TemplateError
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


@dataclass(frozen=True)
class Sampling:
    """Decoding settings; all of them are written into every synthetic record."""
    temperature: float = 1.0
    top_p: float = 0.95
    top_k: int = 50
    max_new_tokens: int = 64
    repetition_penalty: float = 1.0
    do_sample: bool = True

    def as_dict(self) -> dict:
        """Plain dict for JSON logging."""
        return asdict(self)


def vram_mib() -> dict:
    """Current and peak GPU memory (MiB) of this process, plus free memory on the card."""
    if not torch.cuda.is_available():
        return {}
    free, total = torch.cuda.mem_get_info()
    return {
        "allocated": round(torch.cuda.memory_allocated() / 2**20),
        "reserved": round(torch.cuda.memory_reserved() / 2**20),
        "peak_allocated": round(torch.cuda.max_memory_allocated() / 2**20),
        "peak_reserved": round(torch.cuda.max_memory_reserved() / 2**20),
        "card_free": round(free / 2**20),
        "card_total": round(total / 2**20),
    }


class Generator:
    """One causal LLM loaded in 4-bit, with batched chat-template generation."""

    def __init__(self, model_id: str, cache_dir: Path | None = None, device: str = "cuda",
                 quantization: str = "nf4", attn_implementation: str | None = None) -> None:
        """Load tokenizer and model. `quantization` is "nf4" (default) or "none" (bf16, for small models)."""
        if device != "cuda":
            raise ValueError("generators run on the GPU only; CPU generation of a 9B model is not supported")
        self.model_id, self.quantization = model_id, quantization
        kwargs = {"cache_dir": str(cache_dir)} if cache_dir else {}

        # Tokenizer: left padding so that batched prompts all end at the same position
        # (the model continues from the last token of every row).
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, **kwargs)
        self.tokenizer.padding_side = "left"
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Model: NF4 4-bit weights with double quantization, bf16 compute, everything on GPU 0.
        # device_map={"": 0} (not "auto") so that nothing is ever placed on the CPU.
        quant = None
        if quantization == "nf4":
            quant = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4",
                                       bnb_4bit_compute_dtype=torch.bfloat16,
                                       bnb_4bit_use_double_quant=True)
        elif quantization != "none":
            raise ValueError(f"unknown quantization {quantization!r}")
        torch.cuda.reset_peak_memory_stats()
        t0 = time.time()
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, quantization_config=quant, dtype=torch.bfloat16, device_map={"": 0},
            attn_implementation=attn_implementation, **kwargs)
        self.model.eval()
        self.load_seconds = round(time.time() - t0, 1)
        self.revision = getattr(self.model.config, "_commit_hash", None)
        self.system_role_supported = self._probe_system_role()

    def _probe_system_role(self) -> bool:
        """True if the chat template accepts a system message (Gemma-2 based models do not)."""
        try:
            self.tokenizer.apply_chat_template([{"role": "system", "content": "x"},
                                                {"role": "user", "content": "y"}], tokenize=False)
            return True
        except TemplateError:
            return False

    def render(self, messages: list[dict]) -> str:
        """Chat-template a message list into the prompt string the model is conditioned on.

        Gemma-2 (and Fanar, which is built on it) rejects a system role. Instead of dropping
        the instruction, it is merged into the first user turn so every generator sees the
        same wording; the rendered prompt is stored with each record, so this is traceable.
        """
        if messages and messages[0]["role"] == "system" and not self.system_role_supported:
            system, first_user = messages[0]["content"], messages[1]
            messages = [{"role": "user", "content": system + "\n\n" + first_user["content"]}] + messages[2:]
        # enable_thinking=False turns off Qwen3's reasoning block (<think>...</think>), which
        # would otherwise fill the token budget; templates without that variable ignore it.
        return self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True,
                                                  enable_thinking=False)

    @torch.no_grad()
    def generate(self, batch_messages: list[list[dict]], sampling: Sampling, seed: int,
                 max_prompt_tokens: int = 1024) -> list[dict]:
        """Generate one completion per message list; return prompt, raw output and timing per row."""
        prompts = [self.render(m) for m in batch_messages]
        # The template already adds the BOS token, so the tokenizer must not add a second one.
        enc = self.tokenizer(prompts, return_tensors="pt", padding=True, truncation=True,
                             max_length=max_prompt_tokens, add_special_tokens=False).to(self.model.device)

        # One seed per batch: the same (batch, seed) always gives the same text.
        torch.manual_seed(seed)
        t0 = time.time()
        out = self.model.generate(
            **enc, do_sample=sampling.do_sample, temperature=sampling.temperature,
            top_p=sampling.top_p, top_k=sampling.top_k, max_new_tokens=sampling.max_new_tokens,
            repetition_penalty=sampling.repetition_penalty, pad_token_id=self.tokenizer.pad_token_id)
        seconds = time.time() - t0

        # Strip the prompt (left-padded, so it is exactly the first `prompt_len` positions).
        prompt_len = enc["input_ids"].shape[1]
        new_tokens = out[:, prompt_len:]
        results = []
        for i in range(len(prompts)):
            ids = new_tokens[i]
            # Count only real generated tokens (padding after the end of sequence is excluded).
            n_new = int((ids != self.tokenizer.pad_token_id).sum())
            results.append({
                "prompt": prompts[i],
                "raw_output": self.tokenizer.decode(ids, skip_special_tokens=True),
                "new_tokens": n_new,
                "batch_seconds": round(seconds, 3),
                "batch_size": len(prompts),
            })
        return results
