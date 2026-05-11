# Clanker v4 — Direct Mode Reference

Launch ERC-20 tokens with Uniswap V4 pools on 7 EVM chains. Built-in sniper protection, configurable reward splits, and stable token pairing.

**Publisher:** Quick Intel / Web3 Collective — https://quickintel.io
**Source:** https://github.com/Quick-Intel/openclaw-skills/tree/main/token-launcher
**Clanker SDK docs:** https://clanker.gitbook.io/clanker-documentation/sdk/v4.0.0

---

## Setup

```bash
npm install clanker-sdk viem
```

```typescript
import { Clanker } from "clanker-sdk/v4";
import {
  FEE_CONFIGS,
  POOL_POSITIONS,
  WETH_ADDRESSES,
} from "clanker-sdk";
import { createPublicClient, createWalletClient, http } from "viem";
import { privateKeyToAccount } from "viem/accounts";
import { base } from "viem/chains";

// Load securely from secrets manager — never hardcode
const account = privateKeyToAccount(process.env.LAUNCH_WALLET_PRIVATE_KEY as `0x${string}`);

const publicClient = createPublicClient({
  chain: base,
  transport: http(process.env.RPC_URL),
});

const walletClient = createWalletClient({
  account,
  chain: base,
  transport: http(process.env.RPC_URL),
});

const clanker = new Clanker({
  publicClient,
  wallet: walletClient,
});
```

> **Security:** Use a dedicated launch wallet funded with minimal ETH for gas. The private key should be loaded from a secrets manager (AWS Secrets Manager, GCP Secret Manager, etc.), not from a plaintext `.env` file in production. See the [Security section in REFERENCE.md](../REFERENCE.md) for details.

---

## Supported Chains

| Chain | Chain ID | WETH Address | Stable Pairing |
|-------|----------|-------------|----------------|
| Base | 8453 | Via `WETH_ADDRESSES` from SDK | USDC: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Arbitrum | 42161 | Via SDK | USDC: `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` |
| Mainnet | 1 | Via SDK | USDC: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| Unichain | 130 | Via SDK | — |
| Abstract | — | Via SDK | — |
| Monad | — | Via SDK | — |
| BSC | 56 | WBNB via SDK | USDT: BSC USDT address |

Import chain objects from `viem/chains` (`base`, `arbitrum`, `mainnet`, `unichain`). For Monad and Abstract, define custom chain configs.

---

## Launch a Token

### 100% to You (Direct Mode)

```typescript
const { txHash, waitForTransaction, error } = await clanker.deploy({
  chainId: 8453, // Base
  name: "Galaxy Cat",
  symbol: "GCAT",
  image: "https://example.com/gcat.png", // or ipfs:// URI
  tokenAdmin: YOUR_WALLET_ADDRESS,
  metadata: {
    description: "Galaxy Cat ($GCAT) - The first feline in the cosmos",
  },
  pool: {
    pairedToken: WETH_ADDRESSES[8453], // WETH on Base
    positions: POOL_POSITIONS.Standard,
  },
  fees: FEE_CONFIGS.StaticBasic,
  rewards: {
    recipients: [
      {
        recipient: YOUR_WALLET_ADDRESS,  // 100% to you
        admin: YOUR_WALLET_ADDRESS,       // you control this reward entry
        bps: 10_000,                      // 100% of pool fees
        token: "Both",                    // receive both token types
      },
    ],
  },
  sniperFees: {
    startingFee: 666_777,   // 66.7% starting fee
    endingFee: 41_673,      // 4.2% ending fee
    secondsToDecay: 15,     // Decays over 15 seconds
  },
  vanity: true, // Try to get a vanity address
});

if (error) {
  console.error("Deploy failed:", error.message);
} else {
  console.log("TX:", txHash);
  const { address } = await waitForTransaction();
  console.log("Token deployed at:", address);
}
```

### Split Between Multiple Recipients

```typescript
rewards: {
  recipients: [
    {
      recipient: CREATOR_WALLET,
      admin: CREATOR_WALLET,
      bps: 7_000,           // 70%
      token: "Both",
    },
    {
      recipient: TREASURY_WALLET,
      admin: CREATOR_WALLET, // creator can update treasury's share
      bps: 3_000,           // 30%
      token: "Both",
    },
  ],
},
```

Total BPS across all recipients must equal 10,000.

### Stable Token Pairing (USDC/USDT)

Instead of pairing with WETH, pair with a stablecoin:

```typescript
pool: {
  pairedToken: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", // USDC on Base
  positions: POOL_POSITIONS.Standard,
},
```

Not all chains have stable pairing available yet. Check `STABLE_PAIR_ADDRESSES` for your target chain.

---

## Sniper Protection

Clanker v4 includes decaying fee sniper protection. When a token launches, the first swaps pay an elevated fee that decays to normal over a configurable window:

```typescript
sniperFees: {
  startingFee: 666_777,   // 66.7777% — punishes bots in the first seconds
  endingFee: 41_673,      // 4.1673% — normal fee after decay
  secondsToDecay: 15,     // Linear decay over 15 seconds
},
```

This is built into the Uniswap V4 hook. No additional contracts needed.

---

## Check Unclaimed Rewards

```typescript
const available = await clanker.availableRewards({
  token: TOKEN_ADDRESS,
  rewardRecipient: YOUR_WALLET_ADDRESS,
});

// Parse the response — shape varies by SDK version
// Look for pairedAmount, amount, or total fields
console.log("Unclaimed rewards:", available);
```

---

## Claim Rewards

### Direct Claim (Your Wallet Signs)

```typescript
const { txHash, error } = await clanker.claimRewards({
  token: TOKEN_ADDRESS,
  rewardRecipient: YOUR_WALLET_ADDRESS,
});

if (error) {
  console.error("Claim failed:", error.message);
} else {
  console.log("Claimed:", txHash);
}
```

### Unsigned Transaction (For External Agent Wallets)

If your agent wallet signs externally, get the transaction data without executing:

```typescript
const txConfig = await clanker.getClaimRewardsTransaction({
  token: TOKEN_ADDRESS,
  rewardRecipient: AGENT_WALLET_ADDRESS,
});

if (txConfig && txConfig.address) {
  const data = encodeFunctionData({
    abi: txConfig.abi,
    functionName: txConfig.functionName,
    args: txConfig.args,
  });

  // Return this to the agent wallet to sign
  const unsignedTx = {
    to: txConfig.address,
    data: data,
    value: (txConfig.value || 0).toString(),
    gas: "300000",
  };
}
```

---

## Update Reward Recipient

Change who receives the creator fee share. Only the `admin` of a reward entry can update its recipient.

```typescript
// Step 1: Update the recipient
const { txHash, error } = await clanker.updateRewardRecipient({
  token: TOKEN_ADDRESS,
  rewardIndex: 0n, // Index of the reward entry to update (0 = first recipient)
  newRecipient: NEW_WALLET_ADDRESS,
});

// Step 2: Transfer admin rights to the new recipient
// (so they can manage their own fees going forward)
const { txHash: adminTx, error: adminError } = await clanker.updateRewardAdmin({
  token: TOKEN_ADDRESS,
  rewardIndex: 0n,
  newAdmin: NEW_WALLET_ADDRESS,
});
```

### Unsigned Transaction Version

```typescript
const txConfig = await clanker.getUpdateRewardRecipientTransaction({
  token: TOKEN_ADDRESS,
  rewardIndex: 0n,
  newRecipient: NEW_WALLET_ADDRESS,
});

// Encode and return as unsigned TX (same pattern as claim)
```

### Simulation

Before executing, you can simulate to check validity:

```typescript
await clanker.updateRewardRecipientSimulate({
  token: TOKEN_ADDRESS,
  rewardIndex: 0n,
  newRecipient: NEW_WALLET_ADDRESS,
});
```

---

## Context Object (Optional — Privacy Considerations)

Clanker accepts an optional context object for analytics. **All fields are optional and can be omitted entirely.** If you include them, these values are sent to Clanker's infrastructure:

```typescript
// OPTIONAL — omit entirely if privacy is a concern
context: {
  interface: "My Agent",     // Your agent/app name
  platform: "telegram",      // Where the user is
  messageId: "msg_123",      // Message ID that triggered the launch
  id: "user_456",            // User identifier
},
```

**Privacy-safe alternative:** Omit `context` entirely, or use non-identifying values:

```typescript
context: {
  interface: "my-agent",
  platform: "api",
  // Omit messageId and id to avoid sending user identifiers
},
```

No operation requires the context object to succeed.

---

## Key Constants

```typescript
// Reward BPS
const FULL_REWARD = 10_000;    // 100% of pool fees to one recipient

// Sniper protection defaults
const DEFAULT_SNIPER_FEES = {
  startingFee: 666_777,   // ~66.7%
  endingFee: 41_673,      // ~4.2%
  secondsToDecay: 15,
};

// Token supply is always 1 billion (set by Clanker)
// Liquidity is locked (set by Clanker)
```

---

## Error Handling

The Clanker SDK returns `{ txHash, waitForTransaction, error }` from deploy and `{ txHash, error }` from other operations. Always check `error` before proceeding:

```typescript
const { txHash, error } = await clanker.deploy({ ... });

if (error) {
  // Handle: insufficient gas, invalid params, chain not supported, etc.
  console.error(error.message);
  return;
}

// Wait for on-chain confirmation
const { address } = await waitForTransaction();
```

Common errors:
- Insufficient gas in the signing wallet
- Invalid chain ID
- Reward BPS don't total 10,000
- Stable pairing not available on the target chain
- RPC connection issues
