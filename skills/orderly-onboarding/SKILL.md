---
name: orderly-onboarding
description: Agent onboarding for Orderly Network - omnichain perpetual futures infrastructure, MCP server, skills, and developer quickstart
---

# Orderly Network: Agent Onboarding

Orderly is an omnichain orderbook-based trading infrastructure providing perpetual futures liquidity for decentralized exchanges. This skill is your starting point for building on or learning about Orderly Network.

## When to Use

- First time encountering Orderly Network
- Setting up AI agent tools for Orderly development
- Understanding the Orderly ecosystem and offerings
- Finding the right skill or resource for your task
- Understanding what tools are available for AI agents

## What is Orderly Network

Orderly is a combination of an orderbook-based trading infrastructure and a robust liquidity layer offering perpetual futures orderbooks. Unlike traditional platforms, Orderly doesn't have a front end—it operates at the core of the ecosystem, providing essential services to projects built on top.

**Key Characteristics:**

- **Omnichain CLOB**: Shared Central Limit Order Book accessible from all major EVM chains and Solana
- **Backend Infrastructure**: No official front end; builders create DEXes and trading interfaces on top
- **On-chain Settlement**: All trades settle on-chain while maintaining full self-custody
- **Unified Liquidity**: One orderbook serves all integrated front-ends
- **Perpetual Futures**: Trade BTC, ETH, SOL, and more with up to 50x leverage
- **Gasless Trading**: No gas fees once funds are deposited and trading keys activated
- **One-Click Trading**: New trading key pair per session, no further signatures needed

**Primary Use Cases:**

| Use Case              | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| **Builders/DEXes**    | Create your own Perps DEX on EVM and Solana with plug-and-play SDKs        |
| **Perps Aggregators** | Access Orderly's shared liquidity directly via API or SDK                  |
| **Trading Desks**     | Use APIs for CEX-level trading with low latency orderbook                  |
| **Trading Bots**      | Connect to orderbook for best rates, SL/limit orders, gasless transactions |

## Key Advantages

- **Unified Orderbook & Liquidity**: Access all major chains through a single trading infrastructure
- **Quick Development**: Launch a DEX within days using our SDKs
- **Ready-to-Use Liquidity**: Powered by multiple top-tier market makers
- **Revenue Sharing**: Earn a share of generated fees from your platform
- **CEX-Level Performance**: Low latency matching engine with on-chain settlement
- **Self-Custody**: You control your assets and private keys
- **Collaborative Ecosystem**: Join a thriving community of builders

## Architecture

Your Application (DEX, Bot, Wallet, Aggregator)

- Orderly Infrastructure
  - **CLOB** — Shared Central Limit Order Book (unified across all chains)
  - **Matching Engine** — Low-latency order matching (CEX-level performance)
  - **Vault** — On-chain settlement with self-custody
  - **Risk Management** — Liquidation engine and position monitoring
- Settlement Networks
  - **EVM**: Arbitrum, Optimism, Base, Ethereum, Polygon, Mantle
  - **Non-EVM**: Solana

## Getting Started: AI Agent Tools

To build on Orderly, **install the MCP server** for the best development experience. It provides 8 powerful tools for documentation search, SDK patterns, contract addresses, workflows, and API reference.

### MCP Server (Recommended)

The MCP server provides AI assistants with instant access to Orderly documentation, code patterns, and API references.

**Quick Install:**

```bash
npx @orderly.network/mcp-server init --client <client>
```

**Supported Clients:**

| Client      | Command             | Config File            |
| ----------- | ------------------- | ---------------------- |
| Claude Code | `--client claude`   | `.mcp.json`            |
| Cursor      | `--client cursor`   | `.cursor/mcp.json`     |
| VS Code     | `--client vscode`   | `.vscode/mcp.json`     |
| Codex       | `--client codex`    | `~/.codex/config.toml` |
| OpenCode    | `--client opencode` | `.opencode/mcp.json`   |

**Manual Configuration:**

If automatic setup doesn't work, add this configuration to your AI client:

**Claude Code** (`.mcp.json`):

```json
{
  "mcpServers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**Cursor** (`.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**VS Code** (`.vscode/mcp.json`):

```json
{
  "servers": {
    "orderly": {
      "command": "npx",
      "args": ["@orderly.network/mcp-server@latest"]
    }
  }
}
```

**OpenCode** (`.opencode/mcp.json`):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "orderly": {
      "type": "local",
      "command": ["npx", "@orderly.network/mcp-server@latest"],
      "enabled": true
    }
  }
}
```

**Codex** (`~/.codex/config.toml`):

```toml
[mcp_servers.orderly]
command = "npx"
args = ["@orderly.network/mcp-server@latest"]
```

**What the MCP Server Provides:**

| Tool                       | Description                                      |
| -------------------------- | ------------------------------------------------ |
| `search_orderly_docs`      | Search Orderly documentation for specific topics |
| `get_sdk_pattern`          | Get code examples for SDK v2 hooks and patterns  |
| `get_contract_addresses`   | Lookup smart contract addresses for any chain    |
| `explain_workflow`         | Step-by-step guides for common tasks             |
| `get_api_info`             | REST API and WebSocket endpoint documentation    |
| `get_indexer_api_info`     | Trading metrics, events, volume statistics       |
| `get_component_guide`      | React UI component building guides               |
| `get_orderly_one_api_info` | DEX creation and management API for Orderly One  |

### Agent Skills

Install Orderly skills to enhance your AI agent with procedural knowledge for building on Orderly.

**Install all skills globally (recommended):**

```bash
npx skills add OrderlyNetwork/skills --all --agent '*' -g
```

**Install all skills locally:**

```bash
npx skills add OrderlyNetwork/skills --all
```

**Install specific skills:**

```bash
# List available skills
npx skills add OrderlyNetwork/skills --list

# Install specific skill
npx skills add OrderlyNetwork/skills --skill orderly-trading-orders

# Install multiple skills
npx skills add OrderlyNetwork/skills --skill orderly-api-authentication --skill orderly-trading-orders

# Install for specific agent
npx skills add OrderlyNetwork/skills --all --agent claude-code -g
```

**Global vs Local:**

- **Global (`-g`)**: Available across all projects, installed to user directory
- **Local**: Project-specific, creates `.skills/` in repo, can be committed to version control

**Available Skills:**

| Category           | Skill                            | Description                                         |
| ------------------ | -------------------------------- | --------------------------------------------------- |
| **API / Protocol** | `orderly-api-authentication`     | Two-layer auth: EIP-712 (EVM) + Ed25519 (Solana)    |
|                    | `orderly-trading-orders`         | Place, manage, cancel orders via REST API or SDK    |
|                    | `orderly-positions-tpsl`         | Monitor positions, TP/SL, leverage, PnL             |
|                    | `orderly-websocket-streaming`    | Real-time WebSocket for orderbook and executions    |
|                    | `orderly-deposit-withdraw`       | Token deposits, withdrawals, cross-chain operations |
| **SDK / React**    | `orderly-sdk-react-hooks`        | Reference for all React SDK hooks                   |
|                    | `orderly-ui-components`          | Pre-built React UI components                       |
|                    | `orderly-sdk-install-dependency` | Install Orderly SDK packages                        |
|                    | `orderly-sdk-dex-architecture`   | Complete DEX project structure and setup            |
|                    | `orderly-sdk-page-components`    | Pre-built page components                           |
|                    | `orderly-sdk-theming`            | CSS variable theming and customization              |
|                    | `orderly-sdk-trading-workflows`  | End-to-end trading flows                            |
| **Platform**       | `orderly-sdk-wallet-connection`  | Wallet integration for EVM and Solana               |
|                    | `orderly-sdk-debugging`          | Debug/troubleshoot SDK errors                       |
|                    | `orderly-one-dex`                | Create/manage custom DEX with Orderly One API       |

## For Builders (SDK & DEX Development)

Build custom trading interfaces using Orderly's React SDK v2.

**Core SDK Packages:**

```bash
# Full DEX setup
npm install @orderly.network/react-app \
            @orderly.network/trading \
            @orderly.network/portfolio \
            @orderly.network/markets \
            @orderly.network/wallet-connector \
            @orderly.network/i18n

