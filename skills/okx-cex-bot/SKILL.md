---
name: okx-cex-bot
description: Manage Grid bots (spot/contract/coin-margined) and DCA Martingale bots (Spot DCA 现货马丁 / Contract DCA 合约马丁) on OKX. Covers create, stop, amend, monitor P&L, TP/SL, margin/investment adjustment, and AI-recommended parameters. Requires API credentials. Not for regular orders (okx-cex-trade), market data (okx-cex-market), or account info (okx-cex-portfolio).
license: MIT
metadata:
  author: okx
  version: "1.1.0"
  homepage: "https://www.okx.com"
  agent:
    emoji: "🤖"
    requires:
      bins: ["okx"]
    install:
      - id: npm
        kind: node
        package: "@okx_ai/okx-trade-cli"
        bins: ["okx"]
        label: "Install okx CLI (npm)"
---

# OKX CEX Bot Trading

Grid and DCA (Spot & Contract Martingale) bot management on OKX. All bots are **native OKX server-side** — they run on OKX and do not require a local process.

## Prerequisites

```bash
npm install -g @okx_ai/okx-trade-cli
```

Check credentials, then set up if missing:

```bash
okx config show          # shows configured profiles (api_key shows last 4 chars)
okx config init          # interactive wizard if not configured
```

> **Security**: NEVER accept API credentials in chat. Guide users to `okx config init` or edit `~/.okx/config.toml` directly.

## Credential & Profile Check

**Run before every authenticated command.**

### Step A — Verify credentials

```bash
okx config show
```

If no configuration → stop, guide user to `okx config init`, wait for completion.

### Step B — Determine profile (required)

| `--profile` | Mode | Funds |
|---|---|---|
| `live` | 实盘 | Real money |
| `demo` | 模拟盘 | Simulated, safe for testing |

Resolution:
1. User intent is clear ("real"/"实盘"/"live" → `live`; "test"/"模拟"/"demo" → `demo`) → use it, inform user
2. No explicit declaration → check conversation context for previous profile → use it if found
3. Nothing found → ask: "Live (实盘) or Demo (模拟盘)?" — wait before proceeding

**After every command**: append `[profile: live]` or `[profile: demo]`

### Handling 401 Errors

Stop immediately. Guide user to update `~/.okx/config.toml` with their editor. Verify with `okx config show` before retrying.

## Skill Routing

| Need | Skill |
|---|---|
| Market data, prices, depth | `okx-cex-market` |
| Account balance, positions, fees | `okx-cex-portfolio` |
| Regular spot/swap/futures orders | `okx-cex-trade` |
| **Grid / DCA bots** | **`okx-cex-bot` (this skill)** |

## Command Index

### Grid Bot

| Command | Type | Description |
|---|---|---|
| `okx bot grid create` | WRITE | Create a grid bot (spot or contract) |
| `okx bot grid stop` | WRITE | Stop a grid bot |
| `okx bot grid orders` | READ | List active or history grid bots |
| `okx bot grid details` | READ | Grid bot details + PnL |
| `okx bot grid sub-orders` | READ | Individual grid fills or pending orders |

### DCA Bot (Spot & Contract)

| Command | Type | Description |
|---|---|---|
| `okx bot dca create` | WRITE | Create a DCA (Martingale) bot (spot or contract) |
| `okx bot dca stop` | WRITE | Stop a DCA bot (spot or contract) |
| `okx bot dca orders` | READ | List active or history DCA bots (default: contract_dca) |
| `okx bot dca details` | READ | DCA bot details + PnL |
| `okx bot dca sub-orders` | READ | DCA cycles and orders within a cycle |

## Operation Flow

### Step 1 — Identify bot type and action

Parse user request → determine module (Grid / DCA) and action (create / stop / list / details).

### Step 2 — Execute

**READ commands** (orders, details, sub-orders): run immediately after profile confirmation.

**WRITE commands** (create, stop): confirm key parameters with user once before executing.

### Step 3 — Verify after writes

- After create → run the corresponding `orders` command to confirm active
- After stop → run `orders --history` to confirm stopped

## Key Rules

