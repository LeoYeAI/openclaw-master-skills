---
name: bettafish-opinion-analysis
description: |
  BettaFish（微舆）多智能体舆情分析系统 - 基于 QueryAgent、MediaAgent、InsightAgent 三引擎并行架构，通过 ForumEngine 实现 Agent 间协作讨论，生成 Word/PDF + 高设计质量 HTML 双格式报告。

  当用户需要以下分析时触发此 skill：
  - 分析某品牌/企业/产品的社交媒体声誉和口碑
  - 追踪热点舆情事件（如某车企被抨击、某明星争议事件）
  - 挖掘特定社媒账号的内容和影响力数据
  - 监测竞品舆情动态，进行多品牌对比
  - 分析公众对某话题的情绪倾向和态度
  - 生成舆情监测报告或危机预警分析
  - 需要Word文档/PDF格式的正式报告
  - 需要高设计质量的交互式HTML可视化报告
  - 需要基于真实数据的深度舆情分析

  此 skill 采用 QueryAgent + MediaAgent + InsightAgent 并行架构，通过 ForumEngine 实现 Agent 间讨论协作，执行 3 轮反思循环优化分析结果，最终输出:
  1. **Word/PDF 文档** - 使用 docx/pdf subskill 生成，适合正式汇报、打印、存档
  2. **高设计质量 HTML 报告** - 使用 frontend-design subskill，独特的编辑杂志风格，交互式可视化

  **不使用任何数据库和模拟数据**，所有数据通过 WebSearch/WebFetch/Browser/Curl 实时获取。

  即使遇到复杂的多步骤分析需求、需要整合多个数据源、或生成专业格式的舆情报告，也请务必使用此 skill。
compatibility: |
  - 需要网络搜索能力（WebSearch/WebFetch/Browser/Curl）
  - 支持主流社交媒体平台：微博、小红书、抖音、B站、知乎等
  - 输出格式：Word文档(.docx) + PDF(.pdf) + HTML交互报告(.html)
  - 无数据库依赖，纯前端可视化（ECharts/D3.js）
  - 视频分析依赖 video-frames subskill
---

# BettaFish 舆情分析系统

BettaFish（微舆）是一个**无数据库依赖、无模拟数据**的多智能体舆情分析系统，采用 **QueryAgent + MediaAgent + InsightAgent 三引擎并行架构**，通过 **ForumEngine** 实现 Agent 间协作讨论，执行 **3 轮反思循环**优化分析，最终**同时生成 Word/PDF 文档和高质量 HTML 可视化报告**。

## 输出产物说明

本 Skill **同时生成三种格式的报告**，每种格式都必须包含**丰富的文本内容**，而不仅仅是视觉效果：

### 报告内容结构要求

所有报告必须包含以下**8个核心章节**，每个章节都需要**详细的文本分析和数据支撑**：

```
1. 执行摘要（核心发现 + 关键指标 + 主要结论）
2. 品牌声量与影响力分析（整体趋势 + 渠道分布 + 区域分析）
3. 关键事件深度回顾（时间线 + 多方观点 + 数据支撑）
4. 情感与认知分析（情感光谱 + 品牌联想 + 核心议题）
5. 用户画像分析（人群属性 + 触媒习惯）
6. 声誉风险与机遇洞察（负面议题 + 风险预警 + 正面机遇）
7. 结论与战略建议（SWOT分析 + 优化建议 + 监测重点）
8. 数据附录（指标汇总 + 来源清单）
```

### 内容丰富度标准

**每个章节必须包含**：
- **详细分析段落**：至少3-5段深入分析文字，解释数据背后的洞察
- **具体数据支撑**：KPI指标、百分比、对比数据等
- **多维度视角**：Query/Media/Insight 三引擎的交叉分析
- **案例说明**：具体事件、引用、用户评论示例
- **表格展示**：事件时间线、数据对比、来源清单等
- **引用块**：关键结论、分析师总结、用户原话

**禁止**：
- ❌ 只有图表没有文字解释
- ❌ 只有数据没有分析洞察
- ❌ 只有标题没有详细内容
- ❌ 使用占位符或模板文本

### 1. Word 文档 (.docx)
- **用途**: 正式汇报、打印存档、邮件附件、向上级提交
- **特点**:
  - 结构清晰、内容完整、格式规范
  - **图文并茂**：图表配合详细文字说明
  - 标准公文格式，适合正式场合
- **生成方式**: 使用 `docx` subskill 通过 docx-js 生成

