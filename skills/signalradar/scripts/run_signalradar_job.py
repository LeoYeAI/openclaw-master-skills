#!/usr/bin/env python3
"""SignalRadar market normalization helpers.

v0.8.0 note:
- orchestration lives in signalradar.py
- this module remains as a compatibility helper for tests and older imports
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from typing import Any


def as_percent(value: Any) -> float | None:
    """Convert probability value to 0-100 percentage."""
    if value is None:
        return None
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if v <= 1.0:
        return round(v * 100.0, 6)
    return round(v, 6)


def first_non_null(item: dict[str, Any], keys: list[str]) -> Any:
    for key in keys:
        if key in item and item[key] is not None:
            return item[key]
    return None


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "unknown"


def extract_probability(item: dict[str, Any]) -> float | None:
    """Extract Yes outcome probability as percentage (0-100)."""
    val = first_non_null(
        item,
        ["probability", "current", "price", "lastPrice", "yesPrice", "lastTradePrice"],
    )
    p = as_percent(val)
    if p is not None:
        return p
    outcome_prices = item.get("outcomePrices")
    if isinstance(outcome_prices, str) and outcome_prices.startswith("["):
        try:
            outcome_prices = json.loads(outcome_prices)
        except (json.JSONDecodeError, ValueError):
            outcome_prices = None
    if isinstance(outcome_prices, list) and outcome_prices:
        return as_percent(outcome_prices[0])
    return None


def normalize_item(item: dict[str, Any]) -> dict[str, Any] | None:
    """Normalize a raw Polymarket market item to standard format."""
    market_id = first_non_null(item, ["id", "market_id", "marketId", "conditionId"])
    question = first_non_null(item, ["question", "title", "name"])
    if market_id is None or not question:
        return None
    probability = extract_probability(item)
    if probability is None:
        return None

    event_id = str(
        first_non_null(item, ["event_id", "eventId", "event", "parentEvent", "eventSlug", "id"]) or market_id
    )
    status = str(first_non_null(item, ["status", "state"]) or "active")
    if "active" in item and item.get("active") is False:
        status = "inactive"
    end_date = first_non_null(item, ["endDate", "end_date", "closeTime", "endDateIso"])

    return {
        "source": "polymarket",
        "market_id": str(market_id),
        "event_id": str(event_id),
        "slug": str(item.get("slug") or slugify(str(question))),
        "question": str(question),
        "probability": probability,
        "status": status.lower(),
        "end_date": end_date,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
