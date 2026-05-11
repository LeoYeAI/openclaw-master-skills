/**
 * Guardian Angel before_tool_call Hook
 * 
 * The final gate before tool execution.
 */

import { evaluate } from "./evaluate.js";
import type { Store, GuardianAngelConfig, PluginLogger } from "./types.js";

interface BeforeToolCallEvent {
  toolName: string;
  params: Record<string, unknown>;
}

interface BeforeToolCallResult {
  params?: Record<string, unknown>;
  block?: boolean;
  blockReason?: string;
}

interface ToolContext {
  agentId?: string;
  sessionKey?: string;
  toolName: string;
}

/**
 * Create the before_tool_call hook handler.
 */
export function createBeforeToolCallHandler(
  config: GuardianAngelConfig,
  store: Store,
  logger: PluginLogger
) {
  return async (
    event: BeforeToolCallEvent,
    ctx: ToolContext
  ): Promise<BeforeToolCallResult | void> => {
    const { toolName, params } = event;

    // 1. Check if plugin is disabled
    if (config.enabled === false) {
      return; // Allow everything
    }

    // 2. Check exemptions
    const neverBlock = config.neverBlock || [];
    if (neverBlock.includes(toolName)) {
      logger.debug?.(`[GA] ${toolName}: exempt, allowing`);
      return; // Allow
    }

    // 3. Check if this call has a valid approval
    const paramsHash = store.hashParams(toolName, params);
    const approval = store.consumeApproval(paramsHash);
    if (approval) {
      logger.info(`[GA] ${toolName}: approved via nonce ${approval.nonce}`);
      return; // Allow (approval consumed)
    }

    // 4. Check alwaysBlock list
    const alwaysBlock = config.alwaysBlock || [];
    if (alwaysBlock.includes(toolName)) {
      return escalate(
        toolName,
        params,
        paramsHash,
        store,
        logger,
        `Tool '${toolName}' requires explicit approval per configuration`
      );
    }

    // 5. Run virtue-based evaluation
    const result = evaluate(toolName, params, ctx, config, logger);

    switch (result.decision) {
      case "allow":
        logger.debug?.(`[GA] ${toolName}: virtues aligned (score=${(result.clarity || 1) * (result.stakes || 1)}), allowing`);
        return; // Allow

      case "block":
        // Intrinsic evil or hard block — no approval possible
        logger.warn(`[GA] ${toolName}: BLOCKED (${result.reason})`);
        return {
          block: true,
          blockReason: `GUARDIAN_ANGEL_BLOCK|${result.reason}`,
        };

      case "escalate":
        return escalate(toolName, params, paramsHash, store, logger, result.reason || "High-stakes action requires approval");
    }
  };
}

/**
 * Create an escalation block with nonce.
 */
function escalate(
  toolName: string,
  params: Record<string, unknown>,
  paramsHash: string,
  store: Store,
  logger: PluginLogger,
  reason: string
): BeforeToolCallResult {
  // Generate and store nonce
  const nonce = store.createPending(paramsHash, toolName, params);

  logger.info(`[GA] ${toolName}: escalating (nonce: ${nonce})`);

  // Return structured block reason the agent can parse
  return {
    block: true,
    blockReason: `GUARDIAN_ANGEL_ESCALATE|${nonce}|${reason}`,
  };
}
