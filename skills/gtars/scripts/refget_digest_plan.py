#!/usr/bin/env python3
"""Validate local refget metadata and FASTA sequence digests without networking."""

from __future__ import annotations

import argparse
import base64
import hashlib
import re
import sys
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    int_type,
    iter_text_lines,
    load_json,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-refget-digest-plan"
_SHA512T24U = re.compile(r"^[A-Za-z0-9_-]{32}$")
_MD5 = re.compile(r"^[0-9a-f]{32}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate a local refget metadata JSON document and optionally compare "
            "it with a local FASTA. No store is opened and no endpoint is contacted."
        )
    )
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--fasta", help="Optional local FASTA or FASTA.GZ.")
    parser.add_argument("--assembly", required=True)
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=5_000_000,
        help="Maximum FASTA text lines (default: 5,000,000).",
    )
    add_path_mode_argument(parser)
    return parser


def sha512t24u(sequence: bytes) -> str:
    """Return the unprefixed GA4GH sha512t24u digest used by gtars."""
    digest = hashlib.sha512(sequence.upper()).digest()[:24]
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def _normalize_expected_digest(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    if value.lower().startswith("sq."):
        value = value[3:]
    return value if _SHA512T24U.fullmatch(value) else None


def _read_fasta(
    path: Path,
    *,
    max_bytes: int,
    max_records: int,
) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    name: str | None = None
    chunks: list[bytes] = []
    names: set[str] = set()

    def finish() -> None:
        nonlocal name, chunks
        if name is None:
            return
        sequence = b"".join(chunks).upper()
        if not sequence:
            raise SafetyError("FASTA contains an empty sequence")
        records.append(
            {
                "name": name,
                "length": len(sequence),
                "sha512t24u": sha512t24u(sequence),
                "md5": hashlib.md5(sequence).hexdigest(),
            }
        )

    for line_number, line in iter_text_lines(
        path,
        max_bytes=max_bytes,
        max_records=max_records,
    ):
        if line.startswith(">"):
            finish()
            header = line[1:].strip()
            candidate = header.split(maxsplit=1)[0] if header else ""
            if not candidate or len(candidate) > 1_000:
                raise SafetyError(f"invalid FASTA name at line {line_number}")
            if candidate in names:
                raise SafetyError("duplicate FASTA sequence name")
            names.add(candidate)
            name = candidate
            chunks = []
            continue
        if name is None:
            if line.strip():
                raise SafetyError("FASTA sequence data appears before the first header")
            continue
        compact = "".join(line.split())
        try:
            encoded = compact.encode("ascii")
        except UnicodeEncodeError as exc:
            raise SafetyError(
                f"non-ASCII FASTA sequence near line {line_number}"
            ) from exc
        if any(byte < 33 or byte > 126 for byte in encoded):
            raise SafetyError(f"invalid FASTA sequence byte near line {line_number}")
        chunks.append(encoded)
    finish()
    if not records:
        raise SafetyError("FASTA contains no sequences")
    return records


def validate(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")
    metadata_path = local_path(args.metadata, kind="file")
    document = load_json(
        metadata_path,
        max_bytes=min(args.max_bytes, 64 * 1024**2),
    )
    if not isinstance(document, dict):
        raise SafetyError("metadata root must be a JSON object")

    errors: dict[str, int] = {}
    warnings: dict[str, int] = {}
    if document.get("schema_version") != "1.0":
        errors["metadata:unsupported_schema_version"] = 1
    if document.get("assembly") != assembly:
        errors["metadata:assembly_mismatch"] = 1
    if document.get("coordinate_system") != "0-based-half-open":
        errors["metadata:coordinate_system_mismatch"] = 1

    collection_digest = document.get("collection_digest")
    if not isinstance(collection_digest, str) or not _SHA512T24U.fullmatch(
        collection_digest
    ):
        errors["metadata:invalid_collection_digest_shape"] = 1
    else:
        warnings["collection_digest_shape_only_not_recomputed"] = 1

    expected = document.get("sequences")
    if not isinstance(expected, list) or not expected:
        raise SafetyError("metadata.sequences must be a nonempty array")
    if len(expected) > args.max_records:
        raise SafetyError("metadata sequence count exceeds max-records")

    expected_by_name: dict[str, dict] = {}
    for item in expected:
        if not isinstance(item, dict):
            errors["metadata:non_object_sequence_record"] = (
                errors.get("metadata:non_object_sequence_record", 0) + 1
            )
            continue
        name = item.get("name")
        length = item.get("length")
        digest = _normalize_expected_digest(item.get("sha512t24u"))
        md5 = item.get("md5")
        if not isinstance(name, str) or not name or len(name) > 1_000:
            errors["metadata:invalid_sequence_name"] = (
                errors.get("metadata:invalid_sequence_name", 0) + 1
            )
            continue
        if name in expected_by_name:
            errors["metadata:duplicate_sequence_name"] = (
                errors.get("metadata:duplicate_sequence_name", 0) + 1
            )
            continue
        expected_by_name[name] = item
        if type(length) is not int or length < 1:
            errors["metadata:invalid_sequence_length"] = (
                errors.get("metadata:invalid_sequence_length", 0) + 1
            )
        if digest is None:
            errors["metadata:invalid_sha512t24u"] = (
                errors.get("metadata:invalid_sha512t24u", 0) + 1
            )
        if not isinstance(md5, str) or not _MD5.fullmatch(md5.lower()):
            errors["metadata:invalid_md5"] = errors.get("metadata:invalid_md5", 0) + 1

    fasta_report = None
    if args.fasta:
        fasta_path = local_path(args.fasta, kind="file")
        actual = _read_fasta(
            fasta_path,
            max_bytes=args.max_bytes,
            max_records=args.max_records,
        )
        actual_by_name = {item["name"]: item for item in actual}
        missing = set(expected_by_name) - set(actual_by_name)
        unexpected = set(actual_by_name) - set(expected_by_name)
        length_mismatch = 0
        sha_mismatch = 0
        md5_mismatch = 0
        for name in set(expected_by_name) & set(actual_by_name):
            expected_item = expected_by_name[name]
            actual_item = actual_by_name[name]
            if expected_item.get("length") != actual_item["length"]:
                length_mismatch += 1
            expected_sha = _normalize_expected_digest(
                expected_item.get("sha512t24u")
            )
            if expected_sha != actual_item["sha512t24u"]:
                sha_mismatch += 1
            expected_md5 = expected_item.get("md5")
            if (
                not isinstance(expected_md5, str)
                or expected_md5.lower() != actual_item["md5"]
            ):
                md5_mismatch += 1
        for code, count in (
            ("fasta:missing_sequences", len(missing)),
            ("fasta:unexpected_sequences", len(unexpected)),
            ("fasta:length_mismatches", length_mismatch),
            ("fasta:sha512t24u_mismatches", sha_mismatch),
            ("fasta:md5_mismatches", md5_mismatch),
        ):
            if count:
                errors[code] = count
        fasta_digest, fasta_bytes = sha256_file(
            fasta_path,
            max_bytes=args.max_bytes,
        )
        fasta_report = {
            "path": display_path(fasta_path, 2, args.path_mode),
            "sha256": fasta_digest,
            "size_bytes": fasta_bytes,
            "sequence_count": len(actual),
            "all_sequence_digests_match": not any(
                (missing, unexpected, length_mismatch, sha_mismatch, md5_mismatch)
            ),
        }
    else:
        warnings["fasta_not_supplied_digest_values_not_recomputed"] = 1

    metadata_digest, metadata_bytes = sha256_file(
        metadata_path,
        max_bytes=min(args.max_bytes, 64 * 1024**2),
    )
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "network_used": False,
            "store_opened": False,
            "cache_written": False,
            "packages_imported": False,
            "symlinks_allowed": False,
        },
        "metadata": {
            "path": display_path(metadata_path, 1, args.path_mode),
            "sha256": metadata_digest,
            "size_bytes": metadata_bytes,
            "sequence_count": len(expected_by_name),
            "collection_digest_present": isinstance(collection_digest, str),
        },
        "fasta": fasta_report,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "approved_execution_plan": [
            "prefer RefgetStore.open_local for a reviewed local store",
            "for a new store use RefgetStore.in_memory, verify, then persist explicitly",
            "before open_remote record an HTTPS allowlist, immutable revision, expected digests, cache path, byte quota, and approval",
            "treat get_substring and stream_sequence on a remote store as network reads",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, status = validate(args)
        print_json(report)
        return status
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
