"""Abstract backend interface for future AI narration support."""

from __future__ import annotations


class LLMBackend:
    """Minimal backend protocol for text generation."""

    name = "base"

    def complete(self, prompt: str) -> str:
        raise NotImplementedError
