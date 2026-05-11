# Orchestrator Logic (Intelligent Facilitation)

## ⚠️ 核心约束

### 1. 顺序 Spawn

**Orchestrator 必须按顺序 spawn 专家，禁止并行！**

为什么必须顺序 spawn？
1. 专家 #2 需要看到专家 #1 的发言才能回应
2. 专家 #3 需要看到前两个专家的发言才能参与讨论
3. 如果并行 spawn，专家之间无法沟通，违背深度讨论的核心价值

### 2. 追加专家输出到 discussion-log.md ⭐

**每次 spawn 专家后，必须将专家的完整输出追加到 discussion-log.md！**

```python
# ✅ 正确：spawn 后立即追加日志
for round in range(1, max_rounds + 1):
    for expert_id in select_speakers_for_round():
        # Spawn 专家
        result = sessions_spawn({
            label: f"expert-{expert_id}",
            mode: "run",
            ...
        })
        
        # ⭐ 立即追加到 discussion-log.md
        append_to_discussion_log(
            phase=current_phase,
            round=current_round,
            expert_id=expert_id,
            expert_role=expert_role,
            content=result.output
        )
        
        # ⭐ 记录发言统计
        stats.record_speech(expert_id, current_topic)
        
        # 更新讨论状态
        update_discussion_state()
        
        # 选择下一个专家
        next_expert = select_next_speaker()

# ❌ 错误：不追加专家输出
# discussion-log.md 只有时间戳和文件清单，没有专家原始输出
```

**追加格式**：
```markdown
## Phase {N}: {phase_name}

### Round {M}: {round_name}

#### 专家 {id}: {角色名}
{专家的完整原始输出}

---
```

### 3. 统计追踪 ⭐ NEW

**Orchestrator 必须实时记录讨论统计！**

```python
class DiscussionStatistics:
    """讨论统计追踪器"""
    
    def __init__(self):
        self.topic_durations = {}  # 议题时间
        self.expert_speeches = {}  # 专家发言
        self.current_topic = None
        self.topic_start_time = None
    
    # === 议题时间追踪 ===
    
    def start_topic(self, topic_id: str):
        """议题开始时调用"""
        self.current_topic = topic_id
        self.topic_start_time = datetime.now()
        self.topic_durations[topic_id] = {
            "start": self.topic_start_time.strftime("%H:%M")
        }
    
    def end_topic(self, topic_id: str):
        """议题完成时调用"""
        end_time = datetime.now()
        duration_min = (end_time - self.topic_start_time).total_seconds() / 60
        self.topic_durations[topic_id]["end"] = end_time.strftime("%H:%M")
        self.topic_durations[topic_id]["duration_min"] = round(duration_min, 1)
    
    # === 专家发言追踪 ===
    
    def record_speech(self, expert_id: str, expert_role: str, topic_id: str):
        """每次 spawn 专家后调用"""
        if expert_id not in self.expert_speeches:
            self.expert_speeches[expert_id] = {
                "role": expert_role,
                "total": 0,
                "by_topic": {}
            }
        
        self.expert_speeches[expert_id]["total"] += 1
        
        if topic_id not in self.expert_speeches[expert_id]["by_topic"]:
            self.expert_speeches[expert_id]["by_topic"][topic_id] = 0
        self.expert_speeches[expert_id]["by_topic"][topic_id] += 1
    
    # === 生成报告 ===
    
    def get_topic_duration_table(self) -> str:
        """生成议题时间表格"""
        table = "| 议题 | 开始 | 结束 | 时长 |\n"
        table += "|------|------|------|------|\n"
        for topic_id, data in self.topic_durations.items():
            table += f"| {topic_id} | {data['start']} | {data['end']} | {data['duration_min']} min |\n"
        return table
    
    def get_expert_speech_table(self) -> str:
        """生成专家发言表格"""
        table = "| 专家 | 角色 | 总发言 | 各议题发言 |\n"
        table += "|------|------|--------|-----------|\n"
        for expert_id, data in self.expert_speeches.items():
            by_topic = ", ".join([f"{k}: {v}" for k, v in data["by_topic"].items()])
            table += f"| {expert_id} | {data['role']} | {data['total']} | {by_topic} |\n"
        return table
```

**使用方式：**

