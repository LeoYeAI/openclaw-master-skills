# EMR Serverless 计算组运维指南

本文档聚焦 EMR Serverless 计算组的运维操作，包括：创建、查询、修改、启动、停止、删除计算组 以及查询计算组监控Metrics 等接口。

## 通过 OpenAPI 运维（命令行）

本节仅给出最常用的 OpenAPI 调用骨架，统一使用命令行工具 `scripts/on_serverless/emr_serverless_cli.py`，避免在文档中内嵌 Python 调用代码。

- Service 固定为 `emr_serverless`
- Version 固定为 `2024-03-25`

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action <Action> \
  --method <GET|POST> \
  --query '<json>' \
  --body '<json>'
```

### 1. 创建计算组（CreateQueueComponent）

**接口描述**

兼容预/后付费的队列开通接口。
注意：不能在公共队列上调用
**请求参数**

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| Name | String | Y | 计算组名，不可重复 |
| QueueId | String | Y | 队列ID |
| EngineType | String | Y | Spark/Presto/Ray |
| ApplyStrategy | String | Y | 部署策略。等待：wait，抢占：preempt |
| WaitTimeoutMin | Int | N | 策略为 wait 时必填，单位分钟 |
| Description | String | N | 备注 |
| Settings | json String | Y | 不同引擎的配置 (详细配置见下表) |

**Settings 参数说明**

#### 1. Spark

**JSON 结构**

```json
{
  "driverCpu": Long,
  "executorCpu": Long,
  "executorMinReplicas": Int,
  "executorMaxReplicas": Int,
  "catalogType": String,
  "externalCatalog": {
    "vpc": String,
    "subnet": String,
    "securityGroup": String,
    "hmsAddress": String
  },
  "boltEnabled": Boolean,
  "customConf": String,
  "maxRunningQueries": Int
}
```

**参数说明**

| 参数 | 类型 | 描述 |
|---|---|---|
| driverCpu | Long | Driver 的 CPU 核数 |
| executorCpu | Long | Executor 的 CPU 核数 |
| executorMinReplicas | Int | Executor 最小副本数 |
| executorMaxReplicas | Int | Executor 最大副本数 |
| catalogType | String | 元数据类型 (枚举: LasCatalog / ExternalCatalog) |
| externalCatalog | Object | 外部元数据配置 (当 catalogType 为 ExternalCatalog 时必填) |
| - vpc | String | 外部元数据 VPC ID |
| - subnet | String | 外部元数据子网 ID |
| - securityGroup | String | 外部元数据安全组 ID |
| - hmsAddress | String | HMS Thrift 地址 |
| boltEnabled | Boolean | 是否开启 Bolt (默认 false) |
| customConf | String | 自定义配置字符串 |
| maxRunningQueries | Int | 最大并发运行查询数 |

#### 2. Presto

**JSON 结构**

```json
{
  "coordinatorCpu": Long,
  "workerCpu": Long,
  "coordinatorReplicas": Int,
  "workerReplicas": Int,
  "prestoOnBolt": Boolean,
  "catalogType": String,
  "externalCatalog": {
    "vpc": String,
    "subnet": String,
    "securityGroup": String,
    "hmsAddress": String
  },
  "autoScaling": {
    "triggerType": String,
    "triggerUpValue": Int,
    "triggerDownValue": Int,
    "triggerUpSeconds": Int,
    "triggerDownSeconds": Int
  },
  "resourceGroupFile": String,
  "elasticWorkerReplicas": Int,
  "maxRunningQueries": Int,
  "idleSeconds": Int
}
```

**参数说明**

| 参数 | 类型 | 描述 |
|---|---|---|
| coordinatorCpu | Long | Coordinator 的 CPU 核数 |
| workerCpu | Long | Worker 的 CPU 核数 |
| coordinatorReplicas | Int | Coordinator 副本数 |
| workerReplicas | Int | Worker 副本数 |
| prestoOnBolt | Boolean | 是否在 Bolt 上运行 Presto |
| catalogType | String | 元数据类型 (枚举: LasCatalog / ExternalCatalog) |
| externalCatalog | Object | 外部元数据配置 |
| autoScaling | Object | 自动扩缩容配置 |
| - triggerType | String | 触发类型 (枚举: cpu, memory, pendingQuery) |
| - triggerUpValue | Int | 触发扩容的阈值 |
| - triggerDownValue | Int | 触发缩容的阈值 |
| - triggerUpSeconds | Int | 持续触发扩容的时间(秒) |
| - triggerDownSeconds | Int | 持续触发缩容的时间(秒) |
| resourceGroupFile | String | 资源组配置文件路径 |
| elasticWorkerReplicas | Int | 弹性 Worker 副本数 |
| maxRunningQueries | Int | 最大并发运行查询数 |
| idleSeconds | Int | 空闲超时时间(秒) |

#### 3. Ray

**JSON 结构**

```json
{
  "image": String,
  "imageCustomized": Boolean,
  "headCpu": Long,
  "headGpu": Long,
  "headMem": String,
  "headInstanceFlavor": String,
  "workerCpu": Long,
  "workerGpu": Long,
  "workerMem": String,
  "workerReplicas": Int,
  "autoScaling": Boolean,
  "workerMinReplicas": Int,
  "workerMaxReplicas": Int,
  "workerMgpuCore": Long,
  "workerMgpuMemory": String,
  "workerInstanceFlavor": String
}
```

**参数说明**

| 参数 | 类型 | 描述 |
|---|---|---|
| image | String | 镜像地址 |
| imageCustomized | Boolean | 是否为自定义镜像 |
| headCpu | Long | Head 节点 CPU 核数 |
| headGpu | Long | Head 节点 GPU 卡数 |
| headMem | String | Head 节点内存大小 (例如 "4Gi") |
| headInstanceFlavor | String | Head 节点实例规格 ID (异构队列必填) |
| workerCpu | Long | Worker 节点 CPU 核数 |
| workerGpu | Long | Worker 节点 GPU 卡数 |
| workerMem | String | Worker 节点内存大小 |
| workerReplicas | Int | Worker 节点副本数 |
| autoScaling | Boolean | 是否开启自动扩缩容 |
| workerMinReplicas | Int | Worker 最小副本数 |
| workerMaxReplicas | Int | Worker 最大副本数 |
| workerMgpuCore | Long | Worker mGPU 核心数 |
| workerMgpuMemory | String | Worker mGPU 显存大小 |
| workerInstanceFlavor | String | Worker 节点实例规格 ID (异构队列必填) |

#### 4. RayServe

**JSON 结构**

```json
{
  "image": String,
  "imageCustomized": Boolean,
  "headCpu": Long,
  "headGpu": Long,
  "headMem": String,
  "headInstanceFlavor": String,
  "workerCpu": Long,
  "workerGpu": Long,
  "workerMem": String,
  "workerReplicas": Int,
  "autoScaling": Boolean,
  "workerMinReplicas": Int,
  "workerMaxReplicas": Int,
  "workerMgpuCore": Long,
  "workerMgpuMemory": String,
  "workerInstanceFlavor": String,
  "crossVpcId": String,
  "zones": [{
    "ZoneId": String,
    "CrossVpcSubnetId": String
  }],
  "crossVpcSgId": String,
  "configYaml": String
}
```

**参数说明**

| 参数 | 类型 | 描述 |
|---|---|---|
| (基础参数) | - | 同 Ray |
| crossVpcId | String | 跨 VPC ID |
| zones | List | 可用区配置列表 |
| - ZoneId | String | 可用区 ID |
| - CrossVpcSubnetId | String | 跨 VPC 子网 ID |
| crossVpcSgId | String | 跨 VPC 安全组 ID |
| configYaml | String | Ray Serve 配置文件内容 (YAML 字符串) |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action CreateQueueComponent \
  --method POST \
  --body '{"Name":"my-compute-group","QueueId":"queue_id","EngineType":"Spark","ApplyStrategy":"wait","WaitTimeoutMin":10,"Description":"test compute group","Settings":"<settings_json_string>"}'
```

