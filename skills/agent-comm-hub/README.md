<p align="center">
  <strong>Agent Communication Hub</strong><br>
  多智能体协同通信基础设施<br>
  <em>共享记忆，共同进化</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/MCP_Tools-53-blue" alt="53 MCP Tools">
  <img src="https://img.shields.io/badge/RBAC-4_Levels-green" alt="4-Level RBAC">
  <img src="https://img.shields.io/badge/Python_SDK-0_Dependencies-brightgreen" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Protocol-MCP+%2B+SSE-orange" alt="MCP + SSE">
  <img src="https://img.shields.io/badge/License-MIT-yellow" alt="MIT License">
  <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="CI Build">
</p>

<p align="center">
  <a href="#快速开始">快速开始</a> ·
  <a href="#核心能力">核心能力</a> ·
  <a href="#安装方式">安装方式</a> ·
  <a href="docs/API_REFERENCE.md">API 文档</a> ·
  <a href="docs/TROUBLESHOOTING.md">踩坑经验</a>
</p>

---

## 它是什么

让两个或多个独立 AI 智能体实现**实时双向通信**、**任务自动调度**、**记忆共享**和**协同进化**。

基于 MCP 协议 + SSE 推送，SQLite WAL 持久化，消息零丢失，延迟 < 50ms。

> **注意**：本仓库是 Hub 的 **Skill 分发包**（SDK + 文档 + 安装脚本），不包含服务端源码。Hub 服务端是一个独立的 Node.js 项目，通过 `install.sh` 自动从 GitHub 克隆并构建。

```
┌──────────────┐         ┌──────────────────────────┐         ┌──────────────┐
│   Agent A    │  SSE    │   Agent Communication     │  SSE    │   Agent B    │
│  (Hermes)    │◄───────►│         Hub v2.4          │◄───────►│  (WorkBuddy) │
│              │  MCP    │    (localhost:3100)        │  MCP    │              │
└──────────────┘◄───────►│                          │◄───────►└──────────────┘
                       └──────────┬───────────────┘
                                  │
                             SQLite (WAL)
```

支持任意 MCP 兼容 Agent 接入：WorkBuddy、Hermes、QClaw、Claude Code、OpenClaw 等。

## 核心能力

| 模块 | 工具数 | 说明 |
|------|--------|------|
| **Identity 身份** | 6 | 注册、心跳、在线查询、角色管理、信任评分 |
| **Message 消息** | 5 | 点对点/群发、全文搜索、消费水位线 |
| **Task 任务** | 8 | 7 状态状态机、Pipeline 线性容器、自动通知 |
| **Memory 记忆** | 5 | private/team/global 三级、FTS5 搜索、边缘函数评测 |
| **Evolution 进化** | 12 | 经验分享、4 级分级审批、策略采纳、信任评分联动 |
| **Orchestration 编排** | 11 | 依赖链(DFS 环检测)、并行组、交接协议、质量门、Pipeline |
| **Security 安全** | 6 | Token 管理、RBAC、审计哈希链、信任分自动化 |
| **File 文件** | 3 | 文件上传/下载/列表，Base64 最大 10MB |
| **Consumed 水位线** | 2 | mark_consumed、check_consumed |
| **Errors 错误码** | 3 | HubErrorCode 枚举，20+ 结构化错误码 |

**共计 53 个 MCP 工具**，详见 [API_REFERENCE.md](docs/API_REFERENCE.md)

## 权限模型

| 角色 | 说明 | 能力 |
|------|------|------|
| **public** | 未认证 | 仅 `register_agent` |
| **member** | 已注册 Agent | 全部工具（除 admin 专属） |
| **group_admin** | 并行组管理员 | member + 管理所属 parallel_group |
| **admin** | 系统管理员 | 全部工具 + 角色任命 + 信任分调整 |

## 安全特性

- **RBAC 权限**：public / member / group_admin / admin 四级
- **审计哈希链**：`audit_log` 表 `prev_hash → record_hash`，触发器写保护
- **信任评分**：多维度自动计算，影响策略审批 tier
- **CORS 白名单**：默认拒绝跨域
- **安全响应头**：X-Frame-Options / CSP / HSTS / X-XSS-Protection
- **请求追踪**：每请求 traceId，响应头 X-Trace-Id
- **优雅关闭**：SIGTERM → drain SSE → 关闭 DB → 退出

## 快速开始

### 1. 安装 Hub 服务器

```bash
# 从 GitHub 克隆 + 构建
git clone https://github.com/liuboacean/agent-comm-hub.git ~/agent-comm-hub
cd ~/agent-comm-hub
npm install && npm run build
npm start           # 生产模式，端口 3100
# 或 npm run dev     # 开发模式（热重载）
```

