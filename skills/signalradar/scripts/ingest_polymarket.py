#!/usr/bin/env python3
"""Normalize Polymarket market data into SignalRadar snapshot format.

Usage:
  python3 scripts/ingest_polymarket.py --input raw_markets.json --output cache/snapshots/polymarket.json
"""

from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import datetime, timezone
from typing import Any

from error_utils import emit_error


def slugify(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r"[^a-z0-9]+", "-", lowered)
    return lowered.strip("-") or "unknown"


def as_percent(value: Any) -> float | None:
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


def normalize_item(item: dict[str, Any]) -> dict[str, Any] | None:
    market_id = first_non_null(item, ["id", "market_id", "marketId"])
    question = first_non_null(item, ["question", "title", "name"])
    if market_id is None or not question:
        return None

    probability = as_percent(
        first_non_null(
            item,
            [
                "probability",
                "current",
                "price",
                "lastPrice",
                "yesPrice",
            ],
        )
    )
    if probability is None:
        outcome_prices = item.get("outcomePrices")
        if isinstance(outcome_prices, str) and outcome_prices.startswith("["):
            try:
                outcome_prices = json.loads(outcome_prices)
            except (json.JSONDecodeError, ValueError):
                outcome_prices = None
        if isinstance(outcome_prices, list) and outcome_prices:
            probability = as_percent(outcome_prices[0])
    if probability is None:
        return None

    event_id = str(first_non_null(item, ["event_id", "eventId", "event", "parentEvent", "id"]) or market_id)
    status = str(first_non_null(item, ["status", "state"]) or "active")
    volume_24h = first_non_null(item, ["volume_24h", "volume24h", "volume", "liquidity"])
    end_date = first_non_null(item, ["endDate", "end_date", "closeTime"])

    return {
        "source": "polymarket",
        "market_id": str(market_id),
        "event_id": str(event_id),
        "slug": slugify(str(question)),
        "question": str(question),
        "probability": probability,
        "volume_24h": float(volume_24h) if volume_24h is not None else None,
        "status": status.lower(),
        "end_date": end_date,
        "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }


def fetch_json(url: str, timeout: int) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "signalradar-skill/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def load_input(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif args.url:
        payload = fetch_json(args.url, args.timeout)
    else:
        raise ValueError("either --input or --url is required")

    if isinstance(payload, dict):
        for key in ["markets", "data", "items"]:
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break
    if not isinstance(payload, list):
        raise ValueError("input payload must be a list or an object containing list data")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize Polymarket feed")
    parser.add_argument("--input", help="Path to raw JSON input")
    parser.add_argument("--url", help="Optional Polymarket URL to fetch")
    parser.add_argument("--timeout", type=int, default=15, help="HTTP timeout seconds")
    parser.add_argument("--output", required=True, help="Normalized snapshots JSON path")
    args = parser.parse_args()

    try:
        raw_items = load_input(args)
        normalized: list[dict[str, Any]] = []
        for item in raw_items:
            if not isinstance(item, dict):
                continue
            row = normalize_item(item)
            if row is not None:
                normalized.append(row)

        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(normalized, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print(f"wrote {len(normalized)} snapshots -> {args.output}")
        return 0
    except Exception as exc:  # noqa: BLE001
        return emit_error(
            "SR_SOURCE_UNAVAILABLE",
            f"ingest failed: {exc}",
            retryable=True,
            details={"script": "ingest_polymarket.py"},
        )


if __name__ == "__main__":
    raise SystemExit(main())
