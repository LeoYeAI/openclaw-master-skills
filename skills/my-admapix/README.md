# AdMapix — Ad Intelligence & App Analytics Skill

[中文文档](README_CN.md)

All-in-one ad intelligence assistant. Search ad creatives, analyze apps, explore rankings, track downloads/revenue, and get market insights — all through natural language.

## Features

- **Creative Search** — Search ad creatives by keyword, region, media, creative type, with H5 visual results
- **App Analysis** — Look up any app's details, developer info, and ad creative portfolio
- **Rankings** — App Store / Google Play charts, promotion rankings, download rankings, revenue rankings
- **Download & Revenue** — Track download and revenue trends over time (third-party estimates)
- **Ad Distribution** — Analyze where and how an app advertises (countries, media placements, creative formats)
- **Market Analysis** — Industry-level insights by country, media channel, advertiser, and publisher
- **Deep Dive** — Multi-dimensional reports combining all of the above
- **Deep Research** — AI-powered deep analysis for complex queries (multi-app comparisons, market strategy reports, trend analysis). Automatically triggered for questions requiring 2+ API calls, returns structured HTML reports with key findings

## Install

```bash
npx clawhub install admapix
```

## Setup

1. Go to [www.admapix.com](https://www.admapix.com) to register and get your API Key
2. Configure:

```bash
openclaw config set skills.entries.admapix.apiKey "YOUR_ADMAPIX_API_KEY"
```

## Usage Examples

After setup, just tell your AI assistant:

| Category | Example prompts |
|----------|----------------|
| Creative Search | "Search video ads for puzzle games", "Find casual game creatives in Southeast Asia" |
| App Analysis | "Tell me about Temu", "Who is the developer of TikTok?" |
| Rankings | "App Store free chart US", "Top apps by ad spend this week" |
| Downloads | "How are Temu's downloads trending?", "Compare Temu vs SHEIN downloads" |
| Ad Distribution | "Which countries does Temu advertise in?", "What ad channels does this game use?" |
| Market Analysis | "Which country has the most game ads?", "Who are the top game advertisers?" |
| Deep Dive | "Full ad strategy analysis for Temu", "Compare Temu and SHEIN" |
| Deep Research | "Analyze Temu's ad strategy in Southeast Asia", "Compare top 5 casual games' ad performance" |

Supports both **English** and **Chinese** — the assistant responds in your language.

## Deep Research — AI-Powered Intelligence Reports

For complex analytical queries, AdMapix automatically activates its **Deep Research Framework** — a server-side AI research engine that goes far beyond simple API lookups.

**How it works:**

1. The skill classifies your query by complexity. Simple lookups (single search, single ranking) are handled directly. Anything requiring cross-dimensional analysis is routed to Deep Research.
2. The research engine autonomously plans and executes a multi-step investigation — orchestrating dozens of API calls, cross-referencing data sources, and synthesizing findings.
3. Results are delivered as a structured HTML report with key findings summary, ready for sharing or further analysis.

**What triggers Deep Research:**

- Multi-app comparisons: *"Compare Temu, SHEIN, and Wish's ad strategies"*
- Strategy analysis: *"How is this game acquiring users in Japan?"*
- Market intelligence: *"Southeast Asia casual game ad market overview"*
- Trend interpretation: *"Why did this app's downloads spike last week?"*
- Any question requiring 2+ API calls or cross-entity reasoning

**What you get:**

- Structured HTML report with charts and data tables
- Executive summary with key findings
- Cross-dimensional insights (geo × media × creative × time)
- Actionable recommendations based on competitive data

The framework typically completes in 1–5 minutes depending on query complexity. Reports are hosted and shareable via link.

## Links

- Website: [www.admapix.com](https://www.admapix.com)
- GitHub: [github.com/fly0pants/admapix](https://github.com/fly0pants/admapix)

---

Built by [Miaozhisheng](https://www.admapix.com)
