#!/usr/bin/env python3
"""Validate a bounded MATLAB/Octave project and product manifest."""

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
    load_json,
    relative_id,
    validate_release,
)

TOOL = "validate_project_manifest"
TOP_LEVEL = {
    "schema_version",
    "project_name",
    "runtime",
    "matlab_release",
    "octave_version",
    "entry_points",
    "test_paths",
    "required_products",
    "optional_products",
    "octave_packages",
    "startup_actions",
    "shutdown_actions",
    "external_interfaces",
    "generated_artifacts",
    "notes",
}
REQUIRED = {
    "schema_version",
    "project_name",
    "runtime",
    "entry_points",
    "test_paths",
    "required_products",
    "optional_products",
    "octave_packages",
    "startup_actions",
    "shutdown_actions",
    "external_interfaces",
    "generated_artifacts",
    "notes",
}
PRODUCT_KEYS = {"name", "purpose", "minimum_release", "license_status"}
ENTRY_KEYS = {"path", "kind"}
OCTAVE_VERSION = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ._+()/-]{0,126}$")


def _string(value: Any, name: str, *, maximum: int = 500) -> str:
    if not isinstance(value, str) or not value or len(value) > maximum:
        raise CliError(f"{name} must be a nonempty string up to {maximum} characters")
    if any(ord(character) < 32 for character in value):
        raise CliError(f"{name} contains control characters")
    return value


def _list(value: Any, name: str, *, maximum: int = 500) -> list[Any]:
    if not isinstance(value, list):
        raise CliError(f"{name} must be an array")
    if len(value) > maximum:
        raise CliError(f"{name} has {len(value)} entries; limit is {maximum}")
    return value


def _validate_product(
    value: Any, *, field: str, index: int, warnings: list[str]
) -> str:
    if not isinstance(value, dict) or set(value) != PRODUCT_KEYS:
        raise CliError(
            f"{field}[{index}] must contain exactly {sorted(PRODUCT_KEYS)}"
        )
    name = _string(value["name"], f"{field}[{index}].name", maximum=127)
    if not SAFE_NAME.fullmatch(name):
        raise CliError(f"{field}[{index}].name contains unsupported characters")
    _string(value["purpose"], f"{field}[{index}].purpose", maximum=1000)
    release = value["minimum_release"]
    if release is not None:
        validate_release(_string(release, f"{field}[{index}].minimum_release"))
    status = value["license_status"]
    if status not in {"unknown", "confirmed", "unavailable"}:
        raise CliError(
            f"{field}[{index}].license_status must be unknown, confirmed, "
            "or unavailable"
        )
    if status == "confirmed":
        warnings.append(
            f"{name}: manifest says license confirmed; validator cannot verify "
            "installation, entitlement, or checkout availability"
        )
    return name


def _validate_path(
    raw: Any,
    *,
    root: Path,
    name: str,
    allow_missing: bool,
    kind: str = "any",
    suffixes: set[str] | None = None,
) -> str:
    text = _string(raw, name)
    if allow_missing:
        candidate = Path(text)
        if (
            candidate.is_absolute()
            or ".." in candidate.parts
            or "://" in text
            or "\x00" in text
        ):
            raise CliError(f"{name} must be a relative path without traversal")
        if suffixes and candidate.suffix.casefold() not in suffixes:
            raise CliError(f"{name} has unsupported suffix")
        return candidate.as_posix()
    path = checked_input(text, root=root, kind=kind, suffixes=suffixes)
    return relative_id(path, root)