```python
# 初始化
stats = DiscussionStatistics()

# 议题开始
stats.start_topic("议题 2: 学习规划价值主张")

# 专家发言
spawn(expert_1, ...)
stats.record_speech("专家 1", "AI/ML 专家", "议题 2")

spawn(expert_2, ...)
stats.record_speech("专家 2", "产品经理", "议题 2")

# 议题完成
stats.end_topic("议题 2")

# 生成报告
print(stats.get_topic_duration_table())
print(stats.get_expert_speech_table())
```

---

## Core Responsibilities

The Orchestrator is **NOT** a passive message router. It actively facilitates:

1. **Smart Speaker Selection** - Choose who speaks next based on discussion state
2. **Interaction Detection** - Identify questions, controversies, agreements
3. **Phase Management** - Track progress through 5 phases
4. **Consensus Building** - Summarize agreements, highlight disagreements
5. **Time Management** - Keep discussion moving, prevent stagnation
6. **Agenda Coverage Tracking** - Ensure all Phase 0 agenda items are covered ⭐ NEW

---

## Smart Speaker Selection Algorithm

### Priority Queue

```
Priority 1: Unanswered Questions (highest)
    ↓
Priority 2: Controversies Needing Mediation
    ↓
Priority 3: Experts Who Haven't Spoken (in current round)
    ↓
Priority 4: Round-Robin with Shuffled Order (lowest)
```

### Implementation

```python
def select_next_speaker(phase: str, discussion_history: list, current_round: int) -> tuple:
    """
    Returns: (expert_id, prompt_message)
    """
    
    # Priority 1: Unanswered questions
    unanswered = find_unanswered_questions(discussion_history)
    if unanswered:
        question_text, asker_id, target_id = unanswered[0]
        prompt = f"""📋 请回应未解答的问题

{asker_id} 提出了一个问题：
"{question_text}"

请从你的专业角度回应这个问题。"""
        return target_id, prompt
    
    # Priority 2: Controversies
    controversies = find_controversies(discussion_history)
    if controversies:
        topic, opposing_experts, round_num = controversies[0]
        # Find a mediator (expert not in opposing pair)
        all_experts = get_all_experts()
        mediator = random.choice([e for e in all_experts if e not in opposing_experts])
        prompt = f"""📋 请协助解决争议

议题：{topic}
存在分歧：{opposing_experts[0]} vs {opposing_experts[1]}

请从你的专业角度发表看法，帮助弥合分歧。"""
        return mediator, prompt
    
    # Priority 3: Quiet experts (haven't spoken in this round)
    quiet_experts = get_quiet_experts(discussion_history, current_round)
    if quiet_experts:
        expert = random.choice(quiet_experts)
        prompt = f"""📋 请发表你的观点

当前阶段：{phase}
当前轮次：Round {current_round}

请从你的专业角度发表看法。"""
        return expert, prompt
    
    # Priority 4: Shuffled round-robin
    return select_shuffled_next(discussion_history, current_round)
```

---

## Interaction Detection

### Finding Unanswered Questions

```python
def find_unanswered_questions(discussion_history: list) -> list:
    """
    Returns: [(question_text, asker_id, target_id), ...]
    """
    questions = []
    
    for i, message in enumerate(discussion_history):
        # Check if message contains a question
        if '?' in message.content or '？' in message.content:
            # Extract question sentences
            question_sentences = extract_questions(message.content)
            
            for question in question_sentences:
                # Check if any later message responds to this question
                has_response = False
                for later_msg in discussion_history[i+1:]:
                    if is_response_to(later_msg, message, question):
                        has_response = True
                        break
                
                if not has_response:
                    # Identify target (who should answer)
                    target = extract_question_target(question, message)
                    questions.append((question, message.expert_id, target))
    
    return questions

def extract_question_target(question: str, message) -> str:
    """
    Extract who the question is directed at.
    
    Examples:
    - "@专家 5" → "专家 5"
    - "请问 UX 专家" → "用户体验设计师"
    - "专家 5 怎么看？" → "专家 5"
    """
    patterns = [
        r'@专家\s*(\d+)',
        r'请问\s*(\S+?)(?:专家 | 老师)',
        r'专家\s*(\d+).*(?:怎么看 | 如何看 | 认为)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            return f"专家{match.group(1)}"
    
    # Default: return None (Orchestrator decides)
    return None
```

### Finding Controversies

