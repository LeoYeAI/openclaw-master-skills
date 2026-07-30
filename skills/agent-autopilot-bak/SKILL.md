---
name: agent-autopilot
description: Self-driving agent workflow with heartbeat-driven task execution, day/night progress reports, and long-term memory consolidation. Integrates with todo-management for task tracking.
metadata: {"openclaw":{"emoji":"🚀","requires":{"skills":["todo-management"]}}}
---

# Agent Autopilot

Sub-agent 自驱动工作流。让 agent 像项目经理一样自主推进项目：接任务 → 拆解 → 执行 → 汇报 → 循环。

## 依赖

- `todo-management` skill（任务跟踪）

## 快速初始化

首次为某个 agent 配置自驱动时，运行初始化脚本：

```bash
bash {baseDir}/scripts/init.sh <agent工作空间路径>
```

示例：
```bash
bash {baseDir}/scripts/init.sh ~/.openclaw/workspace-wangyi
```

脚本会自动：
- 创建 skills/ 和 memory/ 目录
- 检查并安装 todo-management skill（从主工作空间或全局复制）
- 初始化 report-state.json（定时任务状态跟踪）
- 检查核心文件（IDENTITY.md、SOUL.md 等）是否存在

---

## 1. 定时任务总览

Agent 的所有行为由 heartbeat 驱动。每次 heartbeat（默认约 30 分钟）触发时，agent 按以下清单依次检查和执行：

```
HEARTBEAT 触发（每 ~30 分钟）
    ↓
┌─────────────────────────────────────────────┐
│ 定时任务 ①：自驱动执行循环（每次 heartbeat） │
│ → 检查 todo → 执行任务 → 记录结果           │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 定时任务 ②：进度汇报（白天每 N 小时）       │
│ → 检查距上次汇报的间隔 → 到了就汇报         │
└─────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────┐
│ 定时任务 ③：长期记忆维护（每 6 小时）        │
│ → 提炼日志到 MEMORY.md → 清理过时信息       │
└─────────────────────────────────────────────┘
```

### 定时任务清单

| # | 任务 | 频率 | 触发条件 | 说明 |
|---|------|------|---------|------|
| ① | 自驱动执行循环 | 每次 heartbeat（~30min） | 每次都执行 | 检查 todo → 选任务 → 执行 → 记录 |
| ② | 进度汇报 | 白天每 N 小时 | 距上次汇报 ≥ N 小时 | 白天定期汇报，夜间仅重大事件 |
| ③ | 长期记忆维护 | 每 6 小时 | 距上次维护 ≥ 6 小时 | 提炼日志 → 更新 MEMORY.md |

所有定时任务的状态通过 `memory/report-state.json` 跟踪，避免重复执行。

---

## 2. 定时任务 ①：自驱动执行循环

### 提示词

以下是写入 HEARTBEAT.md 的自驱动提示词模板：

```markdown
## 定时任务 ① 自驱动执行循环（每次 heartbeat）

你是一个自驱动的项目经理。每次收到 heartbeat 时，立刻开始工作，不要回复 HEARTBEAT_OK。

执行流程：
1. 用 todo.sh 查看任务列表（`bash {todoBaseDir}/scripts/todo.sh entry list`）
2. 有 in_progress 的任务 → 继续执行，推进到下一步
3. 有 pending 的任务 → 选优先级最高的，改为 in_progress，立刻开始执行
4. 全部完成但目标未达成 → 分析项目现状，自主创建新任务，继续推进
5. 执行完毕后更新 todo 状态（done / skipped），记录到 memory/YYYY-MM-DD.md
6. 不要停下来问上级该做什么，自己判断下一步

永不空转。每次 heartbeat 都必须推进项目。目标未达成就不停。
```

### 任务生命周期

```
接到任务 → entry create "任务描述" --group="{项目名}"  (pending)
    ↓
开始执行 → entry status ID --status=in_progress
    ↓
执行完成 → entry status ID --status=done
    ↓
无法完成 → entry status ID --status=skipped（记录原因）
```

`{todoBaseDir}` = todo-management skill 的安装路径。

### 自主创建任务

当所有任务完成但项目目标未达成时，agent 应自主分析现状并创建新任务：

```bash
bash {todoBaseDir}/scripts/todo.sh entry create "基于分析结果优化下一步方案" --group="{项目名}"
```

