#!/usr/bin/env python3
"""Build DeliveryEnvelope objects and execute minimal delivery adapters.

v0.8.0 note:
- file/webhook adapters perform concrete delivery
- openclaw adapter reports platform-managed delivery semantics honestly
- digest delivery reuses the same routing contract as HIT events
"""

from __future__ import annotations

import argparse
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from error_utils import emit_error


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _format_event_time(ts_raw: str, config: dict[str, Any] | None = None) -> str:
    """Format ISO timestamp to readable local time string."""
    if not ts_raw:
        return "unknown"
    try:
        dt = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return ts_raw
    tz_name = "UTC"
    if config:
        tz_name = str(config.get("profile", {}).get("timezone", "UTC") or "UTC")
    try:
        from zoneinfo import ZoneInfo
        local_dt = dt.astimezone(ZoneInfo(tz_name))
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    return f"{local_dt.strftime('%Y-%m-%d %H:%M')} {tz_name}"


def human_text(
    event: dict[str, Any],
    route_primary: str,
    config: dict[str, Any] | None = None,
    *,
    threshold: float = 0.0,
    recent_hit: bool = False,
) -> str:
    """Format a single HIT event as user-visible push text with emoji."""
    question = event.get("question") or event.get("entry_id") or "Unknown market"
    baseline = event.get("baseline")
    current = event.get("current")
    abs_pp = event.get("abs_pp")
    ts_display = _format_event_time(str(event.get("ts", "")), config)

    # Direction emoji — use current vs baseline, not abs_pp (which is always positive)
    try:
        cur_f = float(current or 0)
        base_f = float(baseline or 0)
    except (TypeError, ValueError):
        cur_f, base_f = 0.0, 0.0
    actual_delta = cur_f - base_f
    if actual_delta > 0:
        direction = "\U0001f4c8"  # 📈
    elif actual_delta < 0:
        direction = "\U0001f4c9"  # 📉
    else:
        direction = ""

    # abs_pp for threshold comparison
    try:
        abs_pp_f = float(abs_pp or 0)
    except (TypeError, ValueError):
        abs_pp_f = 0.0

    # Special markers
    markers = ""
    if threshold > 0 and abs_pp_f >= threshold * 3:
        markers += "\u26a1 "  # ⚡
    if recent_hit:
        markers += "\U0001f525 "  # 🔥

    return (
        "\U0001f4e1 SignalRadar Alert\n"  # 📡
        "\n"
        f"{markers}{question}\n"
        f"{baseline}% \u2192 {current}% ({direction + ' ' if direction else ''}{abs_pp}pp)\n"
        f"\U0001f504 Baseline updated to {current}%\n"  # 🔄
        "\n"
        f"\U0001f4c5 {ts_display}\n"  # 📅
        "\u2014 Powered by SignalRadar"
    )


