# Get ERC20 token metadata by symbols

Fetch metadata (name, symbol, decimals, logo) for a list of ERC20 token symbols.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/erc20/metadata/symbols`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| symbols | array | Yes | The symbols to get metadata for | - |

## Response Example

Status: 200

Returns metadata for a given token contract address (name, symbol, decimals, logo).

```json
[
  {
    "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "address_label": "Binance 1",
    "name": "Kylin Network",
    "symbol": "KYL",
    "decimals": "18",
    "logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
    "logo_hash": "ee7aa2cdf100649a3521a082116258e862e6971261a39b5cd4e4354fcccbc54d",
    "thumbnail": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c_thumb.png",
    "total_supply": "420689899999994793099999999997400",
    "total_supply_formatted": "420689899999994.7930999999999974",
    "implementations": [
      {
        "chainId": "0x1",
        "chain": "eth",
        "chainName": "Ethereum",
        "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933"
      }
    ],
    "fully_diluted_valuation": "3407271444.05",
    "block_number": "block_number_example",
    "validated": 0,
    "created_at": "created_at_example",
    "possible_spam": "false",
    "verified_contract": false,
    "categories": [
      "stablecoin"
    ],
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
    "circulating_supply": "4206864.7489303",
    "market_cap": "3407271444.05"
  }
]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/erc20/metadata/symbols?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
