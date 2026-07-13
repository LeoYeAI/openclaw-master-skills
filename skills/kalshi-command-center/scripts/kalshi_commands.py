#!/usr/bin/env python3
"""
Kalshi Command Center — Standalone trading interface.

Complete Kalshi API wrapper for portfolio management, live market scanning,
trade execution, and risk management.

Prerequisites:
  pip install --break-system-packages --user kalshi-python pyyaml

Authentication via environment variables:
  export KALSHI_KEY_ID="your-api-key-id"
  export KALSHI_KEY_PATH="/path/to/private.key"

Or config file (~/.openclaw/config.yaml):
  kalshi:
    enabled: true
    api_key_id: "your-key-id"
    private_key_file: "keys/kalshi-private.key"
"""

import argparse
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Try to load pyyaml for config file support
try:
    import yaml
except ImportError:
    yaml = None

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("kalshi")

# ── Config ────────────────────────────────────────────────────────────────────

def _load_config() -> dict:
    """Load config from ~/.openclaw/config.yaml if available."""
    if not yaml:
        return {}

    for candidate in [
        Path.home() / ".openclaw" / "config.yaml",
        Path.home() / ".config" / "imsg-watcher" / "config.yaml",
    ]:
        if candidate.exists():
            try:
                with open(candidate) as f:
                    data = yaml.safe_load(f) or {}
                    return data if isinstance(data, dict) else {}
            except Exception:
                pass
    return {}


_CONFIG = _load_config()
_KALSHI = _CONFIG.get("kalshi", {})

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"
TICKER_NAMES = _KALSHI.get("ticker_names", {})

# Environment variable overrides
KEY_ID = os.environ.get(
    "KALSHI_KEY_ID",
    _KALSHI.get("api_key_id", _KALSHI.get("key_id", ""))
)

_private_key_file = os.environ.get("KALSHI_KEY_PATH") or _KALSHI.get("private_key_file", "")
_legacy_private_path = _KALSHI.get("private_key_path", "")

if _private_key_file:
    _p = Path(_private_key_file).expanduser()
    PRIVATE_KEY_PATH = str(_p if _p.is_absolute() else (Path.home() / ".openclaw" / "keys" / _p))
else:
    PRIVATE_KEY_PATH = os.path.expanduser(_legacy_private_path)

CACHE_FILE = Path.home() / ".openclaw" / ".kalshi_research_cache.json"
TRADE_LOG = Path.home() / ".openclaw" / "logs" / "trades.jsonl"

_last_client_error = None  # populated by _get_client on failure


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


# ── Risk Limits ────────────────────────────────────────────────────────────

MAX_SINGLE_TRADE_COST = 25.00   # USD — hard cap per trade
MAX_POSITION_SIZE = 100          # contracts per trade
MAX_DAILY_LOSS = 50.00           # USD — kill switch


def _check_enabled():
    """Return error string if Kalshi is not configured, else None."""
    if not _KALSHI.get("enabled", False) and not (KEY_ID and PRIVATE_KEY_PATH):
        return "❌ Kalshi is not enabled. Set kalshi.enabled: true in config.yaml or set KALSHI_KEY_ID + KALSHI_KEY_PATH env vars."
    if not KEY_ID or KEY_ID.startswith("TODO"):
        return "❌ Kalshi key_id not configured. Set KALSHI_KEY_ID env var or kalshi.api_key_id in config.yaml."
    if not PRIVATE_KEY_PATH or not os.path.exists(PRIVATE_KEY_PATH):
        return f"❌ Kalshi private key not found at: {PRIVATE_KEY_PATH}"
    return None


def _get_client(*, _retries: int = 1, _backoff: float = 2.0):
    """Initialize Kalshi API client with retry on transient failures.

    Args:
        _retries: Number of retry attempts after initial failure (default: 1).
        _backoff: Seconds to wait between retries (default: 2.0).
    """
    global _last_client_error
    _last_client_error = None

    for attempt in range(_retries + 1):
        try:
            try:
                from kalshi_python_sync import Configuration, KalshiClient
            except ImportError:
                from kalshi_python import Configuration, KalshiClient

            config = Configuration(host=BASE_URL)
            with open(PRIVATE_KEY_PATH, 'r') as f:
                config.private_key_pem = f.read()
            config.api_key_id = KEY_ID
            client = KalshiClient(config)
            # Clear PEM from config object after client init — no reason to keep
            # the private key in memory longer than needed.
            config.private_key_pem = None

            # Verify auth — try public method first, fall back to internal API
            try:
                client.get_positions(limit=1)
            except (TypeError, AttributeError):
                client._portfolio_api.get_balance()

            if attempt > 0:
                logger.info("Kalshi client connected after %d retries", attempt)
            return client

        except Exception as e:
            _last_client_error = e
            err_str = str(e).lower()
            if "timeout" in err_str or "connection" in err_str or "reset" in err_str:
                category = "network"
            elif "401" in err_str or "403" in err_str or "auth" in err_str or "key" in err_str:
                category = "auth"
            elif "429" in err_str or "rate" in err_str:
                category = "rate_limit"
            else:
                category = "unknown"

            logger.error("Kalshi client init failed (attempt %d/%d, category=%s): %s",
                         attempt + 1, _retries + 1, category, e)

            if attempt < _retries:
                time.sleep(_backoff)

    return None


def _classify_kalshi_error(error) -> str:
    """Return a user-friendly error message based on the last _get_client failure."""
    if error is None:
        return "Unable to connect to Kalshi API."

    err_str = str(error).lower()
    if "timeout" in err_str or "connection" in err_str or "reset" in err_str:
        return "Can't reach Kalshi API — network timeout or connection reset. Likely a temporary issue on their end."
    if "401" in err_str or "403" in err_str or "auth" in err_str or "key" in err_str:
        return "Kalshi auth failed — API key may be expired or invalid. Check config.yaml credentials."
    if "429" in err_str or "rate" in err_str:
        return "Kalshi rate limited — too many requests. Try again in a minute."
    return f"Kalshi API error: {error}"


def _trade_audit(event: str, data: dict):
    """Append-only trade audit log with file locking for atomic writes."""
    import fcntl
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **data,
    }
    try:
        TRADE_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(TRADE_LOG, "a") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            try:
                f.write(json.dumps(entry) + "\n")
                f.flush()
                os.fsync(f.fileno())
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)
    except Exception as e:
        logger.warning(f"Failed to write trade audit log: {e}")


