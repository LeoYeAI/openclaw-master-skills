# Nimble Search API Reference

Complete API documentation for the Nimble Search endpoint.

## Prerequisites

**Nimble API Key Required** - Get your key at https://www.nimbleway.com/

Set the `NIMBLE_API_KEY` environment variable:

- **Claude Code:** Add to `~/.claude/settings.json` in `env` object
- **VS Code/GitHub Copilot:** Use GitHub Actions secrets or repository config
- **Shell:** `export NIMBLE_API_KEY="your-api-key-here"`

The skill works with any platform that supports environment variables.

## Authentication

All requests require an API key passed in the Authorization header:

```bash
Authorization: Bearer $NIMBLE_API_KEY
```

**Always validate the API key before making requests:**

```bash
if [ -z "$NIMBLE_API_KEY" ]; then
  echo "❌ Error: NIMBLE_API_KEY not configured"
  echo "Get your key at https://www.nimbleway.com/"
  echo "Set using your platform's environment variable method"
  exit 1
fi
```

## Endpoint

```
POST https://nimble-retriever.webit.live/search
```

## Request Parameters

### Required Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Search query (max 500 characters) |

### Optional Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `focus` | string | `"general"` | Search focus mode: `general`, `coding`, `news`, `academic`, `shopping`, `social`, `geo`, `location` |
| `max_results` | integer | `10` | Number of results to return (1-100) |
| `include_answer` | boolean | `false` | Generate AI-powered answer from results |
| `deep_search` | boolean | `true` | **Recommended: `false`** for fastest response. Set `true` only when full page content is needed |
| `output_format` | string | `"markdown"` | Content format: `markdown`, `plain_text`, `simplified_html` |
| `include_domains` | array | `[]` | Only include results from these domains (max 50) |
| `exclude_domains` | array | `[]` | Exclude results from these domains (max 50) |
| `time_range` | string | `null` | **Recommended:** Filter by recency: `hour`, `day`, `week`, `month`, `year` |
| `start_date` | string | `null` | Filter results after this date (YYYY-MM-DD or YYYY). Mutually exclusive with `time_range` |
| `end_date` | string | `null` | Filter results before this date (YYYY-MM-DD or YYYY). Mutually exclusive with `time_range` |
| `content_type` | array | `[]` | Filter by file type (general focus only): `pdf`, `docx`, `documents`, etc. |
| `max_subagents` | integer | `3` | Max parallel subagents for shopping/social/geo (1-5) |
| `locale` | string | `"en"` | Search language locale |
| `country` | string | `"US"` | Search country code |

## Request Example

```bash
curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "React Server Components tutorial",
    "focus": "coding",
    "max_results": 10,
    "include_answer": true,
    "deep_search": false,
    "time_range": "month",
    "include_domains": ["reactjs.org", "nextjs.org"]
  }'
```

## Time Filtering

### Using time_range (Recommended)

For simple recency filtering, use `time_range` - it's the easiest way to filter results by how recent they are:

```json
{
  "query": "AI developments",
  "focus": "news",
  "time_range": "week"
}
```

**Available values:**
- `"hour"` - Last hour
- `"day"` - Last 24 hours
- `"week"` - Last 7 days
- `"month"` - Last 30 days
- `"year"` - Last 365 days

### Using start_date and end_date (Alternative)

For precise date ranges, use `start_date` and `end_date`:

```json
{
  "query": "tech trends 2026",
  "focus": "general",
  "start_date": "2026-01-01",
  "end_date": "2026-06-30"
}
```

**Date formats:**
- Full date: `YYYY-MM-DD` (e.g., `"2026-01-15"`)
- Year only: `YYYY` (e.g., `"2026"`)

**Important:** `time_range` and date filters (`start_date`/`end_date`) are **mutually exclusive**. Using both will result in an error. `time_range` takes precedence and is recommended for most use cases.

## Deep Search Configuration

### When to use deep_search=false (Recommended)

Use `deep_search=false` for **fastest response** times:

```json
{
  "query": "React hooks tutorial",
  "focus": "coding",
  "deep_search": false
}
```

**Returns:** Title, description/snippet, URL for each result

**Best for:**
- Quick reference lookups
- URL discovery
- Fast research scans
- Answer generation (works with snippets)
- Resource collection

### When to use deep_search=true

Use `deep_search=true` only when you need **full page content**:

```json
{
  "query": "API documentation",
  "focus": "coding",
  "deep_search": true,
  "output_format": "markdown"
}
```

**Returns:** Full page content + title, description, URL

**Best for:**
- Detailed content analysis
- Text extraction and archiving
- Processing full documentation
- Building comprehensive datasets

**Performance note:** `deep_search=true` takes significantly longer as it fetches and parses full page content.

## Response Format

### Success Response (200 OK)

```json
{
  "status": "success",
  "query": "React Server Components tutorial",
  "focus": "coding",
  "total_results": 10,
  "results": [
    {
      "url": "https://reactjs.org/blog/2023/03/22/react-labs-what-we-have-been-working-on-march-2023.html",
      "title": "React Labs: What We've Been Working On – March 2023",
      "description": "An update on React Server Components and what we've learned...",
      "content": "Full page content in markdown format (if deep_search=true)",
      "published_date": "2023-03-22T00:00:00Z",
      "domain": "reactjs.org"
    }
  ],
  "include_answer": "React Server Components (RSC) is a new feature that allows...",
  "urls": [
    "https://reactjs.org/blog/2023/03/22/...",
    "https://nextjs.org/docs/app/building-your-application/..."
  ],
  "processing_time_ms": 1247
}
```

### Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "max_results must be between 1 and 20",
    "parameter": "max_results"
  }
}
```

## Response Fields

### Root Level

| Field | Type | Description |
|-------|------|-------------|
| `status` | string | `"success"` or `"error"` |
| `query` | string | Original search query |
| `focus` | string | Focus mode used |
| `total_results` | integer | Number of results returned |
| `results` | array | Array of search result objects |
| `answer` | string | AI-generated answer (if `include_answer=true`) |
| `urls` | array | List of result URLs |
| `processing_time_ms` | integer | Processing time in milliseconds |

### Result Object

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Result URL |
| `title` | string | Page title |
| `description` | string | Page description/snippet |
| `content` | string | Full page content (if `deep_search=true`) |
| `published_date` | string | Publication date (ISO 8601) |
| `domain` | string | Domain name |

## Error Codes

| Code | HTTP Status | Description | Solution |
|------|------------|-------------|----------|
| `AUTHENTICATION_FAILED` | 401 | Invalid or missing API key | Check API key is correct and active |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests | Wait and retry, or upgrade plan |
| `INVALID_PARAMETER` | 400 | Invalid parameter value | Check parameter format and constraints |
| `QUERY_TOO_LONG` | 400 | Query exceeds max length | Shorten query to ≤500 characters |
| `INVALID_FOCUS_MODE` | 400 | Unknown focus mode | Use valid focus mode |
| `INVALID_DATE_FORMAT` | 400 | Invalid start_date format | Use ISO 8601 format (YYYY-MM-DD) |
| `MAX_RESULTS_EXCEEDED` | 400 | max_results too large | Set max_results between 1-20 |
| `TIMEOUT` | 504 | Request timed out | Retry with fewer results |
| `INTERNAL_ERROR` | 500 | Server error | Retry with exponential backoff |

## Rate Limits

Rate limits vary by plan:

| Plan | Requests/Min | Requests/Day |
|------|-------------|--------------|
| Free | 10 | 100 |
| Basic | 60 | 1,000 |
| Pro | 300 | 10,000 |
| Enterprise | Custom | Custom |

Rate limit headers included in response:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640000000
```

## Best Practices

### Performance Optimization

1. **Start Small**: Begin with 10 results, increase if needed
2. **Cache Results**: Store results locally when appropriate
3. **Batch Queries**: Group related queries
4. **Use Focus Modes**: Dramatically improves relevance
5. **Domain Filtering**: Reduces noise, speeds up processing

### Cost Optimization

1. **Disable Content Extraction**: Only use when needed
2. **Minimize max_results**: More results = higher cost
3. **Skip Answer Generation**: When not synthesizing
4. **Smart Retries**: Don't retry immediately on errors
5. **Result Caching**: Avoid duplicate queries

### Quality Optimization

1. **Choose Right Focus**: Critical for relevance
2. **Specific Queries**: More context = better results
3. **Domain Filtering**: Target authoritative sources
4. **Date Filtering**: For time-sensitive queries
5. **Content Extraction**: For deeper analysis

## Code Examples

### Python

