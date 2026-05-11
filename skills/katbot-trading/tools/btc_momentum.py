#!/usr/bin/env python3
"""
btc_momentum.py — BTC Momentum Index (BMI)

Fetches 24 hourly BTC/USD candles from Kraken, computes a momentum score
from -100 (max bearish) to +100 (max bullish), and evaluates open positions
against that momentum to support trade decisions.

Usage:
    python btc_momentum.py                        # print full report
    python btc_momentum.py --json                 # machine-readable output
    python btc_momentum.py --send                 # send via openclaw (requires OPENCLAW_NOTIFY_CHANNEL + OPENCLAW_NOTIFY_TARGET)
"""

import argparse
import json
import math
import os
import pathlib
import subprocess
import sys
import time
from typing import Optional

import requests

KRAKEN_OHLC_URL = "https://api.kraken.com/0/public/OHLC"
BTC_PAIR = "XBTUSD"
INTERVAL = 60  # 1-hour candles
LOOKBACK = 24  # candles

# Messaging — read channel and target from env vars so alerts work with any openclaw channel.
# Set OPENCLAW_NOTIFY_CHANNEL (e.g. "telegram", "slack", "discord") and
# OPENCLAW_NOTIFY_TARGET (e.g. a chat/user ID) to enable --send.
CHANNEL = os.environ.get("OPENCLAW_NOTIFY_CHANNEL", "")
TARGET_ID = os.environ.get("OPENCLAW_NOTIFY_TARGET", "")

# Resolve tools directory dynamically from this file's location — no hardcoded paths
_TOOLS_DIR = str(pathlib.Path(__file__).parent.resolve())


# ─── Data Fetch ───────────────────────────────────────────────────────────────

def fetch_candles() -> list[dict]:
    """Fetch last 24 hourly candles from Kraken for BTC/USD."""
    since = int(time.time()) - (LOOKBACK + 2) * 3600
    resp = requests.get(KRAKEN_OHLC_URL, params={"pair": BTC_PAIR, "interval": INTERVAL, "since": since}, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise ValueError(f"Kraken error: {data['error']}")
    raw = list(data["result"].values())[0]
    candles = [
        {
            "time": int(c[0]),
            "open": float(c[1]),
            "high": float(c[2]),
            "low": float(c[3]),
            "close": float(c[4]),
            "volume": float(c[6]),
        }
        for c in raw
    ]
    return candles[-LOOKBACK:]  # last 24


# ─── Indicators ───────────────────────────────────────────────────────────────

def exponential_weights(n: int) -> list[float]:
    """Exponential weights — recent candles matter more. Sums to 1."""
    raw = [math.exp(i / (n / 3)) for i in range(n)]
    total = sum(raw)
    return [w / total for w in raw]


def compute_rsi(closes: list[float], period: int = 14) -> float:
    if len(closes) < period + 1:
        return 50.0
    deltas = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0) for d in deltas[-period:]]
    losses = [abs(min(d, 0)) for d in deltas[-period:]]
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def compute_macd(closes: list[float]) -> dict:
    """Returns MACD line, signal, histogram."""
    def ema(data, period):
        k = 2 / (period + 1)
        result = [data[0]]
        for v in data[1:]:
            result.append(v * k + result[-1] * (1 - k))
        return result

    if len(closes) < 26:
        return {"macd": 0, "signal": 0, "histogram": 0}

    ema12 = ema(closes, 12)
    ema26 = ema(closes, 26)
    macd_line = [e12 - e26 for e12, e26 in zip(ema12[-len(ema26):], ema26)]
    signal = ema(macd_line, 9)
    hist = macd_line[-1] - signal[-1]
    return {"macd": macd_line[-1], "signal": signal[-1], "histogram": hist}


def candle_body_bias(candles: list[dict], weights: list[float]) -> float:
    """
    Weighted ratio of green (bullish) candle bodies vs total.
    Returns -1.0 (all bearish) to +1.0 (all bullish).
    """
    score = 0.0
    for c, w in zip(candles, weights):
        if c["close"] > c["open"]:
            score += w
        elif c["close"] < c["open"]:
            score -= w
    return score  # already weighted, range roughly -1 to +1


