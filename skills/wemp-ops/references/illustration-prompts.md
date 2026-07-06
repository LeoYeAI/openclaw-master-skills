# 正文配图指南

用于公众号文章正文中的信息图、概念图、流程图等配图。封面图见 cover-image-guide.md。

---

## 一、Type × Style 二维矩阵

插图由两个独立维度决定：**Type（画什么类型的图）** 和 **Style（用什么视觉风格）**。

### Type（信息类型）

| Type | 适用场景 | 内容信号关键词 |
|------|---------|---------------|
| `framework` | 方法论、模型、架构、分层体系 | 架构、分层、模型、组件、系统、四大支柱 |
| `flowchart` | 流程、工作流、步骤、决策树 | 步骤、流程、先…再…然后、第一步、工作流 |
| `comparison` | 对比、前后、选择、优劣 | vs、对比、优势、劣势、区别、before/after |
| `infographic` | 数据、指标、统计、趋势 | 数字、百分比、增长、数据、指标、排名 |
| `scene` | 叙事、故事、情感、体验 | 我、经历、记得、那天、叙事语气 |
| `screenshot` | 真实产品界面、代码、终端 | 代码块、命令行、产品名+界面描述 |

### Style（视觉风格）

#### Style A：notion-sketch（默认，推荐）

Notion/Linear 官方插画风手绘线条。技术/产品/方法论文章首选。

```
# 视觉风格
- 以单一主色为主（根据文章主题选择：科技蓝 #4A90D9 / 活力橙 #FF6B35 / 极客绿 #2ECC71）
- 线条粗细不均匀，像马克笔随手画的质感
- 笔触松弛、略带抖动，不追求工整
- 简笔画人物：圆润的头、点或线表示五官
- 不要彩色渐变或复杂配色
- 不要粗黑边框或生硬分隔线
- 不要 3D 效果、阴影、立体感
- 文字简化为核心关键词（3-5字），不密集堆砌
- 保持大量留白和呼吸感
```

#### Style B：tech-flat（适合数据/架构类）

极简扁平化科技信息图。

```
极简扁平化科技信息图。
配色限定为深蓝(#1E3A5F)、电光蓝(#3B82F6)、纯白、浅灰(#F1F5F9)。
线条简洁有力(2-3px均匀粗细)，造型几何化干净，纯色填充，零纹理。
白色背景，无阴影，无渐变，高对比度。
中文文字采用无衬线字体，仅提取核心关键词（3-5字），绝不大段文字。
图标使用线性简笔风格，保持统一视觉语言。
整体风格：专业、克制、信息密度适中。
```

#### Style C：warm-doodle（适合故事/教育类）

白纸手绘知识图，手账/板书感。

```
白纸背景手绘知识图，无横线无网格。
黑色细线笔轮廓（像 0.5mm 中性笔手绘）。
彩色标记点缀：青色(#06B6D4)、橙色(#F97316)、柔和红色(#EF4444)。
拟人化角色承载抽象概念（详见角色映射表）。
高信息密度但用短句（3-5字标签）承载，不用长段文字。
手写体感觉的文字标注。
整体风格：亲切、可爱、信息量大但不杂乱。
```

**角色映射表（我们公众号的固定隐喻）：**
- Agent → 🦞 小龙虾（OpenClaw 品牌元素）
- 记忆/知识 → 📚 小书架 / 图书馆
- 错误/Bug → 💥 爆炸星号
- 用户/PM → 圆头简笔人物（蓝色T恤）
- 数据流 → 虚线箭头 + 水滴
- Token → 小方块 / 积木

**warm-doodle 子模板：**
- **机制图**：主体居中 + 内部运作展开 + 输入输出箭头
- **对比图**：左右分区 + 中间差异标注（✓ vs ✗）
- **步骤图**：从左到右或从上到下 + 编号圆圈 + 角色引导

#### Style F：morandi-journal（莫兰迪手帐风）

适合生活感悟、感性话题、非技术类文章。

