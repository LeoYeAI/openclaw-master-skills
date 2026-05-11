# Changelog

## v0.24.8

### Fix — Remove child_process from wallet-raw-call.mjs

- `execFileSync("which")` 替换为纯 Node.js PATH 遍历（`existsSync` + `realpathSync`），彻底移除 `child_process` 依赖，消除安全扫描警告

## v0.24.7

### Fix — Welcome title update

- 欢迎语标题统一为 "Hello World from the World of Agents!"（SKILL.md + daemon 推送）

## v0.24.6

### Fix — Onboarding auto-select + redundant setRecipient after bind

- **注册时必须让用户选择**: Onboarding Step 2 不再标注 "(recommended)"，明确要求 agent 展示 Option A/B 并等待用户选择，不得自动选择
- **bind 后不再冗余调用 setRecipient**: 明确说明 `bind(target)` 后 `resolveRecipient()` 沿绑定链解析收益地址，已自动指向 target——无需再调用 `setRecipient()`。在 S1 节、Onboarding Step 2、Rules 三处均添加此规则

## v0.24.5

### Fix — Code review (29 issues), notification redesign, description optimization

**Notification system redesign**:
- **Step 3 通知配置重写**: 彻底移除不存在的 `OPENCLAW_CHANNEL`/`OPENCLAW_TARGET` 环境变量依赖。采用 benchmark-worker 模式——agent 在 skill 加载时写入 `~/.awp/openclaw.json`（含 channel + target），daemon 每周期热加载此文件，通过 `openclaw message send` 推送
- daemon 移除 `--channel`/`--target` CLI 参数，简化为仅 `--interval`
- `_get_openclaw_config()` 简化为每次读文件（支持 agent 随时更新配置）
- SKILL.md `optional_env` 中移除 `OPENCLAW_CHANNEL`/`OPENCLAW_TARGET`
- 步骤重编号 1-8（Welcome → Install wallet → Configure notifications → …）
- `sessionToken` → `token` 统一全文

**Description optimization**:
- 重写 skill description 提升触发准确率
- eval 结果: 20/20（10/10 应触发 + 10/10 不应触发）

**SKILL.md (其余修复)**:
- `$TOKEN` never assigned in onboarding — added capture from `awp-wallet unlock` output
- Daemon pgrep command — `pgrep -f "python3.*awp-daemon"` 避免 self-match
- `~/.awp` dir not guaranteed before daemon start — added `mkdir -p`
- `grep -oP` not portable — replaced with `sed -n`
- Step 5 missing wallet_addr parse — added JSON eoaAddress extraction instruction

**awp-daemon.py (8 fixes)**:
- `owner` None crash — safe handling for missing/short owner strings
- `check_updates()` runs every cycle — now every 12 cycles (~1 hour)
- Address truncation crash for short addresses — length check before slicing
- No negative caching for openclaw config — added `_openclaw_config_checked` flag
- Non-atomic notification file write — use tmp + rename pattern
- `subnet_id` not cast to int — explicit `int()` for set membership checks
- Fragile phase logic — handle `registered is None` case explicitly

**awp_lib.py (6 fixes)**:
- Bare `except Exception` in `to_wei` → specific `(ValueError, TypeError, ArithmeticError)`
- `days_to_seconds` missing try/except — added error handling
- `pad_address` no hex validation — added regex check for hex characters
- `encode_calldata` no selector validation — added `0x + 8 hex` format check
- `get_wallet_address` no address validation — added `ADDR_RE` check on returned value

**Script fixes (6 fixes)**:
- `onchain-vote.py`: `token_id` not cast to int in eligible_ids
- `relay-register-subnet.py`: `--subnet-manager` and `--salt` not validated
- `wallet-raw-call.mjs`: hex regex allows odd-length strings — require even-length
- `onchain-register-and-stake.py`: no check that allocate_amount ≤ deposit amount
- `onchain-deposit.py`: no uint64 overflow guard on lock_seconds
- `onchain-add-position.py`: no uint64 overflow guard on new_lock_end

