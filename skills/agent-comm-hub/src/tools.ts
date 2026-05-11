/**
 * tools.ts — MCP 工具注册入口
 * Phase A 重构：原 2687 行拆分为 8 个模块 + 本入口（~50 行）
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "./security.js";
import { registerIdentityTools } from "./tools/identity.js";
import { registerMessageTools } from "./tools/message.js";
import { registerMemoryTools } from "./tools/memory.js";
import { registerConsumedTools } from "./tools/consumed.js";
import { registerEvolutionTools } from "./tools/evolution.js";
import { registerOrchestratorTools } from "./tools/orchestrator.js";
import { registerSecurityTools } from "./tools/security.js";
import { registerFileTools } from "./tools/file.js";

/**
 * 注册所有 MCP 工具
 * @param server McpServer 实例
 * @param authContext 认证上下文（未认证时为 undefined）
 */
export function registerTools(server: McpServer, authContext?: AuthContext): void {
  registerIdentityTools(server, authContext);
  registerMessageTools(server, authContext);
  registerMemoryTools(server, authContext);
  registerConsumedTools(server, authContext);
  registerEvolutionTools(server, authContext);
  registerOrchestratorTools(server, authContext);
  registerSecurityTools(server, authContext);
  registerFileTools(server, authContext);
}
