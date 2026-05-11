# Enhanced API Reference

## Overview

NodeReal Enhanced APIs extend standard JSON-RPC with proprietary methods prefixed with `nr_`. These provide rich token, NFT, and transaction data without the need for custom indexing infrastructure.

**API Endpoint Format:** `https://{chain}-{network}.nodereal.io/v1/{API-key}`

Examples:
- BSC Mainnet: `https://bsc-mainnet.nodereal.io/v1/your-api-key`
- ETH Mainnet: `https://eth-mainnet.nodereal.io/v1/your-api-key`
- opBNB Mainnet: `https://opbnb-mainnet.nodereal.io/v1/your-api-key`
- Combo Mainnet: `https://combo-mainnet.nodereal.io/v1/your-api-key`

The Enhanced API is organized into these categories:

- **Fungible Tokens API** -- ERC-20/BEP-20 token balances, metadata, holdings, holders
- **NFT API** -- ERC-721/ERC-1155 holdings, holders, inventory, metadata
- **Transaction Receipts API** -- Asset transfers, contract creation, transaction details, receipts by block
- **Platform API** -- Account lists, account counts, token lists, daily stats, health check
- **BNBBurn API** -- Block rewards, daily block counts, block-number-by-timestamp
- **Historical Token Holder API** -- Async historical token holder snapshots

---

## Table of Contents

