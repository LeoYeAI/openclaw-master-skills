#!/usr/bin/env node
/**
 * SafeLink MCP Server entry point
 *
 * Registers MCP tools that can be called from Claude Desktop, Claude Code,
 * or any MCP-compatible host.
 *
 * Transport: stdio (standard MCP pattern)
 * Set MCP_SERVER=1 in env before calling to enable MCP-native approval flow.
 */

// Load .env before any config validation
import { config as loadDotenv } from "dotenv";
loadDotenv();

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  type Tool,
} from "@modelcontextprotocol/sdk/types.js";

import { safe_register_as_service } from "./tools/register.js";
import { safe_hire_agent } from "./tools/hire.js";
import { safe_hire_agents_batch } from "./tools/hire_batch.js";
import { safe_listen_for_hire } from "./tools/listen.js";
import { safe_execute_tx } from "./tools/execute_tx.js";
import { checkpoint_memory } from "./tools/checkpoint.js";
import { create_agentic_wallet } from "./tools/wallet.js";
import { setup_agentic_wallet } from "./tools/setup_wallet.js";
import { get_agent_reputation } from "./tools/get_reputation.js";
import { generate_agent_card } from "./tools/generate_agent_card.js";
import { verify_task_proof } from "./tools/verify_task_proof.js";
import { agent_analytics_summary } from "./tools/analytics_summary.js";
import { ApprovalRequiredError } from "./security/approval.js";
import { SafeChainError } from "./utils/errors.js";
import { logger } from "./utils/logger.js";

// Set flag so approval.ts knows to throw structured errors (not prompt stdin)
process.env["MCP_SERVER"] = "1";

