---
name: ai-news-daily-brief
description: 从指定信源检索最近24小时AI新闻，完成去重/分类/摘要，生成结构化AI新闻日报。Invoke when user wants AI news digest or daily brief.
---

# AI News Daily Brief

## Overview
This skill generates a structured daily AI news brief by collecting, deduplicating, classifying, and summarizing the most important AI news from the past 24 hours.

It is designed for users who want a fast, high-quality overview of recent AI developments without reading fragmented reports across many sources.

The skill focuses on a fixed set of trusted Chinese AI media sources, global technology media sources, and official first-party AI company sources. It produces a concise but information-dense daily brief containing **10–20 high-value news items**, ranked and organized for easy reading.

This skill is especially useful for:
- AI product managers
- industry researchers
- strategy teams
- enterprise AI practitioners
- users who want a daily AI news digest for tracking trends, competitors, and product updates

---

## Output Language
Unless the user explicitly requests another language, **all output must be written in Simplified Chinese**.

Rules:
1. Section headings, summaries, analysis, takeaways, and explanations must be written in Simplified Chinese.
2. Original article titles may remain in their original language when necessary, but Chinese translation or Chinese summary should be provided.
3. Do not output the final daily brief in English unless the user explicitly asks for English.
4. Keep the writing concise, clear, and suitable for Chinese-speaking professional users.

---

## Supported Sources

### Chinese AI / tech media
- AIBase（入口：https://news.aibase.com/zh/daily）
- 36Kr AI
- 机器之心
- 量子位

### Global media
- Reuters
- **TechCrunch**（新增）
- **The Information**（新增）
- The Verge
- WIRED
- VentureBeat

### Official first-party sources
- Google DeepMind Blog
- OpenAI News
- Anthropic Newsroom
- Anthropic Engineering
- NVIDIA Blog

Do not expand beyond these sources unless explicitly instructed by the user.

---

## Search Language Rules
Use source-appropriate search language to improve recall and precision.

1. For Chinese sources (AIBase, 36Kr AI, 机器之心, 量子位):
   - Search primarily in Chinese.
   - Use Chinese topic phrases and Chinese summaries of events.
   - Preserve important English entity names when helpful, such as OpenAI, NVIDIA, DeepMind, Anthropic, Agent, RAG.

2. For global and official sources (Reuters, The Verge, WIRED, VentureBeat, Google DeepMind Blog, OpenAI News, Anthropic Newsroom, Anthropic Engineering, NVIDIA Blog):
   - Search primarily in English.
   - Use original English company names, product names, and technical terms.
   - When useful, map Chinese user intent into English search queries before searching.

3. For major cross-language events:
   - Try both Chinese and English query variants when necessary.
   - Merge duplicated results across languages into one unified story.

4. Prefer bilingual keyword expansion for important entities and concepts when useful, for example:
   - 英伟达 / NVIDIA
   - 谷歌DeepMind / Google DeepMind
   - 智能体 / Agent
   - 检索增强生成 / RAG
   - 推理模型 / reasoning model

5. Final output language must still follow the output language rules:
   - Default output is Simplified Chinese unless the user explicitly requests another language.

---

## When to Use
Trigger this skill when the user wants:
- an AI news daily brief
- a daily digest of AI industry updates
- a roundup of the latest AI news from the last 24 hours
- a structured summary of important AI developments
- a curated AI news report based on predefined trusted sources

Example user requests:
- “帮我整理今天的AI新闻日报”
- “汇总最近24小时AI圈的重要新闻”
- “给我一份AI行业日报”
- “基于固定信源整理今天的AI动态”
- “Generate an AI news daily brief”

---

## Core Task
Your job is to:
1. Search the supported sources for AI-related news from the last 24 hours.
2. Filter out low-value, weakly related, repetitive, or promotional content.
3. Deduplicate overlapping reports about the same event.
4. Prioritize official first-party announcements when available.
5. Merge repeated coverage of the same event into a single unified news item.
6. Rank the final news items by importance.
7. Output a structured AI news daily brief. Standard target: **8–12 items** (expand to 12–15 when news is dense; reduce to 5–8 when verified sources are limited).

Do not merely list headlines. Extract facts, summarize clearly, and explain why each item matters.

---

## Time Scope
Default time window: **the last 24 hours**.

If an item is slightly older than 24 hours but remains highly relevant in the current cycle and is still a major topic across the supported sources, it may be included sparingly. If so, make that clear in the summary.

---
## Hard Constraints

The skill must strictly follow these constraints:

1. Only use the approved sources listed in `references/sources.md`.
   - Do not use any source outside the approved whitelist unless the user explicitly requests broader coverage.
   - If a story cannot be traced back to an approved source, exclude it.

2. Only include stories whose original publication time can be verified from the source page itself.
   - The skill must open the source page and confirm the explicit original publication date/time.
   - Do not rely only on search snippets, search ranking, summaries, reposts, or secondary mentions.

