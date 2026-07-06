"""
Tunee API request and error handling utilities.
"""

import os
import sys
from dataclasses import dataclass
from enum import IntEnum
import requests

API_BASE = "https://agent.test.i52hz.com"
API_GENERATE = f"{API_BASE}/open-apis/v1/music/gen"
API_TASK = f"{API_BASE}/open-apis/v1/music/query"
API_MODELS = f"{API_BASE}/open-apis/v1/models"
API_CREDITS = f"{API_BASE}/open-apis/v1/credits"


def _raw_message(raw: dict) -> str | None:
    """Prefer `message`, fall back to `msg` (some API responses use `msg`)."""
    return raw.get("msg")


@dataclass
class TuneeErrorResponse:
    """Structured representation of a Tunee API error response."""

    message: str
    status: int
    request_id: str | None


@dataclass
class TuneeResponse:
    """Tunee API unified response; business data in the data field."""

    status: int
    message: str
    request_id: str | None
    data: dict
    raw: dict

    @classmethod
    def from_json(cls, raw: dict) -> "TuneeResponse":
        """Parse raw JSON into a unified response."""
        return cls(
            status=raw.get("status", 0),
            message=_raw_message(raw) or "ok",
            request_id=raw.get("request_id"),
            data=raw.get("data") or {},
            raw=raw,
        )

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict (symmetric with from_json for logging/debug)."""
        return {
            "status": self.status,
            "message": self.message,
            "request_id": self.request_id,
            "data": self.data,
            "raw": self.raw,
        }


class TuneeStatus(IntEnum):
    """Tunee API business status codes; extensible."""

    SUCCESS = 200000

    @classmethod
    def is_known(cls, code: int) -> bool:
        """Whether the code is a defined status."""
        return code in cls._value2member_map_

    @classmethod
    def is_success(cls, code: int) -> bool:
        """Whether the code indicates success."""
        return code == cls.SUCCESS


class TuneeAPIError(Exception):
    """Tunee API call failed (HTTP != 200 or fail=true in JSON)."""

    def __init__(self, http_status: int, error: TuneeErrorResponse):
        self.http_status = http_status
        self.error = error
        super().__init__(f"[{http_status}] {error.message} (status={error.status})")


def tunee_api_error_from_biz(
        biz_msg: str,
        *,
        biz_code: str | int | None = None,
        http_status: int = 200,
        request_id: str | None = None,
) -> TuneeAPIError:
    """Build TuneeAPIError from API bizCode/bizMsg (e.g. when polling item fails)."""
    status_int = -1
    if biz_code is not None:
        if isinstance(biz_code, int):
            status_int = biz_code
        elif isinstance(biz_code, str) and biz_code.isdigit():
            status_int = int(biz_code)
    err = TuneeErrorResponse(message=biz_msg, status=status_int, request_id=request_id)
    return TuneeAPIError(http_status, err)


def parse_tunee_error(status_code: int, data: dict) -> TuneeErrorResponse | None:
    """
    Parse Tunee error response. Returns TuneeErrorResponse if error, else None.
    Error when: HTTP != 200, or status != 200000.
    """
    if status_code != 200:
        return TuneeErrorResponse(
            message=_raw_message(data) or str(data) or f"HTTP {status_code}",
            status=data.get("status", status_code),
            request_id=data.get("request_id"),
        )
    if not TuneeStatus.is_success(data.get("status")):
        return TuneeErrorResponse(
            message=_raw_message(data) or str(data) or "Unknown error",
            status=data.get("status", -1),
            request_id=data.get("request_id"),
        )
    return None


def format_tunee_error(e: TuneeAPIError) -> str:
    """Format error for user feedback (HTTP status, business status, request_id)."""
    lines = [
        f"HTTP status: {e.http_status}",
        f"Business status: {e.error.status}",
        f"Message: {e.error.message}",
    ]
    if e.error.request_id:
        lines.append(f"request_id: {e.error.request_id} (provide this when reporting issues)")
    return "\n".join(lines)


def request_tunee_api(url: str, access_key: str, json_payload: dict, timeout: int = 10) -> TuneeResponse:
    """POST request. Returns TuneeResponse on success; raises TuneeAPIError or RequestException on failure."""
    headers = build_headers(access_key)
    resp = requests.post(url, json=json_payload, headers=headers, timeout=timeout)
    raw = resp.json() if resp.content else {}
    err = parse_tunee_error(resp.status_code, raw)
    if err is not None:
        raise TuneeAPIError(resp.status_code, err)
    return TuneeResponse.from_json(raw)


def fetch_credits(access_key: str, timeout: int = 10) -> TuneeResponse:
    """POST /open-apis/v1/credits with empty JSON body. Returns TuneeResponse on success."""
    return request_tunee_api(API_CREDITS, access_key, {}, timeout=timeout)


def resolve_access_key(cli_key: str | None) -> str | None:
    """Resolve API Key in order: CLI argument > TUNEE_API_KEY."""
    for key in (cli_key, os.environ.get("TUNEE_API_KEY")):
        if not key:
            continue
        key = key.strip()
        if not key:
            continue
        if key != "your-access-key-here":
            return key
    # No key; print help and exit
    print_api_key_help()
    sys.exit(1)


def build_headers(access_key: str) -> dict:
    """Build request headers: Authorization + Content-Type."""
    return {
        "Authorization": f"Bearer {access_key}",
        "Content-Type": "application/json",
    }


def print_api_key_help() -> None:
    """Print API Key configuration guide to stderr."""
    print("Error: No API Key detected.", file=sys.stderr)
    print("", file=sys.stderr)
    print("Configure via one of:", file=sys.stderr)
    print("  1. CLI: --api-key \"your-api-key\"", file=sys.stderr)
    print("  2. Env (Unix): export TUNEE_API_KEY=\"your-api-key\"", file=sys.stderr)
    print("  3. Env (Windows PowerShell): $env:TUNEE_API_KEY=\"your-api-key\"", file=sys.stderr)
    print("", file=sys.stderr)
    print("Get an API Key at https://www.tunee.ai", file=sys.stderr)
