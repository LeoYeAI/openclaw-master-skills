# 达人 (Influencer)

TikTok 达人数据模块，包括多维度达人搜索、各类达人榜单、以及单个达人的全部详情子接口。

---

## 搜索与榜单

### 1. 达人搜索

```
GET /api/open/influencers/search
```

多维度搜索 TikTok 达人，支持粉丝数、带货数据、互动率、联系方式等 18+ 筛选条件。上游接口：`/api/author/search`。

> **注意**：值为 `None`、空字符串或 `"-1"` 的参数不会传给上游。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "12,2" | 排序规则（12=综合排序） |
| `words` | str | 否 | - | 搜索关键词（达人昵称/简介） |
| `shop_window` | str | 否 | - | 橱窗商品数范围 |
| `follower` | str | 否 | - | 粉丝数范围，格式 `"min,max"` |
| `cid` | str | 否 | - | 带货品类 ID |
| `product` | str | 否 | - | 带货商品数范围 |
| `is_shop` | str | 否 | - | 是否拥有 TikTok Shop 店铺 |
| `verify` | str | 否 | - | 是否蓝V认证 |
| `gender` | str | 否 | - | 性别筛选 |
| `age` | str | 否 | - | 年龄段筛选 |
| `contact` | str | 否 | - | 是否公开联系方式 |
| `has_partner` | str | 否 | - | 是否签约 MCN 机构 |
| `follower_28d_count` | str | 否 | - | 近28天涨粉数范围 |
| `sale_28d_count` | str | 否 | - | 近28天带货销量范围 |
| `prod_video_28d_count` | str | 否 | - | 近28天发布带货视频数范围 |
| `prod_live_28d_count` | str | 否 | - | 近28天开播带货直播数范围 |
| `avg_28d_play_count` | str | 否 | - | 近28天场均播放量范围 |
| `avg_28d_sale_play_count` | str | 否 | - | 近28天带货视频场均播放量范围 |
| `interaction_v1_rate` | str | 否 | - | 互动率范围 |
| `like_followers_v1_rate` | str | 否 | - | 点赞粉丝比范围 |
| `first_video_time` | str | 否 | - | 首发视频时间范围 |

---

### 2. 达人榜

```
GET /api/open/influencers/rank
```

达人排行榜，支持涨粉榜、蓝V榜、热门榜三种类型。上游接口：`/api/followers/followersList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
| `type` | int | 否 | 1 | 榜单类型：`1`=涨粉榜、`2`=蓝V榜、`3`=热门榜 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `date_type` | int | 否 | - | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `cid` | str | 否 | - | 品类 ID |

---

### 3. 带货达人榜

```
GET /api/open/influencers/commerce-rank
```

按带货销售额/销量排名的达人榜单。上游接口：`/api/ecommerce/rank`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
| `order` | str | 否 | "1,2" | 排序规则 |
| `date_type` | int | 否 | 1 | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `cid` | str | 否 | - | 品类 ID |

---

### 4. 黑马达人榜

```
GET /api/open/influencers/dark-horse
```

近期增长迅速的潜力达人排行（黑马榜）。上游接口：`/api/author/potential/rank`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `page` | int | 否 | 1 | 页码，≥1 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 50 |
| `region` | str | 否 | US | 目标市场 |
| `date_type` | int | 否 | 1 | 时间维度类型 |
| `date_value` | str | 否 | - | 具体时间值 |
| `is_ecommerce` | int | 否 | 1 | 是否仅带货达人：`1`=是 |
| `order` | str | 否 | - | 排序规则 |
| `follower` | str | 否 | - | 粉丝数范围 |
| `gender` | str | 否 | - | 性别筛选 |
| `age` | str | 否 | - | 年龄段筛选 |
| `cid` | str | 否 | - | 品类 ID |

---

## 达人详情

以下接口均需要 `uid`（达人 UID）作为必填参数。

### 5. 达人综合详情

```
GET /api/open/influencers/detail
```

获取达人的全面信息。后端内部并行请求 4 个上游接口并合并返回：
- `/api/author/v3/detail/baseInfo` — 基础资料（昵称、头像、简介、粉丝数等）
- `/api/author/v3/detail/authorIndex` — 达人指数（带货力、影响力等评分）
- `/api/author/v3/detail/getStatInfo` — 数据统计（视频数、直播数、商品数等）
- `/api/author/v3/detail/authorContact` — 联系方式（可能为空）

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `region` | str | 否 | US | 目标市场 |

**响应结构**（由后端组装）：
```json
{
  "code": 200,
  "data": {
    "base": { /* 基础资料 */ },
    "index": { /* 达人指数评分 */ },
    "stat": { /* 数据统计 */ },
    "contact": { /* 联系方式，获取失败时为空对象 */ }
  }
}
```

---

### 6. 数据趋势图

```
GET /api/open/influencers/detail/chart
```

获取达人某项数据指标在时间范围内的逐日变化趋势。上游接口：`/api/author/v3/detail/dataList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `field_type` | str | 否 | "follower" | 数据指标类型，可选：`follower`（粉丝）、`play`（播放）、`digg`（点赞）等 |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `region` | str | 否 | US | 目标市场 |

