#!/usr/bin/env python3
"""
Fetch Twitter/X posts from KOL accounts using X API.

Reads sources.json, filters Twitter sources, fetches recent posts using
either the official X API v2 or twitterapi.io, and outputs structured JSON.

Usage:
    python3 fetch-twitter.py [--config CONFIG_DIR] [--hours 48] [--output FILE] [--verbose]
    python3 fetch-twitter.py --backend twitterapiio  # force twitterapi.io backend

Environment:
    TWITTER_API_BACKEND - Backend selection: "auto" (default), "getxapi", "twitterapiio", or "official"
                        Auto priority: getxapi ($0.001/call) > twitterapi.io (~$5/mo) > official X API
    GETX_API_KEY        - GetXAPI API key (preferred backend, $0.001 per call)
    TWITTERAPI_IO_KEY   - twitterapi.io API key (alternative backend, ~$5/month)
    X_BEARER_TOKEN      - Twitter/X official API v2 bearer token (fallback)
"""

import json
import sys
import os
import argparse
import logging
import time
import tempfile
import re
import threading
from abc import ABC, abstractmethod
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode, quote
from pathlib import Path
from typing import Dict, List, Any, Optional

TIMEOUT = 30
MAX_WORKERS = 5  # Lower for API rate limits
RETRY_COUNT = 2
RETRY_DELAY = 2.0
MAX_TWEETS_PER_USER = 20
ID_CACHE_PATH = "/tmp/tech-news-digest-twitter-id-cache.json"
ID_CACHE_TTL_DAYS = 7

# Twitter API v2 endpoints
OFFICIAL_API_BASE = "https://api.x.com/2"
USER_LOOKUP_ENDPOINT = f"{OFFICIAL_API_BASE}/users/by"

# twitterapi.io endpoints
TWITTERAPIIO_BASE = "https://api.twitterapi.io"
GETXAPI_BASE = "https://api.getxapi.com"


