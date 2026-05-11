# Get trending tokens

**Solana variant:** Discover tokens gaining popularity based on trading and social metrics.

This EVM endpoint supports Solana via the `chain=solana` parameter.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/discovery/tokens/trending`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f, solana) | No | The chain to query | \`solana\` |
| min_market_cap | number | No | The minimum market cap in usd of a token | \`50000000\` |
| security_score | number | No | The minimum security score of a token | \`80\` |

## Response Example

Status: 200

Returns the token details

```json
[]
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/discovery/tokens/trending?chain=solana&min_market_cap=50000000&security_score=80" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
