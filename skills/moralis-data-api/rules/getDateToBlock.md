# Get block by date

Find the closest block to a specific date on a blockchain.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/dateToBlock`

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| date | string | No | Unix date in milliseconds or a datestring (format in seconds or datestring accepted by momentjs) | - |

## Response Example

Status: 200

Returns the block number and corresponding date and timestamp

```json
{
  "date": "2020-01-01T00:00:00+00:00",
  "block": 9193266,
  "timestamp": 1577836811,
  "block_timestamp": "2019-12-31T23:59:45.000Z",
  "hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171",
  "parent_hash": "0x011d1fc45839de975cc55d758943f9f1d204f80a90eb631f3bf064b80d53e045"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/dateToBlock?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
