You are creating an OpenClaw AgentSkill named ospex-one.

**Goal:** produce a single SKILL.md file that exactly matches ospex-one **version 1.7.1** behavior/spec.

This is a "generate-your-own-skill" prompt for users who prefer not to install from a third-party registry. The output SKILL.md must be self-contained and executable as an OpenClaw skill procedure.

## Output requirements (strict)

- Output **only** the contents of `SKILL.md` (Markdown). No commentary.
- Include YAML frontmatter with at least:
  - `name: ospex-one`
  - `description`: mention one-word sports bet; examples; supported leagues NBA/NHL/NCAAB
  - `version: 1.7.1`
  - `homepage: https://ospex.org`
  - `allowed-tools`: include what's required to run Node and shell commands
  - `compatibility`: a short sentence covering runtime requirements (Node, ethers.js v6), required env vars with sensitivity notes for `OSPEX_WALLET_PRIVATE_KEY`, and a reminder to use a dedicated low-fund wallet
  - `metadata` suitable for ClawHub/OpenClaw that declares:
    - Supported OSes
    - Required binaries: `curl`, `node`
    - Required env vars: `OSPEX_WALLET_PRIVATE_KEY`, `OSPEX_WALLET_ADDRESS`, `OSPEX_RPC_URL`
    - Optional install hint for ethers (npm)
- The body must be a complete, agent-executable procedure with clear steps and exact API calls / behaviors.
- Include an **Invocation** paragraph stating the skill is **invocation-only**: the agent will not use it unless the user explicitly asks or references a team name in context. This avoids accidental bets.

## Hard constraints (do not deviate)

- Keep user-facing messages minimal and operational.
- No marketing tone.
- No emojis in the SKILL body (frontmatter metadata may include platform emoji if standard).
- Do not add extra files. Do not reference any local scripts. Everything must be described within SKILL.md.
- Use Ospex API + on-chain calls exactly as specified below.
- **Critical:** For on-chain calls, do **not** compute transaction arguments yourself. You must use the `txParams` object returned by the quote/counter-accept endpoints.

## Required SKILL.md content (spec)

### Trust & safety

- Include a **Trust & safety** paragraph that:
  - States this skill executes real transactions on Polygon mainnet using the configured wallet.
  - Cap position size at **3 USDC** per transaction by default.
  - Mentions unmatched funds can be withdrawn at any time.
  - States the agent verifies all transaction parameters against hardcoded contract addresses and expected method names before signing — if anything is unexpected, it halts and reports rather than proceeding.
  - States OSPEX_WALLET_PRIVATE_KEY is high-sensitivity: the agent must never log, echo, or expose it.
  - States this skill should only be used with a dedicated low-fund wallet — do not configure it with a wallet containing more funds than you are willing to lose.
  - Links to the canonical risks doc: https://github.com/ospex-org/ospex-contracts-v2/blob/main/docs/RISKS.md

### Input expectations

- This skill is designed for single-word input — a team name, city, or abbreviation.
- If the user's message contains additional modifiers (spread/total language, amount language, etc.), proceed if intent is unambiguous; otherwise ask a single clarification question.

### Defaults section

Define defaults in a small table:

- Market: moneyline (but allow override to spread/total via input like `Lakers -6.5` or `over 220.5`)
- Amount: 3 USDC (maximum per transaction)
- Side: the named team
- Odds multiplier: 1.05
- Odds: market odds × multiplier

### Communication Rules

Instruct the agent to execute the entire flow silently (Steps 1–3) and only message the user when one of these occurs:

- **Ambiguity:** The team name matches multiple games and clarification is needed.
- **Counter-offer:** Michelle offered worse odds and the user's approval is needed before proceeding.
- **Final result:** Step 4 — the position is created and matched (or the match fallback message).
- **Hard failure:** An API error, on-chain revert, or any condition that stops the flow.

If any API call returns an unexpected error: stop and report it. Do not silently retry or work around failures.

### Step 1 — Resolve team and market type

On any input: your **first action** is always to call the API (do not ask the user anything first).

Detect market type from input:
- If input includes a point value (e.g., `Atlanta -6.5`, `Boise +1.5`, `Celtics -3`) → market type = **spread**, line = that signed number
- If input includes `over` or `under` with a number (e.g., `Lakers over 220.5`) → market type = **total**, line = that number
- Else → market type = **moneyline**

For spread/total:
- This skill uses the **current market line** from odds-history.
- If the user-specified line differs from the market's current line: inform the user of the current line and ask if they want to proceed at the market line. Do not create a position at a non-market line.

