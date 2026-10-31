#!/usr/bin/env python3
"""Inspect local HypoGeniC hypothesis/result JSON without echoing raw content."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence

if __package__:
    from ._common import (
        MAX_JSON_BYTES,
        MISSING_PREDICTION,
        CliError,
        checked_input_file,
        count_values,
        emit_error,
        emit_json,
        load_json_document,
        sha256_file,
        summarize_numbers,
        validate_hypothesis_bank,
        validate_result_document,
    )
else:
    from _common import (  # type: ignore
        MAX_JSON_BYTES,
        MISSING_PREDICTION,
        CliError,
        checked_input_file,
        count_values,
        emit_error,
        emit_json,
        load_json_document,
        sha256_file,
        summarize_numbers,
        validate_hypothesis_bank,
        validate_result_document,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect bounded local output JSON. Raw hypotheses, prompts, responses, "
            "record IDs, labels, and predictions are never printed."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for name, help_text in (
        ("hypotheses", "Inspect an upstream hypothesis-bank JSON object"),
        ("results", "Inspect a strict local prediction-result JSON object"),
    ):
        child = subparsers.add_parser(name, help=help_text)
        child.add_argument("--input", required=True, help="Local strict JSON file")
        child.add_argument("--root", default=".", help="Existing local I/O boundary")
    return parser


def inspect_hypotheses(document: object, *, file_sha256: str) -> dict:
    entries = validate_hypothesis_bank(document)
    normalized_counts = Counter(entry["normalized_sha256"] for entry in entries)
    duplicate_hashes = sorted(
        digest for digest, count in normalized_counts.items() if count > 1
    )
    return {
        "ok": True,
        "inspection_kind": "hypogenic_hypothesis_bank",
        "file_sha256": file_sha256,
        "hypothesis_count": len(entries),
        "unique_normalized_hypothesis_count": len(normalized_counts),
        "normalized_duplicate_group_count": len(duplicate_hashes),
        "normalized_duplicate_groups": [
            {
                "normalized_sha256": digest,
                "count": normalized_counts[digest],
            }
            for digest in duplicate_hashes[:20]
        ],
        "duplicate_groups_truncated": len(duplicate_hashes) > 20,
        "character_length": summarize_numbers(
            [entry["characters"] for entry in entries]
        ),
        "word_count": summarize_numbers([entry["words"] for entry in entries]),
        "accuracy": summarize_numbers([entry["accuracy"] for entry in entries]),
        "reward": summarize_numbers([entry["reward"] for entry in entries]),
        "num_visits": summarize_numbers([entry["num_visits"] for entry in entries]),
        "correct_example_count": summarize_numbers(
            [entry["correct_example_count"] for entry in entries]
        ),
        "hypothesis_sha256_sample": sorted(
            entry["text_sha256"] for entry in entries
        )[:20],
        "hypothesis_sample_truncated": len(entries) > 20,
        "candidate_text_is_scientific_evidence": False,
        "raw_hypothesis_text_included": False,
        "text_interpreted_as_instructions": False,
        "network_access": False,
        "model_called": False,
    }


def inspect_results(document: object, *, file_sha256: str) -> dict:
    result = validate_result_document(document)
    records = result["records"]
    predictions = [
        (
            str(record["prediction"])
            if record["prediction"] is not None
            else MISSING_PREDICTION
        )
        for record in records
    ]
    return {
        "ok": True,
        "inspection_kind": "hypogenic_local_results",
        "file_sha256": file_sha256,
        "schema_version": result["schema_version"],
        "dataset_manifest_sha256": result["dataset_manifest_sha256"],
        "hypothesis_bank_sha256": result["hypothesis_bank_sha256"],
        "split": result["split"],
        "record_count": len(records),
        "unique_record_id_count": len({record["id"] for record in records}),
        "missing_prediction_count": sum(
            record["prediction"] is None for record in records
        ),
        "label_counts_redacted": count_values(
            str(record["label"]) for record in records
        ),
        "prediction_counts_redacted": count_values(predictions),
        "raw_records_included": False,
        "record_text_interpreted_as_instructions": False,
        "candidate_metrics_are_scientific_validation": False,
        "network_access": False,
        "model_called": False,
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        path = checked_input_file(
            args.input,
            root=args.root,
            suffixes={".json"},
            max_bytes=MAX_JSON_BYTES,
        )
        document = load_json_document(
            args.input,
            root=args.root,
            max_bytes=MAX_JSON_BYTES,
        )
        digest = sha256_file(path, max_bytes=MAX_JSON_BYTES)
        report = (
            inspect_hypotheses(document, file_sha256=digest)
            if args.command == "hypotheses"
            else inspect_results(document, file_sha256=digest)
        )
        emit_json(report)
        return 0
    except (CliError, OSError) as error:
        return emit_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
