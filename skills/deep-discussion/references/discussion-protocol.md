# Discussion Protocol (Agenda Checklist Based)

## Overview

This protocol defines the **agenda checklist based** multi-agent deep discussion, with intelligent Orchestrator facilitation.

**Key Principles:**
1. **Agenda checklist tracking** - Track progress with checklist, mark ✅ when complete
2. **First agenda item: Modify agenda** - Discuss whether to modify the agenda
3. **Phase = Logical grouping** - Group related agenda items together
4. **3 rounds per topic** - Diverge → Discuss → Converge

---

## File Structure

```
workspace/deep-discussion/{topic-slug}/
├── agenda.md          # 议程清单（checklist 格式）⭐ 核心
├── discussion-log.md  # 完整讨论记录
├── report.md          # 结构化报告
└── action-plan.md     # 行动计划
```

---

## Agenda Checklist Format

```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. 学习规划功能的价值主张是什么？
- [ ] 3. 与自适应引擎如何协同？

## Phase 2: 实现方式
- [ ] 4. 时长预测技术路径？
- [ ] 5. 数据需求与特征工程？

## Phase 3: 用户落地
- [ ] 6. 学生真的会按规划学习吗？
...

## 讨论进度
- 总议题数：{N}
- 已完成：0
- 进行中：0
```

---

## Discussion Flow

```
1. 创建议程清单（agenda.md）
    ↓
2. 议程第 1 项：讨论是否要修改议程
   ├─ 并行 spawn 所有专家收集反馈
   ├─ 根据反馈更新议程（考虑依赖关系）
   └─ 打勾 ✅
    ↓
3. 按议程逐项讨论：
   ├─ Round 1: 发表观点（并行）
   ├─ Round 2: 互相讨论（依次）
   ├─ Round 3: 收敛共识
   └─ 打勾 ✅ → 下一议题
    ↓
4. 所有议题完成 → 生成报告
```

---

## Step 1: Create Agenda Checklist

### Goals
- Create agenda.md with initial checklist
- First item must be "讨论是否要修改议程"
- Group related items into Phases

### Template

```markdown
# 议程清单 - {topic}

## Phase 1: 问题定义
- [ ] 1. 讨论是否要修改议程
- [ ] 2. {核心问题是什么？}
- [ ] 3. {目标用户是谁？}

## Phase 2: 方案设计
- [ ] 4. {技术方案？}
- [ ] 5. {实现路径？}

## Phase 3: 落地执行
- [ ] 6. {行动计划？}
...

## 讨论进度
- 总议题数：{N}
- 已完成：0
- 进行中：0
```

### ⚠️ 议程依赖关系

When modifying agenda, consider dependencies:

```
正确的顺序：
1. 问题定义 → 2. 技术方案 → 3. 实施计划

错误的顺序：
1. 实施计划 → 2. 问题定义 → 3. 技术方案
（实施依赖于问题定义和技术方案）
```

**Dependency rules:**
- "技术方案" depends on "问题定义"
- "实施计划" depends on "技术方案" and "资源评估"
- "测试策略" depends on "技术方案"

---

## Step 2: Agenda Item 1 - Modify Agenda

### Round 1: Expert Feedback (Parallel Spawn)

**Orchestrator Prompt:**
```
请审视以下议程草案：

## Phase 1: 问题定义
- [ ] 1. 讨论是否要修改议程
- [ ] 2. {议题}
...

请从你的专业角度：
1. 是否有遗漏的议题？
2. 议题顺序是否合理？需要调整吗？
3. 是否有议题需要合并或拆分？
```

**Spawn all experts in parallel:**
```python
for expert in experts:
    spawn(expert, task=prompt, parallel=True)
wait_for_all()
```

### Round 2: Update Agenda

**Orchestrator Task:**
```
根据专家反馈更新议程：

1. 分析所有专家的建议
2. 考虑依赖关系编排顺序
3. 合并相似议题
4. 拆分复杂议题
5. 添加遗漏议题
6. 更新 agenda.md
```

**Update agenda.md:**
```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [x] 1. 讨论是否要修改议程 ✅
- [ ] 2. 学习规划功能的价值主张是什么？
...

## 讨论进度
- 总议题数：{N}
- 已完成：1
- 进行中：0
```

---

## Step 3: Discuss Each Agenda Item

### Round 1: Diverge (Parallel Spawn)

**Orchestrator Prompt:**
```
议题 {N}: {议题标题}

请发表你的观点。

要求：
1. 从你的专业角度分析
2. 提出关键问题或挑战
3. 给出初步建议
```

