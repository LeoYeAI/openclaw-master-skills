# EMR on ECS 用户管理操作指南

## 概述

EMR on ECS 提供半托管的 ECS 形态大数据服务，主要面向集群的用户管理。

## 说明

本文档提供 EMR on ECS 中 **用户管理** 相关的 OpenAPI。

**OpenAPI 调用方式**

- **API Version** 统一为 **2023-08-15**
- **Service**： emr

## 核心调用方法

所有 EMR on ECS 用户管理操作均通过下列脚本实现

```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action <Action> \
  --version 2023-08-15 \
  --method <POST> \
  --query '<json>' \
  --body '<json>'
```

## 用户管理操作

### 1. 创建集群用户

**接口描述**
调用 CreateClusterUser，在 E-MapReduce（EMR）集群中创建新用户。

**使用场景**
为指定集群创建新的用户账户。

**请求方式**： `POST`  
**Action**： `CreateClusterUser`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | CreateClusterUser | 要执行的操作，取值：CreateClusterUser |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserName | String | 是 | emr_user | 要新建的用户的名称。该参数只能由字母、数字、下划线（_）、"."、"-"组成，最多支持64字符 |
| Password | String | 是 | Password123! | 要新建的用户的登录密码。 密码的长度需在8-20个字符之间，支持数字，字母，-，_ 且 至少包含1个数字和1个字母。 |
| UserGroupNames | Array of String | 否 | ["emr_usergroup"] | 需要绑定用户组（用户组名称只能以字母开头，后跟零个或多个字母、数字或下划线组成的字符串，最多支持64字符） |
| Description | String | 否 | 用户描述 | 要新建的用户的备注信息 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action CreateClusterUser \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"CreateClusterUser","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserName":"emr_user","Password":"Password123!"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserName": "emr_user",
  "Password": "Password123!"
}
```

**返回参数**
本接口无特有的返回参数。更多信息请见返回结构。

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "202407011045060872172181073BB6B5",
    "Action": "CreateClusterUser",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": null
}
```

### 2. 修改已创建用户信息

**接口描述**
调用 UpdateClusterUser，修改 E-MapReduce（EMR）集群中已创建的用户信息。

**使用场景**
修改指定集群中已存在用户的用户组或描述信息。

**请求方式**： `POST`  
**Action**： `UpdateClusterUser`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateClusterUser | 要执行的操作，取值：UpdateClusterUser |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | EMR集群ID |
| UserName | String | 是 | emr_user | 集群用户名（不支持修改） |
| UserGroupNames | Array of String | 否 | ["emr_usergroup"] | 用户所属用户组 |
| Description | String | 否 | 用户描述 | 用户的备注信息 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateClusterUser \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"UpdateClusterUser","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserName":"emr_user","UserGroupNames":["emr_usergroup"],"Description":"用户描述"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserName": "emr_user",
  "UserGroupNames": [
    "emr_usergroup"
  ],
  "Description": "用户描述"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构。

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Result | String | null | 更新用户信息 |

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "2024070110342609912124619718B8A1",
    "Action": "UpdateClusterUser",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": null
}
```

### 3. 获取集群用户列表

**接口描述**
调用 ListClusterUsers，获取 E-MapReduce（EMR）集群的用户列表。

**使用场景**
查询指定集群的用户信息列表。

**请求方式**： `POST`  
**Action**： `ListClusterUsers`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | ListClusterUsers | 要执行的操作，取值：ListClusterUsers |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserName | String | 否 | emr_user | 集群用户名 |
| Keyword | String | 否 | emr | 关键字，用户名称模糊匹配 |
| UserGroupName | String | 否 | emr_usergroup | 集群用户组名 |
| CreatorName | String | 否 | creator | 创建者名称 |
| UserNameOrder | String | 否 | ASC，DESC | 用户名排序方式 |
| CreateTimeOrder | String | 否 | ASC，DESC | 用户创建时间排序方式 |
| UpdateTimeOrder | String | 否 | ASC，DESC | 用户更新时间排序方式 |
| UserNames | Array of String | 否 | ["emr_user"] | 批量查询使用 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action ListClusterUsers \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"ListClusterUsers","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构。

| 参数    | 类型 | 示例值 | 描述 |
|-------|------|--------|------|
| Items | Array of Object | [ { "ClusterId": "emr-xxx", "UserName": "emr_user", "Description": "用户描述", "CreatorId": "12345678", "CreatorName": "creator", "UserGroupNames": [ "emr_usergroup" ] } ] | 用户集群信息 |

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "202407081019341630311861572E4666",
    "Action": "ListClusterUsers",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": {
    "Items": [
      {
        "ClusterId": "emr-xxx",
        "UserName": "emr_user",
        "Description": "用户描述",
        "CreatorId": "12345678",
        "CreatorName": "creator"
      }
    ]
  }
}
```

