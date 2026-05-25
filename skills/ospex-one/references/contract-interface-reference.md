# Contract Interface Reference

Deep reference for on-chain contract interactions. For the standard flow (team → quote → position → match), see the main skill file.

See also: `{baseDir}/references/theNumber-conversion.md` for spread/total line conversion.

---

## Network & Addresses

| Item | Value |
|------|-------|
| Network | Polygon (chain ID 137) |
| RPC | Use `OSPEX_RPC_URL` from environment |
| USDC | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` (6 decimals) |
| PositionModule | `0xF717aa8fe4BEDcA345B027D065DA0E1a31465B1A` |
| Moneyline Scorer | `0x82c93AAf547fC809646A7bEd5D8A9D4B72Db3045` |
| Spread Scorer | `0x4377A09760b3587dAf1717F094bf7bd455daD4af` |
| Total Scorer | `0xD7b35DE1bbFD03625a17F38472d3FBa7b77cBeCf` |

---

## Parameter Details

### Odds (uint64, 1e7 precision)

The contract stores odds as integers with 7 decimal places of precision.

**Conversion: decimal odds → contract format**

```
contractOdds = Math.round(decimalOdds * 10000000)
```

Examples:
- 1.91 → `19100000`
- 2.10 → `21000000`
- 1.50 → `15000000`
- 3.25 → `32500000`

**Conversion: American odds → decimal → contract format**

```
Negative American (e.g., -110): decimal = 1 + 100 / |american|
Positive American (e.g., +150): decimal = 1 + american / 100
```

Examples:
- -110 → 1 + 100/110 = 1.909... → `19100000`
- +150 → 1 + 150/100 = 2.50 → `25000000`
- -200 → 1 + 100/200 = 1.50 → `15000000`

**Important:** Use `Math.round()` before converting to integer. Without rounding, floating-point imprecision causes off-by-one errors (e.g., 1.64 * 10000000 = 16399999.999... would truncate incorrectly).

**Bounds:** Minimum odds = `10100000` (1.01), Maximum odds = `1010000000` (101.00). Odds must be a multiple of `100000` (0.01 increments). The contract rounds to the nearest valid increment automatically.

### Amount (uint256, USDC 6 decimals)

```
contractAmount = usdcAmount * 1000000
```

- 3 USDC → `3000000`
- 1 USDC → `1000000`
- 0.50 USDC → `500000`

### Position Type

| Value | Name | Moneyline | Spread | Total |
|-------|------|-----------|--------|-------|
| `0` | Upper | Away wins | Away team covers | Over |
| `1` | Lower | Home wins | Home team covers | Under |

When the user says a team name, determine whether that team is home or away from the `/markets` response. Away team = Upper (0), Home team = Lower (1).

### unmatchedExpiry (uint32, unix timestamp)

Set to the game's start time (available from `GET /markets`). The position expires unmatched when the game begins. A value of `0` means no expiry — the position stays open until matched or the speculation closes.

### theNumber (int32)

- **Moneyline:** Always `0`
- **Spread/Total:** See `{baseDir}/references/theNumber-conversion.md` for the full conversion logic

Quick reference for spreads: `theNumber` is always from the away team's perspective, using `Math.floor()` to eliminate pushes. For totals: `Math.ceil(line)`. Lines always end in `.5` in display form.

### contributionAmount (uint256)

Default: `0`. This is an optional contribution to support the protocol. Pass any amount in USDC 6-decimal format (same as the position amount). For example, 1 USDC = `1000000`. The contribution is transferred along with the position amount. Not required.

---

## Position Lifecycle

```
createUnmatchedPair
  → Position exists with unmatchedAmount > 0
    → adjustUnmatchedPair (add/withdraw funds while speculation is open)
    → completeUnmatchedPair (taker matches some or all of the unmatched amount)
  → Speculation settles (game scored)
    → claimPosition (collects matched winnings + any unmatched remainder)
