# eBay Product Research - eBay 选品工具

📦 数据驱动，选品无忧

## 核心功能

| 功能 | 说明 | 价值 |
|------|------|------|
| 销量分析 | 估算月销量 | 判断市场需求 |
| 竞争评估 | 卖家数量、Listing 质量 | 避开红海 |
| 利润计算 | 售价 - 成本 - 费用 | 确保盈利 |
| 价格趋势 | 历史价格波动 | 把握入场时机 |
| 季节性 | 淡旺季分析 | 规划库存 |

## 利润计算公式

```
毛利润 = 售价 - 采购成本 - 头程运费
eBay 费用 = 成交费 (10-12%) + 支付处理费 (2.9%+$0.30)
净利润 = 毛利润 - eBay 费用 - 广告费
```

## 定价

- **单次使用**: ¥8
- **套餐**: 10 次¥70（省¥10）
- **免费试用**: 前 1 次免费

## 示例

```bash
# 研究产品
/ebay-product-research --category electronics --keyword "wireless earbuds"

# 竞品分析
/ebay-product-research --action competitor --seller "top_seller"

# 利润计算
/ebay-product-research --action profit --price 25 --cost 8
```

## 选品标准

✅ 月销量 > 300
✅ 竞争卖家 < 50
✅ 利润率 > 30%
✅ 无品牌垄断
✅ 非季节性/全年可售

---
**SkillPay 收费 Skill** | 版本 1.0.0
