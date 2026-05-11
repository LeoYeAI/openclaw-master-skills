#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Web Search Fallback — Drop-in replacement for the `web_search` tool.

When the host AI environment does not provide a built-in `web_search` tool
(e.g., no API key configured), this script provides equivalent search
functionality — zero API keys needed.

Search engine priority:
  1. DuckDuckGo HTML (most reliable, no captcha)
  2. Bing HTML (fallback, may hit captcha in some networks)

Usage:
    # Basic search (returns JSON to stdout)
    python web_search_fallback.py "electric kettle review 2025"

    # With result count
    python web_search_fallback.py "电竞椅 推荐 避坑" --count 15

    # Site-restricted search (equivalent to web_search + site:)
    python web_search_fallback.py "office chair review" --site reddit.com

    # Multiple site-restricted searches in one call
    python web_search_fallback.py "电竞椅 推荐" --sites zhihu.com,v2ex.com,smzdm.com --count 5

    # Search + fetch content in one call (reduces round trips)
    python web_search_fallback.py "电竞椅 避坑" --count 10 --fetch-content --fetch-limit 3

    # Force a specific engine
    python web_search_fallback.py "test query" --engine bing
    python web_search_fallback.py "test query" --engine duckduckgo

Output format (JSON):
    {
        "query": "...",
        "engine": "duckduckgo",
        "total_results": N,
        "results": [
            {"title": "...", "url": "...", "snippet": "..."},
            ...
        ]
    }
