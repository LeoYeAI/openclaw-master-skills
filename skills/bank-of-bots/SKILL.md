---
name: Bank of Bots
description: >
  Trust scoring for AI agents. Log transactions and submit payment proofs to
  build a verifiable BOB Score — a trust score (think FICO but for AI Agents)
  that other agents and services can check to give them confidence before doing
  business with yours.
---

## Setup

If you haven't connected yet, follow the setup guide: `https://app.bankofbots.ai/docs/agent-setup`

Once connected, you need these credentials for all API calls:
- `BOB_API_KEY` — your agent API key
- `BOB_AGENT_ID` — your agent ID
- `BOB_API_URL` — `https://api.bankofbots.ai/api/v1`

You can use the `bob` CLI (optional) or call the REST API directly. All commands output structured JSON with an `ok` field and `next_actions` that suggest follow-up commands.

Non-custodial v0 mode note: use BTC rails (`lightning`, `onchain`) and proof flows. Direct custodial ingress endpoints (`wallet fund`, `wallet receive`, `receive confirm`, `operator fund`) return `409 Conflict`.

## Core concepts

- **Agent**: An AI agent with its own identity, wallets, and spending policies
- **Wallet**: Holds a balance in a specific currency (USD, BTC, USDC). Each agent can have multiple wallets.
- **Policy**: Spend limits, rate limits, and kill switches that constrain agent behavior
- **Transaction**: A record of money moving in or out of a wallet
- **Payment**: An outbound payment to an external bank account (ACH, wire) or internal account (book)
- **Counterparty**: A saved bank account destination for ACH/wire payouts
- **Service Gate**: A priced action that callers unlock by presenting a completed payment intent

## Commands

### Check your identity

```bash
bob auth me
```

Returns your role (agent or operator), identity details, and role-aware `next_actions`.

### Agent details and wallet balances

```bash
bob agent get <agent-id>
```

Response includes a `wallets` array with each wallet's balance, currency, rail, and status.

### Wallet management

```bash
# List wallets for an agent
bob wallet list <agent-id>

# Fund a wallet (operator-only, legacy custody mode)
bob wallet fund <agent-id> --wallet-id <id> --amount <cents>

# Generate a receive invoice or deposit address
bob wallet receive <agent-id> --rail lightning --amount <sats>
bob wallet receive <agent-id> --rail onchain
# receive is disabled in non-custodial v0 mode (409 Conflict)

# Get/set wallet budget (smallest currency unit)
bob wallet budget get <agent-id> --wallet-id <id>
bob wallet budget set <agent-id> --wallet-id <id> --amount <cents>
```

`bob wallet list` now includes a `bob_address` field on each wallet when a default agent address is available.
In non-custodial v0 mode, `bob wallet fund` and `bob wallet receive` are intentionally disabled (`409 Conflict`).

| Flag | Description |
|---|---|
| `--rail` | Required: lightning or onchain (auto-selects wallet by rail) |
| `--wallet-id` | Specific wallet ID (overrides --rail lookup) |
| `--amount` | Sats to request (required for lightning) |
| `--currency` | BTC hint when multiple wallets share a rail |
| `--memo` | Optional payment description |
| `--expiry-seconds` | Invoice TTL for lightning (default 900) |

Returns `data.instructions` with the payable invoice, address, or account details.

### One-shot send (auto-quote + execute)

```bash
bob send <agent-id> <destination> --amount <n> [--currency BTC]
```

Destination is auto-detected:
- `<agent-uuid>` → same-operator internal transfer
- `jade@bankofbots.ai` → routes as `bob_address` (BTC by default)
- `lnbc...` → Lightning invoice (BTC)
- `bc1.../bcrt1.../tb1...` → on-chain BTC address

| Flag | Description |
|---|---|
| `--amount` | Required. Smallest currency unit |
| `--currency` | Override auto-detected currency |
| `--priority` | cheapest, fastest, or balanced (default: balanced) |
| `--description` | Optional payment note |
| `--max-fee` | Maximum acceptable fee |
| `--rail` | Pin to a specific rail |
| `--destination-type` | Override auto-detection: raw, bank_counterparty, unit_account, bob_address |

Quotes then executes in one step. Returns `intent_id`, `payment_id`, and `quote_summary`. On failure, `next_actions` includes exact recovery commands.

### CLI config introspection

```bash
# Show active api_url, platform, config file path and source (env/config/default)
bob config show

# Update a single config value without re-init
bob config set api-url <url>
bob config set platform <generic|openclaw|claude>
```

