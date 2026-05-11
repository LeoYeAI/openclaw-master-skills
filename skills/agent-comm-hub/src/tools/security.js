import { z } from "zod";
import { getEnhancedDbStats, archiveOldMessages, archiveOldAuditLogs, vacuumDatabase, getDbSize } from "../db.js";
import { auditLog, recalculateTrustScore, recalculateAllTrustScores } from "../security.js";
import { setAgentRole as setAgentRoleFromIdentity } from "../identity.js";
import { logError } from "../logger.js";
import { requireAuth } from "../utils.js";
/**
 * 注册安全与维护工具
 */
export function registerSecurityTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // Phase 5a: set_agent_role — admin only
    // 任命/撤销 group_admin，或调整角色
    // ────────────────────────────────────────────────────
    server.tool("set_agent_role", "设置 Agent 角色（admin/member/group_admin）。group_admin 需指定 managed_group_id，仅能管理该 parallel_group 内成员的任务。仅 admin 可调用。", {
        agent_id: z.string().describe("目标 Agent ID"),
        role: z.enum(["admin", "member", "group_admin"]).describe("新角色"),
        managed_group_id: z.string().optional().describe("管理组 ID（仅 group_admin 角色需要）"),
    }, async ({ agent_id, role, managed_group_id }) => {
        const ctx = requireAuth(authContext, "set_agent_role");
        const result = setAgentRoleFromIdentity(agent_id, role, ctx.agentId, managed_group_id);
        if (!result.ok) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: result.error }),
                    }],
            };
        }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        agent_id,
                        old_role: result.old_role,
                        new_role: result.new_role,
                        managed_group_id: result.managed_group_id,
                        note: result.new_role === "group_admin"
                            ? "group_admin 可管理指定 parallel_group 内成员的任务"
                            : result.new_role === "member"
                                ? "已降级为普通成员"
                                : "管理员权限（完全控制）",
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Phase 5a: recalculate_trust_scores — admin only
    // 手动触发信任分重算（admin 覆盖自动值后可用此工具重置）
    // ────────────────────────────────────────────────────
    server.tool("recalculate_trust_scores", "手动触发信任评分重算。基于多因子自动计算：verified capabilities (+3)、approved strategies (+2)、positive feedback (+1)、negative feedback (-2)、rejected applications (-3)、revoked tokens (-10)。不传 agent_id 则重算全部。仅 admin 可调用。", {
        agent_id: z.string().optional().describe("目标 Agent ID（不传则重算全部 Agent）"),
    }, async ({ agent_id }) => {
        const ctx = requireAuth(authContext, "recalculate_trust_scores");
        try {
            if (agent_id) {
                const score = recalculateTrustScore(agent_id);
                return {
                    content: [{
                            type: "text",
                            text: JSON.stringify({
                                success: true,
                                agent_id,
                                new_score: score,
                                note: "信任评分已重新计算并写入 agents.trust_score",
                            }, null, 2),
                        }],
                };
            }
            else {
                const results = recalculateAllTrustScores();
                return {
                    content: [{
                            type: "text",
                            text: JSON.stringify({
                                success: true,
                                total_agents: results.length,
                                scores: results,
                                note: `已重算 ${results.length} 个 Agent 的信任评分`,
                            }, null, 2),
                        }],
                };
            }
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // v2.3 Phase 3.2: 数据库维护工具（admin only）
    // ────────────────────────────────────────────────────
    // Tool DB1: get_db_stats — admin only
    server.tool("get_db_stats", "获取数据库统计信息。包括各表行数、数据库文件大小、WAL 大小、最后归档时间等。仅 admin 可调用。", {}, async () => {
        requireAuth(authContext, "get_db_stats");
        try {
            const stats = getEnhancedDbStats();
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            ...stats,
                            note: stats.database_size_mb > 100
                                ? "⚠️ 数据库超过 100MB，建议执行 VACUUM 或归档旧数据"
                                : "数据库状态正常",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("get_db_stats_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool DB2: archive_data — admin only
    server.tool("archive_data", "手动触发数据归档。将指定天数之前的记录从主表移入归档表，以减少主表体积。可归档 messages（默认 30 天前）或 audit_log（默认 90 天前）。仅 admin 可调用。", {
        type: z.enum(["messages", "audit_log"]).describe("要归档的数据类型"),
        days: z.number().int().min(1).max(365).optional()
            .describe("归档多少天前的数据（messages 默认 30 天，audit_log 默认 90 天）"),
        vacuum: z.boolean().optional().default(false)
            .describe("归档后是否执行 VACUUM 压缩数据库文件"),
    }, async ({ type, days, vacuum }) => {
        requireAuth(authContext, "archive_data");
        try {
            const daysForType = days ?? (type === "messages" ? 30 : 90);
            let archivedCount = 0;
            if (type === "messages") {
                archivedCount = archiveOldMessages(daysForType);
            }
            else {
                archivedCount = archiveOldAuditLogs(daysForType);
            }
            // VACUUM（可选，低峰期调用）
            if (vacuum) {
                vacuumDatabase();
            }
            const dbSize = getDbSize();
            auditLog("tool_archive_data", authContext.agentId, `type=${type}, days=${daysForType}, archived=${archivedCount}, vacuum=${vacuum}`);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            type,
                            days: daysForType,
                            archived_count: archivedCount,
                            vacuum_executed: vacuum ?? false,
                            database_size_bytes: dbSize,
                            database_size_mb: Math.round((dbSize / 1024 / 1024) * 100) / 100,
                            note: archivedCount > 0
                                ? `已归档 ${archivedCount} 条 ${type} 记录`
                                : `没有需要归档的 ${type} 记录`,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            logError("archive_data_error", err);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
}
//# sourceMappingURL=security.js.map