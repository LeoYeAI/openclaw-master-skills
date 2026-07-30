---
title: "AI News Daily Brief - Search Rules"
---

# Search Rules and Deduplication Rules

This file defines how the skill should search, filter, merge, and rank AI news items for the daily brief.

The goal is to maximize signal quality, reduce duplication, and improve consistency.

---

## 1. Search Scope

The default time range is the last 24 hours.

The skill should search only within the approved sources listed in `sources.md`.

Do not expand beyond the approved source list unless the user explicitly requests broader coverage.

---

## 2. Search Language Rules

### For Chinese sources
Applicable sources:
- AIBase
- 36Kr AI
- 机器之心
- 量子位

Rules:
1. Search primarily in Chinese.
2. Use Chinese topic phrases, event summaries, and translated subject terms.
3. Preserve important English company names, product names, and technical terms when helpful, such as:
   - OpenAI
   - Anthropic
   - NVIDIA
   - Google DeepMind
   - Agent
   - RAG
   - API
4. Prefer Chinese search phrasing for business, industry, and product news.
5. When a topic is highly cross-border, use bilingual keyword expansion as needed.

Examples:
- OpenAI 发布 新模型
- 英伟达 AI 芯片 推理
- 谷歌 DeepMind 多模态 模型
- 智能体 办公 自动化
- 企业 AI 知识库 RAG

### For global and official sources
Applicable sources:
- Reuters
- TechCrunch
- The Information
- The Verge
- WIRED
- VentureBeat
- Google DeepMind Blog
- OpenAI News
- Anthropic Newsroom
- Anthropic Engineering
- NVIDIA Blog

Rules:
1. Search primarily in English.
2. Use original English names for companies, products, models, APIs, and technical terms.
3. Map Chinese user intent into English search queries when needed.
4. Use domain-specific technical wording where appropriate.

Examples:
- OpenAI new model release
- Anthropic Claude enterprise update
- NVIDIA inference chip launch
- AI agent workflow automation
- RAG enterprise deployment
- DeepMind multimodal model

### Cross-language event rules
1. For major stories with likely coverage in both Chinese and English sources, try both Chinese and English query variants.
2. Merge duplicated results across languages into one event.
3. Prefer the most authoritative primary source, but use cross-language coverage for context if helpful.

---

## 3. Source Page Extraction — Fallback Chain

When verifying publication time or extracting article content, use the following fallback chain:

**Chain: `web_fetch` → `agent-browser` → `tavily`**

1. **Primary**: `web_fetch` tool — fast, works for most Western sites (The Verge, Wired, VentureBeat, NVIDIA Blog, TechCrunch, Anthropic, OpenAI article pages, AIBase)
2. **If web_fetch fails or blocked**: `agent-browser` tool — works better for Chinese sites (机器之心, 量子位, 36kr)
3. **If both fail (Reuters, DeepMind)**: `tavily` — use Tavily search to find the article and verify recency

**Important notes:**
- Reuters (reuters.com) is network-level blocked — use `tavily` with `site:reuters.com` query
- DeepMind Blog — domain returns redirect loop via curl — use `tavily` with `site:deepmind.google` query
- OpenAI main page returns 403 but article-level URLs typically work via web_fetch
- 机器之心 sometimes refuses direct connection — try agent-browser or tavily fallback
- 36Kr homepage anti-bot — try section/tag URLs instead of homepage

**Strict rule**: If the article page cannot be opened by any method, the story must be excluded. Search snippets are not acceptable as sole evidence of publication time.

---

## 4. Inclusion Rules

Include only stories that are directly related to AI and have real informational value.

Priority topics:
- model launches and major upgrades
- multimodal models, reasoning models, agent systems
- API and platform changes
- AI products and major feature releases
- AI agents and workflow automation
- enterprise AI, knowledge bases, RAG, copilots
- chips, GPUs, inference systems, data centers, compute
- major partnerships, acquisitions, funding, and business strategy moves
- policy, regulation, safety, copyright, governance
- research with clear industry or product relevance

---

## 5. Exclusion Rules

Do not include:
- weakly related general tech news
- vague opinion pieces without concrete developments
- promotional or marketing-heavy content
- reposts with no added information
- trivial updates with little industry significance
- rumor-only content without credible basis
- duplicate stories already represented elsewhere in the brief

If relevance or value is unclear, exclude the item.

---

## 6. Deduplication Rules

Before drafting the brief, deduplicate all overlapping reports.

Rules:
1. Treat all coverage of the same event as one story.
2. Use the most authoritative and information-rich source as the primary source.
3. Record other strong sources as supplementary sources.
4. Merge repeated media coverage into one unified event summary.
5. Do not repeat the same event in multiple categories.
6. Do not keep separate entries just because different outlets use different headlines.

Example:
If OpenAI announces a new feature and Reuters, TechCrunch, The Verge, and 36Kr all report it:
- Primary source: OpenAI News
- Supplementary sources: Reuters, TechCrunch, The Verge, 36Kr
- Final output: one merged story

