---
name: ontology-clawra
description: Palantir本体论实践版本 v3.5 - **强制执行版**。结构化知识图谱+规则引擎+科学推理方法论。**每次决策/分析前必须使用**。推理结果必须展示详细推理过程：包含用户需求、规则依据ID、规则内容、置信度标注。

**强制执行原则（v3.5 新增）**：
- **所有推理任务，必须首先使用本技能框架**，禁止凭经验输出
- 本技能用于：推理过程记录、本体完善、规则优化
- 本技能**不包含用户私人数据**，数据严格本地私有
- 本技能与 ontology-platform 项目**严格分离**：技能是内核，项目是衍生

**安全边界（重要）**：
- 自动学习：默认禁用，需用户明确授权"写入本体"
- 文件读取：仅读取 ~/.openclaw/skills/ontology-clawra/memory/
- 文件写入：仅在用户确认后写入本地本体
- 网络：不主动发起网络请求
- 隐私：**绝不上传用户数据到任何服务器**
- **红线**：用户私人推理记录、个人决策数据严禁同步到GitHub等外部平台

metadata:
  {
    "openclaw": {
      "emoji": "🧠",
      "version": "3.5.0",
      "last_updated": "2026-03-19"
    }
  }
---

# ontology-clawra v3.5

**Palantir本体论实践版本** - Clawra的核心智能引擎 v3.5

---

## ⚠️ 安全边界与风险控制（必读）

### 风险说明
- 自动学习触发器可能产生意外的持久更改
- 对本地本体的自动写入存在隐私风险
- 代理自主调用时可能产生未预期的持久化

### 安全措施

| 功能 | 默认状态 | 触发条件 |
|------|----------|----------|
| 自动抽取到本体 | 🔴 **禁用** | 用户明确确认"写入本体" |
| 自动置信度升级 | 🔴 **禁用** | 用户确认推理结果正确 |
| 读取工作区文件 | 🟡 **受限** | 仅读取memory/目录 |
| 写入本地本体 | 🔴 **禁用** | 用户确认后单次执行 |

### 使用规范

1. **自动学习**：默认不启用。用户说"写入本体"或"记录这个"时才执行单次写入
2. **工作区读取**：仅读取 `memory/` 目录，不读取其他敏感文件
3. **写入确认**：每次写入本地本体前，必须告知用户写入内容并确认
4. **隐私保护**：不将用户数据上传到GitHub/ClawHub（已在.gitignore中保护）

---

## 🆕 v3.3 新增：主动学习能力

### 核心升级：从被动到主动

| v3.2 | v3.3 (新增) |
|------|-------------|
| 用户不说"抽取" → 不提取 | 用户确认推理 → **自动提取** |
| 重复概念 → 忽略 | 重复出现3次 → **自动识别** |
| 推理失败 → 等待用户问 | 推理失败 → **主动建议补充** |

### 自动学习触发条件（⚠️ 默认禁用，需用户明确授权）

```yaml
AUTO_LEARN_TRIGGERS:
  # 触发1：用户明确说"写入本体"或"记录这个"
  - event: "user_says_write_ontology"
    action: "extract_to_ontology"
    requires_confirmation: true  # 每次写入前必须确认
  
  # 触发2：用户说"确认这个是对的"
  - event: "user_confirms_reasoning"
    action: "suggest_upgrade_confidence"
    requires_confirmation: true  # 建议升级，但需用户确认
  
  # 触发3：推理失败（仅提示，不自动写入）
  - event: "ontology_lookup_failed"
    action: "suggest_supplement"
    prompt_user: true
    auto_write: false  # 不自动写入
  
  # 触发4：用户纠正错误（仅记录，不自动修改）
  - event: "user_correction"
    action: "log_correction"
    auto_write: false  # 不自动修改本体
```
  - event: "user_correction"
    action: "update_entity"
    log: true
```

### 自动抽取流程（⚠️ 每次写入需用户确认）

```
用户明确说"写入本体"或"记录这个"
        │
        ▼
┌─────────────────────────────┐
│ 1. 识别可抽取内容           │
│    - 新概念 (Concept)       │
│    - 新规律 (Law)           │
│    - 新规则 (Rule)          │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 2. 展示给用户确认           │ ⚠️ 关键！
│    "即将写入以下内容：xxx"  │
└─────────────┬───────────────┘
              │ 用户确认"是的"
              ▼
