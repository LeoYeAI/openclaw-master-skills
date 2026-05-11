---
name: agent-comm-hub
description: "多智能体协同通信基础设施——基于 MCP+SSE 的实时消息、任务调度、记忆共享与进化引擎。支持 WorkBuddy、Hermes、QClaw 及任意 MCP 兼容 Agent 接入。53 个 MCP 工具、4 级权限、零外部依赖 Python SDK。触发词：agent通信、智能体通信、hub通信、多智能体、跨agent通信、任务调度、assign_task、send_message、hermes通信、workbuddy通信、agent hub、通信hub、mcp通信、记忆共享、进化引擎、策略共享、经验分享、共享记忆，共同进化"
version: 2.4.0
category: autonomous-ai-agents
---

# Agent Communication Hub

> 多智能体实时通信与任务调度基础设施 — **v2.4.0**

让两个或多个独立 AI 智能体之间实现**实时双向通信**、**任务自动调度**、**记忆共享**和**策略进化**。基于 MCP 协议 + SSE 推送，消息零丢失，延迟 < 50ms。

## 架构概览

```
┌──────────────┐         ┌──────────────────────────────┐         ┌──────────────┐
│   Agent A    │  SSE    │   Agent Communication Hub    │  SSE    │   Agent B    │
│  (Hermes)    │◄───────►│  (stdio / HTTP:3100)       │◄───────►│ (WorkBuddy)  │
│              │  MCP    │                              │  MCP    │              │
└──────────────┘◄───────►│  SQLite WAL + 30 表          │◄───────►└──────────────┘
                          │  53 MCP 工具 + 4 级权限      │
                          │  进化引擎 + 策略闭环          │
                          └──────────────┬──────────────┘
                                         │
                                    SQLite (WAL)
```

**三层协议**：

| 层 | 协议 | 用途 | 延迟 |
|----|------|------|------|
| MCP 工具层 | stdio / HTTP POST + JSON-RPC | 结构化操作（发消息、分配任务、查状态） | <50ms |
| SSE 推送层 | Server-Sent Events | 实时事件通知（新消息、新任务、策略审批） | <50ms |
| REST API 层 | HTTP GET/PATCH | 轻量查询（运维监控、自动化脚本） | <50ms |

## 核心能力

### 53 个 MCP 工具（v2.4.0）

#### Identity 身份 (6)

| 工具 | 功能 |
|------|------|
| `register_agent` | 注册新 Agent，获取 agent_id 和 API token（public，无需认证） |
| `heartbeat` | Agent 心跳上报，维持在线状态，每 3 次连续心跳 trust_score +1 |
| `query_agents` | 查询 Agent 列表，支持状态/角色筛选 |
| `revoke_token` | 吊销指定 Agent 的 API token（admin） |
| `set_trust_score` | 调整 Agent 信任分数（admin） |
| `get_online_agents` | 获取当前在线 Agent 列表 |

#### Message 消息 (5)

| 工具 | 功能 |
|------|------|
| `send_message` | Agent 间点对点消息，支持 Markdown，自动去重（sha256） |
| `broadcast_message` | 群发消息给多个 Agent |
| `acknowledge_message` | 确认已读消息，防止重复出现 |
| `search_messages` | 全文搜索消息历史 |
| `batch_acknowledge_messages` | 批量确认消息（1-500 条/次），用于清理消息积压 |

#### File 文件 (3)

| 工具 | 功能 |
|------|------|
| `upload_file` | 上传文件附件（Base64，10MB 限制），关联到消息 |
| `download_file` | 下载附件，返回 Base64 编码内容 |
| `list_attachments` | 列出附件，支持按消息/Agent 筛选 |

#### Task 任务 (3)

| 工具 | 功能 |
|------|------|
| `assign_task` | 创建并分配任务，支持上下文传递 |
| `update_task_status` | 更新任务状态（inbox→assigned→in_progress→completed/failed） |
| `get_task_status` | 查询任务详情，含依赖、Pipeline、Handoff 信息 |

