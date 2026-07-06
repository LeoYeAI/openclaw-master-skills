---
name: Vincent - A wallet for agents
description: Use this skill to safely create a wallet the agent can use for transfers, swaps, and any EVM chain transaction.  Also supports raw signing and polymarket betting.
---

# Vincent - A wallet for agents

Use this skill to safely create a wallet the agent can use for transfers, swaps, and any EVM chain transaction without ever exposing private keys to the agent. Create a wallet, set spending policies, and your agent can transfer tokens, do swaps, and interact with smart contracts within the boundaries you define.

**The agent never sees the private key.** All transactions are executed server-side through a smart account. The wallet owner controls what the agent can do via configurable policies.

## Which Wallet Type to Use

| Type                | Use Case                                  | Network                 | Gas              |
| ------------------- | ----------------------------------------- | ----------------------- | ---------------- |
| `EVM_WALLET`        | Transfers, swaps, DeFi, contract calls    | Any EVM chain           | Sponsored (free) |
| `RAW_SIGNER`        | Raw message signing for special protocols | Any (Ethereum + Solana) | You pay          |
| `POLYMARKET_WALLET` | Prediction market trading                 | Polygon only            | Sponsored (free) |

**Choose `EVM_WALLET`** (default) for:

- Sending ETH or tokens
- Swapping tokens on DEXs
- Interacting with smart contracts
- Any standard EVM transaction

**Choose `RAW_SIGNER`** only when you need:

- Raw ECDSA/Ed25519 signatures for protocols that don't work with smart accounts
- To sign transaction hashes you'll broadcast yourself
- Solana signatures

**Choose `POLYMARKET_WALLET`** only for:

- Betting on Polymarket prediction markets
- Requires USDC.e on Polygon for funding

## Configuration

All API requests require a Bearer token (the API key returned when creating a wallet). If you're an openclaw instance, store and retrieve it from `~/.openclaw/credentials/agentwallet/<API_KEY_ID>.json`. Otherwise, you can store it in your current working directory at `agentwallet/<API_KEY_ID>.json`.

```
Authorization: Bearer <API_KEY>
```

## Quick Start

### 1. Create a Wallet

Create a new smart account wallet for your agent. This generates a private key server-side (you never see it), creates a ZeroDev smart account, and returns an API key for the agent plus a claim URL for the wallet owner.

```bash
curl -X POST "https://heyvincent.ai/api/secrets" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "EVM_WALLET",
    "memo": "My agent wallet",
    "chainId": 84532
  }'
```

Response includes:

- `apiKey` -- store this securely; use it as the Bearer token for all future requests
- `claimUrl` -- share this with the user so they can claim the wallet and set policies
- `address` -- the smart account address

After creating, tell the user:

> "Here is your wallet claim URL: `<claimUrl>`. Use this to claim ownership, set spending policies, and monitor your agent's wallet activity."

### 2. Get Wallet Address

```bash
curl -X GET "https://heyvincent.ai/api/skills/evm-wallet/address" \
  -H "Authorization: Bearer <API_KEY>"
```

### 3. Check Balances

```bash
# Get all token balances across all supported chains (ETH, WETH, USDC, etc.)
curl -X GET "https://heyvincent.ai/api/skills/evm-wallet/balances" \
  -H "Authorization: Bearer <API_KEY>"

# Filter to specific chains (comma-separated chain IDs)
curl -X GET "https://heyvincent.ai/api/skills/evm-wallet/balances?chainIds=1,137,42161" \
  -H "Authorization: Bearer <API_KEY>"
```

Returns all ERC-20 tokens and native balances with symbols, decimals, logos, and USD values.

### 4. Transfer ETH or Tokens

```bash
# Transfer native ETH
curl -X POST "https://heyvincent.ai/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "0.01"
  }'

# Transfer ERC-20 token
curl -X POST "https://heyvincent.ai/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "100",
    "token": "0xTokenContractAddress"
  }'
```

### 5. Swap Tokens

Swap one token for another using DEX liquidity (powered by 0x).

