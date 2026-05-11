"""
Content Claw - Autonomous Topic Discovery

Discovers trending topics relevant to a brand using Exa search.

Usage:
    uv run discover_topics.py <brand-dir>

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

    Returns a dict with key: exa_queries.
    Each is a list of query strings tailored to Exa search.
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

    if pain_points:
        exa_queries.append(f"{pain_points[0]} solutions {keyword_str}")

    return {
        "exa_queries": exa_queries,
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
        print(json.dumps({"error": "Usage: discover_topics.py <brand-dir>"}), file=sys.stderr)
        sys.exit(1)

    load_env()

    brand_dir = sys.argv[1]

    # Load brand graph
    brand_graph = load_brand_graph(brand_dir)
    if not brand_graph:
        print(json.dumps({"error": f"No brand graph found at {brand_dir}"}), file=sys.stderr)
        sys.exit(1)

    # Plan queries
    queries = plan_queries(brand_graph)

    # Execute Exa search
    all_topics = search_exa(queries["exa_queries"])

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
