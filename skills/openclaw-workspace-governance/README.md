<p align="center">
  <img src="https://api.iconify.design/fluent-emoji:brain.svg" width="120" height="120" alt="Brain Icon" />
</p>

<h1 align="center">OpenClaw Workspace Governance</h1>

<p align="center">
  <strong>A System-Level Architecture Upgrade & Governance Framework</strong>
</p>

<p align="center">
  Languages: <a href="#-简体中文">简体中文</a> · <a href="#-english">English</a>
</p>

---

<h2 id="-简体中文">🇨🇳 简体中文</h2>

> 🚨 **高危/重要提示 (IMPORTANT WARNING)** 🚨
> **这不是一个普通的工具型 Skill，而是针对 OpenClaw 工作区的系统级架构升级与治理方案。**
> **在让你的 Agent 实施本指南之前，请务必对你的 Workspace 进行完整备份，并确保你理解其对文件状态和检索优先级的改变。请勿在未做快照的生产环境中盲目运行全自动治理！**

这是一个面向**复杂 OpenClaw 工作区**的治理型 skill。它不是为了制造更多流程，而是为了在复杂度已经上来之后，帮你压住漂移、明确当前事实层、缩小 live docs 面积，并让语义检索变得更可控。

### 系统能力详解 (System Capabilities)

本 Skill 提供了一套完整的系统级框架，赋予你的 OpenClaw 以下核心能力：
- **多 Agent 协作架构 (Multi-Agent Architecture)**：建立以 Supervisor 为中心的调度机制，实现“写审分离”。明确区分代码编写、代码审查、规则审核、文档撰写等专职岗位，防止单一 Agent 越权闭环。
- **分层记忆系统 (Layered Memory System)**：告别无序的长文档堆砌。建立从“原始日志 (Daily Notes)”到“主题卡片 (Topic Cards)”，再到“长期记忆 (Long-Term Memory)”的逐层蒸馏与质量门控机制。
- **语义检索与路由 (Semantic Retrieval Routing)**：将系统查询分类（如：状态查询、规则边界、历史溯源等），并建立基于桥接文件 (Bridge Files)、结构化记忆与 qmd 语义搜索的精准召回优先级。
- **审批与安全治理 (Approval & Governance)**：强制核心文件（如 AGENTS.md）的修改必须经过独立评审与人工授权；内置针对特定岗位的“防偷懒协议（代码交付契约）”，保障自动化任务的执行完整性。


### 适用场景

当你的工作区已经出现真实复杂度时，再用这份 skill。典型信号包括：
- 多个 Agent 或多角色执行路径已经出现
- 文档、记忆、状态层越来越多
- 回答“现在到底什么是真的”开始变难
- semantic search（语义搜索）有用，但不再能无脑相信
- live docs 过多、working set 不清、维护开始失控

⚠️ 这是进阶 skill，不是新手入门包，也不是 v1 的全自动 orchestrator。

### 非目标

这份 skill **不会**替你自动拍板、自动改规则，也不会把所有旧文档都继续维持成“活文档”。它提供的是治理 playbook，不是无限自动化引擎。

它不试图做这些事：
- 发布私有角色 lore 或内部组织文化
- 打包个人记忆、日记或私有运行历史
- 自动决定审批结果
- 自动改政策或规则
- 在 v1 里做全自动多 Agent 编排
- 因为“怕以后要用”而让所有旧文档都保持 live

### 快速开始

先别急着改文件，先判清楚你遇到的是哪一种 drift。主线只有六步：
1. 分类问题
2. 选择治理路径
3. 找到应该回答问题的权威事实层
4. 收紧文档角色和 freshness 边界
5. 用代表性问题验证
6. 在主线足够完整时主动收口

如果工作区现在很乱，先减少歧义，不要先加流程。

### 核心工作流

#### 1. 先分类问题

先判断你面对的是哪一类 drift，不要一上来就盲改文件。先分清类型，后面所有动作才不会跑偏。

