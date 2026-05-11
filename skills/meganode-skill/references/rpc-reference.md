# MegaNode RPC API Reference

## Overview

MegaNode provides standard Ethereum-compatible JSON-RPC 2.0 endpoints over HTTPS and WSS for 25+ blockchain networks. All methods follow the standard JSON-RPC request/response format.

The standard RPC methods are available across **BNB Smart Chain (BSC)**, **opBNB**, **Ethereum**, and **Optimism** with identical interfaces. Each chain exposes the same JSON-RPC categories:

- **Account Information** -- `eth_accounts`, `eth_getBalance`, `eth_getCode`, `eth_getStorageAt`, `eth_getTransactionCount`
- **Chain & Network** -- `eth_chainId`, `eth_syncing`, `net_version`, `net_listening`, `net_peerCount`, `web3_clientVersion`, `web3_sha3`
- **Gas & Fees** -- `eth_gasPrice`, `eth_estimateGas`, `eth_maxPriorityFeePerGas`, `eth_feeHistory`, `eth_baseFee`
- **Blocks** -- `eth_blockNumber`, `eth_getBlockByHash`, `eth_getBlockByNumber`, `eth_getBlockReceipts`, `eth_getBlockTransactionCountByHash`, `eth_getBlockTransactionCountByNumber`
- **Event Logs & Filters** -- `eth_getLogs`, `eth_newFilter`, `eth_newBlockFilter`, `eth_newPendingTransactionFilter`, `eth_getFilterChanges`, `eth_getFilterLogs`, `eth_uninstallFilter`
- **EVM Execution** -- `eth_call`, `eth_sendRawTransaction`
- **Transactions** -- `eth_getTransactionByHash`, `eth_getTransactionByBlockHashAndIndex`, `eth_getTransactionByBlockNumberAndIndex`, `eth_getTransactionReceipt`
- **Uncle Blocks** -- `eth_getUncleByBlockHashAndIndex`, `eth_getUncleByBlockNumberAndIndex`, `eth_getUncleCountByBlockHash`, `eth_getUncleCountByBlockNumber`
- **WebSockets** -- `eth_subscribe` (newHeads, logs, newPendingTransactions, syncing), `eth_unsubscribe`

## Table of Contents

