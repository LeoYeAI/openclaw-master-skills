# ClawLaunch Token Trading Reference

Complete reference for trading tokens on the ClawLaunch bonding curve.

## Overview

ClawLaunch uses a bonding curve pricing mechanism where token price increases as supply grows. All trades are executed against the bonding curve contract, not an order book.

**Key Points:**
- Trades execute instantly against the curve
- Price is deterministic based on supply
- 1% total fee (95% to creator, 5% to platform)
- Minimum trade: 0.0001 ETH
- Slippage protection via `slippageBps` parameter

## Trading Flow

```
1. Get Quote       →  Check price/impact before trading
2. Prepare TX      →  Get transaction calldata from API
3. Execute TX      →  Sign and broadcast with your wallet
4. Confirm         →  Wait for on-chain confirmation
```

## API Endpoints

### GET /tokens

List available tokens for trading.

**Request:**
```bash
curl "https://www.clawlaunch.fun/api/v1/tokens?limit=50" \
  -H "x-api-key: $CLAWLAUNCH_API_KEY"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| limit | number | 50 | Max results (1-100) |
| creator | address | - | Filter by creator |
| includeGraduated | boolean | false | Include graduated tokens |

**Response:**
```json
{
  "success": true,
  "tokens": [{
    "address": "0x...",
    "name": "Moon Token",
    "symbol": "MOON",
    "creator": "0x...",
    "price": "1000000000000000",
    "reserve": "500000000000000000",
    "totalSupply": "1000000000000000000000",
    "isGraduated": false,
    "createdAt": 1706745600
  }],
  "total": 42
}
```

### POST /token/quote

Get a price quote before trading. **Always call this first.**

**Request:**
```bash
curl -X POST https://www.clawlaunch.fun/api/v1/token/quote \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CLAWLAUNCH_API_KEY" \
  -d '{
    "tokenAddress": "0x...",
    "action": "buy",
    "amount": "1000000000000000000",
    "amountType": "eth"
  }'
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tokenAddress | address | Yes | Token contract address |
| action | string | Yes | "buy" or "sell" |
| amount | string | Yes | Amount in wei |
| amountType | string | No | "eth" (default for buy) or "token" |

**Response:**
```json
{
  "success": true,
  "quote": {
    "action": "buy",
    "tokenAddress": "0x...",
    "tokenName": "Moon Token",
    "tokenSymbol": "MOON",
    "inputAmount": "1000000000000000000",
    "outputAmount": "500000000000000000000000",
    "price": "2000000000000000",
    "priceImpact": "0.5",
    "fee": "10000000000000000",
    "humanReadable": "Buy ~500,000 MOON for 1.0 ETH"
  }
}
```

### POST /token/buy

Get transaction calldata to buy tokens.

**Request:**
```bash
curl -X POST https://www.clawlaunch.fun/api/v1/token/buy \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CLAWLAUNCH_API_KEY" \
  -d '{
    "tokenAddress": "0x...",
    "walletAddress": "0x...",
    "ethAmount": "1000000000000000000",
    "slippageBps": 200
  }'
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tokenAddress | address | Yes | Token contract address |
| walletAddress | address | Yes | Buyer's wallet address |
| ethAmount | string | Yes | ETH to spend (wei) |
| slippageBps | number | No | Slippage tolerance (default: 200 = 2%) |

**Response:**
```json
{
  "success": true,
  "transaction": {
    "to": "0x...",
    "data": "0x...",
    "value": "1000000000000000000",
    "chainId": 8453,
    "gas": "150000"
  },
  "quote": {
    "action": "buy",
    "inputAmount": "1000000000000000000",
    "outputAmount": "500000000000000000000000",
    "minOutputAmount": "490000000000000000000000",
    "slippageBps": 200
  },
  "humanReadableMessage": "Buy ~500,000 MOON for 1.0 ETH with 2% max slippage"
}
```

### POST /token/sell

Get transaction calldata to sell tokens.

**Request:**
```bash
curl -X POST https://www.clawlaunch.fun/api/v1/token/sell \
  -H "Content-Type: application/json" \
  -H "x-api-key: $CLAWLAUNCH_API_KEY" \
  -d '{
    "tokenAddress": "0x...",
    "walletAddress": "0x...",
    "tokenAmount": "500000000000000000000000",
    "slippageBps": 200,
    "sellAll": false
  }'
