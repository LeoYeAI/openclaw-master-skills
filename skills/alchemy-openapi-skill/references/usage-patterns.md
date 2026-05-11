# Alchemy Prices API Skill - Usage Patterns

## Link Setup

```bash
command -v alchemy-openapi-cli
uxc link alchemy-openapi-cli https://api.g.alchemy.com \
  --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/alchemy-openapi-skill/references/alchemy-prices.openapi.json
alchemy-openapi-cli -h
```

## Auth Setup

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

Validate the binding:

```bash
uxc auth binding match https://api.g.alchemy.com
```

## Read Examples

```bash
# Read token prices by symbol
alchemy-openapi-cli get:/tokens/by-symbol symbols=ETH currency=USD

# Read token prices by contract address
alchemy-openapi-cli post:/tokens/by-address '{"addresses":[{"network":"eth-mainnet","address":"0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"}],"currency":"USD"}'

# Read historical token prices
alchemy-openapi-cli post:/tokens/historical '{"symbol":"ETH","startTime":"2025-01-01T00:00:00Z","endTime":"2025-01-07T00:00:00Z","interval":"1d","currency":"USD"}'
```

## Fallback Equivalence

- `alchemy-openapi-cli <operation> ...` is equivalent to
  `uxc https://api.g.alchemy.com --schema-url <alchemy_openapi_schema> <operation> ...`.

## Notes

- The live API can accept repeated `symbols=` query parameters, but this curated v1 schema keeps `get:/tokens/by-symbol` to one symbol per call so it remains directly executable through `uxc`.
