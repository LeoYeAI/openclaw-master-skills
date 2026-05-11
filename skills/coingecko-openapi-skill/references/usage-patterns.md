# CoinGecko And GeckoTerminal Skill - Usage Patterns

## Link Setup

```bash
command -v coingecko-openapi-cli
uxc link coingecko-openapi-cli https://api.coingecko.com/api/v3 \
  --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/coingecko-openapi-skill/references/coingecko-market.openapi.json
coingecko-openapi-cli -h
```

## Demo Auth Setup

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

Validate the binding:

```bash
uxc auth binding match https://api.coingecko.com/api/v3
```

## Pro Host Override

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

## Read Examples

```bash
# Confirm API liveness
coingecko-openapi-cli get:/ping

# Read spot prices for two assets
coingecko-openapi-cli get:/simple/price ids=bitcoin,ethereum vs_currencies=usd include_24hr_change=true

# Discover asset IDs
coingecko-openapi-cli get:/coins/list include_platform=false

# Read market screener rows
coingecko-openapi-cli get:/coins/markets vs_currency=usd ids=bitcoin,ethereum order=market_cap_desc per_page=10 page=1

# Read trending assets
coingecko-openapi-cli get:/search/trending

# List supported GeckoTerminal networks
coingecko-openapi-cli get:/onchain/networks

# Read onchain token prices for one network and one or more addresses
coingecko-openapi-cli get:/onchain/simple/networks/{network}/token_price/{addresses} \
  network=eth \
  addresses=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48

# Read trending pools across supported onchain networks
coingecko-openapi-cli get:/onchain/networks/trending_pools
```

## Fallback Equivalence

- `coingecko-openapi-cli <operation> ...` is equivalent to
  `uxc https://api.coingecko.com/api/v3 --schema-url <coingecko_openapi_schema> <operation> ...`.
