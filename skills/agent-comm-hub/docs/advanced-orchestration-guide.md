# 进阶编排使用指南

> **版本**：v1.0 | **日期**：2026-04-25
> **所属**：Agent Synergy Framework Phase 4b
> **Hub 版本**：v2.0.0+（含 Task Orchestrator 进阶能力）

---

## 概述

Phase 4b 在 Phase 4a 线性 Pipeline 基础上，引入了四种进阶编排能力：

| 能力 | 解决的问题 | 核心工具 |
|------|-----------|---------|
| **依赖链** | 任务有前后顺序（B 必须等 A 完成） | `add_dependency` / `remove_dependency` / `get_task_dependencies` |
| **并行组** | 多个任务可同时执行（A、B、C 互不依赖） | `create_parallel_group` |
| **质量门** | Pipeline 阶段检查点（代码 review 后才能继续） | `add_quality_gate` / `evaluate_quality_gate` |
| **交接协议** | 任务负责人变更（双向握手确认） | `request_handoff` / `accept_handoff` / `reject_handoff` |

---

## 1. 依赖链

### 1.1 概念

依赖链定义任务间的执行顺序。当任务 B 依赖任务 A 时：
- A 未完成 → B 处于 `waiting` 状态
- A 完成 → B 自动从 `waiting` 变为可执行
- 如果 A→B→C→A 形成环 → 自动拒绝（DFS 环检测）

### 1.2 依赖类型

| 类型 | 说明 | 触发时机 |
|------|------|---------|
| `finish_to_start` | 上游**完成后**下游可开始（默认） | 上游 status = completed |
| `start_to_start` | 上游**开始后**下游可开始 | 上游 status = in_progress |
| `finish_to_finish` | 上游**完成后**下游可完成 | 上游 status = completed |

### 1.3 使用示例

```json
// 1. 创建三个任务
{ "tool": "assign_task", "args": { "task_id": "design", "title": "UI设计", "assigned_to": "designer", "operator_id": "pm" } }
{ "tool": "assign_task", "args": { "task_id": "frontend", "title": "前端开发", "assigned_to": "dev1", "operator_id": "pm" } }
{ "tool": "assign_task", "args": { "task_id": "test", "title": "测试", "assigned_to": "qa", "operator_id": "pm" } }

// 2. 建立依赖：design → frontend → test
{ "tool": "add_dependency", "args": { "upstream_id": "design", "downstream_id": "frontend" } }
{ "tool": "add_dependency", "args": { "upstream_id": "frontend", "downstream_id": "test" } }

// 3. 此时 frontend 和 test 自动变为 waiting 状态
// 4. designer 完成 design → frontend 自动解除 waiting → dev1 可以开始
```

### 1.4 工具参数

#### add_dependency

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `upstream_id` | string | ✅ | 上游任务 ID（需先完成） |
| `downstream_id` | string | ✅ | 下游任务 ID（依赖上游完成后才能开始） |
| `dep_type` | enum | ❌ | 依赖类型，默认 `finish_to_start` |

**返回**：依赖创建结果 + 自动评估下游任务状态

**错误**：循环依赖 → `"Circular dependency detected"` / 任务不存在 → `"Task not found"`

#### get_task_dependencies

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 要查询的任务 ID |

**返回**：

```json
{
  "task_id": "frontend",
  "upstreams": [
    { "task_id": "design", "status": "completed", "dep_type": "finish_to_start", "dep_status": "satisfied" }
  ],
  "downstreams": [
    { "task_id": "test", "status": "waiting", "dep_type": "finish_to_start", "dep_status": "pending" }
  ]
}
```

### 1.5 状态机扩展

```
原始状态机：
inbox → assigned → in_progress → completed
                     ↓            ↓
                  cancelled    failed

Phase 4b 扩展：
inbox → assigned → waiting → in_progress → completed
                     ↓          ↓            ↓
                  cancelled  cancelled    failed
```

`waiting` 状态：任务有未满足的上游依赖，自动进入。所有上游依赖满足后自动解除。

---

## 2. 并行组

### 2.1 概念

并行组标记一组可以同时执行的任务。同一 `parallel_group` 内的任务互不依赖，可由不同 Agent 并行处理。

