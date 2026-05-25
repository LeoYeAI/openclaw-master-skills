# OpenMM MCP Tools Reference -- Trading

Reference table for all trading-related MCP tools exposed by the OpenMM MCP server.

## Order Management

### create_order

Place a limit or market order on a supported exchange.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | Yes | Trading pair (e.g. BTC/USDT, ADA/EUR) |
| `type` | string | Yes | Order type: `limit` or `market` |
| `side` | string | Yes | Order side: `buy` or `sell` |
| `amount` | number | Yes | Amount in base currency |
| `price` | number | Limit only | Price in quote currency (required for limit, ignored for market) |

### cancel_order

Cancel a specific order by ID.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `orderId` | string | Yes | The order ID to cancel |
| `symbol` | string | Yes | Trading pair the order belongs to |

### cancel_all_orders

Cancel all open orders for a trading pair.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | Yes | Trading pair to cancel all orders for |

### list_orders

List open orders, optionally filtered by trading pair.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | No | Filter by trading pair (returns all if omitted) |

## Account

### get_balance

Get account balances for all assets or a specific asset.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `asset` | string | No | Filter by asset (e.g. USDT, BTC). Returns all if omitted |

## Strategy

### start_grid_strategy

Calculate and optionally place grid trading orders around the current price. Defaults to dry-run mode.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `exchange` | string | Yes | -- | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | Yes | -- | Trading pair (e.g. INDY/USDT) |
| `levels` | number | No | 5 | Grid levels per side (1-10) |
| `spacing` | number | No | 0.02 | Base spacing as decimal (0.02 = 2%) |
| `orderSize` | number | No | 50 | Base order size in quote currency |
| `spacingModel` | string | No | linear | Spacing model: linear or geometric |
| `spacingFactor` | number | No | 1.3 | Factor for geometric spacing |
| `sizeModel` | string | No | flat | Size model: flat or pyramidal |
| `dryRun` | boolean | No | true | Preview grid without placing orders |

### stop_strategy

Cancel all open orders for a trading pair, stopping any running grid strategy.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | Yes | Trading pair to stop strategy for |

### get_strategy_status

Get current grid strategy status including open orders, current price, and P&L estimate.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `exchange` | string | Yes | Exchange: mexc, gateio, kraken, bitget |
| `symbol` | string | Yes | Trading pair to check status for |

## Summary Table

| Tool | Category | Description |
|------|----------|-------------|
| `create_order` | Orders | Place a limit or market order |
| `cancel_order` | Orders | Cancel an order by ID |
| `cancel_all_orders` | Orders | Cancel all orders for a pair |
| `list_orders` | Orders | List open orders |
| `get_balance` | Account | Get account balances |
| `start_grid_strategy` | Strategy | Calculate/place grid orders (dry-run default) |
| `stop_strategy` | Strategy | Stop a running grid strategy |
| `get_strategy_status` | Strategy | Get grid status and P&L |
