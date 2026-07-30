import { z } from "zod";
import { keccak256, encodePacked } from "viem";
import {
  validateInput,
  validateEndpointUrlStrict,
  EvmAddress,
  USDCRate,
  SafeTaskDescription,
  PaymentModel,
  PolicySchema,
  type Policy,
} from "../security/input-gate.js";
import { createTempSession, destroySession } from "../security/session.js";
import { createSandbox, enforcePolicyForPayment, destroySandbox } from "../security/sandbox.js";
import { ApprovalRequiredError } from "../security/approval.js";
import { assertReputation } from "../registry/reputation.js";
import { depositEscrow, releaseEscrow, refundEscrow } from "../payments/escrow.js";
import { sendX402Payment } from "../payments/x402.js";
import { toAtomicUSDC } from "../payments/usdc.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { toError, ProofVerificationError } from "../utils/errors.js";
import {
  acquireIdempotencyLock,
  markIdempotencyCompleted,
  releaseIdempotencyLock,
} from "../security/replay.js";
import { buildSignedTaskHeaders } from "../security/request-auth.js";
import { recordHireEvent } from "../analytics/store.js";

// ── Input schema ──────────────────────────────────────────────────────────────

const HireSchema = z.object({
  target_id: EvmAddress.describe("ERC-8004 registered agent address to hire"),
  task_description: SafeTaskDescription,
  payment_model: PaymentModel,
  rate: USDCRate,
  idempotency_key: z
    .string()
    .min(8)
    .max(128)
    .regex(/^[a-zA-Z0-9:_-]+$/, "idempotency_key contains invalid characters")
    .optional(),
  policy: PolicySchema.optional(),
  confirmed: z.boolean().optional().default(false),
});

export type HireInput = z.infer<typeof HireSchema>;

// ── Shared task DTO ───────────────────────────────────────────────────────────
// Kept in sync with src/server/http.ts request body schema.

export interface TaskRequestBody {
  task_description: string;
  payer: `0x${string}`;
  amount_atomic_usdc: string; // bigint serialised as decimal string
  session_id: string;         // hirer's session ID — worker uses for proof generation
}

export interface TaskResponseBody {
  task_id: string;
  proof_hash: `0x${string}`;
  output: unknown;
}

// ── Output type ───────────────────────────────────────────────────────────────

export interface HireResult {
  task_id: string;
  escrow_id: `0x${string}`;
  result: unknown;
  proof_hash: `0x${string}`;
  status: "completed" | "failed" | "refunded";
  reputation_score_at_hire: number;
  amount_paid_usdc: number;
  idempotency_key: string;
}

// ── A2A task delivery ─────────────────────────────────────────────────────────

async function deliverTaskToAgent(params: {
  agentId: `0x${string}`;
  taskDescription: string;
  paymentReceipt: string;
  escrowId: `0x${string}`;
  sessionId: string;
  hirerAddress: `0x${string}`;
  amountAtomicUSDC: bigint;
}): Promise<TaskResponseBody> {
  const config = getConfig();
  const { getAgentRecord } = await import("../registry/erc8004.js");
  const record = await getAgentRecord(params.agentId);

  const endpointCap = record.capabilities.find((c) => c.startsWith("endpoint:"));
  if (!endpointCap) {
    throw new Error(`Agent ${params.agentId} has no registered HTTP endpoint capability`);
  }

  const endpointBase = endpointCap.replace("endpoint:", "");

  // SSRF protection: validate URL before fetching (blocks localhost, private IPs, non-https)
  await validateEndpointUrlStrict(endpointBase);

  const body: TaskRequestBody = {
    task_description: params.taskDescription,
    payer: params.hirerAddress,
    amount_atomic_usdc: params.amountAtomicUSDC.toString(),
    session_id: params.sessionId, // worker uses this to compute matching proof_hash
  };
  const rawBody = JSON.stringify(body);
  const maybeAuthHeaders = config.TASK_AUTH_SHARED_SECRET
    ? buildSignedTaskHeaders({
      escrowId: params.escrowId,
      paymentReceipt: params.paymentReceipt,
      rawBody,
      sharedSecret: config.TASK_AUTH_SHARED_SECRET,
    })
    : {};

  const resp = await fetch(`${endpointBase}/task`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Payment-Receipt": params.paymentReceipt,
      "X-Escrow-Id": params.escrowId,
      ...maybeAuthHeaders,
    },
    body: rawBody,
    signal: AbortSignal.timeout(60_000),
    redirect: "error", // CRIT-04: refuse all HTTP redirects — prevents SSRF via 301/302
  });

  if (!resp.ok) {
    throw new Error(`Agent returned ${resp.status}: ${await resp.text()}`);
  }

  // Runtime-validate response — never trust foreign agent's shape
  const raw = await resp.json();
  const TaskResponseSchema = z.object({
    task_id: z.string().optional(),
    proof_hash: z
      .string()
      .regex(/^0x[a-fA-F0-9]{64}$/, "proof_hash must be 32-byte hex (0x + 64 chars)"),
    output: z.unknown().superRefine((v, ctx) => {
      if (JSON.stringify(v ?? "").length > 64 * 1024) {
        ctx.addIssue({ code: "custom", message: "output exceeds 64 KB limit" });
      }
    }),
  });
  return TaskResponseSchema.parse(raw) as TaskResponseBody;
}

// ── Proof verification ────────────────────────────────────────────────────────

