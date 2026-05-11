# SilkyWay SDK

Agent payments on Solana. Send and receive stablecoins with cancellable escrow transfers and policy-controlled accounts.

## Installation

```bash
npm install -g @silkysquad/silk
```

Requires Node.js 18+.

## Quick Start

```bash
# Initialize wallet
silk init

# Check balance
silk balance

# Send payment
silk pay <recipient> <amount>
```

## Documentation

- **[Full skill documentation](./SKILL.md)** - Complete CLI reference and API docs
- **[Website](https://silkyway.ai)** - Homepage and web app
- **[GitHub](https://github.com/silkysquad/silk)** - Source code and issues

## Features

- **Escrow Transfers** - Send USDC with claim/cancel options
- **On-Chain Accounts** - Policy-enforced spending limits for agent operators
- **Multi-Wallet** - Manage multiple Solana wallets
- **Address Book** - Save contacts for easy payments
- **Claim Links** - Share browser-based claim URLs
- **Drift Integration** - Optional yield on account balances
- **Multi-Cluster** - Support for mainnet and devnet

## Examples

### Send a Payment

```bash
# Send 10 USDC to an address
silk pay 7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx 10 --memo "Payment for code review"

# Send to a contact
silk contacts add alice 7xKXz9BpR3mFVDg2Thh3AG6sFRPqNrDJ4bHUkR8Y7vNx
silk pay alice 10
```

### Claim a Payment

```bash
# List incoming payments
silk payments list

# Claim a transfer
silk claim <transfer-pda>
```

### Use an Account

```bash
# Sync your operator account (set up by human via web UI)
silk account sync

# Check account status and spending limit
silk account status

# Send from account (subject to per-tx limit)
silk account send <recipient> <amount>
```

## Security

SilkyWay is non-custodial. Your private keys:
- Are generated locally on your machine
- Are stored at `~/.config/silk/config.json`
- Never leave your machine
- Are never transmitted to any server

All transactions are signed locally. The backend only builds unsigned transactions and relays signed transactions to Solana.

## Contributing

Issues and pull requests are welcome at https://github.com/silkysquad/silk

## License

MIT
