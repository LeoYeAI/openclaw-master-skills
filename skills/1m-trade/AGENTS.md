# Agent Composition Handbook

This document defines a set of preset Agents used to automate complex on-chain workflows composed of the `1m-trade-news`, and `1m-trade-dex` skills. You can invoke these Agents directly to achieve specific goals.

## Agent list

### 1) Agent: Market Scout
- **Invocation name**: `market-scout`
- **Description**: Runs a daily market health check. If the user provides no specific instructions, this agent can produce a comprehensive market snapshot.
- **Workflow**:
  1. **Trigger**: user asks "How is the market today?" or a scheduled run.
  2. **Execution**:
     a. Call `1m-trade-news` → Scenario 1: Market snapshot.
     b. Fetch sentiment indicator, important newsflashes, BTC ETF net flow, and daily on-chain tx volume in parallel.
  3. **Output**: a formatted report with a data summary and brief interpretation (e.g. if sentiment < 20, highlight a potential opportunity zone).
- **Use cases**: pre-open review, quick market sentiment check, decision support.

### 2) Agent: Wallet Setup
- **Invocation name**: `wallet-setup`
- **Description**: Directs users to **[1M-Trade](https://www.1m-trade.com)** for **wallet creation and management** in the browser; then guides **`hl1m init-wallet`** with wallet **public address** + **proxy (API) private key**. Does not bridge assets.
- **Workflow**:
  1. **Trigger**: user wants to connect or configure trading (e.g. "init wallet", "set up Hyperliquid", "configure my API/proxy key", or non-English phrases with the same meaning plus labeled wallet address and proxy private key).
  2. **Execution**:
     a. For **creating/managing** the wallet in the UI, send the user to **[1M-Trade](https://www.1m-trade.com)**.
     b. Call `1m-trade-dex` → **Wallet initialization** and **Natural-language binding** (`skills/1m-trade-dex/SKILL.md`).
     c. If the user sends **both** address and proxy key in one message (labeled, e.g. `wallet address` / `proxy private key` or equivalent in other languages), parse and **invoke** `hl1m init-wallet --address … --pri_key …` in a trusted shell; do not echo full keys in chat.
     d. Otherwise, show placeholders only and ask the user to run locally:
        `hl1m init-wallet --address 0xYourWalletAddress --pri_key 0xYourProxyPrivateKey`
     e. **Critical**: **Never** use the wallet **main / master private key** for `init-wallet` — only the **proxy** key intended for automation/API use.
  3. **Output**: step-by-step checklist; confirm success with `hl1m query-user-state` after init. Do not repeat full private keys in assistant-visible text.
- **Security note**: Prefer local init without pasting keys. If the user voluntarily pastes address + proxy key for binding, pass values only to the `hl1m` CLI invocation; do not store or quote them in chat.

### 3) Agent: Trend Trader
- **Invocation name**: `trend-trader`
- **Description**: Combines macro fund flows and micro price action to produce conditional trade ideas or simulated trades.
- **Workflow**:
  1. **Trigger**: user asks "Can I buy BTC now?" or "Where is money flowing?"
  2. **Execution**:
     a. Call `1m-trade-news` → Scenario 2: Fund flow analysis.
     b. Call `1m-trade-news` → Scenario 3: Macro environment.
     c. If conditions are met (e.g. stablecoin expansion + top net inflow on a chain + macro not bearish):
        i. Call `1m-trade-dex` to query live market data.
        ii. Generate a trade idea report including target, macro rationale, on-chain rationale, and current price.
  3. **Output**: a report with bullish/bearish rationale and recommended targets. **Do not execute trades automatically**; require final user confirmation.
- **Use cases**: data-driven decision support for manual traders.

### 4) Agent: News-driven Trade Alert
- **Invocation name**: `news-alert-trader`
- **Description**: Monitors configured news keywords and, when triggered, checks related asset market data to provide fast reaction context.
- **Workflow**:
  1. **Configure**: user pre-defines keywords (e.g. "ETF approval", "hack", "mainnet launch").
  2. **Trigger**: periodically call `1m-trade-news` → Scenario 5: Keyword search (e.g. every 5 minutes).
  3. **Execution**: when new items contain keywords:
     a. Extract related assets from the news text (e.g. "Ethereum" → ETH).
     b. Call `1m-trade-dex` to query latest price/order book.
     c. Call `1m-trade-dex` to get recent kline.
  4. **Output**: alert including title, summary, related assets, price before/after, order book pressure change, and short-term kline trend.
- **Use cases**: capture sudden news-driven moves for short-term traders.

### 5) Agent: HIP-3 TradFi Arb Monitor
- **Invocation name**: `hip3-arb-monitor`
- **Description**: Monitors HIP-3 markets (e.g. stocks/commodities) around TradFi open to find spread/arb opportunities.
- **Workflow**:
  1. **Trigger**: run around US equity open (ET 9:30 AM).
  2. **Execution**:
     a. Call `1m-trade-dex` to list HIP-3 markets and filter targets (e.g. `xyz:AAPL`, `xyz:GOLD`).
     b. For each target in parallel:
        i. Get Hyperliquid price.
        ii. (Simulated) fetch TradFi open/spot price from an external API (not provided; mark as TODO).
        iii. Compute spread percentage.
  3. **Output**: spread report highlighting assets above a threshold (e.g. 2%) and optionally search related news via `1m-trade-news`.
- **Use cases**: cross-market arbitrage and tokenized TradFi monitoring.

## How to use these agents
You can invoke agents via natural language or structured commands.

Examples:
- Natural language: "Start `market-scout` and give me a morning report."
- Structured: `/agent run market-scout`
- Combined: "Run `market-scout` first; if sentiment is bullish, then run `wallet-setup` so I can configure `hl1m init-wallet` before trading."

## Configuration & extension
Each agent definition is a "script". You can modify this file to:
1. **Adjust flows**: change internal skill call order or condition logic.
2. **Create new agents**: combine skills with new logic using the same format.
3. **Parameterize**: extract fixed parameters (keywords, thresholds) into configurable variables.

---
*`AGENTS.md` together with the root `SKILL.md` forms the "strategy layer" and "tactics layer" of this skill library: automation workflows and interactive service definitions.*