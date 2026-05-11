# Agenda Checklist Guide

议程清单（agenda.md）是 Deep Discussion 的核心追踪工具，采用 Markdown checklist 格式。

---

## Why Agenda Checklist?

### Problem

Without agenda checklist:
- Discussion may drift off-topic
- Some topics may be forgotten
- No clear progress visibility
- Hard to resume after breaks

### Solution

Agenda checklist provides:
- ✅ Clear progress tracking
- ✅ All topics visible upfront
- ✅ Easy to resume after breaks
- ✅ Dependency-aware ordering

---

## Agenda Checklist Format

### Basic Template

```markdown
# 议程清单 - {topic}

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. {议题标题}
- [ ] 3. {议题标题}

## Phase 2: 实现方式
- [ ] 4. {议题标题}
- [ ] 5. {议题标题}

## Phase 3: 用户落地
...

## 讨论进度
- 总议题数：{N}
- 已完成：0
- 进行中：0
```

### Mark Complete

```markdown
- [x] 1. 讨论是否要修改议程 ✅
- [x] 2. 学习规划功能的价值主张是什么？ ✅
- [ ] 3. 与自适应引擎如何协同？
```

### Update Progress

```markdown
## 讨论进度
- 总议题数：9
- 已完成：2
- 进行中：1
```

---

## First Agenda Item: Modify Agenda

**The first item must ALWAYS be "讨论是否要修改议程".**

This replaces the old Phase 0 agenda confirmation.

### Workflow

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

---

## Agenda Dependencies

**When modifying agenda, consider dependencies between topics.**

### Dependency Rules

```
问题定义 → 技术方案 → 实施计划

错误顺序：
1. 实施计划 → 2. 问题定义 → 3. 技术方案
（实施依赖于问题定义和技术方案，不能先讨论）

正确顺序：
1. 问题定义 → 2. 技术方案 → 3. 实施计划
```

### Common Dependencies

| 议题 | 依赖于 |
|------|--------|
| 技术方案 | 问题定义 |
| 实施计划 | 技术方案、资源评估 |
| 测试策略 | 技术方案 |
| 成功指标 | 问题定义、目标用户 |

### Implementation

```python
def update_agenda_with_dependencies(initial_agenda, expert_feedback):
    """
    Update agenda considering dependencies.
    
    Steps:
    1. Parse expert feedback for new/modified topics
    2. Identify dependencies between topics
    3. Topologically sort topics
    4. Group into logical Phases
    5. Return updated agenda
    """
    topics = parse_topics(initial_agenda, expert_feedback)
    dependencies = identify_dependencies(topics)
    sorted_topics = topological_sort(topics, dependencies)
    phased_agenda = group_into_phases(sorted_topics)
    return phased_agenda
```

---

## API Reference

### agenda.md Operations

```python
class AgendaManager:
    """Manage agenda.md checklist"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.topics = []
        self.completed = 0
    
    def load(self):
        """Load agenda from file"""
        pass
    
    def save(self):
        """Save agenda to file"""
        pass
    
    def mark_complete(self, topic_number: int):
        """Mark a topic as complete: - [x] {topic} ✅"""
        pass
    
    def update_progress(self):
        """Update 讨论进度 section"""
        pass
    
    def add_topic(self, phase: str, topic: str, position: int = None):
        """Add new topic to agenda"""
        pass
    
    def remove_topic(self, topic_number: int):
        """Remove topic from agenda"""
        pass
    
    def move_topic(self, topic_number: int, new_phase: str, new_position: int):
        """Move topic to new position"""
        pass
    
    def get_current_topic(self) -> tuple:
        """Get the first incomplete topic"""
        for topic in self.topics:
            if not topic.completed:
                return topic
        return None
    
    def get_progress(self) -> dict:
        """Get progress statistics"""
        return {
            "total": len(self.topics),
            "completed": self.completed,
            "in_progress": 1 if self.get_current_topic() else 0,
            "percentage": self.completed / len(self.topics) * 100
        }
```

### Usage Example

```python
# Initialize
agenda = AgendaManager("workspace/deep-discussion/{topic-slug}/agenda.md")

# Load existing agenda
agenda.load()

# Get current topic
current = agenda.get_current_topic()
print(f"Current topic: {current.number}. {current.title}")

# Mark complete after discussion
agenda.mark_complete(current.number)

# Update progress
agenda.update_progress()

# Save
agenda.save()
```

---

## Checklist Format Details

### Checkbox Syntax

```markdown
- [ ] 未完成
- [x] 已完成
```

### With Topic Number

```markdown
- [ ] 1. 议题标题
- [x] 2. 议题标题 ✅
```

### Phase Headers

```markdown
## Phase 1: 价值定位
## Phase 2: 实现方式
## Phase 3: 用户落地
```

### Progress Section

```markdown
## 讨论进度
- 总议题数：9
- 已完成：2
- 进行中：0
```

---

## Best Practices

### Do's ✅

- First item: "讨论是否要修改议程"
- Number all topics sequentially
- Group related topics into Phases
- Consider dependencies when ordering
- Update after each topic completes

### Don'ts ❌

- Don't skip topic numbering
- Don't forget to update progress
- Don't ignore dependencies
- Don't add topics mid-discussion without updating

---

## Example: Full Agenda Lifecycle

```markdown
# Before Discussion

# 议程清单 - 学习规划功能

## Phase 1: 价值定位
- [ ] 1. 讨论是否要修改议程
- [ ] 2. 学习规划功能的价值主张是什么？
- [ ] 3. 与自适应引擎如何协同？

## Phase 2: 实现方式
- [ ] 4. 时长预测技术路径？
- [ ] 5. 数据需求与特征工程？

## 讨论进度
- 总议题数：5
- 已完成：0
- 进行中：0
```

```markdown
# After Agenda Item 1 (modified agenda)

# 议程清单 - 学习规划功能

## Phase 1: 价值定位
- [x] 1. 讨论是否要修改议程 ✅
- [ ] 2. 学习规划功能的价值主张是什么？
- [ ] 3. 与自适应引擎如何协同？
- [ ] 4. 目标用户优先级？（新增）

## Phase 2: 实现方式
- [ ] 5. 时长预测技术路径？
- [ ] 6. 数据需求与特征工程？
- [ ] 7. 反馈闭环机制？（新增）

## 讨论进度
- 总议题数：7
- 已完成：1
- 进行中：0
```

```markdown
# After Topic 2

- [x] 1. 讨论是否要修改议程 ✅
- [x] 2. 学习规划功能的价值主张是什么？ ✅
- [ ] 3. 与自适应引擎如何协同？
...

## 讨论进度
- 总议题数：7
- 已完成：2
- 进行中：0
```

---

## Testing

```python
def test_agenda_manager():
    # Create test agenda
    agenda = AgendaManager("/tmp/test-agenda.md")
    agenda.topics = [
        Topic(1, "讨论是否要修改议程", "Phase 1"),
        Topic(2, "价值主张", "Phase 1"),
        Topic(3, "技术路径", "Phase 2"),
    ]
    
    # Test get current
    current = agenda.get_current_topic()
    assert current.number == 1
    
    # Test mark complete
    agenda.mark_complete(1)
    agenda.update_progress()
    assert agenda.completed == 1
    
    # Test get current again
    current = agenda.get_current_topic()
    assert current.number == 2
    
    print("All tests passed!")
```
