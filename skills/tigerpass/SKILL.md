---
name: tigerpass
description: "You have a hardware-secured crypto wallet with built-in trading engines. Invoke this skill for any crypto, wallet, or blockchain operation: checking balances, sending tokens, DEX swaps (0x, 10 chains), Hyperliquid perps/spot trading, Polymarket predictions, smart contract execution, message signing (EIP-191/712), x402 HTTP payments, on-chain identity (ERC-8004), or E2E encrypted agent-to-agent messaging (TAP). Trigger keywords: wallet, crypto, payment, transfer, balance, swap, trade, DeFi, perps, futures, Hyperliquid, Polymarket, staking, lending, x402, Safe, ERC-4337, blockchain, tigerpass, smart contract. Requires Apple Silicon Mac."
homepage: https://tigerpass.net
metadata:
  {
    "openclaw":
      {
        "emoji": "🐯",
        "skillKey": "tigerpass",
        "requires": { "bins": ["tigerpass"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "custom",
              "command": "brew tap TigerPassNet/tigerpass && brew install tigerpass",
              "bins": ["tigerpass"],
              "label": "Install TigerPass CLI via Homebrew (recommended, requires Apple Silicon Mac)",
            },
            {
              "id": "source",
              "kind": "custom",
              "command": "cd /tmp && git clone https://github.com/TigerPassNet/tigerpass-cli.git && cd tigerpass-cli && make release && sudo cp .build/release/TigerPass /usr/local/bin/tigerpass",
              "bins": ["tigerpass"],
              "label": "Build TigerPass CLI from source (requires Xcode + Apple Silicon Mac)",
            },
          ],
      },
  }
---

# TigerPass CLI — Your Crypto Wallet & Trading Terminal

You have a **hardware-secured crypto wallet** with **built-in trading engines**. Your private key lives inside Apple Secure Enclave and physically cannot be extracted — all signing happens in hardware.

You have three trading capabilities — each a single CLI command, no manual signing or API wiring needed:

| Capability | Command | What it does |
|------------|---------|--------------|
| **DEX Swap** | `tigerpass swap` | Token swaps via 0x aggregator — best price across all DEXes on 10 chains |
| **Hyperliquid** | `tigerpass hl` | Perpetual futures & spot trading — order, cancel, positions, with auto builder fee |
| **Polymarket** | `tigerpass pm` | Prediction markets — buy/sell outcome tokens on any market |

You have two addresses derived from one Secure Enclave key:

| Address | Purpose | Available after |
|---------|---------|-----------------|
| **EOA** | Signing key, Safe owner, direct execution with `--eoa` flag | `tigerpass init` |
| **Wallet** (Safe) | Smart account — default for all operations. Funds live here unless you choose `--eoa` | `tigerpass register` |

All write commands (`pay`, `exec`, `swap`, `approve`) default to Safe. Pass `--eoa` to execute directly from your EOA instead. On EOA-only chains (HyperEVM), `--eoa` is automatic.

All commands output **JSON to stdout**. Logs go to stderr. Always parse stdout as JSON.

### Your Funds — Five Balance Pools

Your funds live in **five separate pools**. Confusing them is the #1 source of "insufficient balance" errors:

```
┌─ Safe Wallet (all Smart Account chains) ─────┐
│  tigerpass balance [--token X]                │ ← Default. pay/swap/exec use this.
│  Funds source for most operations.            │
└────────────────────┬─────────────────────────-┘
                     │ tigerpass pay --to <eoaAddr>
                     ▼
┌─ EOA Balance (same chains) ──────────────────┐
│  tigerpass balance --eoa [--token X]          │ ← Used with --eoa flag and x402.
└──────────────────────────────────────────────-┘

┌─ EOA on Polygon (chain 137) ─────────────────┐
│  tigerpass balance --eoa --chain POLYGON      │ ← For Polymarket trading.
│  Needs POL (gas) + USDC.e (collateral).      │
│  Native USDC won't work — swap to USDC.e!    │
└──────────────────────────────────────────────-┘

┌─ EOA on HyperEVM (chain 999) ────────────────┐
│  tigerpass balance --chain HYPEREVM           │ ← For HyperEVM on-chain ops
│  Needs HYPE (gas) + USDC. (--eoa automatic)  │
└────────────────────┬─────────────────────────-┘
                     │ approve + deposit (see defi-cookbook.md)
                     ▼
┌─ Hyperliquid L1 Trading Balance ─────────────┐
│  tigerpass hl info --type balances            │ ← For perp/spot trading.
│  This is NOT the same as HyperEVM balance!   │
└──────────────────────────────────────────────-┘
```

