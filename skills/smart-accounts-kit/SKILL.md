---
name: smart-accounts-kit
description: Web3 development using MetaMask Smart Accounts Kit. Use when the user wants to build dApps with ERC-4337 smart accounts, send user operations, batch transactions, configure signers (EOA, passkey, multisig), implement gas abstraction with paymasters, create delegations, or request advanced permissions (ERC-7715). Supports Viem integration, multiple signer types (Dynamic, Web3Auth, Wagmi), gasless transactions, and the Delegation Framework.
metadata: {"openclaw":{"emoji":"🦊","homepage":"https://docs.metamask.io/smart-accounts-kit"}}
---
## Quick Reference

This skill file provides quick access to the MetaMask Smart Accounts Kit v0.3.0. For detailed information, refer to the specific reference files.

**📚 Detailed References:**

- [Smart Accounts Reference](./references/smart-accounts.md) - Account creation, implementations, signers
- [Delegations Reference](./references/delegations.md) - Delegation lifecycle, scopes, caveats
- [Advanced Permissions Reference](./references/advanced-permissions.md) - ERC-7715 permissions via MetaMask

## Package Installation

```bash
npm install @metamask/smart-accounts-kit@0.3.0
```

For custom caveat enforcers:

```bash
forge install metamask/delegation-framework@v1.3.0
```

## Core Concepts Summary

### 1. Smart Accounts (ERC-4337)

Three implementation types:

| Implementation | Best For | Key Feature |
|---------------|----------|-------------|
| **Hybrid** (`Implementation.Hybrid`) | Standard dApp users | EOA + passkey signers, most flexible |
| **MultiSig** (`Implementation.MultiSig`) | Treasury/DAO operations | Threshold-based security, Safe-compatible |
| **Stateless7702** (`Implementation.Stateless7702`) | Power users with existing EOA | Keep same address, add smart account features via EIP-7702 |

**Decision Guide:**
- Building for general users? → Hybrid
- Managing treasuries or multi-party control? → MultiSig  
- Upgrading existing EOAs without address change? → Stateless7702

### 2. Delegation Framework (ERC-7710)

Grant permissions from delegator to delegate:

- **Scopes** - Initial authority (spending limits, function calls)
- **Caveats** - Restrictions enforced by smart contracts
- **Types** - Root, open root, redelegation, open redelegation
- **Lifecycle** - Create → Sign → Store → Redeem

### 3. Advanced Permissions (ERC-7715)

Request permissions via MetaMask extension:

- Human-readable UI confirmations
- ERC-20 and native token permissions
- Requires MetaMask Flask 13.5.0+
- User must have smart account

## Quick Code Examples

### Create Smart Account

```typescript
import { Implementation, toMetaMaskSmartAccount } from '@metamask/smart-accounts-kit'
import { privateKeyToAccount } from 'viem/accounts'

const account = privateKeyToAccount('0x...')

const smartAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Hybrid,
  deployParams: [account.address, [], [], []],
  deploySalt: '0x',
  signer: { account },
})
```

### Create Delegation

```typescript
import { createDelegation } from '@metamask/smart-accounts-kit'
import { parseUnits } from 'viem'

const delegation = createDelegation({
  to: delegateAddress,
  from: delegatorSmartAccount.address,
  environment: delegatorSmartAccount.environment,
  scope: {
    type: 'erc20TransferAmount',
    tokenAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
    maxAmount: parseUnits('10', 6),
  },
  caveats: [
    { type: 'timestamp', afterThreshold: now, beforeThreshold: expiry },
    { type: 'limitedCalls', limit: 5 },
  ],
})
```

### Sign Delegation

```typescript
const signature = await smartAccount.signDelegation({ delegation })
const signedDelegation = { ...delegation, signature }
```

### Redeem Delegation

```typescript
import { createExecution, ExecutionMode } from '@metamask/smart-accounts-kit'
import { DelegationManager } from '@metamask/smart-accounts-kit/contracts'
import { encodeFunctionData, erc20Abi } from 'viem'

const callData = encodeFunctionData({
  abi: erc20Abi,
  args: [recipient, parseUnits('1', 6)],
  functionName: 'transfer',
})

const execution = createExecution({ target: tokenAddress, callData })

const redeemCalldata = DelegationManager.encode.redeemDelegations({
  delegations: [[signedDelegation]],
  modes: [ExecutionMode.SingleDefault],
  executions: [[execution]],
})

// Via smart account
const userOpHash = await bundlerClient.sendUserOperation({
  account: delegateSmartAccount,
  calls: [{ to: delegateSmartAccount.address, data: redeemCalldata }],
})

// Via EOA
const txHash = await delegateWalletClient.sendTransaction({
  to: environment.DelegationManager,
  data: redeemCalldata,
})
```

