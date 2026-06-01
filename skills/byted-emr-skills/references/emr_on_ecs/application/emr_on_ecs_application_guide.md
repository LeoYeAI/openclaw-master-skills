# EMR on ECS 应用管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的应用列表、组件列表、组件实例列表、执行应用操作等管理。

## 说明

本文档提供 EMR on ECS 中 **应用管理** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 应用管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 应用管理操作

### 1. 应用列表查询

**接口描述**  
调用 ListApplications，获取一个 E-MapReduce（EMR）集群应用列表信息。

**使用场景**  
查询指定集群下的所有应用信息。

**请求方式**： `POST`  
**Action**： `ListApplications`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListApplications | 要执行的操作，取值：ListApplications |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationNames | Array of String | 否 | ["HDFS"] | 应用名称列表 |
| MaxResults | Integer | 否 | 10 | 返回的最大记录数 |
| NextToken | String | 否 | xxx | 分页查询的下一页token |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListApplications \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListApplications","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求示例**
```json
{
   "ClusterId":"emr-xxx"
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 集群应用信息列表 |
| ApplicationName | String | HDFS | 应用名 |
| ApplicationVersion | String | 3.3.4 | 应用版本 |
| User | String | hdfs | 应用用户 |
| Group | String | hadoop | 应用用户组 |
| ApplicationConfigHome | String | /etc/emr/${name}/conf | 应用配置路径 |
| ApplicationHome | String | /usr/lib/emr/current/${name} | 应用安装路径 |
| SupportClient | Boolean | false | 是否支持客户端 |
| ApplicationState | String | NORMAL | 服务状态（NORMAL-正常, WARNING-告警, STOPPED-已停止, INIT-初始化中, INSTALLING-安装中, INSTALLED-已安装, STARTING-启动中, STARTED-已启动, STOPPING-停止中, UNINSTALLING-卸载中, UNINSTALLED-已卸载, EXCEPTION-异常） |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | IcKlh2bKXei9E5Uv/3XjOA== | 分页查询的下一页token |
| TotalCount | Integer | 17 | 总记录数 |


**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "202312051929157D73231DC5Cxxx",
        "Action": "ListApplications",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "Items": [
            {
                "ApplicationName": "PROMETHEUS",
                "ReleaseVersion": "1.1.0",
                "User": "prometheus",
                "Group": "prometheus",
                "ApplicationConfigHome": "/etc/emr/${name}/conf",
                "ApplicationHome": "/usr/lib/emr/current/${name}",
                "SupportClient": false
            },
            {
                "ApplicationName": "KNOX",
                "ReleaseVersion": "1.5.0",
                "User": "knox",
                "Group": "knox",
                "ApplicationConfigHome": "/etc/emr/${name}/conf",
                "ApplicationHome": "/usr/lib/emr/current/${name}",
                "SupportClient": false
            }
        ],
        "TotalCount": 17,
        "MaxResults": 10,
        "NextToken": "IcKlh2bKXei9E5Uv/3XjOA=="
    }
}
```

### 2. 组件列表查询

**接口描述**  
调用 ListComponents，获取一个 E-MapReduce（EMR）集群组件列表。

**使用场景**  
查询指定集群下的所有组件信息。

**请求方式**： `POST`  
**Action**： `ListComponents`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListComponents | 要执行的操作，取值：ListComponents |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationNames | Array of String | 否 | ["HDFS"] | 服务名称列表 |
| ComponentNames | Array of String | 否 | ["DATANODE"] | 组件名称列表 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListComponents \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListComponents","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求示例**
```json
{
   "ClusterId":"emr-xxx"
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 组件信息列表 |
| ApplicationName | String | HDFS | 应用名称 |
| ComponentName | String | DATANODE | 组件名称 |
| Replica | Integer | 0 | 副本数 |
| ClusterId | String | emr-xxx | 集群ID |
| ComponentState | String | STARTED | 运行状态（STARTED-已启动, STOPPED-已停止, INIT-初始化中, INSTALLING-安装中, INSTALLED-已安装, STARTING-启动中, STOPPING-停止中, UNINSTALLING-卸载中, UNINSTALLED-已卸载, EXCEPTION-异常） |
| CreateTime | Long | xxx | 创建时间 |
| StartTime | Long | xxx | 开始时间 |
| TotalCount | Integer | 6 | 总记录数 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | null | 分页查询的下一页token |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231205115604A412C01E25FABxxx",
        "Action": "ListComponents",
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
                "ApplicationName": "HDFS",
                "ComponentName": "NAMENODE",
                "Replica": 0,
                "ComponentState": "STARTED",
                "CreateTime": null,
                "StartTime": null
            },
            {
                "ClusterId": "emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "JOURNALNODE",
                "Replica": 0,
                "ComponentState": "STARTED",
                "CreateTime": null,
                "StartTime": null
            },
            {
                "ClusterId": "emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "DATANODE",
                "Replica": 0,
                "ComponentState": "STARTED",
                "CreateTime": null,
                "StartTime": null
            },
            {
                "ClusterId": "emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "ROUTER",
                "Replica": 0,
                "ComponentState": "STARTED",
                "CreateTime": null,
                "StartTime": null
            },
            {
                "ClusterId": "emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "ZKFC",
                "Replica": 0,
                "ComponentState": "STARTED",
                "CreateTime": null,
                "StartTime": null
            },
            {
                "ClusterId": "emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "HdfsFoundation",
                "Replica": 0,
                "ComponentState": "INSTALLED",
                "CreateTime": null,
                "StartTime": null
            }
        ],
        "TotalCount": 6,
        "MaxResults": 10,
        "NextToken": null
    }
}
```

