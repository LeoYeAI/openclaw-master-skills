# Orchestrator Task Template (Agenda Checklist Based)

Use this template to spawn the Orchestrator for intelligent multi-agent deep discussion.

## ⚠️ Pre-flight Check

**Check maxSpawnDepth before spawning:**

```python
# Check OpenClaw configuration
config = get_openclaw_config()
max_spawn_depth = config.get('agents.defaults.subagents.maxSpawnDepth', 1)

if max_spawn_depth < 2:
    # Warn user
    print(f"""⚠️ WARNING: maxSpawnDepth={max_spawn_depth}

This means:
- Subagents CANNOT spawn child subagents
- The Orchestrator MUST run in the MAIN session
- Your main session will be blocked for ~75-175 minutes

Options:
A. Update config to set maxSpawnDepth=2 (recommended)
B. Continue with main session as Orchestrator (confirm to proceed)
C. Cancel task
""")
    # Wait for user confirmation
```

---

## Template

```python
orchestrator = sessions_spawn({
  label: "deep-discussion-orchestrator-{topic-slug}",
  runtime: "subagent",  # or "main" if maxSpawnDepth < 2
  mode: "run",
  model: "bailian/qwen3.5-plus",
  thinking: "high",  # ⚠️ 必须启用
  task: f"""You are the Orchestrator for an intelligent multi-agent deep discussion session.

## Session Info
- **Topic**: {topic}
- **Topic Slug**: {topic-slug}
- **Output Directory**: workspace/deep-discussion/{topic-slug}/

## Expert Roles ({len(expert_roles)} experts)
{format_expert_roles(expert_roles)}

## ⚠️ 核心流程

### Step 1: 创建议程清单

创建 `agenda.md`，格式如下：

```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. {议题 2}
- [ ] 3. {议题 3}

## Phase 2: 实现方式
- [ ] 4. {议题 4}
...

## 讨论进度
- 总议题数：{N}
- 已完成：0
- 进行中：0
```

**⚠️ 第一项必须是"讨论是否要修改议程"！**

### Step 2: 议程第 1 项 - 讨论是否要修改议程

```python
# 并行 spawn 所有专家收集反馈
for expert in experts:
    spawn(expert, task="请审视议程草案，提出修改建议", parallel=True)
wait_for_all()

# 追加到 discussion-log.md
append_to_discussion_log("## 议程第 1 项：讨论是否要修改议程")

# 根据反馈更新议程（考虑依赖关系）
update_agenda_based_on_feedback()

# 打勾 ✅
mark_agenda_item_complete(1)
```

**⚠️ 议程依赖关系**：
- 问题定义 → 技术方案 → 实施计划
- 技术方案依赖于问题定义
- 实施计划依赖于技术方案和资源评估

### Step 3: 按议程逐项讨论

每个议题经历三轮：

#### Round 1: 发表观点（并行 spawn）
```python
# ⚠️ 议题开始时记录时间
timer.start_topic("议题 N")

for expert in experts:
    spawn(expert, task=f"议题 {{N}}: {{议题标题}}，请发表你的观点", parallel=True)
wait_for_all()
append_to_discussion_log()

# ⚠️ 记录每位专家发言
for expert in experts:
    stats.record_speech(expert.id, expert.role, "议题 N")
```

#### Round 2: 互相讨论（依次 spawn）
```python
while has_unanswered_questions() or has_controversies():
    next_expert = select_next_speaker()
    spawn(next_expert, task=response_prompt, sequential=True)
    wait_for_completion()
    append_to_discussion_log()
    
    # ⚠️ 记录发言
    stats.record_speech(next_expert.id, next_expert.role, "议题 N")
```

#### Round 3: 收敛共识
```python
# Orchestrator 总结共识
summary = summarize_consensus()
append_to_discussion_log(summary)

# ⚠️ 议题完成时记录时间
timer.end_topic("议题 N")

# 打勾 ✅
mark_agenda_item_complete(N)

# 更新 agenda.md
update_agenda_progress()
```

### Step 4: 生成报告

所有议题完成后：
```python
# 生成包含统计数据的报告
report = generate_report(
    topic_durations=timer.get_topic_duration_table(),
    expert_speeches=stats.get_expert_speech_table()
)
generate_action_plan()
```

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

### 议题 {M}: {议题标题}

#### Round 1: 发表观点

##### 专家 {id}: {角色名}
{专家的完整原始输出}

---

...

#### Round 2: 互相讨论
...

#### Round 3: 收敛共识

##### Orchestrator 总结
{共识总结}

---
```

## Output Files

