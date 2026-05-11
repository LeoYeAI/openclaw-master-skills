# WebSocket Reference -- Real-Time Subscriptions

## Overview

MegaNode provides WebSocket (WSS) connections for real-time blockchain event streaming. Subscriptions push new data to clients as events occur on-chain, eliminating the need for polling.

WebSocket connections use the `eth_subscribe` and `eth_unsubscribe` JSON-RPC methods.

---

## Table of Contents

1. [WSS Endpoint Format](#wss-endpoint-format) -- Connection URL pattern
2. [Supported Chains and Endpoints](#supported-chains-and-endpoints) -- Available networks and URLs
3. [eth_subscribe](#eth_subscribe) -- Create real-time subscriptions
4. [Subscription Types](#subscription-types) -- Available event subscription kinds
5. [eth_unsubscribe](#eth_unsubscribe) -- Cancel active subscriptions
6. [Billing](#billing) -- WebSocket bandwidth CU costs
7. [wscat Examples](#wscat-examples) -- CLI subscription examples
8. [Code Examples](#code-examples) -- JavaScript integration samples
9. [Best Practices](#best-practices) -- Recommended usage guidelines

---

## WSS Endpoint Format

```
wss://{chain}-{network}.nodereal.io/ws/v1/{API-key}
```

## Supported Chains and Endpoints

| Chain | Network | WSS Endpoint |
|-------|---------|-------------|
| **BNB Smart Chain** | Mainnet | `wss://bsc-mainnet.nodereal.io/ws/v1/{API-key}` |
| **BNB Smart Chain** | Testnet | `wss://bsc-testnet.nodereal.io/ws/v1/{API-key}` |
| **opBNB** | Mainnet | `wss://opbnb-mainnet.nodereal.io/ws/v1/{API-key}` |
| **opBNB** | Testnet | `wss://opbnb-testnet.nodereal.io/ws/v1/{API-key}` |
| **Ethereum** | Mainnet | `wss://eth-mainnet.nodereal.io/ws/v1/{API-key}` |
| **Optimism** | Mainnet | `wss://opt-mainnet.nodereal.io/ws/v1/{API-key}` |

---

## eth_subscribe

Creates a new subscription for the specified event type. Returns a subscription ID used to identify incoming notifications and to unsubscribe.

### Parameters

- `SUBSCRIPTION TYPE NAME` [required] -- one of the following:
  - `newHeads` -- notification each time a new header is appended to the chain
  - `logs` -- logs from newly imported blocks matching given filter criteria
    - `address` (optional) -- either an address or an array of addresses
    - `topics` (optional) -- only logs which match the specified topics
  - `newPendingTransactions` -- hash for all transactions added to the pending state
  - `syncing` -- indicates when the node starts or stops synchronizing

### Returns

- `SUBSCRIPTION ID` -- ID of the newly created subscription on the node

### Chain Reorganizations

When a chain reorganization occurs, the `newHeads` subscription will emit events containing all new headers for the new chain. This means you may see multiple headers with the same block number. When this happens, the later (highest) block should be taken as the correct one after reorganization.

---

## Subscription Types

### `newHeads`

Notification each time a new block header is appended to the chain, including during chain reorganizations.

**Request:**
```json
{"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
```

**Notification payload:**
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
      "logsBloom": "0x000000000000000000000000000000000000000000000000...",
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

### `logs`

Filtered event logs from newly imported blocks.

**Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_subscribe",
  "params": [
    "logs",
    {
      "address": "0x8320fe7702b96890f7bbc0d4a888ed1468216cfd",
      "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]
    }
  ]
}
```

**Filter parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | `string` or `string[]` | No | Contract address(es) to filter |
| `topics` | `string[]` | No | Topic filters for log matching |

**Notification payload:**
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

### `newPendingTransactions`

Notification for each transaction added to the pending state. Returns the transaction hash only.

**Request:**
```json
{"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}
```

**Notification payload:**
```json
{
  "jsonrpc": "2.0",
  "method": "eth_subscription",
  "params": {
    "subscription": "0xc3b33aa549fe9a60e95d21862596617c",
    "result": "0xd6fdc5cc41a9959e9ee4d0cb772a9aef46f4daea279307bc5f7024edc4ccd7fa"
  }
}
```

### `syncing`

Notifications about node sync status changes.

**Request:**
```json
{"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["syncing"]}
```

**Notification payload (when syncing):**
```json
{
  "jsonrpc": "2.0",
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
```

---

## eth_unsubscribe

Cancel a subscription using the subscription ID returned during creation.

### Parameters

- `SUBSCRIPTION ID` -- the ID returned by `eth_subscribe`

### Returns

- `boolean` -- `true` if the subscription was cancelled successfully

### Request

```json
{"id": 1, "method": "eth_unsubscribe", "params": ["0x9cef478923ff08bf67fde6c64013158d"]}
```

### Response

```json
{"jsonrpc":"2.0","id":1,"result":true}
```

---

## Billing

WebSocket subscriptions are charged by bandwidth:

**Rate:** `0.04 CU per byte` of data transferred

This applies to all data received through WebSocket subscriptions. Filter subscriptions tightly to minimize costs.

---

## wscat Examples

### Connect and Subscribe (BSC)

```bash
$ wscat -c wss://bsc-mainnet.nodereal.io/ws/v1/your-api-key

# newHeads
> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}

# logs with filter
> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["logs", {"address": "0x8320fe7702b96890f7bbc0d4a888ed1468216cfd", "topics": ["0xd78a0cb8bb633d06981248b816e7bd33c2a35a6089241d099fa519e361cab902"]}]}

# newPendingTransactions
> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newPendingTransactions"]}

# syncing
> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["syncing"]}
```

### Connect and Subscribe (Ethereum)

```bash
$ wscat -c wss://eth-mainnet.nodereal.io/ws/v1/your-api-key

> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
```

### Connect and Subscribe (Optimism)

```bash
$ wscat -c wss://opt-mainnet.nodereal.io/ws/v1/your-api-key

> {"jsonrpc":"2.0", "id": 1, "method": "eth_subscribe", "params": ["newHeads"]}
```

### Unsubscribe

```bash
$ wscat -c wss://bsc-mainnet.nodereal.io/ws/v1/your-api-key

> {"id": 1, "method": "eth_unsubscribe", "params": ["0x9cef478923ff08bf67fde6c64013158d"]}
< {"jsonrpc":"2.0","id":1,"result":true}
```

---

## Code Examples

### Node.js with `ws`

```javascript
import WebSocket from "ws";

const ws = new WebSocket(
  `wss://bsc-mainnet.nodereal.io/ws/v1/${process.env.NODEREAL_API_KEY}`
);

ws.on("open", () => {
  console.log("Connected to MegaNode WebSocket");

  // Subscribe to new blocks
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "eth_subscribe",
    params: ["newHeads"],
  }));
});

ws.on("message", (data) => {
  const message = JSON.parse(data.toString());

  // Handle subscription confirmation
  if (message.id) {
    console.log("Subscription ID:", message.result);
    return;
  }

  // Handle new block notification
  if (message.params) {
    const block = message.params.result;
    console.log("New block:", parseInt(block.number, 16));
  }
});

ws.on("error", (error) => {
  console.error("WebSocket error:", error);
});

ws.on("close", () => {
  console.log("Connection closed");
  // Implement reconnection logic
});
```

### Monitor ERC-20 Transfer Events

```javascript
const TRANSFER_TOPIC = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef";

ws.on("open", () => {
  // Subscribe to Transfer events for a specific token
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "eth_subscribe",
    params: ["logs", {
      address: "0xTokenContractAddress",
      topics: [TRANSFER_TOPIC],
    }],
  }));
});

ws.on("message", (data) => {
  const message = JSON.parse(data.toString());
  if (message.params?.result) {
    const log = message.params.result;
    const from = "0x" + log.topics[1].slice(26);
    const to = "0x" + log.topics[2].slice(26);
    const value = BigInt(log.data);
    console.log(`Transfer: ${from} -> ${to}, Amount: ${value}`);
  }
});
```

### ethers.js WebSocket Provider

```javascript
import { ethers } from "ethers";

const provider = new ethers.WebSocketProvider(
  `wss://bsc-mainnet.nodereal.io/ws/v1/${process.env.NODEREAL_API_KEY}`
);

// Listen for new blocks
provider.on("block", (blockNumber) => {
  console.log("New block:", blockNumber);
});

// Listen for specific contract events
const contract = new ethers.Contract(contractAddress, abi, provider);
contract.on("Transfer", (from, to, value) => {
  console.log(`Transfer: ${from} -> ${to}, Value: ${value}`);
});
```

---

## Best Practices

- **Filter tightly:** Use specific `address` and `topics` to reduce bandwidth and CU costs
- **Implement reconnection:** WebSocket connections may drop -- always implement auto-reconnect with exponential backoff
- **Handle reorgs:** `newHeads` includes reorganizations -- track the `removed` field in log subscriptions
- **Unsubscribe when done:** Clean up subscriptions to stop billing
- **Prefer WSS over polling:** For real-time data, WSS is more efficient than repeated `eth_getLogs` calls
- **Monitor bandwidth:** At 0.04 CU/byte, high-volume subscriptions (e.g., `newPendingTransactions`) can consume CUs quickly
