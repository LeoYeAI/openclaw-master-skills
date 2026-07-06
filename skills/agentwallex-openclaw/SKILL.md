---
name: agentwallex-openclaw
description: Create and manage AI agents, send USDC/USDT payments, check balances across Ethereum, BSC, and Tron
homepage: https://agentwallex.com
emoji: 💳
metadata: {"openclaw": {"requires": {"bins": ["curl", "jq"], "configPaths": ["~/.openclaw/agentwallex/config.json"]}, "zeroConfig": false, "disableModelInvocation": false, "humanConfirmation": {"required": true, "actions": ["transfer", "pay"]}}}
---

# AgentWallex Payment Skill

## What It Does

The AgentWallex Payment skill gives AI agents core capabilities for managing agents and crypto payments:

- **Zero-config setup** — Set up AgentWallex through conversation. No config files or environment variables needed.
- **Create and manage agents** — Create, update, suspend, and delete AI agents with dedicated wallets.
- **Multi-chain support** — Operate across Ethereum, BSC, and Tron networks.
- **Check token balances** — Query available, locked, and pending balances for any agent wallet on supported chains.
- **Send outbound transfers** — Create and submit on-chain USDC/USDT transfers to any recipient address.
- **Query transaction status** — Track payment lifecycle from pending through confirmed or failed, with full tx hash details.

## Supported Chains & Tokens

### Mainnet

| Chain | Tokens | Address Format |
|-------|--------|----------------|
| Ethereum | USDC, USDT | `0x...` (42 chars) |
| BSC | USDC, USDT | `0x...` (42 chars) |
| Tron | USDT | `T...` (34 chars) |

### Sandbox (Testnet)

| Chain | Network | Tokens |
|-------|---------|--------|
| Ethereum | Sepolia | USDC, USDT |
| BSC | BSC Testnet | USDC, USDT |
| Tron | Nile Testnet | USDT |

**Start with sandbox** for development and testing. Sandbox transactions use testnet tokens and don't cost real money.

## Requirements

| Requirement | Details |
|---|---|
| System binaries | `curl`, `jq` |

No API key or environment variable is needed upfront — credentials are configured through conversation and stored locally.

## Setup

Install via ClawHub:

```bash
clawhub install agentwallex-openclaw
```

Then tell your AI agent:

```
"Set up AgentWallex"
```

The agent will use the `agentwallex_setup` tool and guide you through:

1. Opening the [AgentWallex Dashboard](https://app-sandbox.agentwallex.com) (sandbox) or [Production Dashboard](https://app.agentwallex.com)
2. Signing in with Google
3. Creating an API key (starts with `awx_`)
4. Copying your Agent ID
5. Pasting the credentials back — they're validated and saved automatically

Credentials are stored locally at `~/.openclaw/agentwallex/config.json` with owner-only permissions (0600). No environment variables needed.

### Reconfiguring

To change credentials or switch agents, just say:

```
"Reconfigure AgentWallex with my new API key awx_xxx and agent ID agent-123"
```

The agent will validate the new credentials and update the local config.

## Upgrade

Update to the latest version:

```bash
openclaw plugins update @agentwallex/agentwallex-openclaw
```

Or update all plugins at once:

```bash
openclaw plugins update --all
```

## Uninstall

```bash
openclaw plugins uninstall @agentwallex/agentwallex-openclaw
```

To keep plugin files on disk:

```bash
openclaw plugins uninstall @agentwallex/agentwallex-openclaw --keep-files
```

To also remove locally stored credentials:

```bash
rm -rf ~/.openclaw/agentwallex
```

## Available Tools

| Tool | Requires Config | Description |
|---|---|---|
| `agentwallex_setup` | No | Check configuration status and get setup instructions |
| `agentwallex_configure` | No | Validate and save API credentials |
| `agentwallex_create_agent` | Yes | Create a new AI agent with its own wallet |
| `agentwallex_list_agents` | Yes | List all agents and their status |
| `agentwallex_update_agent` | Yes | Update an agent's name or description |
| `agentwallex_delete_agent` | Yes | Delete an agent |
| `agentwallex_agent_status` | Yes | Update agent status (active / suspended) |
| `agentwallex_create_wallet` | Yes | Get or create a deposit address for the agent |
| `agentwallex_check_balance` | Yes | Check the agent's token balances (per chain) |
| `agentwallex_pay` | Yes | Send a payment to a recipient address |
| `agentwallex_tx_status` | Yes | Query the status of a transaction |
| `agentwallex_list_transactions` | Yes | List transactions with filtering |

## API Reference

### Environments

| Environment | Base URL | Description |
|---|---|---|
| **Sandbox** | `https://api-sandbox.agentwallex.com/api/v1` | Testing and development. Use sandbox API keys (`awx_sk_test_*`). |
| **Production** | `$AGENTWALLEX_BASE_URL` | Live environment. Use production API keys (`awx_sk_live_*`). |

**Start with sandbox** for development and testing. Switch to production when ready to go live.

```bash
# Set the base URL (default: sandbox)
export AGENTWALLEX_BASE_URL="https://api-sandbox.agentwallex.com/api/v1"
```

All requests require the API key header:

```
X-API-Key: <your-api-key>
```

### Response Format

**Success (single object):** Returns the object directly, no envelope.

```json
{
  "agent_id": "agent-a1b2c3",
  "agent_name": "payment-bot",
  "chain": "ethereum",
  "status": "active"
}
```

**Success (paginated list):**

```json
{
  "data": [ ... ],
  "total": 42,
  "has_more": true
}
```

**Error:**

```json
{
  "code": "not_found",
  "type": "not_found_error",
  "message": "Agent not found"
}
```

Error types: `validation_error` (400), `authentication_error` (401), `authorization_error` (403), `not_found_error` (404), `conflict_error` (409), `rate_limit_error` (429), `internal_error` (500), `service_unavailable` (503).

### Pagination Parameters

All list endpoints support:

| Parameter | Type | Default | Description |
|---|---|---|---|
| `page_num` | number | 1 | Page number |
| `page_size` | number | 20 | Items per page (max 100) |
| `sort` | string | `created_at` | Field to sort by |
| `order` | string | `desc` | Sort order: `asc` or `desc` |

### Create Agent

Creates a new AI agent with its own wallet on the specified chain. Returns `201 Created`.

```bash
curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "payment-bot",
    "chain": "ethereum",
    "agent_description": "Handles outbound payments"
  }' | jq
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_name` | string | yes | Name for the new agent |
| `chain` | string | yes | Blockchain network: `ethereum`, `bsc`, `tron` (mainnet) or `ethereum-sepolia`, `bsc-testnet`, `tron-nile` (sandbox) |
| `agent_description` | string | no | Optional description of the agent's purpose |
| `wallet_address` | string | no | Existing wallet address to associate |
| `metadata` | string | no | Arbitrary metadata string |

**Response** — An `Agent` object:

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | Unique agent identifier |
| `agent_name` | string | Agent name |
| `chain` | string | Blockchain network |
| `status` | string | Agent status (`active`, `inactive`, `suspended`) |
| `wallet_address` | string | Associated wallet address (if any) |
| `created_at` | string | ISO 8601 creation timestamp |

### List Agents

Lists all agents accessible to the current API key, with optional filtering.

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/agents?status=active&page_num=1&page_size=20" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq
```

**Query parameters:**

| Field | Type | Required | Description |
|---|---|---|---|
| `status` | string | no | Filter by status: `active`, `inactive`, `suspended` |
| `chain` | string | no | Filter by blockchain network |
| `page_num` | number | no | Page number (default: 1) |
| `page_size` | number | no | Items per page (default: 20) |
| `sort` | string | no | Sort field (default: `created_at`) |
| `order` | string | no | Sort order: `asc` or `desc` (default: `desc`) |

**Response** — A paginated list:

```json
{
  "data": [
    {
      "agent_id": "agent-a1b2c3",
      "agent_name": "payment-bot",
      "chain": "ethereum",
      "status": "active",
      "wallet_address": "0x...",
      "created_at": "2025-03-01T12:00:00Z"
    }
  ],
  "total": 1,
  "has_more": false
}
```

### Check Balance

Returns balances for a specific agent (one entry per chain/token).

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/agents/AGENT_ID/balance" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq
```

**Response** — An array of balance objects (one per chain/token):

| Field | Type | Description |
|---|---|---|
| `agent_id` | string | The agent identifier |
| `chain` | string | Blockchain network |
| `token` | string | Token symbol (`USDC` or `USDT`) |
| `available` | string | Available balance for spending |
| `locked` | string | Balance locked in pending transactions |
| `pending_income` | string | Incoming funds not yet confirmed |
| `total_deposited` | string | Lifetime deposited amount |
| `total_withdrawn` | string | Lifetime withdrawn amount |
| `total_paid` | string | Lifetime outbound payments |
| `total_earned` | string | Lifetime earned income |

### Get Deposit Address

Returns a deposit address for funding the agent wallet. EVM chains (Ethereum, BSC) share the same address.

```bash
curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents/AGENT_ID/deposit" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "chain": "ethereum"
  }' | jq
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `chain` | string | no | Target chain: `ethereum`, `bsc`, `tron` (defaults to `ethereum`) |

**Response:**

```json
{
  "agent_id": "AGENT_ID",
  "chain": "ethereum",
  "address": "0x..."
}
```

### Transfer

Initiates a transfer from an agent's wallet.

```bash
curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents/AGENT_ID/transfer" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "10.00",
    "to_address": "0xRecipientAddress",
    "chain": "ethereum",
    "token": "USDC"
  }' | jq
