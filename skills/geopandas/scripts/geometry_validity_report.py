#!/usr/bin/env python3
"""Audit and simulate repair of bounded local geometries with optional new output."""

from __future__ import annotations

import argparse
import hashlib
import sys
from typing import Any

from _common import (
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    CliError,
    checked_input_file,
    checked_output_file,
    crs_summary,
    duplicate_column_state,
    emit_json,
    fail_json,
    finite_number,
    geometry_state,
    load_geodataframe,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
    write_new_geopackage,
)

TOOL = "geometry_validity_report"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Audit null/empty/invalid geometry and simulate make_valid locally. "
            "Default is dry-run; --repair-output writes only a new GeoPackage."
        ),
        epilog=(
            "No coordinates, paths, IDs, or validity-reason coordinates are emitted. "
            "URLs, archives, symlinks, traversal, and overwrite are rejected."
        ),
    )
    parser.add_argument("input", help="Allowlisted local GDAL vector file")
    parser.add_argument("--root", default=".", help="Existing local I/O root")
    parser.add_argument("--layer", help="Exact input layer name")
    parser.add_argument("--id-column", help="Optional stable ID column to audit")
    parser.add_argument(
        "--method",
        choices=("linework", "structure"),
        default="linework",
        help="Shapely make_valid algorithm (default: linework)",
    )
    parser.add_argument(
        "--drop-collapsed",
        action="store_true",
        help="For structure repair only, drop lower-dimensional collapsed parts",
    )
    parser.add_argument(
        "--precision-grid",
        help=(
            "Optional positive post-repair precision grid in projected CRS units; "
            "geographic or missing CRS is rejected"
        ),
    )
    parser.add_argument(
        "--repair-output",
        help="Optional new .gpkg path; existing paths are never overwritten",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
    )
    parser.add_argument(
        "--max-output-bytes",
        type=positive_int,
        default=DEFAULT_MAX_OUTPUT_BYTES,
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
    )
    return parser


def _type_transition_count(before: Any, after: Any) -> int:
    before_types = [
        "missing" if value is None else str(value) for value in before.geom_type
    ]
    after_types = [
        "missing" if value is None else str(value) for value in after.geom_type
    ]
    return sum(left != right for left, right in zip(before_types, after_types))


def report(args: argparse.Namespace) -> dict[str, Any]:
    if args.drop_collapsed and args.method != "structure":
        raise CliError("--drop-collapsed is valid only with --method structure")
    path = checked_input_file(
        args.input,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    frame = load_geodataframe(
        path,
        layer=args.layer,
        max_features=args.max_features,
    )
    before_geometry = frame.geometry.copy()
    before = geometry_state(frame)
    id_state = duplicate_column_state(frame, args.id_column)
    crs = crs_summary(frame.crs)

    grid_size: float | None = None
    if args.precision_grid is not None:
        grid_size = finite_number(args.precision_grid, name="precision_grid")
        if grid_size <= 0:
            raise CliError("precision_grid must be greater than zero")
        if not crs["present"] or crs["geographic"] or not crs["projected"]:
            raise CliError("precision_grid requires a known projected CRS")

    repaired_frame = frame.copy()
    repaired_geometry = repaired_frame.geometry.make_valid(
        method=args.method,
        keep_collapsed=not args.drop_collapsed,
    )
    if grid_size is not None:
        repaired_geometry = repaired_geometry.set_precision(
            grid_size,
            mode="valid_output",
        )
    repaired_frame = repaired_frame.set_geometry(repaired_geometry)
    simulated = geometry_state(repaired_frame)

    output_report: dict[str, Any] = {
        "requested": args.repair_output is not None,
        "written": False,
        "path_emitted": False,
        "basename_sha256": None,
        "sha256": None,
        "roundtrip_verified": False,
    }
    if args.repair_output is not None:
        destination = checked_output_file(
            args.repair_output,
            root=args.root,
            allowed_suffixes={".gpkg"},
        )
        write_new_geopackage(
            repaired_frame,
            destination,
            max_output_bytes=args.max_output_bytes,
        )
        roundtrip = load_geodataframe(
            destination,
            layer="repaired",
            max_features=args.max_features,
        )
        roundtrip_state = geometry_state(roundtrip)
        if roundtrip_state != simulated:
            destination.unlink(missing_ok=True)
            raise CliError("roundtrip geometry-state verification failed; output removed")
        output_report = {
            "requested": True,
            "written": True,
            "path_emitted": False,
            "basename_sha256": hashlib.sha256(
                destination.name.encode("utf-8")
            ).hexdigest(),
            "sha256": sha256_file(destination),
            "roundtrip_verified": True,
        }

    return {
        "ok": True,
        "tool": TOOL,
        "dry_run": args.repair_output is None,
        "source": {
            "primary_file_sha256": sha256_file(path),
            "primary_file_bytes": path.stat().st_size,
            "path_emitted": False,
        },
        "crs": crs,
        "stable_id_audit": id_state,
        "before": before,
        "simulated_after": simulated,
        "repair_contract": {
            "method": args.method,
            "keep_collapsed": not args.drop_collapsed,
            "precision_grid": grid_size,
            "precision_grid_units": (
                "source_projected_crs_units" if grid_size is not None else None
            ),
            "type_transition_rows": _type_transition_count(
                before_geometry,
                repaired_geometry,
            ),
            "source_modified": False,
        },
        "output": output_report,
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "stack": {"packages": package_versions(), "native": native_versions()},
        "warnings": [
            "Repair can change type, dimension, component count, area, and emptiness.",
            "Validity reasons were reduced to categories; defect coordinates were not emitted.",
            "A written GeoPackage retains source attributes and coordinates and remains sensitive.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        emit_json(report(args))
        return 0
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
