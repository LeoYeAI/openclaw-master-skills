# Delegations Reference

## Overview

Delegation is the ability for a MetaMask smart account to grant permission to another smart account or EOA to perform specific executions on its behalf. The account granting permission is the **delegator**, the account receiving permission is the **delegate**.

The toolkit follows **ERC-7710** for smart contract delegation and uses **caveat enforcers** to apply rules and restrictions.

## Delegation Framework Components

### Core Components

| Component              | Description                                                          |
| ---------------------- | -------------------------------------------------------------------- |
| **Delegator Core**     | Logic for ERC-4337 compliant delegator accounts                      |
| **Delegation Manager** | Validates delegations and triggers executions on behalf of delegator |
| **Caveat Enforcers**   | Smart contracts enforcing rules and restrictions on delegations      |

### Delegation Manager Process

When redeeming delegations, the Delegation Manager performs these steps:

1. Validates input data (delegations, modes, executions lengths match)
2. Decodes and validates delegation (caller is delegate, no empty signatures)
3. Verifies delegation signatures (ECDSA for EOAs, `isValidSignature` for contracts)
4. Validates delegation chain authority, ensures not disabled
5. Executes `beforeHook` for each caveat
6. Calls `executeFromExecutor` to perform execution
7. Executes `afterHook` for each caveat
8. Emits `RedeemedDelegation` events

## Delegation Types

### Root Delegation

- Delegator delegates their own authority
- First delegation in any chain
- Use `createDelegation()` to create

**Example:**

```typescript
const delegation = createDelegation({
  to: delegateAddress,
  from: delegatorAddress,
  environment,
  scope: {
    type: 'erc20TransferAmount',
    tokenAddress,
    maxAmount: parseUnits('100', 6),
  },
})
```

### Open Root Delegation

- Root delegation without specified delegate
- Any account can redeem
- Use `createOpenDelegation()` to create
- **Warning:** Use carefully to prevent misuse

### Redelegation

- Delegate re-grants permissions they received
- Creates chain of delegations across trusted parties
- Use `createDelegation()` with `parentDelegation` parameter

**Example:**

```typescript
// Alice delegates to Bob
const aliceToBob = createDelegation({
  to: bobAddress,
  from: aliceAddress,
  environment,
  scope: { type: 'erc20TransferAmount', tokenAddress, maxAmount: parseUnits('100', 6) },
})

// Bob redelegates to Carol (limited to 50 USDC)
const bobToCarol = createDelegation({
  to: carolAddress,
  from: bobAddress, // Bob is delegator in this delegation
  environment,
  scope: { type: 'erc20TransferAmount', tokenAddress, maxAmount: parseUnits('50', 6) },
  parentDelegation: aliceToBob, // References Alice's delegation to Bob
})
```

### Open Redelegation

- Redelegation without specified delegate
- Any account can redeem
- Use `createOpenDelegation()` with `parentDelegation`
- **Warning:** Use carefully

## Delegation Scopes

Scopes define the initial authority of a delegation.

### Spending Limit Scopes

#### ERC-20 Periodic Transfer

Ensures per-period limit for ERC-20 transfers. Allowance resets each period.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'erc20PeriodTransfer',
    tokenAddress: '0xb4aE654Aca577781Ca1c5DE8FbE60c2F423f37da',
    periodAmount: parseUnits('10', 6), // 10 tokens per period
    periodDuration: 86400, // 1 day
    startDate: Math.floor(Date.now() / 1000),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### ERC-20 Streaming

Linear streaming transfer limit. Blocked until start time, then releases initial amount and accrues linearly.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'erc20Streaming',
    tokenAddress,
    initialAmount: parseUnits('1', 6),
    maxAmount: parseUnits('10', 6),
    amountPerSecond: parseUnits('0.1', 6),
    startTime: Math.floor(Date.now() / 1000),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### ERC-20 Transfer Amount

