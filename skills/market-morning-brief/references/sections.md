# Market Morning Brief — Section Documentation

This document details each section of the morning and evening brief, including data sources, output formats, and error handling.

## Morning Brief Sections

### 1. Header

**Output:**
```
MARKET MORNING BRIEF — [Day], [Month] [Date], [Year]
```

**Example:**
```
MARKET MORNING BRIEF — Thursday, March 7, 2026
```

**Notes:**
- Always first
- Always succeeds (no external data needed)

---

## 2. Portfolio Summary

**Section Header:** `PORTFOLIO ([count] positions, [+/-]$[amount] unrealized)`

**Data Source:** Kalshi API (read-only) — direct HTTP calls, no caching

**Configuration:**
```yaml
kalshi:
  enabled: true
  api_key_id: "your-key-id"
  private_key_file: "/path/to/private.key"
```

### Fetching Portfolio

**Kalshi API call:**
```
GET /portfolio
Authorization: Bearer <JWT from private key>
```

**Response fields used:**
- `ticker` — market identifier (e.g., "POTUS-2028-DEM")
- `side` — "YES" or "NO"
- `quantity` — contracts held
- `average_price_cents` — what you paid
- `days_until_expiration` — TTL to market close
- Current market price — for unrealized P&L calculation

### Output Format

Each position on one line, tab-separated:

```
TICKER            SIDE  QTY@PRICE  COST      UNREALIZED      (expires: days)
```

**Example:**
```
POTUS-2028-DEM    YES   100@48¢    $48 cost  +$18 unrl (exp: 242 days)
UKRAINE-2026-NO   YES   50@28¢     $14 cost  +$8 unrl (exp: 118 days)
FED-MAR-CUT       NO    200@35¢    $70 cost  -$2 unrl (exp: 8 days)
```

### Calculation

**Unrealized P&L:**
```
unrealized = (current_price - average_price) * quantity

where:
  current_price = mid of current bid/ask, or last_price
  average_price = total_cost / quantity
  quantity = contracts held
```

**Summary line:**
```
PORTFOLIO ([count] positions, [+/-]$[total_unrealized])
```

### Error Handling

**If Kalshi API unavailable:**
```
PORTFOLIO: unavailable (check Kalshi API)
```

**If parsing fails:**
```
PORTFOLIO: error (failed to fetch positions)
```

**Fail-safe:** Missing one position doesn't skip portfolio. Prints all parseable positions, logs error for failed ones.

---

## 3. Kalshalyst Edges (Optional)

**Section Header:** `EDGES (Kalshalyst, top [count])`

**Data Source:** Cache file (`.kalshi_research_cache.json`)

**Cache path (configurable):**
```yaml
cache_paths:
  kalshalyst: "./state/.kalshi_research_cache.json"
```

### Cache File Format

Written by Kalshalyst skill every edge scan run (default: hourly).

```json
{
  "insights": [
    {
      "ticker": "POTUS-2028-DEM",
      "title": "Will a Democrat win the 2028 presidential election?",
      "side": "NO",
      "yes_bid": 45,
      "yes_ask": 51,
      "volume": 2500,
      "open_interest": 8000,
      "days_to_close": 672,
      "edge_type": "claude_contrarian",
      "market_prob": 0.48,
      "estimated_prob": 0.38,
      "edge_pct": 14.0,
      "effective_edge_pct": 14.0,
      "direction": "overpriced",
      "reasoning": "Market overweighting base rate without pricing recent policy momentum...",
      "confidence": 0.72,
      "estimator": "claude"
    }
  ],
  "cached_at": "2026-03-08T15:32:18+00:00"
}
```

### Output Format

Top 3 opportunities only:

```
EDGES (Kalshalyst, top 3):
1. TICKER    SIDE @ PRICE  (+[edge]% edge, [conf]% conf)
2. TICKER    SIDE @ PRICE  (+[edge]% edge, [conf]% conf)
3. TICKER    SIDE @ PRICE  (+[edge]% edge, [conf]% conf)
```

**Example:**
```
EDGES (Kalshalyst, top 3):
1. POTUS-2028-DEM    NO @ 38%  (+14% edge, 72% conf)
2. INFLATION-2026    YES @ 68%  (+8% edge, 65% conf)
3. UKRAINE-PEACE     YES @ 55%  (+6% edge, 58% conf)
```

