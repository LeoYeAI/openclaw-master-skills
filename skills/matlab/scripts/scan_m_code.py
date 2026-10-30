#!/usr/bin/env python3
"""Bounded static risk triage for MATLAB source and opaque artifacts."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from _common import (
    CliError,
    bounded_int,
    checked_input,
    checked_root,
    emit_json,
    fail_json,
    read_text,
    relative_id,
)

TOOL = "scan_m_code"
SEVERITY = {"low": 1, "medium": 2, "high": 3, "critical": 4}
SOURCE_SUFFIX = ".m"
OPAQUE_SUFFIXES = {
    ".fig": ("opaque_figure", "high", "MATLAB figure object file is opaque."),
    ".mat": ("mat_file", "high", "MAT file can contain objects and callbacks."),
    ".mlapp": ("opaque_app", "high", "MATLAB app archive is opaque and executable."),
    ".mlx": ("opaque_live_script", "high", "Live script archive is opaque."),
    ".p": ("protected_code", "high", "Protected MATLAB code is not reviewable."),
    ".prj": ("project_file", "medium", "Project metadata can configure actions."),
    ".slx": ("simulink_model", "high", "Simulink model archive can execute callbacks."),
    ".mdl": ("simulink_model", "high", "Simulink model can execute callbacks."),
}
RULES: tuple[tuple[str, str, str, re.Pattern[str]], ...] = (
    (
        "dynamic_eval",
        "critical",
        "Dynamic evaluation can execute text as MATLAB code.",
        re.compile(r"\b(?:eval|evalin)\s*\(", re.IGNORECASE),
    ),
    (
        "workspace_injection",
        "high",
        "assignin mutates another workspace and can hide data flow.",
        re.compile(r"\bassignin\s*\(", re.IGNORECASE),
    ),
    (
        "text_dispatch",
        "high",
        "Review feval/str2func inputs; text-derived dispatch executes code.",
        re.compile(r"\b(?:feval|str2func)\s*\(", re.IGNORECASE),
    ),
    (
        "shell_execution",
        "critical",
        "Shell entry point can execute external commands.",
        re.compile(r"(?:^\s*!|\b(?:system|unix|dos)\s*\()", re.IGNORECASE),
    ),
    (
        "python_execution",
        "high",
        "Python integration can execute Python/native code.",
        re.compile(r"\b(?:pyrun|pyrunfile|pyenv)\s*\(|\bpy\.", re.IGNORECASE),
    ),
    (
        "java_execution",
        "high",
        "Java integration or class-path mutation crosses the runtime boundary.",
        re.compile(
            r"\b(?:javaObject|javaMethod|javaaddpath|javarmpath|javaclasspath)"
            r"\s*\(|\bjava\.",
            re.IGNORECASE,
        ),
    ),
    (
        "dotnet_execution",
        "high",
        ".NET assembly/type access can execute external code.",
        re.compile(r"\bNET\.addAssembly\s*\(|\bSystem\.", re.IGNORECASE),
    ),
    (
        "native_execution",
        "critical",
        "Native library or MEX entry point can execute process-native code.",
        re.compile(
            r"\b(?:mex|loadlibrary|calllib|libpointer|javaaddpath)\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "code_generation",
        "high",
        "Code generation/build invokes separate products and toolchains.",
        re.compile(r"\b(?:codegen|mcc|compiler\.build)\s*\(", re.IGNORECASE),
    ),
    (
        "mat_load",
        "high",
        "Loading MAT/object data can invoke installed class deserialization code.",
        re.compile(r"(?:^\s*load(?:\s|\()|\bload\s*\()", re.IGNORECASE),
    ),
    (
        "deserialization_callback",
        "critical",
        "Object load callback/custom serialization executes during restoration.",
        re.compile(
            r"\bloadobj\s*\(|\bloadObjectImpl\s*\(|"
            r"matlab\.mixin\.CustomElementSerialization",
            re.IGNORECASE,
        ),
    ),
    (
        "network_io",
        "high",
        "Network API can transmit data or retrieve executable/untrusted content.",
        re.compile(
            r"\b(?:webread|webwrite|websave|urlread|urlwrite|tcpclient|udpport)"
            r"\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "callback",
        "medium",
        "Review callback provenance and lifecycle.",
        re.compile(
            r"\b(?:addlistener|timer)\s*\(|"
            r"\b(?:Callback|TimerFcn|StartFcn|StopFcn)\b",
            re.IGNORECASE,
        ),
    ),
    (
        "path_mutation",
        "medium",
        "Path mutation can shadow trusted functions.",
        re.compile(
            r"\b(?:addpath|rmpath|path|userpath|savepath|genpath)\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "file_mutation",
        "medium",
        "File mutation requires reviewed local paths and collision policy.",
        re.compile(
            r"\b(?:delete|movefile|copyfile|mkdir|rmdir|fopen|diary)\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "serialization_write",
        "medium",
        "Save/export can overwrite files or serialize executable objects.",
        re.compile(r"\b(?:save|savefig|exportgraphics|writetable)\s*\(", re.IGNORECASE),
    ),
    (
        "interactive_input",
        "medium",
        "Interactive input/dialog can hang or fail in batch mode.",
        re.compile(
            r"\b(?:input|uigetfile|uiputfile|questdlg|inputdlg)\s*\(",
            re.IGNORECASE,
        ),
    ),
    (
        "broad_clear",
        "low",
        "Broad clearing hides workspace/function-state dependencies.",
        re.compile(r"\bclear\s+all\b", re.IGNORECASE),
    ),
)


def _without_comments(line: str, *, in_block: bool) -> tuple[str, bool]:
    stripped = line.lstrip()
    if in_block:
        if stripped.startswith("%}"):
            return "", False
        return "", True
    if stripped.startswith("%{"):
        return "", True
    single = False
    double = False
    index = 0
    while index < len(line):
        char = line[index]
        if char == "'" and not double:
            if single and index + 1 < len(line) and line[index + 1] == "'":
                index += 2
                continue
            single = not single
        elif char == '"' and not single:
            if double and index + 1 < len(line) and line[index + 1] == '"':
                index += 2
                continue
            double = not double
        elif char == "%" and not single and not double:
            return line[:index], False
        index += 1
    return line, False


def scan_source(
    path: Path, root: Path, *, max_file_bytes: int
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    text = read_text(path, max_bytes=max_file_bytes)
    in_block = False
    for line_number, line in enumerate(text.splitlines(), start=1):
        code, in_block = _without_comments(line, in_block=in_block)
        for rule, severity, message, pattern in RULES:
            for match in pattern.finditer(code):
                findings.append(
                    {
                        "column": match.start() + 1,
                        "file": relative_id(path, root),
                        "line": line_number,
                        "message": message,
                        "rule": rule,
                        "severity": severity,
                    }
                )
    if path.name.casefold() in {"startup.m", "finish.m", "pathdef.m"}:
        findings.append(
            {
                "column": 1,
                "file": relative_id(path, root),
                "line": 1,
                "message": "Lifecycle/path file can execute implicitly.",
                "rule": "implicit_lifecycle_file",
                "severity": "high",
            }
        )
    return findings


def _opaque_finding(path: Path, root: Path) -> dict[str, Any] | None:
    suffix = path.suffix.casefold()
    details = OPAQUE_SUFFIXES.get(suffix)
    if suffix.startswith(".mex"):
        details = (
            "mex_binary",
            "critical",
            "MEX file is unreviewed native executable code.",
        )
    if details is None:
        return None
    rule, severity, message = details
    return {
        "column": None,
        "file": relative_id(path, root),
        "line": None,
        "message": message,
        "rule": rule,
        "severity": severity,
    }


def collect(
    source: Path,
    *,
    root: Path,
    recursive: bool,
    max_files: int,
    max_file_bytes: int,
    max_total_bytes: int,
) -> list[Path]:
    if source.is_file():
        suffix = source.suffix.casefold()
        supported = (
            suffix == SOURCE_SUFFIX
            or suffix in OPAQUE_SUFFIXES
            or suffix.startswith(".mex")
        )
        if not supported:
            raise CliError("input file is not .m or a recognized opaque artifact")
        size = source.stat().st_size
        if size > max_file_bytes or size > max_total_bytes:
            raise CliError(
                f"file is {size} bytes; per-file/total limits are "
                f"{max_file_bytes}/{max_total_bytes}"
            )
        return [source]
    output: list[Path] = []
    stack = [source]
    total_bytes = 0
    while stack:
        directory = stack.pop()
        try:
            entries = sorted(directory.iterdir(), key=lambda item: item.name.casefold())
        except OSError as exc:
            raise CliError(f"cannot read directory: {directory}") from exc
        for entry in entries:
            if entry.is_symlink():
                raise CliError(f"symlink encountered during scan: {entry}")
            if entry.is_dir():
                if recursive:
                    stack.append(entry)
                continue
            if not entry.is_file():
                continue
            suffix = entry.suffix.casefold()
            if suffix != SOURCE_SUFFIX and suffix not in OPAQUE_SUFFIXES and not (
                suffix.startswith(".mex")
            ):
                continue
            size = entry.stat().st_size
            if size > max_file_bytes:
                raise CliError(f"file is {size} bytes; limit is {max_file_bytes}")
            total_bytes += size
            if total_bytes > max_total_bytes:
                raise CliError(
                    f"selected files total {total_bytes} bytes; "
                    f"limit is {max_total_bytes}"
                )
            output.append(entry)
            if len(output) > max_files:
                raise CliError(f"more than {max_files} relevant files found")
    return sorted(output)


def scan(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    root = checked_root(args.root)
    source = checked_input(args.input, root=root, kind="any")
    max_files = bounded_int(
        args.max_files, name="max_files", minimum=1, maximum=5000
    )
    max_file_bytes = bounded_int(
        args.max_file_bytes,
        name="max_file_bytes",
        minimum=1,
        maximum=64 * 1024 * 1024,
    )
    max_total_bytes = bounded_int(
        args.max_total_bytes,
        name="max_total_bytes",
        minimum=1,
        maximum=256 * 1024 * 1024,
    )
    files = collect(
        source,
        root=root,
        recursive=args.recursive,
        max_files=max_files,
        max_file_bytes=max_file_bytes,
        max_total_bytes=max_total_bytes,
    )
    findings: list[dict[str, Any]] = []
    scanned_text = 0
    opaque = 0
    for path in files:
        if path.suffix.casefold() == ".m":
            scanned_text += 1
            findings.extend(
                scan_source(path, root, max_file_bytes=max_file_bytes)
            )
        else:
            finding = _opaque_finding(path, root)
            if finding:
                opaque += 1
                findings.append(finding)
    findings.sort(
        key=lambda item: (
            item["file"],
            item["line"] if item["line"] is not None else 0,
            item["column"] if item["column"] is not None else 0,
            item["rule"],
        )
    )
    counts = Counter(item["severity"] for item in findings)
    threshold = 5 if args.fail_on == "none" else SEVERITY[args.fail_on]
    failing = sum(SEVERITY[item["severity"]] >= threshold for item in findings)
    report = {
        "content_emitted": False,
        "executes": False,
        "fail_on": args.fail_on,
        "files_considered": len(files),
        "findings": findings,
        "network_accessed": False,
        "ok": failing == 0,
        "opaque_files": opaque,
        "static_only": True,
        "summary": {
            severity: counts.get(severity, 0)
            for severity in ("critical", "high", "medium", "low")
        },
        "text_files_scanned": scanned_text,
        "tool": TOOL,
        "warning": (
            "Static pattern triage can miss dynamic behavior and can produce "
            "false positives; never treat a clean report as permission to execute."
        ),
    }
    return report, 1 if failing else 0


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Statically triage reviewed MATLAB text and flag opaque artifacts. "
            "No MATLAB/Octave runtime is launched."
        )
    )
    result.add_argument("input", help="local .m file or directory")
    result.add_argument("--root", default=".", help="allowed local root")
    result.add_argument(
        "--recursive", action="store_true", help="scan nested directories"
    )
    result.add_argument(
        "--fail-on",
        choices=("critical", "high", "medium", "low", "none"),
        default="high",
    )
    result.add_argument("--max-files", default=500)
    result.add_argument("--max-file-bytes", default=4 * 1024 * 1024)
    result.add_argument("--max-total-bytes", default=32 * 1024 * 1024)
    return result


def main() -> int:
    try:
        report, status = scan(parser().parse_args())
        emit_json(report)
        return status
    except CliError as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
