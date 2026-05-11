# Range Algorithm Documentation

CL LP Auto-Rebalancer 的核心范围计算算法详解。

## Overview

核心思想：**波动率决定范围宽度**。

```
ATR(24h) → 波动率分类 → 范围乘数 → 趋势不对称调整 → tick 对齐 → 最终范围
```

低波动率时收紧范围以提高资本效率（更多手续费捕获），高波动率时放宽范围以减少调仓频率和无常损失。

## Step 1: ATR Calculation

使用 1H K 线（24 根）计算 Average True Range：

```python
def calc_atr(candles):
    """Calculate ATR from 1H OHLCV candles."""
    true_ranges = []
    for i in range(1, len(candles)):
        high = float(candles[i]["high"])
        low = float(candles[i]["low"])
        prev_close = float(candles[i-1]["close"])
        tr = max(
            high - low,              # 当前 bar 振幅
            abs(high - prev_close),  # 跳空高开
            abs(low - prev_close)    # 跳空低开
        )
        true_ranges.append(tr)
    return sum(true_ranges) / len(true_ranges) if true_ranges else 0

# ATR percentage (relative to current price)
atr_pct = (atr / current_price) * 100
```

**Why ATR over stddev?** ATR 使用 OHLC 数据（包含 bar 内波动），比收盘价标准差更准确地反映真实波动幅度。特别是在有大影线但收盘价变化不大的情况下，ATR 能捕获到 stddev 忽略的波动。

## Step 2: Volatility Classification

将 ATR 百分比映射到波动率等级：

```python
VOL_THRESHOLD_LOW = 1.5      # %
VOL_THRESHOLD_HIGH = 3.0     # %
VOL_THRESHOLD_EXTREME = 5.0  # %

def classify_volatility(atr_pct):
    if atr_pct < VOL_THRESHOLD_LOW:
        return "low"
    elif atr_pct < VOL_THRESHOLD_HIGH:
        return "medium"
    elif atr_pct < VOL_THRESHOLD_EXTREME:
        return "high"
    else:
        return "extreme"
```

| Volatility Class | ATR Range | Market Condition |
|---|---|---|
| Low | < 1.5% | 横盘/低波动，典型的低流动性时段 |
| Medium | 1.5% - 3% | 正常交易，常见日间波动 |
| High | 3% - 5% | 活跃行情，新闻驱动的波动 |
| Extreme | > 5% | 极端事件，黑天鹅，闪崩 |

## Step 3: Base Range Width

每个波动率等级对应一个 ATR 乘数：

```python
VOL_MULTIPLIERS = {
    "low":     1.0,   # 紧凑范围 → 最高资本效率 (Base gas ≈ 0)
    "medium":  2.0,   # 平衡
    "high":    3.5,   # 宽范围 → 减少调仓
    "extreme": 6.0,   # 极宽 → 安全优先
}

def calc_base_range(price, atr, vol_class):
    multiplier = VOL_MULTIPLIERS[vol_class]
    half_width = atr * multiplier
    return (price - half_width, price + half_width)
```

**Examples** (ETH at $2000):

| Vol Class | ATR | Multiplier | Half Width | Range | Width % | Capital Efficiency |
|---|---|---|---|---|---|---|
| Low | $25 (1.25%) | 2× | $50 | $1950-$2050 | 5.0% | 20× |
| Medium | $45 (2.25%) | 3× | $135 | $1865-$2135 | 13.5% | 7.4× |
| High | $70 (3.5%) | 5× | $350 | $1650-$2350 | 35.0% | 2.9× |
| Extreme | $120 (6%) | 8× | $960 | $1040-$2960 | 96.0% | 1.0× |

**Capital Efficiency** = `price / range_width`。越高表示同样的流动性能捕获更多手续费，但出范围的风险也更高。

## Step 4: Trend Asymmetry

复用 grid-trading 的多时间框架 (MTF) 趋势分析，根据趋势方向调整上下范围的不对称性：

