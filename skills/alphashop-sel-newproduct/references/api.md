# 遨虾AI选品API文档

## 接口概述

**接口名称**: AI新品报告执行API
**接口功能**: 通过用户选择的关键词以及商品筛选条件去执行并返回新品分析报告
**请求方式**: POST
**Content-Type**: application/json
**响应耗时**: 几十秒（同步返回）
**Endpoint**: `https://api.alphashop.cn/opp.selection.newproduct.report/1.0`

## 请求参数

### 必填参数

| 字段名 | 类型 | 说明 | 示例值 |
|--------|------|------|--------|
| `productKeyword` | String | 关键词（**必须使用关键词查询API返回的关键词**） | `"phone"` |
| `targetPlatform` | String | 目标平台（`amazon` 或 `tiktok`） | `"amazon"` |
| `targetCountry` | String | 目标国家代码 | `"US"` |

### 可选参数

| 字段名 | 类型 | 说明 | 默认值 |
|--------|------|------|--------|
| `listingTime` | String | 商品上架时间范围（`"90"` 或 `"180"`） | `"180"` |
| `minPrice` | Long | 最低价格 | - |
| `maxPrice` | Long | 最高价格 | - |
| `minVolume` | Integer | 最低月销量 | - |
| `maxVolume` | Integer | 最高月销量 | - |
| `minRating` | Double | 最低评分（0-5.0） | - |
| `maxRating` | Double | 最高评分（0-5.0） | - |

### 参数约束

#### 平台和国家

**Amazon平台** 支持8个地区：
- US (美国)
- UK (英国)
- ES (西班牙)
- FR (法国)
- DE (德国)
- IT (意大利)
- CA (加拿大)
- JP (日本)

**TikTok平台** 支持15个地区：
- ID (印度尼西亚)
- VN (越南)
- MY (马来西亚)
- TH (泰国)
- PH (菲律宾)
- US (美国)
- SG (新加坡)
- BR (巴西)
- MX (墨西哥)
- GB (英国)
- ES (西班牙)
- FR (法国)
- DE (德国)
- IT (意大利)
- JP (日本)

#### 筛选条件约束

- **价格区间**: 最低价 < 最高价
- **销量区间**: 最低销量 < 最高销量
- **评分区间**: [0, 5.0]，最低评分 < 最高评分
- **上架时间**: 只能是 `"90"` 或 `"180"`

⚠️ **注意**: 设置过于严格的筛选条件可能导致 `PRODUCT_RECALL_EMPTY` 错误

## 请求示例

```json
{
  "productKeyword": "phone",
  "targetPlatform": "amazon",
  "targetCountry": "US",
  "listingTime": "90",
  "minPrice": 10,
  "maxPrice": 100,
  "minVolume": 1,
  "maxVolume": 1000,
  "minRating": 2.0,
  "maxRating": 5.0
}
```

## 响应结构

### 成功响应

```json
{
  "success": true,
  "code": "SUCCESS",
  "msg": null,
  "data": {
    "keywordSummary": { ... },
    "productList": [ ... ]
  }
}
```

### 失败响应

```json
{
  "success": false,
  "code": "KEYWORD_ILLEGAL",
  "msg": "请填写有效的关键词",
  "data": null
}
```

## 响应数据详解

### 1. keywordSummary（市场分析）

#### 1.1 summary（市场总结）

Markdown格式的市场分析文本，包含：
- 市场机会总结（市场评级、市场总结）
- 市场情况分析（供给情况、需求情况、商品销售情况）

示例：
```markdown
##### 1. 市场机会总结
- **市场评级**：✅推荐进入。[高增长、高客单、低新品竞争下的结构性机会]
- **市场总结**：该关键词市场正处于需求强势扩张期...
```

#### 1.2 keywordLevelDetail（市场评级）

| 字段 | 类型 | 说明 | 示例值 |
|------|------|------|--------|
| `valueLevel` | String | 评级等级 | `"GOOD"` |
| `text` | String | 评级文字 | `"推荐进入"` |
| `valueLevelDesc` | String | 评级说明 | `"高增长、高客单..."` |

评级等级：
- `BEST` - 强烈推荐
- `GOOD` - 推荐进入
- `MEDIUM` - 建议观望
- `BAD` - 不建议进入

#### 1.3 keywordIndexesInfo（关键指标）

**基本信息**：
- `platform` - 平台
- `keyword` - 关键词
- `keywordCn` - 中文关键词
- `region` - 地区
- `oppScore` - 机会分
- `oppScoreDesc` - 机会分描述

**需求侧数据（demandInfo）**：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `searchRank` | 最新搜索排名 | `"# 1.9k+"` |
| `searchRankLevel` | 排名等级 | `"BEST"` |
| `rankTrends` | 近12个月搜索排名趋势 | `[{"x":"202412","y":2643}, ...]` |
| `salesVolumeTrends` | 近12个月销量趋势 | `[{"x":"202412","y":91878}, ...]` |

**供给侧数据（supplyInfo）**：

