# Flowing Balances — Real-Time Streaming Token Display

Superfluid streams tokens per-second. On-chain, a balance is stored as a
snapshot: an amount at a point in time, plus a flow rate. To display the
*current* balance you compute `balance + flowRate × (now - timestamp)`.
Animate that computation and you get a counter that ticks up (or down) in
real-time — a **flowing balance**.

## The Core Algorithm

All inputs come from on-chain data (e.g. `realtimeBalanceOf`, GDA pool
member snapshots, or subgraph `AccountTokenSnapshot` entities):

- `balance` — wei amount at the snapshot time
- `balanceTimestamp` — Unix seconds when the snapshot was taken
- `flowRate` — net tokens per second in wei (positive = receiving, negative = sending)

Every animation frame:

```
elapsed = now() - balanceTimestamp
currentBalance = balance + flowRate × elapsed
```

## Critical Rules

Follow ALL of these when implementing flowing balances. Violating any one
produces a visually broken or incorrect result.

1. **`requestAnimationFrame`, NEVER `setInterval`.** rAF syncs with the
   browser paint cycle, pauses in background tabs, and does not block the
   main thread. `setInterval` has none of these properties — it causes jank
   when multiple flowing balances are on screen. Use rAF with manual
   throttling (skip frames until enough time has elapsed).

2. **BigInt arithmetic, not floating-point.** Wei values are integers up to
   10^77. JavaScript `Number` loses precision above 2^53. All balance math
   must use `BigInt`. Convert to a display string only at the final step.

3. **Auto decimal precision.** Different flow rates need different decimal
   counts. Hardcoding (e.g. `.toFixed(6)`) produces either too many or too
   few digits. Compute once from the flow rate magnitude — see the algorithm
   below.

4. **`font-variant-numeric: tabular-nums`.** In proportional fonts "1" is
   narrower than "0", so digits jump horizontally. Apply `tabular-nums` CSS
   (or use a monospace font) on the container.

5. **Skip animation when `flowRate === 0n`.** No flow = no change. Render
   the static balance once and stop the loop.

6. **Render as a leaf component.** The rAF loop triggers re-renders every
   tick. Keep the flowing component as a leaf node to avoid re-rendering
   its entire subtree.

7. **Throttle the update rate.** Even with rAF, recalculating every frame
   (~16ms) is wasteful when visible digits don't change that fast:
   - **60ms** ("fast") — smooth animation, ~3 visible digits ticking
   - **400ms** ("slow") — subtle pulse, good for secondary balances

## Auto Decimal Precision

The number of decimal places to show depends on how fast the balance
changes per tick. The goal: the last ~3 visible digits should animate
smoothly.

Algorithm:
1. Compute `flowRatePerTick = flowRate / ticksPerSecond`
2. Format to ether and inspect the result
3. If the integer part is non-zero → show 0 decimal places
4. Otherwise count leading zeroes after the decimal point, add 2
5. Cap at 18 (max ether precision)

This means a high flow rate (changing whole tokens per tick) shows no
decimals, while a tiny trickle shows many — and the animation looks
equally smooth in both cases.

## Visual Polish

### Preventing layout shift

Two causes of layout shift — fix both:

**1. Fluctuating decimal places.** If the number of decimals changes
frame-to-frame the string length jumps. Fix: pick a fixed decimal count
once based on the flow rate and keep it constant. The Auto Decimal
Precision algorithm above does this automatically — it inspects how much
the balance changes per tick and locks in the right number of decimals.

**2. Variable-width digit glyphs.** In proportional fonts "1" is narrower
than "0", so the number shifts horizontally as digits change. Fix:

- **`font-variant-numeric: tabular-nums`** (CSS) — forces equal-width
  digits in any proportional font. Recommended approach.
- **Monospace font** — also works, though it rarely matches the design
  system.

### Integer / decimal split

Rendering the integer part at full size and the decimal part at ~80% size
(e.g. `font-size: 0.8em`) gives a currency-like feel. The two parts
should share the same baseline. A common implementation is two inline
elements with `align-items: baseline`.

### Thousand separators

Insert commas every 3 digits in the integer part via regex:
```js
integerPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
```

## Vanilla JS Reference Implementation

The simplest portable expression of the algorithm. No framework
dependency — works anywhere with a DOM element:

```js
function startFlowingBalance(element, balance, balanceTimestamp, flowRate) {
    if (flowRate === 0n) {
        element.textContent = formatWei(balance)
        return () => {}
    }

    let lastTick = 0
    let rafId

    function tick(now) {
        rafId = requestAnimationFrame(tick)
        if (now - lastTick < 60) return
        lastTick = now

        // All wei math in BigInt — do NOT convert flowRate to Number
        const elapsed = BigInt(Date.now() - Number(balanceTimestamp) * 1000)
        const current = balance + (flowRate * elapsed) / 1000n
        element.textContent = formatWei(current)
    }

    rafId = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafId)
}
```

