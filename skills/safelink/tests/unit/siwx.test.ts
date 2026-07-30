import { afterEach, describe, expect, it, vi } from "vitest";
import { verifySIWxAssertion } from "../../src/security/siwx.js";

const ORIGINAL_FETCH = globalThis.fetch;

describe("siwx verifier client", () => {
  afterEach(() => {
    globalThis.fetch = ORIGINAL_FETCH;
    vi.restoreAllMocks();
  });

  it("passes when verifier returns valid=true", async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ valid: true, expires_at: new Date(Date.now() + 60_000).toISOString() }),
    })) as typeof fetch;

    await expect(
      verifySIWxAssertion({
        assertion: "proof",
        payer: "0x1111111111111111111111111111111111111111",
        taskId: "task-1",
        verifierUrl: "https://verifier.example.com/siwx/verify",
      })
    ).resolves.toBeUndefined();
  });

  it("fails when verifier returns valid=false", async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ valid: false }),
    })) as typeof fetch;

    await expect(
      verifySIWxAssertion({
        assertion: "proof",
        payer: "0x1111111111111111111111111111111111111111",
        taskId: "task-1",
        verifierUrl: "https://verifier.example.com/siwx/verify",
      })
    ).rejects.toThrow(/invalid/i);
  });

  it("fails when assertion is expired", async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => ({ valid: true, expires_at: new Date(Date.now() - 1_000).toISOString() }),
    })) as typeof fetch;

    await expect(
      verifySIWxAssertion({
        assertion: "proof",
        payer: "0x1111111111111111111111111111111111111111",
        taskId: "task-1",
        verifierUrl: "https://verifier.example.com/siwx/verify",
      })
    ).rejects.toThrow(/expired/i);
  });

  it("fails when verifier returns non-ok HTTP status", async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: false,
      status: 500,
      json: async () => ({}),
    })) as typeof fetch;

    await expect(
      verifySIWxAssertion({
        assertion: "proof",
        payer: "0x1111111111111111111111111111111111111111",
        taskId: "task-1",
        verifierUrl: "https://verifier.example.com/siwx/verify",
      })
    ).rejects.toThrow(/500/);
  });

  it("fails when verifier returns invalid JSON", async () => {
    globalThis.fetch = vi.fn(async () => ({
      ok: true,
      status: 200,
      json: async () => { throw new SyntaxError("Unexpected token"); },
    })) as typeof fetch;

    await expect(
      verifySIWxAssertion({
        assertion: "proof",
        payer: "0x1111111111111111111111111111111111111111",
        taskId: "task-1",
        verifierUrl: "https://verifier.example.com/siwx/verify",
      })
    ).rejects.toThrow(/invalid JSON/i);
  });
});