def validate(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = checked_root(args.root)
    manifest_path = checked_input(
        args.manifest, root=root, suffixes={".json"}, max_bytes=2 * 1024 * 1024
    )
    data = load_json(manifest_path)
    if not isinstance(data, dict):
        raise CliError("manifest root must be a JSON object")
    unknown = set(data) - TOP_LEVEL
    missing = REQUIRED - set(data)
    if unknown:
        raise CliError(f"unknown manifest fields: {sorted(unknown)}")
    if missing:
        raise CliError(f"missing manifest fields: {sorted(missing)}")
    if data["schema_version"] != "1.0":
        raise CliError("schema_version must be 1.0")
    project_name = _string(data["project_name"], "project_name", maximum=127)
    if not SAFE_NAME.fullmatch(project_name):
        raise CliError("project_name contains unsupported characters")
    runtime = data["runtime"]
    if runtime not in {"matlab", "octave", "both"}:
        raise CliError("runtime must be matlab, octave, or both")
    matlab_release = data.get("matlab_release")
    octave_version = data.get("octave_version")
    if runtime in {"matlab", "both"}:
        validate_release(_string(matlab_release, "matlab_release"))
    elif matlab_release is not None:
        validate_release(_string(matlab_release, "matlab_release"))
    if runtime in {"octave", "both"}:
        version = _string(octave_version, "octave_version")
        if not OCTAVE_VERSION.fullmatch(version):
            raise CliError("octave_version must be a three-part numeric version")
    elif octave_version is not None:
        version = _string(octave_version, "octave_version")
        if not OCTAVE_VERSION.fullmatch(version):
            raise CliError("octave_version must be a three-part numeric version")

    warnings: list[str] = []
    entry_ids: list[str] = []
    for index, entry in enumerate(_list(data["entry_points"], "entry_points", maximum=100)):
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise CliError(
                f"entry_points[{index}] must contain exactly {sorted(ENTRY_KEYS)}"
            )
        kind = entry["kind"]
        if kind not in {"function", "script", "live_script"}:
            raise CliError(
                f"entry_points[{index}].kind must be function, script, or live_script"
            )
        suffixes = {".mlx"} if kind == "live_script" else {".m"}
        entry_id = _validate_path(
            entry["path"],
            root=root,
            name=f"entry_points[{index}].path",
            allow_missing=args.allow_missing_paths,
            kind="file",
            suffixes=suffixes,
        )
        entry_ids.append(entry_id)
        if kind == "live_script":
            warnings.append(
                f"{entry_id}: live script is opaque; export reviewed code to .m "
                "before execution"
            )
    if len(set(entry_ids)) != len(entry_ids):
        raise CliError("entry point paths must be unique")

    test_ids = [
        _validate_path(
            value,
            root=root,
            name=f"test_paths[{index}]",
            allow_missing=args.allow_missing_paths,
            kind="any",
        )
        for index, value in enumerate(
            _list(data["test_paths"], "test_paths", maximum=100)
        )
    ]
    if len(set(test_ids)) != len(test_ids):
        raise CliError("test paths must be unique")

    product_names: list[str] = []
    for field in ("required_products", "optional_products"):
        for index, value in enumerate(_list(data[field], field, maximum=200)):
            product_names.append(
                _validate_product(
                    value, field=field, index=index, warnings=warnings
                ).casefold()
            )
    if len(set(product_names)) != len(product_names):
        raise CliError("product names must be unique across required and optional lists")
    required_names = {
        value["name"].casefold() for value in data["required_products"]
    }
    if runtime in {"matlab", "both"} and "matlab" not in required_names:
        raise CliError("MATLAB runtime manifests must declare MATLAB as required")

    package_names: set[str] = set()
    for index, value in enumerate(
        _list(data["octave_packages"], "octave_packages", maximum=200)
    ):
        if not isinstance(value, dict) or set(value) != {
            "name",
            "version",
            "source",
            "sha256",
        }:
            raise CliError(
                "each octave_packages entry must contain name, version, source, "
                "and sha256"
            )
        name = _string(value["name"], f"octave_packages[{index}].name", maximum=127)
        _string(value["version"], f"octave_packages[{index}].version", maximum=64)
        _string(value["source"], f"octave_packages[{index}].source", maximum=500)
        checksum = _string(
            value["sha256"], f"octave_packages[{index}].sha256", maximum=64
        )
        if not SHA256.fullmatch(checksum):
            raise CliError(f"octave_packages[{index}].sha256 must be lowercase SHA-256")
        if name.casefold() in package_names:
            raise CliError("Octave package names must be unique")
        package_names.add(name.casefold())
    if runtime == "matlab" and data["octave_packages"]:
        warnings.append("Octave packages are declared for a MATLAB-only runtime")

    action_ids: list[str] = []
    for field in ("startup_actions", "shutdown_actions"):
        for index, value in enumerate(_list(data[field], field, maximum=100)):
            action_ids.append(
                _validate_path(
                    value,
                    root=root,
                    name=f"{field}[{index}]",
                    allow_missing=args.allow_missing_paths,
                    kind="file",
                    suffixes={".m"},
                )
            )
    if action_ids:
        warnings.append(
            "Startup/shutdown actions require explicit code review before a project opens"
        )

    generated_ids = [
        _validate_path(
            value,
            root=root,
            name=f"generated_artifacts[{index}]",
            allow_missing=True,
        )
        for index, value in enumerate(
            _list(data["generated_artifacts"], "generated_artifacts", maximum=200)
        )
    ]
    external = [
        _string(value, f"external_interfaces[{index}]", maximum=500)
        for index, value in enumerate(
            _list(data["external_interfaces"], "external_interfaces", maximum=100)
        )
    ]
    notes = [
        _string(value, f"notes[{index}]", maximum=1000)
        for index, value in enumerate(_list(data["notes"], "notes", maximum=100))
    ]
    report = {
        "allow_missing_paths": bool(args.allow_missing_paths),
        "entry_points": entry_ids,
        "executes": False,
        "external_interface_count": len(external),
        "generated_artifacts": generated_ids,
        "license_verified": False,
        "manifest": relative_id(manifest_path, root),
        "network_accessed": False,
        "notes_count": len(notes),
        "octave_package_count": len(package_names),
        "ok": True,
        "product_count": len(product_names),
        "project_name": project_name,
        "runtime": runtime,
        "schema_version": "1.0",
        "test_paths": test_ids,
        "tool": TOOL,
        "warnings": warnings,
    }
    return report, 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Validate a strict local MATLAB/Octave project, product, and license-"
            "status manifest. The validator never launches either runtime."
        )
    )
    result.add_argument("manifest", help="local JSON manifest")
    result.add_argument("--root", default=".", help="allowed project root")
    result.add_argument(
        "--allow-missing-paths",
        action="store_true",
        help="schema-check paths without requiring them to exist",
    )
    return result


def main() -> int:
    try:
        report, status = validate(parser().parse_args())
        emit_json(report)
        return status
    except CliError as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
