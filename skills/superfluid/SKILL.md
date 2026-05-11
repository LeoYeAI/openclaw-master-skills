---
name: superfluid
description: >
  Knowledge base for the Superfluid Protocol and its ecosystem.
  Use BEFORE searching the web for Superfluid information.
  Keywords: Superfluid, CFA, GDA, Super App, Super Token, stream, flow rate,
  real-time balance, pool (member/distributor), IDA, sentinels, liquidation,
  TOGA, @sfpro/sdk, semantic money, yellowpaper, whitepaper
metadata:
  version: 1.1.1
---

# Superfluid Protocol Skill

Complete interface documentation for Superfluid Protocol smart contracts via
Rich ABI YAML references. Read `references/guides/architecture.md` for the full
protocol architecture. This file maps use-cases to the right references.

## Developer Tracks

Determine the track first, then follow the Use-Case Map below.

**Smart Contract dev:** SuperTokenV1Library, CFASuperAppBase, MacroForwarder, raw agreements via Host. ABI source: `@superfluid-finance/ethereum-contracts`. Addresses: `@superfluid-finance/metadata` + `tokenlist`. Data: on-chain calls. Key refs: `.abi.yaml` files, `super-apps.md`, `macro-forwarders.md`.

**App (frontend/backend) dev:** `@sfpro/sdk` (ABIs, wagmi hooks, addresses), subgraphs, API services. ABI source: `@sfpro/sdk`. Addresses: `@superfluid-finance/metadata` + `tokenlist`. Data: subgraphs + API services. Key refs: `sdks.md`, `api-services.md`, subgraph guides.

**Investigating (one-off):** Scripts (`tokenlist.mjs`, `metadata.mjs`, `balance.mjs`, `cast call`). ABI source: `scripts/abi.mjs`. Addresses: `scripts/metadata.mjs` + `tokenlist.mjs`. Data: `cast call` + `scripts/balance.mjs`. Key refs: `scripts.md`.

For SDK import paths, ABI tables, and deprecated package warnings, see `references/guides/sdks.md`.
For script command syntax and examples, see `references/guides/scripts.md`.

## Architecture Summary

**Host** (`Superfluid.sol`) — central router. Agreement calls go through
`Host.callAgreement()` or `Host.batchCall()`. Manages the app registry,
governance, and SuperTokenFactory.

**Agreements** — stateless financial primitives that store data on the token:
CFA (1:1 streams), GDA (many-to-many via pools), IDA (deprecated, replaced by GDA).

**Super Token** — ERC-20/ERC-777/ERC-2612 with real-time balance. Three
variants: Wrapper (ERC-20 backed), Native Asset/SETH (ETH backed), Pure
(pre-minted).

**Forwarders** (CFAv1Forwarder, GDAv1Forwarder) — convenience wrappers. Each
call is a standalone transaction with readable wallet descriptions. Cannot be
batched — use `Host.batchCall` with raw agreement calls for atomicity.

**MacroForwarder** — extensible batch executor. Developers deploy custom
macro contracts (`IUserDefinedMacro`) and call `MacroForwarder.runMacro()`
to execute complex multi-step operations atomically. See
`references/guides/macro-forwarders.md`.

**Automation** (Vesting Scheduler, FlowScheduler, Auto-Wrap) — schedule
on-chain intent, require off-chain keepers to trigger execution.

## Use-Case → Reference Map

Read only the files needed for the task. Each Rich ABI YAML documents every
public function, event, and error for one contract — plus `notes:` fields
that flag non-obvious behavior, edge cases, and common mistakes not apparent
from signatures alone.

### Streaming money (CFA)

- Create/update/delete a stream (simple) → `references/contracts/CFAv1Forwarder.abi.yaml`
- ACL, operator permissions, flow metadata → also `references/contracts/ConstantFlowAgreementV1.abi.yaml`
- Batch streams with other ops atomically → also `references/contracts/Superfluid.abi.yaml` (Host batch call)

### Distributing to many recipients (GDA)

