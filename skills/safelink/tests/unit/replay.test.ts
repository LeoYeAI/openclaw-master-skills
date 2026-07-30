import { describe, it, expect, beforeEach } from "vitest";
import {
  __resetReplayStateForTests,
  acquireIdempotencyLock,
  markIdempotencyCompleted,
  markReservedReceiptUsed,
  releaseIdempotencyLock,
  releaseReservedReceipt,
  reserveReceipt,
} from "../../src/security/replay.js";
import { DuplicateRequestError, PaymentError } from "../../src/utils/errors.js";

describe("replay guard", () => {
  beforeEach(async () => {
    await __resetReplayStateForTests();
  });

  it("rejects replayed payment receipts", async () => {
    await reserveReceipt("r-1");
    await expect(reserveReceipt("r-1")).rejects.toThrow(PaymentError);
  });

  it("allows reuse after releasing reserved receipt", async () => {
    await reserveReceipt("r-2");
    await releaseReservedReceipt("r-2");
    await expect(reserveReceipt("r-2")).resolves.toBeUndefined();
  });

  it("marks valid receipt as used and blocks future reuse", async () => {
    await reserveReceipt("r-3");
    await markReservedReceiptUsed("r-3");
    await expect(reserveReceipt("r-3")).rejects.toThrow(PaymentError);
  });

  it("enforces idempotency lock for duplicate concurrent operations", async () => {
    await acquireIdempotencyLock("hire-op-1");
    await expect(acquireIdempotencyLock("hire-op-1")).rejects.toThrow(DuplicateRequestError);
    await releaseIdempotencyLock("hire-op-1");
    await expect(acquireIdempotencyLock("hire-op-1")).resolves.toBeUndefined();
  });

  it("blocks reuse of completed idempotency keys", async () => {
    await acquireIdempotencyLock("hire-op-2");
    await markIdempotencyCompleted("hire-op-2");
    await releaseIdempotencyLock("hire-op-2");
    await expect(acquireIdempotencyLock("hire-op-2")).rejects.toThrow(DuplicateRequestError);
  });
});
