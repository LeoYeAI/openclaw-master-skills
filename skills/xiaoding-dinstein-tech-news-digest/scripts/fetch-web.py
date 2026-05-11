#!/usr/bin/env python3
"""
Fetch web search results for tech digest topics.

Reads topics.json, performs web searches for each topic's search queries,
and outputs structured JSON with search results tagged by topics.

Usage:
    python3 fetch-web.py [--config CONFIG_DIR] [--freshness 48h] [--output FILE] [--verbose]

Note: This script can use Brave Search API if BRAVE_API_KEY is set, otherwise
it provides a JSON interface for agents to use web_search tool.
"""

import json
import sys
import os
import argparse
import logging
import time
import tempfile
import re
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from urllib.request import urlopen, Request
from urllib.error import HTTPError
from urllib.parse import urlencode

TIMEOUT = 30
MAX_RESULTS_PER_QUERY = 5
RETRY_COUNT = 1
RETRY_DELAY = 2.0

# Brave Search API
BRAVE_API_BASE = "https://api.search.brave.com/res/v1/web/search"
TAVILY_API_BASE = "https://api.tavily.com/search"
BRAVE_RATE_LIMIT_CACHE = "/tmp/tech-news-digest-brave-rate-limit.json"


def setup_logging(verbose: bool) -> logging.Logger:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def get_brave_api_keys() -> List[str]:
    """Get Brave Search API keys from environment.
    
    Supports multiple keys via comma-separated BRAVE_API_KEYS (preferred)
    or BRAVE_API_KEY (single key fallback):
        export BRAVE_API_KEYS="key1,key2,key3"
        export BRAVE_API_KEY="key1"  # fallback for single key
    """
    raw = os.getenv('BRAVE_API_KEYS', '') or os.getenv('BRAVE_API_KEY', '')
    if not raw:
        return []
    return [k.strip() for k in raw.split(',') if k.strip()]


def get_brave_api_key() -> Optional[str]:
    """Get first available Brave API key (legacy compat)."""
    keys = get_brave_api_keys()
    return keys[0] if keys else None


