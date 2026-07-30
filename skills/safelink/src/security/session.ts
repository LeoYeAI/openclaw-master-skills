import { randomBytes } from "crypto";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface Session {
  id: string;
  tool: string;
  createdAt: number;
  expiresAt: number;
  /** Opaque context bag — cleared on destroy. */
  context: Map<string, unknown>;
}

// ── Session registry ──────────────────────────────────────────────────────────

const SESSIONS = new Map<string, Session>();

// Default session TTL: 10 minutes. Overridable per-session.
const DEFAULT_TTL_MS = 10 * 60 * 1000;

// ── Public API ────────────────────────────────────────────────────────────────

export interface CreateSessionOptions {
  tool: string;
  ttlMs?: number;
}

/** Create a temporary session. Must call destroySession() in a finally block. */
export function createTempSession(opts: CreateSessionOptions): Session {
  const id = randomBytes(16).toString("hex");
  const now = Date.now();
  const session: Session = {
    id,
    tool: opts.tool,
    createdAt: now,
    expiresAt: now + (opts.ttlMs ?? DEFAULT_TTL_MS),
    context: new Map(),
  };
  SESSIONS.set(id, session);
  logger.debug({ event: "session_created", sessionId: id, tool: opts.tool });
  return session;
}

/** Get an existing session by ID. Returns undefined if expired or not found. */
export function getSession(id: string): Session | undefined {
  const session = SESSIONS.get(id);
  if (!session) return undefined;
  if (Date.now() > session.expiresAt) {
    // Expired — destroy silently
    destroySession(id).catch(() => undefined);
    return undefined;
  }
  return session;
}

/**
 * Destroy a session and zero out all context.
 * Always call this in a finally block after createTempSession().
 */
export async function destroySession(id: string): Promise<void> {
  const session = SESSIONS.get(id);
  if (!session) return;

  // Zero out every context value before deletion (help GC + reduce leak window)
  for (const key of session.context.keys()) {
    session.context.set(key, null);
  }
  session.context.clear();

  SESSIONS.delete(id);
  logger.debug({ event: "session_destroyed", sessionId: id });
}

/** Destroy all expired sessions (call periodically in production). */
export function purgeExpiredSessions(): void {
  const now = Date.now();
  for (const [id, session] of SESSIONS) {
    if (now > session.expiresAt) {
      destroySession(id).catch(() => undefined);
    }
  }
}

// Auto-purge every 5 minutes
if (typeof setInterval !== "undefined") {
  setInterval(purgeExpiredSessions, 5 * 60 * 1000).unref?.();
}
