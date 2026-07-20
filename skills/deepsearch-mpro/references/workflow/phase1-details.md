# 阶段 1：分析框架生成 - 详细流程

## 目的

给定一个**研究主题**，生成一套完整的**分析框架**，作为后续数据收集与最终报告生成的蓝图。

---

## 输入

| 输入项 | 说明 | 是否必需 |
|-------|------|---------|
| **Research Subject（研究主题）** | 要分析的话题或问题 | 是 |
| **Scope / Constraints（范围 / 约束）** | 地域范围、时间区间、行业细分、目标受众等 | 否 |
| **Specific Angles（特定角度）** | 用户希望重点探索的特定视角或假设 | 否 |
| **Domain（分析领域）** | 市场、财务、行业、品牌、消费者、投资、AI 技术、SaaS 厂商等分析领域 | 自动推断 |

---

## 详细工作流程

### Step 1.1：理解研究主题

**识别核心对象和分析领域**：

1. 解析研究主题，识别**核心对象**（市场、品牌、产品、行业、消费群体、金融工具、AI 技术产品、AI 工具、SaaS 厂商等）
2. 识别其所属的**分析领域**（市场、财务、行业、竞争、消费者、投资、宏观、AI 技术、AI 工具、AI 工具学习指南、SaaS 厂商等）
3. **根据领域按需加载对应的专项分析文档**（节约 Token）

**领域识别与文档加载**：

| 分析领域 | 核心对象示例 | 加载专项文档 |
|---------|-------------|-------------|
| **市场/竞争分析** | 市场规模、竞争格局、行业趋势 | `domains/market-analysis.md` |
| **AI 大模型厂商** | Anthropic、OpenAI、DeepSeek、豆包、智谱 | `domains/ai-vendor-analysis.md` |
| **AI 工具产品** | 文生图、文生 PPT、文生视频工具 | `domains/ai-tools-analysis.md` |
| **AI 工具学习指南** | Cursor、ChatGPT、Midjourney、豆包 PPT、即梦 | `domains/ai-tool-learning-guide-framework.md` ⭐ |
| **SaaS 厂商** | 金蝶、用友、SAP、Oracle、Salesforce | `domains/saas-vendor-analysis.md` |
| **财务/投资** | 财务分析、投资尽调、估值 | `methodology/analysis-frameworks.md`（通用框架部分） |
| **消费者洞察** | 用户画像、购买行为、决策路径 | `methodology/analysis-frameworks.md`（通用框架部分） |

**识别示例**：

```markdown
# 示例 1：研究主题"DeepSeek 大模型技术能力分析"
- 核心对象：AI 大模型厂商（DeepSeek）
- 分析领域：AI 技术分析
- 加载文档：domains/ai-vendor-analysis.md

# 示例 2：研究主题"金蝶云星空在制造业的市场表现"
- 核心对象：SaaS 厂商（金蝶）+ 产品（云星空）+ 行业（制造业）
- 分析领域：SaaS 厂商分析 + 市场分析
- 加载文档：domains/saas-vendor-analysis.md + domains/market-analysis.md

# 示例 3：研究主题"豆包 PPT 产品功能评测"
- 核心对象：AI 工具产品（文生 PPT）
- 分析领域：AI 工具产品分析
- 加载文档：domains/ai-tools-analysis.md

# 示例 4：研究主题"Cursor 学习指南"或"如何使用 ChatGPT"
- 核心对象：AI 工具（Cursor / ChatGPT）
- 分析领域：AI 工具学习指南
- 加载文档：domains/ai-tool-learning-guide-framework.md
- 输出：该工具的学习教程（工具概述、学习路径、场景案例、自学练习、学习资源）
```

**AI 技术领域快速参考**：

- **国际厂商**：Anthropic、Google、OpenAI、Microsoft、Meta、Amazon
- **国内厂商**：DeepSeek、豆包、智谱 AI、百度、阿里、腾讯
- **AI Agent/MCP/Skill/OpenClaw**：专项技术框架
- **AI 工具**：文生图（Nano Banana、豆包生图）、文生 PPT（豆包 PPT）、文生视频（即梦、可灵）

