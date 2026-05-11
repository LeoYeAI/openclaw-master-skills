# Gate CrossEx Spot Trading - Scenarios and Prompt Examples

Gate CrossEx spot trading scenarios and expected behaviors.

## Workflow

### Step 1: Validate trading pair and order constraints

Call `cex_crx_list_crx_rule_symbols` with:

- `symbols`: target spot symbol when the user provides a specific pair

Key data to extract:

- symbol validity
- `min_quote_amount`
- amount precision
- quantity precision

### Step 2: Check account balance before submission

Call `cex_crx_get_crx_account` with:

- no required parameters for the default account overview

Key data to extract:

- available quote balance for buy orders
- available base balance for sell orders
- account status needed for the order

### Step 3: Create the order after explicit confirmation

Call `cex_crx_create_crx_order` with:

- `symbol`
- `side`
- `type`
- `quote_qty` for market buys or `qty` for sells and limit orders
- `price` for limit orders

Key data to extract:

- order id
- submitted size or quote amount
- order status

### Step 4: Verify the final order result

Call `cex_crx_get_crx_order` with:

- `order_id`: the order returned by the create step

Key data to extract:

- final order status
- filled quantity
- average fill price
- remaining quantity

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Spot Order Summary
- Symbol: {symbol}
- Side: {side}
- Type: {type}
- Quantity or Quote Amount: {size}
- Price: {price_or_market}
- Status: {status}
- Order ID: {order_id}
```

## API Call Parameters

### Trading Pair Format

```
{EXCHANGE}_SPOT_{BASE}_{QUOTE}
```

**Examples**:

- `GATE_SPOT_BTC_USDT` - Gate BTC/USDT spot
- `BINANCE_SPOT_ETH_USDT` - Binance ETH/USDT spot
- `OKX_SPOT_SOL_USDT` - OKX SOL/USDT spot

### Order Parameters

| Parameter   | Buy                   | Sell               | Description                                   |
|-------------|-----------------------|--------------------|-----------------------------------------------|
| `side`      | `BUY`                 | `SELL`             | Trade direction                               |
| `type`      | `MARKET` / `LIMIT`    | `MARKET` / `LIMIT` | Order type                                    |
| `quote_qty` | **Required** (market) | Optional           | USDT amount (market buy only)                 |
| `qty`       | **Required** (limit)  | **Required**       | Coin quantity                                 |
| `price`     | Optional              | Optional           | Limit order price (required for limit orders) |

### Data Sources

- **Trading Pair Info**: Call `cex_crx_list_crx_rule_symbols` → `min_quote_amount`, `amount_precision`,
  `quantity_precision`
- **Account Balance**: Call `cex_crx_get_crx_account` → `available_balance`
- **Place Order**: Call `cex_crx_create_crx_order`
- **Order Query**: Call `cex_crx_get_crx_order`
- **Current Open Orders**: Call `cex_crx_list_crx_open_orders`

### Pre-checks

1. **Trading Pair Verification**: Call `cex_crx_list_crx_rule_symbols` to verify trading pair exists and is tradable
2. **Balance Check**:
    - Buy: Check if sufficient USDT in `available`
    - Sell: Check if sufficient base coin in `available`
3. **Minimum Amount Check**: Query `min_quote_amount` (typically 3-5 USDT)
4. **Exchange Status**: Verify target exchange is operating normally

### Pre-order Confirmation

**Before placing order**, display **order summary**, only call order placement API after user confirmation.

- **Summary**: Trading pair, direction (buy/sell), quantity or amount, price (limit or "market"), exchange
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** (e.g., "confirm", "yes", "place order") execute the order

### Error Handling

| Error Code                      | Handling                                                                  |
|---------------------------------|---------------------------------------------------------------------------|
| `TRADE_INVALID_QUOTE_ORDER_QTY` | ⚠️ Market buy must use `quote_qty` (USDT amount)                          |
| `TRADE_INVALID_ORDER_QTY`       | ⚠️ Limit orders must use `qty` (coin quantity) + `price`                  |
| `TRADE_ORDER_AMOUNT_MIN_ERROR`  | Order amount below minimum notional value, increase quantity or amount    |
| `BALANCE_NOT_ENOUGH`            | Insufficient available balance, suggest reducing amount or depositing     |
| `SYMBOL_NOT_FOUND`              | Trading pair format incorrect or doesn't exist, confirm format is correct |

---

## Scenario 1: Market Buy (by USDT Amount)

**Context**: User wants to buy cryptocurrency with specified USDT amount.

**Prompt Examples**:

- "Buy 100 USDT worth of BTC"
- "Market buy 50 USDT worth of ETH"
- "Spot buy 10 U of XRP"

**Expected Behavior**:

1. Parse parameters: Trading pair `GATE_SPOT_BTC_USDT`, direction `BUY`, amount `100 USDT`
2. Check minimum amount: Call `cex_crx_list_crx_rule_symbols` to query minimum trading amount for this pair
3. Display order summary and require confirmation
4. Call `cex_crx_create_crx_order`, parameters `side="BUY"`, `type="MARKET"`, `quote_qty="100"`
5. Verify order and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_SPOT_BTC_USDT
- Direction: Buy (BUY)
- Amount: 100 USDT
- Type: Market

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456789
Trading Pair: GATE_SPOT_BTC_USDT
Direction: Buy (BUY)
Amount: 100 USDT
Status: Filled
```

---

## Scenario 2: Market Sell (by Coin Quantity)

**Context**: User wants to sell specified quantity of cryptocurrency.

