#!/usr/bin/env python3
"""Compare momentum signals between two or more tickers side-by-side."""

import json
import os
import ssl
import sys
import urllib.request

BF_API_KEY = os.environ.get('BF_API_KEY', '')
BF_BASE = 'https://bananafarmer.app/api/bot/v1'


def bf_get(endpoint, timeout=15):
    if not BF_API_KEY:
        print("ERROR: BF_API_KEY not set. Get your key at https://bananafarmer.app")
        sys.exit(1)
    url = f"{BF_BASE}/{endpoint}"
    headers = {'x-bf-bot-key': BF_API_KEY, 'User-Agent': 'BananaFarmerBot/1.0'}
    req = urllib.request.Request(url, headers=headers)
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body = json.loads(resp.read().decode('utf-8'))
            return body.get('data', body)
    except urllib.error.HTTPError as e:
        if e.code == 403:
            try:
                err_body = json.loads(e.read().decode('utf-8'))
                err_code = err_body.get('error', {}).get('code', '')
            except Exception:
                err_code = ''
            if err_code == 'TIER_ACCESS_DENIED':
                print(f"ERROR: This endpoint requires a higher tier. Upgrade at https://bananafarmer.app/pricing")
                print(f"  Endpoint: /{endpoint}")
                print(f"  Free tier has access to: health, discover, signals/top, requests/mine")
                return None
            print(f"ERROR: 403 Forbidden on /{endpoint}. Check your API key and User-Agent header.")
            return None
        elif e.code == 429:
            print(f"ERROR: Rate limit exceeded. Wait a moment and try again.")
            return None
        raise


def compare(symbols):
    signals = {}
    for sym in symbols:
        try:
            data = bf_get(f'signals/{sym}')
            if data and data.get('score'):
                signals[sym] = data
            else:
                print(f"  ${sym}: No signal data")
        except Exception as e:
            print(f"  ${sym}: Error — {e}")

    if len(signals) < 2:
        print("Need at least 2 tickers with data to compare.")
        return

    # Header
    syms = list(signals.keys())
    col_width = max(12, max(len(s) + 1 for s in syms))
    header = f"{'Metric':<22}" + ''.join(f"${s:<{col_width}}" for s in syms)
    print(header)
    print("-" * len(header))

    # Rows
    def row(label, getter):
        vals = []
        for s in syms:
            v = getter(signals[s])
            vals.append(str(v) if v is not None else "—")
        print(f"{label:<22}" + ''.join(f"{v:<{col_width}}" for v in vals))

    row("Score", lambda d: d.get('score'))
    row("Badge", lambda d: d.get('badge', '').upper())

    # Price
    row("Price", lambda d: f"${d.get('technicals', {}).get('price') or d.get('currentPrice', 0):,.2f}"
        if (d.get('technicals', {}).get('price') or d.get('currentPrice'))
        else "—")

    # Technicals
    row("RSI", lambda d: d.get('technicals', {}).get('rsi'))
    row("Coil Score", lambda d: d.get('technicals', {}).get('coilScore'))
    row("Above EMA20", lambda d: "Yes" if d.get('technicals', {}).get('aboveEma20') else
        "No" if d.get('technicals', {}).get('aboveEma20') is not None else None)
    row("Above EMA50", lambda d: "Yes" if d.get('technicals', {}).get('aboveEma50') else
        "No" if d.get('technicals', {}).get('aboveEma50') is not None else None)
    row("52w High Prox", lambda d: f"{d.get('technicals', {}).get('prox52wHigh', 0):.0%}"
        if d.get('technicals', {}).get('prox52wHigh') else None)

    # Movement
    row("1d Change", lambda d: d.get('movement', {}).get('priceChange1d',
        d.get('technicals', {}).get('change1d')))
    row("5d Change", lambda d: d.get('movement', {}).get('priceChange5d',
        d.get('technicals', {}).get('change5d')))

    # Scoring breakdown
    row("Technical Score", lambda d: d.get('scoring', {}).get('technical'))
    row("Momentum Score", lambda d: d.get('scoring', {}).get('momentum'))
    row("Social Score", lambda d: d.get('scoring', {}).get('social'))

    # Volatility
    row("Avg Daily Range", lambda d: f"{d.get('volatility', {}).get('avgDailyRangePct', 0):.1f}%"
        if d.get('volatility', {}).get('avgDailyRangePct') else None)
    row("Max Drawdown", lambda d: f"{d.get('volatility', {}).get('maxDrawdownPct', 0):.1f}%"
        if d.get('volatility', {}).get('maxDrawdownPct') else None)

    # Verdict
    print()
    best = max(syms, key=lambda s: signals[s].get('score', 0))
    worst = min(syms, key=lambda s: signals[s].get('score', 0))
    print(f"Strongest momentum: ${best} (score {signals[best].get('score')})")
    print(f"Weakest momentum: ${worst} (score {signals[worst].get('score')})")

    # Risk comparison
    high_rsi = [s for s in syms if (signals[s].get('technicals', {}).get('rsi') or 0) > 70]
    high_coil = [s for s in syms if (signals[s].get('technicals', {}).get('coilScore') or 0) >= 70]
    if high_rsi:
        print(f"Overbought (RSI>70): {', '.join('$'+s for s in high_rsi)}")
    if high_coil:
        print(f"Coiled (potential breakout): {', '.join('$'+s for s in high_coil)}")


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 bf-compare.py SYMBOL1 SYMBOL2 [SYMBOL3 ...]")
        print("Example: python3 bf-compare.py AAPL MSFT NVDA")
        sys.exit(1)

    symbols = [s.upper().replace('$', '') for s in sys.argv[1:] if not s.startswith('-')]

    as_json = '--json' in sys.argv
    if as_json:
        signals = {}
        for sym in symbols:
            try:
                data = bf_get(f'signals/{sym}')
                if data and data.get('score'):
                    signals[sym] = {
                        'score': data.get('score'),
                        'badge': data.get('badge'),
                        'rsi': data.get('technicals', {}).get('rsi'),
                        'coilScore': data.get('technicals', {}).get('coilScore'),
                    }
            except Exception:
                pass
        print(json.dumps(signals, indent=2))
    else:
        print(f"MOMENTUM COMPARISON: {' vs '.join('$'+s for s in symbols)}")
        print("=" * 60)
        print()
        compare(symbols)


if __name__ == '__main__':
    main()
