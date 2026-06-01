# EMR on ECS 应用配置管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的应用配置项列表、集群配置文件列表、配置项修改历史列表、修改配置项等管理。

## 说明

本文档提供 EMR on ECS 中 **应用配置管理** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 应用配置管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 应用配置管理操作

### 1. 应用配置文件列表查询

**接口描述**
调用 ListApplicationConfigFiles，查看一个 E-MapReduce（EMR）集群中的应用配置文件。

**使用场景**
查询指定集群下某个应用的所有配置文件信息。

**请求方式**
**请求方式**： `POST`  
**Action**： `ListApplicationConfigFiles`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListApplicationConfigFiles | 要执行的操作，取值：ListApplicationConfigFiles |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 应用名称 |
| MaxResults | Integer | 否 | 10 | 返回的最大记录数，默认10，最大100 |
| NextToken | String | 否 | xxx | 分页查询的下一页token |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListApplicationConfigFiles \
  --method POST \
  --query '{"Action":"ListApplicationConfigFiles","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS"}'
```

**请求示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName": "HDFS"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 应用配置文件列表 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | TfhvaePXZl2eNA6K58wUIw== | 分页查询的下一页token |
| TotalCount | Integer | 383 | 总记录数 |

**Items 对象结构**

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ApplicationName | String | HDFS | 应用名称 |
| FileName | String | core-site.xml | 配置文件名 |
| FilePath | String | /etc/emr/hadoop/conf | 配置文件路径 |
| FileMode | String | null | 文件权限模式 |
| FileUser | String | hdfs | 文件所属用户 |
| FileGroup | String | hadoop | 文件所属用户组 |
| SupportCustomConfigItem | Boolean | null | 是否支持自定义配置项 |
| Description | String | null | 配置文件描述 |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231204150314DDAD5A0C4767xxx",
        "Action": "ListApplicationConfigFiles",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "Items": [
            {
                "ApplicationName": "HDFS",
                "FileName": "core-site.xml",
                "FilePath": "/etc/emr/hadoop/conf",
                "FileMode": null,
                "FileUser": "hdfs",
                "FileGroup": "hadoop",
                "SupportCustomConfigItem": null,
                "Description": null
            },
            {
                "ApplicationName": "HDFS",
                "FileName": "hadoop-env.sh",
                "FilePath": "/etc/emr/hadoop/conf",
                "FileMode": null,
                "FileUser": "hdfs",
                "FileGroup": "hadoop",
                "SupportCustomConfigItem": null,
                "Description": null
            }
        ],
        "TotalCount": 9,
        "MaxResults": 10,
        "NextToken": null
    }
}
```

### 2. 配置项列表

**接口描述**
调用 ListApplicationConfigs，获取 E-MapReduce（EMR）集群应用配置列表信息。

**使用场景**
查询指定集群下某个应用的所有配置项信息。

