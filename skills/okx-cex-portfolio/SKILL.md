---
name: okx-cex-portfolio
description: "This skill should be used when the user asks about 'account balance', 'how much USDT do I have', 'my funding account', 'show my positions', 'open positions', 'position P&L', 'unrealized PnL', 'closed positions', 'position history', 'realized PnL', 'account bills', 'transaction history', 'trading fees', 'fee tier', 'account config', 'max order size', 'how much can I buy', 'withdrawable amount', 'transfer funds', 'move USDT to trading account', or 'switch position mode'. Requires API credentials. Do NOT use for market prices (use okx-cex-market), placing/cancelling orders (use okx-cex-trade), or grid/DCA bots (use okx-cex-bot)."
license: MIT
metadata:
  author: okx
  version: "1.0.0"
  homepage: "https://www.okx.com"
  agent:
    requires:
      bins: ["okx"]
    install:
      - id: npm
        kind: node
        package: "@okx_ai/okx-trade-cli"
        bins: ["okx"]
        label: "Install okx CLI (npm)"
---

# OKX CEX Portfolio & Account CLI

Account balance, positions, P&L, bills, fees, and fund transfers on OKX exchange. **Requires API credentials.**

## Prerequisites

1. Install `okx` CLI:
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. Configure credentials:
   ```bash
   okx config init
   ```
   Or set environment variables:
   ```bash
   export OKX_API_KEY=your_key
   export OKX_SECRET_KEY=your_secret
   export OKX_PASSPHRASE=your_passphrase
   ```
3. Test with demo mode:
   ```bash
   okx --profile demo account balance
   ```

## Credential & Profile Check

**Run this check before any authenticated command.**

### Step A — Verify credentials

```bash
okx config show       # verify configuration status (output is masked)
```

- If the command returns an error or shows no configuration: **stop all operations**, guide the user to run `okx config init`, and wait for setup to complete before retrying.
- If credentials are configured: proceed to Step B.

### Step B — Confirm profile (required)

`--profile` is **required** for all authenticated commands. Never add a profile implicitly.

| Value | Mode | Funds |
|---|---|---|
| `live` | 实盘 | Real funds |
| `demo` | 模拟盘 | Simulated funds |

**Resolution rules:**
1. Current message intent is clear (e.g. "real" / "实盘" / "live" → `live`; "test" / "模拟" / "demo" → `demo`) → use it and inform the user: `"Using --profile live (实盘)"` or `"Using --profile demo (模拟盘)"`
2. Current message has no explicit declaration → check conversation context for a previous profile:
   - Found → use it, inform user: `"Continuing with --profile live (实盘) from earlier"`
   - Not found → ask: `"Live (实盘) or Demo (模拟盘)?"` — wait for answer before proceeding

### Handling 401 Authentication Errors

If any command returns a 401 / authentication error:
1. **Stop immediately** — do not retry the same command
2. Inform the user: "Authentication failed (401). Your API credentials may be invalid or expired."
3. Guide the user to update credentials by editing the file directly with their local editor:
   ```
   ~/.okx/config.toml
   ```
   Update the fields `api_key`, `secret_key`, `passphrase` under the relevant profile.
   Do NOT paste the new credentials into chat.
4. After the user confirms the file is updated, run `okx config show` to verify (output is masked)
5. Only then retry the original operation

## Demo vs Live Mode

Profile is the single control for 实盘/模拟盘 switching — exactly two options:

| `--profile` | Mode | Funds |
|---|---|---|
| `live` | 实盘 | Real funds |
| `demo` | 模拟盘 | Simulated funds |

```bash
okx --profile live  account balance     # 实盘
okx --profile demo  account balance     # 模拟盘 (simulated balance)
```

**Rules:**
- **Read commands** (balance, positions, bills, etc.): always state which profile was used
- **Write commands** (`transfer`, `set-position-mode`): **profile must be confirmed before execution** (see "Credential & Profile Check" Step B); transfer especially — wrong profile means wrong account
- Every response after a command must append: `[profile: live]` or `[profile: demo]`
- Do **not** use the `--demo` flag — use `--profile` instead

## Skill Routing

- For market data (prices, charts, depth, funding rates) → use `okx-cex-market`
- For account balance, P&L, positions, fees, transfers → use `okx-cex-portfolio` (this skill)
- For regular spot/swap/futures/algo orders → use `okx-cex-trade`
- For grid and DCA trading bots → use `okx-cex-bot`

## Quickstart

