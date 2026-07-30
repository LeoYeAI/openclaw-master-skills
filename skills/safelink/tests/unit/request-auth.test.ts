import { beforeEach, describe, expect, it } from "vitest";
import {
  buildSignedTaskHeaders,
  verifySignedTaskRequest,
} from "../../src/security/request-auth.js";
import { __resetReplayStateForTests } from "../../src/security/replay.js";

const SHARED_SECRET = "x".repeat(48);
const escrowId = "0x" + "ab".repeat(32);
const paymentReceipt = "receipt-123";
const rawBody = JSON.stringify({
  task_description: "test",
  payer: "0x1111111111111111111111111111111111111111",
  amount_atomic_usdc: "1000000",
  session_id: "a".repeat(32),
});

describe("request auth", () => {
  beforeEach(async () => {
    await __resetReplayStateForTests();
  });

  it("builds and verifies signed task headers", async () => {
    const headers = buildSignedTaskHeaders({
      escrowId,
      paymentReceipt,
      rawBody,
      sharedSecret: SHARED_SECRET,
      timestampSeconds: Math.floor(Date.now() / 1000),
      nonce: "nonce-1",
    });

    await expect(
      verifySignedTaskRequest({
        escrowId,
        paymentReceipt,
        rawBody,
        signature: headers["X-SafeLink-Signature"],
        timestamp: headers["X-SafeLink-Timestamp"],
        nonce: headers["X-SafeLink-Nonce"],
        config: {
          required: true,
          sharedSecret: SHARED_SECRET,
          maxSkewSeconds: 300,
        },
      })
    ).resolves.toBeUndefined();
  });

  it("rejects missing headers when auth is required", async () => {
    await expect(
      verifySignedTaskRequest({
        escrowId,
        paymentReceipt,
        rawBody,
        config: {
          required: true,
          sharedSecret: SHARED_SECRET,
          maxSkewSeconds: 300,
        },
      })
    ).rejects.toThrow(/Missing signed auth headers/i);
  });

  it("rejects replayed nonces", async () => {
    const headers = buildSignedTaskHeaders({
      escrowId,
      paymentReceipt,
      rawBody,
      sharedSecret: SHARED_SECRET,
      timestampSeconds: Math.floor(Date.now() / 1000),
      nonce: "nonce-replay",
    });

    const verifyInput = {
      escrowId,
      paymentReceipt,
      rawBody,
      signature: headers["X-SafeLink-Signature"],
      timestamp: headers["X-SafeLink-Timestamp"],
      nonce: headers["X-SafeLink-Nonce"],
      config: {
        required: true,
        sharedSecret: SHARED_SECRET,
        maxSkewSeconds: 300,
      },
    } as const;

    await verifySignedTaskRequest(verifyInput);
    await expect(verifySignedTaskRequest(verifyInput)).rejects.toThrow(/Duplicate request/i);
  });

  it("rejects expired timestamp", async () => {
    const headers = buildSignedTaskHeaders({
      escrowId,
      paymentReceipt,
      rawBody,
      sharedSecret: SHARED_SECRET,
      timestampSeconds: Math.floor(Date.now() / 1000) - 1000,
      nonce: "nonce-expired",
    });

    await expect(
      verifySignedTaskRequest({
        escrowId,
        paymentReceipt,
        rawBody,
        signature: headers["X-SafeLink-Signature"],
        timestamp: headers["X-SafeLink-Timestamp"],
        nonce: headers["X-SafeLink-Nonce"],
        config: {
          required: true,
          sharedSecret: SHARED_SECRET,
          maxSkewSeconds: 60,
        },
      })
    ).rejects.toThrow(/outside allowed skew/i);
  });

  it("rejects short shared secret on buildSignedTaskHeaders", () => {
    expect(() =>
      buildSignedTaskHeaders({
        escrowId,
        paymentReceipt,
        rawBody,
        sharedSecret: "tooshort",
      })
    ).toThrow(/at least 32/i);
  });

  it("rejects tampered signature with wrong byte length", async () => {
    const headers = buildSignedTaskHeaders({
      escrowId,
      paymentReceipt,
      rawBody,
      sharedSecret: SHARED_SECRET,
      timestampSeconds: Math.floor(Date.now() / 1000),
      nonce: "nonce-tampered",
    });

    // Truncate the signature hex so it decodes to a different byte length
    const truncatedSig = headers["X-SafeLink-Signature"]!.slice(0, -2);

    await expect(
      verifySignedTaskRequest({
        escrowId,
        paymentReceipt,
        rawBody,
        signature: truncatedSig,
        timestamp: headers["X-SafeLink-Timestamp"],
        nonce: headers["X-SafeLink-Nonce"],
        config: {
          required: true,
          sharedSecret: SHARED_SECRET,
          maxSkewSeconds: 300,
        },
      })
    ).rejects.toThrow(/Invalid request signature/i);
  });

  it("skips auth when not required and no auth headers present", async () => {
    await expect(
      verifySignedTaskRequest({
        escrowId,
        paymentReceipt,
        rawBody,
        config: {
          required: false,
          maxSkewSeconds: 300,
        },
      })
    ).resolves.toBeUndefined();
  });
});

