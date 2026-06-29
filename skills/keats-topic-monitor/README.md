# Topic Monitor

**Never miss what matters. Get alerted when it happens.**

Topic Monitor transforms your assistant from reactive to proactive by continuously monitoring topics you care about and intelligently alerting you only when something truly important occurs.

## Features

- 🔍 **Automated Monitoring** - Scheduled web searches for your topics
- 🧠 **AI Importance Scoring** - Smart filtering: alert vs digest vs ignore
- 📱 **Multi-Channel Alerts** - Telegram, Discord, Email (agent-delivered)
- 📊 **Weekly Digests** - Curated summaries of interesting findings
- 🧩 **Memory Integration** - Contextual alerts referencing your past conversations
- ⚡ **Rate Limiting** - Prevent alert fatigue
- 🎯 **Custom Conditions** - Fine-tune when to alert

## Quick Start

### Option 1: Interactive Setup (Recommended)

Run the setup wizard for a guided experience:

```bash
python3 scripts/setup.py
```

The wizard asks friendly questions about what you want to monitor and creates your config automatically.

### Option 2: Manual Setup

```bash
# 1. Copy the template
cp config.example.json config.json

# 2. Add your first topic
python3 scripts/manage_topics.py add "AI Models" \
  --query "new AI model release announcement" \
  --keywords "GPT,Claude,Llama,release" \
  --frequency daily \
  --importance high \
  --channels telegram

# 3. Test it
python3 scripts/manage_topics.py test ai-models

# 4. Set up automated monitoring
python3 scripts/setup_cron.py
```

## Use Cases

### 📈 Price Monitoring
Track product prices, SaaS pricing changes, or market trends with alerts on significant changes.

### 🔧 Product Updates
Monitor software releases, patches, and feature announcements.

### 📰 News Tracking
Stay updated on specific topics without drowning in noise.

### 🏢 Competitor Analysis
Track competitor product launches, funding, and news.

### 🎓 Research Papers
Monitor arXiv, GitHub, or academic publications in your field.

## How It Works

1. **Configure Topics** - Define what to monitor and when to alert
2. **Scheduled Checks** - Cron jobs run searches at your chosen frequency
3. **AI Scoring** - Each result is scored for importance
4. **Smart Alerting** - High priority → immediate alert, Medium → digest, Low → ignore
5. **Deduplication** - Never get the same alert twice

## Configuration

See [SKILL.md](SKILL.md) for complete documentation.

### Example Topic

```json
{
  "id": "ai-breakthroughs",
  "name": "AI Research Breakthroughs",
  "query": "artificial intelligence breakthrough research",
  "keywords": ["AI", "LLM", "transformer", "AGI"],
  "frequency": "daily",
  "importance_threshold": "medium",
  "channels": ["telegram"],
  "context": "Following AI developments for work",
  "alert_on": ["major_paper", "model_release"]
}
```

## Commands

### Manage Topics

```bash
# Add topic
python3 scripts/manage_topics.py add "Topic Name" \
  --query "search query" \
  --keywords "word1,word2" \
  --frequency daily

# List topics
python3 scripts/manage_topics.py list

# Edit topic
python3 scripts/manage_topics.py edit topic-id --frequency hourly

# Remove topic
python3 scripts/manage_topics.py remove topic-id

# Test topic
python3 scripts/manage_topics.py test topic-id
```

### Monitor

```bash
# Manual check (dry run)
python3 scripts/monitor.py --dry-run --verbose

# Check specific topic
python3 scripts/monitor.py --topic ai-models

# Check all hourly topics
python3 scripts/monitor.py --frequency hourly
```

### Digest

```bash
# Preview this week's digest
python3 scripts/digest.py --preview

# Generate and send
python3 scripts/digest.py --send
```

### Cron Setup

```bash
# Interactive setup
python3 scripts/setup_cron.py

# Auto-setup
python3 scripts/setup_cron.py --auto

# Remove cron jobs
python3 scripts/setup_cron.py --remove
```

## Integration

### Works With

- **web-search-plus** - Intelligent search routing (Serper, Tavily, Exa)
- **personal-analytics** - Get topic recommendations from your chat patterns
- **OpenClaw message tool** - Send alerts via Telegram/Discord from structured JSON output

### Channel Setup

#### Telegram
Configure in config.json:
```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "chat_id": "@your_username"
    }
  }
}
```

#### Discord
No webhook is needed in `config.json`. `monitor.py` now emits `DISCORD_ALERT` JSON lines and your OpenClaw agent delivers them via the message tool (same pattern as Telegram).

Minimal topic-level channel usage:
```json
{
  "topics": [
    {
      "name": "Team Updates",
      "channels": ["discord"]
    }
  ]
}
```

## Configuration via Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TOPIC_MONITOR_TELEGRAM_ID` | — | Telegram chat ID for alerts (required for Telegram) |
| `TOPIC_MONITOR_DATA_DIR` | `.data/` | Directory for state and findings files |
| `WEB_SEARCH_PLUS_PATH` | Relative to skill | Path to web-search-plus search.py script |
| `SERPER_API_KEY` / `TAVILY_API_KEY` / `EXA_API_KEY` / `YOU_API_KEY` / `SEARXNG_INSTANCE_URL` / `WSP_CACHE_DIR` | — | Optional search-provider vars forwarded via subprocess env allowlist |

**Example:**
```bash
export TOPIC_MONITOR_TELEGRAM_ID="123456789"
export TOPIC_MONITOR_DATA_DIR="/path/to/data"
export WEB_SEARCH_PLUS_PATH="/path/to/skills/web-search-plus/scripts/search.py"
```

## Privacy

- All data stored locally
- No external services except search APIs
- Learning data stays on your machine
- State files are gitignored
- **No hardcoded personal info** — configure via environment variables
- Search subprocess uses env allowlist only (`PATH`, `HOME`, `LANG`, `TERM` + search provider keys)
- No direct HTTP calls from topic-monitor skill code

## Requirements

- Python 3.8+
- Optional: web-search-plus skill (for better search)
- Cron (for automated monitoring)

## License

MIT

## Credits

Built for ClawHub.
