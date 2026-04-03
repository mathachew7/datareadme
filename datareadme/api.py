"""Public APIs for profiling and rendering dataset documentation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from .loader import load_table
from .profiler import profile_dataframe
from .renderer import render_markdown


def profile(source: str | Path | pd.DataFrame, *, sample: int | None = None, title: str | None = None) -> dict[str, Any]:
    """Compute a profile dictionary from a file path or DataFrame."""
    if isinstance(source, pd.DataFrame):
        df = source.copy()
        filename = title or "dataframe"
        file_size_bytes = None
        sampled = False
        row_count_estimate = len(df)
    else:
        loaded = load_table(source, sample=sample)
        df = loaded.dataframe
        filename = title or loaded.filename
        file_size_bytes = loaded.file_size_bytes
        sampled = loaded.sampled
        row_count_estimate = loaded.row_count_estimate
    return profile_dataframe(
        df,
        filename=filename,
        file_size_bytes=file_size_bytes,
        sampled=sampled,
        row_count_estimate=row_count_estimate,
    )


def narrate(profile_data: dict[str, Any], *, llm: str | None = None) -> str:
    """Render a profile into Markdown. LLM support is reserved for later."""
    return render_markdown(profile_data, llm_enabled=bool(llm and llm != "none"))


def generate(
    source: str | Path | pd.DataFrame,
    *,
    output: str | Path | None = None,
    sample: int | None = None,
    title: str | None = None,
    llm: str | None = None,
) -> str:
    """Profile input data and return rendered Markdown."""
    profile_data = profile(source, sample=sample, title=title)
    markdown = narrate(profile_data, llm=llm)
    if output:
        save(markdown, output)
    return markdown


def save(content: str, destination: str | Path) -> None:
    """Persist rendered output to disk."""
    Path(destination).write_text(content, encoding="utf-8")