**SaaS 厂商快速参考**：

- **国际厂商**：SAP、Oracle、Salesforce、Microsoft
- **国内厂商**：金蝶、用友、浪潮

**关键分析维度**（详见加载的专项文档）：
- 产品发布与技术演进
- 市场活动与品牌建设
- 客户案例与行业覆盖
- 招投标与政企市场
- 生态活动与合作伙伴
- 战略合作与投资并购

---

### Step 1.2：选择分析框架与模型

基于识别出的领域和研究主题，从 `methodology/analysis-frameworks.md` 中选择**2-4个**最相关的分析框架。

**选择原则**：

1. **领域优先**：基于步骤 1.1 识别出的领域，选择最相关框架
2. **互补性**：优先选择互补而非重叠的框架（宏观 + 微观）
3. **重深度，轻堆砌**：深入应用 2 个框架，优于表面堆叠 6 个框架
4. **数据可得性**：所选框架必须能被后续数据收集支持

**常用分析框架**：

| 框架名称 | 适用场景 | 关键维度 |
|---------|---------|---------|
| **波特五力** | 竞争格局分析 | 现有竞争者、新进入者、替代品、买家议价、供应商议价 |
| **SWOT** | 战略定位分析 | 优势、劣势、机会、威胁 |
| **PESTEL** | 宏观环境分析 | 政治、经济、社会、技术、环境、法律 |
| **TAM-SAM-SOM** | 市场规模分析 | 总体市场、可服务市场、可获得市场 |
| **商业模式画布** | 商业模式分析 | 价值主张、客户关系、渠道通路、收入来源等 |
| **产品生命周期** | 产品阶段分析 | 导入期、成长期、成熟期、衰退期 |
| **竞争定位矩阵** | 竞争定位分析 | 价格/性能、功能/易用性等维度 |
| **价值链分析** | 企业运营分析 | 主要活动、支持活动 |

**输出格式**：

```markdown
## Framework Selection

| Chapter | Selected Framework(s) | Application |
|---------|----------------------|-------------|
| 市场规模与增长趋势 | TAM-SAM-SOM + 产品生命周期 | 用 TAM-SAM-SOM 量化市场空间，用 PLC 判断市场阶段 |
| 竞争格局评估 | 波特五力 + 战略群组图 | 用五力评估行业竞争强度，用群组图可视化竞争定位 |
```

---

### Step 1.3：设计章节骨架

生成分层章节结构。每章必须包含：

1. **章节标题** —— 专业、简洁、以主题为中心
2. **分析目标** —— 该章节希望揭示什么
3. **分析逻辑** —— 所采用的推理链路或框架（引用步骤 1.2 选定的框架）
4. **核心假设** —— 需要被数据验证或证伪的初步假设

**输出格式**：

```markdown
## Analysis Framework

### Chapter 1: [标题]
- **Analysis Objective**: [本章旨在……]
- **Analysis Logic**: [所用框架或推理链路]
- **Core Hypothesis**: [待验证的假设]
- **Data Requirements**: （见步骤 1.4）
- **Visualization Plan**: （见步骤 1.5）

### Chapter 2: [标题]
...
```

**章节设计原则**：

1. **逻辑连贯**：章节之间应有清晰的逻辑关系（问题 → 分析 → 结论）
2. **层次分明**：主要章节 3-5 个，每个章节 2-4 个小节
3. **目标明确**：每个章节都应有明确的分析目标
4. **可验证**：核心假设应能被数据验证或证伪

**典型章节结构（以市场分析为例）**：

