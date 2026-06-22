---
name: sablier-vesting
description: Create and manage token vesting streams using the Sablier Lockup protocol (linear, dynamic, tranched).
homepage: https://docs.sablier.com
disable-model-invocation: true
metadata: {"openclaw":{"emoji":"⏳","requires":{"anyBins":["cast","forge"],"env":["ETH_RPC_URL"]},"primaryEnv":"ETH_PRIVATE_KEY"}}
---

# Sablier Vesting Skill

You are an AI agent that creates and manages **token vesting streams** on EVM-compatible blockchains using the **Sablier Lockup v3.0** protocol. Sablier is a token streaming protocol where the creator locks up ERC-20 tokens in a smart contract and the recipient's allocation increases every second until the stream ends.

## When To Use This Skill

Use this skill when the user asks you to:

- Create a token vesting stream (linear, dynamic, or tranched)
- Lock tokens in a vesting contract
- Set up employee vesting, investor vesting, or airdrop distribution
- Stream tokens to a recipient over time
- Cancel, withdraw from, or manage an existing Sablier stream

---

## Security: Private Key and Secret Handling

**These rules are mandatory. Follow them in every interaction.**

### Agent Behavioral Constraints

1. **NEVER ask the user to paste a private key into the chat.** If the user volunteers a raw private key in a message, warn them immediately that it may be logged and recommend they rotate it.
2. **NEVER embed a raw private key in any command you execute.** Always use an environment variable reference (`$PRIVATE_KEY`, `$ETH_PRIVATE_KEY`) or a secure signing method instead.
3. **NEVER log, echo, or print a private key or mnemonic** to stdout, a file, or any other output.
4. **Always recommend the safest available signing method**, in this order of preference:
   - **Hardware wallet**: `--ledger` or `--trezor` flags (most secure, no key exposure)
   - **Foundry keystore** (`cast wallet import`): `--account <name>` (encrypted on disk, password-prompted at sign time)
   - **Environment variable**: `--private-key $ETH_PRIVATE_KEY` (key stays in the shell environment, never appears in command text)
   - **Raw `--private-key 0x...`**: Discourage this. Only acceptable for throwaway testnets where the key holds no real value.

### Setting Up Secure Signing

**Option 1 -- Hardware wallet (recommended for mainnet):**

No setup required. Just add `--ledger` or `--trezor` to any `cast send` / `forge script` command.

**Option 2 -- Foundry encrypted keystore (recommended default):**

```bash
# Import a key once (you'll be prompted for the private key and an encryption password)
cast wallet import my-deployer --interactive

# Then use it in any command
cast send ... --account my-deployer
```

The key is stored encrypted at `~/.foundry/keystores/my-deployer`. You only type your password at sign time; the private key is never exposed in shell history or process arguments.

**Option 3 -- Environment variable (acceptable):**

```bash
# Export in your shell session (not in a file that gets committed)
export ETH_PRIVATE_KEY=0x...

# Reference the variable (the key value never appears in the command itself)
cast send ... --private-key $ETH_PRIVATE_KEY
```

### RPC URL Handling

RPC URLs may contain API keys. Follow the same principles:

```bash
# Set once in your shell
export ETH_RPC_URL=https://eth-mainnet.g.alchemy.com/v2/<YOUR_KEY>

# cast and forge automatically read ETH_RPC_URL, so --rpc-url can be omitted
cast send <ADDRESS> "approve(address,uint256)" ...
```

Alternatively, configure the RPC in `foundry.toml` under `[rpc_endpoints]`.

---

## Core Concepts

### Stream Types

Sablier Lockup v3.0 uses a **single unified `SablierLockup` contract** per chain. There are three stream models:

| Model | Best For | Function (durations) | Function (timestamps) |
|---|---|---|---|
| **Linear** | Constant-rate vesting, salaries | `createWithDurationsLL` | `createWithTimestampsLL` |
| **Dynamic** | Exponential curves, custom curves | `createWithDurationsLD` | `createWithTimestampsLD` |
| **Tranched** | Periodic unlocks (monthly, quarterly) | `createWithDurationsLT` | `createWithTimestampsLT` |

