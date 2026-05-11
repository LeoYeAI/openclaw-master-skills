# Gate CrossEx Cross-Exchange Trading

## Overview

[Gate CrossEx](https://www.gate.com/crossex) is an AI Agent skill for Gate's cross-exchange unified trading platform. It
allows users to trade across multiple mainstream exchanges (Gate, Binance, OKX, Bybit) through a single account,
providing complete account management, asset transfer, order placement, and position management features.

### Core Capabilities

| Module        | Description                                        | Example                                  |
|---------------|----------------------------------------------------|------------------------------------------|
| **Spot**      | Limit/market buy/sell, cross-exchange arbitrage    | "Buy 100 USDT worth of BTC"              |
| **Margin**    | Long/short trading, margin management              | "Long 50 USDT worth of XRP on margin"    |
| **Futures**   | USDT perpetual contracts, dual-direction positions | "Open 1 BTC futures long position"       |
| **Transfer**  | Cross-exchange fund transfer                       | "Transfer 100 USDT from Gate to Binance" |
| **Convert**   | Flash convert and convert quote workflow           | "Flash convert 10 USDT to BTC"           |
| **Orders**    | Query, cancel, amend orders                        | "Cancel all BTC_USDT orders"             |
| **Positions** | Query all position types, history records          | "Query all my positions"                 |
| **History**   | Query order/position/trade/interest history        | "Query trade history"                    |

---

## Supported Exchanges

| Exchange    | Code      | Spot | Margin | Futures |
|-------------|-----------|------|--------|---------|
| **Gate**    | `GATE`    | ✅    | ✅      | ✅       |
| **Binance** | `BINANCE` | ✅    | ✅      | ✅       |
| **OKX**     | `OKX`     | ✅    | ✅      | ✅       |
| **Bybit**   | `BYBIT`   | ✅    | ❌      | ✅       |

---

## Architecture

This skill uses a routing architecture. The main `SKILL.md` handles intent detection and routing, while detailed
workflows live in `references/*.md`.

### Routing

Intents are routed to corresponding reference documents via keywords:

| Intent                  | Keywords                                                     | Reference                        |
|-------------------------|--------------------------------------------------------------|----------------------------------|
| Spot Trading            | spot buy, spot sell, buy spot, sell spot                     | `references/spot-trading.md`     |
| Margin Trading          | margin long, margin short, long margin, short margin         | `references/margin-trading.md`   |
| Futures Trading         | futures long, futures short, open long, open short           | `references/futures-trading.md`  |
| Cross-Exchange Transfer | fund transfer, cross-exchange transfer, transfer, move funds | `references/transfer.md`         |
| Convert Trading         | convert trading, flash convert, convert, quote convert       | `references/convert-trading.md`  |
| Order Management        | query orders, cancel order, amend order, list orders         | `references/order-management.md` |
| Position Query          | query positions, check positions, positions                  | `references/position-query.md`   |
| History Query           | history query, trade history, interest history, history      | `references/history-query.md`    |
| Asset Query             | query assets, total assets, available margin, assets         | Call `cex_crx_get_crx_account`   |

---

## Quick Start

### Prerequisites

- Gate MCP configured and connected
- Gate API Key used by MCP must have **CrossEx** permission to operate on the CrossEx account. You use only a small amount of funds for testing.

### Example Prompts

```
# Spot Trading
"Buy 100 USDT worth of BTC"
"Sell 0.5 BTC spot"

# Margin Trading
"Long 50 USDT worth of XRP on margin"
"Short BTC with 10x leverage"

# Futures Trading
"Open 1 BTC futures long position"
"Market short 5 ETH futures"

# Cross-Exchange Transfer
"Transfer 100 USDT from Gate to Binance"

# Convert Trading
"Flash convert 10 USDT to BTC"

# Query Positions
"Query all my positions"
"Show futures positions"
```

---

### File Structure

```
gate-exchange-crossex/
├── README.md
├── SKILL.md
├── CHANGELOG.md
└── references/
    ├── runtime-rules.md  # Shared runtime rules (auth, MCP check, etc.)
    ├── spot-trading.md            # Spot trading scenarios
    ├── margin-trading.md          # Margin trading scenarios
    ├── futures-trading.md         # Futures trading scenarios
    ├── transfer.md                # Cross-exchange transfer scenarios
    ├── convert-trading.md         # Flash convert scenarios
    ├── order-management.md        # Order management scenarios
    ├── position-query.md         # Position query scenarios
    └── history-query.md          # History query scenarios
```

---

## Trading Pair Naming Rules

Format: `{EXCHANGE}_{BUSINESS_TYPE}_{BASE}_{QUOTE}`

### Examples

| Type    | Format                             | Example                   |
|---------|------------------------------------|---------------------------|
| Spot    | `{EXCHANGE}_SPOT_{BASE}_{QUOTE}`   | `GATE_SPOT_BTC_USDT`      |
| Margin  | `{EXCHANGE}_MARGIN_{BASE}_{QUOTE}` | `BINANCE_MARGIN_ETH_USDT` |
| Futures | `{EXCHANGE}_FUTURE_{BASE}_{QUOTE}` | `OKX_FUTURE_SOL_USDT`     |

---

## Security

- Only call `cex_crx_*` MCP functions
- All trading operations require user confirmation before execution
- Does not handle or store credentials in the skill
- **No P2P transfer**: This skill does not support transfers between different users; only transfers within the user's own accounts (e.g., SPOT ↔ CROSSEX) are allowed.
- **No Secret paste**: Never prompt the user to paste API Secret Key into chat; prefer secure local MCP configuration.

**⚠️ Important Notice**:
> Never reveal your API Key or Secret to anyone (including customer support).
> If your API Key is accidentally leaked, delete it immediately and recreate.

---

## License

MIT

---

## Technical Support

### Official Documentation

- [Gate CrossEx API Documentation](https://www.gate.com/docs/developers/crossex)
- [Gate API v4 Documentation](https://www.gate.com/docs/developers/apiv4)
- [Gate CrossEx Product Page](https://www.gate.com/crossex)

### Technical Support

- **Online Ticket**: Submit ticket after login
- **Email Support**: [mm@gate.com](mailto:mm@gate.com)

## Source

- **Repository**: [github.com/gate/gate-skills](https://github.com/gate/gate-skills)
- **Publisher**: [Gate.com](https://www.gate.com)
