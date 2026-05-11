# Changelog - Web Search Plus

## [2.8.6] - 2026-03-03

### Changed
- Documented Perplexity Sonar Pro usage and refreshed release docs.


## [2.8.5] - 2026-02-20

### ✨ Feature: Perplexity freshness filter

- Added `freshness` parameter to Perplexity provider (`day`, `week`, `month`, `year`)
- Maps to Perplexity's native `search_recency_filter` parameter
- Example: `python3 scripts/search.py -p perplexity -q "latest AI news" --freshness day`
- Consistent with freshness support in Serper and Brave providers

## [2.8.4] - 2026-02-20

### 🔒 Security Fix: SSRF protection in setup wizard

- **Fixed:** `setup.py` SearXNG connection test had no SSRF protection (unlike `search.py`)
- **Before:** Operator could be tricked into probing internal networks during setup
- **After:** Same IP validation as `search.py` — blocks private IPs, cloud metadata, loopback
- **Credit:** ClawHub security scanner

## [2.8.3] - 2026-02-20

### 🐛 Critical Fix: Perplexity results empty

- **Fixed:** Perplexity provider returned 0 results because the AI-synthesized answer wasn't mapped into the results array
- **Before:** Only extracted URLs from the answer text were returned as results (often 0)
- **After:** The full answer is now the primary result (title, snippet with cleaned text), extracted source URLs follow as additional results
- **Impact:** Perplexity queries now always return at least 1 result with the synthesized answer

## [2.8.0] - 2026-02-20

### 🆕 New Provider: Perplexity (AI-Synthesized Answers)

Added Perplexity as the 6th search provider via Kilo Gateway — the first provider that returns **direct answers with citations** instead of just links:

#### Features
- **AI-Synthesized Answers**: Get a complete answer, not a list of links
- **Inline Citations**: Every claim backed by `[1][2][3]` source references
- **Real-Time Web Search**: Perplexity searches the web live, reads pages, and summarizes
- **Zero Extra Config**: Works through Kilo Gateway with your existing `KILOCODE_API_KEY`
- **Model**: `perplexity/sonar-pro` (best quality, supports complex queries)

#### Auto-Routing Signals
New direct-answer intent detection routes to Perplexity for:
- Status queries: "status of", "current state of", "what is the status"
- Local info: "events in [city]", "things to do in", "what's happening in"
- Direct questions: "what is", "who is", "when did", "how many"
- Current affairs: "this week", "this weekend", "right now", "today"

#### Usage Examples
```bash
# Auto-routed
python3 scripts/search.py -q "events in Graz Austria this weekend"  # → Perplexity
python3 scripts/search.py -q "what is the current status of Ethereum"  # → Perplexity

# Explicit
python3 scripts/search.py -p perplexity -q "latest AI regulation news"
```

#### Configuration
Requires `KILOCODE_API_KEY` environment variable (Kilo Gateway account).
No additional API key needed — Perplexity is accessed through Kilo's unified API.

```bash
export KILOCODE_API_KEY="your-kilo-key"
```

### 🔧 Routing Rebalance

Major overhaul of the auto-routing confidence scoring to fix Serper dominance:

#### Problem
Serper (Google) was winning ~90% of queries due to:
- High recency multiplier boosting Serper on any query with dates/years
- Default provider priority placing Serper first in ties
- Research and discovery signals not strong enough to override

#### Changes
- **Lowered Serper recency multiplier** — date mentions no longer auto-route to Google
- **Strengthened research signals** for Tavily:
  - Added: "status of", "what happened with", "how does X compare"
  - Boosted weights for comparison patterns (4.0 → 5.0)
- **Strengthened discovery signals** for Exa:
  - Added: "events in", "things to do in", "startups similar to"
  - Boosted weights for local discovery patterns
- **Updated provider priority order**: `tavily → exa → perplexity → serper → you → searxng`
  - Serper moved from 1st to 4th in tie-breaking
  - Research/discovery providers now win on ambiguous queries