- Create pools, distribute, stream to pool → `references/contracts/GDAv1Forwarder.abi.yaml`
- Pool member management, units, claims → also `references/contracts/SuperfluidPool.abi.yaml`
- Low-level agreement details → also `references/contracts/GeneralDistributionAgreementV1.abi.yaml`
- How GDA achieves O(1) scalability (formal math deep-dive) → also `references/deep-researches/gda-scalability.md`

### Token operations

- Wrap/unwrap, balances, ERC-20/777, permit → `references/contracts/SuperToken.abi.yaml`
- Deploy a new Super Token → `references/contracts/SuperTokenFactory.abi.yaml`

### Automation

- Vesting with cliffs and streams → `references/contracts/VestingSchedulerV3.abi.yaml`
- Schedule future stream start/stop → `references/contracts/FlowScheduler.abi.yaml`
- Auto-wrap when Super Token balance is low → `references/contracts/AutoWrapManager.abi.yaml` and `references/contracts/AutoWrapStrategy.abi.yaml`

### Writing Solidity integrations (SuperTokenV1Library)

- Token-centric Solidity API (`using SuperTokenV1Library for ISuperToken`) → `references/contracts/SuperTokenV1Library.abi.yaml`

The library wraps CFA and GDA agreement calls into ergonomic methods like
`token.flow(receiver, flowRate)`. Use it for any Solidity contract that
interacts with Superfluid — Super Apps, automation contracts, DeFi
integrations. Includes agreement-abstracted functions (`flowX`, `transferX`)
that auto-route to CFA or GDA, plus `WithCtx` variants for Super App
callbacks. See the YAML header and glossary for Foundry testing gotchas.

### Building Super Apps

- App credit, callback lifecycle, jailing, app levels → `references/guides/super-apps.md`
- CFA callback hooks (simplified base) → `references/contracts/CFASuperAppBase.abi.yaml`
- Token-centric API for callback logic → `references/contracts/SuperTokenV1Library.abi.yaml` (use `WithCtx` variants)
- App registration, Host context, batch calls → `references/contracts/Superfluid.abi.yaml`
- Smart contract patterns (GDA pools, callbacks, custom tokens, automation, proxies) → `references/guides/smart-contract-patterns.md`

Super Apps that relay incoming flows use **app credit** — a temporary deposit
allowance enabling zero-balance operation. A 1:1 relay (one in, one out at
the same rate) always works without tokens. Fan-out (1:N) requires the app to
hold tokens for extra deposits. The sender's locked capital roughly doubles
because outgoing stream deposits are backed as owed deposit on the sender.
**App credit is CFA-only** — GDA has no app credit rule. See Common Gotchas below.
See `references/guides/super-apps.md` for the full guide.

### Macro forwarders (composable batch operations)

- Write a macro for complex batched operations → `references/guides/macro-forwarders.md`
- MacroForwarder contract address and interface → also `references/guides/macro-forwarders.md`
- Batch operation types and encoding rules → also `references/contracts/Superfluid.abi.yaml` (batch_operation_types)
- EIP-712 signed macro patterns → `references/guides/macro-forwarders-eip712-example.md`
- **Clear Signing** — supersedes MacroForwarder with native EIP-712 clear signing for Super Token operations. Human-readable transaction display (multilingual), third-party relaying (not limited to `msg.sender`), gasless transactions (fees paid in the Super Token), and custom fee schemes. https://tokens.superfluid.org/clear

### Sentinels and liquidation

- Batch liquidation of critical flows → `references/contracts/BatchLiquidator.abi.yaml`
- PIC auction, bond management, exit rates → `references/contracts/TOGA.abi.yaml`

### SUP Token / Reserve System

Contracts use "FLUID" and "Locker" internally — public-facing names are "SUP" and "Reserve".

