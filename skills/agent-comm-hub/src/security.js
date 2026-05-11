/**
 * security.ts — Security Guard
 * Token 认证 + 速率限制 + MCP 工具权限矩阵 + 邀请码 + 审计日志
 *
 * 踩坑经验：
 *   - better-sqlite3 不接受 JS boolean，必须用 1/0
 *   - better-sqlite3 不接受 undefined，必须用 null
 *   - optionalAuth 未认证时不要默认创建 authContext
 */
import { createHash, randomBytes } from "crypto";
import { db } from "./db.js";
import { logError } from "./logger.js";
// ─── Token 工具函数 ──────────────────────────────────────
/** SHA-256 哈希 */
export function sha256(input) {
    return createHash("sha256").update(input).digest("hex");
}
/** 生成明文 Token（一次性返回） */
export function generateToken() {
    return randomBytes(32).toString("hex"); // 64 字符明文 Token
}
/** 验证 Token 并返回 AuthContext，失败返回 null */
export function verifyToken(plainToken) {
    const hash = sha256(plainToken);
    const row = db
        .prepare(`SELECT agent_id, role FROM auth_tokens
       WHERE token_type='api_token' AND token_value=? AND used=1 AND revoked_at IS NULL`)
        .get(hash);
    if (!row)
        return null;
    // 检查是否过期
    const expiresRow = db
        .prepare(`SELECT expires_at FROM auth_tokens WHERE token_value=?`)
        .get(hash);
    if (expiresRow?.expires_at && Date.now() > expiresRow.expires_at) {
        return null;
    }
    return { agentId: row.agent_id, role: row.role };
}
// ─── 速率限制 ────────────────────────────────────────────
const rateLimitMap = new Map();
const RATE_LIMIT_WINDOW = parseInt(process.env.RATE_LIMIT_WINDOW ?? "1000", 10); // 默认 1 秒窗口
const RATE_LIMIT_MAX = parseInt(process.env.RATE_LIMIT_MAX ?? "10", 10); // 默认每秒 10 请求
export function rateLimiter(agentId) {
    const now = Date.now();
    const entry = rateLimitMap.get(agentId);
    if (!entry || now - entry.windowStart > RATE_LIMIT_WINDOW) {
        rateLimitMap.set(agentId, { count: 1, windowStart: now });
        return true;
    }
    entry.count++;
    return entry.count <= RATE_LIMIT_MAX;
}
export const TOOL_PERMISSIONS = {
    // 注册免认证
    register_agent: "public",
    // 心跳与查询 — member 及以上
    heartbeat: "member",
    query_agents: "member",
    get_online_agents: "member",
    // 消息与任务 — member 及以上
    send_message: "member",
    assign_task: "member",
    update_task_status: "member",
    get_task_status: "member",
    broadcast_message: "member",
    acknowledge_message: "member",
    mark_consumed: "member",
    check_consumed: "member",
    // 记忆 — member 及以上
    store_memory: "member",
    recall_memory: "member",
    list_memories: "member",
    delete_memory: "member",
    // 管理 — 仅 admin
    revoke_token: "admin",
    set_trust_score: "admin",
    set_agent_role: "admin", // Phase 5a: 任命/撤销 group_admin
    recalculate_trust_scores: "admin", // Phase 5a: 手动重算信任分
    // Phase 3: Evolution Engine
    share_experience: "member",
    propose_strategy: "member",
    list_strategies: "member",
    search_strategies: "member",
    apply_strategy: "member",
    feedback_strategy: "member",
    approve_strategy: "admin", // 审批仅 admin
    get_evolution_status: "member",
    // Phase 4b Day 2: 依赖链 + 并行组
    add_dependency: "member",
    remove_dependency: "member",
    get_task_dependencies: "member",
    create_parallel_group: "member",
    // Phase 4b Day 3: 交接协议 + 质量门
    request_handoff: "member",
    accept_handoff: "member",
    reject_handoff: "member",
    add_quality_gate: "member",
    evaluate_quality_gate: "member",
    // Phase 4b Day 4: 分级审批
    propose_strategy_tiered: "member",
    check_veto_window: "member",
    veto_strategy: "admin",
    // Phase 2.2: 策略采纳闭环
    score_applied_strategies: "admin",
    // v2.3 Phase 1.1: 文件传输
    upload_file: "member",
    download_file: "member",
    list_attachments: "member",
    // v2.3 Phase 3.2: 数据库维护
    get_db_stats: "admin",
    archive_data: "admin",
};
/**
 * 检查工具调用权限
 * group_admin 权限等同于 member（仅任务相关工具），其余 admin 工具不可用
 * @returns true=允许, false=拒绝
 */
