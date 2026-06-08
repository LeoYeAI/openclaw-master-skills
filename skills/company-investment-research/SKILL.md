---
name: company-investment-research
description: "Structured, multi-dimensional company investment research framework for AI agents and human analysts. Provides a 10-part checklist (moat, tech, market, customers, growth, financials, geography, governance, valuation, recommendation) to turn scattered info into a consistent, high-quality investment memo. | 面向 AI Agent 与人工分析师的公司投研框架，用 10 大维度系统梳理商业模式、护城河、成长与估值，快速产出结构化投研报告。"
---

# Company Investment Research / 公司投资研究框架

This skill provides a systematic framework for conducting comprehensive investment research and due diligence on companies. It structures analysis across 10 critical dimensions to support informed investment decisions.

本技能为公司基本面研究提供一套**结构化投研框架**，覆盖 10 个关键维度，帮助你从零开始梳理一家公司的商业模式、竞争力、增长与估值，并最终形成一份有逻辑的投资结论。

---

## When to Use / 适用场景

Use this skill when you need to:

- Evaluate a company as a potential **investment** (public or late-stage private)
- Understand a company's **competitive advantages and moat** vs peers
- Produce a **structured investment memo** instead of scattered notes
- Compare **two or more companies** in the same sector on a consistent framework

适合在以下场景使用：

- 对某家公司做**系统性投研/估值评估**（上市公司或准上市公司）
- 想明白它相对于同行的**护城河与竞争地位**
- 需要输出一份结构清晰的**投研报告/投资备忘录**
- 在同一行业内对比多家公司，希望有**统一的分析模板**

---

## Quick Usage Examples / 快速使用示例

### 1. Single-company deep dive / 单公司深度研究

> "Analyze NVIDIA (NVDA) as an investment using the company-investment-research framework. Follow all 10 dimensions and end with a clear BUY/HOLD/SELL view, including key risks."

> 「请基于 `company-investment-research` 投研框架，系统分析英伟达（NVIDIA, NVDA）的投资价值，按 10 个维度展开，最后给出 BUY/HOLD/SELL 判断，并列出关键风险。」

### 2. Compare two companies in the same sector / 同行业公司对比

> "Using the company-investment-research skill, compare NVIDIA vs AMD as AI infrastructure investments. Highlight differences in moat, growth drivers, and valuation, then state which one looks more attractive on a 3–5 year horizon and why."

> 「使用该投研框架对比分析 NVIDIA 与 AMD 作为 AI 基础设施投资标的的优劣，从护城河、成长驱动、估值三方面重点展开，并给出未来 3–5 年哪个更具吸引力及原因。」

### 3. Rapid pre-screening / 快速预筛选

> "Run a lightweight version of the company-investment-research framework on Snowflake. Focus on competitive positioning, growth drivers, and valuation to decide whether it deserves full deep-dive research."

> 「对 Snowflake 做一版简化版投研：重点看竞争地位、成长驱动和估值，判断是否值得投入时间做完整深度研究。」

### 4. Memo generation for internal discussion / 生成内部讨论用 Memo

> "Create a 2–3 page investment memo for Tesla using the company-investment-research structure. The target audience is an investment committee; keep language concise but include key numbers and scenarios (base/bull/bear)."

> 「按照本框架，为特斯拉生成一份 2–3 页的投资备忘录，供投委会讨论使用：语言简洁，但需包含核心数据与基础/乐观/悲观三种情景。」

---

## Industry Templates / 行业模板示例

Below are **add-on checklists** for specific industries. Use them on top of the 10 core dimensions.

下面是针对特定行业的**额外检查项**，在 10 大通用维度基础上叠加使用即可。

### A. Internet Platforms (Consumer Internet) / 互联网平台

**Typical businesses / 典型业务：** 内容平台、电商、社交、短视频、本地生活等。

**Extra focus areas / 额外关注点：**

- **User metrics / 用户指标**  
  - MAU/DAU 走势、渗透率、区域分布  
  - 用户结构（核心用户 vs 长尾用户）

- **Engagement & retention / 使用粘性与留存**  
  - 人均使用时长、留存（7 日 / 30 日 / 12 个月）  
  - 用户生命周期路径（拉新→激活→留存→复购/付费）

- **Monetization model / 变现模式**  
  - 广告 / 订阅 / 交易抽佣 / 增值服务  
  - ARPU、付费率、广告负载（广告占用用户时间的比例）

- **Unit economics / 单位经济模型**  
  - CAC（获客成本）、LTV、回本周期  
  - 不同渠道/城市/品类的获客效率差异

**Additional questions / 可直接提问的附加问题：**

