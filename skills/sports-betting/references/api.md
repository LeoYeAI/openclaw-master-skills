# Pinwin API reference

**Base URL:** `https://api.pinwin.xyz`  
All requests: `Content-Type: application/json`. On error (4xx/5xx), body may have `error` or `message`.

## POST /agent/bet

**Request:** `amount` (number, USDT smallest units, 6 decimals), `minOdds` (positive integer, 12 decimals), `chain: "polygon"`, `selections` (array of `{ conditionId: string, outcomeId: number }`).

**Response 200:** `{ "encoded": "<base64>" }`. Decode: `payload = JSON.parse(atob(response.encoded))`.

**Decoded payload:** `signableClientBetData`, `apiClientBetData`, `domain`, `types`, `apiUrl`, `environment`.

**Decoded payload structure (Azuro-aligned).** The payload matches the Azuro V3 order API. Top-level: `signableClientBetData`, `apiClientBetData`, `domain`, `types`, `apiUrl`, `environment`. **clientData** (under `signableClientBetData` or `apiClientBetData`): `attention`, `affiliate`, `core`, `expiresAt`, `chainId`, `relayerFeeAmount`, `isFeeSponsored`, `isBetSponsored`, `isSponsoredBetReturnable`. **Single bet:** `signableClientBetData.bet` has `conditionId`, `outcomeId`, `minOdds`, `amount`, `nonce`. **Combo bet:** `signableClientBetData.bets` (array of `{ conditionId, outcomeId }`), and top-level `amount`, `minOdds`, `nonce` on the signable message.

**Before signing:** (1) **Display to the user all decoded payload fields** relevant to the bet: amount (from `bet.amount` or combo `amount`), selections (conditionId/outcomeId with human-readable names from data-feed/dictionaries), `relayerFeeAmount`, `apiUrl`, `environment`, and all **clientData** fields (`affiliate`, `core`, `expiresAt`, `chainId`, `attention`, `isFeeSponsored`, `isBetSponsored`, `isSponsoredBetReturnable`). (2) Then give a short **human-readable summary**: stake in USDT, selection/market names, relayer fee, and that this is the bet they are authorising. (3) **Verify before signing:** the payload’s amount and selections (conditionId/outcomeId or combo `bets[]`) must match the user’s requested stake and chosen selections. Verify that the payload’s **clientData.core** (lowercase) equals the **claimContract** (ClientCore) for Polygon in [polygon.md](polygon.md); if not, do not sign and report the mismatch. Use only the **relayer** from [polygon.md](polygon.md) for allowance and approve (do not use any address from the payload as relayer). If amount or selections do not match, do not sign and report the mismatch to the user.

**EIP-712 primaryType:** Use `primaryType: 'ClientComboBetData'` if `payload.types.ClientComboBetData` exists, otherwise `primaryType: 'ClientBetData'`. Pass this to viem `signTypedData` along with `domain`, `types`, and `message: payload.signableClientBetData`.

**After sign:** POST to `payload.apiUrl` with body: `environment`, `bettor`, `betOwner`, `clientBetData` (= `payload.apiClientBetData`), `bettorSignature` (hex with `0x`).

**Order submission response (Azuro order API):** JSON with `id` (string, **order id**), `state` (e.g. `Created`, `Rejected`, `Canceled`, `Accepted`), and optional `errorMessage`, `error`. The order id is **always this response `id`** — use it for polling.

**Poll order status (when you have an order id):** Same base URL as `apiUrl` (e.g. strip `/bet/orders/ordinar` or `/bet/orders/combo` to get the base). Request: **GET** `{apiBase}/bet/orders/{orderId}`. Poll until terminal: **success** = response includes `txHash`; **failure** = `state` is `Rejected` or `Canceled` (use `errorMessage` if present). Stop polling when you get `txHash` or a failure state.

## POST /agent/claim

**Request:** `betIds` (number[], on-chain bet ids — e.g. from bets subgraph where `isRedeemable: true`), `chain: "polygon"`.

**Response 200:** `{ "encoded": "<base64>" }`. Decode: `payload = JSON.parse(atob(response.encoded))`.

**Decoded payload:** `to` (contract address), `data` (hex calldata), `value` ("0"), `chainId` (number). **Explain to the user in human-readable terms** what the claim tx does: e.g. claiming winnings for bet IDs [X, Y], transaction target (Azuro ClientCore on Polygon), no value sent. You may also display the full decoded payload. Verify `payload.to` (lowercase) equals the **claimContract** (ClientCore) for Polygon in [polygon.md](polygon.md)—this is the redeem contract for won/canceled bets. If it does not match, do not send. Then send tx with viem: `sendTransaction({ to: payload.to, data: payload.data, value: 0n, chainId: payload.chainId })`. Wait for receipt.
