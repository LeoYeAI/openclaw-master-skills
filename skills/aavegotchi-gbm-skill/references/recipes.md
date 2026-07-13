# Common Recipes (Foundry cast + Subgraph)

Commands below use `~/.foundry/bin/cast` so they work in cron/non-interactive shells. If `cast` is on `PATH`, you can replace `~/.foundry/bin/cast` with `cast`.

Assumes you set defaults from `references/addresses.md`.

## Safety Checks

Verify chain id is Base mainnet (must be `8453`):
```bash
~/.foundry/bin/cast chain-id --rpc-url "${BASE_MAINNET_RPC:-https://mainnet.base.org}"
```

Verify private key corresponds to FROM_ADDRESS (must match exactly):
```bash
~/.foundry/bin/cast wallet address --private-key "$PRIVATE_KEY"
```

Lowercase your address for subgraph filters:
```bash
python3 - <<'PY'
addr = "<FROM_ADDRESS>"
print(addr.lower())
PY
```

## Subgraph Convenience: Auction By ID
```bash
curl -s "$GBM_SUBGRAPH_URL" -H 'content-type: application/json' ${GOLDSKY_API_KEY:+-H "Authorization: Bearer $GOLDSKY_API_KEY"} --data '{
  "query":"query($id:ID!){ auction(id:$id){ id type contractAddress tokenId quantity seller highestBid highestBidder totalBids startsAt endsAt claimAt claimed cancelled presetId category buyNowPrice startBidPrice } }",
  "variables":{"id":"<AUCTION_ID>"}
}'
```

## ERC20: Balances / Allowances

GHST balance:
```bash
~/.foundry/bin/cast call "$GHST" 'balanceOf(address)(uint256)' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

USDC balance:
```bash
~/.foundry/bin/cast call "$USDC" 'balanceOf(address)(uint256)' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

GHST allowance to GBM diamond:
```bash
~/.foundry/bin/cast call "$GHST" 'allowance(address,address)(uint256)' "$FROM_ADDRESS" "$GBM_DIAMOND" --rpc-url "$BASE_MAINNET_RPC"
```

USDC allowance to GBM diamond:
```bash
~/.foundry/bin/cast call "$USDC" 'allowance(address,address)(uint256)' "$FROM_ADDRESS" "$GBM_DIAMOND" --rpc-url "$BASE_MAINNET_RPC"
```

Approve GHST (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GHST" 'approve(address,uint256)' "$GBM_DIAMOND" "<AMOUNT_GHST_WEI>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Approve USDC (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$USDC" 'approve(address,uint256)' "$GBM_DIAMOND" "<AMOUNT_USDC_6DP>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## ERC721 / ERC1155: Approval For All

Check (ERC721 or ERC1155 contract):
```bash
~/.foundry/bin/cast call "<NFT_CONTRACT_ADDRESS>" 'isApprovedForAll(address,address)(bool)' "$FROM_ADDRESS" "$GBM_DIAMOND" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Set approval (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "<NFT_CONTRACT_ADDRESS>" 'setApprovalForAll(address,bool)' "$GBM_DIAMOND" true \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Auction Time Helpers

Compute start/end times (example: start in 60s, duration 24h):
```bash
python3 - <<'PY'
import time
now = int(time.time())
start = now + 60
end = start + 24*60*60
print("startTime:", start)
print("endTime:  ", end)
PY
```

Swap deadline (now + 600):
```bash
python3 - <<'PY'
import time
print(int(time.time()) + 600)
PY
```

## Read hammerTimeDuration / cancellationTime (Storage Slot 12)

Storage slot `12` packs two uint128 values:
- low 128 bits: `hammerTimeDuration`
- high 128 bits: `cancellationTime`

Fetch raw slot:
```bash
~/.foundry/bin/cast storage "$GBM_DIAMOND" 12 --rpc-url "$BASE_MAINNET_RPC"
```

Decode:
```bash
python3 - <<'PY'
slot_hex = "<SLOT_12_HEX>"  # replace output of cast storage
v = int(slot_hex, 16)
mask = (1 << 128) - 1
hammer = v & mask
cancellation = v >> 128
print("hammerTimeDuration:", hammer)
print("cancellationTime:  ", cancellation)
PY
```

## Auction Nonce (Optional Onchain Discovery)

Storage slot `13` is `auctionNonce` (next auction id):
```bash
~/.foundry/bin/cast storage "$GBM_DIAMOND" 13 --rpc-url "$BASE_MAINNET_RPC"
```

In general, prefer the subgraph for listing and discovery.
