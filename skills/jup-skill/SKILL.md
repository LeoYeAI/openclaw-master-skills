---
name: jupiter-skill
description: Execute Jupiter API operations on Solana - fetch quotes, sign transactions, execute swaps, prediction markets. Use when implementing token swaps, DCA, limit orders, lending, prediction markets, or any Jupiter integration. Includes scripts for Ultra and Metis swap flows.
metadata:
  primary_credential: JUP_API_KEY
  required_environment_variables:
    - JUP_API_KEY
  optional_environment_variables:
    - SOLANA_RPC_URL
  required_config_paths:
    - ~/.config/solana/id.json
  sensitive_inputs:
    - Solana wallet JSON file containing private key material
---

# Jupiter API Skill

Execute Jupiter API operations through 4 utility scripts for fetching data, signing transactions, and executing swaps on Solana.

**Base URL**: `https://api.jup.ag`

## Quick Reference

| Task | Script | Example |
|------|--------|---------|
| Fetch any Jupiter API | `fetch-api.ts` | `pnpm fetch-api -e /ultra/v1/search -p '{"query":"SOL"}'` |
| Sign a transaction | `wallet-sign.ts` | `pnpm wallet-sign -t "BASE64_TX" -w ~/.config/solana/id.json` |
| Execute Ultra order | `execute-ultra.ts` | `pnpm execute-ultra -r "REQUEST_ID" -t "SIGNED_TX"` |
| Send tx to RPC | `send-transaction.ts` | `pnpm send-transaction -t "SIGNED_TX"` |

## Setup

Install dependencies before using scripts:
```bash
cd /path/to/jup-skill
pnpm install
```

Run `pnpm install` once per clone (and again after dependency changes) before any `pnpm fetch-api`, `pnpm wallet-sign`, `pnpm execute-ultra`, or `pnpm send-transaction` command.

## API Key Setup

**ALWAYS required.** All Jupiter API endpoints require an `x-api-key` header.