Note the pattern: `requestAnimationFrame` drives the loop, manual
throttling skips frames under 60ms, `BigInt` handles all wei math, and
the returned function cancels the animation via `cancelAnimationFrame`.

## React Reference Implementation

Dependencies: `react` (>=18), `viem` (for `formatEther`).

### Core hooks

```tsx
"use client"

import { useEffect, useMemo, useState } from "react"
import { formatEther } from "viem"

// ─── Configuration ───────────────────────────────────────────────

const ANIMATION_STEP_TIME = { fast: 60, slow: 400 } as const

// ─── Core Hook: useFlowingBalance ────────────────────────────────
// Calculates a real-time balance using requestAnimationFrame.
// NOTE: causes constant re-renders — use only on leaf components.

function useFlowingBalance(params: {
    balance: bigint
    balanceTimestamp: bigint | number
    flowRate: bigint
    animationStepTimeInMs: number
}) {
    const { balance, balanceTimestamp, flowRate, animationStepTimeInMs } = params
    const [flowingBalance, setFlowingBalance] = useState(balance)

    useEffect(() => {
        if (flowRate === 0n) {
            setFlowingBalance(balance)
            return
        }

        let lastAnimationTimestamp: DOMHighResTimeStamp = 0

        const animationStep = (currentAnimationTimestamp: DOMHighResTimeStamp) => {
            animationFrameId = window.requestAnimationFrame(animationStep)
            if (currentAnimationTimestamp - lastAnimationTimestamp > animationStepTimeInMs) {
                const elapsedTimeInMilliseconds = BigInt(
                    Date.now() - Number(balanceTimestamp) * 1000,
                )
                const newFlowingBalance =
                    balance + (flowRate * elapsedTimeInMilliseconds) / 1000n
                setFlowingBalance(newFlowingBalance)
                lastAnimationTimestamp = currentAnimationTimestamp
            }
        }

        let animationFrameId = window.requestAnimationFrame(animationStep)
        return () => window.cancelAnimationFrame(animationFrameId)
    }, [balance, balanceTimestamp, flowRate, animationStepTimeInMs])

    return flowingBalance
}

// ─── Hook: useFlowingDecimalPoint ────────────────────────────────
// Determines how many decimal places to show so that the last ~3
// visible digits animate smoothly at the given tick rate.

function useFlowingDecimalPoint(params: {
    flowRate: bigint
    animationStepTimeInMs: number
}) {
    const { flowRate, animationStepTimeInMs } = params

    return useMemo(() => {
        if (flowRate === 0n) return undefined

        const ticksPerSecond = 1000 / animationStepTimeInMs
        const flowRatePerTick = flowRate / BigInt(Math.round(ticksPerSecond))
        const [beforeDecimal, afterDecimal] = formatEther(flowRatePerTick).split(".")
        const abs = (n: bigint) => (n >= 0 ? n : -n)

        if (abs(BigInt(beforeDecimal)) > 0n) return 0

        const withoutLeadingZeroes = BigInt(afterDecimal)
        const leadingZeroes = afterDecimal
            .toString()
            .replace(withoutLeadingZeroes.toString(), "").length

        return Math.min(leadingZeroes + 2, 18)
    }, [flowRate, animationStepTimeInMs])
}
```

### FlowingBalance component

```tsx
export function FlowingBalance(props: {
    /** Balance snapshot in wei */
    balance: bigint
    /** Unix timestamp (seconds) when balance was recorded */
    balanceTimestamp: bigint | number
    /** Per-second flow rate in wei */
    flowRate: bigint
    /** Optional cap — flowing stops here */
    maxBalance?: bigint
    /** Override auto-detected decimal places */
    decimalPlaces?: number
    /** "fast" = 60ms ticks, "slow" = 400ms ticks */
    animationSpeed?: "fast" | "slow"
    /** CSS class for the outer <span> */
    className?: string
}) {
    const {
        balance,
        balanceTimestamp,
        flowRate: flowRate_,
        maxBalance,
        animationSpeed = "fast",
        className,
    } = props

    const animationStepTimeInMs = ANIMATION_STEP_TIME[animationSpeed]

    const flowingBalance_ = useFlowingBalance({
        balance,
        balanceTimestamp,
        flowRate: flowRate_,
        animationStepTimeInMs,
    })

    const isOverMax = maxBalance !== undefined && flowingBalance_ > maxBalance
    const flowingBalance = isOverMax ? maxBalance : flowingBalance_
    const flowRate = isOverMax ? 0n : flowRate_

    const autoDecimalPlaces = useFlowingDecimalPoint({
        flowRate,
        animationStepTimeInMs,
    })
    const decimalPlaces = props.decimalPlaces ?? autoDecimalPlaces

    return (
        <FormattedBalance
            value={flowingBalance}
            decimalPlaces={decimalPlaces}
            className={className}
        />
    )
}
```