### Request Advanced Permissions

```typescript
import { erc7715ProviderActions } from '@metamask/smart-accounts-kit/actions'

const walletClient = createWalletClient({
  transport: custom(window.ethereum),
}).extend(erc7715ProviderActions())

const grantedPermissions = await walletClient.requestExecutionPermissions([
  {
    chainId: chain.id,
    expiry: now + 604800,
    signer: {
      type: 'account',
      data: { address: sessionAccount.address },
    },
    permission: {
      type: 'erc20-token-periodic',
      data: {
        tokenAddress,
        periodAmount: parseUnits('10', 6),
        periodDuration: 86400,
        justification: 'Transfer 10 USDC daily',
      },
    },
    isAdjustmentAllowed: true,
  },
])
```

### Redeem Advanced Permissions

```typescript
// Smart account
import { erc7710BundlerActions } from '@metamask/smart-accounts-kit/actions'

const bundlerClient = createBundlerClient({
  client: publicClient,
  transport: http(bundlerUrl),
}).extend(erc7710BundlerActions())

const permissionsContext = grantedPermissions[0].context
const delegationManager = grantedPermissions[0].signerMeta.delegationManager

const userOpHash = await bundlerClient.sendUserOperationWithDelegation({
  publicClient,
  account: sessionAccount,
  calls: [
    {
      to: tokenAddress,
      data: calldata,
      permissionsContext,
      delegationManager,
    },
  ],
})

// EOA
import { erc7710WalletActions } from '@metamask/smart-accounts-kit/actions'

const walletClient = createWalletClient({
  account: sessionAccount,
  chain,
  transport: http(),
}).extend(erc7710WalletActions())

const txHash = await walletClient.sendTransactionWithDelegation({
  to: tokenAddress,
  data: calldata,
  permissionsContext,
  delegationManager,
})
```

## Key API Methods

### Smart Accounts

- `toMetaMaskSmartAccount()` - Create smart account
- `aggregateSignature()` - Combine multisig signatures
- `signDelegation()` - Sign delegation
- `signUserOperation()` - Sign user operation
- `signMessage()` / `signTypedData()` - Standard signing

### Delegations

- `createDelegation()` - Create delegation with delegate
- `createOpenDelegation()` - Create open delegation
- `createCaveatBuilder()` - Build caveats array
- `createExecution()` - Create execution struct
- `redeemDelegations()` - Encode redemption calldata
- `signDelegation()` - Sign with private key
- `getSmartAccountsEnvironment()` - Resolve environment
- `deploySmartAccountsEnvironment()` - Deploy contracts
- `overrideDeployedEnvironment()` - Override environment

### Advanced Permissions

- `erc7715ProviderActions()` - Wallet client extension for requesting
- `requestExecutionPermissions()` - Request permissions
- `erc7710BundlerActions()` - Bundler client extension
- `sendUserOperationWithDelegation()` - Redeem with smart account
- `erc7710WalletActions()` - Wallet client extension
- `sendTransactionWithDelegation()` - Redeem with EOA

## Supported ERC-7715 Permission Types

### ERC-20 Token Permissions

| Permission Type | Description |
|----------------|-------------|
| `erc20-token-periodic` | Per-period limit that resets at each period |
| `erc20-token-stream` | Linear streaming with amountPerSecond rate |

### Native Token Permissions

| Permission Type | Description |
|----------------|-------------|
| `native-token-periodic` | Per-period ETH limit that resets |
| `native-token-stream` | Linear ETH streaming with amountPerSecond rate |

## Common Delegation Scopes

### Spending Limits

| Scope                       | Description                   |
| --------------------------- | ----------------------------- |
| `erc20TransferAmount`       | Fixed ERC-20 limit            |
| `erc20PeriodTransfer`       | Per-period ERC-20 limit       |
| `erc20Streaming`            | Linear streaming ERC-20       |
| `nativeTokenTransferAmount` | Fixed native token limit      |
| `nativeTokenPeriodTransfer` | Per-period native token limit |
| `nativeTokenStreaming`      | Linear streaming native       |
| `erc721Transfer`            | ERC-721 (NFT) transfer        |

### Function Calls