# Required: EVM wallet support
npm install @web3-onboard/injected-wallets @web3-onboard/walletconnect

# Required: Solana wallet support
npm install @solana/wallet-adapter-base @solana/wallet-adapter-wallets
```

**Key Components Available:**

- `OrderEntry` - Order placement form
- `Orderbook` - Market depth display
- `PositionsView` - Position management table
- `TradingPage` - Full trading page
- `Portfolio` - User portfolio dashboard
- `ConnectWalletButton` - Wallet connection UI

**Orderly One (White-Label DEX):**

Launch your own branded perpetuals DEX without building from scratch. Orderly One provides a turnkey solution with:

- Custom domain and branding
- Fee revenue sharing after paying graduation fee
- Full trading infrastructure
- Custom theme

**Load these skills for SDK development:**

- **orderly-sdk-install-dependency** - Package installation guide
- **orderly-sdk-dex-architecture** - Project structure and providers
- **orderly-sdk-wallet-connection** - Wallet integration
- **orderly-sdk-trading-workflows** - Complete trading flows
- **orderly-sdk-theming** - Customization guide

## For API / Bot Developers

Integrate directly with Orderly's REST API and WebSocket streams.

**API Base URLs:**

| Network | URL                               |
| ------- | --------------------------------- |
| Mainnet | `https://api.orderly.org`         |
| Testnet | `https://testnet-api.orderly.org` |

**WebSocket URLs:**

| Network | URL                               |
| ------- | --------------------------------- |
| Mainnet | `wss://ws.orderly.org/ws`         |
| Testnet | `wss://testnet-ws.orderly.org/ws` |

**Authentication:**

- Ed25519 key pair generation for API signing
- EIP-712 wallet signatures for EVM accounts
- Ed25519 message signing for Solana accounts

**Symbol Format:**

```
PERP_<TOKEN>_USDC
```

Examples: `PERP_ETH_USDC`, `PERP_BTC_USDC`, `PERP_SOL_USDC`

**Key Endpoints:**

- `POST /v1/order` - Place order
- `GET /v1/positions` - Get positions
- `GET /v1/orders` - Get orders
- `GET /v1/orderbook/{symbol}` - Orderbook snapshot
- `GET /v1/public/futures` - Market info

**Load these skills for API development:**

- **orderly-api-authentication** - Complete auth setup
- **orderly-trading-orders** - Order management
- **orderly-positions-tpsl** - Position management
- **orderly-websocket-streaming** - Real-time data

## Supported Chains

Orderly supports multiple EVM and non-EVM chains. To get the current list of supported networks with their chain IDs, vault addresses, and RPC endpoints:

```
GET https://api.orderly.org/v1/public/chain_info
```

This endpoint returns all mainnet and testnet chains currently supported by Orderly, including Arbitrum, Optimism, Base, Ethereum, Polygon, Mantle, Solana, Sei, Avalanche, BSC, Abstract, and more.

## $ORDER Token

The $ORDER token is central to the Orderly ecosystem:

- **Maximum Supply:** 1,000,000,000 tokens
- **Staking:** Stake $ORDER to earn VALOR and protocol revenue share
- **VALOR:** Non-transferable metric measuring staking position; redeemable for esORDER rewards
- **Revenue Sharing:** 30% of protocol net fees distributed to stakers
- **Governance:** Stakers participate in protocol governance decisions
- **esORDER:** Escrowed ORDER for rewards with vesting mechanics

**Token Contracts:**