def volume_trend(candles: list[dict], weights: list[float]) -> float:
    """
    Compare volume-weighted by candle direction.
    Returns -1.0 to +1.0: positive = more volume on up candles.
    """
    up_vol = sum(c["volume"] * w for c, w in zip(candles, weights) if c["close"] >= c["open"])
    down_vol = sum(c["volume"] * w for c, w in zip(candles, weights) if c["close"] < c["open"])
    total = up_vol + down_vol
    if total == 0:
        return 0.0
    return (up_vol - down_vol) / total


# ─── Score Computation ────────────────────────────────────────────────────────

def compute_bmi(candles: list[dict]) -> dict:
    closes = [c["close"] for c in candles]
    weights = exponential_weights(len(candles))

    # 1. Price trend: weighted average of hourly returns
    returns = [(closes[i] - closes[i - 1]) / closes[i - 1] for i in range(1, len(closes))]
    w_returns = weights[1:]  # align
    w_total = sum(w_returns)
    weighted_return = sum(r * w for r, w in zip(returns, w_returns)) / w_total
    # Normalize: ±0.5% per hour → ±100 score
    trend_score = max(-1.0, min(1.0, weighted_return / 0.005))

    # 2. RSI: map 0-100 → -1 to +1 (50 = 0)
    rsi = compute_rsi(closes)
    rsi_score = (rsi - 50) / 50  # -1 to +1

    # 3. MACD histogram direction normalized
    macd_data = compute_macd(closes)
    hist = macd_data["histogram"]
    price = closes[-1]
    macd_score = max(-1.0, min(1.0, (hist / price) * 5000))  # scale to asset price

    # 4. Candle body bias (already -1 to +1)
    body_score = candle_body_bias(candles, weights)

    # 5. Volume trend (already -1 to +1)
    vol_score = volume_trend(candles, weights)

    # Weighted composite (recent-heavy signals matter more)
    # Trend and MACD are most actionable; RSI is context
    W = {"trend": 0.30, "macd": 0.25, "body": 0.20, "volume": 0.15, "rsi": 0.10}
    composite = (
        trend_score * W["trend"] +
        macd_score  * W["macd"] +
        body_score  * W["body"] +
        vol_score   * W["volume"] +
        rsi_score   * W["rsi"]
    )

    bmi = round(composite * 100)

    # Signal label
    if bmi >= 50:      signal = "STRONGLY BULLISH"
    elif bmi >= 20:    signal = "BULLISH"
    elif bmi >= 5:     signal = "MILDLY BULLISH"
    elif bmi > -5:     signal = "NEUTRAL"
    elif bmi > -20:    signal = "MILDLY BEARISH"
    elif bmi > -50:    signal = "BEARISH"
    else:              signal = "STRONGLY BEARISH"

    # New position bias
    if bmi >= 20:      bias = "LONG"
    elif bmi <= -20:   bias = "SHORT"
    else:              bias = "FLAT"

    return {
        "bmi": bmi,
        "signal": signal,
        "bias": bias,
        "open_new_position": abs(bmi) >= 20,
        "btc_price": closes[-1],
        "btc_24h_pct": round((closes[-1] - closes[0]) / closes[0] * 100, 2),
        "rsi": round(rsi, 2),
        "macd_histogram": round(macd_data["histogram"], 2),
        "components": {
            "trend":  round(trend_score * 100),
            "macd":   round(macd_score * 100),
            "body":   round(body_score * 100),
            "volume": round(vol_score * 100),
            "rsi":    round(rsi_score * 100),
        }
    }


# ─── Position Health ──────────────────────────────────────────────────────────

