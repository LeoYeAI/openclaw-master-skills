---
name: brave-search
description: |
  Brave Search API integration with managed authentication. Search the web, images, news, and videos with privacy-focused search.
  Use this skill when users want to search the web, find images, get news, or search videos using Brave Search.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
compatibility: Requires network access and valid Maton API key
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Brave Search

Access the Brave Search API with managed authentication. Search the web, images, news, and videos with a privacy-focused search engine.

## Quick Start

```bash
# Web search
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/web/search?q=python+programming&count=5')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/brave-search/{native-api-path}
```

Replace `{native-api-path}` with the actual Brave Search API endpoint path. The gateway proxies requests to `api.search.brave.com` and automatically injects your API key.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Brave Search connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=brave-search&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'brave-search'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "1472d925-86d6-4cbb-8f2f-17e18f6bc0c7",
    "status": "ACTIVE",
    "creation_time": "2026-03-10T11:12:30.963141Z",
    "last_updated_time": "2026-03-10T11:13:55.282885Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "brave-search",
    "metadata": {},
    "method": "API_KEY"
  }
}
```

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Brave Search connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/web/search?q=test')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '1472d925-86d6-4cbb-8f2f-17e18f6bc0c7')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Web Search

```bash
GET /brave-search/res/v1/web/search?q={query}
```

**Required Parameters:**
- `q` (string): Search query (1-400 characters, max 50 words)

**Optional Parameters:**
- `country` (string): 2-letter country code (default: "US")
- `search_lang` (string): Search language code (default: "en")
- `ui_lang` (string): UI language in RFC 9110 format (default: "en-US")
- `count` (integer): Results per page, 1-20 (default: 20)
- `offset` (integer): Page offset, 0-9 (default: 0)
- `safesearch` (string): Filter level - "off", "moderate", "strict" (default: "moderate")
- `freshness` (string): Time filter - "pd" (past day), "pw" (past week), "pm" (past month), "py" (past year), or date range
- `text_decorations` (boolean): Include highlighting markers (default: true)
- `result_filter` (string): Comma-separated result types (discussions, faq, infobox, news, videos, web)
- `extra_snippets` (boolean): Get up to 5 alternative excerpts
- `summary` (boolean): Enable summarizer

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/web/search?q=machine+learning&count=10&freshness=pw')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "search",
  "query": {
    "original": "machine learning",
    "show_strict_warning": false,
    "is_navigational": false,
    "country": "us",
    "more_results_available": true
  },
  "web": {
    "type": "search",
    "results": [
      {
        "title": "Machine Learning - Wikipedia",
        "url": "https://en.wikipedia.org/wiki/Machine_learning",
        "description": "Machine learning is a subset of artificial intelligence...",
        "language": "en",
        "family_friendly": true
      }
    ]
  },
  "discussions": {...},
  "faq": {...},
  "videos": {...}
}
```

### Image Search

```bash
GET /brave-search/res/v1/images/search?q={query}
```

**Required Parameters:**
- `q` (string): Search query

**Optional Parameters:**
- `country` (string): 2-letter country code
- `search_lang` (string): Search language code
- `count` (integer): Results per page, 1-20
- `safesearch` (string): Filter level - "off", "moderate", "strict"

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/images/search?q=sunset&count=5')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "images",
  "results": [
    {
      "title": "Beautiful Sunset",
      "url": "https://example.com/sunset.jpg",
      "source": "https://example.com/gallery",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      },
      "properties": {
        "width": 1920,
        "height": 1080,
        "format": "jpeg"
      }
    }
  ]
}
```

### News Search

```bash
GET /brave-search/res/v1/news/search?q={query}
```

**Required Parameters:**
- `q` (string): Search query

**Optional Parameters:**
- `country` (string): 2-letter country code
- `search_lang` (string): Search language code
- `count` (integer): Results per page, 1-20
- `freshness` (string): Time filter - "pd", "pw", "pm", "py"
- `safesearch` (string): Filter level

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/news/search?q=technology&count=5&freshness=pd')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "news",
  "results": [
    {
      "title": "Latest Tech News",
      "url": "https://example.com/news/tech",
      "description": "Breaking technology news...",
      "age": "2 hours ago",
      "source": {
        "name": "Tech News",
        "url": "https://technews.com"
      },
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      }
    }
  ]
}
```

### Video Search

```bash
GET /brave-search/res/v1/videos/search?q={query}
```

**Required Parameters:**
- `q` (string): Search query

**Optional Parameters:**
- `country` (string): 2-letter country code
- `search_lang` (string): Search language code
- `count` (integer): Results per page, 1-20
- `safesearch` (string): Filter level

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/videos/search?q=tutorial&count=5')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "videos",
  "results": [
    {
      "title": "Python Tutorial for Beginners",
      "url": "https://www.youtube.com/watch?v=...",
      "description": "Learn Python programming...",
      "age": "1 year ago",
      "duration": "3:45:00",
      "thumbnail": {
        "src": "https://imgs.search.brave.com/..."
      },
      "meta_url": {
        "hostname": "www.youtube.com"
      }
    }
  ]
}
```

### Local POIs

```bash
GET /brave-search/res/v1/local/pois?ids={poi_ids}
```

Get details about local points of interest by their IDs (obtained from web search results).

**Required Parameters:**
- `ids` (string): Comma-separated POI IDs

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/local/pois?ids=poi_123,poi_456')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "local_pois",
  "results": [
    {
      "id": "poi_123",
      "name": "Coffee Shop",
      "address": "123 Main St",
      "phone": "+1-555-1234",
      "rating": 4.5,
      "reviews": 128
    }
  ]
}
```

