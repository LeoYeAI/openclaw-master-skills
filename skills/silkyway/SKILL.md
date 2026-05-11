---
name: silkyway
version: 1.0.9
description: Agent banking and payments on Solana. Send and receive stablecoins with cancellable escrow transfers. Optional on-chain accounts with policy-enforced spending limits for human-delegated automation.
homepage: https://silkyway.ai
metadata: {"category":"payments","api_base":"https://api.silkyway.ai","author":"silkysquad","openclaw":{"requires":{"bins":["silk"]},"install":[{"id":"silk-npm","kind":"node","label":"Silk CLI","package":"@silkysquad/silk"}]}}
---

# SilkyWay

Agent banking and payments on Solana. Send and receive stablecoins — non-custodial, on-chain.

## Install

```bash
npm install -g @silkysquad/silk
```

Requires Node.js 18+.

## Setup

```bash
# 1. Initialize (creates wallet and agent ID)
silk init

# 2. Check your wallet address
silk wallet list
```

Your wallet and agent ID are saved at `~/.config/silkyway/config.json`. Your private key never leaves your machine. `silk init` is idempotent — safe to run multiple times.

### Cluster configuration

Default cluster is `mainnet-beta` (real USDC). Switch to `devnet` for testing with free tokens.

```bash
silk config set-cluster devnet    # test tokens
silk config set-cluster mainnet-beta  # real USDC
silk config get-cluster           # show current
```

| Cluster | API Base URL | Network |
|---------|-------------|---------|
| `mainnet-beta` | `https://api.silkyway.ai` | Mainnet (real USDC) |
| `devnet` | `https://devnet-api.silkyway.ai` | Devnet (test USDC) |

### Fund your wallet (devnet)

On devnet, use the faucet — it gives you 0.1 SOL (for transaction fees) + 100 USDC:

```bash
silk config set-cluster devnet
silk wallet fund
silk balance
```

On mainnet, send SOL and USDC to your wallet address manually. SOL is required for Solana transaction fees.

## Sending Payments

```bash
silk pay <recipient> <amount> [--memo <text>]
```

This locks USDC into on-chain escrow. The recipient claims it with `silk claim`, or you cancel for a full refund with `silk cancel`.

The output includes a **claim link** (`claimUrl`) — a URL you can share with the recipient's human. They open it in a browser, connect their wallet, and claim the payment. This is the easiest way for a non-technical recipient to claim.

```bash
# Send 10 USDC
silk pay 7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx 10 --memo "Payment for code review"

# Output includes claimUrl — share it with the recipient
# Example: https://app.silkyway.ai/transfers/9aE5kBqRvF3...?cluster=devnet

# Check your balance
silk balance

# View your transfers
silk payments list
silk payments get <transfer-pda>
```

### Claiming a payment

If someone sent you a payment:

```bash
silk payments list
silk claim <transfer-pda>
```

### Cancelling a payment

Cancel a payment you sent (before the recipient claims it):

```bash
silk cancel <transfer-pda>
```

## Address Book

Save contacts so you can send payments by name instead of address.

```bash
silk contacts add alice 7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx
silk contacts list
silk contacts get alice
silk contacts remove alice
```

Once saved, use names anywhere you'd use an address:

```bash
silk pay alice 10 --memo "Thanks for the review"
silk account send alice 5
```

Contact names are case-insensitive and stored lowercase. Saved at `~/.config/silkyway/contacts.json`.

## Multi-Wallet Support

```bash
silk wallet create second-wallet
silk wallet fund --wallet second-wallet
silk wallet list
```

Use `--wallet <label>` on any command to select a non-default wallet:

```bash
silk pay <address> 10 --wallet second-wallet
silk balance --wallet second-wallet
```

## Support Chat

```bash
silk chat "How do I send a payment?"
```

A persistent `agentId` (UUID) is auto-generated on first use for session continuity.

## On-Chain Accounts (Optional)

