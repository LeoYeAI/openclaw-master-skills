import { describe, it, expect, vi, beforeEach } from "vitest";
import { encodePacked, keccak256 } from "viem";

const mocks = vi.hoisted(() => ({
  getEscrowRecord: vi.fn(),
  fetchAgentReputation: vi.fn(),
  getConfig: vi.fn(() => ({ MIN_REPUTATION_SCORE: 70 })),
  getAgentAddress: vi.fn(async () => "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"),
  getAgentRecord: vi.fn(),
  getHireSummary: vi.fn(),
}));

vi.mock("../../src/payments/escrow.js", () => ({
  getEscrowRecord: mocks.getEscrowRecord,
}));

vi.mock("../../src/registry/reputation.js", () => ({
  fetchAgentReputation: mocks.fetchAgentReputation,
}));

vi.mock("../../src/utils/config.js", () => ({
  getConfig: mocks.getConfig,
}));

vi.mock("../../src/wallet/mpc.js", () => ({
  getAgentAddress: mocks.getAgentAddress,
}));

vi.mock("../../src/registry/erc8004.js", () => ({
  getAgentRecord: mocks.getAgentRecord,
}));

vi.mock("../../src/analytics/store.js", () => ({
  getHireSummary: mocks.getHireSummary,
}));

import { verify_task_proof } from "../../src/tools/verify_task_proof.js";
import { get_agent_reputation } from "../../src/tools/get_reputation.js";
import { generate_agent_card } from "../../src/tools/generate_agent_card.js";
import { agent_analytics_summary } from "../../src/tools/analytics_summary.js";