| Scope               | Description                        |
| ------------------- | ---------------------------------- |
| `functionCall`      | Specific methods/addresses allowed |
| `ownershipTransfer` | Ownership transfers only           |

## Common Caveat Enforcers

### Target & Method

- `allowedTargets` - Limit callable addresses
- `allowedMethods` - Limit callable methods
- `allowedCalldata` - Validate specific calldata
- `exactCalldata` / `exactCalldataBatch` - Exact calldata match
- `exactExecution` / `exactExecutionBatch` - Exact execution match

### Value & Token

- `valueLte` - Limit native token value
- `erc20TransferAmount` - Limit ERC-20 amount
- `erc20BalanceChange` - Validate ERC-20 balance change
- `erc721Transfer` / `erc721BalanceChange` - ERC-721 restrictions
- `erc1155BalanceChange` - ERC-1155 validation

### Time & Frequency

- `timestamp` - Valid time range (seconds)
- `blockNumber` - Valid block range
- `limitedCalls` - Limit redemption count
- `erc20PeriodTransfer` / `erc20Streaming` - Time-based ERC-20
- `nativeTokenPeriodTransfer` / `nativeTokenStreaming` - Time-based native

### Security & State

- `redeemer` - Limit redemption to specific addresses
- `id` - One-time delegation with ID
- `nonce` - Bulk revocation via nonce
- `deployed` - Auto-deploy contract
- `ownershipTransfer` - Ownership transfer only
- `nativeTokenPayment` - Require payment
- `nativeBalanceChange` - Validate native balance
- `multiTokenPeriod` - Multi-token period limits

## Execution Modes

| Mode            | Chains   | Processing  | On Failure |
| --------------- | -------- | ----------- | ---------- |
| `SingleDefault` | One      | Sequential  | Revert     |
| `SingleTry`     | One      | Sequential  | Continue   |
| `BatchDefault`  | Multiple | Interleaved | Revert     |
| `BatchTry`      | Multiple | Interleaved | Continue   |

## Contract Addresses (v1.3.0)

### Core

| Contract              | Address                                      |
| --------------------- | -------------------------------------------- |
| EntryPoint            | `0x0000000071727De22E5E9d8BAf0edAc6f37da032` |
| SimpleFactory         | `0x69Aa2f9fe1572F1B640E1bbc512f5c3a734fc77c` |
| DelegationManager     | `0xdb9B1e94B5b69Df7e401DDbedE43491141047dB3` |
| MultiSigDeleGatorImpl | `0x56a9EdB16a0105eb5a4C54f4C062e2868844f3A7` |
| HybridDeleGatorImpl   | `0x48dBe696A4D990079e039489bA2053B36E8FFEC4` |

## Critical Rules

### Always Required

1. **Always use caveats** - Never create unrestricted delegations
2. **Deploy delegator first** - Account must be deployed before redeeming
3. **Check smart account status** - ERC-7715 requires user has smart account

### Behavior

4. **Caveats are cumulative** - In delegation chains, restrictions stack
5. **Function call default** - v0.3.0 defaults to NO native token (use `valueLte`)
6. **Batch mode caveat** - No compatible caveat enforcers available

### Requirements

7. **ERC-7715 requirements** - MetaMask Flask 13.5.0+, smart account
8. **Multisig threshold** - Need at least threshold signers
9. **7702 upgrade** - Stateless7702 requires EIP-7702 upgrade first

## Advanced Patterns

### Parallel User Operations (Nonce Keys)

Smart accounts use a 256-bit nonce structure: 192-bit key + 64-bit sequence. Each unique key has its own independent sequence, enabling parallel execution. This is critical for backend services processing multiple delegations concurrently.

#### Installation

For proper nonce handling, install the permissionless SDK alongside the Smart Accounts Kit:

```bash
npm install permissionless
```

#### How Parallel Nonces Work

ERC-4337 uses a single uint256 nonce where:
- **192 bits** = key identifier (allows parallel streams)
- **64 bits** = sequence number (increments per key)

Each key has an independent sequence, so UserOps with different keys execute in parallel without ordering constraints.

#### Getting Nonce with Permissionless

```typescript
import { getAccountNonce } from 'permissionless'
import { entryPoint07Address } from 'viem/account-abstraction'

// Get nonce for a specific key
const parallelNonce = await getAccountNonce(publicClient, {
  address: smartAccount.address,
  entryPointAddress: entryPoint07Address,
  key: BigInt(Date.now()), // Unique key for parallel execution
})

const userOpHash = await bundlerClient.sendUserOperation({
  account: smartAccount,
  calls: [redeemCalldata],
  nonce: parallelNonce, // Properly encoded 256-bit nonce
})
```

