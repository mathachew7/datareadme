from datareadme.inferrer import infer_column_description, infer_semantic_type


def test_infer_semantic_type_identifier() -> None:
    assert infer_semantic_type("customer_id", "integer") == "identifier"


def test_infer_column_description_status() -> None:
    column = {
        "name": "status",
        "semantic_type": "status",
        "dtype_display": "string",
        "null_pct": 0.0,
        "unique_count": 3,
        "value_counts": [("complete", 7, 70.0), ("pending", 2, 20.0), ("cancelled", 1, 10.0)],
        "flags": {
            "likely_id": False,
            "likely_foreign_key": False,
            "likely_computed": False,
            "mixed_type": False,
        },
    }

    description = infer_column_description(column)

    assert "common values include" in description