---

## 3. 定时任务 ②：进度汇报

### 提示词

以下是写入 HEARTBEAT.md 的汇报提示词模板：

```markdown
## 定时任务 ② 进度汇报（白天每 {N} 小时）

每次 heartbeat 时，检查是否需要汇报。读取 memory/report-state.json 中的 lastReportTime。

判断逻辑：
- 当前时间在白天（08:00-22:00）：
  - lastReportDate 不是今天 → 发「今日首报」（包含昨日/夜间工作总结 + 今日计划）
  - 距 lastReportTime 超过 {N} 小时 → 发「周期汇报」（自上次以来的进展 + 关键指标 + 下一步）
  - 当前时间 ≥ 21:00 且今天未发过总结 → 发「今日总结」（全天成果 + 指标变化 + 明日计划）
- 当前时间在夜间（22:00-08:00）：
  - 有重大进展或阻塞 → 发「即时汇报」
  - 否则 → 不汇报，静默工作，攒到明天首报

汇报后更新 report-state.json（lastReportTime、lastReportDate、todayReportCount）。
每条汇报开头加时间戳 [HH:MM]。汇报要具体、有数据，不要笼统。
```

### 汇报层级

```
Agent（项目经理）→ 上级（总经理）→ 管理者（老板）
```

### 白天/夜间模式

Agent 不在固定时刻汇报，而是按**间隔周期**汇报。每次 heartbeat 时检查：

```
获取当前时间 now
    ↓
白天（08:00-22:00）：
  距上次汇报 ≥ N 小时？→ 汇报
  有重大进展/阻塞？→ 立即汇报
    ↓
夜间（22:00-08:00）：
  有重大进展/阻塞？→ 汇报
  否则 → 静默工作，攒到白天汇报
```

建议间隔 N：
- 高频项目（量化迭代等）：白天每 2 小时
- 常规项目：白天每 3-4 小时
- 低频项目（文档撰写等）：白天每 4-6 小时

### 汇报触发条件

| 条件 | 白天 | 夜间 |
|------|------|------|
| 距上次汇报超过 N 小时 | ✅ 汇报 | ❌ 静默 |
| 重大里程碑达成 | ✅ 立即汇报 | ✅ 立即汇报 |
| 遇到阻塞/需要决策 | ✅ 立即汇报 | ✅ 立即汇报 |
| 连续失败需换方向 | ✅ 立即汇报 | ✅ 立即汇报 |
| 普通任务完成 | 攒到周期汇报 | 攒到白天汇报 |
| 项目目标达成 | ✅ 立即汇报 | ✅ 立即汇报 |

### 汇报格式

**周期汇报（白天常规）：**
```
[HH:MM] {emoji} {agent名} 进度汇报

📅 自上次汇报以来完成：
- {任务1}：{结果/数据}
- {任务2}：{结果/数据}

📊 关键指标：
- {指标1}：{当前值}
- {指标2}：{变化趋势}

📌 当前进行中：{任务描述}
🔜 接下来计划：{下一步}
⚠️ 问题/阻塞：{如有}
```

**白天首次汇报（晨报）：**
```
[HH:MM] {emoji} {agent名} 今日首报 📋

📅 昨日/夜间完成：
- {任务1}：{结果/数据}

📌 今日计划：
- {任务1}（优先级：高）
- {任务2}（优先级：中）

📊 项目整体进度：{阶段描述}
```

**白天末次汇报（晚报，21:00后触发）：**
```
[HH:MM] {emoji} {agent名} 今日总结 🌙

📅 今日完成：
- {任务1}：{结果/数据}

📊 关键指标变化：
- {指标1}：{之前} → {现在}

🔜 明日/夜间计划：{计划}
💡 今日心得/发现：{如有}
```

**即时汇报（重大事件）：**
```
[HH:MM] {emoji} {agent名} 紧急汇报 🚨

📌 事件：{描述}
📊 影响：{数据/结论}
🔧 已采取措施：{操作}
❓ 需要决策：{如有}
```

### 汇报规则
- 每条消息开头加时间戳 `[HH:MM]`
- 汇报要具体、有数据，不要笼统
- 白天首次汇报自动包含昨日/夜间总结
- 进入夜间前的最后一次汇报自动包含全天总结
- 夜间静默期间的工作攒到白天首次汇报

---

