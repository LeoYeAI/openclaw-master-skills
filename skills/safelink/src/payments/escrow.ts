import { encodeAbiParameters, keccak256, encodePacked } from "viem";
import { getConfig } from "../utils/config.js";
import { EscrowError } from "../utils/errors.js";
import { getMPCWalletClient, getAgentAddress } from "../wallet/mpc.js";
import { getPublicClient } from "../wallet/provider.js";
import { simulateTx } from "../security/simulation.js";
import { scoreRisk } from "../security/risk-scorer.js";
import { requireApproval, ApprovalRequiredError } from "../security/approval.js";
import { getUSDCAllowance, getUSDCAddress, buildApproveCalldata } from "./usdc.js";
import { logger } from "../utils/logger.js";

// ── Simple mutex to prevent concurrent approve+deposit races (HIGH-05) ─────────

class SimpleMutex {
  private _locked = false;
  private _queue: Array<() => void> = [];

  async runExclusive<T>(fn: () => Promise<T>): Promise<T> {
    await new Promise<void>((resolve) => {
      const tryAcquire = () => {
        if (!this._locked) { this._locked = true; resolve(); }
        else this._queue.push(tryAcquire);
      };
      tryAcquire();
    });
    try {
      return await fn();
    } finally {
      this._locked = false;
      const next = this._queue.shift();
      if (next) next();
    }
  }
}

const _depositMutex = new SimpleMutex();

// MaxUint256 for single-approval pattern (avoids repeated approve txs and race conditions)
const MAX_UINT256 = 2n ** 256n - 1n;

// ── SafeEscrow ABI (must match SafeEscrow.sol) ────────────────────────────────

const SAFE_ESCROW_ABI = [
  {
    name: "deposit",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "agent", type: "address" },
      { name: "taskHash", type: "bytes32" },
      { name: "proofCommitment", type: "bytes32" },
      { name: "amount", type: "uint256" },
      { name: "durationSeconds", type: "uint256" },
    ],
    outputs: [{ name: "escrowId", type: "bytes32" }],
  },
  {
    name: "release",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [
      { name: "escrowId", type: "bytes32" },
      { name: "proofHash", type: "bytes32" },
    ],
    outputs: [],
  },
  {
    name: "refund",
    type: "function",
    stateMutability: "nonpayable",
    inputs: [{ name: "escrowId", type: "bytes32" }],
    outputs: [],
  },
  {
    name: "getEscrow",
    type: "function",
    stateMutability: "view",
    inputs: [{ name: "escrowId", type: "bytes32" }],
    outputs: [
      { name: "hirer", type: "address" },
      { name: "agent", type: "address" },
      { name: "amount", type: "uint256" },
      { name: "taskHash", type: "bytes32" },
      { name: "proofCommitment", type: "bytes32" },
      { name: "status", type: "uint8" },
      { name: "createdAt", type: "uint256" },
      { name: "expiresAt", type: "uint256" },
    ],
  },
] as const;

// ── Types ─────────────────────────────────────────────────────────────────────

export type EscrowStatus = "active" | "released" | "refunded";

export interface EscrowRecord {
  hirer: `0x${string}`;
  agent: `0x${string}`;
  amountAtomicUSDC: bigint;
  taskHash: `0x${string}`;
  proofCommitment: `0x${string}`;
  status: EscrowStatus;
  createdAt: bigint;
  expiresAt: bigint;
}

// ── Internal helpers ──────────────────────────────────────────────────────────

function getEscrowContract(): `0x${string}` {
  const config = getConfig();
  if (!config.SAFE_ESCROW_ADDRESS) {
    throw new EscrowError(
      "SAFE_ESCROW_ADDRESS not set. Run `npm run deploy:contracts` first."
    );
  }
  return config.SAFE_ESCROW_ADDRESS as `0x${string}`;
}

function buildDepositCalldata(
  agent: `0x${string}`,
  taskHash: `0x${string}`,
  proofCommitment: `0x${string}`,
  amount: bigint,
  durationSeconds: bigint
): `0x${string}` {
  const selector = keccak256(
    encodePacked(["string"], ["deposit(address,bytes32,bytes32,uint256,uint256)"])
  ).slice(0, 10);
  const encoded = encodeAbiParameters(
    [
      { name: "agent", type: "address" },
      { name: "taskHash", type: "bytes32" },
      { name: "proofCommitment", type: "bytes32" },
      { name: "amount", type: "uint256" },
      { name: "durationSeconds", type: "uint256" },
    ],
    [agent, taskHash, proofCommitment, amount, durationSeconds]
  );
  return `${selector}${encoded.slice(2)}` as `0x${string}`;
}

