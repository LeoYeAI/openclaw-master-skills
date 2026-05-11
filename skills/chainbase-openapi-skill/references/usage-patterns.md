# Chainbase Web3 API Skill - Usage Patterns

## Link Setup

```bash
command -v chainbase-openapi-cli
uxc link chainbase-openapi-cli https://api.chainbase.online \
  --schema-url https://raw.githubusercontent.com/holon-run/uxc/main/skills/chainbase-openapi-skill/references/chainbase-web3.openapi.json
chainbase-openapi-cli -h
```

## Auth Setup

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

Validate the binding:

```bash
uxc auth binding match https://api.chainbase.online
```

## Read Examples

```bash
# Read account native balance
chainbase-openapi-cli get:/v1/account/balance \
  chain_id=1 \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045

# Read account token balances
chainbase-openapi-cli get:/v1/account/tokens \
  chain_id=1 \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  page=1 \
  limit=20

# Read account transaction history
chainbase-openapi-cli get:/v1/account/txs \
  chain_id=1 \
  address=0xd8da6bf26964af9d7eed9e03e53415d37aa96045 \
  page=1 \
  limit=20

# Read token metadata
chainbase-openapi-cli get:/v1/token/metadata \
  chain_id=1 \
  contract_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48

# Read token holders
chainbase-openapi-cli get:/v1/token/holders \
  chain_id=1 \
  contract_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48 \
  page=1 \
  limit=20

# Read token price
chainbase-openapi-cli get:/v1/token/price \
  chain_id=1 \
  contract_address=0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48

# Read transaction detail
chainbase-openapi-cli get:/v1/tx/detail \
  chain_id=1 \
  tx_hash=0x4e3f3bc239f496f59c3e4d4a4d5f10f7f0d6d9f4cd790beeb520d05f6f7d98ae
```

## Fallback Equivalence

- `chainbase-openapi-cli <operation> ...` is equivalent to
  `uxc https://api.chainbase.online --schema-url <chainbase_openapi_schema> <operation> ...`.
