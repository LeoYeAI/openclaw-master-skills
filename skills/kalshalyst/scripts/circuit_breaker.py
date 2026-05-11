#!/usr/bin/env python3
"""
Circuit Breaker — Detect and flag contradictory Kalshi API responses.

When the API returns data that contradicts last known state, the circuit
breaker trips and prevents downstream consumers from acting on bad data.

Problem it solves:
    March 13, 2026: Kalshi API returned {"cursor": "..."} (empty portfolio)
    when 10+ positions existed. Optimus reported "no positions" to Matt
    three separate times, including in the evening briefing.

How it works:
    1. Every portfolio fetch writes a snapshot to ~/.openclaw/state/portfolio_snapshot.json
    2. Before returning data, compare against last snapshot + trade ledger
    3. If positions disappeared without matching close/expiry events, TRIP
    4. When tripped, return last known good state + warning flag
    5. Auto-recover when API returns consistent data again

Usage:
    from circuit_breaker import check_portfolio, PortfolioState

    state = check_portfolio(api_positions, api_balance)

    if state.is_tripped:
        # API is returning bad data — use last known state
        print(f"WARNING: {state.trip_reason}")
        positions = state.last_known_positions
    else:
        # API data looks consistent — use it
        positions = state.positions
"""

import json
import logging
from datetime import datetime, timezone
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from trade_ledger import get_open_positions as ledger_positions

logger = logging.getLogger("circuit_breaker")

SNAPSHOT_PATH = Path.home() / ".openclaw" / "state" / "portfolio_snapshot.json"
BREAKER_STATE_PATH = Path.home() / ".openclaw" / "state" / "circuit_breaker.json"

# How many positions can vanish before we trip
_VANISH_THRESHOLD = 2

# How much USD can vanish before we trip
_USD_VANISH_THRESHOLD = 20.0


@dataclass
class PortfolioState:
    """Result of a circuit breaker check."""
    positions: dict = field(default_factory=dict)
    balance: float = 0.0
    is_tripped: bool = False
    trip_reason: str = ""
    last_known_positions: dict = field(default_factory=dict)
    last_known_balance: float = 0.0
    confidence: str = "high"  # high | degraded | stale


def _read_snapshot() -> dict:
    """Read last saved portfolio snapshot."""
    if not SNAPSHOT_PATH.exists():
        return {}
    try:
        with open(SNAPSHOT_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {}


def _write_snapshot(positions: dict, balance: float, position_count: int):
    """Write portfolio snapshot for future comparison."""
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "positions": positions,
        "balance": balance,
        "position_count": position_count,
    }
    with open(SNAPSHOT_PATH, "w") as f:
        json.dump(snapshot, f, indent=2)


def _read_breaker_state() -> dict:
    """Read circuit breaker state (trip count, last trip time)."""
    if not BREAKER_STATE_PATH.exists():
        return {"tripped": False, "trip_count": 0, "last_trip": None}
    try:
        with open(BREAKER_STATE_PATH) as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"tripped": False, "trip_count": 0, "last_trip": None}


def _write_breaker_state(state: dict):
    """Write circuit breaker state."""
    BREAKER_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(BREAKER_STATE_PATH, "w") as f:
        json.dump(state, f, indent=2)