def _position_qty(position: dict) -> int:
    """Parse signed quantity from a Kalshi position payload."""
    value = position.get("position_fp") or position.get("position", 0)
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _fetch_position_snapshot(client) -> dict:
    """Return current signed position quantities keyed by ticker."""
    resp = client._portfolio_api.get_positions_without_preload_content(limit=200)
    data = json.loads(resp.read())
    pos_list = (
        data.get("event_positions")
        or data.get("positions")
        or data.get("market_positions")
        or []
    )
    snapshot = {}
    for position in pos_list:
        ticker = position.get("ticker") or position.get("market_ticker")
        if not ticker:
            continue
        snapshot[str(ticker)] = _position_qty(position)
    return snapshot


def _fetch_resting_orders(client, ticker: str = "") -> list[dict]:
    """Fetch current resting orders, optionally filtered to one ticker."""
    url = f"{BASE_URL}/portfolio/orders?status=resting"
    orders_resp = json.loads(client.call_api("GET", url).read())
    orders = orders_resp.get("orders", [])
    if ticker:
        return [order for order in orders if order.get("ticker") == ticker]
    return orders


def _reconcile_order(
    client,
    *,
    action: str,
    ticker: str,
    side: str,
    quantity: int,
    order_id: str,
    before_positions: dict,
    status: str,
) -> tuple[bool, str]:
    """Verify that an order is resting or changed portfolio state as expected."""
    delays = (0.0, 0.25, 0.75)
    before_qty = before_positions.get(ticker, 0)

    for delay in delays:
        if delay:
            time.sleep(delay)

        resting_orders = _fetch_resting_orders(client, ticker=ticker)
        if any(order.get("order_id") == order_id for order in resting_orders):
            return True, "RECONCILED: resting order confirmed on Kalshi"

        after_positions = _fetch_position_snapshot(client)
        after_qty = after_positions.get(ticker, 0)

        if action == "buy":
            expected_delta = quantity if side == "yes" else -quantity
            observed_delta = after_qty - before_qty
            if expected_delta > 0 and observed_delta >= quantity:
                return True, f"RECONCILED: YES position increased by {observed_delta}"
            if expected_delta < 0 and observed_delta <= -quantity:
                return True, f"RECONCILED: NO position increased by {abs(observed_delta)}"
        else:
            if abs(after_qty) <= max(0, abs(before_qty) - quantity):
                return True, f"RECONCILED: position size moved from {before_qty} to {after_qty}"

    if status == "executed":
        return False, "I don't know if the fill stuck — Kalshi said executed but the position delta never appeared"
    return False, "I don't know if the order is resting or filled — it never showed up in orders or positions"


def _check_risk(cost: float, quantity: int):
    """Check trade against risk limits. Returns error string or None if OK."""
    if cost > MAX_SINGLE_TRADE_COST:
        return f"❌ Trade cost ${cost:.2f} exceeds max ${MAX_SINGLE_TRADE_COST:.2f} per trade."
    if quantity > MAX_POSITION_SIZE:
        return f"❌ Quantity {quantity} exceeds max {MAX_POSITION_SIZE} contracts per trade."
    return None


def _refresh_live_prices(tickers):
    """Fetch live bid/ask for a list of tickers. Returns dict of ticker -> price data."""
    results = {}
    try:
        client = _get_client()
        if not client:
            return results

        for ticker in tickers:
            if not ticker:
                continue
            try:
                url = f"{BASE_URL}/markets/{ticker}"
                mkt = json.loads(client.call_api("GET", url).read()).get("market", {})
                results[ticker] = {
                    "yes_bid": mkt.get("yes_bid", 0) or 0,
                    "yes_ask": mkt.get("yes_ask", 0) or 0,
                    "no_bid": mkt.get("no_bid", 0) or 0,
                    "no_ask": mkt.get("no_ask", 0) or 0,
                    "status": mkt.get("status", "unknown"),
                    "volume_24h": mkt.get("volume_24h", 0) or 0,
                }
            except (KeyError, TypeError, ValueError):
                pass
    except Exception:
        pass

    return results


# ── Commands ──────────────────────────────────────────────────────────────────

