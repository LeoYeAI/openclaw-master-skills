---
name: deepsearch-mpro
version: 1.0.0
description: 专业深度研究与报告生成技能。支持企业竞争分析、产品竞争分析、行业分析、市场规模/竞争格局、AI大模型厂商、AI工具学习指南等领域。整合17个搜索引擎，三阶段工作流（主题确认→框架生成→报告输出），运用PESTEL、SWOT、波特五力、商业模式画布等经典咨询研究模型，输出精美的深蓝色政务风格HTML与Markdown双格式咨询级报告。
---

# 专业研究报告技能

## 概述

该技能用于生成**专业、咨询级别的研究报告**，覆盖市场分析、AI 大模型厂商、SaaS 厂商、AI 工具学习指南、竞争情报、行业研究等领域。

### 核心能力

- ✅ **多源搜索引擎**：17个搜索引擎（8个国内 + 9个国际），无需 API 密钥
- ✅ **三阶段工作流**：主题理解与确认 + 分析框架生成 + 报告生成
- ✅ **交互式确认**：支持用户确认、修改、提问等交互式反馈
- ✅ **双格式输出**：Markdown + HTML，深蓝色政务风格

### 何时使用本技能

- 用户请求市场分析、消费者洞察报告、财务分析、行业研究
- 用户输入具体 AI 工具名称，需要生成学习指南（如"Cursor 学习指南"）
- 用户需要专业的咨询风格研究报告
- 用户提供研究主题，并在数据收集前需要结构化分析框架

### 整合的技能与能力

本技能整合了以下核心搜索能力，提供多源数据搜索与分析支持：

| 整合来源 | 路径 | 能力说明 | 版权归属 |
|---------|------|---------|---------|
| **ddg-web-search** | `ddg-web-search/` | DuckDuckGo 网络搜索能力，提供全球范围内的实时搜索支持 | 原作者所有 |
| **multi-search-engine** | `multi-search-engine/` | 多搜索引擎聚合能力，整合17个搜索引擎（8个国内 + 9个国际），无需 API 密钥 | 原作者所有 |

**能力集成说明**：

本技能已将上述搜索能力整合为核心功能

---

## 三阶段工作流

### 阶段 0：主题理解与确认

**目的**：确保正确理解用户的研究需求，避免方向偏差。

**工作流程**：

1. **解析用户输入**
   - 识别研究主题、分析领域、搜索范围、特定角度

2. **推断分析领域**

根据主题关键词推断分析领域，加载对应的领域文档：

| 主题类型 | 关键词示例 | 领域文档 |
|---------|-----------|---------|
| **行业分析** | "{行业名}行业分析"、"ERP行业趋势"、"AI Agent行业" | `references/domains/industry-analysis.md` |
| **企业竞争分析** | "{公司名}分析"、"{公司名}竞争分析"、"{公司名}研究"、金蝶、用友、SAP等 | `references/domains/company-analysis.md` |
| **产品竞争分析** | "{产品名}分析"、"{产品名}研究"、"{产品名}竞争力" | `references/domains/product-analysis.md` |
| **市场规模/竞争格局** | "市场规模分析"、"竞争格局研究"、"市场机会评估" | `references/domains/market-analysis.md` |
| **AI 大模型厂商** | OpenAI、Anthropic、DeepSeek、智谱AI等 | `references/domains/ai-vendor-analysis.md` |
| **AI 工具学习指南** | "AI工具使用指南"、"Gemini教程" | `references/domains/ai-tool-learning-guide-framework.md` |

**推断逻辑**：
1. **行业关键词**（行业分析、行业趋势、行业研究）→ 行业分析
2. **企业名称 + 分析/研究** → 企业竞争分析
3. **产品名称 + 分析/研究** → 产品竞争分析
4. **市场规模/竞争格局关键词**（市场规模、竞争格局、市场机会）→ 市场规模/竞争格局分析
5. **AI 厂商名**（OpenAI、DeepSeek等）→ AI 厂商分析

3. **生成确认提示**

向用户展示以下确认项，等待用户确认或修改：

| 确认项 | 说明 | 示例 |
|-------|------|------|
| **研究主题** | 解析后的核心研究对象 | "金蝶企业竞争分析" |
| **研究方向** | 分析领域及分析角度 | "企业竞争分析：商业模式 + 竞争格局 + 近期动态" |
| **时间范围** | 数据收集的时间窗口 | "近一周" / "近一月" / "自定义（如2024Q1）" |

