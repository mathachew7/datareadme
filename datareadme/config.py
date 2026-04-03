"""Configuration helpers for future project-level customization."""

from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_CONFIG: dict[str, Any] = {
    "llm": {"backend": "none", "model": None},
    "output": {"format": "markdown", "filename_template": "DATA_README.md"},
    "privacy": {"include_samples": True, "mask_pii": False},
    "thresholds": {"high_null_warning": 20, "very_high_null_warning": 50},
    "columns": {"exclude": [], "override_descriptions": {}},
}


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Return the default config until YAML loading is added."""
    _ = path
    return DEFAULT_CONFIG.copy()
