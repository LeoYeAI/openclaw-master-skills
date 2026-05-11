---
name: alchemy-openapi-skill
description: Operate Alchemy Prices API reads through UXC with a curated OpenAPI schema, path-templated API-key auth, and read-first guardrails.
---

# Alchemy Prices API Skill

Use this skill to run Alchemy Prices API operations through `uxc` + OpenAPI.

Reuse the `uxc` skill for shared execution, auth, and error-handling guidance.

## Prerequisites

- `uxc` is installed and available in `PATH`.
- Network access to `https://api.g.alchemy.com`.
- Access to the curated OpenAPI schema URL:
  - `https://raw.githubusercontent.com/holon-run/uxc/main/skills/alchemy-openapi-skill/references/alchemy-prices.openapi.json`
- An Alchemy API key.

## Scope

This v1 skill intentionally covers the narrow Prices API surface:

- token price lookup by symbol
- token price lookup by contract address
- historical token prices

This skill does **not** cover:

- node JSON-RPC
- NFT or portfolio APIs
- write operations
- the broader Alchemy API surface
- multi-symbol batch lookup in one `uxc` call

## Authentication

Alchemy Prices API places the API key in the request path: `/prices/v1/{apiKey}/...`.

Configure one API-key credential with a request path prefix template:

```bash
uxc auth credential set alchemy-prices \
  --auth-type api_key \
  --secret-env ALCHEMY_API_KEY \
  --path-prefix-template "/prices/v1/{{secret}}"

uxc auth binding add \
  --id alchemy-prices \
  --host api.g.alchemy.com \
  --scheme https \
  --credential alchemy-prices \
  --priority 100
```

Validate the active mapping when auth looks wrong:

```bash
uxc auth binding match https://api.g.alchemy.com
```

## Core Workflow

1. Use the fixed link command by default:
   - `command -v alchemy-openapi-cli`
   - If missing, create it:
     `uxc link alchemy-openapi-cli https://api.g.alchemy.com --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/alchemy-openapi-skill/references/alchemy-prices.openapi.json`
   - `alchemy-openapi-cli -h`

2. Inspect operation schema first:
   - `alchemy-openapi-cli get:/tokens/by-symbol -h`
   - `alchemy-openapi-cli post:/tokens/by-address -h`
   - `alchemy-openapi-cli post:/tokens/historical -h`

3. Start with narrow single-asset reads before batch historical requests:
   - `alchemy-openapi-cli get:/tokens/by-symbol symbols=ETH currency=USD`
   - `alchemy-openapi-cli post:/tokens/by-address '{"addresses":[{"network":"eth-mainnet","address":"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}],"currency":"USD"}'`

 4. Use positional JSON only for the POST endpoints:
   - `alchemy-openapi-cli post:/tokens/historical '{"symbol":"ETH","startTime":"2025-01-01T00:00:00Z","endTime":"2025-01-07T00:00:00Z","interval":"1d","currency":"USD"}'`

## Operations

- `get:/tokens/by-symbol`
- `post:/tokens/by-address`
- `post:/tokens/historical`

## Guardrails

- Keep automation on the JSON output envelope; do not use `--text`.
- Parse stable fields first: `ok`, `kind`, `protocol`, `data`, `error`.
- Treat this v1 skill as read-only and prices-only. Do not imply RPC, trade execution, or wallet mutation support.
- API keys are sensitive because they appear in the request path. Use `--secret-env` or `--secret-op`, not shell history literals, when possible.
- `/tokens/by-symbol` is query-based in the live API.
- The live API supports repeated `symbols=` parameters, but this v1 skill intentionally narrows that endpoint to a single `symbols=<TOKEN>` query because current `uxc` query argument handling does not reliably execute array-shaped query parameters.
- Historical requests can expand quickly. Keep time windows tight unless the user explicitly wants a larger backfill.
- `alchemy-openapi-cli <operation> ...` is equivalent to `uxc https://api.g.alchemy.com --schema-url <alchemy_openapi_schema> <operation> ...`.

## References

- Usage patterns: `references/usage-patterns.md`
- Curated OpenAPI schema: `references/alchemy-prices.openapi.json`
- Alchemy Prices API docs: https://www.alchemy.com/docs/reference/prices-api
- Prices API endpoints: https://www.alchemy.com/docs/reference/prices-api-endpoints
