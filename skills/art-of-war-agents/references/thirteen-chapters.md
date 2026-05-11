# The Thirteen Chapters — Detailed Agent Mappings

## 1. 始计篇 (Laying Plans)

**Original**: Before war, calculate victory probability using Five Constants and Seven Metrics.

**Agent Application**: Task Assessment Framework

### Five Constants (五事)
| 常 | 问题 | Agent 决策 |
|---|------|----------|
| 道 | 这个任务值得做吗？ | 不值得→不做 |
| 天 | 现在是合适的时机吗？ | 否→等待 |
| 地 | 有足够的上下文/数据吗？ | 否→先收集 |
| 将 | 有合适的 agent 吗？ | 否→找替代方案 |
| 法 | 流程清晰吗？ | 否→先规划 |

### Seven Metrics (七计)
Compare your position vs. the task's "resistance":
- 主孰有道？→ 任务目标清晰度
- 将孰有能？→ Agent 能力匹配度
- 天地孰得？→ 环境/工具准备度
- 法令孰行？→ 流程可执行性
- 兵众孰强？→ 资源充足度
- 士卒孰练？→ Agent 熟练度
- 赏罚孰明？→ 反馈机制

**Score <4/7**: Don't deploy. Plan first.

---

## 2. 作战篇 (Waging War)

**Original**: War is expensive; speed is essential. Never prolong.

**Agent Application**: Token Cost Management

### Key Principles
- **日费千金**: Agent runs cost money. Track it.
- **速战速决**: Set iteration limits. Force conclusions.
- **胜久则钝兵挫锐**: Long runs = degraded quality + wasted tokens

### Practical Rules
1. **预算先行**: Before starting, estimate token cost
2. **设限**: Max 5 iterations per agent
3. **因粮于敌**: Reuse existing outputs; don't regenerate
4. **务食于敌**: Use external tools (search, code) vs. internal knowledge

### Red Flags
- Agent on iteration 4+ with no clear progress
- Same question asked twice
- Output getting longer but not better

**Action**: Intervene, redirect, or terminate.

---

## 3. 谋攻篇 (Attack by Stratagem)

**Original**: Best to attack enemy's strategy, not their army. Win without fighting.

**Agent Application**: Planning Hierarchy

### Hierarchy of Solutions
```
1. 上策：消除任务 (Eliminate the task)
   - Can this be automated?
   - Can this be skipped?
   - Can someone else do it?

2. 中策：单 agent 解决 (Single agent)
   - Focused, clear instructions
   - One iteration if possible

3. 下策：多 agent 协作 (Multi-agent)
   - Only when truly necessary
   - High coordination cost
```

### 全胜思维 (Complete Victory)
- Don't just complete the task — complete it so well it never comes back
- Build reusable outputs (templates, scripts, documentation)
- Invest in prevention, not just cure

### Avoid Siege Warfare
**攻城之法为不得已**: Throwing more agents at a poorly-defined problem is siege warfare.

**Better**: Step back, redefine the problem, find the weak point.

---

## 4. 军形篇 (Tactical Dispositions)

**Original**: First make yourself invincible, then wait for enemy to be vulnerable.

**Agent Application**: Defense First

### 先为不可胜 (Make Yourself Undefeatable)
Before deploying agents:
- [ ] Version control in place?
- [ ] Can I undo changes?
- [ ] Is there validation?
- [ ] What's the rollback plan?
- [ ] Are there guardrails?

### 以待敌之可胜 (Wait for Opportunity)
- Don't force agent deployment
- Wait for clear opportunity (well-defined task, right agent available)
- Patience > premature action

### Security Categories
| 风险 | 防御措施 |
|------|---------|
| 幻觉 (Hallucination) | 交叉验证，引用来源 |
| 过时信息 | 指定时间范围，用搜索工具 |
| 工具故障 | 有 fallback 方案 |
| 输出错误 | 自动化测试/验证 |
| 泄露敏感信息 | 过滤/脱敏 |

---

## 5. 兵势篇 (Energy/Impetus)

**Original**: Create momentum so strong it's unstoppable. Combine orthodox and unorthodox.

**Agent Application**: Multi-Agent Momentum

