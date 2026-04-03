# Demo Script

Use this for a short terminal recording, GIF, or screen capture.

## Goal

Show a real dataset going in and a readable `DATA_README.md` coming out in under 20 seconds.

## Suggested flow

```bash
python -m pip install -e .
datareadme examples/transactions/transactions.csv
sed -n '1,80p' examples/transactions/DATA_README.md
```

## Talk track

1. Start with the dataset file and mention that it has no documentation.
2. Run `datareadme` in one command.
3. Open the generated `DATA_README.md`.
4. Point out the summary, columns table, and quality notes.
5. End on the idea that the output is plain Markdown you can edit and commit.

## Good caption

Turn a mystery CSV into a readable `DATA_README.md` in one command.

## Recording tips

- Keep the clip under 20 seconds.
- Use one real example only.
- Zoom in enough that the Markdown is readable.
- End on the generated output, not the command prompt.