### 4. 获取用户详情

**接口描述**
调用 GetClusterUsers，获取 E-MapReduce（EMR）集群的用户详细信息。

**使用场景**
查询指定集群的详细用户信息。

**请求方式**： `POST`  
**Action**： `GetClusterUsers`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | GetClusterUsers | 要执行的操作，取值：GetClusterUsers |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserNames | Array of String | 否 | ["emr_user"] | 待查询用户名称 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action GetClusterUsers \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"GetClusterUsers","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx"
}
```

**返回参数**
下表仅列出本接口特有的返回参数。更多信息请参见返回结构。

| 参数 | 类型 | 示例值 | 描述 |
|------|------|--------|------|
| Result | Array of Object | [ { "ClusterId": "emr-xxx", "UserName": "emr-user", "Description": "emr用户", "CreatorId": "12345678", "CreatorName": "admin", "UserGroupNames": [ "emr_usergroup" ] } ] | 用户详细信息 |

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "20240708105606098087099231A881FE",
    "Action": "GetClusterUsers",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": [
    {
      "ClusterId": "emr-xxx",
      "UserName": "emr-user",
      "Description": "emr用户",
      "CreatorId": "12345678",
      "CreatorName": "admin",
      "UserGroupNames": [
        "emr_usergroup"
      ]
    }
  ]
}
```

### 5. 更新集群用户密码

**接口描述**
调用 UpdateClusterUserPassword，更新 E-MapReduce（EMR）集群用户的密码。

**使用场景**
修改指定集群中已存在用户的登录密码。

**请求方式**： `POST`  
**Action**： `UpdateClusterUserPassword`

**请求参数**
下表仅列出该接口特有的请求参数和部分公共参数。更多信息请见公共参数。

| 参数 | 类型 | 是否必填 | 示例值 | 描述 |
|------|------|----------|--------|------|
| Action | String | 是 | UpdateClusterUserPassword | 要执行的操作，取值：UpdateClusterUserPassword |
| Version | String | 是 | 2023-08-15 | API的版本，取值：2023-08-15 |
| ClusterId | String | 是 | emr-xxx | 集群ID |
| UserName | String | 是 | emr_user | 集群用户名 |
| OldPassword | String | 是 | OldPassword123! | 原有用户密码 |
| NewPassword | String | 是 | NewPassword123! | 新的用户密码 |

**调用示例**
```bash
python ./scripts/on_ecs/emr_on_ecs_cli.py \
  --action UpdateClusterUserPassword \
  --version 2023-08-15 \
  --method POST \
  --query '{"Action":"UpdateClusterUserPassword","Version":"2023-08-15"}' \
  --body '{"ClusterId":"emr-xxx","UserName":"emr_user","OldPassword":"OldPassword123!","NewPassword":"NewPassword123!"}'
```

**请求示例**
```json
{
  "ClusterId": "emr-xxx",
  "UserName": "emr_user",
  "OldPassword": "OldPassword123!",
  "NewPassword": "NewPassword123!"
}
```

**返回参数**
本接口无特有的返回参数。更多信息请见返回结构。

**返回示例**
```json
{
  "ResponseMetadata": {
    "RequestId": "202407011031450390082162467C975F",
    "Action": "UpdateClusterUserPassword",
    "Version": "2023-08-15",
    "Service": "emr",
    "Region": "cn-beijing"
  },
  "Result": null
}
```