```
手绘涂鸦插画风，莫兰迪色调。
背景：暖米色纸纹(#F5F0E6)。
主色：灰绿(#7BA3A8) 用于标题和边框。
辅助色：赭石橙(#D4956A) 用于数字和高亮。
线稿：深棕炭笔(#4A4540)，手绘涂鸦质感，略不规则。
装饰：和纸胶带条纹、虚线边框、角落小插画（星星、小房子、云朵）。
波浪线分割区域。手写体标题，干净手写体正文。
圆角卡片容器包裹内容项。
不要数字化精确图形、emoji、纯白背景、企业感。
横版，比例 16:9。中文。

内容：[在此描述要可视化的内容]
```

适用：个人成长感悟、温情故事、非技术类总结

---

#### Style G：subway-map（地铁线路图风）

适合复杂路线/路径的可视化。

```
地铁线路图风格信息图。
背景纯白或极浅灰。
线路用粗圆角线条（4-6px），每条线路一种颜色。
站点用圆形节点标记，换乘站用双圆圈或大圆圈。
站名用简洁无衬线标签，水平或45度倾斜。
线路仅用直线和90度/45度转弯，不用曲线。
图例在角落标注线路名称+颜色。
极简，无装饰，专注于路径和连接关系。
横版，比例 16:9。中文。

内容：[在此描述要可视化的内容]
```

适用：多路径并行的复杂流程、技能树/学习路径、多线程项目进度

---

#### Style H：chalkboard（黑板粉笔风）

适合教育科普、教学讲解。

```
黑板粉笔风格信息图。
背景：深墨绿黑板色(#2C3E2D)，有微弱粉笔灰尘纹理。
文字和图形：白色粉笔(#F0F0F0)为主。
强调色：黄色粉笔(#F4D03F)、粉色粉笔(#EC7063)、蓝色粉笔(#5DADE2)。
所有线条有粉笔的粗糙颗粒质感，不均匀。
手写体文字，字迹有粗细变化像真实粉笔书写。
可以有粉笔擦除痕迹、虚线框、手绘箭头。
整体感觉像老师在黑板上边讲边画。
横版，比例 16:9。中文。

内容：[在此描述要可视化的内容]
```

适用：概念科普、原理讲解、教程类文章

---

### 兼容矩阵（更新）

| Type ＼ Style | notion-sketch | tech-flat | warm-doodle | real-capture | mermaid | morandi | subway | chalkboard |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `framework` | ⭐⭐ | ⭐⭐ | ⭐ | ✗ | ⭐⭐ | ⭐ | ✗ | ⭐⭐ |
| `flowchart` | ⭐⭐ | ⭐ | ⭐⭐ | ✗ | ⭐⭐ | ✗ | ⭐⭐ | ⭐⭐ |
| `comparison` | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ | ⭐⭐ | ⭐ | ✗ | ⭐ |
| `infographic` | ⭐ | ⭐⭐ | ✗ | ✗ | ✗ | ⭐ | ✗ | ⭐ |
| `scene` | ⭐ | ✗ | ⭐⭐ | ✗ | ✗ | ⭐⭐ | ✗ | ✗ |
| `screenshot` | ✗ | ✗ | ✗ | ⭐⭐ | ✗ | ✗ | ✗ | ✗ |

---

#### Style D：real-capture（真实截图）

不使用 AI 生图，截取真实界面 + 美化。

```bash
# 截图美化
<WORKSPACE>/scripts/beautify-screenshot.sh <input> [output] --shadow --bg "#f5f5f5"
```

### 兼容矩阵

| Type ＼ Style | notion-sketch | tech-flat | warm-doodle | real-capture |
|---|:---:|:---:|:---:|:---:|
| `framework` | ⭐⭐ | ⭐⭐ | ⭐ | ✗ |
| `flowchart` | ⭐⭐ | ⭐ | ⭐⭐ | ✗ |
| `comparison` | ⭐⭐ | ⭐⭐ | ⭐ | ⭐ |
| `infographic` | ⭐ | ⭐⭐ | ✗ | ✗ |
| `scene` | ⭐ | ✗ | ⭐⭐ | ✗ |
| `screenshot` | ✗ | ✗ | ✗ | ⭐⭐ |

> ⭐⭐ 强推荐 | ⭐ 可用 | ✗ 不推荐

#### Style E：mermaid-render（结构化信息图）

用 Mermaid 语法生成 → HTML 渲染 → 浏览器截图。适合信息准确性 > 视觉美感的技术类插图。