1. [Fungible Tokens API (ERC-20 / BEP-20)](#fungible-tokens-api-erc-20--bep-20) -- Token balances, supply, and holders
2. [NFT APIs (ERC-721 / ERC-1155)](#nft-apis-erc-721--erc-1155) -- NFT holdings, metadata, and inventory
3. [Transaction Receipts API](#transaction-receipts-api) -- Asset transfers and transaction details
4. [Platform API](#platform-api) -- Account lists and daily stats
5. [BNBBurn API](#bnbburn-api) -- Block rewards and daily counts
6. [Historical Token Holder API](#historical-token-holder-api) -- Async historical holder snapshots
7. [Supported Chains for Enhanced APIs](#supported-chains-for-enhanced-apis) -- Chain compatibility reference table
8. [Pagination Patterns](#pagination-patterns) -- Offset and cursor pagination styles
9. [Troubleshooting](#troubleshooting) -- Common issues and solutions
10. [Documentation](#documentation) -- Links to official API docs

---

## Fungible Tokens API (ERC-20 / BEP-20)

### `nr_getTokenBalance20`

Get ERC-20/BEP-20 token balance for an address at a specific block.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The ERC-20/BEP-20 contract address |
| 2 | `address` | string | Target wallet address |
| 3 | `blockNumber` | string | Block number in hex format (e.g. `"0x1312D00"`) or `"latest"` |

**Returns:** `balance` -- The token balance as a hex-encoded 32-byte number.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenBalance20","params":["0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56", "0x8894e0a0c962cb723c1976a4421c95949be2d4e3", "0x1312D00"],"id": 0 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": "0x000000000000000000000000000000000000000002e04bb41ca9ed87e4b22cb6"
}
```

---

### `nr_getTotalSupply20`

Get total supply of an ERC-20/BEP-20 token.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `address` | string | The token contract address |
| 2 | `blockNumber` | string | Block number in hex or `"latest"` |

**Returns:** `totalSupply` -- The total supply as a hex-encoded 32-byte number.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTotalSupply20","params":["0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", "latest"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000061245ba1ae22428223e59d4"
}
```

---

### `nr_getTokenMeta`

Get token metadata including name, symbol, decimals, and token type.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | Address of the token contract |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Readable name of the token |
| `symbol` | string | Token symbol/abbreviation |
| `decimails` | integer | Decimal places used for display |
| `tokenType` | string | Token standard (e.g. `"erc20"`) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenMeta","params":["0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d"],"id": 0 }'
```

**Response:**

```json
{
  "id": "0",
  "jsonrpc": "2.0",
  "result": {
    "name": "USD Coin",
    "symbol": "USDC",
    "decimails": 18,
    "tokenType": "erc20"
  }
}
```

---

### `nr_getTokenHoldings`

Get all ERC-20/BEP-20 tokens and amounts held by an account.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `accountAddress` | string | The wallet address |
| 2 | `page` | string | Page number in hex (starts at `"0x1"`) |
| 3 | `pageSize` | string | Page size in hex, max 100 (`"0x64"`) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `totalCount` | string | Total number of token holdings (hex) |
| `details[].tokenAddress` | string | Token contract address |
| `details[].tokenName` | string | Token name |
| `details[].tokenSymbol` | string | Token symbol |
| `details[].tokenDecimails` | string | Token decimals (hex) |
| `details[].tokenBalance` | string | Token balance (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenHoldings","params":["0x0E34aD56379aceC7F09d815729B70c85adC1Ec99", "0x1","0x12"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "totalCount": "0x34",
    "details": [
      {
        "tokenAddress": "0xfcb5DF42e06A39E233dc707bb3a80311eFD11576",
        "tokenName": "www.METH.co.in",
        "tokenSymbol": "METH",
        "tokenDecimails": "0x12",
        "tokenBalance": "0x0000000000000000000000000000000000000000f"
      }
    ]
  }
}
```

---

### `nr_getTokenHoldingCount`

Get the number of distinct ERC-20 token holdings for an account.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `accountAddress` | string | The wallet address |

**Returns:** `count` -- Hex-encoded number of ERC-20 token holdings.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenHoldingCount","params":["0x35BA0C8AB94F09772A074374647E04F7B939F458"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x4E5"
}
```

---

### `nr_getTokenCount`

Get the total number of tokens of a specific type on the chain.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenType` | string | Token type: `"ERC20"`, `"ERC721"`, `"ERC1155"` |

**Returns:** `result` -- Hex-encoded number of tokens.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenCount","params":["ERC721"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123"
}
```

---

### `nr_getTokenHolders`

Get current token holders and their balances for an ERC-20 token. Uses cursor-based pagination.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The token contract address |
| 2 | `pageSize` | string | Page size in hex, max 100 |
| 3 | `pageKey` | string | Empty string for first page; use returned `pageKey` for subsequent pages |
| 4 | `topN` | string | (Optional) Hex-encoded; returns at most N records sorted by balance |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Key for fetching the next page (e.g. `"100_342"`) |
| `details[].accountAddress` | string | Holder address |
| `details[].tokenBalance` | string | Token balance (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenHolders","params":["0xcea59dce6a6d73a24e6d6944cfabc330814c098a", "0x14",""],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "100_342",
    "details": [
      {
        "accountAddress": "0x00000000100f9d75535cbf23f82e23db5558e8c1",
        "tokenBalance": "0x0000000000000000000000000000000000000000f"
      }
    ]
  }
}
```

---

### `nr_getTokenHolderCount`

Get the total number of holders of an ERC-20 token.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The token contract address |

**Returns:** `count` -- Hex-encoded number of token holders.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenHolderCount","params":["0x2170ed0880ac9a755fd29b2688956bd959f933f8"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123"
}
```

---

## NFT APIs (ERC-721 / ERC-1155)

### `nr_getNFTHoldings`

Get ERC-721/ERC-1155 tokens and amounts held by an address.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `accountAddress` | string | Holder address |
| 2 | `tokenType` | string | (Optional) `"ERC721"` or `"ERC1155"` -- omit for all |
| 3 | `page` | string | Page number in hex |
| 4 | `pageSize` | string | Page size in hex, max 100 |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `totalCount` | string | Total count (hex) |
| `details[].tokenAddress` | string | NFT contract address |
| `details[].tokenIdNum` | string | Number of token IDs held (hex) |
| `details[].tokenName` | string | NFT collection name |
| `details[].tokenSymbol` | string | NFT collection symbol |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTHoldings","params":["0x99817ce62abf5b17f58e71071e590cf958e5a1bf","erc721","0x1","0x14"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "totalCount": "0x1",
    "details": [
      {
        "tokenAddress": "0x5e74094cd416f55179dbd0e45b1a8ed030e396a1",
        "tokenIdNum": "0x12",
        "tokenName": "Pancake Lottery Ticket",
        "tokenSymbol": "PLT"
      },
      {
        "tokenAddress": "0xdf7952b35f24acf7fc0487d01c8d5690a60dba07",
        "tokenIdNum": "0x1",
        "tokenName": "Pancake Bunnies",
        "tokenSymbol": "PB"
      }
    ]
  }
}
```

---

### `nr_getNFTHoldingCount`

Get count of NFT (721/1155) token holdings for an account.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `accountAddress` | string | The wallet address |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `count721` | string | Number of ERC-721 token holdings (hex) |
| `count1155` | string | Number of ERC-1155 token holdings (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTHoldingCount","params":["0x21d45650db732cE5dF77685d6021d7D5d1da807f"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "count721": "0x2",
    "count1155": "0x0"
  }
}
```

---

### `nr_getNFTInventory`

Get the ERC-721/1155 token inventory of an address, filtered by contract address. Uses cursor-based pagination.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `accountAddress` | string | The wallet address |
| 2 | `contractAddress` | string | The NFT contract address |
| 3 | `pageSize` | string | Page size in hex, max 100 |
| 4 | `pageKey` | string | Empty string for first page; use returned `pageKey` for next pages |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Cursor for next page |
| `details[].tokenAddress` | string | NFT contract address |
| `details[].tokenId` | string | Token ID (hex) |
| `details[].balance` | string | Balance (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTInventory","params":["0x0042f9b78c67eb30c020a56d07f9a2fc83bc2514","0x64aF96778bA83b7d4509123146E2B3b07F7deF52","0x14",""],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "100_342",
    "details": [
      {
        "tokenAddress": "0x5e74094cd416f55179dbd0e45b1a8ed030e396a1",
        "tokenId": "0x0000000000000000000000000000000000000000f",
        "balance": "0x00000000000000000000000000000000000000001"
      }
    ]
  }
}
```

---

### `nr_getNFTHolders`

Get the owner addresses for a specific ERC-721/1155 token ID.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The NFT contract address |
| 2 | `tokenId` | string | Token ID in hex format |
| 3 | `topN` | string | (Optional) Hex-encoded; returns at most N records sorted by balance |

**Returns:** Array of owner addresses.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTHolders","params":["0x64aF96778bA83b7d4509123146E2B3b07F7deF52","0x5000004"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": [
    "0x99817ce62abf5b17f58e71071e590cf958e5a1bf",
    "0x5e74094cd416f55179dbd0e45b1a8ed030e396a1"
  ]
}
```

---

### `nr_getNFTHoldersWithBalance`

Get owners with their balances for a specific ERC-721/1155 token ID.

**Supported Chains:** BSC and ETH mainnet only.

> **Note:** If owners length > 30,000, only at most 30,000 records are returned.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The NFT contract address |
| 2 | `tokenId` | string | Token ID in hex format |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `items.ownerAddress` | string | Owner address |
| `items.balance` | string | Token balance (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTHoldersWithBalance","params":["0x64aF96778bA83b7d4509123146E2B3b07F7deF52","0x5000004"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "items": {
      "ownerAddress": "0x123",
      "balance": "0x123"
    }
  }
}
```

---

### `nr_getNFTHolderCount`

Get the number of holders of an NFT (721/1155) token.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The NFT contract address |

**Returns:** `holderCount` -- Hex-encoded number of token holders.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTHolderCount","params":["0x07d971c03553011a48e951a53f48632d37652ba1"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123"
}
```

---

### `nr_getNFTCollectionHolderCount`

Get the number of unique holders for an entire NFT collection.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The NFT contract address |
| 2 | `tokenType` | string | `"ERC721"` or `"ERC1155"` |

**Returns:** `count` -- Hex-encoded number of collection holders.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTCollectionHolderCount","params":["0x07D971C03553011a48E951a53F48632D37652Ba1","ERC721"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x4E5"
}
```

---

### `nr_getNFTCollectionHolders`

Get holders of an NFT collection with optional balance information. Uses cursor-based pagination.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The NFT contract address |
| 2 | `tokenType` | string | `"ERC721"` or `"ERC1155"` |
| 3 | `pageSize` | string | Page size in hex, max 100 |
| 4 | `pageKey` | string | Empty string for first page |
| 5 | `withBalance` | boolean | (Optional) Whether to include balance information |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Cursor for next page |
| `holderAddresses` | array | Returned when `withBalance` is false |
| `holderAddressesWithBalances[].holderAddress` | string | Holder address (when `withBalance` is true) |
| `holderAddressesWithBalances[].tokenBalances.tokenId` | string | Token ID |
| `holderAddressesWithBalances[].tokenBalances.balance` | string | Balance |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTCollectionHolders","params":["0xC244E2A5c6bbC89cfda2c32Ae0086052c95c3B55","ERC1155","0x14","",true],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "100_342",
    "holderAddressesWithBalances": [
      {
        "holderAddress": "0x000001f568875f378bf6d170b790967fe429c81a",
        "tokenBalances": {
          "tokenId": "9446",
          "balance": "1"
        }
      }
    ]
  }
}
```

---

### `nr_getNFTMeta`

Get metadata for a specific NFT token (name, description, image URL, attributes).

**Supported Chains:** BSC and ETH mainnet only.

> **Note:** NFT metadata is updated asynchronously. If the metadata is empty on first call but the URI is valid, call the API again -- the background thread will fetch and cache the metadata from the token URI.

> **Warning:** The `meta` field is fetched from `meta_url` (token URI), which is off-chain data. The content can change over time without any on-chain transaction. Do not use meta for security-, permission-, pricing-, or funds-related decisions.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The NFT contract address |
| 2 | `tokenId` | string | Token ID in hex format |
| 3 | `tokenType` | string | `"ERC721"` or `"ERC1155"` |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `token_address` | string | Token contract address |
| `token_id` | string | Token ID (decimal) |
| `meta_url` | string | Token URI pointing to metadata |
| `meta` | string | JSON string of the metadata content |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTMeta","params":["0xEA5613EBBBE1E69BF5F05252C215462254F41565","0x7C7","ERC721"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "token_address": "0xea5613ebbbe1e69bf5f05252c215462254f41565",
    "token_id": "1991",
    "meta": "{\"name\":\"Standard Green Pepe\",\"description\":\"Standard Green Pepe with Earth\\n\\nNothing is beyond our reach\",\"category\":\"memes\",\"collection_address\":\"0xea5613ebBBE1E69Bf5F05252C215462254F41565\",\"creator\":\"0x3988c52ac9a2f9b2e591e14e173161cec6ce98ff\",\"ifps_image\":\"Qme8HFmv5aM2J1nGwxgQqU1Yt2H7e7zVHbadQxqb4Aqynq\",\"attributes\":[]}",
    "meta_url": "https://ipfs.io/ipfs/QmRzUasL1uyFjT9bbgEq5XaRjRgdUo3Q4K9qfHhEjRsy7A"
  }
}
```

---

### `nr_getNFTTokenCount`

Get the number of token IDs in an NFT (721/1155) collection.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The NFT contract address |

**Returns:** `tokenCount` -- Hex-encoded number of token IDs.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTTokenCount","params":["0x07d971c03553011a48e951a53f48632d37652ba1"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123"
}
```

---

### `nr_getNFTTokens`

Get list of token IDs and their total supply for an NFT collection. Uses cursor-based pagination.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The NFT contract address |
| 2 | `tokenType` | string | `"ERC721"` or `"ERC1155"` |
| 3 | `pageSize` | string | Page size in hex, max 100 |
| 4 | `pageKey` | string | Empty string for first page |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `[].tokenId` | string | Token ID (hex) |
| `[].totalSupply` | string | Total supply (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTTokens","params":["0x07d971c03553011a48e951a53f48632d37652ba1","ERC721","0x14",""],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": [
    {
      "tokenId": "0x123",
      "totalSupply": "0x123"
    }
  ]
}
```

