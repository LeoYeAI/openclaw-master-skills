# 方案确认后的技能扫描与装配（阶段 6 子流程）

在用户已确认 `plan.md`（`approved_at` 已写入）之后，由**主 Agent（导演）**结合**任务描述**与**已有技能**完成执行。Orchestrator **不**自动做技能语义匹配（无技能模型）。

**执行顺序（与 `scripts/phases/06-phase_6_execution.md` §0 一致）**：**先**完成「技能扫描与装配」（读 **`AGENTS.md`** → 按任务读工作区根 **`TOOLS.md`** 相关节 → 打开候选 **`skills/<name>/SKILL.md`**），**再**按 SKILL 执行。装配可只记在对话/`execution-log.md`；`skill-pipeline.md` 是可选加重，**不是**跳过扫描的借口。

## 默认 vs 加重（推荐）

| 方式 | 何时用 |
|------|--------|
| **默认（轻量）** | **直接读任务**：用户原话、`plan.md` §6、`deliverables/` 中的清单均可；再查 **`AGENTS.md` + `TOOLS.md`（与任务相关的小节）+ 相关 `skills/<name>/SKILL.md`**，配对技能后**直接执行**。步骤少、路由清晰时**不必**写 `skill-pipeline.md`。 |
| **加重（可选）** | 多步骤、**多技能串联**、需复盘或交接时，再落盘 **`skill-pipeline.md`**（见 §5），避免遗漏与争议。 |

不变的红线：**禁止凭记忆捏造技能名**；互斥与「不适用」以 `AGENTS.md` 为准。

---

## 1. 设计目标

| 目标 | 说明 |
|------|------|
| **可复现** | 同一 `plan.md` + 同一套 `skills/`，装配结果应稳定、可审计 |
| **不虚构技能** | 只选用 `workspace/skills/<name>/SKILL.md` 真实存在且 `AGENTS.md` 可路由到的项（或用户声明启用的第三方技能） |
| **先想清楚再执行** | 复杂时在纸上（或 `skill-pipeline.md`）排好序；简单任务可在脑内完成配对 |
| **人机分界** | 低置信度或互斥技能并存时，**停下来问用户**一句，而不是静默猜 |

---

## 2. 技能目录从哪来（扫描范围）

按优先级阅读，合并成**导演脑内的技能索引**。简单任务只读表即可；**复杂执行**再考虑落盘快照（见 §5）。

1. **`AGENTS.md` 的「技能路由」表** — 人类维护的类别、触发词、**不适用**说明（如 **生图落地包** 内 xhs-card vs baoyu-xhs-images），优先级最高。
2. **`TOOLS.md`（工作区根）** — 本机路径、浏览器/Obsidian/cron、飞书附件、基础库、**生图/生视频端到端**；阶段 6 按任务**点开相关节**，与 `SKILL.md` 一起构成可执行上下文。
3. **`skills/*/SKILL.md` 的 YAML frontmatter** — `name`、`description`、`version`；`description` 是**语义匹配的主信号**。
4. **`openclaw.json` / `skills-lock.json`（若存在）** — 第三方技能是否启用、是否与本地 `skills/` 重名。

**禁止**：凭训练记忆捏造技能名；若描述模糊，打开对应 `SKILL.md` 读「使用方法 / 不适用」再决定。

---

## 3. 装配算法（导演执行；可从「读任务」一步开始）

```
读任务（含 plan / deliverables）
    → A 枚举原子任务（简单任务可只有 1 步）
    → B 为每任务打「能力标签」（可选，步少时可省略）
    → C 用 §2 索引做技能候选排序
    → D（可选）输出流水线文件 + 依赖 + 人工确认点
    → 按序执行并更新 plan / execution-log
```

### A. 枚举原子任务

从以下来源拆成**不可再拆的一步一事**（每步对应一次 skill 调用或明确的外链人工步骤）：

- `plan.md` §6 执行清单；
- `deliverables/` 内文档中的「制作步骤 / 执行清单」表；
- 若二者冲突，以 **`plan.md` + 用户最新口头确认** 为准；若已写 `skill-pipeline.md`，在表中注明冲突处理。

