#!/usr/bin/env python3
"""Portfolio intelligence — cross-reference holdings against Banana Farmer momentum signals."""

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


def generate_brief(accounts, account_filter=None):
    if account_filter:
        accounts = [a for a in accounts if account_filter.lower() in a['id'].lower()
                     or account_filter.lower() in a['name'].lower()]

    # Collect all symbols
    all_symbols = set()
    for acct in accounts:
        for h in acct.get('holdings', []):
            all_symbols.add(h['symbol'])

    # Batch lookup
    cache = {}
    for sym in sorted(all_symbols):
        try:
            data = bf_get(f'signals/{sym}')
            if data and data.get('score'):
                cache[sym] = data
        except Exception:
            pass

    # Market status
    try:
        health = bf_get('health')
        market_status = health.get('marketStatus', health.get('market', {}).get('status', 'unknown'))
        freshness = health.get('dataFreshness', health.get('data', {}).get('freshness', 'unknown'))
    except Exception:
        market_status = 'unknown'
        freshness = 'unknown'

    lines = [
        "PORTFOLIO INTELLIGENCE BRIEF",
        f"Market: {market_status} | Data: {freshness}",
        f"Holdings scanned: {len(all_symbols)} | Signals found: {len(cache)}",
    ]

    for acct in accounts:
        name = acct['name']
        risk = acct.get('risk_profile', 'moderate')
        holdings = acct.get('holdings', [])

        lines.extend(['', '=' * 40, f"{name} ({risk})", '=' * 40])

        alerts = []
        holding_lines = []

        for h in holdings:
            sym = h['symbol']
            shares = h.get('shares', 0)
            cost = h.get('cost_basis', 0)
            sig = cache.get(sym)

            if not sig:
                holding_lines.append(f"  ${sym}: No BF data")
                continue

            score = sig.get('score', 0)
            badge = sig.get('badge', '?')
            techs = sig.get('technicals', {})
            price = techs.get('price') or sig.get('currentPrice')
            move = sig.get('movement', {})
            c1d = move.get('priceChange1d', techs.get('change1d', ''))
            c5d = move.get('priceChange5d', techs.get('change5d', ''))
            rsi = techs.get('rsi')

            price_str = f"${price:,.2f}" if price else "N/A"
            line = f"  ${sym}: {price_str} | Score {score} ({badge})"
            if c1d:
                line += f" | 1d: {c1d}"
            if c5d:
                line += f" | 5d: {c5d}"
            if rsi:
                line += f" | RSI {rsi}"

            # P&L
            if shares > 0 and cost > 0 and price:
                pnl = (price - cost) * shares
                pnl_pct = ((price - cost) / cost) * 100
                line += f"\n    {shares} shares | Cost ${cost:.2f} | P&L: {'+'if pnl>=0 else ''}{pnl:,.2f} ({pnl_pct:+.1f}%)"

            holding_lines.append(line)

            # Alerts
            def pct_val(s):
                try:
                    return float(str(s).replace('%', '').replace('+', ''))
                except (ValueError, TypeError):
                    return 0.0

            if badge in ('ripe', 'overripe'):
                alerts.append(f"  SIGNAL: ${sym} is {badge.upper()} (score {score})")
            if badge == 'too-late':
                alerts.append(f"  CAUTION: ${sym} Too-Late — momentum may be exhausted")
            if rsi and rsi > 70:
                alerts.append(f"  {'OVERBOUGHT' if rsi > 80 else 'Elevated RSI'}: ${sym} RSI {rsi}")
            if rsi and rsi < 30:
                alerts.append(f"  OVERSOLD: ${sym} RSI {rsi} — potential bounce zone")
            if abs(pct_val(c1d)) > 5:
                d = "UP" if pct_val(c1d) > 0 else "DOWN"
                alerts.append(f"  BIG MOVE: ${sym} {d} {c1d} today")
            if abs(pct_val(c5d)) > 10:
                d = "up" if pct_val(c5d) > 0 else "down"
                alerts.append(f"  WEEKLY: ${sym} {d} {c5d} over 5 days")
            if risk == 'conservative' and score > 80:
                alerts.append(f"  NOTE: ${sym} score {score} — high momentum for conservative account")

        if alerts:
            lines.append('')
            lines.append('ALERTS:')
            lines.extend(alerts)

        lines.append('')
        lines.append('HOLDINGS:')
        lines.extend(holding_lines)

    return '\n'.join(lines), cache


def main():
    args = sys.argv[1:]
    as_json = '--json' in args
    account_filter = None

    # Find portfolio file (first non-flag argument)
    portfolio_file = None
    for i, a in enumerate(args):
        if a == '--account' and i + 1 < len(args):
            account_filter = args[i + 1]
        elif not a.startswith('-') and a.endswith('.json'):
            portfolio_file = a

    if not portfolio_file:
        print("Usage: python3 bf-portfolio.py portfolios.json [--account NAME] [--json]")
        sys.exit(1)

    if not os.path.exists(portfolio_file):
        print(f"ERROR: {portfolio_file} not found")
        sys.exit(1)

    with open(portfolio_file) as f:
        portfolios = json.load(f)

    accounts = portfolios.get('accounts', [])
    if not accounts:
        print("No accounts found in portfolio file")
        sys.exit(1)

    brief_text, cache = generate_brief(accounts, account_filter)

    if as_json:
        print(json.dumps({
            'brief': brief_text,
            'signals': {s: {'score': d.get('score'), 'badge': d.get('badge')}
                        for s, d in cache.items()}
        }, indent=2))
    else:
        print(brief_text)


if __name__ == '__main__':
    main()
