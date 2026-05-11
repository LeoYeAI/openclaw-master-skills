# Self-Funding Setup

Set up a full self-funding agent: wallet, optional token + V4 pool, treasury management, ERC-8004 identity, and x402 configuration in one orchestrated workflow.

→ **[SKILL.md](SKILL.md)** — Full skill specification and workflow.

## Installation

Install into Claude Code or Cursor with:

```bash
npx skills add https://github.com/wpank/Agentic-Uniswap/tree/main/.ai/skills/self-funding-setup
```

Or via Clawhub:

```bash
npx clawhub@latest install self-funding-setup
```

## When to use

Use this skill when:

- You want to take an agent from **zero to self-funding** in one command.
- You need to coordinate **wallet provisioning, token launch (optional), treasury config, identity, and x402**.
- You want a **coherent self-funding setup** instead of configuring each piece manually.

## Example prompts

- "Set up a fully self-funding agent on Base, including a token and V4 pool, with conservative treasury rules."
- "Configure my existing agent to become self-funding using Uniswap fees and x402 payments."
- "Create a self-funding pipeline for a research agent that monetizes via Uniswap-based services."