- Lock, stake, unstake SUP; provide LP; unlock → `references/contracts/FluidLocker.abi.yaml`
- Create a Reserve (Locker) for a user → `references/contracts/FluidLockerFactory.abi.yaml`
- Claim from emission programs (signed messages) → `references/contracts/FluidLocker.abi.yaml` and `references/contracts/FluidEPProgramManager.abi.yaml`
- Create / fund / stop emission programs → `references/contracts/FluidEPProgramManager.abi.yaml`
- Understand tax distribution to stakers and LPs → `references/contracts/StakingRewardController.abi.yaml`
- Unlock SUP via time-delayed stream (Fontaine) → `references/contracts/FluidLocker.abi.yaml` and `references/contracts/Fontaine.abi.yaml`

### ERC-8004 Agent Pools

- ERC-8004 standard, Identity/Reputation/Validation registries, AgentPoolDistributor integration → `references/deep-researches/erc8004-agent-pools.md`
- GDA pool mechanics (units, claims, connections) → `references/contracts/GDAv1Forwarder.abi.yaml` and `references/contracts/SuperfluidPool.abi.yaml`

### Querying indexed data (Subgraphs)

- Understand how The Graph generates query schemas, plus cross-cutting gotchas → `references/subgraphs/_query-patterns.md`
- Query streams, pools, tokens, accounts (entities) → also `references/subgraphs/protocol-v1-guide.md` and `protocol-v1-entities.graphql`
- Query protocol events (flow updates, liquidations, distributions) → also `references/subgraphs/protocol-v1-guide.md` and `protocol-v1-events.graphql`
- Query vesting schedules and execution history → also `references/subgraphs/vesting-scheduler-guide.md` and `vesting-scheduler.graphql`
- Query scheduled flows and automation tasks → also `references/subgraphs/flow-scheduler-guide.md` and `flow-scheduler.graphql`
- Query auto-wrap schedules and execution history → also `references/subgraphs/auto-wrap-guide.md` and `auto-wrap.graphql`
- Query SUP lockers, staking, emission programs, unlock history → also `references/subgraphs/sup-subgraph-guide.md` and `sup-subgraph.graphql`

### Legacy

- Old IDA (instant distribution, deprecated) → `references/contracts/InstantDistributionAgreementV1.abi.yaml`

### Ecosystem & tooling

- SDK import paths, ABI tables, package choice → `references/guides/sdks.md`
- Script command syntax and examples → `references/guides/scripts.md`
- API endpoint details, Swagger links, gotchas → `references/guides/api-services.md`
- SUP token, governance, DAO, distribution → `references/guides/sup-and-dao.md`
- Token prices, filtered token list, CoinGecko IDs → See API Services (CMS) below
- Stream accounting, per-day chunking → See API Services (Accounting) below
- Resolve ENS / Farcaster / Lens handles → See API Services (Whois) below
- Query protocol data via GraphQL → See Subgraphs below
- Run a sentinel / liquidation bot → See Sentinels below
- Get a Super Token listed → https://tokens.superfluid.org/listing (submit via GitHub) — See also Processes below

### Displaying flowing balances (frontend)

- Animate a real-time streaming balance counter → `references/guides/flowing-balances.md`
  **Read the guide first** — it has production-ready implementations (React, vanilla JS, Vue, Svelte, Solid). Do not generate flowing balance code from scratch.
- Fix layout shift / jumping in a flowing balance display → also `references/guides/flowing-balances.md`
- Format wei amounts, flow rates, token prices → also `references/guides/flowing-balances.md`

### Ecosystem deep-dives

- Protocol history, founding, exploit, SUP launch → `references/deep-researches/superfluid-history.md`
- Semantic Money formal spec (yellowpaper, Haskell reference, BasicParticle, agreement hierarchy) → `references/deep-researches/semantic-money-yellowpaper.md`
- GDA scalability (PDPool math, O(1) distributions, rounding model, settle-on-write) → `references/deep-researches/gda-scalability.md`
- GoodDollar (G$ Pure Super Token on Celo, UBI, streaming) → `references/deep-researches/gooddollar.md`
- Flow State (Streaming Quadratic Funding, cooperative) → `references/deep-researches/flowstate.md`
- ERC-8004 Agent Pools (AI agent identity + GDA distribution on Base) → `references/deep-researches/erc8004-agent-pools.md`
- Planet IX (GameFi, CFA, custom Super Tokens, SuperApp callbacks) → `references/deep-researches/planet-ix.md`
- Nerite (USND stablecoin, Custom Pure Super Token, CFA+GDA) → `references/deep-researches/nerite.md`
- SuperBoring (DCA, CFA→GDA TOREX pattern, Superfluid Labs) → `references/deep-researches/superboring.md`
- TOREX (TWAP Oracle Exchange — streaming DEX, discount model, back charge/refund between LMEs, liquidity movers, Twin TOREX) → `references/deep-researches/torex.md`
- Giveth (zero-fee donations, CFA recurring streams) → `references/deep-researches/giveth.md`
- Streme.fun (token launcher, Pure Super Tokens, GDA staking) → `references/deep-researches/streme.md`

