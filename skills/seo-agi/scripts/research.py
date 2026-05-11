#!/usr/bin/env python3
"""
seo-agi research orchestrator.
Pulls SERP data, keyword data, PAA questions, and competitor content analysis
into a single research.json file that feeds content generation.

Usage:
    python3 research.py "<keyword>" [options]

Options:
    --serp-depth=N       Number of SERP results to analyze (default: 10)
    --include-paa        Include People Also Ask extraction (default: true)
    --location=CODE      DataForSEO location code (default: 2840 = US)
    --language=CODE      Language code (default: en)
    --output=FORMAT      Output: json|compact|brief (default: compact)
    --save-dir=PATH      Save raw data (default: ~/.local/share/seo-agi/research/)
    --content-depth=N    Number of top results to parse for content (default: 5)
    --mock               Use fixture data instead of live API calls
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

# Add parent dir to path for lib imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.env import load_env, load_config, get_credentials, ensure_dirs
from lib.dataforseo import DataForSEOClient
from lib.serp_analyze import analyze_serp


def parse_args():
    parser = argparse.ArgumentParser(description="SEO-AGI Research")
    parser.add_argument("keyword", help="Target keyword or topic")
    parser.add_argument(
        "--serp-depth", type=int, default=10, help="SERP depth"
    )
    parser.add_argument(
        "--content-depth",
        type=int,
        default=5,
        help="Number of competitors to parse content from",
    )
    parser.add_argument(
        "--location", type=int, default=None, help="Location code"
    )
    parser.add_argument(
        "--language", default=None, help="Language code"
    )
    parser.add_argument(
        "--output",
        choices=["json", "compact", "brief"],
        default="compact",
        help="Output format",
    )
    parser.add_argument(
        "--save-dir", default=None, help="Directory to save research data"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use fixture data (no API calls)",
    )
    return parser.parse_args()


def load_mock_data(keyword: str) -> dict:
    """Load fixture data for testing without API calls."""
    fixtures_dir = (
        Path(__file__).parent.parent / "fixtures"
    )

    serp_fixture = fixtures_dir / "serp_sample.json"
    keywords_fixture = fixtures_dir / "keywords_sample.json"

    serp_data = {"organic": [], "paa": [], "featured_snippet": None}
    related_kw = []

    if serp_fixture.exists():
        with open(serp_fixture) as f:
            serp_data = json.load(f)

    if keywords_fixture.exists():
        with open(keywords_fixture) as f:
            related_kw = json.load(f)

    return {
        "keyword": keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock",
        "serp": serp_data,
        "related_keywords": related_kw,
        "analysis": {
            "intent": "commercial",
            "word_count_stats": {
                "min": 800,
                "max": 3200,
                "median": 1800,
                "recommended_min": 1440,
                "recommended_max": 2340,
            },
            "paa_questions": serp_data.get("paa", []),
            "topic_frequency": [],
            "heading_patterns": {
                "avg_h2_count": 6,
                "avg_h3_count": 8,
                "median_h2_count": 5,
                "median_h3_count": 7,
            },
        },
    }


def run_research(args) -> dict:
    """Execute the full research pipeline."""
    creds = get_credentials()
    config = load_config()

    location = args.location or config["default_location"]
    language = args.language or config["default_language"]

    if args.mock:
        return load_mock_data(args.keyword)

    if not creds["has_dataforseo"]:
        print(
            "NO_DATAFORSEO_CREDS: DataForSEO credentials not found.",
            file=sys.stderr,
        )
        print(
            "Falling back to mock data. For live research, add credentials to "
            "~/.config/seo-agi/.env",
            file=sys.stderr,
        )
        print(
            "Or use Ahrefs/SEMRush MCP tools in Claude Code as alternative data sources.",
            file=sys.stderr,
        )
        # Return a skeleton that the agent can fill in via MCP tools or WebSearch
        return {
            "keyword": args.keyword,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "no-creds-fallback",
            "location": location,
            "language": language,
            "serp": {"organic": [], "paa": [], "featured_snippet": None},
            "related_keywords": [],
            "analysis": {
                "keyword": args.keyword,
                "intent": "unknown",
                "word_count_stats": {},
                "paa_questions": [],
                "topic_frequency": [],
                "heading_patterns": {},
                "competitors_analyzed": 0,
                "total_organic_results": 0,
                "featured_snippet": None,
            },
            "_fallback_note": (
                "No DataForSEO credentials. Use Ahrefs MCP, SEMRush MCP, "
                "or WebSearch to gather competitive data manually."
            ),
        }

    client = DataForSEOClient(
        creds["dataforseo_login"], creds["dataforseo_password"]
    )

    # Step 1: SERP results
    print(f"Fetching SERP for: {args.keyword}", file=sys.stderr)
    serp_data = client.serp_live(
        args.keyword, location, language, args.serp_depth
    )

    # Step 2: Related keywords
    print("Fetching related keywords...", file=sys.stderr)
    related_kw = client.related_keywords(args.keyword, location, language)

    # Step 3: Parse competitor content (top N)
    content_data = []
    organic = serp_data.get("organic", [])
    parse_count = min(args.content_depth, len(organic))

    for i in range(parse_count):
        url = organic[i].get("url", "")
        if url:
            print(
                f"Parsing content ({i+1}/{parse_count}): {url[:80]}...",
                file=sys.stderr,
            )
            content = client.content_parse(url)
            content_data.append(content)

            # Merge content data back into organic result
            if content:
                organic[i]["word_count"] = content.get("word_count", 0)
                organic[i]["headings"] = content.get("headings", [])
        else:
            content_data.append(None)

    # Step 4: Analyze
    print("Analyzing competitive landscape...", file=sys.stderr)
    analysis = analyze_serp(serp_data, content_data, args.keyword)

    # Assemble research output
    research = {
        "keyword": args.keyword,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": location,
        "language": language,
        "source": "dataforseo",
        "serp": serp_data,
        "related_keywords": related_kw[:20],
        "analysis": analysis,
    }

    return research


def save_research(research: dict, save_dir: str = None):
    """Save research data to disk."""
    ensure_dirs()
    config = load_config()

    if save_dir:
        out_dir = Path(save_dir).expanduser()
    else:
        out_dir = Path.home() / ".local" / "share" / "seo-agi" / "research"

    out_dir.mkdir(parents=True, exist_ok=True)

    # Filename from keyword + date
    slug = (
        research["keyword"]
        .lower()
        .replace(" ", "-")
        .replace("/", "-")[:50]
    )
    date_str = datetime.now().strftime("%Y%m%d")
    filename = f"{slug}-{date_str}.json"

    filepath = out_dir / filename
    with open(filepath, "w") as f:
        json.dump(research, f, indent=2)

    print(f"Research saved: {filepath}", file=sys.stderr)
    return str(filepath)


def format_compact(research: dict) -> str:
    """Format research as compact human-readable output."""
    lines = []
    kw = research["keyword"]
    analysis = research.get("analysis", {})
    serp = research.get("serp", {})
    organic = serp.get("organic", [])

    lines.append(f"# Research: {kw}")
    lines.append(f"Intent: {analysis.get('intent', 'unknown')}")

    # Word count
    wc = analysis.get("word_count_stats", {})
    if wc:
        lines.append(
            f"Competitor word count: {wc.get('min', '?')}-{wc.get('max', '?')} "
            f"(median: {wc.get('median', '?')})"
        )
        lines.append(
            f"Recommended range: {wc.get('recommended_min', '?')}-"
            f"{wc.get('recommended_max', '?')} words"
        )

    # Top results
    lines.append(f"\n## Top {len(organic)} Results")
    for r in organic[:10]:
        wc_str = (
            f" ({r.get('word_count', '?')} words)"
            if r.get("word_count")
            else ""
        )
        lines.append(f"  {r['position']}. {r['title']}{wc_str}")
        lines.append(f"     {r['url']}")

    # PAA
    paa = analysis.get("paa_questions", serp.get("paa", []))
    if paa:
        lines.append(f"\n## People Also Ask ({len(paa)})")
        for q in paa:
            lines.append(f"  - {q}")

    # Related keywords
    related = research.get("related_keywords", [])
    if related:
        lines.append(f"\n## Related Keywords (top 10)")
        for kw_data in related[:10]:
            lines.append(
                f"  - {kw_data['keyword']} "
                f"(vol: {kw_data['volume']}, "
                f"diff: {kw_data.get('difficulty', '?')})"
            )

    # Topics
    topics = analysis.get("topic_frequency", [])
    if topics:
        lines.append(f"\n## Common Topics Across Competitors")
        for t in topics[:15]:
            lines.append(
                f"  - {t['topic']} (in {t['competitor_count']} pages)"
            )

    # Heading patterns
    hp = analysis.get("heading_patterns", {})
    if hp:
        lines.append(f"\n## Heading Structure")
        lines.append(
            f"  Avg H2s: {hp.get('avg_h2_count', '?')}, "
            f"Avg H3s: {hp.get('avg_h3_count', '?')}"
        )

    return "\n".join(lines)


def main():
    args = parse_args()
    research = run_research(args)

    # Save
    filepath = save_research(research, args.save_dir)

    # Output
    if args.output == "json":
        print(json.dumps(research, indent=2))
    elif args.output == "brief":
        # Minimal output for piping into content generation
        analysis = research.get("analysis", {})
        brief_data = {
            "keyword": research["keyword"],
            "intent": analysis.get("intent"),
            "word_count_stats": analysis.get("word_count_stats"),
            "paa_questions": analysis.get(
                "paa_questions",
                research.get("serp", {}).get("paa", []),
            ),
            "topic_frequency": analysis.get("topic_frequency", [])[:10],
            "heading_patterns": analysis.get("heading_patterns"),
            "research_file": filepath,
        }
        print(json.dumps(brief_data, indent=2))
    else:
        print(format_compact(research))


if __name__ == "__main__":
    main()
