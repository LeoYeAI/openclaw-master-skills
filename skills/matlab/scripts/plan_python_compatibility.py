#!/usr/bin/env python3
"""Plan MATLAB R2026a Python compatibility without importing or starting Engine."""

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
    validate_release,
)

TOOL = "plan_python_compatibility"
PYTHON_VERSION = re.compile(r"^([0-9]{1,2})\.([0-9]{1,2})(?:\.[0-9]{1,3})?$")
PACKAGE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")


def compatibility_data() -> dict[str, Any]:
    skill_root = checked_root(Path(__file__).resolve().parents[1])
    path = checked_input(
        skill_root / "assets" / "python_compatibility_r2026a.json",
        root=skill_root,
        suffixes={".json"},
    )
    value = load_json(path)
    if not isinstance(value, dict) or value.get("schema_version") != "1.0":
        raise CliError("bundled compatibility data is invalid")
    return value


def normalize_python(value: str) -> tuple[str, str]:
    match = PYTHON_VERSION.fullmatch(value)
    if not match:
        raise CliError("Python version must look like 3.13 or 3.13.5")
    major_minor = f"{int(match.group(1))}.{int(match.group(2))}"
    return value, major_minor


def plan(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    release = validate_release(args.matlab_release)
    data = compatibility_data()
    if release != data["matlab_release"]:
        raise CliError(
            "bundled compatibility data is pinned only to R2026a; consult the "
            "official support table for another release"
        )
    requested_python, major_minor = normalize_python(args.python_version)
    engine_version = args.engine_version
    if not PACKAGE_VERSION.fullmatch(engine_version):
        raise CliError("Engine version must be a three-part numeric version")
    supported = major_minor in data["supported_python_versions"]
    exact_engine = engine_version == data["matlab_engine_package"]["version"]
    bits_ok = args.python_bits == data["python_architecture_bits"]
    implementation_ok = args.implementation == data["python_implementation"]
    software_compatible = supported and exact_engine and bits_ok and implementation_ok
    installed_ok = args.matlab_installed == "yes"
    license_ok = args.license_status == "confirmed"
    ready_to_launch = software_compatible and installed_ok and license_ok
    warnings = [
        "This static plan does not inspect PATH, PYTHONPATH, sys.path, the "
        "environment, installations, credentials, or licenses.",
        "Package installation does not install MATLAB or grant a license.",
        "MATLAB Runtime cannot host MATLAB Engine for Python.",
    ]
    if args.matlab_installed == "unknown":
        warnings.append("Installed MATLAB R2026a has not been confirmed.")
    if args.license_status == "unknown":
        warnings.append("MATLAB and required-product license availability is unknown.")
    if not supported:
        warnings.append(
            f"CPython {major_minor} is outside the R2026a supported set."
        )
    if not exact_engine:
        warnings.append(
            "Engine package version does not match the reviewed R2026a package."
        )
    if not bits_ok:
        warnings.append("R2026a Engine requires matching 64-bit Python.")
    if not implementation_ok:
        warnings.append("The reviewed interface supports CPython.")
    launch_snippet = None
    if args.include_launch_snippet:
        launch_snippet = [
            "import matlab.engine",
            "engine = matlab.engine.start_matlab()  # explicit MATLAB launch/license action",
            "try:",
            "    pass  # call one reviewed function with explicit nargout",
            "finally:",
            "    engine.quit()",
        ]
        warnings.append(
            "Launch snippet is informational and was not executed; review MATLAB "
            "startup code and obtain explicit approval before using it."
        )
    report = {
        "as_of": data["as_of"],
        "engine_launch_explicit": bool(args.include_launch_snippet),
        "engine_launch_snippet": launch_snippet,
        "executes": False,
        "implementation": args.implementation,
        "install_plan_argv": [
            "uv",
            "pip",
            "install",
            f"matlabengine=={data['matlab_engine_package']['version']}",
        ],
        "license_status": args.license_status,
        "matlab_installed": args.matlab_installed,
        "matlab_release": release,
        "network_accessed": False,
        "ok": software_compatible,
        "preinstalled_engine_path": (
            "<matlabroot>/" + data["preinstalled_engine_relative_path"]
        ),
        "python_architecture_bits": args.python_bits,
        "python_version_requested": requested_python,
        "ready_to_launch": ready_to_launch,
        "reviewed_engine_package": data["matlab_engine_package"],
        "software_compatible": software_compatible,
        "supported_python_versions": data["supported_python_versions"],
        "tool": TOOL,
        "warnings": warnings,
    }
    return report, 0 if software_compatible else 1


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Check a requested CPython and MATLAB Engine version against the "
            "bundled R2026a support record. No environment probing or launch occurs."
        )
    )
    result.add_argument("--matlab-release", default="R2026a")
    result.add_argument("--python-version", required=True)
    result.add_argument("--engine-version", default="26.1.12")
    result.add_argument("--python-bits", type=int, choices=(32, 64), default=64)
    result.add_argument("--implementation", choices=("CPython",), default="CPython")
    result.add_argument(
        "--matlab-installed",
        choices=("yes", "no", "unknown"),
        default="unknown",
    )
    result.add_argument(
        "--license-status",
        choices=("confirmed", "unavailable", "unknown"),
        default="unknown",
    )
    result.add_argument(
        "--include-launch-snippet",
        action="store_true",
        help="include, but do not execute, an explicit Engine lifecycle snippet",
    )
    return result


def main() -> int:
    try:
        report, status = plan(parser().parse_args())
        emit_json(report)
        return status
    except CliError as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
