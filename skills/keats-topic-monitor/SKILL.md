---
name: topic-monitor
version: 1.3.5
description: Monitor topics of interest and proactively alert when important developments occur. Use when user wants automated monitoring of specific subjects (e.g., product releases, price changes, news topics, technology updates). Supports scheduled web searches, AI-powered importance scoring, smart alerts vs weekly digests, and memory-aware contextual summaries.
metadata: {"openclaw":{"requires":{"bins":["python3"],"env":{"TOPIC_MONITOR_TELEGRAM_ID":"optional - Telegram chat ID for alerts","TOPIC_MONITOR_DATA_DIR":"optional - defaults to .data/ in skill dir","WEB_SEARCH_PLUS_PATH":"optional - defaults to relative path"},"note":"All env vars optional. Defaults work out of the box."}}}
---

# Topic Monitor

**Monitor what matters. Get notified when it happens.**

Topic Monitor transforms your assistant from reactive to proactive by continuously monitoring topics you care about and intelligently alerting you only when something truly matters.

---

## ⚡ Quick Start (New in v1.2.0!)

**Just want to monitor one topic? One command:**

```bash
python3 scripts/quick.py "AI Model Releases"
```

That's it! This creates a topic with sensible defaults:
- **Query:** Auto-generated from topic name
- **Keywords:** Extracted from topic name
- **Frequency:** Daily
- **Importance:** Medium
- **Channel:** Telegram

### Quick Start Options

```bash
# Basic - just a topic name
python3 scripts/quick.py "Bitcoin Price"

# With keywords
python3 scripts/quick.py "Security CVEs" --keywords "CVE,vulnerability,critical"

# High priority, hourly checks
python3 scripts/quick.py "Production Alerts" --frequency hourly --importance high

# Custom query
python3 scripts/quick.py "Competitor News" --query "CompanyName product launch funding"

# Different channel
python3 scripts/quick.py "Team Updates" --channel discord
```

### Quick Start vs Full Setup

| Feature | Quick Start | Full Setup |
|---------|-------------|------------|
| Speed | ⚡ 1 command | 📝 Wizard |
| Defaults | Smart | Customizable |
| Use case | Single topic | Multiple topics |
| Configuration | Minimal | Full control |

**After Quick Start, you can always customize:**
```bash
python3 scripts/manage_topics.py edit ai-model-releases --frequency hourly
```

---

## Core Capabilities

1. **Topic Configuration** - Define subjects with custom parameters
2. **Scheduled Monitoring** - Automated searches at configurable intervals
3. **AI Importance Scoring** - Smart filtering: immediate alert vs digest vs ignore
4. **Contextual Summaries** - Not just links—meaningful summaries with context
5. **Weekly Digest** - Low-priority findings compiled into readable reports
6. **Memory Integration** - References your past conversations and interests

---

## Full Setup (Interactive Wizard)

For configuring multiple topics or advanced options:

```bash
python3 scripts/setup.py
```

The wizard will guide you through:

1. **Topics** - What subjects do you want to monitor?
2. **Search queries** - How to search for each topic
3. **Keywords** - What terms indicate relevance
4. **Frequency** - How often to check (hourly/daily/weekly)
5. **Importance threshold** - When to send alerts (low/medium/high)
6. **Weekly digest** - Compile non-urgent findings into a summary

The wizard creates `config.json` with your preferences. You can always edit it later or use `manage_topics.py` to add/remove topics.

**Example session:**
```
🔍 Topic Monitor - Setup Wizard

What topics do you want to monitor?
  > AI Model Releases
  > Security Vulnerabilities
  > 

--- Topic 1/2: AI Model Releases ---
  Search query for 'AI Model Releases' [AI Model Releases news updates]: new AI model release announcement
  Keywords to watch for in 'AI Model Releases'?
  > GPT, Claude, Llama, release

--- Topic 2/2: Security Vulnerabilities ---
  Search query for 'Security Vulnerabilities' [Security Vulnerabilities news updates]: CVE critical vulnerability patch
  Keywords to watch for in 'Security Vulnerabilities'?
  > CVE, vulnerability, critical, patch

How often should I check for updates?
  1. hourly
  2. daily *
  3. weekly

✅ Setup Complete!
```

## Quick Start

Already know what you're doing? Here's the manual approach:

```bash
# Initialize config from template
cp config.example.json config.json

# Add a topic
python3 scripts/manage_topics.py add "Product Updates" \
  --keywords "release,update,patch" \
  --frequency daily \
  --importance medium

# Test monitoring (dry run)
python3 scripts/monitor.py --dry-run

# Set up cron for automatic monitoring
python3 scripts/setup_cron.py
```

