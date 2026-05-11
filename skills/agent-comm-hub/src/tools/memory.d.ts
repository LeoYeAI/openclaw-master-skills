/**
 * memory.ts — MCP 工具：记忆存储模块
 * 包含：store_memory, recall_memory, list_memories, delete_memory, search_memories
 * 来源：tools.ts 第 665-849 + 2253-2317 行
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
export declare function registerMemoryTools(server: McpServer, authContext?: AuthContext): void;