- What are the key user cohorts and how do their retention/ARPU differ?
- How does the company balance growth vs profitability (e.g., marketing spend intensity)?
- What regulatory risks exist around data privacy, content moderation, or platform power?

> Prompt 示例：
> 「针对某互联网平台公司，在 10 大维度基础上，额外重点分析用户增长 & 留存、变现模式与单位经济模型，并结合监管风险给出中长期盈利能力判断。」

---

### B. Semiconductors / 半导体

**Typical businesses / 典型业务：** GPU/CPU/ASIC 设计、晶圆制造（Foundry）、封装测试、设备与材料等。

**Extra focus areas / 额外关注点：**

- **Position in the value chain / 产业链位置**  
  - Fabless（无晶圆设计）、IDM、一体化厂商、Foundry（代工）、OSAT（封测）、设备/材料  
  - 上游/下游依赖关系

- **Technology node & roadmap / 工艺节点与技术路线**  
  - 制程节点（3nm/5nm/7nm/成熟制程）  
  - 关键产品的性能/功耗/成本相对优势  
  - 与主要代工厂（如 TSMC/Samsung）的绑定深度与议价力

- **End markets & demand drivers / 下游应用与需求驱动**  
  - 智能手机、PC、数据中心、汽车电子、工业、IoT 等占比  
  - 周期性 vs 结构性需求（如 AI、汽车电子的渗透提升）

- **Capacity & supply constraints / 产能与供给约束**  
  - 产能利用率、扩产/资本开支计划  
  - 上游瓶颈（设备交付、材料供应）

**Additional questions / 可直接提问的附加问题：**

- Which part of the semiconductor value chain does the company dominate, and how cyclical is that segment?
- How exposed is the company to AI, automotive, or other structural growth drivers?
- What are the key supply chain/geopolitical risks (export controls, tariffs, onshoring)?

> Prompt 示例：
> 「针对某半导体公司，在 10 大维度基础上，重点补充其在产业链中的位置、主要下游应用结构、工艺/产品路线图以及 AI/汽车电子等结构性需求的暴露度，并评估地缘政治对其业务的潜在影响。」

---

### C. Chain Coffee & Food Service / 连锁咖啡与餐饮服务

**Typical businesses / 典型业务：** 连锁咖啡品牌、连锁茶饮、快餐/休闲餐厅品牌等。

**Extra focus areas / 额外关注点：**

- **Store economics / 单店模型**  
  - 单店投资额、回本周期  
  - 单店收入结构（堂食/外卖/零售）、毛利率  
  - 不同城市/商圈/模型（街边店、商场店、写字楼店）的差异

- **Same-store sales & expansion / 同店增长与扩店节奏**  
  - 同店销售增长（SSS）走势  
  - 开店与关店节奏，新店 vs 老店贡献  
  - 是否存在“激进开店 → 同店下滑 → 关店潮”的风险

- **Brand & customer perception / 品牌力与消费者心智**  
  - 品牌定位（高端 / 大众 / 性价比）  
  - 核心产品力（咖啡/饮品/食品）与价格带  
  - 用户复购率、会员体系、社交媒体口碑

- **Supply chain & cost structure / 供应链与成本结构**  
  - 原材料成本（咖啡豆、乳制品、辅料）、人工、租金占比  
  - 集中采购与议价能力  
  - 食品安全与供应链稳定性

**Additional questions / 可直接提问的附加问题：**

- What does a typical store P&L look like (revenue, gross margin, fixed costs)?
- How sustainable is the pace of new store openings without diluting unit economics?
- How sensitive is the business to macro factors (consumer confidence, rent, raw material prices)?

> Prompt 示例：
> 「针对某连锁咖啡品牌，在 10 大通用维度基础上，重点拆解单店经济模型（投资额、回本周期、毛利结构）、同店增长与扩店策略、品牌定位与复购率，并评估在不同经济周期下的抗压能力。」

---

## Research Framework / 研究框架

When analyzing a company for investment, follow this structured approach to ensure comprehensive coverage:

在分析一家公司时，建议按以下 10 个维度逐一梳理，避免遗漏关键点：

### 1. Competitive Positioning Analysis / 竞争优势与护城河

**Core Questions:**
- What are the company's core competitive advantages compared to rivals?
- What is the company's economic moat? (network effects, switching costs, cost advantages, intangible assets, scale)
- How sustainable and defensible is this moat?

**Search Strategy:**
- Search for "[Company] competitive advantages moat"
- Search for "[Company] vs [Top Competitor] comparison"
- Look for industry analyst reports on competitive landscape