**时间范围说明**：
- **近一周**：聚焦最新动态、热点事件、近期发布
- **近一月**：平衡时效性与深度，适合大多数分析
- **自定义**：特定时间段（如财报季、产品发布周期）

**时间参数传递**：
- 时间范围确认后，记录为全局参数 `search_time_range`
- 在阶段1数据收集时，自动转换为搜索时间过滤条件
- 示例：`search_time_range = "近一周"` → 搜索引擎添加 `&before=2026-03-18&after=2026-03-11`

4. **处理反馈**
   - 用户确认 → 记录时间参数，进入阶段 1
   - 用户修改 → 更新确认项后重新确认
   - 用户提问 → 解答后重新确认

**详细流程和示例**：见 `references/workflow/phase0-details.md`

---

### 阶段 1：分析框架生成

**目的**：生成完整的分析框架，作为后续数据收集与报告生成的蓝图。

**工作流程**：

1. **理解研究主题**
   - 识别核心对象和分析领域
   - 加载对应的领域文档（`references/domains/*.md`）

2. **选择分析模型**
   - 根据领域文档推荐，按需加载模型文件（`references/models/*.md`）
   - 每次研究只加载 2-4 个模型，避免堆砌
   - 模型索引：`references/models/README.md`

3. **设计章节骨架**
   - 每章包含：分析目标、分析逻辑、核心假设
   - 典型结构：3-5 个主要章节

4. **定义数据需求**
   - 每条需求包含：指标、类型、来源、搜索方法、优先级
   - P0 数据必须收集，P1 重要，P2 补充

5. **定义可视化方案**
   - 为每章定义图表类型和数据来源

**详细流程和示例**：见 `references/workflow/phase1-details.md`

---

### 阶段 2：报告生成

**目的**：将分析框架和数据整合为最终的咨询级报告。

**工作流程**：

1. **接收并校验输入**
   - 确认分析框架和数据包齐全
   - 检查 P0 数据完整性

2. **映射报告结构**
   - Abstract → Introduction → Body Chapters → Conclusion → References

3. **撰写报告**
   - 遵循"视觉锚点 → 数据对比 → 综合分析"流程
   - 每个小节以充分的分析段落结尾（≥200字）

4. **撰写摘要和结论**
   - 摘要：3-5 句话，200-300 字
   - 结论：纯客观综合判断，不使用 bullet points

5. **整理参考文献**
   - 按 GB/T 7714-2015 格式列出

6. **生成输出文件**
   - Markdown 文件：`assets/report-template.md`
   - HTML 文件：根据分析模型组合模块化模板

**HTML 模板系统**：

位于 `assets/templates/` 目录，提供 10 个模块化模板：

| 模板文件 | 分析模型 |
|---------|---------|
| `product-overview-template.html` | 产品概览 |
| `target-users-template.html` | 目标用户分析 |
| `core-features-template.html` | 核心功能 |
| `business-model-canvas-template.html` | 商业模式画布 |
| `porter-five-forces-template.html` | 波特五力分析 |
| `swot-analysis-template.html` | SWOT 分析 |
| `pestel-analysis-template.html` | PESTEL 分析 |
| `competitor-matrix-template.html` | 竞品对比矩阵 |
| `timeline-template.html` | 关键时间线 |
| `key-metrics-template.html` | 关键指标 |

**模板组合建议**：

| 研究类型 | 推荐模板组合 |
|---------|-------------|
| AI 厂商/产品 | 产品概览 → PESTEL → 目标用户 → 竞品矩阵 → 商业模式画布 → SWOT → 核心功能 |
| 市场竞争 | 产品概览 → PESTEL → 波特五力 → 竞品矩阵 → 关键指标 |
| 商业模式 | 产品概览 → PESTEL → 商业模式画布 → SWOT |
| 行业研究 | 产品概览 → PESTEL → 波特五力 → 关键指标 → 时间线 |

**详细流程和示例**：见 `references/workflow/phase2-details.md`

---

## 数据收集策略

### 多层搜索方案（优先级顺序）

**第一层：Agent 内置 web_search**（优先使用）

- 快速获取基础信息
- 参数：query、max_results（建议 3-10）
- 适用场景：初步数据获取、验证数据是否存在

**第二层：web_fetch 深度搜索**

- 直接访问搜索引擎获取详细结果
- 中文市场：百度、微信、头条
- 国际市场：Google、Bing
- 政府数据：site:gov.cn
- 行业报告：filetype:pdf
- 详细使用方法：见 `references/technical/search-engines.md`

