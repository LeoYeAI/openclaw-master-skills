import { z } from "zod";
import { pushToAgent } from "../sse.js";
import { auditLog, recalculateTrustScore } from "../security.js";
import { shareExperience, proposeStrategy, proposeStrategyTiered, listStrategies, searchStrategies, applyStrategy, feedbackStrategy, provideFeedback, scoreAppliedStrategies, approveStrategy, getEvolutionStatus, checkVetoWindow, vetoStrategy as vetoStrategyFromEvolution, } from "../evolution.js";
import { requireAuth } from "../utils.js";
/**
 * 注册 Evolution Engine 相关工具（12 个）
 */
export function registerEvolutionTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // Phase 3: Evolution Engine 工具
    // ────────────────────────────────────────────────────
    // Tool E1: share_experience — member 及以上
    server.tool("share_experience", "分享经验到 Hub。经验直接发布（不需审批），所有 Agent 可见。适合记录踩坑经验、最佳实践。", {
        title: z.string().min(3).max(200).describe("经验标题"),
        content: z.string().min(10).max(5000).describe("经验内容（Markdown，最多 5000 字符）"),
        tags: z.array(z.string()).max(10).optional().describe("标签列表，如 ['debugging', 'mcp']"),
        task_id: z.string().optional().describe("关联任务 ID"),
    }, async ({ title, content, tags, task_id }) => {
        const ctx = requireAuth(authContext, "share_experience");
        const result = shareExperience(title, content, ctx.agentId, { task_id });
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_share_experience", ctx.agentId, String(result.strategy.id), `title=${title.slice(0, 50)}, tags=${tags ? JSON.stringify(tags) : "none"}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id: result.strategy.id,
                        status: "approved",
                        category: "experience",
                        note: "经验已发布，所有 Agent 可通过 search_strategies 搜索到",
                    }, null, 2),
                }],
        };
    });
    // Tool E2: propose_strategy — member 及以上
    server.tool("propose_strategy", "提议一个策略。策略需 admin 审批后才能被其他 Agent 搜索和采纳。Hub 会自动判定敏感级别。", {
        title: z.string().min(3).max(200).describe("策略标题"),
        content: z.string().min(10).max(5000).describe("策略内容（Markdown，最多 5000 字符）"),
        category: z.enum(["workflow", "fix", "tool_config", "prompt_template", "other"])
            .describe("策略分类"),
        task_id: z.string().optional().describe("关联任务 ID"),
    }, async ({ title, content, category, task_id }) => {
        const ctx = requireAuth(authContext, "propose_strategy");
        const result = proposeStrategy(title, content, category, ctx.agentId, { task_id });
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_propose_strategy", ctx.agentId, String(result.strategy.id), `category=${category}, sensitivity=${result.sensitivity}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id: result.strategy.id,
                        status: "pending",
                        category,
                        sensitivity: result.sensitivity,
                        note: result.sensitivity === "high"
                            ? "⚠️ 高敏感策略，审批流程更严格"
                            : "策略已提交，等待 admin 审批",
                    }, null, 2),
                }],
        };
    });
    // Tool E3: list_strategies — member 及以上
    server.tool("list_strategies", "查询策略/经验列表。支持按状态、分类、提议者筛选。", {
        status: z.enum(["pending", "approved", "rejected", "all"]).optional().describe("状态筛选"),
        category: z.enum(["experience", "workflow", "fix", "tool_config", "prompt_template", "other", "all"]).optional().describe("分类筛选"),
        proposer_id: z.string().optional().describe("提议者 Agent ID"),
        limit: z.number().min(1).max(50).optional().default(20).describe("最大返回数量"),
    }, async ({ status, category, proposer_id, limit }) => {
        const ctx = requireAuth(authContext, "list_strategies");
        const strategies = listStrategies({ status, category, proposer_id, limit });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        strategies: strategies.map(s => ({
                            id: s.id,
                            title: s.title,
                            category: s.category,
                            sensitivity: s.sensitivity,
                            proposer_id: s.proposer_id,
                            status: s.status,
                            source_trust: s.source_trust,
                            apply_count: s.apply_count,
                            feedback_count: s.feedback_count,
                            positive_count: s.positive_count,
                            proposed_at: s.proposed_at,
                            approved_at: s.approved_at,
                        })),
                        count: strategies.length,
                        queried_by: ctx.agentId,
                    }, null, 2),
                }],
        };
    });
    // Tool E4: search_strategies — member 及以上
    server.tool("search_strategies", "通过关键词全文搜索策略和经验。仅返回已审批（approved）的策略。", {
        query: z.string().min(2).max(200).describe("搜索关键词（支持中文 N-gram 分词）"),
        category: z.string().optional().describe("分类筛选"),
        limit: z.number().min(1).max(20).optional().default(10).describe("最大返回数量"),
    }, async ({ query, category, limit }) => {
        const ctx = requireAuth(authContext, "search_strategies");
        const results = searchStrategies(query, { category, limit });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        query,
                        results: results.map(s => ({
                            id: s.id,
                            title: s.title,
                            content: s.content,
                            category: s.category,
                            proposer_id: s.proposer_id,
                            apply_count: s.apply_count,
                            feedback_count: s.feedback_count,
                            positive_count: s.positive_count,
                        })),
                        count: results.length,
                        queried_by: ctx.agentId,
                    }, null, 2),
                }],
        };
    });
    // Tool E5: apply_strategy — member 及以上
    server.tool("apply_strategy", "采纳一个已审批的策略。记录到策略应用记录中，apply_count 自增。", {
        strategy_id: z.number().describe("策略 ID"),
        context: z.string().max(500).optional().describe("应用场景描述"),
    }, async ({ strategy_id, context }) => {
        const ctx = requireAuth(authContext, "apply_strategy");
        const result = applyStrategy(strategy_id, ctx.agentId, { context });
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_apply_strategy", ctx.agentId, String(strategy_id));
        // Phase 2.2: 自动创建反馈占位（neutral），等待 7 天内更新
        let feedbackCreated = false;
        try {
            provideFeedback({
                strategyId: strategy_id,
                agentId: ctx.agentId,
                feedback: "neutral",
                comment: `自动创建反馈占位 - 策略 ${strategy_id} 被 ${ctx.agentId} 采纳，等待实际效果反馈`,
                applied: 1,
            });
            feedbackCreated = true;
        }
        catch {
            // Non-blocking — 不影响采纳成功
        }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        application_id: result.application_id,
                        strategy_id,
                        note: "策略已采纳，已记录应用历史",
                        feedback_reminder: feedbackCreated
                            ? "已自动创建反馈占位，请在 7 天内通过 feedback_strategy 工具更新实际效果"
                            : undefined,
                    }, null, 2),
                }],
        };
    });
    // Tool E6: feedback_strategy — member 及以上
    server.tool("feedback_strategy", "对策略提供反馈（正面/负面/中性）。每个 Agent 对每个策略只能反馈一次（防刷）。", {
        strategy_id: z.number().describe("策略 ID"),
        feedback: z.enum(["positive", "negative", "neutral"]).describe("反馈类型"),
        comment: z.string().max(500).optional().describe("反馈备注"),
        applied: z.boolean().optional().describe("是否实际采纳到工作中"),
    }, async ({ strategy_id, feedback, comment, applied }) => {
        const ctx = requireAuth(authContext, "feedback_strategy");
        const result = feedbackStrategy(strategy_id, ctx.agentId, feedback, { comment, applied });
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_feedback_strategy", ctx.agentId, String(strategy_id), `feedback=${feedback}`);
        // Phase 5a Day 2: 反馈影响信任评分
        try {
            recalculateTrustScore(ctx.agentId);
        }
        catch { }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        feedback_id: result.feedback_id,
                        strategy_id,
                        feedback,
                        note: "反馈已记录，感谢你的贡献",
                    }, null, 2),
                }],
        };
    });
    // Tool A1: approve_strategy — admin only
    server.tool("approve_strategy", "审批策略（approve/reject）。仅 admin 可调用。审批后通过 SSE 通知提议者。", {
        strategy_id: z.number().describe("策略 ID"),
        action: z.enum(["approve", "reject"]).describe("审批动作"),
        reason: z.string().max(1000).describe("审批理由"),
    }, async ({ strategy_id, action, reason }) => {
        const ctx = requireAuth(authContext, "approve_strategy");
        const result = approveStrategy(strategy_id, ctx.agentId, action, reason);
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_approve_strategy", ctx.agentId, String(strategy_id), `action=${action}, status=${result.strategy.status}`);
        // SSE 通知提议者（直接使用顶层 import 的 pushToAgent）
        pushToAgent(result.strategy.proposer_id, {
            event: "strategy_approved",
            strategy: {
                id: result.strategy.id,
                title: result.strategy.title,
                status: result.strategy.status,
                action,
                reason,
                approved_by: ctx.agentId,
                approved_at: Date.now(),
            },
        });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id: result.strategy.id,
                        new_status: result.strategy.status,
                        action,
                        reason,
                        proposer_notified: true,
                        note: action === "approve"
                            ? "策略已通过审批，所有 Agent 现在可以搜索和采纳"
                            : "策略已拒绝，提议者已收到通知",
                    }, null, 2),
                }],
        };
    });
    // Tool A2: get_evolution_status — member 及以上
    server.tool("get_evolution_status", "查看 Evolution Engine 进化指标统计。包含经验数、策略数、审批率、贡献者排名等。", {}, async () => {
        const ctx = requireAuth(authContext, "get_evolution_status");
        const stats = getEvolutionStatus();
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        ...stats,
                        queried_by: ctx.agentId,
                    }, null, 2),
                }],
        };
    });
    // Tool A3: score_applied_strategies — admin only (Phase 2.2)
    server.tool("score_applied_strategies", "自动评分已采纳策略：将 7 天前采纳但仍为 neutral 反馈的策略降为 negative。应定期调用。", {}, async () => {
        const ctx = requireAuth(authContext, "score_applied_strategies");
        const result = scoreAppliedStrategies();
        auditLog("tool_score_applied_strategies", ctx.agentId, `scored=${result.scored}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        scored: result.scored,
                        details: result.details,
                        note: result.scored > 0
                            ? `已自动降分 ${result.scored} 条策略反馈（7 天内无实际效果反馈）`
                            : "所有策略反馈均正常，无需降分",
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Phase 4b Day 4: 分级审批工具
    // ────────────────────────────────────────────────────
    // Tool T1: propose_strategy_tiered — member 及以上
    server.tool("propose_strategy_tiered", "提议策略（分级审批）。Hub 自动判定审批等级：auto（自动通过+72h观察窗口）、peer（同行审批）、admin（管理员审批）、super（高风险，需人工审批）。返回判定等级和审批状态。", {
        title: z.string().min(3).max(200).describe("策略标题"),
        content: z.string().min(10).max(5000).describe("策略内容（Markdown，最多 5000 字符）"),
        category: z.enum(["workflow", "fix", "tool_config", "prompt_template", "other"])
            .describe("策略分类"),
        task_id: z.string().optional().describe("关联任务 ID"),
    }, async ({ title, content, category, task_id }) => {
        const ctx = requireAuth(authContext, "propose_strategy_tiered");
        const result = proposeStrategyTiered(title, content, category, ctx.agentId, { task_id });
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        auditLog("tool_propose_strategy_tiered", ctx.agentId, String(result.strategy.id), `tier=${result.tier}, sensitivity=${result.sensitivity}, auto_approved=${result.auto_approved}`);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id: result.strategy.id,
                        status: result.strategy.status,
                        tier: result.tier,
                        sensitivity: result.sensitivity,
                        auto_approved: result.auto_approved,
                        veto_deadline: result.veto_deadline,
                        note: result.tier === "auto"
                            ? "✅ 自动通过审批，72h 观察窗口已启动"
                            : result.tier === "peer"
                                ? "📋 已提交，需 peer 审批"
                                : result.tier === "super"
                                    ? "⚠️ 高风险策略，需 super 人工审批"
                                    : "📋 已提交，需 admin 审批",
                    }, null, 2),
                }],
        };
    });
    // Tool T2: check_veto_window — member 及以上
    server.tool("check_veto_window", "检查策略的否决窗口状态。处于 48h 否决窗口内的策略，如果负面反馈超过正面反馈的 50%，可被 admin 撤回。", {
        strategy_id: z.number().describe("策略 ID"),
    }, async ({ strategy_id }) => {
        const ctx = requireAuth(authContext, "check_veto_window");
        const result = checkVetoWindow(strategy_id);
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id,
                        ...result,
                        note: result.in_window
                            ? result.can_veto
                                ? `⚠️ 否决窗口内，负面反馈比 ${result.veto_ratio} > 0.5，可被 admin 撤回`
                                : `🔒 否决窗口内，但负面反馈比 ${result.veto_ratio} <= 0.5，暂不可撤回`
                            : "否决窗口已过，策略已稳固",
                    }, null, 2),
                }],
        };
    });
    // Tool T3: veto_strategy — admin only
    server.tool("veto_strategy", "撤回处于否决窗口内的策略（admin only）。仅在负面反馈超过正面反馈 50% 时可用。", {
        strategy_id: z.number().describe("策略 ID"),
        reason: z.string().max(1000).describe("撤回理由"),
    }, async ({ strategy_id, reason }) => {
        const ctx = requireAuth(authContext, "veto_strategy");
        const result = vetoStrategyFromEvolution(strategy_id, ctx.agentId, reason);
        if (!result.ok) {
            return {
                content: [{ type: "text", text: JSON.stringify({ success: false, error: result.error }) }],
            };
        }
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        strategy_id,
                        new_status: "rejected",
                        vetoed_by: ctx.agentId,
                        reason,
                    }, null, 2),
                }],
        };
    });
}
//# sourceMappingURL=evolution.js.map