---
name: aavegotchi-baazaar
description: >
  View, add, and execute Aavegotchi Baazaar listings on Base mainnet (8453).
  Buy with GHST directly or buy with USDC using swapAndBuy*.
  Safety-first: dryRun defaults true (simulate with cast call; only broadcast with cast send when dryRun=false / DRY_RUN=0).
homepage: https://github.com/aavegotchi/aavegotchi-baazaar-skill
metadata:
  openclaw:
    requires:
      bins:
        - cast
        - curl
        - python3
      env:
        - FROM_ADDRESS
        - PRIVATE_KEY
        - BASE_MAINNET_RPC
        - RECIPIENT_ADDRESS
        - DRY_RUN
        - SLIPPAGE_PCT
        - PAYMENT_FEE_PCT_USDC
        - GHST_USD_PRICE
        - DIAMOND
        - GHST
        - USDC
        - SUBGRAPH_URL
    primaryEnv: PRIVATE_KEY
---

## Safety Rules

- Default to `dryRun=true` (`DRY_RUN=1`). Never broadcast unless explicitly instructed to do so.
- Mandatory confirmation gate for every `cast send`:
  - First simulate with `cast call` and show a transaction summary (method, args, chain id, from, rpc URL).
  - Then require an explicit user confirmation message before broadcast.
  - Only allow broadcast when `DRY_RUN=0` and `BROADCAST_CONFIRM=CONFIRM_SEND` are both set.
  - If any transaction argument changes after confirmation, invalidate confirmation and require a new confirmation.
- Always verify Base mainnet:
  - `~/.foundry/bin/cast chain-id --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"` must be `8453`.
- Always verify key/address alignment:
  - `~/.foundry/bin/cast wallet address --private-key "$PRIVATE_KEY"` must equal `$FROM_ADDRESS`.
- Always refetch the listing from the subgraph immediately before simulating or broadcasting (listings can be cancelled/sold/price-updated).
- Never print or log `$PRIVATE_KEY`.
- Never accept a private key from user chat input; only read `$PRIVATE_KEY` from environment.

## Shell Input Safety (Avoid RCE)

This skill includes shell commands. Treat any value you copy from a user or an external source (subgraph responses, chat messages, etc.) as untrusted.

Rules:
- Never execute user-provided strings as shell code (avoid `eval`, `bash -c`, `sh -c`).
- Use only allowlisted command templates from this file/references. Do not build free-form shell commands by concatenating user text.
- Only substitute addresses that match `0x` + 40 hex chars.
- Only substitute uint values that are base-10 digits (no commas, no decimals).
- Hard rule: user/external values must be validated first, stored as data values, and passed as quoted positional args. Never let user text become shell flags, subcommands, operators, pipes, redirects, or command substitutions.
- In the command examples below, listing-specific inputs are written as quoted placeholders like `"<LISTING_ID>"` to avoid accidental shell interpolation. Replace them with literal values after you validate them.

Allowlisted command templates:
- `~/.foundry/bin/cast chain-id|wallet address|call|send ...` using fixed ABI signatures from this skill.
- `curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '...static GraphQL query...'`.
- `curl -s "$COINGECKO_SIMPLE_PRICE_URL"` for GHST/USD only.
- `python3` inline snippets from this skill/references for validation and deterministic math only.
- Disallow `eval`, `bash -c`, `sh -c`, backticks, and `$(...)` with untrusted input.

Quick validators (replace the placeholder values):
```bash
python3 - <<'PY'
import re

listing_id = "<LISTING_ID>"  # digits only
token_contract = "<TOKEN_CONTRACT_ADDRESS>"  # 0x + 40 hex chars
price_in_wei = "<PRICE_IN_WEI>"  # digits only

if not re.fullmatch(r"[0-9]+", listing_id):
    raise SystemExit("LISTING_ID must be base-10 digits only")
if not re.fullmatch(r"0x[a-fA-F0-9]{40}", token_contract):
    raise SystemExit("TOKEN_CONTRACT_ADDRESS must be a 0x + 40-hex address")
if not re.fullmatch(r"[0-9]+", price_in_wei):
    raise SystemExit("PRICE_IN_WEI must be base-10 digits only")

print("ok")
PY
```

## Required Setup

Required env vars:
- `PRIVATE_KEY`: EOA private key used for `cast send` (never print/log).
- `FROM_ADDRESS`: EOA address that owns funds/NFTs and will submit txs.
- `BASE_MAINNET_RPC`: RPC URL. If unset, use `https://mainnet.base.org`.

