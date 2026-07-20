# 1688 到 Ozon 商品铺货 SKILL

将 1688 商品快速铺货到俄罗斯电商平台 Ozon 的自动化工具。

更多有趣的电商SKILL，可以通过https://skill.alphashop.cn/获取，安全可靠的企业级别SKILL HUB

## ✨ 核心特性

- 🔄 **类目自动映射** - 1688 类目自动映射到 Ozon 类目
- 📝 **属性智能转换** - AI 智能映射商品属性，自动查询字典值
- 🌐 **图片自动翻译** - 商品图片文字自动翻译为俄语
- 💰 **智能定价** - 支持 RUB/CNY 双币种自动定价
- 🚀 **一键上架** - 自动上传商品并查询上架状态

## 🚀 快速开始

### 1. 配置密钥

**Ozon 密钥** — 存储在配置文件 `~/.openclaw/skillconfig/1688-Product-to-Ozon/ozon_config.json`：

```json
{
  "OZON_API_KEY": "your-api-key",
  "OZON_CLIENT_ID": "your-client-id",
  "OZON_CURRENCY": "CNY"
}
```

**AlphaShop 密钥** — 在 OpenClaw config 中配置：

```json5
{
  skills: {
    entries: {
      "1688-Product-to-Ozon": {
        env: {
          ALPHASHOP_ACCESS_KEY: "YOUR_AK",
          ALPHASHOP_SECRET_KEY: "YOUR_SK"
        }
      }
    }
  }
}
```

### 2. 获取密钥

- **Ozon**: 在 [Ozon 卖家后台](https://seller.ozon.ru/) → API 设置中生成
- **AlphaShop**: 访问 https://www.alphashop.cn/seller-center/apikey-management 申请

### 3. 使用 SKILL

在 Claude Code 中直接说：

```
"帮我把这个1688商品铺货到Ozon"
```

## 🎯 主要功能

### 类目映射

```bash
python scripts/queryCategoryMapping.py <1688类目ID>
```

### 查询 Ozon 类目属性

```bash
python scripts/queryOzonProperties.py <externalCategoryId>
```

### 查询字典属性值

```bash
# 搜索模式
python scripts/queryDictionaryValues.py \
  --attribute_id 85 --description_category_id 17028922 \
  --type_id 91565 --search "Нет бренда"

# 列表模式
python scripts/queryDictionaryValues.py \
  --attribute_id 85 --description_category_id 17028922 \
  --type_id 91565 --limit 50
```

### 图片翻译

```bash
# 翻译单张图片
python scripts/translate_images.py --image-url "<图片URL>"

# 批量翻译
python scripts/translate_images.py --image-url "<URL1>" "<URL2>" "<URL3>"
```

### 商品上架

```bash
python scripts/upload_product.py --product-data tmp/my_products.json
```

### 查询上架结果

```bash
python scripts/check_status.py <task_id>
```

## 📁 项目结构

```
1688-Product-to-Ozon/
├── SKILL.md                          # SKILL 配置文件
├── README.md                         # 本文档
├── requirements.txt                  # Python 依赖
├── references/
│   └── offer_description.json        # 商品详情描述模板
├── scripts/
│   ├── queryCategoryMapping.py       # 1688→Ozon 类目映射
│   ├── queryOzonProperties.py        # Ozon 类目属性查询
│   ├── queryDictionaryValues.py      # 字典属性值查询
│   ├── translate_images.py           # 图片翻译（单张/批量）
│   ├── batch_translate.py            # 批量翻译工具
│   ├── upload_product.py             # 商品上传到 Ozon
│   ├── check_status.py              # 查询上传状态
│   └── check_upload_status.py        # 上传状态检查
└── tmp/                              # 临时文件目录
    └── my_products.json              # 商品数据存储
```

## 📝 注意事项

1. **币种匹配** - `OZON_CURRENCY` 必须与 Ozon 卖家后台设置的币种一致，否则 API 会报错
2. **图片翻译** - 所有商品图片（主图 + SKU图）都必须翻译为俄语后再上传
3. **字典值** - 不要手写 `dictionary_value_id`，必须通过脚本查询获取
4. **定价规则** - 默认使用 SKU 价格 × 3（RUB 还需乘汇率）
5. **品牌属性** - 固定使用 "Нет бренда"（dictionary_value_id: 126745801）
6. **AlphaShop 欠费** - 如返回欠费错误，需前往 https://www.alphashop.cn/seller-center/home/api-list 购买积分

## 📄 License

MIT

## 👤 作者

红淼

---

**最后更新**: 2026-03-19