Procedure:
1. Call `GET /markets`.
2. Search all responses for the input text in `homeTeam` and `awayTeam`.
   - Note: All API responses use a `{ data: ..., formatted: "..." }` envelope. The `formatted` field is a display convenience — never use it for branching decisions. Always use the `data` object. When searching for teams, look inside the `data` array, not the top-level response.
3. If found in exactly one game: capture `contestId`, `matchTime`, whether the selected team is home/away.
   - Check the `speculations` array for an existing `speculationId` matching the detected market type. If one exists, note the `speculationId`. For spread speculations, note `awayLine` (away team's perspective, e.g. -3.5) and `homeLine` (home team's perspective, e.g. 3.5) — use whichever matches the user's team. For total speculations, note the `line` field. These are the actual on-chain lines for the bet.
   - If no `speculationId` exists for the detected market type, respond: "No {marketType} market available for {team} right now." and stop.
4. If not found: respond exactly `No active market found for {input}`.

Only ask for clarification if the team is genuinely ambiguous across multiple games.

### Step 2 — Get a quote from the agent market maker (Michelle)

First determine requested odds:
- Call `GET /analytics/odds-history/{contestId}`.
- Select current odds for the detected market type:
  - Moneyline: `current.moneyline.awayOdds` or `current.moneyline.homeOdds` depending on user team
  - Spread: `current.spread.awayOdds` or `current.spread.homeOdds`
  - Total: `current.total.overOdds` or `current.total.underOdds`

Apply odds multiplier and floor to 2 decimals:
- `Math.floor(marketOdds * oddsMultiplier * 100) / 100`

Notes:
- Higher decimal odds = better payout for the bettor.
- If odds-history returns no data:
  - spread/total: use **1.91** default
  - moneyline: ask the user what odds they want (do not guess)

Line reporting:
- For spread markets, use `awayLine` or `homeLine` from the speculation (noted in Step 1) depending on the user's team — not the line from odds-history. For total markets, use `line` from the speculation. Odds-history is for odds values only — ignore its `line` field for spread/total direction. The speculation's line fields are the actual on-chain lines the user is betting on. Use these in all user-facing messages including the Step 4 result.

Line validation:
- Quote API requires .5 increments for spread/total. If the odds-history line is a whole number or does not end in .5: stop and tell the user:
  - `Spread/total line unavailable for this market right now.`
  - Do not attempt to convert.

Quote request:

Request a quote from Michelle using the speculationId from Step 1:
```
POST /instant-match/{speculationId}/quote?stream=false
{
  "side": "home" | "away" | "over" | "under",
  "amountUSDC": 3,
  "odds": {calculatedOddsDecimal},
  "oddsFormat": "decimal",
  "wallet": "{OSPEX_WALLET_ADDRESS}"
}
```

This returns: `quoteId`, `approved`, `approvedOddsDecimal`, `approvedOddsAmerican`, `expiresAt`, optional `counterOffer`, and **`txParams`**.

Rules:
- **Save `txParams`** — it contains all pre-computed on-chain parameters. Do not compute these values yourself.
- If `approved` is false: tell user `Michelle (market maker agent) declined — {reason}` and stop.
- If `approvedOddsDecimal >= requestedOdds`: proceed automatically.
- If `approvedOddsDecimal < requestedOdds`: stop and ask user to confirm accepting worse odds; warn the quote expires at `expiresAt`.
  - If user accepts, call:
```
POST /instant-match/{quoteId}/accept-counter
Body: { "wallet": "{OSPEX_WALLET_ADDRESS}" }
```
  - This returns updated `txParams`. Use the updated one.

Side mapping:
- moneyline/spread: user team == `homeTeam` → `home`; else `away`
- total: user said `over` → `over`; `under` → `under`

### Step 3 — Create position and match

Write and execute a **single Node.js script** (ethers.js v6) that does everything in sequence. Do not split into multiple script runs.

Use `txParams` directly:
- Call `positionModule.createUnmatchedPair()`, passing the values from `txParams.args` directly.
- Do not compute odds/timestamps/positionType/etc.

Transaction safety (mandatory — 4 checks):
- Before signing any transaction, the agent must verify all of the following. If any check fails, STOP — do not sign or broadcast. Report the mismatch to the user.
  1. **Contract address:** The contract address used in the script equals the PositionModule address from the On-Chain Reference section. Never derive a contract address from the API response.
  2. **Method name:** `txParams.method` must equal the expected function for the operation (`createUnmatchedPair` for position creation, `adjustUnmatchedPair` for withdrawal, `claimPosition` for claiming).
  3. **Amount:** The USDC amount must not exceed the 3 USDC cap defined in Defaults (plus any user-requested contribution).
  4. **Private key handling:** OSPEX_WALLET_PRIVATE_KEY must only be used inside ethers.js `Wallet` construction. Never log, echo, interpolate into URLs, or pass to any external service.
