/**
 * types.ts — DB Row 类型定义 + 工具类型
 * Phase D: 消除 any，统一类型
 */

// ─── SQLite pragma 结果类型 ─────────────────────────────────

/** `PRAGMA table_info(...)` 返回的列信息 */
export interface PragmaColumnInfo {
  cid: number;
  name: string;
  type: string;
  notnull: number;
  dflt_value: number | string | null;
  pk: number;
}

/** 聚合查询 `COUNT(*) as cnt` 返回 */
export interface CountRow {
  cnt: number;
}

/** `MAX(col) as ts` 返回 */
export interface MaxTimestampRow {
  ts: number | null;
}

// ─── Agent 相关 ─────────────────────────────────────────────

export interface AgentRow {
  agent_id: string;
  name: string;
  role: "admin" | "member" | "superadmin";
  api_token?: string | null;
  status: "online" | "offline";
  trust_score: number;
  last_heartbeat?: number | null;
  managed_group_id?: string | null;
  created_at: number;
}

export interface AgentCapabilityRow {
  id: string;
  agent_id: string;
  capability: string;
  params?: string | null;
  verified: number;
  verified_at?: number | null;
  created_at: number;
}

export interface AuthTokenRow {
  token_id: string;
  token_type: string;
  token_value: string;
  agent_id?: string | null;
  role?: string | null;
  used: number;
  created_at: number;
  expires_at?: number | null;
  revoked_at?: number | null;
}

// ─── Dedup 相关 ─────────────────────────────────────────────

export interface DedupCacheRow {
  msg_hash: string;
  sender_id: string;
  nonce: number;
  created_at: number;
}

// ─── Memory 相关 ────────────────────────────────────────────

export interface MemoryRow {
  id: string;
  agent_id: string;
  title?: string | null;
  content: string;
  fts_tokens: string;
  scope: "private" | "group" | "collective";
  tags?: string | null;
  source_agent_id?: string | null;
  source_task_id?: string | null;
  created_at: number;
  updated_at?: number | null;
}

// ─── Evolution 相关 ─────────────────────────────────────────

export interface StrategyRow {
  id: number;
  title: string;
  content: string;
  category: string;
  sensitivity: string;
  proposer_id: string;
  status: string;
  approve_reason?: string | null;
  approved_by?: string | null;
  approved_at?: number | null;
  proposed_at: number;
  task_id?: string | null;
  source_trust: number;
  apply_count: number;
  feedback_count: number;
  positive_count: number;
  approval_tier?: string | null;
  observation_start?: number | null;
  veto_deadline?: number | null;
  source_trust_score?: number | null;
}

export interface StrategyFeedbackRow {
  id: number;
  strategy_id: number;
  agent_id: string;
  feedback: string;
  comment?: string | null;
  applied: number;
  created_at: number;
}

export interface StrategyApplicationRow {
  id: number;
  strategy_id: number;
  agent_id: string;
  context?: string | null;
  result?: string | null;
  created_at: number;
}

// ─── Audit 相关 ─────────────────────────────────────────────

export interface AuditLogRow {
  id: string;
  action: string;
  agent_id?: string | null;
  target?: string | null;
  details?: string | null;
  ip_address?: string | null;
  created_at: number;
  prev_hash?: string | null;
  record_hash?: string | null;
}

// ─── Pipeline 相关 ─────────────────────────────────────────

export interface PipelineRow {
  id: string;
  name: string;
  description?: string | null;
  status: string;
  creator: string;
  config?: string | null;
  created_at: number;
  updated_at: number;
}

export interface PipelineTaskRow {
  id: string;
  pipeline_id: string;
  task_id: string;
  order_index: number;
  created_at: number;
}

// ─── 质量门 ─────────────────────────────────────────────────

export interface QualityGateRow {
  id: string;
  pipeline_id: string;
  gate_name: string;
  criteria: string;
  after_order: number;
  status: string;
  evaluator_id?: string | null;
  result?: string | null;
  evaluated_at?: number | null;
  created_at: number;
}

// ─── 归档表 ─────────────────────────────────────────────────

export interface MessageArchiveRow {
  id: string;
  from_agent: string;
  to_agent: string;
  content: string;
  type: string;
  metadata?: string | null;
  status: string;
  created_at: number;
  archived_at: number;
}

export interface AuditLogArchiveRow {
  id: string;
  action: string;
  agent_id?: string | null;
  target?: string | null;
  details?: string | null;
  ip_address?: string | null;
  created_at: number;
  prev_hash?: string | null;
  record_hash?: string | null;
  archived_at: number;
}

// ─── Express 类型扩展 ──────────────────────────────────────

/** Hub Agent 认证上下文 */
export interface AgentContext {
  agentId: string;
  name: string;
  role: string;
  trustScore: number;
}

// ─── 错误类型 ───────────────────────────────────────────────

/** 从 unknown 提取错误消息 */
export function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  if (typeof err === "string") return err;
  return String(err);
}
