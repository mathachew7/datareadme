"""Signal-based inference helpers for generic dataset documentation."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any


NAME_TOKEN_GROUPS: dict[str, set[str]] = {
    "identifier": {"id", "uuid", "guid", "identifier"},
    "entity_key": {"subject", "participant", "respondent", "customer", "user", "patient", "member"},
    "temporal": {"date", "timestamp", "created", "updated", "modified", "submitted"},
    "temporal_cycle": {"year", "month", "day", "week", "quarter", "season", "hour", "time", "timepoint"},
    "longitude": {"longitude", "lon", "lng", "long"},
    "latitude": {"latitude", "lat"},
    "money": {"price", "cost", "amount", "revenue", "salary", "wage", "fee", "value", "bill", "fare", "tip", "toll", "tolls", "spending", "expense", "expenses", "premium", "losses"},
    "income": {"income", "earnings"},
    "payment_method": {"payment"},
    "status": {"status", "stage", "phase", "condition"},
    "category": {"category", "type", "kind", "class", "group", "segment"},
    "target": {"target", "label", "outcome", "churn", "default", "fraud"},
    "score": {"score", "rating", "rank", "probability", "confidence"},
    "count": {"count", "num", "number", "qty", "quantity", "rooms", "bedrooms", "population", "households", "passengers"},
    "age": {"age"},
    "measurement": {"length", "width", "depth", "height", "weight", "mass", "magnitude", "diameter", "radius", "distance", "speed", "pulse", "pressure", "temperature"},
    "unit": {"mm", "cm", "m", "km", "g", "kg", "lb", "lbs", "oz"},
    "measurement_name": {"carat", "expectancy", "precipitation", "wind", "horsepower", "acceleration", "displacement"},
    "location": {"city", "state", "country", "region", "postal", "zip", "airport", "port", "ocean"},
    "contact": {"email", "phone", "address", "ssn"},
    "code": {"code", "sku", "abbr", "abbrev", "iata", "icao", "iso"},
    "text": {"comment", "description", "notes", "message", "text", "summary"},
}

YES_NO_VALUES = {"yes", "no", "y", "n", "true", "false", "t", "f", "0", "1"}


def infer_semantic_type(name: str, dtype_display: str) -> str:
    """Provide a lightweight name-based semantic hint before full inference."""
    tokens = set(_tokenize(name))
    if NAME_TOKEN_GROUPS["longitude"] & tokens:
        return "longitude"
    if NAME_TOKEN_GROUPS["latitude"] & tokens:
        return "latitude"
    if NAME_TOKEN_GROUPS["identifier"] & tokens:
        return "identifier"
    if NAME_TOKEN_GROUPS["entity_key"] & tokens:
        return "entity_key"
    if NAME_TOKEN_GROUPS["temporal"] & tokens:
        return "datetime"
    if NAME_TOKEN_GROUPS["temporal_cycle"] & tokens:
        return "temporal_cycle"
    if NAME_TOKEN_GROUPS["money"] & tokens:
        return "money"
    if NAME_TOKEN_GROUPS["income"] & tokens:
        return "money"
    if NAME_TOKEN_GROUPS["target"] & tokens:
        return "target"
    if NAME_TOKEN_GROUPS["status"] & tokens:
        return "status"
    if NAME_TOKEN_GROUPS["score"] & tokens:
        return "score"
    if NAME_TOKEN_GROUPS["payment_method"] & tokens and dtype_display == "string":
        return "payment_method"
    if NAME_TOKEN_GROUPS["contact"] & tokens:
        overlap = NAME_TOKEN_GROUPS["contact"] & tokens
        return next(iter(sorted(overlap)))
    if tokens == {"name"} or {"first", "name"} <= tokens or {"last", "name"} <= tokens:
        return "name"
    if dtype_display == "boolean":
        return "boolean_flag"
    if dtype_display == "datetime":
        return "datetime"
    return "unknown"


def infer_column_evidence(column: dict[str, Any], row_count: int) -> dict[str, Any]:
    """Infer a generic role and semantic label from mixed name/statistical signals."""
    name = column["name"]
    lowered = name.lower()
    tokens = set(_tokenize(name))
    candidates: dict[tuple[str, str], float] = defaultdict(float)
    reasons: dict[tuple[str, str], list[str]] = defaultdict(list)

    def add(role: str, semantic: str, score: float, reason: str) -> None:
        key = (role, semantic)
        candidates[key] += score
        reasons[key].append(reason)

    dtype_display = column["dtype_display"]
    unique_pct = column["unique_pct"]
    value_counts = column.get("value_counts") or []
    avg_length = column.get("avg_length")

    if dtype_display == "datetime":
        add("temporal", "datetime", 0.95, "datetime dtype")
    if NAME_TOKEN_GROUPS["temporal"] & tokens:
        overlap = sorted(NAME_TOKEN_GROUPS["temporal"] & tokens)
        add("temporal", "datetime", 0.7, f"name suggests time ({', '.join(overlap)})")
    if NAME_TOKEN_GROUPS["temporal_cycle"] & tokens:
        overlap = sorted(NAME_TOKEN_GROUPS["temporal_cycle"] & tokens)
        add("temporal", "temporal_cycle", 0.85, f"name suggests calendar cycle ({', '.join(overlap)})")
    if NAME_TOKEN_GROUPS["longitude"] & tokens:
        add("location", "longitude", 0.95, "longitude-style token")
    if NAME_TOKEN_GROUPS["latitude"] & tokens:
        add("location", "latitude", 0.95, "latitude-style token")
    if NAME_TOKEN_GROUPS["identifier"] & tokens:
        add("identifier", "identifier", 0.8, "identifier-style token")
    if NAME_TOKEN_GROUPS["entity_key"] & tokens:
        add("identifier", "entity_key", 0.75, "subject/respondent-style token")
    if lowered.startswith("unnamed") and dtype_display in {"integer", "float"}:
        add("descriptor", "index_like", 0.95, "looks like exported index column")
    if lowered.endswith("_id") or lowered == "id":
        add("identifier", "identifier", 0.95, "id naming convention")
    if unique_pct >= 95 and dtype_display == "string" and avg_length is not None and avg_length >= 6:
        add("identifier", "identifier", 0.5, "nearly all values unique")
    if NAME_TOKEN_GROUPS["contact"] & tokens:
        for semantic in sorted(NAME_TOKEN_GROUPS["contact"] & tokens):
            add("descriptor", semantic, 0.85, f"name suggests {semantic}")
    if NAME_TOKEN_GROUPS["status"] & tokens:
        add("category", "status", 0.85, "status-style token")
    if NAME_TOKEN_GROUPS["payment_method"] & tokens and dtype_display == "string":
        add("category", "payment_method", 0.95, "payment-method style token")
    if NAME_TOKEN_GROUPS["category"] & tokens:
        add("category", "category", 0.75, "category-style token")
    if NAME_TOKEN_GROUPS["target"] & tokens:
        add("target", "target", 0.9, "target-style token")
    if NAME_TOKEN_GROUPS["score"] & tokens:
        add("measure", "score", 0.85, "score-style token")
    if NAME_TOKEN_GROUPS["money"] & tokens:
        add("measure", "money", 0.85, "money/value-style token")
    if NAME_TOKEN_GROUPS["income"] & tokens:
        add("measure", "money", 0.75, "income-style token")
    if NAME_TOKEN_GROUPS["measurement"] & tokens or NAME_TOKEN_GROUPS["unit"] & tokens or NAME_TOKEN_GROUPS["measurement_name"] & tokens:
        add("measure", "measurement", 0.8, "measurement/unit-style token")
    if (NAME_TOKEN_GROUPS["count"] & tokens) and not (
        NAME_TOKEN_GROUPS["money"] & tokens or NAME_TOKEN_GROUPS["income"] & tokens or NAME_TOKEN_GROUPS["measurement"] & tokens
    ):
        add("measure", "count", 0.7, "count-style token")
    if NAME_TOKEN_GROUPS["age"] & tokens:
        add("measure", "age", 0.7, "age-style token")
    if NAME_TOKEN_GROUPS["code"] & tokens:
        add("descriptor", "code", 0.7, "code-style token")
    if NAME_TOKEN_GROUPS["location"] & tokens:
        add("descriptor", "location_label", 0.7, "location-style token")
    if NAME_TOKEN_GROUPS["text"] & tokens:
        add("text", "free_text", 0.8, "free-text style token")

    if dtype_display == "boolean":
        add("category", "boolean_flag", 0.95, "boolean dtype")
    elif dtype_display == "string":
        if _looks_payment_method_values(value_counts):
            add("category", "payment_method", 0.9, "values look like payment methods")
        if _looks_month_name_cycle(value_counts):
            add("temporal", "temporal_cycle", 0.9, "values look like month names")
        if value_counts and len(value_counts) <= 12:
            add("category", "category", 0.65, "low-cardinality text values")
        if avg_length is not None and avg_length >= 25:
            add("text", "free_text", 0.7, "long average text length")
        if unique_pct >= 60:
            add("descriptor", "text_label", 0.45, "many distinct text values")
        if _looks_yes_no(value_counts):
            add("category", "boolean_flag", 0.75, "yes/no style values")
    elif dtype_display in {"integer", "float"}:
        if _looks_year_range(column):
            add("temporal", "temporal_cycle", 0.9, "numeric range looks like years")
        if _is_score_range(column):
            add("measure", "score", 0.35, "bounded score-like range")
        if dtype_display == "integer" and _is_count_like(column):
            add("measure", "count", 0.4, "non-negative count-like numeric range")
        add("measure", "numeric", 0.35, "numeric dtype")

    if not candidates:
        if dtype_display in {"integer", "float"}:
            add("measure", "numeric", 0.3, "fallback numeric interpretation")
        elif dtype_display == "string":
            add("descriptor", "text_label", 0.3, "fallback text interpretation")
        else:
            add("descriptor", "unknown", 0.2, "fallback interpretation")

    winner = max(candidates.items(), key=lambda item: item[1])[0]
    score = candidates[winner]
    role, semantic = winner
    confidence = "high" if score >= 0.9 else "medium" if score >= 0.55 else "low"
    return {
        "role": role,
        "semantic_type": semantic,
        "confidence": confidence,
        "confidence_score": round(score, 2),
        "tokens": sorted(tokens),
        "reasons": reasons[winner],
    }


def refine_inferences_with_context(columns: list[dict[str, Any]]) -> None:
    """Adjust ambiguous column meanings using lightweight dataset-level context."""
    money_columns = sum(1 for column in columns if column["semantic_type"] == "money")
    for column in columns:
        evidence = column["inference"]
        tokens = set(evidence.get("tokens", []))
        values = column.get("value_counts") or []

        if evidence["semantic_type"] == "payment_method":
            if "payment" not in tokens and not _looks_payment_method_values(values):
                _apply_refined_inference(
                    column,
                    role="category",
                    semantic_type="category",
                    confidence="medium",
                    reason="payment-method guess downgraded by dataset context",
                )

        if _looks_total_value_candidate(column["name"], column["dtype_display"]) and money_columns >= 2:
            _apply_refined_inference(
                column,
                role="measure",
                semantic_type="money",
                confidence="medium",
                reason="co-occurs with multiple money-like columns",
            )


def _apply_refined_inference(
    column: dict[str, Any],
    *,
    role: str,
    semantic_type: str,
    confidence: str,
    reason: str,
) -> None:
    confidence_score = {"low": 0.45, "medium": 0.75, "high": 0.95}[confidence]
    column["inference"] = {
        **column["inference"],
        "role": role,
        "semantic_type": semantic_type,
        "confidence": confidence,
        "confidence_score": max(column["inference"]["confidence_score"], confidence_score),
        "reasons": column["inference"]["reasons"] + [reason],
    }
    column["semantic_type"] = semantic_type
    column["role"] = role


def infer_flags(
    column: dict[str, Any],
    row_count: int,
    *,
    money_column_count: int = 0,
) -> dict[str, Any]:
    evidence = column["inference"]
    name = column["name"].lower()
    return {
        "likely_id": evidence["role"] == "identifier",
        "likely_target": evidence["role"] == "target",
        "likely_foreign_key": evidence["role"] == "identifier" and name.endswith("_id") and name != "id",
        "likely_computed": _looks_computed_name(name, evidence["semantic_type"], money_column_count=money_column_count),
        "high_nulls": column["null_pct"] >= 20.0,
        "very_high_nulls": column["null_pct"] >= 50.0,
        "all_unique": bool(row_count and column["unique_count"] == row_count),
        "constant": column["unique_count"] == 1,
        "possible_pii": evidence["semantic_type"] in {"email", "phone", "address", "ssn"},
        "mixed_type": column.get("mixed_type", False),
    }


def infer_dataset_summary(profile: dict[str, Any]) -> str:
    row_count = f"{profile['row_count']:,}"
    column_count = profile["column_count"]
    role_counts = Counter(column.get("inference", {}).get("role", "descriptor") for column in profile["columns"])
    semantic_counts = Counter(column.get("inference", {}).get("semantic_type", "unknown") for column in profile["columns"])
    pieces = [f"Tabular dataset with {row_count} rows and {column_count} columns."]

    temporal_cycle_count = semantic_counts.get("temporal_cycle", 0)
    measure_count = role_counts.get("measure", 0)

    column_names = {column["name"].lower() for column in profile["columns"]}

    if semantic_counts.get("longitude") and semantic_counts.get("latitude"):
        pieces.append("Includes latitude and longitude-style coordinate fields.")
    elif (
        measure_count >= 1
        and (
            {"year", "month"} <= column_names
            or any(column["dtype_display"] == "datetime" for column in profile["columns"]) and temporal_cycle_count >= 1
        )
    ):
        pieces.append("Looks like a compact time-series style table with temporal fields and numeric measures.")
    elif role_counts.get("measure", 0) >= max(2, column_count // 2) and (
        role_counts.get("category", 0) >= 1 or role_counts.get("descriptor", 0) >= 1
    ):
        pieces.append("Mostly composed of numeric measures, with categorical or label fields for grouping.")
    elif temporal_cycle_count >= 1:
        pieces.append("Includes temporal grouping fields alongside measured or categorical values.")
    elif role_counts.get("measure", 0) >= max(2, column_count // 2):
        pieces.append("Mostly composed of numeric measures.")
    elif role_counts.get("category", 0) >= max(2, column_count // 3):
        pieces.append("Contains several categorical fields.")

    dates = [
        col for col in profile["columns"]
        if col["dtype_display"] == "datetime" and col.get("min_date") and col.get("max_date")
    ]
    if dates:
        date_col = dates[0]
        pieces.append(f"Covers values from {date_col['min_date']} to {date_col['max_date']} in `{date_col['name']}`.")

    null_rate = profile["overall_null_pct"]
    if null_rate > 0:
        pieces.append(f"Overall null rate is {null_rate:.1f}%.")

    identifier_count = role_counts.get("identifier", 0)
    if identifier_count:
        pieces.append(f"Includes {identifier_count} identifier-like column{'s' if identifier_count != 1 else ''}.")

    return " ".join(pieces)


def infer_column_description(column: dict[str, Any]) -> str:
    evidence = column["inference"]
    role = evidence["role"]
    semantic = evidence["semantic_type"]
    confidence = evidence["confidence"]
    null_pct = column["null_pct"]
    flags = column["flags"]

    if role == "identifier":
        if flags["likely_foreign_key"]:
            sentence = "Identifier that likely links to related records."
        elif semantic == "entity_key":
            sentence = "Subject or participant identifier."
        else:
            sentence = "Unique record identifier." if confidence == "high" else "Identifier-like field."
    elif role == "temporal":
        if semantic == "temporal_cycle":
            sentence = _temporal_cycle_sentence(column, confidence)
        else:
            sentence = _date_sentence(_confidence_label("Date or timestamp field", confidence), column)
    elif role == "location" and semantic == "longitude":
        sentence = _numeric_sentence("Longitude coordinate", column)
    elif role == "location" and semantic == "latitude":
        sentence = _numeric_sentence("Latitude coordinate", column)
    elif role == "location":
        sentence = _numeric_sentence(_confidence_label("Coordinate-like numeric field", confidence), column)
    elif role == "target":
        sentence = _categorical_sentence(_confidence_label("Likely target variable", confidence), column)
    elif role == "category" and semantic == "boolean_flag":
        sentence = _categorical_sentence(_confidence_label("Boolean-style flag", confidence), column)
    elif role == "category" and semantic == "status":
        sentence = _categorical_sentence(_confidence_label("Status field", confidence), column)
    elif role == "category" and semantic == "payment_method":
        sentence = _categorical_sentence(_confidence_label("Payment method field", confidence), column)
    elif role == "category":
        sentence = _categorical_sentence(_confidence_label("Categorical field", confidence), column)
    elif role == "text":
        sentence = _text_sentence(column, confidence)
    elif role == "descriptor" and semantic in {"email", "phone", "address", "name", "ssn"}:
        sentence = _descriptor_sentence(semantic, confidence, column)
    elif role == "descriptor" and semantic == "index_like":
        sentence = "Index-like column, likely carried over from a saved table export."
    elif role == "descriptor" and semantic == "code":
        sentence = _code_sentence(column, confidence)
    elif role == "descriptor" and semantic == "text_label":
        sentence = f"{_soft_label('Label-like text field', confidence)} with {column['unique_count']} distinct values."
    elif role == "descriptor" and semantic == "location_label":
        sentence = _categorical_sentence(_soft_label("Location or geography field", confidence), column)
    elif role == "measure" and semantic == "money":
        sentence = _numeric_sentence(_soft_label("Amount or value measure", confidence), column, include_money=True)
    elif role == "measure" and semantic == "score":
        sentence = _numeric_sentence(_soft_label("Score-like numeric measure", confidence), column)
    elif role == "measure" and semantic == "measurement":
        sentence = _numeric_sentence(_soft_label("Measured numeric field", confidence), column)
    elif role == "measure" and semantic == "age":
        sentence = _numeric_sentence(_soft_label("Age-like numeric measure", confidence), column)
    elif role == "measure" and semantic == "count":
        sentence = _numeric_sentence(_soft_label("Count-like numeric measure", confidence), column)
    elif role == "measure":
        sentence = _numeric_sentence(_soft_label("Numeric measure", confidence), column)
    else:
        sentence = "Purpose unclear from name alone."

    if null_pct > 0:
        sentence += f" {null_pct:.1f}% nulls."
    if flags["mixed_type"]:
        sentence += " Mixed value types detected."
    if flags["likely_computed"]:
        sentence += " May be derived from other fields."
    return sentence.strip()


def _numeric_sentence(lead: str, column: dict[str, Any], *, include_money: bool = False) -> str:
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


def _temporal_cycle_sentence(column: dict[str, Any], confidence: str) -> str:
    name = column["name"].lower()
    if "year" in name:
        return _numeric_sentence(_soft_label("Year field", confidence), column)
    if "month" in name:
        return _categorical_sentence(_soft_label("Month field", confidence), column)
    if "quarter" in name:
        return _categorical_sentence(_soft_label("Quarter field", confidence), column)
    if "week" in name:
        return _numeric_sentence(_soft_label("Week-based temporal field", confidence), column)
    if "day" in name:
        return _categorical_sentence(_soft_label("Day-based temporal field", confidence), column)
    if name == "time":
        return _categorical_sentence(_soft_label("Time grouping field", confidence), column)
    if column["dtype_display"] == "string":
        return _categorical_sentence(_soft_label("Temporal cycle field", confidence), column)
    return _numeric_sentence(_soft_label("Temporal cycle field", confidence), column)


def _categorical_sentence(lead: str, column: dict[str, Any]) -> str:
    values = column.get("value_counts") or []
    if values:
        top_values = ", ".join(f"`{value}` ({pct:.0f}%)" for value, _, pct in values[:3])
        return f"{lead}; common values include {top_values}."
    return f"{lead} with {column['unique_count']} distinct values."


def _text_sentence(column: dict[str, Any], confidence: str) -> str:
    unique_count = column["unique_count"]
    avg_length = column.get("avg_length")
    lead = _confidence_label("Free-text field", confidence)
    if avg_length is not None and not _is_nan(avg_length):
        return f"{lead}; average length {avg_length:.1f} characters across {unique_count} distinct values."
    return f"{lead} with {unique_count} distinct values."


def _descriptor_sentence(semantic: str, confidence: str, column: dict[str, Any]) -> str:
    lead_map = {
        "email": "Email-like field",
        "phone": "Phone-like field",
        "address": "Address-like field",
        "name": "Name-like field",
        "ssn": "Sensitive identifier-like field",
    }
    return _categorical_sentence(_confidence_label(lead_map[semantic], confidence), column)


def _code_sentence(column: dict[str, Any], confidence: str) -> str:
    return f"{_confidence_label('Code-like field', confidence)} with {column['unique_count']} distinct values."


def _confidence_label(base: str, confidence: str) -> str:
    if confidence == "high":
        return base
    if confidence == "medium":
        return f"Likely {base[0].lower()}{base[1:]}"
    return f"{base}; purpose not fully clear"


def _soft_label(base: str, confidence: str) -> str:
    if confidence == "medium":
        return f"Likely {base[0].lower()}{base[1:]}"
    return base


def _is_score_range(column: dict[str, Any]) -> bool:
    min_value = column.get("min")
    max_value = column.get("max")
    if min_value is None or max_value is None or any(_is_nan(v) for v in (min_value, max_value)):
        return False
    return (0 <= min_value <= max_value <= 1.0) or (0 <= min_value <= max_value <= 10.0)


def _looks_computed_name(name: str, semantic_type: str, *, money_column_count: int) -> bool:
    if semantic_type not in {"money", "numeric"}:
        return False
    if any(token in name for token in ("ratio", "pct", "percent")):
        return True
    if "amount" in name:
        return True
    if name in {"total", "grand_total"} and money_column_count >= 2:
        return True
    return False


def _is_count_like(column: dict[str, Any]) -> bool:
    min_value = column.get("min")
    max_value = column.get("max")
    if min_value is None or max_value is None or any(_is_nan(v) for v in (min_value, max_value)):
        return False
    return min_value >= 0 and max_value >= 1 and column.get("pct_negative", 0) == 0.0


def _looks_year_range(column: dict[str, Any]) -> bool:
    min_value = column.get("min")
    max_value = column.get("max")
    if min_value is None or max_value is None or any(_is_nan(v) for v in (min_value, max_value)):
        return False
    return 1800 <= min_value <= 2200 and 1800 <= max_value <= 2200


def _looks_yes_no(value_counts: list[tuple[str, int, float]]) -> bool:
    if not value_counts:
        return False
    values = {value.lower() for value, _, _ in value_counts}
    return values <= YES_NO_VALUES


def _looks_payment_method_values(value_counts: list[tuple[str, int, float]]) -> bool:
    if not value_counts:
        return False
    payment_terms = {
        "cash", "card", "credit", "credit card", "debit", "debit card", "paypal",
        "voucher", "wire", "check", "bank transfer", "mobile payment", "no charge",
    }
    values = {value.lower() for value, _, _ in value_counts}
    return values <= payment_terms


def _looks_total_value_candidate(name: str, dtype_display: str) -> bool:
    lowered = name.lower()
    return dtype_display in {"integer", "float"} and lowered in {"total", "grand_total", "trip_total", "invoice_total"}


def _looks_month_name_cycle(value_counts: list[tuple[str, int, float]]) -> bool:
    if not value_counts:
        return False
    months = {
        "january", "february", "march", "april", "may", "june",
        "july", "august", "september", "october", "november", "december",
        "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
    }
    values = {value.lower() for value, _, _ in value_counts}
    return values <= months


def _tokenize(name: str) -> list[str]:
    normalized = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return [token for token in re.split(r"[^a-zA-Z0-9]+", normalized.lower()) if token]


def _fmt_money(value: float) -> str:
    return f"${value:,.2f}"


def _fmt_number(value: float) -> str:
    if float(value).is_integer():
        return f"{int(value):,}"
    return f"{value:,.2f}"


def _is_nan(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)
