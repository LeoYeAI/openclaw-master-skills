# Gate CrossEx Futures Trading - Scenarios and Prompt Examples

Gate CrossEx USDT perpetual contract trading scenarios and expected behaviors.

## Workflow

### Step 1: Validate the futures contract and trading limits

Call `cex_crx_list_crx_rule_symbols` with:

- `symbols`: target futures symbol when the user provides a contract

Key data to extract:

- contract validity
- `min_quote_amount`
- contract size metadata
- quantity precision

### Step 2: Check balance and current position state

Call `cex_crx_list_crx_positions` with:

- `symbol`: target futures symbol when filtering is needed

Key data to extract:

- current position side
- current position size
- entry price
- liquidation price

### Step 3: Resolve leverage before order placement

Call `cex_crx_get_crx_positions_leverage` with:

- `symbols`: target futures symbol when leverage is symbol-specific

Key data to extract:

- current leverage
- leverage limit
- whether leverage must be updated

### Step 4: Submit the futures order after confirmation

Call `cex_crx_create_crx_order` with:

- `symbol`
- `side`
- `position_side`
- `type`
- `qty`
- `price` for limit orders

Key data to extract:

- order id
- submitted size
- immediate order status

### Step 5: Verify the resulting position

Call `cex_crx_list_crx_positions` with:

- `symbol`: the traded futures symbol

Key data to extract:

- updated size
- updated entry price
- liquidation price
- unrealized pnl

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Futures Operation Summary
- Symbol: {symbol}
- Side: {side}
- Position Side: {position_side}
- Size: {qty}
- Leverage: {leverage}
- Price: {price_or_market}
- Status: {status}
- Order ID: {order_id}
```

## API Call Parameters

### Trading Pair Format

```
{EXCHANGE}_FUTURE_{BASE}_{QUOTE}
```

**Examples**:

- `GATE_FUTURE_BTC_USDT` - Gate BTC/USDT futures
- `BINANCE_FUTURE_ETH_USDT` - Binance ETH/USDT futures
- `OKX_FUTURE_SOL_USDT` - OKX SOL/USDT futures

### Order Parameters

| Parameter       | Long                | Short               | Description                                   |
|-----------------|---------------------|---------------------|-----------------------------------------------|
| `side`          | `BUY`               | `SELL`              | Trade direction                               |
| `position_side` | `LONG` (required)   | `SHORT` (required)  | Position direction                            |
| `type`          | `MARKET` / `LIMIT`  | `MARKET` / `LIMIT`  | Order type                                    |
| `qty`           | **Required** (size) | **Required** (size) | Contract size                                 |
| `price`         | Optional            | Optional            | Limit order price (required for limit orders) |

### Data Sources

- **Trading Pair Info**: Call `cex_crx_list_crx_rule_symbols` → `min_quote_amount`, `amount_precision`,
  `quantity_precision`, `contract_size`
- **Account Balance**: Call `cex_crx_get_crx_account` → `available`
- **Futures Positions**: Call `cex_crx_list_crx_positions` → `size`, `leverage`, `entry_price`, `liquidation_price`
- **Leverage Multiplier**: Call `cex_crx_get_crx_positions_leverage` → Current leverage
- **Adjust Leverage**: Call `cex_crx_update_crx_positions_leverage` → Set new leverage
- **Place Order**: Call `cex_crx_create_crx_order`
- **Size Calculation**: `calc_future_qty_by_value(symbol, value)` → Calculate size by value

### Pre-checks

1. **Trading Pair Verification**: Call `cex_crx_list_crx_rule_symbols` to verify trading pair exists and is tradable
2. **Balance Check**: Check if sufficient USDT in `available_balance` (as margin)
3. **Leverage Check**: Query current leverage, adjust if user specifies
4. **Position Check**: Check existing positions to avoid direction conflicts
5. **Minimum Size Check**: Query `min_quote_amount` (typically 1 contract)
6. **Liquidation Price Calculation**: Estimate liquidation price and warn user

### Pre-order Confirmation

**Before placing order**, display **order summary**, only call order placement API after user confirmation.

- **Summary**: Trading pair, direction (long/short), size, leverage, estimated liquidation price, price (limit or "
  market"), exchange
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** (e.g., "confirm", "yes", "place order") execute the order

### Leverage Adjustment API

**Only adjust leverage when user explicitly specifies leverage.**

- **Query Current Leverage**: Call `cex_crx_get_crx_positions_leverage`
- **Set New Leverage**: Call `cex_crx_update_crx_positions_leverage`
    - Parameters: `symbol` (trading pair), `leverage` (leverage multiplier)

**⚠️ Note**:

- Adjusting leverage affects all positions in that trading pair
- Increasing leverage significantly increases liquidation risk
- Some trading pairs may have maximum leverage limits

### Error Handling

| Error Code                           | Handling                                                                     |
|--------------------------------------|------------------------------------------------------------------------------|
| `TRADE_FUTURE_INVALID_PZ_SIDE_ERROR` | ⚠️ Futures trading must specify `position_side` (LONG/SHORT)                 |
| `TRADE_INVALID_ORDER_QTY`            | ⚠️ Futures trading must use `qty` (size), supports calculating size by value |
| `TRADE_ORDER_AMOUNT_MIN_ERROR`       | Order size below minimum, increase size                                      |
| `BALANCE_NOT_ENOUGH`                 | Insufficient available margin, suggest reducing size or depositing           |
| `POSITION_NOT_EMPTY`                 | Prompt to close position before reversing direction                          |
| `INVALID_LEVERAGE`                   | Leverage multiplier out of range, adjust to valid range                      |
| `CALC_QTY_FAILED`                    | Size calculation failed, check price data                                    |

---

## Scenario 1: Futures Long (by Size)

**Context**: User wants to open long position with specified contract size.

**Prompt Examples**:

- "Open 1 BTC futures long position"
- "BTC perpetual long 1 contract"
- "Buy 1 BTC futures contract"

**Expected Behavior**:

1. Parse parameters: Trading pair `GATE_FUTURE_BTC_USDT`, direction `BUY`, position side `LONG`, size `1`
2. Check minimum size: Call `cex_crx_list_crx_rule_symbols` to query minimum size for this pair
3. Query current leverage: Call `cex_crx_get_crx_positions_leverage`
4. Display order summary (including estimated liquidation price) and require confirmation
5. Call `cex_crx_create_crx_order`, parameters `side="BUY"`, `type="MARKET"`, `qty="1"`, `position_side="LONG"`
6. Verify position and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_FUTURE_BTC_USDT
- Direction: Long (LONG)
- Size: 1 contract
- Leverage: 10x
- Type: Market
- Est. Liquidation Price: 45000 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456796
Trading Pair: GATE_FUTURE_BTC_USDT
Direction: Long (LONG)
Size: 1 contract
Entry Price: 50000 USDT
Leverage: 10x
Margin: 10 USDT
Liquidation Price: 45000 USDT
```

