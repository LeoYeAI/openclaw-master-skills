#!/usr/bin/env python3
"""
Fetch RSS feeds from unified sources configuration.

Reads sources.json, filters RSS sources, fetches feeds in parallel with retry
mechanism, and outputs structured JSON with articles tagged by topics.

Usage:
    python3 fetch-rss.py [--config CONFIG_DIR] [--hours 48] [--output FILE] [--verbose]
"""

import json
import re
import sys
import os
import argparse
import logging
import time
import tempfile
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urljoin
from pathlib import Path
from typing import Dict, List, Any, Optional
import threading

# Try to import feedparser, fall back to regex parsing
try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False
    logging.warning("feedparser not installed — using basic XML regex parser (may miss some feeds). Install with: pip install feedparser")

TIMEOUT = 30
MAX_WORKERS = 10  
MAX_ARTICLES_PER_FEED = 20
RETRY_COUNT = 1
RETRY_DELAY = 2.0  # seconds
RSS_CACHE_PATH = "/tmp/tech-news-digest-rss-cache.json"
RSS_CACHE_TTL_HOURS = 24


def setup_logging(verbose: bool) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def parse_date_regex(s: str) -> Optional[datetime]:
    """Parse date string using regex patterns (fallback method)."""
    if not s:
        return None
    s = s.strip()
    
    # Common date formats
    formats = [
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z", 
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt
        except ValueError:
            continue
            
    # ISO fallback
    try:
        dt = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return dt
    except (ValueError, AttributeError):
        pass
        
    return None


def extract_cdata(text: str) -> str:
    """Extract content from CDATA sections."""
    m = re.search(r"<!\[CDATA\[(.*?)\]\]>", text, re.DOTALL)
    return m.group(1) if m else text


def strip_tags(html: str) -> str:
    """Remove HTML tags from text."""
    return re.sub(r"<[^>]+>", "", html).strip()


def get_tag(xml: str, tag: str) -> str:
    """Extract content from XML tag using regex."""
    m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", xml, re.DOTALL | re.IGNORECASE)
    return extract_cdata(m.group(1)).strip() if m else ""


def validate_article_domain(article_link: str, source: Dict[str, Any]) -> bool:
    """Validate that article links from mirror sources point to expected domains.
    
    Sources with 'expected_domains' field will have their article links checked.
    Returns True if valid or if no domain restriction is set.
    """
    expected = source.get("expected_domains")
    if not expected:
        return True
    if not article_link:
        return False
    from urllib.parse import urlparse
    domain = urlparse(article_link).hostname or ""
    return any(domain == d or domain.endswith("." + d) for d in expected)


def resolve_link(link: str, base_url: str) -> str:
    """Resolve relative links against the feed URL. Rejects non-HTTP(S) schemes."""
    if not link:
        return link
    if link.startswith(("http://", "https://")):
        return link
    resolved = urljoin(base_url, link)
    if not resolved.startswith(("http://", "https://")):
        return ""  # reject javascript:, data:, etc.
    return resolved


def parse_feed_feedparser(content: str, cutoff: datetime, feed_url: str) -> List[Dict[str, Any]]:
    """Parse feed using feedparser library."""
    articles = []
    
    try:
        feed = feedparser.parse(content)
        
        for entry in feed.entries[:MAX_ARTICLES_PER_FEED]:
            title = entry.get('title', '').strip()
            link = entry.get('link', '').strip()
            
            # Try multiple date fields
            pub_date = None
            for date_field in ['published_parsed', 'updated_parsed']:
                if hasattr(entry, date_field) and getattr(entry, date_field):
                    try:
                        pub_date = datetime(*getattr(entry, date_field)[:6], tzinfo=timezone.utc)
                        break
                    except (TypeError, ValueError):
                        continue
                        
            # Fallback to string parsing
            if pub_date is None:
                for date_field in ['published', 'updated']:
                    if hasattr(entry, date_field) and getattr(entry, date_field):
                        pub_date = parse_date_regex(getattr(entry, date_field))
                        if pub_date:
                            break
                            
            if title and link and pub_date and pub_date >= cutoff:
                articles.append({
                    "title": title[:200],
                    "link": resolve_link(link, feed_url),
                    "date": pub_date.isoformat(),
                })
                
    except Exception as e:
        logging.debug(f"feedparser parsing failed: {e}")
        
    return articles


def parse_feed_regex(content: str, cutoff: datetime, feed_url: str) -> List[Dict[str, Any]]:
    """Parse feed using regex patterns (fallback method)."""
    articles = []

    # RSS 2.0 items
    for item in re.finditer(r"<item[^>]*>(.*?)</item>", content, re.DOTALL):
        block = item.group(1)
        title = strip_tags(get_tag(block, "title"))
        link = resolve_link(get_tag(block, "link"), feed_url)
        date_str = get_tag(block, "pubDate") or get_tag(block, "dc:date")
        pub = parse_date_regex(date_str)

        if title and link and pub and pub >= cutoff:
            articles.append({
                "title": title[:200],
                "link": link,
                "date": pub.isoformat(),
            })

    # Atom entries fallback
    if not articles:
        for entry in re.finditer(r"<entry[^>]*>(.*?)</entry>", content, re.DOTALL):
            block = entry.group(1)
            title = strip_tags(get_tag(block, "title"))
            link_m = re.search(r'<link[^>]*href=["\']([^"\']+)["\']', block)
            if not link_m:
                link = get_tag(block, "link")
            else:
                link = link_m.group(1)
            link = resolve_link(link, feed_url)
            date_str = get_tag(block, "updated") or get_tag(block, "published")
            pub = parse_date_regex(date_str)

            if title and link and pub and pub >= cutoff:
                articles.append({
                    "title": title[:200],
                    "link": link,
                    "date": pub.isoformat(),
                })

    return articles[:MAX_ARTICLES_PER_FEED]


def parse_feed(content: str, cutoff: datetime, feed_url: str) -> List[Dict[str, Any]]:
    """Parse feed using best available method."""
    if HAS_FEEDPARSER:
        articles = parse_feed_feedparser(content, cutoff, feed_url)
        if articles:
            return articles
        logging.debug("feedparser returned no articles, trying regex fallback")
        
    return parse_feed_regex(content, cutoff, feed_url)


def _load_rss_cache() -> Dict[str, Any]:
    """Load RSS ETag/Last-Modified cache."""
    try:
        with open(RSS_CACHE_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save_rss_cache(cache: Dict[str, Any]) -> None:
    """Save RSS ETag/Last-Modified cache."""
    try:
        with open(RSS_CACHE_PATH, 'w') as f:
            json.dump(cache, f)
    except Exception as e:
        logging.warning(f"Failed to save RSS cache: {e}")


# Module-level cache, loaded once per run
# Protected by _rss_cache_lock for thread-safe access
_rss_cache: Optional[Dict[str, Any]] = None
_rss_cache_dirty = False
_rss_cache_lock = threading.RLock()  # Reentrant lock to allow nested acquisition


def _get_rss_cache(no_cache: bool = False) -> Dict[str, Any]:
    global _rss_cache
    with _rss_cache_lock:
        if _rss_cache is None:
            _rss_cache = {} if no_cache else _load_rss_cache()
        return _rss_cache


def _flush_rss_cache() -> None:
    global _rss_cache, _rss_cache_dirty
    with _rss_cache_lock:
        if _rss_cache_dirty and _rss_cache is not None:
            _save_rss_cache(_rss_cache)
            _rss_cache_dirty = False


def fetch_feed_with_retry(source: Dict[str, Any], cutoff: datetime, no_cache: bool = False) -> Dict[str, Any]:
    """Fetch RSS feed with retry mechanism and conditional requests."""
    source_id = source["id"]
    name = source["name"]
    url = source["url"]
    priority = source["priority"]
    topics = source["topics"]
    
    global _rss_cache, _rss_cache_dirty
    
    for attempt in range(RETRY_COUNT + 1):
        try:
            req_headers = {"User-Agent": "TechDigest/2.0"}
            
            # Add conditional headers from cache (thread-safe)
            with _rss_cache_lock:
                cache = _rss_cache if _rss_cache is not None else {}
                cache_entry = cache.get(url)
            now = time.time()
            ttl_seconds = RSS_CACHE_TTL_HOURS * 3600
            
            if cache_entry and not no_cache and (now - cache_entry.get("ts", 0)) < ttl_seconds:
                if cache_entry.get("etag"):
                    req_headers["If-None-Match"] = cache_entry["etag"]
                if cache_entry.get("last_modified"):
                    req_headers["If-Modified-Since"] = cache_entry["last_modified"]
            
            req = Request(url, headers=req_headers)
            try:
                with urlopen(req, timeout=TIMEOUT) as resp:
                    # Update cache with response headers (thread-safe)
                    etag = resp.headers.get("ETag")
                    last_mod = resp.headers.get("Last-Modified")
                    if etag or last_mod:
                        with _rss_cache_lock:
                            if _rss_cache is None:
                                _rss_cache = {}
                            _rss_cache[url] = {"etag": etag, "last_modified": last_mod, "ts": now}
                            _rss_cache_dirty = True
                    
                    final_url = resp.url if hasattr(resp, 'url') else url
                    content = resp.read().decode("utf-8", errors="replace")
            except URLError as e:
                if hasattr(e, 'code') and e.code == 304:
                    logging.info(f"⏭ {name}: not modified (304)")
                    return {
                        "source_id": source_id,
                        "source_type": "rss",
                        "name": name,
                        "url": url,
                        "priority": priority,
                        "topics": topics,
                        "status": "ok",
                        "attempts": attempt + 1,
                        "not_modified": True,
                        "count": 0,
                        "articles": [],
                    }
                raise
                
            articles = parse_feed(content, cutoff, final_url)
            
            # Tag articles with topics and validate domains
            validated_articles = []
            for article in articles:
                article["topics"] = topics[:]
                if validate_article_domain(article.get("link", ""), source):
                    validated_articles.append(article)
                else:
                    logging.warning(f"⚠️ {name}: rejected article with unexpected domain: {article.get('link', '')}")
            articles = validated_articles
            
            return {
                "source_id": source_id,
                "source_type": "rss",
                "name": name,
                "url": url,
                "priority": priority,
                "topics": topics,
                "status": "ok",
                "attempts": attempt + 1,
                "count": len(articles),
                "articles": articles,
            }
            
        except Exception as e:
            error_msg = str(e)[:100]
            logging.debug(f"Attempt {attempt + 1} failed for {name}: {error_msg}")
            
            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY * (2 ** attempt))  # Exponential backoff
                continue
            else:
                return {
                    "source_id": source_id,
                    "source_type": "rss",
                    "name": name,
                    "url": url,
                    "priority": priority,
                    "topics": topics,
                    "status": "error",
                    "attempts": attempt + 1,
                    "error": error_msg,
                    "count": 0,
                    "articles": [],
                }


def load_sources(defaults_dir: Path, config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load RSS sources from unified configuration with overlay support."""
    try:
        from config_loader import load_merged_sources
    except ImportError:
        # Fallback for relative import
        import sys
        sys.path.append(str(Path(__file__).parent))
        from config_loader import load_merged_sources
    
    # Load merged sources from defaults + optional user overlay
    all_sources = load_merged_sources(defaults_dir, config_dir)
    
    # Filter RSS sources that are enabled
    rss_sources = []
    for source in all_sources:
        if source.get("type") == "rss" and source.get("enabled", True):
            rss_sources.append(source)
            
    logging.info(f"Loaded {len(rss_sources)} enabled RSS sources")
    return rss_sources


def main():
    """Main RSS fetching function."""
    parser = argparse.ArgumentParser(
        description="Parallel RSS/Atom feed fetcher for tech-news-digest. "
                   "Fetches enabled RSS sources from unified configuration, "
                   "filters by time window, and outputs structured article data.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 fetch-rss.py
    python3 fetch-rss.py --defaults config/defaults --config workspace/config --hours 48 -o results.json
    python3 fetch-rss.py --config workspace/config --verbose  # backward compatibility
        """
    )
    
    parser.add_argument(
        "--defaults",
        type=Path,
        default=Path("config/defaults"),
        help="Default configuration directory with skill defaults (default: config/defaults)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="User configuration directory for overlays (optional)"
    )
    
    parser.add_argument(
        "--hours",
        type=int,
        default=48,
        help="Time window in hours for articles (default: 48)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output JSON path (default: auto-generated temp file)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Bypass ETag/Last-Modified conditional request cache"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch even if cached output exists"
    )
    
    args = parser.parse_args()
    logger = setup_logging(args.verbose)
    
    # Resume support: skip if output exists, is valid JSON, and < 1 hour old
    if args.output and args.output.exists() and not args.force:
        try:
            age_seconds = time.time() - args.output.stat().st_mtime
            if age_seconds < 3600:
                with open(args.output, 'r') as f:
                    json.load(f)  # validate JSON
                logger.info(f"Skipping (cached output exists): {args.output}")
                return 0
        except (json.JSONDecodeError, OSError):
            pass
    
    # Auto-generate unique output path if not specified
    if not args.output:
        fd, temp_path = tempfile.mkstemp(prefix="tech-news-digest-rss-", suffix=".json")
        os.close(fd)
        args.output = Path(temp_path)
    
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
        
        # Backward compatibility: if only --config provided, use old behavior
        if args.config and args.defaults == Path("config/defaults") and not args.defaults.exists():
            logger.debug("Backward compatibility mode: using --config as sole source")
            sources = load_sources(args.config, None)
        else:
            sources = load_sources(args.defaults, args.config)
        
        if not sources:
            logger.warning("No RSS sources found or all disabled")
            
        logger.info(f"Fetching {len(sources)} RSS feeds (window: {args.hours}h)")
        
        # Check feedparser availability
        if HAS_FEEDPARSER:
            logger.debug("Using feedparser library for parsing")
        else:
            logger.info("feedparser not available, using regex parsing")
        
        # Initialize cache
        _get_rss_cache(no_cache=args.no_cache)
        
        results = []
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(fetch_feed_with_retry, source, cutoff, args.no_cache): source 
                      for source in sources}
            
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                
                if result["status"] == "ok":
                    logger.debug(f"✅ {result['name']}: {result['count']} articles")
                else:
                    logger.debug(f"❌ {result['name']}: {result['error']}")

        # Flush conditional request cache
        _flush_rss_cache()
        
        # Sort: priority first, then by article count
        results.sort(key=lambda x: (not x.get("priority", False), -x.get("count", 0)))

        ok_count = sum(1 for r in results if r["status"] == "ok")
        total_articles = sum(r.get("count", 0) for r in results)

        output = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "source_type": "rss",
            "defaults_dir": str(args.defaults),
            "config_dir": str(args.config) if args.config else None,
            "hours": args.hours,
            "feedparser_available": HAS_FEEDPARSER,
            "sources_total": len(results),
            "sources_ok": ok_count,
            "total_articles": total_articles,
            "sources": results,
        }

        # Write output
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"✅ Done: {ok_count}/{len(results)} feeds ok, "
                   f"{total_articles} articles → {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"💥 RSS fetch failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())