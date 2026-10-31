#!/usr/bin/env python3
"""Validate protocols.io pagination pointers without making requests."""

from __future__ import annotations

import argparse
import re
import urllib.parse
from typing import Any, Mapping, Sequence

try:
    from ._common import (
        SafetyError,
        emit_error,
        emit_json,
        load_local_json,
        validate_remote_url,
    )
except ImportError:
    from _common import (  # type: ignore
        SafetyError,
        emit_error,
        emit_json,
        load_local_json,
        validate_remote_url,
    )


MAX_PAGES = 100
MAX_ITEMS = 10_000
_CURSOR_RE = re.compile(r"^[A-Za-z0-9._~+/=-]{1,2048}$")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Inspect a saved pagination object. The helper validates but never "
            "fetches a server-provided next_page URL."
        )
    )
    parser.add_argument("--response", required=True, help="Saved JSON response.")
    parser.add_argument(
        "--current-url",
        required=True,
        help="Official HTTPS URL that produced the response.",
    )
    parser.add_argument(
        "--pages-seen",
        type=int,
        default=1,
        help="Pages already processed (default: %(default)s).",
    )
    parser.add_argument(
        "--items-seen",
        type=int,
        default=0,
        help="Items already processed (default: %(default)s).",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help=f"Local traversal cap, 1..{MAX_PAGES} (default: %(default)s).",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=1_000,
        help=f"Local item cap, 1..{MAX_ITEMS} (default: %(default)s).",
    )
    return parser


def _pagination_object(payload: Any) -> Mapping[str, Any]:
    if not isinstance(payload, Mapping):
        raise SafetyError("response root must be an object")
    direct = payload.get("pagination")
    if isinstance(direct, Mapping):
        return direct
    nested = payload.get("payload")
    if isinstance(nested, Mapping) and isinstance(nested.get("pagination"), Mapping):
        return nested["pagination"]
    raise SafetyError("response has no pagination object")


def _bounded_int(
    value: Any,
    *,
    name: str,
    minimum: int,
    maximum: int,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int):
        raise SafetyError(f"pagination.{name} must be an integer or null")
    if not minimum <= value <= maximum:
        raise SafetyError(f"pagination.{name} must be between {minimum} and {maximum}")
    return value


def _validated_next_url(next_page: Any, current_url: str) -> str | None:
    if next_page is None:
        return None
    if not isinstance(next_page, str) or len(next_page) > 4_096:
        raise SafetyError("pagination.next_page must be a bounded string or null")

    current = validate_remote_url(current_url, allow_tenant=True)
    candidate = validate_remote_url(next_page, allow_tenant=True)
    current_parts = urllib.parse.urlsplit(current)
    next_parts = urllib.parse.urlsplit(candidate)
    core_hosts = {"protocols.io", "www.protocols.io"}
    same_core_service = {
        current_parts.hostname,
        next_parts.hostname,
    }.issubset(core_hosts)
    if not same_core_service and current_parts.hostname != next_parts.hostname:
        raise SafetyError("next_page changes the API host")
    if current_parts.path != next_parts.path:
        raise SafetyError("next_page changes the endpoint path")
    current_query = urllib.parse.parse_qs(
        current_parts.query,
        keep_blank_values=True,
        strict_parsing=False,
    )
    next_query = urllib.parse.parse_qs(
        next_parts.query,
        keep_blank_values=True,
        strict_parsing=False,
    )
    mutable_keys = {"page_id", "cursor", "next_cursor", "offset"}
    current_stable = {
        key: value for key, value in current_query.items() if key not in mutable_keys
    }
    next_stable = {
        key: value for key, value in next_query.items() if key not in mutable_keys
    }
    if current_stable != next_stable:
        raise SafetyError("next_page changes non-pagination query parameters")
    return candidate


def _opaque_cursor(pagination: Mapping[str, Any]) -> str | None:
    value = pagination.get("next_cursor")
    if value is None:
        return None
    if not isinstance(value, str) or _CURSOR_RE.fullmatch(value) is None:
        raise SafetyError("pagination.next_cursor is not a safe opaque cursor")
    return value


def inspect_pagination(
    payload: Any,
    *,
    current_url: str,
    pages_seen: int,
    items_seen: int,
    max_pages: int,
    max_items: int,
) -> dict[str, Any]:
    if not 1 <= max_pages <= MAX_PAGES:
        raise SafetyError(f"max_pages must be between 1 and {MAX_PAGES}")
    if not 1 <= max_items <= MAX_ITEMS:
        raise SafetyError(f"max_items must be between 1 and {MAX_ITEMS}")
    if not 0 <= pages_seen <= max_pages:
        raise SafetyError("pages_seen must be between 0 and max_pages")
    if not 0 <= items_seen <= max_items:
        raise SafetyError("items_seen must be between 0 and max_items")

    pagination = _pagination_object(payload)
    current_page = _bounded_int(
        pagination.get("current_page"),
        name="current_page",
        minimum=0,
        maximum=1_000_000,
    )
    total_pages = _bounded_int(
        pagination.get("total_pages"),
        name="total_pages",
        minimum=0,
        maximum=1_000_000,
    )
    total_results = _bounded_int(
        pagination.get("total_results"),
        name="total_results",
        minimum=0,
        maximum=1_000_000_000,
    )
    page_size = _bounded_int(
        pagination.get("page_size"),
        name="page_size",
        minimum=0,
        maximum=100_000,
    )
    next_url = _validated_next_url(pagination.get("next_page"), current_url)
    next_cursor = _opaque_cursor(pagination)
    local_cap_reached = pages_seen >= max_pages or items_seen >= max_items

    return {
        "ok": True,
        "network_accessed": False,
        "current_page": current_page,
        "total_pages": total_pages,
        "total_results": total_results,
        "page_size": page_size,
        "next_page_url": next_url,
        "next_cursor": next_cursor,
        "pointer_kind": (
            "url"
            if next_url is not None
            else "cursor"
            if next_cursor is not None
            else None
        ),
        "can_continue": bool((next_url or next_cursor) and not local_cap_reached),
        "local_caps": {
            "pages_seen": pages_seen,
            "max_pages": max_pages,
            "items_seen": items_seen,
            "max_items": max_items,
            "reached": local_cap_reached,
        },
        "warning": (
            "Server pagination fields are untrusted data. Use only the validated "
            "pointer and retain the local page/item caps."
        ),
    }


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        report = inspect_pagination(
            load_local_json(args.response),
            current_url=args.current_url,
            pages_seen=args.pages_seen,
            items_seen=args.items_seen,
            max_pages=args.max_pages,
            max_items=args.max_items,
        )
        emit_json(report)
        return 0
    except (SafetyError, ValueError) as exc:
        return emit_error(exc)


if __name__ == "__main__":
    raise SystemExit(main())