---

### `nr_getNFTTokenOwners`

Get the list of owners for all token IDs in an NFT collection. Uses cursor-based pagination.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The NFT contract address |
| 2 | `tokenType` | string | `"ERC721"` or `"ERC1155"` |
| 3 | `pageSize` | string | Page size in hex, max 100 |
| 4 | `pageKey` | string | Empty string for first page |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Cursor for next page |
| `items.tokenId` | string | Token ID (hex) |
| `items.ownerAddress` | string | Owner address |
| `items.balance` | string | Balance (hex) |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getNFTTokenOwners","params":["0x07d971c03553011a48e951a53f48632d37652ba1","ERC721","0x14",""],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "qh000000-0X5j-WSqq-mCLq-kPfWRH8B1GPS",
    "items": {
      "tokenId": "0x123",
      "ownerAddress": "0x123",
      "balance": "0x0000000000000000000000000000000000000000000000000000000000001bdf"
    }
  }
}
```

---

### `nr_getSummedSupply1155`

Get the summed total supply across all token IDs in an ERC-1155 contract.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The ERC-1155 contract address |

**Returns:** `summedSupply` -- Hex-encoded summed supply.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getSummedSupply1155","params":["0xed8711feff83b446158259981fd97645856e82a5"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123456"
}
```

---

### `nr_getTokenBalance1155`

Get ERC-1155/BEP-1155 token balance for a specific token ID and account.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The ERC-1155 contract address |
| 2 | `accountAddress` | string | Account to check balance for |
| 3 | `blockNumber` | string | Block number in hex or `"latest"` / `"earliest"` |
| 4 | `tokenId` | string | Token ID in hex format |

**Returns:** `balance` -- 32-byte hex-encoded balance.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenBalance1155","params":["0x98387108842a7CfC7bA23E080030351f6ea68ac0", "0x38767ebadf9b4f9302c5cb88be9a3426234bc9a5", "0x1333EF1", "0x1"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x000000000000000000000000000000000000000000000000000000000000006c"
}
```

---

### `nr_getTokenBalance721`

Get ERC-721/BEP-721 token balance (count of owned tokens) for an account.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The ERC-721 contract address |
| 2 | `accountAddress` | string | Account to check balance for |
| 3 | `blockNumber` | string | Block number in hex or `"latest"` / `"earliest"` |

**Returns:** `balance` -- 32-byte hex-encoded balance (count of owned NFTs).

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTokenBalance721","params":["0x07D971C03553011a48E951a53F48632D37652Ba1", "0x3d99cfc0839a0b2fe5ca8451cb160bdd205234f6", "0x1333EF1"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000000000000000000000002a5d"
}
```

---

### `nr_getTotalSupply1155`

Get total supply of a specific ERC-1155 token ID.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The ERC-1155 contract address |
| 2 | `blockNumber` | string | Block number in hex or `"latest"` / `"earliest"` |
| 3 | `tokenId` | string | Token ID in hex format |

**Returns:** `totalSupply` -- 32-byte hex-encoded total supply.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTotalSupply1155","params":["0xBe23dD3c644DB84d32eA91d6121A55b8B3Eea6F1","0x1333EF1","0x80"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000000000000000000000000001"
}
```

---

### `nr_getTotalSupply721`

Get total supply of an ERC-721 token.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `tokenAddress` | string | The ERC-721 contract address |
| 2 | `blockNumber` | string | Block number in hex or `"latest"` / `"earliest"` |

**Returns:** `totalSupply` -- 32-byte hex-encoded total supply.

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTotalSupply721","params":["0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d", "0x895440"],"id": 0 }'
```

**Response:**

```json
{
  "id": "0",
  "jsonrpc": "2.0",
  "result": "0x000000000000000000000000000000000000000005bf8de73e1a17553e3e59d4"
}
```

---

## Transaction Receipts API

### `nr_getAssetTransfers`

Get transfer history including normal, ERC-20, ERC-721, ERC-1155, and internal transactions.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:** Single object parameter with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | array | List of categories: `"external"`, `"internal"`, `"20"`, `"721"`, `"1155"` |
| `fromBlock` | string | Hex block number or `"latest"`. Range with `toBlock` must be <= 100,000 blocks |
| `toBlock` | string | Hex block number or `"latest"` |
| `contractAddresses` | array | (Optional) Filter by contract addresses, max 100 |
| `fromAddress` | string | (Optional) Sender address filter |
| `toAddress` | string | (Optional) Recipient address filter |
| `order` | string | `"asc"` or `"desc"` |
| `transactionHash` | string | (Optional) Specific transaction hash filter |
| `maxCount` | string | Hex-encoded max results, max `"0x3E8"` (1000) |
| `excludeZeroValue` | boolean | (Optional) Exclude zero-value transfers |
| `pageKey` | string | UUID for pagination; omit for first request |

**Category descriptions:**
- `"external"` -- Normal transactions (native coin transfers like BNB/ETH, contract interactions without token events)
- `"internal"` -- Internal contract calls and cross-contract calls
- `"20"` -- ERC-20 token transfer events
- `"721"` -- ERC-721 NFT transfer events
- `"1155"` -- ERC-1155 transfer events

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | UUID for next page |
| `transfers[].category` | string | Transfer category |
| `transfers[].blockNum` | string | Block number (hex) |
| `transfers[].from` | string | Sender address |
| `transfers[].to` | string | Recipient address |
| `transfers[].value` | string | Transfer value (hex) |
| `transfers[].erc721TokenId` | string | ERC-721 token ID (when category is `"721"`) |
| `transfers[].erc1155Metadata` | array | ERC-1155 metadata (when category is `"1155"`) |
| `transfers[].asset` | string | Asset symbol (e.g. `"BNB"`, `"ETH"`, token symbol) |
| `transfers[].hash` | string | Transaction hash |
| `transfers[].contractAddress` | string | Contract address (null for external) |
| `transfers[].decimal` | string | Token decimals |
| `transfers[].blockTimeStamp` | integer | Block timestamp |
| `transfers[].gasPrice` | integer | Gas price (external only) |
| `transfers[].gasUsed` | integer | Gas used (external only) |
| `transfers[].receiptsStatus` | integer | Receipt status: 1=success, 0=failed |