#### Routing Test Results

| Query | Before | After | ✓ |
|-------|--------|-------|---|
| "latest OpenClaw version Feb 2026" | Serper | Serper | ✅ |
| "Ethereum Pectra upgrade status" | Serper | **Tavily** | ✅ |
| "events in Graz this weekend" | Serper | **Perplexity** | ✅ |
| "compare SearXNG vs Brave for AI agents" | Serper | **Tavily** | ✅ |
| "Sam Altman OpenAI news this week" | Serper | Serper | ✅ |
| "find startups similar to Kilo Code" | Serper | **Exa** | ✅ |

### 📊 Updated Provider Comparison

| Feature | Serper | Tavily | Exa | Perplexity | You.com | SearXNG |
|---------|:------:|:------:|:---:|:----------:|:-------:|:-------:|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡⚡ | ⚡ |
| Direct Answers | ✗ | ✗ | ✗ | ✓✓ | ✗ | ✗ |
| Citations | ✗ | ✗ | ✗ | ✓ | ✗ | ✗ |
| Local Events | ✓ | ✗ | ✓ | ✓✓ | ✗ | ✓ |
| Research | ✗ | ✓✓ | ✓ | ✓ | ✓ | ✗ |
| Discovery | ✗ | ✗ | ✓✓ | ✗ | ✗ | ✗ |
| Self-Hosted | ✗ | ✗ | ✗ | ✗ | ✗ | ✓ |

## [2.7.0] - 2026-02-14

### ✨ Added
- Provider cooldown tracking in `.cache/provider_health.json`
- Exponential cooldown on provider failures: **1m → 5m → 25m → 1h (cap)**
- Retry strategy for transient failures (timeout, 429, 503): up to 2 retries with backoff **1s → 3s → 9s**
- Smarter cache keys hashed from full request context (query/provider/max_results + locale, freshness, time_range, topic, search_engines, include_news, and related params)
- Cross-provider result deduplication by normalized URL during fallback merge

### 🔧 Changed
- Cooldown providers are skipped in routing while their cooldown is active
- Provider health is reset automatically after successful requests
- Fallback output now includes dedup metadata:
  - `deduplicated: true|false`
  - `metadata.dedup_count`


## [2.6.5] - 2026-02-11

### 🆕 File-Based Result Caching

Added local caching to save API costs on repeated searches:

#### Features
- **Automatic Caching**: Search results cached locally by default
- **1-Hour TTL**: Results expire after 3600 seconds (configurable)
- **Cache Indicators**: Response includes `cached: true/false` and `cache_age_seconds`
- **Zero-Cost Repeats**: Cached requests don't hit APIs

#### New CLI Options
- `--cache-ttl SECONDS` — Custom cache TTL (default: 3600)
- `--no-cache` — Bypass cache, always fetch fresh
- `--clear-cache` — Delete all cached results
- `--cache-stats` — Show cache statistics (entries, size, age)

#### Configuration
- **Cache directory**: `.cache/` in skill directory
- **Environment variable**: `WSP_CACHE_DIR` to override location
- **Cache key**: Based on query + provider + max_results (SHA256)

#### Usage Examples
```bash
# First request costs API credits
python3 scripts/search.py -q "AI startups"

# Second request is FREE (uses cache)
python3 scripts/search.py -q "AI startups"

# Force fresh results
python3 scripts/search.py -q "AI startups" --no-cache

# View stats
python3 scripts/search.py --cache-stats

# Clear everything
python3 scripts/search.py --clear-cache
```

#### Technical Details
- Cache files: JSON with metadata (_cache_timestamp, _cache_key, etc.)
- Automatic cleanup of expired entries on access
- Graceful handling of corrupted cache files

## [2.6.1] - 2026-02-04

- Privacy cleanup: removed hardcoded paths and personal info from docs

## [2.5.0] - 2026-02-03

### 🆕 New Provider: SearXNG (Privacy-First Meta-Search)