A SilkyWay account is an on-chain wallet — like a bank account — that a human owner creates and funds with USDC. The owner can add agents as **operators** with per-transaction spending limits enforced on-chain. This is useful for automations, recurring payments, or any scenario where a human wants to delegate spending authority to an agent with guardrails.

You don't need an account to use SilkyWay. Escrow payments (`silk pay`) work with just a wallet. Accounts are an optional upgrade when your human wants to give you direct spending access with on-chain controls.

**Key concepts:**
- **Owner** — The human who creates and funds the account. Full control: can transfer any amount, pause the account, add/remove operators.
- **Operator** — You (the agent). Authorized to send tokens from the account, subject to a per-transaction limit set by the owner.
- **Per-transaction limit** — Maximum USDC you can send in one transaction. Enforced on-chain — the Solana program rejects transactions that exceed it. A limit of 0 means unlimited.
- **Pause** — The owner can pause the account, blocking all operator transfers until unpaused. You cannot unpause it.

### Setting up an account

Your human creates the account — you cannot create it yourself.

1. Share the setup URL with your human (replace with your address from `silk wallet list`):
   ```
   https://app.silkyway.ai/account/setup?agent=YOUR_WALLET_ADDRESS
   ```
   They'll connect their wallet, set your spending limit, and fund the account.

   **Important:** Your human must select the same network (mainnet/devnet) on the setup page as your CLI cluster. If you're on devnet, tell them to switch to devnet before creating the account.

2. After your human creates the account, sync it:
   ```bash
   silk account sync
   ```

3. Check your status and send payments:
   ```bash
   silk account status
   silk account send <recipient> <amount>
   ```

If the amount exceeds your per-transaction limit, the transaction is **rejected on-chain** with `ExceedsPerTxLimit`. If the account is paused, you get `AccountPaused`.

If `silk account sync` returns "No account found", your human hasn't created the account yet — share the setup URL with them.

### Depositing and withdrawing

You can deposit tokens from your wallet into the account, or withdraw them back:

```bash
# Deposit 10 USDC from your wallet into the account
silk account deposit 10

# Withdraw 5 USDC from the account back to your wallet
silk account withdraw 5
```

`deposit` moves tokens from your wallet into the Silk account. `withdraw` is a convenience wrapper around `account send` where the recipient is your own wallet — it's subject to the same per-transaction limit as any other transfer.

### Viewing account activity

Query the audit trail for your account:

```bash
# List all events
silk account events

# Filter by event type
silk account events --type TRANSFER
silk account events --type DEPOSIT
```

Event types: `ACCOUNT_CREATED`, `ACCOUNT_CLOSED`, `DEPOSIT`, `TRANSFER`, `OPERATOR_ADDED`, `OPERATOR_REMOVED`, `PAUSED`, `UNPAUSED`.

### Multi-account behavior

If your wallet is an operator on multiple accounts (different owners added you), `silk account sync` picks one deterministically (sorted by PDA) and warns you. To target a specific account:

```bash
silk account sync --account <pda>
```

### Accounts vs escrow payments

| | Accounts | Escrow (`silk pay`) |
|---|---|---|
| **Setup required** | Human creates account + adds you as operator | None — just a funded wallet |
| **Spending limits** | Per-transaction limit enforced on-chain | No limits |
| **Recipient claims?** | No — direct transfer, tokens arrive immediately | Yes — recipient must `silk claim` |
| **Cancellable?** | No — transfer is instant | Yes — sender can cancel before claim |
| **Best for** | Ongoing payments with human oversight | One-off payments between parties |

If your human has set up an account for you, prefer `silk account send` — it's simpler (no claim step) and your human controls the spending limits.

## CLI Reference

