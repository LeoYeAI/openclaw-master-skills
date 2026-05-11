# xaut-trade

Our skills are developed by Duncan.Aure (Duncan), an AI Agent created by Aurelion, the world's first NASDAQ-listed Tether Gold (XAU₮) treasury company. Duncan executes on-chain financial actions through modular AI Agent Skills. Enables automated XAU₮ trading, cross-protocol DeFi execution, and programmable digital gold allocation.

Buy and sell XAUT (Tether Gold) on Ethereum mainnet via AI Agent, using Uniswap V3 + Node.js (ethers.js) under the hood.

## Quick Start

**Prerequisites:** Node.js ≥ 18 · ETH ≥ 0.005 (gas) · USDT or XAUT to trade

**1. Install**

```bash
npx skills add aurehub/skills
```

**2. Start trading** — if setup is needed, the Agent will guide you through it automatically:

```
buy XAUT with 100 USDT
```

---

## Supported Pairs

| Direction | Pair | Description |
|-----------|------|-------------|
| Buy | USDT → XAUT | Swap USDT for gold token |
| Sell | XAUT → USDT | Swap gold token back to USDT |

## Usage

xaut-trade handles XAUT/USDT trades natively and delegates other intents to specialized skills:

| Intent | Handled by | Example |
|--------|-----------|---------|
| Buy / sell XAUT | xaut-trade (built-in) | `buy XAUT with 100 USDT` |
| Limit order XAUT | xaut-trade (built-in) | `buy 0.01 XAUT when price drops to 3000` |
| Prediction markets | polymarket-trade | `bet on Bitcoin above 100k` |
| Perp / spot futures | hyperliquid-trade | `open long ETH on Hyperliquid` |

Just talk to the Agent in natural language:

### Buy

```
buy XAUT with 100 USDT
buy 200 USDT worth of XAUT
```

### Sell

```
sell 0.01 XAUT
swap 0.05 XAUT for USDT
sell 0.1 XAUT
```

### Limit Buy

```
buy 0.01 XAUT when price drops to 3000 USDT
limit order: buy 0.01 XAUT when price reaches 3000 USDT
limit buy XAUT at 3000, amount 0.01, valid 3 days
```

### Limit Sell

```
sell 0.01 XAUT when price rises to 4000 USDT
limit sell 0.01 XAUT at target price 3800 USDT, valid 3 days
sell 0.01 XAUT when price reaches 4000
```

### Check Limit Order

```
check my limit order status, orderHash is 0x...
```

### Cancel Limit Order

```
cancel limit order, orderHash is 0x...
```

### Check Balance

```
check my XAUT balance
```

## Trade Flow

For both buy and sell, the Agent follows this semi-automated flow:

```
Pre-flight checks → On-chain quote → Preview display → [Threshold-based confirmation] → Approve (mode-based confirmation) → Swap → Result verification
```

Before on-chain writes, the Agent always displays full commands. Confirmation level is policy-driven:
- Trade confirmation uses USD thresholds (`confirm_trade_usd`, `large_trade_usd`):
  - `< confirm_trade_usd`: preview shown, no blocking confirmation required
  - `>= confirm_trade_usd` and `< large_trade_usd`: single confirmation required
  - `>= large_trade_usd` or estimated slippage exceeds `max_slippage_bps_warn`: double confirmation required
- Approval confirmation uses `approve_confirmation_mode` with oversize safety override

## Risk Controls

| Rule | Default Threshold | Behavior |
|------|-------------------|----------|
| Trade confirm threshold | `confirm_trade_usd = $10` | Above threshold requires confirmation |
| Large trade | >= $1,000 USD | Double confirmation required |
| High slippage | > 50 bps (0.5%) | Warning + double confirmation |
| Oversized approval | `approve > 10x amount_in` | Force approval confirmation |
| Insufficient gas | ETH < 0.005 | Hard-stop |
| Insufficient balance | — | Hard-stop, report shortfall |
| Precision exceeded | > 6 decimal places | Hard-stop (XAUT minimum unit: 0.000001) |
| UniswapX Filler unavailable | XAUT is a low-liquidity token | Order expires after deadline; funds safe |

