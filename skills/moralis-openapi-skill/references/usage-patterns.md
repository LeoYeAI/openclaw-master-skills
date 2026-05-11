# Moralis Web3 Data API Skill - Usage Patterns

## Link Setup

```bash
command -v moralis-openapi-cli
uxc link moralis-openapi-cli https://deep-index.moralis.io/api/v2.2 \
  --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/moralis-openapi-skill/references/moralis-evm.openapi.json
moralis-openapi-cli -h
```

## Auth Setup

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

Validate the binding:

```bash
uxc auth binding match https://deep-index.moralis.io/api/v2.2
```

## Read Examples

```bash
# Read native balance
moralis-openapi-cli get:/{address}/balance \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  chain=eth

# Read wallet token balances
moralis-openapi-cli get:/wallets/{address}/tokens \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  chain=eth

# Read wallet history
moralis-openapi-cli get:/wallets/{address}/history \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  chain=eth \
  limit=20

# Read wallet swaps
moralis-openapi-cli get:/wallets/{address}/swaps \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  chain=eth \
  limit=20

# Read wallet net worth
moralis-openapi-cli get:/wallets/{address}/net-worth \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  chain=eth

# Read ERC-20 metadata
moralis-openapi-cli get:/erc20/metadata \
  chain=eth \
  addresses=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48

# Read ERC-20 token price
moralis-openapi-cli get:/erc20/{address}/price \
  address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 \
  chain=eth
```

## Fallback Equivalence

- `moralis-openapi-cli <operation> ...` is equivalent to
  `uxc https://deep-index.moralis.io/api/v2.2 --schema-url <moralis_openapi_schema> <operation> ...`.