### 2. 计算组列表（ListQueueComponent）

**接口描述**

获取Serverless队列计算组列表。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListQueueComponent \
  --method POST \
  --query '{"QueueId":"148196663877225xxx"}'
```

**请求参数**
传入队列ID（query）
```json
{
  "QueueId": "148196663877225xxx"
}
```

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "2026031319084456AA898AC9BE1F2084E6",
    "Action": "ListQueueComponent",
    "Version": "2024-03-25",
    "Service": "emr_serverless",
    "Region": "cn-beijing",
    "Error": null
  },
  "Result": [
    {
      "Id": "0",
      "Name": "Default",
      "QueueId": "148196663877225xxx",
      "QueueName": "test_xxxx",
      "Status": "2",
      "EngineType": "General",
      "ApplyStrategy": null,
      "WaitTimeoutMin": 0,
      "Description": "",
      "Settings": "{}",
      "MinCu": 64,
      "MaxCu": 128,
      "MinGpu": [],
      "MaxGpu": [],
      "UseQueueCapacityInMaxQuota": false,
      "Gpu": 0,
      "AssignedCu": 56,
      "AssignedGpu": 0,
      "StartTime": "2026-03-13T10:46:21",
      "CreateTime": "2026-03-13T10:46:21",
      "CreateBy": "xxxx",
      "AccessAddress": null,
      "ErrorMsg": null,
      "CurrentUsage": {
        "Cpu": "0",
        "GpuCard": "0",
        "GpuInstancesUsage": []
      }
    },
    {
      "Id": "14820xx",
      "Name": "ziwen",
      "QueueId": "148196663877225xxx",
      "QueueName": "test_xxxx",
      "Status": "2",
      "EngineType": "Spark",
      "ApplyStrategy": "wait",
      "WaitTimeoutMin": 10,
      "Description": null,
      "Settings": "{\"executorMinReplicas\":\"1\",\"boltEnabled\":\"false\",\"executorMaxReplicas\":\"1\",\"driverCpu\":\"4\",\"executorCpu\":\"8\",\"catalogType\":\"LasCatalog\",\"maxRunningQueries\":\"10\"}",
      "MinCu": 12,
      "MaxCu": 12,
      "MinGpu": [],
      "MaxGpu": [],
      "UseQueueCapacityInMaxQuota": false,
      "Gpu": 0,
      "AssignedCu": null,
      "AssignedGpu": null,
      "StartTime": "2026-03-13T18:47:03",
      "CreateTime": "2026-03-13T18:33:34",
      "CreateBy": "zzw.data@bytedance.com",
      "AccessAddress": null,
      "ErrorMsg": null,
      "CurrentUsage": {
        "Cpu": "12",
        "GpuCard": "0",
        "GpuInstancesUsage": []
      }
    },
    {
      "Id": "1481968346680262656",
      "Name": "ray_cluster",
      "QueueId": "148196663877225xxx",
      "QueueName": "test_xxxx",
      "Status": "2",
      "EngineType": "Ray",
      "ApplyStrategy": "wait",
      "WaitTimeoutMin": 10,
      "Description": "",
      "Settings": "{\"autoScaling\":\"true\",\"imageCustomized\":\"false\",\"headCpu\":\"8\",\"image\":\"emr-serverless-online-cn-beijing.cr.volces.com/emr-serverless-ray/ray:2.50.1.0-py3.12-ubuntu22.04-852-3.19.0\",\"workerReplicas\":\"1\",\"customConf\":\"\",\"workerMinReplicas\":\"1\",\"workerCpu\":\"8\",\"workerMaxReplicas\":\"1\"}",
      "MinCu": 16,
      "MaxCu": 16,
      "MinGpu": [],
      "MaxGpu": [],
      "UseQueueCapacityInMaxQuota": false,
      "Gpu": 0,
      "AssignedCu": null,
      "AssignedGpu": null,
      "StartTime": "2026-03-13T10:56:42",
      "CreateTime": "2026-03-13T10:53:07",
      "CreateBy": "xxxx",
      "AccessAddress": null,
      "ErrorMsg": null,
      "CurrentUsage": {
        "Cpu": "16",
        "GpuCard": "0",
        "GpuInstancesUsage": []
      }
    },
    {
      "Id": "1481968232884600832",
      "Name": "presto_warehouse",
      "QueueId": "148196663877225xxx",
      "QueueName": "test_xxxx",
      "Status": "2",
      "EngineType": "Presto",
      "ApplyStrategy": "wait",
      "WaitTimeoutMin": 10,
      "Description": "",
      "Settings": "{\"image\":\"emr-serverless-online-cn-beijing.cr.volces.com/emr-serverless-engine/presto:release-1.11.0-558\",\"workerReplicas\":\"1\",\"elasticWorkerReplicas\":\"0\",\"prestoOnBolt\":\"false\",\"accessControlEnabled\":\"false\",\"catalogType\":\"LasCatalog\",\"workerCpu\":\"8\",\"coordinatorCpu\":\"8\",\"maxRunningQueries\":\"8\",\"coordinatorReplicas\":\"1\",\"maxQueueQueries\":\"200\"}",
      "MinCu": 16,
      "MaxCu": 16,
      "MinGpu": [],
      "MaxGpu": [],
      "UseQueueCapacityInMaxQuota": false,
      "Gpu": 0,
      "AssignedCu": null,
      "AssignedGpu": null,
      "StartTime": "2026-03-13T10:55:03",
      "CreateTime": "2026-03-13T10:52:40",
      "CreateBy": "xxxx",
      "AccessAddress": null,
      "ErrorMsg": null,
      "CurrentUsage": {
        "Cpu": "16",
        "GpuCard": "0",
        "GpuInstancesUsage": []
      }
    },
    {
      "Id": "1481968170267836416",
      "Name": "spark_warehouse",
      "QueueId": "148196663877225xxx",
      "QueueName": "test_xxxx",
      "Status": "2",
      "EngineType": "Spark",
      "ApplyStrategy": "wait",
      "WaitTimeoutMin": 10,
      "Description": "",
      "Settings": "{\"executorMinReplicas\":\"1\",\"boltEnabled\":\"false\",\"executorMaxReplicas\":\"1\",\"driverCpu\":\"8\",\"executorCpu\":\"4\",\"catalogType\":\"LasCatalog\",\"maxRunningQueries\":\"4\"}",
      "MinCu": 12,
      "MaxCu": 12,
      "MinGpu": [],
      "MaxGpu": [],
      "UseQueueCapacityInMaxQuota": false,
      "Gpu": 0,
      "AssignedCu": null,
      "AssignedGpu": null,
      "StartTime": "2026-03-13T10:53:20",
      "CreateTime": "2026-03-13T10:52:25",
      "CreateBy": "xxxx",
      "AccessAddress": null,
      "ErrorMsg": null,
      "CurrentUsage": {
        "Cpu": "12",
        "GpuCard": "0",
        "GpuInstancesUsage": []
      }
    }
  ]
}
```

