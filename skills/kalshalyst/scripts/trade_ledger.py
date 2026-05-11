#!/usr/bin/env python3
"""
Trade Ledger — Append-only local record of all trade executions.

Every trade auto_trader executes gets written here BEFORE the API call returns.
When the Kalshi API is broken or returning empty data, any skill can read this
ledger to know what positions SHOULD exist.

File: ~/.openclaw/state/trade_ledger.json
Format: JSON array of trade records, newest last.

Usage:
    from trade_ledger import record_trade, get_open_positions, get_ledger

    # Record a trade (call from auto_trader after execution)
    record_trade(
        ticker="KXSHUTDOWN-43D",
        side="yes",
        contracts=50,
        price_cents=58,
        cost_usd=29.00,
        edge_pct=8.5,
        confidence=0.72,
        order_id="abc-123",
        dry_run=False,
    )

    # Get what the ledger thinks is open (for when API is broken)
    positions = get_open_positions()
    # => {"KXSHUTDOWN-43D": {"side": "yes", "contracts": 50, "cost_usd": 29.00, ...}}

    # Mark a position as closed (resolved, sold, or expired)
    close_position("KXSHUTDOWN-43D", reason="resolved", pnl=21.00)
"""

import fcntl
import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger("trade_ledger")

LEDGER_PATH = Path.home() / ".openclaw" / "state" / "trade_ledger.json"


def _ensure_ledger():
    """Create ledger file if it doesn't exist."""
    LEDGER_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LEDGER_PATH.exists():
        with open(LEDGER_PATH, "w") as f:
            json.dump([], f)


def _read_ledger() -> list:
    """Read the full ledger. Returns empty list if missing or corrupt."""
    _ensure_ledger()
    try:
        with open(LEDGER_PATH, "r") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            try:
                data = json.load(f)
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
        if not isinstance(data, list):
            logger.warning(f"Ledger corrupt (not a list), resetting")
            return []
        return data
    except (json.JSONDecodeError, FileNotFoundError) as e:
        logger.warning(f"Ledger read error: {e}")
        return []


def _write_ledger(data: list):
    """Write the full ledger atomically with file locking."""
    _ensure_ledger()
    tmp_path = LEDGER_PATH.with_suffix(".tmp")
    with open(tmp_path, "w") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        try:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        finally:
            fcntl.flock(f, fcntl.LOCK_UN)
    os.rename(tmp_path, LEDGER_PATH)


def record_trade(
    ticker: str,
    side: str,
    contracts: int,
    price_cents: int,
    cost_usd: float,
    edge_pct: float = 0.0,
    confidence: float = 0.0,
    order_id: str = "",
    order_result: str = "",
    dry_run: bool = False,
    title: str = "",
) -> dict:
    """Record a trade execution to the ledger.

    Call this from auto_trader immediately after a successful order placement.
    Returns the trade record that was written.
    """
    record = {
        "id": str(uuid.uuid4()),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "ticker": ticker,
        "side": side,
        "contracts": contracts,
        "price_cents": price_cents,
        "cost_usd": round(cost_usd, 2),
        "edge_pct": round(edge_pct, 2),
        "confidence": round(confidence, 3),
        "order_id": order_id,
        "title": title[:80],
        "dry_run": dry_run,
        "status": "open",  # open | closed | expired | cancelled
        "confirmation_status": "dry_run" if dry_run else "pending",  # pending | confirmed | unconfirmed | dry_run
        "confirmation_checked_at": None,
        "confirmation_details": "",
        "close_timestamp": None,
        "close_reason": None,
        "pnl": None,
    }

    ledger = _read_ledger()
    ledger.append(record)
    _write_ledger(ledger)

    logger.info(f"Ledger: recorded {'[DRY RUN] ' if dry_run else ''}"
                f"{side.upper()} {contracts}x {ticker} @ {price_cents}¢ (${cost_usd:.2f})")
    return record


def update_trade_confirmation(
    trade_id: str,
    *,
    confirmation_status: str,
    details: str = "",
) -> bool:
    """Update a recorded trade with reconciliation status."""
    if confirmation_status not in {"pending", "confirmed", "unconfirmed", "dry_run"}:
        raise ValueError(f"Unknown confirmation status: {confirmation_status}")

    ledger = _read_ledger()
    found = False

    for entry in ledger:
        if entry.get("id") != trade_id:
            continue
        entry["confirmation_status"] = confirmation_status
        entry["confirmation_checked_at"] = datetime.now(timezone.utc).isoformat()
        entry["confirmation_details"] = details[:240]
        found = True
        break

    if found:
        _write_ledger(ledger)
        logger.info("Ledger: trade %s marked %s", trade_id, confirmation_status)
    else:
        logger.warning("Ledger: trade id not found for confirmation update: %s", trade_id)
    return found