**Curl Example:**

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"nr_getAssetTransfers","params":[{"category": ["external","20"],"fromBlock": "0xE81916","toBlock": "0xE81917","order": "asc","excludeZeroValue": false,"maxCount": "0x5","pageKey": "qg000000-0075-RyKy-efk2-Fx9n32gAu432"}],"id":1}'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "qh000000-0X5j-WSqq-mCLq-kPfWRH8B1GPS",
    "transfers": [
      {
        "category": "external",
        "blockNum": "0x6c92dd",
        "from": "0x646eafba97ec6ee7631887cdee468b323dd65d4f",
        "to": "0x8f07f7312f3ede8b0094f09ab1554c8d89f47ddf",
        "value": "0x0",
        "asset": "BNB",
        "hash": "0xf7605ce61c1855348cde8512d752265a8cbbf57e0ac4c8bc259155f8c1592838",
        "blockTimeStamp": 1620089457,
        "gasPrice": 5000000000,
        "gasUsed": 35813,
        "receiptsStatus": 1
      },
      {
        "category": "20",
        "blockNum": "0x3b8322",
        "from": "0x0554a5d083abf2f056ae3f6029e1714b9a655174",
        "to": "0x28451d455f009a30b37bbe74175c9f3460f45cc7",
        "value": "0x00000000000000000000000000000000000000000000000564d702d38f5e0000",
        "asset": "TWT",
        "hash": "0xc16db18719864e6188578d5870e6f30e84d93c52beeb3630ead1a251e460ce4b",
        "contractAddress": "0x4b0f1812e5df2a09796481ff14017e6005508003",
        "decimal": "18",
        "blockTimeStamp": 1610380207
      },
      {
        "category": "721",
        "blockNum": "0xe97966",
        "from": "0x0000000000000000000000000000000000000000",
        "to": "0xa35ea428864f790f76b80d834b7dbe4340fd8d90",
        "value": "0x0",
        "erc721TokenId": "0x000000000000000000000000000000000000000000000000000000000016ed41",
        "asset": "SpaceShip",
        "hash": "0x6ed64468e1ee365e9670ec373eecdae2ff186d3354e2f88824eddd8d2f1bcccd",
        "contractAddress": "0x25828c7d4914694cbb514bb8f88ef94e715e4819",
        "blockTimeStamp": 1644998842
      },
      {
        "category": "1155",
        "blockNum": "0xeed938",
        "from": "0x0000000000000000000000000000000000000000",
        "to": "0x3acd618733de89269496768784d6b07f844ce480",
        "value": "0x0",
        "erc1155Metadata": [
          {
            "tokenId": "51c7d5f32f7dee06107a3d522b6e0902521ba99806e191acd74b349e00000001",
            "value": "0000000000000000000000000000000000000000000000000000000000000001"
          }
        ],
        "asset": "MELOSPRELUDE1",
        "hash": "0xa931aab01613dce9ab17f22caad4efa3fd209785f675c5d81f19b10179d2f631",
        "contractAddress": "0x42616b05cfe1af50e4488c8930d7e7d65bf87ce9",
        "blockTimeStamp": 1646059155
      }
    ]
  }
}
```

---

### `nr_getAssetTransfersCount`

Get the count of asset transfers matching criteria.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:** Single object parameter with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | array | List of categories: `"external"`, `"internal"`, `"20"`, `"721"`, `"1155"` |
| `fromBlock` | string | Hex block number or `"latest"` |
| `toBlock` | string | Hex block number or `"latest"` |
| `contractAddresses` | array | (Optional) Contract address filter, max 100 |
| `fromAddress` | string | (Optional) Sender address filter |
| `toAddress` | string | (Optional) Recipient address filter |
| `transactionHash` | string | (Optional) Transaction hash filter |
| `excludeZeroValue` | boolean | (Optional) Exclude zero-value transfers |

**Returns:** `result` -- Hex-encoded transfer count.

**Curl Example:**

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"nr_getAssetTransfersCount","params":[{"category": ["external","20"],"fromBlock": "0xE81916","toBlock": "0xE81917","excludeZeroValue": false}],"id":1}'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x4"
}
```

---

### `nr_getTransactionByAddress`

Get transfers for a specific address with filtering by category, direction, and block range.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:** Single object parameter with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | array | List of categories: `"external"`, `"20"`, `"721"`, `"1155"` |
| `fromBlock` | string | Hex block number or `"latest"`. Range with `toBlock` must be <= 1,000 blocks |
| `toBlock` | string | Hex block number or `"latest"` |
| `address` | string | Address to query (required) |
| `addressType` | string | `"from"`, `"to"`, `"contract"`, or null for all |
| `order` | string | `"asc"` or `"desc"` |
| `maxCount` | string | Hex-encoded max results, max `"0x3E8"` (1000) |
| `excludeZeroValue` | boolean | (Optional) Exclude zero-value transfers |
| `pageKey` | string | UUID for pagination; omit for first request |

**Returns:** Same structure as `nr_getAssetTransfers`.

