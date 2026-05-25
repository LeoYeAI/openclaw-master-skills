# openmm-trading Plugin -- Agent Instructions

## What This Plugin Does

The `openmm-trading` plugin provides skills, references, and agent personas for trading with OpenMM. It covers exchange credential setup, manual order management, and automated grid trading strategies across four supported exchanges: MEXC, Gate.io, Kraken, and Bitget.

## How to Use

### Skills

Load the appropriate skill based on the user's intent:

- **exchange-setup** -- Use when the user needs to configure API credentials for a new exchange or troubleshoot connection issues.
- **grid-trading** -- Use when the user wants to create, configure, or manage an automated grid trading strategy.
- **order-management** -- Use when the user wants to place, list, or cancel individual orders.

### References

Consult these references when you need exact CLI flags or MCP tool parameters:

- **references/cli-reference.md** -- Full flag reference for `balance`, `orders`, and `trade` CLI commands.
- **references/mcp-tools.md** -- Trading MCP tools with parameter tables.

### Agents

- **agents/grid-trader.md** -- Load this persona when the user wants autonomous grid trading with pre-flight checks and safety guardrails.

## Safety Rules

1. **Never execute trades without user confirmation.** Always show the plan first and get explicit approval.
2. **Always dry-run grid strategies first.** Use `--dry-run` (CLI) or `dryRun: true` (MCP) before placing real orders.
3. **Check balances before trading.** Run `openmm balance --exchange <ex>` to verify sufficient funds.
4. **Check current price before trading.** Run `openmm ticker --exchange <ex> --symbol <sym>` to verify the market price.
5. **Respect minimum order values.** MEXC/Gate.io/Bitget: 1 USDT minimum. Kraken: 5 EUR/USD minimum.
6. **Never enable withdrawal permissions.** Trading API keys should only have trade and read permissions.
7. **Never commit credentials.** Environment variables and `.env` files must never be committed to version control.
8. **Use risk controls.** Always set `--max-position` and `--safety-reserve` for grid strategies.

## MCP Tools Available

When the OpenMM MCP server is connected, these trading tools are available:

| Tool | Purpose |
|------|---------|
| `create_order` | Place a limit or market order |
| `cancel_order` | Cancel an order by ID |
| `cancel_all_orders` | Cancel all open orders for a pair |
| `list_orders` | List open orders |
| `get_balance` | Check account balances |
| `start_grid_strategy` | Calculate and place grid orders (dry-run by default) |
| `stop_strategy` | Stop a running grid strategy |
| `get_strategy_status` | Get current grid status and P&L |
| `get_ticker` | Get current price and spread |
| `get_orderbook` | Get order book depth |
| `get_trades` | Get recent trades |

## Environment Variables

Each exchange requires its own set of credentials:

- **MEXC:** `MEXC_API_KEY`, `MEXC_SECRET`
- **Gate.io:** `GATEIO_API_KEY`, `GATEIO_SECRET`
- **Kraken:** `KRAKEN_API_KEY`, `KRAKEN_SECRET`
- **Bitget:** `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE`

## Symbol Format

Always use `BASE/QUOTE` format: `BTC/USDT`, `ADA/EUR`, `SNEK/USDT`. The CLI automatically converts to exchange-specific format.
