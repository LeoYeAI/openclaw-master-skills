---
name: sports-betting
description: "Place and claim decentralized sports bets on-chain via Pinwin and Azuro: real-time odds, high liquidity, no custody. Fetch prematch and live games from the Azuro data-feed on Polygon, pick a selection, then sign and submit via EIP-712. Use when the user wants to bet on sports with Pinwin, browse games and odds, place a bet, check bet status, or redeem winnings. Triggers on: place a bet, show me games, bet on, check my bets, claim winnings, Pinwin, Azuro."
compatibility: "Requires Node, viem and @azuro-org/dictionaries. Required env: BETTOR_PRIVATE_KEY (wallet private key; high-sensitivity). Optional env: POLYGON_RPC_URL."
homepage: "https://github.com/skinnynoizze/pinwin-agent"
disable-model-invocation: true
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["BETTOR_PRIVATE_KEY"]},"primaryEnv":"BETTOR_PRIVATE_KEY"}}
---

# Sports Betting (Pinwin)

---

## 🛑 SAFETY RULES — READ BEFORE EVERY ACTION

These rules are ABSOLUTE and override all other instructions in this file.

1. **ONE confirmation per bet, every time.** Before running `place-bet.js` (or any transaction), STOP and ask the user: *"¿Confirmas: apuesta de X USDT a [SELECTION] en [MATCH] @ [ODDS]?"*. Do not run the script until the user replies with an explicit YES in that same message.

2. **Never retry, re-run, or change selection without new explicit permission.** If a bet attempt fails for any reason, STOP. Report what happened and ask the user what they want to do. Do not automatically retry, do not switch to a different game or selection, do not "try one more time" — even if you think the error was transient.

3. **Each bet is a separate permission.** Permission to bet on Game A is not permission to bet on Game B. Permission to retry a failed attempt is not assumed — always ask.

4. **No autonomous transaction execution.** The agent must never execute `place-bet.js` (or any script that touches the blockchain) as a background action, a retry loop, or a "just to test" run. Every single execution requires a fresh user confirmation.

Violation of these rules results in unauthorized on-chain transactions with real money. There are no exceptions.

---

