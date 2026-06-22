---
name: novada-search
version: 1.0.8
author: Novada Labs
description: "AI Agent search platform with 9 engines, Google 13 sub-types, vertical scene search, and intelligent auto/multi/extract modes. Designed for LLM and AI agent consumption."
requiredEnv:
  NOVADA_API_KEY:
    description: "Novada Scraper API key (required for search/extract calls)"
permissions:
  filesystem:
    - "./novada_search.py"
    - "./SKILL.md"
    - "./samples/*"
    - "./tests/*"
    - "./skill.json"
    - "./_meta.json"
  network:
    - "https://scraperapi.novada.com"
---

# Novada Search v2.0

> Multi-engine AI search — 9 engines, 13 Google types, 9 vertical scenes, smart agent modes.
> Powered by [Novada Scraper API](https://novada.com).

**Get started in 30 seconds:**

1. Get your free API key → [novada.com](https://novada.com)
2. Set the key via environment **or** CLI: `export NOVADA_API_KEY="your_key"` (or pass `--api-key $NOVADA_API_KEY`)
3. Search: `python3 {baseDir}/novada_search.py --query "coffee Berlin" --scene local`

## Agent-first + Human-friendly (Intelligent Distance)

This skill is optimized for **agents first**, then rendered for **humans**:

- **Agent layer (machine logic)**
  - Use `--format agent-json`.
  - Provides deterministic fields: `engines_used`, `result_counts`, `duplicates_removed`, `unified_results`, `errors`.
  - Best for planning, tool-chaining, re-ranking, and downstream automation.

- **Human layer (readability)**
  - Use `--format enhanced` or `--format ranked`.
  - Shows concise summaries, links, and ranked lists with less structural noise.

**Recommended default contract for agent handoff:**

```bash
python3 {baseDir}/novada_search.py --query "..." --scene news --format agent-json
```

If a human drags this skill to an agent, the agent should be able to clearly answer:
1) what this tool can do,
2) which mode to call (`auto | multi | extract`), and
3) which output format to consume (`agent-json` for logic).

## SDK, MCP & Integrations (v1.0.8)

### Python SDK

```python
from novada_search import NovadaSearch

client = NovadaSearch(api_key="your_key")
result = client.search("coffee Berlin", scene="local")
result = client.search("buy shoes", mode="auto")
result = client.search("AI news", mode="multi", engines=["google", "bing"])
content = client.extract("https://example.com/article")
```

All SDK methods raise `NovadaSearchError` subclasses (not `SystemExit`), so agents can catch and recover.

### MCP Server

```bash
python3 {baseDir}/novada_mcp_server.py
```

Tools: `novada_search`, `novada_extract`. Config example: `mcp.json`.

### LangChain

```python
from integrations.langchain_tool import NovadaSearchTool
tool = NovadaSearchTool(api_key="your_key")
```

### Install via pip

```bash
pip install novada-search
```

### agent-json enhanced fields

- `response_time_ms`
- `search_metadata`
- per-result `domain`
- per-result `freshness`

---

## What’s New (P0) — Best-Answer First for Agents
- **Unified Best Answer**: `agent-json` now includes `unified_results` (top merged results across engines).
- **Dedup that Agents Love**: aggressive URL normalization + multi-engine merging; exposes `duplicates_removed`.
- **Explainable Scoring**: each unified result has `score` + `agreement_count` + `domain` + a short `rationale`.
- **Regression Guardrail**: added `tests/` fixtures so ranking changes don’t silently degrade.

## Troubleshooting (Read This)

- **Novada may return HTTP 200 even on failure**: the real error is in JSON `data.code` / `data.msg`. This CLI hard-checks it and will exit on non-success codes.
- **Cloud/Vercel IPs may be blocked (402)**: validate from your production egress IP before shipping; request server-to-server allowlisting if needed.
- **Local/Shopping default to `fetch_mode=dynamic`**: slower, but higher hit rate for Maps/e-commerce pages.
- **Debugging**: add `--verbose` to see engine/type selection and execution path.

