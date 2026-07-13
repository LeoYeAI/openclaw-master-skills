---
name: aavegotchi-gbm-skill
description: >
  View, create, cancel, bid, and claim Aavegotchi GBM auctions on Base mainnet (8453).
  Subgraph-first discovery (Goldsky), with onchain verification + execution via Foundry cast.
  Safety-first: DRY_RUN defaults to 1 (simulate with cast call; only broadcast with cast send when DRY_RUN=0 and explicitly instructed).
homepage: https://github.com/aavegotchi/aavegotchi-gbm-skill
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
        - DRY_RUN
        - RECIPIENT_ADDRESS
        - GBM_SUBGRAPH_URL
        - GOLDSKY_API_KEY
        - GBM_DIAMOND
        - GHST
        - USDC
        - SLIPPAGE_PCT
        - GHST_USD_PRICE
        - ETH_USD_PRICE
    primaryEnv: PRIVATE_KEY
---

## Safety Rules

- Default to `DRY_RUN=1`. Never broadcast unless explicitly instructed.
- Always verify Base mainnet:
  - `~/.foundry/bin/cast chain-id --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"` must be `8453`.
- Always verify key/address alignment:
  - `~/.foundry/bin/cast wallet address --private-key "$PRIVATE_KEY"` must equal `$FROM_ADDRESS`.
- Always refetch from the subgraph immediately before any simulate/broadcast step (auctions can be outbid, ended, claimed, or cancelled).
- Always gate onchain immediately before simulating or broadcasting:
  - ensure the onchain `highestBid` matches the `highestBid` you pass into `commitBid` / `swapAndCommitBid`.
  - ensure token params match (token contract, token id, quantity).
- Never print or log `$PRIVATE_KEY`.

## Shell Input Safety (Avoid RCE)

This skill includes shell commands. Treat any value you copy from a user or an external source (subgraph responses, chat messages, etc.) as untrusted.

Rules:
- Never execute user-provided strings as shell code (avoid `eval`, `bash -c`, `sh -c`).
- Only substitute addresses that match `0x` + 40 hex chars.
- Only substitute uint values that are base-10 digits (no commas, no decimals).
- In the command examples below, auction-specific inputs are written as quoted placeholders like `"<AUCTION_ID>"` to avoid accidental shell interpolation. Replace them with literal values only after validation.

Quick validators (replace the placeholder values):
```bash
python3 - <<'PY'
import re

auction_id = "<AUCTION_ID>"                 # digits only
token_contract = "<TOKEN_CONTRACT_ADDRESS>" # 0x + 40 hex chars
token_id = "<TOKEN_ID>"                     # digits only
amount = "<TOKEN_AMOUNT>"                   # digits only

if not re.fullmatch(r"[0-9]+", auction_id):
    raise SystemExit("AUCTION_ID must be base-10 digits only")
if not re.fullmatch(r"0x[a-fA-F0-9]{40}", token_contract):
    raise SystemExit("TOKEN_CONTRACT_ADDRESS must be a 0x + 40-hex address")
if not re.fullmatch(r"[0-9]+", token_id):
    raise SystemExit("TOKEN_ID must be base-10 digits only")
if not re.fullmatch(r"[0-9]+", amount):
    raise SystemExit("TOKEN_AMOUNT must be base-10 digits only")

print("ok")
PY
```

## Required Setup

Required env vars:
- `PRIVATE_KEY`: EOA private key used for `cast send` (never print/log).
- `FROM_ADDRESS`: EOA address that owns NFTs and will submit txs.
- `BASE_MAINNET_RPC`: RPC URL. If unset, use `https://mainnet.base.org`.
- `GBM_SUBGRAPH_URL`: Goldsky subgraph endpoint for auctions.

Optional env vars:
- `DRY_RUN`: `1` (default) to only simulate via `cast call`. Set to `0` to broadcast via `cast send`.
- `RECIPIENT_ADDRESS`: for swap flows; receives any excess GHST refunded by the contract. Defaults to `FROM_ADDRESS`.
- `GOLDSKY_API_KEY`: optional; if set, include `Authorization: Bearer ...` header in subgraph calls.
- `SLIPPAGE_PCT`: defaults to `1` (%); used in `swapAmount` estimate math.
- `GHST_USD_PRICE`, `ETH_USD_PRICE`: optional overrides; if unset, fetch from CoinGecko in the swap math snippets.

