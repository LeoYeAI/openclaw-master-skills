#!/usr/bin/env python3
"""Audit a local interval manifest without exposing sample metadata values."""

from __future__ import annotations

import argparse
import sys
from collections import Counter, defaultdict
from pathlib import Path

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_FILES,
    SafetyError,
    add_path_mode_argument,
    delimiter_from_path,
    display_path,
    fail_json,
    int_type,
    local_path,
    print_json,
    read_delimited_manifest,
    sha256_file,
)


TOOL = "interval-corpus-auditor"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit a local CSV/TSV manifest for paths, assemblies, duplicate "
            "content, and patient/donor split leakage. Metadata values are not printed."
        )
    )
    parser.add_argument("--manifest", required=True, help="Local CSV/TSV manifest.")
    parser.add_argument(
        "--delimiter",
        choices=("auto", "csv", "tsv"),
        default="auto",
    )
    parser.add_argument(
        "--path-column",
        default="path",
        help="Column containing BED paths (default: path).",
    )
    parser.add_argument(
        "--assembly-column",
        default="assembly",
        help="Assembly column (default: assembly).",
    )
    parser.add_argument(
        "--expected-assembly",
        help="Optional expected assembly/accession.",
    )
    parser.add_argument(
        "--group-column",
        action="append",
        default=[],
        help="Patient/donor grouping column; repeat as needed.",
    )
    parser.add_argument(
        "--split-column",
        help="Train/validation/test column used for leakage checks.",
    )
    parser.add_argument(
        "--checksums",
        action="store_true",
        help="Hash each bounded BED to detect duplicate content.",
    )
    parser.add_argument(
        "--max-files",
        type=int_type(minimum=1, maximum=HARD_MAX_FILES, label="max-files"),
        default=10_000,
    )
    parser.add_argument(
        "--max-manifest-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-manifest-bytes",
        ),
        default=64 * 1024**2,
    )
    parser.add_argument(
        "--max-file-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-file-bytes"),
        default=2 * 1024**3,
    )
    parser.add_argument(
        "--max-total-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-total-bytes"),
        default=4 * 1024**3,
    )
    parser.add_argument(
        "--max-output-files",
        type=int_type(minimum=0, maximum=1_000, label="max-output-files"),
        default=100,
        help="Maximum bounded per-file summaries (default: 100).",
    )
    add_path_mode_argument(parser)
    return parser


