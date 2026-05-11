# SignalRadar 上架经验教训

> 基于 SignalRadar 上架 ClawHub 全过程（2026-03-02 ~ 2026-03-03）的经验提炼。
> 包括 Claude 官方 Skill 指南学习要点和新用户体验测试发现的缺陷。

---

## 一、Claude 官方 Skill 指南学到的经验

> 基于 SignalRadar 上架重构（2026-03-02），对照 Claude 官方 Skill 编写指南和 OpenClaw 扩展规范提炼的要点。

### 1.1 SKILL.md 结构规范

**1. Skill 文件夹内禁止 README.md**

Claude 指南明确禁止在 skill 文件夹内放 README.md。doubao-asr 也没有。README 的内容应该整合进 SKILL.md，或放在 GitHub 仓库根目录。SignalRadar 此前有一个 README.md，重构时删除。

**2. Frontmatter 是触发匹配的核心**

Claude 使用 frontmatter 中的 `description` 字段做语义匹配，决定是否触发 skill。description 必须同时包含：
- **正面触发词**：用户可能说的自然语言（"check prediction markets"、"monitor Polymarket"）
- **负面排除**：明确不适用的场景（"Do NOT use for stock market analysis"）
- **双语覆盖**：如果目标用户包含中文用户，在英文描述后追加中文摘要

长度控制在 1024 字符以内。SignalRadar 的 description 为 523 字符。

**3. `allowed-tools` 字段限定执行边界**

声明 skill 只需要什么工具权限。SignalRadar 只需 `Bash(python3:*)`，不需要文件编辑、网络请求等其他权限。这是最小权限原则在 skill 层面的体现。

**4. `name` 必须是 kebab-case**

`name: signalradar`（全小写无连字符也可以）。不能用 `SignalRadar`、`signal_radar` 或 `signal-radar`。这是 slug/标识符，不是显示名称。

### 1.2 Body 写作的 Progressive Disclosure 原则

**5. 结构按用户旅程编排，不按开发者逻辑**

旧版 SKILL.md 的结构是「功能→安装→运行→配置→守护→边界→指纹」——这是开发者视角（我做了什么→你怎么用→我的约束→我的版本）。

重构后的结构是「快速开始→核心功能→理解结果→可选配置→可选调度→可选集成→排障」——这是用户旅程（装好→跑起来→看懂结果→按需定制→出问题了查这里）。

**6. AI Agent Instructions 必须放在正文第一节**

Claude 指南的 "specific and actionable" 原则要求：告诉 AI 应该怎么做、不应该怎么做。SignalRadar 加了 7 条明确指令：
- 怎么呈现 HIT 结果（用自然语言 + 关键数据，不是 raw JSON）
- 怎么呈现 NO_REPLY 结果（一句话确认，不倒 JSON）
- 不要自动创建 cron
- 不要循环运行
- 默认 mode 是 ai

这些指令和 doubao-asr 坑 6/7 的教训一脉相承：**不写 Agent Instructions，AI 会按自己的判断来，结果通常不是你想要的。**

**7. Understanding Results 是被低估的核心章节**

旧版没有这个章节——用户跑完命令，看到一堆 JSON，不知道 `BASELINE`、`SILENT`、`HIT`、`NO_REPLY` 分别意味着什么。更关键的是：AI Agent 也不知道怎么向用户呈现这些结果。

新版增加了：
- 决策结果对照表（4 种 status → 含义 → 发生了什么）
- HIT 输出的 JSON 示例
- AI 应该怎么格式化呈现 HIT 结果的模板

**经验：如果你的 skill 有结构化输出，SKILL.md 里必须有一节专门教 AI 和用户"怎么看懂输出"。这比功能说明更重要——用户不理解输出，等于 skill 没跑。**

### 1.3 应该删掉的内容

**8. 开发者工具不属于用户文档**

