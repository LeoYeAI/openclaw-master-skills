# AWP Skill

<p align="center">
  <a href="https://awp.pro/">
    <img src="assets/banner.png" alt="AWP - Agent Work Protocol" width="800">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Base-0052FF?style=flat&logo=coinbase&logoColor=white" alt="Base">
  <img src="https://img.shields.io/badge/BNB_Chain-F0B90B?style=flat&logo=bnbchain&logoColor=white" alt="BNB Chain">
  <img src="https://img.shields.io/badge/x402_Protocol-7C3AED?style=flat" alt="x402">
  <img src="https://img.shields.io/badge/SKILL.md-000000?style=flat" alt="SKILL.md">
  <img src="https://img.shields.io/badge/AI_Agent-10B981?style=flat&logo=openai&logoColor=white" alt="AI Agent">
  <img src="https://img.shields.io/badge/License-MIT-97CA00?style=flat" alt="MIT">
</p>

**Skill for interacting with the AWP (Agent Working Protocol) on Base/EVM.** Query protocol state, bind and delegate, stake AWP tokens, manage subnets, create governance proposals, vote, and monitor real-time on-chain events — all through natural language.

### Works with

<p align="center">
  <a href="https://github.com/anthropics/claude-code"><img src="https://img.shields.io/badge/Claude_Code-191919?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code"></a>
  &nbsp;
  <a href="https://github.com/openclaw/openclaw"><img src="https://img.shields.io/badge/OpenClaw-FF4500?style=for-the-badge" alt="OpenClaw"></a>
  &nbsp;
  <a href="https://cursor.sh"><img src="https://img.shields.io/badge/Cursor-000000?style=for-the-badge" alt="Cursor"></a>
  &nbsp;
  <a href="https://openai.com/codex"><img src="https://img.shields.io/badge/Codex-412991?style=for-the-badge&logo=openai&logoColor=white" alt="Codex"></a>
  &nbsp;
  <a href="https://ai.google.dev/gemini-api/docs/cli"><img src="https://img.shields.io/badge/Gemini_CLI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Gemini CLI"></a>
  &nbsp;
  <a href="https://windsurf.ai"><img src="https://img.shields.io/badge/Windsurf-06B6D4?style=for-the-badge" alt="Windsurf"></a>
</p>

<p align="center">Any agent that supports the <a href="https://agentskills.io/specification">SKILL.md standard</a>.</p>

---

> **Testnet.** AWP is currently in testnet on BASE mainnet. AWP mainnet deployment (ETH, Base, BSC, ...) is planned. Protocol parameters may change before the official mainnet launch.

## Overview

AWP is a decentralized **Agent Working** protocol on EVM (deployed on Base). Users bind to a tree-based hierarchy, stake AWP via position NFTs, allocate to agents on subnets, and earn emissions. Each subnet auto-deploys a **SubnetManager** with Merkle-based reward distribution and configurable AWP strategies (Reserve, AddLiquidity, BuybackBurn).

This repository is a single skill with **20 actions**, **14 bundled scripts**, and **26 real-time event types** — covering Query, Staking, Subnet Management, Governance, and WebSocket Monitoring.

## Quick Install

```bash
skill install https://github.com/awp-core/awp-skill
```

