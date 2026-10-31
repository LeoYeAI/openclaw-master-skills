#!/usr/bin/env python3
"""Run bounded deterministic or trajectory convergence sweeps."""

from __future__ import annotations

import argparse
from typing import Any

from _common import (
    DEFAULT_SEED,
    MAX_SWEEP_RUNS,
    MAX_TIME_POINTS,
    MAX_TOTAL_SWEEP_TRAJECTORIES,
    MAX_TRAJECTORIES,
    QUTIP_VERSION,
    CliError,
    add_output_arguments,
    emit_json,
    finite_float,
    load_qutip,
    parse_csv_ints,
    run_cli,
)
from two_level_simulation import SimulationConfig, run_simulation


def _parse_rtols(value: str) -> list[float]:
    pieces = [piece.strip() for piece in value.split(",")]
    if not pieces or any(not piece for piece in pieces):
        raise CliError("rtols must be a comma-separated number list")
    if len(pieces) > MAX_SWEEP_RUNS:
        raise CliError(f"rtols may contain at most {MAX_SWEEP_RUNS} values")
    try:
        values = [float(piece) for piece in pieces]
    except ValueError as exc:
        raise CliError("rtols must contain only numbers") from exc
    checked = [
        finite_float(
            item,
            name="rtol",
            minimum=1.0e-12,
            maximum=1.0e-2,
        )
        for item in values
    ]
    if any(left <= right for left, right in zip(checked, checked[1:])):
        raise CliError("rtols must be strictly decreasing from coarse to fine")
    return checked


def _base_config(
    *,
    solver: str,
    args: argparse.Namespace,
    time_points: int,
    trajectories: int,
    rtol: float,
) -> SimulationConfig:
    return SimulationConfig(
        solver=solver,
        initial_state="excited",
        omega=finite_float(
            args.omega,
            name="omega",
            minimum=-100_000.0,
            maximum=100_000.0,
        ),
        drive=finite_float(
            args.drive,
            name="drive",
            minimum=-100_000.0,
            maximum=100_000.0,
        ),
        decay_rate=finite_float(
            args.decay_rate,
            name="decay_rate",
            minimum=0.0,
            maximum=10_000.0,
        ),
        dephasing_rate=finite_float(
            args.dephasing_rate,
            name="dephasing_rate",
            minimum=0.0,
            maximum=10_000.0,
        ),
        t_final=finite_float(
            args.t_final,
            name="t_final",
            minimum=0.0,
            maximum=100_000.0,
            minimum_inclusive=False,
        ),
        time_points=time_points,
        trajectories=trajectories,
        seed=int(args.seed),
        method=str(args.method),
        atol=max(1.0e-14, rtol * 0.01),
        rtol=rtol,
    )