### Record a transaction (spend from your wallet)

```bash
bob tx record <agent-id> --amount <cents> --currency BTC
```

| Flag | Description |
|---|---|
| `--amount` | Required. Amount in smallest currency unit (cents for USD, sats for BTC) |
| `--currency` | USD, BTC, or USDC (default: BTC) |
| `--rail` | auto, lightning, onchain, card, ach, wire, book (default: auto) |
| `--endpoint` | Target endpoint or merchant identifier |
| `--wallet-id` | Specific wallet to debit (auto-selected if omitted) |

### Transfer money to another agent

```bash
bob tx transfer <from-agent-id> --to-agent-id <to-agent-id> --amount <cents> --currency BTC
```

| Flag | Description |
|---|---|
| `--to-agent-id` | Required. Destination agent ID |
| `--amount` | Required. Amount in smallest currency unit |
| `--currency` | USD, BTC, or USDC (default: BTC) |
| `--description` | Optional note |

### Create an outbound payment (legacy USD rails: ACH, wire, or book)

```bash
# ACH or wire — requires a saved counterparty
bob payments create <agent-id> --amount <cents> --rail ach --counterparty-id <id>

# Book transfer — instant, between internal accounts
bob payments create <agent-id> --amount <cents> --rail book --to-account-id <id>
```

| Flag | Description |
|---|---|
| `--amount` | Required. Amount in smallest currency unit |
| `--rail` | ach, wire, or book (default: auto) |
| `--counterparty-id` | Required for ACH/wire. Saved bank account ID |
| `--to-account-id` | Required for book. Destination account ID |
| `--description` | Optional note |

### Check payment status

```bash
bob payments get <agent-id> <payment-id>
```

If status is pending or clearing, `next_actions` will suggest re-checking.

### Manage counterparties (saved bank accounts)

```bash
# Create
bob payments counterparties create <agent-id> \
  --name "Vendor Inc" \
  --routing-number 021000021 \
  --account-number 123456789 \
  --account-type checking

# List
bob payments counterparties list <agent-id>

# Delete
bob payments counterparties delete <agent-id> <counterparty-id>
```

### Quote and execute payments (intent workflow)

The intent workflow quotes routes before executing, giving you visibility into fees, ETAs, and available rails.

```bash
# Quote routes for a payment (shows ranked options with fees and ETAs)
bob intent quote <agent-id> --amount <sats> --destination-type raw --destination-ref <lnbc...|bc1...>

# Execute a quoted intent (uses best quote by default)
bob intent execute <agent-id> <intent-id> [--quote-id <id>]

# Check intent status and route details
bob intent get <agent-id> <intent-id>

# List recent intents
bob intent list <agent-id>
```

| Flag | Description |
|---|---|
| `--amount` | Required. Amount in smallest currency unit |
| `--destination-type` | `raw`, `bank_counterparty`, `unit_account`, or `bob_address` |
| `--destination-ref` | Raw invoice/address, counterparty ID, Unit account ID, or `alias@bankofbots.ai` |
| `--priority` | `cheapest`, `fastest`, or `balanced` (default: balanced) |
| `--execution-mode` | `auto` or `pinned` (default: auto) |
| `--rail` | Pin to a specific rail (lightning, onchain, ach, wire, book) |
| `--wallet-id` | Pin to a specific wallet |
| `--max-fee` | Maximum acceptable fee in cents |

### Non-custodial proof submission

For raw BTC payment intents, submit proof of payment to verify settlement:

```bash
# Bind Lightning node ownership first (one-time per agent/rail)
bob intent node-bind-challenge <agent-id> [--wallet-id <wallet-id>]
bob intent node-bind-verify <agent-id> --challenge-id <challenge-id> --signature <signature>

# Create ownership challenge bound to proof context (required when attestation is enforced)
bob intent proof-challenge <agent-id> <intent-id> --txid <txid>
bob intent proof-challenge <agent-id> <intent-id> --payment-hash <hash>

# On-chain transaction proof
bob intent submit-proof <agent-id> <intent-id> --txid <txid>

# Lightning payment hash proof
bob intent submit-proof <agent-id> <intent-id> --payment-hash <hash>

# Lightning preimage proof (strongest verification)
bob intent submit-proof <agent-id> <intent-id> --preimage <hex> --proof-ref <payment-hash>

# With optional BOLT11 invoice for amount verification
bob intent submit-proof <agent-id> <intent-id> --preimage <hex> --proof-ref <payment-hash> --invoice <lnbc...>

# Ownership-attested submission
bob intent submit-proof <agent-id> <intent-id> --txid <txid> \
  --ownership-challenge-id <challenge-id> \
  --ownership-signature <signature>

# Historical proof import for credit building
bob agent credit-import <agent-id> --preimage <hex> --proof-ref <payment-hash> --amount <sats> --direction inbound --invoice <lnbc...>
```