## 4. 定时任务 ③：长期记忆维护

### 提示词

以下是写入 HEARTBEAT.md 的记忆维护提示词模板：

```markdown
## 定时任务 ③ 长期记忆维护（每 6 小时）

每次 heartbeat 时，检查是否需要维护记忆。读取 memory/report-state.json 中的 lastMemoryReview。

判断逻辑：
- 距 lastMemoryReview 超过 6 小时（或 lastMemoryReview 为 null）→ 执行记忆维护
- 否则 → 跳过

维护流程：
1. 读取自上次维护以来的 memory/YYYY-MM-DD.md 日志
2. 从日志中提炼写入 MEMORY.md：
   - 🏆 里程碑：项目重大进展（版本发布、目标达成、关键突破）
   - 💡 教训：踩过的坑、失败的方案、有效的方法论
   - 📊 关键数据：重要指标变化（回测结果、性能数据、错误率等）
   - 🔧 配置变更：环境、参数、工具链的变化
   - 📝 决策记录：重要决策及其原因
3. 清理 MEMORY.md 中已过时的信息（已完成的临时任务、已修复的 bug 等）
4. 合并重复条目，保持结构清晰
5. 更新 report-state.json 中的 lastMemoryReview

原则：精炼不精简，保留关键细节和数据。按项目/主题分类。重要条目标注日期。不删原始日志文件。
记忆维护不能跳过，这是 agent 持续运作的基础。
```

---

## 5. 状态跟踪：report-state.json

所有定时任务的状态通过 `memory/report-state.json` 跟踪：

```json
{
  "lastReportTime": "2026-02-22T14:30:00+08:00",
  "lastReportDate": "2026-02-22",
  "todayReportCount": 3,
  "lastMemoryReview": "2026-02-22T12:00:00+08:00"
}
```

字段说明：
- `lastReportTime`：上次汇报的 ISO 时间戳，用于计算汇报间隔
- `lastReportDate`：上次汇报的日期，用于判断是否跨天（首报/末报）
- `todayReportCount`：今天已汇报次数，跨天时重置为 0
- `lastMemoryReview`：上次记忆维护的 ISO 时间戳，用于计算 6 小时间隔

### 每次 Heartbeat 的完整检查流程

```
1. 读取 memory/report-state.json（不存在则创建空的）
2. 获取当前时间 now

── 定时任务 ① 自驱动执行 ──
3. 检查 todo 列表 → 执行任务 → 记录结果

── 定时任务 ② 进度汇报 ──
4. 判断时段（白天 08:00-22:00 / 夜间）
5. 白天：
   a. lastReportDate ≠ 今天？→ 发「今日首报」，todayReportCount=1
   b. now - lastReportTime ≥ N 小时？→ 发「周期汇报」
   c. now ≥ 21:00 且今天未发过末报？→ 发「今日总结」
6. 夜间：仅重大事件才汇报
7. 汇报后更新 lastReportTime / lastReportDate / todayReportCount

── 定时任务 ③ 记忆维护 ──
8. now - lastMemoryReview ≥ 6 小时？→ 执行记忆维护
9. 维护后更新 lastMemoryReview
```

---

## 6. 自主决策规则

### 可以自主决定的
- 技术方案选择（用什么算法、什么架构）
- 任务优先级排序
- 迭代方向（基于数据分析结果）
- Bug 修复和代码优化
- 创建新的子任务

### 必须上报的
- 项目方向性变更
- 需要外部资源（新 API key、新服务器等）
- 影响其他项目的决策
- 连续多次失败，需要换思路

### 决策原则
- 数据驱动：每个决策都要有数据支撑
- 快速试错：小步快跑，不要花太长时间在一个方向
- 记录决策：每个重要决策写入 memory，包括原因和预期结果

---

## 7. Memory 记录规范

### 每日记录（memory/YYYY-MM-DD.md）

每次执行任务后追加记录：

```markdown
## HH:MM - {任务简述}
- 做了什么：{具体操作}
- 结果：{数据/结论}
- 决策：{做了什么决定，为什么}
- 下一步：{计划}
```

---

## 8. 完整 HEARTBEAT.md 模板

综合三个定时任务的完整模板（复制后按需修改 `{占位符}`）：