### 3. 启动计算组（StartQueueComponent）

**接口描述**

启动计算组。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action StartQueueComponent \
  --method POST \
  --body '{"Id":"component_id","ApplyStrategy":"wait","WaitTimeoutMin":5}'
```

### 4. 停机计算组（StopQueueComponent）

**接口描述**

停止计算组。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action StopQueueComponent \
  --method POST \
  --body '{"Id":"component_id"}'
```

### 5. 删除计算组（DeleteQueueComponent）

**接口描述**

删除计算组。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action DeleteQueueComponent \
  --method POST \
  --body '{"Id":"component_id"}'
```

### 6. 修改备注（UpdateComponentDescription）

**接口描述**

修改计算组备注。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action UpdateComponentDescription \
  --method POST \
  --body '{"Id":"component_id","Description":"new description"}'
```

### 7. 更配计算组（ModifyQueueComponent）

**接口描述**

参数与创建参数相同，额外新增字段 计算组Id。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ModifyQueueComponent \
  --method POST \
  --body '{"Id":"component_id","Name":"my-compute-group","QueueId":"queue_id","EngineType":"Spark","ApplyStrategy":"wait","Settings":"<settings_json_string>"}'
```

### 8. 可选规格（ComponentSpecificationOptions）

**接口描述**

获取 spark/presto/ray 计算组的可选规格。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ComponentSpecificationOptions \
  --method GET \
  --query '{"EngineType":"Spark","QueueId":"queue_id"}'
```