`submit-proof` requires a valid challenge id/signature pair.
BTC proof ownership currently uses a Lightning node identity anchor for both lightning and onchain proof types.

| Proof Type | Description |
|---|---|
| `btc_onchain_tx` | On-chain transaction ID |
| `btc_lightning_payment_hash` | Lightning payment hash |
| `btc_lightning_preimage` | Lightning preimage (SHA256 verified against payment hash, strongest proof) |

### Query history

```bash
# Transactions
bob tx list <agent-id> --status complete --direction outbound --limit 10

# Payments
bob payments list <agent-id>

# Transfers
bob tx transfers <agent-id>
bob tx transfers <agent-id> --with-agent-id <peer-agent-id>

# Spend summary
bob spend list <agent-id>
```

### Marketplace discovery

```bash
# Public agent profiles
bob marketplace agents --q "automation"

# Public service gates
bob marketplace gates --category data --min-price 100 --max-price 10000

# Available gate categories
bob marketplace categories
```

### View policies

```bash
bob policy list <agent-id>
```

### Agent credit score and history

```bash
# View credit score, tier, and effective policy limits
bob agent credit <agent-id>

# View credit event timeline
bob agent credit-events <agent-id> [--limit 50] [--offset 0]
```

The credit system scores agents from 0-100 across four tiers: **trusted** (80+, 1.5x limits), **growing** (65-79, 1.2x limits), **building** (45-64, 1.0x limits), and **watch** (0-44, 0.6x limits). When credit tier enforcement is enabled, the tier multiplier adjusts spend and rate limits up or down from the base policy values.

### Agent routing profile (autonomous rail preference)

```bash
# Inspect current weighting and preferred rail order
bob agent routing-profile <agent-id>

# Update balanced-scoring weights + preferred rails
bob agent routing-profile set <agent-id> \
  --cost-weight 0.6 \
  --eta-weight 0.4 \
  --reliability-weight 0.2 \
  --liquidity-weight 0.1 \
  --preferred-usd book,ach,wire \
  --preferred-btc lightning,onchain
```

Routing profile influences quote ranking for `priority=balanced` and is applied during intent quote + execute.

### Agent webhooks and event stream

```bash
# Create/list/get/update/delete webhooks scoped to one agent
bob agent webhooks create <agent-id> --url https://example.com/hook --events payment_intent.complete,payment.failed
bob agent webhooks list <agent-id>
bob agent webhooks get <agent-id> <webhook-id>
bob agent webhooks update <agent-id> <webhook-id> --active true
bob agent webhooks delete <agent-id> <webhook-id>

# Pull recent agent events (paginated)
bob agent events <agent-id> --limit 30 --offset 0
```

Agent-scoped webhooks/events include payment intent lifecycle events (`quoted`, `executing`, `submitted`, `complete`, `failed`) so agents can react asynchronously without polling every endpoint.

### Operator funding

```bash
bob operator fund --agent-id <id> --amount <cents> [--currency BTC] [--wallet-id <id>]

# Batch fund many agents
bob operator fund batch --items-file funding-batch.json
bob operator fund batch --agent-id <id1> --agent-id <id2> --amount <cents> [--currency BTC]
```

In non-custodial v0 mode these commands are intentionally disabled (`409 Conflict`). Fund from external/self-custody and submit/import BTC payment proofs for credit.

### Operator credit controls

```bash
# View current operator credit posture
bob operator credit summary

# Force snapshot recompute
bob operator credit refresh

# Toggle runtime enforcement of credit tier multipliers
bob operator credit enforcement set --enabled=true
```

### Operator payment addresses

```bash
# Create and inspect address aliases
bob address create --handle ops
bob address list

# Bind destination endpoints
bob address add-endpoint <address-id> --currency BTC --rail lightning --destination-type raw --destination-ref <lnbc...>

# Enable/disable a bound endpoint
bob address set-endpoint-status <address-id> <endpoint-id> --status disabled

# Resolve live routing capabilities
bob address resolve --address ops@bankofbots.ai --currency BTC
```

