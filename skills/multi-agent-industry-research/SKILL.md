---
name: industry-research
description: |
  Multi-agent collaborative industry research for OpenClaw. Dynamically assigns
  research roles, runs parallel research via sessions_spawn with codex/gemini/claude
  CLI augmentation, iterative quality review, merge & converge, outputs structured
  Markdown report.

  All parameters are configurable via environment variables or interactive setup.

  Trigger: /research, 行业调研, industry research, 调研报告
metadata:
  openclaw:
    emoji: "\U0001F50D"
    homepage: https://github.com/shineliang/industry-research-skill
    requires:
      anyBins:
        - codex
        - gemini
        - claude
---

# 多智能体协同行业调研（OpenClaw 版）

协调多个 sub-agent 并行完成行业调研，通过迭代审核和合并收敛产出高质量报告。

## Commands

```
/research <topic>                    # 启动行业调研（如：/research AI Agent 行业现状）
/research <topic> --depth=deep       # 深度调研模式
/research <topic> --depth=quick      # 快速概览模式
```

## Prerequisites

- **OpenClaw** — 主 agent 运行时（需启用 `sessions_spawn` 和 `exec` 工具）
- **Codex CLI** (`codex`) — 可选，提供 OpenAI 模型补充视角
- **Gemini CLI** (`gemini`) — 可选，提供 Google 模型补充视角
- **Claude CLI** (`claude`) — 可选，提供 Anthropic 模型补充视角
- CLI 工具未安装不影响核心流程，仅跳过补充视角

## 可配置参数

优先级：**环境变量 > 启动时用户选择 > 默认值**

| 参数 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| 研究 agent 数量 | `RESEARCH_AGENT_COUNT` | `auto` | 设为数字则固定，`auto` 则动态分配 |
| 研究迭代上限 | `RESEARCH_MAX_ROUNDS` | `3` | 研究阶段最多迭代几轮 |
| 合并迭代上限 | `MERGE_MAX_ROUNDS` | `2` | 合并阶段最多迭代几轮 |
| 质量总分阈值 | `QUALITY_THRESHOLD` | `35` | 满分 50，总分需达到此值 |
| 单项最低分 | `QUALITY_MIN_PER_DIM` | `6` | 满分 10，每个维度不低于此值 |
| 交叉验证模式 | `RESEARCH_CROSS_MODEL` | `cli` | `cli` / `native` / `both` / `none`，见下方说明 |
| 启用 CLI 工具 | `RESEARCH_CLI_TOOLS` | `codex,gemini,claude` | 可选值：`codex`、`gemini`、`claude`、`none` 或组合 |
| CLI 超时 | `RESEARCH_CLI_TIMEOUT` | `600` | 秒 |
| Native 模型列表 | `RESEARCH_MODELS` | _(空)_ | 如 `anthropic/claude-sonnet-4-6,google/gemini-2.5-pro,openai-codex/gpt-5.4` |
| 输出语言 | `RESEARCH_LANG` | `zh` | `zh` 中文 / `en` 英文 |
| 报告深度 | `RESEARCH_DEPTH` | `standard` | `quick` / `standard` / `deep` |

### 交叉验证模式

不同 AI 模型有不同的知识覆盖、推理偏好和盲区。让多个模型分别分析同一问题，能有效提升调研质量。

| 模式 | 说明 | 适用场景 |
|------|------|----------|
| `cli` | 研究 agent 在自己的分析完成后，**必须**调用 CLI 工具（codex/gemini/claude）对关键发现做交叉验证。CLI 使用订阅账号，无额外 API 费用。**这是默认模式。** | 没有购买多个模型 API 的用户 |
| `native` | 不同研究 agent 通过 `sessions_spawn` 的 `model` 参数使用不同模型原生运行。每个 agent 拥有完整工具链。需要配置 `RESEARCH_MODELS`。 | 已购买多个模型 API key 的用户 |
| `both` | 结合两者：不同 agent 用不同模型 + agent 内部再用 CLI 交叉验证 | 追求最高质量的用户 |
| `none` | 所有 agent 使用默认模型，不做交叉验证 | 快速调研或预算有限 |

