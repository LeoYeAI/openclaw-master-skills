---
name: "category-selection"
description: "亚马逊品类自动化选品分析技能。通过五维评分模型对亚马逊品类进行深度市场调研，生成Markdown分析报告。当用户使用 /category-selection 命令或提出'分析XX品类'、'XX品类市场调研'、'XX品类选品'等需求时触发此技能。支持配置分析数量，默认Top20。"
---

## 快速参考

### 一键执行工作流 (推荐)

```bash
# 使用品类名称
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 直接使用 NodeID (推荐，避免类目搜索问题)
python .claude/skills/category-selection/scripts/workflow.py 679394011 US 20

# 指定分析数量
python .claude/skills/category-selection/scripts/workflow.py "Kitchen" US 50
```

**重要更新 (v4.0)**:
- ✅ **自动读取 API Key**: 无需设置环境变量，自动从 `.mcp.json` 读取
- ✅ **修复控制字符**: 自动处理 JSON 字符串值中的未转义换行符、制表符
- ✅ **改进类目搜索**: 支持模糊匹配和关键词变体
- ✅ **详细日志**: 执行日志保存到 `execution.log`

### 核心 API 工具

| 步骤 | 工具/操作 | 用途 | 返回数据大小 |
|------|----------|------|-------------|
| 1. 搜索类目 | `category_name_search` | 获取类目 nodeId | 小 |
| 2. 类目报告 | `category_report` | 获取 Top 产品列表和统计数据 | **大 (>25KB)** |
| 3. 产品详情 | `product_detail` | 获取单个产品详情 | 小 |
| 4. 类目关键词 | `category_keywords` | 获取类目核心关键词 | **大 (>25KB)** |
| 5. 类目趋势 | `category_trend` | 获取25个月历史趋势 | 中 |
| 6. 1688采购 | `products_1688` | 获取采购成本数据 | 小 |

### 调用格式
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

---

## 触发条件

当用户使用以下方式请求时，启动此分析流程：
- **命令**: `/category-selection {品类名称} {站点} [--limit N]`
- **示例**: `/category-selection "Sofas" US --limit 20`
- **自然语言**: "分析Amazon美国站的Sofas品类"、"Sofas品类市场调研"、"Sofas品类选品"

---

## 角色设定

你是一位拥有10年经验的"亚马逊选品专家"和"市场分析师"。你精通品类分析方法论，能够通过数据洞察市场机会、竞争格局和进入壁垒，为用户提供可执行的选品建议。

---

## 五维评分模型 (标准版)

**评分标准详解**:

| 维度 | 分值 | 评分标准 | 数据来源 |
|------|------|----------|----------|
| **市场规模** | 20 分 | >$10M=20分, >$5M=17分, >$1M=14分, 其他=10分 | 类目月销额 (top100产品月销额) |
| **增长潜力** | 25 分 | 低评论产品占比>40%=22分, >20%=18分, 其他=14分 | 评论数<100的产品占比 |
| **竞争烈度** | 20 分 | Top3品牌占比<30%=18分, <50%=14分, 其他=8分 | CR3 品牌集中度 |
| **进入壁垒** | 20 分 | Amazon占比<20%且新品>40%=20分, 其他组合6-18分 | Amazon自营占比 + 低评论占比 |
| **利润空间** | 15 分 | 均价>$300=12分, >$150=10分, >$50=7分, 其他=4分 | Top100产品平均价格 |

**评级标准**:

| 总分 | 评级 | 建议 |
|------|------|------|
| 80-100 | 优秀 | 强烈推荐进入 |
| 70-79 | 良好 | 可以考虑进入 |
| 50-69 | 一般 | 谨慎进入 |
| 0-49 | 较差 | 不建议进入 |

**完整标准请参考**: [scoring-standard.md](references/scoring-standard.md)

---

## 完整分析流程

### 阶段一: 数据收集

