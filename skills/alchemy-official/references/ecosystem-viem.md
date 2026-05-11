---
id: references/ecosystem-viem.md
name: 'Viem'
description: 'Viem is a modern TypeScript Ethereum client library with strong types and a functional API.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - node-json-rpc.md
updated: 2026-02-05
---
# Viem

## Summary
Viem is a modern TypeScript Ethereum client library with strong types and a functional API.

## Why It Pairs Well With Alchemy
- Easy to plug in Alchemy RPC URLs.
- Strong typing and fast performance.

## Quick Setup
```ts
import { createPublicClient, http } from "viem";
import { mainnet } from "viem/chains";

const client = createPublicClient({
  chain: mainnet,
  transport: http(`https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`),
});
```

## Related Files
- `node-json-rpc.md`

## Official Docs
- [Viem Docs](https://viem.sh/)
