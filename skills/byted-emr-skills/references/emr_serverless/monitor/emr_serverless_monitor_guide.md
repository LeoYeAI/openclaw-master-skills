# EMR Serverless 监控指标管理操作指南

## 概述

EMR Serverless 提供全托管的 Serverless 形态大数据服务，主要面向作业提交和资源队列管理。监控指标提供队列级、计算组级、作业监控数据。

## 说明

本文档提供 Serverless Spark 中 **监控** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2018-01-01**
- **Service**： cloudmonitor
- **Action**： GetMetricData

## 核心调用方法

监控接口推荐使用命令行工具 `scripts/on_serverless/emr_serverless_cli.py` 直连云监控 endpoint：

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetMetricData \
  --method POST \
  --endpoint open.volcengineapi.com \
  --body '<json>'
```

## 一、监控指标管理

监控指标功能用于查询 EMR Serverless 平台上的监控指标数据，包括队列级、计算组级、作业级的监控指标。

### GetMetricData接口的使用方式
- 查询指定指标在指定时间选段内聚合的时序数据。
#### 使用限制
- 调用接口前，请为子账号授权云监控只读权限 `CloudMonitorReadOnlyAccess`，否则会报 `User is not authorized to perform: cloudmonitor:GetMetricData on resource` 错误。具体操作，请参见 [为 IAM 用户授权](https://www.volcengine.com/docs/6393/73833)。
- `GetMetricData` 接口仅支持单指标查询，无法一次查询多个指标数据。
- 一个主账号及该账号下的 IAM 账号，1 秒内调用 `GetMetricData` 接口的次数不超过 20 次，否则将触发限流。
- 单请求最多支持批量拉取 50 个实例的监控数据，单请求的数据点数限制为 1440 个。
- 如果您需要调用的指标和对象较多，可能会因为限频导致拉取失败，建议尽量将请求按照时间维度均摊。
#### 请求说明

- **请求方式**：`POST`
- **请求版本**：`2018-01-01`

#### 请求参数

| 参数 | 类型 | 是否必选 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | GetMetricData | 接口名称。当前 API 的名称为 `GetMetricData`。 |
| Version | String | 是 | 2018-01-01 | 接口版本。当前 API 的版本为 `2018-01-01`。 |
| StartTime | Integer | 否 | 1648048800 | 查询的时间选段的开始时间，秒级时间戳，例如 `1632904500`。 |
| EndTime | Integer | 否 | 1648049400 | 查询的时间选段的结束时间，秒级时间戳，例如 `1632904801`。<br/>- `EndTime` 需要 > `StartTime`。<br/>- `EndTime` 不能输入未来时间。<br/>- `EndTime` < 产品允许查询天数 + `StartTime`。 |
| Instances | Array of [Instance](#instance) | 否 | - | 要查询的监控指标信息。<br/>- 存在多个 `instance` 时，`instance` 和 `instance` 之间的逻辑关系是 `or`。<br/>- 如果不传 `instance` 参数，会返回该地域下所有实例的监控数据。数据量较大可能会导致 `max-select-point` 超限，对业务产生影响，请谨慎操作。<br/>- 如果已报错，请参见错误码部分 `max-select-point` 原因和解决方案。 |
| MetricName | String | 是 | InTraffic | 要查询的监控指标名称。参见 [云监控指标查询](https://www.volcengine.com/docs/6393/73835) 下各产品的 `MetricName`。 |
| Namespace | String | 是 | VCM_EIP | 要查询的监控指标所属的产品空间。参见 [云监控指标查询](https://www.volcengine.com/docs/6393/73835) 下各产品的 `Namespace`。 |
| SubNamespace | String | 是 | Instance | 要查询的指标所属的维度。`SubNamespace` 在不同 `Namespace` 下的可选值不同，参见 [云监控指标查询](https://www.volcengine.com/docs/6393/73835) 下各产品的 `SubNamespace`。 |
| Period | String | 否 | 1m | 查询数据的间隔粒度，支持秒（s）、分钟（m）、时（h）、天（d）和周（w）粒度。<br/>- 例如查询 10 分钟内的数据，并根据 1 分钟进行分割，则会返回 10 条数据。<br/>- 当时间选段较长时，不建议使用小单位作为间隔，否则将会导致数据集过大，可能会导致 `max-select-bucket` 超限，对业务产生影响，请谨慎操作。<br/>- 如果已报错，请参见错误码部分 `max-select-bucket` 原因和解决方案。<br/>- 关于传入 `Period` 后，`StartTime`、`EndTime` 偏移的说明，请参见下文 [Period 说明](#period说明)。 |
| GroupBy | Array of String | 否 | AlternativeDimensionName | 要查询的指标所使用的分组维度。参见 [云监控指标查询](https://www.volcengine.com/docs/6393/73835) 下各产品的 `Dimensions`。<br/>- 如果指标的 `Dimension` 列未标注 **可选**，说明不存在可选 Dimension，默认所有 Dimension 都是必选，都会作为指标分组维度。<br/>  **说明**：必选的含义是无论是否传递这些 Dimension 参数，返回的维度都会以这些 Dimension 进行分组。<br/>  以缓存数据库 Redis 版的指标 `AggregatedTotalQps` 为例，`Dimension` 列为 `ResourceID,Node`。<br/>  - 当 `Dimension` 参数传递 `Node`，不传递 `ReourceID` 时：<br/>    查询条件：`Node=xxx and ResourceID=*`<br/>    分组维度：`Node,ResourceId`<br/>  - 当 `Dimension` 参数传递 `Node` 和 `ReourceID` 时：<br/>    查询条件：`Node=xxx and ResouceId=yyy`<br/>    分组维度：`Node,ResourceId`<br/>- 如果指标的 `Dimension` 列标注了 **可选**，说明存在可选 Dimension，使用时需要额外指定 `GroupBy` 参数。示例请参见下文 [GroupBy 说明](#groupby说明)。<br/>**注意**：SDK 必须升级到以下版本，才支持通过 `GroupBy` 筛选分组维度。<br/>  - Python：1.0.37 以上版本<br/>  - Go：1.0.97 以上版本<br/>  - Java：0.1.75 以上版本 |

- Instance字段说明

| 参数 | 类型 | 是否必选 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Dimensions | Array of [Dimension](#dimension) | 否 | - | 要查询的指标维度。参见 [云监控指标查询](https://www.volcengine.com/docs/6393/73835) 下各产品的 `Dimensions`。<br/>- 每个 `Dimension` 里只包含一组 KV。<br/>- 存在多个 `Dimension` 时，`Dimension` 和 `Dimension` 之间的逻辑关系是 `and`。 |

- Dimension字段说明

| 参数 | 类型 | 是否必选 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Name | String | 否 | ResourceID | 检索指标的 KEY。 |
| Value | String | 否 | eip-13fxxxx | 对应 KEY 的值。 |

- Period字段说明
  - 例如，查询 10 分钟内的数据，并根据 1 分钟进行分割，则会返回 10 条数据。
  - 当时间选段较长时，不建议使用小单位作为间隔，否则将会导致数据集过大。后端具有大值拒绝限制，当传入的参数形成如下条件时，请求失败：(EndTime - StartTime) / Period >= 5000
  **说明**：上述条件中 `EndTime`、`StartTime` 和 `Period` 的单位均为：秒(s)。
  - 对于传入的 `StartTime`、`EndTime`、`Period` 组合，取值范围建议参考下表：
    | 查询时间范围（EndTime-StartTime） | 监控数据聚合周期（Period） |
    |-----------------------------------|----------------------------|
    | (0~6] 小时                       | 30秒                       |
    | (6~24] 小时                      | 1分钟                      |
    | (1~7] 天                         | 5分钟                      |
    | (7~15] 天                        | 60分钟                     |

  - 当传入 `Period` 后，`StartTime`、`EndTime` 参数将会被偏移。返回的数据集合中，时间将会转移至 `Period` 的整分处。整分处为某时间戳可以整除 `Period`。
  - 例如：
    - 传入 `Period` 为 30s，则在当前分钟内，0s，30s 为整分点。
    - 传入 `Period` 为 20s，则在当前分钟内，0s，20s，40s 为整分点。
    - 传入 `Period` 为 10m，则在当前小时内，0m0s，10m0s，20m0s，30m0s，40m0s，50m0s 为整分点。
    - 传入 `Period` 为 24h，则在当前时间段内，UTC+0 00:00:00 为整分点。
  - 例如，`StartTime` 为 2023-03-02 00:00:00，`EndTime` 为 2023-03-05 00:00:00。
  - 实际上，UTC 时间是 `StartTime` 为 2023-03-01 16:00:00，`EndTime` 为 2023-03-04 16:00:00。
  - 因此，返回的是 UTC 时间 2023-03-02 00:00:00，2023-03-03 00:00:00，2023-03-04 00:00:00 的数据。
  - `StartTime` 总会 **向后** 偏移至最近一个整分点，`EndTime` 总会 **向前** 偏移至整分点。因此返回的数据长度和数据时间点会有一定变化，但是 `StartTime` 和 `EndTime` 本身无变化，只是选段区间被偏移。

- GroupBy字段说明
  - `GroupBy` 是查询指标所使用的分组维度。
  - 如果指标的 `Dimension` 列未标注 **可选**，表示不存在可选 Dimension，默认所有 Dimension 都是必选，都会作为指标分组维度。**必选** 是指无论是否传递这些 Dimension 参数，返回的维度都会以这些 Dimension 进行分组。
    例如，缓存数据库 Redis 版的指标 `AggregatedTotalQps`，`Dimension` 列为 `ResourceID,Node`。
    - 当 `Dimension` 参数传递 `Node`，不传递 `ReourceID` 时：
      查询条件：`Node=xxx and ResourceID=*`
      分组维度：`Node,ResourceId`
    - 当 `Dimension` 参数传递 `Node` 和 `ReourceID` 时：
      查询条件：`Node=xxx and ResouceId=yyy`
      分组维度：`Node,ResourceId`
  - 如果指标的 `Dimension` 列标注了 **可选**，表示存在可选 Dimension，使用时需要额外指定 `GroupBy` 参数。
    例如，云搜索服务的指标 `CacheHitRatio`，`Dimension` 列为 `ResourceID,Node(可选)`。多示例场景的配置示例如下：

```json
{
    "Instances": [
        {
            "Dimensions": [
                {
                    "Name": "ResourceID",
                    "Value": "eip-13fxxxx"
                },
                {
                    "Name": "Node",
                    "Value": "xxxx"
                }
            ]
        },
        {
            "Dimensions": [
                {
                    "Name": "ResourceID",
                    "Value": "eip-14dxxxx"
                },
                {
                    "Name": "Node",
                    "Value": "xxxx"
                }
            ]
        }
    ],
    "GroupBy": [
        "Node"
    ]
}
```

####  返回参数

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Data | Object of [Data](#data) | - | 返回数据。 |

- Data字段说明

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Unit | String | Bytes | 指标的单位。 |
| Period | String | 1m | 查询的时间间隔粒度。<br/>- m：分钟<br/>- s：秒<br/>- h：小时<br/>- d：天<br/>- w：周 |
| EndTime | Integer | 1648049400 | 查询选段时间的结束时间戳，秒级时间戳。 |
| Namespace | String | VCM_EIP | 监控指标所属的产品空间。 |
| StartTime | Integer | 1648048800 | 查询选段时间的开始时间戳，秒级时间戳。 |
| MetricName | String | InTraffic | 查询的监控指标的名称。 |
| DescriptionCN | String | 入方向流量 | 查询指标的中文名。 |
| DescriptionEN | String | EIP In Traffic | 查询指标的英文名。 |
| MetricDataResults | Array of [MetricData](#metricdata) | - | 查询到的指标数据。 |

- MetricData字段说明

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Legend | String | eip_in_bytes | 查询指标 `MetricName` 的别名。 |
| DataPoints | Array of [DataPoint](#datapoint) | - | 在指定时间选段内，指定指标的聚合时序数据。 |
| Dimensions | Array of [Dimension](#dimension) | - | 查询条件。 |

- DataPoint字段说明

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Value | Float | 864 | 数据值。 |
| Timestamp | Integer | 1648048800 | 数据采集的秒级时间戳。 |

- Dimension字段说明

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Name | String | ResourceID | 检索指标的 KEY。 |
| Value | String | eip-13fxxxx | 对应 KEY 的值。 |
        

### 1. 队列监控信息

**接口描述**  
此接口用于查询指定队列的监控指标数据。

**请求方式**： `POST`  
**Action**： `GetMetricData`

### 队列监控指标列表
| 指标名称 | MetricName                | 维度 | 用途 |
|----------|--------------------------|------|------|
| 队列计算组作业数量 | QueueComputeGroupTaskNum | ResourceID，ComputeGroupEngineID，JobStatus，AggJobStatus | 监控,报警 |
| 队列失败作业数 | QueueFailedTaskNum       | ResourceID，ComputeGroupEngineID，JobStatus | 监控,报警 |
| 队列运行中作业数 | QueueRunningTaskNum      | ResourceID，ComputeGroupEngineID，JobStatus | 监控,报警 |
| 队列已完成作业数 | QueueCompleteTaskNum     | ResourceID，ComputeGroupEngineID，JobStatus | 监控,报警 |
| 队列等待中作业数 | QueuePendingTaskNum      | ResourceID，ComputeGroupEngineID，JobStatus | 监控,报警 |
| 队列CPU使用量 | QueueCpuUsed             | ResourceID，ComputeGroupEngineID | 监控,报警 |
| 队列CPU使用率 | QueueCpuUsedPercent      | ResourceID | 监控,报警 |
| 队列内存使用率 | QueueMemoryUsedPercent   | ResourceID | 监控,报警 |
| 队列内存使用量 | QueueMemoryUsed          | ResourceID，ComputeGroupEngineID | 监控,报警 |
| 队列作业状态 | QueueTaskStatus          | JobStatus，ResourceID | 监控,报警 |

### 计算组监控指标列表
| 监控项中文名称 | MetricName | Dimensions | 指标用途 |
|----------------|------------|------------|----------|
| CU分配量（CU） | ComputeGroupCUAllocated | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| CU总量（CU） | ComputeGroupCUCapacity | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| CPU分配量（Core） | ComputeGroupCPUAllocated | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| CPU总量（Core） | ComputeGroupCPUCapacity | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| 内存分配量（Bytes） | ComputeGroupMemoryAllocated | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| 内存总量（Bytes） | ComputeGroupMemoryCapacity | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |
| CU分配率 | ComputeGroupCUAllocatedRate | ResourceID，ComputeGroupEngineID | 监控,报警 |
| CPU分配率 | ComputeGroupCPUAllocatedRate | ResourceID，ComputeGroupEngineID | 监控,报警 |
| 内存分配率 | ComputeGroupMemoryAllocatedRate | ResourceID，ComputeGroupEngineID | 监控,报警 |
| 计算组GPU卡数量 | ComputeGroupGPUCardCapacity | ResourceID，ComputeGroupEngineID，MetricsType | 监控,报警 |

### Spark监控项指标
| 监控项中文名称 | MetricName | Dimensions | 指标用途 |
|----------------|------------|------------|----------|
| Spark Executor Count | SparkExecutorCount | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver FGC 次数 | SparkDriverFGCCount | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Used Memory | SparkDriverUsedMemory | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Minor GC Count | SparkDriverMinorGCCount | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Major GC Count | SparkDriverMajorGCCount | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Minor GC Time | SparkDriverMinorGCTime | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Major GC Time | SparkDriverMajorGCTime | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver Memory Usage | SparkDriverMemoryUsage | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Spark Driver容器内存用量 | SparkDriverMemoryUsed | ResourceID，ServerlessJobInstanceId，ComputeGroupEngineID，PodName | 监控,报警 |
| Spark Driver CPU 用量 | SparkDriverCPUUsed | ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId，PodName | 监控,报警 |

### Ray监控项指标
| 监控项中文名称 | MetricName | Dimensions | 指标用途 |
|----------------|------------|------------|----------|
| Ray Cluster Active Nodes 数量 | RayClusterActiveNodesCount | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Ray 集群 Raylet Component Uss 占用平均值 | RayRayletComponentUssMbAvg | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Ray 集群 Raylet Component Uss 占用最小值 | RayRayletComponentUssMbMin | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |
| Ray 集群 Agent CPU 占用最大值 | RayAgentComponentCpuPercentageMax | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 Agent Component CPU 占用平均值 | RayAgentComponentCpuPercentageAvg | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 Agent Component CPU 占用最小值 | RayAgentComponentCpuPercentageMin | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 Raylet CPU 占用最大值 | RayRayletComponentCpuPercentageMax | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 Raylet Component CPU 占用平均值 | RayRayletComponentCpuPercentageAvg | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 Raylet Component CPU 占用最小值 | RayRayletComponentCpuPercentageMin | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,报警,消费 |
| Ray 集群 CPU 资源数 | RayResourceCpuTotal | SessionName，ResourceID，ComputeGroupEngineID，ServerlessJobInstanceId | 监控,消费 |

### Presto监控项指标
| 监控项中文名称 | MetricName | Dimensions | 指标用途 |
|----------------|------------|------------|----------|
| Presto Coordinator CPU 平均用量 | PrestoCoordinatorMeanCPUUsed | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Worker 平均内存用量 | PrestoWorkerMeanMemoryUsed | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Coordinator 平均内存用量 | PrestoCoordinatorMeanMemoryUsed | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Coordinator 网络流出流量速率 | PrestoCoordinatorNetworkTransmitBytesRate | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Coordinator CPU 使用率 | PrestoCoordinatorCpuUsage | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Coordinator 内存 使用率 | PrestoCoordinatorMemoryUsage | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Worker CPU 平均用量 | PrestoWorkerMeanCPUUsed | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Worker 网络流出流量速率 | PrestoWorkerNetworkTransmitBytesRate | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Worker CPU 使用率 | PrestoWorkerCpuUsage | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |
| Presto Worker 内存 使用率 | PrestoWorkerMemoryUsage | ResourceID，ComputeGroupEngineID，PodName | 监控,报警,消费 |

**调用示例**（命令行）
```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetMetricData \
  --method POST \
  --endpoint open.volcengineapi.com \
  --body '{"StartTime":1773557406,"EndTime":1773643806,"MetricName":"QueueMemoryUsageRate","Namespace":"VCM_EMR_Serverless","SubNamespace":"Queue","Period":"1m","Instances":[{"Dimensions":[{"Name":"ResourceID","Value":"1481966638772256768"}]}],"GroupBy":["ResourceID"]}'