def portfolio_command(args: str = "") -> str:
    """Show current Kalshi portfolio: Cash, Positions, Total"""
    err = _check_enabled()
    if err:
        return err

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        balance_resp = client._portfolio_api.get_balance()
        cash = balance_resp.balance / 100.0

        # Get open positions via raw API (avoids SDK deserialization bug)
        resp = client._portfolio_api.get_positions_without_preload_content(limit=100)
        raw_data = json.loads(resp.read())

        # Handle empty portfolio (API returns {"cursor": "..."} with no position keys)
        _EMPTY_ONLY_KEYS = {"cursor"}
        _KNOWN_POS_KEYS = ("event_positions", "positions", "market_positions")
        if set(raw_data.keys()) <= _EMPTY_ONLY_KEYS:
            # Empty portfolio — not a schema drift, just no positions
            pass  # fall through to normal processing with empty lists
        elif not any(k in raw_data for k in _KNOWN_POS_KEYS):
            return (
                f"❌ SCHEMA DRIFT: Kalshi API response has none of the expected position keys.\n"
                f"Got keys: {sorted(raw_data.keys())}\n"
                f"Expected one of: {_KNOWN_POS_KEYS}\n"
                f"This means Kalshi changed their API again. Fix the field name in kalshi_commands.py."
            )

        # v3 API returns event_positions, v2 returns market_positions, SDK uses positions
        all_positions = raw_data.get("event_positions") or raw_data.get("positions") or raw_data.get("market_positions", [])
        positions = [p for p in all_positions if _position_qty(p) != 0]

        # ── Circuit breaker: check API data against last known state ──────
        try:
            from circuit_breaker import check_portfolio
            api_pos_dict = {p.get("ticker", "?"): p for p in positions}
            cb_state = check_portfolio(api_pos_dict, cash, len(positions))
            if cb_state.is_tripped:
                # API data looks wrong — warn the user, show what we know
                from trade_ledger import get_summary as ledger_summary
                ls = ledger_summary()
                warning_lines = [
                    f"⚠️ CIRCUIT BREAKER TRIPPED: {cb_state.trip_reason}",
                    f"",
                    f"API is returning suspicious data. Showing last known state:",
                    f"💵 Cash (last known): ${cb_state.last_known_balance:.2f}",
                    f"📋 Ledger shows {ls['open_positions']} open positions, ${ls['total_deployed_usd']:.2f} deployed:",
                ]
                for ticker, pos in ls["positions"].items():
                    warning_lines.append(
                        f"  • {pos.get('title', ticker)}: {pos['contracts']}x {pos['side'].upper()} "
                        f"@ {pos['price_cents']}¢ (${pos['cost_usd']:.2f})"
                    )
                warning_lines.append("")
                warning_lines.append("⚠️ These numbers are from the local trade ledger, NOT live API data.")
                warning_lines.append("Manual positions (placed in the app) will NOT appear here.")
                return "\n".join(warning_lines)
        except ImportError:
            pass  # circuit_breaker not available — continue without it

        total_cost = 0.0
        total_val = 0.0
        unknown_valuations = 0
        pos_data = []

        for p in positions:
            ticker = p.get("ticker", "?")
            qty = _position_qty(p)
            side = "YES" if qty >= 0 else "NO"
            abs_qty = abs(qty)
            cost = float(p.get("market_exposure_dollars", 0))
            total_cost += cost

            try:
                url = f"{BASE_URL}/markets/{ticker}"
                mkt = _normalize_market(json.loads(client.call_api("GET", url).read()).get("market", {}))
                bid = mkt.get("yes_bid" if side == "YES" else "no_bid", 0)
                if not bid:
                    raise ValueError("missing live bid")
                cur_val = abs_qty * bid / 100.0
                pnl = cur_val - cost
                pct = (pnl / cost * 100) if cost else 0
                total_val += cur_val
                name = TICKER_NAMES.get(ticker, mkt.get("title", ticker))
                pos_data.append({
                    "name": name, "ticker": ticker, "qty": abs_qty, "side": side,
                    "cost": cost, "val": cur_val, "pnl": pnl, "pct": pct,
                })
            except (KeyError, TypeError, ValueError):
                unknown_valuations += 1
                name = TICKER_NAMES.get(ticker, ticker)
                pos_data.append({
                    "name": name, "ticker": ticker, "qty": abs_qty, "side": side,
                    "cost": cost, "val": None, "pnl": None, "pct": None,
                })

        # Sort by absolute P&L (biggest movers first)
        pos_data.sort(
            key=lambda x: abs(x["pnl"]) if isinstance(x.get("pnl"), (int, float)) else -1,
            reverse=True,
        )

        lines = []
        if unknown_valuations:
            lines.append(
                f"❓ I don't know current total P&L because {unknown_valuations} position(s) could not be priced live."
            )
            lines.append(f"💵 Cash: ${cash:.2f}  ·  Deployed: ${total_cost:.2f}  ·  Live value: unknown")
        else:
            total_pnl = total_val - total_cost
            trend = "📈" if total_pnl >= 0 else "📉"
            lines.append(f"{trend} P&L: ${total_pnl:+.2f} across {len(positions)} positions")
            lines.append(f"💵 Cash: ${cash:.2f}  ·  Deployed: ${total_cost:.2f}  ·  Value: ${total_val:.2f}")
        lines.append("")

        for p in pos_data:
            if p["pct"] is None:
                icon = "❓"
            elif p["pct"] >= 20:
                icon = "🔥"
            elif p["pct"] >= 5:
                icon = "✅"
            elif p["pct"] <= -15:
                icon = "⚠️"
            elif p["pct"] < 0:
                icon = "🔻"
            else:
                icon = "➖"
            if p["pct"] is None:
                lines.append(
                    f"{icon} {p['name']}: {p['qty']}x {p['side']} @ ${p['cost']:.2f} → "
                    f"I don't know current value"
                )
            else:
                lines.append(
                    f"{icon} {p['name']}: {p['qty']}x {p['side']} @ ${p['cost']:.2f} "
                    f"→ ${p['val']:.2f} ({p['pct']:+.0f}%)"
                )

        return "\n".join(lines)

    except Exception as e:
        return f"❓ I don't know your live portfolio right now: {e}"


def positions_command(args: str = "") -> str:
    """Show open positions with P&L"""
    return portfolio_command(args)  # same data, same format