def evaluate_positions(bmi_data: dict, positions: list[dict]) -> list[dict]:
    bmi = bmi_data["bmi"]
    results = []
    for pos in positions:
        side = pos["side"].lower()
        pnl = float(pos.get("unrealized_pnl", 0))
        pct = float(pos.get("unrealized_pnl_pct", 0))

        # Alignment: long + bullish OR short + bearish = aligned
        if side == "long":
            aligned = bmi >= 0
        else:
            aligned = bmi <= 0

        # Health: is position making money AND aligned?
        if aligned and pnl > 0:
            health = "HEALTHY"
            action = "HOLD"
        elif aligned and pnl <= 0:
            health = "WATCH"
            action = "MONITOR — aligned with market but underwater"
        elif not aligned and pnl > 0:
            health = "WATCH"
            action = "MONITOR — profitable but fighting market momentum"
        else:
            health = "AT RISK"
            action = "CONSIDER CLOSING — fighting momentum and losing"

        results.append({
            "symbol": pos["symbol"],
            "side": side,
            "pnl_usd": round(pnl, 2),
            "pnl_pct": round(pct, 2),
            "aligned_with_bmi": aligned,
            "health": health,
            "action": action,
        })
    return results


def get_open_positions() -> list[dict]:
    """Fetch open positions via katbot_client using the current Python interpreter."""
    script = f"""
import sys, json
sys.path.insert(0, {_TOOLS_DIR!r})
from katbot_client import get_token, get_portfolio, get_config
token = get_token()
config = get_config()
portfolio_id = config.get('portfolio_id')
if not portfolio_id:
    print('[]')
else:
    p = get_portfolio(token, portfolio_id)
    print(json.dumps(p.get('open_positions', [])))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True, text=True, cwd=_TOOLS_DIR,
        env={**os.environ, "PYTHONPATH": _TOOLS_DIR},
    )
    if result.returncode != 0:
        return []
    for line in result.stdout.splitlines():
        if line.startswith("["):
            import json as _json
            return _json.loads(line)
    return []


# ─── Report ───────────────────────────────────────────────────────────────────

def format_report(bmi_data: dict, position_health: list[dict]) -> str:
    bmi = bmi_data["bmi"]
    bar_len = abs(bmi) // 5
    bar = ("█" * bar_len).ljust(20)
    direction = "▶" if bmi >= 0 else "◀"

    lines = [
        f"📡 BTC Momentum Index: {bmi:+d} — {bmi_data['signal']}",
        f"   {direction} [{bar}]",
        f"   BTC: ${bmi_data['btc_price']:,.0f} | 24h: {bmi_data['btc_24h_pct']:+.2f}%",
        f"   RSI: {bmi_data['rsi']} | MACD hist: {bmi_data['macd_histogram']}",
        f"",
        f"🎯 Bias: {bmi_data['bias']} | New position: {'✅ YES' if bmi_data['open_new_position'] else '⛔ NO'}",
    ]

    if position_health:
        lines.append("")
        lines.append("📋 Position Health:")
        for p in position_health:
            icon = "✅" if p["health"] == "HEALTHY" else ("⚠️" if p["health"] == "WATCH" else "🚨")
            lines.append(f"   {icon} {p['symbol']} {p['side'].upper()}: ${p['pnl_usd']:+.2f} ({p['pnl_pct']:+.2f}%) — {p['action']}")

    return "\n".join(lines)


def send_message(msg: str):
    if not CHANNEL or not TARGET_ID:
        print(
            "Warning: OPENCLAW_NOTIFY_CHANNEL and OPENCLAW_NOTIFY_TARGET must both be set to send messages. Skipping.",
            file=sys.stderr,
        )
        return
    subprocess.run(
        ["openclaw", "message", "send", "--channel", CHANNEL, "--target", TARGET_ID, "--message", msg],
        capture_output=True, text=True
    )


# ─── Main ─────────────────────────────────────────────────────────────────────

def run(send: bool = False, as_json: bool = False) -> dict:
    candles = fetch_candles()
    bmi_data = compute_bmi(candles)
    positions = get_open_positions()
    position_health = evaluate_positions(bmi_data, positions)
    bmi_data["position_health"] = position_health

    if as_json:
        print(json.dumps(bmi_data, indent=2))
    else:
        report = format_report(bmi_data, position_health)
        print(report)
        if send:
            send_message(report)

    return bmi_data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--send", action="store_true", help="Send to Telegram")
    parser.add_argument("--json", action="store_true", dest="as_json", help="JSON output")
    args = parser.parse_args()
    run(send=args.send, as_json=args.as_json)
