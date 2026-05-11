---
name: multi-agent-workshop
description: 七阶段（含阶段0任务澄清）多角色工作坊；角色种类与人数均由任务决定。触发词："多角色研讨"、"需求工作坊"、"需求评审"、"圆桌"、"定方案再执行"。
version: 2.2.3
---

# Multi-Agent Workshop

在**单会话**内由**主 Agent 担任导演**，按 **7 个阶段（含阶段 0）**推进；每阶段产物写入 `workshops/<session_id>/`，角色发言建议用 **subagent**（一次一个角色、只注入该角色立场），避免上下文混乱。

> **所有阶段跳转必须经 `orchestrator.py`（Plan B）**：门禁以代码强制，不依赖 Markdown 约定。导演每次推进阶段时执行 `orchestrator.py advance <sid>`；跳转前检查 `orchestrator.py gate <sid>`。

## 何时启用

用户要：**多人视角讨论同一需求、互评、输出可执行方案、确认后再执行**。

## 核心原则：角色由任务决定，不是固定班子

- **禁止**不经 **阶段 0** 就默认把「如何产出高质量 X」当成 **必须交完整成稿**（或相反）；须先锁定 **交付物类型**（方案/SOP、成稿、大纲+样例、混合等）。
- **禁止**不经阶段 2 就默认使用「运营 / 产品 / 技术」；三者仅是**通用软件需求**的**参考模板**，不是每题的答案。
- **阶段 2 必须先回答**：「要完成这个任务，最少需要哪几种**相互制约的专业视角**？」再列角色。
- **角色人数没有固定值**（不是必须 2 个、3 个或 5 个）：**完全由任务决定**——有几个**不可缺少且彼此能形成张力的视角**，就设几个角色；宁可少也不要凑数。多一个角色就多一轮 token 与协调成本。
- 下文的「2～5」「调用量级表」仅是**常见规模参考**，不是规范；**唯一标准**是阶段 2 的选角理由是否成立。
- 在 `state.md` 必须写清：**任务类型标签** + **为何选这些角色（及为何是这个人数量）**（各一行），便于复盘。

### 任务类型 → 角色组合（示例，可增删）

| 任务类型 | 常见角色视角（示例） | 说明 |
|----------|----------------------|------|
| 通用产品需求 / 功能评审 | 运营、产品、技术 | 参考 `references/sample-roles/` |
| 短视频 / 直播 / 投放素材 | 编导或内容、法务或合规、剪辑或制作 | 重传播与合规，未必需要「技术」 |
| 公关 / 舆情 / 对外声明 | 公关、法务、业务事实负责人 | 避免只有运营 |
| 数据 / 指标 / 实验 | 数据/分析、产品、工程 | 「运营」可换成增长但职责要写清 |
| 纯技术债 / 架构改造 | 技术、SRE/运维、产品（仅定范围） | 可不要运营 |
| 采购 / 商务 / 合同 | 商务、法务、财务或使用方 | 与产研三角无关 |
| 法律合规审查 | 法务、业务、执行对接人 | 不要假装「技术」能替代法务立场 |
| 市场研报 / 行业研究 | 市场情报、分析或产品视角、事实/合规把关 | 需可引用事实时优先安排**一次集中检索**；检索失败须在 `state` 与正文披露 |

**导演动作**：从上表**得到启发即可**，不要机械套用；若用户任务跨界，可**合并角色**（一人兼两视角但分两轮说）或**拆两次工作坊**。

## 目录与产物（相对 workspace 根）

| 产物 | 路径 |
|------|------|
| 工作坊根目录 | `workshops/<session_id>/` |
| 状态 + 阶段 + 摘要 | `workshops/<session_id>/state.md` |
| 完整发言（可选） | `workshops/<session_id>/transcript.md` |
| 可执行方案 | `workshops/<session_id>/plan.md` |
| **交付正文（推荐）** | `workshops/<session_id>/deliverables/*`（报告、脚本包、设计稿等） |

