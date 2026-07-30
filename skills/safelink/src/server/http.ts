/**
 * SafeLink 鈥?HTTP Task Server
 *
 * Exposes a lightweight HTTP endpoint that hiring agents call to deliver
 * tasks. This runs as a background server alongside the MCP stdio transport.
 *
 * Endpoints:
 *   POST /task      鈥?receive and execute a task (requires x402 payment proof)
 *   GET  /health    鈥?readiness check (returns agent address + status)
 *
 * Security model:
 *   1. X-Payment-Receipt header is verified against x402 facilitator before
 *      any task work begins. Invalid or insufficient receipts 鈫?402.
 *   2. Each request runs in a temporary session, destroyed on completion.
 *   3. All request bodies are size-limited (64 KB) to prevent DoS.
 *   4. No private keys or secrets are ever included in responses.
 */

import { createServer, type IncomingMessage, type ServerResponse } from "node:http";
import { processIncomingTask, type IncomingTask } from "../tools/listen.js";
import { getAgentAddress } from "../wallet/mpc.js";
import { getConfig } from "../utils/config.js";
import { logger } from "../utils/logger.js";
import { toError } from "../utils/errors.js";
import { verifySignedTaskRequest } from "../security/request-auth.js";
import { verifySIWxAssertion } from "../security/siwx.js";
import { generate_agent_card } from "../tools/generate_agent_card.js";

// 鈹€鈹€ Constants 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const MAX_BODY_BYTES = 64 * 1024; // 64 KB
const MAX_TASK_DESCRIPTION_CHARS = 2_000;
const MAX_AMOUNT_ATOMIC_USDC = 1_000_000_000_000n; // 1,000,000 USDC @ 6 decimals

// HIGH-02: concurrency cap prevents API rate limit exhaustion under burst load.
// Each task calls Anthropic API 鈥?at Tier 1 rate limits, 10 concurrent is safe.
const MAX_CONCURRENT_TASKS = Number(process.env["MAX_CONCURRENT_TASKS"] ?? "10");

let _activeTasks = 0;

// 鈹€鈹€ Helpers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

function json(res: ServerResponse, status: number, body: unknown): void {
  const payload = JSON.stringify(body);
  res.writeHead(status, {
    "Content-Type": "application/json",
    "Content-Length": Buffer.byteLength(payload),
    "X-Content-Type-Options": "nosniff",
  });
  res.end(payload);
}

async function readBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let data = "";
    let bytes = 0;

    req.on("data", (chunk: Buffer) => {
      bytes += chunk.length;
      if (bytes > MAX_BODY_BYTES) {
        reject(new Error("Request body too large"));
        req.destroy();
        return;
      }
      data += chunk.toString("utf8");
    });

    req.on("end", () => resolve(data));
    req.on("error", reject);
  });
}

// 鈹€鈹€ Request handlers 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

async function handleHealth(res: ServerResponse): Promise<void> {
  const agentAddress = await getAgentAddress();
  json(res, 200, {
    status: "ok",
    agent: agentAddress,
    server: "SafeLink",
    version: "0.1.0",
  });
}

async function handleAgentCard(res: ServerResponse): Promise<void> {
  try {
    const { card_json } = await generate_agent_card({ include_markdown: false });
    json(res, 200, card_json);
  } catch (err) {
    const e = toError(err);
    logger.warn({ event: "agent_card_error", message: e.message });
    json(res, 503, { error: "Agent card unavailable", detail: "Agent not yet registered on-chain." });
  }
}

async function handleTask(req: IncomingMessage, res: ServerResponse): Promise<void> {
  // HIGH-02: concurrency cap 鈥?prevents Anthropic API exhaustion under burst load
  if (_activeTasks >= MAX_CONCURRENT_TASKS) {
    json(res, 429, {
      error: "Too Many Requests",
      detail: `Maximum ${MAX_CONCURRENT_TASKS} concurrent tasks. Retry after current tasks complete.`,
      retry_after_seconds: 30,
    });
    return;
  }
  _activeTasks++;

  try {
    await _handleTaskInner(req, res);
  } finally {
    _activeTasks--;
  }
}

