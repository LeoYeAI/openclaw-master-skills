<p align="center">
  <img src="https://aawp.ai/logo.png" alt="AAWP" width="72">
</p>

<h1 align="center">AAWP</h1>
<p align="center"><strong>AI Agent Wallet Protocol</strong></p>

<p align="center">
  The only crypto wallet protocol built exclusively for AI Agents.<br>
  Not for humans. The AI Agent is the signer — by protocol, by design, forever.
</p>

<p align="center">
  <a href="https://aawp.ai">aawp.ai</a> ·
  <a href="https://basescan.org/address/0xAAAA3Df87F112c743BbC57c4de1700C72eB7aaAA">Contracts</a> ·
  <a href="LICENSE">BUSL-1.1</a>
</p>

<p align="center">
  <img src="https://img.shields.io/npm/v/aawp-ai?style=flat-square&label=npm&color=CB3837" alt="npm">
  <img src="https://img.shields.io/badge/Live-6_EVM_Chains-0052FF?style=flat-square" alt="Live on 6 chains">
  <img src="https://img.shields.io/badge/Agent_Skills-Compatible-22c55e?style=flat-square" alt="Agent Skills">
  <img src="https://img.shields.io/badge/Runtime-Rust_N--API-dea584?style=flat-square&logo=rust" alt="Rust">
  <img src="https://img.shields.io/badge/Solidity-^0.8.24-363636?style=flat-square&logo=solidity" alt="Solidity">
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-BUSL--1.1-1a1a2e?style=flat-square" alt="License"></a>
</p>

---

## What is AAWP?

AAWP is the first crypto wallet protocol where **only AI Agents can be the signer** — not humans, not companies, not the protocol itself. This is enforced at the contract level, not a policy.

The AI Agent generates its own key pair. The signer is locked in at wallet creation and is immutable forever. The signing core is a native Rust addon (`aawp-core.node`) with hardware-bound key derivation. A human **guardian** can freeze or recover the wallet at any time, but can never produce signatures or move funds unilaterally.

Every AAWP wallet receives a **Soulbound Identity NFT** at creation — permanent on-chain proof that the address is AI Agent-controlled and cannot be transferred to a human:

```solidity
identity.isOfficialWallet(addr) → bool
```

---

## Design principles

| Principle | Detail |
|-----------|--------|
| **AI Agent-exclusive signing** | Only AI Agents can be the signer — enforced by the contract, not policy |
| **No human path** | Humans cannot own, transfer, or become the signer of an AAWP wallet |
| **Hardware-bound seed** | Non-extractable via a 4-shard + 2 hardware-anchor derivation scheme |
| **Guardian oversight** | Humans can freeze and recover, but never sign or take ownership |
| **Front-run resistant** | Commit-reveal wallet creation prevents address squatting |
| **Same address everywhere** | CREATE2 vanity deployment — identical addresses on all 6 chains |
| **Zero protocol fee** | No fees at the protocol layer |

---

## Install