```bash
# Preview a swap (no execution, just pricing)
curl -X POST "https://heyvincent.ai/api/skills/evm-wallet/swap/preview" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "sellToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "sellAmount": "0.1",
    "chainId": 1
  }'

# Execute a swap
curl -X POST "https://heyvincent.ai/api/skills/evm-wallet/swap/execute" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "sellToken": "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE",
    "buyToken": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
    "sellAmount": "0.1",
    "chainId": 1,
    "slippageBps": 100
  }'
```

- `sellToken` / `buyToken`: Token contract addresses. Use `0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE` for native ETH.
- `sellAmount`: Human-readable amount to sell (e.g. `"0.1"` for 0.1 ETH).
- `chainId`: The chain to swap on (1 = Ethereum, 137 = Polygon, 42161 = Arbitrum, 10 = Optimism, 8453 = Base, etc.).
- `slippageBps`: Optional slippage tolerance in basis points (100 = 1%). Defaults to 100.

The preview endpoint returns expected buy amount, route info, and fees without executing. The execute endpoint performs the actual swap through the smart account, handling ERC20 approvals automatically.

### 6. Send Arbitrary Transaction

Interact with any smart contract by sending custom calldata.

```bash
curl -X POST "https://heyvincent.ai/api/skills/evm-wallet/send-transaction" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xContractAddress",
    "data": "0xCalldata",
    "value": "0"
  }'
```

## Policies

The wallet owner controls what the agent can do by setting policies via the claim URL. If a transaction violates a policy, the API will reject it or require human approval via Telegram.

| Policy                      | What it does                                                        |
| --------------------------- | ------------------------------------------------------------------- |
| **Address allowlist**       | Only allow transfers/calls to specific addresses                    |
| **Token allowlist**         | Only allow transfers of specific ERC-20 tokens                      |
| **Function allowlist**      | Only allow calling specific contract functions (by 4-byte selector) |
| **Spending limit (per tx)** | Max USD value per transaction                                       |
| **Spending limit (daily)**  | Max USD value per rolling 24 hours                                  |
| **Spending limit (weekly)** | Max USD value per rolling 7 days                                    |
| **Require approval**        | Every transaction needs human approval via Telegram                 |
| **Approval threshold**      | Transactions above a USD amount need human approval                 |

If no policies are set, all actions are allowed by default. Once the owner claims the wallet and adds policies, the agent operates within those boundaries.

## Re-linking (Recovering API Access)

If the agent loses its API key, the wallet owner can generate a **re-link token** from the frontend. The agent then exchanges this token for a new API key.

**How it works:**

1. The user generates a re-link token from the wallet detail page in the frontend
2. The user gives the token to the agent (e.g. by pasting it in chat)
3. The agent calls the re-link endpoint to exchange the token for a new API key

```bash
curl -X POST "https://heyvincent.ai/api/secrets/relink" \
  -H "Content-Type: application/json" \
  -d '{
    "relinkToken": "<TOKEN_FROM_USER>",
    "apiKeyName": "Re-linked API Key"
  }'
```

Response includes:

- `secret` -- the wallet metadata (id, type, address, chainId, etc.)
- `apiKey.key` -- the new API key to use as Bearer token for all future requests

**Important:** Re-link tokens are one-time use and expire after 10 minutes. No authentication is required on this endpoint -- the token itself is the authorization.

If a user tells you they have a re-link token, use this endpoint to regain access to the wallet. Store the returned API key and use it for all subsequent requests.

## Important Notes

- **No gas needed.** A paymaster is fully set up -- all transaction gas fees are sponsored automatically. The wallet does not need ETH for gas.
- **Never try to access raw secret values.** The private key stays server-side -- that's the whole point.
- Always store the API key from wallet creation. If you're an openclaw instance, store it in `~/.openclaw/credentials/agentwallet/<API_KEY_ID>.json`. Otherwise, you can store it in your current working directory at `agentwallet/<API_KEY_ID>.json`.
- Always search for the API keys in the credentials folder before using the API. If you're an openclaw instance, search for the API key in `~/.openclaw/credentials/agentwallet/<API_KEY_ID>.json`. Otherwise, you can search for the API key in your current working directory at `agentwallet/<API_KEY_ID>.json`.
- Always share the claim URL with the user after creating a wallet.
- If a transaction is rejected, it may be blocked by a policy. Tell the user to check their policy settings via the frontend at `https://heyvincent.ai`.
- If a transaction requires approval, it will return `status: "pending_approval"`. The wallet owner will receive a Telegram notification to approve or deny.