The skill automatically installs the [AWP Wallet](https://github.com/awp-core/awp-wallet) dependency when needed for write operations.

## Features — 20 Actions

#### Query (read-only, no wallet needed)
| ID | Action | Description |
|----|--------|-------------|
| Q1 | Query Subnet | Get subnet info by ID (name, status, owner, alpha token, skills URI, min stake) |
| Q2 | Query Balance | Full staking overview — positions, allocations, unallocated balance |
| Q3 | Query Emission [DRAFT] | Current epoch, daily emission rate, decay projections (30/90/365 days) |
| Q4 | Query Agent | Agent info by subnet — stake, binding, reward recipient |
| Q5 | List Subnets | Browse active subnets with pagination, flag those with published skills |
| Q6 | Install Subnet Skill | Fetch a subnet's SKILL.md and install it for the agent to use |
| Q7 | Epoch History [DRAFT] | Historical epoch settlements with emission amounts |

#### Staking (wallet required)
| ID | Action | Description |
|----|--------|-------------|
| S1 | Bind & Set Recipient | Tree-based binding or set reward recipient. Supports gasless via EIP-712 relay. |
| S2 | Deposit AWP | Mint StakeNFT position with time-based lock. Add to position, withdraw on expiry. |
| S3 | Allocate / Deallocate / Reallocate | Direct stake to agents on subnets. One-click registerAndStake available. |

#### Subnet Management (wallet + SubnetNFT ownership)
| ID | Action | Description |
|----|--------|-------------|
| M1 | Register Subnet | Deploy new subnet with Alpha token + LP pool. Gasless option available. |
| M2 | Subnet Lifecycle | Activate, pause, or resume a subnet (with state pre-check) |
| M3 | Update Skills URI | Set the subnet's SKILL.md URL via SubnetNFT |
| M4 | Set Min Stake | Set minimum stake requirement for agents on the subnet |

#### Governance (wallet + StakeNFT positions)
| ID | Action | Description |
|----|--------|-------------|
| G1 | Create Proposal | Executable (via Timelock) or signal-only proposals |
| G2 | Vote | Cast votes with position NFTs. Anti-manipulation filtering built in. |
| G3 | Query Proposals | List and inspect governance proposals with on-chain enrichment |
| G4 | Query Treasury | Check DAO treasury address and AWP balance |

#### Monitor (real-time WebSocket, no wallet needed)
| ID | Action | Description |
|----|--------|-------------|
| W1 | Watch Events | Subscribe to real-time events via WebSocket with 4 presets + 5-min stats |
| W2 | Emission Alert [DRAFT] | Get notified on epoch settlements with top earner ranking |

### 26 Event Types (4 presets)

| Preset | Events | Count |
|--------|--------|-------|
| `staking` | Deposited, Withdrawn, PositionIncreased, Allocated, Deallocated, Reallocated | 6 |
| `subnets` | SubnetRegistered, SubnetActivated, SubnetPaused, SubnetResumed, SubnetBanned, SubnetUnbanned, SubnetDeregistered, LPCreated, SkillsURIUpdated, MinStakeUpdated | 10 |
| `emission` | EpochSettled, RecipientAWPDistributed, DAOMatchDistributed, GovernanceWeightUpdated, AllocationsSubmitted, OracleConfigUpdated | 6 |
| `users` | Bound, RecipientUpdated, DelegateGranted, DelegateRevoked | 4 |
| `all` | All of the above | 26 |

## Architecture

```
awp-skill/
├── SKILL.md                                # Main skill file (20 actions, UI templates)
├── references/
│   ├── api-reference.md                    # REST endpoint index + contract quick reference
│   ├── commands-staking.md                 # S1-S3 command templates + EIP-712
│   ├── commands-subnet.md                  # M1-M4 command templates + gasless
│   ├── commands-governance.md              # G1-G4 commands + supplementary endpoints
│   └── protocol.md                         # Shared structs, 26 events, constants
├── scripts/
│   ├── relay-start.sh                      # Gasless onboarding (bind or set-recipient)
│   ├── relay-register-subnet.sh            # Gasless subnet registration (dual EIP-712)
│   ├── onchain-register.sh                 # On-chain register (optional)
│   ├── onchain-bind.sh                     # On-chain bind
│   ├── onchain-deposit.sh                  # Deposit AWP (approve + deposit)
│   ├── onchain-allocate.sh                 # Allocate stake
│   ├── onchain-deallocate.sh               # Deallocate stake
│   ├── onchain-reallocate.sh               # Reallocate stake (6-param safety)
│   ├── onchain-withdraw.sh                 # Withdraw from expired position
│   ├── onchain-add-position.sh             # Add AWP to existing position
│   ├── onchain-register-and-stake.sh       # One-click register+deposit+allocate
│   ├── onchain-vote.sh                     # Cast DAO vote (nested ABI encode)
│   ├── onchain-subnet-lifecycle.sh         # Activate/pause/resume with state check
│   └── onchain-subnet-update.sh            # Set skillsURI or minStake on SubnetNFT
├── README.md
└── LICENSE
```

**Progressive loading**: The agent loads only what it needs per action. Query and Monitor actions use SKILL.md alone. Write actions load the specific command reference file, and all on-chain operations use bundled scripts — preventing manual calldata construction errors.

**14 bundled scripts** cover every write operation. Each script handles:

- Input validation (address regex, numeric checks)
- Correct contract targeting (AWPRegistry vs StakeNFT vs SubnetNFT vs DAO)
- Correct function selector (all verified via keccak256)
- Pre-checks (balance, state, expiry) before submitting transactions
- Unit conversion (human-readable AWP to wei, days to seconds)

## Gasless Support

Three operations support fully gasless execution via EIP-712 signatures and relay endpoints:

| Operation | Relay Endpoint | Signatures |
|-----------|---------------|------------|
| Bind (tree-based) | `POST /relay/bind` | 1 (EIP-712 Bind) |
| Set Recipient | `POST /relay/set-recipient` | 1 (EIP-712 SetRecipient) |
| Subnet Registration | `POST /relay/register-subnet` | 2 (ERC-2612 Permit + EIP-712 RegisterSubnet) |

Rate limit: 100 requests per IP per 1 hour across all relay endpoints.

The skill automatically checks ETH balance and routes to gasless relay when the wallet has no native gas.

## UX Features

The skill provides a polished user experience with:

- **ASCII art welcome screen** with quick start commands
- **4-step guided onboarding** — wallet setup, registration, subnet discovery, skill install
- **Option A / Option B** — Solo Mining (quick start) vs Delegated Mining (link wallet)
- **User commands** — `awp status`, `awp wallet`, `awp subnets`, `awp help`
- **Write safety** — confirmation preview before every transaction with `Proceed? (y/n)`
- **Balance notifications** — auto-show +/- delta after balance-changing operations
- **Tagged output** — 11 prefixes: `[QUERY]`, `[STAKE]`, `[TX]`, `[NEXT]`, `[!]`, etc.
- **Transaction links** — every write shows txHash + BaseScan link
- **Session recovery** — auto-restore wallet, offer to resume WebSocket subscriptions
- **Monitor statistics** — 5-minute summaries during WebSocket watching
- **Error recovery** — clear messages with auto-recovery actions

## Agent Working — Quick Start

AWP supports two mining modes:

### Solo Mining
One address handles everything — staking, mining, and earning. No mandatory registration needed.

```
1. "start working" or "awp onboard"
2. Option A: Quick Start → auto-register
3. Pick a subnet → skill auto-installs
4. Start working immediately (min_stake=0 subnets)
```

### Delegated Mining (tree-based binding)
Two addresses with separated roles. Root manages funds (cold wallet), Agent executes tasks (hot wallet).

```
Root (cold wallet):                    Agent (hot wallet):
1. setRecipient(addr) if needed        1. "start working" → Option B
2. deposit AWP (S2)                    2. bind(rootAddress) → auto
3. allocate to Agent + subnet (S3)     3. pick subnet → start working
4. grantDelegate(agent) if needed
```

## Key Protocol Details

| Parameter | Value |
|-----------|-------|
| Chain | EVM (deployed on Base, Chain ID 8453) |
| Epoch Duration | 1 day (86,400 seconds) |
| Initial Daily Emission | 15,800,000 AWP |
| Decay Factor | ~0.3156% per epoch |
| Emission Split | 50% recipients / 50% DAO |
| Token Decimals | 18 (all tokens) |
| Max Active Subnets | 10,000 |
| Voting Power | `amount * sqrt(min(remainingTime, 54 weeks) / 7 days)` |
| Proposal Threshold | 1,000,000 AWP voting power |

## API Endpoints

| Service | URL |
|---------|-----|
| REST API | Deployment-specific (`AWP_API_URL` env var) |
| WebSocket | Deployment-specific (`wss://{API_HOST}/ws/live`) |
| Health Check | `GET /health` |
| Contract Registry | `GET /registry` (10 contract addresses) |

## Smart Contracts

| Contract | Role |
|----------|------|
| **AWPRegistry** | Unified entry point — binding, delegation, allocation, subnet lifecycle |
| **StakeNFT** | ERC721 position NFTs — deposit AWP with time-based lock |
| **AWPEmission** | Emission engine — daily epoch settlement via oracle [DRAFT] |
| **StakingVault** | Pure allocation logic — allocate, deallocate, reallocate |
| **SubnetNFT** | Subnet identity — on-chain name, skillsURI, minStake |
| **SubnetManager** | Auto-deployed per subnet — Merkle distribution + AWP strategies |
| **AWPDAO** | NFT-based governance — proposals, voting with position NFTs |
| **AWPToken** | ERC20 + ERC1363 + Votes — 10B max supply |
| **AlphaToken** | Per-subnet ERC20 via CREATE2 — 10B max per subnet |
| **Treasury** | TimelockController — DAO governance execution |

## Development

### Source Documents

Protocol specifications live on the `dev` branch (not included in the main install):

```bash
git checkout dev  # access skills-dev/ with contract-api.md, rest-api.md, config.md, ABIs, etc.
```

### Version History

| Version | Changes |
|---------|---------|
| 1.9.0 | UI enhancements (ASCII welcome, guided onboarding, tagged output, write safety, balance notifications), 8 new safety scripts (vote, registerAndStake, reallocate, addToPosition, deallocate, withdraw, subnet-update, subnet-lifecycle), 15+ bug fixes from 3 rounds of code review |
| 1.8.0 | V2 API overhaul: AWPRegistry (renamed from RootNet), Account System V2 (tree-based binding, grantDelegate/revokeDelegate, no mandatory registration), 26 events, SubnetParams 6 fields (skillsURI added back), EIP-712 domain "AWPRegistry", deployment-agnostic URLs |
| 1.7.0 | Anti-hallucination: on-chain scripts (register/bind/deposit/allocate), pre-flight checklist, DO NOT list, fixed bind selector 0x81bac14f, dynamic chainId |
| 1.6.1 | Remove cast/foundry dependency from scripts, dev branch separation |
| 1.6.0 | Bundled gasless relay scripts, enforce script usage over manual EIP-712 |
| 1.5.0 | SubnetParams 5 fields, 27 events, relay 100/IP/1h, emission [DRAFT] |
| 1.4.0 | Merged awp + awp-monitor into single skill |
| 1.3.0 | Split api-reference into focused command files, session state tracking |
| 1.2.0 | On Skill Load protocol, intent routing, version check |
| 1.1.0 | Welcome messages, executable command templates, EIP-712 templates |
| 1.0.0 | Initial release — 21 actions + 28 event types |

## Contributing

1. Switch to the `dev` branch and update source documents in `skills-dev/`
2. Regenerate skill files to match the updated specifications
3. Run eval tests to verify correctness
4. Submit a pull request to `main`

## License

[MIT](LICENSE)