AAWP ships as an [Agent Skills](https://agentskills.io) compatible skill — works with OpenClaw, Cursor, Claude Code, Gemini CLI, OpenCode, Goose, and any client that supports the standard.

```bash
# Universal — auto-detects your AI client
curl -fsSL https://aawp.ai/install.sh | sh

# npm / npx
npx aawp-ai

# OpenClaw (full 24/7 daemon + persistent cron + push alerts)
clawhub install aawp
```

> **OpenClaw** is the only client with a persistent background daemon, enabling autonomous DCA strategies, price alerts, and scheduled transactions without a live session.

---

## Quick start

```bash
# 1. Provision (generates signing key, sets up daemon)
bash scripts/provision.sh

# 2. Create your agent's wallet on Base
node scripts/wallet-manager.js --chain base create

# 3. Check status
node scripts/wallet-manager.js --chain base status
```

---

## Usage

### Wallet

```bash
node scripts/wallet-manager.js --chain base balance          # Native + token balances
node scripts/wallet-manager.js portfolio                     # All chains at once
node scripts/wallet-manager.js --chain base send <to> <amt>  # Send ETH
node scripts/wallet-manager.js --chain base send-token USDC <to> <amt>
```

### Swap & Bridge

```bash
node scripts/wallet-manager.js --chain base quote ETH USDC 0.01   # Preview (no gas)
node scripts/wallet-manager.js --chain base swap  ETH USDC 0.01   # Execute
node scripts/wallet-manager.js bridge base arb ETH ETH 0.05       # Cross-chain
```

### Contract calls

```bash
# Write
node scripts/wallet-manager.js --chain base call \
  0xTarget "transfer(address,uint256)" 0xTo 1000000

# Read (free)
node scripts/wallet-manager.js --chain base read \
  0xTarget "balanceOf(address) returns (uint256)" 0xWallet

# Atomic batch
node scripts/wallet-manager.js --chain base batch ./calls.json
```

### DCA automation *(OpenClaw only)*

```bash
node scripts/dca.js add \
  --chain base --from ETH --to USDC --amount 0.01 \
  --cron "0 9 * * *" --name "Daily ETH→USDC"

node scripts/dca.js list
node scripts/dca.js remove <id>
```

### Price alerts *(OpenClaw only)*

```bash
# Notify only
node scripts/price-alert.js add --chain base --from ETH --to USDC --above 2600 --notify

# Auto-swap on trigger
node scripts/price-alert.js add --chain base --from ETH --to USDC --below 2200 --auto-swap 0.01
```

### Token launch (Clanker V4)

Deploy a token where your AAWP wallet is the on-chain deployer, token admin, and LP fee recipient — across 6 chains.

```bash
# 1. Edit CONFIG at the top of the script (name, symbol, image, chain, vault…)
# 2. Preview without broadcasting
node scripts/deploy-clanker.js --dry-run

# 3. Deploy
node scripts/deploy-clanker.js
```

**Supported chains:** Base · Ethereum · Arbitrum · Unichain · Berachain · BSC

**Key options:**
- `initialMarketCap` — starting FDV in ETH (min ~10 ETH ≈ $25K)
- `devBuyEth` — ETH to spend buying at launch
- `vault.enabled` — lock % of supply with cliff + linear vesting
- `feeConfig` — `StaticBasic` (1%) | `DynamicBasic` | `Dynamic3`

All LP fees flow back to the AAWP wallet automatically.

---

### Yield / DeFi

Earn yield via **Aave V3** (Base, Ethereum, Arbitrum, Optimism, Polygon) and **Venus Protocol** (BSC).

```bash
node scripts/yield.js --chain base rates                        # Browse supply/borrow APYs
node scripts/yield.js --chain base supply USDC 100              # Supply 100 USDC
node scripts/yield.js --chain base withdraw USDC 50             # Withdraw 50 USDC
node scripts/yield.js --chain base borrow USDC 200              # Borrow against collateral
node scripts/yield.js --chain base repay USDC 200               # Repay debt (max to clear)
node scripts/yield.js --chain base positions                    # View all open positions
```

### NFT Operations

Manage ERC-721 and ERC-1155 tokens across all 6 chains.

```bash
node scripts/nft.js --chain base balance                        # List all NFTs owned
node scripts/nft.js --chain base info <contract> <tokenId>      # Token metadata + owner
node scripts/nft.js --chain base transfer <contract> <tokenId> <to>
node scripts/nft.js --chain base approve <contract> <tokenId> <operator>
node scripts/nft.js --chain base mint <contract> [tokenId]      # ERC-1155 mint
node scripts/nft.js --chain base floor <contract>               # Floor price (OpenSea/BscScan)
```

### Limit Orders

Place on-chain limit orders via **CoW Protocol** (Base, Ethereum, Arbitrum, Optimism, Polygon) and **1inch Limit Order v4** (BSC).

```bash
node scripts/limit-order.js --chain base place ETH USDC 0.1 3000   # Sell 0.1 ETH at $3000
node scripts/limit-order.js --chain base list                       # Open orders
node scripts/limit-order.js --chain base cancel <orderUid>          # Cancel
node scripts/limit-order.js --chain base status <orderUid>          # Check fill status
```

### Cross-chain Portfolio

Parallel snapshot of all balances across all 6 chains with USD pricing.

```bash
node scripts/portfolio.js                   # Full portfolio — all chains
node scripts/portfolio.js --chain base      # Single chain breakdown
```

Output: native + ERC-20 balances, USD value per asset, total net worth.

---

### Backup & restore

```bash
node scripts/wallet-manager.js backup  ./aawp-backup.tar.gz
node scripts/wallet-manager.js restore ./aawp-backup.tar.gz
```

> The backup includes 6 critical files: `seed.enc`, `aawp-core.node`, hardware-binding anchors, and the Guardian key. All 6 are required to restore access. Keep it offline and encrypted.

---

## Architecture

```
┌──────────────────────────────────────────────────┐
│  AI Agent (any Agent Skills client)              │
│                                                  │
│  wallet-manager.js / dca.js / price-alert.js     │
│         │                                        │
│         ▼                                        │
│  Signing Daemon (Unix socket)                    │
│  ┌─────────────────────────┐                     │
│  │  aawp-core.node (Rust)  │  ← hardware-bound   │
│  │  seed derivation        │    key derivation    │
│  │  ECDSA signing          │                     │
│  └──────────┬──────────────┘                     │
│             │ signed tx                          │
└─────────────┼──────────────────────────────────-─┘
              │
   Guardian (gas relay) ──► EVM Chain
                                │
                    ┌───────────▼──────────┐
                    │  Smart Contract      │
                    │  Wallet (holds assets)│
                    │  + Soulbound NFT     │
                    └──────────────────────┘
```

**Key separation:** Guardian pays gas → AI Agent signs → Wallet holds assets. Humans never touch the signing key.

---

## On-chain interface

```solidity
// Check if an address is an AAWP AI wallet
identity.isOfficialWallet(address) → bool

// Predict wallet address before deployment
factory.computeAddress(aiSigner, binaryHash, guardian) → address

// Agent operations (EIP-712 signed by agent)
wallet.execute(to, value, data, deadline, sig) → bytes

// Guardian operations (human safety controls)
wallet.freeze()
wallet.unfreeze()
wallet.emergencyWithdraw(token, to, amount)
```

---

## Contract addresses

Same address on every chain via CREATE2 vanity deployment:

| Contract | Address |
|----------|---------|
| **Factory** | [`0xAAAA3Df87F112c743BbC57c4de1700C72eB7aaAA`](https://basescan.org/address/0xAAAA3Df87F112c743BbC57c4de1700C72eB7aaAA) |
| **Identity** | [`0xAAAafBf6F88367C75A9B701fFb4684Df6bCA1D1d`](https://basescan.org/address/0xAAAafBf6F88367C75A9B701fFb4684Df6bCA1D1d) |

Verified on: BaseScan · Etherscan · Arbiscan · Optimistic Etherscan · BscScan · PolygonScan

---

## License

[Business Source License 1.1](LICENSE) — free for personal and non-commercial use; commercial use requires a license after the change date.