**Prompt Examples**:

- "Sell 0.5 BTC"
- "Market sell 10 ETH"
- "Spot sell 100 XRP"

**Expected Behavior**:

1. Parse parameters: Trading pair `GATE_SPOT_BTC_USDT`, direction `SELL`, quantity `0.5 BTC`
2. Check if balance is sufficient
3. Check minimum notional value: Call `cex_crx_list_crx_rule_symbols` to query minimum trading amount for this pair
4. Display order summary and require confirmation
5. Call `cex_crx_create_crx_order`, parameters `side="SELL"`, `type="MARKET"`, `qty="0.5"`
6. Verify order and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_SPOT_BTC_USDT
- Direction: Sell (SELL)
- Quantity: 0.5 BTC
- Type: Market

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456790
Trading Pair: GATE_SPOT_BTC_USDT
Direction: Sell (SELL)
Quantity: 0.5 BTC
Status: Filled
```

---

## Scenario 3: Limit Buy

**Context**: User wants to buy cryptocurrency at or below a specified price.

**Prompt Examples**:

- "Limit buy 0.001 BTC at 50000"
- "BTC limit buy at 49000 for 100 USDT"
- "ETH limit buy, price 3000, amount 50 USDT"

**Expected Behavior**:

1. Parse parameters: Trading pair, price, quantity
2. Check if price is reasonable (not too far from market price)
3. Display order summary (including limit price) and require confirmation
4. Call `cex_crx_create_crx_order`, parameters `side="BUY"`, `type="LIMIT"`, `price="50000"`, `qty="0.002"`
5. Verify order and output result

**Report Template**:

```
Order Summary:
- Trading Pair: GATE_SPOT_BTC_USDT
- Direction: Buy (BUY)
- Price: 50000 USDT (limit)
- Quantity: 0.002 BTC
- Type: Limit (LIMIT)

⚠️ Note: Limit orders must use quantity (qty) not amount (quote_qty)

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order submitted.

Order ID: 123456791
Trading Pair: GATE_SPOT_BTC_USDT
Direction: Buy (BUY)
Price: 50000 USDT
Amount: 100 USDT
Status: Open
```

---

## Scenario 4: Cross-Exchange Arbitrage

**Context**: User wants to arbitrage price differences across exchanges.

**Prompt Examples**:

- "Buy 100 USDT worth of BTC on Gate, sell on Binance"
- "Arbitrage: buy ETH at low price on Gate, sell at high price on OKX"
- "Cross-exchange arbitrage BTC"

**Expected Behavior**:

1. Identify arbitrage opportunity: Exchange A (buy low), Exchange B (sell high)
2. Query prices on both exchanges
3. Calculate spread and profit (after fees)
4. Display arbitrage plan and require confirmation
5. Place orders on both exchanges (note: actual arbitrage requires simultaneous execution)
6. Verify orders and output results

**Report Template**:

```
Arbitrage Opportunity Analysis:
- Trading Pair: BTC_USDT
- Gate Price: 50000 USDT
- Binance Price: 50100 USDT
- Spread: 100 USDT (0.20%)
- Estimated Profit: 80 USDT (after fees)

Arbitrage Plan:
1. Gate buy 0.002 BTC @ 50000 = 100 USDT
2. Binance sell 0.002 BTC @ 50100 = 100.20 USDT
3. Net Profit: 0.20 USDT

⚠️ Risk Warning: Arbitrage requires simultaneous execution, prices may change rapidly.

Reply 'confirm' to execute the above operation.
```

---

## Scenario 5: Insufficient Balance Error

**Context**: User wants to buy more than account balance.

**Prompt Examples**:

- "Buy 10000 USDT worth of BTC" (account only has 1000 USDT)

**Expected Behavior**:

1. Query account balance: Call `cex_crx_get_crx_account`
2. Detect insufficient balance
3. Display available balance and suggestions

**Report Template**:

```
Order Failed: Insufficient Balance.

Trading Pair: GATE_SPOT_BTC_USDT
Required Amount: 10000 USDT
Available Balance: 1000 USDT
Shortfall: 9000 USDT

Suggestions:
1. Reduce buy amount to below 1000 USDT
2. Deposit to account
3. Check other trading pairs
```

---

## Scenario 6: Amount Below Minimum

**Context**: User wants to buy below exchange minimum.

**Prompt Examples**:

- "Buy 3 USDT worth of BTC" (Gate minimum is 4 USDT)

**Expected Behavior**:

1. Detect amount below minimum
2. Display minimum amount requirements for each exchange
3. Suggest adjusting amount

**Report Template**:

```
Order Failed: Amount Below Minimum.

Trading Pair: GATE_SPOT_BTC_USDT
Your Amount: 3 USDT

Suggestion: Call `cex_crx_list_crx_rule_symbols` to query the minimum trading amount for this pair, then adjust the order amount.
```

---

## Scenario 7: Query Order Status

**Context**: User wants to check execution status of submitted order.

**Prompt Examples**:

- "Query order 123456789"
- "My order status"
- "Order details 123456789"

**Expected Behavior**:

1. Call `cex_crx_get_crx_order` to query order details
2. Display order status and execution information

**Report Template**:

```
Order Details:

Order ID: 123456789
Trading Pair: GATE_SPOT_BTC_USDT
Direction: Buy (BUY)
Type: Market
Status: Filled
Filled Quantity: 0.0019 BTC
Avg Fill Price: 52631.58 USDT
Filled Amount: 100 USDT
Fee: 0.1 USDT
Time: 10:30:25
```
