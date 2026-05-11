# Parameter Mapping Reference / 参数映射参考表

## Creative Type (creative_team) / 创意组类型

| User says (EN) | User says (CN) | Code | Meaning |
|---|---|---|---|
| image, single image | 图片、单图 | "100" | Single image |
| double image | 双图 | "200" | Double image |
| triple image | 三图 | "300" | Triple image |
| multi-image | 多图 | "400" | Multi-image (3+) |
| video | 视频 | "010" | Video |
| playable, playable ad | 试玩、试玩广告、playable | "001" | Playable ad |
| image + video | 单图+视频 | "110" | Image + video combo |
| double image + video | 双图+视频 | "210" | Double image + video |
| video + playable | 视频+试玩 | "011" | Video + playable |
| all images | 所有图片 | ["100","200","300","400"] | All image types |

**Combination rule:** Three-digit code represents "image_count - video - playable". E.g. "110" = 1 image + video + no playable.

## Region → Country Code Mapping / 地区 → 国家代码映射

| Region (EN) | Region (CN) | Country Codes |
|---|---|---|
| Southeast Asia | 东南亚 | TH, VN, ID, MY, PH, SG, MM, KH, LA, BN |
| South Asia | 南亚 | IN, PK, BD, LK, NP, BT, MV |
| East Asia | 东亚 | JP, KR, CN, TW, HK, MO |
| Japan & Korea | 日韩 | JP, KR |
| HK/Macau/Taiwan | 港澳台 | HK, MO, TW |
| North America | 北美 | US, CA |
| United States | 美国 | US |
| Europe | 欧洲 | GB, DE, FR, IT, ES, NL, PL, SE, NO, DK, FI, AT, CH, BE, PT, IE, CZ, RO, HU, GR |
| Western Europe | 西欧 | GB, DE, FR, IT, ES, NL, BE, AT, CH, PT, IE |
| Northern Europe | 北欧 | SE, NO, DK, FI, IS |
| Middle East | 中东 | SA, AE, QA, KW, BH, OM, IL, TR, EG, JO, LB, IQ |
| Latin America | 拉美 | BR, MX, AR, CO, CL, PE, VE, EC |
| Africa | 非洲 | ZA, NG, KE, EG, GH, TZ, ET, MA |
| Oceania | 大洋洲 | AU, NZ |
| CIS/Eastern Europe | 独联体/东欧 | RU, UA, KZ, BY, UZ, GE, AZ, AM |
| Global (no filter) | 全球（无需过滤） | Omit country_ids parameter |

### Common Country Quick Reference / 常见单个国家速查

| Country (EN) | Country (CN) | Code |
|---|---|---|
| United States | 美国 | US |
| United Kingdom | 英国 | GB |
| Japan | 日本 | JP |
| South Korea | 韩国 | KR |
| India | 印度 | IN |
| Brazil | 巴西 | BR |
| Germany | 德国 | DE |
| France | 法国 | FR |
| Indonesia | 印尼 | ID |
| Thailand | 泰国 | TH |
| Vietnam | 越南 | VN |
| Philippines | 菲律宾 | PH |
| Malaysia | 马来西亚 | MY |
| Singapore | 新加坡 | SG |
| Saudi Arabia | 沙特 | SA |
| UAE | 阿联酋 | AE |
| Turkey | 土耳其 | TR |
| Australia | 澳大利亚 | AU |
| Canada | 加拿大 | CA |
| Mexico | 墨西哥 | MX |
| Russia | 俄罗斯 | RU |
| Spain | 西班牙 | ES |
| Italy | 意大利 | IT |
| Netherlands | 荷兰 | NL |
| Poland | 波兰 | PL |
| Egypt | 埃及 | EG |
| South Africa | 南非 | ZA |
| New Zealand | 新西兰 | NZ |

## Sort Options / 排序方式

| User says (EN) | User says (CN) | sort_field | sort_rule | Meaning |
|---|---|---|---|---|
| newest, by date (default) | 最新、按时间（默认） | "3" | "desc" | First seen descending |
| oldest, date ascending | 最早、时间正序 | "3" | "asc" | First seen ascending |
| most relevant, relevance | 最相关、相关性 | "11" | "desc" | By relevance |
| most popular, most impressions | 最热、曝光最多 | "15" | "desc" | Est. impressions descending |
| least impressions | 曝光最少 | "15" | "asc" | Est. impressions ascending |
| longest running | 投放最久、持续时间最长 | "4" | "desc" | Days active descending |
| shortest running | 投放最短 | "4" | "asc" | Days active ascending |

## Date Range Calculation / 时间范围计算

| User says (EN) | User says (CN) | Calculation |
|---|---|---|
| last week / last 7 days | 最近一周 / 近7天 | start_date = today - 7, end_date = today |
| last 2 weeks / last 14 days | 最近两周 / 近14天 | start_date = today - 14, end_date = today |
| last month / last 30 days (default) | 最近一个月 / 近30天（默认） | start_date = today - 30, end_date = today |
| last 3 months / last 90 days | 最近三个月 / 近90天 | start_date = today - 90, end_date = today |
| previous month | 上个月 | start_date = 1st of last month, end_date = last day of last month |
| today | 今天 | start_date = end_date = today |
| YYYY-MM-DD ~ YYYY-MM-DD | YYYY-MM-DD ~ YYYY-MM-DD | Use the exact dates provided |

**Date format:** YYYY-MM-DD (e.g. 2026-03-10)

## Page Size / 每页数量

| User says (EN) | User says (CN) | page_size |
|---|---|---|
| default | 默认 | 20 |
| show more | 多看一些 | 40 |
| maximum | 最多 | 60 (limit) |
| show fewer / brief | 少看几条 / 简要 | 10 |
