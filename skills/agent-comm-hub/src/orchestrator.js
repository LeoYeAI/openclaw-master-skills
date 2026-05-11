/**
 * orchestrator.ts — Task Orchestrator Service (Phase 4a + Phase 4b)
 *
 * 任务状态机 + Pipeline 管理 + Agent 能力匹配 + 依赖链 + 质量门
 */
import { randomUUID } from "crypto";
import { db } from "./db.js";
import { pushToAgent, onlineAgents } from "./sse.js";
import { auditLog, recalculateTrustScore } from "./security.js";
import { taskRepo } from "./repo/sqlite-impl.js";
function getOne(sql, ...params) {
    return db.prepare(sql).get(...params);
}
function getAll(sql, ...params) {
    return db.prepare(sql).all(...params);
}
// ─── 常量 ──────────────────────────────────────────────
/** 合法的状态转换映射 */
const VALID_TRANSITIONS = {
    inbox: ["assigned", "cancelled"],
    assigned: ["waiting", "in_progress", "cancelled"],
    waiting: ["in_progress", "cancelled"], // Phase 4b: 依赖满足后可开始
    pending: ["in_progress", "cancelled"], // 兼容旧数据
    in_progress: ["completed", "failed", "cancelled"],
    completed: [], // 终态
    failed: [], // 终态
    cancelled: [], // 终态
};
/** 终态集合 */
const TERMINAL_STATES = new Set(["completed", "failed", "cancelled"]);
// ─── 状态机校验 ──────────────────────────────────────────
function validateTransition(from, to) {
    const allowed = VALID_TRANSITIONS[from];
    if (!allowed) {
        throw new Error(`Unknown source status: ${from}`);
    }
    if (!allowed.includes(to)) {
        throw new Error(`Invalid transition: ${from} → ${to}. Allowed: [${allowed.join(", ")}]`);
    }
}
/**
 * 创建任务
 */
export function createTask(input) {
    const now = Date.now();
    const status = input.assigned_to ? "assigned" : "inbox";
    const task = {
        id: `task_${now}_${randomUUID().slice(0, 6)}`,
        assigned_by: input.assigned_by,
        assigned_to: input.assigned_to ?? "",
        description: input.description,
        context: input.context ?? null,
        priority: input.priority ?? "normal",
        status,
        result: null,
        progress: 0,
        pipeline_id: input.pipeline_id ?? null,
        order_index: 0,
        required_capability: input.required_capability ?? null,
        due_at: input.due_at ?? null,
        assigned_at: input.assigned_to ? now : null,
        completed_at: null,
        tags: input.tags ? JSON.stringify(input.tags) : "[]",
        created_at: now,
        updated_at: now,
    }; // Phase 4b: parallel_group/handoff_status 由 DB DEFAULT 填充
    db.prepare(`INSERT INTO tasks (id, assigned_by, assigned_to, description, context, priority, status, result, progress, pipeline_id, order_index, required_capability, due_at, assigned_at, completed_at, tags, created_at, updated_at)
     VALUES (@id, @assigned_by, @assigned_to, @description, @context, @priority, @status, @result, @progress, @pipeline_id, @order_index, @required_capability, @due_at, @assigned_at, @completed_at, @tags, @created_at, @updated_at)`).run(task);
    auditLog("create_task", input.assigned_by, task.id, `status=${status}`);
    return task;
}
/**
 * 分配任务（inbox → assigned 或重新分配）
 */
export function assignTask(taskId, toAgent, operatorId) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (TERMINAL_STATES.has(task.status))
        throw new Error(`Cannot assign task in terminal state: ${task.status}`);
    const now = Date.now();
    db.prepare(`UPDATE tasks SET assigned_to=?, assigned_at=?, status='assigned', updated_at=? WHERE id=?`).run(toAgent, now, now, taskId);
    auditLog("assign_task", operatorId, taskId, `to=${toAgent}`);
    pushToAgent(toAgent, {
        type: "task_assigned",
        content: JSON.stringify({
            task_id: taskId,
            description: task.description,
            priority: task.priority,
            context: task.context,
            from: operatorId,
            hint: "调用 update_task_status(in_progress) 开始执行，完成后调用 update_task_status(completed) 并携带结果。",
        }),
    });
    return getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
}
/**
 * 认领任务（inbox → assigned）
 */
