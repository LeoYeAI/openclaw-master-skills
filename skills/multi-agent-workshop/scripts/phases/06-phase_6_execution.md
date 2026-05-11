# 阶段 6：plan 执行 — `phase_6_execution`

## 脚本**不能**替代的
- 具体 **skills / 工具调用**由 OpenClaw 内 LLM 按 `plan.md` 执行。

---

## 调用 `skills/` 工作区技能（执行阶段核心流程）

凡本 skill 与 `AGENTS.md` 所写 **`skills/<技能名>/SKILL.md`**，均相对于**工作区根目录**（本仓库即 `workspace/`；在 Cursor 中与 **`@workspace/skills`** 为同一目录）。阶段 6 **必须**按下列顺序做，**禁止**仅凭记忆捏造技能名、脚本路径或参数。

### 0. 强制顺序：两节拍（先扫描，再执行）

| 节拍 | 名称 | 做什么 | 未完成时 |
|------|------|--------|----------|
| **6a** | **技能扫描与装配** | 对照 `plan.md` 执行清单**逐步**：读 **`AGENTS.md`** → 读工作区根 **`TOOLS.md`** 中与任务相关的节（见下）→ 为每步锁定候选 **`skills/<name>/SKILL.md`**（打开文件，确认适用/不适用）→ 可选落盘 **`skill-pipeline.md`** | **禁止**调用外部 API、禁止凭「习惯」手写替代方案（如随意 HF/自建 HTML 冒充成稿） |
| **6b** | **按技能执行** | 严格按各 **`SKILL.md`** 的入口与环境约定执行，并与 **`TOOLS.md`** 本机配置对齐；产出路径写入 `execution-log.md` 或更新 `plan.md` 状态 | — |

**`TOOLS.md`（工作区根，与 `@workspace/TOOLS.md` 同文件）在 6a 中怎么用**：不要求每次全文通读；凡执行清单涉及下列能力，**必须**打开对应小节后再装配/执行，避免路径、密钥、流程与文档漂移。

| 任务涉及 | 在 `TOOLS.md` 中对照 |
|----------|----------------------|
| Chrome / 浏览器自动化 | **浏览器**（`openclaw.json`、CDP） |
| Obsidian、对话记忆检索 | **Obsidian 知识库**、**双源记忆策略** |
| 定时任务、日志路径 | **定时任务 (cron)** |
| 飞书发文件 | **飞书附件发送** |
| Excel/PDF/MySQL 等经基础库 | **基础库** |
| 生图提示词 → 出图、生视频、MiniMax | **技能库：生图与生视频**（含「图片/视频提示词调用哪一个」与端到端流程） |
| 其它「本机怎么配」 | 从 `TOOLS.md` 目录式浏览；与 **`SKILL.md` 冲突时以 SKILL 为准**，并在 `execution-log.md` 写一行说明 |

**可以「不走某个 skill」的唯一情况**：`AGENTS.md` 与 `skills/` 中**确实无**覆盖该原子步骤的能力 —— 须在 **`execution-log.md`**（或 `skill-pipeline.md` 末行）写 **一行排除理由**，并把该步标为 **`human_design`** 或「外链人工工具」，**不得**静默用未在装配里出现的第三方接口顶替。

> **常见误解**：「步骤少就不用扫描」❌ —— 步骤少时**仍须完成 6a**；可只在对话或 `execution-log` 用两三句话写清「查了 AGENTS、选用/排除了谁」，**不必**强制写长文 `skill-pipeline.md`。

### 1. 路由与选型（6a 的展开）
1. 读工作区根目录 **`AGENTS.md`** 的「技能路由」表：按用户任务 / `plan.md` 执行清单匹配**类别与触发词**，注意表内**互斥**说明（例：新闻长图 vs 小红书卡片）。
2. 读工作区根 **`TOOLS.md`**：按上表「任务涉及 → 小节」点开；**静态图**须走 **主技能** `image-prompt-generator` → **「生图落地包」**择一；**视频**先 `video-prompt-guide` 再 `generate_video.py` 等（见 `TOOLS.md`）。
3. 确定 `<技能名>` 后，打开 **`skills/<技能名>/SKILL.md`**（不是只看表内一行描述）。以该文件为**执行主依据**：入口脚本、环境变量、输出目录、红线与「不适用」；本机路径与 cron 等以 **`TOOLS.md`** 为补全。

### 2. 执行方式（6b）
- **遵循 SKILL.md 正文**：多数技能要求先 `Read` 完整 `SKILL.md` 再跑命令；若 SKILL 内写了 **`SKILL_DIR`** 或绝对路径，按该 skill 约定调用（勿改成错误 cwd）。
- **对齐 `TOOLS.md`**：浏览器配置、Obsidian 路径、cron、飞书附件流程、`minimax-output/` 约定等，按 `TOOLS.md` 执行；与某条 `SKILL.md` 不一致时**以 SKILL 为准**，并记入 `execution-log.md`。
- **产出位置**：默认可执行成果进当前工作坊 **`workshops/<session_id>/deliverables/`**；若目标 skill 强制其它目录（例：`minimax-output/` 在 agent cwd），在 `plan.md` 或 `execution-log.md` **写清路径**，避免验收对不上。
- **安全与边界**：仍遵守 `AGENTS.md` / `TOOLS.md`（如「先问再做」的对外操作）；阶段 6 不自动获得豁免。

### 3. 复杂串联（可选加重）
- 多技能、多步骤、需审计/交接：在执行任意工具**前**可落盘 **`workshops/<session_id>/skill-pipeline.md`**，并与 `execution-log.md` 或 `plan.md` 状态列对齐。
- 装配算法、流水线表格模板、质量自检：见 **`references/skill-composition.md`**（与本阶段配套）。

### 4. 与 `generate_execution.py` 的关系
- 若 `plan.md` 已写 `execution_preset` / `execution_prompts_file` 等，可用 **`workshops/scripts/generate_execution.py --from-plan`** 生成可跑脚本；生成后仍须对照**真实** `skills/*/SKILL.md` 核对依赖与环境，见 **`workshops/scripts/README.md`**。

---

## 导演检查清单
- [ ] `plan.md` 用户确认章节已勾选（或等价自然语言已记录；全量模板为 §8，lite 模板为 §6）
- [ ] **节拍 6a 已完成**：执行清单逐步做过 **AGENTS → SKILL.md** 扫描与装配；未走 skill 的步骤有 **排除理由** + `human_design`/人工标注
- [ ] 交付物在 **`deliverables/`**（若适用）
- [ ] **节拍 6b**：已按上节读 **`AGENTS.md` + 对应 `skills/<name>/SKILL.md`** 执行，未虚构技能名/路径
- [ ] 逐项勾选执行清单或写 `execution-log.md`
- [ ] **每次** subagent/工具链跳：有「结束说明」或导演已补录（`references/subagent-closure.md`）
- [ ] **Session 收口**：`state.md` 更新 **Session 状态**（`completed` / `stopped` / `cancelled`）+ **结束与归档**（时间、交付物列表）
- [ ] 可选：对用户一句话结案（状态 + 交付物路径）

## 参考
- `SKILL.md`「阶段 6」、`references/skill-composition.md`、`references/subagent-closure.md`
- 工作区 **`AGENTS.md`**、**`TOOLS.md`**、`skills/<技能名>/SKILL.md`
