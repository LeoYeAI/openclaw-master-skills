---
name: alphashop-sel-newproduct
category: official-1688
description: >-
  AlphaShop新品选品SKILL：基于关键词和商品筛选条件生成深度市场分析和新品推荐报告。
  支持Amazon和TikTok平台的跨境电商选品，提供市场评级、竞争分析、新品推荐、热销品对比等功能。
metadata:
  version: 1.0.1
  label: AI新品选品
  author: 1688官方技术团队
  openclaw:
    primaryEnv: none
    requires:
      env: []
---

## 配置

### 环境变量

需要配置 AlphaShop API 凭证。在 OpenClaw config 中设置：

```json5
{
  skills: {
    entries: {
      "alphashop-sel-newproduct": {
        env: {
          ALPHASHOP_ACCESS_KEY: "你的AccessKey",
          ALPHASHOP_SECRET_KEY: "你的SecretKey"
        }
      }
    }
  }
}
```

### 如何获取 API Key

#### 获取途径

本 skill 使用 AlphaShop/遨虾平台的 API 服务，需要申请以下凭证：
- `ALPHASHOP_ACCESS_KEY` - API 访问密钥
- `ALPHASHOP_SECRET_KEY` - API 密钥

#### 申请步骤

1. **联系平台方**
   - 如果您是 1688 或阿里内部用户，请联系 AlphaShop/遨虾 平台管理员
   - 平台可能需要您提供：
     - 公司信息
     - 使用场景说明
     - 预期调用量

2. **获取凭证**
   - 平台审核通过后会提供：
     - Access Key（访问密钥）
     - Secret Key（密钥）

3. **配置到环境**
   - 按照上面的配置方式设置环境变量

#### 缺少凭证时的提示

如果运行 skill 时未配置凭证，会看到详细的配置指南：

```
🔐 需要 AlphaShop API 凭证

本 skill 需要以下凭证才能使用：
  • ALPHASHOP_ACCESS_KEY  - API 访问密钥
  • ALPHASHOP_SECRET_KEY  - API 密钥

📋 如何获取凭证：
1. 联系 AlphaShop/遨虾 平台获取 API 凭证
2. 配置环境变量或 OpenClaw 配置
3. 重新运行命令
```

# AlphaShop新品选品SKILL

通过遨虾AI选品API进行跨境电商市场分析和新品推荐，一次调用即可获得完整的市场洞察和选品建议。

## 快速开始

⚠️ **使用前必读**：本 skill 包含两个 API，且有先后依赖关系！

### 正确的使用顺序

```
第一步：关键词搜索 (search)
   ↓ 返回合法的关键词列表（带 keyword 字段）
   ↓
第二步：从返回结果中选择一个 keyword 字段的值
   ↓
第三步：新品报告 (report) - 使用第一步返回的 keyword
```

**示例：**

```bash
# 1️⃣ 先搜索关键词
python3 scripts/selection.py search --keyword "phone" --platform "amazon" --region "US"

# 输出：返回关键词列表，例如：
#   1. phone (手机) - keyword: "phone"
#   2. phone case (手机壳) - keyword: "phone case"

# 2️⃣ 使用返回的 keyword 生成报告
python3 scripts/selection.py report --keyword "phone case" --platform "amazon" --country "US"
```

❌ **错误示例**：直接使用随意关键词会报错
```bash
python3 scripts/selection.py report --keyword "随便的关键词" --platform "amazon" --country "US"
# 错误：KEYWORD_ILLEGAL - 关键词不合法
```

---

## 功能说明

本Skill封装了遨虾AI选品API，提供两大核心功能：

⚠️ **重要提示**：这两个功能有先后顺序依赖关系！
1. **第一步**：必须先调用 **关键词搜索 (search)** 获取合法的关键词列表
2. **第二步**：从返回结果中选择一个 `keyword` 字段的值
3. **第三步**：使用该关键词作为 **新品报告 (report)** 的 `--keyword` 参数

### 1. 关键词搜索 (search)

通过AI关键词查询API，根据用户输入的关键词匹配并返回相关关键词列表及市场数据：

- **关键词推荐** - AI匹配的相关关键词列表（中英文）
- **机会评分** - 每个关键词的市场机会综合评分和排名
- **市场趋势** - 近12个月搜索排名/达人数趋势
- **销售数据** - 30天销量、销售额及环比增长
- **雷达分析** - 市场需求、供给、销售、新品、评价五维评分

### 2. 新品报告 (report)