- **Never auto-transfer funds.** If balance is insufficient for bot creation, report the shortfall (current available vs required) and ask the user how to proceed: (1) transfer funds manually, (2) reduce size, or (3) cancel.
- **`algoId`** is the bot's algo order ID (from create or list output). It is NOT a normal `ordId`. Never fabricate — always obtain from a prior command.
- **`algoOrdType`** for grid must match the bot's actual type. Always use the value from `bot grid orders` — do not infer from user description alone. Mismatch causes error `50016`.
- When operating on existing bots, **always list first** to get correct IDs, unless the user provides them explicitly.
- **TP/SL constraints**: `tpTriggerPx`/`tpRatio` and `slTriggerPx`/`slRatio` are mutually exclusive pairs.

## CLI Command Reference

### Grid Bot — Create

```bash
okx bot grid create --instId <id> --algoOrdType <type> \
  --maxPx <px> --minPx <px> --gridNum <n> \
  [--runType <1|2>] \
  [--quoteSz <n>] [--baseSz <n>] \
  [--direction <long|short|neutral>] [--lever <n>] [--sz <n>] \
  [--basePos] [--no-basePos] \
  [--tpTriggerPx <px>] [--slTriggerPx <px>] [--tpRatio <ratio>] [--slRatio <ratio>] \
  [--algoClOrdId <id>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--instId` | Yes | - | Instrument (e.g., `BTC-USDT` for spot, `BTC-USDT-SWAP` for USDT-M contract, `BTC-USD-SWAP` for coin-M contract) |
| `--algoOrdType` | Yes | - | `grid` (spot grid) or `contract_grid` (contract grid, including coin-margined) |
| `--maxPx` | Yes | - | Upper price boundary |
| `--minPx` | Yes | - | Lower price boundary |
| `--gridNum` | Yes | - | Grid levels (2–100) |
| `--runType` | No | `1` | `1`=arithmetic spacing, `2`=geometric spacing |
| `--quoteSz` | Cond. | - | USDT investment — spot grid only (provide `quoteSz` or `baseSz`) |
| `--baseSz` | Cond. | - | Base currency investment — spot grid only |
| `--direction` | Cond. | - | `long`, `short`, or `neutral` — required for contract grid |
| `--lever` | Cond. | - | Leverage (e.g., `5`) — contract grid only |
| `--sz` | Cond. | - | Investment margin in USDT (USDT-M) or coin (coin-M) — contract grid only |
| `--basePos` / `--no-basePos` | No | `true` | Open a base position at creation — contract grid only (ignored for neutral). Use `--no-basePos` to disable |
| `--tpTriggerPx` | No | - | Take-profit trigger price (mutually exclusive with `--tpRatio`) |
| `--slTriggerPx` | No | - | Stop-loss trigger price (mutually exclusive with `--slRatio`) |
| `--tpRatio` | No | - | Take-profit ratio — contract grid only (mutually exclusive with `--tpTriggerPx`) |
| `--slRatio` | No | - | Stop-loss ratio — contract grid only (mutually exclusive with `--slTriggerPx`) |
| `--algoClOrdId` | No | - | Client-defined algo order ID (1-32 alphanumeric). Unique per user, enables idempotent creation |

---

### Grid Bot — Stop

```bash
okx bot grid stop --algoId <id> --algoOrdType <type> --instId <id> \
  [--stopType <1|2|3|5|6>] [--json]
```

> **`--algoId`** and **`--algoOrdType`** must come from `bot grid orders` output. The `algoOrdType` must match the bot's actual type — do not guess.

| `--stopType` | Behavior |
|---|---|
| `1` | Stop + sell/close all positions at market (default) |
| `2` | Stop + keep current assets as-is |
| `3` | Stop + close at limit prices |
| `5` | Stop + partial close |
| `6` | Stop without selling (smart arbitrage) |

---

### Grid Bot — List Orders

```bash
okx bot grid orders --algoOrdType <type> [--instId <id>] [--algoId <id>] [--history] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--algoOrdType` | Yes | - | `grid` (spot), `contract_grid` (contract), or `moon_grid` (moon) |
| `--instId` | No | - | Filter by instrument |
| `--algoId` | No | - | Filter by algo order ID. NOT a normal trade order ID |
| `--history` | No | false | Show completed/stopped bots instead of active |

---

### Grid Bot — Details

```bash
okx bot grid details --algoOrdType <type> --algoId <id> [--json]
```

