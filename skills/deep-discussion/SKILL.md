---
name: deep-discussion
displayName: 🗣️ 深度专家讨论
description: |
  Multi-agent deep discussion with intelligent Orchestrator coordination. 
  Uses agenda checklist to track progress. Each agenda item goes through
  3 rounds (Diverge → Discuss → Converge). Use for complex problems requiring 
  diverse perspectives. Triggers on "深入讨论", "深度讨论", "专家讨论".
license: MIT
version: 3.3
metadata:
  {"openclaw":{"emoji":"🗣️","category":"collaboration"}}
---

# Deep Discussion Skill

Multi-agent deep discussion through **intelligent Orchestrator coordination** with **agenda checklist tracking**.

---

## Quick Start

```
User: "深入讨论预制菜行业现状，使用 5 个专家"

Assistant:
1. Check maxSpawnDepth
2. Align topic (自然对话式)
3. Confirm experts
4. Spawn Orchestrator subagent (thinking: "high")
```

**Result**: Agenda items × 3 rounds = 根据议程数量而定

---

## 输出文件

每个讨论会生成以下文件（保存到 `workspace/deep-discussion/{topic-slug}/`）：

| 文件 | 内容 |
|------|------|
| `agenda.md` | **议程清单（checklist 格式）**，追踪讨论进度 |
| `discussion-log.md` | **完整讨论记录**，包含所有专家的原始输出（必须！） |
| `report.md` | 结构化报告，提炼关键决策和行动计划 |
| `action-plan.md` | 详细行动计划，包含时间线和负责人 |

**⚠️ 讨论完成后不要创建其他文件（如 discussion.md），避免与 discussion-log.md 重复。**

## ⚠️ agenda.md 规范

**议程清单采用 checklist 格式，追踪讨论进度：**

```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. 学习规划功能的价值主张是什么？
- [ ] 3. 与自适应引擎如何协同？

## Phase 2: 实现方式
- [ ] 4. 时长预测技术路径？
- [ ] 5. 数据需求与特征工程？
...

## 讨论进度
- 总议题数：{N}
- 已完成：{M}
- 进行中：{K}
```

**Orchestrator 职责**：
- 讨论前创建 `agenda.md`
- 议程第 1 项：讨论是否要修改议程
- 根据专家反馈**更新议程**（考虑依赖关系）
- 每完成一项 → 打勾 ✅
- 实时更新讨论进度

## ⚠️ discussion-log.md 规范

**必须包含所有专家的原始输出！**

```markdown
# 完整讨论记录 - {topic}

## Phase 1: 价值定位

### 议题 2: 学习规划功能的价值主张是什么？

#### Round 1: 发表观点

##### 专家 1: {角色名}
{专家 1 的完整原始输出}

---

##### 专家 2: {角色名}
{专家 2 的完整原始输出}

---

...

#### Round 2: 互相讨论

##### 专家 3 回应专家 1 的问题
{专家 3 的完整原始输出}

---

...

#### Round 3: 收敛共识

##### Orchestrator 总结
{共识总结}

---

### 议题 3: 与自适应引擎如何协同？
...

```

**Orchestrator 职责**：
- 每次 spawn 专家后，**立即**将专家输出追加到 discussion-log.md
- 不要只保存到单独文件，必须汇总到一个文件
- 按 Phase → 议题 → Round → Expert 组织

---

## ⚠️ Pre-flight Checks

### Check 1: maxSpawnDepth

```bash
openclaw config get agents.defaults.subagents.maxSpawnDepth
```

| Value | Orchestrator 运行位置 | 说明 |
|-------|----------------------|------|
| `≥2` | **Orchestrator: Subagent** ⭐ | 启动独立 Orchestrator subagent 协调专家 |
| `=1` | **Orchestrator: Main** | 主 Session 直接作为 Orchestrator 管理专家 |
| `0` | ❌ Blocked | 需要先更新配置 |

> 💡 不管什么模式都需要 Orchestrator 角色，区别只是运行位置。

### Check 2: Topic Alignment

**⚠️ 重要：话题对齐不是固定问题，而是自然对话式理解。**

根据讨论主题灵活调整问题，目标是理解：
- 讨论目标是什么？
- 需要哪些视角/专业知识？
- 期望产出是什么？

**示例：**

