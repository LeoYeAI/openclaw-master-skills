/**
 * evolution.ts — Evolution Engine 简化版 (Phase 3)
 *
 * 功能：
 *   - shareExperience: 分享经验（直接 approved，不需审批）
 *   - proposeStrategy: 提议策略（pending，需 admin 审批 + Hub 自动判定 sensitivity）
 *   - listStrategies: 策略列表查询
 *   - searchStrategies: FTS5 搜索策略
 *   - applyStrategy: 采纳策略
 *   - feedbackStrategy: 对策略反馈（UNIQUE 防刷）
 *   - approveStrategy: admin 审批策略
 *   - getEvolutionStatus: 进化指标统计
 */
import { db } from "./db.js";
import { buildFtsTokens, buildSearchQuery } from "./tokenizer.js";
import { auditLog } from "./security.js";
import { logError } from "./logger.js";
// ─── 常量 ────────────────────────────────────────────────
const MAX_CONTENT_LENGTH = 5000;
const MAX_TITLE_LENGTH = 200;
// ─── sensitivity 判定 ────────────────────────────────────
/**
 * Hub 自动判定策略敏感级别（非 Agent 自报告）
 */
function judgeSensitivity(category, content) {
    // 高敏感分类：prompt_template 直接判定 high
    if (category === "prompt_template")
        return "high";
    // 高敏感关键词检测（结构化模式匹配）
    const highPatterns = [
        /system[_\s]*prompt/i,
        /系统指令/,
        /capability[_\s]*declare/i,
        /能力声明/,
        /permission[_\s]*(change|modify|grant)/i,
        /权限变更/,
        /role[_\s]*(change|escalat)/i,
    ];
    for (const pattern of highPatterns) {
        if (pattern.test(content))
            return "high";
    }
    return "normal";
}
// ─── 服务方法 ────────────────────────────────────────────
/**
 * 分享经验（直接 approved，不需审批）
 */
export function shareExperience(title, content, proposerId, options) {
    if (!title || title.trim().length < 3) {
        return { ok: false, error: "Title must be at least 3 characters" };
    }
    if (title.length > MAX_TITLE_LENGTH) {
        return { ok: false, error: `Title too long (${title.length} > ${MAX_TITLE_LENGTH})` };
    }
    if (!content || content.trim().length < 10) {
        return { ok: false, error: "Content must be at least 10 characters" };
    }
    if (content.length > MAX_CONTENT_LENGTH) {
        return { ok: false, error: `Content too long (${content.length} > ${MAX_CONTENT_LENGTH})` };
    }
    const now = Date.now();
    const trustScore = getAgentTrustScore(proposerId);
    try {
        const result = db.prepare(`INSERT INTO strategies (title, content, category, sensitivity, proposer_id, status, proposed_at, task_id, source_trust)
       VALUES (?, ?, 'experience', 'normal', ?, 'approved', ?, ?, ?)`).run(title.trim(), content.trim(), proposerId, now, options?.task_id ?? null, trustScore);
        const strategy = getStrategyById(result.lastInsertRowid);
        if (!strategy) {
            return { ok: false, error: "Failed to retrieve created strategy" };
        }
        // FTS 索引同步
        insertFtsEntry(strategy);
        return { ok: true, strategy };
    }
    catch (err) {
        return { ok: false, error: `Failed to share experience: ${err.message}` };
    }
}
/**
 * 提议策略（pending，需 admin 审批）
 */
