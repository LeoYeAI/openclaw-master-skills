---
name: ditto-workflow
description: Creates, configures, and deploys on-chain automation workflows using the Ditto Network SDK. Use when the user asks to "create a workflow", "automate on-chain", "schedule transactions", "deploy a workflow", "set up recurring transfers", "swap tokens on a schedule", "automate DeFi", "create a cron job on-chain", "trigger on event", or mentions "Ditto Network". Handles workflow building, IPFS upload, on-chain registration, simulation, and cancellation. Do NOT use for general smart contract development unrelated to Ditto workflows.
license: MIT
metadata:
  author: Ditto Network
  version: 1.0.0
  category: web3-automation
  tags: [blockchain, defi, automation, workflows, smart-accounts]
---

# Ditto Workflow SDK Skill

Build and deploy declarative on-chain automation workflows using `@ditto/workflow-sdk`. Workflows define triggers (cron, event, onchain state) and jobs (batched contract calls) that execute via ZeroDev smart accounts with session keys.

**SDK source:** [github.com/dittonetwork/ditto-workflow-sdk](https://github.com/dittonetwork/ditto-workflow-sdk) (branch: `skill-integration`)

## Architecture: Owner vs Executor

Understanding these two roles is critical:

- **Owner** (the client/user): Holds a private key, creates and signs workflows. This is the only key the user provides.
- **Executor** (Ditto Network): A decentralized network of operators that runs workflows. The client only needs the executor's **public address**, never its private key.

`submitWorkflow` takes `executorAddress` (a public `0x...` address) — NOT a private key. The session key system grants scoped permissions to this address so the network can execute on behalf of the owner's smart account.

## Critical: Before You Start

BEFORE writing any workflow code, verify the project setup:

1. Check that `@ditto/workflow-sdk` is installed: look for it in `package.json`
2. Check that a `.env` file exists with required keys (see Environment Setup below)
3. If the SDK is not installed, run: `npm install @ditto/workflow-sdk`

## Environment Setup

The `.env` file MUST contain:

```
PRIVATE_KEY=0x...          # Owner's private key (the user's wallet — used to sign and deploy)
IPFS_SERVICE_URL=https://ipfs-service.dittonetwork.io
```

Optional (only needed for cancellation):
```
WORKFLOW_CONTRACT_ADDRESS=0x... # DittoWFRegistry address
```

The executor address is embedded in the SDK — use `getDittoExecutorAddress()` from `@ditto/workflow-sdk`. Do NOT ask the user for an executor address or private key.

CRITICAL:
- Never ask the user for an executor private key or address. The SDK provides the executor address via `getDittoExecutorAddress()`.
- Never hardcode the owner's private key in source files. Always load from `.env` via `dotenv`.

## Instructions

### Step 1: Gather Requirements

Ask the user for:
- **What action?** (transfer ETH, swap tokens, call a contract function)
- **On which chain?** (see Supported Chains below)
- **When/how often?** (cron schedule, on event, or when a condition is met)
- **How many times?** (execution limit)
- **Target contract address and function signature** (if calling a contract)

If the user is vague, suggest a concrete workflow and confirm before proceeding.

### Step 2: Write the Workflow Script

Create a TypeScript file that:
1. Loads environment variables with `dotenv`
2. Creates the owner account with `privateKeyToAccount`
3. Builds the workflow using `WorkflowBuilder` and `JobBuilder`
4. Submits with `submitWorkflow`, passing the executor's public address

**Key pattern:** `WorkflowBuilder.create()` takes an `Account` (address only, no signing capability). Use `addressToEmptyAccount(owner.address)` for this. The actual `Signer` (full private key account from `privateKeyToAccount`) is passed separately to `submitWorkflow` for signing session keys and transactions.

Minimal template:

```typescript
import {
  WorkflowBuilder, JobBuilder, ChainId,
  submitWorkflow, IpfsStorage, getDittoExecutorAddress
} from '@ditto/workflow-sdk';
import { privateKeyToAccount } from 'viem/accounts';
import { addressToEmptyAccount } from '@zerodev/sdk';
import * as dotenv from 'dotenv';

dotenv.config();

async function main() {
  // Owner: full Signer (signs the workflow and session keys)
  const owner = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);

  // Executor address is provided by the SDK — no user configuration needed
  const executorAddress = getDittoExecutorAddress();

  const storage = new IpfsStorage(process.env.IPFS_SERVICE_URL!);

  // WorkflowBuilder gets Account (address only), not Signer
  const workflow = WorkflowBuilder.create(addressToEmptyAccount(owner.address))
    .addCronTrigger('0 */6 * * *')  // Every 6 hours
    .setCount(10)                    // Max 10 executions
    .setValidUntil(Date.now() + 30 * 24 * 60 * 60 * 1000) // 30 days
    .addJob(
      JobBuilder.create('my-job')
        .setChainId(ChainId.BASE_SEPOLIA)
        .addStep({
          target: '0xRecipientAddress',
          abi: '',           // Empty ABI = raw ETH transfer
          args: [],
          value: BigInt(1e15) // 0.001 ETH in wei
        })
        .build()
    )
    .build();

  const { ipfsHash, userOpHashes } = await submitWorkflow(
    workflow,
    executorAddress,               // Public address, not a key
    storage,
    owner,                         // Owner signs here
    false,                         // prodContract: false = testnet
    process.env.IPFS_SERVICE_URL!,
  );

  console.log('Deployed! IPFS hash:', ipfsHash);
  console.log('Transaction receipts:', userOpHashes);
}

main().catch(console.error);
```

### Step 3: Fund the Smart Account

IMPORTANT: The Ditto SDK uses ZeroDev smart accounts (account abstraction). The smart account address is **different from the owner's EOA wallet address**. It is deterministically derived from the owner's private key by the ZeroDev kernel.

When `submitWorkflow` runs, it registers the workflow on-chain from this smart account. The smart account must have ETH on the target chain to pay for gas.

**How to find the smart account address:** Run the workflow script — if underfunded, the error message will include the smart account address (e.g., `AA21 didn't pay prefund`). Alternatively, add this before `submitWorkflow`:

```typescript
import { signerToEcdsaValidator } from '@zerodev/ecdsa-validator';
import { createKernelAccount } from '@zerodev/sdk';
import { createPublicClient, http } from 'viem';
import { getChainConfig } from '@ditto/workflow-sdk';

const chainConfig = getChainConfig(process.env.IPFS_SERVICE_URL!);
const chain = chainConfig[ChainId.BASE_SEPOLIA]; // use your target chain
const publicClient = createPublicClient({ chain: chain.chain, transport: http(chain.rpcUrl) });
const ecdsaValidator = await signerToEcdsaValidator(publicClient, { signer: owner, entryPoint: { address: '0x0000000071727De22E5E9d8BAf0edAc6f37da032', version: '0.7' } });
const kernelAccount = await createKernelAccount(publicClient, { plugins: { sudo: ecdsaValidator }, entryPoint: { address: '0x0000000071727De22E5E9d8BAf0edAc6f37da032', version: '0.7' } });
console.log('Smart account address (fund this):', kernelAccount.address);
```

**Funding:**
- **Testnet:** Use a faucet (e.g., Sepolia faucet, Base Sepolia faucet) to send test ETH to the smart account address
- **Production:** Send real ETH (0.005–0.01 ETH is typically enough for gas) to the smart account address on the target chain

CRITICAL: Always recommend testnet first. Only proceed to production chains after the user has verified the workflow works on testnet.

### Step 4: Run and Verify

```bash
npx ts-node your-workflow-script.ts
```

Expected output: IPFS hash and transaction receipt(s). The Ditto Network will now automatically execute this workflow according to the triggers. If submission fails, check the Troubleshooting section.

## Supported Chains

**Testnet (use for development):**

| Chain | ChainId Enum | ID |
|-------|-------------|-----|
| Ethereum Sepolia | `ChainId.SEPOLIA` | 11155111 |
| Base Sepolia | `ChainId.BASE_SEPOLIA` | 84532 |

**Production:**

| Chain | ChainId Enum | ID |
|-------|-------------|-----|
| Base | `ChainId.BASE` | 8453 |
| Arbitrum | `ChainId.ARBITRUM` | 42161 |
| Polygon | `ChainId.POLYGON` | 137 |
| Optimism | `ChainId.OPTIMISM` | 10 |
| Ethereum Mainnet | `ChainId.MAINNET` | 1 |

Note: `ChainId.HOLESKY` (17000) exists in the enum but is deprecated and should not be used for new workflows.

CRITICAL: NEVER deploy to production chains (Base, Arbitrum, Polygon, Optimism, Mainnet) without explicit user confirmation. Always default to testnet. When deploying to production, set `prodContract: true` in `submitWorkflow`.

## Trigger Types

### Cron Trigger (time-based)
```typescript
.addCronTrigger('*/5 * * * *')  // Every 5 minutes (UTC)
```

### Event Trigger (log-based)
```typescript
.addEventTrigger({
  chainId: ChainId.SEPOLIA,
  contractAddress: '0xTokenAddress',
  signature: 'Transfer(address,address,uint256)',
  filter: { from: '0xSpecificSender' }  // Optional: filter indexed params
})
```

### Onchain Trigger (state-based)
```typescript
import { OnchainConditionOperator } from '@ditto/workflow-sdk';

.addOnchainTrigger({
  chainId: ChainId.BASE,
  target: '0xOracleAddress',
  abi: 'latestAnswer() view returns (int256)',
  args: [],
  onchainCondition: {
    condition: OnchainConditionOperator.GREATER_THAN,
    value: 200000000000n  // e.g., ETH > $2000 (8 decimals)
  }
})
```

Multiple triggers are AND-ed: all must be satisfied for execution.

**OnchainConditionOperator values:** `EQUAL` (0), `GREATER_THAN` (1), `LESS_THAN` (2), `GREATER_THAN_OR_EQUAL` (3), `LESS_THAN_OR_EQUAL` (4), `NOT_EQUAL` (5), `ONE_OF` (6).

## Key Operations

### Simulate (dry run)

Simulation is typically performed by the Ditto Network operators, not by clients. If you need to simulate locally for debugging, use `executeFromIpfs` with `simulate: true` — but note this requires an executor account with signing capability (for local testing only).

### Cancel a Workflow
```typescript
import { WorkflowContract } from '@ditto/workflow-sdk';

const wfContract = new WorkflowContract(process.env.WORKFLOW_CONTRACT_ADDRESS as `0x${string}`);
await wfContract.cancelWorkflow(ipfsHash, ownerAccount, chainId, process.env.IPFS_SERVICE_URL!);
```

### Check Workflow Status & Execution History

Use the Ditto Network API (base URL: `https://ipfs-service.dittonetwork.io`) to monitor deployed workflows. All endpoints use the IPFS hash returned by `submitWorkflow`. No authentication required.

**1. Workflow status** — check if the workflow is active, paused, or cancelled:
```typescript
const ipfsHash = 'QmYourWorkflowHash';
const res = await fetch(`https://ipfs-service.dittonetwork.io/workflow/status/${ipfsHash}`);
const status = await res.json();
console.log('Workflow status:', status);
```

**2. Execution logs (USE THIS to check last executions)** — returns the actual execution history with results, timestamps, and transaction details:
```typescript
const res = await fetch(`https://ipfs-service.dittonetwork.io/workflow/logs/${ipfsHash}?limit=20`);
const logs = await res.json();
console.log('Execution logs:', logs);
```
This is the primary endpoint for checking whether a workflow has run, when it ran, and whether executions succeeded or failed.

**3. Execution reports (advanced — NOT for checking execution history)** — these are internal simulation reports sent by all network operator nodes participating in the workflow. Each operator independently simulates the workflow, so you'll see multiple reports per execution (one per node). This is useful for debugging network-level issues but NOT for checking whether your workflow actually executed:
```typescript
const res = await fetch(`https://ipfs-service.dittonetwork.io/get-reports?ipfsHash=${ipfsHash}&page=1&limit=100`);
const reports = await res.json();
console.log('Node simulation reports:', reports);
```

IMPORTANT: When the user asks to "check last executions" or "see execution history", always use the **execution logs** endpoint (`/workflow/logs/`), NOT the reports endpoint. Reports show per-node simulation data, not actual execution outcomes.

### Data References (read contract state at execution time)
```typescript
import { dataRef } from '@ditto/workflow-sdk';

const ethPrice = dataRef({
  target: '0xChainlinkOracleAddress',
  abi: 'latestRoundData() returns (uint80, int256, uint256, uint256, uint80)',
  chainId: ChainId.SEPOLIA,
  resultIndex: 1,  // int256 price is the 2nd return value
});

// Use in a step arg - resolved dynamically at execution time by the network
.addStep({
  target: '0xSwapRouter',
  abi: 'swap(uint256)',
  args: [ethPrice],
})
```

## Workflow Limits

| Method | Purpose | Example |
|--------|---------|---------|
| `.setCount(n)` | Max total executions | `.setCount(100)` |
| `.setInterval(sec)` | Min seconds between runs | `.setInterval(300)` |
| `.setValidAfter(date)` | Start time (Date or ms) | `.setValidAfter(Date.now())` |
| `.setValidUntil(date)` | Expiration (Date or ms) | `.setValidUntil(Date.now() + 86400000)` |

## Step Interface

```typescript
interface Step {
  target: string;              // Contract address (0x-prefixed)
  abi: string;                 // Function signature, e.g. "transfer(address,uint256)"
                               // Empty string "" for raw ETH transfer
  args: readonly any[];        // Function arguments (can include dataRef strings)
  value?: bigint | string;     // ETH value in wei
}
```

## Key Function Signatures

### submitWorkflow
```typescript
async function submitWorkflow(
  workflow: Workflow,
  executorAddress: `0x${string}`, // Public address of the Ditto Network executor
  storage: IWorkflowStorage,
  owner: Signer,                  // Owner signs (from privateKeyToAccount)
  prodContract: boolean,          // true = mainnet registry, false = testnet
  ipfsServiceUrl: string,
  usePaymaster?: boolean,         // Default: false
  switchChain?: (chainId: number) => Promise<void>,
  accessToken?: string,
): Promise<{ ipfsHash: string; userOpHashes: UserOperationReceipt[] }>;
```

### executeFromIpfs (used by network operators, not clients)
```typescript
async function executeFromIpfs(
  ipfsHash: string,
  storage: IWorkflowStorage,
  executorAccount: Signer,    // Executor's Signer — held by network operators only
  prodContract: boolean,
  ipfsServiceUrl: string,
  simulate?: boolean,
  usePaymaster?: boolean,
  accessToken?: string,
): Promise<{ success: boolean; results: any[] }>;
```

## Multi-Chain Workflows

A workflow can have multiple jobs on different chains:

```typescript
.addJob(
  JobBuilder.create('job-sepolia')
    .setChainId(ChainId.SEPOLIA)
    .addStep({ /* ... */ })
    .build()
)
.addJob(
  JobBuilder.create('job-base')
    .setChainId(ChainId.BASE)
    .addStep({ /* ... */ })
    .build()
)
```

Each job gets its own session key and on-chain registration.

## Multi-Step Job (Approve + Swap)

Steps within a single job execute atomically:

```typescript
JobBuilder.create('weekly-dca')
  .setChainId(ChainId.BASE)
  .addStep({
    target: tokenAddress,
    abi: 'approve(address,uint256)',
    args: [routerAddress, amount],
  })
  .addStep({
    target: routerAddress,
    abi: 'swapExactTokensForETH(uint256,uint256,address[],address,uint256)',
    args: [amount, 0, [tokenAddress, wethAddress], owner.address, deadline],
  })
  .build()
```

Note: Time-dependent args like `deadline` are computed at script build time, not execution time. For workflows that may execute later, use generous deadlines or `dataRef` for on-chain timestamps.

## Validation Checklist

BEFORE calling `submitWorkflow`, verify:
- Every step has a valid `target` address (0x-prefixed, 42 chars)
- `abi` is a valid Solidity function signature or empty string for raw ETH transfer
- `chainId` is from the supported chains list
- At least one trigger is defined
- `count` is > 0 if set
- `validUntil` is in the future
- `.env` has `PRIVATE_KEY` and `IPFS_SERVICE_URL`

## Troubleshooting

### Error: "Missing required environment variables"
Cause: `.env` file missing or incomplete.
Solution: Ensure `PRIVATE_KEY` and `IPFS_SERVICE_URL` are set. The executor address is provided by the SDK via `getDittoExecutorAddress()` — do NOT add it to `.env`.

### Error: "Chain ID must be greater than 0"
Cause: `setChainId()` not called on JobBuilder.
Solution: Add `.setChainId(ChainId.BASE_SEPOLIA)` before `.build()`.

### Error: "Job must have at least one step"
Cause: No steps added to a job.
Solution: Add at least one `.addStep({...})` call.

### Error: "Expiration time must be in the future"
Cause: `setValidUntil` was given a past timestamp.
Solution: Use `Date.now() + duration_in_ms`.

### Error: "AA21 didn't pay prefund"
Cause: The ZeroDev smart account doesn't have enough ETH to pay for gas. The smart account address is different from the owner's EOA — it's derived deterministically from the owner's private key.
Solution: Send ETH to the smart account address shown in the error on the target chain. See "Step 3: Fund the Smart Account" above. For testnet, use a faucet. For production, 0.005–0.01 ETH is typically enough.

### Transaction fails / reverts
Causes:
- Smart account has insufficient ETH for the step values
- Target contract function reverts (wrong args, permissions)
- Session key expired or misconfigured

Solution: Ensure the owner's smart account is funded on the target chain. Verify contract args are correct.

### IPFS upload fails
Cause: `IPFS_SERVICE_URL` unreachable or invalid.
Solution: Verify the URL is correct and accessible. Default: `https://ipfs-service.dittonetwork.io`