Added SearXNG as the 5th search provider, focused on privacy and self-hosted search:

#### Features
- **Privacy-Preserving**: No tracking, no profiling — your searches stay private
- **Multi-Source Aggregation**: Queries 70+ upstream engines (Google, Bing, DuckDuckGo, etc.)
- **$0 API Cost**: Self-hosted = unlimited queries with no API fees
- **Diverse Results**: Get perspectives from multiple search engines in one query
- **Customizable**: Choose which engines to use, set SafeSearch levels, language preferences

#### Auto-Routing Signals
New privacy/multi-source intent detection routes to SearXNG for:
- Privacy queries: "private", "anonymous", "without tracking", "no tracking"
- Multi-source: "aggregate results", "multiple sources", "diverse perspectives"
- Budget/free: "free search", "no api cost", "self-hosted search"
- German: "privat", "anonym", "ohne tracking", "verschiedene quellen"

#### Usage Examples
```bash
# Auto-routed
python3 scripts/search.py -q "search privately without tracking"  # → SearXNG

# Explicit
python3 scripts/search.py -p searxng -q "linux distros"
python3 scripts/search.py -p searxng -q "AI news" --engines "google,bing,duckduckgo"
python3 scripts/search.py -p searxng -q "privacy tools" --searxng-safesearch 2
```

#### Configuration
```json
{
  "searxng": {
    "instance_url": "https://your-instance.example.com",
    "safesearch": 0,
    "engines": null,
    "language": "en"
  }
}
```

#### Setup
SearXNG requires a self-hosted instance with JSON format enabled:
```bash
# Docker setup (5 minutes)
docker run -d -p 8080:8080 searxng/searxng

# Enable JSON in settings.yml:
# search:
#   formats: [html, json]

# Set instance URL
export SEARXNG_INSTANCE_URL="http://localhost:8080"
```

See: https://docs.searxng.org/admin/installation.html

### 📊 Updated Provider Comparison

| Feature | Serper | Tavily | Exa | You.com | SearXNG |
|---------|:------:|:------:|:---:|:-------:|:-------:|
| Privacy-First | ✗ | ✗ | ✗ | ✗ | ✓✓ |
| Self-Hosted | ✗ | ✗ | ✗ | ✗ | ✓ |
| API Cost | $$ | $$ | $$ | $ | **FREE** |
| Multi-Engine | ✗ | ✗ | ✗ | ✗ | ✓ (70+) |

### 🔧 Technical Changes

- Added `search_searxng()` function with full error handling
- Added `PRIVACY_SIGNALS` to QueryAnalyzer for auto-routing
- Updated setup wizard with SearXNG option (instance URL validation)
- Updated config.example.json with searxng section
- New CLI args: `--searxng-url`, `--searxng-safesearch`, `--engines`, `--categories`

---

## [2.4.4] - 2026-02-03

### 📝 Documentation: Provider Count Fix

- **Fixed:** "You can use 1, 2, or all 3" → "1, 2, 3, or all 4" (we have 4 providers now!)
- **Impact:** Accurate documentation for setup wizard

## [2.4.3] - 2026-02-03

### 📝 Documentation: Updated README

- **Added:** "NEW in v2.4.2" badge for You.com in SKILL.md
- **Impact:** ClawHub README now properly highlights You.com as new feature

## [2.4.2] - 2026-02-03

### 🐛 Critical Fix: You.com API Configuration

- **Fixed:** Incorrect hostname (`api.ydc-index.io` → `ydc-index.io`)
- **Fixed:** Incorrect header name (`X-API-Key` → `X-API-KEY` uppercase)
- **Impact:** You.com now works correctly - was giving 403 Forbidden before
- **Status:** ✅ Fully tested and working

## [2.4.1] - 2026-02-03

### 🐛 Bugfix: You.com URL Encoding

- **Fixed:** URL encoding for You.com queries - spaces and special characters now properly encoded
- **Impact:** Queries with spaces (e.g., "OpenClaw AI framework") work correctly now
- **Technical:** Added `urllib.parse.quote` for parameter encoding