1. [Overview](#overview) -- API summary and scope
2. [Endpoint Format](#endpoint-format) -- URL patterns per chain
3. [Request Format](#request-format) -- JSON-RPC request structure
4. [Block Tags](#block-tags) -- Supported block parameter values
5. [Account Methods](#account-methods) -- Balance, nonce, and code queries
6. [Block Methods](#block-methods) -- Block data retrieval methods
7. [Transaction Methods](#transaction-methods) -- Transaction lookup and receipts
8. [EVM Execution Methods](#evm-execution-methods) -- Call and send transactions
9. [Gas & Fee Methods](#gas--fee-methods) -- Gas price and fee estimation
10. [Chain & Network Methods](#chain--network-methods) -- Chain ID and network status
11. [Filter Methods](#filter-methods) -- Event log filtering and polling
12. [Uncle Block Methods](#uncle-block-methods) -- Uncle block data queries
13. [WebSocket Methods](#websocket-methods) -- Real-time event subscriptions
14. [Batch Requests](#batch-requests) -- Multiple calls in one request
15. [Quick Reference Table](#quick-reference-table) -- Method summary at a glance
16. [Error Codes](#error-codes) -- Standard JSON-RPC error codes
17. [Code Examples](#code-examples) -- Language-specific usage samples
18. [Troubleshooting](#troubleshooting) -- Common issues and solutions
19. [Documentation](#documentation) -- Links to official docs

## Endpoint Format

```
HTTPS (BSC):       https://bsc-mainnet.nodereal.io/v1/{apiKey}
HTTPS (BSC test):  https://bsc-testnet.nodereal.io/v1/{apiKey}
HTTPS (opBNB):     https://opbnb-mainnet.nodereal.io/v1/{apiKey}
HTTPS (opBNB test):https://opbnb-testnet.nodereal.io/v1/{apiKey}
HTTPS (ETH):       https://eth-mainnet.nodereal.io/v1/{apiKey}
HTTPS (Optimism):  https://opt-mainnet.nodereal.io/v1/{apiKey}
WSS (BSC):         wss://bsc-mainnet.nodereal.io/ws/v1/{apiKey}
WSS (opBNB):       wss://opbnb-mainnet.nodereal.io/ws/v1/{apiKey}
```

## Request Format

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "method_name",
  "params": [...]
}
```

## Block Tags

Many methods accept a block tag parameter. Supported values:

- `"latest"` -- The most recent block in the canonical chain observed by the client. May be re-orged under normal conditions.
- `"earliest"` -- The lowest numbered block the client has available (genesis block).
- `"pending"` -- A sample next block built by the client on top of latest, containing transactions from the local mempool.
- `"safe"` -- The most recent crypto-economically secure block. Cannot be re-orged outside of manual intervention. **Ethereum Mainnet and Goerli only.**
- `"finalized"` -- The most recent block accepted by >2/3 of validators. Very unlikely to be re-orged. **Ethereum Mainnet and Goerli only.**
- Hex block number (e.g., `"0xc5043f"`)

---

## Account Methods

### eth_accounts

Returns a list of addresses owned by client.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** Array of 20-byte addresses owned by the client.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_accounts","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": []
}
```

---

### eth_getBalance

Returns the balance of the account of a given address.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 20 Bytes -- Address to check balance of |
| 2 | `string` | Block number (hex) or block tag (`latest`, `earliest`, `pending`, `safe`, `finalized`) |

**Returns:** Hex value of the current balance in wei.

**curl Example (BSC):**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x407d73d8a49eeb85d32cf465507dd71d507100c1","latest"],"id":1}'
```

**curl Example (ETH):**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBalance","params":["0x407d73d8a49eeb85d32cf465507dd71d507100c1","latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0234c8a3397aab58"
}
```

---

### eth_getCode

Returns code at a given address.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 20 Bytes -- Address |
| 2 | `string` | Block number (hex) or block tag |

**Returns:** The code from the given address.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getCode","params":["0xa94f5374fce5edbc8e2a8697c15331677e6ebf0b","0x2"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x600160008035811a818181146012578301005b601b6001356025565b8060005260206000f25b600060078202905091905056"
}
```

---

### eth_getStorageAt

Returns the value from a storage position at a given address. Returns the state of the contract's storage, which may not be exposed via the contract's methods.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 20 Bytes -- Address of the storage |
| 2 | `string` | Integer of the slot position in the storage (in hex) |
| 3 | `string` | Block number (hex) or block tag |

**Returns:** The value at this storage position.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getStorageAt","params":["0x295a70b2de5e3953354a6a8344e616ed314d7251","0x0","latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000000000000000000000000000"
}
```

---

### eth_getTransactionCount

Returns the number of transactions sent from an address.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 20 Bytes -- Address |
| 2 | `string` | Block number (hex) or block tag |

**Returns:** Integer of the number of transactions sent from this address (hex).

**curl Example:**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionCount","params":["0x407d73d8a49eeb85d32cf465507dd71d507100c1","latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

---

## Block Methods

### eth_blockNumber

Returns the number of the most recent block.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** Integer of the current block number the client is on (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x12eed11"
}
```

---

### eth_getBlockByNumber

Returns information about a block by block number.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block number (hex) or block tag |
| 2 | `boolean` | If `true` returns full transaction objects, if `false` only the hashes. Defaults to `false`. |

**Returns:** A block object, or `null` when no block was found. Fields include: `number`, `hash`, `parentHash`, `nonce`, `sha3Uncles`, `logsBloom`, `transactionsRoot`, `stateRoot`, `receiptsRoot`, `miner`, `difficulty`, `totalDifficulty`, `extraData`, `size`, `gasLimit`, `gasUsed`, `timestamp`, `transactions`, `uncles`.

**curl Example (BSC):**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["0xc5043f",false],"id":1}'
```

**curl Example (ETH):**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockByNumber","params":["finalized",false],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "number": "0xc5043f",
    "hash": "0x8f9ecad637559914862de6821bd352d6ac7744d130085d4c5b3d821786aab3ac",
    "parentHash": "0xf1b5d6a7a45df869b2eef85541584c69bbeb7a58f77e557d4898de2b464d5715",
    "nonce": "0x0000000000000000",
    "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
    "logsBloom": "0x00080000...",
    "transactionsRoot": "0xc4b4888ec249430e95f700432d21a3042e5dd2572e68771dc61f73e1fbbd9900",
    "stateRoot": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "receiptsRoot": "0x17f8ad0067aff1dbb35d5100b1f131838564b3e980e2b8a2674b8d5362d12e97",
    "miner": "0x0000000000000000000000000000000000000000",
    "difficulty": "0x0",
    "totalDifficulty": "0x0",
    "extraData": "0x",
    "size": "0x367",
    "gasLimit": "0xbc87657",
    "gasUsed": "0x3daa0",
    "timestamp": "0x628dde24",
    "transactions": ["0x39229c9c973b7675086e4404c30fd23b4130bdb33cef8f799ac0450e2489ba08"],
    "uncles": []
  }
}
```

---

### eth_getBlockByHash

Returns information about a block by block hash.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a block |
| 2 | `boolean` | If `true` returns full transaction objects, if `false` only the hashes. Defaults to `false`. |

**Returns:** A block object (same structure as `eth_getBlockByNumber`), or `null` when no block was found.

**curl Example:**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockByHash","params":["0x8f9ecad637559914862de6821bd352d6ac7744d130085d4c5b3d821786aab3ac",false],"id":1}'
```

**Response:** Same block object structure as `eth_getBlockByNumber`.

---

### eth_getBlockReceipts

Get all transaction receipts for a given block.

**Supported Chains:** BNB Smart Chain, opBNB

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block hash, block number (hex), or block tag |

**Returns:** Array of transaction receipt objects for all transactions in the block. Each receipt contains: `blockHash`, `blockNumber`, `transactionIndex`, `transactionHash`, `from`, `to`, `cumulativeGasUsed`, `gasUsed`, `contractAddress`, `logs`, `logsBloom`, `status`, `effectiveGasPrice`, `type`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockReceipts","params":["latest"],"id":1}'
```

---

### eth_getBlockTransactionCountByHash

Returns the number of transactions in a block matching the given block hash.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a block |

**Returns:** Integer of the number of transactions in this block (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByHash","params":["0x8f9ecad637559914862de6821bd352d6ac7744d130085d4c5b3d821786aab3ac"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

---

### eth_getBlockTransactionCountByNumber

Returns the number of transactions in a block matching the given block number.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block number (hex) or block tag |

**Returns:** Integer of the number of transactions in this block (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getBlockTransactionCountByNumber","params":["latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0xb0"
}
```

---

## Transaction Methods

### eth_getTransactionByHash

Returns the information about a transaction requested by transaction hash. In the response object, `blockHash`, `blockNumber`, and `transactionIndex` are `null` when the transaction is pending.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a transaction |

**Returns:** A transaction object, or `null` when no transaction was found. Fields include: `blockHash`, `blockNumber`, `transactionIndex`, `hash`, `nonce`, `from`, `to`, `gas`, `gasPrice`, `input`, `value`, `v`, `r`, `s`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionByHash","params":["0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "blockHash": "0x1d59ff54b1eb26b013ce3cb5fc9dab3705b415a67127a003c3e61eb445bb8df2",
    "blockNumber": "0x5daf3b",
    "transactionIndex": "0x41",
    "hash": "0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b",
    "nonce": "0x15",
    "from": "0xa7d9ddbe1f17865597fbd27ec712455208b6b76d",
    "to": "0xf02c1c8e6114b1dbe8937a39260b5b0a374432bb",
    "gas": "0xc350",
    "gasPrice": "0x4a817c800",
    "input": "0x68656c6c6f21",
    "value": "0xf3dbb76162000",
    "v": "0x25",
    "r": "0x1b5e176d927f8e9ab405058b2d2457392da3e20f328b16ddabcebc33eaac5fea",
    "s": "0x4ba69724e8f69de52f0125ad8b3c5c2cef33019bac3249e2c0a2192766d1721c"
  }
}
```

---

### eth_getTransactionByBlockHashAndIndex

Returns information about a transaction by block hash and transaction index position.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a block |
| 2 | `string` | Integer of the transaction index position (in hex) |

**Returns:** A transaction object, or `null`. Same structure as `eth_getTransactionByHash`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockHashAndIndex","params":["0x1d59ff54b1eb26b013ce3cb5fc9dab3705b415a67127a003c3e61eb445bb8df2","0x0"],"id":1}'
```

---

### eth_getTransactionByBlockNumberAndIndex

Returns information about a transaction by block number and transaction index position.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block number (hex) or block tag |
| 2 | `string` | The transaction index position (in hex) |

**Returns:** A transaction object, or `null`. Same structure as `eth_getTransactionByHash`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionByBlockNumberAndIndex","params":["latest","0x0"],"id":1}'
```

---

### eth_getTransactionReceipt

Returns the receipt of a transaction by transaction hash.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a transaction |

**Returns:** A transaction receipt object, or `null`. Fields include: `blockHash`, `blockNumber`, `transactionIndex`, `transactionHash`, `from`, `to`, `cumulativeGasUsed`, `gasUsed`, `contractAddress` (null unless contract creation), `logs` (array of log objects), `logsBloom`, `root` (pre-Byzantium), `status` (1 for success, 0 for failure), `effectiveGasPrice`, `type`.

Each log object contains: `blockHash`, `blockNumber`, `transactionIndex`, `address`, `logIndex`, `data`, `removed`, `topics`, `transactionHash`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getTransactionReceipt","params":["0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "blockHash": "0x1d59ff54b1eb26b013ce3cb5fc9dab3705b415a67127a003c3e61eb445bb8df2",
    "blockNumber": "0x5daf3b",
    "transactionIndex": "0x41",
    "transactionHash": "0x88df016429689c079f3b2f6ad39fa052532c56795b733da78a91ebe6a713944b",
    "from": "0xa7d9ddbe1f17865597fbd27ec712455208b6b76d",
    "to": "0xf02c1c8e6114b1dbe8937a39260b5b0a374432bb",
    "cumulativeGasUsed": "0x33bc",
    "gasUsed": "0x4dc",
    "contractAddress": null,
    "logs": [],
    "logsBloom": "0x00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000",
    "status": "0x1",
    "effectiveGasPrice": "0x4a817c800",
    "type": "0x0"
  }
}
```

---

### eth_sendRawTransaction

Creates a new message call transaction or a contract creation for signed transactions.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | The signed transaction data |

**Returns:** 32 Bytes -- the transaction hash, or the zero hash if the transaction is not yet available.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_sendRawTransaction","params":["0xf86c0a8502540be400825208944bbeeb066ed09b7aed07bf39eee0460dfa261520880de0b6b3a7640000801ca0f3ae52c1ef3300f44df0bcfd1341c232ed2e3dd736c21b2e24c993b1b4482611a055b17a4dff0d4948adf0bd3c2d283112cc97a1e2ac2c3a16c21cf6c64e9f1b4d"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0xe670ec64341771606e55d6b4ca35a1a6b75ee3d5145a99d05921026d1527331"
}
```

---

## EVM Execution Methods

### eth_call

Executes a new message call immediately without creating a transaction on the blockchain.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `object` | Transaction call object (see fields below) |
| 2 | `string` | Block number (hex) or block tag |

**Transaction call object fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `from` | `string` | No | 20 Bytes -- The address the transaction is sent from |
| `to` | `string` | **Yes** | 20 Bytes -- The address the transaction is directed to |
| `gas` | `string` | No | Integer of the gas provided for the transaction execution |
| `gasPrice` | `string` | No | Integer of the gasPrice used for each paid gas |
| `value` | `string` | No | Integer of the value sent with this transaction |
| `data` | `string` | No | Hash of the method signature and encoded parameters |

**Returns:** The return value of the executed contract method.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_call","params":[{"to":"0xd46e8dd67c5d32be8058bb8eb970870f07244567","data":"0x70a08231000000000000000000000000407d73d8a49eeb85d32cf465507dd71d507100c1"},"latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0000000000000000000000000000000000000000000000000000000000000000"
}
```

---

### eth_estimateGas

Generates and returns an estimate of how much gas is necessary to allow the transaction to complete. The transaction will not be added to the blockchain.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `object` | Transaction call object (same fields as `eth_call`) |
| 2 | `string` | Block number (hex) or block tag |

**Returns:** The amount of gas used (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_estimateGas","params":[{"to":"0xd46e8dd67c5d32be8058bb8eb970870f07244567","data":"0x70a08231000000000000000000000000407d73d8a49eeb85d32cf465507dd71d507100c1"},"latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x5208"
}
```

---

## Gas & Fee Methods

### eth_gasPrice

Returns the current price per gas in wei.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** Integer of the current gas price in wei (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_gasPrice","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x3b9aca00"
}
```

---

### eth_maxPriorityFeePerGas

Get the priority fee needed to be included in a block.

**Supported Chains:** Ethereum, Optimism, Avalanche C-Chain

**Parameters:** none

**Returns:** Hex value of the priority fee needed to be included in a block.

**curl Example (Avalanche):**
```bash
curl https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/rpc \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_maxPriorityFeePerGas","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x2540be400"
}
```

---

### eth_baseFee

Get the base fee for the next block.

**Supported Chains:** Avalanche C-Chain

**Parameters:** none

**Returns:** Hex value of the base fee for the next block.

**curl Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/rpc \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_baseFee","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x34630b8a00"
}
```

---

### eth_feeHistory

Returns fee history data for the requested block range.

**Supported Chains:** Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Number of blocks in the requested range (hex) |
| 2 | `string` | Highest block of the requested range (block number or block tag) |
| 3 | `array` | Array of percentile values to sample from each block's effective priority fees |

**Returns:** Object containing `oldestBlock`, `baseFeePerGas`, `gasUsedRatio`, and optionally `reward`.

**curl Example:**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_feeHistory","params":["0x4","latest",[25,75]],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "oldestBlock": "0xfab8ac",
    "baseFeePerGas": ["0x602f1cb8b", "0x5e20e5c87", "0x5d770c483", "0x5edb4f2ea", "0x5f12be98e"],
    "gasUsedRatio": [0.3621, 0.4583, 0.5523, 0.4927],
    "reward": [["0x59682f00", "0x59682f00"], ["0x59682f00", "0x59682f00"], ["0x3b9aca00", "0x59682f00"], ["0x59682f00", "0x59682f00"]]
  }
}
```

---

## Chain & Network Methods

### eth_chainId

Returns the chain ID. The chain ID returned should always correspond to the information in the current known head block, ensuring callers can use the retrieved information to sign transactions.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** Integer of the current chain ID (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x38"
}
```

---

### eth_syncing

Returns an object with data about the sync status or `false` when not syncing.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** An object with sync status data or `false` when not syncing. When syncing, returns: `startingBlock` (the block at which the import started), `currentBlock` (same as eth_blockNumber), `highestBlock` (the estimated highest block).

**curl Example:**
```bash
curl https://opt-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_syncing","params":[],"id":1}'
```

**Response (not syncing):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": false
}
```

**Response (syncing):**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "startingBlock": "0x384",
    "currentBlock": "0x386",
    "highestBlock": "0x454"
  }
}
```

---

### net_version

Returns the current network ID.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** String of the current network ID. Common values: `1` (Ethereum Mainnet), `56` (BSC Mainnet), `97` (BSC Testnet), `10` (Optimism).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"net_version","params":[],"id":67}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 67,
  "result": "56"
}
```

---

### net_listening

Returns `true` if client is actively listening for network connections.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** Boolean -- `true` when listening, otherwise `false`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"net_listening","params":[],"id":67}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 67,
  "result": true
}
```

---

### net_peerCount

Returns number of peers currently connected to the client.

**Supported Chains:** Avalanche C-Chain

**Parameters:** none

**Returns:** Integer of the number of connected peers (hex).

**curl Example:**
```bash
curl https://open-platform.nodereal.io/{apiKey}/avalanche-c/ext/bc/C/rpc \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"net_peerCount","params":[],"id":67}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 67,
  "result": "0x2"
}
```

---

### web3_clientVersion

Returns the current client version.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** String of the current client version.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"web3_clientVersion","params":[],"id":67}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 67,
  "result": "Geth/v1.1.12-omnibus-dda4e30c/linux-amd64/go1.18.5"
}
```

---

### web3_sha3

Returns Keccak-256 (not the standardized SHA3-256) of the given data.

**Supported Chains:** Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | The data in hex form to convert into a SHA3 hash (must match pattern `^0[xX][0-9a-fA-F]+$`) |

**Returns:** The SHA3 result of the given string.

**curl Example:**
```bash
curl https://opt-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"web3_sha3","params":["0x68656c6c6f20776f726c64"],"id":64}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 64,
  "result": "0x47173285a8d7341e5e972fc677286384f802f8ef42a5ec5f03bbfa254cb01fad"
}
```

---

## Filter Methods

### eth_newFilter

Creates a filter object, based on filter options, to notify when the state changes (logs).

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `object` | Filter object (see fields below) |

**Filter object fields:**

| Field | Type | Description |
|-------|------|-------------|
| `fromBlock` | `string` | Block number (hex) or block tag. Default: `"latest"`. |
| `toBlock` | `string` | Block number (hex) or block tag. Default: `"latest"`. |
| `address` | `string\|array` | Contract address or list of addresses from which logs should originate |
| `topics` | `array` | Array of 32 Bytes DATA topics. Topics are order-dependent. Each topic can also be an array of DATA with "or" options. |
| `blockHash` | `string` | Equivalent to fromBlock = toBlock = the block with hash blockHash. If present, neither fromBlock nor toBlock are allowed. |

**Returns:** A filter ID.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_newFilter","params":[{"fromBlock":"0x1","toBlock":"0x2","address":"0x8888f1f195afa192cfee860698584c030f4c9db1","topics":["0x000000000000000000000000a94f5374fce5edbc8e2a8697c15331677e6ebf0b"]}],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

---

### eth_newBlockFilter

Creates a filter in the node, to notify when a new block arrives.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** A filter ID.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_newBlockFilter","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

---

### eth_newPendingTransactionFilter

Creates a filter in the node, to notify when new pending transactions arrive. To check if the state has changed, call `eth_getFilterChanges`.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:** none

**Returns:** A filter ID.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_newPendingTransactionFilter","params":[],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x1"
}
```

---

### eth_getFilterChanges

Polling method for a filter, which returns an array of logs which occurred since last poll.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | The filter ID |

**Returns:** Array of log objects, or an empty array if nothing has changed since last poll. Each log object contains: `blockHash`, `blockNumber`, `transactionIndex`, `address`, `logIndex`, `data`, `removed`, `topics`, `transactionHash`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getFilterChanges","params":["0x1"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": []
}
```

---

### eth_getFilterLogs

Returns an array of all logs matching filter with given ID. Can compute the same results with an `eth_getLogs` call.

> **Block range limitation:**
> - Block range > 50K: Not available
> - Block range <= 100: No response size limit
> - Block range between 100 and 50K: Maximum 50K records will be responded

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | The filter ID |

**Returns:** Array of log objects, or an empty array. Same log structure as `eth_getFilterChanges`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getFilterLogs","params":["0x1"],"id":1}'
```

---

### eth_getLogs

Returns an array of all logs matching a given filter object.

> **Block range limitation:**
> - Block range > 50K: Not available
> - Block range <= 100: No response size limit
> - Block range between 100 and 50K: Maximum 50K records will be responded

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `object` | Filter object (same fields as `eth_newFilter`) |

**Returns:** Array of log objects, or an empty array. Each log object contains: `blockHash`, `blockNumber`, `transactionIndex`, `address`, `logIndex`, `data`, `removed`, `topics`, `transactionHash`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getLogs","params":[{"fromBlock":"0x1a2b3c","toBlock":"0x1a2b3d","address":["0x8888f1f195afa192cfee860698584c030f4c9db1"],"topics":["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]}],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": [
    {
      "blockHash": "0x61cdb2a09ab99abf791d474f20c2ea89bf8de2923a2d42bb49944c8c993cbf04",
      "blockNumber": "0x29387",
      "transactionIndex": "0x0",
      "address": "0x8888f1f195afa192cfee860698584c030f4c9db1",
      "logIndex": "0x0",
      "data": "0x00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003",
      "removed": false,
      "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"],
      "transactionHash": "0xe044554a0a55067caafd07f8020ab9f2af60bdfe337e395ecd84b4877a3d1ab4"
    }
  ]
}
```

---

### eth_uninstallFilter

Uninstalls a filter with given ID. Should always be called when watch is no longer needed. Filters timeout when they are not requested with `eth_getFilterChanges` for a period of time.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | The filter ID |

**Returns:** `true` if the filter was successfully uninstalled, otherwise `false`.

**curl Example:**
```bash
curl https://eth-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_uninstallFilter","params":["0x1"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

---

## Uncle Block Methods

### eth_getUncleByBlockHashAndIndex

Returns information about an uncle of a block by hash and uncle index position.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a block |
| 2 | `string` | The uncle's index position (in hex) |

**Returns:** A block object (same structure as `eth_getBlockByHash`), or `null`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getUncleByBlockHashAndIndex","params":["0x1d59ff54b1eb26b013ce3cb5fc9dab3705b415a67127a003c3e61eb445bb8df2","0x0"],"id":1}'
```

---

### eth_getUncleByBlockNumberAndIndex

Returns information about an uncle of a block by number and uncle index position.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block number (hex) or block tag |
| 2 | `string` | The uncle's index position (in hex) |

**Returns:** A block object, or `null`.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getUncleByBlockNumberAndIndex","params":["0x29c","0x0"],"id":1}'
```

---

### eth_getUncleCountByBlockHash

Returns the number of uncles in a block matching the given block hash.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | 32 Bytes -- Hash of a block |

**Returns:** Integer of the number of uncles in this block (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getUncleCountByBlockHash","params":["0x1d59ff54b1eb26b013ce3cb5fc9dab3705b415a67127a003c3e61eb445bb8df2"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0"
}
```

---

### eth_getUncleCountByBlockNumber

Returns the number of uncles in a block matching the given block number.

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Block number (hex) or block tag |

**Returns:** Integer of the number of uncles in this block (hex).

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"eth_getUncleCountByBlockNumber","params":["latest"],"id":1}'
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0x0"
}
```

---

## WebSocket Methods

### eth_subscribe

Creates a subscription for real-time events. **WebSocket connections only.**

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Endpoint Format:**
```
wss://bsc-mainnet.nodereal.io/ws/v1/{apiKey}
wss://opbnb-mainnet.nodereal.io/ws/v1/{apiKey}
```

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Subscription type: `newHeads`, `logs`, `newPendingTransactions`, `syncing` |
| 2 | `object` | (Optional, for `logs` only) Filter object with `address` and `topics` |

**Returns:** Subscription ID for the newly created subscription.

**Subscription Types:**
- `newHeads` -- Receive a notification each time a new header is appended to the chain
- `logs` -- Returns logs that are included in new imported blocks and match the given filter criteria
  - `address` (optional) -- An address or array of addresses
  - `topics` (optional) -- Only logs which match the specified topics
- `newPendingTransactions` -- Returns the hash for all transactions added to the pending state
- `syncing` -- Indicates when the node starts or stops synchronizing

**Request Examples:**
```bash
$ wscat -c wss://bsc-mainnet.nodereal.io/ws/v1/{apiKey}

# newHeads
> {"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["newHeads"]}

# logs with filter
> {"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["logs",{"address":"0x8320fe7702b96890f7bbc0d4a888ed1468216cfd","topics":["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]}]}

# newPendingTransactions
> {"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["newPendingTransactions"]}

# syncing
> {"jsonrpc":"2.0","id":1,"method":"eth_subscribe","params":["syncing"]}
```

**Response (newHeads notification):**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "result": {
      "difficulty": "0x15d9243a23aa",
      "extraData": "0xd983010305544765746887676f312e342e328777696e646f7773",
      "gasLimit": "0x44e7c4",
      "gasUsed": "0x38358",
      "logsBloom": "0x00000000...",
      "miner": "0xf8b483dba2c3b7176a3da541ad41a48bb3121069",
      "nonce": "0x084149928194cc5f",
      "number": "0x1348c9",
      "parentHash": "0x7736fab72105dc611604d22470dadad26f56fe494421b5b333de816ce1f25701",
      "receiptRoot": "0x2fab35823ad00c7bc328595cb46652fe7886e00660a01e867824d3dceb1c8d36",
      "sha3Uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
      "stateRoot": "0xb3346685172db67de23fd8765c43c31009d0eb3bd9c501c9be3229203f15f378",
      "timestamp": "0x56ffeff8",
      "transactionsRoot": "0x0167ffa60e3ebc0b1db7db95f7c0087dd6c0e61413140e39d94d3468d7c9689f"
    },
    "subscription": "0x9ce59a13059e237087c02d3236a0b1cc"
  }
}
```

**Response (logs notification):**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0x4a8a4c0517236924f9838102c5a4dcb7",
    "result": {
      "address": "0x8320fe7702b96890f7bbc0d4a888ed1468216cfd",
      "blockHash": "0x61cdb2a09ab99abf791d474f20c2ea89bf8de2923a2d42bb49944c8c993cbf04",
      "blockNumber": "0x29387",
      "data": "0x00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000003",
      "logIndex": "0x0",
      "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"],
      "transactionHash": "0xe044554a0a55067caafd07f8020ab9f2af60bdfe337e395ecd84b4877a3d1ab4",
      "transactionIndex": "0x0"
    }
  }
}
```

**Response (newPendingTransactions notification):**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0xc3b33aa549fe9a60e95d21862596617c",
    "result": "0xd6fdc5cc41a9959e922cb772a9aef46f4daea279307bc5f7024edc4ccd7fa"
  }
}
```

