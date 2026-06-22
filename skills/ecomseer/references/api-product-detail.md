# 商品详情 (Product Detail)

根据商品 ID 获取单个商品的各维度详细数据，包括基础信息、销售趋势、带货视频/达人、评价、直播等。

---

## 1. 商品基础信息

```
GET /api/open/goods/detail
```

获取单个商品的基础信息，包括标题、价格、图片、品类、店铺等。上游接口：`/api/goods/v3/base`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `region` | str | 否 | US | 目标市场 |

---

## 2. 销售趋势概览

```
GET /api/open/product/overview
```

获取商品在指定时间范围内的销售趋势数据（销量、销售额、关联达人数等）。上游接口：`/api/goods/v3/overview`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `d_type` | int | 否 | 28 | 时间范围天数，可选 7、28、90 |
| `region` | str | 否 | US | 目标市场 |

---

## 3. 带货视频列表

```
GET /api/open/product/videos
```

获取推广该商品的视频列表。上游接口：`/api/goods/v3/video`。

> **内部固定参数**：`d_type=0`、`is_promoted=-1`（表示不限推广类型），调用方无需传递。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 5 | 每页条数，最大 10 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `date_type` | int | 否 | 28 | 时间范围（7/28/90天） |
| `region` | str | 否 | US | 目标市场 |

---

## 4. 带货达人列表

```
GET /api/open/product/authors
```

获取推广该商品的达人列表。上游接口：`/api/goods/v3/author`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 5 | 每页条数，最大 10 |
| `order` | str | 否 | "2,2" | 排序规则 |
| `ecommerce_type` | str | 否 | "all" | 电商类型筛选，`all` 表示全部 |
| `region` | str | 否 | US | 目标市场 |

---

## 5. 商品评价

```
GET /api/open/product/reviews
```

获取商品的用户评价列表。上游接口：`/api/goods/reviewList`。

> **内部固定参数**：`near_day=0`（不限时间）、`is_like=0`（不筛选好评）。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 5 | 每页条数，最大 10 |
| `region` | str | 否 | US | 目标市场 |

---

## 6. 直播带货列表

```
GET /api/open/product/live
```

获取通过直播带货推广该商品的直播间列表。上游接口：`/api/goods/v3/live`。

> **内部固定参数**：`live_type="all"`（不筛选直播类型）。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `product_id` | str | ✅ | - | 商品 ID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 5 | 每页条数，最大 10 |
| `d_type` | int | 否 | 28 | 时间范围天数 |
| `order` | str | 否 | "2,2" | 排序规则 |
| `region` | str | 否 | US | 目标市场 |
