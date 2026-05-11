# Supurr Skills

> Backtest, deploy, and monitor grid trading bots on Hyperliquid. Supports Native Perps, Spot markets (USDC/USDH), and HIP-3 sub-DEXes.

## Installation

### Option 1: skills.sh (Recommended)

```bash
npx skills add Supurr-App/supurr_skill
```

Supports Claude Code, Cursor, OpenCode, Antigravity, and more.

### Option 2: Direct Install

```bash
# Install AI skill to your tools
curl -fsSL https://cli.supurr.app/skill-install | bash
```

## Also Install: Supurr CLI

The skill teaches AI assistants to use the CLI. The skill installer automatically installs the CLI, but you can also install it manually:

```bash
curl -fsSL https://cli.supurr.app/install | bash
```

## Available Skills

| Skill                | Description                                                       |
| -------------------- | ----------------------------------------------------------------- |
| [supurr](./SKILL.md) | Complete CLI for backtesting, deploying, and monitoring grid bots |

## Quick Start

```bash
# 1. Install CLI
curl -fsSL https://cli.supurr.app/install | bash

# 2. Setup credentials
supurr init --address 0x... --api-wallet 0x...

# 3. Create config
supurr new grid --asset BTC --levels 4 --start-price 88000 --end-price 92000

# 4. Backtest
supurr backtest -c config.json -s 2026-01-28 -e 2026-02-01

# 5. Deploy
supurr deploy -c config.json

# 6. Monitor
supurr monitor --watch
```

## Repository Structure

```
supurr_skill/
├── .claude-plugin/
│   └── plugin.json       # Claude plugin manifest
├── scripts/
│   ├── install.sh        # CLI binary installer
│   └── skill-install.sh  # AI skill installer
├── SKILL.md              # Main skill documentation
└── README.md             # This file
```

## License

MIT