**Analysis Approach:**
- Identify unique value propositions
- Evaluate barriers to entry
- Assess competitive intensity using Porter's Five Forces framework
- Determine moat width (narrow/wide) and durability (temporary/enduring)

### 2. Technology & Innovation Assessment / 技术与研发能力

**Core Questions:**
- How large is the technology/R&D team?
- How many patents does the company hold? Any key patents?
- What is the R&D expense ratio (R&D/Revenue)?
- What are the core technological advantages?

**Search Strategy:**
- Search for "[Company] R&D spending annual report"
- Search for "[Company] patents technology"
- Search for "[Company] innovation pipeline"
- Check company's latest 10-K/annual report for R&D headcount

**Key Metrics:**
- R&D headcount and growth trend
- Patent portfolio size and quality
- R&D intensity (industry benchmark comparison)
- Technology leadership indicators

### 3. Market Position & Competition / 市场份额与竞争格局

**Core Questions:**
- What is the market share in primary markets?
- What is the industry ranking (top 3, top 5, etc.)?
- Who are the main competitors?
- How is market share trending?

**Search Strategy:**
- Search for "[Industry] market share [Year]"
- Search for "[Company] market position ranking"
- Search for "[Company] competitors landscape"

**Analysis Framework:**
- Market share % and rank
- Competitive landscape mapping
- Market concentration (HHI index if available)
- Competitive dynamics and threats

### 4. Customer Analysis / 客户结构与集中度

**Core Questions:**
- Who are the largest customers?
- What is customer concentration (top 5/10 customers as % of revenue)?
- What is customer diversification across industries/geographies?
- What is customer retention rate?

**Search Strategy:**
- Search for "[Company] major customers annual report"
- Search for "[Company] customer concentration risk"
- Review 10-K risk factors section

**Risk Assessment:**
- High concentration (>20% from single customer) = significant risk
- Diversified customer base = lower risk
- Long-term contracts and relationships = positive indicator

### 5. Growth Trajectory & New Opportunities / 成长路径与新机会

**Core Questions:**
- What is the current growth profile?
- What are new growth drivers/initiatives?
- Are there new markets, products, or business lines emerging?
- What is total addressable market (TAM) expansion potential?

**Search Strategy:**
- Search for "[Company] growth strategy new products"
- Search for "[Company] expansion plans"
- Search for "[Company] TAM total addressable market"

**Evaluation Criteria:**
- Organic vs. inorganic growth
- New product/service pipeline
- Market expansion opportunities (geographic, vertical)
- Scalability of growth drivers

### 6. Historical & Projected Financials / 历史与预测财务

**Core Questions:**
- Revenue and profit growth over past 5 years (CAGR)
- What drives the historical growth?
- Consensus forecast for next 2-5 years?
- Key assumptions underlying projections?

**Search Strategy:**
- Search for "[Company] revenue profit historical data"
- Search for "[Company] analyst estimates forecast"
- Access latest earnings transcripts and guidance

**Analysis Components:**
- Calculate 5-year revenue CAGR
- Calculate 5-year profit (net income/EBITDA) CAGR
- Analyze margin trends
- Review consensus estimates and evaluate reasonableness
- Create base/bull/bear case scenarios

### 7. International Exposure / 海外业务与地缘风险

**Core Questions:**
- What percentage of revenue comes from overseas?
- Which countries/regions are primary international markets?
- What are international growth trends?
- What are geopolitical or currency risks?

**Search Strategy:**
- Search for "[Company] geographic revenue breakdown"
- Search for "[Company] international expansion"
- Review segment reporting in annual reports

**Key Considerations:**
- Revenue by geography (domestic vs. international split)
- Exposure to high-growth emerging markets
- Currency hedging strategies
- Regulatory and geopolitical risks

### 8. Ownership & Governance / 股权结构与公司治理

**Core Questions:**
- Who is the founder/CEO? What is their background?
- What is the ownership structure (founder/management/institutional/public)?
- Are there any significant insider transactions?
- What is the board composition and quality?

**Search Strategy:**
- Search for "[Company] founder CEO background"
- Search for "[Company] ownership structure institutional holders"
- Search for "[Company] insider transactions recent"

**Governance Assessment:**
- Founder/management ownership alignment
- Track record of leadership team
- Board independence and expertise
- Corporate governance ratings

### 9. Valuation Analysis / 估值分析

**Core Questions:**
- Current market capitalization?
- Current P/E ratio and comparison to historical averages?
- How does valuation compare to peers?
- Is the stock trading within a margin of safety?
- What is the projected market cap in 2 years based on growth assumptions?

**Search Strategy:**
- Search for "[Company] stock price market cap"
- Search for "[Company] PE ratio valuation multiples"
- Search for "[Industry] average PE ratio"

