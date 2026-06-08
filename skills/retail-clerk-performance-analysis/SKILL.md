---
name: retail-clerk-performance-analysis
description: |
  导购个人业绩深度分析工具。支持普通门店（POS数据）和AIoT门店（POS+AIoT数据）。
  
  输出导购个人详细诊断报告，包含：
  1. 核心业绩指标（销售额、排名、业绩占比）
  2. 雷达图能力对比（6维能力 vs 门店平均）
  3. 商品特征分析（品类/价格带/包型/颜色/新品偏好）
  4. Top5 SKU爆品分析（门店贡献率、SPU集中度、上市时间）
  5. 订单结构分析（折扣/连带/会员结构）
  6. AIoT高试用低转化分析（仅AIoT门店）
  7. AIoT客户漏斗分析（仅AIoT门店）
  8. 14天销售趋势分析
  9. 综合诊断与行动建议
  
  触发条件：
  - 用户询问导购业绩（如"李翠业绩怎么样"）
  - 用户分析导购能力（如"导购销售能力如何"）
  - 用户需要导购诊断（如"导购有什么问题"）
---

# 导购个人业绩分析 Skill

## 技能名称
`clerk-performance-analysis`

## 功能描述
对单个导购进行深度业绩分析，支持两种门店类型：
1. **普通门店**（POS数据）- 所有门店可用
2. **AIoT门店**（POS + AIoT数据）- 仅巽融智能体门店可用

输出导购个人的详细诊断报告，包含业绩指标、商品特征、订单结构、AIoT转化分析等多维度分析。

## 快速开始

详见 [USAGE.md](./USAGE.md) 获取完整使用指南。

### 简单示例

```python
import sys
sys.path.insert(0, '~/.openclaw/skills/clerk-performance-analysis')
from analyze import analyze

# 执行分析（Skill自动判断门店类型）
result = analyze(
    store_id="416759_1714379448487",
    guide_name="李翠",
    from_date="2026-03-01",
    to_date="2026-03-25"
)

# 查看结果
print(f"销售额: ¥{result['core_metrics']['sales']['amount']:,.0f}")
print(f"排名: #{result['core_metrics']['sales']['rank']}")
```

## 数据来源

### API 1: 导购详细数据
```
GET /api/v1/guide/detail?guideName={name}&storeId={id}&fromDate={from}&toDate={to}
```

**返回数据结构：**
- `guideOverallPerformance` - 导购整体表现（含排名、雷达图）
- `featureDistribution` - 商品特征分布（品类/价格带/包型/颜色/上市日期）
- `skuRanking` - SKU销售排行

### API 2: 订单分析数据
```
GET /api/v1/guide/order-analysis?storeId={id}&fromDate={from}&toDate={to}&guideName={name}
```

**返回数据结构：**
- `OrderDiscounts` - 订单折扣分布
- `OrderAttachs` - 订单连带分布
- `OrderMembers` - 订单会员结构

### API 3: AIoT高试用低转化分析（仅AIoT门店）
```
GET /api/v1/guide/high-trial-low-conversion?guideName={name}&storeId={id}&fromDate={from}&toDate={to}
```

**返回数据结构：**
- `highTrialLowConversion` - 高试用低转化商品列表
  - `goodsName` - 商品名称
  - `goodsModelCode` - 款号
  - `trialCount` - 试用次数
  - `dealCount` - 成交件数
  - `conversionRate` - 转化率
  - `standardPrice` - 标准价

### API 4: AIoT客户漏斗分析（仅AIoT门店）
```
GET /api/v1/guide/customer-funnel?guideName={name}&storeId={id}&fromDate={from}&toDate={to}
```

**返回数据结构：**
- `customerFunnel` - 客户分层漏斗数据
  - `有效客户` - 有交互行为的客户总数
  - `普通客户` - 无试用行为的客户
  - `潜在客户` - 有普通试用的客户
  - `意向客户` - 有深度试用的客户
  - `成交客户` - 有成交的客户
- 环比数据（与上期对比）

## 核心能力

### 1. 核心业绩指标分析
- 销售额、排名、业绩占比
- 订单数、客单价、连带率
- 新客数、人效值、有订单天数

### 2. 雷达图能力对比
6维能力对比（导购 vs 门店平均）：
- 销售额
- 订单数
- 新客数
- 客单价
- 件单价
- 连带率