def scan_command(args: str = "") -> str:
    """Live scan of Kalshi markets — fetches fresh data, ranks by heuristic edge.

    No Qwen, no Polygon — pure market microstructure signal.
    Designed to answer "what has edge RIGHT NOW?" in under 10 seconds.
    """
    err = _check_enabled()
    if err:
        return err

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        # Blocked ticker prefixes
        blocked_prefixes = {
            "KXHIGH", "KXLOW", "KXRAIN", "KXSNOW", "KXTEMP", "KXWIND",
            "KXWEATH", "INX", "NASDAQ", "FED-MR", "KXCELEB", "KXMOVIE",
            "KXTIKTOK", "KXYT", "KXTWIT", "KXSTREAM",
        }
        blocked_categories = {
            "weather", "climate", "entertainment", "sports",
            "social-media", "streaming", "celebrities",
        }
        sports_tokens = {
            "nfl", "nba", "mlb", "nhl", "mls", "ncaa", "pga", "ufc", "wwe",
            "super bowl", "superbowl", "march madness", "world series",
            "stanley cup", "finals", "playoff", "mvp", "heisman",
            "rushing", "passing", "touchdown", "home run", "strikeout",
            "quarterback", "pitcher", "espn", "sports",
            "valorant", "league of legends", "counter-strike", "dota",
            "overwatch", "fortnite", "call of duty", "esports", "e-sports",
            "atp", "wta", "tennis", "match:", "vs.", "round of",
            "boxing", "mma", "bellator", "formula 1", "f1 ", "nascar", "indycar",
        }

        # Signal-quality patterns — markets where LLM has no edge
        # Based on 165-market eval: politics 0.226 Brier, markets 0.334
        _noise_politics = {
            "primary", "runoff", "special election", "city council",
            "state senate", "state house", "state rep", "alderman",
            "margin of victory", "vote share", "win by more than",
            "win by less than", "percentage of vote",
            "win between", "win above", "seats in the",
            "leave office next", "leave office first",
            "be 1st in the next", "be first in the next",
            "next presidential election first round",
            "dutch election", "czech election", "argentine election",
            "brazilian election", "mexican election", "colombian election",
            "peruvian election", "chilean election", "turkish election",
            "south korean election", "japanese election", "indian election",
            "australian election", "canadian election",
            "romanian presidential", "japanese house",
            "gorton and denton",
        }
        _price_threshold_re = re.compile(
            r'(price|close|drop|fall|rise|trade|open|hit|reach|touch|break|stay)'
            r'\s+(above|below|over|under|at or above|at or below)'
            r'\s+\$?[\d,]+', re.IGNORECASE
        )
        _price_asset_re = re.compile(
            r'(bitcoin|btc|ethereum|eth|solana|sol|dogecoin|doge|xrp'
            r'|s&p|s&p 500|nasdaq|dow jones|djia|russell|vix'
            r'|gold|silver|oil|crude|wti|brent|natural gas'
            r'|aapl|amzn|goog|googl|msft|nvda|tsla|meta)'
            r'\s+.{0,20}(above|below|over|under|exceed|less than)\s+\$?[\d,]+',
            re.IGNORECASE
        )
        _coinflip_patterns = {"when will", "how many", "what will be the", "who will the next", "how much will"}
        _ipo_re = re.compile(r'\bipo\b', re.IGNORECASE)

        # Fetch 3 pages (600 markets)
        all_markets = []
        cursor = None
        for page in range(3):
            url = (
                "https://api.elections.kalshi.com/trade-api/v2/markets"
                "?limit=200&status=open&mve_filter=exclude"
            )
            if cursor:
                url += f"&cursor={cursor}"
            try:
                resp = client.call_api("GET", url)
                data = json.loads(resp.read())
                markets = [_normalize_market(m) for m in data.get("markets", [])]
                all_markets.extend(markets)
                cursor = data.get("cursor")
                if not cursor or not markets:
                    break
            except Exception:
                break

        if not all_markets:
            return "❌ Couldn't fetch Kalshi markets. API may be down."

        # Filter and score
        query = (args or "").strip().lower()
        include_sports = query == "sports"

        scored = []
        for m in all_markets:
            ticker = m.get("ticker", "")
            title = m.get("title", "")
            category = m.get("category", "") or m.get("series_ticker", "")
            volume = m.get("volume", 0) or 0
            oi = m.get("open_interest", 0) or 0
            yes_bid = m.get("yes_bid", 0) or 0
            yes_ask = m.get("yes_ask", 0) or 0

            # Must have a functioning order book
            if not yes_bid or not yes_ask:
                continue

            # Block garbage
            ticker_upper = ticker.upper()
            if any(ticker_upper.startswith(p) for p in blocked_prefixes):
                continue
            if category and category.lower().strip() in blocked_categories:
                continue

            # Signal-quality gate — block no-edge patterns
            title_lower_check = title.lower()
            if _price_threshold_re.search(title):
                continue
            if _price_asset_re.search(title):
                continue
            if any(pat in title_lower_check for pat in _noise_politics):
                continue

            # Volume floor
            if volume < 10:
                continue

            # Sports filter
            combined = f"{ticker} {title}".lower()
            is_sport = any(tok in combined for tok in sports_tokens)
            if is_sport and not include_sports:
                continue
            if include_sports and not is_sport:
                continue

            # Timeframe filter (7-180 days for interactive)
            expiration = m.get("expiration_time") or m.get("close_time", "")
            days_to_close = None
            if expiration and isinstance(expiration, str):
                try:
                    exp_str = expiration.replace("Z", "+00:00")
                    exp_dt = datetime.fromisoformat(exp_str)
                    days_to_close = max(0, (exp_dt - datetime.now(timezone.utc)).total_seconds() / 86400)
                except (ValueError, TypeError):
                    pass

            if days_to_close is not None:
                if days_to_close < 7 or days_to_close > 180:
                    continue

            mid = (yes_bid + yes_ask) / 2
            spread = yes_ask - yes_bid

            # Coinflip filter (needs mid price)
            if 40 <= mid <= 60:
                if _ipo_re.search(title):
                    continue
                if any(pat in title_lower_check for pat in _coinflip_patterns):
                    continue

            # ── Heuristic Edge Score ──
            # 1. Spread tightness (lower spread = better price discovery)
            spread_pct = spread / max(mid, 1) * 100
            spread_score = max(0, 20 - spread_pct) / 20

            # 2. Distance from extremes (20-80 range = actionable)
            centrality = 1 - abs(mid - 50) / 50
            if mid < 15 or mid > 85:
                centrality *= 0.3

            # 3. Liquidity (volume + OI, log-scaled)
            import math
            liq_score = math.log1p(volume) * 0.6 + math.log1p(oi) * 0.4

            # 4. Time value — sweet spot is 14-60 days
            time_score = 1.0
            if days_to_close is not None:
                if days_to_close < 14:
                    time_score = days_to_close / 14
                elif days_to_close > 60:
                    time_score = max(0.3, 1 - (days_to_close - 60) / 120)

            # Composite — optimized via grid search on 165 backtest markets
            # Previous: spread 25, centrality 35, liquidity 25, time 15 (-0.084 corr)
            # Optimized: spread 15, centrality 25, liquidity 35, time 25 (+0.008 corr)
            edge_score = (
                spread_score * 15
                + centrality * 25
                + liq_score * 35
                + time_score * 25
            )

            scored.append({
                "ticker": ticker,
                "title": title[:55],
                "yes_bid": yes_bid,
                "yes_ask": yes_ask,
                "mid": int(mid),
                "spread": spread,
                "spread_pct": round(spread_pct, 1),
                "volume": volume,
                "oi": oi,
                "days_to_close": days_to_close,
                "edge_score": round(edge_score, 1),
                "is_sport": is_sport,
            })

        scored.sort(key=lambda x: x["edge_score"], reverse=True)
        top = scored[:8]

        if not top:
            return "❌ No actionable markets right now. All filtered out by spread/volume/timeframe."

        # Format response
        tag = "🏀" if include_sports else "🎯"
        label = "Sports Scan" if include_sports else "Live Scan"
        lines = [f"{tag} {label} — {len(all_markets)} markets scanned, {len(scored)} passed filters:\n"]

        for i, m in enumerate(top, 1):
            days_str = f"{m['days_to_close']:.0f}d" if m['days_to_close'] is not None else "?"
            lines.append(f"{i}. {m['title']}")
            lines.append(f"   {m['yes_bid']}¢/{m['yes_ask']}¢ (spread {m['spread']}¢ = {m['spread_pct']}%) | vol {m['volume']:,} | OI {m['oi']:,} | {days_str}")
            lines.append(f"   Score: {m['edge_score']} | {m['ticker']}\n")

        lines.append("Scores = composite of spread tightness + price uncertainty + liquidity + time value.")
        lines.append("Say 'get [ticker]' for live bid/ask before trading.")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Live scan failed: {e}"