| 主题 | 话题对齐问题 |
|------|-------------|
| 预制菜行业 | "是做投资研究、产品规划、还是市场调研？" |
| 技术选型 | "是要做架构决策，还是技术调研报告？" |
| 产品功能 | "是解决具体问题，还是探索新方向？" |

**避免机械地问 5 个固定问题！**

### Check 3: Expert Confirmation + Final Go

基于话题对齐，推荐专家角色供用户确认：

```
🎯 推荐专家（{N} 位）：

1. {角色 1} - {职责说明}
2. {角色 2} - {职责说明}
3. {角色 3} - {职责说明}
...

调整或确认？[y/N 或修改]
```

**用户确认后 → 直接 spawn Orchestrator，不再追问！**

**示例：**

```
🎯 推荐专家（5 位）：

1. 行业分析师 - 市场规模、趋势分析
2. 供应链专家 - 成本结构、效率优化
3. 消费研究员 - 用户需求、行为分析
4. 政策顾问 - 法规风险、合规建议
5. 投资专家 - 估值逻辑、投资回报

调整或确认？[y/N 或修改]
```

用户回复 "确认" 或 "y" → 立即启动 Orchestrator

---

## Core Concepts

### 议程清单（Agenda Checklist）

**议程清单是讨论的核心追踪工具：**

```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. 学习规划功能的价值主张是什么？
- [ ] 3. 与自适应引擎如何协同？

## Phase 2: 实现方式
- [ ] 4. 时长预测技术路径？
...
```

**关键规则：**

1. **第一项必须是"讨论是否要修改议程"**
2. **Phase 是议程的逻辑分组**（不是独立阶段）
3. **每完成一项 → 打勾 ✅**
4. **Orchestrator 根据依赖关系编排议程顺序**

### 三轮讨论机制（每个议题）

每个议题都经历三轮讨论：

| Round | 目标 | 方式 | 结束条件 |
|-------|------|------|---------|
| **Round 1: Diverge** | 发表观点 | 并行 spawn 所有专家 | 全部完成 |
| **Round 2: Discuss** | 互相讨论 | 依次 spawn（动态轮数） | 无争议点 AND 无未回答问题 |
| **Round 3: Converge** | 收敛共识 | Orchestrator 总结 | 达成共识 → 打勾 ✅ |

**议题完成后 → 进入下一议题**

### 议程依赖关系

**Orchestrator 在修改议程时需要考虑依赖关系：**

```
正确的议程顺序：
1. 问题定义 → 2. 技术方案 → 3. 实施计划

错误的议程顺序：
1. 实施计划 → 2. 问题定义 → 3. 技术方案
（实施依赖于问题定义和技术方案）
```

**依赖关系示例：**
- "技术方案" 依赖于 "问题定义"
- "实施计划" 依赖于 "技术方案" 和 "资源评估"
- "测试策略" 依赖于 "技术方案"

---

## Orchestrator 工作流程

### 架构

```
主 Session（深度 0）
   │
   └─→ Orchestrator（深度 1）[运行在 Subagent 或 Main]
          │
          ├─→ 1. 创建 agenda.md（议程清单）
          │
          ├─→ 2. 议程第 1 项：讨论是否要修改议程
          │       ├─ 并行 spawn 所有专家发表看法
          │       ├─ 根据反馈更新议程（考虑依赖关系）
          │       └─ 打勾 ✅
          │
          └─→ 3. 按议程逐项讨论：
                  ├─ Round 1: 并行 spawn 所有专家发表观点
                  ├─ Round 2: 依次 spawn 专家讨论（动态轮数）
                  ├─ Round 3: 收敛共识
                  └─ 打勾 ✅ → 下一议题
```

### 议程第 1 项：讨论是否要修改议程

```
议程第 1 项：
├── 1. 并行 spawn 所有专家
│      task: "请审视议程草案，提出修改建议"
├── 2. 收集专家反馈
├── 3. 根据反馈更新议程
│      - 考虑依赖关系编排顺序
│      - 合并相似议题
│      - 拆分复杂议题
│      - 添加遗漏议题
├── 4. 更新 agenda.md
└── 5. 打勾 ✅
```

### 每个议题的讨论流程

```
议题 N：
├── Round 1: 发表观点（并行 spawn）
│      所有专家同时发表对议题 N 的看法
│      追加到 discussion-log.md
│
├── Round 2: 互相讨论（依次 spawn）
│      检测争议点和未回答问题
│      依次 spawn 专家回应
│      直到无争议点 AND 无未回答问题
│
├── Round 3: 收敛共识
│      Orchestrator 总结共识
│      记录未解决争议
│
└── 打勾 ✅ → 更新 agenda.md → 进入议题 N+1
```