| 字段 | 说明 | 等级（valueLevel） |
|------|------|-------------------|
| `itemCount` | 在售商品数 | BEST(供给稀缺) / GOOD(供给偏少) / MEDIUM(供给适中) / BAD(供给过剩) |
| `cnSellerPct` | 中国卖家占比 | BEST(低竞争) / GOOD(中低竞争) / MEDIUM(中高竞争) / BAD(竞争激烈) |
| `brandMonopolyCoefficient` | 品牌垄断系数 | BEST(白牌为主) / GOOD(品牌分散) / MEDIUM(品牌集中) / BAD(品牌垄断) |
| `itemMonopolyCoefficient` | 商品垄断系数 | BEST(低垄断) / GOOD(中低垄断) / MEDIUM(中高垄断) / BAD(高垄断) |
| `newProductSalesPct` | 新品销量占比 | BEST(新品易入) / GOOD(新品较易) / MEDIUM(机会一般) / BAD(较难突围) |
| `ratingAvg` | 商品平均评分 | BEST(口碑极佳) / GOOD(口碑良好) / MEDIUM(口碑一般) / BAD(口碑欠佳) |

**销售表现（salesInfo）**：

| 字段 | 说明 | 示例值 |
|------|------|--------|
| `soldCnt30d` | 30天销量 | `{"value":"17.1w+","growthRate":{"direction":"UP","value":"69.2%"},...}` |
| `soldAmt30d` | 30天销售额 | `{"value":{"amountWithSymbol":"US$4170.1w+"},...}` |

**利润相关（profitInfo）**：

| 字段 | 说明 | 等级 |
|------|------|------|
| `priceAvg` | 平均价格 | BEST(高) / GOOD(较高) / MEDIUM(适中) / BAD(较低) |

**雷达图（radar）**：

```json
{
  "propertyList": [
    {"name": "市场需求分", "value": 46.53},
    {"name": "市场供给分", "value": 58.1},
    {"name": "市场销售分", "value": 51.7},
    {"name": "新品分", "value": 11.5},
    {"name": "评价分", "value": 91}
  ],
  "radarDescription": "通过该关键词的搜索量、销售额..."
}
```

### 2. productList（新品列表）

每个新品包含的字段：

#### 基本信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `productId` | String | 商品唯一ID |
| `title` | String | 商品标题 |
| `catePath` | String | 类目路径 |
| `mainImgUrl` | String | 主图URL |
| `productUrl` | String | 商品链接 |
| `platform` | String | 平台 |
| `region` | String | 地区 |

#### 价格和评分

| 字段 | 类型 | 说明 |
|------|------|------|
| `priceRange` | String | 价格区间 |
| `ratingRange` | String | 评分 |
| `reviewCnt` | Integer | 评论数 |

#### 销售数据

| 字段 | 类型 | 说明 |
|------|------|------|
| `soldCnt30d` | String | 30天销量 |
| `soldCntHisByM` | Array | 月度销量历史 |

示例：
```json
"soldCntHisByM": [
  {"timeValue": "202511", "trendValue": "423.0"},
  {"timeValue": "202510", "trendValue": "38.0"}
]
```

#### 上架信息

| 字段 | 类型 | 说明 |
|------|------|------|
| `onShelfDate` | String | 上架日期 |
| `onShelfDays` | Integer | 上架天数 |

#### 同款簇信息（spInfo）

| 字段 | 类型 | 说明 |
|------|------|------|
| `spItmCnt` | Integer | 同款商品数 |
| `spPriceMin` | Object | 簇内最低价 |
| `spPriceMax` | Object | 簇内最高价 |
| `spRatingMid` | Number | 簇内平均评分 |
| `launchTime` | String | 最早上架时间 |

#### 对比分析（summary）

String (Markdown) - 与同类目热销品的详细对比分析

## 错误码

| 错误码 | 说明 | 解决方案 |
|--------|------|----------|
| `SUCCESS` | 执行成功 | - |
| `REQUEST_PARAM_EMPTY` | 请求参数为空 | 检查必填参数 |
| `KEYWORD_EMPTY` | 关键词为空 | 提供关键词 |
| `KEYWORD_ILLEGAL` | 关键词不合法 | 使用关键词查询API返回的关键词 |
| `TARGET_PLATFORM_EMPTY` | 目标平台为空 | 提供平台参数 |
| `TARGET_COUNTRY_EMPTY` | 目标国家为空 | 提供国家参数 |
| `TARGET_PLATFORM_ILLEGAL` | 目标平台不合法 | 只能是 `amazon` 或 `tiktok` |
| `TARGET_COUNTRY_ILLEGAL` | 目标国家不合法 | 检查国家代码是否在支持列表中 |
| `PRODUCT_LISTING_TIME_ERROR` | 商品上架时间参数错误 | 只能是 `"90"` 或 `"180"` |
| `PRODUCT_FILTER_PARAMS_ERROR` | 商品筛选参数错误 | 检查价格/销量/评分区间 |
| `KEYWORD_SEARCH_ERROR` | 关键词查询异常 | 稍后重试 |
| `NEW_PRODUCT_REPORT_ERROR` | 新品选品报告生成异常 | 稍后重试 |
| `TIMEOUT_ERROR` | 请求超时 | 稍后重试 |
| `KEYWORD_RISK_ERROR` | 关键词涉及违禁 | 更换关键词 |
| `PRODUCT_RECALL_EMPTY` | 商品召回为空 | 放宽筛选条件 |
| `REQUEST_PARAM_ILLEGAL` | 请求参数非法 | 检查参数格式 |
| `USER_ID_EMPTY` | 用户ID为空 | 提供用户ID |

## 使用注意事项

1. **关键词来源**: `productKeyword` 必须使用关键词查询API返回的关键词，随意填写会报错
2. **响应时间**: 接口需要几十秒处理时间，请设置足够的超时时间
3. **筛选条件**: 设置过严可能导致无结果，建议适当放宽
4. **无需鉴权**: API为公开接口，无需配置Token
5. **同步返回**: 一次调用即可获得完整报告，无需轮询
