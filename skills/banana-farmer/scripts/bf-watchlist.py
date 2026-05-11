#!/usr/bin/env python3
"""Curated daily watchlist from Banana Farmer — pre-picked signals with editorial context."""

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


def show_watchlist(as_json=False):
    data = bf_get('content/watchlist')
    if not data:
        print("No watchlist data available")
        return

    items = data.get('watchlist', data) if isinstance(data, dict) else data
    if not items:
        print("Watchlist is empty today")
        return

    if as_json:
        print(json.dumps(items, indent=2))
        return

    print(f"DAILY WATCHLIST — {len(items)} picks")
    print("=" * 50)
    print()

    for item in items:
        sym = item.get('symbol', '?')
        score = item.get('score', '?')
        reason = item.get('reason', '')
        category = item.get('category', '')
        price = item.get('currentPrice')
        coil = item.get('coilScore')
        rsi = item.get('rsi')

        line = f"  ${sym} — Score {score}"
        if price:
            line += f" — ${price:,.2f}"
        print(line)

        extras = []
        if coil:
            extras.append(f"Coil {coil}")
        if rsi:
            extras.append(f"RSI {rsi}")
        if extras:
            print(f"    Technicals: {', '.join(extras)}")

        if category:
            print(f"    Category: {category}")
        if reason:
            print(f"    Why: {reason}")
        print()


def show_scorecard(as_json=False):
    data = bf_get('content/scorecard')
    if not data:
        print("No scorecard data available")
        return

    sdata = data.get('data', data) if isinstance(data, dict) else data

    if as_json:
        print(json.dumps(sdata, indent=2))
        return

    print("SYSTEM SCORECARD")
    print("=" * 50)

    overview = sdata.get('overview', {})
    if overview:
        print(f"\n  Total signals: {overview.get('totalSignalsAnalyzed', '?'):,}")
        print(f"  Data span: {overview.get('dataSpanDays', '?')} days")
        print(f"  Stocks tracked: {overview.get('stocksTracked', '?'):,}")

    wr = sdata.get('winRatesByHorizon', sdata.get('winRates', {}))
    ripe = wr.get('ripeSignals', wr)
    if ripe:
        print(f"\n  Win rates (Ripe signals):")
        for period in ['1d', '3d', '5d', '10d', '1mo', '2mo']:
            p = ripe.get(period, {})
            if p:
                rate = p.get('winRate', 0)
                avg = p.get('avgReturn', 0)
                if isinstance(rate, (int, float)) and rate > 0:
                    # API returns percentages as numbers (76.5 = 76.5%), not decimals
                    print(f"    {period}: {rate:.1f}% win rate, avg +{avg:.2f}%")

    thresh = sdata.get('byScoreThreshold', {})
    if thresh:
        print(f"\n  By score threshold (5d):")
        for label, key in [('80-85', '80to85'), ('85-90', '85to90'), ('90-95', '90to95'), ('95+', '95plus')]:
            t = thresh.get(key, {})
            if t and t.get('winRate5d'):
                print(f"    Score {label}: {t['winRate5d']:.1f}% win rate, n={t.get('sampleSize', '?')}")


def show_horizons(as_json=False):
    data = bf_get('stats/horizons')
    if not data:
        print("No horizon data available")
        return

    hdata = data.get('data', data) if isinstance(data, dict) else data

    if as_json:
        print(json.dumps(hdata, indent=2))
        return

    print("TIME HORIZON ANALYSIS")
    print("=" * 50)
    print()
    print("How long should you hold? Win rates improve significantly with time:")
    print()

    horizons = hdata.get('horizons', hdata)
    if isinstance(horizons, dict):
        for period, stats in horizons.items():
            if isinstance(stats, dict):
                wr = stats.get('winRate', 0)
                avg_r = stats.get('avgReturn', 0)
                if isinstance(wr, (int, float)) and wr > 0:
                    print(f"  {period}: {wr:.1%} win rate, avg +{avg_r:.2%}")
    elif isinstance(horizons, list):
        for h in horizons:
            period = h.get('period', '?')
            wr = h.get('winRate', 0)
            avg_r = h.get('avgReturn', 0)
            print(f"  {period}: {wr:.1%} win rate, avg +{avg_r:.2%}")

    print()
    print("Key insight: Patience pays. The 5-day win rate (79.9%) is significantly")
    print("higher than the 1-day rate. Most signals need 3-5 days to play out fully.")


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 bf-watchlist.py <command> [--json]")
        print()
        print("Commands:")
        print("  picks       Today's curated watchlist picks")
        print("  scorecard   System win rates and performance stats")
        print("  horizons    Time horizon analysis (how long to hold)")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    as_json = '--json' in sys.argv

    if cmd == 'picks':
        show_watchlist(as_json)
    elif cmd == 'scorecard':
        show_scorecard(as_json)
    elif cmd == 'horizons':
        show_horizons(as_json)
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
