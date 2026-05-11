---
name: firecrawl
description: |
  Firecrawl API integration with managed authentication. Scrape, crawl, map, and search web content.
  Use this skill when users want to extract content from websites, crawl entire sites, map URLs, or search the web.
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

# Firecrawl

Access the Firecrawl API with managed authentication. Scrape webpages, crawl entire websites, map site URLs, and search the web with full content extraction.

## Quick Start

```bash
# Scrape a webpage
python <<'EOF'
import urllib.request, os, json
data = json.dumps({"url": "https://example.com", "formats": ["markdown"]}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/scrape', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/firecrawl/{native-api-path}
```

Replace `{native-api-path}` with the actual Firecrawl API endpoint path. The gateway proxies requests to `api.firecrawl.dev` and automatically injects your API key.

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

Manage your Firecrawl connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=firecrawl&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'firecrawl'}).encode()
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
    "connection_id": "b5449045-2dcd-4e99-816f-65f80511affb",
    "status": "ACTIVE",
    "creation_time": "2026-03-11T09:49:09.917114Z",
    "last_updated_time": "2026-03-11T09:49:27.616143Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "firecrawl",
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

If you have multiple Firecrawl connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({"url": "https://example.com"}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/scrape', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', 'b5449045-2dcd-4e99-816f-65f80511affb')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Scrape

```bash
POST /firecrawl/v2/scrape
```

Extract content from a single webpage.

**Required Parameters:**
- `url` (string): The webpage URL to scrape

**Optional Parameters:**
- `formats` (array): Output formats - "markdown", "html", "json", "screenshot", "links" (default: ["markdown"])
- `onlyMainContent` (boolean): Extract only main content, exclude headers/footers (default: true)
- `includeTags` (array): HTML tags to include
- `excludeTags` (array): HTML tags to exclude
- `waitFor` (integer): Milliseconds to wait before scraping (default: 0)
- `timeout` (integer): Request timeout in ms (default: 30000, max: 300000)
- `mobile` (boolean): Emulate mobile device (default: false)
- `actions` (array): Browser actions to perform before scraping
- `headers` (object): Custom HTTP headers
- `blockAds` (boolean): Block ads and cookie banners (default: true)

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "url": "https://docs.firecrawl.dev",
    "formats": ["markdown", "html"],
    "onlyMainContent": True,
    "waitFor": 1000
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/scrape', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "data": {
    "markdown": "# Example Domain\n\nThis domain is for use in documentation...",
    "metadata": {
      "title": "Example Domain",
      "language": "en",
      "sourceURL": "https://example.com",
      "url": "https://example.com/",
      "statusCode": 200,
      "contentType": "text/html",
      "creditsUsed": 1
    }
  }
}
```

### Crawl (Start)

```bash
POST /firecrawl/v2/crawl
```

Start crawling an entire website. Returns a crawl ID for status polling.

**Required Parameters:**
- `url` (string): The base URL to start crawling from

**Optional Parameters:**
- `limit` (integer): Maximum pages to crawl (default: 10000)
- `maxDepth` (integer): Maximum crawl depth
- `includePaths` (array): Regex patterns for URLs to include
- `excludePaths` (array): Regex patterns for URLs to exclude
- `allowSubdomains` (boolean): Enable subdomain crawling
- `allowExternalLinks` (boolean): Follow external links
- `scrapeOptions` (object): Options for each page scrape (formats, onlyMainContent, etc.)
- `webhook` (string): Webhook URL for completion notification

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "url": "https://example.com",
    "limit": 10,
    "scrapeOptions": {
        "formats": ["markdown"]
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/crawl', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "id": "019cdc53-0acf-76ec-a80c-3ead753b2730",
  "url": "https://api.firecrawl.dev/v1/crawl/019cdc53-0acf-76ec-a80c-3ead753b2730"
}
```

### Crawl (Get Status)

```bash
GET /firecrawl/v2/crawl/{id}
```

