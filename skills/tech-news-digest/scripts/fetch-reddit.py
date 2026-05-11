#!/usr/bin/env python3
"""
Fetch Reddit posts from unified sources configuration.

Reads sources.json, filters Reddit sources, fetches posts via Reddit JSON API,
and outputs structured JSON with posts tagged by topics.

Usage:
    python3 fetch-reddit.py [--defaults DEFAULTS_DIR] [--config CONFIG_DIR] [--hours 48] [--output FILE] [--verbose] [--force] [--no-cache]

Environment:
    No API key required. Uses Reddit's public JSON API.
"""

import json
import sys
import os
import argparse
import logging
import ssl
import time
import tempfile
from datetime import datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Any, Optional
from urllib.request import Request, urlopen

_SSL_CTX = ssl.create_default_context()
from urllib.error import HTTPError, URLError

# Constants
MAX_WORKERS = 4
TIMEOUT = 30
RETRY_COUNT = 2
RETRY_DELAY = 3
USER_AGENT = "TechDigest/2.8 (bot; +https://github.com/draco-agent/tech-news-digest)"
RESUME_MAX_AGE_SECONDS = 3600  # 1 hour


def setup_logging(verbose: bool = False) -> logging.Logger:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    return logging.getLogger(__name__)


def load_reddit_sources(defaults_dir: Optional[Path], config_dir: Optional[Path]) -> List[Dict[str, Any]]:
    """Load Reddit sources from config, with user overrides."""
    sys.path.insert(0, str(Path(__file__).parent))
    from config_loader import load_merged_sources as load_sources
    
    all_sources = load_sources(defaults_dir, config_dir)
    reddit_sources = []
    for s in all_sources:
        if s.get('type') != 'reddit':
            continue
        if not s.get('enabled', True):
            continue
        if not s.get('subreddit'):
            logging.warning(f"Reddit source {s.get('id')} missing subreddit, skipping")
            continue
        reddit_sources.append(s)
    
    return reddit_sources


