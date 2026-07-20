---
name: pkedge
description: "Monitor Polymarket prediction markets, spot mispricings between crowd probabilities and real-world evidence, track whale positioning from the top-50 leaderboard wallets, and detect fresh wallet insider signals. Supports four modes: SCAN (daily digest of flagged markets), DEEP DIVE (full single-market analysis with web search evidence), WHALE WATCH (consensus detection across top trader positions), and INSIDER WATCH (fresh wallet large-position detection)."
homepage: https://polymarket.com
metadata: { "openclaw": { "emoji": "📈", "requires": { "bins": ["curl", "node"], "env": ["PKEDGE_TELEGRAM_TOKEN_FREE", "PKEDGE_TELEGRAM_CHAT_FREE", "PKEDGE_TELEGRAM_TOKEN_TRADER", "PKEDGE_TELEGRAM_CHAT_TRADER"] } } }
version: 1.1.0
author: pkedge
license: MIT
---

# PKEdge — Polymarket Intelligence Skill

## Overview
PKEdge is an OpenClaw skill that monitors Polymarket prediction markets, spots mispricings between crowd probabilities and real-world evidence, tracks whale positioning from top-50 leaderboard wallets, and detects fresh wallet insider signals. It operates in four modes: SCAN, DEEP DIVE, WHALE WATCH, and INSIDER WATCH.

**Intel only. Never recommends trading. Always appends "Not financial advice. DYOR."**

**Schedule:**
- 8:00 AM ET — Daily SCAN digest (Trader + Free channels)
- 8:05 AM ET — Morning Whale Watch, 48h lookback (Trader only)
- 8:10 AM ET — Morning Insider Watch, 48h lookback (Trader only)
- 4:00 PM ET — Afternoon Whale Watch, 24h lookback (Trader only)
- 4:05 PM ET — Afternoon Insider Watch, 24h lookback (Trader only)
- Every 30 min — Real-time consensus alert when 3+ whales enter the same market
- Every 30 min — Real-time insider alert when fresh wallet drops >$50K on one market

---

## Install
1. `cd` into the skill folder and run `npm install`
2. Create a `.env` file with your Telegram credentials:
   - `PKEDGE_TELEGRAM_TOKEN_FREE` — bot token for the free channel
   - `PKEDGE_TELEGRAM_CHAT_FREE` — chat ID for the free channel
   - `PKEDGE_TELEGRAM_TOKEN_TRADER` — bot token for the trader channel
   - `PKEDGE_TELEGRAM_CHAT_TRADER` — chat ID for the trader channel
3. Run `node cron.js` to start scheduled jobs, or configure launchd to run on boot

---

## Trigger Phrases

Claude activates this skill when the user says anything matching these patterns:

### SCAN mode
- "pkedge scan"
- "run the pkedge scan"
- "prediction market scan"
- "polymarket scan"
- "what markets are flagged today"
- "pkedge morning digest"

### DEEP DIVE mode
- "pkedge deep dive [question or topic]"
- "analyze this market: [question]"
- "pkedge analyze: [question]"
- "what does pkedge think about [topic]"
- "is [market question] mispriced"
- "/deepdive [question]"

### WHALE WATCH mode
- "pkedge whale watch"
- "whale watch"
- "what are the whales doing"
- "polymarket whale positions"
- "pkedge whales"

### INSIDER WATCH mode
- "pkedge insider watch"
- "insider watch"
- "fresh wallet alert"
- "any insider activity"
- "pkedge insiders"
- "suspicious wallets"
- "new money polymarket"

---

## File Locations

```
~/Projects/pkedge/
  fetch.js      — all Polymarket API calls (no auth required)
  analyze.js    — scoring, flagging, conviction logic
  formatter.js  — Telegram message templates
  deliver.js    — sends to Telegram channels
  cron.js       — scheduled runner
```

---

## Mode: SCAN

**Purpose:** Fetch the top 200 active Polymarket markets by volume, flag anomalies, rank them, deliver the digest.

**Step-by-step:**

1. Call `fetchActiveMarkets()` from fetch.js
   - Returns normalized market objects with yesPrice, noPrice, volume, volume24hr, endDate
   - Filters to markets with >$10K all-time volume

2. Call `runScanFlags(markets)` from analyze.js
   - Applies 5 flags: VOLUME_SURGE, SPREAD_ANOMALY, VOLUME_SPIKE, EXTREME_LOW/HIGH, RESOLVING_SOON
   - Each flag carries a point value; scanScore is the sum
   - Returns flagged markets sorted by score descending

