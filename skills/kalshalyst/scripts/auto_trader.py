#!/usr/bin/env python3
"""
Auto-Trader — Autonomous Kalshi trading orchestrator.

Bridges kalshalyst edge scanner → Kelly sizing → order execution with
six layers of safety controls. Designed for hands-off operation via launchd.

Usage:
    python3 auto_trader.py [--dry-run] [--force]

Config: ~/.openclaw/auto_trader_config.json
Logs:   ~/.openclaw/logs/auto_trader_state.jsonl
Kill:   Set "enabled": false in config, or:
        sed -i '' 's/"enabled": true/"enabled": false/' ~/.openclaw/auto_trader_config.json
"""

import argparse
import fcntl
import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

from trade_ledger import get_summary as get_ledger_summary
from trade_ledger import record_trade, update_trade_confirmation

# ── Logging ───────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] AutoTrader: %(message)s",
)
logger = logging.getLogger("auto_trader")


# ── Slack Notifications ────────────────────────────────────────────────────────
def _notify_slack(message: str) -> None:
    """Send notification via Slack webhook. Silent on failure."""
    import yaml as _yaml
    webhook_url = os.environ.get("OPENCLAW_SLACK_WEBHOOK", "")
    if not webhook_url:
        try:
            cfg_path = Path.home() / ".openclaw" / "config.yaml"
            if cfg_path.exists():
                with open(cfg_path) as f:
                    cfg = _yaml.safe_load(f) or {}
                webhook_url = cfg.get("slack_webhook_url", "")
        except Exception:
            pass
    if not webhook_url:
        return
    try:
        data = json.dumps({"text": message}).encode("utf-8")
        req = urllib.request.Request(webhook_url, data=data, headers={"Content-Type": "application/json"})
        urllib.request.urlopen(req, timeout=10)
    except Exception:
        pass


# ── API Schema Normalization ────────────────────────────────────────────────
def _normalize_market(m: dict) -> dict:
    """Normalize Kalshi API v3 dollar-string fields to integer cents.

    Kalshi API changed field names (e.g., yes_bid → yes_bid_dollars).
    This helper converts new dollar-string fields to integer cents the rest
    of the code expects. Only normalizes if new fields are present and old ones
    are missing (safe to call on already-normalized dicts).
    """
    def _dollars_to_cents(val):
        """Convert dollar string like '0.4500' to integer cents like 45."""
        if val is None:
            return 0
        if isinstance(val, (int, float)):
            return int(val) if val < 10 else int(val)  # already cents or needs conversion
        try:
            return int(round(float(val) * 100))
        except (ValueError, TypeError):
            return 0

    def _fp_to_int(val):
        """Convert float-point string like '1234.00' to integer."""
        if val is None:
            return 0
        if isinstance(val, int):
            return val
        try:
            return int(round(float(val)))
        except (ValueError, TypeError):
            return 0

    # Only normalize if new fields are present and old ones are missing
    if m.get("yes_bid") is None and "yes_bid_dollars" in m:
        m["yes_bid"] = _dollars_to_cents(m.get("yes_bid_dollars"))
        m["yes_ask"] = _dollars_to_cents(m.get("yes_ask_dollars"))
        m["no_bid"] = _dollars_to_cents(m.get("no_bid_dollars"))
        m["no_ask"] = _dollars_to_cents(m.get("no_ask_dollars"))
        m["last_price"] = _dollars_to_cents(m.get("last_price_dollars"))
        m["yes_price"] = m.get("yes_price") or _dollars_to_cents(m.get("yes_bid_dollars"))  # approximate
        m["previous_yes_bid"] = _dollars_to_cents(m.get("previous_yes_bid_dollars"))
        m["previous_yes_ask"] = _dollars_to_cents(m.get("previous_yes_ask_dollars"))
        m["previous_price"] = _dollars_to_cents(m.get("previous_price_dollars"))
        m["volume"] = _fp_to_int(m.get("volume_fp"))
        m["volume_24h"] = _fp_to_int(m.get("volume_24h_fp"))
        m["open_interest"] = _fp_to_int(m.get("open_interest_fp"))
        m["liquidity"] = _dollars_to_cents(m.get("liquidity_dollars"))
        m["notional_value"] = _dollars_to_cents(m.get("notional_value_dollars"))
    return m

