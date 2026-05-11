---
name: pipeline-detail
description: 查询流水线详情。当用户需要查看流水线配置、获取流水线信息时使用此功能。

触发关键词："流水���详情"、"查看流水线配置"、"获取流水线信息"、"编辑流水线"
---

# 流水线详情查询

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

编辑流水线时获取流水线配置参数，包含完整的流水线配置信息。

## 使用方式

```bash
python -m scripts/main detail <pipeline_id>
```

## API接口

- **路径**: GET /rest/openapi/pipeline/edit/{pipelineId}
- **方法**: GET

## 请求参数

### 路径参数

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| pipelineId | String | 是 | 流水线ID | `pipe-abc123` |

## 响应示例

**成功响应**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "pipelineId": "pipe-abc123",
    "name": "订单服务构建流水线",
    "spaceId": 1001,
    "aliasId": "PIPE001",
    "sources": [
      {
        "id": "src-001",
        "name": "order-service",
        "defaultBranch": "master",
        "data": {
          "sourceType": "code",
          "repoType": "gitlab",
          "repoUrl": "https://gitlab.example.com/order/service.git",
          "branch": "master",
          "workPath": "./"
        }
      }
    ],
    "stages": [
      {
        "name": "构建阶段",
        "nodeType": "custom-stage-node",
        "id": "stage-001",
        "steps": [...]
      }
    ],
    "triggerInfo": {
      "triggerType": 0
    },
    "timeoutDuration": "2H",
    "buildPlatform": "linux"
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**失败响应**:
```json
{
  "code": -1,
  "message": "获取流水线参数失败: 流水线不存在",
  "data": null,
  "requestId": "550e8400-e29b-41d4-a716-446655440001"
}
```

## 响应字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| pipelineId | String | 流水线ID |
| name | String | 流水线名称 |
| spaceId | Long | 空间ID |
| aliasId | String | 别名ID |
| sources | List | 代码源配置 |
| stages | List | 阶段配置 |
| triggerInfo | Object | 触发信息 |
| customParameters | List | 自定义参数模板 |
| timeoutDuration | String | 超时时间 |
| buildPlatform | String | 构建平台 |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 404 | 流水线不存在 |
| 429 | 请求过于频繁（触发限流） |

## 注意事项

1. 该接口返回完整的PipelineParams结构
2. 用于编辑流水线时获取原始配置
3. 详细字段说明参见pipeline-create.md中的PipelineParams字段说明
