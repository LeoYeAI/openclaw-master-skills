# Filtered Tokens Reference

Complete reference for the `getFilteredTokens` endpoint (`POST /discovery/tokens`). Use this to build token screeners, discovery tools, and market analysis dashboards.

## Metrics

All 21 `tokenExplorerMetrics` values:

| Metric | Description |
|--------|-------------|
| `experiencedBuyers` | Number of experienced (non-new) wallet addresses buying the token |
| `experiencedSellers` | Number of experienced wallet addresses selling the token |
| `netExperiencedBuyers` | Experienced buyers minus experienced sellers |
| `buyers` | Total number of unique buyer addresses |
| `sellers` | Total number of unique seller addresses |
| `netBuyers` | Buyers minus sellers (positive = more buying pressure) |
| `holders` | Change in holder count over the timeframe |
| `totalHolders` | Total number of token holders (use with timeframe `oneDay`) |
| `tokenAge` | Age of the token in days since first seen on-chain |
| `usdPrice` | Current token price in USD |
| `usdPricePercentChange` | Price change as a percentage over the timeframe |
| `marketCap` | Market capitalization in USD |
| `fullyDilutedValuation` | Fully diluted valuation (price x total supply) |
| `volumeUsd` | Total trading volume in USD |
| `buyVolumeUsd` | Buy-side trading volume in USD |
| `sellVolumeUsd` | Sell-side trading volume in USD |
| `netVolumeUsd` | Buy volume minus sell volume in USD |
| `liquidityChange` | Percentage change in liquidity |
| `liquidityChangeUSD` | Absolute change in liquidity in USD |
| `totalLiquidityUsd` | Total liquidity in USD (use with timeframe `oneDay`) |
| `securityScore` | Token security/quality score (0-100, use with timeframe `oneDay`) |

## TimeFrames

All 8 `tokenExplorerTimeFrames` values:

| Value | Period |
|-------|--------|
| `tenMinutes` | 10 minutes |
| `thirtyMinutes` | 30 minutes |
| `oneHour` | 1 hour |
| `fourHours` | 4 hours |
| `twelveHours` | 12 hours |
| `oneDay` | 24 hours |
| `oneWeek` | 7 days |
| `oneMonth` | 30 days |

**Note:** Some metrics like `securityScore`, `totalHolders`, and `totalLiquidityUsd` are point-in-time values — use `oneDay` as the timeframe.

## Filter Object

Each filter requires `metric` + `timeFrame` + at least one comparison operator:

```json
{
  "metric": "volumeUsd",
  "timeFrame": "oneDay",
  "gt": 100000,
  "lt": 50000000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `metric` | string | Yes | One of the 21 metrics above |
| `timeFrame` | string | Yes | One of the 8 timeframes above |
| `gt` | number | No | Greater than this value |
| `lt` | number | No | Less than this value |
| `eq` | number | No | Equal to this value |

Multiple filters in the `filters` array are combined with **AND logic** — all must match.

## Sort Configuration

```json
{
  "metric": "volumeUsd",
  "timeFrame": "oneDay",
  "type": "DESC"
}
```

| Field | Type | Required | Values |
|-------|------|----------|--------|
| `metric` | string | Yes | Any metric from the table above |
| `timeFrame` | string | Yes | Any timeframe from the table above |
| `type` | string | Yes | `ASC` or `DESC` |

## Categories

Use `categories` to include or exclude token categories:

```json
{
  "categories": {
    "include": ["meme"],
    "exclude": ["stablecoin"]
  }
}
```

Known category values: `stablecoin`, `meme`. Both `include` and `exclude` accept arrays of strings. You can use one or both.

## Practical Examples

### 1. Top tokens by 24h volume on Ethereum

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/discovery/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "chain": "0x1",
  "filters": [
    {"metric": "volumeUsd", "timeFrame": "oneDay", "gt": 500000}
  ],
  "sortBy": {"metric": "volumeUsd", "timeFrame": "oneDay", "type": "DESC"},
  "limit": 10,
  "metricsToReturn": ["volumeUsd", "usdPrice", "usdPricePercentChange"],
  "timeFramesToReturn": ["oneDay"]
}'
```

### 2. Tokens gaining holders with high security score

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/discovery/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "chain": "0x1",
  "filters": [
    {"metric": "holders", "timeFrame": "oneDay", "gt": 100},
    {"metric": "securityScore", "timeFrame": "oneDay", "gt": 70}
  ],
  "sortBy": {"metric": "holders", "timeFrame": "oneDay", "type": "DESC"},
  "limit": 20,
  "categories": {"exclude": ["stablecoin"]}
}'
```

### 3. Multi-chain meme token screener

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/discovery/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "chains": ["0x1", "0x89", "0x38", "0x2105"],
  "filters": [
    {"metric": "volumeUsd", "timeFrame": "oneDay", "gt": 50000},
    {"metric": "usdPricePercentChange", "timeFrame": "oneDay", "gt": 5}
  ],
  "sortBy": {"metric": "usdPricePercentChange", "timeFrame": "oneDay", "type": "DESC"},
  "limit": 20,
  "categories": {"include": ["meme"]}
}'
```

### 4. Whale accumulation detector

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/discovery/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "chain": "0x1",
  "filters": [
    {"metric": "netExperiencedBuyers", "timeFrame": "oneWeek", "gt": 50},
    {"metric": "netVolumeUsd", "timeFrame": "oneDay", "gt": 100000},
    {"metric": "totalLiquidityUsd", "timeFrame": "oneDay", "gt": 500000}
  ],
  "sortBy": {"metric": "netExperiencedBuyers", "timeFrame": "oneWeek", "type": "DESC"},
  "limit": 15,
  "excludeMetadata": true
}'
```

## Important Notes

- **`chain` vs `chains`**: Use `chain` (string) for a single chain, or `chains` (array) for multi-chain queries. One is required.
- **AND logic**: All filters must match — there is no OR combinator. To get OR-like behavior, make separate requests.
- **`metricsToReturn` vs `filters`**: Filters control which tokens match; `metricsToReturn` controls which metric data appears in the response. You can filter on a metric without returning it.
- **`excludeMetadata`**: Set to `true` to skip token metadata (name, symbol, logo, etc.) and reduce payload size. Useful for analytics pipelines.
- **`timeFramesToReturn`**: Limits which timeframe buckets appear in response metrics. If omitted, all timeframes are returned.
- **Numeric filter values**: Pass `gt`, `lt`, `eq` as numbers (not strings) in the JSON body.