"""

import argparse
import json
import re
import sys
import os
import time
import urllib.parse
import urllib.request
import ssl
from html.parser import HTMLParser

# ============================================================
# HTTP utilities
# ============================================================

_SSL_CTX = ssl.create_default_context()

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
}


class _HTMLTextExtractor(HTMLParser):
    """Extract text from HTML, stripping all tags."""
    def __init__(self):
        super().__init__()
        self._parts = []

    def handle_data(self, data):
        self._parts.append(data)

    def get_text(self):
        return "".join(self._parts).strip()


def html_to_text(html_str):
    """Convert HTML snippet to plain text."""
    ext = _HTMLTextExtractor()
    try:
        ext.feed(html_str)
        return ext.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", "", html_str).strip()


def fetch_url(url, timeout=15):
    """Send HTTP GET, return response text."""
    req = urllib.request.Request(url, headers=_HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as resp:
            charset = resp.headers.get_content_charset() or "utf-8"
            return resp.read().decode(charset, errors="replace")
    except Exception as e:
        print(f"[WARN] Request failed: {url} -> {e}", file=sys.stderr)
        return ""


def fetch_page_content(url, max_length=5000):
    """Fetch page body text (for --fetch-content)."""
    html = fetch_url(url, timeout=20)
    if not html:
        return ""
    # Strip scripts, styles
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = html_to_text(html)
    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_length]


# ============================================================
# DuckDuckGo HTML Search (Primary)
# ============================================================

def search_duckduckgo(query, site=None, count=10):
    """
    Search via DuckDuckGo HTML version (https://html.duckduckgo.com/html/).
    No API key needed. More resistant to captcha than Bing.
    """
    search_query = query
    if site:
        search_query = f"site:{site} {query}"

    params = {"q": search_query}
    url = f"https://html.duckduckgo.com/html/?{urllib.parse.urlencode(params)}"

    print(f"[DDG] Fetching: {url}", file=sys.stderr)
    html = fetch_url(url, timeout=20)
    if not html:
        print("[DDG] No response.", file=sys.stderr)
        return []

    # Check for rate limiting
    if "please try again" in html.lower() or len(html) < 500:
        print("[DDG] Rate limited or empty response.", file=sys.stderr)
        return []

    results = parse_duckduckgo_results(html)
    print(f"[DDG] Parsed {len(results)} results.", file=sys.stderr)
    return results[:count]


def parse_duckduckgo_results(html):
    """Parse DuckDuckGo HTML results page."""
    results = []

    # DuckDuckGo HTML format:
    # <a rel="nofollow" class="result__a" href="URL">TITLE</a>
    # <a class="result__snippet" href="URL">SNIPPET</a>
    result_pattern = re.compile(
        r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>'
        r'.*?'
        r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
        re.DOTALL,
    )

    for match in result_pattern.finditer(html):
        raw_url = match.group(1)
        title = html_to_text(match.group(2))
        snippet = html_to_text(match.group(3))

        # DuckDuckGo wraps URLs in a redirect — extract real URL
        url = _extract_ddg_url(raw_url)

        if url and title and "duckduckgo.com" not in url:
            results.append({
                "url": url,
                "title": title,
                "snippet": snippet,
            })

    # Fallback: simpler pattern if above yields nothing
    if not results:
        simple_pattern = re.compile(
            r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>',
            re.DOTALL,
        )
        for match in simple_pattern.finditer(html):
            raw_url = match.group(1)
            title = html_to_text(match.group(2))
            url = _extract_ddg_url(raw_url)
            if url and title and "duckduckgo.com" not in url:
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": "",
                })

    return results


def _extract_ddg_url(raw_url):
    """Extract the real URL from DuckDuckGo's redirect wrapper."""
    if not raw_url:
        return ""
    # DDG sometimes uses //duckduckgo.com/l/?uddg=ENCODED_URL&...
    if "uddg=" in raw_url:
        parsed = urllib.parse.urlparse(raw_url)
        qs = urllib.parse.parse_qs(parsed.query)
        if "uddg" in qs:
            return urllib.parse.unquote(qs["uddg"][0])
    # Direct URL
    if raw_url.startswith("http"):
        return raw_url
    if raw_url.startswith("//"):
        return "https:" + raw_url
    return raw_url


# ============================================================
# Bing HTML Search (Fallback)
# ============================================================

def search_bing_fallback(query, site=None, count=10):
    """
    Search via Bing HTML. May hit captcha in some environments.
    Used as fallback when DuckDuckGo fails.
    """
    search_query = query
    if site:
        search_query = f"site:{site} {query}"

    params = {
        "q": search_query,
        "count": min(count, 50),
    }
    url = f"https://www.bing.com/search?{urllib.parse.urlencode(params)}"

    print(f"[BING] Fetching: {url}", file=sys.stderr)
    html = fetch_url(url, timeout=15)
    if not html:
        print("[BING] No response.", file=sys.stderr)
        return []

    # Check for captcha
    if "captcha" in html.lower() or "are you a robot" in html.lower():
        print("[BING] Captcha detected, skipping.", file=sys.stderr)
        return []

    results = parse_bing_results(html)
    print(f"[BING] Parsed {len(results)} results.", file=sys.stderr)
    return results[:count]


def parse_bing_results(html):
    """Parse Bing HTML results."""
    results = []

    pattern = re.compile(
        r'<li\s+class="b_algo"[^>]*>.*?'
        r'<a\s+href="([^"]+)"[^>]*>(.*?)</a>'
        r'.*?<p[^>]*>(.*?)</p>',
        re.DOTALL,
    )

    for match in pattern.finditer(html):
        url = match.group(1)
        title = html_to_text(match.group(2))
        snippet = html_to_text(match.group(3))
        if url and title:
            results.append({
                "url": url,
                "title": title,
                "snippet": snippet,
            })

    # Broader fallback
    if not results:
        url_pattern = re.compile(r'<a\s+href="(https?://[^"]+)"[^>]*>(.*?)</a>', re.DOTALL)
        for match in url_pattern.finditer(html):
            url = match.group(1)
            title = html_to_text(match.group(2))
            if "bing.com" not in url and "microsoft.com" not in url and title and len(title) > 5:
                results.append({
                    "url": url,
                    "title": title,
                    "snippet": "",
                })

    return results


# ============================================================
# Multi-engine orchestrator
# ============================================================

def search(query, site=None, count=10, engine=None):
    """
    Search with automatic engine fallback.

    Priority: DuckDuckGo -> Bing
    If a specific engine is requested, only use that one.
    """
    engines = []

    if engine == "duckduckgo":
        engines = [("duckduckgo", search_duckduckgo)]
    elif engine == "bing":
        engines = [("bing", search_bing_fallback)]
    else:
        # Auto: try DDG first, fall back to Bing
        engines = [
            ("duckduckgo", search_duckduckgo),
            ("bing", search_bing_fallback),
        ]

    for name, search_fn in engines:
        print(f"[FALLBACK] Trying engine: {name}", file=sys.stderr)
        results = search_fn(query, site=site, count=count)
        if results:
            return name, results
        print(f"[FALLBACK] {name} returned 0 results, trying next...", file=sys.stderr)
        time.sleep(1.0)

    return engines[-1][0] if engines else "none", []


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Web Search Fallback — multi-engine search, no API key needed",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python web_search_fallback.py "best ergonomic chair 2025"
  python web_search_fallback.py "电竞椅 推荐" --count 15
  python web_search_fallback.py "office chair" --site reddit.com
  python web_search_fallback.py "电竞椅" --sites zhihu.com,v2ex.com --count 5
  python web_search_fallback.py "test" --engine duckduckgo
        """,
    )

    parser.add_argument("query", help="Search query string")
    parser.add_argument(
        "--count", "-c",
        type=int, default=10,
        help="Number of results to return (default: 10)",
    )
    parser.add_argument(
        "--site", "-s",
        default=None,
        help="Restrict search to a single site (e.g., reddit.com)",
    )
    parser.add_argument(
        "--sites",
        default=None,
        help="Restrict search to multiple sites (comma-separated), searches each site independently",
    )
    parser.add_argument(
        "--engine",
        choices=["duckduckgo", "bing", "auto"],
        default="auto",
        help="Force a specific search engine (default: auto = try DDG first, then Bing)",
    )
    parser.add_argument(
        "--fetch-content", "-f",
        action="store_true",
        help="Also fetch page content for each result (slower but more useful)",
    )
    parser.add_argument(
        "--fetch-limit",
        type=int, default=3,
        help="Max number of pages to fetch content for (default: 3, use with --fetch-content)",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output file path (JSON). If not specified, outputs to stdout",
    )

    args = parser.parse_args()

    engine_name_to_use = None if args.engine == "auto" else args.engine
    all_results = []
    used_engine = "none"

    if args.sites:
        # Multi-site mode: search each site independently
        sites = [s.strip() for s in args.sites.split(",")]
        for site in sites:
            print(f"\n[FALLBACK] === Searching site: {site} ===", file=sys.stderr)
            eng, results = search(args.query, site=site, count=args.count, engine=engine_name_to_use)
            used_engine = eng
            for r in results:
                r["search_site"] = site
            all_results.extend(results)
            time.sleep(1.0)
    else:
        # Single search
        eng, results = search(args.query, site=args.site, count=args.count, engine=engine_name_to_use)
        used_engine = eng
        all_results = results

    # Deduplicate by URL
    seen_urls = set()
    unique_results = []
    for r in all_results:
        if r["url"] not in seen_urls:
            seen_urls.add(r["url"])
            unique_results.append(r)

    # Optional content fetching
    if args.fetch_content and unique_results:
        fetch_limit = min(args.fetch_limit, len(unique_results))
        print(f"\n[FALLBACK] Fetching content for top {fetch_limit} results...", file=sys.stderr)
        for i, r in enumerate(unique_results[:fetch_limit]):
            print(f"[FALLBACK]   ({i+1}/{fetch_limit}) {r['url']}", file=sys.stderr)
            r["content"] = fetch_page_content(r["url"])
            time.sleep(0.5)

    print(f"\n[FALLBACK] Done. Engine: {used_engine}, Results: {len(unique_results)}", file=sys.stderr)

    # Output JSON
    output_data = {
        "query": args.query,
        "engine": used_engine,
        "site": args.site or args.sites,
        "total_results": len(unique_results),
        "results": unique_results,
    }

    json_str = json.dumps(output_data, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(json_str)
        print(f"[FALLBACK] Results saved to: {args.output}", file=sys.stderr)
    else:
        print(json_str)


if __name__ == "__main__":
    main()
