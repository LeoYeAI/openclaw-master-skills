#!/usr/bin/env python3
"""Create an evaluation plan or score saved predictions without model calls."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

if __package__:
    from ._common import (
        MAX_CONFIG_BYTES,
        MAX_JSON_BYTES,
        SPLIT_NAMES,
        CliError,
        checked_input_file,
        classification_metrics,
        emit_error,
        emit_json,
        load_json_document,
        load_structured_document,
        sha256_file,
        validate_dataset_manifest,
        validate_result_document,
        validate_run_config,
    )
else:
    from _common import (  # type: ignore
        MAX_CONFIG_BYTES,
        MAX_JSON_BYTES,
        SPLIT_NAMES,
        CliError,
        checked_input_file,
        classification_metrics,
        emit_error,
        emit_json,
        load_json_document,
        load_structured_document,
        sha256_file,
        validate_dataset_manifest,
        validate_result_document,
        validate_run_config,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Plan split-safe evaluation or compute metrics from saved strict JSON. "
            "No HypoGeniC/provider package or model is imported or called."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan = subparsers.add_parser(
        "plan",
        help="Create a model-free, split-aware evaluation plan",
    )
    plan.add_argument("--config", required=True, help="Reviewed run policy")
    plan.add_argument("--manifest", required=True, help="Dataset manifest JSON")
    plan.add_argument("--root", default=".", help="Existing local I/O boundary")

    report = subparsers.add_parser(
        "report",
        help="Compute deterministic classification metrics from saved predictions",
    )
    report.add_argument("--results", required=True, help="Strict local result JSON")
    report.add_argument("--root", default=".", help="Existing local I/O boundary")
    report.add_argument(
        "--expected-split",
        choices=SPLIT_NAMES,
        default="test",
        help="Require this split label (default test)",
    )
    return parser


def make_evaluation_plan(
    config: dict,
    manifest: dict,
    *,
    config_sha256: str,
    manifest_sha256: str,
) -> dict:
    split_names = [split["name"] for split in manifest["splits"]]
    return {
        "ok": split_names == list(SPLIT_NAMES),
        "plan_kind": "hypogenic_model_free_evaluation",
        "schema_version": config["schema_version"],
        "config_sha256": config_sha256,
        "dataset_manifest_sha256": manifest_sha256,
        "dataset_source": manifest["source"],
        "provider": {
            "type": config["provider"]["type"],
            "model": config["provider"]["model"],
            "data_destination": config["provider"]["data_destination"],
        },
        "split_protocol": [
            {
                "split": "train",
                "allowed_use": "candidate generation and iterative updates",
                "locked": False,
            },
            {
                "split": "validation",
                "allowed_use": "method, threshold, or hypothesis selection",
                "locked": False,
            },
            {
                "split": "test",
                "allowed_use": "one final evaluation after choices are frozen",
                "locked_until_final": True,
            },
        ],
        "planned_metrics": [
            "coverage",
            "accuracy_all_records",
            "accuracy_covered_records",
            "macro_f1_all_records",
            "redacted_confusion_matrix",
        ],
        "required_provenance": [
            "immutable dataset revision",
            "dataset manifest SHA-256",
            "hypothesis bank SHA-256",
            "exact split",
            "seeds",
            "selection procedure",
            "missing-prediction handling",
            "all deviations from the plan",
        ],
        "limits": {
            "train_examples": config["limits"]["train_examples"],
            "validation_examples": config["limits"]["validation_examples"],
            "test_examples": config["limits"]["test_examples"],
            "max_hypotheses": config["limits"]["max_hypotheses"],
        },
        "execution": {
            "external_calls_authorized": False,
            "requires_separate_confirmation": True,
            "network_access": False,
            "model_called": False,
            "package_imported": False,
        },
        "interpretation": {
            "candidate_hypotheses_are_scientific_evidence": False,
            "predictive_metrics_validate_mechanisms": False,
            "independent_scientific_validation_required": True,
        },
    }


def make_report(result: dict, *, result_sha256: str) -> dict:
    metrics = classification_metrics(result["records"])
    return {
        "ok": True,
        "report_kind": "hypogenic_local_prediction_evaluation",
        "schema_version": result["schema_version"],
        "result_file_sha256": result_sha256,
        "dataset_manifest_sha256": result["dataset_manifest_sha256"],
        "hypothesis_bank_sha256": result["hypothesis_bank_sha256"],
        "split": result["split"],
        "metrics": metrics,
        "raw_labels_predictions_and_ids_included": False,
        "network_access": False,
        "model_called": False,
        "package_imported": False,
        "interpretation": {
            "scope": "classification utility on the declared saved split",
            "candidate_hypotheses_are_scientific_evidence": False,
            "metrics_validate_causality_or_novelty": False,
            "independent_scientific_validation_required": True,
        },
    }


def _plan(args: argparse.Namespace) -> int:
    config_path = checked_input_file(
        args.config,
        root=args.root,
        suffixes={".json", ".yaml", ".yml"},
        max_bytes=MAX_CONFIG_BYTES,
    )
    manifest_path = checked_input_file(
        args.manifest,
        root=args.root,
        suffixes={".json"},
        max_bytes=MAX_CONFIG_BYTES,
    )
    config = validate_run_config(
        load_structured_document(
            args.config,
            root=args.root,
            max_bytes=MAX_CONFIG_BYTES,
        )
    )
    manifest = validate_dataset_manifest(
        load_json_document(
            args.manifest,
            root=args.root,
            max_bytes=MAX_CONFIG_BYTES,
        )
    )
    report = make_evaluation_plan(
        config,
        manifest,
        config_sha256=sha256_file(config_path, max_bytes=MAX_CONFIG_BYTES),
        manifest_sha256=sha256_file(manifest_path, max_bytes=MAX_CONFIG_BYTES),
    )
    emit_json(report)
    return 0 if report["ok"] else 3


def _report(args: argparse.Namespace) -> int:
    result_path = checked_input_file(
        args.results,
        root=args.root,
        suffixes={".json"},
        max_bytes=MAX_JSON_BYTES,
    )
    result = validate_result_document(
        load_json_document(
            args.results,
            root=args.root,
            max_bytes=MAX_JSON_BYTES,
        )
    )
    if result["split"] != args.expected_split:
        raise CliError(
            f"result split {result['split']!r} does not match "
            f"--expected-split {args.expected_split!r}"
        )
    emit_json(
        make_report(
            result,
            result_sha256=sha256_file(result_path, max_bytes=MAX_JSON_BYTES),
        )
    )
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return _plan(args) if args.command == "plan" else _report(args)
    except (CliError, OSError) as error:
        return emit_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
