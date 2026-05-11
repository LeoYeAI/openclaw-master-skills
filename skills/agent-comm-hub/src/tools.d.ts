/**
 * tools.ts — MCP 工具注册入口
 * Phase A 重构：原 2687 行拆分为 8 个模块 + 本入口（~50 行）
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "./security.js";
/**
 * 注册所有 MCP 工具
 * @param server McpServer 实例
 * @param authContext 认证上下文（未认证时为 undefined）
 */
export declare function registerTools(server: McpServer, authContext?: AuthContext): void;