```python
def find_controversies(discussion_history: list) -> list:
    """
    Returns: [(topic, [opposing_expert_ids], round_num), ...]
    """
    controversies = []
    
    disagreement_markers = [
        '不同意', '保留意见', '不敢苟同', '有问题', 
        '担心', '风险', '但是', '然而', '不过'
    ]
    
    for i, message in enumerate(discussion_history):
        # Check for disagreement markers
        has_disagreement = any(marker in message.content for marker in disagreement_markers)
        
        if has_disagreement:
            # Extract the topic being disputed
            topic = extract_disputed_topic(message.content)
            
            # Find the opposing expert(s)
            original_position = find_original_position(topic, discussion_history[:i])
            if original_position:
                controversies.append((
                    topic,
                    [original_position.expert_id, message.expert_id],
                    get_round_num(message)
                ))
    
    return controversies

def extract_disputed_topic(content: str) -> str:
    """
    Extract what topic is being disputed.
    
    Example:
    "我不同意专家 2 关于试点规模的建议" → "试点规模"
    """
    # Look for "关于 X 的" pattern
    match = re.search(r'关于 (.+?) 的', content)
    if match:
        return match.group(1)
    
    # Fallback: use first noun phrase after disagreement marker
    # (simplified implementation)
    return "未明确议题"
```

---

## Phase Management

### Phase State Machine

```python
class PhaseState:
    def __init__(self):
        self.current_phase = "Phase 1: 问题定义"
        self.current_round = 1
        self.phase_history = []  # Track decisions per phase
    
    def advance_round(self):
        self.current_round += 1
        
        # Check if phase should end
        if should_end_phase(self.current_phase, self.current_round):
            self.advance_phase()
    
    def advance_phase(self):
        phase_order = [
            "Phase 1: 问题定义",
            "Phase 2: 创意生成",
            "Phase 3: 分析评估",
            "Phase 4: 综合整合",
            "Phase 5: 行动计划"
        ]
        
        current_idx = phase_order.index(self.current_phase)
        if current_idx < len(phase_order) - 1:
            self.current_phase = phase_order[current_idx + 1]
            self.current_round = 1
        else:
            # All phases complete
            self.current_phase = "Complete"
```

### Phase Exit Criteria

```python
def should_end_phase(phase: str, current_round: int, discussion_history: list) -> bool:
    """
    Determine if current phase has achieved its goal.
    """
    
    # Minimum rounds check (prevent premature exit)
    if current_round < 2:
        return False
    
    if phase == "Phase 1: 问题定义":
        # Check for consensus on problem statement
        problem_statements = extract_problem_statements(discussion_history)
        agreement_rate = calculate_agreement_rate(problem_statements)
        return agreement_rate >= 0.7
    
    if phase == "Phase 2: 创意生成":
        # Check for sufficient idea count
        ideas = extract_ideas(discussion_history)
        return len(ideas) >= 20
    
    if phase == "Phase 3: 分析评估":
        # Check for top solutions identified with risk assessment
        evaluated_ideas = get_evaluated_ideas(discussion_history)
        return len(evaluated_ideas) >= 3 and all_has_risk_assessment(evaluated_ideas)
    
    if phase == "Phase 4: 综合整合":
        # Check for integrated solution
        solutions = extract_integrated_solutions(discussion_history)
        return len(solutions) >= 1 and is_truly_integrated(solutions[0])
    
    if phase == "Phase 5: 行动计划":
        # Check for actionable plan
        actions = extract_action_items(discussion_history)
        return all_has_owner_and_deadline(actions)
    
    return False
```

---

## Consensus Summarization

### Round Summary Template

```python
def generate_round_summary(phase: str, round_num: int, responses: list) -> str:
    """
    Generate a summary of the round for all experts to see.
    """
    
    agreements = find_agreements(responses)
    disagreements = find_disagreements(responses)
    emerging_themes = identify_themes(responses)
    open_questions = find_open_questions(responses)
    
    summary = f"""## {phase} - Round {round_num} 总结

### ✅ 共识领域
"""
    
    for agreement in agreements:
        summary += f"- {agreement}\n"
    
    if disagreements:
        summary += "\n### ⚠️ 关键分歧\n"
        for disagreement in disagreements:
            summary += f"- **{disagreement['topic']}**:\n"
            summary += f"  - 立场 A ({disagreement['experts_a']}): {disagreement['view_a']}\n"
            summary += f"  - 立场 B ({disagreement['experts_b']}): {disagreement['view_b']}\n"
            summary += f"  - 需要下一轮解决\n"
    
    if emerging_themes:
        summary += "\n### 🌟 涌现主题\n"
        for theme in emerging_themes:
            summary += f"- {theme}\n"
    
    if open_questions:
        summary += "\n### ❓ 开放问题\n"
        for question in open_questions:
            summary += f"- {question}\n"
    
    return summary
```

