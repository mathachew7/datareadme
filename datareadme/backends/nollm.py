"""No-LLM backend used by the current MVP."""

from __future__ import annotations

from .base import LLMBackend


class NoLLMBackend(LLMBackend):
    """Backend that intentionally returns no generated text."""

    name = "none"

    def complete(self, prompt: str) -> str:
        _ = prompt
        return ""