**Response (syncing notification):**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0xe2ffeb2703bcf602d44522385829ce96",
    "result": {
      "syncing": true,
      "status": {
        "startingBlock": 674427,
        "currentBlock": 67400,
        "highestBlock": 674432,
        "pulledStates": 0,
        "knownStates": 0
      }
    }
  }
}
```

---

### eth_unsubscribe

Cancels a subscription. **WebSocket connections only.**

**Supported Chains:** BNB Smart Chain, opBNB, Ethereum, Optimism

**Endpoint Format:**
```
wss://bsc-mainnet.nodereal.io/ws/v1/{apiKey}
wss://opbnb-mainnet.nodereal.io/ws/v1/{apiKey}
```

**Parameters:**

| # | Type | Description |
|---|------|-------------|
| 1 | `string` | Subscription ID |

**Returns:** `true` if the subscription was successfully cancelled.

**Request Example:**
```bash
$ wscat -c wss://bsc-mainnet.nodereal.io/ws/v1/{apiKey}
> {"jsonrpc":"2.0","id":1,"method":"eth_unsubscribe","params":["0x9cef478923ff08bf67fde6c64013158d"]}
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": true
}
```

---

## Batch Requests

All MegaNode users can send batch requests containing up to **500 requests** in a single HTTP call. Debug API requests cannot be included in batch requests.

The cost of batch requests is the sum of CUs for all individual API calls within it.

**curl Example:**
```bash
curl https://bsc-mainnet.nodereal.io/v1/{apiKey} \
  -X POST \
  -H "Content-Type: application/json" \
  -d '[{"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]},
       {"jsonrpc":"2.0","id":2,"method":"eth_blockNumber","params":[]},
       {"jsonrpc":"2.0","id":3,"method":"eth_blockNumber","params":[]},
       {"jsonrpc":"2.0","id":4,"method":"eth_blockNumber","params":[]}]'