## [2.4.0] - 2026-02-03

### 🆕 New Provider: You.com

Added You.com as the 4th search provider, optimized for RAG applications and real-time information:

#### Features
- **LLM-Ready Snippets**: Pre-extracted, query-aware text excerpts perfect for feeding into AI models
- **Unified Web + News**: Get both web pages and news articles in a single API call
- **Live Crawling**: Fetch full page content on-demand in Markdown format (`--livecrawl`)
- **Automatic News Classification**: Intelligently includes news results based on query intent
- **Freshness Controls**: Filter by recency (day, week, month, year, or date range)
- **SafeSearch Support**: Content filtering (off, moderate, strict)

#### Auto-Routing Signals
New RAG/Real-time intent detection routes to You.com for:
- RAG context queries: "summarize", "key points", "tldr", "context for"
- Real-time info: "latest news", "current status", "right now", "what's happening"
- Information synthesis: "updates on", "situation", "main takeaways"

#### Usage Examples
```bash
# Auto-routed
python3 scripts/search.py -q "summarize key points about AI regulation"  # → You.com

# Explicit
python3 scripts/search.py -p you -q "climate change" --livecrawl all
python3 scripts/search.py -p you -q "tech news" --freshness week
```

#### Configuration
```json
{
  "you": {
    "country": "US",
    "language": "en",
    "safesearch": "moderate",
    "include_news": true
  }
}
```

#### API Key Setup
```bash
export YOU_API_KEY="your-key"  # Get from https://api.you.com
```

### 📊 Updated Provider Comparison

| Feature | Serper | Tavily | Exa | You.com |
|---------|:------:|:------:|:---:|:-------:|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡⚡ |
| News Integration | ✓ | ✗ | ✗ | ✓ |
| RAG-Optimized | ✗ | ✓ | ✗ | ✓✓ |
| Full Page Content | ✗ | ✓ | ✓ | ✓ |

---

## [2.1.5] - 2026-01-27

### 📝 Documentation

- Added warning about NOT using Tavily/Serper/Exa in core OpenClaw config
- Core OpenClaw only supports `brave` as the built-in provider
- This skill's providers must be used via environment variables and scripts, not `openclaw.json`

## [2.1.0] - 2026-01-23

### 🧠 Intelligent Multi-Signal Routing

Completely overhauled auto-routing with sophisticated query analysis:

#### Intent Classification
- **Shopping Intent**: Detects price patterns ("how much", "cost of"), purchase signals ("buy", "order"), deal keywords, and product+brand combinations
- **Research Intent**: Identifies explanation patterns ("how does", "why does"), analysis signals ("pros and cons", "compare"), learning keywords, and complex multi-clause queries
- **Discovery Intent**: Recognizes similarity patterns ("similar to", "alternatives"), company discovery signals, URL/domain detection, and academic patterns

#### Linguistic Pattern Detection
- "How much" / "price of" → Shopping (Serper)
- "How does" / "Why does" / "Explain" → Research (Tavily)
- "Companies like" / "Similar to" / "Alternatives" → Discovery (Exa)
- Product + Brand name combos → Shopping (Serper)
- URLs and domains in query → Similar search (Exa)

#### Query Analysis Features
- **Complexity scoring**: Long, multi-clause queries get routed to research providers
- **URL detection**: Automatic detection of URLs/domains triggers Exa similar search
- **Brand recognition**: Tech brands (Apple, Samsung, Sony, etc.) with product terms → shopping
- **Recency signals**: "latest", "2026", "breaking" boost news mode

#### Confidence Scoring
- **HIGH (70-100%)**: Strong signal match, very reliable routing
- **MEDIUM (40-69%)**: Good match, should work well
- **LOW (0-39%)**: Ambiguous query, using fallback provider
- Confidence based on absolute signal strength + relative margin over alternatives