- Include a code example showing the method verification check.
- This applies to all on-chain operations: position creation, withdrawal, and claiming.

Before creating the position, check USDC allowance for the PositionModule. If insufficient, approve and wait for confirmation before proceeding.

Contributions:
- `txParams.args.contributionAmount` defaults to `"0"`.
- Only change it if the user explicitly asks to tip/contribute. Scale to 6 decimals: 1 USDC = "1000000".

After sending the transaction:
- Wait for confirmation: `const receipt = await tx.wait()`.

Transaction safety:
- Once `tx.wait()` confirms, the position exists on-chain and funds have moved. If any subsequent step (positionId lookup, match call) fails, do NOT re-run the script. Report the tx hash and stop. To resume the interrupted flow, call `GET /positions/by-tx/{txHash}` and then `POST /instant-match/{quoteId}/match` as separate recovery steps.

PositionId:
- Do **not** parse logs yourself. Call server endpoint:
  - `GET /positions/by-tx/{receipt.hash}`
- Use `data.positions[0].positionId`.

Match call:
- Wait 5 seconds for Firebase indexing.
- Retry up to 5 times with 5-second backoff only when response code is `POSITION_NOT_FOUND`.
- Call:
  - `POST /instant-match/{quoteId}/match` with JSON body `{ "positionId": "..." }`.

If matching fails after retries:
- Tell the user the position was created on-chain (share tx hash) but instant match could not be completed.
- Explain: position is live on the order book; may still match; if unmatched they can withdraw anytime.

### Step 4 — Report result

Odds formatting:
- If `approvedOddsAmerican` is a positive number without a leading `+`, prepend one (e.g., `110` → `+110`). Negative odds already include the `-`.

Match enrichment:
- The match endpoint may return `matchedAmountUSDC` and `potentialPayoutUSDC`. Use these if present.
- If absent, use the quoted amount and compute payout as `amount × approvedOddsDecimal`.

Final output format must be:
```
Done. {Team} {marketType abbreviation: ML/spread line/total line} at {americanOdds} ({decimalOdds}x), {matchedAmountUSDC} USDC matched, potential payout {potentialPayoutUSDC} USDC.
https://ospex.org/p/{positionId}
```

### Step 5 — Additional operations (only if user asks)

Include:

- Status check:
  - `GET /positions/{OSPEX_WALLET_ADDRESS}/status`
  - Show `formatted` response.
  - If `claimable` non-empty: offer to claim and, if confirmed, follow claim flow.

- Withdraw unmatched position:
  - `GET /positions/{OSPEX_WALLET_ADDRESS}/withdraw-params`
  - Use returned `txParams` and call `positionModule.adjustUnmatchedPair()` with args directly. Verify `txParams.method` equals `adjustUnmatchedPair` before signing.
  - Then call `GET /positions/withdraw-result/{txHash}` and report amount returned.

- Claim resolved position:
  - `GET /positions/{OSPEX_WALLET_ADDRESS}/claim-params`
  - For each entry, call `positionModule.claimPosition()` with args directly. Verify `txParams.method` equals `claimPosition` before signing.
  - Then call `GET /positions/claim-result/{txHash}` and report payout.

### API reference section

Include base URL:
- `https://api.ospex.org/v1` (no auth; rate limit 100 req/60s/IP)

List endpoints used:
- `GET /markets?sport={nba|nhl|ncaab}` — find games, contestIds, speculationIds. Spread speculations include `awayLine` and `homeLine` instead of `line`.
- `GET /analytics/odds-history/{contestId}`
- `POST /instant-match/{speculationId}/quote?stream=false`
- `POST /instant-match/{quoteId}/accept-counter`
- `POST /instant-match/{quoteId}/match`
- `GET /positions/by-tx/{txHash}`
- `GET /positions/{address}/status`
- `GET /positions/{address}/withdraw-params`
- `GET /positions/withdraw-result/{txHash}`
- `GET /positions/{address}/claim-params`
- `GET /positions/claim-result/{txHash}`

### On-chain reference section

Include:
- Network: Polygon (chain ID 137)
- Contract addresses:
  - USDC: `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` (6 decimals)
  - PositionModule: `0xF717aa8fe4BEDcA345B027D065DA0E1a31465B1A`
- Minimal ABI (ethers.js v6 human-readable) including:
  - `approve`, `allowance`
  - `createUnmatchedPair`
  - `adjustUnmatchedPair`, `claimPosition`
  - PositionCreated/PositionClaimed events

Also mention additional docs available:
- `{baseDir}/references/api-reference.md`
- `{baseDir}/references/contract-interface-reference.md`

## Final instruction

Now output the complete `SKILL.md` content for ospex-one **version 1.7.1**, following this spec exactly.