```

**Response:**
```json
[
  {"jsonrpc":"2.0","id":1,"result":"0x12eed11"},
  {"jsonrpc":"2.0","id":2,"result":"0x12eed11"},
  {"jsonrpc":"2.0","id":3,"result":"0x12eed11"},
  {"jsonrpc":"2.0","id":4,"result":"0x12eed11"}
]
```

**WSS Batch Example (Arbitrum Nitro, Arbitrum Nova, Avalanche C-Chain only):**
```bash
$ wscat -c wss://open-platform.nodereal.io/ws/{apiKey}/arbitrum-nitro/
> [{"method":"eth_getBlockByNumber","params":["0xc5043f",false],"id":1,"jsonrpc":"2.0"},{"method":"eth_chainId","params":[],"id":2,"jsonrpc":"2.0"}]
```

---

## Quick Reference Table

### Account Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_accounts` | none | Returns list of addresses owned by client |
| `eth_getBalance` | `[address, blockTag]` | Returns balance of the account in wei |
| `eth_getCode` | `[address, blockTag]` | Returns code at a given address |
| `eth_getStorageAt` | `[address, position, blockTag]` | Returns value from storage position |
| `eth_getTransactionCount` | `[address, blockTag]` | Returns number of transactions sent |

### Block Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_blockNumber` | none | Returns latest block number |
| `eth_getBlockByHash` | `[hash, fullTx]` | Returns block by hash |
| `eth_getBlockByNumber` | `[blockTag, fullTx]` | Returns block by number |
| `eth_getBlockReceipts` | `[blockTag]` | Returns all receipts in block (BSC/opBNB) |
| `eth_getBlockTransactionCountByHash` | `[hash]` | Returns tx count in block by hash |
| `eth_getBlockTransactionCountByNumber` | `[blockTag]` | Returns tx count in block by number |

