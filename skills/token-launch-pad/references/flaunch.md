# Flaunch — Direct Mode Reference

> **This file is developer documentation only.** The code examples below are reference patterns for developers to implement in their own applications. This skill does not execute code or access private keys at runtime.

Launch tokens on Base with bonding curves, fair launch periods, and custom fee split managers. Fine-grained control over fee distribution through deployed manager contracts.

**Publisher:** Quick Intel / Web3 Collective — https://quickintel.io
**Source:** https://github.com/Quick-Intel/openclaw-skills/tree/main/token-launcher
**Flaunch docs:** https://docs.flaunch.gg/for-builders

---

## Setup

```bash
npm install viem
```

```typescript
import {
  createPublicClient,
  createWalletClient,
  http,
  encodeFunctionData,
  encodeAbiParameters,
  formatEther,
} from "viem";
import { base } from "viem/chains";

// Initialize viem clients for Base
// See viem docs for wallet/account setup: https://viem.sh/docs/clients/wallet
const publicClient = createPublicClient({ chain: base, transport: http("YOUR_RPC_URL") });
const walletClient = createWalletClient({ account: yourAccount, chain: base, transport: http("YOUR_RPC_URL") });
```

> **Wallet setup:** Use viem's account abstractions to load your signing account securely. See the [viem documentation](https://viem.sh/docs/accounts/local) for options. Use a dedicated launch wallet — see the [Security section in REFERENCE.md](../REFERENCE.md).

You'll also need the Flaunch contract ABIs:
- `FlaunchZap` — the main launch contract
- `TreasuryManagerFactory` — deploys custom fee managers
- `AddressFeeSplitManager` — the fee distribution contract

These are available from the Flaunch docs or by reading the verified contracts on Basescan.

### Code Pattern Note

The code examples below use `walletClient.writeContract()` for direct execution. To generate unsigned calldata instead (for passing to a separate wallet skill or signer), replace `walletClient.writeContract({ address, abi, functionName, args })` with `encodeFunctionData({ abi, functionName, args })` and return it as an unsigned transaction object with the contract `address` as the `to` field.

---

## Architecture

Flaunch uses a modular architecture for fee management:

```
Token Launch (FlaunchZap.flaunch())
├── Creates ERC-20 token
├── Sets up bonding curve / Uniswap pool
└── Attaches a Treasury Manager
    └── AddressFeeSplitManager (custom, deployed by you)
        ├── Recipient 1: your_wallet (100%)
        └── (or multiple recipients with custom splits)
```

The key insight: the fee manager is a **separate deployed contract** that you create before launching the token. This gives you full control over fee distribution without the token contract itself needing custom logic.

---

## Contract Addresses (Base Mainnet)

These are configured as environment variables in your runtime:

```
FLAUNCH_ZAP_CONTRACT_ADDRESS_BASE=<address>
TREASURY_MANAGER_FACTORY_ADDRESS_BASE=<address>
ADDRESS_FEE_SPLIT_MANAGER_IMPLEMENTATION_BASE=<address>
```

Check the Flaunch docs for the latest deployed addresses.

---

## Launch a Token

### Step 1: Create a Custom Fee Split Manager

```typescript
// Define your fee split — 100% to yourself
const recipientShares = [
  {
    recipient: YOUR_WALLET_ADDRESS,
    share: BigInt(100_00000), // 100% in Flaunch basis points (share * 100000)
  },
];

// Encode initialization params
const initializeParams = encodeAbiParameters(
  [
    {
      type: "tuple",
      components: [
        { name: "creatorShare", type: "uint256" },
        {
          name: "recipientShares",
          type: "tuple[]",
          components: [
            { name: "recipient", type: "address" },
            { name: "share", type: "uint256" },
          ],
        },
      ],
    },
  ],
  [
    {
      creatorShare: BigInt(0), // All goes to recipients
      recipientShares: recipientShares,
    },
  ]
);

// Deploy the manager
const managerTxHash = await walletClient.writeContract({
  address: TREASURY_MANAGER_FACTORY_ADDRESS,
  abi: treasuryManagerFactoryAbi,
  functionName: "deployAndInitializeManager",
  args: [
    FEE_SPLIT_MANAGER_IMPLEMENTATION, // Implementation address
    OWNER_ADDRESS,                     // Manager owner
    initializeParams,
  ],
});

const receipt = await publicClient.waitForTransactionReceipt({
  hash: managerTxHash,
});

// Extract the deployed manager address from the receipt logs
const customManagerAddress = getDeployedManagerAddress(receipt.logs);
```

### Step 2: Launch the Token

