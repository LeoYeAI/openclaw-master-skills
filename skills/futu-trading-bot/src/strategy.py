#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Lightweight helpers for writing long-running strategies.

This module keeps strategy concerns small and explicit:
- in-memory state container
- trade lock wrapper
- configurable trading window checks
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, time
import threading
from typing import Any, Generator, Iterable, List, Optional


@dataclass
class StrategyState:
    position: Optional[str] = None
    entry_price: float = 0.0
    entry_time: Optional[datetime] = None
    current_price: float = 0.0
    last_trade_time: Optional[datetime] = None
    extras: dict = field(default_factory=dict)


class TradeGuard:
    def __init__(self) -> None:
        self._lock = threading.Lock()

    @contextmanager
    def locked(self) -> Generator[None, None, None]:
        with self._lock:
            yield


def in_trading_window(
    now: Optional[datetime] = None,
    start_time: str = "09:30",
    end_time: str = "16:00",
) -> bool:
    current = now or datetime.now()
    start = _parse_hhmm(start_time)
    end = _parse_hhmm(end_time)
    current_time = current.time()
    return start <= current_time < end


def trading_window_status(
    now: Optional[datetime] = None,
    start_time: str = "09:30",
    end_time: str = "16:00",
) -> dict:
    current = now or datetime.now()
    start = _parse_hhmm(start_time)
    end = _parse_hhmm(end_time)
    current_time = current.time()
    if current_time < start:
        return {"in_window": False, "reason": "before_open", "now": current.strftime("%H:%M:%S")}
    if current_time >= end:
        return {"in_window": False, "reason": "after_close", "now": current.strftime("%H:%M:%S")}
    return {"in_window": True, "reason": "open", "now": current.strftime("%H:%M:%S")}


def cooldown_elapsed(
    last_trade_time: Optional[datetime],
    cooldown_seconds: int,
    now: Optional[datetime] = None,
) -> bool:
    if last_trade_time is None:
        return True
    current = now or datetime.now()
    return (current - last_trade_time).total_seconds() >= cooldown_seconds


def holding_timeout_exceeded(
    entry_time: Optional[datetime],
    max_holding_seconds: int,
    now: Optional[datetime] = None,
) -> bool:
    if entry_time is None:
        return False
    current = now or datetime.now()
    return (current - entry_time).total_seconds() >= max_holding_seconds


def extract_callback_rows(payload: Any) -> List[dict]:
    if not isinstance(payload, dict):
        return []
    if not payload.get("success", False):
        return []
    data = payload.get("data")
    if data is None:
        return []
    if isinstance(data, list):
        return [row for row in data if isinstance(row, dict)]
    if isinstance(data, dict):
        return [data]
    return []


def filter_rows_by_code(rows: Iterable[dict], code: str) -> List[dict]:
    return [row for row in rows if row.get("code") == code]


def extract_latest_price(payload: Any, code: Optional[str] = None, field: str = "last_price") -> Optional[float]:
    rows = extract_callback_rows(payload)
    if code is not None:
        rows = filter_rows_by_code(rows, code)
    if not rows:
        return None
    value = rows[0].get(field)
    if value in (None, "", "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_hhmm(value: str) -> time:
    try:
        hour_text, minute_text = value.split(":", 1)
        hour = int(hour_text)
        minute = int(minute_text)
        return time(hour=hour, minute=minute)
    except Exception as exc:
        raise ValueError(f"Invalid HH:MM time value: {value}") from exc
