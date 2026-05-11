# Advanced Permissions (ERC-7715) Reference

## Overview

Advanced Permissions (ERC-7715) enable dapps to request fine-grained permissions from MetaMask users to execute transactions on their behalf. Permissions are requested directly via the MetaMask browser extension with human-readable confirmations.

**Key Benefits:**

- Eliminates need for users to approve every transaction
- Enables transaction execution without active wallet connection
- Human-readable permission UI in MetaMask
- Users can modify permission parameters (if allowed)

**⚠️ Requirements:**

- MetaMask Flask 13.5.0+ (or later stable versions with ERC-7715 support)
- User must be upgraded to MetaMask Smart Account

## ERC-7715 Technical Overview

### Core Method: `wallet_grantPermissions`

ERC-7715 defines this JSON-RPC method for requesting wallet permissions.

**Required Parameters:**
| Parameter | Description |
|-----------|-------------|
| `signer` | Entity requesting/managing permission (wallet signer, account signer, etc.) |
| `chainId` | Chain where permission is requested |
| `expiry` | Timestamp when permission expires (seconds) |
| `permission` | Permission configuration (type-specific data) |
| `isAdjustmentAllowed` | Whether user can modify requested permission |

### Signer Types

**Account Signer** (most common example):

- Session account created solely to request/redeem permissions
- Can be smart account or EOA
- Contains no tokens (only for signing)
- Granted permissions via ERC-7710 delegation

```typescript
signer: {
  type: "account",
  data: {
    address: sessionAccount.address,
  },
}
```

### How It Works

1. Dapp requests permission via `wallet_grantPermissions`
2. MetaMask displays human-readable confirmation UI
3. User approves (optionally modifying parameters)
4. MetaMask creates ERC-7710 delegation internally
5. Session account receives permission to execute on user's behalf
6. Session account redeems permission to execute transactions

## Advanced Permissions vs Regular Delegations

| Feature                | Regular Delegations                    | Advanced Permissions                 |
| ---------------------- | -------------------------------------- | ------------------------------------ |
| Signing                | Dapp constructs and requests signature | Via MetaMask extension               |
| Human Readable         | No (dapp provides context)             | Yes (rich UI in MetaMask)            |
| Constraints            | Dapp responsibility                    | Enforced by MetaMask                 |
| User Modification      | No                                     | Yes (if `isAdjustmentAllowed: true`) |
| Smart Account Required | For delegator                          | For user (permission target)         |

**Example UI:**
ERC-20 periodic permission displays:

- Start time
- Amount per period
- Period duration
- Token information

## Supported Permission Types

### ERC-20 Token Permissions

#### ERC-20 Periodic Permission

Allows periodic transfers of ERC-20 tokens up to specified amount per period.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | `"erc20-token-periodic"` | Permission type |
| `tokenAddress` | `Address` | ERC-20 token contract |
| `periodAmount` | `bigint` | Max amount per period (wei format) |
| `periodDuration` | `number` | Period duration in seconds |
| `justification` | `string` | Human-readable description |

**Example:**

```typescript
const grantedPermissions = await walletClient.requestExecutionPermissions([
  {
    chainId: sepolia.id,
    expiry: Math.floor(Date.now() / 1000) + 604800, // 1 week
    signer: {
      type: 'account',
      data: { address: sessionAccount.address },
    },
    permission: {
      type: 'erc20-token-periodic',
      data: {
        tokenAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        periodAmount: parseUnits('10', 6), // 10 USDC
        periodDuration: 86400, // 1 day
        justification: 'Permission to transfer 10 USDC every day',
      },
    },
    isAdjustmentAllowed: true,
  },
])
```

#### ERC-20 Streaming Permission

Ensures a linear streaming transfer limit for ERC-20 tokens. Tokens accrue linearly at the configured rate, up to the maximum allowed amount.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | `"erc20-token-stream"` | Permission type |
| `tokenAddress` | `Address` | ERC-20 token contract |
| `amountPerSecond` | `bigint` | The rate at which tokens accrue per second |
| `initialAmount` | `bigint` | The initial amount that can be transferred at start time (default: 0) |
| `maxAmount` | `bigint` | The maximum total amount that can be unlocked (default: no limit) |
| `startTime` | `number` | The start timestamp in seconds (default: current time) |
| `justification` | `string` | Human-readable description |

**Example:**