| Network          | Address                                        |
| ---------------- | ---------------------------------------------- |
| Ethereum (ERC20) | `0xABD4C63d2616A5201454168269031355f4764337`   |
| EVM Chains (OFT) | `0x4E200fE2f3eFb977d5fd9c430A41531FB04d97B8`   |
| Solana           | `ABt79MkRXUsoHuV2CVQT32YMXQhTparKFjmidQxgiQ6E` |

For full tokenomics details, visit: https://orderly.network/docs/introduction/tokenomics

## Key Links

| Resource         | URL                                                       |
| ---------------- | --------------------------------------------------------- |
| Documentation    | https://orderly.network/docs                              |
| SDK Repository   | https://github.com/orderlynetwork/js-sdk                  |
| Example DEX      | https://github.com/orderlynetwork/example-dex             |
| MCP Server (npm) | https://www.npmjs.com/package/@orderly.network/mcp-server |
| Skills (npm)     | https://www.npmjs.com/package/@orderly.network/skills     |
| Skills.sh        | https://skills.sh                                         |
| Orderly App      | https://app.orderly.network                               |
| Discord          | https://discord.gg/OrderlyNetwork                         |
| Twitter          | https://twitter.com/OrderlyNetwork                        |

## Recommended Next Steps

**If you're building a DEX:**

1. Load **orderly-sdk-install-dependency** and **orderly-sdk-dex-architecture**
2. Install MCP server: `npx @orderly.network/mcp-server init`
3. Set up wallet connection with **orderly-sdk-wallet-connection**
4. Build your UI with **orderly-ui-components**

**If you're building trading bots or API integrations:**

1. Load **orderly-api-authentication** first
2. Install MCP server for API reference
3. Load **orderly-trading-orders** and **orderly-websocket-streaming**

**If you're launching a white-label DEX:**

1. Install MCP server for Orderly One API tools: `npx @orderly.network/mcp-server init`
2. Load **orderly-one-dex** skill for DEX creation and management workflows
3. Load **orderly-sdk-theming** skill to understand theme structure for API updates

**If you're troubleshooting:**

1. Load **orderly-sdk-debugging**
2. Use MCP server to search documentation

**For testing:**

- Use Testnet environment for development
- Request testnet USDC from the faucet: `POST /v1/faucet/usdc` (testnet only)
- Each account can use faucet up to 3 times

## Common Issues

### "Where do I start building?"

Install the MCP server first: `npx @orderly.network/mcp-server init --client <your-client>`

Then ask: "How do I connect to Orderly Network?" or load **orderly-sdk-wallet-connection**.

### "What's the difference between MCP server and Skills?"

- **MCP Server**: Runtime tools for your AI assistant (documentation search, pattern lookup, API reference)
- **Skills**: Procedural knowledge embedded in your context (how-to guides, code examples, best practices)

Use both for the best experience.

### "How do I test without real funds?"

Use the Testnet environment:

- API: `https://testnet-api.orderly.org`
- WebSocket: `wss://testnet-ws.orderly.org/ws`
- Get test USDC: `POST https://testnet-operator-evm.orderly.org/v1/faucet/usdc`

### "Do I need to handle authentication manually?"

The SDK handles authentication automatically. For API-only integration, load **orderly-api-authentication** for the complete auth flow.

## Related Skills

### API / Protocol

- **orderly-api-authentication** - Complete authentication setup
- **orderly-trading-orders** - Order management
- **orderly-positions-tpsl** - Position and risk management
- **orderly-websocket-streaming** - Real-time data streaming
- **orderly-deposit-withdraw** - Asset management

### SDK / React

- **orderly-sdk-react-hooks** - React hooks reference
- **orderly-ui-components** - Pre-built UI components
- **orderly-sdk-install-dependency** - SDK installation
- **orderly-sdk-dex-architecture** - DEX architecture
- **orderly-sdk-page-components** - Page components
- **orderly-sdk-theming** - Theming guide
- **orderly-sdk-trading-workflows** - Trading workflows

### Platform

- **orderly-sdk-wallet-connection** - Wallet integration
- **orderly-sdk-debugging** - Debugging guide
- **orderly-one-dex** - Orderly One DEX management
