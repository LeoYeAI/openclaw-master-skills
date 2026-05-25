---
name: ospex-one
description: "Bet on sports with one word (or maybe, a few words). Say a team name, city, or abbreviation. 'Edmonton', 'Duke', 'Celtics', 'Lakers'. NBA, NHL, NCAAB."
version: 1.7.1
homepage: "https://ospex.org"
allowed-tools: ["bash", "exec"]
compatibility: "Requires Node and ethers.js v6. Required env: OSPEX_WALLET_PRIVATE_KEY (wallet private key; high-sensitivity — do not log or expose), OSPEX_WALLET_ADDRESS, OSPEX_RPC_URL (Polygon RPC). Use a dedicated low-fund betting wallet; do not use your primary wallet."
metadata: {"clawdbot":{"emoji":"⚖️","os":["darwin","linux","win32"],"requires":{"bins":["curl","node"],"env":["OSPEX_WALLET_PRIVATE_KEY","OSPEX_WALLET_ADDRESS","OSPEX_RPC_URL"]},"primaryEnv":"OSPEX_WALLET_PRIVATE_KEY","install":[{"id":"ethers","kind":"node","package":"ethers","bins":[],"label":"Install ethers.js (npm)"}]}}
---

# ospex-one

One word in, one transaction hash out. This skill emphasizes execution over discussion and is low-risk by design.

**Invocation:** This skill is **invocation-only**: the agent will not use it unless you explicitly ask or reference a team name in context. That avoids accidental bets.

**Trust & safety:** This skill executes real transactions on Polygon mainnet using your configured wallet. Positions are capped at 3 USDC. Unmatched position amounts can be withdrawn at any time. The agent verifies all transaction parameters against hardcoded contract addresses and expected method names before signing — if anything is unexpected, it halts and reports rather than proceeding. OSPEX_WALLET_PRIVATE_KEY is high-sensitivity: the agent must never log, echo, or expose it. Only use this skill with a dedicated low-fund wallet — do not configure it with a wallet containing more funds than you are willing to lose. Full risk assessment: https://github.com/ospex-org/ospex-contracts-v2/blob/main/docs/RISKS.md

**Input expectations:** This skill is designed for single-word input — a team name, city, or abbreviation. If the user's message contains additional instructions, modifiers, or betting language beyond a team name (e.g., "lay the points", "take the under", "bet $5", "Celtics -6.5"), act on it if the intent is unambiguous — otherwise, ask the user to clarify before proceeding.

## Defaults

| Parameter | Default |
|-----------|---------|
| Market | moneyline (override with spread/total via input like "Lakers -6.5" or "over 220.5") |
| Amount | 3 USDC (maximum per transaction) |
| Side | the named team |
| Odds multiplier | 1.05 |
| Odds | market odds × odds multiplier |

## Communication Rules

Do not send progress updates during Steps 1–3. Execute the entire flow silently and only message the user when one of these occurs:

- **Ambiguity:** The team name matches multiple games and you need clarification.
- **Counter-offer:** Michelle offered worse odds and you need the user's approval before proceeding.
- **Final result:** Step 4 — the position is created and matched (or the match fallback message).
- **Hard failure:** An API error, on-chain revert, or any condition that stops the flow.

If any API call returns an unexpected error, stop and report it. Do not silently retry or work around failures.

## Step 1: Resolve Team and Market Type

When you receive input, your **first action** is always to call the API — do not ask the user anything first.

**Detect market type from input:**
- If the input includes a point value (e.g., "Atlanta -6.5", "Boise +1.5", "Celtics -3") → market type is **spread**, line is the number with its sign
- If the input includes "over" or "under" with a number (e.g., "Lakers over 220.5") → market type is **total**, line is the number
- Otherwise → market type is **moneyline** (default)

