#!/usr/bin/env python3
"""SignalRadar unified CLI entrypoint.

Commands: doctor, add, list, show, remove, run, config, schedule, digest, onboard
Single source of truth: ~/.signalradar/config/watchlist.json
"""

from __future__ import annotations

__version__ = "1.0.8"

import argparse
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

try:
    from zoneinfo import ZoneInfo
except ImportError:  # pragma: no cover - Python 3.9+ should have zoneinfo
    ZoneInfo = None  # type: ignore[assignment]


# ---------------------------------------------------------------------------
# Resolve paths before importing sibling modules (they use relative imports)
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

from config_utils import (
    DEFAULT_CONFIG,
    add_entries,
    archive_entry,
    deep_merge,
    get_entry_by_number,
    get_nested_value,
    load_json_config,
    load_watchlist,
    save_json_config,
    save_watchlist,
    set_nested_value,
)
from decide_threshold import check_entry, safe_name
from discover_entries import (
    ONBOARDING_URLS,
    extract_probability,
    fetch_market_current_result,
    is_settled,
    normalize_market,
    parse_polymarket_url,
    resolve_event,
)
from route_delivery import deliver_digest, deliver_hit, severity_for_event


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def _workspace_root() -> Path:
    env = os.environ.get("SIGNALRADAR_WORKSPACE_ROOT", "").strip()
    if env:
        return Path(env)
    return SKILL_ROOT.parent.parent


def _user_data_root() -> Path:
    env = os.environ.get("SIGNALRADAR_DATA_DIR", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".signalradar"


def _default_user_config_path() -> Path:
    return _user_data_root() / "config" / "signalradar_config.json"


def _default_config_template_path() -> Path:
    return SKILL_ROOT / "config" / "default_config.json"


def _watchlist_path() -> Path:
    return _user_data_root() / "config" / "watchlist.json"


def _config_path(override: str = "") -> Path:
    if override:
        return Path(override).expanduser()
    env = os.environ.get("SIGNALRADAR_CONFIG", "").strip()
    if env:
        return Path(env).expanduser()
    return _default_user_config_path()


def _baseline_dir() -> Path:
    return _user_data_root() / "cache" / "baselines"


def _audit_log_path() -> Path:
    return _user_data_root() / "cache" / "events" / "signal_events.jsonl"


def _last_run_path() -> Path:
    return _user_data_root() / "cache" / "last_run.json"


def _onboard_state_path() -> Path:
    return _user_data_root() / "cache" / "onboard_state.json"


def _reply_route_path() -> Path:
    return _user_data_root() / "cache" / "openclaw_reply_route.json"


# ---------------------------------------------------------------------------
# Reply-route capture & persistence
# ---------------------------------------------------------------------------

def _capture_reply_route() -> None:
    """If OpenClaw reply-route env vars are present, persist them."""
    channel = os.environ.get("OPENCLAW_REPLY_CHANNEL", "").strip()
    target = os.environ.get("OPENCLAW_REPLY_TARGET", "").strip()
    if not channel or not target:
        return
    route: dict[str, Any] = {
        "schema_version": 1,
        "channel": channel,
        "target": target,
        "captured_at": _utc_now(),
    }
    account = os.environ.get("OPENCLAW_REPLY_ACCOUNT", "").strip()
    thread_id = os.environ.get("OPENCLAW_REPLY_THREAD_ID", "").strip()
    if account:
        route["account"] = account
    if thread_id:
        route["thread_id"] = thread_id
    p = _reply_route_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(route, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_reply_route() -> dict[str, Any] | None:
    """Load stored reply route. Returns None if missing."""
    p = _reply_route_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        if data.get("channel") and data.get("target"):
            return data
        return None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Onboard state helpers
# ---------------------------------------------------------------------------

def _read_onboard_state() -> dict[str, Any] | None:
    """Read onboard state file. Returns None if missing or expired (>1h)."""
    p = _onboard_state_path()
    if not p.exists():
        return None
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        created = data.get("created_at", "")
        if created:
            ts = datetime.fromisoformat(created.replace("Z", "+00:00"))
            if datetime.now(timezone.utc) - ts > timedelta(hours=1):
                p.unlink(missing_ok=True)
                return None
        return data
    except Exception:
        return None


def _write_onboard_state(data: dict[str, Any]) -> None:
    p = _onboard_state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _cron_log_path() -> Path:
    return _user_data_root() / "cache" / "cron.log"


def _digest_state_path() -> Path:
    return _user_data_root() / "cache" / "digest_state.json"


_USER_DATA_READY = False
_USER_DATA_NOTICES: list[str] = []


def _safe_copy_file(src: Path, dst: Path) -> bool:
    if not src.is_file() or dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return True


def _safe_copy_tree(src: Path, dst: Path) -> bool:
    if not src.is_dir() or dst.exists():
        return False
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    return True


def _ensure_user_data_ready() -> list[str]:
    global _USER_DATA_READY, _USER_DATA_NOTICES
    if _USER_DATA_READY:
        return list(_USER_DATA_NOTICES)

    data_root = _user_data_root()
    notices: list[str] = []
    try:
        config_dir = data_root / "config"
        cache_dir = data_root / "cache"
        baseline_dir = cache_dir / "baselines"
        events_dir = cache_dir / "events"
        config_dir.mkdir(parents=True, exist_ok=True)
        baseline_dir.mkdir(parents=True, exist_ok=True)
        events_dir.mkdir(parents=True, exist_ok=True)

        migrated = False
        legacy_config_dir = SKILL_ROOT / "config"
        legacy_cache_dir = SKILL_ROOT / "cache"

        if _safe_copy_file(legacy_config_dir / "watchlist.json", _watchlist_path()):
            migrated = True
        if not _default_user_config_path().exists():
            if _safe_copy_file(legacy_config_dir / "signalradar_config.json", _default_user_config_path()):
                migrated = True
            elif _default_config_template_path().is_file():
                _safe_copy_file(_default_config_template_path(), _default_user_config_path())
            else:
                save_json_config(_default_user_config_path(), DEFAULT_CONFIG)
        if not _watchlist_path().exists():
            save_watchlist(_watchlist_path(), {"entries": [], "archived": []})

        if _safe_copy_tree(legacy_cache_dir / "baselines", _baseline_dir()):
            migrated = True
        if _safe_copy_file(legacy_cache_dir / "events" / "signal_events.jsonl", _audit_log_path()):
            migrated = True
        if _safe_copy_file(legacy_cache_dir / "last_run.json", _last_run_path()):
            migrated = True
        if _safe_copy_file(legacy_cache_dir / "digest_state.json", _digest_state_path()):
            migrated = True
        if _safe_copy_file(legacy_cache_dir / "cron.log", _cron_log_path()):
            migrated = True

        if migrated:
            notices.append(f"Migrated user data from skill directory to {data_root}/")
    except OSError as exc:
        notices.append(
            f"Warning: could not initialize SignalRadar data directory at {data_root}: {exc}. "
            "Set SIGNALRADAR_DATA_DIR to a writable path if needed."
        )

    _USER_DATA_READY = True
    _USER_DATA_NOTICES = notices
    return list(_USER_DATA_NOTICES)


def _load_config(override: str = "") -> dict[str, Any]:
    user_cfg = load_json_config(_config_path(override))
    return deep_merge(DEFAULT_CONFIG, user_cfg)


def _save_config_key(override: str, key: str, value: Any) -> None:
    """Write a single key to the user config file."""
    cfg_path = _config_path(override)
    user_cfg = load_json_config(cfg_path)
    set_nested_value(user_cfg, key, value)
    save_json_config(cfg_path, user_cfg)


def _is_dynamic_config_key(key: str) -> bool:
    dynamic_prefixes = (
        "threshold.per_category_abs_pp.",
        "threshold.per_entry_abs_pp.",
    )
    # Whitelist specific delivery keys instead of allowing arbitrary delivery.primary.*
    delivery_whitelist = {"delivery.primary.channel", "delivery.primary.target"}
    if key in delivery_whitelist:
        return True
    return any(key.startswith(prefix) for prefix in dynamic_prefixes)


def _config_key_exists(key: str, merged: dict[str, Any]) -> bool:
    found, _value = get_nested_value(merged, key)
    return found or _is_dynamic_config_key(key)


_SUPPORTED_DELIVERY_CHANNELS = {"openclaw", "file", "webhook"}
_SUPPORTED_LANGUAGES = {"zh", "en"}
_SUPPORTED_DIGEST_FREQUENCIES = {"off", "daily", "weekly", "biweekly"}
_ZH_TIMEZONE_FALLBACKS = {
    "Asia/Shanghai",
    "Asia/Chongqing",
    "Asia/Harbin",
    "Asia/Urumqi",
    "Asia/Hong_Kong",
    "Asia/Macau",
    "Asia/Taipei",
}
_SUPPORTED_DIGEST_DAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _format_user_time(value: str, config: dict[str, Any]) -> str:
    if value in ("", "never", "unknown"):
        return value
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value
    if ZoneInfo is None:
        return value
    timezone_name = str(config.get("profile", {}).get("timezone", "UTC") or "UTC")
    try:
        local_dt = dt.astimezone(ZoneInfo(timezone_name))
    except Exception:
        return value
    return f"{local_dt.strftime('%Y-%m-%d %H:%M:%S')} {timezone_name}"


def _resolve_language(config: dict[str, Any]) -> str:
    raw = str(config.get("profile", {}).get("language", "") or "").strip().lower()
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("en"):
        return "en"
    return _detect_auto_language(config)


def _detect_auto_language(config: dict[str, Any]) -> str:
    for key in ("OPENCLAW_USER_LANG", "LC_ALL", "LANG"):
        env_value = os.environ.get(key, "").strip().lower()
        if env_value.startswith("zh"):
            return "zh"
        if env_value.startswith("en"):
            return "en"
    timezone_name = str(config.get("profile", {}).get("timezone", "") or "").strip()
    if timezone_name in _ZH_TIMEZONE_FALLBACKS:
        return "zh"
    return "en"


def _persist_detected_language_if_needed(config_override: str = "") -> str:
    config = _load_config(config_override)
    raw = str(config.get("profile", {}).get("language", "") or "").strip().lower()
    if raw.startswith("zh"):
        return "zh"
    if raw.startswith("en"):
        return "en"
    detected = _detect_auto_language(config)
    _save_config_key(config_override, "profile.language", detected)
    return detected


def _event_title_for_entry(entry: dict[str, Any]) -> str:
    title = str(entry.get("event_title", "") or "").strip()
    if title:
        return title
    slug = str(entry.get("slug", "") or "").strip()
    if slug:
        return slug.replace("-", " ").strip().title()
    question = str(entry.get("question", "") or "").strip()
    return question if question else str(entry.get("entry_id", "") or "Unknown event")


def _read_baseline_doc(entry_id: str) -> dict[str, Any] | None:
    if not entry_id:
        return None
    path = _baseline_dir() / f"{safe_name(entry_id)}.json"
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _read_baseline_value(entry_id: str) -> float | None:
    doc = _read_baseline_doc(entry_id)
    if doc is None:
        return None
    value = doc.get("baseline")
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _read_baseline_ts(entry_id: str) -> str:
    doc = _read_baseline_doc(entry_id)
    if doc is None:
        return ""
    return str(doc.get("baseline_ts", "") or "")


def _parse_local_time_string(value: str) -> tuple[int, int] | None:
    text = str(value or "").strip()
    match = re.fullmatch(r"([01]?\d|2[0-3]):([0-5]\d)", text)
    if not match:
        return None
    return int(match.group(1)), int(match.group(2))


def _local_now(config: dict[str, Any]) -> datetime:
    timezone_name = str(config.get("profile", {}).get("timezone", "UTC") or "UTC")
    if ZoneInfo is None:
        return datetime.now(timezone.utc)
    try:
        return datetime.now(ZoneInfo(timezone_name))
    except Exception:
        return datetime.now(timezone.utc)


def _period_start_date(local_now: datetime, frequency: str, weekday: int) -> datetime.date:
    today = local_now.date()
    if frequency == "daily":
        return today
    days_back = (local_now.weekday() - weekday) % 7
    start = today - timedelta(days=days_back)
    if frequency == "biweekly":
        anchor = datetime(2026, 1, 5).date()  # Monday-aligned anchor week
        weeks_since_anchor = (start - anchor).days // 7
        if weeks_since_anchor % 2 != 0:
            start = start - timedelta(days=7)
    return start


def _digest_period_info(config: dict[str, Any], *, local_now: datetime | None = None) -> dict[str, Any]:
    digest_cfg = config.get("digest", {})
    frequency = str(digest_cfg.get("frequency", "weekly") or "weekly").strip().lower()
    day_name = str(digest_cfg.get("day_of_week", "monday") or "monday").strip().lower()
    weekday = _SUPPORTED_DIGEST_DAYS.get(day_name, 0)
    time_raw = str(digest_cfg.get("time_local", "09:00") or "09:00")
    parsed_time = _parse_local_time_string(time_raw) or (9, 0)
    local_now = local_now or _local_now(config)
    start_date = _period_start_date(local_now, frequency, weekday)
    scheduled_local = datetime.combine(
        start_date,
        datetime.min.time(),
        tzinfo=local_now.tzinfo,
    ).replace(hour=parsed_time[0], minute=parsed_time[1])
    if frequency == "daily":
        report_key = f"daily:{start_date.isoformat()}"
    elif frequency == "weekly":
        report_key = f"weekly:{start_date.isoformat()}"
    else:
        report_key = f"biweekly:{start_date.isoformat()}"
    return {
        "frequency": frequency,
        "day_of_week": day_name,
        "time_local": f"{parsed_time[0]:02d}:{parsed_time[1]:02d}",
        "start_date": start_date.isoformat(),
        "report_key": report_key,
        "scheduled_local": scheduled_local,
        "local_now": local_now,
    }


def _load_digest_state() -> dict[str, Any]:
    path = _digest_state_path()
    if not path.exists():
        return {"schema_version": 1, "last_report_key": "", "last_report_ts": "", "snapshot": {}}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"schema_version": 1, "last_report_key": "", "last_report_ts": "", "snapshot": {}}
    if not isinstance(payload, dict):
        return {"schema_version": 1, "last_report_key": "", "last_report_ts": "", "snapshot": {}}
    payload.setdefault("schema_version", 1)
    payload.setdefault("last_report_key", "")
    payload.setdefault("last_report_ts", "")
    payload.setdefault("snapshot", {})
    return payload


def _save_digest_state(state: dict[str, Any]) -> None:
    path = _digest_state_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    save_json_config(path, state)


def _parse_cli_value(raw_value: str) -> Any:
    lowered = raw_value.strip().lower()
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    try:
        return int(raw_value)
    except ValueError:
        try:
            return float(raw_value)
        except ValueError:
            return raw_value


def _validate_config_value(key: str, value: Any) -> str | None:
    if key == "threshold.abs_pp" or key.startswith("threshold.per_category_abs_pp.") or key.startswith("threshold.per_entry_abs_pp."):
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            return "Threshold must be a number."
        if numeric < 0.1:
            return "Minimum threshold is 0.1 percentage points."
    if key == "delivery.primary.channel":
        channel = str(value or "").strip().lower()
        if channel not in _SUPPORTED_DELIVERY_CHANNELS:
            supported = ", ".join(sorted(_SUPPORTED_DELIVERY_CHANNELS))
            return f"Unsupported delivery channel: {value}. Supported values: {supported}."
    if key == "profile.timezone" and ZoneInfo is not None:
        try:
            ZoneInfo(str(value))
        except Exception:
            return f"Unknown timezone: {value}"
    if key == "profile.language":
        lang = str(value or "").strip().lower()
        if lang and not any(lang.startswith(prefix) for prefix in _SUPPORTED_LANGUAGES):
            return "profile.language supports zh or en (or empty for automatic detection)."
    if key == "digest.frequency":
        frequency = str(value or "").strip().lower()
        if frequency not in _SUPPORTED_DIGEST_FREQUENCIES:
            return "digest.frequency must be one of: off, daily, weekly, biweekly."
    if key == "digest.day_of_week":
        day = str(value or "").strip().lower()
        if day not in _SUPPORTED_DIGEST_DAYS:
            return "digest.day_of_week must be a weekday name like monday or sunday."
    if key == "digest.time_local":
        if _parse_local_time_string(str(value or "")) is None:
            return "digest.time_local must use HH:MM 24-hour format."
    if key == "digest.top_n":
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            return "digest.top_n must be an integer."
        if numeric < 1 or numeric > 50:
            return "digest.top_n must be between 1 and 50."
    if key == "check_interval_minutes":
        try:
            numeric = int(value)
        except (TypeError, ValueError):
            return "check_interval_minutes must be an integer."
        if numeric < 5:
            return "Minimum interval is 5 minutes."
        if numeric > 10080:
            return "Maximum interval is 10080 minutes (1 week)."
    return None


def _run_error(entry_id: str, code: str, message: str) -> dict[str, Any]:
    return {
        "entry_id": entry_id,
        "code": code,
        "message": message,
        "error": message,
    }


def _build_observation(
    entry: dict[str, Any],
    *,
    state: str,
    decision: str,
    threshold: float | None = None,
    current_market: dict[str, Any] | None = None,
    result: dict[str, Any] | None = None,
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "entry_id": entry.get("entry_id", ""),
        "question": entry.get("question", ""),
        "slug": entry.get("slug", ""),
        "event_title": entry.get("event_title", ""),
        "category": entry.get("category", "default"),
        "state": state,
        "decision": decision,
        "threshold_abs_pp": threshold,
        "url": entry.get("url", ""),
        "end_date": entry.get("end_date", ""),
    }
    if current_market is not None:
        observation["current"] = current_market.get("probability")
        observation["market_status"] = current_market.get("status", "unknown")
    if result is not None:
        observation["baseline"] = result.get("baseline")
        observation["baseline_ts"] = result.get("baseline_ts")
        observation["abs_pp"] = result.get("abs_pp")
        if result.get("event") is not None:
            observation["reason"] = result["event"].get("reason", "")
    elif state in {"checked", "settled"}:
        baseline_doc = _read_baseline_doc(str(entry.get("entry_id", "")))
        if baseline_doc is not None:
            observation["baseline"] = baseline_doc.get("baseline")
            observation["baseline_ts"] = baseline_doc.get("baseline_ts", "")
    if error is not None:
        observation["error_code"] = error.get("code", "SR_SOURCE_UNAVAILABLE")
        observation["error_message"] = error.get("message", "Unknown error")
    return observation


def _find_entries_for_show(data: dict[str, Any], target: str) -> list[dict[str, Any]]:
    """Resolve show target by list number or case-insensitive text search."""
    entries = data.get("entries", [])
    if target.isdigit():
        entry = get_entry_by_number(data, int(target))
        return [entry] if entry is not None else []

    needle = target.strip().lower()
    matches: list[dict[str, Any]] = []
    for entry in entries:
        haystacks = [
            str(entry.get("question", "")).lower(),
            str(entry.get("slug", "")).lower(),
            str(entry.get("entry_id", "")).lower(),
            str(entry.get("category", "")).lower(),
        ]
        if any(needle in hay for hay in haystacks):
            matches.append(entry)
    return matches


def _classify_market_type(question: str) -> str:
    text = question.strip().lower()
    downside_patterns = (
        r"\bbelow\b",
        r"\bunder\b",
        r"\bless than\b",
        r"\bdrop below\b",
        r"\bfall below\b",
        r"\bfall to\b",
        r"\bat most\b",
    )
    upside_patterns = (
        r"\babove\b",
        r"\bover\b",
        r"\bgreater than\b",
        r"\bexceed\b",
        r"\breach\b",
        r"\bhit\b",
        r"\bat least\b",
    )
    if any(re.search(pattern, text) for pattern in downside_patterns):
        return "downside"
    if any(re.search(pattern, text) for pattern in upside_patterns):
        return "upside"
    return "other"


def _summarize_market_types(markets: list[dict[str, Any]]) -> str:
    counts = {"upside": 0, "downside": 0, "other": 0}
    for market in markets:
        counts[_classify_market_type(str(market.get("question", "")))] += 1
    parts: list[str] = []
    if counts["upside"]:
        parts.append(f"{counts['upside']} upside")
    if counts["downside"]:
        parts.append(f"{counts['downside']} downside")
    if counts["other"]:
        parts.append(f"{counts['other']} other")
    return ", ".join(parts) if parts else "no active markets"


def _print_market_preview(event_title: str, active_markets: list[dict[str, Any]], settled_markets: list[dict[str, Any]]) -> None:
    print(f"\n{event_title}")
    print(f"Active markets: {len(active_markets)}")
    if settled_markets:
        print(f"Settled markets skipped: {len(settled_markets)}")
    print(f"Type summary: {_summarize_market_types(active_markets)}")
    print("Markets to add:")
    for idx, market in enumerate(active_markets, 1):
        probability = market.get("probability")
        probability_text = f"{probability:.0f}%" if isinstance(probability, (int, float)) else "N/A"
        market_type = _classify_market_type(str(market.get("question", "")))
        print(f"  {idx}. [{market_type}] {market.get('question', '?')}  {probability_text}")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def _json_print(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, ensure_ascii=False, indent=2))


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _add_result_payload(
    *,
    status: str,
    event_title: str = "",
    added: list[dict[str, Any]] | None = None,
    skipped: list[dict[str, Any]] | None = None,
    schedule: dict[str, Any] | None = None,
    message: str = "",
    error: str = "",
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "status": status,
        "request_id": str(uuid.uuid4()),
        "ts": _utc_now(),
        "event_title": event_title,
        "added": added or [],
        "skipped": skipped or [],
    }
    if message:
        payload["message"] = message
    if error:
        payload["error"] = error
    if schedule is not None:
        payload["schedule"] = schedule
    return payload


