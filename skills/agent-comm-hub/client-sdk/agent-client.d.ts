/**
 * agent-client.ts — 通用 Agent 客户端 SDK
 * WorkBuddy 和 Hermes 都用这个文件接入 Hub
 *
 * 功能：
 *  1. SSE 长连接（自动重连，零轮询）
 *  2. MCP 工具调用封装（HTTP POST /mcp，含 initialize 握手）
 *  3. 事件路由（new_message / task_assigned / task_updated / pending_messages）
 */
import { EventEmitter } from "events";
export interface AgentClientOptions {
    agentId: string;
    hubUrl: string;
    onTaskAssigned?: (task: TaskEvent) => Promise<void>;
    onMessage?: (msg: MessageEvent) => Promise<void>;
    onTaskUpdated?: (upd: TaskUpdateEvent) => Promise<void>;
    reconnectDelay?: number;
    mcpTimeout?: number;
}
export interface TaskEvent {
    id: string;
    assigned_by: string;
    assigned_to: string;
    description: string;
    context?: string;
    priority: string;
    status: string;
    instruction: string;
}
export interface MessageEvent {
    id: string;
    from_agent: string;
    to_agent: string;
    content: string;
    type: string;
    metadata?: Record<string, unknown>;
    created_at: number;
}
export interface TaskUpdateEvent {
    task_id: string;
    status: string;
    result?: string;
    progress: number;
    updated_by: string;
    timestamp: number;
}
export declare class AgentClient extends EventEmitter {
    private opts;
    private sse;
    private stopping;
    private sessionId;
    private initialized;
    private initPromise;
    private _apiToken;
    constructor(opts: AgentClientOptions);
    start(): Promise<void>;
    stop(): void;
    /**
     * MCP Streamable HTTP Transport 要求先完成 initialize 握手：
     *   1. POST /mcp { method: "initialize", ... }
     *   2. 服务端返回 { result: { capabilities, ... } }
     *   3. POST /mcp { method: "notifications/initialized" }
     *
     * 注意：Hub 使用 Stateless 模式，每次请求独立，无需 session ID。
     */
    private ensureInitialized;
    private doInitialize;
    /**
     * 底层 MCP POST 请求封装
     * 返回 { body: parsedJson, sessionId: Mcp-Session-Id header value }
     *
     * 注意：MCP Streamable HTTP 用 SSE 格式返回响应：
     *   event: message\n
     *   data: {"result":...,"jsonrpc":"2.0","id":1}\n
     *   \n
     * Hub 使用 Stateless 模式，每个请求独立，无需 session ID。
     */
    private postMcp;
    private connectSSE;
    private bindSSEEvents;
    private routeEvent;
    private callTool;
    private _callTool;
    /** 发送消息给另一个 Agent */
    sendMessage(to: string, content: string, metadata?: Record<string, unknown>): Promise<any>;
    /** 分配任务给另一个 Agent */
    assignTask(to: string, description: string, context?: string, priority?: string): Promise<any>;
    /** 汇报任务进度 */
    updateTaskStatus(taskId: string, status: "in_progress" | "completed" | "failed", result?: string, progress?: number): Promise<any>;
    /** 查询任务状态 */
    getTaskStatus(taskId: string): Promise<any>;
    /** 查询在线 Agent */
    getOnlineAgents(): Promise<string[]>;
    /** 广播消息 */
    broadcast(agentIds: string[], content: string, metadata?: Record<string, unknown>): Promise<any>;
    /** 分享经验（直接 approved，无需审批） */
    shareExperience(title: string, content: string, tags?: string[], taskId?: string): Promise<any>;
    /** 提议策略（需 admin 审批） */
    proposeStrategy(title: string, content: string, category?: "workflow" | "fix" | "tool_config" | "prompt_template" | "other", taskId?: string): Promise<any>;
    /** 查询策略列表 */
    listStrategies(opts?: {
        status?: string;
        category?: string;
        proposerId?: string;
        limit?: number;
    }): Promise<any>;
    /** FTS5 全文搜索策略 */
    searchStrategies(query: string, opts?: {
        category?: string;
        limit?: number;
    }): Promise<any>;
    /** 采纳策略 */
    applyStrategy(strategyId: number, context?: string): Promise<any>;
    /** 对策略反馈（每 Agent 每策略一次） */
    feedbackStrategy(strategyId: number, feedback: "positive" | "negative" | "neutral", opts?: {
        comment?: string;
        applied?: boolean;
    }): Promise<any>;
    /** 审批策略（admin only） */
    approveStrategy(strategyId: number, action: "approve" | "reject", reason: string): Promise<any>;
    /** 查看进化指标统计 */
    getEvolutionStatus(): Promise<any>;
    /**
     * 存储一条记忆
     * @param content 记忆正文
     * @param opts 可选字段：title / scope / tags / sourceTaskId
     * @returns { memoryId: string }
     */
    storeMemory(content: string, opts?: {
        title?: string;
        scope?: "private" | "group" | "collective";
        tags?: string[];
        sourceTaskId?: string;
    }): Promise<any>;
    /**
     * 语义搜索记忆（模糊查询）
     * @param query 搜索关键词
     * @param opts 可选字段：scope / limit
     * @returns 匹配的记忆列表
     */
    recallMemory(query: string, opts?: {
        scope?: string;
        limit?: number;
    }): Promise<any>;
    /**
     * 列出记忆（分页）
     * @param opts 可选字段：scope / limit / offset
     * @returns 记忆列表
     */
    listMemories(opts?: {
        scope?: string;
        limit?: number;
        offset?: number;
    }): Promise<any>;
    /**
     * 删除指定记忆
     * @param memoryId 记忆 ID
     * @returns 删除结果
     */
    deleteMemory(memoryId: string): Promise<any>;
    /**
     * 通过 REST API 查询任务列表（支持过滤）
     * @param status 状态过滤（如 "in_progress"）
     * @returns 任务列表
     */
    getTasks(status?: string): Promise<any>;
    /**
     * 取消一个进行中的任务（MCP callTool）
     * @param taskId 任务 ID
     * @returns 取消结果
     */
    cancelTask(taskId: string): Promise<any>;
    /**
     * 添加任务依赖关系
     * @param upstreamId 上游任务 ID
     * @param downstreamId 下游任务 ID
     * @param depType 依赖类型，默认 "finish_to_start"
     * @returns 添加结果
     */
    addDependency(upstreamId: string, downstreamId: string, depType?: string): Promise<any>;
    /**
     * 移除任务依赖关系
     * @param upstreamId 上游任务 ID
     * @param downstreamId 下游任务 ID
     * @returns 移除结果
     */
    removeDependency(upstreamId: string, downstreamId: string): Promise<any>;
    /**
     * 查询指定任务的所有依赖关系
     * @param taskId 任务 ID
     * @returns 依赖关系列表
     */
    getTaskDependencies(taskId: string): Promise<any>;
    /**
     * 检查指定任务的所有上游依赖是否已满足（全部完成）
     * @param taskId 任务 ID
     * @returns { satisfied: boolean; missing: string[] }
     */
    checkDependenciesSatisfied(taskId: string): Promise<any>;
    /**
     * 创建并行组（组内任务可同时执行）
     * @param taskIds 任务 ID 列表
     * @param groupName 可选的组名称
     * @returns { groupId: string }
     */
    createParallelGroup(taskIds: string[], groupName?: string): Promise<any>;
    /**
     * 请求任务交接给另一个 Agent
     * @param taskId 任务 ID
     * @param targetAgentId 目标 Agent ID
     * @returns 交接请求结果
     */
    requestHandoff(taskId: string, targetAgentId: string): Promise<any>;
    /**
     * 接受任务交接
     * @param taskId 任务 ID
     * @returns 接受结果
     */
    acceptHandoff(taskId: string): Promise<any>;
    /**
     * 拒绝任务交接
     * @param taskId 任务 ID
     * @param reason 拒绝原因
     * @returns 拒绝结果
     */
    rejectHandoff(taskId: string, reason?: string): Promise<any>;
    /**
     * 为 Pipeline 添加质量门
     * @param pipelineId Pipeline ID
     * @param gateName 质量门名称
     * @param criteria 通过标准（SQL WHERE 条件或描述文本）
     * @param afterOrder 在哪个步骤之后插入
     * @returns 添加结果
     */
    addQualityGate(pipelineId: string, gateName: string, criteria: string, afterOrder: number): Promise<any>;
    /**
     * 评估质量门结果
     * @param gateId 质量门 ID
     * @param status 评估结果 "passed" | "failed"
     * @param result 可选的详细结果描述
     * @returns 评估结果
     */
    evaluateQualityGate(gateId: string, status: "passed" | "failed", result?: string): Promise<any>;
    /**
     * 提议策略（支持分级审批，自动根据策略内容判断 tier）
     * @param title 策略标题
     * @param content 策略正文
     * @param opts 可选：category / taskId
     * @returns 策略提案结果
     */
    proposeStrategyTiered(title: string, content: string, opts?: {
        category?: string;
        taskId?: string;
    }): Promise<any>;
    /**
     * 检查策略是否处于 veto 窗口期（可行使否决权的时间窗口）
     * @param strategyId 策略 ID
     * @returns { in_window: boolean; remaining_seconds?: number }
     */
    checkVetoWindow(strategyId: number): Promise<any>;
    /**
     * 对策略行使否决权（需在 veto 窗口期内）
     * @param strategyId 策略 ID
     * @param reason 否决理由
     * @returns 否决结果
     */
    vetoStrategy(strategyId: number, reason: string): Promise<any>;
    /**
     * 设置 Agent 角色（admin only）
     * @param agentId Agent ID
     * @param role 新角色，如 "admin" / "member"
     * @param managedGroupId 可选：管理的组 ID
     * @returns 设置结果
     */
    setAgentRole(agentId: string, role: string, managedGroupId?: string): Promise<any>;
    /**
     * 重新计算 Agent 信任评分（admin only）
     * @param agentId 可选，不传则重算所有 Agent
     * @returns 重算结果
     */
    recalculateTrustScores(agentId?: string): Promise<any>;
    /** 设置 REST API 认证 token（register_agent 返回后调用） */
    setToken(token: string): void;
    /** 撤销 Agent 的 API token（admin only） */
    revokeToken(agentId: string): Promise<any>;
    /** 设置 Agent 信任评分（admin only） */
    setTrustScore(agentId: string, score: number): Promise<any>;
    /**
     * 全文搜索记忆（FTS5）
     * @param query 搜索关键词
     * @param opts 可选：scope / limit
     * @returns 匹配的记忆列表
     */
    searchMemories(query: string, opts?: {
        scope?: string;
        limit?: number;
    }): Promise<any>;
    /**
     * 创建 Pipeline（线性任务容器）
     * @param name Pipeline 名称
     * @param description 可选描述
     * @returns { pipelineId: string }
     */
    createPipeline(name: string, description?: string): Promise<any>;
    /**
     * 获取 Pipeline 详情（含任务列表和依赖关系）
     * @param pipelineId Pipeline ID
     * @returns Pipeline 详情
     */
    getPipeline(pipelineId: string): Promise<any>;
    /**
     * 列出所有 Pipeline
     * @param opts 可选：status / limit
     * @returns Pipeline 列表
     */
    listPipelines(opts?: {
        status?: string;
        limit?: number;
    }): Promise<any>;
    /**
     * 向 Pipeline 添加任务
     * @param pipelineId Pipeline ID
     * @param description 任务描述
     * @param opts 可选：assignedTo / order / dependsOn
     * @returns 添加结果
     */
    addTaskToPipeline(pipelineId: string, description: string, opts?: {
        assignedTo?: string;
        order?: number;
        dependsOn?: string;
    }): Promise<any>;
    /**
     * 全文搜索消息历史（FTS5）
     * @param query 搜索关键词
     * @param opts 可选：agentId（限定发送方）/ limit
     * @returns 匹配的消息列表
     */
    searchMessages(query: string, opts?: {
        agentId?: string;
        limit?: number;
    }): Promise<any>;
}