#### Enhanced Debug Mode
```bash
python3 scripts/search.py --explain-routing -q "your query"
```

Now shows:
- Routing decision with confidence level
- All provider scores
- Top matched signals with weights
- Query analysis (complexity, URL detection, recency focus)
- All matched patterns per provider

### 🔧 Technical Changes

#### QueryAnalyzer Class
New `QueryAnalyzer` class with:
- `SHOPPING_SIGNALS`: 25+ weighted patterns for shopping intent
- `RESEARCH_SIGNALS`: 30+ weighted patterns for research intent
- `DISCOVERY_SIGNALS`: 20+ weighted patterns for discovery intent
- `LOCAL_NEWS_SIGNALS`: 25+ patterns for local/news queries
- `BRAND_PATTERNS`: Tech brand detection regex

#### Signal Weighting
- Multi-word phrases get higher weights (e.g., "how much" = 4.0 vs "price" = 3.0)
- Strong signals: price patterns (4.0), similarity patterns (5.0), URLs (5.0)
- Medium signals: product terms (2.5), learning keywords (2.5)
- Bonus scoring: Product+brand combo (+3.0), complex query (+2.5)

#### Improved Output Format
```json
{
  "routing": {
    "auto_routed": true,
    "provider": "serper",
    "confidence": 0.78,
    "confidence_level": "high",
    "reason": "high_confidence_match",
    "top_signals": [{"matched": "price", "weight": 3.0}],
    "scores": {"serper": 7.0, "tavily": 0.0, "exa": 0.0}
  }
}
```

### 📚 Documentation Updates

- **SKILL.md**: Complete rewrite with signal tables and confidence scoring guide
- **README.md**: Updated with intelligent routing examples and confidence levels
- **FAQ**: Updated to explain multi-signal analysis

### 🧪 Test Results

| Query | Provider | Confidence | Signals |
|-------|----------|------------|---------|
| "how much does iPhone 16 cost" | Serper | 68% | "how much", brand+product |
| "how does quantum entanglement work" | Tavily | 86% HIGH | "how does", "what are", "implications" |
| "startups similar to Notion" | Exa | 76% HIGH | "similar to", "Series A" |
| "companies like stripe.com" | Exa | 100% HIGH | URL detected, "companies like" |
| "MacBook Pro M3 specs review" | Serper | 70% HIGH | brand+product, "specs", "review" |
| "Tesla" | Serper | 0% LOW | No signals (fallback) |
| "arxiv papers on transformers" | Exa | 58% | "arxiv" |
| "latest AI news 2026" | Serper | 77% HIGH | "latest", "news", "2026" |

---

## [2.0.0] - 2026-01-23

### 🎉 Major Features

#### Smart Auto-Routing
- **Automatic provider selection** based on query analysis
- No need to manually choose provider - just search!
- Intelligent keyword matching for routing decisions
- Pattern detection for query types (shopping, research, discovery)
- Scoring system for provider selection

#### User Configuration
- **config.json**: Full control over auto-routing behavior
- **Configurable keyword mappings**: Add your own routing keywords
- **Provider priority**: Set tie-breaker order
- **Disable providers**: Turn off providers you don't have API keys for
- **Enable/disable auto-routing**: Opt-in or opt-out as needed

#### Debugging Tools
- **--explain-routing** flag: See exactly why a provider was selected
- Detailed routing metadata in JSON responses
- Shows matched keywords and routing scores

### 📚 Documentation

- **README.md**: Complete auto-routing guide with examples
- **SKILL.md**: Detailed routing logic and configuration reference
- **FAQ section**: Common questions about auto-routing
- **Configuration examples**: Pre-built configs for common use cases

---

## [1.0.x] - Initial Release

- Multi-provider search: Serper, Tavily, Exa
- Manual provider selection with `-p` flag
- Unified JSON output format
- Provider-specific options (--depth, --category, --similar-url, etc.)
- Domain filtering for Tavily/Exa
- Date filtering for Exa
