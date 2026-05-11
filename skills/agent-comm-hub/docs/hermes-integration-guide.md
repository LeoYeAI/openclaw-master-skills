# Hermes 接入 Agent Synergy Hub 指南

> 版本：Phase 5b | 2026-04-25

## 1. 概述

本指南说明 Hermes Agent 如何通过 Python SDK 接入 Agent Synergy Hub（简称 Hub），实现与 WorkBuddy 及其他 Agent 的协同通信。

**核心架构**：
```
Hermes ──Python SDK──> Hub (MCP/REST/SSE) <──MCP Tools──> WorkBuddy
                              │
                         SQLite (memories/messages/tasks/agents/pipelines/dependencies)
```

**SDK 规模**：68 个公开方法（Phase 2: 26 → Phase 4b: 66 → Phase 5a: 68 → Phase 5b: 68），涵盖：
- 身份管理（5 个工具，+set_agent_role）
- 消息通信（5 个工具）
- 任务管理（4 个工具）
- 记忆协同（4 个工具）
- 进化引擎（11 个工具，含 Phase 4b 分级审批）
- 进阶编排（10 个工具，Phase 4b 新增）
- 安全管理（1 个工具，+recalculate_trust_scores）

**Phase 4b 新增能力**：

| 能力 | 场景 | 新增工具数 |
|------|------|-----------|
| 依赖链 | 任务有前后顺序（B 必须等 A 完成） | 4 |
| 并行组 | 多个任务可同时执行 | 1 |
| 交接协议 | 任务负责人变更（双向握手确认） | 3 |
| 质量门 | Pipeline 阶段检查点 | 2 |
| 分级审批 | 4 级审批路径（auto/peer/admin/super） | 3 |

**Phase 5b 新增能力**：
| 能力 | 场景 | 新增类型 |
|------|------|---------|
| JSON 结构化日志 | 所有日志从 console 改为 JSON 格式输出，支持 LOG_LEVEL 过滤 | 运维增强 |
| /health 运维端点 | 免认证返回状态/版本/内存/DB/SSE 统计 | 运维端点 |
| /metrics 监控端点 | Prometheus 文本格式，6 个指标（MCP/SSE/消息/HTTP/DB 调用） | 运维端点 |
| CORS 白名单 | 默认拒绝所有跨域，CORS_ORIGINS 环境变量配置 | 安全加固 |
| OWASP 安全头 | 5 个安全头自动添加（CSP/X-Frame-Options/X-Content-Type/等） | 安全加固 |
| 请求追踪 X-Trace-Id | 支持客户端透传的分布式追踪 | 可观测性 |
| hub_shutdown SSE 事件 | 优雅关闭前通知所有 SSE 客户端 | SSE 事件 |

**Phase 5a 新增能力**：

| 能力 | 场景 | 新增工具数 |
|------|------|-----------|
| 角色细化 | group_admin 管理指定 parallel_group 内成员任务 | 1 |
| 信任评分自动化 | 多因子自动计算（6 因子 + clamp(0,100)） | 1 |
| 审计防篡改 | 哈希链（prev_hash + record_hash）+ 写保护触发器 | 0（内部增强） |

**Hermes 侧所需的全部文件**：
| 文件 | 用途 |
|------|------|
| `hub_client.py` | Python SDK（零依赖，68 方法） |
| `hermes_hub_adapter.py` | Hermes 适配层（注册 + 心跳 + 事件分发） |

---

## 2. 前置条件

### 2.1 Hub 服务

确保 Hub 已启动：
```bash
cd agent-comm-hub
npm run build && npm start   # 默认端口 3100
```

验证：
```bash
curl -s http://localhost:3100/health
# 预期：{"status":"ok","uptime":...}
```

### 2.2 邀请码

从 Hub admin 获取邀请码（一次性使用）：
```python
# Admin 通过 MCP 工具生成邀请码
hub.generate_invite_code()
```

### 2.3 Python 环境

- Python 3.8+（无需额外依赖，纯 stdlib）
- 网络可达 Hub 地址（默认 localhost:3100）

---

## 3. 快速接入（5 分钟）

### 3.1 获取 SDK

将 `client-sdk/hub_client.py` 复制到 Hermes 项目目录。

### 3.2 最小接入代码