## Topic Configuration

Each topic has:

- **name** - Display name (e.g., "AI Model Releases")
- **query** - Search query (e.g., "new AI model release announcement")
- **keywords** - Relevance filters (["GPT", "Claude", "Llama", "release"])
- **frequency** - `hourly`, `daily`, `weekly`
- **importance_threshold** - `high` (alert immediately), `medium` (alert if important), `low` (digest only)
- **channels** - Where to send alerts (["telegram", "discord"])
- **context** - Why you care (for AI contextual summaries)

### Example config.json

```json
{
  "topics": [
    {
      "id": "ai-models",
      "name": "AI Model Releases",
      "query": "new AI model release GPT Claude Llama",
      "keywords": ["GPT", "Claude", "Llama", "release", "announcement"],
      "frequency": "daily",
      "importance_threshold": "high",
      "channels": ["telegram"],
      "context": "Following AI developments for work",
      "alert_on": ["model_release", "major_update"]
    },
    {
      "id": "tech-news",
      "name": "Tech Industry News",
      "query": "technology startup funding acquisition",
      "keywords": ["startup", "funding", "Series A", "acquisition"],
      "frequency": "daily",
      "importance_threshold": "medium",
      "channels": ["telegram"],
      "context": "Staying informed on tech trends",
      "alert_on": ["major_funding", "acquisition"]
    },
    {
      "id": "security-alerts",
      "name": "Security Vulnerabilities",
      "query": "CVE critical vulnerability security patch",
      "keywords": ["CVE", "vulnerability", "security", "patch", "critical"],
      "frequency": "hourly",
      "importance_threshold": "high",
      "channels": ["telegram", "email"],
      "context": "DevOps security monitoring",
      "alert_on": ["critical_cve", "zero_day"]
    }
  ],
  "settings": {
    "digest_day": "sunday",
    "digest_time": "18:00",
    "max_alerts_per_day": 5,
    "deduplication_window_hours": 72,
    "learning_enabled": true
  }
}
```

## Scripts

### manage_topics.py

Manage research topics:

```bash
# Add topic
python3 scripts/manage_topics.py add "Topic Name" \
  --query "search query" \
  --keywords "word1,word2" \
  --frequency daily \
  --importance medium \
  --channels telegram

# List topics
python3 scripts/manage_topics.py list

# Edit topic
python3 scripts/manage_topics.py edit eth-price --frequency hourly

# Remove topic
python3 scripts/manage_topics.py remove eth-price

# Test topic (preview results without saving)
python3 scripts/manage_topics.py test eth-price
```

### monitor.py

Main monitoring script (run via cron):

```bash
# Normal run (alerts + saves state)
python3 scripts/monitor.py

# Dry run (no alerts, shows what would happen)
python3 scripts/monitor.py --dry-run

# Force check specific topic
python3 scripts/monitor.py --topic eth-price

# Verbose logging
python3 scripts/monitor.py --verbose
```

**How it works:**
1. Reads topics due for checking (based on frequency)
2. Searches using web-search-plus or built-in web_search
3. Scores each result with AI importance scorer
4. High-importance → immediate alert
5. Medium-importance → saved for digest
6. Low-importance → ignored
7. Updates state to prevent duplicate alerts

### digest.py

Generate weekly digest:

```bash
# Generate digest for current week
python3 scripts/digest.py

# Generate and send
python3 scripts/digest.py --send

# Preview without sending
python3 scripts/digest.py --preview
```

Output format:
```markdown
# Weekly Research Digest - [Date Range]

## 🔥 Highlights

- **AI Models**: Claude 4.5 released with improved reasoning
- **Security**: Critical CVE patched in popular framework

## 📊 By Topic

### AI Model Releases
- [3 findings this week]

### Security Vulnerabilities
- [1 finding this week]

## 💡 Recommendations

Based on your interests, you might want to monitor:
- "Kubernetes security" (mentioned 3x this week)
```

### setup_cron.py

Configure automated monitoring:

```bash
# Interactive setup
python3 scripts/setup_cron.py

# Auto-setup with defaults
python3 scripts/setup_cron.py --auto

# Remove cron jobs
python3 scripts/setup_cron.py --remove
```

Creates cron entries:
```cron
# Topic Monitor - Hourly topics
0 * * * * cd /path/to/skills/topic-monitor && python3 scripts/monitor.py --frequency hourly

# Topic Monitor - Daily topics  
0 9 * * * cd /path/to/skills/topic-monitor && python3 scripts/monitor.py --frequency daily

# Topic Monitor - Weekly digest
0 18 * * 0 cd /path/to/skills/topic-monitor && python3 scripts/digest.py --send
```

