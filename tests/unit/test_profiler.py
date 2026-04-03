from pathlib import Path

import pandas as pd

from datareadme.api import profile
from datareadme.loader import load_table


def test_profile_dataframe_numeric_and_string_columns() -> None:
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "status": ["complete", "pending", "complete"],
            "total_amount": [10.0, 20.5, 10.0],
        }
    )

    result = profile(df, title="orders.csv")

    assert result["filename"] == "orders.csv"
    assert result["row_count"] == 3
    assert result["column_count"] == 3
    assert result["columns"][0]["flags"]["likely_id"] is True
    assert result["columns"][2]["inference"]["role"] == "measure"
    assert result["columns"][2]["semantic_type"] == "money"


def test_profile_file_sampling(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,A\n2,B\n3,C\n", encoding="utf-8")

    result = profile(path, sample=2)

    assert result["sampled"] is True
    assert result["row_count"] == 2


def test_headerless_file_gets_generated_column_names() -> None:
    loaded = load_table("tests/fixtures/headerless_numbers.csv")

    assert list(loaded.dataframe.columns) == ["col_0", "col_1", "col_2"]
    assert loaded.load_notes


def test_mixed_value_column_sets_mixed_type_flag() -> None:
    result = profile("tests/fixtures/mixed_values.csv")
    mixed_column = next(column for column in result["columns"] if column["name"] == "mixed_value")

    assert mixed_column["flags"]["mixed_type"] is True


def test_total_column_becomes_money_when_other_money_fields_exist() -> None:
    df = pd.DataFrame(
        {
            "fare": [10.0, 12.0, 8.0],
            "tip": [2.0, 3.0, 0.0],
            "tolls": [0.0, 1.5, 0.0],
            "total": [12.0, 16.5, 8.0],
        }
    )

    result = profile(df, title="taxis.csv")
    total_column = next(column for column in result["columns"] if column["name"] == "total")

    assert total_column["semantic_type"] == "money"
