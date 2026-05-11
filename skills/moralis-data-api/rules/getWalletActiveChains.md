# Get active chains by wallet address

List the blockchain networks a wallet is active on, including their first and last seen timestamps. Options to query cross-chain using the `chains` parameter.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/chains`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | Wallet address | \`0xcB1C1FdE09f811B294172696404e88E658659905\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chains | array | No | The chains to query | - |

## Response Example

Status: 200

Returns the active chains for the wallet address.

```json
{
  "address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
  "active_chains": [
    {
      "chain": "eth",
      "chain_id": "0x1"
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xcB1C1FdE09f811B294172696404e88E658659905/chains" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