```

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `amount` | string | yes | Amount to transfer |
| `to_address` | string | yes | Recipient wallet address |
| `chain` | string | no | Target chain (defaults to `ethereum`) |
| `token` | string | no | Token to transfer: `USDC` or `USDT` (defaults to `USDC`) |

**Response:**

| Field | Type | Description |
|---|---|---|
| `transaction_id` | string | Transaction identifier |
| `amount` | string | Transferred amount |
| `to_address` | string | Recipient address |
| `chain` | string | Blockchain network |
| `tx_hash` | string | On-chain transaction hash (when available) |
| `status` | string | Transaction status |

### Get Transaction Status

Retrieves the current status and details of a transaction.

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/transactions/TRANSACTION_ID" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq
```

**Response:**

| Field | Type | Description |
|---|---|---|
| `transaction_id` | string | Transaction identifier |
| `status` | string | One of: `pending`, `completed`, `failed`, `cancelled` |
| `amount` | string | Transaction amount |
| `from_address` | string | Sender wallet address |
| `to_address` | string | Recipient wallet address |
| `token` | string | Token symbol (`USDC` or `USDT`) |
| `chain` | string | Blockchain network |
| `tx_hash` | string | On-chain transaction hash (when available) |
| `error_message` | string | Error details if status is `failed` |
| `confirmed_at` | string | ISO 8601 timestamp of confirmation |

### List Transactions

Lists transactions with optional filtering. Transactions are read-only.

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/transactions?agent_id=AGENT_ID&status=completed&page_num=1" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq
```

**Query parameters:**

| Field | Type | Required | Description |
|---|---|---|---|
| `agent_id` | string | no | Filter by agent |
| `status` | string | no | Filter by status |
| `direction` | string | no | Filter by direction: `inbound`, `outbound` |
| `page_num` | number | no | Page number (default: 1) |
| `page_size` | number | no | Items per page (default: 20) |

## Workflow Examples

### Flow 1: Check Balance, Send Payment, Verify Transaction

Step 1 — Check the agent's available balance:

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/agents/AGENT_ID/balance" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq '.[0].available'
```

Step 2 — Transfer funds (only if balance is sufficient):