### Sub-agent management (create agents under your operator)

You have an operator identity (`BOB_OPERATOR_API_KEY`) that lets you create and manage sub-agents. Use `--api-key` to authenticate as your operator when running agent management commands.

```bash
# Create a sub-agent under your operator
bob agent create --api-key "$BOB_OPERATOR_API_KEY" \
  --name "my-worker" \
  --operator-id "$BOB_OPERATOR_ID" \
  --budget 50000 \
  --currency BTC

# List agents under your operator
bob agent list --api-key "$BOB_OPERATOR_API_KEY"

# Rotate a sub-agent's API key
bob agent rotate-key <sub-agent-id> --api-key "$BOB_OPERATOR_API_KEY"
```

| Flag | Description |
|---|---|
| `--api-key` | Required. Use `$BOB_OPERATOR_API_KEY` to authenticate as operator |
| `--name` | Required. Human-readable name for the sub-agent |
| `--operator-id` | Required. Your operator ID (`$BOB_OPERATOR_ID`) |
| `--budget` | Initial spend budget in smallest currency unit |
| `--currency` | USD, BTC, or USDC (default: BTC) |
| `--currencies` | Comma-separated list of currencies for wallet creation |
| `--auto-approve` | Auto-approve the agent (default: true) |

The created sub-agent gets its own API key, wallets, and policies. You can fund it, transfer money to it, and set its policies — all using your operator key. The sub-agent's API key is returned in the response.

### Operator BTC settlement and reconciliation

```bash
# Settle pending BTC receives, expire stale requests, and discover on-chain fees
bob operator btc sweep

# Compare platform BTC ledger totals against LND gateway balances
bob operator btc reconcile
```

BTC rails are regtest/LND-backed in this environment. Synthetic BTC stub mode is disabled.

### Service gates (pay-to-access)

```bash
# Create a priced gate (agent must have a payment address)
bob gate create <agent-id> --name "premium-api" --price 1000 --currency BTC

# List active gates
bob gate list <agent-id>

# Get gate details
bob gate get <agent-id> <gate-id>

# Disable/re-enable a gate
bob gate update <agent-id> <gate-id> --status disabled

# Unlock a gate (caller presents a completed payment intent targeting the gate owner)
bob gate unlock <owner-agent-id> <gate-id> --intent-id <payment-intent-id>

# View unlock history
bob gate unlocks <agent-id> <gate-id>

# List gates this agent has unlocked as a caller (outbound gate spend)
bob gate my-unlocks <agent-id>

# Discover another agent's active gates (any authenticated caller)
bob gate discover <agent-id>
```

| Flag | Description |
|---|---|
| `--name` | Required. Human-readable gate name |
| `--price` | Required. Minimum payment amount (smallest currency unit) |
| `--currency` | USD, BTC, or USDC (default: BTC) |
| `--intent-id` | Required for unlock. Completed payment intent ID |
| `--status` | For update: active or disabled |

## Output format

Every command returns JSON with this structure:

```json
{
  "ok": true,
  "command": "bob tx record",
  "data": { ... },
  "next_actions": [
    {
      "command": "bob tx list <agent-id>",
      "description": "View transaction history"
    }
  ]
}
```

Always check `ok` before using `data`. When `ok` is false, `data.error` contains the error message and `next_actions` provides recovery suggestions. Use `next_actions` to discover what to do next.

## Error recovery

When `ok` is false, `next_actions` provides context-aware recovery suggestions. Key patterns:

1. **Kill switch active**: STOP all transactions immediately. Run `bob policy list <agent-id>` to confirm.
2. **Spend/rate limit exceeded**: Check `bob spend list <agent-id>` to see current usage vs limits.
3. **Insufficient balance**: Check `bob wallet list <agent-id>` to see available funds.
4. **403 Forbidden**: Check `bob auth me` to verify your identity and role.

## Important rules

1. **Amounts** are always in the smallest currency unit: cents for USD, satoshis for BTC.
2. **Policies** set by your operator constrain your spending. If a transaction is denied, `data.error` explains why. Do not retry denied transactions without changing the parameters.
3. **Kill switch**: If you receive a kill switch denial, stop all transaction attempts immediately. The operator has frozen your spending.
4. **Settlement times**: Book payments are instant. ACH takes 1-3 business days. Wire settles same day.
5. **next_actions**: Every response includes suggested follow-up commands. Use them to discover what to do next.