### 2. PDF 文档 (.pdf)
- **用途**: 正式汇报、跨平台分享、不可编辑存档
- **特点**: 版式固定、兼容性强、专业外观
- **生成方式**: 使用 `pdf` subskill 通过 reportlab 生成

### 3. HTML 交互式报告 (.html)
- **用途**: 演示展示、在线分享、交互探索
- **特点**: 独特的编辑杂志风格设计、丰富的交互可视化
- **生成方式**: 使用 `frontend-design` subskill 生成

---

## 报告模板系统

本 Skill 内置 **6 种专业舆情分析报告模板**，根据用户需求自动匹配最合适的模板结构。

### 模板类型与适用场景

| 模板名称 | 适用场景 | 核心特点 |
|---------|---------|---------|
| **企业品牌声誉分析** | 品牌月度/季度声誉监测 | 品牌形象、用户认知、声誉风险 |
| **突发事件与危机公关** | 危机事件应急分析 | 事件溯源、传播分析、应对策略 |
| **社会公共热点事件** | 社会热点追踪 | 演变脉络、传播路径、多方观点 |
| **市场竞争格局分析** | 竞品对比、市场份额 | SOV对比、口碑对比、营销策略 |
| **特定政策/行业动态** | 政策解读、行业分析 | 政策影响、行业反应、机遇挑战 |
| **日常/定期舆情监测** | 周期性监测报告 | 数据看板、趋势追踪、风险预警 |

### 模板选择逻辑

**Step 1: 识别分析类型**

根据用户查询自动判断适用的模板：

```yaml
关键词匹配规则:
  企业品牌声誉分析:
    - "品牌声誉"
    - "品牌形象"
    - "品牌口碑"
    - "企业舆情"

  突发事件与危机公关:
    - "危机"
    - "突发事件"
    - "负面舆情"
    - "公关"
    - "回应"
    - "道歉"

  社会公共热点事件:
    - "热点事件"
    - "社会热议"
    - "舆论焦点"
    - "公众关注"

  市场竞争格局分析:
    - "竞品"
    - "对比"
    - "竞争"
    - "市场份额"
    - "vs"

  特定政策/行业动态:
    - "政策"
    - "行业"
    - "新规"
    - "监管"

  日常/定期舆情监测:
    - "定期"
    - "周报"
    - "月报"
    - "监测"
    - "追踪"
```

**Step 2: 加载对应模板结构**

根据识别结果，读取 `assets/templates/` 目录下对应模板文件，获取详细的章节结构。

### 模板使用说明

**默认行为**：
- 如果用户查询未明确匹配任何模板类型，使用**企业品牌声誉分析**模板作为默认结构
- 如果用户明确要求"竞品对比"、"危机分析"等，自动切换到对应模板

**模板内容填充要求**：
- 每个章节必须包含 **3-5 段详细分析文字**
- 时间线章节必须包含 **结构化表格**
- 对比分析必须包含 **数据对比表格**
- 每个二级章节下必须有 **具体案例和数据支撑**

---

## 核心架构

```
用户查询输入
    ↓
[并行启动三 Agent]
├─ QueryAgent ──┐
├─ MediaAgent ──┼──→ ForumEngine (Agent 讨论协作)
└─ InsightAgent ─┘         ↓
                    [3轮反思循环优化]
                            ↓
                    [ReportEngine 报告生成]
                            ↓
        ├─ docx subskill → Word 文档
        ├─ pdf subskill → PDF 文档
        └─ frontend-design subskill → HTML 报告
```

## Agent 职责分工

| Agent | 职责 | 数据获取方式 | LLM 推荐 |
|-------|------|-------------|----------|
| **QueryAgent** | 网页搜索、新闻资讯、论坛讨论 | WebSearch + WebFetch + Browser | DeepSeek |
| **MediaAgent** | 短视频/图文内容分析 | 下载视频 → video-frames 提取帧 → 分析 | Gemini-2.5-pro |
| **InsightAgent** | 情感分析、关键词提取、聚类分析 | WebSearch + Python 脚本分析 | Kimi-K2 |
| **ForumHost** | 主持 Agent 讨论、引导研究方向 | LLM 生成 | Qwen-Plus |

## 设计规范：编辑杂志风格

HTML 报告采用 **Editorial/Magazine（编辑杂志）风格**，遵循以下设计原则：

### 视觉风格

