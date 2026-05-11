# Get token details

Retrieve comprehensive details for a specific token, including metadata and stats. For more detailed tokens stats we recommended to use `getTokenAnalytics` or `getMultipleTokenAnalytics`. For pair stats, we recommend to use `getPairStats`.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/discovery/token`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f, solana) | Yes | The chain to query | \`eth\` |
| token_address | string | Yes | The address of the token | \`0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2\` |

## Response Example

Status: 200

Returns the token details

```json
{
  "chain_id": "0x1",
  "token_address": "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2",
  "token_name": "Maker",
  "token_symbol": "MKR",
  "token_logo": "token_logo_example",
  "block_number": 0,
  "block_timestamp": "block_timestamp_example",
  "links": {
    "bitbucket": "bitbucket_example",
    "discord": "discord_example",
    "facebook": "facebook_example",
    "github": "github_example",
    "instagram": "instagram_example",
    "linkedin": "linkedin_example",
    "medium": "medium_example",
    "reddit": "reddit_example",
    "telegram": "telegram_example",
    "tiktok": "tiktok_example",
    "twitter": "twitter_example",
    "website": "website_example",
    "youtube": "youtube_example"
  },
  "rating": 0,
  "total_number_of_rating": 0,
  "total_liquidity_locked_in_percent": 0,
  "total_supply_locked_in_percent": 0,
  "price_usd": 0,
  "token_age_in_days": 0,
  "on_chain_strength_index": 0,
  "security_score": 88,
  "market_cap": 1351767630.85,
  "fully_diluted_valuation": 1363915420.28,
  "twitter_followers": 255217,
  "holders_change": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  },
  "liquidity_change_usd": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  },
  "experienced_net_buyers_change": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  },
  "volume_change_usd": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  },
  "net_volume_change_usd": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  },
  "price_percent_change_usd": {
    "1h": 14,
    "1d": 14,
    "1w": 162,
    "1M": 162
  }
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/discovery/token?chain=eth&token_address=0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
