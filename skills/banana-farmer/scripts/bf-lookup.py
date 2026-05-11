#!/usr/bin/env python3
"""Look up a single ticker on Banana Farmer for momentum score, technicals, and AI analysis."""

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


def format_signal(sym, sig):
    lines = [f"=== ${sym} ==="]

    score = sig.get('score', 0)
    badge = sig.get('badge', 'unknown')
    lines.append(f"Score: {score}/100 ({badge.upper()})")

    # Price
    techs = sig.get('technicals', {})
    price = techs.get('price') or sig.get('currentPrice')
    if price:
        lines.append(f"Price: ${price:,.2f}")

    # Movement
    move = sig.get('movement', {})
    c1d = move.get('priceChange1d', techs.get('change1d', ''))
    c5d = move.get('priceChange5d', techs.get('change5d', ''))
    if c1d or c5d:
        parts = []
        if c1d:
            parts.append(f"1d: {c1d}")
        if c5d:
            parts.append(f"5d: {c5d}")
        lines.append(f"Change: {' | '.join(parts)}")

    # Technicals
    if techs:
        tech_parts = []
        if techs.get('rsi'):
            rsi = techs['rsi']
            label = " (OVERBOUGHT)" if rsi > 70 else " (OVERSOLD)" if rsi < 30 else ""
            tech_parts.append(f"RSI {rsi}{label}")
        if techs.get('coilScore'):
            coil = techs['coilScore']
            label = " (COILED)" if coil >= 70 else ""
            tech_parts.append(f"Coil {coil}{label}")
        if techs.get('aboveEma20') is not None:
            tech_parts.append(f"Above EMA20: {'Yes' if techs['aboveEma20'] else 'No'}")
        if techs.get('aboveEma50') is not None:
            tech_parts.append(f"Above EMA50: {'Yes' if techs['aboveEma50'] else 'No'}")
        if techs.get('prox52wHigh'):
            tech_parts.append(f"52w High Prox: {techs['prox52wHigh']:.0%}")
        if tech_parts:
            lines.append(f"Technicals: {' | '.join(tech_parts)}")
        if techs.get('patterns'):
            lines.append(f"Patterns: {', '.join(techs['patterns'])}")

    # Volatility
    vol = sig.get('volatility', {})
    if vol:
        vol_parts = []
        if vol.get('avgDailyRangePct'):
            vol_parts.append(f"Avg Daily Range: {vol['avgDailyRangePct']}")
        if vol.get('maxDrawdownPct'):
            vol_parts.append(f"Max Drawdown: {vol['maxDrawdownPct']}")
        if vol_parts:
            lines.append(f"Volatility: {' | '.join(vol_parts)}")

    # Scoring breakdown
    scoring = sig.get('scoring', {})
    if scoring:
        parts = []
        if scoring.get('technical'):
            parts.append(f"Technical: {scoring['technical']}")
        if scoring.get('momentum'):
            parts.append(f"Momentum: {scoring['momentum']}")
        if scoring.get('social'):
            parts.append(f"Social: {scoring['social']}")
        if parts:
            lines.append(f"Score Breakdown: {' | '.join(parts)}")

    # Drivers
    drivers = sig.get('drivers', [])
    if drivers:
        lines.append(f"Drivers: {', '.join(drivers[:5])}")

    # AI Summary
    ai = sig.get('aiSummary', {})
    if ai:
        if ai.get('whatItDoes'):
            lines.append(f"\nWhat's happening: {ai['whatItDoes']}")
        if ai.get('bullets'):
            for b in ai['bullets'][:4]:
                lines.append(f"  - {b}")

    # Social snippets
    social = sig.get('social', {})
    if social:
        if social.get('bullCase'):
            lines.append(f"\nBull case: {social['bullCase']}")
        if social.get('bearCase'):
            lines.append(f"Bear case: {social['bearCase']}")
        if social.get('watchFor'):
            lines.append(f"Watch for: {social['watchFor']}")

    # Reliability
    rel = sig.get('reliability', {})
    if rel and rel.get('winRate5d'):
        lines.append(f"\nReliability: {rel['winRate5d']}% 5d win rate (sample: {rel.get('sampleSize', '?')})")

    return '\n'.join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bf-lookup.py SYMBOL [SYMBOL2 ...]")
        print("Example: python3 bf-lookup.py AAPL TSLA NVDA")
        sys.exit(1)

    symbols = [s.upper().replace('$', '') for s in sys.argv[1:]]

    for i, sym in enumerate(symbols):
        if i > 0:
            print()
        try:
            data = bf_get(f'signals/{sym}')
            if not data or not data.get('score'):
                print(f"${sym}: No signal data available")
                continue
            print(format_signal(sym, data))
        except Exception as e:
            print(f"${sym}: Error — {e}")


if __name__ == '__main__':
    main()