#### 步骤 1: 搜索类目获取 nodeId

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"品类关键词"}}}'
```

**处理多个类目结果时**：
- 大类目（如 "Clothing, Shoes & Jewelry"）通常只返回子类目列表
- 展示给用户让其选择最匹配的类目
- 或使用具体的子类目 NodeID 直接查询

**常见类目 NodeID 参考**:
```
Traditional Laptop Computers: 13896615011
2 in 1 Laptop Computers: 13896609011
Women's Fashion Sneakers: 679394011
Women's Road Running Shoes: 14210388011
Men's Fashion Sneakers: 679312011
Kitchen Storage Accessories: 3744031
```

#### 步骤 2: 获取类目报告 (Top100 + 统计)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

**关键**: `category_report` 返回数据通常>25KB，会保存到临时文件

**响应处理**:
```bash
# 使用 workflow.py 自动处理 (推荐)
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 或手动解码 SSE 响应
python .claude/skills/category-selection/scripts/sse_decoder.py {temp_file} {output_dir} 20
```

#### 步骤 3: 获取 Top N 产品详情 (并发)

```bash
# 并发获取 Top3 产品详情
curl ... '{"id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN1"}}}' &
curl ... '{"id":4,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN2"}}}' &
curl ... '{"id":5,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"ASIN3"}}}' &
wait
```

#### 步骤 4: 获取类目关键词 (可选)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"NODE_ID","page":1}}}'
```

**处理关键词数据**:
```bash
python .claude/skills/category-selection/scripts/keywords_parser.py \
  {temp_file} \
  {output_dir} \
  20
```

#### 步骤 5: 获取历史趋势数据 (可选)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"category_trend","arguments":{"amzSite":"US","nodeId":"NODE_ID"}}}'
```

**趋势数据类型**:
- 类目月销量趋势 (25个月)
- 平均售价趋势
- 平均星级趋势
- 品牌数量趋势

### 阶段二: 数据分析

#### 核心分析指标

**1. 市场集中度分析**
```python
# HHI 指数 (赫芬达尔-赫希曼指数)
# 计算: 各品牌市场份额平方和 × 10000
# 解读: <1500=低集中度, 1500-2500=中等, >2500=高集中度

# CR3/CR5 (前N品牌集中度)
# 计算: 前N大品牌销量占比
# 解读: <30%=分散, 30-50%=中等, >50%=集中
```

**2. 品牌分析**
```python
# 品牌分布: 按销量/销额排序
# 品牌数量: 统计独立品牌数
# 品牌多样性: HHI 指数评估
```

**3. 卖家来源分析**
```python
# Amazon 自营占比
# 中国卖家占比
# 美国本土卖家占比
# 其他国际卖家占比
```

**4. 价格分析**
```python
# 价格区间分布
# 平均价格
# 价格中位数
# 价格标准差
```

**5. 新品分析**
```python
# 新产品定义: 上架时间 < 90天
# 新品占比: 新品数量 / 总数量
# 新品表现: 新品平均销量、评论数
```

### 阶段三: 报告生成

#### 生成完整报告

```bash
# 一键生成所有报告格式
python .claude/skills/category-selection/scripts/workflow.py "Sofas" US 20

# 或分步骤生成
python .claude/skills/category-selection/scripts/generate_reports.py {data_json}
```

**输出文件结构**:
```
category-reports/
└── {Category}_{Site}_{YYYYMMDD}/
    ├── report.md                      # Markdown 分析报告
    ├── data.json                      # 完整解码数据 (中文键)
    ├── top_products.json              # Top N 产品列表
    ├── scores.json                    # 五维评分结果
    ├── execution.log                  # 执行日志 (v4.0 新增)
    ├── keywords.json                  # 类目关键词
    ├── trend_data.json                # 25个月趋势数据
    ├── adapted_data.json              # Excel 适配数据 (英文键)
    ├── category_analysis_report.xlsx  # Excel 报告
    ├── dashboard.html                 # HTML 可视化仪表板
    ├── data/                          # 原始数据目录
    │   ├── statistics.csv             # 统计数据
    │   ├── products.csv               # 产品列表
    │   └── scores.csv                 # 评分详情
    └── *_raw.txt                      # 原始 SSE 响应