```bash
# Trading account balance (all currencies with balance > 0)
okx account balance

# Check USDT balance only
okx account balance USDT

# Funding account balance
okx account asset-balance

# All open positions
okx account positions

# Closed position history with realized PnL
okx account positions-history

# Recent account bills (last 100)
okx account bills

# My trading fee tier
okx account fees --instType SPOT

# Transfer 100 USDT from funding (18) to trading (6)
okx account transfer --ccy USDT --amt 100 --from 18 --to 6
```

## Command Index

### Read Commands

| # | Command | Type | Description |
|---|---|---|---|
| 1 | `okx account balance [ccy]` | READ | Trading account equity, available, frozen |
| 2 | `okx account asset-balance [ccy]` | READ | Funding account balance |
| 3 | `okx account positions` | READ | Open contract/swap positions |
| 4 | `okx account positions-history` | READ | Closed positions + realized PnL |
| 5 | `okx account bills` | READ | Account ledger (deposits, withdrawals, trades) |
| 6 | `okx account fees --instType <type>` | READ | My trading fee tier (maker/taker) |
| 7 | `okx account config` | READ | Account level, position mode, UID |
| 8 | `okx account max-size --instId <id> --tdMode <mode>` | READ | Max buy/sell size at current price |
| 9 | `okx account max-avail-size --instId <id> --tdMode <mode>` | READ | Available size for next order |
| 10 | `okx account max-withdrawal [ccy]` | READ | Max withdrawable per currency |

### Write Commands

| # | Command | Type | Description |
|---|---|---|---|
| 11 | `okx account set-position-mode <mode>` | WRITE | Switch net/hedge position mode |
| 12 | `okx account transfer` | WRITE | Transfer funds between accounts |

## Cross-Skill Workflows

### Pre-trade balance check
> User: "I want to buy 0.1 BTC — do I have enough USDT?"

```
1. okx-cex-portfolio okx account balance USDT               → check available equity
2. okx-cex-market    okx market ticker BTC-USDT              → check current price
        ↓ user approves
3. okx-cex-trade     okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.1
```

### Pre-bot balance check
> User: "I want to start a BTC grid bot with 1000 USDT"

```
1. okx-cex-portfolio okx account balance USDT               → confirm available funds ≥ 1000
2. okx-cex-market    okx market candles BTC-USDT --bar 4H --limit 50  → determine price range
        ↓ user approves
3. okx-cex-bot       okx bot grid create --instId BTC-USDT --algoOrdType grid \
                       --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000
```

### Review open positions and P&L
> User: "Show me my current positions and how they're performing"

```
1. okx-cex-portfolio okx account positions                  → open positions with UPL
2. okx-cex-portfolio okx account positions-history          → recently closed positions
3. okx-cex-market    okx market ticker BTC-USDT-SWAP        → check current price vs entry
```

### Transfer and trade
> User: "Move 500 USDT from my funding account to trade BTC"

```
1. okx-cex-portfolio okx account asset-balance USDT         → confirm funding balance ≥ 500
        ↓ user approves
2. okx-cex-portfolio okx account transfer --ccy USDT --amt 500 --from 18 --to 6
3. okx-cex-portfolio okx account balance USDT               → confirm trading balance updated
        ↓ ready to trade
4. okx-cex-trade     okx spot place ...
```

### Check max position size before entering
> User: "How much BTC can I buy with cross margin?"

```
1. okx-cex-portfolio okx account balance                    → total equity
2. okx-cex-portfolio okx account max-size --instId BTC-USDT-SWAP --tdMode cross  → max buy/sell size
3. okx-cex-market    okx market ticker BTC-USDT-SWAP        → current price reference
```

## Operation Flow

### Step 0 — Credential & Profile Check

Before any authenticated command:

**Determine profile (required):**
- Options: `live` (实盘) or `demo` (模拟盘) — exactly these two values
1. Current message intent clear (e.g. "real"/"实盘"/"live" → live; "test"/"模拟"/"demo" → demo) → use it, inform user: `"Using --profile live (实盘)"`
2. Current message has no explicit declaration → check conversation context for previous profile:
   - Found → use it, inform user: `"Continuing with --profile live (实盘) from earlier"`
   - Not found → ask: `"Live (实盘) or Demo (模拟盘)?"` — wait for answer

**If no credentials configured:** guide user to run `okx config init`, stop all trading actions

**After every command result:** append `[profile: live]` or `[profile: demo]` to the response

### Step 1: Identify account action