**native 模式下的模型分配策略**：
- 将 `RESEARCH_MODELS` 中的模型轮询分配给研究 agent
- Reviewer 使用与多数研究 agent 不同的模型
- Merger 使用与 Reviewer 不同的模型
- 示例：`RESEARCH_MODELS=anthropic/claude-sonnet-4-6,google/gemini-2.5-pro,openai-codex/gpt-5.4`

### 深度预设

| 参数 | quick | standard | deep |
|------|-------|----------|------|
| Agent 数量 | 2-3 | 3-5 | 5-8 |
| 研究迭代上限 | 1 | 3 | 10 |
| 合并迭代上限 | 1 | 2 | 3 |
| 质量总分阈值 | 30 | 35 | 40 |
| web_search 最少关键词数 | 3 | 5 | 10 |

## 工作流

### 阶段 0：配置加载与确认

收到调研主题后，**先完成配置再开始调研**：

1. **检查历史调研残留（防污染）**：
   用 `exec` 扫描工作目录下是否存在历史调研产出：
   ```bash
   ls -d */round-1 */merged */output 2>/dev/null | sed 's|/.*||' | sort -u
   ```
   - **如果发现历史调研目录**：向用户列出这些目录及其创建时间，并询问：
     > 检测到以下历史调研目录，它们可能干扰本次调研（旧报告内容可能被误引用、旧 progress/task_plan 可能干扰状态判断）：
     > - `{dir1}/` ({date1})
     > - `{dir2}/` ({date2})
     >
     > 是否清理？
     > - **A：归档到 `_archive/` 后开始**（推荐 — 移走但不删除）
     > - **B：直接删除后开始**
     > - **C：保留，直接开始**（不推荐）
   - 同时检查工作目录根下的孤立状态文件（`progress.md`、`task_plan.md`、`findings.md`、`tmp/`、`generated/`），一并列入清理范围。
   - 用户选 A 时：`mkdir -p _archive && mv {dirs} _archive/`，同时移走孤立状态文件。
   - 用户选 B 时：`rm -rf {dirs}` 及孤立状态文件。
   - 用户选 C 或无历史残留时：跳过，继续下一步。
   - **重要：等待用户回复后再继续。**

2. 用 `exec` 读取环境变量：
```bash
echo "RESEARCH_DEPTH=${RESEARCH_DEPTH:-standard}"
echo "RESEARCH_AGENT_COUNT=${RESEARCH_AGENT_COUNT:-auto}"
echo "RESEARCH_MAX_ROUNDS=${RESEARCH_MAX_ROUNDS:-}"
echo "MERGE_MAX_ROUNDS=${MERGE_MAX_ROUNDS:-}"
echo "QUALITY_THRESHOLD=${QUALITY_THRESHOLD:-}"
echo "QUALITY_MIN_PER_DIM=${QUALITY_MIN_PER_DIM:-}"
echo "RESEARCH_CROSS_MODEL=${RESEARCH_CROSS_MODEL:-cli}"
echo "RESEARCH_CLI_TOOLS=${RESEARCH_CLI_TOOLS:-codex,gemini,claude}"
echo "RESEARCH_CLI_TIMEOUT=${RESEARCH_CLI_TIMEOUT:-600}"
echo "RESEARCH_MODELS=${RESEARCH_MODELS:-}"
echo "RESEARCH_LANG=${RESEARCH_LANG:-zh}"
```

3. 如果设置了 `RESEARCH_DEPTH`，先应用对应预设，再用环境变量中的具体参数覆盖