## AI Importance Scoring

The scorer uses multiple signals to decide alert priority:

### Scoring Signals

**HIGH priority (immediate alert):**
- Major breaking news (detected via freshness + keyword density)
- Price changes >10% (for finance topics)
- Product releases matching your exact keywords
- Security vulnerabilities in tools you use
- Direct answers to specific questions you asked

**MEDIUM priority (digest-worthy):**
- Related news but not urgent
- Minor updates to tracked products
- Interesting developments in your topics
- Tutorial/guide releases
- Community discussions with high engagement

**LOW priority (ignore):**
- Duplicate news (already alerted)
- Tangentially related content
- Low-quality sources
- Outdated information
- Spam/promotional content

### Learning Mode

When enabled (`learning_enabled: true`), the system:
1. Tracks which alerts you interact with
2. Adjusts scoring weights based on your behavior
3. Suggests topic refinements
4. Auto-adjusts importance thresholds

Learning data stored in `.learning_data.json` (privacy-safe, never shared).

## Memory Integration

Topic Monitor connects to your conversation history:

**Example alert:**
> 🔔 **Dirac Live Update**
> 
> Version 3.8 released with the room correction improvements you asked about last week.
> 
> **Context:** You mentioned struggling with bass response in your studio. This update includes new low-frequency optimization.
> 
> [Link] | [Full details]

**How it works:**
1. Reads references/memory_hints.md (create this file)
2. Scans recent conversation logs (if available)
3. Matches findings to past context
4. Generates personalized summaries

### memory_hints.md (optional)

Help the AI connect dots:

```markdown
# Memory Hints for Topic Monitor

## AI Models
- Using Claude for coding assistance
- Interested in reasoning improvements
- Comparing models for different use cases

## Security
- Running production Kubernetes clusters
- Need to patch critical CVEs quickly
- Interested in zero-day disclosures

## Tech News
- Following startup ecosystem
- Interested in developer tools space
- Tracking potential acquisition targets
```

## Alert Channels

### Telegram

Requires OpenClaw message tool:

```json
{
  "channels": ["telegram"],
  "telegram_config": {
    "chat_id": "@your_username",
    "silent": false,
    "effects": {
      "high_importance": "🔥",
      "medium_importance": "📌"
    }
  }
}
```

### Discord

Agent-delivered (no webhook in skill config):

`monitor.py` emits `DISCORD_ALERT` JSON payloads, and OpenClaw sends them via the message tool. This matches the Telegram alert flow (structured output, no direct HTTP in skill code).

```json
{
  "channels": ["discord"]
}
```

### Email

SMTP or API:

```json
{
  "channels": ["email"],
  "email_config": {
    "to": "you@example.com",
    "from": "research@yourdomain.com",
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587
  }
}
```

## Advanced Features

### Alert Conditions

Fine-tune when to alert:

```json
{
  "alert_on": [
    "price_change_10pct",
    "keyword_exact_match",
    "source_tier_1",
    "high_engagement"
  ],
  "ignore_sources": [
    "spam-site.com",
    "clickbait-news.io"
  ],
  "boost_sources": [
    "github.com",
    "arxiv.org",
    "official-site.com"
  ]
}
```

### Regex Patterns

Match specific patterns:

```json
{
  "patterns": [
    "version \\d+\\.\\d+\\.\\d+",
    "\\$\\d{1,3}(,\\d{3})*",
    "CVE-\\d{4}-\\d+"
  ]
}
```

### Rate Limiting

Prevent alert fatigue:

```json
{
  "settings": {
    "max_alerts_per_day": 5,
    "max_alerts_per_topic_per_day": 2,
    "quiet_hours": {
      "start": "22:00",
      "end": "08:00"
    }
  }
}
```

## Environment Variables

Configure these environment variables to customize topic-monitor:

| Variable | Default | Description |
|----------|---------|-------------|
| `TOPIC_MONITOR_TELEGRAM_ID` | — | Your Telegram chat ID for receiving alerts |
| `TOPIC_MONITOR_DATA_DIR` | `.data/` in skill dir | Where to store state and findings |
| `WEB_SEARCH_PLUS_PATH` | Relative to skill | Path to web-search-plus search.py |
| `SERPER_API_KEY` / `TAVILY_API_KEY` / `EXA_API_KEY` / `YOU_API_KEY` / `SEARXNG_INSTANCE_URL` / `WSP_CACHE_DIR` | — | Optional search-provider vars passed via subprocess env allowlist |

