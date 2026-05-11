# Market Analysis API / 市场分析接口

Base URL: `https://api.admapix.com`
Auth: `X-API-Key: $ADMAPIX_API_KEY`

---

## Market Search — 市场分析搜索

`POST /api/data/market-search`

Analyze the advertising market from 5 different dimensions. Provides macro-level market intelligence.

### Request Body

```json
{
  "class_type": 1,
  "data_type": "1",
  "start_date": "",
  "end_date": "",
  "trade_level3": [],
  "country_level2": [],
  "media_ids": [],
  "device": [],
  "ad_company_location": [],
  "traffic_company_location": [],
  "page": 1,
  "page_size": 20
}
```

| Parameter | Type | Default | Description |
|---|---|---|---|
| class_type | int | required | Analysis dimension (1-5, see below) |
| data_type | string | "1" | "1"=game, "2"=app |
| start_date | string | today | YYYY/MM/DD (note: slash format) |
| end_date | string | today | YYYY/MM/DD (note: slash format) |
| trade_level3 | string[] | [] | Sub-industry filter |
| country_level2 | string[] | [] | Country filter |
| media_ids | string[] | [] | Media channel filter |
| device | string[] | [] | Device filter |
| ad_company_location | string[] | [] | Advertiser company location filter |
| traffic_company_location | string[] | [] | Publisher/traffic source location filter |
| page | int | 1 | Page number |
| page_size | int | 20 | Results per page (1-100) |

### Dimensions (class_type)

| class_type | Dimension | Description | Best for |
|---|---|---|---|
| 1 | 国家 Country | Market size by country | "Which countries have the most game ads?" |
| 2 | 媒体 Media | Market share by ad network | "Which ad platforms are most used?" |
| 3 | 子媒体 Sub-Media | Breakdown within media channels | "What Facebook ad placements are popular?" |
| 4 | 广告主 Advertiser | Top advertisers in the market | "Who are the biggest game advertisers?" |
| 5 | 流量主 Publisher | Top publishers / traffic sources | "Which publishers carry the most ads?" |

### Data Type

| data_type | Description |
|---|---|
| "1" | 游戏 Game — game industry data |
| "2" | 应用 App — non-game app data |

**Note:** Date format for this endpoint uses slashes (`YYYY/MM/DD`), not dashes.

### Response

**IMPORTANT:** This endpoint returns a different structure from other endpoints. The response uses `data_list` (not `list`) and nested dot-notation field names.

**Pagination fields:** `page_total` (total pages), `page_num` (current page), `page_size`.

#### class_type=1 (Country) response:
```json
{
  "data_list": [
    {
      "market_query.list.id": "ID",
      "query.country_info.s_code": "ID",
      "query.country_info.c_code": "ID",
      "query.country_info.country_name": "印度尼西亚",
      "market_query.list.raw_impression": 11578945855,
      "market_query.list.impression": "116亿",
      "market_query.list.impressionRatio": "13.64%",
      "market_query.list.rank": 1,
      "query.country_info.image": "https://...flag.png"
    }
  ],
  "page_total": 34,
  "page_num": 1,
  "page_size": 3
}
```

Key fields to extract:
- `query.country_info.country_name` — country name (Chinese)
- `query.country_info.c_code` — country code
- `market_query.list.impression` — impression count (pre-formatted string like "116亿")
- `market_query.list.raw_impression` — raw numeric impression count
- `market_query.list.impressionRatio` — percentage share
- `market_query.list.rank` — rank position

#### class_type=4 (Advertiser) response:
```json
{
  "data_list": [
    {
      "market_query.list.market_query.list.advertiser": "275091615",
      "market_query.list.query.company_info.unified_company_name": "VGam.es",
      "market_query.list.query.company_info.unified_company_id": "275091615",
      "query.pkg_info.productName": "Math Crossword – Endless Fun",
      "query.pkg_info.productLogo": "https://...logo.png",
      "query.pkg_info.unifiedPkgId": "com.vgames.mathcrossword",
      "market_query.list.market_query.list.company_impression": "64亿",
      "market_query.list.market_query.list.raw_company_impression": 6449946845,
      "market_query.list.market_query.list.company_impressionRatio": "10.31%",
      "market_query.list.market_query.list.top1_app_impression": "64亿",
      "market_query.list.market_query.list.rank": 1
    }
  ],
  "page_total": 500,
  "page_num": 1,
  "page_size": 2
}
```

Key fields to extract:
- `market_query.list.query.company_info.unified_company_name` — company name
- `query.pkg_info.productName` — top product name
- `market_query.list.market_query.list.company_impression` — total impression (formatted)
- `market_query.list.market_query.list.company_impressionRatio` — market share %
- `market_query.list.market_query.list.rank` — rank position

---

## Common Workflows / 常用工作流

### "全球游戏广告市场哪个国家最大？"

```json
{"class_type": 1, "data_type": "1"}
```

### "美国市场最大的游戏广告主是谁？"

```json
{"class_type": 4, "data_type": "1", "country_level2": ["US"]}
```

### "电商App广告市场对比：东南亚 vs 北美"

Two queries:
1. `{"class_type": 1, "data_type": "2", "country_level2": ["TH","VN","ID","MY","PH","SG"]}`
2. `{"class_type": 1, "data_type": "2", "country_level2": ["US","CA"]}`

Compare total counts, top advertisers, media distribution.

### Market overview combo (multi-call)

For a comprehensive market report on a segment:
1. `class_type=1` → geographic distribution
2. `class_type=2` → media channel breakdown
3. `class_type=4` → top advertisers
4. `class_type=5` → top publishers

Combine for a full market intelligence report.

---

## Filter Codes

Use `GET /api/data/filter-options` to get valid codes for:
- `trade_level3` — industry/sub-category codes
- `country_level2` — country codes (use the `ccode` field, e.g. "US", "JP")
- `media_ids` — media channel IDs (use the `ccode` field, e.g. "101" for Adcolony)
- `device` — device type codes (use the `ccode` field, e.g. "1" for Android)

See `references/param-mappings.md` for common country/region mappings.
