# datareadme

Turn a CSV or TSV file into a clean `DATA_README.md`.

`datareadme` reads a dataset, profiles its columns, and generates a simple Markdown file that helps someone understand what the data is, what each column likely means, and what quality issues to watch for.

## Why people use it

You get handed a file like `transactions_v3_final_REAL.csv`.

You do not know:

- what the dataset is really about
- what the columns mean
- which fields are safe to trust
- where the obvious quality issues are

`datareadme` gives you a readable first draft of that documentation in Markdown so you can keep it next to the data, edit it, and commit it.

## One-command demo

```bash
datareadme examples/transactions/transactions.csv
```

That generates `examples/transactions/DATA_README.md`.

Example output:

```md
# transactions.csv

> Tabular dataset with 4 rows and 5 columns. Covers values from 2024-01-01 to 2024-02-10 in `created_at`. Includes 1 identifier-like column.

## At a glance

| | |
|---|---|
| Rows | 4 |
| Columns | 5 |
| Duplicate rows | 1 |
| Overall null rate | 0.0% |
```

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

## Why not a profiling dashboard?

`datareadme` is for documentation, not deep statistical exploration.

If you want a large profiling report, correlation analysis, or distribution-heavy dashboards, use a profiling tool.
If you want a clean `DATA_README.md` that a person can skim in two minutes, use `datareadme`.

## Launch Kit

- [Demo script](docs/demo-script.md)
- [Launch copy](docs/launch-kit.md)

## Development

Install development dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run tests:

```bash
python -m pytest
```