Hardcoded Base mainnet constants (override via env if needed):
```bash
export BASE_MAINNET_RPC="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
export DIAMOND="${DIAMOND:-0xA99c4B08201F2913Db8D28e71d020c4298F29dBF}"
export GHST="${GHST:-0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB}"
export USDC="${USDC:-0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913}"
export SUBGRAPH_URL_CANONICAL="https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn"
export SUBGRAPH_URL="${SUBGRAPH_URL:-$SUBGRAPH_URL_CANONICAL}"
export COINGECKO_SIMPLE_PRICE_URL="${COINGECKO_SIMPLE_PRICE_URL:-https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi&vs_currencies=usd}"
```

Optional env vars:
- `RECIPIENT_ADDRESS`: defaults to `FROM_ADDRESS`.
- `DRY_RUN`: `1` (default) to only simulate via `cast call`. Set to `0` to broadcast via `cast send`.
- `BROADCAST_CONFIRM`: must be exactly `CONFIRM_SEND` to allow any `cast send`; unset immediately after broadcast.
- `SLIPPAGE_PCT`: defaults to `1` (used for USDC swapAmount math).
- `PAYMENT_FEE_PCT_USDC`: defaults to `1` (used for USDC swapAmount math).
- `GHST_USD_PRICE`: optional override; if unset, fetch from CoinGecko in the USDC flow.

Notes:
- Commands below use `~/.foundry/bin/cast` (works reliably in cron/non-interactive shells). If `cast` is on `PATH`, you can replace `~/.foundry/bin/cast` with `cast`.
- Canonical addresses and endpoints live in:
  - `references/addresses.md`
  - `references/subgraph.md`

## Network Endpoint Allowlist

Only call these HTTPS endpoints:
- Goldsky subgraph: `$SUBGRAPH_URL_CANONICAL`
- CoinGecko GHST/USD: `$COINGECKO_SIMPLE_PRICE_URL`

Refuse non-allowlisted endpoints:
```bash
test "$SUBGRAPH_URL" = "$SUBGRAPH_URL_CANONICAL" || { echo "Refusing non-allowlisted SUBGRAPH_URL"; exit 1; }
test "$COINGECKO_SIMPLE_PRICE_URL" = "https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi&vs_currencies=usd" || { echo "Refusing non-allowlisted CoinGecko URL"; exit 1; }
```

## View Listings (Subgraph)

Subgraph endpoint (Goldsky):
- Default: `$SUBGRAPH_URL` (see exports above)
- Value: `https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-core-base/prod/gn`

Get ERC721 listing by id:
```bash
curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '{
  "query":"query($id: ID!){ erc721Listing(id:$id){ id category erc721TokenAddress tokenId seller priceInWei cancelled timeCreated timePurchased } }",
  "variables":{"id":"1"}
}'
```

Get ERC1155 listing by id:
- Subgraph field name is `erc1155TypeId` (this maps to the onchain `typeId` / `itemId` argument).
```bash
curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '{
  "query":"query($id: ID!){ erc1155Listing(id:$id){ id category erc1155TokenAddress erc1155TypeId quantity seller priceInWei cancelled sold timeCreated } }",
  "variables":{"id":"1"}
}'
```

Find active listings:
- ERC721: `where:{cancelled:false, timePurchased:\"0\"}`
- ERC1155: `where:{cancelled:false, sold:false}`

Example (active ERC721, newest first):
```bash
curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '{
  "query":"query{ erc721Listings(first:20, orderBy:timeCreated, orderDirection:desc, where:{cancelled:false, timePurchased:\"0\"}){ id erc721TokenAddress tokenId priceInWei seller timeCreated } }"
}'
```

Example (active ERC1155, newest first):
```bash
curl -s "$SUBGRAPH_URL" -H 'content-type: application/json' --data '{
  "query":"query{ erc1155Listings(first:20, orderBy:timeCreated, orderDirection:desc, where:{cancelled:false, sold:false}){ id erc1155TokenAddress erc1155TypeId quantity priceInWei seller timeCreated } }"
}'
```

## Execute Listing (Buy With GHST)

Onchain methods (Diamond):
- `executeERC721ListingToRecipient(uint256 listingId,address contractAddress,uint256 priceInWei,uint256 tokenId,address recipient)`
- `executeERC1155ListingToRecipient(uint256 listingId,address contractAddress,uint256 itemId,uint256 quantity,uint256 priceInWei,address recipient)`