3. For the top 5 flagged markets, call web search on each question to check for recent news
   - Search: `"[market question]" news today`
   - Note any breaking news, resolution events, or catalysts
   - Add this context to the evidence for each market

4. Call `formatScanDigest(flaggedMarkets, 5)` from formatter.js for Trader channel
5. Call `formatScanPreview(flaggedMarkets[0])` from formatter.js for Free channel
6. Deliver via deliver.js `sendToTrader()` and `sendToFree()`

**Output shape:**
```
🔍 PKEdge Morning Scan — Mon, Mar 9, 2026
_5 markets flagged from top 200 by volume_
──────────────────────
1. *Will the Fed cut rates at the March 2026 meeting?*
   🔥 HIGH  Crowd: YES 23.1%  |  24h Vol: $142K  |  Score: 7
   👀 Volume spike: 4.2x average daily volume — unusual activity
   ⏰ Resolves in 3.2 days
...
```

---

## Mode: DEEP DIVE

**Purpose:** Full analysis of a single market. Claude reasons over crowd probability vs. real-world evidence, assesses fair value, and outputs a structured Crowd vs. Reality report.

**Step-by-step:**

1. Parse the market question from the user input

2. Call `searchMarkets(query)` from fetch.js to find the matching Polymarket market
   - If multiple results, pick the one with the highest volume
   - If zero results, tell the user no matching market was found on Polymarket

3. Fetch enriched market data:
   - `fetchPriceHistory(market.id, '1d')` — get price history with daily candles (note: '1d' sets candle granularity, not lookback window; the API returns available history for the market)
   - `fetchBookDepth(market.clobTokenIds[0])` — get order book depth (YES token)
   - Compute price velocity from history: (most recent price − price from ~24h prior) in percentage points

4. Call `analyzeMarket(market, bookDepth)` from analyze.js
   - Returns analysis object with flags, spread note, resolution note, volume note

5. Web search × 3 to gather evidence:
   - Search 1: `"[market question]" news [current month year]`
   - Search 2: `[core topic] forecast prediction [current year]`
   - Search 3: `[core topic] expert analysis probability`
   - Synthesize key findings into 3–5 bullet points (each max 1 sentence)

6. Estimate fair value:
   - Based on web search evidence, base rates, and any quantitative anchors found
   - Express as a probability range: e.g., "52–60% YES"
   - Use the midpoint for conviction calculation

7. Call `computeConviction(crowdPct, fairPct)` from analyze.js
   - Returns { delta, direction, conviction: HIGH/MEDIUM/LOW, label }

8. Call `formatDeepDive(analysis, conviction, evidenceLines)` from formatter.js

9. Deliver via `sendToTrader()` (Deep Dive is Trader-only)

**Output shape:**
```
🧠 PKEdge Deep Dive
_Mar 9, 2026_
──────────────────────
*Will the Fed cut rates at the March 2026 meeting?*

CROWD PRICE
YES: 23.1%  |  NO: 76.9%

MARKET DATA
⏰ Resolves in 3.2 days
💰 All-time: $2.1M  |  24h: $142K
👀 Spread: 1.2¢ (bid 0.229 / ask 0.241)
✅ Order book: DEEP ($340K within 10¢)

EVIDENCE
✅ Fed funds futures pricing ~18% probability of March cut as of today
✅ Powell speech last week signaled patience — no urgency to cut
✅ February CPI came in at 2.9%, above 2% target
✅ No emergency FOMC meeting called — standard meeting format
✅ Metaculus consensus: 15-22% YES

──────────────────────
PKEDGE ASSESSMENT
🔥 Conviction: HIGH
Direction: NO underpriced
Delta: 18 percentage points from crowd
_Crowd is 18 pts away from fair value — strong signal_

`Not financial advice. DYOR. Prediction markets carry risk.`
```

---

## Mode: WHALE WATCH

**Purpose:** Monitor top-50 Polymarket traders by all-time profit for new positions. Detect consensus (3+ whales entering the same market) and fire real-time alerts.

**Runs twice daily:**
- **8:05 AM ET** — 48h lookback window. Catches anything that moved overnight or over the weekend.
- **4:00 PM ET** — 24h lookback window. Covers the full trading day.

**Step-by-step:**

1. Call `fetchLeaderboard(50)` from fetch.js
   - Returns top 50 wallets by all-time profit
   - Each entry has: address, name (if set), pnl, volume

2. Extract all wallet addresses and call `fetchMultiWalletPositions(addresses)`
   - This loops through all 50 wallets with a 150ms delay between calls
   - Returns a Map of address → positions[]