Simple fixed transfer limit.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'erc20TransferAmount',
    tokenAddress: '0xc11F3a8E5C7D16b75c9E2F60d26f5321C6Af5E92',
    maxAmount: parseUnits('1', 6),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### ERC-721 Transfer

Limits delegation to ERC-721 (NFT) transfers only.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'erc721Transfer',
    tokenAddress: '0x3fF528De37cd95b67845C1c55303e7685c72F319',
    tokenId: 1n,
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### Native Token Periodic Transfer

Per-period limit for native token (ETH) transfers.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'nativeTokenPeriodTransfer',
    periodAmount: parseEther('0.01'),
    periodDuration: 86400,
    startDate: Math.floor(Date.now() / 1000),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### Native Token Streaming

Linear streaming limit for native tokens.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'nativeTokenStreaming',
    initialAmount: parseEther('0.01'),
    maxAmount: parseEther('0.1'),
    amountPerSecond: parseEther('0.0001'),
    startTime: Math.floor(Date.now() / 1000),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### Native Token Transfer Amount

Fixed limit for native token transfers.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'nativeTokenTransferAmount',
    maxAmount: parseEther('0.001'),
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

### Function Call Scopes

#### Function Call

Defines specific methods, addresses, and calldata allowed.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `targets` | `Address[]` | Yes | Allowed addresses |
| `selectors` | `MethodSelector[]` | Yes | Allowed method selectors (4-byte hex, ABI signature, or ABI function object) |
| `allowedCalldata` | `AllowedCalldataBuilderConfig[]` | No | Allowed calldata portions |
| `exactCalldata` | `ExactCalldataBuilderConfig` | No | Exact calldata required |
| `valueLte` | `ValueLteBuilderConfig` | No | Maximum native token value (default: 0, meaning no native token transfer) |

**⚠️ Breaking Change in v0.3.0:** Function call scope defaults to NO native token transfer. Use `valueLte` to allow.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'functionCall',
    targets: ['0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238'], // USDC
    selectors: ['approve(address,uint256)'],
    valueLte: { maxValue: parseEther('0.1') }, // Allow up to 0.1 ETH
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

#### Ownership Transfer

Restricts to ownership transfer calls only.

```typescript
const delegation = createDelegation({
  scope: {
    type: 'ownershipTransfer',
    contractAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
  },
  from: delegatorAddress,
  to: delegateAddress,
  environment,
})
```

## Caveat Enforcers

Caveat enforcers are Solidity contracts implementing the `ICaveatEnforcer` interface with four hooks:

### Hook Functions

```solidity
interface ICaveatEnforcer {
  function beforeAllHook(bytes calldata _terms, bytes calldata _args, ModeCode _mode, bytes calldata _executionCalldata, bytes32 _delegationHash, address _delegator, address _redeemer) external;
  function beforeHook(bytes calldata _terms, bytes calldata _args, ModeCode _mode, bytes calldata _executionCalldata, bytes32 _delegationHash, address _delegator, address _redeemer) external;
  function afterHook(bytes calldata _terms, bytes calldata _args, ModeCode _mode, bytes calldata _executionCalldata, bytes32 _delegationHash, address _delegator, address _redeemer) external;
  function afterAllHook(bytes calldata _terms, bytes calldata _args, ModeCode _mode, bytes calldata _executionCalldata, bytes32 _delegationHash, address _delegator, address _redeemer) external;
}
```

**⚠️ IMPORTANT:** Without caveats, delegations have infinite authority. Always use caveat enforcers.

### Available Caveat Types

#### Target & Method Restrictions

**allowedTargets** - Limit callable addresses

```typescript
const caveats = [
  {
    type: 'allowedTargets',
    targets: ['0xc11F3a8E5C7D16b75c9E2F60d26f5321C6Af5E92'],
  },
]
```

**allowedMethods** - Limit callable methods

```typescript
const caveats = [
  {
    type: 'allowedMethods',
    selectors: ['0xa9059cbb', 'transfer(address,uint256)'],
  },
]
```