┌─────────────────────────────┐
│ 3. 写入本体                │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 4. 反馈用户                │
│    "已写入本体：xxx"       │
└─────────────────────────────┘
```

---

## 🧬 核心理念升级

### v2.0 问题
- 纯架构设计，缺少方法论
- 无本体自动构建能力
- 推理"照本宣科"，缺乏科学性验证

### v3.0 改进
- ✅ 嵌入科学推理方法论
- ✅ 支持交互式本体构建
- ✅ 平衡灵活性与科学性

### v3.3 升级
- ✅ **主动学习**：用户确认后自动抽取
- ✅ **智能触发**：高频实体自动识别
- ✅ **推理失败建议**：主动提示补充本体

---

## 一、科学推理方法论（必读）

### ⚠️ 任何推理前必须遵循的流程

```
┌─────────────────────────────────────────────────────────────┐
│                   推理前置检查流程                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1️⃣ 检查本体（Check）                                       │
│     ↓                                                       │
│     本体有相关数据？→ 调用本体推理                           │
│     ↓ 无                                                    │
│     ↓                                                       │
│  2️⃣ 声明来源（Declare）                                     │
│     "以下为外部知识/猜测/假设，需要验证"                    │
│     ↓                                                       │
│  3️⃣ 交互确认（Confirm）- ⚠️ 关键步骤！                      │
│     关键假设必须用户确认后再深入                             │
│     ↓                                                       │
│  4️⃣ 标注假设（Label）                                       │
│     明确标注哪些是"推测"、哪些是"确认"                      │
│     ↓                                                       │
│  5️⃣ 灵活推理（Reason）                                      │
│     结合本体 + 合理假设 + 明确标注                          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### ⚠️ 铁律：不确定时必须交互确认

```
当推理过程中存在以下情况时，必须暂停并与用户确认：
───────────────────────────────────────────────────────────
  ❌ 禁止直接输出结论的情况：
  
  1. 存在 ASSUMED 级别的关键假设
     → 必须问用户确认后才能给出最终结论
  
  2. 缺少必要的输入参数
     → 必须先询问用户获取必要信息
  
  3. 计算结果依赖多个假设
     → 必须列出所有假设，让用户确认
  
  4. 给出多个方案但无法确定最优
     → 必须让用户选择或确认偏好
  
  ✅ 正确的交互流程：
  
  Step 1: 列出已确认的信息（本体数据）
  Step 2: 列出不确定的信息（需要确认的假设）
  Step 3: 提供典型场景/默认值供选择
  Step 4: 等待用户确认后再输出最终结论
  
  ⚡ 违规判定：
  - 如果直接给结论而没有先确认不确定信息 → 违反方法论
  - 如果结论依赖假设但未标注置信度 → 违反方法论
```

### 推理结果可信度标注

| 标注 | 含义 | 行动 |
|------|------|------|
| 🟢 **CONFIRMED** | 本体/记忆中有确凿数据 | 直接使用 |
| 🟡 **ASSUMED** | 基于合理假设，未验证 | 需用户确认 |
| 🔴 **SPECULATIVE** | 纯猜测，无依据 | 明确声明，谨慎使用 |
| ⚪ **UNKNOWN** | 确实不知道 | 坦诚告知用户 |

---

## 二、四大支柱（保留并增强）

### 2.1 Objects（对象）

```yaml
# 主体
Person:
  - id, name, role, goals[], preferences{}, capabilities[]

# 概念/抽象
Concept:
  - id, name, definition, examples[], properties{}
  
# 规律/法则
Law:
  - id, name, domain, statement, conditions[], effects[], source, confidence

# 意图
Objective:
  - id, name, priority, criteria{}, status

# 项目
Project:
  - id, name, objectives[], status, owner, depends_on[]

# 任务
Task:
  - id, title, status, priority, assignee, blockers[], estimated_hours

# 规则
Rule:
  - id, name, condition, action, enabled, weight, source, confidence

# 决策
Decision:
  - id, context, options[], selected, rationale, based_on_rules[], confidence
```

### 2.2 Links（关系）