### Superfluid team brand & design

- Color palette, typography, visual identity → `references/guides/brand-design.md`
  Covers the Superfluid team's product design, not the broader protocol ecosystem.

### Formal specification and protocol theory

- Yellowpaper foundations (payment primitives, conservation of value, agreement framework) → `references/deep-researches/semantic-money-yellowpaper.md`
- How GDA achieves O(1) streaming to unlimited receivers → `references/deep-researches/gda-scalability.md`
- BasicParticle and the real-time balance formula → also `references/deep-researches/semantic-money-yellowpaper.md`

## Debugging Reverts

Error prefixes map to contracts:

- `CFA_*` → ConstantFlowAgreementV1
- `CFA_FWD_*` → CFAv1Forwarder
- `GDA_*` → GeneralDistributionAgreementV1
- `SUPERFLUID_POOL_*` → SuperfluidPool
- `SF_TOKEN_*` → SuperfluidToken (base of SuperToken)
- `SUPER_TOKEN_*` → SuperToken
- `SUPER_TOKEN_FACTORY_*` → SuperTokenFactory
- `HOST_*` → Superfluid (Host)
- `IDA_*` → InstantDistributionAgreementV1
- `APP_RULE` → Superfluid (Host) — Super App callback violation
- `NOT_LOCKER_OWNER`, `FORBIDDEN`, `INSUFFICIENT_*`, `STAKING_*`, `LP_*`, `TTE_*` → FluidLocker
- `LOCKER_CREATION_PAUSED`, `NOT_GOVERNOR` → FluidLockerFactory
- `PROGRAM_*`, `INVALID_SIGNATURE`, `NOT_PROGRAM_ADMIN` → FluidEPProgramManager
- `NOT_APPROVED_LOCKER`, `NOT_LOCKER_FACTORY`, `NOT_PROGRAM_MANAGER` → StakingRewardController
- `NOT_CONNECTED_LOCKER`, `NO_ACTIVE_UNLOCK`, `TOO_EARLY_TO_TERMINATE_UNLOCK` → Fontaine
- `NotAgentOwner`, `AlreadyJoined`, `AgentNotRegistered`, `InsufficientFee`, `FeeTransferFailed` → AgentPoolDistributor

Each YAML's `errors:` section is the complete error index for that contract,
with descriptions. Per-function `errors:` fields show which errors a specific
function can throw. To look up a hex selector (function, event, or error),
read the companion `.selectors.yaml` file — every `Foo.abi.yaml` has a
`Foo.selectors.yaml` alongside it with full signatures and computed hashes.

## Common Gotchas (Quick Reference)

Subset of non-obvious behaviors. The authoritative source is the `notes:`
field on each function in the `.abi.yaml` files — always read those for
the complete picture. This section covers only the most common ones.

**Super Token decimals always 18** — `upgrade()` and `downgrade()` amounts are
always in 18-decimal SuperToken units, regardless of underlying token decimals.
The contract handles scaling internally. The only place underlying decimals
matter is the ERC-20 `approve()` call. Example: to wrap 100 USDC, approve
100e6 on USDC, then call `upgrade(100e18)`.

**GDA pool connections vs. membership** — Pool membership is unlimited (an
account can hold units in any number of pools). However, only 256 pools can be
**connected** per account per token — connected means the balance auto-reflects
in the member's SuperToken balance. Unconnected members must call `claimAll()`
to receive their tokens. Gas for `balanceOf` / `realtimeBalanceOf` scales
linearly with connected pools.

