---
name: cl-lp-rebalancer
description: "Uniswap V3 集中流动性 LP 自动调仓策略。基于波动率自适应范围宽度：低波动率收紧范围（高资本效率），高波动率放宽范围（减少调仓和 IL）。支持趋势不对称调整、多时间框架分析、自动 claim/remove/swap/deposit 全流程。适用于 EVM L2 链上 CL LP 管理、调仓、范围优化、手续费最大化场景。用户查询收益、PnL、仓位、头寸状态、LP 状况、年化、手续费、无常损失时，调用 status 子命令即可获取（每 5 分钟缓存一次，秒级响应）。"
license: Apache-2.0
metadata:
  author: SynthThoughts
  version: "3.9.0"
  pattern: "pipeline, tool-wrapper"
  steps: "5"
---

# CL LP Auto-Rebalancer v1

Cron 驱动的 Uniswap V3 集中流动性自动调仓机器人，运行在 EVM L2 链上，通过 `onchainos` CLI 执行 DeFi 操作。核心思路：**波动率决定范围宽度** — 低波动率时收紧范围提高资本效率，高波动率时放宽范围减少调仓频率和无常损失。

每个 tick：获取价格 → 波动率分析 → 范围计算 → 调仓决策 → 执行调仓 → 报告。

## Architecture

```
Cron (5min) → Python script → onchainos CLI → OKX Web3 API → Chain
                  ↓                ↓
            cl_lp_state.json    Wallet (TEE signing)
                  ↓
            ┌──────────────┐
            │ Price Fetch   │ ← onchainos swap quote / market price
            │ K-line ATR    │ ← onchainos market kline (1H × 24)
            │ MTF Analysis  │ ← price_history (288 bars = 24h)
            └──────┬───────┘
                   ↓
            Range Calculation (vol-adaptive)
                   ↓
            Rebalance Decision
                   ↓
            ┌──────────────┐
            │ Claim Fees    │ ← onchainos defi claim
            │ Remove Liq    │ ← onchainos defi redeem
            │ Swap Ratio    │ ← onchainos swap swap
            │ Add Liq       │ ← onchainos defi deposit
            └──────┬───────┘
                   ↓
            Structured JSON output
```

**OKX Skill Dependencies** (via `onchainos` CLI — 处理认证、链解析、错误重试):

- Price: `onchainos market price --address <token> --chain <chain>`
- K-line: `onchainos market kline --address <token> --chain <chain> --bar 1H --limit 24`
- Quote: `onchainos swap quote --from <A> --to <B> --amount <amt> --chain <chain>`
- Swap: `onchainos swap swap --from <A> --to <B> --amount <amt> --chain <chain> --wallet <addr> --slippage <pct>`
- Approve: `onchainos swap approve --token <addr> --amount <amt> --chain <chain>`
- Pool Search: `onchainos defi search --chain <chain> --token "<token0>,<token1>" --product-group DEX_POOL`
- Pool Detail: `onchainos defi detail --investment-id <id> --chain <chain>`
- Calculate Entry: `onchainos defi calculate-entry --investment-id <id> --chain <chain> --tick-lower <tick> --tick-upper <tick>`
- Deposit: `onchainos defi deposit --investment-id <id> --chain <chain> --amount0 <amt> --amount1 <amt> --tick-lower <tick> --tick-upper <tick>`
- Redeem: `onchainos defi redeem --investment-id <id> --chain <chain> --token-id <id> --percent 100`
- Claim Fees: `onchainos defi claim --investment-id <id> --chain <chain> --token-id <id>`
- Positions: `onchainos defi positions --chain <chain>`
- Position Detail: `onchainos defi position-detail --investment-id <id> --chain <chain> --token-id <id>`

## Step 0: Pool Selection (First-Time Setup)

When user has no `config.json` or asks to set up a new pool, trigger this step.

**核心原则**：AI 应从用户的自然语言中提取意图，自动推断尽可能多的参数，只在信息不足时才追问。

### 0.1 Intent Recognition

从用户输入中提取：