**Curl Example:**

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"nr_getTransactionByAddress","params":[{"category": ["external","20"],"addressType": "from","address": "0xd7cdba6d6fa60a0aa9518dc0dacd0ad896cc02bd","order": "asc","excludeZeroValue": false,"maxCount": "0x5","fromBlock": "0x4","toBlock": "0x615856d7","pageKey": "qg000000-0075-RyKy-efk2-Fx9n32gAu432"}],"id":1}'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "pageKey": "qh000000-0X5j-WSqq-mCLq-kPfWRH8B1GPS",
    "transfers": [
      {
        "category": "external",
        "blockNum": "0x6c92dd",
        "from": "0x646eafba97ec6ee7631887cdee468b323dd65d4f",
        "to": "0x8f07f7312f3ede8b0094f09ab1554c8d89f47ddf",
        "value": "0x0",
        "asset": "BNB",
        "hash": "0xf7605ce61c1855348cde8512d752265a8cbbf57e0ac4c8bc259155f8c1592838",
        "blockTimeStamp": 1620089457,
        "gasPrice": 5000000000,
        "gasUsed": 35813,
        "receiptsStatus": 1
      }
    ]
  }
}
```

---

### `nr_getTransactionByAddressCount`

Get transfer count for an address with filtering by category and direction.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:** Single object parameter with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `category` | array | List of categories: `"external"`, `"internal"`, `"20"`, `"721"`, `"1155"` |
| `fromBlock` | string | Hex block number or `"latest"`. Range with `toBlock` must be <= 1,000 blocks |
| `toBlock` | string | Hex block number or `"latest"` |
| `address` | string | Address to query |
| `addressType` | string | `"from"`, `"to"`, `"contract"`, or null for all |

**Returns:** `result` -- Hex-encoded transfer count.

**Curl Example:**

```bash
curl https://eth-mainnet.nodereal.io/v1/your-api-key \
    -X POST \
    -H "Content-Type: application/json" \
    -d '{"jsonrpc":"2.0","method":"nr_getTransactionByAddressCount","params":[{"category": ["external","20"],"addressType": "from","fromBlock": "0x4","toBlock": "0x615856d7","pageKey": "qg000000-0075-RyKy-efk2-Fx9n32gAu432"}],"id":1}'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": "0x123"
}
```

---

### `nr_getTransactionDetail`

Get detailed transaction information including token transfers, gas details, and input/output data.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `transactionHash` | string | The transaction hash |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `hash` | string | Transaction hash |
| `blockHash` | string | Block hash |
| `blockNumber` | integer | Block number |
| `blockTimeStamp` | integer | Block timestamp |
| `value` | string | Transaction value |
| `fees` | integer | Transaction fees |
| `ethereumSpecific.receiptsStatus` | integer | 1=success, 0=failed |
| `ethereumSpecific.nonce` | integer | Transaction nonce |
| `ethereumSpecific.gas` | integer | Gas limit |
| `ethereumSpecific.gasUsed` | integer | Gas used |
| `ethereumSpecific.gasPrice` | integer | Gas price |
| `ethereumSpecific.input` | string | Input data (hex) |
| `vin.address` | string | Input address |
| `vout.address` | string | Output address |
| `tokenTransfers[].category` | string | Transfer type (`"20"`, `"721"`, `"1155"`) |
| `tokenTransfers[].from` | string | From address |
| `tokenTransfers[].to` | string | To address |
| `tokenTransfers[].token` | string | Token contract address |
| `tokenTransfers[].tokenName` | string | Token name |
| `tokenTransfers[].symbol` | string | Token symbol |
| `tokenTransfers[].decimal` | integer | Token decimals |
| `tokenTransfers[].value` | string | Transfer value |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTransactionDetail","params":["0x07D971C03553011a48E951a53F48632D37652Ba1"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "hash": "0x194def7bf7f6afe6880f38fc6c8679721135bbabf53ada450fcc8080e4ff2f74",
    "blockHash": "0xefa8d65612cbf1e0a2b49e51bb594e7206ab3e2baa6e20ad209910bffb36b812",
    "blockNumber": 21082531,
    "blockTimeStamp": 1662429025,
    "value": "0",
    "fees": 705875000000000,
    "ethereumSpecific": {
      "receiptsStatus": 1,
      "nonce": 334,
      "gas": 141175,
      "gasUsed": 141175,
      "gasPrice": 5000000000,
      "input": "0x68a1a8c60000000000000000000000000000000000000000000000003782dace9d900000"
    },
    "vin": {
      "address": "0xa431b01ba9cf3dbc1baa11be38c4a341378fdc79",
      "isAddress": false,
      "value": "0"
    },
    "vout": {
      "address": "0xa431b01ba9cf3dbc1baa11be38c4a341378fdc79",
      "isAddress": false,
      "value": "0"
    },
    "tokenTransfers": [
      {
        "category": "20",
        "from": "0xa431b01ba9cf3dbc1baa11be38c4a341378fdc79",
        "to": "0x882a6ca7f03fc489661a18f3b8a2c20e05eabfdc",
        "token": "0xb69974f60eb1499ef06e6dfca23a6fd1f631e40c",
        "tokenName": "NMT",
        "symbol": "NMT",
        "decimal": 18,
        "value": "800000000000000000"
      }
    ]
  }
}
```

---

### `nr_getContractCreationTransaction`

Get the creation transaction details for any smart contract.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The contract address |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `hash` | string | Creation transaction hash |
| `blockNumber` | integer | Block number |
| `blockHash` | string | Block hash |
| `timestamp` | integer | Block timestamp |
| `transactionIndex` | integer | Transaction index in block |
| `from` | string | Deployer address |
| `to` | null | Always null for contract creation |
| `gas` | integer | Gas limit |
| `gasPrice` | integer | Gas price |
| `gasUsed` | integer | Gas used |
| `cumulativeGasUsed` | integer | Cumulative gas used |
| `contractAddress` | string | Created contract address |
| `txreceiptStatus` | integer | 1=success, 0=failed |
| `input` | string | Contract bytecode (hex) |
| `nonce` | integer | Deployer nonce |
| `value` | string | Value sent with creation |

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getContractCreationTransaction","params":["0xc297020be32dc91bb24ce4cad116eb50e55ec5ae"],"id": 1 }'
```

**Response:**

```json
{
  "id": "1",
  "jsonrpc": "2.0",
  "result": {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
      "hash": "0x3c49bfbe70e0188142821dfeaba482bce0e44c9953b31415b78b04e836c072dc",
      "blockNumber": 56848,
      "blockHash": "0xf769665c8bf51f0a6678503e1a5e1f2bb494619c3b1fc3cc98eb81f9d6a1ddb8",
      "timestamp": 1598842324,
      "transactionIndex": 0,
      "from": "0xa3fd5cc5ba356433b28209d812ff0cf261881e1b",
      "to": null,
      "gas": 6721975,
      "gasPrice": 20000000000,
      "gasUsed": 225237,
      "cumulativeGasUsed": 225237,
      "contractAddress": "0xc297020be32dc91bb24ce4cad116eb50e55ec5ae",
      "txreceiptStatus": 1,
      "nonce": 0,
      "value": "0x0"
    }
  }
}
```

---

### `nr_getTransactionReceiptsByBlockHash`

Get all transaction receipts for a given block hash.

**Supported Chains:** BSC mainnet, BSC testnet, ETH mainnet, ETH Goerli, and Polygon mainnet.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `blockHash` | string | The block hash |

**Returns:** Array of transaction receipt objects (same structure as `eth_getTransactionReceipt`).

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTransactionReceiptsByBlockHash","params":["0x18ef932f9fe3f5c52c8f489c4a466c0e034b85225eb9c6b1415abce6006bf88a"],"id": 0 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 0,
  "result": [
    {
      "type": "0x0",
      "from": "0x4acc5a5505e6ce8be4a93fa9eab4529de6cdceff",
      "to": "0x0000000000f7cdcb778b0c33b09e175e4786f943",
      "status": "0x1",
      "cumulativeGasUsed": "0x12904",
      "logsBloom": "0x00200000010000000000...",
      "logs": [
        {
          "address": "0x55d398326f99059ff775485246999027b3197955",
          "topics": [
            "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef",
            "0x0000000000000000000000000000000000f7cdcb778b0c33b09e175e4786f943",
            "0x000000000000000000000000b19fb4ae2fd58d0c6503a3f375eb0d80bd523d03"
          ],
          "data": "0x00000000000000000000000000000000000000000000012002d5ffff439c0000",
          "blockNumber": "0x11a6c2c",
          "transactionHash": "0xe57ca657da05171aafbe5bea40758808b04f6d03a964dfb803f0ba16d14b887b",
          "transactionIndex": "0x0",
          "blockHash": "0x18ef932f9fe3f5c52c8f489c4a466c0e034b85225eb9c6b1415abce6006bf88a",
          "logIndex": "0x0",
          "removed": false
        }
      ],
      "transactionHash": "0xe57ca657da05171aafbe5bea40758808b04f6d03a964dfb803f0ba16d14b887b",
      "contractAddress": null,
      "gasUsed": "0x12904",
      "blockHash": "0x18ef932f9fe3f5c52c8f489c4a466c0e034b85225eb9c6b1415abce6006bf88a",
      "blockNumber": "0x11a6c2c",
      "transactionIndex": "0x0"
    }
  ]
}
```

