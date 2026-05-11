---
name: desearch-web-search
description: Search the web and get real-time SERP-style results with titles, URLs, and snippets. Use this for general web queries when you need current links and information from across the internet.
metadata: {"clawdbot":{"emoji":"🌐","homepage":"https://desearch.ai","requires":{"env":["DESEARCH_API_KEY"]}}}
---

# Web Search By Desearch

Real-time web search returning structured SERP-style results with titles, links, and snippets.

## Quick Start

1. Get an API key from https://console.desearch.ai
2. Set environment variable: `export DESEARCH_API_KEY='your-key-here'`

## Usage

```bash
# Basic web search
desearch.py web "quantum computing"

# Paginated results
desearch.py web "quantum computing" --start 10
```

## Options

| Option | Description |
|--------|-------------|
| `--start` | Pagination offset (default: 0). Use to get the next page of results. |

## Response

### Example
```bash
desearch.py web "best sights in Georgia"
```

```json
{
  "data": [
    {
      "title": "Cool places and fun things to do in Georgia ? : r/solotravel",
      "snippet": "I was in Georgia earlier this month. My favorite place was Mtirala National Park in Adjara. The mountains and forest were absolutely beautiful ...",
      "link": "https://www.reddit.com/r/solotravel/comments/py4wls/cool_places_and_fun_things_to_do_in_georgia/",
    },
  ]
}
```

### Notes
- Returns up to 10 results per page. Use `--start` to paginate.

### Errors
Status 401, Unauthorized (e.g., missing/invalid API key)
```json
{
  "detail": "Invalid or missing API key"
}
```

Status 402, Payment Required (e.g., balance depleted)
```json
{
  "detail": "Insufficient balance, please add funds to your account to continue using the service."
}
```

## Resources
- [API Reference](https://desearch.ai/docs/api-reference/get-web)
- [Desearch Console](https://console.desearch.ai)