**`deliverables/`**：阶段 6 或同步写入的**对用户可见成果**默认放此目录，避免与 `state.md` 混写；路径写进 `plan.md` 执行清单或验收表。

**敏感信息**：`workshops/` 可能含未公开需求；对外 git 请忽略或脱敏，见 `workshops/README.md`。

**`session_id` 建议**：`YYYY-MM-DD_主题简写`。用户未命名时由导演生成。

在 `state.md` 的「当前阶段」中统一使用下列 **phase key**（便于检索）：

| 阶段 | phase key |
|------|-----------|
| 0 任务澄清 | `phase_0_intake` |
| 1 任务理解 | `phase_1_understanding` |
| 2 角色拆解 | `phase_2_roles` |
| 3 角色创建 | `phase_3_role_cards` |
| 4 任务讨论 | `phase_4_discussion` |
| 5 plan 起草 | `phase_5_plan` |
| 5 末尾待批 | `awaiting_approval`（`plan.md` 已落盘、**用户未确认**前） |
| 6 plan 执行 | `phase_6_execution` |

**说明**：`awaiting_approval` 仍属**阶段 5 的末尾**，不是第 7 阶段；用户确认后进入 `phase_6_execution`。

## 模板与骨架（复制起盘）

| 用途 | 路径 |
|------|------|
| `state.md` 结构 | `templates/state.example.md` |
| `transcript.md` 结构 | `templates/transcript.example.md` |
| 自建角色卡 | `references/role-card-skeleton.md` |
| 从 JD 构建角色卡 | `references/role-card-from-jd.md` |
| 阶段 1 导演迫问（可选） | `references/director-forcing-questions.md` |
| `plan.md`（全量） | `templates/plan-output.md` |
| `plan.md`（轻量） | `templates/plan-lite.md`（见下文「plan 模板选择」） |
| **Orchestrator（唯一阶段管理入口）** | `scripts/orchestrator.py`（阶段机 + 门禁 + SQLite；**硬性阻塞不满足前置条件的跳转**） |
| **阶段 6 执行脚本生成（可选）** | `workshops/scripts/generate_execution.py`（`--preset` 或 **`--from-plan`** 读 `plan.md` 的 `execution_*`）；说明见 `workshops/scripts/README.md` |
| JD→角色卡草稿生成 | `scripts/jd_to_role_card.py`（`--role <名> --industry <行业> [--task <任务>]`） |
| 各阶段检查清单（给人/LLM 看） | `scripts/phases/00-…06-*.md` |
| **关闭 subagent 并行**（改 `openclaw.json`） | `scripts/openclaw-subagents-parallel.sh`（`off` = `maxConcurrent`→1；需 `python3`；改前自动备份） |

### Orchestrator CLI（唯一阶段管理入口）

`scripts/orchestrator.py`：Python 3.8+，无第三方依赖，状态存 SQLite（`data/orchestrator.db`）。**所有阶段跳转必须经此工具，门禁以代码强制**。

| 子命令 | 说明 |
|--------|------|
| `orchestrator.py init <sid> [-d TYPE]` | 创建 session + workshops 目录（可选指定 deliverable_type） |
| `orchestrator.py status <sid>` | 当前状态 + 下一门禁是否通过 |
| `orchestrator.py advance <sid>` | 推进到下一阶段（**检查门禁**） |
| `orchestrator.py set-phase <sid> <phase> [--force]` | 跳转阶段（检查门禁；`--force` 可强行跳过） |
| `orchestrator.py gate <sid> [phase]` | 查看门禁状态 |
| `orchestrator.py set <sid> <field> <value>` | 设置字段（deliverable_type、raw_requirement、approved_at 等） |
| `orchestrator.py set-role <sid> <name> [-r ...] [-t ...] [--card-path ...]` | 添加/更新角色 |
| `orchestrator.py add-message <sid> --phase ... --role ...` | 记录讨论消息 |
| `orchestrator.py validate <sid>` | 全量校验 |
| `orchestrator.py history <sid>` | 阶段变更历史 |
| `orchestrator.py import <sid>` | 从现有 `workshops/<sid>/state.md` 导入 |
| `orchestrator.py sync <sid>` | DB 状态回写 `state.md`（phase key + Session 状态） |
| `orchestrator.py cleanup` | 清理 OpenClaw 残留 subagent |
| `orchestrator.py list` | 列出所有 session |

