# Token Swaps via OpenSea MCP

OpenSea MCP provides token swap functionality through integrated DEX aggregation. This allows swapping ERC20 tokens and native currencies across supported chains.

## Overview

The `get_token_swap_quote` tool returns:
1. **Quote details** - Expected output, fees, price impact
2. **Transaction calldata** - Ready to submit on-chain

## Supported Chains

- Ethereum (`ethereum`)
- Base (`base`)
- Polygon (`matic`)
- Arbitrum (`arbitrum`)
- Optimism (`optimism`)

## Getting a Swap Quote

### Via mcporter CLI

```bash
mcporter call opensea.get_token_swap_quote --args '{
  "fromContractAddress": "0x0000000000000000000000000000000000000000",
  "fromChain": "base",
  "toContractAddress": "0xb695559b26bb2c9703ef1935c37aeae9526bab07",
  "toChain": "base",
  "fromQuantity": "0.02",
  "address": "0xYourWalletAddress"
}'
```

### Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `fromContractAddress` | Yes | Token to swap FROM. Use `0x0000...0000` for native ETH |
| `toContractAddress` | Yes | Token to swap TO |
| `fromChain` | Yes | Source chain identifier |
| `toChain` | Yes | Destination chain identifier |
| `fromQuantity` | Yes | Amount in human units (e.g., "0.02" for 0.02 ETH) |
| `address` | Yes | Your wallet address |
| `recipient` | No | Recipient address (defaults to sender) |
| `slippageTolerance` | No | Slippage as decimal (e.g., 0.005 for 0.5%) |

### Response Structure

```json
{
  "swapQuote": {
    "swapRoutes": [{
      "toAsset": { "symbol": "MOLT", "usdPrice": "0.00045" },
      "fromAsset": { "symbol": "ETH", "usdPrice": "2370" },
      "costs": [
        { "costType": "GAS", "cost": { "usd": 0.01 } },
        { "costType": "MARKETPLACE", "cost": { "usd": 0.40 } }
      ],
      "swapImpact": { "percent": "3.5" }
    }],
    "totalPrice": { "usd": 47.40 }
  },
  "swap": {
    "actions": [{
      "transactionSubmissionData": {
        "to": "0xSwapRouterContract",
        "data": "0x...",
        "value": "20000000000000000",
        "chain": { "networkId": 8453, "identifier": "base" }
      }
    }]
  }
}
```

## Executing the Swap

### Using viem (JavaScript)

```javascript
import { createPublicClient, createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

// Get quote first (via mcporter or direct API call)
const quote = await getSwapQuote(...);
const txData = quote.swap.actions[0].transactionSubmissionData;

// Setup wallet
const account = privateKeyToAccount(PRIVATE_KEY);
const wallet = createWalletClient({ account, chain: base, transport: http() });
const pub = createPublicClient({ chain: base, transport: http() });

// Execute swap
const hash = await wallet.sendTransaction({
  to: txData.to,
  data: txData.data,
  value: BigInt(txData.value)
});

console.log(`TX: https://basescan.org/tx/${hash}`);

// Wait for confirmation
const receipt = await pub.waitForTransactionReceipt({ hash });
console.log(receipt.status === 'success' ? '✅ Swap complete!' : '❌ Failed');
```

### Using the swap script

```bash
./scripts/opensea-swap.sh <to_token_address> <amount_eth> <your_wallet> <private_key>

# Example: Swap 0.02 ETH to MOLT
./scripts/opensea-swap.sh 0xb695559b26bb2c9703ef1935c37aeae9526bab07 0.02 0xYourWallet 0xYourPrivateKey
```

## Finding Tokens

### Search by name
```bash
mcporter call opensea.search_tokens --args '{"query": "MOLT", "chain": "base", "limit": 5}'
```

### Get trending tokens
```bash
mcporter call opensea.get_trending_tokens --args '{"chains": ["base"], "limit": 10}'
```

### Get top tokens by volume
```bash
mcporter call opensea.get_top_tokens --args '{"chains": ["base"], "limit": 10}'
```

## Checking Balances

```bash
mcporter call opensea.get_token_balances --args '{
  "address": "0xYourWallet",
  "chains": ["base", "ethereum"]
}'
```

## Common Token Addresses (Base)

| Token | Address |
|-------|---------|
| WETH | `0x4200000000000000000000000000000000000006` |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| MOLT | `0xb695559b26bb2c9703ef1935c37aeae9526bab07` |
| CLAWD | `0x9f86db9fc6f7c9408e8fda3ff8ce4e78ac7a6b07` |
| 4CLAW | `0x3b94a3fa7f33930cf9fdc5f36cb251533c947b07` |

## Tips

1. **Use native ETH address** (`0x0000...0000`) when swapping from ETH
2. **Check slippage** - High impact swaps may fail; consider smaller amounts
3. **Quote expiration** - Execute quickly after getting quote; prices change
4. **Gas estimation** - The returned value includes all costs
5. **Cross-chain swaps** - Same-chain swaps are faster and cheaper
