---
name: Vincent - Trading Engine for agents
description: |
  Strategy-driven automated trading for Polymarket and HyperLiquid. Use this skill when users want to create
  trading strategies, set stop-loss/take-profit/trailing stop rules, or manage automated trading.
  Triggers on "trading strategy", "stop loss", "take profit", "trailing stop", "automated trading",
  "trading engine", "trade rules", "strategy monitor".
allowed-tools: Read, Write, Bash(npx:@vincentai/cli*)
version: 1.0.0
author: HeyVincent <contact@heyvincent.ai>
license: MIT
homepage: https://heyvincent.ai
source: https://github.com/HeyVincent-ai/Vincent
metadata:
  clawdbot:
    homepage: https://heyvincent.ai
    requires:
      config:
        - ${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/agentwallet
        - ./agentwallet
---

# Vincent Trading Engine - Strategy-Driven Automated Trading

Use this skill to create and manage automated trading strategies for Polymarket prediction markets and HyperLiquid perpetuals/spot. The Trading Engine combines driver-based monitoring (web search, Twitter, newswire, price feeds) with a signal pipeline and LLM-powered decision-making to automatically trade based on your thesis. It also includes standalone stop-loss, take-profit, and trailing stop rules that work without the LLM.

All commands use the `@vincentai/cli` package.

## How It Works

**The Trading Engine is a unified system with two modes:**

1. **LLM-Powered Strategies** — Create a versioned strategy with a structured thesis, weighted drivers (web search keywords, Twitter accounts, newswire topics, price triggers), and an escalation policy. When drivers detect new information, signals are scored and batched. When the escalation threshold is met, an LLM (Claude via OpenRouter) evaluates the signals against your thesis and decides whether to trade, update the thesis, set protective orders, or alert you.
2. **Standalone Trade Rules** — Set stop-loss, take-profit, and trailing stop rules on positions. These execute automatically when price conditions are met — no LLM involved.

**Architecture:**

- Integrated into the Vincent backend (no separate service to run)
- Strategy endpoints under `/api/skills/polymarket/strategies/...`
- Trade rule endpoints under `/api/skills/polymarket/rules/...`
- HyperLiquid rules use `venue: "hyperliquid"` and route through the HL adapter
- Uses the same API key as the Polymarket or HyperLiquid skill (depending on venue)
- All trades go through Vincent's policy-enforced pipeline
- LLM costs are metered and deducted from the user's credit balance
- Every LLM invocation is recorded with full audit trail (tokens, cost, actions, duration)

## Security Model

- **LLM cannot bypass policies** — all trades go through the venue's policy-enforced skill (`polymarketSkill.placeBet()` or `hyperliquidSkill.trade()`) which enforces spending limits, approval thresholds, and allowlists
- **Backend-side LLM key** — the OpenRouter API key never leaves the server. Agents and users cannot invoke the LLM directly
- **Credit gating** — no LLM invocation without sufficient credit balance
- **Tool constraints** — the LLM's available tools are controlled by the strategy's `config.tools` settings. If `canTrade: false`, the trade tool is not provided
- **Rate limiting** — max concurrent LLM invocations is capped to prevent runaway costs
- **Audit trail** — every invocation is recorded with full prompt, response, actions, cost, and duration
- **No private keys** — the Trading Engine uses the Vincent API for all trades. Private keys stay on Vincent's servers

## Part 1: LLM-Powered Strategies

### Core Concepts

- **Instrument**: A tradeable asset on a venue. Defined by `id`, `type` (stock, perp, swap, binary, option), `venue`, and optional constraints (leverage, margin, liquidity, fees).
- **Thesis**: Your directional view — `estimate` (target price/value), `direction` (long/short/neutral), `confidence` (0–1), and `reasoning`.
- **Driver**: A named information source that feeds the signal pipeline. Each driver has a `weight`, `direction` (bullish/bearish/contextual), and `monitoring` config (entities, keywords, embedding anchor, sources, polling interval).
- **Escalation Policy**: Controls when the LLM is woken up. `signalScoreThreshold` (minimum score to batch), `highConfidenceThreshold` (score that triggers immediate wake), `maxWakeFrequency` (e.g. "1 per 15m"), `batchWindow` (e.g. "5m").
- **Trade Rules**: Entry rules (min edge, order type), exit rules (thesis invalidation triggers), auto-actions (stop-loss, take-profit, trailing stop, price delta triggers), and sizing rules (method, max position, portfolio %, max trades/day).

### Signal Pipeline

Strategies process information through a 6-layer pipeline:

1. **Ingest** — Raw data from driver sources (web search, Twitter, newswire, price feeds, RSS, Reddit, on-chain, filings, options flow)
2. **Filter** — Deduplication and relevance filtering. Drops signals already seen or below quality threshold
3. **Score** — Each signal is scored (0–1) based on driver weight, embedding similarity to the anchor, and entity/keyword matches
4. **Escalate** — Scored signals are batched according to the escalation policy. Low-score signals accumulate in a batch window; high-confidence signals trigger immediate LLM wake
5. **LLM** — The LLM evaluates batched signals against the current thesis. It can update the thesis, issue trade decisions, update driver states, or take no action
6. **Execute** — Trade decisions pass through policy enforcement and are routed to the appropriate venue adapter for execution

### Strategy Lifecycle

Strategies follow a versioned lifecycle: `DRAFT` → `ACTIVE` → `PAUSED` → `ARCHIVED`

- **DRAFT**: Can be edited. Not yet monitoring or invoking the LLM.
- **ACTIVE**: Drivers are running. New signals trigger the pipeline.
- **PAUSED**: Monitoring is stopped. Can be resumed.
- **ARCHIVED**: Permanently stopped. Cannot be reactivated.

To iterate on a strategy, duplicate it as a new version (creates a new DRAFT with incremented version number and the same config).

### Create a Strategy

```bash
npx @vincentai/cli@latest trading-engine create-strategy \
  --key-id <KEY_ID> \
  --name "BTC Momentum" \
  --config '{
    "instruments": [
      { "id": "btc-usd-perp", "type": "perp", "venue": "polymarket" },
      { "id": "BTC", "type": "perp", "venue": "hyperliquid" }
    ],
    "thesis": {
      "estimate": 105000,
      "direction": "long",
      "confidence": 0.7,
      "reasoning": "ETF inflows accelerating, halving supply shock imminent"
    },
    "drivers": [
      {
        "name": "ETF Flow Monitor",
        "weight": 2.0,
        "direction": "bullish",
        "monitoring": {
          "entities": ["BlackRock", "Fidelity"],
          "keywords": ["bitcoin ETF", "BTC inflow"],
          "embeddingAnchor": "Bitcoin ETF institutional inflows",
          "sources": ["web_search", "newswire"]
        }
      },
      {
        "name": "Crypto Twitter",
        "weight": 1.0,
        "direction": "contextual",
        "monitoring": {
          "entities": ["@BitcoinMagazine", "@saborskycnbc"],
          "keywords": ["bitcoin", "BTC"],
          "sources": ["twitter"]
        }
      }
    ],
    "escalation": {
      "signalScoreThreshold": 0.3,
      "highConfidenceThreshold": 0.8,
      "maxWakeFrequency": "1 per 15m",
      "batchWindow": "5m"
    },
    "tradeRules": {
      "entry": { "minEdge": 0.05, "orderType": "limit", "limitOffset": 0.01 },
      "autoActions": { "stopLoss": -0.10, "takeProfit": 0.25, "trailingStop": -0.05 },
      "exit": { "thesisInvalidation": ["ETF outflows exceed $500M/week"] },
      "sizing": {
        "method": "edgeScaled",
        "maxPosition": 500,
        "maxPortfolioPct": 20,
        "maxTradesPerDay": 5,
        "minTimeBetweenTrades": "30m"
      }
    },
    "notifications": {
      "onTrade": true,
      "onThesisChange": true,
      "channel": "none"
    }
  }'
```

**Parameters:**

- `--name`: Strategy name
- `--config`: Full strategy config JSON (see Core Concepts above for structure)
- `--data-source-secret-id`: Optional DATA_SOURCES secret ID for driver monitoring API calls
- `--poll-interval`: Polling interval in minutes for driver monitoring (default: 15)

### List Strategies

```bash
npx @vincentai/cli@latest trading-engine list-strategies --key-id <KEY_ID>
```

### Get Strategy Details

```bash
npx @vincentai/cli@latest trading-engine get-strategy --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Update a Strategy

Update a DRAFT strategy. Pass only the fields you want to change — config is a partial object.

```bash
npx @vincentai/cli@latest trading-engine update-strategy --key-id <KEY_ID> --strategy-id <STRATEGY_ID> \
  --name "Updated Name" --config '{ "thesis": { "confidence": 0.8, "reasoning": "Updated reasoning" } }'
```

**Parameters:**

- `--strategy-id`: Strategy ID (required)
- `--name`: New strategy name
- `--config`: Partial strategy config JSON — only include fields to update
- `--data-source-secret-id`: DATA_SOURCES secret ID
- `--poll-interval`: New polling interval in minutes

### Activate a Strategy

Starts driver monitoring and signal pipeline processing. Strategy must be in DRAFT status.

```bash
npx @vincentai/cli@latest trading-engine activate --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Pause a Strategy

Stops monitoring. Strategy must be ACTIVE.

```bash
npx @vincentai/cli@latest trading-engine pause --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Resume a Strategy

Resumes monitoring. Strategy must be PAUSED.

```bash
npx @vincentai/cli@latest trading-engine resume --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Archive a Strategy

Permanently stops a strategy. Cannot be undone.

```bash
npx @vincentai/cli@latest trading-engine archive --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Duplicate a Strategy (New Version)

Creates a new DRAFT with the same config, incremented version number, and a link to the parent version.

```bash
npx @vincentai/cli@latest trading-engine duplicate-strategy --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### View Version History

See all versions of a strategy lineage.

```bash
npx @vincentai/cli@latest trading-engine versions --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### View LLM Invocation History

See the LLM decision log for a strategy — what data triggered it, what the LLM decided, what actions were taken, and the cost.

```bash
npx @vincentai/cli@latest trading-engine invocations --key-id <KEY_ID> --strategy-id <STRATEGY_ID> --limit 20
```

### View Cost Summary

See aggregate LLM costs for all strategies under a secret.

```bash
npx @vincentai/cli@latest trading-engine costs --key-id <KEY_ID>
```

### View Performance Metrics

See performance metrics for a strategy: P&L, win rate, trade count, and per-instrument breakdown.

```bash
npx @vincentai/cli@latest trading-engine performance --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Driver Configuration

#### Web Search Drivers

Add a driver with `"sources": ["web_search"]`. The engine periodically searches Brave for the driver's keywords and triggers the signal pipeline when new results appear.

```json
{
  "name": "AI News Monitor",
  "weight": 1.5,
  "direction": "bullish",
  "monitoring": {
    "keywords": ["AI tokens", "GPU shortage", "prediction market regulation"],
    "embeddingAnchor": "AI technology investment trends",
    "sources": ["web_search"]
  }
}
```

Each keyword is searched independently. Results are deduplicated — the same URLs won't trigger the pipeline twice.

#### Twitter Drivers

Add a driver with `"sources": ["twitter"]`. The engine periodically checks the specified entities for new tweets.

```json
{
  "name": "Crypto Twitter",
  "weight": 1.0,
  "direction": "contextual",
  "monitoring": {
    "entities": ["@DeepSeek", "@nvidia", "@OpenAI"],
    "keywords": ["AI", "GPU"],
    "sources": ["twitter"]
  }
}
```

Tweets are deduplicated by tweet ID — only genuinely new tweets trigger the pipeline.

#### Newswire Drivers (Finnhub)

Add a driver with `"sources": ["newswire"]`. The engine periodically polls Finnhub's market news API and triggers the pipeline when new headlines matching your keywords appear.

```json
{
  "name": "Market News",
  "weight": 1.5,
  "direction": "contextual",
  "monitoring": {
    "keywords": ["artificial intelligence", "GPU shortage", "semiconductor"],
    "sources": ["newswire"]
  }
}
```

Headlines and summaries are matched case-insensitively. Articles are deduplicated by headline hash with a sliding window.

**Note:** Requires a `FINNHUB_API_KEY` env var on the server. Finnhub's free tier allows 60 API calls/min. No per-call credit deduction.

#### Price Triggers

Price triggers are evaluated in real-time via the Polymarket WebSocket feed. When a price condition is met, the signal pipeline is invoked with the price data.

Trigger types:

- `ABOVE` — triggers when price exceeds a threshold
- `BELOW` — triggers when price drops below a threshold
- `CHANGE_PCT` — triggers on a percentage change from reference price

Price triggers are one-shot: once fired, they're marked as consumed. The LLM can create new triggers if needed.

### Thesis Best Practices

The thesis is your structured directional view. Good theses include:

1. **A clear estimate**: Target price or value the market should reach
2. **A confidence level**: Start at 0.5–0.7 and let the LLM adjust as new data arrives
3. **Specific reasoning**: "ETF inflows accelerating, halving supply shock imminent" is better than "BTC will go up"
4. **Explicit invalidation conditions**: Use `tradeRules.exit.thesisInvalidation` to define what would break your thesis

### LLM Available Tools

When the LLM is invoked, it can use these tools (depending on strategy config):

| Tool                | Description                        | Requires                           |
| ------------------- | ---------------------------------- | ---------------------------------- |
| `place_trade`       | Buy or sell a position             | `canTrade: true` in trade rules    |
| `set_stop_loss`     | Set a stop-loss rule on a position | `canSetRules: true` in trade rules |
| `set_take_profit`   | Set a take-profit rule             | `canSetRules: true` in trade rules |
| `set_trailing_stop` | Set a trailing stop                | `canSetRules: true` in trade rules |
| `alert_user`        | Send an alert without trading      | Always available                   |
| `no_action`         | Do nothing (with reasoning)        | Always available                   |

### Cost Tracking

Every LLM invocation is metered:

- **Token costs**: Input and output tokens are priced per the model's rate
- **Deducted from credit balance**: Same pool as data source credits (`dataSourceCreditUsd`)
- **Pre-flight check**: If insufficient credit, the invocation is skipped and logged
- **Data source costs**: Brave Search (~$0.005/call) and Twitter (~$0.005-$0.01/call) are also metered. Finnhub newswire calls are free (no credit deduction)

Typical LLM invocation cost: $0.05–$0.30 depending on context size.

---

## Part 2: Standalone Trade Rules

Trade rules execute automatically when price conditions are met — no LLM involved. These are stop-loss, take-profit, and trailing stop rules that protect your positions.

### Check Worker Status

```bash
npx @vincentai/cli@latest trading-engine status --key-id <KEY_ID>
# Returns: worker status, active rules count, last sync time, circuit breaker state
```

### Create a Stop-Loss Rule

Automatically sell a position if price drops below a threshold:

```bash
# Polymarket — triggerPrice is 0–1 (outcome token price)
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --market-id 0x123... --token-id 456789 \
  --rule-type STOP_LOSS --trigger-price 0.40

# HyperLiquid — triggerPrice is absolute USD price, marketId and tokenId are the coin name
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --venue hyperliquid --market-id BTC --token-id BTC \
  --rule-type STOP_LOSS --trigger-price 95000
```

**Parameters:**

- `--venue`: `polymarket` (default) or `hyperliquid`
- `--market-id`: Polymarket condition ID, or coin name for HyperLiquid (e.g. `BTC`, `ETH`)
- `--token-id`: Polymarket outcome token ID, or coin name for HyperLiquid
- `--rule-type`: `STOP_LOSS` (sells if price <= trigger), `TAKE_PROFIT` (sells if price >= trigger), or `TRAILING_STOP`
- `--trigger-price`: Price threshold — 0 to 1 for Polymarket, absolute USD price for HyperLiquid

### Create a Take-Profit Rule

Automatically sell a position if price rises above a threshold:

```bash
# Polymarket
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --market-id 0x123... --token-id 456789 \
  --rule-type TAKE_PROFIT --trigger-price 0.75

# HyperLiquid
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --venue hyperliquid --market-id ETH --token-id ETH \
  --rule-type TAKE_PROFIT --trigger-price 4500
```

### Create a Trailing Stop Rule

A trailing stop moves the stop price up as the price rises:

```bash
# Polymarket
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --market-id 0x123... --token-id 456789 \
  --rule-type TRAILING_STOP --trigger-price 0.45 --trailing-percent 5

# HyperLiquid
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --venue hyperliquid --market-id SOL --token-id SOL \
  --rule-type TRAILING_STOP --trigger-price 170 --trailing-percent 5
```

**Trailing stop behavior:**

- `--trailing-percent` is percent points (e.g. `5` = 5%)
- Computes `candidateStop = currentPrice * (1 - trailingPercent/100)`
- If `candidateStop` > current `triggerPrice`, updates `triggerPrice`
- `triggerPrice` never moves down
- Rule triggers when `currentPrice <= triggerPrice`

### List Rules

```bash
# All rules
npx @vincentai/cli@latest trading-engine list-rules --key-id <KEY_ID>

# Filter by status
npx @vincentai/cli@latest trading-engine list-rules --key-id <KEY_ID> --status ACTIVE
```

### Update a Rule

```bash
npx @vincentai/cli@latest trading-engine update-rule --key-id <KEY_ID> --rule-id <RULE_ID> --trigger-price 0.45
```

### Cancel a Rule

```bash
npx @vincentai/cli@latest trading-engine delete-rule --key-id <KEY_ID> --rule-id <RULE_ID>
```

### View Monitored Positions

```bash
npx @vincentai/cli@latest trading-engine positions --key-id <KEY_ID>
```

### View Event Log

```bash
# All events
npx @vincentai/cli@latest trading-engine events --key-id <KEY_ID>

# Events for specific rule
npx @vincentai/cli@latest trading-engine events --key-id <KEY_ID> --rule-id <RULE_ID>

# Paginated
npx @vincentai/cli@latest trading-engine events --key-id <KEY_ID> --limit 50 --offset 100
```

**Event types:**

- `RULE_CREATED` — Rule was created
- `RULE_TRAILING_UPDATED` — Trailing stop moved triggerPrice upward
- `RULE_EVALUATED` — Worker checked the rule against current price
- `RULE_TRIGGERED` — Trigger condition was met
- `ACTION_PENDING_APPROVAL` — Trade requires human approval, rule paused
- `ACTION_EXECUTED` — Trade executed successfully
- `ACTION_FAILED` — Trade execution failed
- `RULE_CANCELED` — Rule was manually canceled

### Rule Statuses

- `ACTIVE` — Rule is live and being monitored
- `TRIGGERED` — Condition was met, trade executed
- `PENDING_APPROVAL` — Trade requires human approval; rule paused
- `CANCELED` — Manually canceled before triggering
- `FAILED` — Triggered but trade execution failed

---

## Complete Workflow: Strategy + Trade Rules

### Polymarket Workflow

### Step 1: Place a bet with the Polymarket skill

```bash
npx @vincentai/cli@latest polymarket bet --key-id <KEY_ID> --token-id 123456789 --side BUY --amount 10 --price 0.55
```

### Step 2: Create a strategy to monitor the thesis

```bash
npx @vincentai/cli@latest trading-engine create-strategy --key-id <KEY_ID> \
  --name "Bitcoin Bull Thesis" \
  --config '{
    "instruments": [
      { "id": "123456789", "type": "binary", "venue": "polymarket" }
    ],
    "thesis": {
      "estimate": 0.85,
      "direction": "long",
      "confidence": 0.7,
      "reasoning": "Bitcoin is likely to break $100k on ETF inflows"
    },
    "drivers": [
      {
        "name": "ETF News",
        "weight": 2.0,
        "direction": "bullish",
        "monitoring": {
          "keywords": ["bitcoin ETF inflows", "bitcoin institutional"],
          "sources": ["web_search", "newswire"]
        }
      },
      {
        "name": "Crypto Twitter",
        "weight": 1.0,
        "direction": "contextual",
        "monitoring": {
          "entities": ["@BitcoinMagazine", "@saborskycnbc"],
          "sources": ["twitter"]
        }
      }
    ],
    "escalation": {
      "signalScoreThreshold": 0.3,
      "highConfidenceThreshold": 0.8,
      "maxWakeFrequency": "1 per 15m",
      "batchWindow": "5m"
    },
    "tradeRules": {
      "entry": { "minEdge": 0.05 },
      "autoActions": { "stopLoss": -0.15, "takeProfit": 0.30, "trailingStop": -0.05 },
      "exit": { "thesisInvalidation": ["ETF outflows accelerate above $500M/week"] },
      "sizing": { "method": "edgeScaled", "maxPosition": 100, "maxPortfolioPct": 20, "maxTradesPerDay": 5 }
    }
  }' \
  --poll-interval 10
```

### Step 3: Set a standalone stop-loss as immediate protection

```bash
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --market-id 0xabc... --token-id 123456789 \
  --rule-type STOP_LOSS --trigger-price 0.40
```

### Step 4: Activate the strategy

```bash
npx @vincentai/cli@latest trading-engine activate --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### Step 5: Monitor activity

```bash
# Check strategy invocations
npx @vincentai/cli@latest trading-engine invocations --key-id <KEY_ID> --strategy-id <STRATEGY_ID>

# Check trade rule events
npx @vincentai/cli@latest trading-engine events --key-id <KEY_ID>

# Check costs
npx @vincentai/cli@latest trading-engine costs --key-id <KEY_ID>

# Check performance
npx @vincentai/cli@latest trading-engine performance --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
```

### HyperLiquid Workflow

### Step 1: Open a perp position with the HyperLiquid skill

```bash
npx @vincentai/cli@latest hyperliquid trade --key-id <KEY_ID> \
  --coin BTC --is-buy true --sz 0.001 --limit-px 106000 --order-type market
```

### Step 2: Set a stop-loss rule for the position

```bash
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --venue hyperliquid --market-id BTC --token-id BTC \
  --rule-type STOP_LOSS --trigger-price 95000
```

### Step 3: Set a take-profit rule

```bash
npx @vincentai/cli@latest trading-engine create-rule --key-id <KEY_ID> \
  --venue hyperliquid --market-id BTC --token-id BTC \
  --rule-type TAKE_PROFIT --trigger-price 115000
```

### Step 4: Create a strategy to monitor your thesis

```bash
npx @vincentai/cli@latest trading-engine create-strategy --key-id <KEY_ID> \
  --name "BTC Perp Momentum" \
  --config '{
    "instruments": [
      { "id": "BTC", "type": "perp", "venue": "hyperliquid" }
    ],
    "thesis": {
      "estimate": 115000,
      "direction": "long",
      "confidence": 0.7,
      "reasoning": "ETF inflows accelerating, halving supply shock imminent"
    },
    "drivers": [
      {
        "name": "ETF News",
        "weight": 2.0,
        "direction": "bullish",
        "monitoring": {
          "keywords": ["bitcoin ETF inflows", "bitcoin institutional"],
          "sources": ["web_search", "newswire"]
        }
      }
    ],
    "escalation": {
      "signalScoreThreshold": 0.3,
      "highConfidenceThreshold": 0.8,
      "maxWakeFrequency": "1 per 15m",
      "batchWindow": "5m"
    },
    "tradeRules": {
      "entry": { "minEdge": 0.05 },
      "autoActions": { "stopLoss": -0.10, "takeProfit": 0.25, "trailingStop": -0.05 },
      "sizing": { "method": "edgeScaled", "maxPosition": 500, "maxPortfolioPct": 20, "maxTradesPerDay": 5 }
    }
  }' \
  --poll-interval 10