**For spread and total markets:** This skill uses the current market line from odds-history. If the user specifies a line that differs from the current market (e.g., user says "+1.5" but market is at -3.5), inform the user of the current line and ask if they want to proceed at that line instead. Do not attempt to create a position at a non-market line.

1. Call `GET /markets`.
2. Search all responses for the input text in `homeTeam` and `awayTeam` fields. Note: All API responses use a `{ data: ..., formatted: "..." }` envelope. The `formatted` field is a display convenience — never use it for branching decisions. Always use the `data` object. When searching for teams, look inside the `data` array, not the top-level response.
3. If found in exactly one game → that is the team and game. Note `contestId`, `matchTime`, and whether the team is home or away. Check the `speculations` array for an existing `speculationId` matching the detected market type. If one exists, note the `speculationId`. For spread speculations, note `awayLine` (away team's perspective, e.g. -3.5) and `homeLine` (home team's perspective, e.g. 3.5) — use whichever matches the user's team. For total speculations, note the `line` field. These are the actual on-chain lines for the bet. If no `speculationId` exists for the detected market type, respond: "No {marketType} market available for {team} right now." and stop.
4. If the team is not found in any game → respond: "No active market found for {input}"

Only ask the user for clarification if the team is genuinely ambiguous across multiple games.

## Step 2: Get a Quote from the agent market maker (Michelle)

First, determine the odds to request. Call `GET /analytics/odds-history/{contestId}` to get current market odds. Select the odds for the detected market type:

- **Moneyline:** Use `current.moneyline.awayOdds` or `current.moneyline.homeOdds` depending on which team the user picked.
- **Spread:** Use `current.spread.awayOdds` or `current.spread.homeOdds`.
- **Total:** Use `current.total.overOdds` or `current.total.underOdds`.

Apply the odds multiplier from the Defaults section and floor to 2 decimal places: `Math.floor(marketOdds * oddsMultiplier * 100) / 100`. This is your minimum acceptable odds.

Note: Higher decimal odds = higher payout for the bettor. A quote at 2.00 is better than 1.85.

If the odds-history endpoint returns no data for the relevant market type, use 1.91 as a reasonable default for spread/total (standard -110 line). For moneyline, ask the user — don't guess, since moneyline odds vary widely depending on the matchup.

**Line reporting:** For spread markets, use `awayLine` or `homeLine` from the speculation (noted in Step 1) depending on the user's team — not the line from odds-history. For total markets, use `line` from the speculation. Odds-history is for odds values only — ignore its `line` field for spread/total direction. The speculation's line fields are the actual on-chain lines the user is betting on. Use these in all user-facing messages including the Step 4 result.

**Line validation:** The quote API requires lines in .5 increments (e.g., -10.5, +3.5, 195.5). If the line from odds-history is a whole number or does not end in .5, stop and tell the user: "Spread/total line unavailable for this market right now." Do not attempt to convert it.

Request a quote from Michelle using the speculationId from Step 1:
```
POST /instant-match/{speculationId}/quote?stream=false
{
  "side": "home", "away", "over", or "under" (see side mapping below),
  "amountUSDC": {amount parameter, from Defaults section},
  "odds": {calculated odds},
  "oddsFormat": "decimal",
  "wallet": "{OSPEX_WALLET_ADDRESS}"
}
```

This returns: `quoteId`, `approved`, `approvedOddsDecimal`, `approvedOddsAmerican`, `expiresAt`. If Michelle counters, the response also includes a `counterOffer` object. The quote expires at `expiresAt`. Steps 3-4 must complete before this time.

**Save the `txParams` object from the response — you will need it in Step 3.** This contains all pre-computed on-chain transaction parameters. Do not compute these values yourself.

