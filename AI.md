# datareadme AI Control

## Mission

Turn tabular data files into readable repository-friendly documentation, with a strong no-LLM mode and optional AI-enhanced descriptions.

## Product Positioning

`datareadme` is not a statistical dashboard and not a data catalog. It is a lightweight documentation generator that produces a `DATA_README.md` someone can commit next to their dataset.

## Current MVP Scope

- Input: CSV and TSV files
- Output: Markdown
- Mode: no-LLM first
- Interface: Python API and CLI
- Core sections:
  - short dataset summary
  - at-a-glance table
  - columns table
  - quality notes
  - loading snippet

## Non-Goals For MVP

- Full AI backend integration
- HTML output
- Database connectors
- Excel and Parquet support
- Deep statistical analysis
- Interactive UI

## Principles

1. Readable over complete.
2. Useful without an LLM.
3. Markdown is the primary artifact.
4. Fail gracefully on messy files.
5. Prefer conservative wording over false confidence.

## Build Order

1. Stable profiler for CSV and TSV
2. Good heuristic inference and stat-based descriptions
3. Markdown renderer and CLI
4. Tests and examples
5. Optional AI narration layer

## Guardrails

- Never require network access for the core path.
- Never crash because one column is messy.
- Avoid claiming semantic meaning unless confidence is reasonable.
- Make generated text easy to edit by humans afterward.
