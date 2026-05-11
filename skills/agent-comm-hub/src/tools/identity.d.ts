/**
 * identity.ts — MCP 工具：Agent Identity 模块
 * 包含：register_agent, heartbeat, query_agents, get_online_agents, set_trust_score, revoke_token
 * 来源：tools.ts 第 125-319 行 + 第 854-873 行
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
export declare function registerIdentityTools(server: McpServer, authContext?: AuthContext): void;