**适用 Type**：`flowchart`、`comparison`、`framework`
**不适用**：`scene`、`infographic`、`screenshot`

**兼容矩阵补充**：

| Type ＼ Style | mermaid-render |
|---|:---:|
| `framework` | ⭐⭐ |
| `flowchart` | ⭐⭐ |
| `comparison` | ⭐⭐ |
| `infographic` | ✗ |
| `scene` | ✗ |
| `screenshot` | ✗ |

**选择条件**：
- ✅ 技术文章 + 内容是流程/架构/对比 + 需要信息精确可读
- ✅ 文章中有明确的步骤序列、组件关系、方案对比
- ❌ 小红书（视觉风格太"技术"）
- ❌ 需要品牌感/角色/情感的配图
- ❌ 封面图

**Mermaid 渲染→截图工作流**：

1. **生成 Mermaid 代码**（遵守语法规范，见下方）
2. **写入临时 HTML**：
   ```bash
   # 模板路径
   <WORKSPACE>/scripts/mermaid-render.html
   ```
   将 Mermaid 代码注入 HTML 模板（白底、大字号、宽画布）
3. **浏览器截图**：
   ```
   browser action:open url:file:///tmp/openclaw/mermaid-render.html
   browser action:act kind:resize width:2560 height:1440
   browser action:screenshot type:png
   ```
4. **裁剪/优化**（如需要）：`sips` 裁剪白边
5. **产出文件**放入文章的 `images/` 目录

**Mermaid 语法关键规范**（完整参考：content-collector/references/mermaid-syntax-rules.md）：
- `1. ` 触发列表错误 → 用 `①`/`(1)`/去空格
- subgraph 带空格 → `subgraph id["显示名"]`
- 节点引用用 ID，不用显示文本
- 不用 Emoji
- 配色使用 `style` 声明语义色（绿=正面、红=问题、紫=处理、青=输出）

**字号建议**（公众号阅读场景）：
- Mermaid 默认字号偏小，HTML 模板中设置 `fontSize: 20` + `fontFamily: 'PingFang SC', sans-serif`
- 节点文字保持 3-8 个字，长文本拆分为多行

---

## 一-B、信息图布局选择（Type 补充维度）

当 Type 为 `framework` / `infographic` / `flowchart` / `comparison` 时，可进一步选择具体的信息图布局。

→ **详见 `infographic-layouts.md`**（8 种专业布局：bento-grid、iceberg、funnel、hub-spoke、bridge、hierarchical-layers、linear-progression、dense-modules）

**选择时机**：确定 Type 后、构造 prompt 前，检查内容是否匹配某个信息图布局。匹配则在 prompt 的 Layout 层引用对应布局的 Prompt 指导词。

---

## 一-C、结构化中间层（Structured Content）

**目的**：在"配图计划"和"prompt 组装"之间，增加一个数据逐字引用的检查点，防止 AI 在生图 prompt 中篡改文章数据。

**触发条件**：当配图涉及文章中的具体数据、术语、引用时，先输出 structured-content 再组装 prompt。

**格式**：

```markdown
## 配图 N: [标题]

**Key Concept**: [一句话概括这张图要传达什么]

**Content (逐字引用原文)**:
- "[文章中的精确数据/术语，一字不改]"
- "[文章中的精确引用，保留原始格式]"

**Text Labels (图中精确文字)**:
- Headline: "[精确标题文字]"
- Labels: "[标签1]", "[标签2]", "[标签3]"

**Visual Element**:
- Type: [framework/flowchart/comparison/infographic]
- Layout: [从 infographic-layouts.md 选择，如 hub-spoke]
- Structure: [具体构图描述]
```

**逐字引用规则**：
- ✅ "73% 的 PM 认为" → 精确引用
- ❌ "大部分 PM 认为" → 不允许模糊化
- ✅ "MEMORY.md → topics/ → memory/" → 保留原始路径
- ❌ "记忆索引 → 主题 → 日志" → 不允许意译
- 所有数字、百分比、人名、产品名必须与原文一致

**工作流**：
```
配图计划表 → structured-content.md → prompt 文件（LDSCS-R 六层）
                   ↑ 数据检查点
```

---

## 二、内容信号自动匹配

根据段落内容关键词自动推荐 Type 和 Style：

