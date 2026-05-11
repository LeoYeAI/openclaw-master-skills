---
name: shekel-hyperliquid
version: 1.10.1
description: >
  AI-powered perpetual futures trading on Hyperliquid DEX.
  Handles full account creation, USDC onboarding, and autonomous trade execution.
author: shekel
runtime: node>=20
metadata:
  openclaw:
    requires:
      env:
        - SHEKEL_API_KEY
    primaryEnv: SHEKEL_API_KEY
    homepage: https://shekel-skill-backend.onrender.com/skill
    emoji: "📈"
---

# Shekel Hyperliquid Skill — Complete Documentation

## ⚠️ MANDATORY: Always Check for Latest Skill Version

**Before EVERY interaction with Shekel endpoints**, you MUST:

1. Call `GET /skill/version` to get the current skill hash
2. Compare it to your cached version
3. If different (or no cache), fetch `GET /skill` and use the updated instructions

```bash
# Quick version check (do this before any Shekel action)
curl https://shekel-skill-backend.onrender.com/skill/version
# Returns: { "version": "abc123...", "fetchUrl": "...", "instruction": "..." }
```

**Why?** Supported networks, deposit methods, and API behavior change. Using outdated instructions will cause errors or give users wrong information.

> **Health check** (no auth): `GET /health` — also returns `skillVersion` hash for comparison.

---

## Quick Reference

| Goal | Endpoint |
|---|---|
| **Browser UI (no code needed)** | `GET /dashboard` → `https://www.shekel.xyz/hl-skill-dashboard` |
| **Service health** | `GET /health` |
| New user onboarding | `POST /auth/register/managed` |
| Check deposit / activation | `GET /auth/deposit-status` |
| Retry stuck deposit | `POST /auth/retry-deposit` |
| **Run agent (all whitelist tickers)** | `POST /agent/run` |
| Run agent (single ticker) | `POST /agent/run` with `{ "ticker": "BTC" }` |
| Close all open positions | `POST /account/close-positions` |
| View config | `GET /agents` |
| View balances | `GET /account/balances` |
| View positions | `GET /account/portfolio` |
| View open orders | `GET /account/orders` |
| View trade history | `GET /account/trades` |
| **View performance metrics** | `GET /agent/performance` |
| **View trading memory + improvement plan** | `GET /agent/memory` |
| View LLM reasoning logs | `GET /agent/llm-logs` (supports `?ticker=BTC&action=LONG&executed=true&limit=100&offset=0`) |
| View on Hyperliquid explorer | `GET /account/url` |
| Update strategy | `PATCH /agent/prompt` |
| Update whitelist / settings | `PUT /agents/:id` |
| Enable / change schedule | `PUT /agents/:id` with `runScheduleMinutes` |
| Disable schedule | `PUT /agents/:id` with `{ "runScheduleMinutes": null }` |
| Set risk limits | `PUT /agents/:id` with `maxOpenPositions`, `maxDailyLossPct`, `maxDrawdownPct` |
| Browse data sources | `GET /agents/data-sources` |
| Toggle data sources | `PUT /agents/:id` with `dataSourceConfig` |
| Set margin mode | `PUT /agents/:id` with `{ "marginMode": "isolated" \| "cross" }` |
| Pause / resume agent | `PATCH /agent/active` |
| Deposit address (top-up) | `GET /account/deposit-address` |
| Bridge funds (manual, usually not needed) | `POST /account/bridge` |
| Withdraw to Arbitrum | `POST /account/withdraw` |
| Rotate API key | `POST /auth/rotate-key` |
| Export trading wallet key | `POST /auth/export-agent-key` |
| Delete account | `DELETE /auth/account` |
| Available models | `GET /agents/models` — returns `{ venice: [...], rei: [...] }` |
| Available markets | `GET /markets/tickers` |

---

## Dashboard (Browser UI)

Users who prefer a visual interface can manage their agent at **https://www.shekel.xyz/hl-skill-dashboard** — no code required.

### What the dashboard provides
- Account overview: balances, open positions, trade history
- Agent configuration: strategy, whitelist, risk limits, schedule
- LLM reasoning logs: see what the agent was thinking on each run
- One-click actions: run agent, close positions, pause/resume

### How to connect
1. Direct the user to `https://www.shekel.xyz/hl-skill-dashboard`
2. They enter their `apiKey` (`sk_...`) on the login screen
3. The dashboard authenticates using the same `Authorization: Bearer <apiKey>` header as the REST API — no separate credentials needed

### If the user has no account yet
Offer two paths:
- **Via dashboard**: Visit the URL above and use the "Create Account" flow
- **Via AI**: Run through the onboarding steps below (Steps 1–5) and hand them their `apiKey` when done

