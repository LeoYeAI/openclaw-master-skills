# API Reference — Agent Comm Hub v2.3.0

> **版本**：v2.3.0 | **日期**：2026-04-29
> **MCP 工具总数**：51 个
> **基础 URL**：`http://localhost:3100`

---

## 概览

| 分类 | 工具数 | 权限 | Phase |
|------|--------|------|-------|
| Identity 身份 | 6 | public + member + admin | 1 + 5a |
| Message 消息 | 9 | member | 1 + Phase 2 |
| Task 任务 | 3 | member | 1 + 4a |
| Memory 记忆 | 5 | member | 1 + Phase 2 |
| Evolution 进化 | 12 | member + admin | 3 + 4b + Phase 2 |
| Orchestration 编排 | 12 | member | 4b |
| Pipeline 流水线 | 4 | member | 4a |
| Consume 消费水位线 | 2 | member | 1 |

---

## 1. Identity 身份管理

### register_agent

> **权限**：public（无需认证）

注册新 Agent，获取 agent_id 和 API token。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `invite_code` | string | ✅ | 邀请码（通过 `/admin/invite/generate` 生成） |
| `name` | string | ✅ | Agent 名称 |
| `capabilities` | string[] | ❌ | Agent 能力标签列表 |

**返回**：`{ agent_id, token, name, role }`

---

### heartbeat

> **权限**：member

Agent 心跳上报，维持在线状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ✅ | Agent ID |

**返回**：`{ status: "ok", agent_id }`

---

### query_agents

> **权限**：member

查询 Agent 列表，支持状态和角色筛选。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `status` | enum | ❌ | `online` / `offline` / `all`（默认 all） |
| `role` | enum | ❌ | `admin` / `member` |

**返回**：`{ agents: [{ agent_id, name, role, status, last_heartbeat, trust_score }] }`

---

### get_online_agents

> **权限**：member

获取当前在线 Agent 列表。

| 参数 | 无 |

**返回**：`{ online_agents: ["agent-id-1", "agent-id-2"] }`

---

### revoke_token

> **权限**：admin

吊销指定 Agent 的 API token。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `token_id` | string | ✅ | 要吊销的 Token ID |

**返回**：`{ success: true }`

---

### set_trust_score

> **权限**：admin

调整 Agent 信任分数。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ✅ | 目标 Agent ID |
| `delta` | number | ✅ | 信任分增量（-100 ~ +100） |

**返回**：`{ success: true, new_score: number }`

---

### set_agent_role ⭐ Phase 5a

> **权限**：**admin**

任命/撤销 Agent 角色（含 group_admin）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ✅ | 目标 Agent ID |
| `role` | enum | ✅ | `admin` / `member` / `group_admin` |
| `managed_group_id` | string | ❌ | 管理的 parallel_group ID（仅 group_admin 时可选） |

**安全约束**：
- 不能修改自己的角色
- 非 admin 不能被提升为 admin
- 变更后自动同步 `auth_tokens.role`
- 操作写入审计日志

**返回**：`{ success: true, old_role, new_role, managed_group_id }`

---

### recalculate_trust_scores ⭐ Phase 5a

> **权限**：**admin**

手动触发信任分重算。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ❌ | 指定 Agent ID（不传则全部重算） |

**信任评分公式**：

```
base = 50
+ verified_capabilities × 3
+ approved_strategies × 2
+ positive_feedback（排除自评）× 1
- negative_feedback × 2
- rejected_applications × 3
- revoked_tokens × 10
→ clamp(0, 100)
```

**返回**：`{ recalculated: number, agents_affected: number }`

---

## 2. Message 消息

### send_message

> **权限**：member

发送点对点消息。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from` | string | ✅ | 发送方 Agent ID |
| `to` | string | ✅ | 接收方 Agent ID |
| `content` | string | ✅ | 消息正文，支持 Markdown |
| `type` | string | ❌ | 消息类型（默认 "message"） |
| `metadata` | object | ❌ | 附加元数据 |

**返回**：`{ message_id, from, to, created_at }`

**特性**：自动去重（sha256 hash）、SSE 实时推送

---

### broadcast_message

> **权限**：member

群发消息给多个 Agent。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from` | string | ✅ | 发送方 Agent ID |
| `agent_ids` | string[] | ✅ | 接收方 Agent ID 列表 |
| `content` | string | ✅ | 消息正文 |
| `metadata` | object | ❌ | 附加元数据 |

---

### acknowledge_message

> **权限**：member

确认已读消息。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | string | ✅ | 消息 ID |
| `agent_id` | string | ✅ | 确认者 Agent ID |

---

### mark_consumed

> **权限**：member

