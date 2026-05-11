/**
 * repo/sqlite-impl.ts — IMessageRepo / ITaskRepo / IConsumedLogRepo 的 SQLite 实现
 * Phase 2 Day 2 基础 + Phase 4b 依赖链 + 质量门扩展
 */
import {
  db,
  msgStmt,
  taskStmt,
  consumedStmt,
  type Message,
  type Task,
  type ConsumedEntry,
} from "../db.js";
import type { IMessageRepo, ITaskRepo, IConsumedLogRepo } from "./interfaces.js";
import type { TaskDependency, QualityGate, DepType, DepStatus, GateStatus } from "./types.js";

// ─── MessageRepo ──────────────────────────────────────────────

class SqliteMessageRepo implements IMessageRepo {
  insert(msg: Message): void {
    msgStmt.insert.run(msg);
  }

  markDelivered(id: string): void {
    msgStmt.markDelivered.run(id);
  }

  markRead(id: string): void {
    msgStmt.markRead.run(id);
  }

  markAcknowledged(id: string): void {
    msgStmt.markAcknowledged.run(id);
  }

  markAllDelivered(toAgent: string): void {
    msgStmt.markAllDelivered.run(toAgent);
  }

  pendingFor(toAgent: string): Message[] {
    return msgStmt.pendingFor.all(toAgent) as Message[];
  }

  getById(id: string): Message | undefined {
    return msgStmt.getById.get(id) as Message | undefined;
  }

  listByStatus(toAgent: string, status: string): Message[] {
    const stmt = db.prepare(
      `SELECT * FROM messages WHERE to_agent=? AND status=? ORDER BY created_at ASC`
    );
    return stmt.all(toAgent, status) as Message[];
  }

  updateStatus(id: string, status: string): void {
    const stmt = db.prepare(`UPDATE messages SET status=? WHERE id=?`);
    stmt.run(status, id);
  }

  listSince(toAgent: string, since: number): Message[] {
    const stmt = db.prepare(
      `SELECT * FROM messages WHERE to_agent=? AND created_at > ? ORDER BY created_at ASC`
    );
    return stmt.all(toAgent, since) as Message[];
  }
}

// ─── TaskRepo ─────────────────────────────────────────────────

class SqliteTaskRepo implements ITaskRepo {
  insert(task: Task): void {
    taskStmt.insert.run(task);
  }

  getById(id: string): Task | undefined {
    return taskStmt.getById.get(id) as Task | undefined;
  }

  update(id: string, status: string, result: string | null, progress: number): void {
    taskStmt.update.run(status, result, progress, Date.now(), id);
  }

  assignTo(id: string, assignedTo: string): void {
    taskStmt.updateAssignee.run(assignedTo, Date.now(), Date.now(), id);
  }

  listFor(assignedTo: string, status: string): Task[] {
    return taskStmt.listFor.all(assignedTo, status) as Task[];
  }

  listByPipeline(pipelineId: string): Task[] {
    return taskStmt.listByPipeline.all(pipelineId) as Task[];
  }

  // ─── Phase 4b: 依赖链实现 ────────────────────────────────

