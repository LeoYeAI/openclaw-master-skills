---
name: cost-optimizer
description: |
  Ultimate cost optimization toolkit for OpenClaw/Claude Code. Smart model routing, context compression,
  heartbeat tuning, usage reports, config generation — save 60-80% on daily token costs.
  (中文) 智能模型路由、上下文压缩、Heartbeat 优化、消耗报告、配置生成，日均节省 60-80%。
user_invocable: true
argument-hint: "[route|compress|heartbeat|report|config] [options]"
allowed-tools: Bash, Read, Write, Edit, Grep, Glob, Agent
license: MIT
metadata:
  version: "1.0.0"
  author: "OpenClaw Community"
  openclaw:
    requires:
      bins: ["node"]
      env: []
    tags: ["cost", "optimization", "routing", "context", "heartbeat"]
---

# Cost Optimizer — OpenClaw/Claude Code 成本优化终极工具包

> 核心问题：OpenClaw 默认配置下 token 消耗极高（日均 $15+，heartbeat 月均 $50-100）。
> 本 skill 通过智能路由、上下文压缩、heartbeat 优化三管齐下，将成本降低 60-80%。

## 参数解析

解析用户输入的第一个参数，路由到对应子命令：

| 参数 | 子命令 | 说明 |
|------|--------|------|
| `route` | `/cost-route` | 智能模型路由 |
| `compress` | `/cost-compress` | 上下文压缩 |
| `heartbeat` | `/cost-heartbeat` | Heartbeat 优化 |
| `report` | `/cost-report` | 消耗报告 |
| `config` | `/cost-config` | 配置生成 |
| （无参数） | `/cost-report` | 默认显示消耗报告 |

---

## 1. `/cost-route` — 智能模型路由

### 任务分类引擎

对用户的 prompt 进行多维度分析，确定最佳模型：

**Step 0: 加载定价与规则数据**

```
Read references/model-pricing.md — 获取最新模型定价，用于成本计算和节省估算
Read references/routing-rules.md — 获取路由规则详情和自定义方法
```

> 如果 references 文件缺失或损坏，使用 index.ts 中硬编码的 MODEL_PRICING 常量作为 fallback。

**Step 1: 提取分类特征**

从当前 prompt 中提取以下特征：

```
特征维度：
- keywords: 关键词匹配（见下方路由规则表）
- context_length: 当前对话上下文 token 数（用 index.ts#estimateTokens 估算）
- complexity_score: 复杂度评分（0-10）
  - 0-2: 简单查询、状态检查
  - 3-5: 单文件操作、格式化、补全
  - 6-8: 多文件代码生成、调试、推理
  - 9-10: 架构设计、多步骤复杂任务
- tool_calls: 预期工具调用数量
- code_ratio: prompt 中代码占比
```

**Step 2: 路由决策**

根据特征匹配路由规则（优先级从高到低）：

| 优先级 | 条件 | 目标模型 | 预估成本/1M tokens |
|--------|------|----------|-------------------|
| P0 | heartbeat / cron / 状态检查 / ping | `deepseek/v3` 或 `gemini-2.0-flash` | $0.07-0.10 |
| P1 | 简单查询（complexity 0-2）、文件列表、搜索 | `gemini-2.0-flash` | $0.10 |
| P2 | 文件读取、代码补全、格式化、lint 修复 | `claude-haiku-4-5` | $0.80 |
| P3 | 代码生成、单文件调试、测试编写 | `claude-sonnet-4-6` | $3.00 |
| P4 | 多文件重构、架构设计、复杂推理 | `claude-opus-4-6` | $15.00 |

**关键词匹配表：**

```
P0 (最便宜):
  - heartbeat, ping, status, health, alive, cron, schedule
  - "是否在线", "检查状态", "心跳"

P1 (低成本):
  - list, find, search, grep, count, ls, pwd, which, where
  - "找到", "搜索", "列出", "有几个"

P2 (中低成本):
  - read, cat, format, lint, fix typo, rename, move
  - complete, autocomplete, suggest, snippet
  - "读取", "格式化", "补全", "重命名"

P3 (中等成本):
  - write, create, implement, generate, test, debug, explain
  - refactor (单文件), fix bug, add feature
  - "写", "创建", "实现", "生成", "测试", "调试"

P4 (高成本 - 仅在必要时):
  - architect, design, plan, review (全局), migrate
  - refactor (多文件), "从零开始", "重新设计"
  - complexity_score >= 9
  - context_length > 100k tokens
```