Get the status and results of a crawl job.

**Path Parameters:**
- `id` (string): The crawl job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
crawl_id = "019cdc53-0acf-76ec-a80c-3ead753b2730"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/crawl/{crawl_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "completed": 2,
  "total": 2,
  "creditsUsed": 2,
  "expiresAt": "2026-03-12T09:56:00.000Z",
  "data": [
    {
      "markdown": "# Example Domain\n\nThis domain is for use in documentation...",
      "metadata": {
        "title": "Example Domain",
        "sourceURL": "https://example.com",
        "statusCode": 200
      }
    }
  ]
}
```

**Status Values:**
- `scraping` - Crawl in progress
- `completed` - Crawl finished successfully
- `failed` - Crawl failed

### Crawl (Cancel)

```bash
DELETE /firecrawl/v2/crawl/{id}
```

Cancel an in-progress crawl job.

**Path Parameters:**
- `id` (string): The crawl job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
crawl_id = "019cdc53-0acf-76ec-a80c-3ead753b2730"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/crawl/{crawl_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "status": "cancelled"
}
```

### Map

```bash
POST /firecrawl/v2/map
```

Get all URLs from a website without scraping content.

**Required Parameters:**
- `url` (string): The starting URL

**Optional Parameters:**
- `search` (string): Query to order results by relevance
- `limit` (integer): Maximum links to return (default: 5000, max: 100000)
- `includeSubdomains` (boolean): Include subdomains (default: true)
- `sitemap` (string): Sitemap handling - "skip", "include", "only" (default: "include")
- `ignoreQueryParameters` (boolean): Exclude URLs with query params (default: true)
- `timeout` (integer): Timeout in milliseconds

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "url": "https://docs.firecrawl.dev",
    "limit": 100,
    "includeSubdomains": False
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/map', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "links": [
    "https://docs.firecrawl.dev",
    "https://docs.firecrawl.dev/api-reference",
    "https://docs.firecrawl.dev/introduction"
  ]
}
```

### Search

```bash
POST /firecrawl/v2/search
```

Search the web and get full page content for each result.

**Required Parameters:**
- `query` (string): Search query (max 500 characters)

**Optional Parameters:**
- `limit` (integer): Number of results (default: 5, max: 100)
- `sources` (array): Search types - "web", "images", "news" (default: ["web"])
- `country` (string): ISO country code (default: "US")
- `location` (string): Geographic targeting (e.g., "Germany")
- `tbs` (string): Time filter - "qdr:d" (day), "qdr:w" (week), "qdr:m" (month), "qdr:y" (year)
- `timeout` (integer): Timeout in ms (default: 60000)
- `scrapeOptions` (object): Options for content extraction

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "query": "web scraping best practices",
    "limit": 5,
    "scrapeOptions": {
        "formats": ["markdown"]
    }
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/search', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "url": "https://example.com/article",
      "title": "Web Scraping Best Practices",
      "description": "Learn the best practices for web scraping...",
      "markdown": "# Web Scraping Best Practices\n\n..."
    }
  ],
  "creditsUsed": 5
}
```

### Batch Scrape (Start)

```bash
POST /firecrawl/v2/batch/scrape
```

Scrape multiple URLs in a single batch job.

**Required Parameters:**
- `urls` (array): List of URLs to scrape

