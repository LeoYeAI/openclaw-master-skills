# Basic Search Examples

Simple search patterns for common use cases.

## Prerequisites

**Nimble API Key Required** - Get your key at https://www.nimbleway.com/

Set the `NIMBLE_API_KEY` environment variable using your platform's method:
- **Claude Code:** `~/.claude/settings.json` with `env` object
- **VS Code/GitHub Copilot:** GitHub Actions secrets
- **Shell:** `export NIMBLE_API_KEY="your-key"`

The examples below assume `$NIMBLE_API_KEY` is set.

## Quick Code Lookup

**Scenario**: Need to find code examples for a programming concept

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "async await error handling in TypeScript",
    "focus": "coding",
    "max_results": 5,
    "include_answer": false,
    "deep_search": false
  }'
```

**Why this works:**
- `focus: coding` targets programming resources
- `max_results: 5` quick results for fast reference
- `deep_search: false` fastest response (titles and URLs only)
- `include_answer: false` just need URLs to examples

## Current News Summary

**Scenario**: Get a summary of recent developments

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "latest AI breakthroughs January 2026",
    "focus": "news",
    "max_results": 10,
    "include_answer": true,
    "deep_search": false,
    "time_range": "month"
  }'
```

**Why this works:**
- `focus: news` prioritizes news sources
- `include_answer: true` generates summary (works with deep_search=false)
- `deep_search: false` faster response using snippets for answer generation
- `time_range: month` ensures recency (last 30 days)
- `max_results: 10` enough for good synthesis

## Product Research

**Scenario**: Research products before purchase

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "best ergonomic keyboard for programming 2026",
    "focus": "shopping",
    "max_results": 8,
    "include_answer": true
  }'
```

**Why this works:**
- `focus: shopping` targets product pages
- `answer: true` synthesizes recommendations
- `max_results: 8` balanced coverage

## Academic Paper Discovery

**Scenario**: Find research papers on a topic

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "neural network interpretability methods 2025",
    "focus": "academic",
    "max_results": 15,
    "include_answer": false,
    "include_domains": ["arxiv.org", "scholar.google.com"]
  }'
```

**Why this works:**
- `focus: academic` targets scholarly content
- `include_domains` ensures quality sources
- `answer: false` want to read papers directly
- `max_results: 15` comprehensive coverage

## Social Media Monitoring

**Scenario**: Track social sentiment on a topic

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "developer reactions to new framework release",
    "focus": "social",
    "max_results": 12,
    "include_answer": false,
    "include_domains": ["reddit.com", "twitter.com", "news.ycombinator.com"]
  }'
```

**Why this works:**
- `focus: social` targets social platforms
- `include_domains` specific communities
- `answer: false` want to see individual opinions
- `max_results: 12` diverse perspectives

## Local Business Search

**Scenario**: Find local businesses or services

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "coffee shops with WiFi near downtown Seattle",
    "focus": "location",
    "max_results": 10,
    "include_answer": false
  }'
```

**Why this works:**
- `focus: location` targets local results
- Specific location in query
- `answer: false` want list of options

## Python Integration

```python
import requests
import os

class NimbleSearch:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('NIMBLE_API_KEY')
        self.base_url = "https://nimble-retriever.webit.live/search"

    def search(self, query, focus="general", max_results=10, **kwargs):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "query": query,
            "focus": focus,
            "max_results": max_results,
            **kwargs
        }

        response = requests.post(self.base_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()

# Usage Examples

client = NimbleSearch()

# Code search
results = client.search(
    "React hooks best practices",
    focus="coding",
    max_results=5
)

# News with answer and time filter
results = client.search(
    "AI regulation updates 2026",
    focus="news",
    max_results=10,
    include_answer=True,
    time_range="month"
)

# Shopping research
results = client.search(
    "mechanical keyboard recommendations",
    focus="shopping",
    max_results=8,
    include_answer=True
)

# Academic search with domain filter
results = client.search(
    "quantum computing error correction",
    focus="academic",
    max_results=15,
    include_domains=["arxiv.org", "nature.com"]
)
```

## JavaScript Integration

```javascript
class NimbleSearch {
  constructor(apiKey) {
    this.apiKey = apiKey || process.env.NIMBLE_API_KEY;
    this.baseUrl = 'https://nimble-retriever.webit.live/search';
  }

  async search(query, options = {}) {
    const {
      focus = 'general',
      maxResults = 10,
      ...otherOptions
    } = options;

    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        query,
        focus,
        max_results: maxResults,
        ...otherOptions
      })
    });

    if (!response.ok) {
      throw new Error(`Search failed: ${response.statusText}`);
    }

    return response.json();
  }
}

// Usage Examples

const client = new NimbleSearch();

// Code search
const codeResults = await client.search(
  'React hooks best practices',
  { focus: 'coding', maxResults: 5 }
);

// News with answer
const newsResults = await client.search(
  'AI regulation updates 2026',
  {
    focus: 'news',
    maxResults: 10,
    answer: true,
    dateFilter: '2026-01-01'
  }
);

// Shopping research
const shoppingResults = await client.search(
  'mechanical keyboard recommendations',
  {
    focus: 'shopping',
    maxResults: 8,
    answer: true
  }
);
```

## Common Patterns

### Pattern 1: Quick Answer

When you need a fast answer to a question:

```json
{
  "query": "what are React Server Components",
  "focus": "coding",
  "max_results": 10,
  "include_answer": true,
  "deep_search": false
}
```

### Pattern 2: URL Collection

When building a resource list:

```json
{
  "query": "TypeScript advanced tutorials",
  "focus": "coding",
  "max_results": 15,
  "include_answer": false,
  "deep_search": false
}
```

### Pattern 3: Deep Research

When you need comprehensive analysis:

```json
{
  "query": "microservices architecture patterns",
  "focus": "coding",
  "max_results": 20,
  "include_answer": true,
  "deep_search": true,
  "output_format": "markdown"
}
```

### Pattern 4: Filtered Search

When targeting specific sources:

```json
{
  "query": "GraphQL vs REST comparison",
  "focus": "coding",
  "max_results": 10,
  "include_answer": true,
  "include_domains": [
    "apollo.com",
    "graphql.org",
    "www.howtographql.com"
  ]
}
```

### Pattern 5: Recent Content

When freshness matters:

```json
{
  "query": "JavaScript features 2026",
  "focus": "coding",
  "max_results": 12,
  "include_answer": true,
  "time_range": "year"
}
```

## Error Handling

```python
def safe_search(query, focus="general", max_results=10):
    try:
        client = NimbleSearch()
        return client.search(query, focus, max_results)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            print("Authentication failed. Check your API key.")
        elif e.response.status_code == 429:
            print("Rate limit exceeded. Please wait and retry.")
        elif e.response.status_code == 400:
            print(f"Invalid request: {e.response.json()['error']['message']}")
        else:
            print(f"Unexpected error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

# Usage
results = safe_search("Python async patterns", "coding", 5)
if results:
    print(f"Found {results['total_results']} results")
```

## Tips for Success

1. **Match focus to query type**: coding for programming, news for current events
2. **Start with 10 results**: Balance between coverage and speed
3. **Use answer generation**: When synthesizing information
4. **Filter domains**: For higher quality and relevance
5. **Add date filters**: For time-sensitive queries
6. **Handle errors gracefully**: Always implement proper error handling
7. **Cache results**: Avoid duplicate API calls
8. **Test queries**: Start simple, iterate based on results
