# Get token analytics by token address

**Solana variant:** Retrieve detailed trading analytics for a specific token, including buy volume, sell volume, buyers, sellers, transactions, liquidity and FDV trends over time.

This EVM endpoint supports Solana via the `chain=solana` parameter.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/tokens/:tokenAddress/analytics`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| tokenAddress | string | Yes | The token address to query | \`0x6982508145454ce325ddbe47a25d4ec3d2311933\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f, solana) | No | The chain to query | \`solana\` |

## Response Example

Status: 200

Successful response

```json
{
  "categoryId": "0x1",
  "totalBuyVolume": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "totalSellVolume": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "totalBuyers": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "totalSellers": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "totalBuys": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "totalSells": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "uniqueWallets": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "pricePercentChange": {
    "5m": 6516719.425429553,
    "1h": 137489621.30780438,
    "6h": 585436101.0503464,
    "24h": 2668170156.0409784
  },
  "usdPrice": "530",
  "totalLiquidity": "530",
  "totalFullyDilutedValuation": "530"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/tokens/0x6982508145454ce325ddbe47a25d4ec3d2311933/analytics?chain=solana" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
