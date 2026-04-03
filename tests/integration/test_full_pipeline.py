from pathlib import Path

from datareadme.api import generate


def test_generate_markdown_from_fixture() -> None:
    fixture = Path("tests/fixtures/transactions.csv")

    markdown = generate(fixture)

    assert "# transactions.csv" in markdown
    assert "## Structure" in markdown
    assert "## Columns" in markdown
    assert "`customer_id`" in markdown