```markdown
### Chapter 1: 市场规模与增长趋势
- Analysis Objective: 量化市场空间，判断市场发展阶段
- Analysis Logic: TAM-SAM-SOM 框架 + 产品生命周期模型
- Core Hypothesis: 市场处于成长期，年复合增长率超过 20%

### Chapter 2: 竞争格局分析
- Analysis Objective: 识别主要竞争者，评估竞争强度
- Analysis Logic: 波特五力模型 + 竞争定位矩阵
- Core Hypothesis: 行业竞争激烈，头部企业市场份额集中度提高

### Chapter 3: 消费者需求洞察
- Analysis Objective: 理解目标用户需求，识别购买决策因素
- Analysis Logic: 消费者决策旅程 + 用户画像分析
- Core Hypothesis: 价格敏感度降低，功能性需求占主导

### Chapter 4: 产品功能对比
- Analysis Objective: 对比主要产品功能，识别差异化优势
- Analysis Logic: 功能对比矩阵 + 用户体验评分
- Core Hypothesis: 产品功能同质化严重，用户体验成为差异化关键

### Chapter 5: 市场机会与威胁
- Analysis Objective: 识别市场机会和潜在威胁
- Analysis Logic: SWOT 分析 + PESTEL 宏观分析
- Core Hypothesis: 技术创新带来新机会，政策监管构成主要威胁
```

---

### Step 1.4：定义数据查询需求

为每一章明确说明**需要收集哪些数据**，以及**推荐的搜索方法**。

**每一条数据需求必须包含**：

| 字段 | 说明 |
|------|------|
| **Data Metric** | 所需的具体指标或数据点 |
| **Data Type** | 定量、定性或混合 |
| **Suggested Sources** | 建议的数据来源类别 |
| **Recommended Search Method** | 推荐的搜索方法（见下文） |
| **Search Keywords** | 搜索关键词（中英文） |
| **Priority** | P0（必须）/ P1（重要）/ P2（补充） |
| **Time Range** | 数据应覆盖的时间范围 |

**数据来源参考**：

- **AI 大模型厂商**：参考 `domains/ai-vendor-analysis.md` 中的"官方数据来源"和"快速搜索模板"
- **AI 工具产品**：参考 `domains/ai-tools-analysis.md` 中的"官方数据来源"和"快速搜索模板"
- **AI 工具学习指南**：参考 `domains/ai-tool-learning-guide-framework.md` 中的工作流程 ⭐
- **SaaS 厂商**：参考 `domains/saas-vendor-analysis.md` 中的"官方数据来源"和"快速搜索模板"
- **市场/竞争分析**：参考 `domains/market-analysis.md` 中的"搜索策略"
- **通用数据来源**：参考 `technical/ai-saas-data-sources.md`

**AI 技术与 SaaS 厂商专项数据需求**：

当研究主题涉及 AI 技术或 SaaS 厂商时，必须包含以下关键数据维度：

| 数据维度 | 关键指标 | 优先级 |
|---------|---------|--------|
| **产品发布与技术演进** | 版本更新、功能迭代、技术路线图、重大里程碑 | P0 |
| **市场活动与品牌建设** | 发布会、峰会、市场活动、品牌传播 | P1 |
| **客户案例与行业覆盖** | 标杆客户、行业解决方案、客户成功案例 | P0 |
| **招投标与政企市场** | 中标信息、政企客户、信创适配、合规认证 | P0（如涉及政企市场） |
| **生态活动与合作伙伴** | 生态大会、ISV 伙伴、开发者社区、平台开放度 | P1 |
| **战略合作与投资并购** | 战略合作、投资并购、组织调整、国际化 | P1 |

**详细的数据来源指南**，参考 `technical/ai-saas-data-sources.md`。

**搜索方法选择**：

| 数据需求类型 | 推荐搜索方法 | 说明 |
|------------|-------------|------|
| 中文市场数据 | multi-search-engine（百度、微信、头条） | 覆盖中国主流平台 |
| 国际市场数据 | multi-search-engine（Google、Bing） | 全球搜索引擎 |
| 政府统计数据 | multi-search-engine（site:gov.cn） | 限定政府网站 |
| 行业报告 | multi-search-engine + filetype:pdf | 搜索 PDF 格式报告 |
| 深度背景研究 | 混合方案：multi-search-engine + ddg-web-search | 多源验证 |
| 快速补充搜索 | ddg-web-search | DuckDuckGo 快速搜索 |

**详细的搜索引擎列表和使用方法**，参考 `technical/search-engines.md`。

**输出格式**：