```python
TREND_ASYM_FACTOR = 0.3      # 最大不对称比例
TREND_ASYM_THRESHOLD = 0.3   # 激活不对称的最小趋势强度

def apply_trend_asymmetry(lower, upper, price, mtf):
    """Adjust range asymmetrically based on trend direction."""
    trend = mtf.get("trend", "neutral")
    strength = mtf.get("strength", 0)

    if strength < TREND_ASYM_THRESHOLD:
        return lower, upper  # 弱趋势 → 保持对称

    asym = TREND_ASYM_FACTOR * strength
    half_width = (upper - lower) / 2

    if trend == "bullish":
        # 看涨：上方放宽（跟随上涨空间），下方收紧（减少下方暴露）
        new_upper = price + half_width * (1 + asym)
        new_lower = price - half_width * (1 - asym)
    elif trend == "bearish":
        # 看跌：下方放宽（防御下跌空间），上方收紧
        new_upper = price + half_width * (1 - asym)
        new_lower = price - half_width * (1 + asym)
    else:
        return lower, upper

    return new_lower, new_upper
```

**Asymmetry Examples** (ETH at $2000, medium vol, half_width=$135):

| Trend | Strength | Asym | Lower | Upper | Effect |
|---|---|---|---|---|---|
| Neutral | 0.1 | 0 | $1865 | $2135 | Symmetric |
| Bullish | 0.5 | 0.15 | $1885 | $2155 | Upper wider, lower tighter |
| Bullish | 0.9 | 0.27 | $1899 | $2171 | Max upper stretch |
| Bearish | 0.5 | 0.15 | $1845 | $2115 | Lower wider, upper tighter |
| Bearish | 0.9 | 0.27 | $1829 | $2101 | Max lower stretch |

**Why asymmetric?**
- 看涨趋势中，价格更可能向上突破。上方放宽减少向上出范围的概率，延长持仓时间。
- 看跌趋势中，价格更可能向下突破。下方放宽提供更多缓冲，延迟被迫调仓的时机。

## Step 5: Tick Math & Alignment

Uniswap V3 使用 tick 系统表示价格，tick 和价格的关系：

```
price = 1.0001 ^ tick
tick = log(price) / log(1.0001)
```

每个池有固定的 `tick_spacing`（如 0.3% fee tier → tick_spacing=60），头寸的 tick_lower 和 tick_upper 必须是 tick_spacing 的整数倍。

```python
import math

def price_to_tick(price):
    """Convert price to Uniswap V3 tick."""
    return int(math.floor(math.log(price) / math.log(1.0001)))

def tick_to_price(tick):
    """Convert tick to price."""
    return 1.0001 ** tick

def align_tick(tick, tick_spacing, direction="down"):
    """Align tick to nearest valid tick_spacing multiple."""
    if direction == "down":
        return (tick // tick_spacing) * tick_spacing
    else:
        return ((tick + tick_spacing - 1) // tick_spacing) * tick_spacing

def calc_tick_range(price_lower, price_upper, tick_spacing):
    """Convert price range to aligned tick range."""
    tick_lower = align_tick(price_to_tick(price_lower), tick_spacing, "down")
    tick_upper = align_tick(price_to_tick(price_upper), tick_spacing, "up")

    # Ensure minimum range
    if tick_upper - tick_lower < 2 * tick_spacing:
        tick_upper = tick_lower + 2 * tick_spacing

    return tick_lower, tick_upper
```

**Tick Spacing by Fee Tier**:

| Fee Tier | Fee | tick_spacing | Min Range (2 × spacing) |
|---|---|---|---|
| 100 | 0.01% | 1 | ~0.02% |
| 500 | 0.05% | 10 | ~0.20% |
| 3000 | 0.30% | 60 | ~1.20% |
| 10000 | 1.00% | 200 | ~4.04% |

**Important**: ETH/USDC 0.3% fee tier 使用 tick_spacing=60。每 60 ticks 约 0.6% 价格变化。

## Step 6: Complete Range Calculation

将以上步骤组合成完整的范围计算函数：