```

---

## 数据处理工具

### 核心工具脚本

| 脚本 | 用途 | 版本 |
|------|------|------|
| `workflow.py` | 一键执行完整分析流程 | **v4.0** |
| `sse_decoder.py` | 解码 category_report SSE 响应 | v6.0 |
| `keywords_parser.py` | 解码 category_keywords 响应 | v3.0 |
| `trend_parser.py` | 解析趋势数据 | v1.0 |
| `data_adapter.py` | 数据格式转换 (中文→英文键) | v1.0 |
| `data_utils.py` | 数据处理工具类 | v2.0 |
| `generate_reports.py` | 统一报告生成器 | v3.0 |
| `generate_excel_report.py` | Excel 报告生成 | v2.0 |
| `generate_markdown_report.py` | Markdown 报告生成 | v2.0 |
| `fix_encoding.py` | 编码修复工具 | v1.0 |

### 数据字段映射

**API 响应字段 → 标准化字段**:

| API 字段 | 标准化字段 | 说明 |
|----------|-----------|------|
| ASIN | asin | 产品唯一标识 |
| 标题/title | title | 产品标题 |
| 价格/price | price | 当前售价 |
| 月销量/monthlySales | monthly_sales | 月销量 |
| 月销额/monthlyRevenue | monthly_revenue | 月销售额 |
| 评论数/reviews | review_count | 评论数量 |
| 星级/rating | rating | 平均评分 |
| 品牌/brand | brand | 品牌名称 |
| 卖家/seller | seller | 卖家名称 |
| 上架时间/daysOnline | days_online | 上架天数 |

---

## HTML 可视化仪表板

### 特性
- 基于 ECharts 的交互式图表
- 五维评分可视化进度条
- KPI 指标卡片展示
- 7 个动态图表：销量趋势、价格趋势、价格分布、评分分布、品牌份额、卖家来源、品牌评分趋势
- Top50 产品详细表格
- 关键发现智能分析

### 模板变量支持

| 变量类型 | 示例变量 | 说明 |
|---------|---------|------|
| 基础信息 | `{{CATEGORY_NAME}}`, `{{SITE}}`, `{{DATA_DATE}}` | 报告基本信息 |
| 五维评分 | `{{MARKET_SIZE_SCORE}}`, `{{MARKET_SIZE_PERCENT}}` | 各维度得分和进度条百分比 |
| KPI指标 | `{{TOTAL_PRODUCTS}}`, `{{AVG_PRICE}}`, `{{CR3}}` | 关键指标数据 |
| 图表数据 | `{{SALES_TREND_DATA}}`, `{{BRAND_SHARE_DATA}}` | JavaScript JSON 数据 |
| 分析结论 | `{{CONCENTRATION_LEVEL}}`, `{{RECOMMENDATION}}` | 智能分析文本 |

---

## 故障排查

### 常见问题与解决方案 (v4.0 更新)

#### 1. API Key 未设置
**问题**: `❌ API Key 未设置` 或 `Authentication required`

**原因**:
1. 环境变量 `SORFTIME_API_KEY` 未设置
2. `.mcp.json` 文件不存在或格式错误

**解决方案** (v4.0 已修复):
- workflow.py v4.0 会自动从 `.mcp.json` 读取 API Key
- 确保项目根目录存在 `.mcp.json` 文件，格式如下：
```json
{
  "mcpServers": {
    "sorftime": {
      "url": "https://mcp.sorftime.com?key=YOUR_API_KEY"
    }
  }
}
```

**手动设置环境变量 (备用)**:
```bash
# Windows PowerShell
$env:SORFTIME_API_KEY="your_api_key"

