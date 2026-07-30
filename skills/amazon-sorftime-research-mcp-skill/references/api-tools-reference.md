# Sorftime MCP 工具参考 (curl 调用格式)

**注意**：Sorftime MCP 使用 SSE 协议，所有工具调用格式如下：

```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":N,"method":"tools/call","params":{"name":"TOOL_NAME","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

---

## 核心工具

### 1. 产品详情 (product_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_detail","arguments":{"amzSite":"US","asin":"B07PQFT83F"}}}'
```

### 2. 产品搜索 (product_search) - 用于验证ASIN
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"PRODUCT_NAME","page":1}}}'
```

### 3. 用户评论 (product_reviews)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"product_reviews","arguments":{"amzSite":"US","asin":"ASIN","reviewType":"Both"}}}'
```
- reviewType: "Positive" (4-5星), "Negative" (1-3星), "Both" (全部)

### 4. 流量关键词 (product_traffic_terms)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"product_traffic_terms","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 5. 竞品关键词布局 (competitor_product_keywords)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"competitor_product_keywords","arguments":{"amzSite":"US","asin":"ASIN"}}}'
```

### 6. 产品趋势 (product_trend)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"product_trend","arguments":{"amzSite":"US","asin":"ASIN","productTrendType":"SalesVolume"}}}'
```
- productTrendType: "SalesVolume" (销量), "SalesAmount" (销售额), "Price" (价格), "Rank" (排名)

### 7. 关键词详情 (keyword_detail)
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":7,"method":"tools/call","params":{"name":"keyword_detail","arguments":{"amzSite":"US","keyword":"KEYWORD"}}}'
```

---

## 并发请求最佳实践

为了提高效率，可以同时发起多个请求：

```bash
# 并发获取所有数据（使用不同的 id）
curl ... '{"id":1,...}' &
curl ... '{"id":2,...}' &
curl ... '{"id":3,...}' &
curl ... '{"id":4,...}' &
curl ... '{"id":5,...}' &
curl ... '{"id":6,...}' &
wait
```

或在同一行使用 `&&` 连接（顺序执行）：
```bash
(curl ... '{"id":1,...}' && curl ... '{"id":2,...}' && ...)
```

---

## 支持的亚马逊站点

US, GB, DE, FR, IN, CA, JP, ES, IT, MX, AE, AU, BR, SA

---

## 故障排查

### 问题1：ASIN 未找到

**现象**：返回 "未查询到对应产品，请检查传入产品ASIN"

**解决方案**：
1. 使用 product_search 工具验证：
```bash
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"product_search","arguments":{"amzSite":"US","keyword":"ASIN_OR_KEYWORD","page":1}}}'
```

2. 检查 ASIN 格式是否正确（10位字母数字）
3. 确认产品是否在该站点上架
4. 尝试其他站点

### 问题2：数据保存到临时文件

**现象**：返回 "Output too large... Full output saved to: ..."

**解决方案**：
```bash
# 使用 Read 工具读取临时文件
Read <file_path>
```

### 问题3：Unicode 转义字符

**现象**：中文显示为 `\u4EA7\u54C1ASIN\u7801`

**解决方案**：
- 大多数现代工具会自动解码
- 如果需要手动解码，使用 Python：
```python
import json
print(json.loads('"\\u4EA7\\u54C1ASIN\\u7801"'))
```

### 问题4：MCP 工具不响应

**现象**：curl 请求超时或无响应

**解决方案**：
1. 检查网络连接
2. 验证 API Key 是否有效
3. 检查 Sorftime 服务状态：`curl -I https://mcp.sorftime.com`
4. 增加超时时间：`curl --max-time 30`

### 问题5：部分数据缺失

**现象**：评论、趋势数据返回 "没有相关数据"

**解决方案**：
- 新产品可能没有历史趋势数据
- 部分产品可能没有评论数据
- 继续使用可用数据进行分析，标注缺失部分
