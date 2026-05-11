#!/usr/bin/env python3
"""Shared structured error helpers for SignalRadar scripts."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def new_request_id() -> str:
    return str(uuid.uuid4())


def build_error_envelope(
    error_code: str,
    message: str,
    *,
    request_id: str | None = None,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "error_code": error_code,
        "message": message,
        "request_id": request_id or new_request_id(),
        "retryable": retryable,
        "ts": utc_now(),
        "details": details or {},
    }


def emit_error(
    error_code: str,
    message: str,
    *,
    request_id: str | None = None,
    retryable: bool = False,
    details: dict[str, Any] | None = None,
    exit_code: int = 1,
) -> int:
    print(
        json.dumps(
            build_error_envelope(
                error_code,
                message,
                request_id=request_id,
                retryable=retryable,
                details=details,
            ),
            ensure_ascii=False,
        )
    )
    return exit_code

