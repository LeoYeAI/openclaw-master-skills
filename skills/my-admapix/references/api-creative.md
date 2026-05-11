# Creative Search API / 素材搜索接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

---

## 1. Search — 素材搜索

`POST /api/data/search`

Search ad creatives across 5 content types. Supports H5 page generation.

### Content Types

| content_type | Label | Description |
|---|---|---|
| `creative` | 创意组合 | Multi-asset ad bundles (image+video+playable combos) |
| `imagevideo` | 图片/视频 | Individual image or video assets |
| `preplay` | 试玩广告 | Playable/interactive ads |
| `demoad` | 落地页 | Landing pages |
| `document` | 文档素材 | Document-format ads |

### Request Body

```json
{
  "content_type": "creative",
  "keyword": "puzzle game",
  "keyword_type": "",
  "is_new": false,
  "start_date": "2026-02-14",
  "end_date": "2026-03-16",
  "page": 1,
  "page_size": 20,
  "sort_field": "3",
  "sort_rule": "desc",
  "country_ids": [],
  "media_ids": [],
  "adfaction_ids": [],
  "device": [],
  "topic_type": [],
  "languages": [],
  "material_type": "",
  "trade_level1": [],
  "trade_level2": [],
  "trade_level3": [],
  "subject_type": [],
  "product_model": [],
  "product_type": [],
  "selling": [],
  "monetization": [],
  "pay_type": [],
  "company_location": [],
  "campaign_list": [],
  "ad_media_type": [],
  "appeal_type_list": [],
  "interaction_list": [],
  "material_tag": [],
  "material_removal_repeat": false,
  "demoad_formats": [],
  "web_tools": [],
  "material_top_limit": "",
  "gpt_search": null,
  "generate_page": false,
  "delivery": null
}
```

### Key Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| content_type | string | required | One of: creative, imagevideo, preplay, demoad, document |
| keyword | string | "" | Search keyword (app name, ad copy, brand, etc.) |
| keyword_type | string | "" | Keyword match scope (leave empty for default per content_type) |
| start_date | string | 30 days ago | YYYY-MM-DD |
| end_date | string | today | YYYY-MM-DD |
| page | int | 1 | Page number (≥1) |
| page_size | int | 60 | Results per page (1-100) |
| sort_field | string | "3" | "3"=first seen, "4"=days active, "11"=relevance, "15"=impressions |
| sort_rule | string | "desc" | "desc" or "asc" |
| country_ids | string[] | [] | Country codes, e.g. ["US","JP"] — use `ccode` from filter-options |
| media_ids | string[] | [] | Media channel IDs — use `ccode` from filter-options |
| device | string[] | [] | Device filter — use `ccode` from filter-options |
| trade_level1/2/3 | string[] | [] | Industry category filters (hierarchical) |
| product_model | string[] | [] | Product model filter — use `ccode` from filter-options `productModel` (e.g. "1"=non-game, "2"=game) |
| material_type | string | "" | Material format filter ("1"=image, "2"=video). **Only effective for `imagevideo` content type** — ignored by other content types |
| ad_media_type | string[] | [] | Ad media type codes |
| material_removal_repeat | bool | false | Deduplicate similar creatives |
| gpt_search | bool/null | null | Enable AI-powered search |
| generate_page | bool | false | Generate H5 result page |
| delivery | object/null | null | `{channel, apiBase, externalUserId}` for H5 page context |

### Response

**Note:** `totalSize` may be `null` for keyword searches. Use `pageIndex` and `pageSize` for pagination.