def markets_command(args: str = "") -> str:
    """List top opportunities from research cache with live price refresh.

    Args:
        args: optional filter — "sports" for sports markets,
              "all" for everything, empty for macro-heavy default.
    """
    err = _check_enabled()
    if err:
        return err

    try:
        if not CACHE_FILE.exists():
            return "❌ No research cache found. Run a deep research scan first."

        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)

        # Pick the right section based on args
        query = (args or "").strip().lower()
        if query == "sports":
            insights = cache.get('sports_insights', cache.get('insights', []))[:8]
            header_emoji = "🏀"
            header_label = "Sports"
        elif query == "all":
            insights = cache.get('all_insights', cache.get('insights', []))[:8]
            header_emoji = "🌐"
            header_label = "All Markets"
        else:
            insights = cache.get('insights', [])[:8]
            header_emoji = "📈"
            header_label = "Top Opportunities"

        if not insights:
            if query == "sports":
                return "❌ No sports opportunities in cache."
            return "❌ No opportunities found in cache."

        cached_at = cache.get('cached_at', '')
        try:
            cache_time = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
            age_min = int((datetime.now(cache_time.tzinfo) - cache_time).total_seconds() / 60)
            age_str = f"{age_min}m ago"
        except ValueError:
            age_str = "unknown age"

        macro_n = cache.get('macro_count', '?')
        sports_n = cache.get('sports_count', '?')

        # Try live price refresh on top tickers
        live_prices = _refresh_live_prices([i.get('ticker') for i in insights[:5]])

        lines = [f"{header_emoji} {header_label} (cache: {age_str} | {macro_n} macro, {sports_n} sports):\n"]

        for i, insight in enumerate(insights, 1):
            ticker = insight.get('ticker', 'unknown')
            title = insight.get('title', ticker)[:50]
            side = insight.get('side', '?')
            confidence = insight.get('confidence', 'unknown').upper()
            is_sport = insight.get('is_sports', False)
            tag = "🏀" if is_sport else "📊"

            days = insight.get('days_to_close')
            days_str = f"{days:.0f}d" if days is not None else "?"
            edge = insight.get('effective_edge_pct', insight.get('edge_pct', 0))
            mkt_prob = insight.get('market_prob', 0)
            est_prob = insight.get('estimated_prob', 0)
            reasoning = insight.get('reasoning', '')[:60]

            lines.append(f"{i}. {tag} {title}")
            lines.append(f"   {side} @ {mkt_prob:.0%} | {edge:.0f}% edge | {confidence} | {days_str}")
            if reasoning:
                lines.append(f"   {reasoning}")
            lines.append(f"   📎 {ticker}\n")

        if not query:
            lines.append("Say 'markets sports' or 'markets all' to filter.")
        lines.append("Say 'execute [#]' to trade a pick.")

        return "\n".join(lines)

    except Exception as e:
        return f"Failed to fetch markets: {e}"


def get_market_command(ticker: str) -> str:
    """Get live market data for a single ticker: bid/ask/last for both sides,
    volume, spread, and status. Use BEFORE placing any buy or sell order."""
    err = _check_enabled()
    if err:
        return err

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        url = f"{BASE_URL}/markets/{ticker}"
        mkt = json.loads(client.call_api("GET", url).read()).get("market", {})

        yes_bid = mkt.get("yes_bid", 0)
        yes_ask = mkt.get("yes_ask", 0)
        no_bid = mkt.get("no_bid", 0)
        no_ask = mkt.get("no_ask", 0)
        last = mkt.get("last_price", 0)
        vol_24h = mkt.get("volume_24h", 0)
        volume = mkt.get("volume", 0)
        status = mkt.get("status", "unknown")
        title = mkt.get("title", ticker)
        close_time = mkt.get("close_time", "?")

        yes_spread = yes_ask - yes_bid if yes_ask and yes_bid else None
        no_spread = no_ask - no_bid if no_ask and no_bid else None

        name = TICKER_NAMES.get(ticker, title)
        lines = [
            f"📊 {name} ({ticker})",
            f"Status: {status} | Close: {close_time}",
            f"",
            f"YES — Bid: {yes_bid}¢ | Ask: {yes_ask}¢ | Spread: {yes_spread}¢" if yes_spread is not None else f"YES — Bid: {yes_bid}¢ | Ask: {yes_ask}¢",
            f"NO  — Bid: {no_bid}¢ | Ask: {no_ask}¢ | Spread: {no_spread}¢" if no_spread is not None else f"NO  — Bid: {no_bid}¢ | Ask: {no_ask}¢",
            f"Last: {last}¢ | Vol 24h: {vol_24h:,} | Total vol: {volume:,}",
        ]

        # Actionable guidance for the user
        lines.append("")
        lines.append("💡 To sell YES contracts: sell at yes_bid ({0}¢) for instant fill, or post ask at {1}¢ for better price.".format(yes_bid, yes_bid + 1 if yes_bid < 99 else 99))
        lines.append("💡 To sell NO contracts: sell at no_bid ({0}¢) for instant fill, or post ask at {1}¢ for better price.".format(no_bid, no_bid + 1 if no_bid < 99 else 99))
        lines.append("💡 To buy YES: buy at yes_ask ({0}¢) for instant fill, or post bid at {1}¢ for better price.".format(yes_ask, yes_ask - 1 if yes_ask > 1 else 1))

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Failed to fetch market data: {e}"


def buy_command(ticker: str, side: str, quantity: int, price_cents: int) -> str:
    """Place a limit buy order on Kalshi."""
    return _place_order("buy", ticker, side, quantity, price_cents)


