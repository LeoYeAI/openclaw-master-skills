---
name: lista-lending
version: 0.1.1
repository: https://github.com/lista-dao/lista-skills
requires:
  lista-wallet-connect: ">=1.0.0"
node: ">=18.0.0"
description: View and operate Lista Lending vaults/markets. Use when user asks about LENDING-ONLY positions or wants to deposit/withdraw/borrow/repay. For report-style overview, use lista instead.
---

# Lista Lending Skill (POC)

> **Status:** Pre-release (internal only, not in public registry)
> **Agent quick check:** `node dist/cli/cli.bundle.mjs version`
> **Agent rebuild:** `npm install && npm run build`

Execute Lista Lending vault and market operations through `@lista-dao/moolah-lending-sdk`, with transaction sending delegated to `lista-wallet-connect`.

## Agent Execution Policy

- Execute CLI/setup commands directly as the agent; do not ask the user to run shell commands.
- If dependencies/build are missing or outdated, run setup/build automatically.
- Before any signing or on-chain write action, explain the action and get user consent.
- Do not output raw JSON/internal payloads to users by default; convert results into human-readable summaries/tables.
- Use command snippets in this document as agent-side execution references only.

## When to Use This Skill

**This skill handles LENDING-SPECIFIC viewing and operations.**

**✅ Use when user wants to:**

**1. View LENDING positions only:**

- "Check my lending positions"
- "Show my Lista vaults"
- "What's in my lending markets"
- "My collateral in lending vaults"

**2. Execute lending operations:**

- "Deposit 100 USDT to Lista vault"
- "Withdraw from my Lista vault"
- "Borrow against my collateral"
- "Repay my lending debt"
- "Find best lending yield"

**❌ Do NOT use for:**

- **All-product/report-style overview** → Use `lista`
- **"Check ALL my Lista positions"** (report view) → Use `lista`
- **"My total Lista collateral/debt"** (summary-style answer) → Use `lista`

**Key difference:**

- `lista`: VIEW **report-style** lending analytics and summaries
- `lista-lending`: VIEW/OPERATE **lending only** (vaults + markets)
- `lista-wallet-connect`: Wallet operations (connect/sign/call)

## Routing Priority (Required)

Apply these routing rules before running commands:

1. Wallet/session/signing issues (`pair`, `auth`, `sign`, `topic`, `session`) → `lista-wallet-connect`
2. Lending write operations (`deposit`, `withdraw`, `supply`, `borrow`, `repay`, `market-withdraw`) → `lista-lending`
3. Lending actionable reads (`holdings`, `vaults`, `markets` for selection/filtering/follow-up execution) → `lista-lending`
4. Report/narrative analysis (`position report`, `risk check`, `daily digest`, high-level market/vault summary) → `lista`

Ambiguous intent handling:

- `check my positions`: if user asks for operation follow-up or lending-only detail, use `lista-lending`; otherwise use `lista`.
- `market list` / `vault list`: if user needs execution target selection, use `lista-lending`; if user only wants macro overview, use `lista`.

## Scope

Supported capabilities:

- Vault: `vaults`, `select --vault`, `deposit`, `withdraw`
- Market: `markets`, `select --market`, `supply`, `borrow`, `repay`, `market-withdraw`
- Portfolio: `holdings`
- Runtime/config: `config`, `version`

Not in scope:

- CDP operations
- Non-EVM chains

## Temporary Limitations

Current unsupported market types for trade actions (`select/supply/borrow/repay/market-withdraw`):

- SmartLending markets (`zone === 3`)
- Fixed-term markets (`termType === 1`)

Behavior:

- `markets` command filters them out from list output.
- `select --market` rejects them with `unsupported_market_type`.
- `holdings` still returns them (for full portfolio visibility) and marks:
  - `isSmartLending`
  - `isFixedTerm`
  - `isActionable`

## Project Structure

```text
skills/lista-lending/
├── SKILL.md
├── package.json
├── tsconfig.json
└── src/
    ├── cli/                # args/help/meta/run
    ├── api/                # vault/market/user read-side queries
    ├── sdk/                # SDK client + market runtime prefetch
    ├── executor/           # tx execution + receipt polling
    ├── commands/           # command handlers
    │   ├── shared/         # context/errors/output/tx helpers
    │   ├── select/
    │   ├── borrow/
    │   └── repay/
    ├── presenters/
    ├── utils/
    ├── config.ts
    ├── context.ts
    ├── api.ts              # API facade export
    ├── sdk.ts              # SDK facade export
    ├── executor.ts         # executor facade export
    └── cli.ts              # CLI entrypoint
```