```json
{
  "pageIndex": 1,
  "pageSize": 20,
  "totalSize": null,
  "list": [
    {
      "id": "87f11b718e162ca06589f3c33ef99472",
      "title": null,
      "describe": null,
      "documentId": null,
      "findCnt": 1,
      "findCntSum": 1,
      "firstTime": "2026-03-16 13:44:54",
      "lastTime": null,
      "globalFirstTime": "2026-03-16 13:44:54",
      "globalLastTime": "2026-03-16 13:44:54",
      "imageFp": [],
      "imageUrl": [],
      "videoFp": ["80c15b563dded967090b0f5850f4941b"],
      "videoUrl": ["https://...video.mp4"],
      "playHtmlFp": [],
      "playHtmlUrl": [],
      "demoadCnt": 1,
      "appList": [
        {
          "id": "6498883328",
          "cnt": null,
          "impression": null,
          "name": "Tile Trip - Match <font color='red'>Puzzle</font> Game",
          "logo": "https://...logo.png",
          "geo": null,
          "pkg": null,
          "developer": "Oakever Games",
          "developerId": "1604529155",
          "productType": [1],
          "tradeLevel1": null,
          "tradeLevel2": null,
          "tradeLevel3": null
        }
      ],
      "sourceAppList": null,
      "originalUrl": null,
      "showCnt": 2802,
      "impression": 145354,
      "webSite": null,
      "demoadWebSite": null,
      "thumbnailConverUrl": ["https://...keyframe.jpg"],
      "videoTimeSpan": [60],
      "growthValue": null,
      "growthRate": null,
      "coverContent": null,
      "novel": null,
      "adSource": 9
    }
  ],
  "folderTotalSize": null,
  "newNum": null,
  "latestDate": null,
  "gptCorrect": {
    "sourceKeyword": "puzzle",
    "correctKeyword": null,
    "type": 3,
    "developers": [],
    "wrongs": [],
    "gptSxes": [],
    "slices": []
  },
  "filters": [],
  "page_url": "/p/abc123",
  "page_key": "abc123",
  "page_expires_at": "2026-03-19 12:00:00"
}
```

`page_url`/`page_key`/`page_expires_at` only present when `generate_page: true`.

### ⚠️ Important Notes

1. **HTML tags in names:** `appList[].name` may contain HTML highlight tags like `<font color='red'>keyword</font>`. Strip these before displaying to the user.
2. **Null values:** Many fields can be `null` — always handle null gracefully.
3. **totalSize null:** For keyword searches, `totalSize` is often `null`. The actual result count is reflected in `list` length per page.

### Response Key Fields

| Field | Description |
|---|---|
| pageIndex | Current page number |
| pageSize | Results per page |
| totalSize | Total matching results (may be null) |
| list[].id | Creative ID |
| list[].title | Ad title (may be null) |
| list[].describe | Ad copy text (may be null) |
| list[].appList[].name | Associated app name — **may contain HTML `<font>` tags** |
| list[].appList[].developer | Developer/publisher name |
| list[].appList[].developerId | Developer ID |
| list[].appList[].logo | App icon URL |
| list[].impression | Estimated impression count |
| list[].findCntSum | Days the ad has been active |
| list[].showCnt | Number of ad variants detected |
| list[].globalFirstTime | First seen date |
| list[].globalLastTime | Last seen date |
| list[].imageUrl | Image asset URLs (array) |
| list[].videoUrl | Video asset URLs (array) |
| list[].playHtmlUrl | Playable ad URLs (array) |
| list[].thumbnailConverUrl | Video thumbnail/keyframe URLs (array) |
| list[].videoTimeSpan | Video durations in seconds (array) |
| list[].demoadCnt | Number of landing pages |
| gptCorrect | AI keyword correction info |

---

## 2. Count — 素材计数

`POST /api/data/count`

Get total count, new count, and latest date for a single content type.

### Request Body

Same as search (content_type + filter params). Only counting fields matter — page/sort are ignored.

### Response

```json
{
  "totalSize": 50000,
  "newNum": 1200,
  "latestDate": "2026-03-16"
}
```

---

## 3. Count All — 全类型计数

`POST /api/data/count-all`

Aggregate counts across all 5 content types. No request body needed.

### Response