describe("tooling coverage suite", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("verify_task_proof", () => {
    it("verifies local and on-chain proof match", async () => {
      const sessionId = "a".repeat(32);
      const agentId = "0x1111111111111111111111111111111111111111";
      const proof = keccak256(encodePacked(["string", "address"], [sessionId, agentId]));

      mocks.getEscrowRecord.mockResolvedValueOnce({
        proofCommitment: proof,
        status: "active",
      });

      const out = await verify_task_proof({
        escrow_id: "0x" + "ab".repeat(32),
        session_id: sessionId,
        agent_id: agentId,
        proof_hash: proof,
        check_onchain: true,
      });

      expect(out.verified).toBe(true);
      expect(out.local_match).toBe(true);
      expect(out.onchain_match).toBe(true);
      expect(out.escrow_status).toBe("active");
    });

    it("returns partial verification state when on-chain check disabled", async () => {
      const sessionId = "b".repeat(32);
      const agentId = "0x1111111111111111111111111111111111111111";
      const proof = keccak256(encodePacked(["string", "address"], [sessionId, agentId]));

      const out = await verify_task_proof({
        escrow_id: "0x" + "cd".repeat(32),
        session_id: sessionId,
        agent_id: agentId,
        proof_hash: proof,
        check_onchain: false,
        zk_proof: "dummy-zk",
        tee_attestation: "dummy-tee",
      });

      expect(out.verified).toBe(true);
      expect(out.onchain_match).toBeUndefined();
      expect(out.zk_hook).toBe("received_not_verified");
      expect(out.tee_hook).toBe("received_not_verified");
    });

    it("fails validation for malformed session id", async () => {
      await expect(
        verify_task_proof({
          escrow_id: "0x" + "ab".repeat(32),
          session_id: "not-hex-32",
          agent_id: "0x1111111111111111111111111111111111111111",
          proof_hash: "0x" + "ef".repeat(32),
        })
      ).rejects.toThrow(/validation/i);
    });
  });

  describe("get_agent_reputation", () => {
    it("returns threshold result with default threshold", async () => {
      mocks.fetchAgentReputation.mockResolvedValueOnce({
        score: 75,
        onChainScore: 80,
        flags: ["NEW_AGENT"],
        active: true,
        capabilities: ["audit"],
        minRateUSDC: 0.05,
      });

      const out = await get_agent_reputation({
        agent_id: "0x1111111111111111111111111111111111111111",
      });

      expect(out.threshold).toBe(70);
      expect(out.meets_threshold).toBe(true);
      expect(out.flags).toContain("NEW_AGENT");
    });

    it("respects custom threshold", async () => {
      mocks.fetchAgentReputation.mockResolvedValueOnce({
        score: 65,
        onChainScore: 65,
        flags: [],
        active: true,
        capabilities: ["audit"],
        minRateUSDC: 0.05,
      });

      const out = await get_agent_reputation({
        agent_id: "0x1111111111111111111111111111111111111111",
        threshold: 70,
      });

      expect(out.meets_threshold).toBe(false);
      expect(out.threshold).toBe(70);
    });
  });

  describe("generate_agent_card", () => {
    it("generates JSON + markdown when include_markdown=true", async () => {
      mocks.getAgentRecord.mockResolvedValueOnce({
        owner: "0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        active: true,
        capabilities: ["audit", "endpoint:https://agent.example.com/task"],
        minRateAtomicUSDC: 50_000n,
      });
      mocks.fetchAgentReputation.mockResolvedValueOnce({
        score: 91,
        onChainScore: 93,
        flags: [],
        active: true,
        capabilities: ["audit"],
        minRateUSDC: 0.05,
      });
      mocks.getHireSummary.mockResolvedValueOnce({
        period_days: 30,
        total_hires: 10,
        completed: 9,
        refunded: 1,
        failed: 0,
        success_rate: 0.9,
        total_spent_usdc: 4.5,
        avg_spent_usdc: 0.45,
        top_targets: [],
      });

      const out = await generate_agent_card({});
      expect(out.card_json.agent_id).toBe("0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
      expect(out.card_markdown).toContain("SafeLink Agent Card");
      expect(out.card_json.reputation.score).toBe(91);
    });

    it("omits markdown when include_markdown=false", async () => {
      mocks.getAgentRecord.mockResolvedValueOnce({
        owner: "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        active: true,
        capabilities: [],
        minRateAtomicUSDC: 10_000n,
      });
      mocks.fetchAgentReputation.mockResolvedValueOnce({
        score: 50,
        onChainScore: 50,
        flags: ["NEW_AGENT"],
        active: true,
        capabilities: [],
        minRateUSDC: 0.01,
      });
      mocks.getHireSummary.mockResolvedValueOnce({
        period_days: 30,
        total_hires: 0,
        completed: 0,
        refunded: 0,
        failed: 0,
        success_rate: 0,
        total_spent_usdc: 0,
        avg_spent_usdc: 0,
        top_targets: [],
      });

      const out = await generate_agent_card({
        agent_id: "0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
        include_markdown: false,
      });
      expect(out.card_json.agent_id).toBe("0xbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb");
      expect("card_markdown" in out).toBe(false);
    });
  });

  describe("agent_analytics_summary", () => {
    it("returns summary and markdown with top targets", async () => {
      mocks.getHireSummary.mockResolvedValueOnce({
        period_days: 7,
        total_hires: 3,
        completed: 2,
        refunded: 1,
        failed: 0,
        success_rate: 0.6667,
        total_spent_usdc: 0.15,
        avg_spent_usdc: 0.05,
        top_targets: [
          { target_id: "0x1111111111111111111111111111111111111111", count: 2 },
          { target_id: "0x2222222222222222222222222222222222222222", count: 1 },
        ],
      });

      const out = await agent_analytics_summary({ period_days: 7 });
      expect(out.summary.total_hires).toBe(3);
      expect(out.markdown).toContain("Top Targets");
      expect(out.markdown).toContain("0x1111111111111111111111111111111111111111");
    });

    it("validates input bounds for period_days", async () => {
      await expect(agent_analytics_summary({ period_days: 0 })).rejects.toThrow(/validation/i);
      await expect(agent_analytics_summary({ period_days: 366 })).rejects.toThrow(/validation/i);
    });
  });
});

