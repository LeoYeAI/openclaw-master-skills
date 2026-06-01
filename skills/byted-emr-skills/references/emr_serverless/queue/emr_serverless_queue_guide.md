# EMR Serverless 队列管理操作指南

## 概述

EMR Serverless 提供全托管的 Serverless 形态大数据服务，主要面向作业提交和资源队列管理。队列是 Serverless 环境中的核心资源单元，负责作业的资源调度和执行。

## 说明

本文档提供 Serverless Spark 中 **资源队列** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2024-03-25**
- **Service**： emr_serverless

## 核心调用方法

所有 EMR Serverless 队列管理操作均通过命令行工具 `scripts/on_serverless/emr_serverless_cli.py` 调用 OpenAPI。
如需指定自定义 endpoint（如 LAS），可通过 `--endpoint` 传入。

## 队列管理操作
### 1. 一键开通EMR Serverless（公共队列 + LAS）

该“一键开通”流程会串行调用两个 OpenAPI：

1. 开通 EMR Serverless 公共队列：`CreateQueueSilently`（Version：`2024-03-25`）
2. 开通 LAS：`CreateOrderInOneStep`（Version：`2024-04-30`，Endpoint：`las.{region}.volcengineapi.com`）

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action CreateQueueSilently \
  --method POST \
  --body '{}'

python ./scripts/on_serverless/emr_serverless_cli.py \
  --action CreateOrderInOneStep \
  --method POST \
  --query '{}' \
  --body '{}' \
  --endpoint las.cn-beijing.volcengineapi.com
```

`CreateQueueSilently` 返回示例：

```json
{
  "Result": {
    "Success": true
  }
}
```

`CreateOrderInOneStep` 返回示例
```json
{
  "Result": {
    "OrderNO": "",
    "Success": true
  }
}
```

### 2. 获取队列列表- ListTagQueue

**接口描述**  
通过丰富的筛选条件（如标签、引擎类型、支付类型、状态包含等）获取当前租户下的资源队列列表。

- **TOP 请求方式**：`POST`
- **Action**：`ListTagQueue`
- **Version**：`2024-03-25`

**请求参数**（JSON Body）

| 参数名 | 类型 | 是否必选 | 默认值 | 描述 |
|--------|------|----------|--------|------|
| QueueName | String | 否 | - | 队列名称或ID |
| QueueIds | List<String> | 否 | - | 队列ID列表 |
| StartTime | String | 否 | - | 开始时间 |
| EndTime | String | 否 | - | 结束时间 |
| SortOrder | String | 否 | - | 排序方式：`asc`、`desc` |
| StatusesInclude | Boolean | 否 | - | 是否包含指定状态的队列 |
| Statuses | List<String> | 否 | - | 队列状态列表（详见状态码说明） |
| PaymentTypesInclude | Boolean | 否 | - | 是否包含指定支付类型的队列 |
| PaymentTypes | List<String> | 否 | - | 支付类型列表：`0` 按量付费，`1` 包年包月，`2` 新人礼包方式 |
| EnginesInclude | Boolean | 否 | - | 是否包含指定引擎的队列 |
| Engines | List<String> | 否 | - | 引擎类型列表：`Spark`、`Presto`、`Ray`、`Hive` |
| Project | String | 否 | - | 项目名称 |
| ProjectInclude | Boolean | 否 | true | 是否包含指定项目的队列 |
| Limit | Integer | 否 | 1000 | 每页数量，最小值为1 |
| Offset | Integer | 否 | 0 | 偏移量，最小值为0 |
| VolcTags | List<VolcTag> | 否 | - | 标签列表 |

**VolcTag 结构**

| 参数名 | 类型 | 是否必选 | 描述 |
|--------|------|----------|------|
| TagKey | String | 是 | 标签键 |
| TagValue | String | 是 | 标签值 |

**队列状态 Status 说明**

| 状态码 | 描述 |
|--------|------|
| -1 | 未开通 |
| 0 | 运行中 |
| 1 | 欠费停服 |
| 2 | 欠费释放 |
| 3 | 服务创建中 |
| 4 | 已欠费 |
| 5 | 试用中 |
| 6 | 已到期 |
| 7 | 到期停服 |
| 8 | 到期释放 |
| 9 | 创建失败 |
| 10 | 扩缩容中 |
| 11 | 待付费 |

**调用示例**（命令行）
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListTagQueue \
  --method POST \
  --body '{"ProjectName":"default","Project":"default","QueueName":"","Limit":1000,"VolcTags":[]}'
```

**响应数据结构**

响应格式：

