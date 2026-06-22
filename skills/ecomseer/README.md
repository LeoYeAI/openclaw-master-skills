# EcomSeer — TikTok Shop E-commerce Intelligence Skill

[中文文档](README_CN.md)

All-in-one TikTok Shop data intelligence assistant. Search products, discover trending items, analyze influencers, explore shops, track video performance, and get ad insights — all through natural language.

## Features

- **Product Search** — Search TikTok Shop products by keyword, category, price, sales volume, with multi-market support
- **Sales Rankings** — Sales ranking, new products, managed (sShop) ranking, hot promotion ranking
- **Product Detail** — Deep dive into any product's sales trends, influencer partnerships, video performance, reviews
- **Influencer Analysis** — Search and analyze TikTok creators: followers, engagement, sales performance, fan demographics
- **Video Analytics** — Hot video search, video-product ranking, video detail with trend data
- **Shop Intelligence** — Search shops, view product lineup, analyze influencer partnerships
- **Ad & Creative Insights** — E-commerce ad search, advertiser analysis, trend insights, top keywords
- **Deep Research** — AI-powered deep analysis for complex queries. Automatically triggered for multi-dimensional analysis, returns structured HTML reports

## Install

```bash
npx clawhub install ecomseer
```

## Setup

1. Go to [www.ecomseer.com](https://www.ecomseer.com) to register and get your API Key
2. Configure:

```bash
openclaw config set skills.entries.ecomseer.apiKey "YOUR_ECOMSEER_API_KEY"
```


## Usage Examples

After setup, just tell your AI assistant:

| Category | Example prompts |
|----------|----------------|
| Product Search | "Search Bluetooth earbuds on TikTok Shop", "Find trending skincare products" |
| Rankings | "US TikTok Shop sales ranking", "Top new products this week" |
| Product Detail | "Show me this product's sales trend", "Which influencers promote this?" |
| Influencer | "Find beauty influencers with 100K+ followers", "Analyze this creator's performance" |
| Video | "Hot TikTok Shop videos this week", "Show video performance data" |
| Shop | "Search TikTok shops selling electronics", "Analyze this shop's product mix" |
| Ads | "Search e-commerce ad creatives", "What are the trending ad keywords?" |
| Deep Research | "Analyze US beauty category trends", "Compare top 5 shops in Southeast Asia" |

Supports both **English** and **Chinese** — the assistant responds in your language.

## Multi-Market Support

EcomSeer covers all TikTok Shop markets:

| Region Code | Market |
|-------------|--------|
| US | United States |
| GB | United Kingdom |
| ID | Indonesia |
| TH | Thailand |
| VN | Vietnam |
| MY | Malaysia |
| PH | Philippines |
| SG | Singapore |

Default market is US. Switch by saying "show me Indonesia data" or "切换到东南亚".

## Deep Research — AI-Powered Intelligence Reports

For complex analytical queries, EcomSeer automatically activates its **Deep Research Framework** — a server-side AI research engine that goes far beyond simple API lookups.

**What triggers Deep Research:**

- Category trend analysis: *"Analyze US beauty category trending products"*
- Multi-entity comparisons: *"Compare these two shops' strategies"*
- Market intelligence: *"Southeast Asia e-commerce opportunity analysis"*
- Influencer strategy: *"Analyze this creator's monetization approach"*
- Any question requiring 2+ API calls or cross-entity reasoning

**What you get:**

- Structured HTML report with charts and data tables
- Executive summary with key findings
- Cross-dimensional insights (products × influencers × videos × ads)
- Actionable e-commerce recommendations

The framework typically completes in 1–5 minutes depending on query complexity. Reports are hosted and shareable via link.

## Links

- Website: [www.ecomseer.com](https://www.ecomseer.com)

---

Built by [EcomSeer](https://www.ecomseer.com)