export function claimTask(taskId, agentId) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (task.status !== "inbox")
        throw new Error(`Cannot claim task in status: ${task.status}. Only inbox tasks can be claimed.`);
    return assignTask(taskId, agentId, agentId);
}
/**
 * 取消任务
 */
export function cancelTask(taskId, operatorId, reason) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (TERMINAL_STATES.has(task.status))
        throw new Error(`Cannot cancel task in terminal state: ${task.status}`);
    const now = Date.now();
    db.prepare(`UPDATE tasks SET status='cancelled', result=?, updated_at=? WHERE id=?`).run(reason ?? "Cancelled by " + operatorId, now, taskId);
    auditLog("cancel_task", operatorId, taskId, reason ?? "cancelled");
    if (task.assigned_to) {
        pushToAgent(task.assigned_to, {
            type: "task_cancelled",
            content: JSON.stringify({ task_id: taskId, reason, cancelled_by: operatorId }),
        });
    }
    pushToAgent(task.assigned_by, {
        type: "task_cancelled",
        content: JSON.stringify({ task_id: taskId, reason, cancelled_by: operatorId }),
    });
    return getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
}
/**
 * 更新任务状态（带状态机校验）
 */
export function updateTaskStatus(taskId, status, operatorId, result, progress) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    validateTransition(task.status, status);
    const now = Date.now();
    const completedAt = (status === "completed" || status === "failed") ? now : null;
    db.prepare(`UPDATE tasks SET status=?, result=?, progress=?, completed_at=?, updated_at=? WHERE id=?`).run(status, result ?? task.result, progress ?? task.progress, completedAt ?? task.completed_at, now, taskId);
    auditLog("update_task_status", operatorId, taskId, `${task.status}→${status}`);
    pushToAgent(task.assigned_by, {
        type: "task_update",
        content: JSON.stringify({
            task_id: taskId,
            status,
            result: result ?? null,
            progress: progress ?? task.progress,
            from: operatorId,
        }),
    });
    // Phase 4b: 任务完成时级联满足下游依赖
    if (status === "completed") {
        cascadeDependencySatisfaction(taskId);
    }
    return getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
}
/**
 * 多维查询任务
 */
export function listTasks(filters) {
    const conditions = [];
    const params = [];
    if (filters.assigned_to) {
        conditions.push("assigned_to = ?");
        params.push(filters.assigned_to);
    }
    if (filters.assigned_by) {
        conditions.push("assigned_by = ?");
        params.push(filters.assigned_by);
    }
    if (filters.status && filters.status !== "all") {
        conditions.push("status = ?");
        params.push(filters.status);
    }
    if (filters.pipeline_id) {
        conditions.push("pipeline_id = ?");
        params.push(filters.pipeline_id);
    }
    if (filters.required_capability) {
        conditions.push("required_capability = ?");
        params.push(filters.required_capability);
    }
    const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
    const limit = filters.limit ?? 50;
    return getAll(`SELECT * FROM tasks ${where} ORDER BY created_at DESC LIMIT ?`, ...params, limit);
}
/**
 * 创建 Pipeline
 */
export function createPipeline(input) {
    const now = Date.now();
    const pipeline = {
        id: `pipe_${now}_${randomUUID().slice(0, 6)}`,
        name: input.name,
        description: input.description ?? null,
        status: "draft",
        creator: input.creator,
        config: input.config ? JSON.stringify(input.config) : null,
        created_at: now,
        updated_at: now,
    };
    db.prepare(`INSERT INTO pipelines VALUES (@id,@name,@description,@status,@creator,@config,@created_at,@updated_at)`).run(pipeline);
    auditLog("create_pipeline", input.creator, pipeline.id, `name=${input.name}`);
    return pipeline;
}
/**
 * 激活 Pipeline
 */
export function activatePipeline(pipelineId, operatorId) {
    return updatePipelineStatus(pipelineId, "active", operatorId);
}
/**
 * 完成 Pipeline
 */
export function completePipeline(pipelineId, operatorId) {
    return updatePipelineStatus(pipelineId, "completed", operatorId);
}
/**
 * 取消 Pipeline
 */