**门禁规则**（代码强制，非建议）：

| 目标阶段 | 前置条件 |
|----------|----------|
| → 阶段 1 | 阶段 0 填了 deliverable_type + success_criteria |
| → 阶段 2 | 阶段 1 填了 raw_requirement |
| → 阶段 3 | 阶段 2 填了 task_type_tag + role_rationale + ≥1 角色 |
| → 阶段 4 | 阶段 3 每个角色有 card_path 或 card_inline |
| → 阶段 5 | 阶段 4 有 ≥1 条讨论消息 |
| → awaiting | plan.md 存在或 plan_version 已设 |
| → 阶段 6 | 当前为 awaiting_approval 且 approved_at 已设 |

示例（完整起盘到推进流程）：

```bash
cd /path/to/workspace
SID="2026-03-22_my-topic"
ORC="python3 skills/multi-agent-workshop/scripts/orchestrator.py"

# 1. 起盘（创建 session + workshops 目录 + 模板文件）
$ORC init $SID -d methodology

# 2. 阶段 0：填交付物类型、成功标准
$ORC set $SID success_criteria "产出可复用的写作方法论 SOP"
$ORC advance $SID                    # → phase_1_understanding（门禁检查）

# 3. 阶段 1：填原始需求
$ORC set $SID raw_requirement "如何产出高质量 AI 观点文章"
$ORC advance $SID                    # → phase_2_roles

# 4. 阶段 2：填任务类型、选角理由、添加角色
$ORC set $SID task_type_tag "内容创作"
$ORC set $SID role_rationale "需要信息捕捉、观点提炼两种张力"
$ORC set-role $SID 趋势猎手 -r "扫描热点" -t "热点vs深度"
$ORC set-role $SID 观点锻造师 -r "提炼角度" -t "差异化vs可论证"
$ORC advance $SID                    # → phase_3_role_cards

# 5. 随时检查状态 / 门禁 / 历史
$ORC status $SID
$ORC gate $SID
$ORC history $SID
```

## 防走样（导演必读）

- 不标 `director_monologue` / 压缩就**禁止**单口吻写多角色全文。
- 省略 subagent 或迫问须在 `state.md` + `plan.md` 风险同时披露。
- 跳过迫问清单须写具体原因（**禁止**仅用「已内化」「略」）。

> 完整规则（独白/压缩叠加、何时不可压缩、迫问跳过格式）→ **`references/anti-drift.md`**

## 导演补充规则

> 以下为**低频参考**，完整内容 → **`references/director-supplementary.md`**

| 主题 | 要点 | 详见 |
|------|------|------|
| 用户确认 | plan 勾选、自然语言「确认执行」、或子集确认均可；模糊表述不算 | `director-supplementary.md` §用户确认 |
| 轮次成本 | 2 角色≈4 调用，3≈6；用户要快可压缩但须标注 | 同上 §轮次与成本 |
| 事实检索 | 阶段 4 前至多 1-2 次集中检索；失败须声明，禁止捏造 | 同上 §事实检索 |
| 会话续跑 | 同 SID 续写须先读 state/plan；默认新 SID | 同上 §会话续跑 |
| subagent 收口 | 每跳有结束说明或导演补录；session 结束写 state.md | `references/subagent-closure.md` |
| OpenClaw 集成 | 阶段 6 遵循 `AGENTS.md` 路由 + `TOOLS.md` | `director-supplementary.md` §OpenClaw |
| gstack 参考 | 只读克隆 `workspace/reference/gstack/` | `docs/gstack-learning-notes.md` |
| 辩论协议 | 提前收束、冲突处理、语言约定 | `references/debate-protocol.md` |

---

## 全局约束（全程有效）