def close_position(
    ticker: str,
    reason: str = "resolved",
    pnl: Optional[float] = None,
) -> bool:
    """Mark a position as closed in the ledger.

    Args:
        ticker: The market ticker to close
        reason: Why it closed (resolved, sold, expired, cancelled)
        pnl: Profit/loss in USD (positive = profit)

    Returns:
        True if a matching open position was found and closed, False otherwise.
    """
    ledger = _read_ledger()
    found = False

    # Close the most recent open entry for this ticker
    for i in range(len(ledger) - 1, -1, -1):
        entry = ledger[i]
        if entry.get("ticker") == ticker and entry.get("status") == "open":
            entry["status"] = "closed"
            entry["close_timestamp"] = datetime.now(timezone.utc).isoformat()
            entry["close_reason"] = reason
            entry["pnl"] = round(pnl, 2) if pnl is not None else None
            found = True
            logger.info(f"Ledger: closed {ticker} — {reason}"
                        f"{f' (P&L: ${pnl:+.2f})' if pnl is not None else ''}")
            break

    if found:
        _write_ledger(ledger)
    else:
        logger.warning(f"Ledger: no open position found for {ticker}")
    return found


def get_open_positions() -> dict:
    """Get all positions the ledger thinks are currently open.

    Returns:
        Dict of {ticker: {side, contracts, cost_usd, price_cents, timestamp, ...}}
        If multiple entries exist for the same ticker, sums contracts.
    """
    ledger = _read_ledger()
    positions = {}

    for entry in ledger:
        if entry.get("status") != "open" or entry.get("dry_run", False):
            continue

        ticker = entry.get("ticker", "")
        if ticker in positions:
            # Same ticker, same side: sum contracts
            positions[ticker]["contracts"] += entry.get("contracts", 0)
            positions[ticker]["cost_usd"] += entry.get("cost_usd", 0)
        else:
            positions[ticker] = {
                "side": entry.get("side", "?"),
                "contracts": entry.get("contracts", 0),
                "cost_usd": entry.get("cost_usd", 0),
                "price_cents": entry.get("price_cents", 0),
                "edge_pct": entry.get("edge_pct", 0),
                "confidence": entry.get("confidence", 0),
                "timestamp": entry.get("timestamp", ""),
                "title": entry.get("title", ""),
                "order_id": entry.get("order_id", ""),
            }

    return positions


def get_ledger() -> list:
    """Get the full trade ledger."""
    return _read_ledger()


def get_summary() -> dict:
    """Get a summary of the ledger state.

    Returns:
        {
            "total_trades": int,
            "open_positions": int,
            "closed_positions": int,
            "total_deployed_usd": float,
            "total_realized_pnl": float,
            "positions": {ticker: {...}},
        }
    """
    ledger = _read_ledger()

    open_count = 0
    closed_count = 0
    total_deployed = 0.0
    total_pnl = 0.0

    for entry in ledger:
        if entry.get("dry_run", False):
            continue
        if entry.get("status") == "open":
            open_count += 1
            total_deployed += entry.get("cost_usd", 0)
        elif entry.get("status") == "closed":
            closed_count += 1
            if entry.get("pnl") is not None:
                total_pnl += entry["pnl"]

    return {
        "total_trades": len([e for e in ledger if not e.get("dry_run")]),
        "open_positions": open_count,
        "closed_positions": closed_count,
        "total_deployed_usd": round(total_deployed, 2),
        "total_realized_pnl": round(total_pnl, 2),
        "positions": get_open_positions(),
    }


def get_monthly_scorecard(now: Optional[datetime] = None) -> dict:
    """Summarize current-month trading performance from the ledger.

    Returns fail-loud metrics: values are present only when the ledger has
    enough confirmed/closed information to support them.
    """
    now = now or datetime.now(timezone.utc)
    month_start = datetime(now.year, now.month, 1, tzinfo=timezone.utc)

    ledger = _read_ledger()
    month_entries = []
    for entry in ledger:
        ts = entry.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        except (TypeError, ValueError):
            continue
        if dt >= month_start and not entry.get("dry_run", False):
            month_entries.append(entry)

    closed_entries = [
        entry for entry in month_entries
        if entry.get("status") == "closed" and entry.get("pnl") is not None
    ]
    confirmed_entries = [
        entry for entry in month_entries
        if entry.get("confirmation_status") == "confirmed"
    ]

    wins = sum(1 for entry in closed_entries if float(entry.get("pnl", 0)) > 0)
    losses = sum(1 for entry in closed_entries if float(entry.get("pnl", 0)) < 0)
    total_pnl = round(sum(float(entry.get("pnl", 0)) for entry in closed_entries), 2)

    best_trade = None
    worst_trade = None
    if closed_entries:
        best_trade = max(closed_entries, key=lambda entry: float(entry.get("pnl", 0)))
        worst_trade = min(closed_entries, key=lambda entry: float(entry.get("pnl", 0)))

    accuracy_sample = wins + losses
    edge_accuracy = None
    if accuracy_sample > 0:
        edge_accuracy = round((wins / accuracy_sample) * 100, 1)

    return {
        "month": month_start.strftime("%Y-%m"),
        "entries_this_month": len(month_entries),
        "confirmed_entries": len(confirmed_entries),
        "resolved_entries": len(closed_entries),
        "wins": wins,
        "losses": losses,
        "total_pnl": total_pnl,
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "edge_accuracy_pct": edge_accuracy,
    }