```

**Request Fields:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| tokenAddress | address | Yes | Token contract address |
| walletAddress | address | Yes | Seller's wallet address |
| tokenAmount | string | Conditional | Tokens to sell (required if sellAll=false) |
| slippageBps | number | No | Slippage tolerance (default: 200 = 2%) |
| sellAll | boolean | No | Sell entire balance (default: false) |

**Response:**
```json
{
  "success": true,
  "transaction": {
    "to": "0x...",
    "data": "0x...",
    "value": "0",
    "chainId": 8453,
    "gas": "150000"
  },
  "quote": {
    "action": "sell",
    "inputAmount": "500000000000000000000000",
    "outputAmount": "980000000000000000",
    "minOutputAmount": "960400000000000000",
    "slippageBps": 200
  },
  "humanReadableMessage": "Sell 500,000 MOON for ~0.98 ETH with 2% max slippage"
}
```

## Executing Transactions

The API returns transaction calldata that you execute with your wallet.

### Using viem (TypeScript)

```typescript
import { createWalletClient, http, parseEther } from 'viem';
import { base } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);
const client = createWalletClient({
  account,
  chain: base,
  transport: http(),
});

// Get buy calldata from API
const response = await fetch('https://www.clawlaunch.fun/api/v1/token/buy', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'x-api-key': process.env.CLAWLAUNCH_API_KEY!,
  },
  body: JSON.stringify({
    tokenAddress: '0x...',
    walletAddress: account.address,
    ethAmount: parseEther('0.1').toString(),
    slippageBps: 200,
  }),
});

const { transaction } = await response.json();

// Execute the transaction
const hash = await client.sendTransaction({
  to: transaction.to,
  data: transaction.data,
  value: BigInt(transaction.value),
  gas: BigInt(transaction.gas),
});

console.log('Transaction hash:', hash);
```

### Using ethers.js

```javascript
const { ethers } = require('ethers');

const provider = new ethers.JsonRpcProvider('https://mainnet.base.org');
const wallet = new ethers.Wallet(process.env.PRIVATE_KEY, provider);

// Get calldata from API...
const { transaction } = response;

const tx = await wallet.sendTransaction({
  to: transaction.to,
  data: transaction.data,
  value: transaction.value,
  gasLimit: transaction.gas,
});

await tx.wait();
console.log('Confirmed:', tx.hash);
```

## Slippage Protection

The `slippageBps` parameter protects against price changes between quote and execution.

| Value | Meaning | Recommendation |
|-------|---------|----------------|
| 100 | 1% | Low volatility tokens |
| 200 | 2% | Default, most tokens |
| 500 | 5% | High volatility tokens |
| 1000 | 10% | Maximum allowed |

**Example:** If you're buying tokens quoted at 1000 tokens:
- With `slippageBps: 200` (2%), minimum accepted is 980 tokens
- If price moves more than 2%, transaction reverts

## Fee Breakdown

**Total fee: 1%** of trade value

```
Trade: 1.0 ETH
├─ Total Fee: 0.01 ETH (1%)
│  ├─ Platform: 0.0005 ETH (0.05%)
│  └─ Creator: 0.0095 ETH (0.95%)
└─ Net to Curve: 0.99 ETH
```

Fees are deducted from the trade amount before bonding curve calculation.

## Graduated Tokens

Tokens graduate to Uniswap V3 when reserve reaches 5 ETH.

**What changes:**
- Trading moves from bonding curve to Uniswap V3
- API endpoints return `TOKEN_GRADUATED` error
- Use Uniswap interface or DEX aggregators instead

**Check graduation status:**
```bash
curl "https://www.clawlaunch.fun/api/v1/tokens?limit=1" \
  -H "x-api-key: $CLAWLAUNCH_API_KEY" | jq '.tokens[0].isGraduated'
```

## Rate Limits

| Endpoint | Limit | Window |
|----------|-------|--------|
| `/token/quote` | 100 | 1 minute |
| `/token/buy` | 50 | 1 hour |
| `/token/sell` | 50 | 1 hour |
| `/tokens` | 100 | 1 minute |

## Best Practices

1. **Always get a quote first** - Check price impact before trading
2. **Use appropriate slippage** - Higher for volatile tokens, lower for stable
3. **Check `isGraduated`** - Don't attempt trades on graduated tokens
4. **Validate addresses** - Ensure token and wallet addresses are correct
5. **Handle errors** - Implement retry logic for transient failures
6. **Monitor gas** - Base has low gas, but check network conditions