### 势 (Shi) — Momentum
Build configurations where each output naturally triggers the next:

```
Research → Synthesis → Critique → Polish → Validate
   ↓          ↓           ↓         ↓         ↓
 Raw      Structured    Gaps     Refined   Certified
 Data       Draft       Found     Final     Output
```

### 奇正 (Orthodox + Unorthodox)
| 正 (Orthodox) | 奇 (Unorthodox) |
|--------------|-----------------|
| Standard workflows | Creative combinations |
| Proven agents | Experimental approaches |
| Reliable output | Breakthrough potential |
| 70% of tasks | 30% of tasks |

**Rule**: Never rely on 奇 alone. Always have 正 as backup.

### 节 (Timing/Rhythm)
- Release agents in waves, not all at once
- Let each wave complete before committing the next
- Adjust rhythm based on results

---

## 6. 虚实篇 (Weak Points & Strong)

**Original**: Avoid enemy strength, attack weakness. Control where battle happens.

**Agent Application**: Strategic Targeting

### 避实击虚 (Avoid Strength, Attack Weakness)
- Don't use agents for tasks requiring human nuance
- Use agents for bulk work, pattern recognition, first drafts
- You handle: judgment, creativity, relationship management
- Agent handles: research, formatting, iteration, validation

### 致人而不致于人 (Control, Don't Be Controlled)
- **You** set the focus, not the agent
- **You** define success, not the agent
- **You** decide when to stop, not the agent

### Identify Critical Bottlenecks
```
Task: Write market analysis report
├─ Data collection (agent excels) ✓
├─ Pattern recognition (agent excels) ✓
├─ Strategic insight (human needed) ⚠
└─ Executive presentation (human needed) ⚠

Deploy agent for ✓, handle ⚠ yourself
```

---

## 7. 军争篇 (Maneuvering)

**Original**: The longest path may be fastest. Appear weak when strong.

**Agent Application**: Indirect Approaches

### 以迂为直 (Indirect = Direct)
Sometimes the "detour" is faster:
- 10 min planning saves 50 min of agent iterations
- Background research prevents wrong-direction work
- Validation step avoids redoing everything

### 示弱 (Appear Weak)
- Let agent explore naive approaches first
- Then guide with "What about X?" instead of dictating
- Agent discovers the insight → more buy-in

### 分合 (Divide and Combine)
- Split complex tasks into focused subtasks
- Each subtask → one focused agent
- Combine outputs systematically

---

## 8. 九变篇 (Nine Variations)

**Original**: Adapt to changing conditions. Know when to vary from standard rules.

**Agent Application**: Flexibility

### Five Dangerous Agent Faults
|  faults | 表现 | 应对 |
|--------|------|------|
| 必死 (Reckless) | 快速迭代但不思考 | 强制暂停，要求解释 |
| 必生 (Cowardly) | 过度谨慎，永不完成 | 设 deadline，强制输出 |
| 忿速 (Quick temper) | 与用户争辩 | 冷静重申目标 |
| 廉洁 (Over-optimizing) | 追求完美忘记目标 | 提醒"完成>完美" |
| 爱民 (People-pleasing) | 从不质疑错误指令 | 鼓励提出反对意见 |

### 将在外，君命有所不受
Give agents autonomy within boundaries:
- Clear goal + constraints
- Freedom on how to achieve
- Check-in points, not micromanagement

---

## 9. 行军篇 (Marching)

**Original**: Read environmental signals. Know terrain before moving.

**Agent Application**: Signal Reading

### 相敌 (Observing the Enemy/Agent)
| 信号 | 含义 | 应对 |
|------|------|------|
| 重复提问 | 指令不清或缺信息 | 补充上下文 |
| 输出变长 | 可能在填充而非思考 | 要求简洁 |
| 过度自信 | 可能幻觉 | 要求来源 |
| 回避问题 | 能力边界 | 换方法或人工 |
| 循环论证 | 卡住了 | 介入重定向 |

### 地形识别 (Terrain Recognition)
- **轻地**: 简单任务 → 快速通过
- **重地**: 复杂任务 → 充分准备
- **困地**: 信息不足 → 先探索

---

## 10. 地形篇 (Terrain)

**Original**: Different terrains require different strategies.