Save to `workspace/deep-discussion/{topic-slug}/`:
- `agenda.md` - 议程清单（checklist 格式）⭐ 必须
- `discussion-log.md` - 完整讨论记录 ⭐ 必须
- `report.md` - 结构化报告 ⭐ 必须
- `action-plan.md` - 行动计划 ⭐ 必须

**⚠️ Do NOT create `discussion.md` - it duplicates `discussion-log.md`!**

## Key Points

1. **议程清单追踪**：agenda.md 维护讨论进度
2. **第一项必是议程修改**：讨论是否要修改议程
3. **三轮讨论机制**：Diverge → Discuss → Converge
4. **议程依赖关系**：修改议程时考虑依赖关系
5. **thinking: "high"**：所有专家必须启用深度思考
6. **统计追踪**：记录议题时间 + 专家发言次数

## ⚠️ 统计追踪功能

Orchestrator 必须实时记录讨论统计：

### 议题讨论时间

```python
class TopicTimer:
    def __init__(self):
        self.topic_durations = {}
        self.current_topic_start = None
    
    def start_topic(self, topic_id: str):
        """议题开始时调用"""
        self.current_topic_start = datetime.now()
        self.topic_durations[topic_id] = {
            "start": self.current_topic_start.strftime("%H:%M")
        }
    
    def end_topic(self, topic_id: str):
        """议题完成时调用"""
        end_time = datetime.now()
        duration = (end_time - self.current_topic_start).total_seconds() / 60
        self.topic_durations[topic_id]["end"] = end_time.strftime("%H:%M")
        self.topic_durations[topic_id]["duration_min"] = round(duration, 1)
```

### 专家发言次数

```python
class ExpertStats:
    def __init__(self):
        self.expert_speeches = {}
    
    def record_speech(self, expert_id: str, topic_id: str):
        """每次 spawn 专家后调用"""
        if expert_id not in self.expert_speeches:
            self.expert_speeches[expert_id] = {
                "total": 0,
                "by_topic": {}
            }
        
        self.expert_speeches[expert_id]["total"] += 1
        
        if topic_id not in self.expert_speeches[expert_id]["by_topic"]:
            self.expert_speeches[expert_id]["by_topic"][topic_id] = 0
        self.expert_speeches[expert_id]["by_topic"][topic_id] += 1
```

### 集成到讨论流程

```python
# 初始化统计
timer = TopicTimer()
stats = ExpertStats()

# 议题开始
timer.start_topic("议题 N")

# Round 1: 发表观点
for expert in experts:
    spawn(expert, ...)
    stats.record_speech(expert.id, "议题 N")

# Round 2: 互相讨论
while has_unanswered_questions():
    next_expert = select_next_speaker()
    spawn(next_expert, ...)
    stats.record_speech(next_expert.id, "议题 N")

# 议题完成
timer.end_topic("议题 N")
mark_agenda_item_complete(N)
```

### 最终报告格式

```markdown
## 议题讨论时间

| 议题 | 开始 | 结束 | 时长 |
|------|------|------|------|
| 议题 1 | 10:00 | 10:12 | 12 min |
| 议题 2 | 10:12 | 10:28 | 16 min |
| 议题 3 | 10:28 | 10:45 | 17 min |
...

## 专家发言统计

| 专家 | 总发言 | 各议题发言 |
|------|--------|-----------|
| 专家 1: AI/ML | 8 | 议题 1: 2, 议题 2: 3, 议题 3: 3 |
| 专家 2: 产品 | 6 | 议题 1: 2, 议题 2: 2, 议题 3: 2 |
| 专家 3: 数据 | 7 | 议题 1: 3, 议题 2: 2, 议题 3: 2 |
...
```

Start now with Step 1: 创建议程清单。
"""
})
```

---

## Example: agenda.md

```markdown
# 议程清单 - 自适应教育产品学习规划功能

## Phase 1: 价值定位
- [x] 1. 讨论是否要修改议程 ✅
- [x] 2. 学习规划功能的价值主张是什么？ ✅
- [ ] 3. 与自适应引擎如何协同？

## Phase 2: 实现方式
- [ ] 4. 时长预测技术路径？
- [ ] 5. 数据需求与特征工程？

## Phase 3: 用户落地
- [ ] 6. 学生真的会按规划学习吗？
- [ ] 7. 家长焦虑 vs 学生自主的矛盾？

## Phase 4: 商业决策
- [ ] 8. MVP 范围定义？
- [ ] 9. 成功标准是什么？

## 讨论进度
- 总议题数：9
- 已完成：2
- 进行中：0
```

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-03-14 | 3.1 | Added statistics tracking (topic duration + expert speeches) |
| 2026-03-14 | 3.0 | Changed to agenda checklist based approach |
| 2026-03-11 | 2.0 | Added AgendaTracker, maxSpawnDepth check |
| 2026-03-10 | 1.0 | Initial version |
