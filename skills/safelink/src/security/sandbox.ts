import type { Policy } from "./input-gate.js";
import { ValidationError } from "../utils/errors.js";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface SandboxContext {
  sessionId: string;
  policy: Policy;
  startedAt: number;
  requestCount: number;
  totalSpendUSDC: number;
}

// ── In-memory sandbox registry ────────────────────────────────────────────────

const SANDBOX_CONTEXTS = new Map<string, SandboxContext>();

// ── Public API ────────────────────────────────────────────────────────────────

export function createSandbox(sessionId: string, policy: Policy): SandboxContext {
  const ctx: SandboxContext = {
    sessionId,
    policy,
    startedAt: Date.now(),
    requestCount: 0,
    totalSpendUSDC: 0,
  };
  SANDBOX_CONTEXTS.set(sessionId, ctx);
  logger.debug({ event: "sandbox_created", sessionId });
  return ctx;
}

export function destroySandbox(sessionId: string): void {
  SANDBOX_CONTEXTS.delete(sessionId);
  logger.debug({ event: "sandbox_destroyed", sessionId });
}

/**
 * Enforce sandbox policy for a payment action.
 * Throws ValidationError if any limit is exceeded.
 */
export function enforcePolicyForPayment(
  sessionId: string,
  amountUSDC: number,
  chain: string
): void {
  const ctx = SANDBOX_CONTEXTS.get(sessionId);
  if (!ctx) {
    throw new ValidationError(`No sandbox found for session ${sessionId}`);
  }

  // Time limit
  const elapsedSeconds = (Date.now() - ctx.startedAt) / 1000;
  if (elapsedSeconds > ctx.policy.max_task_seconds) {
    throw new ValidationError(
      `Session exceeded max_task_seconds (${ctx.policy.max_task_seconds}s). ` +
        `Elapsed: ${Math.round(elapsedSeconds)}s`
    );
  }

  // Chain allowlist
  if (!ctx.policy.allowed_chains.includes(chain as never)) {
    throw new ValidationError(
      `Chain "${chain}" is not in allowed_chains: ${ctx.policy.allowed_chains.join(", ")}`
    );
  }

  // Per-operation rate cap
  if (amountUSDC > ctx.policy.max_rate_usdc) {
    throw new ValidationError(
      `Payment ${amountUSDC} USDC exceeds policy max_rate_usdc (${ctx.policy.max_rate_usdc} USDC)`
    );
  }

  // Record spend
  ctx.requestCount += 1;
  ctx.totalSpendUSDC += amountUSDC;

  logger.debug({
    event: "sandbox_policy_check_passed",
    sessionId,
    amountUSDC,
    totalSpendUSDC: ctx.totalSpendUSDC,
    requestCount: ctx.requestCount,
  });
}