**Valuation Framework:**
- Current market cap
- P/E, P/S, P/B, EV/EBITDA multiples
- Compare to 5-year historical average
- Compare to peer group median
- Calculate intrinsic value range (DCF if appropriate)
- Determine margin of safety (typically seek 20-30% discount)
- Project forward market cap using growth and multiple assumptions

### 10. Investment Recommendation / 投资结论

**Synthesize all analysis into clear recommendation:**

**If Investment is Recommended:**
- Primary thesis (2-3 key reasons)
- Supporting evidence from analysis above
- Expected return and timeframe
- Key risks and mitigation factors
- Position sizing recommendation

**If Investment is NOT Recommended:**
- Primary concerns (2-3 key reasons)
- Supporting evidence from analysis
- What would need to change for positive view
- Alternative opportunities in the sector

---

## Output Structure / 推荐输出结构

Present findings in a clear, structured format:

```markdown
# Investment Analysis: [Company Name]
**Date:** [Current Date]
**Analyst:** [Your Name or Agent]

## Executive Summary
[2-3 paragraph overview with key takeaway and recommendation]

## 1. Competitive Positioning
[Findings]

## 2. Technology & Innovation
[Findings]

## 3. Market Position
[Findings]

## 4. Customer Base
[Findings]

## 5. Growth Analysis
[Findings]

## 6. Financial Performance
[Findings]

## 7. International Exposure
[Findings]

## 8. Ownership & Governance
[Findings]

## 9. Valuation
[Findings]

## 10. Investment Recommendation
**Recommendation:** BUY / HOLD / SELL
**Target Price:** [If applicable]
**Investment Thesis:** [Key reasons]
**Key Risks:** [Main concerns]
```

建议在实际使用中，将上述结构作为 Markdown 模板，一边研究一边填空，最终沉淀为可复用的投研文档库。

---

## Research Best Practices / 研究最佳实践

1. **Use Multiple Sources / 多源交叉验证**  
   Cross-reference information from company filings, analyst reports, news, and financial databases.

2. **Verify Timeliness / 确保数据新鲜度**  
   Always check dates on data – use the most recent available information.

3. **Quantify When Possible / 尽量量化**  
   Provide specific numbers, percentages, and metrics rather than only qualitative descriptions.

4. **Acknowledge Limitations / 明确假设与局限**  
   Note when information is unavailable or when making assumptions.

5. **Maintain Objectivity / 保持客观**  
   Present both bullish and bearish perspectives; avoid confirmation bias.

6. **Source Attribution / 标注关键来源**  
   Cite sources for key data points, especially financial figures.

---

## Integrations: Fetching Filings & Financial Data / 集成：自动拉取财报与数据

This skill focuses on **how to think and structure research**. For data and filings, pair it with external tools/APIs.

本技能侧重于**思考框架与结构化输出**，财报与数据建议通过其他工具或脚本获取，然后作为本框架的输入。

### Example: US-listed companies (e.g., SEC + financial APIs)

示例以美股为主（可按同样思路换成 A 股/港股对应数据源）：

- **Download latest 10-K / 10-Q filings**  
  Use any SEC helper tool or script, for example:

  ```bash
  # Example: download the latest 10-K for NVIDIA (NVDA) into ./filings
  sec-edgar-downloader company "NVIDIA" \
    --form-type 10-K --num 1 --download-folder ./filings
  ```

- **Fetch key financials via an API or Python script**  
  For example, a simple Python entry point:

  ```bash
  python scripts/fetch_financials.py --ticker NVDA --out data/nvda.json
  ```

  The script can query any financial data provider (Yahoo Finance, financial APIs, etc.) and standardize
  outputs (revenue, margins, key ratios) for later use in this framework.

- **Use web_fetch for qualitative sections**  
  For business descriptions, risk factors, and management discussion, you can:

  ```text
  1. Download the filing (PDF/HTML)
  2. Use web_fetch to extract key sections into markdown
  3. Feed those into the 10-dimension analysis
  ```

> 推荐实践：将「数据抓取脚本 + 本投研框架」放在同一项目中，通过 Makefile 或 shell 脚本串联，形成一键跑通的投研流水线（先拉数据，再生成报告草稿）。

---

## Tool Usage Hints / 工具使用提示

- **web_search:** Primary tool for gathering company information, financial data, and market intelligence.
- **web_fetch:** Retrieve full annual reports, investor presentations, and detailed articles for deeper reading.
- Use this skill mainly as a **thinking & structuring framework** – pair it with data sources (e.g., financial APIs, filings) for best results.
