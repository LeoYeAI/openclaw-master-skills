---
name: mkts-market-data
description: Real-time market data, portfolio tracking, trade journaling, screening, and news for stocks, crypto, ETFs, commodities, and forex — no API key required to start
metadata: {"openclaw":{"requires":{"bins":["curl"]},"optionalEnv":["MKTS_API_KEY"],"emoji":"📊"}}
---

# mkts Market Data Skill

A complete financial toolkit for AI agents. Get market overviews, live quotes, historical OHLCV data, earnings calendars, and news from 8+ sources. Screen assets by price, volume, and market cap. Compare tickers side-by-side. Track portfolios with P&L, allocation, and benchmark performance. Log trade rationale in a journal. Manage watchlists. No API key needed for market data — register programmatically for higher limits.

**Base URL**: `https://mkts.io/api/v1`

**Auth**: No API key required for basic access (20 req/hour per IP). For higher limits, register for a free key and pass it via header: `-H "X-API-Key: $MKTS_API_KEY"`

### Register for an API Key (Optional)
Get a free API key programmatically for higher rate limits (100 req/hour):
```bash
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","name":"my-agent"}' \
  https://mkts.io/api/v1/register
```
Returns `{ "success": true, "data": { "apiKey": "mk_live_...", ... } }`. Save the key — it is shown only once. Max 3 keys per email.

## Endpoints

### Market Overview
Get global market stats (total market cap, BTC dominance, etc.):
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/market
```

### List Assets
Get a filtered, paginated list of assets:
```bash
# All assets (default: top 50 by market cap)
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/assets"

# Filter by type
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/assets?type=stock&limit=20"

# Filter by sector
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/assets?type=stock&sector=technology"

# Search by name or symbol
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/assets?search=apple"

# Pagination and sorting
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/assets?sort=change24h&dir=desc&limit=10&offset=0"
```

Query params: `type` (crypto|stock|etf|commodity|forex), `sector`, `platform`, `marketType`, `search`, `limit` (1-500), `offset`, `sort` (price|change24h|volume24h|marketCap), `dir` (asc|desc)

### Single Asset
Get details for a specific asset by symbol:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/BTC
```

### Live Quote (Real-time)
Get a fresh quote directly from Yahoo Finance or CoinGecko (shared 60s cache, stricter rate limits):
```bash
# Auto-detect source
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL/live

# Force crypto source
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/bitcoin/live?type=crypto"
```

For stocks/ETFs, the response includes extended-hours fields when available: `marketState` (PRE, REGULAR, POST, CLOSED), `preMarketPrice`, `preMarketChange`, `preMarketChangePercent`, `preMarketTime`, `postMarketPrice`, `postMarketChange`, `postMarketChangePercent`, `postMarketTime`. Times are Unix timestamps in milliseconds. Fields are `null` when the market is not in that session or for asset types that trade 24/7 (crypto).

### Top Movers
Get top gainers and losers:
```bash
# Both gainers and losers
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/movers

# Just gainers, limited to crypto
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/movers?direction=gainers&type=crypto&limit=5"
```

### Screener
Filter assets with range conditions:
```bash
# Stocks down more than 3%, market cap > $10B
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/screen?type=stock&maxChange=-3&minMarketCap=10000000000"

# Crypto under $1 with high volume
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/screen?type=crypto&maxPrice=1&minVolume=1000000"
```

Query params: `type`, `sector`, `minPrice`, `maxPrice`, `minChange`, `maxChange`, `minVolume`, `maxVolume`, `minMarketCap`, `maxMarketCap`, `limit`, `offset`, `sort`, `dir`

### Sector Performance
Get aggregate performance by sector:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/sectors
```

### Compare Assets
Compare multiple assets side-by-side:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/compare?symbols=AAPL,MSFT,GOOGL"
```

### Market Brief
Get a curated summary ideal for morning briefings or agent digests:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/brief
```

Returns: global market stats, top 5 gainers/losers, sector summary, and natural-language highlights.

### Macro Snapshot
Get key macro indicators in one call (BTC, ETH, S&P 500, Nasdaq, Gold, Oil, DXY, VIX, 10Y):
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/macro
```

