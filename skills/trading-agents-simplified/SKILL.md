---
name: trading-agents
description: Multi-agent stock trading signal analysis framework with two-round debate mechanism. Triggered when users provide a stock ticker for investment analysis. Input a stock ticker, analyze through 7 SubAgents in 4 layers (Information Gathering → Opinion Formation → Two-Round Debate → Final Decision), output BUY/SELL/HOLD recommendation with rationale. Trigger phrases: "analyze this stock", "give me investment advice", "is this stock worth buying", "analyze XX stock", "stock investment analysis".
license: MIT
author: laigen
requires:
  env:
    - name: TUSHARE_TOKEN
      required: true
    - name: BRAVE_API_KEY
      required: false
  pip:
    - tushare>=1.3.0
    - pandas>=1.5.0
    - numpy>=1.21.0
---

# TradingAgents - Stock Trading Signal Analysis Assistant

Multi-agent collaborative stock trading signal analysis framework with **two-round debate mechanism**, inspired by the open-source TradingAgents project.

## Environment Requirements

### Required Environment Variables

| Variable | Required | Description |
|----------|:--------:|-------------|
| **TUSHARE_TOKEN** | ✅ | Tushare Pro API Token, get at: https://tushare.pro/register |
| **BRAVE_API_KEY** | ⚪ | Brave Search API Key (optional, for news search enhancement) |

### Python Dependencies

Install required packages before using this skill:

```bash
pip install tushare>=1.3.0 pandas>=1.5.0 numpy>=1.21.0
```

### Secure Configuration

> **Security Warning**: Do NOT paste your API tokens in chat messages.

**Set Environment Variables**

Before running this skill, ensure the following environment variables are set:

```bash
export TUSHARE_TOKEN=your_token_here
export BRAVE_API_KEY=your_brave_key_here  # optional
```

**Avoid**:
- Do NOT add tokens to `~/.bashrc`, `~/.zshrc`, or other shell config files
- Do NOT include tokens in reports or SubAgent communications
- Do NOT paste tokens in chat messages

### Side Effects

This skill will:
- **Write** reports to `~/.openclaw/workspace/memory/reports/trading-agents-*.md`
- **Connect** to Tushare Pro API (`api.tushare.pro`)
- **Use** web_search for news and sentiment data

No data is transmitted externally beyond these API calls.

## Security Rules

### Credential Protection

1. **Only read TUSHARE_TOKEN and BRAVE_API_KEY** from environment variables
2. **Never read other configuration files** (e.g., openclaw.json, .bashrc, etc.)
3. **Never include API keys or tokens** in:
   - SubAgent inter-communications
   - Generated reports
   - Any output files

### Report Content Rules

All generated reports and SubAgent communications **MUST NOT** contain:
- API keys (TUSHARE_TOKEN, BRAVE_API_KEY)
- Passwords or secrets
- Any credential values

If a SubAgent receives or generates content containing sensitive credentials, it must **redact** them before passing to other agents or writing to files.

## Workflow (4-Layer Architecture)

```
Input: Stock Ticker (e.g., 300750.SZ)
  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 1: Information Gathering (Parallel)          │
│  ├─ SubAgent 1: Fundamental Analyst                 │
│  ├─ SubAgent 2: Market Analyst                      │
│  ├─ SubAgent 3: News Analyst                        │
│  └─ SubAgent 4: Social Media Analyst                │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2: Opinion Formation (Parallel)              │
│  ├─ SubAgent 5: Bull Researcher (Initial Report)    │
│  └─ SubAgent 6: Bear Researcher (Initial Report)    │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 2.5: Two-Round Debate (Sequential)           │
│  ├─ Round 1:                                        │
│  │   ├─ Bear Researcher → Bull's Arguments          │
│  │   └─ Bull Researcher → Bear's Arguments          │
│  └─ Round 2:                                        │
│      ├─ Bear Researcher → Bull's Rebuttals          │
│      └─ Bull Researcher → Bear's Rebuttals          │
└─────────────────────────────────────────────────────┘
  ↓
┌─────────────────────────────────────────────────────┐
│  Layer 3: Final Decision                            │
│  └─ SubAgent 7: Research Manager                    │
│      (Synthesizes all reports + debate history)     │
└─────────────────────────────────────────────────────┘
  ↓
Output: BUY/SELL/HOLD + Investment Plan (Markdown)
```

### Step 7: Export to Markdown Report

Research Manager outputs the complete report to a markdown file:
```
~/.openclaw/workspace/memory/reports/trading-agents-[stock_code]-[timestamp].md
```

The markdown file contains:
- Part I: Final Investment Decision
- Part II: Layer 1 Reports (4 reports)
- Part III: Layer 2 Reports (2 initial reports)
- Part IV: Debate History (4 responses)
- Part V: Appendix

---

## Execution Steps