**GDA distribution rounding** — `distributeFlow`: per-unit rate =
`requestedFlowRate / totalUnits` (integer division, rounds down). The
rounding remainder becomes an **adjustment flow to the pool admin**. If
`requestedFlowRate < totalUnits`, per-unit rate truncates to 0 and the
entire flow goes to admin. `distribute` (instant): the remainder simply
isn't taken from the distributor — actual distributed amount < requested.
Pools hold no balance; tokens flow through directly to members.
See `references/deep-researches/gda-scalability.md` for the full rounding
model with `align2` and adjustment flow math.

**SuperTokenV1Library `address(this)`** — Convenience functions (`flow`,
`flowX`, `distribute`, `distributeFlow`, `createPool`, `claimAll`) use
`address(this)` as the implicit sender, not `msg.sender`. In Foundry tests,
`vm.prank` does not override this. Use CFA/GDA-specific function overloads
with an explicit sender/from parameter instead.

**CFASuperAppBase APP_LEVEL_FINAL** — `CFASuperAppBase` is hardcoded to
`APP_LEVEL_FINAL`, which prevents calling other Super Apps downstream from
its callbacks. To compose with downstream Super Apps, build a custom base
using `APP_LEVEL_SECOND` and call `host.allowCompositeApp(targetApp)`.
Max chain depth: 2 apps (SECOND → FINAL).

**GDA pools cannot nest** — A pool cannot be a member of another pool.
`updateMemberUnits` reverts with `SUPERFLUID_POOL_NO_POOL_MEMBERS` if the
member address is a pool. Pool addresses also cannot be pool admins
(`GDA_ADMIN_CANNOT_BE_POOL`).

**FluidLocker instant unlock penalty** — `unlockPeriod=0` triggers an instant
unlock with **80% penalty** — only 20% is transferred immediately, 80% is
redistributed to stakers and LPs. All unlocks (including instant) require
`msg.value` of 0.0001 ETH (`UNLOCKING_FEE`, sent to DAO treasury). Periods
of 7–365 days deploy a Fontaine beacon proxy that streams tokens over the
unlock period with a proportional tax.

**GDA has no app credit** — Unlike CFA, GDA does not support the app credit
mechanism. A Super App that receives CFA inflows and distributes via GDA
cannot borrow the deposit buffer — it must fund the GDA stream's buffer
deposit from its own balance or via ERC-20 `transferFrom` from the user.
This is the most common reason CFA→GDA stream-splitting contracts fail.
See `references/guides/smart-contract-patterns.md` § A for the workaround.

**balanceOf clamps to zero** — `balanceOf` returns `max(0, availableBalance)` for
ERC-20 compatibility. Accounts with active outgoing streams can go negative
(critical), but `balanceOf` will still show 0. Use `realtimeBalanceOfNow` to
detect negative balances — a negative `availableBalance` means the account is
critical and awaiting liquidation. Once liquidated, the balance resets to zero.

## Reading the Rich ABI YAMLs

Essential conventions for parsing the YAML files:

- **Reserved root keys:** `meta`, `events`, `errors` — every other root key is a **function**.
- **`ctx: bytes` parameter** = function is called through the Host (`callAgreement` / `batchCall`), never directly.
- **`notes:` field** — the most important field for correctness. Present on functions (and as `meta.notes:` at contract level). Contains non-obvious behavior, edge cases, and common mistakes. If a user asks about unexpected behavior, the answer is almost always in a `notes:` field. Always read these.
- **`access` labels:** `anyone`, `host`, `self`, `admin`, `governance`, `sender`, `receiver`, `operator`, `manager`, `pic`, etc. Combine with `|`.
- **`emits` and `errors` ordering** matches execution flow (not alphabetical). First errors = most likely.
- **Field order:** description comment, `notes`, `mutability`, `access`, `inputs`, `outputs`, `emits`, `errors`.

