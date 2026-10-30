#!/usr/bin/env python3
"""Report space-group sensitivity across explicit symmetry tolerances."""

from __future__ import annotations

import argparse
import math
from typing import Any

from _common import (
    CliError,
    DEFAULT_MAX_INPUT_BYTES,
    DEFAULT_MAX_OUTPUT_BYTES,
    DEFAULT_MAX_SITES,
    checked_output_file,
    emit_json,
    load_structure,
    positive_int,
    write_json_new,
)


def parse_tolerances(value: str, label: str) -> list[float]:
    """Parse a unique comma-separated finite positive float list."""
    pieces = [piece.strip() for piece in value.split(",") if piece.strip()]
    if not pieces:
        raise CliError(f"{label} must contain at least one value")
    result: list[float] = []
    for piece in pieces:
        try:
            number = float(piece)
        except ValueError as exc:
            raise CliError(f"{label} contains a non-number: {piece!r}") from exc
        if not math.isfinite(number) or number <= 0:
            raise CliError(f"{label} values must be finite and positive")
        if number not in result:
            result.append(number)
    if len(result) > 10:
        raise CliError(f"{label} may contain at most 10 unique values")
    return result


def analyze_grid(
    structure: Any,
    *,
    symprec_values: list[float],
    angle_values: list[float],
) -> dict[str, Any]:
    """Evaluate a bounded Cartesian product of symmetry tolerances."""
    combinations = len(symprec_values) * len(angle_values)
    if combinations > 25:
        raise CliError("symmetry tolerance grid may contain at most 25 combinations")
    from pymatgen.symmetry.analyzer import SpacegroupAnalyzer

    rows: list[dict[str, Any]] = []
    assignments: set[tuple[str, int]] = set()
    failures = 0
    for symprec in symprec_values:
        for angle in angle_values:
            try:
                analyzer = SpacegroupAnalyzer(
                    structure,
                    symprec=symprec,
                    angle_tolerance=angle,
                )
                symbol = analyzer.get_space_group_symbol()
                number = int(analyzer.get_space_group_number())
                assignments.add((symbol, number))
                rows.append(
                    {
                        "symprec_angstrom": symprec,
                        "angle_tolerance_degrees": angle,
                        "space_group_symbol": symbol,
                        "space_group_number": number,
                        "crystal_system": str(analyzer.get_crystal_system()),
                        "point_group_symbol": analyzer.get_point_group_symbol(),
                        "symmetry_operations": len(
                            analyzer.get_symmetry_operations()
                        ),
                        "equivalent_site_groups": len(
                            analyzer.get_symmetrized_structure().equivalent_indices
                        ),
                    }
                )
            except (RuntimeError, TypeError, ValueError) as exc:
                failures += 1
                rows.append(
                    {
                        "symprec_angstrom": symprec,
                        "angle_tolerance_degrees": angle,
                        "error": f"{type(exc).__name__}: {exc}"[:500],
                    }
                )
    return {
        "backend": "spglib through pymatgen",
        "grid": rows,
        "combinations": combinations,
        "failures": failures,
        "distinct_assignments": [
            {"space_group_symbol": symbol, "space_group_number": number}
            for symbol, number in sorted(assignments, key=lambda item: item[1])
        ],
        "tolerance_sensitive": len(assignments) > 1 or failures > 0,
        "interpretation": (
            "A tolerance-sensitive assignment must be reported with its exact "
            "symprec and angle_tolerance; it is not a unique structure invariant."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compare space-group assignments across a bounded tolerance grid. "
            "The structure is not standardized or written."
        )
    )
    parser.add_argument("structure_file")
    parser.add_argument("--structure-index", type=int, default=0)
    parser.add_argument(
        "--symprec",
        default="0.001,0.01,0.1",
        help="Comma-separated distance tolerances in angstrom",
    )
    parser.add_argument(
        "--angle-tolerance",
        default="1,5",
        help="Comma-separated angle tolerances in degrees",
    )
    parser.add_argument(
        "--allow-disordered",
        action="store_true",
        help="Acknowledge that symmetry assignment for disorder may be misleading",
    )
    parser.add_argument("--output", help="New JSON output; default stdout")
    parser.add_argument(
        "--max-input-bytes",
        type=positive_int,
        default=DEFAULT_MAX_INPUT_BYTES,
    )
    parser.add_argument("--max-sites", type=positive_int, default=DEFAULT_MAX_SITES)
    parser.add_argument(
        "--max-output-bytes",
        type=positive_int,
        default=DEFAULT_MAX_OUTPUT_BYTES,
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.structure_index < 0:
            raise CliError("--structure-index must be non-negative")
        symprec_values = parse_tolerances(args.symprec, "--symprec")
        angle_values = parse_tolerances(
            args.angle_tolerance, "--angle-tolerance"
        )
        structure, input_path, parse_report = load_structure(
            args.structure_file,
            structure_index=args.structure_index,
            max_bytes=args.max_input_bytes,
            max_sites=args.max_sites,
        )
        if not structure.is_ordered and not args.allow_disordered:
            raise CliError(
                "disordered structure requires --allow-disordered after reviewing "
                "occupancies and the chosen symmetry model"
            )
        report = {
            "ok": True,
            "analysis": "symmetry_tolerance_sensitivity",
            "input": parse_report,
            "structure": {
                "formula": structure.composition.reduced_formula,
                "sites": len(structure),
                "ordered": bool(structure.is_ordered),
                "periodic_boundary_conditions": [
                    bool(value) for value in structure.lattice.pbc
                ],
            },
            "symmetry": analyze_grid(
                structure,
                symprec_values=symprec_values,
                angle_values=angle_values,
            ),
            "disorder_acknowledged": bool(args.allow_disordered),
            "structure_modified": False,
        }
        if args.output:
            output = checked_output_file(args.output, input_paths=(input_path,))
            write_json_new(output, report, max_bytes=args.max_output_bytes)
            emit_json(
                {
                    "ok": True,
                    "output": output.name,
                    "overwrote_existing": False,
                    "tolerance_sensitive": report["symmetry"][
                        "tolerance_sensitive"
                    ],
                }
            )
        else:
            emit_json(report)
        return 0
    except (CliError, ImportError, OSError, RuntimeError, TypeError, ValueError) as exc:
        emit_json({"ok": False, "error": f"{type(exc).__name__}: {exc}"[:1000]})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