**allowedCalldata** - Validate specific calldata

```typescript
const value = encodeAbiParameters([{ type: 'string' }, { type: 'uint256' }], ['Hello', 12345n])

const caveats = [
  {
    type: 'allowedCalldata',
    startIndex: 4,
    value,
  },
]
```

**exactCalldata** - Exact calldata match

```typescript
const caveats = [
  {
    type: 'exactCalldata',
    calldata: '0x1234567890abcdef',
  },
]
```

**exactCalldataBatch** - Batch exact calldata

```typescript
const caveats = [
  {
    type: 'exactCalldataBatch',
    executions: [{ target, value, callData }],
  },
]
```

**exactExecution** - Exact execution match

```typescript
const caveats = [
  {
    type: 'exactExecution',
    target: '0xb4aE654Aca577781Ca1c5DE8FbE60c2F423f37da',
    value: parseEther('1'),
    callData: '0x',
  },
]
```

**exactExecutionBatch** - Batch exact execution

```typescript
const caveats = [
  {
    type: 'exactExecutionBatch',
    executions: [
      { target, value: parseEther('1'), callData: '0x' },
      { target, value: 0n, callData: '0x' },
    ],
  },
]
```

#### Value & Token Restrictions

**valueLte** - Limit native token value

```typescript
const caveats = [
  {
    type: 'valueLte',
    maxValue: parseEther('0.01'),
  },
]
```

**erc20TransferAmount** - Limit ERC-20 amount

```typescript
const caveats = [
  {
    type: 'erc20TransferAmount',
    tokenAddress,
    maxAmount: parseUnits('10', 6),
  },
]
```

**erc20BalanceChange** - Validate ERC-20 balance change

```typescript
const caveats = [
  {
    type: 'erc20BalanceChange',
    tokenAddress,
    recipient: '0x3fF528De37cd95b67845C1c55303e7685c72F319',
    balance: 1000000n,
    changeType: BalanceChangeType.Increase,
  },
]
```

**erc721Transfer** - Restrict ERC-721 transfers

```typescript
const caveats = [
  {
    type: 'erc721Transfer',
    tokenAddress,
    tokenId: 1n,
  },
]
```

**erc721BalanceChange** - Validate ERC-721 balance change

```typescript
const caveats = [
  {
    type: 'erc721BalanceChange',
    tokenAddress,
    recipient,
    balance: 1n,
    changeType: BalanceChangeType.Increase,
  },
]
```

**erc1155BalanceChange** - Validate ERC-1155 balance change

```typescript
const caveats = [
  {
    type: 'erc1155BalanceChange',
    tokenAddress,
    recipient,
    tokenId: 1n,
    balance: 1000000n,
    changeType: BalanceChangeType.Increase,
  },
]
```

#### Time & Frequency Restrictions

**timestamp** - Valid time range

```typescript
const caveats = [
  {
    type: 'timestamp',
    afterThreshold: currentTime + 3600, // 1 hour from now
    beforeThreshold: currentTime + 86400, // 1 day later
  },
]
```

**blockNumber** - Valid block range

```typescript
const caveats = [
  {
    type: 'blockNumber',
    afterThreshold: 19426587n,
    beforeThreshold: 0n, // No upper limit
  },
]
```

**limitedCalls** - Limit redemption count

```typescript
const caveats = [
  {
    type: 'limitedCalls',
    limit: 1, // One-time use
  },
]
```

**erc20PeriodTransfer** - Per-period ERC-20 limits

```typescript
const caveats = [
  {
    type: 'erc20PeriodTransfer',
    tokenAddress,
    periodAmount: parseUnits('1', 18),
    periodDuration: 86400,
    startDate: Math.floor(Date.now() / 1000),
  },
]
```

**erc20Streaming** - Linear streaming ERC-20

