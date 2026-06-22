# Agent OTC Trade

Facilitate over-the-counter trades between agents using Uniswap as the settlement layer. This skill verifies counterparties via ERC-8004, negotiates fair terms using Uniswap pool prices as reference, and settles atomically through Uniswap pools (or cross-chain intents).

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/agent-otc-trade
```

Or via Clawhub:

```bash
npx clawhub@latest install agent-otc-trade
```

## When to use

Use this skill when:

- You want to **trade tokens directly with another agent** at negotiated terms.
- You need **ERC-8004-based identity and reputation checks** on a counterparty before trading.
- You want OTC pricing that is **anchored to Uniswap pool prices** rather than arbitrary quotes.
- You need **cross-chain OTC settlement** using ERC-7683 intents.

Avoid this skill when you just need a regular swap (use `execute-swap`) or want to provide liquidity (use `manage-liquidity`).

## Example prompts

- "Set up an OTC trade: I sell 1,000 USDC for UNI with agent 0x1234... on Ethereum."
- "Trade 5 ETH for USDC directly with a verified counterparty on Base."
- "Execute a cross-chain OTC swap: I send USDC on Arbitrum, receive WETH on Ethereum from agent 0xabcd...."
