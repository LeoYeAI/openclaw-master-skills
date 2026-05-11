# Get wallet insight metrics

Retrieve comprehensive wallet insight metrics including activity age, transfer counts, counterparties, and swap volume.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/insight`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The wallet address to get insight for | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chains | array | No | The chains to query. If not provided, aggregates across all supported chains. | \`0x1,0x89\` |

## Response Example

Status: 200

Returns wallet insight metrics.

```json
{
  "address": "0xcB1C1FdE09f811B294172696404e88E658659905",
  "addressType": "evm",
  "walletAgeDays": 1314,
  "firstActivityAt": {
    "chain": "0x1",
    "blockNumber": "23583751",
    "blockTimestamp": "2025-10-15T14:41:23.000Z",
    "transactionHash": "0x...",
    "type": "tokenTransfer",
    "direction": "in"
  },
  "lastActivityAt": {
    "chain": "0x1",
    "blockNumber": "23583751",
    "blockTimestamp": "2025-10-15T14:41:23.000Z",
    "transactionHash": "0x...",
    "type": "tokenTransfer",
    "direction": "in"
  },
  "firstInitiatedAt": {
    "chain": "0x1",
    "blockNumber": "23583751",
    "blockTimestamp": "2025-10-15T14:41:23.000Z",
    "transactionHash": "0x...",
    "type": "tokenTransfer",
    "direction": "in"
  },
  "lastInitiatedAt": {
    "chain": "0x1",
    "blockNumber": "23583751",
    "blockTimestamp": "2025-10-15T14:41:23.000Z",
    "transactionHash": "0x...",
    "type": "tokenTransfer",
    "direction": "in"
  },
  "activeDays": 503,
  "activeChains": 9,
  "transactionsInitiated": 724,
  "transactionsInvolved": 754,
  "nativeTransfers": {
    "sent": 210,
    "received": 272,
    "total": 482
  },
  "erc20Transfers": {
    "sent": 210,
    "received": 272,
    "total": 482
  },
  "nftTransfers": {
    "sent": 210,
    "received": 272,
    "total": 482
  },
  "uniqueCounterparties": {
    "sentTo": 412,
    "receivedFrom": 615,
    "total": 777
  },
  "swapVolumeUsd": 11778.556304337722
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/insight?chains=0x1%2C0x89" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