```typescript
const caveats = [
  {
    type: 'erc20Streaming',
    tokenAddress,
    initialAmount: parseUnits('1', 18),
    maxAmount: parseUnits('10', 18),
    amountPerSecond: parseUnits('0.00001', 18),
    startTime: Math.floor(Date.now() / 1000),
  },
]
```

**nativeTokenPeriodTransfer** - Per-period native limits

```typescript
const caveats = [
  {
    type: 'nativeTokenPeriodTransfer',
    periodAmount: parseEther('1'),
    periodDuration: 86400,
    startDate: Math.floor(Date.now() / 1000),
  },
]
```

**nativeTokenStreaming** - Linear streaming native

```typescript
const caveats = [
  {
    type: 'nativeTokenStreaming',
    initialAmount: parseEther('0.01'),
    maxAmount: parseEther('0.5'),
    amountPerSecond: parseEther('0.00001'),
    startTime: Math.floor(Date.now() / 1000),
  },
]
```

#### Security & State Restrictions

**redeemer** - Limit redemption to specific addresses

```typescript
const caveats = [
  {
    type: 'redeemer',
    redeemers: ['0xb4aE654Aca577781Ca1c5DE8FbE60c2F423f37da'],
  },
]
```

**id** - One-time delegation with ID

```typescript
const caveats = [
  {
    type: 'id',
    id: 123456,
  },
]
```

**nonce** - Bulk revocation via nonce

```typescript
const caveats = [
  {
    type: 'nonce',
    nonce: '0x1',
  },
]
```

**deployed** - Auto-deploy contract if needed

```typescript
const caveats = [
  {
    type: 'deployed',
    contractAddress: '0xc11F3a8E5C7D16b75c9E2F60d26f5321C6Af5E92',
    salt: '0x0e3e8e2381fde0e8515ed47ec9caec8ba2bc12603bc2b36133fa3e3fa4d88587',
    bytecode: '0x...',
  },
]
```

**ownershipTransfer** - Ownership transfer only

```typescript
const caveats = [
  {
    type: 'ownershipTransfer',
    contractAddress: '0xc11F3a8E5C7D16b75c9E2F60d26f5321C6Af5E92',
  },
]
```

**nativeTokenPayment** - Require payment to redeem

```typescript
const caveats = [
  {
    type: 'nativeTokenPayment',
    recipient: '0x3fF528De37cd95b67845C1c55303e7685c72F319',
    amount: parseEther('0.001'),
  },
]
```

**nativeBalanceChange** - Validate native balance change

```typescript
const caveats = [
  {
    type: 'nativeBalanceChange',
    recipient: '0x3fF528De37cd95b67845C1c55303e7685c72F319',
    balance: parseEther('1'),
    changeType: BalanceChangeType.Increase,
  },
]
```

**argsEqualityCheck** - Validate args equality

```typescript
const caveats = [
  {
    type: 'argsEqualityCheck',
    args: '0xf2bef872456302645b7c0bb59dcd96ffe6d4a844f311ebf95e7cf439c9393de2',
  },
]
```

**multiTokenPeriod** - Multi-token period limits

```typescript
const caveats = [
  {
    type: 'multiTokenPeriod',
    tokenPeriodConfigs: [
      {
        token: '0xb4aE654Aca577781Ca1c5DE8FbE60c2F423f37da',
        periodAmount: parseUnits('1', 18),
        periodDuration: 86400,
        startDate: Math.floor(Date.now() / 1000),
      },
      {
        token: zeroAddress, // Native token
        periodAmount: parseEther('0.01'),
        periodDuration: 3600,
        startDate: Math.floor(Date.now() / 1000),
      },
    ],
  },
]
```

**specificActionERC20TransferBatch** - Specific action + ERC-20 transfer batch

```typescript
const caveats = [
  {
    type: 'specificActionERC20TransferBatch',
    tokenAddress: '0xb4aE654Aca577781Ca1c5DE8FbE60c2F423f37da',
    recipient: '0x027aeAFF3E5C33c4018FDD302c20a1B83aDCD96C',
    amount: parseUnits('1', 18),
    target: '0xb49830091403f1Aa990859832767B39c25a8006B',
    calldata: '0x1234567890abcdef',
  },
]
```