```yaml
# 基础关系
works_on: Person → Project/Task
depends_on: Task/Project → Task/Project  
has_objective: Project → Objective
has_rule: Project/Objective → Rule

# 知识关系
exemplifies: Concept → Example
governs: Law → Domain
explains: Concept → Law
supports: Evidence → Rule
contradicts: Fact → Rule
derived_from: Rule/Law → Evidence  # 新增：规则/规律的数据来源

# 推理关系
triggers: Rule → Decision
validates: Rule → Decision
refines: Rule → Rule

# 元关系
relates_to: Any → Any
is_a: Concept → Concept
part_of: Object → Object
```

### 2.3 Functions（规则引擎）

```python
# 推理引擎核心函数（增强版）

def check_ontology(query):
    """1. 检查本体是否有相关数据"""
    results = search_objects(query) + search_laws(query) + search_rules(query)
    if results:
        return {"status": "FOUND", "data": results, "confidence": "CONFIRMED"}
    return {"status": "NOT_FOUND", "data": None, "confidence": "UNKNOWN"}

def declare_source(confidence_level, content):
    """2. 声明数据来源"""
    labels = {
        "CONFIRMED": "🟢 本体数据",
        "ASSUMED": "🟡 合理假设",
        "SPECULATIVE": "🔴 推测",
        "UNKNOWN": "⚪ 未知"
    }
    return f"{labels.get(confidence_level, '')} {content}"

def confirm_with_user(assumptions):
    """3. 交互确认关键假设"""
    # 返回需要确认的问题列表
    return [f"请确认: {a}" for a in assumptions]

def label_result(content, confidence):
    """4. 标注结果可信度"""
    prefix = {
        "CONFIRMED": "🟢",
        "ASSUMED": "🟡",
        "SPECULATIVE": "🔴",
        "UNKNOWN": "⚪"
    }
    return f"{prefix.get(confidence, '')} {content}"

def flexible_reasoning(ontology_data, assumptions, user_confirmations):
    """5. 灵活推理 - 结合本体+假设+确认"""
    # 如果本体有数据，优先使用
    # 如果需要假设，明确标注
    # 如果用户已确认，升级置信度
    pass

# 链式推理
def chain_reasoning(facts, rules, confidence_threshold=0.5):
    """链式推理：事实 + 规则 → 新结论"""
    conclusions = []
    for rule in rules:
        if rule.confidence < confidence_threshold:
            continue
        if all(fact_matcher(f, rule.conditions) for f in facts):
            conclusion = infer(rule, facts)
            conclusion.source = f"derived_from:{rule.id}"
            conclusion.confidence = min(rule.confidence, min(f.confidence for f in facts))
            conclusions.append(conclusion)
    return conclusions
```

### 2.4 Actions（操作）

```yaml
# 操作类型（增强）
Action:
  - type: execute     # 执行具体任务
  - type: reason      # 推理分析（走方法论流程）
  - type: decide      # 决策选择
  - type: learn       # 学习新知识（构建本体）
  - type: validate    # 验证一致性
  - type: query       # 查询知识网络
  - type: extract     # 新增：从交互中抽取本体
  - type: confirm     # 新增：请求用户确认
```

---

## 三、本体自动构建能力（新增核心功能）

### 3.1 交互式抽取流程