### Step 1: Parse Stock Ticker

Extract stock ticker from user input, format to standard:
- A-shares: `600519.SH`, `300750.SZ`
- HK stocks: `00700.HK`
- US stocks: `AAPL`

### Step 2: Execute Layer 1 SubAgents in Parallel

Use `sessions_spawn` to **launch in parallel** 4 SubAgents:

| SubAgent | Task | Output |
|----------|------|--------|
| **Fundamental Analyst** | Fundamental analysis | Fundamental report |
| **Market Analyst** | Market technical analysis | Market analysis report |
| **News Analyst** | News analysis | News summary report |
| **Social Media Analyst** | Social sentiment analysis | Sentiment report |

### Step 3: Collect Layer 1 Reports

Use `subagents(action=list)` to check all SubAgent completion status, then collect report content.

### Step 4: Execute Layer 2 SubAgents in Parallel (Initial Reports)

Pass Layer 1 reports to Layer 2, **launch in parallel** 2 SubAgents:

| SubAgent | Task | Input | Output |
|----------|------|-------|--------|
| **Bull Researcher** | Initial bull report | Layer 1 4 reports | Bull report (initial) |
| **Bear Researcher** | Initial bear report | Layer 1 4 reports | Bear report (initial) |

### Step 5: Two-Round Debate

After Layer 2 completes, initiate **two rounds of debate**:

#### Round 1:
1. **Bear Researcher** receives Bull's initial report → Refutes bull arguments
2. **Bull Researcher** receives Bear's initial report → Refutes bear arguments

#### Round 2:
1. **Bear Researcher** receives Bull's Round 1 rebuttals → Counter-rebuttal
2. **Bull Researcher** receives Bear's Round 1 rebuttals → Counter-rebuttal

**Debate Rules**:
- Use specific data and reasoning to refute opponent's arguments
- Cite sources from all available reports
- Apply conversational debate style
- Reflect on past experience and lessons learned
- Each response should directly address opponent's specific points
- **Never include API keys or tokens in debate content**

### Step 6: Execute Final Decision SubAgent

Launch **Research Manager** with ALL inputs:
- Layer 1: 4 reports (Fundamental, Market, News, Social)
- Layer 2: 2 initial reports (Bull, Bear)
- Layer 2.5: 4 debate responses (Round 1 + Round 2)

Research Manager synthesizes all information and makes final investment recommendation.

---

## SubAgent Details

### SubAgent 1: Fundamental Analyst

**Data Sources**:
- Tushare Pro API (financial data, valuation metrics)
- Company annual/quarterly reports

**Analysis Dimensions**:
1. Financial statement analysis
2. Valuation metrics (PE/PB/PS percentile)
3. Growth metrics
4. Company basic information
5. Shareholder structure

**Detailed Prompt**: See [references/fundamental-analyst.md](references/fundamental-analyst.md)

---

### SubAgent 2: Market Analyst

**Data Sources**:
- Tushare Pro API (daily data)
- Technical indicator calculations

**Analysis Dimensions**:
1. Price trend (MA system)
2. Technical indicators (MACD, RSI, KDJ, BOLL)
3. Volume analysis
4. Capital flow
5. Market anomaly signals

**Detailed Prompt**: See [references/market-analyst.md](references/market-analyst.md)

---

### SubAgent 3: News Analyst

**Data Sources**:
- Web Search (Brave Search API)
- Financial media websites

**Analysis Dimensions**:
1. Company news
2. Industry news
3. Management dynamics
4. Macro news

**Detailed Prompt**: See [references/news-analyst.md](references/news-analyst.md)

---

### SubAgent 4: Social Media Analyst

**Data Sources**:
- Web Search
- Xueqiu, Guba, Weibo, Zhihu, etc.

**Analysis Dimensions**:
1. Sentiment heat
2. Investor sentiment (bullish/bearish ratio)
3. Controversy focus
4. KOL opinions

**Detailed Prompt**: See [references/social-analyst.md](references/social-analyst.md)

---

### SubAgent 5: Bull Researcher

**Role**: Bull analyst advocating for investment

**Tasks**:
1. Generate initial bull report from Layer 1 data
2. Refute bear's arguments in debate rounds
3. Provide counter-rebuttals in Round 2

**Debate Style**:
- Conversational tone addressing opponent directly
- Use specific data to counter opponent's points
- Cite sources from all available reports
- Reflect on past experience and mistakes
- **Never include API keys in output**

**Detailed Prompt**: See [references/bull-researcher.md](references/bull-researcher.md)

---

### SubAgent 6: Bear Researcher

**Role**: Bear analyst advocating against investment

**Tasks**:
1. Generate initial bear report from Layer 1 data
2. Refute bull's arguments in debate rounds
3. Provide counter-rebuttals in Round 2

