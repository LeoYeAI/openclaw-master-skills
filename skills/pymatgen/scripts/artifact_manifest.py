#!/usr/bin/env python3
"""Create a bounded checksum and provenance manifest for explicit local files."""

from __future__ import annotations

import argparse
import mimetypes
import platform
import re
from datetime import datetime, timezone

from _common import (
    CliError,
    DEFAULT_MAX_OUTPUT_BYTES,
    MP_API_VERSION,
    PYMATGEN_CORE_VERSION,
    PYMATGEN_VERSION,
    checked_input_file,
    checked_output_file,
    emit_json,
    package_versions,
    positive_int,
    sha256_file,
    write_json_new,
)


SENSITIVE_NAME = re.compile(
    r"(^|[._-])(?:env|secret|token|credential|api[-_]?key|private[-_]?key)"
    r"($|[._-])",
    re.IGNORECASE,
)
MAX_FILES = 100
MAX_TOTAL_BYTES = 2 * 1024 * 1024 * 1024


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Hash explicitly listed local artifacts and create a new JSON "
            "provenance manifest. Directories, symlinks, and likely secret files "
            "are refused."
        )
    )
    parser.add_argument(
        "--artifact",
        action="append",
        required=True,
        help="Local regular file to include (repeatable)",
    )
    parser.add_argument("--output", required=True, help="New manifest JSON path")
    parser.add_argument(
        "--workflow",
        required=True,
        help="Short workflow label; do not include credentials or full commands",
    )
    parser.add_argument(
        "--source",
        action="append",
        default=[],
        help="Short source/citation URL or identifier (repeatable)",
    )
    parser.add_argument(
        "--max-file-bytes",
        type=positive_int,
        default=512 * 1024 * 1024,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=positive_int,
        default=MAX_TOTAL_BYTES,
    )
    parser.add_argument(
        "--max-output-bytes",
        type=positive_int,
        default=DEFAULT_MAX_OUTPUT_BYTES,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if len(args.artifact) > MAX_FILES:
            raise CliError(f"at most {MAX_FILES} artifacts may be listed")
        if args.max_total_bytes > MAX_TOTAL_BYTES:
            raise CliError("--max-total-bytes may not exceed 2 GiB")
        if not args.workflow.strip() or len(args.workflow) > 200:
            raise CliError("--workflow must be a non-empty label of at most 200 chars")
        if any(len(source) > 2000 for source in args.source):
            raise CliError("--source values may contain at most 2000 chars")
        output = checked_output_file(args.output)
        paths = []
        seen = set()
        total = 0
        for value in args.artifact:
            path = checked_input_file(value, max_bytes=args.max_file_bytes)
            if path == output:
                raise CliError("manifest output cannot also be an input artifact")
            if SENSITIVE_NAME.search(path.name):
                raise CliError(
                    f"refusing likely credential-bearing artifact name: {path.name!r}"
                )
            if path in seen:
                raise CliError(f"duplicate artifact: {path.name!r}")
            seen.add(path)
            total += path.stat().st_size
            if total > args.max_total_bytes:
                raise CliError("artifact set exceeds --max-total-bytes")
            paths.append(path)
        records = []
        for path in paths:
            stat = path.stat()
            records.append(
                {
                    "name": path.name,
                    "bytes": stat.st_size,
                    "sha256": sha256_file(path),
                    "media_type": mimetypes.guess_type(path.name)[0],
                    "modified_at_utc": datetime.fromtimestamp(
                        stat.st_mtime, timezone.utc
                    ).isoformat(),
                }
            )
        manifest = {
            "schema_version": "1.0",
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "workflow": args.workflow,
            "sources": args.source,
            "software": {
                "expected_snapshot": {
                    "pymatgen": PYMATGEN_VERSION,
                    "pymatgen-core": PYMATGEN_CORE_VERSION,
                    "mp-api": MP_API_VERSION,
                },
                "python": platform.python_version(),
                "installed": package_versions(
                    ("pymatgen", "pymatgen-core", "mp-api")
                ),
            },
            "artifacts": records,
            "artifact_count": len(records),
            "total_bytes": total,
            "contract": {
                "network_accessed": False,
                "directories_traversed": False,
                "symlinks_followed": False,
                "artifact_contents_emitted": False,
                "credentials_read": False,
                "pickle_used": False,
                "existing_files_overwritten": False,
            },
        }
        write_json_new(output, manifest, max_bytes=args.max_output_bytes)
        emit_json(
            {
                "ok": True,
                "output": output.name,
                "artifact_count": len(records),
                "total_bytes": total,
                "overwrote_existing": False,
                "network_accessed": False,
            }
        )
        return 0
    except (CliError, OSError, TypeError, ValueError) as exc:
        emit_json({"ok": False, "error": f"{type(exc).__name__}: {exc}"[:1000]})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