---

## 7. Source Priority Rules

When multiple sources cover the same event, use this priority order:

1. Official first-party source
2. Reuters
3. TechCrunch / The Information / The Verge / WIRED / VentureBeat
4. 机器之心 / 量子位 / 36Kr AI
5. AIBase

If the official source and media framing differ:
- prefer the official source for factual claims
- use media coverage only for interpretation or additional context

---

## 8. Ranking Rules

The skill should rank stories by importance, not by publication time alone.

Signals that increase importance:
- official product or model release
- major API or capability update
- broad market or industry impact
- strategic funding, acquisition, or partnership
- infrastructure or compute implications
- regulatory or policy significance
- direct relevance to enterprise AI, product strategy, or competitive dynamics

Signals that lower importance:
- minor feature tweaks
- repetitive commentary
- weak evidence
- shallow repost-style coverage
- stories with low product or industry implications

---

## 9. Target Volume Rules

**Standard: 8–12 items**. This is the default target for a normal news day.

**Expand to 12–15** when the news cycle is unusually dense and high-quality.

**Exceptional max: 20 items** — only when quality remains consistently high across all items and the user has not requested brevity.

**Reduce to 5–8** when genuinely verified high-value stories are limited. This is normal and acceptable — do not pad with filler.

**Note**: The section "一、今日最重要的5条" always shows exactly 5 items (or fewer if verified items are fewer than 5). The section "二、完整新闻清单" reflects the actual total count.

Do not add filler or weakly related stories just to meet a target count.

---

## 10. Final Review Rules

Before final output, verify:
1. duplicates were merged
2. all items are clearly AI-related
3. official and media sources are clearly distinguished
4. each item has a valid source reference and publication time
5. ranking reflects true importance
6. weak content has been filtered out
7. summaries explain why the story matters
8. final output language is Simplified Chinese unless the user explicitly requests another language


---

## 11. Publication Time Verification Rules

Before including any story in the daily brief, the skill must verify the original publication time from the source page itself.

**Required procedure:**
1. Open the article URL using the extraction fallback chain (see Section 3).
2. Locate the explicit publication date/time on the rendered page.
3. Normalize the date/time to a consistent reference timezone (UTC+8 for Chinese context, UTC for English sources).
4. Check whether the story falls within the last 24 hours.
5. Only then may the story be included in the final brief.

**Strict rules:**
- Do not use search result snippets alone as proof of recency.
- Do not infer recency from topic relevance, URL patterns, page ordering, or "latest" labels.
- Do not treat "recent", "updated", "this month", or "March 2026" as sufficient evidence.
- If the publication date/time cannot be confirmed precisely, exclude the story.
- If the page is an evergreen page, archive page, tag page, topic page, or rolling update page without a clear timestamp for the specific story, exclude it unless a specific dated article page is opened and verified.

**Examples of items to exclude:**
- old articles resurfacing in search
- archive pages and topic hubs
- release-note hubs without clear post-level timing
- pages labeled only with approximate time such as "recently"

---

## 12. Tavily Search — Special Fallback for Blocked Sites

For sites that cannot be accessed directly (Reuters, DeepMind), use **Tavily search** as the primary discovery and verification tool.

### Tavily Setup
- API key is configured in gateway config under `env.TAVILY_API_KEY`
- Tavily is invoked via the skill's search script:
  ```bash
  node {baseDir}/scripts/search.mjs "site:reuters.com AI" -n 5 --topic news --days 1
  node {baseDir}/scripts/search.mjs "site:deepmind.google AI" -n 5 --topic news --days 1
  ```

### Tavily Search Commands
```bash
# Reuters AI news from last 24h
node {baseDir}/scripts/search.mjs "site:reuters.com artificial intelligence" -n 5 --topic news --days 1

# DeepMind blog posts from last 7 days
node {baseDir}/scripts/search.mjs "site:deepmind.google" -n 5 --topic news --days 7

# OpenAI news from last 24h
node {baseDir}/scripts/search.mjs "site:openai.com" -n 5 --topic news --days 1

# NVIDIA blog from last 7 days
node {baseDir}/scripts/search.mjs "site:nvidia.com/blog" -n 5 --topic news --days 7
```

### Site-by-Site Access Summary
| Source | Primary | Fallback |
|--------|---------|----------|
| AIBase | web_fetch | agent-browser |
| 36Kr | agent-browser | web_fetch |
| 机器之心 | agent-browser | Tavily search |
| 量子位 | agent-browser | web_fetch |
| **Reuters** | **Tavily search** | — |
| TechCrunch | web_fetch | Tavily search |
| The Information | web_fetch | Tavily search |
| The Verge | web_fetch | — |
| WIRED | web_fetch | — |
| VentureBeat | web_fetch | agent-browser |
| **DeepMind Blog** | **Tavily search** | — |
| OpenAI News | web_fetch | Tavily search |
| Anthropic News | web_fetch | agent-browser |
| NVIDIA Blog | web_fetch | Tavily search |