**Debate Style**:
- Conversational tone addressing opponent directly
- Use specific data to expose weaknesses
- Cite sources from all available reports
- Reflect on past experience and mistakes
- **Never include API keys in output**

**Detailed Prompt**: See [references/bear-researcher.md](references/bear-researcher.md)

---

### SubAgent 7: Research Manager

**Role**: Portfolio manager making final decision

**Input** (9 items total):
1. Fundamental Analysis Report
2. Market Analysis Report
3. News Analysis Report
4. Social Media Sentiment Report
5. Bull Initial Report
6. Bear Initial Report
7. Round 1 Debate (2 responses)
8. Round 2 Debate (2 responses)

**Responsibilities**:
1. Synthesize all reports and debate history
2. Identify most persuasive arguments from both sides
3. Make final decision: **BUY/SELL/HOLD**
4. Develop detailed investment plan
5. **Ensure final report contains NO API keys or tokens**

**Important**: Do not default to "HOLD" - must take a stance based on strongest arguments.

**Detailed Prompt**: See [references/research-manager.md](references/research-manager.md)

---

## Report Format Requirements

### Price Change Color Convention (China Style)
- Red = Up (+)
- Green = Down (-)

### Data Citation
- All data must cite sources
- When using Tushare Pro, note `Data Source: Tushare Pro`
- When using Web Search, cite source URL

### Security Requirement
- **Reports MUST NOT contain any API keys, tokens, or credentials**
- If any credential is found in output, redact immediately

### Signature
- Use signature at end of financial reports

---

## Implementation Scripts

### Get Fundamental Data
```bash
python3 scripts/get_fundamentals.py <stock_code>
```

### Get Market Data
```bash
python3 scripts/get_market_data.py <stock_code>
```

---

## Output Example