def _openclaw_run_text(hits: list[dict[str, Any]], run_ts: str, config: dict[str, Any]) -> str:
    if not hits:
        return "HEARTBEAT_OK"
    ts_display = _format_user_time(run_ts, config)
    lines = [f"SignalRadar detected {len(hits)} market change(s):", ""]
    for idx, hit in enumerate(hits, 1):
        question = str(hit.get("question") or hit.get("entry_id") or "Unknown market")
        baseline = hit.get("baseline")
        current = hit.get("current")
        abs_pp = hit.get("abs_pp")
        lines.append(f"{idx}. {question}")
        lines.append(f"   {baseline}% \u2192 {current}% ({abs_pp}pp)")
        lines.append(f"   Baseline updated to {current}%")
    lines.append("")
    lines.append(f"Run time: {ts_display}")
    return "\n".join(lines)


def _join_openclaw_messages(*parts: str) -> str:
    kept = [part.strip() for part in parts if part and part.strip()]
    if not kept:
        return "HEARTBEAT_OK"
    return "\n\n".join(kept)


def _digest_title(frequency: str) -> str:
    freq = str(frequency or "weekly").strip().lower()
    labels = {
        "daily": "Daily Digest",
        "weekly": "Weekly Digest",
        "biweekly": "Biweekly Digest",
    }
    return f"SignalRadar {labels.get(freq, 'Digest')}"


def _snapshot_row_from_entry(
    entry: dict[str, Any],
    *,
    state: str,
    current: float | None = None,
    market_status: str = "",
    error: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "entry_id": str(entry.get("entry_id", "") or ""),
        "slug": str(entry.get("slug", "") or ""),
        "event_title": _event_title_for_entry(entry),
        "question": str(entry.get("question", "") or ""),
        "category": str(entry.get("category", "default") or "default"),
        "url": str(entry.get("url", "") or ""),
        "end_date": str(entry.get("end_date", "") or ""),
        "state": state,
        "status": market_status or state,
    }
    baseline = _read_baseline_value(row["entry_id"])
    baseline_ts = _read_baseline_ts(row["entry_id"])
    if baseline is not None:
        row["baseline"] = baseline
    if baseline_ts:
        row["baseline_ts"] = baseline_ts
    if current is not None:
        row["current"] = current
    if error is not None:
        row["error_code"] = error.get("code", "SR_SOURCE_UNAVAILABLE")
        row["error_message"] = error.get("message", "Unknown error")
    return row


