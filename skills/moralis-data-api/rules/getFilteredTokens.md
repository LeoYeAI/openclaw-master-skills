# Returns a list of tokens that match the specified filters and criteria

Fetch a list of tokens across multiple chains, filtered and ranked by dynamic on-chain metrics like volume, price change, liquidity, holder composition, and more. Supports advanced filters (e.g. “top 10 whales hold <40%”), category-based inclusion/exclusion (e.g. “exclude stablecoins”), and time-based analytics. Ideal for token discovery, investor research, risk analysis, and portfolio tools. Each token returned includes detailed trading metrics as well as on-chain and off-chain metadata.

## Method

POST

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/discovery/tokens`

## Body

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string | Yes | Chain hex ID (e.g. "0x1" for Ethereum). Required unless 'chains' is provided. See references/FilteredTokens.md for metrics and filter details. | \`0x1\` |
| filters | array | Yes | Array of filter objects. Each has metric, timeFrame, and at least one of gt/lt/eq. Filters are combined with AND logic. See references/FilteredTokens.md for all metrics and timeframes. | \`[object Object]\` |
| sortBy | object | Yes | Sort configuration with metric, timeFrame, and type (ASC or DESC). See references/FilteredTokens.md for all metrics and timeframes. | \`[object Object]\` |
| limit | number | Yes | Maximum number of tokens to return | \`20\` |
| chains | array | No | Array of chain hex IDs for multi-chain queries. Use instead of 'chain' to query multiple chains. | \`0x1,0x89\` |
| categories | object | No | Category-based filtering. Object with 'include' and/or 'exclude' arrays (e.g. ["stablecoin", "meme"]). | \`[object Object]\` |
| timeFramesToReturn | array | No | Which timeframes to include in response metrics. Defaults to all if omitted. See references/FilteredTokens.md for values. | \`oneDay,oneWeek\` |
| metricsToReturn | array | No | Which metrics to include in response. Defaults to all if omitted. See references/FilteredTokens.md for values. | \`volumeUsd,usdPricePercentChange\` |
| excludeMetadata | boolean | No | If true, omits token metadata from response to reduce payload size | \`-\` |

## Response Example

Status: 200

Returns the token details

```json
{
  "metadata": {},
  "metrics": {}
}
```

## Example (curl)

```bash
curl -X POST "https://deep-index.moralis.io/api/v2.2/discovery/tokens" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
  "chain": "0x1",
  "filters": [
    {
      "metric": "volumeUsd",
      "timeFrame": "oneDay",
      "gt": 100000
    }
  ],
  "sortBy": {
    "metric": "volumeUsd",
    "timeFrame": "oneDay",
    "type": "DESC"
  },
  "limit": 20,
  "chains": [
    "0x1",
    "0x89"
  ],
  "categories": {
    "exclude": [
      "stablecoin"
    ]
  },
  "timeFramesToReturn": [
    "oneDay",
    "oneWeek"
  ],
  "metricsToReturn": [
    "volumeUsd",
    "usdPricePercentChange"
  ],
  "excludeMetadata": false
}'
```