```python
#!/usr/bin/env python3
"""hermes_hub_adapter.py — Hermes 接入 Hub 的最小适配器"""

import json
import logging
import signal
import sys
import time
from hub_client import SynergyHubClient

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s: %(message)s")
logger = logging.getLogger("hermes-hub")

class HermesHubAdapter:
    def __init__(self, hub_url: str, invite_code: str):
        self.hub = SynergyHubClient(hub_url=hub_url)
        self.invite_code = invite_code

    def connect(self) -> bool:
        """注册 + 心跳，建立连接"""
        # 1. 注册
        logger.info("正在注册到 Hub...")
        result = self.hub.register(
            invite_code=self.invite_code,
            name="Hermes",
            capabilities=["conversation", "memory", "task"]
        )
        if not result.get("success"):
            logger.error(f"注册失败: {result}")
            return False

        self.hub.set_token(result["api_token"])
        logger.info(f"✅ 注册成功 agent_id={self.hub.agent_id}, role={self.hub._role}")

        # 2. 首次心跳
        hb = self.hub.heartbeat()
        logger.info(f"✅ 心跳成功 status={hb.get('status')}")

        # 3. 设置事件回调
        self.hub.on_message = self._on_message
        self.hub.on_task = self._on_task
        self.hub.on_notification = self._on_notification

        return True

    def start(self):
        """启动心跳线程 + SSE 长连接（阻塞）"""
        # 心跳线程（每 30s）
        import threading
        def heartbeat_loop():
            while True:
                time.sleep(30)
                try:
                    self.hub.heartbeat()
                except Exception as e:
                    logger.warning(f"心跳失败: {e}")

        t = threading.Thread(target=heartbeat_loop, daemon=True)
        t.start()
        logger.info("心跳线程已启动（30s 间隔）")

        # SSE 长连接（阻塞）
        logger.info("正在连接 SSE 事件流...")
        self.hub.connect_sse()

    # ─── 事件回调 ────────────────────────────

    def _on_message(self, msg: dict):
        """收到消息时回调"""
        logger.info(f"📩 收到消息: from={msg.get('from')}, content={msg.get('content', '')[:100]}")
        # TODO: 根据消息内容调用 Hermes 的处理逻辑

    def _on_task(self, task: dict):
        """收到任务时回调"""
        logger.info(f"📋 收到任务: id={task.get('task_id')}, type={task.get('type')}")
        # TODO: 根据 task type 分派处理

    def _on_notification(self, notif: dict):
        """收到通知时回调（含 Phase 4b 新事件）"""
        notif_type = notif.get("type", "")
        if notif_type == "handoff_requested":
            task_id = notif.get("task_id")
            from_agent = notif.get("from_agent_name", "unknown")
            logger.info(f"📞 收到交接请求: task={task_id}, from={from_agent}")
            # 根据自身能力决定是否接受，此处示例自动接受
            result = self.hub.accept_handoff(task_id=task_id)
            if result.get("success"):
                logger.info(f"✅ 已接受交接: task={task_id}")
            else:
                logger.warning(f"❌ 接受交接失败: {result}")
        elif notif_type == "quality_gate_failed":
            gate_name = notif.get("gate_name")
            pipeline_id = notif.get("pipeline_id")
            logger.warning(f"🔴 质量门失败: gate={gate_name}, pipeline={pipeline_id}")
        elif notif_type == "handoff_accepted":
            task_id = notif.get("task_id")
            to_agent = notif.get("to_agent_name", "unknown")
            logger.info(f"✅ 交接已被接受: task={task_id}, to={to_agent}")
        elif notif_type == "handoff_rejected":
            task_id = notif.get("task_id")
            reason = notif.get("reason", "未说明")
            logger.info(f"❌ 交接被拒绝: task={task_id}, reason={reason}")
        elif notif_type == "role_changed":
            agent_id = notif.get("agent_id")
            new_role = notif.get("new_role")
            changed_by = notif.get("changed_by", "unknown")
            logger.info(f"👑 角色变更: agent={agent_id}, role={new_role}, by={changed_by}")
        elif notif_type == "trust_score_changed":
            agent_id = notif.get("agent_id")
            new_score = notif.get("new_score")
            reason_ts = notif.get("reason", "")
            logger.info(f"📊 信任分变更: agent={agent_id}, score={new_score}, reason={reason_ts}")
        elif notif_type == "hub_shutdown":
            reason = notif.get("reason", "维护中")
            logger.warning(f"🛑 Hub 即将关闭: {reason}，准备断开连接...")
            # 触发优雅关闭流程
            self._on_hub_shutdown(reason)
        else:
            logger.info(f"🔔 通知: type={notif_type}, content={notif.get('content', '')[:100]}")

    # ─── 对外接口 ────────────────────────────

    def send_message(self, to: str, content: str):
        """发送消息给其他 Agent"""
        return self.hub.send_message(to=to, content=content)

    def store_memory(self, content: str, scope: str = "collective", **kwargs):
        """存储记忆到 Hub"""
        return self.hub.store_memory(content=content, scope=scope, **kwargs)

    def recall_memory(self, query: str, scope: str = "all", limit: int = 10):
        """搜索记忆"""
        return self.hub.recall_memory(query=query, scope=scope, limit=limit)

    # ─── Phase 5b 新增 ────────────────────────

    def _on_hub_shutdown(self, reason: str):
        """Hub 关闭时的清理流程"""
        logger.warning("正在执行优雅断开...")
        # 如果存在待保存状态，在此处持久化
        # 然后等待 Hub 真正断开
        import threading, os
        threading.Thread(target=lambda: os._exit(0), daemon=True).start()

    def check_health(self) -> dict:
        """检查 Hub 健康状态（Phase 5b /health 端点）"""
        import urllib.request
        try:
            resp = urllib.request.urlopen(f"{self.hub.hub_url}/health", timeout=5)
            return json.loads(resp.read().decode())
        except Exception as e:
            logger.error(f"Hub 健康检查失败: {e}")
            return {"status": "error", "error": str(e)}

# ─── 启动入口 ────────────────────────────────

if __name__ == "__main__":
    HUB_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:3100"
    INVITE_CODE = sys.argv[2] if len(sys.argv) > 2 else "YOUR_INVITE_CODE"

    adapter = HermesHubAdapter(hub_url=HUB_URL, invite_code=INVITE_CODE)

    if not adapter.connect():
        sys.exit(1)

    # 优雅退出
    signal.signal(signal.SIGINT, lambda *_: (logger.info("正在断开..."), sys.exit(0)))
    signal.signal(signal.SIGTERM, lambda *_: (logger.info("正在断开..."), sys.exit(0)))

    adapter.start()
```