Recommended defaults (override via env if needed):
```bash
export BASE_MAINNET_RPC="${BASE_MAINNET_RPC:-https://mainnet.base.org}"
export GBM_DIAMOND="${GBM_DIAMOND:-0x80320A0000C7A6a34086E2ACAD6915Ff57FfDA31}"
export GHST="${GHST:-0xcD2F22236DD9Dfe2356D7C543161D4d260FD9BcB}"
export USDC="${USDC:-0x833589fCD6eDb6E08f4c7C32D4f71b54BDA02913}"
export GBM_SUBGRAPH_URL="${GBM_SUBGRAPH_URL:-https://api.goldsky.com/api/public/project_cmh3flagm0001r4p25foufjtt/subgraphs/aavegotchi-gbm-baazaar-base/prod/gn}"
export DRY_RUN="${DRY_RUN:-1}"
export SLIPPAGE_PCT="${SLIPPAGE_PCT:-1}"
```

Notes:
- Commands below use `~/.foundry/bin/cast` so they work in cron/non-interactive shells.

## View / List Auctions (Subgraph First)

See `references/subgraph.md` for canonical queries.

Auction by id (quick):
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($id:ID!){ auction(id:$id){ id type contractAddress tokenId quantity seller highestBid highestBidder totalBids startsAt endsAt claimAt claimed cancelled presetId category buyNowPrice startBidPrice } }",
  "variables":{"id":"<AUCTION_ID>"}
}'
```

Active auctions (ends soonest first):
```bash
NOW=$(date +%s)
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data "{
  \"query\":\"query(\$now:BigInt!){ auctions(first:20, orderBy: endsAt, orderDirection: asc, where:{claimed:false, cancelled:false, startsAt_lte:\$now, endsAt_gt:\$now}){ id type contractAddress tokenId quantity highestBid highestBidder totalBids startsAt endsAt claimAt presetId category seller } }\",
  \"variables\":{\"now\":\"$NOW\"}
}"
```

## Onchain Verification (Required Before Bids / Sends)

The onchain source of truth is the GBM diamond.

Confirm core auction fields (full struct decode):
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" \
  'getAuctionInfo(uint256)((address,uint96,address,uint88,uint88,bool,bool,address,(uint80,uint80,uint56,uint8,bytes4,uint256,uint96,uint96),(uint64,uint64,uint64,uint64,uint256),uint96,uint96))' \
  "<AUCTION_ID>" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Useful individual getters:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getAuctionHighestBid(uint256)(uint256)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getAuctionHighestBidder(uint256)(address)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getAuctionStartTime(uint256)(uint256)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getAuctionEndTime(uint256)(uint256)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getContractAddress(uint256)(address)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getTokenId(uint256)(uint256)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getTokenKind(uint256)(bytes4)' "<AUCTION_ID>" --rpc-url "$BASE_MAINNET_RPC"
```

## Create Auction

Onchain method:
- `createAuction((uint80,uint80,uint56,uint8,bytes4,uint256,uint96,uint96),address,uint256)(uint256)`

High-level steps:
1. Ensure the token contract is whitelisted on the GBM diamond (otherwise revert `ContractNotAllowed`).
2. Ensure the token is approved to the GBM diamond:
   - ERC721/1155: `setApprovalForAll(GBM_DIAMOND,true)`
3. Choose `InitiatorInfo`:
   - `startTime` must be in the future.
   - `endTime - startTime` must be between 3600 and 604800 seconds (1h to 7d).
   - `tokenKind` is `0x73ad2146` (ERC721) or `0x973bb640` (ERC1155).
   - `buyItNowPrice` optional; `startingBid` optional (if nonzero, you must approve GHST for the 4% prepaid fee).
4. Simulate with `cast call` using `--from "$FROM_ADDRESS"`.
5. Broadcast with `cast send` only when explicitly instructed (`DRY_RUN=0`).
6. Post-tx: query subgraph for newest seller auctions and match `(contractAddress, tokenId)`.