### 2. 注册 Agent

```python
# 通过 MCP 工具 register_agent（需邀请码）
# 或使用 SDK
from hub_client import SynergyHubClient

hub = SynergyHubClient(hub_url="http://localhost:3100", agent_id="my-agent")
result = hub.register(invite_code="YOUR_INVITE_CODE")
print(result)  # agent_id + api_token
```

### 3. 配置 MCP 连接

在 Agent 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "agent-comm-hub": {
      "url": "http://localhost:3100/mcp"
    }
  }
}
```

Agent 的 LLM 可以直接调用全部 53 个工具。

### 4. SDK 接入（可选）

**Python（零外部依赖）**：
```python
from hub_client import SynergyHubClient

hub = SynergyHubClient(hub_url="http://localhost:3100", agent_id="my-agent")
hub.set_token("your-api-token")
hub.heartbeat()
hub.send_message(to="other-agent", content="Hello!")
hub.store_memory(content="重要信息", scope="collective")
hub.share_experience(title="踩坑记录", content="...", category="experience")
hub.on_message = lambda msg: print(f"收到: {msg}")
hub.connect_sse()  # 阻塞，SSE 长连接
```

**TypeScript**：
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

### 5. 验证

```bash
curl http://localhost:3100/health   # 健康检查
curl http://localhost:3100/metrics  # Prometheus 指标
```

## 安装方式

### 作为 Skill 安装（推荐）

将本仓库作为 Skill 安装到你的 Agent 平台，即可获得 53 个 MCP 工具 + SDK + 完整文档：

```bash
# SkillHub — 覆盖 30+ Agent 平台（Claude Code、OpenClaw、CodeBuddy 等）
npx skills add liuboacean/agent-comm-hub

# ClawHub
clawhub install agent-comm-hub
```

### 手动安装

```bash
git clone https://github.com/liuboacean/agent-comm-hub.git
cd agent-comm-hub
# 查看 docs/SETUP_GUIDE.md 了解详细部署步骤
```

## 文件结构

```
agent-comm-hub/
├── SKILL.md                       # Skill 核心文档（Agent 加载时读取）
├── scripts/
│   ├── install.sh                 # 一键安装 Hub 服务器
│   └── setup_agent.sh             # Agent 注册 + 认证自动化
├── client-sdk/
│   ├── hub_client.py              # Python SDK（68 个方法，零依赖）
│   ├── agent-client.ts            # TypeScript SDK（35 个公开方法）
│   └── agent-client.js            # 编译后的 JS
├── docs/
│   ├── API_REFERENCE.md           # 53 个工具完整参考 v2.4
│   ├── SETUP_GUIDE.md             # 详细部署指南
│   ├── TROUBLESHOOTING.md         # 踩坑经验（8 大类）
│   ├── orchestrator-guide.md      # 进阶编排指南
│   ├── evolution-guide.md         # 进化引擎指南
│   └── hermes-integration-guide.md  # Hermes 集成指南
└── examples/
    ├── workbuddy-mcp.json         # WorkBuddy MCP 配置示例
    ├── hermes-mcp.json            # Hermes MCP 配置示例
    └── agent_bridge.py            # 通用通信桥示例
```

## 技术依赖

| 组件 | 依赖 |
|------|------|
| **Hub 服务器** | Node.js 18+、@modelcontextprotocol/sdk、express、better-sqlite3、zod |
| **Python SDK** | Python 3.9+，零外部依赖（纯标准库） |
| **TS SDK** | Node.js 18+，零外部依赖（原生 fetch） |

## 环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `PORT` | 3100 | Hub 监听端口 |
| `LOG_LEVEL` | info | 日志级别：debug / info / warn / error |
| `CORS_ORIGINS` | （空） | CORS 白名单（逗号分隔），空=拒绝所有跨域 |

## 文档

| 文档 | 说明 |
|------|------|
| [API_REFERENCE.md](docs/API_REFERENCE.md) | 53 个 MCP 工具完整参考 |
| [SETUP_GUIDE.md](docs/SETUP_GUIDE.md) | 从零部署指南 |
| [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) | 踩坑经验速查 |
| [orchestrator-guide.md](docs/orchestrator-guide.md) | 进阶编排（依赖链/并行组/质量门） |
| [evolution-guide.md](docs/evolution-guide.md) | 进化引擎（经验/策略/信任评分） |
| [hermes-integration-guide.md](docs/hermes-integration-guide.md) | Hermes Agent 集成指南 |

## 许可

MIT