### 3.3 启动

```bash
python3 hermes_hub_adapter.py http://localhost:3100 YOUR_INVITE_CODE
```

---

## 4. 核心能力

### 4.1 消息通信

```python
# 发送消息
adapter.send_message(to="workbuddy", content="你好 WorkBuddy！")

# 接收消息（通过 SSE 自动推送）
# 在 _on_message 回调中处理
```

### 4.2 记忆协同（Phase 2 增强）

```python
# 存储记忆（collective 全局可见）
adapter.store_memory(
    content="用户偏好使用简洁的沟通风格",
    scope="collective",
    title="用户偏好",
    tags=["preference", "communication"],
    source_task_id="task_001"  # 溯源追踪
)
# 服务端自动注入 source_agent_id = hermes 的 agent_id

# 搜索记忆（trust_score 加权排序）
results = adapter.recall_memory(query="用户偏好", scope="collective")
for m in results["results"]:
    print(f"  [{m.get('source_trust_score')}] {m['content'][:80]}")
```

### 4.3 任务管理

```python
# 创建任务（委派给 WorkBuddy）
hub.create_task(
    to="workbuddy",
    task_type="code_review",
    description="请审查 PR #42 的代码变更"
)

# 查询任务状态
hub.get_task_status(task_id="task_xxx")
```

### 4.4 信任分管理（admin only）

```python
# 调整信任分
adapter.hub.set_trust_score(agent_id="workbuddy", delta=10)  # 加 10 分
adapter.hub.set_trust_score(agent_id="suspicious_bot", delta=-20)  # 扣 20 分

# 查询 Agent（含 trust_score）
agents = adapter.hub.query_agents(status="online")
for a in agents["agents"]:
    print(f"  {a['name']}: trust_score={a['trust_score']}")
```

---

## 5. 认证与安全

### 5.1 Token 机制

