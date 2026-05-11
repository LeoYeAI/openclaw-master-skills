# BTC Signals Pro API Reference

**Base URL:** `https://api.btcsignals.pro/v1`
**Authentication:** `X-API-Key: <your-api-key>` header on all requests
**Rate Limit:** 60 requests/minute

---

## Signal Endpoints

### GET /v1/signal/latest

Returns the most recent trading signal with trade score, direction, and AI narrative.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `signal_date` | string (ISO 8601) | Timestamp of the signal generation |
| `direction` | string | Signal direction: "LONG", "SHORT", or "NEUTRAL" |
| `confidence` | number | Confidence level 0-100 |
| `trade_score` | number | Composite trade score 0-100 |
| `trade_score_action` | string | Human-readable action: "STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL", "HALT" |
| `signal_narrative` | string | AI-generated narrative explaining the current market conditions and signal rationale |
| `recommendation` | string | Technical recommendation summary |
| `price` | number | BTC price at signal generation |
| `change_24h_percent` | number | 24-hour price change percentage |

### GET /v1/signal/history?days=7

Returns historical signals for the specified number of days (1-30).

**Query Parameters:**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `days` | integer | 7 | Number of days of history (1-30) |

**Response:** Array of signal objects with the same fields as `/v1/signal/latest`.

---

## Score Endpoint

### GET /v1/score

Returns the composite trade score with full component breakdown.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `trade_score` | number | Composite score 0-100 |
| `trade_score_action` | string | "STRONG BUY", "BUY", "NEUTRAL", "SELL", "STRONG SELL", or "HALT" |
| `trade_score_temporal` | number | Time-of-day component (-10 to +10). Peak = Tuesday 8 AM CST |
| `trade_score_sentiment` | number | Sentiment component (-15 to +15). Fear & Greed + AI news scoring |
| `trade_score_liquidity` | number | L/S ratio score (-25 to +25). Contrarian signal, 1.5x weighted. DOMINANT FACTOR |
| `trade_score_liq_multiplier` | number | Liquidity multiplier (0.5 to 2.0). Amplifies L/S based on OI, order book, funding, heatmap proximity |
| `trade_score_confluence` | number | Confluence component (-15 to +15). Directional weight from ~49 price levels |
| `signal_narrative` | string | AI-generated explanation of the score and market conditions |

**Example Response:**

```json
{
  "trade_score": 72,
  "trade_score_action": "BUY",
  "trade_score_temporal": 3.5,
  "trade_score_sentiment": 8.2,
  "trade_score_liquidity": -12.4,
  "trade_score_liq_multiplier": 1.35,
  "trade_score_confluence": 9.7,
  "signal_narrative": "Bullish setup forming. Retail is moderately short (contrarian bullish), confluence of key levels below price providing support, and sentiment has shifted positive on ETF inflow news. Temporal component slightly positive as we approach peak volatility window."
}
```

---

## Trade Endpoints

### GET /v1/trades/scalp

Returns the current AI-generated scalp trade setup (4-12 hour timeframe).

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `scalp_direction` | string | "LONG" or "SHORT" |
| `scalp_grade` | string | Trade quality grade: "A", "B", or "C" |
| `scalp_entry` | number | Recommended entry price |
| `scalp_sl` | number | Stop loss price |
| `scalp_tp1` | number | Take profit target 1 (conservative) |
| `scalp_tp2` | number | Take profit target 2 (extended) |
| `scalp_rr` | number | Risk-to-reward ratio |
| `scalp_timeframe` | string | Expected trade duration (e.g., "4-8 hours") |
| `scalp_rationale` | string | AI-generated explanation of the trade setup |

**Example Response:**

```json
{
  "scalp_direction": "LONG",
  "scalp_grade": "A",
  "scalp_entry": 83250.00,
  "scalp_sl": 82800.00,
  "scalp_tp1": 83950.00,
  "scalp_tp2": 84600.00,
  "scalp_rr": 2.33,
  "scalp_timeframe": "4-8 hours",
  "scalp_rationale": "Price sitting on VP POC at 83,200 with heatmap cluster below at 82,500 acting as floor. Retail heavily short (avg L/S 0.68), CVD turning positive on 15m. Entry above POC with stop below heatmap zone for clean invalidation."
}
```

