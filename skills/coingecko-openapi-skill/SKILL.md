---
name: coingecko-openapi-skill
description: Operate CoinGecko and GeckoTerminal market data APIs through UXC with a curated OpenAPI schema, API-key auth, and read-first guardrails.
---

# CoinGecko And GeckoTerminal Skill

Use this skill to run CoinGecko market data and GeckoTerminal onchain DEX operations through `uxc` + OpenAPI.

Reuse the `uxc` skill for shared execution, auth, and error-handling guidance.

## Prerequisites

- `uxc` is installed and available in `PATH`.
- Network access to `https://api.coingecko.com/api/v3`.
- Access to the curated OpenAPI schema URL:
  - `https://raw.githubusercontent.com/holon-run/uxc/main/skills/coingecko-openapi-skill/references/coingecko-market.openapi.json`
- A CoinGecko Demo API key.

## Scope

This skill covers a read-first market data surface:

- API liveness checks
- spot price lookup
- asset ID discovery
- market screener reads
- trending reads
- GeckoTerminal network discovery
- onchain token price lookup
- trending pool reads

This skill does **not** cover:

- paid or enterprise-only method families beyond the selected v1 scope
- historical chart or OHLC families
- portfolio, NFT, or onchain trade execution
- the full CoinGecko or GeckoTerminal API

## Authentication

The default host uses CoinGecko Demo auth with `x-cg-demo-api-key`.

Configure one API-key credential and bind it to `api.coingecko.com/api/v3`:

```bash
uxc auth credential set coingecko-demo \
  --auth-type api_key \
  --api-key-header x-cg-demo-api-key \
  --secret-env COINGECKO_DEMO_API_KEY

uxc auth binding add \
  --id coingecko-demo \
  --host api.coingecko.com \
  --path-prefix /api/v3 \
  --scheme https \
  --credential coingecko-demo \
  --priority 100
```

Validate the active mapping when auth looks wrong:

```bash
uxc auth binding match https://api.coingecko.com/api/v3
```

### Pro Host Override

If you have a Pro plan, keep the same curated schema and create a separate credential, binding, and link:

```bash
uxc auth credential set coingecko-pro \
  --auth-type api_key \
  --api-key-header x-cg-pro-api-key \
  --secret-env COINGECKO_PRO_API_KEY

uxc auth binding add \
  --id coingecko-pro \
  --host pro-api.coingecko.com \
  --path-prefix /api/v3 \
  --scheme https \
  --credential coingecko-pro \
  --priority 100

uxc link coingecko-pro-openapi-cli https://pro-api.coingecko.com/api/v3 \
  --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/coingecko-openapi-skill/references/coingecko-market.openapi.json
```

## Core Workflow

1. Use the fixed link command by default:
   - `command -v coingecko-openapi-cli`
   - If missing, create it:
     `uxc link coingecko-openapi-cli https://api.coingecko.com/api/v3 --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/coingecko-openapi-skill/references/coingecko-market.openapi.json`
   - `coingecko-openapi-cli -h`

2. Inspect operation schema first:
   - `coingecko-openapi-cli get:/simple/price -h`
   - `coingecko-openapi-cli get:/coins/markets -h`
   - `coingecko-openapi-cli get:/onchain/simple/networks/{network}/token_price/{addresses} -h`

3. Prefer narrow read validation before broader reads:
   - `coingecko-openapi-cli get:/ping`
   - `coingecko-openapi-cli get:/coins/list include_platform=false`
   - `coingecko-openapi-cli get:/onchain/networks`

4. Execute with key/value parameters:
   - `coingecko-openapi-cli get:/simple/price ids=bitcoin,ethereum vs_currencies=usd`
   - `coingecko-openapi-cli get:/coins/markets vs_currency=usd ids=bitcoin,ethereum order=market_cap_desc per_page=10 page=1`
   - `coingecko-openapi-cli get:/onchain/simple/networks/{network}/token_price/{addresses} network=eth addresses=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`

## Operation Groups

### Market Data

- `get:/ping`
- `get:/simple/price`
- `get:/coins/list`
- `get:/coins/markets`
- `get:/search/trending`

### GeckoTerminal Onchain Data

- `get:/onchain/networks`
- `get:/onchain/simple/networks/{network}/token_price/{addresses}`
- `get:/onchain/networks/trending_pools`

## Guardrails

- Keep automation on the JSON output envelope; do not use `--text`.
- Parse stable fields first: `ok`, `kind`, `protocol`, `data`, `error`.
- Treat this v1 skill as read-only. Do not imply wallet, trading, or portfolio mutation support.
- Demo and Pro hosts use different API-key headers. If the default Demo credential fails against the Pro host, create a separate Pro credential rather than reusing the Demo header name.
- The Pro host needs its own auth binding on `pro-api.coingecko.com/api/v3`; creating only a credential is not enough for linked calls to send `x-cg-pro-api-key`.
- CoinGecko public and Demo limits are tighter than Pro. Keep default examples narrow and avoid large paginated loops without explicit user intent.
- The GeckoTerminal endpoints in this schema share the same API root and auth flow as the rest of the curated CoinGecko host contract.
- `coingecko-openapi-cli <operation> ...` is equivalent to `uxc https://api.coingecko.com/api/v3 --schema-url <coingecko_openapi_schema> <operation> ...`.

## References

- Usage patterns: `references/usage-patterns.md`
- Curated OpenAPI schema: `references/coingecko-market.openapi.json`
- CoinGecko API docs: https://docs.coingecko.com/reference/endpoint-overview
- Authentication docs: https://docs.coingecko.com/reference/authentication