export function cancelPipeline(pipelineId, operatorId) {
    return updatePipelineStatus(pipelineId, "cancelled", operatorId);
}
function updatePipelineStatus(pipelineId, status, operatorId) {
    const pipeline = getOne(`SELECT * FROM pipelines WHERE id=?`, pipelineId);
    if (!pipeline)
        throw new Error(`Pipeline not found: ${pipelineId}`);
    const now = Date.now();
    db.prepare(`UPDATE pipelines SET status=?, updated_at=? WHERE id=?`).run(status, now, pipelineId);
    auditLog("update_pipeline_status", operatorId, pipelineId, `${pipeline.status}→${status}`);
    return getOne(`SELECT * FROM pipelines WHERE id=?`, pipelineId);
}
/**
 * 添加任务到 Pipeline
 */
export function addTaskToPipeline(pipelineId, taskId, orderIndex, operatorId) {
    const pipeline = getOne(`SELECT * FROM pipelines WHERE id=?`, pipelineId);
    if (!pipeline)
        throw new Error(`Pipeline not found: ${pipelineId}`);
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    let order = orderIndex ?? 0;
    if (orderIndex === undefined) {
        const maxRow = getOne(`SELECT MAX(order_index) as max_order FROM pipeline_tasks WHERE pipeline_id=?`, pipelineId);
        order = (maxRow?.max_order ?? -1) + 1;
    }
    const now = Date.now();
    const pt = {
        id: `pt_${now}_${randomUUID().slice(0, 6)}`,
        pipeline_id: pipelineId,
        task_id: taskId,
        order_index: order,
        created_at: now,
    };
    db.prepare(`INSERT OR REPLACE INTO pipeline_tasks VALUES (@id,@pipeline_id,@task_id,@order_index,@created_at)`).run(pt);
    db.prepare(`UPDATE tasks SET pipeline_id=?, updated_at=? WHERE id=?`).run(pipelineId, now, taskId);
    if (operatorId) {
        auditLog("add_task_to_pipeline", operatorId, pipelineId, `task=${taskId},order=${order}`);
    }
    return pt;
}
/**
 * 获取 Pipeline 进度
 */
export function getPipelineStatus(pipelineId) {
    const pipeline = getOne(`SELECT * FROM pipelines WHERE id=?`, pipelineId);
    if (!pipeline)
        throw new Error(`Pipeline not found: ${pipelineId}`);
    const tasks = getAll(`SELECT t.* FROM tasks t JOIN pipeline_tasks pt ON t.id=pt.task_id WHERE pt.pipeline_id=? ORDER BY pt.order_index ASC`, pipelineId);
    const stats = {
        total: tasks.length,
        inbox: 0, assigned: 0, in_progress: 0,
        completed: 0, failed: 0, cancelled: 0,
    };
    for (const t of tasks) {
        const s = t.status;
        if (s in stats)
            stats[s]++;
    }
    return { pipeline, tasks, stats };
}
/**
 * 注册 Agent 能力
 */
export function registerCapability(input) {
    const now = Date.now();
    const id = `cap_${now}_${randomUUID().slice(0, 6)}`;
    db.prepare(`INSERT INTO agent_capabilities VALUES (?,?,?,?,?,?)`).run(id, input.agent_id, input.capability, input.params ? JSON.stringify(input.params) : null, input.verified ? 1 : 0, input.verified ? now : null, now);
    auditLog("register_capability", input.agent_id, id, `capability=${input.capability}`);
    // Phase 5a Day 2: 验证的能力影响信任评分
    if (input.verified) {
        try {
            recalculateTrustScore(input.agent_id);
        }
        catch { }
    }
    return { id };
}
/**
 * 智能推荐任务执行方
 */