---

### 7. 粉丝画像

```
GET /api/open/influencers/detail/fans-portrait
```

获取达人粉丝的人口统计画像（性别、年龄、地域分布等）。上游接口：`/api/author/v3/detail/fansPortrait`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `region` | str | 否 | US | 目标市场 |

---

### 8. 达人视频列表

```
GET /api/open/influencers/detail/videos
```

获取达人发布的视频列表，可按播放量、点赞数等排序。上游接口：`/api/author/v3/detail/videoList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 20 |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `order` | str | 否 | "play_count,2" | 排序字段。可选：`play_count`（播放量）、`digg_count`（点赞数）、`create_time`（发布时间），方向 `2`=降序 |
| `region` | str | 否 | US | 目标市场 |

---

### 9. 达人商品列表

```
GET /api/open/influencers/detail/goods
```

获取达人带货的商品列表。上游接口：`/api/author/v3/detail/goodsList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 20 |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `order` | str | 否 | "sold_count,2" | 排序字段，`sold_count`=销量降序 |
| `region` | str | 否 | US | 目标市场 |

---

### 10. 达人直播列表

```
GET /api/open/influencers/detail/live
```

获取达人的直播记录列表。上游接口：`/api/author/v3/detail/liveList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 20 |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `order` | str | 否 | "create_time,2" | 排序字段，`create_time`=最新优先 |
| `region` | str | 否 | US | 目标市场 |

---

### 11. 带货品类分布

```
GET /api/open/influencers/detail/category-list
```

获取达人带货商品的品类分布（各品类占比）。上游接口：`/api/author/v3/detail/categoryList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `region` | str | 否 | US | 目标市场 |

---

### 12. 活跃时段分析

```
GET /api/open/influencers/detail/active-range
```

获取达人的发布/活跃时段分布（一周内按小时统计）。上游接口：`/api/author/v3/detail/authorActiveRange`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `date_type` | int | 否 | 28 | 时间范围天数 |
| `region` | str | 否 | US | 目标市场 |

---

### 13. 相似达人

```
GET /api/open/influencers/detail/similarity
```

获取与指定达人风格/品类相似的其他达人列表。上游接口：`/api/author/v3/detail/similarityList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `page` | int | 否 | 1 | 页码 |
| `pagesize` | int | 否 | 10 | 每页条数，最大 20 |
| `region` | str | 否 | US | 目标市场 |

---

### 14. 粉丝活跃分析

```
GET /api/open/influencers/detail/fans-analysis
```

获取达人粉丝的活跃度分析数据。上游接口：`/api/author/v3/detail/authorFansAnalysis`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `region` | str | 否 | US | 目标市场 |

---

### 15. 带货总览

```
GET /api/open/influencers/detail/cargo-summary
```

获取达人的带货业绩总览（总销量、总销售额、平均客单价等汇总数据）。上游接口：`/api/author/v3/detail/cargoSummary`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `region` | str | 否 | US | 目标市场 |

---

### 16. 常用标签

```
GET /api/open/influencers/detail/labels
```

获取达人视频中常用的话题标签列表。上游接口：`/api/author/v3/detail/labelList`。

**参数：**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `uid` | str | ✅ | - | 达人 UID |
| `region` | str | 否 | US | 目标市场 |