| 信息 | 示例用户输入 | 提取结果 |
|------|------------|---------|
| 链 | "在 Base 上做 LP" | chain = base |
| 代币对 | "ETH/USDC 的流动性" | token0 = ETH, token1 = USDC |
| 风险偏好 | "稳定一点的" | pool_type = stablecoin |
| Fee tier | "0.3% 的池子" | fee_tier = 0.3% |

**缺失信息的默认推断**：
- 未指定链 → 推荐 Base（L2 gas 低，适合频繁调仓）
- 未指定代币对 → 必须追问（核心参数，无法推断）
- 未指定 fee tier → 根据代币对自动选 TVL 最大的池子
- 未指定风险偏好 → 从代币对自动分类

### 0.2 Pool Type Classification

根据代币对自动分类，**不需要问用户**：

| 类型 | 判断规则 | 默认参数集 |
|------|---------|-----------|
| **稳定币对** | 两个都是稳定币（USDC/USDT/DAI/FRAX） | 窄范围、低止损 |
| **Native/稳定币** | 一个是 ETH/WETH/WBTC，另一个是稳定币 | 标准参数 |
| **非稳定币对** | 两个都不是稳定币，但都是主流币 | 宽范围、高止损 |
| **含 Meme 币** | 代币不在主流币列表中（市值低、无 Coingecko 排名） | 极宽范围 + 强制风险确认 |

主流币白名单：ETH, WETH, WBTC, USDC, USDT, DAI, FRAX, ARB, OP, MATIC, BNB, AVAX, SOL

### 0.3 Meme Coin Risk Gate

**仅当检测到 meme/低市值代币时触发**。MUST display warning before proceeding:

```
⚠️ Meme 币 LP 额外风险：
1. 极端无常损失 — 价格可能单方向暴涨/暴跌 90%+
2. 流动性枯竭 — 池子 TVL 可能骤降，头寸无法退出
3. 合约风险 — 代币可能有 honeypot/税收/暂停转账等恶意机制
4. 调仓失败 — 低流动性导致 swap 滑点过大
```

Must get explicit user confirmation before proceeding.

### 0.4 Search, Rank & Auto-Select

```bash
onchainos defi search --chain <chain> --token "<token0>,<token1>" --product-group DEX_POOL
```

**自动选择逻辑**（用户无需手动选）：
1. 按 TVL 降序排列
2. 如果用户指定了 fee tier → 直接匹配
3. 如果未指定 → 选 TVL 最大的池子（通常是最佳流动性）
4. 展示选择结果供用户确认：池名、fee tier、TVL、预估池 APY（`rate` 字段）

**Fee tier 参考**（仅在用户问及或多池需选择时展示）：
- 0.01%: 稳定币对 · 0.05%: 高相关性对 · 0.3%: 主流对（推荐）· 1%: 高波动对

### 0.5 Generate config.json

自动 fetch detail (`onchainos defi detail`) 并生成 config，**无需用户手动填写**。

**字段映射**：
- `investment_id` ← search `investmentId`
- `chain_id` ← search `chainIndex`
- `platform_id` ← detail `analysisPlatformId`（注意不是 `platformId`）
- `fee_tier` ← search `feeRate`
- `tick_spacing` ← 根据 fee tier 推导：0.01%→1, 0.05%→10, 0.3%→60, 1%→200
- `token0/token1` ← detail `underlyingToken`。如果 token 是 native ETH（`0xeee...`），LP 合约用 WETH，需映射（Base: `0x4200000000000000000000000000000000000006`）
- `native_token` ← 始终 `0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee`（用于 swap 和余额查询）
- 其余参数 ← 根据 pool type 自动填入下表默认值