### 3. 组件实例列表查询

**接口描述**  
调用 ListComponentInstances，获取一个 E-MapReduce（EMR）集群组件实例列表。

**使用场景**  
查询指定集群下的所有组件实例信息。

**请求方式**： `POST`  
**Action**： `ListComponentInstances`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListComponentInstances | 要执行的操作，取值：ListComponentInstances |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationNames | Array of String | 否 | ["HDFS"] | 服务名称列表 |
| NodeIds | Array of String | 否 | ["master-1.emr-xxx"] | 节点ID列表 |
| NodeNames | Array of String | 否 | ["OpenApi-MasterGroup"] | 节点名称列表 |
| ComponentStates | Array of String | 否 | ["STARTED"] | 组件状态列表 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListComponentInstances \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListComponentInstances","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求示例**
```json
{
   "ClusterId":"emr-xxx"
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 组件实例信息列表 |
| ClusterId | String | emr-xxx | 集群ID |
| NodeId | String | master-1-2.emr-xxx | 节点ID |
| ApplicationName | String | HDFS | 应用名称 |
| ComponentName | String | ZKFC | 组件名称 |
| InstanceState | String | STARTED | 组件实例状态（STARTED-已启动, STOPPED-已停止, INIT-初始化中, INSTALLING-安装中, INSTALLED-已安装, STARTING-启动中, STOPPING-停止中, UNINSTALLING-卸载中, UNINSTALLED-已卸载, EXCEPTION-异常） |
| CreateTime | String | xxx | 创建时间 |
| StartTime | String | xxx | 开始时间 |
| TotalCount | Integer | 6 | 总记录数 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | null | 分页查询的下一页token |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231205115604A412C01E25FABxxx",
        "Action": "ListComponentInstances",
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
                "NodeId": "master-1.emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "NAMENODE",
                "InstanceState": "STARTED",
                "CreateTime": "2023-12-01T10:00:00Z",
                "StartTime": "2023-12-01T10:05:00Z"
            },
            {
                "ClusterId": "emr-xxx",
                "NodeId": "master-2.emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "NAMENODE",
                "InstanceState": "STARTED",
                "CreateTime": "2023-12-01T10:00:00Z",
                "StartTime": "2023-12-01T10:05:00Z"
            },
            {
                "ClusterId": "emr-xxx",
                "NodeId": "core-1.emr-xxx",
                "ApplicationName": "HDFS",
                "ComponentName": "DATANODE",
                "InstanceState": "STARTED",
                "CreateTime": "2023-12-01T10:00:00Z",
                "StartTime": "2023-12-01T10:05:00Z"
            }
        ],
        "TotalCount": 3,
        "MaxResults": 10,
        "NextToken": null
    }
}
```

### 4. 执行应用操作

**接口描述**  
调用 RunApplicationAction，对一个 E-MapReduce（EMR）集群中的各类服务进行重启等操作。

**使用场景**  
对EMR集群中的应用组件执行安装、启动、停止、重启等管理操作。

**请求方式**： `POST`  
**Action**： `RunApplicationAction`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | RunApplicationAction | 要执行的操作，取值：RunApplicationAction |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 应用名称 |
| ComponentName | String | 否 | NAMENODE | 组件名称 |
| ActionName | String | 是 | RESTART | 操作名称（INSTALL-安装, UNINSTALL-卸载, START-启动, RESTART-重启, ROLLING_RESTART-滚动重启, STOP-停止, REBALANCE-再平衡, REFRESHQUEUE-刷新队列, DECOMMISSION_COMPONENT-下线组件, RECOMMISSION_COMPONENT-上线组件） |
| CommandParams | Array of Object | 否 | [{"Key":"hostNames","Value":"[\"master-1-1.emr-xxx\"]"}] | 操作参数 |
| Remark | String | 是 | test | 操作备注 |
| ClientToken | String | 否 | xxxxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action RunApplicationAction \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"RunApplicationAction","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS","ComponentName":"NAMENODE","ActionName":"RESTART","Remark":"重启NameNode服务"}'
```

**请求示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName":"HDFS",
    "ComponentName":"NAMENODE",
    "ActionName":"RESTART",
    "CommandParams":[{
        "Key":"hostNames",
        "Value":"[\"master-1-1.emr-xxx\"]"
    }],
    "Remark":"openapi重启spark服务测试"
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperateId | String | xxx | 集群操作ID |
| ResultData | Object | null | 结果数据 |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "202312042119240BF21498512872xxx",
        "Action": "RunApplicationAction",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "OperateId": "xxx",
        "ClusterId": "emr-xxx",
        "ResultData": null
    }
}
```




