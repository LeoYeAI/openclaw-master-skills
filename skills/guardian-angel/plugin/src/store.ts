/**
 * Guardian Angel Nonce Store
 * 
 * File-based storage for pending escalations and approved actions.
 */

import { createHash, randomBytes } from "node:crypto";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import type { GuardianAngelConfig, PendingEscalation, ApprovedAction, StoreState, Store } from "./types.js";
import { DEFAULT_PENDING_TIMEOUT_MS, DEFAULT_APPROVAL_WINDOW_MS } from "./constants.js";

export function createStore(
  config: GuardianAngelConfig,
  resolvePath: (input: string) => string
): Store {
  const storePath = config.storePath || resolvePath(".ga-state.json");
  const pendingTimeoutMs = config.pendingTimeoutMs || DEFAULT_PENDING_TIMEOUT_MS;
  const approvalWindowMs = config.approvalWindowMs || DEFAULT_APPROVAL_WINDOW_MS;

  function load(): StoreState {
    if (!existsSync(storePath)) {
      return { pending: {}, approved: {} };
    }
    try {
      const data = readFileSync(storePath, "utf-8");
      return JSON.parse(data) as StoreState;
    } catch {
      return { pending: {}, approved: {} };
    }
  }

  function save(state: StoreState): void {
    try {
      writeFileSync(storePath, JSON.stringify(state, null, 2));
    } catch (err) {
      // Log but don't throw - store is best-effort
      console.error("[GA] Failed to save store:", err);
    }
  }

  function hashParams(toolName: string, params: Record<string, unknown>): string {
    // Sort keys for consistent hashing
    const sortedKeys = Object.keys(params).sort();
    const normalized = JSON.stringify({ toolName, params }, sortedKeys);
    return createHash("sha256").update(normalized).digest("hex").slice(0, 16);
  }

  function createPending(
    paramsHash: string,
    toolName: string,
    params: Record<string, unknown>
  ): string {
    const state = load();
    const nonce = randomBytes(4).toString("hex"); // 8 hex chars

    state.pending[nonce] = {
      nonce,
      paramsHash,
      toolName,
      params,
      createdAt: Date.now(),
      expiresAt: Date.now() + pendingTimeoutMs,
    };

    save(state);
    return nonce;
  }

  function approvePending(nonce: string): { ok: true; windowSeconds: number } | { ok: false; error: string } {
    const state = load();
    const pending = state.pending[nonce];

    if (!pending) {
      return { ok: false, error: "Nonce not found or already used" };
    }

    if (Date.now() > pending.expiresAt) {
      delete state.pending[nonce];
      save(state);
      return { ok: false, error: "Escalation expired. Please retry the original action." };
    }

    // Move from pending to approved
    delete state.pending[nonce];
    state.approved[pending.paramsHash] = {
      nonce,
      paramsHash: pending.paramsHash,
      toolName: pending.toolName,
      approvedAt: Date.now(),
      expiresAt: Date.now() + approvalWindowMs,
    };

    save(state);
    return { ok: true, windowSeconds: Math.round(approvalWindowMs / 1000) };
  }

  function consumeApproval(paramsHash: string): { nonce: string } | null {
    const state = load();
    const approved = state.approved[paramsHash];

    if (!approved) {
      return null;
    }

    if (Date.now() > approved.expiresAt) {
      delete state.approved[paramsHash];
      save(state);
      return null;
    }

    // Consume (one-time use)
    delete state.approved[paramsHash];
    save(state);

    return { nonce: approved.nonce };
  }

  function cleanup(): void {
    const state = load();
    const now = Date.now();

    let changed = false;
    for (const [nonce, pending] of Object.entries(state.pending)) {
      if (now > pending.expiresAt) {
        delete state.pending[nonce];
        changed = true;
      }
    }
    for (const [hash, approved] of Object.entries(state.approved)) {
      if (now > approved.expiresAt) {
        delete state.approved[hash];
        changed = true;
      }
    }

    if (changed) save(state);
  }

  // Cleanup on initialization
  cleanup();

  return {
    hashParams,
    createPending,
    approvePending,
    consumeApproval,
    cleanup,
  };
}
