# Sorftime MCP API 接口文档

## 调用方式
```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{...}}}'
```

---

## 一、产品相关接口

### 1.1 产品详情 (product_detail)
**调用消耗**: 1

**用途**: 查询亚马逊电商平台上产品的详情数据

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | 是 | 亚马逊站点 US/GB/DE/FR/IN/CA/JP/ES/IT/MX/AE/AU/BR/SA |
| asin | string | 是 | 产品ASIN |

**返回数据**: 标题、价格、评分、评论数、品牌、类目、排名、销量等

---

### 1.2 产品子体明细 (product_variations)
**调用消耗**: 1

**用途**: 查询亚马逊电商平台产品的子体明细

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN（仅支持单ASIN） |

---

### 1.3 产品历史趋势 (product_trend)
**调用消耗**: 1

**用途**: 查询产品的历史趋势数据，支持月销量/月销额/价格/排名趋势

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN |
| productTrendType | string | 否 | 月销量趋势/月销额趋势/价格趋势/所属大类排名趋势 |

---

### 1.4 产品评论 (product_reviews)
**调用消耗**: 1

**用途**: 查询产品近一年的用户留评，最多返回100条

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN |
| reviewType | string | 否 | 全部（不限星级）/积极评论（4-5星）/消极评论（1-3星） |

---

### 1.5 产品流量关键词 (product_traffic_terms)
**调用消耗**: 1

**用途**: 产品反查关键词，返回产品在哪些关键词前3页中曝光

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN |
| page | int | 否 | 页码索引，默认第1页，每页50条 |

---

### 1.6 竞品关键词布局 (competitor_product_keywords)
**调用消耗**: 1

**用途**: 获取竞品在各核心关键词下的曝光位置（自然曝光）

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN |
| page | int | 否 | 页码索引，默认第1页 |

---

### 1.7 产品关键词排名趋势 (product_keyword_rank_trend)
**调用消耗**: 1

**用途**: 产品在指定关键词下曝光的排名趋势

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| asin | string | 是 | 产品ASIN |
| keyword | string | 是 | 关键词 |
| page | int | 否 | 页码索引，默认第1页 |

---

### 1.8 产品搜索 (product_search)
**调用消耗**: 1

**用途**: 搜索或筛选亚马逊产品，支持多维度筛选实现选品功能

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchName | string | 否 | 搜索产品名称 |
| brand | string | 否 | 筛选品牌 |
| delivery_type | string | 否 | 发货方式 |
| month_sales_volume_range | string | 否 | 月销量范围[x,y] |
| price_range | string | 否 | 价格范围[x,y] |
| property_name | string | 否 | 标题或属性包含词 |
| ratings_count_range | string | 否 | 评论数量范围[x,y] |
| ratings_range | string | 否 | 星级范围[x,y] |
| seasonal_popular_product | string | 否 | 热销旺季产品 |
| seller_name | string | 否 | 卖家名称 |
| subcategory_rank_range | string | 否 | 细分类目排名范围[x,y] |
| variation_count_range | string | 否 | 子体数量范围[x,y] |
| sortby_potential_index | string | 否 | 按潜力指数排序 |

---

### 1.9 潜力产品搜索 (potential_product_search)
**调用消耗**: 1

**用途**: 搜索亚马逊平台上的潜力产品

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 支持的站点 US/GB/DE |
| searchName | string | 否 | 产品名称 |
| price_range | string | 否 | 价格范围[x,y] |
| month_sales_volume_range | string | 否 | 月销量范围[x,y] |
| delivery_type | string | 否 | 发货方式 |

---

## 二、类目相关接口

### 2.1 类目名称搜索 (category_name_search)
**调用消耗**: 1

**用途**: 基于名称查询细分类目市场，返回nodeid和name

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchName | string | 是 | 类目市场名称 |

---

### 2.2 类目树结构 (category_tree)
**调用消耗**: 5

**用途**: 查询类目产品的特点

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchName | string | 是 | 类目名称 |

---

### 2.3 细分类目报告 (category_report)
**调用消耗**: 1

**用途**: 细分类目实时数据报告，基于Top100产品统计

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| nodeId | string | 否 | 细分类目nodeid |

---

### 2.4 细分类目历史报告 (category_history_report)
**调用消耗**: 1

**用途**: 细分类目历史指定时间段数据报告

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| nodeId | string | 否 | 细分类目nodeid |
| startDate | string | 是 | 起始时间(yyyy-MM-dd) |
| endDate | string | 否 | 截止时间，最长40天 |

---

### 2.5 类目趋势 (category_trend)
**调用消耗**: 1

**用途**: 查询类目市场趋势数据，基于Top100统计

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| nodeId | string | 是 | 细分类目nodeid |
| trendIndex | string | 是 | 趋势类型（见下方） |

**趋势类型 (trendIndex)**:
- 类目月销量趋势
- 品牌数量趋势
- 卖家数量趋势
- 平均售价趋势
- 平均评论数量趋势
- 平均星级趋势
- 上架3个月内新品销量占比趋势
- 亚马逊自营销量占比趋势
- 销量前3的产品销量占比趋势
- 销量前3的品牌销量占比趋势
- 销量前3的卖家销量占比趋势

---

### 2.6 类目市场搜索 (category_market_search)
**调用消耗**: 1

