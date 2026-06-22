# 商品搜索与榜单 (Goods)

商品模块提供 TikTok Shop 商品的多维度搜索和各类排行榜数据。

---

## 1. 商品搜索

```
GET /api/open/goods/search
```

根据关键词、品类、价格、销量等多维度条件搜索 TikTok Shop 商品。上游接口：`/api/goods/V2/search`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 20 |
| `region` | str | 否 | US | 目标市场 |
| `keyword` | str | 否 | - | 搜索关键词（内部映射为上游 `words` 参数） |
| `order` | str | 否 | "2,2" | 排序规则 |
| `l1_cid` | str | 否 | - | 一级品类 ID（通过 `/api/open/goods/filters` 获取） |
| `l2_cid` | str | 否 | - | 二级品类 ID |
| `l3_cid` | str | 否 | - | 三级品类 ID |
| `price_min` | str | 否 | - | 最低价格（美元）。与 `price_max` 组合后内部拼接为 `price_amount=min,max` |
| `price_max` | str | 否 | - | 最高价格（美元），`-1` 表示不限 |
| `sold_count` | str | 否 | - | 总销量范围，格式 `"min,max"` |
| `day7_sold_count` | str | 否 | - | 近7天销量范围 |
| `sale_amount` | str | 否 | - | 总销售额范围 |
| `day7_sale_amount` | str | 否 | - | 近7天销售额范围 |
| `crate` | str | 否 | - | 佣金率范围 |
| `relate_author_count` | str | 否 | - | 关联达人数范围 |
| `author_order_rate` | str | 否 | - | 达人出单率范围 |
| `is_free_shipping` | str | 否 | - | 是否包邮（"1"=是） |
| `is_new` | str | 否 | - | 是否新品 |
| `is_hot_sale` | str | 否 | - | 是否热销 |
| `is_local` | str | 否 | - | 是否本地商品 |
| `is_cross_border` | str | 否 | - | 是否跨境商品 |
| `is_sshop` | str | 否 | - | 是否全托管商品（空字符串不传递） |
| `off_shelves` | str | 否 | - | 是否已下架 |
| `commerce_type` | str | 否 | - | 电商类型筛选 |

> **注意**：`price_min` 和 `price_max` 不是直接传给上游的，后端会将它们合并为 `price_amount="min,max"` 格式传递。如果只传其中一个，缺失的部分默认为 `0`（min）或 `-1`（max）。

---

## 2. 商品筛选条件

```
GET /api/open/goods/filters
```

获取商品搜索可用的筛选条件列表，包括品类树（一级/二级/三级品类 ID 和名称）、价格区间选项等。用于构建搜索筛选 UI 或获取品类 ID。上游接口：`/api/goods/filterInfo`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `region` | str | 否 | US | 目标市场，不同市场品类树不同 |

---

## 3. 销量榜

```
GET /api/open/goods/sale-rank
```

按销量排名的商品榜单。上游接口：`/api/goods/saleRank`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 10 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `date_type` | int | 否 | - | 时间维度类型（如 1=日榜、7=周榜） |
| `date_value` | str | 否 | - | 具体时间值，与 `date_type` 配合使用 |
| `l1_cid` | str | 否 | - | 一级品类 ID |

---

## 4. 新品榜

```
GET /api/open/goods/new-product
```

新上架商品排行榜。上游接口：`/api/goods/newProduct`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 10 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `rank_type` | int | 否 | 11 | 榜单类型，固定为 11 |
| `dt` | str | 否 | - | 日期筛选 |
| `cid` | str | 否 | - | 品类 ID |
| `is_cross_border` | str | 否 | - | 是否跨境商品 |
| `is_sshop` | str | 否 | - | 是否全托管商品 |

---

## 5. 全托管商品榜

```
GET /api/open/goods/managed-rank
```

TikTok Shop 全托管（sShop）模式下的热门商品排行。上游接口：`/api/goods/sShopHotList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 10 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "8,2" | 排序规则（默认按字段8降序） |
| `date_type` | int | 否 | - | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `l1_cid` | str | 否 | - | 一级品类 ID |

---

## 6. 热推榜

```
GET /api/open/goods/hot-rank
```

被大量达人推广的热门商品排行。上游接口：`/api/goods/popRank`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 10 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "4,2" | 排序规则（默认按字段4降序） |
| `date_type` | int | 否 | - | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `l1_cid` | str | 否 | - | 一级品类 ID |
