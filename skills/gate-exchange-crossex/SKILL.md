---
name: gate-exchange-crossex
version: "2026.3.23-1"
updated: "2026-03-23"
description: 'Use this skill for Gate CrossEx cross-exchange operations: order placement, transfer, convert, and order/position/history queries across Gate, Binance, OKX and Bybit. Trigger phrases include "buy spot", "transfer", "convert", "query positions", "order history".'
---

# Gate CrossEx Trading Suite

This skill is the unified entry point for Gate CrossEx cross-exchange trading. It supports lots of **core operations**:
order management, position query, and history query. User intents are routed to corresponding workflows.

## General Rules

⚠️ STOP — You MUST read and strictly follow the shared runtime rules before proceeding.
Do NOT select or call any tool until all rules are read. These rules have the highest priority.
→ Read [gate-runtime-rules.md](https://github.com/gate/gate-skills/blob/master/skills/gate-runtime-rules.md)
- **Only call MCP tools explicitly listed in this skill.** Tools not documented here must NOT be called, even if they
  exist in the MCP server.


---

## MCP Dependencies

### Required MCP Servers
| MCP Server | Status |
|------------|--------|
| Gate (main) | ✅ Required |

### MCP Tools Used

**Query Operations (Read-only)**

- cex_crx_get_crx_account
- cex_crx_get_crx_fee
- cex_crx_get_crx_interest_rate
- cex_crx_get_crx_margin_positions_leverage
- cex_crx_get_crx_order
- cex_crx_get_crx_positions_leverage
- cex_crx_list_crx_account_book
- cex_crx_list_crx_adl_rank
- cex_crx_list_crx_coin_discount_rate
- cex_crx_list_crx_history_margin_interests
- cex_crx_list_crx_history_margin_positions
- cex_crx_list_crx_history_orders
- cex_crx_list_crx_history_positions
- cex_crx_list_crx_history_trades
- cex_crx_list_crx_margin_positions
- cex_crx_list_crx_open_orders
- cex_crx_list_crx_positions
- cex_crx_list_crx_rule_risk_limits
- cex_crx_list_crx_rule_symbols
- cex_crx_list_crx_transfer_coins
- cex_crx_list_crx_transfers

**Execution Operations (Write)**

- cex_crx_cancel_crx_order
- cex_crx_close_crx_position
- cex_crx_create_crx_convert_order
- cex_crx_create_crx_convert_quote
- cex_crx_create_crx_order
- cex_crx_create_crx_transfer
- cex_crx_update_crx_account
- cex_crx_update_crx_margin_positions_leverage
- cex_crx_update_crx_order
- cex_crx_update_crx_positions_leverage

### Authentication
- API Key Required: Yes (see skill doc/runtime MCP deployment)
- Permissions: Crx:Write
- Get API Key: https://www.gate.io/myaccount/profile/api-key/manage

### Installation Check
- Required: Gate (main)
- Install: Run installer skill for your IDE
  - Cursor: `gate-mcp-cursor-installer`
  - Codex: `gate-mcp-codex-installer`
  - Claude: `gate-mcp-claude-installer`
  - OpenClaw: `gate-mcp-openclaw-installer`

## Module Overview

| Module        | Description                                                             | Trigger Keywords                                                              |
|---------------|-------------------------------------------------------------------------|-------------------------------------------------------------------------------|
| **Spot**      | Limit/market buy/sell, cross-exchange arbitrage                         | `spot buy`, `spot sell`, `buy spot`, `sell spot`                              |
| **Margin**    | Long/short trading, margin management, auto-borrowing                   | `margin long`, `margin short`, `long margin`, `short margin`                  |
| **Futures**   | USDT perpetual contracts, dual-direction positions, leverage adjustment | `futures long`, `futures short`, `open long`, `open short`                    |
| **Transfer**  | Cross-exchange fund transfer                                            | `fund transfer`, `cross-exchange transfer`, `transfer`, `move funds`          |
| **Convert**   | Flash convert and conversion quote workflow                             | `convert trading`, `flash convert`, `convert`, `quote convert`                |
| **Orders**    | Query, cancel, amend orders, order history                              | `query orders`, `cancel order`, `amend order`, `order history`, `list orders` |
| **Positions** | Query all position types, history records                               | `query positions`, `check positions`, `position history`, `positions`         |
| **History**   | Query order/position/trade/interest history                             | `history query`, `trade history`, `interest history`, `history`               |

## Routing Rules

| Intent                      | Example Phrases                                                                              | Route To                                    |
|-----------------------------|----------------------------------------------------------------------------------------------|---------------------------------------------|
| **Spot Trading**            | "Buy 100 USDT worth of BTC", "Sell 0.5 BTC", "Market buy ETH spot"                           | Read `references/spot-trading.md`           |
| **Margin Trading**          | "Long 50 USDT worth of XRP on margin", "Short BTC on margin", "10x leverage long"            | Read `references/margin-trading.md`         |
| **Futures Trading**         | "Open 1 BTC futures long position", "Market short ETH", "Adjust leverage to 20x"             | Read `references/futures-trading.md`        |
| **Cross-Exchange Transfer** | "Transfer 100 USDT from Gate to Binance", "Move ETH from OKX to Gate"                        | Read `references/transfer.md`               |
| **Convert Trading**         | "Flash convert 10 USDT to BTC", "Convert 50 USDT to ETH on Gate"                             | Read `references/convert-trading.md`        |
| **Order Management**        | "Query all open orders", "Cancel that buy order", "Amend order price", "Query order history" | Read `references/order-management.md`       |
| **Position Query**          | "Query all my positions", "Show futures positions", "Position history"                       | Read `references/position-query.md`         |
| **History Query**           | "Query trade history", "Position history", "Margin interest history", "Account ledger"       | Read `references/history-query.md`          |
| **Unclear**                 | "Show account" , "Help me" , "Please Check my account"                                       | **Clarify**: Query account, then guide user |

## MCP Tools

This skill uses the **CrossEx MCP toolset** with the cex_crx prefix as its only core tool family.

**Scope rule**: Only execute operations explicitly documented in this skill. Only call tools listed in the tables below
or in `references/*.md`. Tools or operations not mentioned here must not be called.

### Tool Naming Convention

- List operations in the cex_crx family query symbols, orders, positions, transfers, or history
- Get operations in the cex_crx family query a single account setting, fee, rate, or order detail
- Create operations in the cex_crx family create an order, transfer, convert quote, or convert order
- Update operations in the cex_crx family update account settings, leverage, or existing orders
- Cancel operations in the cex_crx family cancel an existing order
- Close operations in the cex_crx family close an existing position

### Symbol And Rule Tools

| Tool                                  | Purpose                                    |
|---------------------------------------|--------------------------------------------|
| `cex_crx_list_crx_rule_symbols`       | List supported CrossEx trading symbols     |
| `cex_crx_list_crx_rule_risk_limits`   | Query symbol risk limit rules              |
| `cex_crx_list_crx_transfer_coins`     | List assets supported for CrossEx transfer |
| `cex_crx_get_crx_fee`                 | Query CrossEx trading fee information      |
| `cex_crx_get_crx_interest_rate`       | Query CrossEx interest rates               |
| `cex_crx_list_crx_coin_discount_rate` | Query collateral discount rates            |

### Account Tools

| Tool                            | Purpose                                     |
|---------------------------------|---------------------------------------------|
| `cex_crx_get_crx_account`       | Query CrossEx account overview and balances |
| `cex_crx_update_crx_account`    | Update CrossEx account settings             |
| `cex_crx_list_crx_account_book` | Query CrossEx account ledger entries        |

### Transfer And Convert Tools

| Tool                               | Purpose                          |
|------------------------------------|----------------------------------|
| `cex_crx_list_crx_transfers`       | Query transfer history           |
| `cex_crx_create_crx_transfer`      | Create a cross-exchange transfer |
| `cex_crx_create_crx_convert_quote` | Get a flash convert quote        |
| `cex_crx_create_crx_convert_order` | Execute a flash convert order    |

### Order Tools

| Tool                              | Purpose                   |
|-----------------------------------|---------------------------|
| `cex_crx_list_crx_open_orders`    | Query current open orders |
| `cex_crx_create_crx_order`        | Create a CrossEx order    |
| `cex_crx_get_crx_order`           | Query order details       |
| `cex_crx_update_crx_order`        | Amend an existing order   |
| `cex_crx_cancel_crx_order`        | Cancel a single order     |
| `cex_crx_list_crx_history_orders` | Query order history       |
| `cex_crx_list_crx_history_trades` | Query trade history       |

### Position And Leverage Tools

| Tool                                           | Purpose                            |
|------------------------------------------------|------------------------------------|
| `cex_crx_list_crx_positions`                   | Query current futures positions    |
| `cex_crx_list_crx_margin_positions`            | Query current margin positions     |
| `cex_crx_close_crx_position`                   | Close an existing CrossEx position |
| `cex_crx_get_crx_positions_leverage`           | Query futures leverage settings    |
| `cex_crx_update_crx_positions_leverage`        | Update futures leverage            |
| `cex_crx_get_crx_margin_positions_leverage`    | Query margin leverage settings     |
| `cex_crx_update_crx_margin_positions_leverage` | Update margin leverage             |
| `cex_crx_list_crx_history_positions`           | Query futures position history     |
| `cex_crx_list_crx_history_margin_positions`    | Query margin position history      |
| `cex_crx_list_crx_history_margin_interests`    | Query margin interest history      |
| `cex_crx_list_crx_adl_rank`                    | Query ADL rank information         |

### Usage Guidance

- Use the cex_crx MCP family as the default and only core MCP family for this skill.
- Use list/get tools to query symbol rules, fees, balances, leverage, or supported assets.
- Prefer history and account-book tools when the user asks for records, audit trails, or status verification.

## Execution

### 1. Intent and Parameter Identification

- Determine module (orders/positions/history)
- Extract key parameters:
    - **Trading Pair**: `GATE_SPOT_BTC_USDT`, `GATE_MARGIN_XRP_USDT`, `GATE_FUTURE_ETH_USDT`
    - **Exchange**: `GATE`, `BINANCE`, `OKX`, `BYBIT`
    - **Direction**: `BUY` (buy/long), `SELL` (sell/short)
    - **Quantity**: USDT amount, coin quantity, contract size
    - **Price**: Limit, market
    - **Leverage**: Leverage multiplier (margin/futures only)
    - **Position Side**: `LONG` (long), `SHORT` (short, margin/futures only)
- **Missing Parameters**: If required parameters are missing, ask user

### 2. Pre-checks

- **Trading Pair**: Call `cex_crx_list_crx_rule_symbols` to verify
- **Account Balance**: Call `cex_crx_get_crx_account` to check if available margin is sufficient
- **Position Check**:
    - Margin Trading: Check existing positions to avoid direction conflicts
    - Futures Trading: Check dual-direction position mode
- **Minimum Amount**: Query `min_quote_amount` (typically 3 USDT)
- **Exchange Status**: Verify target exchange is operating normally

### 3. Module Logic

#### Module A: Spot Trading

1. **Parameter Confirmation**:
    - Trading pair format: `GATE_SPOT_{BASE}_{QUOTE}`
    - Buy parameters: `quote_qty` (USDT amount)
    - Sell parameters: `qty` (coin quantity)
2. **Minimum Amount Check**: Call `cex_crx_list_crx_rule_symbols` to query minimum amount
3. **Pre-order Confirmation**: Display order summary (pair, direction, quantity, price), require user confirmation
4. **Place Order**: Call `cex_crx_create_crx_order`
5. **Verification**: Call `cex_crx_get_crx_order` to confirm order status

#### Module B: Margin Trading

1. **Parameter Confirmation**:
    - Trading pair format: `GATE_MARGIN_{BASE}_{QUOTE}`
    - Required parameters: `qty` (coin quantity), `position_side` (`LONG` or `SHORT`)
    - Optional parameters: `quote_qty` (USDT amount)
2. **Leverage Check**: Query current leverage, adjust if user specifies
3. **Position Direction**:
    - Long (`LONG`): Buy coin, borrow USDT
    - Short (`SHORT`): Sell coin, borrow coin
4. **Minimum Amount Check**: Call `cex_crx_list_crx_rule_symbols` to query minimum amount
5. **Pre-order Confirmation**: Display order summary (pair, direction, quantity, leverage), require confirmation
6. **Place Order**: Call `cex_crx_create_crx_order` with parameter `position_side`
7. **Verification**: Call `cex_crx_list_crx_margin_positions` with a `symbol` filter to confirm position

#### Module C: Futures Trading

1. **Parameter Confirmation**:
    - Trading pair format: `GATE_FUTURE_{BASE}_{QUOTE}`
    - Required parameters: `qty` (contract size), `position_side` (`LONG` or `SHORT`)
2. **Leverage Adjustment**: If user specifies leverage, call `cex_crx_get_crx_positions_leverage` and
   `cex_crx_update_crx_positions_leverage`
3. **Contract Size Calculation** (if ordering by value):
    - Get `quanto_multiplier` and current price
    - Round down to ensure overspending is avoided
4. **Minimum Size Check**: Call `cex_crx_list_crx_rule_symbols` to query minimum size
5. **Pre-order Confirmation**: Display order summary (pair, direction, size, leverage), require confirmation
6. **Place Order**: Call `cex_crx_create_crx_order` with parameter `position_side`
7. **Verification**: Call `cex_crx_list_crx_positions` with a `symbol` filter to confirm position

#### Module D: Cross-Exchange Transfer

1. **Transfer Type**:
    - Cross-exchange transfer: `cex_crx_create_crx_transfer` (Exchange A -> Exchange B)
2. **Parameter Confirmation**:
    - Cross-exchange transfer: `from`, `to`, `coin`, `amount`
    - **From/To Account Rules**:
        | Coin | Mode | Valid `from` / `to` | Defaults |
        |------|------|--------------------|---------|
        | USDT | Cross-Exchange | `SPOT` ↔ `CROSSEX` | `CROSSEX_{exchange_type}` → `CROSSEX` |
        | USDT | Sub-Exchange | `SPOT` ↔ `CROSSEX_{exchange_type}` or `CROSSEX_{exchange_type}` ↔ `CROSSEX_{exchange_type}` | `CROSSEX` → `CROSSEX_GATE` |
        | Non-USDT | Any | Must use `CROSSEX_{exchange_type}` (never `CROSSEX` alone). Cross-exchange transfers allowed (e.g., `CROSSEX_BINANCE` ↔ `CROSSEX_GATE`). | — |
3. **Supported Coin Check**: Call `cex_crx_list_crx_transfer_coins` to verify
4. **Balance Check**: Confirm source account has sufficient balance
5. **Pre-transfer Confirmation**: Display transfer summary (source, destination, coin, quantity), require confirmation
6. **Execute Transfer**: Call `cex_crx_create_crx_transfer`
7. **Verification**: Call `cex_crx_list_crx_transfers` to query transfer history and confirm

#### Module E: Convert Trading

1. **Convert Type**:
    - Flash convert quote: `cex_crx_create_crx_convert_quote`
    - Flash convert execution: `cex_crx_create_crx_convert_order`
2. **Parameter Confirmation**:
    - Flash convert: `from_coin`, `to_coin`, `from_amount`, `exchange_type`
3. **Balance Check**: Confirm source account has sufficient balance for the convert pair
4. **Pre-convert Confirmation**: Display source asset, target asset, rate, and expected receive amount, then require
   confirmation
5. **Quote**: Call `cex_crx_create_crx_convert_quote`
6. **Execute Convert**: Call `cex_crx_create_crx_convert_order` with the returned `quote_id`
7. **Verification**: Call `cex_crx_get_crx_account` to confirm resulting balances

#### Module F: Order Management

1. **Query Orders**:
    - Current open orders: Call `cex_crx_list_crx_open_orders`
    - Order details: Call `cex_crx_get_crx_order`
    - **Order History**: Call `cex_crx_list_crx_history_orders` (parameters: limit, page, from, to)
2. **Cancel Orders**:
    - Single cancel: Call `cex_crx_cancel_crx_order`
3. **Amend Orders**:
    - Check order status must be `open`
    - Call `cex_crx_update_crx_order` to amend price or quantity
4. **Display Results**: Display order information in table format

#### Module G: Position Query

1. **Query Types**:
    - Futures positions: Call `cex_crx_list_crx_positions`
    - Margin positions: Call `cex_crx_list_crx_margin_positions`
    - Futures leverage: Call `cex_crx_get_crx_positions_leverage`
    - Margin leverage: Call `cex_crx_get_crx_margin_positions_leverage`
2. **History Query**:
    - **Position History**: Call `cex_crx_list_crx_history_positions` (parameters: limit, page, from, to)
    - **Margin Position History**: Call `cex_crx_list_crx_history_margin_positions`
    - **Trade History**: Call `cex_crx_list_crx_history_trades` (parameters: limit, page, from, to)
3. **Display Format**:
    - Current positions: Table format (pair, direction, quantity, entry price, unrealized PnL)
    - History records: Reverse chronological order, display recent N records

#### Module H: History Query

1. **Order History**:
    - Call `cex_crx_list_crx_history_orders`
    - Parameters: `limit` (max 100), `page`, `from` (start timestamp), `to` (end timestamp)
2. **Trade History**:
    - Call `cex_crx_list_crx_history_trades`
    - Same parameters as above
3. **Position History**:
    - Call `cex_crx_list_crx_history_positions`
    - Same parameters as above
4. **Margin Position History**:
    - Call `cex_crx_list_crx_history_margin_positions`
    - Same parameters as above
5. **Margin Interest History**:
    - Call `cex_crx_list_crx_history_margin_interests`
    - Same parameters as above

## Report Template

After each operation, output a concise standardized result.

## Safety Rules

- **Credentials**: Never prompt or induce the user to paste API Secret Key into chat; prefer secure local MCP configuration.
- **User-to-User Transfer**: This skill does not support P2P or user-to-user transfers; only transfers between the user's own accounts (e.g., SPOT ↔ CROSSEX) are allowed.
- **Trade Orders**: Display complete order summary (pair, direction, quantity, price, leverage), require user
  confirmation before placing order
- **Cross-Exchange Transfer**: Display transfer details (source, destination, quantity, arrival time), require
  confirmation
- **Scope rule**: Only call tools documented in this skill. If the user requests an operation not documented here,
  respond that it is not supported by this skill.
- **Batch Operations**: Display operation scope and impact, require explicit confirmation

Example: *"Reply 'confirm' to execute the above operation."*

## Error Handling

| Error Code                                   | Handling                                                                                                                                                        |
|----------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `USER_NOT_EXIST`                             | Please confirm if a GATE CrossEx account has been opened. Refer to the GATE Help Center -> CrossEx Trading -> CrossEx Account Operation Guide for instructions. |
| `TRADE_INVALID_QUOTE_ORDER_QTY`              | ⚠️ Incorrect parameter name: Market buy must use `quote_qty`                                                                                                    |
| `TRADE_INVALID_ORDER_QTY`                    | ⚠️ Limit order error: Limit orders must use `qty` (coin quantity) + `price`                                                                                     |
| `TRADE_ORDER_AMOUNT_MIN_ERROR`               | Order amount below minimum notional value (typically 3 USDT), increase quantity or amount                                                                       |
| `CONVERT_TRADE_QUOTE_EXCHANGE_INVALID_ERROR` | ⚠️ Flash convert: `exchange_type` parameter value must be uppercase exchange code (e.g., `GATE`)                                                                |
| `TRADE_MARGIN_INVALID_PZ_SIDE_ERROR`         | Prompt that margin/futures trading must specify `position_side` (LONG/SHORT)                                                                                    |
| `BALANCE_NOT_ENOUGH`                         | Insufficient available margin, suggest reducing trade amount or depositing                                                                                      |
| `SYMBOL_NOT_FOUND`                           | Confirm trading pair format is correct (e.g., GATE_SPOT_BTC_USDT)                                                                                               |
| `INVALID_PARAM_VALUE`                        | Check parameter format (qty is numeric string, position_side is LONG/SHORT)                                                                                     |
| `POSITION_NOT_EMPTY`                         | Prompt to close position before reversing direction                                                                                                             |
| `TRADE_ORDER_LOT_SIZE_ERROR`                 | Suggest adjusting quantity to minimum unit of the trading pair                                                                                                  |
| `RATE_LIMIT_EXCEEDED`                        | Prompt user about rate limit; suggest retrying later or reducing request frequency                                                                     |
| `TRADE_INVALID_EXCHANGE_TYPE`                | Invalid exchange type; please check the `exchange_type` parameter (e.g., GATE, BINANCE, OKX, BYBIT)                                                   |
