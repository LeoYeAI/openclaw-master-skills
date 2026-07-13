# 品类选品专用接口参考

本文档列出品类选品分析相关的核心接口及调用示例。

---

## 一、类目搜索与确认

### 1. 类目名称搜索 - category_name_search

**用途**: 根据品类名称查找对应的类目nodeid

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"site":"US","searchName":"sofas"}}}'
```

**返回数据示例**:
```
类目名称 | nodeId
---------|---------
Sofas | 3733551
Sofa Slipcovers | 1234567
Bean Bag Chairs | 2345678
```

---

## 二、市场趋势数据 (11个指标)

### 趋势指标列表

| ID | 趋势类型 | trendIndex参数 | 用途 |
|----|----------|---------------|------|
| 1 | 类目月销量趋势 | 类目月销量趋势 | 市场规模评分 |
| 2 | 品牌数量趋势 | 品牌数量趋势 | 竞争烈度评分 |
| 3 | 卖家数量趋势 | 卖家数量趋势 | 竞争烈度评分 |
| 4 | 平均售价趋势 | 平均售价趋势 | 利润空间评分 |
| 5 | 平均评论数量趋势 | 平均评论数量趋势 | 进入壁垒评分 |
| 6 | 平均星级趋势 | 平均星级趋势 | 市场成熟度 |
| 7 | 新品销量占比趋势 | 上架3个月内新品销量占比趋势 | 进入壁垒评分 |
| 8 | 亚马逊自营销量占比 | 亚马逊自营销量占比 | 竞争烈度评分 |
| 9 | Top3产品销量占比 | 销量前3的产品销量占比趋势 | 市场集中度 |
| 10 | Top3品牌销量占比 | 销量前3的品牌销量占比趋势 | 市场集中度 |
| 11 | Top3卖家销量占比 | 销量前3的卖家销量占比趋势 | 市场集中度 |

### 调用示例

```bash
# 并发调用11个趋势接口
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_trend","arguments":{"site":"US","nodeId":"3733551","trendIndex":"类目月销量趋势"}}}' &

curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"category_trend","arguments":{"site":"US","nodeId":"3733551","trendIndex":"品牌数量趋势"}}}' &

# ... 继续其他9个接口
```

---

## 三、Top100产品数据

### 类目报告 - category_report

**用途**: 获取品类Top100产品列表

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":12,"method":"tools/call","params":{"name":"category_report","arguments":{"site":"US","nodeId":"3733551"}}}'
```

**返回数据字段**:
| 字段 | 说明 |
|------|------|
| ASIN | 产品ASIN |
| Title | 产品标题 |
| Brand | 品牌 |
| Price | 价格 |
| Rating | 评分 |
| ReviewCount | 评论数 |
| MonthlySales | 月销量 |

---

## 四、产品详情批量获取

### 产品详情 - product_detail

**用途**: 获取单个产品详细信息

```bash
# 需要对100个ASIN逐个调用
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":100,"method":"tools/call","params":{"name":"product_detail","arguments":{"site":"US","asin":"B07PWTJ4H1"}}}'
```

**批量获取策略**:
- 并发调用，每次最多10个
- 使用不同的id (100-199)
- 失败的ASIN跳过，记录日志

---

## 五、类目关键词

### 类目核心关键词 - category_keywords

**用途**: 获取类目热搜关键词

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":200,"method":"tools/call","params":{"name":"category_keywords","arguments":{"site":"US","nodeId":"3733551","page":1}}}'
```

**返回数据字段**:
| 字段 | 说明 |
|------|------|
| keyword | 关键词 |
| searchVolume | 月搜索量 |
| recommendBid | 推荐竞价 |

---

## 六、供应链分析

### 1688产品搜索 - products_1688

**用途**: 获取1688采购价格

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":300,"method":"tools/call","params":{"name":"products_1688","arguments":{"searchName":"沙发","page":1}}}'
```

---

## 七、TikTok跨平台分析

### TikTok产品搜索 - tiktok_product_search

**用途**: 搜索TikTok相似产品

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":400,"method":"tools/call","params":{"name":"tiktok_product_search","arguments":{"site":"US","searchName":"sofa","page":1}}}'
```

---

## 数据收集检查清单

- [ ] Step 1.1: 类目搜索，获取nodeid
- [ ] Step 1.2: 11个市场趋势指标 (并发)
- [ ] Step 1.3: Top100产品列表
- [ ] Step 1.4: 100个产品详情 (并发×10)
- [ ] Step 1.5: 类目关键词 (可选)
- [ ] Step 1.6: 1688采购价格 (可选)
- [ ] Step 1.7: TikTok产品搜索 (可选)

---

## 五维评分计算参考

### 1. HHI指数计算

```
HHI = Σ(各品牌市场份额百分比)²

示例:
品牌A: 12.56% → 12.56² = 157.75
品牌B: 9.11%  → 9.11²  = 82.99
品牌C: 3.55%  → 3.55²  = 12.60
...
HHI = 157.75 + 82.99 + 12.60 + ... = 167.71
```

### 2. CR3集中度计算

```
CR3 = Top3品牌市场份额之和

示例:
品牌A: 12.56%
品牌B: 9.11%
品牌C: 3.55%
CR3 = 12.56 + 9.11 + 3.55 = 25.22%
```

### 3. 同比增长率计算

```
同比增长率 = (本期销量 - 去年同期销量) / 去年同期销量 × 100%

示例:
2026年2月: 1233
2025年2月: 1047
增长率 = (1233 - 1047) / 1047 × 100% = 17.76%
```

---

*最后更新: 2026-03-03*