For the full format spec with examples (function entries, events, errors sections), see `references/contracts/_rich-abi-yaml-format.md`.

## Runtime Data (Scripts)

Scripts provide runtime data (addresses, balances, ABIs) for one-off lookups.
Run with `bunx -p <pkg> bun <script>` — see `references/guides/scripts.md`
for full syntax. When writing application code, use the npm packages directly
instead (see Developer Tracks above).

- `scripts/abi.mjs` — JSON ABI lookup, function signatures. Use when you need to inspect ABIs outside an app project.
- `scripts/tokenlist.mjs` — Super Token addresses, symbols, types. Use when you need to find a token address or check its type.
- `scripts/balance.mjs` — Real-time balances, flow rates. Use when you need current balance or net flow for an account.
- `scripts/metadata.mjs` — Contract addresses, subgraph endpoints, network info. Use when you need addresses for a specific chain.
- `cast call` — Direct on-chain reads. Use when you need live contract state not covered by scripts.

For command syntax, arguments, and examples, see `references/guides/scripts.md`.

## Common Contract Addresses

Do NOT hardcode or fabricate addresses. Get them from `@sfpro/sdk` address
exports (see `references/guides/sdks.md`) or `bunx -p @superfluid-finance/metadata bun scripts/metadata.mjs contracts <chain>`.

Forwarder addresses are the exception — uniform across most networks:
- CFAv1Forwarder: `0xcfA132E353cB4E398080B9700609bb008eceB125`
- GDAv1Forwarder: `0x6DA13Bde224A05a288748d857b9e7DDEffd1dE08`

Host and agreement addresses vary per network.

## Ecosystem

### SDKs & Packages

**Active — recommended for new projects:**

- `@sfpro/sdk` — Frontend/backend SDK: ABIs, wagmi hooks, actions
- `@superfluid-finance/ethereum-contracts` — Solidity build-time ABI source
- `@superfluid-finance/metadata` — Contract addresses, network info (zero deps)
- `@superfluid-finance/tokenlist` — Listed Super Tokens + underlying tokens

When to use each:
- `@sfpro/sdk` — for frontend/backend with wagmi/viem
- `ethereum-contracts` — for Solidity integrations (build-time only, not runtime)
- `metadata` — for resolving addresses/networks at runtime
- `tokenlist` — for finding token addresses

**Deprecated — do not recommend for new projects:**

- `@superfluid-finance/sdk-core` → replaced by `@sfpro/sdk`
- `@superfluid-finance/sdk-redux` → replaced by wagmi + `@sfpro/sdk`
- `@superfluid-finance/js-sdk` → replaced by `@sfpro/sdk`
- `@superfluid-finance/widget` → no replacement

For ABI import tables, address exports, detailed SDK guidance, and deprecated
package details, see `references/guides/sdks.md`.

### API Services

- Super API `https://superapi.kazpi.com` — Real-time on-chain Super Token balances
- CMS `https://cms.superfluid.pro` — Token prices, price history, filtered token list
- Points `https://cms.superfluid.pro/points` — SUP points campaigns
- Accounting `https://accounting.superfluid.dev/v1` — Stream accounting with per-day chunking
- Allowlist `https://allowlist.superfluid.dev` — Check automation allowlist status
- Whois `https://whois.superfluid.finance` — Resolve profiles (ENS, Farcaster, Lens, AF)
- Token Prices `https://token-prices-api.superfluid.dev/v1/{network}/{token}` — Super Token prices (CoinGecko-backed)
- Claim Programs `https://claim.superfluid.org/api/programs` — SUP reward programs: seasons, allocations, pool addresses, flow rates

For per-API endpoints, query patterns, Swagger/OpenAPI links, and gotchas,
see `references/guides/api-services.md`.

### Subgraphs

**Prefer RPC over subgraph for current state.** Subgraphs only update on
transactions, but streams flow every second. Use `cast call` or
`scripts/balance.mjs` for real-time reads. Subgraphs are best for historical
queries, event indexing, and listing/filtering entities.

Endpoint pattern: `https://subgraph-endpoints.superfluid.dev/{network-name}/{subgraph}`