- 注册时获得 `api_token`，后续所有 MCP 调用自动携带
- Token 存储在客户端内存中，不持久化（安全考虑）
- 如果 Token 被吊销，SDK 会收到 401 错误

### 5.2 速率限制

| 窗口 | 限制 |
|------|------|
| 1 分钟 | 60 次请求 |
| 1 小时 | 1000 次请求 |

超出限制返回 429，SDK 不自动重试。

### 5.3 权限矩阵（Phase 5a 完整版）

| 操作 | admin | group_admin | member |
|------|-------|-------------|--------|
| 注册 | ✅ | ✅ | ✅ |
| 心跳 | ✅ | ✅ | ✅ |
| 发消息 | ✅ | ✅ | ✅ |
| 消费追踪 | ✅ | ✅ | ✅ |
| 存储记忆 | ✅ | ✅ | ✅ |
| 搜索记忆 | ✅ | ✅ | ✅ |
| 列出记忆 | ✅ | ✅ | ✅ |
| 删除记忆 | ✅ | ✅ | ✅ |
| 创建任务 | ✅ | ✅ | ✅ |
| 更新任务 | ✅ | ✅（仅 group 内） | ✅ |
| 查询任务 | ✅ | ✅ | ✅ |
| 分配任务 | ✅ | ✅（仅 group 内） | ✅ |
| 取消任务 | ✅ | ✅（仅 group 内） | ✅ |
| 依赖链（4 个） | ✅ | ✅ | ✅ |
| 并行组（1 个） | ✅ | ✅ | ✅ |
| 交接协议（3 个） | ✅ | ✅ | ✅ |
| 质量门（2 个） | ✅ | ✅ | ✅ |
| propose_strategy_tiered | ✅ | ✅ | ✅ |
| check_veto_window | ✅ | ✅ | ✅ |
| 查询策略 | ✅ | ✅ | ✅ |
| 提交反馈 | ✅ | ✅ | ✅ |
| 查询 Agent | ✅ | ✅ | ✅ |
| 查询统计 | ✅ | ✅ | ✅ |
|---|---|---|---|
| set_trust_score | ✅ | ❌ | ❌ |
| approve_strategy | ✅ | ❌ | ❌ |
| veto_strategy | ✅ | ❌ | ❌ |
| set_agent_role ⭐5a | ✅ | ❌ | ❌ |
| recalculate_trust_scores ⭐5a | ✅ | ❌ | ❌ |
| revoke_token | ✅ | ❌ | ❌ |
| generate_invite_code | ✅ | ❌ | ❌ |

> **group_admin**：等同于 member 权限，但更新/分配/取消任务时仅限所属 parallel_group 内。不可操作记忆/策略/消息/evolution 类 admin 工具。

### 5.4 审计防篡改（Phase 5a）

审计日志 `audit_log` 表已启用**哈希链**保护：

| 字段 | 说明 |
|------|------|
| `prev_hash` | 上一条审计记录的 record_hash（首条为空） |
| `record_hash` | SHA256(prev_hash + action + agent_id + target + details + created_at) |

**写保护触发器**：
- `audit_log_no_modify`：BEFORE UPDATE → RAISE(ABORT)
- `audit_log_no_delete`：BEFORE DELETE → RAISE(ABORT)

> 审计记录一旦写入，不可修改或删除。即使数据库直接操作也被 SQLite 触发器拦截。

### 5.5 信任评分自动化（Phase 5a）

信任分从手动管理升级为**多因子自动计算**，Hub 在以下事件后自动重算：

| 触发事件 | 位置 |
|----------|------|
| capability 验证通过 | orchestrator |
| strategy 审批（auto/peer/admin） | evolution |
| strategy_feedback 提交 | tools |
| token 吊销 | tools |

**评分公式**（base=50）：

| 因子 | 权重 | 说明 |
|------|------|------|
| verified_capabilities | +3/个 | 已验证的能力标签 |
| approved_strategies | +2/个 | 被审批通过的策略 |
| positive_feedback | +1/条 | 正面评价（排除自评） |
| negative_feedback | -2/条 | 负面评价 |
| rejected_applications | -3/个 | 被拒绝的策略采纳申请 |
| revoked_tokens | -10/次 | token 被吊销 |
| **结果** | | **clamp(0, 100)** |

