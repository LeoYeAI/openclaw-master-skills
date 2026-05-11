# App Distribution API / 应用投放分布接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

> These endpoints require a `unified_product_id`. Get it from `unified-product-search` first.

---

## 1. App Distribution — 应用推广分布

`POST /api/data/app-distribution`

Analyze an app's ad distribution across different dimensions.

### Request Body

```json
{
  "unified_product_id": "xxx",
  "dim": "country",
  "start_time": "",
  "end_time": "",
  "countries": [],
  "media_ids": [],
  "material_type": "",
  "index_type": 0
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| unified_product_id | string | required | Target app ID |
| dim | string | required | Distribution dimension (see below) |
| start_time | string | 30 days ago | YYYY-MM-DD |
| end_time | string | today | YYYY-MM-DD |
| countries | string[] | [] | Country filter |
| media_ids | string[] | [] | Media channel filter |
| material_type | string/int | "" | Material type filter |
| index_type | int | 0 | Index type selector |

### Dimensions

| dim | Description | Returns |
|---|---|---|
| `trend` | 投放趋势 | Time series of ad volume over time |
| `country` | 投放国家分布 | Per-country ad placement distribution |
| `media` | 投放媒体位分布 | Distribution across publisher apps/placements where ads are displayed. **Note:** This returns the specific apps where ads appear (e.g. "Block Blast", "Snake.io", "Solitaire"), NOT ad network names like Facebook/Google. These are the traffic sources/publisher apps carrying the ads. Present them as "投放媒体位" or "广告展示位". |
| `platform` | 平台分布 | iOS vs Android breakdown |
| `type` | 素材类型分布 | Image vs video vs playable distribution |
| `image` | 图片尺寸分布 | Image size/aspect ratio breakdown |
| `video` | 视频时长分布 | Video duration breakdown |
| `lang` | 语言分布 | Ad language distribution |

### Response Examples

**dim=country:**
```json
{
  "list": [
    {"code": "US", "name": "United States", "cnt": 500, "ratio": 0.35},
    {"code": "JP", "name": "Japan", "cnt": 300, "ratio": 0.21}
  ]
}
```

**dim=trend:**
```json
{
  "list": [
    {"date": "2026-03-01", "cnt": 50},
    {"date": "2026-03-02", "cnt": 65}
  ]
}
```

**dim=media (publisher apps / ad placements):**
```json
{
  "list": [
    {"id": "101", "name": "Block Blast Adventure Master", "cnt": 400, "ratio": 0.15},
    {"id": "102", "name": "Snake.io", "cnt": 250, "ratio": 0.09},
    {"id": "103", "name": "Solitaire", "cnt": 180, "ratio": 0.07}
  ]
}
```
These are the apps where the target app's ads are being shown (publisher side). When presenting this data, you can categorize them (e.g. casual games, tools, content apps) to provide more actionable insights.

---

## 2. Distribute Dims — 素材分布维度

`GET /api/data/distribute-dims`

Returns which distribute dimensions are available per content type. This is for the creative-level distribute endpoint (`/api/data/distribute`), not for app-distribution.

### Response

```json
{
  "creative": ["media", "advertiser", "app"],
  "imagevideo": ["media", "advertiser", "app", "country"],
  "preplay": ["media", "advertiser", "app"],
  "demoad": ["media", "advertiser", "app"],
  "document": ["media", "advertiser", "app"]
}
```

---

## 3. Global Promote — 全局推广分布

`POST /api/data/global-promote`

Analyze the global promotion distribution for one or more products across countries, media, or advertisers.

### Request Body

```json
{
  "ids": ["product_id_1", "product_id_2"],
  "dim": "country",
  "keyword": "",
  "sort_field": "15",
  "sort_rule": "desc"
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| ids | string[] | required | Product IDs (non-empty array) |
| dim | string | "country" | Dimension: `country`, `media`, or `adfaction` |
| keyword | string | "" | Optional keyword filter |
| sort_field | string | "15" | Sort field ("15"=impressions) |
| sort_rule | string | "desc" | Sort direction |

### Response

Returns distribution data for the specified dimension. Structure varies by `dim`.

### Difference from app-distribution

- **app-distribution** — Analyzes a single app's ad placement distribution (where/how it advertises)
- **global-promote** — Analyzes one or more products' promotion footprint across the global market (country/media/advertiser breakdown)

---

## Common Workflows / 常用工作流

### "Temu 主要在哪些国家投广告？"

```
app-distribution(unified_product_id=id, dim="country")
```

### "Temu 用了哪些广告渠道？"

```
app-distribution(unified_product_id=id, dim="media")
```

### "Temu 的投放趋势怎么样？"

```
app-distribution(unified_product_id=id, dim="trend", start_time="2026-01-01", end_time="2026-03-16")
```

### "Temu 在美国投了多少视频广告 vs 图片广告？"

```
app-distribution(unified_product_id=id, dim="type", countries=["US"])
```

### Full app advertising profile (multi-call)

1. `dim="country"` → where they advertise (target countries)
2. `dim="media"` → which publisher apps carry their ads (ad placements)
3. `dim="type"` → what creative formats they use
4. `dim="trend"` → how ad volume changes over time
5. `dim="lang"` → which languages they target

Combine all 5 for a comprehensive advertising strategy overview.