**Reference docs (4 fixes)**:
- `commands-subnet.md`: PERMIT_NONCE from wrong endpoint — now reads from AWPToken contract via RPC
- `commands-subnet.md`: event field `tokenId` → `subnetId` for setSkillsURI/setMinStake
- `commands-staking.md`: `$CHAIN_ID` variable never assigned → literal `8453`
- `protocol.md`: SubnetFullInfo struct missing `symbol` field

## v0.24.4

### Fix — Daemon startup false positive + OpenClaw CLI discovery
- **pgrep 误判**: `pgrep -f "awp-daemon.py"` 会匹配自身（启动命令的 subshell），导致 daemon 永远不会被启动。改为 `pgrep -xf "python3 .*awp-daemon\\.py.*"` 精确匹配 python3 进程
- **OpenClaw CLI 查找**: daemon 之前只用 `shutil.which()` 搜索 PATH，遗漏了 `~/.npm-global/bin/openclaw` 等常见 npm 全局安装路径。新增 `_find_openclaw()` 函数，自动补充 `~/.npm-global/bin`、`~/.local/bin`、`~/.yarn/bin` 等目录
- **描述优化验证**: 通过外部项目测试确认 skill description 触发率正常（5/5 AWP 查询正确触发，1/1 非 AWP 查询正确不触发）

## v0.24.3

### Improve — Notification infrastructure
- **Daemon log file**: output redirected to `~/.awp/daemon.log` instead of `/dev/null` — all daemon activity now persisted
- **Status file**: daemon writes `~/.awp/status.json` each cycle with current phase, wallet state, registration, subnet count, and next-step guidance — agent can read this anytime
- **New user commands**: `awp notifications` (read + display + clear daemon notifications), `awp log` (tail daemon log)
- **Intent routing**: added NOTIFICATIONS and LOG routes
- **Help menu**: updated with new commands

## v0.24.2

### Improve — Daemon guided notifications with actionable next steps
- **Wallet not ready**: notification tells user to say "install awp-wallet from ..." to the agent
- **Wallet not initialized**: notification tells user to say "initialize my wallet" to the agent
- **Wallet just became ready** (detected in monitor loop): pushes "Wallet Ready" with next step — tell agent "start working on AWP"
- **Registration detected**: pushes "Registered — Ready to Work" with next steps — list subnets, install skill, or start working
- **Deregistered**: notification includes re-registration guidance
- All notifications include short wallet address for context

## v0.24.1

### Feature — Daemon: welcome push + new subnet notifications
- **Welcome message**: daemon sends banner + active subnet list via `notify()` (OpenClaw push + file); falls back to stdout only when push is unavailable
- **New subnet detection**: each monitoring cycle compares current subnets against known set; new subnets trigger a notification with name, symbol, owner, min stake, skills status
- Monitoring loop now continues checking subnets and updates even when wallet is not yet available

## v0.24.0

### Feature — Auto-start daemon on skill load
- **SKILL.md**: Add Step 7 — launch `awp-daemon.py` as background process on skill load (with `pgrep` guard to prevent duplicates)
- **awp-daemon.py**: No longer exits on missing dependencies — notifies user and retries each cycle
  - Missing awp-wallet → sends notification, keeps running, re-checks each interval
  - Missing wallet init → sends notification, keeps running, re-checks each interval
  - When dependency becomes available mid-run, daemon auto-detects and starts monitoring
- Fix ASCII face in daemon banner (same fix as SKILL.md)

## v0.23.2

### Fix — Install review findings
- Add `node` to required binaries (wallet-raw-call.mjs requires Node.js)
- Move `EVM_RPC_URL`, `OPENCLAW_CHANNEL`, `OPENCLAW_TARGET` from `env` to `optional_env` (they have defaults or are runtime-provided)
- Clarify wallet init is agent-initiated (not unattended auto-init) in Step 5, Onboarding, and error table
- Fix version string in Step 6 version check

## v0.23.1

### Improve — Skill description for better triggering
- Expanded description with explicit action list (deposit, withdraw, allocate, register, vote, etc.)
- Added "hallucination warning" — tells model it CANNOT handle AWP without this skill
- Added trigger phrases: "start working", "awp onboard", "awp status"
- Added negative scope: Compound, generic ERC-20, Hardhat