以下内容从旧版移除：
- 「版本指纹」节：`RELEASE_FINGERPRINT.json` 是开发者做跨环境验收用的，用户不需要知道
- 「运行守护（MVP）」节：`sr_smoke_test.py` 和 `sr_prepublish_gate.py` 是发布前检查工具
- 「重要边界」节：这些约束应该融入对应章节（不自动创建 cron → Agent Instructions，config 可选 → Configuration），单独列出显得像免责声明
- 「方式三：其他调度器」：一句"可接入任何支持 shell 命令的调度系统"没有增量信息

**原则：SKILL.md 是用户文档 + AI 行为指令，不是开发者运维手册。开发者工具放在 references/ 或 scripts/ 的注释里。**

### 1.4 OpenClaw 扩展规范

**9. `metadata.openclaw` 结构**

OpenClaw 生态需要额外的结构化 metadata：
- `emoji`：市场展示用的图标
- `requires.bins`：运行时二进制依赖（如 `python3`）
- `requires.env`：必填环境变量（空数组 = 零配置即跑）
- `requires.pip`：Python 依赖（空数组 = 纯 stdlib）
- `envHelp`：每个环境变量的结构化获取指南

SignalRadar 的核心卖点之一是**零配置即跑**（`env: []`, `pip: []`），这通过 metadata 结构化地表达出来，比在文档里写"无需配置"更可靠——安装引擎直接读 metadata 判断，不需要 AI 理解自然语言。

**10. 可选环境变量用 `envHelp` 而非 `requires.env`**

SignalRadar 只有 watchlist-refresh 模式需要 Notion 环境变量，其他三个模式完全不需要。因此：
- `requires.env: []`（空）——告诉安装引擎"不需要配置任何环境变量就能跑"
- `envHelp.NOTION_API_KEY / NOTION_PARENT_PAGE_ID`——告诉用户"如果你要用 watchlist-refresh，按这个步骤配置"

**不要把可选变量放进 `requires.env`**——安装引擎会把它们全部列为必填，用户还没跑就被 5 个环境变量吓跑了。

---

## 二、上架后新用户体验测试的教训

> 基于 2026-03-02 在 OpenClaw 上模拟新用户安装体验的完整记录，暴露了 SignalRadar v1.0.0 的多个严重缺陷。

### 2.1 API 数据格式假设错误——N/A 概率 bug

**问题**：用户监控活跃市场（以太坊价格、美伊停火），probability 字段显示 N/A。市场明明是活跃的，但 SignalRadar 说"暂无数据"。

**根因**：Polymarket gamma API 的 `outcomePrices` 字段返回的是 **JSON 编码的字符串**（如 `"[\"0.45\", \"0.55\"]"`），不是 Python 原生 list。`run_signalradar_job.py` 的 `extract_probability()` 用 `isinstance(outcome_prices, list)` 判断，永远为 False，导致概率提取失败、市场被静默丢弃。

同样的 bug 存在于 3 个文件（`run_signalradar_job.py`、`ingest_polymarket.py`、`discover_entries.py`），但 `polymarket_watchlist_refresh.py` 和 `check_new_urls.py` 用了正确的 `json.loads()` 解析。**同一个项目内，相同数据源的解析逻辑不一致——这说明代码复用和一致性审查没做到位。**

**教训**：
1. **不要假设 API 的数据类型**。即使字段名叫 `outcomePrices`（暗示是数组），实际返回的可能是字符串。第一次对接 API 时，必须打印原始响应检查实际类型。
2. **同一数据源的解析逻辑必须统一**。5 个文件解析同一个 API，有的用 `json.loads()`，有的用 `isinstance(list)`。应该提取为一个共享函数。
3. **"市场被静默丢弃"是最糟糕的失败模式**。用户看到 NO_REPLY 以为没有变化，实际上是数据根本没读到。应该区分"没变化"和"读取失败"。

### 2.2 watchlist-refresh 自动扩展——用户信任灾难

**问题**：用户只想监控 3 个特定市场，运行 `watchlist-refresh` 后发现生成了 42 个条目，包括 DeepSeek V4、Claude 5、GPT-6 等大量默认市场。用户反应："我没添加这么多啊？" → "真是垃圾。"

