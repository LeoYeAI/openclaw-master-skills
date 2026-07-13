# Bid Math (Minimum Next Bid)

When bidding (`commitBid` / `swapAndCommitBid`), you must:
- Pass the exact current onchain `highestBid` as the `_highestBid` argument (else revert `UnmatchedHighestBid`).
- Bid at or above the contract's effective minimum step, based on preset `stepMin` and `bidDecimals`.

## Effective Minimum Next Bid (Matches Onchain Behavior)

The incentives math uses:
```
baseBid = highestBid * (bidDecimals + stepMin) / bidDecimals
```

If `newBid < baseBid`, the incentives calculation underflows and the bid reverts.

Additionally, if the auction has `startingBid` set, the bid must be:
- `bidAmount >= startingBid`

So the safe minimum is:
```
minNextBid = max(startingBid, baseBid)   (and baseBid is forced to >= 1 when highestBid is 0)
```

### Python Helper (Recommended)

Provide:
- `highestBid` (from onchain `getAuctionHighestBid`)
- `startingBid` (from onchain `getAuctionInfo`, or from subgraph `startBidPrice`)
- `bidDecimals` and `stepMin` (from onchain getters or subgraph fields)

```bash
python3 - <<'PY'
highest_bid = int("<HIGHEST_BID_GHST_WEI>")     # replace
starting_bid = int("<STARTING_BID_GHST_WEI>")   # replace (0 if none)
bid_decimals = int("<BID_DECIMALS>")            # e.g. 100000
step_min = int("<STEP_MIN>")                    # e.g. 5000

base_bid = (highest_bid * (bid_decimals + step_min)) // bid_decimals
if base_bid == 0:
    base_bid = 1

min_next = max(starting_bid, base_bid)
print("minNextBid (GHST wei):", min_next)
PY
```

## Interpreting Presets (Rule of Thumb)

On Base mainnet, presets typically use:
- `bidDecimals = 100000`
- `stepMin` of `1000`, `5000`, or `10000`

This corresponds to a minimum step of roughly:
- `1%`, `5%`, or `10%` (because `stepMin / bidDecimals`)

Verify per-auction via subgraph fields or onchain getters:
- `getAuctionBidDecimals(auctionId)(uint256)`
- `getAuctionStepMin(auctionId)(uint64)`