**请求方式**： `POST`  
**Action**： `ListApplicationConfigs`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListApplicationConfigs | 要执行的操作，取值：ListApplicationConfigs |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 应用名称 |
| ConfigFileName | String | 否 | hdfs-site.xml | 配置文件名称 |
| ConfigItemKey | String | 否 | dfs.http.policy | 配置项键名 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListApplicationConfigs \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListApplicationConfigs","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS"}'
```

**请求示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName": "HDFS"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 应用配置详情列表 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | TfhvaePXZl2eNA6K58wUIw== | 分页查询的下一页token |
| TotalCount | Integer | 383 | 总记录数 |

**Items 对象结构**

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ApplicationName | String | HDFS | 应用名称 |
| ConfigFileName | String | hdfs-site.xml | 配置文件名称 |
| ConfigItemKey | String | dfs.http.policy | 配置项键名 |
| PresetConfigItemValue | String | HTTPS_ONLY | 预设配置项值 |
| ConfigItemValue | String | HTTPS_ONLY | 当前配置项值 |
| Applied | Boolean | false | 是否已应用 |
| Customized | Boolean | false | 是否自定义配置 |
| ConfigVersion | String | null | 配置版本 |
| OperatorId | String | null | 操作人ID |
| Description | String | "" | 配置项描述 |
| Remark | String | null | 备注信息 |
| EffectiveScope | Object | -- | 生效范围配置 |
| UpdateTime | String | null | 更新时间 |

**EffectiveScope 对象结构**

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| EffectiveType | String | COMPONENT_NAME | 生效类型 |
| NodeGroupIds | Array | null | 节点组ID列表 |
| NodeGroupNames | Array | null | 节点组名称列表 |
| NodeGroupTypes | Array | null | 节点组类型列表 |
| NodeNames | Array | null | 节点名称列表 |
| NodeIds | Array | null | 节点ID列表 |
| ComponentNames | Array | ["DATANODE"] | 组件名称列表 |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231205140549749823963EB28xxx",
        "Action": "ListApplicationConfigs",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "Items": [
            {
                "ApplicationName": "HDFS",
                "ConfigFileName": "hdfs-site.xml",
                "ConfigItemKey": "dfs.http.policy",
                "PresetConfigItemValue": "HTTPS_ONLY",
                "ConfigItemValue": "HTTPS_ONLY",
                "Applied": false,
                "Customized": false,
                "ConfigVersion": null,
                "OperatorId": null,
                "Description": "",
                "Remark": null,
                "EffectiveScope": {
                    "EffectiveType": "COMPONENT_NAME",
                    "NodeGroupIds": null,
                    "NodeGroupNames": null,
                    "NodeGroupTypes": null,
                    "NodeNames": null,
                    "NodeIds": null,
                    "ComponentNames": [
                        "DATANODE"
                    ]
                },
                "UpdateTime": null
            },
            {
                "ApplicationName": "HDFS",
                "ConfigFileName": "hdfs-site.xml",
                "ConfigItemKey": "dfs.datanode.data.dir",
                "PresetConfigItemValue": "/data01/hadoop/hdfs/datanode",
                "ConfigItemValue": "/data01/hadoop/hdfs/datanode",
                "Applied": false,
                "Customized": false,
                "ConfigVersion": null,
                "OperatorId": null,
                "Description": "",
                "Remark": null,
                "EffectiveScope": {
                    "EffectiveType": "COMPONENT_NAME",
                    "NodeGroupIds": null,
                    "NodeGroupNames": null,
                    "NodeGroupTypes": null,
                    "NodeNames": null,
                    "NodeIds": null,
                    "ComponentNames": [
                        "*"
                    ]
                },
                "UpdateTime": null
            }
        ],
        "TotalCount": 383,
        "MaxResults": 10,
        "NextToken": "TfhvaePXZl2eNA6K58wUIw=="
    }
}
```

### 3. 获取集群配置文件信息详情

**接口描述**
调用 GetApplicationConfigFile，获取一个 E-MapReduce（EMR）集群的应用配置文件。

**使用场景**
查询指定集群下某个应用的特定配置文件内容。

**请求方式**： `POST`  
**Action**： `GetApplicationConfigFile`  

**注意事项**
- 已拥有火山引擎账号并开通 EMR 权限

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | GetApplicationConfigFile | 要执行的操作，取值：GetApplicationConfigFile |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 应用名称 |
| ConfigFileName | String | 是 | core-site.xml | 应用的配置文件名 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action GetApplicationConfigFile \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"GetApplicationConfigFile","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS","ConfigFileName":"core-site.xml"}'
```

**请求参数示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName": "HDFS",
    "ConfigFileName":"core-site.xml"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ApplicationName | String | HDFS | 应用名称 |
| FileName | String | core-site.xml | 配置文件名称 |
| FilePath | String | /etc/emr/hadoop/conf | 配置文件路径 |
| FileContent | String | <?xml version="1.0" encoding="UTF-8"?>... | 配置文件内容 |
| FileUser | String | hdfs | 配置文件的权限：user |
| FileGroup | String | hadoop | 配置文件的权限：group |
| SupportCustomConfigItem | Boolean | xxx | 配置文件是否允许设置自定义参数 |
| Description | String | xxx | 配置文件的描述信息 |

**返回参数示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "20231204171503C7664BD9E36Axxx",
        "Action": "GetApplicationConfigFile",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "ApplicationName": "HDFS",
        "FileName": "core-site.xml",
        "FilePath": "/etc/emr/hadoop/conf",
        "FileMode": null,
        "FileContent": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"configuration.xsl\"?>\n<configuration>...",
        "FileUser": "hdfs",
        "FileGroup": "hadoop",
        "SupportCustomConfigItem": null,
        "Description": null
    }
}
```