def _manifest_local_path(raw: str, manifest: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    return local_path(str(candidate), kind="file")


def audit(args: argparse.Namespace) -> tuple[dict, int]:
    manifest = local_path(args.manifest, kind="file")
    delimiter = delimiter_from_path(manifest, args.delimiter)
    fields, rows = read_delimited_manifest(
        manifest,
        delimiter_name=delimiter,
        max_bytes=args.max_manifest_bytes,
        max_rows=args.max_files,
    )
    if args.path_column not in fields:
        raise SafetyError(f"path column is missing: {args.path_column}")
    if args.split_column and args.split_column not in fields:
        raise SafetyError(f"split column is missing: {args.split_column}")
    if len(args.group_column) > 20:
        raise SafetyError("at most 20 group columns may be checked")
    missing_groups = [column for column in args.group_column if column not in fields]
    if missing_groups:
        raise SafetyError(f"group columns are missing: {', '.join(missing_groups)}")
    if args.expected_assembly and not args.expected_assembly.strip():
        raise SafetyError("expected assembly must not be blank")

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    path_counts: Counter[Path] = Counter()
    assembly_counts: Counter[str] = Counter()
    group_splits: dict[str, dict[str, set[str]]] = {
        column: defaultdict(set) for column in args.group_column
    }
    missing_group_values: Counter[str] = Counter()
    split_missing = 0
    total_bytes = 0
    file_summaries: list[dict] = []
    checksum_counts: Counter[str] = Counter()

    if args.assembly_column not in fields:
        warnings["assembly_column_missing"] += 1

    for row_index, row in enumerate(rows, start=1):
        raw_path = row.get(args.path_column, "")
        if not raw_path:
            errors["blank_path"] += 1
            continue
        try:
            bed_path = _manifest_local_path(raw_path, manifest)
        except (OSError, SafetyError):
            errors["invalid_or_missing_local_path"] += 1
            continue

        path_counts[bed_path] += 1
        size = bed_path.lstat().st_size
        if size > args.max_file_bytes:
            errors["file_exceeds_byte_limit"] += 1
            continue
        total_bytes += size
        if total_bytes > args.max_total_bytes:
            raise SafetyError("corpus exceeds max-total-bytes")
        lowered_name = bed_path.name.lower()
        if not (lowered_name.endswith(".bed") or lowered_name.endswith(".bed.gz")):
            warnings["nonstandard_bed_extension"] += 1

        assembly = row.get(args.assembly_column, "") if args.assembly_column in fields else ""
        if assembly:
            if len(assembly) > 200:
                errors["assembly_value_too_long"] += 1
            else:
                assembly_counts[assembly] += 1
                if args.expected_assembly and assembly != args.expected_assembly:
                    errors["unexpected_assembly"] += 1
        elif args.assembly_column in fields:
            errors["blank_assembly"] += 1

        split = row.get(args.split_column, "") if args.split_column else ""
        if args.split_column and not split:
            split_missing += 1
        for group_column in args.group_column:
            group_value = row.get(group_column, "")
            if not group_value:
                missing_group_values[group_column] += 1
            elif args.split_column and split:
                group_splits[group_column][group_value].add(split)

        checksum: str | None = None
        if args.checksums:
            checksum, _ = sha256_file(bed_path, max_bytes=args.max_file_bytes)
            checksum_counts[checksum] += 1
        if len(file_summaries) < args.max_output_files:
            summary = {
                "path": display_path(bed_path, row_index, args.path_mode),
                "size_bytes": size,
            }
            if checksum:
                summary["sha256"] = checksum
            file_summaries.append(summary)

    duplicate_path_rows = sum(count - 1 for count in path_counts.values() if count > 1)
    if duplicate_path_rows:
        warnings["duplicate_path_rows"] = duplicate_path_rows
    if len(assembly_counts) > 1:
        errors["mixed_assemblies"] = len(assembly_counts)
    if not assembly_counts:
        warnings["assembly_not_recorded"] += 1
    if split_missing:
        errors["blank_split"] = split_missing
    for column, count in missing_group_values.items():
        if count:
            errors[f"blank_group:{column}"] = count

    leakage: dict[str, dict[str, int]] = {}
    for column, groups in group_splits.items():
        crossing = sum(1 for splits in groups.values() if len(splits) > 1)
        leakage[column] = {
            "distinct_groups": len(groups),
            "groups_crossing_splits": crossing,
        }
        if crossing:
            errors[f"group_leakage:{column}"] = crossing

    duplicate_content_groups = 0
    duplicate_content_files = 0
    if args.checksums:
        duplicate_content_groups = sum(1 for count in checksum_counts.values() if count > 1)
        duplicate_content_files = sum(
            count for count in checksum_counts.values() if count > 1
        )
        if duplicate_content_groups:
            warnings["duplicate_content_groups"] = duplicate_content_groups

    manifest_digest, manifest_size = sha256_file(
        manifest,
        max_bytes=args.max_manifest_bytes,
    )
    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "network_used": False,
            "metadata_values_emitted": False,
            "symlinks_allowed": False,
        },
        "manifest": {
            "path": display_path(manifest, 0, args.path_mode),
            "sha256": manifest_digest,
            "size_bytes": manifest_size,
            "delimiter": delimiter,
            "column_count": len(fields),
            "column_names_emitted": False,
        },
        "summary": {
            "manifest_rows": len(rows),
            "valid_local_file_rows": sum(path_counts.values()),
            "unique_local_files": len(path_counts),
            "total_input_bytes": total_bytes,
            "assembly_count": len(assembly_counts),
            "assemblies": (
                sorted(assembly_counts)[:20]
                if args.path_mode == "full"
                else "<redacted>"
            ),
            "duplicate_path_rows": duplicate_path_rows,
            "duplicate_content_groups": duplicate_content_groups,
            "duplicate_content_files": duplicate_content_files,
            "file_summaries_omitted": max(
                0,
                sum(path_counts.values()) - len(file_summaries),
            ),
        },
        "leakage_checks": leakage,
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "files": file_summaries,
        "recommendations": [
            "keep every patient/donor/biological replicate in exactly one split",
            "build universes and fit preprocessing on training groups only",
            "validate each BED against one checksummed chromosome-sizes file",
            "store full metadata only in the protected project manifest",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = audit(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
