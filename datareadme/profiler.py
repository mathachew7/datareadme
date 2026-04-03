"""Profiling helpers that convert DataFrames into structured metadata."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pandas as pd
import re
from pandas.api.types import (
    is_bool_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
)

from .inferrer import infer_column_evidence, infer_flags, infer_semantic_type, refine_inferences_with_context


def profile_dataframe(
    df: pd.DataFrame,
    *,
    filename: str,
    file_size_bytes: int | None,
    sampled: bool,
    row_count_estimate: int,
    load_notes: list[str],
) -> dict[str, Any]:
    """Generate a serializable profile dictionary from a DataFrame."""
    columns = []
    total_null_count = int(df.isna().sum().sum())
    row_count = int(len(df))
    overall_cells = row_count * max(len(df.columns), 1)
    overall_null_pct = (total_null_count / overall_cells * 100) if overall_cells else 0.0

    for position, name in enumerate(df.columns):
        column_profile = _profile_column(df[name], position=position)
        columns.append(column_profile)

    for column in columns:
        column["inference"] = infer_column_evidence(column, row_count)
        column["semantic_type"] = column["inference"]["semantic_type"]
        column["role"] = column["inference"]["role"]

    refine_inferences_with_context(columns)

    money_column_count = sum(1 for column in columns if column["semantic_type"] == "money")
    for column in columns:
        column["flags"] = infer_flags(column, row_count, money_column_count=money_column_count)

    return {
        "filename": filename,
        "row_count": row_count,
        "row_count_estimate": row_count_estimate,
        "column_count": len(df.columns),
        "file_size_bytes": file_size_bytes,
        "duplicate_row_count": int(df.duplicated().sum()) if row_count else 0,
        "overall_null_count": total_null_count,
        "overall_null_pct": round(overall_null_pct, 1),
        "generation_timestamp": datetime.now(timezone.utc).isoformat(),
        "sampled": sampled,
        "load_notes": load_notes,
        "columns": columns,
    }


def _profile_column(series: pd.Series, *, position: int) -> dict[str, Any]:
    name = str(series.name)
    non_null = series.dropna()
    unique_count = int(non_null.nunique(dropna=True))
    row_count = len(series)
    null_count = int(series.isna().sum())
    null_pct = (null_count / row_count * 100) if row_count else 0.0
    dtype_display = _display_dtype(series)
    semantic_type = infer_semantic_type(name, dtype_display)
    mixed_type = _has_mixed_python_types(non_null)
    if dtype_display == "string":
        mixed_type = mixed_type or _has_mixed_value_patterns(non_null)

    profile: dict[str, Any] = {
        "name": name,
        "position": position,
        "dtype_raw": str(series.dtype),
        "dtype_display": dtype_display,
        "semantic_type": semantic_type,
        "null_count": null_count,
        "null_pct": round(null_pct, 1),
        "has_nulls": bool(null_count),
        "unique_count": unique_count,
        "unique_pct": round((unique_count / row_count * 100), 1) if row_count else 0.0,
        "is_unique": bool(row_count and unique_count == row_count),
        "is_constant": unique_count == 1 and row_count > 0,
        "sample_values": _sample_values(non_null),
        "mixed_type": mixed_type,
        "flags": {},
    }

    if is_numeric_dtype(series) and not is_bool_dtype(series):
        numeric = pd.to_numeric(non_null, errors="coerce")
        profile.update(
            {
                "min": _maybe_float(numeric.min()),
                "max": _maybe_float(numeric.max()),
                "mean": _maybe_float(numeric.mean()),
                "median": _maybe_float(numeric.median()),
                "std": _maybe_float(numeric.std()),
                "pct_negative": round(float((numeric < 0).mean() * 100), 1) if len(numeric) else 0.0,
                "pct_zero": round(float((numeric == 0).mean() * 100), 1) if len(numeric) else 0.0,
            }
        )
    elif _looks_datetime(series):
        datetimes = pd.to_datetime(non_null, errors="coerce")
        datetimes = datetimes.dropna()
        profile["dtype_display"] = "datetime"
        profile["semantic_type"] = infer_semantic_type(name, "datetime")
        profile.update(
            {
                "min_date": _fmt_date(datetimes.min()),
                "max_date": _fmt_date(datetimes.max()),
                "date_range_days": int((datetimes.max() - datetimes.min()).days) if len(datetimes) else None,
            }
        )
    else:
        as_text = non_null.astype(str)
        lengths = as_text.str.len()
        profile.update(
            {
                "min_length": int(lengths.min()) if len(lengths) else None,
                "max_length": int(lengths.max()) if len(lengths) else None,
                "avg_length": round(float(lengths.mean()), 1) if len(lengths) else None,
            }
        )
        if unique_count <= 12:
            counts = series.value_counts(dropna=True, normalize=False)
            profile["value_counts"] = [
                (str(value), int(count), round(count / row_count * 100, 1))
                for value, count in counts.head(5).items()
            ]
    return profile


def _display_dtype(series: pd.Series) -> str:
    if is_bool_dtype(series):
        return "boolean"
    if is_datetime64_any_dtype(series):
        return "datetime"
    if is_numeric_dtype(series):
        return "integer" if pd.api.types.is_integer_dtype(series) else "float"
    return "string"


def _looks_datetime(series: pd.Series) -> bool:
    if is_datetime64_any_dtype(series):
        return True
    non_null = series.dropna()
    if len(non_null) == 0 or len(non_null) > 0 and is_numeric_dtype(series):
        return False
    sample = non_null.astype(str).head(25)
    date_like_ratio = sample.str.contains(r"\d", regex=True).mean()
    separator_ratio = sample.str.contains(r"[-/:T]", regex=True).mean()
    month_name_ratio = sample.str.contains(
        r"\b(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)\b",
        flags=re.IGNORECASE,
        regex=True,
    ).mean()
    clock_ratio = sample.str.contains(r"\d{1,2}:\d{2}", regex=True).mean()
    iso_ratio = sample.str.contains(r"\d{4}-\d{2}-\d{2}", regex=True).mean()
    if (
        date_like_ratio < 0.8
        or (separator_ratio < 0.5 and month_name_ratio < 0.3 and clock_ratio < 0.3 and iso_ratio < 0.3)
    ):
        return False
    parsed = pd.to_datetime(sample, errors="coerce")
    return bool(len(parsed) and parsed.notna().mean() >= 0.7)


def _sample_values(series: pd.Series, *, max_items: int = 5) -> list[Any]:
    sample = series.head(max_items)
    values: list[Any] = []
    for value in sample.tolist():
        if hasattr(value, "isoformat"):
            values.append(value.isoformat())
        else:
            values.append(value)
    return values


def _has_mixed_python_types(series: pd.Series) -> bool:
    if len(series) == 0:
        return False
    type_names = {type(value).__name__ for value in series.head(100).tolist()}
    return len(type_names) > 1


def _has_mixed_value_patterns(series: pd.Series) -> bool:
    if len(series) == 0:
        return False
    sample = series.astype(str).head(100)
    numeric_like = sample.str.fullmatch(r"-?\d+(?:\.\d+)?").fillna(False)
    return bool(numeric_like.any() and (~numeric_like).any())


def _maybe_float(value: Any) -> float | None:
    if pd.isna(value):
        return None
    return float(value)


def _fmt_date(value: Any) -> str | None:
    if pd.isna(value):
        return None
    return pd.Timestamp(value).strftime("%Y-%m-%d")
