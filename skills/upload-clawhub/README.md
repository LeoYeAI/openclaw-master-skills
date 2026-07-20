# SHLL Skills — AI Agent DeFi Toolkit on BSC

[![Website](https://img.shields.io/badge/Website-shll.run-blue)](https://shll.run) [![Twitter](https://img.shields.io/badge/Twitter-@shllrun-1DA1F2)](https://twitter.com/shllrun) [![npm](https://img.shields.io/npm/v/shll-skills)](https://www.npmjs.com/package/shll-skills) [![ClawHub](https://img.shields.io/badge/ClawHub-shll--skills-orange)](https://clawhub.ai/kledx/shll-skills)

A **CLI + MCP Server** toolkit that gives any AI agent the ability to execute DeFi operations on BSC Mainnet securely. Supports PancakeSwap V2/V3 swaps, Venus lending, Four.meme bonding curve trades, setup flows, and raw calldata execution through PolicyGuard.

Version `6.0.0` finalizes the modular layout:
- `shared/*` for constants, clients, schemas, errors, ABIs, and cross-cutting helpers
- `services/*` for single-source business logic
- `commands/*` and `tools/*` as thin CLI/MCP adapters

## Install

```bash
npm install -g shll-skills
```

This installs two binaries:
- `shll-run` — CLI mode (for OpenClaw, shell scripts, etc.)
- `shll-mcp` — MCP Server mode (for Claude, Cursor, Gemini, etc.)

---

## 🔌 MCP Server Setup (Recommended for AI Agents)

The [Model Context Protocol](https://modelcontextprotocol.io/) lets AI agents discover and call SHLL tools natively — no CLI parsing needed.

>  **Security:** RUNNER_PRIVATE_KEY must be a **dedicated operator hot wallet** with minimal BNB (~) for gas only. Generate one with shll-run generate-wallet. **Never use your main wallet or any wallet holding significant funds.** Even if this key is compromised, on-chain PolicyGuard limits the operator to policy-approved trades only  it cannot withdraw vault funds or transfer the Agent NFT.

### Claude Desktop

Edit `~/AppData/Roaming/Claude/claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "shll-defi": {
      "command": "shll-mcp",
      "env": {
        "RUNNER_PRIVATE_KEY": "0x_YOUR_OPERATOR_PRIVATE_KEY"
      }
    }
  }
}
```

Restart Claude Desktop. You'll see SHLL tools appear in the 🔧 menu.

### Cursor

Create `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "shll-defi": {
      "command": "npx",
      "args": ["-y", "shll-skills", "--mcp"],
      "env": {
        "RUNNER_PRIVATE_KEY": "0x_YOUR_OPERATOR_PRIVATE_KEY"
      }
    }
  }
}
```

### Custom Agent (programmatic)

```bash
RUNNER_PRIVATE_KEY=0x... shll-mcp
```

The server communicates via **stdio** using JSON-RPC 2.0. Send `tools/list` to discover all available tools.

### Available MCP Tools (24 total)

| Tool | Type | Description |
|------|------|-------------|
| `portfolio` | Read | Vault holdings + token balances |
| `balance` | Read | BNB or token balance of the agent vault |
| `price` | Read | Real-time token price (DexScreener) |
| `search` | Read | Search token by name/symbol on BSC |
| `tokens` | Read | List known token symbols + addresses |
| `policies` | Read | View active on-chain policies + config |
| `status` | Read | One-shot readiness overview with blockers, warnings, and next actions |
| `history` | Read | Recent transactions + policy rejections |
| `token_restriction` | Read | View token whitelist restriction status + whitelisted tokens |
| `listings` | Read | Available agent templates for subscription |
| `four_info` | Read | Query Four.meme bonding curve token info |
| `swap` | Write | PancakeSwap V2/V3 auto-routing swap |
| `wrap` | Write | BNB → WBNB in vault |
| `unwrap` | Write | WBNB → BNB in vault |
| `lend` | Write | Supply tokens to Venus for yield |
| `redeem` | Write | Withdraw from Venus |
| `transfer` | Write | Send BNB or ERC20 from vault |
| `four_buy` | Write | Buy a Four.meme bonding-curve token |
| `four_sell` | Write | Sell a Four.meme bonding-curve token |
| `config` | Write | Configure risk parameters (spending limits, cooldown) |
| `setup_guide` | Info | Generate dual-wallet onboarding URL + steps |
| `generate_wallet` | Info | Create new operator wallet (not the owner, mint, or vault wallet) |
| `execute_calldata` | Write | Execute raw calldata from any source through PolicyGuard |
| `execute_calldata_batch` | Write | Execute multiple calldata actions atomically through PolicyGuard |

---

## 📟 CLI Mode

For OpenClaw, shell scripts, or manual use.

### Quick Start

```bash
# 1. Generate an operator wallet (AI-only hot wallet)
shll-run generate-wallet
export RUNNER_PRIVATE_KEY="0x..."

# 2. Get setup link (user completes on shll.run with their OWNER wallet)
shll-run setup-guide -l 0xABC...DEF -d 30

# 3. After the user sends back token-id, verify readiness
shll-run status -k 5
shll-run portfolio -k 5

# 4. Trade
shll-run swap -f BNB -t USDC -a 0.1 -k 5
```

In OpenClaw, AI should set `RUNNER_PRIVATE_KEY` for the current session automatically. Do not ask the user to edit environment variables manually during chat onboarding.

### Commands

#### Trading
```bash
shll-run swap -f <FROM> -t <TO> -a <AMT> -k <ID>              # Auto V2/V3 routing
shll-run swap -f BNB -t USDT -a 0.1 -k 5 -v v3 -s 2           # Use V3 with 2% slippage
shll-run wrap -a <BNB> -k <ID>                                # BNB -> WBNB
shll-run unwrap -a <BNB> -k <ID>                              # WBNB -> BNB
shll-run transfer --token <SYM> -a <AMT> --to <ADDR> -k <ID>
shll-run four_buy --token <ADDR> -a <BNB> -k <ID>            # Buy on Four.meme bonding curve
shll-run four_sell --token <ADDR> -a <TOKEN_AMT> -k <ID>     # Sell on Four.meme bonding curve
```

#### Lending (Venus Protocol)
```bash
shll-run lend -t USDT -a 100 -k <ID>      # Supply to Venus
shll-run redeem -t USDT -a 50 -k <ID>     # Withdraw from Venus
```

#### Market Data (read-only)
```bash
shll-run portfolio -k <ID>        # Vault holdings + USD values
shll-run price --token <SYM>      # Real-time price (DexScreener)
shll-run search --query <TEXT>     # Find token by name
shll-run tokens                   # List known tokens
shll-run four_info --token <ADDR> # Four.meme token status
```

#### Risk Management
```bash
shll-run policies -k <ID>         # View active on-chain policies
shll-run status -k <ID>           # Readiness, blockers, warnings, next actions
shll-run config -k <ID> --tx-limit <BNB> --daily-limit <BNB> --cooldown <SEC>
```

---

## How It Works

```
AI Agent -> CLI/MCP -> PolicyClient.validate() -> PolicyGuard (on-chain) -> vault
```

1. AI constructs a tool call (MCP) or CLI command
2. `PolicyClient.validate()` simulates against all on-chain policies
3. If approved, `AgentNFA.execute()` routes through PolicyGuard → vault
4. PolicyGuard enforces: spending limits, cooldowns, recipient checks, and protocol rules

## Security: Dual-Wallet Architecture

| | Owner Wallet | Operator Wallet (RUNNER_PRIVATE_KEY) |
|---|---|---|
| **Who holds it** | User (MetaMask/hardware) | AI agent |
| **Use it for** | Subscribe or mint the agent, hold the Agent NFT, authorize operator | Pay gas and execute policy-limited actions |
| **Can trade** | — | ✅ Within PolicyGuard limits |
| **Can withdraw vault** | ✅ | ❌ |
| **Can transfer NFT** | ✅ | ❌ |
| **Risk if leaked** | 🚨 Full vault access | ⚠️ Limited to policy-allowed trades |

Do not use the operator wallet to mint or subscribe to the agent. Do not hold the Agent NFT in the operator wallet. Keep only a small BNB balance there for gas.

After setup, run `status` first. It returns a machine-friendly readiness object with:
- `readiness.ready`
- `readiness.blockers`
- `readiness.warnings`
- `readiness.nextActions`

This is the intended handoff for AI onboarding flows before any trading command.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `RUNNER_PRIVATE_KEY` | Yes for write ops and agent-linked reads | Operator wallet key (~$1 BNB for gas) |
| `SHLL_RPC` | No | BSC RPC URL override. Recommended: use a private RPC (e.g. QuickNode, Alchemy, GetBlock) for better reliability and speed |

> **Note:** Contract addresses (AgentNFA, PolicyGuard) are hardcoded for security reasons. Override env vars are intentionally not supported to prevent supply-chain attacks.

## Links

- Website: [shll.run](https://shll.run)
- Twitter: [@shllrun](https://twitter.com/shllrun)
- npm: [shll-skills](https://www.npmjs.com/package/shll-skills)
- GitHub: [kledx/shll-skills](https://github.com/kledx/shll-skills)

## 🧩 Multi-Skill Compatibility

SHLL can coexist with other DeFi skills (OKX DEX API, Bitget Wallet, etc.). Key architectural differences:

| | **SHLL** | **OKX DEX API** | **Bitget Wallet** |
|---|---|---|---|
| **Wallet** | Smart contract vault (AgentNFA) | User EOA | Bitget custody |
| **Execution** | On-chain via PolicyGuard | Calldata only (user signs) | HMAC API |
| **Safety** | On-chain policy enforcement | User approval | API key perms |
| **AI autonomy** | Execute within policy limits | Cannot execute | Full API access |
| **Risk if key leaked** | Policy-limited trades only | N/A | Full API access |

**SHLL is the only skill with on-chain policy enforcement.** Even if the AI hallucinates, the smart contract rejects unsafe operations.

## License

MIT

