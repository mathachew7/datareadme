from datareadme.narrator import build_narration_context, build_narration_prompts, narrate_profile


def test_narration_context_includes_compact_column_evidence() -> None:
    profile = {
        "filename": "demo.csv",
        "row_count": 3,
        "column_count": 1,
        "duplicate_row_count": 0,
        "overall_null_pct": 0.0,
        "sampled": False,
        "load_notes": [],
        "columns": [
            {
                "name": "score",
                "dtype_display": "float",
                "role": "measure",
                "semantic_type": "score",
                "null_pct": 0.0,
                "unique_pct": 100.0,
                "sample_values": [1.0, 2.0, 3.0],
                "value_counts": [],
                "min": 1.0,
                "max": 3.0,
                "min_date": None,
                "max_date": None,
                "flags": {"likely_target": False},
                "inference": {"confidence": "high"},
            }
        ],
    }

    context = build_narration_context(profile)

    assert context["dataset"]["filename"] == "demo.csv"
    assert context["columns"][0]["semantic_type"] == "score"


def test_narration_prompts_are_built_without_model_calls() -> None:
    context = {
        "dataset": {
            "filename": "demo.csv",
            "row_count": 3,
            "column_count": 1,
            "duplicate_row_count": 0,
            "overall_null_pct": 0.0,
            "sampled": False,
            "load_notes": [],
        },
        "columns": [
            {
                "name": "score",
                "dtype": "float",
                "role": "measure",
                "semantic_type": "score",
                "confidence": "high",
                "null_pct": 0.0,
                "unique_pct": 100.0,
                "sample_values": [1.0, 2.0],
                "value_counts": [],
                "min": 1.0,
                "max": 2.0,
                "min_date": None,
                "max_date": None,
                "flags": {},
            }
        ],
    }

    prompts = build_narration_prompts(context)

    assert "Write a short plain-English dataset summary." in prompts["dataset"]
    assert "Column: score" in prompts["columns"]["score"]


def test_narrate_profile_none_backend_returns_context_only() -> None:
    profile = {
        "filename": "demo.csv",
        "row_count": 1,
        "column_count": 0,
        "duplicate_row_count": 0,
        "overall_null_pct": 0.0,
        "sampled": False,
        "load_notes": [],
        "columns": [],
    }

    narration = narrate_profile(profile, backend="none")

    assert narration["enabled"] is False
    assert narration["context"]["dataset"]["filename"] == "demo.csv"
