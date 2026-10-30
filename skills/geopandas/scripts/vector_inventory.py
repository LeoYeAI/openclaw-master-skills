#!/usr/bin/env python3
"""Create a redacted, metadata-only inventory of one local vector dataset."""

from __future__ import annotations

import argparse
import hashlib
import sys

from _common import (
    ABSOLUTE_MAX_FEATURES,
    DEFAULT_MAX_FEATURES,
    DEFAULT_MAX_INPUT_BYTES,
    PINNED_STACK,
    bounded_limit,
    checked_input_file,
    emit_json,
    fail_json,
    inspect_local_vector,
    native_versions,
    package_versions,
    positive_int,
    sha256_file,
)

TOOL = "vector_inventory"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory one allowlisted local vector file without loading feature "
            "coordinates or emitting paths, layer names, fields, IDs, or bounds."
        ),
        epilog=(
            "URLs, GDAL VSI paths, archives, compression, symlinks, traversal, "
            "and non-allowlisted extensions are rejected. Native GDAL/GEOS/PROJ "
            "parsers remain a trust boundary; inspect only vetted local files."
        ),
    )
    parser.add_argument("input", help="Local vector or GeoParquet file")
    parser.add_argument(
        "--root",
        default=".",
        help="Existing local root that must contain the input (default: .)",
    )
    parser.add_argument(
        "--layer",
        help="Exact local layer name; required for multi-layer GDAL datasets",
    )
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
        help=f"Maximum primary-file bytes (default: {DEFAULT_MAX_INPUT_BYTES})",
    )
    parser.add_argument(
        "--max-features",
        type=positive_int,
        default=DEFAULT_MAX_FEATURES,
        help=(
            "Downstream feature-load threshold to compare with declared count "
            f"(default: {DEFAULT_MAX_FEATURES}; no features are loaded)"
        ),
    )
    return parser


def inventory(args: argparse.Namespace) -> dict:
    max_features = bounded_limit(
        args.max_features,
        name="max_features",
        maximum=ABSOLUTE_MAX_FEATURES,
    )
    path = checked_input_file(
        args.input,
        root=args.root,
        max_bytes=args.max_input_bytes,
    )
    technical = inspect_local_vector(path, layer=args.layer)
    installed = package_versions()
    declared = technical.get("declared_features")
    warnings = [
        "No feature values, coordinates, bounds, paths, layer names, or field names were emitted.",
        "GDAL/GEOS/PROJ and binary wheels are native-code trust boundaries.",
        "Driver metadata is not proof that every feature or field will parse safely.",
    ]
    if path.suffix.casefold() == ".shp":
        warnings.append(
            "The hash covers only the .shp primary file, not required sidecars."
        )
    if declared is None:
        warnings.append(
            "The driver did not provide a cheap feature count; downstream reads must enforce limit+1."
        )
    return {
        "ok": True,
        "tool": TOOL,
        "source": {
            "basename_sha256": hashlib.sha256(path.name.encode("utf-8")).hexdigest(),
            "suffix": path.suffix.casefold(),
            "primary_file_bytes": path.stat().st_size,
            "primary_file_sha256": sha256_file(path),
            "path_emitted": False,
        },
        "technical_inventory": technical,
        "resource_limits": {
            "max_input_bytes": args.max_input_bytes,
            "max_features_for_downstream_load": max_features,
            "declared_within_feature_limit": (
                None if declared is None else declared <= max_features
            ),
            "feature_data_loaded": False,
        },
        "stack": {
            "packages": installed,
            "native": native_versions(),
            "matches_pinned_snapshot": {
                name: installed.get(name) == expected
                for name, expected in PINNED_STACK.items()
            },
        },
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
        "warnings": warnings,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        emit_json(inventory(args))
        return 0
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