| 内容信号 | 推荐 Type | 推荐 Style |
|---------|-----------|-----------|
| "架构"、"分层"、"模型"、"组件"、"系统" | `framework` | notion-sketch / tech-flat / **mermaid-render**（技术文优先） |
| "步骤"、"流程"、"先…再…然后"、"第一步" | `flowchart` | notion-sketch / warm-doodle / **mermaid-render**（技术文优先） |
| "vs"、"对比"、"优势"、"劣势"、"区别" | `comparison` | tech-flat / notion-sketch / **mermaid-render**（技术文优先） |
| 数字、百分比、"增长"、"数据"、"指标" | `infographic` | tech-flat |
| "我"、"经历"、"记得"、"那天"、叙事语气 | `scene` | warm-doodle |
| 代码块、命令行、产品名+界面描述 | `screenshot` | real-capture |

**mermaid-render 选择指引**：技术/产品类文章中的流程、架构、对比图，当信息精确性和可读性比视觉美感更重要时，优先选 mermaid-render。生活/故事/情感类文章不用。同一篇文章中 mermaid-render 和 AI 生图可以混用（如：架构图用 Mermaid，场景图用 warm-doodle），但不超过 2 种渲染方式。

**混合信号优先级：** screenshot > framework > flowchart > comparison > infographic > scene

---

## 三、自动配图位置推荐

### 定位规则（按优先级）

1. **在显式标题后**：每个 `##` 标题后的第一段，是潜在配图点
2. **在概念首次出现时**：文章引入新概念/术语时，用插图辅助解释
3. **在转折/对比处**：出现"但是"、"然而"、"相比之下"时适合对比图
4. **在总结/提炼处**：段落在总结前文多个要点时适合框架图
5. **在长文本断裂处**：连续超过 800 字无任何图片/代码块/列表时，插入视觉元素

### 配图目的分类（定位后判断）

每个配图位确定后，判断它属于哪类目的，据此选择不同 Type 和 Style：

| 目的 | 说明 | 推荐 Type | 推荐 Style |
|------|------|----------|-----------|
| **信息传递** | 图表达的是数据/结构/逻辑关系 | framework, flowchart, comparison, infographic | tech-flat, mermaid-render, notion-sketch |
| **概念隐喻** | 图表达的是抽象概念的具象化 | framework, scene | warm-doodle, notion-sketch, chalkboard |
| **情感氛围** | 图表达的是感受/场景/画面感 | scene | warm-doodle, morandi-journal |

**关键原则**（借鉴 baoyu-article-illustrator）：
> **Metaphors → visualize the underlying concept, NOT the literal image.**
> 文章说"把大象装进冰箱"→ 画的是"步骤分解方法论"，不是真的冰箱和大象。

### 密度选择（写作开始前确定）

| 密度级别 | 配图数 | 适用场景 | 组成 |
|---------|--------|---------|------|
| `minimal` | 1-2 张 | 时间紧/短文(<1500字)/文字本身即核心 | 封面 + 可选结构图 |
| `balanced` | 3-4 张 | **默认推荐**，大多数文章 | 封面 + 结构图 + 1-2 正文 |
| `per-section` | 每章节1张 | 长文/教程/重点文章 | 封面 + 结构图 + 每##标题一图 |
| `rich` | 5-6 张 | 视觉驱动型/重要文章 | 封面 + 结构图 + 3-4 正文 |

**参考**（密度级别与文章长度的关系）：

| 文章长度 | 建议密度 | 典型配图数 |
|---------|---------|-----------|
| < 1500 字 | minimal | 1-2 张 |
| 1500-2500 字 | balanced | 3-4 张 |
| 2500-3500 字 | balanced 或 per-section | 4-5 张 |
| 3500+ 字 | per-section 或 rich | 5-6 张 |

**规则**：
1. 写作开始前，根据文章长度和重要性选择密度级别
2. 选定后记入配图计划表头部（`密度：balanced`）
3. 生图过程中不随意增减，除非老板指定
4. 硬上限仍为 **6 张**（含封面+结构图）
5. 宁缺毋滥：不确定要不要配图 → 不配

### 配图计划表输出格式

