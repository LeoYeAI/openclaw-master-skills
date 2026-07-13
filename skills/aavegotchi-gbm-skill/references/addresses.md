# Addresses / Constants (Base Mainnet)

Chain:
- Chain ID: `8453` (Base mainnet)
- Default RPC: `https://mainnet.base.org` (override via `BASE_MAINNET_RPC`)

GBM diamond (entrypoint for auctions):
- `GBM_DIAMOND=0x80320A0000C7A6a34086E2ACAD6915Ff57FfDA31`

ERC20s:
- GHST (18 decimals): `GHST=0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB`
- USDC (6 decimals): `USDC=0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913`

Subgraph (Goldsky, no auth required):
- `GBM_SUBGRAPH_URL=https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-gbm-baazaar-base/prod/gn`

GBM Diamond deploy block (useful for log scans):
- `DEPLOY_BLOCK=33276452` (Base mainnet)

Token kind constants (used in `createAuction` InitiatorInfo):
- `ERC721=0x73ad2146`
- `ERC1155=0x973bb640`

Likely-whitelisted token contracts on Base mainnet (from the GBM repo deployment config):
- Aavegotchi diamond (ERC721): `0xA99c4B08201F2913Db8D28e71d020c4298F29dBF`
- Forge diamond (ERC1155): `0x50aF2d63b839aA32b4166FD1Cb247129b715186C`
- Fake Gotchi Card diamond (ERC721): `0xe46B8902dAD841476d9Fee081F1d62aE317206A9`
- Fake Gotchi Art diamond (ERC721): `0xAb59CA4A16925b0a4BaC5026C94bEB20A29Df479`

Recommended shell defaults (allow overrides):
```bash
export BASE_MAINNET_RPC="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
export GBM_DIAMOND="${GBM_DIAMOND:-0x80320A0000C7A6a34086E2ACAD6915Ff57FfDA31}"
export GHST="${GHST:-0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB}"
export USDC="${USDC:-0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913}"
export GBM_SUBGRAPH_URL="${GBM_SUBGRAPH_URL:-https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-gbm-baazaar-base/prod/gn}"
export DRY_RUN="${DRY_RUN:-1}"
export SLIPPAGE_PCT="${SLIPPAGE_PCT:-1}"
```