// 鈹€鈹€ Tool definitions (shown to Claude in tool use) 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const TOOLS: Tool[] = [
  {
    name: "setup_agentic_wallet",
    description:
      "Create or load an MPC wallet for this agent (Coinbase AgentKit or Privy). " +
      "Private keys never leave the HSM. Returns wallet address, ETH balance, and USDC balance. " +
      "Run this first to fund your wallet before registering or hiring agents.",
    inputSchema: {
      type: "object",
      properties: {
        provider: {
          type: "string",
          enum: ["auto", "coinbase", "privy"],
          description:
            "'auto' = Coinbase if CDP keys set, else Privy. " +
            "'coinbase' = Coinbase AgentKit (recommended, portal.cdp.coinbase.com). " +
            "'privy' = Privy MPC (dashboard.privy.io).",
          default: "auto",
        },
      },
      required: [],
    },
  },
  {
    name: "safe_register_as_service",
    description:
      "Register this agent to the ERC-8004 on-chain registry with your capabilities and rate. " +
      "Enables other agents and humans to discover and hire you. " +
      "Performs MPC-signed transaction 鈥?no private keys exposed.",
    inputSchema: {
      type: "object",
      properties: {
        capabilities: {
          type: "array",
          items: { type: "string" },
          description: "List of capabilities (e.g. ['code-review', 'data-analysis', 'endpoint:https://...'])",
          minItems: 1,
          maxItems: 20,
        },
        min_rate: {
          type: "number",
          description: "Minimum USDC per operation (e.g. 0.05 for 5 cents)",
          minimum: 0,
          maximum: 100,
        },
        policy: {
          type: "object",
          description: "Optional policy constraints",
          properties: {
            max_task_seconds: { type: "number", default: 300 },
            allowed_chains: {
              type: "array",
              items: { type: "string", enum: ["base-sepolia", "base-mainnet", "ethereum"] },
              default: ["base-sepolia"],
            },
            require_escrow: { type: "boolean", default: true },
            max_rate_usdc: { type: "number", default: 10 },
          },
        },
        confirmed: {
          type: "boolean",
          description: "Set to true to confirm a previously flagged high-risk action",
          default: false,
        },
      },
      required: ["capabilities", "min_rate"],
    },
  },
  {
    name: "safe_hire_agent",
    description:
      "Hire a registered agent for a task with automatic reputation check, x402 micropayment, " +
      "and on-chain escrow. Funds are only released after verifiable proof of completion. " +
      "Minimum agent reputation: 70/100. All sensitive data stripped before transmission.",
    inputSchema: {
      type: "object",
      properties: {
        target_id: {
          type: "string",
          description: "ERC-8004 registered agent EVM address (0x...)",
          pattern: "^0x[a-fA-F0-9]{40}$",
        },
        task_description: {
          type: "string",
          description: "Natural-language task (PII is auto-stripped). Max 2000 chars.",
          maxLength: 2000,
        },
        payment_model: {
          type: "string",
          enum: ["per_request", "per_min", "per_execution"],
          description: "Payment cadence",
        },
        rate: {
          type: "number",
          description: "USDC rate (e.g. 0.05 = $0.05 per request)",
          minimum: 0,
          maximum: 100,
        },
        idempotency_key: {
          type: "string",
          description:
            "Optional dedupe key to prevent duplicate concurrent hires (8-128 chars, letters/numbers/:/_/-).",
          minLength: 8,
          maxLength: 128,
        },
        confirmed: {
          type: "boolean",
          description: "Set to true to confirm a previously flagged high-risk action",
          default: false,
        },
      },
      required: ["target_id", "task_description", "payment_model", "rate"],
    },
  },
  {
    name: "safe_hire_agents_batch",
    description:
      "Hire multiple agents in one call with bounded concurrency and failure policy control. " +
      "Each item uses the same secure hire flow: reputation gate -> escrow -> x402 -> proof verification -> settlement.",
    inputSchema: {
      type: "object",
      properties: {
        hires: {
          type: "array",
          minItems: 1,
          maxItems: 50,
          items: {
            type: "object",
            properties: {
              target_id: { type: "string", pattern: "^0x[a-fA-F0-9]{40}$" },
              task_description: { type: "string", maxLength: 2000 },
              payment_model: { type: "string", enum: ["per_request", "per_min", "per_execution"] },
              rate: { type: "number", minimum: 0, maximum: 100 },
              idempotency_key: { type: "string", minLength: 8, maxLength: 128 },
              confirmed: { type: "boolean", default: false },
            },
            required: ["target_id", "task_description", "payment_model", "rate"],
          },
        },
        failure_policy: {
          type: "string",
          enum: ["continue", "halt"],
          default: "continue",
          description: "'continue' runs all items; 'halt' stops after first failure.",
        },
        max_concurrency: {
          type: "number",
          minimum: 1,
          maximum: 10,
          default: 3,
          description: "Maximum parallel hires to run in this batch.",
        },
        batch_idempotency_key: {
          type: "string",
          minLength: 8,
          maxLength: 128,
          description: "Optional batch-level idempotency key used to derive per-item keys.",
        },
      },
      required: ["hires"],
    },
  },
  {
    name: "safe_listen_for_hire",
    description:
      "Start accepting hire requests from other agents and humans. " +
      "Verifies x402 payment before executing any task. " +
      "Requires your agent to be registered (use safe_register_as_service first).",
    inputSchema: {
      type: "object",
      properties: {},
      required: [],
    },
  },
  {
    name: "safe_execute_tx",
    description:
      "Safely execute an on-chain transaction from a plain-English intent. " +
      "Pipeline: intent parsing 鈫?EVM fork simulation 鈫?risk scoring 鈫?tiered approval 鈫?MPC sign. " +
      "Risk score 鈮?70 requires confirmed: true. Private keys NEVER exposed.",
    inputSchema: {
      type: "object",
      properties: {
        intent_description: {
          type: "string",
          description:
            "Plain-English transaction intent. E.g. 'Approve 50 USDC to escrow contract 0x...'. " +
            "NEVER include private keys or seed phrases.",
          maxLength: 1000,
        },
        confirmed: {
          type: "boolean",
          description: "Set to true to confirm a previously flagged high-risk transaction",
          default: false,
        },
      },
      required: ["intent_description"],
    },
  },
  {
    name: "checkpoint_memory",
    description:
      "Summarize and permanently archive the current session's memory. " +
      "Encrypts content 鈫?uploads to IPFS + Autonomys 鈫?anchors Merkle root on-chain. " +
      "Provides tamper-proof, verifiable session audit trail.",
    inputSchema: {
      type: "object",
      properties: {
        session_id: {
          type: "string",
          description: "Session ID to checkpoint",
        },
        summary: {
          type: "string",
          description: "Optional manual summary (auto-generated from session if omitted)",
          maxLength: 5000,
        },
        persist_key: {
          type: "boolean",
          description: "Keep encryption key for later retrieval (default: destroy after anchoring)",
          default: false,
        },
      },
      required: ["session_id"],
    },
  },
  {
    name: "get_agent_reputation",
    description:
      "Fetch ERC-8004 reputation profile and trust flags for a target agent before hiring.",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", pattern: "^0x[a-fA-F0-9]{40}$" },
        threshold: { type: "number", minimum: 0, maximum: 100 },
      },
      required: ["agent_id"],
    },
  },
  {
    name: "generate_agent_card",
    description:
      "Generate a shareable Agent Card JSON and markdown profile with capabilities, reputation, and activity metrics.",
    inputSchema: {
      type: "object",
      properties: {
        agent_id: { type: "string", pattern: "^0x[a-fA-F0-9]{40}$" },
        include_markdown: { type: "boolean", default: true },
      },
      required: [],
    },
  },
  {
    name: "verify_task_proof",
    description:
      "Verify proof-before-settlement by matching proof hash against session+agent hash and (optionally) on-chain escrow commitment.",
    inputSchema: {
      type: "object",
      properties: {
        escrow_id: { type: "string", pattern: "^0x[a-fA-F0-9]{64}$" },
        session_id: { type: "string", minLength: 1, maxLength: 128 },
        agent_id: { type: "string", pattern: "^0x[a-fA-F0-9]{40}$" },
        proof_hash: { type: "string", pattern: "^0x[a-fA-F0-9]{64}$" },
        check_onchain: { type: "boolean", default: true },
        zk_proof: { type: "string" },
        tee_attestation: { type: "string" },
      },
      required: ["escrow_id", "session_id", "agent_id", "proof_hash"],
    },
  },
  {
    name: "agent_analytics_summary",
    description:
      "Return hire history, success rate, cost summary, and a weekly markdown report.",
    inputSchema: {
      type: "object",
      properties: {
        period_days: { type: "number", minimum: 1, maximum: 365, default: 7 },
      },
      required: [],
    },
  },
];

