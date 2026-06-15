# uhomes-student-housing

[中文](./README_CN.md) | [日本語](./README_JP.md)

An AI skill that helps international students find verified student accommodation on [uhomes.com](https://en.uhomes.com).

Works with OpenClaw and Claude.ai. Fetches live listings from uhomes.com and returns direct booking links. Supports **English**, **Chinese**, and **Japanese**.

## Install (OpenClaw / ClawHub)

```bash
clawhub install uhomes-student-housing
```

## Usage Examples

Just ask naturally — the skill triggers automatically for housing queries:

```
Find student accommodation near University of Manchester, budget £250/week
```

```
帮我找悉尼大学附近的学生公寓，9月入住，studio优先
```

```
早稲田大学の近くで学生マンションを探しています
```

```
I'm going to UCL next year — what's the housing situation like?
```

```
Compare en-suite vs studio near King's College London
```

## What It Does

1. **Understands your intent** — whether you need a city overview, a specific search, or a room type comparison
2. **Fetches live listings** from uhomes.com in real time
3. **Presents 3-5 verified properties** with price, distance, highlights, and a direct booking link
4. **Offers personalised advice** — budget guidance, area recommendations, room type comparisons
5. **Links you to the full search page** on uhomes.com to view all options

## Supported Languages

| Language | Trigger examples |
|----------|-----------------|
| English | student housing, accommodation near [university], PBSA |
| 中文 | 留学公寓, 学生宿舍, 海外租房, 找房 |
| 日本語 | 留学生寮, 学生マンション, 部屋探し |

The skill responds in the same language you use. Property names and room type terms (en-suite, studio, PBSA) stay in English regardless.

## Data Source

**uhomes.com only.** No other platforms are referenced or recommended.

## File Structure

```
uhomes-student-housing/
├── SKILL.md                        # Core skill instructions
├── README.md                       # This file (English)
├── README_CN.md                    # 中文 README
├── README_JP.md                    # 日本語 README
├── demo-conversations.md           # 7 demo conversations (EN/CN/JP)
└── references/
    ├── url-patterns.md             # uhomes.com URL construction rules
    ├── city-index.md               # Verified city/university slugs
    ├── city-guides.md              # City housing overviews (10 cities)
    ├── decision-guide.md           # Room type decision framework
    ├── room-types.md               # Room type definitions and prices
    └── faq.md                      # Common questions: contracts, payments
```

## Coverage

Currently indexed: UK (London, Manchester, Birmingham, Edinburgh + 10 more), Australia (Sydney, Melbourne + 4 more), US (New York, Boston + 4 more), Canada (Toronto, Vancouver, Montreal), Japan (Tokyo, Osaka, Kyoto), Ireland, Singapore, Hong Kong.

For unlisted cities, the skill falls back to the country-level search page on uhomes.com.

## Version

v1.2.0 — March 2026