```json
{
  "investment_id": "<auto>",
  "pool_chain": "<auto>",
  "chain_id": "<auto>",
  "platform_id": "<auto>",
  "native_token": "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee",
  "fee_tier": "<auto>",
  "tick_spacing": "<auto>",
  "token0": { "symbol": "<auto>", "address": "<auto>", "decimals": "<auto>" },
  "token1": { "symbol": "<auto>", "address": "<auto>", "decimals": "<auto>" },
  "range_mult": { "low": 1.0, "medium": 1.2, "high": 1.5, "extreme": 2.0 },
  "min_range_pct": 2,
  "max_range_pct": 5,
  "asym_factor": 0.3,
  "min_position_age_seconds": 3600,
  "max_rebalances_24h": 6,
  "gas_to_fee_ratio": 0.5,
  "max_il_tolerance_pct": 5.0,
  "edge_proximity_threshold": 0.15,
  "stop_loss_pct": 0.15,
  "trailing_stop_pct": 0.1,
  "slippage_pct": 1,
  "gas_reserve_eth": 0.02,
  "min_trade_usd": 5.0,
  "quiet_interval_seconds": 1800,
  "max_consecutive_errors": 5,
  "cooldown_after_errors_seconds": 3600
}
```

**Pool-type-specific defaults**（自动应用，无需用户选择）：

| Parameter | 稳定币对 | Native/稳定币 | 非稳定币 | Meme 池 |
|-----------|---------|-------------|---------|---------|
| `min_range_pct` | 0.5 | 2 | 3 | 5 |
| `max_range_pct` | 2 | 5 | 8 | 15 |
| `range_mult.low` | 0.5 | 1.0 | 1.2 | 1.5 |
| `range_mult.extreme` | 1.0 | 2.0 | 2.5 | 3.0 |
| `stop_loss_pct` | 0.05 | 0.15 | 0.20 | 0.30 |
| `trailing_stop_pct` | 0.03 | 0.10 | 0.15 | 0.20 |
| `max_il_tolerance_pct` | 1.0 | 5.0 | 8.0 | 15.0 |
| `gas_reserve_eth` | 0.005 | 0.02 | 0.02 | 0.02 |

### 0.6 Gate

- [ ] `config.json` written with valid `investment_id`, `token0`, `token1`
- [ ] `.env` configured (copy from `.env.example`, fill in API credentials + `WALLET_ADDR`)
- [ ] `onchainos wallet balance` returns valid balances for the target chain
- [ ] If meme pool: user has explicitly confirmed risk warning

---

## Pipeline: Runtime Steps

**CRITICAL RULE**: Steps MUST execute in order. Do NOT skip steps or proceed past a gate that has not been satisfied.

### Step 1: Data Acquisition

**Actions**:
1. Fetch current price via `onchainos market price` or `onchainos swap quote`
2. Fetch current position detail via `onchainos defi position-detail` (if position exists)
3. Update `price_history` (append, cap at 288 = 24h @ 5min)
4. Fetch on-chain balances via `onchainos wallet balance`

**Gate** (ALL must pass):
- [ ] Price is non-null and > 0
- [ ] Circuit breaker not active (`consecutive_errors < 5`)
- [ ] Stop not triggered (`stop_triggered == null`)

### Step 2: Volatility & Trend Analysis

**Actions**:
1. Fetch K-line data (1H candles, 24 bars) → compute ATR-based volatility (hourly cache)
2. Classify volatility: low (<1.5%), medium (1.5-3%), high (3-5%), extreme (>5%)
3. Compute multi-timeframe trend analysis (复用 grid-trading MTF):
   - Short EMA (25min), Medium EMA (1h), Long EMA (4h)
   - EMA alignment → trend direction (bullish/bearish/neutral) + strength (0-1)
   - 8h structure detection (uptrend/downtrend/ranging)
4. Compute 1h and 4h momentum

**Output**: `atr_pct` float, `vol_class` string, `mtf` dict

**Gate**:
- [ ] `atr_pct` is non-null and > 0
- [ ] `vol_class` is one of: low, medium, high, extreme
- [ ] `mtf` dict has `trend` and `strength` fields (graceful fallback to neutral)

### Step 3: Range Calculation

**Actions**:
1. Compute range width based on volatility class:
   - Low (<1.5%): `2 × ATR` each side → tight range, max capital efficiency
   - Medium (1.5-3%): `3 × ATR` each side → balanced
   - High (3-5%): `5 × ATR` each side → wide range, fewer rebalances
   - Extreme (>5%): `8 × ATR` each side → safety first
