# Gate CrossEx Margin Trading - Scenarios and Prompt Examples

Gate CrossEx margin trading scenarios and expected behaviors.

## Workflow

### Step 1: Validate symbol and leverage constraints

Call `cex_crx_list_crx_rule_symbols` with:

- `symbols`: target margin symbol when the user provides a specific pair

Key data to extract:

- symbol validity
- `min_quote_amount`
- quantity precision
- supported trading direction

### Step 2: Check balances, current positions, and leverage

Call `cex_crx_list_crx_margin_positions` with:

- `symbol`: target symbol when filtering is needed

Key data to extract:

- existing margin position side
- current position size
- entry price

### Step 3: Confirm leverage settings for the symbol

Call `cex_crx_get_crx_margin_positions_leverage` with:

- `symbols`: target symbol when leverage is symbol-specific

Key data to extract:

- current leverage
- leverage limits
- whether an update is needed

### Step 4: Submit the margin order after confirmation

Call `cex_crx_create_crx_order` with:

- `symbol`
- `side`
- `position_side`
- `type`
- `quote_qty` or `qty`
- `price` for limit orders

Key data to extract:

- order id
- submitted quantity or quote amount
- immediate order status

### Step 5: Verify the resulting margin position

Call `cex_crx_list_crx_margin_positions` with:

- `symbol`: the traded symbol

Key data to extract:

- updated position size
- updated leverage
- unrealized pnl
- position status

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Margin Operation Summary
- Symbol: {symbol}
- Side: {side}
- Position Side: {position_side}
- Type: {type}
- Quantity or Quote Amount: {size}
- Leverage: {leverage}
- Status: {status}
- Order ID: {order_id}
```

## API Call Parameters

### Trading Pair Format

```
{EXCHANGE}_MARGIN_{BASE}_{QUOTE}
```

**Examples**:

- `GATE_MARGIN_BTC_USDT` - Gate BTC/USDT margin
- `BINANCE_MARGIN_ETH_USDT` - Binance ETH/USDT margin
- `OKX_MARGIN_SOL_USDT` - OKX SOL/USDT margin

### Order Parameters

| Parameter       | Long                 | Short                | Description                                   |
|-----------------|----------------------|----------------------|-----------------------------------------------|
| `side`          | `BUY`                | `SELL`               | Trade direction                               |
| `position_side` | `LONG` (required)    | `SHORT` (required)   | Position direction                            |
| `type`          | `MARKET` / `LIMIT`   | `MARKET` / `LIMIT`   | Order type                                    |
| `quote_qty`     | Optional             | Optional             | USDT amount                                   |
| `qty`           | **Required** (limit) | **Required** (limit) | Coin quantity                                 |
| `price`         | Optional             | Optional             | Limit order price (required for limit orders) |

### Data Sources

- **Trading Pair Info**: Call `cex_crx_list_crx_rule_symbols` → `min_quote_amount`, `amount_precision`
- **Account Balance**: Call `cex_crx_get_crx_account` → `available_balance`
- **Margin Positions**: Call `cex_crx_list_crx_margin_positions` → `size`, `leverage`, `entry_price`
- **Margin Leverage**: Call `cex_crx_get_crx_margin_positions_leverage` → Current leverage
- **Adjust Leverage**: Call `cex_crx_update_crx_margin_positions_leverage` → Set new leverage
- **Place Order**: Call `cex_crx_create_crx_order`
- **Interest Rate Query**: Call `cex_crx_get_crx_interest_rate` → Interest rates for each coin

### Pre-checks

1. **Trading Pair Verification**: Call `cex_crx_list_crx_rule_symbols` to verify trading pair exists and is tradable
2. **Balance Check**:
    - Long: Check if sufficient USDT in `available` (as margin)
    - Short: Check if sufficient base coin in `available`
3. **Leverage Check**: Query current leverage, adjust if user specifies
4. **Position Check**: Check existing positions to avoid direction conflicts (cannot hold both long and short in same
   pair)
5. **Minimum Amount Check**: Query `min_quote_amount` (typically 3-5 USDT)

### Pre-order Confirmation

**Before placing order**, display **order summary**, only call order placement API after user confirmation.

- **Summary**: Trading pair, direction (long/short), quantity or amount, leverage, price (limit or "market"), exchange
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** (e.g., "confirm", "yes", "place order") execute the order

### Leverage Adjustment API

**Only adjust leverage when user explicitly specifies leverage.**

- **Query Current Leverage**: Call `cex_crx_get_crx_margin_positions_leverage`
- **Set New Leverage**: Call `cex_crx_update_crx_margin_positions_leverage`
    - Parameters: `symbol` (trading pair), `leverage` (leverage multiplier)

**⚠️ Note**:

- Adjusting leverage affects all positions in that trading pair
- Increasing leverage increases liquidation risk
- Some trading pairs may have maximum leverage limits

### Error Handling

| Error Code                           | Handling                                                               |
|--------------------------------------|------------------------------------------------------------------------|
| `TRADE_MARGIN_INVALID_PZ_SIDE_ERROR` | ⚠️ Margin trading must specify `position_side` (LONG/SHORT)            |
| `TRADE_INVALID_QUOTE_ORDER_QTY`      | ⚠️ Market buy must use `quote_qty` (USDT amount)                       |
| `TRADE_INVALID_ORDER_QTY`            | ⚠️ Limit orders must use `qty` (coin quantity) + `price`               |
| `TRADE_ORDER_AMOUNT_MIN_ERROR`       | Order amount below minimum notional value, increase quantity or amount |
| `BALANCE_NOT_ENOUGH`                 | Insufficient available margin, suggest reducing amount or depositing   |
| `POSITION_NOT_EMPTY`                 | Prompt to close position before reversing direction                    |
| `INVALID_LEVERAGE`                   | Leverage multiplier out of range, adjust to valid range                |

---

## Scenario 1: Margin Long (by USDT Amount)

**Context**: User wants to go long by borrowing USDT to buy cryptocurrency.

**Prompt Examples**:

- "Long 50 USDT worth of XRP on margin"
- "10x leverage long BTC 100 USDT"
- "XRP margin buy, amount 50 U"

**Expected Behavior**:

1. Parse parameters: Trading pair `GATE_MARGIN_XRP_USDT`, direction `BUY`, position side `LONG`, amount `50 USDT`
2. Check minimum amount: Call `cex_crx_list_crx_rule_symbols` to query minimum trading amount for this pair
3. Query current leverage, adjust if user specifies
4. Display order summary (including leverage) and require confirmation
5. Call `cex_crx_create_crx_order`, parameters `side="BUY"`, `type="MARKET"`, `quote_qty="50"`, `position_side="LONG"`
6. Verify position and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_MARGIN_XRP_USDT
- Direction: Long (LONG)
- Amount: 50 USDT
- Leverage: 10x
- Type: Market

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456792
Trading Pair: GATE_MARGIN_XRP_USDT
Direction: Long (LONG)
Quantity: 50 XRP
Entry Price: 1.00 USDT
Leverage: 10x
Margin: 5 USDT
```