export function proposeStrategy(title, content, category, proposerId, options) {
    if (!title || title.trim().length < 3) {
        return { ok: false, error: "Title must be at least 3 characters" };
    }
    if (title.length > MAX_TITLE_LENGTH) {
        return { ok: false, error: `Title too long (${title.length} > ${MAX_TITLE_LENGTH})` };
    }
    if (!content || content.trim().length < 10) {
        return { ok: false, error: "Content must be at least 10 characters" };
    }
    if (content.length > MAX_CONTENT_LENGTH) {
        return { ok: false, error: `Content too long (${content.length} > ${MAX_CONTENT_LENGTH})` };
    }
    const sensitivity = judgeSensitivity(category, content);
    const now = Date.now();
    const trustScore = getAgentTrustScore(proposerId);
    try {
        const result = db.prepare(`INSERT INTO strategies (title, content, category, sensitivity, proposer_id, status, proposed_at, task_id, source_trust)
       VALUES (?, ?, ?, ?, ?, 'pending', ?, ?, ?)`).run(title.trim(), content.trim(), category, sensitivity, proposerId, now, options?.task_id ?? null, trustScore);
        const strategy = getStrategyById(result.lastInsertRowid);
        if (!strategy) {
            return { ok: false, error: "Failed to retrieve created strategy" };
        }
        return { ok: true, strategy, sensitivity };
    }
    catch (err) {
        return { ok: false, error: `Failed to propose strategy: ${err.message}` };
    }
}
/**
 * 策略列表查询
 */
export function listStrategies(options) {
    const limit = Math.min(options?.limit ?? 50, 50);
    const conditions = [];
    const params = [];
    if (options?.status && options.status !== "all") {
        conditions.push("s.status = ?");
        params.push(options.status);
    }
    if (options?.category && options.category !== "all") {
        conditions.push("s.category = ?");
        params.push(options.category);
    }
    if (options?.proposer_id) {
        conditions.push("s.proposer_id = ?");
        params.push(options.proposer_id);
    }
    const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
    params.push(limit);
    try {
        return db.prepare(`SELECT s.* FROM strategies s ${where} ORDER BY s.proposed_at DESC LIMIT ?`).all(...params);
    }
    catch (err) {
        logError("evolution_listStrategies_error", err);
        return [];
    }
}
/**
 * FTS5 搜索策略（仅返回 approved 策略）
 */
export function searchStrategies(query, options) {
    if (!query || query.trim().length < 2)
        return [];
    const limit = Math.min(options?.limit ?? 20, 20);
    const safeQuery = buildSearchQuery(query);
    if (!safeQuery)
        return [];
    try {
        const conditions = [`strategies_fts MATCH ?`, `s.status = 'approved'`];
        const params = [safeQuery];
        if (options?.category) {
            conditions.push("s.category = ?");
            params.push(options.category);
        }
        params.push(limit);
        return db.prepare(`SELECT s.* FROM strategies s
       JOIN strategies_fts ON strategies_fts.rowid = s.id
       WHERE ${conditions.join(" AND ")}
       ORDER BY rank LIMIT ?`).all(...params);
    }
    catch (err) {
        logError("evolution_searchStrategies_error", err);
        return [];
    }
}
/**
 * 采纳策略（仅 approved 策略可采纳）
 */
export function applyStrategy(strategyId, agentId, options) {
    // 验证策略存在且 approved
    const strategy = getStrategyById(strategyId);
    if (!strategy) {
        return { ok: false, error: `Strategy ${strategyId} not found` };
    }
    if (strategy.status !== "approved") {
        return { ok: false, error: `Strategy ${strategyId} is not approved (status: ${strategy.status})` };
    }
    const now = Date.now();
    try {
        const result = db.prepare(`INSERT INTO strategy_applications (strategy_id, agent_id, context, created_at)
       VALUES (?, ?, ?, ?)`).run(strategyId, agentId, options?.context ?? null, now);
        // apply_count++
        db.prepare(`UPDATE strategies SET apply_count = apply_count + 1 WHERE id = ?`).run(strategyId);
        return { ok: true, application_id: result.lastInsertRowid };
    }
    catch (err) {
        return { ok: false, error: `Failed to apply strategy: ${err.message}` };
    }
}
/**
 * 对策略反馈（UNIQUE 防刷）
 */