### GET /v1/trades/swing

Returns the current AI-generated swing trade setup (multi-day timeframe).

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `swing_direction` | string | "LONG" or "SHORT" |
| `swing_grade` | string | Trade quality grade: "A", "B", or "C" |
| `swing_entry` | number | Recommended entry price |
| `swing_sl` | number | Stop loss price |
| `swing_tp1` | number | Take profit target 1 |
| `swing_tp2` | number | Take profit target 2 |
| `swing_tp3` | number | Take profit target 3 (extended) |
| `swing_rr` | number | Risk-to-reward ratio |
| `swing_timeframe` | string | Expected trade duration (e.g., "3-7 days") |
| `swing_rationale` | string | AI-generated explanation of the swing setup |
| `swing_status` | string | "new" (freshly generated), "active" (entry hit), or "modified" (parameters updated) |

---

## Market Endpoints

### GET /v1/market/overview

Returns current BTC market snapshot.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `price` | number | Current BTC price in USD |
| `change_24h_percent` | number | 24-hour price change percentage |
| `fear_greed_index` | number | Fear & Greed Index (0 = Extreme Fear, 100 = Extreme Greed) |

### GET /v1/market/ls-ratios

Returns Long/Short ratios across three exchanges plus the aggregate average.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `exchange_ls_summary` | object | Per-exchange breakdown (see below) |
| `avg_ls_ratio` | number | Average L/S ratio across all exchanges |
| `ls_consensus` | string | "LONG", "SHORT", or "NEUTRAL" — majority retail direction |
| `long_short_ratio` | number | Aggregate long/short ratio |

**`exchange_ls_summary` structure:**

| Field | Type | Description |
|---|---|---|
| `binance` | object | `{ "long_ratio": number, "short_ratio": number, "ls_ratio": number }` |
| `bybit` | object | `{ "long_ratio": number, "short_ratio": number, "ls_ratio": number }` |
| `bitget` | object | `{ "long_ratio": number, "short_ratio": number, "ls_ratio": number }` |

**Example Response:**

```json
{
  "exchange_ls_summary": {
    "binance": { "long_ratio": 0.58, "short_ratio": 0.42, "ls_ratio": 1.38 },
    "bybit": { "long_ratio": 0.61, "short_ratio": 0.39, "ls_ratio": 1.56 },
    "bitget": { "long_ratio": 0.55, "short_ratio": 0.45, "ls_ratio": 1.22 }
  },
  "avg_ls_ratio": 1.39,
  "ls_consensus": "LONG",
  "long_short_ratio": 1.39
}
```

### GET /v1/market/order-book

Returns order book depth and imbalance data.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `ob_imbalance` | number | Order book imbalance ratio. Positive = more bids, negative = more asks |
| `strongest_support` | number | Strongest support price from order book depth |
| `strongest_resistance` | number | Strongest resistance price from order book depth |
| `total_bid_depth` | number | Total bid depth in USD |
| `total_ask_depth` | number | Total ask depth in USD |

### GET /v1/market/funding

Returns funding rates across exchanges.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `funding_rates` | object | Per-exchange funding rate data |

### GET /v1/market/oi

Returns open interest data and changes.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `open_interest` | number | Total open interest in USD |
| `oi_change_24h` | number | 24-hour OI change percentage |

### GET /v1/market/history

Returns historical daily OHLCV (Open, High, Low, Close, Volume) data for BTC with date range filtering. Powered by FMP financial data.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `from` | string | No | 30 days ago | Start date in YYYY-MM-DD format |
| `to` | string | No | today | End date in YYYY-MM-DD format |

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `symbol` | string | Trading pair symbol (e.g., "BTCUSD") |
| `candles` | array | Array of daily OHLCV candle objects |
| `count` | integer | Number of candles returned |

**Candle Object Fields:**

| Field | Type | Description |
|---|---|---|
| `date` | string | Candle date (YYYY-MM-DD) |
| `open` | number | Opening price |
| `high` | number | Highest price of the day |
| `low` | number | Lowest price of the day |
| `close` | number | Closing price |
| `volume` | number | Trading volume in USD |
| `change_percent` | number | Daily percentage change |

**Example Request:**

