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

// ─── 类型定义 ──────────────────────────────────────────
export interface AgentClientOptions {
  agentId:  string;          // 本 Agent 的唯一标识，如 "workbuddy" 或 "hermes"
  hubUrl:   string;          // Hub 地址，如 "http://localhost:3100"
  onTaskAssigned?: (task: TaskEvent) => Promise<void>;   // 收到新任务时的处理函数
  onMessage?:      (msg:  MessageEvent) => Promise<void>;// 收到消息时的处理函数
  onTaskUpdated?:  (upd:  TaskUpdateEvent) => Promise<void>; // 任务进度回调
  reconnectDelay?: number;   // 断线重连间隔（ms），默认 3000
  mcpTimeout?:     number;   // MCP 请求超时（ms），默认 15000
}

export interface TaskEvent {
  id:          string;
  assigned_by: string;
  assigned_to: string;
  description: string;
  context?:    string;
  priority:    string;
  status:      string;
  instruction: string;
}

export interface MessageEvent {
  id:         string;
  from_agent: string;
  to_agent:   string;
  content:    string;
  type:       string;
  metadata?:  Record<string, unknown>;
  created_at: number;
}

export interface TaskUpdateEvent {
  task_id:    string;
  status:     string;
  result?:    string;
  progress:   number;
  updated_by: string;
  timestamp:  number;
}

// ─── AgentClient 类 ────────────────────────────────────
export class AgentClient extends EventEmitter {
  private opts:       AgentClientOptions;
  private sse:        any = null;  // EventSource 实例
  private stopping:   boolean = false;
  private sessionId:  string | null = null;  // MCP session ID
  private initialized: boolean = false;
  private initPromise: Promise<void> | null = null;  // 并发安全
  private _apiToken:  string = "";  // REST API 认证 token

  constructor(opts: AgentClientOptions) {
    super();
    this.opts = {
      reconnectDelay: 3000,
      mcpTimeout:     15000,
      ...opts,
    };
  }

  // ── 启动：MCP 握手 + 建立 SSE 连接 ──────────────────
  async start(): Promise<void> {
    this.stopping = false;
    await this.ensureInitialized();
    this.connectSSE();
    console.log(`[${this.opts.agentId}] 已启动，连接 Hub: ${this.opts.hubUrl}`);
  }

  stop(): void {
    this.stopping = true;
    this.initialized = false;
    this.sessionId = null;
    this.initPromise = null;
    this.sse?.close();
    console.log(`[${this.opts.agentId}] 已停止`);
  }

  // ── MCP Initialize 握手（P0 修复）──────────────────
  /**
   * MCP Streamable HTTP Transport 要求先完成 initialize 握手：
   *   1. POST /mcp { method: "initialize", ... }
   *   2. 服务端返回 { result: { capabilities, ... } }
   *   3. POST /mcp { method: "notifications/initialized" }
   *
   * 注意：Hub 使用 Stateless 模式，每次请求独立，无需 session ID。
   */
  private async ensureInitialized(): Promise<void> {
    if (this.initialized) return;

    // 防止并发多次握手
    if (this.initPromise) return this.initPromise;

    this.initPromise = this.doInitialize();
    try {
      await this.initPromise;
    } finally {
      this.initPromise = null;
    }
  }

  private async doInitialize(): Promise<void> {
    const timeout = this.opts.mcpTimeout!;

    // Step 1: initialize 请求（stateless 模式：每次都成功）
    const initRes = await this.postMcp(
      {
        jsonrpc: "2.0",
        id:      1,
        method:  "initialize",
        params:  {
          protocolVersion: "2025-03-26",
          capabilities:   {},
          clientInfo:     {
            name:    `agent-client-${this.opts.agentId}`,
            version: "1.0.0",
          },
        },
      },
      timeout
    );

    if (initRes.body?.error) {
      throw new Error(`MCP initialize failed: ${JSON.stringify(initRes.body.error)}`);
    }

    console.log(`[${this.opts.agentId}] MCP initialized (stateless)`);

    // Step 2: 发送 initialized 通知（无 id 字段 = notification）
    await this.postMcp(
      {
        jsonrpc: "2.0",
        method:  "notifications/initialized",
      },
      timeout
    );

    this.initialized = true;
  }

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
  private async postMcp(payload: object, timeout: number): Promise<{ body: any; sessionId: string | null }> {
    const url = `${this.opts.hubUrl}/mcp`;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeout);

