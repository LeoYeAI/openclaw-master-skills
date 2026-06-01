# EMR on ECS 节点组管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的节点组列表、节点列表、扩容节点组磁盘、更新节点组ECS规格等管理。

## 说明

本文档提供 EMR on ECS 中 **节点组** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 节点组管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --version 2023-08-15 \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 节点组管理操作

### 1. 节点组列表查询

**接口描述**  
调用 ListNodeGroups，获取一个 E-MapReduce（EMR）集群节点组列表。

**使用场景**  
查询指定集群下的所有节点组信息。

**请求方式**： `POST`  
**Action**： `ListNodeGroups`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListNodeGroups | 要执行的操作，取值：ListNodeGroups |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| NodeGroupIds | Array of String | 否 | ["core-1.emr-xxx"] | 节点组ID列表 |
| NodeGroupNames | Array of String | 否 | ["CoreGroup"] | 节点组名称列表 |
| NodeGroupTypes | Array of String | 否 | ["CORE"] | 节点组类型列表，MASTER、CORE、TASK |
| MaxResults | Integer | 否 | 10 | 返回的最大记录数 |
| NextToken | String | 否 | xxx | 分页查询的下一页token |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListNodeGroups \
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
| ZoneId | String | cn-beijing-b | zoneID |
| NodeGroupId | String | core-1.emr-xxx | 节点组ID |
| NodeGroupName | String | CoreGroup | 节点组名称 |
| NodeGroupType | String | CORE | 节点组类型 |
| WithPublicIp | String | false | 是否开启公网 |
| ChargeType | String | PRE,POST | 付费类型 |
| EcsInstanceTypes | Array of String | ["ecs.r3i.xlarge"] | ecs实例规格列表 |
| SubnetIds | Array of String | ["subnet-xxx"] | 子网ID列表 |
| LayoutComponentNames | Array of String | ["NAMENODE","DATANODE"] | 部署的组件名称列表 |
| CreateTime | Long | 7564423 | 创建时间 |
| TerminateTime | Long | 7564423 | 集群终止时间 |
| SystemDisk | SystemDisk | {"Category": "cloud_essd", "Size": 80, "PerformanceLevel": "ESSD_FlexPL"} | 系统盘信息 |
| DataDisks | Array of DataDisk | [{"Category": "cloud_essd", "Size": 80, "PerformanceLevel": "ESSD_FlexPL", "Count": 1}] | 数据盘信息 |
| NodeGroupState | String | RUNNING, EXTENDING, REDUCING, DISK_EXTENDING, MODIFYING | 节点组状态 |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "20231205164557BD00623CC2xxx", 
        "Action": "ListNodeGroups", 
        "Version": "2023-08-15", 
        "Service": "emr", 
        "Region": "cn-beijing", 
        "Error": null, 
        "Deprecated": false 
    }, 
    "Result": { 
        "Items": [ 
            { 
                "ZoneId": null, 
                "NodeGroupId": "task-1.emr-xxx", 
                "NodeGroupName": "aa11", 
                "NodeGroupType": "TASK", 
                "WithPublicIp": "false", 
                "ChargeType": "POST", 
                "EcsInstanceTypes": [ 
                    "ecs.r2i.xlarge" 
                ], 
                "SubnetIds": null, 
                "LayoutComponentNames": [], 
                "CreateTime": null, 
                "TerminateTime": null, 
                "SystemDisk": { 
                    "Size": 80, 
                    "VolumeType": "ESSD_PL0" 
                }, 
                "DataDisks": [ 
                    { 
                        "Size": 80, 
                        "VolumeType": "ESSD_PL0", 
                        "Count": 1 
                    } 
                ], 
                "NodeGroupState": "RUNNING" 
            }, 
            { 
                "ZoneId": null, 
                "NodeGroupId": "core-1.emr-xxx", 
                "NodeGroupName": "CoreGroup", 
                "NodeGroupType": "CORE", 
                "WithPublicIp": "false", 
                "ChargeType": "POST", 
                "EcsInstanceTypes": [ 
                    "ecs.r3i.xlarge" 
                ], 
                "SubnetIds": null, 
                "LayoutComponentNames": [], 
                "CreateTime": null, 
                "TerminateTime": null, 
                "SystemDisk": { 
                    "Size": 80, 
                    "VolumeType": "ESSD_PL0" 
                }, 
                "DataDisks": [ 
                    { 
                        "Size": 80, 
                        "VolumeType": "ESSD_PL0", 
                        "Count": 1 
                    } 
                ], 
                "NodeGroupState": "RUNNING" 
            }
        ], 
        "TotalCount": 3, 
        "MaxResults": 10, 
        "NextToken": "lnXl1C2wTNK9iCZYl6gbVA==" 
    } 
}
```

### 2. 节点列表查询

**接口描述**  
调用 ListNodes，获取一个 E-MapReduce（EMR）集群节点列表。

**使用场景**  
查询指定集群下的所有节点信息。

**请求方式**： `POST`  
**Action**： `ListNodes`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListNodes | 要执行的操作，取值：ListNodes |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| NodeIds | Array of String | 否 | ["core-1-2.emr-xxx"] | 节点ID列表 |
| NodeNames | Array of String | 否 | ["core-1-2.emr-xxx"] | 节点名称列表 |
| NodeStates | Array of String | 否 | ["RUNNING"] | 节点状态列表 |
| PrivateIps | Array of String | 否 | ["xxx"] | 节点私网IP列表 |
| PublicIps | Array of String | 否 | ["xxx"] | 公网IP列表 |
| MaxResults | Integer | 否 | 10 | 返回的最大记录数 |
| NextToken | String | 否 | 46FOxxx | 分页查询的下一页token |
| Fqdns | Array of String | 否 | ["core-1-2.emr-xxx.offline-cn-beijing.emr-volces.com"] | Fqdns列表 |
| NodeGroupIds | Array of String | 否 | ["core-1.emr-xxx"] | 节点组ID列表 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListNodes \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx","NodeIds":["master-1-1.emr-xxx"]}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx", 
    "NodeIds": ["master-1-1.emr-xxx"] 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| NodeGroupId | String | core-1.emr-xxx | 节点组ID |
| NodeId | String | core-1-2.emr-xxx | 节点ID |
| NodeName | String | core-1-2.emr-xxx | 节点名称 |
| NodeState | String | UNKNOWN,CREATING,RUNNING,STOPPING,STOPPED,REBOOTING,DELETED | 节点状态 |
| NodeFqdn | String | core-1-2.emr-xxx.offline-cn-beijing.emr-volces.com | 节点fqdn |
| PrivateIp | String | ["xxx"] | 内网IP |
| PublicIp | String | ["xxx"] | 公网IP |
| EcsInstanceType | String | ecs.g3i.2xlarge | ecs实例规格 |
| CreateTime | Long | 7553422 | 创建时间 |
| ReadyTime | Long | 7553422 | 准备完毕时间 |
| TerminateTime | String | 7553422 | 集群终止时间 |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "20231205192346B3E08B8D2Fxxx", 
        "Action": "ListNodes", 
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
                "NodeGroupId": null, 
                "NodeId": "task-1-1.emr-xxx", 
                "NodeName": "task-1-1.emr-xxx", 
                "NodeState": "CREATING", 
                "NodeFqdn": "task-1-1.emr-xxx.offline-cn-beijing.emr-volces.com", 
                "PrivateIp": "xxx", 
                "PublicIp": null, 
                "EcsInstanceType": "ecs.g3i.2xlarge", 
                "CreateTime": null, 
                "ReadyTime": null, 
                "TerminateTime": null 
            }, 
            { 
                "ClusterId": "emr-xxx", 
                "NodeGroupId": "core-1.emr-xxx", 
                "NodeId": "core-1-2.emr-xxx", 
                "NodeName": "core-1-2.emr-xxx", 
                "NodeState": "RUNNING", 
                "NodeFqdn": "core-1-2.emr-xxx.offline-cn-beijing.emr-volces.com", 
                "PrivateIp": "xxx", 
                "PublicIp": null, 
                "EcsInstanceType": "ecs.g3i.2xlarge", 
                "CreateTime": null, 
                "ReadyTime": null, 
                "TerminateTime": null 
            }, 
            { 
                "ClusterId": "emr-xxx", 
                "NodeGroupId": "core-1.emr-xxx", 
                "NodeId": "core-1-1.emr-xxx", 
                "NodeName": "core-1-1.emr-xxx", 
                "NodeState": "RUNNING", 
                "NodeFqdn": "core-1-1.emr-xxx.offline-cn-beijing.emr-volces.com", 
                "PrivateIp": "xxx", 
                "PublicIp": null, 
                "EcsInstanceType": "ecs.g3i.2xlarge", 
                "CreateTime": null, 
                "ReadyTime": null, 
                "TerminateTime": null 
            }, 
            { 
                "ClusterId": "emr-xxx", 
                "NodeGroupId": "master-1.emr-xxx", 
                "NodeId": "master-1-1.emr-xxx", 
                "NodeName": "master-1-1.emr-xxx", 
                "NodeState": "RUNNING", 
                "NodeFqdn": "master-1-1.emr-xxx.offline-cn-beijing.emr-volces.com", 
                "PrivateIp": "xxx", 
                "PublicIp": "xxx", 
                "EcsInstanceType": "ecs.c3i.4xlarge", 
                "CreateTime": null, 
                "ReadyTime": null, 
                "TerminateTime": null 
            } 
        ], 
        "TotalCount": 4, 
        "MaxResults": 10, 
        "NextToken": "46FOSv9T/1W1lVvcgDm1XQ==" 
    } 
}
```

