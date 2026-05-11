---
name: upbit-openapi-skill
description: Operate Upbit public exchange market APIs through UXC with a curated OpenAPI schema, market-first discovery, and explicit private-auth boundary notes.
---

# Upbit Open API Skill

Use this skill to run Upbit public market-data operations through `uxc` + OpenAPI.

Reuse the `uxc` skill for shared execution, auth, and error-handling guidance.

## Prerequisites

- `uxc` is installed and available in `PATH`.
- Network access to the chosen Upbit regional API host.
- Access to the curated OpenAPI schema URL:
  - `https://raw.githubusercontent.com/holon-run/uxc/main/skills/upbit-openapi-skill/references/upbit-public.openapi.json`

## Scope

This skill covers a curated Upbit public surface for:

- market discovery
- ticker reads
- minute candles
- order book snapshots

This skill does **not** cover:

- private account or order endpoints in v1
- region-specific account/trade auth flows

## Endpoint

Upbit uses regional hosts. Pick the right one for the market you need before linking.

Examples:

- `https://sg-api.upbit.com`
- `https://id-api.upbit.com`
- `https://th-api.upbit.com`

## Authentication

Public market endpoints in this skill do not require credentials.

Upbit private APIs use provider-specific bearer JWT generation with request-specific claims. Keep this v1 skill public-data-only until a reusable Upbit signer flow exists in `uxc`.

## Core Workflow

1. Choose the correct regional host for the market you need.
2. Use a fixed link command by default:
   - `command -v upbit-openapi-cli`
   - If missing, create it:
     `uxc link upbit-openapi-cli https://sg-api.upbit.com --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/upbit-openapi-skill/references/upbit-public.openapi.json`
   - `upbit-openapi-cli -h`

3. Inspect operation help before execution:
   - `upbit-openapi-cli get:/v1/market/all -h`
   - `upbit-openapi-cli get:/v1/ticker -h`

4. Prefer narrow market reads first:
   - `upbit-openapi-cli get:/v1/ticker markets=SGD-BTC`
   - `upbit-openapi-cli get:/v1/orderbook markets=SGD-BTC`

## Operations

- `get:/v1/market/all`
- `get:/v1/ticker`
- `get:/v1/candles/minutes/{unit}`
- `get:/v1/orderbook`

## Guardrails

- Keep automation on the JSON output envelope; do not use `--text`.
- Parse stable fields first: `ok`, `kind`, `protocol`, `data`, `error`.
- Treat this v1 skill as read-only.
- Confirm the correct regional host and quote market before execution.
- On regional Upbit hosts, live market codes are quote-first, for example `SGD-BTC` and `USDT-BTC`.
- `upbit-openapi-cli <operation> ...` is equivalent to `uxc <upbit_region_host> --schema-url <upbit_public_openapi_schema> <operation> ...`.

## References

- Usage patterns: `references/usage-patterns.md`
- Curated OpenAPI schema: `references/upbit-public.openapi.json`
- Official Upbit Open API overview: https://global-docs.upbit.com/reference/api-overview