def sell_command(ticker: str, side: str, quantity: int, price_cents: int) -> str:
    """Place a limit sell order on Kalshi (exit a position)."""
    return _place_order("sell", ticker, side, quantity, price_cents)


def _place_order(
    action: str, ticker: str, side: str, quantity: int, price_cents: int,
) -> str:
    """Unified order placement for buy and sell."""
    err = _check_enabled()
    if err:
        return err

    side = side.lower().strip()
    if side not in ("yes", "no"):
        return f"❌ Side must be 'yes' or 'no', got '{side}'."
    if not (1 <= price_cents <= 99):
        return f"❌ Price must be 1-99 cents, got {price_cents}."
    if quantity < 1:
        return f"❌ Quantity must be at least 1."

    amount = quantity * price_cents / 100.0

    if action == "buy":
        risk_err = _check_risk(amount, quantity)
        if risk_err:
            _trade_audit("trade_blocked", {
                "ticker": ticker, "side": side, "quantity": quantity,
                "price_cents": price_cents, "reason": risk_err,
            })
            return risk_err

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"
        before_positions = _fetch_position_snapshot(client)

        try:
            from kalshi_python_sync.models.create_order_request import CreateOrderRequest
        except ImportError:
            from kalshi_python.models.create_order_request import CreateOrderRequest

        order_params = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "count": quantity,
            "type": "limit",
        }
        if side == "yes":
            order_params["yes_price"] = price_cents
        else:
            order_params["no_price"] = price_cents

        amount_key = "cost_estimate" if action == "buy" else "proceeds_estimate"
        _trade_audit(f"{action}_submitted", {
            "ticker": ticker, "side": side, "quantity": quantity,
            "price_cents": price_cents, amount_key: amount,
        })

        order_request = CreateOrderRequest(**order_params)
        resp = client._portfolio_api.create_order_without_preload_content(order_request)
        result = json.loads(resp.read())

        # ── Validate API response ──────────────────────────────────────
        if "error" in result:
            error_msg = result.get("error", {})
            if isinstance(error_msg, dict):
                error_msg = error_msg.get("message", str(error_msg))
            _trade_audit(f"{action}_api_error", {
                "ticker": ticker, "error": str(error_msg)[:200],
            })
            return f"❌ Kalshi API error: {error_msg}"

        order = result.get("order")
        if not order or not isinstance(order, dict):
            _trade_audit(f"{action}_invalid_response", {
                "ticker": ticker, "raw_response": str(result)[:300],
            })
            return f"❌ Kalshi returned invalid response — no 'order' object. Raw: {str(result)[:150]}"

        order_id = order.get("order_id")
        status = order.get("status")

        if not order_id:
            _trade_audit(f"{action}_no_order_id", {
                "ticker": ticker, "raw_order": str(order)[:300],
            })
            return f"❌ Kalshi returned order without order_id. Raw: {str(order)[:150]}"

        _trade_audit(f"{action}_placed", {
            "ticker": ticker, "order_id": order_id, "status": status or "unknown",
        })

        try:
            verified, verify_msg = _reconcile_order(
                client,
                action=action,
                ticker=ticker,
                side=side,
                quantity=quantity,
                order_id=order_id,
                before_positions=before_positions,
                status=status or "",
            )
        except Exception as ve:
            verified = False
            verify_msg = f"I don't know if the order stuck — reconciliation failed: {ve}"

        if not verified:
            _trade_audit(f"{action}_unverified", {
                "ticker": ticker,
                "order_id": order_id,
                "status": status,
                "verification": verify_msg[:200],
            })
            try:
                from trade_ledger import get_summary as ledger_summary
                ledger = ledger_summary()
                known = (
                    f"Trade ledger still shows {ledger.get('open_positions', 0)} open positions "
                    f"and ${ledger.get('total_deployed_usd', 0.0):.2f} deployed."
                )
            except Exception:
                known = "Trade ledger context is unavailable."
            return f"❓ Order submitted for {ticker}, but {verify_msg}\n📒 {known}"

        name = TICKER_NAMES.get(ticker, ticker)
        fill_msg = "Filled" if status == "executed" else "Resting" if status == "resting" else (status or "unknown").capitalize()
        verb = "Bought" if action == "buy" else "Sold"
        amount_label = "total cost" if action == "buy" else "est. proceeds"
        return (
            f"✅ {verb} {quantity}x {side.upper()} on {name} at {price_cents}¢\n"
            f"💰 {fill_msg} — {amount_label} ${amount:.2f}\n"
            f"🔍 {verify_msg}"
        )

    except Exception as e:
        _trade_audit(f"{action}_failed", {
            "ticker": ticker, "error": str(e)[:200],
        })
        return f"❌ {'Trade' if action == 'buy' else 'Sell'} failed: {e}"