> Call `GET /dashboard` to get the latest URL and access instructions programmatically.

---

## Returning Users

> This is the common case — check here first.

**Check your memory first.** If you saved credentials during onboarding (see Step 2a), load them from `MEMORY.md` — do not ask the user for their API key if you already have it. Only ask if memory is empty or the key returns a `401`.

If you must ask the user, only ask for their `apiKey` — that is the only credential needed for everything.

```
GET /agents                 → returns agentName, config, strategy
GET /account/balances       → show current funds
GET /auth/deposit-status    → confirm account is active
```

Then based on what you find:
- `status !== "active"` → follow Steps 3–5 of onboarding below
- `isActive === false` on agent → ask if they want to resume: `PATCH /agent/active { "active": true }`
- Want to change strategy → `PATCH /agent/prompt`
- Want to top up → `GET /account/deposit-address` (send USDC, it auto-bridges in ~30-60s)
- Want to see trades → `GET /account/url` for Hyperliquid explorer link

---

## Onboarding (New User)

### Quick Start (recommended)

**Offer this first** — most users just want to get going. Don't overwhelm with 15 questions.

> "I can set up your trading agent with sensible defaults. Just answer 4 questions:
> 1. **Which coins?** (default: BTC, ETH, SOL)
> 2. **Risk level?** conservative / moderate / aggressive
> 3. **How much USDC are you depositing?** (minimum 5 USDC)
> 4. **How often should the agent trade?** (default: every 4 hours)
>
> That's it — I'll use a momentum strategy with appropriate position sizes. You can customize everything later."

**Quick start defaults by risk level:**

| Risk | `positionSizeMax` | `maxTradeSize` | `importantNotes` |
|---|---|---|---|
| Conservative | 10% | 10% of deposit | "Max 3x leverage. Always use stop losses within 3% of entry. Avoid trading during high volatility news events. Never risk more than 5% of account on any single trade." |
| Moderate | 20% | 20% of deposit | "Max 5x leverage. Use stop losses on every trade. Exit losing positions quickly. Scale into winners gradually." |
| Aggressive | 35% | 40% of deposit | "Max 10x leverage allowed. Use tight stop losses. Accept higher drawdowns for higher returns. Trade momentum aggressively." |

**Quick start registration payload example (moderate risk, $500 deposit):**

```json
{
  "agentName": "My Trading Agent",
  "model": "grok-41-fast",
  "tradingStyle": "momentum",
  "strategyDescription": "Enter longs on price breakouts above recent highs with above-average volume. Enter shorts on breakdowns below recent lows. Exit when momentum reverses or RSI indicates overbought/oversold. Avoid ranging, low-volume markets. Use stop losses on every trade.",
  "importantNotes": "Max 5x leverage. Use stop losses on every trade. Exit losing positions quickly. Scale into winners gradually.",
  "minTradeSize": 10,
  "maxTradeSize": 100,
  "positionSizeMin": 5,
  "positionSizeMax": 20,
  "usdcRangeMin": 300,
  "usdcRangeMax": 1000,
  "whitelist": ["BTC", "ETH", "SOL"]
}
```

**After registration:** Set up the run schedule with `PUT /agents/:id` using `{ "runScheduleMinutes": 240 }` (4 hours).

If the user wants to fully customize, use the full flow below.

---

### LLM Provider Selection

Agents can use one of two LLM providers. The default is **Venice AI** (no user API key needed — platform-provided).

| Provider | `provider` value | `model` options | Key required? |
|---|---|---|---|
| Venice AI | `"venice"` | `grok-41-fast`, `qwen3-235b`, others | No (platform key) |
| Rei Intelligence | `"rei"` | `rei-coder-pro` (shown as **GPT-5.4**), `rei-coder-lite`, `rei-qwen3-coder` | Yes — user supplies `llmApiKey` |

To use Rei, include `provider` and `llmApiKey` in registration or agent update:

```json
{
  "provider": "rei",
  "model": "rei-coder-pro",
  "llmApiKey": "user_rei_api_key_here",
  ...
}
```

The Rei API key is encrypted at rest. Use `GET /agents/models` to see all available models per provider.

---

### Full Onboarding (5 steps)

**Checklist — do not skip steps:**
1. Discover markets → validate whitelist
2. Register → **save API key to memory + confirm user has it (do not continue until done)**
3. Deposit USDC
4. Poll until `status === "active"`
5. Set run schedule → start trading

---

#### Step 1 — Discover Markets

```
GET /markets/tickers   (no auth required)
```