### Parsing Logic

1. Load cache file
2. Sort by `edge_pct` (descending)
3. Take top 3
4. For each: extract ticker, side (YES/NO from `estimated_prob` vs market), market_prob, edge_pct, confidence
5. Format one per line

### Error Handling

**If cache file missing:**
```
EDGES: unavailable (install Kalshalyst skill for contrarian analysis)
```

**If cache file unparseable:**
```
EDGES: unavailable (cache corrupted)
```

**If cache file stale (>2 hours old):**
```
EDGES: unavailable (Kalshalyst data stale — check skill)
```

---

## 4. Cross-Platform Divergences (Optional)

**Section Header:** `DIVERGENCES (Arbiter, Kalshi ↔ Polymarket)`

**Data Source:** Cache file (`.crossplatform_divergences.json`)

**Cache path (configurable):**
```yaml
cache_paths:
  arbiter: "./state/.crossplatform_divergences.json"
```

### Cache File Format

Written by Prediction Market Arbiter skill periodically (default: every 4 hours).

```json
{
  "divergences": [
    {
      "ticker": "UKRAINE-2026-NO",
      "title": "Will the war in Ukraine be ongoing in 2026?",
      "kalshi_price": 0.28,
      "kalshi_bid": 27,
      "kalshi_ask": 29,
      "polymarket_price": 0.31,
      "polymarket_bid": 30,
      "polymarket_ask": 32,
      "spread_cents": 3,
      "spread_pct": 10.7,
      "kalshi_volume": 1200,
      "polymarket_volume": 850,
      "volume_difference_pct": 12,
      "opportunity": "Arbitrage: Buy Kalshi @ 28¢, Sell PM @ 31¢"
    }
  ],
  "cached_at": "2026-03-08T15:00:00+00:00"
}
```

### Output Format

Top 2-3 divergences:

```
DIVERGENCES (Arbiter):
TICKER            Kalshi [%] ↔ PM [%]  ($[spread] spread)
TICKER            Kalshi [%] ↔ PM [%]  ($[spread] spread)
```

**Example:**
```
DIVERGENCES (Arbiter):
UKRAINE-2026-NO    Kalshi 28% ↔ PM 31%  ($0.03 spread)
POTUS-2028-DEM     Kalshi 38% ↔ PM 40%  ($0.02 spread)
```

### Parsing Logic

1. Load cache file
2. Sort by `spread_cents` (descending) — biggest spreads first
3. Take top 2
4. For each: extract ticker, kalshi_price, polymarket_price, spread_cents
5. Format one per line

### Error Handling

**If cache file missing:**
```
DIVERGENCES: unavailable (install Prediction Market Arbiter for cross-platform analysis)
```

**If cache file empty:**
```
DIVERGENCES: none found today
```

**If cache file stale (>6 hours old):**
```
DIVERGENCES: unavailable (Arbiter data stale)
```

---

## 5. X Signal Summaries (Optional)

**Section Header:** `X SIGNALS (last 24h)`

**Data Source:** Cache file (`.x_signal_cache.json`)

**Cache path (configurable):**
```yaml
cache_paths:
  xpulse: "./state/.x_signal_cache.json"
```

### Cache File Format

Written by Xpulse skill periodically (default: every 2 hours).

```json
{
  "signals": [
    {
      "signal": "Fed rate cut odds +5%",
      "category": "macroeconomics",
      "confidence": 0.78,
      "reach": 8200,
      "source_count": 3,
      "timestamp": "2026-03-07T15:30:00Z",
      "topics": ["fed", "interest-rates", "inflation"]
    },
    {
      "signal": "Ukraine ceasefire talks escalating",
      "category": "geopolitics",
      "confidence": 0.72,
      "reach": 5100,
      "source_count": 2,
      "timestamp": "2026-03-07T14:15:00Z",
      "topics": ["ukraine", "peace", "geopolitics"]
    }
  ],
  "cached_at": "2026-03-08T16:00:00+00:00"
}
```

### Output Format

Top 2-3 signals from last 24h:

```
X SIGNALS (last 24h):
[signal]  ([confidence]% conf, [reach]K reach)
[signal]  ([confidence]% conf, [reach]K reach)
```