4. 检查 CLI 工具可用性：
```bash
command -v codex && codex --version || echo "CODEX_UNAVAILABLE"
command -v gemini && gemini --version || echo "GEMINI_UNAVAILABLE"
command -v claude && claude --version || echo "CLAUDE_UNAVAILABLE"
```
如果配置了某 CLI 但不可用，自动从 `RESEARCH_CLI_TOOLS` 中移除并提示用户。

5. **检测当前 session 模型（模型继承）**：
   子 agent 必须继承主 session 当前使用的模型，而非回退到 openclaw.json 默认值。
   你（主 agent）应当知道自己当前运行的模型 ID（例如 `openai-codex/gpt-5.3-codex-spark`、`openai-codex/gpt-5.4`、`google/gemini-2.5-pro` 等）。
   如果不确定，可用 `exec` 尝试获取：
   ```bash
   curl -s http://localhost:18789/api/session/info 2>/dev/null | python3 -c "import json,sys; print(json.load(sys.stdin).get('model','UNKNOWN'))" || echo "UNKNOWN"
   ```
   将模型 ID 记录为 `inheritedModel`，写入 config.md。
   **后续所有 `sessions_spawn` 调用必须传入 `model: {inheritedModel}`，确保子 agent 与主 session 使用同一模型。**

6. 向用户展示配置表并请求确认（直接输出，等待用户回复）：
   - 选项 A：使用当前配置开始
   - 选项 B：调整参数（逐项询问需修改的值）
   - 选项 C：切换为深度调研模式
   - 选项 D：切换为快速调研模式

**重要：输出选项后停止，等待用户回复再继续执行。**

7. 创建项目目录，将最终配置写入 `{topic-slug}/config.md`：
```bash
mkdir -p "{topic-slug}/round-1" "{topic-slug}/merged" "{topic-slug}/output"
```

### 阶段 1 + 2：主题分析 → 立即 spawn 研究 agent

**关键：阶段 1 和阶段 2 必须在同一个 turn 内连续完成，不得中间回复用户后停下。**

用户确认配置后，在同一个 turn 中完成以下所有步骤：

1. **分析主题**：拆解调研领域，识别 3-8 个关键维度
2. **动态生成角色**，每个角色包含：
   - 角色名称和代号（如 `market-analyst`、`tech-trend`）
   - 调研范围和具体任务描述
   - 关键问题清单（3-5 个必答问题）
   - 推荐 CLI 工具（Codex/Gemini/Claude/仅 web_search）
3. 用 `write` 写入 `brief.md`
4. **不要停下，不要等待用户确认角色方案，立即执行下一步：**

5. **立即用 `sessions_spawn` 逐个启动 N 个研究 agent**（每个用不同 label）。这是必须调用的工具，不可跳过：

**cli 模式**（默认）：所有 agent 继承主 session 模型，prompt 中包含 CLI 交叉验证指令
```
sessions_spawn({ task: "...(含 CLI 交叉验证指令)", label: "researcher-market-analyst", model: "{inheritedModel}", mode: "run", runTimeoutSeconds: 900 })
sessions_spawn({ task: "...(含 CLI 交叉验证指令)", label: "researcher-tech-trend", model: "{inheritedModel}", mode: "run", runTimeoutSeconds: 900 })
```

**native 模式**：每个 agent 指定不同 model（从 RESEARCH_MODELS 轮询分配）
```
sessions_spawn({ task: "...", label: "researcher-market-analyst", model: "anthropic/claude-sonnet-4-6", mode: "run", runTimeoutSeconds: 900 })
sessions_spawn({ task: "...", label: "researcher-tech-trend", model: "google/gemini-2.5-pro", mode: "run", runTimeoutSeconds: 900 })
sessions_spawn({ task: "...", label: "researcher-app-scenario", model: "openai-codex/gpt-5.4", mode: "run", runTimeoutSeconds: 900 })
```

**both 模式**：指定不同 model + prompt 中包含 CLI 交叉验证指令

6. 用 `write` 将所有返回的 `{runId, childSessionKey, label}` 记录到 `{topic-slug}/round-{N}/tracking.md`

