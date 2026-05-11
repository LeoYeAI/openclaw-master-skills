# DeFi & Trading Cookbook

Step-by-step recipes for your trading and DeFi operations.

You have three **built-in trading engines** that handle signing, approval, and execution automatically. For other protocols, use the universal `exec` command with ABI encoding.

## Table of Contents

1. [DEX Swap (0x Aggregator)](#dex-swap)
2. [Hyperliquid Perpetual Futures & Spot](#hyperliquid)
3. [Bridge to Hyperliquid](#bridge-to-hyperliquid) — Deposit USDC from HyperEVM to HL L1 for trading
4. [EOA Transactions](#eoa-transactions) — Direct EOA operations via `--eoa` flag (any chain) or HyperEVM (automatic)
5. [Fund EOA for Polymarket](#fund-eoa-for-polymarket) — Get POL + USDC.e on Polygon for Polymarket trading
6. [Polymarket Prediction Markets](#polymarket)
7. [Custom Contract Interactions](#custom-contracts) — AAVE, Compound, and any other protocol via `exec`
8. [Common Patterns & Safety](#tips)

---

## DEX Swap

`tigerpass swap` uses the **0x aggregator** to find the best price across all DEXes — Uniswap V3, SushiSwap, Curve, Balancer, and dozens more. One command does everything: quote, approve, and execute.

**Important**: Native token (ETH) is not supported as the sell token by 0x. Use **WETH** instead. Buying native ETH is supported.

### Basic Swap

```bash
# Swap 100 USDC → WETH on Base (default chain)
tigerpass swap --from USDC --to WETH --amount 100

# Swap on a different chain
tigerpass swap --from USDC --to WETH --amount 100 --chain ETHEREUM

# Use contract address for unlisted tokens
tigerpass swap --from 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913 --to WETH --amount 100
```

### Controlling Slippage

```bash
# Tight slippage (0.5% = 50 bps)
tigerpass swap --from USDC --to WETH --amount 100 --slippage 50

# Default is 1% (100 bps) — suitable for most pairs
```

### MEV Protection

```bash
# Route through private mempool to avoid sandwich attacks
tigerpass swap --from USDC --to WETH --amount 1000 --private
```

For any swap above ~$100, use `--private` — it prevents front-running at no extra cost.

### Don't Wait for Confirmation

```bash
# Submit and return immediately (useful for batch workflows)
tigerpass swap --from USDC --to WETH --amount 100 --no-wait
```

### Verify Before and After

```bash
# 1. Check input balance
tigerpass balance --token USDC

# 2. Execute swap
tigerpass swap --from USDC --to WETH --amount 100 --private

# 3. Verify output received
tigerpass balance --token WETH
```

### Output Format

```json
{
  "status": "confirmed",
  "from": "USDC",
  "to": "WETH",
  "sellAmount": "100",
  "buyAmount": "0.0333...",
  "sellToken": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  "buyToken": "0x4200000000000000000000000000000000000006",
  "chain": "BASE",
  "feeBps": 15,
  "userOpHash": "0x...",
  "walletAddress": "0x...",
  "txHash": "0x...",
  "explorer": "https://basescan.org/tx/0x..."
}
```

**Key output fields**: `status` is `"confirmed"` or `"submitted"` (if `--no-wait`). `feeBps` is 15 (0.15% integrator fee). `error` field appears on failure.

### Swap Limitations

- **Sell token must be ERC-20** — use WETH instead of native ETH
- **0x does not support testnets** — `swap` is unavailable in test environment
- **Not available on HyperEVM** — 0x has no HyperEVM support
- **`--eoa` supported** — swap can execute from EOA on any 0x-supported chain (EOA must hold the sell token)

---

## Hyperliquid

`tigerpass hl` trades **perpetual futures** and **spot tokens** on Hyperliquid — the highest-volume perp DEX. All signing, encoding, and builder fee attachment are handled automatically. Add `--spot` to any command to switch from perps (default) to spot trading.

### Setup (Once)

```bash
# Authorize builder fee — required once before the first trade (covers both perps and spot)
tigerpass hl approve-builder
```

### Trading Workflow

```bash
# 1. Check available balance (L1, NOT HyperEVM!)
tigerpass hl info --type balances

# 2. Check current mid prices
tigerpass hl info --type mids

# 3. Place a limit buy order
tigerpass hl order --coin BTC --side buy --price 95000 --size 0.01

# 4. Check order status
tigerpass hl info --type orders

# 5. Check position
tigerpass hl info --type positions
```

### Spot Trading

Add `--spot` to switch to spot market. Spot trades buy/sell actual tokens (not derivatives).

```bash
# Buy 10 HYPE at $25
tigerpass hl order --spot --coin HYPE --side buy --price 25 --size 10

# Sell 5 HYPE at $30
tigerpass hl order --spot --coin HYPE --side sell --price 30 --size 5

# Check spot balances (total, hold/frozen in orders, entry value)
tigerpass hl info --spot --type balances

# Check open spot orders
tigerpass hl info --spot --type orders

# Cancel all spot orders
tigerpass hl cancel --spot --all

# Cancel spot order for specific coin
tigerpass hl cancel --spot --coin HYPE --oid 12345
```

### Order Types

```bash
# GTC — Good 'til Cancelled (default)
tigerpass hl order --coin BTC --side buy --price 95000 --size 0.01

# IOC — Immediate or Cancel (fill or kill)
tigerpass hl order --coin ETH --side buy --price 3200 --size 1.0 --type ioc

# ALO — Add Liquidity Only (maker only, no taker fills)
tigerpass hl order --coin BTC --side sell --price 100000 --size 0.01 --type alo

# Reduce-only (close position, never open new — perps only)
tigerpass hl order --coin BTC --side sell --price 100000 --size 0.01 --reduce-only
```

### Cancel Orders

```bash
# Cancel a specific order by OID
tigerpass hl cancel --coin BTC --oid 12345

# Cancel all orders for one coin
tigerpass hl cancel --all --coin BTC

# Cancel everything
tigerpass hl cancel --all

# Spot cancel examples
tigerpass hl cancel --spot --coin HYPE --oid 67890
tigerpass hl cancel --spot --all
```

### Account Queries

```bash
# --- Perpetual Futures ---
# Positions — coin, size, entry price, PnL, liquidation price, leverage
tigerpass hl info --type positions

# Open orders — coin, side, price, size, OID
tigerpass hl info --type orders

# Balance — account value, margin used, withdrawable
tigerpass hl info --type balances

# All mid prices — every listed asset
tigerpass hl info --type mids

# --- Spot ---
# Spot token balances (total, hold/frozen, entry value)
tigerpass hl info --spot --type balances

# Open spot orders
tigerpass hl info --spot --type orders
```

### Position Output Example

```json
{
  "positions": [
    {
      "coin": "BTC",
      "szi": "0.01",
      "entryPx": "95000.0",
      "unrealizedPnl": "50.00",
      "liquidationPx": "80000.0",
      "leverage": { "type": "cross", "value": 10 }
    }
  ]
}
```

### Builder Fees

Fees are automatically attached to every order:

| Market | Fee | Rate |
|--------|-----|------|
| Perpetual futures | `hyperliquidBuilderFee` | 5bp (0.05%) |
| Spot | `hyperliquidSpotBuilderFee` | 50bp (0.5%) |

Authorized once via `approve-builder` — covers both perps and spot.

---

## Bridge to Hyperliquid

To trade on Hyperliquid (perps or spot), you need USDC deposited into the **Hyperliquid L1 trading layer**. The L1 is separate from HyperEVM — think of it as: HyperEVM is the on-chain EVM, while L1 is the off-chain order book where trading happens.

The bridge flow deposits USDC from HyperEVM into the L1 trading account via the **CoreDepositWallet** contract.

### Architecture

```
HyperEVM (chain 999)          Hyperliquid L1 (trading)
┌──────────────────┐          ┌──────────────────────┐
│  EOA holds USDC  │──bridge──│  USDC trading balance │
│  + HYPE for gas  │          │  (perps + spot)       │
└──────────────────┘          └──────────────────────┘
      ↑ approve + deposit           ↓ trade
      │ via CoreDepositWallet       │ via tigerpass hl
```

### Contract Addresses

| Contract | Testnet (998) | Mainnet (999) |
|----------|--------------|---------------|
| CoreDepositWallet | `0x0b80659a4076e9e93c7dbe0f10675a16a3e5c206` | `0x6b9e773128f453f5c2c60935ee2de2cbc5390a24` |
| Native USDC | `0x2B3370eE501B4a559b57D449569354196457D8Ab` | `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |

### Deposit Function

```solidity
CoreDepositWallet.deposit(uint256 amount, uint32 destinationDex)
```

| Parameter | Value | Meaning |
|-----------|-------|---------|
| `amount` | USDC in 6 decimals (e.g., `10000000` = 10 USDC) | How much to deposit |
| `destinationDex` | `0` | Deposit to **perps** margin |
| `destinationDex` | `4294967295` (uint32 max) | Deposit to **spot** balance |

### How to Fund Your EOA on HyperEVM

You **cannot** autonomously bridge tokens from other chains to HyperEVM. The user must fund the EOA externally:

1. **Get the EOA address**: `tigerpass init` — give this address to the user
2. **User sends HYPE + USDC** to the EOA address on HyperEVM via:
   - Hyperliquid UI (spot withdraw to HyperEVM)
   - Cross-chain bridge (deBridge, Across, etc.)
   - Direct transfer from another HyperEVM wallet

Once the EOA is funded, you can operate autonomously on HyperEVM.

### Full Bridge Workflow (HyperEVM → HyperCore L1)

**Prerequisites**: EOA must have HYPE (gas) and USDC on HyperEVM. In test environment, the CLI auto-resolves `--chain HYPEREVM` to HyperEVM testnet (chain 998).

```bash
# 1. Get your EOA address
tigerpass init

# 2. Verify you have HYPE for gas and USDC on HyperEVM
tigerpass balance --chain HYPEREVM
tigerpass balance --token USDC --chain HYPEREVM

# 3. Approve USDC for CoreDepositWallet
#    Testnet: 0x0b80659a4076e9e93c7dbe0f10675a16a3e5c206
#    Mainnet: 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24
tigerpass approve \
  --token USDC \
  --spender 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --amount 100 \
  --chain HYPEREVM

# 4. Verify approval
tigerpass allowance \
  --token USDC \
  --spender 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --chain HYPEREVM

# 5. Deposit 100 USDC to HyperCore perps margin
#    amount = 100_000_000 (100 USDC × 10^6 decimals)
#    destinationDex = 0 (perps)
tigerpass exec \
  --to 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --fn "deposit(uint256,uint32)" \
  --fn-args '["100000000","0"]' \
  --chain HYPEREVM

# 6. Wait ~30s for the deposit to settle on L1, then verify
tigerpass hl info --type balances
```

**Deposit to spot** (for spot trading):

```bash
# destinationDex = 4294967295 (uint32 max → spot balance)
tigerpass exec \
  --to 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --fn "deposit(uint256,uint32)" \
  --fn-args '["100000000","4294967295"]' \
  --chain HYPEREVM
```

### Simulate Before Depositing

For large deposits, use `--simulate` to dry-run the transaction before real execution:

```bash
tigerpass exec \
  --to 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --fn "deposit(uint256,uint32)" \
  --fn-args '["100000000","0"]' \
  --chain HYPEREVM --simulate
```

Simulation runs `eth_call` and returns `{"simulated": true, "success": true/false, ...}` without signing or paying gas.

### Withdraw (HyperCore L1 → HyperEVM)

Withdrawing USDC from HyperCore back to HyperEVM uses the Hyperliquid exchange API's `spotSend` action — send to the system address `0x2000000000000000000000000000000000000000`. The protocol automatically credits your HyperEVM EOA.

**This is not yet a CLI command.** The user must withdraw via the Hyperliquid UI for now. The `withdrawable` field in `tigerpass hl info --type balances` shows how much can be withdrawn.

### Approve Max (One-Time)

For repeated deposits, approve unlimited USDC once:

```bash
tigerpass approve \
  --token USDC \
  --spender 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 \
  --amount max \
  --chain HYPEREVM
```

### End-to-End: From Zero to First Hyperliquid Trade

```bash
# === One-time setup (requires user to fund EOA first) ===

# 1. Initialize and register
tigerpass init
tigerpass register

# 2. Tell the user your EOA address — they fund it with HYPE + USDC on HyperEVM

# 3. Verify funding arrived
tigerpass balance --chain HYPEREVM           # HYPE for gas
tigerpass balance --token USDC --chain HYPEREVM  # USDC to deposit

# 4. Bridge USDC from HyperEVM → HyperCore L1 (perps margin)
tigerpass approve --token USDC --spender 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 --amount max --chain HYPEREVM
tigerpass exec --to 0x6b9e773128f453f5c2c60935ee2de2cbc5390a24 --fn "deposit(uint256,uint32)" --fn-args '["100000000","0"]' --chain HYPEREVM

# 5. Authorize builder fee
tigerpass hl approve-builder

# === Ready to trade ===

# 6. Check balance on L1 (NOT HyperEVM balance!)
tigerpass hl info --type balances

# 7. Place your first order
tigerpass hl order --coin BTC --side buy --price 95000 --size 0.01
```

### Important Notes

- `deposit(amount, destinationDex)` takes the **exact amount in atomic units** (6 decimals) — `10000000` = 10 USDC
- `destinationDex=0` → perps margin, `destinationDex=4294967295` → spot balance
- Gas on HyperEVM is paid in HYPE — ensure your EOA has HYPE before any HyperEVM transaction
- Deposits typically settle within 30 seconds on L1
- **Do NOT confuse** `tigerpass balance --chain HYPEREVM` (HyperEVM on-chain) with `tigerpass hl info --type balances` (L1 trading) — they are different pools
- Withdraw (L1 → HyperEVM) is not yet a CLI command — use the Hyperliquid UI

---

## EOA Transactions

The `--eoa` flag lets you execute transactions directly from your EOA on **any chain**. On HyperEVM (chain ID 999/998), `--eoa` is automatic — it's an EOA-only chain.

Use `--eoa` when:
- Your EOA already holds the tokens (funded externally or via `tigerpass pay --to <eoaAddr>`)
- The target protocol requires EOA interaction
- You want simpler/faster execution without Smart Account overhead

### Safe vs EOA Path

| | Safe (default) | EOA (`--eoa` or HyperEVM) |
|---|---|---|
| **Transaction source** | Safe wallet (`walletAddress`) | EOA (`eoaAddress`) |
| **Gas payment** | Paymaster (sponsored) | EOA pays in native token |
| **Signing** | ERC-4337 UserOp | EIP-155 legacy tx |
| **Batch exec** | Atomic (multiSend) | Sequential (non-atomic) |
| **Private mempool** | Supported (`--private`) | Not available |
| **Output field** | `walletAddress`, `userOpHash` | `fromAddress`, `txHash` |
| **Available on** | All Smart Account chains | Any chain (flag) / HyperEVM (auto) |

### Transfer with --eoa

```bash
# Send from EOA on Base
tigerpass pay --to 0xRecipient --amount 10 --token USDC --eoa

# Send HYPE on HyperEVM (--eoa is automatic)
tigerpass pay --to 0xRecipient --amount 0.1 --chain HYPEREVM

# Send USDC on HyperEVM
tigerpass pay --to 0xRecipient --amount 10 --token USDC --chain HYPEREVM
```

### Approve with --eoa

```bash
# Approve on Base from EOA
tigerpass approve --token USDC --spender 0xContract --amount 100 --eoa

# Approve on HyperEVM (--eoa is automatic)
tigerpass approve --token USDC --spender 0xContract --amount 100 --chain HYPEREVM

# Unlimited approval
tigerpass approve --token USDC --spender 0xContract --amount max --eoa
```

### Execute with --eoa

```bash
# Execute on any chain from EOA
tigerpass exec --to 0xContract \
  --fn "someFunction(address,uint256)" \
  --fn-args '["0xAddr","1000000"]' \
  --eoa

# Execute on HyperEVM (--eoa is automatic)
tigerpass exec --to 0xContract \
  --fn "someFunction(address,uint256)" \
  --fn-args '["0xAddr","1000000"]' \
  --chain HYPEREVM

# Simulate before executing
tigerpass exec --to 0xContract \
  --fn "riskyFunction(uint256)" \
  --fn-args '["1000"]' --eoa --simulate

# Batch calls (sequential — NOT atomic! Max 10 calls.)
tigerpass exec --calls '[
  {"to":"0xA","value":"0x0","data":"0x..."},
  {"to":"0xB","value":"0x0","data":"0x..."}
]' --eoa
```

**Batch note**: With `--eoa`, batch `exec --calls` is sequential — each call is a separate transaction. If call 2 fails, call 1 has already executed and cannot be rolled back. Output includes `batchTxHashes` array with individual transaction hashes and a `warning` field.

### Read-Only Operations

These work identically to Safe chains — no gas needed:

```bash
# Balance
tigerpass balance --chain HYPEREVM
tigerpass balance --token USDC --chain HYPEREVM
tigerpass balance --address 0xAny --chain HYPEREVM

# Read contract
tigerpass call --to 0xContract --fn "balanceOf(address)" --fn-args '["0xAddr"]' --chain HYPEREVM

# Token info
tigerpass token-info --token USDC --chain HYPEREVM

# Event logs
tigerpass logs --address 0xContract --topic 0x... --chain HYPEREVM
```

---

## Fund EOA for Polymarket

Polymarket uses **EOA directly** on Polygon (not Safe, `sigType=0`).

EOA on Polygon needs:
- **POL** — gas
- **USDC.e** (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`) — collateral

| Token | Address | Polymarket |
|-------|---------|------------|
| **USDC.e** (bridged) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` | YES |
| USDC (native) | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` | NO — swap first |

### Option A: Transfer from Safe Wallet

```bash
# 1. Check Safe balance on Polygon
tigerpass balance --chain POLYGON

# 2. Send POL for gas
tigerpass pay --to <eoaAddr> --amount 0.5 --token POL --chain POLYGON

# 3a. If Safe has USDC.e — send directly
tigerpass pay --to <eoaAddr> --amount 100 --token 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --chain POLYGON

# 3b. If Safe only has native USDC — swap then send
tigerpass swap --from USDC --to 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --amount 100 --chain POLYGON
tigerpass pay --to <eoaAddr> --amount 100 --token 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --chain POLYGON
```

### Option B: User Funds EOA Externally

`tigerpass init` to get EOA address. User sends POL + USDC.e via CEX / bridge / direct transfer.

### Verify Funding

```bash
tigerpass balance --eoa --chain POLYGON                                                        # POL
tigerpass balance --eoa --token 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --chain POLYGON     # USDC.e
```

### End-to-End: Zero to First Polymarket Trade

```bash
# 1. Init + register
tigerpass init
tigerpass register

# 2. Fund EOA on Polygon
tigerpass pay --to <eoaAddr> --amount 0.5 --token POL --chain POLYGON
tigerpass swap --from USDC --to 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --amount 100 --chain POLYGON
tigerpass pay --to <eoaAddr> --amount 100 --token 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174 --chain POLYGON

# 3. Auth + Approve (one-time setup, in order)
tigerpass pm auth
tigerpass pm approve

# 4. Trade
tigerpass pm info --type balances
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55
```

---

## Polymarket

`tigerpass pm` trades prediction market outcome tokens on Polymarket. **EOA-only** (Polygon mainnet), uses **USDC.e** as collateral.

Ensure EOA has POL + USDC.e before trading — see [Fund EOA for Polymarket](#fund-eoa-for-polymarket).

### Setup (Once, in order)

```bash
tigerpass pm auth      # 1. Derive API credentials (stored in Keychain)
tigerpass pm approve   # 2. Approve USDC.e for Polymarket exchange
```

### Trading Workflow

```bash
# 1. Browse available markets
tigerpass pm info --type markets

# 2. Check USDC.e balance on Polymarket
tigerpass pm info --type balances

# 3. Buy YES tokens at 55 cents ($100 worth)
tigerpass pm order --market <conditionId> --outcome YES --side buy --amount 100 --price 0.55

# 4. Check your position
tigerpass pm info --type positions

# 5. Check open orders
tigerpass pm info --type orders
```

### Order Types

```bash
# GTC — Good 'til Cancelled (default)
tigerpass pm order --market <cid> --outcome YES --side buy --amount 100 --price 0.55

# FOK — Fill or Kill (entire amount or nothing)
tigerpass pm order --market <cid> --outcome YES --side buy --amount 100 --price 0.55 --type FOK

# If you already have the token ID (skip market + outcome lookup)
tigerpass pm order --token-id <tokenId> --side buy --amount 100 --price 0.55

# Neg-risk market (multi-outcome events)
tigerpass pm order --market <cid> --outcome YES --side buy --amount 100 --price 0.55 --neg-risk
```

### Cancel Orders

```bash
# Cancel a specific order
tigerpass pm cancel --order-id 0xOrderId...

# Cancel all open orders
tigerpass pm cancel --all
```

### Account Queries

```bash
# Markets — question, conditionId, token prices, active/closed
tigerpass pm info --type markets

# Positions — asset, size, avg price, current price, PnL
tigerpass pm info --type positions

# Balance — USDC available on Polymarket
tigerpass pm info --type balances

# Trade history — id, side, size, price, outcome, status, txHash
tigerpass pm info --type trades

# Open orders — id, side, price, size, matched amount, outcome
tigerpass pm info --type orders
```

---

## Custom Contract Interactions

For any DeFi protocol that doesn't have a built-in command (Uniswap, AAVE, Compound, Curve, etc.), use `tigerpass exec` with ABI encoding. The `--fn` flag is preferred because it's self-documenting and encoding is handled automatically.

### Universal Pattern

Almost every DeFi interaction follows this flow:

```bash
# 1. Check you have the input token
tigerpass balance --token USDC

# 2. Approve the protocol to spend your tokens (skip for native ETH)
tigerpass approve --token USDC --spender <PROTOCOL_ROUTER> --amount max

# 3. Verify approval
tigerpass allowance --token USDC --spender <PROTOCOL_ROUTER>

# 4. Simulate the operation first (dry-run, no gas spent)
tigerpass exec --to <PROTOCOL_ROUTER> \
  --fn "<function_signature>" \
  --fn-args '[...]' --simulate

# 5. Execute the DeFi operation
tigerpass exec --to <PROTOCOL_ROUTER> \
  --fn "<function_signature>" \
  --fn-args '[...]' --private

# 6. Verify the result
tigerpass balance --token WETH
```

### Example: AAVE V3 — Supply & Borrow

```bash
# AAVE V3 Pool on Base: 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5

# Supply 1000 USDC
tigerpass approve --token USDC --spender 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5 --amount 1000
tigerpass exec --to 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5 \
  --fn "supply(address,uint256,address,uint16)" \
  --fn-args '["0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913","1000000000","<YOUR_SAFE_ADDRESS>","0"]'

# Borrow 0.1 WETH (variable rate = 2)
tigerpass exec --to 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5 \
  --fn "borrow(address,uint256,uint256,uint16,address)" \
  --fn-args '["0x4200000000000000000000000000000000000006","100000000000000000","2","0","<YOUR_SAFE_ADDRESS>"]'

# Check health factor
tigerpass call --to 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5 \
  --fn "getUserAccountData(address)" \
  --fn-args '["<YOUR_SAFE_ADDRESS>"]'
```

### Batch Transactions (Approve + Action)

On Safe (default), batch calls are **atomic** — all succeed or all revert. With `--eoa`, batch calls are sequential (non-atomic).

```bash
# Approve + swap in one atomic transaction (max 10 calls)
tigerpass exec --calls '[
  {"to":"0xUSDC","value":"0x0","data":"0x095ea7b3..."},
  {"to":"0xRouter","value":"0x0","data":"0x..."}
]' --private
```

Use `tigerpass abi encode` to generate calldata:

```bash
tigerpass abi encode --sig "approve(address,uint256)" \
  --args '["0xRouter","115792089237316195423570985008687907853269984665640564039457584007913129639935"]'
```

### Reading Prices

```bash
# Chainlink price feed
tigerpass call --to 0xChainlinkFeed --fn "latestRoundData()"
```

### Key Contract Addresses

**Base (chainId 8453)**
| Contract | Address |
|----------|---------|
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |
| AAVE V3 Pool | `0xA238Dd80C259a72e81d7e4664a9801593F98d1c5` |

**Ethereum (chainId 1)**
| Contract | Address |
|----------|---------|
| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` |
| WETH | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| AAVE V3 Pool | `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` |

**Polygon (chainId 137)**
| Contract | Address |
|----------|---------|
| **USDC.e** (bridged — Polymarket collateral) | `0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174` |
| USDC (native — NOT for Polymarket) | `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359` |
| Polymarket CTF Exchange | `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` |
| Polymarket NegRisk Exchange | `0xC5d563A36AE78145C45a50134d48A1215220f80a` |

**Hyperliquid HyperEVM (chainId 999)**
| Contract | Address |
|----------|---------|
| Native USDC | `0xb88339CB7199b77E23DB6E890353E22632Ba630f` |
| USDT | `0x10982ad645D5A112606534d8567418Cf64c14cB5` |
| CoreDepositWallet | `0x6b9e773128f453f5c2c60935ee2de2cbc5390a24` |
| HYPE (native) | `0x2222222222222222222222222222222222222222` (system) |

> Contract addresses change over time. Always verify via official protocol docs before real-money transactions.

---

## Tips

### Amount Conversions

Token amounts in `exec` are always in the smallest unit (atomic):
- ETH: 18 decimals → 1 ETH = 1000000000000000000 (1e18)
- USDC: 6 decimals → 1 USDC = 1000000 (1e6)
- WBTC: 8 decimals → 1 WBTC = 100000000 (1e8)

The `swap`, `pay`, and `hl order` commands handle this automatically (human-readable input). The `exec` command works with raw atomic values. Use `tigerpass token-info --token X` to check decimals.

### Safety Checklist

1. **Check balance first** — `tigerpass balance --token X` before any operation
2. **Check the right pool** — HyperEVM balance ≠ HL L1 balance ≠ Safe wallet balance ≠ Polymarket EOA balance (see SKILL.md "Five Balance Pools")
3. **Use `--simulate`** for complex `exec` transactions — dry-run before real execution
4. **Use `--private`** for swaps and DeFi — prevents MEV sandwich attacks (Safe chains only, ignored on HyperEVM)
5. **Verify allowance** — `tigerpass allowance` after approve, before the main transaction
6. **Check tx status** — `tigerpass tx --hash 0x... --wait` for confirmation

### When to Use Which

| Want to... | Use |
|-----------|-----|
| Swap tokens on any DEX | `tigerpass swap` (automatic routing, best price) |
| Trade perpetual futures | `tigerpass hl order` (Hyperliquid) |
| Trade spot tokens on HL | `tigerpass hl order --spot` (Hyperliquid spot) |
| Deposit USDC for HL trading | Bridge flow: `approve` + `exec` on HyperEVM (see Bridge section) |
| Bet on events/elections | `tigerpass pm order` (Polymarket, Polygon mainnet, EOA + USDC.e) |
| Transfer from EOA (any chain) | `tigerpass pay --eoa` or `--chain HYPEREVM` |
| Execute from EOA (any chain) | `tigerpass exec --eoa` or `--chain HYPEREVM` |
| Swap from EOA | `tigerpass swap --eoa` (any 0x-supported chain) |
| Supply/borrow on lending protocols | `tigerpass exec` with AAVE/Compound ABI |
| Interact with any other contract | `tigerpass exec --fn` or `--data` |
| Read on-chain state (no gas) | `tigerpass call --fn` |
