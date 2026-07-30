# Addresses / Constants (Base Mainnet)

Chain:
- Chain ID: `8453` (Base mainnet)
- Default RPC: `https://mainnet.base.org` (override via `BASE_MAINNET_RPC`)

Diamond (Aavegotchi Baazaar entrypoint):
- `DIAMOND=0xA99c4B08201F2913Db8D28e71d020c4298F29dBF`

ERC20s:
- GHST (18 decimals): `GHST=0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB`
- USDC (6 decimals): `USDC=0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913`

Subgraph (Goldsky, no auth):
- `SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`

Recommended shell defaults (allow overrides):
```bash
export BASE_MAINNET_RPC="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
export DIAMOND="${DIAMOND:-0xA99c4B08201F2913Db8D28e71d020c4298F29dBF}"
export GHST="${GHST:-0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB}"
export USDC="${USDC:-0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913}"
export SUBGRAPH_URL="${SUBGRAPH_URL:-https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn}"
```

