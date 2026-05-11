#!/usr/bin/env python3
"""Firecrawl scrape script for single URLs."""
import argparse
import json
import os
import sys
import urllib.request
from urllib.error import HTTPError


def scrape(url: str, formats: list = None, only_main: bool = True):
    """Scrape a URL using Firecrawl."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    formats = formats or ["markdown"]
    
    req_url = "https://api.firecrawl.dev/v1/scrape"
    
    data = json.dumps({
        "url": url,
        "formats": formats,
        "onlyMainContent": only_main
    }).encode()
    
    req = urllib.request.Request(
        req_url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode())
            return result
    except HTTPError as e:
        print(f"Error: {e.code} - {e.reason}", file=sys.stderr)
        print(e.read().decode(), file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Scrape a URL via Firecrawl")
    parser.add_argument("url", help="URL to scrape")
    parser.add_argument("--html", action="store_true", help="Include HTML format")
    parser.add_argument("--markdown", action="store_true", default=True, help="Include markdown format")
    parser.add_argument("--screenshot", action="store_true", help="Include screenshot")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    formats = []
    if args.html:
        formats.append("html")
    if args.markdown:
        formats.append("markdown")
    if args.screenshot:
        formats.append("screenshot")
    
    result = scrape(args.url, formats)
    
    if args.json:
        print(json.dumps(result, indent=2))
        return
    
    # Pretty print results
    if result.get("success") and "data" in result:
        data = result["data"]
        print(f"Title: {data.get('metadata', {}).get('title', 'N/A')}")
        print(f"URL: {data.get('metadata', {}).get('sourceURL', args.url)}")
        print(f"\n{'='*60}\n")
        
        if "markdown" in data:
            print(data["markdown"])
        elif "html" in data:
            print(data["html"][:5000])
    else:
        print("Error: Failed to scrape")
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