| 设计元素 | 规范 | 说明 |
|---------|------|------|
| **整体风格** | 编辑杂志风 | 高端出版物质感，如《Monocle》《Wallpaper》|
| **色彩方案** | 深海军蓝 + 暖金色 | 主色 `#0a192f`，强调色 `#ffd700`，营造专业权威感 |
| **字体搭配** | Playfair Display + Source Serif Pro | 衬线字体组合，传递优雅与可信度 |
| **布局特点** | 不对称网格 + 慷慨留白 | 打破常规对称，创造视觉张力 |
| **动效设计** | 电影级滚动触发 + 微交互 | 页面加载渐现、图表动画、悬停反馈 |

## 执行步骤

### Step 1: 需求解析与模板选择

#### 1.1 提取分析要素

```yaml
分析目标: "品牌声誉/热点追踪/账号挖掘/竞品对比/危机公关/政策分析"
目标主体: "品牌名/事件名/话题关键词"
时间范围: "近7天/近30天/自定义"
输出格式: "Word + PDF + HTML"
```

#### 1.2 智能模板选择

**根据用户查询内容，自动匹配最合适的报告模板：**

```python
def select_report_template(user_query):
    """
    根据用户查询选择报告模板
    返回: (template_name, template_path)
    """
    query = user_query.lower()

    # 模板匹配规则
    template_keywords = {
        "突发事件与危机公关": ["危机", "突发事件", "负面舆情", "公关", "回应", "道歉", "事故"],
        "社会公共热点事件": ["热点事件", "社会热议", "舆论焦点", "公众关注", "热议话题"],
        "市场竞争格局分析": ["竞品", "对比", "竞争", "市场份额", "vs", "比较"],
        "特定政策或行业动态": ["政策", "行业", "新规", "监管", "法规", "指导意见"],
        "日常或定期舆情监测": ["定期", "周报", "月报", "监测", "追踪", "日报"],
        "企业品牌声誉分析": ["品牌声誉", "品牌形象", "品牌口碑", "企业舆情", "声誉"]
    }

    # 匹配逻辑
    for template_name, keywords in template_keywords.items():
        if any(kw in query for kw in keywords):
            return template_name, f"assets/templates/{template_name}报告模板.md"

    # 默认使用品牌声誉模板
    return "企业品牌声誉分析", "assets/templates/企业品牌声誉分析报告模板.md"
```

**模板选择示例：**

| 用户查询 | 自动选择模板 |
|---------|-------------|
| "分析某咖啡连锁品牌社交媒体口碑" | 企业品牌声誉分析 |
| "某音乐节安全事故危机分析" | 突发事件与危机公关 |
| "对比可口可乐和百事可乐的舆情表现" | 市场竞争格局分析 |
| "追踪环保新规对饮料行业影响" | 特定政策或行业动态 |
| "本周我司品牌舆情监测" | 日常或定期舆情监测 |

#### 1.3 加载模板结构

**读取选定的模板文件，获取详细的章节结构：**

```python
# 读取模板文件
template_content = read_file(selected_template_path)

# 解析章节结构
report_structure = parse_template_structure(template_content)

# 输出示例:
# {
#   "模板名称": "企业品牌声誉分析",
#   "章节": [
#     {"1.0": "摘要与核心发现", "子章节": ["1.1", "1.2", "1.3"]},
#     {"2.0": "品牌声量与影响力分析", "子章节": ["2.1", "2.2", "2.3"]},
#     ...
#   ]
# }
```

#### 1.4 关键词优化

**基于选定的模板类型，生成针对性的搜索关键词：**

```yaml
模板类型: "企业品牌声誉分析"
基础关键词: "某咖啡连锁品牌"
优化后关键词:
  QueryAgent:
    - "某咖啡品牌 用户评价 口碑"
    - "某咖啡品牌 产品 质量"
    - "某咖啡品牌 体验 评测"
  MediaAgent:
    - "某咖啡品牌 抖音 视频"
    - "某咖啡品牌 小红书 种草"
  InsightAgent:
    - "某咖啡品牌 情感分析"
    - "某咖啡品牌 舆情"
```

---

### Step 2: 并行启动三 Agent（ForumEngine 协作）

**所有 Agent 同时启动，独立执行，通过 ForumEngine 共享发现：**

#### QueryAgent 执行流程：
1. 使用 WebSearch 搜索新闻/论坛/博客
2. 使用 Browser 访问关键页面获取详细内容
3. 使用 WebFetch 获取页面结构化数据
4. 提取关键信息，生成初步摘要
5. **发布发现到 ForumEngine**