---

### `nr_getTransactionReceiptsByBlockNumber`

Get all transaction receipts for a given block number.

**Supported Chains:** BSC mainnet, BSC testnet, ETH mainnet, ETH Goerli, and Polygon mainnet.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `blockNumber` | string | Block number in hex format (e.g. `"0x11a6c2c"`) |

**Returns:** Array of transaction receipt objects (same structure as `eth_getTransactionReceipt`).

**Curl Example:**

```bash
curl https://bsc-mainnet.nodereal.io/v1/your-api-key \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getTransactionReceiptsByBlockNumber","params":["0x11a6c2c"],"id": 0 }'
```

**Response:** Same structure as `nr_getTransactionReceiptsByBlockHash`.

---

## Platform API

### `nr_health`

Health check endpoint for the MegaNode service. This is a GET method.

**Supported Chains:** BSC and ETH mainnet only.

**Parameters:** None.

**Returns:** HTTP status code 200 if healthy, 500 if unhealthy.

**Curl Example:**

```bash
curl --location --request GET 'https://bsc-mainnet.nodereal.io/v1/your-api-key/nr_health'
```

---

### `nr_getAccountList`

Get active accounts ordered by token balance.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `maxCount` | string | Hex-encoded max number of results to return |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Pagination key for next page |
| `accountBalance[].Address` | string | Account address |
| `accountBalance[].Balance` | string | Account balance (hex) |

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getAccountList",
  "jsonrpc": "2.0",
  "params": [
    {
      "maxCount": "0x64"
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "pageKey": "ab000000-0000-0000-0000-00000000000r",
    "accountBalance": [
      {
        "Address": "0x4200000000000000000000000000000000000016",
        "Balance": "0x81f7b4a22c0b1ecebf5"
      }
    ]
  }
}
```

---

### `nr_getAccountListCount`

Get the total count of active accounts.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** None.

**Returns:** `result` -- Hex-encoded count of active accounts.

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getAccountListCount",
  "jsonrpc": "2.0",
  "params": []
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x33511"
}
```

---

### `nr_getTokenList`

Get the token info list ordered by the amount of token transfers.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Token type: `"20"`, `"721"`, `"1155"` |
| `maxCount` | string | Hex-encoded max results, max `"0x3E8"` (1000) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Pagination key |
| `tokens[].ID` | integer | Token ID |
| `tokens[].Name` | string | Token name |
| `tokens[].TokenAddress` | string | Token contract address |

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getTokenList",
  "jsonrpc": "2.0",
  "params": [
    {
      "category": "20",
      "maxCount": "0x32"
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "pageKey": "ab000000-0000-0000-0000-00000000000s",
    "tokens": [
      {
        "ID": 21,
        "Name": "X00 Token",
        "TokenAddress": "0x2d5a9b83ecbdfeb0444629d1aaa4dc6e0c892fcd"
      },
      {
        "ID": 3,
        "Name": "X08 Token",
        "TokenAddress": "0xeab5c76def6a1654e3e21e6e8e8ab7f05c7911db"
      }
    ]
  }
}
```

---

### `nr_getSearchedTokenMeta`

Search for token metadata by token symbol. Returns all matching tokens.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `symbol` | string | Token symbol to search for (e.g. `"BUSD"`) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `tokenMetaInfos[].tokenAddress` | string | Token contract address |
| `tokenMetaInfos[].tokenName` | string | Token name |
| `tokenMetaInfos[].tokenSymbol` | string | Token symbol |
| `tokenMetaInfos[].tokenDecimal` | integer | Token decimals |
| `tokenMetaInfos[].tokenType` | string | Token type (e.g. `"ERC20"`) |

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getSearchedTokenMeta",
  "jsonrpc": "2.0",
  "params": ["BUSD"]
}
```

**Response (truncated):**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tokenMetaInfos": [
      {
        "tokenAddress": "0xe9e7cea3dedca5984780bafc599bd69add087d56",
        "tokenName": "BUSD Token",
        "tokenSymbol": "BUSD",
        "tokenDecimal": 18,
        "tokenType": "ERC20"
      }
    ]
  }
}
```

---

### `nr_getDailyCategoryCount`

Get daily chart data about transfers and block info by category.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `category` | string | Category: `"external"`, `"internal"`, `"20"`, `"721"`, `"1155"`, `"deposit"`, `"withdraw"` |
| `totalDay` | integer | Number of days to query (default: 10) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `updateTime` | integer | Last update timestamp |
| `transferDayCount[].timestamp` | integer | Day timestamp |
| `transferDayCount[].count` | integer | Transfer count |
| `transferDayCount[].block_count` | integer | Block count |
| `transferDayCount[].avg_block_time` | string | Average block time |
| `transferDayCount[].avg_block_size` | string | Average block size |

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getDailyCategoryCount",
  "jsonrpc": "2.0",
  "params": [
    {
      "category": "external",
      "totalDay": 10
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "updateTime": 1691744004,
    "transferDayCount": [
      {
        "timestamp": 1691712000,
        "count": 219279,
        "block_count": 31867,
        "avg_block_time": "1.00",
        "avg_block_size": "3349.96"
      },
      {
        "timestamp": 1691625600,
        "count": 423804,
        "block_count": 86400,
        "avg_block_time": "1.00",
        "avg_block_size": "2850.94"
      }
    ]
  }
}
```

---

### `nr_getTransferByTokenId`

Get transfer history for specific token IDs.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `tokenIds` | array | List of token IDs (hex strings) |
| `maxCount` | string | Hex-encoded max results to return |
| `address` | string | Token contract address |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `pageKey` | string | Pagination key |
| `transfers[].category` | string | Transfer type |
| `transfers[].blockNum` | string | Block number (hex) |
| `transfers[].from` | string | Sender address |
| `transfers[].to` | string | Recipient address |
| `transfers[].hash` | string | Transaction hash |

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getTransferByTokenId",
  "jsonrpc": "2.0",
  "params": [
    {
      "tokenIds": ["0x1"],
      "maxCount": "0x64",
      "address": "0x98387108842a7CfC7bA23E080030351f6ea68ac0"
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "pageKey": "qj000003-3Lik-wAf2-p4bo-22w4MiEpDutc",
    "transfers": [
      {
        "category": "1155",
        "blockNum": "0xac6052",
        "from": "0x0000000000000000000000000000000000000000",
        "to": "0x212e0955dda4b206adbe9d49e7c4c599c1d80f4a",
        "value": "0x0",
        "erc1155Metadata": [
          {
            "tokenId": "0x0000000000000000000000000000000000000000000000000000000000000001",
            "value": "0x00000000000000000000000000000000000000000000000000000000000003e8"
          }
        ],
        "asset": "MEC",
        "hash": "0xd2ae4794d3c5faab79c2e8dc0001f79f3f9be70a75bc2fe495f0401f21bb9151",
        "contractAddress": "0x98387108842a7cfc7ba23e080030351f6ea68ac0",
        "decimal": "0",
        "blockTimeStamp": 1632798913
      }
    ]
  }
}
```

---

### `nr_getTransferCountByTokenId`

Get the count of transfers for specific token IDs.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `tokenIds` | array | List of token IDs (hex strings) |
| `address` | string | Token contract address |

**Returns:** `result` -- Integer count of transfers.

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getTransferCountByTokenId",
  "jsonrpc": "2.0",
  "params": [
    {
      "tokenIds": ["0x1"],
      "address": "0x98387108842a7CfC7bA23E080030351f6ea68ac0"
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": 4644633
}
```

