"""Optional narration layer reserved for future AI backends."""

from __future__ import annotations

from typing import Any


def narrate_profile(profile: dict[str, Any], *, backend: str | None = None) -> dict[str, Any]:
    """Return placeholder narration metadata for the current no-LLM release."""
    return {
        "backend": backend or "none",
        "dataset_description": None,
        "column_descriptions": {},
        "enabled": False,
        "profile": profile,
    }