---

## Scenario 2: Margin Short (by USDT Amount)

**Context**: User wants to short by borrowing coins to sell.

**Prompt Examples**:

- "Short 100 USDT worth of BTC on margin"
- "5x leverage short ETH 50 USDT"
- "BTC margin sell, amount 100 U"

**Expected Behavior**:

1. Parse parameters: Trading pair, direction `SELL`, position side `SHORT`, amount
2. Check minimum amount: Call `cex_crx_list_crx_rule_symbols` to query minimum trading amount for this pair
3. Query current leverage: Call `cex_crx_get_crx_margin_positions_leverage` to query current leverage
4. Display order summary and require confirmation
5. Call `cex_crx_create_crx_order`, parameters `side="SELL"`, `type="MARKET"`, `quote_qty="100"`,
   `position_side="SHORT"`
6. Verify position and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_MARGIN_BTC_USDT
- Direction: Short (SHORT)
- Amount: 100 USDT
- Leverage: 5x
- Type: Market

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456793
Trading Pair: GATE_MARGIN_BTC_USDT
Direction: Short (SHORT)
Quantity: 0.01 BTC
Entry Price: 50000 USDT
Leverage: 5x
Margin: 20 USDT
```

---

## Scenario 3: Close Long Position (Partial Close)

**Context**: User wants to close part of long position.

**Prompt Examples**:

- "Close 50% of XRP long position"
- "XRP margin sell 25 coins"
- "Close long XRP, quantity 25"

**Expected Behavior**:

1. Query current margin positions: Call `cex_crx_list_crx_margin_positions` to query current margin positions
2. Find corresponding long position
3. Calculate close quantity
4. Display close plan and require confirmation
5. Call `cex_crx_create_crx_order`, parameters `side="SELL"`, `type="MARKET"`, `qty="25"`, `position_side="LONG"`
6. Verify remaining position and output result

**Report Template**:

```
Close Plan:
- Trading Pair: GATE_MARGIN_XRP_USDT
- Current Position: 50 XRP (long)
- Close Quantity: 25 XRP (50%)
- Estimated PnL: +0.50 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Close successful.

Order ID: 123456794
Trading Pair: GATE_MARGIN_XRP_USDT
Close Quantity: 25 XRP
Close Price: 1.02 USDT
Realized PnL: +0.50 USDT
Remaining Position: 25 XRP (long)
```

---

## Scenario 4: Adjust Margin Leverage

**Context**: User wants to change margin leverage multiplier.

**Prompt Examples**:

- "Set BTC margin leverage to 20x"
- "XRP margin leverage to 5x"
- "Adjust leverage to 10x"

**Expected Behavior**:

1. Parse parameters: Trading pair, leverage multiplier
2. Check current leverage
3. Display adjustment plan and require confirmation
4. Call `cex_crx_update_crx_margin_positions_leverage`, parameter `leverage="20"`
5. Verify leverage adjusted and output result

**Report Template**:

```
Leverage Adjustment Plan:
- Trading Pair: GATE_MARGIN_BTC_USDT
- Current Leverage: 10x
- Target Leverage: 20x
- Maximum Leverage: 100x

⚠️ Increasing leverage increases liquidation risk.

Reply 'confirm' to execute the above operation.

(After user confirmation)

Leverage adjusted.

Trading Pair: GATE_MARGIN_BTC_USDT
Leverage: 20x
Status: Effective
```

---

## Scenario 5: Margin Interest Query

**Context**: User wants to query margin borrowing interest rates.

**Prompt Examples**:

- "Query BTC margin interest"
- "Borrowing interest rate"
- "Margin interest"

**Expected Behavior**:

1. Call `cex_crx_get_crx_interest_rate` to query interest rates for each coin
2. Display current rates and calculation examples

**Report Template**:

```
Margin Borrowing Interest Rates:

| Coin | Daily Rate | APR |
|------|-----------|-----|
| BTC | 0.010% | 3.65% |
| ETH | 0.015% | 5.48% |
| USDT | 0.020% | 7.30% |

Interest Calculation Examples:
- Borrow 100 USDT, daily interest: 0.02 USDT
- Borrow 1 BTC, daily interest: 0.0001 BTC

⚠️ Interest is settled hourly, unpaid positions continue to accrue interest.
```
