# Resolve Address to Unstoppable domain

Find the Unstoppable domain linked to a specific blockchain address.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/resolve/:address/domain`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address to be resolved | \`0x94ef5300cbc0aa600a821ccbc561b057e456ab23\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| currency | string | No | The currency to query | \`eth\` |

## Response Example

Status: 200

Returns an unstoppable domain

```json
{
  "name": "sandy.nft"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/resolve/0x94ef5300cbc0aa600a821ccbc561b057e456ab23/domain?currency=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