```bash
curl -s "https://api.btcsignals.pro/v1/market/history?from=2026-02-11&to=2026-03-13" \
  -H "X-API-Key: <your-api-key>"
```

**Example Response:**

```json
{
  "symbol": "BTCUSD",
  "candles": [
    {
      "date": "2026-03-13",
      "open": 83500.00,
      "high": 84200.00,
      "low": 82900.00,
      "close": 83750.00,
      "volume": 28500000000,
      "change_percent": 0.30
    },
    {
      "date": "2026-03-12",
      "open": 83200.00,
      "high": 83800.00,
      "low": 82500.00,
      "close": 83500.00,
      "volume": 26200000000,
      "change_percent": 0.36
    }
  ],
  "count": 30
}
```

---

## Derivatives Endpoints

### GET /v1/derivatives/options

Returns options market data including max pain.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `max_pain_price` | number | Options max pain price — the price at which most options expire worthless |
| `max_pain_hours_to_expiry` | number | Hours until the nearest major options expiry |
| `put_call_ratio` | number | Put/call ratio. > 1 = more puts (bearish hedging), < 1 = more calls (bullish speculation) |

### GET /v1/derivatives/liquidations

Returns 24-hour liquidation data.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `liq_long_24h` | number | Total long liquidations in USD over the past 24 hours |
| `liq_short_24h` | number | Total short liquidations in USD over the past 24 hours |
| `liq_net_24h` | number | Net liquidation pressure (positive = more longs liquidated, negative = more shorts) |

### GET /v1/derivatives/cvd

Returns Cumulative Volume Delta data.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `cvd_1h` | number | CVD over the past 1 hour. Positive = net buying, negative = net selling |
| `cvd_15m` | number | CVD over the past 15 minutes |
| `cvd_1h_trend` | string | CVD trend direction: "RISING", "FALLING", or "FLAT" |
| `cvd_net_buy_pressure` | number | Net buy pressure indicator |

### GET /v1/derivatives/etf

Returns Bitcoin ETF flow data.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `etf_net_flow` | number | Net ETF inflow/outflow in USD. Positive = inflow (bullish), negative = outflow |
| `etf_flow_date` | string | Date of the flow data |

---

## Technicals Endpoint

### GET /v1/technicals

Returns technical indicator values and summary.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `rsi` | number | Relative Strength Index (14-period). Overbought > 70, oversold < 30 |
| `technical_summary` | string | Overall technical assessment summary |
| `fractal_summary` | string | DTW fractal pattern analysis summary |
| `fractal_prob_bullish` | number | Probability of bullish fractal match (0.0-1.0) |
| `fractal_prob_bearish` | number | Probability of bearish fractal match (0.0-1.0) |
| `sfp_detected` | boolean | Whether a Swing Failure Pattern has been detected |
| `recommendation` | string | Technical recommendation: "BUY", "SELL", "NEUTRAL" |

### GET /v1/fractals

Returns DTW fractal pattern match probabilities.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `fractal_summary` | string | Detailed fractal analysis narrative |
| `fractal_prob_bullish` | number | Bullish pattern match probability (0.0-1.0) |
| `fractal_prob_bearish` | number | Bearish pattern match probability (0.0-1.0) |

---

## Levels Endpoint

### GET /v1/levels

Returns all key price levels, market structure, and the unified confluence engine output.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `monthly_open` | number | Current month's opening price |
| `weekly_open` | number | Current week's opening price |
| `daily_open` | number | Current day's opening price |
| `daily_pivot_pp` | number | Daily pivot point |
| `daily_pivot_s1` | number | Daily pivot support 1 |
| `daily_pivot_s2` | number | Daily pivot support 2 |
| `daily_pivot_r1` | number | Daily pivot resistance 1 |
| `daily_pivot_r2` | number | Daily pivot resistance 2 |
| `market_structure` | string | Current market structure: "BULLISH", "BEARISH", or "RANGING" |
| `structural_bias` | string | Higher-timeframe structural bias |
| `fib_high` | number | Fibonacci range high |
| `fib_low` | number | Fibonacci range low |
| `fib_382` | number | 0.382 Fibonacci retracement level |
| `fib_618` | number | 0.618 Fibonacci retracement level |
| `vp_poc` | number | Volume Profile Point of Control — highest volume price |
| `vp_vah` | number | Volume Profile Value Area High |
| `vp_val` | number | Volume Profile Value Area Low |
| `price_level_confluence` | string | Summary of confluence analysis across all level types |
| `nearby_levels_count` | integer | Number of key levels within close proximity to current price |
| `price_levels_json` | string (JSON) | Full array of all ~49 weighted price levels with type, price, weight, and distance |
| `confluence_above` | number | Number of confluence levels above current price |
| `confluence_below` | number | Number of confluence levels below current price |
| `confluence_direction` | string | Net confluence direction: "BULLISH" or "BEARISH" |
| `confluence_direction_strength` | number | Strength of confluence direction (0.0-1.0) |
| `confluence_magnet_price` | number | Nearest high-weight cluster price — acts as a price magnet |
| `confluence_magnet_side` | string | Whether the magnet is "above" or "below" current price |

