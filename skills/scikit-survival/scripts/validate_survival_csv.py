#!/usr/bin/env python3
"""Validate a local survival CSV and optionally write a structured NumPy array."""

from __future__ import annotations

import argparse
from typing import Any

from _common import (
    DEFAULT_SEED,
    MAX_FEATURES,
    CliError,
    atomic_save_npy,
    bounded_int,
    emit_json,
    parse_names,
    read_csv,
    structured_survival,
    synthetic_survival_frame,
)


def validate_and_convert(
    frame: Any,
    *,
    event_column: str,
    time_column: str,
    feature_columns: list[str] | None = None,
) -> tuple[Any, dict[str, Any]]:
    """Validate outcome/schema columns and build a two-field survival array."""

    if event_column == time_column:
        raise CliError("event and time columns must differ")
    missing_outcomes = [
        name for name in (event_column, time_column) if name not in frame.columns
    ]
    if missing_outcomes:
        raise CliError(f"missing outcome columns: {', '.join(missing_outcomes)}")

    if feature_columns is None:
        features = [
            str(name)
            for name in frame.columns
            if name not in {event_column, time_column}
        ]
    else:
        features = list(feature_columns)
    if len(features) > MAX_FEATURES:
        raise CliError(f"at most {MAX_FEATURES} feature columns are allowed")
    if event_column in features or time_column in features:
        raise CliError("outcome columns must not be included as features")
    missing_features = [name for name in features if name not in frame.columns]
    if missing_features:
        raise CliError(f"missing feature columns: {', '.join(missing_features)}")

    outcome = structured_survival(
        frame[event_column],
        frame[time_column],
        event_name=event_column,
        time_name=time_column,
    )
    event = outcome[event_column]
    time = outcome[time_column]
    feature_dtypes = {name: str(frame[name].dtype) for name in features}
    report = {
        "censoring": {
            "censored_count": int((~event).sum()),
            "censored_fraction": float((~event).mean()),
            "event_count": int(event.sum()),
            "event_fraction": float(event.mean()),
            "type": "right",
        },
        "columns": {
            "event": event_column,
            "features": features,
            "feature_dtypes": feature_dtypes,
            "time": time_column,
        },
        "rows": int(len(frame)),
        "schema_version": "1.0",
        "structured_dtype": [
            [name, outcome.dtype.fields[name][0].str] for name in outcome.dtype.names
        ],
        "time": {
            "maximum": float(time.max()),
            "median": float(__import__("numpy").median(time)),
            "minimum": float(time.min()),
            "strictly_positive": True,
        },
        "validation": {
            "binary_event": True,
            "finite_time": True,
            "outcome_excluded_from_features": True,
            "valid": True,
        },
    }
    return outcome, report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate right-censored survival outcomes in a bounded local CSV. "
            "With no --input, use deterministic synthetic data."
        )
    )
    parser.add_argument(
        "--input", help="Local .csv input; URLs and symlinks are rejected"
    )
    parser.add_argument("--event-column", default="event")
    parser.add_argument("--time-column", default="time")
    parser.add_argument(
        "--feature-columns",
        help="Optional explicit comma-separated features; defaults to other columns",
    )
    parser.add_argument(
        "--synthetic-rows",
        type=bounded_int(40, 20_000),
        default=240,
        help="Synthetic row count when --input is omitted (default: 240)",
    )
    parser.add_argument("--seed", type=bounded_int(0, 2**32 - 1), default=DEFAULT_SEED)
    parser.add_argument(
        "--structured-output",
        help="Optional .npy output containing the structured survival array",
    )
    parser.add_argument("--output", help="Optional .json validation report")
    parser.add_argument("--force", action="store_true", help="Replace explicit outputs")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.input:
            frame, source_name = read_csv(args.input)
            source = {"kind": "local_csv", "name": source_name}
            defaults: list[str] | None = None
        else:
            frame, numeric, categorical = synthetic_survival_frame(
                rows=args.synthetic_rows, seed=args.seed
            )
            source = {
                "kind": "synthetic",
                "network_used": False,
                "seed": args.seed,
            }
            defaults = numeric + categorical

        requested_features = parse_names(args.feature_columns)
        feature_columns = requested_features or defaults
        outcome, report = validate_and_convert(
            frame,
            event_column=args.event_column,
            time_column=args.time_column,
            feature_columns=feature_columns,
        )
        report["source"] = source
        report["structured_output"] = (
            None if args.structured_output is None else args.structured_output
        )
        if args.structured_output:
            atomic_save_npy(outcome, args.structured_output, force=args.force)
        emit_json(report, output=args.output, force=args.force)
    except CliError as exc:
        parser.error(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
