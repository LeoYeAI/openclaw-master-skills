import { type Task, type Pipeline, type PipelineTask } from "./db.js";
import type { DepType } from "./repo/types.js";
import { taskRepo } from "./repo/sqlite-impl.js";
export type TaskCreateInput = {
    description: string;
    context?: string;
    priority?: "low" | "normal" | "high" | "urgent";
    assigned_to?: string;
    assigned_by: string;
    pipeline_id?: string;
    required_capability?: string;
    tags?: string[];
    due_at?: number;
};
/**
 * 创建任务
 */
export declare function createTask(input: TaskCreateInput): Task;
/**
 * 分配任务（inbox → assigned 或重新分配）
 */
export declare function assignTask(taskId: string, toAgent: string, operatorId: string): Task;
/**
 * 认领任务（inbox → assigned）
 */
export declare function claimTask(taskId: string, agentId: string): Task;
/**
 * 取消任务
 */
export declare function cancelTask(taskId: string, operatorId: string, reason?: string): Task;
/**
 * 更新任务状态（带状态机校验）
 */
export declare function updateTaskStatus(taskId: string, status: string, operatorId: string, result?: string | null, progress?: number): Task;
/**
 * 多维查询任务
 */
export declare function listTasks(filters: {
    assigned_to?: string;
    assigned_by?: string;
    status?: string;
    pipeline_id?: string;
    required_capability?: string;
    limit?: number;
}): Task[];
export type PipelineCreateInput = {
    name: string;
    description?: string;
    creator: string;
    config?: {
        auto_assign?: boolean;
        capability_match?: boolean;
    };
};
/**
 * 创建 Pipeline
 */
export declare function createPipeline(input: PipelineCreateInput): Pipeline;
/**
 * 激活 Pipeline
 */
export declare function activatePipeline(pipelineId: string, operatorId: string): Pipeline;
/**
 * 完成 Pipeline
 */
export declare function completePipeline(pipelineId: string, operatorId: string): Pipeline;
/**
 * 取消 Pipeline
 */
export declare function cancelPipeline(pipelineId: string, operatorId: string): Pipeline;
/**
 * 添加任务到 Pipeline
 */
export declare function addTaskToPipeline(pipelineId: string, taskId: string, orderIndex?: number, operatorId?: string): PipelineTask;
/**
 * 获取 Pipeline 进度
 */
export declare function getPipelineStatus(pipelineId: string): {
    pipeline: Pipeline;
    tasks: Task[];
    stats: {
        total: number;
        inbox: number;
        assigned: number;
        in_progress: number;
        completed: number;
        failed: number;
        cancelled: number;
    };
};
export type CapabilityInput = {
    agent_id: string;
    capability: string;
    params?: Record<string, unknown>;
    verified?: boolean;
};
/**
 * 注册 Agent 能力
 */
export declare function registerCapability(input: CapabilityInput): {
    id: string;
};
/**
 * 智能推荐任务执行方
 */
export declare function suggestAssignee(taskId: string): Array<{
    agent_id: string;
    name: string;
    capability_match: boolean;
    online: boolean;
    current_tasks: number;
}>;
/**
 * 添加任务依赖关系（含环检测）
 */
export declare function addDependency(upstreamId: string, downstreamId: string, depType?: DepType, operatorId?: string): {
    dependency: ReturnType<typeof taskRepo.addDependency>;
    downstream_updated: boolean;
};
/**
 * 删除依赖关系
 */
export declare function removeDependency(upstreamId: string, downstreamId: string, operatorId?: string): {
    removed: boolean;
    downstream_ready: boolean;
};
/**
 * 获取任务的上下游依赖
 */
export declare function getDependencies(taskId: string): {
    upstreams: Array<{
        task_id: string;
        status: string;
        dep_type: string;
        dep_status: string;
    }>;
    downstreams: Array<{
        task_id: string;
        status: string;
        dep_type: string;
        dep_status: string;
    }>;
};
/**
 * 检查任务依赖是否满足
 */
export declare function checkDependenciesSatisfied(taskId: string): {
    satisfied: boolean;
    pending_deps: Array<{
        task_id: string;
        dep_type: string;
    }>;
};
/**
 * 创建并行组
 * 将多个任务标记为同一 parallel_group，表示它们可以并行执行。
 * 同一 parallel_group 内的任务在 Pipeline 中逻辑上是并行的。
 */
export declare function createParallelGroup(taskIds: string[], operatorId?: string): {
    group_id: string;
    task_count: number;
    tasks: Array<{
        id: string;
        parallel_group: string;
    }>;
};
/**
 * 获取并行组信息
 */
export declare function getParallelGroup(groupId: string): {
    group_id: string;
    tasks: Array<{
        id: string;
        status: string;
        description: string;
    }>;
};
/**
 * 请求交接
 * 当前负责人将任务交接给目标 Agent。目标 Agent 必须 accept/reject。
 * 交接期间任务状态保持不变，handoff_status 设为 'requested'。
 */
export declare function requestHandoff(taskId: string, targetAgentId: string, operatorId: string): {
    task_id: string;
    handoff_status: string;
    from: string;
    to: string;
};
/**
 * 接受交接
 * 目标 Agent 接受交接，任务 assigned_to 转移。
 */
export declare function acceptHandoff(taskId: string, operatorId: string): {
    task_id: string;
    new_assignee: string;
};
/**
 * 拒绝交接
 * 目标 Agent 拒绝交接，handoff_status 回退为 null。
 */
export declare function rejectHandoff(taskId: string, operatorId: string, reason?: string): {
    task_id: string;
    rejected_by: string;
    reason: string;
};
/**
 * 添加质量门
 * 在 Pipeline 中设置质量门。质量门在指定 order_index 之后阻塞后续任务。
 */
export declare function addQualityGate(pipelineId: string, gateName: string, criteria: string, afterOrder: number, operatorId: string): {
    gate: ReturnType<typeof taskRepo.addQualityGate>;
    pipeline_id: string;
};
/**
 * 评估质量门
 * 评估者对质量门进行通过/失败判定。
 * 质量门失败时，检查 Pipeline 中是否有 after_order 之后的任务需要阻止。
 */
export declare function evaluateQualityGate(gateId: string, status: "passed" | "failed", evaluatorId: string, result?: string): {
    gate_id: string;
    status: string;
    blocked_tasks: string[];
};