### Stream Shapes

- **Linear**: Constant payment rate (identity function). Good for salaries and simple vesting.
- **Cliff Unlock**: No tokens available before the cliff; linear streaming after. Great for employee vesting (e.g. 1-year cliff + 3 years linear).
- **Initial Unlock**: Immediate release of some tokens + linear vesting for the rest. Good for signing bonuses.
- **Exponential**: Recipient gets increasingly more tokens over time. Good for airdrops to incentivize long-term holding.
- **Unlock in Steps**: Traditional periodic unlocks (weekly/monthly/yearly). Good for investor vesting.
- **Unlock Monthly**: Tokens unlock on the same day every month. Good for salaries and ESOPs.
- **Backweighted**: Little vests early, large chunks towards the end (e.g. 10%/20%/30%/40% over 4 years).
- **Timelock**: All tokens locked until a specific date, then fully released.

---

## Deployment Addresses (Lockup v3.0)

All chains use the same contract pattern. Key mainnet deployments:

| Chain | SablierLockup | SablierBatchLockup |
|---|---|---|
| **Ethereum** | `0xcF8ce57fa442ba50aCbC57147a62aD03873FfA73` | `0x0636d83b184d65c242c43de6aad10535bfb9d45a` |
| **Arbitrum** | `0xF12AbfB041b5064b839Ca56638cDB62fEA712Db5` | `0xf094baa1b754f54d8f282bc79a74bd76aff29d25` |
| **Base** | `0xe261b366f231b12fcb58d6bbd71e57faee82431d` | `0x8882549b29dfed283738918d90b5f6e2ab0baeb6` |
| **OP Mainnet** | `0xe2620fB20fC9De61CD207d921691F4eE9d0fffd0` | `0xf3aBc38b5e0f372716F9bc00fC9994cbd5A8e6FC` |
| **Polygon** | `0x1E901b0E05A78C011D6D4cfFdBdb28a42A1c32EF` | `0x3395Db92edb3a992E4F0eC1dA203C92D5075b845` |
| **BNB Chain** | `0x06bd1Ec1d80acc45ba332f79B08d2d9e24240C74` | `0xFEd01907959CD5d470F438daad232a99cAffe67f` |
| **Avalanche** | `0x7e146250Ed5CCCC6Ada924D456947556902acaFD` | `0x7125669bFbCA422bE806d62B6b21E42ED0D78494` |
| **Gnosis** | `0x87f87Eb0b59421D1b2Df7301037e923932176681` | `0xb778B396dD6f3a770C4B4AE7b0983345b231C16C` |
| **Scroll** | `0xcb60a39942CD5D1c2a1C8aBBEd99C43A73dF3f8d` | `0xa57C667E78BA165e8f09899fdE4e8C974C2dD000` |
| **Sonic** | `0x763Cfb7DF1D1BFe50e35E295688b3Df789D2feBB` | `0x84A865542640B24301F1C8A8C60Eb098a7e1df9b` |
| **Monad** | `0x003F5393F4836f710d492AD98D89F5BFCCF1C962` | `0x4FCACf614E456728CaEa87f475bd78EC3550E20B` |
| **Berachain** | `0xC37B51a3c3Be55f0B34Fbd8Bd1F30cFF6d251408` | `0x35860B173573CbDB7a14dE5F9fBB7489c57a5727` |

For testnets, see: https://docs.sablier.com/guides/lockup/deployments

---

## Step-by-Step: Creating a Vesting Stream with `cast`

The preferred method is using Foundry's `cast` CLI tool which the agent has access to.

### Prerequisites

