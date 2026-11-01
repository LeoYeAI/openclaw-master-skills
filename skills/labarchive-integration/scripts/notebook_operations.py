#!/usr/bin/env python3
"""Safely inspect a local LabArchives LA container ZIP without extracting it.

An LA container is an attachment packaging format with lamanifest.xml. It is
not a notebook backup. This script performs no network or remote write.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import zipfile
from collections import Counter
from collections.abc import Mapping, Sequence
from pathlib import Path, PurePosixPath
from typing import Any
from xml.etree import ElementTree


MANIFEST_NAME = "lamanifest.xml"
DEFAULT_MAX_MEMBERS = 10_000
DEFAULT_MAX_TOTAL_BYTES = 4 * 1024 * 1024 * 1024
DEFAULT_MAX_MANIFEST_BYTES = 1024 * 1024
DEFAULT_MAX_INDEX_BYTES = 8 * 1024 * 1024
DEFAULT_MAX_COMPRESSION_RATIO = 1_000.0
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")


class InspectionError(ValueError):
    """Raised for invalid CLI inputs or unsafe local output paths."""


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _member_path_error(name: str) -> str | None:
    if not name or "\x00" in name:
        return "empty or NUL-containing member name"
    if "\\" in name:
        return "backslash in member name"
    if name.startswith("/") or _WINDOWS_DRIVE.match(name):
        return "absolute member path"
    parts = PurePosixPath(name).parts
    if any(part in {"", ".", ".."} for part in parts):
        return "ambiguous or traversing member path"
    return None


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = info.external_attr >> 16
    return stat.S_ISLNK(mode)


def _find_child(parent: ElementTree.Element, name: str) -> ElementTree.Element | None:
    for child in parent:
        if _local_name(child.tag) == name:
            return child
    return None


def _manifest_reference(
    entry_info: ElementTree.Element,
    element_name: str,
    archive_names: set[str],
    errors: list[str],
) -> str | None:
    element = _find_child(entry_info, element_name)
    if element is None:
        errors.append(f"manifest is missing required {element_name} element")
        return None
    reference = (element.get("name") or "").strip()
    if not reference:
        errors.append(f"manifest {element_name} has no name attribute")
        return None
    path_error = _member_path_error(reference)
    if path_error:
        errors.append(
            f"manifest {element_name} reference {reference!r} is unsafe: {path_error}"
        )
        return reference
    if reference not in archive_names:
        errors.append(
            f"manifest {element_name} reference is absent from archive: {reference!r}"
        )
    return reference


def _parse_manifest(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    archive_names: set[str],
    max_manifest_bytes: int,
    max_index_bytes: int,
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "present": True,
        "parsed": False,
        "application_file": None,
        "preview_file": None,
        "index_file": None,
        "index_utf8_valid": None,
    }
    if info.file_size > max_manifest_bytes:
        errors.append(
            "lamanifest.xml exceeds the configured manifest-size limit "
            f"({info.file_size} > {max_manifest_bytes} bytes)"
        )
        return manifest
    if info.flag_bits & 0x1:
        errors.append("lamanifest.xml is encrypted and cannot be safely inspected")
        return manifest

    raw = archive.read(info)
    upper = raw.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        errors.append("lamanifest.xml contains a forbidden DTD or entity declaration")
        return manifest

    try:
        root = ElementTree.fromstring(raw)
    except ElementTree.ParseError as exc:
        errors.append(f"lamanifest.xml is not well-formed XML: {exc}")
        return manifest

    manifest["root_element"] = _local_name(root.tag)
    if _local_name(root.tag) != "la_manifest":
        errors.append("lamanifest.xml root element must be la_manifest")
        return manifest
    entry_info = _find_child(root, "entry_info")
    if entry_info is None:
        errors.append("lamanifest.xml is missing entry_info")
        return manifest

    manifest["parsed"] = True
    for field in ("application_file", "preview_file", "index_file"):
        manifest[field] = _manifest_reference(entry_info, field, archive_names, errors)

    index_name = manifest["index_file"]
    if isinstance(index_name, str) and index_name in archive_names:
        index_info = archive.getinfo(index_name)
        if index_info.flag_bits & 0x1:
            errors.append("manifest index_file is encrypted")
        elif index_info.file_size > max_index_bytes:
            warnings.append(
                "index_file UTF-8 validation skipped because it exceeds the "
                f"configured limit ({index_info.file_size} > {max_index_bytes} bytes)"
            )
        else:
            try:
                archive.read(index_info).decode("utf-8")
            except UnicodeDecodeError as exc:
                errors.append(f"index_file is not valid UTF-8: {exc}")
                manifest["index_utf8_valid"] = False
            else:
                manifest["index_utf8_valid"] = True
    return manifest


def inspect_container(
    input_path: Path,
    *,
    max_members: int = DEFAULT_MAX_MEMBERS,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_manifest_bytes: int = DEFAULT_MAX_MANIFEST_BYTES,
    max_index_bytes: int = DEFAULT_MAX_INDEX_BYTES,
    max_compression_ratio: float = DEFAULT_MAX_COMPRESSION_RATIO,
) -> dict[str, Any]:
    """Inspect an LA container and return a JSON-serializable report."""

    if (
        min(
            max_members,
            max_total_bytes,
            max_manifest_bytes,
            max_index_bytes,
        )
        <= 0
    ):
        raise InspectionError("all size/member limits must be positive")
    if max_compression_ratio <= 0:
        raise InspectionError("compression-ratio limit must be positive")

    resolved = input_path.expanduser().resolve(strict=True)
    if not resolved.is_file():
        raise InspectionError(f"input is not a regular file: {resolved}")

    errors: list[str] = []
    warnings: list[str] = []
    with zipfile.ZipFile(resolved, "r") as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        name_counts = Counter(names)
        duplicates = sorted(name for name, count in name_counts.items() if count > 1)
        if duplicates:
            errors.append(f"duplicate archive member names: {duplicates!r}")

        if len(infos) > max_members:
            errors.append(
                f"archive member count exceeds limit ({len(infos)} > {max_members})"
            )

        total_uncompressed = sum(info.file_size for info in infos)
        total_compressed = sum(info.compress_size for info in infos)
        if total_uncompressed > max_total_bytes:
            errors.append(
                "total uncompressed size exceeds limit "
                f"({total_uncompressed} > {max_total_bytes} bytes)"
            )

        unsafe_members: list[dict[str, str]] = []
        encrypted_members: list[str] = []
        symlink_members: list[str] = []
        high_ratio_members: list[dict[str, Any]] = []
        for info in infos:
            path_error = _member_path_error(info.filename)
            if path_error:
                unsafe_members.append({"name": info.filename, "reason": path_error})
            if info.flag_bits & 0x1:
                encrypted_members.append(info.filename)
            if _is_symlink(info):
                symlink_members.append(info.filename)

            if info.file_size:
                ratio = (
                    float("inf")
                    if info.compress_size == 0
                    else info.file_size / info.compress_size
                )
                if ratio > max_compression_ratio:
                    high_ratio_members.append(
                        {
                            "name": info.filename,
                            "ratio": None if ratio == float("inf") else round(ratio, 2),
                        }
                    )

        if unsafe_members:
            errors.append("archive contains unsafe member paths")
        if encrypted_members:
            errors.append("archive contains encrypted members")
        if symlink_members:
            errors.append("archive contains symbolic-link members")
        if high_ratio_members:
            errors.append("archive contains members above the compression-ratio limit")

        manifest_infos = [info for info in infos if info.filename == MANIFEST_NAME]
        if not manifest_infos:
            errors.append(f"archive is missing required {MANIFEST_NAME}")
            manifest: dict[str, Any] = {"present": False, "parsed": False}
        elif len(manifest_infos) > 1:
            errors.append(f"archive contains multiple {MANIFEST_NAME} members")
            manifest = {"present": True, "parsed": False}
        else:
            manifest = _parse_manifest(
                archive,
                manifest_infos[0],
                set(names),
                max_manifest_bytes,
                max_index_bytes,
                errors,
                warnings,
            )

        referenced = {
            value
            for field in ("application_file", "preview_file", "index_file")
            if isinstance((value := manifest.get(field)), str)
        }
        unreferenced = sorted(
            name for name in names if name != MANIFEST_NAME and name not in referenced
        )
        if unreferenced:
            warnings.append(
                "archive has members not referenced by lamanifest.xml; review them"
            )

    return {
        "valid": not errors,
        "input": str(resolved),
        "format": "LabArchives LA container ZIP",
        "network_request_performed": False,
        "archive": {
            "member_count": len(infos),
            "total_compressed_bytes": total_compressed,
            "total_uncompressed_bytes": total_uncompressed,
            "duplicate_members": duplicates,
            "unsafe_members": unsafe_members,
            "encrypted_members": encrypted_members,
            "symlink_members": symlink_members,
            "high_compression_ratio_members": high_ratio_members,
            "unreferenced_members": unreferenced,
        },
        "manifest": manifest,
        "limits": {
            "max_members": max_members,
            "max_total_uncompressed_bytes": max_total_bytes,
            "max_manifest_bytes": max_manifest_bytes,
            "max_index_bytes": max_index_bytes,
            "max_compression_ratio": max_compression_ratio,
        },
        "errors": errors,
        "warnings": warnings,
    }


def _write_json_safely(
    output_path: Path,
    payload: Mapping[str, Any],
    *,
    input_path: Path,
    force: bool,
    compact: bool,
) -> None:
    parent = output_path.expanduser().parent.resolve(strict=True)
    if not parent.is_dir():
        raise InspectionError(f"output parent is not a directory: {parent}")
    destination = parent / output_path.name
    if destination.resolve(strict=False) == input_path.resolve(strict=True):
        raise InspectionError("output path must not overwrite the input archive")
    if destination.is_symlink():
        raise InspectionError("refusing to write through an output symlink")
    if destination.exists() and not force:
        raise InspectionError(
            f"output already exists (use --force for a regular file): {destination}"
        )
    if destination.exists() and not destination.is_file():
        raise InspectionError("output destination is not a regular file")

    flags = os.O_WRONLY | os.O_CREAT
    flags |= os.O_TRUNC if force else os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = os.open(destination, flags, 0o600)
    os.fchmod(descriptor, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        if compact:
            json.dump(payload, stream, sort_keys=True, separators=(",", ":"))
        else:
            json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")


def _emit_json(payload: Mapping[str, Any], *, compact: bool) -> None:
    if compact:
        json.dump(payload, sys.stdout, sort_keys=True, separators=(",", ":"))
    else:
        json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def command_inspect(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    report = inspect_container(
        input_path,
        max_members=args.max_members,
        max_total_bytes=args.max_total_bytes,
        max_manifest_bytes=args.max_manifest_bytes,
        max_index_bytes=args.max_index_bytes,
        max_compression_ratio=args.max_compression_ratio,
    )
    if args.output:
        _write_json_safely(
            Path(args.output),
            report,
            input_path=input_path,
            force=args.force,
            compact=args.compact,
        )
    else:
        _emit_json(report, compact=args.compact)
    return 0 if report["valid"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a local LabArchives LA container ZIP without extracting it. "
            "This is not a notebook-backup client."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser(
        "inspect", help="validate archive safety and lamanifest.xml references"
    )
    inspect_parser.add_argument("input", help="path to a local LA container ZIP")
    inspect_parser.add_argument(
        "--output",
        help="write JSON to this existing-parent path with mode 0600",
    )
    inspect_parser.add_argument(
        "--force",
        action="store_true",
        help="replace an existing regular output file; never follow symlinks",
    )
    inspect_parser.add_argument(
        "--compact", action="store_true", help="emit compact JSON"
    )
    inspect_parser.add_argument("--max-members", type=int, default=DEFAULT_MAX_MEMBERS)
    inspect_parser.add_argument(
        "--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES
    )
    inspect_parser.add_argument(
        "--max-manifest-bytes", type=int, default=DEFAULT_MAX_MANIFEST_BYTES
    )
    inspect_parser.add_argument(
        "--max-index-bytes", type=int, default=DEFAULT_MAX_INDEX_BYTES
    )
    inspect_parser.add_argument(
        "--max-compression-ratio",
        type=float,
        default=DEFAULT_MAX_COMPRESSION_RATIO,
    )
    inspect_parser.set_defaults(handler=command_inspect)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except (
        FileNotFoundError,
        InspectionError,
        OSError,
        zipfile.BadZipFile,
        zipfile.LargeZipFile,
    ) as exc:
        _emit_json(
            {
                "valid": False,
                "error": str(exc),
                "network_request_performed": False,
            },
            compact=getattr(args, "compact", False),
        )
        return 2
    except KeyboardInterrupt:
        print('{"valid":false,"error":"cancelled"}', file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
