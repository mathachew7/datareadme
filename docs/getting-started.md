# Getting Started

## Install

```bash
python -m pip install -e '.[dev]'
```

## Generate a README

```bash
datareadme path/to/data.csv
```

By default this writes `DATA_README.md` next to the source file.

## Preview Instead Of Saving

```bash
datareadme path/to/data.csv --preview
```

## Use The Python API

```python
import datareadme as dr

markdown = dr.generate("path/to/data.csv")
profile = dr.profile("path/to/data.csv")
```

## Current Supported Formats

- CSV
- TSV
