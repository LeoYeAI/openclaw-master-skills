# Competitive Analysis Patterns

Workflows for competitive intelligence and market analysis.

## Prerequisites

**Nimble API Key Required** - Get your key at https://www.nimbleway.com/

Set the `NIMBLE_API_KEY` environment variable using your platform's method:
- **Claude Code:** `~/.claude/settings.json` with `env` object
- **VS Code/GitHub Copilot:** GitHub Actions secrets
- **Shell:** `export NIMBLE_API_KEY="your-key"`

## Brand Monitoring

```python
def monitor_brand(brand_name, competitors=None):
    """Track brand mentions and competitive positioning"""

    # Brand news and updates
    brand_news = client.search(
        f"{brand_name} latest news announcements",
        focus="news",
        max_results=15,
        time_range="month",
        include_answer=True
    )

    # Social sentiment
    social_sentiment = client.search(
        f"{brand_name} customer opinions reviews",
        focus="social",
        max_results=12,
        include_domains=["twitter.com", "reddit.com"]
    )

    # Competitor comparison
    if competitors:
        competitor_query = f"{brand_name} vs {' vs '.join(competitors)}"
        comparison = client.search(
            competitor_query,
            focus="general",
            max_results=10,
            include_answer=True
        )
    else:
        comparison = None

    return {
        "recent_news": brand_news['answer'],
        "social_mentions": [r['title'] for r in social_sentiment['results']],
        "competitive_comparison": comparison['answer'] if comparison else None
    }
```

## Product Comparison

```python
def compare_products(product_a, product_b, category):
    """Detailed product comparison across multiple dimensions"""

    # Feature comparison
    features = client.search(
        f"{product_a} vs {product_b} features comparison {category}",
        focus="shopping",
        max_results=10,
        include_answer=True
    )

    # User reviews
    reviews_a = client.search(
        f"{product_a} user reviews {category}",
        focus="social",
        max_results=8,
        include_domains=["reddit.com", "amazon.com", "g2.com"]
    )

    reviews_b = client.search(
        f"{product_b} user reviews {category}",
        focus="social",
        max_results=8,
        include_domains=["reddit.com", "amazon.com", "g2.com"]
    )

    # Expert opinions
    expert = client.search(
        f"{product_a} {product_b} expert review {category}",
        focus="general",
        max_results=10,
        include_answer=True
    )

    return {
        "feature_comparison": features['answer'],
        "product_a_reviews": [r['title'] for r in reviews_a['results']],
        "product_b_reviews": [r['title'] for r in reviews_b['results']],
        "expert_analysis": expert['answer']
    }
```

## Market Share Analysis

```python
def analyze_market_share(industry, top_players):
    """Analyze market positioning and share"""

    # Industry overview
    overview = client.search(
        f"{industry} market overview leaders",
        focus="general",
        max_results=12,
        include_answer=True
    )

    # Recent market shifts
    trends = client.search(
        f"{industry} market trends changes 2026",
        focus="news",
        max_results=15,
        start_date="2025-10-01",
        include_answer=True
    )

    # Individual player analysis
    player_data = {}
    for player in top_players:
        data = client.search(
            f"{player} {industry} market position",
            focus="news",
            max_results=8,
            include_answer=True
        )
        player_data[player] = data['answer']

    return {
        "market_overview": overview['answer'],
        "recent_trends": trends['answer'],
        "players": player_data
    }
```

## Technical Stack Analysis

```python
def analyze_tech_stack(company_name):
    """Analyze company's technology choices"""

    # Technology stack
    stack = client.search(
        f"{company_name} technology stack architecture",
        focus="coding",
        max_results=10,
        include_domains=["stackshare.io", "github.com", "builtwith.com"]
    )

    # Developer practices
    practices = client.search(
        f"{company_name} engineering practices culture",
        focus="coding",
        max_results=10,
        include_answer=True
    )

    # Open source presence
    opensource = client.search(
        f"{company_name} open source projects contributions",
        focus="coding",
        max_results=12,
        include_domains=["github.com", "gitlab.com"]
    )

    return {
        "tech_stack": [r['url'] for r in stack['results']],
        "engineering_practices": practices['answer'],
        "opensource_presence": [r['title'] for r in opensource['results']]
    }
```