# ── Paths ─────────────────────────────────────────────────────────────────
CONFIG_PATH = Path.home() / ".openclaw" / "auto_trader_config.json"
STATE_LOG = Path.home() / ".openclaw" / "logs" / "auto_trader_state.jsonl"
TRADE_LOG = Path.home() / ".openclaw" / "logs" / "trades.jsonl"

# ── Sibling imports (add script dir to path) ──────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import from kalshi-command-center (sibling skill)
KALSHI_CMD_DIR = SCRIPT_DIR.parent.parent / "kalshi-command-center" / "scripts"
sys.path.insert(0, str(KALSHI_CMD_DIR))


# ── Config ────────────────────────────────────────────────────────────────

def load_config() -> dict:
    """Load auto-trader config. Returns empty dict if missing."""
    try:
        if CONFIG_PATH.exists():
            cfg = json.loads(CONFIG_PATH.read_text())
            logger.info(f"Config loaded (enabled={cfg.get('enabled', False)})")
            return cfg
    except Exception as e:
        logger.error(f"Failed to load config: {e}")
    return {}


def _load_exit_rules() -> dict:
    """Load exit strategy rules from prompt-lab. Returns empty dict if not found."""
    for path in [Path.home() / "prompt-lab" / "exit_rules.md", Path.home() / ".openclaw" / "exit_rules.md"]:
        if path.exists():
            try:
                text = path.read_text()
                rules = {}
                for line in text.split("\n"):
                    line = line.strip()
                    if ":" in line and not line.startswith("#") and not line.startswith("-"):
                        key, _, val = line.partition(":")
                        key = key.strip().lower().replace(" ", "_")
                        val = val.strip()
                        try:
                            rules[key] = float(val)
                        except ValueError:
                            rules[key] = val
                if rules:
                    logger.info(f"Exit rules loaded from {path} ({len(rules)} params)")
                    return rules
            except Exception as e:
                logger.warning(f"Failed to load exit rules from {path}: {e}")
    logger.info("No exit rules found — position lifecycle management disabled")
    return {}


# ── State Logging ─────────────────────────────────────────────────────────