### Transaction Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_getTransactionByHash` | `[hash]` | Returns transaction by hash |
| `eth_getTransactionByBlockHashAndIndex` | `[blockHash, index]` | Returns tx by block hash and index |
| `eth_getTransactionByBlockNumberAndIndex` | `[blockTag, index]` | Returns tx by block number and index |
| `eth_getTransactionReceipt` | `[hash]` | Returns transaction receipt |
| `eth_sendRawTransaction` | `[signedTxData]` | Submits a signed transaction |

### Call & Estimate Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_call` | `[txObject, blockTag]` | Executes a read-only call |
| `eth_estimateGas` | `[txObject, blockTag]` | Estimates gas needed for transaction |

### Gas & Fee Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_gasPrice` | none | Returns current gas price in wei |
| `eth_maxPriorityFeePerGas` | none | Returns max priority fee suggestion |
| `eth_baseFee` | none | Returns base fee for next block (Avalanche) |
| `eth_feeHistory` | `[blockCount, newestBlock, rewardPercentiles]` | Returns fee history data |

### Filter Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_newFilter` | `[filterObject]` | Creates a new log filter |
| `eth_newBlockFilter` | none | Creates a new block filter |
| `eth_newPendingTransactionFilter` | none | Creates pending tx filter |
| `eth_getFilterChanges` | `[filterId]` | Returns filter changes since last poll |
| `eth_getFilterLogs` | `[filterId]` | Returns all logs matching filter |
| `eth_getLogs` | `[filterObject]` | Returns logs matching filter criteria |
| `eth_uninstallFilter` | `[filterId]` | Removes a filter |