---

### `nr_getUniqueAccountCountByBlockRange`

Get the count of unique active accounts that interacted with specific addresses within a block range.

**Supported Chains:** opBNB (mainnet/testnet), Combo (mainnet/testnet).

**Parameters:** Single object parameter:

| Field | Type | Description |
|-------|------|-------------|
| `fromBlock` | string | Start block number (hex). Max range: 100,000 blocks |
| `toBlock` | string | End block number (hex) |
| `addresses` | array | List of addresses to filter by (max 20) |

**Returns:** `result` -- Hex-encoded count of unique accounts.

**Curl Example:**

```json
{
  "id": 1,
  "method": "nr_getUniqueAccountCountByBlockRange",
  "jsonrpc": "2.0",
  "params": [
    {
      "fromBlock": "0x98ca4b",
      "toBlock": "0x98ca4b",
      "addresses": [
        "0x4200000000000000000000000000000000000007",
        "0x4200000000000000000000000000000000000015",
        "0x4200000000000000000000000000000000000010"
      ]
    }
  ]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x4"
}
```

---

## BNBBurn API

### `nr_getBlockNumberByTimeStamp`

Map a Unix timestamp to the nearest block number.

**Supported Chains:** BSC mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `timestamp` | integer | Unix timestamp in seconds |
| 2 | `closest` | string | `"BEFORE"` or `"AFTER"` -- closest block to the timestamp |

**Returns:** `blockNumber` -- Hex-encoded block number.

**Curl Example:**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "nr_getBlockNumberByTimeStamp",
  "params": [1696118400, "AFTER"]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1eb754f"
}
```

---

### `nr_getDailyBlockCountAndReward`

Get the daily block count and block reward amounts for a date range.

**Supported Chains:** BSC mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `startDate` | string | Start date in `yyyy-mm-dd` format |
| 2 | `endDate` | string | End date in `yyyy-mm-dd` format |
| 3 | `sort` | string | `"asc"` or `"desc"` |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `totalCount` | string | Total number of days (hex) |
| `details[].UTCDate` | string | Date in `yyyy-mm-dd` format |
| `details[].unixTimeStamp` | integer | Unix timestamp |
| `details[].blockCount` | integer | Number of blocks validated that day |
| `details[].blockRewards` | string | Total block rewards (hex) |

**Curl Example:**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "nr_getDailyBlockCountAndReward",
  "params": ["2022-07-09", "2022-07-12", "asc"]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "totalCount": "0x4",
    "details": [
      {
        "UTCDate": "2022-07-09",
        "unixTimeStamp": 1657324800,
        "blockCount": 28787,
        "blockRewards": "0x0000000000000000000000000000000000000000000000875f54b2c6f6622ce5"
      },
      {
        "UTCDate": "2022-07-10",
        "unixTimeStamp": 1657411200,
        "blockCount": 28790,
        "blockRewards": "0x000000000000000000000000000000000000000000000083d182240fefb04caf"
      },
      {
        "UTCDate": "2022-07-11",
        "unixTimeStamp": 1657497600,
        "blockCount": 28793,
        "blockRewards": "0x00000000000000000000000000000000000000000000009e2cedaeca17e30068"
      },
      {
        "UTCDate": "2022-07-12",
        "unixTimeStamp": 1657584000,
        "blockCount": 28773,
        "blockRewards": "0x0000000000000000000000000000000000000000000000a1aed02e235d42789e"
      }
    ]
  }
}
```

---

### `nr_getDailyBlockReward`

Get daily block reward amounts distributed to validators.

**Supported Chains:** BSC mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `startDate` | string | Start date in `yyyy-mm-dd` format |
| 2 | `endDate` | string | End date in `yyyy-mm-dd` format |
| 3 | `sort` | string | `"asc"` or `"desc"` |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `totalCount` | string | Total number of days (hex) |
| `details[].UTCDate` | string | Date in `yyyy-mm-dd` format |
| `details[].unixTimeStamp` | integer | Unix timestamp |
| `details[].blockRewards` | string | Block rewards (hex) |

**Curl Example:**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "nr_getDailyBlockReward",
  "params": ["2022-07-09", "2022-07-12", "asc"]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "totalCount": "0x4",
    "details": [
      {
        "UTCDate": "2022-07-09",
        "unixTimeStamp": 1657324800,
        "blockRewards": "0x0000000000000000000000000000000000000000000000875f54b2c6f6622ce5"
      },
      {
        "UTCDate": "2022-07-10",
        "unixTimeStamp": 1657411200,
        "blockRewards": "0x000000000000000000000000000000000000000000000083d182240fefb04caf"
      },
      {
        "UTCDate": "2022-07-11",
        "unixTimeStamp": 1657497600,
        "blockRewards": "0x00000000000000000000000000000000000000000000009e2cedaeca17e30068"
      },
      {
        "UTCDate": "2022-07-12",
        "unixTimeStamp": 1657584000,
        "blockRewards": "0x0000000000000000000000000000000000000000000000a1aed02e235d42789e"
      }
    ]
  }
}
```

---

### `nr_getBlockReward`

Get the block reward for a specific block number.

**Supported Chains:** BSC mainnet only.

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `blockNumber` | integer | Block number (decimal integer) |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `blockNumber` | integer | Block number |
| `timestamp` | integer | Block timestamp |
| `miner` | string | Validator/miner address |
| `blockReward` | string | Block reward (hex) |
| `uncleInclusionReward` | string | Uncle inclusion reward (not used on BSC) |

**Curl Example:**

```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "method": "nr_getBlockReward",
  "params": [15778116]
}
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "blockNumber": 15778116,
    "timestamp": 1646435288,
    "miner": "0xea0a6e3c511bbd10f4519ece37dc24887e11b55d",
    "blockReward": "0x000000000000000000000000000000000000000000000000012df5841cabc5c5",
    "uncleInclusionReward": "0"
  }
}
```

---

## Historical Token Holder API

### `nr_historyTokenHolderSend`

Submit an async task to generate a historical token holder snapshot. After receiving the resource ID, call `nr_getHistoryTokenHolder` to retrieve results.

**Supported Chains:** BSC mainnet only.

**Supported Token Types:** Fungible tokens (ERC-20, BEP-20) and NFT (ERC-721, BEP-721, ERC-1155, BEP-1155).

> **Rate Limit:** Maximum 5 requests per minute due to high server resource consumption.

**API Endpoint:** `https://open-platform.nodereal.io/{API-KEY}/tokenholder/`

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | The token contract address |
| 2 | `blockNumber` | string | Block number in hex format |