Total cost:
- ERC721: `totalCostGhstWei = priceInWei`
- ERC1155: `totalCostGhstWei = priceInWei * quantity` (but you still pass `quantity` and `priceInWei` separately to the method)

Before buying:
1. Fetch listing details from the subgraph (id, token contract address, tokenId/typeId, quantity, priceInWei).
2. Check GHST balance/allowance and prepare approvals if needed (see `references/recipes.md`).

Dry-run (simulate) ERC721 buy:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'executeERC721ListingToRecipient(uint256,address,uint256,uint256,address)' \
  "<LISTING_ID>" "<ERC721_TOKEN_ADDRESS>" "<PRICE_IN_WEI>" "<TOKEN_ID>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

Broadcast (real) ERC721 buy (only when explicitly instructed):
```bash
test "${DRY_RUN:-1}" = "0" || { echo "Refusing broadcast: DRY_RUN must be 0"; exit 1; }
test "${BROADCAST_CONFIRM:-}" = "CONFIRM_SEND" || { echo "Refusing broadcast: set BROADCAST_CONFIRM=CONFIRM_SEND after explicit user confirmation"; exit 1; }
~/.foundry/bin/cast send "$DIAMOND" \
  'executeERC721ListingToRecipient(uint256,address,uint256,uint256,address)' \
  "<LISTING_ID>" "<ERC721_TOKEN_ADDRESS>" "<PRICE_IN_WEI>" "<TOKEN_ID>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
unset BROADCAST_CONFIRM
```

Dry-run (simulate) ERC1155 buy:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'executeERC1155ListingToRecipient(uint256,address,uint256,uint256,uint256,address)' \
  "<LISTING_ID>" "<ERC1155_TOKEN_ADDRESS>" "<TYPE_ID>" "<QUANTITY>" "<PRICE_IN_WEI>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

Broadcast (real) ERC1155 buy (only when explicitly instructed):
```bash
test "${DRY_RUN:-1}" = "0" || { echo "Refusing broadcast: DRY_RUN must be 0"; exit 1; }
test "${BROADCAST_CONFIRM:-}" = "CONFIRM_SEND" || { echo "Refusing broadcast: set BROADCAST_CONFIRM=CONFIRM_SEND after explicit user confirmation"; exit 1; }
~/.foundry/bin/cast send "$DIAMOND" \
  'executeERC1155ListingToRecipient(uint256,address,uint256,uint256,uint256,address)' \
  "<LISTING_ID>" "<ERC1155_TOKEN_ADDRESS>" "<TYPE_ID>" "<QUANTITY>" "<PRICE_IN_WEI>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
unset BROADCAST_CONFIRM
```

## Execute Listing (Buy With USDC swapAndBuy*)

Onchain methods (Diamond):
- `swapAndBuyERC721(address tokenIn,uint256 swapAmount,uint256 minGhstOut,uint256 swapDeadline,uint256 listingId,address contractAddress,uint256 priceInWei,uint256 tokenId,address recipient)`
- `swapAndBuyERC1155(address tokenIn,uint256 swapAmount,uint256 minGhstOut,uint256 swapDeadline,uint256 listingId,address contractAddress,uint256 itemId,uint256 quantity,uint256 priceInWei,address recipient)`

Required computed args:
- `swapDeadline = now + 600`
- `minGhstOut = totalCostGhstWei` (exactly)
- `swapAmount` (USDC base units, 6 decimals): compute per `references/usdc-swap-math.md`

Before buying:
1. Fetch listing details from the subgraph (and compute `totalCostGhstWei`).
2. Compute `swapAmount` in USDC base units (integer, rounded up).
3. Ensure USDC allowance to the Diamond is at least `swapAmount` (see `references/recipes.md`).

Dry-run (simulate) ERC721 USDC swap+buy:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'swapAndBuyERC721(address,uint256,uint256,uint256,uint256,address,uint256,uint256,address)' \
  "$USDC" "<SWAP_AMOUNT_USDC_6DP>" "<MIN_GHST_OUT_GHST_WEI>" "<SWAP_DEADLINE_UNIX>" "<LISTING_ID>" "<ERC721_TOKEN_ADDRESS>" "<PRICE_IN_WEI>" "<TOKEN_ID>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

