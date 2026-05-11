# Get DEX token pair reserves

Retrieve liquidity reserves for a token pair on Uniswap V2-based DEXs.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/:pair_address/reserves`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| pair_address | string | Yes | The liquidity pair address | \`0xa2107fa5b38d9bbd2c461d6edf11b11a50f6b974\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| to_block | string | No | The block number to get the reserves from | - |
| to_date | string | No | Get the reserves up to this date (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |

## Response Example

Status: 200

Returns the pair reserves

```json
{
  "reserve0": "220969226548536862025877",
  "reserve1": "844810441191293211036"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/0xa2107fa5b38d9bbd2c461d6edf11b11a50f6b974/reserves?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
