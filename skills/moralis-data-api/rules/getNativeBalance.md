# Get native balance by wallet

Check the native token balance (e.g. ETH) for a specific wallet.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/:address/balance`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address from which the native balance will be checked | \`0x057Ec652A4F150f7FF94f089A38008f49a0DF88e\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| to_block | number | No | The block number up to which the balances will be checked. | - |

## Response Example

Status: 200

Returns the native balance for a specific address

```json
{
  "balance": "1234567890"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/0x057Ec652A4F150f7FF94f089A38008f49a0DF88e/balance?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
