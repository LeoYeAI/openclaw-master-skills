---
name: agentwallet-sdk
description: Non-custodial wallet SDK for AI agents. Provides ERC-6551 token-bound accounts, on-chain SpendingPolicy limits, x402 payments, 17-chain CCTP bridging, Circle Nanopayments (gas-free micro-payments), and Uniswap V3 token swaps. Use when an agent needs to hold funds, pay for services, or move value across chains.
metadata: '{"openclaw":{"requires":{"env":["AGENT_WALLET_PRIVATE_KEY"]}}}'
---

# AgentWallet SDK

Non-custodial wallet SDK designed for AI agents. Each agent gets its own ERC-6551 token-bound account with on-chain spending controls, cross-chain bridging, and gas-free micro-payment rails.

- **npm**: `agentwallet-sdk` (~1,200 downloads/week)
- **GitHub**: https://github.com/up2itnow0822/agent-wallet-sdk

## Core Capabilities

- **ERC-6551 Token-Bound Accounts** — Agent identity and wallet tied to an NFT; portable across dApps
- **SpendingPolicy** — On-chain per-period and per-transaction spend limits to constrain agent behavior
- **x402 Payments** — HTTP 402 Payment Required flow for pay-per-use API calls
- **CCTP Bridging** — Circle's Cross-Chain Transfer Protocol across 17 supported chains
- **Circle Nanopayments** — Gas-free micro-payments for high-frequency, low-value transactions
- **Uniswap V3 Swaps** — In-wallet token swaps via Uniswap V3 liquidity pools

## Setup

```bash
npm install agentwallet-sdk
```

Set the agent's private key:

```bash
export AGENT_WALLET_PRIVATE_KEY=0x...
```

## Quick Start

```typescript
import { AgentWallet } from 'agentwallet-sdk';

const wallet = new AgentWallet({
  privateKey: process.env.AGENT_WALLET_PRIVATE_KEY,
  chainId: 1, // Ethereum mainnet
});

// Check balance
const balance = await wallet.getBalance();
console.log(`Balance: ${balance.formatted} ETH`);
```

## SpendingPolicy

Set on-chain limits to constrain how much an agent can spend autonomously:

```typescript
// Set a daily spend limit of 10 USDC
await wallet.setSpendingPolicy({
  periodLimit: '10', // USDC per period
  perTxLimit: '2',   // max per single transaction
  periodSeconds: 86400, // 24-hour rolling window
  token: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // USDC
});
```

## x402 Payments

Handle HTTP 402 Payment Required responses automatically:

```typescript
import { x402Fetch } from 'agentwallet-sdk';

// Automatically pays when the server returns 402
const response = await x402Fetch('https://api.example.com/premium-endpoint', {
  wallet,
  maxPayment: '0.01', // USDC ceiling
});
```

## Cross-Chain Bridging (CCTP)

Move USDC across 17 supported chains via Circle's CCTP:

```typescript
await wallet.bridge({
  fromChain: 1,        // Ethereum
  toChain: 8453,       // Base
  amount: '5.00',      // USDC
  token: 'USDC',
});
```

Supported chains include Ethereum, Base, Arbitrum, Optimism, Polygon, Avalanche, and more.

## Circle Nanopayments

Send gas-free micro-payments using Circle's off-chain payment rails:

```typescript
await wallet.nanopay({
  recipient: '0xRecipient...',
  amount: '0.001', // USDC — gas-free at this scale
});
```

## Uniswap V3 Swaps

Swap tokens in-wallet without leaving the SDK:

```typescript
await wallet.swap({
  tokenIn: 'ETH',
  tokenOut: 'USDC',
  amountIn: '0.01',
  slippageTolerance: 0.5, // 0.5%
});
```

## ERC-6551 Token-Bound Accounts

Each agent wallet is tied to an NFT, giving agents a portable on-chain identity:

```typescript
// Deploy a token-bound account for an existing NFT
const tba = await wallet.deployTokenBoundAccount({
  nftContract: '0xNFTContract...',
  tokenId: '42',
});
console.log(`Agent TBA address: ${tba.address}`);
```

## Security Rules

1. **Never log or print private keys.** Use environment variables only.
2. **Set SpendingPolicy before giving agents autonomy.** On-chain limits are the last line of defense.
3. **Validate x402 payment amounts before signing.** Always cap with `maxPayment`.
4. **Test on testnets first.** Use `chainId: 84532` (Base Sepolia) or `chainId: 11155111` (Sepolia) before mainnet.

## References

- GitHub: https://github.com/up2itnow0822/agent-wallet-sdk
- npm: https://www.npmjs.com/package/agentwallet-sdk
- ERC-6551 spec: https://eips.ethereum.org/EIPS/eip-6551
- Circle CCTP docs: https://developers.circle.com/stablecoins/cctp-getting-started
- x402 protocol: https://x402.org