## v0.23.0

### Code Review — 16 fixes

**SKILL.md:**
- Fix shell injection in OpenClaw config write (use python3 json.dumps instead of shell interpolation)
- Add curl command for version check (Step 6 was unimplementable)
- Remove duplicate Step 4 onboarding label with inconsistent capitalization
- Change `[QUERY]` → `[SETUP]` tag for skill install operations
- Add `https://` to W1 WebSocket event basescan links

**Python scripts:**
- `awp_lib.py`: `float()` → `Decimal()` in `validate_positive_number` (precision on large amounts)
- `awp_lib.py`: `to_wei()` now catches `InvalidOperation` from `Decimal()`
- `onchain-add-position.py`: remove dead guard (`max()` makes `< current` impossible)
- `onchain-vote.py`: `int(p["created_at"])` now wrapped in try/except
- `awp-daemon.py`: enforce `--interval >= 10` (prevent CPU spin loop)

**wallet-raw-call.mjs:**
- `--data` regex now requires ≥8 hex chars (function selector), rejects empty `0x`
- `strict: true` in parseArgs (unknown flags now error instead of silent ignore)
- Null-check `signer` after `loadSigner()`

**Reference docs:**
- `commands-staking.md`: `--calldata` → `--data` (matching actual script flag)
- `commands-subnet.md`: remove duplicate on-chain/gasless command template
- `commands-subnet.md`: replace `cast` (Foundry) with API+python3 for nonce queries

**README.md:**
- Add `wallet-raw-call.mjs` to architecture tree
- Update version history through 0.22.9
- Fix wallet install timing description (skill load, not write operations)

## v0.22.9

### Simplify — Wallet install description
- SKILL.md Step 2: streamlined to single install path — repo URL + follow SKILL.md

## v0.22.8

### Fix — Wallet install: skill-first, fallback to repo
- SKILL.md Step 2: prefer using AWP Wallet skill (available on OpenClaw or if pre-installed), fallback to git clone + follow SKILL.md for standalone environments

## v0.22.7

### Fix — Explicit wallet install steps
- SKILL.md Step 2: give agent concrete 3-step instructions (clone → bash install.sh → verify), not vague "it contains its own install instructions" which agent won't follow

## v0.22.6

### Simplify — Just tell agent where the wallet skill is
- SKILL.md Step 2: point agent to `https://github.com/awp-core/awp-wallet`, let it handle installation — no hardcoded install commands

## v0.22.5

### Fix — Install from local repo, not remote pipe
- SKILL.md Step 2: `git clone` → `bash install.sh`（先拉到本地再执行，不用 `curl | bash` 远程管道）
- daemon: all install/update messages use `git clone` + local `install.sh` instead of `curl | bash`
- Removed `WALLET_INSTALL_SCRIPT` (raw.githubusercontent.com URL) from daemon

## v0.22.4

### Fix — Inline wallet install instructions
- SKILL.md Step 2: provide `git clone → npm install → npm link` steps directly, instead of depending on a wallet skill that may not be loaded in the current session
- Wallet init (`awp-wallet init`) runs directly — no external skill dependency needed
- Avoids the "start a new session to load the wallet skill" problem

## v0.22.3

### Fix — Wallet install via skill, not bash script
- SKILL.md Step 2: removed hardcoded `curl | bash` install command. Now directs agent to install the AWP Wallet skill (from ClawHub or repo), which handles installation and setup
- Onboarding Step 1 & Session recovery Step 5: delegate wallet init to the AWP Wallet skill
- AWP skill no longer contains any remote install scripts — wallet lifecycle is fully owned by the wallet skill

## v0.22.2

### UX Fix — Agent handles install & init
- SKILL.md Step 2: agent directly runs `curl | bash` to install awp-wallet (not the user)
- SKILL.md Step 5: agent runs `awp-wallet init` if wallet not found (not the user)
- Onboarding Step 1: agent runs `awp-wallet init` directly
- Note: daemon script (`awp-daemon.py`) remains check-only — it does not auto-install or auto-init