**Optional Parameters:**
- `formats` (array): Output formats (default: ["markdown"])
- `onlyMainContent` (boolean): Extract only main content (default: true)
- `webhook` (string): Webhook URL for completion notification

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "urls": ["https://example.com", "https://example.org"],
    "formats": ["markdown"]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/batch/scrape', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "id": "019cdc59-56b9-7096-a9f9-95fcc92a3a75",
  "url": "https://api.firecrawl.dev/v1/batch/scrape/019cdc59-56b9-7096-a9f9-95fcc92a3a75"
}
```

### Batch Scrape (Get Status)

```bash
GET /firecrawl/v2/batch/scrape/{id}
```

Get the status and results of a batch scrape job.

**Path Parameters:**
- `id` (string): The batch scrape job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
batch_id = "019cdc59-56b9-7096-a9f9-95fcc92a3a75"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/batch/scrape/{batch_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "completed": 2,
  "total": 2,
  "creditsUsed": 2,
  "expiresAt": "2026-03-12T10:02:54.000Z",
  "data": [
    {
      "markdown": "# Example Domain\n\n...",
      "metadata": {
        "title": "Example Domain",
        "sourceURL": "https://example.com",
        "statusCode": 200
      }
    }
  ]
}
```

### Batch Scrape (Cancel)

```bash
DELETE /firecrawl/v2/batch/scrape/{id}
```

Cancel an in-progress batch scrape job.

**Path Parameters:**
- `id` (string): The batch scrape job ID

### Batch Scrape (Get Errors)

```bash
GET /firecrawl/v2/batch/scrape/{id}/errors
```

Get errors from a batch scrape job.

**Path Parameters:**
- `id` (string): The batch scrape job ID

**Response:**
```json
{
  "errors": [],
  "robotsBlocked": []
}
```

### Crawl (Get Errors)

```bash
GET /firecrawl/v2/crawl/{id}/errors
```

Get errors from a crawl job.

**Path Parameters:**
- `id` (string): The crawl job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
crawl_id = "019cdc53-0acf-76ec-a80c-3ead753b2730"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/crawl/{crawl_id}/errors')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "errors": [],
  "robotsBlocked": []
}
```

### Crawl (Get Active)

```bash
GET /firecrawl/v2/crawl/active
```

Get all active crawl jobs.

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/crawl/active')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "crawls": []
}
```

### Extract (Start)

```bash
POST /firecrawl/v2/extract
```

Extract structured data from URLs using AI.

**Required Parameters:**
- `urls` (array): List of URLs to extract from
- `prompt` (string): Natural language description of what to extract

**Optional Parameters:**
- `schema` (object): JSON schema for structured output
- `scrapeOptions` (object): Options for scraping

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "urls": ["https://example.com"],
    "prompt": "Extract the main heading and description"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/extract', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "id": "019cdc59-977b-774b-b584-af2af45c055b",
  "urlTrace": []
}
```

### Extract (Get Status)

```bash
GET /firecrawl/v2/extract/{id}
```

Get the status and results of an extract job.

**Path Parameters:**
- `id` (string): The extract job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
extract_id = "019cdc59-977b-774b-b584-af2af45c055b"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/extract/{extract_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "heading": "Example Domain",
      "description": "This domain is for use in documentation..."
    }
  ],
  "status": "completed",
  "expiresAt": "2026-03-11T16:03:05.000Z"
}
```

### Browser (Create Session)

```bash
POST /firecrawl/v2/browser
```

Create an interactive browser session for manual control via CDP.

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/browser', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "id": "019cdc5d-5c9d-732e-a7bd-f095a96a2bb1",
  "cdpUrl": "wss://browser.firecrawl.dev/cdp/...",
  "liveViewUrl": "https://liveview.firecrawl.dev/...",
  "interactiveLiveViewUrl": "https://liveview.firecrawl.dev/...",
  "expiresAt": "2026-03-11T10:17:12.409Z"
}
```

### Browser (List Sessions)

```bash
GET /firecrawl/v2/browser
```

List all active browser sessions.

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/browser')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "id": "019cdc5d-5c9d-732e-a7bd-f095a96a2bb1",
      "status": "active",
      "cdpUrl": "wss://browser.firecrawl.dev/cdp/...",
      "liveViewUrl": "https://liveview.firecrawl.dev/..."
    }
  ]
}
```

### Browser (Delete Session)

```bash
DELETE /firecrawl/v2/browser/{id}
```

Delete a browser session.

**Path Parameters:**
- `id` (string): The browser session ID