Returns: bot config, current PnL (`pnlRatio`), grid range, number of grids, state, position info.

---

### Grid Bot — Sub-Orders

```bash
okx bot grid sub-orders --algoOrdType <type> --algoId <id> [--live] [--json]
```

| Flag | Effect |
|---|---|
| *(default)* | Filled sub-orders (executed grid trades) |
| `--live` | Pending grid orders currently on the book |

---

### DCA Bot — Create (Spot & Contract)

```bash
okx bot dca create --algoOrdType <spot_dca|contract_dca> --instId <id> --direction <long|short> \
  --initOrdAmt <n> --maxSafetyOrds <n> --tpPct <ratio> \
  [--lever <n>] [--safetyOrdAmt <n>] [--pxSteps <ratio>] [--pxStepsMult <mult>] [--volMult <mult>] \
  [--slPct <ratio>] [--slMode <limit|market>] [--allowReinvest] \
  [--triggerStrategy <instant|price|rsi>] [--triggerPx <price>] \
  [--triggerCond <cross_up|cross_down>] [--thold <threshold>] [--timeframe <timeframe>] [--timePeriod <period>] \
  [--algoClOrdId <id>] [--reserveFunds <true|false>] [--tradeQuoteCcy <ccy>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--algoOrdType` | Yes | - | `spot_dca` (Spot DCA) or `contract_dca` (Contract DCA) |
| `--instId` | Yes | - | Instrument (e.g., `BTC-USDT` for spot, `BTC-USDT-SWAP` for contract) |
| `--lever` | Cond. | - | Leverage multiplier (e.g., `3`). Required for `contract_dca` |
| `--direction` | Yes | - | `long` or `short`. `spot_dca` must be `long` |
| `--initOrdAmt` | Yes | - | Initial order amount (quote currency) |
| `--maxSafetyOrds` | Yes | - | Max safety orders, integer [0, 100] (e.g., `3`; `0` = no DCA) |
| `--safetyOrdAmt` | Cond. | - | Safety order amount (quote currency). Required when `maxSafetyOrds > 0` |
| `--pxSteps` | Cond. | - | Initial price deviation [0.001, 0.5], e.g., `0.03` = 3%. Required when `maxSafetyOrds > 0` |
| `--pxStepsMult` | Cond. | `1` | Price step multiplier (e.g., `1.2`). Required when `maxSafetyOrds > 0` |
| `--volMult` | Cond. | `1` | Safety order size multiplier (e.g., `1.5`). Required when `maxSafetyOrds > 0` |
| `--tpPct` | Yes | - | Take-profit ratio: long [0.001, 10], short [0.001, 0.9999] (e.g., `0.03` = 3%) |
| `--slPct` | No | - | Stop-loss ratio, must exceed MPD (e.g., `0.05` = 5%). Must be used with `--slMode` |
| `--slMode` | No | `market` | Stop-loss type: `limit` or `market`. Must be used with `--slPct` |
| `--allowReinvest` | No | `true` | Reinvest profit into the next DCA cycle |
| `--triggerStrategy` | No | `instant` | contract_dca: `instant`, `price`, `rsi`; spot_dca: `instant`, `rsi` |
| `--triggerPx` | No | - | Trigger price — required when `triggerStrategy=price` (contract_dca only) |
| `--triggerCond` | No | - | `cross_up` or `cross_down` — required when `triggerStrategy=rsi`, optional when `triggerStrategy=price` |
| `--thold` | No | - | RSI threshold (e.g. `30`) — required when `triggerStrategy=rsi` |
| `--timeframe` | No | - | RSI timeframe (e.g. `15m`) — required when `triggerStrategy=rsi` |
| `--timePeriod` | No | `14` | RSI period — optional when `triggerStrategy=rsi` |
| `--algoClOrdId` | No | - | Client-defined strategy order ID (1-32 alphanumeric) |
| `--reserveFunds` | No | `true` | `true` or `false` — whether to reserve funds |
| `--tradeQuoteCcy` | No | - | Trade quote currency |

