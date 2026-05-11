---
id: references/ecosystem-solana-web3js.md
name: '@solana/web3.js'
description: 'The primary JavaScript library for Solana RPC, transactions, and accounts.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - solana-rpc.md
updated: 2026-02-05
---
# @solana/web3.js

## Summary
The primary JavaScript library for Solana RPC, transactions, and accounts.

## Why It Pairs Well With Alchemy
- Use Alchemy Solana RPC as the connection endpoint.

## Quick Setup
```ts
import { Connection } from "@solana/web3.js";

const connection = new Connection(
  `https://solana-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`
);
```

## Related Files
- `solana-rpc.md`

## Official Docs
- [@solana/web3.js Docs](https://solana-foundation.github.io/solana-web3.js/)
