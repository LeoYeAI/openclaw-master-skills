# Deep Research Workflow

Multi-step research patterns for comprehensive analysis.

## Prerequisites

**Nimble API Key Required** - Get your key at https://www.nimbleway.com/

Set the `NIMBLE_API_KEY` environment variable using your platform's method:
- **Claude Code:** `~/.claude/settings.json` with `env` object
- **VS Code/GitHub Copilot:** GitHub Actions secrets
- **Shell:** `export NIMBLE_API_KEY="your-key"`

The examples below assume `$NIMBLE_API_KEY` is set.

## Complete Research Workflow

### Scenario: Researching a New Technology

**Step 1: Overview (General Understanding)**

```python
# Get broad understanding of the topic
overview = client.search(
    "Svelte 5 web framework overview and features",
    focus="general",
    max_results=10,
    include_answer=True
)

print("Overview:", overview['answer'])
```

**Step 2: Technical Deep Dive**

```python
# Get technical details and code examples
technical = client.search(
    "Svelte 5 runes and reactivity system examples",
    focus="coding",
    max_results=15,
    include_answer=False,
    deep_search=True,
    include_domains=["svelte.dev", "github.com"]
)

# Analyze full content from official docs
for result in technical['results']:
    if result.get('content'):
        analyze_technical_content(result['content'])
```

**Step 3: Recent Developments**

```python
# Check latest news and updates
news = client.search(
    "Svelte 5 latest updates and releases 2026",
    focus="news",
    max_results=8,
    include_answer=True,
    time_range="month"
)

print("Recent developments:", news['answer'])
```

**Step 4: Community Sentiment**

```python
# Get developer opinions and experiences
community = client.search(
    "Svelte 5 developer experiences and opinions",
    focus="social",
    max_results=12,
    include_domains=["reddit.com", "news.ycombinator.com", "dev.to"]
)

# Analyze community feedback
for result in community['results']:
    print(f"Community: {result['title']} - {result['url']}")
```

**Step 5: Academic/Research Context**

```python
# Find research papers or in-depth analysis
research = client.search(
    "frontend framework performance comparisons",
    focus="academic",
    max_results=10,
    include_answer=True,
    include_domains=["arxiv.org", "scholar.google.com"]
)

print("Research findings:", research['answer'])
```

**Step 6: Synthesis**

```python
def synthesize_research(overview, technical, news, community, research):
    """Combine all findings into comprehensive report"""
    report = {
        "overview": overview['answer'],
        "technical_resources": [r['url'] for r in technical['results']],
        "recent_developments": news['answer'],
        "community_sentiment": [r['title'] for r in community['results']],
        "research_findings": research['answer']
    }
    return report

final_report = synthesize_research(overview, technical, news, community, research)
```

## Comparative Analysis Workflow

### Scenario: Comparing Two Technologies

```python
def compare_technologies(tech_a, tech_b):
    """Deep comparison of two technologies"""

    # Step 1: Individual overviews
    overview_a = client.search(
        f"{tech_a} features and capabilities",
        focus="coding",
        max_results=10,
        include_answer=True
    )

    overview_b = client.search(
        f"{tech_b} features and capabilities",
        focus="coding",
        max_results=10,
        include_answer=True
    )

    # Step 2: Direct comparison
    comparison = client.search(
        f"{tech_a} vs {tech_b} comparison",
        focus="coding",
        max_results=15,
        include_answer=True,
        deep_search=True
    )

    # Step 3: Performance benchmarks
    performance = client.search(
        f"{tech_a} {tech_b} performance benchmarks",
        focus="coding",
        max_results=10,
        include_domains=["github.com", "benchmarks.org"]
    )

    # Step 4: Community preferences
    community = client.search(
        f"{tech_a} vs {tech_b} developer opinions",
        focus="social",
        max_results=12,
        include_domains=["reddit.com", "news.ycombinator.com"]
    )

    # Step 5: Recent trends
    trends = client.search(
        f"{tech_a} {tech_b} adoption trends 2026",
        focus="news",
        max_results=8,
        time_range="month",
        include_answer=True
    )

    return {
        "tech_a_overview": overview_a['answer'],
        "tech_b_overview": overview_b['answer'],
        "comparison": comparison['answer'],
        "performance_links": [r['url'] for r in performance['results']],
        "community_opinions": [r['title'] for r in community['results']],
        "trends": trends['answer']
    }

# Usage
report = compare_technologies("React", "Vue.js")
```