- Check balance → `okx account balance` (trading) or `okx account asset-balance` (funding)
- View open positions → `okx account positions`
- View closed positions + PnL → `okx account positions-history`
- View transaction history → `okx account bills`
- Check fee tier → `okx account fees`
- Check account settings → `okx account config`
- Calculate order size → `okx account max-size` or `okx account max-avail-size`
- Check withdrawal limit → `okx account max-withdrawal`
- Transfer funds → `okx account transfer`
- Change position mode → `okx account set-position-mode`

### Step 2: Run read commands immediately — confirm profile (Step 0) then writes

**Read commands** (1–10): run immediately, no confirmation needed.

- `ccy` filter: use currency symbol like `USDT`, `BTC`, `ETH`
- `--instType` for fees/positions: `SPOT`, `SWAP`, `FUTURES`, `OPTION`
- `--archive` for bills: access older records beyond the default window
- `--tdMode` for max-size: `cash` (spot), `cross`, or `isolated`

**Write commands** (11–12): confirm once before executing.

- `set-position-mode`: confirm mode (`net` = one-directional, `long_short_mode` = hedge mode); switching may affect open positions
- `transfer`: confirm `--ccy`, `--amt`, `--from`, `--to` (account types: `6`=trading, `18`=funding); verify source balance first

### Step 3: Verify after writes

- After `set-position-mode`: run `okx account config` to confirm `posMode` updated
- After `transfer`: run `okx account balance` and `okx account asset-balance` to confirm balances updated

## CLI Command Reference

### Account Balance — Trading Account

```bash
okx account balance [ccy] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `ccy` | No | - | Filter to a single currency (e.g., `USDT`) |

Returns table: `currency`, `equity`, `available`, `frozen`. Only shows currencies with balance > 0.

---

### Asset Balance — Funding Account

```bash
okx account asset-balance [ccy] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `ccy` | No | - | Filter to a single currency |

Returns: `ccy`, `bal`, `availBal`, `frozenBal`. Only shows currencies with balance > 0.

---

### Positions — Open Positions

```bash
okx account positions [--instType <type>] [--instId <id>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--instType` | No | - | Filter: `SWAP`, `FUTURES`, `OPTION` |
| `--instId` | No | - | Filter to specific instrument |

Returns: `instId`, `instType`, `side` (posSide), `pos`, `avgPx`, `upl` (unrealized PnL), `lever`. Only shows positions with size ≠ 0.

---

### Positions History — Closed Positions

```bash
okx account positions-history [--instType <type>] [--instId <id>] [--limit <n>] [--json]
```

Returns: `instId`, `direction`, `openAvgPx`, `closeAvgPx`, `realizedPnl`, `uTime`.

---

### Bills — Account Ledger

```bash
okx account bills [--archive] [--instType <type>] [--ccy <ccy>] [--limit <n>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--archive` | No | false | Access older records (archive endpoint) |
| `--instType` | No | - | Filter by instrument type |
| `--ccy` | No | - | Filter by currency |
| `--limit` | No | 100 | Number of records |

Returns: `billId`, `instId`, `type`, `ccy`, `balChg`, `bal`, `ts`.

---

### Fees — Trading Fee Tier

```bash
okx account fees --instType <type> [--instId <id>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--instType` | Yes | - | `SPOT`, `SWAP`, `FUTURES`, `OPTION` |
| `--instId` | No | - | Specific instrument (optional) |

Returns: `level`, `maker`, `taker`, `makerU`, `takerU`, `ts`.

---

### Config — Account Configuration

```bash
okx account config [--json]
```

Returns: `uid`, `acctLv` (account level), `posMode` (net/long_short_mode), `autoLoan`, `greeksType`, `level`, `levelTmp`.

---

### Max Size — Maximum Order Size

```bash
okx account max-size --instId <id> --tdMode <mode> [--px <price>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--instId` | Yes | - | Instrument ID |
| `--tdMode` | Yes | - | `cash` (spot), `cross`, or `isolated` |
| `--px` | No | - | Reference price (uses mark price if omitted) |

Returns: `instId`, `maxBuy`, `maxSell`.

---

### Max Available Size

```bash
okx account max-avail-size --instId <id> --tdMode <mode> [--json]
```

Returns: `instId`, `availBuy`, `availSell` — the immediately available size for the next order.

---

### Max Withdrawal

```bash
okx account max-withdrawal [ccy] [--json]
```

Returns table: `ccy`, `maxWd`, `maxWdEx` (with borrowing). Shows all currencies if no filter.

