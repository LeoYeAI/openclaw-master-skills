#!/usr/bin/env python3
"""Sector momentum analysis — which sectors have the most signals firing."""

import json
import os
import ssl
import sys
import urllib.request
from collections import defaultdict

BF_API_KEY = os.environ.get('BF_API_KEY', '')
BF_BASE = 'https://bananafarmer.app/api/bot/v1'

# Common sector classifications for well-known tickers
SECTOR_MAP = {
    # Tech
    'AAPL': 'Technology', 'MSFT': 'Technology', 'NVDA': 'Technology', 'AMD': 'Technology',
    'GOOGL': 'Technology', 'GOOG': 'Technology', 'META': 'Technology', 'AMZN': 'Technology',
    'TSLA': 'Technology', 'CRM': 'Technology', 'ORCL': 'Technology', 'ADBE': 'Technology',
    'INTC': 'Technology', 'AVGO': 'Technology', 'CSCO': 'Technology', 'ANET': 'Technology',
    'AKAM': 'Technology', 'CRWV': 'Technology',
    # Healthcare
    'UNH': 'Healthcare', 'JNJ': 'Healthcare', 'ABBV': 'Healthcare', 'ABT': 'Healthcare',
    'LLY': 'Healthcare', 'PFE': 'Healthcare', 'MRK': 'Healthcare', 'TMO': 'Healthcare',
    'ANAB': 'Healthcare',
    # Financial
    'JPM': 'Financials', 'BAC': 'Financials', 'WFC': 'Financials', 'GS': 'Financials',
    'MS': 'Financials', 'AXP': 'Financials', 'BLK': 'Financials', 'AFG': 'Financials',
    # Energy
    'XOM': 'Energy', 'CVX': 'Energy', 'DVN': 'Energy', 'COP': 'Energy',
    'CTRA': 'Energy', 'OXY': 'Energy', 'SLB': 'Energy',
    # Consumer
    'WMT': 'Consumer', 'KO': 'Consumer', 'PEP': 'Consumer', 'PG': 'Consumer',
    'COST': 'Consumer', 'MCD': 'Consumer', 'NKE': 'Consumer', 'SBUX': 'Consumer',
    'BURL': 'Consumer', 'BKE': 'Consumer',
    # Industrial
    'CAT': 'Industrials', 'BA': 'Industrials', 'HON': 'Industrials', 'GE': 'Industrials',
    'MMM': 'Industrials', 'ACM': 'Industrials', 'BAH': 'Industrials', 'BLDR': 'Industrials',
    # Real Estate
    'ARE': 'Real Estate', 'AMT': 'Real Estate', 'CCI': 'Real Estate',
    # Utilities
    'NEE': 'Utilities', 'DUK': 'Utilities', 'SO': 'Utilities',
    # Materials
    'AMCR': 'Materials', 'APD': 'Materials',
    # Airlines/Transport
    'AAL': 'Transport', 'UAL': 'Transport', 'DAL': 'Transport',
    # ETFs
    'QQQ': 'ETF', 'SPY': 'ETF', 'VOO': 'ETF', 'VTI': 'ETF', 'SCHD': 'ETF',
}


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


def classify_sector(symbol, name=''):
    """Classify a ticker into a sector. Uses known map first, then name-based heuristics."""
    if symbol in SECTOR_MAP:
        return SECTOR_MAP[symbol]

    name_lower = name.lower()
    if any(w in name_lower for w in ['pharma', 'biotech', 'health', 'medical', 'therapeutics']):
        return 'Healthcare'
    if any(w in name_lower for w in ['bank', 'financial', 'capital', 'insurance']):
        return 'Financials'
    if any(w in name_lower for w in ['energy', 'oil', 'gas', 'petroleum', 'solar']):
        return 'Energy'
    if any(w in name_lower for w in ['tech', 'software', 'semiconductor', 'digital', 'cloud']):
        return 'Technology'
    if any(w in name_lower for w in ['retail', 'restaurant', 'food', 'beverage', 'consumer']):
        return 'Consumer'
    if any(w in name_lower for w in ['reit', 'real estate', 'property']):
        return 'Real Estate'
    if any(w in name_lower for w in ['etf', 'fund', 'trust', 'index']):
        return 'ETF'

    return 'Other'


def analyze_sectors(as_json=False):
    # Get top signals
    data = bf_get('signals/top?limit=50&badge=all')
    if not data:
        print("No signal data available")
        return

    signals = data if isinstance(data, list) else data.get('signals', [])

    # Deduplicate
    seen = set()
    unique = []
    for s in signals:
        sym = s.get('symbol', '')
        if sym and sym not in seen:
            seen.add(sym)
            unique.append(s)

    # Group by sector
    sectors = defaultdict(list)
    for s in unique:
        sym = s.get('symbol', '')
        name = s.get('name', '')
        sector = classify_sector(sym, name)
        sectors[sector].append(s)

    if as_json:
        result = {}
        for sector, sigs in sorted(sectors.items(), key=lambda x: -len(x[1])):
            result[sector] = {
                'count': len(sigs),
                'avg_score': sum(s.get('score', 0) for s in sigs) / len(sigs) if sigs else 0,
                'tickers': [s.get('symbol') for s in sigs],
            }
        print(json.dumps(result, indent=2))
        return

    print(f"SECTOR MOMENTUM ANALYSIS")
    print(f"Signals analyzed: {len(unique)}")
    print("=" * 55)
    print()

    # Sort sectors by count and avg score
    sorted_sectors = sorted(sectors.items(),
                           key=lambda x: (-len(x[1]), -sum(s.get('score', 0) for s in x[1]) / max(len(x[1]), 1)))

    for sector, sigs in sorted_sectors:
        count = len(sigs)
        avg_score = sum(s.get('score', 0) for s in sigs) / count if count else 0
        ripe = sum(1 for s in sigs if s.get('badge') in ('ripe', 'overripe'))
        top = max(sigs, key=lambda s: s.get('score', 0))

        heat = "HOT" if avg_score >= 70 else "WARM" if avg_score >= 60 else "COOL" if avg_score >= 40 else "COLD"
        bar = "#" * min(count, 20)

        print(f"  {sector:<16} [{heat}] {count} signals, avg score {avg_score:.0f}")
        print(f"    {bar}")
        if ripe:
            print(f"    Ripe signals: {ripe}")
        print(f"    Top: ${top.get('symbol')} (score {top.get('score')})")

        # Show top 3 tickers
        top3 = sorted(sigs, key=lambda s: -s.get('score', 0))[:3]
        tickers = ', '.join(f"${s.get('symbol')} ({s.get('score')})" for s in top3)
        print(f"    Leaders: {tickers}")
        print()

    # Summary
    hottest = max(sorted_sectors, key=lambda x: sum(s.get('score', 0) for s in x[1]) / max(len(x[1]), 1))
    most_active = max(sorted_sectors, key=lambda x: len(x[1]))
    print(f"Hottest sector: {hottest[0]} (avg score {sum(s.get('score', 0) for s in hottest[1]) / len(hottest[1]):.0f})")
    print(f"Most active: {most_active[0]} ({len(most_active[1])} signals)")


def main():
    as_json = '--json' in sys.argv
    analyze_sectors(as_json)


if __name__ == '__main__':
    main()