```json
{
  "creative": { "label": "创意组合", "totalSize": 50000, "newNum": 1200, "latestDate": "2026-03-16" },
  "imagevideo": { "label": "图片/视频", "totalSize": 120000, "newNum": 3500, "latestDate": "2026-03-16" },
  "preplay": { "label": "试玩广告", "totalSize": 8000, "newNum": 200, "latestDate": "2026-03-15" },
  "demoad": { "label": "落地页", "totalSize": 30000, "newNum": 800, "latestDate": "2026-03-16" },
  "document": { "label": "文档素材", "totalSize": 5000, "newNum": 100, "latestDate": "2026-03-14" }
}
```

---

## 4. Distribute — 素材分布分析

`POST /api/data/distribute`

Analyze distribution of specific creatives by dimension.

### Request Body

```json
{
  "content_type": "creative",
  "dimension": "media",
  "ids": ["creative_id_1", "creative_id_2"],
  "start_date": "",
  "end_date": ""
}
```

| Parameter | Type | Description |
|---|---|---|
| content_type | string | Content type |
| dimension | string | Distribution dimension — use `advertiser` (not `adfaction`) |
| ids | string[] | Creative IDs to analyze |
| start_date/end_date | string | Date range |

### Available Dimensions per Content Type

| content_type | Dimensions |
|---|---|
| creative | media, advertiser, app |
| imagevideo | media, advertiser, app, country |
| preplay | media, advertiser, app |
| demoad | media, advertiser, app |
| document | media, advertiser, app |

**Note:** Use `advertiser` as the dimension name (the API internally maps it to `adfaction`).

Use `GET /api/data/distribute-dims` to fetch this mapping dynamically.

---

## 5. Filter Options — 筛选枚举项

`GET /api/data/filter-options`

Returns all filter enum options in a single batch call (13 categories).

### Response

**IMPORTANT:** Each item has both `code` (complex internal format) and `ccode` (simplified code). **Always use `ccode` when passing filter values to search/query endpoints.**

```json
{
  "countries": [
    {"code": "毛里塔尼亚_2_MRT", "nameCn": "毛里塔尼亚", "nameEn": "Mauritania", "ccode": "MR", "icon": "https://...flag.png"}
  ],
  "mediaChannels": [
    {"code": "海外平台-101-Adcolony", "nameCn": "Adcolony", "nameEn": "Adcolony", "ccode": "101", "icon": "https://...icon.png"}
  ],
  "adTypes": [
    {"code": "adstyle_原生_1076682150_1076682150", "nameCn": "原生", "nameEn": "Native Ads", "ccode": "1076682150", "icon": null}
  ],
  "device": [
    {"code": "Android_2_1", "nameCn": "Android", "nameEn": "Android", "ccode": "1", "icon": "android"}
  ],
  "tradeLevel": [
    {"code": "601", "nameCn": "工具", "nameEn": "Tools", "ccode": "601", "icon": null}
  ],
  "productModel": [
    {"code": "1", "nameCn": "非游戏", "nameEn": "Non-game", "ccode": "1", "icon": null}
  ],
  "productType": [
    {"code": "app_1_1", "nameCn": "App", "nameEn": "App", "ccode": "1", "icon": null}
  ],
  "selling": [
    {"code": "5005_w2a", "nameCn": "W2A", "nameEn": "W2A", "ccode": "w2a", "icon": null}
  ],
  "subjectType": [
    {"code": "gold_0_1", "nameCn": "金币", "nameEn": "Gold", "ccode": "1", "icon": null}
  ],
  "topicType": [
    {"code": "传奇_9_64", "nameCn": "传奇", "nameEn": "Legend", "ccode": "90064", "icon": null}
  ],
  "languages": [
    {"code": "南非荷兰语_af", "nameCn": "南非荷兰语", "nameEn": "Afrikaans", "ccode": "af", "icon": null}
  ],
  "materialTag": [
    {"code": "AI_0_1", "nameCn": "AI", "nameEn": "AI", "ccode": "001", "icon": ""}
  ],
  "tradeLevel2": [
    {"code": "60301", "nameCn": "电商", "nameEn": "E-commerce", "ccode": "60301", "icon": null}
  ],
  "materialFormat": [
    {"code": "5006_100", "nameCn": "单图", "nameEn": "Single Image", "ccode": "100", "icon": null}
  ]
}
```