### B. 能力标签（示例，可扩展）

用于**粗筛**，不必穷举：

| 标签 | 含义示例 |
|------|----------|
| `search_fact` | 搜索、事实核查 |
| `text_long` | 长文写作、新闻、SEO |
| `image_prompt` | 文生图**提示词**（不直接出图） |
| `image_gen` | 单张/系列**出图**（卡片、信息图等） |
| `doc_office` | PPT/Excel/Word/PDF |
| `browser_auto` | 浏览器自动化 |
| `publish_xhs` | 小红书发布链路 |
| `data_sql` | 数据库导出等 |
| `human_design` | 仅人能做（Figma 精修、实拍等）— **必须显式标出** |

一步可对应多个标签；装配时选**覆盖标签且 `AGENTS.md` 未写「不适用本任务」**的技能。

### C. 候选排序规则

1. **触发词 / 场景** 与当前子任务字面或语义命中（查 `AGENTS.md`）。
2. **`description` 与任务一致性**（读 `SKILL.md` 首段）。
3. **路径最短**：能用单一技能完成的，不拆成两条（除非中间需人工审核）。
4. **已声明的互斥**（如「单张卡片 vs 多图系列」）遵守 `AGENTS.md` 的区分说明。

若两名候选分数接近 → 记入 **「待用户二选一」**，不要默认。

### D. 依赖与顺序

- **数据流**：前一步产出文件路径 / 结构化字段，作为下一步输入，在流水线表中写清。
- **并行**：仅当无数据依赖时允许两步并行（例如三张图三条独立提示词）；否则**严格串行**。

---

## 4. 与工作坊角色的关系

- **多角色研讨**解决的是「做什么、验收标准是什么」；
- **技能装配**解决的是「用哪把锤子」；
- 若某步只有 `human_design`，仍在流水线中占一行，Owner 写 **「用户 / 设计外包」**，避免 Agent 假装已执行。

---

## 5. 可选落盘：`workshops/<session_id>/skill-pipeline.md`

**多技能、多步骤或需要交接/审计时**，在首次执行任意工具**之前**创建（可与 `execution-log.md` 并存）。单步、单技能可省略。

| 序号 | 原子任务 | 能力标签 | 选用技能 | 输入 | 输出 | 依赖序号 | 状态 |
|------|----------|----------|----------|------|------|----------|------|
| 1 | … | … | `name` | … | 文件路径 | - | ☐ |

文末可加：

- **扫描时间**：ISO 时间
- **索引依据**：已读 `AGENTS.md` + 列出本次引用过的 `skills/<name>/SKILL.md`
- **未选用技能**：曾考虑但排除的 1～2 个及**一行理由**（防止事后争议）

---

## 6. 质量检查（导演自检）

```
□ 选用技能均在 skills/ 下真实存在（若写了 skill-pipeline.md，则表中每项可查）
□ 无与 AGENTS.md「不适用」冲突的选用
□ 含人工步骤时已标 human_design，且未用脚本冒充完成
□ 若使用 skill-pipeline.md：执行完成后 execution-log 或 plan 状态列与 pipeline 序号可对齐
```

---

## 7. 可选演进（非必须）

- 小型脚本：遍历 `skills/*/SKILL.md` 抽取 `name` + `description` 生成 `skills-index.generated.md`，减少漏读；**装配决策仍由 LLM + AGENTS 规则完成**。
- **执行脚本落盘**：对已选定的工具链（如 OpenRouter + `xhs-card-generator` 客户端），可用 **`workshops/scripts/generate_execution.py`**（`--preset` 或 **`--from-plan`** 读 `plan.md` 的 `execution_preset` / `execution_prompts_file`）向 `workshops/<sid>/scripts/` 写入可运行脚本，见 **`workshops/scripts/README.md`**。
- 若未来 Orchestrator 增加「阶段 6a：skill_pipeline_validated」类门禁，需先有机器可读 schema 与校验器；当前以文档与导演自检为主。