def check_portfolio(
    api_positions: dict,
    api_balance: float,
    api_position_count: int = 0,
) -> PortfolioState:
    """Check API response against last known state and trade ledger.

    Args:
        api_positions: Positions returned by Kalshi API {ticker: {...}}
        api_balance: Cash balance returned by Kalshi API (USD)
        api_position_count: Number of positions API returned

    Returns:
        PortfolioState with is_tripped=True if data looks wrong.
    """
    snapshot = _read_snapshot()
    ledger_open = ledger_positions()
    breaker = _read_breaker_state()

    last_positions = snapshot.get("positions", {})
    last_count = snapshot.get("position_count", 0)
    last_balance = snapshot.get("balance", 0.0)

    result = PortfolioState(
        positions=api_positions,
        balance=api_balance,
        last_known_positions=last_positions,
        last_known_balance=last_balance,
    )

    # ── Check 1: Positions vanished ──────────────────────────────────────
    # If we had N positions last time and now have 0 (or way fewer),
    # AND the trade ledger says positions should be open, trip.
    if last_count > 0 and api_position_count == 0 and len(ledger_open) > 0:
        result.is_tripped = True
        result.trip_reason = (
            f"API returned 0 positions but ledger shows {len(ledger_open)} open "
            f"(last snapshot had {last_count}). API is likely broken."
        )
        result.confidence = "stale"
        logger.warning(f"CIRCUIT BREAKER TRIPPED: {result.trip_reason}")
        _trip(breaker, result.trip_reason)
        return result

    # ── Check 2: Massive position drop ───────────────────────────────────
    # If position count dropped by more than threshold without matching closes
    if last_count > _VANISH_THRESHOLD and api_position_count < last_count - _VANISH_THRESHOLD:
        vanished = last_count - api_position_count
        result.is_tripped = True
        result.trip_reason = (
            f"{vanished} positions vanished since last check "
            f"({last_count} → {api_position_count}). "
            f"Ledger shows {len(ledger_open)} should be open."
        )
        result.confidence = "degraded"
        logger.warning(f"CIRCUIT BREAKER TRIPPED: {result.trip_reason}")
        _trip(breaker, result.trip_reason)
        return result

    # ── Check 3: Ledger-API mismatch ─────────────────────────────────────
    # If ledger says we have positions the API doesn't show
    if ledger_open and api_position_count > 0:
        missing_from_api = set(ledger_open.keys()) - set(api_positions.keys())
        if len(missing_from_api) > _VANISH_THRESHOLD:
            result.is_tripped = True
            result.trip_reason = (
                f"Ledger has {len(missing_from_api)} positions not in API response: "
                f"{', '.join(list(missing_from_api)[:5])}. "
                f"API may be returning partial data."
            )
            result.confidence = "degraded"
            logger.warning(f"CIRCUIT BREAKER TRIPPED: {result.trip_reason}")
            _trip(breaker, result.trip_reason)
            return result

    # ── All checks passed — data looks consistent ────────────────────────
    if breaker.get("tripped"):
        logger.info("Circuit breaker recovered — API data consistent again")
        breaker["tripped"] = False
        _write_breaker_state(breaker)

    # Save this as the new known-good state
    _write_snapshot(api_positions, api_balance, api_position_count)
    result.confidence = "high"
    return result


def _trip(breaker: dict, reason: str):
    """Record a circuit breaker trip."""
    breaker["tripped"] = True
    breaker["trip_count"] = breaker.get("trip_count", 0) + 1
    breaker["last_trip"] = datetime.now(timezone.utc).isoformat()
    breaker["last_reason"] = reason
    _write_breaker_state(breaker)


def is_tripped() -> bool:
    """Quick check: is the circuit breaker currently tripped?"""
    state = _read_breaker_state()
    return state.get("tripped", False)


def get_last_known_portfolio() -> dict:
    """Get the last known-good portfolio snapshot.

    Use this when the circuit breaker is tripped and you need
    something to show the user instead of wrong data.
    """
    snapshot = _read_snapshot()
    return {
        "positions": snapshot.get("positions", {}),
        "balance": snapshot.get("balance", 0.0),
        "position_count": snapshot.get("position_count", 0),
        "snapshot_time": snapshot.get("timestamp", "unknown"),
        "source": "last_known_good",
    }


def get_status() -> dict:
    """Get the full circuit breaker status for diagnostics."""
    breaker = _read_breaker_state()
    snapshot = _read_snapshot()
    ledger_open = ledger_positions()

    return {
        "tripped": breaker.get("tripped", False),
        "trip_count": breaker.get("trip_count", 0),
        "last_trip": breaker.get("last_trip"),
        "last_reason": breaker.get("last_reason", ""),
        "snapshot_time": snapshot.get("timestamp", "none"),
        "snapshot_position_count": snapshot.get("position_count", 0),
        "ledger_open_count": len(ledger_open),
        "ledger_tickers": list(ledger_open.keys()),
    }
