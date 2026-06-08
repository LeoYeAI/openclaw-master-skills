# 导购个人业绩分析 Skill - 使用指南

## 技能名称
`clerk-performance-analysis`

## 功能概述
对单个导购进行深度业绩分析，支持两种门店类型：
1. **普通门店**（POS数据）- 所有门店可用
2. **AIoT门店**（POS + AIoT数据）- 仅巽融智能体门店可用

## API分类

### 通用API（所有门店）

| 序号 | API | 功能 | 数据维度 |
|------|-----|------|----------|
| 1 | `/api/v1/guide/detail` | 导购详细业绩 | 销售额、订单数、客单价、连带率、新客数、排名、雷达图、商品特征、Top5 SKU |
| 2 | `/api/v1/guide/order-analysis` | 订单结构分析 | 折扣分布、连带分布、会员结构 |
| 3 | `/api/v1/guide/trend14days` | 14天趋势 | 日度销售额、订单数、客单价、业绩占比 |

### AIoT专属API（仅AIoT门店）

| 序号 | API | 功能 | 数据维度 | 依赖条件 |
|------|-----|------|----------|----------|
| 4 | `/api/v1/guide/customer-funnel` | 客户漏斗 | 有效/普通/潜在/意向/成交客户分层 | 无 |
| 5 | `/api/v1/guide/high-trial-low-conversion` | 高试用低转化 | 试用次数多但成交为0的商品 | 无 |
| 6 | **销售额Top5 vs 高试用低转化对比** | 新品转化分析 | 重叠商品、新品转化问题 | **依赖customer-funnel正常** |

**注意：**
1. 如果导购信息未在AIoT系统维护：
   - `customer-funnel` 返回全0数据
   - `high-trial-low-conversion` 返回**门店整体**数据（非个人数据）
   - Skill会自动识别并提示

2. **销售额Top5与高试用低转化对比分析** 仅在 `customer-funnel` 数据正常时可用：
   - 用于分析导购**个人**销售新品的情况
   - 当高试用低转化中**新品≥2个**时，触发"新品转化专项提升"培训建议

## 使用方法

### 步骤1：判断门店类型

```python
import sys
sys.path.insert(0, '/Users/yangguangwei/.openclaw/workspace-front-door')
from api_client import get_api_client

def check_aiot_store(store_id: str) -> bool:
    """检查是否为AIoT门店"""
    client = get_api_client()
    response = client.call_api('copilot', '/api/v1/user/store/list', 
                               params={'pageNo': '1', 'pageSize': '999'})
    
    for store in response.get('list', []):
        if store.get('storeId') == store_id:
            return store.get('isAiot') == 1
    return False

# 使用示例
store_id = "416759_1714379448487"
is_aiot = check_aiot_store(store_id)
print(f"门店 {store_id} 是否为AIoT门店: {is_aiot}")
```

### 步骤2：执行分析

```python
import sys
sys.path.insert(0, '~/.openclaw/skills/clerk-performance-analysis')
from analyze import analyze

# 分析参数
store_id = "416759_1714379448487"
guide_name = "李翠"
from_date = "2026-03-01"
to_date = "2026-03-25"

# 执行分析（Skill内部会自动判断门店类型）
result = analyze(
    store_id=store_id,
    guide_name=guide_name,
    from_date=from_date,
    to_date=to_date
)

# 输出结果
print(f"分析状态: {result['status']}")
print(f"导购: {result['guide_name']}")
print(f"销售额: ¥{result['core_metrics']['sales']['amount']:,.0f}")
```

### 步骤3：解读结果

#### 普通门店输出
```json
{
  "status": "ok",
  "store_id": "...",
  "guide_name": "...",
  "analysis_period": {"from": "...", "to": "..."},
  "core_metrics": {...},        // 核心业绩指标
  "radar_analysis": {...},      // 雷达图对比
  "feature_analysis": {...},    // 商品特征分析
  "sku_analysis": {...},        // Top5 SKU爆品分析
  "order_analysis": {...},      // 订单结构分析
  "trend_analysis": {...},      // 14天趋势分析
  "aiot_analysis": {"is_aiot_store": false},  // 非AIoT门店
  "funnel_analysis": {"is_aiot_store": false}, // 非AIoT门店
  "findings": [...],            // 诊断发现
  "recommendations": [...]      // 行动建议
}
```

#### AIoT门店输出
```json
{
  "status": "ok",
  "store_id": "...",
  "guide_name": "...",
  "analysis_period": {"from": "...", "to": "..."},
  "core_metrics": {...},        // 核心业绩指标
  "radar_analysis": {...},      // 雷达图对比
  "feature_analysis": {...},    // 商品特征分析
  "sku_analysis": {...},        // Top5 SKU爆品分析
  "order_analysis": {...},      // 订单结构分析
  "trend_analysis": {...},      // 14天趋势分析
  "aiot_analysis": {            // AIoT专属：高试用低转化
    "is_aiot_store": true,
    "item_count": 5,
    "total_trials": 14,
    "items": [...]
  },
  "funnel_analysis": {          // AIoT专属：客户漏斗
    "is_aiot_store": true,
    "effective_customers": 42,
    "deal_customers": 42,
    "conversion_rate": 100.0,
    "badge_not_worn": true,     // 是否佩戴工牌
    "funnel": {...}
  },
  "findings": [...],            // 诊断发现（含AIoT专属）
  "recommendations": [...]      // 行动建议（含AIoT专属）
}
```