```

### Step 5: Activate and monitor

```bash
npx @vincentai/cli@latest trading-engine activate --key-id <KEY_ID> --strategy-id <STRATEGY_ID>
npx @vincentai/cli@latest trading-engine events --key-id <KEY_ID>
```

---

## Background Workers

The Trading Engine runs two independent background workers:

1. **Strategy Engine Worker** — Ticks every 30s, checks which strategy drivers are due, fetches new data, scores signals, and invokes the LLM when the escalation threshold is met. Hooks into venue WebSocket feeds (Polymarket and HyperLiquid) for real-time price trigger evaluation.
2. **Trade Rule Worker** — Monitors prices in real-time via WebSocket (with polling fallback), evaluates stop-loss/take-profit/trailing stop rules, executes trades when conditions are met. Supports both Polymarket and HyperLiquid venues.

**Circuit Breaker:** Both workers use a circuit breaker pattern. If a venue API fails 5+ consecutive times, the worker pauses and resumes after a cooldown. Check status with:

```bash
npx @vincentai/cli@latest trading-engine status --key-id <KEY_ID>
```

## Best Practices

1. **Start with `confidence: 0.5`** and let the LLM adjust — avoid overconfidence in the initial thesis
2. **Weight drivers by importance** — a driver with `weight: 3.0` has 3x the signal score contribution of `weight: 1.0`
3. **Use `edgeScaled` sizing** for adaptive position sizes based on thesis confidence and edge
4. **Set `maxPortfolioPct`** to limit exposure — even high-confidence strategies shouldn't risk the entire portfolio
5. **Set both stop-loss and take-profit** on positions for protection (via `autoActions` in the config or standalone rules)
6. **Use `thesisInvalidation` exit rules** to define explicit conditions that should trigger position exits
7. **Monitor invocation costs** — check the costs command regularly
8. **Iterate with versions** — duplicate a strategy to tweak the config without losing the original
9. **Don't set triggers too close** to current price — market noise can trigger prematurely

## Example User Prompts

When a user says:

- **"Create a strategy to monitor AI tokens"** → Create strategy with web search + Twitter drivers
- **"Set a stop-loss at 40 cents"** → Create STOP_LOSS rule
- **"What has my strategy been doing?"** → Show invocations for the strategy
- **"How is my strategy performing?"** → Show performance metrics
- **"How much has the trading engine cost me?"** → Show cost summary
- **"Pause my strategy"** → Pause the strategy
- **"Make a new version with a different thesis"** → Duplicate, then update the draft
- **"Set a 5% trailing stop"** → Create TRAILING_STOP rule

## Output Format

Strategy creation:

```json
{
  "strategyId": "strat-123",
  "name": "BTC Momentum",
  "status": "DRAFT",
  "version": 1
}
```

Rule creation:

```json
{
  "ruleId": "rule-456",
  "ruleType": "STOP_LOSS",
  "triggerPrice": 0.4,
  "status": "ACTIVE"
}
```

LLM invocation log entries:

```json
{
  "invocationId": "inv-789",
  "strategyId": "strat-123",
  "trigger": "web_search",
  "actions": ["place_trade"],
  "costUsd": 0.12,
  "createdAt": "2026-02-26T12:00:00.000Z"
}
```

## Error Handling

| Error                       | Cause                                             | Resolution                                           |
| --------------------------- | ------------------------------------------------- | ---------------------------------------------------- |
| `401 Unauthorized`          | Invalid or missing API key                        | Check that the key-id is correct; re-link if needed  |
| `403 Policy Violation`      | Trade blocked by server-side policy               | User must adjust policies at heyvincent.ai           |
| `402 Insufficient Credit`   | Not enough credit for LLM invocation              | User must add credit at heyvincent.ai                |
| `INVALID_STATUS_TRANSITION` | Strategy can't transition to requested state      | Check current status (e.g., only DRAFT can activate) |
| `CIRCUIT_BREAKER_OPEN`      | Polymarket API failures triggered circuit breaker | Wait for cooldown; check status command              |
| `429 Rate Limited`          | Too many requests or concurrent LLM invocations   | Wait and retry with backoff                          |
| `Key not found`             | API key was revoked or never created              | Re-link with a new token from the wallet owner       |

## Important Notes

- **Authorization:** All endpoints require the API key for the relevant venue (Polymarket or HyperLiquid wallet key)
- **Local only:** The API listens on `localhost:19000` — only accessible from the same VPS
- **No private keys:** All trades use the Vincent API — your private key stays secure on Vincent's servers
- **Policy enforcement:** All trades (both LLM and standalone rules) go through Vincent's policy checks
- **Idempotency:** Rules only trigger once. LLM invocations are deduplicated by driver state.
