/**
 * tools/evolution.ts — Evolution Engine 工具定义（12 个）
 * Phase A 重构：从 tools.ts 提取
 *
 * Tools: share_experience, propose_strategy, list_strategies, search_strategies,
 *        apply_strategy, feedback_strategy, approve_strategy, get_evolution_status,
 *        score_applied_strategies, propose_strategy_tiered, check_veto_window, veto_strategy
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
/**
 * 注册 Evolution Engine 相关工具（12 个）
 */
export declare function registerEvolutionTools(server: McpServer, authContext?: AuthContext): void;