Simulate create (ERC721 example):
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" \
  'createAuction((uint80,uint80,uint56,uint8,bytes4,uint256,uint96,uint96),address,uint256)(uint256)' \
  "(<START_TIME>,<END_TIME>,1,<CATEGORY>,0x73ad2146,<TOKEN_ID>,<BUY_NOW_GHST_WEI>,<STARTING_BID_GHST_WEI>)" \
  "<ERC721_CONTRACT_ADDRESS>" "<PRESET_ID>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast create (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" \
  'createAuction((uint80,uint80,uint56,uint8,bytes4,uint256,uint96,uint96),address,uint256)(uint256)' \
  "(<START_TIME>,<END_TIME>,1,<CATEGORY>,0x73ad2146,<TOKEN_ID>,<BUY_NOW_GHST_WEI>,<STARTING_BID_GHST_WEI>)" \
  "<ERC721_CONTRACT_ADDRESS>" "<PRESET_ID>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Post-create (find your newest auctions and confirm):
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($seller:Bytes!){ auctions(first:10, orderBy: createdAt, orderDirection: desc, where:{seller:$seller}){ id type contractAddress tokenId quantity createdAt startsAt endsAt claimed cancelled } }",
  "variables":{"seller":"<FROM_ADDRESS_LOWERCASE>"}
}'
```

## Cancel Auction

Onchain method:
- `cancelAuction(uint256)`

Steps:
1. Subgraph: check `claimed`, `cancelled`, `endsAt`, `highestBid`.
2. Onchain: call `getAuctionInfo(auctionId)` to verify ownership and state.
3. Simulate with `cast call` (`--from "$FROM_ADDRESS"`).
4. Broadcast only when explicitly instructed.

Simulate:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" 'cancelAuction(uint256)' "<AUCTION_ID>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" 'cancelAuction(uint256)' "<AUCTION_ID>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Bid With GHST (commitBid)

Onchain method:
- `commitBid(uint256,uint256,uint256,address,uint256,uint256,bytes)` (last `bytes` is ignored; pass `0x`)

Steps:
1. Subgraph: fetch auction fields (id, contractAddress, tokenId, quantity, highestBid, startsAt, endsAt, claimed/cancelled).
2. Onchain: refetch `highestBid` and token params; you must pass the exact current onchain `highestBid` or it reverts `UnmatchedHighestBid`.
3. Compute a safe minimum next bid using `references/bid-math.md` (uses onchain `bidDecimals` + `stepMin`).
4. Ensure GHST allowance to the GBM diamond covers `bidAmount`.
5. Simulate via `cast call` (optional but recommended).
6. Broadcast only when explicitly instructed.

Simulate:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" \
  'commitBid(uint256,uint256,uint256,address,uint256,uint256,bytes)' \
  "<AUCTION_ID>" "<BID_AMOUNT_GHST_WEI>" "<HIGHEST_BID_GHST_WEI>" "<TOKEN_CONTRACT_ADDRESS>" "<TOKEN_ID>" "<TOKEN_AMOUNT>" 0x \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" \
  'commitBid(uint256,uint256,uint256,address,uint256,uint256,bytes)' \
  "<AUCTION_ID>" "<BID_AMOUNT_GHST_WEI>" "<HIGHEST_BID_GHST_WEI>" "<TOKEN_CONTRACT_ADDRESS>" "<TOKEN_ID>" "<TOKEN_AMOUNT>" 0x \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Bid With USDC Swap (swapAndCommitBid)

Onchain method:
- `swapAndCommitBid((address,uint256,uint256,uint256,address,uint256,uint256,uint256,address,uint256,uint256,bytes))`

Struct fields (in order):
1. `tokenIn` (USDC)
2. `swapAmount` (USDC 6dp)
3. `minGhstOut` (GHST wei; must be >= bidAmount)
4. `swapDeadline` (unix; must be <= now + 86400)
5. `recipient` (refund receiver for excess GHST)
6. `auctionID`
7. `bidAmount` (GHST wei)
8. `highestBid` (must match onchain)
9. `tokenContract`
10. `tokenID`
11. `amount` (tokenAmount/quantity)
12. `_signature` (ignored; pass `0x`)

Compute `swapAmount` estimate in `references/swap-math.md`.

Simulate:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" \
  'swapAndCommitBid((address,uint256,uint256,uint256,address,uint256,uint256,uint256,address,uint256,uint256,bytes))' \
  "($USDC,<SWAP_AMOUNT_USDC_6DP>,<MIN_GHST_OUT_GHST_WEI>,<SWAP_DEADLINE_UNIX>,${RECIPIENT_ADDRESS:-$FROM_ADDRESS},<AUCTION_ID>,<BID_AMOUNT_GHST_WEI>,<HIGHEST_BID_GHST_WEI>,<TOKEN_CONTRACT_ADDRESS>,<TOKEN_ID>,<TOKEN_AMOUNT>,0x)" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" \
  'swapAndCommitBid((address,uint256,uint256,uint256,address,uint256,uint256,uint256,address,uint256,uint256,bytes))' \
  "($USDC,<SWAP_AMOUNT_USDC_6DP>,<MIN_GHST_OUT_GHST_WEI>,<SWAP_DEADLINE_UNIX>,${RECIPIENT_ADDRESS:-$FROM_ADDRESS},<AUCTION_ID>,<BID_AMOUNT_GHST_WEI>,<HIGHEST_BID_GHST_WEI>,<TOKEN_CONTRACT_ADDRESS>,<TOKEN_ID>,<TOKEN_AMOUNT>,0x)" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Bid With ETH Swap (swapAndCommitBid)

Same method as above, but:
- `tokenIn = 0x0000000000000000000000000000000000000000`
- `--value <SWAP_AMOUNT_WEI>` must equal the `swapAmount` you pass inside the tuple.

Broadcast (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" \
  'swapAndCommitBid((address,uint256,uint256,uint256,address,uint256,uint256,uint256,address,uint256,uint256,bytes))' \
  "(0x0000000000000000000000000000000000000000,<SWAP_AMOUNT_WEI>,<MIN_GHST_OUT_GHST_WEI>,<SWAP_DEADLINE_UNIX>,${RECIPIENT_ADDRESS:-$FROM_ADDRESS},<AUCTION_ID>,<BID_AMOUNT_GHST_WEI>,<HIGHEST_BID_GHST_WEI>,<TOKEN_CONTRACT_ADDRESS>,<TOKEN_ID>,<TOKEN_AMOUNT>,0x)" \
  --value "<SWAP_AMOUNT_WEI>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Claim Auction

Onchain methods:
- `claim(uint256)`
- `batchClaim(uint256[])`

Claim readiness:
- Auction owner can claim at `now >= endsAt`.
- Highest bidder can claim at `now >= endsAt + cancellationTime`.
  - `cancellationTime` is readable from storage slot 12 (see `references/recipes.md`).
  - Subgraph may provide `claimAt` (if populated), but always verify onchain.

Simulate:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" 'claim(uint256)' "<AUCTION_ID>" \
  --from "$FROM_ADDRESS" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Broadcast (only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GBM_DIAMOND" 'claim(uint256)' "<AUCTION_ID>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Optional: Buy Now

Onchain methods:
- `buyNow(uint256)`
- `swapAndBuyNow((address,uint256,uint256,uint256,address,uint256))`

These are not required for the primary use case, but are adjacent to bidding flows. If you use them, follow the same safety gating:
- refetch from subgraph
- verify onchain price/state
- simulate (`cast call`)
- only broadcast when explicitly instructed

## Smoke Tests (No Funds Required)

1. Subgraph reachable (introspection lists `auction`, `auctions`, `bid`, `bids`):
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{ "query":"{ __schema { queryType { fields { name } } } }" }' \
  | python3 -c 'import json,sys; f=[x[\"name\"] for x in json.load(sys.stdin)[\"data\"][\"__schema\"][\"queryType\"][\"fields\"]]; print([n for n in f if n in (\"auction\",\"auctions\",\"bid\",\"bids\")])'
```

