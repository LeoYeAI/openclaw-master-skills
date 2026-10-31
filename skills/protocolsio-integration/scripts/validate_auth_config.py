#!/usr/bin/env python3
"""Validate named protocols.io credential/configuration variables locally."""

from __future__ import annotations

import argparse
import os
from typing import Mapping, Sequence

try:
    from ._common import (
        ACCESS_TOKEN_ENV,
        DEFAULT_ORIGIN,
        SafetyError,
        credential_status,
        emit_error,
        emit_json,
        validate_origin,
    )
except ImportError:
    from _common import (  # type: ignore
        ACCESS_TOKEN_ENV,
        DEFAULT_ORIGIN,
        SafetyError,
        credential_status,
        emit_error,
        emit_json,
        validate_origin,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate protocols.io named environment variables without network "
            "access, .env loading, or secret output."
        )
    )
    parser.add_argument(
        "--origin",
        default=DEFAULT_ORIGIN,
        help="HTTPS API origin (default: %(default)s).",
    )
    parser.add_argument(
        "--tenant-origin",
        help=("Optional organization/VPC origin such as https://tenant.protocols.io."),
    )
    parser.add_argument(
        "--require",
        choices=("none", "read"),
        default="none",
        help="Credential readiness level to require (default: %(default)s).",
    )
    return parser


def _validate_secret_value(name: str, value: str | None) -> None:
    if value is None:
        return
    if (
        not value
        or any(character.isspace() or ord(character) < 32 for character in value)
        or "\x7f" in value
    ):
        raise SafetyError(
            f"{name} must be non-empty and contain no whitespace or control characters"
        )


def validate_config(
    *,
    origin: str,
    tenant_origin: str | None,
    requirement: str,
    environ: Mapping[str, str],
) -> tuple[int, dict[str, object]]:
    normalized_origin = validate_origin(origin)
    normalized_tenant = (
        validate_origin(tenant_origin, allow_tenant=True) if tenant_origin else None
    )
    _validate_secret_value(ACCESS_TOKEN_ENV, environ.get(ACCESS_TOKEN_ENV))

    status = credential_status(environ)

    readiness = {
        "none": True,
        "read": bool(status["rest_bearer_ready"]),
    }
    problems: list[str] = []
    if not readiness[requirement]:
        problems.append(f"credential requirement {requirement!r} is not satisfied")

    report: dict[str, object] = {
        "ok": not problems,
        "network_accessed": False,
        "dotenv_loaded": False,
        "origin": normalized_origin,
        "tenant_origin": normalized_tenant,
        "requirement": requirement,
        "credential_status": status,
        "problems": problems,
        "security": {
            "values_emitted": False,
            "accepted_secret_sources": [ACCESS_TOKEN_ENV],
            "command_line_secrets_accepted": False,
            "oauth_secrets_consumed": False,
        },
    }
    return (0 if report["ok"] else 3), report


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        code, report = validate_config(
            origin=args.origin,
            tenant_origin=args.tenant_origin,
            requirement=args.require,
            environ=os.environ,
        )
        emit_json(report)
        return code
    except (SafetyError, ValueError) as exc:
        return emit_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