export function suggestAssignee(taskId) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    const agents = getAll(`SELECT agent_id, name, status FROM agents WHERE role != 'admin' OR role IS NULL`);
    const onlineSet = new Set(onlineAgents());
    const results = [];
    for (const agent of agents) {
        let capability_match = false;
        if (task.required_capability) {
            const cap = getOne(`SELECT COUNT(*) as count FROM agent_capabilities WHERE agent_id=? AND capability=?`, agent.agent_id, task.required_capability);
            capability_match = (cap?.count ?? 0) > 0;
        }
        else {
            capability_match = true;
        }
        const taskCount = getOne(`SELECT COUNT(*) as count FROM tasks WHERE assigned_to=? AND status IN ('assigned', 'in_progress')`, agent.agent_id);
        results.push({
            agent_id: agent.agent_id,
            name: agent.name,
            capability_match,
            online: onlineSet.has(agent.agent_id),
            current_tasks: taskCount?.count ?? 0,
        });
    }
    results.sort((a, b) => {
        if (a.capability_match !== b.capability_match)
            return b.capability_match ? 1 : -1;
        if (a.online !== b.online)
            return b.online ? 1 : -1;
        return a.current_tasks - b.current_tasks;
    });
    return results;
}
// ═══════════════════════════════════════════════════════════════
// Phase 4b — 依赖链核心
// ═══════════════════════════════════════════════════════════════
/**
 * 级联满足下游依赖
 * 当上游任务完成时，将所有 finish_to_start 类型的下游依赖标记为 satisfied，
 * 并检查下游任务是否所有依赖都满足——如果满足则从 waiting 变为 assigned。
 */
function cascadeDependencySatisfaction(completedTaskId) {
    // 标记依赖为 satisfied
    const satisfiedCount = taskRepo.satisfyDownstream(completedTaskId);
    if (satisfiedCount === 0)
        return;
    // 找到所有被影响的下游任务（这些任务有 upstream = completedTaskId）
    const downstreams = getAll(`SELECT DISTINCT downstream_id FROM task_dependencies WHERE upstream_id=? AND status='satisfied'`, completedTaskId);
    for (const d of downstreams) {
        const task = getOne(`SELECT * FROM tasks WHERE id=?`, d.downstream_id);
        if (!task || task.status !== "waiting")
            continue;
        // 检查该任务是否所有上游依赖都满足
        if (taskRepo.checkDependenciesSatisfied(d.downstream_id)) {
            taskRepo.setTaskReady(d.downstream_id);
            auditLog("cascade_ready", "system", d.downstream_id, `upstream=${completedTaskId}`);
            // 通知下游任务负责人
            if (task.assigned_to) {
                pushToAgent(task.assigned_to, {
                    type: "dependency_satisfied",
                    content: JSON.stringify({
                        task_id: d.downstream_id,
                        satisfied_by: completedTaskId,
                        hint: "所有上游依赖已满足，任务可以开始执行。调用 update_task_status(in_progress) 开始。",
                    }),
                });
            }
        }
    }
}
/**
 * 添加任务依赖关系（含环检测）
 */
export function addDependency(upstreamId, downstreamId, depType = "finish_to_start", operatorId) {
    // 验证任务存在
    const upstream = getOne(`SELECT * FROM tasks WHERE id=?`, upstreamId);
    if (!upstream)
        throw new Error(`Upstream task not found: ${upstreamId}`);
    const downstream = getOne(`SELECT * FROM tasks WHERE id=?`, downstreamId);
    if (!downstream)
        throw new Error(`Downstream task not found: ${downstreamId}`);
    // 环检测
    if (taskRepo.wouldCreateCycle(upstreamId, downstreamId)) {
        throw new Error(`Adding dependency ${upstreamId} → ${downstreamId} would create a cycle`);
    }
    const dependency = taskRepo.addDependency(upstreamId, downstreamId, depType);
    // 如果上游已完成，立即标记为 satisfied
    let downstream_updated = false;
    if (upstream.status === "completed" && depType === "finish_to_start") {
        taskRepo.satisfyDownstream(upstreamId);
        // 检查下游是否所有依赖都满足
        if (downstream.status === "waiting" && taskRepo.checkDependenciesSatisfied(downstreamId)) {
            taskRepo.setTaskReady(downstreamId);
            downstream_updated = true;
        }
    }
    else if (downstream.status === "assigned" || downstream.status === "inbox") {
        // 下游任务有未满足依赖，设为 waiting
        taskRepo.setTaskWaiting(downstreamId);
        downstream_updated = true;
    }
    if (operatorId) {
        auditLog("add_dependency", operatorId, upstreamId, `→${downstreamId}(${depType})`);
    }
    return { dependency, downstream_updated };
}
/**
 * 删除依赖关系
 */
