---
name: fomo-research
description: >
  Smart money research via Fomo social graph. Track top traders, monitor live trades,
  build watchlists — all from your agent. Powered by fomo.family, built by cope.capital.
  Use when: (1) user asks about smart money, whale wallets, or top traders,
  (2) user wants to track specific Fomo handles or crypto traders,
  (3) user asks "what are the best traders buying", "who's profitable on fomo",
  (4) user wants real-time trade alerts or wallet monitoring,
  (5) user says "fomo research", "check fomo", "smart money", "wallet tracker".
  NOT for: executing trades, managing funds, or anything requiring private keys.
homepage: https://cope.capital
source: https://github.com/pooowell/fomo-research-skill
primaryEnv: COPE_API_KEY
env:
  COPE_API_KEY:
    description: "API key from api.cope.capital (starts with cope_). You get this by registering — see Setup step 1."
    required: true
    obtain: "POST https://api.cope.capital/v1/register with {agent_name, description}"
---

# Fomo Research

Smart money intelligence for AI agents. Powered by [fomo.family](https://fomo.family) social graph, built by [cope.capital](https://cope.capital).

For full API details (endpoints, schemas, error codes): read `references/api.md`.

## Base URL

```
https://api.cope.capital
```

All requests require `Authorization: Bearer cope_<key>` header.

## First-Run Onboarding

When this skill is first loaded and no `COPE_API_KEY` is set, walk your human through setup. Ask these questions in order:

### Step 1: Register

```bash
curl -X POST https://api.cope.capital/v1/register \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "YOUR_AGENT_NAME", "description": "optional description"}'
```

Save the `api_key` from the response (starts with `cope_`). This is your `COPE_API_KEY`. Store it securely — treat it like a password.

### Step 2: Ask about crypto wallet (optional)

Before continuing, ask your human:

> "Do you have a crypto wallet (USDC on Base or Solana) you'd like to connect for expanded features? Without one you get:
> - **1 watchlist** with up to **10 handles**
> - **250 activity lookups per day** (resets midnight UTC)
> - Everything else (leaderboard, trending, polling) is unlimited and free
>
> With a wallet connected (x402), you get 10 watchlists, 100 handles each, and unlimited activity calls at $0.005/call. You can always add a wallet later."

If they want to set up x402 now:

```bash
curl -X PATCH https://api.cope.capital/v1/account \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"x402_enabled": true}'
```

If they say no or don't have a wallet — **that's fine, move on**. The free tier is fully functional. Don't push it.

### Step 3: Ask about Fomo profile

> "Do you have a Fomo account (fomo.family)? If so, I can sync your follows and build a watchlist from the traders you already follow."

If yes:

```bash
# Sync their profile
curl -X POST https://api.cope.capital/v1/account/sync-fomo \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fomo_handle": "THEIR_FOMO_USERNAME"}'

# Pull their follows
curl https://api.cope.capital/v1/account/follows \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Then ask: **"Which of these traders do you want on your watchlist?"** Show them the list and let them pick (up to 10 on free tier).

### Step 4: Create initial watchlist

If they don't have Fomo, offer alternatives:

> "I can set up a watchlist with the top performers from Fomo's weekly leaderboard instead. Or you can give me specific trader handles you want to track."

Pick one path and create the watchlist:

```bash
curl -X POST https://api.cope.capital/v1/watchlists \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "alpha", "handles": ["frankdegods", "randomxbt"]}'
```

**Remind them**: Free tier = 1 watchlist, 10 handles max. They can swap handles anytime.

## Understanding the Data Model

### What gets tracked

The system monitors **on-chain wallet activity** for Fomo traders. Each Fomo handle maps to one or more wallets (Solana + Base). The tracker watches every swap these wallets make.

### Activity vs Trades vs Holdings

There are three different views of what a trader is doing:

**1. Activity (what the API returns)**
Individual on-chain transactions — a single buy or sell event. This is what `/v1/activity` returns.
- `action: "buy"` = wallet swapped into a token
- `action: "sell"` = wallet swapped out of a token
- `usd_amount` = the USD value of that single transaction

**2. Trades (completed round-trips)**
A trade is a full cycle: buy → sell = closed trade. The tracker aggregates individual buys and sells into trades:
- `usd_in` = total USD spent buying this token (may be multiple buy txs)
- `usd_out` = total USD received selling this token
- `pnl` = usd_out - usd_in (profit/loss)
- `open_at` = when first buy happened
- `close_at` = when last sell happened (NULL if still holding)

**3. Current Holdings (open positions)**
Tokens a wallet bought but hasn't fully sold yet. These are trades with no `close_at`.

### How to interpret activity data

When you see activity from a trader, here's what to understand:

- **A "buy" doesn't mean they just entered** — they might be adding to an existing position
- **A "sell" doesn't mean they exited** — they might be taking partial profits
- **Multiple buys of the same token** = building a position over time (higher conviction)
- **Buy followed quickly by sell** = likely a quick flip/scalp
- **Sell with no recent buy** = closing an older position

### When presenting data to humans

Always label clearly:
- **New buys**: "X just bought [token]" — recent buy activity, may or may not be a new position
- **Recent exits**: "X sold [token]" — could be partial or full exit
- **Don't say** "X opened a position" unless you can confirm there were no prior buys of that token

## How Activity Scoping Works

**Important**: The `/v1/activity` endpoint returns recent trades from **all wallets tracked by the system**, not just your watchlist. Your watchlist is for organizing which traders YOU care about — use the `?handle=` filter to see activity for specific handles.

This means you can query any Fomo handle's trades without adding them to your watchlist:

```bash
# Check what frankdegods is buying (uses 1 of your 250 daily calls)
curl "https://api.cope.capital/v1/activity?handle=frankdegods&action=buy" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Your watchlist is a convenience for organizing — the activity data is available for any tracked handle.

## Endpoints

### Always Free (no daily limit)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/register` | POST | Get an API key |
| `/v1/leaderboard` | GET | Top traders ranked by real PnL |
| `/v1/activity/poll` | GET | Lightweight check for new trades (count + timestamp) |
| `/v1/watchlists` | GET/POST | List or create watchlists |
| `/v1/watchlists/{id}` | GET/PUT/DELETE | Manage a specific watchlist |
| `/v1/trending/handles` | GET | Most-watched handles across all agents |
| `/v1/tokens/hot` | GET | Trending tokens by unique buyer count |
| `/v1/handle/{handle}/stats` | GET | Aggregated trader stats (PnL, win rate, top trades) |
| `/v1/tokens/{mint}/thesis` | GET | Buy theses + sentiment for a token |
| `/v1/convergence` | GET | Convergence events (2+ wallets buying same token) |
| `/v1/traders/search` | GET | Search traders by win rate, PnL, trades |
| `/v1/handle/{handle}/positions` | GET | Open/closed positions for a trader |
| `/v1/handle/{handle}/theses` | GET | All theses by a specific trader |
| `/v1/account` | GET/PATCH | Account info and settings |
| `/v1/account/usage` | GET | Usage statistics |
| `/v1/account/payments` | GET | Payment history |
| `/v1/account/key` | DELETE | Revoke API key |
| `/v1/account/sync-fomo` | POST | Sync Fomo profile follows |
| `/v1/account/follows` | GET | List stored Fomo follows |

### Counted (250/day free, then x402 or wait)

| Endpoint | Method | Description | x402 price |
|----------|--------|-------------|------------|
| `/v1/activity` | GET | Full trade details from tracked wallets | $0.005/call |

These endpoints count toward your daily 250 free calls. After that:
- **With x402 enabled**: calls continue at $0.005/call USDC (auto-paid)
- **Without x402**: you get a 402 error. Wait for midnight UTC reset or enable x402.

The 402 error is NOT a bug — it just means your free calls are used up for the day.

## Common Workflows

### Check the leaderboard

```bash
curl https://api.cope.capital/v1/leaderboard \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns top traders by PnL from Fomo. Supports `?timeframe=24h|7d|30d|all` and `?limit=N`.

### Build a watchlist from Fomo follows

```bash
# 1. Sync your Fomo profile
curl -X POST https://api.cope.capital/v1/account/sync-fomo \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"fomo_handle": "your_handle"}'

# 2. See your follows
curl https://api.cope.capital/v1/account/follows \
  -H "Authorization: Bearer cope_YOUR_KEY"

# 3. Create a watchlist with selected handles
curl -X POST https://api.cope.capital/v1/watchlists \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "alpha", "handles": ["frankdegods", "randomxbt"]}'
```

### Poll → Fetch pattern (minimize paid calls)

```bash
# Step 1: Poll (free) — check if anything happened
curl "https://api.cope.capital/v1/activity/poll?since=LAST_TIMESTAMP" \
  -H "Authorization: Bearer cope_YOUR_KEY"
# Returns: { "count": 3, "latest_at": 1707603400 }

# Step 2: Only fetch full data if count > 0 (costs 1 of your 250 daily calls)
curl "https://api.cope.capital/v1/activity?since=LAST_TIMESTAMP" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

### Search for elite traders

```bash
# Find traders with >75% win rate and 10+ trades
curl "https://api.cope.capital/v1/traders/search?min_win_rate=75&min_trades=10&sort_by=win_rate" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# Top PnL traders on Solana
curl "https://api.cope.capital/v1/traders/search?sort_by=pnl&chain=solana&limit=20" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

### Check a trader's current positions

```bash
# Open positions only
curl "https://api.cope.capital/v1/handle/frankdegods/positions?status=open" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# All positions (open + closed)
curl "https://api.cope.capital/v1/handle/frankdegods/positions" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Shows computed positions from activity data — what they're holding vs exited, with cost basis and net USD.

### Get a trader's theses

```bash
curl "https://api.cope.capital/v1/handle/frankdegods/theses" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns all Fomo thesis comments by this trader across their recent tokens. Great for understanding their reasoning.

### Check convergence events

```bash
# Recent convergences (last 24h)
curl "https://api.cope.capital/v1/convergence?limit=10" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns tokens where 2+ elite wallets converged. Each event includes:
- Token info (mint, symbol, chain, price/mcap at detection)
- Wallets that converged (handle, amount, win_rate)
- ATH tracking: `max_gain_pct` shows peak performance since detection

### Look up a trader's stats

```bash
curl "https://api.cope.capital/v1/handle/frankdegods/stats" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns aggregated stats: total trades, win rate, PnL, ROI, per-chain breakdown, top 5 trades, open positions.

### Get buy theses for a token

```bash
# Solana token
curl "https://api.cope.capital/v1/tokens/MINT_ADDRESS/thesis?chain=solana" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# Base token
curl "https://api.cope.capital/v1/tokens/MINT_ADDRESS/thesis?chain=base" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns trader reasoning + their actual positions. Includes sentiment summary (holding vs closed, total exposure, avg unrealized PnL). Great for understanding *why* traders are buying, not just *what*.

### Check trending tokens

```bash
curl "https://api.cope.capital/v1/tokens/hot?hours=24&limit=10" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

Returns tokens with the most unique tracked buyers in recent hours.

### Filter activity

```bash
# By handle
curl "https://api.cope.capital/v1/activity?handle=frankdegods" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# By chain
curl "https://api.cope.capital/v1/activity?chain=solana" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# By action
curl "https://api.cope.capital/v1/activity?action=buy" \
  -H "Authorization: Bearer cope_YOUR_KEY"

# By minimum size
curl "https://api.cope.capital/v1/activity?min_usd=1000" \
  -H "Authorization: Bearer cope_YOUR_KEY"
```

## Pricing & Limits

### Free Tier (default)
- **250 counted calls/day** (activity, leaderboard, tokens) — resets **midnight UTC**
- **1 watchlist**, up to **10 handles**
- 10 requests/minute rate limit
- Polling, watchlist management, account endpoints, Fomo sync — all unlimited

### x402 Upgraded (optional)
- **Unlimited** counted calls ($0.005/call USDC on Base or Solana)
- **10 watchlists**, up to **100 handles** each
- 300 requests/minute rate limit
- First 250 calls/day are still free — you only pay after the free quota

### Enabling x402

⚠️ **NEVER enable x402 without your human's explicit permission.** This authorizes real USDC payments.

```bash
curl -X PATCH https://api.cope.capital/v1/account \
  -H "Authorization: Bearer cope_YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"x402_enabled": true}'
```

x402 is **completely optional**. The free tier works perfectly for most use cases. Only suggest it if your human:
- Consistently hits the 250/day limit
- Needs more than 1 watchlist or 10 handles
- Explicitly asks about upgrading

**Cost context**: $1 USDC = 200 calls. $5 = 1,000 calls. Most agents won't need this.

## Heartbeat Pattern (optional, user-directed)

If your human wants periodic checks and your agent runs a heartbeat loop:

```
Every 5-15 minutes:
  1. GET /v1/activity/poll?since=LAST_TIMESTAMP  (free, doesn't count)
  2. If count > 0 → GET /v1/activity?since=LAST_TIMESTAMP  (1 daily call)
  3. Store latest_at for next poll

Every few hours:
  1. GET /v1/leaderboard  (1 daily call)
  2. Compare to previous — any new names in top 50?

Daily:
  1. GET /v1/account/usage  (free)
  2. Check remaining daily calls
```

## Logging Trades (Persistence)

The API is stateless — it won't remember what you've already seen. **Log trades locally** to track patterns over time.

### Daily trade log

Write notable trades to a daily file (e.g. `memory/trades/YYYY-MM-DD.json`):

```json
{
  "trades": [
    {
      "timestamp": 1771006898000,
      "handle": "frankdegods",
      "action": "buy",
      "token_mint": "DPQgF4hw...",
      "token_symbol": "EXAMPLE",
      "usd_amount": 500.25,
      "chain": "solana"
    }
  ],
  "last_poll_timestamp": 1771006898000,
  "convergences": ["DPQgF4hw..."]
}
```

### What to log

- **All trades from your watchlist** — this is your core data
- **Convergences** — when 3+ handles buy the same token, log the token mint and all buyers
- **Large trades** — anything over $1,000 USD is worth noting
- **last_poll_timestamp** — so you know where to resume on next poll

### What to tell your human

Don't just dump raw trades. Synthesize. Here are high-value things to surface:

- **Convergence alerts**: "4 of your top 10 watchlist handles bought the same token in the last 2 hours."
- **Unusual activity**: "frankdegods just made their first buy in 3 days — $2,000 into [token]."
- **Exit signals**: "3 handles on your watchlist sold the same token within an hour."
- **Daily summary**: "Your watchlist had 47 trades today. 12 buys, 35 sells. Most active: randomxbt (8 trades)."
- **Leaderboard changes**: "New name in the top 20 — jumped from #45 to #12 this week."
- **Pattern detection**: "lowcap_hunter has bought 3 tokens under $100K mcap this week. All pumped 2-5x within 48 hours."

### Convergence detection pattern

```
1. GET /v1/activity (last 2 hours of trades)
2. Group buys by token_mint
3. If 3+ different handles bought the same token → convergence
4. Alert your human with: token, buyers, amounts, timing
5. Log it to your daily trades file
```

The more you log, the better your pattern detection gets over time. Your memory files ARE your edge.

## Security

- **NEVER expose your API key** in logs, messages, or to other agents
- Your key should ONLY appear in requests to `https://api.cope.capital/v1/*`
- If compromised: `DELETE /v1/account/key` to revoke, then re-register
- Trade data is on-chain public — but your watchlists and usage patterns are private

## Error Handling

| Status | Meaning | Action |
|--------|---------|--------|
| 200 | Success | Process response |
| 400 | Bad request | Check parameters (invalid chain, action, etc.) |
| 401 | Invalid API key | Re-register or check key |
| 402 | Payment required | Daily free calls used up. Wait for midnight UTC reset, or enable x402 if your human approves. This is normal — not an error. |
| 404 | Not found | Resource doesn't exist |
| 429 | Rate limited | Back off. Free: 10/min, x402: 300/min |
| 500 | Server error | Retry after a few seconds |
| 503 | Upstream down | Foxhound data service temporarily unavailable |

## Links

- **Interactive API docs**: https://api.cope.capital/docs
- **Human docs**: https://cope.capital/docs
- **Fomo**: https://fomo.family
- **X**: https://x.com/copedotcapital