```markdown
#### Data Requirements

| # | Data Metric | Data Type | Suggested Sources | Recommended Search Method | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|--------------------------|-----------------|----------|------------|
| 1 | 市场规模（亿元） | 定量 | 行业报告、政府统计 | multi-search-engine（百度、Bing） | "中国护肤市场规模 2024" | P0 | 2020-2025 |
| 2 | CAGR | 定量 | 行业报告 | multi-search-engine（Google） | "skincare CAGR growth" | P0 | 2020-2025 |
```

---

### Step 1.5：定义可视化方案

为每一章定义最终报告中计划使用的**可视化形式**。

**常见可视化类型**：

| 可视化类型 | 适用场景 | 示例 |
|-----------|---------|------|
| **数据对比表** | 多维度数据对比 | 竞品功能对比表、市场份额表 |
| **柱状图/条形图** | 数值对比 | 市场规模对比、增长率对比 |
| **折线图** | 趋势变化 | 市场增长趋势、用户增长曲线 |
| **饼图/环形图** | 占比分析 | 市场份额占比、用户构成 |
| **雷达图** | 多维度评估 | 产品功能评分、竞争力评估 |
| **矩阵图** | 定位分析 | 竞争定位矩阵、SWOT 矩阵 |
| **流程图** | 流程说明 | 用户决策旅程、商业模式画布 |
| **信息图** | 综合展示 | 核心数据概览、关键洞察 |

**输出格式**：

```markdown
#### Visualization & Content Plan

**Chart 1**: [图表类型] — [图表标题]
- X-axis: [维度], Y-axis: [指标]
- Data source: 对应 Data Requirement #1, #2

**Comparison Table**: [表格标题]
- Columns: [列头]
- Data source: 对应 Data Requirement #3, #4

**Argument Structure**:
- What: [现象描述]
- Why: [原因分析]
- So What: [战略启示]
```

**可视化设计原则**：

1. **一图一观点**：每个可视化应传达一个核心观点
2. **数据可追溯**：每个可视化都应能追溯到数据来源
3. **形式匹配**：选择最适合数据类型的可视化形式
4. **简洁清晰**：避免过度复杂，确保信息传达清晰

---

### Step 1.6：输出完整分析框架

整合以上步骤的输出，生成完整的分析框架文档，包含：

```markdown
# [研究主题] Analysis Framework

## Research Overview
- 研究主题
- 研究范围
- 核心问题

## Framework Selection
- 选定的分析框架及其应用

## Chapter Skeleton
### 1. [章节标题]
- Analysis Objective
- Analysis Logic
- Core Hypothesis
- Data Requirements
- Visualization & Content Plan

### 2. [章节标题]
...

## Data Collection Task List
- 按优先级排列的数据收集任务
```

---

## 完整示例

### 示例：护肤品市场分析框架

**研究主题**：中国护肤品市场 2024 年度分析

**Step 1.1：理解研究主题**

```markdown
- 核心对象：护肤品市场（中国）
- 分析领域：市场分析
- 加载文档：domains/market-analysis.md
```

**Step 1.2：选择分析框架**

```markdown
## Framework Selection

| Chapter | Selected Framework(s) | Application |
|---------|----------------------|-------------|
| 市场规模与增长趋势 | TAM-SAM-SOM + 产品生命周期 | 用 TAM-SAM-SOM 量化市场空间，用 PLC 判断市场阶段 |
| 竞争格局评估 | 波特五力 + 战略群组图 | 用五力评估行业竞争强度，用群组图可视化竞争定位 |
| 消费者需求洞察 | 消费者决策旅程 + 用户画像 | 理解消费者购买路径和需求特征 |
```

**Step 1.3：设计章节骨架**

