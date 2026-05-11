---
name: pipeline-cancel
description: 取消流水线执行。当用户需要停止流水线、中止执行时使用此功能。

触发关键词："取消流水线"、"停止流水线"、"中止执行"
---

# 流水线取消

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

取消正在执行的流水线。

## 使用方式

```bash
python -m scripts/main cancel <pipeline_log_id>
```

## API接口

- **路径**: POST /rest/openapi/pipeline/cancel
- **方法**: POST
- **Content-Type**: application/json

## 请求参数

### 请求体: PipelineCanelDto

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineLogId | Long | 是 | 流水线执行记录ID | `10001` |

## 请求示例

```json
{
  "pipelineLogId": 10001
}
```

## 响应示例

**成功响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": true,
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应**:
```json
{
  "code": -1,
  "message": "取消流水线失败: 流水线已结束或已取消",
  "data": false,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 404 | 流水线不存在 |
| 429 | 请求过于频繁（触发限流） |

## 业务场景示例

**场景: 取消错误的部署**
```bash
curl -X POST "https://api.example.com/rest/openapi/pipeline/cancel" \
  -H "Content-Type: application/json" \
  -H "X-User-Account: your_domain_account" \
  -d '{"pipelineLogId": 10001}'
```

## 注意事项

1. 只能取消正在执行的流水线
2. 取消后无法恢复执行
3. 参数使用的是 **pipelineLogId**（执行记录ID），而非pipelineId
4. pipelineLogId为Long类型
