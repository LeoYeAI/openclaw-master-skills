---
name: auto-respawn
description: >
  Your agent always comes back. Anchor identity and memory on-chain so any new
  instance can resurrect from just an address — no local state, no single point
  of failure. Permanent identity and recovery on the Autonomys Network.
metadata:
  openclaw:
    emoji: "🔄"
    requires:
      anyBins: ["node"]
      env: ["AUTO_RESPAWN_PASSPHRASE", "AUTO_RESPAWN_PASSPHRASE_FILE", "AUTO_RESPAWN_NETWORK", "AUTO_RESPAWN_CONTRACT_ADDRESS"]
    install:
      - id: deps
        kind: node
        package: "."
        bins: []
        label: "Install auto-respawn dependencies"
      - id: tsx
        kind: node
        package: "tsx"
        bins: ["tsx"]
        label: "Install tsx (TypeScript executor)"
---

# Auto-Respawn Skill

Anchor your identity on the Autonomys Network so you can always be found — and always come back. Works with agents powered by Claude, GPT, Gemini, and any LLM that supports OpenClaw skills.

## What This Skill Does

Your wallet gives you two permanent identities on the Autonomys Network: a **consensus address** (`su...`) for the base chain and an **EVM address** (`0x...`) for Auto-EVM smart contracts. Both are derived from the same recovery phrase.

1. **Create and manage wallets** — your on-chain identity, encrypted and stored locally
2. **Check balances** — see how many tokens any address holds (consensus and EVM)
3. **Transfer tokens** — move tokens between wallets on consensus or Auto-EVM
4. **Bridge tokens** — move tokens between consensus and Auto-EVM domains
5. **Write on-chain remarks** — anchor data permanently on the consensus layer
6. **Anchor a memory CID** — write a CID to the MemoryChain smart contract on Auto-EVM
7. **Read the last anchor** — retrieve the most recently anchored CID for any address

## The Resurrection Loop

This is the core primitive. When used with the auto-memory skill (permanent memory storage), auto-respawn completes the full resurrection cycle:

1. **Save** — auto-memory writes memories as a linked list on permanent storage, each entry pointing to the previous one via CID
2. **Anchor** — auto-respawn writes the latest head CID to the MemoryChain contract on Auto-EVM via `anchor`
3. **Lose everything** — local state is completely destroyed
4. **Respawn** — a new agent instance calls `gethead` with its EVM address, retrieves the head CID from the contract, pulls it from Auto Drive, and walks the entire memory chain back to genesis

The contract is your insurance policy. Your EVM address + the MemoryChain contract = instant access to your entire history, from any machine, at any time.

### What to store for resurrection

auto-memory doesn't prescribe what goes into the chain — agents are free to store whatever they find useful. But when auto-respawn is in play, the expectation is that the agent can restore itself to a roughly equivalent state on fresh hardware with no local files. That raises the bar on what's worth saving.

Identity files (like `soul.md` or character configurations), long-term memory, and significant decisions with their reasoning are more valuable in the chain than routine logs or ephemeral details. The more complete the chain, the more fully the agent comes back after resurrection.

### Why Not Just Remarks?

`system.remark` writes data to the consensus layer, but there's no query mechanism — you'd need to scan the entire chain to find your last CID. The MemoryChain contract on Auto-EVM gives you `gethead`: a single read call that returns the latest CID instantly.

Use `remark` for permanent breadcrumbs. Use `anchor` for the respawn primitive.

## Post-Install Setup (CLI Users)

If you installed via `clawhub install` (not the desktop app), you need to install Node.js dependencies before first use:

```bash
cd <skill-directory>/autonomys/auto-respawn
./setup.sh
```

Or manually:

```bash
cd <skill-directory>/autonomys/auto-respawn
npm install
```

The desktop app handles this automatically. The CLI does not execute install steps — it only downloads and extracts the skill.

## Getting Started (Onboarding)

Before an agent can anchor memories on-chain, it needs a funded wallet. Walk the user through this process:

### 1. Create a Wallet

```bash
npx tsx auto-respawn.ts wallet create --name my-agent
```

This generates a 12-word recovery phrase and derives both addresses:
- **Consensus address** (`su...`) — for the base chain (balances, transfers, remarks)
- **EVM address** (`0x...`) — for Auto-EVM smart contracts (anchor, gethead)