function verifyProof(
  proofHash: `0x${string}`,
  sessionId: string,
  agentId: `0x${string}`
): boolean {
  // Strict: must be exactly 32-byte hex AND match keccak256(sessionId, agentAddress).
  // Any other value — including arbitrary 0x strings — is rejected.
  if (!/^0x[a-fA-F0-9]{64}$/.test(proofHash)) return false;

  const expected = keccak256(
    encodePacked(["string", "address"], [sessionId, agentId])
  );
  return proofHash.toLowerCase() === expected.toLowerCase();
}

// ── Tool handler ──────────────────────────────────────────────────────────────

export async function safe_hire_agent(rawInput: unknown): Promise<HireResult> {
  const input = validateInput(HireSchema, rawInput);
  const targetId = input.target_id as `0x${string}`;
  const config = getConfig();
  const policy = (input.policy ?? PolicySchema.parse({})) as Policy;

  const session = createTempSession({ tool: "safe_hire_agent" });
  const idempotencyKey =
    input.idempotency_key ??
    keccak256(
      encodePacked(
        ["address", "string", "string", "uint256"],
        [targetId, input.task_description, input.payment_model, toAtomicUSDC(input.rate)]
      )
    );
  await acquireIdempotencyLock(idempotencyKey);

  createSandbox(session.id, policy);
  let escrowId: `0x${string}` | undefined;
  let finalised = false;
  const ZERO_PROOF_HASH = `0x${"0".repeat(64)}` as `0x${string}`;

  try {
    // 1. Reputation gate
    const reputation = await assertReputation(targetId);
    logger.info({ event: "hire_reputation_ok", target: targetId, score: reputation.score });

    const amountAtomic = toAtomicUSDC(input.rate);

    // 2. Policy sandbox: enforce rate/chain limits before any spending
    const chain = config.BASE_RPC_URL.includes("mainnet") ? "base-mainnet" : "base-sepolia";
    enforcePolicyForPayment(session.id, input.rate, chain);

    // 3. Compute proof commitment (sessionId + workerAddress)
    //    Worker must return keccak256(session.id, workerAddress) to unlock escrow.
    const { getAgentAddress } = await import("../wallet/mpc.js");
    const hirerAddress = await getAgentAddress();

    const proofCommitment = keccak256(
      encodePacked(["string", "address"], [session.id, targetId])
    ) as `0x${string}`;

    // 4. Deposit escrow (includes USDC allowance pre-check, simulation + risk gating)
    const { escrowId: eid, txHash: escrowTxHash } = await depositEscrow(
      targetId,
      input.task_description,
      amountAtomic,
      proofCommitment,
      input.confirmed
    );
    escrowId = eid;
    logger.info({ event: "escrow_deposited", escrowId, escrowTxHash });

    // 5. x402 micropayment
    const payment = await sendX402Payment({
      agentId: targetId,
      amount: amountAtomic,
      paymentModel: input.payment_model,
    });

    // 6. Deliver task via HTTPS to agent's registered endpoint
    let taskResult: TaskResponseBody;
    try {
      taskResult = await deliverTaskToAgent({
        agentId: targetId,
        taskDescription: input.task_description,
        paymentReceipt: payment.receipt,
        escrowId: escrowId!,
        sessionId: session.id,
        hirerAddress,
        amountAtomicUSDC: amountAtomic,
      });
    } catch (deliveryErr) {
      logger.warn({ event: "task_delivery_failed", reason: toError(deliveryErr).message });
      await refundEscrow(escrowId!);
      await recordHireEvent({
        ts: Date.now(),
        target_id: targetId,
        status: "refunded",
        amount_paid_usdc: input.rate,
      });
      await markIdempotencyCompleted(idempotencyKey);
      finalised = true;
      return {
        task_id: session.id,
        escrow_id: escrowId!,
        result: null,
        proof_hash: ZERO_PROOF_HASH,
        status: "refunded",
        reputation_score_at_hire: reputation.score,
        amount_paid_usdc: input.rate,
        idempotency_key: idempotencyKey,
      };
    }

    // 7. Strict proof verification (no wildcards — must match commitment exactly)
    const proofValid = verifyProof(taskResult.proof_hash, session.id, targetId);
    if (!proofValid) {
      await refundEscrow(escrowId!);
      throw new ProofVerificationError(taskResult.proof_hash);
    }

    // 8. Release escrow (proof matches on-chain commitment)
    await releaseEscrow(escrowId!, taskResult.proof_hash);
    await recordHireEvent({
      ts: Date.now(),
      target_id: targetId,
      status: "completed",
      amount_paid_usdc: input.rate,
    });
    await markIdempotencyCompleted(idempotencyKey);
    finalised = true;

    logger.info({ event: "hire_complete", taskId: session.id, proofHash: taskResult.proof_hash });

    return {
      task_id: session.id,
      escrow_id: escrowId!,
      result: taskResult.output,
      proof_hash: taskResult.proof_hash,
      status: "completed",
      reputation_score_at_hire: reputation.score,
      amount_paid_usdc: input.rate,
      idempotency_key: idempotencyKey,
    };
  } catch (err) {
    await recordHireEvent({
      ts: Date.now(),
      target_id: targetId,
      status: "failed",
      amount_paid_usdc: input.rate,
    });
    if (escrowId) {
      try { await refundEscrow(escrowId); } catch (refundErr) {
        logger.error({ event: "escrow_refund_failed", escrowId, reason: toError(refundErr).message });
      }
    }
    throw err;
  } finally {
    if (!finalised) {
      await releaseIdempotencyLock(idempotencyKey);
    }
    destroySandbox(session.id);
    await destroySession(session.id);
  }
}
