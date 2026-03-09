# amazon-price-tracker - 亚马逊价格追踪

## 描述
实时监控亚马逊商品价格，设置降价提醒，追踪历史价格曲线。帮助买家低价购入，卖家竞品监控。

## 定价
- **包月订阅**: ¥29/月
- 最多追踪 50 个商品
- 包含历史价格分析和降价提醒

## 用法
```bash
# 添加追踪商品
/amazon-price-tracker --add <product_url> --target-price 99

# 查看追踪列表
/amazon-price-tracker --list

# 查看价格历史
/amazon-price-tracker --history <product_url>

# 设置提醒
/amazon-price-tracker --alert --email user@example.com
```

## 技能目录
`~/.openclaw/workspace/skills/amazon-price-tracker/`

## 作者
张 sir

## 版本
1.0.0
