# openclaw-openmm

> OpenClaw plugin for OpenMM — trade, monitor, and manage grid strategies from Telegram or any OpenClaw channel

[![npm](https://img.shields.io/npm/v/@qbtlabs/openclaw-openmm)](https://www.npmjs.com/package/@qbtlabs/openclaw-openmm)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](../../../LICENSE)

An [OpenClaw](https://docs.openclaw.ai) plugin that wraps [OpenMM](https://github.com/3rd-Eye-Labs/OpenMM) as agent tools and auto-reply commands. Manage your trading from Telegram, Discord, or any other OpenClaw channel.

---

## Install

### OpenClaw CLI

```bash
openclaw plugins install @qbtlabs/openclaw-openmm
```

### npm (manual)

```bash
npm install @qbtlabs/openclaw-openmm
```

Then add to your OpenClaw config:

```json5
{
  plugins: {
    entries: {
      openmm: { enabled: true }
    }
  }
}
```

---

## Configure

Set your exchange credentials via the OpenClaw Control UI or directly in your config:

```json5
{
  plugins: {
    entries: {
      openmm: {
        enabled: true,
        config: {
          defaultExchange: "mexc",
          mexcApiKey: "...",
          mexcSecret: "...",
          // Add more exchanges as needed
        }
      }
    }
  }
}
```

### Supported Exchanges

| Exchange | Config Keys |
|----------|-------------|
| MEXC | `mexcApiKey`, `mexcSecret`, `mexcUid` |
| Gate.io | `gateioApiKey`, `gateioSecret` |
| Kraken | `krakenApiKey`, `krakenSecret` |
| Bitget | `bitgetApiKey`, `bitgetSecret`, `bitgetPassphrase` |

---

## Agent Tools

These tools are available to the LLM agent during conversation:

| Tool | Description | Side Effect |
|------|-------------|-------------|
| `openmm_balance` | Get exchange balances | No |
| `openmm_ticker` | Current price, bid/ask, volume | No |
| `openmm_orderbook` | Order book depth | No |
| `openmm_trades` | Recent trades | No |
| `openmm_list_orders` | List open orders | No |
| `openmm_grid_status` | Grid strategy status and P&L | No |
| `openmm_cardano_price` | Cardano token price from DEX pools | No |
| `openmm_discover_pools` | Discover Cardano DEX pools | No |
| `openmm_create_order` | Place a limit or market order | **Yes** (optional) |
| `openmm_cancel_order` | Cancel an order by ID | **Yes** (optional) |
| `openmm_cancel_all_orders` | Cancel all open orders | **Yes** (optional) |
| `openmm_grid_start` | Start a grid strategy (dry-run default) | **Yes** (optional) |
| `openmm_grid_stop` | Stop a running grid strategy | **Yes** (optional) |

Tools marked **optional** require explicit allowlisting in your agent config:

```json5
{
  agents: {
    list: [{
      tools: {
        allow: ["openmm_create_order", "openmm_cancel_order", "openmm_grid_start", "openmm_grid_stop"]
      }
    }]
  }
}
```

---

## Auto-Reply Commands

These commands execute immediately without invoking the AI agent:

| Command | Description | Example |
|---------|-------------|---------|
| `/balance [exchange]` | Quick balance check | `/balance mexc` |
| `/price <exchange> <symbol>` | Quick price check | `/price kraken ADA/EUR` |
| `/strategy <exchange> <symbol>` | Grid strategy status | `/strategy mexc SNEK/USDT` |
| `/orders [exchange]` | List open orders | `/orders bitget` |
| `/orderbook <exchange> <symbol>` | Order book (top 10) | `/orderbook mexc BTC/USDT` |
| `/pools <token>` | Discover Cardano DEX pools | `/pools SNEK` |
| `/cardano <token>` | Cardano token DEX price | `/cardano INDY` |
| `/cancel-all <exchange> [symbol]` | Cancel all open orders (auth required) | `/cancel-all mexc SNEK/USDT` |

---

## Background Service

The plugin registers a strategy monitor service that tracks active grid strategies. The service starts automatically when the plugin is enabled.

---

## Safety

- **Order creation and grid start are optional tools** — they require explicit allowlisting before the agent can use them
- **Grid strategies default to dry-run** — the `openmm_grid_start` tool simulates by default unless `dryRun: false` is passed
- **Never enable withdrawal permissions** on your exchange API keys — trading keys should only have trade and read access

---

## Links

- **OpenMM Core:** https://github.com/3rd-Eye-Labs/OpenMM
- **MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
- **OpenClaw Plugin Docs:** https://docs.openclaw.ai/tools/plugin
- **OpenClaw Agent Tools:** https://docs.openclaw.ai/plugins/agent-tools

## License

MIT