# Linux/Mac
export SORFTIME_API_KEY="your_api_key"
```

#### 2. JSON 解析失败 - 未转义的控制字符
**问题**: `JSONDecodeError: Invalid control character at: line 1 column 3401`

**原因**: API 返回的 JSON 字符串值中包含原始的换行符（\n）、制表符（\t）等控制字符，这些控制字符没有被正确转义

**示例**:
```json
// 错误格式（API 返回的原始格式）
{"标题": "类目：Renewed Laptops，排名:2
类目：Traditional Laptops，排名:11"}

// 正确格式
{"标题": "类目：Renewed Laptops，排名:2\\n类目：Traditional Laptops，排名:11"}
```

**解决方案** (v4.0 已修复):
- `escape_control_chars_in_json_strings()` 函数自动转义字符串值内的控制字符
- 该函数只处理字符串值内部的控制字符，不影响 JSON 结构

#### 3. 类目未找到
**问题**: 搜索类目时返回"未查询到对应类目"

**原因**:
1. 大类目（如 "Computers & Accessories"）可能只返回子类目列表
2. 类目名称不准确

**解决方案** (v4.0 已改进):
1. workflow.py v4.0 会自动尝试多种搜索变体
2. 使用更具体的子类目名称
3. **推荐**: 直接使用类目 NodeID 查询

**获取 NodeID 的方法**:
```bash
# 先用大类目搜索，查看返回的子类目列表
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Laptop"}}}'
```

#### 4. 数据解析失败 (Mojibake 编码问题)
**问题**: data.json 中的中文显示为 "Top100äº§å" 等乱码

**原因**: API 返回 Unicode-escape 格式 (\u4ea7\u54c1)，解码后产生 Mojibake

**解决方案** (v4.0 已自动修复):
- `fix_mojibake()` 函数自动修复编码问题
- 在 Unicode-escape 解码后立即应用 `.encode('latin-1').decode('utf-8')`

#### 5. Python dict 格式问题
**问题**: "Expecting property name enclosed in double quotes"

**原因**: API 返回 Python dict 格式（单引号），不是标准 JSON

**解决方案** (v4.0 已修复):
- `python_dict_to_json()` 函数正确处理单引号转换
- 同时处理 True/False/None 字面量

#### 6. 大类目搜索失败
**问题**: "Computers & Accessories" 等大类目搜索无结果

**解决方案**:
1. 使用子类目名称（如 "Laptops", "Computer Accessories"）
2. 先搜索大类目获取子类目列表，让用户选择
3. 直接使用已知 NodeID

### 版本更新记录

| 脚本 | 版本 | 更新内容 |
|------|------|----------|
| `workflow.py` | **v4.0** | ✅ 从 .mcp.json 自动读取 API Key<br>✅ 修复 JSON 字符串中未转义的控制字符<br>✅ 改进类目搜索策略<br>✅ 新增执行日志<br>✅ 更详细的错误信息 |
| `sse_decoder.py` | v6.0 | Mojibake 自动修复、括号匹配、Python dict 转换 |
| `generate_reports.py` | v3.0 | 完整变量替换、分析文本生成 |

### 调试技巧

1. **查看执行日志**:
```bash
# workflow.py v4.0 会自动保存执行日志
cat category-reports/{Category}_{Site}_{YYYYMMDD}/execution.log
```

2. **查看原始响应**:
```bash
# workflow.py 会自动保存原始 SSE 响应
cat category-reports/{Category}_{Site}_{YYYYMMDD}/category_report_raw.txt
```

3. **检查编码问题**:
```python
# 检查文件字节
with open('data.json', 'rb') as f:
    print(f.read(100))
```

4. **验证 JSON 格式**:
```bash
# 使用 Python 验证 JSON
python -m json.tool data.json
```

5. **测试 API 连接**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key={YOUR_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Kitchen"}}}'
```

---

## 支持的站点

**Amazon**: US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA
**TikTok**: US, GB, MY, PH, VN, ID
**1688**: 中国批发平台

---

## 注意事项

1. **API Key 配置**:
   - 推荐在 `.mcp.json` 中配置（v4.0 自动读取）
   - 也可以使用环境变量 `SORFTIME_API_KEY`
2. **参数名称**: 使用 `amzSite` 而非 `site`
3. **id 递增**: 每个请求的 `id` 字段必须递增 (1, 2, 3...)
4. **并发限制**: 建议最多 3-5 个并发请求
5. **数据时效**: 数据可能有 1-7 天延迟
6. **报告命名**: 使用 `{Category}_{Site}_{YYYYMMDD}` 格式

---

## 参考文档

- [评分标准详解](references/scoring-standard.md)
- [API 快速参考](references/api-quick-reference.md)
- [Sorftime MCP API 文档](references/sorftime-mcp-api.md)
- [类目 API 参考](references/category-api-reference.md)

---

*本 Skill 由 Claude Code 维护 | 最后更新: 2026-03-05 (v4.0)*
