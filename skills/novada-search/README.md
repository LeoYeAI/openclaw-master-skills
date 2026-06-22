# Novada Search

[![PyPI](https://img.shields.io/pypi/v/novada-search)](https://pypi.org/project/novada-search/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)

Multi-engine AI search for agents and developers. 9 engines, 13 Google sub-types, 9 vertical scenes.

**[Get API Key (free) →](https://novada.com)**

## Quick Start

```bash
pip install novada-search
export NOVADA_API_KEY="your_key"
```

### Python SDK

```python
from novada_search import NovadaSearch

client = NovadaSearch(api_key="your_key")

# Multi-engine parallel search with dedup
result = client.search("AI trends", mode="multi", engines=["google", "bing"])

# Auto-detect intent (news, academic, jobs, etc.)
result = client.search("latest AI news", mode="auto")

# Extract content from URL
content = client.extract("https://example.com/article")

# Coming soon: Shopping price comparison, Local business search, Research mode
```

### CLI

```bash
novada-search --query "latest AI news" --mode auto
novada-search --query "AI trends" --mode multi --engines google,bing
novada-search --url "https://example.com" --mode extract
# Coming in v1.1: --scene shopping, --scene local, --mode research
```

### MCP Server

Use with Claude Desktop / OpenClaw:

```json
{
  "mcpServers": {
    "novada-search": {
      "command": "python3",
      "args": ["/path/to/novada_mcp_server.py"],
      "env": { "NOVADA_API_KEY": "your_key" }
    }
  }
}
```

### LangChain

```python
from integrations.langchain_tool import NovadaSearchTool

tool = NovadaSearchTool(api_key="your_key")
```

## Engines

| Engine | Best for |
|--------|----------|
| Google | General web + 13 sub-types (Shopping, News, Scholar, Jobs, Flights, Finance, Videos, Images, Patents, Play, Lens) |
| Bing | Web, news |
| Yahoo | Finance |
| DuckDuckGo | Privacy-focused search |
| Yandex | Russian web |
| YouTube | Video search |
| eBay | E-commerce, auctions |
| Walmart | US retail products |
| Yelp | Local business reviews |

## Scenes

Scenes auto-combine the best engines for each use case:

| Scene | Engines | Status |
|-------|---------|--------|
| `news` | Google News + Bing | ✅ Available |
| `academic` | Google Scholar | ✅ Available |
| `jobs` | Google Jobs | ✅ Available |
| `video` | YouTube + Google Videos | ✅ Available |
| `shopping` | Google Shopping + eBay + Walmart | 🔜 Coming in v1.1 |
| `local` | Google Maps + Yelp | 🔜 Coming in v1.1 |
| `travel` | Google Flights | 🔜 Coming in v1.1 |
| `finance` | Google Finance + Yahoo | 🔜 Coming in v1.1 |
| `images` | Google Images | ✅ Available |

## Output formats

`agent-json` (default), `enhanced`, `ranked`, `table`, `raw`.

`agent-json` includes `unified_results`, `response_time_ms`, `search_metadata`, `domain`, `freshness`.

## License

MIT

**[Get API Key →](https://novada.com)**