你通常会遇到这些类型：
- governance drift：角色、审批、审查边界或规则正在漂
- current-state drift：现在到底什么是真的变得不清楚
- retrieval drift：semantic search、bridge files、topic cards、long-term memory 开始互相打架
- doc drift：旧文档还在假装自己代表当前事实
- maintenance drift：live docs 太多，没有 working set，也没人做 freshness checks
- phase drift：系统不停产出流程文档，却没有收口

不要先改文件，先判类型。

#### 2. 让不同变更走对治理路径

实现改动、文档解释改动、治理/规则改动，不是一回事。复杂工作区里，最怕把所有改动都走同一条线。

把工作类型区分清楚：
- implementation change：普通实现或落地改动
- documentation/explanation change：文档措辞、状态标签、说明层改动
- governance/policy/process change：角色边界、审批规则、路由规则、维护规则改动

可使用这些通用角色：
- **Coordinator**：定义问题、选路径、负责收口
- **Implementer**：执行文件/脚本/操作改动
- **Reviewer**：检查实现质量，揪明显问题
- **Policy Auditor**：审治理、流程、规则变化
- **Consensus Peer**：高风险结构变更前的可选同级会审

常见部署形态：
- **2-agent**：Coordinator+Implementer / Reviewer
- **3-agent**：Coordinator / Implementer / Reviewer
- **4-5-agent**：额外加入 Policy Auditor 和可选 Consensus Peer

基本规则：
- 高风险工作里，不要让同一角色既实现又做最终审查
- 治理/政策/流程改动要过 Policy Auditor
- 高风险结构改动前，如果单一规划者判断不够，插入 consensus-peer 会审
- 如果工作区里只有 1 个 agent，要明确写出“本来这里该有第二审”，不要假装自审等价

按需阅读：
- `references/multi-agent-governance.md`

v1 边界：
- 这份 skill 提供可部署的治理指导
- 它**不是** v1 的全自动多 Agent 编排系统

#### 3. 建立权威事实分层

不要把所有资料平均对待。真正的关键不是“资料多不多”，而是**冲突时谁说了算**。

把这些层分清楚：
- **canon**：规则、审批、硬边界
- **bridge/current-state**：回答“现在什么是真的”的短文件
- **health/consistency**：运行健康和一致性状态
- **runtime snapshot**：某一时点的运行事实
- **structured memory**：中等持久度的 topic/index 卡片
- **long-term memory**：只保留高持久事实
- **historical docs**：背景、旧阶段、旧计划、审计、报告

两层冲突时，不要平均；必须决定谁赢。

按需阅读：
- `references/source-of-truth-layering.md`
- `references/query-class-routing.md`

#### 4. 先分 query class，再决定检索顺序

别抽象地问“语义搜索靠不靠谱”。真正该问的是：对哪一类问题靠谱？在什么 runtime / cache 对齐状态下靠谱？它是主裁决层还是辅助召回层？

建议的 query class：
- system-state
- governance / rule-boundary
- runtime-now
- weekly-review / approval-state
- user-preference / profile
- historical trace / evidence
- maintenance / upkeep

默认策略：
- governance → canon first
- system-state → bridge/health first
- runtime-now → snapshot first
- user-preference → curated profile/manual sources first
- historical trace → discovery + verification
- semantic search → 除非明确验证更强，否则只作为 supporting layer

按需阅读：
- `references/query-class-routing.md`
- `references/semantic-search-diagnostics.md`

#### 5. 给文档打角色边界

旧文档最危险的不是存在，而是它还在假装自己代表 current truth。把 live docs 面积压小，系统才会稳。

常见标签与角色：
- `historical-reference`
- `needs-refresh`
- active/live maintenance docs
- special-case active safety restriction

尽量定义一个**最小 live subset**，其他默认降级成次级参考层。

按需阅读：
- `references/live-vs-historical-docs.md`

#### 6. 建 working set 和 freshness checks

working set 不是“所有重要文件”，而是“必须持续保鲜的最小活跃集合”。不要用一个统一阈值去管所有文档。

典型 working set 包括：
- health / consistency 文件
- bridge/current-state 文件
- runtime snapshot
- entrypoint/index docs
- 只有最高价值的 topic cards