**根因**：`DEFAULT_KEYWORDS` 包含 5 个宽泛类别（AI Releases、AI Leaders、OpenAI IPO、SpaceX IPO、SpaceX Missions），每个类别从全市场（3000+）中关键词匹配取 top 20。即使用户只关心 3 个市场，系统也会默认塞入 40+ 个。

更严重的是：**没有任何预览或确认步骤**。用户运行 `watchlist-refresh` 后直接覆盖 watchlist 文件，没有 `--dry-run`，没有"将添加 42 个条目，确认？"，用户看到结果时已经覆盖了。

**教训**：
1. **默认行为必须最小化**。宁可让用户手动添加市场，也不要自动塞入 40 个。默认行为应该是"不添加任何非用户指定的条目"。
2. **任何批量操作必须有预览**。`--dry-run` 不是可选功能，是必须功能。用户必须在写入前看到"将生成 N 个条目"并确认。
3. **静默覆盖 = 信任灾难**。用户的情绪从"以为好了"到"愤怒"只用了 2 分钟。一次自作主张就足以让用户认为整个产品不可靠。

### 2.3 配置系统缺乏"只监控这几个市场"的能力

**问题**：用户通过 Polymarket 链接指定了 3 个市场，添加到 `config.json`，但运行时不生效。

**根因**：`config.json` 的 schema 根本没有 watchlist/entries 字段。用户写入的条目被 `deep_merge` 存储了，但没有任何代码读取它们。`ai` 模式从 MD 文件读 watchlist，`crypto`/`geopolitics` 模式纯靠硬编码关键词，都不读 `config.json` 的自定义条目。

**教训**：
1. **如果用户最自然的操作是"我要监控这个市场"，系统必须支持这个操作**。这是核心用例，不是边缘 feature。
2. **配置和文档必须一致**。如果 `config.json` 不支持添加市场，文档就不能暗示它支持。如果文档说"可选配置"，用户会期望配置能改变行为。
3. **slug 级精确控制是最小可用功能**。用户给了 Polymarket 链接，系统应该能提取 slug 并只监控这一个。

### 2.4 BASELINE 概念对新用户不友好

**问题**：用户第一次运行 `--mode ai`，返回 `BASELINE`。用户问"BASELINE 是什么？"文档虽然写了，但新用户不会先读完文档再运行。

**教训**：
1. **第一次运行的输出必须自解释**。不能假设用户读过文档。BASELINE 输出应该附带一句话："First run — baseline recorded. Run again later to detect changes."
2. **Quick Start 应该明确说"第一次运行返回 BASELINE 是正常的"**。这不是 Understanding Results 里的一行表格能覆盖的——用户的第一次运行是最关键的体验点。

### 2.5 Notion 配置缺少"Internal vs OAuth"引导

**问题**：用户按 SKILL.md 给的链接打开 Notion 集成页面，误点了 OAuth 类型（需要公司信息），以为自己配不了。实际应该选 Internal 类型。

**教训**：
1. **envHelp.howToGet 必须具体到"点哪个按钮"**——这条和 doubao-asr 坑 6 的教训完全一致，但 SignalRadar 没吸取。
2. **整合类型选择是最常见的分歧点**。几乎所有 API 集成都有 OAuth vs API Key vs Internal 等多种类型，howToGet 必须明确指定选哪个。

### 2.6 发布验收：开发者自测 ≠ 新用户体验

**核心认知**：开发者自测永远通过，因为开发者知道所有隐含假设（先建基线、默认关键词会扩展、Events API 和 Markets API 的区别）。新用户不知道这些，每一个隐含假设都是一个踩坑点。

