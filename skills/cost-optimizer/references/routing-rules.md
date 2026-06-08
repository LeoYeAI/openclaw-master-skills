# 路由规则详解与自定义方法

## 路由决策流程

```
用户 Prompt
    │
    ▼
┌──────────────────┐
│ 1. 关键词匹配     │  → 匹配 P0-P4 关键词列表
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 2. 复杂度评分     │  → 综合长度、步骤数、文件引用等
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 3. 上下文大小     │  → 超大上下文可能需要更强模型
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 4. 用户覆盖规则   │  → 自定义规则优先级最高
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 5. 成本上限检查   │  → 接近预算时强制降级
└────────┬─────────┘
         │
         ▼
  最终模型选择
```

## 优先级等级详解

### P0 — 最低成本（deepseek/v3 / gemini-flash）

**适用场景：**
- Heartbeat / 心跳检查：定时探活，不需要智能
- 状态查询：进程是否存活、磁盘空间、内存使用
- Cron 任务触发：定时任务的简单触发逻辑

**典型 prompt 示例：**
```
"检查系统状态"
"ping"
"heartbeat check"
"cron: cleanup temp files"
```

**预估成本：** $0.00001-0.0001/次

---

### P1 — 低成本（gemini-2.0-flash）

**适用场景：**
- 文件搜索和列表：找文件、搜代码、统计行数
- 简单信息查询：变量在哪里定义、函数在哪个文件
- 目录导航：ls、pwd、which

**典型 prompt 示例：**
```
"找到所有 .tsx 文件"
"搜索包含 TODO 的文件"
"列出 src/components 下的文件"
"这个函数在哪定义的？"
```

**预估成本：** $0.0001-0.001/次

---

### P2 — 中低成本（claude-haiku-4-5）

**适用场景：**
- 文件读取和理解：读取文件并解释内容
- 代码补全：自动补全函数体、参数
- 格式化和 lint：修复格式问题、lint 错误
- 简单重命名：变量/函数重命名

**典型 prompt 示例：**
```
"读取 src/app/page.tsx"
"修复这个 eslint 错误"
"把 camelCase 改成 snake_case"
"补全这个函数"
```

**预估成本：** $0.001-0.01/次

---

### P3 — 中等成本（claude-sonnet-4-6）

**适用场景：**
- 新代码编写：实现新功能、编写组件
- 调试和修复：分析 bug、提供修复方案
- 测试编写：单元测试、集成测试
- 代码解释：详细解释复杂逻辑
- 单文件重构：优化单个文件的代码结构

**典型 prompt 示例：**
```
"实现一个用户登录组件"
"修复这个空指针异常"
"为 UserService 编写单元测试"
"解释这段递归逻辑是怎么工作的"
```

**预估成本：** $0.01-0.10/次

---

### P4 — 高成本（claude-opus-4-6）

**适用场景：**
- 系统架构设计：整体架构、技术选型
- 多文件重构：跨多个文件的大规模重构
- 复杂推理：需要深度思考的问题
- 迁移方案：技术栈迁移、数据库迁移

**典型 prompt 示例：**
```
"设计一个微服务架构"
"重构整个认证系统"
"从 REST 迁移到 GraphQL 的方案"
"分析这个系统的性能瓶颈并给出优化方案"
```

**预估成本：** $0.10-1.00/次

**重要提示：** P4 应该尽量少触发。大多数日常开发任务用 P3（Sonnet）完全够用。

---

## 自定义路由规则

### 方法 1：在 openclaw.json 中添加覆盖规则

```json
{
  "cost-optimizer": {
    "routing": {
      "overrides": [
        {
          "pattern": "deploy|发布|上线",
          "model": "claude-sonnet-4-6",
          "reason": "部署操作需要可靠性但不需要最强推理"
        },
        {
          "pattern": "review.*PR|审查.*代码",
          "model": "claude-sonnet-4-6",
          "reason": "代码审查用 Sonnet 性价比最高"
        },
        {
          "pattern": "translate|翻译|i18n",
          "model": "claude-haiku-4-5",
          "reason": "翻译任务对推理要求不高"
        }
      ]
    }
  }
}
```

### 方法 2：按文件类型路由

```json
{
  "cost-optimizer": {
    "routing": {
      "file_type_rules": [
        {
          "extensions": [".md", ".txt", ".json", ".yaml"],
          "model": "claude-haiku-4-5",
          "reason": "配置和文档文件不需要强推理"
        },
        {
          "extensions": [".test.ts", ".spec.ts", ".test.js"],
          "model": "claude-sonnet-4-6",
          "reason": "测试文件需要理解业务逻辑"
        },
        {
          "extensions": [".ts", ".tsx", ".js", ".jsx"],
          "model": "claude-sonnet-4-6",
          "reason": "源代码文件默认用 Sonnet"
        }
      ]
    }
  }
}
```

### 方法 3：按时间段路由

```json
{
  "cost-optimizer": {
    "routing": {
      "time_rules": [
        {
          "hours": "09:00-18:00",
          "description": "工作时间",
          "max_model": "claude-opus-4-6"
        },
        {
          "hours": "18:00-23:00",
          "description": "非工作时间",
          "max_model": "claude-sonnet-4-6"
        },
        {
          "hours": "23:00-09:00",
          "description": "夜间",
          "max_model": "claude-haiku-4-5"
        }
      ]
    }
  }
}
```

---

## 降级策略详解

### 降级链

```
claude-opus-4-6 → claude-sonnet-4-6 → claude-haiku-4-5 → gemini-2.0-flash → deepseek/v3
```

### 触发条件

| 条件 | 说明 | 行为 |
|------|------|------|
| HTTP 429 | 速率限制 | 降一级，等待 retry-after 后恢复 |
| HTTP 503 | 服务不可用 | 降一级，5 分钟后尝试恢复 |
| 超时 > 30s | 响应过慢 | 降一级，本次会话不恢复 |
| 成本 > 80% 预算 | 接近预算上限 | 强制降一级 |
| 成本 > 95% 预算 | 接近硬限制 | 强制降到最便宜 |

### 恢复策略

降级不是永久的。系统会在以下条件下尝试恢复：

1. **速率限制恢复**：等待 `retry-after` 头部指定的时间
2. **服务恢复**：每 5 分钟探测一次原始模型是否可用
3. **预算恢复**：新的计费周期开始时重置

### 日志格式

所有降级事件都会记录：

```
[COST-ROUTE] [DEGRADE] opus→sonnet | reason=429 | retry_after=60s | session=abc123
[COST-ROUTE] [RECOVER] sonnet→opus | reason=rate_limit_cleared | session=abc123
```

---

## 调优建议

### 对于个人开发者

```json
{
  "routing": { "default_model": "claude-sonnet-4-6" },
  "cost_limits": { "daily_budget_usd": 5.00 }
}
```

大多数任务 Sonnet 完全够用，只在遇到真正复杂的问题时手动切换 Opus。

### 对于团队/CI 环境

```json
{
  "routing": { "default_model": "claude-haiku-4-5" },
  "cost_limits": { "daily_budget_usd": 20.00 }
}
```

CI 中的大多数任务（lint、格式化、简单代码生成）用 Haiku 即可。

### 对于预算紧张的场景

```json
{
  "routing": { "default_model": "gemini-2.0-flash" },
  "cost_limits": { "daily_budget_usd": 1.00 }
}
```

以 Gemini Flash 为主，只有复杂任务才升级到 Claude 系列。
