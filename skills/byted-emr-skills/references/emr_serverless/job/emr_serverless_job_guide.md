# EMR Serverless 作业管理操作指南

## 概述

EMR Serverless 提供全托管的 Serverless 形态大数据服务，主要面向作业模板的创建、修改、执行、作业模板详情、列表查询等管理。
## 说明

本文档提供 EMR Serverless 中 **作业模板** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2024-06-13**
- **Service**： emr

## 核心调用方法

所有 EMR Serverless 作业模板管理操作均通过下列脚本实现

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action <Action> \
  --method <GET|POST> \
  --query '<json>' \
  --body '<json>'
```

## 一、作业模板管理操作

作业模板是描述作业运行所需配置的核心对象，包括作业类型、资源依赖、启动参数、执行环境等信息。通过作业模板，您可以标准化作业提交流程，实现作业的快速部署和复用。

### 1. 创建作业模板定义

**接口描述**  
创建新的作业模板，根据 `DevelopMode` 的不同，可通过 JSON 结构体或 YAML 字符串提交作业内容。支持 SparkJar、PySpark、RayJob、RayService 四种作业类型。

**请求方式**： `POST`  
**Action**： `CreateJobDefinition`

**请求参数**

| 字段名 | 类型 | 是否必须 | 描述                                                                                            |
|--------|------|----------|-----------------------------------------------------------------------------------------------|
| JobDefinitionName | String | 是 | 作业模板名称，长度 1-128 字符                                                                            |
| JobType | JobTypeEnum | 是 | 作业类型，可选值：`SparkJar`, `PySpark`, `RayJob`, `RayService`                                        |
| ResourceType | ResourceTypeEnum | 是 | 资源类型，可选值：`EMR_SERVERLESS`, `EMR_ON_VKE`, `EMR_ON_ECS`                                         |
| ResourceId | String | 是 | 资源 ID，例如队列 ID 或集群 ID                                                                          |
| DevelopMode | DevelopModeEnum | 是 | 开发类型，可选值：`UI`, `Json`, `Yaml`                                                                 |
| JobDefinitionContent | Object | 是 | 作业模板内容（JSON 结构体）。当 `DevelopMode` 为 `Json` 时必填，`Yaml` 模式时不传此字段。具体结构根据 `JobType` 不同而变化，详见下方子章节。 |
| JobDefinitionYaml | String | 是 | 作业内容（YAML 格式）。当 `DevelopMode` 为 `Yaml` 时必填。                                                   |
| Description | String | 否 | 作业模板描述                                                                                        |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action CreateJobDefinition \
  --method POST \
  --query '{}' \
  --body '{
    "JobDefinitionName": "liubin_test123",
    "JobType": "PySpark",
    "ResourceType": "EMR_SERVERLESS",
    "Conf": {},
    "ResourceId": "1238543785583968256-0",
    "ResourceName": "公共队列-Default",
    "DevelopMode": "UI",
    "JobDefinitionContent": {
      "Jars": [],
      "PyFiles": [],
      "Files": [],
      "Archives": [],
      "MainApplicationFile": "tos://amoro-lance-test/archive/",
      "StorageMounts": [],
      "JobType": "PySpark",
      "UseExistingRayCluster": false,
      "Volumes": [],
      "VolumeMounts": []
    },
    "ProjectName": "default",
    "UserLocale": "zh"
  }'
```

**请求参数示例**（JSON）

```json
{
    "JobDefinitionName": "my-ray-job",
    "JobType": "RayJob",
    "ResourceType": "EMR_ON_VKE",
    "ResourceId": "cluster-xxx",
    "DevelopMode": "Json",
    "JobDefinitionContent": {
        "VolcanoQueue": "ray-queues",
        "UseExistingRayCluster": false,
        "IsCustomImage": true,
        "Image": "cr.bytedance.com/las/ray:2.9.0-py39",
        "HeadCpu": 4.0,
        "HeadMem": 8.0,
        "WorkerCpu": 8.0,
        "WorkerMem": 16.0,
        "WorkerReplicas": 3,
        "WorkingDirType": "tos",
        "WorkingDir": "tos://las-jobs/ray/train",
        "Entrypoint": "python train.py --epochs 10"
    },
    "Description": "Ray training job"
}
```