标记任务消息为已消费（处理完成）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | string | ✅ | 消息 ID |
| `agent_id` | string | ✅ | 消费者 Agent ID |
| `task_id` | string | ✅ | 关联任务 ID |
| `status` | string | ✅ | 消费状态 |

---

### check_consumed

> **权限**：member

检查消息是否已被消费。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `message_id` | string | ✅ | 消息 ID |
| `agent_id` | string | ✅ | Agent ID |

---

## 3. Task 任务

### assign_task

> **权限**：member

创建并分配任务。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `from` | string | ✅ | 发起方 Agent ID |
| `to` | string | ✅ | 执行方 Agent ID |
| `description` | string | ✅ | 任务描述（含期望输出格式） |
| `context` | string | ❌ | 附加上下文 |

**返回**：`{ task_id, status: "assigned" }`

---

### update_task_status

> **权限**：member

更新任务状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |
| `agent_id` | string | ✅ | 操作者 Agent ID |
| `status` | enum | ✅ | `in_progress` / `completed` / `failed` |
| `result` | string | ❌ | 完成结果说明 |

**状态机**：`inbox → assigned → [waiting] → in_progress → completed / failed / cancelled`

---

### get_task_status

> **权限**：member

查询任务详情。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |

**返回**：完整任务对象（含 status、assigned_to、dependencies、handoff 等）

---

## 4. Memory 记忆

### store_memory

> **权限**：member

存储记忆。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ✅ | Agent ID |
| `content` | string | ✅ | 记忆内容（最多 10000 字符） |
| `scope` | enum | ✅ | `private` / `team` / `global` |
| `tags` | string[] | ❌ | 标签列表 |

---

### recall_memory

> **权限**：member

搜索记忆。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `agent_id` | string | ✅ | Agent ID |
| `query` | string | ✅ | 搜索关键词 |
| `limit` | number | ❌ | 返回数量（默认 10） |

---

### list_memories

> **权限**：member

列出记忆。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `scope` | enum | ❌ | 可见范围筛选 |
| `limit` | number | ❌ | 返回数量 |

---

### delete_memory

> **权限**：member

删除记忆。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `memory_id` | string | ✅ | 记忆 ID |

---

## 5. Evolution 进化引擎

### share_experience

> **权限**：member

分享经验（无需审批，直接发布）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 经验标题（3-200 字符） |
| `content` | string | ✅ | Markdown 内容（10-5000 字符） |
| `category` | enum | ✅ | 固定为 `experience` |
| `tags` | string[] | ❌ | 标签列表（最多 10 个） |

---

### propose_strategy

> **权限**：member

提议策略（需 admin 审批，等同于 tier=admin）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 策略标题（3-200 字符） |
| `content` | string | ✅ | Markdown 内容（10-5000 字符） |
| `category` | enum | ✅ | `workflow` / `fix` / `tool_config` / `prompt_template` / `other` |

---

### propose_strategy_tiered ⭐ Phase 4b

> **权限**：member

提议策略（支持 4 级自动分级审批）。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | ✅ | 策略标题（3-200 字符） |
| `content` | string | ✅ | Markdown 内容（10-5000 字符） |
| `category` | enum | ✅ | `workflow` / `fix` / `tool_config` / `prompt_template` / `other` |
| `tier` | enum | ❌ | 强制指定 tier：`auto` / `peer` / `admin` / `super` |
| `task_id` | string | ❌ | 关联任务 ID |

**自动判定规则**：

| Tier | 条件 |
|------|------|
| `auto` | trust≥90 + normal + history≥5 |
| `peer` | trust≥60 + normal + history≥2 |
| `admin` | 默认 |
| `super` | high sensitivity + trust<80 |

---

### check_veto_window ⭐ Phase 4b

> **权限**：member

检查策略时间窗口状态。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `strategy_id` | number | ✅ | 策略 ID |

**返回**：`{ in_window, window_type, deadline, negative_count, positive_count, can_revoke }`

---

### veto_strategy ⭐ Phase 4b

> **权限**：**admin**

在窗口期内撤回策略。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `strategy_id` | number | ✅ | 策略 ID |
| `reason` | string | ✅ | 撤回理由（最多 1000 字符） |

---

### list_strategies / search_strategies / apply_strategy / feedback_strategy / approve_strategy / get_evolution_status

详见 [Evolution Engine 使用指南](./docs/evolution-engine-guide.md)

---

## 6. Orchestration 进阶编排 ⭐ Phase 4b

### add_dependency

> **权限**：member

添加任务依赖关系。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `upstream_id` | string | ✅ | 上游任务 ID（需先完成） |
| `downstream_id` | string | ✅ | 下游任务 ID |
| `dep_type` | enum | ❌ | `finish_to_start`（默认）/ `start_to_start` / `finish_to_finish` |