| Command | Description |
|---------|-------------|
| `silk init` | Initialize CLI (create wallet, agent ID, and contacts file) |
| `silk wallet create [label]` | Create a new wallet |
| `silk wallet list` | List all wallets with addresses |
| `silk wallet fund [--sol] [--usdc] [--wallet <label>]` | Fund wallet from devnet faucet |
| `silk balance [--wallet <label>]` | Show SOL and USDC balances |
| `silk pay <recipient> <amount> [--memo <text>] [--wallet <label>]` | Send USDC payment into escrow |
| `silk claim <transfer-pda> [--wallet <label>]` | Claim a received payment |
| `silk cancel <transfer-pda> [--wallet <label>]` | Cancel a sent payment |
| `silk payments list [--wallet <label>]` | List transfers |
| `silk payments get <transfer-pda>` | Get transfer details |
| `silk contacts add <name> <address>` | Save a contact to the address book |
| `silk contacts remove <name>` | Remove a contact |
| `silk contacts list` | List all saved contacts |
| `silk contacts get <name>` | Look up a contact's address |
| `silk account sync [--wallet <label>] [--account <pda>]` | Discover and sync your on-chain account |
| `silk account status [--wallet <label>]` | Show account balance, spending limit, and pause state |
| `silk account events [--type <eventType>] [--wallet <label>]` | List account events (audit trail) |
| `silk account deposit <amount> [--wallet <label>]` | Deposit USDC from wallet into account |
| `silk account withdraw <amount> [--wallet <label>]` | Withdraw USDC from account back to your wallet |
| `silk account send <recipient> <amount> [--memo <text>] [--wallet <label>]` | Send from account (policy-enforced on-chain) |
| `silk chat <message>` | Ask SilkyWay support agent a question |
| `silk config set-cluster <cluster>` | Set cluster (`mainnet-beta` or `devnet`) |
| `silk config get-cluster` | Show current cluster and API URL |
| `silk config reset-cluster` | Reset cluster to default (`mainnet-beta`) |

Use `--wallet <label>` on any command to select a non-default wallet. Recipients accept contact names or Solana addresses.

## How Transactions Work

SilkyWay is non-custodial — your private keys never leave your machine.

Every payment follows a build-sign-submit flow:

1. **Build** — The SDK calls an API endpoint with payment details. The backend builds an unsigned Solana transaction and returns it as base64.
2. **Sign** — The SDK signs the transaction locally using your private key.
3. **Submit** — The SDK sends the signed transaction to the backend, which forwards it to Solana.

The backend handles Solana complexity (PDA derivation, instruction building, blockhash management). It never sees your private key — all authorization is enforced on-chain by the Solana program.

## API Endpoints

Base URL: `https://api.silkyway.ai` (mainnet) or `https://devnet-api.silkyway.ai` (devnet)

All requests use `Content-Type: application/json`.

### Escrow Endpoints

### POST /api/tx/create-transfer

Build an unsigned create_transfer transaction. Locks USDC into escrow.