export function removeDependency(upstreamId, downstreamId, operatorId) {
    taskRepo.removeDependency(upstreamId, downstreamId);
    // 检查下游任务是否因依赖减少而可以执行
    let downstream_ready = false;
    const downstream = getOne(`SELECT * FROM tasks WHERE id=?`, downstreamId);
    if (downstream && downstream.status === "waiting") {
        if (taskRepo.checkDependenciesSatisfied(downstreamId)) {
            taskRepo.setTaskReady(downstreamId);
            downstream_ready = true;
        }
    }
    if (operatorId) {
        auditLog("remove_dependency", operatorId, upstreamId, `→${downstreamId}`);
    }
    return { removed: true, downstream_ready };
}
/**
 * 获取任务的上下游依赖
 */
export function getDependencies(taskId) {
    const { upstreams, downstreams } = taskRepo.getDependencies(taskId);
    const mapDep = (dep) => {
        const task = getOne(`SELECT id, status FROM tasks WHERE id=?`, dep.downstream_id);
        return {
            task_id: dep.downstream_id,
            status: task?.status ?? "unknown",
            dep_type: dep.dep_type,
            dep_status: dep.status,
        };
    };
    const mapUp = (dep) => {
        const task = getOne(`SELECT id, status FROM tasks WHERE id=?`, dep.upstream_id);
        return {
            task_id: dep.upstream_id,
            status: task?.status ?? "unknown",
            dep_type: dep.dep_type,
            dep_status: dep.status,
        };
    };
    return {
        upstreams: upstreams.map(mapUp),
        downstreams: downstreams.map(mapDep),
    };
}
/**
 * 检查任务依赖是否满足
 */
export function checkDependenciesSatisfied(taskId) {
    const { upstreams } = taskRepo.getDependencies(taskId);
    const pendingDeps = upstreams
        .filter(d => d.status === "pending")
        .map(d => ({ task_id: d.upstream_id, dep_type: d.dep_type }));
    return {
        satisfied: pendingDeps.length === 0,
        pending_deps: pendingDeps,
    };
}
// ═══════════════════════════════════════════════════════════════
// Phase 4b Day 2 — 并行组
// ═══════════════════════════════════════════════════════════════
/**
 * 创建并行组
 * 将多个任务标记为同一 parallel_group，表示它们可以并行执行。
 * 同一 parallel_group 内的任务在 Pipeline 中逻辑上是并行的。
 */
export function createParallelGroup(taskIds, operatorId) {
    if (taskIds.length < 2) {
        throw new Error("Parallel group requires at least 2 tasks");
    }
    if (taskIds.length > 10) {
        throw new Error("Parallel group cannot exceed 10 tasks");
    }
    const now = Date.now();
    const groupId = `pg_${now}_${randomUUID().slice(0, 6)}`;
    // 验证所有任务存在
    const tasks = [];
    for (const taskId of taskIds) {
        const task = getOne(`SELECT id FROM tasks WHERE id=?`, taskId);
        if (!task)
            throw new Error(`Task not found: ${taskId}`);
        tasks.push({ id: taskId, parallel_group: groupId });
    }
    // 批量更新 parallel_group
    const updateStmt = db.prepare(`UPDATE tasks SET parallel_group=?, updated_at=? WHERE id=?`);
    const updateMany = db.transaction((ids, group, ts) => {
        for (const id of ids) {
            updateStmt.run(group, ts, id);
        }
    });
    updateMany(taskIds, groupId, now);
    if (operatorId) {
        auditLog("create_parallel_group", operatorId, groupId, `tasks=${taskIds.join(",")}`);
    }
    return { group_id: groupId, task_count: taskIds.length, tasks };
}
/**
 * 获取并行组信息
 */
export function getParallelGroup(groupId) {
    const tasks = getAll(`SELECT id, status, description FROM tasks WHERE parallel_group=?`, groupId);
    if (tasks.length === 0) {
        throw new Error(`Parallel group not found: ${groupId}`);
    }
    return {
        group_id: groupId,
        tasks: tasks.map(t => ({ id: t.id, status: t.status, description: t.description })),
    };
}
// ═══════════════════════════════════════════════════════════════
// Phase 4b Day 3 — 交接协议（Handoff Protocol）
// ═══════════════════════════════════════════════════════════════
/**
 * 请求交接
 * 当前负责人将任务交接给目标 Agent。目标 Agent 必须 accept/reject。
 * 交接期间任务状态保持不变，handoff_status 设为 'requested'。
 */