**Step 3: 降级策略**

```
降级链: opus → sonnet → haiku → gemini-flash → deepseek/v3
触发条件:
  - 目标模型 API 返回 429/503 → 降一级
  - 响应时间 > 30s → 降一级
  - 用户设置了成本上限且当前会话已超 80% → 强制降一级
  - 降级后在日志中记录: [COST-ROUTE] 降级: {原模型} → {新模型}, 原因: {reason}
```

**Step 4: 输出路由建议**

```markdown
## 🔀 模型路由建议

| 维度 | 值 |
|------|-----|
| 任务分类 | {category} |
| 复杂度评分 | {score}/10 |
| 上下文长度 | {tokens} tokens |
| 推荐模型 | {model} |
| 预估成本 | ${cost}/次 |
| 对比默认 | 节省 {savings}% |

> 路由依据: {匹配的关键词/规则}
```

**用户自定义覆盖：**

用户可在 `openclaw.json` 中添加自定义路由规则：

```json
{
  "cost-optimizer": {
    "routing": {
      "overrides": [
        {
          "pattern": "deploy|发布",
          "model": "claude-sonnet-4-6",
          "reason": "部署操作需要中等智能但不需要最强模型"
        }
      ]
    }
  }
}
```

---

## 2. `/cost-compress` — 上下文压缩

### 触发条件

- **自动触发**：当对话上下文估算超过 50k tokens 时，输出压缩建议
- **手动触发**：用户执行 `/cost-optimizer compress`

### 压缩策略

**Step 1: 分析当前上下文**

扫描对话历史，按以下类别统计 token 占比：

```
类别           | 描述                    | 压缩率
-------------- | ---------------------- | ------
recent_turns   | 最近 5 轮对话           | 0%（完整保留）
old_turns      | 更早的对话轮次          | 80-90%
tool_results   | 工具调用返回结果        | 70-85%
file_contents  | 文件完整内容            | 90-95%
code_blocks    | 代码块                  | 50-70%
system_context | 系统 prompt / 角色定义   | 0%（不压缩）
```

**Step 2: 执行压缩**

对每种类别应用不同的压缩策略：

1. **历史对话压缩**：
   - 保留最近 5 轮完整内容
   - 第 6-10 轮：提取关键决策点和结论
   - 第 10 轮以前：仅保留一句话摘要
   - 格式：`[轮次 N 摘要] 用户请求 X，助手执行了 Y，结果是 Z`

2. **工具调用结果压缩**：
   - 成功的文件读取 → 替换为 `[已读取 {path}, {lines} 行, 关键内容: {summary}]`
   - 成功的搜索结果 → 替换为 `[搜索 "{query}": 找到 {n} 个匹配, 主要在 {files}]`
   - 失败的工具调用 → 保留错误信息，移除重试的中间结果
   - Bash 输出 → 保留退出码和关键输出行（首尾各 5 行）

3. **文件内容压缩**：
   - 替换为路径+行号摘要：`[文件 {path}: {lines} 行, 函数: {func_list}, 关键逻辑在 L{start}-L{end}]`
   - 如果文件在后续被修改，只保留最终版本的摘要

4. **代码块压缩**：
   - 保留函数签名和关键逻辑
   - 移除注释和空行
   - 对未被后续引用的代码块，替换为 `[代码块: {language}, {lines} 行, 功能: {summary}]`

**Step 3: 生成压缩快照**

将压缩后的上下文摘要写入 `.context-snapshot.md`：

```markdown
# Context Snapshot
> 生成时间: {timestamp}
> 原始 tokens: {original} → 压缩后: {compressed} (节省 {ratio}%)

## 关键决策
- {decision_1}
- {decision_2}

## 活跃文件
- {file_1}: {summary}
- {file_2}: {summary}

## 待处理事项
- {todo_1}
- {todo_2}

## 最近对话（完整）
{last_5_turns}
```

**Step 4: 输出压缩报告**

```markdown
## 📦 上下文压缩报告

| 指标 | 值 |
|------|-----|
| 压缩前 | {original_tokens} tokens (~${original_cost}) |
| 压缩后 | {compressed_tokens} tokens (~${compressed_cost}) |
| 节省 | {saved_tokens} tokens (~${saved_cost}, {ratio}%) |
| 保留轮次 | 最近 {n} 轮完整保留 |
| 快照位置 | .context-snapshot.md |

> 建议：{下一步建议，如"开启新对话并加载快照"}
```

