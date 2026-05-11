# Get snipers by pair address.

Get all snipers.

## Method

GET

## Base URL

`https://solana-gateway.moralis.io`

## Path

`/token/:network/pairs/:pairAddress/snipers`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| network | string (mainnet) | Yes | The network to query | - |
| pairAddress | string | Yes | The address of the pair to query | \`Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| blocksAfterCreation | number | No | - | - |

## Response Example

Status: 200

```json
{
  "transactionHash": "transactionHash_example",
  "blockNumber": 0,
  "blockTimestamp": "blockTimestamp_example",
  "result": [
    {
      "walletAddress": "walletAddress_example",
      "totalTokensSniped": 0,
      "totalSnipedUsd": 0,
      "totalSnipedTransactions": 0,
      "snipedTransactions": [
        {
          "transactionHash": "transactionHash_example",
          "transactionTimestamp": "transactionTimestamp_example",
          "blocksAfterCreation": 0
        }
      ],
      "totalTokensSold": 0,
      "totalSoldUsd": 0,
      "totalSellTransactions": 0,
      "sellTransactions": [
        {
          "transactionHash": "transactionHash_example",
          "transactionTimestamp": "transactionTimestamp_example",
          "blocksAfterCreation": 0
        }
      ],
      "currentBalance": 0,
      "currentBalanceUsdValue": 0,
      "realizedProfitPercentage": 0,
      "realizedProfitUsd": 0
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://solana-gateway.moralis.io/token/mainnet/pairs/Czfq3xZZDmsdGdUyrNLtRhGc47cXcZtLG4crryfu44zE/snipers" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
