# EMR on ECS 用户组管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的用户组管理。

## 说明

本文档提供 EMR on ECS 中 **用户组管理** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 用户组管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --version 2023-08-15 \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 用户组管理操作

### 1. 获取集群用户组列表

**接口描述**
调用 ListClusterUserGroups，获取 E-MapReduce（EMR）集群的用户组列表。

**使用场景**
查询指定集群的用户组信息列表。

**请求方式**： `POST`  
**Action**： `ListClusterUserGroups`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListClusterUserGroups | 要执行的操作，取值：ListClusterUserGroups |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserGroupName | String | 否 | emr_usergroup | 用户组名称 |
| Keyword | String | 否 | emr | 关键字，用户组名称模糊匹配 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListClusterUserGroups \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListClusterUserGroups","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserGroupName":"emr_usergroup"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserGroupName": "emr_usergroup"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构。

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | [ { "ClusterId": "emr-xxx", "UserGroupName": "emr_usergroup", "Description": "emr用户组" } ] | 用户组基础信息 |

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "20240708101656249245174165FBBBAE",
    "Action": "ListClusterUserGroups",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": {
    "Items": [
      {
        "ClusterId": "emr-xxx",
        "UserGroupName": "emr_usergroup",
        "Description": "emr用户组"
      }
    ]
  }
}
```

### 2. 集群用户组详情

**接口描述**
调用 GetClusterUserGroups，获取 E-MapReduce（EMR）集群的用户组详细信息。

**使用场景**
查询指定集群的详细用户组信息。

**请求方式**： `POST`  
**Action**： `GetClusterUserGroups`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | GetClusterUserGroups | 要执行的操作，取值：GetClusterUserGroups |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserGroupNames | Array of String | 是 | ["emr_usergroup"] | 用户组名称 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action GetClusterUserGroups \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"GetClusterUserGroups","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserGroupNames":["emr_usergroup"]}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserGroupNames": [
    "emr_usergroup"
  ]
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构。

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Items | Array of Object | [ { "ClusterId": "emr-xxx", "UserGroupName": "emr_usergroup", "Description": "emr用户组", "Members": [ "emr_user" ] } ] | 用户组详细信息 |

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "2024071716185520704402009795159A",
    "Action": "GetClusterUserGroups",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": {
    "Items": [
      {
        "ClusterId": "emr-xxx",
        "UserGroupName": "emr_usergroup",
        "Description": "emr用户组",
        "Members": [
          "emr_user"
        ]
      }
    ]
  }
}
```

### 3. 创建集群用户组

**接口描述**
调用 CreateClusterUserGroup，在 E-MapReduce（EMR）集群中创建新用户组。

**使用场景**
为指定集群创建新的用户组。

**请求方式**： `POST`  
**Action**： `CreateClusterUserGroup`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | CreateClusterUserGroup | 要执行的操作，取值：CreateClusterUserGroup |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserGroupName | String | 是 | emr_usergroup | 用户组名称 |
| Description | String | 否 | 用户组描述 | 用户组描述 |
| Members | Array of String | 否 | ["emr_user"] | 用户组成员 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action CreateClusterUserGroup \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"CreateClusterUserGroup","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserGroupName":"emr_usergroup"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserGroupName": "emr_usergroup"
}
```

**返回参数**
本接口无特有的返回参数。更多信息请见返回结构。

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "2024070110175113408721519715AD55",
    "Action": "CreateClusterUserGroup",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": null
}
```

### 4. 更新集群用户组

**接口描述**
调用 UpdateClusterUserGroup，更新 E-MapReduce（EMR）集群的用户组信息。

**使用场景**
修改指定集群中已存在用户组的描述或成员信息。

**请求方式**： `POST`  
**Action**： `UpdateClusterUserGroup`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateClusterUserGroup | 要执行的操作，取值：UpdateClusterUserGroup |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserGroupName | String | 是 | emr_usergroup | 用户组名称 |
| Description | String | 否 | 用户组描述 | 用户组描述 |
| Members | Array of String | 否 | ["emr_user"] | 用户组所包含的用户 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateClusterUserGroup \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"UpdateClusterUserGroup","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserGroupName":"emr_usergroup","Description":"emr用户组","Members":["emr_user"]}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserGroupName": "emr_usergroup",
  "Description": "emr用户组",
  "Members": [
    "emr_user"
  ]
}
```

**返回参数**
本接口无特有的返回参数。更多信息请见返回结构。

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "20240701094202027037132149C4CFE3",
    "Action": "UpdateClusterUserGroup",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": null
}
```