  addDependency(upstreamId: string, downstreamId: string, depType: DepType = "finish_to_start"): TaskDependency {
    if (upstreamId === downstreamId) {
      throw new Error("Cannot create self-dependency");
    }

    // 检查是否已存在
    const existing = db.prepare(
      `SELECT * FROM task_dependencies WHERE upstream_id=? AND downstream_id=?`
    ).get(upstreamId, downstreamId);
    if (existing) {
      throw new Error(`Dependency already exists: ${upstreamId} → ${downstreamId}`);
    }

    const id = `dep_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const now = Date.now();

    const dep: TaskDependency = {
      id, upstream_id: upstreamId, downstream_id: downstreamId,
      dep_type: depType, status: "pending", created_at: now,
    };

    db.prepare(
      `INSERT INTO task_dependencies (id, upstream_id, downstream_id, dep_type, status, created_at)
       VALUES (@id, @upstream_id, @downstream_id, @dep_type, @status, @created_at)`
    ).run(dep);

    return dep;
  }

  removeDependency(upstreamId: string, downstreamId: string): void {
    const result = db.prepare(
      `DELETE FROM task_dependencies WHERE upstream_id=? AND downstream_id=?`
    ).run(upstreamId, downstreamId);
    if (result.changes === 0) {
      throw new Error(`Dependency not found: ${upstreamId} → ${downstreamId}`);
    }
  }

  getDependencies(taskId: string): { upstreams: TaskDependency[]; downstreams: TaskDependency[] } {
    const upstreams = db.prepare(
      `SELECT * FROM task_dependencies WHERE downstream_id=? ORDER BY created_at ASC`
    ).all(taskId) as TaskDependency[];

    const downstreams = db.prepare(
      `SELECT * FROM task_dependencies WHERE upstream_id=? ORDER BY created_at ASC`
    ).all(taskId) as TaskDependency[];

    return { upstreams, downstreams };
  }

  checkDependenciesSatisfied(taskId: string): boolean {
    // 查找所有 pending 状态的上游依赖
    const pending = db.prepare(
      `SELECT COUNT(*) as cnt FROM task_dependencies
       WHERE downstream_id=? AND status='pending'`
    ).get(taskId) as { cnt: number };
    return pending.cnt === 0;
  }

  setTaskWaiting(taskId: string): void {
    db.prepare(
      `UPDATE tasks SET status='waiting', updated_at=? WHERE id=?`
    ).run(Date.now(), taskId);
  }

  setTaskReady(taskId: string): void {
    const task = db.prepare(`SELECT * FROM tasks WHERE id=?`).get(taskId) as Task | undefined;
    if (!task) throw new Error(`Task not found: ${taskId}`);
    if (task.status !== "waiting") {
      throw new Error(`Task is not in waiting state: ${task.status}`);
    }
    db.prepare(
      `UPDATE tasks SET status='assigned', updated_at=? WHERE id=?`
    ).run(Date.now(), taskId);
  }

  wouldCreateCycle(upstreamId: string, downstreamId: string): boolean {
    // DFS: 从 downstreamId 出发，沿现有依赖的 downstream 方向搜索，
    // 看是否能到达 upstreamId。
    // 如果能到达，说明添加 upstreamId→downstreamId 后会形成环。
    const visited = new Set<string>();
    const stack = [downstreamId];

    while (stack.length > 0) {
      const current = stack.pop()!;
      if (current === upstreamId) return true;
      if (visited.has(current)) continue;
      visited.add(current);

      const deps = db.prepare(
        `SELECT downstream_id FROM task_dependencies WHERE upstream_id=?`
      ).all(current) as Array<{ downstream_id: string }>;

      for (const d of deps) {
        stack.push(d.downstream_id);
      }
    }
    return false;
  }

  satisfyDownstream(upstreamId: string): number {
    const result = db.prepare(
      `UPDATE task_dependencies SET status='satisfied'
       WHERE upstream_id=? AND status='pending' AND dep_type='finish_to_start'`
    ).run(upstreamId);
    return result.changes;
  }

  // ─── Phase 4b: 质量门实现 ────────────────────────────────

  addQualityGate(gate: Omit<QualityGate, "id"> & { id?: string }): QualityGate {
    const id = gate.id ?? `qg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
    const fullGate: QualityGate = { ...gate, id };

    db.prepare(
      `INSERT INTO quality_gates (id, pipeline_id, gate_name, criteria, after_order, status, evaluator_id, result, evaluated_at, created_at)
       VALUES (@id, @pipeline_id, @gate_name, @criteria, @after_order, @status, @evaluator_id, @result, @evaluated_at, @created_at)`
    ).run(fullGate);

    return fullGate;
  }

  updateQualityGateStatus(gateId: string, status: GateStatus, evaluatorId: string, result?: string): void {
    const now = Date.now();
    db.prepare(
      `UPDATE quality_gates SET status=?, evaluator_id=?, result=?, evaluated_at=? WHERE id=?`
    ).run(status, evaluatorId, result ?? null, now, gateId);
  }

  listGatesByPipeline(pipelineId: string): QualityGate[] {
    return db.prepare(
      `SELECT * FROM quality_gates WHERE pipeline_id=? ORDER BY after_order ASC`
    ).all(pipelineId) as QualityGate[];
  }
}

// ─── ConsumedLogRepo ──────────────────────────────────────────

class SqliteConsumedLogRepo implements IConsumedLogRepo {
  insert(entry: ConsumedEntry): void {
    consumedStmt.insert.run(entry);
  }

  check(agentId: string, resource: string): ConsumedEntry | undefined {
    return consumedStmt.check.get(agentId, resource) as ConsumedEntry | undefined;
  }

  listByAgent(agentId: string, limit = 50): ConsumedEntry[] {
    return consumedStmt.listByAgent.all(agentId, limit) as ConsumedEntry[];
  }
}

// ─── 单例导出 ──────────────────────────────────────────────────

export const messageRepo: IMessageRepo     = new SqliteMessageRepo();
export const taskRepo:    ITaskRepo        = new SqliteTaskRepo();
export const consumedRepo: IConsumedLogRepo = new SqliteConsumedLogRepo();