Returns `{ indicators, generatedAt }`. Each indicator has `name`, `symbol`, `price`, and `change24h`. Snapshot assets (BTC, ETH, SPY, QQQ, GC=F, CL=F) update on data refresh; live indicators (DX-Y.NYB, ^VIX, ^TNX) are fetched in real-time with 60s caching.

### News
Get latest financial news from RSS feeds (free, no extra API cost):
```bash
# All news
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/news

# Filter by category
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/news?category=crypto&limit=10"

# News for a specific symbol (searches all feeds by symbol + company name)
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/news?symbol=HOOD"
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/news?symbol=AAPL&limit=5"
```

Query params: `category` (crypto|markets|commodities|forex), `symbol` (filter by asset symbol — overrides category), `limit` (1-50, default 20).

Returns `{ count, news, sources }` (plus `symbol` when filtering by symbol). Each news item has `title`, `link`, `pubDate`, `source`, and `category`. Sources include CoinDesk, Cointelegraph, Decrypt, MarketWatch, CNBC, Investing.com, OilPrice, and FXStreet.

### Historical Prices (OHLCV)
Get daily historical candles for any asset:
```bash
# Stock — full OHLCV from Yahoo Finance
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/AAPL/history?range=3M"

# Crypto — close + volume from CoinGecko (max 365 days)
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/BTC/history?range=1Y"
```

Query params: `range` (1M|3M|6M|YTD|1Y, default 3M).

Returns `{ symbol, range, candles, source }`. Each candle has `date`, `close`, and optionally `open`, `high`, `low`, `volume`. Stocks/ETFs/commodities include full OHLCV; crypto includes close + volume only.

### Earnings Calendar
Get earnings dates, EPS estimates, and recent quarter history:
```bash
# Real-time lookup for specific symbols (max 20)
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/earnings?symbols=AAPL,TSLA,MSFT"

# Pre-cached weekly view (no real-time Yahoo calls)
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/earnings?week=current"
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/earnings?week=next"
```

Query params: `symbols` (comma-separated, max 20) OR `week` (current|next). Only stocks and ETFs — crypto/commodities are not supported.

Returns `{ earnings }` array. Each record has `symbol`, `name`, `earningsDate`, `earningsDates`, `epsEstimate`, `epsActual`, `revenueEstimate`, `surprisePercent`, and `recentQuarters` (array of `{ date, actual, estimate }`).

### Stock/ETF Details (Fundamentals)
Get comprehensive company data: profile, financials, earnings, analyst consensus, ownership, insider activity, SEC filings, and ETF holdings:
```bash
# Stock fundamentals
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL/details

# ETF details (includes top holdings and sector weightings)
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/SPY/details
```

Stocks and ETFs only — crypto, commodities, and forex are not supported. Real-time Yahoo Finance call with a shared 60s DynamoDB-backed cache (counts against live rate limits).

Returns a rich object with: `symbol`, `name`, `description`, `website`, `industry`, `sector`, `employees`, `headquarters`, `executives`, `trailingPE`, `forwardPE`, `dividendYield`, `beta`, `fiftyTwoWeekHigh`, `fiftyTwoWeekLow`, `targetPrice`, `recommendationKey`, `numberOfAnalysts`, `totalRevenue`, `revenueGrowth`, `grossMargins`, `operatingMargins`, `profitMargins`, `ebitda`, `returnOnAssets`, `returnOnEquity`, `totalCash`, `totalDebt`, `debtToEquity`, `freeCashflow`, `operatingCashflow`, `currentRatio`, `earningsGrowth`, `revenuePerShare`, `earningsQuarterly`, `earningsYearly`, `forwardEstimates`, `insidersPercentHeld`, `institutionsPercentHeld`, `topInstitutionalHolders`, `insiderTransactions`, `netSharePurchaseActivity`, `recommendationTrend`, `upgradeDowngradeHistory`, `calendarEvents`, `secFilings`. ETFs additionally include `fundFamily`, `category`, and `topHoldings` (holdings array, sector weightings, equity holdings ratios).

