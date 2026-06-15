/**
 * Agent path utilities
 */

import path from "node:path";
import os from "node:os";

/**
 * Resolve the OpenClaw agent directory (~/.openclaw)
 */
export function resolveOpenClawAgentDir(): string {
  return process.env.OPENCLAW_AGENT_DIR || process.env.CLAWDBOT_DIR || path.join(os.homedir(), ".openclaw");
}

/** @deprecated Use resolveOpenClawAgentDir */
export const resolveClawdbotAgentDir = resolveOpenClawAgentDir;
