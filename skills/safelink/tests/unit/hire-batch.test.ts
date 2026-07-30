import { describe, it, expect } from "vitest";
import { safe_hire_agents_batch } from "../../src/tools/hire_batch.js";

const item = {
  target_id: "0x" + "ab".repeat(20),
  task_description: "Analyze BTC trend",
  payment_model: "per_request" as const,
  rate: 0.01,
};

describe("safe_hire_agents_batch", () => {
  it("continues on failures when failure_policy=continue", async () => {
    let call = 0;
    const result = await safe_hire_agents_batch(
      {
        hires: [item, item, item],
        failure_policy: "continue",
        max_concurrency: 2,
        batch_idempotency_key: "batch-test-1",
      },
      {
        hireAgent: async () => {
          call += 1;
          if (call === 2) throw new Error("boom");
          return {
            task_id: `t-${call}`,
            escrow_id: "0x" + "cd".repeat(32),
            result: { ok: true },
            proof_hash: "0x" + "ef".repeat(32),
            status: "completed",
            reputation_score_at_hire: 80,
            amount_paid_usdc: 0.01,
            idempotency_key: `item-${call}`,
          };
        },
      }
    );

    expect(result.status).toBe("partial");
    expect(result.total).toBe(3);
    expect(result.succeeded).toBe(2);
    expect(result.failed).toBe(1);
    expect(result.skipped).toBe(0);
  });

  it("halts on first failure when failure_policy=halt", async () => {
    let call = 0;
    const result = await safe_hire_agents_batch(
      {
        hires: [item, item, item, item],
        failure_policy: "halt",
        max_concurrency: 1,
        batch_idempotency_key: "batch-test-2",
      },
      {
        hireAgent: async () => {
          call += 1;
          if (call === 2) throw new Error("stop");
          return {
            task_id: `t-${call}`,
            escrow_id: "0x" + "cd".repeat(32),
            result: { ok: true },
            proof_hash: "0x" + "ef".repeat(32),
            status: "completed",
            reputation_score_at_hire: 80,
            amount_paid_usdc: 0.01,
            idempotency_key: `item-${call}`,
          };
        },
      }
    );

    expect(result.failed).toBe(1);
    expect(result.succeeded).toBe(1);
    expect(result.skipped).toBe(2);
    expect(result.results[2]?.skipped).toBe(true);
  });

  it("succeeds with no idempotency keys (auto-derives none)", async () => {
    // Exercises the branch where both item.idempotency_key and
    // batch_idempotency_key are absent (derivedKey = undefined).
    const result = await safe_hire_agents_batch(
      {
        hires: [item],
        failure_policy: "continue",
        max_concurrency: 1,
        // no batch_idempotency_key
      },
      {
        hireAgent: async () => ({
          task_id: "t-1",
          escrow_id: "0x" + "cd".repeat(32),
          result: { ok: true },
          proof_hash: "0x" + "ef".repeat(32),
          status: "completed",
          reputation_score_at_hire: 80,
          amount_paid_usdc: 0.01,
          idempotency_key: "auto",
        }),
      }
    );

    expect(result.status).toBe("completed");
    expect(result.succeeded).toBe(1);
  });
});