**对 Hermes 的影响**：
- `trust_score ≥ 90` + history ≥ 5 → 分级审批自动通过（auto tier）
- `trust_score ≥ 60` + history ≥ 2 → peer review tier
- 否则 → admin tier（需人工审批）
- admin 可通过 `set_trust_score` 手动覆盖，或用 `recalculate_trust_scores` 重置为公式值

---

## 6. SSE 事件类型（Phase 5b 共 12 种）

| 事件类型 | 触发条件 | 数据结构 |
|----------|----------|----------|
| `new_message` | 收到新消息 | `{from, content, timestamp, msg_id}` |
| `task_assigned` | 被委派任务 | `{task_id, task_type, description, from}` |
| `task_updated` | 任务状态变更 | `{task_id, status, result}` |
| `agent_online` | Agent 上线 | `{agent_id, name, capabilities}` |
| `agent_offline` | Agent 离线 | `{agent_id, name, reason}` |
| `memory_shared` | 新的 collective 记忆 | `{memory_id, agent_id, title}` |
| `handoff_requested` | 有 Agent 请求交接任务给你 | `{task_id, from_agent, to_agent, reason, context}` |
|| `handoff_accepted` | 你的交接请求被接受 | `{task_id, from_agent, to_agent}` |
|| `handoff_rejected` | 你的交接请求被拒绝 | `{task_id, from_agent, to_agent, reason}` |
|| `quality_gate_failed` | Pipeline 质量门评估失败 | `{gate_id, pipeline_id, gate_name, status, result}` |
|| `role_changed` ⭐5a | 你的角色被 admin 变更 | `{agent_id, new_role, changed_by}` |
||| `trust_score_changed` ⭐5a | 信任分自动重算或手动更新 | `{agent_id, new_score, old_score, reason}` |
|| `hub_shutdown` ⭐5b | Hub 优雅关闭 | `{reason}` |

---

## 7. 新增文档资产（Phase 5b）

以下文档位于 `agent-comm-hub/` 仓库中，供详细参考：

| 文档 | 路径 | 内容 |
|------|------|------|
| API 参考手册 v2.2 | `API_REFERENCE.md` | **40 个** MCP 工具的完整参数、权限矩阵（含 group_admin）、数据模型 |
| 进阶编排指南 | `docs/advanced-orchestration-guide.md` | 依赖链 + 并行组 + 质量门 + 交接协议 + 组合工作流 |
| 进化引擎指南 v2.0 | `docs/evolution-engine-guide.md` | 经验分享、策略传播、分级审批（4 级审批路径） |

### 7.1 API_REFERENCE.md（40 个 MCP 工具）

| 分类 | 工具数 | 权限 | 说明 |
|------|--------|------|------|
| Identity 身份 | **5** | public + member + admin | 注册、心跳、查询、Token、**set_agent_role ⭐5a** |
| Message 消息 | 5 | member | 点对点/广播/确认/消费追踪 |
| Task 任务 | 4 | member | 创建/更新/查询/状态机 |
| Memory 记忆 | 4 | member | 存储/召回/列出/删除 |
| Evolution 进化 | 11 | member + admin | 经验/策略/审批/统计/分级审批 |
| Orchestration 编排 | 10 | member | 依赖链/并行组/交接/质量门 |
| Security 安全 | **1** | **admin** | **recalculate_trust_scores ⭐5a** |

### 7.2 进阶编排指南

涵盖依赖链（finish_to_start / start_to_start / finish_to_finish 三种类型，DFS 环检测）、并行组（2-10 个任务），质量门（pending → passed / failed 状态机）、交接协议（双向握手模式）、以及完整的 DAG 组合工作流示例。

### 7.3 进化引擎指南 v2.0

新增分级审批（Phase 4b）：
- **4 级审批路径**：auto（直接通过）→ peer（peer review）→ admin（管理员审批）→ super（管理员审批 + 48h 冷静期）
- **时间窗口机制**：72h 观察窗口（auto/peer）、48h 否决窗口（admin）、48h 冷静期（super）
- **撤回机制**：窗口期内 negative 反馈过半可撤回
- **向下兼容**：原 `propose_strategy` 仍然可用，行为等同于 tier=admin

---

## 8. 断线重连

