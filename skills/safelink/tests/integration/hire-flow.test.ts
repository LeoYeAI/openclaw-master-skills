/**
 * Integration test: end-to-end hire flow on Base Sepolia.
 *
 * This test requires:
 *   - BASE_RPC_URL pointing to Base Sepolia
 *   - PRIVY_APP_ID + PRIVY_APP_SECRET
 *   - ERC8004_REGISTRY_ADDRESS + SAFE_ESCROW_ADDRESS (from `npm run deploy:contracts`)
 *   - Agent wallet funded with Base Sepolia ETH and USDC
 *   - RUN_LIVE_INTEGRATION=1
 *
 * Run with:
 *   RUN_LIVE_INTEGRATION=1 npm run test:integration
 *
 * Safety gate:
 *   The suite only runs when RUN_LIVE_INTEGRATION=1 and all required env vars are set.
 */

import { describe, it, expect, beforeAll } from "vitest";

const REQUIRED_ENV = [
  "BASE_RPC_URL",
  "PRIVY_APP_ID",
  "PRIVY_APP_SECRET",
  "ERC8004_REGISTRY_ADDRESS",
  "SAFE_ESCROW_ADDRESS",
] as const;

const hasRequiredEnv = REQUIRED_ENV.every((key) => Boolean(process.env[key]));
const liveEnabled = process.env["RUN_LIVE_INTEGRATION"] === "1";
const SKIP = !liveEnabled || !hasRequiredEnv;

describe.skipIf(SKIP)("hire flow integration", () => {
  beforeAll(() => {
    if (!liveEnabled) {
      throw new Error(
        "Integration tests require RUN_LIVE_INTEGRATION=1. Refusing to run live chain tests by default."
      );
    }

    const missing = REQUIRED_ENV.filter((key) => !process.env[key]);
    if (missing.length > 0) {
      throw new Error(`Missing required env vars for integration tests: ${missing.join(", ")}`);
    }
  });

  it("registers an agent and verifies on-chain record", async () => {
    const { safe_register_as_service } = await import("../../src/tools/register.js");

    const result = await safe_register_as_service({
      capabilities: ["integration-test", "endpoint:http://localhost:4242"],
      min_rate: 0.01,
      policy: {
        max_task_seconds: 60,
        allowed_chains: ["base-sepolia"],
        require_escrow: true,
        max_rate_usdc: 1,
        auto_approve_below_risk: 50,
      },
      confirmed: true,
    });

    expect(result.agent_id).toMatch(/^0x[a-fA-F0-9]{40}$/);
    expect(result.tx_hash).toMatch(/^0x[a-fA-F0-9]{64}$/);
    expect(result.capabilities).toContain("integration-test");
  }, 60_000);

  it("fetches reputation for registered agent", async () => {
    const { getAgentAddress } = await import("../../src/wallet/mpc.js");
    const { fetchAgentReputation } = await import("../../src/registry/reputation.js");

    const address = await getAgentAddress();
    const rep = await fetchAgentReputation(address);

    expect(rep.score).toBeGreaterThanOrEqual(0);
    expect(rep.score).toBeLessThanOrEqual(100);
    expect(rep.active).toBe(true);
  }, 30_000);

  it("executes a safe tx (gas estimation only on testnet)", async () => {
    const { safe_execute_tx } = await import("../../src/tools/execute_tx.js");

    // Simulate a zero-value transfer to self — low risk, should auto-approve
    const { getAgentAddress } = await import("../../src/wallet/mpc.js");
    const addr = await getAgentAddress();

    const result = await safe_execute_tx({
      intent_description: `Transfer 0 ETH to myself at ${addr}`,
      confirmed: false,
    });

    // Should either broadcast or be blocked by simulation — not crash
    expect(["broadcast", "blocked", "simulation_failed", "rejected_by_user"]).toContain(
      result.status
    );
  }, 60_000);
});

// ── Unit-style integration tests (no wallet needed) ───────────────────────────

describe("session lifecycle", () => {
  it("creates and destroys a session", async () => {
    const { createTempSession, getSession, destroySession } = await import(
      "../../src/security/session.js"
    );

    const session = createTempSession({ tool: "test" });
    expect(session.id).toHaveLength(32); // 16 bytes hex

    const found = getSession(session.id);
    expect(found).toBeDefined();
    expect(found?.tool).toBe("test");

    await destroySession(session.id);
    expect(getSession(session.id)).toBeUndefined();
  });

  it("session context is cleared on destroy", async () => {
    const { createTempSession, destroySession } = await import(
      "../../src/security/session.js"
    );

    const session = createTempSession({ tool: "test" });
    session.context.set("sensitiveKey", "sensitiveValue");
    expect(session.context.get("sensitiveKey")).toBe("sensitiveValue");

    await destroySession(session.id);
    expect(session.context.size).toBe(0);
  });
});
