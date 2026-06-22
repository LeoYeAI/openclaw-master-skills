#!/usr/bin/env python3
"""
Market Morning Brief — Daily market intelligence digest.

Combines portfolio positions, prediction market opportunities, cross-platform
divergences, crypto prices, and X signals into a 30-second morning read.

Usage:
    python morning_brief.py [--config CONFIG] [--dry-run] [--debug]

Outputs plain text to stdout (no markdown, no emojis — SMS/iMessage compatible).
"""

import json
import os
import sys
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Optional dependencies
try:
    import requests
except ImportError:
    requests = None

try:
    import yaml
except ImportError:
    yaml = None

try:
    from kalshi_python_sync import Configuration as KalshiConfiguration, KalshiClient
except ImportError:
    try:
        from kalshi_python import Configuration as KalshiConfiguration, KalshiClient
    except ImportError:
        KalshiConfiguration = None
        KalshiClient = None

DEMO_PORTFOLIO = [
    {
        "ticker": "FEDCUTS-2026-Q3",
        "side": "YES",
        "quantity": 35,
        "entry_price": 0.41,
        "current_price": 0.47,
        "days_to_exp": 110,
    },
    {
        "ticker": "BTC-2026-120K",
        "side": "NO",
        "quantity": 20,
        "entry_price": 0.58,
        "current_price": 0.52,
        "days_to_exp": 74,
    },
    {
        "ticker": "ETHETF-2026",
        "side": "YES",
        "quantity": 18,
        "entry_price": 0.36,
        "current_price": 0.44,
        "days_to_exp": 143,
    },
]

DEMO_EDGES = [
    {
        "ticker": "FEDCUTS-2026-Q3",
        "market_prob": 0.43,
        "estimated_prob": 0.57,
        "edge_pct": 14,
        "confidence": 0.68,
    },
    {
        "ticker": "BTC-2026-120K",
        "market_prob": 0.39,
        "estimated_prob": 0.49,
        "edge_pct": 10,
        "confidence": 0.61,
    },
    {
        "ticker": "STABLECOIN-REG-2026",
        "market_prob": 0.34,
        "estimated_prob": 0.42,
        "edge_pct": 8,
        "confidence": 0.57,
    },
]

DEMO_DIVERGENCES = [
    {
        "ticker": "FEDCUTS-2026",
        "kalshi_price": 0.43,
        "polymarket_price": 0.49,
        "spread_cents": 6,
    },
    {
        "ticker": "BTC-120K-2026",
        "kalshi_price": 0.39,
        "polymarket_price": 0.35,
        "spread_cents": 4,
    },
]

DEMO_X_SIGNALS = [
    {"signal": "Stablecoin bill odds firming after committee chatter", "confidence": 0.73, "reach": 12400},
    {"signal": "Macro desk turning cautious on late-summer rate cuts", "confidence": 0.66, "reach": 8100},
]

DEMO_POLYMARKET = [
    {"question": "Will the Fed cut rates by September 2026?", "volume": 3400000, "implied_prob": 49},
    {"question": "Will Bitcoin hit $120k before July 2026?", "volume": 2800000, "implied_prob": 35},
    {"question": "Will Congress pass stablecoin legislation in 2026?", "volume": 1900000, "implied_prob": 44},
]

LOW_SIGNAL_POLYMARKET_PATTERNS = (
    "highest temperature",
    "temperature in",
    "rainfall",
    "snowfall",
    "precipitation",
    "game ",
    "match ",
    "tournament",
    "masters",
    "esports",
    "vs ",
    "team ",
    "player ",
)


def log(msg, debug=False):
    """Log message to stderr if debug enabled."""
    if debug:
        print(f"[DEBUG] {msg}", file=sys.stderr)


