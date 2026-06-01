# EMR on ECS 操作审计管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的操作审计日志等管理。

## 说明

本文档提供 EMR on ECS 中 **操作审计管理** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 操作审计管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --version 2023-08-15 \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 操作审计管理操作

### 1. 操作列表查询

**接口描述**
调用 ListOperations，获取 E-MapReduce（EMR）集群的操作列表。

**使用场景**
查询指定集群的操作历史记录。

**请求方式**
**请求方式**： `POST`  
**Action**： `ListOperations`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListOperations | 要执行的操作，取值：ListOperations |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 否 | emr-xxx | 集群ID |
| ClusterIds | Array of String | 否 | ["emr-xxx"] | 集群ID列表 |
| ProjectName | String | 否 | default | 项目名称 |
| OperateIds | Array of String | 否 | ["xxx"] | 操作ID列表 |
| OperatorName | String | 否 | xxx | 操作者名称，模糊查询 |
| OperateName | String | 否 | 释放集群 | 操作名称模糊查询 |
| CreateTimeBefore | Long | 否 | 1701694832739 | 操作日期筛选开始时间，时间戳，单位毫秒 |
| CreateTimeAfter | Long | 否 | 1701696832739 | 操作日期筛选结束时间，时间戳，单位毫秒 |
| Tags | Array of Object | 否 | xxx | 标签信息列表 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListOperations \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListOperations","Version":"2023-08-15"}' \
  --body '{"ClusterIds":["emr-xxx"]}'
```

**请求示例**
```json
{
    "ClusterIds":["emr-xxx"]
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 操作信息列表 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | 57N8YtDWZ1LbCkWySngtD3zSgO2YTwUgwmKm/aiKplz4HQgNCpV39A3c3EOggDJ9 | 分页查询的下一页token |
| TotalCount | Integer | 69463 | 总记录数 |

**Items 对象结构**

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperateId | String | 107069 | 操作ID |
| OperateName | String | 释放节点[core-1-1.emr-xxx] | 操作名称 |
| OperateState | String | SUCCESS | 操作状态 |
| OperateType | String | NOT_MATCHED_TYPE | 操作类型 |
| OperatorId | String | null | 操作者ID |
| OperatorName | String | null | 操作者名称 |
| CreateTime | Long | 1701694832755 | 创建时间（时间戳，毫秒） |
| UpdateTime | Long | 1701694832769 | 更新时间（时间戳，毫秒） |
| StartTime | Long | 1701694832757 | 开始时间（时间戳，毫秒） |
| EndTime | Long | 1701694832768 | 结束时间（时间戳，毫秒） |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231204210119283E2950E5FAxxx",
        "Action": "ListOperations",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "Items": [
            {
                "ClusterId": "emr-xxx",
                "OperateId": "107069",
                "OperateName": "释放节点[core-1-1.emr-xxx]",
                "OperateState": "SUCCESS",
                "OperateType": "NOT_MATCHED_TYPE",
                "OperatorId": null,
                "OperatorName": null,
                "CreateTime": 1701694832755,
                "UpdateTime": 1701694832769,
                "StartTime": 1701694832757,
                "EndTime": 1701694832768
            },
            {
                "ClusterId": "emr-xxx",
                "OperateId": "107068",
                "OperateName": "释放节点[master-1-1.emr-xxx]",
                "OperateState": "SUCCESS",
                "OperateType": "NOT_MATCHED_TYPE",
                "OperatorId": null,
                "OperatorName": null,
                "CreateTime": 1701694832739,
                "UpdateTime": 1701694832752,
                "StartTime": 1701694832741,
                "EndTime": 1701694832751
            }
        ],
        "TotalCount": 69463,
        "MaxResults": 10,
        "NextToken": "57N8YtDWZ1LbCkWySngtD3zSgO2YTwUgwmKm/aiKplz4HQgNCpV39A3c3EOggDJ9"
    }
}
```
