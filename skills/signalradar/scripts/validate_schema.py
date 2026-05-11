#!/usr/bin/env python3
"""Validate SignalRadar protocol objects with lightweight checks."""

from __future__ import annotations

import argparse
import json
from typing import Any

from error_utils import emit_error


REQUIRED_FIELDS = {
    "entryspec": [
        "schema_version",
        "entry_id",
        "source",
        "market_id",
        "event_id",
        "slug",
        "status",
        "created_at",
        "updated_at",
        "version",
    ],
    "signalevent": [
        "schema_version",
        "request_id",
        "entry_id",
        "source",
        "current",
        "baseline",
        "abs_pp",
        "confidence",
        "reason",
        "ts",
        "baseline_ts",
    ],
    "intentspec": [
        "schema_version",
        "intent_id",
        "action",
        "entry_ids",
        "confirmed",
        "requested_by",
    ],
    "deliveryenvelope": [
        "schema_version",
        "delivery_id",
        "request_id",
        "idempotency_key",
        "severity",
        "route",
        "human_text",
        "machine_payload",
    ],
}


def validate_one(obj: dict[str, Any], kind: str) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS[kind]:
        if field not in obj:
            errors.append(f"missing required field: {field}")
    if kind == "signalevent":
        confidence = obj.get("confidence")
        if confidence not in {"high", "medium", "low"}:
            errors.append("confidence must be one of high|medium|low")
    if kind == "deliveryenvelope":
        severity = obj.get("severity")
        if severity not in {"P0", "P1", "P2"}:
            errors.append("severity must be one of P0|P1|P2")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="SignalRadar schema validator")
    parser.add_argument("--kind", required=True, choices=sorted(REQUIRED_FIELDS.keys()))
    parser.add_argument("--input", required=True, help="JSON file path")
    args = parser.parse_args()

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)

        objects: list[dict[str, Any]]
        if isinstance(data, list):
            objects = [x for x in data if isinstance(x, dict)]
        elif isinstance(data, dict):
            objects = [data]
        else:
            raise ValueError("input must be object or array of objects")

        total_errors = 0
        for idx, obj in enumerate(objects):
            errors = validate_one(obj, args.kind)
            if errors:
                total_errors += len(errors)
                for err in errors:
                    print(f"[{idx}] {err}")
        if total_errors > 0:
            return emit_error(
                "SR_VALIDATION_ERROR",
                f"validation failed: {total_errors} issue(s)",
                retryable=False,
                details={"kind": args.kind, "input": args.input, "issues": total_errors},
            )
        print(f"validation ok: {len(objects)} object(s)")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_VALIDATION_ERROR",
            f"validate failed: {exc}",
            retryable=False,
            details={"kind": args.kind, "input": args.input},
        )


if __name__ == "__main__":
    raise SystemExit(main())
