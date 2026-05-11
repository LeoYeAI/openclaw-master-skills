/**
 * tools/orchestrator.ts — Task Orchestrator 工具定义（16 个）
 * Phase A 重构：从 tools.ts 提取
 *
 * Tools: assign_task, update_task_status, get_task_status,
 *        add_dependency, remove_dependency, get_task_dependencies, create_parallel_group,
 *        request_handoff, accept_handoff, reject_handoff,
 *        add_quality_gate, evaluate_quality_gate,
 *        create_pipeline, get_pipeline, list_pipelines, add_task_to_pipeline
 */
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { type AuthContext } from "../security.js";
/**
 * 注册 Task Orchestrator 相关工具（16 个）
 */
export declare function registerOrchestratorTools(server: McpServer, authContext?: AuthContext): void;