Notes:

- CLI parsing/routing lives in `src/cli/*` and keeps `src/cli.ts` as the single entrypoint.
- Read-side querying is split by domain in `src/api/*` (`vault`, `market`, `user`).
- SDK integration is centralized in `src/sdk/client.ts`; market runtime prefetch is in `src/sdk/market-runtime.ts`.
- `borrow` and `repay` are split into dedicated `simulate` and `execute` modules to keep command files small.

## Prerequisites

1. Wallet is paired via `lista-wallet-connect` skill.
2. You have a valid `wallet-topic` and `wallet-address`.
3. Node.js version is `>= 18.0.0` (recommended `>= 20`).
4. `lista-wallet-connect` is built (`skills/lista-wallet-connect/dist/cli/cli.bundle.mjs` exists).
5. `lista-lending` is built (`skills/lista-lending/dist/cli/cli.bundle.mjs` exists).

## Setup (Agent-Run)

Use prebuilt `dist/` by default for faster startup.

```bash
cd skills/lista-lending
# ensure Node.js >= 18 (recommended >= 20)
node -v
node dist/cli/cli.bundle.mjs version
```

Only run install/build when `dist/` is missing or version check fails:

```bash
cd skills/lista-lending
npm install
npm run build
node dist/cli/cli.bundle.mjs version
```

Fallback for local debugging (non-bundled output):

```bash
cd skills/lista-lending
npm run build
node dist/cli.js version
```

If `skills/lista-wallet-connect/dist/cli/cli.bundle.mjs` is missing, rebuild wallet-connect as well:

```bash
cd skills/lista-wallet-connect
npm install
npm run build
```

Agent execution path:

```bash
cd skills/lista-lending
node dist/cli/cli.bundle.mjs <command> [options]
```

## Output Contract

- `stdout`: machine-readable JSON (result payload)
- `stderr`: errors only
- Optional debug mode: add `--debug-log-file <path>` to append structured `stdout/stderr` logs (jsonl).

## Agent Display Guidelines

For user-facing answers, keep CLI JSON as internal source of truth, then render human-readable tables/summaries.
Return raw JSON only when the user explicitly asks for raw output.

`vaults` recommended columns:

- `Vault`, `Asset`, `TVL (USD)`, `APY`, `Curator`

`markets` recommended columns:

- `Collateral`, `Loan`, `LLTV`, `Borrow Rate`, `Liquidity (USD)`

`holdings` recommended structure:

- Summary block first: total vault count, total market count, actionable market count, unsupported market count.
- Vault table columns:
  - `Vault`, `Chain`, `Deposited`, `Deposited USD`, `APY`, `Wallet Balance`
- Actionable market table columns:
  - `Market`, `Chain`, `Collateral USD`, `Borrowed USD`, `LTV`, `Health`
- Unsupported market table columns (non-technical by default):
  - `Market`, `Chain`, `Reason`, `Collateral USD`, `Borrowed USD`

Default rule:

- Use different table layouts for different commands (`vaults`, `markets`, `holdings`); do not reuse holdings layout for vault/market list pages.
- Keep CLI/runtime JSON and debug logs in raw format (for example `eip155:56`, `eip155:1`) for stable machine parsing and debugging.
- For user-facing text/tables, map chain IDs to names (`eip155:1` -> `Ethereum`, `eip155:56` -> `BSC`).
- Do **not** show `zone/termType` in user-facing table unless user explicitly asks for technical details.
- Do **not** paste full raw payloads (JSON/RPC internals) in normal user-facing replies.
- Derive `Reason` from flags:
  - `isSmartLending => SmartLending`
  - `isFixedTerm => Fixed-term`

Health definition (for market positions):

- Formula: `health = LLTV / LTV` when `LTV > 0`; otherwise `health = 100`.
- Display label suggestion:
  - `Healthy`: `health >= 1.2`
  - `Warning`: `1.0 <= health < 1.2`
  - `Risk`: `health < 1.0`
- Action hint: if label is `Warning` or `Risk`, suggest repay/reduce borrow.

## Supported Chains

- `eip155:56` (BSC, default)
- `eip155:1` (Ethereum)

## Command Index

