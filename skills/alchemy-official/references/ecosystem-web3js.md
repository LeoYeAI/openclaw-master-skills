---
id: references/ecosystem-web3js.md
name: 'Web3.js'
description: 'Web3.js is a long-standing Ethereum JavaScript library for providers and contracts.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - node-json-rpc.md
updated: 2026-02-05
---
# Web3.js

## Summary
Web3.js is a long-standing Ethereum JavaScript library for providers and contracts.

## Why It Pairs Well With Alchemy
- JSON-RPC compatible with Alchemy endpoints.

## Quick Setup
```ts
import Web3 from "web3";

const web3 = new Web3(
  `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`
);
```

## Related Files
- `node-json-rpc.md`

## Official Docs
- [Web3.js Docs](https://docs.web3js.org/)