⚠️ **前置依赖**：此功能依赖"关键词搜索"的返回结果！
- 必须先执行 `search` 命令获取关键词列表
- `--keyword` 参数必须使用 `search` 返回的 `keyword` 字段值
- 随意填写关键词会报错 `KEYWORD_ILLEGAL`

通过AI新品报告执行API生成深度市场分析和新品推荐：

- **市场分析** - 市场评级、供需情况、销售表现、竞争态势
- **关键指标** - 搜索排名趋势、销量趋势、价格分析、雷达图
- **新品推荐** - AI筛选的机会新品及详细数据
- **竞品对比** - 新品与同类目热销品的深度对比分析


## 支持的平台和国家

### Amazon 平台
支持国家：`US`, `UK`, `ES`, `FR`, `DE`, `IT`, `CA`, `JP`

### TikTok 平台
支持国家：`ID`, `VN`, `MY`, `TH`, `PH`, `US`, `SG`, `BR`, `MX`, `GB`, `ES`, `FR`, `DE`, `IT`, `JP`

## 使用方法

### 功能1：关键词搜索 (search)

#### 基础用法

搜索关键词并获取相关关键词列表及市场数据：

```bash
python3 scripts/selection.py search \
  --keyword "yoga pants" \
  --platform "amazon" \
  --region "US"
```

#### 带上架时间筛选

指定商品上架时间范围：

```bash
python3 scripts/selection.py search \
  --keyword "yoga pants" \
  --platform "amazon" \
  --region "US" \
  --listing-time "90"
```

#### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `--keyword` | String | ✅ | 查询关键词（只支持单个关键词） | `"yoga pants"` |
| `--platform` | String | ✅ | 平台（`amazon` 或 `tiktok`，小写） | `"amazon"` |
| `--region` | String | ✅ | 国家代码（见上方支持列表） | `"US"` |
| `--listing-time` | String | ❌ | 商品上架时间范围（`"90"` 或 `"180"`，默认180天） | `"90"` |
| `--output-json` | Flag | ❌ | 输出完整JSON | - |

#### 返回数据

每个关键词包含：

- **关键词信息**
  - keyword: 英文关键词
  - keywordCn: 中文关键词
  - platform: 平台标识（amazon/tiktok）

- **机会评分**
  - oppScore: 市场机会综合评分（数值越高机会越大）
  - oppScoreDesc: 机会分解读（如"击败同一级类目85.5%关键词"）

- **核心指标**
  - searchRank: Amazon搜索排名 或 TikTok带货达人数
  - rankTrends: 近12个月趋势数据

- **销售数据**
  - soldCnt30d: 近30天累计销量及环比增长率
  - soldAmt30d: 近30天累计销售额及环比增长率

- **雷达分**
  - Amazon: 市场需求分、市场供给分、市场销售分、新品分、评价分（5维）
  - TikTok: 市场供给分、市场销售分、新品分、评价分（4维）

#### 输出示例

```
============================================================
相关关键词 (10)
============================================================

1. yoga pants (瑜伽裤)
   平台: AMAZON
   机会分: 37.2 (击败同一级类目85.5%关键词)
   最新1个月亚马逊搜索排名: # 3.6k+
   30天销量: 113.7w+ (↓ -17.5%)
   30天销售额: US$2603.9w+ (↓ -18.4%)
   雷达分: 市场需求分: 41.51, 市场供给分: 47.9, 市场销售分: 45.4...

2. yoga pants set (瑜伽裤套装)
   平台: AMAZON
   机会分: 38.9 (击败同一级类目91.5%关键词)
   最新1个月亚马逊搜索排名: # 20w+
   30天销量: 34.6w+ (↑ 4.7%)
   30天销售额: US$1219.4w+ (↑ 3.4%)
   雷达分: 市场需求分: 12.86, 市场供给分: 48.7, 市场销售分: 42.5...

============================================================
关键词数据已保存到: output/alphashop-sel-newproduct/keywords-yoga-pants-US-20260312-213928.json
============================================================
```

---

### 功能2：新品报告 (report)

⚠️ **重要**：使用此功能前，必须先调用"关键词搜索"获取合法关键词！

#### 基础用法

生成完整的新品选品报告：

```bash
python3 scripts/selection.py report \
  --keyword "phone" \
  --platform "amazon" \
  --country "US"
```

### 带筛选条件的用法

指定商品上架时间和筛选条件：