**Spawn all experts in parallel:**
```python
# ⚠️ 议题开始时记录时间
timer.start_topic(f"议题 {N}")

for expert in experts:
    spawn(expert, task=f"议题 {N}: {topic}", parallel=True)
wait_for_all()

# Append all responses to discussion-log.md
append_to_discussion_log(phase, topic, round=1, responses)

# ⚠️ 记录每位专家发言
for expert in experts:
    stats.record_speech(expert.id, expert.role, f"议题 {N}")
```

### Round 2: Discuss (Sequential Spawn)

**Detect:**
- Unanswered questions
- Controversies/disagreements

**Sequential spawn:**
```python
while has_unanswered_questions() or has_controversies():
    next_expert = select_next_speaker()
    spawn(next_expert, task=response_prompt, sequential=True)
    wait_for_completion()
    append_to_discussion_log()
    
    # ⚠️ 记录发言
    stats.record_speech(next_expert.id, next_expert.role, f"议题 {N}")
```

**Prompt example:**
```
专家 A 问了你：{question}
专家 B 和 C 对 {topic} 有分歧：
- 专家 B 认为：{position_b}
- 专家 C 认为：{position_c}

请从你的专业角度回应。
```

### Round 3: Converge

**Orchestrator Summary:**
```
议题 {N}: {议题标题} - 共识总结

### 已达成共识
- 共识 1: {description}
- 共识 2: {description}

### 遗留分歧
- 议题 X: {description}（记录为开放问题）

### 关键决策
- 决策 1: {description}
```

**Mark agenda item complete:**
```python
# ⚠️ 议题完成时记录时间
timer.end_topic(f"议题 {N}")

# 打勾 ✅
mark_agenda_item_complete(N)

# 更新讨论进度
update_agenda_progress()
```

---

## Phase Management

**Phase is just logical grouping of agenda items.**

When all items in a Phase are complete:
```
✅ Phase 1 完成！进入 Phase 2
```

**No special Phase 0 anymore** - agenda modification is just agenda item #1.

---

## Final: Report Generation

**Generate report after all agenda items complete.**

```markdown
# {topic} - 深度讨论报告

## 议程完成情况

| Phase | 议题 | 状态 | 关键决策 |
|-------|------|------|---------|
| Phase 1 | 讨论是否要修改议程 | ✅ | 议程已优化 |
| Phase 1 | 学习规划价值主张 | ✅ | 核心价值：降低决策成本 |
| Phase 2 | 时长预测技术路径 | ✅ | 规则引擎先行 |
...

## 执行摘要
...

## 详细讨论记录
见 discussion-log.md

## 行动计划
见 action-plan.md
```

---

## Output Files

**必须生成的文件：**

| 文件 | 内容 |
|------|------|
| `agenda.md` | 议程清单（checklist 格式） |
| `discussion-log.md` | 完整讨论记录 |
| `report.md` | 结构化报告 |
| `action-plan.md` | 行动计划 |

**⚠️ Do NOT create `discussion.md` - it duplicates `discussion-log.md`!**

---

## Anti-Patterns & Interventions

### Pattern: Dominating Speaker

**Symptom:** One expert speaks 50%+ of the time

**Intervention:**
```
感谢专家 X 的深入分析。

现在我想听听其他专家的看法：
- 专家 Y，你从{domain}角度怎么看？
- 专家 Z，你有什么补充或不同意见？
```

### Pattern: Silent Expert

**Symptom:** One expert hasn't spoken in 2+ rounds

**Intervention:**
```
专家 X，我们还没听到你对{topic}的看法。

请从{domain}角度分享一下你的观点。
（1-2 段即可，不需要长篇分析）
```

### Pattern: Circular Discussion

**Symptom:** Same topic discussed for 3+ rounds without progress

**Intervention:**
```
📋 协调者介入

我注意到我们在{topic}上反复讨论。

建议：
1. 记录当前共识点：{list}
2. 记录剩余分歧：{list}
3. 决定是否：
   A. 继续讨论（如果这是关键阻塞点）
   B. 标记为"需更多数据"，进入下一议题
   C. 交由{owner}会后调研

请各位专家表态（A/B/C）。
```

---

## Success Metrics

A successful deep discussion has:

- [ ] All agenda items completed (marked ✅)
- [ ] Every expert spoke in each round (≥80% participation)
- [ ] ≥3 instances of experts building on others' ideas
- [ ] ≥2 instances of experts changing mind based on discussion
- [ ] Clear consensus on 80%+ of key decisions
- [ ] Remaining disagreements explicitly labeled
- [ ] Actionable plan with committed owners
- [ ] Final report generated and saved
