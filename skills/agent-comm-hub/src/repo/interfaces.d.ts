/**
 * repo/interfaces.ts — 数据访问层接口定义 (Phase 2 Day 2, Phase 4b 扩展)
 *
 * 将 tools.ts/server.ts 中散落的 msgStmt/taskStmt/consumedStmt 直接 SQL 调用
 * 统一到接口层，便于测试 mock 和未来数据源替换。
 */
import type { Message, Task, ConsumedEntry } from "../db.js";
import type { TaskDependency, QualityGate, DepType, GateStatus } from "./types.js";
export interface IMessageRepo {
    /** 插入新消息 */
    insert(msg: Message): void;
    /** 标记消息为已投递 */
    markDelivered(id: string): void;
    /** 标记消息为已读 */
    markRead(id: string): void;
    /** 标记消息为已确认 */
    markAcknowledged(id: string): void;
    /** 批量标记指定接收方所有未读消息为已投递 */
    markAllDelivered(toAgent: string): void;
    /** 查询指定接收方的待处理消息（status=unread） */
    pendingFor(toAgent: string): Message[];
    /** 按 ID 查询消息 */
    getById(id: string): Message | undefined;
    /** 按接收方 + 状态查询消息 */
    listByStatus(toAgent: string, status: string): Message[];
    /** 更新消息状态（REST PATCH 用） */
    updateStatus(id: string, status: string): void;
    /** 查询指定接收方在指定时间戳之后的消息（用于 SSE 断线重连回放） */
    listSince(toAgent: string, since: number): Message[];
}
export interface ITaskRepo {
    /** 插入新任务 */
    insert(task: Task): void;
    /** 按 ID 查询任务 */
    getById(id: string): Task | undefined;
    /** 更新任务状态/结果/进度 */
    update(id: string, status: string, result: string | null, progress: number): void;
    /** 分配任务（设置 assigned_to + status=assigned） */
    assignTo(id: string, assignedTo: string): void;
    /** 按执行者 + 状态列出任务 */
    listFor(assignedTo: string, status: string): Task[];
    /** 按 Pipeline 列出任务 */
    listByPipeline(pipelineId: string): Task[];
    /** 添加依赖关系（返回依赖记录，失败抛异常） */
    addDependency(upstreamId: string, downstreamId: string, depType?: DepType): TaskDependency;
    /** 删除依赖关系 */
    removeDependency(upstreamId: string, downstreamId: string): void;
    /** 获取任务的上下游依赖 */
    getDependencies(taskId: string): {
        upstreams: TaskDependency[];
        downstreams: TaskDependency[];
    };
    /** 检查任务所有上游依赖是否满足 */
    checkDependenciesSatisfied(taskId: string): boolean;
    /** 设置任务为 waiting 状态 */
    setTaskWaiting(taskId: string): void;
    /** 将 waiting 任务转为 assigned（依赖满足后） */
    setTaskReady(taskId: string): void;
    /** 检测添加依赖是否会形成环 */
    wouldCreateCycle(upstreamId: string, downstreamId: string): boolean;
    /** 将指定 upstream 的所有 downstream 依赖标记为 satisfied */
    satisfyDownstream(upstreamId: string): number;
    /** 添加质量门 */
    addQualityGate(gate: Omit<QualityGate, "id"> & {
        id?: string;
    }): QualityGate;
    /** 更新质量门状态 */
    updateQualityGateStatus(gateId: string, status: GateStatus, evaluatorId: string, result?: string): void;
    /** 列出 Pipeline 的质量门 */
    listGatesByPipeline(pipelineId: string): QualityGate[];
}
export interface IConsumedLogRepo {
    /** 插入消费记录（OR REPLACE） */
    insert(entry: ConsumedEntry): void;
    /** 查询某 agent 对某资源的消费记录 */
    check(agentId: string, resource: string): ConsumedEntry | undefined;
    /** 列出某 agent 的消费记录 */
    listByAgent(agentId: string, limit?: number): ConsumedEntry[];
}