7. 回复用户通知："已启动 N 个研究 agent，正在并行调研，完成后我会汇总。"

8. **等待 announce 消息**：每个 sub-agent 完成后会自动发送 announce 回主 session。收到 announce 时：
   - 用 `read` 读取该 agent 的产出文件 `{topic-slug}/round-{N}/agent-{role-slug}.md`
   - **将产出的"核心发现"和"交叉验证小结"章节内容发送给用户**，格式如：
     > ✅ Agent {label} 已完成 ({completed}/{total})
     > **核心发现：**
     > 1. xxx
     > 2. xxx
     > **交叉验证：** {一致/矛盾要点}
   - 这样用户可以实时检查每个 agent 的产出质量

9. **兜底机制**：如果等待超过合理时间，用 `sessions_list` 检查未完成 agent 状态

10. **收到所有 announce 后（包括失败的），立即执行以下操作，不得停下：**
    - 用 `exec` 检查 `{topic-slug}/round-{N}/` 下有哪些 `agent-*.md` 文件
    - 统计成功/失败数量，通知用户
    - 如果 ≥50% agent 有产出 → **立即 spawn reviewer**（进入阶段 3）
    - 不要说"我会接着收口"然后停下——这会中断整个流程

### 阶段 3：审核与迭代

1. 用 `sessions_spawn` 启动 reviewer agent：
```
sessions_spawn：
  task: {Reviewer Prompt}
  label: "reviewer-round-{N}"
  model: "{inheritedModel}"
  mode: "run"
  runTimeoutSeconds: 600
```

2. 等待 reviewer 的 announce 消息
3. 用 `read` 读取 `{topic-slug}/round-{N}/review.md`，**将评审结果发送给用户**：
   > 📋 **第 {N} 轮评审结果：{通过/不通过} — 总分 {X}/50**
   > | 维度 | 得分 |
   > |------|------|
   > | （各维度评分表） |
   > **需改进：** {关键修改指令摘要}
4. 根据评分决策：
   - **通过**（总分 ≥ `QUALITY_THRESHOLD` 且单项 ≥ `QUALITY_MIN_PER_DIM`）→ 进入阶段 4
   - **不通过且轮次 < `RESEARCH_MAX_ROUNDS`** → 回到阶段 2（spawn 新 agent，prompt 中包含上轮产出 + 反馈）
   - **不通过且已达上限** → 通知用户并等待决策

### 阶段 4：合并收敛

1. 用 `sessions_spawn` 启动 merger agent：
```
sessions_spawn：
  task: {Merger Prompt}
  label: "merger-{M}"
  model: "{inheritedModel}"
  mode: "run"
  runTimeoutSeconds: 900
```

2. 等待 merger 的 announce，用 `read` 读取合并稿，**将执行摘要发送给用户**：
   > 📄 **合并稿已完成**，执行摘要：
   > {执行摘要内容}
3. 用 `sessions_spawn` 启动 reviewer 审核合并稿，写入 `{topic-slug}/merged/review-{M}.md`
4. **将合并稿审核结果发送给用户**（同阶段 3 格式）
5. 判断逻辑同阶段 3，上限为 `MERGE_MAX_ROUNDS`

### 阶段 5：最终输出

1. 用 `read` 读取通过审核的合并稿
2. 最终格式化和润色
3. 用 `write` 写入 `{topic-slug}/output/report.md`
4. 向用户展示报告摘要和文件路径

---

## Agent Prompt 模板

### 研究 Agent Prompt

spawn 每个研究 agent 时，使用以下 prompt（替换 `{...}` 变量）：

