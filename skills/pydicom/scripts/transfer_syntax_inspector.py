#!/usr/bin/env python3
"""Inspect installed pydicom transfer-syntax decoder/encoder capabilities."""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
from pathlib import Path
from typing import Any

from _common import (
    DEFAULT_MAX_INPUT_BYTES,
    HARD_MAX_INPUT_BYTES,
    SCHEMA_VERSION,
    ToolError,
    atomic_write,
    checked_input,
    checked_output,
    emit_json,
    fail_json,
    json_bytes,
    parse_size,
    paths_overlap,
    require_pydicom,
    safe_dcmread,
    valid_uid,
)

TOOL = "transfer_syntax_inspector"
KNOWN_TRANSFER_SYNTAXES = (
    "1.2.840.10008.1.2",
    "1.2.840.10008.1.2.1",
    "1.2.840.10008.1.2.1.99",
    "1.2.840.10008.1.2.2",
    "1.2.840.10008.1.2.4.50",
    "1.2.840.10008.1.2.4.51",
    "1.2.840.10008.1.2.4.57",
    "1.2.840.10008.1.2.4.70",
    "1.2.840.10008.1.2.4.80",
    "1.2.840.10008.1.2.4.81",
    "1.2.840.10008.1.2.4.90",
    "1.2.840.10008.1.2.4.91",
    "1.2.840.10008.1.2.4.201",
    "1.2.840.10008.1.2.4.202",
    "1.2.840.10008.1.2.4.203",
    "1.2.840.10008.1.2.5",
)
PACKAGES = (
    "pydicom",
    "numpy",
    "Pillow",
    "pylibjpeg",
    "pylibjpeg-libjpeg",
    "pylibjpeg-openjpeg",
    "pylibjpeg-rle",
    "pyjpegls",
    "python-gdcm",
)


def _package_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for package in PACKAGES:
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return versions


def _codec_capability(uid_value: str) -> dict[str, Any]:
    pydicom = require_pydicom()
    from pydicom.pixels import get_decoder, get_encoder

    uid = pydicom.uid.UID(uid_value)
    try:
        compressed: bool | None = bool(uid.is_compressed)
        implicit_vr: bool | None = bool(uid.is_implicit_VR)
        little_endian: bool | None = bool(uid.is_little_endian)
    except ValueError:
        compressed = None
        implicit_vr = None
        little_endian = None
    record: dict[str, Any] = {
        "compressed": compressed,
        "decoder": {
            "available": False,
            "available_plugins": [],
            "implemented": False,
            "missing_dependencies": [],
        },
        "encoder": {
            "available": False,
            "available_plugins": [],
            "implemented": False,
            "missing_dependencies": [],
        },
        "implicit_vr": implicit_vr,
        "little_endian": little_endian,
        "name": uid.name,
        "retired": uid_value == "1.2.840.10008.1.2.2",
        "uid": uid_value,
    }
    try:
        decoder = get_decoder(uid)
        record["decoder"] = {
            "available": bool(decoder.is_available),
            "available_plugins": list(decoder.available_plugins),
            "implemented": True,
            "missing_dependencies": list(decoder.missing_dependencies),
        }
    except (NotImplementedError, ValueError):
        pass
    try:
        encoder = get_encoder(uid)
        record["encoder"] = {
            "available": bool(encoder.is_available),
            "available_plugins": list(encoder.available_plugins),
            "implemented": True,
            "missing_dependencies": list(encoder.missing_dependencies),
        }
    except (NotImplementedError, ValueError):
        pass
    return record


def inspect(args: argparse.Namespace) -> dict[str, Any]:
    requested = list(args.uid or [])
    selected_uid: str | None = None
    source: Path | None = None
    if args.input:
        max_bytes = parse_size(
            args.max_input_bytes,
            name="max_input_bytes",
            maximum=HARD_MAX_INPUT_BYTES,
        )
        source = checked_input(
            args.input,
            root=args.root,
            kind="file",
            max_bytes=max_bytes,
        )
        dataset = safe_dcmread(source, stop_before_pixels=True, force=False)
        selected_uid = str(dataset.file_meta.get("TransferSyntaxUID", ""))
        if not valid_uid(selected_uid):
            raise ToolError("input Transfer Syntax UID is absent or invalid")
        requested.append(selected_uid)
    if not requested:
        requested.extend(KNOWN_TRANSFER_SYNTAXES)
    unique: list[str] = []
    for value in requested:
        if not valid_uid(value):
            raise ToolError("each --uid must be a valid numeric DICOM UID")
        if value not in unique:
            unique.append(value)
    if len(unique) > 256:
        raise ToolError("at most 256 transfer syntaxes may be inspected")
    records = [_codec_capability(value) for value in unique]
    return {
        "capability_scope": (
            "Installed plugin discovery only; image-specific bit depth, color, "
            "platform, and codestream constraints still apply."
        ),
        "input_selected_uid": selected_uid,
        "network_accessed": False,
        "ok": True,
        "package_versions": _package_versions(),
        "pixel_data_loaded": False,
        "records": records,
        "schema_version": SCHEMA_VERSION,
        "tool": TOOL,
        "warnings": [
            "An available plugin is not proof that a particular image will decode correctly.",
            "Verify decoded pixels independently before scientific or clinical use.",
            "Compression can change SOP Instance UID and image metadata; review the pydicom API behavior.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect pydicom 3.0.2 decoder/encoder implementation and installed "
            "plugin availability without loading pixel data."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python transfer_syntax_inspector.py
  python transfer_syntax_inspector.py --input image.dcm
  python transfer_syntax_inspector.py --uid 1.2.840.10008.1.2.4.90

Availability is a deployment preflight, not a pixel-correctness guarantee.
""",
    )
    parser.add_argument("--input", help="Optional local DICOM file")
    parser.add_argument(
        "--uid",
        action="append",
        help="Transfer Syntax UID to inspect; repeat as needed",
    )
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--output", "-o", help="Private JSON report path")
    parser.add_argument(
        "--max-input-bytes",
        default=str(DEFAULT_MAX_INPUT_BYTES),
        help="Maximum optional DICOM input bytes",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite an existing report only"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inspect(args)
        if args.output:
            destination = checked_output(args.output, root=args.root, force=args.force)
            if args.input:
                source = checked_input(
                    args.input,
                    root=args.root,
                    kind="file",
                    max_bytes=parse_size(
                        args.max_input_bytes,
                        name="max_input_bytes",
                        maximum=HARD_MAX_INPUT_BYTES,
                    ),
                )
                if paths_overlap(source, destination):
                    raise ToolError("report must not overwrite its input")
            atomic_write(destination, json_bytes(report), force=args.force)
            emit_json({"ok": True, "report_written": True, "tool": TOOL})
        else:
            emit_json(report)
        return 0
    except Exception as exc:  # noqa: BLE001 - sanitize unexpected library errors
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
