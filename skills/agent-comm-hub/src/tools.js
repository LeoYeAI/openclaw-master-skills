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
export function registerTools(server, authContext) {
    registerIdentityTools(server, authContext);
    registerMessageTools(server, authContext);
    registerMemoryTools(server, authContext);
    registerConsumedTools(server, authContext);
    registerEvolutionTools(server, authContext);
    registerOrchestratorTools(server, authContext);
    registerSecurityTools(server, authContext);
    registerFileTools(server, authContext);
}
//# sourceMappingURL=tools.js.map