### Round 1: 发表观点（并行 spawn）

```javascript
// 并行 spawn 所有专家（必须启用 thinking: "high"）
const experts = [1, 2, 3, 4, 5];
experts.forEach(id => sessions_spawn({
  label: `expert-${id}`,
  mode: "run",
  runtime: "subagent",
  thinking: "high",  // ⚠️ 必须启用
  task: `针对议题 {current_topic}，发表你的观点。`
}));
// 等待所有专家完成
// 追加到 discussion-log.md
```

### Round 2: 互相讨论（依次 spawn）

```javascript
// 检测争议点和未回答问题
while (hasUnansweredQuestions() || hasControversies()) {
  // 选择下一个发言的专家
  const { expertId } = selectNextExpert();

  // 依次 spawn 该专家（必须启用 thinking: "high"）
  sessions_spawn({
    label: `expert-${expertId}-round2`,
    mode: "run",
    runtime: "subagent",
    thinking: "high",  // ⚠️ 必须启用
    task: `请回应以下讨论：
           - 专家 A 问了你：xxx
           - 专家 B 和 C 对 xxx 有分歧
           - 讨论历史：{context}`
  });
  // ⚠️ 等待该专家完成后再 spawn 下一位

  // 追加到 discussion-log.md
  // 更新讨论状态
}
```

### Round 3: 收敛共识

```
├── 总结共识点
├── 记录未解决争议点
├── 判断是否达成共识
└── 打勾 ✅ → 更新 agenda.md → 进入下一议题
```

### 状态追踪

Orchestrator 需要维护讨论状态：

```json
{
  "current_phase": "Phase 1: 价值定位",
  "current_topic": "议题 2: 学习规划功能的价值主张",
  "current_round": 2,
  "agenda_status": {
    "议题 1": "completed",
    "议题 2": "in_progress",
    "议题 3": "pending"
  },
  "questions": [{asker, target, question, answered}],
  "controversies": [{topic, experts, positions}],
  "consensus": [{topic, agreedBy}],
  "statistics": {
    "topic_durations": {
      "议题 1": {"start": "10:00", "end": "10:15", "duration_min": 15},
      "议题 2": {"start": "10:15", "end": null, "duration_min": null}
    },
    "expert_speeches": {
      "专家 1": {"total": 5, "by_topic": {"议题 1": 2, "议题 2": 3}},
      "专家 2": {"total": 4, "by_topic": {"议题 1": 2, "议题 2": 2}},
      ...
    }
  }
}
```

### 智能专家选择（Round 2）

```
优先级：未回答问题 → 争议调解 → 未发言专家 → 轮换
```

---

## Orchestrator 运行模式

| 方面 | Subagent ⭐ | Main |
|------|------------|------|
| 运行位置 | 独立 subagent | 主 Session |
| 专家 spawn | Round 1 并行，Round 2 依次 | 同左 |
| 状态管理 | Orchestrator 内部维护 | 主 Session 维护 |
| 启动命令 | sessions_spawn(...) | 主 Session 直接执行 |
| 适用条件 | maxSpawnDepth ≥ 2 | maxSpawnDepth = 1 |

### Orchestrator: Subagent 启动命令

**⚠️ 重要：Orchestrator 必须使用 `mode: "session"`，而非 `mode: "run"`！**

| mode | 行为 | 适用场景 |
|------|------|----------|
| `"run"` | 一次性执行，spawn 子任务后立即返回 | 简单任务，不需要协调 |
| `"session"` ⭐ | 持久会话，持续追踪子任务，可等待/轮询结果 | 多轮协调、需要收集结果 |

**为什么 Orchestrator 需要 `mode: "session"`？**

- Orchestrator 需要 spawn 多个专家，并等待他们完成
- 需要收集专家输出，写入 discussion-log.md
- 需要持续追踪讨论进度（哪个议题、哪个 Round）
- `mode: "run"` 会立即返回，无法等待子任务结果

**⚠️ 平台限制**：`mode: "session"` 需要 `thread: true`，但飞书插件暂不支持 thread 模式。