```typescript
permission: {
  type: "erc20-token-stream",
  data: {
    tokenAddress: "0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238",
    amountPerSecond: parseUnits("0.0001", 6), // 0.0001 USDC per second
    justification: "Permission to stream USDC continuously",
  },
}
```

### Native Token Permissions

#### Native Token Periodic Permission

Allows periodic transfers of native token (ETH) up to specified amount per period.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | `"native-token-periodic"` | Permission type |
| `periodAmount` | `bigint` | Max amount per period (wei) |
| `periodDuration` | `number` | Period duration in seconds |
| `justification` | `string` | Human-readable description |

**Example:**

```typescript
permission: {
  type: "native-token-periodic",
  data: {
    periodAmount: parseEther("0.01"), // 0.01 ETH per period
    periodDuration: 86400, // 1 day
    justification: "Permission to transfer 0.01 ETH daily",
  },
}
```

#### Native Token Streaming Permission

Ensures a linear streaming transfer limit for native tokens (ETH). ETH accrues linearly at the configured rate, up to the maximum allowed amount.

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `type` | `"native-token-stream"` | Permission type |
| `amountPerSecond` | `bigint` | The rate at which ETH accrues per second |
| `initialAmount` | `bigint` | The initial amount that can be transferred at start time (default: 0) |
| `maxAmount` | `bigint` | The maximum total amount that can be unlocked (default: no limit) |
| `startTime` | `number` | The start timestamp in seconds (default: current time) |
| `justification` | `string` | Human-readable description |

**Example:**

```typescript
permission: {
  type: "native-token-stream",
  data: {
    amountPerSecond: parseEther("0.00001"), // 0.00001 ETH per second
    justification: "Permission to stream ETH continuously",
  },
}
```

## Advanced Permissions Lifecycle

### Step 1: Setup Wallet Client

```typescript
import { createWalletClient, custom } from 'viem'
import { erc7715ProviderActions } from '@metamask/smart-accounts-kit/actions'

const walletClient = createWalletClient({
  transport: custom(window.ethereum),
}).extend(erc7715ProviderActions())
```

### Step 2: Setup Public Client

```typescript
import { createPublicClient, http } from 'viem'
import { sepolia as chain } from 'viem/chains'

const publicClient = createPublicClient({
  chain,
  transport: http(),
})
```

### Step 3: Setup Session Account

**Smart Account:**

```typescript
import { toMetaMaskSmartAccount, Implementation } from '@metamask/smart-accounts-kit'

const sessionAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Hybrid,
  deployParams: [account.address, [], [], []],
  deploySalt: '0x',
  signer: { account },
})
```

**EOA:**

```typescript
import { privateKeyToAccount } from 'viem/accounts'

const sessionAccount = privateKeyToAccount('0x...')
```

### Step 4: Check User Smart Account Status

**For MetaMask Flask 13.9.0+:**

- Advanced Permissions support automatic upgrade
- No manual upgrade needed

**For earlier versions:**

```typescript
const addresses = await walletClient.requestAddresses()
const address = addresses[0]

const code = await publicClient.getCode({ address })

if (code) {
  const delegatorAddress = `0x${code.substring(8)}` // Remove 0xef0100 prefix
  const statelessDelegatorAddress = getSmartAccountsEnvironment(chain.id).implementations
    .EIP7702StatelessDeleGatorImpl

  const isAccountUpgraded =
    delegatorAddress.toLowerCase() === statelessDelegatorAddress.toLowerCase()

  if (!isAccountUpgraded) {
    // Prompt user to upgrade or upgrade programmatically
  }
}
```

**Why upgrade required?**

- Under the hood, ERC-7715 creates an ERC-7710 delegation
- ERC-7710 delegation requires MetaMask Smart Account

### Step 5: Request Permissions

```typescript
const currentTime = Math.floor(Date.now() / 1000)
const expiry = currentTime + 604800 // 1 week

const grantedPermissions = await walletClient.requestExecutionPermissions([
  {
    chainId: chain.id,
    expiry,
    signer: {
      type: 'account',
      data: { address: sessionAccount.address },
    },
    permission: {
      type: 'erc20-token-periodic',
      data: {
        tokenAddress: '0x1c7D4B196Cb0C7B01d743Fbc6116a902379C7238',
        periodAmount: parseUnits('10', 6),
        periodDuration: 86400,
        justification: 'Permission to transfer 10 USDC every day',
      },
    },
    isAdjustmentAllowed: true,
  },
])
```

