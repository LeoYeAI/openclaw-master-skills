/**
 * repo/sqlite-impl.ts — IMessageRepo / ITaskRepo / IConsumedLogRepo 的 SQLite 实现
 * Phase 2 Day 2 基础 + Phase 4b 依赖链 + 质量门扩展
 */
import { db, msgStmt, taskStmt, consumedStmt, } from "../db.js";
// ─── MessageRepo ──────────────────────────────────────────────
class SqliteMessageRepo {
    insert(msg) {
        msgStmt.insert.run(msg);
    }
    markDelivered(id) {
        msgStmt.markDelivered.run(id);
    }
    markRead(id) {
        msgStmt.markRead.run(id);
    }
    markAcknowledged(id) {
        msgStmt.markAcknowledged.run(id);
    }
    markAllDelivered(toAgent) {
        msgStmt.markAllDelivered.run(toAgent);
    }
    pendingFor(toAgent) {
        return msgStmt.pendingFor.all(toAgent);
    }
    getById(id) {
        return msgStmt.getById.get(id);
    }
    listByStatus(toAgent, status) {
        const stmt = db.prepare(`SELECT * FROM messages WHERE to_agent=? AND status=? ORDER BY created_at ASC`);
        return stmt.all(toAgent, status);
    }
    updateStatus(id, status) {
        const stmt = db.prepare(`UPDATE messages SET status=? WHERE id=?`);
        stmt.run(status, id);
    }
    listSince(toAgent, since) {
        const stmt = db.prepare(`SELECT * FROM messages WHERE to_agent=? AND created_at > ? ORDER BY created_at ASC`);
        return stmt.all(toAgent, since);
    }
}
// ─── TaskRepo ─────────────────────────────────────────────────
class SqliteTaskRepo {
    insert(task) {
        taskStmt.insert.run(task);
    }
    getById(id) {
        return taskStmt.getById.get(id);
    }
    update(id, status, result, progress) {
        taskStmt.update.run(status, result, progress, Date.now(), id);
    }
    assignTo(id, assignedTo) {
        taskStmt.updateAssignee.run(assignedTo, Date.now(), Date.now(), id);
    }
    listFor(assignedTo, status) {
        return taskStmt.listFor.all(assignedTo, status);
    }
    listByPipeline(pipelineId) {
        return taskStmt.listByPipeline.all(pipelineId);
    }
    // ─── Phase 4b: 依赖链实现 ────────────────────────────────
    addDependency(upstreamId, downstreamId, depType = "finish_to_start") {
        if (upstreamId === downstreamId) {
            throw new Error("Cannot create self-dependency");
        }
        // 检查是否已存在
        const existing = db.prepare(`SELECT * FROM task_dependencies WHERE upstream_id=? AND downstream_id=?`).get(upstreamId, downstreamId);
        if (existing) {
            throw new Error(`Dependency already exists: ${upstreamId} → ${downstreamId}`);
        }
        const id = `dep_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
        const now = Date.now();
        const dep = {
            id, upstream_id: upstreamId, downstream_id: downstreamId,
            dep_type: depType, status: "pending", created_at: now,
        };
        db.prepare(`INSERT INTO task_dependencies (id, upstream_id, downstream_id, dep_type, status, created_at)
       VALUES (@id, @upstream_id, @downstream_id, @dep_type, @status, @created_at)`).run(dep);
        return dep;
    }
    removeDependency(upstreamId, downstreamId) {
        const result = db.prepare(`DELETE FROM task_dependencies WHERE upstream_id=? AND downstream_id=?`).run(upstreamId, downstreamId);
        if (result.changes === 0) {
            throw new Error(`Dependency not found: ${upstreamId} → ${downstreamId}`);
        }
    }
    getDependencies(taskId) {
        const upstreams = db.prepare(`SELECT * FROM task_dependencies WHERE downstream_id=? ORDER BY created_at ASC`).all(taskId);
        const downstreams = db.prepare(`SELECT * FROM task_dependencies WHERE upstream_id=? ORDER BY created_at ASC`).all(taskId);
        return { upstreams, downstreams };
    }
    checkDependenciesSatisfied(taskId) {
        // 查找所有 pending 状态的上游依赖
        const pending = db.prepare(`SELECT COUNT(*) as cnt FROM task_dependencies
       WHERE downstream_id=? AND status='pending'`).get(taskId);
        return pending.cnt === 0;
    }
    setTaskWaiting(taskId) {
        db.prepare(`UPDATE tasks SET status='waiting', updated_at=? WHERE id=?`).run(Date.now(), taskId);
    }
    setTaskReady(taskId) {
        const task = db.prepare(`SELECT * FROM tasks WHERE id=?`).get(taskId);
        if (!task)
            throw new Error(`Task not found: ${taskId}`);
        if (task.status !== "waiting") {
            throw new Error(`Task is not in waiting state: ${task.status}`);
        }
        db.prepare(`UPDATE tasks SET status='assigned', updated_at=? WHERE id=?`).run(Date.now(), taskId);
    }
    wouldCreateCycle(upstreamId, downstreamId) {
        // DFS: 从 downstreamId 出发，沿现有依赖的 downstream 方向搜索，
        // 看是否能到达 upstreamId。
        // 如果能到达，说明添加 upstreamId→downstreamId 后会形成环。
        const visited = new Set();
        const stack = [downstreamId];
        while (stack.length > 0) {
            const current = stack.pop();
            if (current === upstreamId)
                return true;
            if (visited.has(current))
                continue;
            visited.add(current);
            const deps = db.prepare(`SELECT downstream_id FROM task_dependencies WHERE upstream_id=?`).all(current);
            for (const d of deps) {
                stack.push(d.downstream_id);
            }
        }
        return false;
    }
    satisfyDownstream(upstreamId) {
        const result = db.prepare(`UPDATE task_dependencies SET status='satisfied'
       WHERE upstream_id=? AND status='pending' AND dep_type='finish_to_start'`).run(upstreamId);
        return result.changes;
    }
    // ─── Phase 4b: 质量门实现 ────────────────────────────────
    addQualityGate(gate) {
        const id = gate.id ?? `qg_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
        const fullGate = { ...gate, id };
        db.prepare(`INSERT INTO quality_gates (id, pipeline_id, gate_name, criteria, after_order, status, evaluator_id, result, evaluated_at, created_at)
       VALUES (@id, @pipeline_id, @gate_name, @criteria, @after_order, @status, @evaluator_id, @result, @evaluated_at, @created_at)`).run(fullGate);
        return fullGate;
    }
    updateQualityGateStatus(gateId, status, evaluatorId, result) {
        const now = Date.now();
        db.prepare(`UPDATE quality_gates SET status=?, evaluator_id=?, result=?, evaluated_at=? WHERE id=?`).run(status, evaluatorId, result ?? null, now, gateId);
    }
    listGatesByPipeline(pipelineId) {
        return db.prepare(`SELECT * FROM quality_gates WHERE pipeline_id=? ORDER BY after_order ASC`).all(pipelineId);
    }
}
// ─── ConsumedLogRepo ──────────────────────────────────────────
class SqliteConsumedLogRepo {
    insert(entry) {
        consumedStmt.insert.run(entry);
    }
    check(agentId, resource) {
        return consumedStmt.check.get(agentId, resource);
    }
    listByAgent(agentId, limit = 50) {
        return consumedStmt.listByAgent.all(agentId, limit);
    }
}
// ─── 单例导出 ──────────────────────────────────────────────────
export const messageRepo = new SqliteMessageRepo();
export const taskRepo = new SqliteTaskRepo();
export const consumedRepo = new SqliteConsumedLogRepo();
//# sourceMappingURL=sqlite-impl.js.map