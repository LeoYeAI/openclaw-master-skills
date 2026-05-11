# Get NFT collection metadata

Fetch on-chain metadata like name, symbol, and base token URI for an NFT contract. Also returns off-chain metadata, floor prices and more where available.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/nft/:address/metadata`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | The address of the NFT contract | \`0x524cab2ec69124574082676e6f654a18df49a048\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| include_prices | boolean | No | Should NFT last sale prices be included in the result? | - |

## Response Example

Status: 200

Returns the metadata for an NFT collection.

```json
{
  "token_address": "0x2d30ca6f024dbc1307ac8a1a44ca27de6f797ec22ef20627a1307243b0ab7d09",
  "name": "KryptoKitties",
  "synced_at": "synced_at_example",
  "symbol": "RARI",
  "contract_type": "ERC721",
  "possible_spam": "false",
  "verified_collection": "false",
  "collection_logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
  "collection_banner_image": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
  "collection_category": "Art",
  "project_url": "https://www.cryptokitties.co/",
  "wiki_url": "https://en.wikipedia.org/wiki/CryptoKitties",
  "discord_url": "https://discord.com/invite/cryptokitties",
  "telegram_url": "https://t.me/cryptokitties",
  "twitter_username": "CryptoKitties",
  "instagram_username": "cryptokitties",
  "floor_price": "12345",
  "floor_price_usd": "12345.4899",
  "floor_price_currency": "eth",
  "last_sale": {
    "transaction_hash": "0x19e14f34b8f120c980f7ba05338d64c00384857fb9c561e2c56d0f575424a95c",
    "block_timestamp": "2023-04-04T15:59:11.000Z",
    "buyer_address": "0xcb1c1fde09f811b294172696404e88e658659905",
    "seller_address": "0x497a7dee2f13db161eb2fec060fa783cb041419f",
    "price": "7300000000000000",
    "price_formatted": "0.0073",
    "usd_price_at_sale": "13.61",
    "current_usd_value": "15.53",
    "token_address": "0xe8778996e096b39705c6a0a937eb587a1ebbda17",
    "token_id": "170",
    "payment_token": {
      "token_name": "Ether",
      "token_symbol": "ETH",
      "token_logo": "https://cdn.moralis.io/eth/0x.png",
      "token_decimals": "18",
      "token_address": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"
    }
  }
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/nft/0x524cab2ec69124574082676e6f654a18df49a048/metadata?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