---

## 3. `/cost-heartbeat` — Heartbeat 优化

### 当前问题分析

OpenClaw 默认 heartbeat 配置：
- 间隔：15-30 分钟（过于频繁）
- 内容：全量状态检查（过于冗余）
- 模型：使用默认模型（过于昂贵）
- 月成本估算：$50-100（仅 heartbeat）

### 优化方案

**Step 1: 检查当前 heartbeat 配置**

读取以下位置的配置：
```bash
# OpenClaw 配置
cat ~/.openclaw/config.json 2>/dev/null
cat ./openclaw.json 2>/dev/null

# Claude Code 配置
cat ~/.claude/settings.json 2>/dev/null
cat ./.claude/settings.json 2>/dev/null
```

**Step 2: 生成优化配置**

```json
{
  "heartbeat": {
    "enabled": true,
    "base_interval_minutes": 45,
    "smart_adjustment": {
      "enabled": true,
      "rules": [
        {
          "condition": "active_development",
          "description": "检测到频繁文件变更（5分钟内 > 3次）",
          "interval_minutes": 30,
          "check": "find . -name '*.ts' -o -name '*.js' -o -name '*.py' -newer /tmp/.last-heartbeat 2>/dev/null | wc -l"
        },
        {
          "condition": "idle",
          "description": "无文件变更超过 30 分钟",
          "interval_minutes": 60
        },
        {
          "condition": "night_hours",
          "description": "本地时间 23:00-07:00",
          "interval_minutes": 120,
          "alternative": "disable"
        }
      ]
    },
    "content": {
      "mode": "minimal",
      "checks": [
        "process_alive",
        "disk_space_critical",
        "active_tasks_count"
      ],
      "skip": [
        "full_status_report",
        "dependency_check",
        "code_analysis",
        "git_log_summary"
      ]
    },
    "model": "deepseek/v3",
    "fallback_model": "gemini-2.0-flash",
    "max_tokens_per_heartbeat": 200,
    "cost_cap_monthly_usd": 5.00
  }
}
```

**Step 3: 估算节省**

```markdown
## 💓 Heartbeat 优化报告

### 当前配置 vs 优化配置

| 指标 | 当前 | 优化后 | 节省 |
|------|------|--------|------|
| 平均间隔 | {current}min | {optimized}min | — |
| 日均次数 | {current_daily} | {optimized_daily} | {reduction}% |
| 每次 tokens | ~{current_tokens} | ~{optimized_tokens} | {token_reduction}% |
| 使用模型 | {current_model} | deepseek/v3 | — |
| 每次成本 | ${current_cost} | ${optimized_cost} | {cost_reduction}% |
| **月均成本** | **${current_monthly}** | **${optimized_monthly}** | **${monthly_savings}** |

### 推荐配置

已写入 `openclaw.json` 的 heartbeat 部分。

### 智能间隔说明
- 🟢 活跃开发期（频繁文件变更）→ 30 分钟
- 🟡 普通工作期 → 45 分钟（默认）
- 🔴 静默期（无变更 > 30min）→ 60 分钟
- 🌙 夜间（23:00-07:00）→ 120 分钟或禁用
```

**Step 4: 应用配置**

如果用户确认，将优化配置合并到 `openclaw.json` 和/或 `.claude/settings.json`。

---

## 4. `/cost-report` — 消耗报告

### 数据收集

**Step 0: 加载定价数据**

```
Read references/model-pricing.md — 获取各模型单价，用于费用计算和节省估算
```

> 如果 references 文件缺失，使用 index.ts 中的 MODEL_PRICING 常量。

**Step 1: 读取使用日志**

```bash
# OpenClaw 使用日志
USAGE_LOG="$HOME/.openclaw/usage-log.jsonl"

# 如果日志不存在，基于当前会话估算
```

日志格式（每行一个 JSON）：
```json
{
  "timestamp": "2026-03-20T10:30:00Z",
  "session_id": "abc123",
  "model": "claude-sonnet-4-6",
  "input_tokens": 15000,
  "output_tokens": 3000,
  "task_type": "code_generation",
  "cost_usd": 0.054,
  "routed": false,
  "original_model": null
}
```