### 4. 配置项修改历史列表

**接口描述**
调用 ListApplicationConfigHistories，获取一个 E-MapReduce（EMR）集群应用配置修改历史列表。

**使用场景**
查询指定集群下某个应用的配置项修改历史记录。

**请求方式**： `POST`  
**Action**： `ListApplicationConfigHistories`  

**注意事项**
- 已拥有火山引擎账号并开通 EMR 权限

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListApplicationConfigHistories | 要执行的操作，取值：ListApplicationConfigHistories |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 应用名称 |
| ConfigFileName | String | 否 | core-site.xml | 配置文件名称 |
| ConfigItemKey | String | 否 | 222 | 配置项的key，模糊查询 |
| ConfigVersion | String | 否 | 249850 | 配置版本 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListApplicationConfigHistories \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListApplicationConfigHistories","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS"}'
```

**请求示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName": "HDFS"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | -- | 应用配置历史列表 |
| MaxResults | Integer | 10 | 单次查询可返回的最大记录数 |
| NextToken | String | ygNIwmOwX+RJiT27Fhimew== | 分页查询的下一页token |
| TotalCount | Integer | 383 | 总记录数 |

**Items 对象结构**
| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ApplicationName | String | HDFS | 应用名称 |
| ConfigFileName | String | core-site.xml | 配置文件名称 |
| ConfigItemKey | String | 222 | 配置项键名 |
| BeforeConfigItemValue | String | null | 修改前的配置项值 |
| ConfigItemValue | String | 211231 | 修改后的配置项值 |
| Applied | Boolean | false | 是否已应用 |
| Customized | Boolean | true | 是否自定义配置 |
| ConfigVersion | String | 249850 | 配置版本 |
| OperatorId | String | null | 操作人ID |
| Description | String | null | 配置项描述 |
| Remark | String | 1 | 备注信息 |
| EffectiveScope | Object | -- | 生效范围配置 |
| UpdateTime | Integer | 1701589263752 | 更新时间（时间戳） |

**EffectiveScope 对象结构**
| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| EffectiveType | String | COMPONENT_NAME | 生效类型 |
| NodeGroupIds | Array | null | 节点组ID列表 |
| NodeGroupNames | Array | null | 节点组名称列表 |
| NodeGroupTypes | Array | null | 节点组类型列表 |
| NodeNames | Array | null | 节点名称列表 |
| NodeIds | Array | null | 节点ID列表 |
| ComponentNames | Array | ["*"] | 组件名称列表 |

**返回参数示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "202312041421318F52F2BA7B8xxx",
        "Action": "ListApplicationConfigHistories",
        "Version": "2023-08-15",
        "Service": "emr",
        "Region": "cn-beijing",
        "Error": null,
        "Deprecated": false
    },
    "Result": {
        "Items": [
            {
                "ApplicationName": "HDFS",
                "ConfigFileName": "core-site.xml",
                "ConfigItemKey": "222",
                "BeforeConfigItemValue": null,
                "ConfigItemValue": "211231",
                "Applied": false,
                "Customized": true,
                "ConfigVersion": "249850",
                "OperatorId": null,
                "Description": null,
                "Remark": "1",
                "EffectiveScope": {
                    "EffectiveType": "COMPONENT_NAME",
                    "NodeGroupIds": null,
                    "NodeGroupNames": null,
                    "NodeGroupTypes": null,
                    "NodeNames": null,
                    "NodeIds": null,
                    "ComponentNames": [
                        "*"
                    ]
                },
                "UpdateTime": 1701589263752
            },
            {
                "ApplicationName": "HDFS",
                "ConfigFileName": "core-site.xml",
                "ConfigItemKey": "s111",
                "BeforeConfigItemValue": null,
                "ConfigItemValue": "111",
                "Applied": false,
                "Customized": true,
                "ConfigVersion": "249850",
                "OperatorId": null,
                "Description": null,
                "Remark": "1",
                "EffectiveScope": {
                    "EffectiveType": "COMPONENT_NAME",
                    "NodeGroupIds": null,
                    "NodeGroupNames": null,
                    "NodeGroupTypes": null,
                    "NodeNames": null,
                    "NodeIds": null,
                    "ComponentNames": [
                        "*"
                    ]
                },
                "UpdateTime": 1701589263752
            },
            {
                "ApplicationName": "HDFS",
                "ConfigFileName": "hdfs-site.xml",
                "ConfigItemKey": "dfs.client.block.write.replace-datanode-on-failure.enable",
                "BeforeConfigItemValue": "true",
                "ConfigItemValue": "false",
                "Applied": false,
                "Customized": false,
                "ConfigVersion": "249644",
                "OperatorId": null,
                "Description": "\n",
                "Remark": null,
                "EffectiveScope": {
                    "EffectiveType": "COMPONENT_NAME",
                    "NodeGroupIds": null,
                    "NodeGroupNames": null,
                    "NodeGroupTypes": null,
                    "NodeNames": null,
                    "NodeIds": null,
                    "ComponentNames": [
                        "*"
                    ]
                },
                "UpdateTime": 1701587925163
            }
        ],
        "TotalCount": 3,
        "MaxResults": 10,
        "NextToken": "ygNIwmOwX+RJiT27Fhimew=="
    }
}
```

