# Bets subgraph (history / status)

Use this subgraph to list a bettor’s bets and see whether each is **pending**, **resolved** (won/lost), or **canceled**, and whether it can be **redeemed**. This is a different endpoint from the data-feed (which serves games and conditions).

**URL (Polygon):** `https://thegraph.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-api-polygon-v3`  
**Header:** `Content-Type: application/json`.  
**Body:** JSON with `query` (string) and `variables` (object).

## Query

```graphql
query BettorBets($where: V3_Bet_filter!, $first: Int, $orderBy: V3_Bet_orderBy, $orderDirection: OrderDirection) {
  v3Bets(where: $where, first: $first, orderBy: $orderBy, orderDirection: $orderDirection) {
    betId
    status
    result
    isRedeemable
    isRedeemed
    amount
    payout
    createdBlockTimestamp
    resolvedBlockTimestamp
  }
}
```

## Example variables

`bettor` must be the wallet address in **lowercase**.

**All bets (any status):**
```json
{
  "where": { "bettor": "0xcdb8eaf44f1e22707df63bfad380b72aa1274e67" },
  "first": 50,
  "orderBy": "createdBlockTimestamp",
  "orderDirection": "desc"
}
```

**Only redeemable bets** (ready to claim): add `"isRedeemable": true` to `where`. Use this to get **betIds** for `POST /agent/claim` without filtering client-side.
```json
{
  "where": { "bettor": "0xcdb8eaf44f1e22707df63bfad380b72aa1274e67", "isRedeemable": true },
  "first": 50,
  "orderBy": "createdBlockTimestamp",
  "orderDirection": "desc"
}
```

## Response shape

`data.v3Bets` = array of bets. Each bet:

| Field | Meaning |
|-------|--------|
| **betId** | On-chain bet id (number). Use in Pinwin `POST /agent/claim` as `betIds[]`. |
| **status** | `Accepted` (pending) \| `Resolved` (settled) \| `Canceled` |
| **result** | `Won` \| `Lost` — only when `status === "Resolved"`. |
| **isRedeemable** | `true` if the user can claim (resolved or canceled, not yet redeemed). |
| **isRedeemed** | `true` if already claimed. |
| **amount** | Stake (human-readable). |
| **payout** | Payout when resolved (human-readable); present when won or canceled. |
| **createdBlockTimestamp** | When the bet was placed (Unix seconds). |
| **resolvedBlockTimestamp** | When the bet was settled (Unix seconds); when resolved. |

## How to use

- **Check if a bet is resolved:** `status === "Resolved"`. Then **result** tells **Won** or **Lost**.
- **Check if the user can redeem:** `isRedeemable === true` and `isRedeemed === false`. Collect those bets’ **betId** values and call Pinwin `POST /agent/claim` with `betIds: [<betId>, ...]` and `chain: "polygon"`, then sign and send the returned tx. See [api.md](api.md) and the skill Flow (claim).