---

#### JobDefinitionContent 字段结构

`JobDefinitionContent` 是一个 JSON 对象，必须包含 `JobType` 字段，其余字段根据 `JobType` 的不同而不同。以下分类型说明。

##### 1.1 SparkJar 类型

**参数**

| 字段名 | 类型 | 是否必须 | 描述 |
|--------|------|----------|------|
| JobType | String | 是 | 固定为 `"SparkJar"` |
| VolcanoQueue | String | 否 | Volcano 队列名称 |
| MainClass | String | 是 | 主类全限定名 |
| MainApplicationFile | String | 是 | 主任务 JAR 包路径（如 `tos://bucket/jars/main.jar`） |
| Jars | List<String> | 否 | 依赖的 JAR 包路径列表 |
| Files | List<String> | 否 | 依赖的普通文件路径列表 |
| SparkConf | String | 否 | Spark 配置参数（JSON 字符串格式） |
| MainArguments | String | 否 | 主类入口参数 |

**示例**

```json
{
    "JobType": "SparkJar",
    "VolcanoQueue": "myqueue",
    "MainClass": "com.bytedance.las.JobMain",
    "MainApplicationFile": "tos://las-jobs/spark/jars/analytics.jar",
    "Jars": ["tos://las-jobs/spark/deps/mysql-connector.jar"],
    "Files": ["tos://las-jobs/spark/configs/application.conf"],
    "SparkConf": "{\"spark.executor.cores\":2,\"spark.executor.memory\":\"4g\"}",
    "MainArguments": "--date 20240701 --output-path tos://las-results/report"
}
```

##### 1.2 PySpark 类型

**参数**

| 字段名 | 类型 | 是否必须 | 描述 |
|--------|------|----------|------|
| VolcanoQueue | String | 否 | Volcano 队列名称 |
| MainPythonFile | String | 是 | 主 Python 文件路径（如 `tos://bucket/pyspark/main.py`） |
| Jars | List<String> | 否 | 依赖的 JAR 包路径列表 |
| PyFiles | List<String> | 否 | 依赖的 Python 文件/zip 包路径列表 |
| Files | List<String> | 否 | 依赖的普通文件路径列表 |
| SparkConf | String | 否 | Spark 配置参数（JSON 字符串格式） |
| MainArguments | String | 否 | Python 脚本入口参数 |

**示例**

```json
{
    "VolcanoQueue": "myqueue",
    "MainPythonFile": "tos://las-jobs/pyspark/etl.py",
    "PyFiles": ["tos://las-jobs/pyspark/utils.zip"],
    "Files": ["tos://las-jobs/pyspark/data/source.csv"],
    "SparkConf": "{\"spark.driver.memory\":\"4g\",\"spark.python.worker.memory\":\"2g\"}",
    "MainArguments": "--input tos://data/raw --output tos://data/processed --partitions 10"
}
```

##### 1.3 RayJob 类型

**参数**