### 3. 商品特征分析
- **品类偏好**: 主营品类及占比
- **价格带分布**: 主销价格带、高客单占比（≥800元）
- **包型偏好**: 主销包型分析
- **颜色偏好**: 主销颜色分析
- **新品销售**: 2026年新品销售占比

### 4. 爆品分析（Top5 SKU）
- **Top5 SKU列表**: 销售额排名前五的商品明细
- **销量分析**: 各SKU销量、销售额、成交均价
- **门店贡献率**: 导购该SKU销售额占门店该SKU总销售的比例（反映导购对爆款的主导程度）
- **价格分析**: 标准价 vs 实际成交均价（折扣情况）
- **SPU集中度**: 按商品名称聚合，分析款式集中度
- **上市时间偏好**: 分析导购对新品/老品的销售偏好
- **新品识别**: 成交时上市时间≤3个月的商品（可为负值=预售）

### 5. 订单结构分析
- **折扣结构**: 主销折扣区间、低折扣订单占比（6折以下）
- **连带结构**: 1件单占比、多连带占比（≥3件）、平均连带
- **会员结构**: 老会员/新会员/非会员销售占比

### 6. AIoT高试用低转化分析（仅AIoT门店）
- **高试用低转化商品识别**: 试用次数多但成交为0的商品
- **转化能力评估**: 分析导购的试用后跟进转化能力
- **重点商品关注**: Top3高试用低转化商品详情

### 7. AIoT客户漏斗分析（仅AIoT门店）
- **客户分层漏斗**: 有效客户→普通→潜在→意向→成交的转化路径
- **环比趋势分析**: 与上期对比的客户量变化
- **工牌佩戴检测**: 识别导购是否佩戴电子工牌（影响数据采集完整性）
- **转化效率评估**: 各层级的转化率分析

**重要说明：**
1. **未佩戴电子工牌**：只能记录成交客户（通过订单系统关联），无法获取试用行为数据。此时所有有效客户都显示为"成交客户"，这是**正常情况**。
2. **导购信息未维护**：如果客户漏斗数据全为0，说明导购信息未在AIoT系统维护，此时`high-trial-low-conversion`返回的是**门店整体**数据，非个人数据。

**边界情况处理：**

| 情况 | 现象 | 处理方式 |
|------|------|----------|
| 未佩戴工牌 | 所有客户显示为成交客户 | 正常，提示"未佩戴电子工牌" |
| 信息未维护 | 客户漏斗全为0 | 警告"AIoT信息未维护"，高试用低转化数据为门店整体 |

### 8. 销售额Top5与高试用低转化Top5对比（仅AIoT门店且customer-funnel正常）

**前提条件：**
- 仅AIoT门店可用
- `customer-funnel` 数据正常（不全为0）
- 用于分析导购个人销售新品的情况

**分析维度：**
- **重叠商品分析**: 同时在高销售和高试用的商品
- **销售-only商品**: 销售好但试用少的商品
- **试用-only商品**: 试用多但未成交的商品
- **新品转化分析**: 高试用低转化中的新品识别（重点）
- **SPU集中度对比**: 销售额Top5与高试用低转化Top5的SPU分布

**触发培训建议：**
- 当高试用低转化商品中新品≥2个时，触发"新品转化专项提升"建议

### 9. 14天销售趋势分析
- **日度销售追踪**: 近14天每日销售额、订单数、客单价、业绩占比
- **销售连续性**: 有销售天数 vs 无销售天数
- **峰值识别**: 销售最高/最低的日期
- **近期趋势**: 近7天详细数据

### 10. 综合诊断
- 业绩排名诊断
- 能力短板识别
- 品类集中度风险
- 高客单销售能力评估
- 连带销售能力评估
- 议价能力评估
- 销售连续性评估

## 使用方法

```python
import sys
sys.path.insert(0, '~/.openclaw/skills/clerk-performance-analysis')
from analyze import analyze, batch_analyze

# 分析单个导购
result = analyze(
    store_id="416759_1714379448487",
    guide_name="李翠",
    from_date="2026-03-01",
    to_date="2026-03-25"
)

# 批量分析多个导购
results = batch_analyze(
    store_id="416759_1714379448487",
    guide_names=["李翠", "杨丽", "赵泽瑞"],
    from_date="2026-03-01",
    to_date="2026-03-25"
)
```

