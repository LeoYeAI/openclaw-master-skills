# openmm-trading

Exchange setup, order management, and grid trading strategies for [OpenMM](https://github.com/3rd-Eye-Labs/OpenMM).

## Overview

The `openmm-trading` plugin bundles trading-focused skills and reference material for OpenMM into a single installable package. It covers:

- **Exchange Setup** -- configure API credentials for MEXC, Gate.io, Kraken, and Bitget
- **Order Management** -- place, list, and cancel limit/market orders
- **Grid Trading** -- automated grid strategies with dynamic spacing, sizing, and volatility adjustment

## Installation

### npm

```bash
npm install @qbtlabs/openmm-trading
```

The plugin depends on the OpenMM CLI:

```bash
npm install -g @3rd-eye-labs/openmm
```

### ClawHub

Search for `openmm-trading` on [ClawHub](https://clawhub.dev) and install from the registry.

### OpenClaw (manual)

Copy the plugin directory into your OpenClaw plugins folder:

```
~/.openclaw/plugins/openmm-trading/
```

## Skills

| Skill | Description |
|-------|-------------|
| `exchange-setup` | Step-by-step guide to configure exchange API credentials |
| `grid-trading` | Create and manage automated grid trading strategies |
| `order-management` | Place, list, and cancel orders on supported exchanges |

## References

| Reference | Description |
|-----------|-------------|
| `cli-reference` | Full CLI flag reference for `trade`, `orders`, and `balance` commands |
| `mcp-tools` | Trading MCP tools reference table with parameters |

## Agents

| Agent | Description |
|-------|-------------|
| `grid-trader` | Autonomous grid trading agent with pre-flight checks and safety guardrails |

## Quick Start

1. Install the OpenMM CLI:

```bash
npm install -g @3rd-eye-labs/openmm
```

2. Set up exchange credentials (e.g. MEXC):

```bash
export MEXC_API_KEY="your_api_key"
export MEXC_SECRET="your_secret_key"
```

3. Verify connection:

```bash
openmm balance --exchange mexc
```

4. Preview a grid strategy (dry run):

```bash
openmm trade --strategy grid --exchange mexc --symbol BTC/USDT --dry-run
```

5. Start trading:

```bash
openmm trade --strategy grid --exchange mexc --symbol BTC/USDT \
  --levels 5 --spacing 0.02 --size 50
```

## Supported Exchanges

| Exchange | Min Order | Credentials |
|----------|-----------|-------------|
| MEXC | 1 USDT | `MEXC_API_KEY`, `MEXC_SECRET` |
| Gate.io | 1 USDT | `GATEIO_API_KEY`, `GATEIO_SECRET` |
| Bitget | 1 USDT | `BITGET_API_KEY`, `BITGET_SECRET`, `BITGET_PASSPHRASE` |
| Kraken | 5 EUR/USD | `KRAKEN_API_KEY`, `KRAKEN_SECRET` |

## Links

- **OpenMM GitHub:** https://github.com/3rd-Eye-Labs/OpenMM
- **OpenMM npm:** https://www.npmjs.com/package/@3rd-eye-labs/openmm
- **MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
- **Documentation:** https://deepwiki.com/3rd-Eye-Labs/OpenMM

## License

MIT