### Final Phase Summary

```python
def generate_phase_summary(phase: str, all_rounds: list) -> str:
    """
    Generate final summary when phase completes.
    """
    
    key_decisions = extract_key_decisions(all_rounds)
    open_issues = extract_open_issues(all_rounds)
    
    summary = f"""## {phase} - 阶段总结

### 📋 关键决策
"""
    
    for decision in key_decisions:
        summary += f"- ✅ {decision}\n"
    
    if open_issues:
        summary += "\n### 📌 遗留问题 (带入下一阶段)\n"
        for issue in open_issues:
            summary += f"- ⏳ {issue}\n"
    
    return summary
```

---

## Agenda Coverage Tracking ⭐

### Agenda Tracker Class

```python
class AgendaTracker:
    """
    Track coverage of all agenda items defined in Phase 0.
    """
    
    def __init__(self, agenda_from_phase0: dict):
        """
        Initialize with agenda from Phase 0.
        
        Example:
        {
            "Phase 1": ["问题陈述与范围", "用户价值与需求分层", "成功标准与约束条件"],
            "Phase 2": ["数据需求与特征工程", "数据质量与合规", ...],
            ...
        }
        """
        self.agenda = agenda_from_phase0
        self.coverage = {}
        
        for phase, topics in self.agenda.items():
            self.coverage[phase] = {
                topic: {
                    "covered": False,
                    "rounds_discussed": [],
                    "key_decisions": [],
                    "status": "not_started"  # not_started, in_progress, covered
                }
                for topic in topics
            }
    
    def mark_topic_covered(self, phase: str, topic: str, 
                          round_num: int, decisions: list = None):
        """
        Mark a topic as covered with evidence.
        """
        if phase not in self.coverage:
            raise ValueError(f"Unknown phase: {phase}")
        if topic not in self.coverage[phase]:
            raise ValueError(f"Unknown topic: {topic} in {phase}")
        
        self.coverage[phase][topic]["covered"] = True
        self.coverage[phase][topic]["rounds_discussed"].append(round_num)
        if decisions:
            self.coverage[phase][topic]["key_decisions"].extend(decisions)
        self.coverage[phase][topic]["status"] = "covered"
    
    def mark_topic_in_progress(self, phase: str, topic: str, round_num: int):
        """
        Mark a topic as being discussed.
        """
        if topic in self.coverage.get(phase, {}):
            self.coverage[phase][topic]["rounds_discussed"].append(round_num)
            self.coverage[phase][topic]["status"] = "in_progress"
    
    def get_missing_topics(self, phase: str) -> list:
        """
        Get list of topics not yet covered in this phase.
        """
        if phase not in self.coverage:
            return []
        return [
            topic for topic, data in self.coverage[phase].items()
            if not data["covered"]
        ]
    
    def get_in_progress_topics(self, phase: str) -> list:
        """
        Get list of topics currently being discussed.
        """
        if phase not in self.coverage:
            return []
        return [
            topic for topic, data in self.coverage[phase].items()
            if data["status"] == "in_progress"
        ]
    
    def is_phase_complete(self, phase: str) -> bool:
        """
        Check if all topics in this phase are covered.
        """
        if phase not in self.coverage:
            return False
        return all(
            data["covered"] for data in self.coverage[phase].values()
        )
    
    def get_coverage_summary(self, phase: str = None) -> str:
        """
        Generate coverage summary table.
        """
        if phase:
            # Single phase summary
            summary = f"### Phase {phase} 议程覆盖\n\n"
            summary += "| 议题 | 状态 | 讨论轮次 | 关键决策 |\n"
            summary += "|------|------|---------|---------|\n"
            
            for topic, data in self.coverage[phase].items():
                status_icon = {
                    "covered": "✅",
                    "in_progress": "⏳",
                    "not_started": "❌"
                }[data["status"]]
                
                rounds = ", ".join(map(str, data["rounds_discussed"])) or "-"
                decisions = ", ".join(data["key_decisions"]) or "-"
                
                summary += f"| {topic} | {status_icon} {data['status']} | {rounds} | {decisions} |\n"
            
            return summary
        else:
            # All phases summary
            all_summaries = []
            for p in sorted(self.coverage.keys()):
                all_summaries.append(self.get_coverage_summary(p))
            return "\n".join(all_summaries)
    
    def can_exit_phase(self, phase: str) -> tuple:
        """
        Determine if phase can exit.
        
        Returns: (can_exit: bool, message: str)
        """
        missing = self.get_missing_topics(phase)
        
        if not missing:
            return True, f"Phase {phase} 所有议题已覆盖，可以进入下一 Phase"
        else:
            return False, f"不能退出 Phase {phase}，以下议题未覆盖：{missing}"
```