**Example setup:**
```bash
# Add to ~/.bashrc or .env
export TOPIC_MONITOR_TELEGRAM_ID="123456789"
export TOPIC_MONITOR_DATA_DIR="/home/user/topic-monitor-data"
export WEB_SEARCH_PLUS_PATH="/path/to/skills/web-search-plus/scripts/search.py"
```

## State Management

### .research_state.json

Stored in `TOPIC_MONITOR_DATA_DIR` (default: `.data/` in skill directory).

Tracks:
- Last check time per topic
- Alerted URLs (deduplication)
- Importance scores history
- Learning data (if enabled)

Example:
```json
{
  "topics": {
    "eth-price": {
      "last_check": "2026-01-28T22:00:00Z",
      "last_alert": "2026-01-28T15:30:00Z",
      "alerted_urls": [
        "https://example.com/eth-news-1"
      ],
      "findings_count": 3,
      "alerts_today": 1
    }
  },
  "deduplication": {
    "url_hash_map": {
      "abc123": "2026-01-28T15:30:00Z"
    }
  }
}
```

### .findings/ directory

Stores digest-worthy findings:

```
.findings/
├── 2026-01-22_eth-price.json
├── 2026-01-24_fm26-patches.json
└── 2026-01-27_ai-breakthroughs.json
```

## Best Practices

1. **Start conservative** - Set `importance_threshold: medium` initially, adjust based on alert quality
2. **Use context field** - Helps AI generate better summaries
3. **Refine keywords** - Add negative keywords to filter noise: `"keywords": ["AI", "-clickbait", "-spam"]`
4. **Enable learning** - Improves over time based on your behavior
5. **Review digest weekly** - Don't ignore the digest—it surfaces patterns
6. **Combine with personal-analytics** - Get topic recommendations based on your chat patterns

## Integration with Other Skills

### web-search-plus (optional)

If the `web-search-plus` skill is available, automatically uses intelligent routing:
- Product/price topics → Serper
- Research topics → Tavily  
- Company/startup discovery → Exa

**Fallback:** If `web-search-plus` is not installed, topic-monitor uses the built-in `web_search` tool, which works well for most monitoring use cases.

### personal-analytics

Suggests topics based on conversation patterns:
> "You've asked about Rust 12 times this month. Want me to monitor 'Rust language updates'?"

## Privacy & Security

- **All data local** - No external services except search APIs
- **State files gitignored** - Safe to use in version-controlled workspace
- **Memory hints optional** - You control what context is shared
- **Learning data stays local** - Never sent to APIs
- **Subprocess env allowlist** - monitor forwards only PATH/HOME/LANG/TERM and search-provider keys
- **No direct HTTP in skill code** - alerts are emitted as JSON for OpenClaw delivery

## Troubleshooting

**No alerts being sent:**
- Check cron is running: `crontab -l`
- Verify channel config (Telegram chat ID, topic channel list for Discord/email)
- Run with `--dry-run --verbose` to see scoring

**Too many alerts:**
- Increase `importance_threshold`
- Add rate limiting
- Refine keywords (add negative filters)
- Enable learning mode

**Missing important news:**
- Decrease `importance_threshold`
- Increase check frequency
- Broaden keywords
- Check `.research_state.json` for deduplication issues

**Digest not generating:**
- Verify `.findings/` directory exists and has content
- Check digest cron schedule
- Run manually: `python3 scripts/digest.py --preview`

## Example Workflows

### Track Product Release

```bash
python3 scripts/manage_topics.py add "iPhone 17 Release" \
  --query "iPhone 17 announcement release date" \
  --keywords "iPhone 17,Apple event,September" \
  --frequency daily \
  --importance high \
  --channels telegram \
  --context "Planning to upgrade from iPhone 13"
```

### Monitor Competitor

```bash
python3 scripts/manage_topics.py add "Competitor Analysis" \
  --query "CompetitorCo product launch funding" \
  --keywords "CompetitorCo,product,launch,Series,funding" \
  --frequency weekly \
  --importance medium \
  --channels discord,email
```

### Research Topic

```bash
python3 scripts/manage_topics.py add "Quantum Computing Papers" \
  --query "quantum computing arxiv" \
  --keywords "quantum,qubit,arxiv" \
  --frequency weekly \
  --importance low \
  --channels email
```

## Credits

Built for ClawHub. Uses web-search-plus skill for intelligent search routing.
