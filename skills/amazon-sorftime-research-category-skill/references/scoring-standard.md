# 五维评分模型标准

**版本**: v1.0
**最后更新**: 2026-03-04
**状态**: ✅ 正式版本

---

## 评分维度总览

| 维度 | 分值 | 评估指标 | 数据字段 |
|------|------|----------|----------|
| 市场规模 | 20 分 | Top100 月销额 | `top100产品月销额` |
| 增长潜力 | 25 分 | 低评论产品销量占比 | `low_reviews_sales_volume_share` |
| 竞争烈度 | 20 分 | Top3 品牌销量占比 | `top3_brands_sales_volume_share` |
| 进入壁垒 | 20 分 | Amazon 自营 + 新品机会 | `amazonOwned_sales_volume_share` + `low_reviews_sales_volume_share` |
| 利润空间 | 15 分 | 平均价格 | `average_price` |
| **总分** | **100 分** | | |

---

## 1. 市场规模 (20 分)

**评估指标**: `top100产品月销额` (Top100 产品月销额)

| 销额范围 | 得分 |
|----------|------|
| > $10,000,000 | 20 |
| > $5,000,000 | 17 |
| > $1,000,000 | 14 |
| 其他 | 10 |

**Python 代码**:
```python
revenue = float(stats.get('top100产品月销额', 0))
if revenue > 10_000_000:
    market_size_score = 20
elif revenue > 5_000_000:
    market_size_score = 17
elif revenue > 1_000_000:
    market_size_score = 14
else:
    market_size_score = 10
```

---

## 2. 增长潜力 (25 分)

**评估指标**: `low_reviews_sales_volume_share` (低评论产品销量占比，即评价数<300的产品)

| 占比范围 | 得分 | 说明 |
|----------|------|------|
| > 40% | 22 | 新品空间大 |
| > 20% | 18 | 新品有机会 |
| 其他 | 14 | 新品空间有限 |

**Python 代码**:
```python
low_review_share = float(stats.get('low_reviews_sales_volume_share', 0))
if low_review_share > 40:
    growth_score = 22
elif low_review_share > 20:
    growth_score = 18
else:
    growth_score = 14
```

---

## 3. 竞争烈度 (20 分)

**评估指标**: `top3_brands_sales_volume_share` (Top3 品牌销量占比)

| 占比范围 | 得分 | 竞争程度 |
|----------|------|----------|
| < 30% | 18 | 低度集中，机会大 |
| < 50% | 14 | 中度集中 |
| 其他 | 8 | 高度集中，竞争激烈 |

**Python 代码**:
```python
top3_share = float(stats.get('top3_brands_sales_volume_share', 0))
if top3_share < 30:
    competition_score = 18
elif top3_share < 50:
    competition_score = 14
else:
    competition_score = 8
```

---

## 4. 进入壁垒 (20 分)

**评估指标**:
- `amazonOwned_sales_volume_share` (Amazon 自营占比)
- `low_reviews_sales_volume_share` (新品机会)

**评分逻辑**: Amazon 占比越低 + 新品机会越大 = 壁垒越低

### Amazon 自营影响 (0-10 分)

| 占比范围 | 得分 |
|----------|------|
| < 20% | 10 | 挤压小 |
| < 40% | 6 | 中等挤压 |
| 其他 | 3 | 挤压大 |

### 新品机会影响 (0-10 分)

| 占比范围 | 得分 |
|----------|------|
| > 40% | 10 | 机会大 |
| > 20% | 6 | 有机会 |
| 其他 | 3 | 机会小 |

### 总分计算

`进入壁垒得分 = Amazon 自营得分 + 新品机会得分`

**范围**: 6-20 分

**Python 代码**:
```python
amazon_share = float(stats.get('amazonOwned_sales_volume_share', 0))
low_review_share = float(stats.get('low_reviews_sales_volume_share', 0))

barrier_score = 0

# Amazon 占影响分
if amazon_share < 20:
    barrier_score += 10
elif amazon_share < 40:
    barrier_score += 6
else:
    barrier_score += 3

# 新品机会得分
if low_review_share > 40:
    barrier_score += 10
elif low_review_share > 20:
    barrier_score += 6
else:
    barrier_score += 3
```

---

## 5. 利润空间 (15 分)

**评估指标**: `average_price` (平均价格)

| 价格范围 | 得分 |
|----------|------|
| > $300 | 12 |
| > $150 | 10 |
| > $50 | 7 |
| 其他 | 4 |

**Python 代码**:
```python
avg_price = float(stats.get('average_price', 0))
if avg_price > 300:
    profit_score = 12
elif avg_price > 150:
    profit_score = 10
elif avg_price > 50:
    profit_score = 7
else:
    profit_score = 4
```

---

## 评级判定

| 总分范围 | 评级 | 建议 |
|----------|------|------|
| 80 - 100 | 优秀 | 强烈推荐进入 |
| 70 - 79 | 良好 | 可以考虑进入 |
| 50 - 69 | 一般 | 谨慎进入 |
| 0 - 49 | 较差 | 不建议进入 |

---

## 字段名称映射表

| 中文名称 | 英文键名 | 数据来源 |
|----------|----------|----------|
| Top100 产品月销额 | `top100产品月销额` | category_report |
| Top100 产品月销量 | `top100产品月销量` | category_report |
| 平均价格 | `average_price` | category_report |
| 中位数价格 | `median_price` | category_report |
| Top3 品牌销量占比 | `top3_brands_sales_volume_share` | category_report |
| Amazon 自营占比 | `amazonOwned_sales_volume_share` | category_report |
| 高评分产品占比 | `high_rated_sales_volume_share` | category_report |
| 低评论产品占比 | `low_reviews_sales_volume_share` | category_report |

---

## 实现文件清单

以下文件应使用本标准:

| 文件 | 状态 | 备注 |
|------|------|------|
| `scripts/data_utils.py` | ✅ 已修复 | calculate_five_dimension_score() |
| `scripts/parse_sorftime_sse.py` | ✅ 正确 | calculate_scores() |
| `scripts/sse_decoder.py` | ✅ 已添加 | calculate_five_dimension_score() |
| `SKILL.md` | ✅ 正确 | 文档说明 |

---

## 测试用例

### 测试案例 1: Sofas 品类 (美国)

```python
stats = {
    'top100产品月销额': 24869166.89,  # $24.87M
    'low_reviews_sales_volume_share': 52.99,  # 52.99%
    'top3_brands_sales_volume_share': 19.49,  # 19.49%
    'amazonOwned_sales_volume_share': 6.37,  # 6.37%
    'average_price': 323.75
}

# 预期得分:
# 市场规模: 20 (>$10M)
# 增长潜力: 22 (>40%)
# 竞争烈度: 18 (<30%)
# 进入壁垒: 20 (10 + 10)
# 利润空间: 12 (>$300)
# 总分: 92/100 → 优秀
```

### 测试案例 2: 小品类

```python
stats = {
    'top100产品月销额': 800000,  # $0.8M
    'low_reviews_sales_volume_share': 15,  # 15%
    'top3_brands_sales_volume_share': 55,  # 55%
    'amazonOwned_sales_volume_share': 45,  # 45%
    'average_price': 35
}

# 预期得分:
# 市场规模: 10 (<$1M)
# 增长潜力: 14 (<20%)
# 竞争烈度: 8 (>50%)
# 进入壁垒: 6 (3 + 3)
# 利润空间: 4 (<$50)
# 总分: 42/100 → 较差
```

---

*本文档由 Claude Code 维护 | 如有修改请同步更新所有实现文件*