### SEC Filings
Get filings directly without pulling the full company details payload:
```bash
# Latest filings
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL/filings

# Filter by form type
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/AAPL/filings?type=10-K&limit=5"
```

Query params: `type` (optional SEC form type, e.g. `10-K`, `10-Q`, `8-K`), `limit` (1-50, default 20). Backed by a shared 5-minute DynamoDB cache per symbol.

Returns `{ symbol, count, filings, fetchedAt }`. Each filing has `date`, `type`, `title`, and `edgarUrl`.

### Filings Search
Search filings across a bounded stock or ETF universe:
```bash
# Latest large-cap 8-Ks
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/filings/search?filingType=8-K&minMarketCap=10000000000&limit=20"

# Tech 10-Qs with title keyword filtering
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/filings/search?sector=technology&filingType=10-Q&title=earnings&dateFrom=2026-01-01"
```

Query params: `type` (`stock` or `etf`, default `stock`), `sector`, `search`, `symbols`, `filingType`, `title`, `minMarketCap`, `maxMarketCap`, `dateFrom`, `dateTo`, `limit`, `universe`.

`symbols` is capped at 25 tickers. `universe` is bounded by tier: keyless `10`, free key `40`, premium `150`. `dateFrom` and `dateTo` use `YYYY-MM-DD`. The endpoint uses your snapshot to define the candidate universe, then fetches filings live from Yahoo Finance with a shared per-symbol cache and a shared short-lived result cache.

Returns `{ results, total, limit, scanned, universe, source }`. Each result includes `symbol`, `name`, `sector`, `marketCap`, and a nested `filing` object with `date`, `type`, `title`, and `edgarUrl`. Response headers include `X-Query-Cache` (`hit` or `miss`) and `X-Query-Universe` (effective capped universe).

### Trending / Market Highlights
Get the most active stocks, top gainers, and top losers from Yahoo Finance screener (pre-cached, updated every 30 minutes):
```bash
# All sections
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/trending

# Just gainers
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/trending?section=gainers"

# Limit to top 5 per section
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/trending?count=5"
```

Query params: `section` (trending|gainers|losers — omit for all), `count` (1-50, limits results per section).

Returns `{ trending, gainers, losers, fetchedAt }`. Each item has `symbol`, `shortName`, `price`, `change`, `changePct`, `volume`, `marketCap`. US equities only. Snapshot endpoint (not live), no extra Yahoo calls.

### Fundamentals Time Series
Get historical financial statements (income statement, balance sheet, cash flow) with computed margins:
```bash
# Annual fundamentals (default: last 5 years, all statements)
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL/fundamentals

# Quarterly income statement
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/MSFT/fundamentals?type=quarterly&module=financials"
```

Query params: `type` (annual|quarterly, default annual), `module` (all|financials|balance-sheet|cash-flow, default all).

Stocks and ETFs only — crypto, commodities, and forex are not supported. Real-time Yahoo Finance call with a shared 60s DynamoDB-backed cache (counts against live rate limits).

Returns `{ symbol, type, module, periods, fetchedAt }`. Each period has: `date`, `periodLabel`, `revenue`, `costOfRevenue`, `grossProfit`, `operatingIncome`, `netIncome`, `ebitda`, `eps`, `grossMargin`, `operatingMargin`, `netMargin`, `totalAssets`, `totalLiabilities`, `stockholdersEquity`, `totalDebt`, `cashAndEquivalents`, `workingCapital`, `operatingCashFlow`, `capitalExpenditure`, `freeCashFlow`. Margins are decimals (0.35 = 35%). Periods are sorted chronologically (oldest first).

### Fundamentals Screener
Screen stocks or ETFs using valuation, profitability, growth, leverage, liquidity, and cash-flow metrics:
```bash
# Profitable large-cap tech with strong margins
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/fundamentals/screen?sector=technology&minMarketCap=10000000000&minGrossMargin=0.50&minOperatingMargin=0.20&sort=revenueGrowth"

# ETFs with positive analyst upside
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/fundamentals/screen?type=etf&minTargetPriceUpside=0.05&sort=targetPriceUpside"
```