// 鈹€鈹€ Tool dispatch 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const HANDLERS: Record<string, (args: unknown) => Promise<unknown>> = {
  setup_agentic_wallet,
  create_agentic_wallet,
  safe_register_as_service,
  safe_hire_agent,
  safe_hire_agents_batch,
  safe_listen_for_hire: (_args) => safe_listen_for_hire(),
  safe_execute_tx,
  checkpoint_memory,
  get_agent_reputation,
  generate_agent_card,
  verify_task_proof,
  agent_analytics_summary,
};

// 鈹€鈹€ MCP Server setup 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

const server = new Server(
  {
    name: "safelink",
    version: "0.1.0",
  },
  {
    capabilities: { tools: {} },
  }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS,
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  const handler = HANDLERS[name];

  if (!handler) {
    return {
      content: [{ type: "text", text: `Unknown tool: ${name}` }],
      isError: true,
    };
  }

  try {
    const result = await handler(args);
    return {
      content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
    };
  } catch (err) {
    // Structured approval request 鈫?surface to MCP host as actionable content
    if (err instanceof ApprovalRequiredError) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(err.toMCPContent(), null, 2),
          },
        ],
      };
    }

    // Known safe errors
    if (err instanceof SafeChainError) {
      logger.warn({ event: "tool_error", tool: name, code: err.code, message: err.message });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({ error: err.message, code: err.code }, null, 2),
          },
        ],
        isError: true,
      };
    }

    // Unexpected error 鈥?log but don't leak internals
    const message = err instanceof Error ? err.message : String(err);
    logger.error({ event: "tool_unexpected_error", tool: name, message });
    return {
      content: [{ type: "text", text: `Unexpected error: ${message}` }],
      isError: true,
    };
  }
});

// 鈹€鈹€ Boot 鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€鈹€

async function main() {
  try {
    // Validate env on startup 鈥?fail fast with clear message
    const { getConfig } = await import("./utils/config.js");
    getConfig();
  } catch (err) {
    process.stderr.write(`SafeLink startup error:\n${err instanceof Error ? err.message : String(err)}\n`);
    process.exit(1);
  }

  const transport = new StdioServerTransport();
  await server.connect(transport);

  logger.info({ event: "server_started", name: "safelink", version: "0.1.0" });
}

main().catch((err) => {
  process.stderr.write(`Fatal: ${err instanceof Error ? err.message : String(err)}\n`);
  process.exit(1);
});