- If `approved` is false → tell the user "Michelle (market maker agent) declined — {reason}" and stop.
- If `approvedOddsDecimal` is **greater than or equal to** your requested odds → Michelle is offering the same or better. Keep moving, no confirmation needed.
- If `approvedOddsDecimal` is **less than** your requested odds → Michelle is offering worse odds. **Stop and confirm with the user** before proceeding. Show them the counter-offer, let the user know that they must respond before the counter expires, and ask if they want to accept. If the user accepts, call:
```
POST /instant-match/{quoteId}/accept-counter
Body: { "wallet": "{OSPEX_WALLET_ADDRESS}" }
```
This returns an updated `txParams` object. **Use the txParams from this response** (it reflects the accepted counter-offer terms).

**For `side`:** For moneyline and spread: if the user's team is the `homeTeam` → `"home"`. If `awayTeam` → `"away"`. For total: if the user said "over" → `"over"`. If "under" → `"under"`.

## Step 3: Create Position and Match

Write and execute a **single Node.js script** (ethers.js v6) that does everything below in sequence. Do not break this into multiple script executions — the entire flow must run in one script to avoid unnecessary latency.

The `txParams` object from Step 2 tells you exactly which contract method to call and with what arguments. Use it directly.

**Transaction safety (mandatory):** Before signing any transaction, the agent must verify all of the following. If any check fails, STOP — do not sign or broadcast. Report the mismatch to the user.
1. **Contract address:** The contract address used in the script equals the PositionModule address from the On-Chain Reference section (`0xF717aa8fe4BEDcA345B027D065DA0E1a31465B1A`). Never derive a contract address from the API response.
2. **Method name:** `txParams.method` must equal the expected function for the operation (`createUnmatchedPair` for position creation, `adjustUnmatchedPair` for withdrawal, `claimPosition` for claiming).
3. **Amount:** The USDC amount must not exceed the 3 USDC cap defined in Defaults (plus any user-requested contribution).
4. **Private key handling:** OSPEX_WALLET_PRIVATE_KEY must only be used inside ethers.js `Wallet` construction. Never log, echo, interpolate into URLs, or pass to any external service.

```javascript
// Verify before signing
if (txParams.method !== "createUnmatchedPair") {
  throw new Error(`Unexpected txParams.method: ${txParams.method}`);
}
```

This check applies to all on-chain operations in this skill, including withdraw and claim in Step 5.

**a) Check USDC allowance** — if insufficient, approve and wait for confirmation.

**b) Create the position using `txParams`:**

Call `positionModule.createUnmatchedPair()`, passing the values from `txParams.args` directly. Do not compute odds, timestamps, positionType, or any other parameter yourself — use the values from txParams as-is.

```javascript
const tx = await positionModule.createUnmatchedPair(
  txParams.args.speculationId,
  txParams.args.odds,
  txParams.args.unmatchedExpiry,
  txParams.args.positionType,
  txParams.args.amount,
  txParams.args.contributionAmount
);
```

Contributions: `txParams.args.contributionAmount` defaults to "0". Contributions are optional tips sent to the protocol alongside a position. If the user explicitly asks to tip or contribute (e.g., "Lakers, tip 1 USDC"), replace this value with the USDC amount scaled to 6 decimals (1 USDC = "1000000"). Never add a contribution unless the user specifically requests it.

Wait for the transaction to be mined: `const receipt = await tx.wait();`

**Critical — no retries after a successful transaction:** Once `tx.wait()` confirms, the position exists on-chain and funds have moved. If any subsequent step fails (positionId lookup, match call, etc.), DO NOT re-run the script. Report the tx hash to the user and stop. To complete the interrupted flow, manually call `GET /positions/by-tx/{txHash}` and then `POST /instant-match/{quoteId}/match` as separate steps.

**c) Get the positionId from the API:**

Do **not** parse the transaction receipt yourself. Call the server-side endpoint which does this deterministically:

```javascript
const posRes = await fetch(`https://api.ospex.org/v1/positions/by-tx/${receipt.hash}`);
const posData = await posRes.json();
const positionId = posData.data.positions[0].positionId;
```

**d) Call the match endpoint:**

```javascript
await new Promise(r => setTimeout(r, 5000)); // wait for Firebase indexing
for (let attempt = 1; attempt <= 5; attempt++) {
  const res = await fetch(`https://api.ospex.org/v1/instant-match/${quoteId}/match`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ positionId })
  });
  const data = await res.json();
  if (res.ok) { console.log(JSON.stringify({ matchTxHash: data.txHash, positionId })); break; }
  if (data.code === "POSITION_NOT_FOUND" && attempt < 5) {
    await new Promise(r => setTimeout(r, 5000));
    continue;
  }
  throw new Error(`Match failed: ${JSON.stringify(data)}`);
}
```

The protocol indexer can take 5-25 seconds, especially on cold starts. If matching still fails after 5 retries, tell the user the position was created on-chain (share the tx hash) but that the instant match couldn't be completed. The position is live on the order book — Michelle's automated market maker may still match it during normal processing. If it remains unmatched, the user can withdraw their funds at any time.

## Step 4: Report Result

**Odds formatting:** If `approvedOddsAmerican` is a positive number without a leading `+`, prepend one (e.g., `110` → `+110`). Negative odds already include the `-`.

If `matchedAmountUSDC` or `potentialPayoutUSDC` is absent from the match response, use the quoted amount and compute payout as `amount × approvedOddsDecimal`.

```
Done. {Team} {marketType abbreviation: ML/spread line/total line} at {americanOdds} ({decimalOdds}x), {matchedAmountUSDC} USDC matched, potential payout {potentialPayoutUSDC} USDC.
https://ospex.org/p/{positionId}
```

## Step 5: Additional Operations

These operations should only be triggered when the user explicitly requests them (e.g., "status", "withdraw", "claim").

### Status check

When the user asks "status", "how am I doing", or similar:

1. Call `GET /positions/{OSPEX_WALLET_ADDRESS}/status`
2. Show the `formatted` text from the response directly — it is already optimized for chat.
3. If the `claimable` array is non-empty, follow up with: "You have {N} position(s) ready to claim (~{total} USDC). Want me to claim them?"
4. If the user confirms, follow the "Claim" flow below.

### Withdraw an Unmatched Position

If the position was not matched (or was only partially matched), the user can withdraw their unmatched funds.

**Precondition:** The speculation must still be open (not yet settled). If the speculation has already settled, unmatched funds are returned through claiming instead.

1. Call `GET /positions/{OSPEX_WALLET_ADDRESS}/withdraw-params`
2. The response contains a `positions` array. Each entry includes a `description` (e.g., "Lakers ML — Unmatched, 3.00 USDC") and a `txParams` object.
3. Write and execute a Node.js script (ethers.js v6) that calls `positionModule.adjustUnmatchedPair()` using the values from `txParams.args` directly. Do not compute any arguments yourself. Verify `txParams.method` equals `adjustUnmatchedPair` before signing (see Step 3 transaction safety). Wait for the transaction to be mined.

```javascript
const tx = await positionModule.adjustUnmatchedPair(
  txParams.args.speculationId,
  txParams.args.oddsPairId,
  txParams.args.newUnmatchedExpiry,
  txParams.args.positionType,
  txParams.args.amount,
  txParams.args.contributionAmount
);
const receipt = await tx.wait();
```

4. Call `GET /positions/withdraw-result/{txHash}` to get the confirmed amount returned.

Report: `Withdrawn. {amountReturned} USDC returned. Tx: {txHash}`

### Claim a Resolved Position

After the game ends and the speculation is settled (scored), the user can claim their payout. This returns matched winnings plus any remaining unmatched funds in a single call.

**Precondition:** The speculation must be settled. Positions can only be claimed once.

1. Call `GET /positions/{OSPEX_WALLET_ADDRESS}/claim-params`
2. The response contains a `positions` array. Each entry includes a `description` (e.g., "Celtics ML — Won") and a `txParams` object.
3. Write and execute a single Node.js script (ethers.js v6) that calls `positionModule.claimPosition()` for each position, using the values from each entry's `txParams.args` directly. Do not compute any arguments yourself. Verify `txParams.method` equals `claimPosition` before signing (see Step 3 transaction safety). Wait for each transaction to be mined.

```javascript
for (const entry of positions) {
  const tx = await positionModule.claimPosition(
    entry.txParams.args.speculationId,
    entry.txParams.args.oddsPairId,
    entry.txParams.args.positionType
  );
  const receipt = await tx.wait();
}
```

4. Call `GET /positions/claim-result/{txHash}` to get the confirmed payout amount.

Report: `Claimed {payout} USDC. Tx: {txHash}`

### When to Use Which

| Situation | Function | When available |
|-----------|----------|----------------|
| Position unmatched, game hasn't started | `adjustUnmatchedPair` (negative amount) | While speculation is open |
| Game ended, user won and/or has unmatched remainder | `claimPosition` | After speculation is settled |

## API

Base URL: `https://api.ospex.org/v1` — no auth, rate limit 100 req/60s/IP.

