"""Input loading utilities for supported tabular files."""

from __future__ import annotations

import csv
import re
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
    load_notes: list[str]


def load_table(source: str | Path, *, sample: int | None = None) -> LoadedTable:
    """Load a CSV or TSV file into a DataFrame with light metadata."""
    path = Path(source)
    suffix = path.suffix.lower()
    delimiter = "\t" if suffix in {".tsv", ".tab"} else ","
    nrows = sample if sample and sample > 0 else None
    header_missing = _looks_headerless(path, delimiter=delimiter)
    dataframe = _read_delimited(path, delimiter=delimiter, nrows=nrows, header_missing=header_missing)
    file_size_bytes = path.stat().st_size
    sampled = nrows is not None
    row_count_estimate = len(dataframe)
    load_notes: list[str] = []
    if header_missing:
        load_notes.append("Column headers were not detected reliably; generated names like `col_0` were used.")
    return LoadedTable(
        dataframe=dataframe,
        filename=path.name,
        file_size_bytes=file_size_bytes,
        sampled=sampled,
        row_count_estimate=row_count_estimate,
        load_notes=load_notes,
    )


def _read_delimited(path: Path, *, delimiter: str, nrows: int | None, header_missing: bool) -> pd.DataFrame:
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    last_error: Exception | None = None
    for encoding in encodings:
        try:
            dataframe = pd.read_csv(
                path,
                sep=delimiter,
                nrows=nrows,
                encoding=encoding,
                header=None if header_missing else "infer",
            )
            if header_missing:
                dataframe.columns = [f"col_{index}" for index in range(len(dataframe.columns))]
            return dataframe
        except UnicodeDecodeError as exc:
            last_error = exc
    if last_error:
        raise last_error
    raise ValueError(f"Unable to read file: {path}")


def _looks_headerless(path: Path, *, delimiter: str) -> bool:
    try:
        with path.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle, delimiter=delimiter)
            first = next(reader, None)
            second = next(reader, None)
    except UnicodeDecodeError:
        return False

    if not first or not second or len(first) != len(second):
        return False

    first_score = sum(_cell_looks_like_data(cell) for cell in first)
    second_score = sum(_cell_looks_like_data(cell) for cell in second)
    identifierish = sum(_cell_looks_like_header(cell) for cell in first)

    return (
        first_score / len(first) >= 0.75
        and second_score / len(second) >= 0.75
        and identifierish / len(first) <= 0.4
    )


def _cell_looks_like_data(cell: str) -> bool:
    value = cell.strip()
    if not value:
        return False
    if _looks_numeric(value):
        return True
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return True
    if value.lower() in {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
        "male", "female", "true", "false", "yes", "no",
    }:
        return True
    return False


def _cell_looks_like_header(cell: str) -> bool:
    value = cell.strip()
    return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value))


def _looks_numeric(value: str) -> bool:
    return bool(re.fullmatch(r"-?\d+(?:\.\d+)?", value))
