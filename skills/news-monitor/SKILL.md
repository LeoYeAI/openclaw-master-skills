---
name: buzz
description: Real-time news aggregator with Discord & Telegram push. Manage Jin10, BlockBeats, RSS, X KOLs, Polymarket, OpenNews via REST API.
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    requires:
      bins:
        - node
        - npm
    emoji: "\U0001F4F0"
    os:
      - darwin
      - linux
      - win32
---

# Buzz Skill

Install, run, and manage a real-time news aggregator with Discord & Telegram push notifications. All configuration is done via REST API with hot-reload — no restarts needed.

**Base URL**: `http://localhost:3848` (default, configurable via `dashboard.port`)

## Quick Setup

```bash
git clone https://github.com/zxcnny930/buzz.git
cd buzz
npm install
cp config.example.json config.json
npm start
```

The dashboard is at `http://localhost:3848`, settings page at `/settings.html?lang=en`.

## Authentication

If a dashboard password is set, all `/api/*` endpoints require `?pw=PASSWORD`:

```bash
curl -s "http://localhost:3848/api/config?pw=YOUR_PASSWORD"
```

If password is empty string, no authentication is needed.

**IMPORTANT: All curl examples below omit `?pw=` for brevity. If the server has a password configured, append `?pw=PASSWORD` to every URL.**

Auth failure response (HTTP 401):

```json
{ "ok": false, "error": "Unauthorized" }
```

---

## API Endpoints

### 1. Get Current Config

```bash
curl -s http://localhost:3848/api/config
```

Returns the full configuration JSON. Sensitive fields (apiKey, token, botToken, password) are redacted as `"••••••"` in the response.

### 2. Update Config (Partial, Hot-Reload)

`POST /api/config` accepts partial updates. Only send the sections you want to change.

**Enable Jin10 with 10-second polling:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"jin10": {"enabled": true, "pollIntervalMs": 10000}}'
```

**Disable Polymarket:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"polymarket": {"enabled": false}}'
```

**Set Discord webhook:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"discord": {"webhookUrl": "https://discord.com/api/webhooks/..."}}'
```

**Enable Telegram:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"telegram": {"enabled": true, "botToken": "123456:ABC-DEF", "chatId": "-1001234567890"}}'
```

