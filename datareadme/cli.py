"""Command-line interface for datareadme."""

from __future__ import annotations

import argparse
from pathlib import Path

from .api import generate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="datareadme",
        description="Generate readable dataset documentation from tabular data files.",
    )
    parser.add_argument("source", help="Path to a CSV or TSV file")
    parser.add_argument("-o", "--output", help="Output path for generated Markdown")
    parser.add_argument("--sample", type=int, help="Limit profiling to the first N rows")
    parser.add_argument("--title", help="Override the dataset title/filename in the output")
    parser.add_argument("--preview", action="store_true", help="Print the result instead of saving it")
    parser.add_argument("--llm", default="none", help="Reserved for future AI backends")
    parser.add_argument("--no-llm", action="store_true", help="Force the no-LLM path")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    llm = None if args.no_llm else args.llm
    output = args.output
    if not output and not args.preview:
        output = str(Path(args.source).with_name("DATA_README.md"))
    markdown = generate(args.source, output=output, sample=args.sample, title=args.title, llm=llm)
    if args.preview:
        print(markdown)
    elif output:
        print(f"Wrote {output}")


if __name__ == "__main__":
    main()