Dry-run (simulate) ERC1155 USDC swap+buy:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'swapAndBuyERC1155(address,uint256,uint256,uint256,uint256,address,uint256,uint256,uint256,address)' \
  "$USDC" "<SWAP_AMOUNT_USDC_6DP>" "<MIN_GHST_OUT_GHST_WEI>" "<SWAP_DEADLINE_UNIX>" "<LISTING_ID>" "<ERC1155_TOKEN_ADDRESS>" "<TYPE_ID>" "<QUANTITY>" "<PRICE_IN_WEI>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

Broadcast (real) ERC721 swap+buy (only when explicitly instructed):
```bash
test "${DRY_RUN:-1}" = "0" || { echo "Refusing broadcast: DRY_RUN must be 0"; exit 1; }
test "${BROADCAST_CONFIRM:-}" = "CONFIRM_SEND" || { echo "Refusing broadcast: set BROADCAST_CONFIRM=CONFIRM_SEND after explicit user confirmation"; exit 1; }
~/.foundry/bin/cast send "$DIAMOND" \
  'swapAndBuyERC721(address,uint256,uint256,uint256,uint256,address,uint256,uint256,address)' \
  "$USDC" "<SWAP_AMOUNT_USDC_6DP>" "<MIN_GHST_OUT_GHST_WEI>" "<SWAP_DEADLINE_UNIX>" "<LISTING_ID>" "<ERC721_TOKEN_ADDRESS>" "<PRICE_IN_WEI>" "<TOKEN_ID>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
unset BROADCAST_CONFIRM
```

Broadcast (real) ERC1155 swap+buy (only when explicitly instructed):
```bash
test "${DRY_RUN:-1}" = "0" || { echo "Refusing broadcast: DRY_RUN must be 0"; exit 1; }
test "${BROADCAST_CONFIRM:-}" = "CONFIRM_SEND" || { echo "Refusing broadcast: set BROADCAST_CONFIRM=CONFIRM_SEND after explicit user confirmation"; exit 1; }
~/.foundry/bin/cast send "$DIAMOND" \
  'swapAndBuyERC1155(address,uint256,uint256,uint256,uint256,address,uint256,uint256,uint256,address)' \
  "$USDC" "<SWAP_AMOUNT_USDC_6DP>" "<MIN_GHST_OUT_GHST_WEI>" "<SWAP_DEADLINE_UNIX>" "<LISTING_ID>" "<ERC1155_TOKEN_ADDRESS>" "<TYPE_ID>" "<QUANTITY>" "<PRICE_IN_WEI>" "${RECIPIENT_ADDRESS:-$FROM_ADDRESS}" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
unset BROADCAST_CONFIRM
```

## Add Listing

Onchain methods (Diamond):
- `getListingFeeInWei()(uint256)`
- `addERC721Listing(address erc721TokenAddress,uint256 tokenId,uint256 category,uint256 priceInWei)`
- `setERC1155Listing(address erc1155TokenAddress,uint256 typeId,uint256 quantity,uint256 category,uint256 priceInWei)`

Steps:
1. Check listing fee:
   - `~/.foundry/bin/cast call "$DIAMOND" 'getListingFeeInWei()(uint256)' --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"`
2. Ensure the NFT contract has `setApprovalForAll($DIAMOND,true)` (ERC721/1155) before listing.
3. Submit the listing tx (simulate with `cast call` when `dryRun=true`, broadcast with `cast send` only when explicitly instructed).
4. After listing, find the newest listingId via the subgraph for `seller=$FROM_ADDRESS` ordered by `timeCreated desc` and confirm it matches token/typeId.

ERC721 list (simulate):
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'addERC721Listing(address,uint256,uint256,uint256)' \
  "<ERC721_TOKEN_ADDRESS>" "<TOKEN_ID>" "<CATEGORY>" "<PRICE_IN_WEI>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

ERC1155 list (simulate):
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'setERC1155Listing(address,uint256,uint256,uint256,uint256)' \
  "<ERC1155_TOKEN_ADDRESS>" "<TYPE_ID>" "<QUANTITY>" "<CATEGORY>" "<PRICE_IN_WEI>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

## Common Failure Modes

- `Diamond: Function does not exist`: wrong contract address or wrong function signature (or wrong chain).
- `ERC1155Marketplace: not enough GHST`: insufficient balance or allowance (or computed `totalCostGhstWei` is wrong).
- `ERC1155Marketplace: Not approved` / approval errors: missing `setApprovalForAll` for listing, or missing ERC20 `approve` for buying.
- Swap errors (e.g. `LibTokenSwap: swapAmount must be > 0`): bad swapAmount math or missing inputs.
- Listing cancelled/sold or price changed: refetch from subgraph and re-simulate before broadcasting.
