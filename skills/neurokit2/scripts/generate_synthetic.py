#!/usr/bin/env python3
"""Generate deterministic, dependency-free synthetic biosignal CSV fixtures."""

from __future__ import annotations

import argparse
import math
import random
from collections.abc import Sequence
from typing import Any

from _common import (
    MAX_ROWS,
    CliError,
    emit_json,
    finite_float,
    parse_name_list,
    run_cli,
    sha256_bytes,
    write_csv,
)

MODALITIES = ("ecg", "ppg", "rsp", "eda", "emg", "trigger")
UNITS = {
    "time_s": "s",
    "ecg": "arbitrary_unit",
    "ppg": "arbitrary_unit",
    "rsp": "arbitrary_unit",
    "eda": "arbitrary_unit",
    "emg": "arbitrary_unit",
    "trigger": "binary",
}


def _gaussian(phase: float, center: float, width: float) -> float:
    distance = min(abs(phase - center), 1.0 - abs(phase - center))
    return math.exp(-0.5 * (distance / width) ** 2)


def _event_times(duration: float, interval: float) -> list[float]:
    first = interval
    return [
        first + index * interval
        for index in range(max(0, int((duration - first) // interval) + 1))
        if first + index * interval < duration
    ]


def generate_rows(
    *,
    duration: float,
    sampling_rate: float,
    heart_rate: float,
    respiratory_rate: float,
    modalities: Sequence[str],
    seed: int,
    event_interval: float,
) -> tuple[list[str], list[list[float]], list[float]]:
    """Return deterministic analytic fixtures, not validated physiology."""

    samples = round(duration * sampling_rate)
    if not 1 <= samples <= MAX_ROWS:
        raise CliError(f"synthetic row count must be between 1 and {MAX_ROWS}")
    rng = random.Random(seed)
    events = _event_times(duration, event_interval)
    cardiac_period = 60.0 / heart_rate
    respiratory_period = 60.0 / respiratory_rate
    columns = ["time_s", *modalities]
    rows: list[list[float]] = []

    for sample in range(samples):
        time_s = sample / sampling_rate
        cardiac_phase = (time_s % cardiac_period) / cardiac_period
        respiratory_phase = (time_s % respiratory_period) / respiratory_period
        values: dict[str, float] = {}

        if "ecg" in modalities:
            values["ecg"] = (
                0.12 * _gaussian(cardiac_phase, 0.18, 0.025)
                - 0.15 * _gaussian(cardiac_phase, 0.36, 0.012)
                + 1.00 * _gaussian(cardiac_phase, 0.40, 0.010)
                - 0.25 * _gaussian(cardiac_phase, 0.43, 0.014)
                + 0.30 * _gaussian(cardiac_phase, 0.68, 0.055)
                + rng.gauss(0.0, 0.008)
            )
        if "ppg" in modalities:
            pulse = max(0.0, math.sin(math.pi * cardiac_phase)) ** 2.5
            notch = 0.12 * _gaussian(cardiac_phase, 0.72, 0.035)
            values["ppg"] = pulse - notch + rng.gauss(0.0, 0.006)
        if "rsp" in modalities:
            values["rsp"] = math.sin(2 * math.pi * respiratory_phase) + rng.gauss(
                0.0, 0.01
            )
        if "eda" in modalities:
            phasic = 0.0
            for event_time in events:
                elapsed = time_s - event_time
                if elapsed >= 0:
                    phasic += (1.0 - math.exp(-elapsed / 0.45)) * math.exp(
                        -elapsed / 2.2
                    )
            values["eda"] = (
                1.0 + 0.002 * time_s + 0.15 * phasic + rng.gauss(0.0, 0.0015)
            )
        if "emg" in modalities:
            active = any(0.5 <= time_s - event_time < 1.2 for event_time in events)
            scale = 0.16 if active else 0.01
            values["emg"] = rng.gauss(0.0, scale)
        if "trigger" in modalities:
            values["trigger"] = (
                1.0
                if any(
                    0 <= time_s - event_time < max(0.02, 2.0 / sampling_rate)
                    for event_time in events
                )
                else 0.0
            )
        rows.append([time_s, *(values[name] for name in modalities)])
    return columns, rows, events


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a deterministic local CSV of analytic biosignal-like fixtures. "
            "The output is for software tests and education, not physiological validation."
        )
    )
    parser.add_argument("--output", required=True, help="local .csv output path")
    parser.add_argument("--root", default=".", help="existing local I/O boundary")
    parser.add_argument("--duration", type=float, default=30.0, help="seconds")
    parser.add_argument("--sampling-rate", type=float, default=250.0, help="Hz")
    parser.add_argument("--heart-rate", type=float, default=70.0, help="beats/min")
    parser.add_argument(
        "--respiratory-rate", type=float, default=15.0, help="breaths/min"
    )
    parser.add_argument(
        "--modalities",
        default="ecg,rsp,eda,trigger",
        help=f"comma-separated subset of: {', '.join(MODALITIES)}",
    )
    parser.add_argument("--event-interval", type=float, default=5.0, help="seconds")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--report", help="optional local .json report path")
    parser.add_argument("--force", action="store_true")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    duration = finite_float(
        args.duration, name="--duration", minimum=0.1, maximum=3600.0
    )
    sampling_rate = finite_float(
        args.sampling_rate,
        name="--sampling-rate",
        minimum=1.0,
        maximum=5000.0,
    )
    heart_rate = finite_float(
        args.heart_rate, name="--heart-rate", minimum=20.0, maximum=240.0
    )
    respiratory_rate = finite_float(
        args.respiratory_rate,
        name="--respiratory-rate",
        minimum=2.0,
        maximum=80.0,
    )
    event_interval = finite_float(
        args.event_interval,
        name="--event-interval",
        minimum=0.5,
        maximum=3600.0,
    )
    modalities = parse_name_list(args.modalities, name="--modalities")
    unknown = sorted(set(modalities) - set(MODALITIES))
    if unknown:
        raise CliError(f"unknown modalities: {', '.join(unknown)}")
    if not modalities:
        raise CliError("select at least one modality")
    if not -(2**31) <= args.seed < 2**31:
        raise CliError("--seed must be a signed 32-bit integer")

    columns, rows, event_times = generate_rows(
        duration=duration,
        sampling_rate=sampling_rate,
        heart_rate=heart_rate,
        respiratory_rate=respiratory_rate,
        modalities=modalities,
        seed=args.seed,
        event_interval=event_interval,
    )
    payload = write_csv(
        args.output,
        columns,
        rows,
        root=args.root,
        force=args.force,
    )
    report: dict[str, Any] = {
        "artifact": "synthetic_biosignal_fixture",
        "columns": columns,
        "duration_s": duration,
        "event_onsets_s": event_times,
        "path_redacted": True,
        "physiological_validation": False,
        "row_count": len(rows),
        "sampling_rate_hz": sampling_rate,
        "seed": args.seed,
        "sha256": sha256_bytes(payload),
        "units": {column: UNITS[column] for column in columns},
        "warning": (
            "Analytic waveforms are deterministic software fixtures; they do not "
            "validate a sensor, method, population, diagnosis, or medical device."
        ),
    }
    emit_json(report, output=args.report, root=args.root, force=args.force)


if __name__ == "__main__":
    raise SystemExit(run_cli(main))