def _probe_brave_key(api_key: str) -> Dict[str, Any]:
    """Probe a single Brave API key. Returns {qps, workers, exhausted, error}."""
    try:
        params = urlencode({'q': 'test', 'count': 1})
        url = f"{BRAVE_API_BASE}?{params}"
        req = Request(url, headers={
            'Accept': 'application/json',
            'X-Subscription-Token': api_key,
            'User-Agent': 'TechDigest/2.0'
        })
        with urlopen(req, timeout=TIMEOUT) as resp:
            limit_header = resp.headers.get('x-ratelimit-limit', '1')
            remaining = resp.headers.get('x-ratelimit-remaining', '')
            per_second = int(limit_header.split(',')[0].strip())
            resp.read()

        exhausted = False
        if remaining.isdigit() and int(remaining) == 0:
            exhausted = True

        workers = min(per_second // 2, 5) if per_second >= 10 else 1
        return {'qps': per_second, 'workers': workers, 'exhausted': exhausted, 'error': None}
    except HTTPError as e:
        if e.code == 429:
            return {'qps': 1, 'workers': 1, 'exhausted': True, 'error': '429 rate limited'}
        return {'qps': 1, 'workers': 1, 'exhausted': False, 'error': f'HTTP {e.code}'}
    except Exception as e:
        return {'qps': 1, 'workers': 1, 'exhausted': False, 'error': str(e)}


def select_brave_key_and_limits(keys: List[str]) -> Tuple[Optional[str], int, int]:
    """Select the best available Brave API key and detect rate limits.
    
    Tries each key in order. Skips exhausted keys (cached for 24h).
    Returns (api_key, max_qps, max_workers) or (None, 0, 0) if all exhausted.
    """
    if not keys:
        return None, 0, 0

    # Override via env var
    brave_plan = os.getenv('BRAVE_PLAN', '').lower()
    plan_qps = None
    if brave_plan == 'free':
        plan_qps, plan_workers = 1, 1
    elif brave_plan == 'pro':
        plan_qps, plan_workers = 15, 5

    # Load cache
    cache = {}
    try:
        with open(BRAVE_RATE_LIMIT_CACHE, 'r') as f:
            cache = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass

    now = time.time()
    key_cache = cache.get('keys', {})

    for i, key in enumerate(keys):
        key_id = f"key_{i}"  # Don't log actual keys
        cached = key_cache.get(key_id, {})
        cache_age = now - cached.get('ts', 0)

        # Use cache if fresh (24h)
        if cache_age < 86400 and cached.get('exhausted'):
            logging.debug(f"Brave {key_id}: exhausted (cached), skipping")
            continue

        if plan_qps is not None:
            logging.info(f"Using Brave {key_id} with BRAVE_PLAN={brave_plan} override: {plan_qps} QPS")
            return key, plan_qps, plan_workers

        if cache_age < 86400 and 'qps' in cached and not cached.get('exhausted'):
            qps = cached['qps']
            workers = cached['workers']
            logging.info(f"Using Brave {key_id} (cached): {qps} QPS, {workers} workers")
            return key, qps, workers

        # Probe
        result = _probe_brave_key(key)
        key_cache[key_id] = {'ts': now, **result}

        if result['exhausted']:
            logging.warning(f"Brave {key_id}: exhausted ({result.get('error', 'quota reached')}), trying next")
            continue

        if result['error']:
            logging.warning(f"Brave {key_id}: probe error ({result['error']}), trying next")
            continue

        logging.info(f"Using Brave {key_id}: {result['qps']} QPS, {result['workers']} workers")
        # Save cache
        try:
            cache['keys'] = key_cache
            with open(BRAVE_RATE_LIMIT_CACHE, 'w') as f:
                json.dump(cache, f)
        except OSError:
            pass
        return key, result['qps'], result['workers']

    # All keys exhausted
    logging.warning("All Brave API keys exhausted or errored")
    # Save cache
    try:
        cache['keys'] = key_cache
        with open(BRAVE_RATE_LIMIT_CACHE, 'w') as f:
            json.dump(cache, f)
    except OSError:
        pass
    return None, 0, 0


def detect_brave_rate_limit(api_key: str) -> Tuple[int, int]:
    """Legacy wrapper: detect rate limit for a single key."""
    _, qps, workers = select_brave_key_and_limits([api_key])
    return max(qps, 1), max(workers, 1)


def search_brave(query: str, api_key: str, freshness: Optional[str] = None) -> Dict[str, Any]:
    """Perform search using Brave Search API."""
    params = {
        'q': query,
        'count': MAX_RESULTS_PER_QUERY,
        'search_lang': 'en',
        'country': 'ALL',
        'safesearch': 'moderate',
        'text_decorations': 'false'
    }
    
    if freshness:
        params['freshness'] = freshness
    
    url = f"{BRAVE_API_BASE}?{urlencode(params)}"
    headers = {
        'Accept': 'application/json',
        'X-Subscription-Token': api_key,
        'User-Agent': 'TechDigest/2.0'
    }
    
    try:
        req = Request(url, headers=headers)
        with urlopen(req, timeout=TIMEOUT) as resp:
            raw = resp.read()
            # Handle gzip if server sends it anyway
            if raw[:2] == b'\x1f\x8b':
                import gzip
                raw = gzip.decompress(raw)
            data = json.loads(raw.decode())
            
        results = []
        if 'web' in data and 'results' in data['web']:
            for result in data['web']['results']:
                results.append({
                    'title': result.get('title', ''),
                    'link': result.get('url', ''),
                    'snippet': result.get('description', ''),
                    'date': datetime.now(timezone.utc).isoformat()  # Search timestamp
                })
                
        return {
            'status': 'ok',
            'query': query,
            'results': results,
            'total': len(results)
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'query': query,
            'error': str(e)[:100],
            'results': [],
            'total': 0
        }


def filter_content(text: str, must_include: List[str], exclude: List[str]) -> bool:
    """Check if content matches inclusion/exclusion criteria."""
    text_lower = text.lower()

    # Check must_include (any match)
    if must_include:
        has_required = any(keyword.lower() in text_lower for keyword in must_include)
        if not has_required:
            return False

    # Check exclude (any match disqualifies)
    if exclude:
        has_excluded = any(keyword.lower() in text_lower for keyword in exclude)
        if has_excluded:
            return False
            
    return True


def search_topic_brave(topic: Dict[str, Any], api_key: str, freshness: Optional[str] = None,
                       max_workers: int = 1, delay: float = 0.5) -> Dict[str, Any]:
    """Search all queries for a topic using Brave API.
    
    Args:
        max_workers: Number of parallel search threads (1 = sequential)
        delay: Delay between requests in sequential mode (ignored when parallel)
    """
    topic_id = topic["id"]
    queries = topic["search"]["queries"]
    must_include = topic["search"].get("must_include", [])
    exclude = topic["search"].get("exclude", [])
    
    all_results = []
    query_stats = []
    
    if max_workers > 1:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(search_brave, q, api_key, freshness): q for q in queries}
            for future in as_completed(futures):
                search_result = future.result()
                query_stats.append({
                    'query': search_result['query'],
                    'status': search_result['status'],
                    'count': search_result['total']
                })
                if search_result['status'] == 'ok':
                    for result in search_result['results']:
                        combined_text = f"{result['title']} {result['snippet']}"
                        if filter_content(combined_text, must_include, exclude):
                            result['topics'] = [topic_id]
                            all_results.append(result)
    else:
        for query in queries:
            search_result = search_brave(query, api_key, freshness)
            query_stats.append({
                'query': query,
                'status': search_result['status'],
                'count': search_result['total']
            })
            if search_result['status'] == 'ok':
                for result in search_result['results']:
                    combined_text = f"{result['title']} {result['snippet']}"
                    if filter_content(combined_text, must_include, exclude):
                        result['topics'] = [topic_id]
                        all_results.append(result)
            time.sleep(delay)
    
    return {
        'topic_id': topic_id,
        'status': 'ok',
        'queries_executed': len(queries),
        'queries_ok': sum(1 for q in query_stats if q['status'] == 'ok'),
        'query_stats': query_stats,
        'count': len(all_results),
        'articles': all_results
    }