def execute_pick_command(pick_number: int, qty_override: int = 0) -> str:
    """Execute a trade from the research cache by pick number.

    Steps:
      1. Load pick from .kalshi_research_cache.json
      2. Fetch live bid/ask from Kalshi API
      3. Size position via Kelly (or fallback to qty_override / default)
      4. Place the order via _place_order
      5. Verify the order exists in open/resting orders or positions
    """
    err = _check_enabled()
    if err:
        return err

    # ── Step 1: Load research cache ──────────────────────────────────────
    if not CACHE_FILE.exists():
        return "❌ No research cache found. Run Kalshalyst edge scan first."

    try:
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    except Exception as e:
        return f"❌ Failed to read research cache: {e}"

    insights = cache.get('insights', [])
    if not insights:
        return "❌ Research cache is empty. Run Kalshalyst edge scan first."

    if pick_number < 1 or pick_number > len(insights):
        return f"❌ Pick #{pick_number} out of range. Cache has {len(insights)} picks (1-{len(insights)})."

    pick = insights[pick_number - 1]
    ticker = pick.get('ticker')
    if not ticker:
        return f"❌ Pick #{pick_number} has no ticker."

    side = (pick.get('side', '') or '').lower().strip()
    if side not in ('yes', 'no'):
        return f"❌ Pick #{pick_number} has invalid side: '{pick.get('side')}'. Expected 'yes' or 'no'."

    title = pick.get('title', ticker)[:50]
    est_prob = pick.get('estimated_prob', 0)
    confidence_str = pick.get('confidence', 'unknown')
    edge_pct = pick.get('effective_edge_pct', pick.get('edge_pct', 0))

    lines = [f"🎯 Executing pick #{pick_number}: {title}", f"   Side: {side.upper()} | Edge: {edge_pct:.0f}% | Conf: {confidence_str}", ""]

    # ── Step 2: Fetch live prices ────────────────────────────────────────
    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        url = f"{BASE_URL}/markets/{ticker}"
        mkt = json.loads(client.call_api("GET", url).read()).get("market", {})
    except Exception as e:
        return f"❌ Failed to fetch live prices for {ticker}: {e}"

    status = mkt.get("status", "unknown")
    if status != "open":
        return f"❌ Market {ticker} is not open (status: {status}). Cannot trade."

    # Determine execution price (buy at ask for the chosen side)
    if side == "yes":
        exec_price = mkt.get("yes_ask", 0) or 0
        bid = mkt.get("yes_bid", 0) or 0
    else:
        exec_price = mkt.get("no_ask", 0) or 0
        bid = mkt.get("no_bid", 0) or 0

    if exec_price <= 0 or exec_price > 99:
        return f"❌ No valid ask price for {side.upper()} on {ticker}. Market may be illiquid."

    spread = exec_price - bid if bid > 0 else None
    spread_str = f" (spread: {spread}¢)" if spread is not None else ""
    lines.append(f"📊 Live price: {side.upper()} ask {exec_price}¢ | bid {bid}¢{spread_str}")

    # ── Step 3: Position sizing ──────────────────────────────────────────
    quantity = 0
    sizing_method = ""

    if qty_override > 0:
        quantity = qty_override
        sizing_method = "manual override"
    else:
        # Try Kelly sizing from kalshalyst
        try:
            # Attempt to import kelly_size from kalshalyst scripts
            import importlib.util
            kelly_paths = [
                Path.home() / "skills" / "kalshalyst" / "scripts" / "kelly_size.py",
                Path(__file__).parent.parent.parent / "kalshalyst" / "scripts" / "kelly_size.py",
            ]
            kelly_mod = None
            for kp in kelly_paths:
                if kp.exists():
                    spec = importlib.util.spec_from_file_location("kelly_size", kp)
                    if spec and spec.loader:
                        kelly_mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(kelly_mod)
                        break

            if kelly_mod:
                # Fetch bankroll (cash available)
                bal_url = f"{BASE_URL}/portfolio/balance"
                bal_resp = json.loads(client.call_api("GET", bal_url).read())
                bankroll = bal_resp.get("balance", 0) / 100.0  # cents to dollars

                # Resolve confidence to float
                conf_float = 0.5
                if isinstance(confidence_str, (int, float)):
                    conf_float = float(confidence_str)
                elif isinstance(confidence_str, str):
                    conf_map = {"high": 0.8, "medium": 0.6, "low": 0.3}
                    conf_float = conf_map.get(confidence_str.lower(), 0.5)

                market_price_cents = exec_price if side == "yes" else (100 - exec_price)
                result = kelly_mod.kelly_size(
                    estimated_prob=est_prob,
                    market_price_cents=market_price_cents,
                    confidence=conf_float,
                    bankroll_usd=bankroll,
                    side=side,
                )
                quantity = result.contracts
                sizing_method = f"Kelly (f={result.kelly_fraction:.3f}, frac={result.fractional_kelly:.4f}, bankroll=${bankroll:.2f})"
                lines.append(f"📐 Kelly sizing: {result.reason}")
        except Exception as e:
            logger.warning("Kelly sizing failed, using fallback: %s", e)

    # Fallback if Kelly returned 0 or wasn't available
    if quantity <= 0:
        # Default: $25 max / ask price, capped at 100 contracts
        quantity = min(int(MAX_SINGLE_TRADE_COST / (exec_price / 100.0)), MAX_POSITION_SIZE)
        quantity = max(quantity, 1)
        sizing_method = sizing_method or f"fallback (${MAX_SINGLE_TRADE_COST:.0f} cap / {exec_price}¢)"

    cost = quantity * exec_price / 100.0
    lines.append(f"📐 Size: {quantity} contracts @ {exec_price}¢ = ${cost:.2f} ({sizing_method})")
    lines.append("")

    # ── Step 4: Place the order ──────────────────────────────────────────
    order_result = _place_order("buy", ticker, side, quantity, exec_price)
    lines.append(order_result)

    # Check if order placement failed
    if order_result.startswith("❌"):
        _trade_audit("execute_pick_failed", {
            "pick": pick_number, "ticker": ticker, "side": side,
            "quantity": quantity, "price_cents": exec_price,
            "order_result": order_result[:200],
        })
        return "\n".join(lines)

    # ── Step 5: Verify order exists ──────────────────────────────────────
    lines.append("")
    try:
        # Check resting orders
        orders_url = f"{BASE_URL}/portfolio/orders?status=resting"
        orders_resp = json.loads(client.call_api("GET", orders_url).read())
        resting = orders_resp.get("orders", [])
        found_resting = any(o.get("ticker") == ticker for o in resting)

        # Check executed (filled) orders — look at positions
        positions_url = f"{BASE_URL}/portfolio/positions"
        pos_resp = json.loads(client.call_api("GET", positions_url).read())
        pos_list = pos_resp.get("event_positions") or pos_resp.get("positions") or pos_resp.get("market_positions", [])
        found_position = any(
            p.get("ticker") == ticker or p.get("market_ticker") == ticker
            for p in pos_list
        )

        if found_resting:
            lines.append("✅ VERIFIED: Order found in resting orders on Kalshi.")
        elif found_position:
            lines.append("✅ VERIFIED: Position found — order was filled immediately.")
        else:
            lines.append("⚠️ WARNING: Could not verify order in resting orders or positions. Check Kalshi directly.")
            _trade_audit("execute_pick_unverified", {
                "pick": pick_number, "ticker": ticker,
            })
    except Exception as e:
        lines.append(f"⚠️ Verification check failed: {e}. Confirm on Kalshi directly.")

    _trade_audit("execute_pick_completed", {
        "pick": pick_number, "ticker": ticker, "side": side,
        "quantity": quantity, "price_cents": exec_price,
        "cost_usd": cost, "sizing_method": sizing_method,
    })

    return "\n".join(lines)