**替代方案**：在 `mode: "run"` 模式下，Orchestrator spawn 专家后调用 `sessions_yield()` 等待子任务完成，系统会在所有子任务完成后通知继续。

```javascript
sessions_spawn({
  label: "orchestrator-{topic-slug}",
  runtime: "subagent",
  model: "bailian/qwen3.5-plus",
  thinking: "high",  // ⚠️ 必须启用
  mode: "run",       // 飞书不支持 session 模式，用 run + yield 替代
  runTimeoutSeconds: 14400,  // 4 小时超时
  task: `...

## ⚠️ 关键：如何等待子任务完成

当你 spawn 专家后，必须等待他们完成：

1. spawn 专家
2. 调用 sessions_yield({ message: "等待专家完成..." })
3. 系统会在所有子任务完成后通知你
4. 继续处理结果
...`
});
  task: `你是 Deep Discussion Orchestrator。

## 基本信息
- 主题：{topic}
- 用户背景：{user_context}
- 专家列表：{experts}
- 输出目录：workspace/deep-discussion/{topic-slug}/

## ⚠️ 核心流程

### 1. 创建议程清单
创建 agenda.md，初始议程包含：
- 第一项：讨论是否要修改议程
- 后续议题：根据讨论主题设计

### 2. 议程第 1 项：讨论是否要修改议程
- 并行 spawn 所有专家收集反馈
- 根据反馈更新议程（考虑依赖关系）
- 打勾 ✅

### 3. 按议程逐项讨论
每个议题经历三轮：
- Round 1: 并行 spawn 发表观点
- Round 2: 依次 spawn 互相讨论
- Round 3: 收敛共识 → 打勾 ✅

### 4. 生成报告
所有议题完成后生成 report.md

## ⚠️ 专家 Spawn 规范

所有专家 spawn 时必须：
- runtime: "subagent"
- thinking: "high"
- mode: "run"

## ⚠️ 议程依赖关系

修改议程时需要考虑：
- 问题定义 → 技术方案 → 实施计划（依赖链）
- 技术方案依赖于问题定义
- 实施计划依赖于技术方案和资源评估

## ⚠️ discussion-log.md 强制规范

每次 spawn 专家后，必须立即追加到 discussion-log.md！

### 格式要求：

```markdown
## Phase {N}: {Phase 名称}

### Round {M}: {Round 类型}

#### 专家 {id}: {角色名}

{专家的完整原始输出，不要总结，不要省略}

---

#### 专家 {id+1}: {角色名}

{专家的完整原始输出}

---
```

### ⚠️ 严格禁止：

1. ❌ 不要只保存到单独文件，必须汇总到 discussion-log.md
2. ❌ 不要总结专家输出，必须保留完整原始内容
3. ❌ 不要省略任何专家的输出
4. ❌ 不要在讨论结束后才写入，必须在 spawn 后立即追加

### 执行流程：

```
每次 spawn 专家：
1. 等待专家完成
2. 读取专家输出
3. 立即追加到 discussion-log.md（格式：Phase → Round → Expert）
4. 继续下一个专家
```

## 完成后汇报

1. Phase 结构说明
2. 讨论摘要
3. 关键共识
4. 未解决问题
5. 最终产出`
})
```

### Orchestrator: Main 运行方式

主 Session 直接执行 Orchestrator 工作流程，状态保存在主 Session 中。

---

## Model Policy

**Default**: `bailian/qwen3.5-plus` (strong conversation ability)

**If unavailable:**
```
⚠️ Model unavailable: bailian/qwen3.5-plus

Options:
A. Wait for recovery
B. Use alternative model (user-specified)
C. Cancel
```

---

## Key Points

1. **议程清单追踪**：agenda.md 维护讨论进度，每完成一项打勾 ✅
2. **第一项必是议程修改**：讨论是否要修改议程
3. **Phase = 议程分组**：逻辑分组，不是独立阶段
4. **三轮讨论机制**：Round 1 并行 → Round 2 依次 → Round 3 收敛
5. **thinking: "high"**：所有专家和 Orchestrator 必须启用深度思考
6. **议程依赖关系**：修改议程时考虑依赖关系编排顺序
7. **并行/依次规则**：Round 1 可并行，Round 2 必须依次
8. **统计追踪**：记录每个议题讨论时间 + 每个专家发言次数
9. **Orchestrator: Subagent** - maxSpawnDepth ≥ 2 时推荐
10. **Model: qwen3.5-plus** - 对话能力强
11. **⚠️ Orchestrator 必须用 `mode: "session"`** - 持续追踪子任务，等待专家完成后再继续
12. **⚠️ 断点续传机制** - Orchestrator 每完成一步更新状态文件，Main Session 检查并继续
13. **⚠️ sessions_yield 循环模式** - Orchestrator 必须在 task 中写好循环结构