---

## Raw Signer (Advanced)

For raw ECDSA/Ed25519 signing when smart accounts won't work.

### Create a Raw Signer

```bash
curl -X POST "https://heyvincent.ai/api/secrets" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "RAW_SIGNER",
    "memo": "My raw signer"
  }'
```

Response includes both Ethereum (secp256k1) and Solana (ed25519) addresses derived from the same seed.

### Get Addresses

```bash
curl -X GET "https://heyvincent.ai/api/skills/raw-signer/addresses" \
  -H "Authorization: Bearer <API_KEY>"
```

Returns `ethAddress` and `solanaAddress`.

### Sign a Message

```bash
curl -X POST "https://heyvincent.ai/api/skills/raw-signer/sign" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "0x<hex-encoded-bytes>",
    "curve": "ethereum"
  }'
```

- `message`: Hex-encoded bytes to sign (must start with `0x`)
- `curve`: `"ethereum"` for secp256k1 ECDSA, `"solana"` for ed25519

Returns a hex-encoded signature. For Ethereum, this is `r || s || v` (65 bytes). For Solana, it's a 64-byte ed25519 signature.

---

## Polymarket Prediction Markets

Polymarket wallets use Gnosis Safe wallets on Polygon with gasless trading through Polymarket's relayer.

### Create a Polymarket Wallet

```bash
curl -X POST "https://heyvincent.ai/api/secrets" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "POLYMARKET_WALLET",
    "memo": "My prediction market wallet"
  }'
```

Response includes:

- `apiKey` -- use as Bearer token for all Polymarket requests
- `claimUrl` -- share with the user to claim ownership and set policies
- `walletAddress` -- the EOA address (Safe is deployed lazily on first use)

**Important:** After creation, the wallet has no funds. The user must send **USDC.e (bridged USDC)** on Polygon to the Safe address before placing bets.

### Get Balance

```bash
curl -X GET "https://heyvincent.ai/api/skills/polymarket/balance" \
  -H "Authorization: Bearer <API_KEY>"
```

Returns:

- `walletAddress` -- the Safe address (deployed on first call if needed)
- `collateral.balance` -- USDC.e balance available for trading
- `collateral.allowance` -- approved amount for Polymarket contracts

**Note:** The first balance call triggers Safe deployment and collateral approval (gasless via relayer). This may take 30-60 seconds.

### Fund the Wallet

Before placing bets, the user must send USDC.e to the Safe address:

1. Get the wallet address from `/balance` endpoint
2. Send USDC.e (bridged USDC, contract `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`) on Polygon to that address
3. Minimum $1 required per bet (Polymarket minimum)

**Do not send native USDC** (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`). Polymarket only accepts bridged USDC.e.

### Browse & Search Markets

```bash
# Search markets by keyword (recommended)
curl -X GET "https://heyvincent.ai/api/skills/polymarket/markets?query=bitcoin&limit=20" \
  -H "Authorization: Bearer <API_KEY>"

# Get all active markets (paginated)
curl -X GET "https://heyvincent.ai/api/skills/polymarket/markets?active=true&limit=50" \
  -H "Authorization: Bearer <API_KEY>"

# Get specific market by condition ID
curl -X GET "https://heyvincent.ai/api/skills/polymarket/market/<CONDITION_ID>" \
  -H "Authorization: Bearer <API_KEY>"
```

**Market response includes:**

- `question`: The market question
- `outcomes`: Array like `["Yes", "No"]` or `["Team A", "Team B"]`
- `outcomePrices`: Current prices for each outcome
- `tokenIds`: **Array of token IDs for each outcome** - use these for placing bets
- `acceptingOrders`: Whether the market is open for trading
- `closed`: Whether the market has resolved

**Important:** Always use the `tokenIds` array from the market response. Each outcome has a corresponding token ID at the same index. For a "Yes/No" market:

- `tokenIds[0]` = "Yes" token ID
- `tokenIds[1]` = "No" token ID

### Get Order Book

```bash
curl -X GET "https://heyvincent.ai/api/skills/polymarket/orderbook/<TOKEN_ID>" \
  -H "Authorization: Bearer <API_KEY>"
```

Returns bids and asks with prices and sizes. Use this to determine current market prices before placing orders.

### Place a Bet

```bash
curl -X POST "https://heyvincent.ai/api/skills/polymarket/bet" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "tokenId": "<OUTCOME_TOKEN_ID>",
    "side": "BUY",
    "amount": 5,
    "price": 0.55
  }'
