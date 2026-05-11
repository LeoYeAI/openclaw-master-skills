export interface Strategy {
    id: number;
    title: string;
    content: string;
    category: "experience" | "workflow" | "fix" | "tool_config" | "prompt_template" | "other";
    sensitivity: "normal" | "high";
    proposer_id: string;
    status: "pending" | "approved" | "rejected" | "withdrawn";
    approve_reason: string | null;
    approved_by: string | null;
    approved_at: number | null;
    proposed_at: number;
    task_id: string | null;
    source_trust: number;
    apply_count: number;
    feedback_count: number;
    positive_count: number;
}
export interface StrategyFeedback {
    strategy_id: number;
    agent_id: string;
    feedback: "positive" | "negative" | "neutral";
    comment: string | null;
    applied: number;
    created_at: number;
}
export interface StrategyApplication {
    strategy_id: number;
    agent_id: string;
    context: string | null;
    result: string | null;
    created_at: number;
}
export interface EvolutionStats {
    total_experiences: number;
    total_strategies: number;
    pending_approval: number;
    approved_count: number;
    rejected_count: number;
    total_applications: number;
    total_feedback: number;
    positive_feedback: number;
    approved_rate: number;
    top_contributors: Array<{
        agent_id: string;
        count: number;
        trust_score: number;
    }>;
    recent_approved: Strategy[];
}
/**
 * 分享经验（直接 approved，不需审批）
 */
export declare function shareExperience(title: string, content: string, proposerId: string, options?: {
    tags?: string[];
    task_id?: string;
}): {
    ok: true;
    strategy: Strategy;
} | {
    ok: false;
    error: string;
};
/**
 * 提议策略（pending，需 admin 审批）
 */
export declare function proposeStrategy(title: string, content: string, category: "workflow" | "fix" | "tool_config" | "prompt_template" | "other", proposerId: string, options?: {
    task_id?: string;
}): {
    ok: true;
    strategy: Strategy;
    sensitivity: string;
} | {
    ok: false;
    error: string;
};
/**
 * 策略列表查询
 */
export declare function listStrategies(options?: {
    status?: "pending" | "approved" | "rejected" | "all";
    category?: "experience" | "workflow" | "fix" | "tool_config" | "prompt_template" | "other" | "all";
    proposer_id?: string;
    limit?: number;
}): Strategy[];
/**
 * FTS5 搜索策略（仅返回 approved 策略）
 */
export declare function searchStrategies(query: string, options?: {
    category?: string;
    limit?: number;
}): Strategy[];
/**
 * 采纳策略（仅 approved 策略可采纳）
 */
export declare function applyStrategy(strategyId: number, agentId: string, options?: {
    context?: string;
}): {
    ok: true;
    application_id: number;
} | {
    ok: false;
    error: string;
};
/**
 * 对策略反馈（UNIQUE 防刷）
 */
export declare function feedbackStrategy(strategyId: number, agentId: string, feedback: "positive" | "negative" | "neutral", options?: {
    comment?: string;
    applied?: boolean;
}): {
    ok: true;
    feedback_id: number;
} | {
    ok: false;
    error: string;
};
/**
 * admin 审批策略（approve/reject）
 */
export declare function approveStrategy(strategyId: number, adminId: string, action: "approve" | "reject", reason: string): {
    ok: true;
    strategy: Strategy;
} | {
    ok: false;
    error: string;
};
/**
 * 进化指标统计
 */
export declare function getEvolutionStatus(): EvolutionStats;
/** 审批等级 */
export type ApprovalTier = "auto" | "peer" | "admin" | "super";
export interface TieredStrategy extends Strategy {
    approval_tier: ApprovalTier | null;
    observation_start: number | null;
    veto_deadline: number | null;
}
export interface TierJudgment {
    tier: ApprovalTier;
    reason: string;
    trust_score: number;
    sensitivity: "normal" | "high";
    history_count: number;
}
/**
 * 判定策略审批等级
 *
 * 4 级 tier 规则：
 * 1. super: sensitivity=high → 需人工审批（最高权限）
 * 2. auto: trust≥90 + sensitivity=normal + 历史≥5 → 自动通过 + 72h 观察窗口
 * 3. peer: trust≥60 + sensitivity=normal + 历史≥2 → peer 审批
 * 4. admin: 其他 → admin 审批
 */
export declare function judgeTier(proposerId: string, category: string, content: string): TierJudgment;
/**
 * 自动通过策略（auto tier）
 * 设置 approved + 启动 72h 观察窗口
 */
export declare function autoApprove(strategyId: number): {
    ok: true;
    strategy: TieredStrategy;
} | {
    ok: false;
    error: string;
};
/**
 * 启动观察窗口（peer tier 策略被 peer 审批通过后调用）
 * 72h 观察窗口内如果负面反馈超过阈值，策略可被撤回
 */
export declare function startObservation(strategyId: number, approverId: string): {
    ok: true;
    strategy: TieredStrategy;
    veto_deadline: number;
} | {
    ok: false;
    error: string;
};
/**
 * 检查否决窗口（48h）
 * 在否决窗口内，如果负面反馈超过正面反馈的 50%，任何 admin 可以撤回策略
 */
export declare function checkVetoWindow(strategyId: number): {
    in_window: boolean;
    can_veto: boolean;
    negative_count: number;
    positive_count: number;
    veto_ratio: number;
    veto_deadline: number | null;
    observation_start: number | null;
};
/**
 * 撤回处于否决窗口内的策略
 */
export declare function vetoStrategy(strategyId: number, adminId: string, reason: string): {
    ok: true;
    strategy: Strategy;
} | {
    ok: false;
    error: string;
};
/**
 * 分级策略提议（统一入口）
 * 自动判定 tier 并执行对应流程
 */
export declare function proposeStrategyTiered(title: string, content: string, category: "workflow" | "fix" | "tool_config" | "prompt_template" | "other", proposerId: string, options?: {
    task_id?: string;
}): {
    ok: true;
    strategy: TieredStrategy;
    tier: ApprovalTier;
    sensitivity: string;
    auto_approved: boolean;
    veto_deadline: number | null;
} | {
    ok: false;
    error: string;
};
/**
 * 提供反馈（UPSERT 版本）— 用于自动创建反馈占位和后续更新
 * 与 feedbackStrategy 不同：使用 ON CONFLICT DO UPDATE 而非拒绝重复
 */
export declare function provideFeedback(params: {
    strategyId: number;
    agentId: string;
    feedback: string;
    comment?: string;
    applied?: number;
}): {
    id: number;
};
/**
 * 自动评分已采纳策略
 * 将 7 天内仍为 neutral 反馈的策略降为 negative（无实际效果证据）
 * 应由 cron 或清理任务定期调用
 */
export declare function scoreAppliedStrategies(): {
    scored: number;
    details: Array<{
        strategyId: number;
        title: string;
        action: string;
    }>;
};
