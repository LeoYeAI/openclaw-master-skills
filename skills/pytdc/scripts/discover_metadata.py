#!/usr/bin/env python3
"""Discover PyTDC registries without constructing loaders or downloading data."""

from __future__ import annotations

import argparse
import sys
from typing import Any, Iterable

from _common import (
    CliError,
    bounded_int,
    canonical_name,
    emit_json,
    load_pytdc_metadata,
)


def _window(values: Iterable[Any], offset: int, limit: int) -> dict[str, Any]:
    items = list(values)
    selected = items[offset : offset + limit]
    return {
        "items": selected,
        "limit": limit,
        "offset": offset,
        "returned": len(selected),
        "total": len(items),
        "truncated": offset + len(selected) < len(items),
    }


def collect_metadata(
    metadata: Any,
    package_version: str,
    *,
    kind: str,
    task: str | None,
    offset: int,
    limit: int,
) -> dict[str, Any]:
    """Collect a bounded view of the installed metadata registries."""

    dataset_registry = dict(metadata.dataset_names)
    if task is not None:
        task = canonical_name(task, dataset_registry, "task")

    sections: dict[str, Any] = {}
    requested = (
        ["tasks", "datasets", "benchmarks", "evaluators", "oracles"]
        if kind == "all"
        else [kind]
    )

    if "tasks" in requested:
        sections["tasks"] = _window(
            (
                {"task": name, "dataset_count": len(names)}
                for name, names in dataset_registry.items()
            ),
            offset,
            limit,
        )

    if "datasets" in requested:
        if task is not None:
            values = (
                {"task": task, "dataset": name}
                for name in dataset_registry[task]
            )
        else:
            values = (
                {"task": task_name, "dataset": dataset_name}
                for task_name, names in dataset_registry.items()
                for dataset_name in names
            )
        sections["datasets"] = _window(values, offset, limit)

    if "benchmarks" in requested:
        values = (
            {
                "group": group_name,
                "task": task_name,
                "benchmark": benchmark_name,
            }
            for group_name, task_map in metadata.benchmark_names.items()
            for task_name, names in task_map.items()
            for benchmark_name in names
        )
        sections["benchmarks"] = _window(values, offset, limit)

    if "evaluators" in requested:
        sections["evaluators"] = _window(
            ({"name": name} for name in dict.fromkeys(metadata.evaluator_name)),
            offset,
            limit,
        )

    if "oracles" in requested:
        sections["oracles"] = _window(
            ({"name": name} for name in dict.fromkeys(metadata.oracle_names)),
            offset,
            limit,
        )

    return {
        "download_performed": False,
        "kind": kind,
        "package": "PyTDC",
        "package_version": package_version,
        "source": "installed tdc.metadata registry",
        "task_filter": task,
        **sections,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Read task, dataset, benchmark, evaluator, and oracle names from the "
            "installed PyTDC metadata module. This command never instantiates a "
            "loader or downloads a dataset/model."
        )
    )
    parser.add_argument(
        "--kind",
        choices=("tasks", "datasets", "benchmarks", "evaluators", "oracles", "all"),
        default="tasks",
        help="registry to show (default: tasks)",
    )
    parser.add_argument("--task", help="exact task filter for --kind datasets")
    parser.add_argument(
        "--offset",
        type=bounded_int(0, 1_000_000),
        default=0,
        help="skip this many registry entries (default: 0)",
    )
    parser.add_argument(
        "--limit",
        type=bounded_int(1, 500),
        default=50,
        help="maximum entries returned per section (default: 50; max: 500)",
    )
    parser.add_argument("--output", help="write JSON to a relative workspace path")
    parser.add_argument(
        "--force", action="store_true", help="replace an existing --output file"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.task and args.kind not in {"datasets", "all"}:
        parser.error("--task is only valid with --kind datasets or --kind all")

    try:
        metadata, package_version = load_pytdc_metadata()
        result = collect_metadata(
            metadata,
            package_version,
            kind=args.kind,
            task=args.task,
            offset=args.offset,
            limit=args.limit,
        )
        emit_json(result, args.output, force=args.force)
    except (CliError, OSError, TypeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
