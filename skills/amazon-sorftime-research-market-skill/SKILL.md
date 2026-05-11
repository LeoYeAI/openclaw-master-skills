---
name: product-research
description: 基于Sorftime MCP的深度选品调研。通过LLM Agent执行多维度分析：数据采集→属性标注→交叉分析→竞品VOC→壁垒评估→选品决策评估。交互式执行，输出Markdown报告和Dashboard看板。
argument-hint: "[产品/类目关键词] [站点]"
user-invocable: true
---

# 选品分析器 (Product Research - LLM Agent 驱动版)

## 定位

基于 **Sorftime MCP + LLM Agent** 的深度选品调研。LLM 直接执行分析逻辑，脚本仅负责数据采集和报告渲染。

**核心特点**：
- **LLM 驱动**：分析、洞察、决策全部由 LLM 完成
- **交互式执行**：逐步推进，用户可中途干预
- **轻量脚本**：仅用于 API 调用和 Dashboard 渲染

---

## Script Directory

| 脚本 | 用途 | 何时调用 |
|------|------|---------|
| `run_analysis.py` | **主入口脚本**：整合数据采集、分析、报告生成 | 推荐使用 |
| `collect_data.py` | Sorftime 数据采集（类目、Top100、关键词、趋势） | Step 1 |
| `get_reviews.py` | 竞品差评数据采集 | Step 4 |
| `api_client.py` | Sorftime API 调用 + SSE 解析 + 编码修复 | 每次 API 调用 |
| `render_dashboard.py` | 生成 Dashboard 可视化看板（v3.1 修复版） | 报告生成阶段 |
| `fix_data_json.py` | **数据验证和修复脚本**：校验并自动修复 data.json | Dashboard 生成前 |
| `validate_data.py` | **数据验证脚本**：校验 data.json 字段命名和数据一致性 | 报告生成前 |

**脚本职责**：
- **不做分析判断**：所有分析由 LLM 完成
- **不做复杂计算**：交叉分析让 LLM 从数据中发现
- **仅做数据搬运**：API → 结构化数据

**推荐使用方式**：

```bash
# 阶段1：数据采集（基础版 Dashboard）
python scripts/run_analysis.py "earbuds" US

# 阶段2：LLM 分析完成后，生成最终版报告
python scripts/run_analysis.py "earbuds" US --final

# 其他选项
python scripts/run_analysis.py "earbuds" US --collect-only  # 仅数据采集
python scripts/run_analysis.py "earbuds" US --no-reviews     # 跳过差评采集
```

---

## 执行流程（两阶段）

**重要**：选品分析分为两个阶段，数据采集由脚本自动完成，LLM 分析需要人工参与。

### 阶段1：数据采集（脚本自动）

```bash
python scripts/run_analysis.py "keyword" US
```

**输出**：
- `data.json` - 基础数据结构（不含分析结论）
- `dashboard.html` - 基础版看板（不含决策评分、VOC 等）
- `raw/` - 原始数据文件

**脚本自动完成**：
1. 类目搜索 → 获取 nodeId
2. Top100 产品数据采集
3. 关键词数据采集
4. 类目趋势数据采集
5. 竞品差评采集
6. 市场分析（价格区间、品牌分布）

### 阶段2：LLM 分析（交互式）

**必须完成的 LLM 分析任务**：

| 步骤 | 任务 | 输出到 data.json |
|------|------|------------------|
| 1 | 属性标注 | `product_types`、`dimensions_analysis` |
| 2 | 交叉分析 | `cross_analysis` |
| 3 | VOC 分析 | `voc_analysis.dimensions` |
| 4 | 壁垒评估 | `barriers` |
| 5 | 决策评估 | `decision` (overall_score, verdict) |

**完成后运行**：

```bash
python scripts/run_analysis.py "keyword" US --final
```

`--final` 参数会：
1. ✅ 验证分析数据完整性
2. ✅ 更新 data.json
3. ✅ 生成完整版 Dashboard（含决策评分、VOC 等）
4. ✅ 如果数据不完整，会提示缺失的字段

