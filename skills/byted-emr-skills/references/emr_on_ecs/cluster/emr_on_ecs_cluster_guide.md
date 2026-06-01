# EMR on ECS 集群管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的集群列表、集群详情查询、更新集群属性等管理。

## 说明

本文档提供 EMR on ECS 中 **集群** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 集群管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --version 2023-08-15 \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 集群管理操作 

### 1. 集群列表查询 

**接口描述**  
调用 ListClusters，查询该账号下所有 E-MapReduce（EMR）集群。 

**请求方式**： `POST`  
**Action**： `ListClusters`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。 

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListClusters | 要执行的操作，取值：ListClusters |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterName | String | 否 | OpenApiHadoop3.7.0-xxx | 集群名称，模糊查询 |
| ClusterId | String | 否 | emr-xxx | 集群ID，模糊查询 |
| ReleaseVersion | String | 否 | 3.7.0 | 集群版本 |
| ProjectName | String | 否 | default | 项目名称 |
| CreateTimeBefore | String | 否 | 1701764286000 | 开始日期，时间戳单位ms |
| CreateTimeAfter | String | 否 | 1701764286300 | 结束日期，时间戳单位ms |
| ClusterIds | Array of String | 否 | ["emr-xxx"] | 集群ID列表 |
| ClusterTypes | Array of String | 否 | ["Hadoop"] | 集群类型列表 |
| ClusterStates | Array of String | 否 | ["RUNNING"] | 集群状态列表 |
| ChargeTypes | Array of String | 否 | ["POST"] | 集群付费类型列表 |
| Tags | Array of Tag | 否 | xxx | 标签列表 |
| MaxResults | Integer | 否 | 10 | 返回的最大记录数 |
| NextToken | String | 否 | 57N8YtDWxxx | 分页查询的下一页token |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListClusters \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{
    "ClusterStates": [
        "CREATING",
        "FAILED",
        "TERMINATED_WITH_ERROR",
        "RUNNING",
        "EXCEPTION",
        "WARNING",
        "PAUSED",
        "PAUSING",
        "RESTORING",
        "SHUTDOWN",
        "TERMINATING",
        "PENDING_FOR_PAYMENT"
    ],
    "MaxResults": 20
}'
```

**请求参数示例**  
```json
{ 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构 

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| RegionId | String | cn-beijing | 地域ID |
| ProjectName | String | default | 项目名称 |
| ClusterId | String | emr-xxx | 集群ID |
| ClusterName | String | OpenApiHadoop3.7.0-xxx | 集群名称 |
| ClusterType | String | Hadoop | 集群类型 |
| ReleaseVersion | String | 3.7.0 | 集群版本 |
| SecurityGroupId | String | sg-xxx | 集群全局安全组ID |
| VpcId | String | vpc-xxx | 私有网络 |
| Creator | String | 6xxx | 创建者 |
| AccountId | String | 210xxx | 账号ID |
| NodeAttribute | NodeAttribute | {"ZoneId":"cn-beijing-b","EcsIamRole":"VEECSforEMRRole"} | 集群的全局节点属性 |
| ClusterState | String | RUNNING | 集群状态，可选值：PENDING_FOR_PAYMENT,CREATING,RUNNING,TERMINATING,TERMINATED,TERMINATED_WITH_ERROR,FAILED,SHUTDOWN |
| ChargeType | String | POST | 付费类型，可选值：PRE（包年包月）、POST（按量付费） |
| CreateTime | Long | 1701764286214 | 创建时间，单位ms |
| ReadyTime | Long | 1701764779378 | 集群创建完成时间，单位ms |
| ExpireTime | Long | 1701764286214 | 集群过期时间，单位ms |
| TerminateTime | Long | 1701764286214 | 集群终止时间，单位ms |
| StateChangeReason | StateChangeReason | null | 状态变更原因 |

- NodeAttribute

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ZoneId | String | cn-beijing-b | 可用区ID（NodeAttribute的子字段） |
| EcsIamRole | String | VEECSforEMRRole | ECS上绑定的IAM Role名称（NodeAttribute的子字段） |

- StateChangeReason

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| code | String |  | 状态更新码（StateChangeReason的子字段） |
| reason | String |  | 状态更新的原因详情（StateChangeReason的子字段） |


**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "20231205174720B3E08B8D2FB8E9xxx", 
        "Action": "ListClusters", 
        "Version": "2023-08-15", 
        "Service": "emr", 
        "Region": "cn-beijing", 
        "Error": null, 
        "Deprecated": false 
    }, 
    "Result": { 
        "Items": [ 
            { 
                "RegionId": "cn-beijing", 
                "ProjectName": "default", 
                "ClusterId": "emr-xxx", 
                "ClusterName": "OpenApiHadoop3.7.0-xxx", 
                "ClusterType": "Hadoop", 
                "ReleaseVersion": "3.7.0", 
                "SecurityGroupId": "sg-xxx", 
                "VpcId": "xxx", 
                "Creator": "6xxx", 
                "AccountId": 2100xxx, 
                "NodeAttribute": { 
                    "ZoneId": "cn-beijing-b", 
                    "EcsIamRole": "VEECSforEMRRole", 
                    "LoginUserName": null 
                }, 
                "ClusterState": "RUNNING", 
                "ChargeType": "POST", 
                "CreateTime": 1701764286214, 
                "ReadyTime": 1701764779378, 
                "ExpireTime": null, 
                "TerminateTime": null, 
                "StateChangeReason": null 
            } 
        ], 
        "TotalCount": 1, 
        "MaxResults": 10, 
        "NextToken": "57N8YtDWZ1LbCkWySngtD53oS+eCiHNIpxxx" 
    } 
}
```

### 2. 获取集群详情

**接口描述**  
调用 GetCluster，查询该账号下 E-MapReduce（EMR）集群详情。

**请求方式**： `POST`  
**Action**： `GetCluster`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | GetCluster | 要执行的操作，取值：GetCluster |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action GetCluster \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx" 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Tags | Array of Tag | [{"Key":"volc:emr:create_by","Value":"EMR"},{"Key":"volc:emr:emr_cluster_type","Value":"Hadoop"},{"Key":"volc:emr:location","Value":"cn-beijing/cn-beijing-b"}] | 标签列表 |
| RegionId | String | cn-beijing | 地域ID |
| ProjectName | String | default | 项目名称 |
| ClusterId | String | emr-xxx | 集群ID |
| ClusterName | String | OpenApiHadoop3.7.0-xxx | 集群名称 |
| ClusterType | String | Hadoop | 集群类型 |
| ReleaseVersion | String | 3.7.0 | 集群版本 |
| SecurityGroupId | String | sg-xxx | 集群全局安全组ID |
| VpcId | String | vpc-xxx | 集群vpcId |
| NodeAttribute | NodeAttribute | {"ZoneId":"cn-beijing-b","EcsIamRole":"VEECSforEMRRole"} | 集群全局的节点信息 |
| ClusterDomainNames | Array of String | ["emr-xxx.offline-cn-beijing.emr-volces.com","offline-cn-beijing.emr-volces.com"] | 集群DNS域名后缀 |
| AccountId | Long | 2100xxx | 账号ID |
| CreatorId | Long | 6xxx | 创建者ID |
| CreatorName | String | xxx | 创建者名称 |
| Autorenew | Boolean | false | 是否自动续费 |
| AutorenewPeriod | Integer | 1 | 自动续费周期 |
| AutorenewPeriodUnit | String | Week,Month,Year | 自动续费周期单位 |
| ClusterState | String | RUNNING | 集群状态，可选值：PENDING_FOR_PAYMENT,CREATING,RUNNING,TERMINATING,TERMINATED,TERMINATED_WITH_ERROR,FAILED,SHUTDOWN |
| ChargeType | String | POST | 付费类型，可选值：PRE（包年包月）、POST（按量付费） |
| DeployMode | String | HA | 集群部署模式，可选值：NORMAL,HA |
| SecurityMode | String | NORMAL | 安全模式，可选值：NORMAL,KERBEROS |
| CreateTime | Long | 1703437906000 | 集群创建时间 |
| ReadyTime | Long | 1703437906000 | 集群创建完成时间 |
| ExpireTime | Long | 1703437906000 | 集群过期时间 |
| TerminateTime | Long | 1703437906000 | 集群终止时间 |
| StateChangeReason | StateChangeReason | xxx | 状态变更原因 |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "20231205194333E4CF0C48565Cxxx", 
        "Action": "GetCluster", 
        "Version": "2023-08-15", 
        "Service": "emr", 
        "Region": "cn-beijing", 
        "Error": null, 
        "Deprecated": false 
    }, 
    "Result": { 
        "RegionId": "cn-beijing", 
        "ProjectName": "default", 
        "ClusterId": "emr-xxx", 
        "ClusterName": "OpenApiHadoop3.7.0-xxx", 
        "ClusterType": "Hadoop", 
        "ReleaseVersion": "3.7.0", 
        "SecurityGroupId": "sg-xxx", 
        "VpcId": "vpc-xxx", 
        "NodeAttribute": { 
            "ZoneId": "cn-beijing-b", 
            "EcsIamRole": "VEECSforEMRRole", 
            "LoginUserName": null 
        }, 
        "ClusterDomainNames": [ 
            "emr-xxx.offline-cn-beijing.emr-volces.com", 
            "offline-cn-beijing.emr-volces.com" 
        ], 
        "AccountId": 210xxx, 
        "CreatorId": 64xxx, 
        "CreatorName": null, 
        "Autorenew": false, 
        "AutorenewPeriod": 1, 
        "AutorenewPeriodUnit": null, 
        "ClusterState": "RUNNING", 
        "ChargeType": "POST", 
        "DeployMode": "HIGH_AVAILABLE", 
        "SecurityMode": "SIMPLE", 
        "CreateTime": 1701764286214, 
        "ReadyTime": 1701770482932, 
        "ExpireTime": null, 
        "TerminateTime": null, 
        "Tags": null, 
        "StateChangeReason": null 
    } 
}
```

### 3. 更新集群属性

**接口描述**  
调用UpdateClusterAttribute，更新指定账号和 E-MapReduce（EMR）集群的属性，如集群名称。

**请求方式**： `POST`  
**Action**： `UpdateClusterAttribute`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateClusterAttribute | 要执行的操作，取值：UpdateClusterAttribute |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ClusterName | String | 是 | emr-test-xxx | 集群名称 |
| ClientToken | String | 否 | xxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateClusterAttribute \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx","ClusterName":"emr-openapi测试V1"}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx", 
    "ClusterName":"emr-openapi测试V1" 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | xxx | 集群ID |
| OperationId | String | emr-xxx | 集群操作ID |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "202312042119240BF214985128722xxx", 
        "Action": "UpdateClusterAttribute", 
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