Query params: `type` (`stock` or `etf`, default `stock`), `sector`, `search`, `symbols`, `limit`, `universe`, `sort`, `dir`, `minMarketCap`, `maxMarketCap`, `minTrailingPE`, `maxTrailingPE`, `minForwardPE`, `maxForwardPE`, `minRevenueGrowth`, `maxRevenueGrowth`, `minGrossMargin`, `maxGrossMargin`, `minOperatingMargin`, `maxOperatingMargin`, `minProfitMargin`, `maxProfitMargin`, `minReturnOnEquity`, `maxReturnOnEquity`, `minReturnOnAssets`, `maxReturnOnAssets`, `minDebtToEquity`, `maxDebtToEquity`, `minCurrentRatio`, `maxCurrentRatio`, `minDividendYield`, `maxDividendYield`, `minFreeCashflow`, `maxFreeCashflow`, `minTotalRevenue`, `maxTotalRevenue`, `minEarningsGrowth`, `maxEarningsGrowth`, `minTargetPriceUpside`, `maxTargetPriceUpside`.

`symbols` is capped at 25 tickers. `universe` is bounded by tier: keyless `10`, free key `40`, premium `150`. Margin, yield, growth, and upside fields are decimals (`0.20 = 20%`). The screener enriches a capped snapshot universe with shared-cache company details, then filters and sorts the enriched set. Query results also use a shared short-lived result cache.

Returns `{ results, total, limit, scanned, universe, source }`. Each result includes snapshot fields plus valuation, growth, profitability, leverage, and analyst fields. Response headers include `X-Query-Cache` (`hit` or `miss`) and `X-Query-Universe` (effective capped universe).

### Options Chain
Get the options chain for a stock or ETF (calls, puts, open interest, implied volatility, expirations):
```bash
# Default (nearest expiration)
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/asset/AAPL/options

# Specific expiration
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/asset/AAPL/options?expiration=2026-03-21"
```

Stocks and ETFs only — crypto, commodities, and forex are not supported. Real-time Yahoo Finance call with a shared 60s DynamoDB-backed cache (counts against live rate limits).

Returns `symbol`, `expirations` (array of available dates), `selectedExpiration`, `lastPrice`, `calls`, `puts`, and `summary` (totalCallOI, totalPutOI, putCallRatio, totalCallVolume, totalPutVolume). Each contract has `strike`, `lastPrice`, `bid`, `ask`, `change`, `percentChange`, `volume`, `openInterest`, `impliedVolatility`, `inTheMoney`, `expiration`, `contractSymbol`.

### Portfolio Card Image
Generate a shareable 1200×630 PNG card showing portfolio summary:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" "https://mkts.io/api/v1/portfolio/card?range=YTD" -o card.png
```

Query params: `range` (1M|3M|6M|YTD|1Y, default YTD). Requires API key. Returns `image/png`.

The card shows total portfolio value, gain/loss with color coding, a sparkline chart, and top holdings by allocation.

### Portfolio (Read)
Get the authenticated user's portfolio holdings with current prices, P&L, and allocation:
```bash
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/portfolio
```

Returns `totalValue`, `totalCost`, `totalGainLoss`, `totalGainLossPercent`, `dayChange`, `dayChangePercent`, and a `holdings` array. Each holding includes `symbol`, `name`, `type`, `quantity`, `avgCostBasis`, `currentPrice`, `currentValue`, `costBasis`, `gainLoss`, `gainLossPercent`, `dayChange`, `dayChangePercent`, and `allocation` (percentage of portfolio). An empty portfolio returns zero totals and an empty holdings array.

### Portfolio (Write)
Add, remove, or clear holdings:
```bash
# Add a holding
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"symbol":"AAPL","name":"Apple Inc.","assetType":"stock","quantity":10,"avgCostBasis":150.00}' \
  https://mkts.io/api/v1/portfolio

# Delete a single holding by ID
curl -s -X DELETE -H "X-API-Key: $MKTS_API_KEY" \
  https://mkts.io/api/v1/portfolio/HOLDING_ID

# Clear all holdings
curl -s -X DELETE -H "X-API-Key: $MKTS_API_KEY" \
  https://mkts.io/api/v1/portfolio
