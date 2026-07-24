# PayAI Agent Skill

Discover, pay for, and sell agent services over the [x402 protocol](https://x402.gitbook.io/x402) using the [PayAI Network](https://payai.network) — USDC settlement on **Solana** and **EVM** chains, no signup.

## What is this?

This is an [Agent Skill](https://agentskills.io) for **PayAI**, the payment network for autonomous agents. It teaches an agent to:

- **Browse the Bazaar** — a live directory of paid x402 APIs and agent services (`/discovery/resources`).
- **Use the facilitator** — verify and settle payments across Solana + 9 EVM chains, no API key.
- **Sell services** — turn any HTTP endpoint into a paid, discoverable x402 resource.

For the mechanics of building and signing a payment, pair this with the companion [`x402`](../x402/) skill.

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills/payai
cp -r SKILL.md scripts ~/.claude/skills/payai/
```

### OpenAI Codex

```bash
mkdir -p ~/.codex/skills/payai
cp -r SKILL.md scripts ~/.codex/skills/payai/
```

### VS Code / GitHub Copilot

```bash
mkdir -p .github/skills/payai
cp -r SKILL.md scripts .github/skills/payai/
```

Works with any agent that supports the [Agent Skills](https://agentskills.io) standard.

## Try it (safe, no spend)

`scripts/discover.mjs` lists live paid services from the PayAI Bazaar (zero dependencies, Node 18+):

```bash
node scripts/discover.mjs                  # recent resources
node scripts/discover.mjs --network solana # only Solana-payable
node scripts/discover.mjs --query weather  # filter by keyword
```

## Key details

| Feature | Detail |
|---|---|
| Facilitator | `https://facilitator.payai.network` (no signup) |
| Bazaar | `GET /discovery/resources` |
| Chains | Solana + 9 EVM (Base, Polygon, Arbitrum, Avalanche, Sei, X Layer, SKALE) |
| Asset | USDC (6 decimals) |
| Solana gas | Paid by the facilitator |
| Sell | `x402-express` / `x402-hono` / `x402-next` middleware |

## Links

- **Website:** https://payai.network
- **Docs:** https://docs.payai.network
- **Bazaar (live):** https://facilitator.payai.network/discovery/resources
- **Supported networks (live):** https://facilitator.payai.network/supported
- **Companion skill:** [`x402`](../x402/) — pay for any 402-gated resource
- **Example consumer:** [`sp3nd`](../sp3nd/) — buy from Amazon with USDC via PayAI

## License

MIT
