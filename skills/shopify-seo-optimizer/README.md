# Shopify SEO Optimizer - Shopify SEO 优化

🛍️ 提升店铺自然流量

## 优化清单

### 产品页
| 元素 | 优化要点 |
|------|---------|
| 标题 | 品牌 + 核心词 + 属性 (60 字符内) |
| 描述 | 独特内容，包含关键词，200+ 字 |
| 图片 | 压缩 + 描述性 Alt 文本 |
| URL | /products/关键词 - 产品名 |
| 价格 | 结构化数据标记 |

### 集合页
| 元素 | 优化要点 |
|------|---------|
| 标题 | 集合名 + 核心词 |
| 描述 | 150-160 字符，吸引点击 |
| 内容 | 集合顶部/底部添加描述文本 |

## Shopify SEO 最佳实践

```liquid
<!-- 产品页标题模板 -->
{{ product.title }} | {{ shop.name }}

<!-- 元描述 -->
<meta name="description" content="{{ product.description | strip_html | truncate: 160 }}">

<!-- 图片 Alt -->
<img src="{{ image.src }}" alt="{{ image.alt | default: product.title }}">
```

## 定价

- **单次优化**: ¥10
- **批量优化**: ¥80/10 个产品
- **全店审计**: ¥50
- **免费试用**: 前 1 次免费

## 示例

```bash
# 优化产品
/shopify-seo-optimizer --type product --handle "wireless-earbuds" --keyword "蓝牙耳机"

# 批量优化
/shopify-seo-optimizer --action bulk --type products --limit 50

# SEO 审计
/shopify-seo-optimizer --action audit --url "mystore.myshopify.com"
```

---
**SkillPay 收费 Skill** | 版本 1.0.0
