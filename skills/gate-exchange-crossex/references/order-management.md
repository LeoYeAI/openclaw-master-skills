# Gate CrossEx Order Management - Scenarios and Prompt Examples

Gate CrossEx order query, cancel, and amend scenarios.

## Workflow

### Step 1: Identify the target order set

Call `cex_crx_list_crx_open_orders` with:

- `symbol`: optional filter when the user provides a symbol
- `exchange_type`: optional filter when the user provides an exchange scope

Key data to extract:

- matching open orders
- order ids
- order side and type

### Step 2: Query a specific order before mutating it

Call `cex_crx_get_crx_order` with:

- `order_id`: the order to inspect

Key data to extract:

- current order status
- current price
- current quantity
- whether the order can be amended or cancelled

### Step 3: Cancel an order after confirmation

Call `cex_crx_cancel_crx_order` with:

- `order_id`: the order approved for cancellation

Key data to extract:

- cancelled order id
- cancellation status
- cancellation timestamp when available

### Step 4: Amend an order after confirmation

Call `cex_crx_update_crx_order` with:

- `order_id`
- `price` when updating price
- `qty` when updating quantity

Key data to extract:

- updated order id
- updated price
- updated quantity
- resulting order status

### Step 5: Verify historical records when the user asks for past orders

Call `cex_crx_list_crx_history_orders` with:

- `symbol` when filtering by pair
- `from`
- `to`
- `page`
- `limit`

Key data to extract:

- matching historical orders
- final status
- timestamps
- pagination information

## Report Template

Use the scenario-specific templates below. The minimum response should include:

```text
Order Management Summary
- Operation: {operation}
- Order ID: {order_id}
- Symbol: {symbol}
- Price: {price}
- Quantity: {qty}
- Status: {status}
```

## API Call Parameters

### Order Operation Types

```
{ACTION} : {ORDER_ID} / {SYMBOL}
```

**Examples**:

- `QUERY : 123456789` - Query order
- `CANCEL : 123456789` - Cancel single order
- `CANCEL_ALL : GATE_SPOT_BTC_USDT` - Cancel all orders for specific trading pair
- `MODIFY : 123456789` - Amend order

### Order Query Parameters

| Parameter  | Description                |
|------------|----------------------------|
| `order_id` | Order ID                   |
| `symbol`   | Trading pair (optional)    |
| `status`   | Order status (optional)    |
| `limit`    | Return quantity (optional) |

### Amend Order Parameters

| Parameter | Description                                    |
|-----------|------------------------------------------------|
| `price`   | New price (required when amending price)       |
| `qty`     | New quantity (required when amending quantity) |
| `amount`  | New amount (optional for spot buy)             |

### Data Sources

- **Order Query**: Call `cex_crx_get_crx_order` → Order details
- **Current Open Orders**: Call `cex_crx_list_crx_open_orders` → All open orders
- **Order History**: Call `cex_crx_list_crx_history_orders` → Historical orders
- **Cancel Order**: Call `cex_crx_cancel_crx_order` → Cancel result
- **Batch Cancel**: Query open orders with `cex_crx_list_crx_open_orders`, then cancel each order via
  `cex_crx_cancel_crx_order`
- **Amend Order**: Call `cex_crx_update_crx_order` → Amend result

### Pre-checks

1. **Order Existence**: Call `cex_crx_get_crx_order` to verify order exists
2. **Order Status**: Check if order can be cancelled or amended (only open orders can be operated)
3. **Permission Verification**: Verify order belongs to current user
4. **Amend Parameters**: Verify new price or new quantity comply with trading rules

### Pre-operation Confirmation

**Before operation**, display **operation summary**, only call operation API after user confirmation.

- **Cancel Summary**: Order ID, trading pair, direction, quantity, price
- **Amend Summary**: Order ID, current price/quantity, new price/quantity
- **Batch Cancel Summary**: List of all orders to be cancelled
- **Confirmation**: *"Reply 'confirm' to execute the above operation."*
- **Only after user confirmation** (e.g., "confirm", "yes", "cancel") execute operation