```python
def calc_optimal_range(price, candles, mtf, tick_spacing):
    """
    Calculate optimal LP range based on volatility and trend.

    Returns: (tick_lower, tick_upper, range_info)
    """
    # Step 1: ATR
    atr = calc_atr(candles)
    atr_pct = (atr / price) * 100

    # Step 2: Classify
    vol_class = classify_volatility(atr_pct)

    # Step 3: Base range
    lower, upper = calc_base_range(price, atr, vol_class)

    # Step 4: Trend asymmetry
    lower, upper = apply_trend_asymmetry(lower, upper, price, mtf)

    # Step 5: Tick alignment
    tick_lower, tick_upper = calc_tick_range(lower, upper, tick_spacing)

    # Actual prices after alignment
    price_lower = tick_to_price(tick_lower)
    price_upper = tick_to_price(tick_upper)

    # Capital efficiency
    range_width = price_upper - price_lower
    capital_efficiency = price / range_width if range_width > 0 else 0

    range_info = {
        "atr": atr,
        "atr_pct": atr_pct,
        "vol_class": vol_class,
        "multiplier": VOL_MULTIPLIERS[vol_class],
        "price_lower": price_lower,
        "price_upper": price_upper,
        "range_width_pct": (range_width / price) * 100,
        "capital_efficiency": capital_efficiency,
        "trend": mtf.get("trend", "neutral"),
        "trend_strength": mtf.get("strength", 0),
        "asymmetric": mtf.get("strength", 0) >= TREND_ASYM_THRESHOLD,
    }

    return tick_lower, tick_upper, range_info
```

## Rebalance Trigger Conditions

### Trigger 1: Out of Range (priority: MUST)

当前价格超出头寸范围。此时 LP 完全停止赚取手续费，必须调仓。

```python
def check_out_of_range(price, position):
    return price < position["price_lower"] or price > position["price_upper"]
```

### Trigger 2: Volatility Shift (priority: ADAPTIVE)

波动率显著变化，当前范围不再最优。

```python
VOL_SHIFT_THRESHOLD = 0.30  # 30%

def check_vol_shift(current_atr_pct, position_atr_pct):
    if position_atr_pct == 0:
        return False
    shift = abs(current_atr_pct - position_atr_pct) / position_atr_pct
    return shift > VOL_SHIFT_THRESHOLD
```

**Scenarios**:
- 波动率增大 30%+：当前范围太窄，出范围风险增加 → 放宽
- 波动率减小 30%+：当前范围太宽，资本效率浪费 → 收紧

### Trigger 3: Time Decay (priority: MAINTENANCE)

头寸持有超过最大时间，即使没有其他触发条件也进行维护性调仓。

```python
MAX_POSITION_AGE_H = 24  # hours

def check_time_decay(position):
    age_hours = (now() - position["created_at"]).total_seconds() / 3600
    return age_hours > MAX_POSITION_AGE_H
```

**Why?** 即使价格在范围内，长时间持有的头寸可能基于过时的波动率估计。定期刷新确保范围始终反映当前市场状况。

## Anti-Churn Gates

调仓有成本（gas + swap slippage + 短暂的零收益期），因此需要防止过度调仓：

```python
def should_rebalance(trigger, position, state, new_range, expected_fees):
    """Check all anti-churn conditions. Returns (should, reason)."""

    # Gate 1: Minimum position age
    age_seconds = (now() - position["created_at"]).total_seconds()
    if age_seconds < MIN_POSITION_AGE:  # 7200s = 2h
        if trigger != "out_of_range":  # out-of-range overrides age check
            return False, f"position_too_young ({age_seconds}s < {MIN_POSITION_AGE}s)"

    # Gate 2: Daily frequency limit
    recent_rebalances = count_rebalances_last_24h(state["rebalance_history"])
    if recent_rebalances >= MAX_REBALANCES_24H:  # 6
        return False, f"daily_limit ({recent_rebalances} >= {MAX_REBALANCES_24H})"

    # Gate 3: Gas cost ratio
    estimated_gas = estimate_rebalance_gas()
    if estimated_gas > expected_fees * GAS_TO_FEE_RATIO:  # 50%
        return False, f"gas_too_high ({estimated_gas:.2f} > {expected_fees * GAS_TO_FEE_RATIO:.2f})"

    # Gate 4: Minimum range change
    old_width = position["price_upper"] - position["price_lower"]
    new_width = new_range["price_upper"] - new_range["price_lower"]
    range_change = abs(new_width - old_width) / old_width
    if range_change < MIN_RANGE_CHANGE_PCT:  # 5%
        return False, f"range_change_too_small ({range_change:.1%} < {MIN_RANGE_CHANGE_PCT:.0%})"

    return True, trigger
```