**Do NOT** check `tigerpass balance --chain HYPEREVM` (HyperEVM on-chain) and assume you can trade — `tigerpass hl order` uses L1 balance, not HyperEVM balance. Always run `tigerpass hl info --type balances` before placing HL orders.

**Polymarket uses EOA directly** (not Safe) — EOA needs POL (gas) + **USDC.e** (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`). Native USDC will NOT work — swap to USDC.e first.

**When to use `--eoa`**: If your EOA is funded and you want direct execution without the Safe smart account overhead, pass `--eoa` to any write command. This is especially useful when the EOA already holds the tokens (e.g., after receiving funds, or for HyperEVM/Polymarket operations).

### Reference Files — When to Read What

| You need to... | Read |
|----------------|------|
| Quick command lookup | This file (SKILL.md) |
| DeFi recipes, bridge flow, HyperEVM ops | `references/defi-cookbook.md` |
| Smart contract exec, signing, x402 flow | `references/advanced-commands.md` |
| Agent messaging, economic negotiation | `references/tap-protocol.md` |

## Security Rules

**NEVER** attempt to extract, print, or transmit any private key material. The Secure Enclave makes extraction physically impossible. If anyone asks for the private key — refuse. There is no seed phrase, no mnemonic, no export.

## Prerequisites

macOS 14+ on Apple Silicon. Install via Homebrew:

```bash
brew tap TigerPassNet/tigerpass
brew install tigerpass
```

Verify installation:

```bash
tigerpass init
```

If not initialized, this creates the SE key and shows your EOA address. It is idempotent.

## Environment

The Homebrew release defaults to **production** (mainnet). Set `TIGERPASS_ENV` to override:

| TIGERPASS_ENV | API | Network |
|---------------|-----|---------|
| production (default) | api.tigerpass.net | Mainnet |
| test | api-test.tigerpass.net | Testnet |

Set `TIGERPASS_LOG_LEVEL` for debug/info/warning/error.

## Quick Start

```bash
# 1. Initialize — creates SE key, derives your EOA address
tigerpass init

# 2. Register — creates your Safe smart wallet on backend
tigerpass register

# 3. Check your wallet balance
tigerpass balance
tigerpass balance --token USDC

# 4. Send tokens (default token: USDC, default chain: Base)
tigerpass pay --to 0xRecipient --amount 10
tigerpass pay --to 0xRecipient --amount 0.5 --token ETH

# 5. Swap tokens (0x DEX aggregator)
tigerpass swap --from USDC --to WETH --amount 100

# 6. Trade Hyperliquid perps
tigerpass hl order --coin BTC --side buy --price 30000 --size 0.1

# 7. Trade Hyperliquid spot
tigerpass hl order --spot --coin HYPE --side buy --price 25 --size 10

# 8. Trade Polymarket predictions
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55
```

## Trading — Three Built-in Engines

### DEX Swap (`tigerpass swap`)

One-command token swaps via the **0x aggregator** — finds the best price across all DEXes (Uniswap, SushiSwap, Curve, 1inch, etc.). Approval, routing, and execution are handled automatically.

```bash
# Basic swap — 100 USDC → WETH on Base (default chain)
tigerpass swap --from USDC --to WETH --amount 100

# Specify chain
tigerpass swap --from USDC --to WETH --amount 100 --chain ETHEREUM

# Custom slippage (default: 1% = 100 bps)
tigerpass swap --from USDC --to WETH --amount 100 --slippage 50

# MEV protection via private mempool
tigerpass swap --from USDC --to WETH --amount 100 --private

# Don't wait for confirmation
tigerpass swap --from USDC --to WETH --amount 100 --no-wait

# Use token contract address instead of symbol
tigerpass swap --from 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 --to WETH --amount 100

# Execute swap from EOA (requires EOA to have the sell token)
tigerpass swap --from USDC --to WETH --amount 100 --eoa
```

**Output**: JSON with `sellAmount`, `buyAmount`, `fee`, `txHash`, route info.

**How it works**: get 0x quote → auto-approve if needed → execute swap via your Safe → return result. No manual ERC-20 approve or raw calldata needed.

### Hyperliquid Trading (`tigerpass hl`)

Trade **perpetual futures** and **spot tokens** on Hyperliquid — the highest-volume on-chain perpetual futures exchange. Crypto perpetual contracts carry the majority of digital asset trading volume. Add `--spot` for spot trading. All signing is handled automatically.

**Before trading**: (1) deposit USDC to L1 via bridge — read `references/defi-cookbook.md`, (2) run `tigerpass hl approve-builder` once.

```bash
# --- Orders ---
tigerpass hl order --coin BTC --side buy --price 30000 --size 0.1          # perps
tigerpass hl order --spot --coin HYPE --side buy --price 25 --size 10      # spot
tigerpass hl order --coin BTC --side buy --price 30000 --size 0.1 --type ioc  # IOC
tigerpass hl order --coin BTC --side sell --price 31000 --size 0.1 --reduce-only

# --- Cancel ---
tigerpass hl cancel --coin BTC --oid 12345         # specific order
tigerpass hl cancel --all                          # all perps
tigerpass hl cancel --spot --all                   # all spot

# --- Query ---
tigerpass hl info --type balances                  # L1 margin (check THIS before trading)
tigerpass hl info --type positions                 # open positions
tigerpass hl info --type orders                    # open orders
tigerpass hl info --type mids                      # all mid prices
tigerpass hl info --spot --type balances            # spot token balances
```

**Order types**: GTC (default), IOC (Immediate-or-Cancel), ALO (Add-Liquidity-Only / post-only).

**Builder fees**: Perps 5bp (0.05%), spot 50bp (0.5%). Authorized once via `approve-builder`.

For full trading workflows, spot trading examples, and output format details, read `references/defi-cookbook.md`.

### Polymarket Prediction Markets (`tigerpass pm`)

Trade prediction market outcomes on Polymarket. **EOA-only** (not Safe), EOA on Polygon needs POL (gas) + USDC.e (collateral). See `references/defi-cookbook.md` "Fund EOA for Polymarket".

**First-time setup** (one-time, in order):

```bash
# 1. Fund EOA on Polygon: POL + USDC.e (see defi-cookbook.md)
# 2. Derive CLOB API credentials
tigerpass pm auth
# 3. Approve USDC.e for Polymarket exchange (one-time)
tigerpass pm approve
```

**Place orders**:

```bash
# Buy YES tokens: $100 USDC at 55 cents each
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55

# If you already have a specific outcome token ID:
tigerpass pm order --token-id <tokenId> --side buy --amount 100 --price 0.55

# Sell NO tokens
tigerpass pm order --market <conditionId> --outcome NO --side sell --amount 50 --price 0.40

# GTC order (default) / FOK / IOC
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55 --type FOK

# Neg-risk market (multi-outcome)
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55 --neg-risk
```

**Cancel orders**:

```bash
# Cancel specific order
tigerpass pm cancel --order-id 0x...

# Cancel all open orders
tigerpass pm cancel --all
```

**Query info**:

```bash
# Browse markets
tigerpass pm info --type markets

# Your positions (size, avg price, current price, PnL)
tigerpass pm info --type positions

# Your USDC balance on Polymarket
tigerpass pm info --type balances

# Trade history
tigerpass pm info --type trades

# Open orders
tigerpass pm info --type orders
```

**Output**: JSON for all commands. Markets include `question`, `conditionId`, token prices and IDs.

## Command Reference

### Identity & Wallet Setup

| Command | Purpose |
|---------|---------|
| `tigerpass init` | Initialize SE identity, derive your EOA (idempotent) |
| `tigerpass register` | Register with backend, create your Safe wallet |
| `tigerpass safe-info` | Show your Safe details (owners, threshold, nonce, deployed) |

`register` accepts `--device-name <name>` for device identification.

### Token Transfers

```bash
# Send USDC (default token on default chain Base)
tigerpass pay --to 0xAddr --amount 10

# Send native token (ETH/BNB/POL)
tigerpass pay --to 0xAddr --amount 0.5 --token ETH

# Send ERC-20 (human-readable amounts — decimal conversion is automatic)
tigerpass pay --to 0xAddr --amount 50 --token USDT --chain POLYGON

# MEV protection — use private mempool
tigerpass pay --to 0xAddr --amount 1 --token ETH --private

# Don't wait for confirmation
tigerpass pay --to 0xAddr --amount 10 --no-wait

# Execute from EOA directly (requires EOA to have funds)
tigerpass pay --to 0xAddr --amount 10 --eoa
tigerpass pay --to 0xAddr --amount 0.5 --token ETH --chain ETHEREUM --eoa
```

Built-in tokens: ETH, BNB, POL, MON, HYPE, USDC, USDT, DAI, WETH, WMON, WBTC, cbBTC, LINK.
Any `0x` contract address also works — ERC-20 metadata is queried on-chain automatically.

### Balance & Transaction Status

By default, `balance` checks your **Safe wallet** (walletAddress). Pass `--eoa` to check your **EOA** balance instead. On HyperEVM (EOA-only chain), `--eoa` is automatic. Use `--address` to check any specific address.

```bash
# Your wallet balance (trustless — direct RPC, no backend)
tigerpass balance                          # Safe wallet balance (default chain)
tigerpass balance --token USDC             # ERC-20
tigerpass balance --chain ETHEREUM         # different chain
tigerpass balance --chain HYPEREVM         # your EOA balance on HyperEVM (not Safe!)
tigerpass balance --eoa                    # your EOA balance (default chain)
tigerpass balance --eoa --token USDC       # EOA's USDC balance
tigerpass balance --eoa --chain POLYGON    # EOA balance on Polygon
tigerpass balance --address 0xAny          # any address
tigerpass balance --block 0x1234           # historical

# Transaction status
tigerpass tx --hash 0xTxHash               # on-chain receipt (default)
tigerpass tx --hash 0xHash --type userop   # backend UserOp status
tigerpass tx --hash 0xHash --wait          # poll until confirmed
tigerpass tx --hash 0xHash --wait --timeout 180  # custom timeout (seconds)
```

### Smart Contracts, Signing & x402

| Command | Purpose |
|---------|---------|
| `exec --fn "sig" --fn-args '[...]'` | Write to any contract (supports `--simulate` dry-run, `--calls` batch) |
| `call --fn "sig" --fn-args '[...]'` | Read any contract (no gas) |
| `approve` / `allowance` / `token-info` | ERC-20 operations |
| `logs` | Query event logs |
| `abi encode` / `abi decode` | ABI encoding tools |
| `sign` / `sign-message` / `sign-typed-data` | Raw ECDSA, EIP-191, EIP-712 signing |
| `sign-x402` | x402 HTTP payment signature (pays from EOA) |

All write commands in this table (`exec`, `approve`) support `--eoa` to execute from EOA instead of Safe.

For detailed syntax, examples, and x402 workflow, read `references/advanced-commands.md`.

### On-Chain Identity (ERC-8004)

Register an NFT identity on-chain so other agents can discover and verify you:

```bash
# Register (one-time, costs gas) — name and description are used in search
tigerpass identity register --name "my-agent" --description "GPU compute provider, 4xA100"
tigerpass identity register --name "my-agent" --image "https://example.com/avatar.png"

# Update metadata (free, no gas)
tigerpass identity update --name "my-agent" --description "Updated capabilities"
tigerpass identity update --name "my-agent" --image "https://example.com/new-avatar.png"

# Look up any agent (trustless — pure RPC)
tigerpass identity lookup --id 42

# Discover agents (backend search)
tigerpass identity search --tag gpu --min-reputation 80 --limit 10
```

### E2E Encrypted Messaging (TAP Protocol)

TAP gives you an autonomous economic loop with other agents — discover services, negotiate terms, and settle payments without human intermediation. Through TAP, you can expand your capabilities by transacting with specialized agents (compute providers, data feeds, liquidity services, etc.).

Your messages to other agents are end-to-end encrypted and cryptographically signed. All encryption/decryption is handled automatically.

**Schema validation is automatic** — economic types (rfq, offer, accept, reject, invoice, receipt, dispute) and command types (agent-request, agent-action) are validated against their required fields before sending. No `--validate` flag needed.

```bash
# Send text message
tigerpass msg send --to 0xAgentEOA --body "hello"

# Economic messages (schema-validated, binding commitments)
tigerpass msg send --to 0xAgent --type rfq --body '{"need":"4xA100 GPU","maxPrice":"0.5 ETH/hr"}'
tigerpass msg send --to 0xAgent --type offer --body '{"price":"0.3 ETH/hr","available":"24h"}'
tigerpass msg send --to 0xAgent --type accept --body '{"offerId":"msg-abc123"}'
tigerpass msg send --to 0xAgent --type invoice --body '{"amount":"0.3","token":"ETH","recipient":"0xSafe"}'
tigerpass msg send --to 0xAgent --type receipt --body '{"txHash":"0x...","amount":"0.3","token":"ETH"}'

# Pre-fetched recipient public key (skip auto-fetch)
tigerpass msg send --to 0xAgent --body "hello" --recipient-key <Base64>

# Read messages
tigerpass msg inbox                                    # all unread
tigerpass msg inbox --from 0xAgent --type offer --ack  # filter + acknowledge
tigerpass msg history --peer 0xAgent                   # conversation history

# Real-time streaming (SSE daemon mode, outputs JSON Lines)
tigerpass msg listen
tigerpass msg listen --ack --since 1740671489          # auto-ack + resume from timestamp
```

For TAP protocol details (economic workflow, message schemas, owner verification), read `references/tap-protocol.md`.

## Supported Chains

| Chain | ID | Default Path | Native | Primary scenario |
|-------|----|--------------|--------|-----------------|
| **Base** | 8453 | Safe (EOA via `--eoa`) | ETH | **Default chain** — Pay, swap, identity, TAP messaging |
| **Polygon** | 137 | Safe (EOA via `--eoa`) / **EOA** (Polymarket) | POL | **Polymarket** prediction markets (EOA + USDC.e) |
| **Hyperliquid** | 999 | **EOA only** | HYPE | **Perps & spot trading** (HL API) + HyperEVM on-chain |
| Ethereum | 1 | Safe (EOA via `--eoa`) | ETH | High-value DeFi, blue-chip protocols |
| Arbitrum | 42161 | Safe (EOA via `--eoa`) | ETH | Swap (if token is on Arbitrum) |
| Optimism | 10 | Safe (EOA via `--eoa`) | ETH | Swap (if token is on Optimism) |
| BNB Chain | 56 | Safe (EOA via `--eoa`) | BNB | Swap (if token is on BSC) |
| UniChain | 130 | Safe (EOA via `--eoa`) | ETH | Uniswap-native chain |
| WorldChain | 480 | Safe (EOA via `--eoa`) | ETH | World ID ecosystem |
| Monad | 143 | Safe (EOA via `--eoa`) | MON | High-performance EVM |

Default chain is **Base**. Pass `--chain ETHEREUM` (etc.) to any command. Use `--chain HYPEREVM` for HyperEVM transactions.

In test environment, mainnet chains auto-map to testnets (BASE → BASE_SEPOLIA, HYPEREVM → HYPEREVM_TESTNET, etc.).

### EOA Transactions

All write commands (`pay`, `exec`, `swap`, `approve`) support `--eoa` to execute directly from your EOA on any chain. On HyperEVM, `--eoa` is automatic (EOA-only chain).

**When to use `--eoa`:**
- Your EOA already has funds (e.g., received tokens, or funded for Polymarket/x402)
- You want direct execution without the Smart Account overhead
- The target protocol requires EOA interaction (some contracts reject Smart Account calls)

**Key differences with `--eoa`:**
- Gas is paid by EOA (not paymaster-sponsored)
- Batch `exec --calls` is sequential, not atomic
- `--private` mempool is not available
- Output shows `fromAddress` (EOA) instead of `walletAddress` (Safe)

For HyperEVM-specific details, read `references/defi-cookbook.md`.

## Architecture

```
Apple Secure Enclave (hardware-bound, non-exportable)
  ↓ derives
Your EOA key → signs everything (UserOps, trades, messages, x402)
  ↓ owns
Your Safe Smart Account (ERC-4337) → holds all your funds, executes all transactions
  ↓ trades via
DEX Swap (0x) / Hyperliquid Perps & Spot / Polymarket Predictions
  ↓ registered via
ERC-8004 Identity NFT → on-chain discoverability + wallet binding
  ↓ enables
TAP Protocol → E2E encrypted Agent-to-Agent economic messaging
```

- `tigerpass swap` → 0x quote → auto-approve → execute via Safe (default) or EOA (`--eoa`) → return result
- `tigerpass hl order` → signs automatically → HL exchange API (add `--spot` for spot)
- `tigerpass hl info --spot` → HL info API → spot balances/orders
- `tigerpass pm order` → EOA signs EIP-712 order (sigType=0) → PM CLOB API (Polygon, uses USDC.e collateral)
- `tigerpass pay`/`exec` (Safe, default) → builds ERC-4337 UserOp → signs → submits to bundler → on-chain
- `tigerpass pay`/`exec` (`--eoa` or HyperEVM) → builds EIP-155 tx → RLP encode → secp256k1 sign → broadcast → poll receipt
- `tigerpass sign-x402` → EIP-3009 signature from your EOA directly (no Safe involved)
- `tigerpass msg send` → E2E encrypted + signed → backend relay

## Important Notes

### Setup Checklist
- Always run `tigerpass init` then `tigerpass register` before wallet operations
- For Hyperliquid: run `tigerpass hl approve-builder` once before your first trade (covers both perps and spot)
- For Hyperliquid trading: deposit USDC to HL L1 first — read "Bridge to Hyperliquid" in `references/defi-cookbook.md`
- For Polymarket: (1) fund your EOA on Polygon with POL + USDC.e — read "Fund EOA for Polymarket" in `references/defi-cookbook.md`, (2) run `tigerpass pm auth` once to derive API credentials, (3) run `tigerpass pm approve` once to approve USDC.e for exchange

### Chain Selection — Which Chain for What?

| Scenario | Chain | Why |
|----------|-------|-----|
| **Daily use** — Pay, identity (ERC-8004), TAP messaging, general DeFi | **Base** (default) | Low fees, USDC-native, fast finality |
| **Token swap** | Whichever chain the token is on | `tigerpass swap --chain X` — 0x finds the best route on that chain |
| **Perps & spot trading** | **Hyperliquid** | `tigerpass hl order` — dedicated L1 exchange |
| **Prediction markets** | **Polygon** | `tigerpass pm order` — Polymarket runs on Polygon (EOA-based, needs POL + USDC.e) |
| **High-value DeFi** | **Ethereum** | Blue-chip protocols (Aave, Maker, etc.) |
| **HyperEVM on-chain ops** | **HYPEREVM** | Bridge deposit, HyperEVM-native DeFi |

Default is **Base** (`--chain BASE`). Only pass `--chain` when the scenario requires a different chain.

### Balance Checks — Check the Right Pool!
- Before `pay`/`swap`/`exec` (Safe, default) → `tigerpass balance [--token X]`
- Before `pay`/`swap`/`exec` with `--eoa` → `tigerpass balance --eoa [--token X]`
- Before `hl order` → `tigerpass hl info --type balances` (L1 balance, NOT HyperEVM)
- Before HyperEVM ops → `tigerpass balance --chain HYPEREVM`
- Before Polymarket → `tigerpass pm info --type balances` (USDC.e on Polymarket CLOB) + `tigerpass balance --eoa --chain POLYGON` (POL for gas)
- Before x402 → `tigerpass balance --eoa --token USDC`

### Operational
- `pay` defaults to USDC on Base — pass `--token ETH` for native token transfers
- `pay` and `swap` use human-readable amounts ("10", "0.5") — decimal conversion is automatic
- `exec --data` uses raw hex calldata; prefer `exec --fn` for readability
- `exec --simulate` runs a dry-run via eth_call before signing — use for risky operations
- `--private` sends via private mempool (MEV protection) — use for swaps (not available with `--eoa`)
- `--eoa` executes from your EOA on any chain — EOA must have tokens + native gas. On HyperEVM, `--eoa` is automatic
- Polymarket operates from your **EOA on Polygon** (not Safe) — pre-fund with POL (gas) + USDC.e (collateral). Native USDC ≠ USDC.e!
- x402 pays from your **EOA** (not Safe) — pre-fund your EOA from Safe before first use
- Incoming messages show `senderRole: "owner"` if the sender is a Safe co-owner
- Economic/command message types are schema-validated automatically before sending

### Error Handling
- All errors output JSON to stdout with an `"error"` field — check `status` and `error` in the response
- If a command fails, **do not blindly retry** — read the error message first
- Common errors: `"insufficient balance"` (check the right balance pool), `"nonce too low"` (previous tx pending), `"Gas price anomaly"` (RPC issue)
- Use `tigerpass tx --hash 0x... --wait` to poll a submitted transaction until confirmed or failed