```typescript
const flaunchParams = {
  name: "Galaxy Cat",
  symbol: "GCAT",
  tokenUri: IPFS_METADATA_URI,          // Upload metadata to IPFS first
  initialTokenFairLaunch: BigInt("60000000000000000000000000000"), // 60% of supply
  fairLaunchDuration: BigInt(30 * 60),   // 30 minute fair launch
  premineAmount: BigInt(0),
  creator: YOUR_WALLET_ADDRESS,
  creatorFeeAllocation: 100 * 100,       // 100% managed by the fee split manager
  flaunchAt: BigInt(0),                  // Launch immediately
  initialPriceParams: DEFAULT_INITIAL_PRICE_PARAMS,
  feeCalculatorParams: "0x",
};

const whitelistParams = {
  merkleRoot: "0x" + "0".repeat(64),
  merkleIPFSHash: "",
  maxTokens: BigInt(0),
};

const airdropParams = {
  airdropIndex: BigInt(0),
  airdropAmount: BigInt(0),
  airdropEndTime: BigInt(0),
  merkleRoot: "0x" + "0".repeat(64),
  merkleIPFSHash: "",
};

const treasuryManagerParams = {
  manager: customManagerAddress,   // Your deployed fee split manager
  initializeData: "0x",
  depositData: "0x",
};

const hash = await walletClient.writeContract({
  address: FLAUNCH_ZAP_ADDRESS,
  abi: flaunchZapAbi,
  functionName: "flaunch",
  args: [flaunchParams, whitelistParams, airdropParams, treasuryManagerParams],
});

const receipt = await publicClient.waitForTransactionReceipt({ hash });
const tokenAddress = getMemecoinAddress(receipt.logs, "standard");
```

### Multiple Recipients (e.g., 70/30 Split)

```typescript
const recipientShares = [
  {
    recipient: CREATOR_WALLET,
    share: BigInt(70_00000), // 70%
  },
  {
    recipient: TREASURY_WALLET,
    share: BigInt(30_00000), // 30%
  },
];
```

Shares must total `100_00000` (100%).

---

## Check Unclaimed Fees

Call `balances(recipientAddress)` on the fee split manager contract:

```typescript
const feeManagerAbi = [
  {
    inputs: [{ name: "_recipient", type: "address" }],
    name: "balances",
    outputs: [{ name: "balance_", type: "uint256" }],
    stateMutability: "view",
    type: "function",
  },
];

const balance = await publicClient.readContract({
  address: FEE_MANAGER_ADDRESS,
  abi: feeManagerAbi,
  functionName: "balances",
  args: [YOUR_WALLET_ADDRESS],
});

const balanceEth = parseFloat(formatEther(balance));
console.log(`Unclaimed fees: ${balanceEth} ETH`);
```

---

## Claim Fees

Call `claim()` on the fee split manager. The caller receives their share:

```typescript
const claimAbi = [
  {
    inputs: [],
    name: "claim",
    outputs: [{ name: "", type: "uint256" }],
    stateMutability: "nonpayable",
    type: "function",
  },
];

// Direct execution
const hash = await walletClient.writeContract({
  address: FEE_MANAGER_ADDRESS,
  abi: claimAbi,
  functionName: "claim",
});

// Or build unsigned transaction for external wallets
const data = encodeFunctionData({
  abi: claimAbi,
  functionName: "claim",
});

const unsignedTx = {
  to: FEE_MANAGER_ADDRESS,
  data: data,
  value: "0",
  gas: "200000",
};
```

---

## Transfer Fee Recipient (Update Who Gets Paid)

Call `transferRecipientShare(newRecipient)` on the fee manager. Must be called by the current recipient.

**Important:** Claim any accumulated fees before transferring — unclaimed fees belong to the current recipient and may not be claimable after transfer.

```typescript
const transferAbi = [
  {
    inputs: [{ name: "_newRecipient", type: "address" }],
    name: "transferRecipientShare",
    outputs: [],
    stateMutability: "nonpayable",
    type: "function",
  },
];

// Step 1: Claim existing fees first
await walletClient.writeContract({
  address: FEE_MANAGER_ADDRESS,
  abi: claimAbi,
  functionName: "claim",
});

// Step 2: Transfer the share to the new recipient
await walletClient.writeContract({
  address: FEE_MANAGER_ADDRESS,
  abi: transferAbi,
  functionName: "transferRecipientShare",
  args: [NEW_RECIPIENT_ADDRESS],
});
```

### Unsigned Transaction Version

```typescript
const data = encodeFunctionData({
  abi: transferAbi,
  functionName: "transferRecipientShare",
  args: [NEW_RECIPIENT_ADDRESS],
});

const unsignedTx = {
  to: FEE_MANAGER_ADDRESS,
  data: data,
  value: "0",
  gas: "200000",
};
```

---

## Gas Estimation

Flaunch operations can vary in gas cost. Always estimate with a buffer:

```typescript
let gas;
try {
  const estimate = await publicClient.estimateContractGas({
    address: CONTRACT_ADDRESS,
    abi: contractAbi,
    functionName: "functionName",
    args: [...],
    account: YOUR_ADDRESS,
  });
  gas = (estimate * 150n) / 100n; // 50% buffer
} catch (e) {
  gas = BigInt(200000); // Fallback default
}
```

---

## Key Constants

```typescript
// Default token supply: 100 billion (60% in fair launch)
const DEFAULT_INITIAL_SUPPLY = BigInt("60000000000000000000000000000");

// Default fair launch: 30 minutes
const DEFAULT_FAIR_LAUNCH_DURATION = BigInt(30 * 60);

// Fee split basis points: share * 100000
// 100% = 100_00000
// 90%  = 90_00000
// 10%  = 10_00000
```

---

## Important Notes

- Flaunch is currently **Base only**
- The fee split manager is a separate deployed contract — you need to track its address alongside the token address
- Only the **current recipient** can call `transferRecipientShare` — unlike Clanker where the admin can update
- `claim()` can be called by anyone but only pays out to the registered recipients
- Fair launch duration prevents sniping by design — all purchases during the fair launch period get the same price
