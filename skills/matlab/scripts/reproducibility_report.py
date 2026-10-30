#!/usr/bin/env python3
"""Create a deterministic named-file reproducibility report."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

from _common import (
    CliError,
    checked_input,
    checked_output,
    checked_root,
    emit_json,
    fail_json,
    load_json,
    relative_id,
    sha256_file,
    validate_release,
    write_new_text,
)

TOOL = "reproducibility_report"
OCTAVE_VERSION = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
ALLOWED_SUFFIXES = {
    ".csv",
    ".fig",
    ".h5",
    ".hdf5",
    ".json",
    ".m",
    ".mat",
    ".mlx",
    ".pdf",
    ".png",
    ".svg",
    ".tsv",
    ".txt",
}


def _finite_nonnegative(value: float | None, name: str) -> float | None:
    if value is None:
        return None
    if not math.isfinite(value) or value < 0:
        raise CliError(f"{name} must be finite and nonnegative")
    return value


def _runtime_version(runtime: str, version: str) -> str:
    if runtime == "matlab":
        return validate_release(version)
    if not OCTAVE_VERSION.fullmatch(version):
        raise CliError("Octave runtime version must be a three-part numeric version")
    return version


def _named_fact(value: str | None, name: str, *, maximum: int = 500) -> str | None:
    if value is None:
        return None
    if not value or len(value) > maximum or any(
        ord(character) < 32 for character in value
    ):
        raise CliError(f"{name} must be bounded printable text")
    return value


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(args.root)
    if len(args.file) > 200:
        raise CliError("at most 200 named files are accepted")
    if not args.file:
        raise CliError("provide at least one --file")
    files = [
        checked_input(
            value,
            root=root,
            suffixes=ALLOWED_SUFFIXES,
            max_bytes=args.max_file_bytes,
        )
        for value in args.file
    ]
    ids = [relative_id(path, root) for path in files]
    if len(set(ids)) != len(ids):
        raise CliError("--file paths must be unique")
    file_records = [
        {
            "path": relative_id(path, root),
            "sha256": sha256_file(path, max_bytes=args.max_file_bytes),
            "size_bytes": path.stat().st_size,
        }
        for path in sorted(files, key=lambda item: relative_id(item, root))
    ]
    product_manifest: dict[str, Any] | None = None
    if args.product_manifest:
        path = checked_input(
            args.product_manifest,
            root=root,
            suffixes={".json"},
            max_bytes=2 * 1024 * 1024,
        )
        data = load_json(path)
        if not isinstance(data, dict) or data.get("schema_version") != "1.0":
            raise CliError("product manifest must be a schema_version 1.0 object")
        product_manifest = {
            "path": relative_id(path, root),
            "sha256": sha256_file(path, max_bytes=2 * 1024 * 1024),
            "license_status_verified": False,
        }
    command_plan: dict[str, Any] | None = None
    if args.command_plan:
        path = checked_input(
            args.command_plan,
            root=root,
            suffixes={".json"},
            max_bytes=2 * 1024 * 1024,
        )
        data = load_json(path)
        if not isinstance(data, dict) or data.get("executes") is not False:
            raise CliError("command plan must be a nonexecuting JSON plan")
        command_plan = {
            "path": relative_id(path, root),
            "sha256": sha256_file(path, max_bytes=2 * 1024 * 1024),
        }
    runtime_version = _runtime_version(args.runtime, args.runtime_version)
    abs_tol = _finite_nonnegative(args.absolute_tolerance, "absolute_tolerance")
    rel_tol = _finite_nonnegative(args.relative_tolerance, "relative_tolerance")
    if (abs_tol is not None or rel_tol is not None) and not args.tolerance_rationale:
        raise CliError(
            "--tolerance-rationale is required when a numeric tolerance is recorded"
        )
    if args.rng_seed is not None and not 0 <= args.rng_seed <= 2**32 - 1:
        raise CliError("--rng-seed must be between 0 and 4294967295")
    if args.rng_substream is not None and not 1 <= args.rng_substream <= 2**31 - 1:
        raise CliError("--rng-substream must be between 1 and 2147483647")
    rng_algorithm = _named_fact(args.rng_algorithm, "rng_algorithm", maximum=100)
    tolerance_rationale = _named_fact(
        args.tolerance_rationale, "tolerance_rationale", maximum=2000
    )
    platform_os = _named_fact(args.platform_os, "platform_os", maximum=200)
    platform_arch = _named_fact(args.platform_arch, "platform_arch", maximum=200)
    return {
        "command_plan": command_plan,
        "environment_dumped": False,
        "executes": False,
        "named_files": file_records,
        "network_accessed": False,
        "numeric_policy": {
            "absolute_tolerance": abs_tol,
            "relative_tolerance": rel_tol,
            "rationale": tolerance_rationale,
        },
        "ok": True,
        "platform": {
            "architecture": platform_arch,
            "operating_system": platform_os,
            "source": "caller-supplied; not probed",
        },
        "products_manifest": product_manifest,
        "randomness": {
            "algorithm": rng_algorithm,
            "seed": args.rng_seed,
            "substream": args.rng_substream,
        },
        "root_emitted": False,
        "runtime": args.runtime,
        "runtime_version": runtime_version,
        "schema_version": "1.0",
        "tool": TOOL,
        "warning": (
            "Hashes and named facts support provenance but do not establish "
            "safety, scientific validity, or license availability."
        ),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Hash only named local artifacts and emit a deterministic MATLAB/"
            "Octave reproducibility report. No environment or runtime probe occurs."
        )
    )
    result.add_argument("--root", default=".", help="allowed local root")
    result.add_argument(
        "--file", action="append", default=[], help="named local artifact; repeat"
    )
    result.add_argument("--runtime", choices=("matlab", "octave"), default="matlab")
    result.add_argument("--runtime-version", default="R2026a")
    result.add_argument("--product-manifest")
    result.add_argument("--command-plan")
    result.add_argument("--rng-algorithm")
    result.add_argument("--rng-seed", type=int)
    result.add_argument("--rng-substream", type=int)
    result.add_argument("--absolute-tolerance", type=float)
    result.add_argument("--relative-tolerance", type=float)
    result.add_argument("--tolerance-rationale")
    result.add_argument("--platform-os", default="unknown")
    result.add_argument("--platform-arch", default="unknown")
    result.add_argument("--max-file-bytes", type=int, default=64 * 1024 * 1024)
    result.add_argument("--output", help="optional new .json output under root")
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        if args.max_file_bytes < 1 or args.max_file_bytes > 512 * 1024 * 1024:
            raise CliError("--max-file-bytes must be between 1 and 536870912")
        report = build(args)
        if args.output:
            root = checked_root(args.root)
            output = checked_output(args.output, root=root, suffixes={".json"})
            write_new_text(
                output,
                json.dumps(
                    report, indent=2, sort_keys=True, ensure_ascii=False
                )
                + "\n",
            )
        emit_json(report)
        return 0
    except CliError as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