### FormattedBalance (display helper)

```tsx
function FormattedBalance(props: {
    value: bigint
    decimalPlaces?: number
    className?: string
}) {
    const { value, decimalPlaces, className } = props
    let formatted: string

    if (decimalPlaces === 18) {
        const raw = formatEther(value)
        const [intPart, decPart] = raw.split(".")
        const formattedInt = intPart.replace(/\B(?=(\d{3})+(?!\d))/g, ",")
        formatted = decPart ? `${formattedInt}.${decPart}` : formattedInt
    } else {
        formatted = formatEtherAndRound(value, decimalPlaces ?? 0)
    }

    const [integerPart, decimalPart] = formatted.split(".")

    return (
        <span className={className ?? "inline-flex items-baseline tabular-nums"}>
            {integerPart}
            {decimalPart && (
                <span className="inline-block text-[0.8em]">.{decimalPart}</span>
            )}
        </span>
    )
}
```

### Props

| Prop | Type | Required | Description |
|------|------|----------|-------------|
| `balance` | `bigint` | Yes | Balance snapshot in wei |
| `balanceTimestamp` | `bigint \| number` | Yes | Unix timestamp (seconds) when `balance` was recorded |
| `flowRate` | `bigint` | Yes | Tokens per second in wei |
| `maxBalance` | `bigint` | No | Cap — counter stops here and flow rate becomes 0 |
| `decimalPlaces` | `number` | No | Override auto-detected precision |
| `animationSpeed` | `"fast" \| "slow"` | No | `"fast"` = 60ms ticks (default), `"slow"` = 400ms ticks |
| `className` | `string` | No | CSS class for outer `<span>` (default: `"inline-flex items-baseline tabular-nums"`) |

### Usage

```tsx
import { FlowingBalance } from "./FlowingBalance"

<FlowingBalance
    balance={1000000000000000000000n}   // 1000 tokens (in wei)
    balanceTimestamp={1710000000n}       // Unix seconds when balance was snapshotted
    flowRate={38580246913580n}           // ~100 tokens/month in wei/second
/>
```

## Other Frameworks

The core loop is framework-independent. Only the "set the displayed value"
mechanism changes.

### Vue 3

Use `watchEffect` with cleanup — the rAF loop is identical:

```js
watchEffect((onCleanup) => {
    // ... same rAF loop, updating a ref instead of setState
    onCleanup(() => cancelAnimationFrame(rafId))
})
```

### Svelte 5

Use `$effect` with a cleanup return — same loop, update a `$state` rune.

### Solid

Use `createEffect` with `onCleanup` — same loop, update a signal.

## Formatting Utilities

Pure functions usable in any JS/TS project. Build on viem's `formatEther`
and `parseEther`.

### formatEtherAndRound

Converts wei `bigint` to a human-readable string with thousand separators
and configurable decimal places.

```ts
function formatEtherAndRound(value: bigint, decimals?: number): string

formatEtherAndRound(1000000000000000000000n)       // "1,000"
formatEtherAndRound(1000000000000000000000n, 2)     // "1,000.00"
formatEtherAndRound(1234500000000000000n, 4)        // "1.2345"
```

### getPrettyShortNumber

Compact display with K/M abbreviations for space-constrained UI.

```ts
function getPrettyShortNumber(wei: bigint): string

getPrettyShortNumber(1234567000000000000000000n)  // "1.23M"
getPrettyShortNumber(1234000000000000000000n)     // "1.23K"
```

### getSignificantDecimals

Calculates how many decimal places are needed to show meaningful digits
for values of unknown magnitude.

```ts
function getSignificantDecimals(value: bigint, minDecimals?: number, extraDigits?: number): number

getSignificantDecimals(26700000000000n)        // 7  (shows "0.0000267")
getSignificantDecimals(1000000000000000000n)   // 0  (1 ETH — no decimals)
```

### Other utilities

- **`roundWeiToPrettyAmount(value, decimals?)`** — Detects 3+ consecutive 9's and rounds up. Avoids displaying `1,499,999.999...`.
- **`normalizeDecimalInput(value)`** — Sanitizes user-typed amounts: strips commas, collapses multiple decimals (`"1.2.3"` → `"1.23"`).
- **`safeParseEther(value)`** — Wraps `parseEther` — returns `undefined` instead of throwing on invalid input.
- **`formatUSD(value)` / `calculateTokenUSD(amount, priceUSD)`** — USD formatting with K/M abbreviations.

## Flow Rate Display

The ecosystem convention is to show flow rates as monthly amounts. Multiply
the per-second wei rate by `2628000` (average seconds per month:
365.25 days / 12) and format with `formatEtherAndRound`.

```ts
const SECONDS_PER_MONTH = 2628000n
const monthlyWei = flowRate * SECONDS_PER_MONTH
const display = formatEtherAndRound(monthlyWei, 2) // e.g. "100.00"
```