- **阶段 0～5**：以分析、文档、讨论为主；**不**擅自执行对外发送、改生产、支付等离开本机的操作。
- **阶段 6**：仅当用户在对话中**明确确认** `plan.md`（或确认修改后的版本）后启动；高风险步骤先复述再执行。

---

## 阶段 0：任务澄清（phase_0_intake）

**目的**：在选角与多轮讨论前，锁定 **交付物类型** 与 **非目标**，避免典型走样：用户要「**可复用的写作方法论**」，系统却直接交付「**一篇完整文章**」（或相反）。

**何时必须做**：用户表述模糊（如「如何产出高质量文章」「帮我做好内容」）且未明确 **交付形态** 时；**默认新 session 从本阶段开始**（`state.md` 模板默认 `phase_0_intake`）。

**动作**：

- 在 `state.md`「阶段 0」勾选或填写 **期望交付物类型**（见 `templates/state.example.md`）：`methodology` / `artifact` / `outline_sample` / `review` / `mixed`（混合须写清边界与顺序）。
- 写 **非目标**（例：本 session **不**默认交付 3000 字成稿；或 **不**只给空洞框架而不给可执行步骤）。
- 写 **成功标准** + **用户原话摘要** + **导演对齐说明**（有歧义须追问，**禁止**单方面猜交付物）。
- 若用户改口改变交付物类型：回到本阶段更新 `state.md`，或进入阶段 5+ 时 **递增 `plan_version`** 并在风险中披露。

**完成条件**：阶段 0 字段齐全 → 执行 `orchestrator.py set <sid> deliverable_type <type>` + `set <sid> success_criteria "..."` → `orchestrator.py advance <sid>`（门禁检查 deliverable_type + success_criteria）。

---

## 阶段 1：任务理解（phase_1_understanding）

**目的**：在 **交付物类型已锁定** 的前提下，把「用户到底要什么细节」说清楚，避免后面角色空转。

**动作**：

- 从用户输入提取：**业务目标、用户/客户、时间约束、成功标准**；缺失则写**假设**并标「待用户确认」。**不得**在本阶段悄悄改阶段 0 的交付物类型；若需改则回到阶段 0 或走 plan 变更流程。
- **推荐**：按 `references/director-forcing-questions.md` **择问**（不必六问全问），把答案并入上文假设或「待澄清」；未使用清单时须满足 `references/anti-drift.md`「迫问清单跳过格式」。用户要求快进时可同步启用 **压缩模式**。
- 在 `state.md` 写入 **原始需求**（可含原文摘要 + 导演理解的一段话）。

**完成条件**：`state.md` 中「原始需求 + 约束与假设」齐全 → 执行 `orchestrator.py set <sid> raw_requirement "..."` → `orchestrator.py advance <sid>`（门禁检查 raw_requirement）。

---

## 阶段 2：角色拆解（phase_2_roles）

**目的**：为**当前这一条任务**定制视角组合；**不是**默认固定三人。

**动作**：

1. 在 `state.md` 写 **任务类型标签**（如：`短视频`、`功能开发`、`数据需求`、`公关声明`）。
2. 自问：哪些视角之间会有**真实张力**（例如传播 vs 合规、范围 vs 工期）？只邀请这些视角进组。
3. 若选用 **运营 / 产品 / 技术**：必须在 `state.md` 写一句 **「为何本任务适用产研三角」**；否则视为阶段 2 未完成。
4. 若任务与产研无关，**不得**硬塞 `ops/product/tech`；应改用阶段 3 的 **session 角色卡** 定义新角色。
5. 写入 **角色列表**：`角色名` + `一句话职责` + `在本任务中最关心的冲突点`。

**完成条件**：任务类型 + 选角理由（含**为何是 N 个角色、能否再少**）+ 角色列表齐全 → 执行 `orchestrator.py set <sid> task_type_tag "..."` + `set <sid> role_rationale "..."` + `set-role <sid> <name> -r ... -t ...`（每个角色） → `orchestrator.py advance <sid>`（门禁检查 task_type_tag + role_rationale + ≥1 角色）。若阶段 1 已用迫问清单，选角应与迫问暴露的**张力**一致。