## v0.22.1

### Security Hardening
- **Removed auto-install**: daemon no longer downloads or executes remote install scripts (`curl | bash`). Prints manual install instructions instead
- **Removed auto-init**: daemon no longer runs `awp-wallet init` automatically. User must explicitly initialize wallet
- **Removed `/tmp` glob scanning**: `_get_openclaw_config()` no longer reads `/tmp/awp-worker-*-config.json` patterns (writable by any process). Only reads `~/.awp/openclaw.json`
- **Declared OpenClaw env vars**: added `OPENCLAW_CHANNEL` and `OPENCLAW_TARGET` to `requires.env` (optional)
- **Clarified update checks**: version checks are informational only, no auto-download or auto-execute
- **Reference docs**: added default value (`https://tapi.awp.sh/api`) and `AWP_API_URL` env var to all 4 API Base URL annotations

## v0.22.0

### Fixed — awp-wallet CLI Compatibility
- **CRITICAL**: `awp-wallet send --data` does NOT exist — `send` only supports token transfers (`--to`, `--amount`, `--asset`). Added `wallet-raw-call.mjs` bridge script that imports awp-wallet internal modules (keystore/session/viem) for raw contract calls
- **CRITICAL**: `awp_lib.py:wallet_send()` was silently failing — all on-chain Python scripts broken. Fixed to use bridge script
- `--chain base` is a global option, NOT per-subcommand — removed from `approve`, `balance` calls
- `awp-wallet unlock --scope` EXISTS (read|transfer|full) — re-added with `--scope transfer` default
- `awp-wallet status --token` EXISTS — added `wallet_status()` to awp_lib.py
- awp-wallet install: `skill install` → `curl -sSL install.sh | bash` (not on npm registry)
- awp-daemon: wallet version check was reading non-existent SKILL.md from awp-wallet repo → now reads package.json
- Reference docs: replaced all broken `awp-wallet send --data $(cast calldata ...)` templates with bundled Python script commands
- CHANGELOG v0.20.7 correction: `--scope full` DOES exist — it was incorrectly removed in that version

---

## v0.21.0

### Changed — Shell → Python Migration
- **All 14 shell scripts converted to Python** — eliminates `curl`/`jq`/`sed` dependencies, only `python3` required
- New shared library `scripts/awp_lib.py` (~285 lines) — API calls, wallet commands, ABI encoding, input validation, EIP-712 builder
- Shell injection surface fully eliminated — no more `python3 -c` inline, no `$VAR` interpolation in subshells
- All scripts now use native Python `urllib` for HTTP and `argparse` for CLI parsing
- Dependencies reduced from `curl + jq + python3` to `python3` only
- Reference docs updated: `scripts/*.sh` → `scripts/*.py`

---

## v0.20.7

### Fixed — Deep Code Review
- **CRITICAL**: `awp-wallet status` command does not exist → replaced with `awp-wallet receive` across 14 scripts + 3 reference files + SKILL.md
- **CRITICAL**: `.address` field does not exist → replaced with `.eoaAddress` across all 20 files
- **CRITICAL**: `--scope full` parameter does not exist → removed from `awp-wallet unlock` (3 places)
- `onchain-vote.sh`: `$ELIGIBLE_TOKEN_IDS` shell injection → now passed via `os.environ`
- `relay-start.sh`: `sed` injection risk → replaced with `jq` for safe JSON construction
- `onchain-deposit.sh`: `--lock-days 0` incorrectly passed validation → now rejected
- `AWP_TOKEN` null check missing in `onchain-deposit.sh` and `onchain-register-and-stake.sh` → added
- `awp-daemon.py`: wallet update falsely reported success on failure → now checks return code
- `awp-daemon.py`: deregistration event silently dropped → now logs and notifies
- `awp-daemon.py`: `except Exception` too broad → narrowed to `(JSONDecodeError, OSError)`
- `$RPC_URL` → `$EVM_RPC_URL` in `commands-subnet.md` and `commands-governance.md`
- SKILL.md: stale example date `2025-12-01` → `2026-12-01`

