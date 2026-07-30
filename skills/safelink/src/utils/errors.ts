// Custom error hierarchy for SafeLink.
// All errors include a `code` field suitable for MCP error responses.

export class SafeChainError extends Error {
  readonly code: string;
  constructor(message: string, code: string) {
    super(message);
    this.name = "SafeChainError";
    this.code = code;
  }
}

export class ValidationError extends SafeChainError {
  constructor(message: string) {
    super(message, "VALIDATION_ERROR");
    this.name = "ValidationError";
  }
}

export class ReputationError extends SafeChainError {
  readonly agentId: string;
  readonly score: number;
  constructor(agentId: string, score: number, threshold: number) {
    super(
      `Agent ${agentId} reputation score ${score}/100 is below threshold ${threshold}`,
      "REPUTATION_TOO_LOW"
    );
    this.name = "ReputationError";
    this.agentId = agentId;
    this.score = score;
  }
}

export class SimulationError extends SafeChainError {
  readonly revertReason?: string;
  constructor(revertReason?: string) {
    super(
      `Transaction simulation failed${revertReason ? ": " + revertReason : ""}`,
      "SIMULATION_FAILED"
    );
    this.name = "SimulationError";
    if (revertReason !== undefined) this.revertReason = revertReason;
  }
}

export class RiskBlockedError extends SafeChainError {
  readonly riskScore: number;
  readonly flags: string[];
  constructor(score: number, flags: string[]) {
    super(
      `Transaction blocked: risk score ${score}/100. Flags: ${flags.join(", ")}`,
      "RISK_BLOCKED"
    );
    this.name = "RiskBlockedError";
    this.riskScore = score;
    this.flags = flags;
  }
}

export class UserRejectedError extends SafeChainError {
  constructor(action: string) {
    super(`User rejected action: ${action}`, "USER_REJECTED");
    this.name = "UserRejectedError";
  }
}

export class EscrowError extends SafeChainError {
  constructor(message: string) {
    super(message, "ESCROW_ERROR");
    this.name = "EscrowError";
  }
}

export class PaymentError extends SafeChainError {
  constructor(message: string) {
    super(message, "PAYMENT_ERROR");
    this.name = "PaymentError";
  }
}

export class DuplicateRequestError extends SafeChainError {
  constructor(message: string) {
    super(message, "DUPLICATE_REQUEST");
    this.name = "DuplicateRequestError";
  }
}

export class ProofVerificationError extends SafeChainError {
  readonly proofHash: string;
  constructor(proofHash: string) {
    super(`Proof verification failed for hash ${proofHash}`, "PROOF_INVALID");
    this.name = "ProofVerificationError";
    this.proofHash = proofHash;
  }
}

export class WalletError extends SafeChainError {
  constructor(message: string) {
    super(message, "WALLET_ERROR");
    this.name = "WalletError";
  }
}

export class RegistryError extends SafeChainError {
  constructor(message: string) {
    super(message, "REGISTRY_ERROR");
    this.name = "RegistryError";
  }
}

export class MemoryError extends SafeChainError {
  constructor(message: string) {
    super(message, "MEMORY_ERROR");
    this.name = "MemoryError";
  }
}

/** Narrow any thrown value to an Error instance. */
export function toError(e: unknown): Error {
  if (e instanceof Error) return e;
  return new Error(String(e));
}