```markdown
## Analysis Framework

### Chapter 1: 市场规模与增长趋势
- **Analysis Objective**: 量化中国护肤品市场空间，判断市场发展阶段
- **Analysis Logic**: TAM-SAM-SOM 框架量化市场空间，产品生命周期模型判断市场阶段
- **Core Hypothesis**: 中国护肤品市场处于成长期，年复合增长率超过 10%

### Chapter 2: 竞争格局分析
- **Analysis Objective**: 识别主要竞争者，评估竞争强度，分析竞争定位
- **Analysis Logic**: 波特五力模型评估竞争强度，竞争定位矩阵分析定位
- **Core Hypothesis**: 国际品牌主导高端市场，国货品牌在大众市场竞争激烈

### Chapter 3: 消费者需求洞察
- **Analysis Objective**: 理解目标用户需求，识别购买决策因素
- **Analysis Logic**: 消费者决策旅程模型分析购买路径，用户画像分析需求特征
- **Core Hypothesis**: Z 世代成为核心消费群体，功效性和成分透明度成为关键决策因素

### Chapter 4: 产品趋势分析
- **Analysis Objective**: 识别产品创新方向，分析品类发展趋势
- **Analysis Logic**: 产品创新矩阵 + 品类增长分析
- **Core Hypothesis**: 功效护肤和纯净美妆成为主要趋势

### Chapter 5: 市场机会与威胁
- **Analysis Objective**: 识别市场机会和潜在威胁
- **Analysis Logic**: SWOT 分析 + PESTEL 宏观分析
- **Core Hypothesis**: 国货品牌崛起带来机会，监管趋严构成挑战
```

**Step 1.4：定义数据查询需求**

```markdown
#### Chapter 1: 市场规模与增长趋势

| # | Data Metric | Data Type | Suggested Sources | Recommended Search Method | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|--------------------------|-----------------|----------|------------|
| 1 | 市场规模（亿元） | 定量 | 行业报告、政府统计 | multi-search-engine（百度、Bing） | "中国护肤市场规模 2024" | P0 | 2020-2025 |
| 2 | CAGR | 定量 | 行业报告 | multi-search-engine（Google） | "skincare CAGR growth" | P0 | 2020-2025 |
| 3 | 主要品类占比 | 定量 | 行业报告 | multi-search-engine（百度） | "护肤品品类占比 2024" | P1 | 2024 |
| 4 | 增长驱动力 | 定性 | 专家观点、行业分析 | multi-search-engine（百度、微信） | "护肤品市场增长驱动力" | P1 | 2024 |

#### Chapter 2: 竞争格局分析

| # | Data Metric | Data Type | Suggested Sources | Recommended Search Method | Search Keywords | Priority | Time Range |
|---|-------------|-----------|-------------------|--------------------------|-----------------|----------|------------|
| 5 | 主要品牌市场份额 | 定量 | 行业报告、市场调研 | multi-search-engine（百度、Google） | "护肤品品牌市场份额 2024" | P0 | 2024 |
| 6 | 头部企业营收数据 | 定量 | 财报、新闻报道 | multi-search-engine（百度） | "欧莱雅 资生堂 营收 2024" | P0 | 2024 |
| 7 | 竞争强度评估 | 定性 | 专家观点、行业分析 | multi-search-engine（微信） | "护肤品行业竞争分析" | P1 | 2024 |
```

**Step 1.5：定义可视化方案**

```markdown
#### Chapter 1: 市场规模与增长趋势

**Chart 1**: 柱状图 — 中国护肤品市场规模（2020-2025）
- X-axis: 年份, Y-axis: 市场规模（亿元）
- Data source: Data Requirement #1

**Chart 2**: 折线图 — 市场增长率趋势（2020-2025）
- X-axis: 年份, Y-axis: CAGR（%）
- Data source: Data Requirement #2

**Chart 3**: 饼图 — 主要品类市场份额
- Data source: Data Requirement #3

#### Chapter 2: 竞争格局分析

**Table 1**: 竞争定位矩阵
- Columns: 品牌、市场定位、价格区间、核心优势
- Data source: Data Requirement #5, #6

**Chart 4**: 柱状图 — 头部品牌市场份额对比
- Data source: Data Requirement #5
```

---

## 质量检查清单

完成阶段1后，确认以下事项：

- [ ] 框架覆盖了该领域自然应有的全部分析维度
- [ ] 每章均有明确的分析目标、分析逻辑与核心假设
- [ ] 数据需求具体、可衡量，并指定了推荐搜索方法
- [ ] 每章至少有一个可视化方案
- [ ] 分析框架已保存为 Markdown 文档