**Example:**
```
X SIGNALS (last 24h):
Fed rate cut odds +5%   (78% conf, 8.2K reach)
Ukraine ceasefire +3%   (72% conf, 5.1K reach)
```

### Parsing Logic

1. Load cache file
2. Filter signals with `timestamp` within last 24 hours
3. Sort by `confidence` (descending)
4. Take top 2
5. For each: extract signal, confidence, reach (formatted as K for thousands)
6. Format one per line

### Error Handling

**If cache file missing:**
```
X SIGNALS: unavailable (install Xpulse for social sentiment analysis)
```

**If cache file empty or no recent signals:**
```
X SIGNALS: none found (check Xpulse directly)
```

**If cache file stale (>4 hours old):**
```
X SIGNALS: unavailable (Xpulse data stale)
```

---

## 6. Crypto Prices (Optional)

**Section Header:** `CRYPTO`

**Data Source:** Coinbase API (live) or fallback cache

**Configuration:**
```yaml
coinbase:
  enabled: true
  api_key: "sk-..."
  tickers: ["BTC", "ETH", "SOL"]
```

### Coinbase API Call

```
GET /api/v3/brokerage/market/products/{product_id}
Authorization: Bearer <OAuth token or API key>
```

Product IDs: BTC-USD, ETH-USD, SOL-USD, etc.

### Output Format

Two tickers per line, separated by `|`:

```
CRYPTO:
BTC  $[price]  ([+/-]X.X%)  | ETH  $[price]  ([+/-]X.X%)
SOL  $[price]  ([+/-]X.X%)  | AVAX $[price]  ([+/-]X.X%)
```

**Example:**
```
CRYPTO:
BTC  $62,400  (+1.2%)   | ETH  $3,140  (-0.8%)
SOL  $142     (-2.1%)   | AVAX $38     (+0.5%)
```

### Price Calculation

**24h change:**
```
pct_change = (current_price - 24h_price) / 24h_price * 100
```

### Error Handling

**If Coinbase not configured:**
```
CRYPTO: unavailable (configure Coinbase API for crypto prices)
```

**If Coinbase API unavailable:**
```
CRYPTO: unavailable (Coinbase API error)
```

**If single ticker fails:** Skip that ticker, continue with others.

---

## 7. Polymarket Activity

**Section Header:** `POLYMARKET (top [count] by volume)`

**Data Source:** Polymarket public API (free, no auth)

**API Endpoint:**
```
https://clob.polymarket.com/markets?limit=100&order_by=volume
```

### API Response Fields Used

```json
{
  "data": [
    {
      "id": "0x123...",
      "question": "Will X happen?",
      "tokens": [
        {
          "outcome": "Yes",
          "price": 0.48
        },
        {
          "outcome": "No",
          "price": 0.52
        }
      ],
      "volume": 2400000,
      "liquidity": 50000
    }
  ]
}
```

### Output Format

Top 3 markets by 24h volume:

```
POLYMARKET (top 3 by volume):
[Question]: $[volume]M vol, [implied_prob]% [side]
[Question]: $[volume]M vol, [implied_prob]% [side]
[Question]: $[volume]M vol, [implied_prob]% [side]
```

**Example:**
```
POLYMARKET (top 3 by volume):
POTUS 2028: $2.4M vol, 48% DEM (vs 52% GOP)
Inflation >4% 2026: $1.1M vol, 32% prob
Bitcoin >$100K 2026: $0.8M vol, 58% prob
```

### Parsing Logic

1. Fetch from Polymarket API
2. Sort by `volume` (descending)
3. Take top 3
4. For each:
   - Extract question (truncate to 40 chars if needed)
   - Format volume in millions
   - Use token with highest price as "implied_prob"
   - Format one per line

### Error Handling

**If Polymarket API unavailable:**
```
POLYMARKET: unavailable (check Polymarket directly)
```

**If request times out:**
```
POLYMARKET: timeout (try again later)
```

---

## Evening Brief Sections

### 1. Header

```
EVENING BRIEFING — [Day], [Month] [Date], [Year]
```

### 2. Day's Activity

**Data Source:** Kalshi API (read-only)

