# Common Patterns Reference

## Overview

Common integration patterns for building with NodeReal MegaNode APIs. These patterns combine multiple MegaNode products to solve typical blockchain development tasks.

---

## Table of Contents

1. [Multi-Chain dApp Setup](#1-multi-chain-dapp-setup) -- configure providers for multiple chains with a single API key
2. [Real-Time Transfer Monitoring](#2-real-time-transfer-monitoring) -- monitor ERC-20 Transfer events via WebSocket
3. [Token Portfolio Query](#3-token-portfolio-query) -- get all ERC-20 tokens for a wallet using Enhanced APIs

---

## 1. Multi-Chain dApp Setup

Use a single NodeReal API key to configure providers for all supported chains:

```javascript
const chains = {
  bsc: `https://bsc-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`,
  ethereum: `https://eth-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`,
  optimism: `https://opt-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`,
  opbnb: `https://opbnb-mainnet.nodereal.io/v1/${process.env.NODEREAL_API_KEY}`,
  // Note: Klaytn uses the Marketplace endpoint format, not standard RPC
  klaytn: `https://open-platform.nodereal.io/${process.env.NODEREAL_API_KEY}/klaytn/`,
};

// Create providers for each chain
const providers = Object.fromEntries(
  Object.entries(chains).map(([name, url]) => [
    name,
    new ethers.JsonRpcProvider(url),
  ])
);
```

---

## 2. Real-Time Transfer Monitoring

Monitor ERC-20 Transfer events on BSC using WebSocket subscriptions:

```javascript
// Monitor ERC-20 Transfer events on BSC
const ws = new WebSocket(
  `wss://bsc-mainnet.nodereal.io/ws/v1/${process.env.NODEREAL_API_KEY}`
);

ws.on("open", () => {
  ws.send(JSON.stringify({
    jsonrpc: "2.0",
    id: 1,
    method: "eth_subscribe",
    params: ["logs", {
      topics: [
        "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef" // Transfer(address,address,uint256)
      ],
    }],
  }));
});
```

---

## 3. Token Portfolio Query

Get all ERC-20 tokens held by a wallet address using the Enhanced API:

```javascript
// Get all ERC-20 tokens for a wallet
async function getTokenPortfolio(walletAddress) {
  const response = await fetch(RPC_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: 1,
      method: "nr_getTokenHoldings",
      params: [walletAddress, "0x1", "0x64"], // page 1, size 100
    }),
  });
  return response.json();
}
```