**第三层：multi-search-engine 备用方案**（如前两层无法获取数据）

- 整合 17 个搜索引擎（8个国内 + 9个国际）
- 无需 API 密钥
- 支持高级搜索操作符和时间过滤
- 适用场景：当 web_search 和 web_fetch 都无法获取数据时

**第四层：ddg-web-search 最终备选**

- DuckDuckGo Lite 搜索
- 零依赖，仅需 web_fetch 工具
- 适用场景：当所有搜索引擎都无法访问时的最终备选

### 搜索策略执行逻辑

```markdown
对于每个数据需求（P0/P1/P2）：

1. 先使用 web_search 快速获取
   - 成功：进入数据提取
   - 失败：进入第2层

2. 使用 web_fetch 深度搜索
   - 成功：进入数据提取
   - 失败：进入第3层

3. 使用 multi-search-engine 备用方案
   - 根据数据类型选择合适引擎：
     * 中文市场 → 百度、微信、头条
     * 国际市场 → Google、Bing
     * 政府数据 → site:gov.cn
     * 行业报告 → filetype:pdf
   - 成功：进入数据提取
   - 失败：进入第4层

4. 使用 ddg-web-search 最终备选
   - 成功：进入数据提取
   - 失败：标注"数据暂不可得"

数据提取：
- 从搜索结果中提取关键数据
- 多源交叉验证（至少2个来源）
- 标注数据可信度（high/medium/low）
```

### 内置搜索能力说明

本技能已内置整合以下搜索能力，**用户无需额外安装任何子技能**：

| 搜索层 | 能力来源 | 说明 |
|--------|---------|------|
| 第1层 | Agent 内置 `web_search` | 默认优先使用 |
| 第2层 | Agent 内置 `web_fetch` | 深度搜索 |
| 第3层 | **已整合** `multi-search-engine` | 17个搜索引擎，无需安装 |
| 第4层 | **已整合** `ddg-web-search` | DuckDuckGo Lite，无需安装 |

**子技能已整合**：
- `./multi-search-engine/` 和 `./ddg-web-search/` 的能力已完全整合进本技能
- 所有搜索引擎的 URL 模板和使用方法见 `references/technical/search-engines.md`
- 四层搜索策略的详细流程见 `references/technical/multi-layer-search-strategy.md`

---

## 数据真实性协议

**严格遵循规则**：报告中呈现的所有数据，**必须**直接来源于提供的 Data Summary 或 External Search Findings。

- **禁止幻觉**：不得编造、估算或模拟数据
- **可追溯来源**：每个重要结论和图表都必须能够追溯到输入的数据包
- **数据缺失处理**：如数据缺失，明确写出"数据暂不可得"

---

## 输出格式

### Markdown 文件

- 文件名：`{主题关键词}-report-{日期}.md`
- 模板：`assets/report-template.md`

### HTML 文件

- 文件名：`{主题关键词}-report-{日期}.html`
- 模板：`assets/html-template.html`
- 风格：深蓝色政务/企业内报风格
- 布局：左侧树状导航（固定）+ 右侧内容展示

### 格式与语气标准

- **语气**：麦肯锡 / BCG 风格 —— 权威、客观、专业
- **数字格式**：千位分隔使用英文逗号（`1,000`）
- **数据强调**：重要观点和关键数字需加粗
- **标题编号**：使用标准编号（`1.`、`1.1`）
- **参考文献**：必须严格遵循 GB/T 7714-2015

---

## 参考文档体系

### 领域分析框架

| 文档 | 说明 |
|------|------|
| `references/domains/industry-analysis.md` | 行业分析框架（PESTEL + 波特五力 + 价值链） |
| `references/domains/company-analysis.md` | 企业竞争分析框架（含 SaaS 厂商分析，商业模式画布 + SWOT + 竞品矩阵） |
| `references/domains/product-analysis.md` | 产品竞争分析框架（目标用户 + 竞品矩阵 + 核心功能） |
| `references/domains/market-analysis.md` | 市场规模/竞争格局分析框架（TAM-SAM-SOM + 波特五力） |
| `references/domains/ai-vendor-analysis.md` | AI 大模型厂商分析框架 |
| `references/domains/ai-tool-learning-guide-framework.md` | AI 工具学习指南生成框架 |
| `references/domains/hotspot-analysis.md` | 热点分析公共模块（企业/产品/AI/SaaS/全球AI热点） |