---

## Scenario 2: Futures Short (by USDT Value)

**Context**: User wants to open short position with specified USDT value.

**Prompt Examples**:

- "Open 100 USDT worth of SOL futures short"
- "SOL perpetual short 100 U"
- "Sell 100 USDT value of SOL futures"

**Expected Behavior**:

1. Parse parameters: Trading pair `GATE_FUTURE_SOL_USDT`, direction `SELL`, position side `SHORT`, value `100 USDT`
2. Query current leverage: Call `cex_crx_get_crx_positions_leverage`
3. Display order summary and require confirmation
4. Call `cex_crx_create_crx_order`, parameters `side="SELL"`, `type="MARKET"`, `qty="calculated size"`,
   `position_side="SHORT"`
5. Verify position and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_FUTURE_SOL_USDT
- Direction: Short (SHORT)
- Value: 100 USDT
- Size: 10 contracts (calculated)
- Leverage: 20x
- Type: Market
- Est. Liquidation Price: 120 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456797
Trading Pair: GATE_FUTURE_SOL_USDT
Direction: Short (SHORT)
Size: 10 contracts
Entry Price: 10.00 USDT
Leverage: 20x
Margin: 5 USDT
Liquidation Price: 12.00 USDT
```

---

## Scenario 3: Close Futures Long

**Context**: User wants to close long position.

**Prompt Examples**:

- "Close BTC futures long position"
- "Close long 1 BTC"
- "BTC futures sell to close long"

**Expected Behavior**:

1. Query current futures positions: Call `cex_crx_list_crx_positions`
2. Find corresponding long position
3. Display close plan and require confirmation
4. Call `cex_crx_create_crx_order`, parameters `side="SELL"`, `type="MARKET"`, `qty="close size"`,
   `position_side="LONG"`
5. Verify remaining position and output result

**Report Template**:

```
Close Plan:
- Trading Pair: GATE_FUTURE_BTC_USDT
- Current Position: 1 contract (long)
- Entry Price: 50000 USDT
- Close Size: 1 contract
- Est. PnL: +100 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Close successful.

Order ID: 123456798
Trading Pair: GATE_FUTURE_BTC_USDT
Close Size: 1 contract
Close Price: 50100 USDT
Realized PnL: +100 USDT
Remaining Position: Cleared
```

---

## Scenario 4: Adjust Futures Leverage

**Context**: User wants to change futures leverage multiplier.

**Prompt Examples**:

- "Set BTC futures leverage to 50x"
- "SOL futures leverage to 20x"
- "Adjust futures leverage to 100x"

**Expected Behavior**:

1. Parse parameters: Trading pair, leverage multiplier
2. Check current leverage
3. Display adjustment plan (including new liquidation price) and require confirmation
4. Call `cex_crx_update_crx_positions_leverage`, parameter `leverage="50"` (as required)
5. Verify leverage adjusted and output result

**Report Template**:

```
Leverage Adjustment Plan:
- Trading Pair: GATE_FUTURE_BTC_USDT
- Current Leverage: 10x
- Target Leverage: 50x
- Current Liquidation Price: 45000 USDT
- New Liquidation Price: 49000 USDT (closer to market)

⚠️ Increasing leverage significantly increases liquidation risk!

Reply 'confirm' to execute the above operation.

(After user confirmation)

Leverage adjusted.

Trading Pair: GATE_FUTURE_BTC_USDT
Leverage: 50x
Liquidation Price: 49000 USDT
Status: Effective
```