export function checkPermission(toolName, role) {
    const level = TOOL_PERMISSIONS[toolName];
    if (!level) {
        // 未注册的工具默认 member 可访问
        return true;
    }
    if (level === "public")
        return true;
    if (level === "member")
        return true;
    if (level === "admin")
        return role === "admin";
    return false;
}
/**
 * 获取权限级别（用于返回错误信息）
 */
export function getRequiredPermission(toolName) {
    return TOOL_PERMISSIONS[toolName];
}
// ─── Express 中间件 ──────────────────────────────────────
/**
 * 强制认证中间件 — 所有 API/MCP 端点使用
 * 无有效 Token → 401
 */
export function authMiddleware(req, res, next) {
    const token = extractToken(req);
    if (!token) {
        res.status(401).json({ error: "Missing authentication token" });
        return;
    }
    const ctx = verifyToken(token);
    if (!ctx) {
        res.status(401).json({ error: "Invalid or expired token" });
        return;
    }
    // 速率限制
    if (!rateLimiter(ctx.agentId)) {
        res.status(429).json({ error: "Rate limit exceeded (10 req/s)" });
        return;
    }
    // 将认证信息挂载到 req 上
    req.auth = { agent: ctx };
    next();
}
/**
 * 可选认证中间件 — SSE 端点使用
 * 有 Token 则验证，无 Token 则 auth = undefined
 * ⚠️ 关键：未认证时 auth 必须为 undefined，不能创建默认 authContext
 */
export function optionalAuthMiddleware(req, res, next) {
    const token = extractToken(req);
    if (!token) {
        req.auth = { agent: undefined };
        next();
        return;
    }
    const ctx = verifyToken(token);
    req.auth = { agent: ctx ?? undefined }; // undefined 不是 null
    next();
}
/** 从 Header 或 Query 提取 Token */
function extractToken(req) {
    // Header: Authorization: Bearer <token>
    const authHeader = req.headers.authorization;
    if (authHeader?.startsWith("Bearer ")) {
        return authHeader.slice(7);
    }
    // Query: ?token=<token>
    const queryToken = req.query.token;
    if (queryToken) {
        return queryToken;
    }
    // x-api-key header
    const apiKey = req.headers["x-api-key"];
    if (apiKey) {
        return apiKey;
    }
    return null;
}
// ─── 邀请码管理 ──────────────────────────────────────────
/**
 * 生成邀请码（明文）
 * @returns 明文邀请码
 */
export function generateInviteCode() {
    return randomBytes(4).toString("hex"); // 8 字符
}
/**
 * 创建邀请码记录
 * @returns 明文邀请码（唯一一次可见）
 */
export function createInviteCode(role = "member") {
    const plain = generateInviteCode();
    const hash = sha256(plain);
    const now = Date.now();
    const expiresAt = now + 24 * 60 * 60 * 1000; // 24 小时有效
    db.prepare(`INSERT INTO auth_tokens (token_id, token_type, token_value, role, used, created_at, expires_at)
     VALUES (?, 'invite_code', ?, ?, 0, ?, ?)`).run(`invite_${now}_${randomBytes(4).toString("hex")}`, hash, role, now, expiresAt);
    return plain;
}
/**
 * 验证邀请码并标记已使用
 * @returns 有效邀请码的角色，或 null
 */
