/**
 * file.ts — 文件传输工具
 * Tools: upload_file, download_file, list_attachments
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
/**
 * 注册文件传输工具
 */
export declare function registerFileTools(server: McpServer, authContext?: AuthContext): void;