### POI Descriptions

```bash
GET /brave-search/res/v1/local/descriptions?ids={poi_ids}
```

Get detailed descriptions for local points of interest.

**Required Parameters:**
- `ids` (string): Comma-separated POI IDs

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/local/descriptions?ids=poi_123')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "local_descriptions",
  "results": [
    {
      "id": "poi_123",
      "description": "A cozy coffee shop known for artisanal brews..."
    }
  ]
}
```

### Autosuggest

> **Note:** Requires Autosuggest subscription plan.

```bash
GET /brave-search/res/v1/suggest/search?q={query}
```

Get search suggestions as users type.

**Required Parameters:**
- `q` (string): Partial search query

**Optional Parameters:**
- `country` (string): 2-letter country code
- `count` (integer): Number of suggestions to return
- `rich` (boolean): Enable enhanced metadata

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/suggest/search?q=how+to&count=5&rich=true')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "suggest",
  "query": {
    "original": "how to"
  },
  "results": [
    {
      "query": "how to learn python",
      "is_entity": false
    },
    {
      "query": "how to code",
      "is_entity": false
    }
  ]
}
```

### Spellcheck

> **Note:** Requires Spellcheck subscription plan.

```bash
GET /brave-search/res/v1/spellcheck/search?q={query}
```

Check spelling and get corrections.

**Required Parameters:**
- `q` (string): Query to check for spelling errors
- `country` (string): Country code for localized corrections

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/spellcheck/search?q=helo+wrold&country=US')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "type": "spellcheck",
  "query": {
    "original": "helo wrold"
  },
  "results": [
    {
      "query": "hello world"
    }
  ]
}
```

### Summarizer

> **Note:** Requires Summarizer subscription plan.

First, perform a web search with `summary=1` to get a summarizer key, then use that key to fetch the summary.

#### Get Summarizer Key

```bash
GET /brave-search/res/v1/web/search?q={query}&summary=1
```

#### Fetch Summary

```bash
GET /brave-search/res/v1/summarizer/search?key={summarizer_key}
```

**Optional Parameters:**
- `entity_info` (boolean): Include entity details
- `inline_references` (boolean): Include citation markers

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json

# Step 1: Get summarizer key from web search
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/web/search?q=what+is+python&summary=1')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
data = json.load(urllib.request.urlopen(req))
summarizer_key = data.get('summarizer', {}).get('key')

# Step 2: Fetch summary using the key
if summarizer_key:
    req = urllib.request.Request(f'https://gateway.maton.ai/brave-search/res/v1/summarizer/search?key={summarizer_key}')
    req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
    print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

#### Additional Summarizer Endpoints

```bash
GET /brave-search/res/v1/summarizer/summary?key={key}           # Summary only
GET /brave-search/res/v1/summarizer/title?key={key}             # Title only
GET /brave-search/res/v1/summarizer/enrichments?key={key}       # Enrichment data
GET /brave-search/res/v1/summarizer/followups?key={key}         # Follow-up suggestions
GET /brave-search/res/v1/summarizer/entity_info?key={key}       # Entity information
```

## Pagination

Use `count` and `offset` for pagination:

```bash
# First page (results 1-10)
GET /brave-search/res/v1/web/search?q=test&count=10&offset=0

# Second page (results 11-20)
GET /brave-search/res/v1/web/search?q=test&count=10&offset=1
```

**Note:** `offset` ranges from 0-9, giving access to up to 200 results (20 results × 10 pages).

Check `query.more_results_available` in the response to determine if more results exist.

## Location Headers

For location-aware results, include location headers:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/brave-search/res/v1/web/search?q=restaurants+near+me&count=10')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('x-loc-lat', '37.7749')
req.add_header('x-loc-long', '-122.4194')
req.add_header('x-loc-city', 'San Francisco')
req.add_header('x-loc-state', 'CA')
req.add_header('x-loc-country', 'US')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Available Location Headers:**
- `x-loc-lat`: Latitude (-90 to 90)
- `x-loc-long`: Longitude (-180 to 180)
- `x-loc-timezone`: IANA timezone identifier
- `x-loc-city`: City name
- `x-loc-state`: State/province
- `x-loc-country`: 2-letter country code
- `x-loc-postal-code`: ZIP/postal code

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/brave-search/res/v1/web/search?q=javascript&count=10',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
console.log(data.web.results);
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/brave-search/res/v1/web/search',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    params={'q': 'python programming', 'count': 10}
)
data = response.json()
for result in data.get('web', {}).get('results', []):
    print(f"{result['title']}: {result['url']}")
```

## Notes

- Maximum 20 results per request
- Maximum 10 pages of results (offset 0-9)
- Query length: 1-400 characters, max 50 words
- Brave Search is privacy-focused and doesn't track users
- Results include multiple types: web, news, videos, discussions, FAQ, infobox
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Brave Search connection |
| 401 | Invalid or missing Maton API key |
| 404 | Subscription not found |
| 422 | Invalid subscription token |
| 429 | Rate limited or quota exceeded |
| 4xx/5xx | Passthrough error from Brave Search API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `brave-search`. For example:

- Correct: `https://gateway.maton.ai/brave-search/res/v1/web/search?q=test`
- Incorrect: `https://gateway.maton.ai/res/v1/web/search?q=test`

## Resources

- [Brave Search API Documentation](https://api-dashboard.search.brave.com/documentation)
- [Brave Search API Dashboard](https://api-dashboard.search.brave.com/)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
