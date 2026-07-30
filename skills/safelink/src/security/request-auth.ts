import { createHash, createHmac, randomUUID, timingSafeEqual } from "node:crypto";
import { acquireIdempotencyLock } from "./replay.js";

const MIN_SECRET_LENGTH = 32;

export interface RequestAuthConfig {
  required: boolean;
  sharedSecret?: string;
  maxSkewSeconds: number;
}

export interface AuthHeadersInput {
  escrowId: string;
  paymentReceipt: string;
  rawBody: string;
  sharedSecret: string;
  timestampSeconds?: number;
  nonce?: string;
}

export interface AuthVerificationInput {
  escrowId: string;
  paymentReceipt: string;
  rawBody: string;
  signature?: string;
  timestamp?: string;
  nonce?: string;
  config: RequestAuthConfig;
}

function sha256Hex(input: string): string {
  return createHash("sha256").update(input, "utf8").digest("hex");
}

function canonicalPayload(
  timestamp: string,
  nonce: string,
  escrowId: string,
  paymentReceipt: string,
  bodyHashHex: string
): string {
  return `${timestamp}\n${nonce}\n${escrowId.toLowerCase()}\n${paymentReceipt}\n${bodyHashHex}`;
}

function signPayload(payload: string, sharedSecret: string): string {
  return createHmac("sha256", sharedSecret).update(payload, "utf8").digest("hex");
}

export function buildSignedTaskHeaders(input: AuthHeadersInput): Record<string, string> {
  if (input.sharedSecret.length < MIN_SECRET_LENGTH) {
    throw new Error(`TASK_AUTH_SHARED_SECRET must be at least ${MIN_SECRET_LENGTH} characters`);
  }

  const timestamp = String(input.timestampSeconds ?? Math.floor(Date.now() / 1000));
  const nonce = input.nonce ?? randomUUID();
  const bodyHash = sha256Hex(input.rawBody);
  const payload = canonicalPayload(
    timestamp,
    nonce,
    input.escrowId,
    input.paymentReceipt,
    bodyHash
  );
  const signature = signPayload(payload, input.sharedSecret);

  return {
    "X-SafeLink-Timestamp": timestamp,
    "X-SafeLink-Nonce": nonce,
    "X-SafeLink-Signature": signature,
  };
}

export async function verifySignedTaskRequest(input: AuthVerificationInput): Promise<void> {
  const modeRequired = input.config.required;
  const secret = input.config.sharedSecret;

  const hasAnyAuthHeader = Boolean(input.signature || input.timestamp || input.nonce);
  if (!modeRequired && !hasAnyAuthHeader) {
    return;
  }

  if (!secret || secret.length < MIN_SECRET_LENGTH) {
    throw new Error(
      "Task request authentication is enabled but TASK_AUTH_SHARED_SECRET is missing/too short"
    );
  }

  if (!input.signature || !input.timestamp || !input.nonce) {
    throw new Error("Missing signed auth headers (X-SafeLink-Timestamp/Nonce/Signature)");
  }

  if (!/^\d{10,}$/.test(input.timestamp)) {
    throw new Error("Invalid X-SafeLink-Timestamp format");
  }

  const tsSeconds = Number(input.timestamp);
  if (!Number.isFinite(tsSeconds)) {
    throw new Error("Invalid X-SafeLink-Timestamp value");
  }

  const nowSeconds = Math.floor(Date.now() / 1000);
  const skew = Math.abs(nowSeconds - tsSeconds);
  if (skew > input.config.maxSkewSeconds) {
    throw new Error("Signed request timestamp outside allowed skew");
  }

  // Replay resistance for auth nonces using existing distributed idempotency store.
  const nonceTtlMs = (input.config.maxSkewSeconds + 60) * 1000;
  await acquireIdempotencyLock(`task-auth-nonce:${input.nonce}`, nonceTtlMs);

  const bodyHash = sha256Hex(input.rawBody);
  const payload = canonicalPayload(
    input.timestamp,
    input.nonce,
    input.escrowId,
    input.paymentReceipt,
    bodyHash
  );
  const expected = signPayload(payload, secret);

  const provided = input.signature.toLowerCase();
  const expectedBuf = Buffer.from(expected, "hex");
  const providedBuf = Buffer.from(provided, "hex");

  if (expectedBuf.length !== providedBuf.length || !timingSafeEqual(expectedBuf, providedBuf)) {
    throw new Error("Invalid request signature");
  }
}