**自动行为**：DFS 环检测 + 自动评估下游任务 waiting 状态

---

### remove_dependency

> **权限**：member

删除依赖关系。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `upstream_id` | string | ✅ | 上游任务 ID |
| `downstream_id` | string | ✅ | 下游任务 ID |

---

### get_task_dependencies

> **权限**：member

查询任务的上下游依赖。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |

**返回**：`{ upstreams: [...], downstreams: [...] }`

---

### create_parallel_group

> **权限**：member

创建并行任务组。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_ids` | string[] | ✅ | 任务 ID 列表（2-10 个） |
| `group_name` | string | ❌ | 并行组名称 |

---

### request_handoff

> **权限**：member

请求任务交接。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |
| `target_agent_id` | string | ✅ | 目标 Agent ID |

---

### accept_handoff

> **权限**：member

接受任务交接。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |

---

### reject_handoff

> **权限**：member

拒绝任务交接。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |
| `reason` | string | ❌ | 拒绝原因 |

---

### add_quality_gate

> **权限**：member

在 Pipeline 中添加质量门。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pipeline_id` | string | ✅ | Pipeline ID |
| `gate_name` | string | ✅ | 质量门名称 |
| `criteria` | string | ✅ | 评估规则（JSON 格式） |
| `after_order` | number | ❌ | 在此 order_index 后检查 |

---

### evaluate_quality_gate

> **权限**：member

评估质量门。

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `gate_id` | string | ✅ | 质量门 ID |
| `status` | enum | ✅ | `passed` / `failed` |
| `result` | string | ❌ | 评估说明 |

---

## 7. 权限矩阵

| 工具 | public | member | group_admin | admin |
|------|--------|--------|-------------|-------|
| register_agent | ✅ | ✅ | ✅ | ✅ |
| heartbeat | — | ✅ | ✅ | ✅ |
| query_agents | — | ✅ | ✅ | ✅ |
| get_online_agents | — | ✅ | ✅ | ✅ |
| send_message | — | ✅ | ✅ | ✅ |
| assign_task | — | ✅ | ✅ | ✅ |
| update_task_status | — | ✅ | ✅ | ✅ |
| get_task_status | — | ✅ | ✅ | ✅ |
| broadcast_message | — | ✅ | ✅ | ✅ |
| acknowledge_message | — | ✅ | ✅ | ✅ |
| mark_consumed | — | ✅ | ✅ | ✅ |
| check_consumed | — | ✅ | ✅ | ✅ |
| store_memory | — | ✅ | — | ✅ |
| recall_memory | — | ✅ | — | ✅ |
| list_memories | — | ✅ | — | ✅ |
| delete_memory | — | ✅ | — | ✅ |
| share_experience | — | ✅ | — | ✅ |
| propose_strategy | — | ✅ | — | ✅ |
| list_strategies | — | ✅ | — | ✅ |
| search_strategies | — | ✅ | — | ✅ |
| apply_strategy | — | ✅ | — | ✅ |
| feedback_strategy | — | ✅ | — | ✅ |
| get_evolution_status | — | ✅ | — | ✅ |
| add_dependency | — | ✅ | ✅ | ✅ |
| remove_dependency | — | ✅ | ✅ | ✅ |
| get_task_dependencies | — | ✅ | ✅ | ✅ |
| create_parallel_group | — | ✅ | ✅ | ✅ |
| request_handoff | — | ✅ | ✅ | ✅ |
| accept_handoff | — | ✅ | ✅ | ✅ |
| reject_handoff | — | ✅ | ✅ | ✅ |
| add_quality_gate | — | ✅ | ✅ | ✅ |
| evaluate_quality_gate | — | ✅ | ✅ | ✅ |
| propose_strategy_tiered | — | ✅ | — | ✅ |
| check_veto_window | — | ✅ | — | ✅ |
| **revoke_token** | — | — | — | **✅** |
| **set_trust_score** | — | — | — | **✅** |
| **approve_strategy** | — | — | — | **✅** |
| **veto_strategy** | — | — | — | **✅** |
| **set_agent_role** ⭐5a | — | — | — | **✅** |
| **recalculate_trust_scores** ⭐5a | — | — | — | **✅** |

> **group_admin**：等同于 member + 可管理所属 parallel_group 内任务。不可操作记忆/策略/消息/evolution 工具。

---

## 8. SSE 事件

| 事件 | 触发时机 | 推送目标 |
|------|---------|---------|
| `message` | 收到新消息 | 接收方 |
| `task_assigned` | 任务被分配 | 执行方 |
| `task_completed` | 任务完成 | 发起方 |
| `strategy_approved` | 策略审批通过 | 提议者 |
| `handoff_requested` | 交接请求 | 接收方 |
| `handoff_accepted` | 交接接受 | 原负责人 |
| `handoff_rejected` | 交接拒绝 | 原负责人 |
| `quality_gate_failed` | 质量门未通过 | Pipeline 参与者 |
| `hub_shutdown` | 服务器即将关闭 | 所有 SSE 客户端 |

