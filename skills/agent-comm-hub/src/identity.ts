/**
 * identity.ts — Identity Service
 * Agent 注册（邀请码）、心跳检测、在线状态查询
 *
 * Day 3 核心：心跳超时检测定时器
 *   - 90s 无心跳 → 自动标记 offline
 *   - 5min 无心跳 → 通知其他在线 Agent
 *
 * 踩坑经验：
 *   - better-sqlite3 boolean 绑定必须用 1/0
 *   - better-sqlite3 undefined 必须用 null
 */
import { randomUUID, randomBytes } from "crypto";
import { db } from "./db.js";
import {
  generateToken,
  sha256,
  createInviteCode,
  verifyInviteCode,
  markInviteCodeUsed,
  auditLog,
  type AuthContext,
} from "./security.js";
import { pushToAgent, onlineAgents } from "./sse.js";
import { logger } from "./logger.js";
import type { AgentRow, AgentCapabilityRow } from "./types.js";
import { getErrorMessage } from "./types.js";

// ─── 常量 ────────────────────────────────────────────────
const HEARTBEAT_ONLINE_THRESHOLD = parseInt(process.env.HEARTBEAT_ONLINE_THRESHOLD ?? "90000", 10);  // 90s → offline
const HEARTBEAT_NOTIFY_THRESHOLD = parseInt(process.env.HEARTBEAT_NOTIFY_THRESHOLD ?? "300000", 10); // 5min → 通知
const HEARTBEAT_CHECK_INTERVAL   = parseInt(process.env.HEARTBEAT_CHECK_INTERVAL ?? "30000", 10);  // 30s 检查一次

// Phase 1.2: 连续心跳信任分增长配置
export const HEARTBEAT_CONFIG = {
  TRUST_SCORE_INCREMENT_INTERVAL: 3,  // 每 3 次连续心跳 +1 分
  TRUST_SCORE_MAX: 100,               // trust_score 上限
};

// 连续心跳计数器：agentId → 连续在线心跳次数
const heartbeatCounters = new Map<string, number>();

// ─── 类型 ────────────────────────────────────────────────
export interface AgentInfo {
  agent_id: string;
  name: string;
  role: "admin" | "member" | "group_admin" | "superadmin";
  status: "online" | "offline";
  trust_score: number;
  last_heartbeat: number | null;
  created_at: number;
  capabilities?: string[];
}

// ─── Agent 注册 ──────────────────────────────────────────

/**
 * 注册新 Agent
 * @returns { agentId, apiToken } 或错误信息
 */
export function registerAgent(
  inviteCode: string,
  name: string,
  capabilities: string[] = []
): { success: boolean; agentId?: string; apiToken?: string; role?: string; error?: string } {
  // 1. 验证邀请码
  const role = verifyInviteCode(inviteCode);
  if (!role) {
    return { success: false, error: "Invalid or expired invite code" };
  }

  // 2. 标记邀请码已使用
  markInviteCodeUsed(inviteCode);

  // 3. 创建 Agent 记录
  const agentId = `agent_${randomBytes(4).toString("hex")}_${Date.now()}`;
  const now = Date.now();

  try {
    db.prepare(
      `INSERT INTO agents (agent_id, name, role, status, last_heartbeat, created_at)
       VALUES (?, ?, ?, 'offline', NULL, ?)`
    ).run(agentId, name, role, now);
  } catch (err: unknown) {
    // 可能 agent_id 冲突（极低概率），重试一次
    const retryId = `agent_${randomBytes(4).toString("hex")}_${Date.now()}`;
    db.prepare(
      `INSERT INTO agents (agent_id, name, role, status, last_heartbeat, created_at)
       VALUES (?, ?, ?, 'offline', NULL, ?)`
    ).run(retryId, name, role, now);
    return registerAgentWithId(retryId, name, role, capabilities, now);
  }

  return registerAgentWithId(agentId, name, role, capabilities, now);
}

function registerAgentWithId(
  agentId: string,
  name: string,
  role: "admin" | "member",
  capabilities: string[],
  now: number
): { success: boolean; agentId: string; apiToken: string; role: string } {
  // 4. 生成 API Token
  const plainToken = generateToken();
  const tokenHash = sha256(plainToken);
  const tokenId = `token_${agentId}_${randomBytes(4).toString("hex")}`;

  db.prepare(
    `INSERT INTO auth_tokens (token_id, token_type, token_value, agent_id, role, used, created_at)
     VALUES (?, 'api_token', ?, ?, ?, 1, ?)`
  ).run(tokenId, tokenHash, agentId, role, now);

  // 4.5 同步 token hash 到 agents 表
  db.prepare(`UPDATE agents SET api_token=? WHERE agent_id=?`).run(tokenHash, agentId);

  // 5. 存储能力（如果有）
  for (const cap of capabilities) {
    db.prepare(
      `INSERT INTO agent_capabilities (id, agent_id, capability, verified, created_at)
       VALUES (?, ?, ?, 0, ?)`
    ).run(randomUUID(), agentId, cap, now);
  }

  auditLog("agent_registered", agentId, name, `role=${role}, capabilities=${capabilities.length}`);

  return { success: true, agentId, apiToken: plainToken, role };
}