export function verifyInviteCode(plainCode) {
    const hash = sha256(plainCode);
    const row = db
        .prepare(`SELECT role, expires_at FROM auth_tokens
       WHERE token_type='invite_code' AND token_value=? AND used=0 AND revoked_at IS NULL`)
        .get(hash);
    if (!row)
        return null;
    // 检查过期
    if (row.expires_at && Date.now() > row.expires_at) {
        return null;
    }
    return row.role;
}
/**
 * 标记邀请码已使用
 */
export function markInviteCodeUsed(plainCode) {
    const hash = sha256(plainCode);
    db.prepare(`UPDATE auth_tokens SET used=1 WHERE token_type='invite_code' AND token_value=?`).run(hash);
}
// ─── Token 吊销 ──────────────────────────────────────────
/**
 * 吊销 API Token
 */
export function revokeToken(tokenId) {
    const now = Date.now();
    const result = db
        .prepare(`UPDATE auth_tokens SET revoked_at=? WHERE token_id=? AND token_type='api_token'`)
        .run(now, tokenId);
    return result.changes > 0;
}
// ─── 审计日志（Phase 5a: 哈希链防篡改） ─────────────────
/**
 * 记录审计日志（带哈希链）
 * 每条记录包含 prev_hash 和 record_hash，形成不可篡改链
 */
export function auditLog(action, agentId, target, details) {
    const id = `audit_${Date.now()}_${randomBytes(4).toString("hex")}`;
    const now = Date.now();
    try {
        // 获取上一条记录的 record_hash
        const lastRow = db.prepare(`SELECT record_hash FROM audit_log ORDER BY created_at DESC, id DESC LIMIT 1`).get();
        const prevHash = lastRow?.record_hash ?? "GENESIS";
        // 计算当前记录的 hash
        const hashInput = `${prevHash}|${action}|${agentId ?? ""}|${target ?? ""}|${details ?? ""}|${now}`;
        const recordHash = createHash("sha256").update(hashInput).digest("hex");
        db.prepare(`INSERT INTO audit_log (id, action, agent_id, target, details, prev_hash, record_hash, created_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`).run(id, action, agentId, target || null, details || null, prevHash, recordHash, now);
    }
    catch (err) {
        logError("audit_log_failed", err);
    }
}
/**
 * 验证审计日志哈希链完整性
 * @returns { valid, total, checked, firstBreak } — valid=true 表示链完整
 */
export function verifyAuditChain() {
    const rows = db.prepare(`SELECT id, action, agent_id, target, details, prev_hash, record_hash, created_at
     FROM audit_log ORDER BY created_at ASC, id ASC`).all();
    if (rows.length === 0) {
        return { valid: true, total: 0, checked: 0 };
    }
    let expectedPrev = "GENESIS";
    for (const row of rows) {
        // 旧数据（哈希链实现前写入的）prev_hash/record_hash 为 null，跳过验证
        if (row.prev_hash === null || row.record_hash === null) {
            if (row.record_hash)
                expectedPrev = row.record_hash;
            // 继续用上一条的 record_hash 作为 expectedPrev
            continue;
        }
        // 检查 prev_hash 连续性
        if (row.prev_hash !== expectedPrev) {
            return {
                valid: false,
                total: rows.length,
                checked: rows.indexOf(row),
                firstBreak: {
                    id: row.id,
                    action: row.action,
                    expected: expectedPrev,
                    actual: row.prev_hash,
                },
            };
        }
        // 重新计算 hash 验证
        const hashInput = `${row.prev_hash}|${row.action}|${row.agent_id ?? ""}|${row.target ?? ""}|${row.details ?? ""}|${row.created_at}`;
        const computedHash = createHash("sha256").update(hashInput).digest("hex");
        if (computedHash !== row.record_hash) {
            return {
                valid: false,
                total: rows.length,
                checked: rows.indexOf(row) + 1,
                firstBreak: {
                    id: row.id,
                    action: row.action,
                    expected: computedHash,
                    actual: row.record_hash,
                },
            };
        }
        expectedPrev = row.record_hash;
    }
    return { valid: true, total: rows.length, checked: rows.length };
}
// ─── 信任评分自动化（Phase 5a Day 2） ───────────────────
/**
 * 重新计算 Agent 信任评分
 *
 * 公式：
 *   base = 50
 *   + verified_capabilities × 3
 *   + auto_approved_strategies × 2
 *   + positive_feedback × 1
 *   - negative_feedback × 2
 *   - rejected_applications × 3
 *   - revoked_token_count × 10
 *   → clamp(0, 100)
 *
 * @returns 计算后的信任分数
 */