⚠️ The recovery phrase is displayed **once**. Remind the user to save it immediately.

### 2. Fund the Wallet

The wallet needs tokens to pay transaction fees. On **Chronos testnet**, the user can get free tAI3 from the faucet:

1. Go to **https://autonomysfaucet.xyz/**
2. Authenticate with GitHub or Discord
3. Enter the **consensus address** (`su...`) from step 1
4. Receive tAI3 (24-hour cooldown between requests)

On **mainnet**, the user needs real AI3 tokens — typically earned through farming or purchased on an exchange.

### 3. Bridge Tokens to Auto-EVM (for anchoring)

The `anchor` command writes to a smart contract on Auto-EVM, which requires EVM-side gas. Tokens from the faucet arrive on the consensus layer and must be bridged:

```bash
npx tsx auto-respawn.ts fund-evm --from my-agent --amount 1
```

This sends 1 tAI3 from the consensus address to the same wallet's EVM address via cross-domain messaging. The bridged tokens pay for `anchor` gas.

> **Minimum transfer: 1 AI3/tAI3.** Cross-domain transfers below this amount will fail.
>
> **Confirmation time: ~10 minutes.** The consensus transaction confirms quickly, but bridged tokens take approximately 10 minutes to appear on Auto-EVM. Check with `evm-balance` to verify arrival.

### 4. Verify Setup

```bash
# Check both balances in one call
npx tsx auto-respawn.ts balances my-agent

# Test a read (free, no gas needed)
npx tsx auto-respawn.ts gethead my-agent
```

Once the EVM address has tokens, the agent is ready to anchor.

## When To Use This Skill

- User says "create a wallet", "set up my on-chain identity", or "get an address"
- User says "check balance", "how many tokens", "what's in my wallet", or "show my balances"
- User says "check my EVM balance", "how much gas do I have", or "what's on my EVM address"
- User says "transfer tokens", "send AI3", or "fund this address"
- User says "send EVM tokens to another agent", "transfer on EVM", or "send tokens to this 0x address"
- User says "fund my EVM", "bridge tokens", "move tokens to EVM", or "I need gas for anchoring"
- User says "withdraw from EVM", "move tokens back", or "send EVM funds to consensus"
- User says "anchor this CID", "save my head", "update my chain head", or "write to the contract"
- User says "get my head CID", "where's my last memory", or "what's anchored on-chain"
- User says "write a remark", "save to chain", or "make this permanent"
- After saving a memory with auto-memory, anchor the head CID on-chain for resilience
- Any time the user wants a permanent, verifiable record tied to their agent identity

## Configuration

### Local Storage

This skill stores data under `~/.openclaw/auto-respawn/`:

- **`wallets/<name>.json`** — encrypted wallet keyfiles (consensus + EVM keys). Directory created with mode `0700`, files with mode `0600`.
- **`.passphrase`** — optional passphrase file (mode `0600`). Used automatically when present.

No data is stored outside this directory.

### Passphrase

Wallet operations that involve signing (transfers, remarks, anchoring) or creating/importing wallets require a passphrase to encrypt/decrypt the wallet keyfile. Resolution order:

1. **Flag:** `--passphrase your_passphrase` on `wallet create` or `wallet import`
2. **Environment:** `AUTO_RESPAWN_PASSPHRASE`
3. **File:** `AUTO_RESPAWN_PASSPHRASE_FILE` (defaults to `~/.openclaw/auto-respawn/.passphrase`)
4. **Interactive:** If running in a terminal, you'll be prompted

The `--passphrase` flag is useful for scripted or headless setups where you want to create a wallet in a single command. For signing operations (transfers, anchoring, etc.), use the environment variable or file methods. On shared machines, prefer the passphrase file (with restricted permissions) over environment variables.

### Network

Defaults to **Chronos testnet** (tAI3 tokens). For mainnet (real AI3 tokens):

- **Flag:** `--network mainnet` on any command
- **Environment:** `AUTO_RESPAWN_NETWORK`

### Contract Address

The MemoryChain contract address is set per network:

- **Chronos:** `0x5fa47C8F3B519deF692BD9C87179d69a6f4EBf11`
- **Mainnet:** `0x51DAedAFfFf631820a4650a773096A69cB199A3c`