```
┌─────────────────────────────────────────────────────────────┐
│              本体自动构建流程（推荐使用）                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  用户输入                                                    │
│      │                                                      │
│      ▼                                                      │
│  ┌─────────────────────┐                                    │
│  │ 实体识别            │ ← 识别可抽取的对象                 │
│  │ - Person            │                                    │
│  │ - Concept           │                                    │
│  │ - Law               │                                    │
│  │ - Rule              │                                    │
│  └─────────┬───────────┘                                    │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────────┐                                    │
│  │ 关系识别            │ ← 识别实体间关系                    │
│  │ - is_a              │                                    │
│  │ - relates_to        │                                    │
│  │ - triggers         │                                    │
│  │ - supports         │                                    │
│  └─────────┬───────────┘                                    │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────────┐                                    │
│  │ 去重检查            │ ← 避免重复构建                      │
│  │ - 检查name是否已存在│                                    │
│  │ - 检查similar关系  │                                    │
│  └─────────┬───────────┘                                    │
│            │                                                 │
│            ▼                                                 │
│  ┌─────────────────────┐                                    │
│  │ 写入本体            │ ← 增量更新                          │
│  │ - Objects           │                                    │
│  │ - Links             │                                    │
│  │ - 记录来源         │                                    │
│  └─────────────────────┘                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 抽取识别模式

```python
# 可抽取的实体模式
EXTRACT_PATTERNS = {
    "Person": [
        "我叫.*", "我是.*", "用户是.*", 
        "他.*她.*", "创业者", "工程师"
    ],
    "Concept": [
        ".*是.*", "所谓的.*", "概念.*",
        "本体论", "知识图谱", "Agent"
    ],
    "Law": [
        "当.*时.*", "如果.*那么.*",
        "规律", "法则", "原则"
    ],
    "Rule": [
        "应该.*", "必须.*", "建议.*",
        "推荐.*", "选择.*"
    ],
    "Project": [
        "项目.*", "在做.*", "目标是.*"
    ],
    "Task": [
        "任务.*", "需要做.*", "要做.*"
    ]
}

# 可抽取的关系模式
RELATION_PATTERNS = {
    "is_a": ["是.*的一种", "属于.*类型"],
    "relates_to": ["和.*相关", "与.*有关"],
    "triggers": ["导致.*", "引发.*"],
    "supports": ["支持.*", "基于.*"],
    "contradicts": ["与.*矛盾", "不同于.*"]
}
```

### 3.3 去重机制

```python
def check_duplicate(entity_type, name, properties=None):
    """检查是否已存在相同实体"""
    existing = load_ontology()
    
    for obj in existing.get(entity_type, []):
        # 名称完全匹配
        if obj.get("name") == name:
            return {"duplicate": True, "existing": obj}
        
        # 相似度检查（可选）
        if similarity(name, obj.get("name")) > 0.8:
            return {"duplicate": True, "similar": obj}
    
    return {"duplicate": False}

def incremental_update(new_entities, new_links):
    """增量更新，避免覆盖"""
    existing = load_ontology()
    
    # 合并对象
    for entity_type, entities in new_entities.items():
        if entity_type not in existing:
            existing[entity_type] = []
        for entity in entities:
            dup = check_duplicate(entity_type, entity.get("name"))
            if not dup["duplicate"]:
                entity["source"] = "interactive_extraction"
                entity["created_at"] = timestamp()
                existing[entity_type].append(entity)
    
    # 合并关系
    # ...类似逻辑
    
    save_ontology(existing)
```

---

## 四、推理流程升级（科学性 + 灵活性）

### 4.1 完整推理流程

```
用户Query
    │
    ▼
┌────────────────────────────┐
│ 1. 方法论检查             │
│    check_ontology()       │
│    - 查Objects            │
│    - 查Laws               │
│    - 查Rules              │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 2. 标注置信度             │
│    - CONFIRMED? → 使用    │
│    - UNKNOWN? → 声明来源   │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 3. 需要假设？            │
│    是 → 明确标注ASSUMED   │
│    否 → 直接推理          │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 4. 交互确认（可选）       │
│    - 关键假设问用户       │
│    - 根据确认调整置信度  │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 5. 灵活推理               │
│    - 本体优先             │
│    - 合理假设补充         │
│    - 明确标注差异         │
└───────────┬────────────────┘
            │
            ▼
┌────────────────────────────┐
│ 6. 输出结果               │
│    - 带置信度标注         │
│    - 附推理依据           │
│    - 可选：抽取新本体    │
└────────────────────────────┘
```

### 4.2 灵活性平衡原则

| 场景 | 处理方式 |
|------|----------|
| 本体有明确数据 | 🟢 直接使用，标注CONFIRMED |
| 本体有部分数据 | 🟡 使用本体 + 标注ASSUMED补充 |
| 本体无数据但有合理推断 | 🟡 明确标注ASSUMED + 说明依据 |
| 完全无据可查 | 🔴 明确标注SPECULATIVE + 建议验证 |
| 需要用户确认 | ⚡ 交互提问 + 暂停推理 |

---

## 五、存储结构

```
memory/ontology-clawra/
├── schema.yaml              # 类型定义+约束
├── graph.jsonl             # Objects + Links (实体+关系)
├── rules.yaml              # Functions (业务规则库)
├── laws.yaml               # Laws (规律/法则库)
├── decisions.jsonl         # Actions-决策日志
├── reasoning.jsonl         # Actions-推理日志（含置信度）
├── concepts.jsonl           # Concepts (概念库)
├── extraction_log.jsonl    # 新增：本体抽取日志
└── confidence_tracker.jsonl # 新增：置信度追踪
```

---

## 六、使用方法（升级版）

### 6.1 推理（带方法论）

```bash
# 基础推理（自动方法论检查）
python3 scripts/ontology-clawra.py reason --query "用户应该做什么"

