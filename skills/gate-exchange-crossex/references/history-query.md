# Gate CrossEx History Query - Scenarios and Prompt Examples

Gate CrossEx history query scenarios, including order history, trade history, position history, interest history, and
account ledger.

## Workflow

### Step 1: Validate query type and time range

Call `cex_crx_list_crx_rule_symbols` with:

- `symbols`: target symbol when the user provides a pair that needs validation

Key data to extract:

- symbol validity
- whether the symbol filter can be applied
- normalized query scope

### Step 2: Query order and trade history when requested

Call `cex_crx_list_crx_history_orders` with:

- `symbol` when filtering by pair
- `from`
- `to`
- `page`
- `limit`

Key data to extract:

- order history rows
- order status
- timestamps
- pagination information

### Step 3: Query position and interest history when requested

Call `cex_crx_list_crx_history_positions` with:

- `symbol` when filtering by pair
- `from`
- `to`
- `page`
- `limit`

Key data to extract:

- position history rows
- realized pnl
- close time
- pagination information

### Step 4: Query ledger records when the user asks for account movements

Call `cex_crx_list_crx_account_book` with:

- `coin` when filtering by asset
- `from`
- `to`
- `page`
- `limit`

Key data to extract:

- ledger rows
- balance changes
- record types
- timestamps

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
History Query Summary
- Query Type: {query_type}
- Symbol: {symbol_or_all}
- Time Range: {time_range}
- Records Returned: {count}
- Page: {page}
```

## API Call Parameters

### Query Types

```
{QUERY_TYPE} : {SYMBOL} : {TIME_RANGE}
```

**Examples**:

- `ORDER_HISTORY` - Query all order history
- `TRADE_HISTORY` - Query all trade history
- `POSITION_HISTORY` - Query all position history
- `BTC_ORDER_HISTORY` - Query BTC order history
- `RECENT_3DAYS` - Query recent 3 days history

### Universal Query Parameters

| Parameter | Description                    | Default      |
|-----------|--------------------------------|--------------|
| `limit`   | Return quantity (max 100)      | 100          |
| `page`    | Page number (starting from 1)  | 1            |
| `from`    | Start timestamp (milliseconds) | 7 days ago   |
| `to`      | End timestamp (milliseconds)   | Current time |
| `symbol`  | Trading pair (optional)        | All          |

### Query Data Sources

| Query Type              | MCP TOOL                                    | Description              |
|-------------------------|---------------------------------------------|--------------------------|
| Order History           | `cex_crx_list_crx_history_orders`           | Historical order records |
| Trade History           | `cex_crx_list_crx_history_trades`           | Historical trade records |
| Position History        | `cex_crx_list_crx_history_positions`        | Futures position history |
| Margin Position History | `cex_crx_list_crx_history_margin_positions` | Margin position history  |
| Margin Interest History | `cex_crx_list_crx_history_margin_interests` | Margin interest records  |
| Account Ledger          | `cex_crx_list_crx_account_book`             | Account ledger records   |

### Response Field Descriptions

#### Order History Fields

- `order_id` - Order ID
- `symbol` - Trading pair
- `type` - Order type (MARKET/LIMIT)
- `side` - Trade direction (BUY/SELL)
- `qty` - Quantity
- `price` - Price
- `status` - Order status (OPEN/CANCELLED/FILLED)
- `create_time` - Create time
- `update_time` - Update time

#### Trade History Fields

- `order_id` - Order ID
- `symbol` - Trading pair
- `side` - Trade direction
- `fill_qty` - Filled quantity
- `fill_price` - Fill price
- `fee` - Fee
- `create_time` - Fill time

#### Position History Fields

- `symbol` - Trading pair
- `position_side` - Position side (LONG/SHORT)
- `close_size` - Close size
- `entry_price` - Entry price
- `close_price` - Close price
- `realised_pnl` - Realized PnL
- `close_time` - Close time

#### Margin Interest Fields

- `symbol` - Trading pair
- `currency` - Borrowed currency
- `size` - Borrowed quantity
- `rate` - Interest rate
- `interest` - Interest amount
- `time` - Interest time

#### Account Ledger Fields

- `time` - Time
- `type` - Type (trade/fee/transfer/deposit/withdraw)
- `symbol` - Trading pair
- `change` - Change amount
- `balance` - Balance after change
- `text` - Note description

### Pre-checks

1. **Time Range Verification**: Verify time range is reasonable (max 90 days)
2. **Parameter Verification**: Verify limit, page parameters are valid
3. **Trading Pair Verification**: Verify trading pair format is correct
4. **Permission Verification**: Verify query permission

### Paginated Query

**When there are many history records**, use paginated query.

- **Per Page Quantity**: Default 100 records (max 100)
- **Total Pages Calculation**: Total records / Per page quantity
- **Page Navigation**: Display "View Next Page" or "View Page N"

### Time Range Resolution

**Supports natural language time ranges**:

- "yesterday" → Yesterday 00:00:00 to 23:59:59
- "last 3 days" → 3 days ago to now
- "this week" → This Monday 00:00:00 to now
- "this month" → This month 1st 00:00:00 to now

### Statistics Information

**When querying history**, display statistics information.

- **Order Statistics**: Total orders, filled, cancelled, fill rate
- **Trade Statistics**: Total trades, total volume, total fees
- **PnL Statistics**: Total PnL, win rate, winning trades, losing trades
- **Ledger Statistics**: Total ledger records, total deposits, total withdrawals

### Error Handling

| Error Code            | Handling                                                 |
|-----------------------|----------------------------------------------------------|
| `INVALID_TIME_RANGE`  | Time range invalid, adjust query parameters              |
| `TIME_RANGE_TOO_LONG` | Time range exceeds limit, shorten query range            |
| `INVALID_PAGE`        | Page number invalid, adjust to valid range               |
| `INVALID_SYMBOL`      | Trading pair format incorrect, confirm format is correct |
| `NO_HISTORY`          | No history records, prompt user can start trading        |
| `QUERY_FAILED`        | Query failed, retry later                                |
| `RATE_LIMIT_EXCEEDED` | Query frequency too high, retry later                    |

---

## Scenario 1: Query Order History

**Context**: User wants to view historical order records.

**Prompt Examples**:

- "Query order history"
- "Show historical orders"
- "Past orders"
- "order history"

**Expected Behavior**:

1. Call `cex_crx_list_crx_history_orders` to query order history
2. Parameters: `limit` (max 100), `page`, `from` (start timestamp), `to` (end timestamp)
3. Display recent order records

**Report Template**:

```
Order History (Recent 10):