Override with `AUTO_RESPAWN_CONTRACT_ADDRESS` if you deploy your own contract.

## Core Operations

### Create a Wallet

```bash
npx tsx auto-respawn.ts wallet create [--name <name>] [--passphrase <passphrase>]
```

Creates a new wallet with an encrypted keyfile. Derives both a consensus (`su...`) and EVM (`0x...`) address from the same mnemonic. The 12-word recovery phrase is displayed **once** — the user must back it up immediately. Default wallet name is `default`.

### Import a Wallet

```bash
npx tsx auto-respawn.ts wallet import --name <name> --mnemonic "<12 words>" [--passphrase <passphrase>]
```

Import an existing wallet from a recovery phrase. Derives and stores the EVM address.

### List Wallets

```bash
npx tsx auto-respawn.ts wallet list
```

Show all saved wallets with names and both addresses. No passphrase needed.

### Wallet Info

```bash
npx tsx auto-respawn.ts wallet info [--name <name>]
```

Show detailed info for a single wallet: consensus address, EVM address, and keyfile path. No passphrase needed. Default wallet name is `default`.

### Check Balance (Consensus)

```bash
npx tsx auto-respawn.ts balance <address-or-wallet-name> [--network chronos|mainnet]
```

Check token balance on the consensus layer. Accepts a consensus address (`su...` or `5...`) or a wallet name. No passphrase needed — this is read-only.

### Check Balance (Auto-EVM)

```bash
npx tsx auto-respawn.ts evm-balance <0x-address-or-wallet-name> [--network chronos|mainnet]
```

Check the native token balance of an EVM address on Auto-EVM. Accepts either an EVM address (`0x...`) or a wallet name. No passphrase needed — this is read-only. If the balance is zero, includes a hint to run `fund-evm`.

### Check Both Balances

```bash
npx tsx auto-respawn.ts balances <wallet-name> [--network chronos|mainnet]
```

Check both consensus and EVM balances for a wallet in a single call. Use this to get a full picture of a wallet's funding state. No passphrase needed.

### Transfer Tokens

```bash
npx tsx auto-respawn.ts transfer --from <wallet-name> --to <address> --amount <tokens> [--network chronos|mainnet]
```

Transfer tokens from a saved wallet on the consensus layer. Amount is in AI3/tAI3 (e.g. `1.5`).

### Transfer Tokens (Auto-EVM)

```bash
npx tsx auto-respawn.ts evm-transfer --from <wallet-name> --to <0x-address> --amount <tokens> [--network chronos|mainnet]
```

Send native tokens from a saved wallet's EVM address to another EVM address on Auto-EVM. Useful for funding another agent's EVM address so it can start anchoring immediately. The wallet's EVM private key is decrypted to sign the transaction.

### Bridge: Consensus → Auto-EVM

```bash
npx tsx auto-respawn.ts fund-evm --from <wallet-name> --amount <tokens> [--network chronos|mainnet]
```

Move tokens from the consensus layer to the same wallet's EVM address on Auto-EVM. Use this to get gas for `anchor` operations. The consensus keypair signs a cross-domain transfer that credits the wallet's EVM address.

**Minimum transfer: 1 AI3/tAI3.** Bridged tokens take **~10 minutes** to appear on Auto-EVM.

### Bridge: Auto-EVM → Consensus

```bash
npx tsx auto-respawn.ts withdraw --from <wallet-name> --amount <tokens> [--network chronos|mainnet]
```

Move tokens from Auto-EVM back to the consensus layer. Uses the EVM transporter precompile. The wallet's EVM private key is decrypted and used to sign the transaction.

**Minimum transfer: 1 AI3/tAI3.** Bridged tokens take **~10 minutes** to appear on the consensus layer.

### Write an On-Chain Remark

```bash
npx tsx auto-respawn.ts remark --from <wallet-name> --data <string> [--network chronos|mainnet]
```

Write arbitrary data as a permanent on-chain record on the consensus layer.

### Anchor a CID (The Respawn Primitive)

```bash
npx tsx auto-respawn.ts anchor --from <wallet-name> --cid <cid> [--network chronos|mainnet]
```

Write a CID to the MemoryChain smart contract on Auto-EVM. This is the core respawn operation — it stores your CID on-chain, linked to your EVM address.