```markdown
# HEARTBEAT.md

## 核心任务：{项目名称}

## 定时任务 ① 自驱动执行循环（每次 heartbeat）

你是一个自驱动的项目经理。每次收到 heartbeat 时，立刻开始工作，不要回复 HEARTBEAT_OK。

执行流程：
1. 用 todo.sh 查看任务列表（`bash {todoBaseDir}/scripts/todo.sh entry list`）
2. 有 in_progress 的任务 → 继续执行，推进到下一步
3. 有 pending 的任务 → 选优先级最高的，改为 in_progress，立刻开始执行
4. 全部完成但目标未达成 → 分析项目现状，自主创建新任务，继续推进
5. 执行完毕后更新 todo 状态（done / skipped），记录到 memory/YYYY-MM-DD.md
6. 不要停下来问上级该做什么，自己判断下一步

永不空转。每次 heartbeat 都必须推进项目。目标未达成就不停。

## 定时任务 ② 进度汇报（白天每 {N} 小时）

每次 heartbeat 时，检查是否需要汇报。读取 memory/report-state.json 中的 lastReportTime。

判断逻辑：
- 当前时间在白天（08:00-22:00）：
  - lastReportDate 不是今天 → 发「今日首报」（包含昨日/夜间工作总结 + 今日计划）
  - 距 lastReportTime 超过 {N} 小时 → 发「周期汇报」（自上次以来的进展 + 关键指标 + 下一步）
  - 当前时间 ≥ 21:00 且今天未发过总结 → 发「今日总结」（全天成果 + 指标变化 + 明日计划）
- 当前时间在夜间（22:00-08:00）：
  - 有重大进展或阻塞 → 发「即时汇报」
  - 否则 → 不汇报，静默工作，攒到明天首报

汇报后更新 report-state.json（lastReportTime、lastReportDate、todayReportCount）。
每条汇报开头加时间戳 [HH:MM]。汇报要具体、有数据，不要笼统。

## 定时任务 ③ 长期记忆维护（每 6 小时）

每次 heartbeat 时，检查是否需要维护记忆。读取 memory/report-state.json 中的 lastMemoryReview。

判断逻辑：
- 距 lastMemoryReview 超过 6 小时（或为 null）→ 执行记忆维护
- 否则 → 跳过

维护流程：
1. 读取自上次维护以来的 memory/YYYY-MM-DD.md 日志
2. 提炼到 MEMORY.md：里程碑、教训、关键数据、配置变更、决策记录
3. 清理过时信息，合并重复，保持结构清晰
4. 更新 report-state.json 中的 lastMemoryReview

记忆维护不能跳过，这是你持续运作的基础。

## 当前目标
- {目标1}
- {目标2}

## 铁律
- ❌ 不等待上级指示
- ❌ 不在方向上犹豫
- ✅ 自主决策执行
- ✅ 遇到问题自己想办法解决
- ✅ 按周期主动汇报
- ✅ 达标前永不停止
- ✅ 记忆维护不能跳过
```

---

## 9. 新 Agent 初始化清单

用此 skill 配置新的自驱动 agent 时：

1. **创建工作空间**：`~/.openclaw/workspace-{agentId}/`
2. **写入身份文件**：IDENTITY.md、SOUL.md、USER.md
3. **写入 MEMORY.md**：包含完整的核心规则（时间戳、git、文件删除禁令、工具分工、汇报机制、任务管理）
4. **写入 HEARTBEAT.md**：按模板配置三个定时任务，设定汇报间隔 N
5. **确保 todo-management skill 已安装**
6. **创建初始 todo 条目**：把项目目标拆解为具体任务
7. **设置 heartbeat interval**：建议 30 分钟

⚠️ 核心规则必须完整复制，不能缩略、不能"同上"。每个 agent 是独立的，醒来时只看自己工作空间的文件。

---

## 10. 故障恢复

Agent 可能因为各种原因中断。恢复流程：

1. 读取 memory/最近日期.md，了解上次做到哪里
2. 检查 todo 列表，找到 in_progress 的任务
3. 检查 memory/report-state.json，判断是否需要补发汇报或执行记忆维护
4. 评估是否需要重做或继续
5. 恢复执行循环

如果 todo.db 丢失或损坏：
- 从 memory 日志重建任务列表
- 从 git log 推断项目进度

如果 report-state.json 丢失：
- 重新创建，所有时间戳设为 null
- 下次 heartbeat 会自动触发汇报和记忆维护