**Agent Application**: Task Classification

### Six Terrains
| 地形 | 特征 | 策略 |
|------|------|------|
| 通形 | 清晰、直接 | 标准流程，快速执行 |
| 挂形 | 易陷入细节 | 时间限制，强制输出 |
| 支形 | 信息不足 | 先收集，后决策 |
| 隘形 | 高约束 | 精确指令，严格验证 |
| 险形 | 高风险 | 多重验证，保守 |
| 远形 | 长链条 | 分阶段，检查点 |

---

## 11. 九地篇 (Nine Grounds)

**Original**: Different commitment levels for different situations.

**Agent Application**: Resource Allocation

### Commitment Matrix
| 地 | 任务类型 | Agent 投入 | 示例 |
|---|---------|----------|------|
| 散地 | 日常 | 轻量 | 邮件草稿、格式转换 |
| 轻地 | 低价值 | 最小 | 快速搜索、简单总结 |
| 争地 | 时间敏感 | 优先 | 竞品分析、紧急报告 |
| 交地 | 协作 | 明确接口 | 跨团队文档 |
| 衢地 | 多目标 | 平衡 | 产品规划 |
| 重地 | 高价值 | 充分 | 投资决策、战略分析 |
| 圮地 | 信息不足 | 探索先行 | 新市场研究 |
| 围地 | 受约束 | 创造性 | 预算有限方案 |
| 死地 | 背水一战 | 全力 | 危机处理 |

---

## 12. 火攻篇 (Fire Attack)

**Original**: Use fire (powerful weapons) at the right time, with preparation.

**Agent Application**: Tool Usage

### Five Fires
| 火 | 工具类型 | 使用时机 |
|---|---------|---------|
| 人火 | 用户提供 | 已有数据/文档 |
| 积火 | 缓存资源 | 之前的输出 |
| 辎火 | API/搜索 | 需要外部数据 |
| 库火 | 代码执行 | 计算、处理 |
| 队火 | 多 agent | 复杂协作 |

### 用火原则
- **行必有备**: Have fallback if tool fails
- **发火有时**: Right timing (not too early, not too late)
- **发火在早**: Use tools early to validate direction
- **小心火烛**: Tool outputs need validation too

---

## 13. 用间篇 (Spies)

**Original**: Intelligence is everything. Use multiple sources, cross-verify.

**Agent Application**: Information Strategy

### Five Intelligence Sources
| 间 | Agent 应用 | 可信度 |
|---|-----------|--------|
| 因间 | 现有文档/代码 | 高 |
| 内间 | 内部系统访问 | 高 |
| 反间 | 交叉验证多源 | 最高 |
| 死间 | 一次性搜索 | 中 |
| 生间 | 持续监控 | 高 |

### 三反原则 (Triple Verification)
Never trust a single source:
1. Agent's internal knowledge
2. External search/API
3. User-provided context

If all 3 align → high confidence
If they diverge → investigate why

### 先知原则 (Know First)
Gather intelligence BEFORE making decisions:
- Research before planning
- Validate before committing
- Test before deploying

---

## Summary Card

```
┌─────────────────────────────────────────────────────┐
│           ART OF WAR AGENT DECISION CARD            │
├─────────────────────────────────────────────────────┤
│ 1. 始计：五事七计 → 值得做吗？                       │
│ 2. 作战：速战速决 → 预算多少？                       │
│ 3. 谋攻：上兵伐谋 → 能不做吗？                       │
│ 4. 军形：先胜后战 → 有风险吗？                       │
│ 5. 兵势：奇正相生 → 怎么组合？                       │
│ 6. 虚实：避实击虚 → 哪里用 agent？                   │
│ 7. 军争：以迂为直 → 有捷径吗？                       │
│ 8. 九变：灵活应变 → 需要调整吗？                     │
│ 9. 行军：读信号 → agent 状态如何？                    │
│ 10. 地形：什么任务？→ 什么策略？                     │
│ 11. 九地：多重要？→ 投多少？                         │
│ 12. 火攻：用什么工具？→ 何时用？                     │
│ 13. 用间：信息够吗？→ 验证了吗？                     │
└─────────────────────────────────────────────────────┘
```
