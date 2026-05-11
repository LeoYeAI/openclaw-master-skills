/**
 * repo/types.ts — Phase 4b 依赖链 + 质量门类型定义
 */

// ─── 依赖类型 ──────────────────────────────────────────────

/** 依赖类型 */
export type DepType = "finish_to_start" | "start_to_start" | "finish_to_finish";

/** 依赖状态 */
export type DepStatus = "pending" | "satisfied" | "failed";

/** 任务依赖关系 */
export interface TaskDependency {
  id:            string;
  upstream_id:   string;
  downstream_id: string;
  dep_type:      DepType;
  status:        DepStatus;
  created_at:    number;
}

// ─── 质量门类型 ─────────────────────────────────────────────

/** 质量门状态 */
export type GateStatus = "pending" | "passed" | "failed";

/** 质量门 */
export interface QualityGate {
  id:            string;
  pipeline_id:   string;
  gate_name:     string;
  criteria:      string;   // JSON: { type, threshold?, check_expr? }
  after_order:   number;
  status:        GateStatus;
  evaluator_id?: string | null;
  result?:       string | null;
  evaluated_at?: number | null;
  created_at:    number;
}

// ─── 状态机扩展 ─────────────────────────────────────────────

/** Phase 4b: 完整任务状态（含 waiting） */
export type TaskStatusAll =
  | "inbox" | "assigned" | "waiting" | "pending" | "in_progress"
  | "completed" | "failed" | "cancelled";
