# Cross-Chain Arbitrage

Find and execute cross-chain arbitrage: scan prices across chains, evaluate profitability after all costs, assess risk, and optionally execute. Supports scan-only mode.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/cross-chain-arbitrage
```

Or via Clawhub:

```bash
npx clawhub@latest install cross-chain-arbitrage
```

## When to use

Use this skill when:

- You want to **scan for price discrepancies** for a token across multiple Uniswap chains.
- You need to know whether **arbitrage is profitable after gas, bridge, and slippage costs**.
- You may want the agent to **execute profitable opportunities** or just report them (scan-only).

## Example prompts

- "Scan for cross-chain arbitrage opportunities for WETH across Ethereum, Arbitrum, and Base—do not execute, just report."
- "Identify and execute any clearly profitable cross-chain arbitrage for USDC with conservative assumptions."
- "Show me recent cross-chain arb opportunities for UNI and whether they’d have been profitable."