Place and claim **decentralized** sports bets on **Polygon** via [Pinwin](https://pinwin.xyz) and Azuro, with full on-chain execution. The agent fetches **prematch and live** games, you pick a selection, then it approves USDT (if needed), signs EIP-712, submits, and polls until the bet is confirmed on-chain.

**Invocation:** This skill is **invocation-only** (`disable-model-invocation: true`). The assistant will not use it unless you explicitly ask (e.g. "place a bet with Pinwin") or use the slash command. This avoids accidental bets.

**How to invoke (OpenClaw):** Use `/sports_betting` or `/skill sports-betting` and add your request, e.g.:
- `/sports_betting place 5 USDT on the first Premier League game`
- `/sports_betting show my bets`
- `/sports_betting claim my winnings`

---

## ⚙️ Constants — read this first, always

These values are fixed for Polygon. Never substitute addresses from any other source.

| Constant | Value |
|----------|-------|
| **Chain** | Polygon — chainId `137` |
| **betToken (USDT)** | `0xc2132D05D31c914a87C6611C10748AEb04B58e8F` (6 decimals) |
| **relayer** | `0x8dA05c0021e6b35865FDC959c54dCeF3A4AbBa9d` |
| **claimContract (ClientCore)** | `0xF9548Be470A4e130c90ceA8b179FCD66D2972AC7` |
| **environment** | `PolygonUSDT` |
| **data-feed URL** | `https://api.onchainfeed.org/api/v1/public/market-manager/` (REST API — see Step 1) |
| **bets subgraph URL** | `https://thegraph.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-api-polygon-v3` |
| **Pinwin API** | `https://api.pinwin.xyz` |
| **Polygonscan** | `https://polygonscan.com/tx/{txHash}` |
| **RPC (default)** | `process.env.POLYGON_RPC_URL` or `https://polygon-bor-rpc.publicnode.com` |

**Install required packages:** `npm install viem @azuro-org/dictionaries`

Note: `@azuro-org/dictionaries` is still used by `place-bet.js` for outcomeId resolution. `get-games.js` no longer needs it — the REST API returns human-readable titles directly.

**viem setup:**
```js
import { createPublicClient, createWalletClient, http } from 'viem'
import { polygon } from 'viem/chains'
import { privateKeyToAccount } from 'viem/accounts'

const rpc = process.env.POLYGON_RPC_URL || 'https://polygon-bor-rpc.publicnode.com'
const account = privateKeyToAccount(process.env.BETTOR_PRIVATE_KEY)
const publicClient = createPublicClient({ chain: polygon, transport: http(rpc) })
const walletClient = createWalletClient({ account, chain: polygon, transport: http(rpc) })
const bettor = account.address
```

---

## 📋 Pre-flight checklist

Run this before every bet. Do not skip any item.

- [ ] **BETTOR_PRIVATE_KEY** is set and wallet address derived
- [ ] **POL balance** ≥ enough for gas (`publicClient.getBalance({ address: bettor })`)
- [ ] **USDT balance** ≥ stake (`readContract` on betToken with `balanceOf`)
- [ ] **Selected condition** `state === "Active"` — re-check immediately before calling `/agent/bet`, not just at game fetch time
- [ ] **Allowance** checked and approved if needed (see Step 5)

If any check fails, inform the user and stop. Do not proceed.

---

## Flow — place a bet

### Step 0 — Check balances

```js
const erc20Abi = parseAbi([
  'function balanceOf(address) view returns (uint256)',
  'function allowance(address,address) view returns (uint256)',
  'function approve(address,uint256) returns (bool)',
])
const USDT = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'

const pol = await publicClient.getBalance({ address: bettor })
const usdt = await publicClient.readContract({ address: USDT, abi: erc20Abi, functionName: 'balanceOf', args: [bettor] })
```

- `pol` must be > 0 (for gas). **Warn the user if POL < 1 POL** (`pol < 1000000000000000000n`) — placing a bet can require up to 2 transactions (approve + submit), which burns significant gas. Suggested message: "⚠️ Your POL balance is low ({pol} POL). You need gas for up to 2 txs. Consider topping up before proceeding."
- `usdt` must be ≥ stake in 6-decimal units (e.g. 2 USDT = `2000000n`)
- If either is insufficient, stop and inform the user

### Step 1 — Fetch games

**CRITICAL — use the bundled script, do not call the REST API manually.**

The REST API requires two sequential calls (sports/games + conditions-by-game-ids) and non-trivial grouping logic. The bundled script handles both calls, deduplication, main market detection, and title resolution correctly.

```bash
# Install once (if not already installed):
npm install @azuro-org/dictionaries

# Browse by sport/league:
node scripts/get-games.js                              # top 20 games, all sports
node scripts/get-games.js basketball nba 10            # NBA only
node scripts/get-games.js football premier-league 10   # Premier League
node scripts/get-games.js hockey 5                     # NHL

# Search by team or match name:
node scripts/get-games.js --search "Real Madrid"       # find Real Madrid games
node scripts/get-games.js --search "Celtics" 3         # find Celtics games
node scripts/get-games.js --search "Lakers vs" 5       # find Lakers matchups
```

**When to use --search vs sport/league filter:**
- Use `--search` when the user mentions a specific team, player, or match by name
- Use sport/league filters when the user asks for a list of games (e.g. "show me NBA tonight")
- `--search` queries across all sports and leagues simultaneously

The script outputs:
1. A **clean human-readable list** with main market odds per game — show this to the user
2. A `---JSON---` block with machine-readable data — use the `conditionId` and `outcomeId` values from this for bet placement in Step 2

Optional GraphQL filters still available if the user requests by country or time window — pass them as additional arguments or modify the script call. See `references/subgraph.md` for all filter options.

**The script handles all translation and filtering automatically.** Show its human-readable output directly to the user.

**Secondary markets** (only if user explicitly asks — e.g. "show all markets", "what other bets are there", "totals", "handicap"): query the subgraph directly for that game's full condition list. See `references/subgraph.md`.

**CRITICAL — how to identify the main market condition:**

Each game returns multiple conditions from the subgraph. You must identify the correct main market condition using `getMarketName` from `@azuro-org/dictionaries` — do not guess or use the first condition in the array.

**Verified main market names from `@azuro-org/dictionaries` (confirmed by scanning the full package):**

| Market name | Outcomes | Sports |
|-------------|----------|--------|
| `"Match Winner"` | 2: `"1"`, `"2"` | Basketball (NBA), Tennis, Esports, most 1v1 |
| `"Full Time Result"` | 3: `"1"`, `"X"`, `"2"` | Football/Soccer |
| `"Winner"` | 2: `"1"`, `"2"` | Hockey (NHL), MMA, some others |
| `"Fight Winner"` | 2: `"1"`, `"2"` | MMA/Boxing specifically |
| `"Whole game - Full time result Goal"` | 3: `"1"`, `"X"`, `"2"` | Football variant |

These are the **exact strings** returned by `getMarketName({ outcomeId })`. Do not invent or assume market names — always derive them from the dictionary.

```js
import { getMarketName, getSelectionName } from '@azuro-org/dictionaries'

// All known main market names — verified against @azuro-org/dictionaries
const MAIN_MARKET_NAMES = [
  'Match Winner',                        // Basketball, Tennis, Esports
  'Full Time Result',                    // Football/Soccer (3-way: 1 X 2)
  'Winner',                              // Hockey (NHL), MMA, others
  'Fight Winner',                        // MMA/Boxing
  'Whole game - Full time result Goal',  // Football variant
]

// For each game, find the main market condition:
const mainCondition = game.conditions
  .filter(c => c.state === 'Active')
  .find(c => {
    try {
      const name = getMarketName({ outcomeId: c.outcomes[0].outcomeId })
      return MAIN_MARKET_NAMES.includes(name)
    } catch { return false }
  })

if (!mainCondition) {
  // No main market active — skip game in default view
  return
}

// Map outcome selections to display labels:
// "1" = participants[0] (home), "2" = participants[1] (away), "X" = Draw
mainCondition.outcomes.forEach(o => {
  const selection = getSelectionName({ outcomeId: o.outcomeId, withPoint: true })
  const label = selection === '1' ? game.participants[0].name
              : selection === '2' ? game.participants[1].name
              : 'Draw'
  console.log(label, '@', o.currentOdds)
})
```

- If multiple Active conditions match `MAIN_MARKET_NAMES`, use the first one in the array.
- If no condition matches, show the game with "No active main market — ask for all markets to see available options" and skip it in the default view.
- **Never hardcode outcomeIds** — always resolve market names via `getMarketName` at runtime.

Example default output:
```
🏀 NBA — Tonight
1. Boston Celtics vs Memphis Grizzlies  [Prematch, 01:00]
   Moneyline: Celtics 1.07 | Grizzlies 7.92

2. Toronto Raptors vs Denver Nuggets  [Prematch, 00:30]
   Moneyline: Raptors 3.21 | Nuggets 1.31

3. Dallas Mavericks vs Cleveland Cavaliers  [LIVE 🔴]
   Moneyline: Mavericks 2.10 | Cavaliers 1.68
```

Never output raw `outcomeId` numbers, condition arrays, or unfiltered API responses. If no Active conditions exist for the main market, show the game with "No active main market — ask for all markets to see available options."

### Step 2 — Choose selection

Ask the user which game and selection they want. Use the `---JSON---` output from the script to get the exact values needed for bet placement — do not re-query the subgraph.

```
// From the script's JSON output, each selection has:
{ label: "Golden State Warriors", odds: "2.67", outcomeId: 6983, conditionId: "1006..." }
```

Get from the chosen selection:
- `conditionId` (string) — from the JSON output
- `outcomeId` (number) — from the JSON output  
- `currentOdds` (string) — from the JSON output (`odds` field)

**CRITICAL — use the bundled script for bet placement, do not implement Steps 3-7 inline.**

Once the user confirms, run:

```bash
node scripts/place-bet.js --stake <USDT> --outcome <outcomeId> --condition <conditionId> --odds <currentOdds> --starts-at <startsAt> --match "<Team A vs Team B>"
```

Example:
```bash
node scripts/place-bet.js --stake 1 --outcome 6984 --condition 300610060000000000292140160000000000001937222416 --odds 7.92 --starts-at 1774047000 --match "Boston Celtics vs Memphis Grizzlies"
```

- `--starts-at` and `--match` come from the `---JSON---` output of `get-games.js` (`startsAt` and `title` fields). Always pass them — they enable automatic result notification via `watch-bets.js`.
- If `--starts-at` is provided, the script automatically launches `watch-bets.js` in background after the bet is confirmed. No extra action needed.

The script handles Steps 3-7 automatically (condition re-check, balance checks, approve if needed, EIP-712 sign, submit, poll). Do not attempt to run these steps manually or look for other scripts. The only three scripts are `get-games.js` (fetch), `place-bet.js` (bet), and `watch-bets.js` (result notification).

Compute `minOdds` (for reference only — the script does this internally):
- Single bet: `minOdds = Math.round(parseFloat(currentOdds) * 1e12)`
- Combo bet: multiply each leg's odds in 12-decimal space, dividing by `1e12n` per extra leg:

```js
// Example: 2-leg combo with odds 2.5 and 1.8 → combined odds 4.5
// leg1: 2.5 → 2_500_000_000_000n
// leg2: 1.8 → 1_800_000_000_000n
// combined: (2_500_000_000_000n * 1_800_000_000_000n) / 1_000_000_000_000n = 4_500_000_000_000n

const toOdds12 = (o) => BigInt(Math.round(parseFloat(o) * 1e12))
const minOdds = [odds1, odds2, ...oddsN].reduce(
  (acc, o) => (acc * toOdds12(o)) / 1_000_000_000_000n,
  1_000_000_000_000n
)
```

**CRITICAL — re-check the condition is still Active immediately before calling `/agent/bet`:**
```json
GET https://api.onchainfeed.org/api/v1/public/market-manager/conditions-by-game-ids with { "gameIds": [...], "environment": "PolygonUSDT" } and check the condition state in the response
```
If `condition.state !== "Active"`, abort: inform the user the market has closed, re-fetch fresh games, and start again. Do not call `/agent/bet` on a closed condition.

### Step 3 — Call Pinwin

> **NOTE: Steps 3-7 are implemented by `scripts/place-bet.js`. Run the script (see Step 2) and do not execute these steps manually. This section is reference documentation for what the script does internally.**

```
POST https://api.pinwin.xyz/agent/bet
Content-Type: application/json

{
  "amount": <stake in USDT 6-decimal units, e.g. 2000000 for 2 USDT>,
  "minOdds": <computed above>,
  "chain": "polygon",
  "selections": [{ "conditionId": "<string>", "outcomeId": <number> }]
}
```

For combo, add more objects to `selections`.

Response: `{ "encoded": "<base64>" }`. Decode:
```js
const payload = JSON.parse(atob(response.encoded))
```

### Step 4 — Explain to user before signing

**Always show the full decoded payload before any approval or signing.** The user must understand and confirm what they are authorising.

Display:
- Stake: `amount` in USDT (divide by 1e6), e.g. "2.00 USDT"
- Selection(s): human-readable names (from dictionaries), conditionId, outcomeId
- Relayer fee: `relayerFeeAmount` (divide by 1e6), e.g. "0.05 USDT"
- Total USDT needed: stake + relayerFeeAmount
- `apiUrl`, `environment`, `expiresAt`, `affiliate`, `isFeeSponsored`, `isBetSponsored`

Then ask for explicit confirmation before proceeding.

### Step 5 — Approve USDT (if needed)

**CRITICAL — never skip this step.**

```js
const relayer = '0x8dA05c0021e6b35865FDC959c54dCeF3A4AbBa9d'
const USDT    = '0xc2132D05D31c914a87C6611C10748AEb04B58e8F'
const relayerFeeAmount = BigInt(payload.signableClientBetData.clientData?.relayerFeeAmount ?? 0)
const stakeAmount      = BigInt(payload.signableClientBetData.bet?.amount ?? payload.signableClientBetData.amount)
const buffer           = 200000n // 0.2 USDT in 6-decimal units
const required         = stakeAmount + relayerFeeAmount + buffer

const allowance = await publicClient.readContract({
  address: USDT, abi: erc20Abi, functionName: 'allowance', args: [bettor, relayer]
})

if (allowance < required) {
  const approveTx = await walletClient.sendTransaction({
    to: USDT,
    data: encodeFunctionData({ abi: erc20Abi, functionName: 'approve', args: [relayer, required] })
  })
  await publicClient.waitForTransactionReceipt({ hash: approveTx })
  // Inform user: "USDT approval confirmed."
}
```

### Step 6 — Verify payload

Before signing, verify:

1. `payload.signableClientBetData.bet.amount` (single) or `payload.signableClientBetData.amount` (combo) matches the user's requested stake
2. `conditionId` and `outcomeId` in the payload match the user's chosen selection(s)
3. `payload.signableClientBetData.clientData.core.toLowerCase()` === `0xf9548be470a4e130c90cea8b179fcd66d2972ac7` (claimContract)

If any check fails, **do not sign**. Report the mismatch to the user and stop.

### Step 7 — Sign, submit, and poll

```js
// Determine primaryType
const primaryType = payload.types.ClientComboBetData ? 'ClientComboBetData' : 'ClientBetData'

// Sign
const bettorSignature = await walletClient.signTypedData({
  account,
  domain: payload.domain,
  types: payload.types,
  primaryType,
  message: payload.signableClientBetData,
})

// Submit to Azuro order API
const submitRes = await fetch(payload.apiUrl, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    environment: payload.environment,
    bettor,
    betOwner: bettor,
    clientBetData: payload.apiClientBetData,
    bettorSignature,
  })
})
const submitData = await submitRes.json()
```

If submission fails (4xx/5xx or `state: "Rejected"` / `"Canceled"`), report `submitData.errorMessage` or `submitData.error` to the user and stop.

**CRITICAL — poll until txHash. Do not declare success on `state: "Created"`.**

The order is only on-chain when `txHash` is present. `state: "Created"` is only an initial state — the bet is NOT confirmed yet.

```js
// Derive base URL from apiUrl
// e.g. "https://api.onchainfeed.org/v1/bet/orders/ordinar" → "https://api.onchainfeed.org/v1"
const apiBase = payload.apiUrl.replace(/\/bet\/orders\/(ordinar|combo)$/, '')
const orderId = submitData.id

let txHash = null
for (let i = 0; i < 30; i++) {
  const delayMs = Math.min(2000 + (i * 1000), 10000) // progressive backoff: 2s, 3s, 4s … 10s max
  await new Promise(r => setTimeout(r, delayMs))
  const poll = await fetch(`${apiBase}/bet/orders/${orderId}`).then(r => r.json())
  if (poll.txHash) { txHash = poll.txHash; break }
  if (poll.state === 'Rejected' || poll.state === 'Canceled') {
    // Report failure and stop
    throw new Error(`Order ${poll.state}: ${poll.errorMessage || 'unknown error'}`)
  }
}

if (!txHash) throw new Error('Order did not settle after 90s — check manually on Polygonscan')
```

**On success**, show the user:
```
✅ Bet confirmed on-chain!
   Match:      {teams}
   Selection:  {market} — {selection} @ {odds}
   Stake:      {stake} USDT
   To win:     {potential payout} USDT
   Tx:         https://polygonscan.com/tx/{txHash}
```

---

## Flow — resume interrupted flow

If the user resumes a bet request after an interruption (e.g. session ended mid-flow), check current state before starting over to avoid double-approvals or duplicate bets:

1. **Check allowance** — if `allowance(bettor, relayer) >= stake + fee`, approval was already sent. Skip Step 5.
2. **Check for pending bets** — query the bets subgraph for `status: "Accepted"` bets from this wallet placed in the last 10 minutes. If found, poll that order instead of creating a new one.
3. If no pending bet found and no clear state, start the flow from Step 1 with a fresh game fetch.

---

## Flow — check bet status

Query the bets subgraph to see pending, resolved, or redeemable bets.

```
POST https://thegraph.onchainfeed.org/subgraphs/name/azuro-protocol/azuro-api-polygon-v3
Content-Type: application/json

{
  "query": "query BettorBets($where: V3_Bet_filter!, $first: Int, $orderBy: V3_Bet_orderBy, $orderDirection: OrderDirection) { v3Bets(where: $where, first: $first, orderBy: $orderBy, orderDirection: $orderDirection) { betId status result isRedeemable isRedeemed amount payout createdBlockTimestamp resolvedBlockTimestamp } }",
  "variables": {
    "where": { "bettor": "<address in lowercase>" },
    "first": 50,
    "orderBy": "createdBlockTimestamp",
    "orderDirection": "desc"
  }
}
```

To fetch only redeemable bets: add `"isRedeemable": true` to `where`.

**Interpret results:**

| `status` | `result` | `isRedeemable` | Meaning |
|----------|----------|----------------|---------|
| `Accepted` | — | false | Pending — not settled yet |
| `Resolved` | `Won` | true | Won — claim available |
| `Resolved` | `Lost` | false | Lost |
| `Canceled` | — | true | Canceled — stake refundable |
| `Resolved` | `Won` | false | Already claimed |

**On invocation, always check for newly resolved bets** from previous sessions and surface them proactively:
> "You have a resolved bet: {match} — {selection} — **{Won/Lost}**. Payout: {payout} USDT."
> If won: "Would you like to claim your winnings?"

---

## Flow — claim

Only for bets where `isRedeemable === true` and `isRedeemed === false`. Collect `betId` values from the subgraph.

### Step 1 — Call Pinwin

```
POST https://api.pinwin.xyz/agent/claim
Content-Type: application/json

{ "betIds": [<betId>, ...], "chain": "polygon" }
```

Decode: `payload = JSON.parse(atob(response.encoded))`

Explain to the user in plain terms: "This transaction claims your winnings for bet IDs [X, Y] from the Azuro ClientCore contract on Polygon. No ETH/POL value is sent."

Display the full decoded payload: `to`, `data`, `value`, `chainId`.

### Step 2 — Verify claim contract

**CRITICAL:** `payload.to.toLowerCase()` must equal `0xf9548be470a4e130c90cea8b179fcd66d2972ac7`.

If it does not match, **do not send the transaction**. Report the mismatch and stop.

### Step 3 — Send and confirm

```js
const claimTx = await walletClient.sendTransaction({
  to: payload.to,
  data: payload.data,
  value: 0n,
  chainId: payload.chainId,
})
await publicClient.waitForTransactionReceipt({ hash: claimTx })
```

On success, show:
```
✅ Winnings claimed!
   Bet IDs:  {betIds}
   Tx:       https://polygonscan.com/tx/{claimTx}
```

---

## Tools summary

| Step | Tool | Purpose |
|------|------|---------|
| Balance check | viem `getBalance`, `readContract` | POL gas, USDT balance and allowance |
| Fetch games | Data-feed subgraph (GraphQL) | Prematch/live games, conditions, odds |
| Translate odds | `@azuro-org/dictionaries` | `outcomeId` → human-readable market/selection names |
| Place bet | `POST /agent/bet` | Get encoded EIP-712 payload |
| Sign | viem `signTypedData` | EIP-712 bet signature |
| Submit | Azuro order API (`payload.apiUrl`) | Submit signed bet |
| Poll | `GET {apiBase}/bet/orders/{orderId}` | Wait for `txHash` confirmation |
| Watch result | `scripts/watch-bets.js` (auto-launched by `place-bet.js`) | Waits until kickoff + 2h, queries bets subgraph, notifies user via sendPrompt |
| Bet status | Bets subgraph (GraphQL) | Check status, result, isRedeemable |
| Claim | `POST /agent/claim` + viem `sendTransaction` | Redeem winnings on-chain |

---

## Error handling

| Error | Cause | Action |
|-------|-------|--------|
| `state: "Rejected"` / `"Canceled"` on order | Invalid bet, market moved, odds expired | Report `errorMessage`, do not retry automatically |
| Empty order ID from submission | Condition no longer Active (market closed) | Re-check condition state, re-fetch games |
| `allowance` < required | USDT not approved | Run Step 5 (approve) before signing |
| `txHash` not received after 90s | Relayer slow or order stuck | Show last known order state, give orderId for manual check on Polygonscan |
| Subgraph returns 200 with `data.errors` | GraphQL error | Read `data.errors[0].message`, report to user |
| POL balance = 0 | No gas | Inform user to fund wallet with POL for gas |
| Payload stake = 0 after `/agent/bet` | **Always run `place-bet.js --dry-run` first to see request body.** Likely causes: (1) `outcomeId` not valid for that `conditionId` — always take both from the same entry in the `---JSON---` output of `get-games.js`, never mix them; (2) `conditionId` format wrong (must be string, not number); (3) Pinwin API temporarily down — retry after 2 min. Do NOT diagnose this by eye — use `--dry-run` to inspect the exact request body then compare with the condition in the data-feed. |

---

## Reference files

Load only if you need full detail beyond what is in this file:

- [`references/api.md`](references/api.md) — Full Pinwin `/agent/bet` and `/agent/claim` request/response schemas, EIP-712 payload structure, combo bet details
- [`references/subgraph.md`](references/subgraph.md) — Data-feed GraphQL query, all filter/orderBy options, full response shape
- [`references/bets-subgraph.md`](references/bets-subgraph.md) — Bets subgraph query, all fields, pagination
- [`references/dictionaries.md`](references/dictionaries.md) — `@azuro-org/dictionaries` full API
- [`references/viem.md`](references/viem.md) — viem full setup, all chain calls
- [`references/polygon.md`](references/polygon.md) — All Polygon addresses and URLs (same as Constants table above)