### Step 6: Setup Client for Redemption

**Smart Account (Bundler Client):**

```typescript
import { createBundlerClient } from 'viem/account-abstraction'
import { erc7710BundlerActions } from '@metamask/smart-accounts-kit/actions'

const bundlerClient = createBundlerClient({
  client: publicClient,
  transport: http('https://your-bundler-rpc.com'),
  paymaster: true,
}).extend(erc7710BundlerActions())
```

**EOA (Wallet Client):**

```typescript
import { createWalletClient, http } from 'viem'
import { erc7710WalletActions } from '@metamask/smart-accounts-kit/actions'

const sessionAccountWalletClient = createWalletClient({
  account: sessionAccount,
  chain,
  transport: http(),
}).extend(erc7710WalletActions())
```

### Step 7: Redeem Permissions

**Extract from permission response:**

```typescript
const permissionsContext = grantedPermissions[0].context
const delegationManager = grantedPermissions[0].signerMeta.delegationManager
```

**Smart Account Redemption:**

```typescript
const calldata = encodeFunctionData({
  abi: erc20Abi,
  args: [recipient, parseUnits('1', 6)],
  functionName: 'transfer',
})

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
  maxFeePerGas: 1n,
  maxPriorityFeePerGas: 1n,
})
```

**EOA Redemption:**

```typescript
const txHash = await sessionAccountWalletClient.sendTransactionWithDelegation({
  to: tokenAddress,
  data: calldata,
  permissionsContext,
  delegationManager,
})
```

## API Methods

### Wallet Client Actions

#### requestExecutionPermissions()

Requests Advanced Permissions from MetaMask extension.

**Requirements:**

- Wallet Client must be extended with `erc7715ProviderActions()`
- User must have MetaMask Flask 13.5.0+

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `chainId` | `number` | Yes | Chain ID for permission |
| `expiry` | `number` | Yes | Expiration timestamp (seconds) |
| `permission` | `SupportedPermissionParams` | Yes | Permission configuration |
| `signer` | `SignerParam` | Yes | Account receiving permission |
| `isAdjustmentAllowed` | `boolean` | Yes | Allow user modification |
| `address` | `Address` | No | Wallet address to request from |

**Returns:**

```typescript
{
  context: Hex,              // Encoded permissions context
  signerMeta: {
    delegationManager: Address,  // Delegation Manager address
    // ... other metadata
  },
  // ... other permission details
}
```

#### sendTransactionWithDelegation()

Sends transaction to redeem delegated permissions (EOA only).

**Requirements:**

- Wallet Client must be extended with `erc7710WalletActions()`

**Additional Parameters (beyond standard sendTransaction):**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `delegationManager` | `Address` | Yes | Delegation Manager address |
| `permissionsContext` | `Hex` | Yes | Encoded calldata from permission response |

**Example:**

```typescript
const hash = await walletClient.sendTransactionWithDelegation({
  to: tokenAddress,
  value: 0n,
  data: calldata,
  permissionsContext,
  delegationManager,
})
```

### Bundler Client Actions

#### sendUserOperationWithDelegation()

Sends user operation to redeem delegated permissions (Smart Account only).

**Requirements:**

- Bundler Client must be extended with `erc7710BundlerActions()`

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `publicClient` | `PublicClient` | Yes | For reading chain state |
| `account` | `SmartAccount` | Yes | Session account |
| `calls` | `Call[]` | Yes | Calls to execute |
| `calls[].permissionsContext` | `Hex` | Yes | From permission response |
| `calls[].delegationManager` | `Address` | Yes | From permission response |

**Example:**

```typescript
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
  maxFeePerGas: 1n,
  maxPriorityFeePerGas: 1n,
})
```

## Configuration

### Extending Clients

**Wallet Client for Requesting Permissions:**

```typescript
import { erc7715ProviderActions } from '@metamask/smart-accounts-kit/actions'

const walletClient = createWalletClient({
  transport: custom(window.ethereum),
}).extend(erc7715ProviderActions())
```

**Wallet Client for EOA Redemption:**

```typescript
import { erc7710WalletActions } from '@metamask/smart-accounts-kit/actions'

const walletClient = createWalletClient({
  account: sessionAccount,
  transport: http(),
  chain,
}).extend(erc7710WalletActions())
```