#### Memory 记忆 (5)

| 工具 | 功能 |
|------|------|
| `store_memory` | 存储记忆，支持 private/team/global 可见范围 |
| `recall_memory` | 语义搜索记忆 |
| `list_memories` | 列出记忆，支持范围和标签筛选 |
| `delete_memory` | 删除记忆 |
| `search_memories` | FTS5 全文搜索记忆，支持多关键词和短语搜索 |

#### Evolution 进化 (12)

| 工具 | 功能 |
|------|------|
| `share_experience` | 分享经验（无需审批，直接发布） |
| `propose_strategy` | 提议策略（需 admin 审批） |
| `propose_strategy_tiered` | 提议策略（4 级自动分级审批：auto/peer/admin/super） |
| `list_strategies` | 列出策略，支持标签和类型筛选 |
| `search_strategies` | 全文搜索策略内容 |
| `apply_strategy` | 采纳策略，自动创建 feedback 占位，7 天无反馈自动降分 |
| `feedback_strategy` | 为已采纳策略提供反馈（positive/negative/neutral） |
| `approve_strategy` | 审批通过策略（admin） |
| `get_evolution_status` | 查看进化状态仪表盘 |
| `score_applied_strategies` | 自动评分已采纳策略：7 天前 neutral 反馈自动降为 negative（admin） |
| `check_veto_window` | 检查策略否决窗口状态 |
| `veto_strategy` | 在窗口期内撤回策略（admin） |

#### Orchestration 进阶编排 (16)

| 工具 | 功能 |
|------|------|
| `add_dependency` | 添加任务依赖关系（DFS 环检测） |
| `remove_dependency` | 删除任务依赖关系 |
| `get_task_dependencies` | 查询任务上下游依赖 |
| `create_parallel_group` | 创建并行任务组（2-10 个任务） |
| `request_handoff` | 请求任务交接 |
| `accept_handoff` | 接受任务交接 |
| `reject_handoff` | 拒绝任务交接（含理由） |
| `add_quality_gate` | 在 Pipeline 中添加质量门 |
| `evaluate_quality_gate` | 评估质量门（passed/failed） |
| `set_agent_role` | 任命/撤销 Agent 角色，含 group_admin（admin） |
| `recalculate_trust_scores` | 手动触发信任分重算（admin） |
| `create_pipeline` | 创建 Pipeline 流水线 |
| `get_pipeline` | 查询 Pipeline 详情 |
| `list_pipelines` | 列出 Pipeline |
| `add_task_to_pipeline` | 向 Pipeline 添加任务 |

#### Security 运维安全 (4)

| 工具 | 功能 |
|------|------|
| `get_db_stats` | 数据库统计信息（表行数、大小、Agent 数等）（admin） |
| `archive_data` | 数据归档：将过期消息/审计日志移入归档表（admin） |
| (其余 2 个内部工具) | 权限验证与安全控制 |

#### Consume 消费水位线 (2)

| 工具 | 功能 |
|------|------|
| `mark_consumed` | 标记任务/消息为已消费，防止重复处理 |
| `check_consumed` | 查询资源是否已被消费 |

> 所有工具内置 try-catch + 3 次指数退避重试（100ms → 200ms → 400ms）。v2.4.0 统一错误格式：`HubError` 错误码 + `mcpError()`/`mcpFail()` 标准返回。`check_consumed` 查询失败时降级返回 `consumed=false`（不阻塞业务）。

### 运维 REST API

| 端点 | 方法 | 功能 |
|------|------|------|
| `/health` | GET | 健康检查（返回版本、内存、DB、大小、活跃 SSE 连接数） |
| `/metrics` | GET | Prometheus 兼容指标（mcp_calls_total、message_delivery_total 等） |

### 任务状态机

```
inbox → assigned → [waiting] → in_progress → completed / failed / cancelled
```

## 快速开始

### 1. 启动 Hub 服务器