Thresholds can be customized in the `risk` section of `config.yaml`.

## Configuration

### .env (required)

| Variable | Description | Example |
|----------|-------------|---------|
| `WALLET_MODE` | Wallet backend: `wdk` (recommended) or `foundry` | `wdk` |
| `ETH_RPC_URL` | Ethereum RPC URL | `https://eth.llamarpc.com` |
| `ETH_RPC_URL_FALLBACK` | Comma-separated fallback RPCs tried in order on network error (429/502/timeout) | `https://eth.merkle.io,...` |
| `WDK_PASSWORD_FILE` | Path to WDK vault password file (**WDK mode**) | `~/.aurehub/.wdk_password` |
| `WDK_VAULT_FILE` | Override default vault path (**WDK mode**, optional) | `~/.aurehub/.wdk_vault` |
| `FOUNDRY_ACCOUNT` | Foundry keystore account name (**Foundry mode**) | `aurehub-wallet` |
| `KEYSTORE_PASSWORD_FILE` | Path to keystore password file (**Foundry mode**) | `~/.aurehub/.wallet.password` |
| `UNISWAPX_API_KEY` | UniswapX API Key (**limit orders only**, not needed for market orders) | Get at: developers.uniswap.org/dashboard |
| `RANKINGS_OPT_IN` | Join activity rankings — opt-in only (default: `false`) | `true` or `false` |
| `NICKNAME` | Display name for activity rankings (required if `RANKINGS_OPT_IN=true`) | `Alice` |

### config.yaml (optional)

Key adjustable parameters:

```yaml
risk:
  default_slippage_bps: 50      # Default slippage protection 0.5%
  max_slippage_bps_warn: 50     # Slippage warning threshold
  confirm_trade_usd: 10         # Single-confirm threshold (USD)
  large_trade_usd: 1000         # Large trade threshold (USD)
  approve_confirmation_mode: "first_only" # always | first_only | never (never is high-risk)
  approve_force_confirm_multiple: 10       # Force confirm if approve > 10x amount_in
  min_eth_for_gas: "0.005"      # Minimum ETH for gas
  deadline_seconds: 300         # Swap transaction timeout (seconds)

token_rules:
  USDT:
    requires_reset_approve: true  # USDT needs approve(0) before approve(amount)

limit_order:
  default_expiry_seconds: 86400   # Default order expiry: 1 day
  min_expiry_seconds: 300         # Minimum: 5 minutes
  max_expiry_seconds: 2592000     # Maximum: 30 days
  uniswapx_api: "https://api.uniswap.org/v2"  # Override for local mock testing
```

## Local Testing (Anvil Fork)

> **Note: Limit orders cannot be tested with Anvil fork** because the UniswapX API does not recognize local chain IDs.
> For limit orders, use a very small amount (e.g. 1 USDT → XAUT) on mainnet for end-to-end verification.
> Signature format can be validated against a local mock service via `limit_order.uniswapx_api` in `config.yaml`.

Use Anvil to fork mainnet state locally for zero-cost testing of the full buy/sell flow without spending real assets.

### 1. Start Anvil Fork

```bash
# Fork Ethereum mainnet locally (requires a mainnet RPC)
anvil --fork-url https://eth.llamarpc.com

# Optionally pin a block (for reproducible state)
anvil --fork-url https://eth.llamarpc.com --fork-block-number 19500000
```

Anvil starts with 10 pre-funded accounts, each with 10,000 ETH. Default: `http://127.0.0.1:8545`.

### 2. Point .env to Local

```bash
# .env
WALLET_MODE=foundry
ETH_RPC_URL=http://127.0.0.1:8545
FOUNDRY_ACCOUNT=aurehub-wallet
KEYSTORE_PASSWORD_FILE=~/.aurehub/.wallet.password
```
If you want to use Anvil account #0, import it once into keystore:

```bash
cast wallet import aurehub-wallet --interactive
```

### 3. Fund the Test Account with USDT

Anvil pre-funded accounts only have ETH. Use `cast` to impersonate a whale and transfer tokens:

```bash
# Find a USDT whale (e.g. Binance Hot Wallet)
USDT=0xdAC17F958D2ee523a2206206994597C13D831ec7
WHALE=0xF977814e90dA44bFA03b6295A0616a897441aceC  # Binance hot wallet

# Impersonate whale, transfer 10,000 USDT to test account
cast send $USDT "transfer(address,uint256)" \
  0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 10000000000 \
  --from $WHALE \
  --unlocked \
  --rpc-url http://127.0.0.1:8545

# Verify balance
cast call $USDT "balanceOf(address)" \
  0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266 \
  --rpc-url http://127.0.0.1:8545
```

### 4. Run Test Trades

Once configured, just use the skill normally:

```
buy XAUT with 100 USDT
```

The Agent will run the full flow (quote → confirm → approve → swap), all on the local fork — no real funds spent.

### 5. Notes

- Anvil fork state is **temporary** and resets on restart (unless using `anvil --state` for persistence)
- Local testing may use `--unlocked` + `--from` for manual token funding, while skill runtime signing remains keystore-only (`--account` + `--password-file`)
- If the fork runs for a long time, on-chain state may diverge from current mainnet; restart the fork to refresh
- Whale addresses may change over time; if the transfer fails, check the latest top holders on [Etherscan](https://etherscan.io/token/0xdAC17F958D2ee523a2206206994597C13D831ec7#balances)

## Security & Privacy

> For the complete environment and security declaration (required config files, environment variables, filesystem access, security safeguards), see the **Environment & Security Declaration** section in [SKILL.md](SKILL.md).

This skill communicates with external services during setup and trading:

| Service | When | Data Sent |
|---------|------|-----------|
| foundry.paradigm.xyz | First setup | Downloads and executes Foundry installer (`curl \| bash`) |
| npmjs.com | Limit order setup | Downloads Node.js dependencies |
| Ethereum RPC (configurable) | Every trade | On-chain calls (wallet address, transaction data) |
| UniswapX API (api.uniswap.org) | Limit orders | Order data, wallet address |
| xaue.com Rankings API | Opt-in only | Wallet address, nickname |

- **Foundry installation** uses `curl | bash`. Review the source at [github.com/foundry-rs/foundry](https://github.com/foundry-rs/foundry) before proceeding. The setup script asks for confirmation before running.
- **Rankings registration** remains opt-in (`RANKINGS_OPT_IN=false` by default). If not enabled during setup, the Agent can prompt once after your first successful trade.
- **All API calls use HTTPS.**

## FAQ

**Q: What if a transaction gets stuck or fails?**
The Agent will provide retry suggestions: reduce amount, increase slippage tolerance, or check nonce and gas.

**Q: Why does USDT approval require two steps?**
USDT's non-standard implementation requires `approve(0)` to reset the allowance before `approve(amount)`. XAUT does not.

**Q: Are other chains supported?**
Only Ethereum mainnet (chain_id: 1) is currently supported. Anvil fork is for local testing only, not a production deployment target.

**Q: I see `Device not configured (os error 6)` in Foundry mode — what do I do?**

This happens on macOS when Foundry's keystore cannot access the system Keychain in a non-interactive environment. Fix:

1. Create a password file and set permissions:
   ```bash
   echo "your_keystore_password" > ~/.aurehub/.wallet.password
   chmod 600 ~/.aurehub/.wallet.password
   ```
2. Set `KEYSTORE_PASSWORD_FILE` to point to this file in `.env`.
3. Re-run the trade flow.

**Q: What is a Skill package? How does it drive the AI to trade gold?**

A Skill package is a set of structured AI instruction files (`SKILL.md`) that define the Agent's behavior, operation flow, and risk boundaries for a specific scenario. The `xaut-trade` Skill tells the Agent how to check prerequisites, call the Uniswap V3 quote contract, execute trades via Node.js scripts, handle USDT's non-standard approval, and more. The Agent itself does not store private keys or have execution authority — it reads the Skill and generates commands. Depending on the configured risk thresholds, the Agent requests the required confirmation(s) before signing and broadcasting.

**Q: Do I need a computer running 24/7?**

- **Market orders (buy/sell)**: No. Market trades are one-shot interactions — you send the instruction → Agent quotes → you confirm → trade completes. No need to stay online.
- **Limit orders**: No. After signing, the order is submitted to the UniswapX network, where third-party Filler nodes automatically fill it when the price is met. Your computer can be off. Note: if no Filler fills the order before the `deadline`, it expires naturally with no loss of funds.

**Q: Does it only work with Claude Code?**

No. The Skill supports two main runners:

- **Claude Code** (recommended): install locally and use directly via Claude chat — no server needed
- **OpenClaw**: use via Slack / Telegram etc.; each user must configure their own wallet credentials independently

The primary test target is Claude (Sonnet / Opus series); other LLMs that can follow Skill instructions and call shell commands should work in theory but are not verified.

**Q: Will you read my API Key or private key from `.env`?**

No. The Skill package runs entirely locally. The only optional external data sharing is the activity rankings feature (opt-in during setup or first-success prompt, sends wallet address and nickname to xaue.com). All trades are executed via local Node.js scripts — no intermediary servers. Private keys are encrypted locally (WDK vault or Foundry keystore); `.env` only stores the account name and other config (wallet address is derived at runtime). Never commit `.env` to version control.

**Q: Will the Agent auto-buy based on price movements?**

No. The Agent does not monitor prices or make autonomous decisions. It is an execution assistant that acts only when you explicitly give an instruction:

- **Market order**: you say "buy XAUT with 100 USDT" → Agent quotes → you confirm → executes
- **Limit order**: you set "buy 0.01 when XAUT drops to 3000" → Agent signs and submits the order → UniswapX Fillers fill it when the condition is met

**Q: Do I need to manually confirm each trade? Can it spend my money without confirmation?**

By default, confirmation is threshold-based: small trades show full preview and can execute without blocking confirmation, medium trades require one confirmation, and large/high-risk trades require double confirmation. Approval confirmations are controlled by `approve_confirmation_mode`, with a mandatory override for oversized approvals. `approve_confirmation_mode=never` is high-risk and intended for advanced users only. The Agent cannot sign without your local keystore/password setup.

**Q: Can I use multiple wallets simultaneously?**

The current Skill is designed for a single wallet per instance. For multi-wallet use, prepare a separate `.env` for each wallet (with distinct `FOUNDRY_ACCOUNT` and `KEYSTORE_PASSWORD_FILE`), and switch config files before each operation. There is no built-in multi-wallet concurrent management.

**Q: Do I need to reinstall after a Skill update?**

Yes. Re-fetch the latest version through the same channel you used to install. Updates will not overwrite your local config (`.env`, `config.yaml`).

## Skill Delegation

When a non-XAUT intent is detected, xaut-trade automatically delegates to the appropriate skill.
If the required skill is not installed, the Agent will output the install command.

| Skill | Triggers | Install |
|-------|---------|---------|
| `polymarket-trade` | polymarket, prediction market, bet on, odds on, will X happen, chances of | `npx skills add aurehub/skills` |
| `hyperliquid-trade` | hyperliquid, perp, perpetual, futures, long, short, open long, open short, close position, leverage | `npx skills add aurehub/skills` |

## Stay Connected

For our updates, new skills, and ecosystem developments. Check out:

- **X**: [Aure_duncan](https://x.com/Aure_duncan)
- **Telegram**: [@aure_duncanbot](https://t.me/aure_duncanbot)
- **Aurelion**: [aurelion.com](https://www.aurelion.com/)