### Agent (Start)

```bash
POST /firecrawl/v2/agent
```

Start an AI agent to autonomously navigate and extract data.

**Required Parameters:**
- `prompt` (string): Description of what data to extract (max 10,000 chars)

**Optional Parameters:**
- `urls` (array): URLs to constrain the agent to
- `schema` (object): JSON schema for structured output
- `maxCredits` (integer): Spending limit (default: 2500)
- `strictConstrainToURLs` (boolean): Only visit provided URLs
- `model` (string): "spark-1-mini" (default, cheaper) or "spark-1-pro" (higher accuracy)

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "prompt": "Find the pricing information",
    "urls": ["https://example.com"],
    "model": "spark-1-mini"
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/agent', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "id": "019cdc5d-a2d4-728c-9c91-e9eae475568f"
}
```

### Agent (Get Status)

```bash
GET /firecrawl/v2/agent/{id}
```

Get the status and results of an agent job.

**Path Parameters:**
- `id` (string): The agent job ID

**Example:**
```bash
python <<'EOF'
import urllib.request, os, json
agent_id = "019cdc5d-a2d4-728c-9c91-e9eae475568f"
req = urllib.request.Request(f'https://gateway.maton.ai/firecrawl/v2/agent/{agent_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "success": true,
  "status": "completed",
  "model": "spark-1-pro",
  "data": {...},
  "expiresAt": "2026-03-12T10:07:30.055Z"
}
```

### Agent (Cancel)

```bash
DELETE /firecrawl/v2/agent/{id}
```

Cancel an in-progress agent job.

**Path Parameters:**
- `id` (string): The agent job ID

## Browser Actions

Use `actions` parameter to interact with pages before scraping:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({
    "url": "https://example.com",
    "formats": ["markdown", "screenshot"],
    "actions": [
        {"type": "wait", "milliseconds": 2000},
        {"type": "click", "selector": "#load-more"},
        {"type": "scroll", "direction": "down", "amount": 500},
        {"type": "screenshot"}
    ]
}).encode()
req = urllib.request.Request('https://gateway.maton.ai/firecrawl/v2/scrape', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Available Actions:**
- `wait` - Wait for specified milliseconds
- `click` - Click an element by CSS selector
- `write` - Type text into an input field
- `scroll` - Scroll the page
- `screenshot` - Take a screenshot
- `execute` - Run custom JavaScript

## Code Examples

### JavaScript

```javascript
const response = await fetch('https://gateway.maton.ai/firecrawl/v2/scrape', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.MATON_API_KEY}`
  },
  body: JSON.stringify({
    url: 'https://example.com',
    formats: ['markdown']
  })
});
const data = await response.json();
console.log(data.data.markdown);
```

### Python

```python
import os
import requests

response = requests.post(
    'https://gateway.maton.ai/firecrawl/v2/scrape',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'},
    json={
        'url': 'https://example.com',
        'formats': ['markdown']
    }
)
data = response.json()
print(data['data']['markdown'])
```

## Notes

- Scrape uses 1 credit per page (basic proxy)
- Enhanced proxy for anti-bot sites uses up to 5 credits
- Crawl results expire after 24 hours
- Maximum timeout is 300,000ms (5 minutes)
- Use `onlyMainContent: true` to get cleaner output without navigation/footer
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Firecrawl connection or invalid parameters |
| 401 | Invalid or missing Maton API key |
| 402 | Payment required (Firecrawl credits exhausted) |
| 409 | Conflict (e.g., crawl already completed) |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Firecrawl API |

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

1. Ensure your URL path starts with `firecrawl`. For example:

- Correct: `https://gateway.maton.ai/firecrawl/v2/scrape`
- Incorrect: `https://gateway.maton.ai/v2/scrape`

## Resources

- [Firecrawl API Documentation](https://docs.firecrawl.dev/api-reference/v2-introduction)
- [Firecrawl Dashboard](https://firecrawl.dev)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