**Conditional required logic:**
- Always required: `--algoOrdType`, `--instId`, `--direction`, `--initOrdAmt`, `--maxSafetyOrds`, `--tpPct`
- When `algoOrdType=contract_dca`: also required `--lever`
- When `maxSafetyOrds > 0`: also required `--safetyOrdAmt`, `--pxSteps`, `--pxStepsMult`, `--volMult`
- `--slPct` and `--slMode` must be both set or both omitted

---

### DCA Bot — Stop

```bash
okx bot dca stop --algoOrdType <spot_dca|contract_dca> --algoId <id> [--stopType <1|2>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--algoOrdType` | Yes | - | `spot_dca` or `contract_dca` |
| `--algoId` | Yes | - | DCA bot algo order ID (from create or list output). NOT a normal trade order ID |
| `--stopType` | Cond. | `1` (contract_dca) | Required for `spot_dca`: `1`=sell all tokens, `2`=keep tokens. `contract_dca` always uses `1` (close position) |

---

### DCA Bot — List Orders

```bash
okx bot dca orders [--algoOrdType <spot_dca|contract_dca>] [--algoId <id>] [--instId <id>] [--history] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--algoOrdType` | No | `contract_dca` | Filter by strategy type |
| `--algoId` | No | - | Filter by DCA bot algo order ID |
| `--instId` | No | - | Filter by instrument |
| `--history` | No | false | Show completed/stopped bots instead of active |

---

### DCA Bot — Details

```bash
okx bot dca details --algoOrdType <spot_dca|contract_dca> --algoId <id> [--json]
```

Returns: `avgPx`, `upl`, `liqPx`, `sz`, `tpPx`, `slPx`, `initPx`, `fundingFee`, `fee`, `fillSafetyOrds`, `algoClOrdId`, `baseSz`, `quoteSz`, `tradeQuoteCcy`.

---

### DCA Bot — Sub-Orders

```bash
okx bot dca sub-orders --algoOrdType <spot_dca|contract_dca> --algoId <id> [--cycleId <id>] [--json]
```

| Flag / Param | Effect |
|---|---|
| *(default)* | List all cycles |
| `--cycleId <id>` | Show orders within a specific cycle |

## Quickstart

```bash
# Spot grid: BTC $90k–$100k, 10 grids, 1000 USDT
okx bot grid create --instId BTC-USDT --algoOrdType grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000

# Contract grid: BTC perp, neutral, 5x, 100 USDT margin
okx bot grid create --instId BTC-USDT-SWAP --algoOrdType contract_grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 \
  --direction neutral --lever 5 --sz 100

# Coin-margined contract grid: BTC inverse perp
okx bot grid create --instId BTC-USD-SWAP --algoOrdType contract_grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 \
  --direction long --lever 5 --sz 0.01

# Contract DCA bot: BTC perp, long, 3x, 3% TP
okx bot dca create --algoOrdType contract_dca --instId BTC-USDT-SWAP --lever 3 --direction long \
  --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
  --pxSteps 0.03 --pxStepsMult 1 --volMult 1 --tpPct 0.03

# Spot DCA bot: BTC spot, long, 5% TP
okx bot dca create --algoOrdType spot_dca --instId BTC-USDT --direction long \
  --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
  --pxSteps 0.03 --pxStepsMult 1.2 --volMult 1.5 --tpPct 0.05

# List all active bots
okx bot grid orders --algoOrdType grid
okx bot grid orders --algoOrdType contract_grid
okx bot dca orders --algoOrdType contract_dca
okx bot dca orders --algoOrdType spot_dca
```

## Cross-Skill Workflows

### Spot Grid Bot
> User: "Start a BTC grid bot between $90k and $100k with 10 grids, invest 1000 USDT"

```
1. okx-cex-market    okx market ticker BTC-USDT                     → confirm price is in range
2. okx-cex-portfolio okx account balance USDT                       → confirm available funds
        ↓ user approves
3. okx-cex-bot       okx bot grid create --instId BTC-USDT --algoOrdType grid \
                       --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000
4. okx-cex-bot       okx bot grid orders --algoOrdType grid          → confirm bot is active
5. okx-cex-bot       okx bot grid details --algoOrdType grid --algoId <id> → monitor PnL
```

### Contract DCA Bot
> User: "Start a long DCA bot on BTC perp, 3x leverage, $200 initial, 3% TP"