---

### Set Position Mode

```bash
okx account set-position-mode <net|long_short_mode> [--json]
```

| Value | Behavior |
|---|---|
| `net` | One-directional (default) — long and short net out |
| `long_short_mode` | Hedge mode — long and short can coexist |

> **Warning**: Switching modes when positions are open may cause unexpected behavior. Check `okx account positions` first.

---

### Transfer Funds

```bash
okx account transfer --ccy <ccy> --amt <n> --from <acctType> --to <acctType> \
  [--transferType <type>] [--subAcct <name>] [--json]
```

| Param | Required | Default | Description |
|---|---|---|---|
| `--ccy` | Yes | - | Currency to transfer (e.g., `USDT`) |
| `--amt` | Yes | - | Amount to transfer |
| `--from` | Yes | - | Source account type: `6`=trading, `18`=funding |
| `--to` | Yes | - | Destination account type: `6`=trading, `18`=funding |
| `--transferType` | No | `0` | `0`=within account, `1`=to sub-account, `2`=from sub-account |
| `--subAcct` | No | - | Sub-account name (required for sub-account transfers) |

Returns: `transId`, `ccy`, `amt`.

---

## MCP Tool Reference

| Tool | Description |
|---|---|
| `account_get_balance` | Trading account balance |
| `account_get_asset_balance` | Funding account balance |
| `account_get_positions` | Open positions |
| `account_get_positions_history` | Closed position history |
| `account_get_bills` | Account bills (recent) |
| `account_get_bills_archive` | Account bills (archive) |
| `account_get_trade_fee` | Trading fee tier |
| `account_get_config` | Account configuration |
| `account_get_max_size` | Max order size |
| `account_get_max_avail_size` | Max available size |
| `account_get_max_withdrawal` | Max withdrawable |
| `account_set_position_mode` | Set position mode |
| `account_transfer` | Transfer between accounts |

---

## Input / Output Examples

**"How much USDT do I have?"**
```bash
okx account balance USDT
# → currency: USDT | equity: 5000.00 | available: 4500.00 | frozen: 500.00
```

**"Show all my open positions"**
```bash
okx account positions
# → table: instId, instType, side, pos, avgPx, upl, lever
```

**"What's my trading history and realized PnL?"**
```bash
okx account positions-history
# → table: instId, direction, openAvgPx, closeAvgPx, realizedPnl, uTime
```

**"Show my recent account activity"**
```bash
okx account bills --limit 20
# → table: billId, instId, type, ccy, balChg, bal, ts
```

**"What are my trading fees for SWAP?"**
```bash
okx account fees --instType SWAP
# → level: VIP1 | maker: -0.0001 | taker: 0.0005
```

**"How much BTC can I buy in cross margin?"**
```bash
okx account max-size --instId BTC-USDT-SWAP --tdMode cross
# → instId: BTC-USDT-SWAP | maxBuy: 12.5 | maxSell: 12.5
```

**"Transfer 200 USDT from funding to trading"**
```bash
okx account transfer --ccy USDT --amt 200 --from 18 --to 6
# → Transfer: TXN123456 (USDT 200)
```

**"Check my account config"**
```bash
okx account config
# → uid: 123456789 | acctLv: 2 | posMode: net | autoLoan: false
```

## Edge Cases

- **No balance shown**: balance is filtered to > 0 — if nothing shows, all currencies have zero balance
- **Positions command returns empty**: no open contracts; spot holdings are not shown here (use `account balance`)
- **bills --archive**: required for transactions older than 7 days (default window); may be slower
- **set-position-mode**: cannot switch to `net` if you have both long and short positions on the same instrument
- **transfer --from/--to codes**: `6`=trading account, `18`=funding account; other values exist for sub-account flows
- **max-size vs max-avail-size**: `max-size` is the theoretical maximum; `max-avail-size` accounts for existing orders and reserved margin
- **Demo mode**: `okx --profile demo account balance` shows simulated balances, not real funds

## Global Notes

- All write commands require valid credentials in `~/.okx/config.toml` or env vars
- `--profile <name>` is required for all authenticated commands; see "Credential & Profile Check" section
- Every command result includes a `[profile: <name>]` tag for audit reference
- `--json` returns raw OKX API v5 response
- Rate limit: 10 requests per 2 seconds for account endpoints
- Positions shown are for the unified trading account; funding account assets are separate
- Account types: `6`=Unified Trading Account (spot + derivatives), `18`=Funding Account (deposits/withdrawals)
