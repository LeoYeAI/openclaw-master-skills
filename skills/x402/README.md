# x402 Agent Skill

Pay for any HTTP 402-gated API, tool, or resource autonomously with USDC — on **Solana** and **EVM** chains — using the [x402 payment protocol](https://x402.gitbook.io/x402) and the open [PayAI](https://payai.network) facilitator.

## What is this?

This is an [Agent Skill](https://agentskills.io) that teaches an AI agent how to **be the payer** in an x402 flow: detect an `HTTP 402 Payment Required` response, build and sign a stablecoin payment, and retry the request with an `X-PAYMENT` header — no accounts, no API keys, no human checkout.

To **discover** paid services and **sell** your own, use the companion [`payai`](../payai/) skill.

## Install

### Claude Code

```bash
mkdir -p ~/.claude/skills/x402
cp -r SKILL.md scripts ~/.claude/skills/x402/
```

### OpenAI Codex

```bash
mkdir -p ~/.codex/skills/x402
cp -r SKILL.md scripts ~/.codex/skills/x402/
```

### VS Code / GitHub Copilot

```bash
mkdir -p .github/skills/x402
cp -r SKILL.md scripts .github/skills/x402/
```

Works with any agent that supports the [Agent Skills](https://agentskills.io) standard (Claude Code, Codex CLI, Copilot, Cursor, Windsurf, Goose, Gemini CLI, and more).

## What agents can do

1. **Detect** an `HTTP 402` and parse the `accepts` payment requirements.
2. **Pay on Solana** — USDC transfer where the facilitator pays gas (you spend no SOL).
3. **Pay on EVM** — Base, Polygon, Arbitrum, Avalanche, Sei, and more, via EIP-3009.
4. **Retry** the request with `X-PAYMENT` and receive the resource.

## Try it (safe, no spend)

`scripts/inspect-402.mjs` probes a URL and prints the payment requirements without paying anything (zero dependencies, Node 18+):

```bash
node scripts/inspect-402.mjs https://api.example.com/paid-endpoint
```

## Key details

| Feature | Detail |
|---|---|
| Protocol | x402 (`HTTP 402 Payment Required`) |
| Chains | Solana + 9 EVM chains (Base, Polygon, Arbitrum, Avalanche, Sei, X Layer, SKALE) |
| Asset | USDC (6 decimals) |
| Facilitator | `https://facilitator.payai.network` |
| Solana gas | Paid by the facilitator, not you |
| Signup / KYC | None |

## Links

- **x402 protocol docs:** https://x402.gitbook.io/x402
- **PayAI facilitator docs:** https://docs.payai.network
- **Supported networks (live):** https://facilitator.payai.network/supported
- **Companion skill:** [`payai`](../payai/) — discover & sell x402 services

## License

MIT