## 输入参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `store_id` | str | 是 | 门店ID |
| `guide_name` | str | 是 | 导购姓名 |
| `from_date` | str | 是 | 分析开始日期 (YYYY-MM-DD) |
| `to_date` | str | 是 | 分析结束日期 (YYYY-MM-DD) |

## 输出结构

```json
{
  "status": "ok",
  "store_id": "416759_1714379448487",
  "guide_name": "李翠",
  "analysis_period": {"from": "2026-03-01", "to": "2026-03-25"},
  "core_metrics": {
    "sales": {"amount": 64559, "rank": 2, "share": 20.6},
    "orders": {"count": 96, "rank": 2},
    "atv": {"value": 672.49, "rank": 3},
    "attach": {"qty_ratio": 1.48, "sku_ratio": 1.43},
    "new_customers": {"count": 29, "rank": 1},
    "efficiency": {"value": 3398, "rank": 1, "order_days": 19}
  },
  "radar_analysis": {
    "salesAmount": {"guide": 64559, "store_avg": 43391, "ratio": 1.49, "gap": 21168},
    "effectiveOrderCount": {"guide": 96, "store_avg": 70, "ratio": 1.37, "gap": 26},
    "newCustomerCount": {"guide": 29, "store_avg": 16, "ratio": 1.81, "gap": 13},
    "customerUnitPrice": {"guide": 672, "store_avg": 655, "ratio": 1.03, "gap": 17},
    "qtyUnitPrice": {"guide": 455, "store_avg": 450, "ratio": 1.01, "gap": 5},
    "attachQtyRatio": {"guide": 1.48, "store_avg": 1.48, "ratio": 1.0, "gap": 0}
  },
  "feature_analysis": {
    "category": {"top": "女包", "top_percentage": 78, "distribution": [...]},
    "price_range": {"top": "1000-1200", "top_percentage": 30, "high_price_ratio": 65},
    "shape": {"top": "方包", "top_percentage": 30},
    "color": {"top": "黑色系", "top_percentage": 37},
    "new_items": {"ratio": 30}
  },
  "sku_analysis": {
    "top5_skus": [
      {
        "rank": 1,
        "name": "心遥",
        "code": "H51556659",
        "sales": 3510.1,
        "qty": 3,
        "avg_price": 1170.03,
        "contribute_rate": 100,
        "standard_price": 1299,
        "launch_date": "2025/7/1",
        "launch_year": 2025,
        "launch_month": 7,
        "is_new": false,
        "months_diff": 8
      }
    ],
    "total_skus": 5,
    "top5_total_sales": 13161.13,
    "top5_total_qty": 12,
    "spu_concentration": {
      "total_spu": 4,
      "spu_list": [
        {"name": "心遥", "sku_count": 2, "sales": 5444.12, "qty": 5},
        {"name": "舒珀", "sku_count": 1, "sales": 3409.05, "qty": 3}
      ]
    },
    "launch_date_analysis": {
      "total_items": 5,
      "new_items_count": 1,
      "new_items_ratio": 20.0,
      "launch_dates": [...]
    },
    "new_items": [
      {
        "name": "鞣迹",
        "code": "H51457102",
        "launch_date": "2025/12/1",
        "months_diff": 3,
        "is_new": true
      }
    ]
  },
  "order_analysis": {
    "discount": {
      "main_range": "8-9折",
      "main_share": 55.2,
      "low_discount_ratio": 27.6,
      "total_orders": 98
    },
    "attach": {
      "single_item_ratio": 65.3,
      "multi_item_ratio": 12.2,
      "avg_attach": 1.50,
      "total_orders": 98
    },
    "member": {
      "old_member_ratio": 64.2,
      "new_member_ratio": 33.3,
      "non_member_ratio": 2.3,
      "total_customers": 89
    }
  },
  "aiot_analysis": {
    "is_aiot_store": true,
    "item_count": 5,
    "total_trials": 14,
    "items": [
      {
        "name": "心遥（2）",
        "code": "H51757021",
        "trial_count": 3,
        "deal_count": 0,
        "conversion_rate": 0,
        "price": 1299
      }
    ]
  },
  "funnel_analysis": {
    "is_aiot_store": true,
    "effective_customers": 42,
    "deal_customers": 42,
    "conversion_rate": 100.0,
    "badge_not_worn": true,
    "note": "导购未佩戴电子工牌，仅记录成交客户",
    "funnel": {
      "有效客户": {"value": 42, "percentage": 100, "trend": "down", "link_relative_rate": 28.0},
      "普通客户": {"value": 0, "percentage": 0},
      "潜在客户": {"value": 0, "percentage": 0},
      "意向客户": {"value": 0, "percentage": 0},
      "成交客户": {"value": 42, "percentage": 100, "trend": "down", "link_relative_rate": 22.0}
    }
  },
  "findings": [...],
  "recommendations": [...]
}
```

