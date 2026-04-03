"""Narration preparation layer for future optional LLM integration."""

from __future__ import annotations

from typing import Any

from .backends.nollm import NoLLMBackend


def narrate_profile(profile: dict[str, Any], *, backend: str | None = None) -> dict[str, Any]:
    """Prepare narration context and optional generated descriptions."""
    backend_name = (backend or "none").lower()
    backend_instance = _resolve_backend(backend_name)
    context = build_narration_context(profile)
    prompts = build_narration_prompts(context)

    if backend_instance.name == "none":
        return {
            "backend": backend_instance.name,
            "enabled": False,
            "dataset_description": None,
            "column_descriptions": {},
            "context": context,
            "prompts": prompts,
        }

    dataset_description = backend_instance.complete(prompts["dataset"])
    column_descriptions = {
        column["name"]: backend_instance.complete(prompts["columns"][column["name"]])
        for column in context["columns"]
    }
    return {
        "backend": backend_instance.name,
        "enabled": True,
        "dataset_description": dataset_description or None,
        "column_descriptions": column_descriptions,
        "context": context,
        "prompts": prompts,
    }


def build_narration_context(profile: dict[str, Any]) -> dict[str, Any]:
    """Return a compact, LLM-safe evidence bundle for future narration."""
    columns = []
    for column in profile["columns"]:
        columns.append(
            {
                "name": column["name"],
                "dtype": column["dtype_display"],
                "role": column.get("role", "descriptor"),
                "semantic_type": column.get("semantic_type", "unknown"),
                "confidence": column.get("inference", {}).get("confidence", "low"),
                "null_pct": column["null_pct"],
                "unique_pct": column["unique_pct"],
                "sample_values": column.get("sample_values", [])[:5],
                "value_counts": column.get("value_counts", [])[:3],
                "min": column.get("min"),
                "max": column.get("max"),
                "min_date": column.get("min_date"),
                "max_date": column.get("max_date"),
                "flags": column.get("flags", {}),
            }
        )

    return {
        "dataset": {
            "filename": profile["filename"],
            "row_count": profile["row_count"],
            "column_count": profile["column_count"],
            "duplicate_row_count": profile["duplicate_row_count"],
            "overall_null_pct": profile["overall_null_pct"],
            "sampled": profile["sampled"],
            "load_notes": profile.get("load_notes", []),
        },
        "columns": columns,
    }


def build_narration_prompts(context: dict[str, Any]) -> dict[str, Any]:
    """Build prompt strings from the evidence bundle without making any network calls."""
    dataset = context["dataset"]
    column_names = ", ".join(column["name"] for column in context["columns"])
    dataset_prompt = "\n".join(
        [
            "Write a short plain-English dataset summary.",
            "Focus on what the dataset appears to represent, its size, and the main caveats.",
            f"Filename: {dataset['filename']}",
            f"Rows: {dataset['row_count']}",
            f"Columns: {dataset['column_count']}",
            f"Column names: {column_names}",
            f"Overall null rate: {dataset['overall_null_pct']:.1f}%",
            f"Duplicate rows: {dataset['duplicate_row_count']}",
            f"Load notes: {dataset['load_notes']}",
        ]
    )

    column_prompts: dict[str, str] = {}
    for column in context["columns"]:
        column_prompts[column["name"]] = "\n".join(
            [
                "Write one short README-friendly description for this dataset column.",
                "Stay concrete and avoid overclaiming if confidence is low.",
                f"Column: {column['name']}",
                f"Type: {column['dtype']}",
                f"Role: {column['role']}",
                f"Semantic hint: {column['semantic_type']}",
                f"Confidence: {column['confidence']}",
                f"Nulls: {column['null_pct']:.1f}%",
                f"Unique pct: {column['unique_pct']:.1f}%",
                f"Sample values: {column['sample_values']}",
                f"Top values: {column['value_counts']}",
                f"Numeric/date range: min={column['min']} max={column['max']} min_date={column['min_date']} max_date={column['max_date']}",
                f"Flags: {column['flags']}",
            ]
        )

    return {
        "dataset": dataset_prompt,
        "columns": column_prompts,
    }


def _resolve_backend(name: str) -> Any:
    if name in {"none", "no-llm", "nollm"}:
        return NoLLMBackend()
    raise ValueError(
        f"LLM backend '{name}' is not implemented yet. Use 'none' for the current no-LLM flow."
    )
