# Contributing

Thanks for helping improve `datareadme`.

The project is still intentionally small. The best contributions keep it readable, lightweight, and useful on real datasets.

## Principles

- Keep the core output readable and concise.
- Preserve a strong no-LLM workflow.
- Prefer graceful degradation over crashes.
- Avoid domain-specific hacks when a reusable signal or heuristic would work.
- Add tests for new heuristics and edge cases.

## Ways to contribute

- Report incorrect or misleading generated descriptions.
- Share tricky CSV or TSV examples that expose weak spots.
- Improve output readability and documentation quality.
- Add tests for edge cases and regression coverage.
- Tighten heuristics without making the engine bloated or brittle.

## Local development

Install dependencies:

```bash
python -m pip install -e '.[dev]'
```

Run the test suite:

```bash
python -m pytest
```

Try the CLI locally:

```bash
datareadme examples/transactions/transactions.csv --preview
```

## Pull request guidelines

- Keep changes focused.
- Explain the problem being fixed, not just the code change.
- Include or update tests when behavior changes.
- Prefer conservative inference over fake confidence.
- Update docs or examples when the public behavior changes.

## Good issues to open

- A dataset where the summary is misleading
- A column description that is clearly wrong
- A crash on a valid CSV or TSV file
- A quality note that should have been included but was missed
- A regression introduced by a new heuristic