3. For the daily brief, only include stories published within the last 24 hours.
   - If the original publication time is outside the last 24 hours, exclude the story.
   - If the publication time is ambiguous, missing, approximate, or cannot be confirmed, exclude the story.

4. Never relax the time window, source whitelist, or factual verification rules just to increase the item count.
   - If there are not enough verified high-value stories, return fewer items.

5. Accuracy is more important than completeness.
   - It is acceptable to output only 5–8 items if those are the only verified high-value stories in the time window.

6. If a page is a landing page, archive page, category page, rolling update page, or release notes hub without a clearly verifiable article timestamp, do not use it as a final story source.
   - Only use a specific article or post page with an explicit publication date/time.
   - If the article page cannot be opened by any extraction method (`web_fetch` → `browser.snapshot`), exclude the story. Search snippets are not acceptable as sole evidence of publication time.

7. **Emergency exception — major breaking news**: If a significant AI event is generating widespread coverage but ALL approved sources are unable to verify publication time (e.g., a major model launch breaking on a source not yet in the whitelist), you may include it as a "待核实" item with explicit note that time could not be verified. This exception requires: (a) the event is genuinely major and globally recognized; (b) at least one credible approved source links to or mentions the event; (c) the item is clearly labeled as "待核实". Do not use this exception to circumvent source quality rules for routine news.

---

## Source Access — Tools & Fallback Chain

Different sources require different tools. Use the following recommended strategy:

### Tools Comparison
| Tool | Coverage | Speed | Best for |
|------|----------|-------|----------|
| `web_fetch` | 9/14 sites | Fast | The Verge, Wired, VentureBeat*, NVIDIA Blog, TechCrunch, The Information, Anthropic, OpenAI (article pages), AIBase, 36Kr |
| `agent-browser` | 2/14 sites | Medium | 机器之心, 量子位 (blocked by HTTP/Cloudflare) |
| `tavily` | 5/14 sites | Fast | Reuters, DeepMind Blog, OpenAI (fallback), VentureBeat (primary to avoid 429), 机器之心 (fallback) |

*VentureBeat triggers 429 rate limit via web_fetch; use tavily as primary

*OpenAI main page returns 403, but article-level URLs work via web_fetch

### Recommended Extraction Order
1. **Try `web_fetch`** first (fast, works for 9/14 sites: Western media + OpenAI article pages + AIBase + 36Kr)
2. **Try `agent-browser`** for Chinese sites that block HTTP (机器之心, 量子位)
3. **Try `tavily`** as primary for blocked domains (Reuters, DeepMind) and rate-limited sites (VentureBeat)
4. **Try article-level URLs** — category/homepage blocked doesn't mean all article pages are

### Site-by-Site Strategy
| Source | Primary Tool | Fallback | Notes |
|--------|-------------|----------|-------|
| AIBase | web_fetch | agent-browser | Direct fetch works |
| 36Kr | web_fetch | agent-browser | Homepage anti-bot; try section URLs |
| 机器之心 | agent-browser | tavily | HTTP blocked; browser required |
| 量子位 | agent-browser | tavily | Cloudflare blocks; browser required |
| Reuters | tavily | — | Domain blocked; tavily is the ONLY reliable path |
| TechCrunch | web_fetch | tavily | Direct fetch works |
| The Information | web_fetch | tavily | Direct fetch works |
| The Verge | web_fetch | — | Direct fetch works |
| WIRED | web_fetch | — | Direct fetch works |
| VentureBeat | tavily | agent-browser | web_fetch triggers 429 rate limit |
| DeepMind Blog | tavily | — | Redirect loop; tavily is the ONLY reliable path |
| OpenAI News | web_fetch (article pages) | tavily | Homepage returns 403; article URLs work |
| Anthropic News | web_fetch | agent-browser | Direct fetch works |
| NVIDIA Blog | web_fetch | — | Direct fetch works |

### Strict Rule
If no method can access a source, the story must be excluded. Never pad with low-signal content just to hit a count target.

---

## Inclusion Criteria
Include only news that is directly related to AI and has clear informational value.

Priority topics include:
- model launches and major model updates
- multimodal models, reasoning models, agent systems
- AI products and feature launches
- AI agents, workflow automation, AI office tools
- enterprise AI, knowledge bases, RAG, copilots
- chips, GPUs, inference infrastructure, data centers, compute
- major partnerships, acquisitions, funding, or commercial milestones
- AI policy, regulation, security, safety, copyright, governance
- research breakthroughs with clear product or industry implications

---

## Exclusion Criteria
Do not include:
- weakly related general tech news
- clickbait or headline-only articles
- marketing copy or promotional articles
- pure reposts with no additional information
- speculative opinion pieces without factual basis
- trivial updates with no clear industry significance
- repeated reports of the same event as separate items

If a topic is not clearly AI-related or does not add meaningful signal, exclude it.

