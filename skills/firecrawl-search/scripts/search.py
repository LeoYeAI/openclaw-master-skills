#!/usr/bin/env python3
"""Firecrawl web search script."""
import argparse
import json
import os
import sys
import urllib.request
from urllib.error import HTTPError


def search(query: str, limit: int = 10):
    """Search the web using Firecrawl."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    url = "https://api.firecrawl.dev/v1/search"
    
    data = json.dumps({
        "query": query,
        "limit": limit,
        "lang": "en",
        "country": "us"
    }).encode()
    
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode())
            return result
    except HTTPError as e:
        print(f"Error: {e.code} - {e.reason}", file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Search the web via Firecrawl")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--limit", type=int, default=10, help="Max results")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    result = search(args.query, args.limit)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    # Pretty print results
    if result.get("success") and "data" in result:
        for item in result["data"]:
            print(f"\n{'='*60}")
            print(f"Title: {item.get('title', 'N/A')}")
            print(f"URL: {item.get('url', 'N/A')}")
            print(f"Description: {item.get('description', 'N/A')}")
            if "markdown" in item:
                content = item["markdown"][:500] + "..." if len(item["markdown"]) > 500 else item["markdown"]
                print(f"Content preview:\n{content}")
    else:
        print("No results found")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
