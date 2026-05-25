# Report Source Notes

## Primary Sources

- Report list API: https://www.iresearch.com.cn/api/products/GetReportList
- Report detail page: https://report.iresearch.cn/report/YYYYMM/NNNN.shtml
- Online reader page: https://report.iresearch.cn/report_pdf.aspx?id=NNNN
- QuestMobile report listing page: https://www.questmobile.com.cn/research/reports/
- QuestMobile report detail page: https://www.questmobile.com.cn/research/report/NNNN

## List API Parameters

| Parameter | Meaning | Example |
|-----------|---------|---------|
| `fee` | 是否只看免费报告。当前 skill 固定优先 `0` | `0` |
| `date` | 日期过滤，默认空字符串 | `` |
| `lastId` | 翻页游标，下一页用上一页最后一条的 `Id` | `freport.4695` |
| `pageSize` | 每页数量 | `12` |

## Verified Behavior

- The iResearch free-report API works with minimal browser headers and does not require hardcoded cookies
- iResearch pagination uses the last item `Id` from the previous page as the next `lastId`
- Key iResearch JSON fields:

| Field | Meaning |
|-------|---------|
| `Id` | Cursor report ID, for example `freport.4694` |
| `NewsId` | Numeric report ID, for example `4694` |
| `Title` | Report title |
| `Content` | List summary |
| `Keyword` | Keyword array |
| `industry` | Industry label |
| `Uptime` | Publish timestamp |
| `views` | View count |
| `VisitUrl` | Detail page URL |

## QuestMobile Listing Behavior

- QuestMobile exposes a public paginated JSON endpoint:

```text
https://www.questmobile.com.cn/api/v2/report/article-list?version=0&pageSize=6&pageNo=1&industryId=-1&labelId=-1
```

- The listing page embeds this endpoint and its SSR response state
- The endpoint returns paginated data including `currentPage`, `totalPage`, `limit`, and `data`
- Key QuestMobile list fields include:

| Field | HTML Hint |
|-------|-----------|
| `id` | Report ID |
| `title` | Report title |
| `introduction` | Short public summary |
| `publishTime` | Publish date |
| `industryList` | Industry labels |
| `labelList` | Keyword labels |
| `coverImgUrl` | Card cover image |

- The HTML card structure can still be used as a fallback, but the API is the preferred source for deeper pagination

## QuestMobile Detail Behavior

- QuestMobile detail pages are UTF-8 HTML pages
- Useful stable fields include:

| Field | HTML Hint |
|-------|-----------|
| Title | `<h1>` |
| Meta summary | `<meta name="description">` |
| Industry | `行业：<span>...` block |
| Keywords | `关键词：</strong><span>...` block |
| Published date | date span in `dataAndsource` |
| Source | `来源：QuestMobile研究院` |
| Intro summary | `.daoyu` block |
| Section headings | `<h3>` and `<h4>` in the article body |
| Images | `https://ws.questmobile.cn/report/article/images/...png` |

## Encoding

- The iResearch list API is standard UTF-8 JSON
- iResearch detail pages and online reader pages should be decoded as `gb18030`
- QuestMobile listing and detail pages can be decoded as UTF-8

## Detail Page Anchors

The current script relies on these iResearch anchors:

- `<h3>报告简介</h3>`
- `<h3>目录</h3>`
- `<h3>图表目录</h3>`
- `所属行业：`
- `报告类型：`
- `页数：`
- `图表：`
- `在线浏览`

## Online Reader Notes

- The iResearch online reader is an image stream
- Image URLs look like:

```text
https://pic.iresearch.cn/rimgs/4694/1.jpg
https://pic.iresearch.cn/rimgs/4694/2.jpg
```

- The exposed image count may be lower than the reported page count because public image availability can vary

## Recommended Workflow

1. Use the iResearch list API for primary recall and rough ranking
2. Use QuestMobile public report cards as the secondary source pool
2. Use QuestMobile `article-list` pagination for deeper secondary-source coverage
3. Enrich chosen iResearch hits with detail pages, catalog, chart catalog, and online reader images when needed
4. Enrich chosen QuestMobile hits with detail-page intro text, headings, and body images when needed
5. When mixed-source results are shown, group them by source with iResearch first and QuestMobile second
6. Only after those two groups should any other source appear