| 字段名 | 类型 | 是否必须 | 描述 |
|--------|------|----------|------|
| VolcanoQueue | String | 否 | Volcano 队列名称 |
| UseExistingRayCluster | Boolean | 是 | 是否使用已有 Ray 集群（默认：`false`） |
| ExistingRayClusterName | String | 否 | 已有 Ray 集群名，`UseExistingRayCluster` 为 `true` 时必填 |
| IsCustomImage | Boolean | 是 | 是否使用自定义镜像（默认：`false`） |
| CustomImageRepoUser | String | 否 | 自定义镜像仓库用户（仅半托管需要） |
| CustomImageRepoPassword | String | 否 | 自定义镜像仓库密码（仅半托管需要） |
| ImageType | String | 否 | 镜像类型，可选值：`ray`, `ray-ds`, `ray-ml` |
| Image | String | 是 | 镜像地址 |
| HeadCpu | Double | 是 | Head 节点 CPU 核数（默认：2.0） |
| HeadMem | Double | 是 | Head 节点内存大小（单位：GB，默认：4.0） |
| HeadStorageConfig | StorageConfig | 否 | Head 节点存储配置（结构见下方） |
| HeadSchedulePolicy | String | 是 | Head 节点调度策略 |
| WorkerCpu | Double | 是 | Worker 节点 CPU 核数（默认：4.0） |
| WorkerMem | Double | 是 | Worker 节点内存大小（单位：GB，默认：8.0） |
| WorkerGpuSpec | String | 否 | Worker GPU 规格 |
| WorkerGpuNum | Integer | 否 | Worker GPU 卡数 |
| WorkerReplicas | Integer | 是 | Worker 节点数量（默认：2） |
| WorkerStorageConfig | StorageConfig | 否 | Worker 节点存储配置 |
| WorkerSchedulePolicy | String | 否 | Worker 节点调度策略 |
| WorkingDirType | String | 是 | 工作目录类型，可选值：`tos`, `mount`, `in-image` |
| WorkingDir | String | 是 | 工作目录路径 |
| Entrypoint | String | 是 | 执行命令（如 `python main.py --epochs 10`） |
| GcsFaultToleranceOptions | Boolean | 是 | GCS 容灾开关 |
| GcsRedisAddress | String | 否 | GCS Redis 地址 |
| GcsRedisPass | String | 否 | GCS Redis 密码 |
| HeadGpuAmount | Double | 否 | Head 节点 GPU 数量 |
| WorkerGpuAmount | Double | 否 | Worker 节点 GPU 数量 |

**针对 Serverless Ray 的附加参数**

| 字段名 | 类型 | 是否必须 | 描述 |
|--------|------|----------|------|
| EnvVars | List<EnvVar> | 否 | 环境变量列表，每个元素包含 `Name` 和 `Value` |
| Autoscaling | Object | 否 | 弹性伸缩配置，包含 `EnableAutoscaling`（Boolean）、`MinReplicas`（Integer）、`MaxReplicas`（Integer） |
| CrossVpc | Object | 否 | 跨 VPC 配置，包含 `CrossVpcEnabled`（Boolean）、`CrossVpcId`（String）、`Zones`（List，每个 Zone 包含 `CrossVpcSubnetId` 和 `ZoneId`）、`CrossVpcSgId`（String） |
| IdleTimeout | Object | 否 | 空闲超时回收配置，包含 `EnableIdleTimeout`（Boolean）、`Timeout`（Integer）、`TimeUnite`（TimeUnitEnum，0:秒,1:分钟,2:小时,4:天,5:月） |

**StorageConfig 结构**

```json
{
    "Volumes": [
        {
            "Pvc": "my-pvc",
            "Name": "volume-1"
        }
    ],
    "VolumeMounts": [
        {
            "MountPath": "/data",
            "VolumeName": "volume-1",
            "ReadOnly": false
        }
    ]
}
```

**RayJob 示例**

```json
{
    "VolcanoQueue": "mytestqueue",
    "UseExistingRayCluster": false,
    "IsCustomImage": true,
    "ImageType": "ray-ml",
    "Image": "cr.bytedance.com/las/ray:2.9.0-py39",
    "HeadCpu": 4.0,
    "HeadMem": 8.0,
    "HeadStorageConfig": {
        "Volumes": [{"Pvc": "my-pvc", "Name": "volume-1"}],
        "VolumeMounts": [{"MountPath": "/data", "VolumeName": "volume-1", "ReadOnly": false}]
    },
    "HeadSchedulePolicy": "{xxx}",
    "WorkerCpu": 8.0,
    "WorkerMem": 16.0,
    "WorkerGpuSpec": "NVIDIA",
    "WorkerGpuNum": 1,
    "WorkerReplicas": 3,
    "WorkerStorageConfig": {
        "Volumes": [{"Pvc": "my-pvc", "Name": "volume-1"}],
        "VolumeMounts": [{"MountPath": "/data", "VolumeName": "volume-1", "ReadOnly": false}]
    },
    "WorkerSchedulePolicy": "{xxx}",
    "WorkingDirType": "tos",
    "WorkingDir": "tos://las-jobs/ray/train",
    "Entrypoint": "python train.py --data-path ./data --model-name resnet50 --epochs 50",
    "EnvVars": [
        {"Name": "PYTHONPATH", "Value": "/app"}
    ],
    "Autoscaling": {
        "EnableAutoscaling": true,
        "MinReplicas": 2,
        "MaxReplicas": 10
    }
}
```