### Chain & Network Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_chainId` | none | Returns chain ID |
| `eth_syncing` | none | Returns sync status or false |
| `net_version` | none | Returns network ID |
| `net_listening` | none | Returns true if listening |
| `net_peerCount` | none | Returns number of peers (Avalanche) |
| `web3_clientVersion` | none | Returns client version |
| `web3_sha3` | `[data]` | Returns Keccak-256 hash |

### Uncle Block Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_getUncleByBlockHashAndIndex` | `[hash, index]` | Returns uncle by block hash and index |
| `eth_getUncleByBlockNumberAndIndex` | `[blockTag, index]` | Returns uncle by block number and index |
| `eth_getUncleCountByBlockHash` | `[hash]` | Returns uncle count in block by hash |
| `eth_getUncleCountByBlockNumber` | `[blockTag]` | Returns uncle count in block by number |

### WebSocket Methods

| Method | Parameters | Description |
|--------|------------|-------------|
| `eth_subscribe` | `[type, options]` | Subscribe to events (newHeads, logs, newPendingTransactions, syncing) |
| `eth_unsubscribe` | `[subscriptionId]` | Cancel a subscription |

---

## Error Codes

| Code | Message | Description |
|------|---------|-------------|
| `-32700` | Parse error | Invalid JSON |
| `-32600` | Invalid request | Invalid request object |
| `-32601` | Method not found | Method does not exist |
| `-32602` | Invalid params | Invalid method parameters |
| `-32603` | Internal error | Internal JSON-RPC error |
| `-32005` | Rate limit / CU exceeded | CUPS or monthly CU quota exceeded |