def setup_logging(verbose: bool) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def clean_tweet_text(text: str) -> str:
    """Clean tweet text for better display."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Truncate if too long
    if len(text) > 280:
        text = text[:277] + "..."
    return text


# ---------------------------------------------------------------------------
# Rate limiting
# ---------------------------------------------------------------------------

class RateLimiter:
    """Simple token-bucket rate limiter."""
    def __init__(self, qps: float):
        self._lock = threading.Lock()
        self._min_interval = 1.0 / qps
        self._last = 0.0

    def wait(self):
        with self._lock:
            now = time.monotonic()
            wait_time = self._min_interval - (now - self._last)
            if wait_time > 0:
                time.sleep(wait_time)
            self._last = time.monotonic()


# ---------------------------------------------------------------------------
# Backend abstraction
# ---------------------------------------------------------------------------

class TwitterBackend(ABC):
    """Base class for Twitter API backends."""

    @staticmethod
    def _make_result(source, articles, attempt):
        return {
            "source_id": source["id"],
            "source_type": "twitter",
            "name": source["name"],
            "handle": source["handle"].lstrip('@'),
            "priority": source["priority"],
            "topics": source["topics"],
            "status": "ok",
            "attempts": attempt + 1,
            "count": len(articles),
            "articles": articles,
        }

    @staticmethod
    def _make_error(source, error_msg, attempt):
        return {
            "source_id": source["id"],
            "source_type": "twitter",
            "name": source["name"],
            "handle": source["handle"].lstrip('@'),
            "priority": source["priority"],
            "topics": source["topics"],
            "status": "error",
            "attempts": attempt + 1,
            "error": error_msg,
            "count": 0,
            "articles": [],
        }

    @abstractmethod
    def fetch_all(self, sources: List[Dict[str, Any]], cutoff: datetime) -> List[Dict[str, Any]]:
        """Fetch tweets for all sources. Returns list of source result dicts."""


class OfficialBackend(TwitterBackend):
    """Official X API v2 backend (existing logic)."""

    def __init__(self, bearer_token: str, no_cache: bool = False):
        self.bearer_token = bearer_token
        self.no_cache = no_cache

    # -- ID cache helpers --

    @staticmethod
    def _load_id_cache() -> Dict[str, Any]:
        try:
            with open(ID_CACHE_PATH, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    @staticmethod
    def _save_id_cache(cache: Dict[str, Any]) -> None:
        try:
            with open(ID_CACHE_PATH, 'w') as f:
                json.dump(cache, f)
        except Exception as e:
            logging.warning(f"Failed to save ID cache: {e}")

    def _batch_resolve_user_ids(self, handles: List[str]) -> Dict[str, str]:
        now = time.time()
        cache = {} if self.no_cache else self._load_id_cache()
        ttl_seconds = ID_CACHE_TTL_DAYS * 86400

        result: Dict[str, str] = {}
        to_resolve: List[str] = []
        for handle in handles:
            key = handle.lower()
            entry = cache.get(key)
            if entry and (now - entry.get("ts", 0)) < ttl_seconds:
                result[key] = entry["id"]
            else:
                to_resolve.append(handle)

        if to_resolve:
            logging.info(f"Batch resolving {len(to_resolve)} usernames (cached: {len(result)})")
            headers = {
                "Authorization": f"Bearer {self.bearer_token}",
                "User-Agent": "TechDigest/2.0"
            }
            for i in range(0, len(to_resolve), 100):
                batch = to_resolve[i:i+100]
                url = f"{USER_LOOKUP_ENDPOINT}?{urlencode({'usernames': ','.join(batch)})}"
                try:
                    req = Request(url, headers=headers)
                    with urlopen(req, timeout=TIMEOUT) as resp:
                        data = json.loads(resp.read().decode())

                    if 'data' in data:
                        for user in data['data']:
                            key = user['username'].lower()
                            result[key] = user['id']
                            cache[key] = {"id": user['id'], "ts": now}

                    if 'errors' in data:
                        for err in data['errors']:
                            logging.warning(f"User lookup error: {err.get('detail', err)}")

                except Exception as e:
                    logging.error(f"Batch user lookup failed: {e}")
                    for handle in batch:
                        try:
                            fallback_url = f"{USER_LOOKUP_ENDPOINT}?{urlencode({'usernames': handle})}"
                            req = Request(fallback_url, headers=headers)
                            with urlopen(req, timeout=TIMEOUT) as resp:
                                fallback_data = json.loads(resp.read().decode())
                            if 'data' in fallback_data and fallback_data['data']:
                                key = handle.lower()
                                result[key] = fallback_data['data'][0]['id']
                                cache[key] = {"id": result[key], "ts": now}
                        except Exception as e2:
                            logging.warning(f"Individual lookup failed for @{handle}: {e2}")

            if not self.no_cache:
                self._save_id_cache(cache)
        else:
            logging.info(f"All {len(result)} usernames resolved from cache")

        return result

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        try:
            if date_str.endswith('Z'):
                date_str = date_str[:-1] + '+00:00'
            return datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            logging.debug(f"Failed to parse Twitter date: {date_str}")
            return None

    def _fetch_user_tweets(self, source: Dict[str, Any], cutoff: datetime,
                           user_id: Optional[str] = None) -> Dict[str, Any]:
        handle = source["handle"].lstrip('@')
        topics = source["topics"]

        for attempt in range(RETRY_COUNT + 1):
            try:
                params = {
                    "max_results": min(MAX_TWEETS_PER_USER, 100),
                    "tweet.fields": "created_at,public_metrics,context_annotations,referenced_tweets",
                    "expansions": "author_id",
                    "user.fields": "verified,public_metrics"
                }

                if not user_id:
                    user_url = f"{USER_LOOKUP_ENDPOINT}?{urlencode({'usernames': handle})}"
                    headers = {
                        "Authorization": f"Bearer {self.bearer_token}",
                        "User-Agent": "TechDigest/2.0"
                    }
                    req = Request(user_url, headers=headers)
                    with urlopen(req, timeout=TIMEOUT) as resp:
                        user_data = json.loads(resp.read().decode())
                    if 'data' not in user_data or not user_data['data']:
                        raise ValueError(f"User not found: {handle}")
                    user_id = user_data['data'][0]['id']

                headers = {
                    "Authorization": f"Bearer {self.bearer_token}",
                    "User-Agent": "TechDigest/2.0"
                }

                time.sleep(0.3)

                tweets_url = f"{OFFICIAL_API_BASE}/users/{user_id}/tweets?{urlencode(params)}"
                req = Request(tweets_url, headers=headers)

                with urlopen(req, timeout=TIMEOUT) as resp:
                    tweets_data = json.loads(resp.read().decode())

                articles = []
                if 'data' in tweets_data:
                    for tweet in tweets_data['data']:
                        created_at = self._parse_date(tweet.get('created_at', ''))
                        if not created_at or created_at < cutoff:
                            continue

                        text = tweet.get('text', '')
                        if text.startswith('RT @'):
                            continue
                        referenced = tweet.get('referenced_tweets', [])
                        if any(ref.get('type') == 'replied_to' for ref in referenced):
                            continue

                        articles.append({
                            "title": clean_tweet_text(text),
                            "link": f"https://twitter.com/{handle}/status/{tweet['id']}",
                            "date": created_at.isoformat(),
                            "topics": topics[:],
                            "metrics": tweet.get('public_metrics', {}),
                            "tweet_id": tweet['id']
                        })

                return self._make_result(source, articles, attempt)

            except HTTPError as e:
                if e.code == 429:
                    error_msg = "Rate limit exceeded"
                    logging.warning(f"Rate limit hit for @{handle}, attempt {attempt + 1}")
                    if attempt < RETRY_COUNT:
                        time.sleep(60)
                        continue
                else:
                    error_msg = f"HTTP {e.code}: {e.reason}"

            except Exception as e:
                error_msg = str(e)[:100]
                logging.debug(f"Attempt {attempt + 1} failed for @{handle}: {error_msg}")

            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY * (2 ** attempt))
                continue

            return self._make_error(source, error_msg, attempt)

    def fetch_all(self, sources: List[Dict[str, Any]], cutoff: datetime) -> List[Dict[str, Any]]:
        all_handles = [s["handle"].lstrip('@') for s in sources]
        user_id_map = self._batch_resolve_user_ids(all_handles)

        results: List[Dict[str, Any]] = []
        total = len(sources)
        done = 0
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {}
            for source in sources:
                handle = source["handle"].lstrip('@')
                resolved_id = user_id_map.get(handle.lower())
                futures[pool.submit(self._fetch_user_tweets, source, cutoff, resolved_id)] = source

            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                done += 1
                if result["status"] == "ok":
                    logging.info(f"[{done}/{total}] ✅ @{result['handle']}: {result['count']} tweets"
                                 + (f" (top: {result['articles'][0]['metrics']['like_count']}❤️)" if result.get('articles') else ""))
                else:
                    logging.warning(f"[{done}/{total}] ❌ @{result['handle']}: {result.get('error','unknown')}")

        return results


class TwitterApiIoBackend(TwitterBackend):
    """twitterapi.io backend."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._limiter = RateLimiter(qps=5)

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime]:
        """Parse twitterapi.io date format: 'Tue Dec 10 07:00:30 +0000 2024'."""
        try:
            return datetime.strptime(date_str, "%a %b %d %H:%M:%S %z %Y")
        except (ValueError, TypeError):
            logging.debug(f"Failed to parse twitterapi.io date: {date_str}")
            return None

    def _parse_tweets_page(self, tweets: list, handle: str, topics: list, cutoff: datetime) -> list:
        """Parse a page of tweets into article dicts."""
        articles = []
        for tweet in tweets:
            # Skip retweets
            if tweet.get("retweeted_tweet"):
                continue
            created_at = self._parse_date(tweet.get("createdAt", ""))
            if not created_at or created_at < cutoff:
                continue

            text = tweet.get("text", "")
            if text.startswith("RT @"):
                continue

            tweet_id = tweet.get("id", "")
            link = tweet.get("url") or f"https://twitter.com/{handle}/status/{tweet_id}"

            articles.append({
                "title": clean_tweet_text(text),
                "link": link,
                "date": created_at.isoformat(),
                "topics": topics[:],
                "metrics": {
                    "like_count": tweet.get("likeCount", 0),
                    "retweet_count": tweet.get("retweetCount", 0),
                    "reply_count": tweet.get("replyCount", 0),
                    "quote_count": tweet.get("quoteCount", 0),
                    "impression_count": tweet.get("viewCount", 0),
                },
                "tweet_id": tweet_id,
            })
        return articles

    def _fetch_user_tweets(self, source: Dict[str, Any], cutoff: datetime) -> Dict[str, Any]:
        handle = source["handle"].lstrip('@')
        topics = source["topics"]

        for attempt in range(RETRY_COUNT + 1):
            try:
                params = urlencode({
                    "userName": handle,
                    "includeReplies": "false",
                })
                url = f"{TWITTERAPIIO_BASE}/twitter/user/last_tweets?{params}"
                headers = {
                    "X-API-Key": self.api_key,
                    "User-Agent": "TechDigest/2.0",
                }

                self._limiter.wait()

                req = Request(url, headers=headers)
                with urlopen(req, timeout=TIMEOUT) as resp:
                    raw = json.loads(resp.read().decode())

                # API wraps response in {"data": {...}} envelope
                data = raw.get("data", raw)

                articles = self._parse_tweets_page(
                    data.get("tweets", []), handle, topics, cutoff
                )

                # Pagination: fetch one more page if available and all tweets still in window
                has_next = data.get("has_next_page", False)
                next_cursor = data.get("next_cursor")
                if has_next and next_cursor and articles:
                    oldest = min(a["date"] for a in articles)
                    if oldest >= cutoff.isoformat():
                        self._limiter.wait()
                        page2_params = urlencode({
                            "userName": handle,
                            "includeReplies": "false",
                            "cursor": next_cursor,
                        })
                        page2_url = f"{TWITTERAPIIO_BASE}/twitter/user/last_tweets?{page2_params}"
                        req2 = Request(page2_url, headers=headers)
                        with urlopen(req2, timeout=TIMEOUT) as resp2:
                            raw2 = json.loads(resp2.read().decode())
                        data2 = raw2.get("data", raw2)
                        articles.extend(self._parse_tweets_page(
                            data2.get("tweets", []), handle, topics, cutoff
                        ))
                        has_next = data2.get("has_next_page", False)

                # Truncation warning
                if has_next and articles:
                    oldest = min(a["date"] for a in articles)
                    if oldest >= cutoff.isoformat():
                        logging.warning(f"@{handle}: results may be truncated ({len(articles)} tweets, more available)")

                return self._make_result(source, articles, attempt)

            except HTTPError as e:
                if e.code == 429:
                    error_msg = "Rate limit exceeded"
                    logging.warning(f"Rate limit hit for @{handle}, attempt {attempt + 1}")
                    if attempt < RETRY_COUNT:
                        time.sleep(5)
                        continue
                else:
                    error_msg = f"HTTP {e.code}: {e.reason}"

            except Exception as e:
                error_msg = str(e)[:100]
                logging.debug(f"Attempt {attempt + 1} failed for @{handle}: {error_msg}")

            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY * (2 ** attempt))
                continue

            return self._make_error(source, error_msg, attempt)

    def fetch_all(self, sources: List[Dict[str, Any]], cutoff: datetime) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        total = len(sources)
        done = 0
        with ThreadPoolExecutor(max_workers=3) as pool:
            futures = {pool.submit(self._fetch_user_tweets, source, cutoff): source
                       for source in sources}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                done += 1
                if result["status"] == "ok":
                    logging.info(f"[{done}/{total}] ✅ @{result['handle']}: {result['count']} tweets"
                                 + (f" (top: {result['articles'][0]['metrics']['like_count']}❤️)" if result['articles'] else ""))
                else:
                    logging.warning(f"[{done}/{total}] ❌ @{result['handle']}: {result['error']}")

        return results