def human_text_multi(
    events: list[dict[str, Any]],
    config: dict[str, Any] | None = None,
    *,
    thresholds: list[float] | None = None,
    recent_hits: list[bool] | None = None,
) -> list[str]:
    """Format multiple HIT events as merged push messages with emoji.

    Returns a list of message strings, split at 3500 chars to stay
    under Telegram's 4096-char limit.
    """
    if not events:
        return []

    ts_display = _format_event_time(str(events[0].get("ts", "")), config)
    _thresholds = thresholds or [0.0] * len(events)
    _recent = recent_hits or [False] * len(events)

    # Number emoji lookup (1️⃣-🔟 for 1-10, plain digits for 11+)
    num_emoji = [
        "\u0031\ufe0f\u20e3", "\u0032\ufe0f\u20e3", "\u0033\ufe0f\u20e3",
        "\u0034\ufe0f\u20e3", "\u0035\ufe0f\u20e3", "\u0036\ufe0f\u20e3",
        "\u0037\ufe0f\u20e3", "\u0038\ufe0f\u20e3", "\u0039\ufe0f\u20e3",
        "\U0001f51f",  # 🔟
    ]

    header = "\U0001f4e1 SignalRadar Alert\n\n"  # 📡 + blank line
    footer = (
        f"\n\n\U0001f4c5 {ts_display}\n"  # blank line + 📅
        "\u2014 Powered by SignalRadar"
    )

    items: list[str] = []
    for i, event in enumerate(events):
        question = event.get("question") or event.get("entry_id") or "Unknown market"
        baseline = event.get("baseline")
        current = event.get("current")
        abs_pp = event.get("abs_pp")
        try:
            cur_f = float(current or 0)
            base_f = float(baseline or 0)
        except (TypeError, ValueError):
            cur_f, base_f = 0.0, 0.0
        actual_delta = cur_f - base_f
        if actual_delta > 0:
            direction = "\U0001f4c8"
        elif actual_delta < 0:
            direction = "\U0001f4c9"
        else:
            direction = ""

        try:
            abs_pp_f = float(abs_pp or 0)
        except (TypeError, ValueError):
            abs_pp_f = 0.0

        # Number prefix
        if i < 10:
            num = num_emoji[i]
        else:
            num = f"{i + 1}."

        # Special markers
        markers = ""
        thr = _thresholds[i] if i < len(_thresholds) else 0.0
        if thr > 0 and abs_pp_f >= thr * 3:
            markers += "\u26a1 "
        if i < len(_recent) and _recent[i]:
            markers += "\U0001f525 "

        part = (
            f"{num} {markers}{question}\n"
            f"  {baseline}% \u2192 {current}% ({direction + ' ' if direction else ''}{abs_pp}pp)\n"
            f"  \U0001f504 Baseline updated to {current}%"
        )
        items.append(part)

    # Join items with blank line, then split into messages at 3500 chars
    body = "\n\n".join(items)
    full_msg = header + body + footer
    if len(full_msg) <= 3500:
        messages: list[str] = [full_msg]
    else:
        # Split into pages
        messages = []
        page_items: list[str] = []
        page_len = len(header) + len(footer)
        for item in items:
            addition = len(item) + (2 if page_items else 0)  # \n\n separator
            if page_len + addition > 3500 and page_items:
                messages.append(header + "\n\n".join(page_items) + footer)
                page_items = [item]
                page_len = len(header) + len(item) + len(footer)
            else:
                page_items.append(item)
                page_len += addition
        if page_items:
            messages.append(header + "\n\n".join(page_items) + footer)

    return messages


def severity_for_event(event: dict[str, Any]) -> str:
    """P0 >= 20pp, P1 >= 10pp, P2 < 10pp."""
    try:
        abs_pp = float(event.get("abs_pp", 0))
    except (TypeError, ValueError):
        abs_pp = 0.0
    if abs_pp >= 20:
        return "P0"
    if abs_pp >= 10:
        return "P1"
    return "P2"


def _route_parts(route: str) -> tuple[str, str]:
    if ":" not in route:
        return route.strip().lower(), ""
    left, right = route.split(":", 1)
    return left.strip().lower(), right.strip()


