#!/usr/bin/env python3
"""
BMI Alert Workflow — Fetches BMI data and sends an alert via openclaw.

Set OPENCLAW_NOTIFY_CHANNEL (e.g. "telegram", "slack") and OPENCLAW_NOTIFY_TARGET
to enable message delivery. Without these, the alert is printed to stdout only.
"""
import os
import sys
import json
import subprocess

# Local tool imports — require PYTHONPATH={baseDir}/tools
try:
    import btc_momentum
except ImportError:
    # If not in PYTHONPATH yet, try to find it relative to this script
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    import btc_momentum

# Portfolio tokens configuration — default path in workspace
PORTFOLIO_FILE = os.path.expanduser("~/.openclaw/workspace/portfolio_tokens.json")
STATE_FILE = os.path.expanduser("~/.openclaw/workspace/memory/bmi_alert_state.json")

def get_bmi():
    """Fetch BMI signal by calling btc_momentum logic directly."""
    # Use the function from btc_momentum if it provides one, 
    # or run it as a subprocess if that's more reliable.
    # Here we run as subprocess to maintain existing behavior but use the local path.
    script_path = os.path.join(os.path.dirname(__file__), "btc_momentum.py")
    result = subprocess.run(
        [sys.executable, script_path, "--json"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"BMI script failed: {result.stderr}")
    data = json.loads(result.stdout)
    return {
        "bmi": data["bmi"],
        "signal": data["signal"],
        "btc_24h_pct": data["btc_24h_pct"]
    }

def get_portfolio_tokens():
    """Load portfolio tokens from configuration file."""
    try:
        with open(PORTFOLIO_FILE) as f:
            data = json.load(f)
        return data.get("portfolio_tokens", [])
    except Exception as e:
        print(f"Warning: Could not load portfolio tokens: {e}")
        return []

def get_top_tokens(top=5, bearish=False):
    """Fetch top gainers/losers from CoinGecko."""
    try:
        import requests
        resp = requests.get(
            "https://api.coingecko.com/api/v3/coins/markets",
            params={"vs_currency": "usd", "order": "market_cap_desc", "per_page": 100, "page": 1},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        coins = [c for c in data if c.get("price_change_percentage_24h")]
        
        if bearish:
            sorted_coins = sorted(coins, key=lambda x: x["price_change_percentage_24h"])[:top]
        else:
            sorted_coins = sorted(coins, key=lambda x: x["price_change_percentage_24h"], reverse=True)[:top]
        
        return [{"symbol": c["symbol"].upper(), "pct_24h": c["price_change_percentage_24h"]} for c in sorted_coins]
    except Exception as e:
        print(f"Warning: Could not fetch tokens: {e}")
        return []

def send_alert(message):
    """Send alert via openclaw using the configured channel and target.

    Reads OPENCLAW_NOTIFY_CHANNEL and OPENCLAW_NOTIFY_TARGET from the environment.
    If either is unset, prints the message to stdout and skips the send.
    """
    channel = os.environ.get("OPENCLAW_NOTIFY_CHANNEL", "")
    target = os.environ.get("OPENCLAW_NOTIFY_TARGET", "")
    if not channel or not target:
        print(
            "Warning: OPENCLAW_NOTIFY_CHANNEL and OPENCLAW_NOTIFY_TARGET must both be set to send alerts. Printing to stdout.",
            file=sys.stderr,
        )
        print(message)
        return
    subprocess.run(
        ["openclaw", "message", "send", "--channel", channel, "--target", target, "--message", message],
        capture_output=True,
        text=True
    )
    print(message)

def load_state():
    try:
        with open(STATE_FILE) as f:
            return json.load(f)
    except Exception:
        return {"last_direction": None}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

def main():
    bmi_data = get_bmi()
    bmi_value = bmi_data['bmi']
    signal = bmi_data['signal']
    btc_24h = bmi_data['btc_24h_pct']
    
    # Determine direction
    if bmi_value >= 20:
        direction = "BULLISH"
        header = "🚀 BMI Alert"
        tokens = get_top_tokens(5, bearish=False)
        footer = "Consider running the LONG workflow."
    elif bmi_value <= -20:
        direction = "BEARISH"
        header = "📉 BMI Alert"
        tokens = get_top_tokens(5, bearish=True)
        footer = "Consider running the SHORT workflow."
    else:
        direction = "NEUTRAL"
        header = "⏸ BMI Alert"
        tokens = []
        footer = "Market is neutral. No action needed."

    # Only alert if the direction has changed
    state = load_state()
    if state.get("last_direction") == direction:
        print(f"BMI {bmi_value} ({direction}) — no change, skipping alert.")
        return

    # Direction changed — send alert and save new state
    save_state({"last_direction": direction})

    message = f"{header}: {bmi_value} ({direction}) | BTC 24h: {btc_24h:+.2f}%\n\n"
    
    # Use portfolio tokens instead of CoinGecko top tokens
    portfolio_tokens = get_portfolio_tokens()
    if portfolio_tokens:
        message += "Portfolio Tokens:\n"
        for t in portfolio_tokens:
            message += f"• {t['symbol']}: {t['pct_24h']:+.2f}%\n"
    elif tokens:
        message += "Top 5 Bullish Tokens:\n" if direction == "BULLISH" else "Top 5 Bearish Tokens:\n"
        for t in tokens:
            message += f"• {t['symbol']}: {t['pct_24h']:+.2f}%\n"
    
    message += f"\n{footer}"
    send_alert(message)

if __name__ == "__main__":
    main()