---

## Code Examples

### ethers.js v6

```javascript
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(
  `https://bsc-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`
);

// Read operations
const blockNumber = await provider.getBlockNumber();
const balance = await provider.getBalance("0x407d73d8a49eeb85d32cf465507dd71d507100c1");
const block = await provider.getBlock(blockNumber);

// Contract interaction
const contract = new ethers.Contract(contractAddress, abi, provider);
const result = await contract.someReadMethod();

// Transaction submission (requires signer)
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);
const tx = await wallet.sendTransaction({
  to: "0x407d73d8a49eeb85d32cf465507dd71d507100c1",
  value: ethers.parseEther("0.01"),
});
```

### viem

```javascript
import { createPublicClient, http } from "viem";
import { bsc } from "viem/chains";

const client = createPublicClient({
  chain: bsc,
  transport: http(`https://bsc-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`),
});

const blockNumber = await client.getBlockNumber();
const balance = await client.getBalance({ address: "0x407d73d8a49eeb85d32cf465507dd71d507100c1" });
const block = await client.getBlock();
```

### Raw fetch

```javascript
async function rpcCall(method, params = []) {
  const response = await fetch(
    `https://bsc-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method,
        params,
      }),
    }
  );
  const data = await response.json();
  if (data.error) throw new Error(data.error.message);
  return data.result;
}

const blockNumber = await rpcCall("eth_blockNumber");
const balance = await rpcCall("eth_getBalance", ["0x407d73d8a49eeb85d32cf465507dd71d507100c1", "latest"]);
```

### Python (web3.py)

```python
from web3 import Web3
import os

w3 = Web3(Web3.HTTPProvider(
    f"https://bsc-mainnet.nodereal.io/v1/{os.environ['NODEREAL_API_KEY']}"
))

block_number = w3.eth.block_number
balance = w3.eth.get_balance("0x407d73d8a49eeb85d32cf465507dd71d507100c1")
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| `-32005` rate limit error | Exceeded CUPS (calls per second) limit | Implement exponential backoff; upgrade plan for higher CUPS |
| `-32005` "ran out of cu" | Monthly CU quota exhausted | Upgrade plan or wait for monthly reset |
| `method not found` error | Method not supported on this chain | Check supported chains for chain-specific availability |
| Empty response for `eth_getLogs` | Block range too large or no matching logs | Reduce block range to under 50K blocks; verify contract address and topics |
| `execution reverted` on `eth_call` | Contract reverted the call | Check function selector, parameters, and contract state |
| Timeout on archive queries | Archive data retrieval is slower | Use `latest` block tag when historical data is not needed |
| WebSocket disconnects | Idle connections are closed after timeout | Implement reconnection logic with exponential backoff |

## Documentation

- **API Reference:** https://docs.nodereal.io/reference
- **Supported Chains:** https://docs.nodereal.io/docs/supported-chains
- **Pricing & CU Costs:** https://nodereal.io/pricing
- **LLM-Optimized Docs:** https://docs.nodereal.io/llms.txt