#### MediaAgent 执行流程：
1. 使用 WebSearch 搜索短视频/图文内容链接
2. 下载相关视频文件到本地
3. 使用 **video-frames subskill** 提取关键帧
4. 分析视频帧内容（画面、文字、场景）
5. **发布发现到 ForumEngine**

#### InsightAgent 执行流程：
1. 使用 WebSearch 获取补充数据
2. 执行情感分析（基于规则引擎）
3. 提取关键词和热点话题
4. 使用 **search_clustering.py** 对搜索结果聚类采样
5. **发布发现到 ForumEngine**

### Step 3: ForumEngine Agent 讨论（3轮反思循环）

**ForumEngine 机制**：
- 每个 Agent 将发现以结构化格式提交到论坛
- ForumHost（主持人）每收集到 3 条 Agent 发言后生成引导
- 主持人提出新的研究问题和方向
- Agent 根据引导进行下一轮搜索和分析

**3轮反思循环**：
```
第1轮：初步搜索 → Agent 发言 → 主持人引导
第2轮：深度搜索 → Agent 补充 → 主持人总结
第3轮：验证搜索 → Agent 确认 → 最终结论
```

### Step 4: 数据整合与知识图谱构建

1. 收集三 Agent 和 ForumEngine 的所有发现
2. 使用 **graph_generator.py** 构建知识图谱
3. 生成 D3.js 力导向图数据

### Step 5: 双格式报告生成（基于选定模板）

**⚠️ 关键：严格按照 Step 1 选定的模板结构生成报告**

#### 5.1 读取模板结构

```python
# 获取 Step 1 选定的模板
template_structure = load_template(selected_template_path)

# 按模板章节结构遍历生成内容
for chapter in template_structure.chapters:
    for subsection in chapter.subsections:
        # 根据子章节类型生成对应内容
        content = generate_content_by_type(subsection.title, agent_findings)
```

#### 5.2 内容生成规范

**每个章节必须包含**：
- **详细分析段落**：3-5段深入分析文字
- **数据表格**：时间线、对比表等
- **高亮框**：重要发现
- **引用块**：分析师总结
- **三引擎交叉分析**：Query/Media/Insight视角

**内容类型判断**：
- 标题含"时间线" → 生成结构化时间线表格
- 标题含"对比" → 生成数据对比表格
- 其他 → 生成3-5段分析段落

#### 5.3 同时生成三种格式

**A. Word文档**（使用docx subskill）
- 结构：封面 + 目录 + 8章正文 + 附录
- 字体：正文宋体、标题黑体
- 格式：1.5倍行距、首行缩进2字符
- 使用`docx-js`通过JavaScript生成

**B. PDF文档**（使用pdf subskill）
- 版式固定、中文字体支持
- 使用`reportlab`通过Python生成
- 必须注册中文字体（SimSun/SimHei）