```
1. okx-cex-market    okx market ticker BTC-USDT-SWAP                → confirm current price
2. okx-cex-portfolio okx account balance USDT                       → confirm margin
        ↓ user approves
3. okx-cex-bot       okx bot dca create --algoOrdType contract_dca --instId BTC-USDT-SWAP \
                       --lever 3 --direction long \
                       --initOrdAmt 200 --safetyOrdAmt 100 --maxSafetyOrds 3 \
                       --pxSteps 0.03 --pxStepsMult 1 --volMult 1 --tpPct 0.03
4. okx-cex-bot       okx bot dca orders --algoOrdType contract_dca   → confirm active
5. okx-cex-bot       okx bot dca details --algoOrdType contract_dca --algoId <id> → monitor PnL
```

### Spot DCA Bot
> User: "帮我在现货上 DCA BTC，首单 100 USDT，5% 止盈"

```
1. okx-cex-market    okx market ticker BTC-USDT                     → confirm current price
2. okx-cex-portfolio okx account balance USDT                       → confirm funds
        ↓ user approves
3. okx-cex-bot       okx bot dca create --algoOrdType spot_dca --instId BTC-USDT \
                       --direction long \
                       --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
                       --pxSteps 0.03 --pxStepsMult 1.2 --volMult 1.5 --tpPct 0.05
4. okx-cex-bot       okx bot dca orders --algoOrdType spot_dca       → confirm active
```

## Edge Cases

### Grid Bot

- **Price out of range**: `--minPx` must be < current price < `--maxPx`; check with `okx-cex-market` first
- **Insufficient balance**: check `okx-cex-portfolio` → `account balance` before creating. If insufficient, **do NOT auto-transfer** — report the shortfall and ask the user for instructions
- **Contract grid direction**: `long` (buys more at lower prices), `short` (sells at higher), `neutral` (both). Direction is required for contract grid
- **Contract grid basePos**: defaults to `true` — long/short grids automatically open a base position at creation. Neutral direction ignores this. Pass `--no-basePos` to disable
- **Contract grid --sz**: investment margin in USDT (USDT-M) or coin (coin-M), not number of contracts
- **Coin-margined grids**: use inverse instruments (e.g., `BTC-USD-SWAP`). Margin unit is the base coin (BTC), not USDT
- **Stop type**: `stopType 1` sells/closes all (default); `stopType 2` keeps assets; `stopType 5/6` for contract grid positions
- **TP/SL**: `tpTriggerPx`/`tpRatio` and `slTriggerPx`/`slRatio` are mutually exclusive pairs. Ratio-based TP/SL is contract grid only
- **Already stopped bot**: stop returns error — check `bot grid orders --history` first to confirm state
- **Insufficient margin (51340)**: extract required minimum from error, check balance via `okx-cex-portfolio`, report shortfall to user — do NOT auto-transfer
- **Demo mode**: `okx --profile demo bot grid create ...` — safe for testing, no real funds
- **algoClOrdId duplicate**: if the same `algoClOrdId` already exists, the API returns error code `51065`

### DCA Bot

- **Spot DCA direction**: must always be `long`. If user says "short spot DCA", explain that spot DCA only supports long direction
- **Spot DCA stopType**: always ask user whether to sell all tokens (`1`) or keep them (`2`) when stopping
- **Contract DCA lever**: required. If missing, the tool returns a validation error
- **pxStepsMult**: `1.0` = equal spacing; `>1.0` = widen gaps between successive safety orders
- **volMult**: `1.0` = equal sizes; `>1.0` = increase per safety order (Martingale scaling)
- **triggerStrategy**: `instant` starts immediately; `price` waits for trigger price (contract_dca only); `rsi` waits for RSI condition (both spot_dca and contract_dca)
- **Already stopped bot**: stop returns error — check `bot dca orders --history` first
- **Demo mode**: `okx --profile demo bot dca create ...` — safe testing, no real funds
- **INVALID_PRICE_STEPS_MULTIPLIER error**: adjust `slPct`. Recalculate MPD = Σ(pxSteps × pxStepsMult^i) for i = 0..maxSafetyOrds−1, then set `slPct` > MPD
- **algoClOrdId duplicate**: error code `51065`

## Communication Guidelines