### 3. 更新节点组属性

**接口描述**  
调用 UpdateNodeGroupAttribute，更新一个 E-MapReduce（EMR）集群下的一个节点组的属性。

**使用场景**  
修改指定节点组的属性，如节点组名称。

**请求方式**： `POST`  
**Action**： `UpdateNodeGroupAttribute`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateNodeGroupAttribute | 要执行的操作，取值：UpdateNodeGroupAttribute |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| NodeGroupName | String | 是 | CoreGroup-test | 节点组名称 |
| NodeGroupId | String | 是 | core-1.emr-xxx | 节点组ID |
| ClientToken | String | 否 | xxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateNodeGroupAttribute \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx","NodeGroupName":"CoreGroup-test","NodeGroupId":"core-1.emr-xxx"}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx", 
    "NodeGroupName":"CoreGroup-test", 
    "NodeGroupId":"core-1.emr-xxx" 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperationId | String | Orderxxx | 集群操作ID |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "202312042119240BF214985xxx", 
        "Action": "UpdateNodeGroupAttribute", 
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

### 4. 扩容节点组磁盘

**接口描述**  
调用 ScaleUpNodeGroupDisk，扩容一个 E-MapReduce（EMR）集群下的一个节点组的磁盘容量。

**使用场景**  
扩容指定节点组的磁盘容量。