### 数据完整性检查

也可以单独检查数据完整性：

```bash
python scripts/render_dashboard.py data.json --check
```

输出示例：
```
✓ 数据完整，可以渲染完整版 Dashboard
  包含: decision.overall_score, voc_analysis.dimensions, barriers, cross_analysis
```

或

```
⚠️ 数据不完整，缺少以下字段:
  - decision.overall_score
  - voc_analysis.dimensions

ℹ️ 请先完成 LLM 分析，然后重新运行渲染
```

---

## 执行流程（交互式）

### Step 0: 信息收集

```
📋 选品分析 - 信息确认

1. 产品/类目关键词：[用户提供]
2. 目标站点：[US/GB/DE/FR/IT/ES/CA/JP，默认US]
3. 选品场景：[新手入门/蓝海发现/季节性/品牌打造/定向品类]
4. 约束条件（可选）：
   - 价格区间：如 $10-40
   - 月销量：如 > 1000
   - 预算：如 10万人民币
```

### Step 1: 数据采集（增强版 v3.0）

**API 调用顺序**：

| 步骤 | API | 输出 | 说明 | 优先级 |
|------|-----|------|------|----------|
| 0.5 | `search_categories_broadly` | blue_ocean_categories.json | **【新增】蓝海市场发现** | 📋 按需 |
| 1.1 | `category_name_search` | category_info.json | 按产品名搜索类目（使用 searchName 参数） | ⛔ 必调 |
| 1.2 | `category_report` | top100.json | Top100 产品数据 | ⛔ 必调 |
| 1.3 | `keyword_detail` × 3+ | keywords.json | 多维度关键词对比 | ⛔ 必调 |
| 1.4 | `category_trend` | trend.json | 新品占比趋势 | ⛔ 必调 |
| 1.5 | `keyword_extends` | keyword_extends.json | **【新增】关键词延伸词（维度发现）** | 📋 推荐 |
| 1.6 | `potential_product` | potential_products.json | **【新增】潜力产品发现** | 📋 推荐 |
| 1.7 | `product_detail` × 6-10 | products.json | 竞品详情（按需） | 📋 按需 |
| 1.8 | `product_reviews` × 6-10 | reviews.json | 竞品差评（按需） | 📋 按需 |

**⚠️ 重要：API 参数说明（v3.0）**

- `category_name_search` 参数：`{"amzSite": "US", "searchName": "bluetooth speaker"}`
  - **正确的类目搜索 API，参数名是 searchName**
- `search_categories_broadly` 参数（蓝海发现）：`{"amzSite": "US", "top3Product_sales_share": 0.4}`
- `potential_product` 参数（潜力产品）：`{"amzSite": "US", "monthlySales_min": 500}`
- `keyword_extends` 参数（延伸词）：`{"amzSite": "US", "keyword": "bluetooth speaker"}`
- `category_report` 参数：`{"amzSite": "US", "nodeId": "7073956011"}`
  - **nodeId 是字符串类型**

**脚本调用方式**：

```python
# 方法1: 使用 collect_data.py (推荐)
from scripts.collect_data import collect_data
result = collect_data("bluetooth speaker", "US")

# 方法2: 使用 api_client.py
from scripts.api_client import SorftimeClient

client = SorftimeClient()

# 获取类目ID（正确的方式）
category = client.search_category_by_product_name("US", "bluetooth speaker")
node_id = category[0]['nodeId']

# 获取Top100
top100 = client.get_category_report("US", node_id)

# 获取关键词详情
keywords = client.get_keyword_detail("US", "bluetooth speaker")
```

### Step 2: 属性标注（LLM 驱动）

**LLM 任务**：从 Top100 标题中提取关键差异化维度

```markdown
## 属性标注任务

基于以下 Top100 产品标题，提取 3-6 个关键差异化维度：

### 标题样本
[提供 Top20-30 标题作为样本]

### 提取要求
1. 识别差异化维度（如：功率、防水、续航、形态等）
2. 为每个产品标注维度值
3. 标注置信度（高/中/低）

### 输出格式
| ASIN | 功率 | 防水 | 续航 | ... | 置信度 |
```