### Error Handling

| Error Code                | Handling                                                         |
|---------------------------|------------------------------------------------------------------|
| `ORDER_NOT_FOUND`         | Order doesn't exist or already cancelled, query order history    |
| `ORDER_ALREADY_FILLED`    | Order already filled, cannot cancel or amend                     |
| `ORDER_ALREADY_CANCELLED` | Order already cancelled, no need to operate again                |
| `INVALID_PRICE`           | New price doesn't comply with rules, check price precision       |
| `INVALID_QTY`             | New quantity doesn't comply with rules, check quantity precision |
| `ORDER_NOT_MODIFIABLE`    | Order type doesn't support amendment, cancel and re-place        |
| `CANCEL_FAILED`           | Cancel failed, retry later                                       |

---

## Scenario 1: Query All Open Orders

**Context**: User wants to view all current open orders.

**Prompt Examples**:

- "Query all open orders"
- "Show my orders"
- "What are my current open orders"
- "list orders"

**Expected Behavior**:

1. Call `cex_crx_list_crx_open_orders` to query all open orders
2. Display order list (including order ID, trading pair, direction, quantity, price)

**Report Template**:

```
Current Open Orders:

| Order ID | Trading Pair | Direction | Quantity | Price | Time |
|----------|--------------|-----------|----------|--------|------|
| 123456789 | GATE_SPOT_BTC_USDT | Buy | 0.001 | 50000 | 10:30:25 |
| 123456790 | GATE_FUTURE_ETH_USDT | Long | 1 | 3000 | 10:35:12 |
| 123456791 | GATE_MARGIN_XRP_USDT | Short | 10 | 1.00 | 11:02:45 |

Total: 3 open orders
```

---

## Scenario 2: Query Order Details

**Context**: User wants to view detailed information for a specific order.

**Prompt Examples**:

- "Query order 123456789"
- "Order details 123456789"
- "My order 123456789 status"

**Expected Behavior**:

1. Call `cex_crx_get_crx_order` to query order details
2. Display complete order information

**Report Template**:

```
Order Details:

Order ID: 123456789
Trading Pair: GATE_SPOT_BTC_USDT
Direction: Buy (BUY)
Type: Limit (GTC)
Quantity: 0.001 BTC
Price: 50000 USDT
Filled: 0 BTC
Remaining: 0.001 BTC
Status: Open
Create Time: 10:30:25
Update Time: 10:30:25
```

---

## Scenario 3: Cancel Single Order

**Context**: User wants to cancel a specific order.

**Prompt Examples**:

- "Cancel order 123456789"
- "Cancel that buy order"

**Expected Behavior**:

1. Parse order ID
2. Call `cex_crx_get_crx_order` to query order details
3. Display cancel plan and require confirmation
4. Call `cex_crx_cancel_crx_order` to cancel order
5. Verify order cancelled and output result

**Report Template**:

```
Cancel Plan:
- Order ID: 123456789
- Trading Pair: GATE_SPOT_BTC_USDT
- Direction: Buy (BUY)
- Quantity: 0.001 BTC
- Price: 50000 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order cancelled successfully.

Order ID: 123456789
Status: Cancelled
```

---

## Scenario 4: Amend Order

**Context**: User wants to modify order price or quantity.

**Prompt Examples**:

- "Amend order 123456789 price to 49500"
- "Change order quantity to 0.002"
- "Modify order price"

**Expected Behavior**:

1. Parse order ID and new parameters
2. Call `cex_crx_get_crx_order` to query current order details
3. Display amendment plan and require confirmation
4. Call `cex_crx_update_crx_order` to amend order
5. Verify order amended and output result

**Report Template**:

```
Amendment Plan:
- Order ID: 123456789
- Trading Pair: GATE_SPOT_BTC_USDT
- Current Price: 50000 USDT
- New Price: 49500 USDT

Reply 'confirm' to execute the above operation.

(After user confirmation)

Order amended successfully.

Order ID: 123456789
New Price: 49500 USDT
Status: Open
```

---

## Scenario 5: Query Order History

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
```
