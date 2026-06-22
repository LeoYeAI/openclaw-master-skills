# 店铺 (Shop)

TikTok Shop 店铺数据模块，提供店铺搜索、详情、商品列表、关联达人等。

---

## 1. 店铺筛选条件

```
GET /api/open/shops/filter-info
```

获取店铺搜索可用的筛选条件（品类、店铺类型等选项列表）。上游接口：`/api/shop/filterInfo`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `region` | str | 否 | US | 目标市场 |

---

## 2. 店铺搜索

```
GET /api/open/shops/search
```

多条件搜索 TikTok Shop 店铺。上游接口：`/api/shop/V3/search`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 20 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `words` | str | 否 | - | 搜索关键词（店铺名称） |
| `cid` | str | 否 | - | 品类 ID |
| `is_sshop` | str | 否 | - | 是否全托管店铺（空字符串不传递） |
| `shop_type` | str | 否 | - | 店铺类型 |
| `shop_position` | str | 否 | - | 店铺所在地 |
| `date_type` | int | 否 | - | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `sold_count` | str | 否 | - | 销量范围 |
| `sale_amount` | str | 否 | - | 销售额范围 |
| `author_count` | str | 否 | - | 关联达人数范围 |
| `rating` | str | 否 | - | 店铺评分范围 |

---

## 3. 店铺详情

```
GET /api/open/shops/detail
```

获取单个店铺的基础详情信息。上游接口：`/api/shop/V3/base`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | str | ✅ | - | 店铺 ID |
| `region` | str | 否 | US | 目标市场 |

---

## 4. 店铺商品列表

```
GET /api/open/shops/products
```

获取指定店铺内的商品列表。上游接口：`/api/shop/V3/goods`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `id` | str | ✅ | - | 店铺 ID |
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 20 | 每页条数，最大 50 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `region` | str | 否 | US | 目标市场 |

---

## 5. 店铺关联达人

```
GET /api/open/shops/authors
```

获取与指定店铺有合作关系的达人列表。上游接口：`/api/shop/V3/author`。

> **注意**：此接口使用 `seller_id` 参数（非 `id`），与其他店铺接口不同。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `seller_id` | str | ✅ | - | 卖家 ID（注意：不是店铺 ID `id`） |
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 20 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