// ─── 心跳 ────────────────────────────────────────────────

/**
 * 处理 Agent 心跳
 * 连续在线心跳每 TRUST_SCORE_INCREMENT_INTERVAL 次自动增加 1 点 trust_score（上限 TRUST_SCORE_MAX）
 * @returns 更新后的状态
 */
export function heartbeat(agentId: string): {
  success: boolean;
  status: "online" | "offline";
  last_heartbeat: number;
  trust_score?: number;
  error?: string;
} {
  // 检查 Agent 是否存在
  const agent = db
    .prepare(`SELECT agent_id, trust_score FROM agents WHERE agent_id=?`)
    .get(agentId) as Pick<AgentRow, "agent_id" | "trust_score"> | undefined;

  if (!agent) {
    return { success: false, status: "offline", last_heartbeat: 0, error: "Agent not found" };
  }

  const now = Date.now();

  db.prepare(
    `UPDATE agents SET status='online', last_heartbeat=? WHERE agent_id=?`
  ).run(now, agentId);

  // Phase 1.2: 连续心跳信任分增长
  const counter = (heartbeatCounters.get(agentId) ?? 0) + 1;
  heartbeatCounters.set(agentId, counter);

  if (counter % HEARTBEAT_CONFIG.TRUST_SCORE_INCREMENT_INTERVAL === 0) {
    // 每 3 次连续心跳 +1 trust_score
    db.prepare(
      `UPDATE agents SET trust_score = MIN(trust_score + 1, ?) WHERE agent_id = ?`
    ).run(HEARTBEAT_CONFIG.TRUST_SCORE_MAX, agentId);
  }

  const newTrustScore = (db.prepare(`SELECT trust_score FROM agents WHERE agent_id=?`).get(agentId) as any)?.trust_score ?? 50;

  return { success: true, status: "online", last_heartbeat: now, trust_score: newTrustScore };
}

// ─── 查询 Agent ──────────────────────────────────────────

/**
 * 查询已注册的 Agent 列表
 */
export function queryAgents(filters?: {
  status?: "online" | "offline" | "all";
  role?: "admin" | "member" | "group_admin";
  capability?: string;
}): AgentInfo[] {
  let sql = `SELECT DISTINCT a.agent_id, a.name, a.role, a.status, a.trust_score, a.last_heartbeat, a.created_at
             FROM agents a`;
  const params: (string | number)[] = [];

  if (filters?.capability) {
    sql += ` LEFT JOIN agent_capabilities c ON a.agent_id = c.agent_id`;
  }

  const conditions: string[] = [];
  if (filters?.status && filters.status !== "all") {
    conditions.push("a.status = ?");
    params.push(filters.status);
  }
  if (filters?.role) {
    conditions.push("a.role = ?");
    params.push(filters.role);
  }
  if (filters?.capability) {
    conditions.push("c.capability = ?");
    params.push(filters.capability);
  }

  if (conditions.length > 0) {
    sql += " WHERE " + conditions.join(" AND ");
  }

  sql += " ORDER BY a.created_at ASC";

  const rows = db.prepare(sql).all(...params) as AgentRow[];

  return rows.map(row => ({
    agent_id:      row.agent_id,
    name:          row.name,
    role:          row.role,
    status:        row.status,
    trust_score:   row.trust_score ?? 50,
    last_heartbeat: row.last_heartbeat ?? null,
    created_at:    row.created_at,
  }));
}

/**
 * 查询单个 Agent 信息
 */
export function getAgent(agentId: string): AgentInfo | null {
  const row = db
    .prepare(`SELECT * FROM agents WHERE agent_id=?`)
    .get(agentId) as AgentRow | undefined;

  if (!row) return null;

  // 获取能力列表
  const caps = db
    .prepare(`SELECT capability FROM agent_capabilities WHERE agent_id=?`)
    .all(agentId) as AgentCapabilityRow[];

  return {
    agent_id:      row.agent_id,
    name:          row.name,
    role:          row.role,
    status:        row.status,
    trust_score:   row.trust_score ?? 50,
    last_heartbeat: row.last_heartbeat ?? null,
    created_at:    row.created_at,
    capabilities:  caps.map((c) => c.capability),
  };
}

// ─── 心跳超时检测定时器（Day 3 核心） ────────────────────

