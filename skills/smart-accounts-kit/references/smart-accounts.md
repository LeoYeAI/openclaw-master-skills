# Smart Accounts Reference

## Overview

MetaMask Smart Accounts are ERC-4337 compliant smart contract accounts supporting programmable behavior, multi-signature approvals, automated transaction batching, and custom security policies. Unlike traditional wallets, they use smart contracts to govern account logic.

## Account Abstraction (ERC-4337)

### Core Concepts

| Concept                  | Description                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| **User Operation**       | Package of instructions signed by user, specifying executions for the smart account                    |
| **Bundler**              | Service that collects user operations, packages them into a single transaction, and submits to network |
| **Entry Point Contract** | Validates and processes bundled user operations                                                        |
| **Paymasters**           | Entities that handle gas fee payments on behalf of users                                               |

### Smart Account Flow

1. **Account Setup** - Deploy smart contract with ownership/security settings
2. **User Operation Creation** - Create and sign operation with necessary details
3. **Bundlers and Mempool** - Submit to special mempool where bundlers package operations
4. **Validation and Execution** - Entry point contract validates and executes operations

## Implementation Types

### 1. Hybrid Smart Account

**Reference:** `Implementation.Hybrid`

Flexible implementation supporting both EOA owner and any number of passkey (WebAuthn/P256) signers.

**Deploy Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `owner` | `Hex` | Owner's account address (can be zero address) |
| `p256KeyIds` | `Hex[]` | Array of key identifiers for passkey signers |
| `p256XValues` | `bigint[]` | Array of public key x-values for passkey signers |
| `p256YValues` | `bigint[]` | Array of public key y-values for passkey signers |

**Signers Supported:**

- Viem Account (private key)
- Viem Wallet Client
- WebAuthnAccount (passkey) - requires Ox SDK

**Example - Account Signer:**

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

**Example - Wallet Client Signer:**

```typescript
const addresses = await walletClient.getAddresses()
const owner = addresses[0]

const smartAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Hybrid,
  deployParams: [owner, [], [], []],
  deploySalt: '0x',
  signer: { walletClient },
})
```

**Example - Passkey Signer:**

```typescript
import { toWebAuthnAccount } from 'viem/account-abstraction'
import { Address, PublicKey } from 'ox'
import { toHex } from 'viem'

// After creating WebAuthn credential
const credential = await createWebAuthnCredential({ name: 'MetaMask smart account' })
const webAuthnAccount = toWebAuthnAccount({ credential })

// Deserialize compressed public key
const publicKey = PublicKey.fromHex(credential.publicKey)
const owner = Address.fromPublicKey(publicKey)

const smartAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Hybrid,
  deployParams: [owner, [toHex(credential.id)], [publicKey.x], [publicKey.y]],
  deploySalt: '0x',
  signer: { webAuthnAccount, keyId: toHex(credential.id) },
})
```

### 2. Multisig Smart Account

**Reference:** `Implementation.MultiSig`

Supports multiple signers with configurable threshold. Valid signature requires signatures from at least threshold signers.

**Deploy Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `signers` | `Hex[]` | Array of EOA signer addresses |
| `threshold` | `bigint` | Number of signers required for valid signature |

**Signers Supported:**

- Multiple Viem Accounts
- Multiple Viem Wallet Clients
- Combination of both

**Example:**

```typescript
const owners = [account1.address, account2.address]
const signer = [{ account: account1 }, { walletClient: walletClient2 }]
const threshold = 2n

const smartAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.MultiSig,
  deployParams: [owners, threshold],
  deploySalt: '0x',
  signer,
})
```

**Note:** Number of signers in signatories must be at least equal to threshold.

### 3. Stateless 7702 Smart Account

**Reference:** `Implementation.Stateless7702`

EOA upgraded to support smart account functionality via EIP-7702. Enables EOAs to perform smart account operations including delegations.

**Note:** Does not handle upgrade process - requires EIP-7702 upgrade first.

**Parameters:**
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `address` | `Address` | Yes | Address of the upgraded EOA |

**Signers Supported:**

- Viem Account
- Viem Wallet Client

**Example - Account Signer:**

```typescript
const smartAccount = await toMetaMaskSmartAccount({
  client: publicClient,
  implementation: Implementation.Stateless7702,
  address: account.address, // Address of upgraded EOA
  signer: { account },
})
```

## API Methods

### toMetaMaskSmartAccount()

Creates a MetaMaskSmartAccount instance.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `client` | `Client` | Yes | Viem Client to retrieve smart account data |
| `implementation` | `TImplementation` | Yes | Implementation type (Hybrid, MultiSig, Stateless7702) |
| `signer` | `SignerConfigByImplementation<TImplementation>` | Yes | Signers (Account, WalletClient, or WebAuthnAccount) |
| `environment` | `SmartAccountsEnvironment` | No | Environment to resolve smart contracts |
| `deployParams` | `DeployParams<TImplementation>` | Required if `address` not provided | Parameters for deployment |
| `deploySalt` | `Hex` | Required if `address` not provided | Salt for deployment |
| `address` | `Address` | Required for Stateless7702 or if deployParams/deploySalt not provided | Existing smart account address |

### aggregateSignature()

Aggregates multiple partial signatures into single combined multisig signature.

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `signatures` | `PartialSignature[]` | Collection of partial signatures to merge |

**Example:**

```typescript
import { aggregateSignature } from '@metamask/smart-accounts-kit'

const aggregatedSignature = aggregateSignature({
  signatures: [
    { signer: aliceAccount.address, signature: aliceSignature, type: 'ECDSA' },
    { signer: bobAccount.address, signature: bobSignature, type: 'ECDSA' },
  ],
})
```

