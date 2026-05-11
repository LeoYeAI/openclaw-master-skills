---
name: "btc-signals-pro"
description: "Real-time Bitcoin trading intelligence API providing market data, AI trade signals, derivatives flow, liquidation heatmaps, live crypto news, economic calendar, historical OHLCV, and 50+ data sources for AI-driven trade decisions and automated trading bots."
author: "BTC Signals Pro"
version: "1.2.0"
price: "free"
homepage: "https://github.com/ricklaughhunn/btc-signals-pro"
config:
  BTC_SIGNALS_API_KEY:
    required: true
    description: "Your BTC Signals Pro API key. Get one at https://btcsignals.pro/pricing — the Pro data plan is $20/mo."
metadata:
  clawdbot:
    requires:
      env: ["BTC_SIGNALS_API_KEY"]
    primaryEnv: "BTC_SIGNALS_API_KEY"
---

# Skill: BTC Signals Pro

> **This skill is free to install.** A Pro data plan ($20/mo) is required to access the API. Sign up at [btcsignals.pro/pricing](https://btcsignals.pro/pricing) to get your API key.

## Purpose

You are a Bitcoin trading intelligence assistant with access to institutional-grade market data from 50+ sources. Use the BTC Signals Pro API to provide real-time market analysis, trade recommendations, derivatives flow data, key price levels, live crypto news, and historical market data. Help users make informed trading decisions or build automated trading strategies. Never print the full API key in chat.

## Capabilities

- **Market Analysis:** BTC price, 24h change, Fear & Greed, Trade Score 0-100
- **AI Trade Signals:** scalp (4-12hr) and swing (multi-day) with entry/SL/TP/grade/rationale
- **Derivatives Intelligence:** L/S ratios (3 exchanges), funding, OI, CVD, liquidations, options max pain, ETF flows
- **Price Level Mapping:** pivots, fibs, Volume Profile, swing H/L, unified confluence engine (~49 weighted levels)
- **Liquidation Heatmaps:** zones across 24h, 7d, 30d timeframes
- **Live Crypto News:** real-time crypto news feed with headline, source, date, and symbol filtering
- **News & Macro:** severity-scored breaking alerts, DXY, Gold, VIX, Treasury, live economic calendar
- **Economic Calendar:** live upcoming events (FOMC, CPI, NFP, GDP) with actual/estimate/previous values and impact ratings
- **Historical Data:** daily OHLCV with date range queries for backtesting and analysis
- **Historical Signals:** past 1-30 days of signals

## Instructions & Workflow

### Authentication

- **Header:** `X-API-Key: {{BTC_SIGNALS_API_KEY}}`
- **Base URL:** `https://api.btcsignals.pro/v1`
- **Rate Limit:** 60 requests/minute

### Initialization

1. Check if `BTC_SIGNALS_API_KEY` is available in the skill config.
2. If not configured, ask the user to subscribe and get a key at https://btcsignals.pro/pricing
3. Verify the key works with `GET /v1/account` before making other calls.

### Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/v1/signal/latest` | GET | Current signal: trade score, action, direction, narrative |
| `/v1/signal/history?days=7` | GET | Historical signals (1-30 days) |
| `/v1/score` | GET | Trade score 0-100 + component breakdown |
| `/v1/trades/scalp` | GET | AI scalp trade (4-12hr): direction, entry, SL, TP1-2, grade, R:R |
| `/v1/trades/swing` | GET | AI swing trade (multi-day): direction, entry, SL, TP1-3, grade, status |
| `/v1/market/overview` | GET | Price, 24h change, volume, Fear & Greed |
| `/v1/market/ls-ratios` | GET | Long/Short ratios (Binance, Bybit, Bitget) + average |
| `/v1/market/order-book` | GET | Bid/ask depth, imbalance, support/resistance |
| `/v1/market/funding` | GET | Funding rates across exchanges |
| `/v1/market/oi` | GET | Open interest + changes |
| `/v1/market/history` | GET | Historical daily OHLCV with date range params |
| `/v1/derivatives/options` | GET | Max pain, put/call ratio, hours to expiry |
| `/v1/derivatives/liquidations` | GET | Long/short liquidations (24h), net pressure |
| `/v1/derivatives/cvd` | GET | CVD 1h + 15m, trend, net buy pressure |
| `/v1/derivatives/etf` | GET | Bitcoin ETF flow data |
| `/v1/technicals` | GET | RSI, MACD, EMA, Bollinger Bands, ATR |
| `/v1/levels` | GET | Pivots, fibs, VP, confluence zones, market structure |
| `/v1/fractals` | GET | DTW fractal pattern match probabilities |
| `/v1/heatmaps` | GET | Liquidation heatmap zones (24h, 7d, 30d) |
| `/v1/news` | GET | Breaking news alerts (severity 1-10) |
| `/v1/news/crypto` | GET | Live crypto news feed with headlines, sources, and symbol filtering |
| `/v1/macro` | GET | DXY, Gold, VIX, Treasury rates |
| `/v1/calendar` | GET | Live economic calendar with actual/estimate/previous values and impact ratings |
| `/v1/account` | GET | Subscription status + usage |

### Execution Steps

When a user asks about Bitcoin markets or trading:

1. **Always check news first** — `GET /v1/news` — warn the user immediately if any alert has severity >= 7.
2. **Get the market snapshot** — `GET /v1/market/overview` and `GET /v1/score` to establish current conditions.
3. **For trade recommendations** — `GET /v1/trades/scalp` and `GET /v1/trades/swing` to get AI-generated trade setups.
4. **For deeper analysis** — fetch relevant endpoints based on what the user needs (derivatives, levels, heatmaps, macro, etc.).
5. **For crypto news context** — `GET /v1/news/crypto` to get the latest crypto headlines and market narratives.
6. **For macro event risk** — `GET /v1/calendar` to check upcoming high-impact economic events with actual vs estimate data.
7. **For historical analysis** — `GET /v1/market/history?from=YYYY-MM-DD&to=YYYY-MM-DD` for backtesting or trend context.

#### Curl Examples

```bash
# Get current trade score
curl -s "https://api.btcsignals.pro/v1/score" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get latest signal
curl -s "https://api.btcsignals.pro/v1/signal/latest" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get scalp trade setup
curl -s "https://api.btcsignals.pro/v1/trades/scalp" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get swing trade setup
curl -s "https://api.btcsignals.pro/v1/trades/swing" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get market overview
curl -s "https://api.btcsignals.pro/v1/market/overview" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get L/S ratios
curl -s "https://api.btcsignals.pro/v1/market/ls-ratios" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get historical daily OHLCV (last 30 days)
curl -s "https://api.btcsignals.pro/v1/market/history?from=2026-02-11&to=2026-03-13" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get liquidation heatmap
curl -s "https://api.btcsignals.pro/v1/heatmaps" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get key price levels
curl -s "https://api.btcsignals.pro/v1/levels" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get breaking news alerts
curl -s "https://api.btcsignals.pro/v1/news" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get live crypto news feed (latest 20)
curl -s "https://api.btcsignals.pro/v1/news/crypto?limit=20" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get Bitcoin-specific crypto news
curl -s "https://api.btcsignals.pro/v1/news/crypto?symbol=BTCUSD&limit=10" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get signal history (past 7 days)
curl -s "https://api.btcsignals.pro/v1/signal/history?days=7" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get macro indicators
curl -s "https://api.btcsignals.pro/v1/macro" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Get live economic calendar
curl -s "https://api.btcsignals.pro/v1/calendar" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"

# Check account status
curl -s "https://api.btcsignals.pro/v1/account" \
  -H "X-API-Key: {{BTC_SIGNALS_API_KEY}}"
```

### Data Interpretation Rules

#### Trade Score (0-100)

| Score Range | Interpretation |
|---|---|
| 80-100 | HIGH CONVICTION BUY |
| 65-79 | BUY |
| 35-64 | NEUTRAL |
| 20-34 | SELL |
| 0-19 | HIGH CONVICTION SELL |
| 0 (exact) | HALT — critical news event, do not trade |

#### Score Components

- **Temporal (-10 to +10):** Time-of-day volatility adjustment. Peak volatility = Tuesday 8 AM CST.
- **Sentiment (-15 to +15):** Fear & Greed Index (contrarian weighting) combined with AI-scored news sentiment.
- **L/S Score (-25 to +25, 1.5x weight):** Contrarian Long/Short ratio signal. This is the DOMINANT FACTOR in the trade score. When retail is heavily long, the score pushes bearish, and vice versa.
- **Liquidity Multiplier (0.5-2.0):** Amplifies or dampens the L/S Score based on OI changes, order book imbalance, funding rates, and heatmap proximity.
- **Confluence (-15 to +15):** Directional weight derived from ~49 key price levels (pivots, fibs, Volume Profile, swing H/L). Positive = price above key levels (bullish), negative = below (bearish).

#### Long/Short Ratios — CONTRARIAN INTERPRETATION

- `avg_ls_ratio > 1.5` = retail heavily long = **BEARISH** signal (fade the crowd)
- `avg_ls_ratio < 0.7` = retail heavily short = **BULLISH** signal (fade the crowd)
- `avg_ls_ratio ~ 1.0` = balanced = **NEUTRAL**

Always interpret L/S ratios as a contrarian indicator. The crowd is usually wrong at extremes.

#### Heatmap Zones — Liquidity Magnets

- Price is drawn TOWARD liquidation clusters before reversing.
- `cv_nearest_zone_direction`: tells you if the nearest cluster is above or below current price.
- Zones **below** current price = short squeeze targets (cascading short liquidations push price up).
- Zones **above** current price = long squeeze targets (cascading long liquidations push price down).

#### CVD (Cumulative Volume Delta)

- Positive `cvd_1h` = net buying pressure = bullish
- Negative `cvd_1h` = net selling pressure = bearish
- Compare `cvd_1h` vs `cvd_15m` for trend acceleration/deceleration.

#### Confluence Direction (from /v1/levels)

- `confluence_direction`: BULLISH or BEARISH — the net directional weight of all ~49 price levels.
- `confluence_direction_strength`: 0.0 to 1.0 — how strong the directional agreement is.
- `confluence_magnet_price`: the nearest high-weight cluster price — acts as a magnet for price action.

#### Crypto News Sentiment (from /v1/news/crypto)

- Scan headlines for bullish/bearish bias to gauge market narrative.
- Cross-reference with `/v1/news` severity-scored alerts for high-impact events.
- Use `symbol` filter to focus on BTC-specific news vs broader crypto market.

#### Economic Calendar Events (from /v1/calendar)

- Events with `impact: "High"` can cause 2-5% BTC swings within hours.
- Compare `actual` vs `estimate` for surprise factor — larger surprises = larger moves.
- `actual: null` means the event hasn't happened yet — trade cautiously ahead of it.
- Key events: FOMC Rate Decision, CPI, Non-Farm Payrolls, GDP, PCE Price Index.

#### Historical OHLCV (from /v1/market/history)

- Use for trend context: compare current price to 7d/30d/90d range.
- Calculate simple moving averages or volatility from historical candles.
- Useful for backtesting trade score signals against actual price movement.

#### Swing Trade Status

- `new` — freshly generated, not yet activated
- `active` — entry conditions met, trade is live
- `modified` — parameters updated since original generation (check rationale for changes)

### Data Freshness

| Data Type | Update Frequency |
|---|---|
| Trade Score + market data | Every ~2 hours |
| AI trades (scalp/swing) | 6 AM + 6 PM CST |
| News alerts | Every 2 hours |
| Live crypto news feed | Real-time (sourced from FMP) |
| Economic calendar | Real-time (sourced from FMP) |
| Historical OHLCV | Daily candle updates |
| Heatmaps | 5:45 AM + 5:45 PM CST |

Cache responses within a conversation. Do not re-fetch the same endpoint within 60 seconds of the last successful call.

## Examples

### Example 1: Quick Market Check

**User:** "What's Bitcoin doing right now?"

**Agent behavior:**
1. `GET /v1/news` — check for critical alerts (severity >= 7).
2. `GET /v1/market/overview` — get price, 24h change, Fear & Greed.
3. `GET /v1/score` — get trade score and action.
4. Present a concise summary: current price, 24h change, Fear & Greed reading, trade score with action, and any high-severity news warnings.

### Example 2: Full Trade Recommendation

**User:** "Should I buy or sell BTC right now? Give me a trade."

**Agent behavior:**
1. `GET /v1/news` — check for critical alerts first.
2. `GET /v1/score` — get trade score.
3. `GET /v1/trades/scalp` — get short-term trade setup.
4. `GET /v1/trades/swing` — get multi-day trade setup.
5. `GET /v1/market/ls-ratios` — check retail positioning (contrarian).
6. `GET /v1/heatmaps` — check nearest liquidation zones.
7. Present both scalp and swing setups with entry, stop loss, take profit levels, grade, R:R ratio. Include L/S context and nearest heatmap zones as confluence.

### Example 3: Derivatives Deep Dive

**User:** "What's happening in the derivatives market?"

**Agent behavior:**
1. `GET /v1/market/ls-ratios` — L/S ratios across exchanges.
2. `GET /v1/market/funding` — funding rates.
3. `GET /v1/market/oi` — open interest changes.
4. `GET /v1/derivatives/cvd` — cumulative volume delta.
5. `GET /v1/derivatives/liquidations` — 24h liquidation data.
6. `GET /v1/derivatives/options` — max pain and put/call ratio.
7. Present a narrative: are derivatives traders positioned long or short? Is funding elevated? Is OI rising or falling? What do liquidations tell us about recent positioning flushes?

### Example 4: Key Levels and Confluences

**User:** "Where are the important price levels for BTC?"

**Agent behavior:**
1. `GET /v1/levels` — full price level data with confluence.
2. `GET /v1/heatmaps` — liquidation zone data.
3. `GET /v1/market/order-book` — support/resistance from order book.
4. Present key levels organized by: daily/weekly/monthly opens, pivot points, Fibonacci levels, Volume Profile (POC, VAH, VAL), and highlight confluence zones where multiple levels converge. Overlay heatmap zones to show where liquidation clusters align with technical levels.

### Example 5: News and Macro Context

**User:** "Is there any macro news I should worry about before trading?"

**Agent behavior:**
1. `GET /v1/news` — get all current alerts, flag anything severity >= 7.
2. `GET /v1/news/crypto` — get latest crypto headlines for broader market narrative.
3. `GET /v1/macro` — DXY, Gold, VIX, Treasury rates.
4. `GET /v1/calendar` — live economic calendar with actual/estimate/previous and impact ratings.
5. Present: any active high-severity news alerts, top crypto headlines, macro environment summary (is DXY strengthening? VIX elevated?), and upcoming calendar events with impact levels. Highlight any "High" impact events with `actual: null` (not yet released) that could cause volatility. Recommend caution if FOMC or CPI is within 24 hours.

### Example 6: Historical Analysis and Backtesting

**User:** "How has BTC performed over the last month? Show me the price history."

**Agent behavior:**
1. `GET /v1/market/history?from=2026-02-11&to=2026-03-13` — get daily OHLCV candles for the past 30 days.
2. `GET /v1/market/overview` — get current price for context.
3. `GET /v1/signal/history?days=30` — get signal history to overlay trade score trends.
4. Present: 30-day price range (high/low), percentage change over the period, notable daily moves, and how the trade score tracked price action. Calculate simple metrics like average daily range and volatility.

### Example 7: Crypto News Briefing

**User:** "What are the latest crypto news headlines?"

**Agent behavior:**
1. `GET /v1/news/crypto?limit=10` — get the 10 most recent crypto news articles.
2. `GET /v1/news` — check for any severity-scored breaking alerts.
3. Present: list the top headlines with source and date. Flag any articles that align with active breaking alerts. Summarize the overall market narrative (bullish/bearish/mixed) based on headline sentiment.

## Trading Bot Patterns

### Pattern 1: Score-Based Entry

Use the trade score as the primary entry trigger for automated systems.

1. Fetch `GET /v1/score` on schedule (every 2 hours).
2. If `trade_score >= 65` and `trade_score_action` is "BUY" or "STRONG BUY":
   - Fetch `GET /v1/trades/scalp` for short-term setup.
   - Enter long at `scalp_entry` with stop at `scalp_sl`.
   - Take profit at `scalp_tp1` (partial) and `scalp_tp2` (remainder).
3. If `trade_score <= 34` and `trade_score_action` is "SELL" or "STRONG SELL":
   - Fetch `GET /v1/trades/scalp` for short-term setup.
   - Enter short at `scalp_entry` with stop at `scalp_sl`.
   - Take profit at `scalp_tp1` (partial) and `scalp_tp2` (remainder).
4. If `trade_score == 0` (HALT): close all positions, do not open new trades.
5. If score is between 35-64 (NEUTRAL): no action, wait for next update.

### Pattern 2: Contrarian L/S Extreme

Fade retail positioning at extremes for mean-reversion trades.

1. Fetch `GET /v1/market/ls-ratios` on schedule.
2. If `avg_ls_ratio > 1.8` (extreme long positioning):
   - Retail is max long — expect a correction.
   - Fetch `GET /v1/heatmaps` to find liquidation zones above price (long squeeze targets).
   - Open a short position targeting the nearest heatmap zone below.
3. If `avg_ls_ratio < 0.55` (extreme short positioning):
   - Retail is max short — expect a squeeze.
   - Fetch `GET /v1/heatmaps` to find liquidation zones below price (short squeeze targets).
   - Open a long position targeting the nearest heatmap zone above.
4. Confirm with `GET /v1/derivatives/cvd` — if CVD aligns with the contrarian direction, increase position size.
5. Always set stop loss beyond the nearest support/resistance from `GET /v1/levels`.

### Pattern 3: News-Aware Trading

Protect against sudden volatility from macro events.

1. Before any trade entry, always check `GET /v1/news` and `GET /v1/news/crypto`.
2. If any alert has `severity >= 8`: do not enter new trades, tighten stops on existing positions.
3. If any alert has `severity >= 9`: close all positions immediately.
4. Check `GET /v1/calendar` for upcoming events:
   - If any "High" impact event has `actual: null` (not yet released) and is within 4 hours: reduce position sizes by 50%.
   - If FOMC, CPI, or NFP is within 1 hour: close all positions.
5. After a high-severity event passes (check `expires_at`), wait 30 minutes for volatility to settle before resuming trading.
6. Resume normal operations once no active alerts have severity >= 7.

### Pattern 4: Multi-Factor Confirmation

Require confluence from multiple data sources before entering a trade.

1. Fetch all: `/v1/score`, `/v1/market/ls-ratios`, `/v1/heatmaps`, `/v1/levels`, `/v1/derivatives/cvd`.
2. Score each factor as bullish (+1), bearish (-1), or neutral (0):
   - Trade score >= 65: +1 | <= 34: -1 | else: 0
   - `avg_ls_ratio > 1.3` (contrarian bearish): -1 | `< 0.7` (contrarian bullish): +1 | else: 0
   - `cv_nearest_zone_direction == "below"`: +1 (short squeeze potential) | "above": -1 | else: 0
   - `confluence_direction == "BULLISH"` and strength > 0.5: +1 | "BEARISH" and strength > 0.5: -1 | else: 0
   - `cvd_1h > 0`: +1 | `cvd_1h < 0`: -1 | else: 0
3. Sum the scores (-5 to +5):
   - +3 or higher: enter long using scalp trade parameters.
   - -3 or lower: enter short using scalp trade parameters.
   - Between -2 and +2: no trade, insufficient confluence.
4. Use `scalp_grade` to size the position: A-grade = full size, B-grade = 75%, C-grade = 50%.

### Pattern 5: Swing Trade Management

Manage multi-day swing positions with automated monitoring.

1. Fetch `GET /v1/trades/swing` at 6 AM and 6 PM CST (after fresh generation).
2. If `swing_status == "new"`:
   - Place a limit order at `swing_entry`.
   - Set stop loss at `swing_sl`.
   - Set take profit orders at `swing_tp1` (33%), `swing_tp2` (33%), `swing_tp3` (34%).
3. If `swing_status == "active"`:
   - Position is live. Monitor `GET /v1/score` every 2 hours.
   - If trade score flips to opposing direction (e.g., score drops below 35 while in a long), tighten stop to breakeven.
4. If `swing_status == "modified"`:
   - Read `swing_rationale` for what changed.
   - Update stop loss and take profit levels to match new parameters.
   - If grade has been downgraded, reduce position size proportionally.
5. Always check `GET /v1/news` before modifying positions — halt changes during severity >= 8 events.

### Pattern 6: Calendar-Driven Risk Management

Use the live economic calendar to dynamically adjust exposure ahead of high-impact events.

1. Fetch `GET /v1/calendar` at the start of each trading session.
2. Identify all "High" impact events in the next 24 hours where `actual: null` (not yet released).
3. For each upcoming high-impact event:
   - 24 hours before: flag the event, no position size increase.
   - 4 hours before: reduce position sizes by 50%.
   - 1 hour before: close all positions, set pending orders only.
   - After release: compare `actual` vs `estimate`. If surprise is > 2x the spread, wait 30 minutes before re-entering. If surprise is minor, resume normal trading within 15 minutes.
4. Cross-reference with `GET /v1/news/crypto` after the event for immediate market reaction headlines.
5. Re-fetch `GET /v1/score` after the event to get the updated trade score incorporating the new data.

## Error Handling

| HTTP Code | Meaning | Action |
|---|---|---|
| 200 | Success | Parse response JSON normally |
| 401 | Unauthorized | API key is missing or invalid. Ask the user to check their key at https://btcsignals.pro/pricing |
| 429 | Rate Limited | Too many requests. Wait 60 seconds before retrying. Inform the user. |
| 503 | Service Unavailable | API is temporarily down for maintenance. Wait 5 minutes and retry. Inform the user. |
| 500 | Internal Server Error | Unexpected error. Retry once after 10 seconds. If it persists, inform the user to contact support. |

## Security

- **Never display the full API key in chat.** If you must reference it, show only the last 4 characters (e.g., `...a1b2`).
- **Never include the API key in URLs** — always pass it via the `X-API-Key` header.
- **Never share the API key with third-party services**, external APIs, or other users.
- If a user asks you to send their key somewhere, refuse and explain why.