let heartbeatTimer: ReturnType<typeof setInterval> | null = null;
let offlineNotifiedSet = new Set<string>(); // 已发送离线通知的 Agent

/**
 * 启动心跳超时检测定时器
 * - 90s 无心跳 → 标记 offline
 * - 5min 无心跳 → 通知其他在线 Agent
 */
export function startHeartbeatMonitor(onAgentOffline?: (agentId: string) => void): void {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
  }

  logger.info("HeartbeatMonitor started", { module: "heartbeat", interval_ms: HEARTBEAT_CHECK_INTERVAL });

  heartbeatTimer = setInterval(() => {
    const now = Date.now();

    // 查找所有 status='online' 但心跳超时的 Agent
    const staleAgents = db
      .prepare(
        `SELECT agent_id, name, last_heartbeat FROM agents
         WHERE status='online' AND last_heartbeat IS NOT NULL AND last_heartbeat < ?
         ORDER BY last_heartbeat ASC`
      )
      .all(now - HEARTBEAT_ONLINE_THRESHOLD) as any[];

    for (const agent of staleAgents) {
      const elapsed = now - agent.last_heartbeat;

      // 90s → 标记 offline
      if (elapsed >= HEARTBEAT_ONLINE_THRESHOLD) {
        db.prepare(
          `UPDATE agents SET status='offline' WHERE agent_id=?`
        ).run(agent.agent_id);

        // Phase 1.2: 重置连续心跳计数器
        heartbeatCounters.delete(agent.agent_id);

        logger.info("agent_offline_marked", {
          module: "heartbeat",
          agent_id: agent.agent_id,
          name: agent.name,
          elapsed_s: Math.round(elapsed / 1000),
        });

        auditLog("agent_offline", agent.agent_id, agent.name,
          `heartbeat_timeout: ${Math.round(elapsed / 1000)}s`);

        // 回调
        if (onAgentOffline) {
          onAgentOffline(agent.agent_id);
        }
      }

      // 5min → 通知其他在线 Agent
      if (elapsed >= HEARTBEAT_NOTIFY_THRESHOLD && !offlineNotifiedSet.has(agent.agent_id)) {
        offlineNotifiedSet.add(agent.agent_id);

        const onlineList = onlineAgents().filter(id => id !== agent.agent_id);
        for (const onlineId of onlineList) {
          pushToAgent(onlineId, {
            event: "agent_offline",
            agent_id: agent.agent_id,
            name: agent.name,
            last_heartbeat: agent.last_heartbeat,
            offline_duration: Math.round(elapsed / 1000),
            message: `${agent.name} (${agent.agent_id}) 已离线超过 5 分钟`,
          });
        }

        logger.info("agent_offline_notified", {
          module: "heartbeat",
          agent_id: agent.agent_id,
          notified_count: onlineList.length,
        });
      }
    }
  }, HEARTBEAT_CHECK_INTERVAL);
}

/**
 * 停止心跳超时检测
 */
export function stopHeartbeatMonitor(): void {
  if (heartbeatTimer) {
    clearInterval(heartbeatTimer);
    heartbeatTimer = null;
    offlineNotifiedSet.clear();
    logger.info("HeartbeatMonitor stopped", { module: "heartbeat" });
  }
}

/**
 * 清除离线通知标记（Agent 重新上线时调用）
 */
export function clearOfflineNotification(agentId: string): void {
  offlineNotifiedSet.delete(agentId);
}

// ─── Trust Score 管理（Phase 2 Day 4） ───────────────────

const TRUST_SCORE_MIN = 0;
const TRUST_SCORE_MAX = 100;
const TRUST_SCORE_DEFAULT = 50;

/**
 * 获取 Agent 信任分
 */
export function getAgentTrustScore(agentId: string): number {
  const row = db
    .prepare(`SELECT trust_score FROM agents WHERE agent_id=?`)
    .get(agentId) as any;
  return row ? row.trust_score : TRUST_SCORE_DEFAULT;
}

/**
 * 更新 Agent 信任分（admin only）
 * @returns 更新后的信任分，或 null（Agent 不存在）
 */
export function updateAgentTrustScore(
  agentId: string,
  delta: number,
  operatorId?: string
): { ok: true; new_score: number } | { ok: false; error: string } {
  const row = db
    .prepare(`SELECT trust_score FROM agents WHERE agent_id=?`)
    .get(agentId) as any;

  if (!row) {
    return { ok: false, error: `Agent ${agentId} not found` };
  }

  const current = row.trust_score;
  const newScore = Math.max(TRUST_SCORE_MIN, Math.min(TRUST_SCORE_MAX, current + delta));

  db.prepare(`UPDATE agents SET trust_score=? WHERE agent_id=?`).run(newScore, agentId);

  auditLog("trust_score_updated", operatorId ?? null, agentId,
    `${current} → ${newScore} (delta=${delta})`);

  return { ok: true, new_score: newScore };
}

