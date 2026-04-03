"""Rule-based semantic and text inference helpers."""

from __future__ import annotations

import math
import re
from typing import Any


SEMANTIC_RULES: list[tuple[str, str]] = [
    (r"(^id$|_id$|^id_)", "identifier"),
    (r"uuid|guid", "identifier"),
    (r"created_at|created_on|creation_date", "creation_timestamp"),
    (r"updated_at|modified_at|last_modified", "update_timestamp"),
    (r"(^date$|_date$|^date_)", "date"),
    (r"price|cost|amount|revenue|salary|wage|fee", "currency"),
    (r"discount|reduction", "discount"),
    (r"(^name$|first_name|last_name|full_name|user_name)", "name"),
    (r"email|e_mail|mail", "email"),
    (r"phone|mobile|tel|contact_number", "phone"),
    (r"(^age$|_age$|^age_)", "age"),
    (r"address|street|city|state|country|zip|postal", "address"),
    (r"lat(itude)?", "coordinate"),
    (r"lon(gitude)?|lng", "coordinate"),
    (r"status|state|stage|phase|condition", "status"),
    (r"category|type|kind|class|group", "category"),
    (r"flag|^is_|^has_|active|enabled|deleted", "boolean_flag"),
    (r"^target$|label|(^|_)y$|outcome|churn|default|fraud", "target_variable"),
    (r"score|rating|rank|probability|confidence", "score"),
]

PII_NAME_HINTS: list[tuple[str, str]] = [
    ("email", "email"),
    ("phone", "phone"),
    ("address", "address"),
    ("name", "name"),
    ("ssn", "ssn"),
]


def infer_semantic_type(name: str, dtype_display: str) -> str:
    lowered = name.lower()
    for pattern, semantic in SEMANTIC_RULES:
        if re.search(pattern, lowered):
            return semantic
    if dtype_display == "boolean":
        return "boolean_flag"
    if dtype_display == "datetime":
        return "date"
    return "unknown"


def infer_flags(column: dict[str, Any], row_count: int) -> dict[str, Any]:
    name = column["name"].lower()
    semantic_type = column["semantic_type"]
    return {
        "likely_id": semantic_type == "identifier" or name.endswith("_id") or name == "id",
        "likely_target": semantic_type == "target_variable",
        "likely_foreign_key": name.endswith("_id") and name != "id",
        "likely_computed": semantic_type == "currency" and any(token in name for token in ("total", "amount")),
        "high_nulls": column["null_pct"] >= 20.0,
        "very_high_nulls": column["null_pct"] >= 50.0,
        "all_unique": bool(row_count and column["unique_count"] == row_count),
        "constant": column["unique_count"] == 1,
        "possible_pii": infer_possible_pii(name, semantic_type),
        "mixed_type": column.get("mixed_type", False),
    }


def infer_possible_pii(name: str, semantic_type: str) -> bool:
    lowered = name.lower()
    if semantic_type in {"email", "phone", "address", "name"}:
        return True
    return any(hint in lowered for hint, _ in PII_NAME_HINTS)


def infer_dataset_summary(profile: dict[str, Any]) -> str:
    row_count = f"{profile['row_count']:,}"
    column_count = profile["column_count"]
    dates = [
        col for col in profile["columns"]
        if col["dtype_display"] == "datetime" and col.get("min_date") and col.get("max_date")
    ]
    ids = sum(1 for col in profile["columns"] if col["flags"]["likely_id"])
    null_rate = profile["overall_null_pct"]
    pieces = [
        f"Tabular dataset with {row_count} rows and {column_count} columns."
    ]
    if dates:
        date_col = dates[0]
        pieces.append(f"Covers values from {date_col['min_date']} to {date_col['max_date']} in `{date_col['name']}`.")
    if null_rate > 0:
        pieces.append(f"Overall null rate is {null_rate:.1f}%.")
    if ids:
        pieces.append(f"Includes {ids} identifier-like column{'s' if ids != 1 else ''}.")
    return " ".join(pieces)


def infer_column_description(column: dict[str, Any]) -> str:
    name = column["name"]
    semantic_type = column["semantic_type"]
    dtype_display = column["dtype_display"]
    null_pct = column["null_pct"]
    unique_count = column["unique_count"]
    flags = column["flags"]

    if flags["likely_id"]:
        if flags["likely_foreign_key"]:
            sentence = f"Identifier that likely links to a related `{name[:-3]}` record."
        else:
            sentence = "Unique identifier field."
    elif semantic_type == "creation_timestamp":
        sentence = _date_sentence("Creation timestamp", column)
    elif semantic_type == "update_timestamp":
        sentence = _date_sentence("Last update timestamp", column)
    elif semantic_type == "date":
        sentence = _date_sentence("Date field", column)
    elif semantic_type == "currency":
        sentence = _numeric_sentence(name, "Monetary value", column, include_money=True)
    elif semantic_type == "status":
        sentence = _categorical_sentence("Status field", column)
    elif semantic_type == "category":
        sentence = _categorical_sentence("Category-like field", column)
    elif semantic_type == "target_variable":
        sentence = _categorical_sentence("Likely target variable", column)
    elif semantic_type == "boolean_flag":
        sentence = _categorical_sentence("Boolean-style flag", column)
    elif dtype_display in {"integer", "float"}:
        sentence = _numeric_sentence(name, "Numeric field", column)
    elif dtype_display == "datetime":
        sentence = _date_sentence("Datetime field", column)
    elif dtype_display == "boolean":
        sentence = _categorical_sentence("Boolean field", column)
    elif dtype_display == "string":
        sentence = _string_sentence(column)
    else:
        sentence = "Purpose unclear from name alone."

    if null_pct > 0:
        sentence += f" {null_pct:.1f}% nulls."
    if flags["mixed_type"]:
        sentence += " Mixed value types detected."
    if flags["likely_computed"]:
        sentence += " May be derived from other fields."
    return sentence.strip()


def _numeric_sentence(name: str, lead: str, column: dict[str, Any], *, include_money: bool = False) -> str:
    min_value = column.get("min")
    max_value = column.get("max")
    if min_value is not None and max_value is not None and not any(_is_nan(v) for v in (min_value, max_value)):
        if include_money:
            return f"{lead}; ranges from {_fmt_money(min_value)} to {_fmt_money(max_value)}."
        return f"{lead}; ranges from {_fmt_number(min_value)} to {_fmt_number(max_value)}."
    return f"{lead}."


def _date_sentence(lead: str, column: dict[str, Any]) -> str:
    min_date = column.get("min_date")
    max_date = column.get("max_date")
    if min_date and max_date:
        return f"{lead}; spans {min_date} to {max_date}."
    return f"{lead}."


def _categorical_sentence(lead: str, column: dict[str, Any]) -> str:
    values = column.get("value_counts") or []
    if values:
        top_values = ", ".join(f"`{value}` ({pct:.0f}%)" for value, _, pct in values[:3])
        return f"{lead}; common values include {top_values}."
    return f"{lead} with {column['unique_count']} distinct values."


def _string_sentence(column: dict[str, Any]) -> str:
    unique_count = column["unique_count"]
    if unique_count <= 12 and column.get("value_counts"):
        return _categorical_sentence("Text field", column)
    avg_length = column.get("avg_length")
    if avg_length is not None and not _is_nan(avg_length):
        return f"Text field with {unique_count} distinct values; average length {avg_length:.1f} characters."
    return f"Text field with {unique_count} distinct values."


def _fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_number(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _is_nan(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)