```
你是行业调研团队的 {角色名}（{角色代号}）。

## 你的任务
{来自 brief.md 的角色定义和任务描述}

## 必答问题
{来自 brief.md 的关键问题清单，每个问题单独一行}

## 工作流程
1. 使用 web_search 搜索相关信息（至少搜索 {config.minSearchKeywords} 个不同关键词，覆盖中英文）
2. 整理初步研究结果，识别核心发现
3. 调用 {推荐的 CLI 工具} 获取补充视角（遵循下方 CLI 调用协议）
4. 按照输出模板格式，用 write 将研究报告写入文件：{目标文件路径}
5. 完成后返回结果

{如果是迭代轮次 > 1，包含以下段落：}
## 上轮产出和反馈
请先用 read 阅读以下文件：
- 你的上轮产出：{上轮文件路径}
- Reviewer 反馈：{review 文件路径}

重点关注 reviewer 对你（{角色名}）的具体修改指令，逐条落实。保留上轮中已获好评的内容，只改进被指出的问题。
{/如果}

## 输出模板（必须严格遵循此格式）

# {调研维度名称}

> 调研员：{角色名} | 轮次：{N} | 日期：{今日日期}

## 核心发现
1. {发现1 — 一句话概括}
2. {发现2}
3. {发现3}
（3-5 条）

## 详细分析

### {子主题 1}
{分析内容，包含数据、趋势、案例}

### {子主题 2}
{分析内容}

## 数据与信源
| 数据点 | 数值 | 来源 | 可信度 |
|--------|------|------|--------|
| {数据名} | {具体数值} | {来源名称和链接} | {高/中/低} |

## 交叉验证（CLI 模式下必填，native/none 模式删除此节）
> 以下为通过不同 AI 模型对核心发现的交叉验证结果

### {CLI 工具名} 验证结果
{CLI 返回的分析 — 重点标注与你的发现一致或矛盾的部分}

### 交叉验证小结
| 核心发现 | 本 agent 结论 | CLI 验证结论 | 是否一致 |
|----------|--------------|-------------|---------|
| {发现1} | {你的结论} | {CLI 结论} | 一致/矛盾/补充 |

## 风险与不确定性
- {不确定因素1}
- {不确定因素2}

## 待深入研究
- {可进一步挖掘的方向}

## CLI 交叉验证（当 RESEARCH_CROSS_MODEL 为 cli 或 both 时，此步骤必须执行，不可跳过）

完成 web_search 和初步分析后，**你必须用 exec 调用 CLI 工具对核心发现做交叉验证**。详细步骤见 references/cross-validation.md。

简要流程：
1. `exec`: 将核心发现写入 `/tmp/research-cross-validate.txt`
2. `exec`: 调用推荐 CLI（如 `cat /tmp/research-cross-validate.txt | gemini -p "审核提示..." 2>&1`）
3. 失败则按降级链尝试下一个 CLI，全部失败标注 "[交叉验证：CLI 不可用]"
4. 将 CLI 返回整合到"交叉验证"章节
5. 清理临时文件

## 规则
- 数据必须标注来源和可信度评估
- 不要编造数据，找不到就明确标注"未找到可靠数据"
- 对不确定的判断使用"可能""推测""初步判断"等措辞
- 保持客观中立，呈现多元视角
- 优先引用一手数据和权威信源
```

### Reviewer Agent Prompt