def fetch_subreddit(source: Dict[str, Any], cutoff: datetime) -> Dict[str, Any]:
    """Fetch posts from a subreddit using Reddit's JSON API."""
    source_id = source['id']
    subreddit = source['subreddit']
    sort = source.get('sort', 'hot')
    limit = source.get('limit', 25)
    min_score = source.get('min_score', 0)
    priority = source.get('priority', False)
    topics = source.get('topics', [])
    name = source.get('name', f'r/{subreddit}')
    
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json?limit={limit}&raw_json=1"
    
    for attempt in range(RETRY_COUNT + 1):
        try:
            req = Request(url, headers={
                'User-Agent': USER_AGENT,
                'Accept': 'text/html,application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            })
            
            with urlopen(req, timeout=TIMEOUT, context=_SSL_CTX) as resp:
                data = json.loads(resp.read().decode('utf-8'))
            
            articles = []
            children = data.get('data', {}).get('children', [])
            
            for child in children:
                post = child.get('data', {})
                if not post:
                    continue
                
                # Parse timestamp
                created_utc = post.get('created_utc', 0)
                post_time = datetime.fromtimestamp(created_utc, tz=timezone.utc)
                
                # Filter by time
                if post_time < cutoff:
                    continue
                
                # Filter by score
                score = post.get('score', 0)
                if score < min_score:
                    continue
                
                # Skip stickied/pinned posts
                if post.get('stickied', False):
                    continue
                
                # Get the external URL (if it's a link post) vs self post
                permalink = f"https://www.reddit.com{post.get('permalink', '')}"
                external_url = post.get('url', '')
                is_self = post.get('is_self', True)
                
                # If it's a self post or URL points to reddit, use permalink
                if is_self or 'reddit.com' in external_url or 'redd.it' in external_url:
                    link = permalink
                    external_url = None
                else:
                    link = external_url
                
                title = post.get('title', '').strip()
                if not title:
                    continue
                
                flair = post.get('link_flair_text', '')
                num_comments = post.get('num_comments', 0)
                upvote_ratio = post.get('upvote_ratio', 0)
                
                articles.append({
                    "title": title,
                    "link": link,
                    "reddit_url": permalink,
                    "external_url": external_url,
                    "date": post_time.isoformat(),
                    "score": score,
                    "num_comments": num_comments,
                    "flair": flair,
                    "is_self": is_self,
                    "topics": topics[:],
                    "metrics": {
                        "score": score,
                        "num_comments": num_comments,
                        "upvote_ratio": upvote_ratio
                    }
                })
            
            return {
                "source_id": source_id,
                "source_type": "reddit",
                "name": name,
                "subreddit": subreddit,
                "sort": sort,
                "priority": priority,
                "topics": topics,
                "status": "ok",
                "attempts": attempt + 1,
                "count": len(articles),
                "articles": articles,
            }
        
        except HTTPError as e:
            if e.code == 429:
                logging.warning(f"Rate limit for r/{subreddit}, attempt {attempt + 1}")
                if attempt < RETRY_COUNT:
                    time.sleep(10)
                    continue
            elif e.code == 403:
                logging.warning(f"r/{subreddit} is private or quarantined")
                return {
                    "source_id": source_id,
                    "source_type": "reddit",
                    "name": name,
                    "subreddit": subreddit,
                    "status": "error",
                    "error": f"HTTP {e.code}: Forbidden",
                    "count": 0,
                    "articles": [],
                }
            error_msg = f"HTTP {e.code}"
            logging.warning(f"Error fetching r/{subreddit}: {error_msg}")
        except (URLError, OSError) as e:
            error_msg = str(e)
            logging.warning(f"Network error for r/{subreddit}: {error_msg}")
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Unexpected error for r/{subreddit}: {error_msg}")
        
        if attempt < RETRY_COUNT:
            time.sleep(RETRY_DELAY)
    
    return {
        "source_id": source_id,
        "source_type": "reddit",
        "name": name,
        "subreddit": subreddit,
        "status": "error",
        "error": error_msg,
        "count": 0,
        "articles": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch Reddit posts from configured subreddits.\n"
                    "Uses Reddit's public JSON API (no authentication required).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
    python3 fetch-reddit.py --defaults config/defaults --output /tmp/td-reddit.json --verbose
    python3 fetch-reddit.py --defaults config/defaults --config ~/workspace/config --hours 48
    """
    )
    parser.add_argument('--defaults', type=Path, default=Path('config/defaults'),
                       help='Default config directory')
    parser.add_argument('--config', type=Path, default=None,
                       help='User config directory (overrides defaults)')
    parser.add_argument('--hours', type=int, default=48,
                       help='How many hours back to fetch (default: 48)')
    parser.add_argument('--output', type=Path, default=None,
                       help='Output JSON file path')
    parser.add_argument('--verbose', action='store_true',
                       help='Enable debug logging')
    parser.add_argument('--force', action='store_true',
                       help='Force fetch even if cached output exists')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable all caching')
    
    args = parser.parse_args()
    logger = setup_logging(args.verbose)
    
    # Auto-generate output path if not specified
    if not args.output:
        fd, temp_path = tempfile.mkstemp(prefix="tech-news-digest-reddit-", suffix=".json")
        os.close(fd)
        args.output = Path(temp_path)
    
    # Resume support
    if not args.force and args.output.exists():
        try:
            age = time.time() - args.output.stat().st_mtime
            if age < RESUME_MAX_AGE_SECONDS:
                with open(args.output) as f:
                    existing = json.load(f)
                if existing.get('subreddits'):
                    logger.info(f"⏭️  Skipping fetch: {args.output} is {age:.0f}s old (< {RESUME_MAX_AGE_SECONDS}s). Use --force to override.")
                    print(f"Output (cached): {args.output}")
                    return 0
        except (json.JSONDecodeError, KeyError):
            pass
    
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=args.hours)
        
        # Load sources
        if args.config and args.defaults == Path("config/defaults") and not args.defaults.exists():
            sources = load_reddit_sources(args.config, None)
        else:
            sources = load_reddit_sources(args.defaults, args.config)
        
        if not sources:
            logger.warning("No Reddit sources found or all disabled")
            output = {
                "source": "reddit",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "subreddits": [],
                "skipped_reason": "No Reddit sources configured"
            }
            with open(args.output, "w") as f:
                json.dump(output, f, indent=2)
            print(f"Output (empty): {args.output}")
            return 0
        
        logger.info(f"📡 Fetching {len(sources)} subreddits (cutoff: {cutoff.strftime('%Y-%m-%d %H:%M')} UTC)")
        
        results = []
        total_posts = 0
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            futures = {pool.submit(fetch_subreddit, source, cutoff): source for source in sources}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                total_posts += result.get('count', 0)
        
        ok_count = sum(1 for r in results if r['status'] == 'ok')
        
        output = {
            "source": "reddit",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
            "defaults_dir": str(args.defaults),
            "config_dir": str(args.config) if args.config else None,
            "hours": args.hours,
            "cutoff": cutoff.isoformat(),
            "subreddits_total": len(results),
            "subreddits_ok": ok_count,
            "total_posts": total_posts,
            "subreddits": results
        }
        
        json_str = json.dumps(output, ensure_ascii=False, indent=2)
        with open(args.output, "w", encoding='utf-8') as f:
            f.write(json_str)
        
        logger.info(f"✅ Fetched {ok_count}/{len(results)} subreddits, {total_posts} posts")
        print(f"Output: {args.output}")
        return 0
    
    except Exception as e:
        logger.error(f"💥 Reddit fetch failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
