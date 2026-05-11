#!/usr/bin/env python3
"""
Enrich high-scoring articles with full text content.

Fetches full article text for top articles from merged JSON, using:
1. Cloudflare Markdown for Agents (Accept: text/markdown) — preferred
2. HTML readability extraction — fallback
3. Skip — for paywalled/JS-heavy pages

Usage:
    python3 enrich-articles.py --input merged.json --output enriched.json [--min-score 10] [--verbose]
"""

import json
import re
import sys
import os
import argparse
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import HTTPError, URLError

TIMEOUT = 10
MAX_WORKERS = 5
DEFAULT_MIN_SCORE = 10
DEFAULT_MAX_ARTICLES = 15
DEFAULT_MAX_CHARS = 2000
USER_AGENT = "TechDigest/3.0 (article enrichment)"

SKIP_DOMAINS = {
    "twitter.com", "x.com",
    "reddit.com", "old.reddit.com",
    "github.com",
    "youtube.com", "youtu.be",
    "nytimes.com", "bloomberg.com", "wsj.com", "ft.com",
    "arxiv.org",
}


def setup_logging(verbose=False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(level=level, format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    return logging.getLogger(__name__)


def get_domain(url):
    try:
        from urllib.parse import urlparse
        return urlparse(url).netloc.lower().lstrip("www.")
    except Exception:
        return ""


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._text = []
        self._skip = False
        self._skip_tags = {"script", "style", "nav", "footer", "header", "aside", "noscript"}

    def handle_starttag(self, tag, attrs):
        if tag in self._skip_tags:
            self._skip = True

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False
        if tag in ("p", "br", "div", "h1", "h2", "h3", "h4", "li"):
            self._text.append("\n")

    def handle_data(self, data):
        if not self._skip:
            self._text.append(data)

    def get_text(self):
        raw = "".join(self._text)
        raw = re.sub(r"[ \t]+", " ", raw)
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        return raw.strip()


def extract_readable_text(html):
    article_match = re.search(r"<article[^>]*>(.*?)</article>", html, re.DOTALL | re.IGNORECASE)
    fragment = article_match.group(1) if article_match else html
    extractor = TextExtractor()
    try:
        extractor.feed(fragment)
    except Exception:
        return ""
    return extractor.get_text()


def fetch_full_text(url, max_chars=DEFAULT_MAX_CHARS):
    domain = get_domain(url)
    if domain in SKIP_DOMAINS:
        return {"text": "", "method": "skipped", "tokens": 0, "error": f"domain {domain} in skip list"}

    try:
        headers = {"Accept": "text/markdown, text/html;q=0.9", "User-Agent": USER_AGENT}
        req = Request(url, headers=headers)
        with urlopen(req, timeout=TIMEOUT) as resp:
            content_type = resp.headers.get("Content-Type", "")
            token_header = resp.headers.get("x-markdown-tokens", "")
            raw = resp.read()

            if raw[:2] == b"\x1f\x8b":
                import gzip
                raw = gzip.decompress(raw)

            text = raw.decode("utf-8", errors="replace")

            if "text/markdown" in content_type:
                tokens = int(token_header) if token_header.isdigit() else len(text) // 4
                return {"text": text[:max_chars], "method": "cf-markdown", "tokens": tokens, "error": None}

            extracted = extract_readable_text(text)
            if len(extracted) < 100:
                return {"text": "", "method": "html-too-short", "tokens": 0, "error": "extracted text too short"}

            return {"text": extracted[:max_chars], "method": "html-extract", "tokens": len(extracted[:max_chars]) // 4, "error": None}

    except HTTPError as e:
        return {"text": "", "method": "error", "tokens": 0, "error": f"HTTP {e.code}"}
    except URLError as e:
        return {"text": "", "method": "error", "tokens": 0, "error": f"URL error: {e.reason}"}
    except Exception as e:
        return {"text": "", "method": "error", "tokens": 0, "error": str(e)[:100]}


def enrich_articles(articles, min_score=DEFAULT_MIN_SCORE, max_articles=DEFAULT_MAX_ARTICLES, max_chars=DEFAULT_MAX_CHARS):
    # Eligible: high-score articles OR RSS blog articles (lower threshold for blogs)
    blog_domains = {
        "simonwillison.net", "overreacted.io", "eli.thegreenplace.net",
        "matklad.github.io", "lucumr.pocoo.org", "devblogs.microsoft.com",
        "rachelbythebay.com", "xeiaso.net", "pluralistic.net", "lcamtuf.substack.com",
        "hillelwayne.com", "dynomight.net", "geoffreylitt.com", "fabiensanglard.net",
        "blog.cloudflare.com", "antirez.com", "paulgraham.com", "danluu.com",
        "latent.space", "www.latent.space",
    }
    eligible = []
    for a in articles:
        if a.get("full_text") or not a.get("link"):
            continue
        score = a.get("quality_score", 0)
        domain = get_domain(a.get("link", ""))
        # Blog articles get lower threshold (score >= 3), others use min_score
        if score >= min_score or (domain in blog_domains and score >= 3):
            eligible.append(a)

    seen_urls = {}
    unique = []
    for a in eligible:
        url = a["link"]
        if url not in seen_urls:
            seen_urls[url] = a
            unique.append(a)

    unique.sort(key=lambda x: -x.get("quality_score", 0))
    to_fetch = unique[:max_articles]

    if not to_fetch:
        logging.info("No articles eligible for enrichment")
        return 0, 0, 0

    logging.info(f"Enriching {len(to_fetch)} articles (min_score={min_score})")

    attempted = success = cf_count = 0
    results = {}

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(fetch_full_text, a["link"], max_chars): a["link"] for a in to_fetch}
        for future in as_completed(futures):
            url = futures[future]
            attempted += 1
            result = future.result()
            results[url] = result
            if result["text"]:
                success += 1
                if result["method"] == "cf-markdown":
                    cf_count += 1
                logging.debug(f"  ✅ [{result['method']}] {url[:60]}... ({result['tokens']} tokens)")
            else:
                logging.debug(f"  ⏭️ [{result['method']}] {url[:60]}... ({result.get('error', '')})")

    for a in articles:
        url = a.get("link", "")
        if url in results and results[url]["text"]:
            r = results[url]
            a["full_text"] = r["text"]
            a["full_text_method"] = r["method"]
            a["full_text_tokens"] = r["tokens"]

    logging.info(f"Enrichment: {success}/{attempted} enriched ({cf_count} via CF Markdown)")
    return attempted, success, cf_count


def main():
    parser = argparse.ArgumentParser(description="Enrich articles with full text")
    parser.add_argument("--input", "-i", type=Path, required=True, help="Input merged JSON")
    parser.add_argument("--output", "-o", type=Path, help="Output enriched JSON (default: overwrite input)")
    parser.add_argument("--min-score", type=int, default=DEFAULT_MIN_SCORE)
    parser.add_argument("--max-articles", type=int, default=DEFAULT_MAX_ARTICLES)
    parser.add_argument("--max-chars", type=int, default=DEFAULT_MAX_CHARS)
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--force", action="store_true", help="Ignored (pipeline compat)")
    args = parser.parse_args()
    setup_logging(args.verbose)

    if not args.input.exists():
        logging.error(f"Input file not found: {args.input}")
        return 1

    output_path = args.output or args.input

    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)

        all_articles = []
        topics = data.get("topics", {})
        if isinstance(topics, dict):
            for topic_data in topics.values():
                if isinstance(topic_data, dict):
                    all_articles.extend(topic_data.get("articles", []))
                elif isinstance(topic_data, list):
                    all_articles.extend(topic_data)

        t0 = time.time()
        attempted, success, cf_count = enrich_articles(all_articles, args.min_score, args.max_articles, args.max_chars)
        elapsed = time.time() - t0

        data["enrichment"] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "attempted": attempted, "success": success, "cf_markdown": cf_count,
            "elapsed_s": round(elapsed, 1), "min_score": args.min_score, "max_chars": args.max_chars,
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logging.info(f"✅ Done: {success}/{attempted} enriched in {elapsed:.1f}s → {output_path}")
        return 0

    except Exception as e:
        logging.error(f"💥 Enrichment failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
