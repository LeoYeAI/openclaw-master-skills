# Full LP Workflow

End-to-end LP workflow: find an opportunity, design a strategy, assess risk, execute any needed swaps, enter the position, and report portfolio impact.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/full-lp-workflow
```

Or via Clawhub:

```bash
npx clawhub@latest install full-lp-workflow
```

## When to use

Use this skill when:

- You want a **fully-managed LP workflow** from opportunity discovery to position entry.
- You have capital ready and want the agent to **scan, design, risk-check, and execute**.
- You prefer a **single orchestrated flow** instead of stitching together many skills manually.

## Example prompts

- "With $10,000 USDC and moderate risk tolerance, run the full LP workflow and open the best position for me."
- "Find the best LP opportunity for WETH on Arbitrum and enter it end to end."
- "Use the full LP workflow to deploy a diversified LP strategy across two chains."
