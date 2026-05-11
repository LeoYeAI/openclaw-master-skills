# Frequently Asked Questions

## Caching (NEW in v2.7.0!)

### How does caching work?
Search results are automatically cached locally for 1 hour (3600 seconds). When you make the same query again, you get instant results at $0 API cost. The cache key is based on: query text + provider + max_results.

### Where are cached results stored?
In `.cache/` directory inside the skill folder by default. Override with `WSP_CACHE_DIR` environment variable:
```bash
export WSP_CACHE_DIR="/path/to/custom/cache"
```

### How do I see cache stats?
```bash
python3 scripts/search.py --cache-stats
```
This shows total entries, size, oldest/newest entries, and breakdown by provider.

### How do I clear the cache?
```bash
python3 scripts/search.py --clear-cache
```

### Can I change the cache TTL?
Yes! Default is 3600 seconds (1 hour). Set a custom TTL per request:
```bash
python3 scripts/search.py -q "query" --cache-ttl 7200  # 2 hours
```

### How do I skip the cache?
Use `--no-cache` to always fetch fresh results:
```bash
python3 scripts/search.py -q "query" --no-cache
```

### How do I know if a result was cached?
The response includes:
- `"cached": true/false` — whether result came from cache
- `"cache_age_seconds": 1234` — how old the cached result is (when cached)

---

## General

### How does auto-routing decide which provider to use?
Multi-signal analysis scores each provider based on: price patterns, explanation phrases, similarity keywords, URLs, product+brand combos, and query complexity. Highest score wins. Use `--explain-routing` to see the decision breakdown.

### What if it picks the wrong provider?
Override with `-p serper/tavily/exa`. Check `--explain-routing` to understand why it chose differently.

### What does "low confidence" mean?
Query is ambiguous (e.g., "Tesla" could be cars, stock, or company). Falls back to Serper. Results may vary.

### Can I disable a provider?
Yes! In config.json: `"disabled_providers": ["exa"]`

---

## API Keys

### Which API keys do I need?
At minimum ONE key (or SearXNG instance). You can use just Serper, just Tavily, just Exa, just You.com, or just SearXNG. Missing keys = that provider is skipped.

### Where do I get API keys?
- Serper: https://serper.dev (2,500 free queries, no credit card)
- Tavily: https://tavily.com (1,000 free searches/month)
- Exa: https://exa.ai (1,000 free searches/month)
- You.com: https://api.you.com (Limited free tier for testing)
- SearXNG: Self-hosted, no key needed! https://docs.searxng.org/admin/installation.html

### How do I set API keys?
Two options (both auto-load):

**Option A: .env file**
```bash
export SERPER_API_KEY="your-key"
```

**Option B: config.json** (v2.2.1+)
```json
{ "serper": { "api_key": "your-key" } }
```

---

## Routing Details

### How do I know which provider handled my search?
Check `routing.provider` in JSON output, or `[🔍 Searched with: Provider]` in chat responses.

### Why does it sometimes choose Serper for research questions?
If the query has brand/product signals (e.g., "how does Tesla FSD work"), shopping intent may outweigh research intent. Override with `-p tavily`.

### What's the confidence threshold?
Default: 0.3 (30%). Below this = low confidence, uses fallback. Adjustable in config.json.

---

## You.com Specific

### When should I use You.com over other providers?
You.com excels at:
- **RAG applications**: Pre-extracted snippets ready for LLM consumption
- **Real-time information**: Current events, breaking news, status updates
- **Combined sources**: Web + news results in a single API call
- **Summarization tasks**: "What's the latest on...", "Key points about..."

### What's the livecrawl feature?
You.com can fetch full page content on-demand. Use `--livecrawl web` for web results, `--livecrawl news` for news articles, or `--livecrawl all` for both. Content is returned in Markdown format.

### Does You.com include news automatically?
Yes! You.com's intelligent classification automatically includes relevant news results when your query has news intent. You can also use `--include-news` to explicitly enable it.

---

## SearXNG Specific

### Do I need my own SearXNG instance?
Yes! SearXNG is self-hosted. Most public instances disable the JSON API to prevent bot abuse. You need to run your own instance with JSON format enabled. See: https://docs.searxng.org/admin/installation.html

### How do I set up SearXNG?
Docker is the easiest way:
```bash
docker run -d -p 8080:8080 searxng/searxng
```
Then enable JSON in `settings.yml`:
```yaml
search:
  formats:
    - html
    - json
```

### Why am I getting "403 Forbidden"?
The JSON API is disabled on your instance. Enable it in `settings.yml` under `search.formats`.

### What's the API cost for SearXNG?
**$0!** SearXNG is free and open-source. You only pay for hosting (~$5/month VPS). Unlimited queries.

