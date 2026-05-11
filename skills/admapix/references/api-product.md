# Product & Company API / 产品与公司接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

---

## 1. Unified Product Search — 统一产品搜索

`POST /api/data/unified-product-search`

Search for unified products (cross-platform aggregated apps). This is the primary entry point for finding apps/products.

### Request Body

```json
{
  "keyword": "temu",
  "type": 1,
  "page": 1,
  "page_size": 20,
  "start_date": "",
  "end_date": "",
  "sort_field": "3",
  "sort_rule": "desc",
  "unified_product_id": "",
  "unified_developer_id": ""
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| keyword | string | "" | Search keyword |
| type | int | 1 | Search type |
| page | int | 1 | Page number |
| page_size | int | 20 | Results per page (1-100) |
| start_date | string | 30 days ago | YYYY-MM-DD |
| end_date | string | today | YYYY-MM-DD |
| sort_field | string | "3" | Sort field |
| sort_rule | string | "desc" | Sort direction |
| unified_product_id | string | "" | Filter by specific unified product |
| unified_developer_id | string | "" | Filter by specific developer |
| country_ids | string[] | [] | Country filter (mapped to countryLevel2) |
| media_ids | string[] | [] | Media channel filter |
| device | string[] | [] | Device filter |

**Note:** `country_ids`, `media_ids`, and `device` also apply to `product-search` and `company-search`.

### Response

```json
{
  "pageIndex": 1,
  "pageSize": 20,
  "totalSize": 96,
  "list": [
    {
      "unifiedProductId": "1641486558",
      "unifiedProductName": "<font color='red'>Temu</font>: Shop Like a Billionaire",
      "unifiedCompanyId": "569338280",
      "unifiedCompanyName": "Temu",
      "productIds": ["com.einnovation.temu", "1641486558", "com.Temu_Team_Up.used_letgo_buy_app1"],
      "tradeLevel1": ["603"],
      "tradeLevel2": ["60301", "60303"],
      "tradeLevel3": ["6030102", "6030301"],
      "tradeLevel4": [],
      "showCost": 23236263827,
      "impression": 2412399002696,
      "materialUvCnt": 7451078,
      "productCnt": 3,
      "iconUrl": "https://...logo.png",
      "collectId": null,
      "formerNames": null,
      "adSource": 9
    }
  ],
  "folderTotalSize": null,
  "newNum": 0,
  "latestDate": null,
  "gptCorrect": null,
  "filters": null
}
```

### ⚠️ Important Notes

1. **HTML tags in names:** `unifiedProductName` may contain HTML highlight tags `<font color='red'>keyword</font>`. Strip these before displaying.
2. The `unifiedProductId` returned here is the key input for detail/distribution/download/revenue endpoints.
3. `productIds` contains platform-specific IDs (Android package name, iOS app ID).

### Key Fields

| Field | Description |
|---|---|
| unifiedProductId | Unique cross-platform product ID — **use this for all detail/distribution queries** |
| unifiedProductName | App name (may contain HTML `<font>` tags for keyword highlighting) |
| unifiedCompanyId | Developer/company ID |
| unifiedCompanyName | Developer/company name |
| productIds | Array of platform-specific product IDs |
| iconUrl | App icon URL |
| showCost | Total ad spend estimate (raw number) |
| impression | Total impression count (raw number) |
| materialUvCnt | Total unique creative count |
| productCnt | Number of platform versions |
| tradeLevel1/2/3/4 | Industry category codes |

---

## 2. Product Search — 产品搜索

`POST /api/data/product-search`

Search for individual products (platform-specific). Same request body as unified product search.

### Response

Returns **normalized** product items (different structure from unified-product-search):

```json
{
  "list": [
    {
      "id": "com.einnovation.temu",
      "unifiedProductId": "com.einnovation.temu",
      "name": "Temu: Shop Like a Billionaire",
      "logo": "https://...logo.png",
      "pkg": "com.einnovation.temu",
      "developer": "Whaleco Inc.",
      "developerId": "569338280",
      "os": "android",
      "tags": ["60301", "60303"],
      "impressionEstimate": 2412399002696,
      "materialCnt": 7451078,
      "firstTime": "2022-09-01",
      "lastTime": "2026-03-17",
      "adDays": 1293,
      "countries": ["US", "JP"],
      "mediaList": ["Facebook", "Google"],
      "selling": "w2a",
      "productType": "App"
    }
  ],
  "totalSize": 96
}
```

### Key Fields

| Field | Description |
|---|---|
| id | Product ID (package name or app store ID) |
| unifiedProductId | Same as id for individual products |
| name | App name (HTML stripped) |
| os | "android" or "ios" |
| tags | Industry category codes (tradeLevel3 > tradeLevel2 > tradeLevel1) |
| impressionEstimate | Estimated impressions (raw number) |
| adDays | Calculated days between firstTime and lastTime |

---

## 3. Company Search — 公司/开发者搜索

`POST /api/data/company-search`

Search for companies/developers. Same request body as unified product search.

### Response

```json
{
  "pageIndex": 1,
  "pageSize": 1,
  "totalSize": 7,
  "list": [
    {
      "unifiedCompanyId": "1773957248",
      "unifiedCompanyName": "<font color='red'>Bytedance</font> 字节跳动",
      "unifiedCompanyRegion": "CN",
      "uaList": [1, 2, 3],
      "showCost": 10768429037,
      "impression": 2844436033460,
      "collectId": null,
      "productIds": ["com.zhiliaoapp.musically", "com.ss.android.ugc.trill", "1235601864", "..."],
      "productCnt": 53,
      "downloadCnt": null,
      "hitDeveloper": false,
      "unifiedCompanyNameDefault": null,
      "developerList": [
        {"id": "640989321", "name": "Bytedance Pte. Ltd", "status": 0, "productCnt": 9, "collectId": null}
      ],
      "unifiedCompanyNameOrigin": "Bytedance 字节跳动",
      "adSource": 9
    }
  ]
}
```

### Key Fields

| Field | Description |
|---|---|
| unifiedCompanyId | Unified company ID — **use for developer-detail queries** |
| unifiedCompanyName | Company name (may contain HTML `<font>` tags) |
| unifiedCompanyNameOrigin | Original company name without highlighting |
| unifiedCompanyRegion | Company region code (e.g. "CN") |
| showCost | Total ad spend estimate |
| impression | Total impressions |
| productCnt | Total number of products |
| productIds | All product IDs under this company |
| developerList | List of developer accounts under the company |
| developerList[].id | Developer ID |
| developerList[].name | Developer name |
| developerList[].productCnt | Products under this developer |

---

## 4. App Detail — 应用详情

`GET /api/data/app-detail?id={unifiedProductId}`

Get comprehensive detail for a specific app/product.

| Parameter | Type | Description |
|---|---|---|
| id | string | unified product ID (from unified-product-search), or a package name (e.g. `com.einnovation.temu`) — the API will auto-resolve package names to unified IDs |

### Response

```json
{
  "unifiedProductId": "com.einnovation.temu",
  "unifiedProductName": "Temu: Shop Like a Billionaire",
  "unifiedCompanyId": "569338280",
  "unifiedCompanyName": "Temu",
  "productIds": ["com.einnovation.temu", "1641486558", "com.Temu_Team_Up.used_letgo_buy_app1"],
  "tradeLevel1": ["603"],
  "tradeLevel2": ["60301", "60303"],
  "tradeLevel3": ["6030102", "6030301"],
  "tradeLevel4": null,
  "showCost": null,
  "impression": null,
  "materialUvCnt": null,
  "productCnt": 3,
  "iconUrl": "https://...logo.png",
  "collectId": null,
  "formerNames": null,
  "adSource": 9
}
```

**Note:** `showCost`, `impression`, `materialUvCnt` are `null` in app-detail (these are only available in search results). Use unified-product-search to get these metrics.

---

## 5. Developer Detail — 开发者详情

`GET /api/data/developer-detail?id={unifiedCompanyId}`

Get developer/company detail.

| Parameter | Type | Description |
|---|---|---|
| id | string | unified company ID (from unified-product-search or company-search) |

### Response

```json
{
  "unifiedCompanyId": "569338280",
  "unifiedCompanyName": "Temu",
  "unifiedCompanyRegion": "美国",
  "uaList": [1, 2, 3],
  "showCost": null,
  "impression": null,
  "collectId": null,
  "productIds": ["com.einnovation.temu", "1641486558", "com.Temu_Team_Up.used_letgo_buy_app1"],
  "productCnt": 6,
  "downloadCnt": null,
  "hitDeveloper": null,
  "unifiedCompanyNameDefault": null,
  "developerList": [
    {"id": "444696740", "name": "HY Dev LLC", "status": 0, "productCnt": 7, "collectId": null},
    {"id": "480100326", "name": "Temu", "status": 0, "productCnt": 2, "collectId": null}
  ],
  "unifiedCompanyNameOrigin": null,
  "adSource": 9
}
```

### Key Fields

| Field | Description |
|---|---|
| unifiedCompanyName | Company name |
| unifiedCompanyRegion | Company location (Chinese name, e.g. "美国") |
| productIds | All product IDs |
| productCnt | Total product count |
| developerList | Sub-developer accounts |

---

## 6. For Product List — 公司子产品列表

`POST /api/data/for-product-list`

Get individual products under a company (used in company search popover).

### Request Body

```json
{
  "unified_id": "xxx",
  "page": 1,
  "page_size": 10
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| unified_id | string | required | Unified company ID |
| page | int | 1 | Page number |
| page_size | int | 10 | Results per page (1-100) |
| trade_level3 | string[] | [] | Industry category filter |
| device | string[] | [] | Device filter |
| country_level2 | string[] | [] | Country filter |

---

## 6b. Product List — 子产品列表

`POST /api/data/product-list`

Get individual products (per platform) under a unified product.

### Request Body

```json
{
  "unified_product_id": "xxx",
  "page": 1,
  "page_size": 20
}
```

---

## 7. Product Agg List — 开发者产品聚合列表

`POST /api/data/product-agg-list`

Get aggregated products under a specific developer.

### Request Body

```json
{
  "unified_developer_id": "xxx",
  "page": 1,
  "page_size": 20
}
```

---

## 8. Product Content Search — 产品维度素材搜索

`POST /api/data/product-content-search`

Search for ad creatives specifically associated with a product.

### Request Body

```json
{
  "content_type": "creative",
  "unified_product_id": "xxx",
  "keyword": "",
  "page": 1,
  "page_size": 20,
  "start_date": "",
  "end_date": "",
  "sort_field": "3",
  "sort_rule": "desc"
}
```

| Parameter | Type | Description |
|---|---|---|
| content_type | string | creative, imagevideo, preplay, demoad, document |
| unified_product_id | string | Required — the target product |
| keyword | string | Optional further keyword filter |

### Response

Same structure as `/api/data/search` response — `pageIndex`, `pageSize`, `totalSize` + `list[]` of creatives. See api-creative.md for full field documentation.

---

## 9. App Profile — 应用商店画像

`GET /api/data/app-profile?id={productId}&type=1`

Get app store profile and audience data.

| Parameter | Type | Default | Description |
|---|---|---|---|
| id | string | required | Product ID |
| type | int | 1 | Profile type |

### Response

Returns store information, audience demographics, category rankings, etc.

---

## 10. Similar Apps — 相似/竞品应用

`POST /api/data/similar-apps`

Find apps with similar audiences or competitive overlap based on a package name.

### Request Body

```json
{
  "pkg": "com.einnovation.temu",
  "sort_field": "7",
  "sort_rule": "desc",
  "trade_level3": [],
  "device": [],
  "country_level2": []
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| pkg | string | required | App package name |
| sort_field | string | "7" | Sort: "7"=ad days, "1"=similarity, "15"=impressions, "5"=creative count, "3"=first seen |
| sort_rule | string | "desc" | Sort direction |
| trade_level3 | string[] | [] | Industry category filter |
| device | string[] | [] | Device filter |
| country_level2 | string[] | [] | Country filter |

### Response

Returns normalized product list (same structure as `product-search` response), with an additional `similarity` field per item.

---

## 11. SDK Detail — SDK 集成详情

`GET /api/data/sdk-detail?pkg={packageName}`

Query which SDKs an app has integrated.

| Parameter | Type | Default | Description |
|---|---|---|---|
| pkg | string | required | App package name (e.g. `com.einnovation.temu`) |
| sdk_type | string | "" | Optional SDK type filter |

### Response

Returns SDK integration details for the specified app. Returns `{}` if no data available.

---

## 12. Product Content Counts — 产品素材类型计数

`POST /api/data/product-content-counts`

Get the total creative count for a product across all 5 content types. Useful for showing a quick overview of a product's ad creative portfolio.

### Request Body

```json
{
  "unified_product_id": "com.einnovation.temu",
  "start_date": "",
  "end_date": ""
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| product_ids | string[] | — | Product ID list (use this OR unified_product_id) |
| unified_product_id | string | — | Unified product ID (use this OR product_ids) |
| start_date | string | 365 days ago | YYYY-MM-DD |
| end_date | string | today | YYYY-MM-DD |

### Response

```json
{
  "creative": 1234,
  "imagevideo": 5678,
  "preplay": 90,
  "demoad": 345,
  "document": 67
}
```

---

## ⚠️ Common Pitfalls

1. **HTML tags in names:** Both `unifiedProductName` and `unifiedCompanyName` may contain `<font color='red'>keyword</font>` HTML tags when returned from search endpoints. Always strip HTML before displaying.
2. **Null metrics in detail endpoints:** `app-detail` and `developer-detail` return `null` for `showCost`, `impression`, `materialUvCnt`. These metrics are only available in search result lists.
3. **ID types:** `unifiedProductId` and `unifiedCompanyId` are strings, not integers. Some may look like iOS app IDs (numeric) while others are Android package names.

---

## Common Workflow / 常用工作流

### Finding an app's full data

1. **Search** → `unified-product-search(keyword="temu")` → get `unifiedProductId`
2. **Detail** → `app-detail(id=unifiedProductId)` → full app info
3. **Creatives** → `product-content-search(unified_product_id=id, content_type="creative")` → app's ads
4. **Sub-products** → `product-list(unified_product_id=id)` → iOS/Android versions

### Finding a developer's portfolio

1. **Search** → `company-search(keyword="ByteDance")` → get `unifiedCompanyId`
2. **Detail** → `developer-detail(id=unifiedCompanyId)` → company info
3. **Products** → `product-agg-list(unified_developer_id=id)` → all their apps

### Finding competitors for an app

1. **Search** → `unified-product-search(keyword="temu")` → get package name from `productIds`
2. **Similar** → `similar-apps(pkg="com.einnovation.temu")` → competitor list
3. **Enrich** → For each competitor, use `app-detail` or `product-content-counts` for deeper analysis

### Quick app creative portfolio overview

1. **Search** → `unified-product-search(keyword="temu")` → get `unifiedProductId`
2. **Counts** → `product-content-counts(unified_product_id=id)` → counts per content type
3. **Browse** → `product-content-search(unified_product_id=id, content_type="creative")` → actual creatives