```

POST body fields: `symbol` (required, uppercase), `name` (required), `assetType` (crypto|stock|etf|commodity|forex), `quantity` (> 0), `avgCostBasis` (>= 0). Optional: `purchaseDate` (ISO string, max 20 chars), `notes` (max 1000 chars).
Returns the created holding with a server-generated `id`.

### Portfolio Performance with Benchmarks
Compare your portfolio's historical performance against market benchmarks:
```bash
# YTD performance vs S&P 500
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/portfolio/performance?range=YTD&benchmarks=SPY"

# 3-month performance vs S&P 500 and Bitcoin
curl -s -H "X-API-Key: $MKTS_API_KEY" \
  "https://mkts.io/api/v1/portfolio/performance?range=3M&benchmarks=SPY,BTC-USD"
```

Query params: `range` (1M|3M|6M|YTD|1Y|ALL), `benchmarks` (comma-separated, max 4 from: SPY, QQQ, DIA, IWM, BTC-USD, GLD, AGG).

Returns `portfolio.percentChange`, `portfolio.startValue`, `portfolio.endValue`, per-benchmark `percentChange`, and a unified `chartData` array with daily percentage changes. Empty portfolio returns zero values.

### Journal
Log trade rationale, notes, and observations:
```bash
# List all journal entries
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/journal

# Create a journal entry
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"title":"AAPL thesis","content":"Strong services growth...","symbol":"AAPL","tags":["thesis","buy"]}' \
  https://mkts.io/api/v1/journal

# Delete a journal entry
curl -s -X DELETE -H "X-API-Key: $MKTS_API_KEY" \
  https://mkts.io/api/v1/journal/ENTRY_ID
```

POST body fields: `title` (required, max 200), `content` (required, max 10000). Optional: `symbol`, `tags` (array from: thesis, lesson, mistake, observation, buy, sell, watchlist).
GET returns `{ count, entries }` sorted by most recent first.

### Watchlist
Create and manage watchlists of symbols:
```bash
# List all watchlists
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/watchlist

# Create a watchlist (optionally with symbols)
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"Tech","symbols":["AAPL","MSFT","GOOGL"]}' \
  https://mkts.io/api/v1/watchlist

# Get a single watchlist
curl -s -H "X-API-Key: $MKTS_API_KEY" https://mkts.io/api/v1/watchlist/WATCHLIST_ID

# Update a watchlist (rename, add/remove symbols)
curl -s -X PATCH -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"name":"Big Tech","addSymbols":["AMZN"],"removeSymbols":["GOOGL"]}' \
  https://mkts.io/api/v1/watchlist/WATCHLIST_ID

# Delete a single watchlist
curl -s -X DELETE -H "X-API-Key: $MKTS_API_KEY" \
  https://mkts.io/api/v1/watchlist/WATCHLIST_ID

# Delete all watchlists
curl -s -X DELETE -H "X-API-Key: $MKTS_API_KEY" \
  https://mkts.io/api/v1/watchlist
```

POST body fields: `name` (required, max 100 chars). Optional: `symbols` (array of uppercase symbols).
PATCH body fields (all optional): `name`, `addSymbols` (array), `removeSymbols` (array).
GET returns `{ count, watchlists }` sorted by most recent first. Each watchlist has `id`, `userId`, `name`, `symbols`, `createdAt`, `updatedAt`.

## Response Format

All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "lastUpdated": 1708721400000,
    "requestsRemaining": 94,
    "resetTime": 1708725000000
  }
}
```

Errors:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "meta": { "requestsRemaining": 0, "resetTime": 1708725000000 }
}
```

## Rate Limits

| Tier | Snapshot endpoints | Live endpoints |
|------|-------------------|----------------|
| Keyless (no API key) | 20 req/hour per IP | 20 req/hour per IP |
| Free (with API key) | 100 req/hour | 10 req/hour |
| Premium | 1,000 req/hour | 100 req/hour |

When rate limited, you'll receive a 429 response with a `Retry-After` header (in seconds). Register at `POST /register` for higher limits.

## Error Handling

- **401**: Invalid API key, or API key required (portfolio/journal/watchlist endpoints)
- **404**: Asset not found
- **429**: Rate limit exceeded — wait and retry after `Retry-After` seconds
- **500/502/503**: Server error — retry with backoff

### Ask (Natural Language)
Query market data using natural language. Requires API key. Counts against daily AI usage limit (5/day free, unlimited premium).
```bash
# Screen for assets
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"q":"tech stocks down more than 5%"}' \
  https://mkts.io/api/v1/ask