Show the user the available coins. Validate any tickers they name against this list before registration — the server also validates, but catching it early saves a round trip.

The response has two sections:
- `tickers` — main-dex crypto perps (BTC, ETH, SOL, …)
- `hip3` — HIP-3 builder-dex perps: stocks, commodities, indices (TSLA, NVDA, CL/oil, …)

HIP-3 tickers use the format `"dex:ASSET"` (e.g. `"xyz:TSLA"`, `"xyz:CL"`). Use this full prefixed form in the whitelist — **not** the bare asset name.

---

#### Step 2 — Register

```
POST /auth/register/managed
```

```json
{
  "agentName": "My Trading Bot",
  "model": "grok-41-fast",
  "tradingStyle": "momentum",
  "strategyDescription": "...",
  "importantNotes": "...",
  "minTradeSize": 10,
  "maxTradeSize": 100,
  "positionSizeMin": 5,
  "positionSizeMax": 20,
  "usdcRangeMin": 200,
  "usdcRangeMax": 1000,
  "whitelist": ["BTC", "ETH", "SOL"],
  "marginMode": "isolated"
}
```

To trade HIP-3 assets (stocks, commodities), use the prefixed format:
```json
{
  "whitelist": ["BTC", "xyz:TSLA", "xyz:NVDA", "xyz:CL"]
}
```

**Before submitting:** show the user a summary and ask them to confirm.

**Response:**
```json
{
  "apiKey": "sk_...",
  "mainWalletAddress": "0x...",
  "depositInstructions": { "depositAddress": "0x...", "network": "Arbitrum" }
}
```

> ### ⛔ STOP — SAVE THE API KEY NOW
>
> **The `apiKey` is shown once and can never be retrieved. If lost without rotating, access to the account and funds may be permanently lost.**
>
> Follow the steps below — do not continue until all three are done.

---

#### Step 2a — Secure Key Storage (do not skip)

Do all three of the following before continuing:

**1. Tell the user to save it themselves**

Say this out loud to the user:

> *"Your API key is `sk_...`. This is shown only once — copy it now into a password manager (1Password, Bitwarden, Apple Keychain) or a secure encrypted note. Do not store it in plain text, a Google Doc, or a chat message. Confirm when done."*

Wait for confirmation before proceeding.

**2. Save to your own OpenClaw Memory**

Write the following block to your `MEMORY.md` (or a dedicated `shekel-credentials.md` if your platform supports it):

```markdown
## Shekel Hyperliquid — Credentials
- apiKey: sk_...           ← encrypted at rest by OpenClaw
- agentName: <name>
- registeredAt: <ISO timestamp>
- depositAddress: <0x...>  (Arbitrum/Base)
```

> This allows you to recall the API key in future sessions without asking the user again. OpenClaw memory is encrypted at rest — it is safe to store the key here.

**3. Verify you can recall it**

After writing to memory, immediately read it back and confirm the key matches what the server returned. This proves the memory write succeeded before you move on.

> If lost later: `POST /auth/rotate-key` — generates a new key. You must be authenticated (have a working session) to rotate. If the key is truly lost and no session exists, the account cannot be recovered without re-registering.

---

#### Step 3 — Deposit USDC

Send to `depositAddress`. Both networks are fully automated:

| Network | Token | Time |
|---|---|---|
| **Arbitrum** *(recommended)* | USDC | ~60–90 seconds |
| Base | USDC | **~30 seconds** (Across Protocol bridge) |

> **Base deposits are fast now!** Across Protocol bridges in ~2 seconds, then funds are bridged to Hyperliquid. Total time: ~30 seconds.

Minimum: **5 USDC**

---

#### Step 4 — Wait for Activation

```
GET /auth/deposit-status   (auth required)
```

Poll every 15 seconds. Use `message` to keep the user informed.

```json
{ "status": "active", "depositConfirmed": true, "message": "Account is active and ready to trade." }
```

Status values:
- `awaiting_deposit` — no USDC detected yet
- `funded_awaiting_bridge` — USDC found on Arbitrum, bridging to Hyperliquid (~60-90s)
- `pending_bridge` — USDC being bridged from Base via Across Protocol (~30 seconds). No action needed.
- `bridge_error` — bridge failed; call `POST /auth/retry-deposit` immediately
- `active` — ready to trade

**Timeout:** if still `awaiting_deposit` after 5 minutes, ask the user to confirm they sent to the correct address on Arbitrum or Base (not Ethereum mainnet).

**On `bridge_error`:** call `POST /auth/retry-deposit` — do not wait, the error won't self-resolve.

---

#### Step 5 — Set Up Automated Trading