## Market Research Workflow

### Scenario: Understanding a Market Space

```python
def market_research(topic, industry):
    """Comprehensive market research"""

    # Step 1: Market overview
    overview = client.search(
        f"{topic} market overview {industry}",
        focus="general",
        max_results=12,
        include_answer=True
    )

    # Step 2: Recent news and trends
    trends = client.search(
        f"{topic} {industry} trends 2026",
        focus="news",
        max_results=15,
        include_answer=True,
        start_date="2025-10-01"
    )

    # Step 3: Academic research
    research = client.search(
        f"{topic} {industry} research analysis",
        focus="academic",
        max_results=10,
        include_answer=True
    )

    # Step 4: Product landscape
    products = client.search(
        f"{topic} {industry} products and solutions",
        focus="shopping",
        max_results=12,
        include_answer=True
    )

    # Step 5: Social sentiment
    sentiment = client.search(
        f"{topic} {industry} discussions",
        focus="social",
        max_results=10,
        include_domains=["linkedin.com", "twitter.com"]
    )

    return {
        "market_overview": overview['answer'],
        "trends": trends['answer'],
        "research_insights": research['answer'],
        "product_landscape": products['answer'],
        "social_sentiment": [r['title'] for r in sentiment['results']]
    }

# Usage
report = market_research("AI agents", "software development")
```

## Problem-Solving Workflow

### Scenario: Debugging Complex Issue

```python
def debug_issue(error_message, context):
    """Multi-angle approach to solving technical problems"""

    # Step 1: Direct error search
    exact_match = client.search(
        f'"{error_message}" {context}',
        focus="coding",
        max_results=8,
        include_domains=["stackoverflow.com", "github.com"]
    )

    # Step 2: Broader search if no exact matches
    if exact_match['total_results'] < 3:
        broader = client.search(
            f"{context} common errors and solutions",
            focus="coding",
            max_results=12,
            include_answer=True
        )
    else:
        broader = None

    # Step 3: Official documentation
    docs = client.search(
        f"{context} documentation error handling",
        focus="coding",
        max_results=5,
        include_domains=["official-docs.com"]  # Replace with actual domain
    )

    # Step 4: Community discussions
    community = client.search(
        f"{error_message} {context}",
        focus="social",
        max_results=8,
        include_domains=["reddit.com", "dev.to"]
    )

    # Step 5: Recent solutions
    recent = client.search(
        f"{error_message} {context} fix",
        focus="coding",
        max_results=8,
        time_range="month",  # Recent solutions
        include_answer=True
    )

    return {
        "exact_matches": [r['url'] for r in exact_match['results']],
        "broader_context": broader['answer'] if broader else None,
        "official_docs": [r['url'] for r in docs['results']],
        "community_discussions": [r['url'] for r in community['results']],
        "recent_solutions": recent['answer']
    }

# Usage
solutions = debug_issue(
    "TypeError: Cannot read property 'map' of undefined",
    "React components"
)
```

## Learning Path Workflow

### Scenario: Creating a Learning Plan