### 5. 更新配置项

**接口描述**
调用 UpdateApplicationConfig，更新 E-MapReduce（EMR）集群的应用配置。

**使用场景**
修改指定集群下某个应用的配置项值。

**请求方式**
**请求方式**： `POST`  
**Action**： `UpdateApplicationConfig`  

**注意事项**
- 已拥有火山引擎账号并开通 EMR 权限

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateApplicationConfig | 要执行的操作，取值：UpdateApplicationConfig |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| ApplicationName | String | 是 | HDFS | 服务名称 |
| Remark | String | 是 | 测试 | 操作备注 |
| Configs | Array of Object | 是 | [{"ConfigFileName":"hdfs-site.xml","ConfigItemKey":"dfs.blockreport.initialDelay","ConfigItemValue":2}] | 需要修改的配置项 |
| ClientToken | String | 否 | xxx | 调用方生成的唯一标识这次请求的标识，用来保证幂等 |

**Configs 对象结构**
| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| ConfigFileName | String | 是 | hdfs-site.xml | 配置文件名称 |
| ConfigItemKey | String | 是 | dfs.blockreport.initialDelay | 配置项键名 |
| ConfigItemValue | String | 是 | 2 | 配置项值 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateApplicationConfig \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"UpdateApplicationConfig","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","ApplicationName":"HDFS","Configs":[{"ConfigFileName":"hdfs-site.xml","ConfigItemKey":"dfs.blockreport.initialDelay","ConfigItemValue":"2"}],"Remark":"测试"}'
```

**请求示例**
```json
{
    "ClusterId":"emr-xxx",
    "ApplicationName": "HDFS",
    "Configs":[{
        "ConfigFileName":"hdfs-site.xml",
        "ConfigItemKey":"dfs.blockreport.initialDelay",
        "ConfigItemValue":"2"   
    }],
    "Remark":"刘斌测试"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| ClusterId | String | emr-xxx | 集群ID |
| OperateId | String | 73xxx | 集群操作ID |
| ResultData | Object | -- | 结果数据 |

**返回示例**
```json
{
    "ResponseMetadata": {
        "RequestId": "202312042119240BF2149851287xxx",
        "Action": "UpdateApplicationConfig",
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