```json
{
    "ResponseMetadata": {
        "RequestId": "2026031414452144D1DD06A487426B44FC",
        "Action": "ListTagQueue",
        "Version": "2024-03-25",
        "Service": "emr_serverless",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Queue": [
            {
                "Id": "1238543785583968256",
                "Name": "公共队列",
                "PaymentType": 0,
                "Status": "0",
                "ExpiredTime": null,
                "SuspendTime": null,
                "ReclaimTime": null,
                "RemainingTime": null,
                "AutoRenewal": null,
                "ResourceType": null,
                "CreateTime": "2024-05-10 17:30:50",
                "Period": null,
                "PrestoQuantity": 0,
                "SparkQuantity": null,
                "SparkJarQuantity": null,
                "ElasticSparkQuantity": null,
                "ElasticPrestoQuantity": null,
                "Region": "cn-beijing",
                "RoleName": "admin",
                "Type": "public",
                "RunningTotal": 0,
                "WaitingTotal": 0,
                "TotalQuantity": null,
                "CpuUsedPercent": 0,
                "MemUsedPercent": 0,
                "TriggerBy": "Volcano",
                "LessThanMin": 0,
                "GreaterThanMax": 0,
                "InstanceType": 0,
                "EnablePrestoCluster": false,
                "IfPrestoOnBolt": false,
                "ErrorMessage": null,
                "VolcTags": [],
                "ProjectName": "default",
                "EngineType": "Spark",
                "IgnoreQueueAuth": 1,
                "SparkQuantityStepSize": null,
                "PrestoQuantityStepSize": null,
                "MinCu": null,
                "MaxCu": null,
                "InstanceNo": "EMR-Serverless7367299493479747878",
                "ZoneId": null,
                "MemoryRatio": null,
                "BoltEnabled": null,
                "IsEipEnabled": null,
                "CrossVpcEnabled": null,
                "CrossVpcId": null,
                "CrossVpcDefaultEnabled": null,
                "CrossVpcSubnetId": null,
                "CrossVpcSgId": null,
                "Zones": null,
                "CatalogType": null,
                "ExternalCatalog": null,
                "IsMixedQueue": null,
                "GpuInstances": null,
                "ResourceStatus": 2,
                "AccountId": "2100005493",
                "UserId": "22996259",
                "PreOrderNumber": null,
                "OrderNumber": null,
                "MountServiceName": null,
                "VePFSInfos": null
            },
            {
                "Id": "1238610629099520000",
                "Name": "test1",
                "PaymentType": 1,
                "Status": "1",
                "ExpiredTime": "2024-06-01 12:01:29",
                "SuspendTime": "2024-06-02 12:00:00",
                "ReclaimTime": "2024-06-17 12:00:00",
                "RemainingTime": "15626:43:52",
                "AutoRenewal": 0,
                "ResourceType": 0,
                "CreateTime": "2024-05-10 21:56:26",
                "Period": "M_1",
                "PrestoQuantity": 0,
                "SparkQuantity": 1,
                "SparkJarQuantity": 1,
                "ElasticSparkQuantity": null,
                "ElasticPrestoQuantity": null,
                "Region": "cn-beijing",
                "RoleName": "admin",
                "Type": "private",
                "RunningTotal": 0,
                "WaitingTotal": 0,
                "TotalQuantity": null,
                "CpuUsedPercent": 0,
                "MemUsedPercent": 0,
                "TriggerBy": "Volcano",
                "LessThanMin": 0,
                "GreaterThanMax": 0,
                "InstanceType": 0,
                "EnablePrestoCluster": false,
                "IfPrestoOnBolt": false,
                "ErrorMessage": null,
                "VolcTags": [],
                "ProjectName": null,
                "EngineType": "Spark",
                "IgnoreQueueAuth": null,
                "SparkQuantityStepSize": null,
                "PrestoQuantityStepSize": null,
                "MinCu": 16,
                "MaxCu": 16,
                "InstanceNo": "EMR-Serverless7367369345314443529",
                "ZoneId": null,
                "MemoryRatio": null,
                "BoltEnabled": null,
                "IsEipEnabled": null,
                "CrossVpcEnabled": null,
                "CrossVpcId": null,
                "CrossVpcDefaultEnabled": null,
                "CrossVpcSubnetId": "",
                "CrossVpcSgId": null,
                "Zones": [
                    {
                        "ZoneId": "",
                        "CrossVpcSubnetId": ""
                    }
                ],
                "CatalogType": "LasCatalog",
                "ExternalCatalog": null,
                "IsMixedQueue": false,
                "GpuInstances": [],
                "ResourceStatus": 9,
                "AccountId": "2100005493",
                "UserId": "22996259",
                "PreOrderNumber": null,
                "OrderNumber": null,
                "MountServiceName": null,
                "VePFSInfos": null
            }
        ],
        "Limit": 54,
        "Offset": 1,
        "Total": 54
    }
}
```

