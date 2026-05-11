---
name: chainbase-openapi-skill
description: Operate Chainbase indexed wallet and token reads through UXC with a curated OpenAPI schema, API-key auth, and read-first guardrails.
---

# Chainbase Web3 API Skill

Use this skill to run Chainbase indexed data operations through `uxc` + OpenAPI.

Reuse the `uxc` skill for shared execution, auth, and error-handling guidance.

## Prerequisites

- `uxc` is installed and available in `PATH`.
- Network access to `https://api.chainbase.online`.
- Access to the curated OpenAPI schema URL:
  - `https://raw.githubusercontent.com/holon-run/uxc/main/skills/chainbase-openapi-skill/references/chainbase-web3.openapi.json`
- A Chainbase API key.

## Scope

This skill covers a read-first indexed data surface:

- account native balance lookup
- account token balances
- account transaction history
- token metadata
- token holder reads
- token price lookup
- transaction detail lookup

This skill does **not** cover:

- raw chain RPC methods
- write or transaction submission flows
- the broader Chainbase data product surface beyond the selected Web3 API reads

## Authentication

Chainbase uses `X-API-KEY` header auth.

Configure one API-key credential and bind it to `api.chainbase.online`:

```bash
uxc auth credential set chainbase \
  --auth-type api_key \
  --api-key-header X-API-KEY \
  --secret-env CHAINBASE_API_KEY

uxc auth binding add \
  --id chainbase \
  --host api.chainbase.online \
  --scheme https \
  --credential chainbase \
  --priority 100
```

Validate the active mapping when auth looks wrong:

```bash
uxc auth binding match https://api.chainbase.online
```

## Core Workflow

1. Use the fixed link command by default:
   - `command -v chainbase-openapi-cli`
   - If missing, create it:
     `uxc link chainbase-openapi-cli https://api.chainbase.online --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/chainbase-openapi-skill/references/chainbase-web3.openapi.json`
   - `chainbase-openapi-cli -h`

2. Inspect operation schema first:
   - `chainbase-openapi-cli get:/v1/account/balance -h`
   - `chainbase-openapi-cli get:/v1/account/tokens -h`
   - `chainbase-openapi-cli get:/v1/token/metadata -h`

3. Prefer narrow account validation before broader reads:
   - `chainbase-openapi-cli get:/v1/account/balance chain_id=1 address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045`
   - `chainbase-openapi-cli get:/v1/token/price chain_id=1 contract_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`
   - `chainbase-openapi-cli get:/v1/tx/detail chain_id=1 tx_hash=0x4e3f3bc239f496f59c3e4d4a4d5f10f7f0d6d9f4cd790beeb520d05f6f7d98ae`

4. Execute with key/value parameters:
   - `chainbase-openapi-cli get:/v1/account/tokens chain_id=1 address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 page=1 limit=20`
   - `chainbase-openapi-cli get:/v1/token/holders chain_id=1 contract_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 page=1 limit=20`

## Operation Groups

### Account Reads

- `get:/v1/account/balance`
- `get:/v1/account/tokens`
- `get:/v1/account/txs`

### Token And Transaction Reads

- `get:/v1/token/metadata`
- `get:/v1/token/holders`
- `get:/v1/token/price`
- `get:/v1/tx/detail`

## Guardrails

- Keep automation on the JSON output envelope; do not use `--text`.
- Parse stable fields first: `ok`, `kind`, `protocol`, `data`, `error`.
- Treat this v1 skill as read-only. Do not imply RPC write methods, mempool send, or signing support.
- Chainbase has multiple product surfaces. This skill is intentionally limited to indexed HTTP reads on `https://api.chainbase.online`.
- Start with small `page` and `limit` values before building large crawls.
- `chainbase-openapi-cli <operation> ...` is equivalent to `uxc https://api.chainbase.online --schema-url <chainbase_openapi_schema> <operation> ...`.

## References

- Usage patterns: `references/usage-patterns.md`
- Curated OpenAPI schema: `references/chainbase-web3.openapi.json`
- Chainbase auth docs: https://docs.chainbase.com/quickstart/authenticate-your-api-key
- Chainbase Web3 API docs: https://docs.chainbase.com/api-reference/web3-api/balance
