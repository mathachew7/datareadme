from datareadme.renderer import render_markdown


def test_render_markdown_includes_sections() -> None:
    profile = {
        "filename": "orders.csv",
        "row_count": 2,
        "column_count": 1,
        "file_size_bytes": 100,
        "duplicate_row_count": 0,
        "overall_null_pct": 0.0,
        "generation_timestamp": "2026-04-02T12:00:00+00:00",
        "sampled": False,
        "load_notes": [],
        "columns": [
            {
                "name": "order_id",
                "dtype_display": "integer",
                "role": "identifier",
                "null_pct": 0.0,
                "unique_count": 2,
                "semantic_type": "identifier",
                "inference": {
                    "role": "identifier",
                    "semantic_type": "identifier",
                    "confidence": "high",
                },
                "flags": {
                    "likely_id": True,
                    "likely_foreign_key": False,
                    "likely_computed": False,
                    "possible_pii": False,
                    "likely_target": False,
                    "mixed_type": False,
                },
                "is_constant": False,
            }
        ],
    }

    rendered = render_markdown(profile)

    assert "# orders.csv" in rendered
    assert "## At a glance" in rendered
    assert "## Structure" in rendered
    assert "## Columns" in rendered


def test_render_quality_note_for_small_nonzero_null_rate() -> None:
    profile = {
        "filename": "housing.csv",
        "row_count": 10,
        "column_count": 1,
        "file_size_bytes": 100,
        "duplicate_row_count": 0,
        "overall_null_pct": 1.0,
        "generation_timestamp": "2026-04-02T12:00:00+00:00",
        "sampled": False,
        "load_notes": [],
        "columns": [
            {
                "name": "total_bedrooms",
                "dtype_display": "float",
                "role": "measure",
                "null_pct": 1.0,
                "unique_count": 9,
                "semantic_type": "count",
                "inference": {
                    "role": "measure",
                    "semantic_type": "count",
                    "confidence": "medium",
                },
                "flags": {
                    "likely_id": False,
                    "likely_foreign_key": False,
                    "likely_computed": False,
                    "possible_pii": False,
                    "likely_target": False,
                    "mixed_type": False,
                },
                "is_constant": False,
                "min": 1.0,
                "max": 10.0,
            }
        ],
    }

    rendered = render_markdown(profile)

    assert "worth checking before use" in rendered


def test_render_profiling_notes_for_load_warnings() -> None:
    profile = {
        "filename": "headerless.csv",
        "row_count": 4,
        "column_count": 3,
        "file_size_bytes": 100,
        "duplicate_row_count": 0,
        "overall_null_pct": 0.0,
        "generation_timestamp": "2026-04-02T12:00:00+00:00",
        "sampled": False,
        "load_notes": ["Column headers were not detected reliably; generated names like `col_0` were used."],
        "columns": [
            {
                "name": "col_0",
                "dtype_display": "integer",
                "role": "temporal",
                "null_pct": 0.0,
                "unique_count": 2,
                "semantic_type": "temporal_cycle",
                "inference": {
                    "role": "temporal",
                    "semantic_type": "temporal_cycle",
                    "confidence": "medium",
                },
                "flags": {
                    "likely_id": False,
                    "likely_foreign_key": False,
                    "likely_computed": False,
                    "possible_pii": False,
                    "likely_target": False,
                    "mixed_type": False,
                },
                "is_constant": False,
                "min": 1949.0,
                "max": 1950.0,
            }
        ],
    }

    rendered = render_markdown(profile)

    assert "## Profiling notes" in rendered
    assert "generated names like `col_0` were used" in rendered


def test_render_markdown_uses_narration_overrides_when_provided() -> None:
    profile = {
        "filename": "demo.csv",
        "row_count": 2,
        "column_count": 1,
        "file_size_bytes": 100,
        "duplicate_row_count": 0,
        "overall_null_pct": 0.0,
        "generation_timestamp": "2026-04-02T12:00:00+00:00",
        "sampled": False,
        "load_notes": [],
        "columns": [
            {
                "name": "value",
                "dtype_display": "float",
                "role": "measure",
                "null_pct": 0.0,
                "unique_count": 2,
                "semantic_type": "measurement",
                "inference": {
                    "role": "measure",
                    "semantic_type": "measurement",
                    "confidence": "medium",
                },
                "flags": {
                    "likely_id": False,
                    "likely_foreign_key": False,
                    "likely_computed": False,
                    "possible_pii": False,
                    "likely_target": False,
                    "mixed_type": False,
                },
                "is_constant": False,
                "min": 1.0,
                "max": 2.0,
            }
        ],
    }
    narration = {
        "dataset_description": "Tiny demo dataset.",
        "column_descriptions": {"value": "Custom narration description."},
        "enabled": True,
    }

    rendered = render_markdown(profile, narration=narration, llm_enabled=True)

    assert "Tiny demo dataset." in rendered
    assert "Custom narration description." in rendered