### When should I use SearXNG?
- **Privacy-sensitive queries**: No tracking, no profiling
- **Budget-conscious**: $0 API cost
- **Diverse results**: Aggregates 70+ search engines
- **Self-hosted requirements**: Full control over your search infrastructure
- **Fallback provider**: When paid APIs are rate-limited

### Can I limit which search engines SearXNG uses?
Yes! Use `--engines google,bing,duckduckgo` to specify engines, or configure defaults in `config.json`.

---

## Provider Selection

### Which provider should I use?

| Query Type | Best Provider | Why |
|------------|---------------|-----|
| **Shopping** ("buy laptop", "cheap shoes") | **Serper** | Google Shopping, price comparisons, local stores |
| **Research** ("how does X work?", "explain Y") | **Tavily** | Deep research, academic quality, full-page content |
| **Startups/Papers** ("companies like X", "arxiv papers") | **Exa** | Semantic/neural search, startup discovery |
| **RAG/Real-time** ("summarize latest", "current events") | **You.com** | LLM-ready snippets, combined web+news |
| **Privacy** ("search without tracking") | **SearXNG** | No tracking, multi-source, self-hosted |

**Tip:** Enable auto-routing and let the skill choose automatically! 🎯

### Do I need all 5 providers?
**No!** All providers are optional. You can use:
- **1 provider** (e.g., just Serper for everything)
- **2-3 providers** (e.g., Serper + You.com for most needs)
- **All 5** (maximum flexibility + fallback options)

### How much do the APIs cost?

| Provider | Free Tier | Paid Plan |
|----------|-----------|-----------|
| **Serper** | 2,500 queries/mo | $50/mo (5,000 queries) |
| **Tavily** | 1,000 queries/mo | $150/mo (10,000 queries) |
| **Exa** | 1,000 queries/mo | $1,000/mo (100,000 queries) |
| **You.com** | Limited free | ~$10/mo (varies by usage) |
| **SearXNG** | **FREE** ✅ | Only VPS cost (~$5/mo if self-hosting) |

**Budget tip:** Use SearXNG as primary + others as fallback for specialized queries!

### How private is SearXNG really?

| Setup | Privacy Level |
|-------|---------------|
| **Self-hosted (your VPS)** | ⭐⭐⭐⭐⭐ You control everything |
| **Self-hosted (Docker local)** | ⭐⭐⭐⭐⭐ Fully private |
| **Public instance** | ⭐⭐⭐ Depends on operator's logging policy |

**Best practice:** Self-host if privacy is critical.

### Which provider has the best results?

| Metric | Winner |
|--------|--------|
| **Most accurate for facts** | Serper (Google) |
| **Best for research depth** | Tavily |
| **Best for semantic queries** | Exa |
| **Best for RAG/AI context** | You.com |
| **Most diverse sources** | SearXNG (70+ engines) |
| **Most private** | SearXNG (self-hosted) |

**Recommendation:** Enable multiple providers + auto-routing for best overall experience.

### How does auto-routing work?
The skill analyzes your query for keywords and patterns:

```python
"buy cheap laptop"     → Serper (shopping signals)
"how does AI work?"    → Tavily (research/explanation)
"companies like X"     → Exa (semantic/similar)
"summarize latest news" → You.com (RAG/real-time)
"search privately"     → SearXNG (privacy signals)
```

**Confidence threshold:** Only routes if confidence > 30%. Otherwise uses default provider.

**Override:** Use `-p provider` to force a specific provider.

---

## Production Use

### Can I use this in production?
**Yes!** Web-search-plus is production-ready:
- ✅ Error handling with automatic fallback
- ✅ Rate limit protection
- ✅ Timeout handling (30s per provider)
- ✅ API key security (.env + config.json gitignored)
- ✅ 5 providers for redundancy

**Tip:** Monitor API usage to avoid exceeding free tiers!

### What if I run out of API credits?
1. **Fallback chain:** Other enabled providers automatically take over
2. **Use SearXNG:** Switch to self-hosted (unlimited queries)
3. **Upgrade plan:** Paid tiers have higher limits
4. **Rate limit:** Use `disabled_providers` to skip exhausted APIs temporarily

---

## Updates

### How do I update to the latest version?

**Via ClawHub (recommended):**
```bash
clawhub update web-search-plus --registry "https://www.clawhub.ai" --no-input
```

**Manually:**
```bash
cd /path/to/workspace/skills/web-search-plus/
git pull origin main
python3 scripts/setup.py  # Re-run to configure new features
```

### Where can I report bugs or request features?
- **GitHub Issues:** https://github.com/robbyczgw-cla/web-search-plus/issues
- **ClawHub:** https://www.clawhub.ai/skills/web-search-plus
