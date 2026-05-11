import * as path from "path";
import * as fs from "fs";

import {
  SecurityEngine,
  ValidationMetadata,
} from "../../dist/core/security-engine";
import { ConfigManager } from "../../dist/core/config-manager";
import { DatabaseManager } from "../../dist/core/database-manager";
import { Action, Severity } from "../../dist/types/index";

interface ToolParameter {
  name: string;
  value: any;
  type?: string;
}

function normalizeToolParameters(parameters: unknown): ToolParameter[] {
  if (
    !parameters ||
    typeof parameters !== "object" ||
    Array.isArray(parameters)
  ) {
    return [];
  }

  return Object.entries(parameters).map(([name, value]) => ({
    name,
    value,
    type: typeof value,
  }));
}

function getValidatableParameters(
  toolName: string,
  parameters: ToolParameter[],
): ToolParameter[] {
  const validatable: ToolParameter[] = [];

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
    if (paramsToCheck.includes(param.name.toLowerCase())) {
      validatable.push(param);
    } else if (
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

function shouldBlock(action: Action): boolean {
  return action === Action.BLOCK || action === Action.BLOCK_NOTIFY;
}

export default function (api) {
  const pluginId = "security-tool-validator-plugin";

  api.on("before_tool_call", async (toolCall: any, ctx) => {
    try {
      api.logger.info(`[${pluginId}] toolcall validator check start`);

      const toolName = toolCall.name || toolCall.toolName || "";
      const parameters = normalizeToolParameters(
        toolCall.parameters || toolCall.params,
      );

      if (!toolName || parameters.length === 0) {
        return;
      }

      const configPaths = [
        path.join(process.cwd(), ".openclaw-sec.yaml"),
        path.join(
          process.env.HOME || "~",
          ".openclaw",
          "security-config.yaml",
        ),
      ];

      let config;
      for (const configPath of configPaths) {
        if (fs.existsSync(configPath)) {
          config = await ConfigManager.load(configPath);
          break;
        }
      }

      if (!config) {
        config = ConfigManager.getDefaultConfig();
      }

      if (!config.enabled) {
        return;
      }

      const dbPath =
        config.database?.path ||
        path.join(process.env.HOME || "~", ".openclaw", "security.db");
      const dbManager = new DatabaseManager(dbPath);

      const engine = new SecurityEngine(config, dbManager);

      const validatableParams = getValidatableParameters(toolName, parameters);

      if (validatableParams.length === 0) {
        await engine.stop();
        dbManager.close();
        return;
      }

      const allFindings: any[] = [];
      let maxSeverity = Severity.SAFE;
      let finalAction = Action.ALLOW;

      for (const param of validatableParams) {
        const valueStr =
          typeof param.value === "string"
            ? param.value
            : JSON.stringify(param.value);

        const metadata: ValidationMetadata = {
          userId: toolCall.userId || ctx?.user?.id || "unknown-user",
          sessionId: ctx?.sessionId,
          context: {
            hookType: "security-tool-validator",
            toolName: toolName,
            parameterName: param.name,
            timestamp: new Date().toISOString(),
          },
        };

        const result = await engine.validate(valueStr, metadata);

        if (result.findings.length > 0) {
          allFindings.push(
            ...result.findings.map((f) => ({
              parameter: param.name,
              module: f.module,
              category: f.pattern.category,
              description: f.pattern.description,
              severity: f.severity,
            })),
          );
        }

        if (compareSeverity(result.severity, maxSeverity) > 0) {
          maxSeverity = result.severity;
        }

        if (shouldBlock(result.action) && !shouldBlock(finalAction)) {
          finalAction = result.action;
        }
      }

      await engine.stop();
      dbManager.close();

      if (allFindings.length > 0) {
        if (shouldBlock(finalAction)) {
          api.logger.error(
            `[${pluginId}] 🚫 Tool Call Blocked: Security threats detected in ${toolName}\n` +
              `Severity: ${maxSeverity}\n` +
              `Findings:\n` +
              allFindings
                .map(
                  (f, i) =>
                    `${i + 1}. [${f.parameter}] ${f.category}: ${f.description}`,
                )
                .join("\n"),
          );

          return {
            block: true,
            blockReason: "exec is disabled by policy",
          };
        } else {
          api.logger.warn(
            `[${pluginId}] ⚠️  Security Notice: Potential issues detected in ${toolName}. ` +
              `The call will be allowed but logged for review.`,
          );
        }
      }
    } catch (error) {
      if (
        error instanceof Error &&
        error.message.includes("🚫 Tool Call Blocked")
      ) {
        throw error;
      }

      console.error("OpenClaw Security Tool Validator Error:", error);
    }
  });

  api.logger.info(`[${pluginId}] 插件加载完成`);
}
