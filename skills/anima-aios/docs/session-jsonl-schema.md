# OpenClaw Session JSONL Schema

> 枢衡 P0-1 要求：先写 schema 再开发
> 基于实际数据分析 | 2026-03-25

## 文件位置

- 正常文件：`~/.openclaw/agents/{agentId}/sessions/{uuid}.jsonl`
- Reset 文件：`*.jsonl.reset.{timestamp}`（**跳过，不导入**）

## 行类型

### type: "session"（首行）
```json
{
  "type": "session",
  "version": 3,
  "id": "uuid",
  "timestamp": "ISO8601",
  "cwd": "/root/.openclaw/workspace-xxx"
}
```

### type: "model_change"
```json
{
  "type": "model_change",
  "id": "hex8",
  "provider": "bailian",
  "modelId": "qwen3.5-plus"
}
```

### type: "message"（核心）

**role 类型：**
- `user` — 用户消息
- `assistant` — AI 回复（可能包含 toolCall）
- `toolResult` — 工具调用结果

**assistant 消息中的 content 类型：**
- `type: "text"` — 文本内容
- `type: "thinking"` — 思考过程
- `type: "toolCall"` — 工具调用（⚠️ 是 toolCall 不是 tool_call）
  - `name`: 工具名（如 read, write, exec, message）
  - `id`: toolCallId
  - `arguments`: 参数对象

**toolResult 消息：**
```json
{
  "role": "toolResult",
  "toolCallId": "toolu_xxx",
  "toolName": "read",
  "content": [...],
  "isError": false
}
```

## 工具调用统计（全员 94 个 session）

| 工具名 | 调用次数 | 五维映射 |
|--------|---------|---------|
| exec | 2930 | application |
| read | 1340 | understanding |
| edit | 939 | creation |
| write | 713 | creation |
| message | 78 | collaboration |
| process | 76 | application |
| memory_search | 62 | application |
| sessions_list | 44 | metacognition |
| sessions_spawn | 22 | creation |
| web_search | 14 | understanding |
| memory_write | 12 | understanding |
| feishu_* | ~40 | application |
| cron | 8 | metacognition |

**总计：6334 次工具调用**