**对低置信度产品**：调用 `product_detail` 补充验证

### Step 3: 交叉分析（LLM 直接发现）

**LLM 任务**：从标注数据中发现供需缺口

```markdown
## 交叉分析任务

基于以下已标注的 Top100 产品数据，执行交叉分析：

### 数据
[提供标注后的产品数据]

### 分析要求
1. 选择 2-3 对有意义的维度组合（如：功率×价格、防水×场景）
2. 识别：空白点（0产品）、薄供给（≤2产品）、高需求低供给
3. 分析每个缺口的原因（技术限制？需求不存在？被忽视？）
4. 按机会价值排序

### 输出格式
| 维度组合 | 状态 | 产品数 | 月销量 | 原因分析 | 机会评级 |
```

**关键点**：让 LLM 直接从数据中发现规律，而不是用 Python 脚本计算

### Step 4: 竞品与 VOC 分析

**竞品选择逻辑表**（LLM 按细分段选择）：

| ASIN | 品牌 | 选择理由 | 类型 | 覆盖维度 |
|------|------|----------|------|----------|
| [LLM 选择 6-10 个代表性竞品] |

**⛔ 差评维度归类（关键步骤）**

**必须按维度归类，禁止按 ASIN 组织**

**LLM 任务**：将竞品差评按属性维度归类，并映射到品牌能力和产品方案

**输入**：`competitor_reviews.json`（按 ASIN 组织的原始差评）
**输出**：`data.json` 中的 `voc_analysis` 字段（按维度归类）

**归类要求**：
1. **识别主要维度**（3-6 个）- 基于差评内容提取痛点类别
2. **每个维度包含**：
   - `dimension`: 维度名称（如：音质/音量、舒适度、续航）
   - `pain_point`: 痛点描述
   - `frequency`: 提及频次
   - `percentage`: 占比（如 "32%"）
   - `affected_brands`: 涉及品牌列表
   - `brand_opportunity`: 品牌/供应链能力如何解决
   - `product_solution`: 具体产品改进方向

**输出格式示例**：

```json
{
  "voc_analysis": {
    "dimensions": [
      {
        "dimension": "音质/音量",
        "pain_point": "音量太小，户外听不清",
        "frequency": 45,
        "percentage": "32%",
        "affected_brands": ["SHOKZ", "JLab"],
        "brand_opportunity": "有14.2mm大动圈供应链",
        "product_solution": "14.2mm动圈+音量增强模式"
      }
    ],
    "summary": "主要痛点集中在音质(32%)、舒适度(28%)、续航(18%)"
  }
}
```

**禁止的输出方式**：
- ❌ 按 ASIN 组织：`{"B0XXX": {"reviews": [...]}}`
- ❌ 缺少频次/占比数据
- ❌ 缺少品牌机会和产品方案映射

### Step 5: 评估与决策

**进入壁垒评估**：

| 壁垒类型 | 等级 | 数据锚点 | 预估成本 | 缓解方案 |
|----------|------|----------|----------|----------|
| Review 壁垒 | 中/高 | Top10 均值 XXX 评论 | $XXX | Vine + PPC |
| 资金壁垒 | 中/高 | 首批备货 + 广告 | ¥XX | 控制首批 MOQ |
| ... | ... | ... | ... | ... |

**选品决策评估（五维评分）**：

| 维度 | 权重 | 评分(1-10) | 加权分 | 依据 |
|------|------|-----------|--------|------|
| 市场规模 | 20% | [LLM 评分] | X.X | [数据依据] |
| 竞争格局 | 25% | [LLM 评分] | X.X | [数据依据] |
| ... | ... | ... | ... | ... |
| **总分** | 100% | - | **X.XX** | **决策结论** |

**决策结论映射**：
- 7.5-10分 → **建议进入** (优先推进)
- 6.0-7.4分 → **谨慎进入** (需精准定位，明确准入条件)
- 4.0-5.9分 → **暂缓观望** (需更多数据验证)
- 0-3.9分 → **不建议进入** (风险大于机会)