```bash
python3 scripts/selection.py report \
  --keyword "phone" \
  --platform "amazon" \
  --country "US" \
  --listing-time "90" \
  --min-price 10 \
  --max-price 100 \
  --min-sales 1 \
  --max-sales 1000 \
  --min-rating 2.0 \
  --max-rating 5.0
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 示例 |
|------|------|------|------|------|
| `--keyword` | String | ✅ | **⚠️ 必须从 `search` 命令返回的 `keyword` 字段获取，不可随意填写** | `"phone"` |
| `--platform` | String | ✅ | 平台（`amazon` 或 `tiktok`，小写） | `"amazon"` |
| `--country` | String | ✅ | 国家代码（见上方支持列表） | `"US"` |
| `--listing-time` | String | ❌ | 商品上架时间范围（`"90"` 或 `"180"`，默认180天） | `"90"` |
| `--min-price` | Number | ❌ | 最低价格 | `10` |
| `--max-price` | Number | ❌ | 最高价格 | `100` |
| `--min-sales` | Integer | ❌ | 最低月销量 | `1` |
| `--max-sales` | Integer | ❌ | 最高月销量 | `1000` |
| `--min-rating` | Float | ❌ | 最低评分（0-5.0） | `2.0` |
| `--max-rating` | Float | ❌ | 最高评分（0-5.0） | `5.0` |

## 返回数据说明

### 1. 市场分析（keywordSummary）

#### 市场评级
- **强烈推荐** (BEST) - 高增长、低竞争的蓝海机会
- **推荐进入** (GOOD) - 市场健康，有结构性机会
- **建议观望** (MEDIUM) - 市场平稳，需谨慎评估
- **不建议进入** (BAD) - 红海市场或需求萎缩

#### 市场总结（Markdown格式）
```markdown
##### 1. 市场机会总结
- 市场评级：✅推荐进入
- 市场总结：该关键词市场正处于需求强势扩张期...

##### 2. 市场情况分析
- 供给情况：在售商品数量过剩，落后于69%的同类市场...
- 需求情况：Amazon搜索排名持续提升...
- 商品销售情况：近30天销量达17.1万件...
```

#### 关键指标数据
- **需求侧**
  - 搜索排名趋势（近12个月）
  - 销量趋势（近12个月）
  - Google Trends数据
- **供给侧**
  - 在售商品数、品牌垄断系数、商品垄断系数
  - 中国卖家占比、新品销量占比
  - 商品平均评分
- **销售表现**
  - 30天销量/销售额及环比增长
  - 平均价格及价格带分析
- **雷达图**
  - 市场需求分、供给分、销售分、新品分、评价分

### 2. 新品推荐（productList）

每个新品包含：
- **基本信息**：标题、ASIN、类目、图片、链接
- **价格评分**：价格区间、评分、评论数
- **销售数据**：近30天销量、近12个月销量趋势
- **上架信息**：上架日期、上架天数
- **同款簇信息**：同款商品数、价格范围、平均评分
- **对比分析**：与同类目热销品的深度对比（Markdown格式）

## 输出示例

### 命令行输出

```
=== 市场分析 ===

市场评级: ✅推荐进入 (GOOD)
评级说明: 高增长、高客单、低新品竞争下的结构性机会

机会分: 41.7 (击败同一级类目60.5%关键词)

📊 关键指标:
- 30天销量: 17.1w+ (↑ 69.2%)
- 30天销售额: US$4170.1w+ (↑ 113.8%)
- 平均价格: US$313.27 (较高)
- 搜索排名: # 1.9k+ (BEST)
- 在售商品数: 133 (供给适中)
- 中国卖家占比: 19.3% (中低竞争)
- 新品成交占比: 0.1% (较难突围)

=== 推荐新品 (1) ===

1. Apple iPhone 17 Pro Max, US Version...
   价格: US$1449.99~US$1950.0
   评分: 4.1 ⭐ (0条评论)
   30天销量: 473件
   上架: 2025-10-09 (75天)
   同款: 12个商品
   链接: https://www.amazon.com/dp/B0FTC2PRVZ/