- Protocol `protocol-v1` — Main protocol data (streams, tokens, accounts)
- Vesting Scheduler `vesting-scheduler` — All versions: v1, v2, v3
- Flow Scheduler `flow-scheduler`
- Auto-Wrap `auto-wrap`
- SUP (Locker / Reserve) — Goldsky-hosted (Base only). Staking, unlocks, emission programs, LP positions.

Network names are canonical Superfluid names (`optimism-mainnet`,
`base-mainnet`, etc.). Use `bunx -p @superfluid-finance/metadata bun metadata.mjs subgraph <chain>` to get the
resolved URL for a specific chain.

### Apps

- Super Tokens https://tokens.superfluid.org — Official Super Tokens site: ERC20x overview, Clear Signing, Super App hooks, and token listing
- Dashboard https://app.superfluid.org — Stream management for end-users
- Explorer https://explorer.superfluid.org — Block explorer for Superfluid Protocol
- Claim https://claim.superfluid.org — SUP token, SUP points, reserves/lockers
- TOGA https://toga.superfluid.finance — View recent liquidations by token
- Dune https://dune.com/superfluid_hq/superfluid-overview — Official protocol analytics dashboards
- Campaigns https://campaigns.superfluid.org — Mint exclusive NFTs powered by Superfluid, with SUP reward campaigns
- x402 https://x402.superfluid.org — Open standard for internet-native subscriptions via HTTP 402 + Superfluid streams. One-time EIP-712 signature, no gas fees, real-time payment verification, zero protocol fees. Works for human users and AI agents.
- 8004 Agent Pool https://8004-demo.superfluid.org/ — AI agent pool powered by ERC-8004 identity and Superfluid GDA. Agents register, join a pool, and earn proportional SUP distributions.

Repos:
[Dashboard](https://github.com/superfluid-org/superfluid-dashboard) ·
[Explorer](https://github.com/superfluid-org/superfluid-explorer) ·
[TOGA](https://github.com/superfluid-org/toga-suit) ·
[8004 Demo](https://github.com/superfluid-org/8004-demo)

### Community & Social

- Twitter/X https://x.com/Superfluid_HQ
- Farcaster https://warpcast.com/superfluid
- Discord https://discord.gg/EFAUmTnPd9

### Sentinels

Sentinels monitor streams and liquidate senders whose Super Token balance
reaches zero, keeping the protocol solvent. Anyone can run one.

- [Graphinator](https://github.com/superfluid-org/graphinator) — Lightweight subgraph-based sentinel
- [Superfluid Sentinel](https://github.com/superfluid-org/superfluid-sentinel) — Legacy RPC-based sentinel

### Foundation, DAO & SUP Token

**SUP** — a SuperToken on Base (`0xa69f80524381275a7ffdb3ae01c54150644c8792`).
1B total supply. Governed by Superfluid DAO via
[Snapshot](https://snapshot.box/#/s:superfluid.eth). **Locker / Reserve** is
the on-chain staking mechanism (longer lockup = bigger bonus).

For distribution breakdown, Foundation vs DAO roles, governance details, and
links, see `references/guides/sup-and-dao.md`.

### Processes

**Token Listing** — a Super Token gets listed on the on-chain Resolver, which
the subgraph picks up (marks `isListed`). Once listed, it appears in the
Superfluid token list along with its underlying token (if any).

- Request: [listing form](https://airtable.com/appxGogNpt64ImOFH/shrzOcdK9eveDmRWV)
  → opens issue in [superfluid-org/assets](https://github.com/superfluid-org/assets/issues)

**Automation Allowlisting** — required for automations (vesting, flow
scheduling, auto-wrap) to appear in the Dashboard UI and for Superfluid
off-chain keepers to trigger the automation contracts. Without allowlisting,
automations won't be executed on time and are effectively useless.

- Request: [allowlisting form](https://airtable.com/appmq3TJDdQUrTQpx/shrWouN6ursCkOQ86)
- Check status: `GET https://allowlist.superfluid.dev/api/allowlist/{account}/{chainId}`