**产品矩阵**（Tier 1 必填具体规格）：

```markdown
### Tier 1: [产品定位]

**目标市场**：[维度组合空白/机会]
**决策理由**：[数据依据]

| 维度 | 规格 | 决策依据 |
|------|------|----------|
| [维度1] | [具体值] | [为什么] |
| [维度2] | [具体值] | [为什么] |

**目标定价**：$XX.XX
**差异化主张**：[一句话]
**对标竞品**：[ASIN] — [我们的优势]
**预估月销潜力**：XX-XX 件
```

### Step 6: 报告输出

**输出文件**：

```
product-research-reports/
└── {category}_{site}_{YYYYMMDD}/
    ├── report.md              # Markdown 完整报告（LLM 直接输出）
    ├── data.json              # 结构化数据（供 Dashboard 使用）
    ├── dashboard.html         # 可视化看板（脚本渲染）
    └── raw/                   # 数据文件
        ├── category_info.json # 类目信息
        ├── top100.json        # Top100 产品数据
        ├── trend.json         # 趋势数据
        └── keywords.json      # 关键词数据
```

**data.json 结构**（简化版）：

```json
{
  "metadata": {
    "category": "bluetooth speaker",
    "site": "US",
    "date": "20260319"
  },
  "market_overview": {
    "top100_monthly_sales": 55000,
    "top100_monthly_revenue": 5200000,
    "avg_price": 95,
    "top3_product_concentration": 0.2578,
    "top3_brand_concentration": 0.5058,
    "top10_brand_concentration": 0.8234
  },
  "dimensions": [...],
  "cross_analysis": [...],
  "competitors": [...],
  "voc_analysis": {
    "dimensions": [
      {
        "dimension": "音质/音量",
        "pain_point": "音量太小，户外听不清",
        "frequency": 45,
        "percentage": "32%",
        "affected_brands": ["SHOKZ", "JLab"],
        "brand_opportunity": "采用更大驱动单元",
        "product_solution": "14.2mm动圈+音量增强模式"
      }
    ],
    "summary": "主要痛点集中在音质(32%)、舒适度(28%)、续航(18%)"
  },
  "barriers": [...],
  "go_nogo": {...}
}
```

**⛔ 重要：数据字段命名规范**

| 字段名 | 说明 | 示例 |
|--------|------|------|
| `top3_product_concentration` | Top3 **产品**销量占 Top100 总销量的比例 | 0.2578 = 25.78% |
| `top3_brand_concentration` | Top3 **品牌**销量占 Top100 总销量的比例 | 0.5058 = 50.58% |
| `top10_brand_concentration` | Top10 **品牌**销量占 Top100 总销量的比例 | 0.8234 = 82.34% |
| `new_product_share` | 新品（上架<6个月）销量占比 | 0.26 = 26% |

**禁止模糊命名**：
- ❌ `top3_concentration`（不明确是产品还是品牌）
- ✅ `top3_product_concentration` 或 `top3_brand_concentration`

**⛔ 重要：VOC 分析数据结构**

`voc_analysis` 字段必须包含按**维度归类**的差评分析，而非按 ASIN 组织：

| 字段 | 类型 | 说明 |
|------|------|------|
| `dimension` | string | 痛点维度（如：音质/音量、舒适度、续航等） |
| `pain_point` | string | 痛点描述 |
| `frequency` | number | 提及频次 |
| `percentage` | string | 占比（如 "32%"）|
| `affected_brands` | array | 涉及的品牌列表 |
| `brand_opportunity` | string | 品牌/供应链能力如何解决 |
| `product_solution` | string | 具体产品改进方案 |

---

## Dashboard 渲染规范

`render_dashboard.py` 负责将 `data.json` 渲染为可视化看板。关键渲染规则：

### 产品维度分布
- **必须使用表格形式**，禁止使用柱状图
- 双栏布局：左侧价格区间分布，右侧产品形态分布
- 每行显示：维度值、产品数、占比（带颜色标签）
- 占比标签颜色规则：≥30%蓝色、≥20%绿色、≥10%黄色、<10%灰色