def format_time(ts_str):
    """Format ISO timestamp to readable string."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return ts_str


def check_cache_age(cache_file, max_age_seconds):
    """Check if cache is fresh. Returns ('fresh', age_secs) or ('stale', age_secs) or ('missing', 0).

    Handles both ISO "cached_at" strings and unix epoch "timestamp" floats.
    """
    try:
        with open(cache_file) as f:
            data = json.load(f)

        # Try ISO "cached_at" first, then unix epoch "timestamp"
        cached_at = data.get("cached_at")
        timestamp = data.get("timestamp")

        if cached_at:
            try:
                dt = datetime.fromisoformat(cached_at.replace("Z", "+00:00"))
                age_seconds = (datetime.now(timezone.utc) - dt).total_seconds()
            except (ValueError, TypeError):
                age_seconds = None
        elif timestamp:
            try:
                import time as _time
                age_seconds = _time.time() - float(timestamp)
            except (ValueError, TypeError):
                age_seconds = None
        else:
            return "missing", 0

        if age_seconds is None:
            return "error", 0

        if age_seconds > max_age_seconds:
            return "stale", age_seconds
        return "fresh", age_seconds
    except FileNotFoundError:
        return "missing", 0
    except Exception:
        return "error", 0


def emphasize(value):
    """Lightweight emphasis for high-signal values."""
    return f"**{value}**"


def _notify_slack(message: str) -> None:
    """Send notification via Slack webhook. Silent on failure."""
    webhook_url = os.environ.get("OPENCLAW_SLACK_WEBHOOK", "")
    if not webhook_url:
        try:
            config = load_config()
            webhook_url = config.get("slack_webhook_url", "")
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


def is_low_signal_polymarket_market(question):
    """Suppress noisy first-run markets so the section stays trader-relevant."""
    text = (question or "").strip().lower()
    if not text:
        return True
    return any(pattern in text for pattern in LOW_SIGNAL_POLYMARKET_PATTERNS)


def format_demo_portfolio_section():
    """Show a realistic portfolio preview when Kalshi isn't configured yet."""
    total_unrealized = 0.0
    lines = []

    for pos in DEMO_PORTFOLIO:
        unrealized = pos["quantity"] * (pos["current_price"] - pos["entry_price"])
        total_unrealized += unrealized
        unrealized_str = f"+${unrealized:.0f}" if unrealized >= 0 else f"-${abs(unrealized):.0f}"
        cost = pos["quantity"] * pos["entry_price"]
        current_price_str = f"{pos['current_price'] * 100:.0f}c"
        lines.append(
            f"{pos['ticker']:20} {pos['side']:3}  "
            f"{emphasize(pos['quantity'])}@{emphasize(current_price_str)}  "
            f"${cost:.0f} cost  {emphasize(unrealized_str)} (exp: {pos['days_to_exp']}d)"
        )

    header = (
        f"PORTFOLIO P&L PREVIEW ({emphasize(len(DEMO_PORTFOLIO))} positions, "
        f"{emphasize(f'+${total_unrealized:.0f}') if total_unrealized >= 0 else emphasize(f'-${abs(total_unrealized):.0f}')} unrealized):"
    )
    return "\n".join([header] + lines)


def format_demo_edges_section():
    """Show a sample edge section before the rest of the stack is configured."""
    lines = ["TOP 3 EDGES PREVIEW (Kalshalyst):"]
    for i, edge in enumerate(DEMO_EDGES, 1):
        side = "YES" if edge["estimated_prob"] > edge["market_prob"] else "NO"
        market_prob_str = f"{edge['market_prob'] * 100:.0f}%"
        edge_str = f"+{edge['edge_pct']:.0f}%"
        confidence_str = f"{edge['confidence'] * 100:.0f}%"
        lines.append(
            f"{i}. {edge['ticker']:20}  {side} @ {emphasize(market_prob_str)}  "
            f"({emphasize(edge_str)} edge, {emphasize(confidence_str)} conf)"
        )
    return "\n".join(lines)


def format_demo_divergences_section():
    """Show sample divergence output for first-run preview."""
    lines = ["DIVERGENCES DEMO (Arbiter, Kalshi ↔ Polymarket):"]
    for div in DEMO_DIVERGENCES:
        kalshi_str = f"{div['kalshi_price'] * 100:.0f}%"
        pm_str = f"{div['polymarket_price'] * 100:.0f}%"
        spread_str = f"{div['spread_cents']}c"
        lines.append(
            f"{div['ticker']:20}  Kalshi {emphasize(kalshi_str)} "
            f"↔ PM {emphasize(pm_str)}  "
            f"({emphasize(spread_str)} spread)"
        )
    return "\n".join(lines)


