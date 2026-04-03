from datareadme.inferrer import (
    infer_column_description,
    infer_column_evidence,
    infer_dataset_summary,
    infer_semantic_type,
)


def test_infer_semantic_type_identifier() -> None:
    assert infer_semantic_type("customer_id", "integer") == "identifier"


def test_signal_based_evidence_detects_coordinate_role() -> None:
    column = {
        "name": "longitude",
        "dtype_display": "float",
        "unique_pct": 75.0,
        "value_counts": [],
        "avg_length": None,
        "min": -124.35,
        "max": -114.31,
        "pct_negative": 100.0,
    }

    evidence = infer_column_evidence(column, row_count=100)

    assert evidence["role"] == "location"
    assert evidence["semantic_type"] == "longitude"
    assert evidence["confidence"] == "high"


def test_signal_based_description_for_status_category() -> None:
    column = {
        "name": "status",
        "dtype_display": "string",
        "null_pct": 0.0,
        "unique_count": 3,
        "value_counts": [("complete", 7, 70.0), ("pending", 2, 20.0), ("cancelled", 1, 10.0)],
        "avg_length": 8.0,
        "flags": {
            "likely_id": False,
            "likely_foreign_key": False,
            "likely_computed": False,
            "mixed_type": False,
        },
        "inference": {
            "role": "category",
            "semantic_type": "status",
            "confidence": "high",
        },
    }

    description = infer_column_description(column)

    assert "Status field" in description
    assert "common values include" in description


def test_dataset_summary_mentions_coordinates_when_present() -> None:
    profile = {
        "row_count": 20640,
        "column_count": 10,
        "overall_null_pct": 0.1,
        "columns": [
            {
                "name": "longitude",
                "dtype_display": "float",
                "inference": {"role": "location", "semantic_type": "longitude"},
            },
            {
                "name": "latitude",
                "dtype_display": "float",
                "inference": {"role": "location", "semantic_type": "latitude"},
            },
            {
                "name": "median_house_value",
                "dtype_display": "float",
                "inference": {"role": "measure", "semantic_type": "money"},
            },
        ],
    }

    summary = infer_dataset_summary(profile)

    assert "coordinate fields" in summary


def test_signal_based_evidence_detects_temporal_cycle_fields() -> None:
    year_column = {
        "name": "year",
        "dtype_display": "integer",
        "unique_pct": 8.0,
        "value_counts": [],
        "avg_length": None,
        "min": 1949,
        "max": 1960,
        "pct_negative": 0.0,
    }
    month_column = {
        "name": "month",
        "dtype_display": "string",
        "unique_pct": 8.0,
        "value_counts": [("January", 8, 8.0), ("February", 8, 8.0), ("March", 8, 8.0)],
        "avg_length": 6.0,
    }

    year_evidence = infer_column_evidence(year_column, row_count=144)
    month_evidence = infer_column_evidence(month_column, row_count=144)

    assert year_evidence["role"] == "temporal"
    assert year_evidence["semantic_type"] == "temporal_cycle"
    assert month_evidence["role"] == "temporal"
    assert month_evidence["semantic_type"] == "temporal_cycle"


def test_dataset_summary_mentions_time_series_shape() -> None:
    profile = {
        "row_count": 144,
        "column_count": 3,
        "overall_null_pct": 0.0,
        "columns": [
            {"name": "year", "dtype_display": "integer", "inference": {"role": "temporal", "semantic_type": "temporal_cycle"}},
            {"name": "month", "dtype_display": "string", "inference": {"role": "temporal", "semantic_type": "temporal_cycle"}},
            {"name": "passengers", "dtype_display": "integer", "inference": {"role": "measure", "semantic_type": "count"}},
        ],
    }

    summary = infer_dataset_summary(profile)

    assert "time-series" in summary


def test_payment_method_and_subject_tokens_map_to_generic_roles() -> None:
    payment_column = {
        "name": "payment",
        "dtype_display": "string",
        "unique_pct": 10.0,
        "value_counts": [("cash", 3, 50.0), ("card", 3, 50.0)],
        "avg_length": 4.0,
    }
    subject_column = {
        "name": "subject",
        "dtype_display": "integer",
        "unique_pct": 33.0,
        "value_counts": [],
        "avg_length": None,
        "min": 1.0,
        "max": 20.0,
        "pct_negative": 0.0,
    }

    payment_evidence = infer_column_evidence(payment_column, row_count=6)
    subject_evidence = infer_column_evidence(subject_column, row_count=60)

    assert payment_evidence["role"] == "category"
    assert payment_evidence["semantic_type"] == "payment_method"
    assert subject_evidence["role"] == "identifier"
    assert subject_evidence["semantic_type"] == "entity_key"


def test_method_column_without_payment_context_stays_generic_category() -> None:
    column = {
        "name": "method",
        "dtype_display": "string",
        "unique_pct": 20.0,
        "value_counts": [("Radial Velocity", 5, 50.0), ("Transit", 5, 50.0)],
        "avg_length": 10.0,
    }

    evidence = infer_column_evidence(column, row_count=10)

    assert evidence["role"] == "category"
    assert evidence["semantic_type"] == "category"