async function _handleTaskInner(req: IncomingMessage, res: ServerResponse): Promise<void> {
  // 1. Parse headers
  const paymentReceipt = req.headers["x-payment-receipt"];
  const escrowId = req.headers["x-escrow-id"];
  const taskId = req.headers["x-task-id"] ?? crypto.randomUUID();

  if (!paymentReceipt || typeof paymentReceipt !== "string") {
    json(res, 402, {
      error: "Payment required",
      detail: "Missing X-Payment-Receipt header. Send an x402 payment receipt.",
    });
    return;
  }

  if (!escrowId || typeof escrowId !== "string") {
    json(res, 400, {
      error: "Bad request",
      detail: "Missing X-Escrow-Id header. Include the SafeEscrow deposit ID.",
    });
    return;
  }

  // Validate escrow ID format
  if (!/^0x[a-fA-F0-9]{64}$/.test(escrowId)) {
    json(res, 400, {
      error: "Bad request",
      detail: "X-Escrow-Id must be a 32-byte hex string (0x + 64 hex chars).",
    });
    return;
  }

  // 2. Parse body
  let body: unknown;
  let rawBody = "";
  try {
    rawBody = await readBody(req);
    body = JSON.parse(rawBody);
  } catch (err) {
    json(res, 400, { error: "Bad request", detail: "Body must be valid JSON (max 64 KB)." });
    return;
  }

  try {
    const cfg = getConfig();
    await verifySignedTaskRequest({
      escrowId,
      paymentReceipt,
      rawBody,
      ...(typeof req.headers["x-safelink-signature"] === "string"
        ? { signature: req.headers["x-safelink-signature"] }
        : {}),
      ...(typeof req.headers["x-safelink-timestamp"] === "string"
        ? { timestamp: req.headers["x-safelink-timestamp"] }
        : {}),
      ...(typeof req.headers["x-safelink-nonce"] === "string"
        ? { nonce: req.headers["x-safelink-nonce"] }
        : {}),
      config: {
        required: cfg.TASK_AUTH_REQUIRED,
        ...(cfg.TASK_AUTH_SHARED_SECRET !== undefined
          ? { sharedSecret: cfg.TASK_AUTH_SHARED_SECRET }
          : {}),
        maxSkewSeconds: cfg.TASK_AUTH_MAX_SKEW_SECONDS,
      },
    });
  } catch (err) {
    json(res, 401, {
      error: "Unauthorized",
      detail: "Invalid or missing SafeLink request signature headers.",
    });
    return;
  }

  if (
    typeof body !== "object" ||
    body === null ||
    typeof (body as Record<string, unknown>)["task_description"] !== "string" ||
    typeof (body as Record<string, unknown>)["payer"] !== "string" ||
    typeof (body as Record<string, unknown>)["amount_atomic_usdc"] !== "string" ||
    typeof (body as Record<string, unknown>)["session_id"] !== "string"
  ) {
    json(res, 400, {
      error: "Bad request",
      detail:
        "Body must include: task_description (string), payer (0x address), " +
        "amount_atomic_usdc (string bigint), session_id (string).",
    });
    return;
  }

  const b = body as Record<string, string>;

  // Validate payer address
  if (!/^0x[a-fA-F0-9]{40}$/.test(b["payer"]!)) {
    json(res, 400, { error: "Bad request", detail: "payer must be a valid EVM address." });
    return;
  }

  // Validate session_id is non-empty
  if (!/^[a-f0-9]{32}$/.test(b["session_id"] ?? "")) {
    json(res, 400, { error: "Bad request", detail: "session_id must be 32 lowercase hex characters." });
    return;
  }

  if ((b["task_description"] ?? "").length > MAX_TASK_DESCRIPTION_CHARS) {
    json(res, 400, {
      error: "Bad request",
      detail: `task_description exceeds ${MAX_TASK_DESCRIPTION_CHARS} characters.`,
    });
    return;
  }

  // 3. Build IncomingTask
  let amountAtomicUSDC: bigint;
  try {
    amountAtomicUSDC = BigInt(b["amount_atomic_usdc"]!);
  } catch {
    json(res, 400, { error: "Bad request", detail: "amount_atomic_usdc must be a valid integer string." });
    return;
  }
  if (amountAtomicUSDC <= 0n) {
    json(res, 400, { error: "Bad request", detail: "amount_atomic_usdc must be > 0." });
    return;
  }
  if (amountAtomicUSDC > MAX_AMOUNT_ATOMIC_USDC) {
    json(res, 400, {
      error: "Bad request",
      detail: "amount_atomic_usdc exceeds configured safety limit.",
    });
    return;
  }

  const task: IncomingTask = {
    taskId: typeof taskId === "string" ? taskId : String(taskId),
    payer: b["payer"]! as `0x${string}`,
    escrowId: escrowId as `0x${string}`,
    taskDescription: b["task_description"]!,
    paymentReceipt,
    amountAtomicUSDC,
    hirerSessionId: b["session_id"]!,
  };

  const cfg = getConfig();
  if (cfg.SIWX_REQUIRED) {
    const siwxAssertion = req.headers["x-siwx-assertion"];
    if (!siwxAssertion || typeof siwxAssertion !== "string") {
      json(res, 401, {
        error: "Unauthorized",
        detail: "Missing X-SIWx-Assertion header.",
      });
      return;
    }

    try {
      await verifySIWxAssertion({
        assertion: siwxAssertion,
        payer: task.payer,
        taskId: task.taskId,
        verifierUrl: cfg.SIWX_VERIFIER_URL!,
      });
    } catch {
      json(res, 401, {
        error: "Unauthorized",
        detail: "SIWx assertion verification failed.",
      });
      return;
    }
  }

  // 4. Process task (payment verification happens inside processIncomingTask)
  try {
    const result = await processIncomingTask(task);

    json(res, 200, {
      task_id: task.taskId,
      proof_hash: result.proof_hash,
      output: result.output,
    });

    logger.info({
      event: "http_task_complete",
      taskId: task.taskId,
      payer: task.payer,
      proof_hash: result.proof_hash,
    });
  } catch (err) {
    const e = toError(err);
    const isPaymentError = e.message.includes("Invalid") || e.message.includes("payment");
    const status = isPaymentError ? 402 : 500;

    logger.warn({
      event: "http_task_error",
      taskId: task.taskId,
      status,
      message: e.message,
    });

    // MED-04: never leak full internal error message to caller
    json(res, status, {
      error: isPaymentError ? "Payment verification failed" : "Task execution failed",
      // Safe detail: only expose sanitized reason, not full stack/internals
      detail: isPaymentError
        ? "Payment receipt invalid or insufficient. Retry with valid x402 receipt."
        : "Task could not be completed. Check agent logs for details.",
    });
  }
}