- **Grid/DCA**: use "bot" not "strategy" (e.g., "grid bot", "DCA bot")
- **DCA**: always say "DCA" or "Martingale" — DCA supports both Spot DCA and Contract DCA
- **Chinese**: Grid = "网格", Spot DCA = "现货马丁", Contract DCA = "合约马丁"
- Use natural language for parameters — "What price range?" not "Enter minPx and maxPx"
- If the user already provides values, map directly — don't re-ask

### Parameter Display Names

> `{base}` and `{quote}`: extract from `instId` by splitting on `-`. E.g., `BTC-USDT-SWAP` → base=BTC, quote=USDT.

#### Grid Bot — Spot (`algoOrdType=grid`)

| API Field | EN | ZH |
|---|---|---|
| `instId` | Trading pair | 交易对 |
| `minPx` | Lower price bound | 网格下限价格 |
| `maxPx` | Upper price bound | 网格上限价格 |
| `gridNum` | Number of grids | 网格数量 |
| `quoteSz` | Investment amount ({quote}) | 投入金额（{quote}） |
| `baseSz` | Investment amount ({base}) | 投入金额（{base}） |
| `runType` | Spacing mode (1=arithmetic, 2=geometric) | 网格间距模式（1=等差, 2=等比） |
| `stopType` | Stop behavior | 停止方式 |

#### Grid Bot — Contract (`algoOrdType=contract_grid`)

| API Field | EN | ZH |
|---|---|---|
| `instId` | Trading pair | 交易对 |
| `minPx` | Lower price bound | 网格下限价格 |
| `maxPx` | Upper price bound | 网格上限价格 |
| `gridNum` | Number of grids | 网格数量 |
| `sz` | Investment margin (USDT for USDT-M; {base} for coin-M) | 投入保证金（USDT-M 为 USDT；币本位为 {base}） |
| `direction` | Direction (long / short / neutral) | 方向（做多 / 做空 / 中性） |
| `lever` | Leverage | 杠杆倍数 |
| `runType` | Spacing mode (1=arithmetic, 2=geometric) | 网格间距模式（1=等差, 2=等比） |
| `basePos` | Open base position | 是否开底仓 |
| `stopType` | Stop behavior | 停止方式 |

#### DCA Bot (Spot & Contract)

| API Field | EN | ZH |
|---|---|---|
| `algoOrdType` | Strategy type (spot/contract) | 策略类型（现货/合约） |
| `instId` | Trading pair | 交易对 |
| `initOrdAmt` | Initial order amount ({quote}) | 首单金额（{quote}） |
| `safetyOrdAmt` | Safety order amount ({quote}) | 补仓金额（{quote}） |
| `maxSafetyOrds` | Max safety orders | 最大补仓次数 |
| `pxSteps` | Price drop per safety order (%) | 补仓价格跌幅（%） |
| `pxStepsMult` | Price step multiplier | 补仓跌幅倍数 |
| `volMult` | Safety order size multiplier | 补仓金额倍数 |
| `tpPct` | Take-profit ratio (%) | 止盈比例（%） |
| `slPct` | Stop-loss ratio (%) | 止损比例（%） |
| `slMode` | Stop-loss type (limit/market) | 止损类型（限价/市价） |
| `lever` | Leverage | 杠杆倍数 |
| `direction` | Direction (long/short) | 方向（做多/做空） |
| `allowReinvest` | Reinvest profit | 利润再投入 |
| `triggerStrategy` | Trigger mode (contract_dca: instant/price/rsi; spot_dca: instant/rsi) | 触发方式 |
| `triggerPx` | Trigger price | 触发价格 |
| `algoClOrdId` | Client order ID | 客户端策略订单 ID |
| `stopType` | Stop type (sell all / keep tokens) | 停止类型（卖出/保留） |
| `reserveFunds` | Reserve funds | 预留资金 |

> **`slPct` stop-loss logic:**
> - Long: stop-loss price = initial fill price × (1 − slPct)
> - Short: stop-loss price = initial fill price × (1 + slPct)
> When triggered and position fully closed, the bot ends.

## Global Notes

- All bots run on OKX servers — stopping the CLI does not affect them
- `--profile` is required for all authenticated commands
- `--json` returns raw OKX API v5 response
- Rate limit: 20 requests per 2 seconds per UID
- Grid `--gridNum` range: 2–100