---

## Source Priority Rules
When the same event appears across multiple sources, use the following priority order:

1. Official first-party source
2. Reuters
3. TechCrunch / The Information / The Verge / WIRED / VentureBeat
4. 机器之心 / 量子位 / 36Kr AI
5. AIBase

If media interpretation differs from the official announcement, prefer the official source and note that other outlets framed it differently if needed.

---

## Deduplication Rules
Before writing the brief, you must deduplicate and merge overlapping coverage.

Rules:
- Treat the same event covered by multiple outlets as one story.
- Keep the most authoritative and information-rich source as the primary source.
- Record other relevant outlets as supplementary sources.
- Write the news item around the event itself, not around any one outlet’s headline.
- Do not repeat the same story in multiple categories.

---

## Output Requirements
Prefer to keep **8–12 curated news items** in the daily brief.

If there is an unusually dense and high-quality news cycle, the brief may expand to **12–15 items**.

In exceptional cases with very high signal density, the brief may expand up to **20 items**, but only when quality remains consistently high and all items pass verification.

If the number of genuinely high-value and fully verified stories is limited, the brief may be reduced to **5–8 items**. Do not add filler, weakly related updates, approximate matches, or insufficiently verified stories just to reach a target count.

Always prioritize:
- source whitelist compliance
- publication time verification
- factual accuracy
- signal quality
- readability
---

## Output Format

# AI新闻日报（{date}）

## 一、今日最重要的5条AI新闻
按重要性对 5 条新闻进行排序。

每条新闻包含：
- **标题**
- **类别**
- **主来源**
- **发布时间**
- **事件摘要**：100–150字
- **关键看点**：2–3条
- **影响判断**：50–100字，说明为什么值得关注
- **原始链接**
- **补充来源**（如有）

可用类别：
- 模型与产品发布
- Agent与应用落地
- 企业与商业化动态
- 基础设施 / 芯片 / 算力
- 政策 / 监管 / AI安全
- 研究进展与技术趋势

## 二、完整新闻清单（通常为12–15条，高价值不足时可降至8–10条）
按类别分组列出所有入选新闻。

每条包含：
- **标题**
- **来源**
- **时间**
- **一句话摘要**
- **原始链接**

类别顺序：
1. 模型与产品发布
2. Agent与应用落地
3. 企业与商业化动态
4. 基础设施 / 芯片 / 算力
5. 政策 / 监管 / AI安全
6. 研究进展与技术趋势

## 三、日报总结
最后给出：
- **今日最值得关注的3个信号**
- **对AI产品经理最有价值的3条启示**
- **对企业AI / 知识库 / RAG / 办公场景最相关的机会点或风险点**

---

## Writing Style
- Final output must be in Simplified Chinese by default.
- Be concise, factual, and high-signal.
- Do not copy headlines mechanically.
- Compress information and explain it clearly.
- Focus on facts first, then interpretation.
- Avoid hype language and promotional phrasing.
- Explicitly label uncertain claims as “待核实”.
- Keep the brief readable in about 5 minutes.

---

## Quality Checks
Before finalizing the output, verify:
1. Duplicate stories have been merged.
2. Weakly related or low-value items have been removed.
3. Primary sources and supplementary sources are used appropriately, with approved official sources preferred when available.
4. Every story includes a source and link.
5. The top 5 are genuinely ranked by importance.
6. The final brief contains only 10–20 meaningful items.
7. The summaries explain not just what happened, but why it matters.
8. The final output language is Simplified Chinese unless the user explicitly requested another language.

---

## Success Criteria
A good result should:
- save the user time
- surface only the highest-value AI developments
- clearly distinguish original announcements from media reporting
- avoid duplicate noise
- provide usable insight for product, strategy, and industry tracking
- produce a clean, readable Chinese daily brief

---

## Task Scheduling

This skill is designed to be run on a daily schedule. To automate it, set up a cron job that triggers this skill once per day (recommended time: 07:00–09:00 Asia/Shanghai).

**Recommended cron configuration:**
- Schedule: `cron` expression `0 7 * * *` with timezone `Asia/Shanghai`
- Session target: `isolated` (do not run in the main conversation session)
- Delivery: `none` (results are written directly to Tencent Docs; no Feishu push needed)

**Output targets:**
- Daily AI news doc: `https://docs.qq.com/aio/DUEtYTUNWaVNxeXN4`
- AI knowledge base: `https://docs.qq.com/aio/DUG9ocVBZU01sRmtG`

Use the Tencent Docs API (`mcporter call "tencent-docs" "smartcanvas.append_insert_smartcanvas_by_markdown"`) to write results. Do not send Feishu messages from the scheduled session.

---

## Example Invocation
- Generate today’s AI news daily brief.
- Create an AI news digest for the last 24 hours.
- 帮我整理最近24小时的AI新闻日报。
- 基于既定信源生成今日AI新闻简报。