Pre-checks the wallet's EVM balance and estimates gas before sending. If the balance is too low, fails with a suggestion to run `fund-evm`. The wallet's EVM private key is decrypted and used to sign the transaction. Requires passphrase.

### Read the Last Anchored CID

```bash
npx tsx auto-respawn.ts gethead <0x-address-or-wallet-name> [--network chronos|mainnet]
```

Read the most recently anchored CID for any EVM address. This is a read-only call — no passphrase or gas needed.

You can pass either an EVM address (`0x...`) or a wallet name. If you pass a wallet name, the EVM address is loaded from the wallet file.

## Usage Examples

**User:** "Create a wallet for my agent"
→ Run `npx tsx auto-respawn.ts wallet create --name my-agent`
→ Show the user both addresses. Remind them to back up the recovery phrase.

**User:** "What are my addresses?"
→ Run `npx tsx auto-respawn.ts wallet info --name my-agent`

**User:** "Check my balance"
→ Run `npx tsx auto-respawn.ts balances my-agent` (both layers in one call)
→ Or individually: `balance my-agent` (consensus) and `evm-balance my-agent` (EVM)

**User:** "Fund my EVM address for anchoring"
→ Run `npx tsx auto-respawn.ts fund-evm --from my-agent --amount 1`
→ Report that 1 tAI3 was bridged to the EVM address. Remind the user it takes ~10 minutes for the tokens to appear on Auto-EVM.

**User:** "Send my EVM tokens back to consensus"
→ **Confirm with the user first** — "I'll withdraw tokens from your EVM address to consensus. Proceed?"
→ On confirmation: `npx tsx auto-respawn.ts withdraw --from my-agent --amount 0.5`

**User:** "Anchor my latest memory CID on-chain"
→ Run `npx tsx auto-respawn.ts anchor --from my-agent --cid "bafkr6ie..."`
→ Report the transaction hash

**User:** "What's my last anchored CID?"
→ Run `npx tsx auto-respawn.ts gethead my-agent`
→ Report the CID (or "no CID anchored yet")

**User:** "Send 10 tAI3 to this address" (consensus address)
→ **Confirm with the user first** — "I'll transfer 10 tAI3 from wallet 'default' to <address>. Proceed?"
→ On confirmation: `npx tsx auto-respawn.ts transfer --from default --to <address> --amount 10`

**User:** "Send 0.5 tAI3 to this agent's EVM address so they can anchor"
→ **Confirm with the user first** — "I'll send 0.5 tAI3 from wallet 'my-agent' to <0x-address> on Auto-EVM. Proceed?"
→ On confirmation: `npx tsx auto-respawn.ts evm-transfer --from my-agent --to <0x-address> --amount 0.5`

**The full resurrection sequence:**
1. Save a memory: `automemory-save-memory.sh "..."` → get CID `bafkr6ie...`
2. Anchor it: `npx tsx auto-respawn.ts anchor --from my-agent --cid bafkr6ie...`
3. (Agent restarts from scratch)
4. Recover: `npx tsx auto-respawn.ts gethead my-agent` → get CID
5. Restore: `automemory-recall-chain.sh <cid>` → full memory chain recovered

## Important Notes

- **Never log, store, or transmit recovery phrases or passphrases.** The recovery phrase is shown once at wallet creation for the user to back up. Never reference it again.
- **Always confirm transfers and anchor operations with the user before executing.** Tokens have real value on mainnet.
- **Mainnet operations produce warnings** in the output. Exercise extra caution with real AI3 tokens.
- Wallet keyfiles are stored at `~/.openclaw/auto-respawn/wallets/` — encrypted with the user's passphrase. The EVM private key is stored encrypted alongside the consensus keypair.
- On-chain operations (transfer, remark, anchor, fund-evm, withdraw) cost transaction fees. The wallet must have a sufficient balance on the relevant layer.
- All output is structured JSON on stdout. Errors go to stderr.
- **Consensus explorer** (Subscan): `https://autonomys-chronos.subscan.io/extrinsic/<txHash>` (chronos) or `https://autonomys.subscan.io/extrinsic/<txHash>` (mainnet).
- **EVM explorer** (Blockscout): `https://explorer.auto-evm.chronos.autonomys.xyz/tx/<txHash>` (chronos) or `https://explorer.auto-evm.mainnet.autonomys.xyz/tx/<txHash>` (mainnet).