2. Subgraph data sane:
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{\"query\":\"query($id:ID!){ auction(id:$id){ id contractAddress tokenId } }\",\"variables\":{\"id\":\"0\"}}'
```

3. Onchain reachable + matches subgraph:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" \
  'getAuctionInfo(uint256)((address,uint96,address,uint88,uint88,bool,bool,address,(uint80,uint80,uint56,uint8,bytes4,uint256,uint96,uint96),(uint64,uint64,uint64,uint64,uint256),uint96,uint96))' \
  0 \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Common Failure Modes

- `UnmatchedHighestBid`: you passed a stale `highestBid` param. Refetch onchain and retry.
- `InvalidAuctionParams`: token contract / id / amount mismatch. Refetch and verify.
- `AuctionNotStarted` / `AuctionEnded`: timing mismatch. Check `startsAt`/`endsAt` (subgraph + onchain).
- `AuctionClaimed`: already claimed or cancelled. Check `claimed` (subgraph + onchain).
- `BiddingNotAllowed`: diamond paused, contract bidding disabled, or re-entrancy lock. Refetch onchain state.
- Swap errors:
  - `LibTokenSwap: swapAmount must be > 0`
  - `LibTokenSwap: deadline expired`
  - `LibTokenSwap: Insufficient output amount` (increase `swapAmount` or slippage)
