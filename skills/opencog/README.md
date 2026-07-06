# precog

OpenClaw skill for [PrecogMasterV8](https://precog.markets) prediction markets.

## Credentials and local state

This skill generates and stores a private key on your machine.

- **`~/.openclaw/.env`** — created on first `setup.mjs --generate`. Contains `PRIVATE_KEY=0x...`. This file is never printed or transmitted, but it controls a real wallet. Back it up; losing it means losing access to any funds in that wallet.
- **`PRIVATE_KEY`** env var — all trading scripts (`buy`, `sell`, `quote`, `positions`) require this key to be present. They read it from `~/.openclaw/.env` automatically.
- **No key is ever sent to any server.** All transactions are signed locally and broadcast directly to the RPC.

## Installation

```bash
cd ~/.openclaw/skills
git clone https://github.com/0xAstraea/opencog-basic precog
npm install
```

## Networks

| Network | Flag | Default? |
|---|---|---|
| Base Sepolia (testnet) | `--network sepolia` | **Yes** — safe to use, no real funds |
| Base Mainnet | `--network mainnet` | No — real funds, explicit opt-in required |

The default network is **Base Sepolia**. To use mainnet, pass `--network mainnet` to any script or set `PRECOG_NETWORK=mainnet` in your environment.

## What's included

- **Wallet**: Generate a local wallet, check address and balances
- **Markets**: List all open markets with current prices and status
- **Market detail**: Outcomes, probabilities, category, and resolution criteria for a specific market
- **Quotes**: Price trades before executing (always quote first)
- **Trading**: Buy and sell outcome shares with slippage protection
- **Positions**: View share holdings and net cost per market

See [SKILL.md](SKILL.md) for full documentation.