```

### adjustUnmatchedPair

Adds to or withdraws from the unmatched portion of a position. Can also update the expiry.

```solidity
function adjustUnmatchedPair(
    uint256 speculationId,
    uint128 oddsPairId,
    uint32  newUnmatchedExpiry,  // new expiry timestamp, or 0 to clear
    uint8   positionType,        // 0=Upper, 1=Lower
    int256  amount,              // positive = add funds, negative = withdraw funds
    uint256 contributionAmount   // 0 (optional protocol contribution)
) external
```

**Preconditions:**
- Speculation must be open (not settled) — reverts with `PositionModule__SpeculationNotOpen`
- `newUnmatchedExpiry` must be in the future or `0` — reverts with `PositionModule__InvalidUnmatchedExpiry`
- If adding funds: `unmatchedAmount + addAmount` must not exceed `maxSpeculationAmount` — reverts with `PositionModule__InvalidAmount`
- If withdrawing: `|amount|` must not exceed current `unmatchedAmount` — reverts with `PositionModule__InvalidAmount`

**USDC approval:** Only needed when `amount > 0` (adding funds). Withdrawals transfer USDC back to the caller with no approval required.

**Full withdrawal:** Pass `amount = -(unmatchedAmount)` and `newUnmatchedExpiry = 0`.

**Expiry-only update:** Pass `amount = 0` with the new `newUnmatchedExpiry` value. No USDC is transferred.

### claimPosition

Claims all funds from a settled position: matched winnings (if any) plus any unmatched remainder.

```solidity
function claimPosition(
    uint256 speculationId,
    uint128 oddsPairId,
    uint8   positionType         // 0=Upper, 1=Lower
) external
```

**Preconditions:**
- Speculation must be settled (status = Closed) — reverts with `PositionModule__NotSettled`
- `matchedAmount > 0` or `unmatchedAmount > 0` — reverts with `PositionModule__NoPayout`
- Must not be already claimed — reverts with `PositionModule__AlreadyClaimed`

**Payout calculation:** `calculatePayout(speculationId, pos) + pos.unmatchedAmount`

- If the user **won**: payout includes their matched stake plus the opponent's matched stake (proportional to odds)
- If the user **lost**: matched portion pays 0, but any unmatched remainder is still returned
- If the speculation was **voided**: all funds (matched + unmatched) are returned

After claiming, the position is zeroed out and marked as claimed. Cannot be called again.

### completeUnmatchedPair (taker side)

Takes the other side of an existing unmatched order. Included here for reference — the main skill flow uses Michelle's instant-match API to handle this automatically.

```solidity
function completeUnmatchedPair(
    uint256 speculationId,
    address maker,               // original position creator
    uint128 oddsPairId,
    uint8   makerPositionType,   // the maker's side (0=Upper, 1=Lower)
    uint256 amount               // USDC amount the taker is betting
) external
```

**What happens:** The taker's USDC is transferred to the contract. The maker's `unmatchedAmount` decreases by `amount`. The taker gets a position on the opposite side of the maker. Partial fills are allowed — `amount` can be less than the maker's full `unmatchedAmount`.

**Preconditions:**
- Speculation must be open — reverts with `PositionModule__SpeculationNotOpen`
- Unmatched pair must not be expired — reverts with `PositionModule__UnmatchedExpired`
- `amount` must not exceed maker's `unmatchedAmount` — reverts with `PositionModule__InsufficientUnmatchedAmount`

---

## Events

### PositionCreated

Emitted by `createUnmatchedPair`.

```solidity
event PositionCreated(
    uint256 indexed speculationId,
    address indexed user,
    uint128 oddsPairId,
    uint32  unmatchedExpiry,
    uint8   positionType,
    uint256 amount,
    uint64  upperOdds,
    uint64  lowerOdds
)
```

The `oddsPairId` is required for constructing the `positionId` and for all subsequent operations (adjust, claim). The `upperOdds` and `lowerOdds` confirm the actual odds stored on-chain (may differ slightly from requested due to rounding to 0.01 increments).

### PositionAdjusted

Emitted by `adjustUnmatchedPair`.

```solidity
event PositionAdjusted(
    uint256 indexed speculationId,
    address indexed user,
    uint128 oddsPairId,
    uint32  unmatchedExpiry,
    uint8   positionType,
    int256  amount
)
```

The `amount` field is the signed adjustment as passed to the function (positive = added, negative = withdrawn). The `unmatchedExpiry` is the `newUnmatchedExpiry` input value (0 if clearing).

### PositionClaimed

Emitted by `claimPosition`.

```solidity
event PositionClaimed(
    uint256 indexed speculationId,
    address indexed user,
    uint128 oddsPairId,
    uint8   positionType,
    uint256 payout
)
```

The `payout` field is the total USDC transferred to the user (matched winnings + unmatched remainder). Divide by `1000000` for the human-readable USDC amount.

---

## Error Cases

### Position Creation

| Error | Meaning | What to Do |
|-------|---------|------------|
| `PositionModule__SpeculationNotOpen` | Game has started or market is closed | Inform user, don't retry |
| `PositionModule__InvalidAmount` | Below minimum or above maximum | Check min/max via SpeculationModule |
| `PositionModule__OddsOutOfRange` | Odds < 1.01 or > 101.00 | Fix odds value |
| `PositionModule__InvalidUnmatchedExpiry` | Expiry is in the past | Use a future timestamp or 0 |
| `PositionModule__PositionAlreadyExists` | Wallet already has a position at this speculation/odds/side | Use `adjustUnmatchedPair` to add funds instead |
| USDC transfer fails | Insufficient balance or approval | Check balance and allowance first |

### Withdraw (adjustUnmatchedPair)

| Error | Meaning | What to Do |
|-------|---------|------------|
| `PositionModule__SpeculationNotOpen` | Speculation has settled | Use `claimPosition` instead |
| `PositionModule__InvalidUnmatchedExpiry` | New expiry is in the past (and not 0) | Use 0 or a future timestamp |
| `PositionModule__InvalidAmount` | Withdrawing more than unmatched balance, or adding would exceed max | Check current unmatched amount before withdrawing |
| `PositionModule__PositionDoesNotExist` | No position found for this wallet/speculation/odds/side | Verify positionId components are correct |

### Claim (claimPosition)

| Error | Meaning | What to Do |
|-------|---------|------------|
| `PositionModule__NotSettled` | Speculation hasn't been scored yet | Wait for settlement — games are typically scored within ~30 min of completion |
| `PositionModule__NoPayout` | Position has 0 matched and 0 unmatched | Nothing to claim — may have been claimed already |
| `PositionModule__AlreadyClaimed` | Position was already claimed | No action needed — funds were already returned |

### Match (completeUnmatchedPair)

| Error | Meaning | What to Do |
|-------|---------|------------|
| `PositionModule__SpeculationNotOpen` | Speculation has settled or not yet open | Cannot match after settlement |
| `PositionModule__UnmatchedExpired` | The maker's unmatched position has expired | Find a different position to match |
| `PositionModule__InsufficientUnmatchedAmount` | Amount exceeds maker's available unmatched funds | Reduce amount or query current unmatched balance |
| USDC transfer fails | Insufficient balance or approval | Check balance and allowance first |

---

## ABI (Complete)

**USDC (ERC-20):**
```json
[
    "function approve(address spender, uint256 amount) returns (bool)",
    "function allowance(address owner, address spender) view returns (uint256)",
    "function balanceOf(address account) view returns (uint256)"
]
```

**PositionModule:**
```json
[
    "function createUnmatchedPair(uint256 speculationId, uint64 odds, uint32 unmatchedExpiry, uint8 positionType, uint256 amount, uint256 contributionAmount)",
    "function adjustUnmatchedPair(uint256 speculationId, uint128 oddsPairId, uint32 newUnmatchedExpiry, uint8 positionType, int256 amount, uint256 contributionAmount)",
    "function claimPosition(uint256 speculationId, uint128 oddsPairId, uint8 positionType)",
    "function completeUnmatchedPair(uint256 speculationId, address maker, uint128 oddsPairId, uint8 makerPositionType, uint256 amount)",
    "function completeUnmatchedPairBatch(uint256 speculationId, address[] makers, uint128[] oddsPairIds, uint8[] makerPositionTypes, uint256[] amounts)",
    "function transferPosition(uint256 speculationId, address from, uint128 oddsPairId, uint8 positionType, address to, uint256 amount)",
    "function getPosition(uint256 speculationId, address user, uint128 oddsPairId, uint8 positionType) view returns (tuple(uint256 matchedAmount, uint256 unmatchedAmount, bool claimed))",
    "function getOddsPair(uint128 oddsPairId) view returns (tuple(uint64 upperOdds, uint64 lowerOdds))",
    "function ODDS_PRECISION() view returns (uint64)",
    "event PositionCreated(uint256 indexed speculationId, address indexed user, uint128 oddsPairId, uint32 unmatchedExpiry, uint8 positionType, uint256 amount, uint64 upperOdds, uint64 lowerOdds)",
    "event PositionAdjusted(uint256 indexed speculationId, address indexed user, uint128 oddsPairId, uint32 unmatchedExpiry, uint8 positionType, int256 amount)",
    "event PositionClaimed(uint256 indexed speculationId, address indexed user, uint128 oddsPairId, uint8 positionType, uint256 payout)"
]
```

These are ethers.js v6 human-readable ABI fragments. Pass directly to `new ethers.Contract(address, abi, signer)`.