#### Parallel Execution Pattern

```typescript
import { getAccountNonce } from 'permissionless'
import { entryPoint07Address } from 'viem/account-abstraction'

// Execute multiple redemption UserOps in parallel
const redeems = await Promise.all(
  delegations.map(async (delegation, index) => {
    // Generate unique key for this operation
    const nonceKey = BigInt(Date.now()) + BigInt(index * 1000)
    
    // Get properly encoded nonce for this key
    const nonce = await getAccountNonce(publicClient, {
      address: backendSmartAccount.address,
      entryPointAddress: entryPoint07Address,
      key: nonceKey,
    })
    
    const redeemCalldata = DelegationManager.encode.redeemDelegations({
      delegations: [[delegation]],
      modes: [ExecutionMode.SingleDefault],
      executions: [[execution]],
    })
    
    return bundlerClient.sendUserOperation({
      account: backendSmartAccount,
      calls: [{ to: backendSmartAccount.address, data: redeemCalldata }],
      nonce, // Parallel execution enabled via unique key
    })
  })
)
```

#### Without Permissionless (Manual Approach)

The EntryPoint contract encodes nonce as: `sequence | (key << 64)`

If not using permissionless, encode manually:

```typescript
// EntryPoint: nonceSequenceNumber[sender][key] | (uint256(key) << 64)
const key = BigInt(Date.now())
const sequence = 0n // New key starts at sequence 0
const nonce = sequence | (key << 64n)
// Or equivalently: (key << 64n) | sequence
```

However, `getAccountNonce` from permissionless is recommended as it:
- Fetches the current sequence for the key from the EntryPoint
- Properly encodes the 256-bit value
- Handles edge cases and validation

#### Key Points

- **Different keys = parallel execution** — no ordering guarantees between different keys
- **Same key = sequential execution** — sequence increments monotonically per key
- **Use cases:** Backend redemption services, DCA apps, high-frequency trading, batch operations
- **Nonce generation:** `getAccountNonce` returns the full 256-bit nonce properly encoded

#### Common Mistakes

| Mistake | Result |
|---------|--------|
| Reusing same nonce key | Sequential execution (defeats purpose) |
| Using `Date.now()` without offset | Potential collision if multiple ops fire simultaneously |
| Not using `getAccountNonce` | May miss current sequence, causing replacement instead of new op |
| Assuming ordering | Race conditions in dependent operations |

#### Error Handling

```typescript
const results = await Promise.allSettled(redeems)

results.forEach((result, index) => {
  if (result.status === 'rejected') {
    // Check for specific errors
    if (result.reason.message?.includes('AA25')) {
      console.error(`Nonce collision for op ${index}`)
    }
    // Handle or retry
  }
})
```

### Backend Delegation Redemption

For server-side automation (DCA bots, keeper services, automated trading):

```typescript
// 1. Backend creates its own smart account as delegate
const backendAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Hybrid,
  deployParams: [backendOwner.address, [], [], []],
  deploySalt: '0x',
  signer: { account: backendOwner },
})

// 2. Backend redeems by sending UserOp FROM its account
const userOpHash = await bundlerClient.sendUserOperation({
  account: backendAccount,
  calls: [{
    to: backendAccount.address,
    data: DelegationManager.encode.redeemDelegations({
      delegations: [[userDelegation]],
      modes: [ExecutionMode.SingleDefault],
      executions: [[swapExecution]],
    })
  }],
})
```

**Use case:** Automated dollar-cost averaging (DCA) bots that redeem swap delegations based on market signals or scheduled intervals.

### Counterfactual Account Deployment

Delegator accounts must be deployed before delegations can be redeemed. The DelegationManager reverts with `0xb9f0f171` for counterfactual accounts.

**Solution:** Deploy automatically via first UserOp:

```typescript
// Build redemption calldata
const redeemCalldata = DelegationManager.encode.redeemDelegations({
  delegations: [[signedDelegation]],
  modes: [ExecutionMode.SingleDefault],
  executions: [[execution]],
})

// First redemption deploys the account automatically via initCode
const userOpHash = await bundlerClient.sendUserOperation({
  account: smartAccount, // Will deploy if counterfactual
  calls: [{
    to: smartAccount.address,
    data: redeemCalldata,
    value: 0n,
  }],
})
```

### Session Accounts for AI Agents

