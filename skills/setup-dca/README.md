# Setup DCA

Set up non-custodial dollar-cost averaging on Uniswap: recurring swaps, Gelato keeper automation, and monitoring.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/setup-dca
```

Or via Clawhub:

```bash
npx clawhub@latest install setup-dca
```

## When to use

Use this skill when:

- You want to **dollar-cost average** into a token over time using Uniswap.
- You prefer a **non-custodial setup** where you control funds at all times.
- You want **automated execution** (e.g., via Gelato) and monitoring for your DCA strategy.

## Example prompts

- "Set up a weekly DCA from USDC into WETH on Arbitrum for the next 6 months."
- "Create a daily DCA from USDC to UNI on Base with $100 per day."
- "Configure a DCA strategy into ETH from my stablecoin balance and show how to pause or stop it."