```python
def create_learning_path(topic, skill_level="beginner"):
    """Build comprehensive learning resources"""

    # Step 1: Beginner resources
    if skill_level == "beginner":
        beginner = client.search(
            f"{topic} tutorial for beginners",
            focus="coding",
            max_results=12,
            include_answer=False,
            deep_search=True
        )
    else:
        beginner = None

    # Step 2: Core concepts
    concepts = client.search(
        f"{topic} core concepts and fundamentals",
        focus="coding",
        max_results=15,
        include_answer=True,
        deep_search=True
    )

    # Step 3: Practical examples
    examples = client.search(
        f"{topic} practical examples and projects",
        focus="coding",
        max_results=15,
        include_domains=["github.com", "codepen.io"]
    )

    # Step 4: Best practices
    best_practices = client.search(
        f"{topic} best practices and patterns",
        focus="coding",
        max_results=10,
        include_answer=True
    )

    # Step 5: Advanced topics
    advanced = client.search(
        f"{topic} advanced techniques",
        focus="coding",
        max_results=10,
        include_answer=True
    )

    # Step 6: Recent developments
    latest = client.search(
        f"{topic} latest features 2026",
        focus="news",
        max_results=8,
        time_range="month"
    )

    return {
        "beginner_resources": [r['url'] for r in beginner['results']] if beginner else [],
        "core_concepts": concepts['answer'],
        "practical_examples": [r['url'] for r in examples['results']],
        "best_practices": best_practices['answer'],
        "advanced_topics": advanced['answer'],
        "latest_updates": [r['title'] for r in latest['results']]
    }

# Usage
learning_plan = create_learning_path("GraphQL", skill_level="intermediate")
```

## Competitive Analysis Workflow

### Scenario: Analyzing Competitors

```python
def competitive_analysis(company_name, industry):
    """Analyze company and competitive landscape"""

    # Step 1: Company overview
    company = client.search(
        f"{company_name} company overview products",
        focus="general",
        max_results=10,
        include_answer=True,
        include_domains=[f"{company_name.lower()}.com"]
    )

    # Step 2: News and updates
    news = client.search(
        f"{company_name} news updates",
        focus="news",
        max_results=15,
        start_date="2025-10-01",
        include_answer=True
    )

    # Step 3: Competitive landscape
    competitors = client.search(
        f"{company_name} competitors {industry}",
        focus="general",
        max_results=12,
        include_answer=True
    )

    # Step 4: Customer sentiment
    sentiment = client.search(
        f"{company_name} reviews customer feedback",
        focus="social",
        max_results=15,
        include_domains=["reddit.com", "trustpilot.com", "g2.com"]
    )

    # Step 5: Technical analysis (if tech company)
    if industry in ["software", "tech", "saas"]:
        technical = client.search(
            f"{company_name} technical architecture stack",
            focus="coding",
            max_results=8,
            include_domains=["stackshare.io", "github.com"]
        )
    else:
        technical = None

    # Step 6: Market position
    market = client.search(
        f"{company_name} market share {industry}",
        focus="news",
        max_results=10,
        include_answer=True
    )

    return {
        "company_overview": company['answer'],
        "recent_news": news['answer'],
        "competitive_landscape": competitors['answer'],
        "customer_sentiment": [r['title'] for r in sentiment['results']],
        "technical_stack": [r['url'] for r in technical['results']] if technical else [],
        "market_position": market['answer']
    }

# Usage
analysis = competitive_analysis("Anthropic", "AI")
```

## Tips for Deep Research

1. **Start Broad, Then Narrow**: Begin with general searches, progressively focus
2. **Mix Focus Modes**: Combine different perspectives (coding, news, social, academic)
3. **Enable Content Extraction**: For key resources you'll analyze deeply
4. **Use Domain Filters**: Target authoritative sources for quality
5. **Check Multiple Timeframes**: Recent + historical for complete picture
6. **Generate Answers Strategically**: For synthesis steps, not collection steps
7. **Cache Intermediate Results**: Save API calls and enable re-analysis
8. **Document Findings**: Build structured reports from multiple searches
9. **Iterate Based on Results**: Let findings guide next search steps
10. **Synthesize at End**: Combine all perspectives for final analysis

## Performance Considerations

- **Parallel Searches**: Run independent searches concurrently
- **Progressive Loading**: Start with summaries, drill down as needed
- **Result Caching**: Store and reuse results across sessions
- **Smart Extraction**: Only extract content when you'll analyze it
- **Batch Similar Queries**: Group related searches together
- **Monitor API Usage**: Track costs for multi-step workflows