```
你是行业调研团队的质量审核员。你的职责是严格、公正地评估调研产出的质量。

## 你的任务
审核第 {N} 轮所有调研 agent 的产出，按评分标准评审，给出结构化反馈。

## 评审标准（5 维度，各 10 分，满分 50）

| 维度 | 评分标准 |
|------|----------|
| 事实准确性 | 声明是否有据可查、数据是否标注来源、是否存在明显错误或自相矛盾 |
| 信源覆盖度 | 是否涵盖多元视角（中英文、不同机构）、是否有一手/权威信源、是否存在明显遗漏领域 |
| 分析深度 | 是否有原因分析而非仅罗列事实、是否有独到洞察、逻辑推理是否严密 |
| 内部一致性 | 各 agent 之间数据是否矛盾、同一 agent 内部论述是否自洽、结论是否与论据匹配 |
| 完整性 | 相对于 brief.md 中定义的调研范围和必答问题，覆盖率如何、有无关键遗漏 |

## 通过标准
总分 ≥ {config.qualityThreshold}/50，且每个单项 ≥ {config.qualityMinPerDim}/10

## 工作流程
1. 用 read 阅读调研简报：{brief.md 路径}
2. 用 read 逐个阅读所有 agent 产出：{各文件路径列表}
3. 按 5 个维度逐一打分
4. 交叉验证各 agent 之间的数据一致性
5. 对每个 agent 写出具体、可执行的修改指令
6. 做出通过/不通过决定
7. 用 write 按以下模板写入文件：{review.md 路径}
8. 完成后返回结论（通过/不通过 + 总分）

## 输出模板（必须严格遵循）

# 第 {N} 轮评审报告

## 评审结论：{通过 / 不通过}
## 总分：{X}/50

## 各维度评分
| 维度 | 得分 | 说明 |
|------|------|------|
| 事实准确性 | {X}/10 | {一句话说明扣分/加分原因} |
| 信源覆盖度 | {X}/10 | {一句话说明} |
| 分析深度 | {X}/10 | {一句话说明} |
| 内部一致性 | {X}/10 | {一句话说明} |
| 完整性 | {X}/10 | {一句话说明} |

## 亮点
- {值得保留的优质内容}

## 逐 Agent 修改指令

### Agent: {角色名}
1. {具体修改指令 — 明确说明需要补充/修改什么、期望的产出是什么}
2. {具体修改指令}

### Agent: {角色名}
1. {具体修改指令}

## 整体建议
{对整体调研方向或方法的建议，如有}

## 规则
- 评分必须基于实际内容质量，不可随意给高分放水
- 修改指令必须具体可执行（不可只说"需要改进"，要说明改进什么、怎么改）
- 交叉验证各 agent 之间的数据，发现矛盾必须指出
- 关注信源的权威性、时效性和多元性
- 如果某 agent 产出已经很好，明确说明"保持现状"而非无病呻吟
```

### Merger Agent Prompt

```
你是行业调研团队的报告整合专家。你的职责是将多个调研 agent 的产出整合为一份完整、连贯、有洞察的行业调研报告。

## 你的任务
将以下 agent 的调研产出合并为一份统一报告。

## 工作流程
1. 用 read 阅读调研简报：{brief.md 路径}
2. 用 read 阅读调研配置：{config.md 路径}
3. 用 read 逐个阅读所有 agent 最终产出：{各文件路径列表}
4. 提取各维度的核心发现
5. 识别并处理各 agent 之间的矛盾或重叠
6. 构建完整叙事逻辑，形成有洞察的报告
7. 用 write 按以下结构输出到：{merged/draft-N.md 路径}
8. 完成后返回结果

{如果是修订轮，包含以下段落：}
## Reviewer 反馈
请先用 read 阅读 reviewer 的审核意见：{review 文件路径}
按反馈意见逐条修订报告。保留已获好评的内容。
{/如果}

## 报告结构

# {调研主题} — 行业调研报告

> 日期：{今日日期} | 调研深度：{config.depth} | 迭代轮次：{实际轮次}

## 执行摘要
{500 字以内，概括核心发现、关键数据和主要结论}

## 1. 行业概述
{行业定义、边界、发展历程简述}

## 2. {维度 1 标题}
{整合该维度所有 agent 的研究成果}

## 3. {维度 2 标题}
{整合内容}

...（按实际维度数量扩展）

## N. 关键发现与洞察
{跨维度的核心洞察，不是简单罗列而是有分析的判断}

## N+1. 风险与挑战
{整合所有 agent 提到的风险，去重并分类}

## N+2. 展望与建议
{基于分析得出的行动建议}

## 附录
### 数据来源汇总
{所有信源的汇总表}

### 调研方法说明
{本次调研使用的方法、工具、agent 角色说明}

## 规则
- 去重合并时保留最准确、最有信源支持的版本
- 对矛盾数据必须标注说明（"A 数据显示 X，而 B 数据显示 Y"），不可静默丢弃
- 保持报告的叙事连贯性，避免简单拼接各 agent 的内容
- 所有数据保留原始信源标注
- 执行摘要必须能独立阅读，包含最重要的 3-5 个发现
```

