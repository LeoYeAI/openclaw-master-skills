#!/usr/bin/env python3
"""Create a dependency-free, non-executing structure conversion plan."""

from __future__ import annotations

import argparse

from _common import (
    CliError,
    DEFAULT_MAX_OUTPUT_BYTES,
    checked_output_file,
    emit_json,
    positive_int,
    write_json_new,
)


FORMAT_CAPABILITIES = {
    "cif": {
        "periodic": True,
        "disorder": True,
        "oxidation_states": "format-dependent",
        "site_properties": "limited",
        "coordinate_modes": ["fractional"],
    },
    "cssr": {
        "periodic": True,
        "disorder": False,
        "oxidation_states": False,
        "site_properties": False,
        "coordinate_modes": ["fractional"],
    },
    "json": {
        "periodic": True,
        "disorder": True,
        "oxidation_states": True,
        "site_properties": True,
        "coordinate_modes": ["fractional", "cartesian-with-explicit-flag"],
    },
    "poscar": {
        "periodic": True,
        "disorder": False,
        "oxidation_states": False,
        "site_properties": "selective-dynamics/velocity-specific",
        "coordinate_modes": ["direct", "cartesian"],
    },
    "xsf": {
        "periodic": True,
        "disorder": False,
        "oxidation_states": False,
        "site_properties": False,
        "coordinate_modes": ["cartesian"],
    },
    "xyz": {
        "periodic": False,
        "disorder": False,
        "oxidation_states": False,
        "site_properties": False,
        "coordinate_modes": ["cartesian"],
    },
}


def build_plan(args: argparse.Namespace) -> dict:
    """Build a conversion contract without opening any files."""
    target = FORMAT_CAPABILITIES[args.output_format]
    blockers: list[str] = []
    risks: list[str] = []
    if args.kind == "molecule":
        blockers.append(
            "the bundled structure_converter accepts periodic Structure objects only"
        )
    if args.periodic and not target["periodic"]:
        risks.append("target drops lattice vectors and periodic boundary conditions")
    if args.disordered and target["disorder"] is not True:
        blockers.append("target cannot faithfully represent partial occupancies")
    if args.oxidation_states and target["oxidation_states"] is not True:
        risks.append("target may drop oxidation-state decoration")
    if args.site_properties and target["site_properties"] is not True:
        risks.append("target may drop arbitrary site properties")
    if args.output_format == "poscar" and args.coordinate_mode == "not-applicable":
        blockers.append("POSCAR requires direct or cartesian coordinate mode")
    if args.output_format != "poscar" and args.coordinate_mode != "not-applicable":
        blockers.append("coordinate-mode flag is only accepted for POSCAR output")
    argv = [
        "python",
        "scripts/structure_converter.py",
        args.input,
        args.output,
        "--output-format",
        args.output_format,
        "--coordinate-mode",
        args.coordinate_mode,
    ]
    if risks:
        argv.append("--allow-lossy")
    return {
        "ok": not blockers,
        "action": "io_conversion_plan",
        "executed": False,
        "files_opened": False,
        "network_accessed": False,
        "source": {
            "path_as_provided": args.input,
            "format": args.input_format,
            "kind": args.kind,
            "periodic": args.periodic,
            "has_disorder": args.disordered,
            "has_oxidation_states": args.oxidation_states,
            "has_site_properties": args.site_properties,
        },
        "target": {
            "path_as_provided": args.output,
            "format": args.output_format,
            "coordinate_mode": args.coordinate_mode,
            "capabilities": target,
        },
        "blockers": blockers,
        "representation_risks": risks,
        "reviewed_argv": argv if not blockers else None,
        "requirements_before_execution": [
            "Inspect parser warnings and all structures in multi-block CIF files.",
            "Validate units, occupancies, oxidation states, lattice, and coordinate mode.",
            "Use a new output path; never overwrite the source or an existing artifact.",
            "Round-trip and scientifically compare the result before downstream use.",
        ],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan, but do not run, a local pymatgen conversion. No input file is "
            "opened and no package import or network call occurs."
        )
    )
    parser.add_argument("--input", required=True, help="Input path for disclosure")
    parser.add_argument("--output", required=True, help="Intended new output path")
    parser.add_argument(
        "--input-format",
        required=True,
        choices=tuple(FORMAT_CAPABILITIES),
    )
    parser.add_argument(
        "--output-format",
        required=True,
        choices=tuple(FORMAT_CAPABILITIES),
    )
    parser.add_argument("--kind", choices=("structure", "molecule"), default="structure")
    periodicity = parser.add_mutually_exclusive_group()
    periodicity.add_argument("--periodic", action="store_true", default=True)
    periodicity.add_argument(
        "--nonperiodic", action="store_false", dest="periodic"
    )
    parser.add_argument("--disordered", action="store_true")
    parser.add_argument("--oxidation-states", action="store_true")
    parser.add_argument("--site-properties", action="store_true")
    parser.add_argument(
        "--coordinate-mode",
        choices=("direct", "cartesian", "not-applicable"),
        default="not-applicable",
    )
    parser.add_argument("--plan-output", help="New JSON file for this plan")
    parser.add_argument(
        "--max-output-bytes",
        type=positive_int,
        default=DEFAULT_MAX_OUTPUT_BYTES,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if "://" in args.input or "://" in args.output:
            raise CliError("conversion paths must be local, not URLs")
        plan = build_plan(args)
        if args.plan_output:
            output = checked_output_file(args.plan_output)
            write_json_new(output, plan, max_bytes=args.max_output_bytes)
            emit_json(
                {
                    "ok": plan["ok"],
                    "plan_output": output.name,
                    "executed": False,
                    "overwrote_existing": False,
                }
            )
        else:
            emit_json(plan)
        return 0 if plan["ok"] else 2
    except (CliError, OSError, TypeError, ValueError) as exc:
        emit_json(
            {
                "ok": False,
                "error": f"{type(exc).__name__}: {exc}"[:1000],
                "executed": False,
            }
        )
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