**响应字段说明**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| Queue | List<QueueResponse> | 队列列表 |
| Limit | Integer | 每页数量 |
| Offset | Integer | 偏移量 |
| Total | Integer | 总数量 |

**QueueResponse 字段说明**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| Id | String | 队列ID |
| Name | String | 队列名称 |
| PaymentType | Integer | 支付类型：0 按量付费，1 包年包月，2 新人礼包方式 |
| Status | String | 队列状态（同请求参数中的状态码） |
| ExpiredTime | String | 到期时间 |
| SuspendTime | String | 预计关停时间 |
| ReclaimTime | String | 释放时间 |
| RemainingTime | String | 剩余时间 |
| AutoRenewal | Integer | 是否自动续费：0 否，1 是 |
| ResourceType | Integer | 资源类型 |
| CreateTime | String | 创建时间 |
| Period | String | 购买周期：W_1, W_2, M_1, M_2, M_3, M_6, Y_1, Y_2, Y_3 |
| PrestoQuantity | Integer | Presto CU数量 |
| SparkQuantity | Integer | Spark CU数量 |
| SparkJarQuantity | Integer | Spark Jar CU数量 |
| ElasticSparkQuantity | Integer | 弹性Spark CU数量 |
| ElasticPrestoQuantity | Integer | 弹性Presto CU数量 |
| Region | String | 地域 |
| RoleName | String | 角色名称：admin, developer, viewer, none |
| Type | String | 队列类型：private, public |
| RunningTotal | Integer | 运行中任务数 |
| WaitingTotal | Integer | 等待中任务数 |
| TotalQuantity | Integer | 总数量 |
| CpuUsedPercent | Integer | CPU使用率百分比 |
| MemUsedPercent | Integer | 内存使用率百分比 |
| TriggerBy | String | 部署方式：volcano |
| LessThanMin | Integer | 低于最小值次数 |
| GreaterThanMax | Integer | 高于最大值次数 |
| InstanceType | Integer | 实例类型 |
| EnablePrestoCluster | Boolean | 是否启用Presto集群 |
| IfPrestoOnBolt | Boolean | Presto是否运行在Bolt上 |
| ErrorMessage | String | 错误信息 |
| VolcTags | List<VolcTag> | 标签列表 |
| ProjectName | String | 项目名称 |
| EngineType | String | 引擎类型：Spark, Presto, Ray, Hive |
| IgnoreQueueAuth | Integer | 是否忽略队列权限 |
| SparkQuantityStepSize | Integer | Spark CU步长 |
| PrestoQuantityStepSize | Integer | Presto CU步长 |
| MinCu | Integer | 最小CU数 |
| MaxCu | Integer | 最大CU数 |
| InstanceNo | String | 实例编号 |
| ZoneId | String | 可用区ID |
| MemoryRatio | Integer | 内存比例：2、4、8 |
| BoltEnabled | Boolean | 是否启用Bolt |
| IsEipEnabled | Boolean | 是否启用EIP |
| CrossVpcEnabled | Boolean | 是否启用跨VPC |
| CrossVpcId | String | 跨VPC ID |
| CrossVpcDefaultEnabled | Boolean | 是否默认启用跨VPC |
| CrossVpcSubnetId | String | 跨VPC子网ID |
| CrossVpcSgId | String | 跨VPC安全组ID |
| Zones | List<CrossVpcSubnet> | 可用区列表 |
| CatalogType | String | 目录类型 |
| ExternalCatalog | ExternalCatalog | 外部目录信息 |
| IsMixedQueue | Boolean | 是否为混合队列 |
| GpuInstances | List<PrivateQueue.GpuInstance> | GPU实例列表 |
| PreOrderNumber | String | 订单号 |
| MountServiceName | String | 关联挂载服务 |
| VePFSInfos | List<VepfsInfo> | 队列上关联的 vePFS 信息 |
| StorageVpcId | String | 存储网络VPC ID |
| StorageVpcSgId | String | 存储网络安全组ID |
| StorageSubnetIds | String[] | 存储网络子网列表 |

**vePFS 信息说明**

| 参数 | 类型 | 描述 |
|------|------|------|
| FileSystemName | String | 文件系统名称 |
| FileSystemId | String | 文件系统ID |
| Status | String | 绑定状态：Attaching（绑定中）、AttachError（绑定失败）、Attached（已绑定）、Detaching（解绑中）、DetachError（解绑失败） |
| CustomerPath | String | 用户挂载路径 |

**CrossVpcSubnet 结构**

| 参数名 | 类型 | 描述 |
|--------|------|------|
| ZoneId | String | 可用区ID |
| CrossVpcSubnetId | String | 跨VPC子网ID |


### 3. 队列详情查询（GetQueue）

**接口描述**
获取指定队列详情。