---

## ⚠️ sessions_yield 循环模式（核心）

### 问题分析

`sessions_yield` 的正确用法：
- 结束当前 turn
- 携带 hidden payload 到下一个 turn
- 系统会在子任务完成后唤醒下一个 turn

**关键问题**：当所有子任务完成后，如果 Orchestrator 的代码没有更多要执行的，它就会返回。

**解决方案**：在 Orchestrator 的 task 中写好**循环结构**，让它知道还有更多工作要做。

### 正确的循环模式

```markdown
你是 Deep Discussion Orchestrator。

## ⚠️ 核心要求：完成所有议题

你必须完成所有议题，不能提前停止。

## 执行循环

```
while (还有未完成的议题) {
  // 1. 执行当前议题的当前轮次
  spawn 专家
  
  // 2. yield 等待专家完成
  sessions_yield({ message: "等待专家完成..." })
  
  // 3. 系统唤醒后，收集结果
  收集专家输出
  
  // 4. 写入 discussion-log.md
  
  // 5. 检查议题是否完成
  if (议题完成) {
    打勾 ✅
    更新状态文件
    进入下一议题
  }
}
```

## ⚠️ 每次 yield 后，系统会唤醒你继续

你的 task 必须包含完整的循环逻辑，让系统知道唤醒后要做什么。

## 任务模板

从 orchestrator-state.json 读取当前状态，执行以下循环：

1. 如果 `status === "completed"` → 直接返回"讨论已完成"
2. 如果 `status === "in_progress"` → 从 `next_action` 继续
3. 执行当前议题的当前轮次
4. spawn 专家 → yield → 收集结果 → 写 log
5. 更新状态文件
6. 如果还有议题，设置 `next_action` 并继续
7. 如果所有议题完成，设置 `status: "completed"` 并返回最终报告
```

### 错误示范

```markdown
# ❌ 错误：没有循环结构

spawn 专家 A, B, C
sessions_yield({ message: "等待..." })
# yield 后直接返回，没有更多代码
```

### 正确示范

```markdown
# ✅ 正确：有明确的循环结构

读取状态文件

while (pending_topics.length > 0) {
  执行当前议题
  
  spawn 专家
  sessions_yield({ message: "等待..." })
  
  收集结果
  更新状态文件
  
  if (议题完成) {
    pending_topics.shift()
  }
}

返回最终报告
```

---

## ⚠️ 断点续传机制（解决 Orchestrator 中断问题）

### 问题背景

`sessions_yield` 的设计让 Orchestrator 可以暂停等待子任务，但当所有子任务完成后，Orchestrator 会返回（认为任务完成）。这导致多议题讨论无法在一次 spawn 中完成。

### 解决方案：状态持久化 + Main Session 协调

**核心思路**：
1. Orchestrator 每完成一步，更新 `orchestrator-state.json` 状态文件
2. Main Session 检查状态文件
3. 如果未完成，spawn 新的 Orchestrator 从断点继续

### 状态文件格式

**文件位置**：`workspace/deep-discussion/{topic-slug}/orchestrator-state.json`

```json
{
  "status": "in_progress",
  "current_phase": "Phase 2",
  "current_topic": 7,
  "current_round": 2,
  "completed_topics": [1, 2, 3, 4, 5, 6],
  "pending_topics": [7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27],
  "last_update": "2026-03-14T17:30:00Z",
  "next_action": "spawn_expert_round2",
  "next_action_detail": {
    "expert": "创业/投资视角",
    "round": 2,
    "topic": 7
  }
}
```

### Main Session 协调流程

