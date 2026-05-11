# AdClaw — Ad Creative Search Skill

Search competitor ad creatives using natural language. Results displayed as interactive H5 pages.

## Features

- Keyword search for ad creatives (app name, ad copy, brand, etc.)
- Filter by creative type: video / image / playable ad
- Filter by region: Southeast Asia, North America, Europe, Japan & Korea, Middle East, etc.
- Sort by date, impressions, or days active
- Visual H5 result pages with inline video and image preview

## Install

```bash
npx clawhub install adclaw
```

## Setup

1. Go to [adclaw.miaozhisheng.tech](https://adclaw.miaozhisheng.tech) to register and get your API Key
2. Configure:

```bash
openclaw config set skills.entries.adclaw.apiKey "YOUR_ADCLAW_API_KEY"
```

## Usage Examples

After setup, just tell your AI assistant:

- "Search video ads for puzzle games"
- "Find casual game creatives in Southeast Asia"
- "Show me temu's latest ad creatives"
- "Search e-commerce ads with the most impressions this week"

## Supported Filters

| Filter | Examples |
|--------|----------|
| Keyword | puzzle game, temu, e-commerce |
| Creative type | video, image, playable ad |
| Region | Southeast Asia, US, Japan & Korea, Europe, Middle East |
| Date range | last week, last month, custom dates |
| Sort by | newest, most popular (impressions), longest running |

## Links

- Website: [adclaw.miaozhisheng.tech](https://adclaw.miaozhisheng.tech)
- GitHub: [github.com/fly0pants/adclaw](https://github.com/fly0pants/adclaw)

---

Built by [Miaozhisheng](https://adclaw.miaozhisheng.tech)
