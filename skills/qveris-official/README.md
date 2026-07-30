# QVeris Official Skill

The official QVeris skill for OpenClaw and other AI agents. Enables semantic tool discovery and unified execution across thousands of professional data sources, tool services, and APIs via the QVeris API.

## Features

- **Semantic Tool Discovery**: Search for APIs, tools, and services by describing what you need in natural language (English queries recommended for best results)
- **Unified Execution**: Execute any discovered tool with structured parameters and get machine-readable responses
- **Wide Coverage**: Financial markets, economics, news, social media, blockchain, AI/ML, image/video generation, geocoding, navigation, academic research, healthcare, weather, cloud services, and thousands more
- **Zero Extra Dependencies**: Uses only Node.js built-in `fetch` — no Python, no `uv`, no npm install

## Installation

### Prerequisites

- **Node.js 18+** (already present if you have OpenClaw installed)
- **QVERIS_API_KEY** — get your API key at https://qveris.ai

Set your API key:
```bash
export QVERIS_API_KEY="your-api-key-here"
```

### Install the Skill

**Option 1: Install via ClawdHub (Recommended)**
```bash
npx clawdhub install qveris-official
```

**Option 2: Manual Installation**

Copy this folder to your OpenClaw skills directory:
```bash
cp -r qveris-official ~/.openclaw/skills/
```

## Usage

Once installed, your AI agent will automatically use this skill when tasks involve:
- **Data**: stock prices, crypto, forex, commodities, economic indicators, company financials, news, social media analytics, blockchain/on-chain data
- **Tool services**: image/video generation, text-to-speech, OCR, PDF extraction, translation, AI model inference
- **Location & geo**: maps, geocoding, navigation, POI search, satellite imagery
- **Research**: academic papers, patent databases, clinical trials, datasets
- And thousands more...

### Manual Commands

```bash
# Search for tools
node scripts/qveris_tool.mjs search "stock price data"
node scripts/qveris_tool.mjs search "image generation" --limit 5

# Execute a tool
node scripts/qveris_tool.mjs execute <tool_id> --search-id <search_id> --params '{"symbol": "AAPL"}'

# Get tool details by ID (skip full search for known tools)
node scripts/qveris_tool.mjs get-by-ids <tool_id>

# Output raw JSON
node scripts/qveris_tool.mjs search "weather forecast" --json
node scripts/qveris_tool.mjs execute <tool_id> --search-id <search_id> --params '{"city": "London"}' --json
```

## Author

[@QVeris_AI](https://x.com/QVeris_AI)

## License

MIT
