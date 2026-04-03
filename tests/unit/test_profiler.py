from pathlib import Path

import pandas as pd

from datareadme.api import profile


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
    assert result["columns"][2]["semantic_type"] == "currency"


def test_profile_file_sampling(tmp_path: Path) -> None:
    path = tmp_path / "sample.csv"
    path.write_text("id,name\n1,A\n2,B\n3,C\n", encoding="utf-8")

    result = profile(path, sample=2)

    assert result["sampled"] is True
    assert result["row_count"] == 2
