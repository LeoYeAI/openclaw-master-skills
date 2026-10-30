#!/usr/bin/env python3
"""Create a bounded, local-only Geniml consensus-universe execution plan."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
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
    load_chrom_sizes,
    local_path,
    print_json,
    read_delimited_manifest,
    sha256_file,
)


TOOL = "consensus-peaks-planner"
_SAFE_PREFIX = re.compile(r"^[A-Za-z0-9_.-]{1,100}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate local consensus inputs and emit argv arrays for Geniml "
            "0.8.4. No command, coverage tool, or network request is executed."
        )
    )
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--chrom-sizes", required=True)
    parser.add_argument("--assembly", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--coverage-dir")
    parser.add_argument("--likelihood-model")
    parser.add_argument("--method", choices=("cc", "ccf", "ml", "hmm"), required=True)
    parser.add_argument("--coverage-prefix", default="all")
    parser.add_argument(
        "--cutoff",
        type=int_type(minimum=1, maximum=2**31 - 1, label="cutoff"),
    )
    parser.add_argument(
        "--merge",
        type=int_type(minimum=0, maximum=10_000_000, label="merge"),
        default=0,
    )
    parser.add_argument(
        "--filter-size",
        type=int_type(minimum=0, maximum=10_000_000, label="filter-size"),
        default=0,
    )
    parser.add_argument("--no-normalize", action="store_true")
    parser.add_argument("--save-max-coverage", action="store_true")
    parser.add_argument("--path-column", default="path")
    parser.add_argument("--assembly-column", default="assembly")
    parser.add_argument(
        "--delimiter",
        choices=("auto", "csv", "tsv"),
        default="auto",
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
        "--max-total-input-bytes",
        type=int_type(
            minimum=1,
            maximum=HARD_MAX_BYTES,
            label="max-total-input-bytes",
        ),
        default=4 * 1024**3,
    )
    add_path_mode_argument(parser)
    return parser


def _manifest_bed(raw: str, manifest: Path) -> Path:
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = manifest.parent / candidate
    return local_path(str(candidate), kind="file")


def _render(path: Path, label: str, mode: str) -> str:
    if mode == "full":
        return str(path)
    if mode == "basename":
        return path.name
    return f"<{label}>"


def plan(args: argparse.Namespace) -> tuple[dict, int]:
    if not args.assembly.strip() or len(args.assembly) > 200:
        raise SafetyError("assembly must be a nonempty value of at most 200 characters")
    if not _SAFE_PREFIX.fullmatch(args.coverage_prefix):
        raise SafetyError("coverage prefix contains unsupported characters")
    if args.cutoff is not None and args.cutoff < 1:
        raise SafetyError("cutoff must be at least 1")
    if args.method != "cc" and (
        args.cutoff is not None or args.merge != 0 or args.filter_size != 0
    ):
        raise SafetyError("cutoff, merge, and filter-size apply only to method cc")
    if args.method != "hmm" and (args.no_normalize or args.save_max_coverage):
        raise SafetyError("normalization and max-coverage flags apply only to method hmm")
    if args.likelihood_model and args.method != "ml":
        raise SafetyError("likelihood-model applies only to method ml")

    manifest = local_path(args.manifest, kind="file")
    chrom_sizes = local_path(args.chrom_sizes, kind="file")
    output_dir = local_path(args.output_dir, kind="dir")
    delimiter = delimiter_from_path(manifest, args.delimiter)
    fields, rows = read_delimited_manifest(
        manifest,
        delimiter_name=delimiter,
        max_bytes=args.max_manifest_bytes,
        max_rows=args.max_files,
    )
    if args.path_column not in fields:
        raise SafetyError(f"path column is missing: {args.path_column}")
    if args.assembly_column not in fields:
        raise SafetyError(f"assembly column is missing: {args.assembly_column}")
    if not rows:
        raise SafetyError("manifest has no data rows")

    sizes, contig_order = load_chrom_sizes(
        chrom_sizes,
        max_bytes=min(args.max_manifest_bytes, 128 * 1024**2),
        max_records=1_000_000,
    )
    manifest_digest, manifest_size = sha256_file(
        manifest,
        max_bytes=args.max_manifest_bytes,
    )
    chrom_digest, chrom_size_bytes = sha256_file(
        chrom_sizes,
        max_bytes=min(args.max_manifest_bytes, 128 * 1024**2),
    )

    errors: Counter[str] = Counter()
    warnings: Counter[str] = Counter()
    local_beds: list[Path] = []
    total_input_bytes = 0
    for row in rows:
        raw_path = row.get(args.path_column, "")
        if not raw_path:
            errors["blank_path"] += 1
            continue
        if row.get(args.assembly_column, "") != args.assembly:
            errors["assembly_mismatch"] += 1
        try:
            bed = _manifest_bed(raw_path, manifest)
        except (OSError, SafetyError):
            errors["invalid_or_missing_local_bed"] += 1
            continue
        local_beds.append(bed)
        total_input_bytes += bed.lstat().st_size
        if total_input_bytes > args.max_total_input_bytes:
            raise SafetyError("BED corpus exceeds max-total-input-bytes")
    if len(set(local_beds)) != len(local_beds):
        errors["duplicate_bed_paths"] = len(local_beds) - len(set(local_beds))

    coverage_dir: Path | None = None
    required_coverage_names = (
        [f"{args.coverage_prefix}_core.bw"]
        if args.method in {"cc", "ccf"}
        else [
            f"{args.coverage_prefix}_start.bw",
            f"{args.coverage_prefix}_core.bw",
            f"{args.coverage_prefix}_end.bw",
        ]
    )
    coverage_files: list[dict[str, str | int]] = []
    if args.coverage_dir:
        coverage_dir = local_path(args.coverage_dir, kind="dir")
        for index, name in enumerate(required_coverage_names, start=1):
            try:
                coverage_file = local_path(str(coverage_dir / name), kind="file")
            except (OSError, SafetyError):
                errors[f"missing_coverage:{name}"] += 1
                continue
            digest, size = sha256_file(
                coverage_file,
                max_bytes=args.max_total_input_bytes,
            )
            coverage_files.append(
                {
                    "name": name,
                    "sha256": digest,
                    "size_bytes": size,
                }
            )
    else:
        warnings["coverage_generation_required"] += 1

    output_file = output_dir / f"universe_{args.method}.bed"
    if output_file.exists() or output_file.is_symlink():
        errors["output_file_already_exists"] += 1

    coverage_arg = (
        _render(coverage_dir, "LOCAL_COVERAGE_DIR", args.path_mode)
        if coverage_dir
        else "<LOCAL_COVERAGE_DIR>"
    )
    output_arg = _render(output_file, "OUTPUT_UNIVERSE_BED", args.path_mode)

    stages: list[dict] = [
        {
            "stage": "validate_beds",
            "executed": False,
            "instruction": (
                "Run bed_validator.py for every BED using the same chromosome sizes; "
                "reject any invalid result."
            ),
        },
        {
            "stage": "generate_coverage",
            "executed": False,
            "blocked": coverage_dir is None,
            "required_outputs": required_coverage_names,
            "instruction": (
                "Use an explicitly pinned and checksummed coverage executable. "
                "Capture its installed --help; this planner does not guess a Gtars/uniwig argv."
            ),
        },
    ]

    likelihood_path: Path | None = None
    if args.method == "ml":
        if args.likelihood_model:
            likelihood_path = local_path(args.likelihood_model, kind="file")
        else:
            likelihood_path = output_dir / "likelihood_model.tar"
            if likelihood_path.exists() or likelihood_path.is_symlink():
                errors["planned_likelihood_model_already_exists"] += 1
            lh_template = [
                "geniml",
                "lh",
                "--model-file",
                "<LIKELIHOOD_MODEL_TAR>",
                "--coverage-folder",
                "<LOCAL_COVERAGE_DIR>",
                "--coverage-prefix",
                args.coverage_prefix,
                "--file-no",
                str(len(set(local_beds))),
            ]
            lh_argv = None
            if args.path_mode == "full" and coverage_dir:
                lh_argv = [
                    "geniml",
                    "lh",
                    "--model-file",
                    str(likelihood_path),
                    "--coverage-folder",
                    str(coverage_dir),
                    "--coverage-prefix",
                    args.coverage_prefix,
                    "--file-no",
                    str(len(set(local_beds))),
                ]
            stages.append(
                {
                    "stage": "build_likelihood_model",
                    "executed": False,
                    "argv_template": lh_template,
                    "argv": lh_argv,
                }
            )

    command_template = [
        "geniml",
        "build-universe",
        args.method,
        "--coverage-folder",
        "<LOCAL_COVERAGE_DIR>",
        "--coverage-prefix",
        args.coverage_prefix,
        "--output-file",
        "<OUTPUT_UNIVERSE_BED>",
    ]
    command = [
        "geniml",
        "build-universe",
        args.method,
        "--coverage-folder",
        coverage_arg,
        "--coverage-prefix",
        args.coverage_prefix,
        "--output-file",
        output_arg,
    ]
    if args.method == "cc":
        if args.cutoff is not None:
            command_template.extend(["--cutoff", str(args.cutoff)])
            command.extend(["--cutoff", str(args.cutoff)])
            if args.cutoff > len(set(local_beds)):
                warnings["cutoff_exceeds_file_count"] += 1
        command_template.extend(["--merge", str(args.merge), "--filter-size", str(args.filter_size)])
        command.extend(["--merge", str(args.merge), "--filter-size", str(args.filter_size)])
    elif args.method == "ml":
        command_template.extend(["--model-file", "<LIKELIHOOD_MODEL_TAR>"])
        command.extend(
            [
                "--model-file",
                _render(
                    likelihood_path,
                    "LIKELIHOOD_MODEL_TAR",
                    args.path_mode,
                ),
            ]
        )
    elif args.method == "hmm":
        if args.no_normalize:
            command_template.append("--not-normalize")
            command.append("--not-normalize")
        if args.save_max_coverage:
            command_template.append("--save-max-cove")
            command.append("--save-max-cove")

    stages.append(
        {
            "stage": "build_universe",
            "executed": False,
            "argv_template": command_template,
            "argv": command if args.path_mode == "full" and coverage_dir else None,
        }
    )
    stages.append(
        {
            "stage": "validate_output",
            "executed": False,
            "instruction": (
                "Validate BED coordinates, sorting, contigs, bounds, nonempty output, "
                "and checksum before constructing a tokenizer."
            ),
        }
    )

    ready = not errors and coverage_dir is not None
    report = {
        "ok": not errors,
        "ready_to_execute": ready,
        "tool": TOOL,
        "contract": {
            "assembly": args.assembly,
            "coordinate_system": "0-based-half-open",
            "method": args.method,
            "network_used": False,
            "commands_executed": False,
            "paths_disclosed": args.path_mode == "full",
        },
        "inputs": {
            "manifest": {
                "path": display_path(manifest, 1, args.path_mode),
                "sha256": manifest_digest,
                "size_bytes": manifest_size,
            },
            "chromosome_sizes": {
                "path": display_path(chrom_sizes, 2, args.path_mode),
                "sha256": chrom_digest,
                "size_bytes": chrom_size_bytes,
                "contig_count": len(sizes),
                "first_contigs": contig_order[:10],
            },
            "bed_rows": len(rows),
            "unique_local_beds": len(set(local_beds)),
            "total_bed_bytes": total_input_bytes,
            "coverage_files": coverage_files,
        },
        "errors": dict(sorted(errors.items())),
        "warnings": dict(sorted(warnings.items())),
        "stages": stages,
        "provenance_requirements": [
            "patient/donor-grouped training-only manifest",
            "input BED and chromosome-sizes checksums",
            "coverage executable version, checksum, help output, and argv",
            "coverage-track and universe checksums",
            "Geniml/Gtars/Python lockfile and platform",
        ],
    }
    return report, 0 if not errors else 2


def main() -> int:
    args = build_parser().parse_args()
    try:
        report, exit_code = plan(args)
        print_json(report)
        return exit_code
    except (OSError, SafetyError, UnicodeError) as exc:
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
