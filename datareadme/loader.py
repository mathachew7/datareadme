"""Input loading utilities for supported tabular files."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass(slots=True)
class LoadedTable:
    dataframe: pd.DataFrame
    filename: str
    file_size_bytes: int
    sampled: bool
    row_count_estimate: int


def load_table(source: str | Path, *, sample: int | None = None) -> LoadedTable:
    """Load a CSV or TSV file into a DataFrame with light metadata."""
    path = Path(source)
    suffix = path.suffix.lower()
    delimiter = "\t" if suffix in {".tsv", ".tab"} else ","
    nrows = sample if sample and sample > 0 else None
    dataframe = _read_delimited(path, delimiter=delimiter, nrows=nrows)
    file_size_bytes = path.stat().st_size
    sampled = nrows is not None
    row_count_estimate = len(dataframe)
    return LoadedTable(
        dataframe=dataframe,
        filename=path.name,
        file_size_bytes=file_size_bytes,
        sampled=sampled,
        row_count_estimate=row_count_estimate,
    )


def _read_delimited(path: Path, *, delimiter: str, nrows: int | None) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            return pd.read_csv(path, sep=delimiter, nrows=nrows, encoding=encoding)
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise ValueError(f"Unable to read file: {path}")
