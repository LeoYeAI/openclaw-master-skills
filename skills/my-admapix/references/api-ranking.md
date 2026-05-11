# Ranking API / 排行榜接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

---

## 1. Store Rank — 应用商店排行

`POST /api/data/store-rank`

Fetch App Store / Google Play official rankings.

### Request Body

```json
{
  "market": "appstore",
  "rank_type": "free",
  "cat_type": "game",
  "cat_code": "games",
  "country": ["US"],
  "page": 1,
  "page_size": 20
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| market | string | "appstore" | `appstore` or `googleplay` |
| rank_type | string | "free" | `free`, `paid`, `grossing` |
| cat_type | string | "game" | `game` or `app` |
| cat_code | string | "games" | Category code (from store-categories API). App Store uses lowercase (e.g. "games"), Google Play uses uppercase (e.g. "GAME") |
| country | string[] | ["US"] | Country codes (required, non-empty) |
| page | int | 1 | Page number |
| page_size | int | 20 | Results per page (1-100) |
| date | string | "" | Ranking date (YYYY-MM-DD). Omit for latest. |
| compare_date | string | "" | Compare date for trend comparison |
| is_compare | int | 0 | Enable comparison: 0=off, 1=on |

### Response

**Note:** Uses nested dot-notation field names.

```json
{
  "totalSize": 25,
  "pageIndex": 1,
  "pageSize": 2,
  "maxDate": "2026-03-16",
  "list": [
    {
      "query.info.query.info.productNameEn": "Solitaire Associations Journey",
      "query.info.query.info.productNameCn": null,
      "query.info.query.info.productNameDefault": "Solitaire Associations Journey",
      "query.info.query.info.productLogo": "https://...logo.png",
      "query.info.query.info.unifiedPkgId": "6748950306",
      "query.info.query.info.developerId": 1049188906,
      "query.info.query.companyInfo.companyId": "1049188906",
      "query.info.query.companyInfo.companyName": "Hitapps Games LTD",
      "query.list.rank": 1,
      "query.list.id": "6748950306"
    }
  ]
}
```

Key fields to extract:
- `query.info.query.info.productNameDefault` or `productNameEn` — app name
- `query.info.query.info.productLogo` — app icon URL
- `query.info.query.companyInfo.companyName` — developer name
- `query.info.query.info.unifiedPkgId` — unified product ID (use this for detail/distribution queries)
- `query.list.rank` — ranking position

---

## 2. Generic Rank — 通用排行榜

`POST /api/data/generic-rank`

Unified endpoint for 6 ranking types based on ad intelligence data.

### Request Body

```json
{
  "rank_type": "promotion",
  "category_id": "6014",
  "date_type": 1,
  "page": 1,
  "page_size": 50,
  "start_date": "",
  "end_date": "",
  "country": [],
  "sort_field": "",
  "sort_rule": "desc",
  "day_mode": ""
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| rank_type | string | required | See ranking types below |
| category_id | string | "6014" | Industry category filter. "6014" = all categories. Use tradeLevel1 codes for specific industries: "601" = app, "602" = game. Can also use tradeLevel2/3 codes for finer filtering |
| date_type | int | 1 | Date range type: 1 = last 30 days, 2 = last 7 days, 3 = last 3 days |
| page | int | 1 | Page number |
| page_size | int | 50 | Results per page (1-100) |
| start_date | string | 30 days ago | YYYY-MM-DD (overrides date_type if set) |
| end_date | string | today | YYYY-MM-DD (overrides date_type if set) |
| country | string[] | [] | Country filter |
| sort_field | string | varies | Sort field (default varies by rank_type) |
| sort_rule | string | "desc" | Sort direction |
| day_mode | string | "" | Time window: "D3", "D7", "D30" (promotion only) |

### Ranking Types

| rank_type | Description | Default sort_field |
|---|---|---|
| `promotion` | 推广排行 — apps by ad promotion volume | "15" |
| `download` | 下载排行 — apps by download estimates | "1" |
| `revenue` | 收入排行 — apps by revenue estimates | "1" |
| `newapp` | 新应用排行 — recently launched apps | "15" |
| `overseas` | 出海排行 — Chinese apps going global | "15" |
| `drama` | 短剧排行 — short drama/content apps | "2" |

### Response — varies by rank_type!

**IMPORTANT:** Different rank types return different response structures.

#### promotion / newapp / overseas response:

Uses nested dot-notation field names (same style as store-rank):
```json
{
  "totalSize": 1000,
  "list": [
    {
      "query.info.query.info.productNameDefault": "App Name",
      "query.info.query.info.productLogo": "https://...logo.png",
      "query.info.query.info.unifiedPkgId": "123456",
      "query.info.query.companyInfo.companyName": "Developer Name",
      "query.list.rank": 1,
      "query.list.id": "123456"
    }
  ]
}
```

#### download response:

Uses flat field names:
```json
{
  "totalSize": 505970,
  "list": [
    {
      "productId": "6448311069",
      "appCode": "6448311069",
      "appName": "ChatGPT",
      "developer": "OpenAI OpCo, LLC",
      "developerId": "620366005",
      "iconUrl": "https://...logo.png",
      "queryDownloadCnt": 78578987,
      "compareDownloadCnt": 85509701,
      "downloadGrowth": -6930714,
      "growthPercent": -8.11,
      "isAd": "1",
      "productCnt": 3
    }
  ]
}
```

Key fields:
- `appName` — app name
- `queryDownloadCnt` — download count in query period
- `compareDownloadCnt` — download count in compare period
- `downloadGrowth` — absolute growth
- `growthPercent` — growth percentage (negative = decline)

#### revenue response:

Similar flat structure to download, with revenue-specific fields.

### Rank Type Details

**promotion** — Ranks apps by advertising intensity. "Which apps are spending the most on ads?"
- Supports `day_mode`: "D3" (3 days), "D7" (7 days), "D30" (30 days)
- Advanced filter params (optional): `keyword`, `trade_level1/2/3`, `subject_type`, `topic_type`, `product_model`, `product_type`, `selling`, `monetization`, `pay_type`, `company_location`, `campaign_list`, `media_ids`, `device`

**download** — Ranks apps by estimated download volume. "Which apps are downloaded the most?"
- Includes auto-calculated compare period for growth calculation
- Advanced filter params (optional): `trade_level1/2/3`, `subject_type`, `topic_type`, `product_model`, `product_type`, `selling`, `monetization`, `pay_type`, `company_location`, `media_ids`, `device`
- ⚠️ Download/revenue figures are third-party estimates

**revenue** — Ranks apps by estimated revenue. "Which apps earn the most?"
- Same advanced filter params as download
- ⚠️ Revenue figures are third-party estimates

**newapp** — Tracks newly launched apps. "What new apps just launched?"

**overseas** — Tracks Chinese companies' apps in global markets. "Which Chinese apps are going overseas?"

**drama** — Tracks short drama / content apps. "What's trending in short drama?"

---

## 3. Store Categories — 商店分类

`GET /api/data/store-categories`

Fetch available app store categories for use with store-rank.

---

## 4. Store Countries — 商店国家列表

`GET /api/data/store-countries`

Fetch available countries for store ranking filter.

---

## User Intent Mapping / 用户意图映射

| User says | rank_type | Extra params |
|---|---|---|
| "App Store 免费榜" | → use store-rank | market=appstore, rank_type=free |
| "Google Play 畅销榜" | → use store-rank | market=googleplay, rank_type=grossing |
| "哪个App广告投得最多" | promotion | sort by default |
| "下载量最高的游戏" | download | — |
| "收入最高的App" | revenue | — |
| "最近新上线的App" | newapp | — |
| "出海做得好的中国App" | overseas | — |
| "短剧排行" | drama | — |
| "美国市场推广排行" | promotion | country=["US"] |
| "最近3天广告量最大的" | promotion | day_mode="D3" |