**C. HTML报告**（使用frontend-design subskill）
- 编辑杂志风格设计
- 深海军蓝(#0a192f)背景 + 金色(#ffd700)强调
- Playfair Display + Source Serif Pro字体
- 包含ECharts图表和D3.js知识图谱
- 分页导航 + 键盘操作支持

#### 5.4 报告质量检查

- [ ] 三Agent并行执行完成
- [ ] ForumEngine完成3轮讨论
- [ ] 所有数据来自真实WebSearch
- [ ] 同时生成Word、PDF、HTML三种格式
- [ ] 每个章节包含3-5段详细分析文字
- [ ] 包含数据表格和图表
- [ ] HTML报告有章节导航

## 数据采集规范

### QueryAgent 数据获取

**使用智能体自带工具，禁止模拟数据：**

```
1. WebSearch("某咖啡连锁品牌 口碑评价")
2. WebSearch("site:weibo.com 某咖啡品牌")
3. Browser 访问关键页面获取详细内容
4. WebFetch 获取页面结构化数据
5. Curl 命令行获取 API 数据或特殊页面
```

**Curl 使用示例：**
```bash
# API 数据获取
curl -s "https://api.social-media.com/posts?q=某咖啡品牌"

# 带 Headers 的页面请求
curl -s -H "User-Agent: Mozilla/5.0" \
  -H "Accept: application/json" \
  "https://www.example.com/api/data"

# 获取并重定向输出到 Python 处理
curl -s "https://api.example.com/data" | python -c "import sys,json; print(json.load(sys.stdin))"
```

### MediaAgent 视频分析

**真实视频分析流程：**

```
1. WebSearch 搜索视频链接（抖音、B站、小红书）
2. 下载视频到本地临时目录
3. 使用 video-frames subskill 提取关键帧：

   {baseDir}/scripts/frame.sh /tmp/video.mp4 --time 00:00:05 --out /tmp/frame_5s.jpg

4. 分析视频帧内容（画面元素、文字、场景）
5. 结合视频描述文字进行综合分析
```

### InsightAgent 数据分析

**使用 Python 脚本进行分析：**

```python
# 情感分析
from scripts.sentiment_analyzer import SentimentAnalyzer
analyzer = SentimentAnalyzer()
results = analyzer.analyze_batch(texts)

# 搜索结果聚类采样
from scripts.search_clustering import cluster_search_results
clusters = cluster_search_results(search_results, n_clusters=5)
```

## 内置工具使用

### 1. 搜索结果聚类采样（search_clustering.py）

```python
from scripts.search_clustering import cluster_search_results, sample_from_clusters

# 对搜索结果进行 KMeans 聚类
clusters = cluster_search_results(
    results=search_results,
    n_clusters=5,
    samples_per_cluster=3
)

# 返回每个聚类的代表性样本
representative_samples = sample_from_clusters(clusters)
```

### 2. 情感分析（sentiment_analyzer.py）

```python
from scripts.sentiment_analyzer import SentimentAnalyzer, analyze_sentiment_distribution

analyzer = SentimentAnalyzer()
result = analyzer.analyze("这个产品真的很棒！")
# 返回: label, confidence, positive_score, negative_score, fine_emotions, aspects
```

### 3. 知识图谱构建（graph_generator.py）

```python
from scripts.graph_generator import KnowledgeGraphBuilder

builder = KnowledgeGraphBuilder(topic="某咖啡连锁品牌")
builder.build_from_analysis_result(
    query_results=query_data,
    media_results=media_data,
    insight_results=insight_data
)
graph_data = builder.to_dict()
```

## ForumEngine 协作协议

### Agent 发言格式

```json
{
  "agent": "QueryAgent",
  "round": 1,
  "findings": {
    "key_points": ["发现1", "发现2"],
    "sources": [{"title": "...", "url": "..."}],
    "confidence": 0.85
  },
  "questions": ["需要进一步验证的问题"]
}
```

### 主持人引导格式

```json
{
  "host": "ForumHost",
  "round": 1,
  "summary": "本轮讨论总结",
  "directions": ["下一步研究方向1", "方向2"],
  "questions": ["需要回答的关键问题"]
}
```

## 质量检查清单

生成报告前检查：

- [ ] **三 Agent 并行执行完成**
- [ ] **ForumEngine 完成 3 轮讨论**
- [ ] **所有数据来自真实 WebSearch，无模拟数据**
- [ ] **视频分析使用 video-frames 提取帧**
- [ ] **搜索结果经过聚类采样处理**
- [ ] **同时生成 Word、PDF、HTML 三种格式**
- [ ] **Word 使用 docx subskill 生成，格式规范**
- [ ] **PDF 使用 pdf subskill 生成**
- [ ] **HTML 使用 frontend-design subskill，编辑杂志风格**
- [ ] **情感分布饼图使用艺术化设计**
- [ ] **趋势图有电影级动画效果**
- [ ] **知识图谱可交互（D3.js 力导向图）**
- [ ] **支持 PDF 导出功能**
- [ ] **不使用任何数据库和深度学习模型**

## Subskills 调用方式

### video-frames
```bash
# 提取视频帧
{baseDir}/subskills/video-frames/scripts/frame.sh /path/to/video.mp4 --time 00:00:10 --out /tmp/frame.jpg
```

### docx
```javascript
// 生成 Word 文档
const { Document, Packer } = require('docx');
// ... 详见 docx subskill 文档
```

### frontend-design
```
使用 frontend-design subskill 生成 HTML 报告
- 深海军蓝 (#0a192f) 背景
- 金色 (#ffd700) 强调
- Playfair Display 字体
- 电影级动画效果
```

### pdf
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate
# ... 详见 pdf subskill 文档
```

## 版本历史

- **v1.0.0** - 初始版本
  - 实现 QueryAgent + MediaAgent + InsightAgent 三引擎并行架构
  - 实现 ForumEngine Agent 间协作讨论
  - 实现 3 轮反思循环优化
  - 集成 video-frames、docx、frontend-design、pdf subskills
  - 同时输出 Word、PDF、HTML 三种格式
  - 无数据库依赖，无模拟数据
  - 搜索结果聚类采样