```markdown
# TradingAgents Investment Decision Report: 宁德时代 (300750.SZ)

Report Generated: YYYY-MM-DD HH:MM
Framework Version: TradingAgents v2.0 with Debate Mechanism

---

# Part I: Final Investment Decision

## 一、决策摘要

### 投资建议

# 🟢 买入 / 🔴 卖出 / 🟡 持有

### 核心理由

[一句话概括核心理由，基于辩论结果]

### 信心指数

| 维度 | 信心度 | 说明 |
|------|:------:|------|
| 基本面 | x/5 | [说明] |
| 市场面 | x/5 | [说明] |
| 消息面 | x/5 | [说明] |
| 综合信心 | x/5 | - |

---

## 二、辩论精华回顾

### 2.1 初始观点对比

| 方面 | 看涨观点 | 看跌观点 |
|------|----------|----------|
| 核心论点 | [论点] | [论点] |
| 支撑数据 | [数据] | [数据] |
| 初始得分 | x/5 | x/5 |

### 2.2 第一轮辩论结果

#### 看跌方对看涨方的挑战

| 看涨论点 | 看跌方反驳 | 反驳有效性 | 幸存状态 |
|----------|------------|:----------:|:--------:|
| [论点1] | [反驳] | 高/中/低 | ✅/❌ |
| [论点2] | [反驳] | 高/中/低 | ✅/❌ |

#### 看涨方对看跌方的挑战

| 看跌论点 | 看涨方反驳 | 反驳有效性 | 幸存状态 |
|----------|------------|:----------:|:--------:|
| [论点1] | [反驳] | 高/中/低 | ✅/❌ |
| [论点2] | [反驳] | 高/中/低 | ✅/❌ |

### 2.3 第二轮辩论结果

| 议题 | 看涨最终立场 | 看跌最终立场 | 辩论胜出方 |
|------|--------------|--------------|:----------:|
| [议题1] | [立场] | [立场] | 🟢/🔴/🟡 |
| [议题2] | [立场] | [立场] | 🟢/🔴/🟡 |

### 2.4 辩论胜负关键

**看涨方胜出理由** (如适用):
1. [理由1]
2. [理由2]

**看跌方胜出理由** (如适用):
1. [理由1]
2. [理由2]

---

## 三、最终判断

### 3.1 为什么选择 [买入/卖出/持有]

[详细解释基于辩论结果做出此决策的原因]

### 3.2 经过辩论验证的核心论点

#### 买入/持有支撑论点 (经辩论验证)

| 优先级 | 论点 | 辩论验证结果 | 来源 |
|:------:|------|--------------|------|
| 1 | [论点] | 看跌方无法有效反驳 | [来源] |
| 2 | [论点] | 看跌方反驳力度不足 | [来源] |

#### 卖出/回避风险论点 (经辩论验证)

| 优先级 | 论点 | 辩论验证结果 | 来源 |
|:------:|------|--------------|------|
| 1 | [论点] | 看涨方无法有效反驳 | [来源] |
| 2 | [论点] | 风险确认 | [来源] |

### 3.3 辩论暴露的关键风险

| 风险 | 暴露程度 | 应对策略 |
|------|:--------:|----------|
| [风险1] | 高/中/低 | [策略] |
| [风险2] | 高/中/低 | [策略] |

---

## 四、投资计划

### a) 投资建议

**[买入/卖出/持有]**

| 配置建议 | 建议 |
|----------|------|
| 建议仓位 | 低配(10-20%) / 标配(20-40%) / 高配(40-60%) |
| 持有期限 | 短线(1-3月) / 中线(3-12月) / 长线(1年+) |
| 信心等级 | 低 / 中 / 高 |

### b) 理由

[详细解释这些论据为何能够得到该结论]

### c) 战略行动

| 步骤 | 具体操作 | 时间节点 |
|:----:|----------|----------|
| 1 | 分批建仓：建议分x批买入 | [时间] |
| 2 | 入场时机：[技术面建议] | [条件] |
| 3 | 止损设置：设定止损位在 xx | [条件] |

---

## 五、后续跟踪要点

### 需要关注的关键指标

| 指标 | 当前值 | 警戒值 | 触发行动 |
|------|--------|--------|----------|
| [指标1] | xx | xx | [行动] |

### 需要关注的关键事件

| 事件 | 预计时间 | 对论点的影响 | 行动预案 |
|------|---------|--------------|----------|
| [事件1] | [时间] | 影响[论点] | [预案] |

---

## 六、免责声明

本报告基于多智能体辩论分析框架生成，综合了看涨和看跌双方观点及其辩论过程。投资决策应基于个人风险承受能力和投资目标。本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

# Part II: Layer 1 Reports (Information Gathering)

## 1. Fundamental Analysis Report

[Complete fundamental analyst report]

## 2. Market Analysis Report

[Complete market analyst report]

## 3. News Analysis Report

[Complete news analyst report]

## 4. Social Media Sentiment Report

[Complete social media analyst report]

---

# Part III: Layer 2 Reports (Opinion Formation)

## 5. Bull Researcher Initial Report

[Complete bull researcher initial report]

## 6. Bear Researcher Initial Report

[Complete bear researcher initial report]

---

# Part IV: Debate History (Layer 2.5)

## Round 1

### Bear's Rebuttal to Bull's Arguments

[Bear's round 1 response]

### Bull's Rebuttal to Bear's Arguments

[Bull's round 1 response]

## Round 2

### Bear's Counter-Rebuttal

[Bear's round 2 response]

### Bull's Counter-Rebuttal

[Bull's round 2 response]

---

# Part V: Appendix

## Data Sources

- Tushare Pro API
- Web Search (Brave Search)
- Social Media Platforms

## Methodology

This report was generated using the TradingAgents Multi-Agent Debate Framework:
1. **Layer 1**: 4 specialized analysts gather comprehensive information
2. **Layer 2**: Bull and Bear researchers form opposing viewpoints
3. **Layer 2.5**: Two rounds of structured debate
4. **Layer 3**: Portfolio manager synthesizes debate outcomes into final decision

## Disclaimer

本报告基于多智能体辩论分析框架生成，综合了看涨和看跌双方观点及其辩论过程。投资决策应基于个人风险承受能力和投资目标。本报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。

---

🐂 TradingAgents Multi-Agent Debate Analysis Framework
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v2.4.2 | 2026-03-26 | Synchronized SKILL.md Output Example with research-manager.md Output Format (full Part I-V structure) |
| v2.4.0 | 2026-03-26 | Enhanced security: removed openclaw.json reference, added SubAgent security rules, unified install spec |
| v2.3.0 | 2026-03-26 | Removed PDF export, simplified dependencies, unified metadata |
| v2.2.0 | 2026-03-26 | Security hardening: Fixed metadata inconsistencies, improved credential handling |
| v2.0.0 | 2026-03-25 | Added two-round debate mechanism |
| v1.0.0 | 2026-03-20 | Initial release with 7 SubAgents |

---

## Security & Privacy

### Credential Handling
- **TUSHARE_TOKEN** and **BRAVE_API_KEY** are sensitive credentials
- Read **only** from environment variables
- Do NOT paste tokens in chat messages
- Do NOT store tokens in shell config files (`.bashrc`, `.zshrc`)

### Data Handling
- Financial data fetched from Tushare Pro API only
- Reports saved locally, not transmitted externally
- No telemetry or analytics collected

### SubAgent Security Rules
- SubAgents MUST NOT read any configuration beyond TUSHARE_TOKEN and BRAVE_API_KEY
- SubAgents MUST NOT pass API keys in inter-agent communications
- Generated reports MUST NOT contain any sensitive credential information

### Side Effects
- Writes reports to `~/.openclaw/workspace/memory/reports/`
- Connects to external APIs (Tushare, web search)
- Does not modify any other files or configurations