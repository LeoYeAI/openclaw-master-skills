# Get NFT sale prices by collection

Fetch sale prices for NFTs in a contract over a specified number of days. Returns the last sale, lowest sale, highest sale, average sale and total trades within the specified period.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/nft/:address/price`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the NFT collection | \`0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| days | number | No | The number of days to look back to find the lowest price
If not provided 7 days will be the default and 365 is the maximum
 | - |

## Response Example

Status: 200

Returns the sold price details

```json
{
  "last_sale": {
    "transaction_hash": "transaction_hash_example",
    "block_timestamp": "block_timestamp_example",
    "buyer_address": "buyer_address_example",
    "seller_address": "seller_address_example",
    "price": "price_example",
    "price_formatted": "price_formatted_example",
    "usd_price_at_sale": "usd_price_at_sale_example",
    "current_usd_value": "current_usd_value_example",
    "token_id": "token_id_example",
    "payment_token": {
      "token_name": "token_name_example",
      "token_symbol": "token_symbol_example",
      "token_logo": "token_logo_example",
      "token_decimals": "token_decimals_example",
      "token_address": "token_address_example"
    }
  },
  "lowest_sale": {
    "transaction_hash": "transaction_hash_example",
    "block_timestamp": "block_timestamp_example",
    "buyer_address": "buyer_address_example",
    "seller_address": "seller_address_example",
    "price": "price_example",
    "price_formatted": "price_formatted_example",
    "usd_price_at_sale": "usd_price_at_sale_example",
    "current_usd_value": "current_usd_value_example",
    "token_id": "token_id_example",
    "payment_token": {
      "token_name": "token_name_example",
      "token_symbol": "token_symbol_example",
      "token_logo": "token_logo_example",
      "token_decimals": "token_decimals_example",
      "token_address": "token_address_example"
    }
  },
  "highest_sale": {
    "transaction_hash": "transaction_hash_example",
    "block_timestamp": "block_timestamp_example",
    "buyer_address": "buyer_address_example",
    "seller_address": "seller_address_example",
    "price": "price_example",
    "price_formatted": "price_formatted_example",
    "usd_price_at_sale": "usd_price_at_sale_example",
    "current_usd_value": "current_usd_value_example",
    "token_id": "token_id_example",
    "payment_token": {
      "token_name": "token_name_example",
      "token_symbol": "token_symbol_example",
      "token_logo": "token_logo_example",
      "token_decimals": "token_decimals_example",
      "token_address": "token_address_example"
    }
  },
  "average_sale": {
    "price": "price_example",
    "price_formatted": "price_formatted_example",
    "current_usd_value": "current_usd_value_example"
  },
  "total_trades": 0,
  "message": "message_example"
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/nft/0xBC4CA0EdA7647A8aB7C2061c2E118A18a936f13D/price?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
