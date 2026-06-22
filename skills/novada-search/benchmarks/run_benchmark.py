#!/usr/bin/env python3
"""Novada Search Benchmark — requires NOVADA_API_KEY env var."""
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from novada_search import NovadaSearch, NovadaSearchError


def run():
    queries = json.loads((Path(__file__).parent / "queries.json").read_text())
    client = NovadaSearch()
    results = []

    for i, q in enumerate(queries):
        print(f"[{i+1}/{len(queries)}] {q['query'][:50]}...", end=" ", flush=True)
        try:
            start = time.time()
            r = client.search(q["query"], scene=q.get("scene"), format="agent-json")
            elapsed = int((time.time() - start) * 1000)
            entry = {
                "query": q["query"], "scene": q.get("scene"), "category": q["category"],
                "response_time_ms": elapsed,
                "unified_count": r.get("unified_count", 0),
                "organic_count": r.get("result_counts", {}).get("organic", 0),
                "shopping_count": r.get("result_counts", {}).get("shopping", 0),
                "local_count": r.get("result_counts", {}).get("local", 0),
                "has_price_comparison": "price_comparison" in r,
                "duplicates_removed": r.get("duplicates_removed", 0),
                "error": None,
            }
            results.append(entry)
            print(f"{elapsed}ms, {entry['unified_count']} results")
        except NovadaSearchError as e:
            results.append({"query": q["query"], "error": str(e)})
            print(f"ERROR: {e}")
        time.sleep(1)

    out = Path(__file__).parent / "results" / "latest.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"Saved: {out}")


if __name__ == "__main__":
    run()
