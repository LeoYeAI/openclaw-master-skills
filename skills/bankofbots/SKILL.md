---
name: bankofbots
description: >
  Trust scoring for AI agents. Log transactions and submit payment proofs to
  build a verifiable BOB Score — a trust score (think FICO but for AI Agents)
  that other agents and services can check to give them confidence before doing
  business with yours.
metadata: '{"openclaw":{"requires":{"env":["BOB_API_KEY","BOB_AGENT_ID"]},"optional":{"env":["BOB_API_URL"]},"primaryEnv":"BOB_API_KEY"}}'
---

## Setup

Download the latest `bob` binary from **https://github.com/bankofbots/bob-cli/releases/latest** and place it on your PATH.

You need these credentials for all API calls:
- `BOB_API_KEY` — your agent API key
- `BOB_AGENT_ID` — your agent ID
- `BOB_API_URL` — `https://api.bankofbots.ai/api/v1`

All commands output structured JSON with an `ok` field and `next_actions` that suggest follow-up commands.

**Supported rails: `lightning` and `onchain` (BTC only).** USD and USDC rails are not available.

## Core concepts

- **Agent**: An AI agent with its own identity, wallets, and spending policies
- **Wallet**: Holds a BTC balance on a specific rail (lightning or onchain)
- **Policy**: Spend limits, rate limits, and kill switches that constrain agent behavior
- **Transaction**: A record of money moving in or out of a wallet
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

# Get/set wallet budget (sats)
bob wallet budget get <agent-id> --wallet-id <id>
bob wallet budget set <agent-id> --wallet-id <id> --amount <sats>
```

`bob wallet list` includes a `bob_address` field when a default agent address is available.

### One-shot send (auto-quote + execute)

```bash
bob send <agent-id> <destination> --amount <sats> [--currency BTC]
```

Destination is auto-detected:
- `jade@bankofbots.ai` → routes as `bob_address` (BTC)
- `lnbc...` → Lightning invoice
- `bc1.../tb1...` → on-chain BTC address

| Flag | Description |
|---|---|
| `--amount` | Required. Satoshis |
| `--priority` | cheapest, fastest, or balanced (default: balanced) |
| `--description` | Optional payment note |
| `--max-fee` | Maximum acceptable fee in sats |
| `--rail` | Pin to lightning or onchain |
| `--destination-type` | Override auto-detection: `raw` or `bob_address` |

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
bob tx record <agent-id> --amount <sats> --currency BTC
```

| Flag | Description |
|---|---|
| `--amount` | Required. Satoshis |
| `--currency` | BTC (only supported currency) |
| `--rail` | lightning or onchain (default: auto) |
| `--endpoint` | Target endpoint or merchant identifier |
| `--wallet-id` | Specific wallet to debit (auto-selected if omitted) |

### Transfer BTC to another agent

```bash
bob tx transfer <from-agent-id> --to-agent-id <to-agent-id> --amount <sats> --currency BTC
```

| Flag | Description |
|---|---|
| `--to-agent-id` | Required. Destination agent ID |
| `--amount` | Required. Satoshis |
| `--description` | Optional note |

### Quote and execute payments (intent workflow)

The intent workflow quotes routes before executing, giving you visibility into fees, ETAs, and available rails.

```bash
# Quote routes for a payment
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
| `--amount` | Required. Satoshis |
| `--destination-type` | `raw` or `bob_address` |
| `--destination-ref` | Lightning invoice, on-chain address, or `alias@bankofbots.ai` |
| `--priority` | `cheapest`, `fastest`, or `balanced` (default: balanced) |
| `--execution-mode` | `auto` or `pinned` (default: auto) |
| `--rail` | Pin to `lightning` or `onchain` |
| `--wallet-id` | Pin to a specific wallet |
| `--max-fee` | Maximum acceptable fee in sats |

### Non-custodial proof submission

Submit proof of BTC payment to verify settlement and build your BOB Score:

```bash
# On-chain transaction proof
bob intent submit-proof <agent-id> <intent-id> --txid <txid>

# Lightning payment hash proof
bob intent submit-proof <agent-id> <intent-id> --payment-hash <hash>

# Lightning preimage proof (strongest verification)
bob intent submit-proof <agent-id> <intent-id> --preimage <hex> --proof-ref <payment-hash>

# With optional BOLT11 invoice for amount verification
bob intent submit-proof <agent-id> <intent-id> --preimage <hex> --proof-ref <payment-hash> --invoice <lnbc...>

# Historical proof import for credit building
bob agent credit-import <agent-id> --preimage <hex> --proof-ref <payment-hash> --amount <sats> --direction inbound --invoice <lnbc...>
```

| Proof Type | Description |
|---|---|
| `btc_onchain_tx` | On-chain transaction ID |
| `btc_lightning_payment_hash` | Lightning payment hash |
| `btc_lightning_preimage` | Lightning preimage (SHA256 verified against payment hash, strongest proof) |

### Query history

```bash
# Transactions
bob tx list <agent-id> --status complete --direction outbound --limit 10

# Transfers
bob tx transfers <agent-id>

# Spend summary
bob spend list <agent-id>
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

The BOB Score runs from 0–1000. New operators start at **350**. Tiers: **Legendary** (925+), **Elite** (800+), **Trusted** (650+, 1.5x limits), **Established** (500+, 1.2x limits), **Verified** (400+, 1.0x limits), **New** (300+, 1.0x limits), **Unverified** (150+, 0.6x limits), **Blacklisted** (0+, 0.6x limits). When credit tier enforcement is enabled, the tier multiplier adjusts spend and rate limits up or down from the base policy values.

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

Agent-scoped webhooks/events include payment intent lifecycle events (`quoted`, `executing`, `submitted`, `complete`, `failed`) so agents can react asynchronously without polling.

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

# List gates this agent has unlocked as a caller
bob gate my-unlocks <agent-id>

# Discover another agent's active gates
bob gate discover <agent-id>
```

| Flag | Description |
|---|---|
| `--name` | Required. Human-readable gate name |
| `--price` | Required. Minimum payment amount in sats |
| `--currency` | BTC |
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

Always check `ok` before using `data`. When `ok` is false, `data.error` contains the error message and `next_actions` provides recovery suggestions.

## Error recovery

When `ok` is false, `next_actions` provides context-aware recovery suggestions. Key patterns:

1. **Kill switch active**: STOP all transactions immediately. Run `bob policy list <agent-id>` to confirm.
2. **Spend/rate limit exceeded**: Check `bob spend list <agent-id>` to see current usage vs limits.
3. **Insufficient balance**: Check `bob wallet list <agent-id>` to see available funds.
4. **403 Forbidden**: Check `bob auth me` to verify your identity and role.
5. **409 Conflict**: Resource already exists (e.g., agent already registered). Do not retry — run `bob agent get <agent-id>` to confirm current state.

## Important rules

1. **Amounts** are always in satoshis (BTC).
2. **Policies** set by your operator constrain your spending. If a transaction is denied, `data.error` explains why. Do not retry denied transactions without changing the parameters.
3. **Kill switch**: If you receive a kill switch denial, stop all transaction attempts immediately. The operator has frozen your spending.
4. **next_actions**: Every response includes suggested follow-up commands. Use them to discover what to do next.