#### 返回数据结构
- 字段描述

| 字段名 | 类型 | 描述          |
|--------|------|-------------|
| JobDefinitionId | String | 新创建的作业模板 ID |
| RequestId | String | 请求 ID，用于追踪  |

创建成功时，返回的 JSON 结构如下：

**示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314155712CF91A622A26D036E32E4",
        "Action": "CreateJobDefinition",
        "Version": "2024-06-13",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "JobDefinitionId": "85"
    }
}
```

### 2. 作业模板详情

**接口描述**  
获取指定作业模板的详细信息。

**请求方式**： `POST`  
**Action**： `GetJobDefinition`

**请求参数**

| 字段名 | 类型 | 是否必须 | 描述      |
|--------|------|----------|---------|
| Id | String | 是 | 作业模板 ID |


**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action GetJobDefinition \
  --method POST \
  --body '{
    "Id": "job-def-123"
  }'
```

**请求参数示例**（JSON）

```json
{
    "Id": "job-def-123"
}
```

**响应参数**

| 字段名 | 字段类型 | 描述                                                     |
|--------|----------|--------------------------------------------------------|
| Id | Int | 作业模板Id                                                 |
| JobDefinitionName | String | 作业模板名称（长度1-128字符）                                      |
| JobType | JobTypeEnum | 作业类型，可选值：`SparkJar`, `PySpark`, `RayJob`, `RayService` |
| Engine | ExecutionEngineEnum | 执行引擎，可选值：`Spark`, `Presto`, `Hive`, `Ray`              |
| ResourceType | ResourceTypeEnum | 资源类型，可选值：`EMR Serverless`, `EMR_ON_VKE`, `EMR_ON_ECS`  |
| ResourceId | String | 资源 ID                                                  |
| DevelopMode | DevelopModeEnum | 开发类型，可选值 `UI`, `Json`, `Yaml`                          |
| JobDefinitionContent | String | 作业内容，`JobDefinitionContent` 同创建作业                      |
| Description | String | 作业描述                                                   |

**响应示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314155913647B9B2392ABD01F50DB",
        "Action": "GetJobDefinition",
        "Version": "2024-06-13",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Id": "85",
        "JobDefinitionName": "liubin_test",
        "JobType": "PySpark",
        "Engine": "Spark",
        "ResourceType": "EMR_SERVERLESS",
        "ResourceId": "1238543785583968256-0",
        "ResourceName": "公共队列-Default",
        "DevelopMode": "UI",
        "JobDefinitionContent": {
            "JobType": "PySpark",
            "VolcanoQueue": null,
            "StorageMounts": [],
            "MainClass": null,
            "MainApplicationFile": "tos://1-2lx-hms-4923rwisyr5az4knka6g/spark-eventlog-dir/",
            "Jars": [],
            "Files": [],
            "PyFiles": [],
            "Archives": [],
            "SparkConf": null,
            "MainArguments": null
        },
        "JobDefinitionYaml": null,
        "Conf": {},
        "TabId": null,
        "AccountId": 2100005493,
        "CreatorIdentityId": "21177421",
        "CreatorIdentityType": "User",
        "CreatorName": "liubin.007@bytedance.com",
        "IdentityId": "21177421",
        "IdentityType": "User",
        "IsOnline": true,
        "IsDeleted": false,
        "Description": "测试",
        "LastExecuteTime": "2026-03-14T15:57:12",
        "CreateTime": "2026-03-14T15:57:12",
        "UpdateTime": "2026-03-14T15:57:12",
        "IsResourceReleased": false
    }
}
```


### 3. 修改作业模板

**接口描述**  
更新指定作业模板的配置信息。

**请求方式**： `POST`  
**Action**： `UpdateJobDefinition`

**请求参数**

| 字段名 | 字段类型 | 是否必须 | 描述                                               |
|--|----------|----------|--------------------------------------------------|
| Id | String | 是 | 作业模板 ID                                          |
| JobDefinitionName | String | 是 | 作业模板名称（长度1-128字符）                                |
| JobType | JobTypeEnum | 是 | 作业类型，可选值：`SparkJar`, `PySpark`, `RayJob`, `RayService` |
| ResourceId | String | 是 | 资源 ID                                            |
| ResourceName | String | 是 | 资源名称                                             |
| ResourceType | ResourceTypeEnum | 是 | 资源类型，可选值：`EMR Serverless`, `EMR_ON_VKE`, `EMR_ON_ECS` |
| DevelopMode | DevelopModeEnum | 是 | 开发类型，可选值 `UI`, `Json`, `Yaml`                    |
| JobDefinitionContent | String | 是 | 作业内容，`JobDefinitionContent` 内容与创建作业相同            |
| Description | String | 否 | 作业描述                                             |


**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action UpdateJobDefinition \
  --method POST \
  --body '{
    "Id": "job-def-789",
    "JobDefinitionName": "updated-ray-job",
    "Description": "更新后的Ray分布式训练作业"
  }'
```

