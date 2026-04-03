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
        "columns": [
            {
                "name": "order_id",
                "dtype_display": "integer",
                "null_pct": 0.0,
                "unique_count": 2,
                "semantic_type": "identifier",
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
    assert "## Columns" in rendered