def get_open_orders_command() -> str:
    """List all open/resting orders (unfilled limit orders)."""
    err = _check_enabled()
    if err:
        return err

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        url = f"{BASE_URL}/portfolio/orders?status=resting"
        resp = client.call_api("GET", url)
        result = json.loads(resp.read())
        orders = result.get("orders", [])

        if not orders:
            return "📋 No open orders."

        lines = [f"📋 {len(orders)} open order(s):"]
        for o in orders:
            ticker = o.get("ticker", "?")
            action = o.get("action", "?").upper()
            side = o.get("side", "?").upper()
            count = o.get("remaining_count", o.get("count", "?"))
            price = o.get("yes_price") or o.get("no_price") or "?"
            order_id = o.get("order_id", "?")
            name = TICKER_NAMES.get(ticker, ticker)
            lines.append(f"  {action} {count}x {side} on {name} @ {price}¢ — ID: {order_id}")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Failed to fetch orders: {e}"


def cancel_order_command(order_id: str) -> str:
    """Cancel an open/resting order by order ID."""
    err = _check_enabled()
    if err:
        return err

    if not order_id or order_id.strip() == "":
        return "❌ order_id is required."

    try:
        client = _get_client()
        if not client:
            return f"❌ {_classify_kalshi_error(_last_client_error)}"

        url = f"{BASE_URL}/portfolio/orders/{order_id.strip()}"
        resp = client.call_api("DELETE", url)
        result = json.loads(resp.read())

        _trade_audit("order_cancelled", {
            "order_id": order_id,
            "result": str(result)[:200],
        })

        cancelled = result.get("order", result)
        status = cancelled.get("status", "cancelled")
        return f"✅ Order {order_id} cancelled. Status: {status}"

    except Exception as e:
        _trade_audit("cancel_failed", {
            "order_id": order_id, "error": str(e)[:200],
        })
        return f"❌ Cancel failed: {e}"


# ── CLI Entry Point ────────────────────────────────────────────────────────────

def main():
    """CLI entry point with argparse routing."""
    parser = argparse.ArgumentParser(
        description="Kalshi Command Center — Trading interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s portfolio           - Show portfolio P&L
  %(prog)s scan               - Live market scan
  %(prog)s scan sports        - Sports-only scan
  %(prog)s markets            - Cached opportunities
  %(prog)s get TICKER         - Live bid/ask
  %(prog)s buy TICKER yes 10 35   - Buy 10x YES @ 35¢
  %(prog)s sell TICKER no 5 63    - Sell 5x NO @ 63¢
  %(prog)s orders             - List open orders
  %(prog)s cancel ORDER_ID    - Cancel order
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Portfolio commands
    subparsers.add_parser("portfolio", help="Show portfolio P&L")
    subparsers.add_parser("positions", help="Show open positions")

    # Scan commands
    scan_parser = subparsers.add_parser("scan", help="Live market scan")
    scan_parser.add_argument("filter", nargs="?", default="", help="Filter: 'sports' or empty")

    # Markets command
    markets_parser = subparsers.add_parser("markets", help="Cached research results")
    markets_parser.add_argument("filter", nargs="?", default="", help="Filter: 'sports', 'all', or empty")

    # Get market data
    get_parser = subparsers.add_parser("get", help="Get live market data")
    get_parser.add_argument("ticker", help="Market ticker")

    # Buy command
    buy_parser = subparsers.add_parser("buy", help="Place limit buy order")
    buy_parser.add_argument("ticker", help="Market ticker")
    buy_parser.add_argument("side", help="'yes' or 'no'")
    buy_parser.add_argument("quantity", type=int, help="Number of contracts")
    buy_parser.add_argument("price", type=int, help="Limit price in cents (1-99)")

    # Sell command
    sell_parser = subparsers.add_parser("sell", help="Place limit sell order")
    sell_parser.add_argument("ticker", help="Market ticker")
    sell_parser.add_argument("side", help="'yes' or 'no'")
    sell_parser.add_argument("quantity", type=int, help="Number of contracts")
    sell_parser.add_argument("price", type=int, help="Limit price in cents (1-99)")

    # Orders command
    subparsers.add_parser("orders", help="List open orders")

    # Execute from cache
    exec_parser = subparsers.add_parser("execute", help="Execute a pick from research cache")
    exec_parser.add_argument("pick", type=int, help="Pick number (1-based)")
    exec_parser.add_argument("qty", nargs="?", type=str, default="",
                             help="Optional: 'qty' keyword (ignored) or quantity")
    exec_parser.add_argument("qty_val", nargs="?", type=str, default="",
                             help="Optional: quantity override (e.g., '25' or '25 contracts')")

    # Cancel command
    cancel_parser = subparsers.add_parser("cancel", help="Cancel an order")
    cancel_parser.add_argument("order_id", help="Order ID to cancel")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Route to handlers
    if args.command == "portfolio":
        print(portfolio_command())
    elif args.command == "positions":
        print(positions_command())
    elif args.command == "scan":
        print(scan_command(args.filter))
    elif args.command == "markets":
        print(markets_command(args.filter))
    elif args.command == "get":
        print(get_market_command(args.ticker))
    elif args.command == "buy":
        print(buy_command(args.ticker, args.side, args.quantity, args.price))
    elif args.command == "sell":
        print(sell_command(args.ticker, args.side, args.quantity, args.price))
    elif args.command == "execute":
        # Parse flexible qty syntax: "execute 1 qty 25", "execute 1 25", "execute 1 25 contracts"
        qty_override = 0
        raw_qty = args.qty_val or args.qty or ""
        raw_qty = raw_qty.replace("contracts", "").replace("qty", "").strip()
        if raw_qty:
            try:
                qty_override = int(raw_qty)
            except ValueError:
                pass
        # If args.qty is a plain number (not "qty"), treat it as the quantity
        if qty_override == 0 and args.qty:
            clean = args.qty.replace("contracts", "").replace("qty", "").strip()
            if clean:
                try:
                    qty_override = int(clean)
                except ValueError:
                    pass
        print(execute_pick_command(args.pick, qty_override))
    elif args.command == "orders":
        print(get_open_orders_command())
    elif args.command == "cancel":
        print(cancel_order_command(args.order_id))


if __name__ == "__main__":
    main()