For automated services, session accounts act as isolated signers that can only operate within granted delegations. The private key can be generated ephemerally, stored in environment variables, or managed via HSM/server wallets:

```typescript
// Session account created from various sources
const sessionAccount = privateKeyToAccount(
  process.env.SESSION_KEY || generatePrivateKey() || hsmWallet.key
)

// Request delegation from user to session account
const delegation = createDelegation({
  to: sessionAccount.address,
  from: userSmartAccount.address,
  environment,
  scope: { type: 'erc20TransferAmount', tokenAddress, maxAmount: parseUnits('100', 6) },
  caveats: [
    { type: 'timestamp', afterThreshold: now, beforeThreshold: expiry },
    { type: 'limitedCalls', limit: 10 },
  ],
})
// Session account can only act within delegation constraints
```

## Common Patterns

### Pattern 1: ERC-20 with Time Limit

```typescript
const delegation = createDelegation({
  to: delegate,
  from: delegator,
  environment,
  scope: {
    type: 'erc20TransferAmount',
    tokenAddress,
    maxAmount: parseUnits('100', 6),
  },
  caveats: [
    { type: 'timestamp', afterThreshold: now, beforeThreshold: expiry },
    { type: 'limitedCalls', limit: 10 },
    { type: 'redeemer', redeemers: [delegate] },
  ],
})
```

### Pattern 2: Function Call with Value

```typescript
const delegation = createDelegation({
  to: delegate,
  from: delegator,
  environment,
  scope: {
    type: 'functionCall',
    targets: [contractAddress],
    selectors: ['transfer(address,uint256)'],
    valueLte: { maxValue: parseEther('0.1') },
  },
  caveats: [{ type: 'allowedMethods', selectors: ['transfer(address,uint256)'] }],
})
```

### Pattern 3: Periodic Native Token

```typescript
const delegation = createDelegation({
  to: delegate,
  from: delegator,
  environment,
  scope: {
    type: 'nativeTokenPeriodTransfer',
    periodAmount: parseEther('0.01'),
    periodDuration: 86400,
    startDate: now,
  },
})
```

### Pattern 4: Redelegation Chain

```typescript
// Alice → Bob (100 USDC)
const aliceToBob = createDelegation({
  to: bob,
  from: alice,
  environment,
  scope: { type: 'erc20TransferAmount', tokenAddress, maxAmount: parseUnits('100', 6) },
})

// Bob → Carol (50 USDC, subset of authority)
const bobToCarol = createDelegation({
  to: carol,
  from: bob,
  environment,
  scope: { type: 'erc20TransferAmount', tokenAddress, maxAmount: parseUnits('50', 6) },
  parentDelegation: aliceToBob,
  caveats: [{ type: 'timestamp', afterThreshold: now, beforeThreshold: expiry }],
})
```

## Troubleshooting Quick Fixes

| Issue                    | Solution                                                     |
| ------------------------ | ------------------------------------------------------------ |
| Account not deployed     | Use `bundlerClient.sendUserOperation()` to deploy            |
| Invalid signature        | Verify chain ID, delegation manager, signer permissions      |
| Caveat enforcer reverted | Check caveat parameters match execution, verify order        |
| Redemption failed        | Check delegator balance, calldata validity, target contracts |
| ERC-7715 not working     | Upgrade to Flask 13.5.0+, ensure user has smart account      |
| Permission denied        | Handle gracefully, provide manual fallback                   |
| Threshold not met        | Add more signers for multisig                                |
| 7702 not working         | Confirm EOA upgraded via EIP-7702 first                      |

## Error Code Reference