def get_tavily_api_key() -> Optional[str]:
    """Get Tavily API key from environment."""
    return os.getenv('TAVILY_API_KEY', '').strip() or None


def search_tavily(query: str, api_key: str, topic: str = "general",
                  max_results: int = 10, search_depth: str = "basic",
                  days: Optional[int] = None) -> Dict[str, Any]:
    """Perform search using Tavily Search API.
    
    Args:
        topic: 'general' or 'news' (news for real-time updates)
        days: Limit results to the last N days (None = no limit)
    """
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": search_depth,
        "topic": topic,
        "max_results": max_results,
        "include_answer": False,
    }
    if days is not None:
        payload["days"] = days

    try:
        data = json.dumps(payload).encode()
        req = Request(TAVILY_API_BASE, data=data, headers={
            "Content-Type": "application/json",
            "User-Agent": "TechDigest/3.0"
        }, method="POST")
        with urlopen(req, timeout=TIMEOUT) as resp:
            result = json.loads(resp.read().decode())

        articles = []
        for r in result.get("results", []):
            articles.append({
                "title": r.get("title", ""),
                "link": r.get("url", ""),
                "snippet": r.get("content", "")[:300],
                "date": r.get("published_date", ""),
                "source": "tavily",
            })

        return {
            "query": query,
            "status": "ok",
            "total": len(articles),
            "results": articles,
        }
    except HTTPError as e:
        logging.warning(f"Tavily search error for '{query}': HTTP {e.code}")
        return {"query": query, "status": "error", "total": 0, "results": [], "error": f"HTTP {e.code}"}
    except Exception as e:
        logging.warning(f"Tavily search error for '{query}': {e}")
        return {"query": query, "status": "error", "total": 0, "results": [], "error": str(e)}


def search_topic_tavily(topic: Dict[str, Any], api_key: str, days: Optional[int] = None) -> Dict[str, Any]:
    """Search all queries for a topic using Tavily API."""
    topic_id = topic["id"]
    queries = topic["search"]["queries"]
    must_include = topic["search"].get("must_include", [])
    exclude = topic["search"].get("exclude", [])

    all_results = []
    query_stats = []

    for query in queries:
        search_result = search_tavily(query, api_key, topic="news", days=days)
        query_stats.append({
            "query": search_result["query"],
            "status": search_result["status"],
            "count": search_result["total"],
        })
        if search_result["status"] == "ok":
            for result in search_result["results"]:
                combined_text = f"{result['title']} {result['snippet']}"
                if filter_content(combined_text, must_include, exclude):
                    result["topics"] = [topic_id]
                    all_results.append(result)

    ok_count = sum(1 for s in query_stats if s["status"] == "ok")
    return {
        "topic": topic_id,
        "status": "ok" if ok_count > 0 else "error",
        "queries": len(queries),
        "queries_ok": ok_count,
        "count": len(all_results),
        "articles": all_results,
        "query_details": query_stats,
    }


