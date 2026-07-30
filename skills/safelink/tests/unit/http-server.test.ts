/**
 * HTTP task server unit tests.
 *
 * Tests the routing, request validation, and response structure of the
 * task server without making real blockchain calls.
 *
 * Strategy: start the server on a random port, send raw HTTP requests,
 * assert on status codes and response shapes.
 */

import { describe, it, expect, beforeAll, afterAll, vi } from "vitest";
import { startTaskServer, type TaskServer } from "../../src/server/http.js";
import { buildSignedTaskHeaders } from "../../src/security/request-auth.js";

const mocks = vi.hoisted(() => ({
  getConfig: vi.fn().mockReturnValue({
    ANTHROPIC_API_KEY: "test-key",
    PRIVY_APP_ID: "test-privy-id",
    PRIVY_APP_SECRET: "test-privy-secret",
    BASE_RPC_URL: "https://sepolia.base.org",
    X402_FACILITATOR_URL: "https://x402.org/facilitator",
    AUTONOMYS_NETWORK: "taurus-testnet",
    NODE_ENV: "test",
    LOG_LEVEL: "error",
    RISK_APPROVAL_THRESHOLD: 70,
    MIN_REPUTATION_SCORE: 70,
    TASK_SERVER_PORT: 0,
    TASK_AUTH_REQUIRED: false,
    TASK_AUTH_SHARED_SECRET: undefined,
    TASK_AUTH_MAX_SKEW_SECONDS: 300,
    TENDERLY_PROJECT_SLUG: "safechain-agent",
    AGENT_NAME: "test-agent",
  }),
}));

// 鈹€鈹€ Mock heavy dependencies 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

vi.mock("../../src/wallet/mpc.js", () => ({
  getAgentAddress: vi.fn().mockResolvedValue("0xDeAdBeEf00000000000000000000000000000001"),
  getMPCWalletClient: vi.fn(),
}));

vi.mock("../../src/tools/generate_agent_card.js", () => ({
  generate_agent_card: vi.fn().mockResolvedValue({
    card_json: {
      version: "1.0",
      agent_id: "0xDeAdBeEf00000000000000000000000000000001",
      owner: "0xDeAdBeEf00000000000000000000000000000001",
      active: true,
      capabilities: ["code-audit"],
      min_rate_usdc: 0.05,
      reputation: { score: 88, on_chain_score: 80, flags: [] },
      analytics_30d: { total_hires: 5, success_rate: 1, total_spent_usdc: 0.25 },
    },
  }),
}));

vi.mock("../../src/utils/config.js", () => ({
  getConfig: mocks.getConfig,
}));

vi.mock("../../src/utils/logger.js", () => ({
  logger: { info: vi.fn(), warn: vi.fn(), error: vi.fn(), debug: vi.fn() },
}));

// 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

async function get(server: TaskServer, path: string): Promise<{ status: number; body: unknown }> {
  const res = await fetch(`http://localhost:${server.port}${path}`);
  const body = await res.json();
  return { status: res.status, body };
}