**Priority override**: `out_of_range` 触发跳过 position age gate（因为出范围意味着零收益，等待更糟）。

## Capital Efficiency Formula

Uniswap V3 的核心优势是集中流动性带来的资本效率提升。

**Full-range LP** (V2-style): 流动性均匀分布在 (0, ∞)

**Concentrated LP** (V3): 流动性集中在 [p_lower, p_upper]

```
Capital Efficiency = sqrt(p_upper / p_lower) / (sqrt(p_upper / p_lower) - 1)

Simplified approximation (for narrow ranges):
Capital Efficiency ≈ current_price / range_width
```

**Capital Efficiency by Range Width**:

| Range Width | Capital Efficiency | Fee Multiplier vs V2 |
|---|---|---|
| 2% | ~50× | 50× more fees per $ |
| 5% | ~20× | 20× more fees per $ |
| 10% | ~10× | 10× more fees per $ |
| 20% | ~5× | 5× more fees per $ |
| 50% | ~2× | 2× more fees per $ |
| 100% (full range) | 1× | Same as V2 |

**Trade-off**: 更高的资本效率意味着更窄的范围，出范围的概率更高，调仓更频繁。波动率自适应算法的目标就是在这个 trade-off 中找到最优平衡点。

## Impermanent Loss (IL) Tracking

每次调仓时记录实现的无常损失：

```python
def calc_il(initial_price, final_price, amount0, amount1):
    """
    Calculate IL for a concentrated LP position.

    IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1

    where price_ratio = final_price / initial_price
    """
    ratio = final_price / initial_price
    il_pct = 2 * math.sqrt(ratio) / (1 + ratio) - 1
    return abs(il_pct) * 100  # as percentage

# IL reference table
# Price change | IL (full range) | IL (5% range) | IL (2% range)
# ±1%         | 0.00%           | ~0.01%        | ~0.02%
# ±5%         | 0.06%           | ~0.12%        | ~0.30%
# ±10%        | 0.23%           | ~0.46%        | ~1.15%
# ±20%        | 0.94%           | ~1.88%        | ~4.70%
# ±50%        | 5.72%           | N/A (out)     | N/A (out)
```

**Note**: 集中流动性的 IL 比全范围 LP 更大（相同价格变化下），因为流动性更集中。这就是为什么 `MAX_IL_TOLERANCE_PCT=5%` 作为硬停保护。

## Net Yield Calculation

```python
def calc_net_yield(stats):
    """
    Net Yield = Fees Claimed - Gas Spent - IL Realized

    Annualized = (Net Yield / Portfolio Value) * (365 / days_running) * 100
    """
    net = stats["total_fees_claimed_usd"] - stats["total_gas_spent_usd"]
    # IL is tracked per-rebalance in rebalance_history
    total_il = sum(r.get("il_realized_usd", 0) for r in state["rebalance_history"])
    net -= total_il

    days = (now() - stats["started_at"]).total_seconds() / 86400
    if days > 0 and stats["initial_portfolio_usd"] > 0:
        annualized = (net / stats["initial_portfolio_usd"]) * (365 / days) * 100
    else:
        annualized = 0

    return net, annualized
```

## Emergency Fallback

如果调仓过程中途失败（例如 remove 成功但 deposit 失败），资金处于裸露状态（不在任何 LP 头寸中，零收益）。

```python
EMERGENCY_WIDTH_MULT = 3.0

def emergency_deploy(price, atr, vol_class, tick_spacing):
    """Deploy at 3× normal width as safety net."""
    normal_mult = VOL_MULTIPLIERS[vol_class]
    emergency_half = atr * normal_mult * EMERGENCY_WIDTH_MULT
    lower = price - emergency_half
    upper = price + emergency_half
    tick_lower, tick_upper = calc_tick_range(lower, upper, tick_spacing)
    return tick_lower, tick_upper
```

**Why 3×?** 极宽范围几乎不会出范围，确保资金在下次正常调仓前持续产生（少量）手续费，而不是完全闲置。
