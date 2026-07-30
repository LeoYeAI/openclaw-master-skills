import * as readline from "readline";
import type { SimulationReport } from "./simulation.js";
import type { RiskResult } from "./risk-scorer.js";
import { logger } from "../utils/logger.js";

// ── Types ─────────────────────────────────────────────────────────────────────

export interface ApprovalRequest {
  action: string;
  details: SimulationReport;
  riskScore: number;
  riskFlags?: string[];
  riskDetails?: Record<string, string>;
  amountUSDC?: number;
  targetAgent?: string;
}

// ── Human-in-the-loop approval ────────────────────────────────────────────────
//
// In Claude Desktop / Claude Code, this will surface as a tool confirmation
// dialog because the MCP server returns a structured "approval_required"
// response that the host application renders natively.
//
// When running as a CLI / standalone process (e.g. tests, scripts), we fall
// back to stdin prompt so the developer can still approve interactively.

export async function requireApproval(req: ApprovalRequest): Promise<boolean> {
  logger.warn({
    event: "approval_required",
    action: req.action,
    riskScore: req.riskScore,
    flags: req.riskFlags ?? [],
  });

  // Check if we're running inside an MCP server (stdio transport)
  // In that mode, we cannot use stdin — throw a structured error that the
  // MCP host will catch and present as a confirmation dialog.
  if (process.env["MCP_SERVER"] === "1") {
    throw new ApprovalRequiredError(req);
  }

  // CLI fallback: prompt to stderr (not stdout, which is MCP wire)
  return promptStdin(req);
}

async function promptStdin(req: ApprovalRequest): Promise<boolean> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stderr,
  });

  const flagLines =
    req.riskFlags && req.riskFlags.length > 0
      ? `  Flags: ${req.riskFlags.join(", ")}\n`
      : "";

  const prompt =
    `\n⚠️  HIGH-RISK ACTION REQUIRES APPROVAL\n` +
    `  Action: ${req.action}\n` +
    `  Risk score: ${req.riskScore}/100\n` +
    flagLines +
    (req.amountUSDC !== undefined ? `  Amount: $${req.amountUSDC} USDC\n` : "") +
    (req.targetAgent ? `  Target agent: ${req.targetAgent}\n` : "") +
    `\n  Type "yes" to approve, anything else to reject: `;

  return new Promise((resolve) => {
    rl.question(prompt, (answer) => {
      rl.close();
      const approved = answer.trim().toLowerCase() === "yes";
      logger.info({ event: "approval_response", approved, action: req.action });
      resolve(approved);
    });
  });
}

// ── Structured error for MCP host to surface as confirmation dialog ───────────

export class ApprovalRequiredError extends Error {
  readonly code = "APPROVAL_REQUIRED";
  readonly request: ApprovalRequest;

  constructor(req: ApprovalRequest) {
    super(
      `Action requires human approval: ${req.action} (risk score ${req.riskScore}/100)`
    );
    this.name = "ApprovalRequiredError";
    this.request = req;
  }

  /** Serialise for MCP tool response. */
  toMCPContent(): Record<string, unknown> {
    return {
      type: "approval_required",
      action: this.request.action,
      risk_score: this.request.riskScore,
      risk_flags: this.request.riskFlags ?? [],
      risk_details: this.request.riskDetails ?? {},
      amount_usdc: this.request.amountUSDC,
      target_agent: this.request.targetAgent,
      instructions:
        "Call this tool again with `{ confirmed: true }` to approve, " +
        "or `{ confirmed: false }` to reject.",
    };
  }
}