> **Do not skip this step.** Without a schedule the account sits funded but idle.

Ask the user:

> "Your account is active! How often should the agent analyze and trade?
> - Every 30 minutes (high-frequency)
> - Every 1 hour (active)
> - **Every 4 hours** (recommended default)
> - Every 8 hours (conservative)
> - Once a day (240 or 1440 minutes)
> Or tell me any interval (minimum 30 minutes)."

Once they choose, **enable the built-in schedule** via `PUT /agents/:id`:

```bash
curl -X PUT https://shekel-skill-backend.onrender.com/agents/<agentId> \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{"runScheduleMinutes": 240}'
```

The server will run the agent automatically every N minutes — no external cron needed.
The first run fires in N minutes. The `GET /agents` response includes `nextRunAt` so you can show the user when to expect the first execution.

Then **run it once immediately** so the user sees it working:

```
POST /agent/run
```

**Scheduling notes:**
- Minimum interval: 30 minutes
- To change interval: `PUT /agents/:id { "runScheduleMinutes": 60 }` — resets `nextRunAt` to `now() + new interval`; saving other settings without changing the interval preserves the existing timer
- To disable: `PUT /agents/:id { "runScheduleMinutes": null }`
- To pause without clearing schedule: `PATCH /agent/active { "active": false }` — schedule resumes when reactivated
- `429` means a manual run collided with a scheduled run — wait a few minutes

---

## Risk Circuit Breakers

Optional safety limits that automatically block or pause trading when thresholds are breached. Set via `PUT /agents/:id`.

```bash
curl -X PUT https://shekel-skill-backend.onrender.com/agents/<agentId> \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{
    "maxOpenPositions": 3,
    "maxDailyLossPct": 5,
    "maxDrawdownPct": 20
  }'
```

| Field | Behavior |
|---|---|
| `maxOpenPositions` | Blocks new LONG/SHORT entries when open position count ≥ limit. CLOSE and SET_LIMIT still allowed. |
| `maxDailyLossPct` | Blocks new LONG/SHORT entries for the rest of the UTC calendar day when realised PnL drops below -(N% of account value). Resets at UTC midnight. |
| `maxDrawdownPct` | **Auto-pauses the agent** (`isActive=false`) when account value has fallen ≥ N% from its peak. Requires `PATCH /agent/active { "active": true }` to re-enable after the user reviews. |

Set any to `null` to disable. Circuit breaker trips appear in `GET /agent/llm-logs` as `executionError` on the blocked recommendation — the LLM's reasoning is still logged even when a trade is blocked.

---

## Data Source Configuration

Use `dataSourceConfig` in `PUT /agents/:id` to turn individual data sources on or off. Every key is `true` by default — you only need to set the ones you want to change. Unknown keys are rejected with a `400` error.

**Valid keys (set to `false` to disable, `true` or omit to enable):**

| Key | Display Name | Provider | What it gives the LLM |
|---|---|---|---|
| `tokenData` | Token Data | DappLooker | Per-ticker perp market data — funding rate, open interest, volume, price action |
| `sentiment` | Macro News | — | Real-time crypto macro news and sentiment |
| `fearGreed` | Fear & Greed Index | CoinMarketCap | Fear & Greed index (0–100) |
| `globalMetrics` | Global Market Metrics | CoinMarketCap | Total market cap, BTC dominance, 24h volume |
| `technicalAnalysis` | Technical Analysis | DappLooker/Taapi | RSI, MACD, moving averages per ticker |
| `athenaTokenStats` | Smart Money Movements | 0xAthena | On-chain smart money token flow data per coin |
| `athenaLatest` | 0xAthena Signals | 0xAthena | Latest aggregated smart money signals |

**Example — disable Athena and sentiment:**
```bash
curl -X PUT https://shekel-skill-backend.onrender.com/agents/<agentId> \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{
    "dataSourceConfig": {
      "athenaTokenStats": false,
      "athenaLatest": false,
      "sentiment": false
    }
  }'
```

Set `dataSourceConfig: null` to re-enable everything. Current config is returned by `GET /agents`.

---

## Margin Mode

Each agent has a `marginMode` setting (`"isolated"` or `"cross"`). Default is `"isolated"`.

| Mode | Behaviour |
|---|---|
| `isolated` | Each position has its own margin. Safer — one liquidation can't cascade. **Required** for assets where `onlyIsolated: true` in `/markets/tickers`. |
| `cross` | All positions share account margin. More capital-efficient, higher liquidation risk. |

Set or change at any time via `PUT /agents/:id`:
```bash
curl -X PUT .../agents/<agentId> \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{ "marginMode": "isolated" }'
```