**Example Response:**

```json
{
  "monthly_open": 82150.00,
  "weekly_open": 83400.00,
  "daily_open": 83680.00,
  "daily_pivot_pp": 83550.00,
  "daily_pivot_s1": 83100.00,
  "daily_pivot_s2": 82650.00,
  "daily_pivot_r1": 84000.00,
  "daily_pivot_r2": 84450.00,
  "market_structure": "BULLISH",
  "structural_bias": "BULLISH",
  "fib_high": 84800.00,
  "fib_low": 81200.00,
  "fib_382": 82575.00,
  "fib_618": 83425.00,
  "vp_poc": 83200.00,
  "vp_vah": 84100.00,
  "vp_val": 82400.00,
  "price_level_confluence": "Strong support cluster at 83,100-83,250 with 4 converging levels. Resistance thins above 84,000.",
  "nearby_levels_count": 7,
  "price_levels_json": "[{\"type\":\"pivot_pp\",\"price\":83550,\"weight\":3},{\"type\":\"vp_poc\",\"price\":83200,\"weight\":5}]",
  "confluence_above": 12,
  "confluence_below": 18,
  "confluence_direction": "BULLISH",
  "confluence_direction_strength": 0.62,
  "confluence_magnet_price": 83200.00,
  "confluence_magnet_side": "below"
}
```

---

## Heatmaps Endpoint

### GET /v1/heatmaps

Returns liquidation heatmap zones across three timeframes: 24h, 7d, and 30d.

**24-Hour Heatmap Fields:**

| Field | Type | Description |
|---|---|---|
| `cv_liquidity_zones` | string (JSON) | Array of liquidation zone objects for the 24h timeframe |
| `cv_zones_count` | integer | Number of liquidation zones identified (24h) |
| `cv_nearest_zone` | number | Price of the nearest liquidation zone (24h) |
| `cv_nearest_zone_direction` | string | "above" or "below" current price (24h) |
| `cv_nearest_zone_distance_pct` | number | Distance to nearest zone as a percentage of current price (24h) |
| `cv_data_stale` | boolean | Whether the 24h heatmap data is stale (older than expected) |

**7-Day Heatmap Fields:**

| Field | Type | Description |
|---|---|---|
| `cv_zones_7d` | string (JSON) | Array of liquidation zone objects for the 7d timeframe |
| `cv_zones_count_7d` | integer | Number of liquidation zones identified (7d) |
| `cv_nearest_zone_7d` | number | Price of the nearest liquidation zone (7d) |
| `cv_nearest_zone_direction_7d` | string | "above" or "below" current price (7d) |
| `cv_nearest_zone_distance_pct_7d` | number | Distance to nearest zone as a percentage (7d) |

**30-Day Heatmap Fields:**

| Field | Type | Description |
|---|---|---|
| `cv_zones_30d` | string (JSON) | Array of liquidation zone objects for the 30d timeframe |
| `cv_zones_count_30d` | integer | Number of liquidation zones identified (30d) |
| `cv_nearest_zone_30d` | number | Price of the nearest liquidation zone (30d) |
| `cv_nearest_zone_direction_30d` | string | "above" or "below" current price (30d) |
| `cv_nearest_zone_distance_pct_30d` | number | Distance to nearest zone as a percentage (30d) |

**Example Response:**