async function post(
  server: TaskServer,
  path: string,
  headers: Record<string, string>,
  body: unknown
): Promise<{ status: number; body: unknown }> {
  const res = await fetch(`http://localhost:${server.port}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...headers },
    body: JSON.stringify(body),
  });
  const resBody = await res.json();
  return { status: res.status, body: resBody };
}

// 鈹€鈹€ Tests 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

describe("HTTP Task Server", () => {
  let server: TaskServer;

  beforeAll(async () => {
    // Port 0 鈫?OS assigns a free port
    server = await startTaskServer(0);
  });

  afterAll(async () => {
    await server.close();
  });

  // 鈹€鈹€ GET /health 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

  describe("GET /health", () => {
    it("returns 200 with agent address and status ok", async () => {
      const { status, body } = await get(server, "/health");
      expect(status).toBe(200);
      expect((body as Record<string, unknown>)["status"]).toBe("ok");
      expect((body as Record<string, unknown>)["agent"]).toMatch(/^0x[a-fA-F0-9]{40}$/i);
      expect((body as Record<string, unknown>)["server"]).toBe("SafeLink");
    });
  });

  // ── GET /.well-known/agent-card.json ──────────────────────────────────────

  describe("GET /.well-known/agent-card.json", () => {
    it("returns 200 with agent card JSON", async () => {
      const { status, body } = await get(server, "/.well-known/agent-card.json");
      expect(status).toBe(200);
      const b = body as Record<string, unknown>;
      expect(b["version"]).toBe("1.0");
      expect(b["agent_id"]).toMatch(/^0x[a-fA-F0-9]{40}$/i);
      expect(b["active"]).toBe(true);
    });

    it("returns 503 when agent card generation fails", async () => {
      const { generate_agent_card } = await import("../../src/tools/generate_agent_card.js");
      vi.mocked(generate_agent_card).mockRejectedValueOnce(new Error("not registered"));
      const { status, body } = await get(server, "/.well-known/agent-card.json");
      expect(status).toBe(503);
      expect((body as Record<string, unknown>)["error"]).toMatch(/unavailable/i);
    });
  });

  // 鈹€鈹€ Unknown routes 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

  describe("unknown routes", () => {
    it("GET /unknown 鈫?404", async () => {
      const { status } = await get(server, "/unknown");
      expect(status).toBe(404);
    });

    it("GET /task 鈫?404 (wrong method)", async () => {
      const { status } = await get(server, "/task");
      expect(status).toBe(404);
    });
  });

  // 鈹€鈹€ POST /task 鈥?header validation 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

  describe("POST /task 鈥?missing headers", () => {
    it("no X-Payment-Receipt 鈫?402", async () => {
      const { status, body } = await post(server, "/task", {}, {});
      expect(status).toBe(402);
      expect((body as Record<string, unknown>)["error"]).toMatch(/[Pp]ayment/);
    });

    it("has X-Payment-Receipt but missing X-Escrow-Id 鈫?400", async () => {
      const { status, body } = await post(
        server,
        "/task",
        { "X-Payment-Receipt": "receipt-token" },
        {}
      );
      expect(status).toBe(400);
      expect((body as Record<string, unknown>)["error"]).toMatch(/[Bb]ad request/);
    });

    it("invalid escrow ID format 鈫?400", async () => {
      const { status } = await post(
        server,
        "/task",
        {
          "X-Payment-Receipt": "receipt-token",
          "X-Escrow-Id": "not-a-valid-id",
        },
        {}
      );
      expect(status).toBe(400);
    });
  });

  // 鈹€鈹€ POST /task 鈥?body validation 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

  describe("POST /task 鈥?invalid body", () => {
    const validHeaders = {
      "X-Payment-Receipt": "receipt-token",
      "X-Escrow-Id": "0x" + "ab".repeat(32),
    };

    it("non-JSON body 鈫?400", async () => {
      const res = await fetch(`http://localhost:${server.port}/task`, {
        method: "POST",
        headers: { "Content-Type": "text/plain", ...validHeaders },
        body: "not json",
      });
      expect(res.status).toBe(400);
    });

    it("missing task_description 鈫?400", async () => {
      const { status } = await post(server, "/task", validHeaders, {
        payer: "0x" + "ab".repeat(20),
        amount_atomic_usdc: "1000000",
        session_id: "sess-abc",
      });
      expect(status).toBe(400);
    });

    it("missing session_id 鈫?400", async () => {
      const { status } = await post(server, "/task", validHeaders, {
        task_description: "Do something",
        payer: "0x" + "ab".repeat(20),
        amount_atomic_usdc: "1000000",
        // session_id omitted
      });
      expect(status).toBe(400);
    });

    it("invalid payer address 鈫?400", async () => {
      const { status } = await post(server, "/task", validHeaders, {
        task_description: "Do something",
        payer: "not-an-address",
        amount_atomic_usdc: "1000000",
        session_id: "sess-abc",
      });
      expect(status).toBe(400);
    });

    it("invalid amount_atomic_usdc 鈫?400", async () => {
      const { status } = await post(server, "/task", validHeaders, {
        task_description: "Do something",
        payer: "0x" + "ab".repeat(20),
        amount_atomic_usdc: "not-a-number",
        session_id: "sess-abc",
      });
      expect(status).toBe(400);
    });
  });

  describe("POST /task - signed auth", () => {
    const baseHeaders = {
      "X-Payment-Receipt": "receipt-token",
      "X-Escrow-Id": "0x" + "ab".repeat(32),
    };

    const validBody = {
      task_description: "Do something",
      payer: "0x" + "ab".repeat(20),
      amount_atomic_usdc: "1000000",
      session_id: "a".repeat(32),
    };

    it("returns 401 when auth is required but signature headers are missing", async () => {
      mocks.getConfig.mockReturnValueOnce({
        ...mocks.getConfig(),
        TASK_AUTH_REQUIRED: true,
        TASK_AUTH_SHARED_SECRET: "s".repeat(48),
      });

      const { status } = await post(server, "/task", baseHeaders, validBody);
      expect(status).toBe(401);
    });

    it("accepts valid signed headers when auth is required", async () => {
      const secret = "s".repeat(48);
      mocks.getConfig.mockReturnValueOnce({
        ...mocks.getConfig(),
        TASK_AUTH_REQUIRED: true,
        TASK_AUTH_SHARED_SECRET: secret,
      });

      const rawBody = JSON.stringify({
        ...validBody,
        payer: "not-an-address", // force 400 after auth passes
      });
      const signed = buildSignedTaskHeaders({
        escrowId: baseHeaders["X-Escrow-Id"],
        paymentReceipt: baseHeaders["X-Payment-Receipt"],
        rawBody,
        sharedSecret: secret,
      });

      const res = await fetch(`http://localhost:${server.port}/task`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...baseHeaders,
          ...signed,
        },
        body: rawBody,
      });

      expect(res.status).toBe(400);
    });
  });

  describe("POST /task - SIWx auth", () => {
    const baseHeaders = {
      "X-Payment-Receipt": "receipt-token",
      "X-Escrow-Id": "0x" + "ab".repeat(32),
    };

    const validBody = {
      task_description: "Do something",
      payer: "0x" + "ab".repeat(20),
      amount_atomic_usdc: "1000000",
      session_id: "a".repeat(32),
    };

    it("returns 401 when SIWx is required but assertion header is missing", async () => {
      const cfg = {
        ...mocks.getConfig(),
        SIWX_REQUIRED: true,
        SIWX_VERIFIER_URL: "https://verifier.example.com/siwx/verify",
      };
      mocks.getConfig.mockReturnValueOnce(cfg);
      mocks.getConfig.mockReturnValueOnce(cfg);

      const { status } = await post(server, "/task", baseHeaders, validBody);
      expect(status).toBe(401);
    });
  });
});

