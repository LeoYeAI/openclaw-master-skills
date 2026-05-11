/**
 * consumed.ts — MCP 工具：消费水位线模块
 * 包含：mark_consumed, check_consumed
 * 来源：tools.ts 第 936-1050 行
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
export declare function registerConsumedTools(server: McpServer, authContext?: AuthContext): void;