用分组阈值，不要用一个笼统阈值：
- health/bridge/runtime/entry docs 用更短阈值
- structured topic/index docs 用更长阈值

用 freshness checker 把“谁应该记得更新一下”变成可重复执行的检查。

按需阅读：
- `references/freshness-discipline.md`

#### 7. 认真诊断 semantic-search runtime

语义检索出问题时，最常见的坑不是模型不行，而是 path alignment、cache/index 混线，或者 split-brain（诊断一个索引、查询另一个索引）。

诊断时建议按这条线走：
1. 先记录 before-state baseline
2. 确认 runtime config 与 cache/index context 是否对齐
3. 检查是否存在 split-brain
4. 修掉明显的 indexing/embedding 缺口
5. 用少量代表性 query classes 回归验证
6. 不要给 blanket trust label，要按 query class 标可信度

按需阅读：
- `references/semantic-search-diagnostics.md`

#### 8. 用代表性问题验证，而不是只看结构

结构看起来整齐，不等于系统真的能回答问题。至少拿 system-state、governance、maintenance、historical/preference 这几类真实问题测一轮。

最低验证集：
- 一个 system-state 问题
- 一个 governance 问题
- 一个 maintenance 问题
- 一个 historical 或 preference 问题

判定结果建议只用三种：
- PASS
- PASS WITH ESCALATION
- FAIL

只有当较小的 live subset 也确实能回答日常问题时，才算成立。

#### 9. 主动收尾，不要无限扩相

如果一个 phase 已经主线落地，就该收口进 maintenance observation（维护观察期），而不是继续生产更多流程文档。

每个 phase 都要明确：
- 什么是 **landed**
- 什么是 **improving**
- 什么是 **deferred**
- 主线是否已经足够完整，可以关闭

一旦主线够完整：
- 转入 maintenance observation
- 保持 live subset 尽量小
- 做小修，不要再开一轮 sprawling phase

按需阅读：
- `references/completion-criteria.md`

### v1 推荐脚本

这些脚本覆盖 v1 最关键的三条治理检查线：freshness、semantic runtime、doc status。

- `scripts/freshness-check.py`
- `scripts/semantic-runtime-check.sh`
- `scripts/doc-status-scan.py`

### v1 推荐参考文档

这些 references 构成 v1 的主参考集；它们负责解释治理原则，不负责替你自动执行一切。

- `references/multi-agent-governance.md`
- `references/source-of-truth-layering.md`
- `references/query-class-routing.md`
- `references/live-vs-historical-docs.md`
- `references/freshness-discipline.md`
- `references/semantic-search-diagnostics.md`
- `references/completion-criteria.md`

### v1 推荐示例

先用这些示例建 working set、system-state index 和 health 示例，再按你的工作区实际情况收窄。

- `assets/examples/working-set.example.md`
- `assets/examples/working-set.example.json`
- `assets/examples/current-health.example.json`
- `assets/examples/system-state-index.example.md`

### v1 叙事要收紧

这是一份 workspace governance tool / governance playbook。它包含多 Agent 治理指导，但它不是 roleplay 包，也不是 v1 的全自动 multi-agent orchestrator。

它最核心的承诺只有五条：
- 减少 drift
- 让 current truth 更容易识别
- 把 live docs 面积压小
- 让 semantic retrieval 更可控
- 让维护更可持续

### 发布与草案边界

当前正式发布内容以本目录下的 package-local 文件为准。旧的 `docs/skill-draft-*` 文件属于设计历史，不应继续和当前发布包竞争解释权。

---

<h2 id="-english">🇬🇧 English</h2>

> 🚨 **IMPORTANT WARNING** 🚨
> ***This is NOT a standard tool-level skill. It is a system-level architecture upgrade and governance framework for your OpenClaw workspace.***
> ***Before allowing your Agent to implement these guidelines, you MUST take a full backup of your workspace. Do not run automated governance in a production environment without understanding how it alters document states and retrieval routing.***

This is a governance skill for **complex OpenClaw workspaces**. It is not here to add process for its own sake. It helps you reduce drift, clarify current truth, shrink the live-doc surface, and make semantic retrieval more controllable.

### System Capabilities

