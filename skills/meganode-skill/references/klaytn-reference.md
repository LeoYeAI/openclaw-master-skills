# Klaytn RPC Reference

## Overview

Klaytn (KAIA) blockchain JSON-RPC access with `klay_` namespace methods. This reference covers all 54 supported `klay_*` methods available through the NodeReal MegaNode platform, organized by functional category. Klaytn is a high-performance blockchain with unique features including fee delegation, multiple account key types, and council/committee-based consensus.

**Endpoint:**
```
https://open-platform.nodereal.io/{apiKey}/klaytn/
```

**Supported Networks:** Klaytn Cypress (mainnet)

## Table of Contents

1. [Account Methods](#account-methods-12) -- 12 methods for account info, balances, keys, and storage
2. [Block Methods](#block-methods-11) -- 11 methods for block data, headers, receipts, and rewards
3. [Transaction Methods](#transaction-methods-12) -- 12 methods for transaction lookup, sending, and fee delegation
4. [Call / Execution Methods](#call--execution-methods-3) -- 3 methods for call execution and gas/computation estimation
5. [Gas / Fee Methods](#gas--fee-methods-4) -- 4 methods for gas price and fee history
6. [Filter Methods](#filter-methods-2) -- 2 methods for log filtering
7. [Chain Information Methods](#chain-information-methods-7) -- 7 methods for chain ID, sync status, and node info
8. [Council / Committee Methods](#council--committee-methods-4) -- 4 methods for validator council and committee info
9. [Utility](#utility-1) -- 1 method for hashing
10. [Klaytn Transaction Error Codes](#klaytn-transaction-error-codes-txerror) -- Common txError codes

### Account Methods (12)

| Method | Description |
|--------|-------------|
| `klay_accountCreated` | Check if account exists at address |
| `klay_accounts` | List addresses owned by client |
| `klay_getAccount` | Get account information (EOA or Smart Contract) |
| `klay_getAccountKey` | Get account key of EOA |
| `klay_encodeAccountKey` | RLP encode an account key |
| `klay_decodeAccountKey` | Decode RLP-encoded account key |
| `klay_getBalance` | Get balance in peb |
| `klay_getCode` | Get contract code at address |
| `klay_getTransactionCount` | Get nonce for address |
| `klay_isContractAccount` | Check if address is a contract |
| `klay_sign` | Sign data with address |
| `klay_getStorageAt` | Get storage value at position |

#### klay_getAccount

Returns account information. Klaytn has two account types: EOA (accType=1) and Smart Contract (accType=2).

```bash
curl https://open-platform.nodereal.io/{apiKey}/klaytn/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"klay_getAccount","params":["0x3111a0577f322e8fb54f78d9982a26ae7ca0f722", "latest"],"id":1}'
```

**Response (EOA):**
```json
{
  "id": 1,
  "jsonrpc": "2.0",
  "result": {
    "accType": 1,
    "account": {
      "balance": 4985316100000000000,
      "humanReadable": false,
      "key": {
        "key": {
          "x": "0x230037a99462acd829f317d0ce5c8e2321ac2951de1c1b1a18f9af5cff66f0d7",
          "y": "0x18a7fb1b9012d2ac87bc291cbf1b3b2339356f1ce7669ae68405389be7f8b3b6"
        },
        "keyType": 2
      },
      "nonce": 11
    }
  }
}
```

#### klay_getBalance

```bash
curl https://open-platform.nodereal.io/{apiKey}/klaytn/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"klay_getBalance","params":["0xc94770007dda54cF92009BFF0dE90c06F603a09f", "latest"],"id":1}'
```

### Block Methods (11)

| Method | Description |
|--------|-------------|
| `klay_blockNumber` | Get current block number |
| `klay_getBlockByNumber` | Get block by number |
| `klay_getBlockByHash` | Get block by hash |
| `klay_getBlockReceipts` | Get all receipts in a block |
| `klay_getBlockTransactionCountByNumber` | Get tx count in block by number |
| `klay_getBlockTransactionCountByHash` | Get tx count in block by hash |
| `klay_getBlockWithConsensusInfoByHash` | Get block with consensus info by hash |
| `klay_getBlockWithConsensusInfoByNumber` | Get block with consensus info by number |
| `klay_getHeaderByHash` | Get header by hash |
| `klay_getHeaderByNumber` | Get header by number |
| `klay_getRewards` | Get block rewards |

### Transaction Methods (12)

| Method | Description |
|--------|-------------|
| `klay_getTransactionByHash` | Get transaction by hash |
| `klay_getTransactionByBlockHashAndIndex` | Get tx by block hash and index |
| `klay_getTransactionByBlockNumberAndIndex` | Get tx by block number and index |
| `klay_getTransactionBySenderTxHash` | Get tx by sender tx hash (Klaytn-specific) |
| `klay_getTransactionReceipt` | Get transaction receipt |
| `klay_getTransactionReceiptBySenderTxHash` | Get receipt by sender tx hash |
| `klay_sendRawTransaction` | Send signed transaction |
| `klay_sendTransaction` | Send transaction (node signs) |
| `klay_sendTransactionAsFeePayer` | Send as fee payer (fee delegation) |
| `klay_signTransaction` | Sign transaction without sending |
| `klay_signTransactionAsFeePayer` | Sign as fee payer |

Klaytn transactions include fee delegation fields: `feePayer`, `feePayerSignatures`, `feeRatio`, `senderTxHash`.

#### klay_getTransactionReceipt

```bash
curl https://open-platform.nodereal.io/{apiKey}/klaytn/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc":"2.0","method":"klay_getTransactionReceipt","params":["0xaca5d9a1ed8b86b1ef61431b2bedfc99a66eaefc3a7e1cffdf9ff53653956a67"],"id":1}'
```

### Call / Execution Methods (3)

| Method | Description |
|--------|-------------|
| `klay_call` | Execute call without creating transaction |
| `klay_estimateGas` | Estimate gas for transaction |
| `klay_estimateComputationCost` | Estimate computation cost (Klaytn-specific) |

#### klay_call

```bash
curl https://open-platform.nodereal.io/{apiKey}/klaytn/ \
  -X POST \
  -H "Content-Type: application/json" \
  --data '{"jsonrpc": "2.0", "method": "klay_call", "params": [{"from": "0x3f71029af4e252b25b9ab999f77182f0cd3bc085", "to": "0x87ac99835e67168d4f9a40580f8f5c33550ba88b", "gas": "0x100000", "gasPrice": "0x5d21dba00", "value": "0x0", "input": "0x8ada066e"}, "latest"], "id": 1}'
```

### Gas / Fee Methods (4)

| Method | Description |
|--------|-------------|
| `klay_gasPrice` | Get current gas price in peb |
| `klay_gasPriceAt` | Get gas price at specific block |
| `klay_feeHistory` | Get fee history for block range |
| `klay_maxPriorityFeePerGas` | Get suggested gas tip cap |

### Filter Methods (2)

| Method | Description |
|--------|-------------|
| `klay_getFilterChanges` | Poll filter for new changes |
| `klay_getFilterLogs` | Get all logs matching filter |

### Chain Information Methods (7)

| Method | Description |
|--------|-------------|
| `klay_chainID` | Get chain ID (0x2019 = 8217 for Cypress) |
| `klay_clientVersion` | Get client version |
| `klay_protocolVersion` | Get protocol version |
| `klay_syncing` | Get sync status |
| `klay_rewardbase` | Get rewardbase address |
| `klay_isParallelDBWrite` | Check parallel DB write status |
| `klay_isSenderTxHashIndexingEnabled` | Check sender tx hash indexing |

### Council / Committee Methods (4)

| Method | Description |
|--------|-------------|
| `klay_getCouncil` | Get list of council validators |
| `klay_getCouncilSize` | Get council size |
| `klay_getCommittee` | Get list of committee validators |
| `klay_getCommitteeSize` | Get committee size |

### Utility (1)

| Method | Description |
|--------|-------------|
| `klay_sha3` | Compute Keccak-256 hash |

**Total: 54 klay_* methods**

### Klaytn Transaction Error Codes (txError)

| Code | Description |
|------|-------------|
| 0x02 | VM error while running smart contract |
| 0x03 | Max call depth exceeded |
| 0x07 | Out of gas |
| 0x09 | EVM: execution reverted |
| 0x0a | Opcode computation cost limit reached |
| 0x0e | Fee ratio out of range [1, 99] |

**Notes:**
- Klaytn uses **peb** (1 KLAY = 10^18 peb) and **ston** (1 ston = 10^9 peb)
- Fee delegation allows a separate fee payer via `feePayer` and `feeRatio` fields
- Block time is approximately 1 second
- `senderTxHash` differs from `transactionHash` for fee-delegated transactions