| Order ID | Trading Pair | Direction | Type | Quantity | Price | Status | Time |
|----------|--------------|-----------|------|----------|--------|--------|------|
| 123456788 | GATE_SPOT_BTC_USDT | Buy | Market | 0.0019 | 52631.58 | Filled | 10:25:10 |
| 123456787 | GATE_FUTURE_ETH_USDT | Long | Limit | 1 | 3000 | Cancelled | 10:20:05 |
| 123456786 | GATE_MARGIN_XRP_USDT | Short | Market | 50 | 1.02 | Filled | 10:15:30 |

Total: 3 records
Filled: 2, Cancelled: 1
Fill Rate: 66.7%
```

---

## Scenario 2: Query Trade History

**Context**: User wants to view historical trade records.

**Prompt Examples**:

- "Query trade history"
- "Show my trades"
- "Trade records"
- "trade history"

**Expected Behavior**:

1. Call `cex_crx_list_crx_history_trades` to query trade history
2. Display recent trade records

**Report Template**:

```
Trade History (Recent 10):

| Order ID | Trading Pair | Direction | Filled Qty | Fill Price | Fee | Time |
|----------|--------------|-----------|------------|------------|-----|------|
| 123456788 | GATE_SPOT_BTC_USDT | Buy | 0.0019 | 52631.58 | 0.1 | 10:25:10 |
| 123456786 | GATE_MARGIN_XRP_USDT | Short | 50 | 1.02 | 0.5 | 10:15:30 |
| 123456785 | GATE_FUTURE_ETH_USDT | Long | 1 | 3000 | 0.3 | 10:10:15 |

