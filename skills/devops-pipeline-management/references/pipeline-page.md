---
name: pipeline-page
description: 分页查询流水线列表。当用户需要查看工作空间下的流水线、查找流水线ID、搜索流水线时使用此功能。

触发关键词："流水线列表"、"查询流水线"、"流水线查询"、"pipelines"
---

# 流水线列表分页查询

> ⚠️ **大模型执行约束（必须严格遵守）**
>
> **执行铁律**：
> 1. **API调用规范**：任何发生 API 调用的，**必须实际调用 Python 脚本的 API 功能**，禁止模拟或跳过

## 功能描述

分页查询工作空间下的流水线列表，支持按名称模糊搜索、按收藏/创建者筛选。可获取流水线ID用于后续的执行、详情查询等操作。

## 使用方式

```bash
python -m scripts/main pipelines <space_id> [options]
```

## API接口

- **路径**: POST /rest/openapi/pipeline/queryPipelinePage
- **方法**: POST

## 请求参数

### Body 参数 (JSON)

| 字段名 | 类型 | 必填 | 描述 | 示例值 |
|--------|------|------|------|--------|
| spaceId | Long | 是 | 工作空间ID | `1001` |
| pipelineName | String | 否 | 流水线名称（模糊搜索） | `构建` |
| queryFlag | Integer | 否 | 查询标识 | `0` |
| account | String | 否 | 当前登录账号 | `zhangsan` |
| flag | Boolean | 否 | 是否需要关联权限表查询 | `true` |
| pageNum | Integer | 否 | 页码（默认1） | `1` |
| pageSize | Integer | 否 | 每页大小（默认10） | `10` |

### 命令行参数

| 参数 | 说明 | 示例 |
|------|------|------|
| space_id | 工作空间ID（必填） | `133` |
| --name | 流水线名称（模糊搜索） | `--name 构建` |
| --query-flag | 查询标识 | `--query-flag 1` |
| --page-num | 页码 | `--page-num 1` |
| --page-size | 每页大小 | `--page-size 20` |

### queryFlag 查询标识说明

| 值 | 说明 |
|----|------|
| 0 | 全部流水线（默认） |
| 1 | 我收藏的流水线 |
| 2 | 我创建的流水线 |
| 3 | 最后一次由我执行的流水线 |

## 请求示例

**命令行 - 基础查询**:
```bash
python -m scripts/main pipelines 133
```

**命令行 - 按名称搜索**:
```bash
python -m scripts/main pipelines 133 --name 构建
```

**命令行 - 分页查询**:
```bash
python -m scripts/main pipelines 133 --page-num 1 --page-size 20
```

**命令行 - 查询我收藏的流水线**:
```bash
python -m scripts/main pipelines 133 --query-flag 1
```

**API请求体示例**:
```json
{
  "spaceId": 133,
  "pipelineName": "构建",
  "queryFlag": 0,
  "pageNum": 1,
  "pageSize": 10
}
```

## 响应示例

```json
{
  "code": 0,
  "message": "success",
  "data": {
    "total": 50,
    "size": 10,
    "current": 1,
    "pages": 5,
    "records": [
      {
        "id": "4059831ef9ee41d3ad7d7c4c4be567b1",
        "pipelineName": "订单服务构建流水线",
        "pipelineKey": "order-service-build",
        "pipelineAliasId": "PIPE001",
        "pipelineLabel": "[\"Java\", \"Microservice\"]",
        "spaceId": 133,
        "createTime": "2025-01-15T10:00:00",
        "updateTime": "2025-01-15T10:00:00",
        "creator": "zhangsan",
        "creatorName": "张三",
        "store": 0,
        "permissionList": ["edit", "delete", "run"]
      },
      {
        "id": "abc123def456789abcdef0123456789",
        "pipelineName": "用户服务构建流水线",
        "pipelineKey": "user-service-build",
        "pipelineAliasId": "PIPE002",
        "pipelineLabel": "[\"Java\", \"Microservice\"]",
        "spaceId": 133,
        "createTime": "2025-01-14T09:00:00",
        "updateTime": "2025-01-14T09:00:00",
        "creator": "lisi",
        "creatorName": "李四",
        "store": 1,
        "permissionList": ["run"]
      }
    ]
  },
  "requestId": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Page<PipelineTemplateVO> 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| total | Long | 总记录数 |
| size | Long | 每页大小 |
| current | Long | 当前页码 |
| pages | Long | 总页数 |
| records | List | 流水线列表（PipelineTemplateVO） |

## PipelineTemplateVO 字段说明

| 字段名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| id | String | 流水线ID（用于执行、详情查询等操作） | `4059831ef9ee41d3ad7d7c4c4be567b1` |
| pipelineName | String | 流水线名称 | `订单服务构建流水线` |
| pipelineKey | String | 流水线Key | `order-service-build` |
| pipelineAliasId | String | 流水线别名ID | `PIPE001` |
| pipelineLabel | String | 流水线标签（JSON数组字符串） | `["Java", "Microservice"]` |
| spaceId | Long | 空间ID | `133` |
| createTime | LocalDateTime | 创建时间 | `2025-01-15T10:00:00` |
| updateTime | LocalDateTime | 更新时间 | `2025-01-15T10:00:00` |
| creator | String | 创建人（域账号） | `zhangsan` |
| creatorName | String | 创建人（中文姓名） | `张三` |
| store | Integer | 是否已收藏（0-未收藏/1-已收藏） | `0` |
| permissionList | List | 操作权限列表 | `["edit", "delete", "run"]` |

## permissionList 权限说明

| 权限 | 说明 |
|------|------|
| edit | 可编辑流水线配置 |
| delete | 可删除流水线 |
| run | 可执行流水线 |

## 错误码

| 错误码 | 说明 |
|-------|------|
| 0 | 成功 |
| -1 | 通用失败（具体信息见message） |
| 401 | 无API访问权限 |
| 429 | 请求过于频繁（触发限流） |

## 典型使用场景

### 1. 获取流水线ID用于执行

```bash
# 1. 先查询工作空间获取space_id
python -m scripts/main workspaces --name devops

# 2. 查询流水线列表获取pipeline_id
python -m scripts/main pipelines 133

# 3. 使用pipeline_id执行流水线
python -m scripts/main run 4059831ef9ee41d3ad7d7c4c4be567b1
```

### 2. 按名称搜索流水线

```bash
# 搜索包含"构建"关键字的流水线
python -m scripts/main pipelines 133 --name 构建
```

### 3. 查看我收藏的流水线

```bash
python -m scripts/main pipelines 133 --query-flag 1
```

### 4. 查看我创建的流水线

```bash
python -m scripts/main pipelines 133 --query-flag 2
```

## 与执行记录查询的区别

| 功能 | 命令 | 说明 |
|------|------|------|
| 流水线列表查询 | `pipelines <space_id>` | 查询工作空间下的流水线配置列表 |
| 执行记录查询 | `list <pipeline_id>` | 查询某个流水线的历史执行记录 |

## 注意事项

1. **spaceId为必填参数**，可通过 `workspaces` 命令查询获取
2. **id字段（流水线ID）** 是后续操作的关键参数：
   - 用于 `run` 命令执行流水线
   - 用于 `detail` 命令查询流水线详情
   - 用于 `update` 命令更新流水线配置
   - 用于 `delete` 命令删除流水线
   - 用于 `list` 命令查询执行记录
3. **pipelineName 支持模糊搜索**，不需要完整匹配
4. 默认分页大小为10，可根据需要调整 `--page-size` 参数
5. **permissionList** 字段表示当前用户对该流水线的操作权限