```markdown
## 配图计划

**全文风格锁定：** Style = notion-sketch | 主色 = 科技蓝 #4A90D9 | 背景 = 纯白

| # | 位置 | Type | 渲染方式 | 内容描述 | 必要性 |
|---|------|------|---------|---------|--------|
| 0 | 封面 | - | AI 生图 | 文章主题封面 | 必要 |
| 0.5 | 封面后 | framework | mermaid-render | 全文结构总览图 | 推荐 |
| 1 | §2 标题后 | framework | mermaid-render | Agent 记忆分层架构 | 必要 |
| 2 | §4 对比段 | comparison | mermaid-render | 方案 A vs B 对比 | 推荐 |
| 3 | §6 总结前 | scene | AI 生图 | 场景示意图 | 可选 |
```

**渲染方式选择**：`AI 生图`（Seedream/nano/ComfyUI）或 `mermaid-render`（Mermaid→截图）。同一篇文章可混用，但不超过 2 种渲染方式。

---

## 四、Prompt 结构化构造规范（LDSCS-R 六层）

所有插图 prompt 必须包含以下 6 层结构：

### L - Layout（布局）
**先描述构图和分区，再描述内容。**
- framework："centered main title box, radiating outward to 4 connected sub-modules"
- flowchart："left-to-right flow with 4 stages connected by arrows"
- comparison："split vertically into left and right halves with a divider"
- infographic："3 horizontal zones: top header, middle data cards, bottom summary"

### D - Data（真实数据）
**标签必须用文章中的真实术语和数字，不用占位符。**
- ✅ "MEMORY.md (index) → topics/ (details) → memory/ (daily logs)"
- ✅ "200K tokens → context explosion → session crash"
- ❌ "Layer 1 → Layer 2 → Layer 3"
- ❌ "Component A → Component B"

### S - Semantics（语义颜色）
**用颜色传达含义，不是装饰。**
- 🔴 红色/橙色 = 问题、风险、错误、告警
- 🟢 绿色 = 解决方案、效率、正面结果
- 🔵 蓝色 = 技术、系统、中性信息
- ⚫ 灰色 = 背景、次要信息、已完成

### C - Characters（角色/隐喻，仅 warm-doodle）
**将抽象概念具象化为可爱角色。**
- 参照上方角色映射表
- ⚠️ **绝不把比喻画成字面意思**：文章说"把大象装进冰箱"→ 画的是"步骤分解方法论"，不是真的冰箱和大象

### S - Style（风格块）
**直接引用对应风格的标准 prompt 块**（从上方 Style A/B/C 中复制），确保全文一致。

### R - Ratio（宽高比）
- 正文插图：16:9（Seedream 用 `2560x1440`）
- 封面图：2.35:1（`2560x1440` 生成后 `sips -c 1090 2560` 裁剪）
- 结构图：16:9（`2560x1440`）

### Prompt 组装示例

```
# Layout
A hand-drawn sketch diagram showing a layered architecture.
Central rectangle labeled "Agent" at top, with 3 layers branching downward.

# Data (from article)
Top layer: "MEMORY.md" (index, < 2KB)
Middle layer: "topics/" (user-profile, projects, tools, rules)
Bottom layer: "memory/YYYY-MM-DD.md" (daily logs, events, decisions)
Arrows connecting layers, labeled "compaction writes up" and "session reads down".

# Style
[插入 notion-sketch 风格块]

# Semantics
Blue (#4A90D9) for system components, orange (#FF6B35) for data flow arrows, gray for background labels.

# Constraints
No 3D effects, no gradients, no dense text blocks.
Aspect ratio 16:9, high quality.
Do not include any photographic elements.
Do not render long sentences in the image — use short labels (3-5 characters) only.
```

---

## 四-B、Type-Specific 填空模板

LDSCS-R 是通用结构。下方是每种 Type 的**具体填空骨架**——确定 Type 后复制对应模板，填入文章真实数据。

### framework（架构/框架图）

```
[标题] — 概念框架

Layout: [hierarchical / network / matrix / radial]
（如有信息图布局匹配，引用 infographic-layouts.md 的 Prompt 指导词）

NODES:
- [概念1] — [角色/定义，逐字引用原文]
- [概念2] — [角色/定义]
- [概念3] — [角色/定义]

RELATIONSHIPS: [节点如何连接，箭头方向和含义]
LABELS: [文章原文术语，一字不改]
COLORS: [语义配色，引用 LDSCS-R 的 S 层]
STYLE: [引用锁定的风格块]
ASPECT: 16:9
```

