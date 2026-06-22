#!/usr/bin/env python3
"""
Generate real API response samples for Novada Search documentation.

Usage:
    export NOVADA_API_KEY="your_key"
    python3 generate_samples.py

Creates:
    samples/shopping_real.json   — shopping scene with price_comparison
    samples/local_real.json      — local scene with ratings/address
    samples/research_real.json   — research mode with extracted content
    samples/general_real.json    — basic web search

After running, pick the best parts and paste into SKILL.md / README.
"""

import json
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from novada_search import NovadaSearch, NovadaSearchError

def save(data: dict, filename: str):
    path = ROOT / "samples" / filename
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"  Saved → {path}")

def main():
    key = os.environ.get("NOVADA_API_KEY")
    if not key:
        print("ERROR: Set NOVADA_API_KEY first")
        print("  export NOVADA_API_KEY=\"your novada key here\"")
        sys.exit(1)

    client = NovadaSearch()

    queries = [
        {
            "name": "shopping_real.json",
            "desc": "Shopping — price comparison",
            "kwargs": {"query": "AirPods Pro 2", "scene": "shopping"},
        },
        {
            "name": "local_real.json",
            "desc": "Local — businesses near location",
            "kwargs": {"query": "coffee Düsseldorf Altstadt", "scene": "local"},
        },
        {
            "name": "general_real.json",
            "desc": "General — web search",
            "kwargs": {"query": "what is retrieval augmented generation", "mode": "auto"},
        },
    ]

    for q in queries:
        print(f"\n[{q['desc']}] {q['kwargs'].get('query', '')}")
        try:
            result = client.search(**q["kwargs"], format="agent-json")
            save(result, q["name"])

            # Print key stats
            print(f"  engines_used: {result.get('engines_used')}")
            print(f"  unified_results: {result.get('unified_count', 0)}")
            print(f"  response_time_ms: {result.get('response_time_ms')}")
            if "price_comparison" in result:
                print(f"  price_comparison: {len(result['price_comparison'])} items")
                if result.get("lowest_price"):
                    lp = result["lowest_price"]
                    print(f"  lowest_price: {lp.get('price')} from {lp.get('seller')}")
            if "local_results" in result:
                lr = result["local_results"]
                print(f"  local businesses: {lr.get('total_found', 0)}")
                print(f"  average_rating: {lr.get('average_rating')}")
        except NovadaSearchError as e:
            print(f"  ERROR: {e}")

    # Research mode (separate because it takes longer)
    print(f"\n[Research — search + extract]")
    try:
        result = client.research("AI agent search API comparison 2026", max_sources=3)
        save(result, "research_real.json")
        print(f"  sources_extracted: {result.get('sources_extracted')}")
        print(f"  sources_failed: {result.get('sources_failed')}")
        extracted = result.get("extracted_content", [])
        for e in extracted[:3]:
            url = e.get("url", "")[:60]
            has_content = bool(e.get("content"))
            print(f"  {'✅' if has_content else '❌'} {url}")
    except NovadaSearchError as e:
        print(f"  ERROR: {e}")

    print(f"\n=== Done. Check samples/ directory. ===")
    print("Next step: pick the best JSON snippets and add to SKILL.md and README.md")


if __name__ == "__main__":
    main()