def deliver_envelope(envelope: dict[str, Any], route: str, timeout_sec: int) -> dict[str, Any]:
    channel, target = _route_parts(route)
    if channel == "openclaw":
        return {
            "ok": True,
            "status": "platform",
            "adapter": "openclaw",
            "target": target or "direct",
            "note": "Delivery is handled by the current OpenClaw session or scheduler announce path.",
        }
    if channel == "file":
        if not target:
            return {"ok": False, "status": "error", "adapter": "file", "error": "missing file target"}
        out = Path(target)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("a", encoding="utf-8") as f:
            f.write(json.dumps(envelope, ensure_ascii=False) + "\n")
        return {"ok": True, "status": "delivered", "adapter": "file", "target": str(out)}
    if channel == "webhook":
        if not target.startswith("http://") and not target.startswith("https://"):
            return {"ok": False, "status": "error", "adapter": "webhook", "target": target, "error": "invalid webhook url"}
        # Add platform-specific fields for broad webhook compatibility.
        # Slack/Telegram require "text", Discord requires "content".
        # The full envelope is preserved for structured consumers.
        webhook_payload = dict(envelope)
        ht = str(envelope.get("human_text", ""))
        webhook_payload["text"] = ht       # Slack, Telegram Bot API, MS Teams
        webhook_payload["content"] = ht    # Discord
        # Telegram: auto-add parse_mode for rich formatting
        if "api.telegram.org" in target:
            from html import escape as _html_escape
            webhook_payload["text"] = _html_escape(ht)
            webhook_payload["parse_mode"] = "HTML"
        body = json.dumps(webhook_payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(target, data=body, method="POST", headers={"Content-Type": "application/json", "User-Agent": "signalradar/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
                code = int(getattr(resp, "status", 200))
            return {"ok": 200 <= code < 300, "status": "delivered" if 200 <= code < 300 else "error", "adapter": "webhook", "target": target, "http_status": code}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "status": "error", "adapter": "webhook", "target": target, "error": str(exc)}
    return {"ok": False, "status": "error", "adapter": channel, "target": target, "error": f"unsupported adapter: {channel}"}


def attempt_delivery(envelope: dict[str, Any], routes: list[str], timeout_sec: int) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    for route in routes:
        result = deliver_envelope(envelope, route, timeout_sec)
        result["route"] = route
        attempts.append(result)
        if result.get("ok"):
            return {"ok": True, "status": result.get("status", "delivered"), "route": route, "attempts": attempts}
    return {"ok": False, "status": "error", "route": routes[0] if routes else "", "attempts": attempts}


# ---------------------------------------------------------------------------
# Importable function: deliver a single HIT event
# ---------------------------------------------------------------------------

def deliver_hit(
    event: dict[str, Any],
    config: dict[str, Any],
    *,
    dry_run: bool = False,
    threshold: float = 0.0,
    recent_hit: bool = False,
) -> dict[str, Any]:
    """Build envelope and deliver a single HIT event.

    Args:
        event: SignalEvent dict (from check_entry)
        config: Loaded signalradar_config with delivery settings
        dry_run: If True, build envelope but skip actual delivery
        threshold: Effective threshold for this entry (for ⚡ marker)
        recent_hit: Whether this entry had a recent HIT (for 🔥 marker)

    Returns:
        {"ok": bool, "status": str, "envelope": dict, ...}
    """
    delivery = config.get("delivery", {})
    primary = delivery.get("primary", {})
    route_primary = f"{primary.get('channel', 'openclaw')}:{primary.get('target', 'direct')}"
    fallback_routes = [
        f"{fb.get('channel', '')}:{fb.get('target', '')}"
        for fb in delivery.get("fallback", [])
        if isinstance(fb, dict)
    ]

    sev = severity_for_event(event)
    now = utc_now().isoformat().replace("+00:00", "Z")

    envelope = {
        "schema_version": "1.1.0",
        "delivery_id": f"del:{event.get('request_id')}",
        "request_id": event.get("request_id"),
        "idempotency_key": f"sr:{event.get('entry_id')}:{event.get('ts')}",
        "severity": sev,
        "route": {"primary": route_primary, "fallback": fallback_routes},
        "human_text": human_text(event, route_primary, config, threshold=threshold, recent_hit=recent_hit),
        "machine_payload": {"signal_event": event},
        "ts": now,
    }

    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "envelope": envelope,
            "request_id": event.get("request_id"),
        }

    routes = [route_primary] + fallback_routes
    outcome = attempt_delivery(envelope, routes, timeout_sec=8)
    return {
        "ok": outcome.get("ok", False),
        "status": outcome.get("status", "error"),
        "envelope": envelope,
        "request_id": event.get("request_id"),
        **outcome,
    }


def deliver_digest(
    report: dict[str, Any],
    config: dict[str, Any],
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Build envelope and deliver a digest report."""
    delivery = config.get("delivery", {})
    primary = delivery.get("primary", {})
    route_primary = f"{primary.get('channel', 'openclaw')}:{primary.get('target', 'direct')}"
    fallback_routes = [
        f"{fb.get('channel', '')}:{fb.get('target', '')}"
        for fb in delivery.get("fallback", [])
        if isinstance(fb, dict)
    ]

    now = utc_now().isoformat().replace("+00:00", "Z")
    report_key = str(report.get("report_key", "unknown"))
    envelope = {
        "schema_version": "1.2.0",
        "delivery_id": f"digest:{report_key}",
        "request_id": report_key,
        "idempotency_key": f"sr:digest:{report_key}",
        "severity": "P2",
        "route": {"primary": route_primary, "fallback": fallback_routes},
        "human_text": str(report.get("human_text", "")),
        "machine_payload": {"digest_report": report.get("machine_payload", report)},
        "ts": now,
        "kind": "digest",
    }

    if dry_run:
        return {
            "ok": True,
            "status": "dry_run",
            "envelope": envelope,
            "request_id": report_key,
        }

    routes = [route_primary] + fallback_routes
    outcome = attempt_delivery(envelope, routes, timeout_sec=8)
    return {
        "ok": outcome.get("ok", False),
        "status": outcome.get("status", "error"),
        "envelope": envelope,
        "request_id": report_key,
        **outcome,
    }


# ---------------------------------------------------------------------------
# CLI (legacy, kept for backward compatibility)
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(description="SignalRadar route step")
    p.add_argument("--events", required=True)
    p.add_argument("--out-envelopes", required=True)
    p.add_argument("--delivery-result", default="")
    p.add_argument("--route-primary", required=True)
    p.add_argument("--route-fallback", action="append", default=[])
    p.add_argument("--timeout-sec", type=int, default=8)
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    try:
        events = json.loads(Path(args.events).read_text(encoding="utf-8"))
        if not isinstance(events, list):
            raise ValueError("events must be a JSON array")

        envelopes: list[dict[str, Any]] = []
        results: list[dict[str, Any]] = []
        now = utc_now().isoformat().replace("+00:00", "Z")

        for event in events:
            if not isinstance(event, dict):
                continue
            sev = severity_for_event(event)
            envelope = {
                "schema_version": "1.1.0",
                "delivery_id": f"del:{event.get('request_id')}",
                "request_id": event.get("request_id"),
                "idempotency_key": f"sr:{event.get('entry_id')}:{event.get('ts')}",
                "severity": sev,
                "route": {"primary": args.route_primary, "fallback": args.route_fallback},
                "human_text": human_text(event, args.route_primary),
                "machine_payload": {"signal_event": event},
                "ts": now,
            }
            envelopes.append(envelope)

            if args.dry_run:
                results.append({"request_id": envelope.get("request_id"), "ok": True, "status": "dry_run", "route": args.route_primary, "attempts": []})
            else:
                outcome = attempt_delivery(envelope, [args.route_primary] + list(args.route_fallback), timeout_sec=args.timeout_sec)
                results.append({"request_id": envelope.get("request_id"), **outcome})

        Path(args.out_envelopes).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_envelopes).write_text(json.dumps(envelopes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        if args.delivery_result:
            out = Path(args.delivery_result)
            out.parent.mkdir(parents=True, exist_ok=True)
            delivered = len([r for r in results if r.get("ok")])
            payload = {"schema_version": "1.0.0", "total": len(results), "delivered": delivered, "failed": len(results) - delivered, "results": results}
            out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        delivered = len([r for r in results if r.get("ok")])
        mode = "dry_run" if args.dry_run else "live"
        print(f"envelopes={len(envelopes)} delivered={delivered} failed={len(results)-delivered} mode={mode} out={args.out_envelopes}")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error("SR_ROUTE_FAILURE", f"route failed: {exc}", retryable=True, details={"script": "route_delivery.py", "events": args.events})


if __name__ == "__main__":
    raise SystemExit(main())