### 工作流程详细文档

| 文档 | 说明 |
|------|------|
| `references/workflow/phase0-details.md` | 阶段0 详细流程和示例 |
| `references/workflow/phase1-details.md` | 阶段1 详细流程和示例 |
| `references/workflow/phase2-details.md` | 阶段2 详细流程和示例 |
| `references/workflow/examples-complete.md` | 完整示例集（5个场景） |

### 技术指南

| 文档 | 说明 |
|------|------|
| `references/technical/multi-layer-search-strategy.md` | 四层搜索策略详细指南 |
| `references/technical/search-engines.md` | 多源搜索引擎使用指南 |
| `references/technical/data-quality-guidelines.md` | 数据质量控制标准 |
| `references/technical/format-conversion.md` | 格式转换指南 |

### HTML 模板

| 文档 | 说明 |
|------|------|
| `assets/templates/README.md` | 模板使用说明 |
| `assets/templates/*.html` | 10 个模块化 HTML 模板 |

### 领域分析框架（重复）

| 文档 | 说明 |
|------|------|
| `references/domains/industry-analysis.md` | 行业分析框架（PESTEL + 波特五力 + 价值链） |
| `references/domains/company-analysis.md` | 企业竞争分析框架（商业模式画布 + SWOT + 竞品矩阵） |
| `references/domains/product-analysis.md` | 产品竞争分析框架（目标用户 + 竞品矩阵 + 核心功能） |
| `references/domains/ai-vendor-analysis.md` | AI 大模型厂商分析框架 |
| `references/domains/ai-tool-learning-guide-framework.md` | AI 工具学习指南框架 |
| `references/domains/saas-vendor-analysis.md` | SaaS 厂商分析框架 |
| `references/domains/market-analysis.md` | 市场与竞争分析框架 |

### 分析模型库

| 文档 | 说明 |
|------|------|
| `references/models/README.md` | 模型索引和使用说明 |
| `references/models/strategic/*.md` | 战略模型（SWOT、PESTEL、波特五力、VRIO） |
| `references/models/market/*.md` | 市场模型（STP、BCG、TAM-SAM-SOM） |
| `references/models/competitive/*.md` | 竞争模型（商业模式画布、竞品矩阵、价值链） |
| `references/models/consumer/*.md` | 消费者模型（决策旅程、AARRR、RFM） |
| `references/models/financial/*.md` | 财务模型（杜邦分析、DCF、可比公司） |

### 方法论

| 文档 | 说明 |
|------|------|
| `references/methodology/deep-research-methodology.md` | 深度研究方法论 |
| `references/methodology/report-writing-guide.md` | 报告撰写指南 |

---

## 质量检查清单

### 阶段 0（主题理解与确认）

- [ ] 研究主题已明确
- [ ] 分析领域已识别
- [ ] 搜索范围已确定
- [ ] 用户已确认

### 阶段 1（分析框架）

- [ ] 框架覆盖了该领域自然应有的全部分析维度
- [ ] 每章均有明确的分析目标、分析逻辑与核心假设
- [ ] 数据需求具体、可衡量，并指定了推荐搜索方法
- [ ] 每章至少有一个可视化方案

### 阶段 1→2（数据收集）

- [ ] 所有 P0 数据任务已完成
- [ ] 关键数据至少从 2 个来源验证
- [ ] 数据来源已记录
- [ ] 数据可信度已标注

### 阶段 2（报告生成）

- [ ] Markdown 报告零幻觉
- [ ] 每个小节均遵循"数据对比 → 综合分析"
- [ ] 参考文献格式正确（GB/T 7714-2015）

---

## 配置项

```text
output_locale = zh_CN  # zh/en
default_search_engines = ["baidu", "bing", "google"]
data_validation_required = true  # P0 数据必须验证
interactive_confirmation = true  # 交互式确认，支持用户修改研究参数
```

---

## 版本历史

- **v1.0.0**: 正式版
  - 三阶段工作流（主题确认→框架生成→报告输出）
  - 整合 17 个搜索引擎（8个国内 + 9个国际）
  - 支持市场分析、行业分析、AI/SaaS厂商分析、竞争情报、竞争分析等领域
  - 交互式主题确认，支持用户修改研究参数
  - 双格式输出（Markdown + HTML）
  - 四层搜索策略（web_search → web_fetch → multi-search-engine → ddg-web-search）