- JobDefinitionContent的传参可参考创建作业定义中JobDefinitionContent字段结构描述

**请求参数示例**（JSON）

```json
{
    "JobDefinitionName": "liubin_test",
    "JobType": "PySpark",
    "ResourceType": "EMR_SERVERLESS",
    "Conf": {},
    "ResourceId": "1238543785583968256-0",
    "ResourceName": "公共队列-Default",
    "DevelopMode": "UI",
    "Description": "测试333",
    "JobDefinitionContent": {
        "JobType": "PySpark",
        "StorageMounts": [],
        "MainClass": null,
        "MainApplicationFile": "tos://1-2lx-hms-4923rwisyr5az4knka6g/spark-eventlog-dir/",
        "Jars": [],
        "Files": [],
        "PyFiles": [],
        "Archives": [],
        "SparkConf": null,
        "MainArguments": null,
        "UseExistingRayCluster": false,
        "Volumes": [],
        "VolumeMounts": []
    },
    "Id": "85",
    "ProjectName": "default",
    "UserLocale": "zh"
}
```

**响应参数**

| 字段名 | 字段类型 | 描述 |
|--------|----------|------|
| ResponseMetadata | ResponseMetadata | 响应元数据 |
| Result | Boolean | 修改结果（true表示成功） |

**响应示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314160010DAC64E2A3183DF2BD92D",
        "Action": "UpdateJobDefinition",
        "Version": "2024-06-13",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": true
}
```


### 4. 运行作业模板

**接口描述**  
基于指定的作业模板运行作业。

**请求方式**： `POST`  
**Action**： `RunJobDefinition`

**请求参数**

| 字段名 | 字段类型 | 是否必须 | 描述      |
|--------|----------|----------|---------|
| JobDefinitionId | String | 是 | 作业模板 ID |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action RunJobDefinition \
  --method POST \
  --body '{
    "JobDefinitionId": "job-def-123"
  }'
```

**请求参数示例**（JSON）

```json
{
    "JobDefinitionId": "job-def-123"
}
```

**响应参数**

| 字段名 | 字段类型 | 描述 |
|--------|----------|------|
| ResponseMetadata | ResponseMetadata | 响应元数据 |
| Result | Integer | 作业运行 ID |

**响应示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314160548EDC620A02521042C7787",
        "Action": "RunJobDefinition",
        "Version": "2024-06-13",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": 325894298
}
```

### 5. 作业模板列表 (ListJobDefinitions)

**接口描述**  
查询作业模板列表

**请求方式**： `POST`  
**Action**： `ListJobDefinitions`  
**Version**： `2024-06-13`

**请求参数**

| 字段名 | 字段类型 | 是否必须 | 描述 |
|--------|----------|----------|------|
| FileSystemIds | List<String> | 否 | 文件系统id |
| HasFsxMount | Boolean | 否 | 筛选作业挂载fsx的 |

**调用示例**

```bash
python ./scripts/on_serverless/emr_serverless_cli.py \
  --action ListJobDefinitions \
  --method POST \
  --body '{}'