    try {
      const res = await fetch(url, {
        method:  "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept":        "application/json, text/event-stream",
        },
        body:    JSON.stringify(payload),
        signal:  controller.signal,
      });

      const sessionId = res.headers.get("mcp-session-id");

      // 解析 SSE 格式响应：提取 data: 行的 JSON
      const raw = await res.text();
      let body: any;

      if (res.headers.get("content-type")?.includes("text/event-stream")) {
        // SSE 格式：找 "data: " 开头的行
        const dataLine = raw.split("\n")
          .map(line => line.trim())
          .find(line => line.startsWith("data: "));

        if (dataLine) {
          const jsonStr = dataLine.slice(6); // 去掉 "data: " 前缀
          body = JSON.parse(jsonStr);
        } else {
          body = null;
        }
      } else {
        // 普通 JSON 响应
        body = raw ? JSON.parse(raw) : null;
      }

      return { body, sessionId };
    } catch (err: any) {
      if (err.name === "AbortError") {
        throw new Error(`MCP request timeout (${timeout}ms): ${JSON.stringify(payload)}`);
      }
      throw err;
    } finally {
      clearTimeout(timer);
    }
  }

  // ── SSE 连接（含自动重连）───────────────────────────
  private connectSSE(): void {
    const url = `${this.opts.hubUrl}/events/${this.opts.agentId}`;

    try {
      // 尝试浏览器原生
      this.sse = new (globalThis as any).EventSource(url);
    } catch {
      // Node.js 回退：动态 import eventsource 包（ESM 兼容）
      import("eventsource").then((mod: any) => {
        this.sse = new (mod.default || mod.EventSource || mod)(url);
        this.bindSSEEvents();
      });
      return; // bindSSEEvents 将在 import 完成后调用
    }

    this.bindSSEEvents();
  }

  private bindSSEEvents(): void {
    if (!this.sse) return;

    // P0-3: 重连超时缩短到 5 秒（原来依赖 opts.reconnectDelay 3000ms）
    // EventSource 内置重连逻辑由服务端心跳控制，这里用 onerror兜底
    this.sse.onmessage = (e: { data: string }) => {
      try {
        const data = JSON.parse(e.data);
        this.routeEvent(data);
      } catch (err) {
        console.error(`[${this.opts.agentId}] SSE 解析失败:`, err);
      }
    };

    this.sse.onerror = () => {
      if (this.stopping) return;
      console.warn(`[${this.opts.agentId}] SSE 断线，${this.opts.reconnectDelay}ms 后重连...`);
      this.sse?.close();
      this.sse = null;
      setTimeout(() => {
        if (!this.stopping) this.connectSSE();
      }, this.opts.reconnectDelay);
    };
  }

  // ── 事件路由 ─────────────────────────────────────────
  private async routeEvent(data: any): Promise<void> {
    switch (data.event) {
      case "task_assigned":
        this.emit("task_assigned", data.task);
        await this.opts.onTaskAssigned?.(data.task);
        break;

      case "new_message":
        this.emit("new_message", data.message);
        await this.opts.onMessage?.(data.message);
        break;

      case "task_updated":
        this.emit("task_updated", data.update);
        await this.opts.onTaskUpdated?.(data.update);
        break;

      case "pending_messages":
        for (const msg of data.messages ?? []) {
          this.emit("new_message", msg);
          await this.opts.onMessage?.(msg);
        }
        break;
    }
  }

  // ── MCP 工具调用封装 ─────────────────────────────────
  private async callTool(toolName: string, args: Record<string, unknown>): Promise<any> {
    // 每次调用前确保握手完成
    await this.ensureInitialized();
    return this._callTool(toolName, args);
  }

  private async _callTool(toolName: string, args: Record<string, unknown>): Promise<any> {
    const { body } = await this.postMcp(
      {
        jsonrpc: "2.0",
        id:      crypto.randomUUID(),
        method:  "tools/call",
        params:  { name: toolName, arguments: args },
      },
      this.opts.mcpTimeout!
    );

    // 错误处理
    if (body.error) {
      const errMsg = body.error.message ?? JSON.stringify(body.error);
      throw new Error(`MCP tool error [${toolName}]: ${errMsg}`);
    }

    // 从标准 MCP 响应中提取结果
    const text = body?.result?.content?.[0]?.text ?? body?.result;
    if (typeof text === "string") {
      try { return JSON.parse(text); } catch { return text; }
    }
    return body;
  }

  // ── 对外 API ─────────────────────────────────────────

  /** 发送消息给另一个 Agent */
  async sendMessage(to: string, content: string, metadata?: Record<string, unknown>) {
    return this.callTool("send_message", {
      from: this.opts.agentId, to, content, type: "message", metadata,
    });
  }

  /** 分配任务给另一个 Agent */
  async assignTask(to: string, description: string, context?: string, priority?: string) {
    return this.callTool("assign_task", {
      from: this.opts.agentId, to, description, context,
      priority: priority ?? "normal",
    });
  }

  /** 汇报任务进度 */
  async updateTaskStatus(
    taskId: string,
    status: "in_progress" | "completed" | "failed",
    result?: string,
    progress?: number
  ) {
    return this.callTool("update_task_status", {
      task_id: taskId, agent_id: this.opts.agentId, status, result, progress: progress ?? 0,
    });
  }

  /** 查询任务状态 */
  async getTaskStatus(taskId: string) {
    return this.callTool("get_task_status", { task_id: taskId });
  }

  /** 查询在线 Agent */
  async getOnlineAgents(): Promise<string[]> {
    const result = await this.callTool("get_online_agents", {});
    return result?.online_agents ?? [];
  }

  /** 广播消息 */
  async broadcast(agentIds: string[], content: string, metadata?: Record<string, unknown>) {
    return this.callTool("broadcast_message", {
      from: this.opts.agentId, agent_ids: agentIds, content, metadata,
    });
  }

  // ═══════════════════════════════════════════════════════
  // Evolution Engine — 经验共享 + 策略传播
  // ═══════════════════════════════════════════════════════

  /** 分享经验（直接 approved，无需审批） */
  async shareExperience(title: string, content: string, tags?: string[], taskId?: string) {
    const args: Record<string, unknown> = { title, content };
    if (tags) args.tags = tags;
    if (taskId) args.task_id = taskId;
    return this.callTool("share_experience", args);
  }

  /** 提议策略（需 admin 审批） */
  async proposeStrategy(
    title: string, content: string,
    category: "workflow" | "fix" | "tool_config" | "prompt_template" | "other" = "workflow",
    taskId?: string,
  ) {
    const args: Record<string, unknown> = { title, content, category };
    if (taskId) args.task_id = taskId;
    return this.callTool("propose_strategy", args);
  }

  /** 查询策略列表 */
  async listStrategies(
    opts?: { status?: string; category?: string; proposerId?: string; limit?: number },
  ) {
    const args: Record<string, unknown> = {};
    if (opts?.status) args.status = opts.status;
    if (opts?.category) args.category = opts.category;
    if (opts?.proposerId) args.proposer_id = opts.proposerId;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("list_strategies", args);
  }

  /** FTS5 全文搜索策略 */
  async searchStrategies(query: string, opts?: { category?: string; limit?: number }) {
    const args: Record<string, unknown> = { query };
    if (opts?.category) args.category = opts.category;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("search_strategies", args);
  }

  /** 采纳策略 */
  async applyStrategy(strategyId: number, context?: string) {
    const args: Record<string, unknown> = { strategy_id: strategyId };
    if (context) args.context = context;
    return this.callTool("apply_strategy", args);
  }

  /** 对策略反馈（每 Agent 每策略一次） */
  async feedbackStrategy(
    strategyId: number,
    feedback: "positive" | "negative" | "neutral",
    opts?: { comment?: string; applied?: boolean },
  ) {
    const args: Record<string, unknown> = { strategy_id: strategyId, feedback };
    if (opts?.comment) args.comment = opts.comment;
    if (opts?.applied !== undefined) args.applied = opts.applied;
    return this.callTool("feedback_strategy", args);
  }

  /** 审批策略（admin only） */
  async approveStrategy(strategyId: number, action: "approve" | "reject", reason: string) {
    return this.callTool("approve_strategy", {
      strategy_id: strategyId, action, reason,
    });
  }

  /** 查看进化指标统计 */
  async getEvolutionStatus() {
    return this.callTool("get_evolution_status", {});
  }

  // ═══════════════════════════════════════════════════════
  // 记忆模块 — Memory Service
  // ═══════════════════════════════════════════════════════

  /**
   * 存储一条记忆
   * @param content 记忆正文
   * @param opts 可选字段：title / scope / tags / sourceTaskId
   * @returns { memoryId: string }
   */
  async storeMemory(
    content: string,
    opts?: {
      title?: string;
      scope?: "private" | "group" | "collective";
      tags?: string[];
      sourceTaskId?: string;
    },
  ) {
    const args: Record<string, unknown> = { content };
    if (opts?.title) args.title = opts.title;
    if (opts?.scope) args.scope = opts.scope;
    if (opts?.tags) args.tags = opts.tags;
    if (opts?.sourceTaskId) args.source_task_id = opts.sourceTaskId;
    return this.callTool("store_memory", args);
  }

  /**
   * 语义搜索记忆（模糊查询）
   * @param query 搜索关键词
   * @param opts 可选字段：scope / limit
   * @returns 匹配的记忆列表
   */
  async recallMemory(query: string, opts?: { scope?: string; limit?: number }) {
    const args: Record<string, unknown> = { query };
    if (opts?.scope) args.scope = opts.scope;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("recall_memory", args);
  }

  /**
   * 列出记忆（分页）
   * @param opts 可选字段：scope / limit / offset
   * @returns 记忆列表
   */
  async listMemories(opts?: { scope?: string; limit?: number; offset?: number }) {
    const args: Record<string, unknown> = {};
    if (opts?.scope) args.scope = opts.scope;
    if (opts?.limit) args.limit = opts.limit;
    if (opts?.offset) args.offset = opts.offset;
    return this.callTool("list_memories", args);
  }

  /**
   * 删除指定记忆
   * @param memoryId 记忆 ID
   * @returns 删除结果
   */
  async deleteMemory(memoryId: string) {
    return this.callTool("delete_memory", { memory_id: memoryId });
  }

  // ═══════════════════════════════════════════════════════
  // 任务模块补充 — Task Extensions
  // ═══════════════════════════════════════════════════════

  /**
   * 通过 REST API 查询任务列表（支持过滤）
   * @param status 状态过滤（如 "in_progress"）
   * @returns 任务列表
   */
  async getTasks(status?: string) {
    const url = new URL(`${this.opts.hubUrl}/api/tasks`);
    if (status) url.searchParams.set("status", status);

    const res = await fetch(url.toString(), {
      headers: { Authorization: `Bearer ${this._apiToken}` },
    });
    if (!res.ok) throw new Error(`getTasks failed: ${res.status} ${res.statusText}`);
    return res.json();
  }

  /**
   * 取消一个进行中的任务（MCP callTool）
   * @param taskId 任务 ID
   * @returns 取消结果
   */
  async cancelTask(taskId: string) {
    return this.callTool("cancel_task", { task_id: taskId });
  }

  // ═══════════════════════════════════════════════════════
  // 依赖链 + 并行组 — Dependency Chain & Parallel Groups
  // ═══════════════════════════════════════════════════════

  /**
   * 添加任务依赖关系
   * @param upstreamId 上游任务 ID
   * @param downstreamId 下游任务 ID
   * @param depType 依赖类型，默认 "finish_to_start"
   * @returns 添加结果
   */
  async addDependency(
    upstreamId: string,
    downstreamId: string,
    depType?: string,
  ) {
    return this.callTool("add_dependency", {
      upstream_task_id: upstreamId,
      downstream_task_id: downstreamId,
      dependency_type: depType ?? "finish_to_start",
    });
  }

  /**
   * 移除任务依赖关系
   * @param upstreamId 上游任务 ID
   * @param downstreamId 下游任务 ID
   * @returns 移除结果
   */
  async removeDependency(upstreamId: string, downstreamId: string) {
    return this.callTool("remove_dependency", {
      upstream_task_id: upstreamId,
      downstream_task_id: downstreamId,
    });
  }

  /**
   * 查询指定任务的所有依赖关系
   * @param taskId 任务 ID
   * @returns 依赖关系列表
   */
  async getTaskDependencies(taskId: string) {
    return this.callTool("get_task_dependencies", { task_id: taskId });
  }

  /**
   * 检查指定任务的所有上游依赖是否已满足（全部完成）
   * @param taskId 任务 ID
   * @returns { satisfied: boolean; missing: string[] }
   */
  async checkDependenciesSatisfied(taskId: string) {
    return this.callTool("check_dependencies_satisfied", { task_id: taskId });
  }

  /**
   * 创建并行组（组内任务可同时执行）
   * @param taskIds 任务 ID 列表
   * @param groupName 可选的组名称
   * @returns { groupId: string }
   */
  async createParallelGroup(taskIds: string[], groupName?: string) {
    const args: Record<string, unknown> = { task_ids: taskIds };
    if (groupName) args.group_name = groupName;
    return this.callTool("create_parallel_group", args);
  }

  // ═══════════════════════════════════════════════════════
  // 交接协议 — Handoff Protocol
  // ═══════════════════════════════════════════════════════

  /**
   * 请求任务交接给另一个 Agent
   * @param taskId 任务 ID
   * @param targetAgentId 目标 Agent ID
   * @returns 交接请求结果
   */
  async requestHandoff(taskId: string, targetAgentId: string) {
    return this.callTool("request_handoff", {
      task_id: taskId,
      target_agent_id: targetAgentId,
    });
  }

  /**
   * 接受任务交接
   * @param taskId 任务 ID
   * @returns 接受结果
   */
  async acceptHandoff(taskId: string) {
    return this.callTool("accept_handoff", { task_id: taskId });
  }

  /**
   * 拒绝任务交接
   * @param taskId 任务 ID
   * @param reason 拒绝原因
   * @returns 拒绝结果
   */
  async rejectHandoff(taskId: string, reason?: string) {
    const args: Record<string, unknown> = { task_id: taskId };
    if (reason) args.reason = reason;
    return this.callTool("reject_handoff", args);
  }

  // ═══════════════════════════════════════════════════════
  // 质量门 — Quality Gates
  // ═══════════════════════════════════════════════════════

  /**
   * 为 Pipeline 添加质量门
   * @param pipelineId Pipeline ID
   * @param gateName 质量门名称
   * @param criteria 通过标准（SQL WHERE 条件或描述文本）
   * @param afterOrder 在哪个步骤之后插入
   * @returns 添加结果
   */
  async addQualityGate(
    pipelineId: string,
    gateName: string,
    criteria: string,
    afterOrder: number,
  ) {
    return this.callTool("add_quality_gate", {
      pipeline_id: pipelineId,
      gate_name: gateName,
      criteria,
      after_order: afterOrder,
    });
  }

  /**
   * 评估质量门结果
   * @param gateId 质量门 ID
   * @param status 评估结果 "passed" | "failed"
   * @param result 可选的详细结果描述
   * @returns 评估结果
   */
  async evaluateQualityGate(
    gateId: string,
    status: "passed" | "failed",
    result?: string,
  ) {
    const args: Record<string, unknown> = { gate_id: gateId, status };
    if (result) args.result = result;
    return this.callTool("evaluate_quality_gate", args);
  }

  // ═══════════════════════════════════════════════════════
  // 分级审批 — Tiered Strategy Approval
  // ═══════════════════════════════════════════════════════

  /**
   * 提议策略（支持分级审批，自动根据策略内容判断 tier）
   * @param title 策略标题
   * @param content 策略正文
   * @param opts 可选：category / taskId
   * @returns 策略提案结果
   */
  async proposeStrategyTiered(
    title: string,
    content: string,
    opts?: { category?: string; taskId?: string },
  ) {
    const args: Record<string, unknown> = { title, content };
    if (opts?.category) args.category = opts.category;
    if (opts?.taskId) args.task_id = opts.taskId;
    return this.callTool("propose_strategy_tiered", args);
  }

  /**
   * 检查策略是否处于 veto 窗口期（可行使否决权的时间窗口）
   * @param strategyId 策略 ID
   * @returns { in_window: boolean; remaining_seconds?: number }
   */
  async checkVetoWindow(strategyId: number) {
    return this.callTool("check_veto_window", { strategy_id: strategyId });
  }

  /**
   * 对策略行使否决权（需在 veto 窗口期内）
   * @param strategyId 策略 ID
   * @param reason 否决理由
   * @returns 否决结果
   */
  async vetoStrategy(strategyId: number, reason: string) {
    return this.callTool("veto_strategy", {
      strategy_id: strategyId,
      reason,
    });
  }

  // ═══════════════════════════════════════════════════════
  // Phase 5a Security — RBAC + Trust Score
  // ═══════════════════════════════════════════════════════

  /**
   * 设置 Agent 角色（admin only）
   * @param agentId Agent ID
   * @param role 新角色，如 "admin" / "member"
   * @param managedGroupId 可选：管理的组 ID
   * @returns 设置结果
   */
  async setAgentRole(agentId: string, role: string, managedGroupId?: string) {
    const args: Record<string, unknown> = { agent_id: agentId, role };
    if (managedGroupId) args.managed_group_id = managedGroupId;
    return this.callTool("set_agent_role", args);
  }

  /**
   * 重新计算 Agent 信任评分（admin only）
   * @param agentId 可选，不传则重算所有 Agent
   * @returns 重算结果
   */
  async recalculateTrustScores(agentId?: string) {
    const args: Record<string, unknown> = {};
    if (agentId) args.agent_id = agentId;
    return this.callTool("recalculate_trust_scores", args);
  }

  // ═══════════════════════════════════════════════════════
  // Token 管理 — Token Management
  // ═══════════════════════════════════════════════════════

  /** 设置 REST API 认证 token（register_agent 返回后调用） */
  setToken(token: string): void {
    this._apiToken = token;
  }

  /** 撤销 Agent 的 API token（admin only） */
  async revokeToken(agentId: string) {
    return this.callTool("revoke_token", { agent_id: agentId });
  }

  /** 设置 Agent 信任评分（admin only） */
  async setTrustScore(agentId: string, score: number) {
    return this.callTool("set_trust_score", {
      agent_id: agentId,
      trust_score: score,
    });
  }

  // ═══════════════════════════════════════════════════════
  // 记忆搜索 — Memory Search (Phase 6)
  // ═══════════════════════════════════════════════════════

  /**
   * 全文搜索记忆（FTS5）
   * @param query 搜索关键词
   * @param opts 可选：scope / limit
   * @returns 匹配的记忆列表
   */
  async searchMemories(
    query: string,
    opts?: { scope?: string; limit?: number },
  ) {
    const args: Record<string, unknown> = { query };
    if (opts?.scope) args.scope = opts.scope;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("search_memories", args);
  }

  // ═══════════════════════════════════════════════════════
  // Pipeline 管理 — Pipeline Management (Phase 6)
  // ═══════════════════════════════════════════════════════

  /**
   * 创建 Pipeline（线性任务容器）
   * @param name Pipeline 名称
   * @param description 可选描述
   * @returns { pipelineId: string }
   */
  async createPipeline(name: string, description?: string) {
    const args: Record<string, unknown> = { name };
    if (description) args.description = description;
    return this.callTool("create_pipeline", args);
  }

  /**
   * 获取 Pipeline 详情（含任务列表和依赖关系）
   * @param pipelineId Pipeline ID
   * @returns Pipeline 详情
   */
  async getPipeline(pipelineId: string) {
    return this.callTool("get_pipeline", { pipeline_id: pipelineId });
  }

  /**
   * 列出所有 Pipeline
   * @param opts 可选：status / limit
   * @returns Pipeline 列表
   */
  async listPipelines(opts?: { status?: string; limit?: number }) {
    const args: Record<string, unknown> = {};
    if (opts?.status) args.status = opts.status;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("list_pipelines", args);
  }

  /**
   * 向 Pipeline 添加任务
   * @param pipelineId Pipeline ID
   * @param description 任务描述
   * @param opts 可选：assignedTo / order / dependsOn
   * @returns 添加结果
   */
  async addTaskToPipeline(
    pipelineId: string,
    description: string,
    opts?: {
      assignedTo?: string;
      order?: number;
      dependsOn?: string;
    },
  ) {
    const args: Record<string, unknown> = {
      pipeline_id: pipelineId,
      description,
    };
    if (opts?.assignedTo) args.assigned_to = opts.assignedTo;
    if (opts?.order !== undefined) args.order = opts.order;
    if (opts?.dependsOn) args.depends_on = opts.dependsOn;
    return this.callTool("add_task_to_pipeline", args);
  }

  // ═══════════════════════════════════════════════════════
  // 消息搜索 — Message Search (Phase 6)
  // ═══════════════════════════════════════════════════════

  /**
   * 全文搜索消息历史（FTS5）
   * @param query 搜索关键词
   * @param opts 可选：agentId（限定发送方）/ limit
   * @returns 匹配的消息列表
   */
  async searchMessages(
    query: string,
    opts?: { agentId?: string; limit?: number },
  ) {
    const args: Record<string, unknown> = { query };
    if (opts?.agentId) args.agent_id = opts.agentId;
    if (opts?.limit) args.limit = opts.limit;
    return this.callTool("search_messages", args);
  }
}