2. Apply trend asymmetry (if trend strength > 0.3):
   - Bullish: upper side wider, lower side tighter (跟随上涨空间)
   - Bearish: lower side wider, upper side tighter (防御下跌空间)
3. Convert price range to tick range (aligned to pool's `tick_spacing`)
4. Compute capital efficiency estimate: `price / (upper - lower)`

**Output**: `tick_lower`, `tick_upper`, `range_width_pct`, `capital_efficiency`

**Gate**:
- [ ] `tick_lower < current_tick < tick_upper`
- [ ] Range width >= minimum (2 × tick_spacing)
- [ ] tick values aligned to pool's `tick_spacing`

### Step 4: Rebalance Decision

**Actions**:
1. If no existing position → always deploy (first run)
2. Check rebalance triggers:
   - **Out of range**: price < lower or price > upper → MUST rebalance
3. Anti-churn checks:
   - Position age >= `MIN_POSITION_AGE` (2h)
   - Rebalance count < `MAX_REBALANCES_24H` (6/day)
   - Gas cost < `GAS_TO_FEE_RATIO` × expected fees (50%)
   - New range differs >5% from current range
4. Check stop conditions: stop-loss, trailing stop, IL tolerance

**Gate**:
- [ ] Rebalance trigger identified, OR no rebalance needed (skip to Step 5)
- [ ] All anti-churn checks passed (if rebalancing)
- [ ] No stop condition triggered

### Step 5: Execution & Notification

**Actions** (if rebalancing):
1. Claim accumulated fees: `onchainos defi claim`
2. Remove liquidity: `onchainos defi redeem --percent 100`
3. Calculate target token ratio for new range: `onchainos defi calculate-entry`
4. Swap to correct ratio: `onchainos swap swap` (if needed)
5. Deposit at new range: `onchainos defi deposit`
6. On failure at any sub-step: emergency fallback deploy at 3× normal width
7. Record rebalance in state, update position info

**Actions** (always):
8. Calculate performance metrics (PnL, fees claimed, IL, time-in-range)
9. Build structured notification output (see Notification Tiers below)

**Output**: tiered notification JSON (via `---JSON---` block)

## Tool Wrapper: onchainos CLI Reference

### Prerequisites

```bash
which onchainos  # must be installed
# Auth via environment variables
OKX_API_KEY=...
OKX_SECRET_KEY=...
OKX_PASSPHRASE=...
```

### Core DeFi Operations

| Operation | Command | Key Parameters |
|---|---|---|
| Search Pools | `onchainos defi search --chain base --token "ETH,USDC" --product-group DEX_POOL` | chain, token, product-group |
| Pool Detail | `onchainos defi detail --investment-id <id> --chain base` | investment-id |
| Calculate Entry | `onchainos defi calculate-entry --investment-id <id> --chain base --tick-lower <t> --tick-upper <t>` | ticks, amounts |
| Deposit | `onchainos defi deposit --investment-id <id> --chain base --amount0 <a> --amount1 <a> --tick-lower <t> --tick-upper <t>` | amounts, ticks |
| Redeem | `onchainos defi redeem --investment-id <id> --chain base --token-id <nft> --percent 100` | token-id, percent |
| Claim Fees | `onchainos defi claim --investment-id <id> --chain base --token-id <nft>` | token-id |
| My Positions | `onchainos defi positions --chain base` | chain |
| Position Detail | `onchainos defi position-detail --investment-id <id> --chain base --token-id <nft>` | token-id |

### Market & Swap Operations

| Operation | Command | Key Parameters |
|---|---|---|
| Get Price | `onchainos market price --address <token> --chain base` | token address |
| Get K-line | `onchainos market kline --address <token> --chain base --bar 1H --limit 24` | bar size, limit |
| Swap Quote | `onchainos swap quote --from <A> --to <B> --amount <amt> --chain base` | tokens, amount |
| Execute Swap | `onchainos swap swap --from <A> --to <B> --amount <amt> --chain base --wallet <addr> --slippage 1` | wallet, slippage |
| Approve Token | `onchainos swap approve --token <addr> --amount <amt> --chain base` | token, amount |

### Error Handling Protocol

Every function returns `(result, failure_info)`. Failure info is structured:

```python
failure_info = {
    "reason": str,      # machine-readable: "claim_failed", "redeem_failed", "deposit_failed", etc.
    "detail": str,      # human-readable context
    "retriable": bool,  # safe to auto-retry?
    "hint": str         # "transient_api_error", "retry_with_fresh_quote", "insufficient_balance"
}
```

Auto-retry policy: 1 retry for `retriable=True` with 3s delay.

Rebalance failure fallback: if deposit fails after remove, emergency deploy at 3× normal width.

## Tunable Parameters

### Range Configuration

| Parameter | Default | Description |
|---|---|---|
| `VOL_MULTIPLIER_LOW` | `2.0` | ATR multiplier for low volatility (<1.5%) |
| `VOL_MULTIPLIER_MED` | `3.0` | ATR multiplier for medium volatility (1.5-3%) |
| `VOL_MULTIPLIER_HIGH` | `5.0` | ATR multiplier for high volatility (3-5%) |
| `VOL_MULTIPLIER_EXTREME` | `8.0` | ATR multiplier for extreme volatility (>5%) |
| `VOL_THRESHOLD_LOW` | `1.5` | Low/medium volatility boundary (%) |
| `VOL_THRESHOLD_HIGH` | `3.0` | Medium/high volatility boundary (%) |
| `VOL_THRESHOLD_EXTREME` | `5.0` | High/extreme volatility boundary (%) |
| `TREND_ASYM_FACTOR` | `0.3` | Max trend asymmetry ratio (0=symmetric, 1=fully asymmetric) |
| `TREND_ASYM_THRESHOLD` | `0.3` | Minimum trend strength to activate asymmetry |

### Rebalance Triggers

| Parameter | Default | Description |
|---|---|---|
| `MIN_RANGE_CHANGE_PCT` | `0.05` | Skip rebalance if new range <5% different |

### Anti-Churn Controls

| Parameter | Default | Description |
|---|---|---|
| `MIN_POSITION_AGE` | `7200` | 2h minimum position hold time (seconds) |
| `MAX_REBALANCES_24H` | `6` | Maximum rebalances per 24h period |
| `GAS_TO_FEE_RATIO` | `0.5` | Skip if gas > 50% of expected fees |

### Multi-Timeframe Analysis

| Parameter | Default | Description |
|---|---|---|
| `MTF_SHORT_PERIOD` | `5` | 5-bar EMA (25min @ 5min tick) |
| `MTF_MEDIUM_PERIOD` | `12` | 12-bar EMA (1h @ 5min tick) |
| `MTF_LONG_PERIOD` | `48` | 48-bar EMA (4h @ 5min tick) |
| `MTF_STRUCTURE_PERIOD` | `96` | 96-bar (8h) for structure detection |

### Risk Controls

| Parameter | Default | Description |
|---|---|---|
| `STOP_LOSS_PCT` | `0.15` | Stop if portfolio drops 15% below cost basis |
| `TRAILING_STOP_PCT` | `0.10` | Stop if portfolio drops 10% from peak |
| `MAX_IL_TOLERANCE_PCT` | `0.05` | Hard stop if IL exceeds 5% |
| `MAX_CONSECUTIVE_ERRORS` | `5` | Circuit breaker threshold |
| `COOLDOWN_AFTER_ERRORS` | `3600` | 1h cooldown after circuit breaker trips |
| `GAS_RESERVE` | `0.003` | Native token reserved for gas |

### Execution

| Parameter | Default | Description |
|---|---|---|
| `SLIPPAGE_PCT` | `1` | Slippage tolerance for swaps |
| `EMERGENCY_WIDTH_MULT` | `3.0` | Emergency fallback range = 3× normal width |
| `DRY_RUN` | `false` | Fetch real data but simulate operations |

## Risk Control Flow

```
[1] stop_triggered → refuse all operations, emit alert JSON
[2] circuit_breaker (consecutive_errors >= 5) → 1h cooldown, refuse
[3] data validation (price/balance/position null) → refuse
[4] stop-loss / trailing-stop / IL tolerance → set stop_triggered, alert
[5] rebalance frequency (>6/day) → skip rebalance
[6] position age (<2h) → skip rebalance
[7] gas cost check (>50% of expected fees) → skip rebalance
[8] minimum range change (<5%) → skip rebalance
[9] execute rebalance → success / failure with emergency fallback
```

## Operational Interface

### Sub-Commands

| Command | Purpose | Trigger | Notification |
|---|---|---|---|
| `tick` | 主循环：采集→分析→决策→执行，结果缓存到 `_cached_snapshot` | Cron 每 5min | 🔔 Trade Alert / ⚠️ Risk Alert / 📊 Hourly Pulse |
| `status` | **用户查询入口**：Portfolio 总览 + 头寸 + 收益 + 范围。优先读 5min 缓存（秒级响应），过期才实时查询 | 用户主动 | 终端输出（不推送） |
| `report` | 每日绩效报告 | Cron 每日 00:00 UTC | 📈 Daily Report |
| `history` | 调仓历史 | 用户主动 | 终端输出（不推送） |
| `analyze` | 详细 JSON 分析（波动率、范围、效率） | AI agent | 终端输出（不推送） |
| `reset` | 关闭头寸并重新部署 | 手动 | 🔔 Trade Alert |
| `close` | 完全退出头寸 | 手动 | 🔔 Trade Alert |

**`status` 触发词**（用户说以下任意内容时应调用 `status`）：
- 查询收益、收益怎么样、赚了多少、PnL、盈亏
- 查询仓位、头寸状态、LP 状况、仓位情况
- 年化多少、APY、费用收入、手续费
- 无常损失、IL
- 总资产、Portfolio、余额
- LP 里有多少 ETH / USDC

```python
COMMANDS = {
    "tick": tick, "status": status, "report": report,
    "history": history_cmd, "reset": reset, "close": close,
    "analyze": analyze
}
if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "tick"
    COMMANDS.get(cmd, tick)()
```

### Notification Tiers

脚本内部封装完整的消息格式化和可视化逻辑，通过 `---JSON---` 块输出结构化数据（含 `notification` 渲染块），由调度器路由到通信渠道。

| Tier | 触发条件 | 推送 |
|------|---------|------|
| **Trade Alert** | 调仓成功或失败 | 每次交易立即推送 |
| **Risk Alert** | 止损/熔断/连续错误 | 立即推送 |
| **Hourly Pulse** | 距上次推送 ≥ `QUIET_INTERVAL` 且无交易 | 每小时推送 |
| **Daily Report** | `report` 命令 (cron daily) | 每日推送 |

`status`/`analyze` 命令为用户主动查询，直接输出到终端，不推送。`status` 优先从 `_cached_snapshot`（每 5min tick 时写入）读取已计算好的数据，无需任何 API 调用即可返回完整状态（Portfolio 跨平台总览 + 头寸 + PnL + IL + APY + LP 代币拆分）。缓存过期（>360s）时自动 fallback 到实时查询。

脚本负责：消息标题、字段组织、范围位置可视化、颜色级别、footer 上下文。调度器只需透传 `notification` 块到通信平台。

## State Schema

```json
{
  "version": 1,
  "pool": {
    "investment_id": "uniswap-v3-base-eth-usdc-3000",
    "chain": "base",
    "chain_id": 8453,
    "token0": "0x4200000000000000000000000000000000000006",
    "token1": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
    "fee_tier": 3000,
    "tick_spacing": 60
  },
  "position": {
    "token_id": null,
    "tick_lower": null,
    "tick_upper": null,
    "price_lower": null,
    "price_upper": null,
    "created_at": null,
    "created_atr_pct": null,
    "created_vol_class": null
  },
  "price_history": [],
  "vol_history": [],
  "rebalance_history": [
    {
      "time": "ISO timestamp",
      "trigger": "out_of_range",
      "old_range": [-198120, -197400],
      "new_range": [-198300, -197100],
      "fees_claimed_usd": 1.25
    }
  ],
  "stats": {
    "total_rebalances": 0,
    "total_fees_claimed_usd": 0,
    "unclaimed_fee_usd": 0,
    "time_in_range_pct": 100,
    "initial_portfolio_usd": null,
    "total_deposits_usd": 0,
    "portfolio_peak_usd": null,
    "started_at": null,
    "last_check": null
  },
  "errors": {
    "consecutive": 0,
    "cooldown_until": null
  },
  "stop_triggered": null,
  "kline_cache": null,
  "mtf_cache": null,
  "last_quiet_report": null
}
```

Key fields:
- `pool`: target pool configuration (chain, tokens, fee tier, tick spacing)
- `position.token_id`: NFT position ID (null if no active position)
- `position.created_atr_pct`: ATR at position creation (for vol shift detection)
- `rebalance_history`: full audit trail of all rebalances with costs
- `stats.time_in_range_pct`: key performance metric — % of ticks where price was in range
- `stats.initial_portfolio_usd` + `total_deposits_usd`: PnL 计算的成本基准
- `stats.total_fees_claimed_usd` + `unclaimed_fee_usd`: LP 手续费总收入，用于推导 IL
- `stop_triggered`: string describing trigger condition, or null

## Core Algorithm

```
1. Fetch current price
2. Fetch position detail (if exists)
3. Update price_history (cap at 288 = 24h)
4. Fetch K-line data (1H × 24) → compute ATR volatility (hourly cache)
5. Classify volatility → vol_class (low/medium/high/extreme)
6. Multi-timeframe analysis → trend/strength/momentum/structure
7. Compute optimal range:
   a. Base width = VOL_MULTIPLIER[vol_class] × ATR each side
   b. Apply trend asymmetry (upper/lower sides)
   c. Convert to ticks, align to tick_spacing
8. Check rebalance triggers:
   a. Out of range → must rebalance
9. Anti-churn gates (position age, frequency, gas cost, range change)
10. If rebalancing:
    a. Claim fees → remove liquidity → swap to ratio → deposit at new range
    b. On failure: emergency fallback at 3× width
11. Check stop conditions (stop-loss, trailing stop, IL tolerance)
12. Calculate performance metrics
13. Report status (structured JSON)
```

## Deployment

### OpenClaw Cron (recommended)

```bash
# Register tick (every 5 minutes)
zeroclaw cron add '*/5 * * * *' \
  'cd ~/.openclaw/skills/cl-lp-rebalancer/references && set -a && . ../.env && set +a && python3 cl_lp.py tick'

# Register daily report (08:00 CST = 00:00 UTC)
zeroclaw cron add '0 0 * * *' \
  'cd ~/.openclaw/skills/cl-lp-rebalancer/references && set -a && . ../.env && set +a && python3 cl_lp.py report'
```

### Manual

```bash
# Single tick
python3 cl_lp.py tick

# Dry run (fetch real data, simulate operations)
DRY_RUN=true python3 cl_lp.py tick

# Status check
python3 cl_lp.py status

# Close position and exit
python3 cl_lp.py close
```

## Failure & Rollback

```
IF rebalance sub-step fails:
  1. Log failure reason to cl_lp.log
  2. Increment errors.consecutive
  3. If errors.consecutive >= 5: trigger circuit breaker (1h cooldown)
  4. If failure after remove liquidity: emergency deploy at 3× normal width
     (priority: get funds back into a position, even if suboptimal)
  5. Report failure via JSON output
  6. On next tick: retry from last successful sub-step if possible
```

## Anti-Patterns

| Pattern | Problem |
|---|---|
| Rebalance every tick | Gas costs eat all fee income |
| Too tight range in high vol | Constant out-of-range, excessive rebalancing |
| Too wide range in low vol | Capital inefficiency, minimal fee capture |
| No minimum position age | Rapid back-and-forth rebalancing (churn) |
| Skip emergency fallback | Funds sit idle after failed rebalance (zero yield) |
| Ignore gas costs | L1 gas can exceed daily fee income |
| Symmetric range in trends | Miss upside in bull, excess downside in bear |
| No IL tracking | Cannot detect when IL exceeds fee income |
| Rebalance on vol change alone | Minor ATR fluctuations cause unnecessary churn — only rebalance when out of range |
| No time-in-range tracking | Cannot measure strategy effectiveness |