```

**请求参数示例**（JSON）

```json
{
    
}
```

**返回参数**

| 字段名 | 字段类型 | 描述 |
|--------|----------|------|
| ResponseMetadata | ResponseMetadata | 响应元数据 |
| Result | Object | 查询结果 |

**Result 对象字段**

| 字段名 | 字段类型 | 描述 |
|--------|----------|------|
| Data | Array<JobDefinition> | 作业定义列表 |
| Limit | Integer | 每页数量 |
| Offset | Integer | 偏移量 |
| Total | Integer | 总记录数 |

**JobDefinition 对象字段**

| 字段名 | 字段类型 | 描述       |
|--------|----------|----------|
| Id | String | 作业定义ID   |
| JobDefinitionName | String | 作业模板名称   |
| JobType | String | 作业类型     |
| Engine | String | 执行引擎     |
| ResourceType | String | 资源类型     |
| ResourceId | String | 资源ID     |
| ResourceName | String | 资源名称     |
| DevelopMode | String | 开发模式     |
| JobDefinitionContent | Object | 作业模板内容   |
| JobDefinitionYaml | String | 作业YAML内容 |
| Conf | Object | 配置信息     |
| TabId | String | 标签页ID    |
| AccountId | Integer | 账户ID     |
| CreatorIdentityId | String | 创建者身份ID  |
| CreatorIdentityType | String | 创建者身份类型  |
| CreatorName | String | 创建者名称    |
| IdentityId | String | 身份ID     |
| IdentityType | String | 身份类型     |
| IsOnline | Boolean | 是否在线     |
| IsDeleted | Boolean | 是否已删除    |
| Description | String | 描述信息     |
| LastExecuteTime | String | 最后执行时间   |
| CreateTime | String | 创建时间     |
| UpdateTime | String | 更新时间     |
| IsResourceReleased | Boolean | 资源是否已释放  |

**JobDefinitionContent 对象字段**

| 字段名 | 字段类型 | 描述 |
|--------|----------|------|
| JobType | String | 作业类型 |
| VolcanoQueue | String | Volcano队列 |
| StorageMounts | Array | 存储挂载列表 |
| MainClass | String | 主类 |
| MainApplicationFile | String | 主应用文件 |
| Jars | Array<String> | JAR包列表 |
| Files | Array<String> | 文件列表 |
| PyFiles | Array<String> | Python文件列表 |
| Archives | Array<String> | 归档文件列表 |
| SparkConf | String | Spark配置 |
| MainArguments | String | 主参数 |

**响应示例**

```json
{
    "ResponseMetadata": {
        "RequestId": "20260314175800E6EBB1F20066336CE364",
        "Action": "ListJobDefinitions",
        "Version": "2024-06-13",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null
    },
    "Result": {
        "Data": [
            {
                "Id": "86",
                "JobDefinitionName": "liubin_test12",
                "JobType": "PySpark",
                "Engine": "Spark",
                "ResourceType": "EMR_SERVERLESS",
                "ResourceId": "1238543785583968256-0",
                "ResourceName": "公共队列-Default",
                "DevelopMode": "UI",
                "JobDefinitionContent": {
                    "JobType": "PySpark",
                    "VolcanoQueue": null,
                    "StorageMounts": [],
                    "MainClass": null,
                    "MainApplicationFile": "tos://amoro-lance-test/archive/",
                    "Jars": [],
                    "Files": [],
                    "PyFiles": [],
                    "Archives": [],
                    "SparkConf": null,
                    "MainArguments": null
                },
                "JobDefinitionYaml": null,
                "Conf": {},
                "TabId": null,
                "AccountId": 2100005493,
                "CreatorIdentityId": "21177421",
                "CreatorIdentityType": "User",
                "CreatorName": "liubin.007@bytedance.com",
                "IdentityId": "21177421",
                "IdentityType": "User",
                "IsOnline": true,
                "IsDeleted": false,
                "Description": null,
                "LastExecuteTime": "2026-03-14T17:56:07",
                "CreateTime": "2026-03-14T17:56:07",
                "UpdateTime": "2026-03-14T17:56:07",
                "IsResourceReleased": false
            }
        ],
        "Limit": 10,
        "Offset": 1,
        "Total": 3
    }
}
```

---