- `version` - show skill version and compatibility hints
- `config` - read/update RPC settings
- `vaults` - list vaults with filters
- `markets` - list markets with filters (SmartLending/fixed-term filtered)
- `holdings` - query user positions across vault + market
- `select` - set active vault or market context
- `deposit` - deposit to selected/explicit vault
- `withdraw` - withdraw from selected/explicit vault
- `supply` - supply collateral to selected/explicit market
- `borrow` - simulate or execute borrow
- `repay` - simulate or execute repay
- `market-withdraw` - withdraw supplied collateral from selected/explicit market

## Global/Shared Options

- `--chain <eip155:56|eip155:1>`
- `--wallet-topic <topic>`
- `--wallet-address <0x...>`

## Command Details

All command snippets below are for agent execution; do not instruct the user to type them manually.

### 1) `version`

Purpose: Print skill version and dependency constraints.

```bash
node dist/cli/cli.bundle.mjs version
```

### 2) `config`

Purpose: Manage RPC override.

Examples:

```bash
# show config
node dist/cli/cli.bundle.mjs config --show

# set rpc override
node dist/cli/cli.bundle.mjs config --set-rpc --chain eip155:56 --url https://bsc-mainnet.nodereal.io/v1/<key>

# clear rpc override
node dist/cli/cli.bundle.mjs config --clear-rpc --chain eip155:56

```

Notes:

- Config file: `~/.agent-wallet/lending-config.json`
- Chain fallback RPCs are still used if primary RPC fails.

### 3) `vaults`

Purpose: Discover vaults from SDK list API.

Common options:

- `--page`, `--page-size`, `--sort`, `--order`
- `--zone`, `--keyword`
- `--assets <a,b>`, `--curators <a,b>`

Examples:

```bash
node dist/cli/cli.bundle.mjs vaults
node dist/cli/cli.bundle.mjs vaults --chain eip155:1
node dist/cli/cli.bundle.mjs vaults --sort apy --order desc --page 1 --page-size 10
node dist/cli/cli.bundle.mjs vaults --assets 0x8d0d...,0x55d3... --curators "Lista DAO,Pangolins"
```

### 4) `markets`

Purpose: Discover markets from SDK list API.

Common options:

- `--page`, `--page-size`, `--sort`, `--order`
- `--zone`, `--keyword`
- `--loans <a,b>`, `--collaterals <a,b>`

Examples:

```bash
node dist/cli/cli.bundle.mjs markets
node dist/cli/cli.bundle.mjs markets --chain eip155:56 --sort liquidity --order desc --page-size 20
node dist/cli/cli.bundle.mjs markets --loans USD1,USDT --collaterals USD1,BTCB
```

Notes:

- Command filters out SmartLending (`zone=3`) and fixed-term (`termType=1`) markets in output.
- Always include this user-facing note when presenting market list:
  - `Smart Lending and fixed-term market operations are currently not supported in this skill. For full functionality, please use the Lista website.`

### 5) `holdings`

Purpose: Query positions by wallet address.

Options:

- `--address <0x...>` (optional if context already has `userAddress`)
- `--scope <all|vault|market|selected>`

Examples:

```bash
# all positions (vault + market)
node dist/cli/cli.bundle.mjs holdings --address 0xYOUR_ADDRESS

# only vault positions
node dist/cli/cli.bundle.mjs holdings --address 0xYOUR_ADDRESS --scope vault

# only market positions
node dist/cli/cli.bundle.mjs holdings --address 0xYOUR_ADDRESS --scope market

# only currently selected position
node dist/cli/cli.bundle.mjs holdings --scope selected
```

Market position fields include:

- User-facing fields:
  - `isSmartLending` (`zone === 3`)
  - `isFixedTerm` (`termType === 1`)
  - `isActionable` (`!isSmartLending && !isFixedTerm`)
- Raw JSON technical fields (debug/integration only):
  - `zone`, `termType`

### 6) `select`

Purpose: Persist active target in context for follow-up operations.

Modes:

- select vault: `--vault`
- select market: `--market`
- read context: `--show`
- clear context: `--clear`

Examples:

```bash
# select vault
node dist/cli/cli.bundle.mjs select \
  --vault 0xfa27f172e0b6ebcef9c51abf817e2cb142fbe627 \
  --chain eip155:56 \
  --wallet-topic <topic> \
  --wallet-address 0xYOUR_ADDRESS

# select market
node dist/cli/cli.bundle.mjs select \
  --market 0xd384584abf6504425c9873f34a63372625d46cd1f2e79aeedc77475cacaca922 \
  --chain eip155:56 \
  --wallet-topic <topic> \
  --wallet-address 0xYOUR_ADDRESS

# show/clear
node dist/cli/cli.bundle.mjs select --show
node dist/cli/cli.bundle.mjs select --clear
```