## 核心指标解释

### 业绩指标
| 指标 | 字段 | 说明 |
|------|------|------|
| 销售额 | `sales.amount` | 销售总额 |
| 业绩排名 | `sales.rank` | 门店内排名 |
| 业绩占比 | `sales.share` | 占门店总业绩比例 |
| 订单数 | `orders.count` | 有效订单数 |
| 客单价 | `atv.value` | 平均客单价 |
| 连带率 | `attach.qty_ratio` | 数量连带率 |
| 新客数 | `new_customers.count` | 新增会员数 |
| 人效值 | `efficiency.value` | 日均业绩贡献 |
| 有订单天数 | `efficiency.order_days` | 统计周期内有成交的天数 |

### 雷达图指标
| 指标 | 说明 |
|------|------|
| `ratio` | 导购值 / 门店平均值，>1表示优于平均 |
| `gap` | 导购与门店平均的绝对差距 |

### 商品特征指标
| 指标 | 说明 |
|------|------|
| `top` | 占比最高的品类/价格带/包型/颜色 |
| `top_percentage` | 占比百分比 |
| `high_price_ratio` | 800元以上商品销售占比 |
| `new_items.ratio` | 2026年新品销售占比 |

### 订单结构指标
| 指标 | 字段 | 说明 |
|------|------|------|
| 主销折扣 | `order_analysis.discount.main_range` | 占比最高的折扣区间 |
| 低折扣占比 | `order_analysis.discount.low_discount_ratio` | 6折以下订单占比 |
| 1件单占比 | `order_analysis.attach.single_item_ratio` | 单件订单占比 |
| 多连带占比 | `order_analysis.attach.multi_item_ratio` | ≥3件订单占比 |
| 平均连带 | `order_analysis.attach.avg_attach` | 平均连带件数 |
| 老会员占比 | `order_analysis.member.old_member_ratio` | 老会员销售占比 |
| 新会员占比 | `order_analysis.member.new_member_ratio` | 新会员销售占比 |

### AIoT指标（仅AIoT门店）
| 指标 | 字段 | 说明 |
|------|------|------|
| 是否AIoT门店 | `aiot_analysis.is_aiot_store` | 是否有AIoT数据 |
| 高试用低转化商品数 | `aiot_analysis.item_count` | 试用>0但成交=0的商品数 |
| 总试用次数 | `aiot_analysis.total_trials` | 这些商品的总试用次数 |
| 商品名称 | `aiot_analysis.items[].name` | 高试用低转化商品名称 |
| 试用次数 | `aiot_analysis.items[].trial_count` | 该商品被试用次数 |
| 成交件数 | `aiot_analysis.items[].deal_count` | 该商品成交件数 |
| 转化率 | `aiot_analysis.items[].conversion_rate` | 试用转化率 |

## 诊断规则

| 问题 | 判断条件 | 严重程度 |
|------|----------|----------|
| 业绩排名靠后 | 排名 > 3 | 🟡 中 |
| 新客获取能力不足 | 新客数 < 门店平均70% | 🟡 中 |
| 新客获取能力突出 | 新客数 > 门店平均150% | 🟢 低（优势）|
| 客单价偏低 | 客单价 < 门店平均85% | 🟡 中 |
| 品类过于集中 | 单一品类占比 > 70% | 🟡 中 |
| 高客单销售弱 | 800元以上占比 < 30% | 🟡 中 |
| **连带销售能力不足** | **1件单占比 > 60%** | 🟡 中 |
| **低折扣订单占比过高** | **6折以下订单 > 20%** | 🟡 中 |
| **导购AIoT信息未维护** | **客户漏斗全为0** | 🟡 中（仅AIoT） |
| **高试用低转化商品多** | **≥3个高试用低转化商品** | 🟡 中（仅AIoT） |
| **新品试用转化差** | **高试用低转化中新品≥2个** | 🟡 中（仅AIoT） |
| **有效客户大幅下降** | **环比下降>20%** | 🔴 高（仅AIoT） |
| **无销售天数过多** | **14天中≥5天无销售** | 🟡 中 |
| **日均销售额偏低** | **日均<¥1000** | 🟡 中 |