### Changed
- **Multi-EVM**: `BASE_RPC_URL` → `EVM_RPC_URL` across all scripts and references
- Description updated: "on Base" → "on EVM" to reflect all EVM-compatible chains
- README badges: added Ethereum, EVM Compatible; updated descriptions for multi-chain
- README: removed stale "Proceed? (y/n)" UX description (agent wallet model executes directly)
- Reference docs: clarified that `cast` examples are for reference only; agents must use bundled scripts
- Version history in README aligned with 0.x.x scheme

---

## v0.19.9

### Security
- Q6 subnet skill install: auto-install from `awp-core/*`; third-party sources show `⚠ third-party source` notice (non-blocking)
- Metadata now declares all dependencies: `curl`, `jq`, `python3`
- Wallet auto-manages credentials in default mode — no password files needed

### Changed
- **Agent wallet model** — transactions execute directly, no confirmation prompts. This is a work wallet for AWP tasks only; users are told not to store personal assets.
- `awp-wallet` installs from registry first, falls back to GitHub: `skill install awp-wallet || skill install https://github.com/awp-core/awp-wallet`
- Description rewritten: 511 chars (was 916), natural language instead of keyword list
- Removed all V1 `.rootNet` fallback code — V2 API is now authoritative

### Fixed
- Deep audit: `$REASON`, `$SKILLS_URI`, `$POSITIONS` injection — now passed via `os.environ`
- All 9 onchain scripts: added registry/contract null checks
- `AMOUNT=0` and `POSITION=0` rejected in validation
- `onchain-withdraw.sh`: hardcoded `remainingTime` selector (removed `web3` dependency)
- `relay-start.sh`: removed fallback to deleted `/relay/register` endpoint
- `onchain-vote.sh`: `RPC_URL` → `BASE_RPC_URL` (consistent with other scripts)
- Pre-Flight unlock now includes password pipe

---

## v0.19.1 — Initial Public Release