class GetXApiBackend(TwitterBackend):
    """GetXAPI backend."""

    def __init__(self, api_key: str):
        """Initialize GetXAPI backend with API key validation."""
        if not api_key or len(api_key) < 10:
            raise ValueError("Invalid GETX_API_KEY format - expected at least 10 characters")
        self.api_key = api_key
        self.logger = logging.getLogger("fetch-twitter")

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse GetXAPI date string with multiple format support.
        
        Supported formats:
        - 'Tue Dec 10 07:00:30 +0000 2024' (Twitter format)
        - '2024-12-10T07:00:30+00:00' (ISO 8601)
        - '2024-12-10 07:00:30' (Simple datetime)
        """
        formats = [
            "%a %b %d %H:%M:%S %z %Y",      # Twitter format
            "%Y-%m-%dT%H:%M:%S%z",          # ISO 8601
            "%Y-%m-%d %H:%M:%S",            # Simple datetime
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                continue
        
        self.logger.debug(f"Failed to parse date '{date_str}' with all known formats")
        return None

    def _parse_tweets_page(self, tweets: list, handle: str, topics: list, cutoff: datetime) -> list:
        articles = []
        for tweet in tweets:
            tweet_id = tweet.get("id")
            text = tweet.get("text")
            created_at_raw = tweet.get("createdAt")
            if not tweet_id or not text or not created_at_raw:
                continue
            if tweet.get("isReply"):
                continue
            if text.startswith("RT @"):
                continue

            created_at = self._parse_date(created_at_raw)
            if not created_at or created_at < cutoff:
                continue

            link = tweet.get("url") or f"https://x.com/{handle}/status/{tweet_id}"

            articles.append({
                "title": clean_tweet_text(text),
                "link": link,
                "date": created_at.isoformat(),
                "topics": topics[:],
                "metrics": {
                    "like_count": tweet.get("likeCount", 0),
                    "retweet_count": tweet.get("retweetCount", 0),
                    "reply_count": tweet.get("replyCount", 0),
                    "quote_count": tweet.get("quoteCount", 0),
                    "impression_count": tweet.get("viewCount", 0),
                },
                "tweet_id": tweet_id,
            })
        return articles

    def _fetch_user_tweets(self, source: Dict[str, Any], cutoff: datetime) -> Dict[str, Any]:
        handle = source["handle"].lstrip('@')
        topics = source["topics"]

        for attempt in range(RETRY_COUNT + 1):
            try:
                url = f"{GETXAPI_BASE}/twitter/user/tweets?{urlencode({'userName': handle})}"
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": "TechDigest/2.0",
                }

                req = Request(url, headers=headers)
                with urlopen(req, timeout=TIMEOUT) as resp:
                    raw = json.loads(resp.read().decode())

                if raw.get("error"):
                    return self._make_error(source, str(raw["error"])[:100], attempt)

                articles = self._parse_tweets_page(
                    raw.get("tweets", []), handle, topics, cutoff
                )

                has_more = raw.get("has_more", False)
                next_cursor = raw.get("next_cursor")
                
                # Fetch page 2 if more results available (with retry)
                if has_more and next_cursor and articles:
                    oldest = min(datetime.fromisoformat(a["date"]) for a in articles)
                    if oldest >= cutoff:
                        for page_attempt in range(RETRY_COUNT + 1):
                            try:
                                page2_url = f"{GETXAPI_BASE}/twitter/user/tweets?{urlencode({'userName': handle, 'cursor': next_cursor})}"
                                req2 = Request(page2_url, headers=headers)
                                with urlopen(req2, timeout=TIMEOUT) as resp2:
                                    raw2 = json.loads(resp2.read().decode())
                                if raw2.get("error"):
                                    raise ValueError(str(raw2["error"])[:100])
                                articles.extend(self._parse_tweets_page(
                                    raw2.get("tweets", []), handle, topics, cutoff
                                ))
                                has_more = raw2.get("has_more", False)
                                break  # Success
                            except Exception as e:
                                self.logger.warning(f"@{handle}: page 2 attempt {page_attempt + 1} failed: {e}")
                                if page_attempt < RETRY_COUNT:
                                    time.sleep(RETRY_DELAY * (2 ** page_attempt))
                                else:
                                    self.logger.warning(f"@{handle}: page 2 failed after {RETRY_COUNT} attempts, keeping page 1 results")
                                    has_more = False

                if has_more and articles:
                    oldest = min(datetime.fromisoformat(a["date"]) for a in articles)
                    if oldest >= cutoff:
                        logging.warning(f"@{handle}: results may be truncated ({len(articles)} tweets, more available)")

                return self._make_result(source, articles, attempt)

            except HTTPError as e:
                if e.code == 429:
                    error_msg = "Rate limit exceeded"
                    logging.warning(f"Rate limit hit for @{handle}, attempt {attempt + 1}")
                    if attempt < RETRY_COUNT:
                        time.sleep(5)
                        continue
                else:
                    error_msg = f"HTTP {e.code}: {e.reason}"

            except Exception as e:
                error_msg = str(e)[:100]
                logging.debug(f"Attempt {attempt + 1} failed for @{handle}: {error_msg}")

            if attempt < RETRY_COUNT:
                time.sleep(RETRY_DELAY * (2 ** attempt))
                continue

            return self._make_error(source, error_msg, attempt)

    def fetch_all(self, sources: List[Dict[str, Any]], cutoff: datetime) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        total = len(sources)
        done = 0
        with ThreadPoolExecutor(max_workers=5) as pool:
            futures = {pool.submit(self._fetch_user_tweets, source, cutoff): source
                       for source in sources}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                done += 1
                if result["status"] == "ok":
                    logging.info(f"[{done}/{total}] ✅ @{result['handle']}: {result['count']} tweets"
                                 + (f" (top: {result['articles'][0]['metrics']['like_count']}❤️)" if result['articles'] else ""))
                else:
                    logging.warning(f"[{done}/{total}] ❌ @{result['handle']}: {result['error']}")

        return results


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------

def select_backend(backend_name: str, no_cache: bool = False) -> Optional[TwitterBackend]:
    """Select and instantiate the appropriate backend.

    Returns None if no credentials are available for the chosen backend.
    """
    if backend_name == "getxapi":
        key = os.getenv("GETX_API_KEY")
        if not key:
            logging.error("GETX_API_KEY not set (required for getxapi backend)")
            return None
        logging.info("Using GetXAPI backend")
        return GetXApiBackend(key)

    if backend_name == "twitterapiio":
        key = os.getenv("TWITTERAPI_IO_KEY")
        if not key:
            logging.error("TWITTERAPI_IO_KEY not set (required for twitterapiio backend)")
            return None
        logging.info("Using twitterapi.io backend")
        return TwitterApiIoBackend(key)

    if backend_name == "official":
        token = os.getenv("X_BEARER_TOKEN")
        if not token:
            logging.error("X_BEARER_TOKEN not set (required for official backend)")
            return None
        logging.info("Using official X API v2 backend")
        return OfficialBackend(token, no_cache=no_cache)

    # auto: try getxapi first, then twitterapiio, then official
    if backend_name == "auto":
        getx_key = os.getenv("GETX_API_KEY")
        if getx_key:
            logging.info("Auto-selected GetXAPI backend (GETX_API_KEY set)")
            return GetXApiBackend(getx_key)
        key = os.getenv("TWITTERAPI_IO_KEY")
        if key:
            logging.info("Auto-selected twitterapi.io backend (TWITTERAPI_IO_KEY set)")
            return TwitterApiIoBackend(key)
        token = os.getenv("X_BEARER_TOKEN")
        if token:
            logging.info("Auto-selected official X API v2 backend (X_BEARER_TOKEN set)")
            return OfficialBackend(token, no_cache=no_cache)
        logging.warning("No Twitter API credentials found (checked GETX_API_KEY, TWITTERAPI_IO_KEY, X_BEARER_TOKEN)")
        return None

    logging.error(f"Unknown backend: {backend_name}")
    return None


# ---------------------------------------------------------------------------
# Source loading
# ---------------------------------------------------------------------------

def load_twitter_sources(defaults_dir: Path, config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load Twitter sources from unified configuration with overlay support."""
    try:
        from config_loader import load_merged_sources
    except ImportError:
        # Fallback for relative import
        import sys
        sys.path.append(str(Path(__file__).parent))
        from config_loader import load_merged_sources

    # Load merged sources from defaults + optional user overlay
    all_sources = load_merged_sources(defaults_dir, config_dir)

    # Filter Twitter sources that are enabled
    twitter_sources = []
    for source in all_sources:
        if source.get("type") == "twitter" and source.get("enabled", True):
            if not source.get("handle"):
                logging.warning(f"Twitter source {source.get('id')} missing handle, skipping")
                continue
            twitter_sources.append(source)

    logging.info(f"Loaded {len(twitter_sources)} enabled Twitter sources")
    return twitter_sources


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Main Twitter fetching function."""
    parser = argparse.ArgumentParser(
        description="Fetch recent tweets from Twitter/X KOL accounts. "
                   "Supports official X API v2, GetXAPI, and twitterapi.io backends.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    export X_BEARER_TOKEN="your_token_here"
    python3 fetch-twitter.py
    python3 fetch-twitter.py --defaults config/defaults --config workspace/config --hours 24 -o results.json
    python3 fetch-twitter.py --backend twitterapiio  # use twitterapi.io
    python3 fetch-twitter.py --config workspace/config --verbose  # backward compatibility
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
        help="Time window in hours for tweets (default: 48)"
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
        help="Bypass username→ID cache (official backend only)"
    )

    parser.add_argument(
        "--force",
        action="store_true",
        help="Force re-fetch even if cached output exists"
    )

    parser.add_argument(
        "--backend",
        choices=["official", "twitterapiio", "getxapi", "auto"],
        default=None,
        help="Twitter API backend (overrides TWITTER_API_BACKEND env var). "
             "auto = getxapi if GETX_API_KEY set, else twitterapiio if TWITTERAPI_IO_KEY set, else official if X_BEARER_TOKEN set"
    )

    args = parser.parse_args()
    logger = setup_logging(args.verbose)

    # Resume support: skip if output exists, is valid JSON, and < 1 hour old
    if args.output and args.output.exists() and not args.force:
        try:
            age_seconds = time.time() - args.output.stat().st_mtime
            if age_seconds < 3600:
                with open(args.output, 'r') as f:
                    json.load(f)
                logger.info(f"Skipping (cached output exists): {args.output}")
                return 0
        except (json.JSONDecodeError, OSError):
            pass

    # Resolve backend: CLI arg > env var > default (auto)
    backend_name = args.backend or os.getenv("TWITTER_API_BACKEND", "auto")

    backend = select_backend(backend_name, no_cache=args.no_cache)
    if not backend:
        logger.warning("No Twitter backend available. Writing empty result and skipping Twitter fetch.")
        empty_result = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "source_type": "twitter",
            "backend": backend_name,
            "hours": args.hours,
            "sources_total": 0,
            "sources_ok": 0,
            "total_articles": 0,
            "sources": [],
            "skipped_reason": f"No credentials for backend '{backend_name}'"
        }
        output_path = args.output or Path("/tmp/td-twitter.json")
        with open(output_path, "w") as f:
            json.dump(empty_result, f, indent=2)
        print(f"Output (empty): {output_path}")
        return 0

    # Auto-generate unique output path if not specified
    if not args.output:
        fd, temp_path = tempfile.mkstemp(prefix="tech-news-digest-twitter-", suffix=".json")
        os.close(fd)
        args.output = Path(temp_path)

    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)

        # Backward compatibility: if only --config provided, use old behavior
        if args.config and args.defaults == Path("config/defaults") and not args.defaults.exists():
            logger.debug("Backward compatibility mode: using --config as sole source")
            sources = load_twitter_sources(args.config, None)
        else:
            sources = load_twitter_sources(args.defaults, args.config)

        if not sources:
            logger.warning("No Twitter sources found or all disabled")

        logger.info(f"Fetching {len(sources)} Twitter accounts (window: {args.hours}h, backend: {backend_name})")

        results = backend.fetch_all(sources, cutoff)

        # Sort: priority first, then by article count
        results.sort(key=lambda x: (not x.get("priority", False), -x.get("count", 0)))

        ok_count = sum(1 for r in results if r["status"] == "ok")
        total_tweets = sum(r.get("count", 0) for r in results)

        output = {
            "generated": datetime.now(timezone.utc).isoformat(),
            "source_type": "twitter",
            "backend": backend_name,
            "defaults_dir": str(args.defaults),
            "config_dir": str(args.config) if args.config else None,
            "hours": args.hours,
            "sources_total": len(results),
            "sources_ok": ok_count,
            "total_articles": total_tweets,
            "sources": results,
        }

        # Write output
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"✅ Done: {ok_count}/{len(results)} accounts ok, "
                   f"{total_tweets} tweets → {args.output}")

        return 0

    except Exception as e:
        logger.error(f"💥 Twitter fetch failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