## 分析示例

### 李翠（3月1日-25日）

**核心业绩：**
- 销售额 ¥64,559，排名#2，占比20.6%
- 订单数 96单，排名#2
- 新客数 29人，排名#1
- 人效值 3398，排名#1

**雷达图对比：**
- 销售额：149%（优于平均49%）
- 订单数：137%（优于平均37%）
- 新客数：181%（优于平均81%）⭐
- 客单价：103%（与平均持平）
- 连带率：100%（与平均持平）

**商品特征：**
- 主营品类：女包（78%）
- 主销价格带：1000-1200元（30%）
- 高客单占比：65%
- 主销包型：方包（30%）
- 新品销售占比：30%

**订单结构：**
- 主销折扣：8-9折（55.2%）
- 低折扣订单：27.6%（6折以下）
- 1件单占比：65.3%
- 多连带占比：12.2%
- 老会员：64.2%，新会员：33.3%

**爆品分析（Top5 SKU）：**

| 排名 | 款号 | 名称 | 销量 | 销售额 | 均价 | 门店贡献率 | 上市时间 | 新品 |
|------|------|------|------|--------|------|------------|----------|------|
| #1 | H51556659 | 心遥 | 3件 | ¥3,510 | ¥1,170 | 100% | 2025/7 | |
| #2 | H51456675 | 舒珀 | 3件 | ¥3,409 | ¥1,136 | 100% | 2025/7 | |
| #3 | H51457102 | 鞣迹 | 2件 | ¥2,174 | ¥1,087 | 69% | 2025/12 | ✓ |
| #4 | H60101090 | 爱旅 | 2件 | ¥2,134 | ¥1,067 | 100% | 2025/7 | |
| #5 | H51556656 | 心遥 | 2件 | ¥1,934 | ¥967 | 34% | 2025/7 | |

**Top5合计**: 销量12件, 销售额¥13,161（占总业绩20.4%）

> **门店贡献率** = 导购该SKU销售额 / 门店该SKU总销售额

**SPU集中度：**
- 共涉及4个SPU（商品名称）
- 心遥: 2个SKU, 销售额¥5,444（41.4%）
- 舒珀: 1个SKU, 销售额¥3,409（25.9%）
- 鞣迹: 1个SKU, 销售额¥2,174（16.5%）
- 爱旅: 1个SKU, 销售额¥2,134（16.2%）

**上市时间偏好：**
- 新品占比: 1/5 (20.0%)
- 新品: 鞣迹 (2025/12/1, +3月)

**AIoT高试用低转化分析（仅AIoT门店）：**
- 发现 5 个高试用低转化商品
- 总试用次数：14 次
- Top3：心遥（2）3次、迁屿3次、合和3次（均0成交）

**AIoT客户漏斗分析（仅AIoT门店）：**
- 有效客户：42人，成交客户：42人，转化率100%
- ℹ️ 导购未佩戴电子工牌，仅记录成交客户，无法获取试用行为数据
- 有效客户环比下降28%（需关注）

**诊断发现：**
- 🟢 业绩表现良好（排名#2）
- 🟢 新客获取能力突出（门店第一）
- 🟡 品类销售过于集中（女包78%）
- 🟡 **连带销售能力不足**（1件单65.3%）
- 🟡 **低折扣订单占比过高**（27.6%）
- 🟡 **存在5个高试用低转化商品**（AIoT）
- 🔴 **有效客户环比下降28%**（AIoT）

**行动建议：**
1. 🔴 连带销售强化训练 - 练习二拍一话术、搭配推荐
2. 🔴 **试用跟进转化专项** - 针对心遥（2）等试用未成交商品，学习跟进话术
3. 🔴 **客流提升专项** - 加强邀约回店、社群运营（应对有效客户下降）
4. 🟡 议价能力提升 - 减少不必要的折扣让步
5. 🟡 拓展品类销售 - 加强其他品类学习

## 版本
v3.1.0 - 导购个人业绩深度分析（新增销售额Top5与高试用低转化Top5对比分析）

## 相关文档
- [USAGE.md](./USAGE.md) - 详细使用指南和API说明