def generate_search_interface(topic: Dict[str, Any]) -> Dict[str, Any]:
    """Generate JSON interface for agent web search."""
    topic_id = topic["id"]
    queries = topic["search"]["queries"]
    must_include = topic["search"].get("must_include", [])
    exclude = topic["search"].get("exclude", [])
    
    return {
        'topic_id': topic_id,
        'status': 'interface',
        'search_required': True,
        'queries': queries,
        'filters': {
            'must_include': must_include,
            'exclude': exclude
        },
        'instructions': [
            f"Use web_search tool for each query in 'queries' list",
            f"Filter results using 'filters.must_include' and 'filters.exclude'",
            f"Tag matching articles with topic: '{topic_id}'",
            f"Expected max results per query: {MAX_RESULTS_PER_QUERY}"
        ],
        'count': 0,
        'articles': []
    }


def load_topics(defaults_dir: Path, config_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load topics from configuration with overlay support."""
    try:
        from config_loader import load_merged_topics
    except ImportError:
        # Fallback for relative import
        import sys
        sys.path.append(str(Path(__file__).parent))
        from config_loader import load_merged_topics
    
    # Load merged topics from defaults + optional user overlay
    topics = load_merged_topics(defaults_dir, config_dir)
    logging.info(f"Loaded {len(topics)} topics for web search")
    return topics


def convert_freshness(hours: int) -> str:
    """Convert hours to Brave API freshness format."""
    if hours <= 24:
        return "pd"  # past day
    elif hours <= 168:  # 7 days
        return "pw"  # past week
    elif hours <= 720:  # 30 days
        return "pm"  # past month
    else:
        return "py"  # past year


def main():
    """Main web search function."""
    parser = argparse.ArgumentParser(
        description="Perform web searches for tech digest topics. "
                   "Can use Brave Search API (BRAVE_API_KEY) or generate interface for agents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # With Brave API
    export BRAVE_API_KEY="your_key_here"
    python3 fetch-web.py --defaults config/defaults --config workspace/config --freshness 24h
    
    # Without API (generates interface)
    python3 fetch-web.py --config workspace/config --output web-search-interface.json  # backward compatibility
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
        "--freshness",
        default="48h",
        help="Search freshness: 24h, 48h, 1w, 1m (default: 48h)"
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
                    json.load(f)
                logger.info(f"Skipping (cached output exists): {args.output}")
                return 0
        except (json.JSONDecodeError, OSError):
            pass
    
    # Auto-generate unique output path if not specified
    if not args.output:
        fd, temp_path = tempfile.mkstemp(prefix="tech-news-digest-web-", suffix=".json")
        os.close(fd)
        args.output = Path(temp_path)
    
    try:
        # Backward compatibility: if only --config provided, use old behavior
        if args.config and args.defaults == Path("config/defaults") and not args.defaults.exists():
            logger.debug("Backward compatibility mode: using --config as sole source")
            topics = load_topics(args.config, None)
        else:
            topics = load_topics(args.defaults, args.config)
        
        if not topics:
            logger.warning("No topics found")
            return 1
            
        # Backend selection: WEB_SEARCH_BACKEND env or auto-detect
        web_backend = os.getenv('WEB_SEARCH_BACKEND', 'auto').lower()
        tavily_key = get_tavily_api_key()
        brave_keys = get_brave_api_keys()
        
        use_tavily = False
        use_brave = False
        api_key = None
        max_qps = 1
        max_workers = 1
        
        if web_backend == 'tavily' and tavily_key:
            use_tavily = True
        elif web_backend == 'brave' and brave_keys:
            api_key, max_qps, max_workers = select_brave_key_and_limits(brave_keys)
            use_brave = bool(api_key)
        elif web_backend == 'auto':
            if tavily_key:
                use_tavily = True
            elif brave_keys:
                api_key, max_qps, max_workers = select_brave_key_and_limits(brave_keys)
                use_brave = bool(api_key)
        
        if use_tavily:
            logger.info(f"Using Tavily Search API for {len(topics)} topics")
            
            # Convert freshness to days for Tavily
            tavily_days = None
            if args.freshness in ('pd',): tavily_days = 1
            elif args.freshness in ('pw',): tavily_days = 7
            elif args.freshness in ('pm',): tavily_days = 30
            elif args.freshness in ('py',): tavily_days = 365
            else:
                try:
                    tavily_days = max(1, int(args.freshness.rstrip('h')) // 24)
                except (ValueError, AttributeError):
                    tavily_days = 2
            
            results = []
            for topic in topics:
                if not topic.get("search", {}).get("queries"):
                    logger.debug(f"Topic {topic['id']} has no search queries, skipping")
                    continue
                logger.debug(f"Searching topic: {topic['id']}")
                result = search_topic_tavily(topic, tavily_key, days=tavily_days)
                results.append(result)
            
            total_articles = sum(r.get("count", 0) for r in results)
            ok_topics = sum(1 for r in results if r["status"] == "ok")
            
            output = {
                "generated": datetime.now(timezone.utc).isoformat(),
                "source_type": "web",
                "defaults_dir": str(args.defaults),
                "config_dir": str(args.config) if args.config else None,
                "freshness": args.freshness,
                "api_used": "tavily",
                "topics_total": len(topics),
                "topics_ok": ok_topics,
                "total_articles": total_articles,
                "topics": results,
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            
            logger.info(f"\u2705 Done: {ok_topics}/{len(topics)} topics ok, {total_articles} articles → {args.output}")
            return 0
        
        elif use_brave:
            logger.info(f"Using Brave Search API for {len(topics)} topics ({len(brave_keys)} key(s) configured)")
            
            delay = 1.0 / max_qps if max_workers == 1 else 0
            
            # Convert freshness to Brave API format
            # Accept both Brave native (pd/pw/pm/py) and human-friendly (24h/48h/1w/1m)
            if args.freshness in ('pd', 'pw', 'pm', 'py'):
                brave_freshness = args.freshness
            else:
                freshness_map = {'1w': 168, '1m': 720, '1y': 8760}
                if args.freshness in freshness_map:
                    freshness_hours = freshness_map[args.freshness]
                else:
                    try:
                        freshness_hours = int(args.freshness.rstrip('h'))
                    except ValueError:
                        logger.warning(f"Unrecognized freshness format '{args.freshness}', defaulting to 48h")
                        freshness_hours = 48
                brave_freshness = convert_freshness(freshness_hours)
            
            results = []
            for topic in topics:
                if not topic.get("search", {}).get("queries"):
                    logger.debug(f"Topic {topic['id']} has no search queries, skipping")
                    continue
                    
                logger.debug(f"Searching topic: {topic['id']}")
                result = search_topic_brave(topic, api_key, brave_freshness,
                                           max_workers=max_workers, delay=delay)
                results.append(result)
            
            total_articles = sum(r.get("count", 0) for r in results)
            ok_topics = sum(1 for r in results if r["status"] == "ok")
            
            output = {
                "generated": datetime.now(timezone.utc).isoformat(),
                "source_type": "web",
                "defaults_dir": str(args.defaults),
                "config_dir": str(args.config) if args.config else None,
                "freshness": args.freshness,
                "api_used": "brave",
                "topics_total": len(results),
                "topics_ok": ok_topics,
                "total_articles": total_articles,
                "topics": results
            }
            
            logger.info(f"✅ Searched {ok_topics}/{len(results)} topics, "
                       f"{total_articles} articles found")
            
        else:
            logger.info("No BRAVE_API_KEY found, generating search interface for agents")
            
            results = []
            for topic in topics:
                if not topic.get("search", {}).get("queries"):
                    continue
                result = generate_search_interface(topic)
                results.append(result)
            
            output = {
                "generated": datetime.now(timezone.utc).isoformat(),
                "source_type": "web",
                "defaults_dir": str(args.defaults),
                "config_dir": str(args.config) if args.config else None,
                "freshness": args.freshness,
                "api_used": "interface",
                "topics_total": len(results),
                "topics_ok": 0,  # Requires manual execution
                "total_articles": 0,
                "topics": results,
                "agent_instructions": [
                    "This file contains search interface for web_search tool",
                    "For each topic, execute the queries using web_search",
                    "Apply the filters (must_include/exclude) to results",
                    "Tag matching articles with the topic_id",
                    "Update this file with results for merge-sources.py"
                ]
            }
            
            logger.info(f"✅ Generated search interface for {len(results)} topics")

        # Write output
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(json_str)

        logger.info(f"Output written to: {args.output}")
        return 0
        
    except Exception as e:
        logger.error(f"💥 Web search failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())