3. Call `buildWhaleReport(leaderboard, walletPositions, windowHours)` from analyze.js
   - Morning run (8:05 AM): pass `48` as windowHours — covers overnight + weekend
   - Afternoon run (4:00 PM): pass `24` as windowHours — covers the trading day
   - Filters to positions opened within the window with >$1K value
   - Detects consensus: 3+ whales in the same market
   - Sorts by position size and consensus count

4. Call `formatWhaleWatch(report)` from formatter.js

5. Deliver via `sendToTrader()`

6. For any consensus markets not yet alerted today:
   - Call `formatWhaleAlert(consensusMarket, latestPosition)` from formatter.js
   - Deliver as an immediate alert (separate message, not part of digest)
   - Mark as alerted in the dedup set

**Output shape:**
```
🐋 PKEdge Whale Watch — Mon, Mar 9, 2026
_Top 50 traders scanned | Last 24h_
──────────────────────
🔥 CONSENSUS DETECTED (1 market)

1. *Will the Fed cut rates at the March 2026 meeting?*
   🐋x4 whales  |  💰$48K combined  |  Direction: *NO*
   _PredictWiz, 0x4f2a…1b3c, MarketMaker99 +1 more_

──────────────────────
NEW POSITIONS (6 total)

🐋 *PredictWiz*  →  NO
   _Will the Fed cut rates at the March 2026 meeting?_
   $22K @ 77¢  |  2h ago
...
```

---

## Mode: INSIDER WATCH

**Purpose:** Detect fresh wallets placing unusually large positions — a classic signal of informed trading. Insiders often create new wallets specifically to avoid leaderboard detection. Two or more fresh wallets entering the same market within 6 hours is treated as a coordinated signal.

**Fresh wallet definition:**
- Wallet age < 30 days (based on first trade timestamp)
- Total lifetime trade count < 20
- Single position size > $5K

**Alert tiers:**
- > $5K single position = 👀 WATCH (held for digest)
- > $25K single position = ⚠️ ALERT (held for digest)
- > $50K single position = 🚨 IMMEDIATE (fires real-time, does not wait for digest)
- 2+ fresh wallets same market within 6h = 🚨 COORDINATED (fires real-time regardless of size)

**Runs twice daily:**
- **8:10 AM ET** — 48h lookback
- **4:05 PM ET** — 24h lookback
- **Every 30 min** — real-time scan for >$50K single fresh wallet drops (lower amounts held for digest)

**Step-by-step:**

1. Call `fetchActiveMarkets()` — sort by 24h volume, take top 30 as scan targets

2. Call `fetchLeaderboard(50)` — build a Set of known addresses to exclude

3. For each top market, call `fetchRecentTrades(market.clobTokenIds[0], windowHours)` from fetch.js
   - Collect unique maker/taker addresses from trades
   - Filter to trades with sizeUSD > $5K
   - Exclude addresses in the leaderboard Set

4. For each unknown address with a qualifying trade, call `fetchWalletProfile(address)` from fetch.js
   - Returns { firstTradeAt, tradeCount, totalVolume }
   - Flag as fresh if: wallet age ≤ 30 days AND tradeCount ≤ 20

5. Call `buildInsiderReport(freshSignals, windowHours)` from analyze.js
   - Groups fresh wallet positions by market
   - Detects coordinated entries: 2+ fresh wallets same market within 6h
   - Scores each signal (see Scoring Reference)
   - Returns: { signals, coordinatedMarkets, immediateAlerts }

6. Call `formatInsiderWatch(report)` from formatter.js

7. Deliver via `sendToTrader()`

8. For IMMEDIATE-tier (>$50K) or COORDINATED signals not yet alerted today:
   - Call `formatInsiderAlert(signal, isCoordinated)` from formatter.js
   - Deliver as a real-time alert
   - Mark in the dedup set

**Output shape — daily digest:**
```
🕵️ PKEdge Insider Watch — Mon, Mar 9, 2026
_Unknown wallets scanned | Last 24h_
──────────────────────
🚨 COORDINATED SIGNAL (1 market)

*Will the Fed cut rates at the March 2026 meeting?*
   🆕x2 fresh wallets  |  💰$61K combined  |  Direction: *NO*
   _First two entered within 2h of each other_
   Wallet: 0x7c3b…9a12 — Age: 4 days | 3 trades | $38K → NO
   Wallet: 0x2d1f…4e87 — Age: 11 days | 7 trades | $23K → NO

──────────────────────
WATCH LIST (3 signals)

👀 *Fresh wallet — 0x9f4a…2c31*
   _Will Trump win the 2026 midterms?_
   $8K → YES @ 41¢  |  6h ago
   Age: 18 days | 12 trades lifetime

`Not financial advice. DYOR. Fresh wallet signals are circumstantial.`
```