### flowchart（流程图）

```
[标题] — 流程视图

Layout: [left-to-right / top-to-bottom / circular]

STEPS:
1. [步骤名，原文] — [简述]
2. [步骤名] — [简述]
3. [步骤名] — [简述]
（如有决策分支：Step 2 → YES: Step 3 / NO: Step 4）

CONNECTIONS: [箭头类型，实线=主流程，虚线=可选]
LABELS: [文章原文步骤名]
STYLE: [引用锁定的风格块]
ASPECT: 16:9
```

### comparison（对比图）

```
[标题] — 对比视图

LEFT SIDE - [选项A名称，原文]:
- [要点1，逐字引用]
- [要点2]
- [要点3]

RIGHT SIDE - [选项B名称，原文]:
- [要点1，逐字引用]
- [要点2]
- [要点3]

DIVIDER: [中间分隔方式：垂直线 / vs标记 / 渐变过渡]
COLORS: [左=正面色(绿/蓝)，右=问题色(红/灰)，或中性双色]
LABELS: [文章原文标签]
STYLE: [引用锁定的风格块]
ASPECT: 16:9
```

### infographic（数据/信息图）

```
[标题] — 数据可视化

Layout: [grid / radial / hierarchical / timeline]
（引用 infographic-layouts.md 的对应布局）

ZONES:
- Zone 1: [数据点，含精确数字，逐字引用]
- Zone 2: [对比/趋势，含指标]
- Zone 3: [总结/结论]

LABELS: [精确数字/百分比/术语，逐字引用原文]
COLORS: [语义配色]
STYLE: [引用锁定的风格块]
ASPECT: 16:9
```

### scene（氛围/叙事图）

```
[标题] — 氛围场景

FOCAL POINT: [画面主体]
ATMOSPHERE: [光照、环境、时间段]
MOOD: [要传达的情感：温暖/紧张/宁静/...]
COLOR TEMPERATURE: [warm / cool / neutral]
CHARACTERS: [如有人物，引用角色映射表]
STYLE: [引用锁定的风格块]
ASPECT: 16:9
```

**使用方式**：选定 Type → 复制对应模板 → 填入文章真实数据 → 套上 LDSCS-R 的 S/C/S/R 层 → 完整 prompt。

---

## 五、全文视觉一致性锁定

**一篇文章一套视觉参数，开始生图前确定，中途不改。**

### 锁定项（全文不变）

| 参数 | 说明 | 示例 |
|------|------|------|
| Style | 全文统一一种风格 | notion-sketch |
| 主色调 | 一个主色 | 科技蓝 #4A90D9 |
| 辅助色 | 最多 1 个辅助色 | 活力橙 #FF6B35 |
| 背景 | 统一背景色 | 纯白 / 浅灰 #F8F9FA |
| 线条 | 统一线条特征 | 不均匀手绘 2-3px |
| 人物 | 如有人物，锁定外观 | 圆头简笔画，蓝色T恤 |
| 中文字体描述 | 统一字体方向 | 无衬线，简洁 |

### 允许变化项

- **Type**：不同段落可用不同类型（framework / flowchart / comparison）
- **内容布局**：每张图的构图可以不同
- **语义颜色**：红/绿/蓝/灰 用法不变，但具体元素不同

### 风格锚点

生成第一张图后，记录成功图的关键特征作为"风格锚点"。后续图片 prompt 末尾附加：

```
Maintain visual consistency with previous illustrations:
- Same hand-drawn line style with uneven thickness
- Same color palette: primary #4A90D9, accent #FF6B35, background white
- Same minimalist Notion-style aesthetic
- Same simple stick-figure character design if people appear
```

将风格锚点保存到 `prompts/style-anchor.md`，每次生图时引用。

### Ref 图三级使用

当有参考图片（历史成功图/外部风格参考/品牌素材）时，分三级使用：