**Step 2: 计算统计数据**

使用 `index.ts` 中的工具函数计算：

- 本次会话消耗（基于对话长度估算）
- 本日/本周/本月累计（基于日志）
- 按模型分类的消耗分布
- 按任务类型的消耗分布
- 如果启用了路由，计算实际节省

**Step 3: 输出报告**

```markdown
## 📊 成本消耗报告

### 本次会话
| 指标 | 值 |
|------|-----|
| 总 tokens | {total_tokens} (输入: {input}, 输出: {output}) |
| 使用模型 | {models_used} |
| 估算成本 | ${session_cost} |
| 会话时长 | {duration} |

### 本周累计 ({week_start} - {week_end})
| 模型 | Tokens | 成本 | 占比 |
|------|--------|------|------|
| claude-opus-4-6 | {tokens} | ${cost} | {pct}% |
| claude-sonnet-4-6 | {tokens} | ${cost} | {pct}% |
| claude-haiku-4-5 | {tokens} | ${cost} | {pct}% |
| deepseek/v3 | {tokens} | ${cost} | {pct}% |
| **合计** | **{total}** | **${total_cost}** | **100%** |

### 按任务类型
| 类型 | 次数 | 平均 Tokens | 总成本 | 占比 |
|------|------|-------------|--------|------|
| 代码生成 | {n} | {avg} | ${cost} | {pct}% |
| 调试修复 | {n} | {avg} | ${cost} | {pct}% |
| 文件操作 | {n} | {avg} | ${cost} | {pct}% |
| heartbeat | {n} | {avg} | ${cost} | {pct}% |
| 其他 | {n} | {avg} | ${cost} | {pct}% |

### 趋势（最近 7 天）
{ascii_bar_chart}

### 💡 节省建议
{savings_recommendations}

> 如果本周全部使用智能路由，预计可节省 **${potential_savings}**（{savings_pct}%）
```

**ASCII 柱状图格式：**
```
日期       | 成本     | 分布
03-14 Mon  | $12.30  | ████████████░░░░░░░░
03-15 Tue  | $8.50   | ████████░░░░░░░░░░░░
03-16 Wed  | $15.20  | ███████████████░░░░░
03-17 Thu  | $6.30   | ██████░░░░░░░░░░░░░░
03-18 Fri  | $11.00  | ███████████░░░░░░░░░
03-19 Sat  | $3.20   | ███░░░░░░░░░░░░░░░░░
03-20 Sun  | $1.50   | █░░░░░░░░░░░░░░░░░░░
           +---------+--------------------
             总计: $58.00  日均: $8.29
```

---

## 5. `/cost-config` — 配置生成

### 预设方案

提供三档预设，用户可选择：

| 预设 | 说明 | 预估日均成本 | 适用场景 |
|------|------|-------------|---------|
| `conservative` | 保守优化，最小化风险 | $8-12 | 不确定时的安全选择 |
| `balanced` | 平衡成本与质量（推荐） | $4-8 | 日常开发 |
| `aggressive` | 激进节省，可能影响质量 | $1-4 | 预算紧张、简单任务为主 |

**Step 1: 分析当前配置**

读取现有配置文件：
```bash
cat ./openclaw.json 2>/dev/null || echo "{}"
cat ./.claude/settings.json 2>/dev/null || echo "{}"
```

**Step 2: 生成配置**

根据选择的预设生成完整的 `openclaw.json`（参考本 skill 目录下的 `openclaw.json` 模板）。

**Step 3: 输出配置 diff**

```markdown
## ⚙️ 配置生成 — {preset} 方案

### 变更预览

\`\`\`diff
--- openclaw.json (当前)
+++ openclaw.json (优化后)
@@ model_routing @@
- "default_model": "claude-opus-4-6"
+ "default_model": "claude-sonnet-4-6"
+ "routing_rules": [...]

@@ heartbeat @@
- "interval_minutes": 15
+ "interval_minutes": 45
+ "model": "deepseek/v3"

@@ context @@
+ "max_context_tokens": 80000
+ "auto_compress_threshold": 50000
\`\`\`

### 预估效果
| 指标 | 优化前 | 优化后 | 节省 |
|------|--------|--------|------|
| 日均成本 | ~${before}/天 | ~${after}/天 | ${savings}/天 |
| 月均成本 | ~${before_m}/月 | ~${after_m}/月 | ${savings_m}/月 |
| heartbeat 月成本 | ~${hb_before}/月 | ~${hb_after}/月 | ${hb_savings}/月 |

确认应用？输入 `yes` 应用，`no` 取消，或指定其他预设（conservative/balanced/aggressive）。
```