**Output shape — real-time alert:**
```
🚨 PKEdge Insider Alert
_Fresh wallet just dropped big money_

*Will the Fed cut rates at the March 2026 meeting?*
Direction: NO  |  Size: $38K @ 77¢
Wallet: `0x7c3b…9a12`
Age: 4 days  |  3 trades lifetime

`Not financial advice. DYOR. Circumstantial signal only.`
```

---

## API Reference (All Free, No Auth)

| Endpoint | Purpose |
|---|---|
| `GET https://gamma-api.polymarket.com/markets?active=true&limit=200` | Market discovery |
| `GET https://gamma-api.polymarket.com/markets?slug={slug}` | Single market by slug |
| `GET https://gamma-api.polymarket.com/prices-history?market={id}&interval=1d` | Price history |
| `GET https://clob.polymarket.com/book?token_id={tokenId}` | Order book |
| `GET https://clob.polymarket.com/midpoint?token_id={tokenId}` | Midpoint price |
| `GET https://clob.polymarket.com/bbo?token_id={tokenId}` | Best bid/offer |
| `GET https://clob.polymarket.com/trades?token_id={tokenId}&limit=500` | Recent market trades (Insider Watch) |
| `GET https://data-api.polymarket.com/v1/leaderboard?timePeriod=ALL&orderBy=PNL&limit=50` | Top traders |
| `GET https://data-api.polymarket.com/positions?user={address}` | Wallet positions |
| `GET https://data-api.polymarket.com/trades?user={address}&limit=500` | Wallet trade history + profile |

---

## Environment Variables

```
PKEDGE_TELEGRAM_TOKEN_FREE=
PKEDGE_TELEGRAM_CHAT_FREE=
PKEDGE_TELEGRAM_TOKEN_TRADER=
PKEDGE_TELEGRAM_CHAT_TRADER=
```

No market data API keys needed. Polymarket APIs are fully public.

---

## Subscription Tiers

| Tier | Price | What They Get |
|---|---|---|
| FREE EDGE | $0 | 1 market preview from daily SCAN |
| WATCHER | $9/mo | Full 5-market SCAN digest, @PKEdgeBot basic (3 lookups/day) |
| TRADER | $29/mo | Unlimited DEEP DIVE, WHALE WATCH, INSIDER WATCH, all real-time alerts |
| QUANT | $99/mo | Raw scoring API, Discord quant channel, historical accuracy log |

---

## Scoring Reference

**SCAN Score Flags:**

| Flag | Points | Trigger |
|---|---|---|
| VOLUME_SPIKE | 3 | 24h volume >3× average daily |
| VOLUME_SURGE | 2 | >25% of all-time volume traded in last 24h |
| RESOLVING_SOON | 2 | Resolves within 7 days |
| SPREAD_ANOMALY | 1 | YES + NO gap >6¢ |
| EXTREME_LOW / HIGH | 1 | Price ≤10% or ≥90% on high volume |

**Score thresholds:** 2 = WATCH | 4 = ELEVATED | 6+ = HIGH

**Conviction thresholds:** <7 pts = LOW | 7-14 pts = MEDIUM | 15+ pts = HIGH

**Insider Signal Score:**

| Factor | Points |
|---|---|
| Position > $5K | 1 |
| Position > $25K | 3 |
| Position > $50K | 3 |
| Wallet age < 7 days | 3 |
| Wallet age 7–14 days | 2 |
| Wallet age 15–30 days | 1 |
| Trade count < 5 | 2 |
| Trade count 5–10 | 1 |
| Coordinated (2+ fresh wallets same market within 6h) | +5 bonus |

**Insider alert thresholds:** 3 = WATCH | 6 = ALERT | 9+ = COORDINATED / IMMEDIATE

---

## Guardrails

- Never state that a market "will" resolve in a particular direction
- Never say "buy YES" or "buy NO" — frame as "YES appears underpriced relative to evidence"
- Always append `Not financial advice. DYOR. Prediction markets carry risk.`
- If web search returns no useful news, state that clearly rather than fabricating evidence
- If a market has a thin order book (<$10K depth), always flag it prominently
- Do not deep-dive markets with <$5K total volume — not enough liquidity to be meaningful
- For Insider Watch: never accuse wallets of wrongdoing — frame as "unusual pattern" not "insider trading"
- Fresh wallet signals are circumstantial — always note that large new positions can have innocent explanations