export function requestHandoff(taskId, targetAgentId, operatorId) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (TERMINAL_STATES.has(task.status))
        throw new Error(`Cannot handoff task in terminal state: ${task.status}`);
    if (task.handoff_status === "requested")
        throw new Error(`Handoff already requested for task: ${taskId}`);
    if (!task.assigned_to)
        throw new Error(`Task has no assignee: ${taskId}`);
    // 只有负责人或创建者可以请求交接
    if (operatorId !== task.assigned_to && operatorId !== task.assigned_by) {
        throw new Error(`Only assignee or creator can request handoff. Current: ${operatorId}, assignee: ${task.assigned_to}`);
    }
    const now = Date.now();
    db.prepare(`UPDATE tasks SET handoff_status='requested', handoff_to=?, updated_at=? WHERE id=?`).run(targetAgentId, now, taskId);
    auditLog("request_handoff", operatorId, taskId, `→${targetAgentId}`);
    // SSE 通知目标 Agent
    pushToAgent(targetAgentId, {
        type: "handoff_requested",
        content: JSON.stringify({
            task_id: taskId,
            description: task.description,
            from: task.assigned_to,
            priority: task.priority,
            hint: "调用 accept_handoff 接管任务，或 reject_handoff 拒绝交接。",
        }),
    });
    // SSE 通知原负责人
    if (task.assigned_to !== operatorId) {
        pushToAgent(task.assigned_to, {
            type: "handoff_requested",
            content: JSON.stringify({
                task_id: taskId,
                from: operatorId,
                to: targetAgentId,
            }),
        });
    }
    return { task_id: taskId, handoff_status: "requested", from: task.assigned_to, to: targetAgentId };
}
/**
 * 接受交接
 * 目标 Agent 接受交接，任务 assigned_to 转移。
 */
export function acceptHandoff(taskId, operatorId) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (task.handoff_status !== "requested")
        throw new Error(`No pending handoff for task: ${taskId}`);
    if (!task.handoff_to)
        throw new Error(`Task handoff_to is null: ${taskId}`);
    // 只有目标 Agent 可以接受
    if (operatorId !== task.handoff_to) {
        throw new Error(`Only the target agent can accept handoff. Target: ${task.handoff_to}, caller: ${operatorId}`);
    }
    const now = Date.now();
    const oldAssignee = task.assigned_to;
    db.prepare(`UPDATE tasks SET assigned_to=?, handoff_status='accepted', handoff_to=null, assigned_at=?, updated_at=? WHERE id=?`).run(operatorId, now, now, taskId);
    auditLog("accept_handoff", operatorId, taskId, `from=${oldAssignee}`);
    // SSE 通知原负责人
    if (oldAssignee) {
        pushToAgent(oldAssignee, {
            type: "handoff_accepted",
            content: JSON.stringify({
                task_id: taskId,
                accepted_by: operatorId,
            }),
        });
    }
    // SSE 通知创建者
    if (task.assigned_by && task.assigned_by !== oldAssignee && task.assigned_by !== operatorId) {
        pushToAgent(task.assigned_by, {
            type: "handoff_accepted",
            content: JSON.stringify({
                task_id: taskId,
                from: oldAssignee,
                to: operatorId,
            }),
        });
    }
    // SSE 通知新负责人（任务已分配给你）
    pushToAgent(operatorId, {
        type: "task_assigned",
        content: JSON.stringify({
            task_id: taskId,
            description: task.description,
            priority: task.priority,
            context: task.context,
            from: oldAssignee,
            hint: "你已接管此任务。调用 update_task_status(in_progress) 开始执行。",
        }),
    });
    return { task_id: taskId, new_assignee: operatorId };
}
/**
 * 拒绝交接
 * 目标 Agent 拒绝交接，handoff_status 回退为 null。
 */