---

## 阶段 3：角色创建（phase_3_role_cards）

**目的**：每个角色有**可执行的立场说明**（给 subagent 用），且**与当前任务绑定**。

**动作**：

对阶段 2 确定的**每个角色**，导演按下表判断角色卡来源，然后执行对应路径：

| 条件 | 路径 | 做什么 |
|------|------|--------|
| 角色与 `sample-roles/`（ops/product/tech）**语义一致**，且导演能准确写出该角色在**本任务**中的立场边界 | **复用样例** | 复制 `references/sample-roles/*.md`，在开头加「本任务中你的侧重点」段 |
| 角色是**通用职能**（如项目经理、设计师）但不在 sample-roles 中，导演对该岗位职责边界**有把握** | **直接新建** | 按 `references/role-card-skeleton.md` 手写 |
| **以下任一为真则必须查 JD** ↓ | **JD 构建** | 搜索 JD → 提炼 → 写卡（见下方流程） |
| ① 角色属于**垂直/专业领域**（如合规法务、供应链、临床研究、财税）——导演不确定该岗位真实的职责边界和禁区 | | |
| ② 角色名在团队日常中**不常见**或导演从未写过该角色的卡 | | |
| ③ 阶段 2 选角时导演**犹豫过**该角色"到底管什么、不管什么" | | |

**JD 构建流程**（满足上表"必须查 JD"条件时执行）：

1. **搜索**：执行 `python3 scripts/jd_to_role_card.py --role "<角色名>" --industry "<行业>" --task "<本次任务>"` 生成草稿；或在对话中搜索 `"<角色名>" <行业> 岗位职责 任职要求 BOSS直聘 OR 猎聘`。
2. **提炼**：从 JD 片段中提取 **职责→立场、任职要求→发言要求、岗位边界→禁止项**（映射规则见 `references/role-card-from-jd.md`）。
3. **绑定**：首行写明 `针对任务：〈…〉`，将通用 JD 画像裁剪为本任务的具体侧重点。
4. **落盘**：写入 `workshops/<session_id>/roles_<slug>.md`。

> **不查 JD 也可以，但要说明原因**：若导演认为自己对该角色足够了解而跳过 JD 查询，须在 `state.md` 角色列表旁写一句 **「未查 JD，理由：…」**（如"该角色与 sample-roles/ops 语义一致"）。禁止无声跳过。

**完成条件**：每个参与讨论的角色均有可注入文本 → 执行 `orchestrator.py set-role <sid> <name> --card-path <path>` 或 `--card-inline "..."` → `orchestrator.py advance <sid>`（门禁检查每个角色有 card）。

---

## 阶段 4：任务讨论（phase_4_discussion）

**目的**：先**各抒己见**，再**互评**，形成可写进 plan 的共识与分歧。

**动作**：

### 4a 观点轮（每角色一次或按 `max_rounds` 控制）

subagent 任务模板：

```
你是【角色名】，立场与输出格式必须严格遵守：
（粘贴对应 session 角色卡全文或 references/sample-roles/*.md）

共同上下文：
（粘贴 state.md 中的「原始需求」+ 已有发言摘要）

本轮任务：
- 阐述你对需求的理解（目标、范围、指标）
- 明确你与其他角色可能冲突的假设
- 提出至少 2 条可验证的待澄清问题
输出：中文 Markdown，小标题分段。
末尾必须附：**### 本子 agent 结束说明**（见 `references/subagent-closure.md` 模板）。
```

每角色结束后，将**≤400 字摘要**写入 `state.md`「轮次摘要」；若模型未附结束说明，**导演补录**。

### 4b 互评轮

subagent 任务改为：

- 回应其他角色理解中与你**不一致**之处；
- 指出对方**具体**不足（附「若成立则影响」）；
- 你的**让步条件**与**底线**。
末尾必须附：**### 本子 agent 结束说明**（同上）。

摘要同样写入 `state.md`；无结束说明则导演补录。