Error codes from the MetaMask Delegation Framework contracts (v1.3.0). Use a decoder like [calldata.swiss-knife.xyz](https://calldata.swiss-knife.xyz/decoder) to identify error signatures.

### DelegationManager Errors (Verified)

| Error Code | Error Name | Meaning |
|------------|-----------|---------|
| `0xb5863604` | `InvalidDelegate()` | **Caller is not the delegate** — Most common error |
| `0xb9f0f171` | `InvalidDelegator()` | Caller is not the delegator |
| `0x05baa052` | `CannotUseADisabledDelegation()` | Attempting to redeem a disabled delegation |
| `0xded4370e` | `InvalidAuthority()` | Delegation chain authority validation failed |
| `0x1bcaf69f` | `BatchDataLengthMismatch()` | Array lengths don't match in batch |
| `0x005ecddb` | `AlreadyDisabled()` | Delegation has already been disabled |
| `0xf2a5f75a` | `AlreadyEnabled()` | Delegation is already enabled |
| `0xf645eedf` | `ECDSAInvalidSignature()` | Invalid ECDSA signature format |
| `0xfce698f7` | `ECDSAInvalidSignatureLength(uint256)` | Signature length is incorrect |
| `0xd78bce0c` | `ECDSAInvalidSignatureS(bytes32)` | Signature S value is invalid |
| `0xac241e11` | `EmptySignature()` | Signature is empty |
| `0xd93c0665` | `EnforcedPause()` | Contract is paused |
| `0x3db6791c` | `InvalidEOASignature()` | EOA signature verification failed |
| `0x155ff427` | `InvalidERC1271Signature()` | Smart contract signature (ERC1271) failed |
| `0x118cdaa7` | `OwnableUnauthorizedAccount(address)` | Unauthorized account attempted owner-only action |
| `0x1e4fbdf7` | `OwnableInvalidOwner(address)` | Invalid owner address in ownership transfer |
| `0xf6b6ef5b` | `InvalidShortString()` | String parameter too short |
| `0xaa0ea2d8` | `StringTooLong(string)` | String parameter exceeds maximum length |

### DeleGatorCore Errors (Verified)

| Error Code | Error Name | Meaning |
|------------|-----------|---------|
| `0xd663742a` | `NotEntryPoint()` | Caller is not the EntryPoint contract |
| `0x0796d945` | `NotEntryPointOrSelf()` | Caller is neither EntryPoint nor this contract |
| `0x1a4b3a04` | `NotDelegationManager()` | Caller is not the DelegationManager |
| `0xb96fcfe4` | `UnsupportedCallType(bytes1)` | Execution call type not supported |
| `0x1187dc06` | `UnsupportedExecType(bytes1)` | Execution type not supported |
| `0x29c3b7ee` | `NotSelf()` | Caller is not this contract itself |

### Common Caveat Enforcer Errors (Revert Strings)

| Error String | Meaning |
|--------------|---------|
| `AllowedTargetsEnforcer:target-address-not-allowed` | Target contract not in allowed list |
| `AllowedTargetsEnforcer:invalid-terms-length` | Terms length not multiple of 20 bytes |
| `ERC20TransferAmountEnforcer:invalid-terms-length` | Terms must be 52 bytes |
| `ERC20TransferAmountEnforcer:invalid-contract` | Target doesn't match allowed token |
| `ERC20TransferAmountEnforcer:invalid-method` | Method is not `transfer` |
| `ERC20TransferAmountEnforcer:allowance-exceeded` | Transfer exceeds delegated limit |
| `CaveatEnforcer:invalid-call-type` | Must use single call type |
| `CaveatEnforcer:invalid-execution-type` | Must use default execution type |

### Most Common Errors in Production

**`0xb5863604` — InvalidDelegate()**
- **Cause:** Caller doesn't match the delegate address in delegation
- **Fix:** Verify `msg.sender` equals the `to` address in the delegation

**`0xb9f0f171` — InvalidDelegator()**
- **Cause:** Attempting to enable/disable from wrong address, or counterfactual account
- **Fix:** Only delegator can enable/disable; for counterfactual, first UserOp auto-deploys

**`0x05baa052` — CannotUseADisabledDelegation()**
- **Cause:** Delegation was disabled by delegator
- **Fix:** Ask delegator to re-enable, or use different delegation

**`0xded4370e` — InvalidAuthority()**
- **Cause:** Broken delegation chain (redelegation parent mismatch)
- **Fix:** Ensure redelegation chains are properly ordered (leaf → root)

**`0x1bcaf69f` — BatchDataLengthMismatch()**
- **Cause:** Array lengths don't match in `redeemDelegations` call
- **Fix:** Ensure `permissionContexts`, `modes`, `executionCallDatas` have equal length

**`0x3db6791c` — InvalidEOASignature()**
- **Cause:** EOA signature invalid, wrong chain, or wrong delegation manager
- **Fix:** Verify signature was created with correct chain ID and delegation manager

## Resources

- **NPM:** `@metamask/smart-accounts-kit`
- **Contracts:** `metamask/delegation-framework@v1.3.0`
- **ERC Standards:** ERC-4337, ERC-7710, ERC-7715, ERC-7579
- **MetaMask Flask:** https://metamask.io/flask

## Version Info

- **Toolkit:** 0.3.0
- **Delegation Framework:** 1.3.0
- **Breaking Change:** Function call scope defaults to no native token transfer

---

**For detailed documentation, see the reference files in the `/references` directory.**