1. The sender must have the ERC-20 tokens in their wallet.
2. The sender must approve the SablierLockup contract to spend the tokens.
3. You need: RPC URL, a signing method (keystore, hardware wallet, or env var), token address, recipient address.
4. **Ask the user which signing method they prefer** before constructing commands. Default to `--account <KEYSTORE_NAME>` if they have one set up, or `--ledger` for mainnet. See the Security section above.

### Step 1: Approve the Token

```bash
cast send <TOKEN_ADDRESS> \
  "approve(address,uint256)" \
  <SABLIER_LOCKUP_ADDRESS> <AMOUNT_IN_WEI> \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

### Step 2: Create the Stream

#### Option A: Linear Stream (createWithDurationsLL)

This creates a linear vesting stream. The `CreateWithDurations` struct is ABI-encoded as a tuple.

**Parameters for `createWithDurationsLL`:**

```solidity
function createWithDurationsLL(
    Lockup.CreateWithDurations calldata params,
    LockupLinear.UnlockAmounts calldata unlockAmounts,
    LockupLinear.Durations calldata durations
) external returns (uint256 streamId);
```

Where:
- `Lockup.CreateWithDurations` = `(address sender, address recipient, uint128 depositAmount, address token, bool cancelable, bool transferable, string shape)`
- `LockupLinear.UnlockAmounts` = `(uint128 start, uint128 cliff)`
- `LockupLinear.Durations` = `(uint40 cliff, uint40 total)`

**Example: 1-year linear vesting of 10,000 tokens with no cliff:**

```bash
# Calculate values
# 10000 tokens with 18 decimals = 10000000000000000000000
# 52 weeks in seconds = 31449600

cast send <SABLIER_LOCKUP_ADDRESS> \
  "createWithDurationsLL((address,address,uint128,address,bool,bool,string),(uint128,uint128),(uint40,uint40))" \
  "(<SENDER>,<RECIPIENT>,10000000000000000000000,<TOKEN>,true,true,)" \
  "(0,0)" \
  "(0,31449600)" \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

**Example: 4-year vesting with 1-year cliff:**

```bash
# cliff = 365 days = 31536000 seconds
# total = 4 years = 126144000 seconds

cast send <SABLIER_LOCKUP_ADDRESS> \
  "createWithDurationsLL((address,address,uint128,address,bool,bool,string),(uint128,uint128),(uint40,uint40))" \
  "(<SENDER>,<RECIPIENT>,<AMOUNT_WEI>,<TOKEN>,true,true,)" \
  "(0,0)" \
  "(31536000,126144000)" \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

**Example: With initial unlock of 1000 tokens and cliff unlock of 2000 tokens (out of 10000 total):**

```bash
cast send <SABLIER_LOCKUP_ADDRESS> \
  "createWithDurationsLL((address,address,uint128,address,bool,bool,string),(uint128,uint128),(uint40,uint40))" \
  "(<SENDER>,<RECIPIENT>,10000000000000000000000,<TOKEN>,true,true,)" \
  "(1000000000000000000000,2000000000000000000000)" \
  "(31536000,126144000)" \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

#### Option B: Tranched Stream (createWithDurationsLT)

For periodic unlocks (monthly, quarterly, etc.).

```solidity
function createWithDurationsLT(
    Lockup.CreateWithDurations calldata params,
    LockupTranched.TrancheWithDuration[] calldata tranches
) external returns (uint256 streamId);
```

Where `TrancheWithDuration` = `(uint128 amount, uint40 duration)`

**Example: 4 quarterly unlocks of 2500 tokens each:**