export function feedbackStrategy(strategyId, agentId, feedback, options) {
    // 验证策略存在
    const strategy = getStrategyById(strategyId);
    if (!strategy) {
        return { ok: false, error: `Strategy ${strategyId} not found` };
    }
    const now = Date.now();
    const applied = options?.applied ? 1 : 0;
    try {
        const result = db.prepare(`INSERT INTO strategy_feedback (strategy_id, agent_id, feedback, comment, applied, created_at)
       VALUES (?, ?, ?, ?, ?, ?)`).run(strategyId, agentId, feedback, options?.comment ?? null, applied, now);
        // 更新计数器
        db.prepare(`UPDATE strategies SET feedback_count = feedback_count + 1,
       positive_count = positive_count + CASE WHEN ? = 'positive' THEN 1 ELSE 0 END
       WHERE id = ?`).run(feedback, strategyId);
        return { ok: true, feedback_id: result.lastInsertRowid };
    }
    catch (err) {
        // UNIQUE 约束冲突 = 重复反馈
        if (err.message.includes("UNIQUE")) {
            return { ok: false, error: "You have already provided feedback for this strategy" };
        }
        return { ok: false, error: `Failed to submit feedback: ${err.message}` };
    }
}
/**
 * admin 审批策略（approve/reject）
 */
export function approveStrategy(strategyId, adminId, action, reason) {
    if (!reason || reason.trim().length === 0) {
        return { ok: false, error: "Approval reason is required" };
    }
    if (reason.length > 1000) {
        return { ok: false, error: "Reason too long (max 1000 characters)" };
    }
    const strategy = getStrategyById(strategyId);
    if (!strategy) {
        return { ok: false, error: `Strategy ${strategyId} not found` };
    }
    if (strategy.status !== "pending") {
        return { ok: false, error: `Strategy ${strategyId} is not pending (status: ${strategy.status})` };
    }
    const newStatus = action === "approve" ? "approved" : "rejected";
    const now = Date.now();
    try {
        db.prepare(`UPDATE strategies SET status = ?, approve_reason = ?, approved_by = ?, approved_at = ? WHERE id = ?`).run(newStatus, reason.trim(), adminId, now, strategyId);
        // 如果 approved，同步 FTS 索引
        if (action === "approve") {
            insertFtsEntry(getStrategyById(strategyId));
        }
        const updated = getStrategyById(strategyId);
        return { ok: true, strategy: updated };
    }
    catch (err) {
        return { ok: false, error: `Failed to approve/reject strategy: ${err.message}` };
    }
}
/**
 * 进化指标统计
 */