def run_sweep(
    args: argparse.Namespace,
    qutip_module: Any | None = None,
) -> dict[str, Any]:
    """Execute the requested bounded convergence sweep."""

    import numpy as np

    qutip = qutip_module or load_qutip()
    acceptance = finite_float(
        args.acceptance,
        name="acceptance",
        minimum=1.0e-12,
        maximum=0.5,
    )
    seed = int(args.seed)
    if seed < 0 or seed > 2**63 - 1:
        raise CliError("seed must be from 0 through 2^63-1")

    reports: list[dict[str, Any]] = []
    run_summaries: list[dict[str, Any]] = []

    if args.mode == "deterministic":
        points = parse_csv_ints(
            args.time_points,
            name="time_points",
            minimum=2,
            maximum=MAX_TIME_POINTS,
        )
        rtols = _parse_rtols(args.rtols)
        if len(points) < 2:
            raise CliError("deterministic convergence requires at least two runs")
        if len(points) != len(rtols):
            raise CliError("time_points and rtols must contain the same number of values")
        for index, (count, rtol) in enumerate(zip(points, rtols)):
            config = _base_config(
                solver="mesolve",
                args=args,
                time_points=count,
                trajectories=1,
                rtol=rtol,
            )
            report = run_simulation(config, qutip)
            reports.append(report)
            run_summaries.append(
                {
                    "index": index,
                    "time_points": count,
                    "atol": config.atol,
                    "rtol": rtol,
                    "final_excited_population": float(
                        report["expectations"]["excited_population"][-1]
                    ),
                    "analytic_max_abs_error": report["analytic_reference"][
                        "max_abs_error"
                    ],
                    "final_state_valid": report["checks"]["final_state"].get(
                        "valid_within_tolerance", False
                    ),
                    "solver_stats": report["solver"]["stats"],
                }
            )

        reference_times = np.asarray(reports[-1]["times"], dtype=float)
        reference_values = np.asarray(
            reports[-1]["expectations"]["excited_population"],
            dtype=float,
        )
        comparisons = []
        for index, report in enumerate(reports[:-1]):
            times = np.asarray(report["times"], dtype=float)
            values = np.asarray(
                report["expectations"]["excited_population"],
                dtype=float,
            )
            reference_on_grid = np.interp(times, reference_times, reference_values)
            difference = float(np.max(np.abs(values - reference_on_grid)))
            comparisons.append(
                {
                    "run_index": index,
                    "reference_run_index": len(reports) - 1,
                    "max_abs_population_difference": difference,
                    "within_acceptance": difference <= acceptance,
                }
            )
        status = (
            "converged_at_requested_threshold"
            if comparisons and all(item["within_acceptance"] for item in comparisons)
            else "not_converged_at_requested_threshold"
        )
        design = {
            "varied": ["time_points", "rtol", "atol"],
            "paired_randomness": None,
        }
    else:
        counts = parse_csv_ints(
            args.trajectory_counts,
            name="trajectory_counts",
            minimum=2,
            maximum=MAX_TRAJECTORIES,
        )
        if len(counts) < 2:
            raise CliError("Monte Carlo convergence requires at least two runs")
        if sum(counts) > MAX_TOTAL_SWEEP_TRAJECTORIES:
            raise CliError(
                f"sum of trajectory_counts exceeds {MAX_TOTAL_SWEEP_TRAJECTORIES}"
            )
        time_points = int(args.mc_time_points)
        if not 2 <= time_points <= MAX_TIME_POINTS:
            raise CliError(
                f"mc_time_points must be from 2 through {MAX_TIME_POINTS}"
            )
        rtol = finite_float(
            args.mc_rtol,
            name="mc_rtol",
            minimum=1.0e-12,
            maximum=1.0e-2,
        )
        for index, count in enumerate(counts):
            config = _base_config(
                solver="mcsolve",
                args=args,
                time_points=time_points,
                trajectories=count,
                rtol=rtol,
            )
            if config.decay_rate == 0.0 and config.dephasing_rate == 0.0:
                raise CliError(
                    "monte-carlo mode requires a nonzero decay or dephasing rate"
                )
            report = run_simulation(config, qutip)
            reports.append(report)
            standard_error = report["trajectory_statistics"][
                "excited_population_standard_error_estimate"
            ]
            run_summaries.append(
                {
                    "index": index,
                    "trajectories_requested": count,
                    "trajectories_run": report["trajectory_statistics"][
                        "trajectories_run"
                    ],
                    "final_excited_population": float(
                        report["expectations"]["excited_population"][-1]
                    ),
                    "final_standard_error_estimate": float(standard_error[-1]),
                    "analytic_max_abs_error": report["analytic_reference"][
                        "max_abs_error"
                    ],
                    "seed_count": len(
                        report["trajectory_statistics"]["seeds"] or []
                    ),
                }
            )
        reference_value = run_summaries[-1]["final_excited_population"]
        comparisons = []
        for summary in run_summaries[:-1]:
            difference = abs(summary["final_excited_population"] - reference_value)
            uncertainty_scale = max(
                summary["final_standard_error_estimate"],
                run_summaries[-1]["final_standard_error_estimate"],
            )
            comparisons.append(
                {
                    "run_index": summary["index"],
                    "reference_run_index": len(run_summaries) - 1,
                    "absolute_final_population_difference": difference,
                    "acceptance_threshold": acceptance,
                    "within_absolute_acceptance": difference <= acceptance,
                    "difference_over_larger_standard_error": (
                        difference / uncertainty_scale
                        if uncertainty_scale > 0.0
                        else None
                    ),
                }
            )
        status = "sampling_diagnostic_complete"
        design = {
            "varied": ["ntraj"],
            "paired_randomness": (
                "The same base seed is intentionally used so QuTiP spawns "
                "comparable trajectory prefixes; these are not independent replicates."
            ),
        }

    return {
        "report_type": "qutip.convergence_sweep",
        "schema_version": 1,
        "qutip_version": QUTIP_VERSION,
        "mode": args.mode,
        "acceptance": acceptance,
        "design": design,
        "runs": run_summaries,
        "comparisons": comparisons,
        "status": status,
        "limits": {
            "maximum_runs": MAX_SWEEP_RUNS,
            "maximum_total_trajectories": MAX_TOTAL_SWEEP_TRAJECTORIES,
            "maximum_time_points_per_run": MAX_TIME_POINTS,
        },
        "interpretation": (
            "A synthetic sweep demonstrates numerical checks; repeat convergence "
            "for every cutoff and reported observable in the scientific model."
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Run a bounded synthetic QuTiP convergence sweep over deterministic "
            "tolerances/grids or Monte Carlo trajectory counts."
        )
    )
    parser.add_argument(
        "--mode",
        choices=("deterministic", "monte-carlo"),
        default="deterministic",
    )
    parser.add_argument("--omega", type=float, default=1.0)
    parser.add_argument("--drive", type=float, default=0.0)
    parser.add_argument("--decay-rate", type=float, default=0.2)
    parser.add_argument("--dephasing-rate", type=float, default=0.0)
    parser.add_argument("--t-final", type=float, default=10.0)
    parser.add_argument("--method", choices=("adams", "bdf", "lsoda"), default="adams")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--acceptance", type=float, default=1.0e-5)
    parser.add_argument(
        "--time-points",
        default="101,201,401",
        help="deterministic mode: increasing comma-separated output-grid sizes",
    )
    parser.add_argument(
        "--rtols",
        default="1e-5,1e-7,1e-9",
        help="deterministic mode: decreasing comma-separated relative tolerances",
    )
    parser.add_argument(
        "--trajectory-counts",
        default="50,100,200",
        help="Monte Carlo mode: increasing comma-separated trajectory counts",
    )
    parser.add_argument("--mc-time-points", type=int, default=101)
    parser.add_argument("--mc-rtol", type=float, default=1.0e-8)
    add_output_arguments(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_sweep(args)
    emit_json(report, output=args.output, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
