# OpenMM AI Skills

> Open-source market making skills for AI agents

[![npm](https://img.shields.io/npm/v/@3rd-eye-labs/openmm)](https://www.npmjs.com/package/@3rd-eye-labs/openmm)
[![openmm-trading](https://img.shields.io/npm/v/@qbtlabs/openmm-trading?label=openmm-trading)](https://www.npmjs.com/package/@qbtlabs/openmm-trading)
[![openmm-market-data](https://img.shields.io/npm/v/@qbtlabs/openmm-market-data?label=openmm-market-data)](https://www.npmjs.com/package/@qbtlabs/openmm-market-data)
[![openclaw-openmm](https://img.shields.io/npm/v/@qbtlabs/openclaw-openmm?label=openclaw-openmm)](https://www.npmjs.com/package/@qbtlabs/openclaw-openmm)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![DeepWiki](https://img.shields.io/badge/docs-DeepWiki-purple)](https://deepwiki.com/3rd-Eye-Labs/OpenMM)

[Agent Skills](https://agentskills.io/home) for [OpenMM](https://github.com/3rd-Eye-Labs/OpenMM) — multi-exchange trading, grid strategies, portfolio management, and real-time market data for AI agents.

Built on the open [Agent Skills](https://agentskills.io/home) standard — a portable skill format recognized by OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, VS Code, OpenClaw, and 20+ other platforms.

---

## Install

### Install a skill (OpenClaw / ClawHub)

```bash
clawhub install openmm-exchange-setup
clawhub install openmm-grid-trading
clawhub install openmm-portfolio
```

### Install a skill (agents)

Point your agent at the raw skill URL:

```
https://raw.githubusercontent.com/QBT-Labs/OpenMM-ai/main/SKILL.md
https://raw.githubusercontent.com/QBT-Labs/OpenMM-ai/main/skills/exchange-setup/SKILL.md
https://raw.githubusercontent.com/QBT-Labs/OpenMM-ai/main/skills/grid-trading/SKILL.md
https://raw.githubusercontent.com/QBT-Labs/OpenMM-ai/main/skills/portfolio/SKILL.md
```

---

## Skills

| Skill | What it does | Install |
|-------|-------------|---------|
| **[OpenMM (Core)](#openmm-core)** | Full CLI, MCP, and library reference for multi-exchange market making | [`SKILL.md`](SKILL.md) |
| **[Exchange Setup](#exchange-setup)** | Step-by-step guide to configure exchange API credentials | [`SKILL.md`](skills/exchange-setup/SKILL.md) |
| **[Grid Trading](#grid-trading)** | Create and manage automated grid trading strategies | [`SKILL.md`](skills/grid-trading/SKILL.md) |
| **[Portfolio](#portfolio)** | Balance tracking, order overview, and market data across exchanges | [`SKILL.md`](skills/portfolio/SKILL.md) |

---

## Skill details

### OpenMM (Core)

The main skill — covers everything an agent needs to use OpenMM. Balance checks, market data, order management, grid trading, Cardano pool discovery, and safety rules. Includes full CLI reference and all 13 MCP tool mappings.

**[Download SKILL.md](SKILL.md)**

### Exchange Setup

Step-by-step guide to configure exchange API credentials via environment variables. Covers MEXC, Gate.io, Kraken, and Bitget. Includes permission setup, MCP server config, troubleshooting, and security best practices.

**[Download SKILL.md](skills/exchange-setup/SKILL.md)**

### Grid Trading

Create automated grid strategies that profit from market volatility. Linear and geometric spacing, flat and pyramidal sizing, volatility-based spread adjustment, grid profiles, and risk management.

**[Download SKILL.md](skills/grid-trading/SKILL.md)**

### Portfolio

Track balances and open orders across exchanges, check market prices, compare DEX vs CEX prices for Cardano tokens, and discover liquidity pools.

**[Download SKILL.md](skills/portfolio/SKILL.md)**

---

## Plugins

Self-contained plugin packages for structured agent integration:

| Plugin | What it does | Path |
|--------|-------------|------|
| **[openmm-trading](packages/plugins/openmm-trading)** | Exchange setup, order management, and grid trading strategies | `packages/plugins/openmm-trading` |
| **[openmm-market-data](packages/plugins/openmm-market-data)** | Market data, portfolio tracking, and Cardano DEX integration | `packages/plugins/openmm-market-data` |
| **[openclaw-openmm](packages/plugins/openclaw-openmm)** | OpenClaw plugin — agent tools and commands for Telegram/Discord | `packages/plugins/openclaw-openmm` |

### Install a plugin (OpenClaw)

```bash
openclaw plugins install @qbtlabs/openclaw-openmm
```

---

## Components

```
OpenMM Ecosystem
├── OpenMM (Core)           → github.com/3rd-Eye-Labs/OpenMM
├── OpenMM-MCP (Tools)      → github.com/QBT-Labs/OpenMM-MCP
└── OpenMM-AI (Skills)      → this repo
    ├── skills/             → flat skill files (Agent Skills standard)
    └── packages/plugins/   → structured plugin packages
```

Each skill folder is self-contained — `SKILL.md` has the core instructions an agent needs. Plugins bundle related skills with references, agents, and OpenClaw integration.

**x402 (coming soon)** — Payment layer for AI agent transactions is a work in progress.

---

## What are Agent Skills?

[Agent Skills](https://agentskills.io/home) is an open standard for portable AI agent capabilities. Skills are `SKILL.md` files that any compatible agent can read and execute.

These skills are built for OpenMM on centralized exchanges, but the format works with any platform that supports the Agent Skills standard — including OpenAI Codex, Gemini CLI, GitHub Copilot, Cursor, VS Code, OpenClaw, and more.

---

## Links

- **Core Library:** https://github.com/3rd-Eye-Labs/OpenMM
- **MCP Server:** https://github.com/QBT-Labs/OpenMM-MCP
- **npm:** https://www.npmjs.com/package/@3rd-eye-labs/openmm
- **Documentation:** https://deepwiki.com/3rd-Eye-Labs/OpenMM
- **Agent Skills Standard:** https://agentskills.io/home
- **Website:** https://qbtlabs.io

## License

MIT © [QBT Labs](https://qbtlabs.io)