```

Parameters:

- `tokenId`: The outcome token ID (from market data or order book)
- `side`: `"BUY"` or `"SELL"`
- `amount`: For BUY orders, USD amount to spend. For SELL orders, number of shares to sell.
- `price`: Limit price (0.01 to 0.99). Optional -- omit for market order.

**BUY orders:**

- `amount` is the USD you want to spend (e.g., `5` = $5)
- You'll receive `amount / price` shares (e.g., $5 at 0.50 = 10 shares)
- Minimum order is $1

**SELL orders:**

- `amount` is the number of shares to sell
- You'll receive `amount * price` USD
- Must own the shares first (from a previous BUY)

**Important timing:** After a BUY fills, wait a few seconds before selling. Shares need time to settle on-chain.

### View Positions & Orders

```bash
# Get open orders
curl -X GET "https://heyvincent.ai/api/skills/polymarket/positions" \
  -H "Authorization: Bearer <API_KEY>"

# Get trade history
curl -X GET "https://heyvincent.ai/api/skills/polymarket/trades" \
  -H "Authorization: Bearer <API_KEY>"
```

### Cancel Orders

```bash
# Cancel specific order
curl -X DELETE "https://heyvincent.ai/api/skills/polymarket/orders/<ORDER_ID>" \
  -H "Authorization: Bearer <API_KEY>"

# Cancel all open orders
curl -X DELETE "https://heyvincent.ai/api/skills/polymarket/orders" \
  -H "Authorization: Bearer <API_KEY>"
```

### Polymarket Workflow Example

1. **Create wallet:**

   ```bash
   POST /api/secrets {"type": "POLYMARKET_WALLET", "memo": "Betting wallet"}
   ```

2. **Get Safe address (triggers deployment):**

   ```bash
   GET /api/skills/polymarket/balance
   # Returns walletAddress -- give this to user to fund
   ```

3. **User sends USDC.e to the Safe address on Polygon**

4. **Search for a market:**

   ```bash
   # Search by keyword - returns only active, tradeable markets
   GET /api/skills/polymarket/markets?query=bitcoin&active=true
   ```

   Response example:

   ```json
   {
     "markets": [
       {
         "question": "Will Bitcoin hit $100k by end of 2025?",
         "outcomes": ["Yes", "No"],
         "outcomePrices": ["0.65", "0.35"],
         "tokenIds": ["123456...", "789012..."],
         "acceptingOrders": true
       }
     ]
   }
   ```

5. **Check order book for the outcome you want:**

   ```bash
   # Use the tokenId from the market response
   GET /api/skills/polymarket/orderbook/123456...
   # Note the bid/ask prices
   ```

6. **Place BUY bet using the correct token ID:**

   ```bash
   # tokenId must be from the tokenIds array, NOT the conditionId
   POST /api/skills/polymarket/bet
   {"tokenId": "123456...", "side": "BUY", "amount": 5, "price": 0.55}
   ```

7. **Wait for settlement** (a few seconds)

8. **Sell position:**
   ```bash
   POST /api/skills/polymarket/bet
   {"tokenId": "123456...", "side": "SELL", "amount": 9.09, "price": 0.54}
   ```

**Common Errors:**

- `"No orderbook exists for the requested token id"` - The market is closed or you're using the wrong ID. Make sure:
  - The market has `acceptingOrders: true`
  - You're using a `tokenId` from the `tokenIds` array, not the `conditionId`
  - The market hasn't already resolved
