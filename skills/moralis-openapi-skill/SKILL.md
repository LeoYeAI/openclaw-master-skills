---
name: moralis-openapi-skill
description: Operate Moralis EVM wallet and token reads through UXC with a curated OpenAPI schema, API-key auth, and wallet-intelligence guardrails.
---

# Moralis Web3 Data API Skill

Use this skill to run Moralis EVM data operations through `uxc` + OpenAPI.

Reuse the `uxc` skill for shared execution, auth, and error-handling guidance.

## Prerequisites

- `uxc` is installed and available in `PATH`.
- Network access to `https://deep-index.moralis.io/api/v2.2`.
- Access to the curated OpenAPI schema URL:
  - `https://raw.githubusercontent.com/holon-run/uxc/main/skills/moralis-openapi-skill/references/moralis-evm.openapi.json`
- A Moralis API key.

## Scope

This skill covers a read-first wallet intelligence surface:

- native balance lookup
- wallet token balances
- wallet history
- wallet swaps
- wallet net worth
- ERC-20 metadata lookup
- ERC-20 token price lookup

This skill does **not** cover:

- write or transaction submission flows
- Solana, Streams, or NFT-specific surfaces
- the full Moralis API

## Authentication

Moralis uses `X-API-Key` header auth.

Configure one API-key credential and bind it to `deep-index.moralis.io/api/v2.2`:

```bash
uxc auth credential set moralis \
  --auth-type api_key \
  --api-key-header X-API-Key \
  --secret-env MORALIS_API_KEY

uxc auth binding add \
  --id moralis \
  --host deep-index.moralis.io \
  --path-prefix /api/v2.2 \
  --scheme https \
  --credential moralis \
  --priority 100
```

Validate the active mapping when auth looks wrong:

```bash
uxc auth binding match https://deep-index.moralis.io/api/v2.2
```

## Core Workflow

1. Use the fixed link command by default:
   - `command -v moralis-openapi-cli`
   - If missing, create it:
     `uxc link moralis-openapi-cli https://deep-index.moralis.io/api/v2.2 --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/moralis-openapi-skill/references/moralis-evm.openapi.json`
   - `moralis-openapi-cli -h`

2. Inspect operation schema first:
   - `moralis-openapi-cli get:/{address}/balance -h`
   - `moralis-openapi-cli get:/wallets/{address}/tokens -h`
   - `moralis-openapi-cli get:/erc20/{address}/price -h`

3. Prefer narrow reads before broader wallet scans:
   - `moralis-openapi-cli get:/{address}/balance address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 chain=eth`
   - `moralis-openapi-cli get:/erc20/{address}/price address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 chain=eth`
   - `moralis-openapi-cli get:/wallets/{address}/net-worth address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 chain=eth`

4. Execute with key/value parameters:
   - `moralis-openapi-cli get:/wallets/{address}/tokens address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 chain=eth`
   - `moralis-openapi-cli get:/wallets/{address}/history address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 chain=eth limit=20`

## Operation Groups

### Wallet Reads

- `get:/{address}/balance`
- `get:/wallets/{address}/tokens`
- `get:/wallets/{address}/history`
- `get:/wallets/{address}/swaps`
- `get:/wallets/{address}/net-worth`

### Token Reads

- `get:/erc20/metadata`
- `get:/erc20/{address}/price`

## Guardrails

- Keep automation on the JSON output envelope; do not use `--text`.
- Parse stable fields first: `ok`, `kind`, `protocol`, `data`, `error`.
- Treat this v1 skill as read-only. Do not imply signing or transaction broadcast support.
- Moralis supports multiple chains. Always pass `chain` explicitly instead of assuming Ethereum.
- Wallet history and swaps can become expensive at large ranges. Start with small limits and narrow time windows.
- `moralis-openapi-cli <operation> ...` is equivalent to `uxc https://deep-index.moralis.io/api/v2.2 --schema-url <moralis_openapi_schema> <operation> ...`.

## References

- Usage patterns: `references/usage-patterns.md`
- Curated OpenAPI schema: `references/moralis-evm.openapi.json`
- Moralis wallet docs: https://docs.moralis.com/data-api/evm/wallet
- Moralis token docs: https://docs.moralis.com/data-api/evm/token
