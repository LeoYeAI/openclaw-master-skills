# Get snipers by pair address

Identify sniper wallets that bought a token within a specified timeframe (`blocksAfterCreation`). Each wallet returned includes detailed information about how much was bought, sold as well as PnL stats and more.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/pairs/:address/snipers`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The pair address token-transactions are to be retrieved for. | \`0xa3c2076eb97d573cc8842f1db1ecdf7b6f77ba27\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| blocksAfterCreation | number | No | Number of blocks after the creation
 | - |

## Response Example

Status: 200

Returns snipers by pair address.

```json
{
  "transactionHash": "0x2bfcba4715774420936669cd0ff2241d70e9abecab76c9db813602015b3134ad",
  "blockTimestamp": "2022-02-22T00:00:00Z",
  "blockNumber": 21093423,
  "result": [
    {
      "walletAddress": "0x2bfcba4715774420936669cd0ff2241d70e9abec",
      "totalTokensSniped": 0,
      "totalSnipedUsd": 0,
      "totalSnipedTransactions": 0,
      "totalTokensSold": 0,
      "totalSoldUsd": 0,
      "totalSellTransactions": 0,
      "currentBalance": 0,
      "currentBalanceUsdValue": 0,
      "realizedProfitPercentage": 0,
      "realizedProfitUsd": 0,
      "snipedTransactions": [
        {
          "transactionHash": "0x2bfcba4715774420936669cd0ff2241d70e9abec",
          "blocksAfterCreation": 0,
          "transactionTimestamp": 0
        }
      ],
      "sellTransactions": [
        {
          "transactionHash": "0x2bfcba4715774420936669cd0ff2241d70e9abec",
          "blocksAfterCreation": 0,
          "transactionTimestamp": 0
        }
      ]
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/pairs/0xa3c2076eb97d573cc8842f1db1ecdf7b6f77ba27/snipers?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