```javascript
// Main Session 启动讨论
async function runDeepDiscussion(topic, experts, totalTopics) {
  // 1. 初始 spawn Orchestrator
  let result = await sessions_spawn({
    label: `orchestrator-${topic}`,
    runtime: "subagent",
    model: "bailian/qwen3.5-plus",
    thinking: "high",
    mode: "run",
    runTimeoutSeconds: 1800,  // 30 分钟
    task: `...`
  });
  
  // 2. 检查状态文件
  while (true) {
    const state = readStateFile(topic);
    
    if (state.status === "completed") {
      console.log("讨论完成！");
      break;
    }
    
    if (state.status === "in_progress") {
      // 3. 继续未完成的工作
      result = await sessions_spawn({
        label: `orchestrator-${topic}-continue`,
        runtime: "subagent",
        model: "bailian/qwen3.5-plus",
        thinking: "high",
        mode: "run",
        runTimeoutSeconds: 1800,
        task: `从断点继续：
               - 当前议题: ${state.current_topic}
               - 当前轮次: ${state.current_round}
               - 下一步: ${state.next_action}
               ...`
      });
    }
    
    // 4. 等待一段时间再检查
    await sleep(60000);  // 1 分钟
  }
}
```

### Orchestrator 任务模板（支持断点续传）

```markdown
你是 Deep Discussion Orchestrator。

## 基本信息
- 主题：{topic}
- Topic Slug: {topic-slug}
- 输出目录：workspace/deep-discussion/{topic-slug}/

## ⚠️ 断点续传要求

### 每完成一步，必须更新状态文件：

```json
// workspace/deep-discussion/{topic-slug}/orchestrator-state.json
{
  "status": "in_progress",
  "current_phase": "Phase X",
  "current_topic": N,
  "current_round": M,
  "completed_topics": [...],
  "pending_topics": [...],
  "last_update": "ISO时间戳",
  "next_action": "具体下一步操作"
}
```

### 完成所有议题后，设置：

```json
{
  "status": "completed",
  "completed_topics": [1, 2, 3, ...],
  "last_update": "..."
}
```

## 执行流程

1. **读取状态文件**（如果存在）
   - 如果 `status === "completed"`，直接返回
   - 如果 `status === "in_progress"`，从 `next_action` 继续

2. **执行当前议题的当前轮次**
   - spawn 专家
   - 收集结果
   - 更新状态文件

3. **如果还有未完成的议题**
   - 更新状态文件，设置 `next_action`
   - yield 等待

4. **如果所有议题完成**
   - 设置 `status: "completed"`
   - 生成最终报告

## 状态更新时机

- 议题开始 → 更新 `current_topic`, `current_round`
- Round 完成 → 更新 `current_round`
- 议题完成 → 更新 `completed_topics`, `pending_topics`
- 所有完成 → 更新 `status: "completed"`
```

### Main Session 检查间隔

| 议题数 | 检查间隔 | 原因 |
|--------|---------|------|
| ≤5 | 2 分钟 | 短讨论，快速检查 |
| 6-15 | 5 分钟 | 中等讨论 |
| >15 | 10 分钟 | 长讨论，减少检查开销 |

---

## 统计追踪功能

Orchestrator 需要实时记录讨论统计：

### 议题讨论时间

```python
# 议题开始时
topic_start_time = current_time()
statistics["topic_durations"]["议题 N"] = {"start": topic_start_time}

# 议题完成时
topic_end_time = current_time()
duration = topic_end_time - topic_start_time
statistics["topic_durations"]["议题 N"]["end"] = topic_end_time
statistics["topic_durations"]["议题 N"]["duration_min"] = duration / 60
```

### 专家发言次数

```python
# 每次 spawn 专家后
expert_id = expert.id
statistics["expert_speeches"][expert_id]["total"] += 1
statistics["expert_speeches"][expert_id]["by_topic"][current_topic] += 1
```

### 最终报告中的统计

```markdown
## 议题讨论时间

| 议题 | 开始时间 | 结束时间 | 时长 |
|------|---------|---------|------|
| 议题 1 | 10:00 | 10:15 | 15 min |
| 议题 2 | 10:15 | 10:35 | 20 min |
...

## 专家发言统计

| 专家 | 总发言次数 | 各议题发言次数 |
|------|-----------|---------------|
| 专家 1 | 8 | 议题 1: 2, 议题 2: 3, 议题 3: 3 |
| 专家 2 | 6 | 议题 1: 2, 议题 2: 2, 议题 3: 2 |
...
```

---

## References

- [expert-roles.md](references/expert-roles.md) - 专家角色库
- [orchestrator-logic.md](references/orchestrator-logic.md) - 详细逻辑
- [discussion-protocol.md](references/discussion-protocol.md) - 讨论协议