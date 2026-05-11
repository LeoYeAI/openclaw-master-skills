---
name: ai-news-aggregator-sl
description: >
  Fetches AI & tech news (default) or any custom topic (crypto, geopolitics, etc.)
  from RSS feeds, Tavily search, Twitter/X, and YouTube. Writes an English editorial
  digest using OpenAI by default (or DeepSeek / Claude), then posts it to Discord.
  Supports any time range (today, last 3 days, last week). Trigger when user asks for
  news, a digest, trending topics, or YouTube updates on any subject.
version: 1.5.1

metadata:
  openclaw:
    emoji: 🦞
    os: [linux, mac, windows]
    primaryEnv: OPENAI_API_KEY
    requires:
      env:
        - DISCORD_WEBHOOK_URL     # Required: Discord channel webhook to post results
      optionalEnv:
        - OPENAI_API_KEY          # Required if using OpenAI provider (default)
        - DEEPSEEK_API_KEY        # Required if using DeepSeek provider
        - ANTHROPIC_API_KEY       # Required if using Claude provider
        - AI_PROVIDER             # Optional: deepseek | openai | claude (default: deepseek)
        - AI_MODEL                # Optional: override model name
        - TAVILY_API_KEY          # Optional: enables custom topic search
        - TWITTERAPI_IO_KEY       # Optional: enables Twitter/X trending
        - YOUTUBE_API_KEY         # Optional: enables YouTube results
      anyBins:
        - uv
    # Python dependencies declared inline in news_aggregator.py (PEP 723).
    # `uv run news_aggregator.py` installs them automatically — no manual setup needed.
---

# 🦞 AI News Aggregator

Collects news on any topic, writes an English editorial digest using your choice of AI provider, and posts it to Discord.

**Default (AI topic):** TechCrunch · The Verge · NYT Tech (RSS) + curated AI YouTube channels
**Custom topics:** Tavily news search + YouTube topic search (no Shorts, sorted by views)
**AI providers:** OpenAI (default) · DeepSeek · Anthropic Claude — switchable per request

---

## Network Endpoints

| Endpoint | Purpose | Condition |
|----------|---------|-----------|
| `https://api.deepseek.com/chat/completions` | AI editorial summarisation | Always (required) |
| `https://discord.com/api/webhooks/...` | Post digest to Discord | Always (required) |
| `https://techcrunch.com/.../feed/` | RSS news (AI topic) | Default AI topic only |
| `https://www.theverge.com/rss/...` | RSS news (AI topic) | Default AI topic only |
| `https://www.nytimes.com/svc/collections/...` | RSS news (AI topic) | Default AI topic only |
| `https://api.tavily.com/search` | Custom topic news search | Only if `TAVILY_API_KEY` set |
| `https://api.twitterapi.io/twitter/tweet/advanced_search` | Twitter search | Only if `TWITTERAPI_IO_KEY` set |
| `https://www.googleapis.com/youtube/v3/...` | YouTube search | Only if `YOUTUBE_API_KEY` set |

The script does **not** contact OpenAI endpoints. The `openai` package is used solely as an HTTP client pointed at `https://api.deepseek.com`. `OPENAI_API_KEY` is explicitly removed from the environment at startup.

---

## Usage Examples

- "Get today's AI news"
- "Collect news about crypto"
- "Last week's news about climate change"
- "What's trending in AI today?"
- "Get crypto news from the last 3 days using OpenAI"
- "Show me recent Bitcoin YouTube videos"
- "Summarise WWIII news with Claude"
- "AI news using GPT-4o"
- "AI news dry run" *(preview without posting to Discord)*
- "Test my Discord webhook"

---

## API Keys