### 2.2 使用示例

```json
// 1. 创建多个独立任务
{ "tool": "assign_task", "args": { "task_id": "api-dev", "title": "API开发", "assigned_to": "backend-dev" } }
{ "tool": "assign_task", "args": { "task_id": "ui-dev", "title": "UI开发", "assigned_to": "frontend-dev" } }
{ "tool": "assign_task", "args": { "task_id": "doc-dev", "title": "文档编写", "assigned_to": "tech-writer" } }

// 2. 标记为并行组
{ "tool": "create_parallel_group", "args": {
    "task_ids": ["api-dev", "ui-dev", "doc-dev"],
    "group_name": "v2-parallel-sprint"
}}

// 3. 三个任务可以同时执行
// 4. 查看并行组信息（通过 get_task_status 或直接查询）
```

### 2.3 工具参数

#### create_parallel_group

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_ids` | string[] | ✅ | 并行任务 ID 列表（2-10 个） |
| `group_name` | string | ❌ | 并行组名称（便于识别） |

**约束**：最少 2 个，最多 10 个任务

### 2.4 与依赖链组合

并行组常与依赖链组合使用，形成 DAG 工作流：

```
[design] ──完成──→ [并行组: api-dev + ui-dev + doc-dev] ──全部完成──→ [integration-test]
                  ↑                  ↑                     ↑
            互不依赖，可并行       三个都完成后           最后集成
```

---

## 3. 质量门

### 3.1 概念

质量门是 Pipeline 阶段的检查点。只有通过质量门后，后续任务才能继续。适用于代码 review、测试验收等场景。

### 3.2 使用示例

```json
// 1. 创建质量门（代码 review）
{ "tool": "add_quality_gate", "args": {
    "pipeline_id": "release-pipeline",
    "gate_name": "code_review",
    "criteria": "{\"type\":\"all_completed\",\"threshold\":1}",
    "after_order": 3
}}

// 2. 前面 3 个任务完成后，QA 评估质量门
{ "tool": "evaluate_quality_gate", "args": {
    "gate_id": "<gate-id>",
    "agent_id": "senior-dev",
    "passed": true,
    "result": "代码质量良好，无重大问题"
}}

// 3. 如果 passed=false，后续任务被阻塞
// 4. 修复后重新评估
```

### 3.3 工具参数

#### add_quality_gate

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `pipeline_id` | string | ✅ | Pipeline ID |
| `gate_name` | string | ✅ | 阶段名称（2-100 字符） |
| `criteria` | string | ✅ | JSON 判定条件 |
| `after_order` | number | ❌ | 在 order_index > 此值的任务开始前检查 |

**criteria 格式**：

```json
// 方式1：所有前置任务完成
{ "type": "all_completed" }

// 方式2：最低成功率
{ "type": "min_success_rate", "threshold": 0.8 }

// 方式3：自定义检查表达式
{ "type": "custom", "check_expr": "test_coverage > 0.9" }
```

#### evaluate_quality_gate

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `gate_id` | string | ✅ | 质量门 ID |
| `agent_id` | string | ✅ | 评估者 Agent ID |
| `passed` | boolean | ✅ | 是否通过 |
| `result` | string | ❌ | 评估结果说明 |

### 3.4 质量门状态

```
pending → passed / failed
```

- `pending`：等待评估
- `passed`：门已通过，后续任务可继续
- `failed`：门未通过，后续任务被阻塞（需修复后重新评估）

### 3.5 SSE 事件

| 事件 | 触发时机 | 推送目标 |
|------|---------|---------|
| `quality_gate_passed` | 门通过 | Pipeline 参与者 |
| `quality_gate_failed` | 门未通过 | Pipeline 参与者 + 管理员 |

---

## 4. 交接协议

### 4.1 概念

交接协议是任务负责人的变更流程，采用双向握手模式：

```
发起方(A)                    接收方(B)
   |                            |
   |-- request_handoff -------->|
   |                            |
   |<-- accept_handoff ---------|  或  |-- reject_handoff -------->|
   |                            |          (任务仍归 A)
   |-- assigned_to 更新为 B -->|
