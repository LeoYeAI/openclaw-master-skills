/**
 * Guardian Angel Startup Diagnostics
 * 
 * Checks for potential security issues at gateway start.
 */

import { GA_PRIORITY } from "./constants.js";
import type { PluginLogger } from "./types.js";

interface PluginApi {
  logger: PluginLogger;
  // Note: Hook introspection API not yet available in OpenClaw
  // Future: api.runtime.hooks?.list?.("before_tool_call")
}

/**
 * Run startup diagnostics.
 */
export function runStartupDiagnostics(api: PluginApi): void {
  const logger = api.logger;

  logger.info("[GA] Running startup diagnostics...");

  // Log our priority
  logger.info(`[GA] Registered at priority ${GA_PRIORITY}`);

  // Note about limitations
  // OpenClaw doesn't currently expose hook introspection, so we can't
  // programmatically check for lower-priority hooks. We document this
  // limitation and recommend manual verification.
  
  logger.info(
    "[GA] ℹ️ Note: Cannot verify hook priority ordering (introspection API not available). " +
    "If other plugins register before_tool_call hooks with priority < -10000, " +
    "they could theoretically override GA decisions."
  );

  // Future implementation when OpenClaw exposes hook registry:
  /*
  const hooks = api.runtime.hooks?.list?.("before_tool_call") ?? [];
  const lowerPriorityHooks = hooks.filter(h => 
    h.pluginId !== "guardian-angel" && 
    (h.priority ?? 0) < GA_PRIORITY
  );

  if (lowerPriorityHooks.length > 0) {
    logger.warn(
      `[GA] ⚠️ SECURITY WARNING: ${lowerPriorityHooks.length} hook(s) registered ` +
      `with lower priority than Guardian Angel. These could override GA decisions:\n` +
      lowerPriorityHooks.map(h => `  - ${h.pluginId} (priority: ${h.priority})`).join("\n")
    );
  } else {
    logger.info("[GA] ✓ No hooks registered below Guardian Angel priority.");
  }
  */

  logger.info("[GA] ✓ Diagnostics complete. Guardian Angel is active.");
}