**请求参数**

| 参数 | 类型 | 是否必须 | 描述 |
|------|------|----------|------|
| Id | String | Y | 队列 ID |

**请求方式**： GET  
**Action**： GetQueue  
**Version**： 2024-03-25  

**调用示例**：

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetQueue \
  --method GET \
  --query '{"Id":"1482043093233434624"}'
```

**返回数据结构（示例）**：
注意：队列所有计算引擎都能跑！！！不要用EnablePrestoCluster、PrestoQuantity、EngineType 判断队列类型
```json
{
  "Result": {
    "Id": "148204309xx",
    "Name": "公共队列",
    "PaymentType": 0,
    "Status": "0",
    "CreateTime": "2026-03-13 15:50:08",
    "Region": "cn-beijing",
    "RoleName": "admin",
    "Type": "public",
    "RunningTotal": 0,
    "WaitingTotal": 0,
    "CpuUsedPercent": 0,
    "MemUsedPercent": 0,
    "TriggerBy": "Volcano",
    "LessThanMin": 0,
    "GreaterThanMax": 0,
    "InstanceType": 0,
    "EnablePrestoCluster": false,
    "IfPrestoOnBolt": false,
    "VolcTags": [],
    "ProjectName": "default",
    "IgnoreQueueAuth": 0,
    "InstanceNo": "xxx",
    "IsCrossVpcEnabled": false,
    "IsEipEnabled": false,
    "CurrentPrestoCu": 0,
    "CurrentSparkCu": 0,
    "PrestoQuantity": 0,
    "ResourceStatus": 2,
    "AccountId": "2100005493",
    "UserId": "22358529"
  }
}
```

### 资源队列 Queue 字段说明

| 字段名 | 类型 | 备注                                                                                                                                                                       |
|--------|------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| Id | String | 队列ID                                                                                                                                                                     |
| Name | String | 队列名称                                                                                                                                                                     |
| Region | String | 可用区域                                                                                                                                                                     |
| Type | String | 队列类型：<br>- public： 公共队列<br>- private： 独占队列                                                                                                                               |
| Status | String | 队列状态，参见 [资源队列状态 Status](#资源队列状态-status)                                                                                                                                  |
| CreateTime | String | 开通时间                                                                                                                                                                     |
| ExpiredTime | String | 有效期至，具体含义如下：<br>- 公共队列：不返回此字段<br>- 独占队列：合同到期时间                                                                                                                           |
| RemainingTime | String | 剩余时长，不同队列状态表达的含义不同：<br>- 公共队列：返回00:00:00，是正常情况<br>- 正常/创建中：距离合同到期时间<br>- 已欠费：距离停服时间<br>- 欠费停服：距离释放时间<br>- 已到期：距离停服时间<br>- 到期停服：距离释放时间<br>格式HH:mm:ss, 比如还有18秒钟："00:00:18" |
| Period | String | 购买时长，包年包月时返回，不同值的含义如下：<br>- M_1： 1个月<br>- M_3：3个月<br>- M_6：6个月<br>- Y_1： 1年<br>- Y_2： 2年<br>- Y_3： 3年                                                                    |
| AutoRenewal | Int | 是否自动续费，包年包月时生效，默认值为0：<br>- 0：否<br>- 1：是                                                                                                                                  |
| ResourceType | Int | 独占队列资源类型，仅包年包月时生效，默认值为0：<br>- 0: 固定资源<br>- 1: 弹性资源                                                                                                                       |
| SparkQuantity | Int | 数据处理资源单元N，参数示例：<br>[N] x 16 = xxx CU，本参数传 N                                                                                                                              |
| SparkJarQuantity | Int | 数据处理资源单元N，参数示例：<br>[N] x 16 = xxx CU，本参数传 N                                                                                                                              |
| ElasticSparkQuantity | Int | 弹性资源单元上限Max，参数示例：<br>[Max] x 16 = xxx CU，本参数传 Max                                                                                                                        |
| RoleName | String | 当前用户对于此资源队列拥有的权限：<br>- admin<br>- developer<br>- viewer<br>- none(无任何权限)                                                                                                 |

## 资源队列状态 Status

| 状态码 | 描述 |
|--------|------|
| Creating | 创建中 |
| Active | 正常 |
| Arrears | 已欠费 |
| ArrearsStopped | 欠费停服 |
| Expired | 已到期 |
| ExpiredStopped | 到期停服 |
| Released | 已释放 |

## 最佳实践


## 参考文档

- [火山引擎 EMR Serverless 产品文档](https://www.volcengine.com/docs/6491/1164733)
- [EMR Serverless API 参考](https://www.volcengine.com/docs/6491/1164734)
- [队列管理最佳实践](https://www.volcengine.com/docs/6491/1164735)
