# datareadme

Turn tabular data into readable dataset documentation in seconds.

`datareadme` generates a repository-friendly `DATA_README.md` that explains what a dataset appears to be, what each column likely means, and what quality issues deserve attention before analysis.

## Why this exists

Most datasets arrive with missing context. You inherit a file like `transactions_v3_final_REAL.csv`, but not the explanation that makes it usable. Existing tools often optimize for statistical depth or enterprise catalog workflows. `datareadme` focuses on the simpler job: produce a Markdown document someone can read in two minutes and commit next to the data.

## Current scope

The first release is intentionally narrow:

- CSV and TSV input
- Markdown output
- strong no-LLM mode
- CLI and Python API

## Quick start

```bash
python -m pip install -e .
datareadme examples/transactions/transactions.csv
```

Preview instead of saving:

```bash
datareadme examples/transactions/transactions.csv --preview
```

## What it generates

Each generated `DATA_README.md` includes:

- a short dataset summary
- an at-a-glance table
- a columns table with inferred descriptions
- data quality notes
- a loading snippet

Example output:

```md
# transactions.csv

> Tabular dataset with 4 rows and 5 columns. Covers values from 2024-01-01
> to 2024-02-10 in `created_at`. Includes 1 identifier-like column.
```

See full examples:

- [transactions example](/Users/subashyadav/Documents/projects/datareadme/examples/transactions/DATA_README.md)
- [survey example](/Users/subashyadav/Documents/projects/datareadme/examples/survey/DATA_README.md)

## Python API

```python
import datareadme as dr

markdown = dr.generate("examples/transactions/transactions.csv")
profile = dr.profile("examples/transactions/transactions.csv")
```

## Project structure

- [AI.md](/Users/subashyadav/Documents/projects/datareadme/AI.md): product intent and build guardrails
- [PROGRESS.md](/Users/subashyadav/Documents/projects/datareadme/PROGRESS.md): current project state
- [BUILD_LOG.md](/Users/subashyadav/Documents/projects/datareadme/BUILD_LOG.md): lightweight development log
- [docs/index.md](/Users/subashyadav/Documents/projects/datareadme/docs/index.md): supporting docs

## Development

Install local dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run tests:

```bash
python -m pytest
```