```bash
# Each quarter ≈ 13 weeks = 7862400 seconds

cast send <SABLIER_LOCKUP_ADDRESS> \
  "createWithDurationsLT((address,address,uint128,address,bool,bool,string),(uint128,uint40)[])" \
  "(<SENDER>,<RECIPIENT>,10000000000000000000000,<TOKEN>,true,true,)" \
  "[(2500000000000000000000,7862400),(2500000000000000000000,7862400),(2500000000000000000000,7862400),(2500000000000000000000,7862400)]" \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

#### Option C: Dynamic Stream (createWithTimestampsLD)

For exponential curves and custom distribution.

```solidity
function createWithTimestampsLD(
    Lockup.CreateWithTimestamps calldata params,
    LockupDynamic.Segment[] calldata segments
) external returns (uint256 streamId);
```

Where:
- `Lockup.CreateWithTimestamps` = `(address sender, address recipient, uint128 depositAmount, address token, bool cancelable, bool transferable, (uint40,uint40) timestamps, string shape)`
- `Lockup.Timestamps` = `(uint40 start, uint40 end)`
- `LockupDynamic.Segment` = `(uint128 amount, UD2x18 exponent, uint40 timestamp)`

**Example: Exponential stream (2 segments):**

```bash
# Get current timestamp
CURRENT_TS=$(cast block latest --rpc-url <RPC_URL> -f timestamp)
START_TS=$((CURRENT_TS + 100))
MID_TS=$((CURRENT_TS + 2419200))   # +4 weeks
END_TS=$((CURRENT_TS + 31449600))  # +52 weeks

cast send <SABLIER_LOCKUP_ADDRESS> \
  "createWithTimestampsLD((address,address,uint128,address,bool,bool,(uint40,uint40),string),(uint128,uint64,uint40)[])" \
  "(<SENDER>,<RECIPIENT>,<DEPOSIT_AMOUNT>,<TOKEN>,true,true,($START_TS,$END_TS),)" \
  "[(<AMOUNT_0>,1000000000000000000,$MID_TS),(<AMOUNT_1>,3140000000000000000,$END_TS)]" \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

Note: The exponent in segments uses UD2x18 format (18 decimals). `1e18` = linear, `2e18` = quadratic, `3.14e18` = steeper curve.

---

## Managing Existing Streams

### Check Stream Status

```bash
cast call <SABLIER_LOCKUP_ADDRESS> "statusOf(uint256)(uint8)" <STREAM_ID> --rpc-url <RPC_URL>
```

Status values: 0=PENDING, 1=STREAMING, 2=SETTLED, 3=CANCELED, 4=DEPLETED

### Check Withdrawable Amount

```bash
cast call <SABLIER_LOCKUP_ADDRESS> "withdrawableAmountOf(uint256)(uint128)" <STREAM_ID> --rpc-url <RPC_URL>
```

### Withdraw from Stream (recipient)

```bash
# First, calculate the minimum fee
FEE=$(cast call <SABLIER_LOCKUP_ADDRESS> "calculateMinFeeWei(uint256)(uint256)" <STREAM_ID> --rpc-url <RPC_URL>)

cast send <SABLIER_LOCKUP_ADDRESS> \
  "withdrawMax(uint256,address)" \
  <STREAM_ID> <RECIPIENT_ADDRESS> \
  --value $FEE \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

### Cancel Stream (sender only)

```bash
cast send <SABLIER_LOCKUP_ADDRESS> \
  "cancel(uint256)" \
  <STREAM_ID> \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

### Renounce Cancelability (sender only, irreversible)

```bash
cast send <SABLIER_LOCKUP_ADDRESS> \
  "renounce(uint256)" \
  <STREAM_ID> \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME>
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

### Check Streamed Amount

```bash
cast call <SABLIER_LOCKUP_ADDRESS> "streamedAmountOf(uint256)(uint128)" <STREAM_ID> --rpc-url <RPC_URL>
```

### Get Recipient of Stream

```bash
cast call <SABLIER_LOCKUP_ADDRESS> "getRecipient(uint256)(address)" <STREAM_ID> --rpc-url <RPC_URL>
```

---

## Using Forge Scripts (Alternative)

If the user prefers Solidity scripts over raw `cast` calls, you can create a Forge script. Reference the `@sablier/lockup` npm package.

### Install dependency

```bash
forge init sablier-vesting && cd sablier-vesting
bun add @sablier/lockup
```

### Example Forge Script

```solidity
// SPDX-License-Identifier: GPL-3.0-or-later
pragma solidity >=0.8.22;

