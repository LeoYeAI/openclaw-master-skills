import { createHash } from "crypto";
import { DuplicateRequestError, PaymentError } from "../utils/errors.js";

interface Entry {
  expiresAt: number;
  state: "reserved" | "used";
}

const RECEIPTS = new Map<string, Entry>();
const IDEMPOTENCY_LOCKS = new Map<string, number>();
const IDEMPOTENCY_COMPLETED = new Map<string, number>();

const DEFAULT_RECEIPT_RESERVED_TTL_MS = 60_000;
const DEFAULT_RECEIPT_USED_TTL_MS = 24 * 60 * 60 * 1000;
const DEFAULT_IDEMPOTENCY_TTL_MS = 2 * 60 * 1000;
const DEFAULT_IDEMPOTENCY_COMPLETED_TTL_MS = 24 * 60 * 60 * 1000;
interface RedisLikeClient {
  set(
    key: string,
    value: string,
    options?: { NX?: boolean; PX?: number }
  ): Promise<string | null>;
  get(key: string): Promise<string | null>;
  del(key: string): Promise<number>;
  connect(): Promise<void>;
  on(event: string, listener: (...args: unknown[]) => void): void;
}

let redisClientPromise: Promise<RedisLikeClient | null> | undefined;

function digest(input: string): string {
  return createHash("sha256").update(input).digest("hex");
}

function purgeExpiredMemory(now = Date.now()): void {
  for (const [key, value] of RECEIPTS) {
    if (value.expiresAt <= now) RECEIPTS.delete(key);
  }
  for (const [key, expiry] of IDEMPOTENCY_LOCKS) {
    if (expiry <= now) IDEMPOTENCY_LOCKS.delete(key);
  }
  for (const [key, expiry] of IDEMPOTENCY_COMPLETED) {
    if (expiry <= now) IDEMPOTENCY_COMPLETED.delete(key);
  }
}

function key(kind: "receipt" | "idempotency", digestHex: string): string {
  const prefix = process.env["REDIS_PREFIX"] || "SafeLink";
  return `${prefix}:${kind}:${digestHex}`;
}

async function getRedisClient(): Promise<RedisLikeClient | null> {
  const redisUrl = process.env["REDIS_URL"];
  if (!redisUrl) return null;
  if (redisClientPromise) return redisClientPromise;

  redisClientPromise = (async () => {
    const { createClient } = await import("redis");
    const client = createClient({ url: redisUrl }) as unknown as RedisLikeClient;
    client.on("error", () => {
      // Intentionally swallowed here; operations fail closed below.
    });
    await client.connect();
    return client;
  })().catch(() => null);

  return redisClientPromise ?? null;
}

export async function reserveReceipt(
  receipt: string,
  ttlMs = DEFAULT_RECEIPT_RESERVED_TTL_MS
): Promise<void> {
  const hashed = digest(receipt);
  const redis = await getRedisClient();
  if (redis) {
    const reserved = await redis.set(
      key("receipt", hashed),
      JSON.stringify({ state: "reserved" }),
      { NX: true, PX: ttlMs }
    );
    if (reserved !== "OK") {
      throw new PaymentError("Payment receipt replay detected");
    }
    return;
  }

  purgeExpiredMemory();
  const existing = RECEIPTS.get(hashed);
  if (existing && existing.expiresAt > Date.now()) {
    throw new PaymentError("Payment receipt replay detected");
  }
  RECEIPTS.set(hashed, { state: "reserved", expiresAt: Date.now() + ttlMs });
}

export async function markReservedReceiptUsed(
  receipt: string,
  ttlMs = DEFAULT_RECEIPT_USED_TTL_MS
): Promise<void> {
  const hashed = digest(receipt);
  const redis = await getRedisClient();
  if (redis) {
    const raw = await redis.get(key("receipt", hashed));
    if (!raw) {
      throw new PaymentError("Receipt reservation missing");
    }
    const payload = JSON.parse(raw) as { state?: string };
    if (payload.state !== "reserved") {
      throw new PaymentError("Payment receipt replay detected");
    }
    await redis.set(key("receipt", hashed), JSON.stringify({ state: "used" }), { PX: ttlMs });
    return;
  }

  const existing = RECEIPTS.get(hashed);
  if (!existing || existing.state !== "reserved") {
    throw new PaymentError("Receipt reservation missing");
  }
  RECEIPTS.set(hashed, { state: "used", expiresAt: Date.now() + ttlMs });
}

export async function releaseReservedReceipt(receipt: string): Promise<void> {
  const hashed = digest(receipt);
  const redis = await getRedisClient();
  if (redis) {
    const raw = await redis.get(key("receipt", hashed));
    if (!raw) return;
    const payload = JSON.parse(raw) as { state?: string };
    if (payload.state === "reserved") {
      await redis.del(key("receipt", hashed));
    }
    return;
  }

  const existing = RECEIPTS.get(hashed);
  if (existing?.state === "reserved") {
    RECEIPTS.delete(hashed);
  }
}

export async function acquireIdempotencyLock(
  lockKey: string,
  ttlMs = DEFAULT_IDEMPOTENCY_TTL_MS
): Promise<void> {
  const hashed = digest(lockKey);
  const redis = await getRedisClient();
  if (redis) {
    const locked = await redis.set(
      key("idempotency", hashed),
      "1",
      { NX: true, PX: ttlMs }
    );
    if (locked !== "OK") {
      throw new DuplicateRequestError("Duplicate request detected (idempotency lock active)");
    }
    return;
  }

  purgeExpiredMemory();
  const now = Date.now();
  const completedExpiry = IDEMPOTENCY_COMPLETED.get(hashed);
  if (completedExpiry && completedExpiry > now) {
    throw new DuplicateRequestError("Duplicate request detected (idempotency key already completed)");
  }
  const expiry = IDEMPOTENCY_LOCKS.get(hashed);
  if (expiry && expiry > now) {
    throw new DuplicateRequestError("Duplicate request detected (idempotency lock active)");
  }
  IDEMPOTENCY_LOCKS.set(hashed, now + ttlMs);
}

export async function markIdempotencyCompleted(
  lockKey: string,
  ttlMs = DEFAULT_IDEMPOTENCY_COMPLETED_TTL_MS
): Promise<void> {
  const hashed = digest(lockKey);
  const redis = await getRedisClient();
  if (redis) {
    await redis.set(key("idempotency", hashed), "completed", { PX: ttlMs });
    return;
  }
  purgeExpiredMemory();
  IDEMPOTENCY_COMPLETED.set(hashed, Date.now() + ttlMs);
}

export async function releaseIdempotencyLock(lockKey: string): Promise<void> {
  const hashed = digest(lockKey);
  const redis = await getRedisClient();
  if (redis) {
    const existing = await redis.get(key("idempotency", hashed));
    if (existing === "1") {
      await redis.del(key("idempotency", hashed));
    }
    return;
  }
  IDEMPOTENCY_LOCKS.delete(hashed);
}

export async function __resetReplayStateForTests(): Promise<void> {
  RECEIPTS.clear();
  IDEMPOTENCY_LOCKS.clear();
  IDEMPOTENCY_COMPLETED.clear();
}

