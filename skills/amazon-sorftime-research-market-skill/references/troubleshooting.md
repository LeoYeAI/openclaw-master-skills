# Product-Research 故障排查指南

## 快速诊断流程

```
问题发生
    ↓
是 API 调用错误? → 查看第2节
    ↓
是数据解析错误? → 查看第3节
    ↓
是编码问题? → 查看第4节
    ↓
其他问题 → 查看第5节
```

---

## 1. 数据采集失败

### 问题: 类目搜索返回 406 错误

**症状**: `HTTP Error 406: Not Acceptable`

**原因**: API 参数名称错误

**解决方案**:
```python
# ❌ 错误写法
client._call('category_search_from_product_name', {
    'amzSite': 'US',
    'productName': 'bluetooth speaker'  # 错误!
})

# ✅ 正确写法
client.search_category_by_product_name('US', 'bluetooth speaker')
# 或直接调用
client._call('category_name_search', {
    'amzSite': 'US',
    'searchName': 'bluetooth speaker'  # 正确!
})
```

### 问题: 找不到类目

**症状**: 返回空列表或 "未查询到对应类目"

**诊断步骤**:
1. 检查关键词拼写
2. 尝试更通用的关键词 (如 "speaker" 而非 "portable bluetooth speaker")
3. 检查站点是否支持该类目

**解决方案**:
```python
# 尝试多个关键词
keywords = ['bluetooth speaker', 'portable speaker', 'wireless speaker', 'speaker']
for kw in keywords:
    result = client.search_category_by_product_name('US', kw)
    if result:
        break
```

---

## 2. API 调用错误

### 问题: "An error occurred invoking 'xxx'"

**原因**: 工具名称不存在

**常用工具名称对照**:

| 功能 | 正确名称 | 错误名称 |
|------|----------|----------|
| 类目搜索 | `category_name_search` | `category_search_from_product_name` ❌ |
| 类目报告 | `category_report` | - |
| 关键词详情 | `keyword_detail` | - |
| 产品详情 | `product_detail` | - |

### 问题: 认证失败

**症状**: `Authentication required`

**检查**:
```bash
# 验证 API Key
curl "https://mcp.sorftime.com?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

**解决方案**:
1. 检查 `.mcp.json` 文件
2. 确认 URL 格式: `https://mcp.sorftime.com?key=XXX`
3. 获取新 API Key: https://sorftime.com/zh-cn/mcp

---

## 3. 数据解析错误

### 问题: Top100 数据解析失败

**症状**: `KeyError: 'Top100产品'` 或产品列表为空

**原因**: Sorftime 返回格式可能有多种变体

**解决方案**:
```python
def safe_extract_products(data):
    """安全提取产品列表"""
    if not isinstance(data, dict):
        return []

    # 尝试多个可能的键名
    products = (
        data.get('Top100产品') or
        data.get('top100_products') or
        data.get('products') or
        data.get('productList') or
        data.get('product_list') or
        []
    )

    return products
```

### 问题: SSE 响应解析失败

**症状**: `API 返回数据解析失败`

**调试方法**:
```python
# 保存原始响应用于调试
import os
debug_file = os.path.join(output_dir, 'raw_response.txt')
with open(debug_file, 'w', encoding='utf-8') as f:
    f.write(response)

# 检查响应格式
print("原始响应前500字符:")
print(response[:500])
```

---

## 4. 编码问题

### 问题: 中文显示为乱码

**症状**: `äº§å` 或类似字符

**解决方案**: 使用 `api_client.py` 中的修复函数

```python
from api_client import fix_mojibake

fixed_text = fix_mojibake(bad_text)
```

### 问题: Unicode 转义未解码

**症状**: `\u4ea7\u54c1` 格式

**解决方案**:
```python
import codecs

decoded = codecs.decode(escaped_text, 'unicode-escape')
```

---

## 5. 其他常见问题

### 问题: 模块导入失败

**症状**: `ModuleNotFoundError: No module named 'xxx'`

**解决方案**:
```python
# 确保脚本目录在 Python 路径中
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from api_client import SorftimeClient
```

### 问题: 文件保存失败

**症状**: `FileNotFoundError` 或权限错误

**解决方案**:
```python
# 确保目录存在
os.makedirs(output_dir, exist_ok=True)

# 使用绝对路径
output_path = os.path.abspath(output_dir)
```

---

## 6. 调试技巧

### 启用详细日志

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 在代码中添加日志
logger.debug(f"API 请求: {method_name} {arguments}")
logger.info(f"获取到 {len(products)} 个产品")
```

### 分步测试

```python
# 测试 API 连接
client = SorftimeClient()
result = client._call('category_name_search', {
    'amzSite': 'US',
    'searchName': 'speaker'
})
print(json.dumps(result, ensure_ascii=False, indent=2))
```

### 使用 curl 直接测试

```bash
# 测试类目搜索
curl -s -X POST "https://mcp.sorftime.com?key=YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "category_name_search",
      "arguments": {
        "amzSite": "US",
        "searchName": "speaker"
      }
    }
  }'
```

---

## 7. 获取帮助

1. 检查 `SKILL.md` 中的执行流程说明
2. 查看 `api_client.py` 中的方法文档
3. 参考 `category-selection` skill 的类似实现
4. 在项目根目录运行测试命令验证环境

---

*最后更新: 2026-03-19*
