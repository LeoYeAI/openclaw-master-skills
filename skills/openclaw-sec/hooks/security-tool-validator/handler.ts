import type { HookHandler } from "../../src/hooks/hooks.js";
import { SecurityEngine, ValidationMetadata } from "../../src/core/security-engine.js";
import { ConfigManager } from "../../src/core/config-manager.js";
import { DatabaseManager } from "../../src/core/database-manager.js";
import { Action, Severity } from "../../src/types/index.js";
import * as path from "path";
import * as fs from "fs";

/**
 * Security Tool Validator Hook
 *
 * Validates tool call parameters before execution.
 * Uses the tool_result_persist plugin API.
 */

interface ToolParameter {
  name: string;
  value: any;
  type?: string;
}

/**
 * Determine which parameters need security validation based on tool
 */
function getValidatableParameters(toolName: string, parameters: ToolParameter[]): ToolParameter[] {
  const validatable: ToolParameter[] = [];

  // Map of tools to parameters that need validation
  const toolParamMap: Record<string, string[]> = {
    bash: ["command"],
    exec: ["command", "script"],
    read: ["file_path", "path"],
    write: ["file_path", "path", "content"],
    edit: ["file_path", "old_string", "new_string"],
    web_fetch: ["url"],
    web_search: ["query"],
    fetch: ["url"],
    curl: ["url"],
    wget: ["url"],
  };

  const paramsToCheck = toolParamMap[toolName.toLowerCase()] || [];

  parameters.forEach((param) => {
    // Check if this parameter should be validated
    if (paramsToCheck.includes(param.name.toLowerCase())) {
      validatable.push(param);
    }
    // Also check any parameter with security-relevant names
    else if (
      param.name.toLowerCase().includes("command") ||
      param.name.toLowerCase().includes("url") ||
      param.name.toLowerCase().includes("path") ||
      param.name.toLowerCase().includes("file")
    ) {
      validatable.push(param);
    }
  });

  return validatable;
}

/**
 * Compare severity levels
 */
function compareSeverity(s1: Severity, s2: Severity): number {
  const order = {
    [Severity.SAFE]: 0,
    [Severity.LOW]: 1,
    [Severity.MEDIUM]: 2,
    [Severity.HIGH]: 3,
    [Severity.CRITICAL]: 4,
  };

  return order[s1] - order[s2];
}

/**
 * Check if action should block
 */
function shouldBlock(action: Action): boolean {
  return action === Action.BLOCK || action === Action.BLOCK_NOTIFY;
}

const handler: HookHandler = async (event) => {
  // This hook bootstraps the tool validation system
  if (event.type === "agent" && event.action === "bootstrap") {
    // Register tool_result_persist plugin API
    if (event.api?.registerPlugin) {
      event.api.registerPlugin("tool_result_persist", async (toolCall: any) => {
        try {
          const toolName = toolCall.name || toolCall.toolName || "";
          const parameters: ToolParameter[] = toolCall.parameters || toolCall.params || [];

          if (!toolName || parameters.length === 0) {
            return; // Nothing to validate
          }

          // Find config file
          const configPaths = [
            path.join(process.cwd(), ".openclaw-sec.yaml"),
            path.join(process.env.HOME || "~", ".openclaw", "security-config.yaml"),
          ];

          let config;
          for (const configPath of configPaths) {
            if (fs.existsSync(configPath)) {
              config = await ConfigManager.load(configPath);
              break;
            }
          }

          // Use default config if none found
          if (!config) {
            config = ConfigManager.getDefaultConfig();
          }

          // Check if security is disabled
          if (!config.enabled) {
            return; // Security disabled, allow through
          }

          // Initialize database
          const dbPath = config.database?.path || path.join(
            process.env.HOME || "~",
            ".openclaw",
            "security.db"
          );
          const dbManager = new DatabaseManager(dbPath);

          // Initialize security engine
          const engine = new SecurityEngine(config, dbManager);

          // Get parameters that need validation
          const validatableParams = getValidatableParameters(toolName, parameters);

          if (validatableParams.length === 0) {
            // No parameters need validation
            await engine.stop();
            dbManager.close();
            return;
          }

          // Validate each parameter
          const allFindings: any[] = [];
          let maxSeverity = Severity.SAFE;
          let finalAction = Action.ALLOW;

          for (const param of validatableParams) {
            // Convert parameter value to string for validation
            const valueStr =
              typeof param.value === "string" ? param.value : JSON.stringify(param.value);

            const metadata: ValidationMetadata = {
              userId: toolCall.userId || event.user?.id || "unknown-user",
              sessionId: toolCall.sessionId || event.session?.id || `session-${Date.now()}`,
              context: {
                hookType: "security-tool-validator",
                toolName: toolName,
                parameterName: param.name,
                timestamp: new Date().toISOString(),
              },
            };

            const result = await engine.validate(valueStr, metadata);

            // Track findings
            if (result.findings.length > 0) {
              allFindings.push(
                ...result.findings.map((f) => ({
                  parameter: param.name,
                  module: f.module,
                  category: f.pattern.category,
                  description: f.pattern.description,
                  severity: f.severity,
                }))
              );
            }

            // Update max severity and action
            if (compareSeverity(result.severity, maxSeverity) > 0) {
              maxSeverity = result.severity;
            }

            if (shouldBlock(result.action) && !shouldBlock(finalAction)) {
              finalAction = result.action;
            }
          }

          // Stop engine and cleanup
          await engine.stop();
          dbManager.close();

          // Handle findings
          if (allFindings.length > 0) {
            if (shouldBlock(finalAction)) {
              // Block the tool call
              throw new Error(
                `🚫 Tool Call Blocked: Security threats detected in ${toolName}\n\n` +
                `Severity: ${maxSeverity}\n` +
                `Findings:\n` +
                allFindings
                  .map(
                    (f, i) => `${i + 1}. [${f.parameter}] ${f.category}: ${f.description}`
                  )
                  .join("\n")
              );
            } else {
              // Warn but allow
              console.warn(
                `⚠️  Security Notice: Potential issues detected in ${toolName}\n` +
                `The call will be allowed but logged for review.`
              );
            }
          }

          // Allow the tool call to proceed
        } catch (error) {
          // On error, log but allow the request (fail-open)
          if (error instanceof Error && error.message.includes("🚫 Tool Call Blocked")) {
            // This is our blocking error, re-throw it
            throw error;
          }

          // Other errors - log and allow
          console.error("OpenClaw Security Tool Validator Error:", error);
          // Don't block on error
        }
      });
    }
  }
};

export default handler;
