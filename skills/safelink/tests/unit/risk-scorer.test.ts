import { describe, it, expect } from "vitest";
import { scoreRisk, isAutoApprovable, requiresApproval } from "../../src/security/risk-scorer.js";
import type { SimulationReport } from "../../src/security/simulation.js";

// ── Helpers ───────────────────────────────────────────────────────────────────

function makeReport(overrides: Partial<SimulationReport> = {}): SimulationReport {
  return {
    success: true,
    gasEstimate: 100_000n,
    to: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
    stateDiff: {},
    approvals: [],
    delegateCalls: [],
    eventLogs: [],
    opcodes: [],
    raw: {},
    ...overrides,
  };
}

// ── Tests ─────────────────────────────────────────────────────────────────────

describe("scoreRisk", () => {
  it("returns score 0 with no flags for clean simulation", async () => {
    const result = await scoreRisk(makeReport());
    expect(result.score).toBe(0);
    expect(result.flags).toHaveLength(0);
  });

  it("returns score 100 for failed simulation", async () => {
    const result = await scoreRisk(makeReport({ success: false, revertReason: "Reverted" }));
    expect(result.score).toBe(100);
    expect(result.flags).toContain("SIMULATION_FAILED");
  });

  it("flags UNLIMITED_APPROVAL for MaxUint256 approve", async () => {
    const MAX = BigInt(2 ** 256) - 1n;
    const result = await scoreRisk(
      makeReport({
        approvals: [
          {
            owner: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
            spender: "0x1234567890123456789012345678901234567890",
            amount: MAX,
            token: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
          },
        ],
      })
    );
    expect(result.flags).toContain("UNLIMITED_APPROVAL");
    expect(result.score).toBeGreaterThanOrEqual(40);
  });

  it("flags SELF_DESTRUCT when opcode present", async () => {
    const result = await scoreRisk(makeReport({ opcodes: ["PUSH1", "SELFDESTRUCT"] }));
    expect(result.flags).toContain("SELF_DESTRUCT");
    expect(result.score).toBeGreaterThanOrEqual(80);
  });

  it("flags DELEGATECALL_TO_EOA", async () => {
    const result = await scoreRisk(
      makeReport({
        delegateCalls: [
          {
            from: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
            to: "0x1234567890123456789012345678901234567890",
            targetIsEOA: true,
          },
        ],
      })
    );
    expect(result.flags).toContain("DELEGATECALL_TO_EOA");
    expect(result.score).toBeGreaterThanOrEqual(70);
  });

  it("flags HIGH_GAS for gas > 500k", async () => {
    const result = await scoreRisk(makeReport({ gasEstimate: 600_000n }));
    expect(result.flags).toContain("HIGH_GAS");
  });

  it("flags OWNERSHIP_TRANSFER for known topic", async () => {
    const TOPIC = "0x8be0079c531659141344cd1fd0a4f28419497f9722a3daafe3b4186f6b6457e0";
    const result = await scoreRisk(
      makeReport({
        eventLogs: [
          {
            address: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
            topic0: TOPIC as `0x${string}`,
            data: "0x",
          },
        ],
      })
    );
    expect(result.flags).toContain("OWNERSHIP_TRANSFER");
  });

  it("accumulates multiple flags but caps at 100", async () => {
    const MAX = BigInt(2 ** 256) - 1n;
    const result = await scoreRisk(
      makeReport({
        approvals: [
          {
            owner: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
            spender: "0x1234567890123456789012345678901234567890",
            amount: MAX,
            token: "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
          },
        ],
        opcodes: ["SELFDESTRUCT"],
        delegateCalls: [
          {
            from: "0x742d35Cc6634C0532925a3b8D4C9cF55B6E9e54b",
            to: "0x1234567890123456789012345678901234567890",
            targetIsEOA: true,
          },
        ],
      })
    );
    expect(result.score).toBe(100); // capped
    expect(result.flags.length).toBeGreaterThan(1);
  });
});

describe("isAutoApprovable", () => {
  it("returns true for score below threshold", () => {
    expect(isAutoApprovable(20, 30)).toBe(true);
    expect(isAutoApprovable(29, 30)).toBe(true);
  });

  it("returns false for score at or above threshold", () => {
    expect(isAutoApprovable(30, 30)).toBe(false);
    expect(isAutoApprovable(50, 30)).toBe(false);
  });
});

describe("requiresApproval", () => {
  it("returns true for high-risk score", () => {
    expect(requiresApproval(70, 70)).toBe(true);
    expect(requiresApproval(100, 70)).toBe(true);
  });

  it("returns false for acceptable score", () => {
    expect(requiresApproval(69, 70)).toBe(false);
    expect(requiresApproval(0, 70)).toBe(false);
  });
});