export function recalculateTrustScore(agentId) {
    const verifiedCaps = db.prepare(`SELECT COUNT(*) as cnt FROM agent_capabilities WHERE agent_id=? AND verified=1`).get(agentId)?.cnt ?? 0;
    const autoStrategies = db.prepare(`SELECT COUNT(*) as cnt FROM strategies WHERE proposer_id=? AND status='approved'`).get(agentId)?.cnt ?? 0;
    // 注意：strategy_applications 没有 status/rejected 列，无法直接统计拒绝数
    // 退而查 apply_strategy_fail 审计记录
    const rejectedApps = db.prepare(`SELECT COUNT(*) as cnt FROM audit_log WHERE action='apply_strategy' AND agent_id=? AND details LIKE '%fail%'`).get(agentId)?.cnt ?? 0;
    const revokedTokens = db.prepare(`SELECT COUNT(*) as cnt FROM audit_log WHERE action='revoke_token' AND agent_id=?`).get(agentId)?.cnt ?? 0;
    // 注意：strategy_feedback.agent_id 是反馈者，不是提案者
    // 要查"别人给该 agent 策略的反馈"需要 JOIN strategies.proposer_id
    const positiveFb = db.prepare(`SELECT COUNT(*) as cnt FROM strategy_feedback sf
     JOIN strategies s ON sf.strategy_id = s.id
     WHERE s.proposer_id = ? AND sf.feedback = 'positive' AND sf.agent_id != ?`).get(agentId, agentId)?.cnt ?? 0;
    const negativeFb = db.prepare(`SELECT COUNT(*) as cnt FROM strategy_feedback sf
     JOIN strategies s ON sf.strategy_id = s.id
     WHERE s.proposer_id = ? AND sf.feedback = 'negative' AND sf.agent_id != ?`).get(agentId, agentId)?.cnt ?? 0;
    let score = 50;
    score += verifiedCaps * 3;
    score += autoStrategies * 2;
    score += positiveFb * 1;
    score -= negativeFb * 2;
    score -= rejectedApps * 3;
    score -= revokedTokens * 10;
    // clamp(0, 100)
    score = Math.max(0, Math.min(100, score));
    // 写回 agents.trust_score
    db.prepare(`UPDATE agents SET trust_score=? WHERE agent_id=?`).run(score, agentId);
    return score;
}
/**
 * 重新计算所有 Agent 的信任评分
 * @returns { agent_id, score } 数组
 */
export function recalculateAllTrustScores() {
    const agents = db.prepare(`SELECT agent_id FROM agents`).all();
    const results = [];
    for (const agent of agents) {
        const score = recalculateTrustScore(agent.agent_id);
        results.push({ agent_id: agent.agent_id, score });
    }
    return results;
}
// ─── 路径安全 ────────────────────────────────────────────
/**
 * 检查路径是否安全（防止路径遍历）
 */
export function sanitizePath(inputPath) {
    const normalized = inputPath.replace(/\\/g, "/");
    return (!normalized.includes("..") &&
        !normalized.startsWith("/") &&
        !normalized.includes("\0"));
}
//# sourceMappingURL=security.js.map