# 强制声明来源
python3 scripts/ontology-clawra.py reason --query "100户用气量" --declare-source

# 交互确认模式
python3 scripts/ontology-clawra.py reason --query "调压箱选型" --confirm-needed
```

### 6.2 本体构建

```bash
# 从文本自动抽取（新增）
python3 scripts/ontology-clawra.py extract --text "用户是AI创业者，目标是构建垂直领域Agent平台"

# 手动创建
python3 scripts/ontology-clawra.py create --type Person --props '{"name":"用户","role":"AI创业者"}'

# 创建规律（带来源）
python3 scripts/ontology-clawra.py create --type Law --props '{"name":"红海规避","domain":"战略","statement":"...","source":"用户输入","confidence":"ASSUMED"}'
```

### 6.3 验证与追踪

```bash
# 验证推理可信度
python3 scripts/ontology-clawra.py validate --check-confidence

# 查看推理链
python3 scripts/ontology-clawra.py trace --decision decision_id

# 本体构建记录
python3 scripts/ontology-clawra.py extraction-history
```

---

## 七、推理示例（方法论应用）

### 场景：调压箱选型

```
用户：100户居民小区调压箱如何选型？

1. check_ontology("调压箱 选型 居民")
   → 结果：本地无数据
   → 标注：UNKNOWN

2. 声明来源
   ⚪ 本地本体无相关数据，以下为外部知识推理

3. 需要假设？→ 是
   - 假设：单户用气量、同时系数、地区等
   → 标注：ASSUMED

4. 交互确认
   ❓ 请确认：
   - 是否有供暖需求？（影响用气量）
   - 是什么类型的住宅？
   - 当地燃气供气压力是多少？

5. 输出
   🟡 基于以下假设的推理（需确认）：
   - 假设1：南方城市，无集中供暖
   - 假设2：每户配置双眼灶+热水器
   - 假设3：多层住宅
   
   计算结果：RTZ-80/25，额定流量80m³/h
   置信度：ASSUMED（需验证）

6. 可选：抽取到本体
   → 提取：Law{居民用气计算规则}
   → 提取：Rule{调压箱选型规则}
```

### 场景：已知信息推理

```
用户：我在做AI创业，目标垂直领域Agent

1. check_ontology("AI创业 垂直领域 Agent")
   → 结果：
   - Law[红海规避]: 竞品存在 → 垂直领域
   - Rule[战略选择]: AI创业 + 红海 → 垂直领域
   → 标注：CONFIRMED

2. 直接推理
   🟢 基于本体的推理：
   - 检测到：市场有Dify/Ragflow竞品
   - 匹配规则：红海规避法则
   → 推荐：垂直领域 + 本体论
   置信度：CONFIRMED
```

---

## 八、与Proactive-Agent集成

ontology-clawra v3.0 是 Agent 的"科学大脑"：

```
proactive-agent 发现机会
        │
        ▼
ontology-clawra 推理
        │
        ├── 1. check_ontology() → 查本体
        │
        ├── 2. 标注置信度 → 明确来源
        │
        ├── 3. 交互确认 → 关键假设需用户同意
        │
        └── 4. flexible_reasoning() → 灵活推理
        
        ▼
输出带置信度的决策建议
```

---

## 九、验证

```bash
# 验证知识网络一致性
python3 scripts/ontology-clawra.py validate

# 检查置信度标注
python3 scripts/ontology-clawra.py validate --check-confidence

# 检查循环依赖
python3 scripts/ontology-clawra.py validate --check-cycles