| Key | Required | Where to get it |
|-----|----------|----------------|
| `DISCORD_WEBHOOK_URL` | ✅ Always | Discord → Channel Settings → Integrations → Webhooks → Copy URL |
| `DEEPSEEK_API_KEY` | If using DeepSeek (default) | [platform.deepseek.com/api_keys](https://platform.deepseek.com/api_keys) |
| `OPENAI_API_KEY` | If using OpenAI | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) |
| `ANTHROPIC_API_KEY` | If using Claude | [console.anthropic.com](https://console.anthropic.com) → API Keys |
| `TAVILY_API_KEY` | For custom topics | [app.tavily.com](https://app.tavily.com) |
| `TWITTERAPI_IO_KEY` | Optional | [twitterapi.io](https://twitterapi.io) |
| `YOUTUBE_API_KEY` | Optional | [console.cloud.google.com](https://console.cloud.google.com) → YouTube Data API v3 |

## AI Providers & Models

| Provider | `--provider` value | Default model | Best for |
|----------|--------------------|---------------|---------|
| OpenAI | `openai` **(default)** | `gpt-4o-mini` | Quality, reliability |
| DeepSeek | `deepseek` | `deepseek-chat` | Cost-effective, fast |
| Claude | `claude` | `claude-3-5-haiku-20241022` | Nuanced writing |

Override per request using the `--provider` flag. Set a permanent non-default with `openclaw config set env.AI_PROVIDER '"deepseek"'`. Override the model with `--model` (e.g. `--model gpt-4o` or `--model claude-3-5-sonnet-20241022`).

---

## Implementation

**IMPORTANT:** Always run `news_aggregator.py` using the steps below. Do NOT search the web manually or improvise a response — the script handles all fetching, summarisation, and Discord posting.

### Step 1 — Locate the script

The script is bundled with this skill. Find it:

```bash
SKILL_DIR=$(ls -d ~/.openclaw/skills/ai-news-aggregator-sl 2>/dev/null || ls -d ~/.openclaw/skills/news-aggregator 2>/dev/null)
SCRIPT="$SKILL_DIR/news_aggregator.py"
echo "Script: $SCRIPT"
ls "$SCRIPT"
```

### Step 2 — Check uv is available

```bash
which uv && uv --version || echo "uv not found"
```

If `uv` is not found, ask the user to install it from their system package manager or from [https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/). Do not run a curl-pipe-sh command on the user's behalf.

### Step 3 — API keys

Env vars are passed automatically by OpenClaw from its config. No `.env` file is needed.

Verify the required keys are set (without revealing values):

```bash
[[ -n "$OPENAI_API_KEY" ]]      && echo "OPENAI_API_KEY: set"      || echo "OPENAI_API_KEY: MISSING (required for default provider)"
[[ -n "$DISCORD_WEBHOOK_URL" ]] && echo "DISCORD_WEBHOOK_URL: set" || echo "DISCORD_WEBHOOK_URL: MISSING"
```

If any are missing, ask the user to register them:
```
openclaw config set env.OPENAI_API_KEY '<key>'
openclaw config set env.DISCORD_WEBHOOK_URL '<url>'
# Optional alternatives:
openclaw config set env.DEEPSEEK_API_KEY '<key>'
openclaw config set env.ANTHROPIC_API_KEY '<key>'
```

### Step 4 — Parse the request

Extract **topic**, **days**, and **provider** from what the user said:

For AI provider:

| User said | --provider | --model |
|-----------|-----------|---------|
| "use OpenAI" / "with GPT" / "using ChatGPT" | `--provider openai` | *(omit)* |
| "use Claude" / "with Anthropic" | `--provider claude` | *(omit)* |
| "use DeepSeek" / nothing specified | *(omit — default)* | *(omit)* |
| "use GPT-4o" / "with gpt-4o" | `--provider openai` | `--model gpt-4o` |
| "use claude sonnet" | `--provider claude` | `--model claude-3-5-sonnet-20241022` |
| "use deepseek reasoner" | `--provider deepseek` | `--model deepseek-reasoner` |

Extract **topic** and **days** from what the user said:

| User said | --topic | --days |
|-----------|---------|--------|
| "AI news" / "tech news" / nothing specific | *(omit — default AI)* | 1 |
| "crypto news" | `--topic "crypto"` | 1 |
| "news about climate change" | `--topic "climate change"` | 1 |
| "last week's crypto news" | `--topic "crypto"` | 7 |
| "last 3 days of Bitcoin news" | `--topic "Bitcoin"` | 3 |
| "yesterday's AI news" | *(omit topic)* | 1 |
| "this week in AI" | *(omit topic)* | 7 |

For report type:

| User said | flag to add |
|-----------|-------------|
| "news" / "articles" / "digest" | `--report news` |
| "trending" / "Twitter" / "YouTube" | `--report trending` |
| "dry run" / "preview" / "don't post" | `--dry-run` |
| "test Discord" / "test webhook" | `--test-discord` |
| anything else | *(omit — runs all)* |

### Step 5 — Run with uv

`uv run` automatically installs all dependencies from the script's inline metadata — no venv setup needed.

```bash
uv run "$SCRIPT" [--topic "TOPIC"] [--days N] [--report TYPE] [--provider PROVIDER] [--model MODEL] [--dry-run]
```

Examples:

```bash
# AI news today — DeepSeek (default)
uv run "$SCRIPT"

# Crypto news using OpenAI
uv run "$SCRIPT" --topic "crypto" --provider openai

# Last week's climate news using Claude
uv run "$SCRIPT" --topic "climate change" --days 7 --provider claude

# Use a specific model
uv run "$SCRIPT" --topic "Bitcoin" --provider openai --model gpt-4o

# Trending AI on Twitter and YouTube
uv run "$SCRIPT" --report trending

# Preview without posting to Discord
uv run "$SCRIPT" --topic "Bitcoin" --dry-run

# Test webhook connection
uv run "$SCRIPT" --test-discord
```

### Step 6 — Report back

Tell the user what was posted to Discord, how many items were found per source, and note any skipped sources (e.g. "YouTube skipped — YOUTUBE_API_KEY not set").