export function getEvolutionStatus() {
    try {
        const totalExperiences = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE category = 'experience'`).get()?.cnt ?? 0;
        const totalStrategies = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE category != 'experience'`).get()?.cnt ?? 0;
        const pendingApproval = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE status = 'pending'`).get()?.cnt ?? 0;
        const approvedCount = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE status = 'approved'`).get()?.cnt ?? 0;
        const rejectedCount = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE status = 'rejected'`).get()?.cnt ?? 0;
        const totalApplications = db.prepare(`SELECT COUNT(*) as cnt FROM strategy_applications`).get()?.cnt ?? 0;
        const totalFeedback = db.prepare(`SELECT COUNT(*) as cnt FROM strategy_feedback`).get()?.cnt ?? 0;
        const positiveFeedback = db.prepare(`SELECT COUNT(*) as cnt FROM strategy_feedback WHERE feedback = 'positive'`).get()?.cnt ?? 0;
        const total = totalExperiences + totalStrategies;
        const approvedRate = total > 0 ? Math.round((approvedCount / total) * 10000) / 100 : 0;
        // Top contributors
        const contributors = db.prepare(`SELECT s.proposer_id as agent_id, COUNT(*) as count, COALESCE(a.trust_score, 50) as trust_score
       FROM strategies s
       LEFT JOIN agents a ON s.proposer_id = a.agent_id
       GROUP BY s.proposer_id
       ORDER BY count DESC LIMIT 10`).all();
        // Recent approved (last 5)
        const recentApproved = db.prepare(`SELECT * FROM strategies WHERE status = 'approved' ORDER BY approved_at DESC LIMIT 5`).all();
        return {
            total_experiences: totalExperiences,
            total_strategies: totalStrategies,
            pending_approval: pendingApproval,
            approved_count: approvedCount,
            rejected_count: rejectedCount,
            total_applications: totalApplications,
            total_feedback: totalFeedback,
            positive_feedback: positiveFeedback,
            approved_rate: approvedRate,
            top_contributors: contributors,
            recent_approved: recentApproved,
        };
    }
    catch (err) {
        logError("evolution_getEvolutionStatus_error", err);
        return {
            total_experiences: 0, total_strategies: 0, pending_approval: 0,
            approved_count: 0, rejected_count: 0, total_applications: 0,
            total_feedback: 0, positive_feedback: 0, approved_rate: 0,
            top_contributors: [], recent_approved: [],
        };
    }
}
/** 审批等级判定阈值 */
const TIER_THRESHOLDS = {
    auto: { minTrust: 90, maxRisk: "normal", requireHistory: 5 }, // 高信任+低风险+有历史 → 自动通过
    peer: { minTrust: 60, maxRisk: "normal", requireHistory: 2 }, // 中等信任+低风险 → peer 审批
    admin: { minTrust: 0, maxRisk: "any", requireHistory: 0 }, // 默认 → admin 审批
    super: { maxRisk: "high" }, // 高风险 → super 审批（需人工）
};
/** 观察窗口时长：72h */
const OBSERVATION_WINDOW_MS = 72 * 60 * 60 * 1000;
/** 否决窗口时长：48h */
const VETO_WINDOW_MS = 48 * 60 * 60 * 1000;
// ─── 分级判定 ────────────────────────────────────────────
/**
 * 判定策略审批等级
 *
 * 4 级 tier 规则：
 * 1. super: sensitivity=high → 需人工审批（最高权限）
 * 2. auto: trust≥90 + sensitivity=normal + 历史≥5 → 自动通过 + 72h 观察窗口
 * 3. peer: trust≥60 + sensitivity=normal + 历史≥2 → peer 审批
 * 4. admin: 其他 → admin 审批
 */
export function judgeTier(proposerId, category, content) {
    const sensitivity = judgeSensitivity(category, content);
    const trustScore = getAgentTrustScore(proposerId);
    const historyCount = getStrategyHistoryCount(proposerId);
    // 规则 1: super — 高风险策略
    if (sensitivity === "high") {
        return {
            tier: "super",
            reason: `高风险策略（sensitivity=high），需 super 人工审批`,
            trust_score: trustScore,
            sensitivity,
            history_count: historyCount,
        };
    }
    // 规则 2: auto — 高信任+低风险+有历史
    if (trustScore >= TIER_THRESHOLDS.auto.minTrust &&
        historyCount >= TIER_THRESHOLDS.auto.requireHistory) {
        return {
            tier: "auto",
            reason: `高信任策略（trust=${trustScore}, history=${historyCount}），自动通过 + 72h 观察窗口`,
            trust_score: trustScore,
            sensitivity,
            history_count: historyCount,
        };
    }
    // 规则 3: peer — 中等信任+低风险+有少量历史
    if (trustScore >= TIER_THRESHOLDS.peer.minTrust &&
        historyCount >= TIER_THRESHOLDS.peer.requireHistory) {
        return {
            tier: "peer",
            reason: `中等信任策略（trust=${trustScore}, history=${historyCount}），需 peer 审批`,
            trust_score: trustScore,
            sensitivity,
            history_count: historyCount,
        };
    }
    // 规则 4: admin — 默认
    return {
        tier: "admin",
        reason: `默认审批（trust=${trustScore}, history=${historyCount}），需 admin 审批`,
        trust_score: trustScore,
        sensitivity,
        history_count: historyCount,
    };
}
/**
 * 自动通过策略（auto tier）
 * 设置 approved + 启动 72h 观察窗口
 */
export function autoApprove(strategyId) {
    const strategy = getStrategyById(strategyId);
    if (!strategy) {
        return { ok: false, error: `Strategy ${strategyId} not found` };
    }
    if (strategy.status !== "pending") {
        return { ok: false, error: `Strategy ${strategyId} is not pending (status: ${strategy.status})` };
    }
    const now = Date.now();
    const vetoDeadline = now + VETO_WINDOW_MS;
    // 更新：approved + 观察窗口 + 否决窗口
    db.prepare(`UPDATE strategies SET status='approved', approval_tier='auto',
     approved_at=?, approved_by='system:auto',
     observation_start=?, veto_deadline=?
     WHERE id=?`).run(now, now, vetoDeadline, strategyId);
    // FTS 索引同步
    const updated = getStrategyWithTier(strategyId);
    if (updated) {
        insertFtsEntry(updated);
    }
    auditLog("auto_approve", "system:auto", String(strategyId), `veto_deadline=${vetoDeadline}`);
    if (!updated) {
        return { ok: false, error: "Failed to retrieve updated strategy" };
    }
    return { ok: true, strategy: updated };
}
/**
 * 启动观察窗口（peer tier 策略被 peer 审批通过后调用）
 * 72h 观察窗口内如果负面反馈超过阈值，策略可被撤回
 */
export function startObservation(strategyId, approverId) {
    const strategy = getStrategyById(strategyId);
    if (!strategy) {
        return { ok: false, error: `Strategy ${strategyId} not found` };
    }
    if (strategy.status !== "approved") {
        return { ok: false, error: `Strategy ${strategyId} is not approved` };
    }
    const now = Date.now();
    const vetoDeadline = now + VETO_WINDOW_MS;
    db.prepare(`UPDATE strategies SET approval_tier='peer', observation_start=?, veto_deadline=?
     WHERE id=?`).run(now, vetoDeadline, strategyId);
    auditLog("start_observation", approverId, String(strategyId), `veto_deadline=${vetoDeadline}`);
    const updated = getStrategyWithTier(strategyId);
    if (!updated) {
        return { ok: false, error: "Failed to retrieve updated strategy" };
    }
    return { ok: true, strategy: updated, veto_deadline: vetoDeadline };
}
/**
 * 检查否决窗口（48h）
 * 在否决窗口内，如果负面反馈超过正面反馈的 50%，任何 admin 可以撤回策略
 */
export function checkVetoWindow(strategyId) {
    const strategy = db.prepare(`SELECT veto_deadline, observation_start, positive_count, feedback_count
     FROM strategies WHERE id=?`).get(strategyId);
    if (!strategy) {
        return {
            in_window: false, can_veto: false,
            negative_count: 0, positive_count: 0, veto_ratio: 0,
            veto_deadline: null, observation_start: null,
        };
    }
    const now = Date.now();
    const negativeCount = (strategy.feedback_count ?? 0) - (strategy.positive_count ?? 0);
    // 否决窗口判断
    const inWindow = strategy.veto_deadline && now < strategy.veto_deadline;
    // 否决条件：负面超过正面的 50%
    const positiveCount = strategy.positive_count ?? 0;
    const vetoRatio = positiveCount > 0 ? negativeCount / positiveCount : (negativeCount > 0 ? 1 : 0);
    const canVeto = inWindow && vetoRatio > 0.5;
    return {
        in_window: !!inWindow,
        can_veto: canVeto,
        negative_count: negativeCount,
        positive_count: positiveCount,
        veto_ratio: Math.round(vetoRatio * 100) / 100,
        veto_deadline: strategy.veto_deadline,
        observation_start: strategy.observation_start,
    };
}
/**
 * 撤回处于否决窗口内的策略
 */
export function vetoStrategy(strategyId, adminId, reason) {
    // 验证否决窗口
    const vetoCheck = checkVetoWindow(strategyId);
    if (!vetoCheck.in_window) {
        return { ok: false, error: "Strategy is not in veto window" };
    }
    if (!vetoCheck.can_veto) {
        return { ok: false, error: `Cannot veto: veto ratio ${vetoCheck.veto_ratio} <= 0.5 threshold` };
    }
    const now = Date.now();
    db.prepare(`UPDATE strategies SET status='rejected', approval_tier='vetoed',
     approve_reason=?, approved_by=?, approved_at=?,
     observation_start=null, veto_deadline=null
     WHERE id=?`).run(reason, adminId, now, strategyId);
    // 从 FTS 移除
    db.prepare(`DELETE FROM strategies_fts WHERE rowid=?`).run(strategyId);
    // Phase 5a Day 2: 审计 FTS 索引删除
    auditLog("delete_strategy_fts", adminId, String(strategyId), `reason=${reason}`);
    auditLog("veto_strategy", adminId, String(strategyId), `reason=${reason}`);
    const updated = getStrategyById(strategyId);
    if (!updated) {
        return { ok: false, error: "Failed to retrieve updated strategy" };
    }
    return { ok: true, strategy: updated };
}
/**
 * 分级策略提议（统一入口）
 * 自动判定 tier 并执行对应流程
 */
export function proposeStrategyTiered(title, content, category, proposerId, options) {
    // 基础校验
    if (!title || title.trim().length < 3) {
        return { ok: false, error: "Title must be at least 3 characters" };
    }
    if (title.length > MAX_TITLE_LENGTH) {
        return { ok: false, error: `Title too long (${title.length} > ${MAX_TITLE_LENGTH})` };
    }
    if (!content || content.trim().length < 10) {
        return { ok: false, error: "Content must be at least 10 characters" };
    }
    if (content.length > MAX_CONTENT_LENGTH) {
        return { ok: false, error: `Content too long (${content.length} > ${MAX_CONTENT_LENGTH})` };
    }
    // 判定分级
    const judgment = judgeTier(proposerId, category, content);
    const sensitivity = judgment.sensitivity;
    const now = Date.now();
    const trustScore = getAgentTrustScore(proposerId);
    try {
        // 创建策略（初始 pending）
        const result = db.prepare(`INSERT INTO strategies (title, content, category, sensitivity, proposer_id,
       status, proposed_at, task_id, source_trust, approval_tier)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`).run(title.trim(), content.trim(), category, sensitivity, proposerId, "pending", now, options?.task_id ?? null, trustScore, judgment.tier);
        const strategyId = result.lastInsertRowid;
        let autoApproved = false;
        let vetoDeadline = null;
        if (judgment.tier === "auto") {
            // auto tier: 自动通过 + 启动观察窗口
            const approveResult = autoApprove(strategyId);
            if (approveResult.ok) {
                autoApproved = true;
                vetoDeadline = approveResult.strategy.veto_deadline;
            }
        }
        // peer / admin / super: 保持 pending 状态
        const strategy = getStrategyWithTier(strategyId);
        if (!strategy) {
            return { ok: false, error: "Failed to retrieve created strategy" };
        }
        return {
            ok: true,
            strategy,
            tier: judgment.tier,
            sensitivity,
            auto_approved: autoApproved,
            veto_deadline: vetoDeadline,
        };
    }
    catch (err) {
        return { ok: false, error: `Failed to propose strategy: ${err.message}` };
    }
}
// ─── 内部辅助函数 ────────────────────────────────────────
function getStrategyById(id) {
    return db.prepare(`SELECT * FROM strategies WHERE id = ?`).get(id);
}
function getStrategyWithTier(id) {
    return db.prepare(`SELECT * FROM strategies WHERE id = ?`).get(id);
}
function getStrategyHistoryCount(proposerId) {
    try {
        const row = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE proposer_id = ? AND status = 'approved'`).get(proposerId);
        return row?.cnt ?? 0;
    }
    catch {
        return 0;
    }
}
function getAgentTrustScore(agentId) {
    try {
        const row = db.prepare(`SELECT trust_score FROM agents WHERE agent_id = ?`).get(agentId);
        return row?.trust_score ?? 50;
    }
    catch {
        return 50;
    }
}
function insertFtsEntry(strategy) {
    try {
        const tokens = buildFtsTokens(strategy.title, strategy.content);
        db.prepare(`INSERT INTO strategies_fts (rowid, title, content, category) VALUES (?, ?, ?, ?)`).run(strategy.id, strategy.title, tokens, strategy.category);
    }
    catch (err) {
        logError("evolution_fts_insert_error", err);
    }
}
// ─── Phase 2.2: 策略采纳闭环 ─────────────────────────────────
/**
 * 提供反馈（UPSERT 版本）— 用于自动创建反馈占位和后续更新
 * 与 feedbackStrategy 不同：使用 ON CONFLICT DO UPDATE 而非拒绝重复
 */