First public release of the AWP Skill for [Claude Code](https://github.com/anthropics/claude-code), [OpenClaw](https://openclaw.ai), and other SKILL.md-compatible agents.

### What is AWP Skill?

A natural-language interface to the **AWP (Agent Working Protocol)** on EVM-compatible chains. Install it in any compatible agent, and the agent can register on AWP, join subnets, stake tokens, vote on governance proposals, and monitor real-time on-chain events — all through conversation.

```bash
skill install https://github.com/awp-core/awp-skill
```

### Highlights

- **20 actions** across 5 categories: Query, Staking, Subnet Management, Governance, and WebSocket Monitoring
- **14 bundled shell scripts** that handle all on-chain operations — the agent never constructs calldata manually, eliminating an entire class of ABI-encoding and selector errors
- **Gasless onboarding** — registration is free via EIP-712 relay; no ETH or AWP tokens needed to get started
- **26 real-time event types** via WebSocket with 4 presets (staking, subnets, emission, users)
- **Guided onboarding flow** — 4-step wizard (wallet → register → discover subnets → install skill) with progress indicators
- **Optimized for weaker models** — concrete URLs (no placeholders), one way to do each operation (no choices), and explicit rules preventing common mistakes

### Architecture

```
awp-skill/
├── SKILL.md                    Main skill file (589 lines)
├── references/                 5 reference docs loaded on demand
│   ├── api-reference.md          REST + contract quick reference
│   ├── commands-staking.md       S1-S3 templates + EIP-712
│   ├── commands-subnet.md        M1-M4 templates + gasless
│   ├── commands-governance.md    G1-G4 + supplementary endpoints
│   └── protocol.md              Structs, 26 events, constants
├── scripts/                    14 executable bash scripts
│   ├── awp_lib.py                Shared library (API, wallet, ABI, validation)
│   ├── relay-start.py            Gasless register/bind
│   ├── relay-register-subnet.py  Gasless subnet registration
│   ├── onchain-register.py       On-chain register
│   ├── onchain-bind.py           On-chain bind
│   ├── onchain-deposit.py        Deposit AWP
│   ├── onchain-allocate.py       Allocate stake
│   ├── onchain-deallocate.py     Deallocate stake
│   ├── onchain-reallocate.py     Reallocate stake
│   ├── onchain-withdraw.py       Withdraw expired position
│   ├── onchain-add-position.py   Add to existing position
│   ├── onchain-register-and-stake.py  One-click register+deposit+allocate
│   ├── onchain-vote.py           Cast DAO vote
│   ├── onchain-subnet-lifecycle.py  Activate/pause/resume subnet
│   └── onchain-subnet-update.py  Set skillsURI or minStake
├── assets/
│   └── banner.png
├── README.md
└── LICENSE
```

### Actions

| Category | Actions | Wallet Required |
|----------|---------|:---------------:|
| **Query** | Q1 Subnet, Q2 Balance, Q3 Emission, Q4 Agent, Q5 List Subnets, Q6 Install Skill, Q7 Epoch History | No |
| **Staking** | S1 Register/Bind, S2 Deposit/Withdraw/AddPosition, S3 Allocate/Deallocate/Reallocate | Yes |
| **Subnet** | M1 Register Subnet, M2 Lifecycle, M3 Update Skills URI, M4 Set Min Stake | Yes |
| **Governance** | G1 Create Proposal, G2 Vote, G3 Query Proposals, G4 Query Treasury | Yes |
| **Monitor** | W1 Watch Events, W2 Emission Alert | No |

### UX Features

- ASCII art welcome screen with quick-start commands
- `awp status` / `awp wallet` / `awp subnets` / `awp help` quick commands
- Agent wallet model — transactions execute directly (work wallet, no personal assets)
- Balance change notifications with +/- delta after writes
- Tagged output: `[QUERY]`, `[STAKE]`, `[TX]`, `[NEXT]`, `[!]` prefixes
- Transaction links to basescan.org
- Auto-generate wallet password (never asks user)
- Session recovery on reconnect

### Anti-Hallucination Measures

Every write operation is wrapped in a bundled script that:
- Validates all inputs (address regex, numeric checks, subnet > 0)
- Targets the correct contract (AWPRegistry vs StakeNFT vs SubnetNFT vs DAO)
- Uses hardcoded, keccak256-verified function selectors
- Pre-checks state before submitting (balance, registration, lock expiry)
- Handles unit conversion (human-readable AWP ↔ wei, days ↔ seconds)

The agent never:
- Constructs ABI-encoded calldata manually
- Builds EIP-712 JSON by hand
- Hardcodes contract addresses
- Assumes the user has AWP tokens to start

### Gasless Operations

| Operation | Endpoint | Signatures |
|-----------|----------|:----------:|
| Register (setRecipient) | `POST /relay/set-recipient` | 1 |
| Bind (tree-based) | `POST /relay/bind` | 1 |
| Register Subnet | `POST /relay/register-subnet` | 2 |

Nonce from `GET /nonce/{address}`. EIP-712 domain from `GET /registry → eip712Domain`.

### Protocol Details

| Parameter | Value |
|-----------|-------|
| Chain | EVM-compatible (testnet: Base, Chain ID 8453) |
| Gas Token | ETH |
| Epoch Duration | 1 day |
| Initial Daily Emission | 15,800,000 AWP |
| Decay | ~0.3156% per epoch |
| Max Active Subnets | 10,000 |
| Voting Power | `amount × √(min(remainingTime, 54w) / 7d)` |
| Explorer | deployment-specific (default: basescan.org) |

### Security

- All user inputs validated before reaching `python3 -c` (regex in shell)
- `$REASON` and `$SKILLS_URI` passed via `os.environ`, not string interpolation
- `$POSITIONS` API response passed via environment variable
- Registry address null-checked in all 14 scripts
- AMOUNT=0 and POSITION=0 rejected

### Compatibility

Works with any agent that supports the [SKILL.md standard](https://agentskills.io/specification):
- Claude Code
- OpenClaw
- Cursor
- Codex
- Gemini CLI
- Windsurf

### Install

```bash
skill install https://github.com/awp-core/awp-skill
```

Then say **"start working"** to begin.