**Add an RSS source:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"rssFeeds": [{"enabled": true, "name": "CoinDesk", "feedUrl": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml", "pollIntervalMs": 300000, "color": 3447003}]}'
```

> Note: `rssFeeds` is an array — sending it replaces the entire array, not appends.

**Configure OpenNews AI filtering:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"opennews": {"enabled": true, "pollIntervalMs": 60000, "minScore": 70, "signals": ["long"], "coins": ["BTC", "ETH"], "engineTypes": ["news", "listing"]}}'
```

**Configure Polymarket alerts:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"polymarket": {"enabled": true, "minChangePp": 5, "zThreshold": 2.5, "volSpikeThreshold": 2.0, "minLiquidity": 10000, "tagIds": [21, 120], "excludeTagIds": [100639]}}'
```

**Set AI translation model:**

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"grok": {"apiKey": "xai-...", "model": "grok-4.1-fast", "baseUrl": "https://api.x.ai/v1"}}'
```

**Success response:**

```json
{ "ok": true }
```

**Validation error response:**

```json
{
  "ok": false,
  "errors": ["polymarket.zThreshold must be > 0", "dashboard.port must be 1024-65535"]
}
```

### 3. Get Source Status

```bash
curl -s http://localhost:3848/api/status
```

**Response:**

```json
{
  "jin10": { "active": true, "interval": 15000 },
  "blockbeats": { "active": true, "interval": 30000 },
  "polymarket": { "active": true, "interval": 180000 },
  "x6551": { "active": true, "interval": 3600000 },
  "opennews": { "active": false, "interval": 60000 },
  "rss:https://www.blocktempo.com/feed/": { "active": true, "interval": 300000 }
}
```

Each key is a source identifier. RSS sources are prefixed with `rss:` followed by their feed URL.

### 4. Manage KOL Tracking List

**List all tracked accounts:**

```bash
curl -s -X POST http://localhost:3848/api/kols \
  -H "Content-Type: application/json" \
  -d '{"action": "list"}'
```

Response:

```json
{ "ok": true, "kols": ["elonmusk", "VitalikButerin"] }
```

**Add a KOL:**

```bash
curl -s -X POST http://localhost:3848/api/kols \
  -H "Content-Type: application/json" \
  -d '{"action": "add", "username": "caboronli"}'
```

Response:

```json
{ "ok": true, "kols": ["elonmusk", "VitalikButerin", "caboronli"] }
```

If already exists:

```json
{ "ok": true, "message": "already exists", "kols": ["elonmusk", "VitalikButerin", "caboronli"] }
```

**Remove a KOL:**

```bash
curl -s -X POST http://localhost:3848/api/kols \
  -H "Content-Type: application/json" \
  -d '{"action": "remove", "username": "elonmusk"}'
```

Response:

```json
{ "ok": true, "kols": ["VitalikButerin", "caboronli"] }
```

If username not found:

```json
{ "ok": false, "error": "not found", "kols": ["VitalikButerin", "caboronli"] }
```

> Username strings are trimmed and `@` prefix is automatically stripped.

### 5. Health Check

```bash
curl -s http://localhost:3848/health
```

Response:

```json
{ "ok": true, "clients": 2, "history": 150 }
```

- `clients`: number of active SSE connections
- `history`: number of events in memory

No authentication required.

### 6. Server-Sent Events (Live Stream)

```bash
curl -s -N http://localhost:3848/sse
```

Streams real-time news events as SSE. On connection, all historical events are sent first, then new events arrive in real-time. Heartbeat every 15 seconds.

---

## Full Configuration Schema

### jin10

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `true` | | Enable Jin10 flash news |
| `pollIntervalMs` | number | `15000` | >= 5000 | Poll interval in milliseconds |
| `onlyImportant` | boolean | `true` | | Only push important items |

### blockbeats

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `true` | | Enable BlockBeats |
| `pollIntervalMs` | number | `30000` | >= 5000 | Poll interval |
| `onlyImportant` | boolean | `true` | | Only push important items |
| `lang` | string | `"cht"` | | Language: `cht` (Trad. Chinese), `en`, `cn` (Simp. Chinese) |

### rssFeeds (array)

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `true` | | Enable this feed |
| `name` | string | | | Display name |
| `feedUrl` | string | | must start with `http(s)://` | RSS/Atom feed URL |
| `pollIntervalMs` | number | `300000` | >= 5000 | Poll interval |
| `color` | number | | | Discord embed color as integer (e.g. `3447003` = `#3498DB`) |

### x6551

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `true` | | Enable X tweet monitoring |
| `apiBase` | string | `"https://ai.6551.io"` | must start with `http(s)://` | API base URL |
| `token` | string | | | API token from [6551.io/mcp](https://6551.io/mcp) |
| `pollIntervalMs` | number | `3600000` | >= 5000 | Poll interval |
| `kolSyncIntervalMs` | number | `300000` | | KOL list refresh interval |
| `kols` | string[] | `[]` | | Usernames to monitor (without @) |

### opennews

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `false` | | Enable OpenNews AI news |
| `pollIntervalMs` | number | `60000` | >= 5000 | Poll interval |
| `minScore` | number | `70` | 0-100 | Minimum AI score to push |
| `signals` | string[] | `[]` | | Filter: `"long"`, `"short"`, `"neutral"` (empty = all) |
| `coins` | string[] | `[]` | | Filter by coin symbols, e.g. `["BTC","ETH"]` (empty = all). **OpenNews-only** — other sources (Jin10, BlockBeats, RSS, Polymarket) cannot be coin-filtered. |
| `engineTypes` | string[] | `[]` | | Filter: `"news"`, `"listing"`, `"onchain"`, `"meme"`, `"market"` (empty = all). **OpenNews-only.** |

### polymarket

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `enabled` | boolean | `true` | | Enable Polymarket monitoring |
| `pollIntervalMs` | number | `180000` | >= 5000 | Price check interval |
| `marketRefreshMs` | number | `600000` | >= 60000 | Market list refresh interval |
| `minChangePp` | number | `5` | | Min percentage point change to alert |
| `zThreshold` | number | `2.5` | > 0 | Z-Score anomaly threshold (0 = off) |
| `volSpikeThreshold` | number | `2.0` | > 0 | Volume spike multiplier |
| `minLiquidity` | number | `10000` | >= 0 | Min market liquidity in USD |
| `rollingWindowMinutes` | number | `30` | | Window for price change calculation |
| `cooldownMs` | number | `900000` | >= 60000 | Min interval before re-alerting same market |
| `tagIds` | number[] | `[]` | | Only track these categories (empty = all) |
| `excludeTagIds` | number[] | `[]` | | Exclude these categories |

**Polymarket Tag IDs:**

| ID | Category |
|----|----------|
| 21 | Crypto |
| 2 | Politics |
| 120 | Finance |
| 1401 | Tech |
| 596 | Culture |
| 100265 | Geopolitics |
| 100639 | Sports |

### grok (AI Translation)

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `apiKey` | string | | | API key for translation |
| `model` | string | `"grok-4.1-fast"` | | Model name (any OpenAI-compatible) |
| `baseUrl` | string | `"https://api.x.ai/v1"` | must start with `http(s)://` | API endpoint |

Supported models: `grok-4.1-fast`, `gpt-4o-mini`, `gpt-4.1-mini`, `claude-sonnet-4-6`, `claude-haiku-4-5-20251001`, `gemini-2.0-flash`, or any OpenAI-compatible model.

### discord

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `webhookUrl` | string | `""` | Discord webhook URL (simple mode) |
| `botToken` | string | `""` | Discord bot token (advanced mode) |
| `channelId` | string | `""` | Discord channel ID (required for bot mode) |

Use **either** `webhookUrl` **or** `botToken` + `channelId`, not both.

### telegram

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | boolean | `false` | Enable Telegram notifications |
| `botToken` | string | `""` | Telegram bot token from @BotFather |
| `chatId` | string | `""` | Target chat/group/channel ID |

### dashboard

| Field | Type | Default | Validation | Description |
|-------|------|---------|------------|-------------|
| `port` | number | `3848` | 1024-65535 | HTTP server port (restart required) |
| `password` | string | `""` | | Access password (empty = no auth) |

---

## Common Workflows

### Check what's currently running

```bash
curl -s http://localhost:3848/api/status | jq 'to_entries[] | select(.value.active) | .key'
```

### Enable a source and verify

```bash
# Enable Jin10
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"jin10": {"enabled": true, "pollIntervalMs": 15000}}'

# Verify it's active
curl -s http://localhost:3848/api/status | jq '.jin10'
```

### Set up Discord + Telegram dual push

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{
    "discord": {"webhookUrl": "https://discord.com/api/webhooks/..."},
    "telegram": {"enabled": true, "botToken": "123456:ABC-DEF", "chatId": "-1001234567890"}
  }'
```

### Add a new RSS feed (without losing existing ones)

**IMPORTANT:** `rssFeeds` is an array. POSTing it replaces the entire list. You must GET first, append, then POST back.

**Step 1 — Get current feeds:**

```bash
curl -s http://localhost:3848/api/config | jq '.rssFeeds'
```

**Step 2 — POST the full array with the new feed appended:**

```bash
# Example: existing feeds are BlockTempo and PTS News, adding CoinDesk
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"rssFeeds": [
    {"enabled": true, "name": "BlockTempo", "feedUrl": "https://www.blocktempo.com/feed/", "pollIntervalMs": 300000, "color": 16746496},
    {"enabled": true, "name": "PTS News", "feedUrl": "https://news.pts.org.tw/xml/newsfeed.xml", "pollIntervalMs": 300000, "color": 3447003},
    {"enabled": true, "name": "CoinDesk", "feedUrl": "https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml", "pollIntervalMs": 300000, "color": 2067276}
  ]}'
```

> Same pattern applies when removing or editing an RSS feed — always send the complete updated array.

### Remove an RSS feed

GET current list, remove the target, POST back the remaining array.

```bash
# Get current feeds, then POST without the one you want to remove
curl -s http://localhost:3848/api/config | jq '.rssFeeds'
# POST back the array minus the removed feed
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"rssFeeds": [
    {"enabled": true, "name": "BlockTempo", "feedUrl": "https://www.blocktempo.com/feed/", "pollIntervalMs": 300000, "color": 16746496}
  ]}'
