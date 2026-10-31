#!/usr/bin/env python3
"""Validate a local BED file without rewriting or uploading it."""

from __future__ import annotations

import argparse
import sys

from _common import (
    HARD_MAX_BYTES,
    HARD_MAX_RECORDS,
    SafetyError,
    add_path_mode_argument,
    display_path,
    fail_json,
    inspect_bed,
    int_type,
    load_chrom_sizes,
    local_path,
    print_json,
    sha256_file,
)


TOOL = "gtars-bed-validator"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate one local BED/BED.GZ file as 0-based half-open intervals. "
            "No input is rewritten and no network operation is available."
        )
    )
    parser.add_argument("--input", required=True, help="Local BED or BED.GZ file.")
    parser.add_argument(
        "--assembly",
        required=True,
        help="Declared reference assembly/accession for the report.",
    )
    parser.add_argument(
        "--chrom-sizes",
        help="Local two-column chrom.sizes file for contig and bounds checks.",
    )
    parser.add_argument(
        "--require-sorted",
        action="store_true",
        help="Fail if rows are not in chrom.sizes order then numeric start/end.",
    )
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Allow a BED with no data records.",
    )
    parser.add_argument(
        "--max-bytes",
        type=int_type(minimum=1, maximum=HARD_MAX_BYTES, label="max-bytes"),
        default=512 * 1024**2,
        help="Compressed and expanded byte cap (default: 512 MiB).",
    )
    parser.add_argument(
        "--max-records",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_RECORDS,
            label="max-records",
        ),
        default=1_000_000,
    )
    parser.add_argument(
        "--max-examples",
        type=int_type(minimum=0, maximum=100, label="max-examples"),
        default=10,
    )
    add_path_mode_argument(parser)
    return parser


def validate(args: argparse.Namespace) -> tuple[dict, int]:
    assembly = args.assembly.strip()
    if not assembly or len(assembly) > 200:
        raise SafetyError("assembly must contain 1-200 characters")

    bed_path = local_path(args.input, kind="file")
    chrom_sizes = None
    chrom_order = None
    chrom_sizes_report = None
    if args.chrom_sizes:
        chrom_path = local_path(args.chrom_sizes, kind="file")
        chrom_sizes, chrom_order = load_chrom_sizes(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
            max_records=min(args.max_records, 1_000_000),
        )
        chrom_digest, chrom_bytes = sha256_file(
            chrom_path,
            max_bytes=min(args.max_bytes, 128 * 1024**2),
        )
        chrom_sizes_report = {
            "path": display_path(chrom_path, 2, args.path_mode),
            "sha256": chrom_digest,
            "size_bytes": chrom_bytes,
            "contig_count": len(chrom_sizes),
        }

    summary = inspect_bed(
        bed_path,
        max_bytes=args.max_bytes,
        max_records=args.max_records,
        chrom_sizes=chrom_sizes,
        chrom_order=chrom_order,
        max_examples=args.max_examples,
    )
    errors = dict(summary.pop("errors"))
    warnings = dict(summary.pop("warnings"))
    examples = summary.pop("issue_examples")
    if summary["records"] == 0 and not args.allow_empty:
        errors["no_data_records"] = 1
    if args.require_sorted and summary["out_of_order_records"]:
        errors["sorting_required"] = summary["out_of_order_records"]

    plan: list[dict[str, str]] = [
        {
            "action": "preserve_coordinate_contract",
            "detail": "BED is 0-based, start-inclusive, end-exclusive",
        },
        {
            "action": "preserve_assembly_and_contig_names",
            "detail": "do not rename contigs or liftover implicitly",
        },
    ]
    if chrom_sizes is None:
        plan.append(
            {
                "action": "supply_chromosome_sizes",
                "detail": "required before contig and interval-bound validation",
            }
        )
    if summary["out_of_order_records"]:
        plan.append(
            {
                "action": "stable_sort_a_copy",
                "detail": "chrom.sizes order, numeric start, numeric end; retain original",
            }
        )

    report = {
        "ok": not errors,
        "tool": TOOL,
        "contract": {
            "assembly": assembly,
            "coordinate_system": "0-based-half-open",
            "input_mutated": False,
            "network_used": False,
            "subprocess_used": False,
            "symlinks_allowed": False,
            "gtars_coordinate_limit": "u32",
        },
        "input": {
            "path": display_path(bed_path, 1, args.path_mode),
            **summary,
        },
        "chromosome_sizes": chrom_sizes_report,
        "errors": errors,
        "warnings": warnings,
        "issue_examples": examples,
        "normalization_plan": plan,
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