function buildReleaseCalldata(
  escrowId: `0x${string}`,
  proofHash: `0x${string}`
): `0x${string}` {
  const selector = keccak256(
    encodePacked(["string"], ["release(bytes32,bytes32)"])
  ).slice(0, 10);
  const encoded = encodeAbiParameters(
    [{ name: "escrowId", type: "bytes32" }, { name: "proofHash", type: "bytes32" }],
    [escrowId, proofHash]
  );
  return `${selector}${encoded.slice(2)}` as `0x${string}`;
}

function buildRefundCalldata(escrowId: `0x${string}`): `0x${string}` {
  const selector = keccak256(
    encodePacked(["string"], ["refund(bytes32)"])
  ).slice(0, 10);
  const encoded = encodeAbiParameters(
    [{ name: "escrowId", type: "bytes32" }],
    [escrowId]
  );
  return `${selector}${encoded.slice(2)}` as `0x${string}`;
}

// ── Public API ────────────────────────────────────────────────────────────────

/**
 * Deposit USDC into escrow for a task.
 *
 * Security pipeline:
 *  1. Pre-check USDC allowance — auto-approves if insufficient (simulated first).
 *  2. Simulate deposit tx before any signing.
 *  3. Risk-score simulation — blocks if score ≥ threshold and !confirmed.
 *  4. proofCommitment stored on-chain; only the matching proof can release funds.
 */
export async function depositEscrow(
  agent: `0x${string}`,
  taskDescription: string,
  amountAtomicUSDC: bigint,
  proofCommitment: `0x${string}`,
  confirmed = false,
  durationSeconds = 900 // increased from 300 → 900s (15 min) for congested networks
): Promise<{ escrowId: `0x${string}`; txHash: `0x${string}` }> {
  // HIGH-05: mutex prevents concurrent approve+deposit races where two callers
  // both see allowance=0, both issue approve(), first mines and gets spent,
  // second deposit fails with insufficient allowance.
  return _depositMutex.runExclusive(async () => {
    const config = getConfig();
    const escrowAddress = getEscrowContract();
    const taskHash = keccak256(encodePacked(["string"], [taskDescription])) as `0x${string}`;
    const network = config.BASE_RPC_URL.includes("mainnet")
      ? ("base-mainnet" as const)
      : ("base-sepolia" as const);

    // ── USDC allowance pre-check ────────────────────────────────────────────
    const hirerAddress = await getAgentAddress();
    const usdcAddress = getUSDCAddress(config.BASE_RPC_URL);
    const currentAllowance = await getUSDCAllowance(hirerAddress, escrowAddress, network);

    if (currentAllowance < amountAtomicUSDC) {
      logger.info({
        event: "usdc_approve_needed",
        currentAllowance: currentAllowance.toString(),
        required: amountAtomicUSDC.toString(),
      });

    const approveTx = {
      to: usdcAddress,
      // HIGH-05: approve MaxUint256 once — eliminates repeated approvals
      // and prevents the race condition where two concurrent deposits both
      // read allowance=0, both approve, and one deposit fails.
      data: buildApproveCalldata(escrowAddress, MAX_UINT256),
      value: 0n,
    };

    const approveSimulation = await simulateTx(approveTx);
    if (!approveSimulation.success) {
      throw new EscrowError(
        `USDC approve simulation failed: ${approveSimulation.revertReason ?? "unknown"}`
      );
    }

    const approveWallet = await getMPCWalletClient();
    const approveTxHash = await approveWallet.sendTransaction(approveTx);
    await getPublicClient().waitForTransactionReceipt({ hash: approveTxHash });
    logger.info({ event: "usdc_approved", approveTxHash });
  }

  // ── Build and simulate deposit tx ─────────────────────────────────────────
  const calldata = buildDepositCalldata(
    agent,
    taskHash,
    proofCommitment,
    amountAtomicUSDC,
    BigInt(durationSeconds)
  );
  const depositTx = { to: escrowAddress, data: calldata, value: 0n };

  const simulation = await simulateTx(depositTx);
  if (!simulation.success) {
    throw new EscrowError(
      `Escrow deposit simulation failed: ${simulation.revertReason ?? "unknown"}`
    );
  }

  // ── Risk gating ───────────────────────────────────────────────────────────
  const { score, flags } = await scoreRisk(simulation);
  logger.info({ event: "escrow_deposit_risk", score, flags });

  if (score >= config.RISK_APPROVAL_THRESHOLD && !confirmed) {
    throw new ApprovalRequiredError({
      action: `Deposit ${amountAtomicUSDC} atomic USDC into escrow for agent ${agent}`,
      details: simulation,
      riskScore: score,
      riskFlags: flags,
    });
  }

  if (score >= 30 && score < config.RISK_APPROVAL_THRESHOLD) {
    const approved = await requireApproval({
      action: `Escrow deposit (moderate risk score: ${score})`,
      details: simulation,
      riskScore: score,
      riskFlags: flags,
    });
    if (!approved) {
      throw new EscrowError("User rejected escrow deposit");
    }
  }

  // ── Sign and broadcast ────────────────────────────────────────────────────
  const wallet = await getMPCWalletClient();
  const txHash = await wallet.sendTransaction(depositTx);
  const receipt = await getPublicClient().waitForTransactionReceipt({ hash: txHash });

  // Parse escrowId from EscrowDeposited(bytes32 indexed escrowId, ...) log
  const depositLog = receipt.logs.find(
    (l) =>
      l.address.toLowerCase() === escrowAddress.toLowerCase() &&
      l.topics[0] ===
        keccak256(
          encodePacked(
            ["string"],
            ["EscrowDeposited(bytes32,address,address,uint256,bytes32,uint256)"]
          )
        )
  );

  if (!depositLog?.topics[1]) {
    throw new EscrowError("EscrowDeposited event not found in receipt");
  }

    const escrowId = depositLog.topics[1] as `0x${string}`;
    logger.info({ event: "escrow_deposited", escrowId, txHash });
    return { escrowId, txHash };
  }); // end _depositMutex.runExclusive
}