1. Visit [portal.jup.ag](https://portal.jup.ag)
2. Create account and generate API key
3. Set via environment variable (recommended):
   ```bash
   export JUP_API_KEY=your_api_key_here
   ```
   Or pass via `--api-key` flag on each command.

## Wallet Safety

Signing requires access to a local Solana wallet JSON file (`--wallet`), which contains private key material.

- Do not use a high-value wallet for automation.
- Prefer a dedicated low-balance wallet for this workflow.
- For testing, prefer ephemeral keys.
- If your setup supports it, prefer hardware signing over raw key files.

## Scripts

### fetch-api.ts

Fetch data from any Jupiter API endpoint.

```bash
# Search for tokens
pnpm fetch-api -e /ultra/v1/search -p '{"query":"SOL"}'

# Get Ultra swap order (quote + unsigned transaction)
pnpm fetch-api -e /ultra/v1/order -p '{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "taker": "YOUR_WALLET_ADDRESS"
}'

# Get Metis quote
pnpm fetch-api -e /swap/v1/quote -p '{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "slippageBps": "50"
}'

# POST request (for Metis swap transaction)
pnpm fetch-api -e /swap/v1/swap -m POST -b '{
  "quoteResponse": {...},
  "userPublicKey": "YOUR_WALLET"
}'
```

**Arguments:**
- `-e, --endpoint` (required): API path, e.g., `/ultra/v1/order`
- `-p, --params`: Query params (GET) or body (POST) as JSON string
- `-b, --body`: Request body for POST requests
- `-m, --method`: HTTP method, `GET` (default) or `POST`
- `-k, --api-key`: API key (or use `JUP_API_KEY` env var)

### wallet-sign.ts

Sign transactions using a local wallet file.

> **SECURITY NOTE**: The `--wallet` flag is required. This script does not accept private keys via command line arguments to prevent exposure in shell history and process listings.

```bash
# Using Solana CLI wallet (JSON array format)
pnpm wallet-sign -t "BASE64_UNSIGNED_TX" --wallet ~/.config/solana/id.json

# Tilde expansion is supported
pnpm wallet-sign -t "BASE64_UNSIGNED_TX" --wallet ~/my-wallets/trading.json
```

**Arguments:**
- `-t, --unsigned-tx` (required): Base64-encoded unsigned transaction
- `-w, --wallet` (required): Path to Solana CLI JSON wallet file (supports ~ for home directory)

**Output:** Signed transaction (base64) to stdout.

### execute-ultra.ts

Execute Ultra orders after signing.

```bash
pnpm execute-ultra -r "REQUEST_ID_FROM_ORDER" -t "BASE64_SIGNED_TX"
```

**Arguments:**
- `-r, --request-id` (required): Request ID from `/ultra/v1/order` response
- `-t, --signed-tx` (required): Base64-encoded signed transaction
- `-k, --api-key`: API key (or use `JUP_API_KEY` env var)

**Output:** Execution result JSON including signature and status.

### send-transaction.ts

Send signed transactions to Solana RPC. **Use for Metis swaps** (Ultra handles RPC internally).

> **Warning**: The default public Solana RPC (`api.mainnet-beta.solana.com`) is rate-limited and unreliable for production use. Use a dedicated RPC provider (Helius, QuickNode, Triton, etc.) for production applications.

```bash
# Default RPC (mainnet-beta)
pnpm send-transaction -t "BASE64_SIGNED_TX"

# Custom RPC
pnpm send-transaction -t "BASE64_SIGNED_TX" -r "https://your-rpc.com"

# With environment variable
export SOLANA_RPC_URL="https://your-rpc.com"
pnpm send-transaction -t "BASE64_SIGNED_TX"
```

**Arguments:**
- `-t, --signed-tx` (required): Base64-encoded signed transaction
- `-r, --rpc-url`: RPC endpoint (default: `https://api.mainnet-beta.solana.com`)
- `--skip-preflight`: Skip preflight checks (faster, less safe)
- `--max-retries`: Max send retries (default: 3)

**Output:** Transaction signature to stdout.

---

## Workflows

### Ultra Swap (Recommended)

Ultra is RPC-less, gasless, with automatic slippage optimization.

```
Ultra Swap Progress:
- [ ] Step 1: Get order from /ultra/v1/order
- [ ] Step 2: Sign the transaction
- [ ] Step 3: Execute via /ultra/v1/execute
- [ ] Step 4: Verify result
```

**Step 1: Get Order**

```bash
ORDER=$(pnpm fetch-api -e /ultra/v1/order -p '{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "taker": "YOUR_WALLET_ADDRESS"
}')
echo "$ORDER"
```

Response contains `requestId` and `transaction` (base64 unsigned).

**Step 2: Sign Transaction**

Extract transaction from response and sign:

```bash
UNSIGNED_TX=$(echo "$ORDER" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
```

**Step 3: Execute Order**

```bash
REQUEST_ID=$(echo "$ORDER" | jq -r '.requestId')
pnpm execute-ultra -r "$REQUEST_ID" -t "$SIGNED_TX"
```

**Step 4: Verify**

Check the signature on [Solscan](https://solscan.io).

---

### Metis Swap (Advanced)

Use Metis when you need custom transaction composition or fine-grained control.

```
Metis Swap Progress:
- [ ] Step 1: Get quote from /swap/v1/quote
- [ ] Step 2: Build transaction via /swap/v1/swap
- [ ] Step 3: Sign the transaction
- [ ] Step 4: Send to RPC
- [ ] Step 5: Verify on-chain
```

**Step 1: Get Quote**

```bash
QUOTE=$(pnpm fetch-api -e /swap/v1/quote -p '{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "slippageBps": "50"
}')
```

**Step 2: Build Transaction**

```bash
SWAP_TX=$(pnpm fetch-api -e /swap/v1/swap -m POST -b "{
  \"quoteResponse\": $QUOTE,
  \"userPublicKey\": \"YOUR_WALLET_ADDRESS\",
  \"dynamicComputeUnitLimit\": true,
  \"prioritizationFeeLamports\": \"auto\"
}")
```

**Step 3: Sign**

```bash
UNSIGNED_TX=$(echo "$SWAP_TX" | jq -r '.swapTransaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" --wallet ~/.config/solana/id.json)
```

**Step 4: Send to RPC**

```bash
pnpm send-transaction -t "$SIGNED_TX" -r "https://your-rpc.com"
```

**Step 5: Verify**

Check signature on Solscan.

---

### Prediction Markets (Beta)

Trade on real-world event outcomes. Contracts trade $0-$1 USD, with prices reflecting outcome probability.

```
Prediction Market Flow:
- [ ] Step 1: Browse events/markets
- [ ] Step 2: Create order (buy YES/NO contracts)
- [ ] Step 3: Sign and send transaction
- [ ] Step 4: Monitor position
- [ ] Step 5: Claim winnings (if correct)
```

**Step 1: Browse Events**

```bash
# Search for events
pnpm fetch-api -e /prediction/v1/events/search -p '{"query":"election","limit":"10"}'

# List all events
pnpm fetch-api -e /prediction/v1/events -p '{"category":"politics","includeMarkets":"true"}'

# Get specific event with markets
pnpm fetch-api -e /prediction/v1/events/{eventId} -p '{"includeMarkets":"true"}'
```

**Step 2: Create Order**

```bash
# Buy YES contracts on a market
ORDER=$(pnpm fetch-api -e /prediction/v1/orders -m POST -b '{
  "ownerPubkey": "YOUR_WALLET_ADDRESS",
  "marketId": "MARKET_ID",
  "isYes": true,
  "isBuy": true,
  "contracts": 10,
  "maxBuyPriceUsd": 0.65
}')
```

Response contains `transaction` (base64 unsigned) and order details.

**Step 3: Sign and Send**

```bash
UNSIGNED_TX=$(echo "$ORDER" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
pnpm send-transaction -t "$SIGNED_TX" -r "YOUR_RPC_URL"
```

**Step 4: Monitor Position**

```bash
# List your positions
pnpm fetch-api -e /prediction/v1/positions -p '{"ownerPubkey":"YOUR_WALLET_ADDRESS"}'

# Get specific position
pnpm fetch-api -e /prediction/v1/positions/{positionPubkey}

# View order history
pnpm fetch-api -e /prediction/v1/history -p '{"ownerPubkey":"YOUR_WALLET_ADDRESS"}'
```

**Step 5: Claim Winnings**

After market resolves, claim payout for winning positions:

```bash
CLAIM=$(pnpm fetch-api -e /prediction/v1/positions/{positionPubkey}/claim -m POST -b '{
  "ownerPubkey": "YOUR_WALLET_ADDRESS"
}')
UNSIGNED_TX=$(echo "$CLAIM" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
pnpm send-transaction -t "$SIGNED_TX" -r "YOUR_RPC_URL"
```

**Prediction API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/prediction/v1/events` | List events with filters |
| GET | `/prediction/v1/events/search` | Search events by query |
| GET | `/prediction/v1/events/{eventId}` | Get event details |
| GET | `/prediction/v1/markets/{marketId}` | Get market details |
| GET | `/prediction/v1/orderbook/{marketId}` | Get orderbook |
| POST | `/prediction/v1/orders` | Create order (returns unsigned tx) |
| DELETE | `/prediction/v1/orders` | Close/cancel order |
| GET | `/prediction/v1/positions` | List user positions |
| DELETE | `/prediction/v1/positions/{positionPubkey}` | Sell position |
| POST | `/prediction/v1/positions/{positionPubkey}/claim` | Claim winnings |
| GET | `/prediction/v1/leaderboards` | View leaderboards |
| GET | `/prediction/v1/profiles/{ownerPubkey}` | User profile stats |

**Key Concepts**

- **Contracts**: Trade in units, each worth $0-$1 based on probability
- **YES/NO**: Binary outcomes - buy YES if you think event happens, NO otherwise
- **Settlement**: Winning contracts pay $1, losing contracts pay $0
- **No claim fees**: Winners receive full $1 per contract

---

### Jupiter Lend

Deposit tokens to earn yield or borrow against collateral.

**Deposit (Earn)**

```bash
# Get deposit transaction
DEPOSIT=$(pnpm fetch-api -e /lend/v1/earn/deposit -m POST -b '{
  "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "signer": "YOUR_WALLET_ADDRESS"
}')

# Sign and send
UNSIGNED_TX=$(echo "$DEPOSIT" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
pnpm send-transaction -t "$SIGNED_TX" -r "YOUR_RPC_URL"
```

**Withdraw**

```bash
WITHDRAW=$(pnpm fetch-api -e /lend/v1/earn/withdraw -m POST -b '{
  "asset": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "amount": "1000000",
  "signer": "YOUR_WALLET_ADDRESS"
}')
# Sign and send as above
```

---

### Portfolio API

Track DeFi positions, platform info, and staked JUP across Solana.

**Get Positions**

Fetch all positions for a wallet address across Jupiter products.

```bash
# Get all positions
pnpm fetch-api -e /portfolio/v1/positions/YOUR_WALLET_ADDRESS

# Filter by specific platforms
pnpm fetch-api -e /portfolio/v1/positions/YOUR_WALLET_ADDRESS -p '{"platforms":"jupiter-exchange,jupiter-governance"}'
```

Response includes:
- `elements`: Array of position types (Multiple, Liquidity, Leverage, BorrowLend, Trade)
- `tokenInfo`: Token metadata indexed by network and address
- `fetcherReports`: Status of each data fetcher

**Get Platforms**

List all available platforms tracked by the Portfolio API.

```bash
pnpm fetch-api -e /portfolio/v1/platforms
```

Response includes platform details:
- `id`: Platform identifier (e.g., `jupiter-exchange`)
- `name`: Display name
- `image`: Logo URL
- `description`: Platform summary
- `defiLlamaId`: DefiLlama reference
- `isDeprecated`: Whether platform is deprecated
- `tags`: Categorization tags
- `links`: Social/web links (website, discord, twitter, github, docs)

**Get Staked JUP**

Check staked JUP amounts and pending unstaking for a wallet.

```bash
pnpm fetch-api -e /portfolio/v1/staked-jup/YOUR_WALLET_ADDRESS
```

Response:
```json
{
  "stakedAmount": 15000.5,
  "unstaking": [
    {
      "amount": 500,
      "until": 1711000000000
    }
  ]
}
```

- `stakedAmount`: Total staked JUP
- `unstaking`: Pending unstakes with amount and completion timestamp (ms)

---

### Trigger API (Limit Orders)

Create orders that execute automatically when price conditions are met.

**Create Limit Order**

```bash
ORDER=$(pnpm fetch-api -e /trigger/v1/createOrder -m POST -b '{
  "inputMint": "So11111111111111111111111111111111111111112",
  "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "maker": "YOUR_WALLET_ADDRESS",
  "payer": "YOUR_WALLET_ADDRESS",
  "params": {
    "makingAmount": "1000000000",
    "takingAmount": "150000000",
    "expiredAt": null
  }
}')

# Sign and send
UNSIGNED_TX=$(echo "$ORDER" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
pnpm send-transaction -t "$SIGNED_TX" -r "YOUR_RPC_URL"
```

Parameters:
- `makingAmount`: Amount of input token to sell (in smallest units)
- `takingAmount`: Minimum amount of output token to receive
- `expiredAt`: Unix timestamp for expiration (null = no expiry)
- `slippageBps`: Optional slippage tolerance (0 = exact price only)

**Get Orders**

```bash
# Get active orders
pnpm fetch-api -e /trigger/v1/getTriggerOrders -p '{"user":"YOUR_WALLET","orderStatus":"active"}'

# Get order history
pnpm fetch-api -e /trigger/v1/getTriggerOrders -p '{"user":"YOUR_WALLET","orderStatus":"history","page":"1"}'
```

**Cancel Order**

```bash
# Cancel single order
CANCEL=$(pnpm fetch-api -e /trigger/v1/cancelOrder -m POST -b '{
  "maker": "YOUR_WALLET_ADDRESS",
  "order": "ORDER_ACCOUNT_ADDRESS",
  "computeUnitPrice": "auto"
}')
# Sign and send transaction

# Cancel all orders (batched in groups of 5)
CANCEL_ALL=$(pnpm fetch-api -e /trigger/v1/cancelOrders -m POST -b '{
  "maker": "YOUR_WALLET_ADDRESS",
  "computeUnitPrice": "auto"
}')
```

**Trigger API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trigger/v1/createOrder` | Create limit order |
| GET | `/trigger/v1/getTriggerOrders` | Get orders by wallet |
| POST | `/trigger/v1/cancelOrder` | Cancel single order |
| POST | `/trigger/v1/cancelOrders` | Cancel multiple orders (batched) |

**Fees**: 0.03% for stable pairs, 0.1% for other pairs.

---

### Recurring API (DCA)

Automate recurring token purchases at specified intervals.

**Create DCA Order**

```bash
ORDER=$(pnpm fetch-api -e /recurring/v1/createOrder -m POST -b '{
  "user": "YOUR_WALLET_ADDRESS",
  "inputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "outputMint": "So11111111111111111111111111111111111111112",
  "params": {
    "time": {
      "inAmount": "10000000",
      "numberOfOrders": 10,
      "interval": 86400,
      "minPrice": null,
      "maxPrice": null,
      "startAt": null
    }
  }
}')

# Sign and send
UNSIGNED_TX=$(echo "$ORDER" | jq -r '.transaction')
SIGNED_TX=$(pnpm wallet-sign -t "$UNSIGNED_TX" -w ~/.config/solana/id.json)
pnpm send-transaction -t "$SIGNED_TX" -r "YOUR_RPC_URL"
```

Parameters:
- `inAmount`: Total amount to spend (raw units)
- `numberOfOrders`: How many purchases to make
- `interval`: Seconds between purchases (86400 = daily)
- `minPrice`/`maxPrice`: Optional price bounds (null = any price)
- `startAt`: Unix timestamp to start (null = immediate)

**Get Orders**

```bash
# Get active DCA orders
pnpm fetch-api -e /recurring/v1/getRecurringOrders -p '{"user":"YOUR_WALLET","orderStatus":"active","recurringType":"time"}'

# Get order history
pnpm fetch-api -e /recurring/v1/getRecurringOrders -p '{"user":"YOUR_WALLET","orderStatus":"history","recurringType":"time","page":"1"}'
```

**Cancel Order**

```bash
CANCEL=$(pnpm fetch-api -e /recurring/v1/cancelOrder -m POST -b '{
  "user": "YOUR_WALLET_ADDRESS",
  "order": "ORDER_ACCOUNT_ADDRESS",
  "recurringType": "time"
}')
# Sign and send transaction
```

**Recurring API Endpoints**

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/recurring/v1/createOrder` | Create DCA order |
| GET | `/recurring/v1/getRecurringOrders` | Get orders by wallet |
| POST | `/recurring/v1/cancelOrder` | Cancel order |

**Fees**: 0.1% per execution. Token2022 tokens NOT supported.

---

## API Endpoints Reference

| Use Case | API | Endpoint |
|----------|-----|----------|
| Token swaps (default) | Ultra | `/ultra/v1/order`, `/ultra/v1/execute` |
| Swaps with control | Metis | `/swap/v1/quote`, `/swap/v1/swap` |
| Limit orders | Trigger | `/trigger/v1/createOrder`, `/trigger/v1/cancelOrder` |
| Get limit orders | Trigger | `/trigger/v1/getTriggerOrders` |
| DCA orders | Recurring | `/recurring/v1/createOrder`, `/recurring/v1/cancelOrder` |
| Get DCA orders | Recurring | `/recurring/v1/getRecurringOrders` |
| Token search | Ultra | `/ultra/v1/search` |
| Token holdings | Ultra | `/ultra/v1/holdings/{address}` |
| Token warnings | Ultra | `/ultra/v1/shield` |
| Token prices | Price | `/price/v3?ids={mints}` |
| Token metadata | Tokens | `/tokens/v2/search?query={query}` |
| Portfolio positions | Portfolio | `/portfolio/v1/positions/{address}` |
| Portfolio platforms | Portfolio | `/portfolio/v1/platforms` |
| Staked JUP | Portfolio | `/portfolio/v1/staked-jup/{address}` |
| Prediction markets | Prediction | `/prediction/v1/events`, `/prediction/v1/orders` |
| Lending deposit | Lend | `/lend/v1/earn/deposit` |
| Lending withdraw | Lend | `/lend/v1/earn/withdraw` |

---

## Caveats & Limitations

### API Key & Rate Limits

| Tier | Rate Limit |
|------|------------|
| Free | 60 requests/minute |
| Pro | Up to 30,000 requests/minute |
| Ultra | Dynamic scaling with executed swap volume |

Ultra rate limits increase as you execute more swaps. Base: 50 requests per 10-second window.

### Fees

| API | Fee |
|-----|-----|
| Ultra | 5-10 basis points per swap |
| Metis | No Jupiter fee (you pay gas) |

Integrators can add custom fees (50-255 bps). Jupiter takes 20% of integrator fees.

### Gasless Requirements

Ultra offers "gasless" swaps where Jupiter pays the transaction fees, but with important caveats:
- **User still needs SOL** for account rent (creating token accounts)
- **User must sign** the transaction (not truly "zero-touch")
- **Minimum trade amount**: ~$10 equivalent
- Automatic when taker has <0.01 SOL
- JupiterZ RFQ: market makers pay transaction fees

### Transaction Size Limit

Solana transactions are limited to **1232 bytes**. If you hit this:
- Reduce `maxAccounts` parameter in quote request
- Use `dynamicComputeUnitLimit: true` for Metis

### Token Limitations

- **Token2022**: NOT supported for Recurring (DCA) orders
- Some tokens may have transfer fees or freeze authority

### Ultra vs Metis

| Feature | Ultra | Metis |
|---------|-------|-------|
| RPC required | No (Jupiter handles) | Yes (your RPC) |
| Gasless | Yes (conditions apply) | No |
| Custom instructions | No | Yes |
| Transaction composition | No | Yes |
| Slippage | Auto-optimized | Manual |

**Use Ultra** for most swaps. **Use Metis** only when you need to add custom instructions or compose transactions.

### Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `TransactionExpiredBlockhashNotFound` | Blockhash expired | Request fresh order/quote |
| `SlippageToleranceExceeded` | Price moved too much | Increase slippage or retry |
| `InsufficientFunds` | Not enough SOL/tokens | Check balances |
| `RateLimited (429)` | Too many requests | Wait and retry, or upgrade tier |
| `InvalidSignature` | Wrong signer or corrupted tx | Verify wallet matches taker address |

### Ultra Execute Error Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| -1 to -5 | Client/validation errors |
| -1000 to -1999 | Aggregator routing errors |
| -2000 to -2999 | RFQ (market maker) errors |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `JUP_API_KEY` | Jupiter API key | (required) |
| `SOLANA_RPC_URL` | RPC endpoint for send-transaction | `https://api.mainnet-beta.solana.com` |

---

## Common Token Mints

| Token | Mint Address |
|-------|--------------|
| SOL (wrapped) | `So11111111111111111111111111111111111111112` |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |
| JUP | `JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN` |

---

## Resources

**Freshness note:** This skill includes Jupiter API guidance, but the API can change. After each new run/session, verify endpoints and params against the latest docs at [dev.jup.ag](https://dev.jup.ag).

### Docs URLs for Claude Sync

Check these first on each run/session:

- `https://dev.jup.ag/llms.txt`
- `https://dev.jup.ag/llms-full.txt`

Then verify workflow-specific pages:

- `https://dev.jup.ag/get-started/index.md`
- `https://dev.jup.ag/portal/setup.md`
- `https://dev.jup.ag/portal/rate-limit.md`
- `https://dev.jup.ag/portal/responses.md`
- `https://dev.jup.ag/docs/ultra/index.md`
- `https://dev.jup.ag/docs/ultra/get-started.md`
- `https://dev.jup.ag/docs/ultra/get-order.md`
- `https://dev.jup.ag/docs/ultra/execute-order.md`
- `https://dev.jup.ag/docs/ultra/response.md`
- `https://dev.jup.ag/docs/ultra/rate-limit.md`
- `https://dev.jup.ag/docs/ultra/search-token.md`
- `https://dev.jup.ag/docs/swap/index.md`
- `https://dev.jup.ag/docs/swap/get-quote.md`
- `https://dev.jup.ag/docs/swap/build-swap-transaction.md`
- `https://dev.jup.ag/docs/swap/send-swap-transaction.md`
- `https://dev.jup.ag/docs/swap/common-errors.md`
- `https://dev.jup.ag/updates/index.md`

Any Jupiter docs page can also be fetched as markdown by appending `.md` to the path.

- [Jupiter Portal](https://portal.jup.ag) - API key management
- [Jupiter Docs](https://dev.jup.ag) - Full documentation
- [Status Page](https://status.jup.ag) - API status
- [Solscan](https://solscan.io) - Transaction explorer