**用途**: 查询或搜索细分类目市场

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchName | string | 否 | 类目市场名称 |
| month_sales_volume_range | string | 否 | 月销量范围[x,y] |
| ratings_range | string | 否 | 星级范围[x,y] |
| ratings_count_range | string | 否 | 评论数范围[x,y] |
| price_range | string | 否 | 平均销售价范围[x,y] |
| seasonal_popular_product | string | 否 | 热销旺季 |
| top3Product_sales_share | string | 否 | Top3产品销量占比[x,y](0-1) |
| amazonOwned_sales_share | string | 否 | 亚马逊自营占比[x,y](0-1) |
| top100_top400_sales_share | string | 否 | Top100在Top400占比[x,y](0-1) |
| newproduct_sales_share | string | 否 | 新品销量占比[x,y](0-1) |

---

### 2.7 类目核心关键词 (category_keywords)
**调用消耗**: 1

**用途**: 查询细分类目市场的核心关键词

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| nodeId | string | 是 | 细分类目nodeid |
| page | int | 否 | 页码索引，默认第1页 |

---

## 三、关键词相关接口

### 3.1 关键词详情 (keyword_detail)
**调用消耗**: 1

**用途**: 查询热搜关键词详情

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| keyword | string | 是 | 查询的关键词 |

---

### 3.2 关键词搜索结果 (keyword_search_result)
**调用消耗**: 1

**用途**: 查询关键词搜索结果自然位产品清单

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchKeyword | string | 是 | 查询的关键词 |
| page | int | 否 | 页码索引，默认第1页 |

---

### 3.3 关键词历史趋势 (keyword_trend)
**调用消耗**: 1

**用途**: 查询关键词历史趋势（搜索量/搜索排名/CPC价格）

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchKeyword | string | 是 | 查询的关键词 |

---

### 3.4 关键词延伸词 (keyword_related_words)
**调用消耗**: 1

**用途**: 查询关键词的延伸词，用于发现长尾词

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | 亚马逊站点 |
| searchKeyword | string | 是 | 查询的关键词 |
| page | int | 否 | 页码索引，默认第1页 |

---

## 四、关键词词库管理接口

### 4.1 添加关键词收藏 (add_keyword)
**调用消耗**: 1

**参数**: site, keyword, dict(可选)

---

### 4.2 移动关键词到收藏夹 (move_keyword)
**调用消耗**: 1

**参数**: site, keyword, toDict, fromDict(可选)

---

### 4.3 删除关键词收藏 (remove_keyword)
**调用消耗**: 1

**参数**: site, keyword, dict(可选)

---

### 4.4 查询收藏夹列表 (query_keyword_dict_list)
**调用消耗**: 1

**参数**: site, page

---

### 4.5 查询收藏的词 (query_keyword_dict)
**调用消耗**: 1

**参数**: site, dict(可选，all查询全部), page

---

## 五、1688 供货平台接口

### 5.1 1688产品搜索 (products_1688)
**调用消耗**: 1

**用途**: 通过1688平台找产品的采购货源，分析产品采购成本价

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| searchName | string | 是 | 查询的产品名称 |
| page | int | 否 | 页码索引，默认第1页，每页50条 |

---

## 六、TikTok 电商平台接口

### 6.1 TikTok产品搜索 (tiktok_product_search)
**调用消耗**: 1

**用途**: 查询产品在TikTok平台上的相似产品，分析销售情况

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 查询的产品名称 |
| page | int | 是 | 页码索引，默认第1页，每页50条 |

---

### 6.2 TikTok产品详情 (tiktok_product_detail)
**调用消耗**: 1

**用途**: 查询TikTok平台产品详情

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 产品ID |

---

### 6.3 TikTok带货视频 (tiktok_product_videos)
**调用消耗**: 1

**用途**: 查询TikTok平台产品的带货视频

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 产品ID |
| page | int | 是 | 页码索引，默认第1页，每页50条 |

---

### 6.4 TikTok带货达人分析 (tiktok_product_influencers)
**调用消耗**: 1

**用途**: TikTok平台产品的带货达人分析

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 产品ID |

---

### 6.5 TikTok产品趋势 (tiktok_product_trend)
**调用消耗**: 1

**用途**: 查询TikTok平台产品趋势，返回销量、价格、星级、评论数量、新增带货视频数、新增带货达人数

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| productId | string | 是 | 产品ID |

---

### 6.6 TikTok达人搜索 (tiktok_influencer_search)
**调用消耗**: 1

**用途**: 按产品名称搜索相关带货达人

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 搜索的产品名称 |
| page | int | 是 | 页码索引，默认第1页，每页50条 |

---

### 6.7 TikTok类目搜索 (tiktok_category_name_search)
**调用消耗**: 1

**用途**: 按名称搜索TikTok上相关类目市场，返回类目市场名称和nodeid

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| searchName | string | 是 | 搜索的产品名称 |

---

### 6.8 TikTok类目报告 (tiktok_category_report)
**调用消耗**: 1

**用途**: 查询TikTok电商平台指定类目的类目数据报告

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
|amzSite | string | 是 | TikTok站点 US/GB/MY/PH/VN/ID |
| nodeId | string | 是 | 类目市场nodeid，可通过tiktok_category_name_search获得 |

---

## 支持的平台站点

### 亚马逊 (14个站点)
`US`, `GB`, `DE`, `FR`, `IN`, `CA`, `JP`, `ES`, `IT`, `MX`, `AE`, `AU`, `BR`, `SA`

### TikTok (6个站点)
`US`, `GB`, `MY`, `PH`, `VN`, `ID`

### 1688 供货平台
国内批发采购平台

## 调用限制
- 大部分接口调用消耗: 1
- category_tree: 5
- 返回数据为SSE格式，需解析

---

*最后更新: 2026-03-03*
