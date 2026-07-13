# GBM Auction Presets (Base)

Presets are stored onchain and copied into each auction at creation time.

Read a preset:
```bash
~/.foundry/bin/cast call "$GBM_DIAMOND" 'getAuctionPresets(uint256)((uint64,uint64,uint64,uint64,uint256))' 0 --rpc-url "$BASE_MAINNET_RPC"
```

Base mainnet presets (from the GBM repo deployment config; verify onchain):

Preset `0` (low):
- `incMin=500`
- `incMax=1000`
- `bidMultiplier=500`
- `stepMin=1000`
- `bidDecimals=100000`
- Interpreting `stepMin/bidDecimals`: ~`1%` minimum step (used in bid math)

Preset `1` (medium):
- `incMin=500`
- `incMax=5000`
- `bidMultiplier=4970`
- `stepMin=5000`
- `bidDecimals=100000`
- Interpreting `stepMin/bidDecimals`: ~`5%` minimum step

Preset `2` (high):
- `incMin=1000`
- `incMax=10000`
- `bidMultiplier=11000`
- `stepMin=10000`
- `bidDecimals=100000`
- Interpreting `stepMin/bidDecimals`: ~`10%` minimum step

Tip:
- If you are creating an auction for a specific contract and you want to match platform defaults, query recent auctions for that contract in the subgraph and copy the `presetId` used.