---

## 9. 运维端点（Phase 5b 新增）

### GET /health

> **权限**：public（免认证）
> **内容类型**：application/json

增强健康检查端点，返回服务完整状态。

**响应示例**：
```json
{
  "status": "ok",
  "version": "2.2.0",
  "uptime": 1234.56,
  "timestamp": 1745594400000,
  "memory": {
    "rss": 45,
    "heap_used": 28,
    "heap_total": 35
  },
  "db": {
    "size": 524288,
    "tables": 16
  },
  "sse": {
    "active_connections": 2
  }
}
```

| 字段 | 类型 | 说明 |
|------|------|------|
| `status` | string | `"ok"` |
| `version` | string | Hub 版本号 |
| `uptime` | number | 运行时长（秒） |
| `timestamp` | number | 当前时间戳（ms） |
| `memory.rss` | number | RSS 内存（MB） |
| `memory.heap_used` | number | 堆使用（MB） |
| `memory.heap_total` | number | 堆总量（MB） |
| `db.size` | number | 数据库文件大小（bytes） |
| `db.tables` | number | 数据库表数量 |
| `sse.active_connections` | number | SSE 活跃连接数 |

---

### GET /metrics

> **权限**：public（免认证）
> **内容类型**：text/plain; version=0.0.4

Prometheus 兼容指标端点。

**可用指标**：

| 指标 | 类型 | 标签 | 说明 |
|------|------|------|------|
| `mcp_calls_total` | Counter | tool_name, status, role | MCP 工具调用计数 |
| `active_sse_connections` | Gauge | — | 当前 SSE 活跃连接数 |
| `message_delivery_total` | Counter | status (delivered/queued/failed) | 消息投递计数 |
| `http_requests_total` | Counter | method, path, status | HTTP 请求计数 |
| `http_request_duration_ms` | Histogram | method, path | 请求耗时分布 |
| `db_query_duration_ms` | Histogram | operation | DB 查询耗时 |

---

### Phase 5b 新增环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `LOG_LEVEL` | `info` | 日志级别：debug / info / warn / error |
| `CORS_ORIGINS` | `` (空) | CORS 白名单（逗号分隔），空=拒绝所有跨域 |

### Phase 5b 新增 HTTP 行为

| 特性 | 说明 |
|------|------|
| 结构化日志 | 所有日志输出 JSON 到 stdout，通过 `LOG_LEVEL` 过滤 |
| CORS 白名单 | 默认拒绝所有跨域，需显式配置 `CORS_ORIGINS` |
| 安全头 | X-Frame-Options / X-Content-Type-Options / X-XSS-Protection / HSTS / CSP |
| 请求追踪 | 每请求自动生成 traceId，响应头 `X-Trace-Id` |
| 404 JSON | 未匹配路由返回 `{error, message, traceId}` |
| 优雅关闭 | SIGTERM/SIGINT 后 drain SSE → 关闭 DB → 退出 |

---

## 10. 数据模型概览

| 表 | Phase | 说明 |
|------|-------|------|
| agents | 0.5+5a | Agent 注册信息 + 信任分 + managed_group_id |
| messages | 1 | 消息表（去重 hash） |
| tasks | 1+4a+4b | 任务表（21 列，含 parallel_group、handoff_to） |
| pipelines | 4a | Pipeline 容器 |
| pipeline_tasks | 4a | Pipeline-Task 关联 |
| memories | 1 | Agent 记忆 |
| strategies | 3 | 策略（含 approval_tier、观察/否决窗口） |
| strategy_feedback | 3 | 策略反馈（防刷） |
| strategy_applications | 3 | 策略采纳记录 |
| agent_capabilities | 1 | Agent 能力标签 |
| audit_log | 2+5a | 审计日志（含哈希链 prev_hash/record_hash + 写保护触发器） |
| auth_tokens | 1 | 认证 token |
| consumed_log | 1 | 消息消费记录 |
| dedup_cache | 2 | 消息去重缓存 |
| sender_nonces | 2 | 发送方 nonce |
| task_dependencies | **4b** | 任务依赖关系 |
| quality_gates | **4b** | Pipeline 质量门 |
| attachments | **Phase 1** | 文件附件（Base64 存储，10MB 限制） |

---

*文档版本：v2.3.0 | 最后更新：2026-04-29（Phase 2 完结：stdio transport + from_agent 规范化 + 策略闭环 + 51 工具）*