### encodeCalls()

Encodes calls for execution by smart account.

- Single call directly to smart account → returns call data directly
- Multiple calls or calls to other addresses → creates executions for `execute` function
- Execution mode: `SingleDefault` for single call, `BatchDefault` for multiple

**Parameters:**
| Name | Type | Description |
|------|------|-------------|
| `calls` | `Call[]` | List of calls to encode |

### getFactoryArgs()

Returns factory address and factory data for deploying smart account.

```typescript
const { factory, factoryData } = await smartAccount.getFactoryArgs()
```

### getNonce()

Returns nonce for smart account.

```typescript
const nonce = await smartAccount.getNonce()
```

### signDelegation()

Signs delegation and returns signature.

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| `delegation` | `Omit<Delegation, "signature">` | Yes | Unsigned delegation object |
| `chainId` | `number` | No | Chain ID where Delegation Manager is deployed |

**Example:**

```typescript
const signature = await smartAccount.signDelegation({ delegation })
```

### signMessage()

Generates EIP-191 signature using smart account signer.

**Parameters:** See Viem signMessage parameters

**Example:**

```typescript
const signature = await smartAccount.signMessage({ message: 'hello world' })
```

### signTypedData()

Generates EIP-712 signature using smart account signer.

**Parameters:** See Viem signTypedData parameters

**Example:**

```typescript
const signature = await smartAccount.signTypedData({
  domain,
  types,
  primaryType: "Mail",
  message: { ... },
})
```

### signUserOperation()

Signs user operation with smart account signer.

**Parameters:** See Viem signUserOperation parameters

**Example:**

```typescript
const userOpSignature = await smartAccount.signUserOperation({
  callData: '0xdeadbeef',
  callGasLimit: 141653n,
  maxFeePerGas: 15000000000n,
  maxPriorityFeePerGas: 2000000000n,
  nonce: 0n,
  preVerificationGas: 53438n,
  sender: '0xE911628bF8428C23f179a07b081325cAe376DE1f',
  verificationGasLimit: 259350n,
  signature: '0x',
})
```

## Configuration

### Bundler & Paymaster Setup

```typescript
import { createBundlerClient, createPaymasterClient } from 'viem/account-abstraction'
import { http } from 'viem'

const paymasterClient = createPaymasterClient({
  transport: http('https://your-paymaster-url.com'),
})

const bundlerClient = createBundlerClient({
  transport: http('https://your-bundler-url.com'),
  paymaster: paymasterClient,
  chain,
})
```

**Note:** Paymaster is optional, but without it, smart contract account must have funds to pay gas.

### Environment

**SmartAccountsEnvironment** defines contract addresses for interacting with Delegation Framework.

**Auto-resolve from smart account:**

```typescript
const environment: SmartAccountsEnvironment = smartAccount.environment
```

**Manual resolve:**

```typescript
import { getSmartAccountsEnvironment } from '@metamask/smart-accounts-kit'
const environment = getSmartAccountsEnvironment(chain.id)
```

**Deploy custom environment:**

```typescript
import { deploySmartAccountsEnvironment } from '@metamask/smart-accounts-kit/utils'

const environment = await deploySmartAccountsEnvironment(walletClient, publicClient, chain)
```

**Override deployed environment:**

```typescript
import { overrideDeployedEnvironment } from '@metamask/smart-accounts-kit/utils'

overrideDeployedEnvironment(chain.id, '1.3.0', environment)
```

## Deployment

**Deploy Smart Account:**

```typescript
const userOpHash = await bundlerClient.sendUserOperation({
  account: smartAccount,
  calls: [{ to: smartAccount.address, value: 0n, data: '0x' }],
})
```

**Important:** Account must be deployed before creating delegations.

## Signer Guides

### EOA Wallets

- Use `privateKeyToAccount` from viem/accounts
- Or use Wallet Client with custom transport

### Passkeys (WebAuthn)

- Install Ox SDK
- Use `createWebAuthnCredential` and `toWebAuthnAccount`
- Convert public key to address using Ox utilities

### Embedded Wallets (Privy, Dynamic)

- Follow wallet provider documentation
- Use exported accounts with smart account kit

## Best Practices

1. **Always deploy before delegating** - Undeployed accounts cannot redeem delegations
2. **Choose appropriate implementation** - Hybrid for flexibility, Multisig for security, 7702 for EOA upgrades
3. **Secure signers** - Protect private keys and passkey credentials
4. **Test on testnets** - Validate flows before mainnet deployment
5. **Monitor nonce** - Track account state for operation ordering
6. **Gas management** - Use paymasters or ensure account has sufficient funds

## Troubleshooting

| Issue                | Solution                                                       |
| -------------------- | -------------------------------------------------------------- |
| Account not deployed | Deploy via `sendUserOperation` before creating delegations     |
| Invalid signature    | Check chain ID, delegation manager address, signer permissions |
| Threshold not met    | Ensure enough signers provided for multisig                    |
| Passkey not working  | Verify Ox SDK installed, credential properly created           |
| 7702 not functioning | Confirm EOA upgraded via EIP-7702 first                        |

## Related Concepts

- **Delegator Accounts** - Smart accounts that create delegations (see Delegations Reference)
- **Advanced Permissions** - ERC-7715 permissions via MetaMask extension (see Advanced Permissions Reference)
- **Caveat Enforcers** - Smart contracts enforcing delegation rules (see Caveats Reference in Delegations)
