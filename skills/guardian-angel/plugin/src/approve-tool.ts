/**
 * Guardian Angel Approval Tool
 * 
 * Allows the agent to approve escalated actions after user confirmation.
 */

import type { Store, PluginLogger } from "./types.js";

interface ToolResult {
  content: Array<{ type: string; text: string }>;
}

/**
 * Create the ga_approve tool definition.
 */
export function createApprovalTool(store: Store, logger: PluginLogger) {
  return {
    name: "ga_approve",
    description: `Approve a Guardian Angel escalation. Use this after the user confirms they want to proceed with a blocked action. The nonce comes from the GUARDIAN_ANGEL_ESCALATE block reason. After approval, immediately retry the original tool call.`,
    parameters: {
      type: "object",
      properties: {
        nonce: {
          type: "string",
          description: "The escalation nonce from the block reason (e.g., 'a7f3c21b')",
        },
        reason: {
          type: "string",
          description: "Optional: user's reason for approving",
        },
      },
      required: ["nonce"],
    },
    async execute(
      _id: string,
      params: { nonce: string; reason?: string }
    ): Promise<ToolResult> {
      const { nonce, reason } = params;

      const result = store.approvePending(nonce);

      if (!result.ok) {
        logger.warn(`[GA] Approval failed for nonce ${nonce}: ${result.error}`);
        return {
          content: [
            {
              type: "text",
              text: `❌ Approval failed: ${result.error}`,
            },
          ],
        };
      }

      logger.info(`[GA] Approved nonce ${nonce}${reason ? ` (reason: ${reason})` : ""}`);

      return {
        content: [
          {
            type: "text",
            text: `✓ Approved. You may now retry the action. Approval expires in ${result.windowSeconds}s.`,
          },
        ],
      };
    },
  };
}