// 鈹€鈹€ Server lifecycle 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

export interface TaskServer {
  port: number;
  address: string;
  close(): Promise<void>;
}

/**
 * Start the HTTP task server.
 *
 * @param port  TCP port to listen on. Defaults to TASK_SERVER_PORT env var or 3402.
 * @returns     Server handle with address and close() method.
 */
export async function startTaskServer(port?: number): Promise<TaskServer> {
  const config = getConfig();
  const listenPort = port ?? config.TASK_SERVER_PORT;

  const server = createServer(async (req: IncomingMessage, res: ServerResponse) => {
    const method = req.method ?? "GET";
    const url = req.url ?? "/";

    try {
      if (method === "GET" && url === "/health") {
        await handleHealth(res);
      } else if (method === "GET" && url === "/.well-known/agent-card.json") {
        await handleAgentCard(res);
      } else if (method === "POST" && url === "/task") {
        await handleTask(req, res);
      } else {
        json(res, 404, { error: "Not found", detail: `${method} ${url} is not a valid endpoint.` });
      }
    } catch (err) {
      const e = toError(err);
      logger.error({ event: "http_server_error", message: e.message });
      if (!res.headersSent) {
        json(res, 500, { error: "Internal server error" });
      }
    }
  });

  await new Promise<void>((resolve, reject) => {
    server.listen(listenPort, "127.0.0.1", resolve);
    server.once("error", reject);
  });

  // When port=0, the OS assigns a free port. Retrieve the actual bound port.
  const bound = server.address();
  const actualPort =
    bound !== null && typeof bound === "object" ? bound.port : listenPort;
  const addr = `http://127.0.0.1:${actualPort}`;

  logger.info({ event: "task_server_started", address: addr });

  return {
    port: actualPort,
    address: addr,
    close: () =>
      new Promise<void>((resolve, reject) =>
        server.close((err) => (err ? reject(err) : resolve()))
      ),
  };
}

/**
 * Start the task server and print the endpoint to stdout so the agent's
 * capability string can be auto-populated on first run.
 */
export async function startTaskServerAndLog(port?: number): Promise<TaskServer> {
  const srv = await startTaskServer(port);
  process.stdout.write(
    `[SafeLink] Task server listening on ${srv.address}\n` +
      `[SafeLink] Register with capability: endpoint:${srv.address}/task\n`
  );
  return srv;
}