This skill provides a complete system-level framework, empowering your OpenClaw with the following core capabilities:
- **Multi-Agent Architecture**: Establishes a Supervisor-centric dispatch mechanism, ensuring "separation of writing and reviewing". It clearly separates roles like code generation, code review, policy auditing, and documentation, preventing any single agent from making unauthorized closed-loop decisions.
- **Layered Memory System**: Moves away from chaotic long documents. It builds a progressive distillation and quality-gating mechanism from "Raw Daily Notes" to "Topic Cards" and finally to "Long-Term Memory".
- **Semantic Retrieval Routing**: Classifies system queries (e.g., state queries, rule boundaries, historical traces) and establishes precise recall priorities across bridge files, structured memory, and qmd semantic search.
- **Approval & Governance**: Mandates that modifications to core files (like AGENTS.md) must pass independent review and human authorization. It includes built-in "anti-laziness protocols (code delivery contracts)" for specific roles to ensure the completeness of automated tasks.


### Scope

Use this skill when the workspace already has real complexity, such as:
- multiple agents or role-like execution paths
- growing docs / memory / state layers
- uncertainty about what is current vs historical
- semantic search that is useful but not equally trustworthy for every query class
- maintenance drift caused by too many live docs and weak closure discipline

This is an advanced governance skill. It is **not** a beginner skill and not a full automated orchestrator in v1.

### Non-goals

This skill does **not** try to:
- publish private role lore or internal organization culture
- ship personal memory, daily logs, or private operational history
- automate approval decisions
- automate policy changes
- automate full multi-agent orchestration in v1
- keep every old document live "just in case"

### Quick Start

Use this skill in six steps:
1. classify the drift or governance problem
2. choose the right governance path
3. identify the source-of-truth layers that should answer the question
4. set doc-role and freshness boundaries
5. validate the system with representative questions
6. close the phase when the mainline is complete enough

If the workspace is unclear, start by reducing ambiguity rather than adding more process.

### Core workflow

#### 1. Classify the problem first

Identify which of these is happening:
- governance drift (roles, approvals, reviewer boundaries, policy changes)
- current-state drift (what is true now is unclear)
- retrieval drift (semantic search, bridge files, topic cards, long-term memory are fighting)
- doc drift (old docs are masquerading as current truth)
- maintenance drift (too many docs are "live", no working set, no freshness checks)
- phase drift (the system keeps producing process docs without closure)

Do not start by editing files blindly. First decide the drift type.

#### 2. Route change types through the right governance path

Treat these as different work types:
- **implementation change**: normal execution work
- **documentation/explanation change**: doc wording, status labels, explanatory layers
- **governance/policy/process change**: role boundaries, approval rules, routing rules, maintenance rules

Use these generic roles:
- **Coordinator**: frames the work, chooses path, closes the loop
- **Implementer**: makes the operational/file/script changes
- **Reviewer**: checks implementation quality and catches obvious mistakes
- **Policy Auditor**: checks governance, process, or rule changes
- **Consensus Peer**: optional peer used before risky structural changes

Deployment shapes:
- **2-agent**: Coordinator+Implementer / Reviewer
- **3-agent**: Coordinator / Implementer / Reviewer
- **4-5-agent**: add Policy Auditor and optional Consensus Peer

Rules:
- never let the same role both implement and perform final review on risky work
- send governance/policy/process changes through Policy Auditor review
- insert a consensus-peer pass before risky structural changes when one planner's judgment is not enough
- if the workspace only has 1 agent, state explicitly where a second review would normally be required instead of pretending self-review is equivalent

Read when needed:
- `references/multi-agent-governance.md`

Important v1 limit:
- this skill gives deployable governance guidance
- it does **not** provide full automated multi-agent orchestration in v1

#### 3. Build source-of-truth layering

Separate these layers clearly:
- **canon**: rules, approvals, hard boundaries
- **bridge/current-state**: short files that answer "what is true now?"
- **health/consistency**: operational health and alignment state
- **runtime snapshot**: point-in-time runtime truth
- **structured memory**: topic/index cards with medium durability
- **long-term memory**: durable facts only
- **historical docs**: background, prior phases, old plans, audits, reports