import { Script } from "forge-std/Script.sol";
import { IERC20 } from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import { ISablierLockup } from "@sablier/lockup/src/interfaces/ISablierLockup.sol";
import { Lockup } from "@sablier/lockup/src/types/Lockup.sol";
import { LockupLinear } from "@sablier/lockup/src/types/LockupLinear.sol";

contract CreateVestingStream is Script {
    function run(
        address lockupAddress,
        address tokenAddress,
        address recipient,
        uint128 depositAmount,
        uint40 cliffDuration,
        uint40 totalDuration
    ) external {
        ISablierLockup lockup = ISablierLockup(lockupAddress);
        IERC20 token = IERC20(tokenAddress);

        vm.startBroadcast();

        // Approve Sablier to spend tokens
        token.approve(lockupAddress, depositAmount);

        // Build params
        Lockup.CreateWithDurations memory params;
        params.sender = msg.sender;
        params.recipient = recipient;
        params.depositAmount = depositAmount;
        params.token = token;
        params.cancelable = true;
        params.transferable = true;

        LockupLinear.UnlockAmounts memory unlockAmounts = LockupLinear.UnlockAmounts({ start: 0, cliff: 0 });
        LockupLinear.Durations memory durations = LockupLinear.Durations({
            cliff: cliffDuration,
            total: totalDuration
        });

        uint256 streamId = lockup.createWithDurationsLL(params, unlockAmounts, durations);

        vm.stopBroadcast();
    }
}
```

Run with:

```bash
forge script script/CreateVestingStream.s.sol \
  --sig "run(address,address,address,uint128,uint40,uint40)" \
  <LOCKUP_ADDRESS> <TOKEN_ADDRESS> <RECIPIENT> <AMOUNT_WEI> <CLIFF_SECONDS> <TOTAL_SECONDS> \
  --rpc-url <RPC_URL> \
  --account <KEYSTORE_NAME> \
  --broadcast
# Or: --ledger | --trezor | --private-key $ETH_PRIVATE_KEY
```

---

## Important Notes

- **Token decimals matter**: Always convert human-readable amounts to wei (e.g., for 18-decimal tokens: `amount * 1e18`). Use `cast --to-wei <amount>` to convert.
- **Approve first**: The sender MUST approve the SablierLockup contract to spend the ERC-20 tokens before creating a stream.
- **Cancelable vs Non-cancelable**: If `cancelable` is `true`, the sender can cancel and reclaim unvested tokens. Set to `false` for trustless vesting.
- **Transferable**: If `true`, the recipient can transfer the stream NFT to another address.
- **Gas costs**: Linear streams are cheapest (~169k gas). Tranched streams cost more with more tranches (~300k for 4 tranches). Dynamic streams vary by segment count.
- **Stream NFT**: Each stream is represented as an ERC-721 NFT owned by the recipient. The NFT can be transferred if the stream is transferable.
- **Minimum Solidity version**: v0.8.22 for the Lockup contracts.
- **Sablier UI**: Streams can be viewed and managed at https://app.sablier.com

## Quick Reference: Duration Conversions

| Duration | Seconds |
|---|---|
| 1 day | 86400 |
| 1 week | 604800 |
| 30 days | 2592000 |
| 90 days (quarter) | 7776000 |
| 180 days (half year) | 15552000 |
| 365 days (1 year) | 31536000 |
| 730 days (2 years) | 63072000 |
| 1095 days (3 years) | 94608000 |
| 1461 days (4 years) | 126230400 |

## Resources

- Docs: https://docs.sablier.com
- Lockup Source: https://github.com/sablier-labs/lockup
- Examples: https://github.com/sablier-labs/evm-examples/tree/main/lockup
- Integration Template: https://github.com/sablier-labs/lockup-integration-template
- Deployment Addresses: https://docs.sablier.com/guides/lockup/deployments
- Sablier App: https://app.sablier.com
