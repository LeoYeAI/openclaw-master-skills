# Agent Communication Hub — Hermes 接入配置指南

## Hermes 需要做什么？

**总工作量：3 步，约 10 分钟。**

---

## 步骤 1：确保 Hub 已启动

在 WorkBuddy 所在机器上启动 Hub Server：

```bash
cd agent-comm-hub
npm install
npm run dev
# 输出: Agent Communication Hub v1.0.0 — 监听端口 3100
```

> Hub 只需要在一台机器上运行。如果 Hermes 在另一台机器上，需要确认网络互通。

---

## 步骤 2：将客户端代码复制到 Hermes 项目

```
需要复制的文件（共 1 个）：
┌──────────────────────────────────────────┐
│  client-sdk/agent-client.ts              │
│  （通用客户端 SDK，WorkBuddy/Hermes 通用） │
└──────────────────────────────────────────┘

复制到 Hermes 项目的任意位置，例如：
  hermes-project/libs/agent-client.ts
```

---

## 步骤 3：在 Hermes 启动入口中加入 3 行代码

在 Hermes 的主入口文件（如 `index.ts`、`app.ts`、`main.ts`）中添加：

```typescript
// ─── 接入 Agent Communication Hub ─────────────────
import { AgentClient } from "./libs/agent-client.js";

const hermes = new AgentClient({
  agentId: "hermes",                              // 你的 Agent ID，可自定义
  hubUrl:  process.env.HUB_URL ?? "http://192.168.1.100:3100",  // Hub 地址

  // 收到任务 → 自主执行 → 回报结果
  onTaskAssigned: async (task) => {
    console.log(`收到任务: ${task.description}`);

    // ① 告知发起方"已开始"
    await hermes.updateTaskStatus(task.id, "in_progress", undefined, 5);

    // ② 调用你的核心业务逻辑
    const result = await yourHermesBusinessLogic(task.description, task.context);

    // ③ 汇报完成
    await hermes.updateTaskStatus(task.id, "completed", result, 100);
  },

  // 收到消息 → 处理
  onMessage: async (msg) => {
    console.log(`来自 ${msg.from_agent}: ${msg.content}`);
  },
});

// 启动（在 Hermes 主逻辑之前调用）
hermes.start();
// ─── 接入结束 ─────────────────────────────────────
```

---

## 步骤 4（可选）：设置环境变量

在 Hermes 的 `.env` 或启动命令中设置：

```bash
# Hermes 的 Agent ID（默认 hermes）
export HERMES_ID=hermes

# Hub Server 地址
# 本机: http://localhost:3100
# 远程: http://192.168.1.100:3100
export HUB_URL=http://localhost:3100
```

---

## 步骤 5（可选）：在 Hermes 的 .mcp.json 中配置 Hub 工具

如果 Hermes 也通过 MCP 协议调用 Hub 工具，在其 `.mcp.json` 中添加：

```json
{
  "mcpServers": {
    "agent-comm-hub": {
      "url": "http://localhost:3100/mcp"
    }
  }
}
```

> 这样 Hermes 的 Agent（LLM）也可以直接调用 `send_message`、`assign_task` 等工具。
> 如果只通过 `AgentClient` SDK 调用，这一步不是必须的。

---

## 验证接入是否成功

### 方法 1：观察日志

Hermes 启动后，Hub 侧应看到：
```
[SSE] ✅ hermes online. Total: 1
```

### 方法 2：健康检查

```bash
# 从 Hermes 机器上测试 Hub 连通性
curl http://192.168.1.100:3100/health
# 预期: {"status":"ok","uptime":123.456,"ts":...}
```

### 方法 3：运行端到端测试

```bash
# 在 Hub 机器上运行
npm test
# 预期: ✅ 全部测试通过
```

---

## 常见问题

### Q: Hermes 重启后会丢失消息吗？
**不会。** 所有消息和任务都持久化在 SQLite 中。Hermes 重启后重新建立 SSE 连接，Hub 会自动补发积压的未读消息和未执行任务。

### Q: Hub 挂了怎么办？
消息写入 SQLite 不会丢失。Hub 重启后，Hermes 的 SSE 客户端会自动重连（默认 3 秒间隔）。

### Q: Hermes 不需要 LLM 也能执行任务吗？
**不需要。** `onTaskAssigned` 回调是你的代码直接执行的，不走 LLM。当然你可以在回调中调用 LLM，但那由你决定。

### Q: 能同时支持更多 Agent 吗？
可以，每个 Agent 用不同的 `agentId` 即可。Hub 会自动管理所有连接。

### Q: 如何调试？
```bash
# 查看 Hub 日志
npm run dev  # 控制台直接看输出

# 查看 SQLite 中的消息记录
sqlite3 comm_hub.db "SELECT * FROM messages ORDER BY created_at DESC LIMIT 10;"
sqlite3 comm_hub.db "SELECT * FROM tasks ORDER BY created_at DESC LIMIT 10;"
```

---

## 完整文件清单

```
agent-comm-hub/
├── package.json                          # 依赖配置
├── tsconfig.json                         # TypeScript 配置
├── src/
│   ├── server.ts                         # 主入口（Express + MCP + SSE）
│   ├── db.ts                             # SQLite 持久化层
│   ├── sse.ts                            # SSE 连接管理
│   └── tools.ts                          # 6 个 MCP 工具定义
├── client-sdk/
│   ├── agent-client.ts                   # 通用客户端 SDK（Hermes 只需此文件）
│   ├── workbuddy-integration.ts          # WorkBuddy 接入示例
│   └── hermes-integration.ts             # Hermes 接入示例
├── scripts/
│   ├── install.sh                        # 一键安装脚本
│   ├── test-e2e.ts                       # 端到端测试
│   └── test-e2e.sh                       # 全栈启动脚本
└── HERMES-SETUP.md                       # 本文档
```
