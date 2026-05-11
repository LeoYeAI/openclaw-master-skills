# Polygon addresses

Chain ID **137**. Polygon production.

**RPC (defaults):** If `POLYGON_RPC_URL` is not set, use one of these — try in order if the first fails:
- `https://poly.api.pocket.network`
- `https://polygon-bor-rpc.publicnode.com` ([PublicNode](https://polygon-bor-rpc.publicnode.com))

| Field | Value |
|-------|--------|
| **native gas token** | POL (for gas: approve, claim txs) |
| **data-feed URL** | `https://thegraph-1.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-data-feed-polygon` |
| **bets subgraph URL** | `https://thegraph.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-api-polygon-v3` |
| **relayer** | `0x8dA05c0021e6b35865FDC959c54dCeF3A4AbBa9d` (for USDT approval; verify bet payload does not override) |
| **betToken** | `0xc2132d05d31c914a87c6611c10748aeb04b58e8f` (USDT, **6 decimals**) |
| **core** (ClientCore) | `0xF9548Be470A4e130c90ceA8b179FCD66D2972AC7` (for bet payload clientData.core; same as claimContract) |
| **claimContract** (ClientCore, redeem won/canceled bets) | `0xF9548Be470A4e130c90ceA8b179FCD66D2972AC7` |
| **environment** | `PolygonUSDT` |
