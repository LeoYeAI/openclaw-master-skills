import { z } from "zod";
import { randomUUID } from "crypto";
import { db } from "../db.js";
import { taskRepo } from "../repo/sqlite-impl.js";
import { pushToAgent } from "../sse.js";
import { auditLog } from "../security.js";
import { addDependency as addDep, removeDependency as removeDep, getDependencies as getDeps, checkDependenciesSatisfied as checkDepsSatisfied, createParallelGroup, requestHandoff, acceptHandoff, rejectHandoff, addQualityGate as addQGate, evaluateQualityGate as evalQGate, createPipeline, getPipelineStatus, addTaskToPipeline, } from "../orchestrator.js";
import { requireAuth } from "../utils.js";
/**
 * 注册 Task Orchestrator 相关工具（16 个）
 */
export function registerOrchestratorTools(server, authContext) {
    // ────────────────────────────────────────────────────
    // Tool 6: assign_task (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("assign_task", "将任务分配给另一个 Agent。对方收到 task_assigned 事件后会自主开始执行，无需人工确认。", {
        from: z.string().describe("发起方 Agent ID"),
        to: z.string().describe("执行方 Agent ID"),
        description: z.string().describe("任务目标描述，尽量清晰，包含期望输出格式"),
        context: z.string().optional()
            .describe("执行任务所需背景信息，减少执行方反复询问"),
        priority: z.enum(["low", "normal", "high", "urgent"]).default("normal"),
    }, async ({ from, to, description, context, priority }) => {
        requireAuth(authContext, "assign_task");
        const task = {
            id: `task_${Date.now()}_${randomUUID().slice(0, 6)}`,
            assigned_by: from,
            assigned_to: to,
            description,
            context: context || null,
            priority,
            status: "assigned",
            result: null,
            progress: 0,
            pipeline_id: null,
            order_index: 0,
            required_capability: null,
            due_at: null,
            assigned_at: Date.now(),
            completed_at: null,
            tags: "[]",
            created_at: Date.now(),
            updated_at: Date.now(),
        };
        taskRepo.insert(task);
        const delivered = pushToAgent(to, {
            event: "task_assigned",
            task: {
                ...task,
                instruction: [
                    "你收到了一项新任务，请立即开始执行。",
                    "执行前先调用 update_task_status（status=in_progress）告知发起方。",
                    "完成后调用 update_task_status（status=completed）并携带结果。",
                    "如遇问题，status=failed 并说明原因。",
                ].join(" "),
            },
        });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        taskId: task.id,
                        assigned_to: to,
                        priority,
                        note: delivered
                            ? `✅ ${to} 在线，任务已实时推送，对方将自主执行`
                            : `📦 ${to} 离线，任务已存储，上线后立即推送执行`,
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Tool 7: update_task_status (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("update_task_status", "更新任务执行状态，自动实时通知发起方。支持中途汇报进度（in_progress + progress）。", {
        task_id: z.string().describe("任务 ID"),
        agent_id: z.string().describe("执行方 Agent ID"),
        status: z.enum(["in_progress", "completed", "failed"]),
        result: z.string().optional().describe("执行结果或错误信息"),
        progress: z.number().min(0).max(100).optional().default(0)
            .describe("完成百分比，0-100"),
    }, async ({ task_id, agent_id, status, result, progress }) => {
        requireAuth(authContext, "update_task_status");
        const task = taskRepo.getById(task_id);
        if (!task) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ error: `Task ${task_id} not found` }),
                    }],
            };
        }
        taskRepo.update(task_id, status, result || null, progress);
        pushToAgent(task.assigned_by, {
            event: "task_updated",
            update: {
                task_id,
                status,
                result,
                progress,
                updated_by: agent_id,
                timestamp: Date.now(),
            },
        });
        return {
            content: [{
                    type: "text",
                    text: JSON.stringify({
                        success: true,
                        task_id,
                        status,
                        progress,
                        notified: task.assigned_by,
                    }, null, 2),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Tool 8: get_task_status (原有，添加权限检查)
    // ────────────────────────────────────────────────────
    server.tool("get_task_status", "查询任务的当前状态、进度和执行结果。", {
        task_id: z.string(),
    }, async ({ task_id }) => {
        requireAuth(authContext, "get_task_status");
        const task = taskRepo.getById(task_id);
        return {
            content: [{
                    type: "text",
                    text: task
                        ? JSON.stringify(task, null, 2)
                        : JSON.stringify({ error: "Task not found" }),
                }],
        };
    });
    // ────────────────────────────────────────────────────
    // Phase 4b Day 2: 依赖链 + 并行组工具
    // ────────────────────────────────────────────────────
    // Tool D1: add_dependency — member 及以上
    server.tool("add_dependency", "添加任务依赖关系。下游任务必须等上游任务完成后才能开始。自动进行环检测。添加后下游任务自动进入等待状态。", {
        upstream_id: z.string().describe("上游任务 ID（需先完成）"),
        downstream_id: z.string().describe("下游任务 ID（依赖上游完成后才能开始）"),
        dep_type: z.enum(["finish_to_start", "start_to_start", "finish_to_finish", "start_to_finish"])
            .optional().default("finish_to_start")
            .describe("依赖类型，默认 finish_to_start"),
    }, async ({ upstream_id, downstream_id, dep_type }) => {
        const ctx = requireAuth(authContext, "add_dependency");
        try {
            const result = addDep(upstream_id, downstream_id, dep_type, ctx.agentId);
            auditLog("tool_add_dependency", ctx.agentId, upstream_id, `→${downstream_id}(${dep_type}), downstream_updated=${result.downstream_updated}`);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            dependency_id: result.dependency.id,
                            upstream_id,
                            downstream_id,
                            dep_type,
                            downstream_updated: result.downstream_updated,
                            hint: result.downstream_updated
                                ? "下游任务状态已更新（waiting 或 ready）"
                                : "下游任务状态未变更（上游已完成或下游在终态）",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool D2: remove_dependency — member 及以上
    server.tool("remove_dependency", "删除任务依赖关系。删除后自动检查下游任务是否可以开始执行。", {
        upstream_id: z.string().describe("上游任务 ID"),
        downstream_id: z.string().describe("下游任务 ID"),
    }, async ({ upstream_id, downstream_id }) => {
        const ctx = requireAuth(authContext, "remove_dependency");
        try {
            const result = removeDep(upstream_id, downstream_id, ctx.agentId);
            auditLog("tool_remove_dependency", ctx.agentId, upstream_id, `→${downstream_id}, downstream_ready=${result.downstream_ready}`);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            upstream_id,
                            downstream_id,
                            removed: result.removed,
                            downstream_ready: result.downstream_ready,
                            hint: result.downstream_ready
                                ? "下游任务已从 waiting 恢复为可执行状态"
                                : "下游任务仍有其他未满足依赖，保持 waiting",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool D3: get_task_dependencies — member 及以上
    server.tool("get_task_dependencies", "查询任务的上下游依赖关系。返回依赖图，包含每个关联任务的状态和依赖类型。", {
        task_id: z.string().describe("要查询的任务 ID"),
    }, async ({ task_id }) => {
        const ctx = requireAuth(authContext, "get_task_dependencies");
        try {
            const deps = getDeps(task_id);
            const check = checkDepsSatisfied(task_id);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            task_id,
                            dependencies_satisfied: check.satisfied,
                            pending_deps: check.pending_deps,
                            upstreams: deps.upstreams,
                            downstreams: deps.downstreams,
                            queried_by: ctx.agentId,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool D4: create_parallel_group — member 及以上
    server.tool("create_parallel_group", "将多个任务标记为并行组。同一并行组内的任务可以同时执行，无需等待其他任务完成。适用于无依赖关系的同层任务。", {
        task_ids: z.array(z.string()).min(2).max(10)
            .describe("并行任务 ID 列表（至少 2 个，最多 10 个）"),
    }, async ({ task_ids }) => {
        const ctx = requireAuth(authContext, "create_parallel_group");
        try {
            const result = createParallelGroup(task_ids, ctx.agentId);
            auditLog("tool_create_parallel_group", ctx.agentId, result.group_id, `task_count=${result.task_count}`);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            group_id: result.group_id,
                            task_count: result.task_count,
                            tasks: result.tasks,
                            hint: "同一并行组内的任务可以同时执行，互不阻塞",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Phase 4b Day 3: 交接协议工具
    // ────────────────────────────────────────────────────
    // Tool H1: request_handoff — member 及以上
    server.tool("request_handoff", "请求任务交接。将任务转交给另一个 Agent。目标 Agent 需要调用 accept_handoff 或 reject_handoff。只有负责人或创建者可以发起交接。", {
        task_id: z.string().describe("要交接的任务 ID"),
        target_agent_id: z.string().describe("目标 Agent ID（交接对象）"),
    }, async ({ task_id, target_agent_id }) => {
        const ctx = requireAuth(authContext, "request_handoff");
        try {
            const result = requestHandoff(task_id, target_agent_id, ctx.agentId);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            task_id: result.task_id,
                            handoff_status: result.handoff_status,
                            from: result.from,
                            to: result.to,
                            hint: `已向 ${target_agent_id} 发送交接请求，等待对方响应`,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool H2: accept_handoff — member 及以上
    server.tool("accept_handoff", "接受任务交接。只有被请求的 target Agent 可以调用。接受后任务 assigned_to 转移到当前 Agent。", {
        task_id: z.string().describe("要接受的任务 ID"),
    }, async ({ task_id }) => {
        const ctx = requireAuth(authContext, "accept_handoff");
        try {
            const result = acceptHandoff(task_id, ctx.agentId);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            task_id: result.task_id,
                            new_assignee: result.new_assignee,
                            hint: "你已接管此任务。调用 update_task_status(in_progress) 开始执行。",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool H3: reject_handoff — member 及以上
    server.tool("reject_handoff", "拒绝任务交接。只有被请求的 target Agent 可以调用。拒绝后交接请求取消。", {
        task_id: z.string().describe("要拒绝的任务 ID"),
        reason: z.string().optional().describe("拒绝原因"),
    }, async ({ task_id, reason }) => {
        const ctx = requireAuth(authContext, "reject_handoff");
        try {
            const result = rejectHandoff(task_id, ctx.agentId, reason);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            task_id: result.task_id,
                            rejected_by: result.rejected_by,
                            reason: result.reason,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Phase 4b Day 3: 质量门工具
    // ────────────────────────────────────────────────────
    // Tool Q1: add_quality_gate — member 及以上
    server.tool("add_quality_gate", "在 Pipeline 中添加质量门。质量门在指定 order_index 之后阻塞后续任务，直到评估通过。criteria 为 JSON 格式的检查规则。", {
        pipeline_id: z.string().describe("Pipeline ID"),
        gate_name: z.string().describe("质量门名称"),
        criteria: z.string().describe("评估规则（JSON 格式，如 {\"type\":\"manual\",\"check\":\"code_review\"}）"),
        after_order: z.number().int().min(0).describe("在哪个 order_index 之后的任务需要等待此质量门通过"),
    }, async ({ pipeline_id, gate_name, criteria, after_order }) => {
        const ctx = requireAuth(authContext, "add_quality_gate");
        try {
            const result = addQGate(pipeline_id, gate_name, criteria, after_order, ctx.agentId);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            gate_id: result.gate.id,
                            pipeline_id: result.pipeline_id,
                            gate_name: result.gate.gate_name,
                            after_order: result.gate.after_order,
                            status: "pending",
                            hint: "质量门已创建，等待 evaluate_quality_gate 评估",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool Q2: evaluate_quality_gate — member 及以上
    server.tool("evaluate_quality_gate", "评估质量门（通过/失败）。质量门失败时，Pipeline 中阻塞的后续任务自动进入 waiting 状态。", {
        gate_id: z.string().describe("质量门 ID"),
        status: z.enum(["passed", "failed"]).describe("评估结果"),
        result: z.string().optional().describe("评估说明"),
    }, async ({ gate_id, status, result }) => {
        const ctx = requireAuth(authContext, "evaluate_quality_gate");
        try {
            const evalResult = evalQGate(gate_id, status, ctx.agentId, result);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            gate_id: evalResult.gate_id,
                            status: evalResult.status,
                            blocked_tasks: evalResult.blocked_tasks,
                            hint: evalResult.blocked_tasks.length > 0
                                ? `质量门未通过，${evalResult.blocked_tasks.length} 个任务已暂停`
                                : evalResult.status === "passed"
                                    ? "质量门已通过，后续任务可继续执行"
                                    : "质量门评估完成",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // ────────────────────────────────────────────────────
    // Phase 6: Pipeline MCP 工具
    // ────────────────────────────────────────────────────
    // Tool P1: create_pipeline — member 及以上
    server.tool("create_pipeline", "创建一个新的 Pipeline（任务流水线）。Pipeline 是任务的有序容器，可添加质量门进行阶段性质量检查。", {
        name: z.string().describe("Pipeline 名称"),
        description: z.string().optional().describe("Pipeline 描述"),
    }, async ({ name, description }) => {
        const ctx = requireAuth(authContext, "create_pipeline");
        try {
            const pipeline = createPipeline({
                name,
                description,
                creator: ctx.agentId,
            });
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            pipeline_id: pipeline.id,
                            name: pipeline.name,
                            status: pipeline.status,
                            note: "Pipeline 已创建（draft 状态）。使用 add_task_to_pipeline 添加任务，完成后调用 update_pipeline_status 激活。",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool P2: get_pipeline — member 及以上
    server.tool("get_pipeline", "查询 Pipeline 状态和进度。返回 Pipeline 信息、关联任务列表及各状态统计。", {
        pipeline_id: z.string().describe("Pipeline ID"),
    }, async ({ pipeline_id }) => {
        const ctx = requireAuth(authContext, "get_pipeline");
        try {
            const result = getPipelineStatus(pipeline_id);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            pipeline: result.pipeline,
                            tasks: result.tasks.map(t => ({
                                id: t.id,
                                description: t.description,
                                status: t.status,
                                progress: t.progress,
                                assigned_to: t.assigned_to,
                                order_index: t.order_index,
                            })),
                            stats: result.stats,
                            queried_by: ctx.agentId,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool P3: list_pipelines — member 及以上
    server.tool("list_pipelines", "列出所有 Pipeline。支持按状态筛选，按创建时间倒序排列。", {
        status: z.enum(["active", "completed", "cancelled", "all"]).optional()
            .default("all").describe("状态筛选"),
        limit: z.number().min(1).max(50).optional().default(20)
            .describe("最大返回数量"),
    }, async ({ status, limit }) => {
        const ctx = requireAuth(authContext, "list_pipelines");
        try {
            const conditions = [];
            const params = [];
            if (status !== "all") {
                conditions.push("status = ?");
                params.push(status);
            }
            const where = conditions.length > 0 ? `WHERE ${conditions.join(" AND ")}` : "";
            const pipelines = db.prepare(`SELECT * FROM pipelines ${where} ORDER BY created_at DESC LIMIT ?`).all(...params, limit);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            pipelines: pipelines.map(p => ({
                                id: p.id,
                                name: p.name,
                                description: p.description,
                                status: p.status,
                                creator: p.creator,
                                created_at: p.created_at,
                                updated_at: p.updated_at,
                            })),
                            count: pipelines.length,
                            queried_by: ctx.agentId,
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
    // Tool P4: add_task_to_pipeline — member 及以上
    server.tool("add_task_to_pipeline", "将任务添加到 Pipeline。指定任务在 Pipeline 中的顺序。不传 order_index 则自动追加到末尾。", {
        pipeline_id: z.string().describe("Pipeline ID"),
        task_id: z.string().describe("任务 ID"),
        order_index: z.number().int().min(0).optional().describe("顺序索引（不传则自动追加到末尾）"),
    }, async ({ pipeline_id, task_id, order_index }) => {
        const ctx = requireAuth(authContext, "add_task_to_pipeline");
        try {
            const result = addTaskToPipeline(pipeline_id, task_id, order_index, ctx.agentId);
            auditLog("tool_add_task_to_pipeline", ctx.agentId, pipeline_id, `task=${task_id}, order=${result.order_index}`);
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({
                            success: true,
                            pipeline_task_id: result.id,
                            pipeline_id,
                            task_id,
                            order_index: result.order_index,
                            note: "任务已添加到 Pipeline",
                        }, null, 2),
                    }],
            };
        }
        catch (err) {
            return {
                content: [{
                        type: "text",
                        text: JSON.stringify({ success: false, error: err.message }),
                    }],
            };
        }
    });
}
//# sourceMappingURL=orchestrator.js.map