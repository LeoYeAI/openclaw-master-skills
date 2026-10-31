#!/usr/bin/env python3
"""Plan bounded steady-state and spectrum calculations for QuTiP 5."""

from __future__ import annotations

import argparse
import math
from typing import Any

from _common import (
    MAX_ABS_FREQUENCY,
    MAX_FREQUENCY_POINTS,
    MAX_HILBERT_DIMENSION,
    MAX_TIME,
    QUTIP_VERSION,
    CliError,
    add_output_arguments,
    bounded_int,
    emit_json,
    finite_float,
    run_cli,
)


STEADY_METHODS = ("direct", "eigen", "svd", "power", "propagator")
LINEAR_SOLVERS = (
    "auto",
    "solve",
    "lstsq",
    "spsolve",
    "gmres",
    "lgmres",
    "bicgstab",
    "splu",
)


def create_plan(args: argparse.Namespace) -> dict[str, Any]:
    """Return a current API plan plus numerical acceptance checks."""

    dimension = bounded_int(
        args.dimension,
        name="dimension",
        minimum=2,
        maximum=MAX_HILBERT_DIMENSION,
    )
    frequency_points = bounded_int(
        args.frequency_points,
        name="frequency_points",
        minimum=2,
        maximum=MAX_FREQUENCY_POINTS,
    )
    tau_points = bounded_int(
        args.tau_points,
        name="tau_points",
        minimum=2,
        maximum=MAX_FREQUENCY_POINTS,
    )
    frequency_min = finite_float(
        args.frequency_min,
        name="frequency_min",
        minimum=-MAX_ABS_FREQUENCY,
        maximum=MAX_ABS_FREQUENCY,
    )
    frequency_max = finite_float(
        args.frequency_max,
        name="frequency_max",
        minimum=-MAX_ABS_FREQUENCY,
        maximum=MAX_ABS_FREQUENCY,
    )
    if frequency_max <= frequency_min:
        raise CliError("frequency_max must be greater than frequency_min")
    tau_max = finite_float(
        args.tau_max,
        name="tau_max",
        minimum=0.0,
        maximum=MAX_TIME,
        minimum_inclusive=False,
    )
    residual_tolerance = finite_float(
        args.residual_tolerance,
        name="residual_tolerance",
        minimum=1.0e-14,
        maximum=1.0e-3,
    )
    positivity_tolerance = finite_float(
        args.positivity_tolerance,
        name="positivity_tolerance",
        minimum=1.0e-14,
        maximum=1.0e-3,
    )

    warnings: list[str] = []
    blockers: list[str] = []
    steady_kwargs: dict[str, Any] = {"method": args.steady_method}
    if args.linear_solver != "auto":
        steady_kwargs["solver"] = args.linear_solver
    if args.steady_method == "svd" and dimension > 16:
        warnings.append("svd is dense and may be expensive beyond small systems")
    if args.degenerate_possible:
        warnings.append(
            "a small residual does not choose a unique state from a degenerate nullspace"
        )
    if args.time_dependent:
        blockers.append(
            "static steadystate/spectrum is not generally valid for a time-dependent "
            "Hamiltonian; use a periodic/Floquet or explicit long-time analysis"
        )
    if not args.stationary_confirmed:
        blockers.append("stationarity has not been confirmed for spectral analysis")

    dt = tau_max / (tau_points - 1)
    nyquist = math.pi / dt
    angular_resolution = 2.0 * math.pi / (tau_points * dt)
    requested_abs_frequency = max(abs(frequency_min), abs(frequency_max))
    if requested_abs_frequency > nyquist:
        warnings.append(
            "requested frequency range exceeds the FFT Nyquist angular frequency"
        )

    direct_plan = {
        "api": "qutip.spectrum",
        "signature": "spectrum(H, wlist, c_ops, a_op, b_op, solver='es')",
        "solver_strategy": args.direct_solver,
        "frequency_grid": {
            "minimum": frequency_min,
            "maximum": frequency_max,
            "points": frequency_points,
            "units": "angular frequency",
        },
        "checks": [
            "steady-state uniqueness or nullspace structure",
            "operator order and adjoints",
            "positive/negative-frequency convention",
            "compare es, pi, or solve strategy near singular features",
            "expand frequency range and refine spacing",
        ],
    }
    fft_plan = {
        "apis": [
            "qutip.correlation_2op_1t",
            "qutip.spectrum_correlation_fft",
        ],
        "tau_grid": {
            "start": 0.0,
            "stop": tau_max,
            "points": tau_points,
            "step": dt,
        },
        "derived_angular_frequency_limits": {
            "nyquist": nyquist,
            "approximate_bin_spacing": angular_resolution,
        },
        "checks": [
            "uniform strictly increasing tau grid",
            "correlation tail decayed before tau_max",
            "double tau_max to test resolution",
            "halve dt to test aliasing",
            "compare window choices and disclose them",
            "verify transform sign/normalization on an analytic signal",
        ],
    }

    selected: list[dict[str, Any]] = []
    if args.spectrum_mode in {"direct", "both"}:
        selected.append(direct_plan)
    if args.spectrum_mode in {"fft", "both"}:
        selected.append(fft_plan)

    return {
        "report_type": "qutip.steady_state_spectrum_plan",
        "schema_version": 1,
        "qutip_version": QUTIP_VERSION,
        "model_size": {
            "hilbert_dimension": dimension,
            "liouvillian_shape": [dimension * dimension, dimension * dimension],
        },
        "steady_state": {
            "api": "qutip.steadystate",
            "kwargs": steady_kwargs,
            "checks": {
                "liouvillian_residual_norm_at_most": residual_tolerance,
                "trace_error_at_most": residual_tolerance,
                "minimum_eigenvalue_at_least": -positivity_tolerance,
                "hermitian": True,
                "compare_multiple_initial_states": bool(args.degenerate_possible),
            },
        },
        "spectrum_mode": args.spectrum_mode,
        "spectrum_plans": selected,
        "warnings": warnings,
        "blockers": blockers,
        "status": "blocked_pending_model_evidence" if blockers else "ready_to_implement",
        "safety": {
            "planner_only": True,
            "network": False,
            "model_code_loaded": False,
            "bounded_grids": True,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan bounded QuTiP steady-state and direct/FFT spectrum checks "
            "without importing QuTiP or running a model."
        )
    )
    parser.add_argument("--dimension", type=int, default=2)
    parser.add_argument("--steady-method", choices=STEADY_METHODS, default="direct")
    parser.add_argument("--linear-solver", choices=LINEAR_SOLVERS, default="auto")
    parser.add_argument(
        "--spectrum-mode",
        choices=("direct", "fft", "both"),
        default="both",
    )
    parser.add_argument(
        "--direct-solver",
        choices=("es", "pi", "solve"),
        default="es",
    )
    parser.add_argument("--frequency-min", type=float, default=-5.0)
    parser.add_argument("--frequency-max", type=float, default=5.0)
    parser.add_argument("--frequency-points", type=int, default=1001)
    parser.add_argument("--tau-max", type=float, default=50.0)
    parser.add_argument("--tau-points", type=int, default=2001)
    parser.add_argument("--residual-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--positivity-tolerance", type=float, default=1.0e-9)
    parser.add_argument("--stationary-confirmed", action="store_true")
    parser.add_argument("--time-dependent", action="store_true")
    parser.add_argument("--degenerate-possible", action="store_true")
    add_output_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = create_plan(args)
    emit_json(report, output=args.output, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