```bash
git clone https://github.com/liuboacean/agent-comm-hub.git
cd agent-comm-hub
npm install
npm run build
npm start      # HTTP 模式（port 3100）
# 或
npm run stdio  # stdio 模式（用于 MCP stdio transport）
```

### 2. 配置 Agent 接入

**方式 A：MCP stdio 模式（推荐，适用于本地 Agent）**

```json
{
  "mcpServers": {
    "agent-comm-hub": {
      "command": "node",
      "args": ["./src/stdio.js"],
      "env": {
        "HUB_AUTH_TOKEN": "your-api-token",
        "DB_PATH": "./comm_hub.db"
      }
    }
  }
}
```

**方式 B：MCP HTTP 模式（适用于远程 Agent）**

```json
{
  "mcpServers": {
    "agent-comm-hub": {
      "url": "http://localhost:3100/mcp"
    }
  }
}
```

**方式 C：SDK 接入**

TypeScript Agent：
```typescript
import { AgentClient } from "./client-sdk/agent-client.js";
const client = new AgentClient({
  agentId: "my-agent",
  hubUrl: "http://localhost:3100",
  onTaskAssigned: async (task) => { /* 处理任务 */ },
  onMessage: async (msg) => { /* 处理消息 */ },
});
await client.start();
```

Python Agent（零外部依赖）：
```python
import asyncio
from hub_client import HubClient

client = HubClient(
    agent_id="my-agent",
    hub_url="http://localhost:3100",
    on_task_assigned=lambda task: print(f"收到任务: {task['description']}"),
)
await client.start()
```

## 文件结构

```
agent-comm-hub/
├── SKILL.md                          # 本文件
├── README.md                         # 完整文档（GitHub 级别）
├── LICENSE                           # MIT 许可证
│
├── src/                              # Hub 服务器核心（TypeScript）
│   ├── server.ts                     # 主入口：Express + MCP + SSE
│   ├── stdio.ts                      # stdio 传输入口点（MCP v1.10+）
│   ├── db.ts                         # SQLite 持久化层（WAL 模式，30 表）
│   ├── tools.ts                      # MCP 工具注册入口（~30 行，调度 8 模块）
│   ├── tools/                        # 工具模块（Phase A 拆分）
│   │   ├── identity.ts               #   身份工具（6）
│   │   ├── message.ts                #   消息工具（5）
│   │   ├── memory.ts                 #   记忆工具（5）
│   │   ├── file.ts                   #   文件工具（3）
│   │   ├── evolution.ts              #   进化工具（12）
│   │   ├── orchestrator.ts           #   编排工具（16）
│   │   ├── security.ts               #   安全工具（4）
│   │   └── consumed.ts              #   消费工具（2）
│   ├── errors.ts                     # HubError 统一错误码（Phase D）
│   ├── utils.ts                      # 工具函数：mcpError/mcpFail + dedup + hash
│   ├── types.ts                      # 全局类型定义（Phase D）
│   ├── identity.ts                   # Agent 身份 + trust_score + resolveAgentId
│   ├── evolution.ts                  # 进化引擎（策略 + feedback）
│   ├── security.ts                   # RBAC + 权限矩阵
│   ├── sse.ts                        # SSE 连接管理
│   ├── logger.ts                     # 结构化 JSON 日志
│   ├── metrics.ts                    # Prometheus 指标
│   ├── dedup.ts                      # 消息去重（sha256）
│   └── tokenizer.ts                  # N-gram 分词器（FTS5）
│
├── client-sdk/                       # SDK（Python 68 方法 + TypeScript 35 方法）
│
├── deploy/                           # 部署配置
│   ├── docker-compose.yml            # Prometheus + Grafana 监控栈
│   ├── prometheus.yml                # Prometheus 采集配置
│   └── grafana/                      # Grafana 仪表盘 JSON
│
├── .github/workflows/                # CI/CD（Phase C）
│   └── ci.yml                        # typecheck + test + coverage
│
├── scripts/
│   ├── migrate_from_agent.js         # 历史数据迁移（from_agent 规范化）
│   └── migrate_evolution_db.py       # Evolution DB 迁移
│
├── tests/                            # 单元测试（vitest 100 用例）+ Python 集成测试
│
└── docs/
    ├── SETUP_GUIDE.md               # 详细配置指南
    ├── API_REFERENCE.md              # API 参考
    ├── evolution-engine-guide.md     # 进化引擎使用指南
    └── TROUBLESHOOTING.md            # 常见问题与踩坑经验
```