**Token 控制**：默认观点轮 1 轮 + 互评 1 轮；若角色 >3 或用户要求缩短，导演可在 `state.md` 说明「压缩轮次」并在 plan「风险」中记录。

**完成条件**：各角色完成观点 + 互评（或导演提前收束并说明）→ 每轮用 `orchestrator.py add-message <sid> --phase phase_4_discussion --role <role> --summary "..."` 记录 → `orchestrator.py advance <sid>`（门禁检查 ≥1 条讨论消息）。

---

## 阶段 5：plan 建立（phase_5_plan）

**目的**：把讨论**收敛**为单一可执行文档，并等人拍板。

### plan 模板选择

| 条件 | 使用模板 | 必填标记 |
|------|----------|----------|
| 多里程碑、执行清单 ≥3 项、需完整风险矩阵 | `templates/plan-output.md` | 默认 |
| **单一交付物**（如一篇报告、一个视频包）、清单 ≤2 项 | `templates/plan-lite.md` | `plan.md` 内写 **`plan_template: lite`**，且 **§风险** 说明相对全量模板缺了哪些节 |

全量与 lite **不可混用结构不声明**；升级 scope 时可将 lite **升格**为全量并递增 `plan_version`。

**动作**：

- 主 Agent（导演）阅读 `state.md` 摘要，必要时回看 `transcript.md`。
- 按所选模板写 **`plan.md`**（全量：共识、指标、里程碑、执行清单、风险、`plan_version`、`CHANGELOG` 约定见 `plan-output.md`；lite 见 `plan-lite.md`）。
- 汇总待澄清项：已解决的写入共识表；未决写入「未决项」或 plan 风险。
- 执行 `orchestrator.py set <sid> plan_version 1` → `orchestrator.py advance <sid>`（门禁检查 plan.md 存在）→ 自动进入 `awaiting_approval`。
- 在对话中**明确请用户确认或修改** `plan.md`。

**完成条件**：`plan.md` 已落盘 → 用户确认后执行 `orchestrator.py set <sid> approved_at "YYYY-MM-DDTHH:MM"` → `orchestrator.py advance <sid>`（门禁要求 awaiting_approval + approved_at 已设）→ 进入 `phase_6_execution`。

---

## 阶段 6：plan 执行（phase_6_execution）

**目的**：按清单调用 **工作区 `skills/`**（与 Cursor `@workspace/skills` 同目录、相对**工作区根**）内的技能及工具，并留痕。

**路径约定**：`<技能名>` 与 `AGENTS.md` 路由表一致；每个原子步骤**打开并遵循** `skills/<技能名>/SKILL.md`，不得凭记忆编造脚本路径或技能名。

**本机与环境**：阶段 6 执行须**对照工作区根 `TOOLS.md`**（与 Cursor `@workspace/TOOLS.md` 同文件）——浏览器、Obsidian、cron、飞书附件、基础库路径、**生图/生视频端到端流程**（提示词技能 vs 出图/海螺脚本顺序）等；不要求每次通读全文，但**任务涉及哪一节就必须读哪一节**。细则与检查清单见 `scripts/phases/06-phase_6_execution.md` §0 表格。

**阶段 6 执行清单（给人/导演逐步核对）**：`scripts/phases/06-phase_6_execution.md`（含「`AGENTS.md` + `TOOLS.md` + `skills/`」完整流程）。

**技能搭配（阶段 6：先扫描装配，再执行）**：

用户一旦确认方案（`approved_at` 已写入），阶段 6 **分两节拍**（详见 `scripts/phases/06-phase_6_execution.md` §0）：

1. **节拍 6a — 技能扫描与装配（必先做）**：对照 `plan.md` 执行清单**逐步**读 **`AGENTS.md`** → 按任务打开 **`TOOLS.md`** 对应小节 → 为每步打开并核对相关 **`skills/<name>/SKILL.md`**，再决定「用哪把锤子」；**未完成 6a 前**，不得调用计划外 API、不得用临时方案冒充交付物。
2. **节拍 6b — 按 SKILL 执行**：严格按各 **`SKILL.md`** 执行，并与 **`TOOLS.md`** 本机约定对齐；留痕。