/** Release escrow funds to the agent. proofHash must equal the on-chain proofCommitment. */
export async function releaseEscrow(
  escrowId: `0x${string}`,
  proofHash: `0x${string}`
): Promise<`0x${string}`> {
  const escrowAddress = getEscrowContract();
  const wallet = await getMPCWalletClient();
  const txHash = await wallet.sendTransaction({
    to: escrowAddress,
    data: buildReleaseCalldata(escrowId, proofHash),
    value: 0n,
  });
  // MED-05: wait for on-chain confirmation before declaring success
  const receipt = await getPublicClient().waitForTransactionReceipt({
    hash: txHash,
    timeout: 120_000,
  });
  if (receipt.status === "reverted") {
    throw new EscrowError(
      `Escrow release tx reverted (${txHash}). Escrow is still active — check on-chain state.`
    );
  }
  logger.info({ event: "escrow_released", escrowId, txHash });
  return txHash;
}

/** Refund escrow back to hirer on task failure or timeout. */
export async function refundEscrow(escrowId: `0x${string}`): Promise<`0x${string}`> {
  const escrowAddress = getEscrowContract();
  const wallet = await getMPCWalletClient();
  const txHash = await wallet.sendTransaction({
    to: escrowAddress,
    data: buildRefundCalldata(escrowId),
    value: 0n,
  });
  // MED-05: wait for on-chain confirmation
  const receipt = await getPublicClient().waitForTransactionReceipt({
    hash: txHash,
    timeout: 120_000,
  });
  if (receipt.status === "reverted") {
    throw new EscrowError(
      `Escrow refund tx reverted (${txHash}). Funds may still be locked — check on-chain state.`
    );
  }
  logger.info({ event: "escrow_refunded", escrowId, txHash });
  return txHash;
}

/** Read escrow state from chain. */
export async function getEscrowRecord(escrowId: `0x${string}`): Promise<EscrowRecord> {
  const client = getPublicClient();
  const escrowAddress = getEscrowContract();

  const result = await client.readContract({
    address: escrowAddress,
    abi: SAFE_ESCROW_ABI,
    functionName: "getEscrow",
    args: [escrowId],
  });

  const STATUS_MAP: Record<number, EscrowStatus> = {
    0: "active",
    1: "released",
    2: "refunded",
  };

  return {
    hirer: result[0],
    agent: result[1],
    amountAtomicUSDC: result[2],
    taskHash: result[3],
    proofCommitment: result[4],
    status: STATUS_MAP[result[5]] ?? "active",
    createdAt: result[6],
    expiresAt: result[7],
  };
}
