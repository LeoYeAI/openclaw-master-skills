# Download & Revenue API / 下载量与收入接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

> These endpoints require a `unified_product_id`. Get it from `unified-product-search` first.

---

## 1. Download Date Range — 下载量可用日期

`GET /api/data/download-date`

Returns the available date range for download data queries.

### Response

```json
{
  "startDate": "2023-01-01",
  "endDate": "2026-03-15"
}
```

**Use this to validate date params before calling download-detail/download-country.**

---

## 2. Download Detail — 下载量趋势

`POST /api/data/download-detail`

Fetch download trend data for a specific app over time.

### Request Body

```json
{
  "unified_product_id": "xxx",
  "query_start_date": "2026-02-14",
  "query_end_date": "2026-03-16",
  "compare_start_date": "",
  "compare_end_date": "",
  "country_st": [],
  "day_type": 1,
  "flag": true,
  "is_all": false
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| unified_product_id | string | required | Target app ID |
| query_start_date | string | required | YYYY-MM-DD |
| query_end_date | string | required | YYYY-MM-DD |
| compare_start_date | string | "" | Compare period start (optional) |
| compare_end_date | string | "" | Compare period end (optional) |
| country_st | string[] | [] | Country filter (empty = global) |
| day_type | int | 1 | Granularity: 1=daily, 2=weekly, 3=monthly |
| flag | bool | true | Include trend data |
| is_all | bool | false | All countries aggregated |

### Response

Returns time series data:
```json
{
  "list": [
    {"date": "2026-03-01", "download": 150000, "compareDownload": 120000},
    {"date": "2026-03-02", "download": 160000, "compareDownload": 125000}
  ]
}
```

---

## 3. Download Country — 按国家下载量

`POST /api/data/download-country`

Fetch download data broken down by country.

### Request Body

Same as download-detail.

### Response

Returns per-country breakdown:
```json
{
  "list": [
    {"country": "US", "countryName": "United States", "download": 500000},
    {"country": "JP", "countryName": "Japan", "download": 300000}
  ]
}
```

---

## 4. Revenue Date Range — 收入可用日期

`GET /api/data/revenue-date`

Returns the available date range for revenue data queries.

### Response

```json
{
  "startDate": "2023-01-01",
  "endDate": "2026-03-15"
}
```

---

## 5. Revenue Detail — 收入趋势

`POST /api/data/revenue-detail`

Fetch revenue trend data for a specific app.

### Request Body

```json
{
  "unified_product_id": "xxx",
  "query_start_date": "2026-02-14",
  "query_end_date": "2026-03-16",
  "compare_start_date": "",
  "compare_end_date": "",
  "country_st": [],
  "day_type": 1,
  "flag": true,
  "is_all": false,
  "revenue_type": "ALL"
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| (same as download-detail, plus:) | | | |
| revenue_type | string | "ALL" | Revenue type filter |

---

## 6. Revenue Country — 按国家收入

`POST /api/data/revenue-country`

Fetch revenue data broken down by country.

### Request Body

Same as revenue-detail.

---

## Common Workflows / 常用工作流

### "Temu 最近下载量怎么样？"

1. `unified-product-search(keyword="temu")` → get `unifiedProductId`
2. `download-date` → confirm available range
3. `download-detail(unified_product_id=id, query_start_date="2026-02-14", query_end_date="2026-03-16")` → trend
4. Present trend data with insights

### "对比 Temu 在美国和日本的收入"

1. Get `unifiedProductId` (step 1 above)
2. `revenue-country(unified_product_id=id, ...)` → per-country revenue
3. Filter & compare US vs JP data

### "Temu vs SHEIN 下载量对比"

1. Search both apps → get both `unifiedProductId`
2. `download-detail` for each → two trend datasets
3. Present side-by-side comparison

### Day Type Reference

| day_type | Granularity | Best for |
|---|---|---|
| 1 | Daily | Short ranges (≤90 days) |
| 2 | Weekly | Medium ranges (1-6 months) |
| 3 | Monthly | Long ranges (6+ months) |