---

## 主 Agent 编排逻辑

收到 `/research <topic>` 后：

1. **阶段 0**（可与用户交互）：`exec` 读取环境变量 → 应用预设 → 检查 CLI → 展示配置**等待用户确认**→ `write` config.md
2. **阶段 1+2**（**必须在一个 turn 内连续完成，不可中途停下**）：分析主题 → 生成角色 → `write` brief.md → **立即调用 `sessions_spawn` 启动所有研究 agent** → `write` tracking.md → 通知用户已启动
3. **阶段 3**：收到所有 announce 后 → `sessions_spawn` 启动 reviewer → 等待 announce → `read` review.md → 通过/不通过决策
4. **阶段 4**：`sessions_spawn` 启动 merger → announce 后 spawn reviewer 审核
5. **阶段 5**：`read` 合并稿 → 润色 → `write` output/report.md → 展示摘要

**核心规则：**
- **模型继承**：所有模式下，`sessions_spawn` 都必须带 `model` 参数。cli/none 模式传入 `{inheritedModel}`（从主 session 继承）；native/both 模式从 `RESEARCH_MODELS` 轮询分配。**绝不可省略 model 参数让子 agent 回退到 openclaw.json 默认值。**
- **只有阶段 0 允许等待用户回复。阶段 1 到阶段 5 应连续执行。**
- **cli/both 模式下**：研究 agent 的 prompt 必须包含 CLI 交叉验证协议，且协议中明确标注"必须执行，不可跳过"。
- **native/both 模式下**：`sessions_spawn` 必须带 `model` 参数，从 `RESEARCH_MODELS` 轮询分配。Reviewer 和 Merger 使用与多数研究 agent 不同的模型。

---

## 异步 Agent 异常处理与自动推进规则

**核心原则：收到所有 announce 后（无论成功还是失败），必须立即推进到下一阶段，不得停下。**

### 自动推进规则

收到所有 N 个 agent 的 announce 后，检查产出文件：
- **≥50% 的 agent 有产出** → 立即 spawn reviewer，在 reviewer prompt 中标注缺失的维度
- **<50% 有产出** → 通知用户，询问是否重试失败的 agent 或降级继续
- **全部失败** → 通知用户并建议排查

**关键：不要因为某个 agent 失败就停下来等待或"接着收口"。失败是正常的，用现有产出继续推进流程。**

### 失败 agent 的处理

1. 检查失败 agent 的输出文件是否存在（可能 abort 前已部分写入）
2. 有部分产出 → 在 reviewer prompt 中标注 "[不完整，仅供参考]"
3. 无产出 → 在 reviewer prompt 中标注 "维度 {X} 缺失（agent 执行失败），请在评审中指出此缺失对整体质量的影响"
4. 在 merged 报告中对缺失维度标注说明，不要假装它存在

---

## 文件结构

每次调研在当前工作目录下创建：

```
{topic-slug}/
├── config.md                    # 本次调研的实际配置
├── brief.md                     # 调研简报（主题、范围、角色分配）
├── round-1/
│   ├── tracking.md              # sub-agent 跟踪信息
│   ├── agent-{role-slug}.md     # 各 agent 调研产出
│   └── review.md               # Reviewer 评审结果
├── round-2/                     # 如需迭代
│   ├── tracking.md
│   ├── agent-{role-slug}.md
│   └── review.md
├── merged/
│   ├── draft-1.md               # 合并稿
│   ├── review-1.md              # 合并稿审核
│   └── ...
└── output/
    └── report.md               # 最终报告
```