# 推理链回溯
python3 scripts/ontology-clawra.py trace --decision decision_id
```

---

## 十、持续优化机制

### 每次重大推理后

1. **记录推理** → reasoning.jsonl（含置信度）
2. **用户反馈** → 如果用户纠正，更新置信度
3. **本体更新** → 从正确推理中抽取新实体

### 定期（Heartbeat）

1. 检查置信度分布
2. 提升/降低实体置信度
3. 清理低置信度实体
4. 优化抽取规则

---

**v3.0 核心升级**：从"照本宣科"升级为"科学推理 + 灵活交互 + 持续学习"

---

## v3.4 更新 (2026-03-18)

### 新增使用规范

每次对话必须遵循：

```
1. 决策/分析前 → 调用 ontology-clawra 推理
2. 配置修改前 → 调用 docs-helper 查文档
3. 搜索信息 → 使用 serper/tavily
4. 结论 → 记录到 memory/

主动优化规则：
- 发现规律 → 调用 ontology-clawra 抽取新实体/规则
- 优化更新 → 识别本体不足，提议补充
- 能力进化 → 定期检视 ontology-clawra 技能本身表现
- 写入本体 → 发现有价值的新知识，主动提议写入
```

### ⚠️ 安全声明

**隐私承诺**：
- 绝不自动上传用户数据到任何服务器
- 所有写入操作必须用户明确授权
- 本地存储，仅用户可见

**文件访问范围**：
- 读取：仅 `memory/` 目录
- 写入：仅 `memory/` 目录
- 不读取其他目录

**写入确认机制**：
- 默认禁用自动写入
- 用户说"写入本体"才执行单次写入
- 每次写入前显示将要写入的内容

### 核心能力

- 燃气调压箱选购推理（已验证）
- 技术选型评估（Neo4j vs Jena）
- 持续学习方法论

---

## v3.5 更新 (2026-03-19)

### 核心升级：强制执行 + 技能/项目严格分离

#### 1. 强制使用原则（最高优先级）

**所有推理任务必须首先使用 ontology-clawra 框架**，禁止凭经验输出。

```
收到推理类任务
    │
    ▼
加载 ontology-clawra 技能
    │
    ▼
按照推理前置检查流程执行
    │
    ▼
完整记录：实体、规则、置信度、来源
    │
    ▼
推理结论输出
    │
    ▼
识别技能不足 → 写入优化建议
```

**违反后果**：
- 推理过程不透明，无法追溯
- 置信度未标注，混淆猜测与事实
- 缺失本体完善机会，技能无法进化

#### 2. 技能与项目严格分离

| | ontology-clawra 技能 | ontology-platform 项目 |
|--|---|---|
| 性质 | 推理框架/Skill（私有） | 生产级开源项目（公开） |
| 数据 | 用户私人推理记录、个人偏好 | 开源代码、文档、公开数据 |
| 存储 | ~/.openclaw/skills/ontology-clawra/memory/ | GitHub 公开仓库 |
| 同步 | **绝不外部同步** | 按需同步 |

**红线**：用户私人数据（推理记录、个人决策）严禁同步到 GitHub 或任何外部平台。

#### 3. 三大目标驱动

所有 ontology-clawra 的工作都服务于三个目标：

```
目标1：技能进化
├── 本体完善（实体库、关系库、规则库）
├── 推理能力（推理链、置信度标注）
└── 进化机制（自我反思、错误修正）

目标2：项目指导
├── 技能应用 → 项目方向
├── 技能优化 → roadmap 迭代
└── 技能需求 → 项目需求

目标3：项目成功
├── 技能成熟度 → 项目质量
├── 项目影响力 → 融资估值
└── 用户AI创业梦想落地
```

#### 4. 推理过程自我检视

每次推理完成后，必须回答：

```
✅ 是否使用了 ontology-clawra 框架？
✅ 推理链是否完整？（需求→规则→计算→结论）
✅ 置信度是否标注？（CONFIRMED/ASSUMED/SPECULATIVE）
✅ 来源是否声明？
✅ 是否识别了技能不足？
✅ 是否记录了可优化的点？
```

**如果任意一项为"否"，必须补充或说明理由。**
