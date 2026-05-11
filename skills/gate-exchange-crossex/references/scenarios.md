# Gate CrossEx Trading Suite - Scenarios & Prompt Examples

## Scenario 1: Spot Trading Request

**Context**: User wants to place a spot buy or sell order on a supported exchange through Gate CrossEx.

**Prompt Examples**:

- "Buy 100 USDT worth of BTC"
- "Sell 0.5 ETH spot"
- "Place a market buy for SOL on Gate"

**Expected Behavior**:

1. Identify the intent as spot trading and route to `references/spot-trading.md`.
2. Extract trading pair, exchange, side, order type, and quantity or quote amount.
3. Check symbol validity, minimum amount, and available balance before submission.
4. Present an order summary and require explicit user confirmation.
5. Submit the order only after confirmation and return the final order status.

## Scenario 2: Margin Trading Request

**Context**: User wants to open, close, or adjust a margin long or short position.

**Prompt Examples**:

- "Long 50 USDT worth of XRP on margin"
- "Short BTC with 5x leverage"
- "Close part of my ETH margin long"

**Expected Behavior**:

1. Identify the intent as margin trading and route to `references/margin-trading.md`.
2. Extract trading pair, exchange, side, position side, leverage, and quantity or amount.
3. Check margin balance, current position state, leverage setting, and minimum trade amount.
4. Present a margin order summary with leverage and require explicit user confirmation.
5. Submit or adjust the margin action only after confirmation and report the resulting position or order state.

## Scenario 3: Futures Trading Request

**Context**: User wants to trade USDT perpetual futures, including opening, closing, or adjusting leverage.

**Prompt Examples**:

- "Open 1 BTC futures long position"
- "Short 100 USDT worth of SOL perpetuals"
- "Set my ETH futures leverage to 20x"

**Expected Behavior**:

1. Identify the intent as futures trading and route to `references/futures-trading.md`.
2. Extract contract symbol, exchange, direction, position side, size or value, and leverage.
3. Check contract validity, minimum size, available margin, and current leverage or position state.
4. Present a futures summary including size, leverage, and key risk information, then require explicit confirmation.
5. Execute the futures action only after confirmation and return the resulting order or position details.

## Scenario 4: Cross-Exchange Transfer Request

**Context**: User wants to move funds between exchanges within Gate CrossEx.

**Prompt Examples**:

- "Transfer 100 USDT from Gate to Binance"
- "Move ETH from OKX to Gate"
- "Transfer 50 USDT to OKX"

**Expected Behavior**:

1. Identify the intent as cross-exchange transfer and route to `references/transfer.md`.
2. Extract source exchange, target exchange, asset, and amount.
3. Check supported assets, available balance, and transfer constraints.
4. Present a transfer summary and require explicit user confirmation.
5. Execute the transfer only after confirmation and return the final result or history record.

## Scenario 5: Convert Trading Request

**Context**: User wants to perform a flash convert within Gate CrossEx.

**Prompt Examples**:

- "Convert 10 USDT to BTC on Gate"
- "Flash convert 50 USDT to ETH"
- "Quote convert SOL to BTC"

**Expected Behavior**:

1. Identify the intent as convert trading and route to `references/convert-trading.md`.
2. Extract source coin, target coin, source amount, and exchange type.
3. Request a convert quote and validate available balance before execution.
4. Present a convert summary with quoted rate and expected receive amount, then require explicit user confirmation.
5. Execute the convert only after confirmation and return the final result.

## Scenario 6: Order Management Request

**Context**: User wants to query, cancel, or amend an existing order.

**Prompt Examples**:

- "Show all my open orders"
- "Cancel order 123456"
- "Amend my BTC order price to 50000"

**Expected Behavior**:

1. Identify the intent as order management and route to `references/order-management.md`.
2. Extract operation type, order ID, symbol, status filter, or amendment parameters.
3. Check whether the target order exists and whether its current status allows the requested action.
4. Present the relevant order details or action summary, requiring confirmation for cancel or amend operations.
5. Execute the cancel or amend action only after confirmation, or return the queried order data directly when no
   confirmation is required.

## Scenario 7: Position Query Request

**Context**: User wants to view current positions, filtered positions, or position-related risk information.

**Prompt Examples**:

- "Show all my positions"
- "Query my futures positions"
- "Do I have any margin positions open?"

**Expected Behavior**:

1. Identify the intent as position query and route to `references/position-query.md`.
2. Extract position type, exchange, symbol, and any filtering scope.
3. Query the relevant current position data, leverage, or risk-related fields.
4. Format the result clearly, highlighting symbol, direction, size, entry price, and unrealized PnL when available.
5. Return the requested position summary and surface any notable risk warnings if relevant.

## Scenario 8: History Query Request

**Context**: User wants to query historical orders, trades, positions, ledger entries, or interest records.

**Prompt Examples**:

- "Show my trade history"
- "Query BTC order history for the last 7 days"
- "Check my margin interest history"

**Expected Behavior**:

1. Identify the intent as history query and route to `references/history-query.md`.
2. Extract history type, symbol, exchange, time range, pagination inputs, and any filters.
3. Validate the requested time range and determine the appropriate history endpoint.
4. Query the historical records and organize them in reverse chronological order.
5. Return a concise history summary with key fields such as time, symbol, side, size, price, and status where
   applicable.
