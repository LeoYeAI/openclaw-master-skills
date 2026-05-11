/**
 * Guardian Angel Types
 */

export interface GuardianAngelConfig {
  enabled?: boolean;
  logLevel?: "debug" | "info" | "warn" | "error";
  escalationThreshold?: number;
  pendingTimeoutMs?: number;
  approvalWindowMs?: number;
  storePath?: string;
  alwaysBlock?: string[];
  neverBlock?: string[];
}

export interface EvaluationResult {
  decision: "allow" | "block" | "escalate";
  reason?: string;
  clarity?: number;
  stakes?: number;
}

export interface PendingEscalation {
  nonce: string;
  paramsHash: string;
  toolName: string;
  params: Record<string, unknown>;
  createdAt: number;
  expiresAt: number;
}

export interface ApprovedAction {
  nonce: string;
  paramsHash: string;
  toolName: string;
  approvedAt: number;
  expiresAt: number;
}

export interface StoreState {
  pending: Record<string, PendingEscalation>;
  approved: Record<string, ApprovedAction>;
}

export interface Store {
  hashParams(toolName: string, params: Record<string, unknown>): string;
  createPending(paramsHash: string, toolName: string, params: Record<string, unknown>): string;
  approvePending(nonce: string): { ok: true; windowSeconds: number } | { ok: false; error: string };
  consumeApproval(paramsHash: string): { nonce: string } | null;
  cleanup(): void;
}

export interface PluginLogger {
  debug?: (message: string) => void;
  info: (message: string) => void;
  warn: (message: string) => void;
  error: (message: string) => void;
}