**Fields:**
- Realized P&L from closed positions
- Positions opened today
- Positions closed today
- Net cash available

**Output:**
```
DAY'S ACTIVITY:
Closed: [TICKER] [+/-]$[amount] ([realized])
Opened: [TICKER] [qty]@[price]
Net realized today: [+/-]$[amount] | Current positions: [count]
```

### 3. Overnight Watch

**Data Source:** Kalshi portfolio + market data

**Identifies:**
- Positions expiring within 7 days
- Wide bid-ask spreads (potential liquidity warning)
- Low volume markets
- Geopolitical risks (from Xpulse/news if available)

**Output:**
```
OVERNIGHT WATCH:
[TICKER] expires in [N] days — [watch reason]
[TICKER] low liquidity ([M] contracts asking) — [watch reason]
```

### 4. Top X Signals (Today Only)

**Data Source:** Xpulse cache, filtered to last 24h

**Output:**
```
TOP X SIGNALS TODAY:
• [signal] ([confidence]% conf)
• [signal] ([confidence]% conf)
```

---

## Cache File Locations

All cache files are JSON and located in the `state/` directory relative to the skill:

| Skill | Filename | Path |
|-------|----------|------|
| Kalshalyst | `.kalshi_research_cache.json` | `state/.kalshi_research_cache.json` |
| Arbiter | `.crossplatform_divergences.json` | `state/.crossplatform_divergences.json` |
| Xpulse | `.x_signal_cache.json` | `state/.x_signal_cache.json` |

**Configuration:**
```yaml
cache_paths:
  kalshalyst: "./state/.kalshi_research_cache.json"
  arbiter: "./state/.crossplatform_divergences.json"
  xpulse: "./state/.x_signal_cache.json"
```

All paths are relative to skill working directory.

---

## Graceful Degradation Logic

Every section:

1. **Try to load data** (cache file or API call)
2. **On success:** Format and output
3. **On failure:**
   - If cache-based: "unavailable (reason)"
   - If API-based: "unavailable (check service)"
   - Continue to next section

Example:

```python
try:
    with open(cache_path) as f:
        data = json.load(f)
    # Parse and output
except FileNotFoundError:
    print("EDGES: unavailable (install Kalshalyst skill)")
except json.JSONDecodeError:
    print("EDGES: unavailable (cache corrupted)")
except Exception as e:
    print(f"EDGES: unavailable ({e})")
```

No single section failure stops the entire brief.

---

## Timestamps & Freshness Checks

**Cache staleness:**
- Kalshalyst: warn if >2 hours old
- Arbiter: warn if >6 hours old
- Xpulse: warn if >4 hours old

**Live API staleness:**
- Coinbase: always fresh (live call)
- Polymarket: acceptable if <1 minute old (edge case)

Check cache timestamp:
```json
{
  "cached_at": "2026-03-08T15:32:18+00:00"
}
```

---

## Line Length & Formatting

**Max line length:** 80 characters (for iMessage/SMS compatibility)

**Section headers:** Always `[SECTION NAME]` with details in parentheses

**Data rows:** Tab-separated or space-padded to align columns

**Example alignment:**
```
TICKER                   SIDE  QTY      PRICE    UNREALIZED
POTUS-2028-DEM           YES   100@48¢  $48      +$18 (exp: 242d)
UKRAINE-2026-NO          YES   50@28¢   $14      +$8 (exp: 118d)
```

---

## Configuration Reference

```yaml
market_morning_brief:
  enabled: true
  morning_time: "07:30"
  evening_time: "18:00"
  timezone: "America/New_York"

  # Kalshi (required for portfolio)
  kalshi:
    enabled: true
    api_key_id: "your-key-id"
    private_key_file: "/path/to/private.key"

  # Coinbase (optional, for crypto)
  coinbase:
    enabled: false
    api_key: "sk-..."
    tickers: ["BTC", "ETH"]

  # Cache paths
  cache_paths:
    kalshalyst: "./state/.kalshi_research_cache.json"
    arbiter: "./state/.crossplatform_divergences.json"
    xpulse: "./state/.x_signal_cache.json"

  # Section toggles
  include:
    portfolio: true
    kalshalyst_edges: true
    arbiter_divergences: true
    xpulse_signals: true
    crypto: false
    polymarket: true
```
