# Sorftime API 快速参考 (Product-Research)

## API 端点

```
https://mcp.sorftime.com?key={API_KEY}
```

## 请求格式

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "{工具名称}",
    "arguments": {
      "amzSite": "US",
      ...
    }
  }
}
```

## 响应格式 (SSE)

```
event: message
data: {"result":{"content":[{\"type\":\"text\",\"text\":\"{数据}\"}],\"isError\":false},"id":1,\"jsonrpc\":\"2.0\"}

```

---

## 常用 API 工具

### 1. category_name_search

**用途**: 按名称搜索类目，获取 NodeId

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 (US, GB, DE, etc.) |
| searchName | string | ✓ | 类目名称关键词 |

**示例**:
```bash
curl -s -X POST "https://mcp.sorftime.com?key={KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "category_name_search",
      "arguments": {
        "amzSite": "US",
        "searchName": "bluetooth speaker"
      }
    }
  }'
```

**响应**:
```json
[
  {
    "nodeId": "7073956011",
    "Name": "Portable Bluetooth Speakers"
  },
  {
    "nodeId": "12097477011",
    "Name": "Outdoor Speakers"
  }
]
```

---

### 2. category_report

**用途**: 获取类目 Top100 产品和统计数据

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 |
| nodeId | string | ✓ | 类目 Node ID |

**示例**:
```python
client.get_category_report("US", "7073956011")
```

**响应结构**:
```json
{
  "Top100产品": [
    {
      "ASIN": "B0XXXXXXXX",
      "标题": "...",
      "月销量": "10000",
      "月销额": "500000.00",
      "品牌": "JBL",
      "价格": 49.99,
      "评论数": 5000,
      "星级": 4.7
    }
  ],
  "类目统计报告": {
    "nodeid": "7073956011",
    "类目名称": "Portable Bluetooth Speakers",
    "top100产品月销量": "279733",
    "top100产品月销额": "19842968.40",
    "top3_product_sales_volume_share": "19.66%"
  }
}
```

---

### 3. category_trend

**用途**: 获取类目趋势数据

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 |
| nodeId | string | ✓ | 类目 Node ID |
| trendIndex | string | ✗ | 趋势类型 (默认: NewProductSalesAmountShare) |

**trendIndex 选项**:
- `NewProductSalesAmountShare` - 新品销量占比
- `NewProductProductShare` - 新品数量占比
- `BrandConcentration` - 品牌集中度
- `PriceDistribution` - 价格分布

**示例**:
```python
trend = client.get_category_trend("US", "7073956011", "NewProductSalesAmountShare")
```

**响应**:
```json
[
  "2024年03月=3.32",
  "2024年04月=1.98",
  ...
]
```

---

### 4. keyword_detail

**用途**: 获取关键词详情

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 |
| keyword | string | ✓ | 关键词 |

**示例**:
```python
detail = client.get_keyword_detail("US", "bluetooth speaker")
```

**响应结构**:
```json
{
  "搜索量": "50000",
  "CPC": "1.50",
  "竞价": "8",
  "自然位产品": [...]
}
```

---

### 5. product_detail

**用途**: 获取单个产品详情

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 |
| asin | string | ✓ | 产品 ASIN |

---

### 6. product_reviews

**用途**: 获取产品评论

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| amzSite | string | ✓ | 站点代码 |
| asin | string | ✓ | 产品 ASIN |
| reviewType | string | ✗ | 评论类型 (Both/Positive/Negative) |

---

## Python 客户端使用

### 基本用法

```python
from api_client import SorftimeClient

client = SorftimeClient()

# 搜索类目
categories = client.search_category_by_product_name("US", "bluetooth speaker")
node_id = categories[0]['nodeId']

# 获取 Top100
top100 = client.get_category_report("US", node_id)
products = top100.get('Top100产品', [])

# 获取趋势
trend = client.get_category_trend("US", node_id)

# 获取关键词详情
keyword_data = client.get_keyword_detail("US", "bluetooth speaker")
```

### 批量调用

```python
# 并发获取多个产品详情
asins = ["B0XXX1", "B0XXX2", "B0XXX3"]
details = []
for asin in asins:
    try:
        detail = client.get_product_detail("US", asin)
        details.append(detail)
    except Exception as e:
        print(f"Failed for {asin}: {e}")
```

---

## 支持的站点

| 代码 | 市场 |
|------|------|
| US | 美国亚马逊 |
| GB | 英国亚马逊 |
| DE | 德国亚马逊 |
| FR | 法国亚马逊 |
| IT | 意大利亚马逊 |
| ES | 西班牙亚马逊 |
| CA | 加拿大亚马逊 |
| JP | 日本亚马逊 |
| MX | 墨西哥亚马逊 |
| AE | 阿联酋亚马逊 |
| AU | 澳大利亚亚马逊 |
| BR | 巴西亚马逊 |
| SA | 沙特阿拉伯亚马逊 |

---

## 数据类型说明

### 月销量/月销额

- 类型: `string` (需要转换为数字)
- 示例: `"28908"`, `"1443954.60"`
- 转换: `float(value)`

### 价格

- 类型: `float` 或 `string`
- 示例: `49.95`, `"29.99"`

### 评论数

- 类型: `int` 或 `string`
- 示例: `14558`, `"5000"`

---

## 错误代码

| HTTP 状态 | 含义 | 解决方案 |
|-----------|------|----------|
| 200 | 成功 | - |
| 406 | 参数错误 | 检查参数名称和格式 |
| 401 | 认证失败 | 检查 API Key |
| 500 | 服务器错误 | 稍后重试 |

---

*最后更新: 2026-03-19*