## API Keys & Permissions
- NOVADA_API_KEY is **required**. Either export it (recommended for deployments) or pass `--api-key` per run.
- The CLI no longer scans home directories for secrets; it only checks CLI flag, `NOVADA_API_KEY`, or a local `.env` in the working folder.
- Declared permissions: filesystem (`./*.py`, `./*.md`, `./samples/*`) and network access to `https://scraperapi.novada.com`.

## Real-World Example

**Query:** `--query "dessert Düsseldorf" --scene local`

**Output:**

### 🍰 Düsseldorf TOP 5 Dessert Shops

| Rank | Shop | Rating | Reviews | Address |
|:----:|:-----|:------:|:-------:|:--------|
| 🥇 | [donecake](https://www.google.com/maps/search/?api=1&query=donecake%20Graf-Adolf-Stra%C3%9Fe%2068) | 4.8★ | 3,500 | Graf-Adolf-Straße 68 |
| 🥈 | [SugArt Factory](https://www.google.com/maps/search/?api=1&query=SugArt%20Factory%20Schlo%C3%9Fstra%C3%9Fe%2076-78) | 4.8★ | 423 | Schloßstraße 76-78 |
| 🥉 | [Eiscafe Pia](https://www.google.com/maps/search/?api=1&query=Eiscafe%20Pia%20Kasernenstra%C3%9Fe%201) | 4.7★ | 2,100 | Kasernenstraße 1 |
| 4 | [Unbehaun Eis](https://www.google.com/maps/search/?api=1&query=Unbehaun%20Eis%20Aachener%20Str.%20159) | 4.6★ | 5,000 | Aachener Str. 159 |
| 5 | [Aux Merveilleux de fred](https://www.google.com/maps/search/?api=1&query=Aux%20Merveilleux%20de%20fred%20Kasernenstra%C3%9Fe%2015) | 4.6★ | 626 | Kasernenstraße 15 |

> Click any shop name to open in Google Maps. This is the default `enhanced` output — actionable links, no extra flags needed.

---

## Architecture

```
  Layer 3  │  AI Agent    │  auto · multi · extract
  Layer 2  │  Scenes      │  shopping · local · jobs · academic · video · news · travel · finance · images
  Layer 1  │  Engines     │  google · bing · yahoo · duckduckgo · yandex · youtube · ebay · walmart · yelp
           │              │  + Google: shopping · local · news · scholar · jobs · flights · finance · patents · videos · images · play · lens
```

---

## Layer 1 — Engines

### 9 Engines

| Engine | Strength | Example |
|--------|----------|---------|
| `google` | General + 13 sub-types | `--engine google` |
| `bing` | Web, news | `--engine bing` |
| `yahoo` | Finance | `--engine yahoo` |
| `duckduckgo` | Privacy | `--engine duckduckgo` |
| `yandex` | Russian web | `--engine yandex` |
| `youtube` | Video | `--engine youtube` |
| `ebay` | E-commerce | `--engine ebay` |
| `walmart` | US retail | `--engine walmart` |
| `yelp` | Local reviews | `--engine yelp` |

### 13 Google Sub-Types

Use `--engine google --google-type <type>`:

| Type | What it searches | Type | What it searches |
|------|-----------------|------|-----------------|
| `search` | Web (default) | `shopping` | Products & prices |
| `local` | Google Maps | `news` | Latest headlines |
| `scholar` | Academic papers | `jobs` | Job listings |
| `flights` | Airlines | `finance` | Stocks & markets |
| `videos` | Video content | `images` | Pictures |
| `patents` | IP / patents | `play` | Android apps |
| `lens` | Visual search | | |

```bash
python3 {baseDir}/novada_search.py --query "MacBook Pro M4" --engine google --google-type shopping
python3 {baseDir}/novada_search.py --query "transformer attention" --engine google --google-type scholar
python3 {baseDir}/novada_search.py --query "python developer remote" --engine google --google-type jobs
python3 {baseDir}/novada_search.py --query "SFO to NRT" --engine google --google-type flights
python3 {baseDir}/novada_search.py --query "NVIDIA" --engine google --google-type finance
```

---

## Layer 2 — Scenes

Scenes auto-combine the best engines for each use case. Use `--scene <name>`:

| Scene | Engines combined | Use case | Status |
|-------|-----------------|----------|--------|
| 📰 `news` | Google News + Bing | Multi-source news aggregation | ✅ Available |
| 🎓 `academic` | Google Scholar | Research papers & citations | ✅ Available |
| 💼 `jobs` | Google Jobs | Structured job listings | ✅ Available |
| 🎬 `video` | YouTube + Google Videos | Video tutorials & reviews | ✅ Available |
| 🖼️ `images` | Google Images | Image search | ✅ Available |
| 🛒 `shopping` | Google Shopping + eBay + Walmart | Cross-platform price comparison | 🔜 Coming in v1.1 |
| 📍 `local` | Google Local + Yelp | Local business with ratings & maps | 🔜 Coming in v1.1 |
| ✈️ `travel` | Google Flights | Flight search & pricing | 🔜 Coming in v1.1 |
| 💰 `finance` | Google Finance + Yahoo | Stock data & market info | 🔜 Coming in v1.1 |

```bash
python3 {baseDir}/novada_search.py --query "MacBook Pro" --scene shopping
python3 {baseDir}/novada_search.py --query "ramen Tokyo" --scene local
python3 {baseDir}/novada_search.py --query "react hooks tutorial" --scene video
python3 {baseDir}/novada_search.py --query "AI startup funding" --scene news
```

### Scene Output Example — Shopping

**Query:** `--query "AirPods Pro" --scene shopping --format agent-json`

```json
{
  "query": "AirPods Pro",
  "scene": "shopping",
  "engines_used": ["google:shopping", "ebay", "walmart"],
  "result_counts": { "shopping": 15, "organic": 6 },
  "shopping_results": [
    { "title": "Apple AirPods Pro 2nd Gen", "price": "$189.99", "seller": "Walmart", "rating": 4.8 },
    { "title": "Apple AirPods Pro 2 - New", "price": "$179.00", "seller": "eBay", "rating": 4.9 },
    { "title": "AirPods Pro (2nd generation)", "price": "$249.00", "seller": "Apple", "rating": 4.7 }
  ]
}
```

#### Shopping Scene Enhanced Output (Coming in v1.1)

> ⚠️ Shopping price comparison requires engine-specific data parsing that is being finalized.
> The `price_comparison`, `lowest_price`, and `price_range` fields will be available in v1.1
> when Walmart and eBay result parsing is complete.

#### Local Scene Enhanced Output (Coming in v1.1)

> ⚠️ Local business enrichment (phone, hours, open_now) depends on Google Maps and Yelp
> data parsing that is being finalized for v1.1.

---

## Layer 3 — Agent Modes

Use `--mode <auto|multi|extract>`:

### Auto — Smart intent detection

Analyzes your query and auto-selects the best scene:

```bash
python3 {baseDir}/novada_search.py --query "buy Nike Air Max" --mode auto
#  → detects "shopping" → uses eBay + Walmart + Google Shopping

python3 {baseDir}/novada_search.py --query "best pizza near me" --mode auto
#  → detects "local" → uses Google Maps + Yelp

python3 {baseDir}/novada_search.py --query "latest AI news" --mode auto
#  → detects "news" → uses Google News + Bing
```

Intent keywords (EN/DE/ZH): buy/kaufen, near me/in der nähe, job/stelle, paper/forschung, video/tutorial, news/nachrichten, flight/flug, stock/aktie, image/bild

### Multi — Parallel engines + dedup

Search multiple engines simultaneously, deduplicate by URL:

```bash
python3 {baseDir}/novada_search.py --query "web scraping tools" --mode multi --engines google,bing,duckduckgo

# Colon syntax for Google sub-types
python3 {baseDir}/novada_search.py --query "coffee maker" --mode multi --engines ebay,walmart,google:shopping
```

### Extract — URL content for LLM

Pull clean text from any URL:

```bash
python3 {baseDir}/novada_search.py --url "https://example.com/article" --mode extract
```

### Research — Search + Extract + Merge (Coming in v1.1)

> ⚠️ Research mode depends on the extract API which requires dynamic fetch mode.
> This feature will be fully available in v1.1.

```bash
python3 {baseDir}/novada_search.py --query "AI agent trends 2026" --mode research
```

SDK:
```python
result = client.research("AI agent trends 2026", max_sources=5)
# result includes: unified_results + extracted_content[] + sources_extracted
```

---


## Optional: AI Analysis (Bring Your Own LLM)

This tool focuses on **search + structured results**. If you want additional reasoning, use your own LLM API:

1. Run with structured output:
```bash
python3 {baseDir}/novada_search.py --query "..." --scene news --format agent-json > results.json
```
2. Feed `results.json` into your own LLM prompt (OpenAI/Claude/etc.) for summarization, ranking, or extraction.

> This keeps Novada Search read-only and avoids bundling external AI keys into the skill.


## Output Formats

Default is `enhanced` (clickable links). Override with `--format <name>`:

| Format | Output type | Best for |
|--------|------------|----------|
| `enhanced` **(default)** | Markdown + clickable Maps/website links | Daily use |
| `ranked` | Readable markdown with ratings | Quick overview |
| `agent-json` | Structured JSON for AI agents | LLM integration |
| `table` | Side-by-side comparison table | Comparing options |
| `action-links` | Shell `open` commands | Automation |
| `raw` | Full API response | Debugging |

> See `samples/agent-json-example.json` for a ready-to-copy agent-json payload with `source_engine` + `confidence` fields.

---

## Full Command Reference

```
python3 {baseDir}/novada_search.py
  --query "search terms"                          # required (unless extract mode)
  --engine google|bing|yahoo|duckduckgo|yandex|youtube|ebay|walmart|yelp
  --google-type search|shopping|local|news|scholar|jobs|flights|finance|videos|images|patents|play|lens
  --scene shopping|local|jobs|academic|video|news|travel|finance|images
  --mode auto|multi|extract
  --engines google,bing,ebay                      # for multi mode (colon syntax: google:shopping)
  --url "https://..."                             # for extract mode
  --format enhanced|ranked|agent-json|table|action-links|raw
  --max-results 1-20                              # default: 10
  --fetch-mode static|dynamic                     # static = fast, dynamic = JS pages
```

**Priority:** `--mode auto` overrides everything. `--scene` overrides `--engine`. Direct `--engine` is the fallback.

---

## vs Tavily

| Feature | Novada Search | Tavily |
|---------|:------------:|:------:|
| Search engines | **9** | 1 |
| Google sub-types | **13** | 0 |
| Vertical scenes | **9** | 0 |
| Shopping (eBay+Walmart+Google) | **v1.1** | No |
| Local (Maps+Yelp) | **v1.1** | No |
| Video (YouTube) | **Yes** | No |
| Jobs / Academic / Travel | **Yes** | No |
| Multi-engine parallel | **Yes** | No |
| Auto intent detection | **Yes** | No |
| Content extraction | Yes | Yes |
| Agent JSON output | Yes | Yes |

---

**[Get your API key →](https://novada.com)** · [GitHub](https://github.com/NovadaLabs/novada-search) · Powered by Novada Scraper API v2.0

---

# 中文版｜Novada Search v2.0


## 更新亮点（P0）— 面向 Agent 的“最佳答案优先”
- **统一最佳答案**：`agent-json` 新增 `unified_results`（多引擎合并后的 Top 结果）。
- **强力去重**：URL 归一 + 多引擎聚合；并输出 `duplicates_removed`。
- **可解释评分**：每条 unified 结果带 `score` + `agreement_count` + `domain` + `rationale`（为什么排前）。
- **回归测试**：新增 `tests/` 固件，保证排序逻辑稳定不退化。


> 多引擎 AI 搜索平台——一次调用叠加 9 套主引擎、13 种 Google 类型、9 个垂直场景，并内置 auto / multi / extract 三层 Agent 模式。

## 快速上手
1. 在 [novada.com](https://novada.com) 申请 NOVADA_API_KEY。
2. 用 `export NOVADA_API_KEY="..."` 或运行时 `--api-key $NOVADA_API_KEY` 注入（推荐显式传参，脚本不会再扫描个人目录）。
3. 运行示例：`python3 {baseDir}/novada_search.py --query "coffee Berlin" --scene local`。

## 常见问题｜踩坑
- Novada HTTP 常年 200，真实错误在 JSON `data.code` / `data.msg`，脚本已内建校验。
- 云服务器 / Vercel IP 可能被封（402），上线前先在目标 IP 做 Step 1.6 验证。
- local / shopping 场景默认 `fetch_mode=dynamic`，命中率更高但更慢。
- `--verbose` 可查看 engine/type 选择与节点评估。

## 真实案例
`--query "dessert Düsseldorf" --scene local` 会输出带点击链接的 Top 5 甜品店表格，可直接跳转 Google Maps。

## 架构分层
- **Layer 1 引擎层**：google / bing / yahoo / duckduckgo / yandex / youtube / ebay / walmart / yelp，Google 额外 13 个子类型（shopping/local/news/...）。
- **Layer 2 场景层**：shopping、local、jobs、academic、video、news、travel、finance、images，根据场景组合多引擎并定义合并策略。
- **Layer 3 Agent 模式**：`auto`（意图识别 → 场景）、`multi`（自选引擎并行去重）、`extract`（URL 正文抽取）。

## 指令参考
```
python3 {baseDir}/novada_search.py \
  --query "search" --scene news --format agent-json
python3 {baseDir}/novada_search.py \
  --mode multi --engines google:shopping,ebay,walmart --format table
python3 {baseDir}/novada_search.py \
  --mode extract --url "https://example.com/article"
```

## 输出格式
- `enhanced`：默认 Markdown，附地图/官网快速操作。
- `ranked`：排名 + 摘要。
- `table`：商品/本地商家对照表。
- `agent-json` / `brave`：结构化 JSON 供 LLM 食用（示例见 `samples/agent-json-example.json`）。
- `action-links`：生成 `open "URL"` 命令，方便自动化。
- `raw`：原始 API 回包。

## vs Tavily 对比（精简版）
| 功能 | Novada | Tavily |
|------|--------|--------|
| 搜索引擎数量 | 9 | 1 |
| Google 子类型 | 13 | 0 |
| 垂直场景 | 9 | 0 |
| Shopping（eBay+Walmart+Google） | ✅ | ❌ |
| Local（Maps+Yelp） | ✅ | ❌ |
| 多引擎并行 | ✅ | ❌ |
| Auto intent | ✅ | ❌ |
| Extract API | ✅ | ✅ |

## 实用建议
- 需要稳定输出 → 显式指定 `--scene` 或 `--mode multi`，避免 auto 误判。
- 需要被别的 Agent 调用 → 优先 `--format agent-json`，字段与 Tavily 兼容。
- 线上引用时建议直接传 `--api-key` 或在进程环境里 export（CLI 现仅读取 `--api-key` / `NOVADA_API_KEY` / 当前目录 `.env`）。
- 发布时请确保 registry metadata 与本包的 `requiredEnv.NOVADA_API_KEY`、`permissions` 保持一致（避免扫描器判定 metadata mismatch）。

