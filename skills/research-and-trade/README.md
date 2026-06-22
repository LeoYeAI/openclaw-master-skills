# Research and Trade

Research a token and execute a trade only if risk assessment approves. Stops and reports if risk is too high.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/research-and-trade
```

Or via Clawhub:

```bash
npx clawhub@latest install research-and-trade
```

## When to use

Use this skill when:

- You want a **research-to-trade pipeline**: do due diligence and only trade if it passes risk checks.
- You prefer **automatic vetoes** for tokens or setups that are too risky.
- You want a **single command** that goes from "what is this token?" to "buy it if it looks good."

## Example prompts

- "Research this token address on Base and buy $1,000 worth only if it passes risk assessment."
- "Look into PEPE across Uniswap pools and execute a small test buy if risk is acceptable."
- "Do due diligence on this new token and don't trade if liquidity or risk looks bad."