```

### 4.2 使用示例

```json
// 1. A 请求交接
{ "tool": "request_handoff", "args": {
    "task_id": "bugfix-123",
    "from": "dev-a",
    "to": "dev-b",
    "reason": "需要前端专家处理",
    "context": "已完成初步排查，CSS 兼容性问题，需要 Chrome 特定调试"
}}

// 2. B 接受（任务转移）
{ "tool": "accept_handoff", "args": {
    "task_id": "bugfix-123",
    "agent_id": "dev-b"
}}

// 或者 B 拒绝（任务仍归 A）
{ "tool": "reject_handoff", "args": {
    "task_id": "bugfix-123",
    "agent_id": "dev-b",
    "reason": "当前排期已满"
}}
```

### 4.3 工具参数

#### request_handoff

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 要交接的任务 ID |
| `from` | string | ✅ | 当前负责人 Agent ID |
| `to` | string | ✅ | 目标接收人 Agent ID |
| `reason` | string | ❌ | 交接原因 |
| `context` | string | ❌ | 交接说明（进度、注意事项等） |

**约束**：
- 只有任务当前负责人才能发起交接
- 已终态（completed/failed/cancelled）的任务不能交接

#### accept_handoff / reject_handoff

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务 ID |
| `agent_id` | string | ✅ | 操作者 Agent ID |
| `reason` | string | ❌ | 拒绝原因（仅 reject） |

### 4.4 SSE 事件

| 事件 | 触发时机 | 推送目标 |
|------|---------|---------|
| `handoff_requested` | 交接请求发出 | 接收方 |
| `handoff_accepted` | 接收方接受 | 原负责人 |
| `handoff_rejected` | 接收方拒绝 | 原负责人 |

### 4.5 交接状态

```
none → requested → accepted
                  → rejected → (可重新请求)
```

---

## 5. 组合工作流示例

一个完整的 DAG 工作流，组合依赖链 + 并行组 + 质量门 + 交接：

```
┌──────────────┐
│   需求分析    │  (PM)
└──────┬───────┘
       │ finish_to_start
       ▼
┌──────────────┐
│   架构设计    │  (Architect)
└──────┬───────┘
       │ finish_to_start
       ▼
┌──────────────┐
│  设计 Review  │ ← 质量门（code_review，必须通过）
└──────┬───────┘
       │ 门通过
       ▼
┌─────┴─────┐
│  并行组    │
│ ┌───────┐ │
│ │API开发 │ │  (Backend Dev)
│ ├───────┤ │
│ │前端开发│ │  (Frontend Dev)
│ ├───────┤ │
│ │文档编写│ │  (Tech Writer)
│ └───────┘ │
└─────┬─────┘
      │ 全部完成
      ▼
┌──────────────┐
│   集成测试    │  (QA)
└──────┬───────┘
       │ 测试通过
       ▼
┌──────────────┐
│  发布交接    │  (Dev → SRE) ← 交接协议
└──────────────┘
```

---

## 6. 数据模型

### task_dependencies 表

| 列 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 依赖关系 ID |
| upstream_id | TEXT FK→tasks | 上游任务 |
| downstream_id | TEXT FK→tasks | 下游任务 |
| dep_type | TEXT | finish_to_start / start_to_start / finish_to_finish |
| status | TEXT | pending / satisfied / failed |
| created_at | INTEGER | 创建时间戳 |

**索引**：`idx_deps_downstream(downstream_id, status)`、`idx_deps_upstream(upstream_id, status)`

### quality_gates 表

| 列 | 类型 | 说明 |
|------|------|------|
| id | TEXT PK | 质量门 ID |
| pipeline_id | TEXT FK→pipelines | 所属 Pipeline |
| gate_name | TEXT | 阶段名称 |
| criteria | TEXT | JSON 判定条件 |
| after_order | INTEGER | 在此 order_index 后检查 |
| status | TEXT | pending / passed / failed |
| evaluator_id | TEXT | 评估者 |
| result | TEXT | 评估结果详情 |
| evaluated_at | INTEGER | 评估时间 |

---

*文档版本：v1.0 | 最后更新：2026-04-25*