def format_demo_xsignals_section():
    """Show sample Xpulse output when cache is missing."""
    lines = ["X SIGNALS DEMO (last 24h):"]
    for sig in DEMO_X_SIGNALS:
        reach = sig["reach"]
        reach_str = f"{reach/1000:.1f}K" if reach > 1000 else str(reach)
        confidence_str = f"{sig['confidence'] * 100:.0f}%"
        lines.append(
            f"{sig['signal'][:40]:40}  "
            f"({emphasize(confidence_str)} conf, {emphasize(reach_str)} reach)"
        )
    return "\n".join(lines)


def format_demo_polymarket_section():
    """Show sample Polymarket movers if public API fails."""
    lines = ["POLYMARKET DEMO (top 3 by volume):"]
    for market in DEMO_POLYMARKET:
        volume_str = f"${market['volume'] / 1_000_000:.1f}M"
        implied_prob_str = f"{market['implied_prob']:.0f}%"
        lines.append(
            f"{market['question'][:45]:45}  "
            f"{emphasize(volume_str)} vol, {emphasize(implied_prob_str)}"
        )
    return "\n".join(lines)


def format_portfolio_section(kalshi, config, debug=False):
    """Fetch and format portfolio section."""
    if not kalshi:
        return format_demo_portfolio_section()

    try:
        # Raw API call — avoids SDK v3 pydantic deserialization bug (Issue #9)
        resp = kalshi._portfolio_api.get_positions_without_preload_content(limit=100)
        raw_data = json.loads(resp.read())

        positions = (
            raw_data.get("event_positions")
            or raw_data.get("positions")
            or raw_data.get("market_positions")
            or []
        )

        # Filter to non-zero positions
        positions = [p for p in positions if int(float(p.get("position_fp") or p.get("position", 0) or 0)) != 0]

        if not positions:
            return "PORTFOLIO: (no positions)"

        total_unrealized = 0.0
        unknown_pricing = 0
        lines = [f"PORTFOLIO ({len(positions)} positions):"]

        for pos in positions:
            ticker = pos.get("ticker", "?")
            side = "YES" if pos.get("yes_price") else "NO"
            quantity = pos.get("quantity", 0)
            avg_price = pos.get("average_price", 0) / 100 if pos.get("average_price") else 0

            # Fetch market data ONCE per ticker (not twice)
            current_price = avg_price
            days_to_exp = 0
            try:
                market = kalshi.get_market(ticker)
                if market.get("last_price"):
                    current_price = market["last_price"] / 100
                exp_ts = market.get("close_datetime")
                if exp_ts:
                    exp_dt = datetime.fromisoformat(exp_ts.replace("Z", "+00:00"))
                    days_to_exp = (exp_dt - datetime.now(timezone.utc)).days
            except Exception:
                unknown_pricing += 1
                current_price = None

            cost = quantity * avg_price
            if current_price is None:
                line = (
                    f"{ticker:20} {side:3}  {emphasize(quantity)}@??¢  ${cost:.0f} cost  "
                    f"I don't know P&L (exp: {days_to_exp}d)"
                )
            else:
                unrealized = quantity * (current_price - avg_price)
                total_unrealized += unrealized
                unrealized_str = f"+${unrealized:.0f}" if unrealized >= 0 else f"-${abs(unrealized):.0f}"
                line = (
                    f"{ticker:20} {side:3}  {emphasize(quantity)}@{emphasize(f'{current_price*100:.0f}c')}  "
                    f"${cost:.0f} cost  {emphasize(unrealized_str):6} (exp: {days_to_exp}d)"
                )

            lines.append(line)

        if unknown_pricing:
            lines[0] = (
                f"PORTFOLIO ({len(positions)} positions): I don't know total unrealized P&L "
                f"because {unknown_pricing} market(s) could not be priced live."
            )
        else:
            total_str = f"+${total_unrealized:.0f}" if total_unrealized >= 0 else f"-${abs(total_unrealized):.0f}"
            lines[0] = (
                f"PORTFOLIO P&L ({emphasize(len(positions))} positions, {emphasize(total_str)} unrealized):"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Portfolio fetch error: {e}", debug)
        return format_demo_portfolio_section()


def format_kalshalyst_section(cache_path, config, debug=False):
    """Read Kalshalyst edges from cache."""
    freshness, age = check_cache_age(cache_path, 7200)  # 2 hour tolerance

    if freshness == "missing":
        return format_demo_edges_section()

    if freshness == "stale":
        log(f"Kalshalyst cache stale: {age}s old", debug)
        return format_demo_edges_section()

    try:
        with open(cache_path) as f:
            data = json.load(f)

        status = data.get("status", "")
        message = data.get("message", "")
        insights = data.get("insights", [])[:3]
        if not insights:
            if status == "demo":
                return format_demo_edges_section()
            clear_message = message or "No edge markets right now."
            return f"TOP EDGES: {clear_message} Check back later."

        if status == "demo":
            lines = [f"TOP {len(insights)} EDGES PREVIEW (Kalshalyst):"]
        else:
            lines = [f"TOP {len(insights)} EDGES (Kalshalyst):"]

        for i, edge in enumerate(insights, 1):
            ticker = edge.get("ticker", "?")
            market_prob = edge.get("market_prob", 0.5)
            estimated_prob = edge.get("estimated_prob", 0.5)

            # CODEX: if the estimate is above the market, the actionable side is YES.
            side = "YES" if estimated_prob > market_prob else "NO"

            edge_pct = edge.get("edge_pct", 0)
            confidence = edge.get("confidence", 0)

            lines.append(
                f"{i}. {ticker:20}  {side} @ {emphasize(f'{market_prob*100:.0f}%')}  "
                f"({emphasize(f'+{edge_pct:.0f}%')} edge, {emphasize(f'{confidence*100:.0f}%')} conf)"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Kalshalyst parse error: {e}", debug)
        return format_demo_edges_section()


def format_arbiter_section(cache_path, config, debug=False):
    """Read Arbiter divergences from cache."""
    freshness, age = check_cache_age(cache_path, 21600)  # 6 hour tolerance

    if freshness == "missing":
        return format_demo_divergences_section()

    if freshness == "stale":
        log(f"Arbiter cache stale: {age}s old", debug)
        return format_demo_divergences_section()

    try:
        with open(cache_path) as f:
            data = json.load(f)

        # Support both "divergences" (new) and "matches" (legacy) keys
        divergences = data.get("divergences", data.get("matches", []))[:2]
        if not divergences:
            return None  # suppress zero-result arbiter output

        lines = ["DIVERGENCES (Arbiter, Kalshi ↔ Polymarket):"]

        for div in divergences:
            ticker = div.get("ticker", div.get("kalshi_title", "?"))[:20]
            kalshi_p = div.get("kalshi_price", 0)
            pm_p = div.get("polymarket_price", div.get("pm_price", 0))

            # Handle both 0-1 float (new) and integer cents (legacy)
            if kalshi_p > 1:
                kalshi_p = kalshi_p / 100.0
            if pm_p > 1:
                pm_p = pm_p / 100.0

            spread_cents = div.get("spread_cents", div.get("delta", 0))

            lines.append(
                f"{ticker:20}  Kalshi {emphasize(f'{kalshi_p*100:.0f}%')} "
                f"↔ PM {emphasize(f'{pm_p*100:.0f}%')}  ({emphasize(f'{spread_cents}c')} spread)"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Arbiter parse error: {e}", debug)
        return format_demo_divergences_section()


def format_xpulse_section(cache_path, config, debug=False):
    """Read Xpulse signals from cache, filter to last 24h."""
    freshness, age = check_cache_age(cache_path, 14400)  # 4 hour tolerance

    if freshness == "missing":
        return format_demo_xsignals_section()

    if freshness == "stale":
        log(f"Xpulse cache stale: {age}s old", debug)
        return format_demo_xsignals_section()

    try:
        with open(cache_path) as f:
            data = json.load(f)

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(hours=24)

        signals = []
        for sig in data.get("signals", []):
            ts_str = sig.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if ts > cutoff:
                    signals.append(sig)
            except Exception:
                pass

        # Sort by confidence, take top 2
        signals.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        signals = signals[:2]

        if not signals:
            return "X SIGNALS: none found (check Xpulse directly)"

        lines = ["X SIGNALS (last 24h):"]

        for sig in signals:
            signal_text = sig.get("signal", "?")
            confidence = sig.get("confidence", 0)
            reach = sig.get("reach", 0)
            reach_str = f"{reach/1000:.1f}K" if reach > 1000 else str(reach)
            confidence_str = f"{confidence*100:.0f}%"
            lines.append(
                f"{signal_text[:40]:40}  "
                f"({emphasize(confidence_str)} conf, {emphasize(reach_str)} reach)"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Xpulse parse error: {e}", debug)
        return format_demo_xsignals_section()


def format_crypto_section(config, debug=False):
    """Fetch crypto prices from Coinbase."""
    if not requests:
        return "CRYPTO: unavailable (requests library not installed)"

    coinbase_cfg = config.get("coinbase", {})
    if not coinbase_cfg.get("enabled"):
        return "CRYPTO: unavailable (configure Coinbase API for crypto prices)"

    api_key = coinbase_cfg.get("api_key")
    if not api_key:
        return "CRYPTO: unavailable (Coinbase API key not configured)"

    tickers = coinbase_cfg.get("tickers", ["BTC", "ETH"])

    lines = ["CRYPTO:"]
    prices = []

    for ticker in tickers:
        try:
            url = f"https://api.coinbase.com/v2/prices/{ticker}-USD/spot"
            resp = requests.get(url, timeout=3, headers={"Authorization": f"Bearer {api_key}"})
            resp.raise_for_status()

            data = resp.json()
            price = float(data.get("data", {}).get("amount", 0))
            prices.append(f"{ticker:5}  ${price:10,.2f}")

        except Exception as e:
            log(f"Crypto fetch error ({ticker}): {e}", debug)

    if not prices:
        return "CRYPTO: unavailable (Coinbase API error)"

    # Format as pairs
    lines = ["CRYPTO:"]
    for i in range(0, len(prices), 2):
        if i + 1 < len(prices):
            lines.append(f"{prices[i]}  | {prices[i+1]}")
        else:
            lines.append(prices[i])

    return "\n".join(lines)


def format_polymarket_section(config, debug=False):
    """Fetch top Polymarket markets."""
    if not requests:
        return "POLYMARKET: unavailable (requests library not installed)"

    try:
        # Use Gamma API (market listing), not CLOB API (order-book focused)
        url = "https://gamma-api.polymarket.com/markets?closed=false&limit=10&order=volume&ascending=false"
        resp = requests.get(url, timeout=10, headers={
            "Accept": "application/json",
            "User-Agent": "OpenClaw-MorningBrief/1.0",
        })
        resp.raise_for_status()

        data = resp.json()
        markets = data if isinstance(data, list) else data.get("data", [])
        if not markets:
            return format_demo_polymarket_section()

        filtered_markets = []
        for market in markets:
            question = market.get("question", market.get("title", ""))
            if is_low_signal_polymarket_market(question):
                continue
            filtered_markets.append(market)
            if len(filtered_markets) == 3:
                break

        if len(filtered_markets) < 3:
            return format_demo_polymarket_section()

        markets = filtered_markets
        if all(float(m.get("volume", 0) or 0) < 1000 for m in markets):
            return format_demo_polymarket_section()

        lines = ["POLYMARKET (top 3 by volume):"]

        for market in markets:
            question = market.get("question", market.get("title", "?"))[:50]
            volume = float(market.get("volume", 0) or 0)

            # Get implied probability from outcomePrices
            prices_raw = market.get("outcomePrices", "[]")
            if isinstance(prices_raw, str):
                try:
                    prices_raw = json.loads(prices_raw)
                except Exception:
                    prices_raw = []

            if prices_raw:
                implied_prob = float(prices_raw[0]) * 100
            else:
                implied_prob = 50

            volume_m = volume / 1_000_000 if volume > 0 else 0

            lines.append(
                f"{question:45}  {emphasize(f'${volume_m:.1f}M')} vol, "
                f"{emphasize(f'{implied_prob:.0f}%')}"
            )

        return "\n".join(lines)

    except Exception as e:
        log(f"Polymarket fetch error: {e}", debug)
        return format_demo_polymarket_section()


def build_morning_brief(config, kalshi=None, debug=False):
    """Build complete morning brief."""
    now = datetime.now()
    header = f"MARKET MORNING BRIEF — {now.strftime('%A, %B %d, %Y')}"

    sections = [header]
    if not kalshi:
        sections.append(
            "FIRST RUN PREVIEW: sample portfolio and edge sections are shown so you can see the brief before wiring Kalshi credentials."
        )

    # Portfolio (required)
    if config.get("include", {}).get("portfolio", True):
        portfolio = format_portfolio_section(kalshi, config, debug)
        sections.append(portfolio)

    # Kalshalyst edges (optional)
    if config.get("include", {}).get("kalshalyst_edges", True):
        cache_path = config.get("cache_paths", {}).get("kalshalyst")
        if cache_path:
            edges = format_kalshalyst_section(cache_path, config, debug)
            sections.append(edges)

    # Arbiter divergences (optional)
    if config.get("include", {}).get("arbiter_divergences", True):
        cache_path = config.get("cache_paths", {}).get("arbiter")
        if cache_path:
            divergences = format_arbiter_section(cache_path, config, debug)
            if divergences:
                sections.append(divergences)

    # Xpulse signals (optional)
    if config.get("include", {}).get("xpulse_signals", True):
        cache_path = config.get("cache_paths", {}).get("xpulse")
        if cache_path:
            signals = format_xpulse_section(cache_path, config, debug)
            sections.append(signals)

    # Crypto (optional)
    if config.get("include", {}).get("crypto", False):
        crypto = format_crypto_section(config, debug)
        sections.append(crypto)

    # Polymarket (optional)
    if config.get("include", {}).get("polymarket", True):
        pm = format_polymarket_section(config, debug)
        sections.append(pm)

    return "\n\n".join(sections)


def load_config(config_path=None):
    """Load config from YAML file or return defaults."""
    if config_path and Path(config_path).exists():
        if yaml:
            with open(config_path) as f:
                data = yaml.safe_load(f)
                return data.get("market_morning_brief", {})

    # Default config
    return {
        "enabled": True,
        "kalshi": {"enabled": False},
        "cache_paths": {
            "kalshalyst": str(Path.home() / ".openclaw" / "state" / "kalshalyst_cache.json"),
            "arbiter": str(Path.home() / ".openclaw" / "state" / "arbiter_cache.json"),
            "xpulse": str(Path.home() / ".openclaw" / "state" / "x_signal_cache.json"),
        },
        "include": {
            "portfolio": True,
            "kalshalyst_edges": True,
            "arbiter_divergences": True,
            "xpulse_signals": True,
            "crypto": False,
            "polymarket": True,
        },
    }


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Market Morning Brief")
    parser.add_argument("--config", help="Path to config.yaml")
    parser.add_argument("--dry-run", action="store_true", help="Don't send, just print")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--test-slack", action="store_true", help="Send a test Slack notification and exit")
    args = parser.parse_args()

    if args.test_slack:
        _notify_slack("MORNING-BRIEF TEST: Slack notification is working.")
        print("Sent test Slack notification.")
        return

    config = load_config(args.config)

    # Initialize Kalshi client if configured
    kalshi = None
    if config.get("kalshi", {}).get("enabled") and KalshiClient:
        try:
            api_key_id = config["kalshi"].get("api_key_id")
            private_key_file = config["kalshi"].get("private_key_file")

            if api_key_id and private_key_file:
                base_url = "https://api.elections.kalshi.com/trade-api/v2"
                sdk_config = KalshiConfiguration(host=base_url)
                with open(private_key_file) as f:
                    sdk_config.private_key_pem = f.read()
                sdk_config.api_key_id = api_key_id
                kalshi = KalshiClient(sdk_config)
                sdk_config.private_key_pem = None
        except Exception as e:
            log(f"Kalshi init error: {e}", args.debug)

    brief = build_morning_brief(config, kalshi, debug=args.debug)

    print(brief)

    # Send to Slack if configured
    _notify_slack(brief)

    if args.debug:
        print("\n[DEBUG] Brief generated successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