**检查清单更新（新增项）**：
- [ ] **模拟新用户全流程**：从 `clawhub install` 到第一个 HIT，不依赖任何预知
- [ ] **第一次运行的输出自解释**：用户不读文档也能看懂
- [ ] **批量操作有预览**：`watchlist-refresh --dry-run` 等
- [ ] **配置即行为**：用户写入的配置必须影响运行结果
- [ ] **API 响应类型验证**：第一次对接新 API 时打印原始类型
- [ ] **同一数据源的解析逻辑统一**：提取为共享函数
- [ ] **AI Agent Instructions 与实际行为一致**：不能写"never modify cache/"而工具正常运行时就会写 cache
- [ ] **脚本 docstring 与 SKILL.md 一致**：不能 docstring 写"every 5 minutes scheduled job"而 SKILL.md 说"不自动创建 cron"
- [ ] **显式声明 skill 写入的文件**：在 SKILL.md 中列出所有写入路径和触发条件，避免安全扫描认为是"未披露的文件写入"

---

## 三、安全扫描被标记 Suspicious 的教训

> 基于 2026-03-03 OpenClaw Code Insight 安全扫描结果（Suspicious, medium confidence）。

### 3.1 AI Agent Instructions 与实际行为矛盾——最易触发的安全标记

**问题**：SKILL.md 的 AI Agent Instructions 写了"Never modify cache/, config/, or baseline files unless the user explicitly asks"，但工具正常运行时**必然**会写入 `cache/baselines/` 和 `cache/events/`。Code Insight 准确识别了这个矛盾："SKILL.md contains contradictory guidance"。

**根因**：写 Agent Instructions 时的思维是"告诉 AI 不要乱动文件"，但措辞过于绝对。"Never modify" 字面意思是"任何情况下都不能写"，而工具的正常操作就是写这些文件。这不是 AI 的误读——是文档自相矛盾。

**修复**：改为"Do not manually edit or delete cache/, config/, or baseline files unless the user explicitly asks. Note: normal runs automatically write baseline and cache files as part of standard operation — this is expected behavior."

**教训**：AI Agent Instructions 的措辞必须和工具的实际行为一致。安全扫描器**逐字比对**指令与代码行为——任何矛盾都会被标记。写"never"之前想清楚：工具运行时到底会不会做这件事？

### 3.2 脚本 docstring 与 SKILL.md 矛盾

**问题**：`check_new_urls.py` 的 docstring 写了"Designed to run as a lightweight scheduled job every 5 minutes"，而 SKILL.md 说"Never create cron jobs or scheduled tasks automatically"。Code Insight 将此识别为"mixed guidance could cause unexpected state changes"。

**根因**：docstring 是开发者给自己看的技术备忘，写的是"这个脚本可以怎么用"。但安全扫描器把 docstring 当作 skill 的行为声明来审——docstring 说"每 5 分钟跑一次"= 这个 skill 会创建定时任务。

**修复**：改为"Run manually or via user-configured cron when needed (not auto-scheduled)"。

**教训**：安全扫描器审的不只是 SKILL.md，**所有代码中的自然语言描述都会被审**。docstring、注释、README 中的任何暗示性描述都可能被当作行为声明。Skill 发布前应全局搜索"cron"、"schedule"、"every N minutes"等关键词，确保和 SKILL.md 的立场一致。

### 3.3 文件写入行为必须显式声明

**问题**：Code Insight 指出"several scripts will write local state"并建议"the skill will create local baseline and audit files under cache/ and memory/ during normal runs — should be acknowledged by the user"。虽然写文件是监控工具的正常行为，但 SKILL.md 没有明确列出写入哪些文件、什么时候写。

**修复**：新增"Local State (What This Skill Writes)"章节，用表格列出每个写入路径、用途和触发条件。同时明确"Use --dry-run to fetch and evaluate without writing any state"。

**教训**：安全扫描遵循"显式优于隐式"原则。即使文件写入是合理的、预期的，也必须在 SKILL.md 中**显式声明**。不声明 = 安全扫描认为你在偷偷写文件。doubao-asr 的坑 1（上传到第三方未披露）是同一类问题的极端版本——这次是"本地写入未披露"。
