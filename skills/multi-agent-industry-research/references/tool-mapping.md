# Claude Code → OpenClaw 工具映射参考

本文件记录从 Claude Code 到 OpenClaw 的工具映射，供适配和调试参考。

## 核心工具映射

| Claude Code | OpenClaw | 差异说明 |
|---|---|---|
| `Agent` tool | `sessions_spawn` | CC 同步等待；OC 异步返回 `{runId, childSessionKey}`，结果通过 announce 回报 |
| `AskUserQuestion` | 直接对话 | OC 中 agent 直接输出问题，等待用户下一条消息 |
| `Bash` | `exec` | 功能等价，OC 的 `exec` 支持 `timeout`、`background`、`host` 等参数 |
| `WebSearch` | `web_search` | 功能等价，OC 支持 9 种搜索 provider |
| `WebFetch` | `web_fetch` | 功能等价 |
| `Read` | `read` | 功能等价 |
| `Write` | `write` | 功能等价 |
| `Edit` | `edit` | 功能等价 |
| `Glob` | `exec` + `find` | OC 无专用 glob 工具 |
| `Grep` | `exec` + `grep`/`rg` | OC 无专用 grep 工具 |

## sessions_spawn 参数详解

```
sessions_spawn({
  task: string,              // 必填：sub-agent 的完整 prompt
  label: string,             // 可选：标识符，用于日志和追踪
  agentId: string,           // 可选：目标 agent（默认当前 agent）
  model: string,             // 可选：覆盖默认模型
  thinking: string,          // 可选：推理级别
  runTimeoutSeconds: number, // 可选：超时时间（秒）
  mode: "run" | "session",   // 可选：run=一次性，session=持久
  cleanup: "delete" | "keep", // 可选：完成后是否清理
  sandbox: "inherit" | "require" // 可选：沙箱继承或强制
})
```

**返回值**：`{ status: "accepted", runId, childSessionKey }`（立即返回，非阻塞）

## sessions_list 状态检查

用于兜底检查 sub-agent 状态：

```
sessions_list({
  kinds: "other",        // sub-agent sessions
  activeMinutes: 30,     // 最近 30 分钟内活跃
  messageLimit: 1        // 返回最后一条消息
})
```

## Announce 机制

Sub-agent 完成后自动发送 announce 消息到父 session，包含：
- 结果文本（assistant reply 或最后一个 tool result）
- 状态（completed/failed/timed out）
- 运行时间和 token 统计

## CC Agent Tool vs OC sessions_spawn 关键差异

| 特性 | Claude Code Agent | OpenClaw sessions_spawn |
|---|---|---|
| 执行模式 | 同步（等待完成） | 异步（立即返回） |
| 结果获取 | 直接返回 | announce 消息 |
| 并行控制 | 单条消息多个 Agent call | 多次 sessions_spawn |
| 权限控制 | `mode: "bypassPermissions"` | 默认继承所有工具（除 session 工具） |
| 子 agent 嵌套 | 无限制 | `maxSpawnDepth` 控制（默认 1） |
| 最大并发 | 无显式限制 | `maxConcurrent`（默认 8） |
