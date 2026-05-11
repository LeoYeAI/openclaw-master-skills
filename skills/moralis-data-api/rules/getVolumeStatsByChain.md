# Get trading stats by chain

Retrieve volume, active wallets and transaction stats for a blockchain over various time periods. Returns data for all chains in a single request.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/volume/chains`

## Response Example

Status: 200

Successful response

```json
{
  "chains": [
    {
      "chainId": "0x1",
      "totalVolume": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "activeWallets": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      },
      "totalTransactions": {
        "5m": 6516719.425429553,
        "1h": 137489621.30780438,
        "6h": 585436101.0503464,
        "24h": 2668170156.0409784
      }
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/volume/chains" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