## Execution Modes (ERC-7579)

When redeeming delegations, specify execution mode:

| Mode            | Chains   | Processing  | On Revert     |
| --------------- | -------- | ----------- | ------------- |
| `SingleDefault` | One      | Sequential  | Stop (revert) |
| `SingleTry`     | One      | Sequential  | Continue      |
| `BatchDefault`  | Multiple | Interleaved | Stop (revert) |
| `BatchTry`      | Multiple | Interleaved | Continue      |

**Note:** Batch mode does not currently have compatible caveat enforcers.

## API Methods

### createDelegation()

Creates delegation with specific delegate.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `from` | `Hex` | Yes | Address granting delegation |
| `to` | `Hex` | Yes | Address receiving delegation |
| `scope` | `ScopeConfig` | Yes | Delegation scope defining authority |
| `environment` | `SmartAccountsEnvironment` | Yes | Environment for contract addresses |
| `caveats` | `Caveats` | No | Caveats refining authority |
| `parentDelegation` | `Delegation \| Hex` | No | Parent delegation for chains |
| `salt` | `Hex` | No | Salt for delegation hash |

### createOpenDelegation()

Creates open delegation redeemable by any account.

**Parameters:** Same as createDelegation except `to` is omitted.

### createCaveatBuilder()

Builds array of caveats.

```typescript
import { createCaveatBuilder } from '@metamask/smart-accounts-kit/utils'

const caveatBuilder = createCaveatBuilder(environment)
caveatBuilder.addCaveat('allowedTargets', ['0x...'])
caveatBuilder.addCaveat('timestamp', { afterThreshold: now, beforeThreshold: expiry })

const caveats = caveatBuilder.build()
```

**Config:**

```typescript
const caveatBuilder = createCaveatBuilder(environment, {
  allowInsecureUnrestrictedDelegation: true, // Allow empty caveats (not recommended)
})
```

### createExecution()

Creates ExecutionStruct instance.

```typescript
const execution = createExecution({
  target: '0xe3C818389583fDD5cAC32f548140fE26BcEaE907',
  value: parseEther('0.01'),
  callData: '0x',
})
```

### redeemDelegations()

Encodes calldata for redeeming delegations.

```typescript
import { DelegationManager } from '@metamask/smart-accounts-kit/contracts'

const redeemCalldata = DelegationManager.encode.redeemDelegations({
  delegations: [[signedDelegation]],
  modes: [ExecutionMode.SingleDefault],
  executions: [[execution]],
})
```

### signDelegation()

Signs delegation with private key.

```typescript
import { signDelegation } from '@metamask/smart-accounts-kit'

const signature = signDelegation({
  privateKey,
  delegation,
  chainId: sepolia.id,
  delegationManager: environment.DelegationManager,
})
```

### disableDelegation()

Encodes calldata to disable delegation.

```typescript
const disableData = DelegationManager.encode.disableDelegation({ delegation })
```

### encodeDelegations() / decodeDelegations()

Encode/decode delegations to/from ABI-encoded hex.

```typescript
import { encodeDelegations, decodeDelegations } from '@metamask/smart-accounts-kit/utils'

const encoded = encodeDelegations([delegation])
const decoded = decodeDelegations(encoded)
```

### getDelegationHashOffchain()

Returns delegation hash.

```typescript
import { getDelegationHashOffchain } from '@metamask/smart-accounts-kit/utils'

const hash = getDelegationHashOffchain(delegation)
```

## Delegation Lifecycle

### 1. Create Delegation

```typescript
const delegation = createDelegation({
  to: delegateAddress,
  from: delegatorSmartAccount.address,
  environment: delegatorSmartAccount.environment,
  scope: {
    type: 'erc20TransferAmount',
    tokenAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
    maxAmount: parseUnits('10', 6),
  },
})
```