### 交叉分析（价格区间 × 产品形态）
- **必须使用矩阵表格形式**，禁止使用图表
- 行：价格区间（$0-30 到 $200+）
- 列：产品形态（骨传导、夹耳式、开放式挂耳、入耳式）
- 单元格：产品数量
- 特殊标记：
  - 竞争激烈（≥15款）：红色"红海"标签
  - 市场空白（0款）且为机会点：绿色"机会"标签
- 底部必须有洞察提示框，说明红海和机会区域

### 示例输出
```html
<!-- 维度分布：双表格布局 -->
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
  <!-- 价格区间表格 -->
  <!-- 产品形态表格 -->
</div>

<!-- 交叉分析：矩阵表格 -->
<table>
  <thead><!-- 表头：产品形态 --></thead>
  <tbody><!-- 行：价格区间，列：产品数 --></tbody>
</table>
<div class="insight-box">洞察：...</div>
```

---

## LLM Prompt 模板库

详细 Prompt 模板请参考：`references/prompt_templates.md`

包含 6 个模板：
1. 属性标注 - 从产品标题提取差异化维度
2. 交叉分析 - 发现供需缺口
3. 竞品选择 - 选择代表性竞品
4. 差评归类 - 按属性维度归类痛点
5. 选品决策评估 - 五维加权决策
6. 产品矩阵规划 - Tier 1/2/3 具体规格

---

## 硬性规则（⛔ 不可省略）

1. ⛔ Top100 必须完整 100 条
2. ⛔ 关键词至少 3 个维度对比
3. ⛔ 竞品选择 6-10 个，覆盖量级标杆/功能差异/价格带/痛点
4. ⛔ **差评必须按维度归类**（非按 ASIN 归类），输出到 `data.json` 的 `voc_analysis` 字段
5. ⛔ VOC 分析必须包含：频次、占比、涉及品牌、品牌机会、产品方案
6. ⛔ 选品决策评估必须量化评分
7. ⛔ Tier 1 产品必须具体到规格（禁止"待确认"占位）
8. ⛔ 每个数据表后有"关键洞察"段落
9. ⛔ 空白/薄供给必须附带原因分析
10. ⛔ **数据字段命名必须清晰**：使用 `top3_product_concentration` / `top3_brand_concentration`，禁止模糊的 `top3_concentration`
11. ⛔ **数据一致性校验**：报告生成前必须校验 `data.json` 中的数值与报告文本一致

---

## 常见场景策略

### 场景1：新手入门（预算<15万）
- 价格 $10-20
- 轻小件
- 无售后风险
- 中国卖家占比 > 70%

### 场景2：蓝海发现
- Top3 集中度 < 30%
- 新品占比 > 15%
- 关键词首页评论 < 500

### 场景3：定向品类分析（用户已指定）
- 跳过类目扫描，直接进入数据采集
- ⛔ 必须执行属性标注
- ⛔ 必须执行交叉分析
- ⛔ 必须执行选品决策评估（五维评分）

---

## 与其他 Skills 的关系

```
category-selection (品类筛选五维评分)
        ↓
product-research (深度选品调研) ← 本 Skill
        ↓
amazon-analyse (竞品 Listing 深挖)
        ↓
review-analysis (评论深度分析)
```

**区别**：
- `category-selection`：品类级别的快速筛选，五维评分
- `product-research`：指定品类的深度调研，多维度分析 + 选品决策评估
- `amazon-analyse`：单个竞品 Listing 的详细分析
- `review-analysis`：评论的深度痛点分析

---

## 支持的站点

US, GB, DE, FR, IT, ES, CA, JP, MX, AE, AU, BR, SA

---

## 注意事项

1. **API Key**：自动从 `.mcp.json` 读取
2. **数据时效**：Sorftime 数据可能有 1-7 天延迟
3. **API 限流**：每批最多 8 个并发请求
4. **编码问题**：脚本自动处理 Unicode-escape 和 Mojibake
5. **原始数据**：所有 API 响应保存在 `raw/` 目录供验证

