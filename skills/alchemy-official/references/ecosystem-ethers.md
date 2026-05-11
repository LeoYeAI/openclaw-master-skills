---
id: references/ecosystem-ethers.md
name: 'Ethers.js'
description: 'Ethers.js is a widely used Ethereum library for wallets, providers, and contract interactions.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - node-json-rpc.md
updated: 2026-02-05
---
# Ethers.js

## Summary
Ethers.js is a widely used Ethereum library for wallets, providers, and contract interactions.

## Why It Pairs Well With Alchemy
- Works with any JSON-RPC provider.
- Mature ecosystem and tooling.

## Quick Setup
```ts
import { ethers } from "ethers";

const provider = new ethers.JsonRpcProvider(
  `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`
);
```

## Related Files
- `node-json-rpc.md`

## Official Docs
- [Ethers v6 Docs](https://docs.ethers.org/v6/)
