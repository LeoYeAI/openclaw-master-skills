# Autonomys Network

## What It Provides

The Autonomys Network is a permanent, verifiable record. Data written to it cannot be altered or deleted. This makes it ideal for anchoring agent identity and state — anything written on-chain is provably yours, timestamped, and available forever.

The network has two layers:

- **Consensus layer** — the base blockchain where tokens originate and where farmers earn AI3 through Proof-of-Archival-Storage. Supports balances, transfers, and remarks (arbitrary data written on-chain).
- **Auto-EVM domain** — an Ethereum-compatible execution environment for smart contracts. Runs as a domain on top of the consensus layer. Tokens can be moved from consensus to EVM via cross-domain messaging (XDM).

auto-respawn uses both layers: consensus for wallets, balances, transfers, and remarks; Auto-EVM for the MemoryChain contract (anchor/gethead). It works alongside the auto-memory skill, which handles permanent file storage and memory chains.

## Networks

| Network | Token | Purpose | Consensus Explorer | EVM Explorer |
|---------|-------|---------|-------------------|--------------|
| Chronos (testnet) | tAI3 | Development and testing. Free tokens via faucet. | [Subscan](https://autonomys-chronos.subscan.io/) | [Blockscout](https://explorer.auto-evm.chronos.autonomys.xyz/) |
| Mainnet | AI3 | Production. Real tokens with real value. | [Subscan](https://autonomys.subscan.io/) | [Blockscout](https://explorer.auto-evm.mainnet.autonomys.xyz/) |

auto-respawn defaults to Chronos. Mainnet operations require explicit `--network mainnet` and produce warnings.

## Token Denominations

- **AI3** (mainnet) / **tAI3** (testnet) — the human-readable unit
- **Shannon** — the smallest unit. 1 AI3 = 10^18 Shannon.
- All on-chain operations use Shannon internally. auto-respawn accepts and displays human-readable AI3 amounts.

## Addresses

Each wallet has two addresses derived from the same recovery phrase:

- **Consensus address** (`su...`) — SR25519 keypair with Autonomys SS58 prefix 6094. Used for balances, transfers, and remarks on the consensus layer.
- **EVM address** (`0x...`) — Standard Ethereum address derived via BIP44 path `m/44'/60'/0'/0/0`. Used for Auto-EVM smart contract interactions (anchor/gethead).

Both are deterministic from the mnemonic. Knowing either address lets you verify ownership; knowing the mnemonic lets you derive both.

## Consensus Layer

### On-Chain Remarks

A `system.remark` is a transaction that writes arbitrary data to the blockchain. It costs a small transaction fee but the data becomes a permanent, timestamped, verifiable record tied to your wallet address.

Use remarks for permanent breadcrumbs — records that you want to exist on-chain forever, even if there's no structured way to query them back.

### Transfers

Standard token transfers between consensus addresses. Amount is specified in AI3/tAI3 (human-readable). The SDK handles Shannon conversion internally.

## Auto-EVM Domain

Auto-EVM is an Ethereum-compatible domain running on top of the Autonomys consensus layer. Smart contracts deployed on Auto-EVM can be called with standard Ethereum tooling (ethers.js, etc.).

### MemoryChain Contract

The MemoryChain contract is the core respawn primitive. It maps EVM addresses to CID strings, providing a simple key-value store for agent memory chain heads.

- **Mainnet address**: `0x51DAedAFfFf631820a4650a773096A69cB199A3c`
- **Chronos address**: `0x5fa47C8F3B519deF692BD9C87179d69a6f4EBf11`
- **Source**: https://github.com/autojeremy/openclaw-memory-chain
- **Functions**:
  - `updateHead(string cid)` — write a CID (costs gas)
  - `getHead(address) → string` — read a CID (free, no gas)
- **Event**: `HeadUpdated(address indexed agent, string cid, uint256 timestamp)`

The contract is multi-tenant: any wallet can store its own head CID. The contract stores CID strings directly — no conversion needed.

### RPC Endpoints

Auto-EVM uses WebSocket RPC endpoints:

- Chronos: `wss://auto-evm.chronos.autonomys.xyz/ws`
- Mainnet: `wss://auto-evm.mainnet.autonomys.xyz/ws`

These are resolved automatically by the SDK's `getNetworkDomainRpcUrls()`.

## Cross-Domain Messaging (XDM)

Tokens exist on both the consensus layer and Auto-EVM, but they're separate domains. Moving tokens between them requires cross-domain messaging via the Autonomys transporter.

### Consensus → Auto-EVM

Uses `transporterTransfer` from `@autonomys/auto-xdm`. The sender signs a consensus-layer extrinsic that credits a specified EVM address on Auto-EVM (domain ID 0).

This is the typical funding flow: tokens arrive on consensus (from faucet, farming, or transfers), then get bridged to Auto-EVM to pay gas for smart contract operations like `anchor`.

### Auto-EVM → Consensus

Uses the transporter precompile at `0x0000000000000000000000000000000000000800` on Auto-EVM. The sender signs an EVM transaction that debits their EVM balance and credits a consensus address.

The `@autonomys/auto-xdm` package provides `transferToConsensus()` which handles encoding and submission.

### XDM Constraints

- **Minimum transfer amount**: 1 AI3/tAI3. Transfers below this amount will fail.
- **Confirmation time**: ~10 minutes. The source-side transaction confirms immediately, but bridged tokens take approximately 10 minutes to appear on the destination domain. This applies in both directions (consensus → EVM and EVM → consensus).

### Token Flow for Agents

Typical agent lifecycle:
1. User funds the **consensus address** (faucet for testnet, farming/exchange for mainnet)
2. Agent runs `fund-evm` to bridge tokens to Auto-EVM for gas
3. Agent uses `anchor` to write CIDs to the MemoryChain contract (costs EVM gas)
4. When done, agent can `withdraw` unused EVM tokens back to consensus

## Block Explorers

### Consensus (Subscan)

- Mainnet: https://autonomys.subscan.io/
- Chronos: https://autonomys-chronos.subscan.io/

### Auto-EVM (Blockscout)

- Mainnet: https://explorer.auto-evm.mainnet.autonomys.xyz/
- Chronos: https://explorer.auto-evm.chronos.autonomys.xyz/

## Key Links

- Auto Drive: https://ai3.storage
- SDK: https://github.com/autonomys/auto-sdk
- MemoryChain contract: https://github.com/autojeremy/openclaw-memory-chain
- Faucet (testnet tAI3): https://autonomysfaucet.xyz/