export function rejectHandoff(taskId, operatorId, reason) {
    const task = getOne(`SELECT * FROM tasks WHERE id=?`, taskId);
    if (!task)
        throw new Error(`Task not found: ${taskId}`);
    if (task.handoff_status !== "requested")
        throw new Error(`No pending handoff for task: ${taskId}`);
    // 只有目标 Agent 可以拒绝
    if (operatorId !== task.handoff_to) {
        throw new Error(`Only the target agent can reject handoff. Target: ${task.handoff_to}, caller: ${operatorId}`);
    }
    const now = Date.now();
    const rejectReason = reason ?? "No reason provided";
    db.prepare(`UPDATE tasks SET handoff_status=null, handoff_to=null, updated_at=? WHERE id=?`).run(now, taskId);
    auditLog("reject_handoff", operatorId, taskId, `reason=${rejectReason}`);
    // SSE 通知原负责人
    if (task.assigned_to) {
        pushToAgent(task.assigned_to, {
            type: "handoff_rejected",
            content: JSON.stringify({
                task_id: taskId,
                rejected_by: operatorId,
                reason: rejectReason,
            }),
        });
    }
    return { task_id: taskId, rejected_by: operatorId, reason: rejectReason };
}
// ═══════════════════════════════════════════════════════════════
// Phase 4b Day 3 — 质量门（Quality Gate）业务逻辑
// ═══════════════════════════════════════════════════════════════
/**
 * 添加质量门
 * 在 Pipeline 中设置质量门。质量门在指定 order_index 之后阻塞后续任务。
 */
export function addQualityGate(pipelineId, gateName, criteria, afterOrder, operatorId) {
    // 验证 Pipeline 存在
    const pipeline = getOne(`SELECT * FROM pipelines WHERE id=?`, pipelineId);
    if (!pipeline)
        throw new Error(`Pipeline not found: ${pipelineId}`);
    const now = Date.now();
    const gate = taskRepo.addQualityGate({
        pipeline_id: pipelineId,
        gate_name: gateName,
        criteria,
        after_order: afterOrder,
        status: "pending",
        evaluator_id: null,
        result: null,
        evaluated_at: null,
        created_at: now,
    });
    auditLog("add_quality_gate", operatorId, gate.id, `pipeline=${pipelineId}, name=${gateName}, after=${afterOrder}`);
    return { gate, pipeline_id: pipelineId };
}
/**
 * 评估质量门
 * 评估者对质量门进行通过/失败判定。
 * 质量门失败时，检查 Pipeline 中是否有 after_order 之后的任务需要阻止。
 */
export function evaluateQualityGate(gateId, status, evaluatorId, result) {
    // 验证质量门存在
    const gate = getOne(`SELECT id, pipeline_id, status, after_order FROM quality_gates WHERE id=?`, gateId);
    if (!gate)
        throw new Error(`Quality gate not found: ${gateId}`);
    if (gate.status !== "pending")
        throw new Error(`Quality gate already evaluated: ${gate.status}`);
    // 更新质量门状态
    taskRepo.updateQualityGateStatus(gateId, status, evaluatorId, result);
    auditLog("evaluate_quality_gate", evaluatorId, gateId, `status=${status}`);
    // 如果质量门失败，找出 Pipeline 中 after_order 之后的任务并设为 waiting
    const blockedTasks = [];
    if (status === "failed") {
        const laterTasks = getAll(`SELECT pt.task_id, t.status
       FROM pipeline_tasks pt
       JOIN tasks t ON pt.task_id = t.id
       WHERE pt.pipeline_id=? AND pt.order_index > ?
         AND t.status NOT IN ('completed', 'failed', 'cancelled')`, gate.pipeline_id, gate.after_order);
        for (const t of laterTasks) {
            if (t.status !== "waiting") {
                taskRepo.setTaskWaiting(t.task_id);
                blockedTasks.push(t.task_id);
                const task = getOne(`SELECT assigned_to FROM tasks WHERE id=?`, t.task_id);
                if (task?.assigned_to) {
                    pushToAgent(task.assigned_to, {
                        type: "quality_gate_failed",
                        content: JSON.stringify({
                            task_id: t.task_id,
                            gate_id: gateId,
                            gate_name: gateId,
                            hint: "前置质量门未通过，任务已暂停。等待质量门重新评估。",
                        }),
                    });
                }
            }
        }
    }
    return { gate_id: gateId, status, blocked_tasks: blockedTasks };
}
//# sourceMappingURL=orchestrator.js.map