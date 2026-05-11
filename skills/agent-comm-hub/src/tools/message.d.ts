/**
 * message.ts — MCP 工具：消息通信模块
 * 包含：send_message, broadcast_message, acknowledge_message, batch_acknowledge_messages, search_messages
 * 来源：tools.ts 第 324-426 + 581-659 + 878-931 + 2195-2251 + 2323-2420 行
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
export declare function registerMessageTools(server: McpServer, authContext?: AuthContext): void;