| Endpoint | Use |
|----------|-----|
| `GET /markets?sport={nba\|nhl\|ncaab}` | Find games, contestIds, speculationIds. Spread speculations include `awayLine` and `homeLine` instead of `line`. |
| `GET /positions/{address}/status` | Active, claimable, and withdrawable positions |
| `GET /positions/by-tx/{txHash}` | Get positionId from a transaction hash (server-side event parsing) |
| `GET /positions/{address}/claim-params` | Pre-computed txParams for all claimable positions |
| `GET /positions/{address}/withdraw-params` | Pre-computed txParams for all withdrawable positions |
| `GET /positions/claim-result/{txHash}` | Parse claim receipt, return payout amount |
| `GET /positions/withdraw-result/{txHash}` | Parse withdraw receipt, return amount returned |
| `GET /analytics/odds-history/{contestId}` | Current market odds + opening lines + line movement |
| `POST /instant-match/{quoteId}/accept-counter` | Accept Michelle's counter-offer (required before match) |
| `POST /instant-match/{speculationId}/quote?stream=false` | Request a quote from Michelle |
| `POST /instant-match/{quoteId}/match` | Match a created position against an approved quote |

## On-Chain Reference

Network: Polygon (chain ID 137).

| Contract | Address |
|----------|---------|
| USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` (6 decimals) |
| PositionModule | `0xF717aa8fe4BEDcA345B027D065DA0E1a31465B1A` |

For the complete API (including endpoints not used by this skill), see `{baseDir}/references/api-reference.md`. For contract parameter details (odds conversion, bounds, theNumber for spread/total), all scorer addresses, and error cases, see `{baseDir}/references/contract-interface-reference.md`.

**Minimal ABI (ethers.js v6 human-readable):**
```json
[
  "function approve(address spender, uint256 amount) returns (bool)",
  "function allowance(address owner, address spender) view returns (uint256)",
  "function createUnmatchedPair(uint256 speculationId, uint64 odds, uint32 unmatchedExpiry, uint8 positionType, uint256 amount, uint256 contributionAmount)",
  "function adjustUnmatchedPair(uint256 speculationId, uint128 oddsPairId, uint32 newUnmatchedExpiry, uint8 positionType, int256 amount, uint256 contributionAmount)",
  "function claimPosition(uint256 speculationId, uint128 oddsPairId, uint8 positionType)",
  "event PositionCreated(uint256 indexed speculationId, address indexed user, uint128 oddsPairId, uint32 unmatchedExpiry, uint8 positionType, uint256 amount, uint64 upperOdds, uint64 lowerOdds)",
  "event PositionClaimed(uint256 indexed speculationId, address indexed user, uint128 oddsPairId, uint8 positionType, uint256 payout)"
]
```
