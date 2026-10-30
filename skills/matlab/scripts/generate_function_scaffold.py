#!/usr/bin/env python3
"""Dry-run or write deterministic MATLAB function and unit-test scaffolds."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import Any

from _common import (
    CliError,
    checked_input,
    checked_root,
    emit_json,
    fail_json,
    relative_id,
    validate_identifier,
    write_new_text,
)

TOOL = "generate_function_scaffold"
SAFE_DIRECTORY = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,63}$")


def _directory(root: Path, name: str, *, write: bool) -> Path:
    if not SAFE_DIRECTORY.fullmatch(name):
        raise CliError("source/test directory must be one simple local directory name")
    path = root / name
    if path.exists():
        return checked_input(path, root=root, kind="directory")
    if not write:
        return path
    try:
        path.mkdir()
    except FileExistsError:
        return checked_input(path, root=root, kind="directory")
    except OSError as exc:
        raise CliError(f"cannot create directory: {path}") from exc
    return path


def _title_name(name: str) -> str:
    return name[0].upper() + name[1:]


def function_source(name: str) -> str:
    upper = name.upper()
    return f"""function result = {name}(data, options)
%{upper} Scale a finite numeric matrix.
%   RESULT = {upper}(DATA, Scale=VALUE) multiplies DATA by VALUE.

arguments
    data (:,:) double {{mustBeFinite}}
    options.Scale (1,1) double {{mustBeFinite}} = 1
end

result = data .* options.Scale;
end
"""


def test_source(name: str, class_name: str) -> str:
    return f"""classdef {class_name} < matlab.unittest.TestCase
    methods (Test)
        function scalesFiniteMatrix(testCase)
            actual = {name}([1 2; 3 4], Scale=2);
            expected = [2 4; 6 8];
            testCase.verifyEqual(actual, expected, AbsTol=1e-14);
        end

        function preservesShape(testCase)
            actual = {name}(zeros(2, 3));
            testCase.verifySize(actual, [2 3]);
        end
    end
end
"""


def generate(args: argparse.Namespace) -> dict[str, Any]:
    root = checked_root(args.root)
    name = validate_identifier(args.name, name="function name")
    class_name = validate_identifier(
        "Test" + _title_name(name), name="test class name"
    )
    if args.source_dir == args.test_dir:
        raise CliError("source and test directories must be distinct")
    if not SAFE_DIRECTORY.fullmatch(args.source_dir) or not SAFE_DIRECTORY.fullmatch(
        args.test_dir
    ):
        raise CliError(
            "source/test directory must be one simple local directory name"
        )
    source_dir = _directory(root, args.source_dir, write=args.write)
    test_dir = _directory(root, args.test_dir, write=args.write)
    function_path = source_dir / f"{name}.m"
    test_path = test_dir / f"{class_name}.m"
    for path in (function_path, test_path):
        if path.exists() or path.is_symlink():
            raise CliError(f"refusing to overwrite existing scaffold: {path}")
    function_text = function_source(name)
    test_text = test_source(name, class_name)
    if args.write:
        write_new_text(function_path, function_text)
        try:
            write_new_text(test_path, test_text)
        except Exception:
            try:
                function_path.unlink(missing_ok=True)
            except OSError:
                pass
            raise
    return {
        "contents": {
            "function": function_text,
            "test": test_text,
        },
        "dry_run": not args.write,
        "executes": False,
        "files": {
            "function": relative_id(function_path, root),
            "test": relative_id(test_path, root),
        },
        "network_accessed": False,
        "ok": True,
        "requires_matlab_to_run_tests": True,
        "target_release": "R2026a",
        "tool": TOOL,
        "wrote_files": bool(args.write),
        "warning": (
            "Generated text is a starting point. Review domain semantics, "
            "tolerances, products, paths, and safety before execution."
        ),
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Generate a MATLAB R2026a function and matlab.unittest class. "
            "Default is dry-run; --write refuses collisions."
        )
    )
    result.add_argument("name", help="MATLAB function identifier")
    result.add_argument("--root", default=".", help="allowed project root")
    result.add_argument("--source-dir", default="src")
    result.add_argument("--test-dir", default="tests")
    result.add_argument(
        "--write", action="store_true", help="create new files and directories"
    )
    return result


def main() -> int:
    try:
        emit_json(generate(parser().parse_args()))
        return 0
    except CliError as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