**请求方式**： `POST`  
**Action**： `ScaleUpNodeGroupDisk`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ScaleUpNodeGroupDisk | 要执行的操作，取值：ScaleUpNodeGroupDisk |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| NodeGroupId | String | 是 | task-1.emr-xxx | 节点组ID |
| TargetDiskSize | Integer | 是 | 81 | 待扩容的目标磁盘大小，最小60GB，最大2048GB，单位GB |
| ClientToken | String | 否 | xxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ScaleUpNodeGroupDisk \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx","NodeGroupId":"task-1.emr-xxx","TargetDiskSize":81}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx", 
    "NodeGroupId":"task-1.emr-xxx", 
    "TargetDiskSize":81 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperationId | String | Order7xxx | 集群操作ID |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "202312042119240BF214985128xxx", 
        "Action": "ScaleUpNodeGroupDisk", 
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

### 5. 更新节点组ECS规格

**接口描述**  
调用 UpdateNodeGroupEcsSpec，更新一个 E-MapReduce（EMR）集群下的一个节点组的ECS规格。

**使用场景**  
修改指定节点组的ECS实例规格。

**请求方式**： `POST`  
**Action**： `UpdateNodeGroupEcsSpec`  

**请求参数**  
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateNodeGroupEcsSpec | 要执行的操作，取值：UpdateNodeGroupEcsSpec |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| NodeGroupId | String | 是 | task-1.emr-xxx | 节点组ID |
| TargetEcsInstanceType | String | 是 | ecs.g2i.4xlarge | 待变更的目标ECS规格 |
| ClientToken | String | 否 | xxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**调用示例**  
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateNodeGroupEcsSpec \
  --version 2023-08-15 \
  --method POST \
  --query '{}' \
  --body '{"ClusterId":"emr-xxx","NodeGroupId":"task-1.emr-xxx","TargetEcsInstanceType":"ecs.g2i.4xlarge"}'
```

**请求参数示例**  
```json
{ 
    "ClusterId":"emr-xxx", 
    "NodeGroupId":"task-1.emr-xxx", 
    "TargetEcsInstanceType":"ecs.g2i.4xlarge" 
}
```

**返回参数**  
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperationId | String | Orderxxx | 集群操作ID |

**返回示例**  
```json
{ 
    "ResponseMetadata": { 
        "RequestId": "202312042119240BF21498512xxx", 
        "Action": "UpdateNodeGroupEcsSpec", 
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