**Returns:** `result` -- A resource ID string used to retrieve the results.

**Curl Example:**

```bash
curl https://open-platform.nodereal.io/{API-KEY}/tokenholder/ \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_historyTokenHolderSend","params":["0xeDa21B525Ac789EaB1a08ef2404dd8505FfB973D","0x1550e20"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "59d30c83562b9f9d1989ceb8ceaf4f6f7e749e8ffd1440d577fc0823169b0866"
}
```

---

### `nr_getHistoryTokenHolder`

Retrieve historical token holder list using the resource ID from `nr_historyTokenHolderSend`.

**Supported Chains:** BSC mainnet only.

**API Endpoint:** `https://open-platform.nodereal.io/{API-KEY}/tokenholder/`

**Parameters:**

| # | Name | Type | Description |
|---|------|------|-------------|
| 1 | `contractAddress` | string | Same contract address used in `nr_historyTokenHolderSend` |
| 2 | `blockNumber` | string | Same block number used in `nr_historyTokenHolderSend` |
| 3 | `resourceId` | string | Resource ID received from `nr_historyTokenHolderSend` |

**Returns:**

| Field | Type | Description |
|-------|------|-------------|
| `status` | integer | 0=Error, 1=Success, 2=Generating, 3=Incorrect resource ID |
| `links` | array | Download URLs for the token holder list JSON file |

> **Note:** Results are Base64 encoded. The download link expires after 24 hours.

**Curl Example:**

```bash
curl https://open-platform.nodereal.io/{API-KEY}/tokenholder/ \
-X POST \
-H "Content-Type: application/json" \
-d '{"jsonrpc":"2.0","method":"nr_getHistoryTokenHolder","params":["0xeDa21B525Ac789EaB1a08ef2404dd8505FfB973D","0x1550e20", "59d30c83562b9f9d1989ceb8ceaf4f6f7e749e8ffd1440d577fc0823169b0866"],"id": 1 }'
```

**Response:**

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": 1,
    "links": [
      "https://tf-nodereal-prod-bsc-gold-digger.s3.amazonaws.com/public/a4a4b76170ddc1w2d060717342826c31ca4307w8d3edfbb01593f5c48c78b7ab"
    ]
  }
}
```

**Downloaded File Format:**

```json
{
  "blockNumber": 22351392,
  "tokenAddress": "0x15b3d410fcd0d695e1bbe4f717f8e1b6d0fb2d0c",
  "holders": [
    {
      "account": "0x2f003ce63d5ebe72d9cb5afd94b00b14d75d47be",
      "balance": "0x0000000000000000000000000000000000000000000000000de0b6b3a7640000"
    },
    {
      "account": "0x68368ef36bb436f92b20d97b64fc080212821be5",
      "balance": "0x0000000000000000000000000000000000000000000000000000006c86d6dda0"
    }
  ]
}
```

---

## Supported Chains for Enhanced APIs

| Method | BSC | ETH | opBNB | Combo | Polygon |
|--------|-----|-----|-------|-------|---------|
| **Fungible Token APIs** (`nr_getTokenBalance20`, `nr_getTotalSupply20`, `nr_getTokenMeta`, `nr_getTokenHoldings`, `nr_getTokenHoldingCount`, `nr_getTokenCount`, `nr_getTokenHolders`, `nr_getTokenHolderCount`) | Yes | Yes | Yes | Yes | -- |
| **NFT APIs** (`nr_getNFTHoldings`, `nr_getNFTInventory`, `nr_getNFTHolders`, `nr_getNFTMeta`, `nr_getNFTTokens`, etc.) | Yes | Yes | Yes | Yes | -- |
| **Asset Transfer APIs** (`nr_getAssetTransfers`, `nr_getAssetTransfersCount`) | Yes | Yes | Yes | Yes | -- |
| **Transaction APIs** (`nr_getTransactionByAddress`, `nr_getTransactionDetail`, `nr_getContractCreationTransaction`) | Yes | Yes | Yes | Yes | -- |
| **Block Receipt APIs** (`nr_getTransactionReceiptsByBlockHash`, `nr_getTransactionReceiptsByBlockNumber`) | Yes | Yes | -- | -- | Yes |
| **BNBBurn APIs** (`nr_getBlockNumberByTimeStamp`, `nr_getDailyBlockCountAndReward`, `nr_getDailyBlockReward`, `nr_getBlockReward`) | Yes | -- | -- | -- | -- |
| **Historical Holder APIs** (`nr_historyTokenHolderSend`, `nr_getHistoryTokenHolder`) | Yes | -- | -- | -- | -- |
| **Platform APIs** (`nr_getAccountList`, `nr_getAccountListCount`, `nr_getTokenList`, `nr_getDailyCategoryCount`, `nr_getSearchedTokenMeta`, `nr_getTransferByTokenId`, `nr_getTransferCountByTokenId`, `nr_getUniqueAccountCountByBlockRange`) | -- | -- | Yes | Yes | -- |
| **Health Check** (`nr_health`) | Yes | Yes | -- | -- | -- |

---

## Pagination Patterns

Enhanced APIs use two pagination styles:

### Offset-based Pagination (older methods)
- `page` (hex): Page number starting at `"0x1"`
- `pageSize` (hex): Items per page, typically max `"0x64"` (100)
- Response includes `totalCount` to determine total pages

### Cursor-based Pagination (newer methods)
- `pageSize` (hex): Items per page, max `"0x64"` (100)
- `pageKey` (string): Empty string `""` for first page; use returned `pageKey` for subsequent pages
- More efficient for large datasets

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| Empty response or `totalCount` is 0 | No data found or wrong address format | Verify address is correct; try on a different chain |
| `totalCount` is 0 for NFT queries | Wrong token type parameter | Use `"ERC721"` or `"ERC1155"` (or `"erc721"`/`"erc1155"` for some methods) |
| Empty metadata from `nr_getNFTMeta` | Metadata not yet fetched from URI | Call the API again -- background thread fetches from token URI asynchronously |
| `method not found` for `nr_` methods | Enhanced APIs not available on this chain | Check Supported Chains table above |
| Large `nr_getAssetTransfers` response | Too many transactions in range | Use `fromBlock`/`toBlock` to narrow range; reduce `maxCount` |
| `nr_getTransactionByAddress` block range error | Range exceeds 1,000 blocks | Ensure `toBlock - fromBlock <= 1000` |
| `nr_getAssetTransfers` block range error | Range exceeds 100,000 blocks | Ensure `toBlock - fromBlock <= 100000` |
| `nr_historyTokenHolderSend` rate limited | More than 5 requests/minute | Wait and retry; this endpoint is rate-limited to 5 req/min |
| Historical holder file expired | Download link valid for 24 hours only | Submit a new task with `nr_historyTokenHolderSend` |

---

## Documentation

- **Enhanced API Reference:** https://docs.nodereal.io/reference/nr_gettokenbalance20
- **API Reference (all methods):** https://docs.nodereal.io/reference
- **LLM-Optimized Docs:** https://docs.nodereal.io/llms.txt
