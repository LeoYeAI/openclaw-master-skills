---
id: references/ecosystem-wagmi.md
name: 'wagmi'
description: 'wagmi provides React hooks for Ethereum, commonly used with wallet connectors and UI kits.'
tags:
  - alchemy
  - ecosystem
  - tooling
related:
  - node-json-rpc.md
updated: 2026-02-05
---
# wagmi

## Summary
wagmi provides React hooks for Ethereum, commonly used with wallet connectors and UI kits.

## Why It Pairs Well With Alchemy
- Easy to configure Alchemy RPC for read/write hooks.

## Quick Setup
```ts
import { createConfig, http } from "wagmi";
import { mainnet } from "wagmi/chains";

const config = createConfig({
  chains: [mainnet],
  transports: {
    [mainnet.id]: http(`https://eth-mainnet.g.alchemy.com/v2/${process.env.ALCHEMY_API_KEY}`),
  },
});
```

## Related Files
- `node-json-rpc.md`

## Official Docs
- [wagmi Docs](https://wagmi.sh/)
