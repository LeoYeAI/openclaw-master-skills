---
name: Vincent - Polymarket for agents
description: |
  Polymarket prediction market trading for agents. Use this skill when users want to create a
  Polymarket wallet, browse markets, place bets, manage positions, or withdraw funds.
  Triggers on "polymarket", "prediction market", "place bet", "browse markets", "trade prediction",
  "polymarket wallet", "betting", "market odds".
allowed-tools: Read, Write, Bash(npx:@vincentai/cli*)
version: 1.0.0
author: HeyVincent <contact@heyvincent.ai>
license: MIT
homepage: https://heyvincent.ai
source: https://github.com/HeyVincent-ai/Vincent
metadata:
  clawdbot:
    homepage: https://heyvincent.ai
    requires:
      config:
        - ${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/agentwallet
        - ./agentwallet
---

# Vincent - Polymarket for agents

Use this skill to create a Polymarket wallet for your agent and trade on prediction markets. Browse markets, place bets, track holdings, and manage orders — all without exposing private keys to the agent. Wallets use Gnosis Safe on Polygon with gasless trading through Polymarket's relayer.

**The agent never sees the private key.** All operations are executed server-side. The agent receives a scoped API key that can only perform actions permitted by the wallet owner's policies. The private key never leaves the Vincent server.

All commands use the `@vincentai/cli` package. API keys are stored and resolved automatically — you never handle raw keys or file paths.

## Security Model

This skill is designed for **autonomous agent trading with human oversight via server-side controls**. Understanding this model is important:

**No environment variables are required** because this skill uses agent-first onboarding: the agent creates its own Polymarket wallet at runtime by calling the Vincent API, which returns a scoped API key. There is no pre-existing credential to configure. The CLI stores the returned API key automatically during wallet creation. The config paths where the key is persisted (`${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/credentials/agentwallet/` or `./agentwallet/`) are declared in this skill's metadata.

**The agent's API key is not a private key.** It is a scoped Bearer token that can only execute actions within the policies set by the wallet owner. The Vincent server enforces all policies server-side — the agent cannot bypass them regardless of what it sends. If a trade violates a policy, the server rejects it. If a trade requires approval, the server holds it and notifies the wallet owner via Telegram for out-of-band human approval.

**Model invocation is intentionally enabled.** The purpose of this skill is to give AI agents autonomous Polymarket trading capabilities. The agent is expected to invoke trading actions (browse markets, place bets, manage positions) on its own, within the boundaries the human operator defines. The human controls what the agent can do through policies (spending limits, approval thresholds) — not by gating individual invocations. The stored key is scoped and policy-constrained — even if another process reads it, it can only perform actions the wallet owner's policies allow, and the owner can revoke it instantly.

**All API calls go exclusively to `heyvincent.ai`** over HTTPS/TLS. No other endpoints, services, or external hosts are contacted. The agent does not read, collect, or transmit any data beyond what is needed for Polymarket wallet operations.

**Key lifecycle:**

- **Creation**: The agent runs `secret create` — the CLI stores the API key automatically and returns a `keyId` and `claimUrl`.
- **Claim**: The human operator uses the claim URL to take ownership and configure policies at `https://heyvincent.ai`.
- **Revocation**: The wallet owner can revoke the agent's API key at any time from the Vincent frontend. Revoked keys are rejected immediately by the server.
- **Re-linking**: If the agent loses its API key, the wallet owner generates a one-time re-link token and the agent exchanges it for a new key via `secret relink`.
- **Rotation**: The wallet owner can revoke the current key and issue a re-link token to rotate credentials at any time.

## Quick Start

### 1. Check for Existing Keys

Before creating a new wallet, check if one already exists:

```bash
npx @vincentai/cli@latest secret list --type POLYMARKET_WALLET
```

If a key is returned, use its `id` as the `--key-id` for all subsequent commands. If no keys exist, create a new wallet.

### 2. Create a Polymarket Wallet

```bash
npx @vincentai/cli@latest secret create --type POLYMARKET_WALLET --memo "My prediction market wallet"
```

Returns `keyId` (use for all future commands), `claimUrl` (share with the user), and `walletAddress` (the EOA address; Safe is deployed lazily on first use).

After creating, tell the user:

> "Here is your wallet claim URL: `<claimUrl>`. Use this to claim ownership, set spending policies, and monitor your agent's wallet activity at https://heyvincent.ai."

**Important:** After creation, the wallet has no funds. The user must send **USDC.e (bridged USDC)** on Polygon to the Safe address before placing bets.

### 3. Get Balance

```bash
npx @vincentai/cli@latest polymarket balance --key-id <KEY_ID>
```

Returns:

- `walletAddress` — the Safe address (deployed on first call if needed)
- `collateral.balance` — USDC.e balance available for trading
- `collateral.allowance` — approved amount for Polymarket contracts

**Note:** The first balance call triggers Safe deployment and collateral approval (gasless via relayer). This may take 30-60 seconds.

### 4. Fund the Wallet

Before placing bets, the user must send USDC.e to the Safe address:

1. Get the wallet address from the balance command
2. Send USDC.e (bridged USDC, contract `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`) on Polygon to that address
3. Minimum $1 required per bet (Polymarket minimum)

**Do not send native USDC** (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`). Polymarket only accepts bridged USDC.e.

### 5. Transfer from Vincent EVM Wallet (Alternative Funding Method)

If you have a Vincent EVM wallet with funds, you can transfer directly to your Polymarket wallet using the wallet `transfer-between` commands (see the wallet skill). Vincent verifies you own both secrets and automatically handles token conversion and cross-chain bridging to get USDC.e on Polygon.

```bash
# Preview the transfer first (use your EVM wallet key-id)
npx @vincentai/cli@latest wallet transfer-between preview --key-id <EVM_KEY_ID> \
  --to-secret-id <POLYMARKET_SECRET_ID> --from-chain 8453 --to-chain 137 \
  --token-in 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 --amount 10 \
  --token-out 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --slippage 100

# Execute the transfer
npx @vincentai/cli@latest wallet transfer-between execute --key-id <EVM_KEY_ID> \
  --to-secret-id <POLYMARKET_SECRET_ID> --from-chain 8453 --to-chain 137 \
  --token-in 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 --amount 10 \
  --token-out 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --slippage 100
```

**Key points:**

- Use your **EVM wallet's key-id** (not the Polymarket key-id) for these commands
- The `--to-secret-id` must be your Polymarket wallet's secret ID
- For Polymarket destinations, only `--to-chain 137` (Polygon) and `--token-out 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` (USDC.e) are allowed
- The server verifies you own both secrets — transfers to other users' wallets are rejected
- For cross-chain transfers, check status with `wallet transfer-between status --key-id <EVM_KEY_ID> --relay-id <RELAY_REQUEST_ID>`

### 6. Browse & Search Markets

```bash
# Search markets by keyword (recommended)
npx @vincentai/cli@latest polymarket markets --key-id <KEY_ID> --query bitcoin --limit 20

# Search by Polymarket URL or slug
npx @vincentai/cli@latest polymarket markets --key-id <KEY_ID> --slug btc-updown-5m-1771380900

# Or use a full Polymarket URL as the slug parameter
npx @vincentai/cli@latest polymarket markets --key-id <KEY_ID> --slug https://polymarket.com/event/btc-updown-5m-1771380900

# Get all active markets
npx @vincentai/cli@latest polymarket markets --key-id <KEY_ID> --active --limit 50

# Get specific market by condition ID
npx @vincentai/cli@latest polymarket market --key-id <KEY_ID> --condition-id <CONDITION_ID>
```

**Market response includes:**

- `question`: The market question
- `outcomes`: Array like `["Yes", "No"]` or `["Team A", "Team B"]`
- `outcomePrices`: Current prices for each outcome
- `tokenIds`: **Array of token IDs for each outcome** — use these for placing bets
- `acceptingOrders`: Whether the market is open for trading
- `closed`: Whether the market has resolved

**Important:** Always use the `tokenIds` array from the market response. Each outcome has a corresponding token ID at the same index. For a "Yes/No" market:

- `tokenIds[0]` = "Yes" token ID
- `tokenIds[1]` = "No" token ID

### 7. Get Order Book

```bash
npx @vincentai/cli@latest polymarket orderbook --key-id <KEY_ID> --token-id <TOKEN_ID>
```

Returns bids and asks with prices and sizes. Use this to determine current market prices before placing orders.

### 8. Place a Bet

```bash
npx @vincentai/cli@latest polymarket bet --key-id <KEY_ID> --token-id <TOKEN_ID> --side BUY --amount 5 --price 0.55
```

Parameters:

- `--token-id`: The outcome token ID (from market data or order book)
- `--side`: `BUY` or `SELL`
- `--amount`: For BUY orders, USD amount to spend. For SELL orders, number of shares to sell.
- `--price`: Optional limit price (0.01 to 0.99). Omit for market order. ALWAYS use a market order unless the user specifies a limit price.

**BUY orders:**

- `amount` is the USD you want to spend (e.g., `5` = $5)
- You'll receive `amount / price` shares (e.g., $5 at 0.50 = 10 shares)
- Minimum order is $1

**SELL orders:**

- `amount` is the number of shares to sell
- You'll receive `amount * price` USD
- Must own the shares first (from a previous BUY)

**Important timing:** After a BUY fills, wait a few seconds before selling. Shares need time to settle on-chain.

If a trade violates a policy, the server returns an error explaining which policy was triggered. If a trade requires human approval (based on the approval threshold policy), the server returns `status: "pending_approval"` and the wallet owner receives a Telegram notification to approve or deny.

### 9. View Holdings, Open Orders & Trades

```bash
# Get current holdings with P&L (recommended for viewing positions)
npx @vincentai/cli@latest polymarket holdings --key-id <KEY_ID>

# Get open orders (unfilled limit orders in the order book)
npx @vincentai/cli@latest polymarket open-orders --key-id <KEY_ID>

# Filter open orders by market
npx @vincentai/cli@latest polymarket open-orders --key-id <KEY_ID> --market <CONDITION_ID>

# Get trade history
npx @vincentai/cli@latest polymarket trades --key-id <KEY_ID>
```

**Holdings** returns all positions with shares owned, average entry price, current price, and unrealized P&L. This is the best endpoint for:

- Checking current positions before placing sell orders
- Setting up stop-loss or take-profit rules
- Calculating total portfolio value and performance
- Showing the user their active bets

**Open Orders** returns unfilled limit orders waiting in the order book.

**Trades** returns historical trade activity.

### 10. Cancel Orders

```bash
# Cancel specific order
npx @vincentai/cli@latest polymarket cancel-order --key-id <KEY_ID> --order-id <ORDER_ID>

# Cancel all open orders
npx @vincentai/cli@latest polymarket cancel-all --key-id <KEY_ID>
```

### 11. Redeem Resolved Positions

After a market resolves, winning positions can be redeemed to convert conditional tokens back into USDC.e. Use the holdings command to check which positions have `redeemable: true`, then call redeem.

```bash
# Redeem all redeemable positions
npx @vincentai/cli@latest polymarket redeem --key-id <KEY_ID>

# Redeem specific markets by condition ID
npx @vincentai/cli@latest polymarket redeem --key-id <KEY_ID> --condition-ids 0xabc123,0xdef456
```

If no positions are redeemable, `redeemed` will be an empty array and no transaction is submitted.

**How it works:** Redemption is gasless (executed via Polymarket's relayer through the Safe). For standard markets, it calls `redeemPositions` on the CTF contract. For negative-risk markets, it calls `redeemPositions` on the NegRiskAdapter. Both types are handled automatically.

**When to redeem:** Check holdings periodically. After a market resolves, it may take some time before positions become redeemable. Look for `redeemable: true` in the holdings response.

### 12. Withdraw USDC

Transfer USDC.e from your Polymarket Safe to any Ethereum address on Polygon. This is gasless — executed via Polymarket's relayer.

```bash
npx @vincentai/cli@latest polymarket withdraw --key-id <KEY_ID> --to <RECIPIENT_ADDRESS> --amount <AMOUNT>
```

Parameters:

- `--to`: Recipient Ethereum address (0x..., 42 characters)
- `--amount`: Amount in USDC (human-readable, e.g. "100" = 100 USDC)

**Response:**

- `status`: `"executed"`, `"pending_approval"`, or `"denied"`
- `transactionHash`: Polygon transaction hash (only if executed)
- `walletAddress`: The Safe address that sent the funds

If the amount exceeds the wallet's USDC balance, the server returns an `INSUFFICIENT_BALANCE` error. Policy checks (spending limits, approval thresholds) apply to withdrawals the same way they apply to bets.

## Output Format

CLI commands return JSON to stdout. Market search results:

```json
{
  "markets": [
    {
      "question": "Will Bitcoin exceed $100k?",
      "outcomes": ["Yes", "No"],
      "outcomePrices": ["0.65", "0.35"],
      "tokenIds": ["123456...", "789012..."],
      "acceptingOrders": true
    }
  ]
}
```

Bet placement:

```json
{
  "orderId": "0x...",
  "status": "MATCHED",
  "side": "BUY",
  "price": "0.55",
  "size": "9.09"
}
```

For trades requiring human approval:

```json
{
  "status": "pending_approval",
  "message": "Transaction requires owner approval via Telegram"
}
```

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| `401 Unauthorized` | Invalid or missing API key | Check that the key-id is correct; re-link if needed |
| `403 Policy Violation` | Trade blocked by server-side policy | User must adjust policies at heyvincent.ai |
| `INSUFFICIENT_BALANCE` | Not enough USDC.e for the trade | Fund the wallet with USDC.e on Polygon |
| `429 Rate Limited` | Too many requests | Wait and retry with backoff |
| `pending_approval` | Trade exceeds approval threshold | User will receive Telegram notification to approve/deny |
| `No orderbook exists` | Market closed or wrong token ID | Verify `acceptingOrders: true` and use `tokenIds[]`, not `conditionId` |
| `Key not found` | API key was revoked or never created | Re-link with a new token from the wallet owner |

## Policies (Server-Side Enforcement)

The wallet owner controls what the agent can do by setting policies via the claim URL at `https://heyvincent.ai`. All policies are enforced server-side by the Vincent API — the agent cannot bypass or modify them. If a trade violates a policy, the API rejects it. If a trade triggers an approval threshold, the API holds it and sends the wallet owner a Telegram notification for out-of-band human approval.

| Policy                      | What it does                                                     |
| --------------------------- | ---------------------------------------------------------------- |
| **Spending limit (per tx)** | Max USD value per transaction                                    |
| **Spending limit (daily)**  | Max USD value per rolling 24 hours                               |
| **Spending limit (weekly)** | Max USD value per rolling 7 days                                 |
| **Require approval**        | Every transaction needs human approval via Telegram              |
| **Approval threshold**      | Transactions above a USD amount need human approval via Telegram |

Before the wallet is claimed, the agent can operate without policy restrictions. This is by design: agent-first onboarding allows the agent to begin trading immediately. Once the human operator claims the wallet via the claim URL, they can add any combination of policies to constrain the agent's behavior. The wallet owner can also revoke the agent's API key entirely at any time.

## Re-linking (Recovering API Access)

If the agent loses its API key, the wallet owner can generate a **re-link token** from the frontend. The agent then exchanges this token for a new scoped API key.

**How it works:**

1. The user generates a re-link token from the wallet detail page at `https://heyvincent.ai`
2. The user gives the token to the agent (e.g. by pasting it in chat)
3. The agent runs the relink command:

```bash
npx @vincentai/cli@latest secret relink --token <TOKEN_FROM_USER>
```

The CLI exchanges the token for a new API key, stores it automatically, and returns the new `keyId`. Use this `keyId` for all subsequent commands.

**Important:** Re-link tokens are one-time use and expire after 10 minutes, so it's safe for users to send you a relink token through chat since you will immediately consume it.

## Workflow Example

1. **Create wallet:**

   ```bash
   npx @vincentai/cli@latest secret create --type POLYMARKET_WALLET --memo "Betting wallet"
   ```

2. **Get Safe address (triggers deployment):**

   ```bash
   npx @vincentai/cli@latest polymarket balance --key-id <KEY_ID>
   # Returns walletAddress — give this to user to fund
   ```

3. **User sends USDC.e to the Safe address on Polygon**

4. **Search for a market:**

   ```bash
   # Search by keyword — returns only active, tradeable markets
   # Tip: use short keyword phrases; stop-words like "or" can cause empty results
   npx @vincentai/cli@latest polymarket markets --key-id <KEY_ID> --query "bitcoin up down" --active
   ```

5. **Check order book for the outcome you want:**

   ```bash
   npx @vincentai/cli@latest polymarket orderbook --key-id <KEY_ID> --token-id 123456...
   ```

6. **Place BUY bet using the correct token ID:**

   ```bash
   # tokenId must be from the tokenIds array, NOT the conditionId
   npx @vincentai/cli@latest polymarket bet --key-id <KEY_ID> --token-id 123456... --side BUY --amount 5 --price 0.55
   ```

7. **Wait for settlement** (a few seconds)

8. **Sell position:**

   ```bash
   npx @vincentai/cli@latest polymarket bet --key-id <KEY_ID> --token-id 123456... --side SELL --amount 9.09 --price 0.54
   ```

9. **Redeem after market resolves** (if holding through resolution):

   ```bash
   # Check holdings for redeemable positions
   npx @vincentai/cli@latest polymarket holdings --key-id <KEY_ID>
   # If redeemable: true, redeem to get USDC.e back
   npx @vincentai/cli@latest polymarket redeem --key-id <KEY_ID>
   ```

10. **Withdraw USDC to another wallet:**

    ```bash
    npx @vincentai/cli@latest polymarket withdraw --key-id <KEY_ID> --to 0xRecipientAddress --amount 50
    ```

## Important Notes

- **After any bet or trade**, share the user's Polymarket profile link so they can verify and view their positions: `https://polymarket.com/profile/<polymarketWalletAddress>` (use the wallet's Safe address).
- **No gas needed.** All Polymarket transactions are gasless via Polymarket's relayer.
- **Never try to access raw secret values.** The private key stays server-side — that's the whole point.
- Always share the claim URL with the user after creating a wallet.
- If a transaction is rejected, it may be blocked by a server-side policy. Tell the user to check their policy settings at `https://heyvincent.ai`.
- If a transaction requires approval, it will return `status: "pending_approval"`. The wallet owner will receive a Telegram notification to approve or deny.

See the **Error Handling** section above for a full list of common errors and resolutions.