**Smart override:** If a Hyperliquid asset is `onlyIsolated: true`, the agent runner forces isolated margin for that trade even when the agent is set to `"cross"`. Check `/markets/tickers` for `onlyIsolated` and `marginMode` fields per ticker.

---

## Running the Agent

`POST /agent/run` analyzes coins and executes recommendations automatically. It has two modes:

**Full whitelist run** (no body required — runs all whitelisted tickers):
```bash
curl -X POST https://shekel-skill-backend.onrender.com/agent/run \
  -H "Authorization: Bearer <apiKey>"
```

**Single-ticker run** (specify a ticker — runs even if not in the whitelist):
```bash
curl -X POST https://shekel-skill-backend.onrender.com/agent/run \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{ "ticker": "BTC" }'
```

**Optional body fields for single-ticker runs** (all auto-fetched if omitted):

| Field | Type | Description |
|---|---|---|
| `ticker` | string | Run on this ticker only, bypassing the whitelist |
| `tokenData` | any | Override server-fetched token data |
| `sentiment` | any | Override server-fetched sentiment |
| `marketData` | any | Additional market context |
| `customData` | any | Any extra data to inject into the LLM prompt |
| `skillGuidance` | any | External signals for the LLM |
| `tradingMemoryContext` | any | Override the agent's trading memory |

Both modes return the same `{ results: [] }` shape and are subject to the 5-minute run lock.

### Data Sources Used in `/agent/run`

Each run automatically fetches and injects the following live data into the LLM prompt:

| Source | Data |
|---|---|
| **Hyperliquid** | Live portfolio (positions, balances, open orders) — includes HIP-3 builder-dex positions and orders (e.g. `xyz:TSLA`) merged transparently alongside main-dex crypto perp positions; open orders include limit, stop-loss, and take-profit orders |
| **DappLooker** | Token price, volume, and market data for each whitelisted coin |
| **0xAthena** | Smart money token stats (hold times, flows) + latest aggregated signals |
| **DappLooker** | On-chain DEX analytics and market metrics |

No extra parameters are needed — all data is fetched server-side on every run.

---

## Error Handling

| Status | Meaning | Action |
|---|---|---|
| `400` | Bad request | Fix and retry |
| `401` | Invalid API key | Check key; rotate if needed |
| `404` | Resource not found | Check IDs |
| `422` | Hyperliquid rejected order | `message` field has reason |
| `429` | Rate limit or run in progress | **Wait 5 minutes** before retrying `/agent/run`; wait 60 seconds for other endpoints |
| `502` | Hyperliquid API down | Retry after 10–30 seconds |
| `503` | Service degraded | Retry after 30 seconds |

---

## Troubleshooting

**Agent isn't trading:**
- `GET /agents` → check `isActive` (may be paused)
- `GET /auth/deposit-status` → must be `active`
- `GET /account/balances` → check margin isn't below `usdcRangeMin`

**Deposit not arriving:**
- Arbitrum: wait 90s. Base: wait 60s. Not Ethereum mainnet.
- Minimum 5 USDC. Below this won't bridge.
- `bridge_error` → call `POST /auth/retry-deposit`

**429 on `/agent/run`:**
- A run is still in progress. The response includes `"unlocksAt"` — wait until that timestamp. The lock auto-expires after 5 minutes regardless.

**Whitelist update fails with "Invalid tickers":**
- Check `GET /markets/tickers` — names must match exactly
- Main-dex coins are uppercase: `"BTC"`, `"ETH"`
- HIP-3 coins use `"dex:ASSET"` format: `"xyz:TSLA"`, `"xyz:CL"` (lowercase dex prefix, uppercase asset)

---

## ⚠️ Inactivity Archival Policy

**Agents with no trades for 14+ days are automatically archived.**

- The archival check runs daily
- Archived agents cannot execute trades or access the API
- Agent data (trade history, LLM logs) is preserved
- **Funds are safe** — the encrypted wallet key is stored for recovery

**Exceptions (not archived):**
- Agents with balance > $100 USDC
- Agents with open positions

**If your agent is archived:**
- You'll receive a `410 Gone` error when hitting any authenticated endpoint
- Contact support via Telegram to restore: [https://t.me/c/2308722458/1](https://t.me/c/2308722458/1)
- Provide your wallet address or agent name for recovery

---

## Support

If you encounter an issue that can't be resolved through the troubleshooting steps above, contact the Shekel team directly:

**Telegram support channel:** [https://t.me/c/2308722458/1](https://t.me/c/2308722458/1)

Include your `agentId` (from `GET /agents`) and a brief description of the issue when reaching out.