```json
{
  "cv_liquidity_zones": "[{\"price\":82500,\"intensity\":0.85,\"type\":\"short\"},{\"price\":84800,\"intensity\":0.72,\"type\":\"long\"}]",
  "cv_zones_count": 5,
  "cv_nearest_zone": 82500,
  "cv_nearest_zone_direction": "below",
  "cv_nearest_zone_distance_pct": 1.2,
  "cv_data_stale": false,
  "cv_zones_7d": "[{\"price\":81000,\"intensity\":0.91,\"type\":\"short\"},{\"price\":86200,\"intensity\":0.78,\"type\":\"long\"}]",
  "cv_zones_count_7d": 8,
  "cv_nearest_zone_7d": 81000,
  "cv_nearest_zone_direction_7d": "below",
  "cv_nearest_zone_distance_pct_7d": 2.8,
  "cv_zones_30d": "[{\"price\":78500,\"intensity\":0.95,\"type\":\"short\"},{\"price\":89000,\"intensity\":0.88,\"type\":\"long\"}]",
  "cv_zones_count_30d": 12,
  "cv_nearest_zone_30d": 78500,
  "cv_nearest_zone_direction_30d": "below",
  "cv_nearest_zone_distance_pct_30d": 5.6
}
```

---

## News Endpoints

### GET /v1/news

Returns current breaking news alerts scored by severity.

**Response:** Array of news alert objects.

**Alert Fields:**

| Field | Type | Description |
|---|---|---|
| `id` | string | Unique alert identifier |
| `severity` | integer | Alert severity 1-10. >= 7 = significant, >= 9 = critical |
| `headline` | string | Short headline of the news event |
| `summary` | string | Detailed summary of the event and market implications |
| `alert_type` | string | Type of alert (e.g., "regulatory", "hack", "etf", "macro", "exchange") |
| `source_url` | string | URL to the original news source |
| `created_at` | string (ISO 8601) | When the alert was created |
| `expires_at` | string (ISO 8601) | When the alert expires and is no longer considered active |

### GET /v1/news/crypto

Returns a live crypto news feed with the latest headlines from major crypto news sources. Powered by FMP financial data. Supports optional symbol filtering to focus on specific cryptocurrencies.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `symbol` | string | No | all | Filter by crypto symbol (e.g., "BTCUSD", "ETHUSD", "SOLUSD") |
| `limit` | integer | No | 20 | Number of articles to return (1-50) |

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `articles` | array | Array of news article objects |
| `count` | integer | Number of articles returned |
| `symbol_filter` | string/null | The symbol filter applied, or null if showing all crypto news |

**Article Object Fields:**

| Field | Type | Description |
|---|---|---|
| `title` | string | Article headline |
| `published_date` | string | Publication date (YYYY-MM-DD HH:MM:SS) |
| `source` | string | News source domain (e.g., "coindesk.com", "cointelegraph.com") |
| `url` | string | Link to the full article |
| `symbol` | string | Related crypto symbol (e.g., "BTCUSD") |
| `snippet` | string | Article summary/snippet |

**Example Request:**

```bash
# Get latest 20 crypto news articles
curl -s "https://api.btcsignals.pro/v1/news/crypto?limit=20" \
  -H "X-API-Key: <your-api-key>"

# Get Bitcoin-specific news only
curl -s "https://api.btcsignals.pro/v1/news/crypto?symbol=BTCUSD&limit=10" \
  -H "X-API-Key: <your-api-key>"
```

**Example Response:**

```json
{
  "articles": [
    {
      "title": "Bitcoin Rebounds After Hitting 5-Week Low at $82K",
      "published_date": "2026-03-13 07:46:28",
      "source": "coindesk.com",
      "url": "https://coindesk.com/...",
      "symbol": "BTCUSD",
      "snippet": "Bitcoin has recovered above $83,000 after a brief dip to..."
    },
    {
      "title": "Ethereum ETF Approval Odds Rise to 75%",
      "published_date": "2026-03-13 06:30:00",
      "source": "cointelegraph.com",
      "url": "https://cointelegraph.com/...",
      "symbol": "ETHUSD",
      "snippet": "Bloomberg analysts have raised the probability of..."
    }
  ],
  "count": 20,
  "symbol_filter": null
}
```

**Supported Symbols:**