```
- ResourceID：一般为队列ID
- ComputeGroupEngineID：一般为计算组ID
- ServerlessJobInstanceId：一般为作业ID

**请求参数示例**（JSON）

```json
{
    "MetricName": "QueueMemoryUsageRate",
    "StartTime": 1773557406,
    "EndTime": 1773643806,
    "Namespace": "VCM_EMR_Serverless",
    "Instances": [
        {
            "Dimensions": [
                {
                    "Name": "ResourceID",
                    "Value": "1481966638772256768"
                }
            ]
        }
    ],
    "GroupBy": [
        "ResourceID"
    ],
    "SubNamespace": "Queue",
    "Region": "cn-beijing"
}
```

**成功响应 (200 OK)**
```json
{
    "ResponseMetadata": {
        "RequestId": "202603161500036879108B06118548AA17",
        "Action": "GetMetricData",
        "Version": "2018-01-01",
        "Service": "cloudmonitor",
        "Region": "cn-beijing",
        "Env": "volc"
    },
    "Result": {
        "Data": [
            {
                "Namespace": "VCM_EMR_Serverless",
                "MetricName": "QueueMemoryUsageRate",
                "DescriptionCN": "队列实际内存使用率",
                "DescriptionEN": "queue real memory usage",
                "Description": "队列实际内存使用率",
                "Period": "1m0s",
                "StartTime": 1773557460,
                "EndTime": 1773643800,
                "Unit": "Percent",
                "MetricDataResults": [
                    {
                        "Legend": "volcano_queue_allocated_memory_bytes",
                        "Dimensions": [
                            {
                                "Name": "ResourceID",
                                "Value": "1481966638772256768"
                            }
                        ],
                        "DataPoints": [
                            {
                                "Timestamp": 1773557460,
                                "Value": 1.7072198912501335
                            },
                            {
                                "Timestamp": 1773557520,
                                "Value": 1.7066966742277145
                            },
                            {
                                "Timestamp": 1773557580,
                                "Value": 1.706644706428051
                            }
                        ]
                    }
                ]
            }
        ]
    }
}
```

## 最佳实践：获取计算组监控并生成报告

### 1. 获取监控项
- 选择 SubNamespace（计算组监控枚举）：`Spark` / `Presto` / `Ray` / `ComputeGroup`
- 确定维度：
  - `ResourceID`：队列 ID（公共队列可用 `public`）
  - `ComputeGroupEngineID`：计算组 ID（Default 通常为 `0`）
- 在本仓库的计算组指标清单中选择对应引擎的 MetricName 与 GroupBy：
  - [emr_serverless_compute_guide.md](emr-skills/references/emr_serverless/compute/emr_serverless_compute_guide.md)

### 2. 每个监控项调用接口
- `GetMetricData` 仅支持单指标查询，建议按 MetricName 逐个调用，避免一次请求过大导致限流或数据点超限。
- 以某个指标为例（替换 MetricName / SubNamespace / Dimensions / GroupBy）：

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetMetricData \
  --method POST \
  --endpoint open.volcengineapi.com \
  --body '{"StartTime":<start_ts>,"EndTime":<end_ts>,"MetricName":"<MetricName>","Namespace":"VCM_EMR_Serverless","SubNamespace":"<SubNamespace>","Period":"1m","Instances":[{"Dimensions":[{"Name":"ResourceID","Value":"<queue_id>"},{"Name":"ComputeGroupEngineID","Value":"<compute_group_id>"}]}],"GroupBy":[<group_by_list>]}'
```

### 3. 整理报告
- 将每个指标返回的 `DataPoints` 按时间对齐，输出：
  - 摘要：平均值 / 峰值 / P95（如有）/ 最新点
  - 异常：突增突降、长时间为 0、持续高水位
  - 关联信息：队列/计算组/PodName(SessionName) 等分组维度下的 TopN
- 建议把“指标名 → 解释 → 结论 → 建议”固定成模板，减少自然语言扩写导致的幻觉与 token 浪费。
