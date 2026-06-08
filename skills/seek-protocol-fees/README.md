# Seek Protocol Fees

Analyze TokenJar profitability and optionally execute a Firepit burn-and-claim. Defaults to preview-only mode unless explicitly asked to execute.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/seek-protocol-fees
```

Or via Clawhub:

```bash
npx clawhub@latest install seek-protocol-fees
```

## When to use

Use this skill when:

- You want to know if **TokenJar balances currently justify a profitable burn**.
- You need a **detailed profitability breakdown** vs. UNI burn cost.
- You may want the agent to **simulate or execute a Firepit burn-and-claim**.

## Example prompts

- "Is the TokenJar currently profitable enough to justify a Firepit burn? Show the math."
- "Simulate a Firepit burn-and-claim and report expected returns without executing."
- "If it's clearly profitable, execute a Firepit burn and show final balances."
