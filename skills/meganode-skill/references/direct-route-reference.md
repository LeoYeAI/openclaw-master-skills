# Direct Route Reference -- MEV Protection

## Overview

NodeReal Builder (formerly Direct Route) provides MEV (Maximal Extractable Value) protection by routing transactions directly to validators, bypassing the public mempool. This prevents front-running, sandwich attacks, and other MEV exploitation.

**Supported chain:** BNB Smart Chain (BSC) only

## Endpoint

```
https://bsc-mainnet-builder.nodereal.io
```

## Key Features

- **Mempool bypass:** Transactions are never visible in the public mempool
- **Sealed-bid auction:** Users privately communicate bid and ordering preferences
- **No failed transaction costs:** Losing bids are never included in a block
- **Bundle atomicity:** All transactions in a bundle succeed together or none are included
- **Good Will Alliance member:** Committed to fair execution practices

---

## Table of Contents

1. [Endpoint](#endpoint) -- Builder service URL
2. [Key Features](#key-features) -- MEV protection capabilities
3. [API Methods](#api-methods) -- Available JSON-RPC methods
4. [Coinbase Deposit (Priority Boost)](#coinbase-deposit-priority-boost) -- Higher priority via BNB deposit
5. [Code Examples](#code-examples) -- JavaScript integration samples
6. [Processing Timeline](#processing-timeline) -- Submission to inclusion timing
7. [Use Cases](#use-cases) -- Common MEV protection scenarios
8. [Best Practices](#best-practices) -- Recommended usage guidelines

---

## API Methods

### `eth_sendPrivateTransaction`

Submit a single private transaction that bypasses the public mempool.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_sendPrivateTransaction",
  "params": ["0xSignedTransactionHex"]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `params[0]` | `string` | Yes | Signed, RLP-encoded transaction hex string |

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0xTransactionHash"
}
```

### `eth_sendBundle`

Submit multiple transactions as an atomic bundle. All transactions execute together or none are included.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_sendBundle",
  "params": [{
    "txs": [
      "0xSignedTx1Hex",
      "0xSignedTx2Hex"
    ],
    "maxBlockNumber": "0x...",
    "minTimestamp": 0,
    "maxTimestamp": 1700000000,
    "revertingTxHashes": []
  }]
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `txs` | `string[]` | Yes | Array of signed, encoded transaction hex strings |
| `maxBlockNumber` | `string` | No | Maximum block number for inclusion (hex) |
| `minTimestamp` | `number` | No | Earliest Unix timestamp for bundle verification |
| `maxTimestamp` | `number` | No | Latest Unix timestamp (set 60+ seconds ahead) |
| `revertingTxHashes` | `string[]` | No | Hashes of transactions allowed to revert |

**Constraint:** Only one transaction sender is allowed per bundle.

**Response:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": "0xBundleHash"
}
```

### `eth_getBundleByHash`

Query bundle status and details by bundle hash.

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_getBundleByHash",
  "params": ["0xBundleHash"]
}
```

### `eth_bundlePrice`

Get current suggested bundle price (volatile based on network congestion).

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "eth_bundlePrice",
  "params": []
}
```

---

## Coinbase Deposit (Priority Boost)

For higher priority inclusion, deposit BNB to the Coinbase contract:

| Network | Contract Address |
|---------|-----------------|
| BSC Mainnet | `0xB3BB00B9785f35D0BE13B2BD91C8e3742D9Ab03a` |
| BSC Testnet | `0xE7febD44315508a1100E1a06701e7e0Ae5e325Bc` |

---

## Code Examples

### Send Private Transaction

```javascript
import { ethers } from "ethers";

const BUILDER_URL = "https://bsc-mainnet-builder.nodereal.io";

async function sendPrivateTransaction(signedTx) {
  const response = await fetch(BUILDER_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_sendPrivateTransaction",
      params: [signedTx],
    }),
  });
  return response.json();
}

// Usage
const provider = new ethers.JsonRpcProvider(
  `https://bsc-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`
);
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

const tx = await wallet.signTransaction({
  to: "0xRecipient",
  value: ethers.parseEther("0.1"),
  gasPrice: await provider.getFeeData().then(f => f.gasPrice),
  gasLimit: 21000,
  nonce: await provider.getTransactionCount(wallet.address),
  chainId: 56,
});

const result = await sendPrivateTransaction(tx);
console.log("Private tx hash:", result.result);
```

### Send Atomic Bundle

```javascript
async function sendBundle(signedTxs) {
  const response = await fetch(BUILDER_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_sendBundle",
      params: [{
        txs: signedTxs,
        maxTimestamp: Math.floor(Date.now() / 1000) + 120,
        minTimestamp: 0,
      }],
    }),
  });
  return response.json();
}

// Monitor bundle status
async function checkBundleStatus(bundleHash) {
  const response = await fetch(BUILDER_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_getBundleByHash",
      params: [bundleHash],
    }),
  });
  return response.json();
}
```

### Get Current Bundle Price

```javascript
async function getBundlePrice() {
  const response = await fetch(BUILDER_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "eth_bundlePrice",
      params: [],
    }),
  });
  return response.json();
}
```

---

## Processing Timeline

After successful bundle/transaction submission:
- Wait **3-60 seconds** for on-chain verification
- Check status via `eth_getBundleByHash` or `eth_getTransactionReceipt`
- If not included after 60 seconds, consider resubmission with updated parameters

## Use Cases

- **DeFi trades:** Protect swaps from sandwich attacks
- **Token launches:** Prevent front-running of buy transactions
- **Arbitrage:** Execute multi-step atomic transactions
- **Liquidations:** Private submission of liquidation transactions

## Best Practices

- Always set `maxTimestamp` at least 60 seconds ahead of current time
- Monitor bundle status after submission -- do not assume inclusion
- Use `revertingTxHashes` for transactions that may legitimately fail
- Only one sender per bundle -- design transaction flow accordingly
- Implement retry logic with updated timestamps on bundle expiry
- Check `eth_bundlePrice` before submission to set competitive gas prices