```bash
TX=$(curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents/AGENT_ID/transfer" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "10.00",
    "to_address": "0xRecipientAddress",
    "chain": "ethereum",
    "token": "USDC"
  }')

TX_ID=$(echo "$TX" | jq -r '.transaction_id')
echo "Transaction ID: $TX_ID"
```

Step 3 — Check the transaction:

```bash
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/transactions?agent_id=AGENT_ID&status=completed" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq '.data[0]'
```

### Flow 2: Create Agent, Fund Wallet, Send Payment

Step 1 — Create a new agent:

```bash
AGENT=$(curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_name": "payment-bot",
    "chain": "ethereum",
    "agent_description": "Handles outbound payments"
  }')

AGENT_ID=$(echo "$AGENT" | jq -r '.agent_id')
echo "Agent ID: $AGENT_ID"
```

Step 2 — Get a deposit address for the new agent:

```bash
DEPOSIT=$(curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents/$AGENT_ID/deposit" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"chain": "ethereum"}')

echo "Deposit to: $(echo "$DEPOSIT" | jq -r '.address')"
```

Step 3 — After funding, check balance and transfer:

```bash
# Check balance
curl -s -X GET \
  "$AGENTWALLEX_BASE_URL/agents/$AGENT_ID/balance" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" | jq '.[0].available'

# Transfer USDC
curl -s -X POST \
  "$AGENTWALLEX_BASE_URL/agents/$AGENT_ID/transfer" \
  -H "X-API-Key: $AGENTWALLEX_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": "10.00",
    "to_address": "0xRecipientAddress",
    "chain": "ethereum",
    "token": "USDC"
  }' | jq
```

## Guardrails & Safety

When using this skill, you MUST follow these rules:

- **Never send to zero or null addresses.** Always validate that `to_address` is a non-empty, properly formatted address before creating a transaction.
- **Always check balance before sending.** Query the agent's available balance and confirm it covers the intended amount plus potential fees.
- **Verify transaction amounts are reasonable.** Before submitting, confirm the amount matches the intended payment. Reject or flag amounts that appear unusually large.
- **Confirm recipient address format.** For EVM chains (Ethereum, BSC): address starts with `0x` and is 42 characters. For Tron: address starts with `T` and is 34 characters.
- **Verify token support on chain.** Ethereum and BSC support USDC and USDT. Tron only supports USDT.

## Error Handling

| HTTP Status | Error Type | Description | Action |
|---|---|---|---|
| 400 | `validation_error` | Invalid request parameters | Check request body and fix validation errors |
| 401 | `authentication_error` | Invalid or missing API key | Run `agentwallex_setup` to reconfigure credentials |
| 403 | `authorization_error` | Insufficient permissions | Check API key scope and agent ownership |
| 404 | `not_found_error` | Resource does not exist | Verify the ID is correct and exists |
| 409 | `conflict_error` | Resource conflict | The resource already exists or has a conflict |
| 429 | `rate_limit_error` | Too many requests | Back off with exponential delay and retry |
| 500 | `internal_error` | Internal server error | Retry after a short delay |
| 503 | `service_unavailable` | Service temporarily unavailable | Retry after a short delay |

## Troubleshooting

| Problem | Solution |
|---|---|
| "AgentWallex is not configured yet" | Run `agentwallex_setup` to start the setup flow, then use `agentwallex_configure` to save credentials. |
| "Invalid API key format" | API keys must start with `awx_`. Get a valid key from the [Dashboard](https://app.agentwallex.com). |
| Balance shows 0 but funds were deposited | Deposits may take a few minutes to confirm on-chain. Wait and re-query. Also verify you are checking the correct chain. |
| Transaction stuck in `pending` | On-chain confirmation times vary. Poll the transaction status endpoint periodically. If stuck for over 10 minutes, check the chain's block explorer using the `tx_hash`. |
| `curl: command not found` | Install curl via your system package manager (`apt install curl`, `brew install curl`, etc.). |
| `jq: command not found` | Install jq via your system package manager (`apt install jq`, `brew install jq`, etc.). |