报告已保存到: output/alphashop-sel-newproduct/report-phone-US-20261212-143000.json
```

## 错误处理

### 常见错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `KEYWORD_ILLEGAL` | 关键词不合法 | 使用关键词查询API返回的关键词 |
| `TARGET_PLATFORM_ILLEGAL` | 平台不合法 | 只能是 `amazon` 或 `tiktok` |
| `TARGET_COUNTRY_ILLEGAL` | 国家不合法 | 检查国家代码是否在支持列表中 |
| `PRODUCT_LISTING_TIME_ERROR` | 上架时间参数错误 | 只能是 `"90"` 或 `"180"` |
| `PRODUCT_FILTER_PARAMS_ERROR` | 筛选参数错误 | 检查价格/销量/评分区间是否合理 |
| `PRODUCT_RECALL_EMPTY` | 商品召回为空 | 放宽筛选条件（扩大价格/销量区间） |
| `KEYWORD_RISK_ERROR` | 关键词涉及违禁 | 更换其他关键词 |
| `TIMEOUT_ERROR` | 请求超时 | 稍后重试 |

## 使用技巧

### 1. API 依赖关系（重要！）

⚠️ **关键词来源限制**：新品报告 API 的 `--keyword` 参数必须来自关键词搜索 API 的返回结果！

**正确的使用流程：**

```bash
# 步骤1：调用关键词搜索 API
python3 scripts/selection.py search \
  --keyword "phone" \
  --platform "amazon" \
  --region "US"

# 步骤2：从返回的关键词列表中选择一个 keyword 值
# 例如返回了：
# 1. phone - keyword: "phone"
# 2. phone case - keyword: "phone case"
# 3. phone holder - keyword: "phone holder"

# 步骤3：使用选中的 keyword 调用新品报告 API
python3 scripts/selection.py report \
  --keyword "phone case"  # ⚠️ 必须是 search 返回的 keyword 字段值
  --platform "amazon" \
  --country "US"
```

**错误示例：**
```bash
# ❌ 直接使用随意的关键词（会报错 KEYWORD_ILLEGAL）
python3 scripts/selection.py report \
  --keyword "my random keyword" \
  --platform "amazon" \
  --country "US"
```

**为什么有这个限制？**
- 关键词搜索 API 会对关键词进行 AI 分析和校验
- 只有经过校验的关键词才能保证新品报告的数据质量
- 随意填写的关键词可能无法匹配到有效的市场数据

### 2. 筛选条件设置
- **价格区间**：根据目标利润空间设置，最低价 < 最高价
- **销量区间**：建议设置宽松范围，避免召回为空
- **评分区间**：0-5.0，建议 `minRating >= 3.0` 过滤低质商品
- **上架时间**：`"90"` 查找最新商品，`"180"` 覆盖面更广

### 3. 报错处理
- `PRODUCT_RECALL_EMPTY`：说明筛选条件太严，建议：
  - 扩大价格区间（如 1-500）
  - 放宽销量要求（如 0-10000）
  - 降低评分门槛（如 0-5.0）

## API 接口地址

| 接口 | 方法 | URL | 响应耗时 |
|------|------|-----|---------|
| 关键词搜索API | POST | `https://api.alphashop.cn/opp.selection.keyword.search/1.0` | 10秒内 |
| 新品报告API | POST | `https://api.alphashop.cn/opp.selection.newproduct.report/1.0` | 10秒内 |

## 注意事项

1. **响应时间**：接口响应需要几十秒，请耐心等待
2. **无需鉴权**：API为公开接口，无需配置Token
3. **同步返回**：一次调用即可获得完整报告，无需轮询
4. **关键词限制**：仅支持单个关键词，不支持多关键词组合
5. **平台差异**：Amazon和TikTok的数据结构和指标略有差异

## 完整示例

### 正确的完整工作流

```bash
# ====================================
# 步骤1：关键词搜索
# ====================================
python3 scripts/selection.py search \
  --keyword "yoga pants" \
  --platform "amazon" \
  --region "US" \
  --listing-time "90"

# 输出示例：
# 1. yoga pants (瑜伽裤) - keyword: "yoga pants"
# 2. yoga pants women (女士瑜伽裤) - keyword: "yoga pants women"
# 3. yoga pants set (瑜伽裤套装) - keyword: "yoga pants set"

# ====================================
# 步骤2：选择关键词生成新品报告
# ====================================
# ⚠️ 注意：--keyword 必须使用步骤1返回的 keyword 字段值

python3 scripts/selection.py report \
  --keyword "yoga pants set" \
  --platform "amazon" \
  --country "US" \
  --listing-time "90" \
  --min-price 15 \
  --max-price 50 \
  --min-sales 10 \
  --min-rating 3.5

# ====================================
# TikTok 平台完整示例
# ====================================

# 步骤1：搜索关键词
python3 scripts/selection.py search \
  --keyword "female dress" \
  --platform "tiktok" \
  --region "ID"

# 步骤2：生成报告
python3 scripts/selection.py report \
  --keyword "female dress"  # 使用步骤1返回的 keyword
  --platform "tiktok" \
  --country "ID" \
  --listing-time "180"
```

## API 参考文档

完整的API接口和数据结构文档请参阅 [references/api.md](references/api.md)。
