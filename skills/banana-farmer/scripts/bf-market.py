#!/usr/bin/env python3
"""Market pulse, top signals, and system health from Banana Farmer."""

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


def cmd_health():
    data = bf_get('health')
    if not data:
        print("Could not reach BF API")
        return
    status = data.get('marketStatus', data.get('market', {}).get('status', 'unknown'))
    freshness = data.get('dataFreshness', data.get('data', {}).get('freshness', 'unknown'))
    print(f"Market: {status}")
    print(f"Data freshness: {freshness}")
    if data.get('safetyAdvisory'):
        print(f"Advisory: {data['safetyAdvisory']}")
    print("System: OK")


def cmd_top(args):
    limit = 10
    badge = 'all'
    i = 0
    while i < len(args):
        if args[i] == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        elif args[i] == '--badge' and i + 1 < len(args):
            badge = args[i + 1]
            i += 2
        else:
            i += 1

    endpoint = f'signals/top?limit={limit}'
    if badge != 'all':
        endpoint += f'&badge={badge}'

    data = bf_get(endpoint)
    if not data:
        print("No signals available")
        return

    signals = data if isinstance(data, list) else data.get('signals', [])

    # Dedup by symbol
    seen = set()
    unique = []
    for s in signals:
        sym = s.get('symbol', '')
        if sym not in seen:
            seen.add(sym)
            unique.append(s)

    print(f"TOP {len(unique)} SIGNALS")
    print(f"{'Symbol':<8} {'Score':>5} {'Badge':<12} {'1d Change':<10} {'5d Change':<10}")
    print("-" * 52)

    for s in unique[:limit]:
        sym = s.get('symbol', '?')
        score = s.get('score', 0)
        badge_val = s.get('badge', '?')
        move = s.get('movement', {})
        c1d = move.get('priceChange1d', s.get('technicals', {}).get('change1d', ''))
        c5d = move.get('priceChange5d', s.get('technicals', {}).get('change5d', ''))
        print(f"${sym:<7} {score:>5} {badge_val:<12} {str(c1d):<10} {str(c5d):<10}")

        drivers = s.get('drivers', [])
        if drivers:
            print(f"         Drivers: {', '.join(drivers[:3])}")


def cmd_pulse():
    data = bf_get('market/pulse')
    if not data:
        print("Could not get market pulse")
        return

    print("MARKET PULSE")
    print("=" * 40)

    narrative = data.get('narrative')
    if narrative:
        if isinstance(narrative, dict):
            print(f"\n{narrative.get('summary', '')}")
        else:
            print(f"\n{narrative}")

    counts = data.get('signalCounts', data.get('counts', {}))
    if counts:
        print(f"\nSignal counts:")
        for badge, count in counts.items():
            print(f"  {badge}: {count}")

    trending = data.get('trending', [])
    if trending:
        if isinstance(trending, list):
            print(f"\nTrending: {', '.join(['$' + t.get('symbol', t) if isinstance(t, dict) else '$' + t for t in trending[:8]])}")
        elif isinstance(trending, dict):
            parts = []
            mover = trending.get('biggestMover')
            if mover and isinstance(mover, dict):
                parts.append(f"Biggest mover: ${mover.get('symbol', '?')} (+{mover.get('scoreChange', '?')})")
            sector = trending.get('hottestSector')
            if sector:
                parts.append(f"Hottest sector: {sector}")
            new_ripe_today = trending.get('newRipeToday', [])
            if new_ripe_today:
                symbols = ['$' + s for s in new_ripe_today[:5]]
                parts.append(f"New ripe: {', '.join(symbols)}")
            about = trending.get('aboutToRipe', [])
            if about:
                symbols = ['$' + s for s in about[:5]]
                parts.append(f"About to ripe: {', '.join(symbols)}")
            if parts:
                print(f"\n" + "\n".join(parts))

    new_ripe = data.get('newRipe', [])
    if new_ripe:
        print(f"\nNewly Ripe: {', '.join(['$' + s.get('symbol', s) if isinstance(s, dict) else '$' + s for s in new_ripe[:5]])}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bf-market.py <command> [options]")
        print()
        print("Commands:")
        print("  health              Check system and market status")
        print("  top [--limit N] [--badge ripe|ripening|all]")
        print("                      Show top momentum signals")
        print("  pulse               Market overview and trends")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == 'health':
        cmd_health()
    elif cmd == 'top':
        cmd_top(sys.argv[2:])
    elif cmd == 'pulse':
        cmd_pulse()
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