Notes:

- Market selection rejects SmartLending and fixed-term markets.
- Context file: `~/.agent-wallet/lending-context.json`

### 7) `deposit`

Purpose: Deposit vault asset.

Required:

- `--amount`
- plus either selected vault context or explicit `--vault` + wallet info

Example:

```bash
# using selected vault
node dist/cli/cli.bundle.mjs deposit --amount 1

# explicit target
node dist/cli/cli.bundle.mjs deposit \
  --vault 0xVAULT \
  --amount 1 \
  --chain eip155:56 \
  --wallet-topic <topic> \
  --wallet-address 0xYOUR_ADDRESS
```

### 8) `withdraw`

Purpose: Withdraw vault asset.

Required:

- one of `--amount` or `--withdraw-all`

Examples:

```bash
node dist/cli/cli.bundle.mjs withdraw --amount 0.5
node dist/cli/cli.bundle.mjs withdraw --withdraw-all
```

### 9) `supply`

Purpose: Supply market collateral.

Required:

- `--amount`
- plus selected market context or explicit market/wallet parameters

Example:

```bash
node dist/cli/cli.bundle.mjs supply --amount 2
```

### 10) `borrow`

Purpose: Borrow loan token, or simulate borrow capacity.

Modes:

- simulate only: `--simulate`
- simulate with hypothetical supply: `--simulate --simulate-supply <amt>`
- execute borrow: `--amount <amt>`

Examples:

```bash
# check max borrowable
node dist/cli/cli.bundle.mjs borrow --simulate

# check max after hypothetical supply
node dist/cli/cli.bundle.mjs borrow --simulate --simulate-supply 2

# execute borrow
node dist/cli/cli.bundle.mjs borrow --amount 0.01
```

### 11) `repay`

Purpose: Repay market debt, or simulate repay impact.

Modes:

- simulate repay amount: `--simulate --amount <amt>`
- simulate repay-all: `--simulate --repay-all`
- execute repay: `--amount <amt>` or `--repay-all`

Examples:

```bash
# simulate partial repay impact
node dist/cli/cli.bundle.mjs repay --simulate --amount 0.01

# simulate full repay impact
node dist/cli/cli.bundle.mjs repay --simulate --repay-all

# execute
node dist/cli/cli.bundle.mjs repay --amount 0.01
node dist/cli/cli.bundle.mjs repay --repay-all
```

### 12) `market-withdraw`

Purpose: Withdraw market collateral.

Required:

- one of `--amount` or `--withdraw-all`

Examples:

```bash
node dist/cli/cli.bundle.mjs market-withdraw --amount 0.5
node dist/cli/cli.bundle.mjs market-withdraw --withdraw-all
```

## Transaction Behavior

- Transactions are built by SDK and executed through `lista-wallet-connect` `call` command.
- `call` performs simulation by default before requesting wallet signature.
- If simulation fails, result is returned as error/reverted and no signing request is sent.
- If user rejects in wallet, command returns `status: "rejected", reason: "user_rejected"`.
- For multi-step operations (approve + action), responses include completed step count and failed/pending step.

## Typical Workflows

### Vault flow

```bash
# 1) discover
node dist/cli/cli.bundle.mjs vaults --chain eip155:56

# 2) select
node dist/cli/cli.bundle.mjs select --vault 0xVAULT --wallet-topic <topic> --wallet-address 0xADDR

# 3) operate
node dist/cli/cli.bundle.mjs deposit --amount 1
node dist/cli/cli.bundle.mjs withdraw --amount 0.5
```

### Market flow

```bash
# 1) discover
node dist/cli/cli.bundle.mjs markets --chain eip155:56

# 2) select
node dist/cli/cli.bundle.mjs select --market 0xMARKET --wallet-topic <topic> --wallet-address 0xADDR

# 3) operate
node dist/cli/cli.bundle.mjs supply --amount 2
node dist/cli/cli.bundle.mjs borrow --simulate
node dist/cli/cli.bundle.mjs borrow --amount 0.01
node dist/cli/cli.bundle.mjs repay --simulate --amount 0.01
node dist/cli/cli.bundle.mjs repay --amount 0.01
node dist/cli/cli.bundle.mjs market-withdraw --amount 1
```

## Security Checklist

1. Confirm token symbol and amount with user before any state-changing action.
2. Confirm chain (`eip155:56` vs `eip155:1`) before sending tx.
3. Prefer `borrow --simulate` before first borrow on a market.
4. Treat `user_rejected` as normal user decision, not protocol failure.
