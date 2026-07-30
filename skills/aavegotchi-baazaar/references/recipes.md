# Common Recipes (Foundry cast)

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

## ERC20: Balances / Allowances

GHST balance:
```bash
~/.foundry/bin/cast call "$GHST" 'balanceOf(address)(uint256)' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

USDC balance:
```bash
~/.foundry/bin/cast call "$USDC" 'balanceOf(address)(uint256)' "$FROM_ADDRESS" --rpc-url "$BASE_MAINNET_RPC"
```

GHST allowance to Diamond:
```bash
~/.foundry/bin/cast call "$GHST" 'allowance(address,address)(uint256)' "$FROM_ADDRESS" "$DIAMOND" --rpc-url "$BASE_MAINNET_RPC"
```

USDC allowance to Diamond:
```bash
~/.foundry/bin/cast call "$USDC" 'allowance(address,address)(uint256)' "$FROM_ADDRESS" "$DIAMOND" --rpc-url "$BASE_MAINNET_RPC"
```

Approve GHST (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$GHST" 'approve(address,uint256)' "$DIAMOND" "<AMOUNT_GHST_WEI>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Approve USDC (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "$USDC" 'approve(address,uint256)' "$DIAMOND" "<AMOUNT_USDC_6DP>" \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## ERC721 / ERC1155: Approval For All

Check (ERC721 or ERC1155 contract):
```bash
~/.foundry/bin/cast call "<NFT_CONTRACT_ADDRESS>" 'isApprovedForAll(address,address)(bool)' "$FROM_ADDRESS" "$DIAMOND" \
  --rpc-url "$BASE_MAINNET_RPC"
```

Set approval (broadcast; do this only when explicitly instructed):
```bash
~/.foundry/bin/cast send "<NFT_CONTRACT_ADDRESS>" 'setApprovalForAll(address,bool)' "$DIAMOND" true \
  --private-key "$PRIVATE_KEY" \
  --rpc-url "$BASE_MAINNET_RPC"
```

## Listing Fee

Listing fee (GHST wei) on the Diamond:
```bash
~/.foundry/bin/cast call "$DIAMOND" 'getListingFeeInWei()(uint256)' --rpc-url "$BASE_MAINNET_RPC"
```

## Swap Deadline (now + 600)

```bash
python3 - <<'PY'
import time
print(int(time.time()) + 600)
PY
```

## Multiply Big Ints (ERC1155 total cost)

When total cost is `priceInWei * quantity` and values may exceed shell integer limits:
```bash
python3 - <<'PY'
price_in_wei = int("1000000000000000000")  # replace
quantity = int("3")                        # replace
print(price_in_wei * quantity)
PY
```

## Fetch GHST/USD (CoinGecko)

```bash
curl -s 'https://api.coingecko.com/api/v3/simple/price?ids=aavegotchi&vs_currencies=usd' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)[\"aavegotchi\"][\"usd\"])'
```

## Smoke Tests (No Funds Required)

These confirm function selectors exist on the Diamond (you should see a meaningful revert reason, not "Function does not exist").

Swap method exists:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'swapAndBuyERC1155(address,uint256,uint256,uint256,uint256,address,uint256,uint256,uint256,address)' \
  "$USDC" 0 0 0 1 \
  "$DIAMOND" 59 1 1000000000000000000000 \
  0x000000000000000000000000000000000000dEaD \
  --rpc-url "$BASE_MAINNET_RPC"
```

Execute method exists:
```bash
~/.foundry/bin/cast call "$DIAMOND" \
  'executeERC1155ListingToRecipient(uint256,address,uint256,uint256,uint256,address)' \
  1 "$DIAMOND" 59 1 1000000000000000000000 \
  0x000000000000000000000000000000000000dEaD \
  --from 0x000000000000000000000000000000000000dEaD \
  --rpc-url "$BASE_MAINNET_RPC"
```