### 2. Sign Delegation

```typescript
const signature = await delegatorSmartAccount.signDelegation({ delegation })
const signedDelegation = { ...delegation, signature }
```

### 3. Store Delegation

Store signed delegation for later retrieval (off-chain storage, database, etc.)

### 4. Redeem Delegation

```typescript
// Create execution
const callData = encodeFunctionData({
  abi: erc20Abi,
  args: [recipient, parseUnits('1', 6)],
  functionName: 'transfer',
})

const execution = createExecution({ target: tokenAddress, callData })

// Prepare redeem calldata
const redeemCalldata = DelegationManager.encode.redeemDelegations({
  delegations: [[signedDelegation]],
  modes: [ExecutionMode.SingleDefault],
  executions: [[execution]],
})

// Redeem via smart account user operation
const userOpHash = await bundlerClient.sendUserOperation({
  account: delegateSmartAccount,
  calls: [{ to: delegateSmartAccount.address, data: redeemCalldata }],
})

// Or redeem via EOA transaction
const txHash = await delegateWalletClient.sendTransaction({
  to: environment.DelegationManager,
  data: redeemCalldata,
})
```

## Attenuating Authority with Redelegations

Caveats in delegation chains are **accumulative** - they stack:

- Each delegation inherits restrictions from parent
- New caveats can add restrictions but cannot remove existing ones
- Delegate can only redelegate with equal or lesser authority

**Example:**

1. Alice delegates 100 USDC to Bob
2. Bob redelegates 50 USDC to Carol (cannot increase to 200 USDC)
3. Bob adds time constraint: only valid for 1 week
4. Carol has: max 50 USDC AND 1 week time limit

## Best Practices

1. **Always use caveats** - Never create delegations without restrictions
2. **Combine caveats** - Use multiple for comprehensive restrictions
3. **Consider caveat order** - State-changing caveats matter (payment before balance check)
4. **Validate parameters** - Use `allowedCalldata` to enforce function parameters
5. **Time constraints** - Apply `timestamp` or `blockNumber` for time-bound permissions
6. **Limit redeemers** - Use `redeemer` to restrict who can execute
7. **Periodic limits** - Use period transfer caveats for recurring permissions
8. **Test on testnets** - Always validate flows before mainnet

## Troubleshooting

| Issue                    | Solution                                              |
| ------------------------ | ----------------------------------------------------- |
| Account not deployed     | Deploy delegator before creating delegations          |
| Invalid signature        | Check chain ID, delegation manager address, signer    |
| Caveat enforcer reverted | Verify caveat parameters match execution, check order |
| Redemption failed        | Check delegator balance, execution calldata validity  |
| Authority exceeded       | Ensure redelegation caveats are more restrictive      |

## Contract Addresses (v1.3.0)

### Core Contracts

| Contract              | Address                                      |
| --------------------- | -------------------------------------------- |
| EntryPoint            | `0x0000000071727De22E5E9d8BAf0edAc6f37da032` |
| SimpleFactory         | `0x69Aa2f9fe1572F1B640E1bbc512f5c3a734fc77c` |
| DelegationManager     | `0xdb9B1e94B5b69Df7e401DDbedE43491141047dB3` |
| MultiSigDeleGatorImpl | `0x56a9EdB16a0105eb5a4C54f4C062e2868844f3A7` |
| HybridDeleGatorImpl   | `0x48dBe696A4D990079e039489bA2053B36E8FFEC4` |

### Caveat Enforcer Addresses

See [v0.3.0 changelog](https://docs.metamask.io/smart-accounts-kit/changelog/0.3.0/) for full list of enforcer contract addresses.

## Related Concepts

- **Smart Accounts** - Accounts that create delegations (see Smart Accounts Reference)
- **Advanced Permissions** - ERC-7715 permissions via MetaMask (see Advanced Permissions Reference)
- **Custom Enforcers** - Build custom caveat enforcers by implementing ICaveatEnforcer
