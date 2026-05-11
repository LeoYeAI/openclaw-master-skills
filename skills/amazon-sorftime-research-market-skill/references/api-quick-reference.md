# Sorftime MCP API 快速参考

## 品类选品分析常用接口

### 1. category_name_search - 搜索类目

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"category_name_search","arguments":{"amzSite":"US","searchName":"Sofas"}}}'
```

**返回关键数据**: `NodeId` (用于后续调用)

---

### 2. category_report - 类目报告 (核心)

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"category_report","arguments":{"amzSite":"US","nodeId":"3733551"}}}'
```

**返回数据**:
- `Top100产品[]`: 产品列表 (ASIN, 标题, 价格, 月销量, 星级, 品牌, 评论数, 卖家来源等)
- `类目统计报告`: 统计数据

**关键统计字段**:
| 字段名 | 说明 | 用途 |
|--------|------|------|
| `top100产品月销量` | Top100 总销量 | 市场规模 |
| `top100产品月销额` | Top100 总销额 | 市场规模 |
| `average_price` | 平均价格 | 定价参考 |
| `top3_brands_sales_volume_share` | Top3 品牌占比 | 竞争集中度 |
| `amazonOwned_sales_volume_share` | Amazon 自营占比 | 平台压力 |
| `low_reviews_sales_volume_share` | 低评论产品占比 | 新品机会 |

---

### 3. product_detail - 产品详情

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B0DDTCQGTR"}}}'
```

**返回关键数据**: 标题, 主图URL, 价格, 星级, 评论数, 品牌, 上线日期, 月销量, 产品描述等

---

### 4. category_keywords - 类目关键词

```bash
curl -s -X POST "https://mcp.sorftime.com?key={API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"category_keywords","arguments":{"amzSite":"US","nodeId":"3733551","page":1}}}'
```

**返回关键数据**:
- `关键词`: 关键词
- `周搜索排名`: 搜索排名
- `月搜索量`: 月搜索量
- `cpc精准竞价`: PPC 竞价

---

## SSE 响应处理

### 响应格式
```
event: message
data: {"result":{"content":[{"type":"text","text":"..."}}]}
```

### Python 解码示例
```python
import codecs

# 解码 Unicode 转义
decoded = codecs.decode(encoded_text, 'unicode-escape')
```

---

## 支持的站点

| 代码 | 站点 |
|------|------|
| US | 美国 |
| GB | 英国 |
| DE | 德国 |
| FR | 法国 |
| CA | 加拿大 |
| JP | 日本 |
| ES | 西班牙 |
| IT | 意大利 |
