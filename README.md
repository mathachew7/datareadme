# datareadme

Turn a CSV or TSV file into a clean `DATA_README.md`.

`datareadme` reads a dataset, profiles its columns, and generates a simple Markdown file that helps someone understand what the data is, what each column likely means, and what quality issues to watch for.

## What it does

For a tabular file, `datareadme` generates:

- a short plain-English dataset summary
- a compact "At a glance" section
- a columns table with inferred descriptions
- data quality notes for nulls, duplicates, mixed values, and other warnings
- a small loading snippet for pandas

The goal is not a giant profiling report. The goal is documentation you can keep next to the data.

## Install

From the repo:

```bash
python -m pip install -e .
```

## Use it

Generate a README next to the source file:

```bash
datareadme path/to/data.csv
```

Write to a specific file:

```bash
datareadme path/to/data.csv -o DATA_README.md
```

Preview without saving:

```bash
datareadme path/to/data.csv --preview
```

Limit profiling to the first `N` rows:

```bash
datareadme path/to/data.csv --sample 10000
```

The current release is focused on:

- CSV and TSV input
- Markdown output
- strong no-LLM behavior by default

## Python API

```python
import datareadme as dr

markdown = dr.generate("examples/transactions/transactions.csv")
profile = dr.profile("examples/transactions/transactions.csv")
```

## Examples

- [transactions example](examples/transactions/DATA_README.md)
- [survey example](examples/survey/DATA_README.md)

## Development

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run tests:

```bash
python -m pytest
```
