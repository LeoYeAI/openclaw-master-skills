#!/usr/bin/env python3
"""Produce a deterministic privacy/generalization checklist without reading data."""

from __future__ import annotations

import argparse
import sys

from _common import CliError, emit_json, fail_json, finite_number, positive_int

TOOL = "sensitive_coordinates_checklist"
SENSITIVE_FLAGS = (
    "precise_points",
    "contains_addresses",
    "trajectories",
    "parcel_boundaries",
    "rare_categories",
    "linked_identifiers",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a conservative coordinate/privacy/generalization release "
            "checklist. No file, environment variable, coordinate, or network is read."
        ),
        epilog=(
            "This is a technical review aid, not a legal, ethical, or regulatory "
            "compliance determination. Exact coordinates and addresses can reidentify."
        ),
    )
    parser.add_argument(
        "--audience",
        choices=("private-analysis", "restricted-team", "public"),
        default="private-analysis",
    )
    parser.add_argument("--public-output", action="store_true")
    parser.add_argument("--precise-points", action="store_true")
    parser.add_argument("--contains-addresses", action="store_true")
    parser.add_argument("--trajectories", action="store_true")
    parser.add_argument("--parcel-boundaries", action="store_true")
    parser.add_argument("--rare-categories", action="store_true")
    parser.add_argument("--linked-identifiers", action="store_true")
    parser.add_argument(
        "--generalization",
        action="append",
        choices=(
            "aggregate",
            "coarsen-coordinates",
            "simplify",
            "suppress-small-groups",
            "remove-sensitive-fields",
            "mask-extent",
        ),
        default=[],
        help="Applied/proposed control; repeat for multiple controls",
    )
    parser.add_argument(
        "--minimum-group-size",
        type=positive_int,
        help="Smallest released aggregate group; not a compliance threshold",
    )
    parser.add_argument(
        "--tolerance",
        help="Optional positive generalization tolerance; value is not echoed",
    )
    crs = parser.add_mutually_exclusive_group()
    crs.add_argument(
        "--projected-linear-crs",
        action="store_true",
        help="Attest tolerance uses a reviewed projected linear CRS",
    )
    crs.add_argument(
        "--geographic-crs",
        action="store_true",
        help="Mark coordinates/tolerance as angular longitude-latitude",
    )
    parser.add_argument("--direct-identifiers-removed", action="store_true")
    parser.add_argument("--attribute-review-complete", action="store_true")
    parser.add_argument("--reidentification-review-complete", action="store_true")
    parser.add_argument("--visual-review-complete", action="store_true")
    parser.add_argument("--provenance-recorded", action="store_true")
    parser.add_argument("--tile-and-cdn-access-disabled", action="store_true")
    return parser


def checklist(args: argparse.Namespace) -> dict:
    public = bool(args.public_output or args.audience == "public")
    flags = {name: bool(getattr(args, name)) for name in SENSITIVE_FLAGS}
    sensitive = any(flags.values())
    controls = sorted(set(args.generalization))
    blockers: list[str] = []
    warnings: list[str] = []

    tolerance_provided = args.tolerance is not None
    if tolerance_provided:
        tolerance = finite_number(args.tolerance, name="tolerance")
        if tolerance <= 0:
            raise CliError("tolerance must be greater than zero")
        if not args.projected_linear_crs:
            blockers.append(
                "a numeric generalization tolerance requires a reviewed projected linear CRS"
            )
    if args.geographic_crs and any(
        item in controls for item in ("coarsen-coordinates", "simplify")
    ):
        blockers.append(
            "angular-coordinate generalization needs an explicit distortion-aware design"
        )

    if public and sensitive:
        if not controls:
            blockers.append("public sensitive geodata requires documented generalization")
        if not args.direct_identifiers_removed:
            blockers.append("remove direct identifiers before public release")
        if not args.attribute_review_complete:
            blockers.append("complete an attribute disclosure review")
        if not args.reidentification_review_complete:
            blockers.append("complete a linkage/reidentification review")
        if not args.visual_review_complete:
            blockers.append("inspect the rendered and serialized outputs")
        if not args.provenance_recorded:
            blockers.append("record source and generalization provenance")
    if public and not args.tile_and_cdn_access_disabled:
        blockers.append(
            "disable or explicitly approve tile/CDN access for the public artifact"
        )
    if args.contains_addresses and "remove-sensitive-fields" not in controls:
        blockers.append("exact addresses require removal from released attributes")
    if args.trajectories and "aggregate" not in controls:
        blockers.append("trajectories require aggregation or a separately reviewed model")
    spatial_controls = {
        "aggregate",
        "coarsen-coordinates",
        "mask-extent",
        "simplify",
    }
    if (
        (args.precise_points or args.parcel_boundaries)
        and public
        and not set(controls) & spatial_controls
    ):
        blockers.append("exact geometry needs spatial generalization before release")
    if (
        (args.rare_categories or args.linked_identifiers)
        and public
        and "suppress-small-groups" not in controls
    ):
        blockers.append("small/rare linked groups require suppression review")

    if args.minimum_group_size is None and public and sensitive:
        blockers.append("define and review a minimum released aggregate group size")
    elif args.minimum_group_size is not None:
        if args.minimum_group_size < 5:
            warnings.append(
                "The declared group size is very small; no universal threshold guarantees privacy."
            )
        if "suppress-small-groups" not in controls:
            warnings.append(
                "A group-size value was supplied without the suppress-small-groups control."
            )

    if not sensitive:
        warnings.append(
            "No sensitivity flags were selected; verify that classification is complete."
        )
    if not public:
        warnings.append(
            "Restricted handling still needs access control, retention, and audit policy."
        )
    warnings.extend(
        [
            "Jittering alone is not anonymization and can preserve reidentifiable patterns.",
            "Rasterization, simplification, or coordinate rounding alone does not remove sensitive attributes.",
            "HTML/SVG/GeoJSON can embed exact coordinates and properties beyond what is visibly rendered.",
        ]
    )

    return {
        "ok": not blockers,
        "tool": TOOL,
        "not_a_compliance_determination": True,
        "audience": "public" if public else args.audience,
        "sensitivity": {
            "any_flagged": sensitive,
            "categories": flags,
        },
        "controls": controls,
        "minimum_group_size_declared": args.minimum_group_size is not None,
        "tolerance": {
            "provided": tolerance_provided,
            "value_emitted": False,
            "projected_linear_crs_attested": bool(args.projected_linear_crs),
            "geographic_crs_flagged": bool(args.geographic_crs),
        },
        "review_attestations": {
            "direct_identifiers_removed": bool(args.direct_identifiers_removed),
            "attribute_review_complete": bool(args.attribute_review_complete),
            "reidentification_review_complete": bool(
                args.reidentification_review_complete
            ),
            "visual_review_complete": bool(args.visual_review_complete),
            "provenance_recorded": bool(args.provenance_recorded),
            "tile_and_cdn_access_disabled": bool(
                args.tile_and_cdn_access_disabled
            ),
        },
        "blockers": blockers,
        "warnings": warnings,
        "files_opened": False,
        "environment_read": False,
        "network_accessed": False,
        "coordinates_emitted": False,
        "identifiers_emitted": False,
    }


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = checklist(args)
        emit_json(report)
        return 0 if report["ok"] else 2
    except Exception as exc:  # noqa: BLE001 - errors are redacted at CLI boundary
        return fail_json(TOOL, exc)


if __name__ == "__main__":
    sys.exit(main())