When two layers disagree, do not average them. Decide which layer wins.

Read when needed:
- `references/source-of-truth-layering.md`
- `references/query-class-routing.md`

#### 4. Classify query classes before deciding retrieval order

Ask:
- reliable for which query class?
- under what runtime/cache alignment?
- as primary authority or supporting recall?

Recommended query classes:
- system-state
- governance / rule-boundary
- runtime-now
- weekly-review / approval-state
- user-preference / profile
- historical trace / evidence
- maintenance / upkeep

Default policy:
- governance → canon first
- system-state → bridge/health first
- runtime-now → snapshot first
- user-preference → curated profile/manual sources first
- historical trace → discovery + verification
- semantic search → supporting layer unless explicitly validated stronger for that class

Read when needed:
- `references/query-class-routing.md`
- `references/semantic-search-diagnostics.md`

#### 5. Mark docs as live, historical, stale, or special-case

Use labels and roles such as:
- `historical-reference`
- `needs-refresh`
- active/live maintenance docs
- special-case active safety restriction

Define a **minimal live subset** and treat everything else as secondary by default.

Read when needed:
- `references/live-vs-historical-docs.md`

#### 6. Establish a working set and freshness checks

Create a narrow working set for documents that must remain fresh.

Typical working set includes:
- health / consistency files
- bridge/current-state files
- runtime snapshot
- entrypoint/index docs
- only the highest-value topic cards

Use grouped thresholds rather than one blanket threshold.
For example:
- shorter threshold for health/bridge/runtime/entry docs
- longer threshold for structured topic/index docs

Use the freshness checker to turn "someone should remember to update this" into a repeatable check.

Read when needed:
- `references/freshness-discipline.md`

#### 7. Diagnose semantic-search runtime carefully

When semantic search behaves strangely:
1. capture a before-state baseline
2. confirm whether runtime config and cache/index context are aligned
3. check for split-brain behavior (diagnosing one index while querying another)
4. repair obvious pending indexing/embedding gaps
5. validate with a few representative query classes
6. avoid blanket trust labels after the diagnosis — state trust by query class

Use the runtime checker script for aligned checks.

Read when needed:
- `references/semantic-search-diagnostics.md`

#### 8. Validate with representative questions

At minimum validate:
- one system-state question
- one governance question
- one maintenance question
- one historical or preference question

Judgment types:
- PASS
- PASS WITH ESCALATION
- FAIL

Only keep a smaller live subset if it actually answers ordinary questions well enough.

#### 9. Close phases on purpose

For each phase, decide:
- what is **landed**
- what is **improving**
- what is **deferred**
- whether the mainline is complete enough to close

Once the mainline is complete enough:
- move into maintenance observation
- keep the live subset small
- make only small refinements instead of opening another sprawling phase

Read when needed:
- `references/completion-criteria.md`

### Preferred first-release scripts

Use these in v1:
- `scripts/freshness-check.py`
- `scripts/semantic-runtime-check.sh`
- `scripts/doc-status-scan.py`

### Preferred first-release references

Use these as the main governance/reference set in v1:
- `references/multi-agent-governance.md`
- `references/source-of-truth-layering.md`
- `references/query-class-routing.md`
- `references/live-vs-historical-docs.md`
- `references/freshness-discipline.md`
- `references/semantic-search-diagnostics.md`
- `references/completion-criteria.md`

### Preferred first-release examples

Use these as templates/examples:
- `assets/examples/working-set.example.md`
- `assets/examples/working-set.example.json`
- `assets/examples/current-health.example.json`
- `assets/examples/system-state-index.example.md`

### Keep the v1 narrative tight

This is a workspace governance tool / governance playbook. It includes multi-agent governance guidance, but it is not a roleplay package and not a full automated multi-agent orchestrator in v1.

The core promise is simple:
- reduce drift
- make current truth easier to identify
- keep live docs small
- make semantic retrieval more controlled
- make maintenance sustainable

### Package rule

During the current release line, review the package-local files in this directory first. Treat older `docs/skill-draft-*` files as drafting history unless you are explicitly tracing design history.