**Step 4: 应用配置**

用户确认后：
1. 备份当前配置：`cp openclaw.json openclaw.json.bak.{timestamp}`
2. 写入新配置
3. 验证配置格式正确（JSON 解析测试）
4. 输出确认信息

---

## 通用工具函数

本 skill 依赖 `index.ts` 中的工具函数，所有子命令共享：

- `classifyTask(prompt)` — 任务分类，返回 P0-P4 等级
- `estimateTokens(text)` — 基于字符数的 token 快速估算
- `routeModel(category, contextSize)` — 根据分类和上下文大小选择模型
- `compressContext(messages, budget)` — 上下文压缩
- `generateUsageReport(logPath)` — 从日志生成报告
- `calculateSavings(actual, optimized)` — 计算节省金额

详细类型定义和实现见 `index.ts`。

---

## 错误处理

所有文件操作均需显式 fallback，避免因单点故障中断整个流程：

| 操作 | 失败场景 | Fallback 行为 |
|------|---------|--------------|
| 读取 `openclaw.json` | 文件不存在 / JSON 解析失败 | 使用内置默认配置，输出 `⚠️ 配置文件读取失败，使用默认值` |
| 读取 `~/.openclaw/config.json` | 权限不足 / 路径不存在 | 跳过全局配置，仅使用项目级配置 |
| 读取 `references/*.md` | 文件缺失 | 使用 `index.ts` 中硬编码的 `MODEL_PRICING` 常量 |
| 写入日志 `~/.openclaw/cost-optimizer.log` | 目录不存在 / 磁盘满 | 回退到标准输出打印日志，输出 `⚠️ 日志写入失败，回退到 stdout` |
| 写入 `usage-log.jsonl` | 权限不足 | 跳过日志写入，输出 `⚠️ 使用日志写入失败，本次数据未记录` |
| 解析 `usage-log.jsonl` | 某行 JSON 格式损坏 | 跳过损坏行，继续解析后续行，报告中标注 `⚠️ 跳过 {n} 条损坏记录` |
| 写入 `openclaw.json`（配置应用） | 写入失败 | 不覆盖原文件，输出错误信息和配置内容到 stdout，让用户手动粘贴 |
| 备份配置文件 | 备份失败 | 中止配置写入，输出 `⚠️ 备份失败，已中止写入以保护现有配置` |

### 实现原则

1. **读取失败 → 降级到默认值**：永远不因读取失败而中断流程
2. **写入失败 → 回退到 stdout**：确保信息不丢失，用户可手动操作
3. **解析失败 → 跳过并报告**：损坏数据不影响其余有效数据的处理
4. **配置写入 → 备份优先**：备份失败则拒绝写入，保护用户现有配置

---

## 审计与日志

所有路由决策和配置变更都会记录日志：

```bash
# 日志位置
~/.openclaw/cost-optimizer.log

# 日志格式
[2026-03-20T10:30:00Z] [ROUTE] task=code_generation complexity=6 model=claude-sonnet-4-6 tokens=15000 cost=$0.054
[2026-03-20T10:35:00Z] [COMPRESS] before=80000 after=25000 ratio=68.75% snapshot=.context-snapshot.md
[2026-03-20T11:00:00Z] [HEARTBEAT] interval=45min model=deepseek/v3 tokens=150 cost=$0.00001
[2026-03-20T11:05:00Z] [CONFIG] preset=balanced changes=3 backup=openclaw.json.bak.1710924300
```

---

## 平台兼容性

| 功能 | OpenClaw | Claude Code |
|------|----------|-------------|
| 模型路由 | ✅ 完整支持 | ✅ 通过 /model 切换建议 |
| 上下文压缩 | ✅ 完整支持 | ✅ 生成快照文件 |
| Heartbeat 优化 | ✅ 完整支持 | ⚠️ 需手动配置 cron |
| 消耗报告 | ✅ 读取日志 | ✅ 基于会话估算 |
| 配置生成 | ✅ openclaw.json | ✅ settings.json |