# Look up a single asset
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"q":"what is bitcoin at?"}' \
  https://mkts.io/api/v1/ask

# Top movers
curl -s -X POST -H "X-API-Key: $MKTS_API_KEY" -H "Content-Type: application/json" \
  -d '{"q":"top crypto gainers today"}' \
  https://mkts.io/api/v1/ask
```

POST body: `{ "q": "your question" }` (max 500 chars). Returns `{ query, action, summary, results, timestamp }`. Supported actions: `screen`, `lookup`, `compare`, `movers`, `macro`, `brief`. Results are cached for 5 minutes.

## Tips for Agents

- **No API key needed to start** — market data endpoints work without auth (20 req/hour). Register at `POST /register` when you need higher limits
- Portfolio, journal, and watchlist endpoints **require an API key** — register first if you need these
- Use `/v1/brief` for morning market summaries — it combines everything in one call
- Use `/v1/screen` for building watchlists or alert conditions
- Use `/v1/compare` when the user asks to compare specific tickers
- Use `/v1/asset/{symbol}/live` only when the user needs a fresh quote — it has stricter rate limits
- Parse the `meta.requestsRemaining` field to manage your rate limit budget
- The `highlights` array in `/v1/brief` contains pre-formatted natural-language summaries
- Use `/v1/portfolio` when the user asks about their holdings, P&L, allocation, or portfolio performance
- Use `POST /v1/portfolio` to add holdings — the `id` is generated server-side, use it for subsequent deletes
- Use `/v1/portfolio/performance?range=YTD&benchmarks=SPY` to answer "how am I doing vs the S&P?"
- Use `/v1/journal` to log trade rationale — attach a `symbol` and `tags` for better organization
- Portfolio, journal, and watchlist endpoints return `Cache-Control: private, no-store` — do not cache these
- Use `/v1/watchlist` to manage symbol watchlists — create a list, then use `/v1/compare` or `/v1/screen` with those symbols
- Use `PATCH /v1/watchlist/{id}` with `addSymbols`/`removeSymbols` to manage symbols without replacing the whole list
- Use `/v1/news?category=crypto` to get relevant headlines before making trade decisions
- Use `/v1/asset/{symbol}/history` for technical analysis — stocks get full OHLCV, crypto gets close + volume
- Use `/v1/earnings?symbols=AAPL` before earnings season — check EPS estimates and recent quarter surprises
- Use `/v1/earnings?week=current` for a quick weekly earnings calendar (zero real-time API calls)
- Use `/v1/portfolio/card` to generate a shareable portfolio image — pipe to a file with `-o card.png`
- Use `/v1/news?symbol=AAPL` to get news specifically about an asset — searches all feeds by symbol and company name
- Use `/v1/macro` for a quick macro dashboard — BTC, ETH, S&P 500, Nasdaq, Gold, Oil, DXY, VIX, and 10Y in one call
- Use `/v1/asset/{symbol}/details` for deep fundamental analysis — earnings, analyst targets, insider activity, SEC filings, and ETF holdings in one call
- Use `/v1/asset/{symbol}/options` for derivatives analysis — get the full options chain with calls, puts, OI, IV, and all available expirations. Combine with `/v1/asset/{symbol}/live` for delta-neutral strategies
- Use `/v1/trending` for live market movers — most active, top gainers, top losers. Pre-cached from Yahoo screener, no live rate limit cost. Filter by `?section=gainers` or limit with `?count=5`
- Use `/v1/asset/{symbol}/fundamentals` for historical financial analysis — revenue trends, margin evolution, balance sheet health over 5 years. Use `?type=quarterly` for recent quarter-by-quarter trends
- Use `POST /v1/ask` for complex natural language queries — it parses intent and routes to the right data. Requires API key, counts against AI daily limit
