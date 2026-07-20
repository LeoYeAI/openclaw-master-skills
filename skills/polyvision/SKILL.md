---
name: polyvision
description: Analyze Polymarket prediction market wallets — get copy trading scores (1-10), P&L, win rate, risk metrics (Sharpe ratio, Sortino ratio, max drawdown), red flags, position sizing, market category performance, recent performance (7d/30d/90d), streak analysis, individual open positions with entry/current prices, and recent trade history. Also discover elite traders via daily leaderboard, hot bets from top traders, and random wallet discovery. Connects via MCP server or REST API. Use when evaluating whether to copy trade a Polymarket trader, comparing multiple wallets side-by-side, screening for elite prediction market performers, checking if a wallet has bot-like trading patterns or hidden losses, researching a trader's risk profile, viewing recent trade activity, finding today's best open bets, or discovering new traders to follow. Free API key, no daily limits, 6-hour result caching.
homepage: https://polyvisionx.com
license: MIT
disable-model-invocation: true
metadata: {"clawdis":{"emoji":"📊","primaryEnv":"POLYVISION_API_KEY","requires":{"env":["POLYVISION_API_KEY"]}}}
---

# PolyVision — Polymarket Wallet Analyzer

PolyVision analyzes Polymarket prediction market wallets and returns a comprehensive trading profile: copy trading score (1-10), P&L breakdown, win rate, risk metrics (Sharpe ratio, Sortino ratio, max drawdown), position sizing consistency, market category performance, recent performance windows (7d/30d/90d), streak analysis, red flags, and individual open positions with entry/current prices. It also provides a daily leaderboard of top-ranked traders, hot bets (most profitable open positions from top traders), and random elite wallet discovery. Use it to evaluate whether a trader is worth copy trading, compare multiple wallets, screen for elite performers, find today's best bets, or discover new traders to follow.

## When to Use
- User mentions a Polymarket wallet address (0x...)
- User asks about copy trading, trader evaluation, or wallet scoring
- User wants to compare prediction market traders or screen for elite performers
- User asks about a trader's risk profile, red flags, or trading patterns
- User asks what bets top traders are making, or wants today's best open positions
- User wants to discover or find new Polymarket traders to follow
- User asks about a daily leaderboard or top traders ranking
- User wants to see a trader's individual open positions with P&L details
- User asks about a trader's recent trades, trade history, or latest activity
- User asks for copy trading strategy recommendations or optimal settings
- User wants to know what risk profile or parameters to use for copy trading

## When NOT to Use
- General crypto price queries (not Polymarket-specific)
- Placing trades or executing orders (PolyVision is read-only analysis)
- Non-Polymarket wallet lookups (Ethereum DeFi, NFTs, etc.)

## Setup: MCP Server (Recommended)

Add to your MCP client configuration (e.g. `claude_desktop_config.json`, Cursor, Windsurf):

```json
{
  "mcpServers": {
    "polyvision": {
      "type": "streamable-http",
      "url": "https://api.polyvisionx.com/mcp",
      "headers": {
        "Authorization": "Bearer ${POLYVISION_API_KEY}"
      }
    }
  }
}
```

## Setup: Get an API Key

Get a free API key (no daily limits) from the Telegram bot:

1. Open the [PolyVision bot](https://t.me/PolyVisionBot) on Telegram
2. Run `/apikey` to generate your key
3. Copy the `pv_live_...` key (shown only once, store it securely)

Set it as an environment variable:

```bash
export POLYVISION_API_KEY="pv_live_abc123..."
```

Full API docs: https://polyvisionx.com/docs

## MCP Tools Reference

### `analyze_wallet`

Run a comprehensive Polymarket wallet analysis.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `wallet_address` | string | Yes | — | Ethereum address (42 chars, starts with `0x`) |
| `mode` | string | No | `"quick"` | `"quick"` (~5s) or `"full"` (~30-60s with timing data) |

**Returns:** Full analysis dict with P&L, win rate, risk metrics, categories, copy trading score (1-10), red flags, and usage info. Results are cached for 6 hours — cache hits are instant. See `references/response-schemas.md` for the complete field reference.

**Timing:** Quick mode ~5s, full mode ~30-60s. Cached responses are instant.

### `get_score`

Get a compact copy-trading score for a wallet. Shares the same cache as `analyze_wallet`.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `wallet_address` | string | Yes | Ethereum address (42 chars, starts with `0x`) |

**Returns:** Score (1-10), recommendation, tier (green/yellow/orange/red), total P&L, win rate, trade count, Sharpe ratio, red flags, cache status, and usage info.

**Timing:** ~5s fresh, instant if cached.

### `get_hot_bets`

Get today's hot bets from top traders. Returns the most profitable open positions from top-ranked Polymarket traders, sourced from the daily strategy report.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `limit` | integer | No | `20` | Maximum number of bets to return |
| `sort_by` | string | No | `"rank"` | `"rank"` (default) or `"pnl"` |

**Returns:** Scan date, total count, and list of hot bets — each with trader info (wallet, username, score, win rate), market details (title, slug, outcome), pricing (entry price, current price, current value), P&L (unrealized P&L, percent), resolution info (end date, days until resolution), entry timing (entry date, days since entry, hold hours), and Polymarket URL. See `references/response-schemas.md` for the complete field reference.

### `get_leaderboard`

Get the daily top-10 leaderboard of ranked Polymarket traders. Synced daily from the scan pipeline.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `sort_by` | string | No | `"rank"` | `"rank"` (default), `"score"`, or `"pnl"` |

**Returns:** Scan date, total count, and list of leaderboard entries — each with wallet address, username, total P&L, volume, ROI%, win rate, risk metrics (Sharpe ratio, max drawdown, profit factor), copy score (1-10), recommendation, tier (green/yellow/orange/red), red flags, track record days, last trade date, and category percentages (politics, crypto, sports). See `references/response-schemas.md` for the complete field reference.

### `get_strategy`

Get pre-computed copy trading strategy profiles. Returns 3 risk profiles (conservative, moderate, aggressive) with backtested parameters and expected metrics, updated daily.

**Parameters:** None

**Returns:** Scan date, total count, and list of strategy profiles — each with parameters (price range, min score, max trades/day, min trade size, position sizing method), backtest results (win rate, ROI, Sharpe ratio, max drawdown, profit factor, EV/trade, total P&L), cost-adjusted results, and a plain-English description. See `references/response-schemas.md` for the complete field reference.

### `get_recent_trades`

Get recent trades for a Polymarket wallet. Returns trade history with side, size, price, market title, and timestamps.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `wallet_address` | string | Yes | — | Ethereum address (42 chars, starts with `0x`) |
| `since` | integer | No | — | Unix timestamp — only return trades after this time |
| `limit` | integer | No | `50` | Max trades to return (1-100) |

**Returns:** Dict with `wallet_address`, `since`, `count`, and `trades` list — each trade with side (BUY/SELL), size, price, timestamp, market title, outcome, slug, and transaction hash. See `references/response-schemas.md` for the complete field reference.

### `discover_wallet`

Discover a random elite trader from the curated wallet pool (250+). Returns a random wallet address each call — use `analyze_wallet` or `get_score` to investigate it.

**Parameters:** None

**Returns:** `{ "wallet_address": "0x...", "pool_size": 250, "message": "..." }`

### `check_quota`

Check your usage statistics. Does not consume quota.

**Parameters:** None

**Returns:** `{ "used_today": <int>, "tier": "api" }`

API/MCP access has no daily limits — usage is tracked for analytics only.

### `get_portfolio`

Get the user's tracked wallet portfolio with scores and nicknames.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `page` | integer | No | `0` | Page number (0-indexed) |
| `limit` | integer | No | `10` | Results per page (1-50) |

**Returns:** Dict with `total_count`, `page`, `limit`, and `wallets` list — each with wallet address, nickname, score, last analyzed date, and notifications status. See `references/response-schemas.md` for the complete field reference.

### `add_to_portfolio`

Add a wallet to the user's portfolio for tracking.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `wallet_address` | string | Yes | — | Ethereum address (42 chars, starts with `0x`) |
| `nickname` | string | No | — | Display name (defaults to first 10 chars of address) |

**Returns:** Dict with `wallet_address`, `nickname`, and `message` on success, or dict with `error` key on failure (duplicate, limit reached).

**Limits:** Free users: 3 wallets. Premium users: 20 wallets.

### `remove_from_portfolio`

Remove a wallet from the user's portfolio.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `wallet_address` | string | Yes | Ethereum address to remove |

**Returns:** Dict with `wallet_address` and `message` on success, or dict with `error` key if wallet not found.

### `health`

Check system health.

**Parameters:** None

**Returns:** `{ "status": "ok" }` or `{ "status": "degraded" }`

## Score Tiers

| Tier | Score Range | Recommendation | Meaning |
|------|------------|----------------|---------|
| Green | 8.0 – 10.0 | Strong Copy | Consistently profitable, good risk management, strong track record |
| Yellow | 6.0 – 7.9 | Moderate Copy | Decent performance with some concerns, proceed with caution |
| Orange | 4.0 – 5.9 | Risky Copy | Mixed results, significant red flags, high risk |
| Red | 0.0 – 3.9 | Don't Copy | Poor performance, major red flags, likely to lose money |

## Decision Table

| User Intent | Tool | Mode | Why |
|-------------|------|------|-----|
| "Should I copy this trader?" | `get_score` | — | Quick yes/no with score + red flags |
| "Deep dive on this wallet" | `analyze_wallet` | `full` | Complete analysis with timing data |
| "Quick check on a wallet" | `analyze_wallet` | `quick` | Full analysis without activity timing |
| "What are this trader's open positions?" | `analyze_wallet` | `quick` | `open_positions_detail` in analysis response |
| "Compare two traders" | `get_score` x2 | — | Side-by-side scores for fast comparison |
| "What categories does this trader focus on?" | `analyze_wallet` | `quick` | Category breakdown in analysis |
| "What are the best bets right now?" | `get_hot_bets` | — | Today's most profitable open positions from top traders |
| "What bets are top traders making?" | `get_hot_bets` | sort=`pnl` | Hot bets sorted by P&L |
| "Who are the top traders today?" | `get_leaderboard` | — | Daily top-10 ranked traders |
| "Find me a good trader to follow" | `discover_wallet` | — | Random elite wallet, then `get_score` or `analyze_wallet` |
| "What trades has this wallet made recently?" | `get_recent_trades` | — | Recent trade history for a wallet |
| "What strategy should I use for copy trading?" | `get_strategy` | — | 3 risk profiles with backtested parameters |
| "What's the safest way to copy trade?" | `get_strategy` | — | Conservative profile with low drawdown |
| "Discover new traders" | `discover_wallet` x3 | — | Multiple random picks to explore |
| "Show my tracked wallets" | `get_portfolio` | — | View portfolio with scores and nicknames |
| "Add this wallet to my portfolio" | `add_to_portfolio` | — | Track a wallet with optional nickname |
| "Remove wallet from portfolio" | `remove_from_portfolio` | — | Stop tracking a wallet |
| "Is the system up?" | `health` | — | System status check |
| "How many analyses have I run?" | `check_quota` | — | Usage stats (no limits enforced) |

## Red Flag Reference

Red flags are returned as a list of strings. Here's what each one means:

| Red Flag | Trigger | Severity |
|----------|---------|----------|
| Low win rate | Win rate below 40% | High |
| Large single loss | Single worst trade exceeds 50% of total P&L | Medium |
| Overall unprofitable | Net P&L is negative | High |
| Limited track record | Fewer than 10 closed positions | Medium |
| Inactive | No trades in 30+ days | Low |
| BOT ALERT | Median trade duration under 5 minutes | High |
| Very fast trading | Median trade duration under 30 minutes | Medium |
| LOSS HIDING | 70%+ of open positions underwater (5+ open) | High |
| Open positions losing | 50%+ of open positions underwater (3+ open) | Medium |
| No major red flags detected | No concerning patterns found | None |

## REST API (Alternative)

For agents that cannot use MCP, all tools are available as REST endpoints at `https://api.polyvisionx.com`. Most endpoints require Bearer token authentication (exceptions noted below).

Interactive docs and the OpenAPI spec are available at:
- **Swagger UI:** `https://api.polyvisionx.com/docs`
- **OpenAPI JSON:** `https://api.polyvisionx.com/openapi.json`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /v1/auth/me` | GET | Get current user info and usage stats |
| `GET /v1/analyze/{wallet_address}?mode=quick` | GET | Full wallet analysis (includes `open_positions_detail`) |
| `GET /v1/score/{wallet_address}` | GET | Compact copy-trading score |
| `GET /v1/hot-bets?page=0&limit=20&sort_by=rank` | GET | Today's hot bets from top traders |
| `GET /v1/leaderboard?sort_by=rank` | GET | Daily top-10 leaderboard |
| `GET /v1/strategy` | GET | Pre-computed copy trading strategy profiles (3 risk levels) |
| `GET /v1/trades/{wallet_address}?since=&limit=50` | GET | Recent trades for a wallet |
| `GET /v1/discover` | GET | Discover a random elite trader |
| `GET /v1/portfolio?page=0&limit=10` | GET | Get your tracked wallet portfolio |
| `POST /v1/portfolio` | POST | Add a wallet to your portfolio (JSON body: `wallet_address`, `nickname`) |
| `DELETE /v1/portfolio/{wallet_address}` | DELETE | Remove a wallet from your portfolio |
| `GET /health` | GET | Health check (no auth required) |

### Example: Analyze a wallet

```bash
curl -s https://api.polyvisionx.com/v1/analyze/0x1234...abcd?mode=quick \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

### Example: Get a score

```bash
curl -s https://api.polyvisionx.com/v1/score/0x1234...abcd \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

### Example: Get hot bets

```bash
curl -s https://api.polyvisionx.com/v1/hot-bets?sort_by=pnl \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

### Example: Get leaderboard

```bash
curl -s https://api.polyvisionx.com/v1/leaderboard \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

### Example: Get strategy profiles

```bash
curl -s https://api.polyvisionx.com/v1/strategy \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

### Example: Discover a random trader

```bash
curl -s https://api.polyvisionx.com/v1/discover \
  -H "Authorization: Bearer $POLYVISION_API_KEY" | jq .
```

## Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 400 | Invalid wallet address (must be 42-char hex starting with `0x`) | Fix the address format |
| 401 | Invalid or inactive API key | Get a key from the [PolyVision Telegram bot](https://t.me/PolyVisionBot) via `/apikey` |
| 429 | Rate limited | Wait and retry — Polymarket API has upstream limits |
| 503 | System at capacity (all analysis slots in use) | Retry in 30-60 seconds |
| 502 | Upstream Polymarket API error | Retry — the upstream data API may be temporarily unavailable |
| 504 | Analysis timed out | Retry — the wallet may have extensive history |
