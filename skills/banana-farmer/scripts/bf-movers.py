#!/usr/bin/env python3
"""Recent signal movers — winners and losers with real price data from Banana Farmer."""

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


def format_mover(m):
    sym = m.get('symbol', '?')
    price_at = m.get('priceAtCapture')
    price_now = m.get('currentPrice')
    change = m.get('priceChangePercent', '?')
    milestones = m.get('milestones', {})

    line = f"  ${sym}: "
    if isinstance(change, (int, float)):
        line += f"{'+' if change > 0 else ''}{change:.1f}%"
    else:
        line += str(change)
    if price_at and price_now:
        line += f" (${price_at:.2f} → ${price_now:.2f})"

    if isinstance(milestones, dict):
        hits = [f"{k}: {'+' if v > 0 else ''}{v:.1f}%" for k, v in milestones.items() if v is not None]
        if hits:
            line += f"\n    Returns: {', '.join(hits[:4])}"

    return line


def main():
    days = 7
    limit = 5

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == '--days' and i + 1 < len(args):
            days = int(args[i + 1])
            i += 2
        elif args[i] == '--limit' and i + 1 < len(args):
            limit = int(args[i + 1])
            i += 2
        else:
            i += 1

    data = bf_get(f'signals/movers?days={days}&limit={limit}')
    if not data:
        print("No mover data available")
        return

    winners = data.get('winners', [])
    losers = data.get('losers', [])

    print(f"SIGNAL MOVERS — Last {days} days")
    print("=" * 40)

    if winners:
        print(f"\nWINNERS ({len(winners)}):")
        for w in winners[:limit]:
            print(format_mover(w))

    if losers:
        print(f"\nLOSERS ({len(losers)}):")
        for l in losers[:limit]:
            print(format_mover(l))

    if not winners and not losers:
        print("\nNo movers in this period.")

    # Summary
    total = len(winners) + len(losers)
    if total > 0:
        win_rate = len(winners) / total * 100
        print(f"\nWin rate: {win_rate:.0f}% ({len(winners)}/{total})")


if __name__ == '__main__':
    main()