// ─── Phase 5a: 角色管理 ──────────────────────────────────

/**
 * 设置 Agent 角色（admin only）
 * 支持 admin / member / group_admin 三种角色
 * group_admin 需要同时设置 managed_group_id
 */
export function setAgentRole(
  agentId: string,
  newRole: "admin" | "member" | "group_admin",
  operatorId: string,
  managedGroupId?: string
): { ok: true; old_role: string; new_role: string; managed_group_id: string | null } | { ok: false; error: string } {
  // 验证目标 Agent 存在
  const agent = db
    .prepare(`SELECT role, managed_group_id FROM agents WHERE agent_id=?`)
    .get(agentId) as any;

  if (!agent) {
    return { ok: false, error: `Agent ${agentId} not found` };
  }

  const oldRole = agent.role;

  // 不能修改自己
  if (agentId === operatorId) {
    return { ok: false, error: "Cannot modify own role" };
  }

  // 非 admin 不能被设为 admin（防止 member 提权）
  if (newRole === "admin" && oldRole !== "admin") {
    return { ok: false, error: "Only existing admin can be promoted to admin" };
  }

  // group_admin 必须有 managed_group_id
  const groupId = newRole === "group_admin" ? (managedGroupId ?? null) : null;

  // 更新 agents 表
  db.prepare(`UPDATE agents SET role=?, managed_group_id=? WHERE agent_id=?`)
    .run(newRole, groupId, agentId);

  // 同步更新 auth_tokens 表中的 role（保持一致性）
  db.prepare(`UPDATE auth_tokens SET role=? WHERE agent_id=? AND token_type='api_token' AND revoked_at IS NULL`)
    .run(newRole, agentId);

  auditLog("role_changed", operatorId, agentId,
    `${oldRole} → ${newRole}${groupId ? `, group=${groupId}` : ""}`);

  return { ok: true, old_role: oldRole, new_role: newRole, managed_group_id: groupId };
}

/**
 * 获取 Agent 角色
 */
export function getAgentRole(agentId: string): string | null {
  const row = db
    .prepare(`SELECT role FROM agents WHERE agent_id=?`)
    .get(agentId) as any;
  return row?.role ?? null;
}

/**
 * 获取 Agent 的 managed_group_id
 */
export function getAgentManagedGroup(agentId: string): string | null {
  const row = db
    .prepare(`SELECT managed_group_id FROM agents WHERE agent_id=?`)
    .get(agentId) as any;
  return row?.managed_group_id ?? null;
}

/**
 * 获取心跳超时配置（用于测试）
 */
export function getHeartbeatConfig() {
  return {
    onlineThreshold: HEARTBEAT_ONLINE_THRESHOLD,
    notifyThreshold: HEARTBEAT_NOTIFY_THRESHOLD,
    checkInterval:   HEARTBEAT_CHECK_INTERVAL,
  };
}

// ─────────────────────────────────────────────────────────
// from_agent 格式规范化（Phase 2.1）
// ─────────────────────────────────────────────────────────

/**
 * 已知的 Agent 别名映射（兼容历史消息格式）
 * 规范化后不再需要，但用于迁移阶段
 */
const AGENT_ALIAS_MAP: Record<string, string> = {
  'workbuddy': 'agent_workbuddy_a3f7c2e1_1777300825754',
  'hermes':    'agent_hermes_54cfe58b_1777132066111',
  'qclaw':     'agent_1c11a7bd_1777129814251',
};

/**
 * 解析 Agent 标识符为完整 agent_id。
 * 支持：
 *   1. 完整 agent_id（已注册则返回）
 *   2. 已知别名（workbuddy / hermes / qclaw，大小写不敏感）
 *   3. agent_id 子串匹配（大小写不敏感）
 * 返回完整 agent_id 或 null（未找到）
 */
export function resolveAgentId(input: string): string | null {
  const trimmed = input.trim();
  if (!trimmed) return null;

  // 1. 直接以 agent_ 开头 → 验证是否存在于数据库
  if (trimmed.startsWith('agent_')) {
    return getAgent(trimmed) ? trimmed : null;
  }

  // 2. 已知别名映射
  const aliasKey = trimmed.toLowerCase();
  if (AGENT_ALIAS_MAP[aliasKey]) {
    return getAgent(AGENT_ALIAS_MAP[aliasKey]) ? AGENT_ALIAS_MAP[aliasKey] : null;
  }

  // 3. 子串匹配（agent_id 包含输入，大小写不敏感）
  const agents = queryAgents({});
  const lower = trimmed.toLowerCase();
  for (const agent of agents) {
    if (agent.agent_id.toLowerCase().includes(lower)) {
      return agent.agent_id;
    }
  }

  return null;
}