### 9. 基础镜像列表（ListBaseImages）

**接口描述**

基础镜像列表，包含 Spark / Ray。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListBaseImages \
  --method GET \
  --query '{"EngineType":"Spark","TagLike":"latest"}'
```

### 10. 测试网络连接（ExternalHmsConnectionTest）

**接口描述**

spark 情况下，外部hms测试网络连接。

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ExternalHmsConnectionTest \
  --method POST \
  --body '{"VpcId":"vpc-xxx","SubnetId":"subnet-xxx","SecurityGroupId":"sg-xxx","Hms":"thrift://xxx:9083","QueueId":"queue_id"}'
```

### 11. 查询计算组监控（GetMetricData）

**接口描述**

查询指定指标在指定时间选段内聚合的时序数据，用于查看计算组的资源与运行情况。

注意：
- 当查询时，需要先阅读：**计算组指标清单**，找到对应的计算组指标，每一个MetricName都需要调用一次GetMetricData接口拿到监控数据

**请求方式**： POST  
**Action**： GetMetricData  
**Version**： 2018-01-01  
**Endpoint**： open.volcengineapi.com
**service**: cloudmonitor

**请求参数（body）**

| 参数 | 类型 | 是否必须 | 描述 |
|---|---|---|---|
| StartTime | Integer | N | 开始时间（秒级时间戳） |
| EndTime | Integer | N | 结束时间（秒级时间戳，需大于 StartTime，且不能是未来时间） |
| MetricName | String | Y | 指标名称 |
| Namespace | String | Y | 产品空间，固定为 `VCM_EMR_Serverless` |
| SubNamespace | String | Y | 指标维度空间，固定为 `Spark`/`Presto`/`Ray`/`ComputeGroup` |
| Period | String | N | 聚合粒度，如 `1m`/`5m`/`1h` |
| Instances | Array | N | 实例过滤条件（可批量），每个 instance 下的 Dimensions 为 and 关系，instance 之间为 or 关系 |
| GroupBy | Array of String | N | 分组维度（当指标存在可选维度时使用） |

说明：

- Namespace 固定为 `VCM_EMR_Serverless`。
- SubNamespace 固定为以下枚举：`Spark`（spark 计算组监控）、`Presto`（presto 计算组监控）、`Ray`（ray 计算组监控）、`ComputeGroup`（通用计算组监控）
- MetricName 的具体取值需要结合“云监控指标查询”中对应指标定义确定
- Dimensions 必须需要填写跟计算组有关的信息
  - ResourceID: 队列ID（如果是公共队列则ResourceID = public）
  - ComputeGroupEngineID：计算组ID（如果是Default计算组则id = 0）
- GroupBy 根据指标清单里的GroupBy确定

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetMetricData \
  --method POST \
  --endpoint open.volcengineapi.com \
  --body '{"StartTime":<start_ts>,"EndTime":<end_ts>,"MetricName":"YourMetricName","Namespace":"VCM_EMR_Serverless","SubNamespace":"ComputeGroup","Period":"1m","Instances":[{"Dimensions":[{"Name":"ResourceID","Value":"1481966638772256768"},{"Name":"ComputeGroupEngineID","Value":"1481968232884600832"}]}],"GroupBy":[<group_by_list>]}'
```