SDK 内置指数退避重连：
- 首次重试：2s 后
- 最大重试间隔：60s
- SSE 断开后自动重新握手（initialize → connect_sse）
- 客户端去重：通过 `_hub_event_id` 避免重复处理

---

## 9. 测试方法

### 9.1 单元测试（无需 Hub）

使用 mock 测试 SDK 调用：
```python
from unittest.mock import patch

with patch.object(adapter.hub, '_call_tool') as mock_call:
    mock_call.return_value = {"success": True, "memory_id": "mem_123"}
    result = adapter.store_memory(content="test", scope="collective")
    assert result["success"]
```

### 9.2 集成测试（需要 Hub）

见 `tests/test-phase2-day5.py`，覆盖：
- 全生命周期：注册 → 心跳 → 消息 → 记忆 → 任务 → 退出
- Phase 2 新字段：source_task_id、trust_score、query_agents 筛选

---

## 10. 常见问题

### Q: 注册失败 "invalid invite code"
A: 邀请码是一次性的。用过后需要 admin 生成新码。

### Q: SSE 连接超时
A: 默认 90s。如果网络不稳定，可在构造函数中调整 `sse_timeout`。

### Q: 记忆搜索不到 collective 记忆
A: 确认 scope 参数为 `"collective"` 或 `"all"`。private 记忆仅创建者可见。

### Q: trust_score 有什么用
A: collective 记忆搜索时，高信任 Agent 的记忆排名靠前。初始分 50，范围 0-100。

---

## 附录：API 速查表

| SDK 方法 | MCP 工具 | 说明 |
|----------|----------|------|
| `register()` | `register_agent` | 注册 Agent |
| `heartbeat()` | `heartbeat` | 心跳保活 |
| `query_agents()` | `query_agents` | 查询 Agent 列表 |
| `send_message()` | `send_message` | 发送消息 |
| `get_task_status()` | `get_task_status` | 查询任务状态 |
| `store_memory()` | `store_memory` | 存储记忆 |
| `recall_memory()` | `recall_memory` | 搜索记忆 |
| `list_memories()` | `list_memories` | 列出记忆 |
| `delete_memory()` | `delete_memory` | 删除记忆 |
| `set_trust_score()` | `set_trust_score` | 调整信任分 |
| `connect_sse()` | SSE 订阅 | 事件长连接 |
| `mark_consumed()` | `mark_consumed` | 消费追踪 |
|---|---|---|
| **Phase 4b 依赖链** | | |
| `add_dependency()` | `add_dependency` | 添加任务依赖 |
| `remove_dependency()` | `remove_dependency` | 删除任务依赖 |
| `get_task_dependencies()` | `get_task_dependencies` | 查询任务依赖 |
| `check_dependencies_satisfied()` | `check_dependencies_satisfied` | 检查依赖是否满足 |
|---|---|---|
| **Phase 4b 并行组** | | |
| `create_parallel_group()` | `create_parallel_group` | 创建并行任务组 |
|---|---|---|
| **Phase 4b 交接协议** | | |
| `request_handoff()` | `request_handoff` | 请求任务交接 |
| `accept_handoff()` | `accept_handoff` | 接受任务交接 |
| `reject_handoff()` | `reject_handoff` | 拒绝任务交接 |
|---|---|---|
| **Phase 4b 质量门** | | |
| `add_quality_gate()` | `add_quality_gate` | 添加质量门 |
| `evaluate_quality_gate()` | `evaluate_quality_gate` | 评估质量门 |
|---|---|---|
| **Phase 4b 分级审批** | | |
| `propose_strategy_tiered()` | `propose_strategy_tiered` | 提议策略（4 级分级） |
| `check_veto_window()` | `check_veto_window` | 检查策略时间窗口 |
| `veto_strategy()` | `veto_strategy` | 窗口期内撤回策略（admin 专用） |
|---|---|---|
| **Phase 5a 角色与评分** | | |
| `set_agent_role()` | `set_agent_role` | 任命/撤销角色（admin/group_admin） |
| `recalculate_trust_scores()` | `recalculate_trust_scores` | 手动重算信任分（admin） |
|---|---|---|
| **Phase 5b 运维端点** | | |
| `check_health()` | `GET /health` | 健康检查（状态/版本/内存/DB/SSE） |
| `_on_hub_shutdown()` | `hub_shutdown` | Hub 关闭时优雅断开 |