| 用法 | 说明 | 操作 |
|------|------|------|
| `direct` | 直接作为视觉参考传给生图模型 | Seedream 图生图模式传 ref |
| `style` | 只提取风格特征，不传文件 | 分析图的线条/质感/构图 → 写入 prompt |
| `palette` | 只提取配色方案，不传文件 | 吸取 3-5 个主色 hex → 写入 prompt COLORS 层 |

**决策规则**：
- 参考图和目标图**同类型**（都是封面 / 都是 framework 图） → `direct`
- 参考图**风格好但内容不同** → `style`
- 参考图**颜色好但风格不同** → `palette`
- 没有参考图 → 不用 ref，走标准 prompt 流程

**操作方式**：
- `direct`：将参考图作为 Seedream/Gemini 的 image reference 输入（需 API 支持图生图）
- `style`：在 prompt 末尾追加 `STYLE (from ref): 清爽线条，微弱阴影，...`
- `palette`：在 prompt 的 COLORS 部分用提取的 hex 值替代默认色

**典型场景**：
- 同一篇文章的第 2-N 张图 → `direct` 引用第 1 张成功图（与风格锚点配合）
- 看到某篇文章的封面风格好 → `style` 提取其视觉特征
- 品牌素材提供了色板 → `palette` 提取色值

---

## 六、禁止清单

- ❌ **不生成与内容无关的装饰性图片**——每张插图必须传递信息
- ❌ **不在图中生成长段文字**——AI 文字渲染不可靠，用短标签（3-5字）
- ❌ **不把比喻画成字面意思**——画底层概念，不画字面场景
- ❌ **不连续放 2 张以上同类型插图**——避免视觉单调
- ❌ **不用彩色渐变/3D效果/阴影**——除非特定风格要求
- ❌ **不用 emoji 替代图标**——截图时 emoji 会变成色块
- ❌ **不在同一篇文章中混用 2 种以上 Style**——视觉割裂
- ❌ **不直接传 inline prompt 给 Seedream/Gemini**——⛔ 必须先存 `prompts/NN-{type}-{slug}.md`，再引用文件内容生图。好处：失败时改文件重试不用重新构思，全部 prompt 有存档可回溯

---

## 七、生图工具优先级

**Seedream 5.0 Lite → nano-banana-pro → ComfyUI**

| 工具 | 优势 | 劣势 | 使用场景 |
|------|------|------|---------|
| Seedream 5.0 Lite | 0.22元/张、无水印、质量高 | 需 API Key | 主力生图 |
| nano-banana-pro (Gemini) | 免费、3 Key 轮换 | 需去水印、额度限制 | 备选/快速迭代 |
| ComfyUI (本地) | 无费用、无限制 | 需启动、MPS 较慢 | 兜底 |

```bash
# Seedream
<WORKSPACE>/scripts/seedream-generate.sh "prompt" output.jpg "2560x1440" 1

# nano-banana-pro (Gemini)
<WORKSPACE>/scripts/generate-image.sh "prompt" output.png

# 去水印（nano-banana-pro 生图用）
<WORKSPACE>/scripts/remove-watermark.sh <input> [output]
```

---

## 八、Prompt 文件持久化

每篇文章的配图 prompt 保存为独立文件，便于回溯和复用。

### 文件结构

```
wemp-article-NN/
├── draft-v1.md
├── illustration-plan.md          # 配图计划表
├── prompts/                      # prompt 资产
│   ├── style-anchor.md           # 风格锚点（全文一致性参数）
│   ├── 00-cover.md               # 封面图 prompt
│   ├── 00-structure.md           # 结构图 prompt
│   ├── 01-framework-xxx.md       # 正文插图 prompt
│   ├── 02-comparison-xxx.md
│   └── 03-flowchart-xxx.md
└── images/
    ├── cover.jpg
    ├── structure.png
    ├── 01-framework-xxx.png
    ├── 02-comparison-xxx.png
    └── 03-flowchart-xxx.png
```

### Prompt 文件格式

```markdown
---
type: framework
style: notion-sketch
position: §2 "记忆系统设计" 后
purpose: 展示 Agent 记忆的分层架构
ratio: 16:9
tool: seedream
---

# Prompt

[完整的生图 prompt，按 LDSCS-R 六层结构]

# 生成记录
- v1: 2026-03-15 — 文字不清晰，重新生成
- v2: 2026-03-15 — ✅ 最终采用
```
