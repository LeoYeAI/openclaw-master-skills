"""
Content Claw - Autonomous Topic Discovery

Discovers trending topics relevant to a brand using Exa search and
Playwright-based scraping of Reddit and X/Twitter.

Usage:
    uv run discover_topics.py <brand-dir> [--reddit-cookie <path>] [--x-cookie <path>]

Outputs JSON array of discovered topics to stdout.

Environment:
    EXA_API_KEY - Required. Set in .env file.
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta


def load_env():
    """Load only declared keys from .env (scoped to FAL_KEY, EXA_API_KEY)."""
    allowed = {"FAL_KEY", "EXA_API_KEY"}
    env_path = Path(__file__).parent.parent / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key in allowed:
            os.environ.setdefault(key, value.strip())


def load_brand_graph(brand_dir: str) -> dict:
    """Load all YAML files from a brand graph directory."""
    import yaml

    brand_path = Path(brand_dir)
    graph = {}
    for f in brand_path.glob("*.yaml"):
        with open(f) as fh:
            data = yaml.safe_load(fh)
            if data:
                graph[f.stem] = data
    return graph


def plan_queries(brand_graph: dict) -> dict:
    """Generate search queries from brand graph context.

    Returns a dict with keys: exa_queries, reddit_queries, x_queries.
    Each is a list of query strings tailored to the platform.
    """
    identity = brand_graph.get("identity", {})
    audience = brand_graph.get("audience", {})
    strategy = brand_graph.get("strategy", {})

    name = identity.get("name", "")
    positioning = identity.get("positioning", "")
    description = identity.get("description", "")
    keywords = strategy.get("niche_keywords", [])
    goals = strategy.get("goals", [])
    pain_points = audience.get("pain_points", [])
    interests = audience.get("interests", [])

    keyword_str = " ".join(keywords[:5]) if keywords else positioning
    audience_str = " ".join(interests[:3]) if interests else ""

    exa_queries = [
        f"trending {keyword_str} news",
        f"{keyword_str} new tools launches announcements",
        f"{keyword_str} {audience_str} insights analysis",
    ]

    reddit_queries = [
        f"{keyword_str} site:reddit.com",
    ]

    x_queries = [
        keyword_str,
    ]

    if pain_points:
        exa_queries.append(f"{pain_points[0]} solutions {keyword_str}")

    return {
        "exa_queries": exa_queries,
        "reddit_queries": reddit_queries,
        "x_queries": x_queries,
    }


def search_exa(queries: list[str], num_results: int = 10) -> list[dict]:
    """Search Exa for trending content."""
    from exa_py import Exa

    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        return [{"error": "EXA_API_KEY not set"}]

    exa = Exa(api_key=api_key)
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00.000Z")

    results = []
    for query in queries:
        try:
            response = exa.search(
                query,
                type="auto",
                num_results=num_results,
                start_published_date=week_ago,
                contents={
                    "text": {"maxCharacters": 1500},
                    "highlights": {"maxCharacters": 300},
                    "summary": {"query": "what is the main topic and why does it matter"},
                },
            )
            for r in response.results:
                results.append({
                    "title": r.title,
                    "url": r.url,
                    "published_date": r.published_date,
                    "summary": getattr(r, "summary", ""),
                    "highlights": getattr(r, "highlights", []),
                    "text_preview": (r.text or "")[:500],
                    "score": r.score,
                    "source": "exa",
                    "query": query,
                })
        except Exception as e:
            results.append({"error": str(e), "query": query, "source": "exa"})

    return results


def scrape_reddit(queries: list[str], cookie_path: str | None = None) -> list[dict]:
    """Scrape Reddit for trending discussions using Playwright."""
    from playwright.sync_api import sync_playwright
    from readabilipy import simple_json_from_html_string

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        # Load cookies if provided
        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for query in queries:
            try:
                search_url = f"https://www.reddit.com/search/?q={query}&sort=hot&t=week"
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)

                # Extract post links
                links = page.eval_on_selector_all(
                    'a[href*="/comments/"]',
                    "els => els.map(el => ({href: el.href, text: el.textContent})).slice(0, 10)"
                )

                seen_urls = set()
                for link in links:
                    url = link.get("href", "")
                    title = link.get("text", "").strip()
                    if not url or not title or len(title) < 10 or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    results.append({
                        "title": title,
                        "url": url,
                        "source": "reddit",
                        "query": query,
                        "text_preview": "",
                        "summary": "",
                    })

            except Exception as e:
                results.append({"error": str(e), "query": query, "source": "reddit"})

        context.close()
        browser.close()

    return results


def scrape_x(queries: list[str], cookie_path: str | None = None) -> list[dict]:
    """Scrape X/Twitter for trending discussions using Playwright."""
    from playwright.sync_api import sync_playwright

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            locale="en-US",
        )

        # Load cookies if provided (required for X search)
        if cookie_path and Path(cookie_path).exists():
            cookies = json.loads(Path(cookie_path).read_text())
            context.add_cookies(cookies)

        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        for query in queries:
            try:
                search_url = f"https://x.com/search?q={query}&src=typed_query&f=top"
                page.goto(search_url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(5000)

                # Extract tweets
                tweets = page.eval_on_selector_all(
                    'article[data-testid="tweet"]',
                    """els => els.slice(0, 10).map(el => {
                        const textEl = el.querySelector('div[data-testid="tweetText"]');
                        const linkEl = el.querySelector('a[href*="/status/"]');
                        const authorEl = el.querySelector('div[dir="ltr"] > span');
                        return {
                            text: textEl ? textEl.innerText : '',
                            url: linkEl ? linkEl.href : '',
                            author: authorEl ? authorEl.innerText : ''
                        };
                    })"""
                )

                for tweet in tweets:
                    text = tweet.get("text", "").strip()
                    url = tweet.get("url", "")
                    if not text or not url:
                        continue

                    results.append({
                        "title": f"@{tweet.get('author', 'unknown')}: {text[:80]}",
                        "url": url,
                        "text_preview": text[:500],
                        "source": "x",
                        "query": query,
                        "summary": "",
                    })

            except Exception as e:
                results.append({"error": str(e), "query": query, "source": "x"})

        context.close()
        browser.close()

    return results


def deduplicate(topics: list[dict]) -> list[dict]:
    """Simple deduplication by URL and title similarity."""
    seen_urls = set()
    seen_titles = set()
    deduped = []

    for topic in topics:
        if "error" in topic:
            continue

        url = topic.get("url", "")
        title = topic.get("title", "").lower().strip()

        if url in seen_urls:
            continue

        # Simple title similarity: skip if first 40 chars match (ignore empty titles)
        title_key = title[:40]
        if title_key and title_key in seen_titles:
            continue

        if url:
            seen_urls.add(url)
        if title_key:
            seen_titles.add(title_key)
        deduped.append(topic)

    return deduped


def score_topics(topics: list[dict], brand_graph: dict) -> list[dict]:
    """Score topics by relevance to brand graph. Simple keyword matching."""
    strategy = brand_graph.get("strategy", {})
    audience = brand_graph.get("audience", {})
    identity = brand_graph.get("identity", {})

    keywords = set()
    for k in strategy.get("niche_keywords", []):
        keywords.update(k.lower().split())
    for k in audience.get("interests", []):
        keywords.update(k.lower().split())
    keywords.update(identity.get("positioning", "").lower().split())

    # Remove common words
    keywords -= {"the", "a", "an", "and", "or", "for", "to", "in", "of", "is", "with"}

    for topic in topics:
        text = f"{topic.get('title', '')} {topic.get('summary', '')} {topic.get('text_preview', '')}".lower()
        matches = sum(1 for k in keywords if k in text)
        topic["relevance_score"] = min(100, int((matches / max(len(keywords), 1)) * 100))

    topics.sort(key=lambda t: t.get("relevance_score", 0), reverse=True)
    return topics


def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "Usage: discover_topics.py <brand-dir> [--reddit-cookie <path>] [--x-cookie <path>]"}), file=sys.stderr)
        sys.exit(1)

    load_env()

    brand_dir = sys.argv[1]
    reddit_cookie = None
    x_cookie = None

    # Parse optional args
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--reddit-cookie" and i + 1 < len(args):
            reddit_cookie = args[i + 1]
            i += 2
        elif args[i] == "--x-cookie" and i + 1 < len(args):
            x_cookie = args[i + 1]
            i += 2
        else:
            i += 1

    # Load brand graph
    brand_graph = load_brand_graph(brand_dir)
    if not brand_graph:
        print(json.dumps({"error": f"No brand graph found at {brand_dir}"}), file=sys.stderr)
        sys.exit(1)

    # Plan queries
    queries = plan_queries(brand_graph)

    # Execute searches in parallel-ish (sequential for now, each is fast)
    all_topics = []

    # Exa search (always runs)
    exa_results = search_exa(queries["exa_queries"])
    all_topics.extend(exa_results)

    # Reddit scraping (runs if cookies provided or without auth)
    reddit_results = scrape_reddit(queries["reddit_queries"], reddit_cookie)
    all_topics.extend(reddit_results)

    # X scraping (only runs if cookies provided, X requires auth for search)
    if x_cookie:
        x_results = scrape_x(queries["x_queries"], x_cookie)
        all_topics.extend(x_results)

    # Deduplicate and score
    topics = deduplicate(all_topics)
    topics = score_topics(topics, brand_graph)

    # Output
    output = {
        "brand": brand_graph.get("identity", {}).get("name", "unknown"),
        "discovered_at": datetime.now().isoformat(),
        "query_plan": queries,
        "topic_count": len(topics),
        "topics": topics,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