**Bundler Client for Smart Account Redemption:**

```typescript
import { erc7710BundlerActions } from '@metamask/smart-accounts-kit/actions'

const bundlerClient = createBundlerClient({
  client: publicClient,
  transport: http(bundlerUrl),
  paymaster: true,
}).extend(erc7710BundlerActions())
```

## Best Practices

### Permission Design

1. **Appropriate Time Limits** - Set reasonable expiry times
2. **Justification Messages** - Clear descriptions help users understand
3. **Allow Adjustment** - Set `isAdjustmentAllowed: true` for better UX
4. **Periodic over Allowance** - Use periodic for recurring operations
5. **Test Amounts** - Use small amounts for testing

### Security

1. **Session Account Isolation** - Keep session accounts separate from user accounts
2. **No Token Storage** - Session accounts should not hold tokens
3. **Expiry Management** - Monitor and refresh expiring permissions
4. **Permission Validation** - Verify granted permissions match request
5. **Error Handling** - Handle permission denial gracefully

### Implementation

1. **Check Smart Account Status** - Verify or upgrade user before requesting
2. **Permission Caching** - Store granted permissions for reuse
3. **Batch Operations** - Group multiple calls when possible
4. **Gas Management** - Use paymasters for better UX
5. **Fallback Handling** - Provide manual transaction fallback

## Troubleshooting

| Issue                    | Solution                                                                |
| ------------------------ | ----------------------------------------------------------------------- |
| MetaMask not showing UI  | Verify Flask 13.5.0+ installed                                          |
| Permission request fails | Check user upgraded to smart account                                    |
| Redemption fails         | Verify permissionsContext and delegationManager extracted correctly     |
| Gas estimation fails     | Ensure paymaster configured or account has funds                        |
| Invalid permission type  | Use supported types (erc20-token-periodic, erc20-token-stream, native-token-periodic, native-token-stream) |
| Expired permission       | Request new permission with updated expiry                              |
| User denied permission   | Provide fallback UI for manual approval                                 |

## Integration Examples

### DeFi Dapp Integration

**Scenario:** Dapp wants to swap user tokens daily

```typescript
// 1. Setup
const walletClient = createWalletClient({
  transport: custom(window.ethereum),
}).extend(erc7715ProviderActions())

// 2. Request daily swap permission
const grantedPermissions = await walletClient.requestExecutionPermissions([{
  chainId: chain.id,
  expiry: now + 30 * 86400, // 30 days
  signer: { type: "account", data: { address: sessionAccount.address } },
  permission: {
    type: "erc20-token-periodic",
    data: {
      tokenAddress: USDC_ADDRESS,
      periodAmount: parseUnits("100", 6),
      periodDuration: 86400,
      justification: "Daily automated token swaps",
    },
  },
  isAdjustmentAllowed: true,
}])

// 3. Daily automated redemption (backend/schedule)
const userOpHash = await bundlerClient.sendUserOperationWithDelegation({
  publicClient,
  account: sessionAccount,
  calls: [{
    to: DEX_ROUTER,
    data: encodeSwapData(...),
    permissionsContext: grantedPermissions[0].context,
    delegationManager: grantedPermissions[0].signerMeta.delegationManager,
  }],
})
```

### Gaming Dapp Integration

**Scenario:** Game needs to make micro-transactions for user

```typescript
// Request small periodic native token allowance
const grantedPermissions = await walletClient.requestExecutionPermissions([
  {
    chainId: chain.id,
    expiry: now + 7 * 86400, // 1 week
    signer: { type: 'account', data: { address: sessionAccount.address } },
    permission: {
      type: 'native-token-periodic',
      data: {
        periodAmount: parseEther('0.001'), // Small amount
        periodDuration: 3600, // Hourly
        justification: 'In-game purchases and fees',
      },
    },
    isAdjustmentAllowed: true,
  },
])
```

## Resources

- **ERC-7715 Spec:** https://eips.ethereum.org/EIPS/eip-7715
- **ERC-7710 Spec:** https://eips.ethereum.org/EIPS/eip-7710
- **MetaMask Flask:** Required for Advanced Permissions
- **Smart Accounts Kit:** `@metamask/smart-accounts-kit`

## Related Concepts

- **Smart Accounts** - User must be upgraded to smart account
- **Delegations** - Underlying mechanism (ERC-7710)
- **Caveat Enforcers** - Enforce permission constraints