```

### Add an item to any array field (general pattern)

When the user says "also add X", always follow GET → modify → POST:

```bash
# Step 1: GET current value
CURRENT=$(curl -s http://localhost:3848/api/config | jq '.polymarket.tagIds')
# Example result: [21, 120]

# Step 2: Append and POST back
# Adding Sports (100639) to existing [21, 120]
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"polymarket": {"tagIds": [21, 120, 100639]}}'
```

Same pattern applies to `opennews.signals`, `opennews.coins`, `opennews.engineTypes`, `polymarket.excludeTagIds`.

### Monitor high-impact crypto news only

```bash
curl -s -X POST http://localhost:3848/api/config \
  -H "Content-Type: application/json" \
  -d '{"opennews": {"enabled": true, "minScore": 80, "signals": ["long", "short"], "coins": ["BTC", "ETH", "SOL"], "engineTypes": ["news", "listing"]}}'
```

### Track new KOL and verify

```bash
# Add
curl -s -X POST http://localhost:3848/api/kols \
  -H "Content-Type: application/json" \
  -d '{"action": "add", "username": "VitalikButerin"}'

# List all
curl -s -X POST http://localhost:3848/api/kols \
  -H "Content-Type: application/json" \
  -d '{"action": "list"}'
```

## Important Rules

### Array fields are REPLACED, never merged

The config deep-merge only merges plain objects. **All array fields are completely replaced** when you POST them. If the user wants to **add** an item to an existing list, you MUST GET the current config first, modify the array, then POST back.

**Array fields that require GET-first when adding/removing items:**

| Field | Example "add" intent |
|-------|---------------------|
| `rssFeeds` | "Add CoinDesk RSS" — GET current feeds, append, POST full array |
| `polymarket.tagIds` | "Also track Sports" — GET current tagIds, append `100639`, POST |
| `polymarket.excludeTagIds` | "Also exclude Culture" — same pattern |
| `opennews.signals` | "Also show long signals" — GET, append `"long"`, POST |
| `opennews.coins` | "Also track SOL" — GET, append `"SOL"`, POST |
| `opennews.engineTypes` | "Also include listings" — GET, append `"listing"`, POST |

**Exception — KOLs have a safe endpoint:** Use `POST /api/kols` with `action: "add"` or `"remove"`. This does NOT require GET-first. Do NOT modify `x6551.kols` via `POST /api/config` — use the dedicated endpoint instead.

**When the user says "set to" (replace entire list) instead of "add"**, you can POST directly without GET-first. Example: "I only want Crypto and Finance" → `{"polymarket": {"tagIds": [21, 120]}}` is fine.

### Other rules

1. **Object sections support partial update.** You can POST just `{"jin10": {"enabled": false}}` without affecting other jin10 fields or other sections.
2. **Sensitive fields are redacted** in GET responses as `"••••••"`. When POSTing, redacted values are automatically preserved (not overwritten).
3. **All changes are hot-reloaded** — no restart needed, except `dashboard.port`.
4. The `x6551.token` is shared between X tweet monitor and OpenNews.
5. Get your 6551 API token at https://6551.io/mcp

## Error Responses

| HTTP Status | Body | Cause |
|-------------|------|-------|
| 401 | `{ "ok": false, "error": "Unauthorized" }` | Missing or wrong `?pw=` password |
| 400 | `{ "ok": false, "errors": [...] }` | Validation failed (array of error strings) |
| 400 | `{ "ok": false, "error": "Invalid JSON" }` | Malformed request body |
| 404 | `{ "error": "Not found" }` | Unknown API route |