**Request:**
```json
{
  "sender": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
  "recipient": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
  "amount": 10.00,
  "token": "usdc",
  "memo": "Payment for code review"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `sender` | string | yes | Sender's Solana public key |
| `recipient` | string | yes | Recipient's Solana public key |
| `amount` | number | yes | Amount in token units (e.g. `10.00` = 10 USDC) |
| `token` | string | yes | Token symbol (e.g. `"usdc"`) |
| `memo` | string | no | Human-readable memo |
| `claimableAfter` | number | no | Unix timestamp — recipient cannot claim before this time |

You can also pass `mint` (token mint pubkey) or `poolPda` directly instead of `token`, but `token` is the simplest option.

**Response:**
```json
{
  "ok": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAA...base64...AAAAAAA=",
    "transferPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
    "nonce": "1738900000000",
    "message": "Sign and submit via POST /api/tx/submit"
  }
}
```

The `transferPda` is the on-chain address for this escrow. Save it — you need it to claim or cancel.

### POST /api/tx/claim-transfer

Build an unsigned claim_transfer transaction. Moves USDC from escrow to the recipient's wallet.

Only the designated recipient can claim. If `claimableAfter` was set, the claim will fail before that time.

**Request:**
```json
{
  "transferPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
  "claimer": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transferPda` | string | yes | The transfer's on-chain PDA |
| `claimer` | string | yes | Recipient's Solana public key |

**Response:**
```json
{
  "ok": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAA...base64...AAAAAAA=",
    "message": "Sign and submit via POST /api/tx/submit"
  }
}
```

**Common errors:**
- `ClaimTooEarly` (6003) — `claimableAfter` hasn't passed yet
- `TransferAlreadyClaimed` (6000) — already claimed
- `TransferAlreadyCancelled` (6001) — sender cancelled first
- `Unauthorized` (6004) — claimer is not the designated recipient

### POST /api/tx/cancel-transfer

Build an unsigned cancel_transfer transaction. Refunds USDC from escrow back to the sender.

Only the original sender can cancel, and only while the transfer is still `ACTIVE` (not yet claimed).

**Request:**
```json
{
  "transferPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
  "canceller": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `transferPda` | string | yes | The transfer's on-chain PDA |
| `canceller` | string | yes | Sender's Solana public key |

**Response:**
```json
{
  "ok": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAA...base64...AAAAAAA=",
    "message": "Sign and submit via POST /api/tx/submit"
  }
}
```

**Common errors:**
- `TransferAlreadyClaimed` (6000) — recipient already claimed
- `TransferAlreadyCancelled` (6001) — already cancelled
- `Unauthorized` (6004) — canceller is not the original sender

### POST /api/tx/submit

Submit a signed transaction to Solana.

**Request:**
```json
{
  "signedTx": "AQAAAAAAAAAAAAAA...base64-signed...AAAAAAA="
}
```

**Response:**
```json
{
  "ok": true,
  "data": {
    "txid": "5UfDuXsrhFnxGZmyJxNR8z7Ee5JDFrgWHKPdTEJvoTpB3Qw8mKz4GQN1sxZWoGL"
  }
}
```

### GET /api/transfers/:pda

Get details for a single transfer.

**Example:** `GET /api/transfers/9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4`

**Response:**
```json
{
  "ok": true,
  "data": {
    "transfer": {
      "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "transferPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
      "sender": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
      "recipient": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
      "amount": "10000000",
      "amountRaw": "10000000",
      "status": "ACTIVE",
      "memo": "Payment for code review",
      "createTxid": "5UfDuXsrhFnxGZmyJxNR8z7Ee5JDFrgWHKPdTEJvoTpB",
      "claimTxid": null,
      "cancelTxid": null,
      "claimableAfter": null,
      "claimableUntil": null,
      "createdAt": "2025-02-07T12:00:00.000Z",
      "updatedAt": "2025-02-07T12:00:00.000Z",
      "token": { "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU", "symbol": "USDC", "decimals": 6 },
      "pool": { "poolPda": "3Fk8vMYJbCbEB2jzRCdRG9rFJhN2TCmPia9BjEKpTk5R", "feeBps": 50 }
    }
  }
}
```

Note: `amount` is in raw token units. USDC has 6 decimals, so `"10000000"` = 10.00 USDC.

### GET /api/transfers?wallet=\<pubkey\>

List all transfers where the wallet is sender or recipient.

**Example:** `GET /api/transfers?wallet=BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp`

**Response:**
```json
{
  "ok": true,
  "data": {
    "transfers": [
      {
        "transferPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
        "sender": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
        "recipient": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
        "amount": "10000000",
        "status": "ACTIVE",
        "memo": "Payment for code review",
        "createdAt": "2025-02-07T12:00:00.000Z",
        "token": { "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU", "symbol": "USDC", "decimals": 6 },
        "pool": { "poolPda": "3Fk8vMYJbCbEB2jzRCdRG9rFJhN2TCmPia9BjEKpTk5R", "feeBps": 50 }
      }
    ]
  }
}
```

### POST /api/tx/faucet

Airdrop devnet SOL or USDC. Devnet only.

**Request:**
```json
{
  "wallet": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
  "token": "usdc"
}
```

`token` is optional. Omit or use `"sol"` for SOL airdrop, `"usdc"` for USDC mint.

**Response:**
```json
{
  "ok": true,
  "data": {
    "amount": 0.1,
    "txid": "5UfDuXsrhFnxGZmyJxNR8z7Ee5JDFrgWHKPdTEJvoTpB3Qw8mKz4GQN1sxZWoGL"
  }
}
```

### Account Endpoints

#### GET /api/account/by-operator/:pubkey

Find accounts where your wallet is an operator. Used by `silk account sync`.

**Example:** `GET /api/account/by-operator/7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx`

**Response:**
```json
{
  "ok": true,
  "data": {
    "accounts": [
      {
        "pda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
        "owner": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
        "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
        "mintDecimals": 6,
        "isPaused": false,
        "balance": 10000000,
        "operatorSlot": {
          "index": 0,
          "perTxLimit": 5000000,
          "dailyLimit": 0
        }
      }
    ]
  }
}
```

Returns an empty array if no accounts found — this means your human hasn't set up your account yet.

#### GET /api/account/:pda

Get full account details. Used by `silk account status`.

**Example:** `GET /api/account/9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4`

**Response:**
```json
{
  "ok": true,
  "data": {
    "pda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
    "owner": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
    "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
    "mintDecimals": 6,
    "isPaused": false,
    "balance": 10000000,
    "operators": [
      {
        "pubkey": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
        "perTxLimit": 5000000,
        "dailyLimit": 0
      }
    ]
  }
}
```

Note: `balance` and `perTxLimit` are in raw token units. USDC has 6 decimals, so `5000000` = $5.00.

#### POST /api/account/transfer

Build an unsigned transfer transaction from a SilkyWay account. Used by `silk account send`.

**Request:**
```json
{
  "signer": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
  "accountPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
  "recipient": "Dg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx7xKXz9BpR3mFV",
  "amount": 3000000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `signer` | string | yes | Your wallet address (operator) |
| `accountPda` | string | yes | The account's on-chain PDA |
| `recipient` | string | yes | Recipient's Solana public key |
| `amount` | number | yes | Amount in raw token units (e.g. `3000000` = 3.00 USDC) |

**Response:**
```json
{
  "ok": true,
  "data": {
    "transaction": "AQAAAAAAAAAAAAAA...base64...AAAAAAA="
  }
}
```

Sign and submit the returned transaction via `POST /api/tx/submit`.

**Common errors:**
- `ExceedsPerTxLimit` — Amount exceeds your per-transaction spending limit
- `AccountPaused` — Account is paused by the owner; operator transfers blocked
- `Unauthorized` — Signer is not the owner or an operator on this account

#### POST /api/account/create

Build an unsigned create-account transaction. Used by the setup page (human-facing, not typically called by agents).

**Request:**
```json
{
  "owner": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
  "mint": "4zMMC9srt5Ri5X14GAgXhaHii3GnPAEERYPJgZJDncDU",
  "operator": "7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx",
  "perTxLimit": 5000000
}
```

#### POST /api/account/deposit

Build an unsigned deposit transaction. Used by `silk account deposit` and the setup page.

**Request:**
```json
{
  "depositor": "BrKz4GQN1sxZWoGLbNTojp4G3JCFLRkSYk3mSRWhKsXp",
  "accountPda": "9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4",
  "amount": 10000000
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `depositor` | string | yes | Wallet address depositing the tokens |
| `accountPda` | string | yes | The account's on-chain PDA |
| `amount` | number | yes | Amount in raw token units (e.g. `10000000` = 10.00 USDC) |

Sign and submit the returned transaction via `POST /api/tx/submit`.

#### GET /api/account/:pda/events

List audit trail events for an account. Used by `silk account events`.

**Example:** `GET /api/account/9aE5kBqRvF3mNcXz8BpR3mFVDg2Thh3AG6sFRPqNrDJ4/events`

**Query parameters:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `eventType` | string | no | Filter by event type: `ACCOUNT_CREATED`, `ACCOUNT_CLOSED`, `DEPOSIT`, `TRANSFER`, `OPERATOR_ADDED`, `OPERATOR_REMOVED`, `PAUSED`, `UNPAUSED` |

**Example with filter:** `GET /api/account/9aE5kBqRvF3.../events?eventType=TRANSFER`

### POST /chat

Send a message to the SilkyWay support agent. Returns an AI-generated response.

**Request:**
```json
{
  "agentId": "uuid-v4",
  "message": "How do I send a payment?"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `agentId` | string | yes | UUID v4 identifying the agent (auto-generated by the SDK) |
| `message` | string | yes | The question to ask |

**Response (200):**
```json
{
  "ok": true,
  "data": {
    "message": "Use silk pay...",
    "agentId": "uuid-v4"
  }
}
```

## Transfer Statuses

| Status | Description |
|--------|-------------|
| `ACTIVE` | Tokens locked in escrow, awaiting claim or cancellation |
| `CLAIMED` | Recipient claimed the tokens |
| `CANCELLED` | Sender cancelled and reclaimed the tokens |
| `EXPIRED` | Transfer expired past its `claimableUntil` window |

## Error Codes

### Escrow Program Errors (Handshake)

| Code | Name | Description |
|------|------|-------------|
| 6000 | `TransferAlreadyClaimed` | Transfer has already been claimed |
| 6001 | `TransferAlreadyCancelled` | Transfer has already been cancelled |
| 6002 | `TransferExpired` | Transfer has expired |
| 6003 | `ClaimTooEarly` | Cannot claim before `claimableAfter` timestamp |
| 6004 | `Unauthorized` | Signer is not authorized for this action |
| 6005 | `PoolPaused` | The token's escrow pool is temporarily paused — try again later |
| 6006 | `InsufficientFunds` | Sender has insufficient token balance |

### Account Program Errors (Silkysig)

| Code | Name | Description |
|------|------|-------------|
| 6000 | `Unauthorized` | Signer is not the owner or an operator on this account |
| 6001 | `ExceedsPerTxLimit` | Transfer amount exceeds operator's per-transaction spending limit |
| 6002 | `ExceedsDailyLimit` | Transfer exceeds operator daily limit (not yet enforced) |
| 6003 | `AccountPaused` | Account is paused — operator transfers blocked until owner unpauses |
| 6004 | `MaxOperatorsReached` | Account already has 3 operators (maximum) |
| 6005 | `OperatorNotFound` | Specified operator not found on account |
| 6006 | `OperatorAlreadyExists` | Operator is already on this account |
| 6007 | `InsufficientBalance` | Account doesn't have enough tokens for this transfer |
| 6008 | `MathOverflow` | Arithmetic overflow in calculation |

### API Errors

| Error | HTTP | Description |
|-------|------|-------------|
| `INVALID_PUBKEY` | 400 | Invalid Solana public key format |
| `INVALID_AMOUNT` | 400 | Amount must be positive |
| `MISSING_FIELD` | 400 | Required field not provided |
| `TRANSFER_NOT_FOUND` | 404 | No transfer found for the given PDA |
| `POOL_NOT_FOUND` | 404 | No escrow pool found for this token |
| `TOKEN_NOT_FOUND` | 400 | Token symbol or mint not recognized |
| `TX_FAILED` | 400 | Transaction simulation or submission failed |
| `RATE_LIMITED` | 429 | Too many faucet requests |
| `FAUCET_FAILED` | 400 | Faucet airdrop failed |

## Response Format

**Success:**
```json
{
  "ok": true,
  "data": { ... }
}
```

**Error:**
```json
{
   "ok": false,
   "error": "ERROR_CODE",
   "message": "Human-readable description"
}
```

## Security

- **Non-custodial** — the backend builds unsigned transactions; you sign locally with your private key before submitting
- Private keys are never transmitted to the server
- All authorization is enforced on-chain by the Solana program, not by the backend
- Keys are stored locally at `~/.config/silkyway/config.json` — never share this file
