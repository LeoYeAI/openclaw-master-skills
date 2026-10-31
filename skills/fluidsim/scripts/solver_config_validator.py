#!/usr/bin/env python3
"""Validate a bounded FluidSim 0.9 JSON simulation plan."""

from __future__ import annotations

import argparse

try:
    from ._common import ToolError, checked_input, emit_json, fail_json, load_json
    from ._schema import example_config, validate_config
except ImportError:  # Direct script execution.
    from _common import ToolError, checked_input, emit_json, fail_json, load_json
    from _schema import example_config, validate_config


TOOL = "fluidsim-solver-config-validator"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate strict local JSON against the static FluidSim 0.9 CFD "
            "configuration profile. No FluidSim package is imported and nothing runs."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--config", help="Configuration JSON within --root.")
    source.add_argument(
        "--example",
        action="store_true",
        help="Emit a bounded example configuration as strict JSON.",
    )
    parser.add_argument(
        "--root",
        default=".",
        help="Local I/O boundary (default: current directory).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.example:
            emit_json(example_config())
            return 0
        path = checked_input(
            args.config,
            root=args.root,
            kind="file",
            suffixes={".json"},
        )
        report = validate_config(load_json(path))
        report.update(
            {
                "commands_executed": False,
                "dynamic_imports_used": False,
                "network_used": False,
                "source": path.name,
                "tool": TOOL,
            }
        )
        emit_json(report)
        return 0 if report["ok"] else 2
    except (OSError, ToolError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    raise SystemExit(main())