---

## 故障排查

### 常见错误及解决方案

| 错误信息 | 原因 | 解决方案 |
|----------|------|----------|
| `HTTP Error 406: Not Acceptable` | API参数错误 | 检查参数名是否为 `searchName` 而非 `productName` |
| `An error occurred invoking 'xxx'` | API工具不存在 | 检查 TOOLS 映射表中的工具名称 |
| `未查询到对应产品` | ASIN无效或站点错误 | 验证ASIN格式, 确认产品在该站点销售 |
| `Authentication required` | API Key错误 | 检查 `.mcp.json` 中的 key 参数 |
| 中文乱码 | Mojibake编码 | 脚本自动修复, 或运行 `fix_encoding.py` |
| `IndentationError: unexpected indent` | Windows 命令行问题 | 使用脚本文件而非 `python -c` |
| `输出目录路径错误` | 相对路径问题 | 使用 `run_analysis.py`，自动处理路径 |
| `NameError: name 'xxx' is not defined` | 缺少 datetime 导入 | 检查脚本 import 语句 |
| **Dashboard 渲染问题** | | |
| Dashboard 显示空白 | data.json 结构不匹配 | **v3.5 已修复**：`run_analysis.py` 自动渲染 Dashboard |
| Dashboard 未自动生成 | 旧版本未集成渲染 | **v3.5 已修复**：数据采集完成后自动渲染 |
| `PermissionError: [Errno 13]` | 传递目录路径而非文件路径 | 使用绝对路径调用：`python render_dashboard.py -o output.html data.json` |
| `unrecognized arguments` | 参数顺序错误 | 正确格式：`python render_dashboard.py -o dashboard.html data.json` |
| Dashboard 缺少 VOC 数据 | LLM 未生成完整 voc_analysis | 确保 LLM 生成包含 voc_analysis.dimensions 的完整 data.json |
| Dashboard 交叉分析为空 | price_type_matrix 数据缺失 | 确保数据采集包含价格区间分析 |
| `KeyError: 'xxx'` | 字段名不一致 | **v3.4 已修复**：支持新旧字段名兼容 |
| `AttributeError: 'str' object has no attribute 'get'` | data.json 格式问题 | **v3.4 已修复**：自动转换为列表格式 |

### Dashboard 手动渲染方法

如果自动渲染失败，可以手动调用：

```bash
# 从输出目录调用
python .claude/skills/product-research/scripts/render_dashboard.py \
    -o product-research-reports/{keyword}_{site}_{date}/dashboard.html \
    product-research-reports/{keyword}_{site}_{date}/data.json

# 或者使用绝对路径
python "D:\amazon-mcp\.claude\skills\product-research\scripts\render_dashboard.py" \
    -o "D:\amazon-mcp\product-research-reports\{keyword}_{site}_{date}\dashboard.html" \
    "D:\amazon-mcp\product-research-reports\{keyword}_{site}_{date}\data.json"
```

### API 工具名称对照表

| 功能 | 工具名称 | 参数 |
|------|----------|------|
| 类目搜索 | `category_name_search` | `amzSite`, `searchName` |
| 类目报告 | `category_report` | `amzSite`, `nodeId` |
| 类目趋势 | `category_trend` | `amzSite`, `nodeId`, `trendIndex` |
| 关键词详情 | `keyword_detail` | `amzSite`, `keyword` |
| 产品详情 | `product_detail` | `amzSite`, `asin` |
| 产品评论 | `product_reviews` | `amzSite`, `asin`, `reviewType` |

### 调试技巧

1. **启用详细输出**: 在脚本中添加 `print()` 调试信息
2. **检查原始响应**: 查看 SSE 响应的实际内容
3. **分步执行**: 使用 Python 交互式环境逐行调试
4. **验证API Key**: `curl "https://mcp.sorftime.com?key=YOUR_KEY" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'`

---

*版本: v3.6 (两阶段工作流 + 数据验证) | 最后更新: 2026-03-19*