完整装配算法见 **`references/skill-composition.md`**。

- **`skill-pipeline.md`**：**可选落盘**（多步/多技能/要审计时强烈建议）；步骤少时可在 **`execution-log.md`** 用几句话记录「已扫 AGENTS、选用/排除谁」即可 —— **省略的是文档长度，不是 6a 扫描本身**。
- **可选机器化**：若流水线某步对应本机可跑工具链（如 OpenRouter 出图复用 `xhs-card-generator` 客户端），可在 **`plan.md` 写 `execution_preset` / `execution_prompts_file`**（见 `templates/plan-lite.md` §7）后运行 **`workshops/scripts/generate_execution.py --workshop workshops/<session_id> --from-plan`**；或直接 **`--preset <名>`**。在**该会话目录**下生成 `scripts/run_*.py`（详见 **`workshops/scripts/README.md`**）。
- **红线**：不虚构技能名；互斥以 `AGENTS.md` 为准；纯人工步骤标 `human_design`，不得冒充完成。

**动作**：

- 仅当用户已确认方案（可在 `plan.md` 用户确认章节勾选并填确认时间）。
- 将执行清单逐项落实；每完成一项更新 `plan.md` 状态列或写 `execution-log.md`（若使用了 `skill-pipeline.md`，序号与之对齐）。
- **每一次** subagent / 独立工具链任务结束时，须满足 **`references/subagent-closure.md`** 的「单次结束」格式（产出摘要、完成度、对导演的提示）；若模型未输出，**导演补录**到 `transcript.md` 或 `state.md`。
- 若执行中发现需改 scope，**暂停**，回到阶段 5 更新 `plan.md` 并再次确认。

**完成条件**：清单完成或用户主动叫停 → 执行 `orchestrator.py set <sid> session_status completed`（或 `stopped` / `cancelled`）+ `set <sid> ended_at "..."` → `orchestrator.py sync <sid>`（回写 state.md）。并填写 `state.md` **「结束与归档」**（见 `templates/state.example.md`）。

---

## 质量检查

```
□ 阶段 0：`state.md` 含 **期望交付物类型** + **非目标** + **成功标准** + 与用户原话对齐（避免「要方案却给成稿」）
□ state.md 含任务类型标签 + 选角理由（含人数为何是 N）；非产研任务未滥用 ops/product/tech；未为凑人数硬加角色
□ 阶段 1：已用迫问或写明 **「未使用 director-forcing-questions.md，原因：…」**（禁止仅写「已内化」）
□ 若有交付文件，路径在 `deliverables/` 且 `plan` 可验收
□ 选用 `plan-lite` 时已标 `plan_template: lite` 且风险说明与全量模板的差异
□ 阶段 2 角色列表与任务匹配；阶段 3 每角色有任务绑定下的角色卡（门禁已验证「针对任务：…」；骨架见 references/role-card-skeleton.md）
□ phase key 含 awaiting_approval 语义时与正文一致，无「口头阶段与文末矛盾」
□ 阶段 4：每角色独立调用或已标注 director_monologue / 压缩模式
□ plan.md 含 `plan_version`；**全量**模板须含 Owner、依赖、验收标准；**lite** 至少含交付物路径与验收（见 `plan-lite.md`）；阶段 6 前满足「用户确认」一节任一条件
□ 未经确认不进入阶段 6；workshops 敏感内容已考虑是否进 .gitignore
□ 阶段 6：已做 **6a 扫描装配** 再 **6b 执行**（见 `06-phase_6_execution.md` §0）；技能选用对照 **`AGENTS.md` + `TOOLS.md`（任务相关节）+ `skills/<name>/SKILL.md`**；多步已按需落盘 `skill-pipeline.md` 或在 `execution-log.md` 留装配摘要（见 `skill-composition.md`）
□ 子 agent：每跳有结束说明或导演已补录（见 `references/subagent-closure.md`）；session 结束时 `state.md` 含 **Session 状态** + **结束与归档**
```