```python
import requests
import os

def nimble_search(query, focus="general", max_results=10):
    url = "https://nimble-retriever.webit.live/search"
    headers = {
        "Authorization": f"Bearer {os.getenv('NIMBLE_API_KEY')}",
        "Content-Type": "application/json"
    }
    data = {
        "query": query,
        "focus": focus,
        "max_results": max_results,
        "include_answer": True
    }

    response = requests.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

# Usage
results = nimble_search("React hooks tutorial", focus="coding", max_results=5)
print(results["answer"])
for result in results["results"]:
    print(f"{result['title']}: {result['url']}")
```

### Node.js

```javascript
const axios = require('axios');

async function nimbleSearch(query, focus = 'general', maxResults = 10) {
  const url = 'https://nimble-retriever.webit.live/search';
  const headers = {
    'Authorization': `Bearer ${process.env.NIMBLE_API_KEY}`,
    'Content-Type': 'application/json'
  };
  const data = {
    query,
    focus,
    max_results: maxResults,
    answer: true
  };

  const response = await axios.post(url, data, { headers });
  return response.data;
}

// Usage
const results = await nimbleSearch('React hooks tutorial', 'coding', 5);
console.log(results.answer);
results.results.forEach(result => {
  console.log(`${result.title}: ${result.url}`);
});
```

### cURL

```bash
#!/bin/bash

QUERY="React hooks tutorial"
FOCUS="coding"
MAX_RESULTS=5

curl -X POST https://nimble-retriever.webit.live/search \
  -H "Authorization: Bearer $NIMBLE_API_KEY" \
  -H "Content-Type: application/json" \
  -d @- <<EOF
{
  "query": "$QUERY",
  "focus": "$FOCUS",
  "max_results": $MAX_RESULTS,
  "include_answer": true
}
EOF
```

## Advanced Usage

### Parallel Searches

Run multiple searches concurrently for different perspectives:

```python
import asyncio
import aiohttp

async def parallel_search(queries):
    async with aiohttp.ClientSession() as session:
        tasks = [search_async(session, q) for q in queries]
        return await asyncio.gather(*tasks)

# Search with multiple focus modes
queries = [
    {"query": "AI frameworks", "focus": "coding"},
    {"query": "AI frameworks", "focus": "news"},
    {"query": "AI frameworks", "focus": "academic"}
]
results = await parallel_search(queries)
```

### Retry Logic

Implement exponential backoff for reliability:

```python
import time

def search_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return nimble_search(query)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limit
                wait_time = 2 ** attempt
                time.sleep(wait_time)
            else:
                raise
    raise Exception("Max retries exceeded")
```

### Response Caching

Cache results to avoid duplicate API calls:

```python
from functools import lru_cache
import hashlib
import json

@lru_cache(maxsize=100)
def cached_search(query, focus="general", max_results=10):
    return nimble_search(query, focus, max_results)

# Or use file-based caching
def file_cached_search(query, focus="general"):
    cache_key = hashlib.md5(f"{query}{focus}".encode()).hexdigest()
    cache_file = f"cache/{cache_key}.json"

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            return json.load(f)

    results = nimble_search(query, focus)

    with open(cache_file, 'w') as f:
        json.dump(results, f)

    return results
```

## Troubleshooting

### Common Issues

**Issue: No results returned**
- Solution: Broaden query, try different focus mode, check domain filters

**Issue: Slow response times**
- Solution: Reduce max_results, disable content extraction, try simpler query

**Issue: Poor result relevance**
- Solution: Use more specific focus mode, add domain filters, refine query

**Issue: Rate limit errors**
- Solution: Add delays, reduce request frequency, upgrade plan

**Issue: Timeout errors**
- Solution: Reduce max_results, disable deep extraction, retry with backoff

### Debug Mode

Enable debug logging to troubleshoot:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def nimble_search_debug(query, **kwargs):
    logger.debug(f"Search query: {query}")
    logger.debug(f"Parameters: {kwargs}")

    try:
        response = nimble_search(query, **kwargs)
        logger.debug(f"Results: {len(response['results'])} found")
        return response
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise
```

## Changelog

### Version 1.0.0 (Current)
- Initial release
- 8 focus modes
- LLM answer generation
- Deep content extraction
- Domain and date filtering

## Support

- Documentation: https://docs.nimbleway.com/nimble-sdk/search-api
- API Status: https://status.nimbleway.com
- Support: support@nimbleway.com
- Community: https://community.nimbleway.com
