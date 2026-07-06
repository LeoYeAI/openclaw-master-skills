# agentwallex-openclaw

A ClawHub skill for AI agents to send crypto payments (USDC/USDT), check balances, and query transactions via AgentWallex across Ethereum, BSC, and Tron.

## Supported Chains & Tokens

| Chain | Mainnet | Sandbox (Testnet) | Tokens |
|-------|---------|-------------------|--------|
| Ethereum | Ethereum | Sepolia | USDC, USDT |
| BSC | BSC | BSC Testnet | USDC, USDT |
| Tron | Tron | Nile Testnet | USDT |

## Install

```bash
clawhub install agentwallex-openclaw
```

## What It Does

This skill provides agents with the ability to:

- **Zero-config setup** — Configure credentials through conversation, no env vars needed
- Check token balances across Ethereum, BSC, and Tron
- Send outbound USDC/USDT transfers to any address
- Query transaction status and confirmation details

## Setup

After installing, just tell your AI agent:

```
"Set up AgentWallex"
```

The agent will guide you through opening the [AgentWallex Dashboard](https://app.agentwallex.com), creating an API key, and saving your credentials locally. No config files or environment variables required.

See [SKILL.md](./SKILL.md) for full API reference, workflow examples, and troubleshooting.

## Documentation

- [AgentWallex Dashboard](https://app.agentwallex.com)
- [AgentWallex Docs](https://docs.agentwallex.com)
- [SKILL.md](./SKILL.md) — Full skill specification

## License

MIT
