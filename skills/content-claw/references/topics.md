# Topic Discovery

## Discover topics

Run: `cd BASE_DIR && uv run scripts/discover_topics.py BASE_DIR/brand-graphs/<brand>/`

Searches Exa for trending news, launches, and insights matching the brand's niche keywords. Requires EXA_API_KEY in .env.

Output JSON has: topic_count, topics (each with title, url, source, summary, relevance_score 0-100).

Present as a table: title, source, score, URL.

Ask: "Want me to run a recipe on any? Pick a number or 'all' for top 5."

Suggest recipes by source:
- News articles: paper-breakdown-insight, what-you-might-have-missed
- GitHub repos: demo-diagram-breakdown
- General: paper-breakdown-insight

Save results to `BASE_DIR/topics/<date>_<brand>.json`.