def _collect_digest_snapshot(entries: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for entry in entries:
        entry_id = str(entry.get("entry_id", "") or "")
        market_id = entry_id.split(":")[1] if ":" in entry_id else ""
        if not market_id:
            error = _run_error(entry_id, "SR_VALIDATION_ERROR", "Entry ID format is invalid.")
            rows.append(_snapshot_row_from_entry(entry, state="error", error=error))
            errors.append(error)
            continue

        current_market, fetch_error = fetch_market_current_result(market_id)
        if current_market is None:
            if is_settled(entry):
                rows.append(_snapshot_row_from_entry(entry, state="settled", market_status="settled"))
                continue
            error = _run_error(
                entry_id,
                fetch_error.get("code", "SR_SOURCE_UNAVAILABLE") if fetch_error else "SR_SOURCE_UNAVAILABLE",
                fetch_error.get("message", "Could not fetch current market data from Polymarket API.")
                if fetch_error
                else "Could not fetch current market data from Polymarket API.",
            )
            rows.append(_snapshot_row_from_entry(entry, state="error", error=error))
            errors.append(error)
            continue

        probability = current_market.get("probability")
        if is_settled(current_market):
            rows.append(
                _snapshot_row_from_entry(
                    entry,
                    state="settled",
                    current=probability if isinstance(probability, (int, float)) else None,
                    market_status=str(current_market.get("status", "settled") or "settled"),
                )
            )
            continue

        if not isinstance(probability, (int, float)):
            error = _run_error(
                entry_id,
                "SR_VALIDATION_ERROR",
                "Polymarket API returned market data without a probability value.",
            )
            rows.append(_snapshot_row_from_entry(entry, state="error", error=error))
            errors.append(error)
            continue

        rows.append(
            _snapshot_row_from_entry(
                entry,
                state="checked",
                current=float(probability),
                market_status=str(current_market.get("status", "active") or "active"),
            )
        )
    return rows, errors


def _snapshot_for_state(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    snapshot: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry_id = str(row.get("entry_id", "") or "")
        if not entry_id:
            continue
        snapshot[entry_id] = {
            "question": row.get("question", ""),
            "slug": row.get("slug", ""),
            "event_title": row.get("event_title", ""),
            "probability": row.get("current"),
            "status": row.get("state", "unknown"),
        }
    return snapshot


def _digest_due_status(config: dict[str, Any], state: dict[str, Any], *, force: bool = False) -> dict[str, Any]:
    info = _digest_period_info(config)
    frequency = info["frequency"]
    if frequency == "off":
        return {
            "enabled": False,
            "due": False,
            "reason": "disabled",
            **info,
        }
    last_report_key = str(state.get("last_report_key", "") or "")
    if force:
        return {
            "enabled": True,
            "due": True,
            "reason": "forced",
            **info,
        }
    if info["local_now"] < info["scheduled_local"]:
        return {
            "enabled": True,
            "due": False,
            "reason": "before_schedule",
            **info,
        }
    if last_report_key == info["report_key"]:
        return {
            "enabled": True,
            "due": False,
            "reason": "already_sent",
            **info,
        }
    return {
        "enabled": True,
        "due": True,
        "reason": "due",
        **info,
    }


def _build_digest_report(
    config: dict[str, Any],
    entries: list[dict[str, Any]],
    *,
    force: bool = False,
    snapshot_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    state = _load_digest_state()
    due_info = _digest_due_status(config, state, force=force)
    if not due_info["enabled"]:
        return {
            "status": "NO_REPLY",
            "frequency": "off",
            "report_key": "",
            "scheduled_local": "",
            "due": False,
            "due_reason": due_info["reason"],
            "generated_at": _utc_now(),
            "first_report": not bool(state.get("snapshot")),
            "summary": {"active": 0, "new": 0, "settled": 0, "errors": 0, "changed": 0},
            "top_movers": [],
            "events": [],
            "hidden_event_count": 0,
            "new_entries": [],
            "settled_entries": [],
            "error_entries": [],
            "hidden_new_count": 0,
            "hidden_settled_count": 0,
            "hidden_error_count": 0,
            "snapshot_rows": [],
            "snapshot": {},
            "last_report_ts": state.get("last_report_ts", ""),
        }
    rows, errors = (snapshot_rows, []) if snapshot_rows is not None else _collect_digest_snapshot(entries)
    snapshot_rows = list(rows or [])
    previous_snapshot = state.get("snapshot", {})
    if not isinstance(previous_snapshot, dict):
        previous_snapshot = {}

    changed_rows: list[dict[str, Any]] = []
    new_rows: list[dict[str, Any]] = []
    settled_rows: list[dict[str, Any]] = []
    error_rows: list[dict[str, Any]] = []

    for row in snapshot_rows:
        entry_id = str(row.get("entry_id", "") or "")
        previous = previous_snapshot.get(entry_id, {})
        prev_probability = previous.get("probability") if isinstance(previous, dict) else None

        if row.get("state") == "error":
            error_rows.append(row)
            continue
        if row.get("state") == "settled":
            settled_rows.append(row)
            continue

        current = row.get("current")
        if not isinstance(current, (int, float)):
            continue

        if not isinstance(prev_probability, (int, float)):
            row["week_abs_pp"] = None
            new_rows.append(row)
            continue

        delta = round(float(current) - float(prev_probability), 3)
        row["week_abs_pp"] = delta
        row["previous_probability"] = float(prev_probability)
        if abs(delta) > 0:
            changed_rows.append(row)

    top_movers = sorted(
        changed_rows,
        key=lambda item: abs(float(item.get("week_abs_pp", 0.0) or 0.0)),
        reverse=True,
    )

    # Collect unchanged rows for digest "No changes" block
    unchanged_rows: list[dict[str, Any]] = []
    for row in snapshot_rows:
        if row.get("state") != "checked":
            continue
        entry_id = str(row.get("entry_id", "") or "")
        if entry_id and entry_id not in {str(r.get("entry_id", "")) for r in changed_rows} \
                and entry_id not in {str(r.get("entry_id", "")) for r in new_rows}:
            unchanged_rows.append(row)

    event_groups: dict[str, dict[str, Any]] = {}
    for row in snapshot_rows:
        key = str(row.get("slug") or row.get("event_title") or row.get("entry_id") or "")
        group = event_groups.setdefault(
            key,
            {
                "event_key": key,
                "event_title": row.get("event_title") or _event_title_for_entry(row),
                "tracked_count": 0,
                "changed_rows": [],
            },
        )
        group["tracked_count"] += 1
    for row in changed_rows:
        key = str(row.get("slug") or row.get("event_title") or row.get("entry_id") or "")
        event_groups[key]["changed_rows"].append(row)

    grouped_events: list[dict[str, Any]] = []
    for group in event_groups.values():
        changed = sorted(
            group["changed_rows"],
            key=lambda item: abs(float(item.get("week_abs_pp", 0.0) or 0.0)),
            reverse=True,
        )
        if not changed:
            continue
        grouped_events.append(
            {
                "event_key": group["event_key"],
                "event_title": group["event_title"],
                "tracked_count": group["tracked_count"],
                "changed_count": len(changed),
                "top_movers": changed[:3],
                "hidden_changed_count": max(0, len(changed) - 3),
                "max_abs_pp": max(abs(float(item.get("week_abs_pp", 0.0) or 0.0)) for item in changed),
            }
        )

    grouped_events.sort(key=lambda item: float(item.get("max_abs_pp", 0.0)), reverse=True)
    report_ts = _utc_now()
    report = {
        "status": "OK",
        "frequency": due_info["frequency"],
        "report_key": due_info["report_key"],
        "scheduled_local": due_info["scheduled_local"].isoformat(),
        "due": due_info["due"],
        "due_reason": due_info["reason"],
        "generated_at": report_ts,
        "first_report": not bool(previous_snapshot),
        "summary": {
            "active": len([row for row in snapshot_rows if row.get("state") == "checked"]),
            "new": len(new_rows),
            "settled": len(settled_rows),
            "errors": len(error_rows),
            "changed": len(changed_rows),
        },
        "top_movers": top_movers,
        "unchanged_rows": unchanged_rows,
        "events": grouped_events[:5],
        "hidden_event_count": max(0, len(grouped_events) - 5),
        "new_entries": new_rows[:10],
        "settled_entries": settled_rows[:10],
        "error_entries": error_rows[:10],
        "hidden_new_count": max(0, len(new_rows) - 10),
        "hidden_settled_count": max(0, len(settled_rows) - 10),
        "hidden_error_count": max(0, len(error_rows) - 10),
        "snapshot_rows": snapshot_rows,
        "snapshot": _snapshot_for_state(snapshot_rows),
        "last_report_ts": state.get("last_report_ts", ""),
    }
    return report


def _format_digest_text(report: dict[str, Any], config: dict[str, Any]) -> str:
    generated_display = _format_user_time(str(report.get("generated_at", "")), config)
    frequency = str(report.get("frequency", "weekly") or "weekly")
    summary = report.get("summary", {})
    all_rows = report.get("top_movers", [])  # all changed rows (sorted by abs delta)
    digest_threshold = float(config.get("digest", {}).get("threshold_abs_pp", 10.0) or 10.0)

    # Collect all rows including unchanged ones
    unchanged_rows = [r for r in report.get("unchanged_rows", []) if r]
    settled_entries = report.get("settled_entries", []) or []
    error_entries = report.get("error_entries", []) or []
    new_entries = report.get("new_entries", []) or []

    _num_emoji = [
        "\u0031\ufe0f\u20e3", "\u0032\ufe0f\u20e3", "\u0033\ufe0f\u20e3",
        "\u0034\ufe0f\u20e3", "\u0035\ufe0f\u20e3", "\u0036\ufe0f\u20e3",
        "\u0037\ufe0f\u20e3", "\u0038\ufe0f\u20e3", "\u0039\ufe0f\u20e3",
        "\U0001f51f",
    ]
    _sep = "\u2500" * 19

    lines = [
        f"\U0001f4ca {_digest_title(frequency)}",
        f"\U0001f4c5 {generated_display}",
        "",
    ]
    if report.get("first_report"):
        lines.append("Note: this is the first digest. No previous digest snapshot is available yet.")
        lines.append("")

    active = int(summary.get("active", 0))
    changed = int(summary.get("changed", 0))
    settled_count = int(summary.get("settled", 0))
    stable = active - changed
    lines.append(f"\U0001f522 {active} markets \u00b7 {changed} changed \u00b7 {settled_count} settled \u00b7 {stable} stable")
    lines.append("")

    # Classify rows by event
    event_map: dict[str, list[dict[str, Any]]] = {}
    standalone_changed: list[dict[str, Any]] = []
    for row in all_rows:
        et = str(row.get("event_title", "") or "")
        if et:
            event_map.setdefault(et, []).append(row)
        else:
            standalone_changed.append(row)

    event_block: dict[str, str] = {}
    for et, rows in event_map.items():
        has_major = any(abs(float(r.get("week_abs_pp", 0) or 0)) >= digest_threshold for r in rows)
        event_block[et] = "changes" if has_major else "minor"

    # --- 1. Changes ---
    major_items: list[dict[str, Any]] = []
    for et, block in event_block.items():
        if block == "changes":
            for r in event_map[et]:
                if abs(float(r.get("week_abs_pp", 0) or 0)) >= digest_threshold:
                    major_items.append(r)
    for r in standalone_changed:
        if abs(float(r.get("week_abs_pp", 0) or 0)) >= digest_threshold:
            major_items.append(r)
    major_items.sort(key=lambda r: abs(float(r.get("week_abs_pp", 0) or 0)), reverse=True)

    changes_lines: list[str] = []
    for idx, r in enumerate(major_items):
        delta = float(r.get("week_abs_pp", 0) or 0)
        direction = "\U0001f4c8" if delta >= 0 else "\U0001f4c9"
        sign = "+" if delta >= 0 else ""
        num = _num_emoji[idx] if idx < 10 else f"{idx + 1}."
        changes_lines.append(f"{num} {r.get('question', r.get('entry_id', '?'))}")
        changes_lines.append(f"  {r.get('previous_probability')}% \u2192 {r.get('current')}% ({direction} {sign}{delta}pp)")

    if changes_lines:
        lines.extend([_sep, "\U0001f4c8 Changes", _sep])
        lines.extend(changes_lines)
        lines.append("")

    minor_lines: list[str] = []
    for et, block in sorted(event_block.items()):
        rows = event_map[et]
        if block == "changes":
            minor_in = [r for r in rows if abs(float(r.get("week_abs_pp", 0) or 0)) < digest_threshold]
            if minor_in:
                top_row = max(minor_in, key=lambda r: float(r.get("current", 0) or 0))
                minor_lines.append(f"  \u2022 {et} ({len(minor_in)} more markets, top: {top_row.get('question', '?')} at {top_row.get('current', '?')}%)")
        elif block == "minor":
            if len(rows) > 1:
                top_row = max(rows, key=lambda r: float(r.get("current", 0) or 0))
                minor_lines.append(f"  \u2022 {et} ({len(rows)} markets, top: {top_row.get('question', '?')} at {top_row.get('current', '?')}%)")
            else:
                r = rows[0]
                minor_lines.append(f"  \u2022 {r.get('question', r.get('entry_id', '?'))}  ({r.get('current', '?')}%)")
    for r in standalone_changed:
        if abs(float(r.get("week_abs_pp", 0) or 0)) < digest_threshold:
            minor_lines.append(f"  \u2022 {r.get('question', r.get('entry_id', '?'))}  ({r.get('current', '?')}%)")

    if minor_lines:
        lines.append(f"\U0001f4c9 Minor changes (< {int(digest_threshold)}pp)")
        lines.extend(minor_lines)
        lines.append("")

    # --- 2. Stable ---
    unchanged_event_map: dict[str, list[dict[str, Any]]] = {}
    standalone_unchanged: list[dict[str, Any]] = []
    for row in unchanged_rows:
        et = str(row.get("event_title", "") or "")
        if et:
            unchanged_event_map.setdefault(et, []).append(row)
        else:
            standalone_unchanged.append(row)

    seen_ids: set[str] = set()
    deduped_stable: list[dict[str, Any]] = []
    for r in sorted(unchanged_rows + standalone_unchanged, key=lambda x: float(x.get("current", 0) or 0), reverse=True):
        rid = str(r.get("entry_id", ""))
        if rid and rid not in seen_ids:
            deduped_stable.append(r)
            seen_ids.add(rid)

    stable_lines: list[str] = []
    shown = 0
    shown_ids: set[str] = set()
    for r in deduped_stable:
        if shown >= 20:
            break
        rid = str(r.get("entry_id", ""))
        if rid in shown_ids:
            continue
        et = str(r.get("event_title", "") or "")
        if et and et in unchanged_event_map and len(unchanged_event_map[et]) > 1:
            event_rows = unchanged_event_map[et]
            total_stable = len(event_rows)
            total_in_event = total_stable + len([cr for cr in all_rows if str(cr.get("event_title", "")) == et])
            stable_lines.append(f"  \u2022 {et} ({total_stable} of {total_in_event} stable)")
            for er in sorted(event_rows, key=lambda x: float(x.get("current", 0) or 0), reverse=True):
                if shown >= 20:
                    break
                erid = str(er.get("entry_id", ""))
                if erid not in shown_ids:
                    stable_lines.append(f"    \u00b7 {er.get('question', '?')} \u2014 {er.get('current', '?')}%")
                    shown_ids.add(erid)
                    shown += 1
            for er in event_rows:
                shown_ids.add(str(er.get("entry_id", "")))
        else:
            stable_lines.append(f"  \u2022 {r.get('question', r.get('entry_id', '?'))} \u2014 {r.get('current', '?')}%")
            shown_ids.add(rid)
            shown += 1

    remaining_stable = len(deduped_stable) - len(shown_ids)
    if remaining_stable > 0:
        stable_lines.append(f"  (+{remaining_stable} more stable markets)")

    if stable_lines:
        lines.extend([_sep, "\U0001f4a4 Stable", _sep])
        lines.extend(stable_lines)
        lines.append("")

    # --- 3. New entries ---
    if new_entries:
        lines.extend([_sep, "\U0001f195 New entries", _sep])
        for row in new_entries:
            lines.append(f"  \u2022 {row.get('question', row.get('entry_id', '?'))}")
        lines.append("")

    # --- 4. Expiring soon ---
    expiring_lines: list[str] = []
    now_date = datetime.now(timezone.utc).date()
    for row in (report.get("snapshot_rows", []) or []):
        if row.get("state") == "settled":
            continue
        end_str = str(row.get("end_date", "") or "")
        if not end_str:
            continue
        try:
            end_dt = datetime.fromisoformat(end_str.replace("Z", "+00:00")).date()
        except (ValueError, TypeError):
            try:
                end_dt = datetime.strptime(end_str[:10], "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue
        days_left = (end_dt - now_date).days
        if 0 <= days_left <= 30:
            expiring_lines.append(f"  \u2022 {row.get('question', row.get('entry_id', '?'))} ({days_left} days)")

    if expiring_lines:
        lines.extend([_sep, "\u23f3 Expiring soon", _sep])
        lines.extend(expiring_lines)
        lines.append("")

    # --- 5. Errors ---
    if error_entries:
        lines.append("\u26a0\ufe0f Errors")
        for row in error_entries:
            lines.append(f"  \u2022 {row.get('question', row.get('entry_id', '?'))} \u2014 API fetch failed")
        lines.append("")

    # --- 6. Settled ---
    if settled_entries:
        lines.append("\U0001f3c1 Settled")
        max_show = 5
        for row in settled_entries[:max_show]:
            lines.append(f"  \u2022 {row.get('question', row.get('entry_id', '?'))}")
        if len(settled_entries) > max_show:
            lines.append(f"  (+{len(settled_entries) - max_show} more)")
        lines.append("")

    lines.append("\u2014 Powered by SignalRadar")
    return "\n".join(line for line in lines if line is not None).strip()


def _finalize_digest_report(report: dict[str, Any], config: dict[str, Any]) -> dict[str, Any]:
    machine_payload = {
        "kind": "digest",
        "frequency": report.get("frequency"),
        "report_key": report.get("report_key"),
        "generated_at": report.get("generated_at"),
        "summary": report.get("summary", {}),
        "top_movers": report.get("top_movers", []),
        "events": report.get("events", []),
        "new_entries": report.get("new_entries", []),
        "settled_entries": report.get("settled_entries", []),
        "error_entries": report.get("error_entries", []),
    }
    report["human_text"] = _format_digest_text(report, config)
    report["machine_payload"] = machine_payload
    return report


def _has_digest_snapshot(state: dict[str, Any]) -> bool:
    snapshot = state.get("snapshot")
    return isinstance(snapshot, dict) and bool(snapshot)


def _apply_digest_state(report: dict[str, Any]) -> None:
    _save_digest_state(
        {
            "schema_version": 1,
            "last_report_key": report.get("report_key", ""),
            "last_report_ts": report.get("generated_at", ""),
            "snapshot": report.get("snapshot", {}),
        }
    )


def _run_digest_delivery(
    report: dict[str, Any],
    config: dict[str, Any],
    *,
    output_mode: str,
    dry_run: bool,
) -> dict[str, Any]:
    primary_channel = str(config.get("delivery", {}).get("primary", {}).get("channel", "webhook") or "webhook")
    payload = {
        "status": "NO_REPLY",
        "sent": False,
        "report_key": report.get("report_key", ""),
        "frequency": report.get("frequency", ""),
        "delivery": None,
        "human_text": report.get("human_text", ""),
    }
    if not report.get("due", False):
        payload["reason"] = report.get("due_reason", "not_due")
        return payload
    if dry_run:
        payload["status"] = "DRY_RUN"
        payload["reason"] = "dry_run"
        return payload

    if primary_channel == "openclaw":
        if output_mode == "openclaw":
            _apply_digest_state(report)
            payload["status"] = "SENT"
            payload["sent"] = True
            payload["delivery"] = {"status": "platform_stdout", "adapter": "openclaw"}
            return payload
        payload["status"] = "PREVIEW"
        payload["reason"] = "openclaw_requires_stdout"
        payload["delivery"] = {
            "status": "preview_only",
            "adapter": "openclaw",
            "note": "OpenClaw digest delivery requires --output openclaw or the scheduled background path.",
        }
        return payload

    outcome = deliver_digest(report, config, dry_run=False)
    if outcome.get("ok"):
        _apply_digest_state(report)
    payload["status"] = "SENT" if outcome.get("ok") else "ERROR"
    payload["sent"] = bool(outcome.get("ok"))
    payload["delivery"] = outcome
    return payload


def _bootstrap_digest_report(
    config: dict[str, Any],
    entries: list[dict[str, Any]],
    *,
    snapshot_rows: list[dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    report = _finalize_digest_report(
        _build_digest_report(config, entries, snapshot_rows=snapshot_rows),
        config,
    )
    _apply_digest_state(report)
    report["due"] = False
    report["due_reason"] = "bootstrap_snapshot"
    delivery = {
        "status": "BOOTSTRAP",
        "sent": False,
        "reason": "bootstrap_snapshot",
        "delivery": {
            "status": "bootstrap_only",
            "adapter": "digest_state",
            "note": "Initialized digest snapshot. First automatic digest will be sent from the next report cycle.",
        },
        "human_text": "",
        "report_key": report.get("report_key", ""),
        "frequency": report.get("frequency", ""),
    }
    return report, delivery


# ---------------------------------------------------------------------------
# Scheduling helpers (crontab + openclaw cron)
# ---------------------------------------------------------------------------

_CRON_TAG = "# signalradar-auto"
_OPENCLAW_CRON_NAME = "SignalRadar Auto-Monitor"


def _has_openclaw_cli() -> bool:
    return shutil.which("openclaw") is not None


def _resolve_schedule_driver(driver: str = "auto") -> str:
    if driver not in ("", "auto"):
        return driver
    # Prefer crontab (zero LLM cost) over openclaw cron (LLM cost per run)
    if _has_crontab():
        return "crontab"
    if _has_openclaw_cli():
        return "openclaw"
    return "none"


def _scheduler_run_command(output_mode: str) -> str:
    data_prefix = ""
    data_dir = os.environ.get("SIGNALRADAR_DATA_DIR", "").strip()
    if data_dir:
        data_prefix = f"SIGNALRADAR_DATA_DIR={shlex.quote(data_dir)} "
    return (
        f"cd {shlex.quote(str(SKILL_ROOT))} && "
        f"{data_prefix}python3 scripts/signalradar.py run --yes --output {output_mode}"
    )


def _openclaw_scheduler_prompt() -> str:
    command = _scheduler_run_command("openclaw")
    return (
        "Run the scheduled SignalRadar background check for this workspace.\n"
        f"Use Bash exactly once with this command:\n{command}\n"
        "If stdout is exactly HEARTBEAT_OK, reply with exactly HEARTBEAT_OK and nothing else.\n"
        "Otherwise reply with stdout exactly, no markdown, no commentary, no preface."
    )


def _push_message(text: str) -> dict[str, Any]:
    """Push a message via openclaw message send with explicit route.

    Returns delivery outcome dict with keys: attempted, sent, status, error.
    """
    outcome: dict[str, Any] = {
        "attempted": False,
        "sent": False,
        "status": "skipped",
        "error": "",
    }
    if not text or not _has_openclaw_cli():
        outcome["error"] = "no text or openclaw CLI not available"
        return outcome

    route = _load_reply_route()
    if not route:
        outcome["attempted"] = True
        outcome["status"] = "route_missing"
        outcome["error"] = "No stored reply route. A foreground bot interaction is needed first."
        return outcome

    cmd = [
        "openclaw", "message", "send",
        "--channel", route["channel"],
        "--target", route["target"],
        "--message", text,
    ]
    if route.get("account"):
        cmd.extend(["--account", route["account"]])
    if route.get("thread_id"):
        cmd.extend(["--thread-id", route["thread_id"]])

    outcome["attempted"] = True
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            outcome["sent"] = True
            outcome["status"] = "delivered"
        else:
            outcome["status"] = "send_failed"
            outcome["error"] = (result.stderr or result.stdout or "").strip()[:200]
    except Exception as exc:
        outcome["status"] = "send_error"
        outcome["error"] = str(exc)[:200]
    return outcome


def _cron_command_line() -> str:
    """Build the crontab command that runs SignalRadar."""
    log_path = _cron_log_path()
    # Only add --push when delivery channel is openclaw (needs reply route).
    # For webhook/file channels, deliver_hit()/deliver_digest() handle delivery directly.
    config = _load_config(None)
    primary_ch = str(config.get("delivery", {}).get("primary", {}).get("channel", "webhook") or "webhook")
    push_flag = " --push" if primary_ch == "openclaw" and _has_openclaw_cli() else ""
    return (
        f"{_scheduler_run_command('json')}{push_flag} "
        f">> {shlex.quote(str(log_path))} 2>&1  {_CRON_TAG}"
    )


def _has_crontab() -> bool:
    """Check if crontab command is available."""
    return shutil.which("crontab") is not None


def _read_crontab() -> str:
    """Read current crontab. Returns empty string if none."""
    try:
        result = subprocess.run(
            ["crontab", "-l"], capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            return ""
        return result.stdout or ""
    except Exception:
        return ""


def _write_crontab(content: str) -> tuple[bool, str]:
    """Write crontab from string content. Returns (ok, detail)."""
    try:
        fd, tmp = tempfile.mkstemp(suffix=".crontab", prefix="signalradar_")
        try:
            with os.fdopen(fd, "w") as f:
                f.write(content)
            result = subprocess.run(
                ["crontab", tmp], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                return True, ""
            detail = (result.stderr or result.stdout or "").strip()
            return False, detail or "unknown crontab error"
        finally:
            try:
                os.unlink(tmp)
            except OSError:
                pass
    except Exception as exc:
        return False, str(exc) or "unable to invoke crontab"


def _setup_cron(interval_minutes: int, driver: str = "auto") -> tuple[bool, str]:
    """Set up auto-monitoring cron job. Returns (success, message)."""
    driver = _resolve_schedule_driver(driver)
    if driver == "none":
        return False, "No available scheduler. openclaw CLI and crontab are both unavailable."
    if driver == "crontab":
        if not _has_crontab():
            return False, (
                "Note: crontab not available in this environment.\n"
                "To enable auto-monitoring, either:\n"
                "  - Install crontab, then: signalradar.py schedule 10\n"
                "  - Use openclaw: signalradar.py schedule 10 --driver openclaw\n"
                "  - Run manually: signalradar.py run"
            )

        # Remove existing signalradar cron line, then add new one
        existing = _read_crontab()
        lines = [l for l in existing.splitlines() if _CRON_TAG not in l]
        new_line = f"*/{interval_minutes} * * * * {_cron_command_line()}"
        lines.append(new_line)
        # Ensure trailing newline
        content = "\n".join(lines).strip() + "\n"
        ok, detail = _write_crontab(content)
        if ok:
            return True, f"Auto-monitoring enabled: every {interval_minutes} minutes (crontab)."
        return False, f"Failed to write crontab. {detail}".strip()

    elif driver == "openclaw":
        cmd = [
            "openclaw", "cron", "add",
            "--name", _OPENCLAW_CRON_NAME,
            "--every", f"{interval_minutes}m",
            "--session", "isolated",
            "--message", _openclaw_scheduler_prompt(),
            "--announce",
            "--channel", "last",
            "--json",
        ]
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                try:
                    payload = json.loads(result.stdout)
                    if payload.get("ok"):
                        return True, f"Auto-monitoring enabled: every {interval_minutes} minutes (openclaw cron)."
                except json.JSONDecodeError:
                    pass
            stderr = (result.stderr or "").strip()
            return False, f"Failed to create openclaw cron job. {stderr}"
        except FileNotFoundError:
            return False, "openclaw command not found."
        except Exception as e:
            return False, f"Error creating openclaw cron: {e}"

    return False, f"Unknown driver: {driver}"


def _remove_cron() -> tuple[bool, str]:
    """Remove all signalradar cron jobs (both drivers). Returns (success, message)."""
    removed_any = False

    # Try crontab removal
    if _has_crontab():
        existing = _read_crontab()
        if _CRON_TAG in existing:
            lines = [l for l in existing.splitlines() if _CRON_TAG not in l]
            content = "\n".join(lines).strip()
            if content:
                content += "\n"
            else:
                # Empty crontab — remove entirely
                subprocess.run(
                    ["crontab", "-r"], capture_output=True, text=True, timeout=10
                )
                removed_any = True
                # Skip write since we removed
                content = ""
            if content:
                ok, _detail = _write_crontab(content)
                if ok:
                    removed_any = True
            elif not removed_any:
                removed_any = True  # nothing to write, crontab already cleared

    # Try openclaw cron removal
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            jobs = json.loads(result.stdout)
            if isinstance(jobs, list):
                for job in jobs:
                    if "SignalRadar" in str(job.get("name", "")):
                        job_id = job.get("id", "")
                        if job_id:
                            subprocess.run(
                                ["openclaw", "cron", "delete", str(job_id)],
                                capture_output=True, text=True, timeout=15
                            )
                            removed_any = True
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        pass  # openclaw not available, skip

    if removed_any:
        return True, "Auto-monitoring disabled."
    return True, "No active auto-monitoring found."


def _check_cron_status() -> dict[str, Any]:
    """Check current cron scheduling status. Returns frozen-contract dict."""
    status: dict[str, Any] = {
        "enabled": False,
        "interval": 0,
        "driver": "none",
        "next_run": "unknown",
        "last_run": "never",
        "last_run_status": "unknown",
    }

    # Check last_run from cache
    last_run_file = _last_run_path()
    if last_run_file.exists():
        try:
            lr = json.loads(last_run_file.read_text(encoding="utf-8"))
            status["last_run"] = lr.get("ts", "never")
            status["last_run_status"] = lr.get("status", "unknown")
        except Exception:
            pass

    # Check openclaw cron
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            jobs = json.loads(result.stdout)
            if isinstance(jobs, list):
                for job in jobs:
                    if "SignalRadar" in str(job.get("name", "")):
                        status["enabled"] = True
                        status["driver"] = "openclaw"
                        # Parse interval from every field
                        every = str(job.get("every", ""))
                        if every.endswith("m"):
                            try:
                                status["interval"] = int(every[:-1])
                            except ValueError:
                                pass
                        next_run = job.get("next_run")
                        status["next_run"] = next_run if next_run else "unknown"
                        return status
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        pass

    # Check crontab
    if _has_crontab():
        existing = _read_crontab()
        for line in existing.splitlines():
            if _CRON_TAG in line and not line.strip().startswith("#"):
                status["enabled"] = True
                status["driver"] = "crontab"
                # Parse interval from */N pattern
                parts = line.strip().split()
                if parts and parts[0].startswith("*/"):
                    try:
                        status["interval"] = int(parts[0][2:])
                    except ValueError:
                        pass
                status["next_run"] = "unknown"
                return status

    return status


def _ensure_auto_monitoring(interval: int = 10, config_override: str = "", quiet: bool = False, driver: str = "auto") -> dict[str, Any]:
    """Check if cron exists; if not, set it up. Idempotent.

    When delivery.primary.channel == openclaw and the resolved driver is
    crontab (which uses --push), refuse to arm if no reply route is stored.
    Explicit --driver openclaw bypasses this gate (platform announce path).
    """
    cron_status = _check_cron_status()
    if cron_status["enabled"]:
        return {
            "auto_enabled": False,
            "interval_minutes": cron_status.get("interval", interval),
            "driver": cron_status.get("driver", "none"),
            "message": "Auto-monitoring already active.",
        }

    resolved_driver = _resolve_schedule_driver(driver)

    # Delivery readiness check
    route_missing = False
    webhook_unconfigured = False
    config = _load_config(config_override)
    primary_ch = str(config.get("delivery", {}).get("primary", {}).get("channel", "openclaw") or "openclaw")

    if resolved_driver == "crontab" and primary_ch == "openclaw" and _load_reply_route() is None:
        route_missing = True
        if not quiet:
            print(
                "\nWarning: Background push is NOT READY (no reply route captured). "
                "Monitoring will start, but alerts cannot be pushed until you chat "
                "with the bot to capture the route."
            )
    elif primary_ch == "webhook":
        target = str(config.get("delivery", {}).get("primary", {}).get("target", "") or "").strip()
        if not target.startswith("http://") and not target.startswith("https://"):
            webhook_unconfigured = True
            if not quiet:
                print(
                    "\nWarning: Webhook URL not configured. Background alerts will not be "
                    "delivered until you set a webhook URL.\n"
                    "  Use: signalradar.py config delivery.primary.target <YOUR_WEBHOOK_URL>"
                )

    ok, msg = _setup_cron(interval, resolved_driver)
    if ok:
        refreshed = _check_cron_status()
        message = f"Auto-monitoring enabled: checking every {interval} minutes."
        if route_missing:
            message += " (push NOT READY — no reply route)"
        elif webhook_unconfigured:
            message += " (webhook URL not configured — alerts will not be delivered)"
        if not quiet:
            print(f"\n{message}")
            if refreshed.get("driver") and refreshed.get("driver") != "none":
                print(f"Driver: {refreshed['driver']}")
            print(f"To change frequency: signalradar.py schedule 30")
            print(f"To disable: signalradar.py schedule disable")
        # Sync check_interval_minutes to config
        _save_config_key(config_override, "check_interval_minutes", interval)
        result = {
            "auto_enabled": True,
            "interval_minutes": interval,
            "driver": refreshed.get("driver", resolved_driver),
            "message": message,
        }
        if route_missing:
            result["route_missing"] = True
        if webhook_unconfigured:
            result["webhook_unconfigured"] = True
        return result
    if not quiet:
        print(f"\n{msg}")
    return {
        "auto_enabled": False,
        "interval_minutes": interval,
        "driver": resolved_driver if resolved_driver != "none" else "none",
        "message": msg,
    }


# ---------------------------------------------------------------------------
# cmd_doctor
# ---------------------------------------------------------------------------

def cmd_doctor(args: argparse.Namespace) -> int:
    config = _load_config(args.config)
    checks: list[dict[str, Any]] = []
    data_root = _user_data_root()

    def check(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    check("skill_root_exists", SKILL_ROOT.exists(), str(SKILL_ROOT))
    check("data_directory_exists", data_root.exists(), str(data_root))
    check("data_directory_writable", os.access(data_root, os.W_OK), str(data_root))
    check("openclaw_cli_available", _has_openclaw_cli(), shutil.which("openclaw") or "not found")
    check("schedule_driver_default", _resolve_schedule_driver() != "none", _resolve_schedule_driver())
    wl_path = _watchlist_path()
    if not wl_path.exists():
        check("watchlist_loadable", True, f"not yet created: {wl_path}")
    else:
        # Try strict JSON parse first to detect corruption
        try:
            raw = json.loads(wl_path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                check("watchlist_loadable", False, f"watchlist is not a JSON object: {wl_path}")
            elif not isinstance(raw.get("entries"), list):
                check("watchlist_loadable", False, f"watchlist.entries missing or not a list: {wl_path}")
            elif not isinstance(raw.get("archived", []), list):
                check("watchlist_loadable", False, f"watchlist.archived is not a list: {wl_path}")
            else:
                check("watchlist_loadable", True, str(wl_path))
                check("watchlist_entries", True, f"{len(raw.get('entries', []))} entries")
        except (json.JSONDecodeError, ValueError) as e:
            check("watchlist_corrupted", False, f"JSON parse error: {e} — file: {wl_path}")

    cfg_path = _config_path(args.config)
    check("config_exists_optional", True, str(cfg_path) if cfg_path.exists() else f"missing(optional): {cfg_path}")
    primary_channel = str(config.get("delivery", {}).get("primary", {}).get("channel", "webhook") or "webhook").strip().lower()
    check(
        "delivery_primary_supported",
        primary_channel in _SUPPORTED_DELIVERY_CHANNELS,
        primary_channel if primary_channel else "missing",
    )
    # Webhook URL readiness check
    if primary_channel == "webhook":
        target = str(config.get("delivery", {}).get("primary", {}).get("target", "") or "").strip()
        webhook_ok = target.startswith("http://") or target.startswith("https://")
        check(
            "webhook_url_configured",
            webhook_ok,
            target[:80] if webhook_ok else "not configured — use: signalradar.py config delivery.primary.target <URL>",
        )
    cache_dir = _user_data_root() / "cache"
    check("cache_dir_writable", cache_dir.exists() and os.access(cache_dir, os.W_OK), str(cache_dir))

    interval = config.get("check_interval_minutes", 10)
    non_blocking_checks = {"openclaw_cli_available", "webhook_url_configured"}
    ok = all(
        item["ok"]
        for item in checks
        if item["name"] not in non_blocking_checks
    )
    payload: dict[str, Any] = {
        "status": "HEALTHY" if ok else "WARN",
        "data_directory": {
            "path": str(data_root),
            "exists": data_root.exists(),
            "writable": os.access(data_root, os.W_OK),
        },
        "check_interval_minutes": interval,
        "checks": checks,
    }

    if args.output == "json":
        _json_print(payload)
    else:
        if ok:
            print(f"✅ HEALTHY — check_interval_minutes={interval}")
            print(f"data_directory: {data_root}  (exists: {data_root.exists()}, writable: {os.access(data_root, os.W_OK)})")
        else:
            print("⚠️ WARN")
            print(f"data_directory: {data_root}  (exists: {data_root.exists()}, writable: {os.access(data_root, os.W_OK)})")
            for item in checks:
                if not item["ok"]:
                    print(f"  ⚠️ {item['name']}: {item['detail']}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# cmd_add
# ---------------------------------------------------------------------------

def cmd_add(args: argparse.Namespace) -> int:
    url = args.url
    output_json = args.output == "json"

    # No URL provided
    if not url:
        wl = load_watchlist(_watchlist_path())
        if not wl.get("entries"):
            if output_json:
                _json_print({
                    "status": "ONBOARD_NEEDED",
                    "request_id": str(uuid.uuid4()),
                    "ts": _utc_now(),
                    "message": "Watchlist is empty. Run 'signalradar.py onboard --step preview --output json' to start guided setup.",
                })
                return 0
            # Terminal mode: interactive onboarding
            return _onboarding(args)
        else:
            if output_json:
                _json_print(
                    _add_result_payload(
                        status="ERROR",
                        error="Usage: signalradar.py add <polymarket-event-url> or run without a URL on first use for guided setup.",
                    )
                )
            else:
                print("Usage: signalradar.py add <polymarket-event-url>")
                print("       signalradar.py add  (guided setup, first time only)")
            return 1

    slug = parse_polymarket_url(url)
    if not slug:
        if output_json:
            _json_print(
                _add_result_payload(
                    status="ERROR",
                    error=f"Cannot parse Polymarket event URL: {url}",
                )
            )
        else:
            print(f"Error: Cannot parse Polymarket event URL: {url}")
        return 1

    result = resolve_event(slug)
    if not result["ok"]:
        if output_json:
            _json_print(
                _add_result_payload(
                    status="ERROR",
                    error=str(result["error"]),
                )
            )
        else:
            print(f"Error: {result['error']}")
        return 1

    event_title = result["event_title"]
    markets = result["markets"]
    event_id = result["event_id"]

    if not markets:
        if output_json:
            _json_print(
                _add_result_payload(
                    status="NO_REPLY",
                    event_title=event_title,
                    message=f"No markets found for event '{event_title}'.",
                )
            )
        else:
            print(f"No markets found for event '{event_title}'.")
        return 1

    # Check for settled markets
    settled_markets = [m for m in markets if is_settled(m)]
    active_markets = [m for m in markets if not is_settled(m)]

    if settled_markets and not active_markets:
        warning = f"Warning: All {len(markets)} markets in '{event_title}' are settled."
        if not output_json:
            print(warning)
        if not args.yes:
            answer = input("Add anyway? (y/N): ").strip().lower()
            if answer not in ("y", "yes"):
                if output_json:
                    _json_print(
                        _add_result_payload(
                            status="NO_REPLY",
                            event_title=event_title,
                            message="Cancelled.",
                        )
                    )
                else:
                    print("Cancelled.")
                return 0

    # Multi-market events: always preview before write. Large batches require
    # interactive confirmation even if --yes was passed.
    if len(active_markets) > 3:
        if not output_json:
            _print_market_preview(event_title, active_markets, settled_markets)
        if args.yes:
            error = "Bulk add (>3 markets) requires interactive confirmation. Re-run without --yes after reviewing the market preview above."
            if output_json:
                _json_print(
                    _add_result_payload(
                        status="ERROR",
                        event_title=event_title,
                        error=error,
                    )
                )
            else:
                print("\nError: bulk add (>3 markets) requires interactive confirmation.")
                print("Re-run without --yes after reviewing the market preview above.")
            return 1
        answer = input(f"Confirm adding all {len(active_markets)} markets? (Y/n): ").strip().lower()
        if answer in ("n", "no"):
            if output_json:
                _json_print(
                    _add_result_payload(
                        status="NO_REPLY",
                        event_title=event_title,
                        message="Cancelled.",
                    )
                )
            else:
                print("Cancelled.")
            return 0
    elif len(active_markets) > 1:
        if not output_json:
            _print_market_preview(event_title, active_markets, settled_markets)
        if not args.yes:
            answer = input(f"Add all {len(active_markets)} markets? (Y/n): ").strip().lower()
            if answer in ("n", "no"):
                if output_json:
                    _json_print(
                        _add_result_payload(
                            status="NO_REPLY",
                            event_title=event_title,
                            message="Cancelled.",
                        )
                    )
                else:
                    print("Cancelled.")
                return 0

    elif len(active_markets) == 1:
        m = active_markets[0]
        if not output_json:
            print(f"\n{m['question']}  {m['probability']:.0f}%")
        if not args.yes:
            answer = input("Add this market? (Y/n): ").strip().lower()
            if answer in ("n", "no"):
                if output_json:
                    _json_print(
                        _add_result_payload(
                            status="NO_REPLY",
                            event_title=event_title,
                            message="Cancelled.",
                        )
                    )
                else:
                    print("Cancelled.")
                return 0
    else:
        # Only settled markets but user confirmed above
        active_markets = markets

    # Check if watchlist was empty before this add
    wl_path = _watchlist_path()
    wl_before = load_watchlist(wl_path)
    was_empty = not wl_before.get("entries")

    # Build watchlist entries
    category = args.category or "default"
    now = _utc_now()
    new_entries = []
    market_by_entry_id = {m["entry_id"]: m for m in active_markets}
    for m in active_markets:
        new_entries.append({
            "entry_id": m["entry_id"],
            "slug": m["slug"],
            "event_title": event_title,
            "question": m["question"],
            "category": category,
            "url": m["url"],
            "end_date": m.get("end_date", ""),
            "added_at": now,
        })

    added, skipped = add_entries(wl_path, new_entries)

    # Record baselines for newly added entries
    baseline_dir = _baseline_dir()
    for entry in added:
        # Find the market data to get probability
        for m in active_markets:
            if m["entry_id"] == entry["entry_id"]:
                check_entry(
                    entry_id=entry["entry_id"],
                    question=entry["question"],
                    current_prob=m["probability"],
                    baseline_dir=baseline_dir,
                    threshold_abs_pp=5.0,
                    dry_run=False,
                )
                break

    # Show results
    if added and not output_json:
        print(f"\n🆕 Added {len(added)} market(s):")
        for entry in added:
            prob = ""
            m = market_by_entry_id.get(entry["entry_id"])
            if m is not None:
                prob = f"  {m['probability']:.0f}% (baseline)"
            print(f"  ✅ {entry['question']}{prob}")

    if skipped and not output_json:
        print(f"\n⚠️ Skipped {len(skipped)} (already in watchlist):")
        for entry in skipped:
            print(f"  {entry['question']}")

    # Auto-monitoring: enable on first add (watchlist was empty)
    schedule_info: dict[str, Any] | None = None
    if added:
        _persist_detected_language_if_needed(getattr(args, "config", ""))
    if added and was_empty:
        schedule_info = _ensure_auto_monitoring(
            interval=10,
            config_override=getattr(args, "config", ""),
            quiet=output_json,
        )

    if output_json:
        added_payload = []
        for entry in added:
            item = dict(entry)
            market = market_by_entry_id.get(entry["entry_id"])
            if market is not None:
                item["baseline"] = market.get("probability")
            added_payload.append(item)
        skipped_payload = [dict(entry) for entry in skipped]
        payload = _add_result_payload(
            status="OK" if added else "NO_REPLY",
            event_title=event_title,
            added=added_payload,
            skipped=skipped_payload,
            message="Added monitored markets." if added else "No new markets were added.",
        )
        if schedule_info is not None:
            payload["schedule"] = schedule_info
        _json_print(payload)

    return 0


# ---------------------------------------------------------------------------
# cmd_config
# ---------------------------------------------------------------------------

def cmd_config(args: argparse.Namespace) -> int:
    cfg_path = _config_path(args.config)
    user_cfg = load_json_config(cfg_path)
    merged = deep_merge(DEFAULT_CONFIG, user_cfg)

    # No key specified: show current config
    if not args.key:
        if args.output == "json":
            _json_print(merged)
        else:
            print("Current config:\n")
            for k, v in sorted(merged.items()):
                if isinstance(v, dict):
                    print(f"  {k}:")
                    for k2, v2 in sorted(v.items()):
                        print(f"    {k2}: {v2}")
                else:
                    print(f"  {k}: {v}")
            print(f"\nConfig file: {cfg_path}")
        return 0

    key = args.key

    # Shortcut: "config delivery webhook <url>" sets both channel and target
    if key == "delivery" and args.value is not None:
        val = str(args.value).strip()
        if val.startswith("webhook ") or val.startswith("webhook\t"):
            url = val.split(None, 1)[1].strip()
            if not url.startswith("http://") and not url.startswith("https://"):
                print("Error: Webhook URL must start with http:// or https://")
                return 1
            set_nested_value(user_cfg, "delivery.primary.channel", "webhook")
            set_nested_value(user_cfg, "delivery.primary.target", url)
            save_json_config(cfg_path, user_cfg)
            print(f"🔄 Set delivery.primary.channel = webhook")
            print(f"🔄 Set delivery.primary.target = {url}")
            print(f"✅ Saved to {cfg_path}")
            return 0

    # No value specified: show current value for that key
    if args.value is None:
        found, value = get_nested_value(merged, key)
        if not found:
            print(f"Unknown key: {key}")
            return 1
        if isinstance(value, (dict, list)):
            print(json.dumps(value, ensure_ascii=False, indent=2))
        else:
            print(f"{key}: {value}")
        return 0

    if not _config_key_exists(key, merged):
        print(f"Unknown key: {key}")
        return 1

    parsed_value = _parse_cli_value(args.value)
    validation_error = _validate_config_value(key, parsed_value)
    if validation_error:
        print(f"Error: {validation_error}")
        return 1

    set_nested_value(user_cfg, key, parsed_value)
    save_json_config(cfg_path, user_cfg)

    print(f"🔄 Set {key} = {parsed_value}")
    print(f"✅ Saved to {cfg_path}")
    if key == "check_interval_minutes":
        print("📎 Note: this updates the display value only. Use 'signalradar.py schedule N' to change actual monitoring frequency.")
    if key == "delivery.primary.channel" and str(parsed_value).strip().lower() == "webhook":
        # Warn if webhook target is not a valid URL
        reloaded = deep_merge(DEFAULT_CONFIG, load_json_config(cfg_path))
        target = str(reloaded.get("delivery", {}).get("primary", {}).get("target", "") or "").strip()
        if not target.startswith("http://") and not target.startswith("https://"):
            print("⚠️ Warning: delivery.primary.target is not set to a valid URL. "
                  "Use 'signalradar.py config delivery.primary.target <URL>' to set it.")
    return 0


# ---------------------------------------------------------------------------
# cmd_schedule
# ---------------------------------------------------------------------------

def cmd_schedule(args: argparse.Namespace) -> int:
    action = args.action
    config = _load_config(getattr(args, "config", ""))
    resolved_default = _resolve_schedule_driver()

    # No argument: show current status
    if not action:
        status = _check_cron_status()
        route = _load_reply_route()
        route_ready = route is not None
        primary_ch = str(config.get("delivery", {}).get("primary", {}).get("channel", "openclaw") or "openclaw")
        # Read last delivery info from last_run.json
        last_delivery_status = ""
        last_delivery_error = ""
        lr_path = _last_run_path()
        if lr_path.exists():
            try:
                lr = json.loads(lr_path.read_text(encoding="utf-8"))
                last_delivery_status = lr.get("delivery_status", "")
                last_delivery_error = lr.get("delivery_error", "")
            except Exception:
                pass
        # Channel-aware delivery readiness
        webhook_target = str(config.get("delivery", {}).get("primary", {}).get("target", "") or "").strip()
        if primary_ch == "webhook":
            delivery_ready = bool(webhook_target)
            delivery_status = "ready" if delivery_ready else "webhook_url_missing"
        elif primary_ch == "openclaw":
            delivery_ready = route_ready
            delivery_status = "ready" if route_ready else "route_missing"
        elif primary_ch == "file":
            delivery_ready = bool(webhook_target)  # target is file path for file channel
            delivery_status = "ready" if delivery_ready else "file_target_missing"
        else:
            delivery_ready = False
            delivery_status = "unknown_channel"

        if args.output == "json":
            payload = dict(status)
            payload["default_driver"] = resolved_default
            payload["delivery_channel"] = primary_ch
            payload["delivery_status"] = delivery_status
            # Channel-specific fields (only include what's relevant)
            if primary_ch == "openclaw":
                payload["route_ready"] = route_ready
                payload["route_channel"] = route.get("channel", "") if route else ""
                payload["route_captured_at"] = route.get("captured_at", "") if route else ""
            elif primary_ch == "webhook":
                payload["webhook_url_configured"] = bool(webhook_target)
            payload["last_delivery_status"] = last_delivery_status
            payload["last_delivery_error"] = last_delivery_error
            _json_print(payload)
        else:
            if status["enabled"]:
                print(f"Auto-monitoring: enabled")
                print(f"  Interval: every {status['interval']} minutes")
                print(f"  Driver: {status['driver']}")
                print(f"  Next run: {_format_user_time(status['next_run'], config)}")
                print(f"  Last run: {_format_user_time(status['last_run'], config)}")
                print(f"  Last status: {status['last_run_status']}")
            else:
                print("Auto-monitoring: disabled")
                print(f"  Default driver: {resolved_default}")
                if status["last_run"] != "never":
                    print(f"  Last run: {_format_user_time(status['last_run'], config)}")
                    print(f"  Last status: {status['last_run_status']}")
                print("\nTo enable: signalradar.py schedule 10")
            # Channel-aware delivery readiness
            print(f"  Delivery channel: {primary_ch}")
            if primary_ch == "webhook":
                if delivery_ready:
                    print(f"  Background delivery: ready (webhook configured)")
                else:
                    print("  Background delivery: NOT READY (webhook URL not configured)")
                    print("    Set it with: signalradar.py config delivery webhook <URL>")
            elif primary_ch == "openclaw":
                if route_ready:
                    print(f"  Background delivery: ready (route: {route['channel']})")
                else:
                    print("  Background delivery: NOT READY (no reply route captured yet)")
                    print("    A foreground bot interaction is needed to capture the reply route.")
            elif primary_ch == "file":
                if delivery_ready:
                    print(f"  Background delivery: ready (file target configured)")
                else:
                    print("  Background delivery: NOT READY (file target not configured)")
            if last_delivery_status:
                print(f"  Last delivery: {last_delivery_status}")
                if last_delivery_error:
                    print(f"    Error: {last_delivery_error}")
        return 0

    # Disable
    if action == "disable":
        ok, msg = _remove_cron()
        print(msg)
        return 0 if ok else 1

    # Numeric interval
    try:
        interval = int(action)
    except ValueError:
        print(f"Error: Invalid argument '{action}'. Use a number (minutes) or 'disable'.")
        return 1

    if interval < 5:
        print("Minimum interval is 5 minutes (prevents overlapping runs).")
        return 1

    driver = _resolve_schedule_driver(args.driver)
    if driver == "none":
        print("Error: No scheduler available. Install openclaw CLI or crontab.")
        return 1

    # Route gate warning: crontab + openclaw delivery + no route → warn but proceed
    config_override = getattr(args, "config", "")
    if driver == "crontab":
        config = _load_config(config_override)
        primary_ch = str(config.get("delivery", {}).get("primary", {}).get("channel", "openclaw") or "openclaw")
        if primary_ch == "openclaw" and _load_reply_route() is None:
            print(
                "Warning: Background push is NOT READY (no reply route captured). "
                "Monitoring will start, but alerts cannot be pushed until you chat "
                "with the bot to capture the route."
            )

    # Remove existing first (any driver), then set up new
    _remove_cron()

    ok, msg = _setup_cron(interval, driver=driver)
    print(msg)

    if ok:
        # Sync check_interval_minutes to config
        _save_config_key(config_override, "check_interval_minutes", interval)
        print(f"To change: signalradar.py schedule {interval}")
        print(f"To disable: signalradar.py schedule disable")

    return 0 if ok else 1


# ---------------------------------------------------------------------------
# cmd_list
# ---------------------------------------------------------------------------

def cmd_list(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())

    if getattr(args, "output", "text") == "json":
        entries = wl.get("entries", [])
        if args.archived:
            entries = wl.get("archived", [])
        result_entries = []
        for i, entry in enumerate(entries, 1):
            cat = entry.get("category", "default")
            if args.category and cat != args.category:
                continue
            entry_id = str(entry.get("entry_id", ""))
            baseline_val = _read_baseline_value(entry_id)
            baseline_ts = _read_baseline_ts(entry_id)
            result_entries.append({
                "number": i,
                "entry_id": entry_id,
                "question": entry.get("question", ""),
                "category": cat,
                "event_title": entry.get("event_title", ""),
                "baseline": baseline_val,
                "baseline_ts": baseline_ts,
                "end_date": entry.get("end_date", ""),
                "settled": bool(entry.get("settled") or entry.get("archive_reason") == "settled"),
            })
        _json_print({"status": "OK", "total": len(result_entries), "entries": result_entries})
        return 0

    if args.archived:
        archived = wl.get("archived", [])
        if not archived:
            print("No archived entries.")
            return 0
        print(f"Archived entries ({len(archived)}):\n")
        for i, entry in enumerate(archived, 1):
            reason = entry.get("archive_reason", "unknown")
            archived_at = entry.get("archived_at", "")[:10]
            print(f"  {i}. {entry.get('question', entry.get('entry_id', '?'))}")
            print(f"     Reason: {reason}  Archived: {archived_at}")
        return 0

    entries = wl.get("entries", [])
    if not entries:
        print("Watchlist is empty. Use 'signalradar.py add <url>' to add markets.")
        return 0

    # Group by category
    by_category: dict[str, list[tuple[int, dict]]] = {}
    for i, entry in enumerate(entries, 1):
        cat = entry.get("category", "default")
        if args.category and cat != args.category:
            continue
        by_category.setdefault(cat, []).append((i, entry))

    if not by_category:
        print(f"No entries in category '{args.category}'.")
        return 0

    total = sum(len(v) for v in by_category.values())
    print(f"Watchlist ({total} entries):\n")
    for cat in sorted(by_category.keys()):
        print(f"  [{cat}]")
        for num, entry in by_category[cat]:
            q = entry.get("question", entry.get("entry_id", "?"))
            end = entry.get("end_date", "")
            baseline_val = _read_baseline_value(str(entry.get("entry_id", "")))
            parts = [f"    {num}. {q}"]
            if baseline_val is not None:
                parts.append(f"  (baseline {baseline_val}%)")
            if end:
                parts.append(f"  (ends {end})")
            print("".join(parts))
        print()

    return 0


# ---------------------------------------------------------------------------
# cmd_show
# ---------------------------------------------------------------------------

def cmd_show(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entries = wl.get("entries", [])

    if not entries:
        if args.output == "json":
            _json_print({
                "status": "NO_REPLY",
                "request_id": str(uuid.uuid4()),
                "ts": _utc_now(),
                "matches": [],
                "errors": [],
                "message": "Watchlist is empty",
            })
        else:
            print("No monitored markets yet. Add one with: signalradar.py add <url>")
        return 0

    matches = _find_entries_for_show(wl, args.target)
    if not matches:
        if args.output == "json":
            _json_print({
                "status": "NO_REPLY",
                "request_id": str(uuid.uuid4()),
                "ts": _utc_now(),
                "matches": [],
                "errors": [],
                "message": f"No monitored market matched '{args.target}'",
            })
        else:
            print(f"No monitored market matched '{args.target}'.")
            print("Tip: use a list number from 'signalradar.py list' or a keyword from the market question.")
        return 1

    request_id = str(uuid.uuid4())
    run_ts = _utc_now()
    config = _load_config(getattr(args, "config", ""))
    payload_matches: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for entry in matches:
        entry_id = str(entry.get("entry_id", ""))
        market_id = entry_id.split(":")[1] if ":" in entry_id else ""
        if not market_id:
            errors.append(_run_error(entry_id, "SR_VALIDATION_ERROR", "Entry ID format is invalid."))
            continue

        current_market, fetch_error = fetch_market_current_result(market_id)
        if current_market is None:
            if is_settled(entry):
                payload_matches.append(
                    _build_observation(
                        entry,
                        state="settled",
                        decision="SETTLED",
                    )
                )
                continue
            errors.append(
                _run_error(
                    entry_id,
                    fetch_error.get("code", "SR_SOURCE_UNAVAILABLE") if fetch_error else "SR_SOURCE_UNAVAILABLE",
                    fetch_error.get("message", "Could not fetch current market data from Polymarket API.") if fetch_error else "Could not fetch current market data from Polymarket API.",
                )
            )
            continue

        payload_matches.append(
            _build_observation(
                entry,
                state="settled" if is_settled(current_market) else "checked",
                decision="SETTLED" if is_settled(current_market) else "SNAPSHOT",
                current_market=current_market,
            )
        )

    status = "ERROR" if errors and not payload_matches else "OK"
    if args.output == "json":
        _json_print({
            "status": status,
            "request_id": request_id,
            "ts": run_ts,
            "matches": payload_matches,
            "errors": errors,
        })
        return 0 if status != "ERROR" else 1

    print(f"Matched {len(payload_matches)} monitored market(s):\n")
    for item in payload_matches:
        print(f"  {item.get('question', item.get('entry_id', '?'))}")
        if item.get("state") == "settled":
            print("    Market appears settled. No new alerts will fire.")
        else:
            print(f"    Current probability: {item.get('current')}%")
        if item.get("baseline") is not None:
            print(f"    Last-known baseline: {item.get('baseline')}%")
        if item.get("baseline_ts"):
            print(f"    Baseline time: {_format_user_time(str(item.get('baseline_ts')), config)}")
        if item.get("category"):
            print(f"    Category: {item.get('category')}")
        if item.get("url"):
            print(f"    URL: {item.get('url')}")
        print()

    if errors:
        print(f"Could not fetch {len(errors)} matched market(s):")
        for error in errors:
            print(f"  {error.get('entry_id', 'unknown')}: {error.get('message', 'Unknown error')} ({error.get('code', 'SR_SOURCE_UNAVAILABLE')})")

    if payload_matches:
        print(f"Snapshot time: {_format_user_time(run_ts, config)}")

    return 0 if status != "ERROR" else 1


# ---------------------------------------------------------------------------
# cmd_digest
# ---------------------------------------------------------------------------

def cmd_digest(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entries = wl.get("entries", [])
    request_id = str(uuid.uuid4())
    ts = _utc_now()
    config = _load_config(getattr(args, "config", ""))
    frequency = str(config.get("digest", {}).get("frequency", "weekly") or "weekly").strip().lower()

    if not entries:
        payload = {
            "status": "NO_REPLY",
            "request_id": request_id,
            "ts": ts,
            "digest": None,
            "message": "Watchlist is empty",
        }
        if args.output == "json":
            _json_print(payload)
        else:
            print("Watchlist is empty. No digest available.")
        return 0

    if frequency == "off" and not args.force:
        payload = {
            "status": "NO_REPLY",
            "request_id": request_id,
            "ts": ts,
            "digest": None,
            "message": "Digest is disabled. Set digest.frequency first.",
        }
        if args.output == "json":
            _json_print(payload)
        else:
            print("Digest is disabled. Set digest.frequency first.")
        return 0

    report = _finalize_digest_report(
        _build_digest_report(config, entries, force=args.force),
        config,
    )
    delivery = _run_digest_delivery(
        report,
        config,
        output_mode=args.output,
        dry_run=args.dry_run,
    )

    if args.output == "json":
        _json_print(
            {
                "status": "OK" if report.get("human_text") else "NO_REPLY",
                "request_id": request_id,
                "ts": ts,
                "digest": {
                    "frequency": report.get("frequency"),
                    "report_key": report.get("report_key"),
                    "due": report.get("due"),
                    "due_reason": report.get("due_reason"),
                    "first_report": report.get("first_report"),
                    "generated_at": report.get("generated_at"),
                    "scheduled_local": report.get("scheduled_local"),
                    "summary": report.get("summary", {}),
                    "top_movers": report.get("top_movers", []),
                    "events": report.get("events", []),
                    "new_entries": report.get("new_entries", []),
                    "settled_entries": report.get("settled_entries", []),
                    "error_entries": report.get("error_entries", []),
                    "delivery": delivery,
                },
            }
        )
        return 0

    if args.output == "openclaw":
        primary_channel = str(config.get("delivery", {}).get("primary", {}).get("channel", "webhook") or "webhook")
        if primary_channel == "openclaw" and delivery.get("sent"):
            print(report.get("human_text", ""))
        else:
            print("HEARTBEAT_OK")
        return 0 if delivery.get("status") != "ERROR" else 1

    if not report.get("due") and not args.force and not args.dry_run:
        print("No digest is due right now. Previewing the current report:\n")
    elif args.dry_run:
        print("Digest preview (dry-run):\n")

    print(report.get("human_text", ""))

    if delivery.get("sent"):
        print("\nDigest delivered.")
    elif delivery.get("status") == "PREVIEW":
        print("\nDigest preview only. OpenClaw delivery happens through scheduled background runs or --output openclaw.")
    elif delivery.get("status") == "ERROR":
        print(f"\nDigest delivery failed: {delivery.get('delivery', {}).get('error', 'Unknown error')}")
        return 1

    return 0


# ---------------------------------------------------------------------------
# cmd_remove
# ---------------------------------------------------------------------------

def cmd_remove(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entry = get_entry_by_number(wl, args.number)

    if entry is None:
        print(f"Error: No entry #{args.number}. Use 'signalradar.py list' to see entries.")
        return 1

    question = entry.get("question", entry.get("entry_id", "?"))
    print(f"\n🗑️ Removing #{args.number}: {question}")

    if not args.yes:
        answer = input("Confirm removal? (y/N): ").strip().lower()
        if answer not in ("y", "yes"):
            print("Cancelled.")
            return 0

    # Collect baseline history before archiving
    entry_id = entry.get("entry_id", "")
    baseline_dir = _baseline_dir()
    baseline_file = baseline_dir / f"{safe_name(entry_id)}.json"
    baseline_history = []
    if baseline_file.exists():
        try:
            bl = json.loads(baseline_file.read_text(encoding="utf-8"))
            baseline_history.append({
                "value": bl.get("baseline"),
                "ts": bl.get("baseline_ts"),
            })
        except Exception:
            pass

    archived = archive_entry(
        _watchlist_path(),
        entry_id,
        reason="user_removed",
        baseline_history=baseline_history if baseline_history else None,
    )

    if archived:
        print(f"🗑️ Archived: {question}")
    else:
        print("Error: Entry not found during archive.")
        return 1

    return 0


# ---------------------------------------------------------------------------
# cmd_run
# ---------------------------------------------------------------------------

def _write_last_run(status: str, checked: int, hits_count: int,
                    delivery: dict[str, Any] | None = None,
                    delivery_errors: list[dict[str, Any]] | None = None) -> None:
    """Write ~/.signalradar/cache/last_run.json after each run."""
    lr_path = _last_run_path()
    lr_path.parent.mkdir(parents=True, exist_ok=True)
    lr_data: dict[str, Any] = {
        "ts": _utc_now(),
        "status": status,
        "checked": checked,
        "hits": hits_count,
    }
    if delivery is not None:
        lr_data["delivery_attempted"] = delivery.get("attempted", False)
        lr_data["delivery_sent"] = delivery.get("sent", False)
        lr_data["delivery_status"] = delivery.get("status", "skipped")
        lr_data["delivery_error"] = delivery.get("error", "")
    if delivery_errors:
        lr_data["delivery_errors"] = delivery_errors
    lr_path.write_text(
        json.dumps(lr_data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def cmd_run(args: argparse.Namespace) -> int:
    wl = load_watchlist(_watchlist_path())
    entries = wl.get("entries", [])
    config = _load_config(args.config)
    primary_channel = str(config.get("delivery", {}).get("primary", {}).get("channel", "webhook") or "webhook")
    platform_announce_mode = args.output == "openclaw"
    lang = _resolve_language(config)

    # Empty watchlist handling
    if not entries:
        if args.yes:
            # --yes mode (cron/CI): no onboarding, just report empty
            if args.output == "json":
                _json_print({
                    "status": "NO_REPLY",
                    "request_id": str(uuid.uuid4()),
                    "ts": _utc_now(),
                    "hits": [],
                    "errors": [],
                    "observations": [],
                    "message": "Watchlist is empty",
                })
            elif platform_announce_mode:
                print("HEARTBEAT_OK")
            else:
                print("Watchlist is empty. Use 'signalradar.py add <url>' to add markets.")
            return 0
        elif args.output == "json":
            # Bot mode: redirect to onboarding
            _json_print({
                "status": "ONBOARD_NEEDED",
                "request_id": str(uuid.uuid4()),
                "ts": _utc_now(),
                "message": "Watchlist is empty. Run 'signalradar.py onboard --step preview --output json' to start guided setup.",
            })
            return 0
        else:
            # Interactive terminal mode: trigger onboarding
            return _onboarding(args)

    # Normal run: check each entry
    threshold_cfg = config.get("threshold", {})
    default_threshold = float(threshold_cfg.get("abs_pp", 5.0))
    per_entry_thresholds = threshold_cfg.get("per_entry_abs_pp", {})
    per_category_thresholds = threshold_cfg.get("per_category_abs_pp", {})

    baseline_dir = _baseline_dir()
    audit_log = _audit_log_path()

    request_id = str(uuid.uuid4())
    run_ts = _utc_now()
    hits: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    delivery_errors: list[dict[str, Any]] = []
    observations: list[dict[str, Any]] = []
    settled_entries: list[dict[str, Any]] = []
    digest_snapshot_rows: list[dict[str, Any]] = []
    checked = 0

    for entry in entries:
        entry_id = entry.get("entry_id", "")
        question = entry.get("question", "")
        category = entry.get("category", "default")

        # Fetch current market state
        market_id = entry_id.split(":")[1] if ":" in entry_id else ""
        if not market_id:
            err = _run_error(entry_id, "SR_VALIDATION_ERROR", "Entry ID format is invalid.")
            errors.append(err)
            digest_snapshot_rows.append(
                _snapshot_row_from_entry(entry, state="error", error=err)
            )
            observations.append(
                _build_observation(
                    entry,
                    state="error",
                    decision="ERROR",
                    error=err,
                )
            )
            continue

        current_market, fetch_error = fetch_market_current_result(market_id)
        if current_market is None:
            # API failure — check end_date as fallback for settled
            if is_settled(entry):
                settled_entries.append(entry)
                digest_snapshot_rows.append(
                    _snapshot_row_from_entry(entry, state="settled", market_status="settled")
                )
                observations.append(
                    _build_observation(
                        entry,
                        state="settled",
                        decision="SETTLED",
                    )
                )
                continue
            err = _run_error(
                entry_id,
                fetch_error.get("code", "SR_SOURCE_UNAVAILABLE") if fetch_error else "SR_SOURCE_UNAVAILABLE",
                fetch_error.get("message", "Could not fetch current market data from Polymarket API.") if fetch_error else "Could not fetch current market data from Polymarket API.",
            )
            errors.append(err)
            digest_snapshot_rows.append(
                _snapshot_row_from_entry(entry, state="error", error=err)
            )
            observations.append(
                _build_observation(
                    entry,
                    state="error",
                    decision="ERROR",
                    error=err,
                )
            )
            continue

        # Settled detection: API status priority
        if is_settled(current_market):
            settled_entries.append(entry)
            digest_snapshot_rows.append(
                _snapshot_row_from_entry(
                    entry,
                    state="settled",
                    current=float(current_market["probability"]) if isinstance(current_market.get("probability"), (int, float)) else None,
                    market_status=str(current_market.get("status", "settled") or "settled"),
                )
            )
            observations.append(
                _build_observation(
                    entry,
                    state="settled",
                    decision="SETTLED",
                    current_market=current_market,
                )
            )
            continue

        current_prob = current_market.get("probability")
        if current_prob is None:
            err = _run_error(
                entry_id,
                "SR_VALIDATION_ERROR",
                "Polymarket API returned market data without a probability value.",
            )
            errors.append(err)
            digest_snapshot_rows.append(
                _snapshot_row_from_entry(entry, state="error", error=err)
            )
            observations.append(
                _build_observation(
                    entry,
                    state="error",
                    decision="ERROR",
                    current_market=current_market,
                    error=err,
                )
            )
            continue

        # Resolve threshold: per_entry > per_category > default
        threshold = default_threshold
        if entry_id in per_entry_thresholds:
            try:
                threshold = float(per_entry_thresholds[entry_id])
            except (TypeError, ValueError):
                pass
        elif category in per_category_thresholds:
            try:
                threshold = float(per_category_thresholds[category])
            except (TypeError, ValueError):
                pass

        result = check_entry(
            entry_id=entry_id,
            question=question,
            current_prob=current_prob,
            baseline_dir=baseline_dir,
            threshold_abs_pp=threshold,
            dry_run=args.dry_run,
            audit_log_path=audit_log,
        )
        checked += 1
        observations.append(
            _build_observation(
                entry,
                state="checked",
                decision=result["decision"],
                threshold=threshold,
                current_market=current_market,
                result=result,
            )
        )
        digest_snapshot_rows.append(
            _snapshot_row_from_entry(
                entry,
                state="checked",
                current=float(current_prob),
                market_status=str(current_market.get("status", "active") or "active"),
            )
        )

        if result["decision"] == "HIT" and result["event"] is not None:
            # Attach threshold for ⚡ marker
            result["event"]["_effective_threshold"] = threshold
            hits.append(result["event"])

    # --- Multi-HIT merged delivery ---
    if hits and not args.dry_run and not (platform_announce_mode and primary_channel == "openclaw"):
        from route_delivery import human_text_multi

        # Check recent hits for 🔥 marker (same entry_id within last 30 min in audit log)
        recent_hit_ids: set[str] = set()
        try:
            if audit_log.exists():
                cutoff_dt = datetime.now(timezone.utc) - timedelta(minutes=30)
                with audit_log.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            rec = json.loads(line)
                        except (json.JSONDecodeError, ValueError):
                            continue
                        if rec.get("reason") != "HIT":
                            continue
                        rec_ts = str(rec.get("ts", ""))
                        if not rec_ts:
                            continue
                        try:
                            rec_dt = datetime.fromisoformat(rec_ts.replace("Z", "+00:00"))
                            if rec_dt >= cutoff_dt:
                                recent_hit_ids.add(str(rec.get("entry_id", "")))
                        except (ValueError, TypeError):
                            continue
        except Exception:
            pass

        hit_thresholds = [float(h.get("_effective_threshold", 0)) for h in hits]
        hit_recent = [str(h.get("entry_id", "")) in recent_hit_ids for h in hits]

        # Sort by abs(abs_pp) descending
        sorted_indices = sorted(range(len(hits)), key=lambda i: abs(float(hits[i].get("abs_pp", 0) or 0)), reverse=True)
        sorted_hits = [hits[i] for i in sorted_indices]
        sorted_thresholds = [hit_thresholds[i] for i in sorted_indices]
        sorted_recent = [hit_recent[i] for i in sorted_indices]

        if len(sorted_hits) == 1:
            # Single HIT — deliver with emoji params
            evt = sorted_hits[0]
            hit_delivery = deliver_hit(
                evt, config, dry_run=False,
                threshold=sorted_thresholds[0],
                recent_hit=sorted_recent[0],
            )
            if not hit_delivery.get("ok"):
                delivery_errors.append({
                    "entry_id": str(evt.get("entry_id", "")),
                    "error": hit_delivery.get("status", "unknown"),
                    "detail": str(hit_delivery.get("error", hit_delivery.get("attempts", ""))),
                })
        else:
            # Multi-HIT — merge into combined messages
            messages = human_text_multi(
                sorted_hits, config,
                thresholds=sorted_thresholds,
                recent_hits=sorted_recent,
            )
            # Deliver each page
            for msg in messages:
                # Build a minimal envelope and deliver via the same webhook path
                delivery = config.get("delivery", {})
                primary = delivery.get("primary", {})
                route_primary = f"{primary.get('channel', 'webhook')}:{primary.get('target', '')}"
                fallback_routes = [
                    f"{fb.get('channel', '')}:{fb.get('target', '')}"
                    for fb in delivery.get("fallback", [])
                    if isinstance(fb, dict)
                ]
                from route_delivery import attempt_delivery, utc_now as _utc
                envelope = {
                    "schema_version": "1.1.0",
                    "delivery_id": f"del:multi:{request_id}",
                    "request_id": request_id,
                    "idempotency_key": f"sr:multi:{request_id}:{hash(msg) % 100000}",
                    "severity": severity_for_event(sorted_hits[0]),
                    "route": {"primary": route_primary, "fallback": fallback_routes},
                    "human_text": msg,
                    "machine_payload": {"hit_count": len(sorted_hits)},
                    "ts": _utc().isoformat().replace("+00:00", "Z"),
                }
                routes = [route_primary] + fallback_routes
                outcome = attempt_delivery(envelope, routes, timeout_sec=8)
                if not outcome.get("ok"):
                    # Fallback: try delivering individually with emoji context
                    for fb_idx, evt in enumerate(sorted_hits):
                        fb_delivery = deliver_hit(
                            evt, config, dry_run=False,
                            threshold=sorted_thresholds[fb_idx] if fb_idx < len(sorted_thresholds) else 0.0,
                            recent_hit=sorted_recent[fb_idx] if fb_idx < len(sorted_recent) else False,
                        )
                        if not fb_delivery.get("ok"):
                            delivery_errors.append({
                                "entry_id": str(evt.get("entry_id", "")),
                                "error": fb_delivery.get("status", "unknown"),
                                "detail": str(fb_delivery.get("error", fb_delivery.get("attempts", ""))),
                            })
                    break  # Don't try remaining pages after fallback

    # Determine overall status
    if errors and not hits:
        status = "ERROR"
    elif hits:
        status = "HIT"
    else:
        status = "NO_REPLY"

    push_outcome: dict[str, Any] | None = None  # filled later by --push

    digest_report: dict[str, Any] | None = None
    digest_delivery: dict[str, Any] | None = None
    digest_failed = False
    if entries and not args.dry_run:
        digest_state = _load_digest_state()
        digest_due_info = _digest_due_status(config, digest_state)
        if digest_due_info.get("due"):
            if not _has_digest_snapshot(digest_state):
                digest_report, digest_delivery = _bootstrap_digest_report(
                    config,
                    entries,
                    snapshot_rows=digest_snapshot_rows,
                )
            else:
                digest_candidate = _finalize_digest_report(
                    _build_digest_report(config, entries, snapshot_rows=digest_snapshot_rows),
                    config,
                )
                digest_delivery = _run_digest_delivery(
                    digest_candidate,
                    config,
                    output_mode=args.output,
                    dry_run=False,
                )
                if digest_candidate.get("due") or digest_delivery.get("sent") or digest_delivery.get("status") == "ERROR":
                    digest_report = digest_candidate
                digest_failed = bool(digest_delivery.get("status") == "ERROR")

    # --push: direct push via openclaw message send (crontab driver path)
    # Must run BEFORE output so JSON payload includes delivery outcome
    if getattr(args, "push", False) and not args.dry_run:
        push_parts: list[str] = []
        if hits:
            push_parts.append(_openclaw_run_text(hits, run_ts, config))
        if digest_report and digest_delivery and digest_delivery.get("sent"):
            digest_human = digest_report.get("human_text", "")
            if digest_human:
                push_parts.append(digest_human)
        push_text = _join_openclaw_messages(*push_parts) if push_parts else ""
        if push_text and push_text != "HEARTBEAT_OK":
            push_outcome = _push_message(push_text)

    # Write last_run.json (not on dry-run), including delivery outcome
    if not args.dry_run:
        _write_last_run(status, checked, len(hits), delivery=push_outcome,
                        delivery_errors=delivery_errors)

    # Output
    if args.output == "json":
        payload: dict[str, Any] = {
            "status": status,
            "request_id": request_id,
            "ts": run_ts,
            "hits": hits,
            "errors": errors,
            "checked_count": checked,
            "settled_count": len(settled_entries),
            "observations": observations,
        }
        if digest_report is not None:
            payload["digest"] = {
                "frequency": digest_report.get("frequency"),
                "report_key": digest_report.get("report_key"),
                "due": digest_report.get("due"),
                "due_reason": digest_report.get("due_reason"),
                "generated_at": digest_report.get("generated_at"),
                "summary": digest_report.get("summary", {}),
                "delivery": digest_delivery,
            }
        if push_outcome is not None:
            payload["delivery"] = push_outcome
        _json_print(payload)
    elif platform_announce_mode:
        if primary_channel == "openclaw":
            hit_text = _openclaw_run_text(hits, run_ts, config) if hits else ""
            digest_text = digest_report.get("human_text", "") if digest_report and digest_delivery and digest_delivery.get("sent") else ""
            print(_join_openclaw_messages(hit_text, digest_text))
        else:
            print("HEARTBEAT_OK")
    else:
        if hits:
            if lang == "zh":
                print(f"检测到 {len(hits)} 个市场变化超过阈值：\n")
            else:
                print(f"Detected {len(hits)} market change(s) above your threshold:\n")
            for h in hits:
                print(f"  {h.get('question', h.get('entry_id'))}")
                if lang == "zh":
                    print(f"    {h.get('baseline')}% → {h.get('current')}%（{h.get('abs_pp')}pp）")
                    print(f"    基线已更新至 {h.get('current')}%")
                else:
                    print(f"    {h.get('baseline')}% → {h.get('current')}%  ({h.get('abs_pp')}pp)")
                    print(f"    Baseline updated to {h.get('current')}%")
                print()
        else:
            if lang == "zh":
                print(f"已检查 {checked} 个监控市场，无变化超过阈值。")
            else:
                print(f"Checked {checked} monitored market(s). No changes exceeded the threshold.")

        if errors:
            if lang == "zh":
                print(f"\n有 {len(errors)} 个市场暂时无法检查：")
            else:
                print(f"\nCould not check {len(errors)} market(s):")
            for e in errors:
                label = e.get("entry_id", "unknown")
                code = e.get("code", "SR_SOURCE_UNAVAILABLE")
                print(f"  {label}: {e.get('message', e.get('error', 'Unknown error'))} ({code})")

        if settled_entries:
            if lang == "zh":
                print(f"\n{len(settled_entries)} 个监控市场已结算，不会再触发新提醒：")
            else:
                print(f"\n{len(settled_entries)} monitored market(s) appear settled and will not trigger new alerts:")
            for e in settled_entries:
                print(f"  {e.get('question', e.get('entry_id', '?'))}")

        if digest_report is not None:
            if digest_delivery and digest_delivery.get("sent"):
                if lang == "zh":
                    print(f"\n定期报告已发送：{digest_report.get('report_key')}")
                else:
                    print(f"\nDigest sent: {digest_report.get('report_key')}")
            elif digest_failed:
                if lang == "zh":
                    print("\n定期报告发送失败。")
                else:
                    print("\nDigest delivery failed.")

    return 0 if status != "ERROR" and not digest_failed else 1


# ---------------------------------------------------------------------------
# Onboarding: JSON multi-step flow (bot mode)
# ---------------------------------------------------------------------------

def _onboard_preview(args: argparse.Namespace) -> int:
    """Step 1: Resolve preset events and return them as JSON."""
    wl = load_watchlist(_watchlist_path())
    if wl.get("entries"):
        _json_print({
            "status": "NO_REPLY",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "Watchlist already has entries. Onboarding is for first-time setup.",
        })
        return 0

    events_data: list[dict[str, Any]] = []
    for url in ONBOARDING_URLS:
        slug = parse_polymarket_url(url)
        if not slug:
            continue
        result = resolve_event(slug)
        if result["ok"]:
            markets = [m for m in result["markets"] if not is_settled(m)]
            events_data.append({
                "title": result["event_title"],
                "slug": result["slug"],
                "event_id": result["event_id"],
                "markets": [
                    {
                        "entry_id": m["entry_id"],
                        "slug": m["slug"],
                        "question": m["question"],
                        "probability": m["probability"],
                        "url": m["url"],
                        "end_date": m.get("end_date", ""),
                    }
                    for m in markets
                ],
                "url": url,
            })
        else:
            events_data.append({
                "title": slug.replace("-", " ").title(),
                "slug": slug,
                "event_id": "",
                "markets": [],
                "url": url,
                "unavailable": True,
            })

    # Check if we have any usable events (not just unavailable placeholders)
    usable_events = [ev for ev in events_data if not ev.get("unavailable") and ev.get("markets")]
    if not usable_events:
        _json_print({
            "status": "ERROR",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "Could not load any preset events. Check network connection.",
        })
        return 1

    # Write state
    _write_onboard_state({
        "step": "preview_done",
        "created_at": _utc_now(),
        "events_data": events_data,
    })

    # Build event summary for agent
    events_summary = []
    for i, ev in enumerate(events_data, 1):
        events_summary.append({
            "index": i,
            "title": ev["title"],
            "market_count": len(ev["markets"]),
            "unavailable": bool(ev.get("unavailable")),
            "url": ev["url"],
        })

    _json_print({
        "status": "ONBOARD_PREVIEW",
        "request_id": str(uuid.uuid4()),
        "ts": _utc_now(),
        "step": 1,
        "total_steps": 3,
        "events": events_summary,
        "message": f"Found {len(events_data)} events. Tell me which ones to remove (by number), or say 'keep all'.",
        "education": {
            "event": "An event is a question or topic on Polymarket containing one or more sub-markets.",
            "market": "Each market is a specific yes/no prediction question with a real-time probability (0-100%).",
        },
    })
    return 0


def _onboard_confirm(args: argparse.Namespace) -> int:
    """Step 2: Filter events by --keep, return market details."""
    state = _read_onboard_state()
    if not state or state.get("step") != "preview_done":
        _json_print({
            "status": "ERROR",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "No valid preview state. Run 'onboard --step preview' first.",
        })
        return 1

    events_data = state.get("events_data", [])
    keep_raw = getattr(args, "keep", "all").strip()

    # Parse --keep
    valid_range = set(range(1, len(events_data) + 1))
    if keep_raw.lower() == "all" or not keep_raw:
        keep_set = set(valid_range)
    else:
        keep_set = set()
        has_any_token = False
        for part in keep_raw.replace(" ", ",").split(","):
            part = part.strip()
            if not part:
                continue
            has_any_token = True
            if part.isdigit():
                keep_set.add(int(part))
        # If user provided tokens but none were valid numbers, that's an input error
        if has_any_token and not keep_set:
            _json_print({
                "status": "ERROR",
                "request_id": str(uuid.uuid4()),
                "ts": _utc_now(),
                "message": f"Invalid --keep value '{keep_raw}'. Use comma-separated event numbers (e.g. 1,2,4) or 'all'. "
                           f"Valid indices: 1-{len(events_data)}. State preserved — retry with valid indices.",
            })
            return 1
        # Check for out-of-range indices
        out_of_range = keep_set - valid_range
        if out_of_range and not (keep_set & valid_range):
            _json_print({
                "status": "ERROR",
                "request_id": str(uuid.uuid4()),
                "ts": _utc_now(),
                "message": f"All indices out of range: {sorted(out_of_range)}. Valid indices: 1-{len(events_data)}. "
                           f"State preserved — retry with valid indices.",
            })
            return 1

    kept_events = []
    kept_indices = []
    for i, ev in enumerate(events_data, 1):
        if i in keep_set and not ev.get("unavailable") and ev.get("markets"):
            kept_events.append(ev)
            kept_indices.append(i)

    if not kept_events:
        _json_print({
            "status": "NO_REPLY",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "No events selected. You can add markets individually with: signalradar.py add <url>",
        })
        _onboard_state_path().unlink(missing_ok=True)
        return 0

    # Build market list
    markets_list = []
    for ev in kept_events:
        for m in ev["markets"]:
            markets_list.append({
                "event_title": ev["title"],
                "question": m["question"],
                "probability": m["probability"],
                "category": _infer_category(ev["title"]),
                "url": m.get("url", ""),
            })

    # Update state
    state["step"] = "confirm_done"
    state["kept_indices"] = kept_indices
    _write_onboard_state(state)

    _json_print({
        "status": "ONBOARD_CONFIRM",
        "request_id": str(uuid.uuid4()),
        "ts": _utc_now(),
        "step": 2,
        "total_steps": 3,
        "kept_events": len(kept_events),
        "total_markets": len(markets_list),
        "markets": markets_list,
        "message": f"Ready to add {len(kept_events)} events ({len(markets_list)} markets). Confirm to proceed, or cancel.",
        "education": {
            "category": "Categories group related markets (AI, Crypto, Geopolitics, etc.). They are auto-assigned based on event title.",
            "baseline": "A baseline is the 'last known probability' SignalRadar records. When probability changes by more than the threshold (default 5pp), an alert is sent and the baseline updates.",
        },
    })
    return 0


def _onboard_finalize(args: argparse.Namespace) -> int:
    """Step 3: Add entries, record baselines, enable auto-monitoring."""
    state = _read_onboard_state()
    if not state or state.get("step") != "confirm_done":
        _json_print({
            "status": "ERROR",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "No confirmed selection. Run 'onboard --step preview' then '--step confirm' first.",
        })
        return 1

    events_data = state.get("events_data", [])
    kept_indices = set(state.get("kept_indices", []))
    if not kept_indices:
        _json_print({
            "status": "ERROR",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": "No events were confirmed. Run 'onboard --step confirm --keep ...' first.",
        })
        return 1

    kept_events = [ev for i, ev in enumerate(events_data, 1) if i in kept_indices]

    now = _utc_now()
    wl_path = _watchlist_path()
    baseline_dir = _baseline_dir()
    all_new_entries: list[tuple[dict[str, Any], float]] = []

    for ev in kept_events:
        category = _infer_category(ev["title"])
        for m in ev["markets"]:
            entry = {
                "entry_id": m["entry_id"],
                "slug": m["slug"],
                "event_title": ev["title"],
                "question": m["question"],
                "category": category,
                "url": m.get("url", ""),
                "end_date": m.get("end_date", ""),
                "added_at": now,
            }
            all_new_entries.append((entry, m["probability"]))

    entries_to_add = [e for e, _ in all_new_entries]
    added, skipped = add_entries(wl_path, entries_to_add)

    # Record baselines
    for entry, prob in all_new_entries:
        if entry in added:
            check_entry(
                entry_id=entry["entry_id"],
                question=entry["question"],
                current_prob=prob,
                baseline_dir=baseline_dir,
                threshold_abs_pp=5.0,
                dry_run=False,
            )

    # Persist detected language
    _persist_detected_language_if_needed(getattr(args, "config", ""))

    # Auto-monitoring
    config_override = getattr(args, "config", "")
    schedule_info = _ensure_auto_monitoring(
        interval=10,
        config_override=config_override,
        quiet=True,
    )

    # Check route readiness for background push warning
    route = _load_reply_route()
    route_ready = route is not None
    config = _load_config(config_override)
    primary_ch = str(config.get("delivery", {}).get("primary", {}).get("channel", "openclaw") or "openclaw")

    warnings: list[str] = []
    if primary_ch == "openclaw" and not route_ready:
        warnings.append(
            "Markets added and baselines recorded, but background push is NOT yet armed. "
            "No stored reply route found. Continue chatting with the bot to capture the route, "
            "then background delivery will activate automatically."
        )

    # Webhook setup guidance
    primary_target = str(config.get("delivery", {}).get("primary", {}).get("target", "") or "").strip()
    webhook_configured = (
        primary_ch == "webhook"
        and (primary_target.startswith("http://") or primary_target.startswith("https://"))
    )
    webhook_setup: dict[str, Any] = {"needed": not webhook_configured}
    if not webhook_configured:
        webhook_setup["current_channel"] = primary_ch
        webhook_setup["guide"] = (
            "To receive background alerts, configure a webhook URL. "
            "This works on any platform (OpenClaw, Claude Code, standalone) with zero LLM cost."
        )
        webhook_setup["commands"] = [
            "signalradar.py config delivery.primary.channel webhook",
            "signalradar.py config delivery.primary.target <YOUR_WEBHOOK_URL>",
        ]
        webhook_setup["examples"] = {
            "telegram": "https://api.telegram.org/bot<TOKEN>/sendMessage?chat_id=<CHAT_ID>",
            "slack": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
            "discord": "https://discord.com/api/webhooks/YOUR/WEBHOOK/URL",
        }

    # Clean up state
    _onboard_state_path().unlink(missing_ok=True)

    _json_print({
        "status": "ONBOARD_COMPLETE",
        "request_id": str(uuid.uuid4()),
        "ts": _utc_now(),
        "step": 3,
        "total_steps": 3,
        "added": len(added),
        "skipped": len(skipped),
        "schedule": schedule_info,
        "route_ready": route_ready,
        "webhook_setup": webhook_setup,
        "warnings": warnings,
        "message": f"Done! {len(added)} markets added, baselines recorded."
                   + (f" Auto-monitoring enabled (every {schedule_info.get('interval_minutes', 10)} min)." if schedule_info.get("auto_enabled") else "")
                   + (f" {len(skipped)} already in watchlist, skipped." if skipped else ""),
        "education": {
            "baseline_example": "baseline 7% -> probability rises to 15% -> alert sent -> baseline updates to 15%. Next alert requires another 5pp change from 15%.",
            "next_steps": "Use 'list' to see your monitors, 'remove N' to drop one, 'schedule' to change frequency, 'config delivery webhook <URL>' to set up push notifications.",
        },
    })
    return 0


def cmd_onboard(args: argparse.Namespace) -> int:
    """Dispatch onboard subcommand steps."""
    step = args.step
    if step == "preview":
        return _onboard_preview(args)
    elif step == "confirm":
        return _onboard_confirm(args)
    elif step == "finalize":
        return _onboard_finalize(args)
    else:
        _json_print({
            "status": "ERROR",
            "request_id": str(uuid.uuid4()),
            "ts": _utc_now(),
            "message": f"Unknown step '{step}'. Use preview, confirm, or finalize.",
        })
        return 1


# ---------------------------------------------------------------------------
# Onboarding: 3-step code-enforced flow (terminal / text mode)
# ---------------------------------------------------------------------------

def _onboarding(args: argparse.Namespace) -> int:
    """First-time setup with 6 preset events. 3-step interactive flow."""

    print("📡 Welcome to SignalRadar! Loading popular events...\n")

    # Resolve all preset URLs
    events_data: list[dict[str, Any]] = []
    for url in ONBOARDING_URLS:
        slug = parse_polymarket_url(url)
        if not slug:
            continue
        result = resolve_event(slug)
        if result["ok"]:
            markets = [m for m in result["markets"] if not is_settled(m)]
            events_data.append({
                "title": result["event_title"],
                "slug": result["slug"],
                "event_id": result["event_id"],
                "markets": markets,
                "url": url,
            })
        else:
            events_data.append({
                "title": slug.replace("-", " ").title(),
                "slug": slug,
                "event_id": "",
                "markets": [],
                "url": url,
                "unavailable": True,
            })

    if not events_data:
        print("Error: Could not load any preset events. Check network connection.")
        return 1

    # --- STEP 1: Show event titles + market counts ---
    print(f"🔢 Found {len(events_data)} events:\n")
    for i, ev in enumerate(events_data, 1):
        market_count = len(ev["markets"])
        unavail = " (unavailable)" if ev.get("unavailable") else ""
        suffix = f"({market_count} market{'s' if market_count != 1 else ''})"
        print(f"  {i}. {ev['title']}  {suffix}{unavail}")

    print()
    user_input = input("Enter numbers to REMOVE (e.g. 1,5), or press Enter to keep all: ").strip()

    # Parse removal choices
    remove_set: set[int] = set()
    if user_input:
        for part in user_input.replace(" ", ",").split(","):
            part = part.strip()
            if part.isdigit():
                remove_set.add(int(part))

    # Filter events
    kept_events = []
    for i, ev in enumerate(events_data, 1):
        if i not in remove_set and not ev.get("unavailable") and ev["markets"]:
            kept_events.append(ev)

    if not kept_events:
        print("\nNo events selected. You can add markets later with: signalradar.py add <url>")
        return 0

    # --- STEP 2: Show sub-market details, confirm ---
    total_markets = sum(len(ev["markets"]) for ev in kept_events)
    print(f"\n🔄 Adding {len(kept_events)} events ({total_markets} markets):\n")

    # Group by inferred category
    num = 0
    for ev in kept_events:
        for m in ev["markets"]:
            num += 1
            print(f"  {num}. {m['question']}  {m['probability']:.0f}%")
    print()

    answer = input(f"Confirm adding {total_markets} markets? (Y/n): ").strip().lower()
    if answer in ("n", "no"):
        print("Cancelled. You can add markets later with: signalradar.py add <url>")
        return 0

    # --- STEP 3: Add entries + show results ---
    now = _utc_now()
    wl_path = _watchlist_path()
    baseline_dir = _baseline_dir()
    all_new_entries = []

    for ev in kept_events:
        category = _infer_category(ev["title"])
        for m in ev["markets"]:
            entry = {
                "entry_id": m["entry_id"],
                "slug": m["slug"],
                "event_title": ev["title"],
                "question": m["question"],
                "category": category,
                "url": m["url"],
                "end_date": m.get("end_date", ""),
                "added_at": now,
            }
            all_new_entries.append((entry, m["probability"]))

    entries_to_add = [e for e, _ in all_new_entries]
    added, skipped = add_entries(wl_path, entries_to_add)

    # Record baselines
    for entry, prob in all_new_entries:
        if entry in added:
            check_entry(
                entry_id=entry["entry_id"],
                question=entry["question"],
                current_prob=prob,
                baseline_dir=baseline_dir,
                threshold_abs_pp=5.0,
                dry_run=False,
            )

    print(f"\n✅ Done! {len(added)} markets added, baselines recorded.")
    if skipped:
        print(f"⚠️ ({len(skipped)} already in watchlist, skipped)")
    print("📎 Remove any you don't need with: signalradar.py remove <number>")
    if added:
        _persist_detected_language_if_needed(getattr(args, "config", ""))

    print(
        "\nWhat is a baseline?\n"
        "A baseline is the \"last known probability\" SignalRadar records. When probability\n"
        "changes by more than the threshold (default 5pp) and a notification is sent,\n"
        "the baseline updates to the new value. Example:\n"
        "  baseline 7% -> probability rises to 15% -> alert sent -> baseline updates to 15%\n"
        "  Next alert requires another 5pp change from 15%."
    )

    # Auto-monitoring: enable after successful onboarding
    if added:
        _ensure_auto_monitoring(interval=10, config_override=getattr(args, "config", ""))

    return 0


def _infer_category(title: str) -> str:
    """Simple keyword-based category for onboarding events."""
    lower = title.lower()
    ai_keywords = ["gpt", "claude", "ai", "model", "llm", "openai", "anthropic", "gemini", "grok"]
    crypto_keywords = ["bitcoin", "btc", "ethereum", "eth", "crypto", "token"]
    if any(k in lower for k in ai_keywords):
        return "AI"
    if any(k in lower for k in crypto_keywords):
        return "crypto"
    return "default"


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _normalize_argv(argv: list[str]) -> list[str]:
    """Allow --yes/-y and --config before or after subcommand.

    Moves global flags that appear before the subcommand to after it,
    so argparse subparsers can parse them correctly.
    """
    commands = {"doctor", "add", "list", "show", "remove", "run", "config", "schedule", "digest"}
    # Find subcommand position
    cmd_idx = None
    for i, arg in enumerate(argv):
        if arg in commands:
            cmd_idx = i
            break
    if cmd_idx is None:
        return argv  # no subcommand found, let argparse handle the error

    # Move --yes/-y/--config from before subcommand to after
    before = argv[:cmd_idx]
    after = argv[cmd_idx:]
    relocated = []
    remaining = []
    skip_next = False
    for i, arg in enumerate(before):
        if skip_next:
            skip_next = False
            continue
        if arg in ("--yes", "-y"):
            relocated.append(arg)
        elif arg == "--config":
            relocated.append(arg)
            if i + 1 < len(before):
                relocated.append(before[i + 1])
                skip_next = True
        else:
            remaining.append(arg)
    # Insert relocated flags after the subcommand name
    return remaining + [after[0]] + relocated + after[1:]


def _emit_startup_notices(args: argparse.Namespace) -> None:
    # Capture reply route from OpenClaw foreground env if present
    _capture_reply_route()

    notices = _ensure_user_data_ready()
    if not notices:
        return
    stream = sys.stderr if getattr(args, "output", "text") in ("json", "openclaw") else sys.stdout
    for notice in notices:
        print(notice, file=stream)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=f"SignalRadar v{__version__} — Polymarket probability monitor"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # doctor
    p_doc = sub.add_parser("doctor", help="Check runtime health")
    p_doc.add_argument("--output", choices=["text", "json"], default="text")
    p_doc.add_argument("--config", default="", help="Path to config JSON")

    # add
    p_add = sub.add_parser("add", help="Add market(s) by Polymarket URL")
    p_add.add_argument("url", nargs="?", default="", help="Polymarket event URL (omit for guided setup)")
    p_add.add_argument("--category", default="", help="Category for the entries")
    p_add.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")
    p_add.add_argument("--output", choices=["text", "json"], default="text")
    p_add.add_argument("--config", default="", help="Path to config JSON")

    # list
    p_list = sub.add_parser("list", help="List watchlist entries")
    p_list.add_argument("--category", default="", help="Filter by category")
    p_list.add_argument("--archived", action="store_true", help="Show archived entries")
    p_list.add_argument("--output", choices=["json", "text"], default="text", help="Output format")

    # show
    p_show = sub.add_parser("show", help="Show current probability for one monitored market")
    p_show.add_argument("target", help="List number or keyword to match a monitored market")
    p_show.add_argument("--output", choices=["text", "json"], default="text")
    p_show.add_argument("--config", default="", help="Path to config JSON")

    # remove
    p_rm = sub.add_parser("remove", help="Remove entry by number")
    p_rm.add_argument("number", type=int, help="Entry number from 'list'")
    p_rm.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")

    # config
    p_cfg = sub.add_parser("config", help="View or change settings")
    p_cfg.add_argument("key", nargs="?", default="", help="Setting name (e.g. check_interval_minutes)")
    p_cfg.add_argument("value", nargs="?", default=None, help="New value")
    p_cfg.add_argument("--output", choices=["text", "json"], default="text")
    p_cfg.add_argument("--config", default="", help="Path to config JSON")

    # schedule
    p_sched = sub.add_parser("schedule", help="Manage auto-monitoring schedule")
    p_sched.add_argument("action", nargs="?", default="", help="Interval in minutes, or 'disable'")
    p_sched.add_argument("--driver", choices=["auto", "crontab", "openclaw"], default="auto",
                         help="Scheduling driver (default: auto, prefers OpenClaw)")
    p_sched.add_argument("--output", choices=["text", "json"], default="text")
    p_sched.add_argument("--config", default="", help="Path to config JSON")

    # digest
    p_digest = sub.add_parser("digest", help="Preview or send periodic digest")
    p_digest.add_argument("--dry-run", action="store_true", help="Preview only, do not update state")
    p_digest.add_argument("--force", action="store_true", help="Ignore schedule timing and send now")
    p_digest.add_argument("--output", choices=["text", "json", "openclaw"], default="text")
    p_digest.add_argument("--config", default="", help="Path to config JSON")

    # onboard
    p_onboard = sub.add_parser("onboard", help="First-time guided setup (multi-step, bot mode)")
    p_onboard.add_argument("--step", choices=["preview", "confirm", "finalize"], required=True,
                           help="Onboarding step to execute")
    p_onboard.add_argument("--keep", default="all",
                           help="Comma-separated event indices to keep (step confirm), or 'all'")
    p_onboard.add_argument("--output", choices=["text", "json"], default="json")
    p_onboard.add_argument("--config", default="", help="Path to config JSON")

    # run
    p_run = sub.add_parser("run", help="Check all entries for probability changes")
    p_run.add_argument("--dry-run", action="store_true", help="No side effects")
    p_run.add_argument("--output", choices=["text", "json", "openclaw"], default="text")
    p_run.add_argument("--yes", "-y", action="store_true", default=False, help="Skip confirmation")
    p_run.add_argument("--push", action="store_true", default=False,
                       help="Push results via openclaw message send (for crontab driver, zero LLM cost)")
    p_run.add_argument("--config", default="", help="Path to config JSON")

    args = parser.parse_args(_normalize_argv(sys.argv[1:]))
    _emit_startup_notices(args)

    # Dispatch
    cmd = args.command
    if cmd == "doctor":
        return cmd_doctor(args)
    elif cmd == "add":
        return cmd_add(args)
    elif cmd == "list":
        return cmd_list(args)
    elif cmd == "show":
        return cmd_show(args)
    elif cmd == "remove":
        return cmd_remove(args)
    elif cmd == "config":
        return cmd_config(args)
    elif cmd == "schedule":
        return cmd_schedule(args)
    elif cmd == "digest":
        return cmd_digest(args)
    elif cmd == "onboard":
        return cmd_onboard(args)
    elif cmd == "run":
        return cmd_run(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
