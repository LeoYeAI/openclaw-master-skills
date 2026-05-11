/**
 * security.ts — 安全与维护工具
 * Tools: set_agent_role, recalculate_trust_scores, get_db_stats, archive_data
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
/**
 * 注册安全与维护工具
 */
export declare function registerSecurityTools(server: McpServer, authContext?: AuthContext): void;