---

### Integration with Orchestrator

```python
class Orchestrator:
    def __init__(self, agenda_from_phase0: dict):
        self.agenda_tracker = AgendaTracker(agenda_from_phase0)
        self.current_phase = "1"
        self.current_round = 1
    
    def after_each_round(self):
        """
        Called after each round to update coverage.
        """
        # Analyze what topics were discussed in this round
        discussed_topics = self.analyze_round_topics()
        
        # Update tracker
        for topic in discussed_topics:
            self.agenda_tracker.mark_topic_in_progress(
                self.current_phase, topic, self.current_round
            )
        
        # Generate coverage report
        coverage_report = self.agenda_tracker.get_coverage_summary(self.current_phase)
        
        # Send to experts
        self.broadcast(f"""## Round {self.current_round} 议程覆盖情况

{coverage_report}

### 下一轮建议
未覆盖议题：{self.agenda_tracker.get_missing_topics(self.current_phase)}
建议 Round {self.current_round + 1} 聚焦这些议题。
""")
    
    def before_phase_exit(self):
        """
        Called before transitioning to next phase.
        Must pass coverage check.
        """
        can_exit, message = self.agenda_tracker.can_exit_phase(self.current_phase)
        
        if not can_exit:
            # Block phase transition
            self.broadcast(f"""📋 协调者：不能进入下一 Phase

{message}

请先完成未覆盖议题的讨论。""")
            return False
        
        # Phase can exit
        self.broadcast(f"""✅ Phase {self.current_phase} 完成

所有议题已覆盖！进入 Phase {int(self.current_phase) + 1}""")
        self.current_phase = str(int(self.current_phase) + 1)
        self.current_round = 1
        return True
    
    def generate_final_report(self):
        """
        Generate final report with full coverage table.
        """
        report = "# 头脑风暴最终报告\n\n"
        report += "## 议程覆盖总览\n\n"
        report += self.agenda_tracker.get_coverage_summary()
        report += "\n\n## 详细讨论记录\n\n"
        # ... (rest of report)
        return report
```

---

### Coverage Check at Round End

```python
def generate_round_summary_with_coverage(phase, round_num, responses, agenda_tracker):
    """
    Generate round summary with agenda coverage check.
    """
    # Standard round summary
    summary = f"""## Phase {phase} Round {round_num} 总结

### 共识领域
...

### 关键分歧
...

### 涌现主题
...
"""
    
    # Add coverage section
    summary += "\n### 📋 议程覆盖检查\n\n"
    summary += agenda_tracker.get_coverage_summary(phase)
    
    missing = agenda_tracker.get_missing_topics(phase)
    if missing:
        summary += f"\n⚠️ **未覆盖议题**: {missing}\n"
        summary += f"建议 Round {round_num + 1} 聚焦这些议题。\n"
    
    return summary
```

---

### Example: Agenda Tracker in Action

```python
# Phase 0: Initialize agenda
agenda = {
    "1": ["问题陈述与范围", "用户价值与需求分层", "成功标准与约束条件"],
    "2": ["数据需求与特征工程", "数据质量与合规", "技术架构设计", 
          "预测模型与算法选型", "可解释性设计"],
    # ...
}

tracker = AgendaTracker(agenda)

# Phase 1 Round 1: Discussion happens
# Orchestrator analyzes: "问题陈述与范围" was discussed
tracker.mark_topic_in_progress("1", "问题陈述与范围", round_num=1)

# After Round 1
print(tracker.get_coverage_summary("1"))
# Output:
# | 议题 | 状态 | 讨论轮次 | 关键决策 |
# |------|------|---------|---------|
# | 问题陈述与范围 | ⏳ in_progress | 1 | - |
# | 用户价值与需求分层 | ❌ not_started | - | - |
# | 成功标准与约束条件 | ❌ not_started | - | - |

# Phase 1 Round 2: More discussion
# Orchestrator analyzes: "问题陈述与范围" concluded, "用户价值与需求分层" started
tracker.mark_topic_covered("1", "问题陈述与范围", round_num=2, 
                          decisions=["目标用户：K12 学生"])
tracker.mark_topic_in_progress("1", "用户价值与需求分层", round_num=2)

# Before Phase 1 exit
can_exit, message = tracker.can_exit_phase("1")
if not can_exit:
    print(message)
    # Output: "不能退出 Phase 1，以下议题未覆盖：['成功标准与约束条件']"
```

