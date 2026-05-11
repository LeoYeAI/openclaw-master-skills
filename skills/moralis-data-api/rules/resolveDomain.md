# Resolve Unstoppable domain

Map an Unstoppable domain to its corresponding blockchain address.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/resolve/:domain`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| domain | string | Yes | The domain to be resolved | \`brad.crypto\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| currency | string | No | The currency to query | \`eth\` |

## Response Example

Status: 200

Returns an address

```json
{
  "address": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/resolve/brad.crypto?currency=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
