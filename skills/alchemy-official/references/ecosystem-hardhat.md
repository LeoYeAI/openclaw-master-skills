---
id: references/ecosystem-hardhat.md
name: 'Hardhat'
description: 'Hardhat is a popular Ethereum development environment for compiling, testing, and deploying contracts.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - node-json-rpc.md
updated: 2026-02-05
---
# Hardhat

## Summary
Hardhat is a popular Ethereum development environment for compiling, testing, and deploying contracts.

## Why It Pairs Well With Alchemy
- Use Alchemy RPC endpoints for mainnet/testnet forking and deployments.

## Quick Setup
```ts
// hardhat.config.ts
export default {
  networks: {
    mainnet: {
      url: `https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`,
    },
  },
};
```

## Related Files
- `node-json-rpc.md`

## Official Docs
- [Hardhat Docs](https://hardhat.org/docs)