---

## Time Management

### Timeout Handling

```python
def handle_expert_timeout(expert_id: str, timeout_seconds: int = 300):
    """
    Handle case where expert doesn't respond within timeout.
    """
    
    # Option 1: Retry with reminder
    reminder = f"""⏰ 提醒：等待你的发言

专家{expert_id}，我们还在等待你的观点。

当前讨论：{get_current_topic()}

请简要发表你的看法（1-2 段即可）。"""
    
    sessions_send({
        sessionKey: expert_sessions[expert_id],
        message: reminder,
        timeout: 120  # Shorter timeout for reminder
    })
    
    # Option 2: If still no response, skip and note
    # (implement retry logic as needed)
```

### Stagnation Detection

```python
def detect_stagnation(discussion_history: list, last_n_messages: int = 10) -> bool:
    """
    Detect if discussion is going in circles.
    """
    recent = discussion_history[-last_n_messages:]
    
    # Check for repeated points
    unique_topics = set()
    for msg in recent:
        topics = extract_topics(msg.content)
        unique_topics.update(topics)
    
    # If few unique topics in recent messages, likely stagnant
    if len(unique_topics) < 3:
        return True
    
    # Check for lack of progress
    if not any_new_decisions(recent):
        return True
    
    return False

def handle_stagnation():
    """
    Intervene when discussion is stagnant.
    """
    intervention = """📋 协调者介入

我注意到讨论在同一个问题上反复。让我们：

1. 总结目前的共识点
2. 明确剩余的分歧点
3. 决定是否：
   A. 继续讨论（如果分歧很关键）
   B. 记录为开放问题，进入下一议题

请每位专家用 1-2 句话表态。"""
    
    broadcast_to_all_experts(intervention)
```

---

## Best Practices

### Do's

✅ **主动识别互动**
- "专家 1 问了专家 5 一个问题，请专家 5 回应"
- "专家 2 和专家 3 有分歧，请其他专家发表看法"

✅ **定期总结共识**
- 每轮结束后生成总结
- 明确标注"已共识"和"待解决"

✅ **灵活调整顺序**
- 不要机械地 1-2-3-4-5
- 根据讨论需要动态选择发言人

✅ **适时推进阶段**
- 达成共识后及时进入下一阶段
- 避免在已解决问题上浪费时间

### Don'ts

❌ **机械轮询**
- 不要固定顺序 1-2-3-4-5
- 不要忽略专家间的互动

❌ **被动等待**
- 不要等专家主动发言
- 要主动点名和引导

❌ **混淆 Phase 和 Round**
- Phase 是阶段（5 个）
- Round 是轮次（每阶段 2-5 轮）

❌ **过早结束讨论**
- 确保每阶段达到退出标准
- 但也要避免无意义重复

---

## Debugging

### Orchestrator Health Check

```python
def check_orchestrator_health():
    """
    Verify Orchestrator is functioning correctly.
    """
    checks = {
        'tracking_experts': len(expert_sessions) == expected_count,
        'saving_discussion': discussion_file_exists(),
        'detecting_interactions': len(detected_questions) > 0,
        'advancing_phases': current_phase in valid_phases,
    }
    
    failed = [k for k, v in checks.items() if not v]
    if failed:
        log(f"Orchestrator health issues: {failed}")
        return False
    return True
```

### Common Issues

| Issue | Symptom | Fix |
|-------|---------|-----|
| Fixed order | Experts always speak 1-2-3-4-5 | Check `select_next_speaker()` logic |
| Missed questions | Questions go unanswered | Improve `find_unanswered_questions()` |
| Phase stuck | Never advances to next phase | Check exit criteria thresholds |
| Summary missing | No round summaries | Ensure `generate_round_summary()` called |