export function provideFeedback(params) {
    const now = Date.now();
    try {
        const result = db.prepare(`
      INSERT INTO strategy_feedback (strategy_id, agent_id, feedback, comment, applied, created_at)
      VALUES (?, ?, ?, ?, ?, ?)
      ON CONFLICT(strategy_id, agent_id) DO UPDATE SET
        feedback = excluded.feedback,
        comment = excluded.comment,
        applied = excluded.applied
    `).run(params.strategyId, params.agentId, params.feedback, params.comment || null, params.applied ?? 0, now);
        return { id: result.lastInsertRowid };
    }
    catch (err) {
        throw new Error(`创建反馈失败: ${err.message}`);
    }
}
/**
 * 自动评分已采纳策略
 * 将 7 天内仍为 neutral 反馈的策略降为 negative（无实际效果证据）
 * 应由 cron 或清理任务定期调用
 */
export function scoreAppliedStrategies() {
    const sevenDaysAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
    // 查找 7 天前创建的 neutral 反馈
    const staleFeedbacks = db.prepare(`
    SELECT sf.strategy_id, sf.agent_id, sf.id as feedback_id, s.title
    FROM strategy_feedback sf
    JOIN strategies s ON s.id = sf.strategy_id
    WHERE sf.feedback = 'neutral'
      AND sf.created_at < ?
      AND s.approved = 1
  `).all(sevenDaysAgo);
    const details = [];
    let scored = 0;
    for (const fb of staleFeedbacks) {
        // 检查是否有其他 agent 给了非 neutral 反馈
        const otherFeedback = db.prepare(`
      SELECT feedback FROM strategy_feedback
      WHERE strategy_id = ? AND agent_id != ? AND feedback != 'neutral'
    `).all(fb.strategy_id, fb.agent_id);
        if (otherFeedback.length === 0) {
            // 无人提供有效反馈 → 降分为 negative
            db.prepare(`UPDATE strategy_feedback SET feedback = 'negative', comment = ? WHERE id = ?`).run("自动降分：采纳后 7 天内无实际效果反馈", fb.feedback_id);
            // 同步减少 positive_count（如果之前因 neutral 未增加则无需操作）
            details.push({
                strategyId: fb.strategy_id,
                title: fb.title,
                action: "neutral→negative (7天无反馈)",
            });
            scored++;
        }
    }
    if (scored > 0) {
        logError("evolution_auto_score", new Error(`Auto-scored ${scored} stale feedbacks`));
    }
    return { scored, details };
}
//# sourceMappingURL=evolution.js.map