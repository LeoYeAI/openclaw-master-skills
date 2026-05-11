import { z } from "zod";
import { auditLog, revokeToken as revokeTokenFromSecurity, recalculateTrustScore, } from "../security.js";
import { registerAgent as registerAgentFromIdentity, heartbeat as heartbeatFromIdentity, queryAgents as queryAgentsFromIdentity, clearOfflineNotification, updateAgentTrustScore, } from "../identity.js";
import { onlineAgents } from "../sse.js";
import { db } from "../db.js";
import { requireAuth } from "../utils.js";
export function registerIdentityTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // NEW Tool 1: register_agent (Phase 1)
    // 注册新 Agent — public 工具，无需认证
    // ────────────────────────────────────────────────────
    server.tool("register_agent", "注册新 Agent 到 Hub。需要有效的邀请码。注册成功返回 agent_id 和 api_token（仅显示一次）。", {
        invite_code: z.string().describe("邀请码（通过 /admin/invite/generate 获取）"),
        name: z.string().describe("Agent 名称"),
        capabilities: z.array(z.string()).optional()
            .describe("Agent 能力列表，如 ['mcp', 'sse', 'memory']"),
    }, async ({ invite_code, name, capabilities }) => {
        // public 工具，不需要权限检查
        const result = registerAgentFromIdentity(invite_code, name, capabilities || []);
        if (!result.success) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: result.error }),
                    }],
            };
        }
        auditLog("tool_register_agent", result.agentId ?? null, name, `role=${result.role ?? 'unknown'}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        agent_id: result.agentId,
                        api_token: result.apiToken,
                        role: result.role ?? "member",
                        warning: "⚠️ api_token 仅显示一次，请妥善保存！",
                        next_step: "使用此 Token 调用 heartbeat 工具上线，Token 通过 Authorization: Bearer <token> 传递",
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // NEW Tool 2: heartbeat (Phase 1)
    // 上报心跳 — member 及以上
    // ────────────────────────────────────────────────────
    server.tool("heartbeat", "上报 Agent 心跳，维持在线状态并累积信任分。Agent 上线后应每 30 秒调用一次。超过 90 秒无心跳将自动标记为离线。连续在线心跳每 3 次自动增加 1 点 trust_score（上限 100）。", {
        agent_id: z.string().describe("Agent ID（注册时返回的 agent_id）"),
    }, async ({ agent_id }) => {
        const ctx = requireAuth(authContext, "heartbeat");
        // 验证调用者是 Agent 本人
        if (ctx.agentId !== agent_id && ctx.role !== "admin") {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: false,
                            error: "Cannot send heartbeat for another agent (admin only)",
                        }),
                    }],
            };
        }
        const result = heartbeatFromIdentity(agent_id);
        if (result.success) {
            // 清除离线通知标记
            clearOfflineNotification(agent_id);
        }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify(result, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // NEW Tool 3: query_agents (Phase 1)
    // 查询已注册 Agent — member 及以上
    // ────────────────────────────────────────────────────
    server.tool("query_agents", "查询已注册的 Agent 列表。支持按状态、角色筛选。", {
        status: z.enum(["online", "offline", "all"]).optional()
            .default("all").describe("Agent 状态筛选"),
        role: z.enum(["admin", "member", "group_admin"]).optional()
            .describe("角色筛选"),
        capability: z.string().optional()
            .describe("能力筛选"),
    }, async ({ status, role, capability }) => {
        const ctx = requireAuth(authContext, "query_agents");
        const agents = queryAgentsFromIdentity({ status, role, capability });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        agents,
                        count: agents.length,
                        queried_by: ctx.agentId,
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // NEW Tool 4: revoke_token (Phase 1)
    // 吊销 Token — admin only
    // ────────────────────────────────────────────────────
    server.tool("revoke_token", "吊销 API Token，使其立即失效。仅 admin 可调用。", {
        token_id: z.string().describe("要吊销的 Token ID"),
    }, async ({ token_id }) => {
        const ctx = requireAuth(authContext, "revoke_token");
        const success = revokeTokenFromSecurity(token_id);
        if (success) {
            auditLog("tool_revoke_token", ctx.agentId, token_id);
            // Phase 5a Day 2: token 吊销影响信任评分
            try {
                const tokenRow = db.prepare(`SELECT agent_id FROM auth_tokens WHERE token_id=?`).get(token_id);
                if (tokenRow?.agent_id) {
                    recalculateTrustScore(tokenRow.agent_id);
                }
            }
            catch { }
        }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success,
                        token_id,
                        note: success ? "Token 已吊销，使用该 Token 的 Agent 将无法访问" : "Token not found or already revoked",
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // NEW Tool 4b: set_trust_score (Phase 2 Day 4)
    // 设置信任分 — admin only
    // ────────────────────────────────────────────────────
    server.tool("set_trust_score", "调整 Agent 信任分（-100 到 +100 的增量）。信任分影响 collective 记忆搜索排序，高信任 Agent 的记忆排名靠前。仅 admin 可调用。", {
        agent_id: z.string().describe("目标 Agent ID"),
        delta: z.number().min(-100).max(100).describe("信任分增量（正数加分，负数扣分）"),
    }, async ({ agent_id, delta }) => {
        const ctx = requireAuth(authContext, "set_trust_score");
        const result = updateAgentTrustScore(agent_id, delta, ctx.agentId);
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
                        new_score: result.new_score,
                        delta,
                        note: result.new_score >= 80
                            ? "🟢 高信任 Agent，记忆搜索排名优先"
                            : result.new_score >= 30
                                ? "🟡 正常信任分"
                                : "🔴 低信任 Agent，记忆搜索排名靠后",
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Tool 10: get_online_agents (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("get_online_agents", "查询当前通过 SSE 在线连接的 Agent 列表，分配任务前可先确认对方在线。", {}, async () => {
        requireAuth(authContext, "get_online_agents");
        const online = onlineAgents();
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        online_agents: online,
                        count: online.length,
                        timestamp: Date.now(),
                    }, null, 2),
                }],
        };
    });
}
//# sourceMappingURL=identity.js.map