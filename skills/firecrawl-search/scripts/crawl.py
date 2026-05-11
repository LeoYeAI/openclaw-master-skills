#!/usr/bin/env python3
"""Firecrawl crawl script for crawling entire websites."""
import argparse
import json
import os
import sys
import time
import urllib.request
from urllib.error import HTTPError


def start_crawl(url: str, max_pages: int = 50, exclude_paths: list = None):
    """Start a crawl job."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        print("Error: FIRECRAWL_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    
    req_url = "https://api.firecrawl.dev/v1/crawl"
    
    payload = {
        "url": url,
        "limit": max_pages,
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True
        }
    }
    
    if exclude_paths:
        payload["excludePaths"] = exclude_paths
    
    data = json.dumps(payload).encode()
    
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        print(f"Error: {e.code} - {e.reason}", file=sys.stderr)
        sys.exit(1)


def check_crawl_status(job_id: str):
    """Check crawl job status."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    req_url = f"https://api.firecrawl.dev/v1/crawl/{job_id}"
    
    req = urllib.request.Request(
        req_url,
        headers={"Authorization": f"Bearer {api_key}"}
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def main():
    parser = argparse.ArgumentParser(description="Crawl a website via Firecrawl")
    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to crawl")
    parser.add_argument("--wait", action="store_true", help="Wait for completion")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    
    args = parser.parse_args()
    
    # Start crawl
    result = start_crawl(args.url, args.max_pages)
    
    if not result.get("success"):
        print("Error: Failed to start crawl", file=sys.stderr)
        print(json.dumps(result, indent=2))
        sys.exit(1)
    
    job_id = result.get("id")
    print(f"Crawl started: {job_id}")
    
    if not args.wait:
        print(f"Check status with: firecrawl_crawl_status {job_id}")
        return
    
    # Poll for completion
    print("Waiting for completion...")
    while True:
        status = check_crawl_status(job_id)
        
        if status.get("status") in ["completed", "failed", "cancelled"]:
            break
        
        print(f"Status: {status.get('status')}...")
        time.sleep(2)
    
    if args.json:
        print(json.dumps(status, indent=2))
    else:
        print(f"\nCrawl {status.get('status')}")
        if "data" in status:
            print(f"Pages crawled: {len(status['data'])}")
            for page in status["data"]:
                print(f"\n{'='*60}")
                print(f"URL: {page.get('metadata', {}).get('sourceURL', 'N/A')}")
                if "markdown" in page:
                    preview = page["markdown"][:300] + "..." if len(page["markdown"]) > 300 else page["markdown"]
                    print(f"Preview: {preview}")


if __name__ == "__main__":
    main()
