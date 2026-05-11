---
name: cognitive-forge
description: "Dual-value learning system - extracts reusable mental models from books, writes individual pattern files (patterns/{id}.md) with YAML frontmatter for building compound thinking ability. Each run produces: (1) F.A.C.E.T. analysis for user learning, (2) permanent knowledge base entry for AI's decision framework library. Supports breadth/depth modes, configurable topic mapping, multi-source book selection, and brief/full output."
dependencies:
  - book-scout  # Step 1: called to search and recommend books via web search
  - mental-model-forge  # Step 2: called to perform F.A.C.E.T. analysis on selected book
permissions:
  filesystem:
    read:
      - USER.md  # Personalize [T] Transfer dimension with user's profession/projects/challenges
      - memory/reading-history.json  # Load previously analyzed books for deduplication (book titles only)
      - HEARTBEAT-reading.md  # Optional: read schedule config, topic mapping, and Feishu credentials
    write:
      - memory/knowledge-base/patterns/*.md  # Write individual model files with YAML frontmatter
      - memory/knowledge-base/concepts.md  # Append domain-specific concepts
      - memory/reading-history.json  # Record newly analyzed book + model for future deduplication
  env:
    - FEISHU_APP_TOKEN  # Optional: write analysis records to Feishu Bitable for external tracking
    - FEISHU_TABLE_ID  # Optional: target table in Feishu Bitable (used with FEISHU_APP_TOKEN)
    - NOTION_API_KEY  # Optional: alternative to Feishu, write to Notion database
    - NOTION_DATABASE_ID  # Optional: target database in Notion (used with NOTION_API_KEY)
config:
  reads:
    - USER.md
    - memory/reading-history.json
    - HEARTBEAT-reading.md
  writes:
    - memory/knowledge-base/patterns/*.md
    - memory/knowledge-base/concepts.md
    - memory/reading-history.json
  env:
    - FEISHU_APP_TOKEN
    - FEISHU_TABLE_ID
    - NOTION_API_KEY
    - NOTION_DATABASE_ID
---

# Cognitive Forge (认知锻造)

**One run, dual value** — 每次运行同时产出两个价值：

1. **用户获得** F.A.C.E.T. 深度分析，提取可立即应用的思维模型
2. **AI 获得** 永久写入 `patterns/{id}.md` 的决策框架（带 YAML frontmatter），构建可复用的思维模型库

随时间积累，你的 AI 拥有一个不断增长的决策框架库（类似 Charlie Munger 的 "latticework of mental models"），在未来任何领域的提问中都可以引用。

---

## Path Convention

> 所有路径均相对于 OpenClaw workspace 根目录（通常为 `~/.openclaw/workspace/`）。
> 如用户 workspace 位于其他位置，请将文档中的路径替换为实际 workspace 路径。

| 用途 | 相对路径 |
|------|---------|
| 阅读记录 | `memory/reading-history.json` |
| 思维框架库 | `memory/knowledge-base/patterns/*.md` (每个模型一个文件) |
| 概念库 | `memory/knowledge-base/concepts.md` |
| 用户画像 | `USER.md` |
| 调度配置 | `HEARTBEAT-reading.md` |

---

## Routing (路由分支)

根据用户意图，选择不同的执行路径：

| 用户意图 | 路由 | 说明 |
|---------|------|------|
| "生成今日读书简报" / 默认 | → **Main Workflow** (breadth) | 完整选书→分析→写入流程，提取 1 个模型 |
| "深度分析《XXX》" / "depth_mode: depth" | → **Main Workflow** (depth) | 对指定书籍连续提取多个模型，合并输出 |
| "cognitive-forge status" / "认知锻造 状态" | → **Status Branch** | 输出知识库统计 |
| "cognitive-forge review" / 周日自动触发 | → **Review Branch** | 间隔复习本周模型 |
| "分析《XXX》这本书" | → **Main Workflow** (breadth, 跳过选书) | 用户直接指定书籍，提取 1 个核心模型 |

**Depth mode 触发方式**：
1. **手动触发**：用户说"深度分析《XXX》"或传入 `depth_mode: depth`
2. **定时触发**：HEARTBEAT-reading.md 中可配置 `depth: true`，调度时传入该参数则自动走 depth mode

---

## Status Branch (知识库统计)

当用户请求查看知识库状态时：

1. 统计 `memory/knowledge-base/patterns/` 目录下 `.md` 文件数 = 模型总数
2. 读取 `memory/reading-history.json`，统计：
   - 已读书籍总数（`used_models` 数组长度）
   - 各领域分布（按 `category` 分组计数）
   - 最近 5 条记录
3. 输出格式：

```markdown
## 📊 认知锻造 · 知识库状态

**模型总数**: XX 个思维框架
**已读书籍**: XX 本
**知识库大小**: XX KB

### 领域分布
| 领域 | 模型数 | 占比 |
|------|--------|------|
| Business Strategy | 5 | 25% |
| Psychology | 3 | 15% |
| ... | ... | ... |

### 最近 5 条
1. 2026-03-27 | 《反脆弱》 | 反脆弱三元组
2. ...

### 覆盖薄弱领域
⚠️ Philosophy (0), Biography (0) — 建议补充
```

---

## Review Branch (间隔复习)

**触发方式**：
- 用户手动说 "cognitive-forge review"
- 当 HEARTBEAT-reading.md 配置了周日时段时，自动在周日 briefing 中插入复习环节

**执行逻辑**：
1. 读取 `memory/reading-history.json`，筛选最近 7 天的 `used_models` 记录
2. 随机抽取 2-3 个模型
3. 输出复习问答：

```markdown
## 🔄 本周复习：你还记得这些模型吗？

**1.「逃离机制」来自《逃离不平等》**
- 核心框架是什么？（回忆 [F]）
- 什么时候会失效？（回忆 [E]）

**2.「双系统理论」来自《思考，快与慢》**
- 它摧毁了什么常识？（回忆 [C]）
- 你上周在工作中用到了吗？

> 回复你的答案，我帮你查漏补缺。
```

---

## Main Workflow

### Step 0. Environment Check (首次使用自检)

每次运行开始时执行，静默完成（不打断用户）：

1. **检查 `memory/reading-history.json`** 是否存在
   - 不存在 → 自动创建初始文件：
     ```json
     {
       "schema_version": 1,
       "last_attempted": null,
       "queue": [],
       "used_models": []
     }
     ```

2. **检查 `memory/knowledge-base/` 目录** 是否存在
   - 不存在 → 自动创建目录

3. **检查 `memory/knowledge-base/patterns/` 目录** 是否存在
   - 不存在 → 自动创建目录

4. **检查 `memory/knowledge-base/concepts.md`** 是否存在
   - 不存在 → 创建带标题的空文件

5. **检查 `USER.md`** 是否存在
   - 不存在 → 输出提示：`💡 建议创建 USER.md（职业、兴趣、当前挑战），以获得个性化的 [T] Transfer 分析。`
   - 存在 → 静默读取，提取用户画像

6. **检查依赖 skill** 是否可用
   - `book-scout` 和 `mental-model-forge` 必须可调用
   - 不可用 → 报错并停止

7. **检查 `last_attempted` 字段**
   - 如果 `status == "failed"` → 提示用户：
     ```
     ⚠️ 上次运行在「{step}」步骤失败（书籍: {book}）。
     是否要恢复上次操作？回复"是"恢复，或"否"跳过。
     ```

### Step 1. Select Book (选书)

**选书来源优先级**（从高到低）：

#### 来源 1: 用户直接指定
如果用户明确说了 "分析《XXX》by YYY"，直接使用该书，跳过选书流程。
- 标记 `source: "user_specified"`

#### 来源 2: 预排队列
检查 `memory/reading-history.json` 的 `queue` 数组：
```json
{
  "queue": [
    {"title": "《穷查理宝典》", "author": "彼得·考夫曼", "topic": "决策科学"}
  ]
}
```
- 如果 `queue` 非空 → 取第一项，从 queue 中移除
- 标记 `source: "queue"`

#### 来源 3: book-scout 网络搜索
当 queue 为空且用户未指定时，调用 `book-scout` skill。

**确定搜索主题**：

1. 检查 `HEARTBEAT-reading.md` 是否有自定义主题映射（`## 主题映射` section）
   - 如有 → 使用自定义映射
2. 否则使用**默认星期-主题映射**：

| 星期 | 默认主题 |
|------|---------|
| Monday | Business Strategy |
| Tuesday | Psychology |
| Wednesday | Technology |
| Thursday | Economics |
| Friday | Innovation |
| Saturday | Philosophy |
| Sunday | Biography |

> **可配置**: 用户可在 `HEARTBEAT-reading.md` 中添加 `## 主题映射` section 覆盖默认值。
> 也可以按时段细分（参考 HEARTBEAT-reading.md 中的 21 主题轮转配置）。

**加载去重列表**（书名去重）：

从 `memory/reading-history.json` 提取所有 `book_title` 字段值，去重后作为已读书名列表。

> **重要**：不读取 `thinking-patterns.md` 或 `patterns/*.md`。去重只需要书名，不需要模型内容。

**调用 book-scout**：

```
主题: {topic}

已读书籍:
- 《精益创业》
- 《从0到1》
- 《影响力》

执行 book-scout skill，搜索符合主题的经典书籍。
```

**重试机制**：
- Attempt 1 失败 → 等 2s → 重试
- Attempt 2 失败 → 等 3s → 重试
- Attempt 3 失败 → 返回错误给用户：
  ```
  ⚠️ 选书失败：{error}
  已尝试 3 次。你可以直接指定书籍："分析《书名》by 作者"
  ```

**book-scout 成功返回**：
```json
{
  "book_title": "《增长黑客》",
  "author": "肖恩·埃利斯",
  "author_nationality": "美国",
  "publish_date": "2015-04",
  "rating": 8.5,
  "review_count": 10000,
  "score": 74.4,
  "summary": "增长黑客方法论...",
  "reasoning": "评分8.5且有1万真实评价..."
}
```

标记 `source: "web_search"`，进入 Step 2。

**更新 last_attempted**：
```json
"last_attempted": {
  "date": "YYYY-MM-DD",
  "book": "《增长黑客》",
  "step": "book_selection",
  "status": "success"
}
```

### Step 2. Extract Mental Model (提取思维模型)

#### Breadth Mode (默认)

调用 `mental-model-forge` skill，对选中的书进行 F.A.C.E.T. 分析，提取 **1 个核心思维模型**。

#### Depth Mode

当用户指定 `depth_mode: depth` 时，对同一本书**连续提取多个思维模型**：

**工作流**：
1. 第 1 次调用 `mental-model-forge`，提取书中最核心的思维模型
2. 将已提取的模型名称作为 `exclude_models` 参数，再次调用：
   ```
   这本书是《反脆弱》。
   exclude_models: ["反脆弱三元组"]
   请提取这本书中另一个独立的、不同的思维框架。
   ```
3. 重复直到**三重退出条件**任一触发：

| 退出条件 | 判断方式 |
|---------|---------|
| **模型数上限** | 该书已提取 5 个模型 → 停止 |
| **语义去重** | AI 判断新模型与已提取模型本质相同（同一思想的变体或换皮）→ 停止 |
| **AI 自评** | 提取后自问 "这本书还有独立的、值得提取的思维框架吗？" → No → 停止 |

4. 每提取一个模型，立即执行 Step 4-5（写入知识库 + 更新记录）
5. 所有模型提取完毕后，**合并为一份报告**执行 Step 3 + Step 6（生成简报 + 写入外部数据库）

### Step 2.5. F.A.C.E.T. Quality Verification (结构化验证)

`mental-model-forge` 返回后，执行以下自检：

- [ ] **完整性**: 5 个维度 [F][A][C][E][T] 是否都有实质内容（非空、非占位符文本）
- [ ] **[F] 字数**: Framework 是否 ≤ 80 字（中文）或 ≤ 50 words（英文）
- [ ] **[T] 个性化**: Transfer 是否引用了 USER.md 中的具体信息（职业、项目、挑战）
  - 如果 USER.md 存在但 [T] 未引用任何用户上下文 → 验证失败
- [ ] **质量自评**: 整体分析质量 1-10 分

**处理**：
- 自评 ≥ 7 分且全部检查通过 → 进入 Step 3
- 自评 < 7 分或任一检查失败 → 重新调用 `mental-model-forge`（最多重试 **1 次**）
- 重试后仍不合格 → 使用当前版本但在输出中标注 `⚠️ 本次分析质量未达标，建议后续深入阅读`

### Step 3. Generate Briefing (生成简报)

**输出模式**（默认 `full`）：

#### Full Mode (默认)

创建完整结构化简报，**必须适配用户上下文**：

**[强制步骤] 读取 USER.md**：
- Path: `USER.md`（相对于 workspace 根）
- 如果存在，提取：
  - 工作经历 / 现在 → profession
  - 兴趣 / 爱好 → interests
  - 当前焦虑 / 未来规划 → current challenges
- 如果不存在 → 使用通用第二人称（"你"），可追问用户背景

**输出结构**：

```markdown
## 📖 今日思维锚点

**书籍**: 《XXX》 - 作者
**核心一句话**: [今日思维锚点，一句话总结]

---

## 🧠 F.A.C.E.T. 认知穿透

### [F] Framework (核心框架)
[核心机制，≤80字中文]

### [A] Anchor Case (锚定案例)
[最经典的真实案例，生动讲述]

### [C] Contradiction (反共识摧毁)
❌ 被摧毁的常识: "..."
✅ 真相: ...

### [E] Edge (隐性边界)
失效条件:
1. ...
2. ...

### [T] Transfer (跨界迁移)
[映射到用户的实际上下文：职业、项目、挑战]

---

## 🎯 应用场景

| 场景 | 如何应用 | 预期效果 |
|------|---------|---------|
| [场景1：映射用户职业] | ... | ... |
| [场景2：映射用户项目] | ... | ... |
| [场景3：映射用户挑战] | ... | ... |

## 🔴 反面案例
[违反该原则的真实或假设案例]

## 🤔 战略拷问
[尖锐、具体、可行动的问题，引用用户实际上下文]
- Bad: "企业家应该怎么做？"
- Good: "你在爱康国宾的 AI 产品，是在避免失败还是利用失败？"

## 🔄 认知模式更新
**思维框架**: 看到XX → 想到XX
**决策原则**: 在XX场景下，应该XX而非XX
**盲区警告**: 小心XX情况
**反射弧**: 看到XX信号 → 联想到这个模型 → 判断/行动

---

> 💬 这个模型让你想到工作中的哪个具体场景？回复我，我帮你深入分析。
```

**个性化规则**：
- 始终用第二人称（"你的"、"你在"）
- [T] Transfer 必须引用用户具体信息（职业、项目名、公司名）
- 战略拷问必须具体到用户当前处境，不可泛泛而谈
- 应用场景 ≥ 3 个，分别映射用户的不同维度

#### Brief Mode

当用户指定 `output: brief` 时，输出精简版：

```markdown
## 📖 《书名》 - 作者

**核心框架**: [F] 一句话总结核心机制
**破除常识**: [C] 被摧毁的常识信念
**应用到你**: [T] 一个具体行动项（映射用户上下文）
**盲区**: [E] 何时失效

💡 想看完整分析？说 "展开" 即可。
```

- brief 模式同样执行完整的知识库写入流程（Step 4-6），只是输出给用户的部分精简
- 用户说 "展开" 后，输出完整 full 模式内容

#### Depth Mode Output (合并报告)

当 depth mode 提取了多个模型时，**合并为一份报告**输出：

```markdown
## 📖 深度解析：《书名》 - 作者

**提取模型数**: N 个 | **模式**: Depth

---

### 💎 模型 1: [Model Name]

**[F] 核心框架**: [一句话，≤80字]
**[A] 锚定案例**: [最经典案例，2-3句]
**[C] 破除常识**: ❌ "..." → ✅ ...
**[E] 失效边界**: [何时失效]
**[T] 迁移应用**: [映射用户上下文]

---

### 💎 模型 2: [Model Name]

（同上结构）

---

### 💎 模型 3: [Model Name]

（同上结构）

---

## 🔗 模型关联分析

| 模型 | 核心逻辑 | 适用场景 | 与其他模型的关系 |
|------|---------|---------|----------------|
| 模型1 | ... | ... | 与模型2互补 / 与模型3矛盾 |
| 模型2 | ... | ... | ... |
| 模型3 | ... | ... | ... |

## 🤔 综合战略拷问

[基于所有模型的综合视角，提出一个更深层的战略问题]
```

**关键区别**：
- 每个模型的 F.A.C.E.T. 用精简格式（各维度 1-3 句，不展开）
- 新增「模型关联分析」表格 — 展示模型间的互补/矛盾/递进关系
- 战略拷问基于所有模型的综合视角，而非单个模型

### Step 4. Update Knowledge Base (更新知识库)

**分类并存储提取的模型**。

#### 分类决策树

```
提取的知识
├─ 能否在不同领域复用为决策工具？ → YES → Thinking Pattern
├─ 是否是高度抽象的通用指导原则？ → YES → Principle
├─ 是否是领域特定的知识/术语？ → YES → Concept
└─ 边界模糊 → 标记多个 tags
```

**三种分类**：

| 类型 | 定义 | 示例 | 写入位置 |
|------|------|------|---------|
| **Thinking Pattern** | 可复用决策框架 | 颠覆性创新框架、逃离机制 | `patterns/{id}.md` |
| **Principle** | 高度抽象指导原则 | 二八法则、奥卡姆剃刀 | `patterns/{id}.md` |
| **Concept** | 领域特定知识 | 种痘术、能量密度天花板 | `concepts.md` |

> 一个条目可以同时标记多个类型（如 "杠铃策略" 既是 Thinking Pattern 又有 Concept 成分）。

**写入格式**：

**For Thinking Patterns / Principles** (写入 `memory/knowledge-base/patterns/{id}.md`):

从 `mental-model-forge` 返回的 `KB_META` 块提取 frontmatter 字段，从 FACET 维度映射正文字段：

```markdown
---
id: {from KB_META}
name_zh: {from KB_META}
name_en: {from KB_META}
source: {book_title}, {author}
category: {from KB_META}
tags: {from KB_META}
scenarios: {from KB_META}
related_models: {from KB_META}
difficulty: {from KB_META}
date: YYYY-MM-DD
---

**核心逻辑**:
{从 [F] Core Framework 提炼的一段话，比 Framework 更完整}

**思维框架**:
{直接使用 [F] Core Framework 内容}

**决策原则**:
{从 [F] + [E] 推导，格式：在XX场景下，应该XX而非XX}

**盲区警告**:
{直接使用 [E] Hidden Boundaries 内容}

**反射弧**:
{从 scenarios 推导，格式：看到XX信号 → 联想到模型 → 判断/行动}

**锚定案例**:
{直接使用 [A] Anchor Case 内容}

**反共识**:
{from KB_META contradiction field，格式：❌ "旧常识" → ✅ 新真相}
```

**FACET → 知识库字段映射表**：

| FACET 维度 | 知识库字段 | 映射方式 |
|-----------|-----------|---------|
| [F] Framework | 核心逻辑 + 思维框架 | 核心逻辑=扩展版，思维框架=原文 |
| [A] Anchor Case | 锚定案例 | 直接使用 |
| [C] Contradiction | 反共识 | 直接使用 |
| [E] Edge | 盲区警告 | 直接使用 |
| [T] Transfer | **不写入知识库** | 仅用于用户简报 |
| — | 决策原则 | 从 [F]+[E] 提炼 |
| — | 反射弧 | 从 scenarios 推导 |

> **重要**：[T] Transfer 是用户简报专用维度，包含个性化上下文（职业、项目、挑战），不写入知识库。每次生成简报时根据 USER.md 实时生成。

**For Concepts** (写入 `concepts.md`):
```markdown
## [Concept Name] - [Book Title]

**定义 (Definition)**:
- [简洁定义]

**上下文 (Context)**:
- 这个概念在什么领域/场景重要？

**关联理论 (Related Theories)**:
- 与哪些思维框架相关？

**来源**: [Book Title] - [Author]
**日期**: YYYY-MM-DD
```

**更新 last_attempted**：
```json
"last_attempted": {
  "date": "YYYY-MM-DD",
  "book": "《XXX》",
  "step": "knowledge_base_write",
  "status": "success"
}
```

### Step 4.5. Verify Knowledge Base Write (写入验证，必须执行)

**验证逻辑**：

```bash
# 验证: 检查文件是否存在
ls ~/.openclaw/workspace/memory/knowledge-base/patterns/{id}.md
```

**自检清单**：
- □ `patterns/{id}.md` 文件存在？
- □ 文件包含完整 YAML frontmatter（`---` 开头和结尾）？
- □ frontmatter 中 `date` 为当天？
- □ 正文包含所有 7 个字段（核心逻辑、思维框架、决策原则、盲区警告、反射弧、锚定案例、反共识）？

**如果验证失败** → 立即重新写入，再次验证。验证通过后才能继续 Step 5。

### Step 5. Update Reading Records (更新阅读记录)

向 `memory/reading-history.json` 的 `used_models` 数组追加新条目：

```json
{
  "date": "YYYY-MM-DD",
  "book": "书名",
  "author": "作者",
  "model": "提取的思维模型名称",
  "category": "主题分类",
  "source": "web_search | queue | user_specified",
  "applied_count": 0,
  "tags": ["thinking-pattern"]
}
```

同时更新 `last_attempted`:
```json
"last_attempted": {
  "date": "YYYY-MM-DD",
  "book": "《XXX》",
  "step": "reading_history_update",
  "status": "success"
}
```

**错误恢复策略**：
- 如果 Step 4（写入知识库）失败 → 不更新 reading-history，下次运行会重试同一本书
- 如果 Step 5（本步骤）失败 → 知识库已写入但记录未更新，`last_attempted` 标记为 failed，下次运行时提醒用户手动补录

### Step 6. Write to External Database (写入外部数据库)

**[检查] 读取 HEARTBEAT-reading.md 获取数据库配置**：
- Path: `HEARTBEAT-reading.md`
- 寻找 `## 环境配置` section
- 提取 Feishu App Token 和 Table ID
- 如未找到 → 跳过本步骤（local-only mode）

**如果配置存在，写入 Feishu Bitable**：

```javascript
feishu_bitable_create_record({
  app_token: "{from HEARTBEAT-reading.md}",
  table_id: "{from HEARTBEAT-reading.md}",
  fields: {
    "日期": Date.now(),
    "书名": "《反脆弱》",
    "作者": "Nassim Nicholas Taleb",
    "模型名称": "反脆弱三元组",
    "分类": "Innovation",
    "核心框架(F)": "系统分三类：脆弱、坚韧、反脆弱...",
    "应用场景": "产品迭代、技能学习、风险管理",
    "战略拷问": "你的产品是在避免失败还是利用失败？"
  }
})
```

**Notion Database** (alternative):
- Required: `NOTION_API_KEY`, `NOTION_DATABASE_ID`
- Map fields accordingly

**如果无凭证** → 跳过（skill 仍可本地使用）

---

## reading-history.json Schema (v1)

统一 schema 定义：

```json
{
  "schema_version": 1,
  "last_attempted": {
    "date": "2026-03-27",
    "book": "《反脆弱》",
    "step": "knowledge_base_write",
    "status": "success"
  },
  "queue": [
    {
      "title": "《穷查理宝典》",
      "author": "彼得·考夫曼",
      "topic": "决策科学"
    }
  ],
  "used_models": [
    {
      "date": "2026-03-24",
      "book": "《上瘾》",
      "author": "尼尔·埃亚尔",
      "model": "上瘾模型（Hook Model）",
      "category": "用户增长",
      "source": "web_search",
      "applied_count": 0,
      "tags": ["thinking-pattern"]
    }
  ]
}
```

**字段说明**：
- `schema_version`: 当前为 1，用于未来格式升级时的迁移判断
- `last_attempted`: 上次运行的状态快照，用于错误恢复
- `queue`: 用户预排的待读书籍队列（FIFO）
- `used_models`: 已处理的所有模型记录（追加式，不可删除）
  - `source`: 标记选书来源（`web_search` | `queue` | `user_specified`）
  - `applied_count`: 该模型被 AI 在后续对话中引用的次数（未来追踪用，初始为 0）
  - `tags`: 分类标签数组（`thinking-pattern` | `principle` | `concept`）

**迁移指引**：
如果你已有旧格式的 `reading-history.json`（只有 `used_models` 数组，无 `schema_version`），只需手动添加以下顶层字段：
```json
{
  "schema_version": 1,
  "last_attempted": null,
  "queue": [],
  "used_models": [... 保留原有数据 ...]
}
```

---

## Depth Mode Configuration

**默认**: `breadth`（每次运行处理一本新书，提取 1 个模型）

**切换方式**: 用户在对话中指定 `depth_mode: depth` 或说 "深度分析这本书"

**depth 模式详细流程**:

```
选中书籍: 《反脆弱》
│
├─ Round 1: 提取 "反脆弱三元组" → 写入 patterns/antifragility.md + reading-history
├─ Round 2: 提取 "杠铃策略" → 写入 patterns/barbell-strategy.md + reading-history
├─ Round 3: 提取 "林迪效应" → 写入 patterns/lindy-effect.md + reading-history
├─ Round 4: AI 自评 "无更多独立框架" → 停止
│
├─ 合并输出: 一份报告包含 3 个模型（精简 F/A/C/E + 🎯迁移 + 关联分析）
└─ 写入飞书: 每个模型一条记录
```

**三重退出条件**（任一触发即停止）：

1. **模型数上限**: 该书已提取 ≥ 5 个模型
2. **语义去重**: AI 判断新提取的模型与该书已提取模型本质相同（同一思想的变体或换皮表达）
3. **AI 自评**: 提取后自问 "这本书还有独立的、值得提取的思维框架吗？"，回答 No 则停止

---

## Quality Standards

**禁止**:
- 书籍摘要或作者传记
- 泛泛之谈（"这很重要"、"值得学习"）
- 重复已提取的模型（书名和模型名双重检查）
- 文学评论式语言

**要求**:
- 尖锐、可行动的语言
- 具体案例（不是抽象概念）
- 直接映射到用户上下文（不可脱离 USER.md）
- 反书评口吻（不是"推荐阅读"，而是"拿走就能用"）

---

## Configuration

**配置来源优先级**:

### 1. HEARTBEAT-reading.md (推荐)
- Path: `HEARTBEAT-reading.md`
- 可配置内容：
  - 主题映射覆盖
  - Feishu/Notion 凭证
  - 调度时间段

### 2. 环境变量 (备选)
- `FEISHU_APP_TOKEN`, `FEISHU_TABLE_ID`
- `NOTION_API_KEY`, `NOTION_DATABASE_ID`

### 3. 默认值 (兜底)
- 使用默认星期-主题映射
- 无外部数据库集成（local-only mode）

**用户上下文** (可选但强烈推荐):
- Path: `USER.md`
- 用于: 个性化 [T] Transfer、应用场景、战略拷问
- 缺失时: 使用通用第二人称，可能追问用户背景

**知识库路径** (自动创建):
- Thinking Patterns: `memory/knowledge-base/patterns/*.md` (每个模型一个文件)
- Concepts: `memory/knowledge-base/concepts.md`

---

## References

- See [example-output.md](references/example-output.md) for full and brief output format examples
- See [book-selection.md](references/book-selection.md) for multi-source selection logic and configurable topic mapping
- See [knowledge-classification.md](references/knowledge-classification.md) for three-type classification with tag system

---

*Version: 3.0.0*
*Last updated: 2026-03-28*
*Changes: Knowledge base restructure — single-file-per-model with YAML frontmatter (patterns/{id}.md), dedup via reading-history.json only (no longer reads thinking-patterns.md), FACET→KB field mapping table, KB_META extraction from mental-model-forge output, contradiction field added*