### Filter Code Usage

| Filter parameter | Use `ccode` from | Example |
|---|---|---|
| country_ids | countries | "US", "JP", "MR" |
| media_ids | mediaChannels | "101" (Adcolony) |
| device | device | "1" (Android) |
| trade_level1/2/3 | tradeLevel / tradeLevel2 | "601" (Tools), "60301" (E-commerce) |
| product_model | productModel | "1" (Non-game), "2" (Game) |
| ad_media_type | adTypes | "1076682150" (Native Ads) |
| languages | languages | "af" (Afrikaans) |
| material_tag | materialTag | "001" (AI) |

### Additional Response Field: tradeLevelTree

The response also includes `tradeLevelTree` — a hierarchical tree structure of all industry categories (level 1 → 2 → 3), useful for building category pickers or understanding the category hierarchy.

---

## 6. Content Detail — 素材详情

`GET /api/data/content-detail`

Get detailed information about a specific creative, or its related content (associated media, trends, profile, etc.).

### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| content_type | string | required | creative, imagevideo, preplay, demoad, document |
| id | string | required | Content ID |
| related | string | (none) | Related data type (see below). Omit for base info. |
| material_type | string | "" | Only for `related=imagevideo`: "1"=image, "2"=video |
| start_date | string | 365 days ago | YYYY-MM-DD |
| end_date | string | today | YYYY-MM-DD |

### Related Types

| related | Description |
|---|---|
| *(omitted)* | Base info — creative metadata and asset URLs |
| `imagevideo` | Related image/video assets |
| `document` | Related document assets |
| `trend` | Impression/activity trend over time |
| `profile` | Audience profile data |
| `preplay` | Related playable ads |
| `demoad` | Related landing pages |

### Examples

```
# Get base info for a creative
GET /api/data/content-detail?content_type=creative&id=abc123

# Get related videos
GET /api/data/content-detail?content_type=creative&id=abc123&related=imagevideo&material_type=2

# Get trend data
GET /api/data/content-detail?content_type=creative&id=abc123&related=trend&start_date=2026-01-01&end_date=2026-03-16
```

---

## 7. Item Apps — 素材关联应用

`POST /api/data/item-apps`

Batch-fetch the associated apps for a list of creative IDs. Useful for enriching search results with app info.

### Request Body

```json
{
  "content_type": "creative",
  "ids": ["id1", "id2", "id3"]
}
```

| Parameter | Type | Description |
|---|---|---|
| content_type | string | Content type |
| ids | string[] | Creative IDs (max 100) |

### Response

Returns a mapping of creative ID → app list:

```json
{
  "id1": [
    {"id": "com.example.app", "name": "App Name", "logo": "https://..."}
  ],
  "id2": [
    {"id": "6498883328", "name": "Another App", "logo": "https://..."}
  ]
}
```

---

## 8. Screen Types — 单类筛选项

`GET /api/data/screen-types?element_type=1`

Fetch a single filter category by element type ID.

| element_type | Category |
|---|---|
| 1004 | tradeLevel (industry) |
| 2002 | countries |
| 2004 | device |
| 2005 | languages |
| 2006 | mediaChannels |
| 2008 | materialTag |
| 3000 | subjectType |
| 3006 | productType |
| 5001 | adTypes |
| 5005 | selling |
| 5006 | materialFormat |

---

## 7. Page Config — 页面配置

`GET /api/data/page-config?scope=search`

Returns page layout configuration for the specified scope.