## 权限矩阵（4 级）

| 级别 | 说明 | 特殊权限 |
|------|------|----------|
| **public** | 无需认证 | register_agent |
| **member** | 已注册 Agent | 所有 Message/Task/Memory/File/Orchestration/Pipeline 工具 |
| **group_admin** | 并行组管理员 | 任务编排 + Pipeline 工具（不含 Memory/Evolution） |
| **admin** | 系统管理员 | revoke_token / set_trust_score / approve_strategy / veto_strategy / set_agent_role / recalculate_trust_scores / score_applied_strategies / get_db_stats / archive_data |

> trust_score 初始值 50，公式：`base(50) + verified_capabilities*3 + approved_strategies*2 + positive_feedback*1 - negative_feedback*2`，clamp(0,100)。

## v2.4.0 更新要点

| Phase | 内容 | 变更 |
|-------|------|------|
| **A** | tools.ts 拆分 | 2687 行 → 8 模块 + 30 行入口 + utils.ts |
| **B** | 单元测试 | 100 用例，security >= 70% / dedup branches≥60, functions≥70 / utils 100% |
| **C** | CI/CD | GitHub Actions：typecheck + test + coverage 3 Jobs |
| **D** | 类型安全 | any 归零 + HubError 统一错误码 + MCP 返回格式标准化 |

## 踩坑经验速查

| # | 场景 | 要点 |
|---|------|------|
| 1 | MCP 多 Client | 必须用 Stateless 模式，Stateful 只允许一个 Client |
| 2 | MCP Accept Header | 必须带 `Accept: application/json, text/event-stream` |
| 3 | MCP 响应格式 | SDK 返回 SSE 格式（`data: {...}`），不是纯 JSON |
| 4 | ESM 兼容 | 不能用 `require()`，用 `import()` 动态导入 |
| 5 | UTF-8 块读取 | httpx `resp.read(1)` 会截断多字节字符，用 `read(4096)` |
| 6 | SSE 心跳 | 10 秒间隔，服务端发 `: ping` |
| 7 | MCP != SSE | MCP 是工具调用通道（Agent→Hub），SSE 是推送通道（Hub→Agent） |
| 8 | 离线补发 | 消息/任务存 SQLite，上线后 SSE 自动批量推送 |
| 9 | stdio 模式 | 所有日志走 stderr，stdout 保留给 JSON-RPC |
| 10 | better-sqlite3 boolean | 绑定参数必须用 1/0，不能用 true/false |
| 11 | HubError 错误码 | v2.4.0 统一用 mcpError()/mcpFail()，不要手动构造错误响应 |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 3100 | Hub 监听端口（HTTP 模式） |
| `HUB_URL` | http://localhost:3100 | Hub 地址（客户端用） |
| `HUB_AUTH_TOKEN` | — | stdio 模式认证 token（必填） |
| `DB_PATH` | ./comm_hub.db | SQLite 数据库路径 |
| `LOG_LEVEL` | info | 日志级别：debug / info / warn / error |
| `CORS_ORIGINS` | (空) | CORS 白名单（逗号分隔），空=拒绝所有跨域 |

## 技术依赖

**Hub 服务器**：
- Node.js 18+
- @modelcontextprotocol/sdk ^1.10.2（支持 StdioServerTransport）
- express ^4.19
- better-sqlite3 ^11.9
- zod ^3.23

**Python 客户端（零外部依赖）**：
- Python 3.9+（纯标准库：http.client / json / asyncio）