| Symbol | Cryptocurrency |
|---|---|
| `BTCUSD` | Bitcoin |
| `ETHUSD` | Ethereum |
| `SOLUSD` | Solana |
| `XRPUSD` | Ripple |
| `DOGEUSD` | Dogecoin |

---

## Macro Endpoints

### GET /v1/macro

Returns macro market indicators relevant to Bitcoin.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `dxy` | number | US Dollar Index value |
| `gold` | number | Gold price in USD |
| `vix` | number | CBOE Volatility Index |
| `treasury_10y` | number | 10-year US Treasury yield |

### GET /v1/calendar

Returns a live economic calendar with upcoming macroeconomic events. Powered by FMP financial data. Includes actual/estimate/previous values for released events and impact ratings for risk assessment.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|---|---|---|---|---|
| `from` | string | No | today | Start date in YYYY-MM-DD format |
| `to` | string | No | 7 days ahead | End date in YYYY-MM-DD format |

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `events` | array | Array of economic event objects |
| `count` | integer | Number of events in the date range |
| `high_impact_count` | integer | Number of "High" impact events in the range |

**Event Object Fields:**

| Field | Type | Description |
|---|---|---|
| `date` | string | Event date (YYYY-MM-DD) |
| `event` | string | Event name (e.g., "Fed Interest Rate Decision", "CPI Release") |
| `country` | string | Country code (e.g., "US") |
| `actual` | string/null | Actual released value. `null` if the event hasn't occurred yet |
| `previous` | string | Previous period's value |
| `estimate` | string | Market consensus estimate |
| `impact` | string | Impact level: "High", "Medium", or "Low" |

**Example Request:**

```bash
# Get economic calendar for the next 7 days
curl -s "https://api.btcsignals.pro/v1/calendar?from=2026-03-13&to=2026-03-20" \
  -H "X-API-Key: <your-api-key>"
```

**Example Response:**

```json
{
  "events": [
    {
      "date": "2026-03-18",
      "event": "Fed Interest Rate Decision",
      "country": "US",
      "actual": null,
      "previous": "4.50%",
      "estimate": "4.50%",
      "impact": "High"
    },
    {
      "date": "2026-03-14",
      "event": "University of Michigan Consumer Sentiment",
      "country": "US",
      "actual": "67.8",
      "previous": "64.7",
      "estimate": "65.0",
      "impact": "Medium"
    }
  ],
  "count": 12,
  "high_impact_count": 3
}
```

**High-Impact Events to Watch:**

| Event | Why It Matters for BTC |
|---|---|
| Fed Interest Rate Decision | Rate changes directly impact risk assets. Hawkish = bearish for BTC |
| CPI (Consumer Price Index) | Inflation data drives Fed policy expectations. Hot CPI = selloff risk |
| Non-Farm Payrolls (NFP) | Strong jobs = hawkish Fed. Weak jobs = dovish Fed (bullish BTC) |
| GDP Growth Rate | Measures economic health. Recession fears can drive BTC both ways |
| PCE Price Index | The Fed's preferred inflation gauge. Surprise readings move markets |
| Unemployment Rate | Rising unemployment = dovish Fed expectations = bullish BTC |

---

## Account Endpoint

### GET /v1/account

Returns subscription status and API usage information.

**Response Fields:**

| Field | Type | Description |
|---|---|---|
| `subscription_status` | string | "active", "trial", "expired", or "cancelled" |
| `plan` | string | Current plan name |
| `requests_today` | integer | Number of API requests made today |
| `requests_limit` | integer | Daily request limit |
| `rate_limit_per_minute` | integer | Per-minute rate limit |
| `subscription_expires` | string (ISO 8601) | Subscription expiration date |

---

## Common Response Patterns

### Success Response

All successful responses return HTTP 200 with a JSON body containing the relevant fields documented above.

### Error Responses

```json
{
  "error": "Unauthorized",
  "message": "Invalid or missing API key"
}
```

```json
{
  "error": "Rate Limited",
  "message": "Rate limit exceeded. Please wait 60 seconds.",
  "retry_after": 60
}
```

```json
{
  "error": "Service Unavailable",
  "message": "API is undergoing maintenance. Please try again later."
}
```

---

## Field Naming Convention

All response fields use **snake_case** naming and map directly to the internal database column names. This ensures consistency between the API responses and the underlying data model. When building integrations, use the field names exactly as documented above.
