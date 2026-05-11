# NFTScan API Reference

## Overview

Comprehensive NFT data service. Base endpoint:

```
https://open-platform.nodereal.io/{apiKey}/nftscan
```

**Supported chains** (pass as `{chain_name}` path parameter):
`eth`, `bnb`, `polygon`, `moonbeam`, `arbitrum`, `optimism`, `platon`, `avalanche`, `cronos`, `fantom`, `gnosis`

## Table of Contents

1. [NFT Asset Queries](#nft-asset-queries) -- Query NFT assets by account, contract, token ID, attributes, and across multiple chains
2. [NFT Transaction Queries](#nft-transaction-queries) -- Query NFT transactions by account, contract, token ID, to address, hash, and search filters
3. [NFT Collection Queries](#nft-collection-queries) -- Retrieve collection info, search collections, get collections by account or ranking
4. [Rankings and Statistics](#rankings-and-statistics) -- Trade/mint/collection rankings, collection statistics, trade distribution, trending, overview, and blue chip data
5. [Account and Collection Analytics](#account-and-collection-analytics) -- Account overview and holding distribution analytics
6. [Utilities](#utilities) -- Get NFT amounts, owners, latest block number, and refresh metadata

---

## NFT Asset Queries

### Get NFTs by account

Returns NFTs owned by an account address.

```
GET /api/v2/account/own/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Owner wallet address |
| chain_name | path | yes | Chain to query |
| erc_type | query | no | `erc721` or `erc1155` |
| contract_address | query | no | Filter by NFT contract |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| show_attribute | query | no | `true` or `false` |
| sort_field | query | no | `mint_time`, `own_time`, `latest_trade_price` |
| sort_direction | query | no | `asc` or `desc` |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "content": [
      {
        "amount": "1",
        "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        "contract_name": "BoredApeYachtClub",
        "token_id": "1",
        "erc_type": "erc721",
        "name": "#1",
        "image_uri": "QmPbxeGcXhYQQNgsC6a36dDyYUcHgMLnGKnF8pVFmGsvqi",
        "owner": "0xaba7161a7fb69c88e16ed9f455ce62b791ee4d03",
        "latest_trade_price": 38.77,
        "latest_trade_symbol": "WETH",
        "mint_price": 0.7,
        "mint_timestamp": 1619133220000,
        "rarity_rank": 2668,
        "rarity_score": 1.06,
        "attributes": [
          {
            "attribute_name": "Background",
            "attribute_value": "Yellow",
            "percentage": "16.49%"
          }
        ]
      }
    ],
    "next": "NS871DD6359B64187E",
    "total": 30000
  },
  "msg": ""
}
```

---

### Get all NFTs by account

Returns all NFTs owned by an account, grouped by contract address.

```
GET /api/v2/account/own/all/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Owner wallet address |
| chain_name | path | yes | Chain to query |
| erc_type | query | no | `erc721` or `erc1155` |
| show_attribute | query | no | `true` or `false` |

**Response:** Array of `CollectionAssetModel` objects, each containing `assets[]`, `contract_address`, `contract_name`, `floor_price`, `items_total`, `owns_total`, `symbol`.

---

### Get minted NFTs by account

Returns NFTs minted by an account address.

```
GET /api/v2/account/mint/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Minter wallet address |
| chain_name | path | yes | Chain to query |
| erc_type | query | no | `erc721` or `erc1155` |
| contract_address | query | no | Filter by NFT contract |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| show_attribute | query | no | `true` or `false` |

---

### Get NFTs by contract

Returns NFTs belonging to a contract, sorted by token_id ascending.

```
GET /api/v2/assets/{contract_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| chain_name | path | yes | Chain to query |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| show_attribute | query | no | `true` or `false` |

---

### Get single NFT

Returns a single NFT asset.

```
GET /api/v2/assets/{contract_address}/{token_id}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| token_id | path | yes | Token ID (Hex or Number) |
| chain_name | path | yes | Chain to query |
| show_attribute | query | no | `true` or `false` |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "amount": "1",
    "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
    "contract_name": "BoredApeYachtClub",
    "token_id": "1",
    "erc_type": "erc721",
    "name": "#1",
    "owner": "0xaba7161a7fb69c88e16ed9f455ce62b791ee4d03",
    "mint_price": 0.7,
    "latest_trade_price": 38.77,
    "rarity_rank": 2668
  },
  "msg": ""
}
```

---

### Get multiple NFTs

Returns multiple NFTs by contract address + token ID pairs.

```
POST /api/v2/assets/batch/{chain_name}
```

**Request body:**
```json
{
  "contract_address_with_token_id_list": [
    {
      "contract_address": "0x3e855b7941fe8ef5f07dad68c5140d6a3ec1b286",
      "token_id": "0x000000000000000000000000000000000000000000000000000000000000013a"
    }
  ],
  "show_attribute": false
}
```

**Response:** Array of `AssetModel` objects.

---

### Search NFTs

Returns NFTs matching search filters. Block number range cannot exceed 10,000.

```
POST /api/v2/assets/filters/{chain_name}
```

**Request body:**
```json
{
  "block_number_start": 14000000,
  "block_number_end": 15000000,
  "contract_address_list": [],
  "cursor": "100",
  "limit": 20,
  "show_attribute": false
}
```

---

### Get NFTs by attributes

Returns NFTs matching specific attribute filters.

```
POST /api/v2/assets/attributes/{chain_name}
```

**Request body:**
```json
{
  "attributes": [
    {
      "attribute_name": "Fur",
      "attribute_values": "Black,Blue"
    }
  ],
  "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
  "cursor": "100",
  "limit": 20,
  "show_attribute": false
}
```

---

### Get all multi-chain NFTs by account

Returns all NFTs owned across multiple chains, grouped by chain and contract.

```
GET /api/v2/assets/chain/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Owner wallet address |
| chain_name | path | yes | Chain to query |
| chain | query | yes | Chain abbreviations separated by `;` (e.g., `eth;bnb`) |
| erc_type | query | no | `erc721` or `erc1155` |

**Response:** Array of `{ chain, collection_assets[] }` objects.

---

## NFT Transaction Queries

### Get transactions by account

```
GET /api/v2/transactions/account/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Account address |
| chain_name | path | yes | Chain to query |
| contract_address | query | no | Filter by NFT contract |
| token_id | query | no | Filter by token ID |
| event_type | query | no | `Mint`, `Transfer`, `Sale`, `Burn` (separate multiple with `;`) |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| sort_direction | query | no | `asc` or `desc` |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "content": [
      {
        "aggregate_exchange_name": "OpenSea",
        "amount": "1",
        "block_number": 12344148,
        "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
        "contract_name": "BoredApeYachtClub",
        "erc_type": "erc721",
        "event_type": "Transfer",
        "exchange_name": "OpenSea",
        "from": "0xaba7161a7fb69c88e16ed9f455ce62b791ee4d03",
        "hash": "0xe93e858f9330afa4581e260198195623aa7f5cd2809012440ea291d317be9f2f",
        "token_id": "1",
        "trade_price": 0.1,
        "trade_symbol": "ETH",
        "timestamp": 1619133220000
      }
    ],
    "next": "NS871DD6359B64187E",
    "total": 30000
  },
  "msg": ""
}
```

---

### Get transactions by contract

```
GET /api/v2/transactions/{contract_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| chain_name | path | yes | Chain to query |
| event_type | query | no | `Mint;Transfer;Sale;Burn` |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| sort_direction | query | no | `asc` or `desc` |

---

### Get transactions by NFT

```
GET /api/v2/transactions/{contract_address}/{token_id}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| token_id | path | yes | Token ID (Hex or Number) |
| chain_name | path | yes | Chain to query |
| event_type | query | no | `Mint;Transfer;Sale;Burn` |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| sort_direction | query | no | `asc` or `desc` |

---

### Get transactions by to address

```
GET /api/v2/transactions/to/{to_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| to_address | path | yes | The `to` address of the transaction |
| chain_name | path | yes | Chain to query |
| event_type | query | no | `Mint;Transfer;Sale;Burn` |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |
| sort_direction | query | no | `asc` or `desc` |

---

### Get transactions by hash

```
POST /api/v2/transactions/txhash/{chain_name}
```

**Request body:**
```json
{
  "event_type": "",
  "tx_hash_list": [
    "0xe93e858f9330afa4581e260198195623aa7f5cd2809012440ea291d317be9f2f"
  ]
}
```

Maximum 50 transaction hashes per request. Response is a flat array of `TransactionModel` objects.

---

### Search transactions

Returns NFT transactions matching search filters. Block number range cannot exceed 10,000.

```
POST /api/v2/transactions/filters/{chain_name}
```

**Request body:**
```json
{
  "block_number_start": 14000000,
  "block_number_end": 15000000,
  "contract_address_list": [],
  "cursor": "100",
  "event_type": "",
  "limit": 20
}
```

---

## NFT Collection Queries

### Get an NFT collection

Returns information for a collection by contract address.

```
GET /api/v2/collections/{contract_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| chain_name | path | yes | Chain to query |
| show_attribute | query | no | Whether to include attribute distribution |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
    "name": "BoredApeYachtClub",
    "symbol": "BAYC",
    "erc_type": "erc721",
    "items_total": 10000,
    "owners_total": 6271,
    "floor_price": 1.113,
    "opensea_floor_price": 91,
    "opensea_verified": true,
    "royalty": 250,
    "deploy_block_number": 12292922,
    "description": "The Bored Ape Yacht Club is a collection of 10,000 unique Bored Ape NFTs...",
    "logo_url": "https://logo.nftscan.com/logo/0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d.png",
    "website": "http://www.boredapeyachtclub.com/",
    "twitter": "BoredApeYC",
    "discord": "https://discord.gg/3P5K3dzgdB"
  },
  "msg": ""
}
```

---

### Search NFT collections

Returns collections matching search filters.

```
POST /api/v2/collections/filters/{chain_name}
```

**Request body:**
```json
{
  "block_number_start": 14000000,
  "block_number_end": 15000000,
  "contract_address_list": [],
  "limit": 20,
  "name": "BoredApeYachtClub",
  "name_fuzzy_search": false,
  "offset": 0,
  "show_collection": false,
  "sort_direction": "desc",
  "sort_field": "floor_price",
  "symbol": "BAYC",
  "twitter": "BoredApeYC"
}
```

---

### Get NFT collections by account

Returns collections owned by an account, sorted by floor_price descending.

```
GET /api/v2/collections/own/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Account address |
| chain_name | path | yes | Chain to query |
| erc_type | query | yes | `erc721` or `erc1155` |
| offset | query | no | Pagination offset |
| limit | query | no | Page size (default 20, max 100) |

---

### Get NFT collections by ranking

Returns ranked collections by trading metrics.

```
GET /api/v2/collections/rankings/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| sort_field | query | no | `volume_total`, `sales_total`, `average_price`, `floor_price`, `volume_1d`, `volume_7d`, `volume_change_1d`, `volume_change_7d`, `average_price_change_1d`, `average_price_change_7d` |
| sort_direction | query | no | `asc` or `desc` |
| limit | query | no | Result size (default 100, max 500) |

**Response includes:** `average_price`, `volume_total`, `sales_total`, `floor_price` plus all standard collection fields.

---

## Rankings and Statistics

### Trade Ranking

```
GET /api/v2/statistics/ranking/trade/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| time | query | no | `1d`, `15m`, `30m`, `1h`, `6h`, `12h` |
| sort_field | query | no | `volume` or `sales` |
| sort_direction | query | no | `asc` or `desc` |
| show_7d_trends | query | no | Whether to include 7-day trend data |

**Response example:**
```json
{
  "code": 200,
  "data": [
    {
      "contract_address": "0x307135a29962f0b338c0103e06e8e7d03bd7267f",
      "contract_name": "Doodles",
      "volume": 4577.1396,
      "sales": 20,
      "average_price": 1.13,
      "floor_price": 1.12,
      "highest_price": 20,
      "lowest_price": 1.113,
      "market_cap": 55288,
      "volume_change": "53%",
      "sales_change": "10%"
    }
  ],
  "msg": ""
}
```

---

### Mint Ranking

```
GET /api/v2/statistics/ranking/mint/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| time | query | no | `1d`, `15m`, `30m`, `1h`, `6h`, `12h`, `3d` |

**Response example:**
```json
{
  "code": 200,
  "data": [
    {
      "contract_address": "0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d",
      "contract_name": "BoredApeYachtClub",
      "floor_price": 1.113,
      "mint_cost": 0.08,
      "mint_total": 10000,
      "mint_total_change": "53%",
      "sale_total": 25
    }
  ],
  "msg": ""
}
```

---

### Collection Ranking

```
GET /api/v2/statistics/ranking/collection/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| sort_field | query | no | `volume_1d`, `volume_7d`, `volume_30d`, `volume_total`, `volume_change_1d`, `volume_change_7d`, `volume_change_30d`, `sales_1d`, `sales_7d`, `sales_30d`, `sales_total`, `sales_change_1d`, `sales_change_7d`, `sales_change_30d`, `floor_price`, `market_cap` |
| sort_direction | query | no | `asc` or `desc` |
| limit | query | no | Result size (default 20, max 100) |

**Response includes:** `volume_1d`, `volume_7d`, `volume_30d`, `volume_total`, `sales_1d`, `sales_7d`, `sales_30d`, `sales_total`, `average_price_1d`, `market_cap`, plus growth rate fields.

---

### Collection Statistics

```
GET /api/v2/statistics/collection/{contract_address}/{chain_name}
```

**Response example:**
```json
{
  "code": 200,
  "data": {
    "contract_address": "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
    "contract_name": "Doodles",
    "erc_type": "erc721",
    "floor_price": 1.113,
    "highest_price": 296.69,
    "items_total": 10000,
    "market_cap": 68642,
    "owners_total": 6271,
    "sales_24h": 3,
    "total_volume": 94607.141,
    "volume_1d": 762.3803,
    "volume_7d": 5705.4187,
    "volume_30d": 18857.0902,
    "average_price_24h": 10.134,
    "next_blue_chip_probability": "52.22%"
  },
  "msg": ""
}
```

---

### Collection Trade Distribution

```
GET /api/v2/statistics/collection/trade/{contract_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| chain_name | path | yes | Chain to query |
| time | query | no | `1d`, `1h`, `4h`, `12h`, `3d`, `7d`, `30d`, `90d` |

**Response example:**
```json
{
  "code": 200,
  "data": [
    {
      "exchange_name": "Opensea",
      "timestamp": 1658729641000,
      "trade_price": 0.1,
      "transaction_hash": "0x382df08489c766cabf26526db6570927b9df7d7fdc41d866d3a7cb784c1fcba0"
    }
  ],
  "msg": ""
}
```

---

### Collection Trending Statistics

```
GET /api/v2/statistics/collection/trending/{contract_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| contract_address | path | yes | NFT contract address |
| chain_name | path | yes | Chain to query |
| time | query | no | `1d`, `1h`, `4h`, `12h`, `3d`, `7d`, `30d`, `90d`, `all` |

**Response example:**
```json
{
  "code": 200,
  "data": [
    {
      "average_price": 0.2542,
      "begin_timestamp": 1658734117714,
      "end_timestamp": 1658735117714,
      "volume": 22.8775
    }
  ],
  "msg": ""
}
```

---

### Collection Overview

```
GET /api/v2/statistics/collection/overview/{chain_name}
```

**Response example:**
```json
{
  "code": 200,
  "data": [
    {
      "contract_address": "0x8a90cab2b38dba80c64b7734e58ee1db38b8992e",
      "contract_name": "Doodles",
      "floor_price": 6.6952
    }
  ],
  "msg": ""
}
```

---

### Blue Chip

Returns blue chip statistics for a collection.

```
GET /api/v2/statistics/blue/chip/{contract_address}/{chain_name}
```

**Response example:**
```json
{
  "code": 200,
  "data": {
    "blue_chip_owner": 5638,
    "next_blue_chip_probability": "88.11%",
    "owner": 6394
  },
  "msg": ""
}
```

---

## Account and Collection Analytics

### Account Overview

```
GET /api/v2/statistics/overview/{account_address}/{chain_name}
```

**Response example:**
```json
{
  "code": 200,
  "data": {
    "bought_count": 1051,
    "bought_value": 148649.85,
    "bought_value_usdt": 246352936.91,
    "burn_count": 0,
    "gas_value": 6.6,
    "gas_value_usdt": 10941,
    "holding_count": 49,
    "holding_value": 9.97,
    "holding_value_usdt": 16522.98,
    "mint_count": 34,
    "receive_count": 22,
    "send_count": 3,
    "sold_count": 1050,
    "sold_value": 148886.72,
    "sold_value_usdt": 246745494
  },
  "msg": ""
}
```

---

### Account Holding Distribution

```
GET /api/v2/statistics/distribution/{account_address}/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| account_address | path | yes | Account address |
| chain_name | path | yes | Chain to query |
| distribution_type | query | no | Default: `volume` |

**Response:** Distribution array with `contract`, `name`, `proportion`, `value` for each held collection.

---

## Utilities

### Get NFT amount by account

```
POST /api/v2/asset/account/amount/{chain_name}
```

**Request body:**
```json
{
  "account_address_list": ["0xe525fae3fc6fbb23af05e54ff413613a6573cff2"]
}
```

Maximum 50 addresses. **Response:**
```json
{
  "code": 200,
  "data": [
    {
      "account_address": "0xe525fae3fc6fbb23af05e54ff413613a6573cff2",
      "erc721_items_total": 100,
      "erc1155_items_total": 20,
      "items_total": 120
    }
  ],
  "msg": ""
}
```

---

### Get NFT owners by contract (ERC721)

```
GET /api/v2/asset/collection/amount/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| contract_address | query | yes | NFT contract address |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "content": [
      {
        "contract_token_id": "0x0000000000000000000000000000000000000000000000000000000000000001",
        "owner": "0x2e97778b97db81b62eb64103813e019f353537cd",
        "token_id": "1"
      }
    ],
    "next": "NS871DD6359B64187E",
    "total": 30000
  },
  "msg": ""
}
```

---

### Get owners by an NFT (ERC1155)

```
GET /api/v2/asset/owners/{chain_name}
```

| Parameter | Location | Required | Description |
|-----------|----------|----------|-------------|
| chain_name | path | yes | Chain to query |
| contract_address | query | yes | NFT contract address |
| token_id | query | yes | Token ID (Hex or Number) |
| cursor | query | no | Pagination cursor |
| limit | query | no | Page size (default 20, max 100) |

**Response example:**
```json
{
  "code": 200,
  "data": {
    "content": [
      {
        "account_address": "0xe525fae3fc6fbb23af05e54ff413613a6573cff2",
        "amount": "120"
      }
    ],
    "next": "NS871DD6359B64187E",
    "total": 30000
  },
  "msg": ""
}
```

---

### Get latest block number

```
GET /api/v2/blocknumber/{chain_name}
```

**Response example:**
```json
{
  "code": 200,
  "data": {
    "block_number": 14839274
  },
  "msg": ""
}
```

---

### Refresh NFT metadata

```
POST /api/v2/refresh/metadata/{chain_name}
```

**Request body:**
```json
{
  "contract_address": "0x3e855b7941fe8ef5f07dad68c5140d6a3ec1b286",
  "token_id": "0x000000000000000000000000000000000000000000000000000000000000013a"
}
```

**Response example:**
```json
{
  "code": 200,
  "data": {
    "reason": "task already exists",
    "status": "SUCCESS"
  },
  "msg": ""
}
```

---

### Refresh NFT metadata by contract

Submits a background task to refresh metadata for an entire contract.

```
POST /api/v2/refresh/metadata/contract/{chain_name}
```

**Request body:**
```json
{
  "contract_address": "0x3e855b7941fe8ef5f07dad68c5140d6a3ec1b286"
}
```

---