Total: 3 trades
Total Volume: 52.0019
Total Fees: 0.9
```

---

## Scenario 3: Query Position History

**Context**: User wants to view historical position records.

**Prompt Examples**:

- "Query position history"
- "Show closed positions"
- "Position records"

**Expected Behavior**:

1. Call `cex_crx_list_crx_history_positions` to query position history
2. Display recent position records

**Report Template**:

```
Position History (Recent 10):

| Trading Pair | Direction | Close Size | Entry Price | Close Price | Realized PnL | Close Time |
|--------------|-----------|------------|-------------|-------------|--------------|------------|
| GATE_FUTURE_BTC_USDT | Long | 1 | 50000 | 50100 | +100 USDT | 10:25:10 |
| GATE_MARGIN_XRP_USDT | Short | 50 | 1.00 | 0.98 | +10 USDT | 10:20:05 |
| GATE_FUTURE_ETH_USDT | Long | 10 | 3000 | 2950 | -500 USDT | 10:15:30 |

Total: 3 records
Total Realized PnL: -390 USDT
Win Rate: 66.7% (2 wins, 1 loss)
```

---

## Scenario 4: Query Margin Interest History

**Context**: User wants to view margin borrowing interest records.

**Prompt Examples**:

- "Query margin interest history"
- "Show interest records"
- "Borrowing costs"

**Expected Behavior**:

1. Call `cex_crx_list_crx_history_margin_interests` to query interest history
2. Display interest records

**Report Template**:

```
Margin Interest History (Recent 10):

| Trading Pair | Currency | Borrowed Qty | Rate | Interest | Time |
|--------------|----------|--------------|------|----------|------|
| GATE_MARGIN_BTC_USDT | USDT | 100 | 0.02%/day | 0.02 USDT | 10:25:10 |
| GATE_MARGIN_ETH_USDT | ETH | 2 | 0.015%/day | 0.0003 ETH | 10:20:05 |

Total Interest: 0.02 USDT, 0.0003 ETH
```

---

## Scenario 5: Query Account Ledger

**Context**: User wants to view account transaction records.

**Prompt Examples**:

- "Query account ledger"
- "Show account history"
- "Transaction records"

**Expected Behavior**:

1. Call `cex_crx_list_crx_account_book` to query account ledger
2. Display recent ledger records

**Report Template**:

```
Account Ledger (Recent 10):

| Time | Type | Trading Pair | Change | Balance | Note |
|------|------|--------------|--------|---------|------|
| 10:25:10 | Trade | GATE_SPOT_BTC_USDT | -100 USDT | 900 USDT | Buy 0.0019 BTC |
| 10:20:05 | Fee | GATE_FUTURE_ETH_USDT | -0.3 USDT | 1000 USDT | Trading fee |
| 10:15:30 | Transfer | - | +500 USDT | 1500 USDT | Deposit |

Total: 3 records
```

---

## Scenario 6: Query by Time Range

**Context**: User wants to query history for a specific time period.

**Prompt Examples**:

- "Query order history for last 3 days"
- "Show my trades from yesterday"
- "This week's position history"

**Expected Behavior**:

1. Parse time range (natural language or specific dates)
2. Convert to timestamps
3. Call corresponding query API with `from` and `to` parameters
4. Display records within time range

**Report Template**:

```
Order History (Last 3 Days):
Time Range: 2026-03-08 00:00:00 to 2026-03-11 23:59:59

| Order ID | Trading Pair | Direction | Quantity | Status | Time |
|----------|--------------|-----------|----------|--------|------|
| 123456788 | GATE_SPOT_BTC_USDT | Buy | 0.0019 | Filled | 10:25:10 |
| 123456787 | GATE_FUTURE_ETH_USDT | Long | 1 | Filled | 10:20:05 |

Total: 2 records (within time range)
```
