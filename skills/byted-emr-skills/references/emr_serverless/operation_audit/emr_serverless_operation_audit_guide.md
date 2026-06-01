# EMR Serverless 队列管理操作指南

## 概述

EMR Serverless 提供全托管的 Serverless 形态大数据服务，主要面向作业提交和资源队列管理。操作审计提供将分散的、多样的操作事件（包括用户手动操作和系统自动触发）归集管理，提供队列级、计算组级和全局的审计视图和日志

## 说明

本文档提供 Serverless Spark 中 **资源队列** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2024-03-25**
- **Service**： emr_serverless

## 核心调用方法
- 所有的 EMR Serverless 操作审计相关操作均通过下列脚本实现
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action <Action> \
  --method <GET|POST> \
  --query '<json>' \
  --body '<json>'
```


## 二、操作日志管理

操作日志功能用于查询 EMR Serverless 平台上的各种操作记录，包括队列管理、计算组管理、作业执行等操作的历史记录。

### 1 查询操作日志 (ListOperationLogs)

**接口描述**  
此接口用于"日志中心"的全局操作日志页面以及队列、计算组的操作列表查询。

**权限要求**：需要全局或指定项目空间的审计查看权限。

**请求方式**： `POST`  
**Action**： `ListOperationLogs`

**请求参数**

| 参数名 | 类型 | 是否必选 | 描述 |
|--------|------|----------|------|
| QueueIds | string[] | 否 | 要查询的队列 ID 列表，逗号分隔。支持查询历史（已释放）队列。 |
| ComputeGroupIds | string[] | 否 | 要查询的计算组 ID 列表，逗号分隔。支持查询历史（已释放）队列。 |
| ComputeGroupName | String | 否 | 计算组名称模糊搜索 |
| OperationNames | string[] | 否 | 操作名称枚举值列表，逗号分隔。 |
| Statuses | string[] | 否 | 操作状态枚举值列表，逗号分隔。 |
| OperatorName | string | 否 | 操作人名称，用于精确搜索。 |
| StartTime | string | 否 | 查询时间窗口的开始时间，格式：`YYYY-MM-DDTHH:mm:ssZ` |
| EndTime | string | 否 | 查询时间窗口的结束时间，格式：`YYYY-MM-DDTHH:mm:ssZ` |
| Keyword | string | 否 | 模糊搜索关键字，可匹配操作对象名称。 |
| MaxResults | int | 否 | 每页数量，默认 10。 |
| NextToken | int | 否 | 页码，默认 0。 |
| SortBy | string | 否 | 排序字段，默认 `start_time` |
| SortOrder | string | 否 | 排序方式，`asc` 或 `desc`，默认 `desc` |

**调用示例**（Python）

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListOperationLogs \
  --method POST \
  --body '{
    "QueueIds": ["queues-123", "queues-456"],
    "StartTime": "2024-01-01T00:00:00Z",
    "EndTime": "2024-12-31T23:59:59Z",
    "MaxResults": 20,
    "SortBy": "start_time",
    "SortOrder": "desc"
  }'
```

**请求参数示例**（JSON）

```json
{
    "QueueIds": ["queues-123", "queues-456"],
    "StartTime": "2024-01-01T00:00:00Z",
    "EndTime": "2024-12-31T23:59:59Z",
    "MaxResults": 20,
    "SortBy": "start_time",
    "SortOrder": "desc"
}
```

**成功响应 (200 OK)**

```json
{
    "ResponseMetadata": {
        "RequestId": "202603141545375EF3F9087C37492C908F",
        "Action": "ListOperationLogs",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "TotalCount": 6,
        "MaxResults": 10,
        "NextToken": null,
        "Result": [
            {
                "OperationId": "601b7cf9-7b3a-4685-ad8d-8b459dc4aa29",
                "OperationName": "RENEW_RESOURCE",
                "Target": "guanxinyu",
                "TargetId": "1481697957232246784",
                "TargetType": "QUEUE",
                "Status": "COMPLETED",
                "Operator": {
                    "AccountId": 2100005493,
                    "OperatorType": "ACCOUNT",
                    "OperatorUserId": "2100005493",
                    "OperatorName": "EMR_Dev"
                },
                "StartTime": "2026-03-14T00:11:17.402",
                "EndTime": "2026-03-14T00:11:17.473",
                "Remark": null,
                "HasStepTree": true,
                "HasDetail": false
            },
            {
                "OperationId": "b6b0f80a-289c-423d-9657-3c0c355abe4c",
                "OperationName": "RENEW_RESOURCE",
                "Target": "guanxinyu",
                "TargetId": "1481697957232246784",
                "TargetType": "QUEUE",
                "Status": "COMPLETED",
                "Operator": {
                    "AccountId": 2100005493,
                    "OperatorType": "ACCOUNT",
                    "OperatorUserId": "2100005493",
                    "OperatorName": "EMR_Dev"
                },
                "StartTime": "2026-03-13T06:10:51.23",
                "EndTime": "2026-03-13T06:10:51.274",
                "Remark": null,
                "HasStepTree": true,
                "HasDetail": false
            }
        ]
    }
}
```

**响应参数说明**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| TotalCount | Integer | 总记录数 |
| MaxResults | Integer | 每页数量 |
| NextToken | Integer | 下一页令牌 |
| Result | Array | 操作日志记录列表 |

**操作日志记录字段说明**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| OperationId | String | 操作ID |
| OperationName | String | 操作名称 |
| Target | String | 操作目标名称 |
| TargetId | String | 操作目标ID |
| TargetType | String | 操作目标类型 |
| Status | String | 操作状态 |
| Operator | Object | 操作人信息 |
| StartTime | String | 开始时间 |
| EndTime | String | 结束时间 |
| Remark | String | 备注信息 |
| HasStepTree | Boolean | 是否有步骤树 |
| HasDetail | Boolean | 是否有详细信息 |

**操作人信息字段说明**

| 字段名 | 类型 | 描述 |
|--------|------|------|
| AccountId | Integer | 账户ID |
| OperatorType | String | 操作人类型 |
| OperatorUserId | String | 操作人用户ID |
| OperatorName | String | 操作人姓名 |

---

