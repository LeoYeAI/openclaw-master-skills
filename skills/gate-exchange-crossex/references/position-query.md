# Gate CrossEx Position Query - Scenarios and Prompt Examples

Gate CrossEx position query scenarios, including current positions and history records.

## Workflow

### Step 1: Resolve the requested position scope

Call `cex_crx_get_crx_account` with:

- no required parameters for the default account overview

Key data to extract:

- total equity
- available balance
- unrealized pnl summary

### Step 2: Query futures positions when the request includes futures scope

Call `cex_crx_list_crx_positions` with:

- `symbol`: optional symbol filter
- `exchange_type`: optional exchange filter

Key data to extract:

- futures position size
- entry price
- leverage
- liquidation price

### Step 3: Query margin positions when the request includes margin scope

Call `cex_crx_list_crx_margin_positions` with:

- `symbol`: optional symbol filter
- `exchange_type`: optional exchange filter

Key data to extract:

- margin position size
- entry price
- leverage
- unrealized pnl

### Step 4: Query historical position records when the user asks for history

Call `cex_crx_list_crx_history_positions` with:

- `symbol` when filtering by pair
- `from`
- `to`
- `page`
- `limit`

Key data to extract:

- closed positions
- realized pnl
- close time
- pagination information

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Position Query Summary
- Scope: {scope}
- Symbol: {symbol_or_all}
- Size: {size}
- Entry Price: {entry_price}
- Leverage: {leverage}
- PnL: {pnl}
```

## API Call Parameters

### Query Types

```
{QUERY_TYPE} : {SYMBOL} / {POSITION_ID}
```

**Examples**:

- `ALL_POSITIONS` - Query all positions
- `FUTURE_POSITIONS` - Query futures positions
- `MARGIN_POSITIONS` - Query margin positions
- `BTC_POSITIONS` - Query BTC-related positions
- `HISTORY_POSITIONS` - Query position history

### Query Parameters

| Parameter       | Description                                   |
|-----------------|-----------------------------------------------|
| `symbol`        | Trading pair (optional)                       |
| `position_side` | Position side (LONG/SHORT, optional)          |
| `limit`         | Return quantity (optional)                    |
| `from`          | Start timestamp (optional, for history query) |
| `to`            | End timestamp (optional, for history query)   |

### Data Sources

- **Futures Positions**: Call `cex_crx_list_crx_positions` → Futures position list
- **Margin Positions**: Call `cex_crx_list_crx_margin_positions` → Margin position list
- **Account Assets**: Call `cex_crx_get_crx_account` → Asset overview
- **Position History**: Call `cex_crx_list_crx_history_positions` → Historical position records
- **Trade History**: Call `cex_crx_list_crx_history_trades` → Historical trade records
- **Margin Interest**: Call `cex_crx_list_crx_history_margin_interests` → Interest history
- **Account Ledger**: Call `cex_crx_list_crx_account_book` → Account ledger records

### Query Response Fields

#### Futures Position Fields

- `size` - Position size (positive for long, negative for short)
- `leverage` - Leverage multiplier
- `entry_price` - Entry price
- `mark_price` - Mark price
- `liquidation_price` - Liquidation price
- `unrealised_pnl` - Unrealized PnL

#### Margin Position Fields

- `size` - Position quantity
- `leverage` - Leverage multiplier
- `entry_price` - Entry price
- `mark_price` - Mark price
- `unrealised_pnl` - Unrealized PnL
- `margin` - Margin

#### Account Asset Fields

- `total` - Total equity
- `available` - Available balance
- `locked` - Locked balance
- `unrealised_pnl` - Unrealized PnL

### Pre-checks

1. **Connection Check**: Verify API connection is normal
2. **Permission Verification**: Verify query permission
3. **Parameter Verification**: Verify trading pair format is correct
4. **Time Range**: Verify history query time range is reasonable

### Risk Warning

**When querying positions**, if risk level ≥ 80%, display risk warning.

- **Risk Level Calculation**: Position margin / total equity
- **Warning Thresholds**: 80% (high risk), 90% (extreme risk)
- **Suggested Actions**: Reduce leverage, add margin, partial close

### Error Handling

| Error Code            | Handling                                                                  |
|-----------------------|---------------------------------------------------------------------------|
| `INVALID_SYMBOL`      | Trading pair format incorrect or doesn't exist, confirm format is correct |
| `QUERY_FAILED`        | Query failed, retry later                                                 |
| `NO_POSITIONS`        | No positions, prompt user can start trading                               |
| `TIME_RANGE_INVALID`  | Time range invalid, adjust query parameters                               |
| `RATE_LIMIT_EXCEEDED` | Query frequency too high, retry later                                     |

---

## Scenario 1: Query All Positions

**Context**: User wants to view all types of positions.

**Prompt Examples**:

- "Query all my positions"
- "Show my positions"
- "What are my current positions"
- "positions"

**Expected Behavior**:

1. Call `cex_crx_list_crx_positions` to query futures positions
2. Call `cex_crx_list_crx_margin_positions` to query margin positions
3. Display all positions uniformly

**Report Template**:

```
Current All Positions:

**Futures Positions:**

| Trading Pair | Direction | Size | Entry Price | Mark Price | Unrealized PnL | Leverage |
|--------------|-----------|------|-------------|------------|----------------|----------|
| GATE_FUTURE_BTC_USDT | Long | 1 | 50000 | 50100 | +100 USDT | 10x |
| GATE_FUTURE_SOL_USDT | Short | -10 | 10.00 | 9.95 | +50 USDT | 20x |

**Margin Positions:**

| Trading Pair | Direction | Quantity | Entry Price | Mark Price | Unrealized PnL | Leverage |
|--------------|-----------|----------|-------------|------------|----------------|----------|
| GATE_MARGIN_XRP_USDT | Long | 50 | 1.00 | 1.02 | +10 USDT | 10x |

Futures Positions: 2
Margin Positions: 1
Total Unrealized PnL: +160 USDT
```

---

## Scenario 2: Query Futures Positions

**Context**: User only wants to view futures positions.

**Prompt Examples**:

- "Query futures positions"
- "Show my futures holdings"
- "futures positions"

**Expected Behavior**:

1. Call `cex_crx_list_crx_positions` to query futures positions
2. Filter and display contracts with positions

**Report Template**:

```
Futures Positions:

| Trading Pair | Direction | Size | Entry Price | Mark Price | Liquidation Price | Unrealized PnL | Leverage |
|--------------|-----------|------|-------------|------------|-------------------|----------------|----------|
| GATE_FUTURE_BTC_USDT | Long | 1 | 50000 | 50100 | 45000 | +100 USDT | 10x |
| GATE_FUTURE_SOL_USDT | Short | -10 | 10.00 | 9.95 | 12.00 | +50 USDT | 20x |

Total Futures Positions: 2
Total Unrealized PnL: +150 USDT
```

---

## Scenario 3: Query Margin Positions

**Context**: User only wants to view margin positions.

**Prompt Examples**:

- "Query margin positions"
- "Show my margin holdings"
- "margin positions"

**Expected Behavior**:

1. Call `cex_crx_list_crx_margin_positions` to query margin positions
2. Filter and display pairs with positions

**Report Template**:

```
Margin Positions:

| Trading Pair | Direction | Quantity | Entry Price | Mark Price | Unrealized PnL | Leverage | Margin |
|--------------|-----------|----------|-------------|------------|----------------|----------|---------|
| GATE_MARGIN_XRP_USDT | Long | 50 | 1.00 | 1.02 | +10 USDT | 10x | 5 USDT |
| GATE_MARGIN_ETH_USDT | Short | 2 | 3000 | 2990 | -20 USDT | 5x | 20 USDT |

Total Margin Positions: 2
Total Unrealized PnL: -10 USDT
```

---

## Scenario 4: Query Position History

**Context**: User wants to view historical position records.

**Prompt Examples**:

- "Query position history"
- "Show historical positions"
- "position history"

**Expected Behavior**:

1. Call `cex_crx_list_crx_history_positions` to query position history
2. Parameters: `limit`, `page`, `from`, `to`
3. Display recent position records

**Report Template**:

```
Position History (Recent 10):

| Trading Pair | Direction | Size | Entry Price | Close Price | Realized PnL | Close Time |
|--------------|-----------|------|-------------|-------------|--------------|------------|
| GATE_FUTURE_BTC_USDT | Long | 1 | 50000 | 50100 | +100 USDT | 10:25:10 |
| GATE_MARGIN_XRP_USDT | Short | 50 | 1.00 | 0.98 | +10 USDT | 10:20:05 |
| GATE_FUTURE_ETH_USDT | Long | 10 | 3000 | 2950 | -500 USDT | 10:15:30 |

Total: 3 records
Total Realized PnL: -390 USDT
```

---

## Scenario 5: Risk Warning

**Context**: User's position risk level is high.

**Prompt Examples**:

- "Query my positions" (when risk level ≥ 80%)

**Expected Behavior**:

1. Query positions
2. Calculate risk level
3. Display risk warning if risk level ≥ 80%

**Report Template**:

```
Current Positions:

| Trading Pair | Direction | Size | Unrealized PnL | Margin | Risk Level |
|--------------|-----------|------|----------------|---------|-------------|
| GATE_FUTURE_BTC_USDT | Long | 10 | -5000 USDT | 500 USDT | 85% |

⚠️ HIGH RISK WARNING!

Your position risk level is 85%, which is above the safe threshold.

Suggested Actions:
1. Reduce position size
2. Add more margin
3. Close part of position
4. Reduce leverage

Please consider reducing your risk to avoid liquidation.
```
