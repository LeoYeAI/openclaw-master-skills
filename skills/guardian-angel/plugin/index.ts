/**
 * Guardian Angel Plugin
 * 
 * Virtue-based moral conscience for AI agents.
 * Evaluates tool calls through Thomistic ethics and blocks/escalates high-stakes actions.
 * 
 * @version 1.0.0
 * @see skills/guardian-angel/SKILL.md
 * @see skills/guardian-angel/PLUGIN-SPEC.md
 */

import { createBeforeToolCallHandler } from "./src/hook.js";
import { createApprovalTool } from "./src/approve-tool.js";
import { createStore } from "./src/store.js";
import { runStartupDiagnostics } from "./src/diagnostics.js";
import { GA_PRIORITY } from "./src/constants.js";
import type { GuardianAngelConfig } from "./src/types.js";

interface PluginApi {
  id: string;
  name: string;
  config: unknown;
  pluginConfig?: Record<string, unknown>;
  logger: {
    debug?: (message: string) => void;
    info: (message: string) => void;
    warn: (message: string) => void;
    error: (message: string) => void;
  };
  registerTool: (tool: unknown) => void;
  on: (
    hookName: string,
    handler: (...args: unknown[]) => unknown,
    opts?: { priority?: number }
  ) => void;
  resolvePath: (input: string) => string;
}

/**
 * Plugin definition
 */
export default {
  id: "guardian-angel",
  name: "Guardian Angel",
  description: "Virtue-based moral conscience for AI agents",
  version: "1.0.0",

  register(api: PluginApi) {
    const config = (api.pluginConfig || {}) as GuardianAngelConfig;
    
    // Check if disabled
    if (config.enabled === false) {
      api.logger.info("[GA] Guardian Angel is disabled via configuration");
      return;
    }

    // Create the nonce store
    const store = createStore(config, api.resolvePath);

    // Register the before_tool_call hook (runs LAST due to low priority)
    api.on(
      "before_tool_call",
      createBeforeToolCallHandler(config, store, api.logger),
      { priority: GA_PRIORITY }
    );

    // Register the approval tool
    api.registerTool(createApprovalTool(store, api.logger));

    // Run startup diagnostics when gateway starts
    api.on(
      "gateway_start",
      () => runStartupDiagnostics(api),
      { priority: 0 }
    );

    api.logger.info(`[GA] Guardian Angel v1.0.0 active (hook priority: ${GA_PRIORITY})`);
  },
};