def _log_state(event: str, data: dict):
    """Append to auto_trader_state.jsonl with file locking for atomic writes."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **data,
    }
    try:
        STATE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_LOG, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.warning(f"Failed to write state log: {e}")


def _ledger_context() -> dict:
    """Return what the local ledger still knows when APIs are uncertain."""
    try:
        summary = get_ledger_summary()
    except Exception as e:
        return {
            "ledger_known_positions": 0,
            "ledger_deployed_usd": 0.0,
            "ledger_tickers": [],
            "ledger_error": str(e)[:200],
        }

    return {
        "ledger_known_positions": summary.get("open_positions", 0),
        "ledger_deployed_usd": summary.get("total_deployed_usd", 0.0),
        "ledger_tickers": sorted(summary.get("positions", {}).keys()),
    }


def _fail_loud_result(reason: str, edges: list, *, known: str = "") -> dict:
    """Return an explicit unknown-state summary instead of fabricated certainty."""
    message = "I don't know"
    if known:
        message += f" — {known}"
    return {
        "trades_executed": 0,
        "trades_skipped": len(edges),
        "reason": reason,
        "message": message,
        **_ledger_context(),
    }


def _reconcile_trade_with_portfolio(
    client,
    ticker: str,
    side: str,
    contracts: int,
    before_positions: dict,
    wait_seconds: float,
) -> tuple[bool, str, dict]:
    """Wait, re-query the portfolio API, and verify the position exists."""
    if wait_seconds > 0:
        time.sleep(wait_seconds)

    try:
        after_positions = get_current_positions(client)
    except RuntimeError as e:
        return False, f"I don't know — could not re-fetch positions after execution: {e}", {}

    before_qty = before_positions.get(ticker, {}).get("position", 0)
    after = after_positions.get(ticker)
    after_qty = after.get("position", 0) if after else 0
    expected_delta = contracts if side == "yes" else -contracts
    observed_delta = after_qty - before_qty

    if side == "yes" and observed_delta >= contracts:
        return True, f"confirmed via portfolio API ({before_qty} -> {after_qty})", after_positions
    if side == "no" and observed_delta <= -contracts:
        return True, f"confirmed via portfolio API ({before_qty} -> {after_qty})", after_positions

    return False, (
        "I don't know — order was submitted but the expected position delta "
        f"never appeared ({before_qty} -> {after_qty})"
    ), after_positions


# ── Safety Checks ─────────────────────────────────────────────────────────

def get_current_positions(client) -> dict:
    """Fetch current Kalshi positions. Returns {ticker: {position, side}}.

    Raises on ALL errors (auth, network, parse) so callers know positions
    fetch failed vs. genuinely having zero positions. Swallowing errors here
    causes duplicate position opening when the caller assumes zero positions.
    """
    positions = {}
    try:
        resp = client._portfolio_api.get_positions_without_preload_content(limit=100)
        raw = resp.read()
        # Check for HTTP-level auth errors before parsing
        if hasattr(resp, 'status') and resp.status in (401, 403):
            raise RuntimeError(f"Kalshi auth failed (HTTP {resp.status}). Check api_key_id in config.yaml.")
        data = json.loads(raw)
        # Schema validation — fail loud on unknown response shape
        _KNOWN_POS_KEYS = ("event_positions", "positions", "market_positions")
        if not any(k in data for k in _KNOWN_POS_KEYS):
            raise RuntimeError(
                f"SCHEMA DRIFT: Kalshi API response has none of expected position keys. "
                f"Got: {sorted(data.keys())}. Expected one of: {_KNOWN_POS_KEYS}. "
                f"Kalshi changed their API — fix field names in auto_trader.py."
            )
        # v3 API returns event_positions, SDK uses positions, v2 returns market_positions
        positions_list = data.get("event_positions") or data.get("positions") or data.get("market_positions", [])
        if not isinstance(positions_list, list):
            raise RuntimeError(f"Unexpected positions response schema: got {type(positions_list).__name__}")
        for p in positions_list:
            ticker = p.get("ticker", "")
            try:
                v = p.get("position_fp") or p.get("position", 0)
                qty = int(float(v))
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed position entry for {ticker}: {e}")
                continue
            if qty != 0:
                positions[ticker] = {
                    "position": qty,
                    "side": "yes" if qty > 0 else "no",
                    "abs_qty": abs(qty),
                }
    except (RuntimeError, PermissionError) as auth_err:
        logger.error(f"AUTH ERROR fetching positions: {auth_err}")
        raise
    except Exception as e:
        err_str = str(e).lower()
        if "401" in err_str or "403" in err_str or "unauthorized" in err_str or "forbidden" in err_str:
            logger.error(f"AUTH ERROR fetching positions: {e}")
            raise RuntimeError(f"Kalshi auth failed: {e}") from e
        # CRITICAL: Do NOT swallow network/parse errors — raise so caller
        # knows we failed to fetch positions (vs. genuinely having zero).
        logger.error(f"Failed to fetch positions: {e}")
        raise RuntimeError(f"Cannot fetch positions (network/parse error): {e}") from e
    return positions


def get_balance(client) -> float:
    """Get available cash balance in USD.

    Raises on failure — callers must know if balance is unknown vs. zero.
    """
    try:
        balance_resp = client._portfolio_api.get_balance()
        return balance_resp.balance / 100.0
    except Exception as e:
        logger.error(f"Failed to fetch balance: {e}")
        raise RuntimeError(f"Cannot fetch balance: {e}") from e


def get_daily_pnl() -> float:
    """Sum realized P&L from trade log for today (UTC). Negative = loss."""
    today = datetime.now(timezone.utc).date()
    daily_pnl = 0.0
    try:
        if not TRADE_LOG.exists():
            return 0.0
        with open(TRADE_LOG) as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    ts = entry.get("timestamp", "")
                    if not ts:
                        continue
                    entry_date = datetime.fromisoformat(ts.replace("Z", "+00:00")).date()
                    if entry_date == today and "pnl" in entry:
                        daily_pnl += entry["pnl"]
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass
    return daily_pnl


def get_portfolio_exposure(positions: dict) -> float:
    """Estimate total portfolio exposure in USD from positions."""
    # Each contract costs ~price_cents. Approximate with 50¢ avg if we don't
    # have exact prices. Conservative estimate.
    total = 0.0
    for ticker, pos in positions.items():
        # Rough estimate: each contract ≈ $0.50 average cost
        total += pos["abs_qty"] * 0.50
    return total


# ── Stale Order Cleanup ──────────────────────────────────────────────────────

def cleanup_stale_orders(client, max_age_minutes: int = 60) -> int:
    """Cancel resting orders older than max_age_minutes.

    Args:
        client: Initialized Kalshi API client
        max_age_minutes: Age threshold in minutes (default 60)

    Returns:
        Count of cancelled orders
    """
    cancelled = 0
    try:
        # Fetch all resting orders
        resp = client._portfolio_api.get_orders_without_preload_content(status='resting')
        data = json.loads(resp.read())
        orders = data.get('orders', [])

        if not orders:
            logger.info("No resting orders to clean up")
            return 0

        # Current time in UTC
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(minutes=max_age_minutes)

        logger.info(f"Checking {len(orders)} resting orders for age > {max_age_minutes} minutes")

        for order in orders:
            try:
                order_id = order.get('order_id', '')
                ticker = order.get('ticker', '?')
                created_time_str = order.get('created_time', '')

                if not order_id or not created_time_str:
                    continue

                # Parse ISO format created_time
                created_time = datetime.fromisoformat(created_time_str.replace('Z', '+00:00'))
                age_minutes = (now - created_time).total_seconds() / 60.0

                # If order is older than threshold, cancel it
                if created_time < cutoff_time:
                    logger.info(f"Cancelling stale order {order_id} on {ticker} (age={age_minutes:.1f} min)")

                    # Call DELETE endpoint
                    url = f"https://api.elections.kalshi.com/trade-api/v2/portfolio/orders/{order_id}"
                    client.call_api("DELETE", url)

                    # Log the cancellation
                    _log_state("stale_order_cancelled", {
                        "order_id": order_id,
                        "ticker": ticker,
                        "age_minutes": round(age_minutes, 1),
                    })
                    cancelled += 1

            except (ValueError, KeyError) as e:
                logger.warning(f"Failed to parse order: {e}")
                continue
            except Exception as e:
                logger.warning(f"Failed to cancel order {order.get('order_id', '?')}: {e}")
                continue

        if cancelled > 0:
            logger.info(f"Cleaned up {cancelled} stale orders")
            _log_state("stale_cleanup_complete", {"cancelled": cancelled})

        return cancelled

    except Exception as e:
        logger.error(f"Failed to cleanup stale orders: {e}")
        return 0


# ── Core Execution ────────────────────────────────────────────────────────

def auto_execute_edges(client, edges: list, cfg: dict, auto_cfg: dict, dry_run: bool = False) -> dict:
    """Execute trades for discovered edges with full safety checks.

    Args:
        client: Initialized Kalshi API client
        edges: List of edge dicts from kalshalyst (post-filter)
        cfg: Kalshalyst pipeline config
        auto_cfg: Auto-trader config
        dry_run: If True, log but don't place orders

    Returns:
        Execution summary dict
    """
    from kelly_size import kelly_size

    min_edge = auto_cfg.get("min_edge_threshold_pct", 3.5)
    max_daily_loss = auto_cfg.get("max_daily_loss_usd", 50.0)
    max_positions = auto_cfg.get("max_concurrent_positions", 8)
    max_exposure = auto_cfg.get("max_portfolio_exposure_usd", 200.0)
    bankroll = auto_cfg.get("bankroll_usd", 100.0)
    reconcile_wait = float(auto_cfg.get("reconciliation_wait_seconds", 30))

    # ── Pre-flight checks ─────────────────────────────────────────────
    # Balance check — must succeed or abort
    try:
        balance = get_balance(client)
    except RuntimeError as e:
        _log_state("abort", {"reason": f"Cannot fetch balance: {e}"})
        logger.error(f"Aborting: cannot verify balance — {e}")
        return _fail_loud_result("balance_fetch_failed", edges, known=f"ledger still tracks {_ledger_context().get('ledger_known_positions', 0)} open positions")
    if balance < 5.0:
        _log_state("abort", {"reason": f"Insufficient balance: ${balance:.2f}"})
        logger.warning(f"Aborting: balance ${balance:.2f} < $5 minimum")
        return {"trades_executed": 0, "trades_skipped": len(edges), "reason": "low_balance"}

    # Daily loss check
    daily_pnl = get_daily_pnl()
    if daily_pnl < -max_daily_loss:
        _log_state("abort", {"reason": f"Daily loss ${daily_pnl:.2f} exceeds limit ${max_daily_loss}"})
        logger.warning(f"Aborting: daily loss ${daily_pnl:.2f} exceeds -${max_daily_loss}")
        return {"trades_executed": 0, "trades_skipped": len(edges), "reason": "daily_loss_limit"}

    # Current positions — MUST succeed or we abort (prevents duplicate positions)
    try:
        positions = get_current_positions(client)
    except RuntimeError as e:
        _log_state("abort", {"reason": f"Cannot fetch positions: {e}"})
        logger.error(f"Aborting: cannot verify current positions — {e}")
        return _fail_loud_result("positions_fetch_failed", edges, known=f"trade ledger has {get_ledger_summary().get('open_positions', 0)} open positions")
    num_positions = len(positions)
    exposure = get_portfolio_exposure(positions)

    logger.info(f"Pre-flight: balance=${balance:.2f}, positions={num_positions}, "
                f"exposure~${exposure:.2f}, daily_pnl=${daily_pnl:.2f}")

    # ── Execute edges ─────────────────────────────────────────────────
    executed = 0
    skipped = 0
    errors = []
    remaining_balance = balance
    executed_trades = []  # Track executed trades for alerts

    for edge_idx, edge in enumerate(edges[:10], 1):  # Top 10 by edge
        trade_start = time.perf_counter()
        ticker = edge.get("ticker", "")
        title = edge.get("title", "?")[:50]
        est_prob = edge.get("estimated_probability", 0.5)
        market_price = edge.get("yes_price", 50)
        confidence = edge.get("confidence", 0.3)
        effective_edge = edge.get("effective_edge_pct", 0)
        direction = edge.get("direction", "fair")

        logger.info(f"[{edge_idx}/10] Processing: {title} ({ticker})")
        logger.info(f"  Edge={effective_edge:.1f}%, mkt={market_price}¢, est={est_prob:.0%}, conf={confidence:.2f}")

        # Determine side
        side = "yes" if direction == "underpriced" else "no"

        # ── Skip checks ───────────────────────────────────────────
        # Sports hard block (defense-in-depth — kalshalyst should filter upstream)
        if edge.get("is_sports", False):
            _log_state("edge_skipped", {"ticker": ticker, "reason": "sports_blocked"})
            logger.info(f"  BLOCKED: sports market — skipping")
            skipped += 1
            continue

        # Market filter check (defense-in-depth — kalshalyst applies upstream too)
        if edge.get("market_filter_action") == "skip":
            _log_state("edge_skipped", {"ticker": ticker, "reason": "market_filter_skip"})
            logger.info(f"  FILTERED: market filter skip — {edge.get('market_filter_reason', 'unknown')}")
            skipped += 1
            continue

        # Edge threshold
        if effective_edge < min_edge:
            _log_state("edge_skipped", {"ticker": ticker, "reason": "below_threshold",
                                        "edge": effective_edge, "threshold": min_edge})
            skipped += 1
            continue

        # Duplicate position
        if ticker in positions:
            held_side = positions[ticker]["side"]
            if held_side == side:
                _log_state("edge_skipped", {"ticker": ticker, "reason": "duplicate_position",
                                            "held_side": held_side})
                skipped += 1
                continue

        # Concurrent position limit
        if num_positions + executed >= max_positions:
            _log_state("edge_skipped", {"ticker": ticker, "reason": "max_positions",
                                        "current": num_positions + executed, "limit": max_positions})
            skipped += 1
            continue

        # Portfolio exposure limit
        if exposure >= max_exposure:
            _log_state("edge_skipped", {"ticker": ticker, "reason": "max_exposure",
                                        "exposure": round(exposure, 2), "limit": max_exposure})
            skipped += 1
            continue

        # ── Kelly sizing ──────────────────────────────────────────
        try:
            result = kelly_size(
                estimated_prob=est_prob,
                market_price_cents=market_price,
                confidence=confidence,
                bankroll_usd=min(bankroll, remaining_balance),
                side=side,
                current_exposure_usd=exposure,
                max_portfolio_exposure_usd=max_exposure,
            )
        except Exception as e:
            logger.error(f"Kelly sizing failed for {ticker}: {e}")
            errors.append(f"kelly_error:{ticker}")
            skipped += 1
            continue

        logger.info(f"  Kelly: {result.contracts}x @ ${result.cost_usd:.2f} "
                    f"(kelly={result.kelly_fraction:.4f}, frac={result.fractional_kelly:.4f})")

        if result.contracts <= 0:
            logger.info(f"  → Skipped: {result.reason}")
            _log_state("edge_skipped", {"ticker": ticker, "reason": f"kelly_zero: {result.reason}",
                                        "edge": effective_edge})
            skipped += 1
            continue

        # Balance check for this trade
        if result.cost_usd > remaining_balance:
            _log_state("edge_skipped", {"ticker": ticker, "reason": "insufficient_balance",
                                        "cost": result.cost_usd, "available": remaining_balance})
            skipped += 1
            continue

        # ── Execute or dry-run ────────────────────────────────────
        # Determine execution price (use ask for buys)
        exec_price = market_price
        if side == "yes":
            exec_price = edge.get("yes_ask", market_price) or market_price
        else:
            # For NO side, price = 100 - yes_bid
            yes_bid = edge.get("yes_bid", market_price) or market_price
            exec_price = 100 - yes_bid

        if dry_run:
            _log_state("edge_dry_run", {
                "ticker": ticker, "title": title, "side": side,
                "contracts": result.contracts, "cost_usd": round(result.cost_usd, 2),
                "price_cents": exec_price, "edge_pct": effective_edge,
                "kelly_fraction": round(result.fractional_kelly, 4),
                "confidence": confidence,
            })
            logger.info(f"[DRY RUN] {side.upper()} {result.contracts}x {ticker} @ {exec_price}¢ "
                        f"(${result.cost_usd:.2f}, edge={effective_edge:.1f}%)")
            executed_trades.append({
                "ticker": ticker,
                "side": side,
                "contracts": result.contracts,
                "price_cents": exec_price,
                "edge_pct": effective_edge,
                "cost_usd": result.cost_usd,
                "dry_run": True,
            })
            executed += 1
            remaining_balance -= result.cost_usd
            exposure += result.cost_usd
            continue

        # Live execution
        try:
            from kalshi_commands import _place_order, _trade_audit
            before_trade_positions = dict(positions)

            order_result = _place_order("buy", ticker, side, result.contracts, exec_price)

            _log_state("edge_executed", {
                "ticker": ticker, "title": title, "side": side,
                "contracts": result.contracts, "cost_usd": round(result.cost_usd, 2),
                "price_cents": exec_price, "edge_pct": effective_edge,
                "kelly_fraction": round(result.fractional_kelly, 4),
                "confidence": confidence,
                "order_result": order_result[:200],
            })

            submitted = order_result.startswith("✅") or order_result.startswith("❓")
            if submitted:
                logger.info(
                    f"SUBMITTED: {side.upper()} {result.contracts}x {ticker} @ {exec_price}¢ "
                    f"(${result.cost_usd:.2f}, edge={effective_edge:.1f}%)"
                )
                trade_record = record_trade(
                    ticker=ticker, side=side, contracts=result.contracts,
                    price_cents=exec_price, cost_usd=result.cost_usd,
                    edge_pct=effective_edge, confidence=confidence,
                    order_id="", order_result=order_result[:200], title=title, dry_run=False,
                )

                confirmed, confirmation_details, refreshed_positions = _reconcile_trade_with_portfolio(
                    client,
                    ticker=ticker,
                    side=side,
                    contracts=result.contracts,
                    before_positions=before_trade_positions,
                    wait_seconds=reconcile_wait,
                )
                update_trade_confirmation(
                    trade_record["id"],
                    confirmation_status="confirmed" if confirmed else "unconfirmed",
                    details=confirmation_details,
                )
                _log_state(
                    "trade_reconciled",
                    {
                        "ticker": ticker,
                        "trade_id": trade_record["id"],
                        "confirmed": confirmed,
                        "details": confirmation_details[:200],
                    },
                )
                logger.info("  Reconciliation: %s", confirmation_details)

                executed_trades.append({
                    "ticker": ticker,
                    "side": side,
                    "contracts": result.contracts,
                    "price_cents": exec_price,
                    "edge_pct": effective_edge,
                    "cost_usd": result.cost_usd,
                    "dry_run": False,
                    "confirmed": confirmed,
                    "confirmation_details": confirmation_details,
                })
                if confirmed:
                    executed += 1
                    remaining_balance -= result.cost_usd
                    exposure += result.cost_usd
                    positions = refreshed_positions or positions
                    _notify_slack(f"TRADE EXECUTED: {side.upper()} {result.contracts}x {ticker} @ {exec_price}c (${result.cost_usd:.2f}, edge={effective_edge:.1f}%)\nTitle: {title}")
                else:
                    errors.append(f"unconfirmed:{ticker}")
                    skipped += 1
                    _notify_slack(f"TRADE UNCONFIRMED: {side.upper()} {result.contracts}x {ticker} @ {exec_price}c — {confirmation_details[:100]}")
            else:
                logger.warning(f"Order FAILED for {ticker}: {order_result[:200]}")
                errors.append(f"order_failed:{ticker}")
                skipped += 1

        except Exception as e:
            elapsed = time.perf_counter() - trade_start
            logger.error(f"  Execution failed after {elapsed:.2f}s for {ticker}: {e}")
            _log_state("edge_failed", {"ticker": ticker, "error": str(e)[:200], "elapsed_s": round(elapsed, 2)})
            errors.append(f"exec_error:{ticker}")
            skipped += 1

    summary = {
        "trades_executed": executed,
        "trades_skipped": skipped,
        "daily_pnl": round(daily_pnl, 2),
        "portfolio_exposure": round(exposure, 2),
        "balance_remaining": round(remaining_balance, 2),
        "errors": errors,
        "executed_trades": executed_trades,
        **_ledger_context(),
    }
    return summary


# ── Main Entry Point ──────────────────────────────────────────────────────

def run_auto_trader(dry_run: bool = False) -> dict:
    """Full auto-trading cycle: scan → size → execute."""

    _log_state("scan_start", {"dry_run": dry_run})
    logger.info("=" * 60)
    logger.info(f"Auto-Trader starting (dry_run={dry_run})")
    logger.info("=" * 60)

    # ── Load config ───────────────────────────────────────────────────
    auto_cfg = load_config()
    if not auto_cfg:
        logger.info("No auto_trader_config.json found — exiting")
        _log_state("scan_end", {"reason": "no_config"})
        return {"status": "no_config"}

    if not auto_cfg.get("enabled", False):
        logger.info("Auto-trading disabled in config — exiting")
        _log_state("scan_end", {"reason": "disabled"})
        return {"status": "disabled"}

    if dry_run or auto_cfg.get("dry_run", False):
        dry_run = True
        logger.info("DRY RUN MODE — no orders will be placed")

    # ── Initialize Kalshi client ──────────────────────────────────────
    try:
        from kalshi_commands import _get_client, _check_enabled

        err = _check_enabled()
        if err:
            logger.error(f"Kalshi not configured: {err}")
            _log_state("scan_end", {"reason": "kalshi_not_configured", "error": err})
            return {"status": "error", "error": err}

        client = _get_client()
        if not client:
            logger.error("Failed to connect to Kalshi API")
            _log_state("scan_end", {"reason": "kalshi_connection_failed"})
            return {"status": "error", "error": "connection_failed"}

    except ImportError as e:
        logger.error(f"Cannot import kalshi_commands: {e}")
        _log_state("scan_end", {"reason": "import_error", "error": str(e)})
        return {"status": "error", "error": str(e)}

    # ── Cleanup stale orders ──────────────────────────────────────────
    stale_cleanup_count = cleanup_stale_orders(client, max_age_minutes=60)
    logger.info(f"Stale order cleanup: {stale_cleanup_count} orders cancelled")

    # ── Run kalshalyst scan ───────────────────────────────────────────
    try:
        from kalshalyst import fetch_kalshi_markets, calculate_edges, _apply_market_filter

        # Default pipeline config
        pipeline_cfg = {
            "min_volume": 10,
            "min_days_to_close": 1,
            "max_days_to_close": 365,
            "max_pages": 5,
            "max_fetch_seconds": 45,
            "max_markets_to_analyze": 50,
            "no_confidence_lo": 0.48,
            "no_confidence_hi": 0.55,
            "min_edge_pct": 3.0,
            "min_confidence": 0.2,
            "max_spread_cents": 10,
            "exclude_fair_direction": True,
            "ensemble_enabled": False,
        }

        # Check for ensemble config
        ensemble_cfg_path = Path.home() / ".openclaw" / "config.yaml"
        if ensemble_cfg_path.exists():
            try:
                import yaml
                with open(ensemble_cfg_path) as f:
                    full_cfg = yaml.safe_load(f) or {}
                kalshalyst_cfg = full_cfg.get("kalshalyst", {})
                pipeline_cfg.update(kalshalyst_cfg)
            except Exception:
                pass

        # ── Phase 1: Fetch markets ─────────────────────────────────────
        logger.info("Phase 1: Fetching markets...")
        markets = fetch_kalshi_markets(client, pipeline_cfg)
        logger.info("Market scope: policy | politics | tech | economics | macro (sports excluded)")

        if not markets:
            logger.info("No markets passed filters")
            _log_state("scan_end", {"reason": "no_markets", "edges_found": 0})
            return {"status": "no_markets"}

        # ── Phase 3+4: Estimate edges ────────────────────────────────
        edges = []
        if markets:
            logger.info(f"Phase 3+4: Estimating edges for {len(markets)} markets...")
            edges = calculate_edges(markets, pipeline_cfg)

        logger.info("Phase 4.5: Applying market filter...")
        edges = _apply_market_filter(edges, pipeline_cfg)

        logger.info(f"Found {len(edges)} edges after filtering")

    except Exception as e:
        logger.error(f"Scan failed: {e}")
        _log_state("scan_end", {"reason": "scan_error", "error": str(e)[:200]})
        return {"status": "error", "error": str(e)}

    if not edges:
        logger.info("No edges found — nothing to trade")
        _log_state("scan_end", {"edges_found": 0, "trades_executed": 0})
        return {"status": "no_edges"}

    # ── Execute trades ────────────────────────────────────────────────
    logger.info(f"Phase 6: Auto-executing top edges (dry_run={dry_run})...")
    summary = auto_execute_edges(client, edges, pipeline_cfg, auto_cfg, dry_run=dry_run)

    summary["edges_found"] = len(edges)
    summary["markets_scanned"] = len(markets) if markets else 0

    _log_state("scan_end", summary)
    logger.info(f"Scan complete: {summary['trades_executed']} executed, "
                f"{summary['trades_skipped']} skipped, "
                f"{len(edges)} edges found from {len(markets)} markets")

    logger.info("=" * 60)

    if summary.get("trades_executed", 0) > 0:
        trade_lines = []
        for t in summary.get("executed_trades", []):
            trade_lines.append(f"  {t['side'].upper()} {t['contracts']}x {t['ticker']} @ {t['price_cents']}c (${t['cost_usd']:.2f})")
        _notify_slack(f"AUTO-TRADER SCAN COMPLETE\nEdges found: {len(edges)}\nTrades executed: {summary['trades_executed']}\nTrades skipped: {summary['trades_skipped']}\n" + "\n".join(trade_lines))

    return summary


# ── CLI ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OpenClaw Auto-Trader")
    parser.add_argument("--dry-run", action="store_true", help="Log but don't place orders")
    parser.add_argument("--force", action="store_true", help="Run even if recently ran")
    parser.add_argument("--test-slack", action="store_true", help="Send a test Slack notification and exit")
    args = parser.parse_args()

    if args.test_slack:
        _notify_slack("AUTO-TRADER TEST: Slack notification is working.")
        print(json.dumps({"status": "test_slack_sent"}, indent=2))
        sys.exit(0)

    result = run_auto_trader(dry_run=args.dry_run)
    print(json.dumps(result, indent=2))