## 分析维度详解

### 1. 核心业绩指标（所有门店）

| 指标 | 说明 | 用途 |
|------|------|------|
| 销售额 | 销售总额 | 业绩规模评估 |
| 业绩排名 | 门店内排名 | 相对位置判断 |
| 业绩占比 | 占门店总业绩比例 | 贡献度评估 |
| 订单数 | 有效订单数 | 成交频次 |
| 客单价 | 平均客单价 | 单笔价值 |
| 连带率 | 数量连带率 | 连带销售能力 |
| 新客数 | 新增会员数 | 客户开发能力 |
| 人效值 | 日均业绩贡献 | 效率评估 |
| 有订单天数 | 统计周期内有成交的天数 | 出勤/活跃度 |

### 2. 雷达图能力对比（所有门店）

6维能力对比（导购 vs 门店平均）：
- 销售额
- 订单数
- 新客数
- 客单价
- 件单价
- 连带率

### 3. 商品特征分析（所有门店）

- **品类偏好**: 主营品类及占比
- **价格带分布**: 主销价格带、高客单占比（≥800元）
- **包型偏好**: 主销包型分析
- **颜色偏好**: 主销颜色分析
- **新品销售**: 2026年新品销售占比

### 4. 爆品分析 Top5 SKU（所有门店）

- **Top5 SKU列表**: 销售额排名前五的商品明细
- **销量分析**: 各SKU销量、销售额、成交均价
- **门店贡献率**: 导购该SKU销售额占门店该SKU总销售的比例
- **SPU集中度**: 按商品名称聚合，分析款式集中度
- **上市时间偏好**: 分析导购对新品/老品的销售偏好
- **新品识别**: 成交时上市时间≤3个月的商品

### 5. 订单结构分析（所有门店）

- **折扣结构**: 主销折扣区间、低折扣订单占比（6折以下）
- **连带结构**: 1件单占比、多连带占比（≥3件）、平均连带
- **会员结构**: 老会员/新会员/非会员销售占比

### 6. 14天销售趋势（所有门店）

- **日度销售追踪**: 近14天每日销售额、订单数、客单价、业绩占比
- **销售连续性**: 有销售天数 vs 无销售天数
- **峰值识别**: 销售最高/最低的日期
- **近期趋势**: 近7天详细数据

### 7. 高试用低转化分析（仅AIoT门店）

- **高试用低转化商品识别**: 试用次数多但成交为0的商品
- **转化能力评估**: 分析导购的试用后跟进转化能力
- **重点商品关注**: Top3高试用低转化商品详情

### 8. 客户漏斗分析（仅AIoT门店）

- **客户分层漏斗**: 有效客户→普通→潜在→意向→成交的转化路径
- **环比趋势分析**: 与上期对比的客户量变化
- **工牌佩戴检测**: 识别导购是否佩戴电子工牌

**重要说明：**
- 导购**未佩戴电子工牌**时，只能记录成交客户（通过订单系统关联），无法获取试用行为数据
- 此时所有有效客户都显示为"成交客户"，这是**正常情况**，不是数据质量问题
- 成交客户数 ≤ 订单数（部分成交可能未在店内发生行为）

## 诊断规则

### 通用诊断（所有门店）

| 问题 | 判断条件 | 严重程度 |
|------|----------|----------|
| 业绩排名靠后 | 排名 > 3 | 🟡 中 |
| 新客获取能力不足 | 新客数 < 门店平均70% | 🟡 中 |
| 新客获取能力突出 | 新客数 > 门店平均150% | 🟢 低（优势）|
| 客单价偏低 | 客单价 < 门店平均85% | 🟡 中 |
| 品类过于集中 | 单一品类占比 > 70% | 🟡 中 |
| 高客单销售弱 | 800元以上占比 < 30% | 🟡 中 |
| 连带销售能力不足 | 1件单占比 > 60% | 🟡 中 |
| 低折扣订单占比过高 | 6折以下订单 > 20% | 🟡 中 |
| 无销售天数过多 | 14天中≥5天无销售 | 🟡 中 |
| 日均销售额偏低 | 日均 < ¥1000 | 🟡 中 |

### AIoT专属诊断（仅AIoT门店）

| 问题 | 判断条件 | 严重程度 |
|------|----------|----------|
| 导购AIoT信息未维护 | 客户漏斗全为0 | 🟡 中 |
| 高试用低转化商品多 | ≥3个高试用低转化商品 | 🟡 中 |
| 有效客户大幅下降 | 环比下降>20% | 🔴 高 |

**边界情况处理：**

当导购信息未在AIoT系统维护时：
- `customer-funnel` 返回全0数据
- `high-trial-low-conversion` 返回**门店整体**数据
- Skill会自动识别并生成诊断："导购 'XXX' AIoT信息未维护"
- 建议：联系门店管理员维护导购信息

## 版本
v3.0.0 - 导购个人业绩深度分析（完整版，支持普通门店和AIoT门店）
